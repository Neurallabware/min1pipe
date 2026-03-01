"""Standalone component filtering module for calcium imaging.

Extracted from the MIN1PIPE pipeline. This module is fully self-contained.

Pipeline: ROIs + signals -> scale/normalize -> merge (future) -> filter -> output
"""

from .core import run_component_filtering, ComponentFilteringResult

__all__ = ["run_component_filtering", "ComponentFilteringResult"]
