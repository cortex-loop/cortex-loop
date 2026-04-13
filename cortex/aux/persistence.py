"""Bounded AUX persistence for explicit support-memory episodes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.goals import normalize_continuity_reminder


DEFAULT_SUPPORT_MEMORY_STORE_PATH = Path(".cortex/aux/support_memory.sqlite3")
_PLAIN_TEXT_REMINDER = "plain-text-reminder"
_EPISODE_SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    episode_fingerprint TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    host_name TEXT NOT NULL,
    source_label TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_episodes_host_recorded_at
ON episodes(host_name, recorded_at);
CREATE INDEX IF NOT EXISTS idx_episodes_source_recorded_at
ON episodes(source_label, recorded_at);
"""


def _require_text(value: str, *, field_name: str) -> str:
    if not (isinstance(value, str) and value.strip()):
        raise ValueError(f"{field_name} must be non-empty after trimming.")
    return value.strip()


def _require_text_tuple(values: tuple[str, ...], *, field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        actual_type = type(values).__name__
        raise TypeError(f"{field_name} must be tuple[str, ...], got {actual_type}.")
    return tuple(_require_text(value, field_name=field_name) for value in values)


def _dedupe_ordered(values: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


def _metadata_keys(metadata: tuple[MetadataField, ...]) -> tuple[str, ...]:
    return tuple(sorted({field.key for field in metadata}))


def _bounded_reminders(reminders: tuple[str, ...]) -> tuple[str, ...]:
    bounded: list[str] = []
    for reminder in reminders:
        normalized = normalize_continuity_reminder(reminder)
        if normalized is not None:
            bounded.append(normalized)
            continue
        bounded.append(_PLAIN_TEXT_REMINDER)
    return _dedupe_ordered(tuple(bounded))


@dataclass(frozen=True, slots=True)
class SupportEventSignature:
    native_event_name: str
    payload_kind: str
    payload_metadata_keys: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.native_event_name,
            field_name="SupportEventSignature.native_event_name",
        )
        _require_text(
            self.payload_kind,
            field_name="SupportEventSignature.payload_kind",
        )
        _require_text_tuple(
            self.payload_metadata_keys,
            field_name="SupportEventSignature.payload_metadata_keys",
        )


@dataclass(frozen=True, slots=True)
class _SupportReferenceProjection:
    reference_kind: str
    reference_id: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata_keys: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.reference_kind,
            field_name="_SupportReferenceProjection.reference_kind",
        )
        _require_text(
            self.reference_id,
            field_name="_SupportReferenceProjection.reference_id",
        )
        _require_text_tuple(
            self.tags,
            field_name="_SupportReferenceProjection.tags",
        )
        _require_text_tuple(
            self.metadata_keys,
            field_name="_SupportReferenceProjection.metadata_keys",
        )

    def as_support_reference(self) -> SupportReference:
        return SupportReference(
            self.reference_kind,
            self.reference_id,
            tags=frozenset(self.tags),
            metadata=tuple(MetadataField(key, key) for key in self.metadata_keys),
        )


