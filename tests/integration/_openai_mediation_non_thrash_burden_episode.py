"""Build deterministic OpenAI-host non-thrash burden baseline episodes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
import sys

from tests.integration._mediation_non_thrash_burden_common import (
    NonThrashBurdenPairSpec,
    build_non_thrash_burden_artifact,
    build_non_thrash_burden_packet,
    build_non_thrash_burden_snapshot,
    emit_burden_artifacts,
    render_non_thrash_burden_artifact,
    render_non_thrash_packet,
)


DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY = "001"
OPENAI_NON_THRASH_BURDEN_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class OpenAINonThrashBurdenPairSpec(NonThrashBurdenPairSpec):
    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_burden_openai_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_burden_openai_01__experimental_mediated__run_{self.pair_key}.md"
        )

    @property
    def baseline_burden_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_burden_openai_01__baseline_non_mediated__run_{self.pair_key}__aux_burden.md"
        )

    @property
    def mediated_burden_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_burden_openai_01__experimental_mediated__run_{self.pair_key}__aux_burden.md"
        )


OPENAI_NON_THRASH_BURDEN_PAIR_SPECS: Mapping[str, OpenAINonThrashBurdenPairSpec] = {
    "001": OpenAINonThrashBurdenPairSpec(
        pair_key="001",
        pair_id="pair_openai_burden_001",
        baseline_run_id="openai_burden_baseline_run_001",
        mediated_run_id="openai_burden_mediated_run_001",
        session_id="openai-burden-session-1",
        commitment_id="openai-burden-commit-1",
        provenance_artifact_id="openai-burden-artifact-1",
        contradiction_source_tag="openai-burden-check",
        contradiction_summary="OpenAI burden evidence remained partially withheld",
        degradation_reason_code="openai-burden-partial",
        baseline_step_prefix="openai-burden-step",
        mediated_step_prefix="openai-burden-mediated-step",
        host_surface_phrase="OpenAI-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded OpenAI-host completion task with one non-thrash verification step before certified resolution",
    ),
    "002": OpenAINonThrashBurdenPairSpec(
        pair_key="002",
        pair_id="pair_openai_burden_002",
        baseline_run_id="openai_burden_baseline_run_002",
        mediated_run_id="openai_burden_mediated_run_002",
        session_id="openai-burden-session-2",
        commitment_id="openai-burden-commit-2",
        provenance_artifact_id="openai-burden-artifact-2",
        contradiction_source_tag="openai-burden-receipt-check",
        contradiction_summary="OpenAI burden receipt remained partially withheld",
        degradation_reason_code="openai-burden-partial-002",
        baseline_step_prefix="openai-burden-002-step",
        mediated_step_prefix="openai-burden-002-mediated-step",
        host_surface_phrase="OpenAI-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded OpenAI-host completion task with one non-thrash verification step before certified resolution",
    ),
    "003": OpenAINonThrashBurdenPairSpec(
        pair_key="003",
        pair_id="pair_openai_burden_003",
        baseline_run_id="openai_burden_baseline_run_003",
        mediated_run_id="openai_burden_mediated_run_003",
        session_id="openai-burden-session-3",
        commitment_id="openai-burden-commit-3",
        provenance_artifact_id="openai-burden-artifact-3",
        contradiction_source_tag="openai-burden-artifact-check",
        contradiction_summary="OpenAI burden artifact remained partially withheld",
        degradation_reason_code="openai-burden-partial-003",
        baseline_step_prefix="openai-burden-003-step",
        mediated_step_prefix="openai-burden-003-mediated-step",
        host_surface_phrase="OpenAI-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded OpenAI-host completion task with one non-thrash verification step before certified resolution",
    ),
}


def build_openai_non_thrash_burden_episode_snapshot(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    return build_non_thrash_burden_snapshot(
        spec=OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key],
        scenario_id="scenario_burden_openai_01",
        variant="baseline_non_mediated",
        observation_event_name="response.output_text.delta",
        check_event_name="response.output_text.delta",
        publication_event_name="response.completed",
    )


def build_openai_non_thrash_burden_baseline_packet(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    return build_non_thrash_burden_packet(
        spec=spec,
        scenario_id="scenario_burden_openai_01",
        host_family="openai",
        variant="baseline_non_mediated",
        snapshot=build_openai_non_thrash_burden_episode_snapshot(pair_key),
        burden_ref=spec.baseline_burden_path,
    )


def build_openai_non_thrash_burden_baseline_artifact(
    pair_key: str = DEFAULT_OPENAI_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    snapshot = build_openai_non_thrash_burden_episode_snapshot(pair_key)
    return build_non_thrash_burden_artifact(
        scenario_id="scenario_burden_openai_01",
        pair_id=spec.pair_id,
        pair_key=pair_key,
        run_id=spec.baseline_run_id,
        variant="baseline_non_mediated",
        host_family="openai",
        interaction_sequence=list(snapshot["interaction_sequence"]),
    )


OPENAI_NON_THRASH_BURDEN_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}
OPENAI_NON_THRASH_BURDEN_BASELINE_PACKET_DOC_BUILDERS = {
    OPENAI_NON_THRASH_BURDEN_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_openai_non_thrash_burden_baseline_packet, pair_key
    )
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}
OPENAI_NON_THRASH_BURDEN_BASELINE_ARTIFACT_DOC_BUILDERS = {
    OPENAI_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].baseline_burden_path: partial(
        build_openai_non_thrash_burden_baseline_artifact, pair_key
    )
    for pair_key in OPENAI_NON_THRASH_BURDEN_PAIR_KEYS
}


def emit_openai_non_thrash_burden_baseline_candidate() -> None:
    for relative_path, builder in OPENAI_NON_THRASH_BURDEN_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_non_thrash_packet(relative_path, builder()))
        sys.stdout.write("\n")
    emit_burden_artifacts(
        OPENAI_NON_THRASH_BURDEN_BASELINE_ARTIFACT_DOC_BUILDERS,
        renderer=lambda relative_path, artifact: render_non_thrash_burden_artifact(
            relative_path,
            artifact,
            scope_text=(
                "This committed AUX burden artifact records one OpenAI-host baseline-only "
                "non-thrash burden measurement within the committed OpenAI non-thrash "
                "paired-run series for mediation evidence review.\n"
                "It does not justify mediation, authorize implementation work, or imply "
                "generic runtime burden beyond the visible intervention count recorded here."
            ),
        ),
    )

