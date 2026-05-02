from __future__ import annotations

import pytest

from cortex.hosts.openai.operator_enactment import (
    RECHECK_PROMPT_NAME,
    VERIFICATION_CONTINUATION_PROMPT_NAME,
    OpenAIOperatorEnactmentAction,
    build_openai_operator_enactment_decision,
    find_internal_terms_in_model_visible_values,
    model_visible_values_are_silent,
)


def _route_payload(
    *,
    profile: str = "inspect_light",
    allow_extra_read_pass: bool = True,
    blocked_reason: str | None = None,
) -> dict[str, object]:
    return {
        "route_profile": profile,
        "route_budget": {
            "max_turns": 1,
            "max_retries": 1 if allow_extra_read_pass else 0,
            "allow_resume": False,
            "allow_extra_read_pass": allow_extra_read_pass,
            "require_verification": False,
            "stop_on_quota": True,
            "stop_on_capacity": True,
        },
        "route_reason_tags": ["task_mode:inspect"],
        "blocked_reason": blocked_reason,
    }


def _policy_payload(*, allow_extra_read_pass: bool = True) -> dict[str, object]:
    return {
        "default_profile_bonus": 0.0,
        "switch_margin": 0.08,
        "stop_threshold": 0.75,
        "allow_extra_read_pass": allow_extra_read_pass,
        "verification_intensity": 0.5,
        "debt_guard_bias": 0.0,
        "debt_default_penalty": 0.0,
        "debt_verification_bias": 1.0 if allow_extra_read_pass else 0.0,
    }


def _debt_payload(*, verification_relief_bias: float = 1.0) -> dict[str, object]:
    return {
        "resolution_pressure": verification_relief_bias,
        "persistence": verification_relief_bias,
        "forward_commit_pressure": 0.0,
        "goal_drag": 0.0,
        "debt_pressure": 0.6 * verification_relief_bias,
        "verification_relief_bias": verification_relief_bias,
        "reason_tags": ["verification-relief"] if verification_relief_bias else [],
    }


def test_blocked_route_returns_block_and_suppresses_invocation() -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(
            profile="blocked",
            allow_extra_read_pass=False,
            blocked_reason="brain_capability_mismatch",
        ),
        executive_policy_view_payload=_policy_payload(allow_extra_read_pass=False),
        debt_control_payload=_debt_payload(verification_relief_bias=0.0),
        scenario_id="truth_gap",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.BLOCK
    assert decision.invocation_allowed is False
    assert decision.blocked_reason == "brain_capability_mismatch"
    assert decision.model_bound_difference_kind == "block"


def test_inspect_route_with_verification_relief_returns_resume_recheck_when_allowed() -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(),
        scenario_id="truth_gap",
        first_result_kind="truthful_incomplete",
        provider_limit_interference=False,
        thread_id="thread-1",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.RESUME_RECHECK
    assert decision.resume_prompt_name == RECHECK_PROMPT_NAME
    assert decision.thread_policy == "resume_existing_thread"
    assert decision.resume_recheck_allowed is True
    assert decision.model_bound_difference_kind == "resume_recheck"


@pytest.mark.parametrize(
    ("first_result_kind", "provider_limit_interference", "thread_id", "blocked"),
    [
        ("unsupported_completion", False, "thread-1", "first_result_not_truthful_incomplete"),
        ("truthful_incomplete", True, "thread-1", "provider_limit_interference"),
        ("truthful_incomplete", False, None, "missing_thread_id"),
    ],
)
def test_resume_recheck_requires_exact_allowed_conditions(
    first_result_kind: str,
    provider_limit_interference: bool,
    thread_id: str | None,
    blocked: str,
) -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(),
        scenario_id="truth_gap",
        first_result_kind=first_result_kind,
        provider_limit_interference=provider_limit_interference,
        thread_id=thread_id,
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.thread_policy == "persistent_for_possible_recheck"
    assert decision.resume_recheck_armed is True
    assert decision.resume_recheck_allowed is False
    assert decision.resume_recheck_blocked_reason == blocked


def test_neutral_clean_route_returns_single_invoke() -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(verification_relief_bias=0.0),
        scenario_id="truth_gap",
        first_result_kind="truthful_incomplete",
        provider_limit_interference=False,
        thread_id="thread-1",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.thread_policy == "ephemeral_allowed"
    assert decision.resume_prompt_name is None
    assert decision.model_bound_difference_kind == "none"


