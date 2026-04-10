"""Shared helpers for the committed mediation evidence package."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class PackageLayout:
    repo_root: Path
    docs_root: Path
    mediation_claude_packet_root: Path
    mediation_reference_packet_root: Path
    mediation_gemini_packet_root: Path
    mediation_openai_packet_root: Path
    scenario_catalog_path: Path
    evaluation_plan_path: Path
    failure_taxonomy_path: Path
    paired_ledger_path: Path
    axis_table_path: Path
    burden_table_path: Path
    host_split_table_path: Path
    evidence_note_path: Path


def build_layout(repo_root: Path | None = None) -> PackageLayout:
    resolved_repo_root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    docs_root = resolved_repo_root / "docs"
    lab_docs_root = docs_root / "archive" / "lab"
    return PackageLayout(
        repo_root=resolved_repo_root,
        docs_root=docs_root,
        mediation_claude_packet_root=lab_docs_root / "mediation_evidence" / "claude",
        mediation_reference_packet_root=lab_docs_root / "mediation_evidence" / "reference",
        mediation_gemini_packet_root=lab_docs_root / "mediation_evidence" / "gemini",
        mediation_openai_packet_root=lab_docs_root / "mediation_evidence" / "openai",
        scenario_catalog_path=lab_docs_root / "CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md",
        evaluation_plan_path=lab_docs_root / "CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md",
        failure_taxonomy_path=lab_docs_root / "CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0.md",
        paired_ledger_path=lab_docs_root / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md",
        axis_table_path=lab_docs_root / "CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md",
        burden_table_path=lab_docs_root / "CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md",
        host_split_table_path=lab_docs_root / "CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md",
        evidence_note_path=lab_docs_root / "CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md",
    )


DEFAULT_LAYOUT = build_layout()

REPO_ROOT = DEFAULT_LAYOUT.repo_root
DOCS_ROOT = DEFAULT_LAYOUT.docs_root
MEDIATION_CLAUDE_PACKET_ROOT = DEFAULT_LAYOUT.mediation_claude_packet_root
MEDIATION_REFERENCE_PACKET_ROOT = DEFAULT_LAYOUT.mediation_reference_packet_root
MEDIATION_GEMINI_PACKET_ROOT = DEFAULT_LAYOUT.mediation_gemini_packet_root
MEDIATION_OPENAI_PACKET_ROOT = DEFAULT_LAYOUT.mediation_openai_packet_root
SCENARIO_CATALOG_PATH = DEFAULT_LAYOUT.scenario_catalog_path
EVALUATION_PLAN_PATH = DEFAULT_LAYOUT.evaluation_plan_path
FAILURE_TAXONOMY_PATH = DEFAULT_LAYOUT.failure_taxonomy_path
PAIRED_LEDGER_PATH = DEFAULT_LAYOUT.paired_ledger_path
AXIS_TABLE_PATH = DEFAULT_LAYOUT.axis_table_path
BURDEN_TABLE_PATH = DEFAULT_LAYOUT.burden_table_path
HOST_SPLIT_TABLE_PATH = DEFAULT_LAYOUT.host_split_table_path
EVIDENCE_NOTE_PATH = DEFAULT_LAYOUT.evidence_note_path

VERDICTS = {"negative", "neutral", "mixed", "candidate_positive", "insufficient"}
PAIR_STATUSES = {"not_recorded", "usable", "confidence_downgraded", "excluded"}
EQUAL_VALUE_GATES = {"not_recorded", "passed", "failed"}
PLACEHOLDER_TOKEN = "—"
AXIS_HEADINGS = (
    "Reduced Thrashing",
    "Better Branch Discipline",
    "Better Uncertainty Handling",
    "Lower Visible Burden At Equal Task Value",
    "Better Host-Specialized Realization",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def status(path: Path) -> str:
    match = re.search(r"^Status: (.+)$", read(path), re.MULTILINE)
    assert match, f"missing status line in {path}"
    return match.group(1).strip().strip("`")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing section: {heading}"
    return match.group("body").strip()


def subsection(text: str, heading: str) -> str:
    match = re.search(
        rf"^### {re.escape(heading)}\n\n(?P<body>.*?)(?=^### |^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing subsection: {heading}"
    return match.group("body").strip()


def _unwrap_code_literal(value: str) -> str:
    if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
        return value[1:-1]
    return value


def table_cells(line: str) -> list[str]:
    return [_unwrap_code_literal(cell.strip()) for cell in line.strip().strip("|").split("|")]


def parse_markdown_table(section_text: str) -> list[dict[str, str]]:
    table_lines: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            table_lines.append(stripped)
        elif table_lines:
            break

    assert len(table_lines) >= 2, f"missing markdown table in section:\n{section_text}"
    headers = table_cells(table_lines[0])
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        values = table_cells(row_line)
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def parse_bullet_fields(section_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        fields[key.strip()] = _unwrap_code_literal(value.strip())
    return fields


def field(body: str, field_name: str) -> str:
    match = re.search(
        rf"^- {re.escape(field_name)}: `([^`]+)`$",
        body,
        re.MULTILINE,
    )
    assert match, f"missing field {field_name}"
    return match.group(1)


def load_scenarios(layout: PackageLayout = DEFAULT_LAYOUT) -> dict[str, dict[str, str | int]]:
    text = read(layout.scenario_catalog_path)
    scenario_pattern = re.compile(
        r"^### `(scenario_[^`]+)`\n\n(?P<body>.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    scenarios: dict[str, dict[str, str | int]] = {}
    for match in scenario_pattern.finditer(text):
        scenario_id = match.group(1)
        body = match.group("body")
        scenarios[scenario_id] = {
            "scenario_family": field(body, "scenario_family"),
            "host_family": field(body, "host_family"),
            "task_value_rubric_id": field(body, "task_value_rubric_id"),
            "approval_or_environment_context_id": field(
                body, "approval_or_environment_context_id"
            ),
            "minimum_paired_run_count": int(field(body, "minimum_paired_run_count")),
        }
    assert scenarios, "no scenarios parsed from catalog"
    return scenarios


def load_failure_tags(layout: PackageLayout = DEFAULT_LAYOUT) -> set[str]:
    return set(re.findall(r"^### `([^`]+)`$", read(layout.failure_taxonomy_path), re.MULTILINE))


def tag_set(cell_text: str) -> set[str]:
    if cell_text == "none":
        return set()
    return {part.strip() for part in cell_text.split(",") if part.strip()}


def all_tags_allowed(cell_text: str, allowed_tags: set[str]) -> bool:
    return tag_set(cell_text) <= allowed_tags


def supporting_ids(cell_text: str) -> set[str]:
    if cell_text == "none":
        return set()
    return {part.strip() for part in cell_text.split(",") if part.strip()}


def real_pair_rows(layout: PackageLayout = DEFAULT_LAYOUT) -> list[dict[str, str]]:
    rows = parse_markdown_table(section(read(layout.paired_ledger_path), "Recorded Paired Runs"))
    real_rows: list[dict[str, str]] = []
    allowed_tags = load_failure_tags(layout)
    for row in rows:
        assert row["pair_status"] in PAIR_STATUSES
        assert all_tags_allowed(row["failure_tags"], allowed_tags)
        if row["paired_episode_set_id"] == "none_recorded_yet":
            continue
        real_rows.append(row)
    return real_rows


def aggregate_pair_counts(
    pair_rows: list[dict[str, str]]
) -> dict[tuple[str, str], dict[str, int | set[str]]]:
    counts: dict[tuple[str, str], dict[str, int | set[str]]] = defaultdict(
        lambda: {
            "usable": 0,
            "confidence_downgraded": 0,
            "excluded": 0,
            "supporting_ids": set(),
            "usable_ids": set(),
            "excluded_failure_tags": set(),
        }
    )
    for row in pair_rows:
        cell = (row["scenario_id"], row["host_family"])
        pair_status = row["pair_status"]
        pair_id = row["paired_episode_set_id"]
        tags = tag_set(row["failure_tags"])

        if pair_status == "usable":
            counts[cell]["usable"] += 1
            counts[cell]["supporting_ids"].add(pair_id)
            counts[cell]["usable_ids"].add(pair_id)
        elif pair_status == "confidence_downgraded":
            counts[cell]["confidence_downgraded"] += 1
            counts[cell]["supporting_ids"].add(pair_id)
        elif pair_status == "excluded":
            counts[cell]["excluded"] += 1
            counts[cell]["excluded_failure_tags"].update(tags)
        else:
            assert pair_status == "not_recorded"
    return counts


__all__ = [
    "AXIS_HEADINGS",
    "AXIS_TABLE_PATH",
    "BURDEN_TABLE_PATH",
    "DOCS_ROOT",
    "DEFAULT_LAYOUT",
    "EQUAL_VALUE_GATES",
    "EVALUATION_PLAN_PATH",
    "EVIDENCE_NOTE_PATH",
    "FAILURE_TAXONOMY_PATH",
    "HOST_SPLIT_TABLE_PATH",
    "MEDIATION_CLAUDE_PACKET_ROOT",
    "MEDIATION_GEMINI_PACKET_ROOT",
    "MEDIATION_OPENAI_PACKET_ROOT",
    "MEDIATION_REFERENCE_PACKET_ROOT",
    "PAIRED_LEDGER_PATH",
    "PAIR_STATUSES",
    "PLACEHOLDER_TOKEN",
    "PackageLayout",
    "REPO_ROOT",
    "SCENARIO_CATALOG_PATH",
    "VERDICTS",
    "aggregate_pair_counts",
    "all_tags_allowed",
    "build_layout",
    "field",
    "load_failure_tags",
    "load_scenarios",
    "parse_bullet_fields",
    "parse_markdown_table",
    "read",
    "real_pair_rows",
    "section",
    "status",
    "subsection",
    "supporting_ids",
    "table_cells",
    "tag_set",
]
