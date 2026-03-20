"""Mechanical checks for the Gemini host-realization admissibility note."""

from __future__ import annotations

from tests._mediation_evidence import (
    EVIDENCE_NOTE_PATH,
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH,
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
    assert "tests/integration/_gemini_mediation_baseline_packets.py" in text
    assert "tests/integration/test_gemini_mediation_baseline_packets.py" in text
    assert "no committed Gemini host-realization publication surface comparable to the reference `current-pair` packet example" in text
    assert "no committed Gemini truthful-withheld host packet surface yet" in text
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
    assert "same final certified completion class" in text
    assert "no host flattening" in text
    assert "no truth smoothing" in text
    assert "No comparator may count until a committed Gemini host-realization baseline surface is first defined from live code." in text
    assert "claiming host lift from thrash or uncertainty packets" in text
    assert "claiming host lift from candidate-bearing turns alone" in text
    assert "adding a mediated comparator before a committed baseline surface exists" in text
    assert "changing Gemini host semantics to make mediation look better" in text
    assert "using latency-only improvement, shorter artifacts, or cosmetic simplification as host-realization evidence" in text
    assert "claiming host lift from prose-only interpretation with no live code path" in text
    assert "No admissible Gemini host-realization comparator is recorded yet" in text
    assert "No admissible Gemini host-realization baseline anchor is recorded yet" in text


def test_gemini_host_realization_remains_unanchored_and_unpaired() -> None:
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))

    assert {row["scenario_id"] for row in rows} == {
        "scenario_thrash_gemini_01",
        "scenario_uncertainty_gemini_01",
    }
    assert (
        "`scenario_host_gemini_01` is intentionally absent pending the admissibility audit in "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`; "
        "no Gemini host-realization baseline anchor is committed yet."
    ) in read(GEMINI_BASELINE_INDEX_PATH)

    assert not any(
        path.name.startswith("scenario_host_gemini_01__baseline_non_mediated__")
        for path in MEDIATION_GEMINI_PACKET_ROOT.glob("*.md")
    )
    assert not any(
        path.name.startswith("scenario_host_gemini_01__experimental_mediated__")
        for path in MEDIATION_GEMINI_PACKET_ROOT.glob("*.md")
    )

    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    assert not any(row["scenario_id"] == "scenario_host_gemini_01" for row in recorded_rows)


def test_evidence_note_keeps_gemini_host_realization_unpaired_and_mediation_blocked() -> None:
    text = read(EVIDENCE_NOTE_PATH)

    assert (
        "`scenario_host_gemini_01` remains intentionally unpaired pending the Gemini "
        "admissibility audit recorded in "
        "`docs/CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`."
    ) in text
    assert "Mediation remains blocked" in text
    assert "no implementation seam may open" in text
