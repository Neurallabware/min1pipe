"""Optional MATLAB Engine adapter for parity tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MatlabCallSpec:
    function_name: str
    nargout: int
    inputs: list[Any]


class MatlabEngineAdapter:
    """Thin wrapper around MATLAB Engine API.

    This adapter is intentionally optional. If MATLAB Engine is unavailable,
    tests should fall back to golden artifacts.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self._eng = None

    @staticmethod
    def is_available() -> bool:
        try:
            import matlab.engine  # type: ignore

            return True
        except Exception:
            return False

    def __enter__(self) -> "MatlabEngineAdapter":
        import matlab.engine  # type: ignore

        self._eng = matlab.engine.start_matlab()
        self._eng.addpath(self._eng.genpath(str(self.repo_root)), nargout=0)
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._eng is not None:
            self._eng.quit()
            self._eng = None

    def call(self, spec: MatlabCallSpec) -> Any:
        if self._eng is None:
            raise RuntimeError("MATLAB engine is not initialized")
        return self._eng.feval(spec.function_name, *spec.inputs, nargout=spec.nargout)
