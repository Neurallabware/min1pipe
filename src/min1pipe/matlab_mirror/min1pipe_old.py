"""Legacy compatibility wrapper for MATLAB ``min1pipe_old.m``."""

from __future__ import annotations

from typing import Any

from .min1pipe import min1pipe as _min1pipe_current



def min1pipe(
    Fsi: Any | None = None,
    Fsi_new: Any | None = None,
    spatialr: Any | None = None,
    se: Any | None = None,
    ismc: Any | None = None,
    flag: Any | None = None,
) -> tuple[Any, ...]:
    """Route legacy entrypoint to current Python fallback implementation."""
    return _min1pipe_current(Fsi, Fsi_new, spatialr, se, ismc, flag)
