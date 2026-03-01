#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MATLAB_BIN="${MIN1PIPE_MATLAB_BIN:-/home/yz/MATLAB/R2025b/bin/matlab}"
LICENSE_FILE="${MIN1PIPE_MATLAB_LICENSE:-/home/yz/matlab_installer/network.lic}"
LIBASOUND_DIR="${MIN1PIPE_MATLAB_LIBASOUND:-/home/yz/matlab_installer/deps/libasound2t64-root/usr/lib/x86_64-linux-gnu}"
CVX_ROOT="${MIN1PIPE_CVX_ROOT:-${REPO_ROOT}/artifacts/third_party/cvx}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${REPO_ROOT}/artifacts/golden/matlab/demo_data/${TS}"
FORCE=0

usage() {
  cat <<'EOF'
Usage: scripts/run_matlab_demo_reference.sh [--out-dir DIR] [--force]

Options:
  --out-dir DIR   Output directory for canonical MATLAB artifacts
  --force         Remove output directory first if it exists
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ ! -x "$MATLAB_BIN" ]]; then
  echo "MATLAB binary not found: $MATLAB_BIN" >&2
  exit 1
fi

if [[ -d "$OUT_DIR" && "$FORCE" -ne 1 ]]; then
  echo "Output directory already exists: $OUT_DIR (use --force to overwrite)" >&2
  exit 1
fi

if [[ "$FORCE" -eq 1 ]]; then
  rm -rf "$OUT_DIR"
fi
mkdir -p "$OUT_DIR"

OUT_DIR_ABS="$(cd "$OUT_DIR" && pwd)"
TOOLS_DIR="${REPO_ROOT}/tools/matlab"
MATLAB_FORCE="false"
if [[ "$FORCE" -eq 1 ]]; then
  MATLAB_FORCE="true"
fi

escape_matlab_str() {
  local s="$1"
  printf "%s" "${s//\'/\'\'}"
}

OUT_ESC="$(escape_matlab_str "$OUT_DIR_ABS")"
TOOLS_ESC="$(escape_matlab_str "$TOOLS_DIR")"

MATLAB_CMD="addpath('${TOOLS_ESC}'); run_min1pipe_demo_reference('${OUT_ESC}', ${MATLAB_FORCE});"

echo "[MATLAB-REF] Repo root: ${REPO_ROOT}"
echo "[MATLAB-REF] Output dir: ${OUT_DIR_ABS}"
echo "[MATLAB-REF] MATLAB bin: ${MATLAB_BIN}"
echo "[MATLAB-REF] License file present: $([[ -f "$LICENSE_FILE" ]] && echo yes || echo no)"
echo "[MATLAB-REF] CVX root: ${CVX_ROOT}"

if [[ ! -f "${CVX_ROOT}/commands/cvx_begin.m" ]]; then
  echo "[MATLAB-REF] CVX not found. Downloading CVX package..."
  mkdir -p "$(dirname "$CVX_ROOT")"
  tmp_zip="$(mktemp /tmp/cvx-a64.XXXXXX.zip)"
  curl -L "https://web.cvxr.com/cvx/cvx-a64.zip" -o "$tmp_zip"
  rm -rf "$CVX_ROOT"
  unzip -q "$tmp_zip" -d "$(dirname "$CVX_ROOT")"
  rm -f "$tmp_zip"
  # Expected unzip layout is .../cvx/*
  if [[ ! -f "${CVX_ROOT}/commands/cvx_begin.m" ]]; then
    echo "CVX download completed but cvx_begin.m not found in ${CVX_ROOT}" >&2
    exit 1
  fi
fi

export LD_LIBRARY_PATH="${LIBASOUND_DIR}:${LD_LIBRARY_PATH:-}"
export MIN1PIPE_CVX_ROOT="${CVX_ROOT}"
if [[ -f "$LICENSE_FILE" ]]; then
  "$MATLAB_BIN" -c "$LICENSE_FILE" -batch "$MATLAB_CMD"
else
  "$MATLAB_BIN" -batch "$MATLAB_CMD"
fi

python - "$OUT_DIR_ABS" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

out_dir = Path(sys.argv[1])
manifest_path = out_dir / "reference_manifest.json"
if not manifest_path.exists():
    raise SystemExit(f"Missing manifest: {manifest_path}")

manifest = json.loads(manifest_path.read_text())
hashes = {}
for name in (
    "demo_data_data_processed.mat",
    "demo_data_frame_all.mat",
    "demo_data_reg.mat",
    "demo_visualization_matlab.png",
):
    p = out_dir / name
    if not p.exists():
        raise SystemExit(f"Missing output: {p}")
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    hashes[name] = h.hexdigest()

manifest["sha256"] = hashes
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
print(f"[MATLAB-REF] Updated manifest hashes: {manifest_path}")
PY

PARENT_DIR="$(dirname "$OUT_DIR_ABS")"
if [[ "$(basename "$OUT_DIR_ABS")" != "latest" ]]; then
  ln -sfn "$(basename "$OUT_DIR_ABS")" "${PARENT_DIR}/latest"
  echo "[MATLAB-REF] Updated latest symlink: ${PARENT_DIR}/latest -> $(basename "$OUT_DIR_ABS")"
fi

echo "[MATLAB-REF] Completed: ${OUT_DIR_ABS}"
