from __future__ import annotations

import pytest

from cortex.runtime.operator_brain_capability import (
    operator_brain_capability_for_openai_model,
)
from cortex.sre.operator_routing import (
    OperatorBrainCapabilityMismatchLevel,
    OperatorRouteProfile,
    OperatorTaskMode,
    OperatorTaskState,
    build_operator_route_diagnostics,
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


def test_select_operator_route_prefers_default_execute_under_low_pressure() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.45,
    )
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
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.RESUME_EXECUTE,
        complexity=0.55,
        continuity_demand=0.95,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.85,
        quota_pressure=0.90,
        visible_burden_sensitivity=0.55,
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
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.85,
        quota_pressure=0.90,
        visible_burden_sensitivity=0.45,
    )
    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "blocked_by_quota_pressure"
    assert decision.budget.max_turns == 0


def test_build_operator_route_diagnostics_exposes_state_and_budget() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.INSPECT,
        complexity=0.20,
        continuity_demand=0.00,
        verification_demand=0.00,
        uncertainty=0.35,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.80,
    )
    decision = select_operator_route(state)
    payload = build_operator_route_diagnostics(state, decision)

    assert payload["route_profile"] == "inspect_light"
    assert payload["state_vector"] == [0.2, 0.0, 0.0, 0.35, 0.0, 0.0]
    assert payload["quota_pressure"] == 0.0
    assert payload["visible_burden_sensitivity"] == 0.8
    assert payload["contract_binding_demand"] == 0.0
    assert payload["brain_capability_band"] == "standard"
    assert payload["brain_capability_mismatch"]["level"] == "none"
    assert payload["contract_binding_profile"] == "standard"
    assert payload["blocked_reason"] is None
    assert payload["route_budget"]["max_turns"] == 1
    assert payload["modulator_state"] == {
        "focus_gain": 0.0,
        "explore_gain": 0.0,
        "stop_pressure": 0.0,
        "update_pressure": 0.0,
    }
    assert payload["modulator_reason_tags"] == []


def test_select_operator_route_downshifts_continuity_for_bounded_brain_degrade() -> None:
    _band, bounded = operator_brain_capability_for_openai_model(
        "gpt-5.3-codex-spark"
    )
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.RESUME_EXECUTE,
        complexity=0.55,
        continuity_demand=0.85,
        verification_demand=0.80,
        uncertainty=0.45,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.55,
        contract_binding_demand=0.30,
        brain_capability=bounded,
    )

    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.EXECUTE_STANDARD
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.DEGRADE
    )
    assert decision.brain_capability_assessment.contract_binding_profile.value == "lean"
    assert "brain-capability:continuity-downshift" in decision.reason_tags
    assert decision.budget.allow_extra_read_pass is False
    assert decision.blocked_reason is None


def test_select_operator_route_blocks_when_bounded_brain_mismatch_is_over_floor() -> None:
    _band, bounded = operator_brain_capability_for_openai_model(
        "gpt-5.3-codex-spark"
    )
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.10,
        verification_demand=0.90,
        uncertainty=0.45,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.45,
        contract_binding_demand=0.80,
        brain_capability=bounded,
    )

    decision = select_operator_route(state)

    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "brain_capability_mismatch"
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    )
    assert decision.brain_capability_assessment.fallback_family == "check"
    assert "brain-capability:unsupported-floor" in decision.reason_tags
