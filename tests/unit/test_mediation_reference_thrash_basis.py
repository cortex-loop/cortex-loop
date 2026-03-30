"""Mechanical checks for the committed reference mediation thrash basis."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_THRASH_BASELINE_BURDEN_PATHS,
    REFERENCE_THRASH_BASIS_NOTE_PATH,
    REFERENCE_THRASH_PACKET_PATH,
    REFERENCE_THRASH_REPLICATION_NOTE_PATH,
    REFERENCE_THRASH_BASELINE_PACKET_PATHS,
    REFERENCE_THRASH_MEDIATED_BURDEN_PATHS,
    REFERENCE_THRASH_MEDIATED_PACKET_PATHS,
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
    REFERENCE_THRASH_PAIR_KEYS,
    REFERENCE_THRASH_PAIR_SPECS,
    build_reference_thrash_episode_snapshot,
)


def test_reference_thrash_basis_note_exists_and_records_satisfied_basis() -> None:
    text = read(REFERENCE_THRASH_BASIS_NOTE_PATH)

    assert REFERENCE_THRASH_BASIS_NOTE_PATH.is_file()
    assert status(REFERENCE_THRASH_BASIS_NOTE_PATH) == "reference thrash basis satisfied"
    assert "basis is now satisfied by the committed reference-host thrash baseline series" in text
    assert "tests/integration/_reference_mediation_thrash_episode.py" in text
    assert "tests/integration/test_reference_mediation_baseline_packets.py" in text
    assert "docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md" in text
    assert "deterministic visible-burden derivation" in text.lower()


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


def test_reference_thrash_builder_packet_series_and_replication_note_exist() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    thrash_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_reference_01")
    replication_text = read(REFERENCE_THRASH_REPLICATION_NOTE_PATH)

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
    assert status(REFERENCE_THRASH_REPLICATION_NOTE_PATH) == "reference thrash replication law recorded"
    assert "pair_reference_thrash_001" in replication_text
    assert "pair_reference_thrash_002" in replication_text
    assert "pair_reference_thrash_003" in replication_text
    assert "unique:" in replication_text
    assert "session_id" in replication_text
    assert "candidate_id" in replication_text
    assert "commitment_id" in replication_text
    assert "provenance artifact id" in replication_text
    assert "non-main branch track ref" in replication_text
    assert "uncertainty spike tag" in replication_text
    assert "visible intervention step" in replication_text

    for pair_key in REFERENCE_THRASH_PAIR_KEYS:
        snapshot = build_reference_thrash_episode_snapshot(pair_key)
        assert snapshot["branch_sequence"] == list(EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE)
        assert REFERENCE_THRASH_BASELINE_PACKET_PATHS[pair_key].exists()
        assert REFERENCE_THRASH_MEDIATED_PACKET_PATHS[pair_key].exists()
        assert REFERENCE_THRASH_BASELINE_BURDEN_PATHS[pair_key].exists()
        assert REFERENCE_THRASH_MEDIATED_BURDEN_PATHS[pair_key].exists()

    assert len({spec.pair_id for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in REFERENCE_THRASH_PAIR_SPECS.values()}) == 3


def test_evidence_note_uses_reference_thrash_pairs_in_the_j3_decision() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert status(EVIDENCE_NOTE_PATH) == "j2_gap_closure_reference_openai_claude_recorded"
    assert "All current reference-host, Gemini-host, OpenAI-host, and Claude-host committed mediation packet surfaces are now present on the current line." in text
    assert "- reduced thrashing: `candidate_positive`" in text
    assert "scenario_thrash_reference_01/reference" in text
    assert "scenario_branch_reference_01/reference" in text
    assert "candidate_positive" in text
    assert "The accepted J3 decision is that mediation is now justified for one bounded experimental seam." in text
    assert "This evidence package is not a second truth court and does not by itself authorize implementation." in text
