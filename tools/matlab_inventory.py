#!/usr/bin/env python3
"""Generate MATLAB codebase inventory, call graph, and Python 1:1 mapping tables."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
MATLAB_GLOB = "*.m"
ANALYSIS_DIR = REPO_ROOT / "artifacts" / "analysis"
INVENTORY_JSON = ANALYSIS_DIR / "matlab_inventory.json"
INVENTORY_MD = ANALYSIS_DIR / "matlab_inventory.md"
CALLGRAPH_JSON = ANALYSIS_DIR / "matlab_callgraph.json"
CALLGRAPH_EDGES_CSV = ANALYSIS_DIR / "matlab_callgraph_edges.csv"
MAPPING_CSV = ANALYSIS_DIR / "matlab_to_python_mapping.csv"
TOOLBOX_MD = ANALYSIS_DIR / "toolbox_gap_matrix.md"

FUNCTION_RE = re.compile(
    r"^\s*function\s*(?:(?:\[(?P<outs>[^\]]+)\]|(?P<out_single>[A-Za-z]\w*))\s*=\s*)?(?P<name>[A-Za-z]\w*)\s*(?:\((?P<ins>[^)]*)\))?",
    re.IGNORECASE,
)
CALL_RE = re.compile(r"(?<![\w\.])([A-Za-z]\w*)\s*\(")
CMD_RE = re.compile(r"^\s*([A-Za-z]\w*)\s*;?\s*(?:%.*)?$")

IGNORE_TOKENS = {
    "if",
    "for",
    "while",
    "switch",
    "case",
    "otherwise",
    "function",
    "classdef",
    "try",
    "catch",
    "return",
    "end",
    "parfor",
    "spmd",
    "else",
    "elseif",
}

TOOLBOX_PATTERNS: dict[str, tuple[str, ...]] = {
    "Image Processing Toolbox": (
        "imgaussfilt",
        "imopen",
        "imtophat",
        "imerode",
        "imclose",
        "imregionalmax",
        "bwlabeln",
        "regionprops",
        "bwconvhull",
        "improfile",
        "strel",
        "medfilt2",
        "imwarp",
        "imref2d",
    ),
    "Signal Processing Toolbox": ("gausswin", "findpeaks", "xcov", "pwelch", "medfilt1"),
    "Statistics and ML Toolbox": ("fitgmdist", "posterior", "kstest", "skewness"),
    "Parallel Computing Toolbox": (
        "parfor",
        "gcp",
        "parpool",
        "gpuArray",
        "gather",
        "gpuDevice",
        "feature(",
    ),
    "Optimization Toolbox": ("quadprog", "fmincon"),
    "Computer Vision Toolbox": (
        "vision.PointTracker",
        "estimateGeometricTransform",
        "affine2d",
        "detectMinEigenFeatures",
    ),
    "Graph APIs": ("graph(", "conncomp", "rmnode", "digraph("),
    "CVX": ("cvx_begin", "cvx_end"),
}


@dataclass
class MatlabFile:
    path: str
    sha256: str
    loc: int
    is_script: bool
    function_name: str | None
    inputs: list[str]
    outputs: list[str]
    dependencies: list[str]
    python_path: str



def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def _parse_function_signature(lines: list[str]) -> tuple[bool, str | None, list[str], list[str]]:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("%"):
            continue
        if stripped.lower().startswith("function"):
            match = FUNCTION_RE.match(line)
            if not match:
                return False, None, [], []
            name = match.group("name")
            outs_raw = match.group("outs")
            out_single = match.group("out_single")
            ins_raw = match.group("ins")

            if outs_raw:
                outputs = [tok.strip() for tok in outs_raw.split(",") if tok.strip()]
            elif out_single:
                outputs = [out_single.strip()]
            else:
                outputs = []

            inputs = [tok.strip() for tok in ins_raw.split(",") if tok.strip()] if ins_raw else []
            return False, name, inputs, outputs
        return True, None, [], []
    return True, None, [], []



def _collect_dependencies(lines: list[str], name_to_path: dict[str, str], self_path: str) -> list[str]:
    deps: set[str] = set()
    for line in lines:
        code = line.split("%", 1)[0]

        for match in CALL_RE.finditer(code):
            token = match.group(1)
            if token in IGNORE_TOKENS:
                continue
            dep = name_to_path.get(token)
            if dep and dep != self_path:
                deps.add(dep)

        cmd_match = CMD_RE.match(code)
        if cmd_match:
            token = cmd_match.group(1)
            if token in IGNORE_TOKENS:
                continue
            dep = name_to_path.get(token)
            if dep and dep != self_path:
                deps.add(dep)

    return sorted(deps)



def _python_mapping(rel_path: str) -> str:
    return f"src/min1pipe/matlab_mirror/{rel_path[:-2]}.py"



def _load_files() -> tuple[list[Path], dict[str, str]]:
    files = sorted(REPO_ROOT.rglob(MATLAB_GLOB))
    files = [p for p in files if ".git" not in p.parts]
    name_to_path = {p.stem: str(p.relative_to(REPO_ROOT)) for p in files}
    return files, name_to_path



def _build_inventory(files: list[Path], name_to_path: dict[str, str]) -> list[MatlabFile]:
    result: list[MatlabFile] = []
    for path in files:
        rel_path = str(path.relative_to(REPO_ROOT))
        text = path.read_text(errors="ignore")
        lines = text.splitlines()
        is_script, function_name, inputs, outputs = _parse_function_signature(lines)
        deps = _collect_dependencies(lines, name_to_path, rel_path)
        result.append(
            MatlabFile(
                path=rel_path,
                sha256=_sha256(path),
                loc=len(lines),
                is_script=is_script,
                function_name=function_name,
                inputs=inputs,
                outputs=outputs,
                dependencies=deps,
                python_path=_python_mapping(rel_path),
            )
        )
    return result



def _build_callgraph(inventory: list[MatlabFile]) -> dict[str, Any]:
    edges = []
    reverse: dict[str, list[str]] = defaultdict(list)
    for item in inventory:
        for dep in item.dependencies:
            edges.append({"src": item.path, "dst": dep})
            reverse[dep].append(item.path)

    outdeg = sorted(
        ({"path": item.path, "count": len(item.dependencies)} for item in inventory),
        key=lambda x: x["count"],
        reverse=True,
    )
    indeg = sorted(
        ({"path": item.path, "count": len(reverse.get(item.path, []))} for item in inventory),
        key=lambda x: x["count"],
        reverse=True,
    )

    by_path = {item.path: item for item in inventory}
    reachability: dict[str, dict[str, Any]] = {}
    entry_candidates = [
        "min1pipe.m",
        "min1pipe_HPC.m",
        "demo_min1pipe.m",
        "demo_min1pipe_HPC.m",
        "min1pipe_old.m",
    ]
    graph = {item.path: item.dependencies for item in inventory}

    for entry in entry_candidates:
        if entry not in graph:
            continue
        seen = {entry}
        dq = deque([entry])
        while dq:
            cur = dq.popleft()
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    dq.append(nxt)
        reachability[entry] = {
            "reachable_count": len(seen),
            "reachable": sorted(seen),
            "unreachable": sorted(set(graph) - seen),
        }

    return {
        "edges": edges,
        "indegree_top": indeg[:30],
        "outdegree_top": outdeg[:30],
        "reachability": reachability,
    }



def _toolbox_matrix(files: list[Path]) -> dict[str, list[dict[str, Any]]]:
    matrix: dict[str, list[dict[str, Any]]] = {}
    for toolbox, patterns in TOOLBOX_PATTERNS.items():
        rows: list[dict[str, Any]] = []
        for path in files:
            rel = str(path.relative_to(REPO_ROOT))
            text = path.read_text(errors="ignore")
            hits = sorted({pat for pat in patterns if pat in text})
            if hits:
                rows.append({"path": rel, "hits": hits})
        matrix[toolbox] = rows
    return matrix



def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")



def _write_inventory_md(inventory: list[MatlabFile], callgraph: dict[str, Any]) -> None:
    dir_counts = Counter(Path(item.path).parent.as_posix() if Path(item.path).parent.as_posix() != "." else "." for item in inventory)
    total_loc = sum(item.loc for item in inventory)

    lines = [
        "# MATLAB Inventory",
        "",
        f"- Total MATLAB files: **{len(inventory)}**",
        f"- Total LOC: **{total_loc}**",
        "",
        "## Directory Counts",
        "",
    ]
    for d, c in sorted(dir_counts.items()):
        lines.append(f"- `{d}`: {c}")

    lines.extend(["", "## Highest Outdegree", ""])
    for row in callgraph["outdegree_top"][:15]:
        lines.append(f"- `{row['path']}`: {row['count']}")

    lines.extend(["", "## Highest Indegree", ""])
    for row in callgraph["indegree_top"][:15]:
        lines.append(f"- `{row['path']}`: {row['count']}")

    lines.extend(["", "## Top-level Mapping", "", "| MATLAB | Python |", "|---|---|"])
    for item in sorted((i for i in inventory if "/" not in i.path), key=lambda x: x.path):
        lines.append(f"| `{item.path}` | `{item.python_path}` |")

    lines.append("")
    INVENTORY_MD.write_text("\n".join(lines) + "\n")



def _write_mapping_csv(inventory: list[MatlabFile]) -> None:
    with MAPPING_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "matlab_path",
                "python_path",
                "is_script",
                "function_name",
                "inputs",
                "outputs",
                "loc",
                "sha256",
            ],
        )
        writer.writeheader()
        for item in inventory:
            writer.writerow(
                {
                    "matlab_path": item.path,
                    "python_path": item.python_path,
                    "is_script": item.is_script,
                    "function_name": item.function_name or "",
                    "inputs": ";".join(item.inputs),
                    "outputs": ";".join(item.outputs),
                    "loc": item.loc,
                    "sha256": item.sha256,
                }
            )



def _write_edges_csv(callgraph: dict[str, Any]) -> None:
    with CALLGRAPH_EDGES_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["src", "dst"])
        writer.writeheader()
        for edge in callgraph["edges"]:
            writer.writerow(edge)



def _write_toolbox_md(matrix: dict[str, list[dict[str, Any]]]) -> None:
    lines = ["# Toolbox Gap Matrix", ""]
    for toolbox, rows in matrix.items():
        lines.append(f"## {toolbox}")
        lines.append("")
        if not rows:
            lines.append("- No usages detected.")
            lines.append("")
            continue
        lines.append("| File | MATLAB APIs | Proposed Python Workaround |")
        lines.append("|---|---|---|")
        for row in rows:
            apis = ", ".join(f"`{h}`" for h in row["hits"])
            if toolbox == "CVX":
                workaround = "`cvxpy` + `scipy.optimize` fallback"
            elif toolbox == "Computer Vision Toolbox":
                workaround = "`opencv-python` (`calcOpticalFlowPyrLK`, `estimateAffine2D`)"
            elif toolbox == "Image Processing Toolbox":
                workaround = "`scikit-image` + `scipy.ndimage`"
            elif toolbox == "Signal Processing Toolbox":
                workaround = "`scipy.signal`"
            elif toolbox == "Statistics and ML Toolbox":
                workaround = "`scikit-learn` + `scipy.stats`"
            elif toolbox == "Parallel Computing Toolbox":
                workaround = "`joblib`/`concurrent.futures`; optional `cupy`"
            elif toolbox == "Graph APIs":
                workaround = "`networkx`"
            elif toolbox == "Optimization Toolbox":
                workaround = "`scipy.optimize` / `osqp`"
            else:
                workaround = "Manual mapping"
            lines.append(f"| `{row['path']}` | {apis} | {workaround} |")
        lines.append("")
    TOOLBOX_MD.write_text("\n".join(lines) + "\n")



def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    files, name_to_path = _load_files()
    inventory = _build_inventory(files, name_to_path)

    callgraph = _build_callgraph(inventory)
    toolbox = _toolbox_matrix(files)

    inv_payload = {
        "generated_from": str(REPO_ROOT),
        "total_files": len(inventory),
        "files": [
            {
                "path": item.path,
                "sha256": item.sha256,
                "loc": item.loc,
                "is_script": item.is_script,
                "function_name": item.function_name,
                "inputs": item.inputs,
                "outputs": item.outputs,
                "dependencies": item.dependencies,
                "python_path": item.python_path,
            }
            for item in inventory
        ],
    }

    _write_json(INVENTORY_JSON, inv_payload)
    _write_json(CALLGRAPH_JSON, callgraph)
    _write_inventory_md(inventory, callgraph)
    _write_mapping_csv(inventory)
    _write_edges_csv(callgraph)
    _write_toolbox_md(toolbox)

    print(f"Inventory written to {INVENTORY_JSON}")
    print(f"Call graph written to {CALLGRAPH_JSON}")
    print(f"Mapping CSV written to {MAPPING_CSV}")


if __name__ == "__main__":
    main()
