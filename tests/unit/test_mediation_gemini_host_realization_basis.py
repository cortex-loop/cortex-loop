"""Mechanical checks for the Gemini host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
    GEMINI_HOST_REALIZATION_PACKET_PATH,
    GEMINI_PACKET_EXAMPLE_DOC_PATH,
    MEDIATION_GEMINI_PACKET_ROOT,
    PAIRED_LEDGER_PATH,
    parse_markdown_table,
    read,
    section,
    status,
)


def test_gemini_host_realization_admissibility_note_exists_and_records_audit() -> None:
    text = read(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH.is_file()
    assert (
        status(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)
        == "gemini host realization comparator not yet admissible"
    )
    assert "tests/unit/test_gemini_host.py" in text
    assert "tests/unit/test_gemini_host_commitment.py" in text
    assert "tests/unit/test_gemini_host_neutral.py" in text
    assert "tests/integration/_gemini_lane_packet_example.py" in text
    assert "tests/integration/test_gemini_lane_packet_example.py" in text
    assert "docs/CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0.md" in text
    assert "docs/mediation_evidence/gemini/scenario_host_gemini_01__baseline_non_mediated__run_001.md" in text
    assert "one lawful Gemini host-facing publication surface is now committed" in text
    assert "no matched mediated Gemini host-realization publication surface exists yet" in text
    assert "Gemini thrash and uncertainty evidence may not be reused as proxy host-realization evidence" in text


def test_gemini_host_realization_admissibility_law_is_explicit() -> None:
    text = read(GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH)

    assert "`scenario_id=scenario_host_gemini_01`" in text
    assert "`host_family=gemini`" in text
    assert "`task_value_rubric_id=task_value_equal_host_realization`" in text
    assert "`approval_or_environment_context_id=env_boundary_sensitive`" in text
    assert "same Gemini observe/bind meaning" in text
    assert "same commitment truth boundary" in text
    assert "same host-facing evidence/publication surface" in text
    assert "same packet kind: `current-pair`" in text
    assert "same final certified completion class" in text
    assert "same contradiction/degradation preservation law" in text
    assert "same truthful-withheld meaning" in text
    assert "no host flattening" in text
    assert "no truth smoothing" in text
    assert (
        "No comparator may count until a matched mediated Gemini host-realization "
        "publication surface is first defined from live code."
    ) in text
    assert "claiming host lift from thrash or uncertainty packets" in text
    assert "claiming host lift from candidate-bearing turns alone" in text
    assert "adding a mediated comparator before a matched mediated publication surface exists" in text
    assert "changing Gemini host semantics to make mediation look better" in text
    assert "using latency-only improvement, shorter artifacts, or cosmetic simplification as host-realization evidence" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "No admissible Gemini host-realization comparator is recorded yet" in text
    assert "A baseline-only Gemini host-realization anchor is now recorded" in text


def test_gemini_host_realization_anchor_is_recorded_but_remains_unpaired() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))

    assert {row["scenario_id"] for row in rows} == {
        "scenario_host_gemini_01",
        "scenario_thrash_gemini_01",
        "scenario_uncertainty_gemini_01",
    }
    host_row = next(row for row in rows if row["scenario_id"] == "scenario_host_gemini_01")
    assert host_row["run_id"] == "gemini_host_realization_baseline_run_001"
    assert host_row["paired_episode_set_id"] == "pending_pair_gemini_host_001"
    assert host_row["evidence_status"] == "baseline_packet_committed"
    assert host_row["packet_path"] == (
        "docs/mediation_evidence/gemini/"
        "scenario_host_gemini_01__baseline_non_mediated__run_001.md"
    )
    assert (
        host_row["basis_surface"]
        == "tests/integration/test_gemini_lane_packet_example.py::test_gemini_lane_current_pair_packet_example_matches_committed_doc"
    )
    assert "CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md" in host_row["notes"]
    assert GEMINI_PACKET_EXAMPLE_DOC_PATH.is_file()
    assert GEMINI_HOST_REALIZATION_PACKET_PATH.is_file()

    assert not any(
        path.name.startswith("scenario_host_gemini_01__experimental_mediated__")
        for path in MEDIATION_GEMINI_PACKET_ROOT.glob("*.md")
    )

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    assert not any(row["scenario_id"] == "scenario_host_gemini_01" for row in recorded_rows)


def test_evidence_note_keeps_gemini_host_realization_unpaired_and_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "A baseline-only Gemini host-realization anchor is now recorded through "
        "`docs/CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0.md` and "
        "`docs/mediation_evidence/gemini/scenario_host_gemini_01__baseline_non_mediated__run_001.md`, "
        "but `scenario_host_gemini_01` remains intentionally unpaired pending the Gemini "
        "comparator admissibility audit recorded in "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
