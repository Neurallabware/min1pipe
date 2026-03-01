#!/usr/bin/env python3
"""Generate 1:1 Python module mirror for MATLAB source files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_JSON = REPO_ROOT / "artifacts" / "analysis" / "matlab_inventory.json"
SRC_ROOT = REPO_ROOT / "src" / "min1pipe"
MIRROR_ROOT = SRC_ROOT / "matlab_mirror"

HEADER = '''"""Auto-generated MATLAB 1:1 mirror module.

This file preserves path and callable shape from the original MATLAB source.
Behavioral implementation may be incremental for complex algorithms.
"""
'''


def _safe_identifier(name: str) -> str:
    name = name.strip()
    if not name:
        return "arg"
    if name == "~":
        return "arg"
    if name[0].isdigit():
        name = f"arg_{name}"
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name)



def _make_function_stub(item: dict[str, Any], rel_path: str) -> str:
    fn_name = _safe_identifier(item.get("function_name") or Path(rel_path).stem)
    raw_inputs = [_safe_identifier(inp) for inp in item.get("inputs", [])]
    seen: dict[str, int] = {}
    inputs: list[str] = []
    for idx, name in enumerate(raw_inputs):
        base = name or f"arg_{idx}"
        if base in seen:
            seen[base] += 1
            unique = f"{base}_{seen[base]}"
        else:
            seen[base] = 0
            unique = base
        inputs.append(unique)
    if not inputs:
        signature = ""
    else:
        signature = ", ".join(f"{arg}: Any | None = None" for arg in inputs)

    outputs = item.get("outputs", [])
    if len(outputs) == 0:
        ret_ann = "None"
    elif len(outputs) == 1:
        ret_ann = "Any"
    else:
        ret_ann = "tuple[Any, ...]"

    doc = [
        f"MATLAB source: `{item['path']}`.",
        "",
        f"Original function: `{item.get('function_name')}`",
    ]
    if inputs:
        doc.append(f"Original inputs: {', '.join(item['inputs'])}")
    if outputs:
        doc.append(f"Original outputs: {', '.join(outputs)}")

    lines = [
        HEADER,
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "",
        f"def {fn_name}({signature}) -> {ret_ann}:",
        "    \"\"\"",
    ]
    lines.extend([f"    {line}" if line else "" for line in doc])
    lines.extend(
        [
            "    \"\"\"",
            f"    raise NotImplementedError('Function {fn_name} from {item['path']} is not implemented yet.')",
            "",
        ]
    )
    return "\n".join(lines)



def _make_script_stub(item: dict[str, Any]) -> str:
    stem = Path(item["path"]).stem
    lines = [
        HEADER,
        "from __future__ import annotations",
        "",
        "",
        "def main() -> None:",
        "    \"\"\"",
        f"    MATLAB script mirror for `{item['path']}`.",
        "    \"\"\"",
        f"    raise NotImplementedError('Script {item['path']} is not implemented yet.')",
        "",
        "",
        "if __name__ == '__main__':",
        "    main()",
        "",
    ]
    return "\n".join(lines)



def _write_init_files(target: Path) -> None:
    cur = target
    while cur != SRC_ROOT.parent:
        init = cur / "__init__.py"
        if not init.exists():
            init.write_text('"""Auto-generated package."""\n')
        if cur == SRC_ROOT:
            break
        cur = cur.parent



def main() -> None:
    if not INVENTORY_JSON.exists():
        raise FileNotFoundError(f"Inventory not found: {INVENTORY_JSON}")

    payload = json.loads(INVENTORY_JSON.read_text())
    files = payload["files"]

    for item in files:
        rel_py = item["python_path"].replace("src/min1pipe/", "", 1)
        target = SRC_ROOT / rel_py
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_init_files(target.parent)

        if item["is_script"]:
            code = _make_script_stub(item)
        else:
            code = _make_function_stub(item, rel_py)
        target.write_text(code)

    # Root package init and compat exports.
    root_init = SRC_ROOT / "__init__.py"
    root_init.write_text(
        "\n".join(
            [
                '"""MIN1PIPE Python package (MATLAB-to-Python migration)."""',
                "",
                "from .pipeline import min1pipe, min1pipe_hpc",
                "",
                "__all__ = ['min1pipe', 'min1pipe_hpc']",
                "",
            ]
        )
    )

    (SRC_ROOT / "pipeline.py").write_text(
        "\n".join(
            [
                '"""High-level pipeline entrypoints."""',
                "",
                "from __future__ import annotations",
                "",
                "from typing import Any",
                "",
                "from .matlab_mirror.min1pipe import min1pipe as _min1pipe_impl",
                "from .matlab_mirror.min1pipe_HPC import min1pipe_HPC as _min1pipe_hpc_impl",
                "",
                "",
                "def min1pipe(*args: Any, **kwargs: Any) -> Any:",
                "    \"\"\"Entry point compatible with MATLAB `min1pipe.m`.\"\"\"",
                "    return _min1pipe_impl(*args, **kwargs)",
                "",
                "",
                "def min1pipe_hpc(*args: Any, **kwargs: Any) -> Any:",
                "    \"\"\"Entry point compatible with MATLAB `min1pipe_HPC.m`.\"\"\"",
                "    return _min1pipe_hpc_impl(*args, **kwargs)",
                "",
            ]
        )
    )

    print(f"Generated Python mirror under {MIRROR_ROOT}")


if __name__ == "__main__":
    main()
