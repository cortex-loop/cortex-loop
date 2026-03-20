"""Build or emit candidate Gemini mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
import sys

from cortex.core.dispatch import DispatchLane
from tests.integration._gemini_mediation_uncertainty_episode import (
    DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY,
    GEMINI_UNCERTAINTY_PAIR_KEYS,
    GEMINI_UNCERTAINTY_PAIR_SPECS,
    build_gemini_uncertainty_episode_snapshot,
    gemini_uncertainty_scenario_inputs,
)
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


GEMINI_MEDIATION_BASELINE_PACKET_PATHS = {
    "scenario_uncertainty_gemini_01": (
        GEMINI_UNCERTAINTY_PAIR_SPECS[
            DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY
        ].baseline_packet_path
    ),
}
GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
}
_GEMINI_UNCERTAINTY_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed Gemini "
    "uncertainty paired-run series. It is not comparative mediation evidence by "
    "itself and does not justify mediation or authorize any implementation seam."
)


def build_gemini_uncertainty_baseline_packet(
    pair_key: str = DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY,
) -> PacketSnapshot:
    spec = GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key]
    snapshot = build_gemini_uncertainty_episode_snapshot(pair_key)
    steps = snapshot["steps"]

    assert isinstance(steps, list)
    assert snapshot["step_sequence"] == ["guard", "retry", "resolve"]
    assert snapshot["uncertified_loop_count"] == 2
    assert [step["outcome_class"] for step in steps] == [
        "uncertified-full-commitment",
        "uncertified-full-commitment",
        "certified-full-commitment",
    ]
    assert steps[0]["brake_state"] == "guarded"
    assert steps[1]["brake_state"] == "guarded"
    assert steps[2]["dispatch_lane"] == DispatchLane.FULL_COMMITMENT.value

    return build_reference_mediation_packet(
        scenario_id="scenario_uncertainty_gemini_01",
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        host_family="gemini",
        scenario_inputs=gemini_uncertainty_scenario_inputs(spec),
        run_outputs={
            "outcome_summary": (
                "The bounded Gemini-host uncertainty episode reaches certified "
                f"completion at `{spec.baseline_step_prefix}-3` after two guarded "
                "uncertified full-commitment turns."
            ),
            "branch_trajectory_summary": (
                "This Gemini-only uncertainty series stays on a `check`-family path "
                "and records no branch-control sequence."
            ),
            "uncertainty_or_brake_summary": (
                f"`guarded` brake state is explicit at `{spec.baseline_step_prefix}-1` "
                f"and `{spec.baseline_step_prefix}-2`, with contradiction and "
                f"degradation evidence preserved until certified resolution at "
                f"`{spec.baseline_step_prefix}-3`."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Gemini commitment semantics, contradiction-bearing evidence, and the "
                "same certified-resolution truth boundary are preserved."
            ),
        },
        artifact_refs={
            "event_trace_refs": (
                f"{snapshot['event_trace_refs']}; "
                f"uncertified_loop_count={snapshot['uncertified_loop_count']}"
            ),
            "contradiction_refs": str(snapshot["contradiction_ref"]),
            "degradation_refs": str(snapshot["degradation_ref"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This packet records a Gemini-only uncertainty loop without any "
                "branch-control comparison.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any thrash change.",
            ),
            "Better Branch Discipline": (
                "This packet stays on the `check` family and does not exercise branch "
                "control.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any branch-discipline effect.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves guarded uncertified handling with explicit "
                "contradiction and degradation evidence within the committed Gemini "
                "uncertainty paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim uncertainty-handling lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet within the committed Gemini uncertainty paired-run "
                "series; no AUX burden artifact is recorded here.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "This packet stays on the Gemini commitment surface while preserving "
                "contradiction-bearing evidence.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This packet is part of the committed Gemini uncertainty paired-run "
            f"series under `{spec.pair_id}`. A single packet does not justify "
            "mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_GEMINI_UNCERTAINTY_REVIEWER_NOTE,
    )


GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_gemini_uncertainty_baseline_packet, pair_key
    )
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
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
