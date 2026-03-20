"""Build or emit candidate OpenAI mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
import sys

from cortex.core.dispatch import DispatchLane
from tests.integration._openai_lane_packet_example import (
    build_openai_lane_packet_example_snapshot,
)
from tests.integration._openai_mediation_thrash_episode import (
    DEFAULT_OPENAI_THRASH_PAIR_KEY,
    OPENAI_THRASH_PAIR_KEYS,
    OPENAI_THRASH_PAIR_SPECS,
    build_openai_thrash_episode_snapshot,
    openai_thrash_scenario_inputs,
)
from tests.integration._openai_mediation_uncertainty_episode import (
    DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY,
    OPENAI_UNCERTAINTY_PAIR_KEYS,
    OPENAI_UNCERTAINTY_PAIR_SPECS,
    build_openai_uncertainty_episode_snapshot,
    openai_uncertainty_scenario_inputs,
)
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)


OPENAI_MEDIATION_BASELINE_PACKET_PATHS = {
    "scenario_host_openai_01": (
        "docs/mediation_evidence/openai/"
        "scenario_host_openai_01__baseline_non_mediated__run_001.md"
    ),
    "scenario_uncertainty_openai_01": (
        OPENAI_UNCERTAINTY_PAIR_SPECS[
            DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY
        ].baseline_packet_path
    ),
    "scenario_thrash_openai_01": (
        OPENAI_THRASH_PAIR_SPECS[DEFAULT_OPENAI_THRASH_PAIR_KEY].baseline_packet_path
    ),
}
OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS
}
OPENAI_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_THRASH_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_THRASH_PAIR_KEYS
}
_OPENAI_UNCERTAINTY_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed OpenAI "
    "uncertainty paired-run series. It is not comparative mediation evidence by "
    "itself and does not justify mediation or authorize any implementation seam."
)
_OPENAI_THRASH_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed OpenAI thrash "
    "paired-run series. It is not comparative mediation evidence by itself and "
    "does not justify mediation or authorize any implementation seam."
)
_OPENAI_HOST_REALIZATION_REVIEWER_NOTE = (
    "This is baseline-only committed evidence, not comparative mediation evidence, "
    "and it does not justify mediation or authorize any implementation seam."
)


def build_openai_host_realization_baseline_packet() -> PacketSnapshot:
    snapshot = build_openai_lane_packet_example_snapshot()

    assert snapshot["dispatch_lanes"] == {
        "candidate": DispatchLane.CANDIDATE_BEARING.value,
        "publication": DispatchLane.FULL_COMMITMENT.value,
    }
    assert snapshot["candidate_id"] == "openai-host-packet-candidate-1"
    assert snapshot["verdict_status"] == "certified"
    assert snapshot["packet_kind"] == "current-pair"

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
    assert len(contradiction_refs) == 1
    assert len(degradation_refs) == 1

    contradiction_ref = contradiction_refs[0]
    degradation_ref = degradation_refs[0]
    assert isinstance(contradiction_ref, dict)
    assert isinstance(degradation_ref, dict)

    return build_reference_mediation_packet(
        scenario_id="scenario_host_openai_01",
        run_id="openai_host_realization_baseline_run_001",
        paired_episode_set_id="pending_pair_openai_host_001",
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        host_family="openai",
        scenario_inputs={
            "starting_request_or_event": (
                "`response.output_text.delta` candidate-bearing turn on "
                "`openai-host-packet-session-1` followed by `response.completed` "
                "with `commitment_id=openai-host-packet-commit-1`"
            ),
            "host_surface": (
                "OpenAI-host observe/bind plus candidate-bearing continuation and "
                "commitment-to-eval-packet publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation improves OpenAI-native opportunity use or "
                "fallback selection without host flattening"
            ),
            "bounded_environment_or_approval_context": (
                "OpenAI-host candidate-bearing plus commitment/publication path with "
                "lawful provenance, contradiction-preserving degradation handling, and "
                "the committed OpenAI-lane packet/publication surface"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The landed OpenAI-host path produces a certified current-pair "
                "evaluation packet with explicit contradiction, degradation, and "
                "truthful-withheld fields after an OpenAI-native candidate-bearing prelude."
            ),
            "branch_trajectory_summary": (
                "One OpenAI-native candidate-bearing turn is followed by one "
                "full-commitment publication path only; no matched branch-lift "
                "comparison is recorded in this baseline packet."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed OpenAI "
                "packet example; no comparative uncertainty claim is made."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "OpenAI-host observe/bind, candidate-bearing continuation, "
                "commitment, and publication surfaces are exercised end to end "
                "without any pooled host claim."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(event_trace["trace_id"]),
            "contradiction_refs": (
                f"{contradiction_ref['source_tag']}:{contradiction_ref['summary']}"
            ),
            "degradation_refs": str(degradation_ref["reason_code"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "docs/CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "Baseline-only packet; no matched mediated run is recorded.",
                "No repeated reopen/resume metric is available from this packet alone.",
            ),
            "Better Branch Discipline": (
                "Baseline-only packet; no matched mediated run is recorded.",
                "No comparative branch-discipline evidence exists for this scenario-host "
                "cell yet.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves contradiction and degradation explicitly, but no "
                "mediated comparison exists.",
                "One baseline publication packet does not establish comparative "
                "uncertainty lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet; no equal-value burden comparison is recorded.",
                "No committed AUX burden artifact exists for this packet.",
            ),
            "Better Host-Specialized Realization": (
                "This packet exercises the OpenAI-host candidate-bearing and publication "
                "path end to end, but no mediated comparison exists.",
                "OpenAI-host realization remains descriptive only until a matched "
                "mediated run exists.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_openai_host_001` for a future honest comparison if one is "
            "ever earned."
        ),
        reviewer_note=_OPENAI_HOST_REALIZATION_REVIEWER_NOTE,
    )


def build_openai_uncertainty_baseline_packet(
    pair_key: str = DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY,
) -> PacketSnapshot:
    spec = OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key]
    snapshot = build_openai_uncertainty_episode_snapshot(pair_key)
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
        scenario_id="scenario_uncertainty_openai_01",
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        host_family="openai",
        scenario_inputs=openai_uncertainty_scenario_inputs(spec),
        run_outputs={
            "outcome_summary": (
                "The bounded OpenAI-host uncertainty episode reaches certified "
                f"completion at `{spec.baseline_step_prefix}-3` after two guarded "
                "uncertified full-commitment turns."
            ),
            "branch_trajectory_summary": (
                "This OpenAI-only uncertainty series stays on a `check`-family path "
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
                "OpenAI commitment semantics, contradiction-bearing evidence, and the "
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
                "This packet records an OpenAI-only uncertainty loop without any "
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
                "contradiction and degradation evidence within the committed OpenAI "
                "uncertainty paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim uncertainty-handling lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet within the committed OpenAI uncertainty paired-run "
                "series; no AUX burden artifact is recorded here.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "This packet stays on the OpenAI commitment surface while preserving "
                "contradiction-bearing evidence.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This packet is part of the committed OpenAI uncertainty paired-run "
            f"series under `{spec.pair_id}`. A single packet does not justify "
            "mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_OPENAI_UNCERTAINTY_REVIEWER_NOTE,
    )


def build_openai_thrash_baseline_packet(
    pair_key: str = DEFAULT_OPENAI_THRASH_PAIR_KEY,
) -> PacketSnapshot:
    spec = OPENAI_THRASH_PAIR_SPECS[pair_key]
    snapshot = build_openai_thrash_episode_snapshot(pair_key)
    steps = snapshot["steps"]

    assert isinstance(steps, list)
    assert snapshot["branch_sequence"] == ["open", "suspend", "resume", "merge"]
    assert [step["outcome_class"] for step in steps] == [
        "candidate-bearing",
        "uncertified-full-commitment",
        "candidate-bearing",
        "certified-full-commitment",
    ]
    assert steps[1]["brake_state"] == "guarded"
    assert steps[3]["dispatch_lane"] == DispatchLane.FULL_COMMITMENT.value

    return build_reference_mediation_packet(
        scenario_id="scenario_thrash_openai_01",
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="thrash_control",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
        host_family="openai",
        scenario_inputs=openai_thrash_scenario_inputs(spec),
        run_outputs={
            "outcome_summary": (
                "The bounded OpenAI-host episode reaches certified completion at "
                f"`{spec.baseline_step_prefix}-4` after one guarded uncertified "
                f"follow-up at `{spec.baseline_step_prefix}-2`."
            ),
            "branch_trajectory_summary": (
                "The live OpenAI-host episode derives an explicit "
                "`open -> suspend -> resume -> merge` sequence across "
                f"`{spec.baseline_step_prefix}-1` through `{spec.baseline_step_prefix}-4`."
            ),
            "uncertainty_or_brake_summary": (
                f"Brake state is `guarded` only at `{spec.baseline_step_prefix}-2` "
                "from elevated evidence uncertainty; no contradiction or degradation "
                "smoothing occurs."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "OpenAI-host commitment and landed SRE branch-control surfaces are "
                "exercised together without any pooled host claim."
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
                "This packet records one lawful multi-step OpenAI-host branch cycle "
                "within the committed thrash paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim thrash reduction.",
            ),
            "Better Branch Discipline": (
                "This packet preserves explicit branch trajectory evidence on the "
                "OpenAI-host path within the committed thrash paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim branch-discipline lift.",
            ),
            "Better Uncertainty Handling": (
                "The guarded uncertified follow-up remains explicit within the committed "
                "thrash paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim uncertainty lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet within the committed thrash paired-run series; no "
                "AUX burden artifact is recorded here.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim burden lift.",
            ),
            "Better Host-Specialized Realization": (
                "This packet exercises the OpenAI-host commitment path together with "
                "landed SRE branch-control carriers within the committed thrash series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This packet is part of the committed OpenAI thrash paired-run series under "
            f"`{spec.pair_id}`. A single packet does not justify mediation; "
            "package-level evidence notes govern verdicts."
        ),
        reviewer_note=_OPENAI_THRASH_REVIEWER_NOTE,
    )


OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    OPENAI_MEDIATION_BASELINE_PACKET_PATHS["scenario_host_openai_01"]: (
        build_openai_host_realization_baseline_packet
    ),
    **{
        OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key]: partial(
            build_openai_uncertainty_baseline_packet, pair_key
        )
        for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS
    },
    **{
        OPENAI_THRASH_BASELINE_PACKET_PATHS[pair_key]: partial(
            build_openai_thrash_baseline_packet, pair_key
        )
        for pair_key in OPENAI_THRASH_PAIR_KEYS
    },
}


def emit_openai_mediation_baseline_packets() -> None:
    for index, (relative_path, builder) in enumerate(
        OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items()
    ):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))
        if index != len(OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS) - 1:
            sys.stdout.write("\n")


if __name__ == "__main__":
    emit_openai_mediation_baseline_packets()
