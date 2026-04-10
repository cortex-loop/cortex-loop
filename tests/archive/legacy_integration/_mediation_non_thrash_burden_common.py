"""Shared helpers for deterministic non-thrash burden mediation evidence."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
import sys

from cortex.aux.cost import AuxBurdenReport
from cortex.core.envelopes import MetadataField
from tests.archive._mediation_evidence import AXIS_HEADINGS
from tests.archive.legacy_integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
)


BASELINE_INTERACTION_SEQUENCE = ("observe", "check", "resolve")
MEDIATED_INTERACTION_SEQUENCE = ("observe", "resolve")


@dataclass(frozen=True, slots=True)
class NonThrashBurdenPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    commitment_id: str
    provenance_artifact_id: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str
    baseline_step_prefix: str
    mediated_step_prefix: str
    host_surface_phrase: str
    starting_event_phrase: str


def build_non_thrash_burden_snapshot(
    *,
    spec: NonThrashBurdenPairSpec,
    scenario_id: str,
    variant: str,
    observation_event_name: str,
    check_event_name: str,
    publication_event_name: str,
) -> dict[str, object]:
    baseline = variant == "baseline_non_mediated"
    interaction_sequence = (
        BASELINE_INTERACTION_SEQUENCE if baseline else MEDIATED_INTERACTION_SEQUENCE
    )
    step_prefix = spec.baseline_step_prefix if baseline else spec.mediated_step_prefix
    run_id = spec.baseline_run_id if baseline else spec.mediated_run_id
    event_map = {
        "observe": observation_event_name,
        "check": check_event_name,
        "resolve": publication_event_name,
    }
    steps: list[dict[str, object]] = []
    refs: list[str] = []
    for index, step_name in enumerate(interaction_sequence, start=1):
        step_id = f"{step_prefix}-{index}"
        refs.append(f"{step_id}:{event_map[step_name]}/{step_name}")
        steps.append(
            {
                "step_id": step_id,
                "raw_host_event_name": event_map[step_name],
                "interaction_step": step_name,
                "outcome_class": (
                    "certified-full-commitment"
                    if step_name == "resolve"
                    else "candidate-bearing"
                ),
            }
        )
    return {
        "scenario_id": scenario_id,
        "run_id": run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "interaction_sequence": list(interaction_sequence),
        "intervention_burden": float(len(interaction_sequence)),
        "contradiction_ref": f"{spec.contradiction_source_tag}:{spec.contradiction_summary}",
        "degradation_ref": spec.degradation_reason_code,
        "event_trace_refs": ", ".join(refs),
        "steps": steps,
    }


def build_non_thrash_burden_packet(
    *,
    spec: NonThrashBurdenPairSpec,
    scenario_id: str,
    host_family: str,
    variant: str,
    snapshot: dict[str, object],
    burden_ref: str,
) -> PacketSnapshot:
    sequence_text = " -> ".join(snapshot["interaction_sequence"])
    return build_reference_mediation_packet(
        scenario_id=scenario_id,
        run_id=str(snapshot["run_id"]),
        paired_episode_set_id=spec.pair_id,
        scenario_family="equal_value_burden_non_thrash",
        task_value_rubric_id="task_value_equal_completion",
        approval_or_environment_context_id="env_local_default",
        variant=variant,
        host_family=host_family,
        scenario_inputs={
            "starting_request_or_event": spec.starting_event_phrase,
            "host_surface": spec.host_surface_phrase,
            "declared_scenario_goal": (
                "evaluate whether mediation lowers visible burden at equal task value "
                "without relying on thrash-style branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "deterministic local default context with the same commitment boundary "
                "and the same host packet/publication surface on both sides of the pair"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The comparator reaches the same certified completion class and truth "
                "boundary on both sides of the pair."
            ),
            "branch_trajectory_summary": (
                f"This non-thrash comparator records `{sequence_text}` and does not rely "
                "on repeated `open -> suspend -> resume -> merge` churn."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit and the completion "
                "boundary is unchanged."
            ),
            "burden_summary": (
                f"Visible intervention burden is recorded as `intervention_burden={snapshot['intervention_burden']:.1f}` "
                "from the committed non-thrash interaction sequence."
            ),
            "host_realization_summary": (
                "This comparator is burden-focused and does not claim host-native "
                "opportunity specialization lift."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(snapshot["event_trace_refs"]),
            "contradiction_refs": str(snapshot["contradiction_ref"]),
            "degradation_refs": str(snapshot["degradation_ref"]),
            "aux_burden_refs_if_present": burden_ref,
            "evaluation_packet_refs_if_present": "none",
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This family is explicitly non-thrash and should not be used to restate "
                "the existing thrash burden claim.",
                "Thrash promotion should remain tied to branch-discipline and thrash-family counts.",
            ),
            "Better Branch Discipline": (
                "This family is not a branch-discipline verdict surface.",
                "Use the dedicated branch-discipline family for branch metrics.",
            ),
            "Better Uncertainty Handling": (
                "This family is not an uncertainty verdict surface.",
                "Use the uncertainty family for uncertainty-handling claims.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "This packet carries an explicit AUX burden artifact over the same "
                "completion class and truth boundary.",
                "The burden metric is `visible_intervention_steps` over the committed "
                "non-thrash interaction sequence.",
            ),
            "Better Host-Specialized Realization": (
                "This comparator preserves the same host surface but does not claim "
                "host-native opportunity specialization lift.",
                "Host-realization verdicts should continue to come from the dedicated "
                "host_realization family.",
            ),
        },
        exclusion_notes=(
            f"This packet is one side of `{spec.pair_id}`. It is deterministic burden "
            "evidence only and does not by itself justify mediation."
        ),
        reviewer_note=(
            "This is committed non-thrash burden evidence only. It does not justify "
            "mediation implementation and package-level evidence notes govern verdicts."
        ),
    )


def build_non_thrash_burden_artifact(
    *,
    scenario_id: str,
    pair_id: str,
    pair_key: str,
    run_id: str,
    variant: str,
    host_family: str,
    interaction_sequence: list[str],
) -> dict[str, object]:
    burden = AuxBurdenReport(
        intervention_burden=float(len(interaction_sequence)),
        metadata=(
            MetadataField("scenario_id", scenario_id),
            MetadataField("run_id", run_id),
            MetadataField("paired_episode_set_id", pair_id),
            MetadataField("host_family", host_family),
            MetadataField("burden_metric", "visible_intervention_steps"),
        ),
    )
    return {
        "status": "reviewed_evidence",
        "header": {
            "date": "2026-03-30",
            "status": "reviewed_evidence",
            "scenario_id": scenario_id,
            "run_id": run_id,
            "paired_episode_set_id": pair_id,
        },
        "variant_metadata": {
            "variant": variant,
            "host_family": host_family,
            "burden_metric": "visible_intervention_steps",
            "pair_key": pair_key,
        },
        "aux_burden_report": {
            "compute_overhead": f"{burden.compute_overhead:.1f}",
            "memory_overhead": f"{burden.memory_overhead:.1f}",
            "latency_overhead": f"{burden.latency_overhead:.1f}",
            "environment_query_cost": f"{burden.environment_query_cost:.1f}",
            "retrieval_cost": f"{burden.retrieval_cost:.1f}",
            "intervention_burden": f"{burden.intervention_burden:.1f}",
        },
        "metadata": {field.key: str(field.value) for field in burden.metadata},
        "derivation": {
            "interaction_sequence": " -> ".join(interaction_sequence),
            "step_count": str(len(interaction_sequence)),
            "note": (
                "Visible intervention burden is the exact committed non-thrash "
                "interaction-step count for this run."
            ),
        },
    }


def render_non_thrash_burden_artifact(
    relative_path: str,
    artifact: dict[str, object],
    *,
    scope_text: str,
) -> str:
    lines = [
        f"# {Path(relative_path).stem}",
        "",
        f"Date: {artifact['header']['date']}",
        f"Status: `{artifact['status']}`",
        "",
        "## Scope",
        "",
        scope_text,
        "",
        "## Header",
        "",
    ]
    for field_name, value in artifact["header"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Variant Metadata", ""])
    for field_name, value in artifact["variant_metadata"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Aux Burden Report", ""])
    for field_name, value in artifact["aux_burden_report"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Metadata", ""])
    for field_name, value in artifact["metadata"].items():
        lines.append(f"- {field_name}: `{value}`")
    lines.extend(["", "## Derivation", ""])
    for field_name, value in artifact["derivation"].items():
        if field_name == "note":
            lines.append(f"- {field_name}: {value}")
        else:
            lines.append(f"- {field_name}: `{value}`")
    lines.append("")
    return "\n".join(lines)


def emit_burden_artifacts(
    builders: Mapping[str, Callable[[], dict[str, object]]],
    *,
    renderer: Callable[[str, dict[str, object]], str],
) -> None:
    for index, (relative_path, builder) in enumerate(builders.items()):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(renderer(relative_path, builder()))
        if index != len(builders) - 1:
            sys.stdout.write("\n")


def render_non_thrash_packet(relative_path: str, packet: PacketSnapshot) -> str:
    lines = [
        f"# {Path(relative_path).stem}",
        "",
        f"Date: {packet['header']['date']}",
        f"Status: `{packet['status']}`",
        "",
        "## Scope",
        "",
        (
            "This committed run packet records one non-thrash burden mediation comparator "
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
