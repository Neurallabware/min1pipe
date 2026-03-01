#!/usr/bin/env python3
"""Generate conversion status and Notion-compatible progress report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INV = REPO_ROOT / "artifacts" / "analysis" / "matlab_inventory.json"
FIX = REPO_ROOT / "artifacts" / "parity" / "module_fixtures.json"
RES = REPO_ROOT / "artifacts" / "parity" / "runtime" / "parity_results.json"
OUT_MD = REPO_ROOT / "artifacts" / "reports" / "conversion_status.md"
OUT_NOTION = REPO_ROOT / "artifacts" / "reports" / "notion_progress.md"
STRUCT_MD = REPO_ROOT / "docs" / "python_project_structure.md"



def _load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text())



def main() -> None:
    inv = _load_json(INV, {"files": []})
    fixtures = _load_json(FIX, [])
    results = _load_json(RES, [])

    fixture_by_path = {x["matlab_path"]: x for x in fixtures}
    result_by_path = {x["matlab_path"]: x for x in results}

    rows = []
    for file_row in inv["files"]:
        path = file_row["path"]
        fx = fixture_by_path.get(path, {})
        rs = result_by_path.get(path, {})
        rows.append(
            {
                "matlab_path": path,
                "python_path": file_row["python_path"],
                "function_name": file_row.get("function_name") or "(script)",
                "fixture_status": fx.get("status", "pending"),
                "parity_status": rs.get("status", "not-run"),
                "max_abs_dev": rs.get("max_abs_dev", ""),
                "max_rel_dev": rs.get("max_rel_dev", ""),
                "notes": rs.get("message", fx.get("reason", "")),
            }
        )

    total = len(rows)
    ready = sum(1 for r in rows if r["fixture_status"] == "ready")
    passed = sum(1 for r in rows if r["parity_status"] == "pass")
    skipped = sum(1 for r in rows if r["parity_status"] == "skip")

    lines = [
        "# Conversion Status",
        "",
        f"- Total MATLAB modules: **{total}**",
        f"- Ready parity fixtures: **{ready}**",
        f"- Parity passed: **{passed}**",
        f"- Parity skipped/pending: **{skipped}**",
        "",
        "| MATLAB Module | Python Module | Function | Fixture | Parity | Max Abs Dev | Max Rel Dev | Notes |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]

    for r in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | {} | {} | {} | {} | {} |".format(
                r["matlab_path"],
                r["python_path"],
                r["function_name"],
                r["fixture_status"],
                r["parity_status"],
                r["max_abs_dev"],
                r["max_rel_dev"],
                str(r["notes"]).replace("|", "\\|"),
            )
        )

    OUT_MD.write_text("\n".join(lines) + "\n")

    notion_lines = [
        "# MIN1PIPE Migration Progress",
        "",
        "## Milestones",
        "",
        "- [x] Phase 1: Inventory, call graph, toolbox-gap matrix, and 1:1 mapping artifacts generated.",
        "- [x] Phase 2 (initial): 1:1 Python mirror generated for all MATLAB files.",
        "- [x] Phase 2 (foundation): Core shared utilities implemented and unit-tested.",
        "- [x] Phase 2 (parity infra): Dual-mode parity harness scaffold implemented.",
        "- [x] Phase 3: Installable package + dedicated venv bootstrap scaffold created.",
        "- [x] Phase 4 (initial): Visualization notebook scaffold and demo plot path created.",
        "- [ ] Full algorithmic parity across all 146 modules.",
        "",
        "## Current Metrics",
        "",
        f"- Modules mapped: **{total}/{total}**",
        f"- Parity-ready modules: **{ready}/{total}**",
        f"- Parity pass count: **{passed}**",
        f"- Pending parity modules: **{total - ready}**",
        "",
        "## Module Table",
        "",
        "| Module | Python Path | Status | Parity | Max Dev |",
        "|---|---|---|---|---|",
    ]

    for r in rows:
        max_dev = r["max_abs_dev"] if r["max_abs_dev"] != "" else ""
        notion_lines.append(
            f"| `{r['matlab_path']}` | `{r['python_path']}` | {r['fixture_status']} | {r['parity_status']} | {max_dev} |"
        )

    OUT_NOTION.write_text("\n".join(notion_lines) + "\n")

    struct_lines = [
        "# Python Project Structure",
        "",
        "```text",
        "src/min1pipe/",
        "  __init__.py",
        "  cli.py",
        "  pipeline.py",
        "  parity/",
        "  matlab_mirror/",
        "    <1:1 MATLAB path mirrors>.py",
        "tests/",
        "  unit/",
        "  parity/",
        "artifacts/analysis/",
        "artifacts/parity/",
        "artifacts/reports/",
        "```",
        "",
        "Refer to `artifacts/analysis/matlab_to_python_mapping.csv` for exact module-level associations.",
    ]
    STRUCT_MD.write_text("\n".join(struct_lines) + "\n")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_NOTION}")
    print(f"Wrote {STRUCT_MD}")


if __name__ == "__main__":
    main()
