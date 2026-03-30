"""Shared pair specifications for Claude host-realization evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


DEFAULT_CLAUDE_HOST_REALIZATION_PAIR_KEY = "001"
CLAUDE_HOST_REALIZATION_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class ClaudeHostRealizationPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    message_id: str
    candidate_id: str
    commitment_id: str
    provenance_artifact_id: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str

    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/claude/"
            f"scenario_host_claude_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/claude/"
            f"scenario_host_claude_01__experimental_mediated__run_{self.pair_key}.md"
        )


CLAUDE_HOST_REALIZATION_PAIR_SPECS: Mapping[str, ClaudeHostRealizationPairSpec] = {
    "001": ClaudeHostRealizationPairSpec(
        pair_key="001",
        pair_id="pair_claude_host_001",
        baseline_run_id="claude_host_realization_baseline_run_001",
        mediated_run_id="claude_host_realization_mediated_run_001",
        session_id="claude-host-packet-session-1",
        message_id="cl-host-msg-1",
        candidate_id="cl-host-packet-candidate-1",
        commitment_id="cl-host-packet-commit-1",
        provenance_artifact_id="claude-host-artifact-1",
        contradiction_source_tag="claude-host-publication-check",
        contradiction_summary="Claude host publication evidence remains partially withheld",
        degradation_reason_code="claude-host-publication-partial",
    ),
    "002": ClaudeHostRealizationPairSpec(
        pair_key="002",
        pair_id="pair_claude_host_002",
        baseline_run_id="claude_host_realization_baseline_run_002",
        mediated_run_id="claude_host_realization_mediated_run_002",
        session_id="claude-host-packet-session-2",
        message_id="cl-host-msg-2",
        candidate_id="cl-host-packet-candidate-2",
        commitment_id="cl-host-packet-commit-2",
        provenance_artifact_id="claude-host-artifact-2",
        contradiction_source_tag="claude-host-receipt-check",
        contradiction_summary="Claude structured query result omitted one confirmation field",
        degradation_reason_code="claude-host-publication-partial-002",
    ),
    "003": ClaudeHostRealizationPairSpec(
        pair_key="003",
        pair_id="pair_claude_host_003",
        baseline_run_id="claude_host_realization_baseline_run_003",
        mediated_run_id="claude_host_realization_mediated_run_003",
        session_id="claude-host-packet-session-3",
        message_id="cl-host-msg-3",
        candidate_id="cl-host-packet-candidate-3",
        commitment_id="cl-host-packet-commit-3",
        provenance_artifact_id="claude-host-artifact-3",
        contradiction_source_tag="claude-host-artifact-check",
        contradiction_summary="Claude supporting artifact trace remained partial",
        degradation_reason_code="claude-host-publication-partial-003",
    ),
}

CLAUDE_HOST_REALIZATION_PAIR_SPEC = CLAUDE_HOST_REALIZATION_PAIR_SPECS[
    DEFAULT_CLAUDE_HOST_REALIZATION_PAIR_KEY
]
