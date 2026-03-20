"""Mechanical checks for the committed Gemini mediation thrash basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_THRASH_BASIS_NOTE_PATH,
    GEMINI_THRASH_REPLICATION_NOTE_PATH,
    GEMINI_THRASH_BASELINE_PACKET_PATHS,
    GEMINI_THRASH_MEDIATED_PACKET_PATHS,
    GEMINI_THRASH_PACKET_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)
from tests.integration._gemini_mediation_baseline_packets import (
    GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
)
from tests.integration._gemini_mediation_thrash_episode import (
    EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE,
    GEMINI_THRASH_PAIR_KEYS,
    GEMINI_THRASH_PAIR_SPECS,
    build_gemini_thrash_episode_snapshot,
)


def test_gemini_thrash_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(GEMINI_THRASH_BASIS_NOTE_PATH)

    assert GEMINI_THRASH_BASIS_NOTE_PATH.is_file()
    assert status(GEMINI_THRASH_BASIS_NOTE_PATH) == "gemini thrash paired-series basis satisfied"
    assert "old Gemini thrash cell was preseeded" in text
    assert "basis is now satisfied by the committed Gemini-host thrash paired-run series" in text
    assert "tests/integration/_gemini_mediation_thrash_episode.py" in text
    assert "tests/integration/_gemini_mediation_thrash_experimental.py" in text
    assert "tests/integration/test_gemini_mediated_thrash_comparator.py" in text
    assert "docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_REPLICATION_NOTE_0.md" in text


def test_gemini_thrash_replication_note_records_fairness_and_distinctness_law() -> None:
    text = read(GEMINI_THRASH_REPLICATION_NOTE_PATH)

    assert GEMINI_THRASH_REPLICATION_NOTE_PATH.is_file()
    assert status(GEMINI_THRASH_REPLICATION_NOTE_PATH) == "gemini thrash replication law recorded"
    assert "pair_gemini_thrash_001" in text
    assert "pair_gemini_thrash_002" in text
    assert "pair_gemini_thrash_003" in text
    assert "same Gemini observe/bind meaning across `content.delta` and `interaction.complete`" in text
    assert "same direct commitment-path evidence surface plus the same support-session and goal-continuity derivation surface" in text
    assert "same lawful certified completion class" in text
    assert "unique `paired_episode_set_id`" in text
    assert "unique `session_id`" in text
    assert "unique `candidate_id`" in text
    assert "unique `commitment_id`" in text
    assert "provenance artifact id" in text
    assert "non-main branch track ref" in text
    assert "uncertainty spike tag" in text
    assert "claims host-realization lift from this series" in text


def test_gemini_thrash_builder_packet_series_and_replication_note_exist() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))
    gemini_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_gemini_01")

    assert gemini_row["evidence_status"] == "baseline_packet_committed"
    assert gemini_row["paired_episode_set_id"] == "pair_gemini_thrash_001"
    assert gemini_row["packet_path"] == (
        "docs/mediation_evidence/gemini/"
        "scenario_thrash_gemini_01__baseline_non_mediated__run_001.md"
    )
    assert gemini_row["failure_tags"] == "none"
    assert (
        gemini_row["basis_surface"]
        == "tests/integration/test_gemini_mediation_baseline_packets.py::test_gemini_thrash_baseline_packet_matches_committed_doc"
    )
    assert GEMINI_THRASH_PACKET_PATH.is_file()
    assert "docs/mediation_evidence/gemini/scenario_thrash_gemini_01__baseline_non_mediated__run_001.md" in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS

    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        snapshot = build_gemini_thrash_episode_snapshot(pair_key)
        assert snapshot["branch_sequence"] == list(EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE)
        assert GEMINI_THRASH_BASELINE_PACKET_PATHS[pair_key].exists()
        assert GEMINI_THRASH_MEDIATED_PACKET_PATHS[pair_key].exists()

    assert len({spec.pair_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3


def test_evidence_note_keeps_mediation_blocked_with_gemini_thrash_series() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        status(EVIDENCE_NOTE_PATH)
        == "reference_three_series_with_gemini_two_series_and_openai_two_series_recorded"
    )
    assert "Three experimental Gemini-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert "Three experimental OpenAI-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert "docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_BASIS_NOTE_0.md" in text
    assert (
        "`scenario_thrash_gemini_01` / `gemini` now has `candidate_positive` "
        "cell-level signal for reduced thrashing and better branch discipline"
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
