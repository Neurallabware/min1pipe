"""Canonical loading of MIN1PIPE processed HDF5 `.mat` artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import h5py
import numpy as np

Layout = Literal["matlab", "python"]

PROCESSED_KEYS = (
    "imaxn",
    "imaxy",
    "imax",
    "roifn",
    "sigfn",
    "seedsfn",
    "raw_score",
    "corr_score",
    "pixh",
    "pixw",
)


@dataclass(frozen=True)
class SeedIndexInfo:
    """Canonicalized seed index metadata."""

    seed_c0: np.ndarray
    row0: np.ndarray
    col0: np.ndarray
    seed_f1: np.ndarray


def _read_dataset(h5: h5py.File, key: str) -> np.ndarray:
    if key not in h5:
        raise KeyError(f"Missing dataset `{key}` in {h5.filename}")
    return np.asarray(h5[key])


def _scalar_int(arr: np.ndarray) -> int:
    if arr.size == 0:
        raise ValueError("Expected scalar value, got empty array")
    return int(np.ravel(arr)[0])


def seed_c0_to_rc(seed_c0: np.ndarray, pixh: int, pixw: int) -> tuple[np.ndarray, np.ndarray]:
    """Convert canonical C-order 0-based seed indices to row/col coordinates."""
    rows, cols = np.unravel_index(seed_c0.astype(np.int64), (pixh, pixw), order="C")
    return rows.astype(np.int64), cols.astype(np.int64)


def rc_to_seed_c0(rows: np.ndarray, cols: np.ndarray, pixh: int, pixw: int) -> np.ndarray:
    """Convert row/col coordinates to canonical C-order 0-based seed indices."""
    return np.ravel_multi_index((rows.astype(np.int64), cols.astype(np.int64)), (pixh, pixw), order="C")


def normalize_seed_indices(seeds: np.ndarray, pixh: int, pixw: int, source_layout: Layout) -> SeedIndexInfo:
    """Normalize seed indices from MATLAB/Python layout to canonical C-order 0-based indices."""
    seed_in = np.asarray(seeds).reshape(-1).astype(np.int64, copy=False)
    n_pixels = int(pixh) * int(pixw)

    if source_layout == "matlab":
        # MATLAB linear indexing is 1-based and column-major.
        seed_f1 = np.clip(seed_in, 1, n_pixels)
        rows, cols = np.unravel_index(seed_f1 - 1, (pixh, pixw), order="F")
        seed_c0 = rc_to_seed_c0(rows, cols, pixh, pixw)
        return SeedIndexInfo(
            seed_c0=seed_c0.astype(np.int64),
            row0=rows.astype(np.int64),
            col0=cols.astype(np.int64),
            seed_f1=seed_f1.astype(np.int64),
        )

    # Python canonical form is 0-based C-order.
    seed_c0 = np.clip(seed_in, 0, n_pixels - 1)
    rows, cols = seed_c0_to_rc(seed_c0, pixh, pixw)
    seed_f1 = np.ravel_multi_index((rows, cols), (pixh, pixw), order="F") + 1
    return SeedIndexInfo(
        seed_c0=seed_c0.astype(np.int64),
        row0=rows.astype(np.int64),
        col0=cols.astype(np.int64),
        seed_f1=seed_f1.astype(np.int64),
    )


def _canonicalize_projection(arr: np.ndarray, source_layout: Layout) -> np.ndarray:
    out = np.asarray(arr)
    if out.ndim != 2:
        return out
    if source_layout == "matlab":
        # MATLAB v7.3 HDF5 matrices are read transposed with h5py.
        return out.T
    return out


def _canonicalize_sigfn(sig: np.ndarray, n_roi: int) -> np.ndarray:
    out = np.asarray(sig, dtype=np.float64)
    if out.ndim == 1:
        out = out.reshape(1, -1)
    if out.ndim != 2:
        raise ValueError(f"`sigfn` must be 2D, got shape {out.shape}")
    if out.shape[0] == n_roi:
        return out
    if out.shape[1] == n_roi:
        return out.T
    raise ValueError(f"`sigfn` shape {out.shape} incompatible with n_roi={n_roi}")


def _canonicalize_roifn(roifn: np.ndarray, pixh: int, pixw: int, source_layout: Layout) -> np.ndarray:
    out = np.asarray(roifn, dtype=np.float64)
    n_pixels = pixh * pixw
    if out.ndim != 2:
        raise ValueError(f"`roifn` must be 2D, got shape {out.shape}")

    if out.shape[0] != n_pixels and out.shape[1] == n_pixels:
        out = out.T
    if out.shape[0] != n_pixels:
        raise ValueError(f"`roifn` first dimension should be {n_pixels}, got {out.shape[0]}")

    if source_layout == "matlab":
        # MATLAB columns are Fortran-linearized pixels; convert to C-linearized pixels.
        n_roi = out.shape[1]
        roi_maps = out.reshape((pixh, pixw, n_roi), order="F")
        return roi_maps.reshape((n_pixels, n_roi), order="C")

    return out


def load_processed_mat(path: str | Path, source_layout: Layout = "python") -> dict[str, Any]:
    """Load MIN1PIPE processed `.mat` output into canonical orientation/index conventions."""
    mat_path = Path(path).expanduser().resolve()
    if source_layout not in ("matlab", "python"):
        raise ValueError(f"Unsupported source layout `{source_layout}`")

    with h5py.File(mat_path, "r") as h5:
        raw = {k: _read_dataset(h5, k) for k in PROCESSED_KEYS}

    pixh = _scalar_int(raw["pixh"])
    pixw = _scalar_int(raw["pixw"])

    imaxn = _canonicalize_projection(raw["imaxn"], source_layout).astype(np.float64, copy=False)
    imaxy = _canonicalize_projection(raw["imaxy"], source_layout).astype(np.float64, copy=False)
    imax = _canonicalize_projection(raw["imax"], source_layout).astype(np.float64, copy=False)
    roifn = _canonicalize_roifn(raw["roifn"], pixh, pixw, source_layout)

    n_roi = int(roifn.shape[1])
    sigfn = _canonicalize_sigfn(raw["sigfn"], n_roi=n_roi)

    seed_info = normalize_seed_indices(raw["seedsfn"], pixh=pixh, pixw=pixw, source_layout=source_layout)
    raw_score = np.asarray(raw["raw_score"], dtype=np.float64).reshape(-1)
    corr_score = np.asarray(raw["corr_score"], dtype=np.float64).reshape(-1)

    return {
        "path": str(mat_path),
        "source_layout": source_layout,
        "pixh": pixh,
        "pixw": pixw,
        "imaxn": imaxn,
        "imaxy": imaxy,
        "imax": imax,
        "roifn": roifn,
        "sigfn": sigfn,
        "seeds_c0": seed_info.seed_c0,
        "seeds_f1": seed_info.seed_f1,
        "seed_rows0": seed_info.row0,
        "seed_cols0": seed_info.col0,
        "raw_score": raw_score,
        "corr_score": corr_score,
    }
