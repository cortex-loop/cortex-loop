"""Mechanical checks for the Gemini uncertainty baseline anchor."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_UNCERTAINTY_BASIS_NOTE_PATH,
    GEMINI_UNCERTAINTY_PACKET_PATH,
    MEDIATION_GEMINI_PACKET_ROOT,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_gemini_uncertainty_basis_note_exists_and_records_first_non_reference_anchor() -> None:
    text = read(GEMINI_UNCERTAINTY_BASIS_NOTE_PATH)

    assert GEMINI_UNCERTAINTY_BASIS_NOTE_PATH.is_file()
    assert status(GEMINI_UNCERTAINTY_BASIS_NOTE_PATH) == "gemini uncertainty baseline basis satisfied"
    assert "first lawful non-reference baseline seam" in text
    assert "Gemini host now has landed observe/bind, commitment-path, and neutral-only slices" in text
    assert "strongest non-reference baseline seam" in text
    assert "tests/integration/_gemini_mediation_baseline_packets.py" in text
    assert "tests/integration/test_gemini_mediation_baseline_packets.py" in text


def test_gemini_baseline_index_is_gemini_only_and_contains_one_anchor() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))

    assert GEMINI_BASELINE_INDEX_PATH.is_file()
    assert status(GEMINI_BASELINE_INDEX_PATH) == "gemini mediation baseline run index (`active`, baseline-only)"
    assert rows == [
        {
            "run_id": "gemini_uncertainty_baseline_run_001",
            "scenario_id": "scenario_uncertainty_gemini_01",
            "host_family": "gemini",
            "variant": "baseline_non_mediated",
            "paired_episode_set_id": "pending_pair_gemini_uncertainty_001",
            "evidence_status": "baseline_packet_committed",
            "packet_path": (
                "docs/mediation_evidence/gemini/"
                "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md"
            ),
            "basis_surface": (
                "tests/integration/test_gemini_mediation_baseline_packets.py::"
                "test_gemini_uncertainty_baseline_packet_matches_committed_doc"
            ),
            "failure_tags": "none",
            "notes": (
                "Canonical Gemini uncertainty baseline anchor. No Gemini mediated "
                "packet or counted Gemini pair is recorded yet; this anchor is backed "
                "by `docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md`."
            ),
        }
    ]


def test_gemini_baseline_anchor_exists_without_any_mediated_gemini_packet_or_pair() -> None:
    assert GEMINI_UNCERTAINTY_PACKET_PATH.is_file()
    assert sorted(path.name for path in MEDIATION_GEMINI_PACKET_ROOT.glob("*.md")) == [
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md"
    ]
    assert not any(MEDIATION_GEMINI_PACKET_ROOT.glob("*__experimental_mediated__run_*.md"))

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    assert not any(row["scenario_id"] == "scenario_uncertainty_gemini_01" for row in recorded_rows)


def test_evidence_note_records_gemini_baseline_anchor_and_keeps_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert status(EVIDENCE_NOTE_PATH) == "reference_series_and_gemini_baseline_anchor_recorded"
    assert (
        "A committed Gemini uncertainty baseline anchor is now recorded in "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_BASELINE_INDEX_0.md` and backed by "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md`."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
