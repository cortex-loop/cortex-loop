#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from internal.truth.status import STATUS_DOC, load_status


def render_status(data: dict[str, object]) -> str:
    baseline = data["accepted_baseline"]
    bootstrap = data["bootstrap"]
    goal = data["product_goal"]
    work_today = data["work_today"]
    subsystems = data["subsystems"]
    hosts = data["hosts"]
    conformance_summary = data["conformance_summary"]
    proof_commands = data["proof_commands"]
    retained_data = data["retained_data"]
    blocked_moves = data["blocked_moves"]
    active_docs = data["active_docs"]

    lines: list[str] = [
        "# CORTEX Status",
        "",
        "Surface: product",
        "",
        "_Generated from `internal/truth/cortex_status.yaml`. Edit the registry, then run `python3 internal/truth/generate_status.py`._",
        "",
        "## Baseline",
        "",
        f"- Branch: `{baseline['branch']}`",
        f"- Commit: `{baseline['commit']}`",
        f"- Summary: {baseline['summary']}",
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
            "## Work Today",
            "",
            f"- Train: `{work_today['slug']}`",
            f"- Surface: `{work_today['surface']}`",
            f"- Executive benefit: {work_today['executive_benefit']}",
            f"- Why now: {work_today['why_now']}",
            f"- Primary metric: `{work_today['primary_metric']}`",
            f"- Guardrail: `{work_today['guardrail']}`",
            f"- Kill rule: `{work_today['kill_rule']}`",
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
            "## Conformance Summary Truth",
            "",
            f"- Accepted next decision: `{conformance_summary['accepted_next_decision']}`",
            f"- Shipping default: `{conformance_summary['shipping_default']}`",
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
    lines.extend(["", "## Blocked Moves", ""])
    lines.extend(f"- {item}" for item in blocked_moves)
    lines.extend(["", "## Active Docs", ""])
    lines.extend(f"- `{path}`" for path in active_docs)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the single Cortex status doc.")
    parser.add_argument("--check", action="store_true", help="Fail if the generated doc is out of date.")
    args = parser.parse_args()

    rendered = render_status(load_status())
    if args.check:
        current = STATUS_DOC.read_text(encoding="utf-8") if STATUS_DOC.exists() else ""
        if current != rendered:
            raise SystemExit("docs/CORTEX_STATUS.md is out of date. Run python3 internal/truth/generate_status.py")
        return 0

    STATUS_DOC.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
