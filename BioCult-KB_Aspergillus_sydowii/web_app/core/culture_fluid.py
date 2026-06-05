from __future__ import annotations

from dataclasses import dataclass
from math import log10


@dataclass(frozen=True)
class CultureFluidInput:
    biomass_g_l: float
    molasses_g_l: float
    peptone_g_l: float
    collagen_g_l: float
    pH: float = 7.2
    temperature_C: float = 25.0
    shear_rate_s: float = 100.0


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def apparent_viscosity_mpa_s(
    biomass_g_l: float,
    collagen_g_l: float,
    shear_rate_s: float = 100.0,
    k0: float = 0.00105,
    alpha_x: float = 0.00034,
    alpha_c: float = 0.000025,
    flow_index: float = 0.82,
) -> float:
    consistency_pa_s_n = k0 + alpha_x * max(0.0, biomass_g_l) + alpha_c * max(0.0, collagen_g_l)
    viscosity_pa_s = consistency_pa_s_n * max(1.0, shear_rate_s) ** (flow_index - 1.0)
    return round(viscosity_pa_s * 1000.0, 5)


def density_g_ml(molasses_g_l: float, peptone_g_l: float, biomass_g_l: float) -> float:
    return round(1.000 + 0.00056 * molasses_g_l + 0.00018 * peptone_g_l + 0.0018 * biomass_g_l, 5)


def conductivity_ms_cm(peptone_g_l: float, mineral_factor: float, biomass_g_l: float) -> float:
    return round(7.6 + 0.026 * peptone_g_l + 0.7 * mineral_factor + 0.21 * biomass_g_l, 4)


def buffer_capacity_mmol_l_pH(peptone_g_l: float, mineral_factor: float, pH: float) -> float:
    phosphate_like = 6.5 * max(0.0, mineral_factor)
    peptide_like = 0.18 * max(0.0, peptone_g_l)
    ph_fit = clamp(1.0 - abs(pH - 7.2) / 2.2, 0.25, 1.0)
    return round((phosphate_like + peptide_like) * ph_fit, 4)


def ph_corrector_ml(
    current_pH: float,
    target_pH: float,
    volume_l: float,
    buffer_capacity: float,
    normality: float = 2.0,
) -> float:
    delta = abs(target_pH - current_pH)
    mmol_needed = delta * max(0.0, buffer_capacity) * max(0.0, volume_l)
    return round(mmol_needed / max(normality, 1e-9), 4)


def culture_fluid_state(input_data: CultureFluidInput, mineral_factor: float = 1.0) -> dict:
    viscosity = apparent_viscosity_mpa_s(input_data.biomass_g_l, input_data.collagen_g_l, input_data.shear_rate_s)
    density = density_g_ml(input_data.molasses_g_l, input_data.peptone_g_l, input_data.biomass_g_l)
    conductivity = conductivity_ms_cm(input_data.peptone_g_l, mineral_factor, input_data.biomass_g_l)
    buffer_capacity = buffer_capacity_mmol_l_pH(input_data.peptone_g_l, mineral_factor, input_data.pH)
    ionic_strength_proxy = max(0.0, conductivity / 100.0)
    water_activity_proxy = round(1.0 - clamp(log10(1.0 + input_data.molasses_g_l + input_data.peptone_g_l) / 90.0), 5)
    return {
        "density_g_ml": density,
        "viscosity_mpa_s": viscosity,
        "conductivity_ms_cm": conductivity,
        "buffer_capacity_mmol_l_pH": buffer_capacity,
        "ionic_strength_proxy": round(ionic_strength_proxy, 5),
        "water_activity_proxy": water_activity_proxy,
        "rheology_model": "power_law_mycelial_suspension",
    }

