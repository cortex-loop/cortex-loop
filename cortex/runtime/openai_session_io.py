"""Bounded persisted product journal carrier for the OpenAI runtime shell."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from cortex.runtime.openai import OpenAIRuntimeSession

_ARTIFACT_KIND = "openai_product_journal"
_ARTIFACT_VERSION = 1
_TOP_LEVEL_KEYS = ("artifact_kind", "artifact_version", "journal")
_JOURNAL_KEYS = (
    "session_id",
    "event_index",
    "active_goal_ref",
    "pending_goal_refs",
    "confirmed_artifact_refs",
    "last_failure_class",
    "next_recommended_move",
)


@dataclass(frozen=True, slots=True)
class OpenAIRuntimeSessionArtifact:
    artifact_kind: str = _ARTIFACT_KIND
    artifact_version: int = _ARTIFACT_VERSION
    session_id: str | None = None
    event_index: int = 0
    active_goal_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = ()
    confirmed_artifact_refs: tuple[str, ...] = ()
    last_failure_class: str | None = None
    next_recommended_move: str = "continue"

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
            active_goal_ref=self.active_goal_ref,
            pending_goal_refs=self.pending_goal_refs,
            confirmed_artifact_refs=self.confirmed_artifact_refs,
            last_failure_class=self.last_failure_class,
            next_recommended_move=self.next_recommended_move,
        )

    def as_payload(self) -> dict[str, object]:
        return {
            "artifact_kind": self.artifact_kind,
            "artifact_version": self.artifact_version,
            "journal": {
                "session_id": self.session_id,
                "event_index": self.event_index,
                "active_goal_ref": self.active_goal_ref,
                "pending_goal_refs": list(self.pending_goal_refs),
                "confirmed_artifact_refs": list(self.confirmed_artifact_refs),
                "last_failure_class": self.last_failure_class,
                "next_recommended_move": self.next_recommended_move,
            },
        }

    def to_session(self) -> OpenAIRuntimeSession:
        return OpenAIRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            active_goal_ref=self.active_goal_ref,
            pending_goal_refs=self.pending_goal_refs,
            confirmed_artifact_refs=self.confirmed_artifact_refs,
            last_failure_class=self.last_failure_class,
            next_recommended_move=self.next_recommended_move,
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
        active_goal_ref=session.active_goal_ref,
        pending_goal_refs=session.pending_goal_refs,
        confirmed_artifact_refs=session.confirmed_artifact_refs,
        last_failure_class=session.last_failure_class,
        next_recommended_move=session.next_recommended_move,
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
    _require_exact_keys(
        journal_payload,
        _JOURNAL_KEYS,
        "OpenAIRuntimeSessionArtifact.journal",
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
        last_failure_class=_optional_non_empty_string(
            journal_payload["last_failure_class"],
            "OpenAIRuntimeSessionArtifact.journal.last_failure_class",
        ),
        next_recommended_move=_required_non_empty_string(
            journal_payload["next_recommended_move"],
            "OpenAIRuntimeSessionArtifact.journal.next_recommended_move",
        ),
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
    normalized: list[str] = []
    for index, item in enumerate(value):
        normalized.append(_required_non_empty_string(item, f"{label}[{index}]"))
    return tuple(normalized)


__all__ = [
    "OpenAIRuntimeSessionArtifact",
    "build_openai_runtime_session_artifact",
    "parse_openai_runtime_session_artifact",
    "read_openai_runtime_session_artifact",
    "write_openai_runtime_session_artifact",
]
