"""Standalone calcium deconvolution module for calcium imaging.

Extracted from the MIN1PIPE pipeline. This module is fully self-contained.

Pipeline: filtered signals → spike inference → dF/F normalization
"""

from .core import run_calcium_deconvolution, CalciumDeconvolutionResult

__all__ = ["run_calcium_deconvolution", "CalciumDeconvolutionResult"]
