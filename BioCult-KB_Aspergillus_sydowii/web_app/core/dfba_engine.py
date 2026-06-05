from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scipy.integrate import solve_ivp

from .. import gem_cobra
from ..schemas import DfbaStepInput, GemFbaInput, MediaOptimizationInput, ProcessSimulationInput
from .culture_fluid import CultureFluidInput, culture_fluid_state
from .reactor_physics import kla_vant_riet_h, oxygen_transfer_rate_mmol_l_h


@dataclass(frozen=True)
class Rates:
    mu_h: float
    qP_u_g_h: float
    qS_g_g_h: float
    qN_g_g_h: float
    qC_g_g_h: float
    oxygen_demand_mmol_g_h: float
    status: str
    fluxes: dict[str, float]


def _medium_from_state(template: MediaOptimizationInput, molasses: float, nitrogen_g_l: float, collagen: float) -> MediaOptimizationInput:
    return MediaOptimizationInput(
        molasses_g_l=max(0.0, molasses),
        peptone_g_l=max(0.0, nitrogen_g_l / 0.14),
        collagen_g_l=max(0.0, collagen),
        mineral_factor=template.mineral_factor,
        pH=template.pH,
        aeration_vvm=template.aeration_vvm,
        rpm=template.rpm,
        cultivation_time_h=template.cultivation_time_h,
        temperature_C=template.temperature_C,
        working_volume_l=template.working_volume_l,
    )


def _rates(medium: MediaOptimizationInput) -> Rates:
    result = gem_cobra.run_fba(GemFbaInput(medium=medium, objective="balanced", growth_floor=0.03))
    fluxes = result.get("fluxes") or {}
    if result.get("status") != "optimal":
        return Rates(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, str(result.get("status", "degraded")), fluxes)
    mu_capacity = max(0.0, float(fluxes.get("DM_biomass_c", result.get("objective_value") or 0.0)))
    product_capacity = max(0.0, float(fluxes.get("EX_collagenolytic_product_e", 0.0)))
    mu = min(0.095, 0.012 + 0.0065 * mu_capacity)
    qP = min(12.0, 0.55 + 0.32 * product_capacity)
    qS = min(2.9, 0.18 + abs(float(fluxes.get("EX_molasses_proxy_e", 0.0))) * 0.055)
    qN = min(0.48, 0.04 + abs(float(fluxes.get("EX_organic_nitrogen_proxy_e", 0.0))) * 0.018)
    qC = min(0.24, 0.015 + abs(float(fluxes.get("EX_collagen_substrate_e", 0.0))) * 0.014)
    oxygen = min(4.5, 0.25 + abs(float(fluxes.get("EX_o2_e", 0.0))) * 0.045)
    return Rates(mu, qP, qS, qN, qC, oxygen, "optimal", {key: float(value) for key, value in fluxes.items()})


def run_dfba_step(input_data: DfbaStepInput) -> dict[str, Any]:
    medium = input_data.medium
    nitrogen = input_data.peptone_n_g_l if input_data.peptone_n_g_l is not None else medium.peptone_g_l * 0.14
    collagen = input_data.collagen_g_l if input_data.collagen_g_l is not None else medium.collagen_g_l
    state_medium = _medium_from_state(medium, input_data.molasses_g_l, nitrogen, collagen)
    rates = _rates(state_medium)
    fluid = culture_fluid_state(
        CultureFluidInput(
            biomass_g_l=input_data.biomass_g_l,
            molasses_g_l=input_data.molasses_g_l,
            peptone_g_l=state_medium.peptone_g_l,
            collagen_g_l=collagen,
            pH=medium.pH,
            temperature_C=medium.temperature_C,
        ),
        mineral_factor=medium.mineral_factor,
    )
    kla = kla_vant_riet_h(medium.rpm, medium.aeration_vvm, fluid["viscosity_mpa_s"], volume_l=input_data.volume_l)
    otr = oxygen_transfer_rate_mmol_l_h(kla, input_data.do_percent)
    oxygen_factor = min(1.0, max(0.0, input_data.do_percent / 35.0))
    substrate_factor = min(1.0, input_data.molasses_g_l / (input_data.molasses_g_l + 1.8)) if input_data.molasses_g_l > 0 else 0.0
    effective_mu = rates.mu_h * oxygen_factor * substrate_factor

    def ode(_t: float, y: list[float]) -> list[float]:
        x, s, n, c, p, do = y
        growth = effective_mu * x * max(0.0, 1.0 - x / 5.2)
        d_s = -rates.qS_g_g_h * x
        d_n = -rates.qN_g_g_h * x
        d_c = -rates.qC_g_g_h * x
        d_p = rates.qP_u_g_h * x * (0.45 + min(1.0, c / 5.0) * 0.55)
        d_do = (otr / 0.24) - rates.oxygen_demand_mmol_g_h * x * 6.0
        return [growth, d_s, d_n, d_c, d_p, d_do]

    y0 = [input_data.biomass_g_l, input_data.molasses_g_l, nitrogen, collagen, input_data.product_u_ml, input_data.do_percent]
    solution = solve_ivp(ode, (0.0, input_data.dt_h), y0, method="RK45", max_step=max(input_data.dt_h / 8.0, 0.25))
    y = [max(0.0, float(value)) for value in solution.y[:, -1]]
    y[5] = max(0.0, min(100.0, y[5]))
    degraded = rates.status != "optimal" or not solution.success
    return {
        "status": "degraded" if degraded else "optimal",
        "degraded_mode": degraded,
        "time_h": input_data.time_h + input_data.dt_h,
        "volume_l": input_data.volume_l,
        "biomass_g_l": round(y[0], 5),
        "molasses_g_l": round(y[1], 5),
        "peptone_n_g_l": round(y[2], 5),
        "collagen_g_l": round(y[3], 5),
        "product_u_ml": round(y[4], 5),
        "pO2_percent": round(y[5], 5),
        "dfba_mu_h": round(effective_mu, 6),
        "qP_u_g_h": round(rates.qP_u_g_h, 6),
        "qS_g_g_h": round(rates.qS_g_g_h, 6),
        "OUR_mmol_l_h": round(rates.oxygen_demand_mmol_g_h * input_data.biomass_g_l, 6),
        "kLa_h": kla,
        "OTR_mmol_l_h": otr,
        "fluxes": rates.fluxes,
        "warnings": [] if not degraded else ["dFBA step entered degraded mode; inspect solver status and substrate bounds."],
    }


