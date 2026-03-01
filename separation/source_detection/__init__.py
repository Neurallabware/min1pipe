"""Strict standalone source detection module for calcium imaging.

Pipeline: over-complete seed init → coarse GMM/statistical cleansing →
seed merge → ROI/trace initialization.
"""

from .core import run_source_detection, SourceDetectionResult

__all__ = ["run_source_detection", "SourceDetectionResult"]
