"""Core source detection routines for calcium imaging.

Detects neuronal seed locations from a maximum-intensity projection,
builds Gaussian ROI spatial footprints around each seed, and extracts
temporal traces by weighted projection of the movie onto the footprints.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import maximum_filter

from ._utils import default_parameters


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class SourceDetectionResult:
    """Container for source detection outputs.

    Attributes
    ----------
    roifn : np.ndarray
        Spatial footprints, shape ``(n_pixels, n_components)``.
    sigfn : np.ndarray
        Temporal signals, shape ``(n_components, n_frames)``.
    seedsfn : np.ndarray
        Seed linear indices, shape ``(n_components,)``.
    n_components : int
        Number of detected components.
    """
    roifn: np.ndarray      # (n_pixels, n_components) spatial footprints
    sigfn: np.ndarray      # (n_components, n_frames) temporal signals
    seedsfn: np.ndarray    # (n_components,) seed linear indices
    n_components: int


# ---------------------------------------------------------------------------
# Seed detection
# ---------------------------------------------------------------------------

def detect_seeds(
    imax: np.ndarray,
    max_count: int = 80,
) -> np.ndarray:
    """Detect neuronal seed locations from a maximum-intensity projection.

    Seeds are local maxima above the 97th percentile of *imax*, ranked by
    brightness and capped at *max_count*.

    Parameters
    ----------
    imax : np.ndarray
        2-D maximum-intensity projection image (height, width).
    max_count : int, optional
        Maximum number of seeds to return.  Default 80.

    Returns
    -------
    np.ndarray
        1-D array of linear (ravelled) indices into *imax*.
    """
    local_max = maximum_filter(imax, size=5) == imax
    threshold = np.percentile(imax, 97.0)
    mask = local_max & (imax >= threshold)

    ys, xs = np.where(mask)

    # Fallback: if no seed survives, take the global maximum.
    if ys.size == 0:
        flat = np.argmax(imax)
        y, x = np.unravel_index(flat, imax.shape)
        ys = np.array([y])
        xs = np.array([x])

    # Rank by brightness and keep only the top *max_count*.
    strengths = imax[ys, xs]
    order = np.argsort(strengths)[::-1][:max_count]
    ys = ys[order]
    xs = xs[order]

    return np.ravel_multi_index((ys, xs), imax.shape)


# ---------------------------------------------------------------------------
# ROI building & trace extraction
# ---------------------------------------------------------------------------

def build_roi_and_traces(
    data: np.ndarray,
    seeds: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Build Gaussian ROI footprints and extract temporal traces.

    For every seed location a 2-D Gaussian with standard deviation *sigma*
    is placed on the field of view.  The movie is then projected onto the
    (normalised) footprints to obtain temporal traces.

    Parameters
    ----------
    data : np.ndarray
        Motion-corrected movie, shape ``(n_frames, height, width)``.
    seeds : np.ndarray
        1-D array of linear seed indices (into the height x width grid).
    sigma : float
        Standard deviation (in pixels) of the Gaussian footprint.

    Returns
    -------
    roifn : np.ndarray
        Spatial footprints, shape ``(n_pixels, n_components)``, float32.
    sigfn : np.ndarray
        Temporal traces, shape ``(n_components, n_frames)``, float32.
    """
    n_frames, h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]

    rois: list[np.ndarray] = []
    for seed in seeds:
        y, x = np.unravel_index(int(seed), (h, w))
        roi = np.exp(-((yy - y) ** 2 + (xx - x) ** 2) / (2 * sigma ** 2))
        roi = roi / max(float(np.max(roi)), 1e-8)
        rois.append(roi.reshape(-1))

    roifn = np.stack(rois, axis=1).astype(np.float32)

    # Weighted projection: traces = W^T @ movie_flat
    movie_flat = data.reshape(n_frames, -1).T           # (n_pixels, n_frames)
    weights = roifn / np.maximum(
        np.sum(roifn, axis=0, keepdims=True), 1e-8,
    )
    sigfn = (weights.T @ movie_flat).astype(np.float32)  # (n_components, n_frames)

    return roifn, sigfn


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_source_detection(
    corrected_video: np.ndarray,
    imax: np.ndarray,
    params: dict | None = None,
) -> SourceDetectionResult:
    """Run the full source detection stage.

    Parameters
    ----------
    corrected_video : np.ndarray
        Motion-corrected movie, shape ``(n_frames, height, width)``.
    imax : np.ndarray
        Maximum-intensity projection, shape ``(height, width)``.
    params : dict or None, optional
        Override dictionary.  Recognised keys:

        * ``"neuron_size"`` (float) -- Gaussian sigma for ROI footprints.
          Default ``5``.
        * ``"max_seeds"`` (int) -- Maximum number of seed locations.
          Default ``80``.

    Returns
    -------
    SourceDetectionResult
        Dataclass with ``roifn``, ``sigfn``, ``seedsfn``, ``n_components``.
    """
    # Merge caller-supplied params with defaults.
    cfg = default_parameters()
    if params is not None:
        cfg.update(params)

    neuron_size: float = cfg.get("neuron_size", 5)
    max_seeds: int = cfg.get("max_seeds", 80)

    # Step 1 -- seed detection
    seedsfn = detect_seeds(imax, max_count=max_seeds)

    # Step 2 -- ROI footprints + temporal traces
    roifn, sigfn = build_roi_and_traces(
        corrected_video, seedsfn, sigma=neuron_size,
    )

    return SourceDetectionResult(
        roifn=roifn,
        sigfn=sigfn,
        seedsfn=seedsfn,
        n_components=len(seedsfn),
    )
