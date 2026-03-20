"""Mechanical checks for the Gemini host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATH,
    GEMINI_HOST_REALIZATION_PACKET_PATH,
    GEMINI_HOST_REALIZATION_REPLICATION_NOTE_PATH,
    GEMINI_MEDIATED_PACKET_EXAMPLE_DOC_PATH,
    GEMINI_PACKET_EXAMPLE_DOC_PATH,
    MEDIATION_GEMINI_PACKET_ROOT,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_gemini_host_realization_admissibility_note_exists_and_records_audit() -> None:
    text = read(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH.is_file()
    assert (
        status(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)
        == "one lawful gemini host realization comparator pair recorded"
    )
    assert "tests/unit/test_gemini_host.py" in text
    assert "tests/unit/test_gemini_host_commitment.py" in text
    assert "tests/unit/test_gemini_host_neutral.py" in text
    assert "tests/integration/_gemini_lane_packet_example.py" in text
    assert "tests/integration/test_gemini_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0.md" in text
    assert "tests/integration/_gemini_mediated_lane_packet_example.py" in text
    assert "tests/integration/test_gemini_mediated_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_GEMINI_MEDIATED_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/mediation_evidence/gemini/scenario_host_gemini_01__baseline_non_mediated__run_001.md" in text
    assert "docs/mediation_evidence/gemini/scenario_host_gemini_01__experimental_mediated__run_001.md" in text
    assert "one lawful Gemini host-realization comparator pair is recorded" in text
    assert "direct host-native opportunity specialization at the selection layer" in text
    assert "Gemini-only" in text


def test_gemini_host_realization_admissibility_law_is_explicit() -> None:
    text = read(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert "`scenario_id=scenario_host_gemini_01`" in text
    assert "`host_family=gemini`" in text
    assert "`task_value_rubric_id=task_value_equal_host_realization`" in text
    assert "`approval_or_environment_context_id=env_boundary_sensitive`" in text
    assert "same Gemini observe/bind meaning" in text
    assert "same commitment truth boundary" in text
    assert "same evaluation-packet publication surface" in text
    assert "same packet kind: `current-pair`" in text
    assert "same final certified completion class" in text
    assert "same contradiction/degradation preservation law" in text
    assert "same truthful-withheld meaning" in text
    assert "same selected family: `seek-context`" in text
    assert "same host-opportunity set containing `mcp.query`" in text
    assert "claiming host lift from thrash or uncertainty packets" in text
    assert "dropping truthful-withheld fields" in text
    assert "changing `current-pair` packet semantics" in text
    assert "using latency-only improvement, shorter artifacts, or cosmetic simplification as host-realization evidence" in text
    assert "changing Gemini host semantics to make mediation look better" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "one lawful Gemini host-realization comparator pair is recorded" in text
    assert (
        "`scenario_host_gemini_01` / `gemini` still remains `insufficient` because "
        "one pair is below the three-pair minimum"
    ) in text


def test_gemini_host_realization_anchor_is_rebound_to_a_recorded_pair() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))

    assert {row["scenario_id"] for row in rows} == {
        "scenario_host_gemini_01",
        "scenario_thrash_gemini_01",
        "scenario_uncertainty_gemini_01",
    }
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_gemini_01")
    assert host_row["run_id"] == "gemini_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pair_gemini_host_001"
    assert host_row["evidence_status"] == "baseline_packet_committed"
    assert host_row["packet_path"] == (
        "docs/mediation_evidence/gemini/"
        "scenario_host_gemini_01__baseline_non_mediated__run_001.md"
    )
    assert (
        host_row["basis_surface"]
        == "tests/integration/test_gemini_lane_packet_example.py::test_gemini_lane_current_pair_packet_example_matches_committed_doc"
    )
    assert "CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md" in host_row["notes"]
    assert "CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_REPLICATION_NOTE_0.md" in host_row["notes"]
    assert GEMINI_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert GEMINI_MEDIATED_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert GEMINI_HOST_REALIZATION_PACKET_PATH.is_file()
    assert GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATH.is_file()
    assert GEMINI_HOST_REALIZATION_REPLICATION_NOTE_PATH.is_file()

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    recorded_host_rows = [
        row for row in recorded_rows if row["scenario_id"] == "scenario_host_gemini_01"
    ]
    assert [row["paired_episode_set_id"] for row in recorded_host_rows] == [
        "pair_gemini_host_001"
    ]
    assert {row["pair_status"] for row in recorded_host_rows} == {"usable"}
    assert {row["failure_tags"] for row in recorded_host_rows} == {"none"}


def test_evidence_note_records_one_gemini_host_pair_and_keeps_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "One Gemini-only mediation-specific host-realization pair is now recorded for "
        "`scenario_host_gemini_01`, but `scenario_host_gemini_01` / `gemini` remains "
        "`insufficient` because one pair is still below the three-pair minimum."
    ) in text
    assert (
        "reference still carries the only host-realization `candidate_positive` cell."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
