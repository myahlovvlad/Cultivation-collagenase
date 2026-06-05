from __future__ import annotations

from typing import Any

import numpy as np
from pyDOE3 import lhs


DEFAULT_FACTORS = {
    "molasses_g_l": [12.0, 32.0],
    "peptone_g_l": [60.0, 110.0],
    "collagen_g_l": [3.0, 10.0],
    "aeration_vvm": [0.5, 1.2],
    "rpm": [180.0, 300.0],
}


def generate_doe(n_runs: int = 12, factors: dict[str, list[float]] | None = None, seed: int = 42) -> dict[str, Any]:
    factors = factors or DEFAULT_FACTORS
    names = list(factors)
    np.random.seed(seed)
    design = lhs(len(names), samples=n_runs, criterion="maximin")
    runs = []
    for index, row in enumerate(design, start=1):
        payload = {"run": index}
        for col, name in enumerate(names):
            low, high = factors[name]
            payload[name] = round(float(low + row[col] * (high - low)), 4)
        runs.append(payload)
    return {"design_type": "latin_hypercube", "n_runs": n_runs, "factors": factors, "runs": runs}

