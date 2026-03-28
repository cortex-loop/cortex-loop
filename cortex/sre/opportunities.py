"""Bounded host-native opportunity specialization for the reference SRE."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .families import SoftControlFamily

_SAFE_FALLBACK_FAMILIES = frozenset(
    {
        SoftControlFamily.NEUTRAL,
        SoftControlFamily.ESCALATE,
    }
)


@dataclass(frozen=True, slots=True)
class HostNativeOpportunity:
    opportunity_ref: str
    supported_families: frozenset[SoftControlFamily]
    clearly_superior: bool = False
    realizable: bool = True
    degradation_reason: str | None = None
    safer_fallback_family: SoftControlFamily | None = None
    native_surface_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.opportunity_ref.strip():
            raise ValueError(
                "HostNativeOpportunity.opportunity_ref must be non-empty after trimming."
            )
        if any(
            not isinstance(family, SoftControlFamily)
            for family in self.supported_families
        ):
            raise TypeError(
                "HostNativeOpportunity.supported_families must contain only "
                "SoftControlFamily instances."
            )
        if any(not native_surface_tag.strip() for native_surface_tag in self.native_surface_tags):
            raise ValueError(
                "HostNativeOpportunity.native_surface_tags must contain only non-empty values after trimming."
            )
        if not self.supported_families:
            raise ValueError("HostNativeOpportunity.supported_families must not be empty.")
        if self.safer_fallback_family not in _SAFE_FALLBACK_FAMILIES | {None}:
            raise ValueError(
                "HostNativeOpportunity.safer_fallback_family must be neutral, "
                "escalate, or None."
            )
        if self.realizable and self.degradation_reason is not None:
            raise ValueError(
                "HostNativeOpportunity.degradation_reason is only valid when "
                "realizable is False."
            )
        if self.degradation_reason is not None and not self.degradation_reason.strip():
            raise ValueError(
                "HostNativeOpportunity.degradation_reason must be non-empty after trimming when provided."
            )
        if self.realizable and self.safer_fallback_family is not None:
            raise ValueError(
                "HostNativeOpportunity.safer_fallback_family is only valid when "
                "realizable is False."
            )
        if not self.realizable and not self.degradation_reason:
            raise ValueError(
                "HostNativeOpportunity must explain degradation when realizable is False."
            )


@dataclass(frozen=True, slots=True)
class OpportunitySpecializationResult:
    selected_family: SoftControlFamily
    preferred_opportunity: HostNativeOpportunity | None = None
    direct_opportunity_specialization_used: bool = False
    degradation_reason: str | None = None
    safer_fallback_family: SoftControlFamily | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "OpportunitySpecializationResult.selected_family must be "
                f"SoftControlFamily, got {actual_type}."
            )
        if self.preferred_opportunity is not None and not isinstance(
            self.preferred_opportunity,
            HostNativeOpportunity,
        ):
            actual_type = type(self.preferred_opportunity).__name__
            raise TypeError(
                "OpportunitySpecializationResult.preferred_opportunity must be "
                f"HostNativeOpportunity | None, got {actual_type}."
            )
        if self.safer_fallback_family not in _SAFE_FALLBACK_FAMILIES | {None}:
            raise ValueError(
                "OpportunitySpecializationResult.safer_fallback_family must be "
                "neutral, escalate, or None."
            )
        if self.direct_opportunity_specialization_used and self.preferred_opportunity is None:
            raise ValueError(
                "OpportunitySpecializationResult requires a preferred_opportunity "
                "when direct specialization is used."
            )
        if self.direct_opportunity_specialization_used and self.degradation_reason is not None:
            raise ValueError(
                "OpportunitySpecializationResult cannot degrade while using a direct "
                "opportunity specialization."
            )
        if self.degradation_reason is not None and not self.degradation_reason.strip():
            raise ValueError(
                "OpportunitySpecializationResult.degradation_reason must be non-empty after trimming when provided."
            )
        if self.degradation_reason is None and self.safer_fallback_family is not None:
            raise ValueError(
                "OpportunitySpecializationResult.safer_fallback_family requires a "
                "degradation_reason."
            )
        if self.degradation_reason is not None and self.safer_fallback_family is None:
            raise ValueError(
                "OpportunitySpecializationResult must surface a safer fallback when "
                "specialization degrades."
            )


def specialize_host_native_opportunity(
    selected_family: SoftControlFamily,
    opportunities: Sequence[HostNativeOpportunity],
) -> OpportunitySpecializationResult:
    if selected_family is SoftControlFamily.NEUTRAL:
        return OpportunitySpecializationResult(selected_family=selected_family)

    opportunity = _first_clearly_superior_match(selected_family, opportunities)
    if opportunity is None:
        return OpportunitySpecializationResult(selected_family=selected_family)

    if opportunity.realizable:
        return OpportunitySpecializationResult(
            selected_family=selected_family,
            preferred_opportunity=opportunity,
            direct_opportunity_specialization_used=True,
        )

    return OpportunitySpecializationResult(
        selected_family=selected_family,
        preferred_opportunity=opportunity,
        direct_opportunity_specialization_used=False,
        degradation_reason=opportunity.degradation_reason,
        safer_fallback_family=(
            opportunity.safer_fallback_family
            or _default_safer_fallback(selected_family)
        ),
    )


def _first_clearly_superior_match(
    selected_family: SoftControlFamily,
    opportunities: Sequence[HostNativeOpportunity],
) -> HostNativeOpportunity | None:
    for opportunity in opportunities:
        if (
            opportunity.clearly_superior
            and selected_family in opportunity.supported_families
        ):
            return opportunity
    return None


def _default_safer_fallback(
    selected_family: SoftControlFamily,
) -> SoftControlFamily:
    if selected_family is SoftControlFamily.ESCALATE:
        return SoftControlFamily.ESCALATE
    return SoftControlFamily.NEUTRAL


__all__ = [
    "HostNativeOpportunity",
    "OpportunitySpecializationResult",
    "specialize_host_native_opportunity",
]
