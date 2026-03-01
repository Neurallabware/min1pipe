#!/usr/bin/env python3
"""Run modular separation capture with boundary artifacts for QA parity."""

from __future__ import annotations

import argparse
import io
import json
import pickle
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import tifffile

REPO = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from separation.component_filtering import run_component_filtering  # noqa: E402
from separation.motion_correction import run_motion_correction  # noqa: E402
from separation.motion_correction.core import load_video, spatial_downsample, temporal_downsample  # noqa: E402
from separation.source_detection import run_source_detection  # noqa: E402
from separation.calcium_deconvolution import run_calcium_deconvolution  # noqa: E402
from separation._shared.math_utils import normalize_01  # noqa: E402
from separation._shared.params import default_parameters_for_mode  # noqa: E402

SUPPORTED_SUFFIXES = {".tif", ".tiff", ".avi", ".mat"}


def _slugify(path: Path) -> str:
    txt = str(path).strip().replace("\\", "/")
    out = [ch if ch.isalnum() else "_" for ch in txt]
    return "".join(out).strip("_")


def _discover_files(roots: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    entries: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            skipped.append({"file": str(root), "reason": "missing_root"})
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            suffix = path.suffix.lower()
            rel = path.relative_to(root)
            if suffix not in SUPPORTED_SUFFIXES:
                skipped.append({"file": str(path), "reason": f"unsupported_format:{suffix or '<none>'}"})
                continue
            entries.append(
                {
                    "dataset_root": str(root),
                    "file_path": str(path),
                    "file_rel": str(rel),
                    "dataset_key": _slugify(root),
                    "file_key": _slugify(rel.with_suffix(Path(rel).suffix)),
                    "size_bytes": path.stat().st_size,
                }
            )
    return entries, skipped


def _maybe_scalar(v: Any) -> Any:
    if isinstance(v, np.ndarray) and v.shape == ():
        return v.item()
    return v


def _roundtrip_dict(payload: dict[str, Any], serialization: str) -> dict[str, Any]:
    if serialization == "none":
        return payload
    if serialization == "pickle":
        blob = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
        return pickle.loads(blob)
    if serialization == "h5":
        buf = io.BytesIO()
        with h5py.File(buf, "w") as h5:
            for k, v in payload.items():
                arr = np.asarray(v)
                if arr.dtype.kind in {"O", "U", "S"}:
                    continue
                h5.create_dataset(k, data=arr)
        buf.seek(0)
        out: dict[str, Any] = {}
        with h5py.File(buf, "r") as h5:
            for k in h5.keys():
                out[k] = _maybe_scalar(np.asarray(h5[k]))
        return out
    raise ValueError(f"Unsupported serialization: {serialization}")


def _capture_modular(
    file_path: Path,
    params: dict[str, Any],
    mode: str,
    serialization: str,
    max_frames: int | None,
) -> dict[str, np.ndarray]:
    run_path = file_path
    tmp_dir: tempfile.TemporaryDirectory[str] | None = None
    if max_frames is not None and max_frames > 0:
        full = load_video(file_path)
        full = full[:max_frames]
        tmp_dir = tempfile.TemporaryDirectory(prefix="min1pipe_qa_", dir=str(REPO / "artifacts"))
        run_path = Path(tmp_dir.name) / f"{file_path.stem}_head{max_frames}.tif"
        tifffile.imwrite(run_path, full.astype(np.float32))

    # QA_FIX(RC-02): persist explicit pre-motion boundary, not post-motion frames.
    frames_ds = load_video(run_path)
    frames_ds = normalize_01(frames_ds)
    frames_ds = temporal_downsample(frames_ds, float(params["Fsi"]), float(params["Fsi_new"]))
    frames_ds = spatial_downsample(frames_ds, float(params["spatialr"]))

    mc = run_motion_correction(run_path, params=params, mode=mode)
    mc_payload = _roundtrip_dict(asdict(mc), serialization)

    sd = run_source_detection(
        corrected_video=np.asarray(mc_payload["corrected_video"], dtype=np.float32),
        imax=np.asarray(mc_payload["imax"], dtype=np.float32),
        params=params,
        mode=mode,
    )
    sd_payload = _roundtrip_dict(asdict(sd), serialization)

    aux = sd_payload.get("aux")
    if isinstance(aux, np.ndarray):
        aux = None

    cf = run_component_filtering(
        roifn=np.asarray(sd_payload["roifn"], dtype=np.float32),
        sigfn=np.asarray(sd_payload["sigfn"], dtype=np.float32),
        seedsfn=np.asarray(sd_payload["seedsfn"], dtype=np.int64),
        corrected_video=np.asarray(mc_payload["corrected_video"], dtype=np.float32),
        params=params,
        datasmth=np.asarray(sd_payload["datasmth"], dtype=np.float32),
        cutoff=np.asarray(sd_payload["cutoff"], dtype=np.float32),
        pkcutoff=np.asarray(sd_payload["pkcutoff"], dtype=np.float32),
        aux=aux,
        mode=mode,
    )
    cf_payload = _roundtrip_dict(asdict(cf), serialization)

    cd = run_calcium_deconvolution(
        sigfn=np.asarray(cf_payload["sigfn"], dtype=np.float32),
        params=params,
        mode=mode,
    )
    cd_payload = _roundtrip_dict(asdict(cd), serialization)
    if tmp_dir is not None:
        tmp_dir.cleanup()

    return {
        "motion__frames_ds": np.asarray(frames_ds, dtype=np.float32),
        # QA_FIX(RC-05): preserve explicit boundary dtype/shape contracts.
        "motion__imaxn": np.asarray(mc_payload["imaxn"], dtype=np.float32),
        "motion__imeanf": np.asarray(mc_payload["imeanf"], dtype=np.float32),
        "motion__imaxy_pre": np.asarray(mc_payload["imaxy_pre"], dtype=np.float32),
        "motion__corrected_video": np.asarray(mc_payload["corrected_video"], dtype=np.float32),
        "motion__raw_score": np.asarray(mc_payload["raw_score"], dtype=np.float32),
        "motion__corr_score": np.asarray(mc_payload["corr_score"], dtype=np.float32),
        "motion__imax": np.asarray(mc_payload["imax"], dtype=np.float32),
        "source__roifn": np.asarray(sd_payload["roifn"], dtype=np.float32),
        "source__sigfn": np.asarray(sd_payload["sigfn"], dtype=np.float32),
        "source__seedsfn": np.asarray(sd_payload["seedsfn"], dtype=np.int64),
        "component__roifn": np.asarray(cf_payload["roifn"], dtype=np.float32),
        "component__sigfn": np.asarray(cf_payload["sigfn"], dtype=np.float32),
        "component__seedsfn": np.asarray(cf_payload["seedsfn"], dtype=np.int64),
        "component__bgfn": np.asarray(cf_payload["bgfn"], dtype=np.float32),
        "component__bgffn": np.asarray(cf_payload["bgffn"], dtype=np.float32),
        "deconv__spkfn": np.asarray(cd_payload["spkfn"], dtype=np.float32),
        "deconv__dff": np.asarray(cd_payload["dff"], dtype=np.float32),
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
    p.add_argument("--dataset-root", dest="dataset_roots", action="append", default=[])
    p.add_argument("--out-root", type=Path, default=REPO / "artifacts" / "qa_monolith_vs_modular")
    p.add_argument("--timestamp", type=str, required=True)
    p.add_argument("--mode", type=str, default="parity", choices=["parity", "strict"])
    p.add_argument("--serialization", type=str, default="none", choices=["none", "pickle", "h5"])
    p.add_argument("--max-frames", type=int, default=None)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    roots = [Path(r) for r in args.dataset_roots] if args.dataset_roots else [
        Path("/mnt/nas02/Dataset/ca_motion_corr/caiman/2p"),
        Path("/mnt/nas02/Dataset/ca_motion_corr/suite2p/demo"),
        Path("/mnt/nas02/Dataset/ca_motion_corr/fiola"),
    ]

    run_dir = args.out_root.expanduser().resolve() / args.timestamp
    modular_root = run_dir / "modular" / f"{args.mode}_{args.serialization}"
    params = default_parameters_for_mode(args.mode)

    entries, skipped = _discover_files(roots)
    captures: list[dict[str, Any]] = []
    for entry in entries:
        in_path = Path(entry["file_path"])
        file_out = modular_root / entry["dataset_key"] / entry["file_key"]
        arrays = _capture_modular(
            file_path=in_path,
            params=params,
            mode=args.mode,
            serialization=args.serialization,
            max_frames=args.max_frames,
        )
        loc = _save_capture(file_out, arrays)
        captures.append(
            {
                **entry,
                "capture_npz": loc["npz"],
                "capture_summary": loc["summary"],
                "mode": args.mode,
                "serialization": args.serialization,
                "max_frames": args.max_frames,
            }
        )
        print(f"[modular:{args.mode}/{args.serialization}] captured {in_path}")

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "runner": "run_modular_capture.py",
        "dataset_roots": [str(p.expanduser().resolve()) for p in roots],
        "supported_suffixes": sorted(SUPPORTED_SUFFIXES),
        "mode": args.mode,
        "serialization": args.serialization,
        "max_frames": args.max_frames,
        "params": params,
        "captures": captures,
        "skipped": skipped,
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_name = f"manifest_modular_{args.mode}_{args.serialization}.json"
    (run_dir / manifest_name).write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[modular] manifest: {run_dir / manifest_name}")


if __name__ == "__main__":
    main()
