"""Typed lifecycle-surface carriers for the core substrate."""

from __future__ import annotations

from dataclasses import dataclass, field

from .envelopes import MetadataField


@dataclass(frozen=True, slots=True)
class LifecycleEffectBinding:
    """One host-native action tag and its observable consequence tags."""

    action_tag: str
    consequence_tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class LifecycleSurface:
    """Python-facing carrier for the core lifecycle surface law."""

    runtime_name: str
    event_substrate: frozenset[str] = field(default_factory=frozenset)
    context_affordances: frozenset[str] = field(default_factory=frozenset)
    tool_affordances: frozenset[str] = field(default_factory=frozenset)
    turn_affordances: frozenset[str] = field(default_factory=frozenset)
    orchestration_affordances: frozenset[str] = field(default_factory=frozenset)
    mcp_affordances: frozenset[str] = field(default_factory=frozenset)
    effect_map: tuple[LifecycleEffectBinding, ...] = field(default_factory=tuple)


__all__ = ["LifecycleEffectBinding", "LifecycleSurface"]
