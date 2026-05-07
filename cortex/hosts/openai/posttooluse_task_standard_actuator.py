"""PostToolUse task-standard actuator for the Codex App/CLI host."""

from __future__ import annotations

import re
from dataclasses import dataclass
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
from cortex.sre.tool_evidence import (
    ToolEvidenceClassification,
    ToolEvidenceObservation,
    ToolEvidencePhase,
    classify_tool_evidence,
    tool_evidence_has_verification_marker,
    tool_evidence_looks_failed,
    tool_evidence_looks_successful,
    tool_evidence_path_anchors_from_texts,
    tool_evidence_phase_completed,
    tool_evidence_text,
)

from .codex_app_cli_lifecycle import OpenAICodexLifecycleEvent


_POSTTOOLUSE_TASK_STANDARD_CONTEXT_TEMPLATE = (
    "I still need direct evidence for: {standard_item}. The last tool "
    "result did not show that exact item. Next step: {next_step} before treating "
    "this as done."
)
_POSTTOOLUSE_TASK_STANDARD_CONTEXT_SPAN_LIMIT = 180
_POSTTOOLUSE_TASK_STANDARD_CONTEXT_SESSION_LIMIT = 2


class _CodexToolPayload(Protocol):
    hook_event_name: OpenAICodexLifecycleEvent
    tool_name: str | None
    tool_input: Any
    tool_response: Any
    error: str | None


PostToolUseTaskStandardPhase = ToolEvidencePhase
PostToolUseTaskStandardPhaseResult = ToolEvidenceClassification


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
    if already_context_item_ids:
        return PostToolUseTaskStandardContextDecision(
            item_id=None,
            context_text=None,
            reason="posttooluse_context_active_context_pending",
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
    return classify_tool_evidence(
        _tool_evidence_observation_for_payload(
            payload,
            path_anchors=_posttooluse_standard_path_anchors(spine),
        )
    )


def tool_event_has_verification_evidence(
    payload: _CodexToolPayload,
    *,
    active_verification_expectation: bool = False,
) -> bool:
    observation = _tool_evidence_observation_for_payload(payload)
    text = observation.lowered_text
    if not text:
        return False
    if not tool_evidence_has_verification_marker(
        text,
        count_completion_status=False,
    ):
        return False
    if tool_event_looks_failed(payload, text):
        return False
    return active_verification_expectation or tool_evidence_looks_successful(text)


def _tool_evidence_observation_for_payload(
    payload: _CodexToolPayload,
    *,
    path_anchors: tuple[str, ...] = (),
) -> ToolEvidenceObservation:
    return ToolEvidenceObservation.from_tool_parts(
        hook_event_name=payload.hook_event_name.value,
        tool_name=payload.tool_name,
        tool_input=payload.tool_input,
        tool_response=payload.tool_response,
        error=payload.error,
        path_anchors=path_anchors,
        count_completion_status_as_verification_marker=False,
    )


def tool_event_has_verification_marker(normalized_tool_text: str) -> bool:
    return tool_evidence_has_verification_marker(
        normalized_tool_text,
        count_completion_status=False,
    )


def tool_event_text(payload: _CodexToolPayload) -> str:
    return tool_evidence_text(
        payload.tool_name,
        payload.tool_input,
        payload.tool_response,
    )


def tool_event_looks_successful(payload: _CodexToolPayload, text: str) -> bool:
    return (
        payload.hook_event_name is OpenAICodexLifecycleEvent.POST_TOOL_USE
        and tool_evidence_looks_successful(text)
    )


def tool_event_looks_failed(payload: _CodexToolPayload, text: str) -> bool:
    return tool_evidence_looks_failed(
        text,
        error_present=bool(payload.error),
    )


def posttooluse_phase_tool_response_completed(
    payload: _CodexToolPayload,
    tool_text: str,
) -> bool:
    return tool_evidence_phase_completed(
        ToolEvidenceObservation(
            tool_text=tool_text,
            hook_event_name=payload.hook_event_name.value,
            tool_response_present=payload.tool_response is not None,
            error_present=bool(payload.error),
        )
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


def _posttooluse_standard_path_anchors(spine: TaskStandardSpine) -> tuple[str, ...]:
    return tool_evidence_path_anchors_from_texts(
        tuple(item.text for item in spine.all_items)
    )


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
