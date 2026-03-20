"""Integration revalidation for committed reference mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REPO_ROOT,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._reference_mediation_baseline_packets import (
    REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS,
    REFERENCE_MEDIATION_BASELINE_PACKET_PATHS,
    build_reference_host_realization_baseline_packet,
    build_reference_thrash_baseline_packet,
    build_reference_uncertainty_baseline_packet,
    emit_reference_mediation_baseline_packets,
)
from tests.integration._reference_mediation_thrash_episode import (
    EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE,
    build_reference_thrash_episode_snapshot,
)


def test_reference_uncertainty_baseline_packet_matches_committed_doc() -> None:
    committed_path = REPO_ROOT / REFERENCE_MEDIATION_BASELINE_PACKET_PATHS[
        "scenario_uncertainty_reference_01"
    ]
    committed_packet = packet_without_path(parse_run_packet(committed_path))

    assert build_reference_uncertainty_baseline_packet() == committed_packet


def test_reference_host_realization_baseline_packet_matches_committed_doc() -> None:
    committed_path = REPO_ROOT / REFERENCE_MEDIATION_BASELINE_PACKET_PATHS[
        "scenario_host_reference_01"
    ]
    committed_packet = packet_without_path(parse_run_packet(committed_path))

    assert build_reference_host_realization_baseline_packet() == committed_packet


def test_reference_thrash_baseline_packet_matches_committed_doc() -> None:
    committed_path = REPO_ROOT / REFERENCE_MEDIATION_BASELINE_PACKET_PATHS[
        "scenario_thrash_reference_01"
    ]
    committed_packet = packet_without_path(parse_run_packet(committed_path))

    assert build_reference_thrash_baseline_packet() == committed_packet


def test_reference_thrash_episode_derives_expected_branch_sequence() -> None:
    snapshot = build_reference_thrash_episode_snapshot()

    assert snapshot["branch_sequence"] == list(EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE)
    assert [step["derived_branch_operation"] for step in snapshot["steps"]] == list(
        EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE
    )
    assert [step["outcome_class"] for step in snapshot["steps"]] == [
        "candidate-bearing",
        "uncertified-full-commitment",
        "candidate-bearing",
        "certified-full-commitment",
    ]


def test_candidate_emitter_prints_all_three_reference_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_reference_mediation_baseline_packets()
    captured = capsys.readouterr().out

    for relative_path in REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.values())

    for scenario_id, relative_path in REFERENCE_MEDIATION_BASELINE_PACKET_PATHS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS[scenario_id]()


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
