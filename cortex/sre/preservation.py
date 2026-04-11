"""Minimal preservation-state machine for shipped Cortex executive control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterable, Mapping

if TYPE_CHECKING:
    from .verified_work import VerificationOutcome, WorkContract

_ALLOWED_STRUCTURE_CHECKS = frozenset({"parse", "import_smoke", "pytest", "blocked"})
_ALLOWED_MOVES = frozenset({"continue", "check", "repair", "stop"})
_REPAIRABLE_FAILURE_CLASSES = frozenset(
    {
        "output_invalid",
        "import_smoke_failed",
        "test_failed",
    }
)
_CHECK_FAILURE_CLASSES = frozenset({"blocked_missing_info"})
_STOP_FAILURE_CLASSES = frozenset({"blocked_unsafe"})


@dataclass(frozen=True, slots=True)
class TrustedStructure:
    checks: frozenset[str] = frozenset()
    paths: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "checks",
            _normalized_membership_set(
                self.checks,
                "TrustedStructure.checks",
                allowed_values=_ALLOWED_STRUCTURE_CHECKS,
            ),
        )
        object.__setattr__(
            self,
            "paths",
            _normalized_membership_set(
                self.paths,
                "TrustedStructure.paths",
                path_like=True,
            ),
        )

    def as_payload(self) -> dict[str, Any]:
        return {
            "checks": sorted(self.checks),
            "paths": sorted(self.paths),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> TrustedStructure:
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "TrustedStructure payload must be a mapping, "
                f"got {actual_type}."
            )
        _require_exact_keys(payload, ("checks", "paths"), "TrustedStructure")
        return cls(
            checks=_payload_membership_set(
                payload["checks"],
                "TrustedStructure.checks",
                allowed_values=_ALLOWED_STRUCTURE_CHECKS,
            ),
            paths=_payload_membership_set(
                payload["paths"],
                "TrustedStructure.paths",
                path_like=True,
            ),
        )


@dataclass(frozen=True, slots=True)
class FalsifiedStructure:
    failure_class: str | None = None
    checks: frozenset[str] = frozenset()
    failing_tests: frozenset[str] = frozenset()
    blocked_message: str | None = None

    def __post_init__(self) -> None:
        if self.failure_class is not None and not (
            isinstance(self.failure_class, str) and self.failure_class.strip()
        ):
            raise ValueError(
                "FalsifiedStructure.failure_class must be non-empty after trimming when provided."
            )
        object.__setattr__(
            self,
            "checks",
            _normalized_membership_set(
                self.checks,
                "FalsifiedStructure.checks",
                allowed_values=_ALLOWED_STRUCTURE_CHECKS,
            ),
        )
        object.__setattr__(
            self,
            "failing_tests",
            _normalized_membership_set(
                self.failing_tests,
                "FalsifiedStructure.failing_tests",
            ),
        )
        if self.blocked_message is not None and not (
            isinstance(self.blocked_message, str) and self.blocked_message.strip()
        ):
            raise ValueError(
                "FalsifiedStructure.blocked_message must be non-empty after trimming when provided."
            )
        if self.failure_class is None:
            if self.checks:
                raise ValueError(
                    "FalsifiedStructure.checks must be empty when failure_class is None."
                )
            if self.failing_tests:
                raise ValueError(
                    "FalsifiedStructure.failing_tests must be empty when failure_class is None."
                )
            if self.blocked_message is not None:
                raise ValueError(
                    "FalsifiedStructure.blocked_message must be None when failure_class is None."
                )

    def as_payload(self) -> dict[str, Any]:
        return {
            "failure_class": self.failure_class,
            "checks": sorted(self.checks),
            "failing_tests": sorted(self.failing_tests),
            "blocked_message": self.blocked_message,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> FalsifiedStructure:
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "FalsifiedStructure payload must be a mapping, "
                f"got {actual_type}."
            )
        _require_exact_keys(
            payload,
            ("failure_class", "checks", "failing_tests", "blocked_message"),
            "FalsifiedStructure",
        )
        failure_class = payload["failure_class"]
        if failure_class is not None and not isinstance(failure_class, str):
            actual_type = type(failure_class).__name__
            raise TypeError(
                "FalsifiedStructure.failure_class must be a string or null, "
                f"got {actual_type}."
            )
        blocked_message = payload["blocked_message"]
        if blocked_message is not None and not isinstance(blocked_message, str):
            actual_type = type(blocked_message).__name__
            raise TypeError(
                "FalsifiedStructure.blocked_message must be a string or null, "
                f"got {actual_type}."
            )
        return cls(
            failure_class=failure_class,
            checks=_payload_membership_set(
                payload["checks"],
                "FalsifiedStructure.checks",
                allowed_values=_ALLOWED_STRUCTURE_CHECKS,
            ),
            failing_tests=_payload_membership_set(
                payload["failing_tests"],
                "FalsifiedStructure.failing_tests",
            ),
            blocked_message=blocked_message,
        )


@dataclass(frozen=True, slots=True)
class InterventionBudget:
    allowed_moves: frozenset[str]
    remaining_repairs: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "allowed_moves",
            _normalized_membership_set(
                self.allowed_moves,
                "InterventionBudget.allowed_moves",
                allowed_values=_ALLOWED_MOVES,
            ),
        )
        if not self.allowed_moves:
            raise ValueError("InterventionBudget.allowed_moves must be non-empty.")
        if isinstance(self.remaining_repairs, bool) or not isinstance(
            self.remaining_repairs,
            int,
        ):
            actual_type = type(self.remaining_repairs).__name__
            raise TypeError(
                "InterventionBudget.remaining_repairs must be an integer, "
                f"got {actual_type}."
            )
        if self.remaining_repairs < 0:
            raise ValueError("InterventionBudget.remaining_repairs must be non-negative.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "allowed_moves": sorted(self.allowed_moves),
            "remaining_repairs": self.remaining_repairs,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> InterventionBudget:
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "InterventionBudget payload must be a mapping, "
                f"got {actual_type}."
            )
        _require_exact_keys(
            payload,
            ("allowed_moves", "remaining_repairs"),
            "InterventionBudget",
        )
        remaining_repairs = payload["remaining_repairs"]
        if isinstance(remaining_repairs, bool) or not isinstance(remaining_repairs, int):
            actual_type = type(remaining_repairs).__name__
            raise TypeError(
                "InterventionBudget.remaining_repairs must be an integer, "
                f"got {actual_type}."
            )
        return cls(
            allowed_moves=_payload_membership_set(
                payload["allowed_moves"],
                "InterventionBudget.allowed_moves",
                allowed_values=_ALLOWED_MOVES,
            ),
            remaining_repairs=remaining_repairs,
        )


@dataclass(frozen=True, slots=True)
class PreservationState:
    task_anchor: str
    trusted_structure: TrustedStructure
    falsified_structure: FalsifiedStructure
    lawful_repair_surface: frozenset[str]
    intervention_budget: InterventionBudget

    def __post_init__(self) -> None:
        if not (isinstance(self.task_anchor, str) and self.task_anchor.strip()):
            raise ValueError(
                "PreservationState.task_anchor must be non-empty after trimming."
            )
        if not isinstance(self.trusted_structure, TrustedStructure):
            actual_type = type(self.trusted_structure).__name__
            raise TypeError(
                "PreservationState.trusted_structure must be TrustedStructure, "
                f"got {actual_type}."
            )
        if not isinstance(self.falsified_structure, FalsifiedStructure):
            actual_type = type(self.falsified_structure).__name__
            raise TypeError(
                "PreservationState.falsified_structure must be FalsifiedStructure, "
                f"got {actual_type}."
            )
        object.__setattr__(
            self,
            "lawful_repair_surface",
            _normalized_membership_set(
                self.lawful_repair_surface,
                "PreservationState.lawful_repair_surface",
                path_like=True,
            ),
        )
        if not isinstance(self.intervention_budget, InterventionBudget):
            actual_type = type(self.intervention_budget).__name__
            raise TypeError(
                "PreservationState.intervention_budget must be InterventionBudget, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "task_anchor": self.task_anchor,
            "trusted_structure": self.trusted_structure.as_payload(),
            "falsified_structure": self.falsified_structure.as_payload(),
            "lawful_repair_surface": sorted(self.lawful_repair_surface),
            "intervention_budget": self.intervention_budget.as_payload(),
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> PreservationState:
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "PreservationState payload must be a mapping, "
                f"got {actual_type}."
            )
        _require_exact_keys(
            payload,
            (
                "task_anchor",
                "trusted_structure",
                "falsified_structure",
                "lawful_repair_surface",
                "intervention_budget",
            ),
            "PreservationState",
        )
        task_anchor = payload["task_anchor"]
        if not isinstance(task_anchor, str):
            actual_type = type(task_anchor).__name__
            raise TypeError(
                "PreservationState.task_anchor must be a string, "
                f"got {actual_type}."
            )
        return cls(
            task_anchor=task_anchor,
            trusted_structure=TrustedStructure.from_payload(payload["trusted_structure"]),
            falsified_structure=FalsifiedStructure.from_payload(payload["falsified_structure"]),
            lawful_repair_surface=_payload_membership_set(
                payload["lawful_repair_surface"],
                "PreservationState.lawful_repair_surface",
                path_like=True,
            ),
            intervention_budget=InterventionBudget.from_payload(
                payload["intervention_budget"]
            ),
        )


def derive_preservation_state(
    current_task_anchor: str | None,
    work_contract: WorkContract,
    parsed_output_paths: Iterable[str],
    outcome: VerificationOutcome,
    *,
    remaining_repairs: int,
) -> PreservationState:
    from .verified_work import VerificationOutcome as _VerificationOutcome
    from .verified_work import WorkContract as _WorkContract

    if current_task_anchor is not None and not (
        isinstance(current_task_anchor, str) and current_task_anchor.strip()
    ):
        raise ValueError(
            "derive_preservation_state.current_task_anchor must be non-empty after trimming when provided."
        )
    if not isinstance(work_contract, _WorkContract):
        actual_type = type(work_contract).__name__
        raise TypeError(
            "derive_preservation_state.work_contract must be WorkContract, "
            f"got {actual_type}."
        )
    if not isinstance(outcome, _VerificationOutcome):
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

    allowed_paths = frozenset(work_contract.allowed_write_paths)
    normalized_parsed_paths = _normalized_membership_set(
        parsed_output_paths,
        "derive_preservation_state.parsed_output_paths",
        path_like=True,
    )
    parsed_paths = frozenset(path for path in normalized_parsed_paths if path in allowed_paths)

    trusted_checks = set[str]()
    if parsed_paths:
        trusted_checks.add("parse")
    if outcome.import_smoke_ok is True:
        trusted_checks.add("import_smoke")
    if outcome.pytest_ok is True:
        trusted_checks.add("pytest")

    falsified_checks = _falsified_checks(outcome.failure_class)
    if (
        outcome.status == "passed"
        or outcome.failure_class in _STOP_FAILURE_CLASSES | _CHECK_FAILURE_CLASSES
    ):
        lawful_repair_surface = frozenset()
    elif parsed_paths:
        lawful_repair_surface = parsed_paths
    else:
        lawful_repair_surface = allowed_paths

    if outcome.status == "passed":
        allowed_moves = frozenset({"continue"})
    elif outcome.failure_class in _CHECK_FAILURE_CLASSES:
        allowed_moves = frozenset({"check"})
    elif outcome.failure_class in _STOP_FAILURE_CLASSES:
        allowed_moves = frozenset({"stop"})
    elif (
        outcome.failure_class in _REPAIRABLE_FAILURE_CLASSES
        and remaining_repairs > 0
        and lawful_repair_surface
    ):
        allowed_moves = frozenset({"repair"})
    else:
        allowed_moves = frozenset({"stop"})

    return PreservationState(
        task_anchor=_resolved_task_anchor(current_task_anchor, work_contract),
        trusted_structure=TrustedStructure(
            checks=frozenset(trusted_checks),
            paths=parsed_paths,
        ),
        falsified_structure=FalsifiedStructure(
            failure_class=outcome.failure_class,
            checks=frozenset(falsified_checks),
            failing_tests=frozenset(outcome.failing_tests),
            blocked_message=outcome.blocked_message,
        ),
        lawful_repair_surface=lawful_repair_surface,
        intervention_budget=InterventionBudget(
            allowed_moves=allowed_moves,
            remaining_repairs=remaining_repairs,
        ),
    )


def choose_preservation_move(state: PreservationState) -> str:
    if not isinstance(state, PreservationState):
        actual_type = type(state).__name__
        raise TypeError(
            "choose_preservation_move.state must be PreservationState, "
            f"got {actual_type}."
        )
    for move in ("continue", "check", "repair", "stop"):
        if move in state.intervention_budget.allowed_moves:
            return move
    raise ValueError(
        "PreservationState.intervention_budget.allowed_moves must contain a legal move."
    )


def _resolved_task_anchor(
    current_task_anchor: str | None,
    work_contract: WorkContract,
) -> str:
    if current_task_anchor is not None and current_task_anchor.strip():
        return current_task_anchor.strip()
    joined_paths = "|".join(work_contract.allowed_write_paths)
    return f"verified-work:{work_contract.verification_profile}:{joined_paths}"


def _falsified_checks(failure_class: str | None) -> frozenset[str]:
    if failure_class == "output_invalid":
        return frozenset({"parse"})
    if failure_class == "import_smoke_failed":
        return frozenset({"import_smoke"})
    if failure_class == "test_failed":
        return frozenset({"pytest"})
    if failure_class in _CHECK_FAILURE_CLASSES | _STOP_FAILURE_CLASSES:
        return frozenset({"blocked"})
    return frozenset()


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected_keys: tuple[str, ...],
    label: str,
) -> None:
    actual_keys = tuple(payload)
    if actual_keys != expected_keys:
        raise ValueError(
            f"{label} must preserve the exact key order {expected_keys!r}, got {actual_keys!r}."
        )


def _payload_membership_set(
    value: Any,
    label: str,
    *,
    allowed_values: frozenset[str] | None = None,
    path_like: bool = False,
) -> frozenset[str]:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    return _normalized_membership_set(
        value,
        label,
        allowed_values=allowed_values,
        path_like=path_like,
    )


def _normalized_membership_set(
    values: Iterable[str],
    label: str,
    *,
    allowed_values: frozenset[str] | None = None,
    path_like: bool = False,
) -> frozenset[str]:
    normalized: set[str] = set()
    for item in values:
        if not isinstance(item, str):
            actual_type = type(item).__name__
            raise TypeError(f"{label} must contain only strings, got {actual_type}.")
        stripped = item.strip()
        if not stripped:
            raise ValueError(f"{label} must contain only non-empty strings after trimming.")
        if path_like and (
            stripped.startswith("/") or stripped.startswith("../") or "/../" in stripped
        ):
            raise ValueError(f"{label} must contain only bounded relative paths.")
        if allowed_values is not None and stripped not in allowed_values:
            raise ValueError(
                f"{label} must contain only accepted values {sorted(allowed_values)!r}."
            )
        normalized.add(stripped)
    return frozenset(normalized)


__all__ = [
    "FalsifiedStructure",
    "InterventionBudget",
    "PreservationState",
    "TrustedStructure",
    "choose_preservation_move",
    "derive_preservation_state",
]
