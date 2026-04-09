"""Build or emit candidate Claude mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
import sys

from cortex.core.dispatch import DispatchLane
from tests.integration._claude_host_realization_pair import (
    CLAUDE_HOST_REALIZATION_PAIR_KEYS,
    CLAUDE_HOST_REALIZATION_PAIR_SPECS,
    DEFAULT_CLAUDE_HOST_REALIZATION_PAIR_KEY,
)
from tests.integration._claude_lane_packet_example import (
    build_claude_lane_packet_example_snapshot,
)
from tests.integration._claude_mediated_lane_packet_example import (
    build_claude_host_realization_specialization_snapshot,
)
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


_CLAUDE_HOST_REALIZATION_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed Claude "
    "host-realization paired-run series. It is not comparative mediation evidence by "
    "itself, does not justify mediation, and package-level evidence notes govern any "
    "verdict."
)


def build_claude_host_realization_baseline_packet(
    pair_key: str = DEFAULT_CLAUDE_HOST_REALIZATION_PAIR_KEY,
) -> PacketSnapshot:
    spec = CLAUDE_HOST_REALIZATION_PAIR_SPECS[pair_key]
    snapshot = build_claude_lane_packet_example_snapshot(pair_key)
    specialization = build_claude_host_realization_specialization_snapshot(
        clearly_superior=False,
    )

    assert snapshot["dispatch_lanes"] == {
        "candidate": DispatchLane.CANDIDATE_BEARING.value,
        "publication": DispatchLane.FULL_COMMITMENT.value,
    }
    assert snapshot["candidate_id"] == spec.commitment_id
    assert snapshot["verdict_status"] == "certified"
    assert snapshot["packet_kind"] == "current-pair"
    assert specialization["selected_family"] == "seek-context"
    assert specialization["preferred_opportunity_ref"] is None
    assert specialization["direct_opportunity_specialization_used"] is False
    assert specialization["host_opportunity_refs"] == ["mcp.query"]

    candidate_event = snapshot["candidate_event"]
    publication_event = snapshot["publication_event"]
    event_trace = snapshot["event_trace"]
    contradiction_refs = snapshot["contradiction_refs"]
    degradation_refs = snapshot["degradation_refs"]

    assert isinstance(candidate_event, dict)
    assert isinstance(publication_event, dict)
    assert isinstance(event_trace, dict)
    assert isinstance(contradiction_refs, list)
    assert isinstance(degradation_refs, list)
    contradiction_ref = contradiction_refs[0]
    degradation_ref = degradation_refs[0]
    assert isinstance(contradiction_ref, dict)
    assert isinstance(degradation_ref, dict)

    return build_reference_mediation_packet(
        scenario_id="scenario_host_claude_01",
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        host_family="claude",
        scenario_inputs={
            "starting_request_or_event": (
                f"`content_block_delta` candidate-bearing turn on `{spec.session_id}` "
                f"followed by `message_stop` with `commitment_id={spec.commitment_id}`"
            ),
            "host_surface": (
                "Claude-host opportunity selection plus candidate-bearing continuation "
                "and commitment-to-eval-packet publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation produces any Claude-host realization lift "
                "without adding burden or branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "Claude-host candidate-bearing plus commitment/publication path with "
                "lawful provenance, contradiction-preserving degradation handling, the "
                "committed Claude-lane packet/publication surface, and a bounded "
                "host-opportunity set containing `mcp.query`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The baseline Claude-host path preserves the same certified current-pair "
                "evaluation packet with explicit contradiction, degradation, and "
                "truthful-withheld fields while retaining the generic `seek-context` "
                "family without direct host-native specialization."
            ),
            "branch_trajectory_summary": (
                "One Claude-native candidate-bearing turn is followed by one "
                "full-commitment publication path only; the comparator delta for this "
                "pair is the host-opportunity realization choice, not a branch-sequence "
                "change."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed Claude "
                "packet example, and `direct_opportunity_specialization_used=0` remains "
                "explicit for the baseline side of the pair."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Claude-host realization retains the selected family `seek-context` "
                "with `direct_opportunity_specialization_used=0` while preserving the "
                "same host-opportunity set containing `mcp.query` and the same "
                "certified `current-pair` publication surface."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(event_trace["trace_id"]),
            "contradiction_refs": (
                f"{contradiction_ref['source_tag']}:{contradiction_ref['summary']}"
            ),
            "degradation_refs": str(degradation_ref["reason_code"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "docs/experimental/CORTEX_V2_CLAUDE_LANE_PACKET_EXAMPLE_0.md",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This baseline packet is part of the committed Claude host-realization "
                "paired-run series, but it is not a branch-control comparison.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any thrash verdict.",
            ),
            "Better Branch Discipline": (
                "This baseline packet changes no branch trajectory and records no "
                "branch-control lift by itself.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any branch-discipline verdict.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves contradiction and degradation explicitly on the "
                "same certified publication surface used by the comparator.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any uncertainty-handling verdict.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "The pair holds the same certified completion class and truth boundary, "
                "but this packet carries no AUX burden artifact.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any lower-burden verdict.",
            ),
            "Better Host-Specialized Realization": (
                "This baseline packet preserves the same Claude `current-pair` "
                "publication surface without direct host-native specialization.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any host-specialized realization verdict.",
            ),
        },
        exclusion_notes=(
            f"This packet is the baseline side of `{spec.pair_id}`. A single packet "
            "does not justify mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_CLAUDE_HOST_REALIZATION_REVIEWER_NOTE,
    )


CLAUDE_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: CLAUDE_HOST_REALIZATION_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in CLAUDE_HOST_REALIZATION_PAIR_KEYS
}
CLAUDE_HOST_REALIZATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    CLAUDE_HOST_REALIZATION_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_claude_host_realization_baseline_packet, pair_key
    )
    for pair_key in CLAUDE_HOST_REALIZATION_PAIR_KEYS
}


def emit_claude_mediation_baseline_packets() -> None:
    for index, (relative_path, builder) in enumerate(
        CLAUDE_HOST_REALIZATION_BASELINE_PACKET_DOC_BUILDERS.items()
    ):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))
        if index != len(CLAUDE_HOST_REALIZATION_BASELINE_PACKET_DOC_BUILDERS) - 1:
            sys.stdout.write("\n")


if __name__ == "__main__":
    emit_claude_mediation_baseline_packets()
