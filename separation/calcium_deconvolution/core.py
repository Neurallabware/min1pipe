"""Core calcium deconvolution implementation.

Current implementation: simplified spike inference via first-order difference.
The stub functions define the interface for the full CNMF-based deconvolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ._utils import default_parameters


@dataclass
class CalciumDeconvolutionResult:
    spkfn: np.ndarray   # (n_components, n_frames) inferred spike trains
    dff: np.ndarray      # (n_components, n_frames) dF/F normalized signals


def compute_dff(sigfn: np.ndarray) -> np.ndarray:
    """Compute delta-F/F normalized traces.

    Parameters
    ----------
    sigfn : ndarray, shape (n_components, n_frames)
        Filtered temporal signals.

    Returns
    -------
    dff : ndarray, shape (n_components, n_frames)
    """
    baseline = np.min(sigfn, axis=1, keepdims=True)
    denom = np.maximum(baseline, 1e-6)
    return ((sigfn - baseline) / denom).astype(np.float32)


def infer_spikes_simple(sigfn: np.ndarray) -> np.ndarray:
    """Simplified spike inference via positive first-order difference.

    Parameters
    ----------
    sigfn : ndarray, shape (n_components, n_frames)
        Filtered temporal signals.

    Returns
    -------
    spkfn : ndarray, shape (n_components, n_frames)
        Inferred spike trains (non-negative).
    """
    spkfn = np.diff(sigfn, prepend=sigfn[:, :1], axis=1)
    return np.maximum(spkfn, 0).astype(np.float32)


def run_calcium_deconvolution(
    sigfn: np.ndarray,
    params: dict | None = None,
) -> CalciumDeconvolutionResult:
    """Run calcium deconvolution on filtered signals.

    Parameters
    ----------
    sigfn : ndarray, shape (n_components, n_frames)
        Filtered temporal signals from component filtering.
    params : dict, optional
        Parameters. Relevant keys: 'method' ('simple_diff' or 'constrained_foopsi').
    """
    defaults = default_parameters()
    if params is not None:
        defaults.update(params)

    method = defaults.get("method", "simple_diff")

    if method == "constrained_foopsi":
        # Full CNMF-based deconvolution (not yet implemented)
        raise NotImplementedError(
            "constrained_foopsi method not yet implemented. "
            "Use method='simple_diff' or implement pure_refine_sig."
        )

    spkfn = infer_spikes_simple(sigfn)
    dff = compute_dff(sigfn)

    return CalciumDeconvolutionResult(spkfn=spkfn, dff=dff)


# ── Stub interfaces for full MATLAB-equivalent pipeline ──

def pure_refine_sig(sigfn, options):
    """Final spike inference via constrained_foopsi. (Not yet implemented)"""
    raise NotImplementedError("pure_refine_sig: MATLAB source utilities/elements/pure_refine_sig.m")


def constrained_foopsi(y, b=None, c1=None, g=None, sn=None, options=None):
    """Constrained deconvolution via FOOPSI. (Not yet implemented)"""
    raise NotImplementedError("constrained_foopsi: MATLAB source utilities/CNMF/constrained_foopsi.m")


def preprocess_data(Y, p=None):
    """Preprocess data for CNMF (noise estimation, AR coefficients). (Not yet implemented)"""
    raise NotImplementedError("preprocess_data: MATLAB source utilities/CNMF/preprocess_data.m")


def get_noise_fft(Y, options=None):
    """Estimate noise level from frequency domain. (Not yet implemented)"""
    raise NotImplementedError("get_noise_fft: MATLAB source utilities/CNMF/get_noise_fft.m")
