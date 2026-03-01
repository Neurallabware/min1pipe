"""Contour plotting utility compatible with MATLAB ``plot_contour.m``."""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter

from min1pipe.io import normalize_seed_indices


def plot_contour(
    roifn: Any | None = None,
    sigfn: Any | None = None,
    seedsfn: Any | None = None,
    imax: Any | None = None,
    pixh: Any | None = None,
    pixw: Any | None = None,
) -> None:
    """Plot ROI contours on max-projection image with MATLAB coordinate semantics."""
    if roifn is None or sigfn is None or seedsfn is None or imax is None:
        raise ValueError("roifn, sigfn, seedsfn, and imax are required")

    roi = np.asarray(roifn, dtype=np.float64)
    sig = np.asarray(sigfn, dtype=np.float64)
    seeds = np.asarray(seedsfn).reshape(-1)
    imax_arr = np.asarray(imax, dtype=np.float64)

    if pixh is None or pixw is None:
        pixh, pixw = imax_arr.shape
    pixh_i = int(pixh)
    pixw_i = int(pixw)
    n_pixels = pixh_i * pixw_i

    if roi.ndim != 2:
        raise ValueError(f"Expected roifn to be 2D, got shape {roi.shape}")
    if roi.shape[0] != n_pixels and roi.shape[1] == n_pixels:
        roi = roi.T
    if roi.shape[0] != n_pixels:
        raise ValueError(f"roifn first dim should be {n_pixels}, got {roi.shape[0]}")

    seeds_i64 = seeds.astype(np.int64, copy=False)
    matlab_like = bool(np.all((seeds_i64 >= 1) & (seeds_i64 <= n_pixels)))
    seed_info = normalize_seed_indices(
        seeds=seeds_i64,
        pixh=pixh_i,
        pixw=pixw_i,
        source_layout="matlab" if matlab_like else "python",
    )

    # Infer ROI flattening order by agreement between ROI peak and seed locations.
    roi_order = "C"
    n_check = min(10, roi.shape[1], seed_info.seed_c0.shape[0])
    if n_check > 0:
        err_c = 0.0
        err_f = 0.0
        for i in range(n_check):
            peak_idx = int(np.nanargmax(roi[:, i]))
            r_c, c_c = np.unravel_index(peak_idx, (pixh_i, pixw_i), order="C")
            r_f, c_f = np.unravel_index(peak_idx, (pixh_i, pixw_i), order="F")
            rs = int(seed_info.row0[i])
            cs = int(seed_info.col0[i])
            err_c += abs(r_c - rs) + abs(c_c - cs)
            err_f += abs(r_f - rs) + abs(c_f - cs)
        roi_order = "F" if err_f < err_c else "C"

    ax = plt.gca()
    ax.imshow(imax_arr, vmin=0.0, vmax=0.8, cmap="viridis", origin="upper", interpolation="nearest")

    n_ids = min(roi.shape[1], sig.shape[0], seed_info.seed_f1.shape[0])
    for idx in range(n_ids):
        tmp = roi[:, idx].reshape((pixh_i, pixw_i), order=roi_order) * float(np.max(sig[idx, :]))
        tmp = gaussian_filter(tmp, sigma=3.0)
        level = float(np.max(tmp) * 0.8)
        if not np.isfinite(level) or level <= 0:
            continue

        # MATLAB logic:
        #   c = contour(flipud(tmp), [lvl lvl]);
        #   plot(c(1,:), pixh - c(2,:), 'r')
        cs = ax.contour(np.flipud(tmp), levels=[level], colors="none")
        for seg in cs.allsegs[0]:
            if seg.shape[0] < 2:
                continue
            ax.plot(seg[:, 0], pixh_i - seg[:, 1], "r", linewidth=1.0)
        if hasattr(cs, "remove"):
            cs.remove()

        # MATLAB labels: text(y(i), x(i), num2str(i))
        x_txt = float(seed_info.col0[idx] + 1)
        y_txt = float(seed_info.row0[idx] + 1)
        ax.text(x_txt, y_txt, str(idx + 1), fontsize=9)

    ax.set_title("Neural Contours")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(0, pixw_i - 1)
    ax.set_ylim(pixh_i - 1, 0)
