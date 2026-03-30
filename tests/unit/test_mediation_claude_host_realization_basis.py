"""Mechanical checks for the Claude host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    CLAUDE_BASELINE_INDEX_PATH,
    CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    CLAUDE_HOST_REALIZATION_BASELINE_PACKET_PATHS,
    CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATH,
    CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATHS,
    CLAUDE_HOST_REALIZATION_PACKET_PATH,
    CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_PATH,
    CLAUDE_LANE_PACKET_EXAMPLE_DOC_PATH,
    CLAUDE_MEDIATED_PACKET_EXAMPLE_DOC_PATH,
    EVIDENCE_NOTE_PATH,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_claude_host_realization_admissibility_note_exists_and_records_audit() -> None:
    text = read(CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH.is_file()
    assert (
        status(CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)
        == "three lawful claude host realization comparator pairs recorded"
    )
    assert "tests/integration/_claude_lane_packet_example.py" in text
    assert "tests/integration/test_claude_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_CLAUDE_LANE_PACKET_EXAMPLE_0.md" in text
    assert "tests/integration/_claude_mediated_lane_packet_example.py" in text
    assert "tests/integration/test_claude_mediated_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_CLAUDE_MEDIATED_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_0.md" in text
    assert "three lawful Claude host-realization comparator pairs are recorded" in text
    assert "direct host-native opportunity specialization at the selection layer" in text
    assert "Claude-only" in text


def test_claude_host_realization_admissibility_law_is_explicit() -> None:
    text = read(CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert "`scenario_id=scenario_host_claude_01`" in text
    assert "`host_family=claude`" in text
    assert "`task_value_rubric_id=task_value_equal_host_realization`" in text
    assert "`approval_or_environment_context_id=env_boundary_sensitive`" in text
    assert "same Claude observe/bind meaning" in text
    assert "same commitment truth boundary" in text
    assert "same evaluation-packet publication surface" in text
    assert "same packet kind: `current-pair`" in text
    assert "same final certified completion class" in text
    assert "same contradiction/degradation preservation law" in text
    assert "same truthful-withheld meaning" in text
    assert "same selected family: `seek-context`" in text
    assert "same host-opportunity set containing `mcp.query`" in text
    assert "three lawful Claude host-realization comparator pairs are recorded" in text
    assert (
        "`scenario_host_claude_01` / `claude` now has `candidate_positive` cell-level "
        "signal for better host-specialized realization"
    ) in text


def test_claude_host_realization_anchor_is_rebound_to_a_recorded_pair() -> None:
    rows = parse_markdown_table(section(read(CLAUDE_BASELINE_INDEX_PATH), "Index Rows"))
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_claude_01")

    assert host_row["run_id"] == "claude_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pair_claude_host_001"
    assert host_row["evidence_status"] == "baseline_packet_committed"
    assert host_row["packet_path"] == (
        "docs/mediation_evidence/claude/"
        "scenario_host_claude_01__baseline_non_mediated__run_001.md"
    )
    assert (
        host_row["basis_surface"]
        == "tests/integration/test_claude_lane_packet_example.py::test_claude_lane_current_pair_packet_example_matches_committed_doc"
    )
    assert "CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md" in host_row["notes"]
    assert "CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_0.md" in host_row["notes"]
    assert CLAUDE_LANE_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert CLAUDE_MEDIATED_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert CLAUDE_HOST_REALIZATION_PACKET_PATH.is_file()
    assert CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATH.is_file()
    assert all(path.is_file() for path in CLAUDE_HOST_REALIZATION_BASELINE_PACKET_PATHS.values())
    assert all(path.is_file() for path in CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATHS.values())
    assert CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_PATH.is_file()

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    recorded_host_rows = [
        row for row in recorded_rows if row["scenario_id"] == "scenario_host_claude_01"
    ]
    assert [row["paired_episode_set_id"] for row in recorded_host_rows] == [
        "pair_claude_host_001",
        "pair_claude_host_002",
        "pair_claude_host_003",
    ]
    assert {row["pair_status"] for row in recorded_host_rows} == {"usable"}
    assert {row["failure_tags"] for row in recorded_host_rows} == {"none"}


def test_evidence_note_records_three_claude_host_pairs_and_supports_j3_decision() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "Three Claude-only mediation-specific host-realization pairs are now recorded "
        "for `scenario_host_claude_01`."
    ) in text
    assert (
        "`scenario_host_claude_01` / `claude` now has `candidate_positive` signal "
        "for better host-specialized realization"
    ) in text
    assert "Reference, Gemini, OpenAI, and Claude now carry the host-realization `candidate_positive` cells." in text
    assert "The accepted J3 decision is that mediation is now justified for one bounded experimental seam." in text
