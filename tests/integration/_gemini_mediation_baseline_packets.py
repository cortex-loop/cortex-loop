"""Build or emit candidate Gemini mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
import sys

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.gemini_host_commitment import evaluate_gemini_host_commitment
from tests.integration._reference_lane import host_surface_degradation_pair
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


GEMINI_MEDIATION_BASELINE_PACKET_PATHS = {
    "scenario_uncertainty_gemini_01": (
        "docs/mediation_evidence/gemini/"
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md"
    ),
}
_GEMINI_UNCERTAINTY_REVIEWER_NOTE = (
    "This is baseline-only committed evidence, not comparative mediation evidence, "
    "and it does not justify mediation or authorize any implementation seam."
)


def build_gemini_uncertainty_baseline_packet() -> PacketSnapshot:
    contradiction, degradation = host_surface_degradation_pair(
        source_tag="gemini-trace-check",
        summary="Gemini approval evidence remains incomplete",
        evidence_tags=frozenset({"gemini", "approval-evidence"}),
        reason_code="gemini-evidence-partial",
        capability_tags=frozenset({"trace/read"}),
    )
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": "gemini-uncertainty-commit-1",
            "session_id": "gemini-uncertainty-session-1",
            "externally_consequential": True,
        },
        environment_handle=CommitmentEnvironmentHandle(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            capability_tags=frozenset({"trace/read"}),
        ),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == "gemini-uncertainty-commit-1"
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED
    assert contradiction in result.verdict.contradiction_refs
    assert degradation in result.verdict.degradation_refs

    return build_reference_mediation_packet(
        scenario_id="scenario_uncertainty_gemini_01",
        run_id="gemini_uncertainty_baseline_run_001",
        paired_episode_set_id="pending_pair_gemini_uncertainty_001",
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        host_family="gemini",
        scenario_inputs={
            "starting_request_or_event": (
                "`interaction.complete` with "
                "`commitment_id=gemini-uncertainty-commit-1` and "
                "`session_id=gemini-uncertainty-session-1`"
            ),
            "host_surface": (
                "Gemini observe/bind plus commitment-path slice with "
                "contradiction-bearing degradation preserved on an uncertified "
                "full-commitment outcome"
            ),
            "declared_scenario_goal": (
                "establish the first lawful non-reference uncertainty baseline anchor "
                "without adding a Gemini mediated comparator yet"
            ),
            "bounded_environment_or_approval_context": (
                "`CommitmentEnvironmentHandle` with "
                "`available_query_kinds={EXECUTION_TRACE}` and "
                "`capability_tags={trace/read}` on `env_uncertainty_sensitive`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The bounded Gemini-host uncertainty anchor reaches an uncertified "
                "full-commitment outcome on the landed commitment path."
            ),
            "branch_trajectory_summary": (
                "Single Gemini full-commitment anchor only; no branch-control comparison "
                "is recorded in this baseline packet."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit on the uncertified "
                "Gemini verdict; no mediated comparator or retry loop is counted here."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Gemini observe/bind and commitment semantics are exercised without "
                "claiming any host-specialized lift or pooled host result."
            ),
        },
        artifact_refs={
            "event_trace_refs": "gemini-uncertainty-anchor-1:interaction.complete/uncertified",
            "contradiction_refs": "gemini-trace-check:Gemini approval evidence remains incomplete",
            "degradation_refs": "gemini-evidence-partial",
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "Baseline-only Gemini uncertainty anchor; no matched mediated run is recorded.",
                "No branch-control comparison exists for this Gemini cell yet.",
            ),
            "Better Branch Discipline": (
                "Baseline-only Gemini uncertainty anchor; no matched mediated run is recorded.",
                "No comparative branch-discipline evidence exists for this Gemini cell yet.",
            ),
            "Better Uncertainty Handling": (
                "This Gemini baseline anchor preserves an explicit uncertified verdict "
                "together with contradiction and degradation records.",
                "One committed Gemini baseline packet does not establish comparative "
                "uncertainty lift by itself.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only Gemini uncertainty anchor; no equal-value burden comparison is recorded.",
                "No committed AUX burden artifact exists for this Gemini anchor.",
            ),
            "Better Host-Specialized Realization": (
                "This Gemini anchor exercises Gemini-native commitment semantics without "
                "claiming any mediated host-realization lift.",
                "Host-specialized realization remains descriptive only until a lawful "
                "matched mediated comparator exists.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_gemini_uncertainty_001` for a future honest Gemini "
            "comparison if one is ever earned."
        ),
        reviewer_note=_GEMINI_UNCERTAINTY_REVIEWER_NOTE,
    )


GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    GEMINI_MEDIATION_BASELINE_PACKET_PATHS["scenario_uncertainty_gemini_01"]: (
        build_gemini_uncertainty_baseline_packet
    )
}


def emit_gemini_mediation_baseline_packets() -> None:
    for index, (relative_path, builder) in enumerate(
        GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items()
    ):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))
        if index != len(GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS) - 1:
            sys.stdout.write("\n")


if __name__ == "__main__":
    emit_gemini_mediation_baseline_packets()
