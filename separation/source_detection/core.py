"""Source detection for MIN1PIPE separation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter, white_tophat
from scipy.signal import windows
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.stats import kstest, skew

try:
    from separation._shared.indexing import c0_to_f1, seed_rows_cols
    from separation._shared.math_utils import disk_footprint, intensity_filter
    from separation._shared.params import default_parameters_for_mode
except ModuleNotFoundError:  # support direct execution from separation/
    from _shared.indexing import c0_to_f1, seed_rows_cols
    from _shared.math_utils import disk_footprint, intensity_filter
    from _shared.params import default_parameters_for_mode

try:
    from sklearn.mixture import GaussianMixture
except Exception:  # pragma: no cover - optional dependency fallback
    GaussianMixture = None


@dataclass
class SourceDetectionResult:
    roifn: np.ndarray
    sigfn: np.ndarray
    seedsfn: np.ndarray
    n_components: int
    datasmth: np.ndarray
    cutoff: np.ndarray
    pkcutoff: np.ndarray
    seed_rows0: np.ndarray
    seed_cols0: np.ndarray
    seedsfn_f1: np.ndarray
    aux: dict[str, Any] | None = None


def _gaussian_smooth_traces(data: np.ndarray, fs: float) -> np.ndarray:
    win = max(3, int(round(fs)))
    g = windows.gaussian(win, std=max(1.0, win / 6.0))
    g = g / max(float(g.sum()), 1e-8)
    return np.stack([np.convolve(row, g, mode="valid") for row in data], axis=0)


def _cutoff_from_smoothed(datasmth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    st = np.sort(datasmth, axis=1)
    n = st.shape[1]
    ramp = np.linspace(0.0, 1.0, n, dtype=np.float64)[None, :]
    baseline = st[:, :1] + (st[:, -1:] - st[:, :1]) * ramp
    stcr = st - baseline
    minp = np.argmin(stcr, axis=1)
    maxp = np.argmax(stcr, axis=1)
    rows = np.arange(st.shape[0])
    minv = st[rows, minp]
    maxv = st[rows, maxp]
    cutoff = (minv + maxv) / 2.0
    pkcutoff = minv
    return cutoff.astype(np.float32), pkcutoff.astype(np.float32)


def _vld_period_select(trace: np.ndarray, cutoff: float, pkc: float, pxlthres: int = 100) -> np.ndarray:
    data = np.asarray(trace, dtype=np.float64).reshape(-1)
    nf = data.size
    if nf == 0:
        return np.zeros((0,), dtype=bool)
    idx = np.where(data > pkc)[0]
    use = np.zeros(nf, dtype=bool)
    if idx.size == 0:
        m = int(np.argmax(data))
        lo = max(0, m - pxlthres // 2)
        hi = min(nf, m + pxlthres // 2 + 1)
        use[lo:hi] = True
        return use
    for p in idx:
        lo = p
        while lo > 0 and data[lo - 1] <= data[lo]:
            lo -= 1
        hi = p
        while hi + 1 < nf and data[hi + 1] <= data[hi]:
            hi += 1
        use[lo : hi + 1] = True
    if use.sum() < pxlthres:
        top = np.argsort(data)[::-1][:pxlthres]
        use[top] = True
    return use


def _signal_similarity(datasmth: np.ndarray, cutoff: np.ndarray, pkcutoff: np.ndarray) -> np.ndarray:
    n = datasmth.shape[0]
    out = np.eye(n, dtype=np.float32)
    for i in range(n):
        mask = _vld_period_select(datasmth[i], float(cutoff[i]), float(pkcutoff[i]))
        if mask.sum() < 3:
            continue
        ref = datasmth[i, mask]
        ref = (ref - ref.mean()) / (ref.std() + 1e-8)
        others = datasmth[:, mask]
        others = (others - others.mean(axis=1, keepdims=True)) / (others.std(axis=1, keepdims=True) + 1e-8)
        corr = (others @ ref) / max(ref.size, 1)
        out[i, :] = corr.astype(np.float32)
    out = np.maximum(out, out.T)
    np.fill_diagonal(out, 1.0)
    return out


def _merge_seed_indices(
    seeds_c0: np.ndarray,
    datasmth: np.ndarray,
    cutoff: np.ndarray,
    pkcutoff: np.ndarray,
    pixh: int,
    pixw: int,
    neuron_size: int,
    corrthres: float,
) -> np.ndarray:
    if seeds_c0.size <= 1:
        return seeds_c0
    sigcor = _signal_similarity(datasmth, cutoff, pkcutoff)
    rows, cols = seed_rows_cols(seeds_c0, pixh, pixw)
    rr = rows[:, None] - rows[None, :]
    cc = cols[:, None] - cols[None, :]
    dist = np.sqrt(rr * rr + cc * cc)
    spatial = dist < (1.5 * float(neuron_size))
    con = (sigcor > float(corrthres)) & spatial
    np.fill_diagonal(con, False)
    graph = csr_matrix(con.astype(np.int8))
    n_comp, labels = connected_components(graph, directed=False, connection="weak")
    keep: list[int] = []
    for comp in range(n_comp):
        idx = np.where(labels == comp)[0]
        if idx.size == 1:
            keep.append(idx[0])
            continue
        score = np.median(datasmth[idx], axis=1)
        keep.append(int(idx[np.argmax(score)]))
    keep = np.unique(np.asarray(keep, dtype=np.int64))
    return np.sort(seeds_c0[keep])


def _roi_trace_init(
    corrected_video: np.ndarray,
    seeds_c0: np.ndarray,
    neuron_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    n_pixels = pixh * pixw
    flat = data.reshape(nf, -1).T
    rows, cols = seed_rows_cols(seeds_c0, pixh, pixw)

    rois = np.zeros((n_pixels, seeds_c0.size), dtype=np.float32)
    sig = np.zeros((seeds_c0.size, nf), dtype=np.float32)
    yy, xx = np.mgrid[0:pixh, 0:pixw]
    radius = int(max(2, 2 * neuron_size))
    sigma = float(max(1.0, neuron_size / 2.0))
    for i, (r, c, seed) in enumerate(zip(rows, cols, seeds_c0, strict=True)):
        lo_r = max(0, r - radius)
        hi_r = min(pixh, r + radius + 1)
        lo_c = max(0, c - radius)
        hi_c = min(pixw, c + radius + 1)
        patch = data[:, lo_r:hi_r, lo_c:hi_c].reshape(nf, -1).T
        ref = flat[int(seed)]
        refn = (ref - ref.mean()) / (ref.std() + 1e-8)
        pn = (patch - patch.mean(axis=1, keepdims=True)) / (patch.std(axis=1, keepdims=True) + 1e-8)
        corr = (pn @ refn) / max(refn.size, 1)
        corr_map = corr.reshape(hi_r - lo_r, hi_c - lo_c)
        corr_map = np.clip(corr_map, 0.0, None)

        g = np.exp(-((yy[lo_r:hi_r, lo_c:hi_c] - r) ** 2 + (xx[lo_r:hi_r, lo_c:hi_c] - c) ** 2) / (2.0 * sigma * sigma))
        roi_patch = np.maximum(corr_map, g).astype(np.float32)
        if np.max(roi_patch) <= 0:
            roi_patch = g.astype(np.float32)
        roi_patch /= max(float(np.max(roi_patch)), 1e-8)

        full = np.zeros((pixh, pixw), dtype=np.float32)
        full[lo_r:hi_r, lo_c:hi_c] = roi_patch
        rois[:, i] = full.ravel()
        w = rois[:, i] / max(float(np.sum(rois[:, i])), 1e-8)
        sig[i] = (w @ flat).astype(np.float32)
    return rois, sig


def _detect_seeds_parity(imax: np.ndarray, max_count: int = 80) -> np.ndarray:
    """Monolith-equivalent seed detection."""
    local_max = maximum_filter(imax, size=5) == imax
    threshold = np.percentile(imax, 97.0)
    mask = local_max & (imax >= threshold)
    ys, xs = np.where(mask)
    if ys.size == 0:
        y, x = np.unravel_index(int(np.argmax(imax)), imax.shape)
        ys = np.array([y], dtype=np.int64)
        xs = np.array([x], dtype=np.int64)
    strengths = imax[ys, xs]
    order = np.argsort(strengths)[::-1][: max(1, int(max_count))]
    ys = ys[order]
    xs = xs[order]
    return np.ravel_multi_index((ys, xs), imax.shape).astype(np.int64)


def _build_roi_and_traces_parity(data: np.ndarray, seeds: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    """Monolith-equivalent ROI/traces from Gaussian-weighted seeds."""
    nf, pixh, pixw = data.shape
    yy, xx = np.mgrid[0:pixh, 0:pixw]
    rois: list[np.ndarray] = []
    for seed in seeds:
        y, x = np.unravel_index(int(seed), (pixh, pixw))
        roi = np.exp(-((yy - y) ** 2 + (xx - x) ** 2) / (2 * sigma**2))
        roi = roi / max(float(np.max(roi)), 1e-8)
        rois.append(roi.reshape(-1))
    roifn = np.stack(rois, axis=1).astype(np.float32)
    movie_flat = data.reshape(nf, -1).T
    weights = roifn / np.maximum(np.sum(roifn, axis=0, keepdims=True), 1e-8)
    sigfn = (weights.T @ movie_flat).astype(np.float32)
    return roifn, sigfn


def _run_source_detection_parity(
    corrected_video: np.ndarray,
    imax: np.ndarray,
    cfg: dict,
) -> SourceDetectionResult:
    """Parity path: mirror monolith source extraction behavior."""
    # QA_FIX(RC-02): parity source path must use monolithic seed/ROI construction.
    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    max_seeds = int(max(1, cfg.get("max_seeds", 80)))
    seeds_c0 = _detect_seeds_parity(np.asarray(imax, dtype=np.float32), max_count=max_seeds)
    roifn, sigfn = _build_roi_and_traces_parity(data, seeds_c0, sigma=max(float(cfg["neuron_size"]), 1.0))
    rows, cols = seed_rows_cols(seeds_c0, pixh, pixw)
    seeds_f1 = c0_to_f1(seeds_c0, pixh, pixw)
    st = np.sort(sigfn, axis=1)
    cutoff = ((st[:, 0] + st[:, -1]) / 2.0).astype(np.float32)
    pkcutoff = st[:, 0].astype(np.float32)
    datasmth = sigfn.astype(np.float32).copy()
    return SourceDetectionResult(
        roifn=roifn.astype(np.float32),
        sigfn=sigfn.astype(np.float32),
        seedsfn=seeds_c0.astype(np.int64),
        n_components=int(seeds_c0.size),
        datasmth=datasmth,
        cutoff=cutoff,
        pkcutoff=pkcutoff,
        seed_rows0=rows,
        seed_cols0=cols,
        seedsfn_f1=seeds_f1,
        aux=None,
    )


def _run_source_detection_strict(
    corrected_video: np.ndarray,
    imax: np.ndarray,
    cfg: dict,
) -> SourceDetectionResult:
    """Strict seeds-cleansed source detection."""

    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    max_seeds = int(max(1, cfg.get("max_seeds", 80)))
    maxall = np.asarray(imax, dtype=np.float32)
    minall = np.min(data, axis=0)

    niter = int(max(1, cfg["seed_random_iters"]))
    nsel = int(min(max(1, nf // niter), cfg["seed_max_per_iter"]))
    local_stack: list[np.ndarray] = []
    for i in range(0, nf, nsel):
        chunk = data[i : i + nsel]
        maxt = np.max(chunk, axis=0)
        th = white_tophat(maxt, footprint=disk_footprint(4))
        mx = maximum_filter(gaussian_filter(th, sigma=0.5), size=3) == gaussian_filter(th, sigma=0.5)
        local_stack.append(mx)
    proj1 = np.any(np.stack(local_stack, axis=0), axis=0) | (maximum_filter(gaussian_filter(maxall, 1.0), size=5) == gaussian_filter(maxall, 1.0))
    mxs = np.flatnonzero(proj1.ravel())
    if mxs.size == 0:
        mxs = np.array([int(np.argmax(maxall))], dtype=np.int64)

    flat = data.reshape(nf, -1).T
    datause = flat[mxs]
    dtmx = np.percentile(datause, 99.9, axis=1)
    dtmn = np.percentile(datause, 0.1, axis=1)
    scmn = dtmx - dtmn
    if GaussianMixture is not None and scmn.size >= 2:
        gm = GaussianMixture(n_components=2, covariance_type="full", random_state=0)
        gm.fit(scmn.reshape(-1, 1))
        probs = gm.predict_proba(scmn.reshape(-1, 1))
        use_comp = int(np.argmax(gm.means_.ravel()))
        idx_gmm = probs[:, use_comp] > float(cfg["seed_gmm_prob_thres"])
    else:
        idx_gmm = scmn > np.percentile(scmn, 50.0)

    maxmin = maxall - minall
    mm = maxmin.ravel()[mxs]
    idx_int = scmn > intensity_filter(mm)
    keep = idx_gmm & idx_int
    iduse = mxs[keep]
    datuse = datause[keep]
    if iduse.size == 0:
        top = int(np.argmax(maxall))
        iduse = np.array([top], dtype=np.int64)
        datuse = flat[iduse]
    if iduse.size > max_seeds * 5:
        strength = maxall.ravel()[iduse]
        order = np.argsort(strength)[::-1][: max_seeds * 5]
        iduse = iduse[order]
        datuse = datuse[order]

    ithres = intensity_filter(maxall)
    maski = maxall.ravel()[iduse] > ithres
    iduse = iduse[maski]
    datuse = datuse[maski]
    if iduse.size == 0:
        iduse = np.array([int(np.argmax(maxall))], dtype=np.int64)
        datuse = flat[iduse]

    datasmth = _gaussian_smooth_traces(datuse, fs=float(cfg["Fsi_new"]))
    cutoff, pkcutoff = _cutoff_from_smoothed(datasmth)

    keep_stat = np.ones(iduse.size, dtype=bool)
    for i in range(iduse.size):
        z = (datuse[i] - datuse[i].mean()) / (datuse[i].std() + 1e-8)
        keep_stat[i] = kstest(z, "norm").pvalue < 0.05
    keep_sk = skew(datuse, axis=1, nan_policy="omit") > 0
    keep_all = keep_stat & keep_sk
    iduse = iduse[keep_all]
    datuse = datuse[keep_all]
    datasmth = datasmth[keep_all]
    cutoff = cutoff[keep_all]
    pkcutoff = pkcutoff[keep_all]
    if iduse.size == 0:
        iduse = np.array([int(np.argmax(maxall))], dtype=np.int64)
        datuse = flat[iduse]
        datasmth = _gaussian_smooth_traces(datuse, fs=float(cfg["Fsi_new"]))
        cutoff, pkcutoff = _cutoff_from_smoothed(datasmth)
    if iduse.size > max_seeds * 3:
        strength = np.max(datuse, axis=1)
        order = np.argsort(strength)[::-1][: max_seeds * 3]
        iduse = iduse[order]
        datuse = datuse[order]
        datasmth = datasmth[order]
        cutoff = cutoff[order]
        pkcutoff = pkcutoff[order]

    seeds_c0 = _merge_seed_indices(
        iduse.astype(np.int64),
        datasmth,
        cutoff,
        pkcutoff,
        pixh=pixh,
        pixw=pixw,
        neuron_size=int(cfg["neuron_size"]),
        corrthres=float(cfg["pix_select_corrthres"]),
    )
    if seeds_c0.size > max_seeds:
        strength = maxall.ravel()[seeds_c0]
        seeds_c0 = seeds_c0[np.argsort(strength)[::-1][:max_seeds]]
        seeds_c0 = np.sort(seeds_c0)
    # align intermediate vectors with merged order
    loc = {int(v): i for i, v in enumerate(iduse.astype(np.int64))}
    idx = np.array([loc[int(v)] for v in seeds_c0], dtype=np.int64)
    datasmth = datasmth[idx]
    cutoff = cutoff[idx]
    pkcutoff = pkcutoff[idx]

    roifn, sigfn = _roi_trace_init(data, seeds_c0, neuron_size=int(cfg["neuron_size"]))
    rows, cols = seed_rows_cols(seeds_c0, pixh, pixw)
    seeds_f1 = c0_to_f1(seeds_c0, pixh, pixw)
    return SourceDetectionResult(
        roifn=roifn.astype(np.float32),
        sigfn=sigfn.astype(np.float32),
        seedsfn=seeds_c0.astype(np.int64),
        n_components=int(seeds_c0.size),
        datasmth=datasmth.astype(np.float32),
        cutoff=cutoff.astype(np.float32),
        pkcutoff=pkcutoff.astype(np.float32),
        seed_rows0=rows,
        seed_cols0=cols,
        seedsfn_f1=seeds_f1,
        aux={
            "datasmth": datasmth.astype(np.float32),
            "cutoff": cutoff.astype(np.float32),
            "pkcutoff": pkcutoff.astype(np.float32),
        },
    )


def run_source_detection(
    corrected_video: np.ndarray,
    imax: np.ndarray,
    params: dict | None = None,
    mode: str = "parity",
) -> SourceDetectionResult:
    """Run source detection in `parity` (default) or `strict` mode."""
    cfg = default_parameters_for_mode(mode)
    if params:
        cfg.update(params)
    if str(mode).strip().lower() == "strict":
        return _run_source_detection_strict(corrected_video=corrected_video, imax=imax, cfg=cfg)
    return _run_source_detection_parity(corrected_video=corrected_video, imax=imax, cfg=cfg)
