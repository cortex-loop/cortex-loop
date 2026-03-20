"""Shared parsing helpers for mediation evidence docs and run packets."""

from __future__ import annotations

from collections import defaultdict
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "docs"
MEDIATION_REFERENCE_PACKET_ROOT = DOCS_ROOT / "mediation_evidence" / "reference"

SCENARIO_CATALOG_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md"
EVALUATION_PLAN_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md"
FAILURE_TAXONOMY_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0.md"
PAIRED_LEDGER_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md"
AXIS_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md"
BURDEN_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md"
HOST_SPLIT_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md"
EVIDENCE_NOTE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md"
REFERENCE_BASELINE_INDEX_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_BASELINE_INDEX_0.md"

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
RUN_PACKET_INVARIANT_FIELDS = (
    "same_host_family_preserved",
    "same_starting_task_framing_preserved",
    "same_core_commitment_boundary_preserved",
    "same_evidence_or_publication_surface_preserved",
    "same_success_rubric_preserved",
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


def table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def parse_bullet_fields(section_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        fields[key.strip()] = value.strip().strip("`")
    return fields


def load_scenarios() -> dict[str, dict[str, str | int]]:
    text = read(SCENARIO_CATALOG_PATH)
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


def field(body: str, field_name: str) -> str:
    match = re.search(
        rf"^- {re.escape(field_name)}: `([^`]+)`$",
        body,
        re.MULTILINE,
    )
    assert match, f"missing field {field_name}"
    return match.group(1)


def load_failure_tags() -> set[str]:
    return set(re.findall(r"^### `([^`]+)`$", read(FAILURE_TAXONOMY_PATH), re.MULTILINE))


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


def real_pair_rows() -> list[dict[str, str]]:
    rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    real_rows: list[dict[str, str]] = []
    for row in rows:
        assert row["pair_status"] in PAIR_STATUSES
        assert all_tags_allowed(row["failure_tags"], load_failure_tags())
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


def parse_run_packet(path: Path) -> dict[str, object]:
    text = read(path)
    lift_axis_text = section(text, "Lift-Axis Observations")
    return {
        "path": path,
        "status": status(path),
        "header": parse_bullet_fields(section(text, "Header")),
        "variant_metadata": parse_bullet_fields(section(text, "Variant Metadata")),
        "invariant_lock": parse_bullet_fields(section(text, "Invariant Lock")),
        "scenario_inputs": parse_bullet_fields(section(text, "Scenario Inputs")),
        "run_outputs": parse_bullet_fields(section(text, "Run Outputs")),
        "artifact_refs": parse_bullet_fields(section(text, "Artifact Refs")),
        "lift_axes": {
            heading: parse_bullet_fields(subsection(lift_axis_text, heading))
            for heading in AXIS_HEADINGS
        },
        "exclusions": parse_bullet_fields(section(text, "Exclusions Or Unusable-Pair Notes")),
        "reviewer_note": parse_bullet_fields(section(text, "Reviewer Note")),
    }
