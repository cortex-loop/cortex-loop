from __future__ import annotations

from pathlib import Path

import pytest

from cortex.sre.modulators import (
    ExecutiveModulatorInputs,
    update_executive_modulators,
)
from cortex.sre.operator_routing import (
    OperatorTaskMode,
    OperatorTaskState,
    select_operator_route_with_modulators,
)


def test_modulator_update_clips_values_into_unit_interval() -> None:
    update = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=1.0,
            repeated_failure_pressure=1.0,
            quota_pressure=1.0,
            continuity_demand=1.0,
            novelty_pressure=1.0,
        )
    )

    for value in update.state.as_payload().values():
        assert 0.0 <= value <= 1.0


def test_high_quota_pressure_raises_stop_pressure() -> None:
    low = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.1,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.1,
            novelty_pressure=0.1,
        )
    )
    high = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.1,
            repeated_failure_pressure=0.0,
            quota_pressure=1.0,
            continuity_demand=0.1,
            novelty_pressure=0.1,
        )
    )

    assert high.state.stop_pressure > low.state.stop_pressure


def test_high_continuity_raises_focus_gain() -> None:
    low = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.0,
            novelty_pressure=0.1,
        )
    )
    high = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=1.0,
            novelty_pressure=0.1,
        )
    )

    assert high.state.focus_gain > low.state.focus_gain


def test_repeated_failure_raises_explore_gain() -> None:
    low = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.2,
            novelty_pressure=0.1,
        )
    )
    high = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=1.0,
            quota_pressure=0.0,
            continuity_demand=0.2,
            novelty_pressure=0.1,
        )
    )

    assert high.state.explore_gain > low.state.explore_gain


def test_high_novelty_raises_update_pressure() -> None:
    low = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.2,
            novelty_pressure=0.0,
        )
    )
    high = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.2,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.2,
            novelty_pressure=1.0,
        )
    )

    assert high.state.update_pressure > low.state.update_pressure


def test_modulator_stop_pressure_can_block_route() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.45,
        continuity_demand=0.05,
        verification_demand=0.80,
        uncertainty=0.90,
        host_friction=0.10,
        quota_pressure=1.0,
        visible_burden_sensitivity=0.45,
    )
    update = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.90,
            repeated_failure_pressure=1.0,
            quota_pressure=1.0,
            continuity_demand=0.05,
            novelty_pressure=0.2,
        )
    )

    decision = select_operator_route_with_modulators(state, update)

    assert decision.blocked_reason == "blocked_by_modulator_stop_pressure"


def test_modulator_update_pressure_adds_extra_read_pass() -> None:
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.INSPECT,
        complexity=0.20,
        continuity_demand=0.00,
        verification_demand=0.00,
        uncertainty=0.70,
        host_friction=0.00,
        quota_pressure=0.10,
        visible_burden_sensitivity=0.80,
    )
    update = update_executive_modulators(
        ExecutiveModulatorInputs(
            uncertainty=0.70,
            repeated_failure_pressure=0.0,
            quota_pressure=0.10,
            continuity_demand=0.00,
            novelty_pressure=0.80,
        )
    )

    decision = select_operator_route_with_modulators(state, update)

    assert decision.budget.allow_extra_read_pass is True
    assert decision.budget.max_retries == 1


def test_modulator_module_uses_abstract_control_names() -> None:
    text = (
        Path(__file__).resolve().parents[2]
        / "cortex"
        / "sre"
        / "modulators.py"
    ).read_text(encoding="utf-8").lower()

    for forbidden in ("dopamine", "serotonin", "acetylcholine", "norepinephrine"):
        assert forbidden not in text
