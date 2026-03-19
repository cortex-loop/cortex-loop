"""Narrow commitment carrier resolution and field reconciliation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .commitment_payload import (
    DEFAULT_MESSAGE_FIELD_NAMES,
    CommitmentPayloadExtraction,
    extract_commitment_payload,
)

NATIVE_COMMITMENT_SOURCE = "native"
PAYLOAD_COMMITMENT_SOURCE = "payload.stop_fields"
FALLBACK_COMMITMENT_SOURCE = "fallback"
NO_COMMITMENT_SOURCE = "none"


@dataclass(frozen=True, slots=True)
class CommitmentFieldResolution:
    value: Any
    source: str
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CommitmentExtractionResult:
    commitment_fields: dict[str, Any] | None
    carrier_source: str
    fallback_used: bool
    normalization_count: int
    warnings: tuple[str, ...]
    structured_payload_violation: bool

    def __post_init__(self) -> None:
        if self.commitment_fields is not None and not isinstance(self.commitment_fields, dict):
            actual_type = type(self.commitment_fields).__name__
            raise TypeError(
                "CommitmentExtractionResult.commitment_fields must be dict[str, Any] | None, "
                f"got {actual_type}.",
            )
        if not isinstance(self.fallback_used, bool):
            actual_type = type(self.fallback_used).__name__
            raise TypeError(
                "CommitmentExtractionResult.fallback_used must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.normalization_count, int):
            actual_type = type(self.normalization_count).__name__
            raise TypeError(
                "CommitmentExtractionResult.normalization_count must be int, "
                f"got {actual_type}.",
            )
        if self.normalization_count < 0:
            raise ValueError(
                "CommitmentExtractionResult.normalization_count must be non-negative.",
            )
        if any(not isinstance(warning, str) for warning in self.warnings):
            raise TypeError(
                "CommitmentExtractionResult.warnings must contain only string entries.",
            )
        if any(not warning.strip() for warning in self.warnings):
            raise ValueError(
                "CommitmentExtractionResult.warnings must contain only non-empty strings after trimming.",
            )
        if not isinstance(self.structured_payload_violation, bool):
            actual_type = type(self.structured_payload_violation).__name__
            raise TypeError(
                "CommitmentExtractionResult.structured_payload_violation must be bool, "
                f"got {actual_type}.",
            )
        if self.carrier_source not in {
            NATIVE_COMMITMENT_SOURCE,
            PAYLOAD_COMMITMENT_SOURCE,
            FALLBACK_COMMITMENT_SOURCE,
            NO_COMMITMENT_SOURCE,
        }:
            raise ValueError(
                "CommitmentExtractionResult.carrier_source must be one of the canonical source labels: "
                "native, payload.stop_fields, fallback, none.",
            )


def resolve_commitment_extract(
    payload: Mapping[str, Any],
    *,
    native_commitment_fields: Mapping[str, Any] | None = None,
    allow_message_fallback: bool = True,
    require_structured_commitment_payload: bool = False,
    message_field_names: tuple[str, ...] = DEFAULT_MESSAGE_FIELD_NAMES,
) -> CommitmentExtractionResult:
    extraction = extract_commitment_payload(
        payload,
        native_commitment_fields=native_commitment_fields,
        allow_message_fallback=allow_message_fallback,
        message_field_names=message_field_names,
    )
    carrier_source = _carrier_source_label(extraction.source)
    fallback_used = bool(
        carrier_source == FALLBACK_COMMITMENT_SOURCE and extraction.commitment_fields is not None
    )
    warnings = list(extraction.warnings)

    if fallback_used:
        warnings.append(
            "Recovered commitment fields from weaker fallback carrier; emit native structured fields or payload.stop_fields."
        )
    if extraction.normalization_count > 0:
        warnings.append(
            f"Canonicalized {extraction.normalization_count} commitment payload key(s) with surrounding whitespace."
        )

    structured_payload_violation = bool(
        require_structured_commitment_payload
        and not _has_structured_commitment_source(payload, native_commitment_fields)
    )
    if structured_payload_violation:
        if fallback_used:
            warnings.append(
                "Structured commitment payload is required; fallback-only commitment fields are rejected."
            )
        else:
            warnings.append(
                "Structured commitment payload is required; include native structured fields or payload.stop_fields."
            )

    return CommitmentExtractionResult(
        commitment_fields=extraction.commitment_fields,
        carrier_source=carrier_source,
        fallback_used=fallback_used,
        normalization_count=extraction.normalization_count,
        warnings=tuple(warnings),
        structured_payload_violation=structured_payload_violation,
    )


def reconcile_commitment_field(
    *,
    key: str,
    payload: Mapping[str, Any],
    commitment_fields: Mapping[str, Any] | None,
    carrier_source: str,
    value_label: str | None = None,
) -> CommitmentFieldResolution:
    value = payload.get(key)
    if value is not None:
        return CommitmentFieldResolution(value=value, source="payload", warnings=())
    if not (commitment_fields and key in commitment_fields):
        return CommitmentFieldResolution(value=None, source=NO_COMMITMENT_SOURCE, warnings=())

    resolved_value = commitment_fields[key]
    label = value_label or key
    if carrier_source == FALLBACK_COMMITMENT_SOURCE:
        warnings = (f"Using {label} from extracted fallback commitment fields.",)
    elif carrier_source == PAYLOAD_COMMITMENT_SOURCE:
        warnings = (f"Using {label} from payload.stop_fields.",)
    else:
        warnings = ()
    return CommitmentFieldResolution(
        value=resolved_value,
        source=carrier_source,
        warnings=warnings,
    )


def _carrier_source_label(source: str | None) -> str:
    if source == NATIVE_COMMITMENT_SOURCE:
        return NATIVE_COMMITMENT_SOURCE
    if source == PAYLOAD_COMMITMENT_SOURCE:
        return PAYLOAD_COMMITMENT_SOURCE
    if source is None:
        return NO_COMMITMENT_SOURCE
    return FALLBACK_COMMITMENT_SOURCE


def _has_structured_commitment_source(
    payload: Mapping[str, Any],
    native_commitment_fields: Mapping[str, Any] | None,
) -> bool:
    return isinstance(native_commitment_fields, Mapping) or isinstance(
        payload.get("stop_fields"),
        Mapping,
    )


__all__ = [
    "CommitmentExtractionResult",
    "CommitmentFieldResolution",
    "FALLBACK_COMMITMENT_SOURCE",
    "NATIVE_COMMITMENT_SOURCE",
    "NO_COMMITMENT_SOURCE",
    "PAYLOAD_COMMITMENT_SOURCE",
    "reconcile_commitment_field",
    "resolve_commitment_extract",
]
