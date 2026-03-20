"""Mechanical checks for the mediation evidence package scaffold."""

from __future__ import annotations

from collections import defaultdict
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = REPO_ROOT / "docs"

SCENARIO_CATALOG_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md"
EVALUATION_PLAN_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md"
FAILURE_TAXONOMY_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0.md"
PAIRED_LEDGER_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md"
AXIS_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md"
BURDEN_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md"
HOST_SPLIT_TABLE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md"
EVIDENCE_NOTE_PATH = DOCS_ROOT / "CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md"

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
EVIDENCE_DOCS = (
    SCENARIO_CATALOG_PATH,
    PAIRED_LEDGER_PATH,
    AXIS_TABLE_PATH,
    BURDEN_TABLE_PATH,
    HOST_SPLIT_TABLE_PATH,
    EVIDENCE_NOTE_PATH,
)


def test_mediation_evidence_docs_exist_and_are_linked_from_plan() -> None:
    for path in EVIDENCE_DOCS:
        assert path.is_file(), f"missing mediation evidence doc: {path}"

    evaluation_plan = _read(EVALUATION_PLAN_PATH)
    assert _status(EVALUATION_PLAN_PATH) == "active comparative evidence plan for future mediation audit (`planning only`)"
    assert "docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md" in evaluation_plan
    assert "tests/unit/test_mediation_evidence_package.py" in evaluation_plan
    assert "docs/CORTEX_V2_LOCAL_VERIFICATION.md" in evaluation_plan


def test_paired_run_ledger_is_preseeded_from_scenario_catalog() -> None:
    scenarios = _load_scenarios()
    expected_cells = {
        (
            scenario_id,
            scenario["host_family"],
            scenario["scenario_family"],
            scenario["task_value_rubric_id"],
            scenario["approval_or_environment_context_id"],
            str(scenario["minimum_paired_run_count"]),
        )
        for scenario_id, scenario in scenarios.items()
    }

    assert _status(PAIRED_LEDGER_PATH) == "no_live_pairs_recorded"

    coverage_rows = _parse_markdown_table(
        _section(_read(PAIRED_LEDGER_PATH), "Coverage Commitments")
    )
    observed_cells = {
        (
            row["scenario_id"],
            row["host_family"],
            row["scenario_family"],
            row["task_value_rubric_id"],
            row["approval_or_environment_context_id"],
            row["minimum_paired_run_count"],
        )
        for row in coverage_rows
    }
    assert observed_cells == expected_cells
    assert {row["coverage_status"] for row in coverage_rows} == {"planned"}

    recorded_rows = _parse_markdown_table(
        _section(_read(PAIRED_LEDGER_PATH), "Recorded Paired Runs")
    )
    placeholder_rows = [row for row in recorded_rows if row["paired_episode_set_id"] == "none_recorded_yet"]
    assert len(placeholder_rows) == 1
    placeholder_row = placeholder_rows[0]
    assert placeholder_row["pair_status"] == "not_recorded"
    assert placeholder_row["failure_tags"] == "none"
    assert all(
        placeholder_row[field] == PLACEHOLDER_TOKEN
        for field in (
            "scenario_id",
            "host_family",
            "baseline_run_id",
            "mediated_run_id",
            "baseline_packet_ref",
            "mediated_packet_ref",
        )
    )


