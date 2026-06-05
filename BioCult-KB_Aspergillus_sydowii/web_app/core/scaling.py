from __future__ import annotations

from math import pow

from .reactor_physics import kla_vant_riet_h


def predict_scaling(
    source_volume_l: float,
    target_volume_l: float,
    source_rpm: float,
    source_vvm: float,
    viscosity_mpa_s: float,
    target_vvm: float | None = None,
) -> dict:
    target_vvm = source_vvm if target_vvm is None else target_vvm
    source_kla = kla_vant_riet_h(source_rpm, source_vvm, viscosity_mpa_s, volume_l=source_volume_l)
    scale_ratio = max(target_volume_l, 1e-9) / max(source_volume_l, 1e-9)
    rpm_target = source_rpm * pow(scale_ratio, -0.18) * pow(max(source_vvm, 1e-9) / max(target_vvm, 1e-9), 0.22)
    target_kla = kla_vant_riet_h(rpm_target, target_vvm, viscosity_mpa_s, volume_l=target_volume_l)
    return {
        "source_kla_h": source_kla,
        "target_kla_h": target_kla,
        "recommended_rpm": round(rpm_target, 2),
        "target_vvm": round(target_vvm, 4),
        "kla_delta_percent": round((target_kla - source_kla) / max(source_kla, 1e-9) * 100.0, 3),
        "performance_risk": "watch" if abs(target_kla - source_kla) / max(source_kla, 1e-9) > 0.2 else "normal",
    }

