"""Mechanical checks for the mediation evidence package scaffold."""

from __future__ import annotations

import re

from tests._mediation_evidence import (
    AXIS_HEADINGS,
    AXIS_TABLE_PATH,
    BURDEN_TABLE_PATH,
    EQUAL_VALUE_GATES,
    EVALUATION_PLAN_PATH,
    EVIDENCE_NOTE_PATH,
    FAILURE_TAXONOMY_PATH,
    HOST_SPLIT_TABLE_PATH,
    PAIRED_LEDGER_PATH,
    PAIR_STATUSES,
    PLACEHOLDER_TOKEN,
    SCENARIO_CATALOG_PATH,
    VERDICTS,
    aggregate_pair_counts,
    all_tags_allowed,
    load_failure_tags,
    load_scenarios,
    parse_markdown_table,
    read,
    real_pair_rows,
    section,
    status,
    supporting_ids,
    tag_set,
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

    evaluation_plan = read(EVALUATION_PLAN_PATH)
    assert status(EVALUATION_PLAN_PATH) == "active comparative evidence plan for future mediation audit (`planning only`)"
    assert "docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md" in evaluation_plan
    assert "docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md" in evaluation_plan
    assert "tests/unit/test_mediation_evidence_package.py" in evaluation_plan
    assert "docs/CORTEX_V2_LOCAL_VERIFICATION.md" in evaluation_plan


def test_paired_run_ledger_is_preseeded_from_scenario_catalog() -> None:
    scenarios = load_scenarios()
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

    assert status(PAIRED_LEDGER_PATH) == "no_live_pairs_recorded"

    coverage_rows = parse_markdown_table(
        section(read(PAIRED_LEDGER_PATH), "Coverage Commitments")
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

    recorded_rows = parse_markdown_table(
        section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs")
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
    scenarios = load_scenarios()
    expected_cells = {(scenario_id, scenario["host_family"]) for scenario_id, scenario in scenarios.items()}
    allowed_hosts = {scenario["host_family"] for scenario in scenarios.values()}
    allowed_rubrics = {scenario["task_value_rubric_id"] for scenario in scenarios.values()}
    allowed_contexts = {scenario["approval_or_environment_context_id"] for scenario in scenarios.values()}
    allowed_failure_tags = load_failure_tags()
    pair_rows = real_pair_rows()
    for row in pair_rows:
        assert row["scenario_id"] in scenarios
        assert row["host_family"] in allowed_hosts
    pair_counts = aggregate_pair_counts(pair_rows)

    coverage_rows = parse_markdown_table(
        section(read(PAIRED_LEDGER_PATH), "Coverage Commitments")
    )
    assert {row["host_family"] for row in coverage_rows} <= allowed_hosts
    assert {row["task_value_rubric_id"] for row in coverage_rows} <= allowed_rubrics
    assert {row["approval_or_environment_context_id"] for row in coverage_rows} <= allowed_contexts

    axis_text = read(AXIS_TABLE_PATH)
    assert status(AXIS_TABLE_PATH) == "no_live_pairs_recorded"
    for heading in AXIS_HEADINGS:
        rows = parse_markdown_table(section(axis_text, heading))
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
            assert supporting_ids(row["supporting_paired_episode_sets"]) == counts["supporting_ids"]
            if {"scenario_mismatch", "host_mismatch", "boundary_drift"} & counts["excluded_failure_tags"]:
                assert row["current_verdict"] != "candidate_positive"

    burden_rows = parse_markdown_table(section(read(BURDEN_TABLE_PATH), "Comparison Table"))
    assert status(BURDEN_TABLE_PATH) == "no_live_pairs_recorded"
    assert {(row["scenario_id"], row["host_family"]) for row in burden_rows} == expected_cells
    for row in burden_rows:
        cell = (row["scenario_id"], row["host_family"])
        counts = pair_counts[cell]
        assert row["host_family"] in allowed_hosts
        assert row["equal_value_gate"] in EQUAL_VALUE_GATES
        assert row["current_verdict"] in VERDICTS
        assert int(row["usable_pair_count"]) == counts["usable"]
        assert supporting_ids(row["supporting_paired_episode_sets"]) == counts["usable_ids"]
        if row["current_verdict"] != "insufficient":
            assert counts["usable"] >= 3
        if row["current_verdict"] == "candidate_positive":
            assert row["equal_value_gate"] == "passed"

    host_split_text = read(HOST_SPLIT_TABLE_PATH)
    assert status(HOST_SPLIT_TABLE_PATH) == "no_live_pairs_recorded"
    assert "all-hosts" not in host_split_text.lower()
    host_sections = {
        "reference": parse_markdown_table(section(host_split_text, "Reference")),
        "gemini": parse_markdown_table(section(host_split_text, "Gemini")),
        "openai": parse_markdown_table(section(host_split_text, "OpenAI")),
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
            assert all_tags_allowed(row["host_flattening_tags"], allowed_failure_tags)
            assert supporting_ids(row["supporting_paired_episode_sets"]) == counts["usable_ids"]
            if row["current_verdict"] != "insufficient":
                assert counts["usable"] >= 3
            if "host_flattening" in tag_set(row["host_flattening_tags"]):
                assert row["current_verdict"] != "candidate_positive"


def test_evidence_note_keeps_mediation_blocked_without_live_runs() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert status(EVIDENCE_NOTE_PATH) == "reference_baseline_runs_recorded"
    assert "All current reference-host scenario families now have committed baseline run packets" in text
    assert "No live baseline-versus-mediated paired runs are currently recorded" in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
    assert "`scenario_thrash_reference_01` remains an explicit `artifact_gap`" not in text

    axis_statuses = dict(
        re.findall(r"^- ([^:]+): `([^`]+)`$", section(text, "Per-Axis Status"), re.MULTILINE)
    )
    assert axis_statuses == {
        "reduced thrashing": "insufficient",
        "better branch discipline": "insufficient",
        "better uncertainty handling": "insufficient",
        "lower visible burden at equal task value": "insufficient",
        "better host-specialized realization": "insufficient",
    }

    host_statuses = dict(
        re.findall(r"^- `([^`]+)`: `([^`]+)`$", section(text, "Per-Host Status"), re.MULTILINE)
    )
    assert host_statuses == {
        "reference": "baseline_only_runs_recorded",
        "gemini": "planned_only",
        "openai": "planned_only",
    }
