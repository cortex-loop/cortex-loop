"""Mechanical checks for committed mediation reference baseline run packets."""

from __future__ import annotations

from pathlib import Path

from tests.unit._mediation_evidence import (
    MEDIATION_REFERENCE_PACKET_ROOT,
    REFERENCE_BASELINE_INDEX_PATH,
    RUN_PACKET_INVARIANT_FIELDS,
    VERDICTS,
    all_tags_allowed,
    load_failure_tags,
    load_scenarios,
    parse_markdown_table,
    parse_run_packet,
    read,
    section,
    status,
)


def test_reference_baseline_index_is_reference_only_and_explicit_about_gaps() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))

    assert REFERENCE_BASELINE_INDEX_PATH.is_file()
    assert status(REFERENCE_BASELINE_INDEX_PATH) == "reference mediation baseline run index (`active`, baseline-only)"
    assert len(rows) == 3
    assert {row["scenario_id"] for row in rows} == {
        "scenario_uncertainty_reference_01",
        "scenario_host_reference_01",
        "scenario_thrash_reference_01",
    }

    for row in rows:
        assert row["host_family"] == "reference"
        assert row["variant"] == "baseline_non_mediated"
        assert row["scenario_id"] in scenarios
        assert scenarios[row["scenario_id"]]["host_family"] == "reference"
        assert all_tags_allowed(row["failure_tags"], failure_tags)

        if row["evidence_status"] == "baseline_packet_committed":
            packet_path = Path(row["packet_path"])
            assert packet_path.parts[:3] == ("docs", "mediation_evidence", "reference")
            assert (REFERENCE_BASELINE_INDEX_PATH.parents[1] / packet_path).is_file()
            assert row["failure_tags"] == "none"
        else:
            assert row["evidence_status"] == "artifact_gap"
            assert row["scenario_id"] == "scenario_thrash_reference_01"
            assert row["packet_path"] == "none"
            assert row["failure_tags"] == "artifact_gap"


def test_committed_reference_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    committed_rows = [row for row in rows if row["evidence_status"] == "baseline_packet_committed"]

    assert len(committed_rows) == 2
    assert not any(
        row["scenario_id"] == "scenario_thrash_reference_01" and row["evidence_status"] == "baseline_packet_committed"
        for row in rows
    )

    for row in committed_rows:
        packet_path = REFERENCE_BASELINE_INDEX_PATH.parents[1] / row["packet_path"]
        packet = parse_run_packet(packet_path)
        scenario = scenarios[row["scenario_id"]]

        assert packet["status"] == "reviewed_evidence"
        assert packet["header"]["scenario_id"] == row["scenario_id"]
        assert packet["header"]["run_id"] == row["run_id"]
        assert packet["header"]["paired_episode_set_id"] == row["paired_episode_set_id"]
        assert packet["variant_metadata"]["variant"] == "baseline_non_mediated"
        assert packet["variant_metadata"]["host_family"] == "reference"
        assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
        assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
        assert (
            packet["variant_metadata"]["approval_or_environment_context_id"]
            == scenario["approval_or_environment_context_id"]
        )

        for field_name in RUN_PACKET_INVARIANT_FIELDS:
            assert packet["invariant_lock"][field_name] == "yes"

        for axis_payload in packet["lift_axes"].values():
            assert axis_payload["verdict"] in VERDICTS
            assert axis_payload["verdict"] == "insufficient"

        assert packet["exclusions"]["exclusion_status"] == "none"
        assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
        assert packet["exclusions"]["failure_tags"] == "none"
        reviewer_note = packet["reviewer_note"]["reviewer_note"]
        assert "baseline-only committed evidence" in reviewer_note
        assert "not comparative mediation evidence" in reviewer_note
        assert "does not justify mediation" in reviewer_note


def test_reference_packet_directory_contains_only_the_two_committed_packets() -> None:
    packet_names = sorted(path.name for path in MEDIATION_REFERENCE_PACKET_ROOT.glob("*.md"))
    assert packet_names == [
        "scenario_host_reference_01__baseline_non_mediated__run_001.md",
        "scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md",
    ]
