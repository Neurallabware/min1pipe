"""Component filtering stage for MIN1PIPE separation pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter, label, median_filter
from scipy.signal import windows
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from scipy.stats import kstest, skew

try:
    from separation._shared.indexing import seed_rows_cols
    from separation._shared.math_utils import intensity_filter
    from separation._shared.params import default_parameters_for_mode
except ModuleNotFoundError:  # support direct execution from separation/
    from _shared.indexing import seed_rows_cols
    from _shared.math_utils import intensity_filter
    from _shared.params import default_parameters_for_mode


@dataclass
class ComponentFilteringResult:
    roifn: np.ndarray
    sigfn: np.ndarray
    seedsfn: np.ndarray
    bgfn: np.ndarray
    bgffn: np.ndarray
    datasmth: np.ndarray
    cutoff: np.ndarray
    pkcutoff: np.ndarray


def _smooth_traces(sig: np.ndarray, fs: float) -> np.ndarray:
    win = max(3, int(round(fs)))
    g = windows.gaussian(win, std=max(1.0, win / 6.0))
    g = g / max(float(g.sum()), 1e-8)
    return np.stack([np.convolve(row, g, mode="valid") for row in sig], axis=0)


def _signal_similarity(datasmth: np.ndarray) -> np.ndarray:
    if datasmth.shape[0] <= 1:
        return np.ones((datasmth.shape[0], datasmth.shape[0]), dtype=np.float32)
    corr = np.corrcoef(datasmth)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    corr = np.maximum(corr, corr.T)
    np.fill_diagonal(corr, 1.0)
    return corr.astype(np.float32)


def merge_roi(
    corrected_video: np.ndarray,
    roi: np.ndarray,
    sig: np.ndarray,
    seed: np.ndarray,
    imax: np.ndarray,
    datasmthf: np.ndarray,
    cutofff: np.ndarray,
    pkcutofff: np.ndarray,
    ethres: float = 0.9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Merge highly correlated and overlapping ROIs."""
    _ = corrected_video, imax
    nseed = int(seed.size)
    if nseed <= 1:
        return roi, sig, seed, datasmthf, cutofff, pkcutofff

    roi_bin = (roi > 0.2 * np.max(roi, axis=0, keepdims=True)).astype(np.float32)
    denom = (np.sum(roi_bin, axis=0, keepdims=True) + 1e-8)
    overlap = (roi_bin.T @ roi_bin) / ((denom.T + denom) / 2.0)
    roicon = overlap > 0.5
    np.fill_diagonal(roicon, False)

    sigcor = _signal_similarity(datasmthf) > float(ethres)
    con = roicon & sigcor

    graph = csr_matrix(con.astype(np.int8))
    n_comp, labels = connected_components(graph, directed=False, connection="weak")
    keep: list[int] = []
    for comp in range(n_comp):
        idx = np.where(labels == comp)[0]
        if idx.size == 1:
            keep.append(int(idx[0]))
            continue
        score = np.median(datasmthf[idx], axis=1)
        keep.append(int(idx[np.argmax(score)]))
    keep = np.unique(np.asarray(keep, dtype=np.int64))
    return (
        roi[:, keep],
        sig[keep],
        seed[keep],
        datasmthf[keep],
        cutofff[keep],
        pkcutofff[keep],
    )


