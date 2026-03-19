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

    def __post_init__(self) -> None:
        if not (isinstance(self.action_tag, str) and self.action_tag.strip()):
            raise ValueError(
                "LifecycleEffectBinding.action_tag must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.consequence_tags):
            raise ValueError(
                "LifecycleEffectBinding.consequence_tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "LifecycleEffectBinding.metadata must contain only MetadataField instances.",
            )


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

    def __post_init__(self) -> None:
        if not (isinstance(self.runtime_name, str) and self.runtime_name.strip()):
            raise ValueError(
                "LifecycleSurface.runtime_name must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.event_substrate):
            raise ValueError(
                "LifecycleSurface.event_substrate must contain only non-empty values after trimming.",
            )
        if any(not isinstance(binding, LifecycleEffectBinding) for binding in self.effect_map):
            raise TypeError(
                "LifecycleSurface.effect_map must contain only LifecycleEffectBinding instances.",
            )


__all__ = ["LifecycleEffectBinding", "LifecycleSurface"]
