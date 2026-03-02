"""Parameter defaults and mode-specific configuration for separation pipeline."""

from __future__ import annotations

from typing import Any


def strict_default_parameters() -> dict[str, Any]:
    """Default parameters aligned with MATLAB MIN1PIPE behavior."""
    return {
        "Fsi": 20.0,
        "Fsi_new": 20.0,
        "spatialr": 1.0,
        "neuron_size": 5,
        "ismc": True,
        "flag": 1,
        "anidenoise_iter": 4,
        "anidenoise_dt": 1.0 / 7.0,
        "anidenoise_kappa": 0.5,
        "anidenoise_opt": 1,
        "pix_select_sigthres": 0.8,
        "pix_select_corrthres": 0.6,
        "merge_roi_corrthres": 0.9,
        "refine_roi_ispara": False,
        "seed_random_iters": 50,
        "seed_max_per_iter": 500,
        "seed_gmm_prob_thres": 0.5,
        "max_seeds": 80,
        "seed_intensity_scale": 1.0,
        "trace_clean_tflag": 2,
        "rnn_model_path": None,
    }


def parity_default_parameters() -> dict[str, Any]:
    """Default parameters matching monolithic ``min1pipe_HPC.py`` behavior."""
    return {
        # QA_FIX(RC-01): parity defaults must mirror monolithic default_parameters.
        "Fsi": 20.0,
        "Fsi_new": 10.0,
        "spatialr": 0.5,
        "neuron_size": 5,
        "ismc": True,
        "flag": 1,
        "ttype": "single",
        "anidenoise_iter": 4,
        "anidenoise_dt": 1.0 / 7.0,
        "anidenoise_kappa": 0.5,
        "anidenoise_opt": 1,
        "anidenoise_ispara": 1,
        "bg_remove_ispara": 1,
        "mc_scl": 0.004,
        "mc_sigma_x": 5,
        "mc_sigma_f": 10,
        "mc_sigma_d": 1,
        "pix_select_sigthres": 0.8,
        "pix_select_corrthres": 0.6,
        "refine_roi_ispara": 1,
        "merge_roi_corrthres": 0.9,
        "max_seeds": 80,
        "seed_random_iters": 50,
        "seed_max_per_iter": 500,
        "seed_gmm_prob_thres": 0.5,
        "seed_intensity_scale": 1.0,
        "trace_clean_tflag": 2,
        "rnn_model_path": None,
    }


def default_parameters_for_mode(mode: str) -> dict[str, Any]:
    """Return stage defaults for ``mode`` (`parity` or `strict`)."""
    m = str(mode).strip().lower()
    if m == "strict":
        return strict_default_parameters()
    if m == "parity":
        return parity_default_parameters()
    raise ValueError(f"Unsupported mode: {mode!r}. Expected 'parity' or 'strict'.")
