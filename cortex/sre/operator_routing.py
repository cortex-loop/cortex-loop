"""Bounded operator-routing realization over low-dimensional task-state geometry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from numbers import Real


class OperatorTaskMode(str, Enum):
    INSPECT = "inspect"
    EXECUTE = "execute"
    RESUME_EXECUTE = "resume_execute"


class OperatorRouteProfile(str, Enum):
    INSPECT_LIGHT = "inspect_light"
    EXECUTE_STANDARD = "execute_standard"
    EXECUTE_GUARDED = "execute_guarded"
    CONTINUITY_STANDARD = "continuity_standard"
    CONTINUITY_GUARDED = "continuity_guarded"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class OperatorTaskState:
    task_mode: OperatorTaskMode
    complexity: float
    continuity_demand: float
    verification_demand: float
    uncertainty: float
    host_friction: float
    quota_pressure: float
    visible_burden_sensitivity: float

    def __post_init__(self) -> None:
        if not isinstance(self.task_mode, OperatorTaskMode):
            actual_type = type(self.task_mode).__name__
            raise TypeError(
                "OperatorTaskState.task_mode must be OperatorTaskMode, "
                f"got {actual_type}."
            )
        for field_name in (
            "complexity",
            "continuity_demand",
            "verification_demand",
            "uncertainty",
            "host_friction",
            "quota_pressure",
            "visible_burden_sensitivity",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorTaskState.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorTaskState.{field_name} must be between 0.0 and 1.0."
                )

    def as_vector(self) -> tuple[float, ...]:
        return (
            float(self.complexity),
            float(self.continuity_demand),
            float(self.verification_demand),
            float(self.uncertainty),
            float(self.host_friction),
            float(self.quota_pressure),
        )


@dataclass(frozen=True, slots=True)
class OperatorBudgetProfile:
    max_turns: int
    max_retries: int
    allow_resume: bool
    allow_extra_read_pass: bool
    require_verification: bool
    stop_on_quota: bool
    stop_on_capacity: bool

    def __post_init__(self) -> None:
        for field_name in ("max_turns", "max_retries"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBudgetProfile.{field_name} must be int, got {actual_type}."
                )
            if value < 0:
                raise ValueError(
                    f"OperatorBudgetProfile.{field_name} must be non-negative."
                )
        for field_name in (
            "allow_resume",
            "allow_extra_read_pass",
            "require_verification",
            "stop_on_quota",
            "stop_on_capacity",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBudgetProfile.{field_name} must be bool, got {actual_type}."
                )

    def as_payload(self) -> dict[str, int | bool]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OperatorRouteDecision:
    profile: OperatorRouteProfile
    budget: OperatorBudgetProfile
    selected_margin: float
    neutral_margin: float
    reason_tags: frozenset[str]
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile, OperatorRouteProfile):
            actual_type = type(self.profile).__name__
            raise TypeError(
                "OperatorRouteDecision.profile must be OperatorRouteProfile, "
                f"got {actual_type}."
            )
        if not isinstance(self.budget, OperatorBudgetProfile):
            actual_type = type(self.budget).__name__
            raise TypeError(
                "OperatorRouteDecision.budget must be OperatorBudgetProfile, "
                f"got {actual_type}."
            )
        for field_name in ("selected_margin", "neutral_margin"):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorRouteDecision.{field_name} must be numeric, got {actual_type}."
                )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "OperatorRouteDecision.reason_tags must contain only non-empty values after trimming."
            )
        if self.blocked_reason is not None and not self.blocked_reason.strip():
            raise ValueError(
                "OperatorRouteDecision.blocked_reason must be non-empty after trimming when provided."
            )
        if self.profile is OperatorRouteProfile.BLOCKED and self.blocked_reason is None:
            raise ValueError(
                "OperatorRouteDecision.blocked_reason is required when the profile is blocked."
            )
        if self.profile is not OperatorRouteProfile.BLOCKED and self.blocked_reason is not None:
            raise ValueError(
                "OperatorRouteDecision.blocked_reason is only valid for the blocked profile."
            )


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

_ROUTE_PROTOTYPES = {
    OperatorRouteProfile.INSPECT_LIGHT: (0.10, 0.00, 0.05, 0.40, 0.10, 0.10),
    OperatorRouteProfile.EXECUTE_STANDARD: (0.45, 0.05, 0.70, 0.45, 0.20, 0.20),
    OperatorRouteProfile.EXECUTE_GUARDED: (0.40, 0.05, 0.55, 0.45, 0.55, 0.65),
    OperatorRouteProfile.CONTINUITY_STANDARD: (0.55, 0.90, 0.70, 0.45, 0.25, 0.25),
    OperatorRouteProfile.CONTINUITY_GUARDED: (0.50, 0.90, 0.55, 0.45, 0.60, 0.70),
}

_AXIS_WEIGHTS = (1.0, 1.2, 1.0, 0.8, 1.3, 1.5)
_ROUTE_GAIN_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.35,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.60,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.50,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.70,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.58,
}
_HOST_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.10,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.20,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.55,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.25,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.60,
}
_QUOTA_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.10,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.20,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.65,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.25,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.70,
}
_VISIBLE_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.05,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.35,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.25,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.45,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.30,
}
_DEFAULT_PROFILE_BY_MODE = {
    OperatorTaskMode.INSPECT: OperatorRouteProfile.INSPECT_LIGHT,
    OperatorTaskMode.EXECUTE: OperatorRouteProfile.EXECUTE_STANDARD,
    OperatorTaskMode.RESUME_EXECUTE: OperatorRouteProfile.CONTINUITY_STANDARD,
}
_ADMISSIBLE_PROFILES_BY_MODE = {
    OperatorTaskMode.INSPECT: (OperatorRouteProfile.INSPECT_LIGHT,),
    OperatorTaskMode.EXECUTE: (
        OperatorRouteProfile.EXECUTE_STANDARD,
        OperatorRouteProfile.EXECUTE_GUARDED,
    ),
    OperatorTaskMode.RESUME_EXECUTE: (
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    ),
}
_BUDGET_PROFILES = {
    OperatorRouteProfile.INSPECT_LIGHT: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=False,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.EXECUTE_STANDARD: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=False,
        stop_on_capacity=False,
    ),
    OperatorRouteProfile.EXECUTE_GUARDED: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.CONTINUITY_STANDARD: OperatorBudgetProfile(
        max_turns=2,
        max_retries=0,
        allow_resume=True,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=False,
        stop_on_capacity=False,
    ),
    OperatorRouteProfile.CONTINUITY_GUARDED: OperatorBudgetProfile(
        max_turns=2,
        max_retries=0,
        allow_resume=True,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.BLOCKED: OperatorBudgetProfile(
        max_turns=0,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=False,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
}
_LAMBDA_D = 0.55
_LAMBDA_H = 0.20
_LAMBDA_Q = 0.30
_LAMBDA_V = 0.15
_MARGIN_THRESHOLD = 0.08


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


def select_operator_route(state: OperatorTaskState) -> OperatorRouteDecision:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "select_operator_route.state must be OperatorTaskState, "
            f"got {actual_type}."
        )

    admissible_profiles = _ADMISSIBLE_PROFILES_BY_MODE[state.task_mode]
    default_profile = _DEFAULT_PROFILE_BY_MODE[state.task_mode]
    utilities = {
        profile: _route_utility(profile, state)
        for profile in admissible_profiles
    }
    reason_tags = {
        f"task_mode:{state.task_mode.value}",
        f"default_profile:{default_profile.value}",
        f"quota_pressure:{state.quota_pressure:.2f}",
        f"host_friction:{state.host_friction:.2f}",
    }

    if state.task_mode is OperatorTaskMode.RESUME_EXECUTE and state.host_friction >= 0.75:
        utilities[OperatorRouteProfile.CONTINUITY_GUARDED] += 0.10
        reason_tags.add("continuity:guarded-preferred")
    if state.task_mode is OperatorTaskMode.EXECUTE and (
        state.host_friction >= 0.55 or state.quota_pressure >= 0.60
    ):
        utilities[OperatorRouteProfile.EXECUTE_GUARDED] += 0.10
        reason_tags.add("execute:guarded-preferred")

    selected_profile = max(admissible_profiles, key=lambda profile: utilities[profile])
    default_utility = utilities[default_profile]
    selected_utility = utilities[selected_profile]
    neutral_margin = selected_utility - default_utility

    if selected_profile is not default_profile and neutral_margin < _MARGIN_THRESHOLD:
        selected_profile = default_profile
        selected_utility = default_utility
        neutral_margin = 0.0
        reason_tags.add("gate:default-margin")
    elif selected_profile is default_profile:
        reason_tags.add("gate:default-profile")
    else:
        reason_tags.add("gate:non-default-profile")

    if state.quota_pressure >= 0.80 and selected_profile is not OperatorRouteProfile.INSPECT_LIGHT:
        reason_tags.add("blocked:quota-pressure")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            blocked_reason="blocked_by_quota_pressure",
        )

    return OperatorRouteDecision(
        profile=selected_profile,
        budget=_BUDGET_PROFILES[selected_profile],
        selected_margin=selected_utility,
        neutral_margin=neutral_margin,
        reason_tags=frozenset(reason_tags | {f"profile:{selected_profile.value}"}),
    )


def build_operator_route_diagnostics(
    state: OperatorTaskState,
    decision: OperatorRouteDecision,
) -> dict[str, object]:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "build_operator_route_diagnostics.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    if not isinstance(decision, OperatorRouteDecision):
        actual_type = type(decision).__name__
        raise TypeError(
            "build_operator_route_diagnostics.decision must be OperatorRouteDecision, "
            f"got {actual_type}."
        )
    return {
        "route_profile": decision.profile.value,
        "route_budget": decision.budget.as_payload(),
        "route_reason_tags": sorted(decision.reason_tags),
        "selected_margin": round(float(decision.selected_margin), 4),
        "neutral_margin": round(float(decision.neutral_margin), 4),
        "state_vector": [round(value, 4) for value in state.as_vector()],
        "quota_pressure": round(float(state.quota_pressure), 4),
        "host_friction": round(float(state.host_friction), 4),
        "blocked_reason": decision.blocked_reason,
    }


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


def _route_utility(
    profile: OperatorRouteProfile,
    state: OperatorTaskState,
) -> float:
    prototype = _ROUTE_PROTOTYPES[profile]
    distance = sum(
        axis_weight * (state_value - prototype_value) ** 2
        for axis_weight, state_value, prototype_value in zip(
            _AXIS_WEIGHTS,
            state.as_vector(),
            prototype,
            strict=True,
        )
    )
    return (
        _ROUTE_GAIN_PRIORS[profile]
        - (_LAMBDA_D * distance)
        - (_LAMBDA_H * _HOST_COST_PRIORS[profile] * state.host_friction)
        - (_LAMBDA_Q * _QUOTA_COST_PRIORS[profile] * state.quota_pressure)
        - (_LAMBDA_V * _VISIBLE_COST_PRIORS[profile] * state.visible_burden_sensitivity)
    )


__all__ = [
    "OperatorBudgetProfile",
    "OperatorRouteDecision",
    "OperatorRouteProfile",
    "OperatorTaskMode",
    "OperatorTaskState",
    "build_operator_probe_task_state",
    "build_operator_route_diagnostics",
    "build_operator_task_state",
    "select_operator_route",
]
