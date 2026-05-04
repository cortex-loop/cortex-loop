"""Codex App/CLI product hook coordinator.

This module owns the product-side lifecycle bridge for Codex App/CLI hooks. It
normalizes hook payloads, records private per-session state, consumes existing
SRE intervention law, and maps the resulting lifecycle directive to host JSON.

It deliberately does not activate project hook configuration, import repo
workflow guardrails, or render hook-local prompt strings.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from cortex.sre.debt_control import DebtControlPressure
from cortex.sre.expectations import ExpectationLedger, ResolutionDeficitState
from cortex.sre.interventions import (
    GroundedInterventionDecision,
    build_runtime_grounded_intervention,
)
from cortex.sre.operator_routing import OperatorRouteProfile

from .codex_app_cli_lifecycle import (
    OpenAICodexLifecycleDirective,
    OpenAICodexLifecycleDirectiveAction,
    OpenAICodexLifecycleEvent,
    OpenAICodexLifecycleFacts,
    build_openai_codex_app_cli_lifecycle_directive,
)


class OpenAICodexHookHostDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


@dataclass(frozen=True, slots=True)
class OpenAICodexHookPayload:
    session_id: str
    hook_event_name: OpenAICodexLifecycleEvent
    turn_id: str | None = None
    transcript_path: str | None = None
    cwd: str | None = None
    model: str | None = None
    permission_mode: str | None = None
    stop_hook_active: bool = False
    last_assistant_message: str | None = None
    tool_name: str | None = None
    tool_input: Mapping[str, Any] | None = None
    tool_response: Mapping[str, Any] | None = None
    error: str | None = None
    prompt_text_hash: str | None = None
    raw_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_string(self.session_id, "OpenAICodexHookPayload.session_id")
        if not isinstance(self.hook_event_name, OpenAICodexLifecycleEvent):
            actual_type = type(self.hook_event_name).__name__
            raise TypeError(
                "OpenAICodexHookPayload.hook_event_name must be "
                f"OpenAICodexLifecycleEvent, got {actual_type}."
            )
        for field_name in (
            "turn_id",
            "transcript_path",
            "cwd",
            "model",
            "permission_mode",
            "last_assistant_message",
            "tool_name",
            "error",
            "prompt_text_hash",
        ):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OpenAICodexHookPayload.{field_name} must be str | None, "
                    f"got {actual_type}."
                )
        if not isinstance(self.stop_hook_active, bool):
            actual_type = type(self.stop_hook_active).__name__
            raise TypeError(
                "OpenAICodexHookPayload.stop_hook_active must be bool, "
                f"got {actual_type}."
            )
        for field_name in ("tool_input", "tool_response"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, Mapping):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OpenAICodexHookPayload.{field_name} must be Mapping | None, "
                    f"got {actual_type}."
                )
        if any(not (isinstance(key, str) and key.strip()) for key in self.raw_keys):
            raise ValueError("OpenAICodexHookPayload.raw_keys must be non-empty strings.")

    @property
    def has_transcript_backed_assistant_turn(self) -> bool:
        return bool(
            self.hook_event_name is OpenAICodexLifecycleEvent.STOP
            and isinstance(self.transcript_path, str)
            and self.transcript_path.strip()
            and isinstance(self.last_assistant_message, str)
            and self.last_assistant_message.strip()
        )

    def lifecycle_facts(self) -> OpenAICodexLifecycleFacts:
        return OpenAICodexLifecycleFacts(
            hook_event_name=self.hook_event_name,
            transcript_path=self.transcript_path,
            last_assistant_message=self.last_assistant_message,
            stop_hook_active=self.stop_hook_active,
            prior_act_anchor=self.has_transcript_backed_assistant_turn,
        )

    def as_payload(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "hook_event_name": self.hook_event_name.value,
            "transcript_path": self.transcript_path,
            "cwd": self.cwd,
            "model": self.model,
            "permission_mode": self.permission_mode,
            "stop_hook_active": self.stop_hook_active,
            "has_transcript_backed_assistant_turn": self.has_transcript_backed_assistant_turn,
            "tool_name": self.tool_name,
            "tool_input_present": self.tool_input is not None,
            "tool_response_present": self.tool_response is not None,
            "error_present": self.error is not None,
            "prompt_text_hash": self.prompt_text_hash,
            "raw_keys": list(self.raw_keys),
        }


@dataclass(frozen=True, slots=True)
class OpenAICodexSessionState:
    session_id: str
    current_step: int = 0
    last_turn_id: str | None = None
    transcript_path: str | None = None
    prompt_text_hash: str | None = None
    prior_assistant_turn_seen: bool = False
    tool_event_count: int = 0
    tool_failure_count: int = 0
    stop_event_count: int = 0
    warning_tags: tuple[str, ...] = ()
    lifecycle_counts: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty_string(self.session_id, "OpenAICodexSessionState.session_id")
        for field_name in (
            "current_step",
            "tool_event_count",
            "tool_failure_count",
            "stop_event_count",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"OpenAICodexSessionState.{field_name} must be a non-negative int."
                )
        for field_name in ("last_turn_id", "transcript_path", "prompt_text_hash"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OpenAICodexSessionState.{field_name} must be str | None, "
                    f"got {actual_type}."
                )
        if not isinstance(self.prior_assistant_turn_seen, bool):
            actual_type = type(self.prior_assistant_turn_seen).__name__
            raise TypeError(
                "OpenAICodexSessionState.prior_assistant_turn_seen must be bool, "
                f"got {actual_type}."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.warning_tags):
            raise ValueError(
                "OpenAICodexSessionState.warning_tags must contain non-empty strings."
            )
        for item in self.lifecycle_counts:
            if not (
                isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[0], str)
                and item[0].strip()
                and isinstance(item[1], int)
                and item[1] >= 0
            ):
                raise ValueError(
                    "OpenAICodexSessionState.lifecycle_counts must contain "
                    "(event_name, non_negative_count) tuples."
                )

    def as_payload(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "current_step": self.current_step,
            "last_turn_id": self.last_turn_id,
            "transcript_path": self.transcript_path,
            "prompt_text_hash": self.prompt_text_hash,
            "prior_assistant_turn_seen": self.prior_assistant_turn_seen,
            "tool_event_count": self.tool_event_count,
            "tool_failure_count": self.tool_failure_count,
            "stop_event_count": self.stop_event_count,
            "warning_tags": list(self.warning_tags),
            "lifecycle_counts": [
                {"hook_event_name": event_name, "count": count}
                for event_name, count in self.lifecycle_counts
            ],
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "OpenAICodexSessionState":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "OpenAICodexSessionState.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            session_id=_required_string(payload.get("session_id"), "session_id"),
            current_step=_optional_int(payload.get("current_step"), 0),
            last_turn_id=_optional_string(payload.get("last_turn_id")),
            transcript_path=_optional_string(payload.get("transcript_path")),
            prompt_text_hash=_optional_string(payload.get("prompt_text_hash")),
            prior_assistant_turn_seen=bool(payload.get("prior_assistant_turn_seen", False)),
            tool_event_count=_optional_int(payload.get("tool_event_count"), 0),
            tool_failure_count=_optional_int(payload.get("tool_failure_count"), 0),
            stop_event_count=_optional_int(payload.get("stop_event_count"), 0),
            warning_tags=tuple(
                str(tag).strip()
                for tag in payload.get("warning_tags", ())
                if str(tag).strip()
            ),
            lifecycle_counts=tuple(
                (
                    _required_string(item.get("hook_event_name"), "hook_event_name"),
                    _optional_int(item.get("count"), 0),
                )
                for item in payload.get("lifecycle_counts", ())
                if isinstance(item, Mapping)
            ),
        )


@dataclass(frozen=True, slots=True)
class OpenAICodexOperatorRouteView:
    profile: OperatorRouteProfile = OperatorRouteProfile.EXECUTE_STANDARD
    blocked_reason: str | None = None
    brain_capability_assessment: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile, OperatorRouteProfile):
            actual_type = type(self.profile).__name__
            raise TypeError(
                "OpenAICodexOperatorRouteView.profile must be OperatorRouteProfile, "
                f"got {actual_type}."
            )
        if self.blocked_reason is not None and not (
            isinstance(self.blocked_reason, str) and self.blocked_reason.strip()
        ):
            raise ValueError(
                "OpenAICodexOperatorRouteView.blocked_reason must be non-empty "
                "when provided."
            )


@dataclass(frozen=True, slots=True)
class OpenAICodexRuntimeSnapshot:
    expectation_ledger: ExpectationLedger = field(default_factory=ExpectationLedger)
    resolution_deficit: ResolutionDeficitState = field(default_factory=ResolutionDeficitState)
    debt_control: DebtControlPressure = field(default_factory=DebtControlPressure)
    operator_route: Any = field(default_factory=OpenAICodexOperatorRouteView)
    current_step: int = 0
    closure_required: bool = False
    closure_reason_tags: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.expectation_ledger, ExpectationLedger):
            actual_type = type(self.expectation_ledger).__name__
            raise TypeError(
                "OpenAICodexRuntimeSnapshot.expectation_ledger must be "
                f"ExpectationLedger, got {actual_type}."
            )
        if not isinstance(self.resolution_deficit, ResolutionDeficitState):
            actual_type = type(self.resolution_deficit).__name__
            raise TypeError(
                "OpenAICodexRuntimeSnapshot.resolution_deficit must be "
                f"ResolutionDeficitState, got {actual_type}."
            )
        if not isinstance(self.debt_control, DebtControlPressure):
            actual_type = type(self.debt_control).__name__
            raise TypeError(
                "OpenAICodexRuntimeSnapshot.debt_control must be "
                f"DebtControlPressure, got {actual_type}."
            )
        if not isinstance(self.current_step, int) or self.current_step < 0:
            raise ValueError("OpenAICodexRuntimeSnapshot.current_step must be non-negative.")
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "OpenAICodexRuntimeSnapshot.closure_required must be bool, "
                f"got {actual_type}."
            )
        for field_name in ("closure_reason_tags", "warnings"):
            values = getattr(self, field_name)
            if any(not (isinstance(value, str) and value.strip()) for value in values):
                raise ValueError(
                    f"OpenAICodexRuntimeSnapshot.{field_name} must contain "
                    "non-empty strings."
                )


@dataclass(frozen=True, slots=True)
class OpenAICodexHookHostResponse:
    decision: OpenAICodexHookHostDecision = OpenAICodexHookHostDecision.ALLOW
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision, OpenAICodexHookHostDecision):
            actual_type = type(self.decision).__name__
            raise TypeError(
                "OpenAICodexHookHostResponse.decision must be "
                f"OpenAICodexHookHostDecision, got {actual_type}."
            )
        if self.reason is not None and not (
            isinstance(self.reason, str) and self.reason.strip()
        ):
            raise ValueError(
                "OpenAICodexHookHostResponse.reason must be non-empty when provided."
            )
        if self.decision is OpenAICodexHookHostDecision.BLOCK and self.reason is None:
            raise ValueError("OpenAICodexHookHostResponse.reason is required for block.")
        if self.decision is OpenAICodexHookHostDecision.ALLOW and self.reason is not None:
            raise ValueError("OpenAICodexHookHostResponse.reason is only valid for block.")

    @property
    def stdout_payload(self) -> dict[str, str] | None:
        if self.decision is OpenAICodexHookHostDecision.BLOCK:
            return {"decision": "block", "reason": self.reason or ""}
        return None


@dataclass(frozen=True, slots=True)
class OpenAICodexHookCoordinatorResult:
    hook_payload: OpenAICodexHookPayload
    session_state: OpenAICodexSessionState
    grounded_intervention: GroundedInterventionDecision
    directive: OpenAICodexLifecycleDirective
    host_response: OpenAICodexHookHostResponse

    def as_diagnostics(self) -> dict[str, object]:
        return {
            "hook_payload": self.hook_payload.as_payload(),
            "session_state": self.session_state.as_payload(),
            "grounded_intervention": self.grounded_intervention.as_payload(),
            "directive": self.directive.as_payload(),
            "host_response": {
                "decision": self.host_response.decision.value,
                "reason_present": self.host_response.reason is not None,
            },
        }


class OpenAICodexInMemoryStateStore:
    def __init__(self) -> None:
        self._states: dict[str, OpenAICodexSessionState] = {}

    def load(self, session_id: str) -> OpenAICodexSessionState | None:
        return self._states.get(session_id)

    def save(self, state: OpenAICodexSessionState) -> None:
        self._states[state.session_id] = state

    def record_event(self, payload: OpenAICodexHookPayload) -> OpenAICodexSessionState:
        state = _updated_state(self.load(payload.session_id), payload)
        self.save(state)
        return state


class OpenAICodexJsonStateStore:
    """Private file-backed lifecycle state for separate hook processes."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def load(self, session_id: str) -> OpenAICodexSessionState | None:
        path = self._path_for(session_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return OpenAICodexSessionState.from_payload(payload)

    def save(self, state: OpenAICodexSessionState) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path_for(state.session_id)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(state.as_payload(), handle, sort_keys=True, indent=2)
            handle.write("\n")

    def record_event(self, payload: OpenAICodexHookPayload) -> OpenAICodexSessionState:
        state = _updated_state(self.load(payload.session_id), payload)
        self.save(state)
        return state

    def _path_for(self, session_id: str) -> Path:
        digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:32]
        return self.root / f"session-{digest}.json"


