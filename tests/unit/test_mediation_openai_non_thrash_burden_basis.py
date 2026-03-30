"""Mechanical checks for the committed OpenAI non-thrash burden basis."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import parse_markdown_table, read, section, status


LEDGER_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md"
BASIS_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_OPENAI_NON_THRASH_BURDEN_BASIS_NOTE_0.md"
REPLICATION_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_OPENAI_NON_THRASH_BURDEN_REPLICATION_NOTE_0.md"


def test_openai_non_thrash_burden_basis_docs_exist() -> None:
    text = read(BASIS_PATH)
    assert status(BASIS_PATH) == "openai non-thrash burden basis satisfied"
    assert "three lawful openai non-thrash burden comparator pairs are recorded" in text.lower()
    assert "visible_intervention_steps" in text
    assert "does not rely on repeated `open -> suspend -> resume -> merge` churn" in text
    assert REPLICATION_PATH.is_file()


def test_openai_non_thrash_burden_pairs_are_recorded() -> None:
    rows = parse_markdown_table(section(read(LEDGER_PATH), "Recorded Paired Runs"))
    burden_rows = [row for row in rows if row["scenario_id"] == "scenario_burden_openai_01"]
    assert [row["paired_episode_set_id"] for row in burden_rows] == [
        "pair_openai_burden_001",
        "pair_openai_burden_002",
        "pair_openai_burden_003",
    ]
    assert {row["pair_status"] for row in burden_rows} == {"usable"}

