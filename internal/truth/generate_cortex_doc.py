#!/usr/bin/env python3
"""Generate the dynamic sections of docs/CORTEX.md from the status registry.

CORTEX.md is the canonical narrative authority for what Cortex is, where it
came from, and where it is going. The narrative sections (Identity, V1 to V2
evolution, Implementation discipline, How to use this document) are manually
maintained because their job is to carry the project's voice. The dynamic
sections — the failure-modes coverage table, the math to code map, and the
current state and strategy block — are generated from
``internal/truth/cortex_status.json`` so they cannot drift away from
operational truth.

Generated content lives between fenced markers of the form::

    <!-- BEGIN GENERATED: <key> -->
    ...
    <!-- END GENERATED: <key> -->

Anything outside those fences is preserved verbatim. Anything between them
is replaced on regeneration. ``--check`` fails if regeneration would change
the file, exactly like ``generate_status.py``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.truth.status import load_status  # noqa: E402

CORTEX_DOC = ROOT / "docs" / "CORTEX.md"

GENERATED_KEYS = (
    "failure-modes-coverage",
    "math-to-code-map",
    "current-state-and-strategy",
)


def _fence_pattern(key: str) -> re.Pattern[str]:
    return re.compile(
        rf"(<!-- BEGIN GENERATED: {re.escape(key)} -->)(.*?)(<!-- END GENERATED: {re.escape(key)} -->)",
        re.DOTALL,
    )


def _splice(text: str, key: str, new_body: str) -> str:
    pattern = _fence_pattern(key)
    if not pattern.search(text):
        raise SystemExit(
            f"docs/CORTEX.md is missing the generated fence for '{key}'. "
            f"Expected '<!-- BEGIN GENERATED: {key} -->' ... "
            f"'<!-- END GENERATED: {key} -->'."
        )
    replacement = f"<!-- BEGIN GENERATED: {key} -->\n{new_body}\n<!-- END GENERATED: {key} -->"
    return pattern.sub(lambda _match: replacement, text, count=1)


def _render_failure_modes_coverage(matrix: list[dict[str, Any]]) -> str:
    lines = [
        "| Skill | Stolen from | Status | Code homes | Proof surfaces |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in matrix:
        skill = str(entry["skill"])
        stolen = str(entry["stolen_skill"])
        status = str(entry["status"])
        code = ", ".join(f"`{path}`" for path in entry["code_homes"])
        proof = ", ".join(f"`{path}`" for path in entry["proof_surfaces"])
        lines.append(
            f"| {skill} | {stolen} | `{status}` (weight {entry['weight']}) | {code} | {proof} |"
        )
    return "\n".join(lines)


def _render_math_to_code_map(entries: list[dict[str, Any]]) -> str:
    lines = [
        "| Object | Packet ref | Code home | Proof surface | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        label = str(entry["label"])
        packet_ref = str(entry["packet_ref"])
        code = ", ".join(f"`{path}`" for path in entry["code_refs"])
        proof = ", ".join(f"`{path}`" for path in entry["proof_refs"])
        status = str(entry["status"])
        identifier = str(entry["id"])
        lines.append(
            f"| **{label}** (`{identifier}`) | {packet_ref} | {code} | {proof} | `{status}` |"
        )
    return "\n".join(lines)


def _render_current_state(data: dict[str, Any]) -> str:
    work_today = data["work_today"]
    next_train = data["next_product_train"]
    research = data.get("research_lines_under_evaluation", []) or []
    completion = data["executive_completion"]
    matrix = data["bio_to_code_matrix"]
    where_to_work = data.get("where_to_work", [])
    conformance = data["conformance_summary"]
    hosts = data["hosts"]

    landed = sum(1 for entry in matrix if entry["status"] == "landed")
    partial = sum(1 for entry in matrix if entry["status"] == "partial")
    north_star = sum(1 for entry in matrix if entry["status"] == "north_star")
    weight_total = sum(entry["weight"] for entry in matrix)
    threshold = completion["shippable_threshold_percent"]

    host_lines = []
    for host in hosts:
        host_lines.append(
            f"- `{host['name']}` — {host['conformance']}; "
            f"shipping `{host['shipping']}`; surface `{host['strongest_surface']}`"
        )

    lines = [
        "### Bio-to-Code Coverage",
        "",
        f"- Skills landed: {landed} of {len(matrix)} (weights total {weight_total}; "
        f"shippable threshold {threshold}%).",
        f"- Partial: {partial}; north-star (not yet earned): {north_star}.",
        "",
        "### Current Train",
        "",
        f"- Slug: `{work_today['slug']}`",
        "",
        "### Next Product Train",
        "",
    ]
    next_slug = next_train.get("slug")
    if next_slug is None:
        lines.append("- Slug: _none queued yet_")
    else:
        lines.append(f"- Slug: `{next_slug}`")
        lines.append(
            f"- Surface: `{next_train['surface']}`"
        )
        lines.append(
            f"- Why now: {next_train.get('why_now', '')}"
        )
    lines.extend(
        [
            "",
            "### Research Lines Under Evaluation",
            "",
        ]
    )
    if not research:
        lines.append("- _none_")
    else:
        for entry in research:
            lines.append(
                f"- `{entry['slug']}` (`{entry.get('stage', '')}`) — {entry.get('summary', '')}"
            )
    lines.extend(
        [
            "",
            "### Hosts and Shipping Defaults",
            "",
        ]
    )
    lines.extend(host_lines)
    lines.extend(
        [
            "",
            f"- Shipping default lane: `{conformance['shipping_default']}`",
            f"- Accepted next conformance decision: `{conformance['accepted_next_decision']}`",
            "",
            "### Active Leverage and Where to Work",
            "",
        ]
    )
    if not where_to_work:
        lines.append("- _no explicit leverage entries recorded_")
    else:
        for item in where_to_work:
            lines.append(f"- {item}")
    return "\n".join(lines)


def render_cortex_doc(data: dict[str, Any], existing: str) -> str:
    matrix = data["bio_to_code_matrix"]
    math_map = data.get("math_to_code_map", [])
    bodies = {
        "failure-modes-coverage": _render_failure_modes_coverage(matrix),
        "math-to-code-map": _render_math_to_code_map(math_map),
        "current-state-and-strategy": _render_current_state(data),
    }
    rendered = existing
    for key in GENERATED_KEYS:
        rendered = _splice(rendered, key, bodies[key])
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the dynamic sections of docs/CORTEX.md from the registry."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the generated sections are out of date.",
    )
    args = parser.parse_args(argv)

    if not CORTEX_DOC.exists():
        raise SystemExit(
            "docs/CORTEX.md does not exist; author the manual sections "
            "and the generated fences before running generate_cortex_doc.py."
        )
    current = CORTEX_DOC.read_text(encoding="utf-8")
    rendered = render_cortex_doc(load_status(), current)
    if args.check:
        if current != rendered:
            raise SystemExit(
                "docs/CORTEX.md generated sections are out of date. "
                "Run python3 internal/truth/generate_cortex_doc.py"
            )
        return 0
    if current != rendered:
        CORTEX_DOC.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
