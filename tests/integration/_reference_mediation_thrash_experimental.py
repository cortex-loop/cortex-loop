"""Build or emit the experimental reference-host mediated thrash comparator."""

from __future__ import annotations

import sys

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from tests.integration._reference_lane import (
    provenance_manifest_for,
    reference_environment_handle,
)
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)
from tests.integration._reference_mediation_thrash_episode import (
    build_reference_thrash_episode_snapshot,
)


REFERENCE_THRASH_MEDIATED_PACKET_PATH = (
    "docs/mediation_evidence/reference/"
    "scenario_thrash_reference_01__experimental_mediated__run_001.md"
)
EXPERIMENTAL_REFERENCE_THRASH_BRANCH_SEQUENCE = ("open", "suspend", "merge")
_REVIEWER_NOTE = (
    "This is experimental mediated evidence only, remains reference-only, and one paired "
    "run is not enough to justify mediation or authorize any implementation seam."
)


def build_reference_mediated_thrash_episode_snapshot() -> dict[str, object]:
    baseline_snapshot = build_reference_thrash_episode_snapshot()
    baseline_steps = baseline_snapshot["steps"]
    assert isinstance(baseline_steps, list)
    assert baseline_snapshot["branch_sequence"] == ["open", "suspend", "resume", "merge"]

    shared_open_step = {
        **baseline_steps[0],
        "step_id": "thrash-mediated-step-1",
    }
    shared_suspend_step = {
        **baseline_steps[1],
        "step_id": "thrash-mediated-step-2",
    }
    merge_step = _build_merge_step()

    steps = [shared_open_step, shared_suspend_step, merge_step]
    branch_sequence = _derive_branch_sequence(steps)

    return {
        "scenario_id": "scenario_thrash_reference_01",
        "run_id": "reference_thrash_mediated_run_001",
        "paired_episode_set_id": "pair_reference_thrash_001",
        "session_id": "thrash-session-1",
        "candidate_id": "candidate-thrash-1",
        "commitment_id": "thrash-commit-1",
        "branch_sequence": list(branch_sequence),
        "event_trace_refs": ", ".join(
            f"{step['step_id']}:{step['host_event_name']}/{operation}"
            for step, operation in zip(steps, branch_sequence, strict=True)
        ),
        "steps": [
            {
                **step,
                "derived_branch_operation": operation,
            }
            for step, operation in zip(steps, branch_sequence, strict=True)
        ],
    }


