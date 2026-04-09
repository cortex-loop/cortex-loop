"""Raw transcript ingress parsing for the Claude runtime shell."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from experimental.drivers.claude_host import is_raw_claude_host_event_name


@dataclass(frozen=True, slots=True)
class ClaudeHostEventEnvelope:
    event_type: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError(
                "ClaudeHostEventEnvelope.event_type must be a non-empty raw Claude host event name."
            )
        if not is_raw_claude_host_event_name(self.event_type):
            raise ValueError(
                "ClaudeHostEventEnvelope.event_type must be a raw Claude host event name, "
                "not a canonical Cortex event name."
            )
        if not isinstance(self.payload, dict):
            actual_type = type(self.payload).__name__
            raise TypeError(
                "ClaudeHostEventEnvelope.payload must be dict[str, Any], "
                f"got {actual_type}."
            )


def parse_claude_host_event_envelope(record: Mapping[str, Any]) -> ClaudeHostEventEnvelope:
    if not isinstance(record, Mapping):
        actual_type = type(record).__name__
        raise TypeError(
            "parse_claude_host_event_envelope.record must be a mapping, "
            f"got {actual_type}."
        )
    if "event_name" in record or "payload" in record:
        raise ValueError(
            "G2 expects raw host transcript records only; wrapper and mixed "
            "wrapper/transcript shapes that include `event_name` or `payload` are unlawful."
        )
    if "type" not in record:
        raise ValueError("Raw Claude host transcript record must include `type`.")

    event_type = record["type"]
    if not isinstance(event_type, str):
        actual_type = type(event_type).__name__
        raise TypeError(
            "Raw Claude host transcript record `type` must be a string, "
            f"got {actual_type}."
        )
    if not is_raw_claude_host_event_name(event_type):
        raise ValueError(
            "Raw Claude host transcript record `type` must be a raw Claude host event name, "
            "not a canonical Cortex event name."
        )

    payload = {key: value for key, value in record.items() if key != "type"}
    return ClaudeHostEventEnvelope(event_type=event_type, payload=payload)


__all__ = ["ClaudeHostEventEnvelope", "parse_claude_host_event_envelope"]
