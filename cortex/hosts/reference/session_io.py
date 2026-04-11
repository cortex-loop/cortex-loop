"""Bounded persisted continuation carrier for the reference runtime shell."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from cortex.hosts._executive_closure import (
    canonicalize_executive_modulator_memory,
    executive_modulator_memory_payload,
)
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.hosts.reference.runtime import ReferenceRuntimeSession
from cortex.sre.modulators import ExecutiveModulatorMemory

_ARTIFACT_KIND = "reference-runtime-session"
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
    "executive_modulator_memory",
)
_PRE_MODULATOR_CONTROL_RESIDUE_KEYS = (
    "last_budget_band",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
)
_ALLOWED_BUDGET_BANDS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class ReferenceRuntimeSessionArtifact:
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
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        if self.artifact_kind != _ARTIFACT_KIND:
            raise ValueError(
                f"ReferenceRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
            )
        if self.artifact_version != _ARTIFACT_VERSION:
            raise ValueError(
                f"ReferenceRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
            )
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ReferenceRuntimeSessionArtifact.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.event_index must be non-negative."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.pending_goal_refs must contain only non-empty values after trimming."
            )
        if self.last_budget_band is not None and self.last_budget_band not in _ALLOWED_BUDGET_BANDS:
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.last_budget_band must be one of "
                "`low`, `medium`, `high`, or `None`."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "ReferenceRuntimeSessionArtifact.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "ReferenceRuntimeSessionArtifact.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if self.executive_modulator_memory is not None and not isinstance(
            self.executive_modulator_memory,
            ExecutiveModulatorMemory,
        ):
            actual_type = type(self.executive_modulator_memory).__name__
            raise TypeError(
                "ReferenceRuntimeSessionArtifact.executive_modulator_memory must be "
                f"ExecutiveModulatorMemory | None, got {actual_type}."
            )
        if (
            self.last_realization_feedback is not None
            and self.feedback_window.entries
            and self.feedback_window.entries[-1] != self.last_realization_feedback
        ):
            raise ValueError(
                "ReferenceRuntimeSessionArtifact.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )
        normalized_executive_modulator_memory = canonicalize_executive_modulator_memory(
            self.executive_modulator_memory
        )
        if normalized_executive_modulator_memory != self.executive_modulator_memory:
            object.__setattr__(
                self,
                "executive_modulator_memory",
                normalized_executive_modulator_memory,
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
                "executive_modulator_memory": (
                    executive_modulator_memory_payload(self.executive_modulator_memory)
                    if self.executive_modulator_memory is not None
                    else None
                ),
            },
        }

    def to_session(self) -> ReferenceRuntimeSession:
        budget_history = ()
        if self.last_budget_band is not None:
            budget_history = (f"shell-{self.last_budget_band}",)

        brake_history = ()
        last_selected_family = None
        if self.last_realization_feedback is not None:
            brake_history = (self.last_realization_feedback.brake_state.value,)
            last_selected_family = self.last_realization_feedback.selected_family

        return ReferenceRuntimeSession(
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
            executive_modulator_memory=self.executive_modulator_memory,
        )


def build_reference_runtime_session_artifact(
    session: ReferenceRuntimeSession,
) -> ReferenceRuntimeSessionArtifact:
    if not isinstance(session, ReferenceRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "build_reference_runtime_session_artifact.session must be ReferenceRuntimeSession, "
            f"got {actual_type}."
        )
    return ReferenceRuntimeSessionArtifact(
        session_id=session.session_id,
        event_index=session.event_index,
        branch_registry=session.branch_registry,
        active_track_ref=session.active_track_ref,
        pending_goal_refs=session.pending_goal_refs,
        last_budget_band=_last_budget_band(session.budget_history),
        last_commitment_result_summary=session.last_commitment_result_summary,
        last_realization_feedback=session.last_realization_feedback,
        feedback_window=session.feedback_window,
        executive_modulator_memory=session.executive_modulator_memory,
    )


def parse_reference_runtime_session_artifact(
    payload: Mapping[str, Any],
) -> ReferenceRuntimeSession:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_reference_runtime_session_artifact.payload must be a mapping, "
            f"got {actual_type}."
        )

    _require_exact_keys(payload, _TOP_LEVEL_KEYS, "ReferenceRuntimeSessionArtifact")
    artifact_kind = payload["artifact_kind"]
    artifact_version = payload["artifact_version"]
    continuity_truth_payload = payload["continuity_truth"]
    control_residue_payload = payload["control_residue"]

    if artifact_kind != _ARTIFACT_KIND:
        raise ValueError(
            f"ReferenceRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
        )
    if artifact_version != _ARTIFACT_VERSION:
        raise ValueError(
            f"ReferenceRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
        )
    if not isinstance(continuity_truth_payload, Mapping):
        raise TypeError(
            "ReferenceRuntimeSessionArtifact.continuity_truth must be an object."
        )
    if not isinstance(control_residue_payload, Mapping):
        raise TypeError(
            "ReferenceRuntimeSessionArtifact.control_residue must be an object."
        )

    _require_exact_keys(
        continuity_truth_payload,
        _CONTINUITY_TRUTH_KEYS,
        "ReferenceRuntimeSessionArtifact.continuity_truth",
    )
    _require_control_residue_keys(control_residue_payload)

    artifact = ReferenceRuntimeSessionArtifact(
        session_id=_optional_non_empty_string(
            continuity_truth_payload["session_id"],
            "ReferenceRuntimeSessionArtifact.continuity_truth.session_id",
        ),
        event_index=_non_negative_int(
            continuity_truth_payload["event_index"],
            "ReferenceRuntimeSessionArtifact.continuity_truth.event_index",
        ),
        branch_registry=_string_tuple(
            continuity_truth_payload["branch_registry"],
            "ReferenceRuntimeSessionArtifact.continuity_truth.branch_registry",
        ),
        active_track_ref=_required_non_empty_string(
            continuity_truth_payload["active_track_ref"],
            "ReferenceRuntimeSessionArtifact.continuity_truth.active_track_ref",
        ),
        pending_goal_refs=_string_tuple(
            continuity_truth_payload["pending_goal_refs"],
            "ReferenceRuntimeSessionArtifact.continuity_truth.pending_goal_refs",
        ),
        last_budget_band=_optional_budget_band(
            control_residue_payload["last_budget_band"],
            "ReferenceRuntimeSessionArtifact.control_residue.last_budget_band",
        ),
        last_commitment_result_summary=_optional_non_empty_string(
            control_residue_payload["last_commitment_result_summary"],
            "ReferenceRuntimeSessionArtifact.control_residue.last_commitment_result_summary",
        ),
        last_realization_feedback=_optional_feedback(
            control_residue_payload["last_realization_feedback"],
            "ReferenceRuntimeSessionArtifact.control_residue.last_realization_feedback",
        ),
        feedback_window=_feedback_window(
            control_residue_payload["feedback_window"],
            "ReferenceRuntimeSessionArtifact.control_residue.feedback_window",
        ),
        executive_modulator_memory=_optional_executive_modulator_memory(
            control_residue_payload.get("executive_modulator_memory"),
            "ReferenceRuntimeSessionArtifact.control_residue.executive_modulator_memory",
        ),
    )
    return artifact.to_session()


def read_reference_runtime_session_artifact(path: Path) -> ReferenceRuntimeSession:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "read_reference_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return parse_reference_runtime_session_artifact(payload)


def write_reference_runtime_session_artifact(
    path: Path,
    session: ReferenceRuntimeSession,
) -> None:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "write_reference_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    if not path.parent.exists():
        raise FileNotFoundError(
            f"Reference runtime session artifact parent does not exist: {path.parent}"
        )

    artifact = build_reference_runtime_session_artifact(session)
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


def _require_control_residue_keys(payload: Mapping[str, Any]) -> None:
    actual_keys = tuple(payload.keys())
    if actual_keys == _CONTROL_RESIDUE_KEYS or actual_keys == _PRE_MODULATOR_CONTROL_RESIDUE_KEYS:
        return
    expected = f"{_CONTROL_RESIDUE_KEYS} or {_PRE_MODULATOR_CONTROL_RESIDUE_KEYS}"
    missing_keys = [key for key in _CONTROL_RESIDUE_KEYS if key not in payload]
    extra_keys = [key for key in actual_keys if key not in _CONTROL_RESIDUE_KEYS]
    raise ValueError(
        "ReferenceRuntimeSessionArtifact.control_residue keys must be exactly "
        f"{expected}; missing={missing_keys}, extra={extra_keys}."
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


def _optional_executive_modulator_memory(
    value: Any,
    label: str,
) -> ExecutiveModulatorMemory | None:
    if value is None:
        return None
    return _executive_modulator_memory(value, label)


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


def _executive_modulator_memory(value: Any, label: str) -> ExecutiveModulatorMemory:
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    memory_keys = (
        "focus_tonic",
        "explore_tonic",
        "stop_tonic",
        "update_tonic",
    )
    _require_exact_keys(value, memory_keys, label)
    memory = ExecutiveModulatorMemory(
        focus_tonic=_unit_float(value["focus_tonic"], f"{label}.focus_tonic"),
        explore_tonic=_unit_float(value["explore_tonic"], f"{label}.explore_tonic"),
        stop_tonic=_unit_float(value["stop_tonic"], f"{label}.stop_tonic"),
        update_tonic=_unit_float(value["update_tonic"], f"{label}.update_tonic"),
    )
    return canonicalize_executive_modulator_memory(memory)


def _unit_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be numeric, got {actual_type}.")
    parsed = float(value)
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0.")
    return parsed


def _soft_control_family(value: Any, label: str):
    from cortex.sre.families import SoftControlFamily

    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    try:
        return SoftControlFamily(value.strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a canonical soft-control family.") from exc


def _brake_state(value: Any, label: str):
    from cortex.sre.brake import BrakeState

    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    try:
        return BrakeState(value.strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a canonical brake state.") from exc


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


def _last_budget_band(budget_history: tuple[str, ...]) -> str | None:
    if not budget_history:
        return None
    last_budget_entry = budget_history[-1]
    if not last_budget_entry.startswith("shell-"):
        raise ValueError(
            "Reference runtime session artifact only supports shell budget history entries."
        )
    last_budget_band = last_budget_entry.replace("shell-", "", 1)
    if last_budget_band not in _ALLOWED_BUDGET_BANDS:
        raise ValueError(
            "Reference runtime session artifact only supports `shell-low`, "
            "`shell-medium`, and `shell-high` budget entries."
        )
    return last_budget_band


__all__ = [
    "ReferenceRuntimeSessionArtifact",
    "build_reference_runtime_session_artifact",
    "parse_reference_runtime_session_artifact",
    "read_reference_runtime_session_artifact",
    "write_reference_runtime_session_artifact",
]
