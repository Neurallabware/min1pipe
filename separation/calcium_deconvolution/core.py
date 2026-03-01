"""Calcium deconvolution stage for MIN1PIPE separation pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter1d

try:
    from separation._shared.params import default_parameters_for_mode
except ModuleNotFoundError:  # support direct execution from separation/
    from _shared.params import default_parameters_for_mode


@dataclass
class CalciumDeconvolutionResult:
    spkfn: np.ndarray
    dff: np.ndarray


def compute_dff(sigfn: np.ndarray) -> np.ndarray:
    sig = np.asarray(sigfn, dtype=np.float32)
    baseline = np.percentile(sig, 10.0, axis=1, keepdims=True)
    denom = np.maximum(baseline, 1e-6)
    return ((sig - baseline) / denom).astype(np.float32)


def constrained_foopsi(y: np.ndarray, tau: float = 2.0) -> tuple[np.ndarray, np.ndarray]:
    """Lightweight nonnegative AR(1)-style deconvolution fallback."""
    trace = np.asarray(y, dtype=np.float64).reshape(-1)
    smooth = gaussian_filter1d(trace, sigma=max(1.0, tau / 2.0), mode="nearest")
    baseline = np.percentile(smooth, 10.0)
    calcium = np.maximum(smooth - baseline, 0.0)
    spikes = np.diff(calcium, prepend=calcium[:1])
    spikes = np.maximum(spikes, 0.0)
    return calcium.astype(np.float32), spikes.astype(np.float32)


def pure_refine_sig(sigfn: np.ndarray, options: dict | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Refine traces and infer spikes (pipeline-level equivalent of MATLAB pure_refine_sig)."""
    _ = options
    sig = np.asarray(sigfn, dtype=np.float32)
    out_c = np.empty_like(sig)
    out_s = np.empty_like(sig)
    for i in range(sig.shape[0]):
        c, s = constrained_foopsi(sig[i])
        out_c[i] = c
        out_s[i] = s
    return out_c, out_s


def _compute_dff_parity(sigfn: np.ndarray) -> np.ndarray:
    """Monolith-equivalent dF/F baseline using per-trace minimum."""
    sig = np.asarray(sigfn, dtype=np.float32)
    baseline = np.min(sig, axis=1, keepdims=True)
    denom = np.maximum(baseline, 1e-6)
    return ((sig - baseline) / denom).astype(np.float32)


def _run_calcium_deconvolution(sigfn: np.ndarray, params: dict | None = None, mode: str = "parity") -> CalciumDeconvolutionResult:
    cfg = default_parameters_for_mode(mode)
    if params:
        cfg.update(params)
    method = str(cfg.get("method", "foopsi_fallback"))
    sig = np.asarray(sigfn, dtype=np.float32)

    if str(mode).strip().lower() != "strict":
        # QA_FIX(RC-04): parity mode must match monolith np.diff + min-baseline dF/F.
        spk = np.maximum(np.diff(sig, prepend=sig[:, :1], axis=1), 0.0).astype(np.float32)
        dff = _compute_dff_parity(sig)
        return CalciumDeconvolutionResult(spkfn=spk, dff=dff)

    if method == "simple_diff":
        spk = np.maximum(np.diff(sig, prepend=sig[:, :1], axis=1), 0.0).astype(np.float32)
        dff = compute_dff(sig)
        return CalciumDeconvolutionResult(spkfn=spk, dff=dff)

    cref, spk = pure_refine_sig(sig, options=cfg.get("foopsi_options"))
    dff = compute_dff(cref)
    return CalciumDeconvolutionResult(spkfn=spk.astype(np.float32), dff=dff.astype(np.float32))


def run_calcium_deconvolution(
    sigfn: np.ndarray,
    params: dict | None = None,
    mode: str = "parity",
) -> CalciumDeconvolutionResult:
    """Run calcium deconvolution with mode-selectable behavior."""
    return _run_calcium_deconvolution(sigfn=sigfn, params=params, mode=mode)


def preprocess_data(Y: np.ndarray, p: int | None = None) -> dict:
    """Minimal preprocess shim for compatibility with CNMF-style interfaces."""
    data = np.asarray(Y, dtype=np.float32)
    return {
        "p": 2 if p is None else int(p),
        "sn": np.std(data, axis=-1).astype(np.float32),
    }


def get_noise_fft(Y: np.ndarray) -> np.ndarray:
    data = np.asarray(Y, dtype=np.float32)
    return np.std(data, axis=-1).astype(np.float32)
