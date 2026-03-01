"""Python demo mirror for ``demo_min1pipe_HPC.m``."""

from __future__ import annotations

from pathlib import Path

from .demo_min1pipe import main as _run_standard_demo



def main() -> None:
    # The fallback implementation for standard and HPC demos is identical in Python.
    demo_path = Path(__file__).resolve().parents[3] / "demo" / "demo_data.tif"
    if not demo_path.exists():
        raise FileNotFoundError(demo_path)
    _run_standard_demo()


if __name__ == "__main__":
    main()
