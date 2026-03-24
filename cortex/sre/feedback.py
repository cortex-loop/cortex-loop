"""Bounded last-step realization feedback for the reference runtime shell."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.commitments import CommitmentStatus

from .brake import BrakeState
from .families import SoftControlFamily

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)


@dataclass(frozen=True, slots=True)
class ReferenceRealizationFeedback:
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    brake_state: BrakeState
    commitment_result_kind: str | None = None
    warning_codes: tuple[str, ...] = field(default_factory=tuple)
    host_friction_tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "ReferenceRealizationFeedback.commitment_result_kind must be one of the "
                "canonical commitment status values or None."
            )
        if any(not (isinstance(code, str) and code.strip()) for code in self.warning_codes):
            raise ValueError(
                "ReferenceRealizationFeedback.warning_codes must contain only non-empty values after trimming."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.host_friction_tags):
            raise ValueError(
                "ReferenceRealizationFeedback.host_friction_tags must contain only non-empty values after trimming."
            )

    def as_summary(self) -> dict[str, object]:
        return {
            "selected_family": self.selected_family.value,
            "realized_family": self.realized_family.value,
            "brake_state": self.brake_state.value,
            "commitment_result_kind": self.commitment_result_kind,
            "warning_codes": list(self.warning_codes),
            "host_friction_tags": list(self.host_friction_tags),
        }


__all__ = ["ReferenceRealizationFeedback"]