@dataclass(frozen=True, slots=True)
class SupportMemoryEpisode:
    episode_fingerprint: str
    recorded_at: str
    host_name: str
    source_label: str
    event_signatures: tuple[SupportEventSignature, ...] = field(default_factory=tuple)
    candidate_refs: tuple[str, ...] = field(default_factory=tuple)
    wake_reason_tags: tuple[str, ...] = field(default_factory=tuple)
    degradation_reason_codes: tuple[str, ...] = field(default_factory=tuple)
    contradiction_source_tags: tuple[str, ...] = field(default_factory=tuple)
    contradiction_evidence_tags: tuple[str, ...] = field(default_factory=tuple)
    branch_registry: tuple[str, ...] = field(default_factory=tuple)
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    role_view_tags: tuple[str, ...] = field(default_factory=tuple)
    budget_history: tuple[str, ...] = field(default_factory=tuple)
    brake_history: tuple[str, ...] = field(default_factory=tuple)
    reminders: tuple[str, ...] = field(default_factory=tuple)
    host_affordance_tags: tuple[str, ...] = field(default_factory=tuple)
    host_approval_boundary_tags: tuple[str, ...] = field(default_factory=tuple)
    host_constraint_tags: tuple[str, ...] = field(default_factory=tuple)
    host_metadata_keys: tuple[str, ...] = field(default_factory=tuple)
    published_memory_refs: tuple[_SupportReferenceProjection, ...] = field(default_factory=tuple)
    artifact_refs: tuple[_SupportReferenceProjection, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.episode_fingerprint,
            field_name="SupportMemoryEpisode.episode_fingerprint",
        )
        _require_text(
            self.recorded_at,
            field_name="SupportMemoryEpisode.recorded_at",
        )
        _require_text(
            self.host_name,
            field_name="SupportMemoryEpisode.host_name",
        )
        _require_text(
            self.source_label,
            field_name="SupportMemoryEpisode.source_label",
        )
        if any(not isinstance(event, SupportEventSignature) for event in self.event_signatures):
            raise TypeError(
                "SupportMemoryEpisode.event_signatures must contain only SupportEventSignature instances."
            )
        for field_name in (
            "candidate_refs",
            "wake_reason_tags",
            "degradation_reason_codes",
            "contradiction_source_tags",
            "contradiction_evidence_tags",
            "branch_registry",
            "pending_goal_refs",
            "role_view_tags",
            "budget_history",
            "brake_history",
            "reminders",
            "host_affordance_tags",
            "host_approval_boundary_tags",
            "host_constraint_tags",
            "host_metadata_keys",
        ):
            _require_text_tuple(
                getattr(self, field_name),
                field_name=f"SupportMemoryEpisode.{field_name}",
            )
        if any(
            not isinstance(reference, _SupportReferenceProjection)
            for reference in self.published_memory_refs
        ):
            raise TypeError(
                "SupportMemoryEpisode.published_memory_refs must contain only _SupportReferenceProjection instances."
            )
        if any(
            not isinstance(reference, _SupportReferenceProjection)
            for reference in self.artifact_refs
        ):
            raise TypeError(
                "SupportMemoryEpisode.artifact_refs must contain only _SupportReferenceProjection instances."
            )

    def payload_dict(self) -> dict[str, object]:
        return {
            "event_signatures": [
                {
                    "native_event_name": event.native_event_name,
                    "payload_kind": event.payload_kind,
                    "payload_metadata_keys": list(event.payload_metadata_keys),
                }
                for event in self.event_signatures
            ],
            "candidate_refs": list(self.candidate_refs),
            "wake_reason_tags": list(self.wake_reason_tags),
            "degradation_reason_codes": list(self.degradation_reason_codes),
            "contradiction_source_tags": list(self.contradiction_source_tags),
            "contradiction_evidence_tags": list(self.contradiction_evidence_tags),
            "branch_registry": list(self.branch_registry),
            "pending_goal_refs": list(self.pending_goal_refs),
            "role_view_tags": list(self.role_view_tags),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "reminders": list(self.reminders),
            "host_affordance_tags": list(self.host_affordance_tags),
            "host_approval_boundary_tags": list(self.host_approval_boundary_tags),
            "host_constraint_tags": list(self.host_constraint_tags),
            "host_metadata_keys": list(self.host_metadata_keys),
            "published_memory_refs": [
                {
                    "reference_kind": reference.reference_kind,
                    "reference_id": reference.reference_id,
                    "tags": list(reference.tags),
                    "metadata_keys": list(reference.metadata_keys),
                }
                for reference in self.published_memory_refs
            ],
            "artifact_refs": [
                {
                    "reference_kind": reference.reference_kind,
                    "reference_id": reference.reference_id,
                    "tags": list(reference.tags),
                    "metadata_keys": list(reference.metadata_keys),
                }
                for reference in self.artifact_refs
            ],
        }

    @classmethod
    def from_payload(
        cls,
        *,
        episode_fingerprint: str,
        recorded_at: str,
        host_name: str,
        source_label: str,
        payload: dict[str, object],
    ) -> "SupportMemoryEpisode":
        def _projection_rows(name: str) -> tuple[_SupportReferenceProjection, ...]:
            rows = payload.get(name, [])
            if not isinstance(rows, list):
                raise TypeError(f"{name} must be a list in persisted payload.")
            return tuple(
                _SupportReferenceProjection(
                    reference_kind=str(row["reference_kind"]),
                    reference_id=str(row["reference_id"]),
                    tags=tuple(str(value) for value in row.get("tags", [])),
                    metadata_keys=tuple(str(value) for value in row.get("metadata_keys", [])),
                )
                for row in rows
                if isinstance(row, dict)
            )

        return cls(
            episode_fingerprint=episode_fingerprint,
            recorded_at=recorded_at,
            host_name=host_name,
            source_label=source_label,
            event_signatures=tuple(
                SupportEventSignature(
                    native_event_name=str(row["native_event_name"]),
                    payload_kind=str(row["payload_kind"]),
                    payload_metadata_keys=tuple(
                        str(value) for value in row.get("payload_metadata_keys", [])
                    ),
                )
                for row in payload.get("event_signatures", [])
                if isinstance(row, dict)
            ),
            candidate_refs=tuple(str(value) for value in payload.get("candidate_refs", [])),
            wake_reason_tags=tuple(str(value) for value in payload.get("wake_reason_tags", [])),
            degradation_reason_codes=tuple(
                str(value) for value in payload.get("degradation_reason_codes", [])
            ),
            contradiction_source_tags=tuple(
                str(value) for value in payload.get("contradiction_source_tags", [])
            ),
            contradiction_evidence_tags=tuple(
                str(value) for value in payload.get("contradiction_evidence_tags", [])
            ),
            branch_registry=tuple(str(value) for value in payload.get("branch_registry", [])),
            pending_goal_refs=tuple(str(value) for value in payload.get("pending_goal_refs", [])),
            role_view_tags=tuple(str(value) for value in payload.get("role_view_tags", [])),
            budget_history=tuple(str(value) for value in payload.get("budget_history", [])),
            brake_history=tuple(str(value) for value in payload.get("brake_history", [])),
            reminders=tuple(str(value) for value in payload.get("reminders", [])),
            host_affordance_tags=tuple(
                str(value) for value in payload.get("host_affordance_tags", [])
            ),
            host_approval_boundary_tags=tuple(
                str(value) for value in payload.get("host_approval_boundary_tags", [])
            ),
            host_constraint_tags=tuple(
                str(value) for value in payload.get("host_constraint_tags", [])
            ),
            host_metadata_keys=tuple(
                str(value) for value in payload.get("host_metadata_keys", [])
            ),
            published_memory_refs=_projection_rows("published_memory_refs"),
            artifact_refs=_projection_rows("artifact_refs"),
        )


