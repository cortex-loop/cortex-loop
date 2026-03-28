"""Build OpenAI-only AUX burden artifacts for thrash mediation evidence."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
import sys

from cortex.aux.cost import AuxBurdenReport
from cortex.core.envelopes import MetadataField


BurdenArtifactSnapshot = dict[str, object]

_DATE = "2026-03-24"
_STATUS = "reviewed_evidence"
_BURDEN_METRIC = "visible_intervention_steps"
_SUMMARY_NOTE = (
    "Visible intervention burden is the exact committed branch-operation count for this "
    "run."
)


def openai_thrash_baseline_burden_artifact_path(pair_key: str) -> str:
    return (
        "docs/mediation_evidence/openai/"
        f"scenario_thrash_openai_01__baseline_non_mediated__run_{pair_key}__aux_burden.md"
    )


def openai_thrash_mediated_burden_artifact_path(pair_key: str) -> str:
    return (
        "docs/mediation_evidence/openai/"
        f"scenario_thrash_openai_01__experimental_mediated__run_{pair_key}__aux_burden.md"
    )


def build_openai_thrash_burden_artifact(
    *,
    pair_id: str,
    pair_key: str,
    run_id: str,
    variant: str,
    host_family: str,
    branch_sequence: list[str],
) -> BurdenArtifactSnapshot:
    step_count = len(branch_sequence)
    burden = AuxBurdenReport(
        intervention_burden=float(step_count),
        metadata=(
            MetadataField("scenario_id", "scenario_thrash_openai_01"),
            MetadataField("run_id", run_id),
            MetadataField("paired_episode_set_id", pair_id),
            MetadataField("host_family", host_family),
            MetadataField("burden_metric", _BURDEN_METRIC),
        ),
    )

    return {
        "status": _STATUS,
        "header": {
            "date": _DATE,
            "status": _STATUS,
            "scenario_id": "scenario_thrash_openai_01",
            "run_id": run_id,
            "paired_episode_set_id": pair_id,
        },
        "variant_metadata": {
            "variant": variant,
            "host_family": host_family,
            "burden_metric": _BURDEN_METRIC,
            "pair_key": pair_key,
        },
        "aux_burden_report": {
            "compute_overhead": _render_metric(burden.compute_overhead),
            "memory_overhead": _render_metric(burden.memory_overhead),
            "latency_overhead": _render_metric(burden.latency_overhead),
            "environment_query_cost": _render_metric(burden.environment_query_cost),
            "retrieval_cost": _render_metric(burden.retrieval_cost),
            "intervention_burden": _render_metric(burden.intervention_burden),
        },
        "metadata": {field.key: str(field.value) for field in burden.metadata},
        "derivation": {
            "branch_sequence": " -> ".join(branch_sequence),
            "step_count": str(step_count),
            "note": _SUMMARY_NOTE,
        },
    }


def render_openai_thrash_burden_artifact(
    relative_path: str,
    artifact: BurdenArtifactSnapshot,
) -> str:
    variant = str(artifact["variant_metadata"]["variant"])
    lines = [
        f"# {Path(relative_path).stem}",
        "",
        f"Date: {artifact['header']['date']}",
        f"Status: `{artifact['status']}`",
        "",
        "## Scope",
        "",
        _scope_text(variant),
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


def emit_openai_thrash_burden_artifacts(
    builders: Mapping[str, Callable[[], BurdenArtifactSnapshot]],
) -> None:
    for index, (relative_path, builder) in enumerate(builders.items()):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_openai_thrash_burden_artifact(relative_path, builder()))
        if index != len(builders) - 1:
            sys.stdout.write("\n")


def _render_metric(value: float) -> str:
    return f"{value:.1f}"


def _scope_text(variant: str) -> str:
    if variant == "baseline_non_mediated":
        return (
            "This committed AUX burden artifact records one OpenAI-host baseline-only "
            "thrash burden measurement within the committed OpenAI thrash paired-run "
            "series for mediation evidence review.\n"
            "It does not justify mediation, authorize implementation work, or imply "
            "generic runtime burden beyond the visible intervention count recorded here."
        )
    return (
        "This committed AUX burden artifact records one OpenAI-host experimental "
        "mediated thrash burden measurement within the committed OpenAI thrash "
        "paired-run series for mediation evidence review.\n"
        "It does not justify mediation, authorize implementation work, or imply "
        "generic runtime burden beyond the visible intervention count recorded here."
    )
