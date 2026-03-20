"""Mechanical checks for the committed Gemini mediation uncertainty basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_UNCERTAINTY_BASIS_NOTE_PATH,
    GEMINI_UNCERTAINTY_REPLICATION_NOTE_PATH,
    GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    GEMINI_UNCERTAINTY_PACKET_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)
from tests.integration._gemini_mediation_baseline_packets import (
    GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
)
from tests.integration._gemini_mediation_uncertainty_episode import (
    EXPECTED_GEMINI_UNCERTAINTY_STEP_SEQUENCE,
    GEMINI_UNCERTAINTY_PAIR_KEYS,
    GEMINI_UNCERTAINTY_PAIR_SPECS,
    build_gemini_uncertainty_episode_snapshot,
)


def test_gemini_uncertainty_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(GEMINI_UNCERTAINTY_BASIS_NOTE_PATH)

    assert GEMINI_UNCERTAINTY_BASIS_NOTE_PATH.is_file()
    assert status(GEMINI_UNCERTAINTY_BASIS_NOTE_PATH) == "gemini uncertainty paired-series basis satisfied"
    assert "old Gemini baseline anchor packet was lawful but too thin" in text
    assert "basis is now satisfied by the committed Gemini-host uncertainty paired-run series" in text
    assert "tests/integration/_gemini_mediation_uncertainty_episode.py" in text
    assert "tests/integration/test_gemini_mediated_uncertainty_comparator.py" in text
    assert "docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_REPLICATION_NOTE_0.md" in text
    assert "tests/integration/_gemini_mediation_baseline_packets.py" in text
    assert "tests/integration/test_gemini_mediation_baseline_packets.py" in text


def test_gemini_uncertainty_replication_note_records_fairness_and_distinctness_law() -> None:
    text = read(GEMINI_UNCERTAINTY_REPLICATION_NOTE_PATH)

    assert GEMINI_UNCERTAINTY_REPLICATION_NOTE_PATH.is_file()
    assert status(GEMINI_UNCERTAINTY_REPLICATION_NOTE_PATH) == "gemini uncertainty replication law recorded"
    assert "pair_gemini_uncertainty_001" in text
    assert "pair_gemini_uncertainty_002" in text
    assert "pair_gemini_uncertainty_003" in text
    assert "same Gemini commitment-path truth boundary" in text
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


def test_gemini_builder_packet_series_and_replication_note_exist() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))
    gemini_row = next(row for row in rows if row["scenario_id"] == "scenario_uncertainty_gemini_01")

    assert gemini_row["evidence_status"] == "baseline_packet_committed"
    assert gemini_row["paired_episode_set_id"] == "pair_gemini_uncertainty_001"
    assert gemini_row["packet_path"] == (
        "docs/mediation_evidence/gemini/"
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md"
    )
    assert gemini_row["failure_tags"] == "none"
    assert (
        gemini_row["basis_surface"]
        == "tests/integration/test_gemini_mediation_baseline_packets.py::test_gemini_uncertainty_baseline_packet_matches_committed_doc"
    )
    assert GEMINI_UNCERTAINTY_PACKET_PATH.is_file()
    assert "docs/mediation_evidence/gemini/scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md" in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS

    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS:
        snapshot = build_gemini_uncertainty_episode_snapshot(pair_key)
        assert snapshot["step_sequence"] == list(EXPECTED_GEMINI_UNCERTAINTY_STEP_SEQUENCE)
        assert snapshot["uncertified_loop_count"] == 2
        assert GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key].exists()
        assert GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS[pair_key].exists()

    assert len({spec.pair_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_source_tag for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_summary for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.degradation_reason_code for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3


def test_evidence_note_keeps_mediation_blocked_with_gemini_uncertainty_series() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        status(EVIDENCE_NOTE_PATH)
        == "reference_three_series_with_gemini_three_series_and_openai_three_series_recorded"
    )
    assert "Three experimental OpenAI-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert "Three experimental OpenAI-only uncertainty pairs are now recorded" in text
    assert "Three experimental Gemini-only uncertainty pairs are now recorded" in text
    assert "Three experimental Gemini-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert (
        "`scenario_uncertainty_gemini_01` / `gemini` now has `candidate_positive` "
        "cell-level signal for better uncertainty handling"
    ) in text
    assert (
        "`scenario_thrash_gemini_01` / `gemini` now has `candidate_positive` "
        "cell-level signal for reduced thrashing and better branch discipline"
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
