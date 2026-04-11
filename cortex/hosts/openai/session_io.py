"""Bounded persisted product journal carrier for the OpenAI runtime shell."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from cortex.hosts.openai.runtime import OpenAIRuntimeSession
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.sre.families import SoftControlFamily
from cortex.sre.brake import BrakeState
from cortex.sre.preservation import PreservationState

_ARTIFACT_KIND = "openai_product_journal"
_ARTIFACT_VERSION = 1
_TOP_LEVEL_KEYS = ("artifact_kind", "artifact_version", "journal")
_LEGACY_JOURNAL_KEYS = (
    "session_id",
    "event_index",
    "active_goal_ref",
    "pending_goal_refs",
    "confirmed_artifact_refs",
    "last_failure_class",
    "next_recommended_move",
)
_JOURNAL_KEYS = (
    "session_id",
    "event_index",
    "branch_registry",
    "active_track_ref",
    "active_goal_ref",
    "pending_goal_refs",
    "confirmed_artifact_refs",
    "budget_history",
    "brake_history",
    "last_selected_family",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
    "last_failure_class",
    "next_recommended_move",
)
_OPTIONAL_JOURNAL_KEY_SUFFIX = ("preservation_state",)
_ALLOWED_BUDGET_BANDS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class OpenAIRuntimeSessionArtifact:
    artifact_kind: str = _ARTIFACT_KIND
    artifact_version: int = _ARTIFACT_VERSION
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    active_goal_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = ()
    confirmed_artifact_refs: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    last_failure_class: str | None = None
    next_recommended_move: str = "continue"
    preservation_state: PreservationState | None = None

    def __post_init__(self) -> None:
        if self.artifact_kind != _ARTIFACT_KIND:
            raise ValueError(
                f"OpenAIRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
            )
        if self.artifact_version != _ARTIFACT_VERSION:
            raise ValueError(
                f"OpenAIRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
            )
        OpenAIRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            active_goal_ref=self.active_goal_ref,
            pending_goal_refs=self.pending_goal_refs,
            confirmed_artifact_refs=self.confirmed_artifact_refs,
            budget_history=self.budget_history,
            brake_history=self.brake_history,
            last_selected_family=self.last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
            last_failure_class=self.last_failure_class,
            next_recommended_move=self.next_recommended_move,
            preservation_state=self.preservation_state,
        )

    def as_payload(self) -> dict[str, object]:
        journal: dict[str, object] = {
            "session_id": self.session_id,
            "event_index": self.event_index,
            "branch_registry": list(self.branch_registry),
            "active_track_ref": self.active_track_ref,
            "active_goal_ref": self.active_goal_ref,
            "pending_goal_refs": list(self.pending_goal_refs),
            "confirmed_artifact_refs": list(self.confirmed_artifact_refs),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "last_selected_family": (
                self.last_selected_family.value
                if self.last_selected_family is not None
                else None
            ),
            "last_commitment_result_summary": self.last_commitment_result_summary,
            "last_realization_feedback": (
                self.last_realization_feedback.as_summary()
                if self.last_realization_feedback is not None
                else None
            ),
            "feedback_window": [
                entry.as_summary() for entry in self.feedback_window.entries
            ],
            "last_failure_class": self.last_failure_class,
            "next_recommended_move": self.next_recommended_move,
        }
        if self.preservation_state is not None:
            journal["preservation_state"] = self.preservation_state.as_payload()
        return {
            "artifact_kind": self.artifact_kind,
            "artifact_version": self.artifact_version,
            "journal": journal,
        }

    def to_session(self) -> OpenAIRuntimeSession:
        return OpenAIRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            active_goal_ref=self.active_goal_ref,
            pending_goal_refs=self.pending_goal_refs,
            confirmed_artifact_refs=self.confirmed_artifact_refs,
            budget_history=self.budget_history,
            brake_history=self.brake_history,
            last_selected_family=self.last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
            last_failure_class=self.last_failure_class,
            next_recommended_move=self.next_recommended_move,
            preservation_state=self.preservation_state,
        )


def build_openai_runtime_session_artifact(
    session: OpenAIRuntimeSession,
) -> OpenAIRuntimeSessionArtifact:
    if not isinstance(session, OpenAIRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "build_openai_runtime_session_artifact.session must be OpenAIRuntimeSession, "
            f"got {actual_type}."
        )
    return OpenAIRuntimeSessionArtifact(
        session_id=session.session_id,
        event_index=session.event_index,
        branch_registry=session.branch_registry,
        active_track_ref=session.active_track_ref,
        active_goal_ref=session.active_goal_ref,
        pending_goal_refs=session.pending_goal_refs,
        confirmed_artifact_refs=session.confirmed_artifact_refs,
        budget_history=session.budget_history,
        brake_history=session.brake_history,
        last_selected_family=session.last_selected_family,
        last_commitment_result_summary=session.last_commitment_result_summary,
        last_realization_feedback=session.last_realization_feedback,
        feedback_window=session.feedback_window,
        last_failure_class=session.last_failure_class,
        next_recommended_move=session.next_recommended_move,
        preservation_state=session.preservation_state,
    )


def parse_openai_runtime_session_artifact(
    payload: Mapping[str, Any],
) -> OpenAIRuntimeSession:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_openai_runtime_session_artifact.payload must be a mapping, "
            f"got {actual_type}."
        )
    artifact_kind = payload.get("artifact_kind")
    artifact_version = payload.get("artifact_version")
    if artifact_kind != _ARTIFACT_KIND:
        raise ValueError(
            f"OpenAIRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
        )
    if artifact_version != _ARTIFACT_VERSION:
        raise ValueError(
            f"OpenAIRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
        )
    _require_exact_keys(payload, _TOP_LEVEL_KEYS, "OpenAIRuntimeSessionArtifact")
    journal_payload = payload["journal"]
    if not isinstance(journal_payload, Mapping):
        raise TypeError("OpenAIRuntimeSessionArtifact.journal must be an object.")
    _require_journal_keys(journal_payload)

    preservation_state = (
        PreservationState.from_payload(journal_payload["preservation_state"])
        if "preservation_state" in journal_payload
        else None
    )

    if _is_legacy_journal_shape(journal_payload):
        active_goal_ref = _optional_non_empty_string(
            journal_payload["active_goal_ref"],
            "OpenAIRuntimeSessionArtifact.journal.active_goal_ref",
        )
        branch_registry, active_track_ref = _legacy_branch_state(
            active_goal_ref,
            preservation_state=preservation_state,
        )
        artifact = OpenAIRuntimeSessionArtifact(
            session_id=_optional_non_empty_string(
                journal_payload["session_id"],
                "OpenAIRuntimeSessionArtifact.journal.session_id",
            ),
            event_index=_non_negative_int(
                journal_payload["event_index"],
                "OpenAIRuntimeSessionArtifact.journal.event_index",
            ),
            branch_registry=branch_registry,
            active_track_ref=active_track_ref,
            active_goal_ref=active_goal_ref,
            pending_goal_refs=_string_tuple(
                journal_payload["pending_goal_refs"],
                "OpenAIRuntimeSessionArtifact.journal.pending_goal_refs",
            ),
            confirmed_artifact_refs=_string_tuple(
                journal_payload["confirmed_artifact_refs"],
                "OpenAIRuntimeSessionArtifact.journal.confirmed_artifact_refs",
            ),
            last_failure_class=_optional_non_empty_string(
                journal_payload["last_failure_class"],
                "OpenAIRuntimeSessionArtifact.journal.last_failure_class",
            ),
            next_recommended_move=_required_non_empty_string(
                journal_payload["next_recommended_move"],
                "OpenAIRuntimeSessionArtifact.journal.next_recommended_move",
            ),
            preservation_state=preservation_state,
        )
        return artifact.to_session()

    artifact = OpenAIRuntimeSessionArtifact(
        session_id=_optional_non_empty_string(
            journal_payload["session_id"],
            "OpenAIRuntimeSessionArtifact.journal.session_id",
        ),
        event_index=_non_negative_int(
            journal_payload["event_index"],
            "OpenAIRuntimeSessionArtifact.journal.event_index",
        ),
        branch_registry=_string_tuple(
            journal_payload["branch_registry"],
            "OpenAIRuntimeSessionArtifact.journal.branch_registry",
        ),
        active_track_ref=_required_non_empty_string(
            journal_payload["active_track_ref"],
            "OpenAIRuntimeSessionArtifact.journal.active_track_ref",
        ),
        active_goal_ref=_optional_non_empty_string(
            journal_payload["active_goal_ref"],
            "OpenAIRuntimeSessionArtifact.journal.active_goal_ref",
        ),
        pending_goal_refs=_string_tuple(
            journal_payload["pending_goal_refs"],
            "OpenAIRuntimeSessionArtifact.journal.pending_goal_refs",
        ),
        confirmed_artifact_refs=_string_tuple(
            journal_payload["confirmed_artifact_refs"],
            "OpenAIRuntimeSessionArtifact.journal.confirmed_artifact_refs",
        ),
        budget_history=_budget_history(
            journal_payload["budget_history"],
            "OpenAIRuntimeSessionArtifact.journal.budget_history",
        ),
        brake_history=_string_tuple(
            journal_payload["brake_history"],
            "OpenAIRuntimeSessionArtifact.journal.brake_history",
        ),
        last_selected_family=_optional_soft_control_family(
            journal_payload["last_selected_family"],
            "OpenAIRuntimeSessionArtifact.journal.last_selected_family",
        ),
        last_commitment_result_summary=_optional_non_empty_string(
            journal_payload["last_commitment_result_summary"],
            "OpenAIRuntimeSessionArtifact.journal.last_commitment_result_summary",
        ),
        last_realization_feedback=_optional_feedback(
            journal_payload["last_realization_feedback"],
            "OpenAIRuntimeSessionArtifact.journal.last_realization_feedback",
        ),
        feedback_window=_feedback_window(
            journal_payload["feedback_window"],
            "OpenAIRuntimeSessionArtifact.journal.feedback_window",
        ),
        last_failure_class=_optional_non_empty_string(
            journal_payload["last_failure_class"],
            "OpenAIRuntimeSessionArtifact.journal.last_failure_class",
        ),
        next_recommended_move=_required_non_empty_string(
            journal_payload["next_recommended_move"],
            "OpenAIRuntimeSessionArtifact.journal.next_recommended_move",
        ),
        preservation_state=preservation_state,
    )
    return artifact.to_session()


def read_openai_runtime_session_artifact(path: str | Path) -> OpenAIRuntimeSession:
    file_path = _coerce_path(path, "read_openai_runtime_session_artifact.path")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(
            "OpenAI runtime session artifact file must contain a JSON object at the top level."
        )
    return parse_openai_runtime_session_artifact(payload)


def write_openai_runtime_session_artifact(
    path: str | Path,
    session: OpenAIRuntimeSession,
) -> None:
    file_path = _coerce_path(path, "write_openai_runtime_session_artifact.path")
    artifact = build_openai_runtime_session_artifact(session)
    payload = artifact.as_payload()
    serialized = json.dumps(payload, indent=2, sort_keys=False)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=file_path.parent,
        delete=False,
    ) as handle:
        handle.write(serialized)
        handle.write("\n")
        temp_path = Path(handle.name)
    try:
        os.replace(temp_path, file_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _coerce_path(value: str | Path, label: str) -> Path:
    if isinstance(value, Path):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{label} must be non-empty after trimming.")
        return Path(stripped)
    actual_type = type(value).__name__
    raise TypeError(f"{label} must be str | Path, got {actual_type}.")


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected_keys: tuple[str, ...],
    label: str,
) -> None:
    actual_keys = tuple(payload)
    if actual_keys != expected_keys:
        raise ValueError(
            f"{label} must preserve the exact key order {expected_keys!r}, got {actual_keys!r}."
        )


def _require_journal_keys(payload: Mapping[str, Any]) -> None:
    actual_keys = tuple(payload)
    accepted_keys = {
        _LEGACY_JOURNAL_KEYS,
        _LEGACY_JOURNAL_KEYS + _OPTIONAL_JOURNAL_KEY_SUFFIX,
        _JOURNAL_KEYS,
        _JOURNAL_KEYS + _OPTIONAL_JOURNAL_KEY_SUFFIX,
    }
    if actual_keys in accepted_keys:
        return
    raise ValueError(
        "OpenAIRuntimeSessionArtifact.journal must preserve one of the accepted key orders "
        f"{sorted(accepted_keys)!r}, got {actual_keys!r}."
    )


def _is_legacy_journal_shape(payload: Mapping[str, Any]) -> bool:
    return tuple(payload) in {
        _LEGACY_JOURNAL_KEYS,
        _LEGACY_JOURNAL_KEYS + _OPTIONAL_JOURNAL_KEY_SUFFIX,
    }


def _legacy_branch_state(
    active_goal_ref: str | None,
    *,
    preservation_state: PreservationState | None,
) -> tuple[tuple[str, ...], str]:
    if preservation_state is not None or active_goal_ref is None:
        return ("main",), "main"
    return ("main", active_goal_ref), active_goal_ref


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _required_non_empty_string(value, label)


def _required_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


def _non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a non-negative integer, got {actual_type}.")
    if value < 0:
        raise ValueError(f"{label} must be non-negative.")
    return value


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    parsed: list[str] = []
    for item in value:
        parsed.append(_required_non_empty_string(item, label))
    return tuple(parsed)


def _budget_history(value: Any, label: str) -> tuple[str, ...]:
    entries = _string_tuple(value, label)
    for entry in entries:
        if not entry.startswith("shell-"):
            raise ValueError(
                f"{label} only supports shell budget history entries, got {entry!r}."
            )
        budget_band = entry.replace("shell-", "", 1)
        if budget_band not in _ALLOWED_BUDGET_BANDS:
            raise ValueError(
                f"{label} only supports shell budget entries for {_ALLOWED_BUDGET_BANDS!r}."
            )
    return entries


def _optional_soft_control_family(value: Any, label: str) -> SoftControlFamily | None:
    if value is None:
        return None
    return _soft_control_family(value, label)


def _soft_control_family(value: Any, label: str) -> SoftControlFamily:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    try:
        return SoftControlFamily(value.strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a canonical soft-control family.") from exc


def _brake_state(value: Any, label: str) -> BrakeState:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    try:
        return BrakeState(value.strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a canonical brake state.") from exc


def _optional_feedback(value: Any, label: str) -> ReferenceRealizationFeedback | None:
    if value is None:
        return None
    return _feedback(value, label)


def _feedback_window(
    value: Any,
    label: str,
) -> ReferenceRealizationFeedbackWindow:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    return ReferenceRealizationFeedbackWindow(
        entries=tuple(_feedback(item, label) for item in value)
    )


def _feedback(value: Any, label: str) -> ReferenceRealizationFeedback:
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    feedback_keys = (
        "selected_family",
        "realized_family",
        "brake_state",
        "commitment_result_kind",
        "warning_codes",
        "host_friction_tags",
    )
    _require_exact_keys(value, feedback_keys, label)
    return ReferenceRealizationFeedback(
        selected_family=_soft_control_family(value["selected_family"], f"{label}.selected_family"),
        realized_family=_soft_control_family(value["realized_family"], f"{label}.realized_family"),
        brake_state=_brake_state(value["brake_state"], f"{label}.brake_state"),
        commitment_result_kind=_optional_commitment_result_kind(
            value["commitment_result_kind"],
            f"{label}.commitment_result_kind",
        ),
        warning_codes=_string_tuple(value["warning_codes"], f"{label}.warning_codes"),
        host_friction_tags=_string_tuple(
            value["host_friction_tags"],
            f"{label}.host_friction_tags",
        ),
    )


def _optional_commitment_result_kind(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    stripped = value.strip()
    if stripped not in {"certified", "uncertified", "blocked"}:
        raise ValueError(f"{label} must be a canonical commitment status when provided.")
    return stripped


__all__ = [
    "OpenAIRuntimeSessionArtifact",
    "build_openai_runtime_session_artifact",
    "parse_openai_runtime_session_artifact",
    "read_openai_runtime_session_artifact",
    "write_openai_runtime_session_artifact",
]
