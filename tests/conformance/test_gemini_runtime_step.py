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
    assert tuple(result.control_ledger_summary["audit_projection"]) == (
        "selected_family",
        "realized_family",
        "dominant_uncertainty_sources",
        "activation_threshold",
        "selected_delta_over_neutral",
        "rejected_cheaper_families",
        "verification_state",
        "explainability_profile",
        "probe_path_state",
        "probe_result_class",
        "probe_unavailable_reason",
    )
    assert result.control_ledger_summary["audit_projection"]["explainability_profile"] == (
        "focused"
    )


def test_gemini_runtime_step_can_raise_audit_projection_from_explicit_request() -> None:
    result = run_gemini_runtime_step(
        "content.delta",
        {"session_id": "gm-audit", "interaction_id": "gm-int-1", "delta": "hello"},
        audit_intensity="structured",
    )

    projection = result.control_ledger_summary["audit_projection"]

    assert projection["selected_family"] == result.control_ledger_summary["selected_family"]
    assert projection["realized_family"] == result.control_ledger_summary["realized_family"]
    assert projection["dominant_uncertainty_sources"] == ["host-capability", "environment"]
    assert projection["rejected_cheaper_families"] == ["neutral", "check"]
    assert projection["verification_state"] == "not-required"
    assert projection["explainability_profile"] == "structured"
    assert projection["probe_path_state"] == "unavailable"
    assert projection["probe_result_class"] is None
    assert projection["probe_unavailable_reason"] == "documented-probe-surface-unavailable"
