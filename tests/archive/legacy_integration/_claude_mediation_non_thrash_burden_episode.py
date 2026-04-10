"""Build deterministic Claude-host non-thrash burden baseline episodes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
import sys

from tests.archive.legacy_integration._mediation_non_thrash_burden_common import (
    NonThrashBurdenPairSpec,
    build_non_thrash_burden_artifact,
    build_non_thrash_burden_packet,
    build_non_thrash_burden_snapshot,
    emit_burden_artifacts,
    render_non_thrash_burden_artifact,
    render_non_thrash_packet,
)


DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY = "001"
CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class ClaudeNonThrashBurdenPairSpec(NonThrashBurdenPairSpec):
    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/claude/"
            f"scenario_burden_claude_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/claude/"
            f"scenario_burden_claude_01__experimental_mediated__run_{self.pair_key}.md"
        )

    @property
    def baseline_burden_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/claude/"
            f"scenario_burden_claude_01__baseline_non_mediated__run_{self.pair_key}__aux_burden.md"
        )

    @property
    def mediated_burden_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/claude/"
            f"scenario_burden_claude_01__experimental_mediated__run_{self.pair_key}__aux_burden.md"
        )


CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS: Mapping[str, ClaudeNonThrashBurdenPairSpec] = {
    "001": ClaudeNonThrashBurdenPairSpec(
        pair_key="001",
        pair_id="pair_claude_burden_001",
        baseline_run_id="claude_burden_baseline_run_001",
        mediated_run_id="claude_burden_mediated_run_001",
        session_id="claude-burden-session-1",
        commitment_id="claude-burden-commit-1",
        provenance_artifact_id="claude-burden-artifact-1",
        contradiction_source_tag="claude-burden-check",
        contradiction_summary="Claude burden evidence remained partially withheld",
        degradation_reason_code="claude-burden-partial",
        baseline_step_prefix="claude-burden-step",
        mediated_step_prefix="claude-burden-mediated-step",
        host_surface_phrase="Claude-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded Claude-host completion task with one non-thrash verification step before certified resolution",
    ),
    "002": ClaudeNonThrashBurdenPairSpec(
        pair_key="002",
        pair_id="pair_claude_burden_002",
        baseline_run_id="claude_burden_baseline_run_002",
        mediated_run_id="claude_burden_mediated_run_002",
        session_id="claude-burden-session-2",
        commitment_id="claude-burden-commit-2",
        provenance_artifact_id="claude-burden-artifact-2",
        contradiction_source_tag="claude-burden-receipt-check",
        contradiction_summary="Claude burden receipt remained partially withheld",
        degradation_reason_code="claude-burden-partial-002",
        baseline_step_prefix="claude-burden-002-step",
        mediated_step_prefix="claude-burden-002-mediated-step",
        host_surface_phrase="Claude-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded Claude-host completion task with one non-thrash verification step before certified resolution",
    ),
    "003": ClaudeNonThrashBurdenPairSpec(
        pair_key="003",
        pair_id="pair_claude_burden_003",
        baseline_run_id="claude_burden_baseline_run_003",
        mediated_run_id="claude_burden_mediated_run_003",
        session_id="claude-burden-session-3",
        commitment_id="claude-burden-commit-3",
        provenance_artifact_id="claude-burden-artifact-3",
        contradiction_source_tag="claude-burden-artifact-check",
        contradiction_summary="Claude burden artifact remained partially withheld",
        degradation_reason_code="claude-burden-partial-003",
        baseline_step_prefix="claude-burden-003-step",
        mediated_step_prefix="claude-burden-003-mediated-step",
        host_surface_phrase="Claude-host observe/check/resolve path with the same commitment boundary and no thrash-style branch churn",
        starting_event_phrase="bounded Claude-host completion task with one non-thrash verification step before certified resolution",
    ),
}


def build_claude_non_thrash_burden_episode_snapshot(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    return build_non_thrash_burden_snapshot(
        spec=CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key],
        scenario_id="scenario_burden_claude_01",
        variant="baseline_non_mediated",
        observation_event_name="content_block_delta",
        check_event_name="content_block_delta",
        publication_event_name="message_stop",
    )


def build_claude_non_thrash_burden_baseline_packet(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    return build_non_thrash_burden_packet(
        spec=spec,
        scenario_id="scenario_burden_claude_01",
        host_family="claude",
        variant="baseline_non_mediated",
        snapshot=build_claude_non_thrash_burden_episode_snapshot(pair_key),
        burden_ref=spec.baseline_burden_path,
    )


def build_claude_non_thrash_burden_baseline_artifact(
    pair_key: str = DEFAULT_CLAUDE_NON_THRASH_BURDEN_PAIR_KEY,
) -> dict[str, object]:
    spec = CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key]
    snapshot = build_claude_non_thrash_burden_episode_snapshot(pair_key)
    return build_non_thrash_burden_artifact(
        scenario_id="scenario_burden_claude_01",
        pair_id=spec.pair_id,
        pair_key=pair_key,
        run_id=spec.baseline_run_id,
        variant="baseline_non_mediated",
        host_family="claude",
        interaction_sequence=list(snapshot["interaction_sequence"]),
    )


CLAUDE_NON_THRASH_BURDEN_BASELINE_PACKET_PATHS = {
    pair_key: CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}
CLAUDE_NON_THRASH_BURDEN_BASELINE_PACKET_DOC_BUILDERS = {
    CLAUDE_NON_THRASH_BURDEN_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_claude_non_thrash_burden_baseline_packet, pair_key
    )
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}
CLAUDE_NON_THRASH_BURDEN_BASELINE_ARTIFACT_DOC_BUILDERS = {
    CLAUDE_NON_THRASH_BURDEN_PAIR_SPECS[pair_key].baseline_burden_path: partial(
        build_claude_non_thrash_burden_baseline_artifact, pair_key
    )
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS
}


def emit_claude_non_thrash_burden_baseline_candidate() -> None:
    for relative_path, builder in CLAUDE_NON_THRASH_BURDEN_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_non_thrash_packet(relative_path, builder()))
        sys.stdout.write("\n")
    emit_burden_artifacts(
        CLAUDE_NON_THRASH_BURDEN_BASELINE_ARTIFACT_DOC_BUILDERS,
        renderer=lambda relative_path, artifact: render_non_thrash_burden_artifact(
            relative_path,
            artifact,
            scope_text=(
                "This committed AUX burden artifact records one Claude-host baseline-only "
                "non-thrash burden measurement within the committed Claude non-thrash "
                "paired-run series for mediation evidence review.\n"
                "It does not justify mediation, authorize implementation work, or imply "
                "generic runtime burden beyond the visible intervention count recorded here."
            ),
        ),
    )

