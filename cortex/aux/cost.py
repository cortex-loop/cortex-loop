"""Cost-visible AUX burden carriers."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real

from cortex.core.envelopes import MetadataField


@dataclass(frozen=True, slots=True)
class AuxBurdenReport:
    compute_overhead: float = 0.0
    memory_overhead: float = 0.0
    latency_overhead: float = 0.0
    environment_query_cost: float = 0.0
    retrieval_cost: float = 0.0
    intervention_burden: float = 0.0
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in (
            "compute_overhead",
            "memory_overhead",
            "latency_overhead",
            "environment_query_cost",
            "retrieval_cost",
            "intervention_burden",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool):
                raise TypeError(
                    f"AuxBurdenReport.{field_name} must be numeric, got bool.",
                )
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"AuxBurdenReport.{field_name} must be numeric, got {actual_type}.",
                )
            if value < 0:
                raise ValueError(f"AuxBurdenReport.{field_name} must be non-negative.")
        for metadata_field in self.metadata:
            if not isinstance(metadata_field, MetadataField):
                raise TypeError(
                    "AuxBurdenReport.metadata must contain only MetadataField instances.",
                )


__all__ = ["AuxBurdenReport"]
