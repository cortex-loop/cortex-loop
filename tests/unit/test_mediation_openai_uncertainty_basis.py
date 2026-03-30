"""Mechanical checks for the committed OpenAI mediation uncertainty basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    OPENAI_BASELINE_INDEX_PATH,
    OPENAI_UNCERTAINTY_BASIS_NOTE_PATH,
    OPENAI_UNCERTAINTY_REPLICATION_NOTE_PATH,
    OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    OPENAI_UNCERTAINTY_PACKET_PATH,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)
from tests.integration._openai_mediation_baseline_packets import (
    OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
)
from tests.integration._openai_mediation_uncertainty_episode import (
    EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE,
    OPENAI_UNCERTAINTY_PAIR_KEYS,
    OPENAI_UNCERTAINTY_PAIR_SPECS,
    build_openai_uncertainty_episode_snapshot,
)


def test_openai_uncertainty_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(OPENAI_UNCERTAINTY_BASIS_NOTE_PATH)

    assert OPENAI_UNCERTAINTY_BASIS_NOTE_PATH.is_file()
    assert status(OPENAI_UNCERTAINTY_BASIS_NOTE_PATH) == "openai uncertainty paired-series basis satisfied"
    assert "old OpenAI baseline anchor packet was lawful but too thin" in text
    assert "basis is now satisfied by the committed OpenAI-host uncertainty paired-run series" in text
    assert "tests/integration/_openai_mediation_uncertainty_episode.py" in text
    assert "tests/integration/test_openai_mediated_uncertainty_comparator.py" in text
    assert "docs/CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_REPLICATION_NOTE_0.md" in text
    assert "tests/integration/_openai_mediation_baseline_packets.py" in text
    assert "tests/integration/test_openai_mediation_baseline_packets.py" in text


def test_openai_uncertainty_replication_note_records_fairness_and_distinctness_law() -> None:
    text = read(OPENAI_UNCERTAINTY_REPLICATION_NOTE_PATH)

    assert OPENAI_UNCERTAINTY_REPLICATION_NOTE_PATH.is_file()
    assert status(OPENAI_UNCERTAINTY_REPLICATION_NOTE_PATH) == "openai uncertainty replication law recorded"
    assert "pair_openai_uncertainty_001" in text
    assert "pair_openai_uncertainty_002" in text
    assert "pair_openai_uncertainty_003" in text
    assert "same OpenAI commitment-path truth boundary" in text
    assert "same contradiction/degradation preservation law" in text
    assert "same direct commitment-path evidence surface" in text
    assert "unique `paired_episode_set_id`" in text
    assert "unique `session_id`" in text
    assert "unique `commitment_id`" in text
    assert "unique contradiction `source_tag`" in text
    assert "unique contradiction `summary`" in text
    assert "unique degradation `reason_code`" in text
    assert "unique uncertainty `spike_tag`" in text
    assert "blocked-final comparator" in text
    assert "claims host-realization lift from this series" in text


def test_openai_builder_packet_series_and_replication_note_exist() -> None:
    rows = parse_markdown_table(section(read(OPENAI_BASELINE_INDEX_PATH), "Index Rows"))
    openai_row = next(row for row in rows if row["scenario_id"] == "scenario_uncertainty_openai_01")

    assert openai_row["evidence_status"] == "baseline_packet_committed"
    assert openai_row["paired_episode_set_id"] == "pair_openai_uncertainty_001"
    assert openai_row["packet_path"] == (
        "docs/mediation_evidence/openai/"
        "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
    )
    assert openai_row["failure_tags"] == "none"
    assert (
        openai_row["basis_surface"]
        == "tests/integration/test_openai_mediation_baseline_packets.py::test_openai_uncertainty_baseline_packet_matches_committed_doc"
    )
    assert OPENAI_UNCERTAINTY_PACKET_PATH.is_file()
    assert (
        "docs/mediation_evidence/openai/scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
        in OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS
    )

    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS:
        snapshot = build_openai_uncertainty_episode_snapshot(pair_key)
        assert snapshot["step_sequence"] == list(EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE)
        assert snapshot["uncertified_loop_count"] == 2
        assert OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key].exists()
        assert OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS[pair_key].exists()

    assert len({spec.pair_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_source_tag for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_summary for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.degradation_reason_code for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3


def test_evidence_note_keeps_openai_uncertainty_explicit_under_j3() -> None:
    text = read(EVIDENCE_NOTE_PATH)
    ledger_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))

    assert status(EVIDENCE_NOTE_PATH) == "j2_gap_closure_reference_openai_claude_recorded"
    assert "- better uncertainty handling: `insufficient`" in text
    assert "scenario_uncertainty_openai_01/openai" in text
    assert "Current uncertainty signal still comes from one family only and still lacks Claude expansion." in text
    assert "The accepted J3 decision is that mediation is now justified for one bounded experimental seam." in text
    assert "This evidence package is not a second truth court and does not by itself authorize implementation." in text
    assert any(row["scenario_id"] == "scenario_uncertainty_openai_01" for row in ledger_rows)
