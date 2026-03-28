"""Bounded persisted continuation carrier for the OpenAI runtime shell."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from cortex.runtime.openai import OpenAIRuntimeSession
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow

_ARTIFACT_KIND = "openai-runtime-session"
_ARTIFACT_VERSION = 1
_TOP_LEVEL_KEYS = (
    "artifact_kind",
    "artifact_version",
    "continuity_truth",
    "control_residue",
)
_CONTINUITY_TRUTH_KEYS = (
    "session_id",
    "event_index",
    "branch_registry",
    "active_track_ref",
    "pending_goal_refs",
)
_CONTROL_RESIDUE_KEYS = (
    "last_budget_band",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
)
_ALLOWED_BUDGET_BANDS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class OpenAIRuntimeSessionArtifact:
    artifact_kind: str = _ARTIFACT_KIND
    artifact_version: int = _ARTIFACT_VERSION
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    last_budget_band: str | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )

    def __post_init__(self) -> None:
        if self.artifact_kind != _ARTIFACT_KIND:
            raise ValueError(
                f"OpenAIRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
            )
        if self.artifact_version != _ARTIFACT_VERSION:
            raise ValueError(
                f"OpenAIRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
            )
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "OpenAIRuntimeSessionArtifact.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("OpenAIRuntimeSessionArtifact.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.pending_goal_refs must contain only non-empty values after trimming."
            )
        if self.last_budget_band is not None and self.last_budget_band not in _ALLOWED_BUDGET_BANDS:
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.last_budget_band must be one of "
                "`low`, `medium`, `high`, or `None`."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "OpenAIRuntimeSessionArtifact.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "OpenAIRuntimeSessionArtifact.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if (
            self.last_realization_feedback is not None
            and self.feedback_window.entries
            and self.feedback_window.entries[-1] != self.last_realization_feedback
        ):
            raise ValueError(
                "OpenAIRuntimeSessionArtifact.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "artifact_kind": self.artifact_kind,
            "artifact_version": self.artifact_version,
            "continuity_truth": {
                "session_id": self.session_id,
                "event_index": self.event_index,
                "branch_registry": list(self.branch_registry),
                "active_track_ref": self.active_track_ref,
                "pending_goal_refs": list(self.pending_goal_refs),
            },
            "control_residue": {
                "last_budget_band": self.last_budget_band,
                "last_commitment_result_summary": self.last_commitment_result_summary,
                "last_realization_feedback": (
                    self.last_realization_feedback.as_summary()
                    if self.last_realization_feedback is not None
                    else None
                ),
                "feedback_window": [
                    entry.as_summary() for entry in self.feedback_window.entries
                ],
            },
        }

    def to_session(self) -> OpenAIRuntimeSession:
        budget_history = ()
        if self.last_budget_band is not None:
            budget_history = (f"shell-{self.last_budget_band}",)

        brake_history = ()
        last_selected_family = None
        if self.last_realization_feedback is not None:
            brake_history = (self.last_realization_feedback.brake_state.value,)
            last_selected_family = self.last_realization_feedback.selected_family

        return OpenAIRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            pending_goal_refs=self.pending_goal_refs,
            budget_history=budget_history,
            brake_history=brake_history,
            last_selected_family=last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
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
        pending_goal_refs=session.pending_goal_refs,
        last_budget_band=_last_budget_band(session.budget_history),
        last_commitment_result_summary=session.last_commitment_result_summary,
        last_realization_feedback=session.last_realization_feedback,
        feedback_window=session.feedback_window,
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
    _require_exact_keys(payload, _TOP_LEVEL_KEYS, "OpenAIRuntimeSessionArtifact")
    artifact_kind = payload["artifact_kind"]
    artifact_version = payload["artifact_version"]
    continuity_truth_payload = payload["continuity_truth"]
    control_residue_payload = payload["control_residue"]

    if artifact_kind != _ARTIFACT_KIND:
        raise ValueError(
            f"OpenAIRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
        )
    if artifact_version != _ARTIFACT_VERSION:
        raise ValueError(
            f"OpenAIRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
        )
    if not isinstance(continuity_truth_payload, Mapping):
        raise TypeError("OpenAIRuntimeSessionArtifact.continuity_truth must be an object.")
    if not isinstance(control_residue_payload, Mapping):
        raise TypeError("OpenAIRuntimeSessionArtifact.control_residue must be an object.")

    _require_exact_keys(
        continuity_truth_payload,
        _CONTINUITY_TRUTH_KEYS,
        "OpenAIRuntimeSessionArtifact.continuity_truth",
    )
    _require_exact_keys(
        control_residue_payload,
        _CONTROL_RESIDUE_KEYS,
        "OpenAIRuntimeSessionArtifact.control_residue",
    )

    artifact = OpenAIRuntimeSessionArtifact(
        session_id=_optional_non_empty_string(
            continuity_truth_payload["session_id"],
            "OpenAIRuntimeSessionArtifact.continuity_truth.session_id",
        ),
        event_index=_non_negative_int(
            continuity_truth_payload["event_index"],
            "OpenAIRuntimeSessionArtifact.continuity_truth.event_index",
        ),
        branch_registry=_string_tuple(
            continuity_truth_payload["branch_registry"],
            "OpenAIRuntimeSessionArtifact.continuity_truth.branch_registry",
        ),
        active_track_ref=_required_non_empty_string(
            continuity_truth_payload["active_track_ref"],
            "OpenAIRuntimeSessionArtifact.continuity_truth.active_track_ref",
        ),
        pending_goal_refs=_string_tuple(
            continuity_truth_payload["pending_goal_refs"],
            "OpenAIRuntimeSessionArtifact.continuity_truth.pending_goal_refs",
        ),
        last_budget_band=_optional_budget_band(
            control_residue_payload["last_budget_band"],
            "OpenAIRuntimeSessionArtifact.control_residue.last_budget_band",
        ),
        last_commitment_result_summary=_optional_non_empty_string(
            control_residue_payload["last_commitment_result_summary"],
            "OpenAIRuntimeSessionArtifact.control_residue.last_commitment_result_summary",
        ),
        last_realization_feedback=_optional_feedback(
            control_residue_payload["last_realization_feedback"],
            "OpenAIRuntimeSessionArtifact.control_residue.last_realization_feedback",
        ),
        feedback_window=_feedback_window(
            control_residue_payload["feedback_window"],
            "OpenAIRuntimeSessionArtifact.control_residue.feedback_window",
        ),
    )
    return artifact.to_session()


def read_openai_runtime_session_artifact(path: Path) -> OpenAIRuntimeSession:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "read_openai_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return parse_openai_runtime_session_artifact(payload)


def write_openai_runtime_session_artifact(
    path: Path,
    session: OpenAIRuntimeSession,
) -> None:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "write_openai_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    if not path.parent.exists():
        raise FileNotFoundError(
            f"OpenAI runtime session artifact parent does not exist: {path.parent}"
        )

    artifact = build_openai_runtime_session_artifact(session)
    payload = artifact.as_payload()

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = handle.name
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(temp_path, path)
    except Exception:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)
        raise


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected_keys: tuple[str, ...],
    label: str,
) -> None:
    actual_keys = tuple(payload.keys())
    missing_keys = [key for key in expected_keys if key not in payload]
    extra_keys = [key for key in actual_keys if key not in expected_keys]
    if missing_keys or extra_keys:
        raise ValueError(
            f"{label} keys must be exactly {expected_keys}; "
            f"missing={missing_keys}, extra={extra_keys}."
        )


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming when provided.")
    return stripped


def _required_non_empty_string(value: Any, label: str) -> str:
    result = _optional_non_empty_string(value, label)
    if result is None:
        raise ValueError(f"{label} must be non-null.")
    return result


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


def _optional_budget_band(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    stripped = value.strip()
    if stripped not in _ALLOWED_BUDGET_BANDS:
        raise ValueError(
            f"{label} must be one of {tuple(sorted(_ALLOWED_BUDGET_BANDS))} when provided."
        )
    return stripped


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
    from cortex.sre.brake import BrakeState
    from cortex.sre.families import SoftControlFamily

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

    def _family(raw: Any, field_label: str) -> SoftControlFamily:
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be a string, got {actual_type}.")
        try:
            return SoftControlFamily(raw.strip())
        except ValueError as exc:
            raise ValueError(f"{field_label} must be a canonical soft-control family.") from exc

    def _brake(raw: Any, field_label: str) -> BrakeState:
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be a string, got {actual_type}.")
        try:
            return BrakeState(raw.strip())
        except ValueError as exc:
            raise ValueError(f"{field_label} must be a canonical brake state.") from exc

    def _commitment_kind(raw: Any, field_label: str) -> str | None:
        if raw is None:
            return None
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be str | null, got {actual_type}.")
        stripped = raw.strip()
        if stripped not in {"certified", "uncertified", "blocked"}:
            raise ValueError(f"{field_label} must be a canonical commitment status when provided.")
        return stripped

    return ReferenceRealizationFeedback(
        selected_family=_family(value["selected_family"], f"{label}.selected_family"),
        realized_family=_family(value["realized_family"], f"{label}.realized_family"),
        brake_state=_brake(value["brake_state"], f"{label}.brake_state"),
        commitment_result_kind=_commitment_kind(
            value["commitment_result_kind"],
            f"{label}.commitment_result_kind",
        ),
        warning_codes=_string_tuple(value["warning_codes"], f"{label}.warning_codes"),
        host_friction_tags=_string_tuple(
            value["host_friction_tags"],
            f"{label}.host_friction_tags",
        ),
    )


def _last_budget_band(budget_history: tuple[str, ...]) -> str | None:
    if not budget_history:
        return None
    last_budget_entry = budget_history[-1]
    if not last_budget_entry.startswith("shell-"):
        raise ValueError(
            "OpenAI runtime session artifact only supports shell budget history entries."
        )
    last_budget_band = last_budget_entry.replace("shell-", "", 1)
    if last_budget_band not in _ALLOWED_BUDGET_BANDS:
        raise ValueError(
            "OpenAI runtime session artifact only supports `shell-low`, "
            "`shell-medium`, and `shell-high` budget entries."
        )
    return last_budget_band


__all__ = [
    "OpenAIRuntimeSessionArtifact",
    "build_openai_runtime_session_artifact",
    "parse_openai_runtime_session_artifact",
    "read_openai_runtime_session_artifact",
    "write_openai_runtime_session_artifact",
]
