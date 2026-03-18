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

    def __post_init__(self) -> None:
        _validate_query_kind(self.kind)


@dataclass(frozen=True, slots=True)
class ExecutiveEnvironmentView:
    available_query_kinds: frozenset[str] = field(default_factory=frozenset)
    host_capability_tags: frozenset[str] = field(default_factory=frozenset)
    bounded_requests: tuple[EnvironmentQuery, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _validate_query_kind_set(self.available_query_kinds)


@dataclass(frozen=True, slots=True)
class CommitmentEnvironmentHandle:
    available_query_kinds: frozenset[str] = field(default_factory=frozenset)
    evidence_requests: tuple[EnvironmentQuery, ...] = field(default_factory=tuple)
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    boundary_scope_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        _validate_query_kind_set(self.available_query_kinds)


def _validate_query_kind(kind: str) -> None:
    if kind not in CANONICAL_QUERY_KINDS:
        raise ValueError(
            f"Invalid environment query kind {kind!r}; kind must use the canonical core query vocabulary.",
        )


def _validate_query_kind_set(kinds: frozenset[str]) -> None:
    for kind in kinds:
        _validate_query_kind(kind)


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
