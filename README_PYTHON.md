# MIN1PIPE Python Migration (WIP)

This repository now contains a 1:1 Python mirror of the MATLAB codebase under:

- `src/min1pipe/matlab_mirror/`

## Quick Start

```bash
./scripts/bootstrap_venv.sh
source .venv-min1pipe/bin/activate
MIN1PIPE_INPUT_FILE=demo/demo_data.tif min1pipe --mode standard
```

## MATLAB Alignment Workflow (Demo Dataset)

Generate canonical MATLAB reference artifacts:

```bash
./scripts/run_matlab_demo_reference.sh --out-dir artifacts/golden/matlab/demo_data/latest --force
```

Run end-to-end alignment gate (MATLAB reference + Python run + numeric/visual compare):

```bash
./scripts/run_demo_alignment_gate.sh --force
```

Outputs:

- MATLAB artifacts: `artifacts/golden/matlab/demo_data/<timestamp>/`
- Python artifacts: `artifacts/golden/python/demo_data/<timestamp>/`
- Alignment report: `artifacts/parity/runtime/demo_alignment_report.md`

## Key Deliverables

- MATLAB inventory + call graph: `artifacts/analysis/`
- MATLAB-to-Python mapping: `artifacts/analysis/matlab_to_python_mapping.csv`
- Parity harness + logs: `tests/parity/`, `artifacts/parity/`
- Conversion reports: `artifacts/reports/`
- Visualization notebook: `notebooks/min1pipe_visualizations.ipynb`

## Current Status

- 1:1 module mapping generated for all MATLAB files.
- Foundational utility modules are implemented and tested.
- Full algorithmic parity for all modules is in progress.
- Demo alignment tooling is available via MATLAB reference generation and dual-gate comparison scripts.
