from __future__ import annotations

from statistics import mean, pstdev


def update_mu_max(observed_mu_h: list[float], prior_mu_max_h: float = 0.095) -> dict:
    clean = [value for value in observed_mu_h if value >= 0]
    if not clean:
        return {"mu_max_h": prior_mu_max_h, "uncertainty": 1.0, "status": "no_observations"}
    estimate = max(clean)
    blended = 0.65 * prior_mu_max_h + 0.35 * estimate
    uncertainty = min(1.0, (pstdev(clean) if len(clean) > 1 else 0.03) / max(mean(clean), 1e-9))
    return {"mu_max_h": round(blended, 6), "uncertainty": round(uncertainty, 5), "status": "updated"}

