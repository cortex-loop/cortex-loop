"""Build or emit candidate OpenAI mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
import sys

from cortex.core.dispatch import DispatchLane
from tests.integration._openai_host_realization_pair import (
    DEFAULT_OPENAI_HOST_REALIZATION_PAIR_KEY,
    OPENAI_HOST_REALIZATION_PAIR_KEYS,
    OPENAI_HOST_REALIZATION_PAIR_SPECS,
)
from tests.integration._openai_lane_packet_example import (
    build_openai_lane_packet_example_snapshot,
)
from tests.integration._openai_mediated_lane_packet_example import (
    build_openai_host_realization_specialization_snapshot,
)
from tests.integration._openai_mediation_thrash_episode import (
    DEFAULT_OPENAI_THRASH_PAIR_KEY,
    OPENAI_THRASH_PAIR_KEYS,
    OPENAI_THRASH_PAIR_SPECS,
    build_openai_thrash_episode_snapshot,
    openai_thrash_scenario_inputs,
)
from tests.integration._openai_mediation_thrash_burden import (
    build_openai_thrash_burden_artifact,
    emit_openai_thrash_burden_artifacts,
    openai_thrash_baseline_burden_artifact_path,
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
        OPENAI_HOST_REALIZATION_PAIR_SPECS[
            DEFAULT_OPENAI_HOST_REALIZATION_PAIR_KEY
        ].baseline_packet_path
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
OPENAI_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_HOST_REALIZATION_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_HOST_REALIZATION_PAIR_KEYS
}
OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS
}
OPENAI_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_THRASH_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_THRASH_PAIR_KEYS
}
OPENAI_THRASH_BASELINE_BURDEN_PATHS = {
    pair_key: openai_thrash_baseline_burden_artifact_path(pair_key)
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
    "This is baseline-only committed evidence within the committed OpenAI "
    "host-realization paired-run series. It is not comparative mediation evidence by "
    "itself, does not justify mediation, and package-level evidence notes govern any "
    "verdict."
)


def build_openai_host_realization_baseline_packet(
    pair_key: str = DEFAULT_OPENAI_HOST_REALIZATION_PAIR_KEY,
) -> PacketSnapshot:
    spec = OPENAI_HOST_REALIZATION_PAIR_SPECS[pair_key]
    snapshot = build_openai_lane_packet_example_snapshot(pair_key)
    specialization = build_openai_host_realization_specialization_snapshot(
        clearly_superior=False,
    )

    assert snapshot["dispatch_lanes"] == {
        "candidate": DispatchLane.CANDIDATE_BEARING.value,
        "publication": DispatchLane.FULL_COMMITMENT.value,
    }
    assert snapshot["candidate_id"] == spec.candidate_id
    assert snapshot["verdict_status"] == "certified"
    assert snapshot["packet_kind"] == "current-pair"
    assert specialization["selected_family"] == "seek-context"
    assert specialization["preferred_opportunity_ref"] is None
    assert specialization["direct_opportunity_specialization_used"] is False
    assert specialization["host_opportunity_refs"] == ["mcp.query"]
    assert specialization["native_surface_tags"] == ["mcp", "structured-query"]

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
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        host_family="openai",
        scenario_inputs={
            "starting_request_or_event": (
                f"`response.output_text.delta` candidate-bearing turn on "
                f"`{spec.session_id}` followed by `response.completed` "
                f"with `commitment_id={spec.commitment_id}`"
            ),
            "host_surface": (
                "OpenAI-host opportunity selection plus candidate-bearing continuation and "
                "commitment-to-eval-packet publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation produces any OpenAI-host realization lift "
                "without adding burden or branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "OpenAI-host candidate-bearing plus commitment/publication path with "
                "lawful provenance, contradiction-preserving degradation handling, the "
                "committed OpenAI-lane packet/publication surface, and a bounded "
                "host-opportunity set containing `mcp.query`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The baseline OpenAI-host path preserves the same certified current-pair "
                "evaluation packet with explicit contradiction, degradation, and "
                "truthful-withheld fields while retaining the generic `seek-context` "
                "family without direct host-native specialization."
            ),
            "branch_trajectory_summary": (
                "One OpenAI-native candidate-bearing turn is followed by one "
                "full-commitment publication path only; the comparator delta for this "
                "pair is the host-opportunity realization choice, not a branch-sequence "
                "change."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed OpenAI "
                "packet example, and `direct_opportunity_specialization_used=0` remains "
                "explicit for the baseline side of the pair."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "OpenAI-host realization retains the selected family `seek-context` "
                "with `direct_opportunity_specialization_used=0` while preserving the "
                "same host-opportunity set containing `mcp.query` and the same "
                "certified OpenAI `current-pair` publication surface."
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
                "The pair holds the same certified completion class and truth boundary, "
                "but this packet carries no AUX burden artifact.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any lower-burden verdict.",
            ),
            "Better Host-Specialized Realization": (
                "This baseline packet keeps the same host-opportunity set containing "
                "`mcp.query` but does not directly specialize it.",
                "The host-realization metric is "
                "`direct_opportunity_specialization_used=0` on the baseline side of the pair.",
            ),
        },
        exclusion_notes=(
            f"This packet is the baseline side of `{spec.pair_id}`. A single packet "
            "does not justify mediation; package-level evidence notes govern verdicts."
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
    branch_sequence = snapshot["branch_sequence"]
    burden_artifact = build_openai_thrash_baseline_burden_artifact(pair_key)

    assert isinstance(steps, list)
    assert branch_sequence == ["open", "suspend", "resume", "merge"]
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
            "burden_summary": (
                "Visible intervention burden is recorded as "
                f"`intervention_burden={burden_artifact['aux_burden_report']['intervention_burden']}` "
                "from the committed branch-operation count on this baseline run."
            ),
            "host_realization_summary": (
                "OpenAI-host commitment and landed SRE branch-control surfaces are "
                "exercised together without any pooled host claim."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(snapshot["event_trace_refs"]),
            "contradiction_refs": "none",
            "degradation_refs": "none",
            "aux_burden_refs_if_present": OPENAI_THRASH_BASELINE_BURDEN_PATHS[pair_key],
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
                "Baseline-only packet within the committed thrash paired-run series with "
                f"`intervention_burden={burden_artifact['aux_burden_report']['intervention_burden']}` "
                "recorded from the visible branch-operation count.",
                "The burden metric is the exact committed branch-operation count for this "
                "run.",
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


def build_openai_thrash_baseline_burden_artifact(
    pair_key: str = DEFAULT_OPENAI_THRASH_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_THRASH_PAIR_SPECS[pair_key]
    snapshot = build_openai_thrash_episode_snapshot(pair_key)
    branch_sequence = snapshot["branch_sequence"]

    assert branch_sequence == ["open", "suspend", "resume", "merge"]

    return build_openai_thrash_burden_artifact(
        pair_id=spec.pair_id,
        pair_key=pair_key,
        run_id=spec.baseline_run_id,
        variant="baseline_non_mediated",
        host_family="openai",
        branch_sequence=branch_sequence,
    )


OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    **{
        OPENAI_HOST_REALIZATION_BASELINE_PACKET_PATHS[pair_key]: (
            lambda pair_key=pair_key: build_openai_host_realization_baseline_packet(pair_key)
        )
        for pair_key in OPENAI_HOST_REALIZATION_PAIR_KEYS
    },
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
OPENAI_THRASH_BASELINE_BURDEN_DOC_BUILDERS: Mapping[str, Callable[[], dict[str, object]]] = {
    OPENAI_THRASH_BASELINE_BURDEN_PATHS[pair_key]: partial(
        build_openai_thrash_baseline_burden_artifact, pair_key
    )
    for pair_key in OPENAI_THRASH_PAIR_KEYS
}


def emit_openai_mediation_baseline_packets() -> None:
    for index, (relative_path, builder) in enumerate(
        OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items()
    ):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))
        if index != len(OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS) - 1:
            sys.stdout.write("\n")
    if OPENAI_THRASH_BASELINE_BURDEN_DOC_BUILDERS:
        sys.stdout.write("\n")
        emit_openai_thrash_burden_artifacts(OPENAI_THRASH_BASELINE_BURDEN_DOC_BUILDERS)


if __name__ == "__main__":
    emit_openai_mediation_baseline_packets()
