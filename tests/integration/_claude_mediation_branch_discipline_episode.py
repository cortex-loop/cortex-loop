"""Build deterministic Claude-host branch-discipline baseline episodes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
import sys

from tests.integration._mediation_branch_discipline_common import (
    BranchDisciplinePairSpec,
    build_branch_discipline_packet,
    build_branch_discipline_snapshot,
    render_branch_discipline_packet,
)


DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY = "001"
CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class ClaudeBranchDisciplinePairSpec(BranchDisciplinePairSpec):
    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/claude/"
            f"scenario_branch_claude_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/claude/"
            f"scenario_branch_claude_01__experimental_mediated__run_{self.pair_key}.md"
        )


CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS: Mapping[str, ClaudeBranchDisciplinePairSpec] = {
    "001": ClaudeBranchDisciplinePairSpec(
        pair_key="001",
        pair_id="pair_claude_branch_001",
        baseline_run_id="claude_branch_baseline_run_001",
        mediated_run_id="claude_branch_mediated_run_001",
        session_id="claude-branch-session-1",
        candidate_id="claude-branch-candidate-1",
        commitment_id="claude-branch-commit-1",
        provenance_artifact_id="claude-branch-artifact-1",
        branch_track_ref="claude-branch-track-1",
        contradiction_source_tag="claude-branch-check",
        contradiction_summary="Claude branch review remained partially unresolved",
        degradation_reason_code="claude-branch-partial",
        baseline_step_prefix="claude-branch-step",
        mediated_step_prefix="claude-branch-mediated-step",
        host_surface_phrase="Claude-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded Claude-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "002": ClaudeBranchDisciplinePairSpec(
        pair_key="002",
        pair_id="pair_claude_branch_002",
        baseline_run_id="claude_branch_baseline_run_002",
        mediated_run_id="claude_branch_mediated_run_002",
        session_id="claude-branch-session-2",
        candidate_id="claude-branch-candidate-2",
        commitment_id="claude-branch-commit-2",
        provenance_artifact_id="claude-branch-artifact-2",
        branch_track_ref="claude-branch-track-2",
        contradiction_source_tag="claude-branch-receipt-check",
        contradiction_summary="Claude branch receipt review remained partially unresolved",
        degradation_reason_code="claude-branch-partial-002",
        baseline_step_prefix="claude-branch-002-step",
        mediated_step_prefix="claude-branch-002-mediated-step",
        host_surface_phrase="Claude-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded Claude-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "003": ClaudeBranchDisciplinePairSpec(
        pair_key="003",
        pair_id="pair_claude_branch_003",
        baseline_run_id="claude_branch_baseline_run_003",
        mediated_run_id="claude_branch_mediated_run_003",
        session_id="claude-branch-session-3",
        candidate_id="claude-branch-candidate-3",
        commitment_id="claude-branch-commit-3",
        provenance_artifact_id="claude-branch-artifact-3",
        branch_track_ref="claude-branch-track-3",
        contradiction_source_tag="claude-branch-artifact-check",
        contradiction_summary="Claude branch artifact review remained partially unresolved",
        degradation_reason_code="claude-branch-partial-003",
        baseline_step_prefix="claude-branch-003-step",
        mediated_step_prefix="claude-branch-003-mediated-step",
        host_surface_phrase="Claude-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded Claude-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
}


def build_claude_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_claude_01",
        variant="baseline_non_mediated",
        candidate_event_name="content_block_delta",
        publication_event_name="message_stop",
    )


def build_claude_branch_discipline_baseline_packet(
    pair_key: str = DEFAULT_CLAUDE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_claude_01",
        host_family="claude",
        variant="baseline_non_mediated",
        snapshot=build_claude_branch_discipline_episode_snapshot(pair_key),
    )


CLAUDE_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS = {
    pair_key: CLAUDE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS
}
CLAUDE_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS = {
    CLAUDE_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_claude_branch_discipline_baseline_packet, pair_key
    )
    for pair_key in CLAUDE_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_claude_branch_discipline_baseline_candidate() -> None:
    for relative_path, builder in CLAUDE_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

