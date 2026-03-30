"""Tools-side task-state builder for the operator-routing harness."""

from __future__ import annotations

from cortex.sre.operator_routing import OperatorTaskMode, OperatorTaskState


_TASK_DEFAULTS = {
    "pass_minimal": {
        "task_mode": OperatorTaskMode.EXECUTE,
        "complexity": 0.45,
        "continuity_demand": 0.05,
        "verification_demand": 0.80,
        "visible_burden_sensitivity": 0.45,
    },
    "truth_gap": {
        "task_mode": OperatorTaskMode.INSPECT,
        "complexity": 0.20,
        "continuity_demand": 0.00,
        "verification_demand": 0.00,
        "visible_burden_sensitivity": 0.80,
    },
    "restart_continuity": {
        "task_mode": OperatorTaskMode.RESUME_EXECUTE,
        "complexity": 0.55,
        "continuity_demand": 0.95,
        "verification_demand": 0.80,
        "visible_burden_sensitivity": 0.55,
    },
}

_PROBE_DEFAULTS = {
    "task_mode": OperatorTaskMode.INSPECT,
    "complexity": 0.10,
    "continuity_demand": 0.00,
    "verification_demand": 0.05,
    "visible_burden_sensitivity": 0.20,
}


def build_operator_task_state(
    scenario_id: str,
    *,
    previous_same_host_run_failed_before_completion: bool = False,
    recent_probe_failure_class: str | None = None,
    recent_baseline_clean_count: int = 0,
    recent_warning_bearing_success_present: bool = False,
    recent_product_failure_class: str | None = None,
) -> OperatorTaskState:
    if scenario_id not in _TASK_DEFAULTS:
        raise ValueError(f"unsupported operator scenario for task-state build: {scenario_id}")
    defaults = _TASK_DEFAULTS[scenario_id]
    return _build_state(
        task_mode=defaults["task_mode"],
        complexity=defaults["complexity"],
        continuity_demand=defaults["continuity_demand"],
        verification_demand=defaults["verification_demand"],
        visible_burden_sensitivity=defaults["visible_burden_sensitivity"],
        previous_same_host_run_failed_before_completion=previous_same_host_run_failed_before_completion,
        recent_probe_failure_class=recent_probe_failure_class,
        recent_baseline_clean_count=recent_baseline_clean_count,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present,
        recent_product_failure_class=recent_product_failure_class,
    )


def build_operator_probe_task_state(
    *,
    previous_same_host_run_failed_before_completion: bool = False,
    recent_probe_failure_class: str | None = None,
    recent_baseline_clean_count: int = 0,
    recent_warning_bearing_success_present: bool = False,
) -> OperatorTaskState:
    return _build_state(
        task_mode=_PROBE_DEFAULTS["task_mode"],
        complexity=_PROBE_DEFAULTS["complexity"],
        continuity_demand=_PROBE_DEFAULTS["continuity_demand"],
        verification_demand=_PROBE_DEFAULTS["verification_demand"],
        visible_burden_sensitivity=_PROBE_DEFAULTS["visible_burden_sensitivity"],
        previous_same_host_run_failed_before_completion=previous_same_host_run_failed_before_completion,
        recent_probe_failure_class=recent_probe_failure_class,
        recent_baseline_clean_count=recent_baseline_clean_count,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present,
        recent_product_failure_class=None,
    )


def _build_state(
    *,
    task_mode: OperatorTaskMode,
    complexity: float,
    continuity_demand: float,
    verification_demand: float,
    visible_burden_sensitivity: float,
    previous_same_host_run_failed_before_completion: bool,
    recent_probe_failure_class: str | None,
    recent_baseline_clean_count: int,
    recent_warning_bearing_success_present: bool,
    recent_product_failure_class: str | None,
) -> OperatorTaskState:
    default_uncertainty = 0.35 if task_mode is OperatorTaskMode.INSPECT else 0.45
    uncertainty = 0.65 if previous_same_host_run_failed_before_completion else default_uncertainty
    host_friction, quota_pressure = _pressure_levels(
        recent_probe_failure_class=recent_probe_failure_class,
        recent_baseline_clean_count=recent_baseline_clean_count,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present,
        recent_product_failure_class=recent_product_failure_class,
    )
    return OperatorTaskState(
        task_mode=task_mode,
        complexity=complexity,
        continuity_demand=continuity_demand,
        verification_demand=verification_demand,
        uncertainty=uncertainty,
        host_friction=host_friction,
        quota_pressure=quota_pressure,
        visible_burden_sensitivity=visible_burden_sensitivity,
    )


def _pressure_levels(
    *,
    recent_probe_failure_class: str | None,
    recent_baseline_clean_count: int,
    recent_warning_bearing_success_present: bool,
    recent_product_failure_class: str | None,
) -> tuple[float, float]:
    immediate_blockers = {"capacity_exhausted", "quota_exhausted"}
    if recent_probe_failure_class in immediate_blockers or recent_product_failure_class in immediate_blockers:
        return 0.85, 0.90
    if recent_warning_bearing_success_present:
        return 0.55, 0.60
    if recent_baseline_clean_count >= 2:
        return 0.00, 0.00
    return 0.00, 0.00


__all__ = [
    "build_operator_probe_task_state",
    "build_operator_task_state",
]