def refine_roi(
    corrected_video: np.ndarray,
    C: np.ndarray,
    f: np.ndarray,
    Aold: np.ndarray,
    iduse: np.ndarray,
    noise: np.ndarray | None,
    datasmthf: np.ndarray,
    cutofff: np.ndarray,
    pkcutofff: np.ndarray,
    ispara: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Spatial ROI refinement with seed-centered connected component constraint."""
    _ = C, f, noise, ispara
    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    roi = np.asarray(Aold, dtype=np.float32).copy()
    rows, cols = seed_rows_cols(iduse, pixh, pixw)
    for i in range(roi.shape[1]):
        m = roi[:, i].reshape(pixh, pixw)
        m = median_filter(m, size=3, mode="nearest")
        thr = 0.2 * float(np.max(m))
        if thr <= 0:
            continue
        bw = m > thr
        comp, n = label(bw)
        if n > 0:
            rid = int(rows[i])
            cid = int(cols[i])
            cid_lbl = int(comp[rid, cid])
            if cid_lbl == 0:
                sizes = np.bincount(comp.ravel())
                sizes[0] = 0
                cid_lbl = int(np.argmax(sizes))
            m = m * (comp == cid_lbl)
        m = gaussian_filter(m, sigma=1.5)
        roi[:, i] = m.ravel()

    keep = (np.sum(roi, axis=0) > 0) & (np.sum(C if C.size else np.ones((roi.shape[1], 1)), axis=1) > 0)
    if keep.size:
        roi = roi[:, keep]
        iduse = iduse[keep]
        datasmthf = datasmthf[keep]
        cutofff = cutofff[keep]
        pkcutofff = pkcutofff[keep]
    return roi, C[: roi.shape[1]] if C.size else C, iduse, datasmthf, cutofff, pkcutofff


def bg_update(corrected_video: np.ndarray, roi: np.ndarray, sig: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Background update from residuals (MATLAB-inspired)."""
    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    Y = data.reshape(nf, -1).T  # (d, T)
    tmpp = roi @ sig
    mn = Y.mean(axis=1) - tmpp.mean(axis=1)
    mask = mn > 0
    if not np.any(mask):
        bf = np.maximum(np.mean(Y - tmpp, axis=0), 0.0).astype(np.float32)
    else:
        bf = np.maximum(np.mean((Y - tmpp)[mask], axis=0), 0.0).astype(np.float32)
    denom = float(np.dot(bf, bf))
    if denom <= 1e-12:
        return np.zeros((pixh * pixw,), dtype=np.float32), bf[None, :].astype(np.float32)
    Yf = Y @ bf
    tmppf = tmpp @ bf
    b = np.maximum((Yf - tmppf) / denom, 0.0).astype(np.float32)
    return b, bf[None, :]


def refine_sig(
    corrected_video: np.ndarray,
    roifn: np.ndarray,
    bgfn: np.ndarray,
    sigfn: np.ndarray,
    bgffn: np.ndarray,
    seedsfn: np.ndarray,
    datasmth: np.ndarray,
    cutoff: np.ndarray,
    pkcutoff: np.ndarray,
    p: int = 2,
    options: dict | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Temporal refinement with non-negative residual updates."""
    _ = p, options
    data = np.asarray(corrected_video, dtype=np.float32)
    nf, pixh, pixw = data.shape
    Y = data.reshape(nf, -1).T
    A = np.concatenate([roifn, bgfn.reshape(-1, 1)], axis=1).astype(np.float32)
    C = np.concatenate([sigfn, bgffn], axis=0).astype(np.float32)
    denom = np.maximum(np.sum(A, axis=0, keepdims=True), 1e-8)
    for _ in range(2):
        recon = A @ C
        resid = Y - recon
        YrA = (resid.T @ A / denom).T
        C = np.maximum(C + YrA, 0.0)
    sig_new = C[:-1]
    bgf_new = C[-1:, :]
    keep = (np.sum(roifn, axis=0) > 0) & (np.sum(sig_new, axis=1) > 0)
    roifn = roifn[:, keep]
    sig_new = sig_new[keep]
    seedsfn = seedsfn[keep]
    datasmth = datasmth[keep]
    cutoff = cutoff[keep]
    pkcutoff = pkcutoff[keep]
    return sig_new, bgf_new, roifn, seedsfn, datasmth, cutoff, pkcutoff


def final_seeds_select(
    corrected_video: np.ndarray,
    roifn: np.ndarray,
    sigfn: np.ndarray,
    seedsfn: np.ndarray,
    datasmth: np.ndarray,
    cutoff: np.ndarray,
    pkcutoff: np.ndarray,
    sz: int,
    maxall: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Final seed filtering from temporal + intensity constraints."""
    _ = corrected_video, sz
    n = int(seedsfn.size)
    if n == 0:
        return roifn, sigfn, seedsfn, datasmth, cutoff, pkcutoff
    id1 = np.zeros((n,), dtype=bool)
    for i in range(n):
        tr = sigfn[i]
        z = (tr - tr.mean()) / (tr.std() + 1e-8)
        id1[i] = kstest(z, "norm").pvalue < 0.05
    id2 = skew(sigfn, axis=1, nan_policy="omit") > 0
    ith = intensity_filter(maxall) * 0.5
    id3 = maxall.ravel()[seedsfn.astype(np.int64)] > ith
    keep = id1 & id2 & id3
    if not np.any(keep):
        keep[np.argmax(np.max(sigfn, axis=1))] = True
    return roifn[:, keep], sigfn[keep], seedsfn[keep], datasmth[keep], cutoff[keep], pkcutoff[keep]


def _find_valleys(trace: np.ndarray, tflag: int) -> np.ndarray:
    from scipy.signal import find_peaks

    tmpt = np.asarray(trace, dtype=np.float64)
    pks, props = find_peaks(-tmpt)
    if pks.size == 0:
        return np.full_like(tmpt, fill_value=float(np.median(tmpt)))
    vals = -tmpt[pks]
    mn = float(np.median(tmpt))
    if int(tflag) == 1:
        keep = vals >= -mn - 2.0 * float(np.std(tmpt))
    else:
        keep = vals >= -mn
    p = pks[keep]
    if p.size == 0:
        p = np.array([int(np.argmin(tmpt))])
    x = np.concatenate(([0], p, [tmpt.size - 1]))
    y = tmpt[x]
    return np.interp(np.arange(tmpt.size), x, y)


def trace_clean(sigfn: np.ndarray, fs: float, tflag: int) -> np.ndarray:
    """Trace denoise/baseline correction from MATLAB `trace_clean` logic."""
    data = np.asarray(sigfn, dtype=np.float32).copy()
    n1, n2 = data.shape
    out = np.empty_like(data)
    for i in range(n1):
        tr = data[i].astype(np.float64)
        q = max(1, int(round(fs / 4.0)))
        tr[:q] = np.linspace(np.percentile(tr, 1), tr[q - 1], q)
        try:
            import pywt

            coeffs = pywt.wavedec(tr, "sym8", level=4)
            sigma = np.median(np.abs(coeffs[-1])) / 0.6745 + 1e-8
            uth = sigma * np.sqrt(2 * np.log(tr.size))
            coeffs = [coeffs[0]] + [pywt.threshold(c, uth, mode="soft") for c in coeffs[1:]]
            sm = pywt.waverec(coeffs, "sym8")[: tr.size]
        except Exception:
            sm = gaussian_filter(tr, sigma=max(1.0, fs / 8.0))
        valleys = _find_valleys(sm, tflag=tflag)
        tmp = tr - valleys
        offset = np.median(tr) - np.median(tmp)
        out[i] = np.maximum(tmp + offset, 0.0).astype(np.float32)
    return out


def run_component_filtering(
    roifn: np.ndarray,
    sigfn: np.ndarray,
    seedsfn: np.ndarray,
    corrected_video: np.ndarray,
    params: dict | None = None,
    datasmth: np.ndarray | None = None,
    cutoff: np.ndarray | None = None,
    pkcutoff: np.ndarray | None = None,
    aux: dict | None = None,
    mode: str = "parity",
) -> ComponentFilteringResult:
    """Run component filtering in `parity` (default) or `strict` mode."""
    _ = aux
    cfg = default_parameters_for_mode(mode)
    if params:
        cfg.update(params)

    data = np.asarray(corrected_video, dtype=np.float32)
    roifn = np.asarray(roifn, dtype=np.float32)
    sigfn = np.asarray(sigfn, dtype=np.float32)
    seedsfn = np.asarray(seedsfn, dtype=np.int64).reshape(-1)

    if str(mode).strip().lower() != "strict":
        # QA_FIX(RC-03): parity mode mirrors monolith component post-processing.
        roi_max = np.max(roifn, axis=0, keepdims=True) if roifn.size else np.zeros((1, 0), dtype=np.float32)
        roi_max_safe = np.where(roi_max > 0, roi_max, 1.0)
        sig_out = (roi_max.T * sigfn).astype(np.float32) if sigfn.size else sigfn.astype(np.float32)
        roi_out = (roifn / roi_max_safe).astype(np.float32) if roifn.size else roifn.astype(np.float32)
        n_pixels = int(data.shape[1] * data.shape[2])
        bgfn = np.zeros((n_pixels,), dtype=np.float32)
        bgffn = np.zeros((1, sig_out.shape[1] if sig_out.ndim == 2 else data.shape[0]), dtype=np.float32)
        if datasmth is None:
            datasmth = sig_out.copy()
        if cutoff is None or pkcutoff is None:
            st = np.sort(datasmth, axis=1) if datasmth.size else np.zeros((0, 1), dtype=np.float32)
            cutoff = ((st[:, 0] + st[:, -1]) / 2.0).astype(np.float32) if st.size else np.zeros((0,), dtype=np.float32)
            pkcutoff = st[:, 0].astype(np.float32) if st.size else np.zeros((0,), dtype=np.float32)
        return ComponentFilteringResult(
            roifn=roi_out.astype(np.float32),
            sigfn=sig_out.astype(np.float32),
            seedsfn=seedsfn.astype(np.int64),
            bgfn=bgfn,
            bgffn=bgffn,
            datasmth=np.asarray(datasmth, dtype=np.float32),
            cutoff=np.asarray(cutoff, dtype=np.float32),
            pkcutoff=np.asarray(pkcutoff, dtype=np.float32),
        )

    imaxy = np.max(data, axis=0)

    if datasmth is None:
        datasmth = _smooth_traces(sigfn, fs=float(cfg["Fsi_new"]))
    if cutoff is None or pkcutoff is None:
        st = np.sort(datasmth, axis=1)
        cutoff = ((st[:, 0] + st[:, -1]) / 2.0).astype(np.float32)
        pkcutoff = st[:, 0].astype(np.float32)

    roimrg, sigmrg, seedsmrg, datasmth2, cutoff2, pkcutoff2 = merge_roi(
        data,
        roifn,
        sigfn,
        seedsfn,
        imaxy,
        datasmth,
        cutoff,
        pkcutoff,
        ethres=float(cfg["merge_roi_corrthres"]),
    )

    roifn1, sigfn1, seedsfn1, datasmth3, cutoff3, pkcutoff3 = refine_roi(
        data,
        sigmrg,
        np.zeros((1, sigmrg.shape[1]), dtype=np.float32),
        roimrg,
        seedsmrg,
        noise=None,
        datasmthf=datasmth2,
        cutofff=cutoff2,
        pkcutofff=pkcutoff2,
        ispara=bool(cfg["refine_roi_ispara"]),
    )
    bgfn, bgffn = bg_update(data, roifn1, sigfn1)

    sigfn2, bgffn2, roifn2, seedsfn2, datasmth4, cutoff4, pkcutoff4 = refine_sig(
        data,
        roifn1,
        bgfn,
        sigfn1,
        bgffn,
        seedsfn1,
        datasmth3,
        cutoff3,
        pkcutoff3,
        p=2,
        options=None,
    )

    roifn3, sigfn3, seedsfn3, datasmth5, cutoff5, pkcutoff5 = final_seeds_select(
        data,
        roifn2,
        sigfn2,
        seedsfn2,
        datasmth4,
        cutoff4,
        pkcutoff4,
        sz=int(cfg["neuron_size"]),
        maxall=imaxy,
    )
    sigfn3 = trace_clean(sigfn3, fs=float(cfg["Fsi_new"]), tflag=int(cfg["trace_clean_tflag"]))

    roi_max = np.max(roifn3, axis=0, keepdims=True)
    roi_max_safe = np.where(roi_max > 0, roi_max, 1.0)
    sig_out = (roi_max.T * sigfn3).astype(np.float32)
    roi_out = (roifn3 / roi_max_safe).astype(np.float32)

    bgfn2, bgffn3 = bg_update(data, roi_out, sig_out)
    return ComponentFilteringResult(
        roifn=roi_out,
        sigfn=sig_out,
        seedsfn=seedsfn3.astype(np.int64),
        bgfn=bgfn2.astype(np.float32),
        bgffn=bgffn3.astype(np.float32),
        datasmth=datasmth5.astype(np.float32),
        cutoff=cutoff5.astype(np.float32),
        pkcutoff=pkcutoff5.astype(np.float32),
    )
