"""Focused tests for direct Gemini runtime-step behavior."""

import pytest

from cortex.hosts.gemini.runtime import run_gemini_runtime_step


def test_gemini_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw Gemini host event name, not a canonical Cortex event name",
    ):
        run_gemini_runtime_step(
            "external/observation",
            {"session_id": "gm-bad", "interaction_id": "gm-int-1", "delta": "hello"},
        )


def test_gemini_runtime_step_surfaces_probe_unavailability_honestly() -> None:
    result = run_gemini_runtime_step(
        "content.delta",
        {"session_id": "gm-probe", "interaction_id": "gm-int-1", "delta": "hello"},
    )

    assert result.executive_state_summary["probe_path_state"] == "unavailable"
    assert (
        result.executive_state_summary["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_path_state"] == (
        "unavailable"
    )
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_result_class"] is None