def normalize_openai_codex_hook_payload(
    payload: Mapping[str, Any],
) -> OpenAICodexHookPayload:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "normalize_openai_codex_hook_payload payload must be a mapping, "
            f"got {actual_type}."
        )
    event_name = _required_string(payload.get("hook_event_name"), "hook_event_name")
    try:
        hook_event_name = OpenAICodexLifecycleEvent(event_name)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported Codex App/CLI lifecycle event: {event_name}."
        ) from exc
    prompt_text = _first_present_string(
        payload,
        ("prompt", "user_prompt", "message", "input"),
    )
    return OpenAICodexHookPayload(
        session_id=_required_string(payload.get("session_id"), "session_id"),
        turn_id=_optional_string(payload.get("turn_id")),
        hook_event_name=hook_event_name,
        transcript_path=_optional_string(payload.get("transcript_path")),
        cwd=_optional_string(payload.get("cwd")),
        model=_optional_string(payload.get("model")),
        permission_mode=_optional_string(payload.get("permission_mode")),
        stop_hook_active=bool(payload.get("stop_hook_active", False)),
        last_assistant_message=_optional_string(payload.get("last_assistant_message")),
        tool_name=_optional_string(payload.get("tool_name")),
        tool_input=_optional_mapping(payload.get("tool_input"), "tool_input"),
        tool_response=_optional_mapping(payload.get("tool_response"), "tool_response"),
        error=_optional_string(payload.get("error")),
        prompt_text_hash=_hash_text(prompt_text) if prompt_text is not None else None,
        raw_keys=tuple(sorted(str(key) for key in payload.keys())),
    )


