"""Private helpers shared by commitment-path driver slices."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any

from cortex.core.commitment_extract import CommitmentExtractionResult, resolve_commitment_extract
from cortex.core.dispatch import DispatchDecision, DispatchLane

CANDIDATE_ID_KEYS = ("candidate_id", "commitment_id", "claim_id")


def extract_native_commitment_fields(payload: Mapping[str, Any]) -> Any | None:
    if payload.get("commitment_fields_source") != "native":
        return None
    if "commitment_fields" not in payload:
        return None
    return payload.get("commitment_fields")


def resolve_commitment_extract_for_dispatch(
    *,
    payload: Mapping[str, Any],
    dispatch_decision: DispatchDecision,
    native_commitment_fields: Any | None,
    allow_message_commitment_fallback: bool,
) -> CommitmentExtractionResult | None:
    has_structured_carrier = (
        native_commitment_fields is not None
        or isinstance(payload.get("stop_fields"), Mapping)
        or "commitment_fields_source" in payload
    )
    if dispatch_decision.lane is DispatchLane.CHEAP and not has_structured_carrier:
        return None
    return resolve_commitment_extract(
        payload,
        native_commitment_fields=native_commitment_fields,
        allow_message_fallback=allow_message_commitment_fallback,
    )


def candidate_surface_tags(
    *,
    facet_tags: Iterable[str],
    wake_reason_tags: Iterable[str],
) -> frozenset[str]:
    return frozenset(set(facet_tags) | set(wake_reason_tags))


def candidate_id_from_value(value: Any) -> str | None:
    if value is None:
        return None
    candidate_id = str(value).strip()
    return candidate_id or None


def candidate_id_source_label(key: str, source: str) -> str:
    return f"{source}:{key}"


def synthesized_candidate_id(
    *,
    native_event_name: str,
    normalized_payload: Mapping[str, Any],
    payload_handle: Any | None,
) -> str:
    payload_blob = json.dumps(
        normalized_payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    digest_input = (
        f"{native_event_name}|"
        f"{getattr(payload_handle, 'payload_ref', '') if payload_handle is not None else ''}|"
        f"{payload_blob}"
    )
    digest = hashlib.sha1(digest_input.encode("utf-8")).hexdigest()[:12]
    return f"local-candidate-{digest}"


def merge_warnings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    warnings: list[str] = []
    for group in groups:
        for warning in group:
            if warning not in warnings:
                warnings.append(warning)
    return tuple(warnings)
