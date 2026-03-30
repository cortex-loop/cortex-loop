"""Mechanical checks for the reference host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    PAIRED_LEDGER_PATH,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    REFERENCE_HOST_REALIZATION_BASELINE_PACKET_PATHS,
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH,
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATHS,
    REFERENCE_HOST_REALIZATION_PACKET_PATH,
    REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_PATH,
    REFERENCE_MEDIATED_PACKET_EXAMPLE_DOC_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_reference_host_realization_admissibility_note_exists_and_records_audit() -> None:
    text = read(REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH.is_file()
    assert (
        status(REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)
        == "three lawful reference host realization comparator pairs recorded"
    )
    assert "tests/integration/_reference_lane_packet_example.py" in text
    assert "tests/integration/test_reference_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md" in text
    assert "tests/integration/_reference_mediated_lane_packet_example.py" in text
    assert "tests/integration/test_reference_mediated_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/mediation_evidence/reference/scenario_host_reference_01__experimental_mediated__run_001.md" in text
    assert "docs/mediation_evidence/reference/scenario_host_reference_01__experimental_mediated__run_002.md" in text
    assert "docs/mediation_evidence/reference/scenario_host_reference_01__experimental_mediated__run_003.md" in text
    assert "three lawful reference host-realization comparator pairs are now recorded" in text
    assert "direct host-native opportunity specialization at the selection layer" in text
    assert "contradiction-preserving" in text
    assert "truthful-withheld fields" in text


def test_reference_host_realization_admissibility_law_is_explicit() -> None:
    text = read(REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert "`scenario_id=scenario_host_reference_01`" in text
    assert "`host_family=reference`" in text
    assert "`task_value_rubric_id=task_value_equal_host_realization`" in text
    assert "`approval_or_environment_context_id=env_boundary_sensitive`" in text
    assert "same observe/bind meaning" in text
    assert "same commitment truth boundary" in text
    assert "same evaluation-packet publication surface" in text
    assert "same packet kind: `current-pair`" in text
    assert "same final certified completion class" in text
    assert "same contradiction/degradation preservation law" in text
    assert "same truthful-withheld meaning" in text
    assert "same selected family: `seek-context`" in text
    assert "same host-opportunity set containing `mcp.query`" in text
    assert "changing observe/bind semantics" in text
    assert "dropping truthful-withheld fields" in text
    assert "changing `current-pair` packet semantics" in text
    assert "using latency-only improvement or smaller artifact shape alone" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "three lawful reference host-realization comparator pairs are recorded" in text
    assert (
        "`scenario_host_reference_01` / `reference` now has `candidate_positive` "
        "cell-level signal for better host-specialized realization"
    ) in text
    assert "Mediation implementation remains blocked pending J3 justification review" not in text


def test_reference_host_realization_anchor_is_rebound_to_a_recorded_pair() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_reference_01")

    assert host_row["run_id"] == "reference_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pair_reference_host_001"
    assert host_row["evidence_status"] == "baseline_packet_committed"
    assert host_row["packet_path"] == (
        "docs/mediation_evidence/reference/"
        "scenario_host_reference_01__baseline_non_mediated__run_001.md"
    )
    assert (
        host_row["basis_surface"]
        == "tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc"
    )
    assert "CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md" in host_row["notes"]
    assert "CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0.md" in host_row["notes"]
    assert REFERENCE_MEDIATED_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert REFERENCE_HOST_REALIZATION_PACKET_PATH.is_file()
    assert REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH.is_file()
    assert REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_PATH.is_file()
    assert set(path.name for path in REFERENCE_HOST_REALIZATION_BASELINE_PACKET_PATHS.values()) == {
        "scenario_host_reference_01__baseline_non_mediated__run_001.md",
        "scenario_host_reference_01__baseline_non_mediated__run_002.md",
        "scenario_host_reference_01__baseline_non_mediated__run_003.md",
    }
    assert set(path.name for path in REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATHS.values()) == {
        "scenario_host_reference_01__experimental_mediated__run_001.md",
        "scenario_host_reference_01__experimental_mediated__run_002.md",
        "scenario_host_reference_01__experimental_mediated__run_003.md",
    }

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    recorded_host_rows = [
        row for row in recorded_rows if row["scenario_id"] == "scenario_host_reference_01"
    ]
    assert [row["paired_episode_set_id"] for row in recorded_host_rows] == [
        "pair_reference_host_001",
        "pair_reference_host_002",
        "pair_reference_host_003",
    ]
    assert {row["pair_status"] for row in recorded_host_rows} == {"usable"}
    assert {row["failure_tags"] for row in recorded_host_rows} == {"none"}


def test_evidence_note_records_three_reference_host_pairs_and_supports_j3_decision() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "Three reference-only mediation-specific host-realization pairs are now "
        "recorded for `scenario_host_reference_01`."
    ) in text
    assert (
        "`scenario_host_reference_01` / `reference` now has `candidate_positive` "
        "signal for better host-specialized realization"
    ) in text
    assert "Reference, Gemini, OpenAI, and Claude now carry the host-realization `candidate_positive` cells." in text
    assert "The accepted J3 decision is that mediation is now justified for one bounded experimental seam." in text
    assert "This evidence package is not a second truth court and does not by itself authorize implementation." in text
