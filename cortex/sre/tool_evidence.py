"""Shared tool-evidence classification for task-standard consumers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ToolEvidencePhase(str, Enum):
    NO_TOOL_EVENT_TEXT = "no_tool_event_text"
    PRE_ARTIFACT_MISSING = "pre_artifact_missing"
    FAILED_CHECK = "failed_check"
    FAILED_TOOL = "failed_tool"
    CANDIDATE_ARTIFACT_CREATED = "candidate_artifact_created"
    READBACK_COMPLETED = "readback_completed"
    MARKERLESS = "markerless"
    UNRELATED_OR_GENERIC = "unrelated_or_generic"


_NORMALIZED_VERIFICATION_MARKERS = (
    "test",
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
    "check",
    "verify",
    "cat",
    "wc",
    "wc -l",
    "grep",
    "stat",
    "passed",
    "success",
    "content_ok",
    "file_ok",
    "exists",
    "matches exactly",
)
_COMPLETION_STATUS_VERIFICATION_MARKERS = (
    "exit_code 0",
    "status completed",
)
_RAW_VERIFICATION_MARKERS = (
    "$(cat",
    '"cat',
    '\\"cat',
    '"wc',
    '\\"wc',
    '"stat',
    '\\"stat',
    "[ -f",
    "test -f",
    "content=",
    "lines=",
)
_MISSING_ARTIFACT_MARKERS = (
    "no such file or directory",
    "cannot stat",
    "does not exist",
    "open: no such file",
    "open: no such file or directory",
    "no such file",
)
_FAILED_OPTION_RE = re.compile(
    r"(^|\n)\s*[^\n]{0,160}\b(?:illegal|invalid|unrecognized|unknown) option\b",
)
_FAILED_USAGE_RE = re.compile(r"(^|\n)\s*usage:\s+\S+")
_SUCCESS_MARKERS = (
    "file_ok",
    "content_ok",
    "passed",
    "success",
    "ok",
    "matches exactly",
)
_FAILED_MARKERS = (
    "exit_code 1",
    "exit_code 2",
    "status failed",
    "failed",
    "failure",
    "traceback",
    "error:",
    "content_mismatch",
    "not found",
)


@dataclass(frozen=True, slots=True)
class ToolEvidenceObservation:
    tool_text: str
    hook_event_name: str | None = None
    tool_response_present: bool = False
    error_present: bool = False
    path_anchors: tuple[str, ...] = ()
    count_completion_status_as_verification_marker: bool = True

    @classmethod
    def from_tool_parts(
        cls,
        *,
        hook_event_name: str | None,
        tool_name: str | None,
        tool_input: Any,
        tool_response: Any,
        error: str | None,
        path_anchors: tuple[str, ...] = (),
        count_completion_status_as_verification_marker: bool = True,
    ) -> "ToolEvidenceObservation":
        return cls(
            tool_text=tool_evidence_text(tool_name, tool_input, tool_response),
            hook_event_name=hook_event_name,
            tool_response_present=tool_response is not None,
            error_present=bool(error),
            path_anchors=path_anchors,
            count_completion_status_as_verification_marker=(
                count_completion_status_as_verification_marker
            ),
        )

    @property
    def normalized_text(self) -> str:
        return normalize_tool_evidence_text(self.tool_text)

    @property
    def lowered_text(self) -> str:
        return str(self.tool_text).lower()


@dataclass(frozen=True, slots=True)
class ToolEvidenceClassification:
    phase: ToolEvidencePhase
    tool_text: str
    has_verification_marker: bool = False
    candidate_artifact_created: bool = False
    completed: bool = False
    failed_tool: bool = False
    failed_check: bool = False
    missing_artifact: bool = False

    @property
    def silence_reason(self) -> str:
        if self.phase is ToolEvidencePhase.NO_TOOL_EVENT_TEXT:
            return "no_tool_event_text"
        if self.phase is ToolEvidencePhase.PRE_ARTIFACT_MISSING:
            return "pre_artifact_candidate_missing"
        if self.phase is ToolEvidencePhase.FAILED_CHECK:
            return "phase_check_failed"
        if self.phase is ToolEvidencePhase.FAILED_TOOL:
            return "tool_event_failed"
        if self.phase is ToolEvidencePhase.MARKERLESS:
            return "no_verification_marker"
        return "no_candidate_artifact_or_readback"

    @property
    def context_eligible(self) -> bool:
        return self.phase in {
            ToolEvidencePhase.CANDIDATE_ARTIFACT_CREATED,
            ToolEvidencePhase.READBACK_COMPLETED,
        }


def classify_tool_evidence(
    observation: ToolEvidenceObservation,
) -> ToolEvidenceClassification:
    tool_text = observation.lowered_text
    if not tool_text:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.NO_TOOL_EVENT_TEXT,
            tool_text=tool_text,
        )
    has_marker = tool_evidence_has_verification_marker(
        tool_text,
        count_completion_status=(
            observation.count_completion_status_as_verification_marker
        ),
    )
    missing_artifact = tool_evidence_missing_artifact(tool_text)
    failed_check = tool_evidence_failed_check(tool_text)
    failed_tool = tool_evidence_looks_failed(
        tool_text,
        error_present=observation.error_present,
    )
    completed = tool_evidence_phase_completed(observation)
    candidate_artifact_created = completed and tool_evidence_candidate_artifact_created(
        tool_text,
        observation.path_anchors,
    )
    if not has_marker and not candidate_artifact_created:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.MARKERLESS,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            candidate_artifact_created=candidate_artifact_created,
            completed=completed,
            failed_tool=failed_tool,
            failed_check=failed_check,
            missing_artifact=missing_artifact,
        )
    if has_marker and missing_artifact:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.PRE_ARTIFACT_MISSING,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            candidate_artifact_created=candidate_artifact_created,
            completed=completed,
            failed_tool=failed_tool,
            failed_check=failed_check,
            missing_artifact=True,
        )
    if failed_check:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.FAILED_CHECK,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            candidate_artifact_created=candidate_artifact_created,
            completed=completed,
            failed_tool=failed_tool,
            failed_check=True,
            missing_artifact=missing_artifact,
        )
    if failed_tool:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.FAILED_TOOL,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            candidate_artifact_created=candidate_artifact_created,
            completed=completed,
            failed_tool=True,
            failed_check=failed_check,
            missing_artifact=missing_artifact,
        )
    if candidate_artifact_created:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.CANDIDATE_ARTIFACT_CREATED,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            candidate_artifact_created=True,
            completed=True,
        )
    if has_marker and completed:
        return ToolEvidenceClassification(
            phase=ToolEvidencePhase.READBACK_COMPLETED,
            tool_text=tool_text,
            has_verification_marker=has_marker,
            completed=True,
        )
    return ToolEvidenceClassification(
        phase=ToolEvidencePhase.UNRELATED_OR_GENERIC,
        tool_text=tool_text,
        has_verification_marker=has_marker,
        completed=completed,
        failed_tool=failed_tool,
        failed_check=failed_check,
        missing_artifact=missing_artifact,
    )


def tool_evidence_text(
    tool_name: str | None,
    tool_input: Any,
    tool_response: Any,
) -> str:
    return " ".join(
        value
        for value in (
            tool_name or "",
            _json_value_text(tool_input),
            _json_value_text(tool_response),
        )
        if value
    )


def normalize_tool_evidence_text(text: str) -> str:
    text = re.sub(r"[^a-z0-9_./-]+", " ", str(text).lower())
    return f" {re.sub(r'\\s+', ' ', text).strip()} "


def tool_evidence_has_verification_marker(
    text: str,
    *,
    count_completion_status: bool = True,
) -> bool:
    lowered = str(text).lower()
    normalized = normalize_tool_evidence_text(lowered)
    if any(marker in lowered for marker in _RAW_VERIFICATION_MARKERS):
        return True
    markers = _NORMALIZED_VERIFICATION_MARKERS
    if count_completion_status:
        markers = (*markers, *_COMPLETION_STATUS_VERIFICATION_MARKERS)
    return any(f" {marker} " in normalized for marker in markers)


def tool_evidence_missing_artifact(text: str) -> bool:
    lowered = str(text).lower()
    return any(marker in lowered for marker in _MISSING_ARTIFACT_MARKERS)


def tool_evidence_failed_check(text: str) -> bool:
    diagnostic_text = str(text).lower().replace("\\n", "\n")
    return bool(
        _FAILED_OPTION_RE.search(diagnostic_text)
        or _FAILED_USAGE_RE.search(diagnostic_text)
    )


def tool_evidence_looks_successful(text: str) -> bool:
    lowered = str(text).lower()
    normalized = normalize_tool_evidence_text(lowered)
    if " exit_code 0 " in normalized or " status completed " in normalized:
        return True
    return any(f" {marker} " in normalized for marker in _SUCCESS_MARKERS)


def tool_evidence_looks_failed(
    text: str,
    *,
    error_present: bool = False,
) -> bool:
    if error_present:
        return True
    lowered = str(text).lower()
    normalized = normalize_tool_evidence_text(lowered)
    return any(
        marker in lowered or f" {marker} " in normalized
        for marker in _FAILED_MARKERS
    )


def tool_evidence_phase_completed(observation: ToolEvidenceObservation) -> bool:
    if tool_evidence_looks_failed(
        observation.tool_text,
        error_present=observation.error_present,
    ):
        return False
    if tool_evidence_missing_artifact(observation.tool_text):
        return False
    if tool_evidence_failed_check(observation.tool_text):
        return False
    return tool_evidence_looks_successful(observation.tool_text) or (
        observation.hook_event_name == "PostToolUse"
        and observation.tool_response_present
    )


def tool_evidence_candidate_artifact_created(
    text: str,
    path_anchors: tuple[str, ...],
) -> bool:
    normalized_anchors = tuple(
        dict.fromkeys(anchor.lower() for anchor in path_anchors if anchor.strip())
    )
    if not normalized_anchors:
        return False
    lowered = str(text).lower()
    return any(
        _tool_evidence_creates_path_anchor(lowered, anchor)
        for anchor in normalized_anchors
    )


def tool_evidence_path_anchors(text: str) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            anchor.strip()
            for anchor in re.findall(r"[A-Za-z0-9_./-]+\.[A-Za-z0-9_./-]+", text)
            if anchor.strip()
        )
    )


def tool_evidence_path_anchors_from_texts(texts: tuple[str, ...]) -> tuple[str, ...]:
    anchors: list[str] = []
    for text in texts:
        anchors.extend(anchor.lower() for anchor in tool_evidence_path_anchors(text))
    return tuple(dict.fromkeys(anchor for anchor in anchors if anchor.strip()))


def _tool_evidence_creates_path_anchor(text: str, path_anchor: str) -> bool:
    escaped = re.escape(path_anchor)
    creation_patterns = (
        rf">\s*{escaped}\b",
        rf"tee\s+(?:-[A-Za-z]+\s+)*{escaped}\b",
        rf"touch\s+{escaped}\b",
        rf"cat\s+>\s*{escaped}\b",
        rf"cp\s+\S+\s+{escaped}\b",
        rf"mv\s+\S+\s+{escaped}\b",
    )
    return any(re.search(pattern, text) for pattern in creation_patterns)


def _json_value_text(value: Any) -> str:
    if value is None:
        return ""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


__all__ = [
    "ToolEvidenceClassification",
    "ToolEvidenceObservation",
    "ToolEvidencePhase",
    "classify_tool_evidence",
    "normalize_tool_evidence_text",
    "tool_evidence_candidate_artifact_created",
    "tool_evidence_failed_check",
    "tool_evidence_has_verification_marker",
    "tool_evidence_looks_failed",
    "tool_evidence_looks_successful",
    "tool_evidence_missing_artifact",
    "tool_evidence_path_anchors",
    "tool_evidence_path_anchors_from_texts",
    "tool_evidence_phase_completed",
    "tool_evidence_text",
]
