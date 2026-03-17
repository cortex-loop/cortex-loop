"""Bounded branch operation carriers for the reference SRE."""

from __future__ import annotations

from enum import Enum


class BranchOperation(str, Enum):
    OPEN = "open"
    SUSPEND = "suspend"
    RESUME = "resume"
    MERGE = "merge"
    ABANDON = "abandon"


__all__ = ["BranchOperation"]
