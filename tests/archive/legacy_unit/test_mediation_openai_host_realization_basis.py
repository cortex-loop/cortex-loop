"""Mechanical checks for the OpenAI host-realization admissibility note."""

from __future__ import annotations

from tests.archive._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    OPENAI_BASELINE_INDEX_PATH,
    OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    OPENAI_HOST_REALIZATION_BASELINE_PACKET_PATHS,
    OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATH,
    OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATHS,
    OPENAI_HOST_REALIZATION_PACKET_PATH,
    OPENAI_HOST_REALIZATION_REPLICATION_NOTE_PATH,
    OPENAI_MEDIATED_PACKET_EXAMPLE_DOC_PATH,
    OPENAI_PACKET_EXAMPLE_DOC_PATH,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_openai_host_realization_admissibility_note_exists_and_records_audit() -> None:
    text = read(OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH.is_file()
    assert (
        status(OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)
        == "three lawful openai host realization comparator pairs recorded"
    )
    assert "tests/unit/test_openai_host.py" in text
    assert "tests/unit/test_openai_host_commitment.py" in text
    assert "tests/unit/test_openai_host_neutral.py" in text
    assert "tests/integration/_openai_lane_packet_example.py" in text
    assert "tests/integration/test_openai_lane_packet_example.py" in text
    assert "docs/experimental/CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md" in text
    assert "tests/integration/_openai_mediated_lane_packet_example.py" in text
    assert "tests/integration/test_openai_mediated_lane_packet_example.py" in text
    assert "docs/experimental/CORTEX_V2_OPENAI_MEDIATED_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/lab/mediation_evidence/openai/scenario_host_openai_01__baseline_non_mediated__run_001.md" in text
    assert "docs/lab/mediation_evidence/openai/scenario_host_openai_01__experimental_mediated__run_001.md" in text
    assert "docs/lab/CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_REPLICATION_NOTE_0.md" in text
    assert "three lawful OpenAI host-realization comparator pairs are recorded" in text
    assert "direct host-native opportunity specialization at the selection layer" in text
    assert "OpenAI-only" in text


def test_openai_host_realization_admissibility_law_is_explicit() -> None:
    text = read(OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert "`scenario_id=scenario_host_openai_01`" in text
    assert "`host_family=openai`" in text
    assert "`task_value_rubric_id=task_value_equal_host_realization`" in text
    assert "`approval_or_environment_context_id=env_boundary_sensitive`" in text
    assert "same OpenAI observe/bind meaning" in text
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
    assert "changing OpenAI host semantics to make mediation look better" in text
    assert "using latency-only improvement, shorter artifacts, or cosmetic simplification as host-realization evidence" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "three lawful OpenAI host-realization comparator pairs are recorded" in text
    assert (
        "`scenario_host_openai_01` / `openai` now has `candidate_positive` cell-level "
        "signal for better host-specialized realization"
    ) in text


def test_openai_host_realization_anchor_is_rebound_to_a_recorded_pair() -> None:
    rows = parse_markdown_table(section(read(OPENAI_BASELINE_INDEX_PATH), "Index Rows"))

    assert {row["scenario_id"] for row in rows} == {
        "scenario_host_openai_01",
        "scenario_thrash_openai_01",
        "scenario_uncertainty_openai_01",
    }
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_openai_01")
    assert host_row["run_id"] == "openai_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pair_openai_host_001"
    assert host_row["evidence_status"] == "baseline_packet_committed"
    assert host_row["packet_path"] == (
        "docs/lab/mediation_evidence/openai/"
        "scenario_host_openai_01__baseline_non_mediated__run_001.md"
    )
    assert (
        host_row["basis_surface"]
        == "tests/integration/test_openai_lane_packet_example.py::test_openai_lane_current_pair_packet_example_matches_committed_doc"
    )
    assert "CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md" in host_row["notes"]
    assert "CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_REPLICATION_NOTE_0.md" in host_row["notes"]
    assert OPENAI_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert OPENAI_MEDIATED_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert OPENAI_HOST_REALIZATION_PACKET_PATH.is_file()
    assert OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATH.is_file()
    assert all(path.is_file() for path in OPENAI_HOST_REALIZATION_BASELINE_PACKET_PATHS.values())
    assert all(path.is_file() for path in OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATHS.values())
    assert OPENAI_HOST_REALIZATION_REPLICATION_NOTE_PATH.is_file()

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    recorded_host_rows = [
        row for row in recorded_rows if row["scenario_id"] == "scenario_host_openai_01"
    ]
    assert [row["paired_episode_set_id"] for row in recorded_host_rows] == [
        "pair_openai_host_001",
        "pair_openai_host_002",
        "pair_openai_host_003",
    ]
    assert {row["pair_status"] for row in recorded_host_rows} == {"usable"}
    assert {row["failure_tags"] for row in recorded_host_rows} == {"none"}


def test_evidence_note_records_three_openai_host_pairs_and_supports_j3_decision() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "Three OpenAI-only mediation-specific host-realization pairs are now recorded "
        "for `scenario_host_openai_01`."
    ) in text
    assert (
        "`scenario_host_openai_01` / `openai` now has `candidate_positive` signal "
        "for better host-specialized realization"
    ) in text
    assert (
        "Reference, Gemini, OpenAI, and Claude now carry the host-realization "
        "`candidate_positive` cells."
    ) in text
    assert "The accepted J3 decision is that mediation is now justified for one bounded experimental seam." in text
    assert "This evidence package is not a second truth court and does not by itself authorize implementation." in text
