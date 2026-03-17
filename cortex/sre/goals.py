"""Bounded goal continuity carriers for the reference SRE."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GoalContinuityView:
    main_goal_ref: str | None = None
    active_track_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    resume_anchor_available: bool = False


__all__ = ["GoalContinuityView"]
