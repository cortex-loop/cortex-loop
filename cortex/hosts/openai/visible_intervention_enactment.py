"""OpenAI operator enactment for grounded visible interventions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from cortex.sre.interventions import (
    GroundedInterventionDecision,
    GroundedInterventionMode,
    InterventionRenderSurface,
    find_forbidden_model_visible_terms,
    render_grounded_intervention,
)

from .operator_enactment import find_internal_terms_in_model_visible_values


class OpenAIVisibleInterventionAction(str, Enum):
    STAY_SILENT = "stay_silent"
    RESUME_VISIBLE_INTERVENTION = "resume_visible_intervention"


@dataclass(frozen=True, slots=True)
class OpenAIVisibleInterventionEnactment:
    """Host-native authorization for product-rendered intervention text."""

    action: OpenAIVisibleInterventionAction
    invocation_allowed: bool
    thread_policy: str = "ephemeral_allowed"
    rendered_text: str | None = None
    render_surface: str | None = None
    model_bound_difference_kind: str = "none"
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action, OpenAIVisibleInterventionAction):
            actual_type = type(self.action).__name__
            raise TypeError(
                "OpenAIVisibleInterventionEnactment.action must be "
                f"OpenAIVisibleInterventionAction, got {actual_type}."
            )
        if not isinstance(self.invocation_allowed, bool):
            actual_type = type(self.invocation_allowed).__name__
            raise TypeError(
                "OpenAIVisibleInterventionEnactment.invocation_allowed must be bool, "
                f"got {actual_type}."
            )
        if not isinstance(self.thread_policy, str) or not self.thread_policy.strip():
            raise ValueError(
                "OpenAIVisibleInterventionEnactment.thread_policy must be non-empty."
            )
        if self.rendered_text is not None and not self.rendered_text.strip():
            raise ValueError(
                "OpenAIVisibleInterventionEnactment.rendered_text must be non-empty "
                "when provided."
            )
        if self.render_surface is not None and not self.render_surface.strip():
            raise ValueError(
                "OpenAIVisibleInterventionEnactment.render_surface must be non-empty "
                "when provided."
            )
        if not self.model_bound_difference_kind.strip():
            raise ValueError(
                "OpenAIVisibleInterventionEnactment.model_bound_difference_kind must "
                "be non-empty."
            )
        if self.blocked_reason is not None and not self.blocked_reason.strip():
            raise ValueError(
                "OpenAIVisibleInterventionEnactment.blocked_reason must be non-empty "
                "when provided."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "invocation_allowed": self.invocation_allowed,
            "thread_policy": self.thread_policy,
            "rendered_text": self.rendered_text,
            "render_surface": self.render_surface,
            "model_bound_difference_kind": self.model_bound_difference_kind,
            "blocked_reason": self.blocked_reason,
        }


def build_openai_visible_intervention_enactment(
    *,
    grounded_intervention: GroundedInterventionDecision,
    thread_id: str | None,
    provider_limit_interference: bool = False,
    surface: InterventionRenderSurface = InterventionRenderSurface.SAME_THREAD_RESUME,
    prior_act_anchor: bool = False,
) -> OpenAIVisibleInterventionEnactment:
    """Translate a selected grounded intervention into an OpenAI operator action.

    This adapter does not select or recompute intervention policy. It only
    renders a product-runtime `GroundedInterventionDecision` into the host's
    same-thread continuation surface when the host can lawfully carry it.
    """

    if not isinstance(grounded_intervention, GroundedInterventionDecision):
        actual_type = type(grounded_intervention).__name__
        raise TypeError(
            "grounded_intervention must be GroundedInterventionDecision, "
            f"got {actual_type}."
        )
    if not isinstance(provider_limit_interference, bool):
        actual_type = type(provider_limit_interference).__name__
        raise TypeError(
            "provider_limit_interference must be bool, " f"got {actual_type}."
        )
    if not isinstance(surface, InterventionRenderSurface):
        actual_type = type(surface).__name__
        raise TypeError(
            "surface must be InterventionRenderSurface, " f"got {actual_type}."
        )
    if not isinstance(prior_act_anchor, bool):
        actual_type = type(prior_act_anchor).__name__
        raise TypeError(f"prior_act_anchor must be bool, got {actual_type}.")

    if grounded_intervention.mode is GroundedInterventionMode.STAY_SILENT:
        return _silent(grounded_intervention.silence_reason or "stay_silent")
    if grounded_intervention.record is None:
        return _silent("missing_intervention_record")
    if provider_limit_interference:
        return _silent("provider_limit_interference")
    identity_continuous_surface = surface in {
        InterventionRenderSurface.SAME_THREAD_RESUME,
        InterventionRenderSurface.IDENTITY_CONTINUOUS,
    }
    if identity_continuous_surface:
        if not (isinstance(thread_id, str) and thread_id.strip()):
            return _silent("missing_thread_id")
        if not prior_act_anchor:
            return _silent("missing_prior_act_anchor")

    rendered = render_grounded_intervention(
        grounded_intervention.record,
        surface=surface,
        prior_act_anchor=prior_act_anchor,
    )
    leaks = find_model_visible_leaks(
        {
            "rendered_text": rendered,
            "thread_id": thread_id,
        }
    )
    if leaks:
        return _silent("model_visible_forbidden_terms")

    return OpenAIVisibleInterventionEnactment(
        action=OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION,
        invocation_allowed=True,
        thread_policy="resume_existing_thread",
        rendered_text=rendered,
        render_surface=surface.value,
        model_bound_difference_kind="grounded_visible_intervention",
        blocked_reason=None,
    )


def find_model_visible_leaks(
    values: Mapping[str, Any] | Sequence[Any] | str,
) -> tuple[str, ...]:
    """Return all forbidden terms across SRE and OpenAI model-visible checks."""

    text = _flatten_to_text(values)
    found = {
        *find_forbidden_model_visible_terms(text),
        *find_internal_terms_in_model_visible_values(values),
    }
    return tuple(sorted(found))


def _silent(reason: str) -> OpenAIVisibleInterventionEnactment:
    return OpenAIVisibleInterventionEnactment(
        action=OpenAIVisibleInterventionAction.STAY_SILENT,
        invocation_allowed=False,
        thread_policy="ephemeral_allowed",
        rendered_text=None,
        render_surface=None,
        model_bound_difference_kind="none",
        blocked_reason=reason,
    )


def _flatten_to_text(values: Mapping[str, Any] | Sequence[Any] | str) -> str:
    if isinstance(values, str):
        return values
    if isinstance(values, Mapping):
        return "\n".join(_flatten_to_text(value) for value in values.values())
    if isinstance(values, Sequence) and not isinstance(values, (bytes, bytearray)):
        return "\n".join(_flatten_to_text(value) for value in values)
    if values is None:
        return ""
    return str(values)


__all__ = [
    "OpenAIVisibleInterventionAction",
    "OpenAIVisibleInterventionEnactment",
    "build_openai_visible_intervention_enactment",
    "find_model_visible_leaks",
]
