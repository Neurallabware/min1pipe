"""Core motion correction implementation for calcium imaging.

Extracted from MIN1PIPE ``min1pipe_HPC.py``. This module is fully
self-contained and reproduces the motion-correction portion of the
original pipeline exactly.

Pipeline stages:
    1. Load raw video from disk (TIFF, AVI, or MAT)
    2. Normalize pixel intensities to [0, 1]
    3. Temporal downsample (Fsi -> Fsi_new)
    4. Spatial downsample (by spatialr factor)
    5. Compute pre-correction projections
    6. Neural enhancement via Gaussian filtering
    7. Phase-correlation motion correction
    8. Compute post-correction projections and quality scores
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import tifffile
from scipy.ndimage import gaussian_filter, shift, zoom

from ._utils import default_parameters


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class MotionCorrectionResult:
    """Container for all motion correction outputs."""

    corrected_video: np.ndarray   # (nframes, h, w)
    imaxy: np.ndarray             # (h, w) - max projection of enhanced video (pre-correction)
    imaxy_pre: np.ndarray         # (h, w) - same as imaxy, kept for explicit naming
    imaxn: np.ndarray             # (h, w) - max projection of normalized video
    imeanf: np.ndarray            # (h, w) - mean projection of normalized video
    imax: np.ndarray              # (h, w) - max projection of corrected video
    raw_score: np.ndarray         # (nframes,) - displacement before correction
    corr_score: np.ndarray        # (nframes,) - residual displacement after correction
    pixh: int                     # frame height (pixels)
    pixw: int                     # frame width (pixels)
    nf: int                       # number of frames


# ---------------------------------------------------------------------------
# Video loading
# ---------------------------------------------------------------------------

def _ensure_grayscale(frame: np.ndarray) -> np.ndarray:
    """Convert an RGB/RGBA frame to grayscale by averaging colour channels."""
    if frame.ndim == 2:
        return frame
    if frame.ndim == 3:
        return frame[..., :3].mean(axis=-1)
    raise ValueError(f"Unsupported frame shape: {frame.shape}")


def load_video(path: Path | str) -> np.ndarray:
    """Load a video file and return a (nframes, h, w) float array.

    Supported formats: TIFF (.tif/.tiff), AVI (.avi), MATLAB (.mat).
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in {".tif", ".tiff"}:
        data = tifffile.imread(path)
        if data.ndim == 2:
            data = data[None, :, :]
        elif data.ndim == 3 and data.shape[-1] in (3, 4):
            data = _ensure_grayscale(data)[None, :, :]
        elif data.ndim == 3:
            pass
        elif data.ndim == 4:
            data = _ensure_grayscale(data)
        else:
            raise ValueError(f"Unsupported TIFF shape: {data.shape}")
        return np.asarray(data)

    if suffix == ".avi":
        import imageio.v3 as iio

        frames = [
            _ensure_grayscale(np.asarray(frame)) for frame in iio.imiter(path)
        ]
        if not frames:
            raise ValueError(f"No frames read from {path}")
        return np.stack(frames, axis=0)

    if suffix == ".mat":
        # Support v7.3-style HDF5 first.
        try:
            with h5py.File(path, "r") as f:
                for key in f.keys():
                    arr = np.asarray(f[key])
                    if arr.ndim == 3:
                        return np.moveaxis(arr, -1, 0)
        except OSError:
            pass

        from scipy.io import loadmat

        m = loadmat(path)
        for key, val in m.items():
            if key.startswith("__"):
                continue
            if isinstance(val, np.ndarray) and val.ndim == 3:
                return np.moveaxis(val, -1, 0)
        raise ValueError(f"No 3D movie variable found in {path}")

    raise ValueError(f"Unsupported file format: {path}")


# ---------------------------------------------------------------------------
# Pre-processing helpers
# ---------------------------------------------------------------------------

def normalize_01(data: np.ndarray) -> np.ndarray:
    """Normalize pixel intensities to [0, 1] globally."""
    data = data.astype(np.float32, copy=False)
    mn = float(np.min(data))
    mx = float(np.max(data))
    if mx <= mn:
        return np.zeros_like(data, dtype=np.float32)
    return (data - mn) / (mx - mn)


def temporal_downsample(
    data: np.ndarray, fsi: float, fsi_new: float
) -> np.ndarray:
    """Downsample along the time axis by striding.

    Parameters
    ----------
    data : ndarray (nframes, h, w)
    fsi : float
        Original sampling rate (Hz).
    fsi_new : float
        Target sampling rate (Hz).
    """
    if fsi_new <= 0:
        return data
    ratio = max(int(round(float(fsi) / float(fsi_new))), 1)
    return data[::ratio]


def spatial_downsample(data: np.ndarray, spatialr: float) -> np.ndarray:
    """Downsample spatial dimensions by a zoom factor.

    Parameters
    ----------
    data : ndarray (nframes, h, w)
    spatialr : float
        Spatial zoom factor (e.g. 0.5 = half resolution).
    """
    if spatialr is None or spatialr <= 0 or abs(spatialr - 1.0) < 1e-8:
        return data
    # Keep frame axis unchanged.
    return zoom(data, zoom=(1.0, spatialr, spatialr), order=1)


