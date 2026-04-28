"""Bounded outbound Claude host-control composition over the accepted runtime shell."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from cortex.sre.guidance import (
    DEFAULT_PRODUCT_GUIDANCE_MODE,
    append_guidance_to_channel,
    build_guidance_context_from_session,
)
from cortex.sre.closure import assess_output_closure

from .runtime import ClaudeRuntimeSession, run_claude_runtime_step
from .cli import build_claude_cli_record
from .ingress import parse_claude_host_event_envelope
from .host_transport import (
    ClaudeMessageStreamTransportError,
    execute_claude_message_stream,
)

_ACTION_TAG = "claude-message-stream"
_TOP_LEVEL_KEYS = frozenset({"action_tag", "request"})
_REQUEST_KEYS = frozenset(
    {
        "model",
        "input",
        "system",
        "metadata",
        "max_output_tokens",
        "stream",
        "audit_intensity",
    }
)
_AUDIT_INTENSITIES = frozenset({"minimal", "focused", "structured"})

ClaudeMessageStreamTransport = Callable[
    ["ClaudeHostControlRequest"],
    list[dict[str, Any]],
]


@dataclass(frozen=True, slots=True)
class ClaudeHostControlRequest:
    action_tag: str
    model: str
    input_text: str
    max_output_tokens: int
    system: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_intensity: str = "minimal"

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"ClaudeHostControlRequest.action_tag must be `{_ACTION_TAG}`."
            )
        if not (isinstance(self.model, str) and self.model.strip()):
            raise ValueError(
                "ClaudeHostControlRequest.model must be non-empty after trimming."
            )
        if not (isinstance(self.input_text, str) and self.input_text.strip()):
            raise ValueError(
                "ClaudeHostControlRequest.input_text must be non-empty after trimming."
            )
        if self.system is not None and not (
            isinstance(self.system, str) and self.system.strip()
        ):
            raise ValueError(
                "ClaudeHostControlRequest.system must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "ClaudeHostControlRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if any(not (isinstance(key, str) and key.strip()) for key in self.metadata):
            raise ValueError(
                "ClaudeHostControlRequest.metadata keys must be non-empty strings after trimming."
            )
        if isinstance(self.max_output_tokens, bool) or not isinstance(
            self.max_output_tokens,
            int,
        ):
            actual_type = type(self.max_output_tokens).__name__
            raise TypeError(
                "ClaudeHostControlRequest.max_output_tokens must be int, "
                f"got {actual_type}."
            )
        if self.max_output_tokens <= 0:
            raise ValueError(
                "ClaudeHostControlRequest.max_output_tokens must be positive."
            )
        if self.audit_intensity not in _AUDIT_INTENSITIES:
            raise ValueError(
                "ClaudeHostControlRequest.audit_intensity must be one of "
                f"{sorted(_AUDIT_INTENSITIES)!r}."
            )

    def as_payload(self) -> dict[str, Any]:
        request_payload: dict[str, Any] = {
            "model": self.model,
            "input": self.input_text,
            "max_output_tokens": self.max_output_tokens,
        }
        if self.system is not None:
            request_payload["system"] = self.system
        if self.metadata:
            request_payload["metadata"] = dict(self.metadata)
        if self.audit_intensity != "minimal":
            request_payload["audit_intensity"] = self.audit_intensity
        return {
            "action_tag": self.action_tag,
            "request": request_payload,
        }


@dataclass(frozen=True, slots=True)
class ClaudeHostControlResult:
    action_tag: str
    records: tuple[dict[str, Any], ...]
    closure_assessment: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"ClaudeHostControlResult.action_tag must be `{_ACTION_TAG}`."
            )
        if any(not isinstance(record, dict) for record in self.records):
            raise TypeError(
                "ClaudeHostControlResult.records must contain only dict[str, Any] records."
            )
        if self.closure_assessment is not None and not isinstance(
            self.closure_assessment,
            dict,
        ):
            actual_type = type(self.closure_assessment).__name__
            raise TypeError(
                "ClaudeHostControlResult.closure_assessment must be dict[str, Any] | None, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "action_tag": self.action_tag,
            "records": [dict(record) for record in self.records],
        }
        if self.closure_assessment is not None:
            payload["closure_assessment"] = dict(self.closure_assessment)
        return payload


def run_claude_host_control(
    request: ClaudeHostControlRequest,
    session: ClaudeRuntimeSession | None = None,
    *,
    transport: ClaudeMessageStreamTransport | None = None,
) -> tuple[ClaudeHostControlResult, ClaudeRuntimeSession]:
    if not isinstance(request, ClaudeHostControlRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_claude_host_control.request must be ClaudeHostControlRequest, "
            f"got {actual_type}."
        )
    current_session = _coerce_session(session)
    transport_callable = transport if transport is not None else execute_claude_message_stream
    if not callable(transport_callable):
        actual_type = type(transport_callable).__name__
        raise TypeError(
            "run_claude_host_control.transport must be callable when provided, "
            f"got {actual_type}."
        )

    visible_request = _request_with_model_visible_guidance(request, current_session)
    raw_events = transport_callable(visible_request)
    if not raw_events:
        raise ClaudeMessageStreamTransportError(
            "Claude interaction stream returned zero host events."
        )

    action_session_id = current_session.session_id or "cl-session-1"
    records: list[dict[str, Any]] = []
    output_chunks: list[str] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, Mapping):
            actual_type = type(raw_event).__name__
            raise ClaudeMessageStreamTransportError(
                "Claude interaction stream must yield JSON-object events, "
                f"got {actual_type}."
            )
        try:
            normalized_event = dict(raw_event)
            delta = normalized_event.get("delta")
            if isinstance(delta, str) and delta:
                output_chunks.append(delta)
            normalized_event.setdefault("session_id", action_session_id)
            envelope = parse_claude_host_event_envelope(normalized_event)
            step_result = run_claude_runtime_step(
                envelope.event_type,
                envelope.payload,
                current_session,
                audit_intensity=request.audit_intensity,
            )
        except (TypeError, ValueError) as exc:
            raise ClaudeMessageStreamTransportError(
                f"Claude interaction stream yielded an unlawful host event: {exc}"
            ) from exc
        records.append(build_claude_cli_record(step_result))
        current_session = step_result.session

    closure_assessment = assess_output_closure(
        "".join(output_chunks),
        commitment_result_kinds=tuple(
            record.get("commitment_result_kind") for record in records
        ),
        blocker_present=any(record.get("closure_required") for record in records),
    )
    closure_payload = (
        closure_assessment.as_payload()
        if closure_assessment.claim_detected
        or closure_assessment.status.value in {"blocked", "uncertified"}
        else None
    )

    return ClaudeHostControlResult(
        action_tag=request.action_tag,
        records=tuple(records),
        closure_assessment=closure_payload,
    ), current_session


def _coerce_claude_host_control_request(
    payload: Mapping[str, Any],
) -> ClaudeHostControlRequest:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "Claude host control request payload must be a mapping, "
            f"got {actual_type}."
        )
    unknown_top_level_keys = sorted(set(payload) - _TOP_LEVEL_KEYS)
    if unknown_top_level_keys:
        raise ValueError(
            "Claude host control request accepts only `action_tag` and `request`; "
            f"got unsupported top-level keys: {', '.join(unknown_top_level_keys)}."
        )
    if "action_tag" not in payload:
        raise ValueError("Claude host control request must include `action_tag`.")
    if "request" not in payload:
        raise ValueError("Claude host control request must include `request`.")

    request_payload = payload["request"]
    if not isinstance(request_payload, Mapping):
        actual_type = type(request_payload).__name__
        raise TypeError(
            "Claude host control request `request` must be an object, "
            f"got {actual_type}."
        )

    unknown_request_keys = sorted(set(request_payload) - _REQUEST_KEYS)
    if unknown_request_keys:
        raise ValueError(
            "Claude host control request uses a strict text-only whitelist; "
            f"unsupported request keys: {', '.join(unknown_request_keys)}."
        )

    if "stream" in request_payload and request_payload["stream"] is not True:
        raise ValueError(
            "Claude host control request `stream` must be `true` when provided."
        )

    model = _required_non_empty_string(
        request_payload.get("model"),
        "Claude host control request `request.model`",
    )
    input_text = _required_non_empty_string(
        request_payload.get("input"),
        "Claude host control request `request.input`",
    )
    max_output_tokens = _required_positive_int(
        request_payload.get("max_output_tokens"),
        "Claude host control request `request.max_output_tokens`",
    )
    system = _optional_non_empty_string(
        request_payload.get("system"),
        "Claude host control request `request.system`",
    )
    metadata = _metadata_dict(request_payload.get("metadata"))
    audit_intensity = _audit_intensity(
        request_payload.get("audit_intensity"),
        "Claude host control request `request.audit_intensity`",
    )
    action_tag = _required_non_empty_string(
        payload.get("action_tag"),
        "Claude host control request `action_tag`",
    )
    return ClaudeHostControlRequest(
        action_tag=action_tag,
        model=model,
        input_text=input_text,
        max_output_tokens=max_output_tokens,
        system=system,
        metadata=metadata,
        audit_intensity=audit_intensity,
    )


def _request_with_model_visible_guidance(
    request: ClaudeHostControlRequest,
    session: ClaudeRuntimeSession,
) -> ClaudeHostControlRequest:
    guidance_context = build_guidance_context_from_session(
        host_name="claude",
        surface="claude-message-stream",
        transport_channel="system",
        session=session,
    )
    system_text = append_guidance_to_channel(
        request.system,
        guidance_context,
        mode=DEFAULT_PRODUCT_GUIDANCE_MODE,
        task_text=request.input_text,
    )
    return ClaudeHostControlRequest(
        action_tag=request.action_tag,
        model=request.model,
        input_text=request.input_text,
        max_output_tokens=request.max_output_tokens,
        system=system_text if system_text else None,
        metadata=request.metadata,
        audit_intensity=request.audit_intensity,
    )


def _coerce_session(session: ClaudeRuntimeSession | None) -> ClaudeRuntimeSession:
    if session is None:
        return ClaudeRuntimeSession()
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_host_control.session must be ClaudeRuntimeSession | None, "
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


def _required_positive_int(value: Any, label: str) -> int:
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
            "Claude host control request `request.metadata` must be an object, "
            f"got {actual_type}."
        )
    metadata = dict(value)
    if any(not (isinstance(key, str) and key.strip()) for key in metadata):
        raise ValueError(
            "Claude host control request `request.metadata` keys must be non-empty strings after trimming."
        )
    return metadata


__all__ = [
    "ClaudeHostControlRequest",
    "ClaudeHostControlResult",
    "ClaudeMessageStreamTransportError",
    "run_claude_host_control",
]
