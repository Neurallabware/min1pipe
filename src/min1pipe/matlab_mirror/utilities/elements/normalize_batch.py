"""Batch normalization over HDF5-backed arrays."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py
import numpy as np


def normalize_batch(
    filename: Any | None = None,
    var: Any | None = None,
    imx: Any | None = None,
    imn: Any | None = None,
    idbatch: Any | None = None,
    ip: Any | None = None,
) -> str:
    """Normalize a dataset in-place over batched ranges.

    MATLAB source: ``utilities/elements/normalize_batch.m``.
    """
    if filename is None or var is None or imx is None or imn is None or idbatch is None:
        raise ValueError("filename, var, imx, imn, and idbatch are required")

    ip = 3 if ip is None else int(ip)
    ids = [int(v) for v in idbatch]
    if len(ids) < 2:
        return str(filename)

    scale = float(imx) - float(imn)
    if scale == 0:
        scale = 1.0

    path = Path(str(filename))
    ds_name = str(var).lstrip("/")

    with h5py.File(path, "r+") as f:
        if ds_name not in f:
            raise KeyError(f"Dataset not found: {ds_name}")
        ds = f[ds_name]

        for i in range(len(ids) - 1):
            start = ids[i] - 1
            stop = ids[i + 1] - 1
            if stop <= start:
                continue
            if ip == 2:
                tmp = ds[:, start:stop, ...]
                tmpn = (np.asarray(tmp, dtype=np.float64) - float(imn)) / scale
                ds[:, start:stop, ...] = tmpn.astype(ds.dtype, copy=False)
            else:
                tmp = ds[..., start:stop]
                tmpn = (np.asarray(tmp, dtype=np.float64) - float(imn)) / scale
                ds[..., start:stop] = tmpn.astype(ds.dtype, copy=False)

    return str(path)
