"""Minimal replay harness for Cortex v3 verified-work comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from cortex_v3.contracts import VerifiedTurnRequest, WorkContract
from cortex_v3.engine import run_verified_turn
from cortex_v3.preservation import choose_preservation_move, derive_preservation_state
from cortex_v3.providers.base import ProviderAdapter
from cortex_v3.verifier import verify_verified_work_result

_REPAIRABLE_FAILURE_CLASSES = frozenset(
    {"output_invalid", "import_smoke_failed", "test_failed"}
)


@dataclass(frozen=True, slots=True)
class ReplayTask:
    task_id: str
    request: VerifiedTurnRequest


@dataclass(frozen=True, slots=True)
class ReplayOutcome:
    task_id: str
    provider: str
    model: str
    arm: str
    attempt_count: int
    decision: str
    verification_status: str | None
    failure_class: str | None
    pytest_passed: int | None
    pytest_failed: int | None
    parsed_paths: tuple[str, ...]
    duration_seconds: float
    warnings: tuple[str, ...]


def run_replay_case(
    adapter: ProviderAdapter,
    task: ReplayTask,
    *,
    arm: str,
) -> ReplayOutcome:
    started_at = perf_counter()
    if arm == "verified_first_attempt":
        request = _clone_request_with_repairs(task.request, max_repair_turns=0)
        result = run_verified_turn(adapter, request)
    elif arm == "verified_with_repair":
        result = run_verified_turn(adapter, task.request)
    elif arm == "plain_feedback":
        result = _run_plain_feedback_turn(adapter, task.request)
    else:
        raise ValueError("run_replay_case.arm must be accepted.")
    duration_seconds = perf_counter() - started_at
    verification = result.verification
    return ReplayOutcome(
        task_id=task.task_id,
        provider=result.provider,
        model=task.request.model,
        arm=arm,
        attempt_count=result.attempt_count,
        decision=result.decision,
        verification_status=None if verification is None else verification.status,
        failure_class=None if verification is None else verification.failure_class,
        pytest_passed=None if verification is None else verification.pytest_passed,
        pytest_failed=None if verification is None else verification.pytest_failed,
        parsed_paths=result.parsed_paths,
        duration_seconds=duration_seconds,
        warnings=result.warnings,
    )


def _clone_request_with_repairs(
    request: VerifiedTurnRequest,
    *,
    max_repair_turns: int,
) -> VerifiedTurnRequest:
    return VerifiedTurnRequest(
        model=request.model,
        task_prompt=request.task_prompt,
        work_contract=WorkContract(
            allowed_write_paths=request.work_contract.allowed_write_paths,
            verification_profile=request.work_contract.verification_profile,
            output_carrier=request.work_contract.output_carrier,
            max_repair_turns=max_repair_turns,
        ),
        instructions=request.instructions,
        metadata=dict(request.metadata),
        max_output_tokens=request.max_output_tokens,
        context_mode=request.context_mode,
    )


def _run_plain_feedback_turn(
    adapter: ProviderAdapter,
    request: VerifiedTurnRequest,
):
    from cortex_v3.contracts import ProviderTurnRequest, VerifiedTurnResult

    first_request = ProviderTurnRequest(
        provider=adapter.provider,
        model=request.model,
        prompt=request.task_prompt,
        instructions=request.instructions,
        metadata=request.metadata,
        max_output_tokens=request.max_output_tokens,
    )
    first_response = adapter.execute_turn(first_request)
    _, verification = verify_verified_work_result(
        first_response.output_text,
        request.work_contract,
    )
    attempt_count = 1
    final_response = first_response
    final_verification = verification
    if (
        verification.failure_class in _REPAIRABLE_FAILURE_CLASSES
        and request.work_contract.max_repair_turns > 0
    ):
        feedback_lines = [
            request.task_prompt.strip(),
            "",
            "The previous answer failed external verification.",
            f"failure_class: {verification.failure_class}",
        ]
        if verification.failing_tests:
            feedback_lines.append(
                "failing_tests: " + ", ".join(verification.failing_tests)
            )
        if verification.first_failure_excerpt:
            feedback_lines.append(
                "first_failure_excerpt: " + verification.first_failure_excerpt
            )
        repair_request = ProviderTurnRequest(
            provider=adapter.provider,
            model=request.model,
            prompt="\n".join(feedback_lines),
            instructions=request.instructions,
            metadata=request.metadata,
            max_output_tokens=request.max_output_tokens,
        )
        final_response = adapter.execute_turn(repair_request)
        _, final_verification = verify_verified_work_result(
            final_response.output_text,
            request.work_contract,
        )
        attempt_count = 2
    final_state = derive_preservation_state(
        None,
        request.work_contract,
        final_verification,
        remaining_repairs=0,
    )
    decision = choose_preservation_move(final_state)
    return VerifiedTurnResult(
        provider=adapter.provider,
        attempt_count=attempt_count,
        decision=decision,
        result_text=final_response.output_text,
        verification=final_verification,
        parsed_paths=final_verification.parsed_paths,
        raw_trace=tuple(first_response.raw_events + final_response.raw_events)
        if attempt_count == 2
        else first_response.raw_events,
        warnings=tuple(first_response.warnings + final_response.warnings)
        if attempt_count == 2
        else first_response.warnings,
    )


__all__ = ["ReplayOutcome", "ReplayTask", "run_replay_case"]
