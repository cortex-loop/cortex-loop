"""Runtime-backed helpers for reference host-realization evidence generation."""

from __future__ import annotations

from cortex.core.dispatch import DispatchLane
from cortex.core.environment import EXECUTION_TRACE, ExecutiveEnvironmentView
from cortex.hosts.reference.runtime import ReferenceRuntimeStepResult, run_reference_runtime_step
from cortex.sre.families import SoftControlFamily
from cortex.sre.mediation import ReferenceMediationMode
from tests.archive.legacy_integration._reference_host_realization_pairs import (
    DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    REFERENCE_HOST_REALIZATION_PAIR_SPECS,
)
from tests.conformance.integration._reference_lane import full_commitment_event


def build_reference_host_realization_runtime_step_result(
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    *,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
) -> ReferenceRuntimeStepResult:
    spec = REFERENCE_HOST_REALIZATION_PAIR_SPECS[pair_key]
    event_name, payload = full_commitment_event(
        commitment_id=spec.commitment_id,
        session_id=spec.session_id,
    )
    payload["result_artifact_ref"] = spec.provenance_artifact_id

    result = run_reference_runtime_step(
        event_name,
        payload,
        executive_environment_view=ExecutiveEnvironmentView(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-host", "local-cli-runtime"}),
        ),
        mediation_mode=mediation_mode,
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.commitment_result_kind == "certified"
    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    return result


def build_reference_host_realization_runtime_snapshot(
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    *,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
) -> dict[str, object]:
    result = build_reference_host_realization_runtime_step_result(
        pair_key,
        mediation_mode=mediation_mode,
    )
    mediation = result.control_ledger_summary["allocation_diagnostics"]["mediation"]

    assert isinstance(mediation, dict)
    return {
        "selected_family": result.selected_family.value,
        "realized_family": result.realized_family.value,
        "host_opportunity_refs": sorted(result.bound_event.lifecycle_surface.mcp_affordances),
        "mediation": mediation,
    }


__all__ = [
    "build_reference_host_realization_runtime_snapshot",
    "build_reference_host_realization_runtime_step_result",
]
