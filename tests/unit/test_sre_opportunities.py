"""Focused unit tests for SRE host-native opportunity specialization."""

import pytest

from cortex.sre.families import SoftControlFamily
from cortex.sre.opportunities import (
    HostNativeOpportunity,
    specialize_host_native_opportunity,
)


def test_neutral_family_returns_no_direct_opportunity_specialization() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.NEUTRAL,
        (
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
                clearly_superior=True,
            ),
        ),
    )

    assert result.selected_family is SoftControlFamily.NEUTRAL
    assert result.preferred_opportunity is None
    assert result.direct_opportunity_specialization_used is False
    assert result.degradation_reason is None
    assert result.safer_fallback_family is None


def test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.SEEK_CONTEXT,
        (
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset(
                    {
                        SoftControlFamily.SEEK_CONTEXT,
                        SoftControlFamily.CHECK,
                    }
                ),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "structured-query"}),
            ),
        ),
    )

    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.direct_opportunity_specialization_used is True
    assert result.preferred_opportunity is not None
    assert result.preferred_opportunity.opportunity_ref == "mcp.query"
    assert result.preferred_opportunity.native_surface_tags == frozenset(
        {"mcp", "structured-query"}
    )


def test_host_native_opportunity_requires_non_empty_opportunity_ref() -> None:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.CHECK}),
    )

    assert opportunity.opportunity_ref == "mcp.query"

    with pytest.raises(
        ValueError,
        match="HostNativeOpportunity.opportunity_ref must be non-empty after trimming.",
    ):
        HostNativeOpportunity(
            opportunity_ref="   ",
            supported_families=frozenset({SoftControlFamily.CHECK}),
        )


def test_host_native_opportunity_requires_typed_supported_families() -> None:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.CHECK}),
    )

    assert opportunity.supported_families == frozenset({SoftControlFamily.CHECK})

    with pytest.raises(
        TypeError,
        match=(
            "HostNativeOpportunity.supported_families must contain only "
            "SoftControlFamily instances."
        ),
    ):
        HostNativeOpportunity(
            opportunity_ref="mcp.query",
            supported_families=frozenset({"check"}),
        )


def test_host_native_opportunity_requires_non_empty_native_surface_tags() -> None:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.CHECK}),
        native_surface_tags=frozenset({"mcp", "structured-query"}),
    )

    assert opportunity.native_surface_tags == frozenset({"mcp", "structured-query"})

    with pytest.raises(
        ValueError,
        match=(
            "HostNativeOpportunity.native_surface_tags must contain only "
            "non-empty values after trimming."
        ),
    ):
        HostNativeOpportunity(
            opportunity_ref="mcp.query",
            supported_families=frozenset({SoftControlFamily.CHECK}),
            native_surface_tags=frozenset({"   "}),
        )


def test_host_native_opportunity_requires_non_empty_degradation_reason_when_provided() -> None:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.CHECK}),
        realizable=False,
        degradation_reason="host-surface-unavailable",
    )

    assert opportunity.degradation_reason == "host-surface-unavailable"

    with pytest.raises(
        ValueError,
        match=(
            "HostNativeOpportunity.degradation_reason must be non-empty "
            "after trimming when provided."
        ),
    ):
        HostNativeOpportunity(
            opportunity_ref="mcp.query",
            supported_families=frozenset({SoftControlFamily.CHECK}),
            realizable=False,
            degradation_reason="   ",
        )


def test_opportunity_specialization_result_requires_typed_preferred_opportunity() -> None:
    preferred = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.CHECK}),
    )
    result = specialize_host_native_opportunity(
        SoftControlFamily.CHECK,
        (preferred,),
    )

    direct = type(result)(
        selected_family=SoftControlFamily.CHECK,
        preferred_opportunity=preferred,
        direct_opportunity_specialization_used=False,
    )

    assert direct.preferred_opportunity is preferred

    with pytest.raises(
        TypeError,
        match=(
            r"OpportunitySpecializationResult\.preferred_opportunity must be "
            r"HostNativeOpportunity \| None, got str\."
        ),
    ):
        type(result)(
            selected_family=SoftControlFamily.CHECK,
            preferred_opportunity="not-opportunity",
        )


def test_opportunity_specialization_result_requires_non_empty_degradation_reason() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.BRANCH,
        (
            HostNativeOpportunity(
                opportunity_ref="native-subagent",
                supported_families=frozenset({SoftControlFamily.BRANCH}),
                clearly_superior=True,
                realizable=False,
                degradation_reason="host-surface-unavailable",
                safer_fallback_family=SoftControlFamily.ESCALATE,
            ),
        ),
    )

    assert result.degradation_reason == "host-surface-unavailable"

    with pytest.raises(
        ValueError,
        match=(
            "OpportunitySpecializationResult.degradation_reason must be "
            "non-empty after trimming when provided."
        ),
    ):
        type(result)(
            selected_family=SoftControlFamily.CHECK,
            degradation_reason="   ",
            safer_fallback_family=SoftControlFamily.NEUTRAL,
        )


def test_opportunity_specialization_result_requires_typed_selected_family() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.NEUTRAL,
        (),
    )

    assert result.selected_family is SoftControlFamily.NEUTRAL

    with pytest.raises(
        TypeError,
        match=(
            r"OpportunitySpecializationResult\.selected_family must be "
            r"SoftControlFamily, got str\."
        ),
    ):
        type(result)(
            selected_family="check",
        )


def test_family_is_retained_when_no_clearly_superior_opportunity_exists() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.REDIRECT,
        (
            HostNativeOpportunity(
                opportunity_ref="context-switch",
                supported_families=frozenset({SoftControlFamily.REDIRECT}),
                clearly_superior=False,
            ),
        ),
    )

    assert result.selected_family is SoftControlFamily.REDIRECT
    assert result.preferred_opportunity is None
    assert result.direct_opportunity_specialization_used is False
    assert result.degradation_reason is None
    assert result.safer_fallback_family is None


def test_failed_specialization_surfaces_degradation_reason_and_safer_fallback() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.BRANCH,
        (
            HostNativeOpportunity(
                opportunity_ref="native-subagent",
                supported_families=frozenset({SoftControlFamily.BRANCH}),
                clearly_superior=True,
                realizable=False,
                degradation_reason="host-surface-unavailable",
                safer_fallback_family=SoftControlFamily.ESCALATE,
            ),
        ),
    )

    assert result.selected_family is SoftControlFamily.BRANCH
    assert result.direct_opportunity_specialization_used is False
    assert result.preferred_opportunity is not None
    assert result.preferred_opportunity.opportunity_ref == "native-subagent"
    assert result.degradation_reason == "host-surface-unavailable"
    assert result.safer_fallback_family is SoftControlFamily.ESCALATE


def test_selected_family_remains_distinct_from_direct_opportunity() -> None:
    result = specialize_host_native_opportunity(
        SoftControlFamily.CHECK,
        (
            HostNativeOpportunity(
                opportunity_ref="approval-request",
                supported_families=frozenset({SoftControlFamily.CHECK}),
                clearly_superior=True,
            ),
        ),
    )

    assert result.selected_family is SoftControlFamily.CHECK
    assert result.preferred_opportunity is not None
    assert result.preferred_opportunity.opportunity_ref == "approval-request"
    assert result.selected_family.value != result.preferred_opportunity.opportunity_ref
