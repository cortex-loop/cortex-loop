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

    assert status(PAIRED_LEDGER_PATH) == "reference_thrash_and_uncertainty_three_pairs_recorded"

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
    real_rows = [row for row in recorded_rows if row["paired_episode_set_id"] != "none_recorded_yet"]
    assert real_rows == [
        {
            "paired_episode_set_id": "pair_reference_thrash_001",
            "scenario_id": "scenario_thrash_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_thrash_baseline_run_001",
            "mediated_run_id": "reference_thrash_mediated_run_001",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__baseline_non_mediated__run_001.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__experimental_mediated__run_001.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "First reference-only experimental thrash pair. The same scenario, host, "
                "rubric, environment context, commitment boundary, and evidence surface "
                "are preserved."
            ),
        },
        {
            "paired_episode_set_id": "pair_reference_thrash_002",
            "scenario_id": "scenario_thrash_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_thrash_baseline_run_002",
            "mediated_run_id": "reference_thrash_mediated_run_002",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__baseline_non_mediated__run_002.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__experimental_mediated__run_002.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "Second reference-only experimental thrash pair. The same scenario, host, "
                "rubric, environment context, commitment boundary, and evidence surface "
                "are preserved."
            ),
        },
        {
            "paired_episode_set_id": "pair_reference_thrash_003",
            "scenario_id": "scenario_thrash_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_thrash_baseline_run_003",
            "mediated_run_id": "reference_thrash_mediated_run_003",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__baseline_non_mediated__run_003.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_thrash_reference_01__experimental_mediated__run_003.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "Third reference-only experimental thrash pair. The same scenario, host, "
                "rubric, environment context, commitment boundary, and evidence surface "
                "are preserved."
            ),
        },
        {
            "paired_episode_set_id": "pair_reference_uncertainty_001",
            "scenario_id": "scenario_uncertainty_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_uncertainty_baseline_run_001",
            "mediated_run_id": "reference_uncertainty_mediated_run_001",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__experimental_mediated__run_001.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "First reference-only experimental uncertainty pair. The same scenario, "
                "host, rubric, environment context, commitment boundary, contradiction/"
                "degradation law, and evidence surface are preserved."
            ),
        },
        {
            "paired_episode_set_id": "pair_reference_uncertainty_002",
            "scenario_id": "scenario_uncertainty_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_uncertainty_baseline_run_002",
            "mediated_run_id": "reference_uncertainty_mediated_run_002",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__baseline_non_mediated__run_002.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__experimental_mediated__run_002.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "Second reference-only experimental uncertainty pair. The same scenario, "
                "host, rubric, environment context, commitment boundary, contradiction/"
                "degradation law, and evidence surface are preserved."
            ),
        },
        {
            "paired_episode_set_id": "pair_reference_uncertainty_003",
            "scenario_id": "scenario_uncertainty_reference_01",
            "host_family": "reference",
            "baseline_run_id": "reference_uncertainty_baseline_run_003",
            "mediated_run_id": "reference_uncertainty_mediated_run_003",
            "baseline_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__baseline_non_mediated__run_003.md"
            ),
            "mediated_packet_ref": (
                "docs/mediation_evidence/reference/"
                "scenario_uncertainty_reference_01__experimental_mediated__run_003.md"
            ),
            "pair_status": "usable",
            "failure_tags": "none",
            "notes": (
                "Third reference-only experimental uncertainty pair. The same scenario, "
                "host, rubric, environment context, commitment boundary, contradiction/"
                "degradation law, and evidence surface are preserved."
            ),
        },
    ]
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
    host_realization_cell = ("scenario_host_reference_01", "reference")
    assert pair_counts[host_realization_cell]["usable"] == 0
    assert pair_counts[host_realization_cell]["confidence_downgraded"] == 0
    assert pair_counts[host_realization_cell]["excluded"] == 0
    gemini_uncertainty_cell = ("scenario_uncertainty_gemini_01", "gemini")
    assert pair_counts[gemini_uncertainty_cell]["usable"] == 0
    assert pair_counts[gemini_uncertainty_cell]["confidence_downgraded"] == 0
    assert pair_counts[gemini_uncertainty_cell]["excluded"] == 0

    coverage_rows = parse_markdown_table(
        section(read(PAIRED_LEDGER_PATH), "Coverage Commitments")
    )
    assert {row["host_family"] for row in coverage_rows} <= allowed_hosts
    assert {row["task_value_rubric_id"] for row in coverage_rows} <= allowed_rubrics
    assert {row["approval_or_environment_context_id"] for row in coverage_rows} <= allowed_contexts

    axis_text = read(AXIS_TABLE_PATH)
    assert status(AXIS_TABLE_PATH) == "reference_thrash_and_uncertainty_three_pairs_recorded"
    expected_positive = {
        ("Reduced Thrashing", ("scenario_thrash_reference_01", "reference")),
        ("Better Branch Discipline", ("scenario_thrash_reference_01", "reference")),
        ("Better Uncertainty Handling", ("scenario_uncertainty_reference_01", "reference")),
    }
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
                assert (heading, cell) in expected_positive
            elif (heading, cell) in expected_positive:
                raise AssertionError(f"missing candidate_positive verdict for {heading} {cell}")
            if counts["excluded"] == 0:
                assert int(row["excluded_pair_count"]) == 0
            assert supporting_ids(row["supporting_paired_episode_sets"]) == counts["supporting_ids"]
            if {"scenario_mismatch", "host_mismatch", "boundary_drift"} & counts["excluded_failure_tags"]:
                assert row["current_verdict"] != "candidate_positive"
            if cell == host_realization_cell:
                assert row["current_verdict"] == "insufficient"
                assert supporting_ids(row["supporting_paired_episode_sets"]) == set()
            if cell == gemini_uncertainty_cell:
                assert row["current_verdict"] == "insufficient"
                assert supporting_ids(row["supporting_paired_episode_sets"]) == set()

    burden_rows = parse_markdown_table(section(read(BURDEN_TABLE_PATH), "Comparison Table"))
    assert status(BURDEN_TABLE_PATH) == "reference_thrash_and_uncertainty_three_pairs_recorded"
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
    assert status(HOST_SPLIT_TABLE_PATH) == "reference_thrash_and_uncertainty_three_pairs_recorded"
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


def test_evidence_note_keeps_mediation_blocked_with_reference_series_and_gemini_anchor() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert status(EVIDENCE_NOTE_PATH) == "reference_series_and_gemini_baseline_anchor_recorded"
    assert "All current reference-host scenario families now have committed baseline run packets" in text
    assert (
        "A committed Gemini uncertainty baseline anchor is now recorded in "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_BASELINE_INDEX_0.md` and backed by "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md`."
    ) in text
    assert "Three experimental reference-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert "Three experimental reference-only uncertainty pairs are now recorded" in text
    assert (
        "`scenario_host_reference_01` remains intentionally unpaired pending the comparator "
        "admissibility audit recorded in "
        "`docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`."
    ) in text
    assert (
        "`scenario_thrash_reference_01` / `reference` now has `candidate_positive` "
        "cell-level signal for reduced thrashing and better branch discipline" in text
    )
    assert (
        "`scenario_uncertainty_reference_01` / `reference` now has "
        "`candidate_positive` cell-level signal for better uncertainty handling" in text
    )
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
        "reference": "baseline_and_two_paired_series_recorded",
        "gemini": "baseline_anchor_recorded",
        "openai": "planned_only",
    }
