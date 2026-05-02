"""Product tests for bounded expectation-debt control pressure."""

from __future__ import annotations

from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.debt_control import DebtControlPressure, build_debt_control_pressure
from cortex.sre.executive_summary import ExecutiveSignalSummary
from cortex.sre.expectations import ResolutionDeficitState
from cortex.sre.goal_debt import GoalDebtState
from cortex.sre.modulators import (
    ExecutiveModulatorState,
    ExecutiveModulatorUpdate,
    ZERO_EXECUTIVE_MODULATOR_MEMORY,
)
from cortex.sre.operator_routing import (
    OperatorRouteProfile,
    OperatorTaskMode,
    OperatorTaskState,
    select_operator_route_with_policy,
)
from cortex.sre.policy_view import build_executive_policy_view


def test_unpaid_immediate_debt_raises_bounded_control_pressure() -> None:
    pressure = build_debt_control_pressure(
        resolution_deficit=ResolutionDeficitState(
            due_weight=1.0,
            overdue_weight=1.0,
            negative_prediction_error=1.0,
            dominant_deficit_kind="verification",
        ),
        goal_debt=GoalDebtState(
            unfinished_goal_debt=1.0,
            contradiction_rejection_debt=0.0,
            verification_debt=1.0,
            quota_burden_stop_pressure=0.0,
        ),
        task_mode=OperatorTaskMode.EXECUTE,
    )

    assert pressure.resolution_pressure == 1.0
    assert pressure.forward_commit_pressure == 1.0
    assert pressure.goal_drag > 0.0
    assert pressure.debt_pressure > 0.90
    assert "resolution-deficit" in pressure.reason_tags
    assert "goal-drag" in pressure.reason_tags


def test_waiting_and_relieved_states_stay_neutral() -> None:
    pressure = build_debt_control_pressure(
        resolution_deficit=ResolutionDeficitState(
            suspended_weight=1.0,
            relief_weight=1.0,
            negative_prediction_error=0.0,
        ),
        goal_debt=GoalDebtState(
            unfinished_goal_debt=0.0,
            contradiction_rejection_debt=0.0,
            verification_debt=0.0,
            quota_burden_stop_pressure=0.0,
        ),
        task_mode=OperatorTaskMode.EXECUTE,
    )

    assert pressure.debt_pressure == 0.0
    assert pressure.goal_drag == 0.0


def test_quota_burden_does_not_create_truth_engagement_debt() -> None:
    base = build_debt_control_pressure(
        resolution_deficit=ResolutionDeficitState(),
        goal_debt=GoalDebtState(
            unfinished_goal_debt=0.0,
            contradiction_rejection_debt=0.0,
            verification_debt=0.0,
            quota_burden_stop_pressure=0.0,
        ),
        task_mode=OperatorTaskMode.EXECUTE,
    )
    quota_only = build_debt_control_pressure(
        resolution_deficit=ResolutionDeficitState(),
        goal_debt=GoalDebtState(
            unfinished_goal_debt=0.0,
            contradiction_rejection_debt=0.0,
            verification_debt=0.0,
            quota_burden_stop_pressure=1.0,
        ),
        task_mode=OperatorTaskMode.EXECUTE,
    )

    assert quota_only.debt_pressure == base.debt_pressure == 0.0
    assert quota_only.goal_drag == base.goal_drag == 0.0


def test_inspect_context_is_not_punished_by_goal_drag() -> None:
    pressure = build_debt_control_pressure(
        resolution_deficit=ResolutionDeficitState(
            due_weight=1.0,
            overdue_weight=1.0,
            negative_prediction_error=1.0,
            dominant_deficit_kind="verification",
        ),
        goal_debt=GoalDebtState(
            unfinished_goal_debt=1.0,
            contradiction_rejection_debt=0.0,
            verification_debt=1.0,
            quota_burden_stop_pressure=0.0,
        ),
        task_mode=OperatorTaskMode.INSPECT,
    )

    assert pressure.forward_commit_pressure == 0.0
    assert pressure.goal_drag == 0.0
    assert pressure.verification_relief_bias > 0.0


def test_debt_can_guard_brake_but_cannot_latch_by_itself() -> None:
    pressure = DebtControlPressure(
        resolution_pressure=1.0,
        persistence=1.0,
        forward_commit_pressure=1.0,
        goal_drag=1.0,
        debt_pressure=1.0,
    )

    evaluation = evaluate_brake_state((), debt_control_pressure=pressure)

    assert evaluation.state is BrakeState.GUARDED
    assert evaluation.dominant_cause == "resolution-deficit"


def test_debt_policy_biases_execute_route_to_guarded_without_blocking() -> None:
    summary = ExecutiveSignalSummary(
        uncertainty=0.2,
        repeated_failure_pressure=0.0,
        quota_pressure=0.0,
        continuity_demand=0.05,
        novelty_pressure=0.2,
        verification_conflict_pressure=0.0,
    )
    modulator_state = ExecutiveModulatorState(
        focus_gain=0.0,
        explore_gain=0.0,
        stop_pressure=0.0,
        update_pressure=0.0,
    )
    update = ExecutiveModulatorUpdate(
        summary=summary,
        previous_memory=None,
        next_memory=ZERO_EXECUTIVE_MODULATOR_MEMORY,
        state=modulator_state,
        reason_tags=frozenset(),
    )
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.70,
        uncertainty=0.45,
        host_friction=0.05,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.0,
    )
    policy = build_executive_policy_view(
        summary,
        modulator_state,
        debt_control_pressure=DebtControlPressure(debt_pressure=1.0),
    )

    decision = select_operator_route_with_policy(state, update, policy)

    assert decision.profile is OperatorRouteProfile.EXECUTE_GUARDED
    assert decision.blocked_reason is None
    assert "debt-control:execute-guarded" in decision.reason_tags