# ---------------------------------------------------------------------------
# Motion correction
# ---------------------------------------------------------------------------

def phase_shift(
    reference: np.ndarray, frame: np.ndarray
) -> tuple[float, float]:
    """Estimate translational shift via FFT phase correlation.

    Parameters
    ----------
    reference : 2-D array
        Reference frame.
    frame : 2-D array
        Frame to align.

    Returns
    -------
    dy, dx : float
        Estimated shift in pixels (row, col).
    """
    f_ref = np.fft.fftn(reference)
    f_cur = np.fft.fftn(frame)
    cps = f_ref * np.conj(f_cur)
    denom = np.abs(cps)
    denom[denom == 0] = 1.0
    cps /= denom
    corr = np.fft.ifftn(cps)
    maxima = np.unravel_index(np.argmax(np.abs(corr)), corr.shape)
    shifts = np.array(maxima, dtype=np.float64)
    mid = np.array(reference.shape, dtype=np.float64) // 2
    shifts[shifts > mid] -= np.array(reference.shape, dtype=np.float64)[
        shifts > mid
    ]
    return float(shifts[0]), float(shifts[1])


def movement_correct(
    data: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Correct translational motion via phase correlation.

    The first frame is used as the reference.  For each subsequent frame
    the shift is estimated, applied, and then re-estimated to produce
    both a *raw* displacement score and a post-correction *residual*
    score.

    Parameters
    ----------
    data : ndarray (nframes, h, w)
        Enhanced video stack.

    Returns
    -------
    corrected : ndarray (nframes, h, w)
        Motion-corrected video.
    raw_score : ndarray (nframes,)
        Euclidean displacement before correction.
    corr_score : ndarray (nframes,)
        Residual displacement after correction.
    """
    ref = data[0]
    corrected = np.empty_like(data)
    corrected[0] = ref

    raw_score = np.zeros(data.shape[0], dtype=np.float32)
    corr_score = np.zeros(data.shape[0], dtype=np.float32)

    for i in range(1, data.shape[0]):
        dy, dx = phase_shift(ref, data[i])
        raw_score[i] = np.hypot(dy, dx)
        corrected[i] = shift(data[i], shift=(dy, dx), order=1, mode="nearest")
        rdy, rdx = phase_shift(ref, corrected[i])
        corr_score[i] = np.hypot(rdy, rdx)

    return corrected, raw_score, corr_score


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_motion_correction(
    video_path: str | Path,
    params: dict | None = None,
) -> MotionCorrectionResult:
    """Run the full motion-correction pipeline on a raw video file.

    This reproduces the motion-correction portion of ``min1pipe_HPC``
    exactly.  The remaining pipeline stages (seed detection, ROI
    extraction, etc.) are intentionally excluded.

    Parameters
    ----------
    video_path : str or Path
        Path to a raw video file (TIFF, AVI, or MAT).
    params : dict, optional
        Override default MIN1PIPE parameters.  Recognised keys:

        * ``Fsi`` -- original sampling rate in Hz  (default 20)
        * ``Fsi_new`` -- target sampling rate in Hz  (default 10)
        * ``spatialr`` -- spatial zoom factor  (default 0.5)
        * ``ismc`` -- whether to run motion correction (default True)

    Returns
    -------
    MotionCorrectionResult
        Dataclass holding the corrected video, projections, quality
        scores, and dimension metadata.
    """
    # ---- resolve parameters ------------------------------------------------
    defaults = default_parameters()
    if params is not None:
        defaults.update(params)
    p = defaults

    fsi = float(p["Fsi"])
    fsi_new = float(p["Fsi_new"])
    spatialr_f = float(p["spatialr"])
    use_mc = bool(p.get("ismc", True))

    # ---- load & pre-process ------------------------------------------------
    video_path = Path(video_path).expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(video_path)

    frames = load_video(video_path)
    frames = normalize_01(frames)
    frames = temporal_downsample(frames, fsi, fsi_new)
    frames = spatial_downsample(frames, spatialr_f)

    # ---- raw projections ---------------------------------------------------
    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    # ---- neural enhancement (gaussian smoothing) ---------------------------
    enhanced = np.stack(
        [gaussian_filter(frame, sigma=1.0) for frame in frames], axis=0
    )
    imaxy = np.max(enhanced, axis=0).astype(np.float32)

    # ---- motion correction -------------------------------------------------
    if use_mc:
        reg, raw_score, corr_score = movement_correct(enhanced)
    else:
        reg = enhanced
        raw_score = np.zeros(reg.shape[0], dtype=np.float32)
        corr_score = np.zeros(reg.shape[0], dtype=np.float32)

    # ---- post-correction projection ----------------------------------------
    imax = np.max(reg, axis=0).astype(np.float32)

    nf, pixh, pixw = reg.shape

    return MotionCorrectionResult(
        corrected_video=reg,
        imaxy=imaxy,
        imaxy_pre=imaxy,
        imaxn=imaxn,
        imeanf=imeanf,
        imax=imax,
        raw_score=raw_score,
        corr_score=corr_score,
        pixh=pixh,
        pixw=pixw,
        nf=nf,
    )