def test_results_surfaces_are_preseeded_for_all_catalog_cells_and_follow_fairness_rules() -> None:
    scenarios = _load_scenarios()
    expected_cells = {(scenario_id, scenario["host_family"]) for scenario_id, scenario in scenarios.items()}
    allowed_hosts = {scenario["host_family"] for scenario in scenarios.values()}
    allowed_rubrics = {scenario["task_value_rubric_id"] for scenario in scenarios.values()}
    allowed_contexts = {scenario["approval_or_environment_context_id"] for scenario in scenarios.values()}
    allowed_failure_tags = _load_failure_tags()
    pair_rows = _real_pair_rows()
    for row in pair_rows:
        assert row["scenario_id"] in scenarios
        assert row["host_family"] in allowed_hosts
    pair_counts = _aggregate_pair_counts(pair_rows)

    coverage_rows = _parse_markdown_table(
        _section(_read(PAIRED_LEDGER_PATH), "Coverage Commitments")
    )
    assert {row["host_family"] for row in coverage_rows} <= allowed_hosts
    assert {row["task_value_rubric_id"] for row in coverage_rows} <= allowed_rubrics
    assert {row["approval_or_environment_context_id"] for row in coverage_rows} <= allowed_contexts

    axis_text = _read(AXIS_TABLE_PATH)
    assert _status(AXIS_TABLE_PATH) == "no_live_pairs_recorded"
    for heading in AXIS_HEADINGS:
        rows = _parse_markdown_table(_section(axis_text, heading))
        assert {(row["scenario_id"], row["host_family"]) for row in rows} == expected_cells
        for row in rows:
            cell = (row["scenario_id"], row["host_family"])
            counts = pair_counts[cell]
            assert row["host_family"] in allowed_hosts
            assert int(row["usable_pair_count"]) == counts["usable"]
            assert int(row["confidence_downgraded_pair_count"]) == counts["confidence_downgraded"]
            assert int(row["excluded_pair_count"]) == counts["excluded"]
            assert row["current_verdict"] in VERDICTS
            counted_pairs = counts["usable"] + counts["confidence_downgraded"]
            if row["current_verdict"] != "insufficient":
                assert counted_pairs >= 3
            if counts["excluded"] == 0:
                assert int(row["excluded_pair_count"]) == 0
            assert _supporting_ids(row["supporting_paired_episode_sets"]) == counts["supporting_ids"]
            if {"scenario_mismatch", "host_mismatch", "boundary_drift"} & counts["excluded_failure_tags"]:
                assert row["current_verdict"] != "candidate_positive"

    burden_rows = _parse_markdown_table(_section(_read(BURDEN_TABLE_PATH), "Comparison Table"))
    assert _status(BURDEN_TABLE_PATH) == "no_live_pairs_recorded"
    assert {(row["scenario_id"], row["host_family"]) for row in burden_rows} == expected_cells
    for row in burden_rows:
        cell = (row["scenario_id"], row["host_family"])
        counts = pair_counts[cell]
        assert row["host_family"] in allowed_hosts
        assert row["equal_value_gate"] in EQUAL_VALUE_GATES
        assert row["current_verdict"] in VERDICTS
        assert int(row["usable_pair_count"]) == counts["usable"]
        assert _supporting_ids(row["supporting_paired_episode_sets"]) == counts["usable_ids"]
        if row["current_verdict"] != "insufficient":
            assert counts["usable"] >= 3
        if row["current_verdict"] == "candidate_positive":
            assert row["equal_value_gate"] == "passed"

    host_split_text = _read(HOST_SPLIT_TABLE_PATH)
    assert _status(HOST_SPLIT_TABLE_PATH) == "no_live_pairs_recorded"
    assert "all-hosts" not in host_split_text.lower()
    host_sections = {
        "reference": _parse_markdown_table(_section(host_split_text, "Reference")),
        "gemini": _parse_markdown_table(_section(host_split_text, "Gemini")),
        "openai": _parse_markdown_table(_section(host_split_text, "OpenAI")),
    }
    observed_host_cells = {
        (row["scenario_id"], host_family)
        for host_family, rows in host_sections.items()
        for row in rows
    }
    assert observed_host_cells == expected_cells
    for host_family, rows in host_sections.items():
        for row in rows:
            scenario = scenarios[row["scenario_id"]]
            counts = pair_counts[(row["scenario_id"], host_family)]
            assert scenario["host_family"] == host_family
            assert int(row["usable_pair_count"]) == counts["usable"]
            assert row["current_verdict"] in VERDICTS
            assert _all_tags_allowed(row["host_flattening_tags"], allowed_failure_tags)
            assert _supporting_ids(row["supporting_paired_episode_sets"]) == counts["usable_ids"]
            if row["current_verdict"] != "insufficient":
                assert counts["usable"] >= 3
            if "host_flattening" in _tag_set(row["host_flattening_tags"]):
                assert row["current_verdict"] != "candidate_positive"


