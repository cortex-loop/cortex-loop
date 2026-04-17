"""Host-neutral preservation law for the Cortex v3 verified-work engine."""

from __future__ import annotations

from .contracts import PreservationState, VerificationOutcome, WorkContract


_REPAIRABLE_FAILURE_CLASSES = frozenset(
    {
        "output_invalid",
        "import_smoke_failed",
        "test_failed",
    }
)
_CHECK_FAILURE_CLASSES = frozenset({"blocked_missing_info"})
_STOP_FAILURE_CLASSES = frozenset({"blocked_unsafe"})


def derive_preservation_state(
    current_task_anchor: str | None,
    work_contract: WorkContract,
    outcome: VerificationOutcome,
    *,
    remaining_repairs: int,
) -> PreservationState:
    if current_task_anchor is not None and not (
        isinstance(current_task_anchor, str) and current_task_anchor.strip()
    ):
        raise ValueError(
            "derive_preservation_state.current_task_anchor must be non-empty after trimming when provided."
        )
    if not isinstance(work_contract, WorkContract):
        actual_type = type(work_contract).__name__
        raise TypeError(
            "derive_preservation_state.work_contract must be WorkContract, "
            f"got {actual_type}."
        )
    if not isinstance(outcome, VerificationOutcome):
        actual_type = type(outcome).__name__
        raise TypeError(
            "derive_preservation_state.outcome must be VerificationOutcome, "
            f"got {actual_type}."
        )
    if isinstance(remaining_repairs, bool) or not isinstance(remaining_repairs, int):
        actual_type = type(remaining_repairs).__name__
        raise TypeError(
            "derive_preservation_state.remaining_repairs must be an integer, "
            f"got {actual_type}."
        )
    if remaining_repairs < 0:
        raise ValueError("derive_preservation_state.remaining_repairs must be non-negative.")

    parsed_paths = tuple(
        path for path in outcome.parsed_paths if path in work_contract.allowed_write_paths
    )
    trusted_checks: list[str] = []
    if parsed_paths:
        trusted_checks.append("parse")
    if outcome.import_smoke_ok is True:
        trusted_checks.append("import_smoke")
    if outcome.pytest_ok is True:
        trusted_checks.append("pytest")

    if (
        outcome.status == "passed"
        or outcome.failure_class in _CHECK_FAILURE_CLASSES | _STOP_FAILURE_CLASSES
    ):
        lawful_repair_surface: tuple[str, ...] = ()
    elif parsed_paths:
        lawful_repair_surface = parsed_paths
    else:
        lawful_repair_surface = work_contract.allowed_write_paths

    if outcome.status == "passed":
        allowed_moves = ("continue",)
    elif outcome.failure_class in _CHECK_FAILURE_CLASSES:
        allowed_moves = ("check",)
    elif outcome.failure_class in _STOP_FAILURE_CLASSES:
        allowed_moves = ("stop",)
    elif (
        outcome.failure_class in _REPAIRABLE_FAILURE_CLASSES
        and remaining_repairs > 0
        and lawful_repair_surface
    ):
        allowed_moves = ("repair",)
    else:
        allowed_moves = ("stop",)

    return PreservationState(
        task_anchor=_resolved_task_anchor(current_task_anchor, work_contract),
        trusted_checks=tuple(trusted_checks),
        trusted_paths=parsed_paths,
        failure_class=outcome.failure_class,
        failing_tests=outcome.failing_tests,
        blocked_message=outcome.blocked_message,
        lawful_repair_surface=lawful_repair_surface,
        allowed_moves=allowed_moves,
        remaining_repairs=remaining_repairs,
    )


def choose_preservation_move(state: PreservationState) -> str:
    if not isinstance(state, PreservationState):
        actual_type = type(state).__name__
        raise TypeError(
            "choose_preservation_move.state must be PreservationState, "
            f"got {actual_type}."
        )
    for move in ("continue", "check", "repair", "stop"):
        if move in state.allowed_moves:
            return move
    raise ValueError("PreservationState.allowed_moves must contain a legal move.")


def narrow_repair_contract(
    work_contract: WorkContract,
    lawful_repair_surface: tuple[str, ...],
) -> WorkContract:
    narrowed_paths = tuple(
        path for path in work_contract.allowed_write_paths if path in lawful_repair_surface
    )
    if not narrowed_paths:
        raise ValueError("narrow_repair_contract requires a non-empty repair surface.")
    return WorkContract(
        allowed_write_paths=narrowed_paths,
        verification_profile=work_contract.verification_profile,
        output_carrier=work_contract.output_carrier,
        max_repair_turns=0,
    )


def _resolved_task_anchor(
    current_task_anchor: str | None,
    work_contract: WorkContract,
) -> str:
    if current_task_anchor is not None and current_task_anchor.strip():
        return current_task_anchor.strip()
    joined_paths = "|".join(work_contract.allowed_write_paths)
    return f"verified-work:{work_contract.verification_profile}:{joined_paths}"


__all__ = [
    "choose_preservation_move",
    "derive_preservation_state",
    "narrow_repair_contract",
]
