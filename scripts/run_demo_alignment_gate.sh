#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
MATLAB_DIR="${REPO_ROOT}/artifacts/golden/matlab/demo_data/${TS}"
PY_DIR="${REPO_ROOT}/artifacts/golden/python/demo_data/${TS}"
FORCE=0
SKIP_MATLAB=0

usage() {
  cat <<'EOF'
Usage: scripts/run_demo_alignment_gate.sh [--matlab-dir DIR] [--python-dir DIR] [--force] [--skip-matlab]

Runs:
1) MATLAB reference artifact generation
2) Python demo pipeline run
3) Numeric + visual comparison report
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --matlab-dir)
      MATLAB_DIR="$2"
      shift 2
      ;;
    --python-dir)
      PY_DIR="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --skip-matlab)
      SKIP_MATLAB=1
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

if [[ "$FORCE" -eq 1 ]]; then
  rm -rf "$MATLAB_DIR" "$PY_DIR"
fi

mkdir -p "$PY_DIR"
cp "${REPO_ROOT}/demo/demo_data.tif" "${PY_DIR}/demo_data.tif"

if [[ "$SKIP_MATLAB" -eq 1 ]]; then
  echo "[ALIGN] Skipping MATLAB generation and using existing artifacts from: $MATLAB_DIR"
else
  echo "[ALIGN] Generating MATLAB reference artifacts..."
  "${REPO_ROOT}/scripts/run_matlab_demo_reference.sh" --out-dir "$MATLAB_DIR" --force
fi

PYTHON_BIN="python3"
if [[ -x "${REPO_ROOT}/.venv-min1pipe/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv-min1pipe/bin/python"
fi

echo "[ALIGN] Running Python demo pipeline..."
PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}" \
MIN1PIPE_INPUT_FILE="${PY_DIR}/demo_data.tif" \
MIN1PIPE_DEMO_OUTPUT_DIR="${PY_DIR}" \
"$PYTHON_BIN" -m min1pipe.matlab_mirror.demo_min1pipe

ln -sfn "$(basename "$PY_DIR")" "$(dirname "$PY_DIR")/latest"

REPORT_MD="${REPO_ROOT}/artifacts/parity/runtime/demo_alignment_report.md"
REPORT_JSON="${REPO_ROOT}/artifacts/parity/runtime/demo_alignment_report.json"

echo "[ALIGN] Comparing MATLAB vs Python outputs..."
PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}" \
"$PYTHON_BIN" "${REPO_ROOT}/scripts/compare_demo_outputs.py" \
  --matlab-dir "$MATLAB_DIR" \
  --python-dir "$PY_DIR" \
  --report-md "$REPORT_MD" \
  --report-json "$REPORT_JSON"

echo "[ALIGN] Alignment gate passed."
echo "[ALIGN] MATLAB artifacts: $MATLAB_DIR"
echo "[ALIGN] Python artifacts: $PY_DIR"
echo "[ALIGN] Report: $REPORT_MD"
