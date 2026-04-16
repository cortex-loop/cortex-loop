#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.truth.status import STATUS_DOC, load_status


STATUS_CLASS = {
    "green": "good",
    "yellow": "warn",
    "red": "bad",
    "gray": "deferred",
}


def _render_system_map(nodes: list[dict[str, object]], edges: list[dict[str, str]]) -> list[str]:
    lines = ["```mermaid", "flowchart TD"]
    for node in nodes:
        lines.append(f'    {node["id"]}["{node["label"]}"]')
    for edge in edges:
        connector = edge.get("style", "-->")
        lines.append(f'    {edge["from"]} {connector} {edge["to"]}')
    lines.extend(
        [
            "",
            "    classDef good fill:#dff3e4,stroke:#2f855a,color:#1f2937;",
            "    classDef warn fill:#fff3cd,stroke:#b7791f,color:#1f2937;",
            "    classDef bad fill:#f8d7da,stroke:#c53030,color:#1f2937;",
            "    classDef deferred fill:#e5e7eb,stroke:#6b7280,color:#1f2937;",
            "",
        ]
    )
    for node in nodes:
        css_class = STATUS_CLASS[node["status"]]
        lines.append(f'    class {node["id"]} {css_class};')
    lines.append("```")
    return lines


def _format_path_list(paths: list[str]) -> str:
    if not paths:
        return "_planned only_"
    return ", ".join(f"`{path}`" for path in paths)


