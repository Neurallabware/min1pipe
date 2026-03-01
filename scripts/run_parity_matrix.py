#!/usr/bin/env python3
"""Run the module parity matrix and report artifact locations."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]



def main() -> None:
    cmd = ["pytest", "tests/parity/test_parity_matrix.py", "-q"]
    proc = subprocess.run(cmd, cwd=REPO_ROOT)
    runtime = REPO_ROOT / "artifacts" / "parity" / "runtime"
    print(f"Parity JSON: {runtime / 'parity_results.json'}")
    print(f"Parity Markdown: {runtime / 'parity_results.md'}")
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
