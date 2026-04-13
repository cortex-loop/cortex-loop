"""Bounded goal continuity carriers for the reference SRE."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real

_ANCHOR_SOURCES = frozenset(
    {
        "none",
        "pending_goal",
        "continuity_reminder",
        "trace_wake",
        "branch_registry_only",
    }
)
_ANCHOR_FRESHNESS = frozenset({"absent", "fresh", "stale"})


def make_resume_reminder(track_ref: str) -> str:
    if not (isinstance(track_ref, str) and track_ref.strip()):
        raise ValueError("make_resume_reminder.track_ref must be non-empty after trimming.")
    return f"resume {track_ref} after review"


def parse_resume_reminder_track(reminder: str) -> str | None:
    if not (isinstance(reminder, str) and reminder.strip()):
        raise ValueError(
            "parse_resume_reminder_track.reminder must be non-empty after trimming."
        )
    normalized = reminder.strip()
    if not normalized.startswith("resume "):
        return None
    body = normalized.removeprefix("resume ")
    for delimiter in (" after ", " before "):
        if delimiter in body:
            track_ref = body.split(delimiter, 1)[0].strip()
            return track_ref or None
    return None


@dataclass(frozen=True, slots=True)
class GoalContinuityView:
    main_goal_ref: str | None = None
    active_track_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    resume_anchor_available: bool = False
    anchor_source: str = "none"
    anchor_freshness: str = "absent"
    branch_intent_present: bool = False
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
        if self.anchor_source not in _ANCHOR_SOURCES:
            raise ValueError(
                "GoalContinuityView.anchor_source must be one of "
                f"{sorted(_ANCHOR_SOURCES)!r}."
            )
        if self.anchor_freshness not in _ANCHOR_FRESHNESS:
            raise ValueError(
                "GoalContinuityView.anchor_freshness must be one of "
                f"{sorted(_ANCHOR_FRESHNESS)!r}."
            )
        if not isinstance(self.branch_intent_present, bool):
            actual_type = type(self.branch_intent_present).__name__
            raise TypeError(
                "GoalContinuityView.branch_intent_present must be bool, "
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


__all__ = ["GoalContinuityView", "make_resume_reminder", "parse_resume_reminder_track"]
