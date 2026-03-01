"""Type-width helpers compatible with MATLAB parse_type.m."""

from __future__ import annotations

from typing import Any

import numpy as np


def parse_type(ttype: Any | None = None) -> int:
    """Map data type to byte width.

    MATLAB source: ``utilities/elements/parse_type.m``.
    """
    if ttype is None:
        return 1

    if isinstance(ttype, np.dtype):
        key = ttype.name
    else:
        try:
            key = np.dtype(ttype).name
        except Exception:
            key = str(ttype).strip().lower()

    mapping = {
        "double": 8,
        "float64": 8,
        "single": 4,
        "float32": 4,
        "uint32": 4,
        "uint16": 2,
        "int16": 2,
        "int8": 1,
        "uint8": 1,
        "bool": 1,
        "bool_": 1,
    }
    return mapping.get(key, 1)
