"""Executable Python mirror for MATLAB ``min1pipe.m``."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .min1pipe_HPC import min1pipe_HPC



def min1pipe(
    Fsi: Any | None = None,
    Fsi_new: Any | None = None,
    spatialr: Any | None = None,
    se: Any | None = None,
    ismc: Any | None = None,
    flag: Any | None = None,
) -> tuple[Any, ...]:
    """Run MIN1PIPE with path discovery semantics.

    Python fallback behavior:
    - Uses ``MIN1PIPE_INPUT_FILE`` if set.
    - Otherwise falls back to ``demo/demo_data.tif`` in the repository root.
    """
    input_file = os.environ.get("MIN1PIPE_INPUT_FILE")
    if input_file:
        in_path = Path(input_file).expanduser().resolve()
    else:
        in_path = Path(__file__).resolve().parents[3] / "demo" / "demo_data.tif"

    if not in_path.exists():
        raise FileNotFoundError(
            "No input video found. Set MIN1PIPE_INPUT_FILE or place demo/demo_data.tif in repo root."
        )

    return min1pipe_HPC(
        Fsi=Fsi,
        Fsi_new=Fsi_new,
        spatialr=spatialr,
        se=se,
        ismc=ismc,
        flag=flag,
        path_name=str(in_path.parent),
        file_name=in_path.name,
    )
