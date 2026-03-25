"""Bounded realization-feedback carriers for the reference runtime shell."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.commitments import CommitmentStatus

from .brake import BrakeState
from .families import SoftControlFamily

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)
_MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES = 3


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


@dataclass(frozen=True, slots=True)
class ReferenceRealizationFeedbackWindow:
    entries: tuple[ReferenceRealizationFeedback, ...] = ()

    def __post_init__(self) -> None:
        if len(self.entries) > _MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES:
            raise ValueError(
                "ReferenceRealizationFeedbackWindow.entries must contain at most three items."
            )
        if any(not isinstance(entry, ReferenceRealizationFeedback) for entry in self.entries):
            raise TypeError(
                "ReferenceRealizationFeedbackWindow.entries must contain only "
                "ReferenceRealizationFeedback instances."
            )

    def append(
        self,
        feedback: ReferenceRealizationFeedback,
    ) -> "ReferenceRealizationFeedbackWindow":
        if not isinstance(feedback, ReferenceRealizationFeedback):
            actual_type = type(feedback).__name__
            raise TypeError(
                "ReferenceRealizationFeedbackWindow.append feedback must be "
                f"ReferenceRealizationFeedback, got {actual_type}."
            )
        return ReferenceRealizationFeedbackWindow(
            entries=(self.entries + (feedback,))[-_MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES :]
        )


@dataclass(frozen=True, slots=True)
class ReferenceFeedbackWindowSummary:
    window_size: int = 0
    rejection_count: int = 0
    override_count: int = 0
    latched_count: int = 0
    clean_success_streak: int = 0
    goal_progress_floor: float = 0.0
    degradation_pressure_bonus: int = 0
    sustained_spike_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.window_size <= _MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES:
            raise ValueError(
                "ReferenceFeedbackWindowSummary.window_size must be between 0 and 3."
            )
        for field_name in (
            "rejection_count",
            "override_count",
            "latched_count",
            "clean_success_streak",
            "degradation_pressure_bonus",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise TypeError(
                    f"ReferenceFeedbackWindowSummary.{field_name} must be a non-negative integer."
                )
        if not 0.0 <= self.goal_progress_floor <= 1.0:
            raise ValueError(
                "ReferenceFeedbackWindowSummary.goal_progress_floor must be between 0.0 and 1.0."
            )
        if any(not (isinstance(flag, str) and flag.strip()) for flag in self.sustained_spike_flags):
            raise ValueError(
                "ReferenceFeedbackWindowSummary.sustained_spike_flags must contain only non-empty values after trimming."
            )

    def as_summary(self) -> dict[str, object]:
        return {
            "window_size": self.window_size,
            "rejection_count": self.rejection_count,
            "override_count": self.override_count,
            "latched_count": self.latched_count,
            "clean_success_streak": self.clean_success_streak,
            "goal_progress_floor": self.goal_progress_floor,
            "degradation_pressure_bonus": self.degradation_pressure_bonus,
            "sustained_spike_flags": list(self.sustained_spike_flags),
        }


def summarize_reference_feedback_window(
    window: ReferenceRealizationFeedbackWindow,
) -> ReferenceFeedbackWindowSummary:
    if not isinstance(window, ReferenceRealizationFeedbackWindow):
        actual_type = type(window).__name__
        raise TypeError(
            "summarize_reference_feedback_window.window must be "
            f"ReferenceRealizationFeedbackWindow, got {actual_type}."
        )

    entries = window.entries
    rejection_count = sum(1 for entry in entries if _has_rejection_warning(entry))
    override_count = sum(
        1 for entry in entries if entry.realized_family is not entry.selected_family
    )
    latched_count = sum(1 for entry in entries if entry.brake_state is BrakeState.LATCHED)

    clean_success_streak = 0
    for entry in reversed(entries):
        if (
            entry.warning_codes
            or entry.realized_family is not entry.selected_family
            or entry.brake_state is not BrakeState.QUIESCENT
        ):
            break
        clean_success_streak += 1

    rejection_floor = 0.0
    if rejection_count >= 2:
        rejection_floor = 0.70
    elif rejection_count == 1:
        rejection_floor = 0.55

    override_floor = 0.0
    if override_count >= 2:
        override_floor = 0.60
    elif override_count == 1:
        override_floor = 0.45

    degradation_pressure_bonus = 0
    if (
        rejection_count >= 2
        or latched_count >= 2
        or (rejection_count >= 1 and override_count >= 1)
    ):
        degradation_pressure_bonus = 2
    elif rejection_count == 1 or override_count >= 1 or latched_count == 1:
        degradation_pressure_bonus = 1

    sustained_spike_flags: list[str] = []
    if any(
        code.startswith("continuity-rejected:")
        for entry in entries
        for code in entry.warning_codes
    ):
        sustained_spike_flags.append("prior-continuity-rejection")
    if any(
        code.startswith("session-rejected:")
        for entry in entries
        for code in entry.warning_codes
    ):
        sustained_spike_flags.append("prior-session-mismatch")
    if override_count >= 1:
        sustained_spike_flags.append("prior-enforcement-override")
    if rejection_count >= 2 or (rejection_count >= 1 and override_count >= 1):
        sustained_spike_flags.append("sustained-feedback-disruption")
    if latched_count >= 2:
        sustained_spike_flags.append("sustained-latched-brake")

    return ReferenceFeedbackWindowSummary(
        window_size=len(entries),
        rejection_count=rejection_count,
        override_count=override_count,
        latched_count=latched_count,
        clean_success_streak=clean_success_streak,
        goal_progress_floor=max(rejection_floor, override_floor),
        degradation_pressure_bonus=degradation_pressure_bonus,
        sustained_spike_flags=tuple(sustained_spike_flags),
    )


def _has_rejection_warning(entry: ReferenceRealizationFeedback) -> bool:
    return any(
        code.startswith(("continuity-rejected:", "session-rejected:"))
        for code in entry.warning_codes
    )


__all__ = [
    "ReferenceFeedbackWindowSummary",
    "ReferenceRealizationFeedback",
    "ReferenceRealizationFeedbackWindow",
    "summarize_reference_feedback_window",
]
