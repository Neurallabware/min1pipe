"""Tolerance registry for numeric parity checks."""

from __future__ import annotations

from typing import NamedTuple


class Tolerance(NamedTuple):
    rtol: float
    atol: float


DEFAULT_TOLERANCE = Tolerance(rtol=1e-5, atol=1e-7)

MODULE_OVERRIDES: dict[str, Tolerance] = {
    "utilities/CNMF/constrained_foopsi.m": Tolerance(rtol=1e-3, atol=1e-5),
    "utilities/elements/refine_sig.m": Tolerance(rtol=1e-3, atol=1e-5),
    "utilities/elements/refine_roi.m": Tolerance(rtol=1e-3, atol=1e-5),
    "utilities/elements/frame_reg.m": Tolerance(rtol=5e-3, atol=1e-4),
    "utilities/movement_correction/logdemons.m": Tolerance(rtol=5e-3, atol=1e-4),
}


def get_tolerance(matlab_path: str) -> Tolerance:
    """Get tolerance for a MATLAB module path."""
    return MODULE_OVERRIDES.get(matlab_path, DEFAULT_TOLERANCE)
