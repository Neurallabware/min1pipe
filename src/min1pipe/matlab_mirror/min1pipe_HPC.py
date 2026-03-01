"""Executable Python mirror for MATLAB ``min1pipe_HPC.m``.

This implementation is a correctness-first Python fallback that preserves the
public callable shape while replacing MATLAB-specific internals.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import tifffile
from scipy.ndimage import gaussian_filter, shift, zoom, maximum_filter

from .utilities.elements.default_parameters import default_parameters


@dataclass
class PipelineOutputs:
    file_name_to_save: str
    filename_raw: str
    filename_reg: str



def _ensure_grayscale(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return frame
    if frame.ndim == 3:
        return frame[..., :3].mean(axis=-1)
    raise ValueError(f"Unsupported frame shape: {frame.shape}")



def _load_video(path: Path) -> np.ndarray:
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

        frames = [_ensure_grayscale(np.asarray(frame)) for frame in iio.imiter(path)]
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



def _normalize_01(data: np.ndarray) -> np.ndarray:
    data = data.astype(np.float32, copy=False)
    mn = float(np.min(data))
    mx = float(np.max(data))
    if mx <= mn:
        return np.zeros_like(data, dtype=np.float32)
    return (data - mn) / (mx - mn)



def _temporal_downsample(data: np.ndarray, fsi: float, fsi_new: float) -> np.ndarray:
    if fsi_new <= 0:
        return data
    ratio = max(int(round(float(fsi) / float(fsi_new))), 1)
    return data[::ratio]



def _spatial_downsample(data: np.ndarray, spatialr: float) -> np.ndarray:
    if spatialr is None or spatialr <= 0 or abs(spatialr - 1.0) < 1e-8:
        return data
    # Keep frame axis unchanged.
    return zoom(data, zoom=(1.0, spatialr, spatialr), order=1)



def _phase_shift(reference: np.ndarray, frame: np.ndarray) -> tuple[float, float]:
    # FFT phase correlation shift estimate.
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



def _movement_correct(data: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ref = data[0]
    corrected = np.empty_like(data)
    corrected[0] = ref

    raw_score = np.zeros(data.shape[0], dtype=np.float32)
    corr_score = np.zeros(data.shape[0], dtype=np.float32)

    for i in range(1, data.shape[0]):
        dy, dx = _phase_shift(ref, data[i])
        raw_score[i] = np.hypot(dy, dx)
        corrected[i] = shift(data[i], shift=(dy, dx), order=1, mode="nearest")
        rdy, rdx = _phase_shift(ref, corrected[i])
        corr_score[i] = np.hypot(rdy, rdx)

    return corrected, raw_score, corr_score



def _detect_seeds(imax: np.ndarray, max_count: int = 80) -> np.ndarray:
    local_max = maximum_filter(imax, size=5) == imax
    threshold = np.percentile(imax, 97.0)
    mask = local_max & (imax >= threshold)
    ys, xs = np.where(mask)

    if ys.size == 0:
        flat = np.argmax(imax)
        y, x = np.unravel_index(flat, imax.shape)
        ys = np.array([y])
        xs = np.array([x])

    strengths = imax[ys, xs]
    order = np.argsort(strengths)[::-1][:max_count]
    ys = ys[order]
    xs = xs[order]
    return np.ravel_multi_index((ys, xs), imax.shape)



def _build_roi_and_traces(data: np.ndarray, seeds: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    n_frames, h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]

    rois: list[np.ndarray] = []
    for seed in seeds:
        y, x = np.unravel_index(int(seed), (h, w))
        roi = np.exp(-((yy - y) ** 2 + (xx - x) ** 2) / (2 * sigma**2))
        roi = roi / max(float(np.max(roi)), 1e-8)
        rois.append(roi.reshape(-1))

    roifn = np.stack(rois, axis=1).astype(np.float32)
    movie_flat = data.reshape(n_frames, -1).T

    # Weighted average signal per ROI.
    weights = roifn / np.maximum(np.sum(roifn, axis=0, keepdims=True), 1e-8)
    sigfn = (weights.T @ movie_flat).astype(np.float32)
    return roifn, sigfn



def _compute_dff(sigfn: np.ndarray) -> np.ndarray:
    baseline = np.min(sigfn, axis=1, keepdims=True)
    denom = np.maximum(baseline, 1e-6)
    return (sigfn - baseline) / denom



def _save_h5_mat(path: Path, arrays: dict[str, np.ndarray | Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        for key, value in arrays.items():
            f.create_dataset(key, data=np.asarray(value))



def min1pipe_HPC(
    Fsi: Any | None = None,
    Fsi_new: Any | None = None,
    spatialr: Any | None = None,
    se: Any | None = None,
    ismc: Any | None = None,
    flag: Any | None = None,
    path_name: Any | None = None,
    file_name: Any | None = None,
) -> tuple[Any, ...]:
    """Run MIN1PIPE in explicit-path mode.

    This function keeps MATLAB-compatible argument order and return ordering.
    """
    strict_parity = os.environ.get("MIN1PIPE_STRICT_PARITY", "0") == "1"
    if strict_parity:
        raise RuntimeError(
            "Strict parity mode is enabled, but min1pipe_HPC currently runs the Python fallback pipeline. "
            "Unset MIN1PIPE_STRICT_PARITY or use MATLAB reference artifacts for strict comparison."
        )

    params = default_parameters()

    fsi = float(params["Fsi"] if Fsi is None else Fsi)
    fsi_new = float(params["Fsi_new"] if Fsi_new is None else Fsi_new)
    spatialr_f = float(params["spatialr"] if spatialr is None else spatialr)
    neuron_size = float(params["neuron_size"] if se is None else se)
    use_mc = bool(True if ismc is None else ismc)
    _ = flag  # reserved for API compatibility

    if path_name is None or file_name is None:
        raise ValueError("path_name and file_name are required for min1pipe_HPC")

    pdir = Path(str(path_name)).expanduser().resolve()
    in_path = pdir / str(file_name)
    if not in_path.exists():
        raise FileNotFoundError(in_path)

    base = in_path.stem
    filename_raw = str(pdir / f"{base}_frame_all.mat")
    filename_reg = str(pdir / f"{base}_reg.mat")
    file_name_to_save = str(pdir / f"{base}_data_processed.mat")

    frames = _load_video(in_path)
    frames = _normalize_01(frames)
    frames = _temporal_downsample(frames, fsi, fsi_new)
    frames = _spatial_downsample(frames, spatialr_f)

    # raw projections
    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    enhanced = np.stack([gaussian_filter(frame, sigma=1.0) for frame in frames], axis=0)
    imaxy = np.max(enhanced, axis=0).astype(np.float32)

    if use_mc:
        reg, raw_score, corr_score = _movement_correct(enhanced)
    else:
        reg = enhanced
        raw_score = np.zeros(reg.shape[0], dtype=np.float32)
        corr_score = np.zeros(reg.shape[0], dtype=np.float32)

    imax = np.max(reg, axis=0).astype(np.float32)
    seedsfn = _detect_seeds(imax)
    roifn, sigfn = _build_roi_and_traces(reg, seedsfn, sigma=max(neuron_size, 1.0))

    spkfn = np.diff(sigfn, prepend=sigfn[:, :1], axis=1)
    spkfn = np.maximum(spkfn, 0).astype(np.float32)
    dff = _compute_dff(sigfn).astype(np.float32)

    bgfn = np.zeros((roifn.shape[0],), dtype=np.float32)
    bgffn = np.zeros((1, sigfn.shape[1]), dtype=np.float32)
    pixh, pixw = int(reg.shape[1]), int(reg.shape[2])

    params_out = {
        "Fsi": fsi,
        "Fsi_new": fsi_new,
        "spatialr": spatialr_f,
        "neuron_size": neuron_size,
        "ismc": int(use_mc),
    }

    _save_h5_mat(Path(filename_raw), {"frame_all": np.moveaxis(frames, 0, -1)})
    _save_h5_mat(Path(filename_reg), {"reg": np.moveaxis(reg, 0, -1), "imaxy": imaxy})
    _save_h5_mat(
        Path(file_name_to_save),
        {
            "roifn": roifn,
            "sigfn": sigfn,
            "dff": dff,
            "seedsfn": seedsfn.astype(np.int64),
            "spkfn": spkfn,
            "bgfn": bgfn,
            "bgffn": bgffn,
            "imax": imax,
            "pixh": np.asarray(pixh),
            "pixw": np.asarray(pixw),
            "corr_score": corr_score,
            "raw_score": raw_score,
            "Params": np.bytes_(str(params_out)),
            "imaxn": imaxn,
            "imaxy": imaxy,
            "imeanf": imeanf,
        },
    )

    outputs = PipelineOutputs(
        file_name_to_save=file_name_to_save,
        filename_raw=filename_raw,
        filename_reg=filename_reg,
    )
    return outputs.file_name_to_save, outputs.filename_raw, outputs.filename_reg
