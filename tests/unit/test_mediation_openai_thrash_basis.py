"""Mechanical checks for the committed OpenAI mediation thrash basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    OPENAI_BASELINE_INDEX_PATH,
    OPENAI_THRASH_BASIS_NOTE_PATH,
    OPENAI_THRASH_REPLICATION_NOTE_PATH,
    OPENAI_THRASH_BASELINE_PACKET_PATHS,
    OPENAI_THRASH_MEDIATED_PACKET_PATHS,
    OPENAI_THRASH_PACKET_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)
from tests.integration._openai_mediation_baseline_packets import (
    OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
)
from tests.integration._openai_mediation_thrash_episode import (
    EXPECTED_OPENAI_THRASH_BRANCH_SEQUENCE,
    OPENAI_THRASH_PAIR_KEYS,
    OPENAI_THRASH_PAIR_SPECS,
    build_openai_thrash_episode_snapshot,
)


def test_openai_thrash_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(OPENAI_THRASH_BASIS_NOTE_PATH)

    assert OPENAI_THRASH_BASIS_NOTE_PATH.is_file()
    assert status(OPENAI_THRASH_BASIS_NOTE_PATH) == "openai thrash paired-series basis satisfied"
    assert "old OpenAI thrash cell was preseeded" in text
    assert "skips an anchor-only phase" in text
    assert "basis is now satisfied by the committed OpenAI-host thrash paired-run series" in text
    assert "tests/integration/_openai_mediation_thrash_episode.py" in text
    assert "tests/integration/_openai_mediation_thrash_experimental.py" in text
    assert "tests/integration/test_openai_mediated_thrash_comparator.py" in text
    assert "docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_REPLICATION_NOTE_0.md" in text


def test_openai_thrash_replication_note_records_fairness_and_distinctness_law() -> None:
    text = read(OPENAI_THRASH_REPLICATION_NOTE_PATH)

    assert OPENAI_THRASH_REPLICATION_NOTE_PATH.is_file()
    assert status(OPENAI_THRASH_REPLICATION_NOTE_PATH) == "openai thrash replication law recorded"
    assert "pair_openai_thrash_001" in text
    assert "pair_openai_thrash_002" in text
    assert "pair_openai_thrash_003" in text
    assert "same OpenAI observe/bind meaning across `response.output_text.delta` and `response.completed`" in text
    assert "same direct OpenAI commitment-path evidence surface plus the same support-session and goal-continuity derivation surface" in text
    assert "same lawful certified completion class" in text
    assert "unique `paired_episode_set_id`" in text
    assert "unique `session_id`" in text
    assert "unique `candidate_id`" in text
    assert "unique `commitment_id`" in text
    assert "provenance artifact id" in text
    assert "non-main branch track ref" in text
    assert "uncertainty spike tag" in text
    assert "claims host-realization lift from this series" in text


def test_openai_thrash_builder_packet_series_and_replication_note_exist() -> None:
    rows = parse_markdown_table(section(read(OPENAI_BASELINE_INDEX_PATH), "Index Rows"))
    openai_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_openai_01")

    assert openai_row["evidence_status"] == "baseline_packet_committed"
    assert openai_row["paired_episode_set_id"] == "pair_openai_thrash_001"
    assert openai_row["packet_path"] == (
        "docs/mediation_evidence/openai/"
        "scenario_thrash_openai_01__baseline_non_mediated__run_001.md"
    )
    assert openai_row["failure_tags"] == "none"
    assert (
        openai_row["basis_surface"]
        == "tests/integration/test_openai_mediation_baseline_packets.py::test_openai_thrash_baseline_packet_matches_committed_doc"
    )
    assert OPENAI_THRASH_PACKET_PATH.is_file()
    assert "docs/mediation_evidence/openai/scenario_thrash_openai_01__baseline_non_mediated__run_001.md" in OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS

    for pair_key in OPENAI_THRASH_PAIR_KEYS:
        snapshot = build_openai_thrash_episode_snapshot(pair_key)
        assert snapshot["branch_sequence"] == list(EXPECTED_OPENAI_THRASH_BRANCH_SEQUENCE)
        assert OPENAI_THRASH_BASELINE_PACKET_PATHS[pair_key].exists()
        assert OPENAI_THRASH_MEDIATED_PACKET_PATHS[pair_key].exists()

    assert len({spec.pair_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3


def test_evidence_note_keeps_mediation_blocked_with_openai_thrash_series() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        status(EVIDENCE_NOTE_PATH)
        == "reference_three_series_with_gemini_three_series_and_openai_three_series_recorded"
    )
    assert "Three experimental OpenAI-only baseline-versus-mediated thrash pairs are now recorded" in text
    assert "docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_BASIS_NOTE_0.md" in text
    assert (
        "`scenario_thrash_openai_01` / `openai` now has `candidate_positive` "
        "cell-level signal for reduced thrashing and better branch discipline"
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
