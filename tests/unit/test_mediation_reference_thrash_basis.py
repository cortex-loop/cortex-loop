"""Mechanical checks for the reference mediation thrash basis gap."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_THRASH_BASIS_NOTE_PATH,
    REFERENCE_THRASH_PACKET_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)
from tests.integration._reference_mediation_baseline_packets import (
    REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS,
)


def test_reference_thrash_basis_note_exists_and_keeps_gap_honest() -> None:
    text = read(REFERENCE_THRASH_BASIS_NOTE_PATH)

    assert REFERENCE_THRASH_BASIS_NOTE_PATH.is_file()
    assert status(REFERENCE_THRASH_BASIS_NOTE_PATH) == "artifact_gap remains honest"
    assert "`scenario_thrash_reference_01` must remain `artifact_gap`" in text
    assert "reference-host commitment and publication packets" in text
    assert "SRE branch, goals, and brake tests are carrier and policy surfaces" in text
    assert "Carrier or policy tests alone are insufficient." in text
    assert "no current repo surface records a lawful repeated reopen/resume" in text


def test_reference_thrash_basis_note_contains_readiness_checklist_and_anti_patterns() -> None:
    text = read(REFERENCE_THRASH_BASIS_NOTE_PATH)
    readiness = section(text, "Future Packet Readiness Checklist")
    anti_patterns = section(text, "Non-Qualifying Anti-Patterns")

    assert "one bounded `reference`-host multi-step scenario" in readiness
    assert (
        "at least one candidate-bearing or full-commitment turn plus at least one follow-up turn"
        in readiness
    )
    assert "explicit branch trajectory evidence" in readiness
    assert "explicit task-value completion outcome" in readiness
    assert "the same commitment boundary and evidence/publication surface" in readiness
    assert "a live builder from code" in readiness
    assert "a committed markdown baseline packet" in readiness
    assert "a semantic revalidation test from live code" in readiness
    assert "a candidate-emission command that does not overwrite docs" in readiness

    assert "pure carrier-type tests" in anti_patterns
    assert "synthetic branch labels with no host episode" in anti_patterns
    assert "single-turn packets with prose that merely mentions churn" in anti_patterns
    assert (
        "infers reopen/resume behavior without committed trace evidence" in anti_patterns
    )


def test_reference_thrash_row_and_current_surfaces_remain_explicit_gaps() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    thrash_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_reference_01")

    assert thrash_row["evidence_status"] == "artifact_gap"
    assert thrash_row["packet_path"] == "none"
    assert thrash_row["failure_tags"] == "artifact_gap"
    assert "CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0.md" in thrash_row["notes"]
    assert not REFERENCE_THRASH_PACKET_PATH.exists()
    assert "scenario_thrash_reference_01" not in REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS


def test_evidence_note_still_keeps_mediation_blocked_and_paired_runs_absent() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert "No live baseline-versus-mediated paired runs are currently recorded" in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
    assert "CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0.md" in text
