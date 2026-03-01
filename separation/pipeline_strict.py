"""Deterministic strict pipeline orchestrator for separation modules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from separation._shared.fixtures import save_h5, save_npz, write_manifest
    from separation._shared.params import strict_default_parameters
    from separation.calcium_deconvolution import run_calcium_deconvolution
    from separation.component_filtering import run_component_filtering
    from separation.motion_correction import run_motion_correction
    from separation.source_detection import run_source_detection
except ModuleNotFoundError:  # support direct execution from separation/
    from _shared.fixtures import save_h5, save_npz, write_manifest
    from _shared.params import strict_default_parameters
    from calcium_deconvolution import run_calcium_deconvolution
    from component_filtering import run_component_filtering
    from motion_correction import run_motion_correction
    from source_detection import run_source_detection


@dataclass
class StrictPipelineResult:
    motion: Any
    source: Any
    component: Any
    deconv: Any


def run_full_pipeline_strict(
    video_path: str | Path,
    params: dict | None = None,
    artifact_dir: str | Path | None = None,
    verbose: bool = False,
) -> StrictPipelineResult:
    """Run strict separation pipeline with optional artifact logging."""
    cfg = strict_default_parameters()
    if params:
        cfg.update(params)

    if verbose:
        print("[strict] stage 1/4 motion_correction")
    mc = run_motion_correction(video_path, cfg, mode="strict")
    if verbose:
        print(f"[strict] motion done: frames={mc.nf} shape=({mc.pixh},{mc.pixw})")
        print("[strict] stage 2/4 source_detection")
    sd = run_source_detection(
        corrected_video=mc.corrected_video,
        imax=mc.imax,
        params=cfg,
        mode="strict",
    )
    if verbose:
        print(f"[strict] source done: components={sd.n_components}")
        print("[strict] stage 3/4 component_filtering")
    cf = run_component_filtering(
        roifn=sd.roifn,
        sigfn=sd.sigfn,
        seedsfn=sd.seedsfn,
        corrected_video=mc.corrected_video,
        params=cfg,
        datasmth=sd.datasmth,
        cutoff=sd.cutoff,
        pkcutoff=sd.pkcutoff,
        aux=sd.aux,
        mode="strict",
    )
    if verbose:
        print(f"[strict] component done: components={cf.seedsfn.size}")
        print("[strict] stage 4/4 calcium_deconvolution")
    cd = run_calcium_deconvolution(cf.sigfn, params=cfg, mode="strict")
    if verbose:
        print("[strict] deconvolution done")

    if artifact_dir is not None:
        out = Path(artifact_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        arrays = {
            "imaxn": mc.imaxn,
            "imaxy": mc.imaxy,
            "imax": mc.imax,
            "roifn": cf.roifn,
            "sigfn": cf.sigfn,
            "seedsfn": cf.seedsfn,
            "bgfn": cf.bgfn,
            "bgffn": cf.bgffn,
            "raw_score": mc.raw_score,
            "corr_score": mc.corr_score,
            "spkfn": cd.spkfn,
            "dff": cd.dff,
            "pixh": np.asarray(mc.pixh),
            "pixw": np.asarray(mc.pixw),
        }
        save_h5(out / "strict_pipeline_outputs.h5", arrays)
        save_npz(out / "strict_pipeline_outputs.npz", arrays)
        write_manifest(
            out / "strict_pipeline_manifest.json",
            {
                "video_path": str(Path(video_path).expanduser().resolve()),
                "params": cfg,
                "stages": ["motion_correction", "source_detection", "component_filtering", "calcium_deconvolution"],
            },
        )

    return StrictPipelineResult(motion=mc, source=sd, component=cf, deconv=cd)
