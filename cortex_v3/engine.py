"""Shared provider-neutral verified-turn engine for Cortex v3."""

from __future__ import annotations

from .contracts import ProviderTurnRequest, VerifiedTurnRequest, VerifiedTurnResult
from .preservation import (
    choose_preservation_move,
    derive_preservation_state,
    narrow_repair_contract,
)
from .verifier import (
    build_verified_work_input_text,
    build_verified_work_instructions,
    build_verified_work_repair_prompt,
    verify_verified_work_result,
)
from .providers.base import ProviderAdapter


def run_verified_turn(
    adapter: ProviderAdapter,
    request: VerifiedTurnRequest,
) -> VerifiedTurnResult:
    if not isinstance(request, VerifiedTurnRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_verified_turn.request must be VerifiedTurnRequest, "
            f"got {actual_type}."
        )

    first_provider_request = ProviderTurnRequest(
        provider=adapter.provider,
        model=request.model,
        prompt=build_verified_work_input_text(
            request.task_prompt,
            request.work_contract,
            context_mode=request.context_mode,
        ),
        instructions=build_verified_work_instructions(request.work_contract),
        metadata=request.metadata,
        max_output_tokens=request.max_output_tokens,
    )
    first_response = adapter.execute_turn(first_provider_request)
    effective_file_map, verification = verify_verified_work_result(
        first_response.output_text,
        request.work_contract,
    )
    current_state = derive_preservation_state(
        None,
        request.work_contract,
        verification,
        remaining_repairs=request.work_contract.max_repair_turns,
    )
    decision = choose_preservation_move(current_state)
    raw_trace = list(first_response.raw_events)
    warnings = list(first_response.warnings)
    attempt_count = 1
    final_output_text = first_response.output_text
    final_verification = verification

    if decision == "repair":
        repair_contract = narrow_repair_contract(
            request.work_contract,
            current_state.lawful_repair_surface,
        )
        repair_request = ProviderTurnRequest(
            provider=adapter.provider,
            model=request.model,
            prompt=build_verified_work_repair_prompt(
                request.task_prompt,
                repair_contract,
                current_state,
                writable_file_map=effective_file_map,
                context_mode=request.context_mode,
                visible_context_paths=request.work_contract.allowed_write_paths,
            ),
            instructions=build_verified_work_instructions(repair_contract),
            metadata=request.metadata,
            max_output_tokens=request.max_output_tokens,
        )
        repair_response = adapter.execute_turn(repair_request)
        raw_trace.extend(repair_response.raw_events)
        warnings.extend(repair_response.warnings)
        final_output_text = repair_response.output_text
        effective_file_map, final_verification = verify_verified_work_result(
            repair_response.output_text,
            repair_contract,
            preserved_file_map=effective_file_map,
            verifier_contract=request.work_contract,
        )
        current_state = derive_preservation_state(
            current_state.task_anchor,
            request.work_contract,
            final_verification,
            remaining_repairs=0,
        )
        decision = choose_preservation_move(current_state)
        attempt_count = 2

    return VerifiedTurnResult(
        provider=adapter.provider,
        attempt_count=attempt_count,
        decision=decision,
        result_text=final_output_text,
        verification=final_verification,
        parsed_paths=final_verification.parsed_paths if final_verification is not None else (),
        raw_trace=tuple(raw_trace),
        warnings=tuple(warnings),
    )


__all__ = ["run_verified_turn"]
