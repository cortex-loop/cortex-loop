"""Build or emit the experimental Gemini-host mediated uncertainty comparators."""

from __future__ import annotations

from functools import partial
import sys

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.drivers.gemini_host_commitment import evaluate_gemini_host_commitment
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from tests.archive.legacy_integration._gemini_mediation_uncertainty_episode import (
    DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY,
    GEMINI_UNCERTAINTY_PAIR_KEYS,
    GEMINI_UNCERTAINTY_PAIR_SPECS,
    build_gemini_uncertainty_episode_snapshot,
    gemini_environment_handle,
    gemini_uncertainty_pair_evidence,
    gemini_uncertainty_scenario_inputs,
)
from tests.conformance.integration._reference_lane import provenance_manifest_for
from tests.archive.legacy_integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATH = GEMINI_UNCERTAINTY_PAIR_SPECS[
    DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY
].mediated_packet_path
GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS = {
    pair_key: GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
}
EXPERIMENTAL_GEMINI_UNCERTAINTY_STEP_SEQUENCE = ("guard", "resolve")
_REVIEWER_NOTE = (
    "This is experimental mediated evidence only within the committed Gemini "
    "uncertainty paired-run series. It remains Gemini-only, does not justify "
    "mediation, and package-level evidence notes govern any verdict."
)


def build_gemini_mediated_uncertainty_episode_snapshot(
    pair_key: str = DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY,
) -> dict[str, object]:
    spec = GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key]
    baseline_snapshot = build_gemini_uncertainty_episode_snapshot(pair_key)
    baseline_steps = baseline_snapshot["steps"]
    assert isinstance(baseline_steps, list)
    assert baseline_snapshot["step_sequence"] == ["guard", "retry", "resolve"]

    shared_guard_step = {
        **baseline_steps[0],
        "step_id": f"{spec.mediated_step_prefix}-1",
    }
    resolve_step = _build_resolve_step(spec)

    steps = [shared_guard_step, resolve_step]
    return {
        "scenario_id": "scenario_uncertainty_gemini_01",
        "run_id": spec.mediated_run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "contradiction_ref": str(baseline_snapshot["contradiction_ref"]),
        "degradation_ref": str(baseline_snapshot["degradation_ref"]),
        "uncertainty_spike_tag": spec.uncertainty_spike_tag,
        "step_sequence": list(EXPERIMENTAL_GEMINI_UNCERTAINTY_STEP_SEQUENCE),
        "uncertified_loop_count": 1,
        "event_trace_refs": ", ".join(
            (
                f"{spec.mediated_step_prefix}-1:interaction.complete/guard",
                f"{spec.mediated_step_prefix}-2:interaction.complete/resolve",
            )
        ),
        "steps": steps,
    }


def build_gemini_uncertainty_mediated_packet(
    pair_key: str = DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY,
) -> PacketSnapshot:
    spec = GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key]
    snapshot = build_gemini_mediated_uncertainty_episode_snapshot(pair_key)
    steps = snapshot["steps"]

    assert isinstance(steps, list)
    assert snapshot["step_sequence"] == list(EXPERIMENTAL_GEMINI_UNCERTAINTY_STEP_SEQUENCE)
    assert snapshot["uncertified_loop_count"] == 1
    assert [step["outcome_class"] for step in steps] == [
        "uncertified-full-commitment",
        "certified-full-commitment",
    ]
    assert steps[0]["brake_state"] == BrakeState.GUARDED.value
    assert steps[1]["dispatch_lane"] == DispatchLane.FULL_COMMITMENT.value

    return build_reference_mediation_packet(
        scenario_id="scenario_uncertainty_gemini_01",
        run_id=spec.mediated_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        variant="experimental_mediated",
        host_family="gemini",
        scenario_inputs=gemini_uncertainty_scenario_inputs(spec),
        run_outputs={
            "outcome_summary": (
                "The experimental mediated comparator reaches the same certified "
                f"Gemini-host completion class at `{spec.mediated_step_prefix}-2` "
                "after one guarded uncertified follow-up."
            ),
            "branch_trajectory_summary": (
                "This Gemini-only experimental comparator derives `guard -> resolve`, "
                "removing the redundant uncertified retry step present in the baseline "
                "while preserving certified resolution."
            ),
            "uncertainty_or_brake_summary": (
                "The guarded uncertified state remains explicit at "
                f"`{spec.mediated_step_prefix}-1`, contradiction/degradation evidence "
                f"remains explicit, and certification still requires lawful provenance at "
                f"`{spec.mediated_step_prefix}-2`."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "The comparator remains Gemini-only and preserves the same Gemini "
                "commitment, contradiction, degradation, and direct commitment-path "
                "evidence surface as its matched baseline."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(snapshot["event_trace_refs"]),
            "contradiction_refs": str(snapshot["contradiction_ref"]),
            "degradation_refs": str(snapshot["degradation_ref"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This experimental Gemini-only uncertainty packet preserves the same "
                "Gemini uncertainty surface without adding branch behavior.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any thrash change.",
            ),
            "Better Branch Discipline": (
                "This uncertainty comparator keeps the same `check`-family surface and "
                "does not add branch-family intervention.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any branch-discipline effect.",
            ),
            "Better Uncertainty Handling": (
                "This experimental Gemini-only comparator preserves the same guarded "
                "uncertified state and contradiction-bearing evidence while removing one "
                "redundant uncertified loop before certified resolution.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim uncertainty-handling lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Equal certified resolution is preserved and no AUX burden artifact is "
                "recorded within this packet.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "The comparator stays Gemini-only and contradiction-preserving within "
                "the committed uncertainty paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This experimental mediated packet is part of the committed Gemini "
            f"uncertainty paired-run series under `{spec.pair_id}`. A single packet does "
            "not justify mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_REVIEWER_NOTE,
    )


GEMINI_UNCERTAINTY_MEDIATED_PACKET_DOC_BUILDERS = {
    GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS[pair_key]: partial(
        build_gemini_uncertainty_mediated_packet, pair_key
    )
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
}


def emit_gemini_mediated_uncertainty_candidate() -> None:
    for relative_path, builder in GEMINI_UNCERTAINTY_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))


def _build_resolve_step(spec) -> dict[str, object]:
    contradiction, degradation = gemini_uncertainty_pair_evidence(spec)
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": spec.commitment_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=gemini_environment_handle(),
        provenance_manifest=provenance_manifest_for(spec.provenance_artifact_id),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == spec.commitment_id
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED
    assert result.verdict.degradation_refs == (degradation,)
    assert contradiction in result.verdict.contradiction_refs

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, spec.resolve_check_score),
                AllocationScore(SoftControlFamily.BRANCH, spec.resolve_branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    return {
        "step_id": f"{spec.mediated_step_prefix}-2",
        "host_event_name": "interaction.complete",
        "payload_identity": (
            f"commitment_id={spec.commitment_id}, externally_consequential=True, "
            f"session_id={spec.session_id}"
        ),
        "dispatch_lane": result.dispatch_decision.lane.value,
        "selected_soft_control_family": decision.selected_family.value,
        "brake_state": brake.state.value,
        "contradiction_ref": f"{contradiction.source_tag}:{contradiction.summary}",
        "degradation_ref": degradation.reason_code,
        "outcome_class": "certified-full-commitment",
    }


if __name__ == "__main__":
    emit_gemini_mediated_uncertainty_candidate()
