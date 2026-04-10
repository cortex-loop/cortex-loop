from __future__ import annotations

import pytest

from cortex.sre.executive_summary import (
    ExecutiveSignalSummaryInputs,
    build_executive_signal_summary,
)
from cortex.sre.operator_routing import OperatorTaskMode


def test_executive_signal_summary_inputs_require_bounded_values() -> None:
    inputs = ExecutiveSignalSummaryInputs(
        task_mode=OperatorTaskMode.EXECUTE,
        uncertainty=0.45,
        quota_pressure=0.10,
        continuity_demand=0.05,
        previous_same_host_run_failed_before_completion=False,
        recent_product_failure_class=None,
        recent_probe_failure_class=None,
        recent_warning_bearing_success_present=False,
        verification_required=True,
    )

    summary = build_executive_signal_summary(inputs)

    assert summary.as_vector() == (0.45, 0.0, 0.1, 0.05, 0.2, 0.15)

    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        ExecutiveSignalSummaryInputs(
            task_mode=OperatorTaskMode.EXECUTE,
            uncertainty=1.2,
            quota_pressure=0.10,
            continuity_demand=0.05,
            previous_same_host_run_failed_before_completion=False,
            recent_product_failure_class=None,
            recent_probe_failure_class=None,
            recent_warning_bearing_success_present=False,
            verification_required=True,
        )


def test_executive_signal_summary_raises_repeated_failure_pressure_from_observable_failures() -> None:
    summary = build_executive_signal_summary(
        ExecutiveSignalSummaryInputs(
            task_mode=OperatorTaskMode.RESUME_EXECUTE,
            uncertainty=0.45,
            quota_pressure=0.00,
            continuity_demand=0.95,
            previous_same_host_run_failed_before_completion=True,
            recent_product_failure_class="runtime_error",
            recent_probe_failure_class=None,
            recent_warning_bearing_success_present=False,
            verification_required=True,
        )
    )

    assert summary.repeated_failure_pressure == pytest.approx(0.75)
    assert summary.novelty_pressure == pytest.approx(0.55)
    assert summary.verification_conflict_pressure == pytest.approx(0.65)
