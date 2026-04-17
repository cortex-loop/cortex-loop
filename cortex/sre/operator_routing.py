"""Bounded operator-routing realization over low-dimensional task-state geometry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from numbers import Real

from .executive_summary import ExecutiveSignalSummary
from .modulators import (
    ExecutiveModulatorMemory,
    ExecutiveModulatorState,
    ExecutiveModulatorUpdate,
    ZERO_EXECUTIVE_MODULATOR_MEMORY,
)
from .policy_view import ExecutivePolicyView, build_executive_policy_view


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


class OperatorContractBindingProfile(str, Enum):
    STANDARD = "standard"
    LEAN = "lean"


class OperatorBrainCapabilityMismatchLevel(str, Enum):
    NONE = "none"
    DEGRADE = "degrade"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class OperatorBrainCapabilityEnvelope:
    continuity_tolerance: float
    verification_tolerance: float
    output_contract_tolerance: float

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_tolerance",
            "verification_tolerance",
            "output_contract_tolerance",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBrainCapabilityEnvelope.{field_name} must be numeric, "
                    f"got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorBrainCapabilityEnvelope.{field_name} must be between 0.0 and 1.0."
                )

    def as_payload(self) -> dict[str, float]:
        return {
            "continuity_tolerance": round(float(self.continuity_tolerance), 4),
            "verification_tolerance": round(float(self.verification_tolerance), 4),
            "output_contract_tolerance": round(
                float(self.output_contract_tolerance), 4
            ),
        }


@dataclass(frozen=True, slots=True)
class OperatorBrainCapabilityAssessment:
    continuity_mismatch: float
    verification_mismatch: float
    contract_mismatch: float
    level: OperatorBrainCapabilityMismatchLevel
    contract_binding_profile: OperatorContractBindingProfile
    fallback_family: str | None = None
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_mismatch",
            "verification_mismatch",
            "contract_mismatch",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBrainCapabilityAssessment.{field_name} must be numeric, "
                    f"got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorBrainCapabilityAssessment.{field_name} must be between 0.0 and 1.0."
                )
        if not isinstance(
            self.level, OperatorBrainCapabilityMismatchLevel
        ):
            actual_type = type(self.level).__name__
            raise TypeError(
                "OperatorBrainCapabilityAssessment.level must be "
                f"OperatorBrainCapabilityMismatchLevel, got {actual_type}."
            )
        if not isinstance(
            self.contract_binding_profile,
            OperatorContractBindingProfile,
        ):
            actual_type = type(self.contract_binding_profile).__name__
            raise TypeError(
                "OperatorBrainCapabilityAssessment.contract_binding_profile must be "
                f"OperatorContractBindingProfile, got {actual_type}."
            )
        if self.fallback_family is not None and not self.fallback_family.strip():
            raise ValueError(
                "OperatorBrainCapabilityAssessment.fallback_family must be non-empty after trimming when provided."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "OperatorBrainCapabilityAssessment.reason_tags must contain only non-empty values after trimming."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "continuity": round(float(self.continuity_mismatch), 4),
            "verification": round(float(self.verification_mismatch), 4),
            "contract_binding": round(float(self.contract_mismatch), 4),
            "level": self.level.value,
            "fallback_family": self.fallback_family,
        }


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
    contract_binding_demand: float = 0.0
    brain_capability: OperatorBrainCapabilityEnvelope = field(
        default_factory=lambda: OperatorBrainCapabilityEnvelope(
            continuity_tolerance=0.75,
            verification_tolerance=0.75,
            output_contract_tolerance=0.65,
        )
    )

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
            "contract_binding_demand",
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
        if not isinstance(self.brain_capability, OperatorBrainCapabilityEnvelope):
            actual_type = type(self.brain_capability).__name__
            raise TypeError(
                "OperatorTaskState.brain_capability must be "
                f"OperatorBrainCapabilityEnvelope, got {actual_type}."
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
    summary: ExecutiveSignalSummary
    modulator_memory: ExecutiveModulatorMemory
    modulator_state: ExecutiveModulatorState
    modulator_reason_tags: frozenset[str]
    policy_view: ExecutivePolicyView
    brain_capability_assessment: OperatorBrainCapabilityAssessment = field(
        default_factory=lambda: OperatorBrainCapabilityAssessment(
            continuity_mismatch=0.0,
            verification_mismatch=0.0,
            contract_mismatch=0.0,
            level=OperatorBrainCapabilityMismatchLevel.NONE,
            contract_binding_profile=OperatorContractBindingProfile.STANDARD,
        )
    )
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
        if not isinstance(self.modulator_state, ExecutiveModulatorState):
            actual_type = type(self.modulator_state).__name__
            raise TypeError(
                "OperatorRouteDecision.modulator_state must be ExecutiveModulatorState, "
                f"got {actual_type}."
            )
        if not isinstance(self.modulator_memory, ExecutiveModulatorMemory):
            actual_type = type(self.modulator_memory).__name__
            raise TypeError(
                "OperatorRouteDecision.modulator_memory must be ExecutiveModulatorMemory, "
                f"got {actual_type}."
            )
        if not isinstance(self.summary, ExecutiveSignalSummary):
            actual_type = type(self.summary).__name__
            raise TypeError(
                "OperatorRouteDecision.summary must be ExecutiveSignalSummary, "
                f"got {actual_type}."
            )
        if not isinstance(self.policy_view, ExecutivePolicyView):
            actual_type = type(self.policy_view).__name__
            raise TypeError(
                "OperatorRouteDecision.policy_view must be ExecutivePolicyView, "
                f"got {actual_type}."
            )
        if not isinstance(
            self.brain_capability_assessment, OperatorBrainCapabilityAssessment
        ):
            actual_type = type(self.brain_capability_assessment).__name__
            raise TypeError(
                "OperatorRouteDecision.brain_capability_assessment must be "
                f"OperatorBrainCapabilityAssessment, got {actual_type}."
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
        if any(not tag.strip() for tag in self.modulator_reason_tags):
            raise ValueError(
                "OperatorRouteDecision.modulator_reason_tags must contain only non-empty values after trimming."
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

def select_operator_route(state: OperatorTaskState) -> OperatorRouteDecision:
    zero_summary = ExecutiveSignalSummary(
        uncertainty=0.0,
        repeated_failure_pressure=0.0,
        quota_pressure=0.0,
        continuity_demand=0.0,
        novelty_pressure=0.0,
        verification_conflict_pressure=0.0,
    )
    zero_update = ExecutiveModulatorUpdate(
        summary=zero_summary,
        previous_memory=ZERO_EXECUTIVE_MODULATOR_MEMORY,
        next_memory=ZERO_EXECUTIVE_MODULATOR_MEMORY,
        state=ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.0,
            update_pressure=0.0,
        ),
        reason_tags=frozenset(),
    )
    zero_policy = build_executive_policy_view(zero_summary, zero_update.state)
    return select_operator_route_with_policy(state, zero_update, zero_policy)


def select_operator_route_with_modulators(
    state: OperatorTaskState,
    modulator_update: ExecutiveModulatorUpdate | None = None,
) -> OperatorRouteDecision:
    if modulator_update is None:
        return select_operator_route(state)
    if not isinstance(modulator_update, ExecutiveModulatorUpdate):
        actual_type = type(modulator_update).__name__
        raise TypeError(
            "select_operator_route.modulator_update must be ExecutiveModulatorUpdate, "
            f"got {actual_type}."
        )
    return select_operator_route_with_policy(
        state,
        modulator_update,
        build_executive_policy_view(modulator_update.summary, modulator_update.state),
    )


def select_operator_route_with_policy(
    state: OperatorTaskState,
    modulator_update: ExecutiveModulatorUpdate,
    policy_view: ExecutivePolicyView,
) -> OperatorRouteDecision:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "select_operator_route.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    if not isinstance(modulator_update, ExecutiveModulatorUpdate):
        actual_type = type(modulator_update).__name__
        raise TypeError(
            "select_operator_route.modulator_update must be ExecutiveModulatorUpdate, "
            f"got {actual_type}."
        )
    if not isinstance(policy_view, ExecutivePolicyView):
        actual_type = type(policy_view).__name__
        raise TypeError(
            "select_operator_route.policy_view must be ExecutivePolicyView, "
            f"got {actual_type}."
        )

    admissible_profiles = _ADMISSIBLE_PROFILES_BY_MODE[state.task_mode]
    default_profile = _DEFAULT_PROFILE_BY_MODE[state.task_mode]
    brain_capability_assessment = assess_operator_brain_capability(state)
    utilities = {
        profile: _route_utility(profile, state)
        + _policy_profile_adjustment(
            profile,
            default_profile=default_profile,
            state=state,
            policy_view=policy_view,
        )
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
    margin_threshold = _effective_margin_threshold(policy_view)

    if selected_profile is not default_profile and neutral_margin < margin_threshold:
        selected_profile = default_profile
        selected_utility = default_utility
        neutral_margin = 0.0
        reason_tags.add("gate:default-margin")
    elif selected_profile is default_profile:
        reason_tags.add("gate:default-profile")
    else:
        reason_tags.add("gate:non-default-profile")

    if (
        brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    ):
        reason_tags.update(brain_capability_assessment.reason_tags)
        reason_tags.add("blocked:brain-capability")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="brain_capability_mismatch",
        )

    if modulator_update.state.stop_pressure >= policy_view.stop_threshold and selected_profile is not OperatorRouteProfile.INSPECT_LIGHT:
        reason_tags.add("blocked:modulator-stop-pressure")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="blocked_by_modulator_stop_pressure",
        )

    if state.quota_pressure >= 0.80 and selected_profile is not OperatorRouteProfile.INSPECT_LIGHT:
        reason_tags.add("blocked:quota-pressure")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="blocked_by_quota_pressure",
        )

    selected_profile = _apply_brain_capability_profile_downshift(
        selected_profile,
        state=state,
        assessment=brain_capability_assessment,
        reason_tags=reason_tags,
    )
    budget = _apply_policy_to_budget(
        _BUDGET_PROFILES[selected_profile],
        state=state,
        policy_view=policy_view,
        assessment=brain_capability_assessment,
        reason_tags=reason_tags,
    )

    return OperatorRouteDecision(
        profile=selected_profile,
        budget=budget,
        selected_margin=selected_utility,
        neutral_margin=neutral_margin,
        reason_tags=frozenset(reason_tags | {f"profile:{selected_profile.value}"}),
        summary=modulator_update.summary,
        modulator_memory=modulator_update.next_memory,
        modulator_state=modulator_update.state,
        modulator_reason_tags=modulator_update.reason_tags,
        policy_view=policy_view,
        brain_capability_assessment=brain_capability_assessment,
    )


def assess_operator_brain_capability(
    state: OperatorTaskState,
) -> OperatorBrainCapabilityAssessment:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "assess_operator_brain_capability.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    continuity_mismatch = max(
        0.0,
        float(state.continuity_demand)
        - float(state.brain_capability.continuity_tolerance),
    )
    verification_mismatch = max(
        0.0,
        float(state.verification_demand)
        - float(state.brain_capability.verification_tolerance),
    )
    contract_mismatch = max(
        0.0,
        float(state.contract_binding_demand)
        - float(state.brain_capability.output_contract_tolerance),
    )
    max_mismatch = max(
        continuity_mismatch,
        verification_mismatch,
        contract_mismatch,
    )
    if max_mismatch >= 0.50:
        level = OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    elif max_mismatch >= 0.20:
        level = OperatorBrainCapabilityMismatchLevel.DEGRADE
    else:
        level = OperatorBrainCapabilityMismatchLevel.NONE

    reason_tags: set[str] = set()
    if level is not OperatorBrainCapabilityMismatchLevel.NONE:
        if contract_mismatch > 0.0:
            reason_tags.add("brain-capability:contract-mismatch")
        if verification_mismatch > 0.0:
            reason_tags.add("brain-capability:verification-downshift")
    fallback_family = None
    if level is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED:
        reason_tags.add("brain-capability:unsupported-floor")
        fallback_family = _brain_capability_fallback_family(
            state,
            continuity_mismatch=continuity_mismatch,
            verification_mismatch=verification_mismatch,
        )
    return OperatorBrainCapabilityAssessment(
        continuity_mismatch=continuity_mismatch,
        verification_mismatch=verification_mismatch,
        contract_mismatch=contract_mismatch,
        level=level,
        contract_binding_profile=(
            OperatorContractBindingProfile.LEAN
            if level is OperatorBrainCapabilityMismatchLevel.DEGRADE
            else OperatorContractBindingProfile.STANDARD
        ),
        fallback_family=fallback_family,
        reason_tags=frozenset(reason_tags),
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
    brain_capability_band = _brain_capability_band_for_state(state)
    return {
        "route_profile": decision.profile.value,
        "route_budget": decision.budget.as_payload(),
        "route_reason_tags": sorted(decision.reason_tags),
        "selected_margin": round(float(decision.selected_margin), 4),
        "neutral_margin": round(float(decision.neutral_margin), 4),
        "state_vector": [round(value, 4) for value in state.as_vector()],
        "quota_pressure": round(float(state.quota_pressure), 4),
        "host_friction": round(float(state.host_friction), 4),
        "visible_burden_sensitivity": round(
            float(state.visible_burden_sensitivity), 4
        ),
        "contract_binding_demand": round(float(state.contract_binding_demand), 4),
        "brain_capability": state.brain_capability.as_payload(),
        "brain_capability_band": brain_capability_band,
        "brain_capability_mismatch": (
            decision.brain_capability_assessment.as_payload()
        ),
        "brain_capability_reason_tags": sorted(
            decision.brain_capability_assessment.reason_tags
        ),
        "contract_binding_profile": (
            decision.brain_capability_assessment.contract_binding_profile.value
        ),
        "blocked_reason": decision.blocked_reason,
        "modulator_summary": decision.summary.as_payload(),
        "modulator_memory": decision.modulator_memory.as_payload(),
        "modulator_state": decision.modulator_state.as_payload(),
        "modulator_reason_tags": sorted(decision.modulator_reason_tags),
        "policy_view": decision.policy_view.as_payload(),
    }

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


def _policy_profile_adjustment(
    profile: OperatorRouteProfile,
    *,
    default_profile: OperatorRouteProfile,
    state: OperatorTaskState,
    policy_view: ExecutivePolicyView,
) -> float:
    adjustment = 0.0
    if profile is default_profile:
        adjustment += policy_view.default_profile_bonus
    if state.task_mode is OperatorTaskMode.RESUME_EXECUTE and profile in {
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    }:
        adjustment += 0.04 * policy_view.default_profile_bonus
    return adjustment


def _effective_margin_threshold(policy_view: ExecutivePolicyView) -> float:
    return float(policy_view.switch_margin)


def _apply_policy_to_budget(
    budget: OperatorBudgetProfile,
    *,
    state: OperatorTaskState,
    policy_view: ExecutivePolicyView,
    assessment: OperatorBrainCapabilityAssessment,
    reason_tags: set[str],
) -> OperatorBudgetProfile:
    if (
        assessment.level is OperatorBrainCapabilityMismatchLevel.DEGRADE
        and (budget.allow_extra_read_pass or budget.max_retries > 0)
    ):
        reason_tags.add("budget:brain-capability-suppressed")
        return replace(
            budget,
            max_retries=0,
            allow_extra_read_pass=False,
        )
    if state.task_mode is OperatorTaskMode.INSPECT and policy_view.allow_extra_read_pass:
        reason_tags.add("budget:extra-read-pass")
        return replace(
            budget,
            max_retries=budget.max_retries + 1,
            allow_extra_read_pass=True,
        )
    return budget


def _apply_brain_capability_profile_downshift(
    selected_profile: OperatorRouteProfile,
    *,
    state: OperatorTaskState,
    assessment: OperatorBrainCapabilityAssessment,
    reason_tags: set[str],
) -> OperatorRouteProfile:
    if assessment.level is not OperatorBrainCapabilityMismatchLevel.DEGRADE:
        reason_tags.update(assessment.reason_tags)
        return selected_profile
    reason_tags.update(assessment.reason_tags)
    if selected_profile in {
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    }:
        reason_tags.add("brain-capability:continuity-downshift")
        if state.task_mode is OperatorTaskMode.RESUME_EXECUTE:
            return OperatorRouteProfile.EXECUTE_STANDARD
        return OperatorRouteProfile.INSPECT_LIGHT
    return selected_profile


def _brain_capability_fallback_family(
    state: OperatorTaskState,
    *,
    continuity_mismatch: float,
    verification_mismatch: float,
) -> str:
    if state.task_mode is OperatorTaskMode.INSPECT:
        return "inspect"
    if verification_mismatch >= continuity_mismatch or state.verification_demand >= 0.5:
        return "check"
    return "manual_escalation"


def _brain_capability_band_for_state(state: OperatorTaskState) -> str:
    from cortex.runtime.operator_brain_capability import (
        brain_capability_band_for_envelope,
    )

    return brain_capability_band_for_envelope(state.brain_capability)


__all__ = [
    "OperatorBrainCapabilityAssessment",
    "OperatorBrainCapabilityEnvelope",
    "OperatorBudgetProfile",
    "OperatorContractBindingProfile",
    "OperatorRouteDecision",
    "OperatorRouteProfile",
    "OperatorBrainCapabilityMismatchLevel",
    "OperatorTaskMode",
    "OperatorTaskState",
    "assess_operator_brain_capability",
    "build_operator_route_diagnostics",
    "select_operator_route_with_policy",
    "select_operator_route_with_modulators",
    "select_operator_route",
]
