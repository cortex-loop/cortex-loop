from __future__ import annotations

import pytest

from experimental.sre.executive_summary import ExecutiveSignalSummary
from experimental.sre.modulators import ExecutiveModulatorState
from experimental.sre.policy_view import build_executive_policy_view


def test_policy_view_switch_margin_changes_with_focus_and_explore() -> None:
    summary = ExecutiveSignalSummary(
        uncertainty=0.4,
        repeated_failure_pressure=0.0,
        quota_pressure=0.0,
        continuity_demand=0.8,
        novelty_pressure=0.2,
        verification_conflict_pressure=0.0,
    )
    focused = build_executive_policy_view(
        summary,
        ExecutiveModulatorState(
            focus_gain=0.8,
            explore_gain=0.1,
            stop_pressure=0.0,
            update_pressure=0.0,
        ),
    )
    exploratory = build_executive_policy_view(
        summary,
        ExecutiveModulatorState(
            focus_gain=0.1,
            explore_gain=0.8,
            stop_pressure=0.0,
            update_pressure=0.0,
        ),
    )

    assert focused.switch_margin > exploratory.switch_margin


def test_policy_view_allows_extra_read_pass_at_explicit_threshold() -> None:
    summary = ExecutiveSignalSummary(
        uncertainty=0.35,
        repeated_failure_pressure=0.0,
        quota_pressure=0.2,
        continuity_demand=0.0,
        novelty_pressure=0.7,
        verification_conflict_pressure=0.0,
    )
    policy = build_executive_policy_view(
        summary,
        ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.0,
            update_pressure=0.50,
        ),
    )

    assert policy.allow_extra_read_pass is True


def test_policy_view_stop_threshold_responds_to_summary_pressure() -> None:
    low_pressure = build_executive_policy_view(
        ExecutiveSignalSummary(
            uncertainty=0.35,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.0,
            novelty_pressure=0.2,
            verification_conflict_pressure=0.0,
        ),
        ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.6,
            update_pressure=0.0,
        ),
    )
    high_pressure = build_executive_policy_view(
        ExecutiveSignalSummary(
            uncertainty=0.35,
            repeated_failure_pressure=0.0,
            quota_pressure=1.0,
            continuity_demand=0.0,
            novelty_pressure=0.2,
            verification_conflict_pressure=1.0,
        ),
        ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.6,
            update_pressure=0.0,
        ),
    )

    assert high_pressure.stop_threshold < low_pressure.stop_threshold


def test_policy_view_bounds_numeric_fields() -> None:
    summary = ExecutiveSignalSummary(
        uncertainty=1.0,
        repeated_failure_pressure=1.0,
        quota_pressure=1.0,
        continuity_demand=1.0,
        novelty_pressure=1.0,
        verification_conflict_pressure=1.0,
    )
    policy = build_executive_policy_view(
        summary,
        ExecutiveModulatorState(
            focus_gain=1.0,
            explore_gain=1.0,
            stop_pressure=1.0,
            update_pressure=1.0,
        ),
    )

    assert 0.0 <= policy.default_profile_bonus <= 1.0
    assert 0.0 <= policy.switch_margin <= 1.0
    assert 0.0 <= policy.stop_threshold <= 1.0
    assert 0.0 <= policy.verification_intensity <= 1.0
