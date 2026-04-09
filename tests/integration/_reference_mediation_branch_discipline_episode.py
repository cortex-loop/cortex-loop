"""Build deterministic reference-host branch-discipline baseline episodes."""

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


DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY = "001"
REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class ReferenceBranchDisciplinePairSpec(BranchDisciplinePairSpec):
    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/reference/"
            f"scenario_branch_reference_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/reference/"
            f"scenario_branch_reference_01__experimental_mediated__run_{self.pair_key}.md"
        )


REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS: Mapping[str, ReferenceBranchDisciplinePairSpec] = {
    "001": ReferenceBranchDisciplinePairSpec(
        pair_key="001",
        pair_id="pair_reference_branch_001",
        baseline_run_id="reference_branch_baseline_run_001",
        mediated_run_id="reference_branch_mediated_run_001",
        session_id="reference-branch-session-1",
        candidate_id="reference-branch-candidate-1",
        commitment_id="reference-branch-commit-1",
        provenance_artifact_id="reference-branch-artifact-1",
        branch_track_ref="reference-branch-track-1",
        contradiction_source_tag="reference-branch-check",
        contradiction_summary="reference branch review remained partially unresolved",
        degradation_reason_code="reference-branch-partial",
        baseline_step_prefix="reference-branch-step",
        mediated_step_prefix="reference-branch-mediated-step",
        host_surface_phrase="reference-host branch-control and commitment path with landed SRE branch carriers",
        starting_event_phrase="bounded reference-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "002": ReferenceBranchDisciplinePairSpec(
        pair_key="002",
        pair_id="pair_reference_branch_002",
        baseline_run_id="reference_branch_baseline_run_002",
        mediated_run_id="reference_branch_mediated_run_002",
        session_id="reference-branch-session-2",
        candidate_id="reference-branch-candidate-2",
        commitment_id="reference-branch-commit-2",
        provenance_artifact_id="reference-branch-artifact-2",
        branch_track_ref="reference-branch-track-2",
        contradiction_source_tag="reference-branch-receipt-check",
        contradiction_summary="reference branch receipt review remained partially unresolved",
        degradation_reason_code="reference-branch-partial-002",
        baseline_step_prefix="reference-branch-002-step",
        mediated_step_prefix="reference-branch-002-mediated-step",
        host_surface_phrase="reference-host branch-control and commitment path with landed SRE branch carriers",
        starting_event_phrase="bounded reference-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
    "003": ReferenceBranchDisciplinePairSpec(
        pair_key="003",
        pair_id="pair_reference_branch_003",
        baseline_run_id="reference_branch_baseline_run_003",
        mediated_run_id="reference_branch_mediated_run_003",
        session_id="reference-branch-session-3",
        candidate_id="reference-branch-candidate-3",
        commitment_id="reference-branch-commit-3",
        provenance_artifact_id="reference-branch-artifact-3",
        branch_track_ref="reference-branch-track-3",
        contradiction_source_tag="reference-branch-artifact-check",
        contradiction_summary="reference branch artifact review remained partially unresolved",
        degradation_reason_code="reference-branch-partial-003",
        baseline_step_prefix="reference-branch-003-step",
        mediated_step_prefix="reference-branch-003-mediated-step",
        host_surface_phrase="reference-host branch-control and commitment path with landed SRE branch carriers",
        starting_event_phrase="bounded reference-host branch-review task with one candidate-bearing branch detour before certified completion",
    ),
}


def build_reference_branch_discipline_episode_snapshot(
    pair_key: str = DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_snapshot(
        spec=REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_reference_01",
        variant="baseline_non_mediated",
        candidate_event_name="ApprovalRequest",
        publication_event_name="ApprovalResult",
    )


def build_reference_branch_discipline_baseline_packet(
    pair_key: str = DEFAULT_REFERENCE_BRANCH_DISCIPLINE_PAIR_KEY,
) -> dict[str, object]:
    return build_branch_discipline_packet(
        spec=REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key],
        scenario_id="scenario_branch_reference_01",
        host_family="reference",
        variant="baseline_non_mediated",
        snapshot=build_reference_branch_discipline_episode_snapshot(pair_key),
    )


REFERENCE_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS = {
    pair_key: REFERENCE_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].baseline_packet_path
    for pair_key in REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS
}
REFERENCE_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS = {
    REFERENCE_BRANCH_DISCIPLINE_BASELINE_PACKET_PATHS[pair_key]: partial(
        build_reference_branch_discipline_baseline_packet, pair_key
    )
    for pair_key in REFERENCE_BRANCH_DISCIPLINE_PAIR_KEYS
}


def emit_reference_branch_discipline_baseline_candidate() -> None:
    for relative_path, builder in REFERENCE_BRANCH_DISCIPLINE_BASELINE_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_branch_discipline_packet(relative_path, builder()))

