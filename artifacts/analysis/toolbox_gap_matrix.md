# Toolbox Gap Matrix

## Image Processing Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/CNMF/CNMFSetParms.m` | `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/auto_detect_params.m` | `bwlabeln`, `imgaussfilt`, `imopen`, `imregionalmax`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/bg_remove.m` | `imopen`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/dirt_clean.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/frame_reg.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/manual_seeds_select.m` | `bwlabeln` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/neural_enhance.m` | `imtophat`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/pix_select.m` | `bwconvhull`, `bwlabeln`, `imgaussfilt`, `imregionalmax`, `imtophat`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/refine_roi.m` | `bwlabeln`, `imclose`, `imgaussfilt`, `improfile`, `imregionalmax`, `medfilt2`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/remove_dp.m` | `bwlabeln` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/roi_domain.m` | `bwlabeln`, `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/roi_gauss.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/seeds_merge.m` | `improfile` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/seeds_merge_unit.m` | `imgaussfilt`, `imtophat`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/elements/trace_clean.m` | `medfilt2` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/cen_gen.m` | `bwlabeln`, `imgaussfilt`, `regionprops` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/dominant_patch.m` | `bwlabeln`, `imgaussfilt`, `medfilt2`, `regionprops` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/feature2_comp.m` | `imerode`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/feature_select.m` | `imregionalmax` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/hier_clust.m` | `bwlabeln`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/inter_section.m` | `imopen`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/klt_warp.m` | `imref2d`, `imwarp` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/lk2_warp.m` | `imref2d`, `imwarp` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/lk_logdemons_unit.m` | `imgaussfilt`, `imopen`, `strel` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/logdemons.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/movement_correction/ref_select.m` | `imregionalmax` | `scikit-image` + `scipy.ndimage` |
| `utilities/postprocess/mouseClick.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/postprocess/mouseMove.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/postprocess/plot_contour.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |
| `utilities/postprocess/real_neuron_select.m` | `imgaussfilt` | `scikit-image` + `scipy.ndimage` |

## Signal Processing Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/CNMF/constrained_foopsi.m` | `pwelch`, `xcov` | `scipy.signal` |
| `utilities/elements/manual_seeds_select.m` | `gausswin` | `scipy.signal` |
| `utilities/elements/pix_select.m` | `gausswin` | `scipy.signal` |
| `utilities/elements/trace_clean.m` | `findpeaks`, `gausswin` | `scipy.signal` |
| `utilities/elements/vld_prd_slct.m` | `findpeaks` | `scipy.signal` |

## Statistics and ML Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/elements/final_seeds_select.m` | `kstest`, `skewness` | `scikit-learn` + `scipy.stats` |
| `utilities/elements/pix_select.m` | `fitgmdist`, `kstest`, `posterior`, `skewness` | `scikit-learn` + `scipy.stats` |
| `utilities/movement_correction/gmm_bg.m` | `fitgmdist`, `posterior` | `scikit-learn` + `scipy.stats` |

## Parallel Computing Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/CNMF/CNMFSetParms.m` | `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/initMatrix.m` | `gpuArray` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/lstm_predict_unit.m` | `gather` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/lstm_train.m` | `gather` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/rnn_lstm_ca_detector_train.m` | `gpuArray`, `gpuDevice` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/seeds_cleansing_rnn.m` | `gather`, `gpuArray`, `gpuDevice` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/RNN/zeroMatrix.m` | `gpuArray` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/anidenoise.m` | `feature(`, `gcp`, `parfor`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/bg_remove.m` | `feature(`, `gcp`, `parfor`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/dirt_clean.m` | `feature(`, `gcp`, `parfor`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/downsamp_unit.m` | `feature(`, `gcp`, `parfor`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/final_seeds_select.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/frame_reg.m` | `feature(`, `gcp`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/neural_enhance.m` | `feature(`, `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/pix_select.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/pure_refine_sig.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/refine_roi.m` | `feature(`, `gcp`, `parfor`, `parpool` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/refine_sig.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/refine_sig_old.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/seeds_merge_unit.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/elements/trace_clean.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/feature1_comp.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/feature2_comp.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/get_trans_score.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/get_trans_score_ref.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/inter_section.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/intra_section.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/klt_ref_track.m` | `gather` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/klt_track.m` | `gather`, `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/lk_cluster.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/lk_loop.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/logdemons.m` | `gather`, `gpuArray` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/logdemons_cluster.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/logdemons_loop.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/logdemons_unit.m` | `gather`, `gpuArray`, `gpuDevice` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/logdemons_warp_layers.m` | `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/nonstable_section.m` | `feature(`, `parfor` | `joblib`/`concurrent.futures`; optional `cupy` |
| `utilities/movement_correction/select_gpu.m` | `gpuDevice` | `joblib`/`concurrent.futures`; optional `cupy` |

## Optimization Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/CNMF/constrained_foopsi.m` | `fmincon`, `quadprog` | `scipy.optimize` / `osqp` |

## Computer Vision Toolbox

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/movement_correction/klt2.m` | `detectMinEigenFeatures`, `vision.PointTracker` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/klt2_reg.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/klt_geo.m` | `estimateGeometricTransform` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/klt_ref_track.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/klt_track.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/lk2_track.m` | `vision.PointTracker` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/lk2_warp.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/lk_cluster.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/lk_ld_hier.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/lk_loop.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/logdemons_cluster.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/logdemons_loop.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |
| `utilities/movement_correction/temporary_warp.m` | `affine2d` | `opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`) |

## Graph APIs

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/elements/binaryImageGraph3.m` | `graph(` | `networkx` |
| `utilities/elements/merge_unit.m` | `conncomp`, `graph(` | `networkx` |
| `utilities/elements/seeds_merge_unit.m` | `conncomp`, `digraph(`, `graph(`, `rmnode` | `networkx` |
| `utilities/movement_correction/lk_cluster.m` | `conncomp`, `graph(`, `rmnode` | `networkx` |
| `utilities/movement_correction/lk_loop.m` | `conncomp`, `digraph(`, `graph(`, `rmnode` | `networkx` |
| `utilities/movement_correction/logdemons_cluster.m` | `conncomp`, `digraph(`, `graph(`, `rmnode` | `networkx` |
| `utilities/movement_correction/logdemons_loop.m` | `conncomp`, `digraph(`, `graph(`, `rmnode` | `networkx` |

## CVX

| File | MATLAB APIs | Proposed Python Workaround |
|---|---|---|
| `utilities/CNMF/constrained_foopsi.m` | `cvx_begin` | `cvxpy` + `scipy.optimize` fallback |
| `utilities/CNMF/cvx_foopsi.m` | `cvx_begin`, `cvx_end` | `cvxpy` + `scipy.optimize` fallback |
| `utilities/CNMF/lars_regression_noise.m` | `cvx_begin`, `cvx_end` | `cvxpy` + `scipy.optimize` fallback |

