from __future__ import annotations

import json
from pathlib import Path

import h5py
import numpy as np

from min1pipe.matlab_mirror.utilities.elements.batch_compute import batch_compute
from min1pipe.matlab_mirror.utilities.elements.default_parameters import default_parameters
from min1pipe.matlab_mirror.utilities.elements.norm_inner import norm_inner
from min1pipe.matlab_mirror.utilities.elements.normalize import normalize
from min1pipe.matlab_mirror.utilities.elements.normalize_batch import normalize_batch
from min1pipe.matlab_mirror.utilities.elements.parse_type import parse_type
from min1pipe.matlab_mirror.utilities.elements.savef import savef
from min1pipe.matlab_mirror.utilities.elements.sigmoid import sigmoid


def test_inventory_mapping_complete() -> None:
    repo = Path(__file__).resolve().parents[2]
    inv = json.loads((repo / "artifacts" / "analysis" / "matlab_inventory.json").read_text())
    rows = inv["files"]
    assert rows, "inventory is empty"

    for row in rows:
        matlab = repo / row["path"]
        python = repo / row["python_path"]
        assert matlab.exists(), f"missing MATLAB source: {matlab}"
        assert python.exists(), f"missing mapped Python file: {python}"


def test_default_parameters_shape() -> None:
    params = default_parameters()
    for key in ("Fsi", "Fsi_new", "spatialr", "neuron_size", "mc_scl"):
        assert key in params


def test_parse_type_values() -> None:
    assert parse_type("double") == 8
    assert parse_type("single") == 4
    assert parse_type("uint16") == 2
    assert parse_type("uint8") == 1


def test_normalize_global() -> None:
    arr = np.array([[1.0, 3.0], [5.0, 7.0]])
    out = normalize(arr)
    assert np.isclose(float(out.min()), 0.0)
    assert np.isclose(float(out.max()), 1.0)


def test_sigmoid_and_norm_inner() -> None:
    s = sigmoid([0.0, 1.0], 2.0, 0.5)
    assert s.shape == (2,)
    ni = norm_inner(np.array([[1.0, 0.0]]), np.array([[1.0], [0.0]]))
    assert np.isclose(float(ni[0, 0]), 1.0)


def test_savef_and_normalize_batch(tmp_path: Path) -> None:
    path = tmp_path / "test_savef.mat"
    a = np.arange(6, dtype=np.float32).reshape(2, 3)
    b = np.arange(6, 12, dtype=np.float32).reshape(2, 3)

    savef(path, 2, {"frame_allt": a})
    savef(path, 2, {"frame_allt": b})

    with h5py.File(path, "r") as f:
        assert f["frame_allt"].shape == (2, 3, 2)

    normalize_batch(path, "frame_allt", 11.0, 0.0, [1, 3], 3)
    with h5py.File(path, "r") as f:
        data = np.asarray(f["frame_allt"])
        assert data.min() >= 0.0
        assert data.max() <= 1.0 + 1e-6


def test_batch_compute_nonzero() -> None:
    assert batch_compute(0) == 1
    assert batch_compute(1024) >= 1