def build_reference_thrash_mediated_packet() -> PacketSnapshot:
    snapshot = build_reference_mediated_thrash_episode_snapshot()
    steps = snapshot["steps"]

    assert isinstance(steps, list)
    assert snapshot["branch_sequence"] == list(EXPERIMENTAL_REFERENCE_THRASH_BRANCH_SEQUENCE)
    assert [step["outcome_class"] for step in steps] == [
        "candidate-bearing",
        "uncertified-full-commitment",
        "certified-full-commitment",
    ]
    assert steps[1]["brake_state"] == BrakeState.GUARDED.value
    assert steps[2]["dispatch_lane"] == DispatchLane.FULL_COMMITMENT.value

    return build_reference_mediation_packet(
        scenario_id="scenario_thrash_reference_01",
        run_id="reference_thrash_mediated_run_001",
        paired_episode_set_id="pair_reference_thrash_001",
        scenario_family="thrash_control",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
        variant="experimental_mediated",
        scenario_inputs={
            "starting_request_or_event": (
                "bounded reference-host approval flow on `thrash-session-1` with repeated "
                "candidate-bearing follow-up before final certified completion"
            ),
            "host_surface": (
                "reference-host commitment path plus landed SRE goal, brake, allocation, "
                "and core support-session surfaces"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation reduces repeated branch reopen or resume "
                "cycles on a bounded multi-step reference-host episode without reducing "
                "lawful task completion"
            ),
            "bounded_environment_or_approval_context": (
                "`CommitmentEnvironmentHandle` with "
                "`available_query_kinds={EXECUTION_TRACE}` and "
                "`capability_tags={trace/read}` on `env_local_default`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The experimental mediated comparator reaches the same certified "
                "reference-host completion class at `thrash-mediated-step-3` after one "
                "guarded uncertified follow-up."
            ),
            "branch_trajectory_summary": (
                "The experimental comparator derives `open -> suspend -> merge`, removing "
                "the extra `resume` step present in the baseline while preserving "
                "certified completion."
            ),
            "uncertainty_or_brake_summary": (
                "The guarded uncertified intermediate state remains explicit at "
                "`thrash-mediated-step-2`; certification still requires lawful provenance "
                "at `thrash-mediated-step-3`."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "The comparator remains reference-only and preserves the same reference-host "
                "commitment boundary and support-session evidence surface."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(snapshot["event_trace_refs"]),
            "contradiction_refs": "none",
            "degradation_refs": "none",
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This experimental reference-only pair preserves certified completion with "
                "a shorter branch sequence than baseline, but only one pair is recorded.",
                "One paired run is not enough to claim thrash reduction.",
            ),
            "Better Branch Discipline": (
                "This experimental reference-only pair avoids the extra branch `resume` "
                "step while keeping the same completion class, but only one pair exists.",
                "One paired run is not enough to claim branch-discipline lift.",
            ),
            "Better Uncertainty Handling": (
                "The guarded uncertified intermediate state remains explicit, but only one "
                "paired run exists.",
                "One paired run is not enough to claim uncertainty-handling lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Equal certified completion is preserved and no AUX burden artifact is "
                "recorded, but only one paired run exists.",
                "One paired run is not enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "The comparator stays reference-only and host-split, but only one paired "
                "run exists.",
                "One paired run is not enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This experimental mediated packet is paired with the committed baseline "
            "reference thrash packet under `pair_reference_thrash_001`; one pair is not "
            "enough to justify any mediation verdict."
        ),
        reviewer_note=_REVIEWER_NOTE,
    )


def emit_reference_mediated_thrash_candidate() -> None:
    sys.stdout.write(f"--- {REFERENCE_THRASH_MEDIATED_PACKET_PATH}\n")
    sys.stdout.write(
        render_reference_mediation_packet(
            REFERENCE_THRASH_MEDIATED_PACKET_PATH,
            build_reference_thrash_mediated_packet(),
        )
    )


def _build_merge_step() -> dict[str, object]:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "thrash-commit-1",
            "session_id": "thrash-session-1",
            "externally_consequential": True,
        },
        environment_handle=reference_environment_handle(),
        provenance_manifest=provenance_manifest_for("artifact-thrash-1"),
    )
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.12),
                AllocationScore(SoftControlFamily.BRANCH, 0.9),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    return {
        "step_id": "thrash-mediated-step-3",
        "host_event_name": "ApprovalResult",
        "payload_identity": (
            "commitment_id=thrash-commit-1, externally_consequential=True, "
            "session_id=thrash-session-1"
        ),
        "dispatch_lane": result.dispatch_decision.lane.value,
        "selected_soft_control_family": decision.selected_family.value,
        "brake_state": brake.state.value,
        "goal_continuity_view": {
            "main_goal_ref": "goal-thrash-main",
            "active_track_ref": "main",
            "pending_goal_refs": [],
            "resume_anchor_available": True,
        },
        "support_session_snapshot": {
            "branch_registry": ["main"],
            "pending_goal_refs": [],
            "budget_history": ["budget/branch", "budget/check", "budget/check"],
            "brake_history": ["quiescent", "guarded", "quiescent"],
            "wake_counters": {"candidate-bearing": 1},
            "reminders": [],
        },
        "outcome_class": "certified-full-commitment",
    }


def _derive_branch_sequence(steps: list[dict[str, object]]) -> tuple[str, ...]:
    previous_goal = {
        "active_track_ref": "main",
        "resume_anchor_available": True,
    }
    previous_branches = {"main"}
    operations: list[str] = []

    for step in steps:
        current_goal = step["goal_continuity_view"]
        current_session = step["support_session_snapshot"]
        current_branches = set(current_session["branch_registry"])
        selected_family = step["selected_soft_control_family"]
        outcome_class = step["outcome_class"]

        if (
            any(branch != "main" and branch not in previous_branches for branch in current_branches)
            and selected_family == "branch"
        ):
            operations.append("open")
        elif (
            previous_goal["active_track_ref"] not in (None, "main")
            and current_goal["active_track_ref"] == "main"
            and previous_goal["active_track_ref"] in current_branches
        ):
            operations.append("suspend")
        elif (
            any(branch != "main" and branch not in current_branches for branch in previous_branches)
            and outcome_class == "certified-full-commitment"
        ):
            operations.append("merge")
        else:
            raise AssertionError(f"Could not derive branch operation for {step['step_id']}.")

        previous_goal = current_goal
        previous_branches = current_branches

    assert tuple(operations) == EXPERIMENTAL_REFERENCE_THRASH_BRANCH_SEQUENCE
    return tuple(operations)


if __name__ == "__main__":
    emit_reference_mediated_thrash_candidate()
