"""Build deterministic OpenAI-host branch-discipline baseline episodes."""

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


DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY = "001"
OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class OpenAIBranchDisciplinePairSpec(BranchDisciplinePairSpec):
    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_branch_openai_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/openai/"
            f"scenario_branch_openai_01__experimental_mediated__run_{self.pair_key}.md"
        )


OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS: Mapping[str, OpenAIBranchDisciplinePairSpec] = {
    "001": OpenAIBranchDisciplinePairSpec(
        pair_key="001",
        pair_id="pair_openai_branch_001",
        baseline_run_id="openai_branch_baseline_run_001",
        mediated_run_id="openai_branch_mediated_run_001",
        session_id="openai-branch-session-1",
        candidate_id="openai-branch-candidate-1",
        commitment_id="openai-branch-commit-1",
        provenance_artifact_id="openai-branch-artifact-1",
        branch_track_ref="openai-branch-track-1",
        contradiction_source_tag="openai-branch-check",
        contradiction_summary="OpenAI branch review remained partially unresolved",
        degradation_reason_code="openai-branch-partial",
        baseline_step_prefix="openai-branch-step",
        mediated_step_prefix="openai-branch-mediated-step",
        host_surface_phrase="OpenAI-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded OpenAI-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "002": OpenAIBranchDisciplinePairSpec(
        pair_key="002",
        pair_id="pair_openai_branch_002",
        baseline_run_id="openai_branch_baseline_run_002",
        mediated_run_id="openai_branch_mediated_run_002",
        session_id="openai-branch-session-2",
        candidate_id="openai-branch-candidate-2",
        commitment_id="openai-branch-commit-2",
        provenance_artifact_id="openai-branch-artifact-2",
        branch_track_ref="openai-branch-track-2",
        contradiction_source_tag="openai-branch-receipt-check",
        contradiction_summary="OpenAI branch receipt review remained partially unresolved",
        degradation_reason_code="openai-branch-partial-002",
        baseline_step_prefix="openai-branch-002-step",
        mediated_step_prefix="openai-branch-002-mediated-step",
        host_surface_phrase="OpenAI-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded OpenAI-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "003": OpenAIBranchDisciplinePairSpec(
        pair_key="003",
        pair_id="pair_openai_branch_003",
        baseline_run_id="openai_branch_baseline_run_003",
        mediated_run_id="openai_branch_mediated_run_003",
        session_id="openai-branch-session-3",
        candidate_id="openai-branch-candidate-3",
        commitment_id="openai-branch-commit-3",
        provenance_artifact_id="openai-branch-artifact-3",
        branch_track_ref="openai-branch-track-3",
        contradiction_source_tag="openai-branch-artifact-check",
        contradiction_summary="OpenAI branch artifact review remained partially unresolved",
        degradation_reason_code="openai-branch-partial-003",
        baseline_step_prefix="openai-branch-003-step",
        mediated_step_prefix="openai-branch-003-mediated-step",
        host_surface_phrase="OpenAI-host branch-review and commitment publication path with landed SRE branch carriers",
        starting_event_phrase="bounded OpenAI-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
}


def build_openai_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_openai_01",
        variant="baseline_non_mediated",
        candidate_event_name="response.output_text.delta",
        publication_event_name="response.completed",
    )


def build_openai_branch_discipline_baseline_packet(
    pair_key: str = DEFAULT_OPENAI_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_openai_01",
        host_family="openai",
        variant="baseline_non_mediated",
        snapshot=build_openai_branch_discipline_episode_snapshot(pair_key),
    )


OPENAI_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS = {
    pair_key: OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS
}
OPENAI_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS = {
    OPENAI_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_openai_branch_discipline_baseline_packet, pair_key
    )
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_openai_branch_discipline_baseline_candidate() -> None:
    for relative_path, builder in OPENAI_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

