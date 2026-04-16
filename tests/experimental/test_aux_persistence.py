"""Focused tests for bounded AUX persistence episodes and SQLite storage."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import sqlite3

import pytest

from cortex.aux.persistence import (
    SqliteSupportMemoryStore,
    SupportMemoryEpisode,
    episode_from_support_snapshot,
)
from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.support import (
    SupportExecMemoryState,
    SupportHostState,
    SupportReference,
    SupportSessionState,
    SupportSnapshot,
    SupportTraceState,
)
from cortex.sre.goals import make_resume_reminder

from ._aux_test_support import make_temporal_support_snapshot


def test_episode_from_support_snapshot_excludes_payload_text_and_metadata_values() -> None:
    snapshot = SupportSnapshot(
        trace=SupportTraceState(
            recent_events=(
                LifecycleEventEnvelope(
                    native_event_name="turn/complete",
                    payload_metadata=(MetadataField("secret-key", "secret-value"),),
                    payload_handle=EventPayloadHandle(
                        payload_kind="host-payload",
                        metadata=(MetadataField("handle-key", "handle-value"),),
                    ),
                ),
            ),
            candidate_refs=("candidate-alpha",),
            degradation_records=(
                DegradationRecord(
                    reason_code="host-degraded",
                    contradiction_records=(
                        ContradictionRecord(
                            source_tag="host/runtime",
                            summary="sensitive contradiction summary text",
                            evidence_tags=frozenset({"capability-drift"}),
                        ),
                    ),
                ),
            ),
        ),
        session=SupportSessionState(
            branch_registry=("main", "review-track"),
            pending_goal_refs=("goal-alpha",),
            reminders=("review deployment after meeting", make_resume_reminder("review-track")),
        ),
        host=SupportHostState(
            affordance_tags=frozenset({"tool/intercept"}),
            metadata=(MetadataField("host-note", "private-host-value"),),
        ),
        exec_memory_pub=SupportExecMemoryState(
            published_memory_refs=(
                SupportReference(
                    "memory",
                    "memo-alpha",
                    metadata=(MetadataField("memory-key", "memory-value"),),
                ),
            ),
        ),
    )

    episode = episode_from_support_snapshot(
        snapshot,
        host_name="reference",
        source_label="tests/experimental/test_aux_persistence",
    )
    payload_json = json.dumps(episode.payload_dict(), sort_keys=True)

    assert isinstance(episode, SupportMemoryEpisode)
    assert episode.event_signatures[0].payload_metadata_keys == ("handle-key", "secret-key")
    assert episode.reminders == ("plain-text-reminder", make_resume_reminder("review-track"))
    assert "secret-value" not in payload_json
    assert "handle-value" not in payload_json
    assert "sensitive contradiction summary text" not in payload_json
    assert "review deployment after meeting" not in payload_json
    assert "private-host-value" not in payload_json
    assert "memory-value" not in payload_json


def test_sqlite_support_memory_store_round_trips_dedupes_and_filters(tmp_path) -> None:
    store = SqliteSupportMemoryStore(tmp_path / "support_memory.sqlite3")
    recent_snapshot = make_temporal_support_snapshot(
        "recent-support",
        published_memory_refs=("memo-a",),
    )
    old_snapshot = make_temporal_support_snapshot(
        "old-support",
        published_memory_refs=("memo-old",),
    )

    recent_episode = episode_from_support_snapshot(
        recent_snapshot,
        host_name="reference",
        source_label="tests/recent",
        recorded_at="2026-04-14T00:00:00+00:00",
    )
    duplicate_episode = episode_from_support_snapshot(
        recent_snapshot,
        host_name="reference",
        source_label="tests/recent",
        recorded_at="2026-04-14T01:00:00+00:00",
    )
    old_episode = episode_from_support_snapshot(
        old_snapshot,
        host_name="reference",
        source_label="tests/old",
        recorded_at="2026-04-01T00:00:00+00:00",
    )
    other_host_episode = episode_from_support_snapshot(
        recent_snapshot,
        host_name="claude",
        source_label="tests/recent",
        recorded_at="2026-04-14T00:00:00+00:00",
    )

    assert store.insert_episode(recent_episode) is True
    assert store.insert_episode(duplicate_episode) is False
    assert store.insert_episode(old_episode) is True
    assert store.insert_episode(other_host_episode) is True

    episodes = store.load_episodes(
        host_name="reference",
        source_label="tests/recent",
        horizon_hours=72,
        now=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert episodes == (recent_episode,)


def test_sqlite_support_memory_store_memory_path_persists_within_store_instance() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    episode = episode_from_support_snapshot(
        make_temporal_support_snapshot(
            "memory-store",
            published_memory_refs=("memo-a",),
        ),
        host_name="reference",
        source_label="tests/in-memory",
    )

    assert store.insert_episode(episode) is True
    assert store.load_episodes(host_name="reference", source_label="tests/in-memory") == (
        episode,
    )
    store.close()
    store.close()


def test_episode_from_support_snapshot_rejects_naive_recorded_at() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        episode_from_support_snapshot(
            make_temporal_support_snapshot(
                "naive-recorded-at",
                published_memory_refs=("memo-a",),
            ),
            host_name="reference",
            source_label="tests/naive-recorded-at",
            recorded_at="2026-04-14T00:00:00",
        )


def test_sqlite_support_memory_store_uses_absolute_time_for_offset_timestamps(tmp_path) -> None:
    store = SqliteSupportMemoryStore(tmp_path / "support_memory.sqlite3")
    episode = episode_from_support_snapshot(
        make_temporal_support_snapshot(
            "offset-support",
            published_memory_refs=("memo-a",),
        ),
        host_name="reference",
        source_label="tests/offset",
        recorded_at="2026-04-14T08:00:00+09:00",
    )

    assert episode.recorded_at == "2026-04-13T23:00:00+00:00"
    assert store.insert_episode(episode) is True

    assert store.load_episodes(
        host_name="reference",
        source_label="tests/offset",
        horizon_hours=12,
        now=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
    ) == ()
    assert store.load_episodes(
        host_name="reference",
        source_label="tests/offset",
        horizon_hours=14,
        now=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
    ) == (episode,)


def test_sqlite_support_memory_store_backfills_legacy_recorded_at_epoch(tmp_path) -> None:
    path = tmp_path / "legacy_support_memory.sqlite3"
    episode = episode_from_support_snapshot(
        make_temporal_support_snapshot(
            "legacy-offset-support",
            published_memory_refs=("memo-a",),
        ),
        host_name="reference",
        source_label="tests/legacy",
    )
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE episodes (
            episode_fingerprint TEXT PRIMARY KEY,
            recorded_at TEXT NOT NULL,
            host_name TEXT NOT NULL,
            source_label TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO episodes(
            episode_fingerprint,
            recorded_at,
            host_name,
            source_label,
            payload_json
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            episode.episode_fingerprint,
            "2026-04-14T08:00:00+09:00",
            episode.host_name,
            episode.source_label,
            json.dumps(episode.payload_dict(), sort_keys=True, separators=(",", ":")),
        ),
    )
    connection.commit()
    connection.close()

    store = SqliteSupportMemoryStore(path)
    loaded = store.load_episodes(
        host_name="reference",
        source_label="tests/legacy",
        horizon_hours=14,
        now=datetime(2026, 4, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert len(loaded) == 1
    assert loaded[0].recorded_at == "2026-04-13T23:00:00+00:00"

    connection = sqlite3.connect(path)
    row = connection.execute(
        "SELECT recorded_at, recorded_at_epoch FROM episodes"
    ).fetchone()
    connection.close()
    assert row == ("2026-04-13T23:00:00+00:00", 1776121200)


def test_sqlite_support_memory_store_closes_on_disk_connections_per_operation(tmp_path) -> None:
    store = SqliteSupportMemoryStore(tmp_path / "support_memory.sqlite3")
    episode = episode_from_support_snapshot(
        make_temporal_support_snapshot(
            "fd-support",
            published_memory_refs=("memo-a",),
        ),
        host_name="reference",
        source_label="tests/fd",
    )
    baseline_fd_count = len(os.listdir("/dev/fd"))

    for _ in range(10):
        store.insert_episode(episode)
        store.load_episodes(host_name="reference", source_label="tests/fd")

    assert len(os.listdir("/dev/fd")) == baseline_fd_count
