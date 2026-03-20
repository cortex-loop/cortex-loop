"""Mechanical checks for the committed reference mediation thrash basis."""

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
from tests.integration._reference_mediation_thrash_episode import (
    EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE,
    build_reference_thrash_episode_snapshot,
)


def test_reference_thrash_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(REFERENCE_THRASH_BASIS_NOTE_PATH)

    assert REFERENCE_THRASH_BASIS_NOTE_PATH.is_file()
    assert status(REFERENCE_THRASH_BASIS_NOTE_PATH) == "reference thrash basis satisfied"
    assert "basis is now satisfied by one committed reference-host baseline packet" in text
    assert "tests/integration/_reference_mediation_thrash_episode.py" in text
    assert "tests/integration/test_reference_mediation_baseline_packets.py" in text
    assert "docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_001.md" in text


def test_reference_thrash_basis_note_contains_exact_derivation_rules_and_anti_patterns() -> None:
    text = read(REFERENCE_THRASH_BASIS_NOTE_PATH)
    derivation_rules = section(text, "Deterministic Branch Derivation Rules")
    anti_patterns = section(text, "Non-Qualifying Anti-Patterns")

    assert (
        "`open`: a non-main branch appears in `branch_registry` that was absent in the "
        "previous step, and the selected family for the current step is `branch`"
    ) in derivation_rules
    assert (
        "`suspend`: the previous step had `active_track_ref` equal to a non-main branch, "
        "the current step returns `active_track_ref` to `main`, and that branch still "
        "remains in `branch_registry`"
    ) in derivation_rules
    assert (
        "`resume`: the previous step had `active_track_ref=\"main\"`, the current step "
        "switches to an existing non-main branch, and `resume_anchor_available=True`"
    ) in derivation_rules
    assert (
        "`merge`: a non-main branch present in the previous step disappears from "
        "`branch_registry` after the current step yields a `FULL_COMMITMENT` verdict of "
        "`CERTIFIED`"
    ) in derivation_rules
    assert "`open -> suspend -> resume -> merge`" in derivation_rules

    assert "pure carrier-type tests" in anti_patterns
    assert "synthetic branch labels with no host episode" in anti_patterns
    assert "single-turn packets with prose that merely mentions churn" in anti_patterns
    assert (
        "infers reopen/resume behavior without committed trace evidence" in anti_patterns
    )


def test_reference_thrash_builder_and_packet_exist_and_match_index() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    thrash_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_reference_01")
    snapshot = build_reference_thrash_episode_snapshot()

    assert thrash_row["evidence_status"] == "baseline_packet_committed"
    assert thrash_row["paired_episode_set_id"] == "pair_reference_thrash_001"
    assert thrash_row["packet_path"] == (
        "docs/mediation_evidence/reference/"
        "scenario_thrash_reference_01__baseline_non_mediated__run_001.md"
    )
    assert thrash_row["failure_tags"] == "none"
    assert (
        thrash_row["basis_surface"]
        == "tests/integration/test_reference_mediation_baseline_packets.py::test_reference_thrash_baseline_packet_matches_committed_doc"
    )
    assert REFERENCE_THRASH_PACKET_PATH.exists()
    assert "scenario_thrash_reference_01" in REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS
    assert snapshot["branch_sequence"] == list(EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE)


def test_evidence_note_keeps_mediation_blocked_with_one_reference_only_pair() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert "All current reference-host scenario families now have committed baseline run packets" in text
    assert "One experimental reference-only baseline-versus-mediated thrash pair is now recorded" in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
