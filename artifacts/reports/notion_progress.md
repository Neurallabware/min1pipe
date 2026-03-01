# MIN1PIPE Migration Progress

## Milestones

- [x] Phase 1: Inventory, call graph, toolbox-gap matrix, and 1:1 mapping artifacts generated.
- [x] Phase 2 (initial): 1:1 Python mirror generated for all MATLAB files.
- [x] Phase 2 (foundation): Core shared utilities implemented and unit-tested.
- [x] Phase 2 (parity infra): Dual-mode parity harness scaffold implemented.
- [x] Phase 3: Installable package + dedicated venv bootstrap scaffold created.
- [x] Phase 4 (initial): Visualization notebook scaffold and demo plot path created.
- [ ] Full algorithmic parity across all 146 modules.

## Current Metrics

- Modules mapped: **146/146**
- Parity-ready modules: **6/146**
- Parity pass count: **6**
- Pending parity modules: **140**

## Module Table

| Module | Python Path | Status | Parity | Max Dev |
|---|---|---|---|---|
| `demo_min1pipe.m` | `src/min1pipe/matlab_mirror/demo_min1pipe.py` | pending | skip |  |
| `demo_min1pipe_HPC.m` | `src/min1pipe/matlab_mirror/demo_min1pipe_HPC.py` | pending | skip |  |
| `min1pipe.m` | `src/min1pipe/matlab_mirror/min1pipe.py` | pending | skip |  |
| `min1pipe_HPC.m` | `src/min1pipe/matlab_mirror/min1pipe_HPC.py` | pending | skip |  |
| `min1pipe_old.m` | `src/min1pipe/matlab_mirror/min1pipe_old.py` | pending | skip |  |
| `utilities/CNMF/CNMFSetParms.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/CNMFSetParms.py` | pending | skip |  |
| `utilities/CNMF/constrained_foopsi.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/constrained_foopsi.py` | pending | skip |  |
| `utilities/CNMF/cvx_foopsi.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/cvx_foopsi.py` | pending | skip |  |
| `utilities/CNMF/find_unsaturatedPixels.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/find_unsaturatedPixels.py` | pending | skip |  |
| `utilities/CNMF/get_noise_fft.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/get_noise_fft.py` | pending | skip |  |
| `utilities/CNMF/init_roi.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/init_roi.py` | pending | skip |  |
| `utilities/CNMF/kmeans_pp.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/kmeans_pp.py` | pending | skip |  |
| `utilities/CNMF/lars_regression_noise.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/lars_regression_noise.py` | pending | skip |  |
| `utilities/CNMF/preprocess_data.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/preprocess_data.py` | pending | skip |  |
| `utilities/CNMF/update_order.m` | `src/min1pipe/matlab_mirror/utilities/CNMF/update_order.py` | pending | skip |  |
| `utilities/RNN/batch_init.m` | `src/min1pipe/matlab_mirror/utilities/RNN/batch_init.py` | pending | skip |  |
| `utilities/RNN/bprop.m` | `src/min1pipe/matlab_mirror/utilities/RNN/bprop.py` | pending | skip |  |
| `utilities/RNN/check_grad.m` | `src/min1pipe/matlab_mirror/utilities/RNN/check_grad.py` | pending | skip |  |
| `utilities/RNN/cross_entropy_loss.m` | `src/min1pipe/matlab_mirror/utilities/RNN/cross_entropy_loss.py` | pending | skip |  |
| `utilities/RNN/dSigmf.m` | `src/min1pipe/matlab_mirror/utilities/RNN/dSigmf.py` | pending | skip |  |
| `utilities/RNN/dTanh.m` | `src/min1pipe/matlab_mirror/utilities/RNN/dTanh.py` | pending | skip |  |
| `utilities/RNN/dTanhSum.m` | `src/min1pipe/matlab_mirror/utilities/RNN/dTanhSum.py` | pending | skip |  |
| `utilities/RNN/fprop.m` | `src/min1pipe/matlab_mirror/utilities/RNN/fprop.py` | pending | skip |  |
| `utilities/RNN/initMatrix.m` | `src/min1pipe/matlab_mirror/utilities/RNN/initMatrix.py` | pending | skip |  |
| `utilities/RNN/label_predict.m` | `src/min1pipe/matlab_mirror/utilities/RNN/label_predict.py` | pending | skip |  |
| `utilities/RNN/lstm_init.m` | `src/min1pipe/matlab_mirror/utilities/RNN/lstm_init.py` | pending | skip |  |
| `utilities/RNN/lstm_predict_unit.m` | `src/min1pipe/matlab_mirror/utilities/RNN/lstm_predict_unit.py` | pending | skip |  |
| `utilities/RNN/lstm_train.m` | `src/min1pipe/matlab_mirror/utilities/RNN/lstm_train.py` | pending | skip |  |
| `utilities/RNN/lstm_val.m` | `src/min1pipe/matlab_mirror/utilities/RNN/lstm_val.py` | pending | skip |  |
| `utilities/RNN/optimizer_init.m` | `src/min1pipe/matlab_mirror/utilities/RNN/optimizer_init.py` | pending | skip |  |
| `utilities/RNN/rnn_lstm_ca_detector_train.m` | `src/min1pipe/matlab_mirror/utilities/RNN/rnn_lstm_ca_detector_train.py` | pending | skip |  |
| `utilities/RNN/seeds_cleansing_rnn.m` | `src/min1pipe/matlab_mirror/utilities/RNN/seeds_cleansing_rnn.py` | pending | skip |  |
| `utilities/RNN/sgd_adam.m` | `src/min1pipe/matlab_mirror/utilities/RNN/sgd_adam.py` | pending | skip |  |
| `utilities/RNN/sgd_rmsprop.m` | `src/min1pipe/matlab_mirror/utilities/RNN/sgd_rmsprop.py` | pending | skip |  |
| `utilities/RNN/softm.m` | `src/min1pipe/matlab_mirror/utilities/RNN/softm.py` | pending | skip |  |
| `utilities/RNN/zeroMatrix.m` | `src/min1pipe/matlab_mirror/utilities/RNN/zeroMatrix.py` | pending | skip |  |
| `utilities/elements/anidenoise.m` | `src/min1pipe/matlab_mirror/utilities/elements/anidenoise.py` | pending | skip |  |
| `utilities/elements/anisodiff_unit.m` | `src/min1pipe/matlab_mirror/utilities/elements/anisodiff_unit.py` | pending | skip |  |
| `utilities/elements/auto_detect_params.m` | `src/min1pipe/matlab_mirror/utilities/elements/auto_detect_params.py` | pending | skip |  |
| `utilities/elements/batch_compute.m` | `src/min1pipe/matlab_mirror/utilities/elements/batch_compute.py` | ready | pass | 0.0 |
| `utilities/elements/bg_extract.m` | `src/min1pipe/matlab_mirror/utilities/elements/bg_extract.py` | pending | skip |  |
| `utilities/elements/bg_remove.m` | `src/min1pipe/matlab_mirror/utilities/elements/bg_remove.py` | pending | skip |  |
| `utilities/elements/bg_update.m` | `src/min1pipe/matlab_mirror/utilities/elements/bg_update.py` | pending | skip |  |
| `utilities/elements/binaryImageGraph.m` | `src/min1pipe/matlab_mirror/utilities/elements/binaryImageGraph.py` | pending | skip |  |
| `utilities/elements/binaryImageGraph3.m` | `src/min1pipe/matlab_mirror/utilities/elements/binaryImageGraph3.py` | pending | skip |  |
| `utilities/elements/checkConnectivity.m` | `src/min1pipe/matlab_mirror/utilities/elements/checkConnectivity.py` | pending | skip |  |
| `utilities/elements/compute_dff.m` | `src/min1pipe/matlab_mirror/utilities/elements/compute_dff.py` | pending | skip |  |
| `utilities/elements/data_cat.m` | `src/min1pipe/matlab_mirror/utilities/elements/data_cat.py` | pending | skip |  |
| `utilities/elements/data_info.m` | `src/min1pipe/matlab_mirror/utilities/elements/data_info.py` | pending | skip |  |
| `utilities/elements/data_info_HPC.m` | `src/min1pipe/matlab_mirror/utilities/elements/data_info_HPC.py` | pending | skip |  |
| `utilities/elements/default_parameters.m` | `src/min1pipe/matlab_mirror/utilities/elements/default_parameters.py` | ready | pass | 0.0 |
| `utilities/elements/dirt_clean.m` | `src/min1pipe/matlab_mirror/utilities/elements/dirt_clean.py` | pending | skip |  |
| `utilities/elements/downsamp.m` | `src/min1pipe/matlab_mirror/utilities/elements/downsamp.py` | pending | skip |  |
| `utilities/elements/downsamp_unit.m` | `src/min1pipe/matlab_mirror/utilities/elements/downsamp_unit.py` | pending | skip |  |
| `utilities/elements/final_seeds_select.m` | `src/min1pipe/matlab_mirror/utilities/elements/final_seeds_select.py` | pending | skip |  |
| `utilities/elements/frame_reg.m` | `src/min1pipe/matlab_mirror/utilities/elements/frame_reg.py` | pending | skip |  |
| `utilities/elements/frame_sample.m` | `src/min1pipe/matlab_mirror/utilities/elements/frame_sample.py` | pending | skip |  |
| `utilities/elements/graph_cost.m` | `src/min1pipe/matlab_mirror/utilities/elements/graph_cost.py` | pending | skip |  |
| `utilities/elements/imageGraph.m` | `src/min1pipe/matlab_mirror/utilities/elements/imageGraph.py` | pending | skip |  |
| `utilities/elements/intensity_filter.m` | `src/min1pipe/matlab_mirror/utilities/elements/intensity_filter.py` | pending | skip |  |
| `utilities/elements/iter_seeds_select.m` | `src/min1pipe/matlab_mirror/utilities/elements/iter_seeds_select.py` | pending | skip |  |
| `utilities/elements/judge_file.m` | `src/min1pipe/matlab_mirror/utilities/elements/judge_file.py` | pending | skip |  |
| `utilities/elements/manual_seeds_select.m` | `src/min1pipe/matlab_mirror/utilities/elements/manual_seeds_select.py` | pending | skip |  |
| `utilities/elements/merge_roi.m` | `src/min1pipe/matlab_mirror/utilities/elements/merge_roi.py` | pending | skip |  |
| `utilities/elements/merge_unit.m` | `src/min1pipe/matlab_mirror/utilities/elements/merge_unit.py` | pending | skip |  |
| `utilities/elements/neural_enhance.m` | `src/min1pipe/matlab_mirror/utilities/elements/neural_enhance.py` | pending | skip |  |
| `utilities/elements/noise_suppress.m` | `src/min1pipe/matlab_mirror/utilities/elements/noise_suppress.py` | pending | skip |  |
| `utilities/elements/norm_inner.m` | `src/min1pipe/matlab_mirror/utilities/elements/norm_inner.py` | ready | pass | 0.0 |
| `utilities/elements/normalize.m` | `src/min1pipe/matlab_mirror/utilities/elements/normalize.py` | ready | pass | 0.0 |
| `utilities/elements/normalize_batch.m` | `src/min1pipe/matlab_mirror/utilities/elements/normalize_batch.py` | pending | skip |  |
| `utilities/elements/par_init.m` | `src/min1pipe/matlab_mirror/utilities/elements/par_init.py` | pending | skip |  |
| `utilities/elements/parse_type.m` | `src/min1pipe/matlab_mirror/utilities/elements/parse_type.py` | ready | pass | 0.0 |
| `utilities/elements/pix_select.m` | `src/min1pipe/matlab_mirror/utilities/elements/pix_select.py` | pending | skip |  |
| `utilities/elements/pure_refine_sig.m` | `src/min1pipe/matlab_mirror/utilities/elements/pure_refine_sig.py` | pending | skip |  |
| `utilities/elements/rdp.m` | `src/min1pipe/matlab_mirror/utilities/elements/rdp.py` | pending | skip |  |
| `utilities/elements/refine_roi.m` | `src/min1pipe/matlab_mirror/utilities/elements/refine_roi.py` | pending | skip |  |
| `utilities/elements/refine_sig.m` | `src/min1pipe/matlab_mirror/utilities/elements/refine_sig.py` | pending | skip |  |
| `utilities/elements/refine_sig_old.m` | `src/min1pipe/matlab_mirror/utilities/elements/refine_sig_old.py` | pending | skip |  |
| `utilities/elements/remove_dp.m` | `src/min1pipe/matlab_mirror/utilities/elements/remove_dp.py` | pending | skip |  |
| `utilities/elements/requireR2015b.m` | `src/min1pipe/matlab_mirror/utilities/elements/requireR2015b.py` | pending | skip |  |
| `utilities/elements/roi_domain.m` | `src/min1pipe/matlab_mirror/utilities/elements/roi_domain.py` | pending | skip |  |
| `utilities/elements/roi_gauss.m` | `src/min1pipe/matlab_mirror/utilities/elements/roi_gauss.py` | pending | skip |  |
| `utilities/elements/savef.m` | `src/min1pipe/matlab_mirror/utilities/elements/savef.py` | pending | skip |  |
| `utilities/elements/seeds_merge.m` | `src/min1pipe/matlab_mirror/utilities/elements/seeds_merge.py` | pending | skip |  |
| `utilities/elements/seeds_merge_unit.m` | `src/min1pipe/matlab_mirror/utilities/elements/seeds_merge_unit.py` | pending | skip |  |
| `utilities/elements/sig_sim.m` | `src/min1pipe/matlab_mirror/utilities/elements/sig_sim.py` | pending | skip |  |
| `utilities/elements/sigmoid.m` | `src/min1pipe/matlab_mirror/utilities/elements/sigmoid.py` | ready | pass | 0.0 |
| `utilities/elements/trace_clean.m` | `src/min1pipe/matlab_mirror/utilities/elements/trace_clean.py` | pending | skip |  |
| `utilities/elements/vld_prd_slct.m` | `src/min1pipe/matlab_mirror/utilities/elements/vld_prd_slct.py` | pending | skip |  |
| `utilities/movement_correction/BCH.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/BCH.py` | pending | skip |  |
| `utilities/movement_correction/TSP.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/TSP.py` | pending | skip |  |
| `utilities/movement_correction/cen_gen.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/cen_gen.py` | pending | skip |  |
| `utilities/movement_correction/demons_prep.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/demons_prep.py` | pending | skip |  |
| `utilities/movement_correction/dftregistration.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/dftregistration.py` | pending | skip |  |
| `utilities/movement_correction/dominant_patch.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/dominant_patch.py` | pending | skip |  |
| `utilities/movement_correction/feature1_comp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/feature1_comp.py` | pending | skip |  |
| `utilities/movement_correction/feature2_comp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/feature2_comp.py` | pending | skip |  |
| `utilities/movement_correction/feature_select.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/feature_select.py` | pending | skip |  |
| `utilities/movement_correction/find_frame.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/find_frame.py` | pending | skip |  |
| `utilities/movement_correction/frame_stab.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/frame_stab.py` | pending | skip |  |
| `utilities/movement_correction/get_node_name.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/get_node_name.py` | pending | skip |  |
| `utilities/movement_correction/get_trans_score.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/get_trans_score.py` | pending | skip |  |
| `utilities/movement_correction/get_trans_score_ref.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/get_trans_score_ref.py` | pending | skip |  |
| `utilities/movement_correction/gmm_bg.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/gmm_bg.py` | pending | skip |  |
| `utilities/movement_correction/gradient_fast.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/gradient_fast.py` | pending | skip |  |
| `utilities/movement_correction/hier_clust.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/hier_clust.py` | pending | skip |  |
| `utilities/movement_correction/hist_gauss.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/hist_gauss.py` | pending | skip |  |
| `utilities/movement_correction/iminterpolate.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/iminterpolate.py` | pending | skip |  |
| `utilities/movement_correction/imregdft.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/imregdft.py` | pending | skip |  |
| `utilities/movement_correction/inter_section.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/inter_section.py` | pending | skip |  |
| `utilities/movement_correction/intra_section.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/intra_section.py` | pending | skip |  |
| `utilities/movement_correction/jacobian_matrix2d.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/jacobian_matrix2d.py` | pending | skip |  |
| `utilities/movement_correction/klt2.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt2.py` | pending | skip |  |
| `utilities/movement_correction/klt2_reg.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt2_reg.py` | pending | skip |  |
| `utilities/movement_correction/klt_geo.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt_geo.py` | pending | skip |  |
| `utilities/movement_correction/klt_ref_track.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt_ref_track.py` | pending | skip |  |
| `utilities/movement_correction/klt_track.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt_track.py` | pending | skip |  |
| `utilities/movement_correction/klt_warp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/klt_warp.py` | pending | skip |  |
| `utilities/movement_correction/lie_bracket.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lie_bracket.py` | pending | skip |  |
| `utilities/movement_correction/lk2_track.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk2_track.py` | pending | skip |  |
| `utilities/movement_correction/lk2_warp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk2_warp.py` | pending | skip |  |
| `utilities/movement_correction/lk_cluster.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_cluster.py` | pending | skip |  |
| `utilities/movement_correction/lk_combine_layers.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_combine_layers.py` | pending | skip |  |
| `utilities/movement_correction/lk_ld_hier.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_ld_hier.py` | pending | skip |  |
| `utilities/movement_correction/lk_logdemons_unit.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_logdemons_unit.py` | pending | skip |  |
| `utilities/movement_correction/lk_loop.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_loop.py` | pending | skip |  |
| `utilities/movement_correction/lk_ref_track.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_ref_track.py` | pending | skip |  |
| `utilities/movement_correction/lk_warp_layers.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/lk_warp_layers.py` | pending | skip |  |
| `utilities/movement_correction/logdemons.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_cluster.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_cluster.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_combine_layers.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_combine_layers.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_loop.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_loop.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_unit.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_unit.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_warp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_warp.py` | pending | skip |  |
| `utilities/movement_correction/logdemons_warp_layers.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/logdemons_warp_layers.py` | pending | skip |  |
| `utilities/movement_correction/movement_thres.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/movement_thres.py` | pending | skip |  |
| `utilities/movement_correction/nonstable_range.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/nonstable_range.py` | pending | skip |  |
| `utilities/movement_correction/nonstable_section.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/nonstable_section.py` | pending | skip |  |
| `utilities/movement_correction/ref_select.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/ref_select.py` | pending | skip |  |
| `utilities/movement_correction/section_update.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/section_update.py` | pending | skip |  |
| `utilities/movement_correction/select_gpu.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/select_gpu.py` | pending | skip |  |
| `utilities/movement_correction/temporary_warp.m` | `src/min1pipe/matlab_mirror/utilities/movement_correction/temporary_warp.py` | pending | skip |  |
| `utilities/postprocess/mouseClick.m` | `src/min1pipe/matlab_mirror/utilities/postprocess/mouseClick.py` | pending | skip |  |
| `utilities/postprocess/mouseMove.m` | `src/min1pipe/matlab_mirror/utilities/postprocess/mouseMove.py` | pending | skip |  |
| `utilities/postprocess/plot_contour.m` | `src/min1pipe/matlab_mirror/utilities/postprocess/plot_contour.py` | pending | skip |  |
| `utilities/postprocess/real_neuron_select.m` | `src/min1pipe/matlab_mirror/utilities/postprocess/real_neuron_select.py` | pending | skip |  |
