"""Build or emit candidate OpenAI mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
import sys

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.openai_host_commitment import evaluate_openai_host_commitment
from tests.integration._reference_lane import host_surface_degradation_pair
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


OPENAI_MEDIATION_BASELINE_PACKET_PATHS = {
    "scenario_uncertainty_openai_01": (
        "docs/mediation_evidence/openai/"
        "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
    ),
}
_OPENAI_UNCERTAINTY_REVIEWER_NOTE = (
    "This is baseline-only committed evidence, not comparative mediation evidence, "
    "and it does not justify mediation or authorize any implementation seam."
)


def build_openai_uncertainty_baseline_packet() -> PacketSnapshot:
    contradiction, degradation = openai_uncertainty_anchor_evidence()
    result = evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_id": "openai-uncertainty-commit-1",
            "session_id": "openai-uncertainty-session-1",
            "externally_consequential": True,
        },
        environment_handle=openai_environment_handle(),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == "openai-uncertainty-commit-1"
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED
    assert result.verdict.provenance_manifest is None
    assert result.verdict.degradation_refs == (degradation,)
    assert contradiction in result.verdict.contradiction_refs

    return build_reference_mediation_packet(
        scenario_id="scenario_uncertainty_openai_01",
        run_id="openai_uncertainty_baseline_run_001",
        paired_episode_set_id="pending_pair_openai_uncertainty_001",
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        host_family="openai",
        scenario_inputs=openai_uncertainty_scenario_inputs(),
        run_outputs={
            "outcome_summary": (
                "The bounded OpenAI-host uncertainty anchor yields an uncertified full-"
                "commitment outcome on `openai-uncertainty-anchor-1` because explicit "
                "contradiction-bearing degraded evidence remains incomplete."
            ),
            "branch_trajectory_summary": (
                "This OpenAI-only uncertainty anchor records no branch-control sequence "
                "and no comparator yet."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit on the uncertified "
                "OpenAI-host commitment outcome; no certified-resolution or packet-"
                "publication comparison is claimed in this baseline anchor."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "OpenAI commitment semantics and the direct commitment-path evidence "
                "surface are exercised without any pooled host claim."
            ),
        },
        artifact_refs={
            "event_trace_refs": "openai-uncertainty-anchor-1:response.completed/uncertified",
            "contradiction_refs": f"{contradiction.source_tag}:{contradiction.summary}",
            "degradation_refs": degradation.reason_code,
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This packet records an OpenAI-only uncertainty anchor without any "
                "branch-control comparison.",
                "Package-level evidence notes govern whether later repeated paired "
                "evidence is enough to claim any thrash change.",
            ),
            "Better Branch Discipline": (
                "This packet stays on the direct OpenAI commitment path and does not "
                "exercise branch control.",
                "Package-level evidence notes govern whether later repeated paired "
                "evidence is enough to claim any branch-discipline effect.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves an uncertified OpenAI-host commitment result "
                "with explicit contradiction and degradation evidence.",
                "Package-level evidence notes govern whether later repeated paired "
                "evidence is enough to claim uncertainty-handling lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only OpenAI uncertainty anchor; no AUX burden artifact is "
                "recorded here.",
                "Package-level evidence notes govern whether later repeated paired "
                "evidence is enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "This packet stays on the landed OpenAI commitment surface while "
                "preserving contradiction-bearing evidence.",
                "Package-level evidence notes govern whether later repeated paired "
                "evidence is enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_openai_uncertainty_001` for a future honest comparison if "
            "one is ever earned."
        ),
        reviewer_note=_OPENAI_UNCERTAINTY_REVIEWER_NOTE,
    )


def openai_uncertainty_scenario_inputs() -> dict[str, str]:
    return {
        "starting_request_or_event": (
            "bounded OpenAI-host `response.completed` flow on "
            "`openai-uncertainty-session-1` with an uncertified full-commitment outcome"
        ),
        "host_surface": (
            "OpenAI observe/bind plus commitment-path slice with contradiction-bearing "
            "degradation preserved on uncertified full commitment"
        ),
        "declared_scenario_goal": (
            "evaluate whether future mediation improves OpenAI-host uncertainty handling "
            "without smoothing contradiction or degradation evidence or changing "
            "commitment truth"
        ),
        "bounded_environment_or_approval_context": (
            "`CommitmentEnvironmentHandle` with "
            "`available_query_kinds={EXECUTION_TRACE}` and "
            "`capability_tags={trace/read}` on `env_uncertainty_sensitive`"
        ),
    }


def openai_uncertainty_anchor_evidence():
    return host_surface_degradation_pair(
        source_tag="openai-trace-check",
        summary="OpenAI approval evidence remains incomplete",
        evidence_tags=frozenset({"openai", "approval-evidence"}),
        reason_code="openai-evidence-partial",
        capability_tags=frozenset({"trace/read"}),
    )


def openai_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )


OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    OPENAI_MEDIATION_BASELINE_PACKET_PATHS["scenario_uncertainty_openai_01"]: (
        build_openai_uncertainty_baseline_packet
    )
}


def emit_openai_mediation_baseline_packets() -> None:
    for relative_path, builder in OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))


if __name__ == "__main__":
    emit_openai_mediation_baseline_packets()
