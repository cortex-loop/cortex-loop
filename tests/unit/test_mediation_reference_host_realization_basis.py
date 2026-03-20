"""Mechanical checks for the reference host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    PAIRED_LEDGER_PATH,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    REFERENCE_HOST_REALIZATION_PACKET_PATH,
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
        == "host realization comparator not yet admissible"
    )
    assert "tests/integration/_reference_lane_packet_example.py" in text
    assert "tests/integration/test_reference_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md" in text
    assert "current host baseline is already a strong host-native reference surface" in text
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
    assert "changing observe/bind semantics" in text
    assert "dropping truthful-withheld fields" in text
    assert "changing `current-pair` packet semantics" in text
    assert "using latency-only improvement or smaller artifact shape alone" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "No admissible mediated comparator is recorded yet" in text


def test_reference_host_realization_anchor_remains_pending_and_unpaired() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_reference_01")

    assert host_row["run_id"] == "reference_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pending_pair_reference_host_001"
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
    assert REFERENCE_HOST_REALIZATION_PACKET_PATH.is_file()

    mediated_host_packet = (
        REFERENCE_HOST_REALIZATION_PACKET_PATH.parent
        / "scenario_host_reference_01__experimental_mediated__run_001.md"
    )
    assert not mediated_host_packet.exists()

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    assert not any(row["scenario_id"] == "scenario_host_reference_01" for row in recorded_rows)


def test_evidence_note_keeps_host_realization_unpaired_and_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "`scenario_host_reference_01` remains intentionally unpaired pending the comparator "
        "admissibility audit recorded in `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
