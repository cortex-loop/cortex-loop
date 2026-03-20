"""Integration revalidation for the first reference-only mediated host-realization pair."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REPO_ROOT,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._reference_mediated_lane_packet_example import (
    build_reference_host_realization_specialization_snapshot,
)
from tests.integration._reference_mediation_baseline_packets import (
    REFERENCE_MEDIATION_BASELINE_PACKET_PATHS,
    build_reference_host_realization_baseline_packet,
)
from tests.integration._reference_mediation_host_realization_experimental import (
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS,
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH,
    build_reference_host_realization_comparator_snapshot,
    build_reference_host_realization_mediated_packet,
    emit_reference_mediated_host_realization_candidate,
)


def test_reference_host_realization_mediated_packet_matches_committed_doc() -> None:
    committed_packet = packet_without_path(
        parse_run_packet(REPO_ROOT / REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH)
    )

    assert build_reference_host_realization_mediated_packet() == committed_packet


def test_reference_host_realization_pair_remains_fair_and_changes_only_specialization() -> None:
    baseline_packet = build_reference_host_realization_baseline_packet()
    mediated_packet = build_reference_host_realization_mediated_packet()
    baseline_specialization = build_reference_host_realization_specialization_snapshot(
        clearly_superior=False,
    )
    mediated_specialization = build_reference_host_realization_specialization_snapshot(
        clearly_superior=True,
    )
    comparator = build_reference_host_realization_comparator_snapshot()

    assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
    assert baseline_packet["header"]["paired_episode_set_id"] == "pair_reference_host_001"
    assert mediated_packet["header"]["paired_episode_set_id"] == "pair_reference_host_001"
    assert baseline_packet["variant_metadata"]["host_family"] == "reference"
    assert baseline_packet["variant_metadata"] == mediated_packet["variant_metadata"] | {
        "variant": "baseline_non_mediated"
    }
    assert baseline_packet["scenario_inputs"] == mediated_packet["scenario_inputs"]
    assert baseline_packet["invariant_lock"] == mediated_packet["invariant_lock"]
    assert comparator["selected_family"] == "seek-context"
    assert comparator["host_opportunity_refs"] == ["mcp.query"]
    assert comparator["baseline_direct_opportunity_specialization_used"] == 0
    assert comparator["mediated_direct_opportunity_specialization_used"] == 1
    assert baseline_specialization["preferred_opportunity_ref"] is None
    assert mediated_specialization["preferred_opportunity_ref"] == "mcp.query"
    assert baseline_specialization["direct_opportunity_specialization_used"] is False
    assert mediated_specialization["direct_opportunity_specialization_used"] is True
    assert comparator["baseline_packet_kind"] == "current-pair"
    assert comparator["mediated_packet_kind"] == "current-pair"
    assert comparator["baseline_verdict_status"] == "certified"
    assert comparator["mediated_verdict_status"] == "certified"


def test_reference_host_realization_mediated_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_reference_mediated_host_realization_candidate()
    captured = capsys.readouterr().out

    assert f"--- {REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == {REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH}

    for relative_path, builder in REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


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