def test_evidence_note_keeps_mediation_blocked_without_live_runs() -> None:
    text = _read(EVIDENCE_NOTE_PATH)

    assert _status(EVIDENCE_NOTE_PATH) == "no_live_runs_recorded"
    assert "No live baseline-versus-mediated paired runs are currently recorded" in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text

    axis_statuses = dict(
        re.findall(r"^- ([^:]+): `([^`]+)`$", _section(text, "Per-Axis Status"), re.MULTILINE)
    )
    assert axis_statuses == {
        "reduced thrashing": "insufficient",
        "better branch discipline": "insufficient",
        "better uncertainty handling": "insufficient",
        "lower visible burden at equal task value": "insufficient",
        "better host-specialized realization": "insufficient",
    }

    host_statuses = dict(
        re.findall(r"^- `([^`]+)`: `([^`]+)`$", _section(text, "Per-Host Status"), re.MULTILINE)
    )
    assert host_statuses == {
        "reference": "no_live_pairs_recorded",
        "gemini": "no_live_pairs_recorded",
        "openai": "no_live_pairs_recorded",
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _status(path: Path) -> str:
    match = re.search(r"^Status: (.+)$", _read(path), re.MULTILINE)
    assert match, f"missing status line in {path}"
    return match.group(1).strip().strip("`")


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\n\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing section: {heading}"
    return match.group("body").strip()


def _parse_markdown_table(section_text: str) -> list[dict[str, str]]:
    table_lines: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            table_lines.append(stripped)
        elif table_lines:
            break

    assert len(table_lines) >= 2, f"missing markdown table in section:\n{section_text}"
    headers = _table_cells(table_lines[0])
    rows: list[dict[str, str]] = []
    for row_line in table_lines[2:]:
        values = _table_cells(row_line)
        rows.append(dict(zip(headers, values, strict=True)))
    return rows


def _table_cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def _load_scenarios() -> dict[str, dict[str, str | int]]:
    text = _read(SCENARIO_CATALOG_PATH)
    scenario_pattern = re.compile(
        r"^### `(scenario_[^`]+)`\n\n(?P<body>.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    scenarios: dict[str, dict[str, str | int]] = {}
    for match in scenario_pattern.finditer(text):
        scenario_id = match.group(1)
        body = match.group("body")
        scenarios[scenario_id] = {
            "scenario_family": _field(body, "scenario_family"),
            "host_family": _field(body, "host_family"),
            "task_value_rubric_id": _field(body, "task_value_rubric_id"),
            "approval_or_environment_context_id": _field(
                body, "approval_or_environment_context_id"
            ),
            "minimum_paired_run_count": int(_field(body, "minimum_paired_run_count")),
        }
    assert scenarios, "no scenarios parsed from catalog"
    return scenarios


def _field(body: str, field_name: str) -> str:
    match = re.search(
        rf"^- {re.escape(field_name)}: `([^`]+)`$",
        body,
        re.MULTILINE,
    )
    assert match, f"missing field {field_name}"
    return match.group(1)


def _load_failure_tags() -> set[str]:
    return set(re.findall(r"^### `([^`]+)`$", _read(FAILURE_TAXONOMY_PATH), re.MULTILINE))


def _real_pair_rows() -> list[dict[str, str]]:
    rows = _parse_markdown_table(_section(_read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    real_rows: list[dict[str, str]] = []
    for row in rows:
        assert row["pair_status"] in PAIR_STATUSES
        assert _all_tags_allowed(row["failure_tags"], _load_failure_tags())
        if row["paired_episode_set_id"] == "none_recorded_yet":
            continue
        real_rows.append(row)
    return real_rows


def _aggregate_pair_counts(
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
        tags = _tag_set(row["failure_tags"])

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


def _supporting_ids(cell_text: str) -> set[str]:
    if cell_text == "none":
        return set()
    return {part.strip() for part in cell_text.split(",") if part.strip()}


def _tag_set(cell_text: str) -> set[str]:
    if cell_text == "none":
        return set()
    return {part.strip() for part in cell_text.split(",") if part.strip()}


def _all_tags_allowed(cell_text: str, allowed_tags: set[str]) -> bool:
    return _tag_set(cell_text) <= allowed_tags
