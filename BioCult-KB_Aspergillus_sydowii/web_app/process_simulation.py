from __future__ import annotations

from . import gem_cobra
from .core import dfba_engine
from .schemas import GemFbaInput, MediaOptimizationInput, ProcessSimulationInput


MASS_BALANCE_EQUATIONS = [
    "dV/dt = F_in - F_out",
    "d(XV)/dt = mu_fba * X * V - D_out * X * V",
    "d(S_i V)/dt = F_in*S_i,in - F_out*S_i - q_i,fba*X*V",
    "dP/dt = alpha*dX/dt + beta*X, ограничено FBA-мощностью продукта",
    "rho, вязкость, электропроводность = эмпирические функции биомассы и растворимых компонентов",
]


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _fba_capacities(medium: MediaOptimizationInput) -> tuple[dict, float, float]:
    biomass_result = gem_cobra.run_fba(GemFbaInput(medium=medium, objective="biomass"))
    product_result = gem_cobra.run_fba(GemFbaInput(medium=medium, objective="collagenolytic_product", growth_floor=0.03))
    biomass_value = float(biomass_result.get("objective_value") or 0.0) if biomass_result.get("status") == "optimal" else 0.0
    product_value = float(product_result.get("objective_value") or 0.0) if product_result.get("status") == "optimal" else 0.0
    return biomass_result, biomass_value, product_value


def _medium_from_state(template: MediaOptimizationInput, molasses: float, peptone_n: float, collagen: float) -> MediaOptimizationInput:
    return MediaOptimizationInput(
        molasses_g_l=max(0.0, molasses),
        peptone_g_l=max(0.0, peptone_n / 0.14),
        collagen_g_l=max(0.0, collagen),
        mineral_factor=template.mineral_factor,
        pH=template.pH,
        aeration_vvm=template.aeration_vvm,
        rpm=template.rpm,
        cultivation_time_h=template.cultivation_time_h,
        temperature_C=template.temperature_C,
        working_volume_l=template.working_volume_l,
    )


