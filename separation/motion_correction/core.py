"""Motion correction stage for MIN1PIPE separation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np
import tifffile
from scipy.ndimage import gaussian_filter, shift, zoom

try:
    from separation._shared.math_utils import normalize_01
    from separation._shared.params import default_parameters_for_mode
    from separation.neural_enhancement import run_neural_enhancement
except ModuleNotFoundError:  # support direct execution from separation/
    from _shared.math_utils import normalize_01
    from _shared.params import default_parameters_for_mode
    from neural_enhancement import run_neural_enhancement


@dataclass
class MotionCorrectionResult:
    corrected_video: np.ndarray
    imaxy: np.ndarray
    imaxy_pre: np.ndarray
    imaxn: np.ndarray
    imeanf: np.ndarray
    imax: np.ndarray
    raw_score: np.ndarray
    corr_score: np.ndarray
    pixh: int
    pixw: int
    nf: int


def _ensure_grayscale(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return frame
    if frame.ndim == 3:
        return frame[..., :3].mean(axis=-1)
    raise ValueError(f"Unsupported frame shape: {frame.shape}")


def load_video(path: Path | str) -> np.ndarray:
    """Load TIFF/AVI/MAT into (n_frames, h, w) array."""
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in {".tif", ".tiff"}:
        data = tifffile.imread(p)
        if data.ndim == 2:
            data = data[None, ...]
        elif data.ndim == 4:
            data = _ensure_grayscale(data)
        elif data.ndim == 3 and data.shape[-1] in (3, 4):
            data = _ensure_grayscale(data)[None, ...]
        return np.asarray(data)

    if suffix == ".avi":
        import imageio.v3 as iio

        frames = [_ensure_grayscale(np.asarray(f)) for f in iio.imiter(p)]
        if not frames:
            raise ValueError(f"No frames read from {p}")
        return np.stack(frames, axis=0)

    if suffix == ".mat":
        try:
            with h5py.File(p, "r") as h5:
                for key in h5.keys():
                    arr = np.asarray(h5[key])
                    if arr.ndim == 3:
                        return np.moveaxis(arr, -1, 0)
        except OSError:
            pass
        from scipy.io import loadmat

        md = loadmat(p)
        for key, val in md.items():
            if key.startswith("__"):
                continue
            if isinstance(val, np.ndarray) and val.ndim == 3:
                return np.moveaxis(val, -1, 0)
        raise ValueError(f"No movie variable found in {p}")

    raise ValueError(f"Unsupported format: {p}")


def temporal_downsample(data: np.ndarray, fsi: float, fsi_new: float) -> np.ndarray:
    if fsi_new <= 0:
        return data
    ratio = max(int(round(float(fsi) / float(fsi_new))), 1)
    return data[::ratio]


def spatial_downsample(data: np.ndarray, spatialr: float) -> np.ndarray:
    if spatialr is None or spatialr <= 0 or abs(spatialr - 1.0) < 1e-8:
        return data
    return zoom(data, zoom=(1.0, spatialr, spatialr), order=1)


def phase_shift(reference: np.ndarray, frame: np.ndarray) -> tuple[float, float]:
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
    shifts[shifts > mid] -= np.array(reference.shape, dtype=np.float64)[shifts > mid]
    return float(shifts[0]), float(shifts[1])


def movement_correct(data: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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


def _run_motion_correction_parity(video_path: str | Path, cfg: dict) -> MotionCorrectionResult:
    """Parity path: mirror monolithic ``min1pipe_HPC.py`` preprocessing/order."""
    # QA_FIX(RC-02): parity mode must use monolith-equivalent Gaussian enhancement.
    use_mc = bool(cfg.get("use_mc", cfg.get("ismc", True)))
    p = Path(video_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)

    frames = load_video(p)
    frames = normalize_01(frames)
    frames = temporal_downsample(frames, float(cfg["Fsi"]), float(cfg["Fsi_new"]))
    frames = spatial_downsample(frames, float(cfg["spatialr"]))

    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    enhanced = np.stack([gaussian_filter(frame, sigma=1.0) for frame in frames], axis=0).astype(np.float32)
    imaxy_pre = np.max(enhanced, axis=0).astype(np.float32)

    if use_mc:
        reg, raw_score, corr_score = movement_correct(enhanced)
    else:
        reg = enhanced
        raw_score = np.zeros(reg.shape[0], dtype=np.float32)
        corr_score = np.zeros(reg.shape[0], dtype=np.float32)

    imax = np.max(reg, axis=0).astype(np.float32)
    nf, pixh, pixw = reg.shape
    return MotionCorrectionResult(
        corrected_video=reg.astype(np.float32),
        imaxy=imax,
        imaxy_pre=imaxy_pre,
        imaxn=imaxn,
        imeanf=imeanf,
        imax=imax,
        raw_score=raw_score.astype(np.float32),
        corr_score=corr_score.astype(np.float32),
        pixh=int(pixh),
        pixw=int(pixw),
        nf=int(nf),
    )


def _run_motion_correction_strict(video_path: str | Path, cfg: dict) -> MotionCorrectionResult:
    """Strict path with explicit neural enhancement stage."""
    use_mc = bool(cfg.get("use_mc", cfg.get("ismc", True)))
    p = Path(video_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)

    frames = load_video(p)
    frames = normalize_01(frames)
    frames = temporal_downsample(frames, float(cfg["Fsi"]), float(cfg["Fsi_new"]))
    frames = spatial_downsample(frames, float(cfg["spatialr"]))

    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    ne = run_neural_enhancement(frames, cfg)
    enhanced = ne.enhanced_video
    imaxy_pre = np.max(enhanced, axis=0).astype(np.float32)

    if use_mc:
        reg, raw_score, corr_score = movement_correct(enhanced)
    else:
        reg = enhanced
        raw_score = np.zeros(reg.shape[0], dtype=np.float32)
        corr_score = np.zeros(reg.shape[0], dtype=np.float32)

    imax = np.max(reg, axis=0).astype(np.float32)
    nf, pixh, pixw = reg.shape
    return MotionCorrectionResult(
        corrected_video=reg.astype(np.float32),
        imaxy=imax,
        imaxy_pre=imaxy_pre,
        imaxn=imaxn,
        imeanf=imeanf,
        imax=imax,
        raw_score=raw_score.astype(np.float32),
        corr_score=corr_score.astype(np.float32),
        pixh=int(pixh),
        pixw=int(pixw),
        nf=int(nf),
    )


def run_motion_correction(
    video_path: str | Path,
    params: dict | None = None,
    mode: str = "parity",
) -> MotionCorrectionResult:
    """Run motion correction in `parity` (default) or `strict` mode."""
    cfg = default_parameters_for_mode(mode)
    if params:
        cfg.update(params)
    if str(mode).strip().lower() == "strict":
        return _run_motion_correction_strict(video_path, cfg)
    return _run_motion_correction_parity(video_path, cfg)
