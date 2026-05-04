"""Stdin/stdout client for the Codex App/CLI product Stop hook.

The client is intentionally thin: it decodes optional private runtime snapshot
stimuli, lets the product hook coordinator derive state from lifecycle events
when no snapshot is supplied, and maps the host response to the Codex hook JSON
contract. It owns no SRE policy and no repo workflow guardrail.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, TextIO

from cortex.hosts.openai.codex_app_cli_hook_coordinator import (
    OpenAICodexHookCoordinatorResult,
    OpenAICodexJsonStateStore,
    OpenAICodexOperatorRouteView,
    OpenAICodexRuntimeSnapshot,
    handle_openai_codex_hook_payload,
)
from cortex.sre.debt_control import DebtControlPressure
from cortex.sre.expectations import ExpectationLedger, ResolutionDeficitState
from cortex.sre.operator_routing import (
    OperatorBrainCapabilityAssessment,
    OperatorBrainCapabilityMismatchLevel,
    OperatorContractBindingProfile,
    OperatorRouteProfile,
)


Coordinator = Callable[..., OpenAICodexHookCoordinatorResult]


@dataclass(frozen=True, slots=True)
class HookClientRunResult:
    exit_code: int
    stdout_payload: dict[str, str] | None
    stderr_diagnostic: str | None
    diagnostics_row: dict[str, object]


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    return run_hook_client(
        argv=effective_argv,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def run_hook_client(
    *,
    argv: list[str] | None = None,
    stdin: TextIO,
    stdout: TextIO,
    stderr: TextIO,
    coordinator: Coordinator = handle_openai_codex_hook_payload,
) -> int:
    result = _run_hook_client(
        argv=argv,
        stdin_text=stdin.read(),
        coordinator=coordinator,
    )
    if result.stdout_payload is not None:
        stdout.write(json.dumps(result.stdout_payload, separators=(",", ":")))
        stdout.write("\n")
    if result.stderr_diagnostic:
        stderr.write(result.stderr_diagnostic)
        stderr.write("\n")
    _append_diagnostics_from_argv(argv, result.diagnostics_row)
    return result.exit_code


def _run_hook_client(
    *,
    argv: list[str] | None,
    stdin_text: str,
    coordinator: Coordinator,
) -> HookClientRunResult:
    try:
        args = _parse_args(argv)
    except ValueError as exc:
        return _fail_open("argument_parse_failed", {"error": str(exc)})

    payload, payload_error = _parse_hook_payload(stdin_text)
    if payload_error is not None:
        return _fail_open(payload_error, {"input_sha256": _hash_text(stdin_text)})

    state_root = Path(args.state_root)
    runtime_snapshot: OpenAICodexRuntimeSnapshot | None = None
    snapshot_payload: Mapping[str, Any] | None = None
    snapshot_hash: str | None = None
    if args.runtime_snapshot is not None:
        snapshot_path = Path(args.runtime_snapshot)
        try:
            snapshot_payload = load_runtime_snapshot_payload(snapshot_path)
            snapshot_hash = _stable_hash(snapshot_payload)
            runtime_snapshot = runtime_snapshot_from_payload(snapshot_payload)
        except Exception as exc:  # fail-open hook infrastructure path
            return _fail_open(
                "runtime_snapshot_unreadable",
                {
                    "snapshot_path": str(snapshot_path),
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )

    try:
        result = coordinator(
            payload,
            state_store=OpenAICodexJsonStateStore(state_root),
            runtime_snapshot=runtime_snapshot,
        )
    except Exception as exc:  # fail-open hook infrastructure path
        return _fail_open(
            "coordinator_error",
            {"error": f"{type(exc).__name__}: {exc}"},
        )

    stdout_payload = result.host_response.stdout_payload
    rendered_text = (
        stdout_payload.get("reason")
        if isinstance(stdout_payload, Mapping)
        and isinstance(stdout_payload.get("reason"), str)
        else None
    )
    diagnostics_row = {
        "event": "codex_app_cli_product_hook_client",
        "fail_open": False,
        "runtime_snapshot_loaded": runtime_snapshot is not None,
        "runtime_snapshot_hash": snapshot_hash,
        "actual_rendered_text_hash": _hash_text(rendered_text) if rendered_text else None,
        "stdout_payload": stdout_payload,
        "coordinator": result.as_diagnostics(),
    }
    return HookClientRunResult(
        exit_code=0,
        stdout_payload=stdout_payload,
        stderr_diagnostic=None,
        diagnostics_row=diagnostics_row,
    )


def load_runtime_snapshot_payload(path: Path | str) -> Mapping[str, Any]:
    snapshot_path = Path(path)
    with snapshot_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"runtime snapshot must be a mapping, got {actual_type}.")
    return payload


def runtime_snapshot_from_payload(payload: Mapping[str, Any]) -> OpenAICodexRuntimeSnapshot:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"runtime snapshot payload must be a mapping, got {actual_type}.")
    current_step = _non_negative_int(payload.get("current_step"), default=0)
    expectation_ledger = ExpectationLedger.from_payload(payload.get("expectation_ledger"))
    resolution_deficit = (
        _resolution_deficit_from_payload(payload["resolution_deficit"])
        if isinstance(payload.get("resolution_deficit"), Mapping)
        else expectation_ledger.resolution_deficit(current_step=current_step)
    )
    return OpenAICodexRuntimeSnapshot(
        expectation_ledger=expectation_ledger,
        resolution_deficit=resolution_deficit,
        debt_control=_debt_control_from_payload(payload.get("debt_control")),
        operator_route=_operator_route_from_payload(
            payload.get("operator_route_view", payload.get("operator_route"))
        ),
        current_step=current_step,
        closure_required=bool(payload.get("closure_required", False)),
        closure_reason_tags=_string_tuple(payload.get("closure_reason_tags")),
        warnings=_string_tuple(payload.get("warnings")),
    )


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument("--state-root")
    parser.add_argument("--runtime-snapshot")
    parser.add_argument("--diagnostics-path")
    args, unknown = parser.parse_known_args(argv)
    if unknown:
        raise ValueError(f"unknown arguments: {' '.join(unknown)}")
    if not args.state_root:
        raise ValueError("--state-root is required")
    return args


def _parse_hook_payload(stdin_text: str) -> tuple[Mapping[str, Any], str | None]:
    try:
        parsed = json.loads(stdin_text or "{}")
    except json.JSONDecodeError:
        return {}, "malformed_hook_payload"
    if not isinstance(parsed, Mapping):
        return {}, "hook_payload_not_object"
    return parsed, None


def _resolution_deficit_from_payload(payload: Mapping[str, Any]) -> ResolutionDeficitState:
    return ResolutionDeficitState(
        due_weight=_non_negative_float(payload.get("due_weight"), default=0.0),
        fulfilled_weight=_non_negative_float(payload.get("fulfilled_weight"), default=0.0),
        overdue_weight=_non_negative_float(payload.get("overdue_weight"), default=0.0),
        suspended_weight=_non_negative_float(payload.get("suspended_weight"), default=0.0),
        relief_weight=_non_negative_float(payload.get("relief_weight"), default=0.0),
        negative_prediction_error=_unit_float(
            payload.get("negative_prediction_error"),
            default=0.0,
        ),
        dominant_deficit_kind=_optional_string(payload.get("dominant_deficit_kind")),
    )


def _debt_control_from_payload(payload: Any) -> DebtControlPressure:
    if payload is None:
        return DebtControlPressure()
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"debt_control must be a mapping when present, got {actual_type}.")
    return DebtControlPressure(
        resolution_pressure=_unit_float(payload.get("resolution_pressure"), default=0.0),
        persistence=_unit_float(payload.get("persistence"), default=0.0),
        forward_commit_pressure=_unit_float(
            payload.get("forward_commit_pressure"),
            default=0.0,
        ),
        goal_drag=_unit_float(payload.get("goal_drag"), default=0.0),
        debt_pressure=_unit_float(payload.get("debt_pressure"), default=0.0),
        verification_relief_bias=_unit_float(
            payload.get("verification_relief_bias"),
            default=0.0,
        ),
        reason_tags=frozenset(_string_tuple(payload.get("reason_tags"))),
    )


def _operator_route_from_payload(payload: Any) -> OpenAICodexOperatorRouteView:
    if payload is None:
        return OpenAICodexOperatorRouteView()
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"operator route must be a mapping when present, got {actual_type}.")
    profile_value = _optional_string(payload.get("profile")) or "execute_standard"
    return OpenAICodexOperatorRouteView(
        profile=OperatorRouteProfile(profile_value),
        blocked_reason=_optional_string(payload.get("blocked_reason")),
        brain_capability_assessment=_brain_capability_from_payload(
            payload.get("brain_capability_assessment")
        ),
    )


def _brain_capability_from_payload(payload: Any) -> OperatorBrainCapabilityAssessment | None:
    if payload is None:
        return None
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "brain_capability_assessment must be a mapping when present, "
            f"got {actual_type}."
        )
    return OperatorBrainCapabilityAssessment(
        continuity_mismatch=_unit_float(payload.get("continuity_mismatch"), default=0.0),
        verification_mismatch=_unit_float(payload.get("verification_mismatch"), default=0.0),
        contract_mismatch=_unit_float(payload.get("contract_mismatch"), default=0.0),
        level=OperatorBrainCapabilityMismatchLevel(
            _optional_string(payload.get("level")) or "none"
        ),
        contract_binding_profile=OperatorContractBindingProfile(
            _optional_string(payload.get("contract_binding_profile")) or "standard"
        ),
        fallback_family=_optional_string(payload.get("fallback_family")),
        reason_tags=frozenset(_string_tuple(payload.get("reason_tags"))),
    )


def _fail_open(reason: str, details: Mapping[str, object]) -> HookClientRunResult:
    diagnostics_row = {
        "event": "codex_app_cli_product_hook_client",
        "fail_open": True,
        "fail_open_reason": reason,
        "details": dict(details),
        "stdout_payload": None,
    }
    return HookClientRunResult(
        exit_code=0,
        stdout_payload=None,
        stderr_diagnostic=f"cortex codex app cli product hook fail-open: {reason}",
        diagnostics_row=diagnostics_row,
    )


def _append_diagnostics_from_argv(
    argv: list[str] | None,
    diagnostics_row: Mapping[str, object],
) -> None:
    diagnostics_path = _diagnostics_path_from_argv(argv)
    if diagnostics_path is None:
        return
    path = Path(diagnostics_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(diagnostics_row, sort_keys=True) + "\n")


def _diagnostics_path_from_argv(argv: list[str] | None) -> str | None:
    values = list(argv or ())
    for index, value in enumerate(values):
        if value == "--diagnostics-path" and index + 1 < len(values):
            return values[index + 1]
        if value.startswith("--diagnostics-path="):
            return value.split("=", 1)[1]
    return None


def _stable_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _hash_text(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _non_negative_int(value: Any, *, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        actual_type = type(value).__name__
        raise TypeError(f"expected non-negative int, got {actual_type}.")
    return value


def _non_negative_float(value: Any, *, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0.0:
        actual_type = type(value).__name__
        raise TypeError(f"expected non-negative float, got {actual_type}.")
    return float(value)


def _unit_float(value: Any, *, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        actual_type = type(value).__name__
        raise TypeError(f"expected unit float, got {actual_type}.")
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise ValueError("expected unit float in [0.0, 1.0].")
    return number


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        actual_type = type(value).__name__
        raise TypeError(f"expected sequence of strings, got {actual_type}.")
    return tuple(str(item).strip() for item in value if str(item).strip())


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"expected str | None, got {actual_type}.")
    text = value.strip()
    return text or None


__all__ = [
    "HookClientRunResult",
    "load_runtime_snapshot_payload",
    "main",
    "run_hook_client",
    "runtime_snapshot_from_payload",
]


if __name__ == "__main__":
    raise SystemExit(main())
