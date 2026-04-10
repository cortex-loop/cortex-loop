"""Shared pair specifications for reference host-realization evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY = "001"
REFERENCE_HOST_REALIZATION_PAIR_KEYS = ("001", "002", "003")


@dataclass(frozen=True, slots=True)
class ReferenceHostRealizationPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    commitment_id: str
    provenance_artifact_id: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str

    @property
    def candidate_id(self) -> str:
        return self.commitment_id

    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/reference/"
            f"scenario_host_reference_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/reference/"
            f"scenario_host_reference_01__experimental_mediated__run_{self.pair_key}.md"
        )


REFERENCE_HOST_REALIZATION_PAIR_SPECS: Mapping[str, ReferenceHostRealizationPairSpec] = {
    "001": ReferenceHostRealizationPairSpec(
        pair_key="001",
        pair_id="pair_reference_host_001",
        baseline_run_id="reference_host_realization_baseline_run_001",
        mediated_run_id="reference_host_realization_mediated_run_001",
        session_id="packet-session-1",
        commitment_id="commit-packet-1",
        provenance_artifact_id="artifact-packet-1",
        contradiction_source_tag="host-check",
        contradiction_summary="write receipt was incomplete",
        degradation_reason_code="host-surface-degraded",
    ),
    "002": ReferenceHostRealizationPairSpec(
        pair_key="002",
        pair_id="pair_reference_host_002",
        baseline_run_id="reference_host_realization_baseline_run_002",
        mediated_run_id="reference_host_realization_mediated_run_002",
        session_id="packet-session-2",
        commitment_id="commit-packet-2",
        provenance_artifact_id="artifact-packet-2",
        contradiction_source_tag="receipt-check",
        contradiction_summary="structured query result omitted one confirmation field",
        degradation_reason_code="host-surface-degraded-002",
    ),
    "003": ReferenceHostRealizationPairSpec(
        pair_key="003",
        pair_id="pair_reference_host_003",
        baseline_run_id="reference_host_realization_baseline_run_003",
        mediated_run_id="reference_host_realization_mediated_run_003",
        session_id="packet-session-3",
        commitment_id="commit-packet-3",
        provenance_artifact_id="artifact-packet-3",
        contradiction_source_tag="artifact-check",
        contradiction_summary="supporting artifact trace remained partial",
        degradation_reason_code="host-surface-degraded-003",
    ),
}
