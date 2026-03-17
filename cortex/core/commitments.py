"""Minimal commitment-side carriers for the core substrate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .environment import CommitmentEnvironmentHandle
from .envelopes import EventPayloadHandle, MetadataField
from .observation import ObservationBundle


class CommitmentStatus(Enum):
    CERTIFIED = "certified"
    UNCERTIFIED = "uncertified"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class CommitmentCandidate:
    candidate_id: str
    surface_tags: frozenset[str] = field(default_factory=frozenset)
    payload_handle: EventPayloadHandle | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CertificationContext:
    candidate: CommitmentCandidate
    observation: ObservationBundle
    environment_handle: CommitmentEnvironmentHandle
    wake_reasons: frozenset[str] = field(default_factory=frozenset)
    boundary_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.environment_handle, CommitmentEnvironmentHandle):
            actual_type = type(self.environment_handle).__name__
            raise TypeError(
                "CertificationContext requires CommitmentEnvironmentHandle, "
                f"got {actual_type}."
            )


@dataclass(frozen=True, slots=True)
class CommitmentVerdict:
    status: CommitmentStatus
    candidate: CommitmentCandidate


__all__ = [
    "CertificationContext",
    "CommitmentCandidate",
    "CommitmentStatus",
    "CommitmentVerdict",
]
