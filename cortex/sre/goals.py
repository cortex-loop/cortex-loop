"""Bounded goal continuity carriers for the reference SRE."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real


@dataclass(frozen=True, slots=True)
class GoalContinuityView:
    main_goal_ref: str | None = None
    active_track_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    resume_anchor_available: bool = False
    open_branch_count: int = 0
    resume_anchor_quality: float = 0.0
    merge_confidence: float = 0.0

    def __post_init__(self) -> None:
        if self.main_goal_ref is not None and not self.main_goal_ref.strip():
            raise ValueError(
                "GoalContinuityView.main_goal_ref must be non-empty after trimming when provided."
            )
        if self.active_track_ref is not None and not self.active_track_ref.strip():
            raise ValueError(
                "GoalContinuityView.active_track_ref must be non-empty after trimming when provided."
            )
        if any(not goal_ref.strip() for goal_ref in self.pending_goal_refs):
            raise ValueError(
                "GoalContinuityView.pending_goal_refs must contain only non-empty values after trimming."
            )
        if not isinstance(self.resume_anchor_available, bool):
            actual_type = type(self.resume_anchor_available).__name__
            raise TypeError(
                "GoalContinuityView.resume_anchor_available must be bool, "
                f"got {actual_type}."
            )
        if isinstance(self.open_branch_count, bool) or not isinstance(self.open_branch_count, int):
            actual_type = type(self.open_branch_count).__name__
            raise TypeError(
                "GoalContinuityView.open_branch_count must be int, "
                f"got {actual_type}."
            )
        if self.open_branch_count < 0:
            raise ValueError("GoalContinuityView.open_branch_count must be non-negative.")
        for field_name in ("resume_anchor_quality", "merge_confidence"):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"GoalContinuityView.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"GoalContinuityView.{field_name} must be between 0.0 and 1.0."
                )


__all__ = ["GoalContinuityView"]
