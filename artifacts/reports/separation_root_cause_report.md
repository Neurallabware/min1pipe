# Separation Root-Cause Report (Monolith vs Modular QA)

- QA run: `artifacts/qa_monolith_vs_modular/20260301T104708Z_full`
- Ground truth: `src/min1pipe/matlab_mirror/min1pipe_HPC.py`
- Tolerance: `rtol=1e-4`, `atol=1e-6`
- Dataset scope: all supported files under:
  - `/mnt/nas02/Dataset/ca_motion_corr/caiman/2p`
  - `/mnt/nas02/Dataset/ca_motion_corr/suite2p/demo`
  - `/mnt/nas02/Dataset/ca_motion_corr/fiola`
- Unsupported files (skipped): `.hdf5` in `fiola` (reported in discrepancy report)

## Discrepancy Summary

| Variant | Files | Result |
|---|---:|---|
| `parity_none` | 5 | PASS |
| `parity_pickle` | 5 | PASS |

All required module boundaries now match monolith outputs exactly on tested files (`max_abs_err=0`, `max_rel_err=0` for compared fields).

## Root Causes and Fixes

| RC | First divergent boundary (pre-fix) | Code location | Expected (monolith) | Actual (pre-fix modular) | Fix |
|---|---|---|---|---|---|
| RC-01 | Motion preprocessing defaults | `separation/_shared/params.py:35` | Monolith defaults: `Fsi_new=10`, `spatialr=0.5` | Strict defaults were used globally: `Fsi_new=20`, `spatialr=1.0` | Added mode-specific defaults and made `parity` default via `default_parameters_for_mode(...)` (`separation/_shared/params.py:70`). |
| RC-02 | `motion__imaxy_pre` | `separation/motion_correction/core.py:134` and `separation/source_detection/core.py:224` | Gaussian enhancement path from monolith and monolith seed/ROI init | Strict neural enhancement + strict seed-cleansing path | Added parity execution branches in motion/source stages to mirror monolith order and algorithms (`# QA_FIX(RC-02)`). |
| RC-03 | `component__roifn`, `component__sigfn`, `component__bgfn` | `separation/component_filtering/core.py:284` | Monolith component pass: ROI normalization + signal rescale + zero background vectors | Strict refinement/background-update pipeline changed outputs | Added parity branch implementing monolith component post-processing (`# QA_FIX(RC-03)`). |
| RC-04 | `deconv__dff` and spike path | `separation/calcium_deconvolution/core.py:53` | Monolith deconv: `np.diff` spikes, dF/F baseline = per-trace minimum | Strict path used FOOPSI fallback + percentile baseline | Added parity deconvolution branch with monolith-equivalent equations (`# QA_FIX(RC-04)`). |
| RC-05 | Serialization probe robustness at boundaries | `scripts/run_modular_capture.py:76` and `scripts/run_modular_capture.py:159` | Boundary artifacts should preserve numeric arrays across serialization | HDF5 roundtrip failed on object/aux fields; missing explicit pre-motion boundary capture | Added boundary schema casting and object-field filtering for HDF5, plus explicit `motion__frames_ds` capture (`# QA_FIX(RC-05)`). |

## Evidence

1. Full discrepancy report: `artifacts/qa_monolith_vs_modular/20260301T104708Z_full/discrepancy_report.md`
2. Machine-readable metrics: `artifacts/qa_monolith_vs_modular/20260301T104708Z_full/discrepancy_report.json`
3. Per-file captures:
   - Monolith: `artifacts/qa_monolith_vs_modular/20260301T104708Z_full/monolith/.../capture.npz`
   - Modular: `artifacts/qa_monolith_vs_modular/20260301T104708Z_full/modular/parity_none/.../capture.npz`
   - Modular (serialization probe): `artifacts/qa_monolith_vs_modular/20260301T104708Z_full/modular/parity_pickle/.../capture.npz`

## Notes

- During full-run artifact generation, `parity_h5` capture exceeded available disk space. `parity_none` and `parity_pickle` completed and passed.
- HDF5 files in `fiola` remain explicitly skipped as unsupported input format for both pipelines.
