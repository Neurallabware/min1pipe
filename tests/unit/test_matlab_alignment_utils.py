from __future__ import annotations

from pathlib import Path

import h5py
import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt

from min1pipe.io import load_processed_mat, normalize_seed_indices
from min1pipe.matlab_mirror.utilities.postprocess.plot_contour import plot_contour


def test_normalize_seed_indices_matlab_and_python_roundtrip() -> None:
    pixh, pixw = 4, 5
    rows = np.array([0, 2, 3], dtype=np.int64)
    cols = np.array([1, 4, 0], dtype=np.int64)

    seeds_f1 = np.ravel_multi_index((rows, cols), (pixh, pixw), order="F") + 1
    seeds_c0 = np.ravel_multi_index((rows, cols), (pixh, pixw), order="C")

    info_m = normalize_seed_indices(seeds_f1, pixh=pixh, pixw=pixw, source_layout="matlab")
    assert np.array_equal(info_m.row0, rows)
    assert np.array_equal(info_m.col0, cols)
    assert np.array_equal(info_m.seed_c0, seeds_c0)

    info_p = normalize_seed_indices(seeds_c0, pixh=pixh, pixw=pixw, source_layout="python")
    assert np.array_equal(info_p.row0, rows)
    assert np.array_equal(info_p.col0, cols)
    assert np.array_equal(info_p.seed_f1, seeds_f1)


def _write_processed_file(path: Path, arrays: dict[str, np.ndarray]) -> None:
    with h5py.File(path, "w") as h5:
        for key, value in arrays.items():
            h5.create_dataset(key, data=value)


def test_load_processed_mat_canonicalizes_matlab_and_python_layouts(tmp_path: Path) -> None:
    pixh, pixw = 3, 4
    n_pixels = pixh * pixw
    n_roi = 2
    n_f = 5

    imaxn = np.arange(n_pixels, dtype=np.float64).reshape(pixh, pixw)
    imaxy = imaxn + 0.25
    imax = imaxn + 0.5

    roi_maps = np.zeros((pixh, pixw, n_roi), dtype=np.float64)
    roi_maps[0, 1, 0] = 1.0
    roi_maps[2, 3, 1] = 1.0
    roifn_c = roi_maps.reshape((n_pixels, n_roi), order="C")
    roifn_f = roi_maps.reshape((n_pixels, n_roi), order="F")

    sigfn = np.arange(n_roi * n_f, dtype=np.float64).reshape(n_roi, n_f)
    rows = np.array([0, 2], dtype=np.int64)
    cols = np.array([1, 3], dtype=np.int64)
    seeds_f1 = np.ravel_multi_index((rows, cols), (pixh, pixw), order="F") + 1
    seeds_c0 = np.ravel_multi_index((rows, cols), (pixh, pixw), order="C")

    raw_score = np.linspace(0, 1, n_f, dtype=np.float64)
    corr_score = np.linspace(1, 0, n_f, dtype=np.float64)

    matlab_path = tmp_path / "matlab_processed.mat"
    python_path = tmp_path / "python_processed.mat"

    _write_processed_file(
        matlab_path,
        {
            "imaxn": imaxn.T,  # h5py read pattern from MATLAB v7.3
            "imaxy": imaxy.T,
            "imax": imax.T,
            "roifn": roifn_f,
            "sigfn": sigfn.T,
            "seedsfn": seeds_f1,
            "raw_score": raw_score,
            "corr_score": corr_score,
            "pixh": np.asarray(pixh),
            "pixw": np.asarray(pixw),
        },
    )
    _write_processed_file(
        python_path,
        {
            "imaxn": imaxn,
            "imaxy": imaxy,
            "imax": imax,
            "roifn": roifn_c,
            "sigfn": sigfn,
            "seedsfn": seeds_c0,
            "raw_score": raw_score,
            "corr_score": corr_score,
            "pixh": np.asarray(pixh),
            "pixw": np.asarray(pixw),
        },
    )

    mat = load_processed_mat(matlab_path, source_layout="matlab")
    py = load_processed_mat(python_path, source_layout="python")

    for key in ("imaxn", "imaxy", "imax", "roifn", "sigfn", "seeds_c0", "raw_score", "corr_score"):
        assert np.allclose(np.asarray(mat[key]), np.asarray(py[key]))


def test_plot_contour_uses_non_mirrored_seed_geometry() -> None:
    pixh, pixw = 30, 30
    row0, col0 = 5, 22
    yy, xx = np.mgrid[0:pixh, 0:pixw]

    roi_map = np.exp(-((yy - row0) ** 2 + (xx - col0) ** 2) / (2.0 * 2.0**2))
    roifn = roi_map.reshape(-1, 1, order="C")
    sigfn = np.ones((1, 20), dtype=np.float64)
    imax = roi_map
    seed_f1 = np.array([np.ravel_multi_index((row0, col0), (pixh, pixw), order="F") + 1], dtype=np.int64)

    fig, ax = plt.subplots(figsize=(4, 4))
    plt.sca(ax)
    plot_contour(roifn, sigfn, seed_f1, imax, pixh, pixw)

    assert len(ax.texts) == 1
    txt_x, txt_y = ax.texts[0].get_position()
    assert abs(txt_x - (col0 + 1)) < 1e-6
    assert abs(txt_y - (row0 + 1)) < 1e-6

    ys: list[float] = []
    for line in ax.lines:
        ys.extend(line.get_ydata().tolist())
    assert ys, "expected at least one contour polyline"
    mean_y = float(np.mean(ys))

    near_seed = abs(mean_y - (row0 + 1))
    near_mirror = abs(mean_y - (pixh - (row0 + 1)))
    assert near_seed < near_mirror
    plt.close(fig)