def handle_openai_codex_hook_payload(
    payload: Mapping[str, Any],
    *,
    state_store: OpenAICodexInMemoryStateStore | OpenAICodexJsonStateStore,
    runtime_snapshot: OpenAICodexRuntimeSnapshot | None = None,
) -> OpenAICodexHookCoordinatorResult:
    """Coordinate one Codex lifecycle payload through product Cortex law."""

    if not isinstance(
        state_store,
        (OpenAICodexInMemoryStateStore, OpenAICodexJsonStateStore),
    ):
        actual_type = type(state_store).__name__
        raise TypeError(
            "handle_openai_codex_hook_payload.state_store must be an OpenAI Codex "
            f"state store, got {actual_type}."
        )
    hook_payload = normalize_openai_codex_hook_payload(payload)
    state = state_store.record_event(hook_payload)
    intervention = _grounded_intervention_for_event(
        hook_payload,
        runtime_snapshot=runtime_snapshot,
        state=state,
    )
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=intervention,
        lifecycle_facts=hook_payload.lifecycle_facts(),
    )
    return OpenAICodexHookCoordinatorResult(
        hook_payload=hook_payload,
        session_state=state,
        grounded_intervention=intervention,
        directive=directive,
        host_response=_host_response_for_directive(directive),
    )


