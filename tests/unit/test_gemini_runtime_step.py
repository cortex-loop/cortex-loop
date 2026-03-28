"""Focused tests for direct Gemini runtime-step behavior."""

import pytest

from cortex.runtime.gemini import run_gemini_runtime_step


def test_gemini_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw Gemini host event name, not a canonical Cortex event name",
    ):
        run_gemini_runtime_step(
            "external/observation",
            {"session_id": "gm-bad", "interaction_id": "gm-int-1", "delta": "hello"},
        )