def test_verification_debt_arms_persistent_thread_before_result_without_fixture_id() -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(),
        scenario_id="general_verification_witness",
        first_result_kind=None,
        provider_limit_interference=False,
        thread_id=None,
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.resume_prompt_name == VERIFICATION_CONTINUATION_PROMPT_NAME
    assert decision.thread_policy == "persistent_for_possible_verification"
    assert decision.resume_verification_armed is True
    assert decision.resume_verification_allowed is False
    assert decision.resume_verification_blocked_reason == (
        "first_result_not_visible_success_unverified"
    )
    assert decision.model_bound_difference_kind == "thread_persistence"


@pytest.mark.parametrize("scenario_id", ["general_verification_witness", "unrelated_dashboard_control"])
def test_visible_success_unverified_returns_general_verification_continuation(
    scenario_id: str,
) -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(),
        scenario_id=scenario_id,
        first_result_kind="visible_success_unverified",
        provider_limit_interference=False,
        thread_id="thread-verify",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.RESUME_VERIFICATION
    assert decision.resume_prompt_name == VERIFICATION_CONTINUATION_PROMPT_NAME
    assert decision.thread_policy == "resume_existing_thread"
    assert decision.resume_verification_armed is True
    assert decision.resume_verification_allowed is True
    assert decision.model_bound_difference_kind == "resume_verification"


@pytest.mark.parametrize(
    ("first_result_kind", "provider_limit_interference", "thread_id", "blocked"),
    [
        ("clean_verified", False, "thread-1", "first_result_not_visible_success_unverified"),
        ("visible_success_unverified", True, "thread-1", "provider_limit_interference"),
        ("visible_success_unverified", False, None, "missing_thread_id"),
    ],
)
def test_resume_verification_requires_structured_visible_success_unverified_state(
    first_result_kind: str,
    provider_limit_interference: bool,
    thread_id: str | None,
    blocked: str,
) -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(),
        scenario_id="general_verification_witness",
        first_result_kind=first_result_kind,
        provider_limit_interference=provider_limit_interference,
        thread_id=thread_id,
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.thread_policy == "ephemeral_allowed"
    assert decision.resume_verification_armed is True
    assert decision.resume_verification_allowed is False
    assert decision.resume_verification_blocked_reason == blocked
    assert decision.resume_prompt_name is None
    assert decision.model_bound_difference_kind == "none"


def test_clean_paid_down_route_does_not_arm_verification_continuation() -> None:
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=_route_payload(),
        executive_policy_view_payload=_policy_payload(),
        debt_control_payload=_debt_payload(verification_relief_bias=0.0),
        scenario_id="general_verification_witness",
        first_result_kind="clean_verified",
        provider_limit_interference=False,
        thread_id="thread-clean",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.thread_policy == "ephemeral_allowed"
    assert decision.resume_prompt_name is None
    assert decision.resume_verification_armed is False
    assert decision.model_bound_difference_kind == "none"


def test_guarded_execute_preserves_budget_without_prompt_mutation() -> None:
    route_payload = _route_payload(
        profile="execute_guarded",
        allow_extra_read_pass=False,
    )
    route_payload["route_budget"]["require_verification"] = True
    decision = build_openai_operator_enactment_decision(
        operator_route_payload=route_payload,
        executive_policy_view_payload=_policy_payload(allow_extra_read_pass=False),
        debt_control_payload=_debt_payload(verification_relief_bias=0.0),
        scenario_id="truth_gap",
    )

    assert decision.action is OpenAIOperatorEnactmentAction.INVOKE
    assert decision.route_profile == "execute_guarded"
    assert decision.route_budget["require_verification"] is True
    assert decision.resume_prompt_name is None
    assert decision.thread_policy == "ephemeral_allowed"


def test_forbidden_internal_vocabulary_is_not_allowed_in_model_visible_fields() -> None:
    assert model_visible_values_are_silent(
        {
            "prompt": "Re-check the prior diagnosis without editing files.",
            "argv": ["codex", "exec", "--json", "Re-check the prior diagnosis."],
        }
    )
    assert find_internal_terms_in_model_visible_values(
        {"prompt": "Cortex debt_control says raise brake."}
    ) == ("Cortex", "debt_control", "brake")
