"""Shared identity for the first Gemini host-realization comparator pair."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeminiHostRealizationPairSpec:
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
            "docs/mediation_evidence/gemini/"
            "scenario_host_gemini_01__baseline_non_mediated__run_001.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/gemini/"
            "scenario_host_gemini_01__experimental_mediated__run_001.md"
        )


GEMINI_HOST_REALIZATION_PAIR_SPEC = GeminiHostRealizationPairSpec(
    pair_id="pair_gemini_host_001",
    baseline_run_id="gemini_host_realization_baseline_run_001",
    mediated_run_id="gemini_host_realization_mediated_run_001",
    session_id="gemini-host-packet-session-1",
    candidate_id="gemini-host-packet-candidate-1",
    commitment_id="gemini-host-packet-commit-1",
    provenance_artifact_id="gemini-host-artifact-1",
    contradiction_source_tag="gemini-host-publication-check",
    contradiction_summary="Gemini host publication evidence remains partially withheld",
    degradation_reason_code="gemini-host-publication-partial",
)