def _reference_projection(reference: SupportReference) -> _SupportReferenceProjection:
    return _SupportReferenceProjection(
        reference_kind=reference.reference_kind,
        reference_id=reference.reference_id,
        tags=tuple(sorted(reference.tags)),
        metadata_keys=_metadata_keys(reference.metadata),
    )


def _event_signature_payload_keys(snapshot: SupportSnapshot, event_index: int) -> tuple[str, ...]:
    event = snapshot.trace.recent_events[event_index]
    event_metadata = _metadata_keys(event.payload_metadata)
    handle_metadata = ()
    if event.payload_handle is not None:
        handle_metadata = _metadata_keys(event.payload_handle.metadata)
    return tuple(sorted(set(event_metadata) | set(handle_metadata)))


def _episode_payload_dict(
    snapshot: SupportSnapshot,
) -> dict[str, object]:
    event_signatures = tuple(
        SupportEventSignature(
            native_event_name=event.native_event_name,
            payload_kind=(
                event.payload_handle.payload_kind
                if event.payload_handle is not None
                else "none"
            ),
            payload_metadata_keys=_event_signature_payload_keys(snapshot, index),
        )
        for index, event in enumerate(snapshot.trace.recent_events)
    )
    contradiction_source_tags = tuple(
        contradiction.source_tag
        for record in snapshot.trace.degradation_records
        for contradiction in record.contradiction_records
    )
    contradiction_evidence_tags = tuple(
        tag
        for record in snapshot.trace.degradation_records
        for contradiction in record.contradiction_records
        for tag in contradiction.evidence_tags
    )
    return SupportMemoryEpisode(
        episode_fingerprint="placeholder",
        recorded_at="placeholder",
        host_name="placeholder",
        source_label="placeholder",
        event_signatures=event_signatures,
        candidate_refs=_dedupe_ordered(snapshot.trace.candidate_refs),
        wake_reason_tags=_dedupe_ordered(
            tuple(receipt.reason_tag for receipt in snapshot.trace.wake_receipts)
        ),
        degradation_reason_codes=_dedupe_ordered(
            tuple(record.reason_code for record in snapshot.trace.degradation_records)
        ),
        contradiction_source_tags=_dedupe_ordered(contradiction_source_tags),
        contradiction_evidence_tags=_dedupe_ordered(contradiction_evidence_tags),
        branch_registry=_dedupe_ordered(snapshot.session.branch_registry),
        pending_goal_refs=_dedupe_ordered(snapshot.session.pending_goal_refs),
        role_view_tags=tuple(sorted(snapshot.session.role_view_tags)),
        budget_history=_dedupe_ordered(snapshot.session.budget_history),
        brake_history=_dedupe_ordered(snapshot.session.brake_history),
        reminders=_bounded_reminders(snapshot.session.reminders),
        host_affordance_tags=tuple(sorted(snapshot.host.affordance_tags)),
        host_approval_boundary_tags=tuple(sorted(snapshot.host.approval_boundary_tags)),
        host_constraint_tags=tuple(sorted(snapshot.host.constraint_tags)),
        host_metadata_keys=_metadata_keys(snapshot.host.metadata),
        published_memory_refs=tuple(
            _reference_projection(reference)
            for reference in snapshot.exec_memory_pub.published_memory_refs
        ),
        artifact_refs=tuple(
            _reference_projection(reference)
            for reference in snapshot.exec_memory_pub.artifact_refs
        ),
    ).payload_dict()


