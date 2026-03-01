"""Index conversion helpers between Python and MATLAB conventions."""

from __future__ import annotations

import numpy as np


def f1_to_c0(seeds_f1: np.ndarray, pixh: int, pixw: int) -> np.ndarray:
    """Convert MATLAB linear indices (1-based, Fortran order) to C-order 0-based."""
    arr = np.asarray(seeds_f1, dtype=np.int64).reshape(-1)
    arr = np.clip(arr, 1, pixh * pixw)
    rows, cols = np.unravel_index(arr - 1, (pixh, pixw), order="F")
    return np.ravel_multi_index((rows, cols), (pixh, pixw), order="C").astype(np.int64)


def c0_to_f1(seeds_c0: np.ndarray, pixh: int, pixw: int) -> np.ndarray:
    """Convert Python C-order 0-based linear indices to MATLAB 1-based Fortran order."""
    arr = np.asarray(seeds_c0, dtype=np.int64).reshape(-1)
    arr = np.clip(arr, 0, pixh * pixw - 1)
    rows, cols = np.unravel_index(arr, (pixh, pixw), order="C")
    return (np.ravel_multi_index((rows, cols), (pixh, pixw), order="F") + 1).astype(np.int64)


def seed_rows_cols(seeds_c0: np.ndarray, pixh: int, pixw: int) -> tuple[np.ndarray, np.ndarray]:
    """Return row/col coordinates for C-order 0-based indices."""
    arr = np.asarray(seeds_c0, dtype=np.int64).reshape(-1)
    arr = np.clip(arr, 0, pixh * pixw - 1)
    rows, cols = np.unravel_index(arr, (pixh, pixw), order="C")
    return rows.astype(np.int64), cols.astype(np.int64)

