"""Structured commitment payload extraction for later commitment handling."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

COMMITMENT_FIELDS_JSON_MARKER = "COMMITMENT_FIELDS_JSON:"
DEFAULT_MESSAGE_FIELD_NAMES = ("last_assistant_message", "message", "text")


@dataclass(frozen=True, slots=True)
class CommitmentPayloadExtraction:
    commitment_fields: dict[str, Any] | None
    source: str | None
    warnings: tuple[str, ...]
    normalization_count: int


def extract_commitment_payload(
    payload: Mapping[str, Any],
    *,
    native_commitment_fields: Mapping[str, Any] | None = None,
    allow_message_fallback: bool = True,
    message_field_names: tuple[str, ...] = DEFAULT_MESSAGE_FIELD_NAMES,
) -> CommitmentPayloadExtraction:
    warnings: list[str] = []

    if native_commitment_fields is not None:
        if isinstance(native_commitment_fields, Mapping):
            normalized, normalization_count = normalize_commitment_mapping_keys(
                native_commitment_fields
            )
            return CommitmentPayloadExtraction(
                commitment_fields=normalized,
                source="native",
                warnings=tuple(warnings),
                normalization_count=normalization_count,
            )
        warnings.append("Ignoring invalid native commitment carrier; expected an object.")

    raw = payload.get("stop_fields")
    if isinstance(raw, Mapping):
        normalized, normalization_count = normalize_commitment_mapping_keys(raw)
        return CommitmentPayloadExtraction(
            commitment_fields=normalized,
            source="payload.stop_fields",
            warnings=tuple(warnings),
            normalization_count=normalization_count,
        )
    if raw is not None:
        warnings.append("Ignoring invalid payload.stop_fields field; expected an object.")

    if not allow_message_fallback:
        return CommitmentPayloadExtraction(None, None, tuple(warnings), 0)

    for field_name in message_field_names:
        value = payload.get(field_name)
        if not isinstance(value, str):
            continue
        parsed, marker_found, error = parse_commitment_fields_json(value)
        if parsed is not None:
            normalized, normalization_count = normalize_commitment_mapping_keys(parsed)
            return CommitmentPayloadExtraction(
                commitment_fields=normalized,
                source=f"{field_name}.commitment_fields_json",
                warnings=tuple(warnings),
                normalization_count=normalization_count,
            )
        if marker_found and error:
            warnings.append(f"Ignoring invalid COMMITMENT_FIELDS_JSON fallback in {field_name}: {error}")

    return CommitmentPayloadExtraction(None, None, tuple(warnings), 0)


def parse_commitment_fields_json(text: str) -> tuple[dict[str, Any] | None, bool, str | None]:
    for pattern in (r"```(?:commitment-fields|commitment_fields)\s*(\{.*?\})\s*```",):
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            continue
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            return None, True, str(exc)
        if not isinstance(parsed, dict):
            return None, True, "expected a JSON object"
        return parsed, True, None

    marker_index = text.rfind(COMMITMENT_FIELDS_JSON_MARKER)
    if marker_index == -1:
        return None, False, None

    decoder = json.JSONDecoder()
    try:
        parsed, _ = decoder.raw_decode(
            text[marker_index + len(COMMITMENT_FIELDS_JSON_MARKER) :].lstrip()
        )
    except json.JSONDecodeError as exc:
        return None, True, str(exc)
    if not isinstance(parsed, dict):
        return None, True, "expected a JSON object"
    return parsed, True, None


def normalize_commitment_mapping_keys(value: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    normalized: dict[str, Any] = {}
    normalization_count = 0
    for raw_key, raw_value in value.items():
        key = str(raw_key)
        canonical_key = key.strip()
        if canonical_key != key:
            normalization_count += 1
        canonical_value, nested_count = _normalize_commitment_value(raw_value)
        normalization_count += nested_count
        normalized[canonical_key] = canonical_value
    return normalized, normalization_count


def _normalize_commitment_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, Mapping):
        return normalize_commitment_mapping_keys(value)
    if isinstance(value, list):
        items: list[Any] = []
        normalization_count = 0
        for item in value:
            canonical_item, nested_count = _normalize_commitment_value(item)
            items.append(canonical_item)
            normalization_count += nested_count
        return items, normalization_count
    return value, 0


__all__ = [
    "COMMITMENT_FIELDS_JSON_MARKER",
    "CommitmentPayloadExtraction",
    "DEFAULT_MESSAGE_FIELD_NAMES",
    "extract_commitment_payload",
    "normalize_commitment_mapping_keys",
    "parse_commitment_fields_json",
]
