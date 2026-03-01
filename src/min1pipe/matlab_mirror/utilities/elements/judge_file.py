"""File overwrite policy helper."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def judge_file(filename: Any | None = None, msg: Any | None = None) -> bool:
    """Return whether a target file should be overwritten.

    Behavior mirrors MATLAB's ``judge_file.m`` with environment-aware defaults.

    Environment variable:
    - ``MIN1PIPE_OVERWRITE``: ``y``/``n``/``ask`` (default: ``ask``)
    """
    if filename is None:
        raise ValueError("filename is required")

    path = Path(str(filename))
    if not path.exists():
        return True

    policy = os.environ.get("MIN1PIPE_OVERWRITE", "ask").strip().lower()
    if policy in {"y", "yes", "1", "true"}:
        return True
    if policy in {"n", "no", "0", "false"}:
        return False

    if sys.stdin.isatty():
        prompt = str(msg) if msg else f"Overwrite {path}? (y/n) "
        try:
            return input(prompt).strip().lower() == "y"
        except EOFError:
            return False
    return False
