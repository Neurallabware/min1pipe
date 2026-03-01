"""Strict standalone component filtering module for calcium imaging.

Pipeline: merge_roi -> refine_roi -> bg_update -> refine_sig -> final_seeds_select
-> trace_clean.
"""

from .core import run_component_filtering, ComponentFilteringResult

__all__ = ["run_component_filtering", "ComponentFilteringResult"]
