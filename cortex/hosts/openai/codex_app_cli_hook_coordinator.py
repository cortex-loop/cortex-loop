"""Codex App/CLI product hook coordinator.

This module owns the product-side lifecycle bridge for Codex App/CLI hooks. It
normalizes hook payloads, records private per-session state, derives a bounded
runtime snapshot from product-observable lifecycle evidence, consumes existing
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
from cortex.sre.expectations import (
    EvidenceProgress,
    ExpectationLedger,
    ForwardCommitment,
    ResolutionDeficitState,
    open_expectation_from_forward_commitment,
)
from cortex.sre.interventions import (
    GroundedInterventionDecision,
    build_runtime_grounded_intervention,
)
from cortex.sre.operator_routing import OperatorRouteProfile
from cortex.sre.task_standard import (
    TASK_STANDARD_FORMATION_TEXT,
    TaskStandardEvidence,
    TaskStandardEvidenceClass,
    TaskStandardSpine,
    initialize_task_standard_spine,
    record_closure_claims,
    record_task_standard_evidence,
    store_assistant_standard_block,
    task_standard_closure_satisfied,
)

from .codex_app_cli_lifecycle import (
    OpenAICodexLifecycleDirective,
    OpenAICodexLifecycleDirectiveAction,
    OpenAICodexLifecycleEvent,
    OpenAICodexLifecycleFacts,
    build_openai_codex_app_cli_lifecycle_directive,
)
from .posttooluse_task_standard_actuator import (
    posttooluse_task_standard_context_decision,
    tool_event_has_verification_evidence,
    tool_event_looks_failed,
    tool_event_text,
)


class OpenAICodexHookHostDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"


_CODEX_ADDITIONAL_CONTEXT_EVENTS = frozenset(
    {
        "SessionStart",
        "UserPromptSubmit",
        "PostToolUse",
    }
)
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
    tool_use_id: str | None = None
    tool_input: Any = None
    tool_response: Any = None
    error: str | None = None
    prompt_text: str | None = None
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
            "tool_use_id",
            "error",
            "prompt_text",
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
            "tool_use_id": self.tool_use_id,
            "tool_input_present": self.tool_input is not None,
            "tool_response_present": self.tool_response is not None,
            "error_present": self.error is not None,
            "prompt_text_present": self.prompt_text is not None,
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
    expectation_ledger: ExpectationLedger = field(default_factory=ExpectationLedger)
    verification_evidence_count: int = 0
    closure_claim_count: int = 0
    self_repair_response_count: int = 0
    tool_event_count: int = 0
    tool_failure_count: int = 0
    stop_event_count: int = 0
    warning_tags: tuple[str, ...] = ()
    lifecycle_counts: tuple[tuple[str, int], ...] = ()
    task_standard_spine: TaskStandardSpine = field(default_factory=TaskStandardSpine)
    posttooluse_task_standard_context_item_ids: tuple[str, ...] = ()
    last_posttooluse_task_standard_context_item_id: str | None = None
    last_posttooluse_task_standard_context_text: str | None = None
    last_posttooluse_task_standard_context_reason: str | None = None
    last_posttooluse_task_standard_context_silence_reason: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.session_id, "OpenAICodexSessionState.session_id")
        for field_name in (
            "current_step",
            "verification_evidence_count",
            "closure_claim_count",
            "self_repair_response_count",
            "tool_event_count",
            "tool_failure_count",
            "stop_event_count",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"OpenAICodexSessionState.{field_name} must be a non-negative int."
                )
        for field_name in (
            "last_turn_id",
            "transcript_path",
            "prompt_text_hash",
            "last_posttooluse_task_standard_context_item_id",
            "last_posttooluse_task_standard_context_text",
            "last_posttooluse_task_standard_context_reason",
            "last_posttooluse_task_standard_context_silence_reason",
        ):
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
        if not isinstance(self.expectation_ledger, ExpectationLedger):
            actual_type = type(self.expectation_ledger).__name__
            raise TypeError(
                "OpenAICodexSessionState.expectation_ledger must be "
                f"ExpectationLedger, got {actual_type}."
            )
        if not isinstance(self.task_standard_spine, TaskStandardSpine):
            actual_type = type(self.task_standard_spine).__name__
            raise TypeError(
                "OpenAICodexSessionState.task_standard_spine must be "
                f"TaskStandardSpine, got {actual_type}."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.warning_tags):
            raise ValueError(
                "OpenAICodexSessionState.warning_tags must contain non-empty strings."
            )
        if any(
            not (isinstance(item_id, str) and item_id.strip())
            for item_id in self.posttooluse_task_standard_context_item_ids
        ):
            raise ValueError(
                "OpenAICodexSessionState.posttooluse_task_standard_context_item_ids "
                "must contain non-empty strings."
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
            "expectation_ledger": self.expectation_ledger.as_payload(),
            "verification_evidence_count": self.verification_evidence_count,
            "closure_claim_count": self.closure_claim_count,
            "self_repair_response_count": self.self_repair_response_count,
            "tool_event_count": self.tool_event_count,
            "tool_failure_count": self.tool_failure_count,
            "stop_event_count": self.stop_event_count,
            "warning_tags": list(self.warning_tags),
            "lifecycle_counts": [
                {"hook_event_name": event_name, "count": count}
                for event_name, count in self.lifecycle_counts
            ],
            "task_standard_spine": self.task_standard_spine.as_payload(),
            "posttooluse_task_standard_context_item_ids": list(
                self.posttooluse_task_standard_context_item_ids
            ),
            "last_posttooluse_task_standard_context_item_id": (
                self.last_posttooluse_task_standard_context_item_id
            ),
            "last_posttooluse_task_standard_context_text": (
                self.last_posttooluse_task_standard_context_text
            ),
            "last_posttooluse_task_standard_context_reason": (
                self.last_posttooluse_task_standard_context_reason
            ),
            "last_posttooluse_task_standard_context_silence_reason": (
                self.last_posttooluse_task_standard_context_silence_reason
            ),
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
            expectation_ledger=ExpectationLedger.from_payload(
                payload.get("expectation_ledger")
            ),
            verification_evidence_count=_optional_int(
                payload.get("verification_evidence_count"),
                0,
            ),
            closure_claim_count=_optional_int(payload.get("closure_claim_count"), 0),
            self_repair_response_count=_optional_int(
                payload.get("self_repair_response_count"),
                0,
            ),
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
            task_standard_spine=TaskStandardSpine.from_payload(
                payload.get("task_standard_spine")
            ),
            posttooluse_task_standard_context_item_ids=tuple(
                str(item_id).strip()
                for item_id in payload.get(
                    "posttooluse_task_standard_context_item_ids",
                    (),
                )
                if str(item_id).strip()
            ),
            last_posttooluse_task_standard_context_item_id=_optional_string(
                payload.get("last_posttooluse_task_standard_context_item_id")
            ),
            last_posttooluse_task_standard_context_text=_optional_string(
                payload.get("last_posttooluse_task_standard_context_text")
            ),
            last_posttooluse_task_standard_context_reason=_optional_string(
                payload.get("last_posttooluse_task_standard_context_reason")
            ),
            last_posttooluse_task_standard_context_silence_reason=_optional_string(
                payload.get("last_posttooluse_task_standard_context_silence_reason")
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
    context: str | None = None
    context_hook_event_name: str | None = None

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
        if self.context is not None and not (
            isinstance(self.context, str) and self.context.strip()
        ):
            raise ValueError(
                "OpenAICodexHookHostResponse.context must be non-empty when provided."
            )
        if self.decision is OpenAICodexHookHostDecision.BLOCK and self.reason is None:
            raise ValueError("OpenAICodexHookHostResponse.reason is required for block.")
        if self.decision is OpenAICodexHookHostDecision.ALLOW and self.reason is not None:
            raise ValueError("OpenAICodexHookHostResponse.reason is only valid for block.")
        if self.decision is OpenAICodexHookHostDecision.BLOCK and self.context is not None:
            raise ValueError("OpenAICodexHookHostResponse.context is only valid for allow.")
        if self.context_hook_event_name is not None and not (
            isinstance(self.context_hook_event_name, str)
            and self.context_hook_event_name.strip()
        ):
            raise ValueError(
                "OpenAICodexHookHostResponse.context_hook_event_name must be non-empty "
                "when provided."
            )
        if self.context is None and self.context_hook_event_name is not None:
            raise ValueError(
                "OpenAICodexHookHostResponse.context_hook_event_name requires context."
            )
        if self.context is not None:
            if self.context_hook_event_name is None:
                raise ValueError(
                    "OpenAICodexHookHostResponse.context requires context_hook_event_name."
                )
            if self.context_hook_event_name not in _CODEX_ADDITIONAL_CONTEXT_EVENTS:
                raise ValueError(
                    "OpenAICodexHookHostResponse.context_hook_event_name does not "
                    "support additionalContext in Codex."
                )

    @property
    def stdout_payload(self) -> dict[str, object] | None:
        if self.decision is OpenAICodexHookHostDecision.BLOCK:
            return {"decision": "block", "reason": self.reason or ""}
        if self.context is not None:
            return {
                "hookSpecificOutput": {
                    "hookEventName": self.context_hook_event_name or "",
                    "additionalContext": self.context,
                }
            }
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
                "context_present": self.host_response.context is not None,
                "context_hook_event_name": self.host_response.context_hook_event_name,
            },
        }


class OpenAICodexInMemoryStateStore:
    def __init__(self) -> None:
        self._states: dict[str, OpenAICodexSessionState] = {}

    def load(self, session_id: str) -> OpenAICodexSessionState | None:
        return self._states.get(session_id)

    def save(self, state: OpenAICodexSessionState) -> None:
        self._states[state.session_id] = state

    def record_event(
        self,
        payload: OpenAICodexHookPayload,
        *,
        posttooluse_task_standard_context_enabled: bool = False,
    ) -> OpenAICodexSessionState:
        state = _updated_state(
            self.load(payload.session_id),
            payload,
            posttooluse_task_standard_context_enabled=(
                posttooluse_task_standard_context_enabled
            ),
        )
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

    def record_event(
        self,
        payload: OpenAICodexHookPayload,
        *,
        posttooluse_task_standard_context_enabled: bool = False,
    ) -> OpenAICodexSessionState:
        state = _updated_state(
            self.load(payload.session_id),
            payload,
            posttooluse_task_standard_context_enabled=(
                posttooluse_task_standard_context_enabled
            ),
        )
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
        tool_use_id=_optional_string(payload.get("tool_use_id")),
        tool_input=_optional_json_value(payload.get("tool_input")),
        tool_response=_optional_json_value(payload.get("tool_response")),
        error=_optional_string(payload.get("error")),
        prompt_text_hash=_hash_text(prompt_text) if prompt_text is not None else None,
        prompt_text=prompt_text,
        raw_keys=tuple(sorted(str(key) for key in payload.keys())),
    )


def handle_openai_codex_hook_payload(
    payload: Mapping[str, Any],
    *,
    state_store: OpenAICodexInMemoryStateStore | OpenAICodexJsonStateStore,
    runtime_snapshot: OpenAICodexRuntimeSnapshot | None = None,
    task_standard_text_enabled: bool = False,
    posttooluse_task_standard_context_enabled: bool = False,
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
    if not isinstance(task_standard_text_enabled, bool):
        actual_type = type(task_standard_text_enabled).__name__
        raise TypeError(
            "handle_openai_codex_hook_payload.task_standard_text_enabled must be "
            f"bool, got {actual_type}."
        )
    if not isinstance(posttooluse_task_standard_context_enabled, bool):
        actual_type = type(posttooluse_task_standard_context_enabled).__name__
        raise TypeError(
            "handle_openai_codex_hook_payload."
            "posttooluse_task_standard_context_enabled must be bool, "
            f"got {actual_type}."
        )
    hook_payload = normalize_openai_codex_hook_payload(payload)
    state = state_store.record_event(
        hook_payload,
        posttooluse_task_standard_context_enabled=(
            posttooluse_task_standard_context_enabled
        ),
    )
    intervention = _grounded_intervention_for_event(
        hook_payload,
        runtime_snapshot=runtime_snapshot,
        state=state,
    )
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=intervention,
        lifecycle_facts=hook_payload.lifecycle_facts(),
    )
    directive = _accountable_continuation_directive(
        directive,
        hook_payload=hook_payload,
        state=state,
    )
    directive = _posttooluse_task_standard_context_directive(
        directive,
        hook_payload=hook_payload,
        state=state,
    )
    return OpenAICodexHookCoordinatorResult(
        hook_payload=hook_payload,
        session_state=state,
        grounded_intervention=intervention,
        directive=directive,
        host_response=_host_response_for_directive(
            directive,
            hook_payload=hook_payload,
            task_standard_text_enabled=task_standard_text_enabled,
        ),
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
        if _state_has_no_product_perception(state):
            return GroundedInterventionDecision.stay_silent(
                "missing_product_perception_state"
            )
        runtime_snapshot = _runtime_snapshot_from_session_state(state)
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
    *,
    hook_payload: OpenAICodexHookPayload,
    task_standard_text_enabled: bool,
) -> OpenAICodexHookHostResponse:
    if (
        directive.action
        is OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT
    ):
        return OpenAICodexHookHostResponse(
            context=directive.model_visible_text,
            context_hook_event_name=hook_payload.hook_event_name.value,
        )
    if (
        directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    ):
        return OpenAICodexHookHostResponse(
            decision=OpenAICodexHookHostDecision.BLOCK,
            reason=directive.model_visible_text,
        )
    if (
        task_standard_text_enabled
        and hook_payload.hook_event_name is OpenAICodexLifecycleEvent.USER_PROMPT_SUBMIT
    ):
        return OpenAICodexHookHostResponse(
            context=TASK_STANDARD_FORMATION_TEXT,
            context_hook_event_name=hook_payload.hook_event_name.value,
        )
    return OpenAICodexHookHostResponse()


def _updated_state(
    state: OpenAICodexSessionState | None,
    payload: OpenAICodexHookPayload,
    *,
    posttooluse_task_standard_context_enabled: bool = False,
) -> OpenAICodexSessionState:
    prior = state or OpenAICodexSessionState(session_id=payload.session_id)
    lifecycle_counts = _increment_count(
        prior.lifecycle_counts,
        payload.hook_event_name.value,
    )
    warning_tags = prior.warning_tags
    expectation_ledger = prior.expectation_ledger
    task_standard_spine = prior.task_standard_spine
    verification_evidence_count = prior.verification_evidence_count
    closure_claim_count = prior.closure_claim_count
    self_repair_response_count = prior.self_repair_response_count
    tool_event_count = prior.tool_event_count
    tool_failure_count = prior.tool_failure_count
    stop_event_count = prior.stop_event_count
    current_step = prior.current_step
    posttooluse_context_item_ids = prior.posttooluse_task_standard_context_item_ids
    last_posttooluse_context_item_id: str | None = None
    last_posttooluse_context_text: str | None = None
    last_posttooluse_context_reason: str | None = None
    last_posttooluse_context_silence_reason: str | None = None
    task_standard_evidence: TaskStandardEvidence | None = None
    if payload.hook_event_name is OpenAICodexLifecycleEvent.USER_PROMPT_SUBMIT:
        current_step += 1
        expectation_ledger = ExpectationLedger()
        verification_evidence_count = 0
        closure_claim_count = 0
        self_repair_response_count = 0
        warning_tags = ()
        posttooluse_context_item_ids = ()
        task_standard_spine = initialize_task_standard_spine(
            payload.prompt_text,
            event_ref=_event_ref(
                payload,
                current_step=current_step,
                suffix="user-prompt-standard",
            ),
        )
    if payload.hook_event_name in {
        OpenAICodexLifecycleEvent.PRE_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE_FAILURE,
    }:
        task_standard_spine = _capture_pretool_transcript_standard(
            task_standard_spine,
            payload,
            current_step=current_step,
        )
        tool_event_count += 1
    if (
        payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE
        and tool_event_has_verification_evidence(
            payload,
            active_verification_expectation=_has_active_expectation_kind(
                expectation_ledger,
                "verification",
            ),
        )
    ):
        tool_event_ref = _event_ref(payload, current_step=current_step, suffix="tool-check")
        task_standard_spine, task_standard_evidence = record_task_standard_evidence(
            task_standard_spine,
            event_ref=tool_event_ref,
            tool_text=tool_event_text(payload),
            successful=not tool_event_looks_failed(
                payload,
                tool_event_text(payload).lower(),
            ),
        )
        standard_gated = task_standard_spine.has_standard
        aligned_to_standard = task_standard_evidence.evidence_class in {
            TaskStandardEvidenceClass.CLAIM_ALIGNED,
            TaskStandardEvidenceClass.STANDARD_ALIGNED,
        }
        if not standard_gated or aligned_to_standard:
            verification_evidence_count += 1
        should_pay_down = bool(
            not standard_gated or aligned_to_standard
        )
        commitment_id = _active_expectation_commitment_id(
            expectation_ledger,
            "verification",
        )
        if should_pay_down:
            expectation_ledger = expectation_ledger.apply_progress(
                EvidenceProgress(
                    "meaningful_evidence",
                    tool_event_ref,
                    weight=1.0,
                    commitment_id=commitment_id,
                ),
                current_step=current_step,
            )
    elif payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE:
        tool_event_ref = _event_ref(payload, current_step=current_step, suffix="tool-event")
        task_standard_spine, task_standard_evidence = record_task_standard_evidence(
            task_standard_spine,
            event_ref=tool_event_ref,
            tool_text=tool_event_text(payload),
            successful=not tool_event_looks_failed(
                payload,
                tool_event_text(payload).lower(),
            ),
        )
    if (
        posttooluse_task_standard_context_enabled
        and payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE
    ):
        if task_standard_evidence is None:
            last_posttooluse_context_silence_reason = "no_task_standard_evidence"
        else:
            posttooluse_context = posttooluse_task_standard_context_decision(
                task_standard_spine,
                evidence=task_standard_evidence,
                payload=payload,
                already_context_item_ids=posttooluse_context_item_ids,
            )
            last_posttooluse_context_silence_reason = posttooluse_context.reason
        if (
            task_standard_evidence is not None
            and posttooluse_context.context_text is not None
            and posttooluse_context.item_id is not None
        ):
            (
                last_posttooluse_context_item_id,
                last_posttooluse_context_text,
                last_posttooluse_context_reason,
            ) = (
                posttooluse_context.item_id,
                posttooluse_context.context_text,
                posttooluse_context.reason,
            )
            last_posttooluse_context_silence_reason = None
            posttooluse_context_item_ids = tuple(
                dict.fromkeys(
                    (
                        *posttooluse_context_item_ids,
                        last_posttooluse_context_item_id,
                    )
                )
            )
    if payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE_FAILURE:
        tool_failure_count += 1
        warning_tags = tuple(dict.fromkeys((*warning_tags, "tool-failure")))
    if payload.hook_event_name is OpenAICodexLifecycleEvent.STOP:
        stop_event_count += 1
        if payload.has_transcript_backed_assistant_turn:
            message = payload.last_assistant_message or ""
            standard_before_closure = task_standard_spine
            task_standard_spine = store_assistant_standard_block(
                task_standard_spine,
                message,
                event_ref=_event_ref(
                    payload,
                    current_step=current_step,
                    suffix="assistant-standard",
                ),
            )
            if _assistant_surfaces_blocker_or_waiting(message):
                self_repair_response_count += 1
                expectation_ledger = expectation_ledger.apply_progress(
                    EvidenceProgress(
                        "blocker_surfaced",
                        _event_ref(
                            payload,
                            current_step=current_step,
                            suffix="assistant-blocker",
                        ),
                        weight=1.0,
                    ),
                    current_step=current_step,
                )
            elif _assistant_narrows_or_retracts(message):
                self_repair_response_count += 1
                expectation_ledger = expectation_ledger.apply_progress(
                    EvidenceProgress(
                        "liability_retracted",
                        _event_ref(
                            payload,
                            current_step=current_step,
                            suffix="assistant-narrowed",
                        ),
                        weight=1.0,
                    ),
                    current_step=current_step,
                )
            elif _assistant_claims_closure(message) and _can_open_stop_verification(
                prior,
                payload,
                expectation_ledger=expectation_ledger,
            ):
                task_standard_spine = record_closure_claims(
                    task_standard_spine,
                    message,
                    event_ref=_event_ref(
                        payload,
                        current_step=current_step,
                        suffix="assistant-closure-standard",
                    ),
                )
                if (
                    task_standard_spine.has_standard
                    and not task_standard_spine.has_unmatched_closure_items
                    and not standard_before_closure.has_standard
                ):
                    task_standard_spine = replace(
                        task_standard_spine,
                        unmatched_standard_item_ids=tuple(
                            item.item_id for item in task_standard_spine.standard_items
                        ),
                    )
                closure_claim_count += 1
                commitment = ForwardCommitment(
                    commitment_id=_event_ref(
                        payload,
                        current_step=current_step,
                        suffix="assistant-verification-claim",
                    ),
                    source_event_ref=_event_ref(
                        payload,
                        current_step=current_step,
                        suffix="assistant-stop",
                    ),
                    claim_span_ref=_event_ref(
                        payload,
                        current_step=current_step,
                        suffix="closure-claim",
                    ),
                    commitment_kind="verification",
                    assertiveness="high",
                    scope="task",
                    opened_at_step=current_step,
                )
                expectation_ledger = open_expectation_from_forward_commitment(
                    expectation_ledger,
                    commitment,
                )
                if (
                    (
                        verification_evidence_count > 0
                        or task_standard_closure_satisfied(task_standard_spine)
                    )
                    and not task_standard_spine.has_unmatched_closure_items
                ):
                    expectation_ledger = expectation_ledger.apply_progress(
                        EvidenceProgress(
                            "meaningful_evidence",
                            _event_ref(
                                payload,
                                current_step=current_step,
                                suffix="observed-check",
                            ),
                            weight=1.0,
                            commitment_id=commitment.commitment_id,
                        ),
                        current_step=current_step,
                    )
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
        expectation_ledger=expectation_ledger,
        verification_evidence_count=verification_evidence_count,
        closure_claim_count=closure_claim_count,
        self_repair_response_count=self_repair_response_count,
        tool_event_count=tool_event_count,
        tool_failure_count=tool_failure_count,
        stop_event_count=stop_event_count,
        warning_tags=warning_tags,
        lifecycle_counts=lifecycle_counts,
        task_standard_spine=task_standard_spine,
        posttooluse_task_standard_context_item_ids=posttooluse_context_item_ids,
        last_posttooluse_task_standard_context_item_id=last_posttooluse_context_item_id,
        last_posttooluse_task_standard_context_text=last_posttooluse_context_text,
        last_posttooluse_task_standard_context_reason=last_posttooluse_context_reason,
        last_posttooluse_task_standard_context_silence_reason=(
            last_posttooluse_context_silence_reason
        ),
    )


def _increment_count(
    counts: tuple[tuple[str, int], ...],
    event_name: str,
) -> tuple[tuple[str, int], ...]:
    mapping = dict(counts)
    mapping[event_name] = mapping.get(event_name, 0) + 1
    return tuple(sorted(mapping.items()))


def _capture_pretool_transcript_standard(
    spine: TaskStandardSpine,
    payload: OpenAICodexHookPayload,
    *,
    current_step: int,
) -> TaskStandardSpine:
    if spine.standard_items or payload.hook_event_name not in {
        OpenAICodexLifecycleEvent.PRE_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE,
    }:
        return spine
    for message in _pretool_assistant_messages_from_transcript(payload.transcript_path):
        updated = store_assistant_standard_block(
            spine,
            message,
            event_ref=_event_ref(
                payload,
                current_step=current_step,
                suffix="pretool-transcript-standard",
            ),
        )
        if updated.standard_items or (
            updated.malformed_standard_block_count != spine.malformed_standard_block_count
        ):
            return updated
    return spine


def _pretool_assistant_messages_from_transcript(
    transcript_path: str | None,
) -> tuple[str, ...]:
    if not isinstance(transcript_path, str) or not transcript_path.strip():
        return ()
    path = Path(transcript_path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    messages: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return ()
        if not isinstance(row, Mapping):
            continue
        payload = row.get("payload")
        if not isinstance(payload, Mapping):
            continue
        if _transcript_row_is_tool_boundary(row_type=row.get("type"), payload=payload):
            break
        message = _assistant_text_from_transcript_row(
            row_type=row.get("type"),
            payload=payload,
        )
        if message:
            messages.append(message)
    return tuple(messages)


def _transcript_row_is_tool_boundary(
    *,
    row_type: Any,
    payload: Mapping[str, Any],
) -> bool:
    payload_type = payload.get("type")
    if row_type == "response_item" and payload_type in {
        "function_call",
        "function_call_output",
        "tool_call",
        "tool_result",
    }:
        return True
    if row_type == "event_msg" and payload_type in {
        "tool_call",
        "tool_result",
        "tool_started",
        "tool_completed",
    }:
        return True
    return False


def _assistant_text_from_transcript_row(
    *,
    row_type: Any,
    payload: Mapping[str, Any],
) -> str | None:
    if row_type == "event_msg" and payload.get("type") == "agent_message":
        message = payload.get("message")
        return message.strip() if isinstance(message, str) and message.strip() else None
    if row_type != "response_item" or payload.get("type") != "message":
        return None
    if payload.get("role") != "assistant":
        return None
    content = payload.get("content")
    if not isinstance(content, list):
        return None
    parts: list[str] = []
    for item in content:
        if not isinstance(item, Mapping):
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
    combined = "\n".join(parts).strip()
    return combined or None


def _runtime_snapshot_from_session_state(
    state: OpenAICodexSessionState,
) -> OpenAICodexRuntimeSnapshot:
    resolution_deficit = state.expectation_ledger.resolution_deficit(
        current_step=state.current_step
    )
    pressure = float(resolution_deficit.negative_prediction_error)
    reason_tags: set[str] = {"product-perception"}
    if pressure > 0.0:
        reason_tags.add("resolution-deficit")
    if resolution_deficit.dominant_deficit_kind:
        reason_tags.add(f"deficit:{resolution_deficit.dominant_deficit_kind}")
    if resolution_deficit.overdue_weight > 0.0:
        reason_tags.add("overdue-expectation")
    closure_required = bool(
        resolution_deficit.due_weight > 0.0 or resolution_deficit.overdue_weight > 0.0
    )
    return OpenAICodexRuntimeSnapshot(
        expectation_ledger=state.expectation_ledger,
        resolution_deficit=resolution_deficit,
        debt_control=DebtControlPressure(
            resolution_pressure=pressure,
            persistence=pressure,
            debt_pressure=pressure,
            reason_tags=frozenset(reason_tags),
        ),
        current_step=state.current_step,
        closure_required=closure_required,
        closure_reason_tags=("product-perceived-closure-pressure",)
        if closure_required
        else (),
        warnings=state.warning_tags,
    )


def _state_has_no_product_perception(state: OpenAICodexSessionState) -> bool:
    return bool(
        state.prompt_text_hash is None
        and not state.expectation_ledger.active
        and not state.expectation_ledger.resolved
        and state.tool_event_count == 0
        and state.tool_failure_count == 0
        and not state.warning_tags
    )


def _can_open_stop_verification(
    prior: OpenAICodexSessionState,
    payload: OpenAICodexHookPayload,
    *,
    expectation_ledger: ExpectationLedger,
) -> bool:
    return bool(
        prior.prompt_text_hash
        and not payload.stop_hook_active
        and not _has_active_expectation_kind(expectation_ledger, "verification")
    )


def _has_active_expectation_kind(
    expectation_ledger: ExpectationLedger,
    deficit_kind: str,
) -> bool:
    return any(
        record.deficit_kind == deficit_kind and record.remaining_weight > 0.0
        for record in expectation_ledger.active
    )


def _active_expectation_commitment_id(
    expectation_ledger: ExpectationLedger,
    deficit_kind: str,
) -> str | None:
    for record in expectation_ledger.active:
        if record.deficit_kind == deficit_kind and record.remaining_weight > 0.0:
            return record.commitment_id
    return None


def _has_resolved_expectation_kind(
    expectation_ledger: ExpectationLedger,
    deficit_kind: str,
) -> bool:
    return any(record.deficit_kind == deficit_kind for record in expectation_ledger.resolved)


def _accountable_continuation_directive(
    directive: OpenAICodexLifecycleDirective,
    *,
    hook_payload: OpenAICodexHookPayload,
    state: OpenAICodexSessionState,
) -> OpenAICodexLifecycleDirective:
    if (
        hook_payload.hook_event_name is not OpenAICodexLifecycleEvent.STOP
        or not hook_payload.stop_hook_active
        or directive.silence_reason != "stop_hook_active"
    ):
        return directive
    if _has_active_expectation_kind(state.expectation_ledger, "verification"):
        reason = "stop_hook_active_unresolved_verification_expectation"
    elif _has_resolved_expectation_kind(state.expectation_ledger, "verification"):
        reason = "pressure_below_visible_threshold"
    else:
        reason = "stop_hook_active"
    return OpenAICodexLifecycleDirective(
        action=directive.action,
        hook_event_name=directive.hook_event_name,
        model_visible_text=directive.model_visible_text,
        silence_reason=reason,
        model_bound_difference_kind=directive.model_bound_difference_kind,
    )


def _posttooluse_task_standard_context_directive(
    directive: OpenAICodexLifecycleDirective,
    *,
    hook_payload: OpenAICodexHookPayload,
    state: OpenAICodexSessionState,
) -> OpenAICodexLifecycleDirective:
    if (
        hook_payload.hook_event_name is not OpenAICodexLifecycleEvent.POST_TOOL_USE
        or directive.action is not OpenAICodexLifecycleDirectiveAction.ALLOW
        or not state.last_posttooluse_task_standard_context_text
    ):
        return directive
    return OpenAICodexLifecycleDirective(
        action=OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT,
        hook_event_name=hook_payload.hook_event_name.value,
        model_visible_text=state.last_posttooluse_task_standard_context_text,
        silence_reason=None,
        model_bound_difference_kind="posttooluse_task_standard_next_step_context",
    )


def _assistant_surfaces_blocker_or_waiting(message: str) -> bool:
    lowered = message.lower()
    return any(
        marker in lowered
        for marker in (
            "blocked",
            "waiting on",
            "need more information",
            "need input",
            "please provide",
            "can't proceed",
            "cannot proceed",
            "missing information",
            "missing context",
            "approval",
        )
    )


def _assistant_narrows_or_retracts(message: str) -> bool:
    lowered = message.lower()
    return any(
        marker in lowered
        for marker in (
            "not complete",
            "not done",
            "not verified",
            "unverified",
            "can't call this done",
            "cannot call this done",
            "leave it open",
            "still remains",
            "still need",
            "remaining work",
            "narrow",
            "retract",
        )
    )


def _assistant_claims_closure(message: str) -> bool:
    lowered = message.lower()
    return any(
        marker in lowered
        for marker in (
            "done",
            "complete",
            "completed",
            "finished",
            "implemented",
            "created",
            "fixed",
            "resolved",
            "ready",
        )
    )


def _event_ref(
    payload: OpenAICodexHookPayload,
    *,
    current_step: int,
    suffix: str,
) -> str:
    turn = payload.turn_id or "turn"
    digest = hashlib.sha256(
        f"{payload.session_id}:{turn}:{payload.hook_event_name.value}:{suffix}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return f"codex-app-cli:{current_step}:{payload.hook_event_name.value}:{suffix}:{digest}"


def _host_text_from_stdout_payload(payload: dict[str, object] | None) -> str:
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


def _optional_json_value(value: Any) -> Any:
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