def episode_from_support_snapshot(
    snapshot: SupportSnapshot,
    *,
    host_name: str,
    source_label: str,
    recorded_at: str | None = None,
) -> SupportMemoryEpisode:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "episode_from_support_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    host_name = _require_text(host_name, field_name="episode_from_support_snapshot.host_name")
    source_label = _require_text(
        source_label,
        field_name="episode_from_support_snapshot.source_label",
    )
    recorded_at = recorded_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = _episode_payload_dict(snapshot)
    fingerprint_payload = {
        "host_name": host_name,
        "source_label": source_label,
        "payload": payload,
    }
    episode_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return SupportMemoryEpisode.from_payload(
        episode_fingerprint=episode_fingerprint,
        recorded_at=recorded_at,
        host_name=host_name,
        source_label=source_label,
        payload=payload,
    )


class SqliteSupportMemoryStore:
    """Durable AUX-only store for bounded support-memory episodes."""

    def __init__(self, path: str | Path = DEFAULT_SUPPORT_MEMORY_STORE_PATH) -> None:
        self.path = path if isinstance(path, str) else Path(path)
        self._connection: sqlite3.Connection | None = None
        if self.path == ":memory:":
            self._connection = sqlite3.connect(":memory:")
            self._connection.row_factory = sqlite3.Row
            self._connection.executescript(_EPISODE_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        if self._connection is not None:
            return self._connection
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(self.path))
        connection.row_factory = sqlite3.Row
        connection.executescript(_EPISODE_SCHEMA)
        return connection

    def insert_episode(self, episode: SupportMemoryEpisode) -> bool:
        if not isinstance(episode, SupportMemoryEpisode):
            actual_type = type(episode).__name__
            raise TypeError(
                "SqliteSupportMemoryStore.insert_episode() requires SupportMemoryEpisode, "
                f"got {actual_type}.",
            )
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO episodes(
                    episode_fingerprint,
                    recorded_at,
                    host_name,
                    source_label,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    episode.episode_fingerprint,
                    episode.recorded_at,
                    episode.host_name,
                    episode.source_label,
                    json.dumps(
                        episode.payload_dict(),
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                ),
            )
            connection.commit()
            return cursor.rowcount > 0

    def load_episodes(
        self,
        *,
        host_name: str,
        source_label: str | None = None,
        horizon_hours: int = 72,
        limit: int = 32,
        now: datetime | None = None,
    ) -> tuple[SupportMemoryEpisode, ...]:
        host_name = _require_text(host_name, field_name="SqliteSupportMemoryStore.load_episodes.host_name")
        if source_label is not None:
            source_label = _require_text(
                source_label,
                field_name="SqliteSupportMemoryStore.load_episodes.source_label",
            )
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("SqliteSupportMemoryStore.load_episodes.limit must be positive int.")
        if isinstance(horizon_hours, bool) or not isinstance(horizon_hours, int) or horizon_hours <= 0:
            raise ValueError(
                "SqliteSupportMemoryStore.load_episodes.horizon_hours must be positive int."
            )
        current_time = now or datetime.now(timezone.utc)
        since = current_time - timedelta(hours=horizon_hours)
        params: list[object] = [host_name, since.isoformat(timespec="seconds")]
        query = """
            SELECT episode_fingerprint, recorded_at, host_name, source_label, payload_json
            FROM episodes
            WHERE host_name = ? AND recorded_at >= ?
        """
        if source_label is not None:
            query += " AND source_label = ?"
            params.append(source_label)
        query += " ORDER BY recorded_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as connection:
            rows = tuple(connection.execute(query, tuple(params)))
        episodes = [
            SupportMemoryEpisode.from_payload(
                episode_fingerprint=str(row["episode_fingerprint"]),
                recorded_at=str(row["recorded_at"]),
                host_name=str(row["host_name"]),
                source_label=str(row["source_label"]),
                payload=json.loads(str(row["payload_json"])),
            )
            for row in rows
        ]
        episodes.reverse()
        return tuple(episodes)


__all__ = [
    "DEFAULT_SUPPORT_MEMORY_STORE_PATH",
    "SqliteSupportMemoryStore",
    "SupportEventSignature",
    "SupportMemoryEpisode",
    "episode_from_support_snapshot",
]