def _grounded_intervention_for_event(
    hook_payload: OpenAICodexHookPayload,
    *,
    runtime_snapshot: OpenAICodexRuntimeSnapshot | None,
    state: OpenAICodexSessionState,
) -> GroundedInterventionDecision:
    if hook_payload.hook_event_name is not OpenAICodexLifecycleEvent.STOP:
        return GroundedInterventionDecision.stay_silent(
            "non_stop_lifecycle_state_update_only"
        )
    if runtime_snapshot is None:
        return GroundedInterventionDecision.stay_silent("missing_runtime_snapshot")
    warnings = tuple(dict.fromkeys((*runtime_snapshot.warnings, *state.warning_tags)))
    return build_runtime_grounded_intervention(
        resolution_deficit=runtime_snapshot.resolution_deficit,
        debt_control=runtime_snapshot.debt_control,
        operator_route=runtime_snapshot.operator_route,
        expectation_ledger=runtime_snapshot.expectation_ledger,
        current_step=runtime_snapshot.current_step,
        closure_required=runtime_snapshot.closure_required,
        closure_reason_tags=runtime_snapshot.closure_reason_tags,
        warnings=warnings,
    )


def _host_response_for_directive(
    directive: OpenAICodexLifecycleDirective,
) -> OpenAICodexHookHostResponse:
    if (
        directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    ):
        return OpenAICodexHookHostResponse(
            decision=OpenAICodexHookHostDecision.BLOCK,
            reason=directive.model_visible_text,
        )
    return OpenAICodexHookHostResponse()


