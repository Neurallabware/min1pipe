"""Python demo mirror for ``demo_min1pipe.m`` with MATLAB-aligned rendering."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib import pyplot as plt

from min1pipe.io import load_processed_mat

from .min1pipe import min1pipe
from .utilities.elements.normalize import normalize
from .utilities.postprocess.plot_contour import plot_contour


def _load_processed_for_demo() -> tuple[dict[str, Any], Path, str]:
    ref_processed = os.environ.get("MIN1PIPE_REFERENCE_PROCESSED_MAT")
    if ref_processed:
        processed_path = Path(ref_processed).expanduser().resolve()
        layout = os.environ.get("MIN1PIPE_REFERENCE_LAYOUT", "matlab").strip().lower()
        if layout not in {"matlab", "python"}:
            raise ValueError("MIN1PIPE_REFERENCE_LAYOUT must be `matlab` or `python`")
        data = load_processed_mat(processed_path, source_layout=layout)  # type: ignore[arg-type]
        return data, processed_path, layout

    fname, frawname, fregname = min1pipe(20, 20, None, None, True, 1)
    processed_path = Path(fname).resolve()
    data = load_processed_mat(processed_path, source_layout="python")
    print(f"Processed file: {fname}")
    print(f"Raw file: {frawname}")
    print(f"Reg file: {fregname}")
    return data, processed_path, "python"


def _set_square_axes(ax: plt.Axes) -> None:
    # `axis square` equivalent for subplot panels.
    ax.set_box_aspect(1)


def render_demo_visualization(data: dict[str, Any], out_path: Path, title_suffix: str = "") -> Path:
    """Render MATLAB demo-style 2x3 panel visualization."""
    fig = plt.figure(figsize=(12.8, 9.0))

    imaxn = np.asarray(data["imaxn"])
    imaxy = np.asarray(data["imaxy"])
    imax = np.asarray(data["imax"])
    roifn = np.asarray(data["roifn"])
    sigfn = np.asarray(data["sigfn"])
    seeds = np.asarray(data["seeds_f1"])
    raw_score = np.asarray(data["raw_score"]).reshape(-1)
    corr_score = np.asarray(data["corr_score"]).reshape(-1)
    pixh = int(data["pixh"])
    pixw = int(data["pixw"])

    suffix = f" {title_suffix}" if title_suffix else ""

    ax1 = fig.add_subplot(2, 3, 1)
    ax1.imshow(imaxn, cmap="viridis", origin="upper", interpolation="nearest")
    ax1.set_title(f"Raw{suffix}")
    _set_square_axes(ax1)

    ax2 = fig.add_subplot(2, 3, 2)
    ax2.imshow(imaxy, cmap="viridis", origin="upper", interpolation="nearest")
    ax2.set_title(f"Before MC{suffix}")
    _set_square_axes(ax2)

    ax3 = fig.add_subplot(2, 3, 3)
    ax3.imshow(imax, cmap="viridis", origin="upper", interpolation="nearest")
    ax3.set_title(f"After MC{suffix}")
    _set_square_axes(ax3)

    ax4 = fig.add_subplot(2, 3, 4)
    plt.sca(ax4)
    plot_contour(roifn, sigfn, seeds, imax, pixh, pixw)
    _set_square_axes(ax4)

    ax5 = fig.add_subplot(2, 3, 5)
    has_mc = bool(np.any(np.abs(raw_score) > 0) or np.any(np.abs(corr_score) > 0))
    if has_mc:
        ax5.plot(raw_score, label="raw_score")
        ax5.plot(corr_score, label="corr_score")
        ax5.legend(loc="upper right", fontsize=8)
        ax5.set_title(f"MC Scores{suffix}")
    else:
        ax5.set_title(f"MC skipped{suffix}")
    _set_square_axes(ax5)

    ax6 = fig.add_subplot(2, 3, 6)
    sigt = np.asarray(sigfn, dtype=np.float64).copy()
    for i in range(sigt.shape[0]):
        sigt[i, :] = normalize(sigt[i, :])
    ax6.plot((sigt + np.arange(1, sigt.shape[0] + 1)[:, None]).T)
    ax6.axis("tight")
    ax6.set_title(f"Traces{suffix}")
    _set_square_axes(ax6)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main() -> None:
    data, processed_path, source_layout = _load_processed_for_demo()
    out_dir = os.environ.get("MIN1PIPE_DEMO_OUTPUT_DIR")
    if out_dir:
        out_root = Path(out_dir).expanduser().resolve()
    else:
        out_root = Path(__file__).resolve().parents[3] / "demo"
    out_png = out_root / "demo_visualization_python.png"
    out = render_demo_visualization(data=data, out_path=out_png, title_suffix="(demo_min1pipe.m)")
    print(f"Saved visualization: {out}")
    print(f"Processed source ({source_layout}): {processed_path}")


if __name__ == "__main__":
    main()
