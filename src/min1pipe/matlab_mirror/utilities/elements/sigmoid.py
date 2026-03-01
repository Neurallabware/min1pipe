"""Sigmoid utilities."""

from __future__ import annotations

from typing import Any

import numpy as np


def sigmoid(x: Any | None = None, a: Any | None = None, c: Any | None = None) -> np.ndarray:
    """Compute logistic function ``1 / (1 + exp(-a * (x - c)))``."""
    if x is None or a is None or c is None:
        raise ValueError("x, a, and c are required")
    x_arr = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-float(a) * (x_arr - float(c))))
