"""Integration revalidation for committed reference mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REPO_ROOT,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._reference_mediation_baseline_packets import (
    REFERENCE_HOST_REALIZATION_BASELINE_PACKET_PATHS,
    REFERENCE_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
    REFERENCE_MEDIATION_BASELINE_PACKET_PATHS,
    REFERENCE_UNCERTAINTY_BASELINE_PACKET_PATHS,
    REFERENCE_THRASH_BASELINE_PACKET_PATHS,
    build_reference_host_realization_baseline_packet,
    build_reference_thrash_baseline_packet,
    build_reference_uncertainty_baseline_packet,
    emit_reference_mediation_baseline_packets,
)
from tests.integration._reference_host_realization_pairs import (
    REFERENCE_HOST_REALIZATION_PAIR_KEYS,
)
from tests.integration._reference_mediation_thrash_episode import (
    EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE,
    REFERENCE_THRASH_PAIR_KEYS,
    build_reference_thrash_episode_snapshot,
)
from tests.integration._reference_mediation_uncertainty_episode import (
    EXPECTED_REFERENCE_UNCERTAINTY_STEP_SEQUENCE,
    REFERENCE_UNCERTAINTY_PAIR_KEYS,
    build_reference_uncertainty_episode_snapshot,
)


def test_reference_uncertainty_baseline_packet_matches_committed_doc() -> None:
    for pair_key in REFERENCE_UNCERTAINTY_PAIR_KEYS:
        committed_path = REPO_ROOT / REFERENCE_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key]
        committed_packet = packet_without_path(parse_run_packet(committed_path))

        assert build_reference_uncertainty_baseline_packet(pair_key) == committed_packet


def test_reference_host_realization_baseline_packet_matches_committed_doc() -> None:
    for pair_key in REFERENCE_HOST_REALIZATION_PAIR_KEYS:
        committed_path = REPO_ROOT / REFERENCE_HOST_REALIZATION_BASELINE_PACKET_PATHS[pair_key]
        committed_packet = packet_without_path(parse_run_packet(committed_path))

        assert build_reference_host_realization_baseline_packet(pair_key) == committed_packet


def test_reference_thrash_baseline_packet_matches_committed_doc() -> None:
    for pair_key in REFERENCE_THRASH_PAIR_KEYS:
        committed_path = REPO_ROOT / REFERENCE_THRASH_BASELINE_PACKET_PATHS[pair_key]
        committed_packet = packet_without_path(parse_run_packet(committed_path))

        assert build_reference_thrash_baseline_packet(pair_key) == committed_packet


def test_reference_uncertainty_episode_derives_expected_step_sequence() -> None:
    for pair_key in REFERENCE_UNCERTAINTY_PAIR_KEYS:
        snapshot = build_reference_uncertainty_episode_snapshot(pair_key)

        assert snapshot["step_sequence"] == list(EXPECTED_REFERENCE_UNCERTAINTY_STEP_SEQUENCE)
        assert snapshot["uncertified_loop_count"] == 2
        assert [step["outcome_class"] for step in snapshot["steps"]] == [
            "uncertified-full-commitment",
            "uncertified-full-commitment",
            "certified-full-commitment",
        ]
        assert [step["selected_soft_control_family"] for step in snapshot["steps"]] == [
            "check",
            "check",
            "check",
        ]


def test_reference_thrash_episode_derives_expected_branch_sequence() -> None:
    for pair_key in REFERENCE_THRASH_PAIR_KEYS:
        snapshot = build_reference_thrash_episode_snapshot(pair_key)

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


def test_candidate_emitter_prints_all_reference_baseline_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_reference_mediation_baseline_packets()
    captured = capsys.readouterr().out

    for relative_path in REFERENCE_MEDIATION_BASELINE_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(REFERENCE_MEDIATION_BASELINE_PACKET_DOC_BUILDERS)

    for relative_path, builder in REFERENCE_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items():
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
