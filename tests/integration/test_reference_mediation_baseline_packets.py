"""Integration revalidation for committed reference mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_THRASH_PACKET_PATH,
    REPO_ROOT,
    packet_without_path,
    parse_markdown_table,
    parse_run_packet,
    read,
    section,
)
from tests.integration._reference_mediation_baseline_packets import (
    REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS,
    REFERENCE_MEDIATION_BASELINE_PACKET_PATHS,
    emit_reference_mediation_baseline_packets,
)


def test_reference_mediation_baseline_packets_match_committed_docs() -> None:
    for scenario_id, builder in REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS.items():
        committed_path = REPO_ROOT / REFERENCE_MEDIATION_BASELINE_PACKET_PATHS[scenario_id]
        committed_packet = packet_without_path(parse_run_packet(committed_path))

        assert builder() == committed_packet


def test_candidate_emitter_prints_both_reference_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_reference_mediation_baseline_packets()
    captured = capsys.readouterr().out

    for relative_path in REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.values())
    assert "scenario_thrash_reference_01" not in emitted_docs

    for scenario_id, relative_path in REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS[scenario_id]()


def test_reference_thrash_packet_remains_an_explicit_gap() -> None:
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
    thrash_row = next(row for row in rows if row["scenario_id"] == "scenario_thrash_reference_01")

    assert set(REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS) == {
        "scenario_uncertainty_reference_01",
        "scenario_host_reference_01",
    }
    assert thrash_row["evidence_status"] == "artifact_gap"
    assert thrash_row["packet_path"] == "none"
    assert not REFERENCE_THRASH_PACKET_PATH.exists()


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []

    for line in output.splitlines():
        if line.startswith("--- docs/mediation_evidence/reference/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs
