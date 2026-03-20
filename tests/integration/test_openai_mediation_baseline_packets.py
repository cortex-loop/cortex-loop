"""Integration revalidation for committed OpenAI mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    OPENAI_UNCERTAINTY_PACKET_PATH,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._openai_mediation_baseline_packets import (
    OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
    OPENAI_MEDIATION_BASELINE_PACKET_PATHS,
    build_openai_uncertainty_baseline_packet,
    emit_openai_mediation_baseline_packets,
)


def test_openai_uncertainty_baseline_packet_matches_committed_doc() -> None:
    committed_packet = packet_without_path(parse_run_packet(OPENAI_UNCERTAINTY_PACKET_PATH))
    assert build_openai_uncertainty_baseline_packet() == committed_packet


def test_candidate_emitter_prints_openai_baseline_packet_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_openai_mediation_baseline_packets()
    captured = capsys.readouterr().out

    relative_path = OPENAI_MEDIATION_BASELINE_PACKET_PATHS["scenario_uncertainty_openai_01"]
    assert f"--- {relative_path}" in captured

    temp_doc = tmp_path / Path(relative_path).name
    temp_doc.write_text(_parse_emitted_doc(captured), encoding="utf-8")
    emitted_packet = packet_without_path(parse_run_packet(temp_doc))
    assert emitted_packet == OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS[relative_path]()


def _parse_emitted_doc(output: str) -> str:
    prefix = (
        "--- "
        "docs/mediation_evidence/openai/"
        "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
    )
    lines = output.splitlines()
    assert lines[0] == prefix
    return "\n".join(lines[1:]).strip() + "\n"
