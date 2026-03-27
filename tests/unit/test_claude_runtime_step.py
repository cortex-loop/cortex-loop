"""Focused tests for direct Claude runtime-step behavior."""

import pytest

from cortex.runtime.claude import run_claude_runtime_step


def test_claude_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw Claude host event name, not a canonical Cortex event name",
    ):
        run_claude_runtime_step(
            "external/observation",
            {"session_id": "cl-bad", "message_id": "cl-msg-1", "delta": "hello"},
        )
