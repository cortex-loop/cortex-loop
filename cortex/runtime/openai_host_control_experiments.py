"""Internal-only verified-work ablation wrapper over the accepted OpenAI host-control path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from cortex.runtime.openai import OpenAIRuntimeSession, run_openai_runtime_verification_step
from cortex.runtime.openai_host_control import (
    OpenAIHostControlRequest,
    OpenAIHostControlResult,
    OpenAIResponseStreamTransport,
    OpenAIResponseStreamTransportError,
    _last_response_id,
    _run_openai_host_control_attempt,
    run_openai_host_control,
)
from cortex.runtime.openai_host_transport import execute_openai_response_stream_turn
from cortex.runtime.verified_work_runtime import (
    VerifiedWorkContextMode,
    build_verified_work_input_text,
    build_verified_work_instructions,
    build_verified_work_repair_ticket,
    verify_verified_work_result,
)


VisibleContractBinding = Literal["on", "off"]
VerificationBinding = Literal["on", "off"]
RepairTurn = Literal["on", "off"]
RepairTicketStyle = Literal["factual", "minimal"]
VisibleContextVariant = Literal[
    "default",
    "writable_files_only",
    "writable_files_plus_visible_tests",
]


@dataclass(frozen=True, slots=True)
class OpenAIHostControlAblationConfig:
    visible_contract_binding: VisibleContractBinding = "on"
    verification_binding: VerificationBinding = "on"
    repair_turn: RepairTurn = "on"
    repair_ticket_style: RepairTicketStyle = "factual"
    visible_context_variant: VisibleContextVariant = "default"

    def __post_init__(self) -> None:
        if self.visible_contract_binding not in {"on", "off"}:
            raise ValueError(
                "OpenAIHostControlAblationConfig.visible_contract_binding must be `on` or `off`."
            )
        if self.verification_binding not in {"on", "off"}:
            raise ValueError(
                "OpenAIHostControlAblationConfig.verification_binding must be `on` or `off`."
            )
        if self.repair_turn not in {"on", "off"}:
            raise ValueError("OpenAIHostControlAblationConfig.repair_turn must be `on` or `off`.")
        if self.repair_ticket_style not in {"factual", "minimal"}:
            raise ValueError(
                "OpenAIHostControlAblationConfig.repair_ticket_style must be `factual` or `minimal`."
            )
        if self.visible_context_variant not in {
            "default",
            "writable_files_only",
            "writable_files_plus_visible_tests",
        }:
            raise ValueError(
                "OpenAIHostControlAblationConfig.visible_context_variant must be accepted."
            )

    def is_default(self) -> bool:
        return (
            self.visible_contract_binding == "on"
            and self.verification_binding == "on"
            and self.repair_turn == "on"
            and self.repair_ticket_style == "factual"
            and self.visible_context_variant == "default"
        )

    def effective_context_mode(self) -> VerifiedWorkContextMode:
        if self.visible_contract_binding == "off":
            return "off"
        if self.visible_context_variant == "writable_files_only":
            return "writable_files_only"
        if self.visible_context_variant == "writable_files_plus_visible_tests":
            return "writable_files_plus_visible_tests"
        return "default"

    def as_payload(self) -> dict[str, str]:
        return {
            "visible_contract_binding": self.visible_contract_binding,
            "verification_binding": self.verification_binding,
            "repair_turn": self.repair_turn,
            "repair_ticket_style": self.repair_ticket_style,
            "visible_context_variant": self.visible_context_variant,
        }


def run_openai_host_control_experiment(
    request: OpenAIHostControlRequest,
    session: OpenAIRuntimeSession | None = None,
    *,
    transport: OpenAIResponseStreamTransport | None = None,
    ablation_config: OpenAIHostControlAblationConfig | None = None,
) -> tuple[OpenAIHostControlResult, OpenAIRuntimeSession]:
    if ablation_config is None or ablation_config.is_default():
        return run_openai_host_control(request, session, transport=transport)
    if request.work_contract is None:
        return run_openai_host_control(request, session, transport=transport)
    if not isinstance(request, OpenAIHostControlRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_openai_host_control_experiment.request must be OpenAIHostControlRequest, "
            f"got {actual_type}."
        )
    if session is not None and not isinstance(session, OpenAIRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_openai_host_control_experiment.session must be OpenAIRuntimeSession | None, "
            f"got {actual_type}."
        )

    current_session = session or OpenAIRuntimeSession()
    transport_callable = transport if transport is not None else execute_openai_response_stream_turn
    if not callable(transport_callable):
        actual_type = type(transport_callable).__name__
        raise TypeError(
            "run_openai_host_control_experiment.transport must be callable when provided, "
            f"got {actual_type}."
        )

    verified_request = OpenAIHostControlRequest(
        action_tag=request.action_tag,
        model=request.model,
        input_text=build_verified_work_input_text(
            request.input_text,
            request.work_contract,
            context_mode=ablation_config.effective_context_mode(),
        ),
        instructions=build_verified_work_instructions(request.work_contract),
        metadata=request.metadata,
        max_output_tokens=request.max_output_tokens,
        work_contract=request.work_contract,
    )
    raw_events, records, current_session, result_text = _run_openai_host_control_attempt(
        verified_request,
        current_session,
        transport_callable=transport_callable,
    )
    try:
        _, verification = verify_verified_work_result(
            result_text,
            request.work_contract,
        )
    except RuntimeError as exc:
        raise OpenAIResponseStreamTransportError(
            f"OpenAI verified-work verifier failed: {exc}"
        ) from exc

    if ablation_config.verification_binding == "on":
        current_session = run_openai_runtime_verification_step(
            verification,
            current_session,
            work_contract=request.work_contract,
            remaining_repairs=request.work_contract.max_repair_turns,
        )

    attempt_count = 1
    final_result_text = result_text
    repair_allowed = (
        ablation_config.verification_binding == "on"
        and ablation_config.repair_turn == "on"
        and request.work_contract.max_repair_turns > 0
        and current_session.next_recommended_move == "repair"
    )
    if repair_allowed:
        response_id = _last_response_id(raw_events)
        if response_id is None:
            raise OpenAIResponseStreamTransportError(
                "OpenAI verified-work continuation requires a response_id on the first attempt."
            )
        repair_ticket = build_verified_work_repair_ticket(
            verification,
            style=ablation_config.repair_ticket_style,
            repair_surface=request.work_contract.allowed_write_paths,
        )
        repair_events, repair_records, repair_session, repair_result_text = _run_openai_host_control_attempt(
            verified_request,
            current_session,
            transport_callable=transport_callable,
            previous_response_id=response_id,
            input_text_override=repair_ticket,
        )
        records.extend(repair_records)
        final_result_text = repair_result_text
        try:
            _, verification = verify_verified_work_result(
                repair_result_text,
                request.work_contract,
            )
        except RuntimeError as exc:
            raise OpenAIResponseStreamTransportError(
                f"OpenAI verified-work verifier failed: {exc}"
            ) from exc
        current_session = run_openai_runtime_verification_step(
            verification,
            repair_session,
            work_contract=request.work_contract,
            remaining_repairs=0,
        )
        attempt_count = 2

    return OpenAIHostControlResult(
        action_tag=request.action_tag,
        records=tuple(records),
        result_text=final_result_text,
        verification=verification,
        attempt_count=attempt_count,
    ), current_session


__all__ = [
    "OpenAIHostControlAblationConfig",
    "run_openai_host_control_experiment",
]
