"""Integration revalidation for the first reference-only mediated thrash comparator."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REFERENCE_THRASH_MEDIATED_PACKET_PATH,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._reference_mediation_baseline_packets import (
    build_reference_thrash_baseline_packet,
)
from tests.integration._reference_mediation_thrash_episode import (
    EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE,
    build_reference_thrash_episode_snapshot,
)
from tests.integration._reference_mediation_thrash_experimental import (
    EXPERIMENTAL_REFERENCE_THRASH_BRANCH_SEQUENCE,
    REFERENCE_THRASH_MEDIATED_PACKET_PATH as EMITTED_THRASH_PACKET_PATH,
    build_reference_mediated_thrash_episode_snapshot,
    build_reference_thrash_mediated_packet,
    emit_reference_mediated_thrash_candidate,
)


def test_reference_thrash_mediated_packet_matches_committed_doc() -> None:
    committed_packet = packet_without_path(parse_run_packet(REFERENCE_THRASH_MEDIATED_PACKET_PATH))

    assert build_reference_thrash_mediated_packet() == committed_packet


def test_reference_thrash_mediated_pair_remains_fair_and_reduces_branch_ops() -> None:
    baseline_packet = build_reference_thrash_baseline_packet()
    mediated_packet = build_reference_thrash_mediated_packet()
    baseline_snapshot = build_reference_thrash_episode_snapshot()
    mediated_snapshot = build_reference_mediated_thrash_episode_snapshot()

    assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
    assert baseline_packet["header"]["paired_episode_set_id"] == "pair_reference_thrash_001"
    assert mediated_packet["header"]["paired_episode_set_id"] == "pair_reference_thrash_001"
    assert baseline_packet["variant_metadata"]["host_family"] == mediated_packet["variant_metadata"]["host_family"]
    assert baseline_packet["variant_metadata"]["scenario_family"] == mediated_packet["variant_metadata"]["scenario_family"]
    assert (
        baseline_packet["variant_metadata"]["task_value_rubric_id"]
        == mediated_packet["variant_metadata"]["task_value_rubric_id"]
    )
    assert (
        baseline_packet["variant_metadata"]["approval_or_environment_context_id"]
        == mediated_packet["variant_metadata"]["approval_or_environment_context_id"]
    )
    assert baseline_packet["scenario_inputs"] == mediated_packet["scenario_inputs"]
    assert baseline_packet["invariant_lock"] == mediated_packet["invariant_lock"]

    assert baseline_snapshot["branch_sequence"] == list(EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE)
    assert mediated_snapshot["branch_sequence"] == list(
        EXPERIMENTAL_REFERENCE_THRASH_BRANCH_SEQUENCE
    )
    assert len(mediated_snapshot["branch_sequence"]) < len(baseline_snapshot["branch_sequence"])
    assert baseline_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
    assert mediated_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
    assert baseline_snapshot["steps"][1]["brake_state"] == "guarded"
    assert mediated_snapshot["steps"][1]["brake_state"] == "guarded"


def test_reference_thrash_mediated_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_reference_mediated_thrash_candidate()
    captured = capsys.readouterr().out

    assert f"--- {EMITTED_THRASH_PACKET_PATH}" in captured
    temp_doc = tmp_path / Path(EMITTED_THRASH_PACKET_PATH).name
    temp_doc.write_text(captured.split("\n", 1)[1], encoding="utf-8")

    emitted_packet = packet_without_path(parse_run_packet(temp_doc))
    assert emitted_packet == build_reference_thrash_mediated_packet()
