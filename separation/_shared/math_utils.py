"""Math helpers shared by strict separation stages."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter1d


def normalize_01(arr: np.ndarray) -> np.ndarray:
    """Normalize array to [0, 1] with NaN-safe behavior."""
    data = np.asarray(arr, dtype=np.float64)
    if data.size == 0:
        return data.astype(np.float32)
    mn = float(np.nanmin(data))
    mx = float(np.nanmax(data))
    if mx <= mn:
        return np.zeros_like(data, dtype=np.float32)
    return ((data - mn) / (mx - mn)).astype(np.float32)


def disk_footprint(radius: int) -> np.ndarray:
    """Create a binary disk footprint similar to MATLAB `strel('disk', r)`."""
    r = int(max(1, radius))
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    return (xx * xx + yy * yy <= r * r).astype(bool)


def intensity_filter(maxall: np.ndarray) -> float:
    """Python equivalent for MATLAB `intensity_filter` heuristic."""
    vals = np.asarray(maxall, dtype=np.float64).ravel()
    vals = vals[vals > 1.0 / (2**8)]
    if vals.size == 0:
        return 0.0

    vals = np.sort(vals)
    ramp = np.linspace(vals[0], vals[-1], vals.size)
    score = vals - 0.2 * ramp
    sigma = max(1, int(round(vals.size / 10)))
    smooth = gaussian_filter1d(score, sigma=sigma, mode="nearest")
    idx = int(np.argmin(smooth))
    return float(min(np.percentile(vals, 50.0), vals[idx]))

