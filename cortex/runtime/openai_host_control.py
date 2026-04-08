"""Bounded outbound OpenAI host-control composition over the accepted K1 runtime shell."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from cortex.sre.verified_work import VerificationOutcome, WorkContract

from .openai import (
    OpenAIRuntimeSession,
    run_openai_runtime_step,
    run_openai_runtime_verification_step,
)
from .openai_cli import build_openai_cli_record
from .openai_ingress import parse_openai_host_event_envelope
from .openai_host_transport import (
    OpenAIResponseStreamTransportError,
    execute_openai_response_stream_turn,
)
from .openai_verified_work import (
    build_openai_verified_work_instructions,
    build_openai_verified_work_repair_ticket,
    verify_openai_verified_work_result,
)

_ACTION_TAG = "openai-response-stream"
_TOP_LEVEL_KEYS = frozenset({"action_tag", "request"})
_REQUEST_KEYS = frozenset(
    {
        "model",
        "input",
        "instructions",
        "metadata",
        "max_output_tokens",
        "stream",
        "work_contract",
    }
)
_WORK_CONTRACT_KEYS = frozenset(
    {
        "allowed_write_paths",
        "verification_profile",
        "output_carrier",
        "max_repair_turns",
    }
)

OpenAIResponseStreamTransport = Callable[..., list[dict[str, Any]]]


@dataclass(frozen=True, slots=True)
class OpenAIHostControlRequest:
    action_tag: str
    model: str
    input_text: str
    instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    max_output_tokens: int | None = None
    work_contract: WorkContract | None = None

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"OpenAIHostControlRequest.action_tag must be `{_ACTION_TAG}`."
            )
        if not (isinstance(self.model, str) and self.model.strip()):
            raise ValueError(
                "OpenAIHostControlRequest.model must be non-empty after trimming."
            )
        if not (isinstance(self.input_text, str) and self.input_text.strip()):
            raise ValueError(
                "OpenAIHostControlRequest.input_text must be non-empty after trimming."
            )
        if self.instructions is not None and not (
            isinstance(self.instructions, str) and self.instructions.strip()
        ):
            raise ValueError(
                "OpenAIHostControlRequest.instructions must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "OpenAIHostControlRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if any(not (isinstance(key, str) and key.strip()) for key in self.metadata):
            raise ValueError(
                "OpenAIHostControlRequest.metadata keys must be non-empty strings after trimming."
            )
        if self.max_output_tokens is not None:
            if isinstance(self.max_output_tokens, bool) or not isinstance(
                self.max_output_tokens,
                int,
            ):
                actual_type = type(self.max_output_tokens).__name__
                raise TypeError(
                    "OpenAIHostControlRequest.max_output_tokens must be int | None, "
                    f"got {actual_type}."
                )
            if self.max_output_tokens <= 0:
                raise ValueError(
                    "OpenAIHostControlRequest.max_output_tokens must be positive when provided."
                )
        if self.work_contract is not None and not isinstance(self.work_contract, WorkContract):
            actual_type = type(self.work_contract).__name__
            raise TypeError(
                "OpenAIHostControlRequest.work_contract must be WorkContract | None, "
                f"got {actual_type}."
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
        if self.work_contract is not None:
            request_payload["work_contract"] = self.work_contract.as_payload()
        return {
            "action_tag": self.action_tag,
            "request": request_payload,
        }


@dataclass(frozen=True, slots=True)
class OpenAIHostControlResult:
    action_tag: str
    records: tuple[dict[str, Any], ...]
    result_text: str | None = None
    verification: VerificationOutcome | None = None
    attempt_count: int | None = None

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"OpenAIHostControlResult.action_tag must be `{_ACTION_TAG}`."
            )
        if any(not isinstance(record, dict) for record in self.records):
            raise TypeError(
                "OpenAIHostControlResult.records must contain only dict[str, Any] records."
            )
        if self.result_text is not None and not (
            isinstance(self.result_text, str) and self.result_text.strip()
        ):
            raise ValueError(
                "OpenAIHostControlResult.result_text must be non-empty after trimming when provided."
            )
        if self.verification is not None and not isinstance(
            self.verification,
            VerificationOutcome,
        ):
            actual_type = type(self.verification).__name__
            raise TypeError(
                "OpenAIHostControlResult.verification must be VerificationOutcome | None, "
                f"got {actual_type}."
            )
        if self.attempt_count is not None:
            if isinstance(self.attempt_count, bool) or not isinstance(self.attempt_count, int):
                actual_type = type(self.attempt_count).__name__
                raise TypeError(
                    "OpenAIHostControlResult.attempt_count must be int | None, "
                    f"got {actual_type}."
                )
            if self.attempt_count <= 0:
                raise ValueError(
                    "OpenAIHostControlResult.attempt_count must be positive when provided."
                )
        if self.verification is None and self.attempt_count is not None:
            raise ValueError(
                "OpenAIHostControlResult.attempt_count may be provided only when verification is present."
            )

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "action_tag": self.action_tag,
            "records": [dict(record) for record in self.records],
        }
        if self.result_text is not None:
            payload["result_text"] = self.result_text
        if self.verification is not None:
            payload["verification"] = self.verification.as_payload()
        if self.attempt_count is not None:
            payload["attempt_count"] = self.attempt_count
        return payload


def run_openai_host_control(
    request: OpenAIHostControlRequest,
    session: OpenAIRuntimeSession | None = None,
    *,
    transport: OpenAIResponseStreamTransport | None = None,
) -> tuple[OpenAIHostControlResult, OpenAIRuntimeSession]:
    if not isinstance(request, OpenAIHostControlRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_openai_host_control.request must be OpenAIHostControlRequest, "
            f"got {actual_type}."
        )
    current_session = _coerce_session(session)
    transport_callable = transport if transport is not None else execute_openai_response_stream_turn
    if not callable(transport_callable):
        actual_type = type(transport_callable).__name__
        raise TypeError(
            "run_openai_host_control.transport must be callable when provided, "
            f"got {actual_type}."
        )
    if request.work_contract is None:
        raw_events, records, current_session, result_text = _run_openai_host_control_attempt(
            request,
            current_session,
            transport_callable=transport_callable,
        )
        return OpenAIHostControlResult(
            action_tag=request.action_tag,
            records=tuple(records),
            result_text=result_text,
        ), current_session

    verified_request = OpenAIHostControlRequest(
        action_tag=request.action_tag,
        model=request.model,
        input_text=request.input_text,
        instructions=build_openai_verified_work_instructions(request.work_contract),
        metadata=request.metadata,
        max_output_tokens=request.max_output_tokens,
        work_contract=request.work_contract,
    )
    raw_events, records, current_session, result_text = _run_openai_host_control_attempt(
        verified_request,
        current_session,
        transport_callable=transport_callable,
    )
    try:
        _, verification = verify_openai_verified_work_result(
            result_text,
            request.work_contract,
        )
    except RuntimeError as exc:
        raise OpenAIResponseStreamTransportError(
            f"OpenAI verified-work verifier failed: {exc}"
        ) from exc
    current_session = run_openai_runtime_verification_step(
        verification,
        current_session,
        work_contract=request.work_contract,
        remaining_repairs=request.work_contract.max_repair_turns,
    )
    attempt_count = 1
    final_result_text = result_text
    if (
        request.work_contract.max_repair_turns > 0
        and current_session.next_recommended_move == "repair"
    ):
        response_id = _last_response_id(raw_events)
        if response_id is None:
            raise OpenAIResponseStreamTransportError(
                "OpenAI verified-work continuation requires a response_id on the first attempt."
            )
        repair_ticket = build_openai_verified_work_repair_ticket(verification)
        repair_events, repair_records, repair_session, repair_result_text = _run_openai_host_control_attempt(
            verified_request,
            current_session,
            transport_callable=transport_callable,
            previous_response_id=response_id,
            input_text_override=repair_ticket,
        )
        records.extend(repair_records)
        final_result_text = repair_result_text
        try:
            _, verification = verify_openai_verified_work_result(
                repair_result_text,
                request.work_contract,
            )
        except RuntimeError as exc:
            raise OpenAIResponseStreamTransportError(
                f"OpenAI verified-work verifier failed: {exc}"
            ) from exc
        current_session = run_openai_runtime_verification_step(
            verification,
            repair_session,
            work_contract=request.work_contract,
            remaining_repairs=0,
        )
        attempt_count = 2

    return OpenAIHostControlResult(
        action_tag=request.action_tag,
        records=tuple(records),
        result_text=final_result_text,
        verification=verification,
        attempt_count=attempt_count,
    ), current_session


def _extract_response_output_text(raw_events: list[dict[str, Any]]) -> str | None:
    chunks: list[str] = []
    for raw_event in raw_events:
        if raw_event.get("type") != "response.output_text.delta":
            continue
        delta = raw_event.get("delta")
        if isinstance(delta, str) and delta:
            chunks.append(delta)
    if not chunks:
        return None
    joined = "".join(chunks).strip()
    return joined or None


def _run_openai_host_control_attempt(
    request: OpenAIHostControlRequest,
    session: OpenAIRuntimeSession,
    *,
    transport_callable: Callable[..., list[dict[str, Any]]],
    previous_response_id: str | None = None,
    input_text_override: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], OpenAIRuntimeSession, str | None]:
    raw_events = _call_transport_turn(
        transport_callable,
        request,
        previous_response_id=previous_response_id,
        input_text_override=input_text_override,
    )
    if not raw_events:
        raise OpenAIResponseStreamTransportError(
            "OpenAI response stream returned zero host events."
        )

    current_session = session
    records: list[dict[str, Any]] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, Mapping):
            actual_type = type(raw_event).__name__
            raise OpenAIResponseStreamTransportError(
                "OpenAI response stream must yield JSON-object events, "
                f"got {actual_type}."
            )
        try:
            envelope = parse_openai_host_event_envelope(raw_event)
            step_result = run_openai_runtime_step(
                envelope.event_type,
                envelope.payload,
                current_session,
            )
        except (TypeError, ValueError) as exc:
            raise OpenAIResponseStreamTransportError(
                f"OpenAI response stream yielded an unlawful host event: {exc}"
            ) from exc
        records.append(build_openai_cli_record(step_result))
        current_session = step_result.session
    return raw_events, records, current_session, _extract_response_output_text(raw_events)


def _call_transport_turn(
    transport_callable: Callable[..., list[dict[str, Any]]],
    request: OpenAIHostControlRequest,
    *,
    previous_response_id: str | None,
    input_text_override: str | None,
) -> list[dict[str, Any]]:
    if previous_response_id is None and input_text_override is None:
        return transport_callable(request)
    try:
        return transport_callable(
            request,
            previous_response_id=previous_response_id,
            input_text_override=input_text_override,
        )
    except TypeError as exc:
        raise OpenAIResponseStreamTransportError(
            "Verified-work continuation requires a transport that accepts "
            "`previous_response_id` and `input_text_override`."
        ) from exc


def _last_response_id(raw_events: list[dict[str, Any]]) -> str | None:
    for raw_event in reversed(raw_events):
        response_id = raw_event.get("response_id")
        if isinstance(response_id, str) and response_id.strip():
            return response_id.strip()
        response = raw_event.get("response")
        if isinstance(response, Mapping):
            nested_response_id = response.get("id")
            if isinstance(nested_response_id, str) and nested_response_id.strip():
                return nested_response_id.strip()
    return None


def _coerce_openai_host_control_request(
    payload: Mapping[str, Any],
) -> OpenAIHostControlRequest:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "OpenAI host control request payload must be a mapping, "
            f"got {actual_type}."
        )
    unknown_top_level_keys = sorted(set(payload) - _TOP_LEVEL_KEYS)
    if unknown_top_level_keys:
        raise ValueError(
            "OpenAI host control request accepts only `action_tag` and `request`; "
            f"got unsupported top-level keys: {', '.join(unknown_top_level_keys)}."
        )
    if "action_tag" not in payload:
        raise ValueError("OpenAI host control request must include `action_tag`.")
    if "request" not in payload:
        raise ValueError("OpenAI host control request must include `request`.")

    request_payload = payload["request"]
    if not isinstance(request_payload, Mapping):
        actual_type = type(request_payload).__name__
        raise TypeError(
            "OpenAI host control request `request` must be an object, "
            f"got {actual_type}."
        )

    unknown_request_keys = sorted(set(request_payload) - _REQUEST_KEYS)
    if unknown_request_keys:
        raise ValueError(
            "OpenAI host control request uses a strict text-only whitelist; "
            f"unsupported request keys: {', '.join(unknown_request_keys)}."
        )

    if "stream" in request_payload and request_payload["stream"] is not True:
        raise ValueError(
            "OpenAI host control request `stream` must be `true` when provided."
        )

    model = _required_non_empty_string(
        request_payload.get("model"),
        "OpenAI host control request `request.model`",
    )
    input_text = _required_non_empty_string(
        request_payload.get("input"),
        "OpenAI host control request `request.input`",
    )
    instructions = _optional_non_empty_string(
        request_payload.get("instructions"),
        "OpenAI host control request `request.instructions`",
    )
    metadata = _metadata_dict(request_payload.get("metadata"))
    max_output_tokens = _optional_positive_int(
        request_payload.get("max_output_tokens"),
        "OpenAI host control request `request.max_output_tokens`",
    )
    work_contract = _work_contract(
        request_payload.get("work_contract"),
        "OpenAI host control request `request.work_contract`",
    )
    if work_contract is not None and instructions is not None:
        raise ValueError(
            "OpenAIHostControlRequest.instructions must be omitted when work_contract is present because verified-work instructions are fixed."
        )
    action_tag = _required_non_empty_string(
        payload.get("action_tag"),
        "OpenAI host control request `action_tag`",
    )
    return OpenAIHostControlRequest(
        action_tag=action_tag,
        model=model,
        input_text=input_text,
        instructions=instructions,
        metadata=metadata,
        max_output_tokens=max_output_tokens,
        work_contract=work_contract,
    )


def _coerce_session(session: OpenAIRuntimeSession | None) -> OpenAIRuntimeSession:
    if session is None:
        return OpenAIRuntimeSession()
    if not isinstance(session, OpenAIRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_openai_host_control.session must be OpenAIRuntimeSession | None, "
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


def _metadata_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(
            "OpenAI host control request `request.metadata` must be an object, "
            f"got {actual_type}."
        )
    metadata = dict(value)
    if any(not (isinstance(key, str) and key.strip()) for key in metadata):
        raise ValueError(
            "OpenAI host control request `request.metadata` keys must be non-empty strings after trimming."
        )
    return metadata


def _work_contract(value: Any, label: str) -> WorkContract | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    unknown_keys = sorted(set(value) - _WORK_CONTRACT_KEYS)
    if unknown_keys:
        raise ValueError(
            f"{label} accepts only {sorted(_WORK_CONTRACT_KEYS)!r}; unsupported keys: {', '.join(unknown_keys)}."
        )
    allowed_write_paths = value.get("allowed_write_paths")
    if not isinstance(allowed_write_paths, list):
        actual_type = type(allowed_write_paths).__name__
        raise TypeError(f"{label}.allowed_write_paths must be a list, got {actual_type}.")
    verification_profile = _required_non_empty_string(
        value.get("verification_profile"),
        f"{label}.verification_profile",
    )
    output_carrier = _required_non_empty_string(
        value.get("output_carrier"),
        f"{label}.output_carrier",
    )
    max_repair_turns = value.get("max_repair_turns")
    if isinstance(max_repair_turns, bool) or not isinstance(max_repair_turns, int):
        actual_type = type(max_repair_turns).__name__
        raise TypeError(f"{label}.max_repair_turns must be an integer, got {actual_type}.")
    return WorkContract(
        allowed_write_paths=tuple(allowed_write_paths),
        verification_profile=verification_profile,
        output_carrier=output_carrier,
        max_repair_turns=max_repair_turns,
    )


__all__ = [
    "OpenAIHostControlRequest",
    "OpenAIHostControlResult",
    "OpenAIResponseStreamTransportError",
    "run_openai_host_control",
]
