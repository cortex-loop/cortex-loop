"""Provider-neutral runtime-context text for model-visible host-control calls."""

from __future__ import annotations

from cortex.sre.brake import BrakeState
from cortex.sre.feedback import (
    MEANINGFUL_EVIDENCE_PROGRESS_CLASSES,
    STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES,
    ReferenceRealizationFeedback,
)
from cortex.sre.opportunities import PROBE_FAILURE_CLASSES


_LOW_EVIDENCE_CLASSES = frozenset({"none"}) | STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES


def runtime_context_from_last_feedback(
    feedback: ReferenceRealizationFeedback | None,
) -> str | None:
    """Translate newest realization feedback into one model-visible constraint.

    The function deliberately accepts one feedback object, not a feedback window
    or host session, so callers cannot accidentally accumulate context across
    turns. Returned text is an attached-context executive constraint in the
    model's task frame, not a schema block, outside-person warning, or raw
    Cortex diagnostic.
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

    return _next_call_constraint(feedback)


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


def _next_call_constraint(feedback: ReferenceRealizationFeedback) -> str | None:
    if _has_continuity_or_session_warning(feedback):
        return (
            "Continuity is not anchored enough for closure. Prior context needs "
            "to be recovered, or the missing context needs to be asked for, "
            "before closure holds."
        )
    elif feedback.probe_result_class in PROBE_FAILURE_CLASSES:
        return (
            "The usual check did not come through. Alternate evidence from the "
            "current task is needed, or the work should close as blocked for "
            "missing information."
        )
    elif _has_low_evidence_without_continuity(feedback):
        return (
            "Completion is not supported by the evidence yet. An artifact, a "
            "check, or a narrower claim is still needed before closure holds."
        )
    elif (
        feedback.selected_family is not feedback.realized_family
        or feedback.brake_state is not BrakeState.QUIESCENT
        or feedback.warning_codes
    ):
        return (
            "Something in the prior step is unresolved. A check is needed before "
            "the next action is treated as safe to continue."
        )
    return None


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


__all__ = [
    "runtime_context_from_last_feedback",
]
