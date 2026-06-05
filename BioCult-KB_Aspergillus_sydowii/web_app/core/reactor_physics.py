from __future__ import annotations

from math import pi


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def reynolds_number(rpm: float, impeller_diameter_m: float, density_kg_m3: float, viscosity_mpa_s: float) -> float:
    n_s = max(0.0, rpm) / 60.0
    viscosity_pa_s = max(viscosity_mpa_s / 1000.0, 1e-9)
    return round(density_kg_m3 * n_s * impeller_diameter_m**2 / viscosity_pa_s, 3)


def power_per_volume_w_l(
    rpm: float,
    impeller_diameter_m: float = 0.04,
    density_kg_m3: float = 1018.0,
    volume_l: float = 1.7,
    power_number: float = 4.6,
) -> float:
    n_s = max(0.0, rpm) / 60.0
    power_w = power_number * density_kg_m3 * n_s**3 * impeller_diameter_m**5
    return round(power_w / max(volume_l, 1e-9), 6)


def superficial_gas_velocity_m_s(vvm: float, volume_l: float = 1.7, vessel_diameter_m: float = 0.13) -> float:
    gas_flow_m3_s = max(0.0, vvm) * max(volume_l, 0.0) / 1000.0 / 60.0
    area_m2 = pi * (vessel_diameter_m / 2.0) ** 2
    return round(gas_flow_m3_s / max(area_m2, 1e-12), 7)


def kla_vant_riet_h(
    rpm: float,
    vvm: float,
    viscosity_mpa_s: float,
    volume_l: float = 1.7,
    impeller_diameter_m: float = 0.04,
    vessel_diameter_m: float = 0.13,
) -> float:
    pv = power_per_volume_w_l(rpm, impeller_diameter_m=impeller_diameter_m, volume_l=volume_l)
    vg = superficial_gas_velocity_m_s(vvm, volume_l=volume_l, vessel_diameter_m=vessel_diameter_m)
    viscosity_penalty = 1.0 / (1.0 + max(0.0, viscosity_mpa_s - 1.0) * 0.18)
    kla = 112.0 * max(pv, 1e-9) ** 0.42 * max(vg, 1e-9) ** 0.31 * viscosity_penalty
    return round(max(0.0, kla), 5)


def oxygen_transfer_rate_mmol_l_h(kla_h: float, do_percent: float, do_sat_mmol_l: float = 0.24) -> float:
    driving = max(0.0, do_sat_mmol_l * (1.0 - do_percent / 100.0))
    return round(max(0.0, kla_h) * driving, 5)


def carbon_transfer_rate_mmol_l_h(kla_h: float, pco2_percent: float, henry_proxy: float = 0.033) -> float:
    return round(max(0.0, kla_h) * henry_proxy * max(0.0, pco2_percent - 0.04), 5)


def heat_generation_w(our_mmol_l_h: float, volume_l: float, delta_h_kj_mol_o2: float = 460.0) -> float:
    mol_o2_h = max(0.0, our_mmol_l_h) * max(0.0, volume_l) / 1000.0
    return round(mol_o2_h * delta_h_kj_mol_o2 * 1000.0 / 3600.0, 5)


def foam_risk(level_percent: float, conductivity_ms_cm: float, pco2_percent: float) -> dict:
    score = 100.0 * clamp((level_percent - 70.0) / 24.0 + conductivity_ms_cm / 85.0 + pco2_percent / 35.0)
    if score >= 72:
        status = "alarm"
    elif score >= 45:
        status = "watch"
    else:
        status = "normal"
    return {"foam_risk_index": round(score, 2), "status": status}


def reactor_state(
    rpm: float,
    vvm: float,
    viscosity_mpa_s: float,
    pO2_percent: float,
    pCO2_percent: float = 0.3,
    level_percent: float = 71.0,
    conductivity_ms_cm: float = 8.4,
    volume_l: float = 1.7,
) -> dict:
    kla = kla_vant_riet_h(rpm, vvm, viscosity_mpa_s, volume_l=volume_l)
    otr = oxygen_transfer_rate_mmol_l_h(kla, pO2_percent)
    ctr = carbon_transfer_rate_mmol_l_h(kla, pCO2_percent)
    heat = heat_generation_w(otr, volume_l)
    return {
        "reynolds": reynolds_number(rpm, 0.04, 1018.0, viscosity_mpa_s),
        "power_per_volume_w_l": power_per_volume_w_l(rpm, volume_l=volume_l),
        "superficial_gas_velocity_m_s": superficial_gas_velocity_m_s(vvm, volume_l=volume_l),
        "kla_h": kla,
        "OTR_mmol_l_h": otr,
        "CTR_mmol_l_h": ctr,
        "heat_generation_w": heat,
        **foam_risk(level_percent, conductivity_ms_cm, pCO2_percent),
    }

