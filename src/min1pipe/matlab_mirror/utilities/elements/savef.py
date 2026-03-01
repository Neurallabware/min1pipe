"""HDF5-backed save helper compatible with MATLAB savef.m semantics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np


ArrayLike = Any


def _with_mat_suffix(filename: str | Path) -> Path:
    path = Path(filename)
    if path.suffix:
        return path
    return path.with_suffix(".mat")



def _as_mapping(varargin: tuple[Any, ...]) -> dict[str, ArrayLike]:
    # Supported call forms:
    # 1) savef(path, flag, {"name": arr, ...})
    # 2) savef(path, flag, "name", arr, "name2", arr2)
    # 3) savef(path, flag, [("name", arr), ...])
    if not varargin:
        return {}

    if len(varargin) == 1 and isinstance(varargin[0], dict):
        return {str(k): v for k, v in varargin[0].items()}

    if len(varargin) == 1 and isinstance(varargin[0], (list, tuple)):
        seq = varargin[0]
        if seq and isinstance(seq[0], (list, tuple)) and len(seq[0]) == 2:
            return {str(k): v for k, v in seq}

    if len(varargin) % 2 == 0:
        mapping: dict[str, ArrayLike] = {}
        for i in range(0, len(varargin), 2):
            key = varargin[i]
            val = varargin[i + 1]
            mapping[str(key)] = val
        return mapping

    raise ValueError(
        "Unsupported savef call shape. Use dict, list of pairs, or name/value pairs."
    )



def _as_3d(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 0:
        return arr.reshape((1, 1, 1))
    if arr.ndim == 1:
        return arr.reshape((arr.shape[0], 1, 1))
    if arr.ndim == 2:
        return arr[:, :, None]
    return arr



def savef(filename: Any | None = None, flag: Any | None = None, *varargin: Any) -> None:
    """Save or append arrays in HDF5 format.

    MATLAB source: ``utilities/elements/savef.m``.

    ``flag == 1`` creates/replaces datasets.
    ``flag != 1`` appends along the 3rd dimension.
    """
    if filename is None or flag is None:
        raise ValueError("filename and flag are required")

    path = _with_mat_suffix(str(filename))
    path.parent.mkdir(parents=True, exist_ok=True)

    mapping = _as_mapping(varargin)
    if not mapping:
        return

    mode = "a"
    with h5py.File(path, mode) as f:
        for name, value in mapping.items():
            ds_name = str(name).lstrip("/")
            arr = np.asarray(value)

            if int(flag) == 1:
                if ds_name in f:
                    del f[ds_name]
                f.create_dataset(ds_name, data=arr)
                continue

            arr3 = _as_3d(arr)
            if ds_name not in f:
                maxshape = (arr3.shape[0], arr3.shape[1], None)
                chunks = (arr3.shape[0], arr3.shape[1], 1)
                f.create_dataset(ds_name, data=arr3, maxshape=maxshape, chunks=chunks)
                continue

            ds = f[ds_name]
            cur = ds.shape
            if len(cur) == 2:
                ds.resize((cur[0], cur[1], 1))
                cur = ds.shape
            if len(cur) != 3:
                raise ValueError(f"Unsupported dataset rank for append: {ds_name} -> {cur}")

            if cur[0] != arr3.shape[0] or cur[1] != arr3.shape[1]:
                raise ValueError(
                    f"Shape mismatch when appending {ds_name}: existing={cur}, incoming={arr3.shape}"
                )

            start = cur[2]
            new_depth = start + arr3.shape[2]
            ds.resize((cur[0], cur[1], new_depth))
            ds[:, :, start:new_depth] = arr3.astype(ds.dtype, copy=False)
