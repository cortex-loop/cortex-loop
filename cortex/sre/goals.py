"""Bounded goal continuity carriers for the reference SRE."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GoalContinuityView:
    main_goal_ref: str | None = None
    active_track_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    resume_anchor_available: bool = False

    def __post_init__(self) -> None:
        if self.main_goal_ref is not None and not self.main_goal_ref.strip():
            raise ValueError(
                "GoalContinuityView.main_goal_ref must be non-empty after trimming when provided."
            )
        if self.active_track_ref is not None and not self.active_track_ref.strip():
            raise ValueError(
                "GoalContinuityView.active_track_ref must be non-empty after trimming when provided."
            )


__all__ = ["GoalContinuityView"]
