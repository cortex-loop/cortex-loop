"""Provider-neutral runtime-context text for model-visible host-control calls."""

from __future__ import annotations

from cortex.sre.brake import BrakeState
from cortex.sre.feedback import (
    MEANINGFUL_EVIDENCE_PROGRESS_CLASSES,
    STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES,
    ReferenceRealizationFeedback,
)
from cortex.sre.opportunities import PROBE_FAILURE_CLASSES


RUNTIME_CONTEXT_HEADER = "CORTEX_RUNTIME_CONTEXT_V1"
_SOURCE_LINE = "source: last_feedback_only; no_accumulation=true"
_MAX_BLOCK_CHARS = 720
_MAX_TOKEN_CHARS = 48
_LOW_EVIDENCE_CLASSES = frozenset({"none"}) | STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES


def runtime_context_from_last_feedback(
    feedback: ReferenceRealizationFeedback | None,
) -> str | None:
    """Translate the newest realization feedback into bounded model-visible text.

    The function deliberately accepts one feedback object, not a feedback window
    or host session, so callers cannot accidentally accumulate context across
    turns.
    """
    if feedback is None:
        return None
    if not isinstance(feedback, ReferenceRealizationFeedback):
        actual_type = type(feedback).__name__
        raise TypeError(
            "runtime_context_from_last_feedback.feedback must be "
            f"ReferenceRealizationFeedback | None, got {actual_type}."
        )
    if _is_clean_feedback(feedback):
        return None

    lines = (
        RUNTIME_CONTEXT_HEADER,
        _SOURCE_LINE,
        _prior_result_line(feedback),
        _progress_signal_line(feedback),
        _disruption_signal_line(feedback),
        _next_call_constraint_line(feedback),
    )
    block = "\n".join(lines)
    if len(block) > _MAX_BLOCK_CHARS:
        raise RuntimeError(
            "Cortex runtime context exceeded its fixed maximum length; "
            f"got {len(block)} chars."
        )
    return block


def _is_clean_feedback(feedback: ReferenceRealizationFeedback) -> bool:
    if feedback.warning_codes or feedback.host_friction_tags:
        return False
    if feedback.selected_family is not feedback.realized_family:
        return False
    if feedback.brake_state is not BrakeState.QUIESCENT:
        return False
    if feedback.probe_result_class not in (None, "succeeded"):
        return False
    progress_unspecified = (
        feedback.evidence_progress_class is None
        and feedback.evidence_state_moved is None
        and feedback.continuity_progress_class is None
        and feedback.continuity_improved is None
    )
    if progress_unspecified:
        return True
    return _has_meaningful_progress(feedback)


def _has_meaningful_progress(feedback: ReferenceRealizationFeedback) -> bool:
    return bool(
        feedback.evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
        or feedback.evidence_state_moved is True
        or (
            feedback.continuity_progress_class is not None
            and feedback.continuity_progress_class != "none"
        )
        or feedback.continuity_improved is True
        or feedback.probe_result_class == "succeeded"
    )


def _prior_result_line(feedback: ReferenceRealizationFeedback) -> str:
    line = (
        "prior_result: "
        f"selected={feedback.selected_family.value}; "
        f"realized={feedback.realized_family.value}; "
        f"brake={feedback.brake_state.value}"
    )
    return _bounded_line(line, min_chars=40, max_chars=96)


def _progress_signal_line(feedback: ReferenceRealizationFeedback) -> str:
    line = (
        "progress_signal: "
        f"evidence={feedback.evidence_progress_class or 'unknown'}; "
        f"continuity={feedback.continuity_progress_class or 'unknown'}; "
        f"probe={feedback.probe_result_class or 'none'}"
    )
    return _bounded_line(line, min_chars=45, max_chars=120)


def _disruption_signal_line(feedback: ReferenceRealizationFeedback) -> str:
    line = (
        "disruption_signal: "
        f"warnings={_limited_tokens(feedback.warning_codes)}; "
        f"friction={_limited_tokens(feedback.host_friction_tags)}; "
        f"override={_yes_no(feedback.selected_family is not feedback.realized_family)}"
    )
    return _bounded_line(line, min_chars=30, max_chars=160)


def _next_call_constraint_line(feedback: ReferenceRealizationFeedback) -> str:
    if _has_continuity_or_session_warning(feedback):
        constraint = (
            "Do not close this call; recover the missing continuity/session "
            "anchor or ask for exact context before presenting completion."
        )
    elif feedback.probe_result_class in PROBE_FAILURE_CLASSES:
        constraint = (
            "Do not rely on the unavailable probe; use alternate evidence from "
            "the current request or return blocked_missing_info."
        )
    elif _has_low_evidence_without_continuity(feedback):
        constraint = (
            "Do not treat generated text as evidence; produce or check a "
            "concrete artifact, or ask for exact evidence before closure."
        )
    elif (
        feedback.selected_family is not feedback.realized_family
        or feedback.brake_state is not BrakeState.QUIESCENT
        or feedback.warning_codes
    ):
        constraint = (
            "Use a guarded check before acting or closing; verify the next step "
            "because prior control was overridden, warned, or braked."
        )
    else:
        constraint = (
            "Account for prior host friction and choose a lower-risk "
            "inspect/check response; avoid irreversible action until resolved."
        )
    return _bounded_line(
        f"next_call_constraint: {constraint}",
        min_chars=80,
        max_chars=180,
    )


def _has_continuity_or_session_warning(feedback: ReferenceRealizationFeedback) -> bool:
    return any(
        code.startswith(("continuity-rejected:", "session-rejected:"))
        for code in feedback.warning_codes
    )


def _has_low_evidence_without_continuity(
    feedback: ReferenceRealizationFeedback,
) -> bool:
    if feedback.evidence_progress_class not in _LOW_EVIDENCE_CLASSES:
        return feedback.evidence_state_moved is False and not _has_continuity_progress(
            feedback
        )
    return not _has_continuity_progress(feedback)


def _has_continuity_progress(feedback: ReferenceRealizationFeedback) -> bool:
    return bool(
        (
            feedback.continuity_progress_class is not None
            and feedback.continuity_progress_class != "none"
        )
        or feedback.continuity_improved is True
    )


def _limited_tokens(values: tuple[str, ...]) -> str:
    if not values:
        return "none"
    return ",".join(_truncate_token(value) for value in values[:2])


def _truncate_token(value: str) -> str:
    stripped = value.strip()
    if len(stripped) <= _MAX_TOKEN_CHARS:
        return stripped
    return stripped[: _MAX_TOKEN_CHARS - 3] + "..."


def _bounded_line(line: str, *, min_chars: int, max_chars: int) -> str:
    if len(line) > max_chars:
        line = line[: max_chars - 3] + "..."
    if len(line) < min_chars:
        raise RuntimeError(
            "Cortex runtime context field underflow: "
            f"{line!r} has {len(line)} chars, expected at least {min_chars}."
        )
    return line


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


__all__ = [
    "RUNTIME_CONTEXT_HEADER",
    "runtime_context_from_last_feedback",
]
