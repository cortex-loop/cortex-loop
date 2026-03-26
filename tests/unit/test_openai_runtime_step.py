"""Focused tests for direct OpenAI runtime-step behavior."""

import pytest

from cortex.runtime.openai import run_openai_runtime_step


def test_openai_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw OpenAI host event name, not a canonical Cortex event name",
    ):
        run_openai_runtime_step(
            "external/observation",
            {"session_id": "oa-bad", "response_id": "resp-1", "delta": "hello"},
        )
