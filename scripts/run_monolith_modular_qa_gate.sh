#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-.venv-min1pipe/bin/python}"
TS="${1:-$(date -u +%Y%m%dT%H%M%SZ)_full}"
MAX_FRAMES="${MAX_FRAMES:-}"
RUN_PICKLE="${RUN_PICKLE:-1}"
RUN_H5="${RUN_H5:-0}"

COMMON=(--timestamp "$TS")
if [[ -n "$MAX_FRAMES" ]]; then
  COMMON+=(--max-frames "$MAX_FRAMES")
fi

echo "[qa] run timestamp: $TS"
"$PYTHON_BIN" scripts/run_monolithic_capture.py "${COMMON[@]}"
"$PYTHON_BIN" scripts/run_modular_capture.py "${COMMON[@]}" --mode parity --serialization none
if [[ "$RUN_PICKLE" == "1" ]]; then
  "$PYTHON_BIN" scripts/run_modular_capture.py "${COMMON[@]}" --mode parity --serialization pickle
fi
if [[ "$RUN_H5" == "1" ]]; then
  "$PYTHON_BIN" scripts/run_modular_capture.py "${COMMON[@]}" --mode parity --serialization h5
fi
"$PYTHON_BIN" scripts/compare_monolith_modular.py --run-dir "artifacts/qa_monolith_vs_modular/$TS"

echo "[qa] complete: artifacts/qa_monolith_vs_modular/$TS"
