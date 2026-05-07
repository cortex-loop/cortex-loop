"""PostToolUse task-standard actuator for the Codex App/CLI host."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from cortex.sre.task_standard import (
    TaskStandardEvidence,
    TaskStandardEvidenceClass,
    TaskStandardItem,
    TaskStandardItemKind,
    TaskStandardSpine,
    external_scoring_boundary_terms,
    task_standard_closure_satisfied,
)

from .codex_app_cli_lifecycle import OpenAICodexLifecycleEvent


_POSTTOOLUSE_TASK_STANDARD_CONTEXT_TEMPLATE = (
    "I still need direct evidence for: {standard_item}. The last tool "
    "result did not show that exact item. Next step: {next_step} before treating "
    "this as done."
)
_POSTTOOLUSE_TASK_STANDARD_CONTEXT_SPAN_LIMIT = 180
_POSTTOOLUSE_TASK_STANDARD_CONTEXT_SESSION_LIMIT = 2
_POSTTOOLUSE_MISSING_ARTIFACT_MARKERS = (
    "no such file or directory",
    "cannot stat",
    "does not exist",
    "open: no such file",
    "open: no such file or directory",
    "no such file",
)
_POSTTOOLUSE_PHASE_FAILED_OPTION_RE = re.compile(
    r"(^|\n)\s*[^\n]{0,160}\b(?:illegal|invalid|unrecognized|unknown) option\b",
)
_POSTTOOLUSE_PHASE_FAILED_USAGE_RE = re.compile(r"(^|\n)\s*usage:\s+\S+")
_TOOL_VERIFICATION_MARKERS = (
    " test",
    "tests",
    "pytest",
    "unittest",
    "vitest",
    "jest",
    "build",
    "lint",
    "typecheck",
    "tsc",
    "mypy",
    "ruff",
    "cargo test",
    "go test",
    "check",
    "verify",
    "cat ",
    "$(cat",
    "\\\"cat",
    " wc ",
    "wc -l",
    "\\\"wc",
    "grep",
    "stat ",
    "\\\"stat",
    "[ -f",
    "test -f",
    "file_ok",
    "content_ok",
    "content=",
    "lines=",
    "exists",
    "matches exactly",
)


class _CodexToolPayload(Protocol):
    hook_event_name: OpenAICodexLifecycleEvent
    tool_name: str | None
    tool_input: Any
    tool_response: Any
    error: str | None


class PostToolUseTaskStandardPhase(str, Enum):
    NO_TOOL_EVENT_TEXT = "no_tool_event_text"
    PRE_ARTIFACT_MISSING = "pre_artifact_missing"
    FAILED_CHECK = "failed_check"
    FAILED_TOOL = "failed_tool"
    CANDIDATE_ARTIFACT_CREATED = "candidate_artifact_created"
    READBACK_COMPLETED = "readback_completed"
    MARKERLESS = "markerless"
    UNRELATED_OR_GENERIC = "unrelated_or_generic"


@dataclass(frozen=True, slots=True)
class PostToolUseTaskStandardPhaseResult:
    phase: PostToolUseTaskStandardPhase
    tool_text: str
    has_verification_marker: bool = False
    candidate_artifact_created: bool = False

    @property
    def silence_reason(self) -> str:
        if self.phase is PostToolUseTaskStandardPhase.NO_TOOL_EVENT_TEXT:
            return "no_tool_event_text"
        if self.phase is PostToolUseTaskStandardPhase.PRE_ARTIFACT_MISSING:
            return "pre_artifact_candidate_missing"
        if self.phase is PostToolUseTaskStandardPhase.FAILED_CHECK:
            return "phase_check_failed"
        if self.phase is PostToolUseTaskStandardPhase.FAILED_TOOL:
            return "tool_event_failed"
        if self.phase is PostToolUseTaskStandardPhase.MARKERLESS:
            return "no_verification_marker"
        return "no_candidate_artifact_or_readback"

    @property
    def context_eligible(self) -> bool:
        return self.phase in {
            PostToolUseTaskStandardPhase.CANDIDATE_ARTIFACT_CREATED,
            PostToolUseTaskStandardPhase.READBACK_COMPLETED,
        }


@dataclass(frozen=True, slots=True)
class PostToolUseTaskStandardContextDecision:
    item_id: str | None
    context_text: str | None
    reason: str
    phase: PostToolUseTaskStandardPhase | None = None


def posttooluse_task_standard_context_decision(
    spine: TaskStandardSpine,
    *,
    evidence: TaskStandardEvidence,
    payload: _CodexToolPayload,
    already_context_item_ids: tuple[str, ...],
) -> PostToolUseTaskStandardContextDecision:
    if not spine.has_standard:
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="no_model_derived_standard",
        )
    if task_standard_closure_satisfied(spine):
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="task_standard_closure_satisfied",
        )
    if evidence.evidence_class not in {
        TaskStandardEvidenceClass.CLAIM_ALIGNED,
        TaskStandardEvidenceClass.STANDARD_ALIGNED,
    }:
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="evidence_not_standard_aligned",
        )
    if (
        len(already_context_item_ids)
        >= _POSTTOOLUSE_TASK_STANDARD_CONTEXT_SESSION_LIMIT
    ):
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="posttooluse_context_session_cap_reached",
        )
    phase = classify_posttooluse_task_standard_phase(spine, payload)
    if not phase.context_eligible:
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason=phase.silence_reason,
            phase=phase.phase,
        )
    item = _first_unresolved_required_standard_item(
        spine,
        already_context_item_ids=already_context_item_ids,
    )
    if (
        item is None
        and phase.phase is PostToolUseTaskStandardPhase.CANDIDATE_ARTIFACT_CREATED
        and not phase.has_verification_marker
    ):
        item = _first_required_standard_item_by_kind(
            spine,
            kind=TaskStandardItemKind.CLOSURE_EVIDENCE,
            already_context_item_ids=already_context_item_ids,
        )
    if item is None:
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="no_unresolved_required_item",
            phase=phase.phase,
        )
    context_text = render_posttooluse_task_standard_context(spine, item)
    return PostToolUseTaskStandardContextDecision(
        item_id=item.item_id,
        context_text=context_text,
        reason="unresolved_task_standard_item_after_tool",
        phase=phase.phase,
    )


def classify_posttooluse_task_standard_phase(
    spine: TaskStandardSpine,
    payload: _CodexToolPayload,
) -> PostToolUseTaskStandardPhaseResult:
    tool_text = tool_event_text(payload).lower()
    if not tool_text:
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.NO_TOOL_EVENT_TEXT,
            tool_text=tool_text,
        )
    has_verification_marker = tool_event_has_verification_marker(tool_text)
    phase_completed = posttooluse_phase_tool_response_completed(payload, tool_text)
    candidate_artifact_created = (
        phase_completed and _posttooluse_candidate_artifact_created(spine, tool_text)
    )
    if not has_verification_marker and not candidate_artifact_created:
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.MARKERLESS,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=candidate_artifact_created,
        )
    if has_verification_marker and _posttooluse_missing_candidate_artifact(tool_text):
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.PRE_ARTIFACT_MISSING,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=candidate_artifact_created,
        )
    if _posttooluse_phase_check_failed(tool_text):
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.FAILED_CHECK,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=candidate_artifact_created,
        )
    if tool_event_looks_failed(payload, tool_text):
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.FAILED_TOOL,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=candidate_artifact_created,
        )
    if candidate_artifact_created:
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.CANDIDATE_ARTIFACT_CREATED,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=True,
        )
    if has_verification_marker and phase_completed:
        return PostToolUseTaskStandardPhaseResult(
            phase=PostToolUseTaskStandardPhase.READBACK_COMPLETED,
            tool_text=tool_text,
            has_verification_marker=has_verification_marker,
            candidate_artifact_created=False,
        )
    return PostToolUseTaskStandardPhaseResult(
        phase=PostToolUseTaskStandardPhase.UNRELATED_OR_GENERIC,
        tool_text=tool_text,
        has_verification_marker=has_verification_marker,
        candidate_artifact_created=False,
    )


def tool_event_has_verification_evidence(
    payload: _CodexToolPayload,
    *,
    active_verification_expectation: bool = False,
) -> bool:
    text = tool_event_text(payload).lower()
    if not text:
        return False
    if not tool_event_has_verification_marker(text):
        return False
    if tool_event_looks_failed(payload, text):
        return False
    return active_verification_expectation or tool_event_looks_successful(payload, text)


def tool_event_has_verification_marker(normalized_tool_text: str) -> bool:
    return any(marker in normalized_tool_text for marker in _TOOL_VERIFICATION_MARKERS)


def tool_event_text(payload: _CodexToolPayload) -> str:
    return " ".join(
        value
        for value in (
            payload.tool_name or "",
            _json_value_text(payload.tool_input),
            _json_value_text(payload.tool_response),
        )
        if value
    )


def tool_event_looks_successful(payload: _CodexToolPayload, text: str) -> bool:
    if payload.hook_event_name is not OpenAICodexLifecycleEvent.POST_TOOL_USE:
        return False
    if "\"exit_code\":0" in text or "\"exit_code\": 0" in text:
        return True
    if "\"status\":\"completed\"" in text or "\"status\": \"completed\"" in text:
        return True
    return any(
        marker in text
        for marker in (
            "file_ok",
            "content_ok",
            " passed",
            "success",
            "ok",
            "matches exactly",
        )
    )


def tool_event_looks_failed(payload: _CodexToolPayload, text: str) -> bool:
    if payload.error:
        return True
    return any(
        marker in text
        for marker in (
            "\"exit_code\":1",
            "\"exit_code\": 1",
            "\"exit_code\":2",
            "\"exit_code\": 2",
            "failed",
            "failure",
            "traceback",
            "error:",
            "content_mismatch",
            "not found",
        )
    )


def posttooluse_phase_tool_response_completed(
    payload: _CodexToolPayload,
    tool_text: str,
) -> bool:
    if tool_event_looks_failed(payload, tool_text):
        return False
    if _posttooluse_missing_candidate_artifact(tool_text):
        return False
    if _posttooluse_phase_check_failed(tool_text):
        return False
    return tool_event_looks_successful(
        payload,
        tool_text,
    ) or (
        payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE
        and payload.tool_response is not None
    )


def render_posttooluse_task_standard_context(
    spine: TaskStandardSpine,
    item: TaskStandardItem,
) -> str:
    closure_evidence = next(
        (
            standard_item.text
            for standard_item in spine.standard_items
            if standard_item.kind is TaskStandardItemKind.CLOSURE_EVIDENCE
        ),
        "",
    )
    next_step = (
        posttooluse_context_span(closure_evidence)
        if closure_evidence
        else "a direct check for that item"
    )
    return _POSTTOOLUSE_TASK_STANDARD_CONTEXT_TEMPLATE.format(
        standard_item=posttooluse_context_span(item.text),
        next_step=next_step,
    )


def posttooluse_context_span(text: str) -> str:
    compacted = re.sub(r"\s+", " ", str(text)).strip()
    compacted = re.sub(r"\bCortex\b", "this work", compacted)
    for term in external_scoring_boundary_terms():
        compacted = re.sub(re.escape(term), "", compacted, flags=re.IGNORECASE)
    compacted = re.sub(r"\s+", " ", compacted).strip(" .;:")
    if len(compacted) <= _POSTTOOLUSE_TASK_STANDARD_CONTEXT_SPAN_LIMIT:
        return compacted or "a direct check for that item"
    shortened = compacted[: _POSTTOOLUSE_TASK_STANDARD_CONTEXT_SPAN_LIMIT].rsplit(
        " ", 1
    )[0]
    anchors = tuple(
        anchor
        for anchor in posttooluse_product_anchors(compacted)
        if anchor not in shortened
    )
    if anchors:
        anchor_text = " ".join(anchors[:3])
        if len(anchor_text) > 80:
            anchor_text = anchor_text[:80].rsplit(" ", 1)[0].strip()
        prefix_room = (
            _POSTTOOLUSE_TASK_STANDARD_CONTEXT_SPAN_LIMIT - len(anchor_text) - 5
        )
        if prefix_room >= 40:
            shortened = compacted[:prefix_room].rsplit(" ", 1)[0]
            return f"{shortened.strip()}... {anchor_text}".strip()
    return f"{shortened.strip()}..."


def posttooluse_product_anchors(text: str) -> tuple[str, ...]:
    quoted = re.findall(r"`[^`]+`|\"[^\"]+\"|'[^']+'", text)
    paths = re.findall(r"[A-Za-z0-9_./-]+\.[A-Za-z0-9_./-]+", text)
    numeric = re.findall(r"[A-Za-z0-9_./-]*\d[A-Za-z0-9_./-]*", text)
    anchors = (*quoted, *paths, *numeric)
    return tuple(dict.fromkeys(anchor.strip() for anchor in anchors if anchor.strip()))


def _posttooluse_missing_candidate_artifact(tool_text: str) -> bool:
    return any(marker in tool_text for marker in _POSTTOOLUSE_MISSING_ARTIFACT_MARKERS)


def _posttooluse_phase_check_failed(tool_text: str) -> bool:
    diagnostic_text = tool_text.replace("\\n", "\n")
    return bool(
        _POSTTOOLUSE_PHASE_FAILED_OPTION_RE.search(diagnostic_text)
        or _POSTTOOLUSE_PHASE_FAILED_USAGE_RE.search(diagnostic_text)
    )


def _posttooluse_candidate_artifact_created(
    spine: TaskStandardSpine,
    tool_text: str,
) -> bool:
    path_anchors = _posttooluse_standard_path_anchors(spine)
    if not path_anchors:
        return False
    return any(
        _posttooluse_tool_creates_path_anchor(tool_text, path_anchor)
        for path_anchor in path_anchors
    )


def _posttooluse_standard_path_anchors(spine: TaskStandardSpine) -> tuple[str, ...]:
    anchors: list[str] = []
    for item in spine.all_items:
        anchors.extend(
            anchor.lower()
            for anchor in _posttooluse_path_anchors(item.text)
            if anchor.strip()
        )
    return tuple(dict.fromkeys(anchors))


def _posttooluse_path_anchors(text: str) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            anchor.strip()
            for anchor in re.findall(r"[A-Za-z0-9_./-]+\.[A-Za-z0-9_./-]+", text)
            if anchor.strip()
        )
    )


def _posttooluse_tool_creates_path_anchor(tool_text: str, path_anchor: str) -> bool:
    escaped = re.escape(path_anchor)
    creation_patterns = (
        rf">\s*{escaped}\b",
        rf"tee\s+(?:-[A-Za-z]+\s+)*{escaped}\b",
        rf"touch\s+{escaped}\b",
        rf"cat\s+>\s*{escaped}\b",
        rf"cp\s+\S+\s+{escaped}\b",
        rf"mv\s+\S+\s+{escaped}\b",
    )
    return any(re.search(pattern, tool_text) for pattern in creation_patterns)


def _first_unresolved_required_standard_item(
    spine: TaskStandardSpine,
    *,
    already_context_item_ids: tuple[str, ...],
) -> TaskStandardItem | None:
    already = set(already_context_item_ids)
    for kind in (
        TaskStandardItemKind.WORK_STANDARD,
        TaskStandardItemKind.CLOSURE_EVIDENCE,
    ):
        for item in spine.standard_items:
            if item.kind is kind and not item.has_aligned_evidence and item.item_id not in already:
                return item
    return None


def _first_required_standard_item_by_kind(
    spine: TaskStandardSpine,
    *,
    kind: TaskStandardItemKind,
    already_context_item_ids: tuple[str, ...],
) -> TaskStandardItem | None:
    already = set(already_context_item_ids)
    for item in spine.standard_items:
        if item.kind is kind and item.item_id not in already:
            return item
    return None


def _json_value_text(value: Any) -> str:
    if value is None:
        return ""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
