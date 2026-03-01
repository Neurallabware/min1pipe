"""High-level pipeline entrypoints."""

from __future__ import annotations

from typing import Any

from .matlab_mirror.min1pipe import min1pipe as _min1pipe_impl
from .matlab_mirror.min1pipe_HPC import min1pipe_HPC as _min1pipe_hpc_impl


def min1pipe(*args: Any, **kwargs: Any) -> Any:
    """Entry point compatible with MATLAB `min1pipe.m`."""
    return _min1pipe_impl(*args, **kwargs)


def min1pipe_hpc(*args: Any, **kwargs: Any) -> Any:
    """Entry point compatible with MATLAB `min1pipe_HPC.m`."""
    return _min1pipe_hpc_impl(*args, **kwargs)