def simulate_dfba(input_data: ProcessSimulationInput) -> dict[str, Any]:
    medium = input_data.medium
    time_h = 0.0
    volume = input_data.initial_volume_l
    biomass = input_data.initial_biomass_g_l
    molasses = medium.molasses_g_l
    nitrogen = medium.peptone_g_l * 0.14
    collagen = medium.collagen_g_l
    product = 0.0
    do_percent = 92.0
    last_mu = 0.0
    last_product_capacity = 0.0
    profile: list[dict[str, Any]] = []
    degraded = False
    status = "optimal"

    while time_h <= input_data.duration_h + 1e-9:
        fluid = culture_fluid_state(
            CultureFluidInput(biomass, molasses, max(0.0, nitrogen / 0.14), collagen, medium.pH, medium.temperature_C),
            mineral_factor=medium.mineral_factor,
        )
        profile.append(
            {
                "time_h": round(time_h, 3),
                "volume_l": round(volume, 4),
                "biomass_g_l": round(biomass, 4),
                "molasses_g_l": round(molasses, 4),
                "peptone_n_g_l": round(nitrogen, 4),
                "collagen_g_l": round(collagen, 4),
                "amino_nitrogen_mg_percent": round(95 + nitrogen * 22 + biomass * 9, 3),
                "protein_mg_ml": round(0.15 + product * 0.006, 4),
                "product_u_ml": round(product, 4),
                "pO2_percent": round(do_percent, 3),
                "density_g_ml": fluid["density_g_ml"],
                "viscosity_mpa_s": fluid["viscosity_mpa_s"],
                "conductivity_ms_cm": fluid["conductivity_ms_cm"],
                "fba_mu_capacity_h": round(last_mu, 6),
                "fba_product_capacity": round(last_product_capacity, 6),
                "dfba_mu_h": round(last_mu, 6),
                "kLa_h": kla_vant_riet_h(medium.rpm, medium.aeration_vvm, fluid["viscosity_mpa_s"], volume_l=volume),
                "OTR_mmol_l_h": oxygen_transfer_rate_mmol_l_h(
                    kla_vant_riet_h(medium.rpm, medium.aeration_vvm, fluid["viscosity_mpa_s"], volume_l=volume),
                    do_percent,
                ),
            }
        )
        if time_h >= input_data.duration_h:
            break
        step = run_dfba_step(
            DfbaStepInput(
                time_h=time_h,
                dt_h=input_data.step_h,
                medium=medium,
                biomass_g_l=biomass,
                molasses_g_l=molasses,
                peptone_n_g_l=nitrogen,
                collagen_g_l=collagen,
                product_u_ml=product,
                do_percent=do_percent,
                volume_l=volume,
            )
        )
        degraded = degraded or step["degraded_mode"]
        status = step["status"]
        last_mu = step["dfba_mu_h"]
        last_product_capacity = step["qP_u_g_h"]
        biomass = step["biomass_g_l"]
        molasses = step["molasses_g_l"]
        nitrogen = step["peptone_n_g_l"]
        collagen = step["collagen_g_l"]
        product = step["product_u_ml"]
        do_percent = step["pO2_percent"]
        if input_data.process_mode == "fed_batch":
            feed = min(input_data.feed_rate_l_h * input_data.step_h, max(0.0, 2.2 - volume))
            if feed > 0:
                old_volume = volume
                volume += feed
                molasses = (molasses * old_volume + 32.0 * feed) / volume
                nitrogen = (nitrogen * old_volume + 95.0 * 0.14 * feed) / volume
                collagen = (collagen * old_volume + 6.0 * feed) / volume
                biomass *= old_volume / volume
                product *= old_volume / volume
        elif input_data.process_mode == "continuous":
            flow = input_data.feed_rate_l_h * input_data.step_h
            bleed = input_data.bleed_rate_l_h * input_data.step_h
            old_volume = volume
            volume = max(0.05, volume + flow - bleed)
            dilution = min(0.95, bleed / max(old_volume, 1e-6))
            biomass *= 1 - dilution
            product *= 1 - dilution
            molasses = (molasses * old_volume * (1 - dilution) + 24.0 * flow) / max(volume, 1e-6)
            nitrogen = (nitrogen * old_volume * (1 - dilution) + 80.0 * 0.14 * flow) / max(volume, 1e-6)
            collagen = (collagen * old_volume * (1 - dilution) + 3.0 * flow) / max(volume, 1e-6)
        time_h += input_data.step_h

    return {"profile": profile, "degraded_mode": degraded, "fba_status": status}
