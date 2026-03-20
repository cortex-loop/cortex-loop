"""Build or emit candidate reference mediation baseline packet docs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
import sys

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from tests._mediation_evidence import AXIS_HEADINGS
from tests.integration._reference_lane import reference_environment_handle
from tests.integration._reference_lane_packet_example import (
    build_reference_lane_packet_example_snapshot,
)
from tests.integration._reference_mediation_thrash_episode import (
    build_reference_thrash_episode_snapshot,
)


PacketSnapshot = dict[str, object]

REFERENCE_MEDIATION_BASELINE_PACKET_PATHS = {
    "scenario_uncertainty_reference_01": (
        "docs/mediation_evidence/reference/"
        "scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md"
    ),
    "scenario_host_reference_01": (
        "docs/mediation_evidence/reference/"
        "scenario_host_reference_01__baseline_non_mediated__run_001.md"
    ),
    "scenario_thrash_reference_01": (
        "docs/mediation_evidence/reference/"
        "scenario_thrash_reference_01__baseline_non_mediated__run_001.md"
    ),
}
_SCOPE_TEXT = {
    "scenario_uncertainty_reference_01": (
        "This committed run packet records one reference-host baseline-only uncertainty "
        "packet for mediation evidence review.\n"
        "It does not provide comparative mediation evidence, justify mediation, or "
        "authorize implementation work."
    ),
    "scenario_host_reference_01": (
        "This committed run packet records one reference-host baseline-only realization "
        "packet for mediation evidence review.\n"
        "It does not provide comparative mediation evidence, justify mediation, or "
        "authorize implementation work."
    ),
    "scenario_thrash_reference_01": (
        "This committed run packet records one reference-host baseline-only thrash "
        "control packet for mediation evidence review.\n"
        "It does not provide comparative mediation evidence, justify mediation, or "
        "authorize implementation work."
    ),
}
_INVARIANT_LOCK = {
    "same_host_family_preserved": "yes",
    "same_starting_task_framing_preserved": "yes",
    "same_core_commitment_boundary_preserved": "yes",
    "same_evidence_or_publication_surface_preserved": "yes",
    "same_success_rubric_preserved": "yes",
}
_REVIEWER_NOTE = (
    "This is baseline-only committed evidence, not comparative mediation evidence, "
    "and it does not justify mediation or authorize any implementation seam."
)


def build_reference_uncertainty_baseline_packet() -> PacketSnapshot:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "commit-3",
            "externally_consequential": True,
        },
        environment_handle=reference_environment_handle(),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED
    assert result.verdict.provenance_manifest is None
    assert result.verdict.contradiction_refs == ()
    assert result.verdict.degradation_refs == ()

    return _build_packet(
        scenario_id="scenario_uncertainty_reference_01",
        run_id="reference_uncertainty_baseline_run_001",
        paired_episode_set_id="pending_pair_reference_uncertainty_001",
        scenario_family="uncertainty_boundary",
        task_value_rubric_id="task_value_equal_truth_preservation",
        approval_or_environment_context_id="env_uncertainty_sensitive",
        scenario_inputs={
            "starting_request_or_event": (
                "`ApprovalResult` with `commitment_id=commit-3` and "
                "`externally_consequential=True`"
            ),
            "host_surface": "reference-host commitment path",
            "declared_scenario_goal": (
                "evaluate whether mediation improves uncertainty handling or brake timing "
                "on a bounded reference-host episode without smoothing contradictions or "
                "changing commitment truth"
            ),
            "bounded_environment_or_approval_context": (
                "`CommitmentEnvironmentHandle` with "
                "`available_query_kinds={EXECUTION_TRACE}` and "
                "`capability_tags={trace/read}`; no provenance manifest provided"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "Full-commitment reference-host evaluation yields `uncertified` when "
                "lawful evidence is absent."
            ),
            "branch_trajectory_summary": (
                "Single commitment-path evaluation only; no branch-comparison artifact is "
                "recorded in this baseline packet."
            ),
            "uncertainty_or_brake_summary": (
                "Missing evidence remains explicit as `uncertified` rather than being "
                "smoothed into certification or blockedness."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Reference-host commitment semantics remain host-native, but this packet "
                "makes no comparative host-lift claim."
            ),
        },
        artifact_refs={
            "event_trace_refs": "none",
            "contradiction_refs": "none",
            "degradation_refs": "none",
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "Baseline-only packet; no matched mediated run is recorded.",
                "No branch-churn metric is available from this packet alone.",
            ),
            "Better Branch Discipline": (
                "Baseline-only packet; no matched mediated run is recorded.",
                "No comparative branch-state table exists for this scenario-host cell yet.",
            ),
            "Better Uncertainty Handling": (
                "This packet shows lawful uncertified handling under missing evidence, but "
                "no mediated comparison exists.",
                "One baseline-only uncertified outcome is not enough to claim lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet; no equal-value burden comparison is recorded.",
                "No committed AUX burden artifact exists for this packet.",
            ),
            "Better Host-Specialized Realization": (
                "This packet stays on the reference-host commitment surface, but no "
                "mediated comparison exists.",
                "Host realization remains unscored without a matched paired run.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_reference_uncertainty_001` for a future honest comparison if "
            "one is ever earned."
        ),
    )


def build_reference_host_realization_baseline_packet() -> PacketSnapshot:
    snapshot = build_reference_lane_packet_example_snapshot()

    assert snapshot["dispatch_lane"] == DispatchLane.FULL_COMMITMENT.value
    assert snapshot["candidate_id"] == "commit-packet-1"
    assert snapshot["verdict_status"] == CommitmentStatus.CERTIFIED.value
    assert snapshot["packet_kind"] == "current-pair"

    event_trace = snapshot["event_trace"]
    contradiction_refs = snapshot["contradiction_refs"]
    degradation_refs = snapshot["degradation_refs"]

    assert isinstance(event_trace, dict)
    assert isinstance(contradiction_refs, list)
    assert isinstance(degradation_refs, list)
    assert len(contradiction_refs) == 1
    assert len(degradation_refs) == 1

    contradiction_ref = contradiction_refs[0]
    degradation_ref = degradation_refs[0]
    assert isinstance(contradiction_ref, dict)
    assert isinstance(degradation_ref, dict)

    return _build_packet(
        scenario_id="scenario_host_reference_01",
        run_id="reference_host_realization_baseline_run_001",
        paired_episode_set_id="pending_pair_reference_host_001",
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        scenario_inputs={
            "starting_request_or_event": (
                "`ApprovalResult` with `commitment_id=commit-packet-1` and "
                "`session_id=packet-session-1`"
            ),
            "host_surface": (
                "reference-host observe/bind plus commitment-to-eval-packet publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation produces any reference-host realization lift "
                "without adding burden or branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "reference-host commitment path with lawful provenance, "
                "contradiction-preserving degradation handling, and the committed "
                "reference-lane packet/publication surface"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The landed reference-host path produces a certified current-pair "
                "evaluation packet with explicit contradiction, degradation, and "
                "truthful-withheld fields."
            ),
            "branch_trajectory_summary": (
                "Single full-commitment publication path only; no branch-lift comparison "
                "is recorded in this baseline packet."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed packet "
                "example; no comparative uncertainty claim is made."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Reference-host observe/bind, commitment, and publication surfaces are "
                "exercised end-to-end without any pooled host claim."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(event_trace["trace_id"]),
            "contradiction_refs": (
                f"{contradiction_ref['source_tag']}:{contradiction_ref['summary']}"
            ),
            "degradation_refs": str(degradation_ref["reason_code"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": (
                "docs/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md"
            ),
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
                "This packet exercises the reference-host publication path end to end, "
                "but no mediated comparison exists.",
                "Reference-host realization remains descriptive only until a matched "
                "mediated run exists.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_reference_host_001` for a future honest comparison if one is "
            "ever earned."
        ),
    )


def build_reference_thrash_baseline_packet() -> PacketSnapshot:
    snapshot = build_reference_thrash_episode_snapshot()
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

    return _build_packet(
        scenario_id="scenario_thrash_reference_01",
        run_id="reference_thrash_baseline_run_001",
        paired_episode_set_id="pending_pair_reference_thrash_001",
        scenario_family="thrash_control",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
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
                "The bounded reference-host episode reaches certified completion at "
                "`thrash-step-4` after one guarded uncertified follow-up at "
                "`thrash-step-2`."
            ),
            "branch_trajectory_summary": (
                "The live reference-host episode derives an explicit "
                "`open -> suspend -> resume -> merge` sequence across "
                "`thrash-step-1` through `thrash-step-4`."
            ),
            "uncertainty_or_brake_summary": (
                "Brake state is `guarded` only at `thrash-step-2` from elevated evidence "
                "uncertainty; no contradiction or degradation smoothing occurs."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Reference-host commitment and landed SRE branch-control surfaces are "
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
                "This packet records one lawful multi-step reference-host branch cycle, "
                "but no matched mediated comparison exists.",
                "One baseline-only `open -> suspend -> resume -> merge` episode does not "
                "establish thrash reduction.",
            ),
            "Better Branch Discipline": (
                "This packet preserves explicit branch trajectory evidence on the "
                "reference-host path, but no mediated comparison exists.",
                "One baseline-only branch-control trace is descriptive only for this "
                "scenario-host cell.",
            ),
            "Better Uncertainty Handling": (
                "The guarded uncertified follow-up remains explicit at `thrash-step-2`, "
                "but no mediated comparison exists.",
                "One baseline-only guarded transition does not establish comparative lift.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "Baseline-only packet; no equal-value burden comparison is recorded.",
                "No committed AUX burden artifact exists for this packet.",
            ),
            "Better Host-Specialized Realization": (
                "This packet exercises the reference-host commitment path together with "
                "landed SRE branch-control carriers, but no mediated comparison exists.",
                "Reference-host realization remains descriptive until a matched mediated "
                "run exists.",
            ),
        },
        exclusion_notes=(
            "This packet is intentionally baseline-only and reserves "
            "`pending_pair_reference_thrash_001` for a future honest comparison if one "
            "is ever earned."
        ),
    )


REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS: Mapping[
    str, Callable[[], PacketSnapshot]
] = {
    "scenario_uncertainty_reference_01": build_reference_uncertainty_baseline_packet,
    "scenario_host_reference_01": build_reference_host_realization_baseline_packet,
    "scenario_thrash_reference_01": build_reference_thrash_baseline_packet,
}


def render_reference_mediation_baseline_packet(
    relative_path: str,
    packet: PacketSnapshot,
) -> str:
    scenario_id = str(packet["header"]["scenario_id"])
    lines = [
        f"# {Path(relative_path).stem}",
        "",
        f"Date: {packet['header']['date']}",
        f"Status: `{packet['status']}`",
        "",
        "## Scope",
        "",
        _SCOPE_TEXT[scenario_id],
        "",
        "## Header",
        "",
        f"- date: {packet['header']['date']}",
        f"- status: `{packet['header']['status']}`",
        f"- scenario_id: `{packet['header']['scenario_id']}`",
        f"- run_id: `{packet['header']['run_id']}`",
        f"- paired_episode_set_id: `{packet['header']['paired_episode_set_id']}`",
        "",
        "## Variant Metadata",
        "",
        f"- variant: `{packet['variant_metadata']['variant']}`",
        f"- host_family: `{packet['variant_metadata']['host_family']}`",
        f"- scenario_family: `{packet['variant_metadata']['scenario_family']}`",
        f"- task_value_rubric_id: `{packet['variant_metadata']['task_value_rubric_id']}`",
        (
            "- approval_or_environment_context_id: "
            f"`{packet['variant_metadata']['approval_or_environment_context_id']}`"
        ),
        "",
        "## Invariant Lock",
        "",
    ]

    for field_name, value in packet["invariant_lock"].items():
        lines.append(f"- {field_name}: `{value}`")

    lines.extend(
        [
            "",
            "## Scenario Inputs",
            "",
        ]
    )
    for field_name, value in packet["scenario_inputs"].items():
        lines.append(f"- {field_name}: {value}")

    lines.extend(
        [
            "",
            "## Run Outputs",
            "",
        ]
    )
    for field_name, value in packet["run_outputs"].items():
        lines.append(f"- {field_name}: {value}")

    lines.extend(
        [
            "",
            "## Artifact Refs",
            "",
        ]
    )
    for field_name, value in packet["artifact_refs"].items():
        if value == "none":
            lines.append(f"- {field_name}: none")
        else:
            lines.append(f"- {field_name}: `{value}`")

    lines.extend(
        [
            "",
            "## Lift-Axis Observations",
            "",
        ]
    )
    for heading in AXIS_HEADINGS:
        axis_payload = packet["lift_axes"][heading]
        lines.extend(
            [
                f"### {heading}",
                "",
                f"- observation: {axis_payload['observation']}",
                f"- metric_notes: {axis_payload['metric_notes']}",
                f"- verdict: `{axis_payload['verdict']}`",
                "",
            ]
        )
    lines.pop()

    lines.extend(
        [
            "",
            "## Exclusions Or Unusable-Pair Notes",
            "",
            f"- exclusion_status: `{packet['exclusions']['exclusion_status']}`",
            f"- failure_tags: `{packet['exclusions']['failure_tags']}`",
            f"- notes: {packet['exclusions']['notes']}",
            "",
            "## Reviewer Note",
            "",
            f"- reviewer_note: {packet['reviewer_note']['reviewer_note']}",
            "",
        ]
    )
    return "\n".join(lines)


def emit_reference_mediation_baseline_packets() -> None:
    for index, (scenario_id, builder) in enumerate(
        REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS.items()
    ):
        relative_path = REFERENCE_MEDIATION_BASELINE_PACKET_PATHS[scenario_id]
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(
            render_reference_mediation_baseline_packet(relative_path, builder())
        )
        if index != len(REFERENCE_MEDIATION_BASELINE_PACKET_BUILDERS) - 1:
            sys.stdout.write("\n")


def _build_packet(
    *,
    scenario_id: str,
    run_id: str,
    paired_episode_set_id: str,
    scenario_family: str,
    task_value_rubric_id: str,
    approval_or_environment_context_id: str,
    scenario_inputs: dict[str, str],
    run_outputs: dict[str, str],
    artifact_refs: dict[str, str],
    lift_axis_notes: Mapping[str, tuple[str, str]],
    exclusion_notes: str,
) -> PacketSnapshot:
    return {
        "status": "reviewed_evidence",
        "header": {
            "date": "2026-03-20",
            "status": "reviewed_evidence",
            "scenario_id": scenario_id,
            "run_id": run_id,
            "paired_episode_set_id": paired_episode_set_id,
        },
        "variant_metadata": {
            "variant": "baseline_non_mediated",
            "host_family": "reference",
            "scenario_family": scenario_family,
            "task_value_rubric_id": task_value_rubric_id,
            "approval_or_environment_context_id": approval_or_environment_context_id,
        },
        "invariant_lock": dict(_INVARIANT_LOCK),
        "scenario_inputs": dict(scenario_inputs),
        "run_outputs": dict(run_outputs),
        "artifact_refs": dict(artifact_refs),
        "lift_axes": {
            heading: {
                "observation": observation,
                "metric_notes": metric_notes,
                "verdict": "insufficient",
            }
            for heading, (observation, metric_notes) in lift_axis_notes.items()
        },
        "exclusions": {
            "exclusion_status": "none",
            "failure_tags": "none",
            "notes": exclusion_notes,
        },
        "reviewer_note": {
            "reviewer_note": _REVIEWER_NOTE,
        },
    }


if __name__ == "__main__":
    emit_reference_mediation_baseline_packets()
