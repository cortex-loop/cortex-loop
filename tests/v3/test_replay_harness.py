"""Replay harness tests for Cortex v3."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from cortex_v3.contracts import (
    ProviderTurnRequest,
    ProviderTurnResponse,
    VerifiedTurnRequest,
    WorkContract,
)
from lab.v3.replay import ReplayTask, run_replay_case
from tests.product._verified_work_fixtures import (
    VALID_FILE_MAP,
    VALID_NORMALIZE_PORT_FILE_MAP,
    render_full_files_result,
)


@dataclass
class _QueueAdapter:
    provider: str
    responses: list[ProviderTurnResponse]

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        del request
        if not self.responses:
            raise AssertionError("Queue adapter response queue exhausted.")
        return self.responses.pop(0)


def _bookmarks_task() -> ReplayTask:
    return ReplayTask(
        task_id="bookmarks",
        request=VerifiedTurnRequest(
            model="test-model",
            task_prompt="build bookmarks app",
            work_contract=WorkContract(
                allowed_write_paths=(
                    "src/bookmarks_api/main.py",
                    "src/bookmarks_api/models.py",
                    "src/bookmarks_api/store.py",
                ),
                verification_profile="python_workspace_pytest_v1",
                max_repair_turns=1,
            ),
            instructions="Return protocol blocks only.",
        ),
    )


def _normalize_port_task() -> ReplayTask:
    return ReplayTask(
        task_id="normalize-port",
        request=VerifiedTurnRequest(
            model="test-model",
            task_prompt="fix normalize_port",
            work_contract=WorkContract(
                allowed_write_paths=("src/normalize_port.py",),
                verification_profile="python_workspace_pytest_port_fix_v1",
                max_repair_turns=1,
            ),
            instructions="Return protocol blocks only.",
        ),
    )


@pytest.mark.parametrize("provider", ["openai", "claude", "gemini"])
def test_replay_harness_exposes_three_comparison_arms(provider: str) -> None:
    result_text = render_full_files_result(VALID_FILE_MAP)
    task = _bookmarks_task()
    arm_inputs = {
        "verified_first_attempt": _QueueAdapter(
            provider=provider,
            responses=[ProviderTurnResponse(provider=provider, output_text=result_text, raw_events=tuple())],
        ),
        "verified_with_repair": _QueueAdapter(
            provider=provider,
            responses=[ProviderTurnResponse(provider=provider, output_text=result_text, raw_events=tuple())],
        ),
        "plain_feedback": _QueueAdapter(
            provider=provider,
            responses=[ProviderTurnResponse(provider=provider, output_text=result_text, raw_events=tuple())],
        ),
    }

    outcomes = {
        arm: run_replay_case(adapter, task, arm=arm)
        for arm, adapter in arm_inputs.items()
    }

    assert set(outcomes) == {
        "verified_first_attempt",
        "verified_with_repair",
        "plain_feedback",
    }
    for arm, outcome in outcomes.items():
        assert outcome.task_id == "bookmarks"
        assert outcome.provider == provider
        assert outcome.arm == arm
        assert outcome.verification_status == "passed"
        assert outcome.decision == "continue"


@pytest.mark.parametrize("provider", ["openai", "claude", "gemini"])
@pytest.mark.parametrize(
    ("arm", "blocked_text", "expected_decision", "expected_failure_class"),
    [
        (
            "verified_first_attempt",
            "=== BLOCKED: needs_user_input ===\nNeed the archive retention policy.\n=== END BLOCKED ===",
            "check",
            "blocked_missing_info",
        ),
        (
            "verified_with_repair",
            "=== BLOCKED: needs_user_input ===\nNeed the archive retention policy.\n=== END BLOCKED ===",
            "check",
            "blocked_missing_info",
        ),
        (
            "plain_feedback",
            "=== BLOCKED: needs_user_input ===\nNeed the archive retention policy.\n=== END BLOCKED ===",
            "check",
            "blocked_missing_info",
        ),
        (
            "verified_first_attempt",
            "=== BLOCKED: unsafe_request ===\nDeleting production data is unsafe.\n=== END BLOCKED ===",
            "stop",
            "blocked_unsafe",
        ),
        (
            "verified_with_repair",
            "=== BLOCKED: unsafe_request ===\nDeleting production data is unsafe.\n=== END BLOCKED ===",
            "stop",
            "blocked_unsafe",
        ),
        (
            "plain_feedback",
            "=== BLOCKED: unsafe_request ===\nDeleting production data is unsafe.\n=== END BLOCKED ===",
            "stop",
            "blocked_unsafe",
        ),
    ],
)
def test_replay_harness_preserves_blocked_semantics_across_arms(
    provider: str,
    arm: str,
    blocked_text: str,
    expected_decision: str,
    expected_failure_class: str,
) -> None:
    adapter = _QueueAdapter(
        provider=provider,
        responses=[ProviderTurnResponse(provider=provider, output_text=blocked_text, raw_events=tuple())],
    )

    outcome = run_replay_case(adapter, _bookmarks_task(), arm=arm)

    assert outcome.provider == provider
    assert outcome.arm == arm
    assert outcome.attempt_count == 1
    assert outcome.verification_status == "blocked"
    assert outcome.failure_class == expected_failure_class
    assert outcome.decision == expected_decision


@pytest.mark.parametrize("provider", ["openai", "claude", "gemini"])
def test_plain_feedback_retries_only_repairable_failures(provider: str) -> None:
    broken_result = render_full_files_result(
        {"src/normalize_port.py": "def normalize_port(value: int | str) -> int:\n    return int(\n"}
    )
    repaired_result = render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP)
    adapter = _QueueAdapter(
        provider=provider,
        responses=[
            ProviderTurnResponse(provider=provider, output_text=broken_result, raw_events=tuple()),
            ProviderTurnResponse(provider=provider, output_text=repaired_result, raw_events=tuple()),
        ],
    )

    outcome = run_replay_case(adapter, _normalize_port_task(), arm="plain_feedback")

    assert outcome.provider == provider
    assert outcome.attempt_count == 2
    assert outcome.verification_status == "passed"
    assert outcome.failure_class is None
    assert outcome.decision == "continue"
