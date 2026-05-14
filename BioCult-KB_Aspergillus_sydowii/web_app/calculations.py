from math import log
from typing import List, Optional

from .schemas import ObservationBase, CalculationResult


def _safe_float(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def max_value(observations: List[ObservationBase], field: str) -> Optional[float]:
    values = [value for value in (_safe_float(getattr(obs, field)) for obs in observations) if value is not None]
    return max(values) if values else None


def average_value(observations: List[ObservationBase], field: str) -> Optional[float]:
    values = [value for value in (_safe_float(getattr(obs, field)) for obs in observations) if value is not None]
    return sum(values) / len(values) if values else None


def specific_growth_rate(observations: List[ObservationBase]) -> Optional[float]:
    sorted_obs = sorted(
        [obs for obs in observations if _safe_float(obs.biomass) is not None and _safe_float(obs.time_h) is not None],
        key=lambda o: o.time_h,
    )
    if len(sorted_obs) < 2:
        return None

    first = sorted_obs[0]
    last = sorted_obs[-1]
    x1 = _safe_float(first.biomass)
    x2 = _safe_float(last.biomass)
    t1 = _safe_float(first.time_h)
    t2 = _safe_float(last.time_h)

    if x1 is None or x2 is None or t1 is None or t2 is None or t2 - t1 <= 0 or x1 <= 0 or x2 <= 0:
        return None

    return log(x2 / x1) / (t2 - t1)


def estimate_uca(observations: List[ObservationBase]) -> Optional[float]:
    max_kla_value = max_value(observations, "kla")
    max_biomass_value = max_value(observations, "biomass")
    max_protein_value = max_value(observations, "protein")
    if max_kla_value is None:
        return None
    if max_protein_value:
        return max_kla_value / max_protein_value
    if max_biomass_value:
        return max_kla_value / max_biomass_value
    return None


def calculate_metrics(observations: List[ObservationBase]) -> CalculationResult:
    result = CalculationResult(
        max_kla=max_value(observations, "kla"),
        max_biomass=max_value(observations, "biomass"),
        specific_growth_rate_h=specific_growth_rate(observations),
        uca_estimate=estimate_uca(observations),
        average_pH=average_value(observations, "pH"),
        average_pO2=average_value(observations, "pO2_percent"),
        note="Оценка по доступным наблюдениям; при недостатке данных рекомендуется проверить аналитические контроли.",
    )
    return result