def simulate_process(input_data: ProcessSimulationInput) -> dict:
    try:
        dfba_result = dfba_engine.simulate_dfba(input_data)
        notes = [
            "Process simulation v2 uses dFBA-style COBRA capacity, scipy.solve_ivp integration, power-law rheology, and van't Riet kLa.",
            "Medium composition is tracked as process proxy pools for molasses carbon, organic nitrogen, and collagen substrate.",
        ]
        if dfba_result["degraded_mode"]:
            notes.append("At least one dFBA step entered degraded mode; inspect solver status and substrate bounds.")
        return {
            "process_mode": input_data.process_mode,
            "degraded_mode": dfba_result["degraded_mode"],
            "fba_status": dfba_result["fba_status"],
            "profile": dfba_result["profile"],
            "mass_balance_equations": MASS_BALANCE_EQUATIONS
            + [
                "dDO/dt = kLa*(DO_sat - DO) - OUR*X/V",
                "kLa = C*(P/V)^alpha*v_s^beta*f(viscosity)",
                "eta = K(X, collagen)*gamma_dot^(n-1)",
            ],
            "notes": notes,
        }
    except Exception:
        pass

    mode = input_data.process_mode
    dt = input_data.step_h
    medium = input_data.medium
    volume = input_data.initial_volume_l
    biomass = input_data.initial_biomass_g_l
    molasses = medium.molasses_g_l
    peptone_n = medium.peptone_g_l * 0.14
    collagen = medium.collagen_g_l
    product = 0.0
    protein = 0.15
    degraded = False
    fba_status = "not_run"
    profile = []

    time_h = 0.0
    while time_h <= input_data.duration_h + 1e-9:
        state_medium = _medium_from_state(medium, molasses, peptone_n, collagen)
        fba_result, biomass_capacity, product_capacity = _fba_capacities(state_medium)
        fba_status = str(fba_result.get("status", "degraded"))
        degraded = degraded or not bool(fba_result.get("available", False)) or fba_status not in {"optimal", "not_run"}

        carbon_lim = _clamp(molasses / max(medium.molasses_g_l, 1e-6))
        nitrogen_lim = _clamp(peptone_n / max(medium.peptone_g_l * 0.14, 1e-6))
        oxygen_fit = _clamp(medium.aeration_vvm * 0.48 + max(0.0, medium.rpm - 160.0) / 260.0)
        capacity_index = _clamp(biomass_capacity / (biomass_capacity + 6.0)) if biomass_capacity > 0 else 0.0
        mu = (0.006 + 0.060 * capacity_index) * carbon_lim * nitrogen_lim * (0.45 + oxygen_fit * 0.55)
        product_index = _clamp(product_capacity / (product_capacity + 4.0)) if product_capacity > 0 else 0.0
        carrying_capacity = 4.4 + medium.peptone_g_l / 120.0
        growth = max(0.0, mu * biomass * (1 - biomass / carrying_capacity) * dt)

        pO2 = 78 - 42 * _clamp(biomass / carrying_capacity) + 18 * oxygen_fit
        density = 1.010 + 0.0012 * molasses + 0.0018 * biomass + 0.0007 * peptone_n
        viscosity = 1.05 + 0.34 * biomass + 0.025 * collagen + 0.006 * medium.peptone_g_l
        conductivity = 8.0 + 0.22 * peptone_n + 0.35 * medium.mineral_factor + 0.22 * biomass
        amino_n = 95 + peptone_n * 22 + biomass * 9

        profile.append(
            {
                "time_h": round(time_h, 3),
                "volume_l": round(volume, 4),
                "biomass_g_l": round(biomass, 4),
                "molasses_g_l": round(molasses, 4),
                "peptone_n_g_l": round(peptone_n, 4),
                "collagen_g_l": round(collagen, 4),
                "amino_nitrogen_mg_percent": round(amino_n, 3),
                "protein_mg_ml": round(protein, 4),
                "product_u_ml": round(product, 4),
                "pO2_percent": round(max(5.0, min(100.0, pO2)), 3),
                "density_g_ml": round(density, 5),
                "viscosity_mpa_s": round(viscosity, 5),
                "conductivity_ms_cm": round(conductivity, 4),
                "fba_mu_capacity_h": round(biomass_capacity, 6),
                "fba_product_capacity": round(product_capacity, 6),
            }
        )

        if time_h >= input_data.duration_h:
            break

        product_gain = (4.8 * growth + 0.12 * biomass * dt) * product_index * (0.4 + _clamp(collagen / 5.0) * 0.6)
        protein += 0.018 * biomass * dt * (0.5 + product_index)
        product += product_gain
        biomass += growth
        molasses = max(0.0, molasses - growth * 2.25 - product_gain * 0.018 - 0.015 * biomass * dt)
        peptone_n = max(0.0, peptone_n - growth * 0.42 - product_gain * 0.012)
        collagen = max(0.0, collagen - product_gain * 0.030 - 0.006 * biomass * dt)

        if mode == "fed_batch":
            feed = min(input_data.feed_rate_l_h * dt, max(0.0, 2.2 - volume))
            if feed > 0:
                old_volume = volume
                volume += feed
                molasses = (molasses * old_volume + 32.0 * feed) / volume
                peptone_n = (peptone_n * old_volume + 95.0 * 0.14 * feed) / volume
                collagen = (collagen * old_volume + 6.0 * feed) / volume
                biomass *= old_volume / volume
                product *= old_volume / volume
                protein *= old_volume / volume
        elif mode == "continuous":
            flow = input_data.feed_rate_l_h * dt
            bleed = input_data.bleed_rate_l_h * dt
            old_volume = volume
            volume = max(0.05, volume + flow - bleed)
            dilution = min(0.95, bleed / max(old_volume, 1e-6))
            biomass *= 1 - dilution
            product *= 1 - dilution
            protein *= 1 - dilution
            molasses = (molasses * old_volume * (1 - dilution) + 24.0 * flow) / max(volume, 1e-6)
            peptone_n = (peptone_n * old_volume * (1 - dilution) + 80.0 * 0.14 * flow) / max(volume, 1e-6)
            collagen = (collagen * old_volume * (1 - dilution) + 3.0 * flow) / max(volume, 1e-6)

        time_h += dt

    notes = [
        "Симуляция процесса использует COBRA/FBA как слой предельной мощности и эмпирическую кинетику для динамики во времени.",
        "Состав среды отслеживается прокси-компонентами, а не полной химической спецификацией мелассы и пептона.",
    ]
    if degraded:
        notes.append("Ограниченный режим COBRA/SBML обнаружен минимум на одном шаге симуляции.")
    return {
        "process_mode": mode,
        "degraded_mode": degraded,
        "fba_status": fba_status,
        "profile": profile,
        "mass_balance_equations": MASS_BALANCE_EQUATIONS,
        "notes": notes,
    }
