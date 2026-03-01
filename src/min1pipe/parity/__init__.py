"""Parity test infrastructure for MATLAB-vs-Python validation."""

from .runner import ParityOutcome, run_python_case
from .tolerances import get_tolerance

__all__ = ["ParityOutcome", "run_python_case", "get_tolerance"]
