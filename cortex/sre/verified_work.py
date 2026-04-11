"""Shared verified-work carriers and follow-up law."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .preservation import choose_preservation_move, derive_preservation_state

_ALLOWED_OUTPUT_CARRIERS = frozenset({"full_files"})
_ALLOWED_VERIFICATION_PROFILES = frozenset(
    {
        "python_workspace_pytest_v1",
        "python_workspace_pytest_port_fix_v1",
        "python_workspace_pytest_feature_flags_v1",
    }
)
_ALLOWED_VERIFICATION_STATUS = frozenset({"passed", "failed", "blocked"})
_ALLOWED_VERIFICATION_FAILURE_CLASSES = frozenset(
    {
        "output_invalid",
        "import_smoke_failed",
        "test_failed",
        "blocked_missing_info",
        "blocked_unsafe",
    }
)
_REPAIRABLE_FAILURE_CLASSES = frozenset(
    {
        "output_invalid",
        "import_smoke_failed",
        "test_failed",
    }
)
_CHECK_FAILURE_CLASSES = frozenset({"blocked_missing_info"})
_STOP_FAILURE_CLASSES = frozenset({"blocked_unsafe"})
_ALLOWED_FOLLOW_UP_MOVES = frozenset({"continue", "repair", "check", "stop"})


@dataclass(frozen=True, slots=True)
class WorkContract:
    allowed_write_paths: tuple[str, ...]
    verification_profile: str
    output_carrier: str
    max_repair_turns: int

    def __post_init__(self) -> None:
        if not self.allowed_write_paths:
            raise ValueError("WorkContract.allowed_write_paths must be non-empty.")
        normalized_paths: list[str] = []
        for path in self.allowed_write_paths:
            if not (isinstance(path, str) and path.strip()):
                raise ValueError(
                    "WorkContract.allowed_write_paths must contain only non-empty strings."
                )
            stripped = path.strip()
            if stripped.startswith("/") or stripped.startswith("../") or "/../" in stripped:
                raise ValueError(
                    "WorkContract.allowed_write_paths must contain only bounded relative paths."
                )
            if stripped in normalized_paths:
                raise ValueError(
                    "WorkContract.allowed_write_paths may not contain duplicates."
                )
            normalized_paths.append(stripped)
        object.__setattr__(self, "allowed_write_paths", tuple(normalized_paths))
        if self.verification_profile not in _ALLOWED_VERIFICATION_PROFILES:
            raise ValueError(
                "WorkContract.verification_profile must be one of the accepted verified-work profiles."
            )
        if self.output_carrier not in _ALLOWED_OUTPUT_CARRIERS:
            raise ValueError(
                "WorkContract.output_carrier must be one of the accepted verified-work carriers."
            )
        if isinstance(self.max_repair_turns, bool) or not isinstance(self.max_repair_turns, int):
            actual_type = type(self.max_repair_turns).__name__
            raise TypeError(
                "WorkContract.max_repair_turns must be an integer, "
                f"got {actual_type}."
            )
        if self.max_repair_turns not in (0, 1):
            raise ValueError("WorkContract.max_repair_turns must be 0 or 1.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "allowed_write_paths": list(self.allowed_write_paths),
            "verification_profile": self.verification_profile,
            "output_carrier": self.output_carrier,
            "max_repair_turns": self.max_repair_turns,
        }


@dataclass(frozen=True, slots=True)
class VerificationOutcome:
    status: str
    failure_class: str | None
    parsed_paths: tuple[str, ...] = ()
    parse_error: str | None = None
    import_smoke_ok: bool | None = None
    import_smoke_excerpt: str | None = None
    pytest_ok: bool | None = None
    pytest_exit_code: int | None = None
    pytest_passed: int | None = None
    pytest_failed: int | None = None
    failing_tests: tuple[str, ...] = ()
    first_failure_excerpt: str | None = None
    blocked_message: str | None = None

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_VERIFICATION_STATUS:
            raise ValueError(
                "VerificationOutcome.status must be one of `passed`, `failed`, or `blocked`."
            )
        if self.failure_class is not None and self.failure_class not in _ALLOWED_VERIFICATION_FAILURE_CLASSES:
            raise ValueError(
                "VerificationOutcome.failure_class must be one of the accepted verified-work failure classes."
            )
        if self.status == "passed" and self.failure_class is not None:
            raise ValueError(
                "VerificationOutcome.failure_class must be None when status is `passed`."
            )
        if self.status != "passed" and self.failure_class is None:
            raise ValueError(
                "VerificationOutcome.failure_class must be present when status is not `passed`."
            )
        if any(not (isinstance(path, str) and path.strip()) for path in self.parsed_paths):
            raise ValueError(
                "VerificationOutcome.parsed_paths must contain only non-empty strings."
            )
        if any(not (isinstance(name, str) and name.strip()) for name in self.failing_tests):
            raise ValueError(
                "VerificationOutcome.failing_tests must contain only non-empty strings."
            )
        for label in (
            "parse_error",
            "import_smoke_excerpt",
            "first_failure_excerpt",
            "blocked_message",
        ):
            value = getattr(self, label)
            if value is not None and not (isinstance(value, str) and value.strip()):
                raise ValueError(f"VerificationOutcome.{label} must be non-empty when provided.")
        for label in ("pytest_exit_code", "pytest_passed", "pytest_failed"):
            value = getattr(self, label)
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, int):
                    actual_type = type(value).__name__
                    raise TypeError(
                        f"VerificationOutcome.{label} must be an integer when provided, got {actual_type}."
                    )
                if value < 0:
                    raise ValueError(f"VerificationOutcome.{label} must be non-negative.")
        for label in ("import_smoke_ok", "pytest_ok"):
            value = getattr(self, label)
            if value is not None and not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"VerificationOutcome.{label} must be bool | None, got {actual_type}."
                )

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "failure_class": self.failure_class,
            "parsed_paths": list(self.parsed_paths),
            "parse_error": self.parse_error,
            "import_smoke": {
                "ok": self.import_smoke_ok,
                "excerpt": self.import_smoke_excerpt,
            },
            "pytest": {
                "ok": self.pytest_ok,
                "exit_code": self.pytest_exit_code,
                "passed": self.pytest_passed,
                "failed": self.pytest_failed,
                "failing_tests": list(self.failing_tests),
            },
            "first_failure_excerpt": self.first_failure_excerpt,
            "blocked_message": self.blocked_message,
        }


def choose_verified_work_followup(
    work_contract: WorkContract | None,
    outcome: VerificationOutcome | None,
    *,
    remaining_repairs: int,
) -> str:
    if work_contract is None or outcome is None:
        return "continue"
    if isinstance(remaining_repairs, bool) or not isinstance(remaining_repairs, int):
        actual_type = type(remaining_repairs).__name__
        raise TypeError(
            "choose_verified_work_followup.remaining_repairs must be an integer, "
            f"got {actual_type}."
        )
    if remaining_repairs < 0:
        raise ValueError("choose_verified_work_followup.remaining_repairs must be non-negative.")
    state = derive_preservation_state(
        None,
        work_contract,
        outcome.parsed_paths,
        outcome,
        remaining_repairs=remaining_repairs,
    )
    return choose_preservation_move(state)


__all__ = [
    "VerificationOutcome",
    "WorkContract",
    "choose_verified_work_followup",
]
