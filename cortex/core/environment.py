"""Read-only environment surfaces for soft control and commitment-time checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from .envelopes import MetadataField

STATE_SNAPSHOT: Final[str] = "STATE_SNAPSHOT"
STATE_DIFF: Final[str] = "STATE_DIFF"
EXECUTION_TRACE: Final[str] = "EXECUTION_TRACE"
RESULT_ARTIFACT: Final[str] = "RESULT_ARTIFACT"
CAPABILITY_VIEW: Final[str] = "CAPABILITY_VIEW"
EXTERNAL_RECORD: Final[str] = "EXTERNAL_RECORD"

CANONICAL_QUERY_KINDS: Final[frozenset[str]] = frozenset(
    {
        STATE_SNAPSHOT,
        STATE_DIFF,
        EXECUTION_TRACE,
        RESULT_ARTIFACT,
        CAPABILITY_VIEW,
        EXTERNAL_RECORD,
    }
)


@dataclass(frozen=True, slots=True)
class EnvironmentQuery:
    kind: str
    target: str | None = None
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ExecutiveEnvironmentView:
    available_query_kinds: frozenset[str] = field(default_factory=frozenset)
    host_capability_tags: frozenset[str] = field(default_factory=frozenset)
    bounded_requests: tuple[EnvironmentQuery, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CommitmentEnvironmentHandle:
    available_query_kinds: frozenset[str] = field(default_factory=frozenset)
    evidence_requests: tuple[EnvironmentQuery, ...] = field(default_factory=tuple)
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    boundary_scope_tags: frozenset[str] = field(default_factory=frozenset)


__all__ = [
    "CANONICAL_QUERY_KINDS",
    "CAPABILITY_VIEW",
    "CommitmentEnvironmentHandle",
    "EXECUTION_TRACE",
    "EXTERNAL_RECORD",
    "EnvironmentQuery",
    "ExecutiveEnvironmentView",
    "RESULT_ARTIFACT",
    "STATE_DIFF",
    "STATE_SNAPSHOT",
]
