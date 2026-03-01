"""Command-line interface for MIN1PIPE Python migration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .pipeline import min1pipe, min1pipe_hpc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MIN1PIPE pipeline entrypoints")
    parser.add_argument("--mode", choices=["standard", "hpc"], default="standard")
    parser.add_argument("--config", type=Path, help="Optional JSON config with function arguments")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    kwargs: dict[str, Any] = {}
    if args.config:
        kwargs = json.loads(args.config.read_text())

    if args.mode == "hpc":
        min1pipe_hpc(**kwargs)
    else:
        min1pipe(**kwargs)
