"""Standalone source detection module for calcium imaging.

Extracted from the MIN1PIPE pipeline. This module is fully self-contained.

Pipeline: corrected_video → detect seeds (local maxima) → build ROI footprints
         → extract temporal traces
"""

from .core import run_source_detection, SourceDetectionResult

__all__ = ["run_source_detection", "SourceDetectionResult"]
