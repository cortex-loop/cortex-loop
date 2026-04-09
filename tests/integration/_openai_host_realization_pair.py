"""Shared pair specifications for OpenAI host-realization evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


DEFAULT_OPENAI_HOST_REALIZATION_PAIR_KEY = "001"
OPENAI_HOST_REALIZATION_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class OpenAIHostRealizationPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    candidate_id: str
    commitment_id: str
    provenance_artifact_id: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str

    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/openai/"
            f"scenario_host_openai_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/openai/"
            f"scenario_host_openai_01__experimental_mediated__run_{self.pair_key}.md"
        )


OPENAI_HOST_REALIZATION_PAIR_SPECS: Mapping[str, OpenAIHostRealizationPairSpec] = {
    "001": OpenAIHostRealizationPairSpec(
        pair_key="001",
        pair_id="pair_openai_host_001",
        baseline_run_id="openai_host_realization_baseline_run_001",
        mediated_run_id="openai_host_realization_mediated_run_001",
        session_id="openai-host-packet-session-1",
        candidate_id="openai-host-packet-candidate-1",
        commitment_id="openai-host-packet-commit-1",
        provenance_artifact_id="openai-host-artifact-1",
        contradiction_source_tag="openai-host-publication-check",
        contradiction_summary="OpenAI host publication evidence remains partially withheld",
        degradation_reason_code="openai-host-publication-partial",
    ),
    "002": OpenAIHostRealizationPairSpec(
        pair_key="002",
        pair_id="pair_openai_host_002",
        baseline_run_id="openai_host_realization_baseline_run_002",
        mediated_run_id="openai_host_realization_mediated_run_002",
        session_id="openai-host-packet-session-2",
        candidate_id="openai-host-packet-candidate-2",
        commitment_id="openai-host-packet-commit-2",
        provenance_artifact_id="openai-host-artifact-2",
        contradiction_source_tag="openai-host-receipt-check",
        contradiction_summary="OpenAI structured query result omitted one confirmation field",
        degradation_reason_code="openai-host-publication-partial-002",
    ),
    "003": OpenAIHostRealizationPairSpec(
        pair_key="003",
        pair_id="pair_openai_host_003",
        baseline_run_id="openai_host_realization_baseline_run_003",
        mediated_run_id="openai_host_realization_mediated_run_003",
        session_id="openai-host-packet-session-3",
        candidate_id="openai-host-packet-candidate-3",
        commitment_id="openai-host-packet-commit-3",
        provenance_artifact_id="openai-host-artifact-3",
        contradiction_source_tag="openai-host-artifact-check",
        contradiction_summary="OpenAI supporting artifact trace remained partial",
        degradation_reason_code="openai-host-publication-partial-003",
    ),
}

OPENAI_HOST_REALIZATION_PAIR_SPEC = OPENAI_HOST_REALIZATION_PAIR_SPECS[
    DEFAULT_OPENAI_HOST_REALIZATION_PAIR_KEY
]
