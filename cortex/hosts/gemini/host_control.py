"""Bounded outbound Gemini host-control composition over the accepted K1 runtime shell."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .runtime import GeminiRuntimeSession, run_gemini_runtime_step
from .cli import build_gemini_cli_record
from .ingress import parse_gemini_host_event_envelope
from .host_transport import (
    GeminiInteractionStreamTransportError,
    execute_gemini_interaction_stream,
)

_ACTION_TAG = "gemini-interaction-stream"
_TOP_LEVEL_KEYS = frozenset({"action_tag", "request"})
_REQUEST_KEYS = frozenset(
    {
        "model",
        "input",
        "instructions",
        "metadata",
        "max_output_tokens",
        "stream",
        "audit_intensity",
    }
)
_AUDIT_INTENSITIES = frozenset({"minimal", "focused", "structured"})

GeminiInteractionStreamTransport = Callable[
    ["GeminiHostControlRequest"],
    list[dict[str, Any]],
]


@dataclass(frozen=True, slots=True)
class GeminiHostControlRequest:
    action_tag: str
    model: str
    input_text: str
    instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    max_output_tokens: int | None = None
    audit_intensity: str = "minimal"

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"GeminiHostControlRequest.action_tag must be `{_ACTION_TAG}`."
            )
        if not (isinstance(self.model, str) and self.model.strip()):
            raise ValueError(
                "GeminiHostControlRequest.model must be non-empty after trimming."
            )
        if not (isinstance(self.input_text, str) and self.input_text.strip()):
            raise ValueError(
                "GeminiHostControlRequest.input_text must be non-empty after trimming."
            )
        if self.instructions is not None and not (
            isinstance(self.instructions, str) and self.instructions.strip()
        ):
            raise ValueError(
                "GeminiHostControlRequest.instructions must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "GeminiHostControlRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if any(not (isinstance(key, str) and key.strip()) for key in self.metadata):
            raise ValueError(
                "GeminiHostControlRequest.metadata keys must be non-empty strings after trimming."
            )
        if self.max_output_tokens is not None:
            if isinstance(self.max_output_tokens, bool) or not isinstance(
                self.max_output_tokens,
                int,
            ):
                actual_type = type(self.max_output_tokens).__name__
                raise TypeError(
                    "GeminiHostControlRequest.max_output_tokens must be int | None, "
                    f"got {actual_type}."
                )
            if self.max_output_tokens <= 0:
                raise ValueError(
                    "GeminiHostControlRequest.max_output_tokens must be positive when provided."
                )
        if self.audit_intensity not in _AUDIT_INTENSITIES:
            raise ValueError(
                "GeminiHostControlRequest.audit_intensity must be one of "
                f"{sorted(_AUDIT_INTENSITIES)!r}."
            )

    def as_payload(self) -> dict[str, Any]:
        request_payload: dict[str, Any] = {
            "model": self.model,
            "input": self.input_text,
        }
        if self.instructions is not None:
            request_payload["instructions"] = self.instructions
        if self.metadata:
            request_payload["metadata"] = dict(self.metadata)
        if self.max_output_tokens is not None:
            request_payload["max_output_tokens"] = self.max_output_tokens
        if self.audit_intensity != "minimal":
            request_payload["audit_intensity"] = self.audit_intensity
        return {
            "action_tag": self.action_tag,
            "request": request_payload,
        }


@dataclass(frozen=True, slots=True)
class GeminiHostControlResult:
    action_tag: str
    records: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"GeminiHostControlResult.action_tag must be `{_ACTION_TAG}`."
            )
        if any(not isinstance(record, dict) for record in self.records):
            raise TypeError(
                "GeminiHostControlResult.records must contain only dict[str, Any] records."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "action_tag": self.action_tag,
            "records": [dict(record) for record in self.records],
        }


def run_gemini_host_control(
    request: GeminiHostControlRequest,
    session: GeminiRuntimeSession | None = None,
    *,
    transport: GeminiInteractionStreamTransport | None = None,
) -> tuple[GeminiHostControlResult, GeminiRuntimeSession]:
    if not isinstance(request, GeminiHostControlRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_gemini_host_control.request must be GeminiHostControlRequest, "
            f"got {actual_type}."
        )
    current_session = _coerce_session(session)
    transport_callable = transport if transport is not None else execute_gemini_interaction_stream
    if not callable(transport_callable):
        actual_type = type(transport_callable).__name__
        raise TypeError(
            "run_gemini_host_control.transport must be callable when provided, "
            f"got {actual_type}."
        )

    raw_events = transport_callable(request)
    if not raw_events:
        raise GeminiInteractionStreamTransportError(
            "Gemini interaction stream returned zero host events."
        )

    records: list[dict[str, Any]] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, Mapping):
            actual_type = type(raw_event).__name__
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream must yield JSON-object events, "
                f"got {actual_type}."
            )
        try:
            envelope = parse_gemini_host_event_envelope(raw_event)
            step_result = run_gemini_runtime_step(
                envelope.event_type,
                envelope.payload,
                current_session,
                audit_intensity=request.audit_intensity,
            )
        except (TypeError, ValueError) as exc:
            raise GeminiInteractionStreamTransportError(
                f"Gemini interaction stream yielded an unlawful host event: {exc}"
            ) from exc
        records.append(build_gemini_cli_record(step_result))
        current_session = step_result.session

    return GeminiHostControlResult(
        action_tag=request.action_tag,
        records=tuple(records),
    ), current_session


def _coerce_gemini_host_control_request(
    payload: Mapping[str, Any],
) -> GeminiHostControlRequest:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "Gemini host control request payload must be a mapping, "
            f"got {actual_type}."
        )
    unknown_top_level_keys = sorted(set(payload) - _TOP_LEVEL_KEYS)
    if unknown_top_level_keys:
        raise ValueError(
            "Gemini host control request accepts only `action_tag` and `request`; "
            f"got unsupported top-level keys: {', '.join(unknown_top_level_keys)}."
        )
    if "action_tag" not in payload:
        raise ValueError("Gemini host control request must include `action_tag`.")
    if "request" not in payload:
        raise ValueError("Gemini host control request must include `request`.")

    request_payload = payload["request"]
    if not isinstance(request_payload, Mapping):
        actual_type = type(request_payload).__name__
        raise TypeError(
            "Gemini host control request `request` must be an object, "
            f"got {actual_type}."
        )

    unknown_request_keys = sorted(set(request_payload) - _REQUEST_KEYS)
    if unknown_request_keys:
        raise ValueError(
            "Gemini host control request uses a strict text-only whitelist; "
            f"unsupported request keys: {', '.join(unknown_request_keys)}."
        )

    if "stream" in request_payload and request_payload["stream"] is not True:
        raise ValueError(
            "Gemini host control request `stream` must be `true` when provided."
        )

    model = _required_non_empty_string(
        request_payload.get("model"),
        "Gemini host control request `request.model`",
    )
    input_text = _required_non_empty_string(
        request_payload.get("input"),
        "Gemini host control request `request.input`",
    )
    instructions = _optional_non_empty_string(
        request_payload.get("instructions"),
        "Gemini host control request `request.instructions`",
    )
    metadata = _metadata_dict(request_payload.get("metadata"))
    max_output_tokens = _optional_positive_int(
        request_payload.get("max_output_tokens"),
        "Gemini host control request `request.max_output_tokens`",
    )
    audit_intensity = _audit_intensity(
        request_payload.get("audit_intensity"),
        "Gemini host control request `request.audit_intensity`",
    )
    action_tag = _required_non_empty_string(
        payload.get("action_tag"),
        "Gemini host control request `action_tag`",
    )
    return GeminiHostControlRequest(
        action_tag=action_tag,
        model=model,
        input_text=input_text,
        instructions=instructions,
        metadata=metadata,
        max_output_tokens=max_output_tokens,
        audit_intensity=audit_intensity,
    )


def _coerce_session(session: GeminiRuntimeSession | None) -> GeminiRuntimeSession:
    if session is None:
        return GeminiRuntimeSession()
    if not isinstance(session, GeminiRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_gemini_host_control.session must be GeminiRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _required_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _required_non_empty_string(value, label)


def _optional_positive_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an integer, got {actual_type}.")
    if value <= 0:
        raise ValueError(f"{label} must be positive when provided.")
    return value


def _audit_intensity(value: Any, label: str) -> str:
    if value is None:
        return "minimal"
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    normalized = value.strip()
    if normalized not in _AUDIT_INTENSITIES:
        raise ValueError(f"{label} must be one of {sorted(_AUDIT_INTENSITIES)!r}.")
    return normalized


def _metadata_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(
            "Gemini host control request `request.metadata` must be an object, "
            f"got {actual_type}."
        )
    metadata = dict(value)
    if any(not (isinstance(key, str) and key.strip()) for key in metadata):
        raise ValueError(
            "Gemini host control request `request.metadata` keys must be non-empty strings after trimming."
        )
    return metadata


__all__ = [
    "GeminiHostControlRequest",
    "GeminiHostControlResult",
    "GeminiInteractionStreamTransportError",
    "run_gemini_host_control",
]
