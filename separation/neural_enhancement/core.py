"""Neural enhancement stage aligned to MIN1PIPE MATLAB flow.

Pipeline:
1) dead-pixel suppression
2) dirt cleaning
3) anisotropic diffusion
4) morphological opening background removal
5) optional post suppression
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter, grey_opening, median_filter, white_tophat

from separation._shared.math_utils import disk_footprint, intensity_filter, normalize_01
from separation._shared.params import strict_default_parameters


@dataclass
class NeuralEnhancementResult:
    enhanced_video: np.ndarray
    imaxf: np.ndarray
    iminf: np.ndarray
    ibmean: np.ndarray
    imx2: float
    imn2: float


def _anisotropic_diffusion_2d(
    image: np.ndarray,
    niter: int = 4,
    dt: float = 1.0 / 7.0,
    kappa: float = 0.5,
    option: int = 1,
) -> np.ndarray:
    """Perona-Malik anisotropic diffusion for one 2D frame."""
    img = np.asarray(image, dtype=np.float64).copy()
    for _ in range(int(max(1, niter))):
        north = np.roll(img, -1, axis=0) - img
        south = np.roll(img, 1, axis=0) - img
        east = np.roll(img, -1, axis=1) - img
        west = np.roll(img, 1, axis=1) - img
        if int(option) == 1:
            c_n = np.exp(-(north / kappa) ** 2)
            c_s = np.exp(-(south / kappa) ** 2)
            c_e = np.exp(-(east / kappa) ** 2)
            c_w = np.exp(-(west / kappa) ** 2)
        else:
            c_n = 1.0 / (1.0 + (north / kappa) ** 2)
            c_s = 1.0 / (1.0 + (south / kappa) ** 2)
            c_e = 1.0 / (1.0 + (east / kappa) ** 2)
            c_w = 1.0 / (1.0 + (west / kappa) ** 2)
        img = img + dt * (c_n * north + c_s * south + c_e * east + c_w * west)
    return img.astype(np.float32)


def remove_dead_pixels(video: np.ndarray) -> np.ndarray:
    """Suppress temporally static outlier pixels."""
    data = np.asarray(video, dtype=np.float32).copy()
    mean_map = data.mean(axis=0)
    var_map = data.var(axis=0)
    dead = var_map < np.percentile(var_map, 2.0)
    extreme = (mean_map < np.percentile(mean_map, 5.0)) | (mean_map > np.percentile(mean_map, 99.0))
    mask = dead & extreme
    if not np.any(mask):
        return data
    for i in range(data.shape[0]):
        med = median_filter(data[i], size=3, mode="nearest")
        data[i][mask] = med[mask]
    return data


def dirt_clean(video: np.ndarray, neuron_size: int) -> np.ndarray:
    """MATLAB `dirt_clean`: max(gauss(frame)-frame, 0)."""
    data = np.asarray(video, dtype=np.float32)
    out = np.empty_like(data)
    sigma = float(max(1, neuron_size))
    for i in range(data.shape[0]):
        tmp = gaussian_filter(data[i], sigma=sigma, mode="nearest") - data[i]
        out[i] = np.maximum(tmp, 0.0)
    return out


def anisotropic_denoise(video: np.ndarray, params: dict) -> np.ndarray:
    data = np.asarray(video, dtype=np.float32)
    pad = int(max(1, params["neuron_size"]))
    out = np.empty((data.shape[0], data.shape[1] + 2 * pad, data.shape[2] + 2 * pad), dtype=np.float32)
    for i in range(data.shape[0]):
        frame = np.pad(data[i], ((pad, pad), (pad, pad)), mode="edge")
        out[i] = _anisotropic_diffusion_2d(
            frame,
            niter=int(params["anidenoise_iter"]),
            dt=float(params["anidenoise_dt"]),
            kappa=float(params["anidenoise_kappa"]),
            option=int(params["anidenoise_opt"]),
        )
    return out


def bg_remove(video_padded: np.ndarray, neuron_size: int) -> np.ndarray:
    """Morphological opening background removal with MATLAB-like crop."""
    data = np.asarray(video_padded, dtype=np.float32)
    sz = int(max(1, neuron_size))
    fp = disk_footprint(sz)
    out = np.empty((data.shape[0], data.shape[1] - 2 * sz, data.shape[2] - 2 * sz), dtype=np.float32)
    for i in range(data.shape[0]):
        frame = data[i]
        bg = grey_opening(frame, footprint=fp, mode="nearest")
        tmp = frame - bg
        out[i] = tmp[sz:-sz, sz:-sz]
    return out


def noise_suppress(video: np.ndarray, maxall: np.ndarray, fs: float, nflag: int) -> np.ndarray:
    """MATLAB-inspired post-suppression used in neural enhancement flow."""
    data = np.asarray(video, dtype=np.float32).copy()
    mask = maxall > intensity_filter(maxall)
    if int(nflag) == 1:
        low = ~mask
        data[:, low] = np.power(np.maximum(data[:, low], 0.0), 4)
    elif int(nflag) == 2:
        # Temporal detrending per masked pixel + gentle spatial smoothing.
        idx = np.where(mask.ravel())[0]
        if idx.size:
            flat = data.reshape(data.shape[0], -1)
            traces = flat[:, idx]
            base = np.quantile(traces, 0.2, axis=0, keepdims=True)
            traces = np.maximum(traces - base, 0.0)
            # Smooth along time in a MATLAB-like robust way.
            win = max(3, int(round(fs / 2.0)) | 1)
            kernel = np.hanning(win)
            kernel = kernel / max(kernel.sum(), 1e-8)
            padded = np.pad(traces, ((win, win), (0, 0)), mode="edge")
            sm = np.empty_like(traces)
            for j in range(traces.shape[1]):
                sm[:, j] = np.convolve(padded[:, j], kernel, mode="same")[win:-win]
            flat[:, idx] = sm
            data = flat.reshape(data.shape)
        for i in range(data.shape[0]):
            data[i] = gaussian_filter(data[i], sigma=1.0, mode="nearest")
    return normalize_01(data)


def run_neural_enhancement(raw_video: np.ndarray, params: dict | None = None) -> NeuralEnhancementResult:
    """Run strict neural enhancement stage."""
    cfg = strict_default_parameters()
    if params:
        cfg.update(params)

    data = np.asarray(raw_video, dtype=np.float32)
    data = remove_dead_pixels(data)
    dclean = dirt_clean(data, int(cfg["neuron_size"]))
    denoise_in = data + dclean
    denoise_pad = anisotropic_denoise(denoise_in, cfg)
    reg = bg_remove(denoise_pad, int(cfg["neuron_size"]))
    reg = noise_suppress(reg, np.max(reg, axis=0), float(cfg["Fsi_new"]), nflag=1)

    imaxf = np.max(reg, axis=0).astype(np.float32)
    iminf = np.min(reg, axis=0).astype(np.float32)
    bground = np.maximum(data[: reg.shape[0]] - reg, 0.0)
    fp_bg = disk_footprint(int(max(1, round(cfg["neuron_size"] * 6))))
    # Full white-tophat over every frame is very expensive; sample deterministically.
    stride = max(1, bground.shape[0] // 120)
    idx = np.arange(0, bground.shape[0], stride, dtype=np.int64)
    ib = np.empty((idx.size, bground.shape[1], bground.shape[2]), dtype=np.float32)
    for j, i in enumerate(idx):
        ib[j] = white_tophat(bground[i], footprint=fp_bg)
    ibmean = ib.mean(axis=0).astype(np.float32)

    return NeuralEnhancementResult(
        enhanced_video=reg.astype(np.float32),
        imaxf=imaxf,
        iminf=iminf,
        ibmean=ibmean,
        imx2=float(np.max(imaxf)),
        imn2=float(np.min(iminf)),
    )
