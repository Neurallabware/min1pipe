# Monolithic vs Modular Discrepancy Report

- Run dir: `/home/yz/MIN1PIPE/artifacts/qa_monolith_vs_modular/20260301T104708Z_full`
- Tolerance: `rtol=0.0001`, `atol=1e-06`

## Variant Summary

| Variant | Files | Overall |
|---|---:|---|
| `parity_none` | 5 | PASS |
| `parity_pickle` | 5 | PASS |

## First Divergence by File

| Variant | Dataset | File | First Divergence | All Pass |
|---|---|---|---|---|
| `parity_none` | `/mnt/nas02/Dataset/ca_motion_corr/caiman/2p` | `demoMovie.tif` | `<none>` | PASS |
| `parity_none` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `Sue_2x_3000_40_-46.tif` | `<none>` | PASS |
| `parity_none` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `demoMovie.tif` | `<none>` | PASS |
| `parity_none` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `demo_voltage_imaging_init.tif` | `<none>` | PASS |
| `parity_none` | `/mnt/nas02/Dataset/ca_motion_corr/suite2p/demo` | `file_00002_00001.tif` | `<none>` | PASS |
| `parity_pickle` | `/mnt/nas02/Dataset/ca_motion_corr/caiman/2p` | `demoMovie.tif` | `<none>` | PASS |
| `parity_pickle` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `Sue_2x_3000_40_-46.tif` | `<none>` | PASS |
| `parity_pickle` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `demoMovie.tif` | `<none>` | PASS |
| `parity_pickle` | `/mnt/nas02/Dataset/ca_motion_corr/fiola` | `demo_voltage_imaging_init.tif` | `<none>` | PASS |
| `parity_pickle` | `/mnt/nas02/Dataset/ca_motion_corr/suite2p/demo` | `file_00002_00001.tif` | `<none>` | PASS |

## Boundary Metrics

| Variant | File | Field | Pass | Max Abs Err | Max Rel Err | Corr | SSIM |
|---|---|---|---|---:|---:|---:|---:|
| `parity_none` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `Sue_2x_3000_40_-46.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `demo_voltage_imaging_init.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `demo_voltage_imaging_init.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_none` | `file_00002_00001.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_none` | `file_00002_00001.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `Sue_2x_3000_40_-46.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `demo_voltage_imaging_init.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `motion__imax` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `source__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `source__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `component__roifn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `component__sigfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `component__bgfn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `component__bgffn` | PASS | 0 | 0 | 1 | n/a |
| `parity_pickle` | `file_00002_00001.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 | 1.000000 |
| `parity_pickle` | `file_00002_00001.tif` | `deconv__dff` | PASS | 0 | 0 | 1 | 1.000000 |

## Skipped Files

| File | Reason |
|---|---|
| `/mnt/nas02/Dataset/ca_motion_corr/fiola/demo_voltage_imaging.hdf5` | `unsupported_format:.hdf5` |
| `/mnt/nas02/Dataset/ca_motion_corr/fiola/demo_voltage_imaging_ROIs.hdf5` | `unsupported_format:.hdf5` |

## Serialization Probe (vs parity_none)

| Probe | File | Field | Pass | Max Abs Err | Max Rel Err | Corr |
|---|---|---|---|---:|---:|---:|
| `pickle` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `motion__imax` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `source__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `source__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `component__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `component__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `component__bgfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `component__bgffn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 |
| `pickle` | `Sue_2x_3000_40_-46.tif` | `deconv__dff` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `motion__imax` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__bgfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `component__bgffn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demoMovie.tif` | `deconv__dff` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `motion__imax` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `source__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `source__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `component__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `component__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `component__bgfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `component__bgffn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 |
| `pickle` | `demo_voltage_imaging_init.tif` | `deconv__dff` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__frames_ds` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__imaxn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__imeanf` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__imaxy_pre` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__corrected_video` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__raw_score` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__corr_score` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `motion__imax` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `source__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `source__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `source__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `component__roifn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `component__sigfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `component__seedsfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `component__bgfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `component__bgffn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `deconv__spkfn` | PASS | 0 | 0 | 1 |
| `pickle` | `file_00002_00001.tif` | `deconv__dff` | PASS | 0 | 0 | 1 |
