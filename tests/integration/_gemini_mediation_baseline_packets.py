"""Build or emit candidate Gemini mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
import sys

from cortex.core.dispatch import DispatchLane
from tests.integration._gemini_mediation_thrash_episode import (
    DEFAULT_GEMINI_THRASH_PAIR_KEY,
    GEMINI_THRASH_PAIR_KEYS,
    GEMINI_THRASH_PAIR_SPECS,
    build_gemini_thrash_episode_snapshot,
)
from tests.integration._gemini_lane_packet_example import (
    build_gemini_lane_packet_example_snapshot,
)
from tests.integration._gemini_mediated_lane_packet_example import (
    build_gemini_host_realization_specialization_snapshot,
)
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
    "scenario_host_gemini_01": (
        "docs/mediation_evidence/gemini/"
        "scenario_host_gemini_01__baseline_non_mediated__run_001.md"
    ),
    "scenario_uncertainty_gemini_01": (
        GEMINI_UNCERTAINTY_PAIR_SPECS[
            DEFAULT_GEMINI_UNCERTAINTY_PAIR_KEY
        ].baseline_packet_path
    ),
    "scenario_thrash_gemini_01": (
        GEMINI_THRASH_PAIR_SPECS[
            DEFAULT_GEMINI_THRASH_PAIR_KEY
        ].baseline_packet_path
    ),
}
GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: GEMINI_UNCERTAINTY_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
}
GEMINI_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: GEMINI_THRASH_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in GEMINI_THRASH_PAIR_KEYS
}
_GEMINI_UNCERTAINTY_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed Gemini "
    "uncertainty paired-run series. It is not comparative mediation evidence by "
    "itself and does not justify mediation or authorize any implementation seam."
)
_GEMINI_THRASH_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed Gemini "
    "thrash paired-run series. It is not comparative mediation evidence by "
    "itself and does not justify mediation or authorize any implementation seam."
)
_GEMINI_HOST_REALIZATION_REVIEWER_NOTE = (
    "This is baseline-only committed evidence within the committed Gemini "
    "host-realization paired-run series. It is not comparative mediation evidence by "
    "itself, does not justify mediation, and package-level evidence notes govern any "
    "verdict."
)


def build_gemini_host_realization_baseline_packet() -> PacketSnapshot:
    snapshot = build_gemini_lane_packet_example_snapshot()
    specialization = build_gemini_host_realization_specialization_snapshot(
        clearly_superior=False,
    )

    assert snapshot["dispatch_lanes"] == {
        "candidate": DispatchLane.CANDIDATE_BEARING.value,
        "publication": DispatchLane.FULL_COMMITMENT.value,
    }
    assert snapshot["candidate_id"] == "gemini-host-packet-candidate-1"
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
    assert len(contradiction_refs) == 1
    assert len(degradation_refs) == 1

    contradiction_ref = contradiction_refs[0]
    degradation_ref = degradation_refs[0]
    assert isinstance(contradiction_ref, dict)
    assert isinstance(degradation_ref, dict)

    return build_reference_mediation_packet(
        scenario_id="scenario_host_gemini_01",
        run_id="gemini_host_realization_baseline_run_001",
        paired_episode_set_id="pair_gemini_host_001",
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        host_family="gemini",
        scenario_inputs={
            "starting_request_or_event": (
                "`content.delta` candidate-bearing turn on "
                "`gemini-host-packet-session-1` followed by `interaction.complete` "
                "with `commitment_id=gemini-host-packet-commit-1`"
            ),
            "host_surface": (
                "Gemini-host opportunity selection plus candidate-bearing "
                "continuation and commitment-to-eval-packet publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation produces any Gemini-host realization lift "
                "without adding burden or branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "Gemini-host candidate-bearing plus commitment/publication path with "
                "lawful provenance, contradiction-preserving degradation handling, the "
                "committed Gemini-lane packet/publication surface, and a bounded "
                "host-opportunity set containing `mcp.query`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The baseline Gemini-host path preserves the same certified "
                "current-pair evaluation packet with explicit contradiction, "
                "degradation, and truthful-withheld fields while retaining the "
                "generic `seek-context` family without direct host-native specialization."
            ),
            "branch_trajectory_summary": (
                "One Gemini-native candidate-bearing turn is followed by one "
                "full-commitment publication path only; the comparator delta for "
                "this pair is the host-opportunity realization choice, not a "
                "branch-sequence change."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed Gemini "
                "packet example, and `direct_opportunity_specialization_used=0` "
                "remains explicit for the baseline side of the pair."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Gemini-host realization retains the selected family `seek-context` "
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
            "evaluation_packet_refs_if_present": "docs/CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0.md",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This baseline packet is part of the committed Gemini "
                "host-realization paired-run series, but it is not a branch-control "
                "comparison.",
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
                "This baseline packet keeps the same host-opportunity set containing "
                "`mcp.query` but does not directly specialize it.",
                "The host-realization metric is "
                "`direct_opportunity_specialization_used=0` on the baseline side of "
                "the pair.",
            ),
        },
        exclusion_notes=(
            "This packet is the baseline side of `pair_gemini_host_001`. A single "
            "packet does not justify mediation; package-level evidence notes govern "
            "verdicts."
        ),
        reviewer_note=_GEMINI_HOST_REALIZATION_REVIEWER_NOTE,
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


def build_gemini_thrash_baseline_packet(
    pair_key: str = DEFAULT_GEMINI_THRASH_PAIR_KEY,
) -> PacketSnapshot:
    spec = GEMINI_THRASH_PAIR_SPECS[pair_key]
    snapshot = build_gemini_thrash_episode_snapshot(pair_key)
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
        scenario_id="scenario_thrash_gemini_01",
        run_id=spec.baseline_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="thrash_control",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
        host_family="gemini",
        scenario_inputs={
            "starting_request_or_event": (
                f"bounded Gemini-host branch-control flow on `{spec.session_id}` with "
                "repeated candidate-bearing follow-up before final certified completion"
            ),
            "host_surface": (
                "Gemini observe/bind and commitment-path slice plus landed SRE goal, "
                "brake, allocation, and core support-session surfaces"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation reduces repeated control-family oscillation "
                "on a bounded Gemini-host lifecycle episode without flattening "
                "Gemini-native behavior"
            ),
            "bounded_environment_or_approval_context": (
                "`CommitmentEnvironmentHandle` with "
                "`available_query_kinds={EXECUTION_TRACE}` and "
                "`capability_tags={trace/read}` on `env_local_default`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The bounded Gemini-host episode reaches certified completion at "
                f"`{spec.baseline_step_prefix}-4` after one guarded uncertified "
                f"follow-up at `{spec.baseline_step_prefix}-2`."
            ),
            "branch_trajectory_summary": (
                "The live Gemini-host episode derives an explicit "
                "`open -> suspend -> resume -> merge` sequence across "
                f"`{spec.baseline_step_prefix}-1` through `{spec.baseline_step_prefix}-4`."
            ),
            "uncertainty_or_brake_summary": (
                f"Brake state is `guarded` only at `{spec.baseline_step_prefix}-2` from "
                "elevated evidence uncertainty; no contradiction or degradation "
                "smoothing occurs."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Gemini-host commitment and landed SRE branch-control surfaces are "
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
                "This packet records one lawful multi-step Gemini-host branch cycle "
                "within the committed thrash paired-run series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim thrash reduction.",
            ),
            "Better Branch Discipline": (
                "This packet preserves explicit branch trajectory evidence on the "
                "Gemini-host path within the committed thrash paired-run series.",
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
                "This packet exercises the Gemini-host commitment path together with "
                "landed SRE branch-control carriers within the committed thrash series.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim host-specialized realization lift.",
            ),
        },
        exclusion_notes=(
            "This packet is part of the committed Gemini thrash paired-run series "
            f"under `{spec.pair_id}`. A single packet does not justify mediation; "
            "package-level evidence notes govern verdicts."
        ),
        reviewer_note=_GEMINI_THRASH_REVIEWER_NOTE,
    )


GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS: Mapping[str, Callable[[], PacketSnapshot]] = {
    GEMINI_MEDIATION_BASELINE_PACKET_PATHS["scenario_host_gemini_01"]: (
        build_gemini_host_realization_baseline_packet
    ),
    **{
        GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key]: partial(
            build_gemini_uncertainty_baseline_packet, pair_key
        )
        for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS
    },
    **{
        GEMINI_THRASH_BASELINE_PACKET_PATHS[pair_key]: partial(
            build_gemini_thrash_baseline_packet, pair_key
        )
        for pair_key in GEMINI_THRASH_PAIR_KEYS
    },
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
