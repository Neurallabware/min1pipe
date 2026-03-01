#!/usr/bin/env python3
"""Run monolithic MIN1PIPE capture with boundary artifacts for QA parity."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.ndimage import gaussian_filter

REPO = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(REPO / "src"))

from min1pipe.matlab_mirror.min1pipe_HPC import (  # noqa: E402
    _build_roi_and_traces,
    _compute_dff,
    _detect_seeds,
    _load_video,
    _movement_correct,
    _normalize_01,
    _spatial_downsample,
    _temporal_downsample,
)
from min1pipe.matlab_mirror.utilities.elements.default_parameters import (  # noqa: E402
    default_parameters,
)

SUPPORTED_SUFFIXES = {".tif", ".tiff", ".avi", ".mat"}


@dataclass
class FileEntry:
    dataset_root: str
    file_path: str
    file_rel: str
    dataset_key: str
    file_key: str
    size_bytes: int
    sha256: str


def _slugify(path: Path) -> str:
    txt = str(path).strip().replace("\\", "/")
    out = [ch if ch.isalnum() else "_" for ch in txt]
    return "".join(out).strip("_")


def _sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _discover_files(roots: list[Path]) -> tuple[list[FileEntry], list[dict[str, str]]]:
    entries: list[FileEntry] = []
    skipped: list[dict[str, str]] = []
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            skipped.append({"file": str(root), "reason": "missing_root"})
            continue
        files = sorted(p for p in root.rglob("*") if p.is_file())
        for path in files:
            suffix = path.suffix.lower()
            rel = path.relative_to(root)
            if suffix not in SUPPORTED_SUFFIXES:
                skipped.append({"file": str(path), "reason": f"unsupported_format:{suffix or '<none>'}"})
                continue
            entries.append(
                FileEntry(
                    dataset_root=str(root),
                    file_path=str(path),
                    file_rel=str(rel),
                    dataset_key=_slugify(root),
                    file_key=_slugify(rel.with_suffix(Path(rel).suffix)),
                    size_bytes=path.stat().st_size,
                    sha256=_sha256(path),
                )
            )
    return entries, skipped


def _capture_monolithic(file_path: Path, params: dict[str, Any], max_frames: int | None = None) -> dict[str, np.ndarray]:
    fsi = float(params["Fsi"])
    fsi_new = float(params["Fsi_new"])
    spatialr = float(params["spatialr"])
    neuron_size = float(params["neuron_size"])
    use_mc = bool(params.get("ismc", True))

    frames = _load_video(file_path)
    if max_frames is not None and max_frames > 0:
        frames = frames[:max_frames]
    frames = _normalize_01(frames)
    frames = _temporal_downsample(frames, fsi, fsi_new)
    frames = _spatial_downsample(frames, spatialr)

    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    enhanced = np.stack([gaussian_filter(frame, sigma=1.0) for frame in frames], axis=0).astype(np.float32)
    imaxy_pre = np.max(enhanced, axis=0).astype(np.float32)

    if use_mc:
        corrected, raw_score, corr_score = _movement_correct(enhanced)
    else:
        corrected = enhanced
        raw_score = np.zeros(corrected.shape[0], dtype=np.float32)
        corr_score = np.zeros(corrected.shape[0], dtype=np.float32)

    imax = np.max(corrected, axis=0).astype(np.float32)
    seedsfn = _detect_seeds(imax, max_count=int(params.get("max_seeds", 80))).astype(np.int64)
    roifn, sigfn = _build_roi_and_traces(corrected, seedsfn, sigma=max(neuron_size, 1.0))

    roi_max = np.max(roifn, axis=0, keepdims=True)
    roi_max_safe = np.where(roi_max > 0, roi_max, 1.0)
    roi_component = (roifn / roi_max_safe).astype(np.float32)
    sig_component = (roi_max.T * sigfn).astype(np.float32)

    spkfn = np.diff(sig_component, prepend=sig_component[:, :1], axis=1)
    spkfn = np.maximum(spkfn, 0.0).astype(np.float32)
    dff = _compute_dff(sig_component).astype(np.float32)

    bgfn = np.zeros((roi_component.shape[0],), dtype=np.float32)
    bgffn = np.zeros((1, sig_component.shape[1]), dtype=np.float32)

    return {
        "motion__frames_ds": frames.astype(np.float32),
        "motion__imaxn": imaxn,
        "motion__imeanf": imeanf,
        "motion__imaxy_pre": imaxy_pre,
        "motion__corrected_video": corrected.astype(np.float32),
        "motion__raw_score": raw_score.astype(np.float32),
        "motion__corr_score": corr_score.astype(np.float32),
        "motion__imax": imax,
        "source__roifn": roifn.astype(np.float32),
        "source__sigfn": sigfn.astype(np.float32),
        "source__seedsfn": seedsfn.astype(np.int64),
        "component__roifn": roi_component.astype(np.float32),
        "component__sigfn": sig_component.astype(np.float32),
        "component__seedsfn": seedsfn.astype(np.int64),
        "component__bgfn": bgfn,
        "component__bgffn": bgffn,
        "deconv__spkfn": spkfn.astype(np.float32),
        "deconv__dff": dff.astype(np.float32),
    }


def _save_capture(out_dir: Path, arrays: dict[str, np.ndarray]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    npz_path = out_dir / "capture.npz"
    np.savez_compressed(npz_path, **arrays)
    summary: dict[str, Any] = {}
    for key, arr in arrays.items():
        summary[key] = {
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "min": float(np.min(arr)) if arr.size else 0.0,
            "max": float(np.max(arr)) if arr.size else 0.0,
            "mean": float(np.mean(arr)) if arr.size else 0.0,
        }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return {"npz": str(npz_path), "summary": str(out_dir / "summary.json")}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--dataset-root",
        dest="dataset_roots",
        action="append",
        default=[],
        help="Dataset root. Can be passed multiple times.",
    )
    p.add_argument(
        "--out-root",
        type=Path,
        default=REPO / "artifacts" / "qa_monolith_vs_modular",
    )
    p.add_argument("--timestamp", type=str, default=None)
    p.add_argument("--max-frames", type=int, default=None)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    roots = [Path(r) for r in args.dataset_roots] if args.dataset_roots else [
        Path("/mnt/nas02/Dataset/ca_motion_corr/caiman/2p"),
        Path("/mnt/nas02/Dataset/ca_motion_corr/suite2p/demo"),
        Path("/mnt/nas02/Dataset/ca_motion_corr/fiola"),
    ]
    stamp = args.timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.out_root.expanduser().resolve() / stamp
    monolith_root = run_dir / "monolith"

    entries, skipped = _discover_files(roots)
    params = default_parameters()
    params["max_seeds"] = 80

    captures: list[dict[str, Any]] = []
    for entry in entries:
        in_path = Path(entry.file_path)
        file_out = monolith_root / entry.dataset_key / entry.file_key
        arrays = _capture_monolithic(in_path, params, max_frames=args.max_frames)
        loc = _save_capture(file_out, arrays)
        captures.append(
            {
                **asdict(entry),
                "capture_npz": loc["npz"],
                "capture_summary": loc["summary"],
                "max_frames": args.max_frames,
            }
        )
        print(f"[monolith] captured {in_path}")

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "runner": "run_monolithic_capture.py",
        "dataset_roots": [str(p.expanduser().resolve()) for p in roots],
        "supported_suffixes": sorted(SUPPORTED_SUFFIXES),
        "params": params,
        "max_frames": args.max_frames,
        "captures": captures,
        "skipped": skipped,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "manifest_monolith.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[monolith] manifest: {run_dir / 'manifest_monolith.json'}")


if __name__ == "__main__":
    main()
