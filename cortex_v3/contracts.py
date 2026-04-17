"""Provider-neutral contracts for the Cortex v3 verified-work engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
_ALLOWED_DECISIONS = frozenset({"continue", "repair", "check", "stop"})
_ALLOWED_CONTEXT_MODES = frozenset(
    {
        "default",
        "off",
        "writable_files_only",
        "writable_files_plus_visible_tests",
    }
)


def _normalized_relative_paths(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    if not values:
        raise ValueError(f"{label} must be non-empty.")
    normalized: list[str] = []
    for path in values:
        if not (isinstance(path, str) and path.strip()):
            raise ValueError(f"{label} must contain only non-empty strings.")
        stripped = path.strip()
        if stripped.startswith("/") or stripped.startswith("../") or "/../" in stripped:
            raise ValueError(f"{label} must contain only bounded relative paths.")
        if stripped in normalized:
            raise ValueError(f"{label} may not contain duplicates.")
        normalized.append(stripped)
    return tuple(normalized)


def _normalized_string_tuple(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not (isinstance(value, str) and value.strip()):
            raise ValueError(f"{label} must contain only non-empty strings.")
        stripped = value.strip()
        if stripped not in normalized:
            normalized.append(stripped)
    return tuple(normalized)


@dataclass(frozen=True, slots=True)
class WorkContract:
    allowed_write_paths: tuple[str, ...]
    verification_profile: str
    output_carrier: str = "full_files"
    max_repair_turns: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "allowed_write_paths",
            _normalized_relative_paths(
                self.allowed_write_paths,
                "WorkContract.allowed_write_paths",
            ),
        )
        if self.verification_profile not in _ALLOWED_VERIFICATION_PROFILES:
            raise ValueError(
                "WorkContract.verification_profile must be one of the accepted verified-work profiles."
            )
        if self.output_carrier not in _ALLOWED_OUTPUT_CARRIERS:
            raise ValueError(
                "WorkContract.output_carrier must be one of the accepted verified-work carriers."
            )
        if isinstance(self.max_repair_turns, bool) or not isinstance(
            self.max_repair_turns,
            int,
        ):
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
        if (
            self.failure_class is not None
            and self.failure_class not in _ALLOWED_VERIFICATION_FAILURE_CLASSES
        ):
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
        object.__setattr__(
            self,
            "parsed_paths",
            _normalized_string_tuple(
                self.parsed_paths,
                "VerificationOutcome.parsed_paths",
            ),
        )
        object.__setattr__(
            self,
            "failing_tests",
            _normalized_string_tuple(
                self.failing_tests,
                "VerificationOutcome.failing_tests",
            ),
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


@dataclass(frozen=True, slots=True)
class PreservationState:
    task_anchor: str
    trusted_checks: tuple[str, ...]
    trusted_paths: tuple[str, ...]
    failure_class: str | None
    failing_tests: tuple[str, ...]
    blocked_message: str | None
    lawful_repair_surface: tuple[str, ...]
    allowed_moves: tuple[str, ...]
    remaining_repairs: int

    def __post_init__(self) -> None:
        if not (isinstance(self.task_anchor, str) and self.task_anchor.strip()):
            raise ValueError("PreservationState.task_anchor must be non-empty after trimming.")
        object.__setattr__(
            self,
            "trusted_checks",
            _normalized_string_tuple(
                self.trusted_checks,
                "PreservationState.trusted_checks",
            ),
        )
        object.__setattr__(
            self,
            "trusted_paths",
            _normalized_relative_paths(
                self.trusted_paths,
                "PreservationState.trusted_paths",
            )
            if self.trusted_paths
            else (),
        )
        object.__setattr__(
            self,
            "failing_tests",
            _normalized_string_tuple(
                self.failing_tests,
                "PreservationState.failing_tests",
            ),
        )
        object.__setattr__(
            self,
            "lawful_repair_surface",
            _normalized_relative_paths(
                self.lawful_repair_surface,
                "PreservationState.lawful_repair_surface",
            )
            if self.lawful_repair_surface
            else (),
        )
        object.__setattr__(
            self,
            "allowed_moves",
            _normalized_string_tuple(
                self.allowed_moves,
                "PreservationState.allowed_moves",
            ),
        )
        if not self.allowed_moves:
            raise ValueError("PreservationState.allowed_moves must be non-empty.")
        if any(move not in _ALLOWED_DECISIONS for move in self.allowed_moves):
            raise ValueError(
                "PreservationState.allowed_moves must contain only legal decisions."
            )
        if self.failure_class is not None and not (
            isinstance(self.failure_class, str) and self.failure_class.strip()
        ):
            raise ValueError(
                "PreservationState.failure_class must be non-empty after trimming when provided."
            )
        if self.blocked_message is not None and not (
            isinstance(self.blocked_message, str) and self.blocked_message.strip()
        ):
            raise ValueError(
                "PreservationState.blocked_message must be non-empty after trimming when provided."
            )
        if isinstance(self.remaining_repairs, bool) or not isinstance(
            self.remaining_repairs,
            int,
        ):
            actual_type = type(self.remaining_repairs).__name__
            raise TypeError(
                "PreservationState.remaining_repairs must be an integer, "
                f"got {actual_type}."
            )
        if self.remaining_repairs < 0:
            raise ValueError("PreservationState.remaining_repairs must be non-negative.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "task_anchor": self.task_anchor,
            "trusted_checks": list(self.trusted_checks),
            "trusted_paths": list(self.trusted_paths),
            "failure_class": self.failure_class,
            "failing_tests": list(self.failing_tests),
            "blocked_message": self.blocked_message,
            "lawful_repair_surface": list(self.lawful_repair_surface),
            "allowed_moves": list(self.allowed_moves),
            "remaining_repairs": self.remaining_repairs,
        }


@dataclass(frozen=True, slots=True)
class VerifiedTurnRequest:
    model: str
    task_prompt: str
    work_contract: WorkContract
    instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    max_output_tokens: int | None = None
    context_mode: str = "default"

    def __post_init__(self) -> None:
        if not (isinstance(self.model, str) and self.model.strip()):
            raise ValueError("VerifiedTurnRequest.model must be non-empty after trimming.")
        if not (isinstance(self.task_prompt, str) and self.task_prompt.strip()):
            raise ValueError(
                "VerifiedTurnRequest.task_prompt must be non-empty after trimming."
            )
        if not isinstance(self.work_contract, WorkContract):
            actual_type = type(self.work_contract).__name__
            raise TypeError(
                "VerifiedTurnRequest.work_contract must be WorkContract, "
                f"got {actual_type}."
            )
        if self.instructions is not None and not (
            isinstance(self.instructions, str) and self.instructions.strip()
        ):
            raise ValueError(
                "VerifiedTurnRequest.instructions must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "VerifiedTurnRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if any(not (isinstance(key, str) and key.strip()) for key in self.metadata):
            raise ValueError(
                "VerifiedTurnRequest.metadata keys must be non-empty strings after trimming."
            )
        if self.max_output_tokens is not None:
            if isinstance(self.max_output_tokens, bool) or not isinstance(
                self.max_output_tokens,
                int,
            ):
                actual_type = type(self.max_output_tokens).__name__
                raise TypeError(
                    "VerifiedTurnRequest.max_output_tokens must be int | None, "
                    f"got {actual_type}."
                )
            if self.max_output_tokens <= 0:
                raise ValueError(
                    "VerifiedTurnRequest.max_output_tokens must be positive when provided."
                )
        if self.context_mode not in _ALLOWED_CONTEXT_MODES:
            raise ValueError("VerifiedTurnRequest.context_mode must be accepted.")


@dataclass(frozen=True, slots=True)
class ProviderTurnRequest:
    provider: str
    model: str
    prompt: str
    instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    max_output_tokens: int | None = None

    def __post_init__(self) -> None:
        for label in ("provider", "model", "prompt"):
            value = getattr(self, label)
            if not (isinstance(value, str) and value.strip()):
                raise ValueError(
                    f"ProviderTurnRequest.{label} must be non-empty after trimming."
                )
        if self.instructions is not None and not (
            isinstance(self.instructions, str) and self.instructions.strip()
        ):
            raise ValueError(
                "ProviderTurnRequest.instructions must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "ProviderTurnRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if self.max_output_tokens is not None:
            if isinstance(self.max_output_tokens, bool) or not isinstance(
                self.max_output_tokens,
                int,
            ):
                actual_type = type(self.max_output_tokens).__name__
                raise TypeError(
                    "ProviderTurnRequest.max_output_tokens must be int | None, "
                    f"got {actual_type}."
                )
            if self.max_output_tokens <= 0:
                raise ValueError(
                    "ProviderTurnRequest.max_output_tokens must be positive when provided."
                )

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
        }
        if self.instructions is not None:
            payload["instructions"] = self.instructions
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        if self.max_output_tokens is not None:
            payload["max_output_tokens"] = self.max_output_tokens
        return payload


@dataclass(frozen=True, slots=True)
class ProviderTurnResponse:
    provider: str
    output_text: str | None
    raw_events: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not (isinstance(self.provider, str) and self.provider.strip()):
            raise ValueError("ProviderTurnResponse.provider must be non-empty after trimming.")
        if self.output_text is not None and not isinstance(self.output_text, str):
            actual_type = type(self.output_text).__name__
            raise TypeError(
                "ProviderTurnResponse.output_text must be str | None, "
                f"got {actual_type}."
            )
        if any(not isinstance(event, dict) for event in self.raw_events):
            raise TypeError(
                "ProviderTurnResponse.raw_events must contain only dict[str, Any] events."
            )
        object.__setattr__(
            self,
            "warnings",
            _normalized_string_tuple(
                self.warnings,
                "ProviderTurnResponse.warnings",
            ),
        )


@dataclass(frozen=True, slots=True)
class VerifiedTurnResult:
    provider: str
    attempt_count: int
    decision: str
    result_text: str | None
    verification: VerificationOutcome | None
    parsed_paths: tuple[str, ...]
    raw_trace: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not (isinstance(self.provider, str) and self.provider.strip()):
            raise ValueError("VerifiedTurnResult.provider must be non-empty after trimming.")
        if isinstance(self.attempt_count, bool) or not isinstance(self.attempt_count, int):
            actual_type = type(self.attempt_count).__name__
            raise TypeError(
                "VerifiedTurnResult.attempt_count must be an integer, "
                f"got {actual_type}."
            )
        if self.attempt_count <= 0:
            raise ValueError("VerifiedTurnResult.attempt_count must be positive.")
        if self.decision not in _ALLOWED_DECISIONS:
            raise ValueError("VerifiedTurnResult.decision must be a legal decision.")
        if self.result_text is not None and not isinstance(self.result_text, str):
            actual_type = type(self.result_text).__name__
            raise TypeError(
                "VerifiedTurnResult.result_text must be str | None, "
                f"got {actual_type}."
            )
        if self.verification is not None and not isinstance(
            self.verification,
            VerificationOutcome,
        ):
            actual_type = type(self.verification).__name__
            raise TypeError(
                "VerifiedTurnResult.verification must be VerificationOutcome | None, "
                f"got {actual_type}."
            )
        object.__setattr__(
            self,
            "parsed_paths",
            _normalized_string_tuple(
                self.parsed_paths,
                "VerifiedTurnResult.parsed_paths",
            ),
        )
        if any(not isinstance(event, dict) for event in self.raw_trace):
            raise TypeError(
                "VerifiedTurnResult.raw_trace must contain only dict[str, Any] events."
            )
        object.__setattr__(
            self,
            "warnings",
            _normalized_string_tuple(
                self.warnings,
                "VerifiedTurnResult.warnings",
            ),
        )

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "provider": self.provider,
            "attempt_count": self.attempt_count,
            "decision": self.decision,
            "parsed_paths": list(self.parsed_paths),
            "raw_trace": [dict(event) for event in self.raw_trace],
            "warnings": list(self.warnings),
        }
        if self.result_text is not None:
            payload["result_text"] = self.result_text
        if self.verification is not None:
            payload["verification"] = self.verification.as_payload()
        return payload


__all__ = [
    "PreservationState",
    "ProviderTurnRequest",
    "ProviderTurnResponse",
    "VerificationOutcome",
    "VerifiedTurnRequest",
    "VerifiedTurnResult",
    "WorkContract",
]
