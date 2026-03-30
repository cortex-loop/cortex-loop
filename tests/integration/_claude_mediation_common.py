"""Shared Claude mediation helpers for deterministic evidence builders."""

from __future__ import annotations

from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE


def claude_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )

