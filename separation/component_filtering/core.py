"""Core component filtering implementation.

Current implementation: simplified filtering (scale + normalize).
The stub functions below define the interface for the full MATLAB-equivalent
pipeline (merge_roi, refine_roi, refine_sig, final_seeds_select, trace_clean).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ._utils import default_parameters


@dataclass
class ComponentFilteringResult:
    roifn: np.ndarray      # (n_pixels, n_components) filtered spatial footprints
    sigfn: np.ndarray      # (n_components, n_frames) filtered temporal signals
    seedsfn: np.ndarray    # (n_components,) seed locations
    bgfn: np.ndarray       # (n_pixels,) background spatial
    bgffn: np.ndarray      # (1, n_frames) background temporal


def run_component_filtering(
    roifn: np.ndarray,
    sigfn: np.ndarray,
    seedsfn: np.ndarray,
    corrected_video: np.ndarray,
    params: dict | None = None,
) -> ComponentFilteringResult:
    """Run component filtering on detected sources.

    Parameters
    ----------
    roifn : ndarray, shape (n_pixels, n_components)
        Spatial footprints from source detection.
    sigfn : ndarray, shape (n_components, n_frames)
        Temporal signals from source detection.
    seedsfn : ndarray, shape (n_components,)
        Seed pixel linear indices.
    corrected_video : ndarray, shape (n_frames, h, w)
        Motion-corrected video (used for background estimation).
    params : dict, optional
        Parameters. Relevant keys: 'neuron_size', 'merge_corrthres'.
    """
    defaults = default_parameters()
    if params is not None:
        defaults.update(params)

    n_pixels = corrected_video.shape[1] * corrected_video.shape[2]

    # Scale signals by max ROI weight per component
    roi_max = np.max(roifn, axis=0, keepdims=True)  # (1, n_components)
    roi_max_safe = np.where(roi_max > 0, roi_max, 1.0)

    sigfn_filtered = (roi_max.T * sigfn).astype(np.float32)
    roifn_filtered = (roifn / roi_max_safe).astype(np.float32)

    # Background (simplified: zeros)
    bgfn = np.zeros((n_pixels,), dtype=np.float32)
    bgffn = np.zeros((1, sigfn.shape[1]), dtype=np.float32)

    return ComponentFilteringResult(
        roifn=roifn_filtered,
        sigfn=sigfn_filtered,
        seedsfn=seedsfn.copy(),
        bgfn=bgfn,
        bgffn=bgffn,
    )


# -- Stub interfaces for full MATLAB-equivalent pipeline --
# These define the expected signatures for future implementation.

def merge_roi(m, roirf, sigrf, seedsupdt, imaxy,
              datasmthf, cutofff, pkcutofff, corrthres):
    """Merge highly correlated ROIs. (Not yet implemented)"""
    raise NotImplementedError("merge_roi: MATLAB source utilities/elements/merge_roi.m")


def refine_roi(m, sigmrg, bgfrf, roimrg, seedsmrg, noise,
               datasmth, cutoff, pkcutoff, ispara):
    """Refine ROI spatial footprints via CNMF. (Not yet implemented)"""
    raise NotImplementedError("refine_roi: MATLAB source utilities/elements/refine_roi.m")


def bg_update(m, roifn, sigfn):
    """Update background spatial/temporal components. (Not yet implemented)"""
    raise NotImplementedError("bg_update: MATLAB source utilities/elements/bg_update.m")


def refine_sig(m, roifn, bgfn, sigfn, bgffn, seedsfn,
               datasmth, cutoff, pkcutoff, p, options):
    """Refine temporal signals via CNMF. (Not yet implemented)"""
    raise NotImplementedError("refine_sig: MATLAB source utilities/elements/refine_sig.m")


def final_seeds_select(m, roifn, sigfn, seedsfn, datasmth,
                       cutoff, pkcutoff, sz, imaxy):
    """Final seed filtering. (Not yet implemented)"""
    raise NotImplementedError("final_seeds_select: MATLAB source utilities/elements/final_seeds_select.m")


def trace_clean(sigfn, Fsi_new, tflag):
    """Clean temporal traces. (Not yet implemented)"""
    raise NotImplementedError("trace_clean: MATLAB source utilities/elements/trace_clean.m")
