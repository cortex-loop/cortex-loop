"""Mechanical checks for the committed Claude branch-discipline basis."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import parse_markdown_table, read, section, status


LEDGER_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md"
BASIS_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_CLAUDE_BRANCH_DISCIPLINE_BASIS_NOTE_0.md"
REPLICATION_PATH = Path(__file__).resolve().parents[2] / "docs" / "CORTEX_V2_MEDIATION_CLAUDE_BRANCH_DISCIPLINE_REPLICATION_NOTE_0.md"


def test_claude_branch_discipline_basis_docs_exist() -> None:
    text = read(BASIS_PATH)
    assert status(BASIS_PATH) == "claude branch discipline basis satisfied"
    assert "three lawful claude branch-discipline comparator pairs are recorded" in text.lower()
    assert "stale_branch_count" in text
    assert "orphaned_branch_count" in text
    assert "unnecessary_branch_count" in text
    assert REPLICATION_PATH.is_file()


def test_claude_branch_discipline_pairs_are_recorded() -> None:
    rows = parse_markdown_table(section(read(LEDGER_PATH), "Recorded Paired Runs"))
    branch_rows = [row for row in rows if row["scenario_id"] == "scenario_branch_claude_01"]
    assert [row["paired_episode_set_id"] for row in branch_rows] == [
        "pair_claude_branch_001",
        "pair_claude_branch_002",
        "pair_claude_branch_003",
    ]
    assert {row["pair_status"] for row in branch_rows} == {"usable"}
