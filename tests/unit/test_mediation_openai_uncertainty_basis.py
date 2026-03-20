"""Mechanical checks for the committed OpenAI mediation uncertainty basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    OPENAI_BASELINE_INDEX_PATH,
    OPENAI_UNCERTAINTY_BASIS_NOTE_PATH,
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


def test_openai_uncertainty_basis_note_exists_and_records_first_openai_baseline_seam() -> None:
    text = read(OPENAI_UNCERTAINTY_BASIS_NOTE_PATH)

    assert OPENAI_UNCERTAINTY_BASIS_NOTE_PATH.is_file()
    assert status(OPENAI_UNCERTAINTY_BASIS_NOTE_PATH) == "openai uncertainty baseline anchor recorded"
    assert "OpenAI uncertainty is the first lawful OpenAI mediation-evidence seam" in text
    assert "landed OpenAI observe/bind, commitment-path, and neutral-only slices" in text
    assert "baseline-only and does not earn a comparator yet" in text
    assert "direct commitment-path evidence, not evaluation-packet publication evidence" in text
    assert "No host-realization or thrash claim is implied by this anchor" in text
    assert "tests/integration/_openai_mediation_baseline_packets.py" in text
    assert "tests/integration/test_openai_mediation_baseline_packets.py" in text


def test_openai_index_and_baseline_anchor_exist_without_any_mediated_openai_packet() -> None:
    rows = parse_markdown_table(section(read(OPENAI_BASELINE_INDEX_PATH), "Index Rows"))
    row = rows[0]

    assert OPENAI_BASELINE_INDEX_PATH.is_file()
    assert status(OPENAI_BASELINE_INDEX_PATH) == "openai mediation baseline run index (`active`, baseline-only)"
    assert len(rows) == 1
    assert row["run_id"] == "openai_uncertainty_baseline_run_001"
    assert row["scenario_id"] == "scenario_uncertainty_openai_01"
    assert row["host_family"] == "openai"
    assert row["variant"] == "baseline_non_mediated"
    assert row["paired_episode_set_id"] == "pending_pair_openai_uncertainty_001"
    assert row["evidence_status"] == "baseline_packet_committed"
    assert row["packet_path"] == (
        "docs/mediation_evidence/openai/"
        "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
    )
    assert (
        row["basis_surface"]
        == "tests/integration/test_openai_mediation_baseline_packets.py::test_openai_uncertainty_baseline_packet_matches_committed_doc"
    )
    assert row["failure_tags"] == "none"
    assert OPENAI_UNCERTAINTY_PACKET_PATH.is_file()
    assert (
        "docs/mediation_evidence/openai/"
        "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
    ) in OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS
    assert not list(OPENAI_UNCERTAINTY_PACKET_PATH.parent.glob("*__experimental_mediated__run_*.md"))


def test_openai_paired_evidence_remains_absent_for_uncertainty_anchor() -> None:
    ledger_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))

    assert all(
        row["scenario_id"] != "scenario_uncertainty_openai_01"
        for row in ledger_rows
        if row["paired_episode_set_id"] != "none_recorded_yet"
    )


def test_evidence_note_keeps_mediation_blocked_with_openai_baseline_anchor_only() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert status(EVIDENCE_NOTE_PATH) == "reference_and_gemini_series_with_openai_baseline_anchor_recorded"
    assert "A committed OpenAI uncertainty baseline anchor is now recorded" in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
