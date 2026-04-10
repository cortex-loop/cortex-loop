"""Shared helpers for deterministic mediation branch-discipline evidence."""

from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from tests.archive._mediation_evidence import AXIS_HEADINGS
from tests.archive.legacy_integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
)


BASELINE_BRANCH_SEQUENCE = ("open", "suspend", "resume", "merge")
MEDIATED_BRANCH_SEQUENCE = ("open", "merge")


@dataclass(frozen=True, slots=True)
class BranchDisciplinePairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    candidate_id: str
    commitment_id: str
    provenance_artifact_id: str
    branch_track_ref: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str
    baseline_step_prefix: str
    mediated_step_prefix: str
    host_surface_phrase: str
    starting_event_phrase: str


def build_branch_discipline_snapshot(
    *,
    spec: BranchDisciplinePairSpec,
    scenario_id: str,
    variant: str,
    candidate_event_name: str,
    publication_event_name: str,
) -> dict[str, object]:
    baseline = variant == "baseline_non_mediated"
    branch_sequence = BASELINE_BRANCH_SEQUENCE if baseline else MEDIATED_BRANCH_SEQUENCE
    step_prefix = spec.baseline_step_prefix if baseline else spec.mediated_step_prefix
    run_id = spec.baseline_run_id if baseline else spec.mediated_run_id
    stale_branch_count = 1 if baseline else 0
    orphaned_branch_count = 1 if baseline else 0
    unnecessary_branch_count = 1 if baseline else 0
    reopen_resume_count = 1 if baseline else 0

    event_parts: list[str] = []
    steps: list[dict[str, object]] = []
    for index, operation in enumerate(branch_sequence, start=1):
        is_publication = operation == "merge"
        raw_event_name = publication_event_name if is_publication else candidate_event_name
        outcome_class = "certified-full-commitment" if is_publication else "candidate-bearing"
        step_id = f"{step_prefix}-{index}"
        event_parts.append(f"{step_id}:{raw_event_name}/{operation}")
        steps.append(
            {
                "step_id": step_id,
                "raw_host_event_name": raw_event_name,
                "branch_operation": operation,
                "branch_track_ref": spec.branch_track_ref,
                "outcome_class": outcome_class,
            }
        )

    return {
        "scenario_id": scenario_id,
        "run_id": run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "candidate_id": spec.candidate_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "branch_track_ref": spec.branch_track_ref,
        "branch_sequence": list(branch_sequence),
        "stale_branch_count": stale_branch_count,
        "orphaned_branch_count": orphaned_branch_count,
        "unnecessary_branch_count": unnecessary_branch_count,
        "reopen_resume_count": reopen_resume_count,
        "contradiction_ref": f"{spec.contradiction_source_tag}:{spec.contradiction_summary}",
        "degradation_ref": spec.degradation_reason_code,
        "event_trace_refs": ", ".join(event_parts),
        "steps": steps,
    }


def build_branch_discipline_packet(
    *,
    spec: BranchDisciplinePairSpec,
    scenario_id: str,
    host_family: str,
    variant: str,
    snapshot: dict[str, object],
) -> PacketSnapshot:
    baseline = variant == "baseline_non_mediated"
    run_id = spec.baseline_run_id if baseline else spec.mediated_run_id
    sequence_text = " -> ".join(snapshot["branch_sequence"])
    branch_summary = (
        "The baseline branch-discipline comparator records "
        if baseline
        else "The mediated branch-discipline comparator records "
    )
    branch_summary += (
        f"`{sequence_text}` with "
        f"`stale_branch_count={snapshot['stale_branch_count']}`, "
        f"`orphaned_branch_count={snapshot['orphaned_branch_count']}`, and "
        f"`unnecessary_branch_count={snapshot['unnecessary_branch_count']}`."
    )
    return build_reference_mediation_packet(
        scenario_id=scenario_id,
        run_id=run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="branch_discipline",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
        variant=variant,
        host_family=host_family,
        scenario_inputs={
            "starting_request_or_event": spec.starting_event_phrase,
            "host_surface": spec.host_surface_phrase,
            "declared_scenario_goal": (
                "evaluate whether mediation reduces branch-discipline debt without "
                "reducing lawful task completion"
            ),
            "bounded_environment_or_approval_context": (
                "deterministic local default context with the same commitment boundary "
                "and the same host packet/publication surface on both sides of the pair"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The comparator reaches the same certified completion class on both "
                "sides of the pair."
            ),
            "branch_trajectory_summary": branch_summary,
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit and the completion "
                "boundary is unchanged."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "This comparator is not a host-realization claim; it preserves the same "
                "host surface while changing only branch-discipline debt."
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
                "This branch-discipline comparator records explicit reopen/resume pressure "
                "through `reopen_resume_count` within the same completion class.",
                "Package-level promotion is allowed only if the new branch-discipline "
                "cells show repeated lower reopen/resume counts.",
            ),
            "Better Branch Discipline": (
                "This comparator records explicit stale/orphaned/unnecessary branch "
                "counts on both sides of the pair.",
                "The branch-discipline metric is the strict comparison over "
                "`stale_branch_count + orphaned_branch_count + unnecessary_branch_count`.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves contradiction/degradation truth but does not "
                "target the uncertainty axis directly.",
                "Package-level uncertainty verdicts should continue to come from the "
                "uncertainty family unless explicitly widened later.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "This packet is not the non-thrash burden family and does not carry a "
                "burden artifact.",
                "Use the dedicated non-thrash burden family for burden promotion.",
            ),
            "Better Host-Specialized Realization": (
                "This comparator preserves the same host surface and does not claim "
                "host-native opportunity specialization lift.",
                "Host-realization verdicts should continue to come from the dedicated "
                "host_realization family.",
            ),
        },
        exclusion_notes=(
            f"This packet is one side of `{spec.pair_id}`. It is deterministic branch-"
            "discipline evidence only and does not by itself justify mediation."
        ),
        reviewer_note=(
            "This is committed branch-discipline evidence only. It does not justify "
            "mediation implementation and package-level evidence notes govern verdicts."
        ),
    )


def render_branch_discipline_packet(relative_path: str, packet: PacketSnapshot) -> str:
    lines = [
        f"# {Path(relative_path).stem}",
        "",
        f"Date: {packet['header']['date']}",
        f"Status: `{packet['status']}`",
        "",
        "## Scope",
        "",
        (
            "This committed run packet records one branch-discipline mediation comparator "
            "within the committed paired-run series for mediation evidence review.\n"
            "It does not justify mediation, activate mediation, or authorize implementation work."
        ),
        "",
        "## Header",
        "",
    ]
    for field_name, value in packet["header"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Variant Metadata", ""])
    for field_name, value in packet["variant_metadata"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Invariant Lock", ""])
    for field_name, value in packet["invariant_lock"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Scenario Inputs", ""])
    for field_name, value in packet["scenario_inputs"].items():
        lines.append(f"- {field_name}: {value}")
    lines.extend(["", "## Run Outputs", ""])
    for field_name, value in packet["run_outputs"].items():
        lines.append(f"- {field_name}: {value}")
    lines.extend(["", "## Artifact Refs", ""])
    for field_name, value in packet["artifact_refs"].items():
        if value == "none":
            lines.append(f"- {field_name}: none")
        else:
            lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Lift-Axis Observations", ""])
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
