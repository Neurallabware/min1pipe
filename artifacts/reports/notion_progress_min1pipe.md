# MIN1PIPE Separation Redesign Progress (Paste to Notion)

Date: 2026-03-01  
Scope: `separation` strict redesign (demo dataset `demo/demo_data.tif`)

## Milestones Completed
1. Added strict shared infrastructure:
   - `separation/_shared/{params.py,math_utils.py,indexing.py,fixtures.py}`
2. Added new strict stage module:
   - `separation/neural_enhancement/{__init__.py,core.py}`
3. Refactored stage wrappers to strict internals:
   - `separation/motion_correction/core.py`
   - `separation/source_detection/core.py`
   - `separation/component_filtering/core.py`
   - `separation/calcium_deconvolution/core.py`
4. Added strict orchestrator and fixture builder:
   - `separation/pipeline_strict.py`
   - `separation/build_strict_fixtures.py`
5. Reworked tests for strict fixture contract:
   - standalone tests in each module directory
   - `separation/test_pipeline_integration.py` with deviation ledger
6. Rebuilt notebooks and redesigned full pipeline notebook:
   - updated generator `separation/_generate_notebooks.py`
   - regenerated `separation/nb05_full_pipeline.ipynb`
7. Added strict acceptance gate:
   - `scripts/run_separation_strict_gate.sh`
   - `scripts/compare_separation_strict.py`

## Module Status
| Module | Status | Notes |
|---|---|---|
| neural_enhancement | Implemented | Includes dead-pixel suppression, dirt clean, anisotropic diffusion, morphological opening background removal, post suppression |
| motion_correction | Implemented | Uses strict neural enhancement + phase-correlation registration |
| source_detection | Implemented | Over-complete seeds, GMM/statistical cleansing, seed merge, ROI/signal init |
| component_filtering | Implemented | `merge_roi`, `refine_roi`, `bg_update`, `refine_sig`, `final_seeds_select`, `trace_clean` implemented |
| calcium_deconvolution | Implemented | FOOPSI-style fallback path + `dff` |
| strict orchestrator | Implemented | Deterministic pipeline + artifact logging |
| notebook nb05 | Implemented | Executes top-to-bottom in strict mode |

## Test / Gate Results
- Strict gate command:
  - `./scripts/run_separation_strict_gate.sh --rebuild`
- Result: **PASS**
- Reports:
  - `artifacts/parity/runtime/separation_strict_report.md`
  - `artifacts/parity/runtime/separation_strict_report.json`
- Executed notebook artifact:
  - `separation/_test_data_strict/runtime_gate/nb05_full_pipeline.executed.ipynb`

### Strict Fixture Parity
All strict fixture fields pass (`imaxn`, `imaxy`, `imax`, `roifn`, `sigfn`, `seedsfn`, `bgfn`, `bgffn`, `raw_score`, `corr_score`, `spkfn`, `dff`).

### MATLAB Cross-Reference (Current)
- Still failing strict MATLAB parity for multiple fields.
- Major gaps remain in absolute alignment vs MATLAB artifact:
  - ROI count mismatch (Python: 15, MATLAB: 50)
  - score vector length mismatch (`1000` vs `999`)
  - projection value deviations (`imaxy`, `imax`)

## Remaining Work (Next Iteration)
1. Tighten neural enhancement and motion scoring to match MATLAB value ranges.
2. Improve seeds-cleansed extraction to match MATLAB component cardinality and shape selection.
3. Align score vector semantics (`raw_score`, `corr_score`) with MATLAB frame indexing.
4. Add per-step MATLAB parity fixtures for intermediate stages (not only final processed outputs).
5. Enable optional RNN gate with model loading path and report impact.

## Notion Sync Note
Direct Notion MCP write is currently blocked due auth (`Auth required`).  
This file is prepared for direct paste into:
`https://www.notion.so/neurolabware/min1pipe-304e31b2d0c380a0b5c7f31ce35b1554?source=copy_link`

