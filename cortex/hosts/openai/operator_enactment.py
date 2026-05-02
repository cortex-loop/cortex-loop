"""OpenAI operator enactment of already-computed SRE route decisions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from numbers import Real
from typing import Any


RECHECK_PROMPT_NAME = "truth_gap_recheck_operator.md"

MODEL_VISIBLE_FORBIDDEN_TERMS = (
    "CORTEX_RUNTIME_CONTEXT",
    "Cortex",
    "debt_control",
    "debt-control",
    "debt pressure",
    "resolution_deficit",
    "resolution deficit",
    "brake",
    "brake tonic",
    "AUX",
    "goal_drag",
    "pending_goal_debt",
    "verification_relief_bias",
    "executive_policy_view",
    "operator_route_payload",
    "route_reason_tags",
)


class OpenAIOperatorEnactmentAction(str, Enum):
    INVOKE = "invoke"
    BLOCK = "block"
    RESUME_RECHECK = "resume_recheck"


@dataclass(frozen=True, slots=True)
class OpenAIOperatorEnactmentDecision:
    """Host-native action authorized by OpenAI route/brake/debt payloads."""

    action: OpenAIOperatorEnactmentAction
    route_profile: str
    invocation_allowed: bool
    route_budget: dict[str, object]
    blocked_reason: str | None = None
    resume_prompt_name: str | None = None
    thread_policy: str = "ephemeral_allowed"
    resume_recheck_armed: bool = False
    resume_recheck_allowed: bool = False
    resume_recheck_blocked_reason: str | None = None
    model_bound_difference_kind: str = "none"
    reason_tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.action, OpenAIOperatorEnactmentAction):
            actual_type = type(self.action).__name__
            raise TypeError(
                "OpenAIOperatorEnactmentDecision.action must be "
                f"OpenAIOperatorEnactmentAction, got {actual_type}."
            )
        if not isinstance(self.route_profile, str) or not self.route_profile.strip():
            raise ValueError(
                "OpenAIOperatorEnactmentDecision.route_profile must be non-empty."
            )
        if not isinstance(self.invocation_allowed, bool):
            actual_type = type(self.invocation_allowed).__name__
            raise TypeError(
                "OpenAIOperatorEnactmentDecision.invocation_allowed must be bool, "
                f"got {actual_type}."
            )
        if self.blocked_reason is not None and not self.blocked_reason.strip():
            raise ValueError(
                "OpenAIOperatorEnactmentDecision.blocked_reason must be non-empty "
                "when provided."
            )
        if self.resume_prompt_name is not None and not self.resume_prompt_name.strip():
            raise ValueError(
                "OpenAIOperatorEnactmentDecision.resume_prompt_name must be non-empty "
                "when provided."
            )
        if not self.thread_policy.strip():
            raise ValueError(
                "OpenAIOperatorEnactmentDecision.thread_policy must be non-empty."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "OpenAIOperatorEnactmentDecision.reason_tags must be non-empty."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "route_profile": self.route_profile,
            "invocation_allowed": self.invocation_allowed,
            "route_budget": dict(self.route_budget),
            "blocked_reason": self.blocked_reason,
            "resume_prompt_name": self.resume_prompt_name,
            "thread_policy": self.thread_policy,
            "resume_recheck_armed": self.resume_recheck_armed,
            "resume_recheck_allowed": self.resume_recheck_allowed,
            "resume_recheck_blocked_reason": self.resume_recheck_blocked_reason,
            "model_bound_difference_kind": self.model_bound_difference_kind,
            "reason_tags": list(self.reason_tags),
        }


def build_openai_operator_enactment_decision(
    *,
    operator_route_payload: Mapping[str, Any],
    executive_policy_view_payload: Mapping[str, Any],
    debt_control_payload: Mapping[str, Any],
    scenario_id: str,
    first_result_kind: str | None = None,
    provider_limit_interference: bool = False,
    thread_id: str | None = None,
) -> OpenAIOperatorEnactmentDecision:
    """Translate SRE payloads into the OpenAI operator's next allowed action.

    The adapter is deliberately host-local: it does not recompute Core or SRE
    policy, and it does not produce model-visible instruction text.
    """

    if not isinstance(operator_route_payload, Mapping):
        actual_type = type(operator_route_payload).__name__
        raise TypeError(
            "operator_route_payload must be a mapping, " f"got {actual_type}."
        )
    if not isinstance(executive_policy_view_payload, Mapping):
        actual_type = type(executive_policy_view_payload).__name__
        raise TypeError(
            "executive_policy_view_payload must be a mapping, "
            f"got {actual_type}."
        )
    if not isinstance(debt_control_payload, Mapping):
        actual_type = type(debt_control_payload).__name__
        raise TypeError(
            "debt_control_payload must be a mapping, " f"got {actual_type}."
        )
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ValueError("scenario_id must be a non-empty string.")
    if not isinstance(provider_limit_interference, bool):
        actual_type = type(provider_limit_interference).__name__
        raise TypeError(
            "provider_limit_interference must be bool, " f"got {actual_type}."
        )

    route_profile = str(operator_route_payload.get("route_profile", "")).strip()
    if not route_profile:
        raise ValueError("operator_route_payload.route_profile is required.")
    route_budget = _mapping_payload(operator_route_payload.get("route_budget", {}))
    blocked_reason = _optional_non_empty_string(
        operator_route_payload.get("blocked_reason")
    )
    route_reason_tags = tuple(
        str(tag).strip()
        for tag in operator_route_payload.get("route_reason_tags", ())
        if str(tag).strip()
    )

    if route_profile == "blocked" or blocked_reason is not None:
        return OpenAIOperatorEnactmentDecision(
            action=OpenAIOperatorEnactmentAction.BLOCK,
            route_profile=route_profile,
            invocation_allowed=False,
            route_budget=route_budget,
            blocked_reason=blocked_reason or "route_blocked",
            thread_policy="no_invocation",
            model_bound_difference_kind="block",
            reason_tags=("enact:block", *route_reason_tags),
        )

    recheck_armed = _resume_recheck_armed(
        route_budget=route_budget,
        executive_policy_view_payload=executive_policy_view_payload,
        debt_control_payload=debt_control_payload,
        scenario_id=scenario_id,
    )
    if recheck_armed:
        allowed, blocked = _resume_recheck_allowed(
            first_result_kind=first_result_kind,
            provider_limit_interference=provider_limit_interference,
            thread_id=thread_id,
        )
        if allowed:
            return OpenAIOperatorEnactmentDecision(
                action=OpenAIOperatorEnactmentAction.RESUME_RECHECK,
                route_profile=route_profile,
                invocation_allowed=True,
                route_budget=route_budget,
                resume_prompt_name=RECHECK_PROMPT_NAME,
                thread_policy="resume_existing_thread",
                resume_recheck_armed=True,
                resume_recheck_allowed=True,
                model_bound_difference_kind="resume_recheck",
                reason_tags=("enact:resume-recheck", *route_reason_tags),
            )
        return OpenAIOperatorEnactmentDecision(
            action=OpenAIOperatorEnactmentAction.INVOKE,
            route_profile=route_profile,
            invocation_allowed=True,
            route_budget=route_budget,
            resume_prompt_name=RECHECK_PROMPT_NAME,
            thread_policy="persistent_for_possible_recheck",
            resume_recheck_armed=True,
            resume_recheck_allowed=False,
            resume_recheck_blocked_reason=blocked,
            model_bound_difference_kind="thread_persistence",
            reason_tags=("enact:persistent-thread", *route_reason_tags),
        )

    return OpenAIOperatorEnactmentDecision(
        action=OpenAIOperatorEnactmentAction.INVOKE,
        route_profile=route_profile,
        invocation_allowed=True,
        route_budget=route_budget,
        thread_policy="ephemeral_allowed",
        reason_tags=("enact:invoke", *route_reason_tags),
    )


def find_internal_terms_in_model_visible_values(
    values: Mapping[str, Any] | Sequence[Any] | str,
) -> tuple[str, ...]:
    """Return forbidden internal vocabulary found in model-visible values."""

    text = "\n".join(_flatten_visible_values(values))
    lowered = text.lower()
    found = []
    for term in MODEL_VISIBLE_FORBIDDEN_TERMS:
        if term.lower() in lowered:
            found.append(term)
    return tuple(found)


def model_visible_values_are_silent(
    values: Mapping[str, Any] | Sequence[Any] | str,
) -> bool:
    return not find_internal_terms_in_model_visible_values(values)


def _resume_recheck_armed(
    *,
    route_budget: Mapping[str, object],
    executive_policy_view_payload: Mapping[str, Any],
    debt_control_payload: Mapping[str, Any],
    scenario_id: str,
) -> bool:
    if scenario_id != "truth_gap":
        return False
    if route_budget.get("allow_extra_read_pass") is not True:
        return False
    if executive_policy_view_payload.get("allow_extra_read_pass") is not True:
        return False
    verification_relief = _unit_float(
        debt_control_payload.get("verification_relief_bias", 0.0),
        field_name="debt_control_payload.verification_relief_bias",
    )
    return verification_relief > 0.0


def _resume_recheck_allowed(
    *,
    first_result_kind: str | None,
    provider_limit_interference: bool,
    thread_id: str | None,
) -> tuple[bool, str | None]:
    if first_result_kind != "truthful_incomplete":
        return False, "first_result_not_truthful_incomplete"
    if provider_limit_interference:
        return False, "provider_limit_interference"
    if not (isinstance(thread_id, str) and thread_id.strip()):
        return False, "missing_thread_id"
    return True, None


def _mapping_payload(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"route budget must be a mapping, got {actual_type}.")
    return {str(key): item for key, item in value.items()}


def _optional_non_empty_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _unit_float(value: object, *, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be numeric, got {actual_type}.")
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")
    return number


def _flatten_visible_values(values: Mapping[str, Any] | Sequence[Any] | str) -> Iterable[str]:
    if isinstance(values, str):
        yield values
        return
    if isinstance(values, Mapping):
        for value in values.values():
            yield from _flatten_visible_values(value)
        return
    if isinstance(values, Sequence) and not isinstance(values, (bytes, bytearray)):
        for value in values:
            yield from _flatten_visible_values(value)
        return
    if values is not None:
        yield str(values)


__all__ = [
    "MODEL_VISIBLE_FORBIDDEN_TERMS",
    "OpenAIOperatorEnactmentAction",
    "OpenAIOperatorEnactmentDecision",
    "RECHECK_PROMPT_NAME",
    "build_openai_operator_enactment_decision",
    "find_internal_terms_in_model_visible_values",
    "model_visible_values_are_silent",
]