def _updated_state(
    state: OpenAICodexSessionState | None,
    payload: OpenAICodexHookPayload,
) -> OpenAICodexSessionState:
    prior = state or OpenAICodexSessionState(session_id=payload.session_id)
    lifecycle_counts = _increment_count(
        prior.lifecycle_counts,
        payload.hook_event_name.value,
    )
    warning_tags = prior.warning_tags
    tool_event_count = prior.tool_event_count
    tool_failure_count = prior.tool_failure_count
    stop_event_count = prior.stop_event_count
    current_step = prior.current_step
    if payload.hook_event_name is OpenAICodexLifecycleEvent.USER_PROMPT_SUBMIT:
        current_step += 1
    if payload.hook_event_name in {
        OpenAICodexLifecycleEvent.PRE_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE_FAILURE,
    }:
        tool_event_count += 1
    if payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE_FAILURE:
        tool_failure_count += 1
        warning_tags = tuple(dict.fromkeys((*warning_tags, "tool-failure")))
    if payload.hook_event_name is OpenAICodexLifecycleEvent.STOP:
        stop_event_count += 1
    return replace(
        prior,
        current_step=current_step,
        last_turn_id=payload.turn_id or prior.last_turn_id,
        transcript_path=payload.transcript_path or prior.transcript_path,
        prompt_text_hash=payload.prompt_text_hash or prior.prompt_text_hash,
        prior_assistant_turn_seen=(
            prior.prior_assistant_turn_seen
            or payload.has_transcript_backed_assistant_turn
        ),
        tool_event_count=tool_event_count,
        tool_failure_count=tool_failure_count,
        stop_event_count=stop_event_count,
        warning_tags=warning_tags,
        lifecycle_counts=lifecycle_counts,
    )


def _increment_count(
    counts: tuple[tuple[str, int], ...],
    event_name: str,
) -> tuple[tuple[str, int], ...]:
    mapping = dict(counts)
    mapping[event_name] = mapping.get(event_name, 0) + 1
    return tuple(sorted(mapping.items()))


def _host_text_from_stdout_payload(payload: dict[str, str] | None) -> str:
    return json.dumps(payload) if payload is not None else ""


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _first_present_string(
    payload: Mapping[str, Any],
    keys: tuple[str, ...],
) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _optional_mapping(value: Any, field_name: str) -> Mapping[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be a mapping when present, got {actual_type}.")
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"expected str | None, got {actual_type}.")
    text = value.strip()
    return text or None


def _required_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be a non-empty string, got {actual_type}.")
    return value.strip()


def _optional_int(value: Any, default: int) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or value < 0:
        actual_type = type(value).__name__
        raise TypeError(f"expected non-negative int | None, got {actual_type}.")
    return value


def _require_non_empty_string(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be a non-empty string, got {actual_type}.")


__all__ = [
    "OpenAICodexHookCoordinatorResult",
    "OpenAICodexHookHostDecision",
    "OpenAICodexHookHostResponse",
    "OpenAICodexHookPayload",
    "OpenAICodexInMemoryStateStore",
    "OpenAICodexJsonStateStore",
    "OpenAICodexOperatorRouteView",
    "OpenAICodexRuntimeSnapshot",
    "OpenAICodexSessionState",
    "handle_openai_codex_hook_payload",
    "normalize_openai_codex_hook_payload",
]
