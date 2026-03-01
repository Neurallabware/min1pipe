"""Standalone motion correction module for calcium imaging.

Extracted from the MIN1PIPE pipeline. This module is fully self-contained
and can be used independently.

Pipeline: raw video -> load -> normalize -> temporal downsample -> spatial downsample
         -> neural enhancement -> motion correction -> output
"""

from .core import run_motion_correction, MotionCorrectionResult

__all__ = ["run_motion_correction", "MotionCorrectionResult"]
