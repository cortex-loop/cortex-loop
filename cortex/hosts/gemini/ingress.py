"""Raw transcript ingress parsing for the Gemini runtime shell."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.drivers.gemini_host import is_raw_gemini_host_event_name


@dataclass(frozen=True, slots=True)
class GeminiHostEventEnvelope:
    event_type: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError(
                "GeminiHostEventEnvelope.event_type must be a non-empty raw Gemini host event name."
            )
        if not is_raw_gemini_host_event_name(self.event_type):
            raise ValueError(
                "GeminiHostEventEnvelope.event_type must be a raw Gemini host event name, "
                "not a canonical Cortex event name."
            )
        if not isinstance(self.payload, dict):
            actual_type = type(self.payload).__name__
            raise TypeError(
                "GeminiHostEventEnvelope.payload must be dict[str, Any], "
                f"got {actual_type}."
            )


def parse_gemini_host_event_envelope(record: Mapping[str, Any]) -> GeminiHostEventEnvelope:
    if not isinstance(record, Mapping):
        actual_type = type(record).__name__
        raise TypeError(
            "parse_gemini_host_event_envelope.record must be a mapping, "
            f"got {actual_type}."
        )
    if "event_name" in record or "payload" in record:
        raise ValueError(
            "G2 expects raw host transcript records only; wrapper and mixed "
            "wrapper/transcript shapes that include `event_name` or `payload` are unlawful."
        )
    if "type" not in record:
        raise ValueError("Raw Gemini host transcript record must include `type`.")

    event_type = record["type"]
    if not isinstance(event_type, str):
        actual_type = type(event_type).__name__
        raise TypeError(
            "Raw Gemini host transcript record `type` must be a string, "
            f"got {actual_type}."
        )
    if not is_raw_gemini_host_event_name(event_type):
        raise ValueError(
            "Raw Gemini host transcript record `type` must be a raw Gemini host event name, "
            "not a canonical Cortex event name."
        )

    payload = {key: value for key, value in record.items() if key != "type"}
    return GeminiHostEventEnvelope(event_type=event_type, payload=payload)


__all__ = ["GeminiHostEventEnvelope", "parse_gemini_host_event_envelope"]
