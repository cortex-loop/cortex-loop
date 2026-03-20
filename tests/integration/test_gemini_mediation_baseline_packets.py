"""Integration revalidation for committed Gemini mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    GEMINI_UNCERTAINTY_PACKET_PATH,
    REPO_ROOT,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._gemini_mediation_baseline_packets import (
    GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
    build_gemini_uncertainty_baseline_packet,
    emit_gemini_mediation_baseline_packets,
)


def test_gemini_uncertainty_baseline_packet_matches_committed_doc() -> None:
    committed_path = REPO_ROOT / GEMINI_UNCERTAINTY_PACKET_PATH
    committed_packet = packet_without_path(parse_run_packet(committed_path))

    assert build_gemini_uncertainty_baseline_packet() == committed_packet


def test_candidate_emitter_prints_all_gemini_baseline_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_gemini_mediation_baseline_packets()
    captured = capsys.readouterr().out

    for relative_path in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS)

    for relative_path, builder in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []

    for line in output.splitlines():
        if line.startswith("--- docs/mediation_evidence/gemini/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs
