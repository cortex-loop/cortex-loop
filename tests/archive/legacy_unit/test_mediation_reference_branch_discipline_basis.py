"""Mechanical checks for the committed reference branch-discipline basis."""

from __future__ import annotations

from tests.archive._mediation_evidence import parse_markdown_table, read, section, status


DOC_ROOT = "docs/lab/mediation_evidence/reference/"
LEDGER_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "docs"
    / "lab"
    / "CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md"
)
BASIS_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "docs"
    / "lab"
    / "CORTEX_V2_MEDIATION_REFERENCE_BRANCH_DISCIPLINE_BASIS_NOTE_0.md"
)
REPLICATION_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[2]
    / "docs"
    / "lab"
    / "CORTEX_V2_MEDIATION_REFERENCE_BRANCH_DISCIPLINE_REPLICATION_NOTE_0.md"
)


def test_reference_branch_discipline_basis_docs_exist() -> None:
    text = read(BASIS_PATH)
    assert status(BASIS_PATH) == "reference branch discipline basis satisfied"
    assert "three lawful reference branch-discipline comparator pairs are recorded" in text
    assert "stale_branch_count" in text
    assert "orphaned_branch_count" in text
    assert "unnecessary_branch_count" in text
    assert REPLICATION_PATH.is_file()


def test_reference_branch_discipline_pairs_are_recorded() -> None:
    rows = parse_markdown_table(section(read(LEDGER_PATH), "Recorded Paired Runs"))
    branch_rows = [row for row in rows if row["scenario_id"] == "scenario_branch_reference_01"]
    assert [row["paired_episode_set_id"] for row in branch_rows] == [
        "pair_reference_branch_001",
        "pair_reference_branch_002",
        "pair_reference_branch_003",
    ]
    assert {row["pair_status"] for row in branch_rows} == {"usable"}
    assert all(row["baseline_packet_ref"].startswith(DOC_ROOT) for row in branch_rows)
    assert all(row["mediated_packet_ref"].startswith(DOC_ROOT) for row in branch_rows)
