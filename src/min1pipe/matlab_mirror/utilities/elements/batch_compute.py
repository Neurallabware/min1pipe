"""Batch-size computation utilities."""

from __future__ import annotations

import math
import os
import platform
from typing import Any


def _available_memory_bytes() -> int:
    system = platform.system().lower()

    if system == "linux":
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        kib = float(line.split()[1])
                        return int(kib * 1024)
        except OSError:
            pass

    try:
        import psutil  # type: ignore

        return int(psutil.virtual_memory().available)
    except Exception:
        pass

    fallback = int(os.environ.get("MIN1PIPE_FALLBACK_MEM_BYTES", str(2 * 1024**3)))
    return max(fallback, 1)


def batch_compute(nsize: Any | None = None) -> int:
    """Compute number of processing batches from requested bytes.

    MATLAB source: ``utilities/elements/batch_compute.m``.
    """
    if nsize is None:
        return 1

    nsize_f = float(nsize)
    if nsize_f <= 0:
        return 1

    memo = max(_available_memory_bytes() // 2, 1)
    return max(int(math.ceil(nsize_f / memo)), 1)