def render_status(data: dict[str, object]) -> str:
    resting_state = data["resting_state"]
    bootstrap = data["bootstrap"]
    goal = data["product_goal"]
    identity = data["identity"]
    bio_to_code_matrix = data["bio_to_code_matrix"]
    math_to_code_rules = data["math_to_code_rules"]
    work_today = data["work_today"]
    next_product_train = data["next_product_train"]
    system_map = data["system_map"]
    subsystems = data["subsystems"]
    packet_anchors = data["packet_to_code_anchors"]
    hosts = data["hosts"]
    conformance_summary = data["conformance_summary"]
    closure_gates = data["closure_gates"]
    proof_commands = data["proof_commands"]
    retained_data = data["retained_data"]
    retained_refs = data["retained_evidence_refs"]
    blocked_moves = data["blocked_moves"]
    where_to_work = data["where_to_work"]
    active_docs = data["active_docs"]
    host_truth = ", ".join(
        f"`{host['name']}={host['conformance']}`" for host in hosts
    )

    lines: list[str] = [
        "# CORTEX Status",
        "",
        "Surface: product",
        "",
        "_Generated from `internal/truth/cortex_status.json`. Edit the registry, then run `python3 internal/truth/generate_status.py`._",
        "",
        "## Resting State",
        "",
        f"- Branch: `{resting_state['branch']}`",
        f"- Rule: {resting_state['summary']}",
        "",
        "## Bootstrap",
        "",
    ]
    lines.extend(f"- `{item}`" for item in bootstrap)
    lines.extend(
        [
            "",
            "## Goal",
            "",
            f"**{goal['title']}**",
            "",
            goal["statement"],
            "",
            "Not product:",
        ]
    )
    lines.extend(f"- `{item}`" for item in goal["non_product"])
    lines.extend(
        [
            "",
            "## Identity And Research Stance",
            "",
            identity["statement"],
            "",
            "Research stance:",
        ]
    )
    lines.extend(f"- {item}" for item in identity["research_stance"])
    lines.extend(
        [
            "",
            "Answering stance:",
        ]
    )
    lines.extend(f"- {item}" for item in identity["answering_stance"])
    lines.extend(
        [
            "",
            "## Live Product Truth",
            "",
            f"- Shipping default: `{conformance_summary['shipping_default']}`",
            f"- Conformance truth: {host_truth}",
            f"- Accepted conformance next decision: `{conformance_summary['accepted_next_decision']}`",
            "",
            "## Current Focus",
            "",
            f"- Current tracked train: `{work_today['slug']}`",
            f"- Active quality/risk focus: {work_today['note']}",
            f"- Next product train after the current focus: `{next_product_train['slug']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Bio-To-Code Matrix",
            "",
            "| Executive Skill | What We Are Stealing | Status | Weight | Code Homes | Proof Surfaces | Next Move |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in bio_to_code_matrix:
        lines.append(
            f"| {item['skill']} | {item['stolen_skill']} | `{item['status']}` | `{item['weight']}` | {_format_path_list(item['code_homes'])} | {_format_path_list(item['proof_surfaces'])} | {item['next_move']} |"
        )
    lines.extend(
        [
            "",
            "## Math To Code Rules",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in math_to_code_rules["rules"])
    lines.extend(
        [
            f"- Law revision rule: {math_to_code_rules['law_revision_rule']}",
            "",
            "## System Map",
            "",
        ]
    )
    lines.extend(_render_system_map(system_map["nodes"], system_map["edges"]))
    lines.extend(
        [
            "",
            "## Subsystems",
            "",
            "| Subsystem | Status | Code Homes | Note |",
            "| --- | --- | --- | --- |",
        ]
    )
    for subsystem in subsystems:
        homes = ", ".join(f"`{home}`" for home in subsystem["code_homes"])
        lines.append(
            f"| {subsystem['label']} | `{subsystem['status']}` | {homes} | {subsystem['note']} |"
        )
    lines.extend(
        [
            "",
            "## Packet To Code",
            "",
            "| Packet | Responsibility | Code Homes | Proof Surfaces |",
            "| --- | --- | --- | --- |",
        ]
    )
    for anchor in packet_anchors:
        homes = ", ".join(f"`{home}`" for home in anchor["code_homes"])
        proofs = ", ".join(f"`{surface}`" for surface in anchor["proof_surfaces"])
        lines.append(
            f"| `{anchor['packet']}` | {anchor['responsibility']} | {homes} | {proofs} |"
        )
    lines.extend(
        [
            "",
            "## Hosts",
            "",
            "| Host | Shipping | Conformance | Strongest Surface | Daily Iteration | Code Home |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for host in hosts:
        lines.append(
            f"| `{host['name']}` | `{host['shipping']}` | `{host['conformance']}` | `{host['strongest_surface']}` | `{host['daily_iteration_surface']}` | `{host['code_home']}` |"
        )
    lines.extend(
        [
            "",
            "## Shipping And Conformance Truth",
            "",
            f"- Shipping default: `{conformance_summary['shipping_default']}`",
            f"- Accepted conformance next decision: `{conformance_summary['accepted_next_decision']}`",
            "",
            "## Closure Gates",
            "",
            "Workflow gates marked `required` are contractual gates checked by `repo_workflow.py`, not a claim about every attached local worktree at render time.",
            "",
            "| Gate | Status | Note |",
            "| --- | --- | --- |",
        ]
    )
    for gate in closure_gates:
        lines.append(f"| `{gate['id']}` | `{gate['status']}` | {gate['note']} |")
    lines.extend(
        [
            "",
            "## Next Product Train",
            "",
            f"- Train: `{next_product_train['slug']}`",
            f"- Surface: `{next_product_train['surface']}`",
            f"- Executive benefit: {next_product_train['executive_benefit']}",
            f"- Why now: {next_product_train['why_now']}",
            f"- Primary metric: {next_product_train['primary_metric']}",
            f"- Guardrail: {next_product_train['guardrail']}",
            f"- Kill rule: {next_product_train['kill_rule']}",
            "",
            "## Where To Work Next",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in where_to_work)
    lines.extend(
        [
            "",
            "## Canonical Proof",
            "",
        ]
    )
    for label, commands in proof_commands.items():
        lines.append(f"**{label.title()}**")
        lines.append("")
        lines.extend(f"- `{command}`" for command in commands)
        lines.append("")
    lines.extend(["## Retained Data", ""])
    for entry in retained_data:
        labels = ", ".join(f"`{label}`" for label in entry["retained_labels"])
        lines.append(f"- `{entry['lane']}` at `{entry['root']}` keeps {labels}")
        lines.append(f"  Policy: {entry['policy']}")
    lines.extend(["", "## Retained Evidence Refs", ""])
    for ref in retained_refs:
        lines.append(f"- `{ref['label']}` -> `{ref['ref']}`")
        lines.append(f"  Purpose: {ref['purpose']}")
    lines.extend(["", "## Blocked Moves", ""])
    lines.extend(f"- {item}" for item in blocked_moves)
    lines.extend(["", "## Active Docs", ""])
    lines.extend(f"- `{path}`" for path in active_docs)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the single Cortex status doc.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the generated doc is out of date.",
    )
    args = parser.parse_args()

    rendered = render_status(load_status())
    if args.check:
        current = STATUS_DOC.read_text(encoding="utf-8") if STATUS_DOC.exists() else ""
        if current != rendered:
            raise SystemExit(
                "docs/CORTEX_STATUS.md is out of date. Run python3 internal/truth/generate_status.py"
            )
        return 0

    STATUS_DOC.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
