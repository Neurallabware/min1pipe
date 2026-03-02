"""Strict standalone calcium deconvolution module for calcium imaging.

Pipeline: refined signal -> constrained-foopsi-style fallback -> dF/F normalization.
"""

from .core import run_calcium_deconvolution, CalciumDeconvolutionResult

__all__ = ["run_calcium_deconvolution", "CalciumDeconvolutionResult"]
