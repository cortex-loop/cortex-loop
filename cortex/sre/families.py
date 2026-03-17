"""Reference soft-control family set for the first active SRE hinge."""

from __future__ import annotations

from enum import Enum


class SoftControlFamily(str, Enum):
    NEUTRAL = "neutral"
    SEEK_CONTEXT = "seek-context"
    REDIRECT = "redirect"
    CHECK = "check"
    BRANCH = "branch"
    ESCALATE = "escalate"
    BRAKE = "brake"


REFERENCE_SOFT_CONTROL_FAMILIES = frozenset(SoftControlFamily)


__all__ = ["REFERENCE_SOFT_CONTROL_FAMILIES", "SoftControlFamily"]
