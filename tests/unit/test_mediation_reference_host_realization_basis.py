"""Mechanical checks for the reference host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    PAIRED_LEDGER_PATH,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH,
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
        == "one lawful reference host realization comparator pair recorded"
    )
    assert "tests/integration/_reference_lane_packet_example.py" in text
    assert "tests/integration/test_reference_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md" in text
    assert "tests/integration/_reference_mediated_lane_packet_example.py" in text
    assert "tests/integration/test_reference_mediated_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/mediation_evidence/reference/scenario_host_reference_01__experimental_mediated__run_001.md" in text
    assert "one lawful reference host-realization comparator pair is now recorded" in text
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
    assert "one lawful reference host-realization comparator pair is recorded" in text
    assert "still remains `insufficient` because one pair is below the three-pair minimum" in text


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

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    recorded_host_row = next(
        row for row in recorded_rows if row["scenario_id"] == "scenario_host_reference_01"
    )
    assert recorded_host_row["paired_episode_set_id"] == "pair_reference_host_001"
    assert recorded_host_row["pair_status"] == "usable"
    assert recorded_host_row["failure_tags"] == "none"


def test_evidence_note_records_one_reference_host_pair_and_keeps_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "One reference-only mediation-specific host-realization pair is now recorded for "
        "`scenario_host_reference_01`, but the cell remains `insufficient` because one "
        "pair is below the three-pair minimum."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
