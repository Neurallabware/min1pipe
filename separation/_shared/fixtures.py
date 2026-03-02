"""Fixture I/O utilities for strict regression artifacts."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import h5py
import numpy as np


def load_pickle_compat(path: Path | str) -> Any:
    """Load pickle files robustly across numpy module layout changes."""
    p = Path(path)
    try:
        with p.open("rb") as f:
            return pickle.load(f)
    except ModuleNotFoundError as exc:
        msg = str(exc)
        if "numpy._core" not in msg:
            raise
        import sys
        import numpy.core as npcore

        sys.modules.setdefault("numpy._core", npcore)
        sys.modules.setdefault("numpy._core.numeric", npcore.numeric)
        with p.open("rb") as f:
            return pickle.load(f)


def save_pickle(path: Path | str, obj: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def save_npz(path: Path | str, arrays: dict[str, np.ndarray | Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: np.asarray(v) for k, v in arrays.items()}
    np.savez_compressed(p, **payload)


def load_npz(path: Path | str) -> dict[str, np.ndarray]:
    with np.load(Path(path), allow_pickle=False) as data:
        return {k: data[k] for k in data.files}


def save_h5(path: Path | str, arrays: dict[str, np.ndarray | Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(p, "w") as h5:
        for key, value in arrays.items():
            h5.create_dataset(key, data=np.asarray(value))


def load_h5(path: Path | str) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    with h5py.File(Path(path), "r") as h5:
        for key in h5.keys():
            out[key] = np.asarray(h5[key])
    return out


def write_manifest(path: Path | str, manifest: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2) + "\n")

