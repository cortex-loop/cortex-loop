"""Bounded experimental mediation finalization for the reference SRE."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .families import SoftControlFamily
from .opportunities import (
    HostNativeOpportunity,
    OpportunitySpecializationResult,
    specialize_host_native_opportunity,
)


class ReferenceMediationMode(str, Enum):
    """Explicit runtime mode for the bounded reference mediation train."""

    IDENTITY = "identity"
    HOST_REALIZATION_EXPERIMENTAL = "host-realization-experimental"


@dataclass(frozen=True, slots=True)
class ReferenceMediationFinalization:
    mode: ReferenceMediationMode
    selected_family_before_finalization: SoftControlFamily
    selected_family_after_finalization: SoftControlFamily
    opportunity_specialization: OpportunitySpecializationResult
    mediation_reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.mode, ReferenceMediationMode):
            actual_type = type(self.mode).__name__
            raise TypeError(
                "ReferenceMediationFinalization.mode must be ReferenceMediationMode, "
                f"got {actual_type}."
            )
        if not isinstance(
            self.selected_family_before_finalization,
            SoftControlFamily,
        ):
            actual_type = type(self.selected_family_before_finalization).__name__
            raise TypeError(
                "ReferenceMediationFinalization.selected_family_before_finalization "
                f"must be SoftControlFamily, got {actual_type}."
            )
        if not isinstance(
            self.selected_family_after_finalization,
            SoftControlFamily,
        ):
            actual_type = type(self.selected_family_after_finalization).__name__
            raise TypeError(
                "ReferenceMediationFinalization.selected_family_after_finalization "
                f"must be SoftControlFamily, got {actual_type}."
            )
        if not isinstance(
            self.opportunity_specialization,
            OpportunitySpecializationResult,
        ):
            actual_type = type(self.opportunity_specialization).__name__
            raise TypeError(
                "ReferenceMediationFinalization.opportunity_specialization must be "
                f"OpportunitySpecializationResult, got {actual_type}."
            )
        if (
            self.selected_family_after_finalization
            is not self.opportunity_specialization.selected_family
        ):
            raise ValueError(
                "ReferenceMediationFinalization.selected_family_after_finalization "
                "must match the opportunity specialization family."
            )
        if any(not tag.strip() for tag in self.mediation_reason_tags):
            raise ValueError(
                "ReferenceMediationFinalization.mediation_reason_tags must contain "
                "only non-empty values after trimming."
            )

    def as_payload(self) -> dict[str, Any]:
        preferred_opportunity_ref = None
        preferred_opportunity = self.opportunity_specialization.preferred_opportunity
        if preferred_opportunity is not None:
            preferred_opportunity_ref = preferred_opportunity.opportunity_ref

        mediation_active = (
            self.mode is ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL
            and self.selected_family_before_finalization is SoftControlFamily.SEEK_CONTEXT
        )
        mediation_identity = (
            not mediation_active
            or not self.opportunity_specialization.direct_opportunity_specialization_used
        )
        return {
            "mediation_active": mediation_active,
            "mediation_identity": mediation_identity,
            "selected_family_before_finalization": (
                self.selected_family_before_finalization.value
            ),
            "selected_family_after_finalization": (
                self.selected_family_after_finalization.value
            ),
            "preferred_opportunity_ref": preferred_opportunity_ref,
            "direct_opportunity_specialization_used": (
                self.opportunity_specialization.direct_opportunity_specialization_used
            ),
            "mediation_reason_tags": sorted(self.mediation_reason_tags),
        }


def finalize_reference_soft_control(
    selected_family: SoftControlFamily,
    *,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
    opportunities: Sequence[HostNativeOpportunity] = (),
) -> ReferenceMediationFinalization:
    if not isinstance(selected_family, SoftControlFamily):
        actual_type = type(selected_family).__name__
        raise TypeError(
            "finalize_reference_soft_control.selected_family must be SoftControlFamily, "
            f"got {actual_type}."
        )
    if not isinstance(mediation_mode, ReferenceMediationMode):
        actual_type = type(mediation_mode).__name__
        raise TypeError(
            "finalize_reference_soft_control.mediation_mode must be "
            f"ReferenceMediationMode, got {actual_type}."
        )
    if mediation_mode is not ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL:
        return ReferenceMediationFinalization(
            mode=mediation_mode,
            selected_family_before_finalization=selected_family,
            selected_family_after_finalization=selected_family,
            opportunity_specialization=OpportunitySpecializationResult(
                selected_family=selected_family
            ),
            mediation_reason_tags=frozenset({"mode:identity"}),
        )
    if selected_family is not SoftControlFamily.SEEK_CONTEXT:
        return ReferenceMediationFinalization(
            mode=mediation_mode,
            selected_family_before_finalization=selected_family,
            selected_family_after_finalization=selected_family,
            opportunity_specialization=OpportunitySpecializationResult(
                selected_family=selected_family
            ),
            mediation_reason_tags=frozenset(
                {
                    "mode:host-realization-experimental",
                    "identity:selected-family-not-seek-context",
                }
            ),
        )

    opportunity_specialization = specialize_host_native_opportunity(
        selected_family,
        opportunities,
    )
    reason_tags = {
        "mode:host-realization-experimental",
        "family:seek-context",
        "opportunity-source:runtime-visible",
    }
    if opportunity_specialization.direct_opportunity_specialization_used:
        reason_tags.add("host-realization-specialized")
    else:
        reason_tags.add("identity:no-clearly-superior-opportunity")

    return ReferenceMediationFinalization(
        mode=mediation_mode,
        selected_family_before_finalization=selected_family,
        selected_family_after_finalization=opportunity_specialization.selected_family,
        opportunity_specialization=opportunity_specialization,
        mediation_reason_tags=frozenset(reason_tags),
    )


__all__ = [
    "ReferenceMediationFinalization",
    "ReferenceMediationMode",
    "finalize_reference_soft_control",
]
