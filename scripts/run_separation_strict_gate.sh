#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT_ROOT="${REPO_ROOT}/separation/_test_data_strict"
RUNTIME_DIR="${STRICT_ROOT}/runtime_gate"
REPORT_MD="${REPO_ROOT}/artifacts/parity/runtime/separation_strict_report.md"
REPORT_JSON="${REPO_ROOT}/artifacts/parity/runtime/separation_strict_report.json"
MATLAB_PROCESSED="${REPO_ROOT}/artifacts/golden/matlab/demo_data/latest/demo_data_data_processed.mat"
REBUILD=0

usage() {
  cat <<'EOF'
Usage: scripts/run_separation_strict_gate.sh [--rebuild]

Runs:
1) strict fixture build (if needed)
2) strict integration test
3) full notebook execution (nb05_full_pipeline.ipynb)
4) strict report generation
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --rebuild)
      REBUILD=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

PYTHON_BIN="python3"
if [[ -x "${REPO_ROOT}/.venv-min1pipe/bin/python" ]]; then
  PYTHON_BIN="${REPO_ROOT}/.venv-min1pipe/bin/python"
fi
JUPYTER_BIN="jupyter"
if [[ -x "${REPO_ROOT}/.venv-min1pipe/bin/jupyter" ]]; then
  JUPYTER_BIN="${REPO_ROOT}/.venv-min1pipe/bin/jupyter"
fi

if [[ "$REBUILD" -eq 1 || ! -f "${STRICT_ROOT}/manifest.json" ]]; then
  echo "[strict-gate] Building strict fixtures..."
  PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/src:${PYTHONPATH:-}" \
    "$PYTHON_BIN" "${REPO_ROOT}/separation/build_strict_fixtures.py"
fi

echo "[strict-gate] Running strict integration test..."
PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/src:${PYTHONPATH:-}" \
  "$PYTHON_BIN" "${REPO_ROOT}/separation/test_pipeline_integration.py"

echo "[strict-gate] Running strict runtime pipeline..."
PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/src:${PYTHONPATH:-}" \
REPO_ROOT="${REPO_ROOT}" "$PYTHON_BIN" - <<'PY'
import os
from pathlib import Path
from separation.pipeline_strict import run_full_pipeline_strict
from separation._shared.params import strict_default_parameters
from separation._shared.fixtures import save_npz

repo = Path(os.environ["REPO_ROOT"]).resolve()
video = repo / "demo" / "demo_data.tif"
out = repo / "separation" / "_test_data_strict" / "runtime_gate"
res = run_full_pipeline_strict(video, strict_default_parameters(), artifact_dir=out)
save_npz(
    out / "runtime_outputs.npz",
    {
        "imaxn": res.motion.imaxn,
        "imaxy": res.motion.imaxy,
        "imax": res.motion.imax,
        "roifn": res.component.roifn,
        "sigfn": res.component.sigfn,
        "seedsfn": res.component.seedsfn,
        "bgfn": res.component.bgfn,
        "bgffn": res.component.bgffn,
        "raw_score": res.motion.raw_score,
        "corr_score": res.motion.corr_score,
        "spkfn": res.deconv.spkfn,
        "dff": res.deconv.dff,
    },
)
PY

echo "[strict-gate] Executing notebook..."
"${JUPYTER_BIN}" nbconvert --to notebook --execute "${REPO_ROOT}/separation/nb05_full_pipeline.ipynb" \
  --output "${RUNTIME_DIR}/nb05_full_pipeline.executed.ipynb" \
  --ExecutePreprocessor.timeout=1800

echo "[strict-gate] Building strict report..."
PYTHONPATH="${REPO_ROOT}:${REPO_ROOT}/src:${PYTHONPATH:-}" \
  "$PYTHON_BIN" "${REPO_ROOT}/scripts/compare_separation_strict.py" \
    --strict-root "${STRICT_ROOT}" \
    --runtime-npz "${RUNTIME_DIR}/runtime_outputs.npz" \
    --report-md "${REPORT_MD}" \
    --report-json "${REPORT_JSON}" \
    --matlab-processed "${MATLAB_PROCESSED}"

echo "[strict-gate] PASS"
echo "  report: ${REPORT_MD}"
