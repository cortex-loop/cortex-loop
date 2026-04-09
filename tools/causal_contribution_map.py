"""Internal-only causal contribution classification for the E18 train."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

_EPSILON = 1e-9

ContributionClassification = Literal[
    "positive",
    "negative",
    "neutral",
    "mixed",
    "unresolved_env",
]


@dataclass(frozen=True, slots=True)
class OutputQualityMetrics:
    cortex_vs_raw: float
    cortex_vs_tooling_only: float
    cortex_objective_pass_count: int
    cortex_hidden_quality_pass_count: int
    env_blocked: bool = False


@dataclass(frozen=True, slots=True)
class VerifiedWorkMetrics:
    conformant_pack_count: int
    first_attempt_pass_count: int
    repair_conversion_count: int
    env_blocked: bool = False


@dataclass(frozen=True, slots=True)
class ContributionRunReading:
    label: str
    output_quality: OutputQualityMetrics
    verified_work: VerifiedWorkMetrics


def classify_component(
    *,
    baseline: ContributionRunReading,
    runs: tuple[ContributionRunReading, ...],
) -> ContributionClassification:
    if not runs:
        return "unresolved_env"
    if all(
        run.output_quality.env_blocked or run.verified_work.env_blocked
        for run in runs
    ):
        return "unresolved_env"

    all_worse = True
    any_worse = False
    all_better = True
    any_better = False
    any_material = False

    for run in runs:
        worse, better = _compare_against_baseline(baseline=baseline, candidate=run)
        any_material = any_material or worse or better
        any_worse = any_worse or worse
        any_better = any_better or better
        all_worse = all_worse and worse
        all_better = all_better and better

    if not any_material:
        return "neutral"
    if all_worse and not any_better:
        return "positive"
    if all_better and not any_worse:
        return "negative"
    return "mixed"


def has_material_delta(
    *,
    baseline: ContributionRunReading,
    candidate: ContributionRunReading,
) -> bool:
    worse, better = _compare_against_baseline(baseline=baseline, candidate=candidate)
    return worse or better


def render_causal_map_note(summary: dict[str, object]) -> str:
    analysis = summary.get("analysis")
    if isinstance(analysis, dict):
        classifications = analysis.get("component_classifications", {})
        next_lawful_move = analysis.get("next_lawful_move", "not recorded")
    else:
        classifications = summary.get("component_classifications", {})
        next_lawful_move = summary.get("next_lawful_move", "not recorded")
    lines = [
        "# CORTEX_V2_CAUSAL_MAP_NOTE_0",
        "",
        f"- train_name: `{summary.get('train_name', 'causal-contribution-map-openai')}`",
        f"- final_decision: `{summary.get('final_decision', 'none')}`",
        "",
        "## Component classifications",
        "",
    ]
    if isinstance(classifications, dict) and classifications:
        for label, payload in sorted(classifications.items()):
            if isinstance(payload, dict):
                classification = payload.get("classification", "unknown")
                reason = payload.get("reason", "<none>")
                lines.append(f"- `{label}`: `{classification}`")
                lines.append(f"  - {reason}")
    else:
        lines.append("- none recorded")
    lines.extend(
        [
            "",
            "## Next lawful move",
            "",
            str(next_lawful_move),
            "",
        ]
    )
    return "\n".join(lines)


def _compare_against_baseline(
    *,
    baseline: ContributionRunReading,
    candidate: ContributionRunReading,
) -> tuple[bool, bool]:
    worse = False
    better = False
    for metric, threshold in (
        (
            candidate.output_quality.cortex_vs_raw - baseline.output_quality.cortex_vs_raw,
            0.2,
        ),
        (
            candidate.output_quality.cortex_vs_tooling_only
            - baseline.output_quality.cortex_vs_tooling_only,
            0.2,
        ),
    ):
        if metric <= -(threshold - _EPSILON):
            worse = True
        if metric >= threshold - _EPSILON:
            better = True

    for metric in (
        candidate.output_quality.cortex_objective_pass_count
        - baseline.output_quality.cortex_objective_pass_count,
        candidate.output_quality.cortex_hidden_quality_pass_count
        - baseline.output_quality.cortex_hidden_quality_pass_count,
        candidate.verified_work.conformant_pack_count
        - baseline.verified_work.conformant_pack_count,
        candidate.verified_work.first_attempt_pass_count
        - baseline.verified_work.first_attempt_pass_count,
        candidate.verified_work.repair_conversion_count
        - baseline.verified_work.repair_conversion_count,
    ):
        if metric <= -1:
            worse = True
        if metric >= 1:
            better = True

    return worse, better


__all__ = [
    "ContributionClassification",
    "ContributionRunReading",
    "OutputQualityMetrics",
    "VerifiedWorkMetrics",
    "classify_component",
    "has_material_delta",
    "render_causal_map_note",
]
