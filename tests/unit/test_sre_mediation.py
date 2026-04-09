"""Focused unit tests for the bounded reference mediation finalizer."""

from __future__ import annotations

from experimental.sre.families import SoftControlFamily
from experimental.sre.mediation import (
    ReferenceMediationMode,
    finalize_reference_soft_control,
)
from experimental.sre.opportunities import HostNativeOpportunity


def test_reference_mediation_identity_mode_preserves_family_without_specialization() -> None:
    finalization = finalize_reference_soft_control(
        SoftControlFamily.SEEK_CONTEXT,
        mediation_mode=ReferenceMediationMode.IDENTITY,
        opportunities=(
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "structured-query"}),
            ),
        ),
    )

    assert finalization.selected_family_before_finalization is SoftControlFamily.SEEK_CONTEXT
    assert finalization.selected_family_after_finalization is SoftControlFamily.SEEK_CONTEXT
    assert finalization.opportunity_specialization.preferred_opportunity is None
    assert finalization.opportunity_specialization.direct_opportunity_specialization_used is False
    assert finalization.as_payload() == {
        "mediation_active": False,
        "mediation_identity": True,
        "selected_family_before_finalization": "seek-context",
        "selected_family_after_finalization": "seek-context",
        "preferred_opportunity_ref": None,
        "direct_opportunity_specialization_used": False,
        "mediation_reason_tags": ["mode:identity"],
    }


def test_reference_mediation_experimental_mode_specializes_seek_context_when_runtime_visible_opportunity_exists() -> None:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
        clearly_superior=True,
        native_surface_tags=frozenset({"mcp", "structured-query"}),
    )

    finalization = finalize_reference_soft_control(
        SoftControlFamily.SEEK_CONTEXT,
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
        opportunities=(opportunity,),
    )

    assert finalization.selected_family_after_finalization is SoftControlFamily.SEEK_CONTEXT
    assert finalization.opportunity_specialization.preferred_opportunity is opportunity
    assert finalization.opportunity_specialization.direct_opportunity_specialization_used is True
    assert finalization.as_payload()["mediation_active"] is True
    assert finalization.as_payload()["mediation_identity"] is False
    assert finalization.as_payload()["preferred_opportunity_ref"] == "mcp.query"


def test_reference_mediation_experimental_mode_keeps_identity_for_non_seek_context_family() -> None:
    finalization = finalize_reference_soft_control(
        SoftControlFamily.CHECK,
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
        opportunities=(),
    )

    assert finalization.selected_family_before_finalization is SoftControlFamily.CHECK
    assert finalization.selected_family_after_finalization is SoftControlFamily.CHECK
    assert finalization.opportunity_specialization.direct_opportunity_specialization_used is False
    assert finalization.as_payload()["mediation_active"] is False
    assert finalization.as_payload()["mediation_identity"] is True


def test_reference_mediation_experimental_mode_preserves_existing_degradation_fallback_semantics() -> None:
    degraded_opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
        clearly_superior=True,
        realizable=False,
        degradation_reason="host-surface-degraded",
        safer_fallback_family=SoftControlFamily.NEUTRAL,
        native_surface_tags=frozenset({"mcp", "structured-query"}),
    )

    finalization = finalize_reference_soft_control(
        SoftControlFamily.SEEK_CONTEXT,
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
        opportunities=(degraded_opportunity,),
    )

    assert finalization.selected_family_after_finalization is SoftControlFamily.SEEK_CONTEXT
    assert finalization.opportunity_specialization.preferred_opportunity is degraded_opportunity
    assert finalization.opportunity_specialization.direct_opportunity_specialization_used is False
    assert finalization.opportunity_specialization.degradation_reason == "host-surface-degraded"
    assert (
        finalization.opportunity_specialization.safer_fallback_family
        is SoftControlFamily.NEUTRAL
    )
    assert finalization.as_payload()["mediation_active"] is True
    assert finalization.as_payload()["mediation_identity"] is True
