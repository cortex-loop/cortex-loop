from __future__ import annotations

import pytest

from cortex.sre.operator_routing import (
    OperatorRouteProfile,
    OperatorTaskMode,
    OperatorTaskState,
    build_operator_probe_task_state,
    build_operator_route_diagnostics,
    build_operator_task_state,
    select_operator_route,
)


def test_operator_task_state_requires_bounded_numeric_axes() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.00,
        quota_pressure=0.00,
        visible_burden_sensitivity=0.45,
    )

    assert state.as_vector() == (0.45, 0.05, 0.80, 0.45, 0.0, 0.0)

    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        OperatorTaskState(
            task_mode=OperatorTaskMode.EXECUTE,
            complexity=1.2,
            continuity_demand=0.05,
            verification_demand=0.80,
            uncertainty=0.45,
            host_friction=0.00,
            quota_pressure=0.00,
            visible_burden_sensitivity=0.45,
        )


def test_build_operator_task_state_uses_exact_scenario_defaults() -> None:
    execute_state = build_operator_task_state("pass_minimal")
    inspect_state = build_operator_task_state("truth_gap")
    continuity_state = build_operator_task_state("restart_continuity")

    assert execute_state.task_mode is OperatorTaskMode.EXECUTE
    assert execute_state.complexity == pytest.approx(0.45)
    assert execute_state.continuity_demand == pytest.approx(0.05)
    assert execute_state.verification_demand == pytest.approx(0.80)
    assert execute_state.visible_burden_sensitivity == pytest.approx(0.45)

    assert inspect_state.task_mode is OperatorTaskMode.INSPECT
    assert inspect_state.complexity == pytest.approx(0.20)
    assert inspect_state.verification_demand == pytest.approx(0.00)
    assert inspect_state.visible_burden_sensitivity == pytest.approx(0.80)

    assert continuity_state.task_mode is OperatorTaskMode.RESUME_EXECUTE
    assert continuity_state.continuity_demand == pytest.approx(0.95)
    assert continuity_state.verification_demand == pytest.approx(0.80)


def test_build_operator_task_state_applies_uncertainty_and_pressure_rules() -> None:
    calm = build_operator_task_state(
        "pass_minimal",
        recent_baseline_clean_count=2,
    )
    warning = build_operator_task_state(
        "pass_minimal",
        recent_warning_bearing_success_present=True,
    )
    blocked = build_operator_task_state(
        "pass_minimal",
        recent_probe_failure_class="quota_exhausted",
    )
    failed_before_completion = build_operator_task_state(
        "pass_minimal",
        previous_same_host_run_failed_before_completion=True,
        recent_baseline_clean_count=2,
    )

    assert calm.host_friction == pytest.approx(0.0)
    assert calm.quota_pressure == pytest.approx(0.0)

    assert warning.host_friction == pytest.approx(0.55)
    assert warning.quota_pressure == pytest.approx(0.60)

    assert blocked.host_friction == pytest.approx(0.85)
    assert blocked.quota_pressure == pytest.approx(0.90)

    assert failed_before_completion.uncertainty == pytest.approx(0.65)


def test_build_operator_probe_task_state_is_inspect_light_by_default() -> None:
    state = build_operator_probe_task_state(recent_baseline_clean_count=2)
    decision = select_operator_route(state)

    assert state.task_mode is OperatorTaskMode.INSPECT
    assert decision.profile is OperatorRouteProfile.INSPECT_LIGHT
    assert decision.budget.require_verification is False


def test_select_operator_route_prefers_default_execute_under_low_pressure() -> None:
    state = build_operator_task_state("pass_minimal", recent_baseline_clean_count=2)
    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.EXECUTE_STANDARD
    assert decision.blocked_reason is None
    assert decision.budget.max_turns == 1
    assert decision.budget.require_verification is True


def test_select_operator_route_can_choose_guarded_execute_under_higher_pressure() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.75,
        quota_pressure=0.60,
        visible_burden_sensitivity=0.45,
    )
    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.EXECUTE_GUARDED
    assert decision.blocked_reason is None


def test_select_operator_route_prefers_guarded_continuity_for_resumptive_host_friction() -> None:
    state = build_operator_task_state(
        "restart_continuity",
        recent_warning_bearing_success_present=True,
        recent_product_failure_class="capacity_exhausted",
    )
    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "blocked_by_quota_pressure"

    guarded_state = OperatorTaskState(
        task_mode=OperatorTaskMode.RESUME_EXECUTE,
        complexity=0.55,
        continuity_demand=0.95,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.75,
        quota_pressure=0.60,
        visible_burden_sensitivity=0.55,
    )
    guarded_decision = select_operator_route(guarded_state)

    assert guarded_decision.profile is OperatorRouteProfile.CONTINUITY_GUARDED
    assert "continuity:guarded-preferred" in guarded_decision.reason_tags


def test_select_operator_route_blocks_non_inspect_when_quota_is_high() -> None:
    state = build_operator_task_state(
        "pass_minimal",
        recent_probe_failure_class="quota_exhausted",
    )
    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "blocked_by_quota_pressure"
    assert decision.budget.max_turns == 0


def test_build_operator_route_diagnostics_exposes_state_and_budget() -> None:
    state = build_operator_task_state("truth_gap", recent_baseline_clean_count=2)
    decision = select_operator_route(state)
    payload = build_operator_route_diagnostics(state, decision)

    assert payload["route_profile"] == "inspect_light"
    assert payload["state_vector"] == [0.2, 0.0, 0.0, 0.35, 0.0, 0.0]
    assert payload["quota_pressure"] == 0.0
    assert payload["blocked_reason"] is None
    assert payload["route_budget"]["max_turns"] == 1
