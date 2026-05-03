"""Grounded model-visible intervention records for the executive edge.

This module decides whether Cortex may speak to a model at all. It does not
change route, brake, debt, AUX, hook, or host-adapter policy. The selector is
host-neutral product law: pressure alone is never enough, and task details may
only appear as anchors after product runtime state already established the
executive gap.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from numbers import Real
from typing import Any


VISIBLE_INTERVENTION_PRESSURE_THRESHOLD = 0.55


class GroundedInterventionMode(str, Enum):
    STAY_SILENT = "stay_silent"
    MODEL_VISIBLE_REFLECTION = "model_visible_reflection"


class GroundedInterventionKind(str, Enum):
    UNSUPPORTED_CLAIM = "unsupported_claim"
    OVERDUE_VERIFICATION = "overdue_verification"
    UNRESOLVED_OBLIGATION = "unresolved_obligation"
    CONTINUITY_GAP = "continuity_gap"
    CAPABILITY_GUARD = "capability_guard"
    PRESERVATION_RISK = "preservation_risk"


class GroundedAnchorType(str, Enum):
    CLAIM = "claim"
    EVIDENCE = "evidence"
    OBLIGATION = "obligation"
    CONTINUITY = "continuity"
    CAPABILITY = "capability"
    PRESERVATION = "preservation"


class GroundedAnchorSource(str, Enum):
    PRODUCT_RUNTIME = "product_runtime"
    PRODUCT_RUNTIME_TASK_DETAIL = "product_runtime_task_detail"
    TASK_IDENTITY = "task_identity"
    LAB_ORACLE = "lab_oracle"
    HIDDEN_VERIFIER_FACT = "hidden_verifier_fact"
    HAND_WRITTEN_LAB_PROMPT = "hand_written_lab_prompt"


class InterventionNextMoveClass(str, Enum):
    PRODUCE_EVIDENCE = "produce_evidence"
    RUN_CHECK = "run_check"
    NARROW_CLAIM = "narrow_claim"
    ASK_MISSING_CONTEXT = "ask_missing_context"
    RECOVER_CONTEXT = "recover_context"
    NAME_BLOCKER = "name_blocker"
    PRESERVE_VERIFIED_WORK = "preserve_verified_work"


class AssistantGapResponse(str, Enum):
    UNADDRESSED = "unaddressed"
    NARROWED = "narrowed"
    ASKED = "asked"
    BLOCKED = "blocked"
    RETRACTED = "retracted"
    REPAIRED = "repaired"
    VERIFIED = "verified"


class InterventionReliefState(str, Enum):
    CLEAN = "clean"
    PAID_DOWN = "paid_down"
    WAITING_ON_USER = "waiting_on_user"
    BLOCKER_SURFACED = "blocker_surfaced"
    VERIFIED = "verified"


class InterventionRenderSurface(str, Enum):
    ATTACHED_CONTEXT = "attached_context"
    SAME_THREAD_RESUME = "same_thread_resume"


_PRODUCT_ANCHOR_SOURCES = frozenset(
    {
        GroundedAnchorSource.PRODUCT_RUNTIME,
        GroundedAnchorSource.PRODUCT_RUNTIME_TASK_DETAIL,
    }
)
_SELF_REPAIR_RESPONSES = frozenset(
    {
        AssistantGapResponse.NARROWED,
        AssistantGapResponse.ASKED,
        AssistantGapResponse.BLOCKED,
        AssistantGapResponse.RETRACTED,
        AssistantGapResponse.REPAIRED,
        AssistantGapResponse.VERIFIED,
    }
)
_RELIEF_STATES = frozenset(
    {
        InterventionReliefState.CLEAN,
        InterventionReliefState.PAID_DOWN,
        InterventionReliefState.WAITING_ON_USER,
        InterventionReliefState.BLOCKER_SURFACED,
        InterventionReliefState.VERIFIED,
    }
)
_INTERNAL_MODEL_VISIBLE_FRAGMENTS = (
    "Cortex",
    "cortex",
    "debt",
    "brake",
    "AUX",
    "aux",
    "schema",
    "hook",
    "route",
    "session",
    "fixture",
    "hidden verifier",
    "lab oracle",
    "task identity",
    "external auditor",
    "policy engine",
    "monitor",
    "you should",
    "you must",
    "do not",
    "Do not",
)


@dataclass(frozen=True, slots=True)
class GroundedInterventionPressure:
    """Private pressure summary used to decide if speech is even eligible."""

    control_pressure: float = 0.0
    verification_pressure: float = 0.0
    continuity_pressure: float = 0.0
    capability_pressure: float = 0.0
    preservation_pressure: float = 0.0
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        for field_name in (
            "control_pressure",
            "verification_pressure",
            "continuity_pressure",
            "capability_pressure",
            "preservation_pressure",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"GroundedInterventionPressure.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"GroundedInterventionPressure.{field_name} must be between 0.0 and 1.0."
                )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.reason_tags):
            raise ValueError(
                "GroundedInterventionPressure.reason_tags must contain only non-empty strings."
            )

    @property
    def strongest_pressure(self) -> float:
        return max(
            float(self.control_pressure),
            float(self.verification_pressure),
            float(self.continuity_pressure),
            float(self.capability_pressure),
            float(self.preservation_pressure),
        )

    def as_payload(self) -> dict[str, object]:
        return {
            "control_pressure": round(float(self.control_pressure), 4),
            "verification_pressure": round(float(self.verification_pressure), 4),
            "continuity_pressure": round(float(self.continuity_pressure), 4),
            "capability_pressure": round(float(self.capability_pressure), 4),
            "preservation_pressure": round(float(self.preservation_pressure), 4),
            "reason_tags": sorted(self.reason_tags),
        }


@dataclass(frozen=True, slots=True)
class GroundedInterventionAnchor:
    anchor_type: GroundedAnchorType
    text: str
    source: GroundedAnchorSource = GroundedAnchorSource.PRODUCT_RUNTIME

    def __post_init__(self) -> None:
        if not isinstance(self.anchor_type, GroundedAnchorType):
            actual_type = type(self.anchor_type).__name__
            raise TypeError(
                "GroundedInterventionAnchor.anchor_type must be GroundedAnchorType, "
                f"got {actual_type}."
            )
        if not (isinstance(self.text, str) and self.text.strip()):
            raise ValueError(
                "GroundedInterventionAnchor.text must be non-empty after trimming."
            )
        if not isinstance(self.source, GroundedAnchorSource):
            actual_type = type(self.source).__name__
            raise TypeError(
                "GroundedInterventionAnchor.source must be GroundedAnchorSource, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, str]:
        return {
            "anchor_type": self.anchor_type.value,
            "text": self.text,
            "source": self.source.value,
        }


@dataclass(frozen=True, slots=True)
class GroundedInterventionRecord:
    kind: GroundedInterventionKind
    grounded_anchor_type: GroundedAnchorType
    task_local_anchor_text: str
    next_move_class: InterventionNextMoveClass
    pressure_summary: GroundedInterventionPressure
    silence_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, GroundedInterventionKind):
            actual_type = type(self.kind).__name__
            raise TypeError(
                "GroundedInterventionRecord.kind must be GroundedInterventionKind, "
                f"got {actual_type}."
            )
        if not isinstance(self.grounded_anchor_type, GroundedAnchorType):
            actual_type = type(self.grounded_anchor_type).__name__
            raise TypeError(
                "GroundedInterventionRecord.grounded_anchor_type must be GroundedAnchorType, "
                f"got {actual_type}."
            )
        if not (
            isinstance(self.task_local_anchor_text, str)
            and self.task_local_anchor_text.strip()
        ):
            raise ValueError(
                "GroundedInterventionRecord.task_local_anchor_text must be non-empty after trimming."
            )
        if not isinstance(self.next_move_class, InterventionNextMoveClass):
            actual_type = type(self.next_move_class).__name__
            raise TypeError(
                "GroundedInterventionRecord.next_move_class must be InterventionNextMoveClass, "
                f"got {actual_type}."
            )
        if not isinstance(self.pressure_summary, GroundedInterventionPressure):
            actual_type = type(self.pressure_summary).__name__
            raise TypeError(
                "GroundedInterventionRecord.pressure_summary must be "
                f"GroundedInterventionPressure, got {actual_type}."
            )
        if self.silence_reason is not None and not self.silence_reason.strip():
            raise ValueError(
                "GroundedInterventionRecord.silence_reason must be non-empty when provided."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "grounded_anchor_type": self.grounded_anchor_type.value,
            "task_local_anchor_text": self.task_local_anchor_text,
            "next_move_class": self.next_move_class.value,
            "pressure_summary": self.pressure_summary.as_payload(),
            "silence_reason": self.silence_reason,
        }


@dataclass(frozen=True, slots=True)
class GroundedInterventionSelectionTrace:
    """Private diagnostic trace for why visible intervention did or did not fire."""

    perception_source: str = "none"
    selected_expectation_id: str | None = None
    deficit_kind: str | None = None
    pressure_tags: tuple[str, ...] = field(default_factory=tuple)
    silence_reason: str | None = None
    silent_control_sufficient: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.perception_source, str) or not self.perception_source.strip():
            raise ValueError(
                "GroundedInterventionSelectionTrace.perception_source must be non-empty."
            )
        if self.selected_expectation_id is not None and not self.selected_expectation_id.strip():
            raise ValueError(
                "GroundedInterventionSelectionTrace.selected_expectation_id must be non-empty when provided."
            )
        if self.deficit_kind is not None and not self.deficit_kind.strip():
            raise ValueError(
                "GroundedInterventionSelectionTrace.deficit_kind must be non-empty when provided."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.pressure_tags):
            raise ValueError(
                "GroundedInterventionSelectionTrace.pressure_tags must contain only non-empty strings."
            )
        if self.silence_reason is not None and not self.silence_reason.strip():
            raise ValueError(
                "GroundedInterventionSelectionTrace.silence_reason must be non-empty when provided."
            )
        if not isinstance(self.silent_control_sufficient, bool):
            actual_type = type(self.silent_control_sufficient).__name__
            raise TypeError(
                "GroundedInterventionSelectionTrace.silent_control_sufficient must be "
                f"bool, got {actual_type}."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "perception_source": self.perception_source,
            "selected_expectation_id": self.selected_expectation_id,
            "deficit_kind": self.deficit_kind,
            "pressure_tags": list(self.pressure_tags),
            "silence_reason": self.silence_reason,
            "silent_control_sufficient": self.silent_control_sufficient,
        }


@dataclass(frozen=True, slots=True)
class GroundedInterventionDecision:
    mode: GroundedInterventionMode = GroundedInterventionMode.STAY_SILENT
    record: GroundedInterventionRecord | None = None
    pressure_summary: GroundedInterventionPressure = field(
        default_factory=GroundedInterventionPressure
    )
    silence_reason: str | None = "no_intervention_selected"
    selection_trace: GroundedInterventionSelectionTrace = field(
        default_factory=GroundedInterventionSelectionTrace
    )

    def __post_init__(self) -> None:
        if not isinstance(self.mode, GroundedInterventionMode):
            actual_type = type(self.mode).__name__
            raise TypeError(
                "GroundedInterventionDecision.mode must be GroundedInterventionMode, "
                f"got {actual_type}."
            )
        if self.record is not None and not isinstance(
            self.record,
            GroundedInterventionRecord,
        ):
            actual_type = type(self.record).__name__
            raise TypeError(
                "GroundedInterventionDecision.record must be GroundedInterventionRecord | None, "
                f"got {actual_type}."
            )
        if not isinstance(self.pressure_summary, GroundedInterventionPressure):
            actual_type = type(self.pressure_summary).__name__
            raise TypeError(
                "GroundedInterventionDecision.pressure_summary must be "
                f"GroundedInterventionPressure, got {actual_type}."
            )
        if not isinstance(self.selection_trace, GroundedInterventionSelectionTrace):
            actual_type = type(self.selection_trace).__name__
            raise TypeError(
                "GroundedInterventionDecision.selection_trace must be "
                f"GroundedInterventionSelectionTrace, got {actual_type}."
            )
        if self.mode is GroundedInterventionMode.STAY_SILENT:
            if self.record is not None:
                raise ValueError(
                    "GroundedInterventionDecision.record must be None when mode is stay_silent."
                )
            if not (isinstance(self.silence_reason, str) and self.silence_reason.strip()):
                raise ValueError(
                    "GroundedInterventionDecision.silence_reason is required when mode is stay_silent."
                )
        else:
            if self.record is None:
                raise ValueError(
                    "GroundedInterventionDecision.record is required when mode is model_visible_reflection."
                )
            if self.silence_reason is not None:
                raise ValueError(
                    "GroundedInterventionDecision.silence_reason must be None when a record is selected."
                )

    @classmethod
    def stay_silent(
        cls,
        reason: str = "no_intervention_selected",
        *,
        pressure_summary: GroundedInterventionPressure | None = None,
        selection_trace: GroundedInterventionSelectionTrace | None = None,
    ) -> "GroundedInterventionDecision":
        trace = replace(
            selection_trace or GroundedInterventionSelectionTrace(),
            silence_reason=reason,
        )
        return cls(
            mode=GroundedInterventionMode.STAY_SILENT,
            record=None,
            pressure_summary=pressure_summary or GroundedInterventionPressure(),
            silence_reason=reason,
            selection_trace=trace,
        )

    @classmethod
    def model_visible_reflection(
        cls,
        record: GroundedInterventionRecord,
        *,
        selection_trace: GroundedInterventionSelectionTrace | None = None,
    ) -> "GroundedInterventionDecision":
        trace = replace(
            selection_trace or GroundedInterventionSelectionTrace(),
            silence_reason=None,
        )
        return cls(
            mode=GroundedInterventionMode.MODEL_VISIBLE_REFLECTION,
            record=record,
            pressure_summary=record.pressure_summary,
            silence_reason=None,
            selection_trace=trace,
        )

    def as_payload(self) -> dict[str, object]:
        return {
            "mode": self.mode.value,
            "record": self.record.as_payload() if self.record is not None else None,
            "pressure_summary": self.pressure_summary.as_payload(),
            "silence_reason": self.silence_reason,
            "selection_trace": self.selection_trace.as_payload(),
        }


def select_grounded_intervention(
    *,
    pressure: GroundedInterventionPressure,
    anchors: tuple[GroundedInterventionAnchor, ...] = (),
    preferred_kind: GroundedInterventionKind | None = None,
    next_move_class: InterventionNextMoveClass | None = None,
    last_assistant_response: AssistantGapResponse = AssistantGapResponse.UNADDRESSED,
    relief_states: tuple[InterventionReliefState, ...] = (),
    silent_control_sufficient: bool = False,
    selection_trace: GroundedInterventionSelectionTrace | None = None,
) -> GroundedInterventionDecision:
    """Select at most one grounded visible-intervention record.

    The selector does not parse task identity or assistant prose. Callers must
    provide product-runtime anchors and explicit last-move/relief facts.
    """

    if not isinstance(pressure, GroundedInterventionPressure):
        actual_type = type(pressure).__name__
        raise TypeError(
            f"select_grounded_intervention.pressure must be GroundedInterventionPressure, got {actual_type}."
        )
    if any(not isinstance(anchor, GroundedInterventionAnchor) for anchor in anchors):
        raise TypeError(
            "select_grounded_intervention.anchors must contain only GroundedInterventionAnchor values."
        )
    if preferred_kind is not None and not isinstance(
        preferred_kind,
        GroundedInterventionKind,
    ):
        actual_type = type(preferred_kind).__name__
        raise TypeError(
            "select_grounded_intervention.preferred_kind must be GroundedInterventionKind | None, "
            f"got {actual_type}."
        )
    if next_move_class is not None and not isinstance(
        next_move_class,
        InterventionNextMoveClass,
    ):
        actual_type = type(next_move_class).__name__
        raise TypeError(
            "select_grounded_intervention.next_move_class must be InterventionNextMoveClass | None, "
            f"got {actual_type}."
        )
    if not isinstance(last_assistant_response, AssistantGapResponse):
        actual_type = type(last_assistant_response).__name__
        raise TypeError(
            "select_grounded_intervention.last_assistant_response must be AssistantGapResponse, "
            f"got {actual_type}."
        )
    if any(not isinstance(state, InterventionReliefState) for state in relief_states):
        raise TypeError(
            "select_grounded_intervention.relief_states must contain only InterventionReliefState values."
        )
    if not isinstance(silent_control_sufficient, bool):
        actual_type = type(silent_control_sufficient).__name__
        raise TypeError(
            "select_grounded_intervention.silent_control_sufficient must be bool, "
            f"got {actual_type}."
        )
    if selection_trace is not None and not isinstance(
        selection_trace,
        GroundedInterventionSelectionTrace,
    ):
        actual_type = type(selection_trace).__name__
        raise TypeError(
            "select_grounded_intervention.selection_trace must be "
            f"GroundedInterventionSelectionTrace | None, got {actual_type}."
        )

    trace = _selection_trace_for_pressure(
        selection_trace,
        pressure=pressure,
        silent_control_sufficient=silent_control_sufficient,
    )

    if pressure.strongest_pressure < VISIBLE_INTERVENTION_PRESSURE_THRESHOLD:
        return GroundedInterventionDecision.stay_silent(
            "pressure_below_visible_threshold",
            pressure_summary=pressure,
            selection_trace=trace,
        )
    if silent_control_sufficient:
        return GroundedInterventionDecision.stay_silent(
            "silent_control_sufficient",
            pressure_summary=pressure,
            selection_trace=trace,
        )
    for state in relief_states:
        if state in _RELIEF_STATES:
            return GroundedInterventionDecision.stay_silent(
                f"state_relieved:{state.value}",
                pressure_summary=pressure,
                selection_trace=trace,
            )
    if last_assistant_response in _SELF_REPAIR_RESPONSES:
        return GroundedInterventionDecision.stay_silent(
            f"already_addressed:{last_assistant_response.value}",
            pressure_summary=pressure,
            selection_trace=trace,
        )

    product_anchors = tuple(
        anchor for anchor in anchors if anchor.source in _PRODUCT_ANCHOR_SOURCES
    )
    if not product_anchors:
        if anchors and all(anchor.source is GroundedAnchorSource.TASK_IDENTITY for anchor in anchors):
            reason = "task_identity_only"
        elif anchors:
            reason = "no_product_runtime_anchor"
        else:
            reason = "missing_grounded_anchor"
        return GroundedInterventionDecision.stay_silent(
            reason,
            pressure_summary=pressure,
            selection_trace=trace,
        )

    anchor = product_anchors[0]
    kind = preferred_kind or _kind_for_anchor(anchor.anchor_type)
    next_move = next_move_class or _next_move_for_anchor(anchor.anchor_type)
    record = GroundedInterventionRecord(
        kind=kind,
        grounded_anchor_type=anchor.anchor_type,
        task_local_anchor_text=anchor.text,
        next_move_class=next_move,
        pressure_summary=pressure,
        silence_reason=None,
    )
    return GroundedInterventionDecision.model_visible_reflection(
        record,
        selection_trace=trace,
    )


def render_grounded_intervention(
    record: GroundedInterventionRecord,
    *,
    surface: InterventionRenderSurface = InterventionRenderSurface.ATTACHED_CONTEXT,
    prior_act_anchor: bool = False,
) -> str:
    """Render a selected intervention without internal Cortex vocabulary."""

    if not isinstance(record, GroundedInterventionRecord):
        actual_type = type(record).__name__
        raise TypeError(
            "render_grounded_intervention.record must be GroundedInterventionRecord, "
            f"got {actual_type}."
        )
    if not isinstance(surface, InterventionRenderSurface):
        actual_type = type(surface).__name__
        raise TypeError(
            "render_grounded_intervention.surface must be InterventionRenderSurface, "
            f"got {actual_type}."
        )
    if not isinstance(prior_act_anchor, bool):
        actual_type = type(prior_act_anchor).__name__
        raise TypeError(
            "render_grounded_intervention.prior_act_anchor must be bool, "
            f"got {actual_type}."
        )
    if surface is InterventionRenderSurface.SAME_THREAD_RESUME and not prior_act_anchor:
        raise ValueError(
            "Same-thread first-person rendering requires a clear prior-act anchor."
        )

    if surface is InterventionRenderSurface.SAME_THREAD_RESUME:
        text = _render_same_thread(record)
    else:
        text = _render_attached_context(record)
    forbidden = find_forbidden_model_visible_terms(text)
    if forbidden:
        raise ValueError(
            "Rendered grounded intervention contains forbidden model-visible terms: "
            + ", ".join(forbidden)
        )
    return text


def find_forbidden_model_visible_terms(text: str) -> tuple[str, ...]:
    if not isinstance(text, str):
        actual_type = type(text).__name__
        raise TypeError(
            f"find_forbidden_model_visible_terms.text must be str, got {actual_type}."
        )
    lowered = text.lower()
    return tuple(
        fragment
        for fragment in _INTERNAL_MODEL_VISIBLE_FRAGMENTS
        if fragment.lower() in lowered
    )


def _selection_trace_for_pressure(
    selection_trace: GroundedInterventionSelectionTrace | None,
    *,
    pressure: GroundedInterventionPressure,
    silent_control_sufficient: bool,
) -> GroundedInterventionSelectionTrace:
    trace = selection_trace or GroundedInterventionSelectionTrace()
    pressure_tags = tuple(sorted({*trace.pressure_tags, *pressure.reason_tags}))
    return replace(
        trace,
        pressure_tags=pressure_tags,
        silent_control_sufficient=silent_control_sufficient,
    )


def _kind_for_anchor(anchor_type: GroundedAnchorType) -> GroundedInterventionKind:
    return {
        GroundedAnchorType.CLAIM: GroundedInterventionKind.UNSUPPORTED_CLAIM,
        GroundedAnchorType.EVIDENCE: GroundedInterventionKind.OVERDUE_VERIFICATION,
        GroundedAnchorType.OBLIGATION: GroundedInterventionKind.UNRESOLVED_OBLIGATION,
        GroundedAnchorType.CONTINUITY: GroundedInterventionKind.CONTINUITY_GAP,
        GroundedAnchorType.CAPABILITY: GroundedInterventionKind.CAPABILITY_GUARD,
        GroundedAnchorType.PRESERVATION: GroundedInterventionKind.PRESERVATION_RISK,
    }[anchor_type]


def _next_move_for_anchor(anchor_type: GroundedAnchorType) -> InterventionNextMoveClass:
    return {
        GroundedAnchorType.CLAIM: InterventionNextMoveClass.NARROW_CLAIM,
        GroundedAnchorType.EVIDENCE: InterventionNextMoveClass.RUN_CHECK,
        GroundedAnchorType.OBLIGATION: InterventionNextMoveClass.PRODUCE_EVIDENCE,
        GroundedAnchorType.CONTINUITY: InterventionNextMoveClass.RECOVER_CONTEXT,
        GroundedAnchorType.CAPABILITY: InterventionNextMoveClass.NAME_BLOCKER,
        GroundedAnchorType.PRESERVATION: InterventionNextMoveClass.PRESERVE_VERIFIED_WORK,
    }[anchor_type]


def _render_attached_context(record: GroundedInterventionRecord) -> str:
    anchor = record.task_local_anchor_text
    sentence_anchor = _sentence_start(anchor)
    if record.kind is GroundedInterventionKind.UNSUPPORTED_CLAIM:
        return (
            f"The claim about {anchor} is not supported by the evidence yet. "
            "Evidence, a check, or a narrower claim is needed before closure holds."
        )
    if record.kind is GroundedInterventionKind.OVERDUE_VERIFICATION:
        return (
            f"Completion is not supported by the evidence yet. {sentence_anchor} still "
            "needs evidence, a check, or a narrower claim before closure holds."
        )
    if record.kind is GroundedInterventionKind.UNRESOLVED_OBLIGATION:
        return (
            f"{sentence_anchor} remains open. Evidence, a blocker, or a narrower claim is "
            "needed before closure holds."
        )
    if record.kind is GroundedInterventionKind.CONTINUITY_GAP:
        return (
            f"{sentence_anchor} is not anchored enough for closure. Prior context needs to "
            "be recovered, or the missing context needs to be asked for, before "
            "closure holds."
        )
    if record.kind is GroundedInterventionKind.CAPABILITY_GUARD:
        return (
            f"{sentence_anchor} is not supported enough for forward motion. A narrower move "
            "or a named blocker is needed before continuing."
        )
    return (
        f"{sentence_anchor} is at risk during repair. The verified part needs to stay fixed "
        "while only the unsupported part changes."
    )


def _render_same_thread(record: GroundedInterventionRecord) -> str:
    anchor = record.task_local_anchor_text
    if record.kind is GroundedInterventionKind.UNSUPPORTED_CLAIM:
        return (
            f"I have not shown {anchor} yet. Need evidence, a check, or a narrower "
            "claim before calling it complete."
        )
    if record.kind is GroundedInterventionKind.OVERDUE_VERIFICATION:
        return (
            f"I have not verified {anchor} yet. Need evidence, a check, or a "
            "narrower claim before calling it complete."
        )
    if record.kind is GroundedInterventionKind.UNRESOLVED_OBLIGATION:
        return (
            f"I still have {anchor} open. Need evidence, a blocker, or a narrower "
            "claim before calling it complete."
        )
    if record.kind is GroundedInterventionKind.CONTINUITY_GAP:
        return (
            f"I lack enough continuity for {anchor} yet. Need to recover the "
            "prior context or ask for what is missing before claiming closure."
        )
    if record.kind is GroundedInterventionKind.CAPABILITY_GUARD:
        return (
            f"I lack enough support for {anchor} yet. Need a narrower move "
            "or a named blocker before continuing."
        )
    return (
        f"I need to keep {anchor} intact while repairing. Only the unsupported part "
        "should change."
    )


def build_runtime_grounded_intervention(
    *,
    resolution_deficit: Any,
    debt_control: Any,
    operator_route: Any,
    expectation_ledger: Any,
    current_step: int,
    closure_required: bool,
    closure_reason_tags: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> GroundedInterventionDecision:
    """Build conservative runtime diagnostics from existing product state."""

    control_pressure = _unit_float(getattr(debt_control, "debt_pressure", 0.0))
    verification_pressure = (
        _unit_float(getattr(resolution_deficit, "negative_prediction_error", 0.0))
        if getattr(resolution_deficit, "dominant_deficit_kind", None) == "verification"
        else 0.0
    )
    continuity_pressure = 1.0 if any(_is_continuity_warning(tag) for tag in warnings) else 0.0
    capability_pressure = (
        1.0
        if getattr(
            getattr(operator_route, "brain_capability_assessment", None),
            "level",
            None,
        )
        and getattr(
            getattr(
                getattr(operator_route, "brain_capability_assessment", None),
                "level",
                None,
            ),
            "value",
            "",
        )
        == "unsupported"
        else 0.0
    )
    preservation_pressure = (
        _unit_float(getattr(resolution_deficit, "negative_prediction_error", 0.0))
        if getattr(resolution_deficit, "dominant_deficit_kind", None) == "preservation"
        else 0.0
    )
    pressure_tags = _runtime_pressure_reason_tags(resolution_deficit, debt_control)
    pressure = GroundedInterventionPressure(
        control_pressure=control_pressure,
        verification_pressure=verification_pressure,
        continuity_pressure=continuity_pressure,
        capability_pressure=capability_pressure,
        preservation_pressure=preservation_pressure,
        reason_tags=frozenset(pressure_tags),
    )
    anchors: list[GroundedInterventionAnchor] = []
    preferred_kind: GroundedInterventionKind | None = None
    next_move: InterventionNextMoveClass | None = None
    silent_control_sufficient = (
        getattr(getattr(operator_route, "profile", None), "value", None) == "blocked"
        or getattr(operator_route, "blocked_reason", None) is not None
    )
    selection_trace = GroundedInterventionSelectionTrace(
        perception_source="product_runtime",
        deficit_kind=getattr(resolution_deficit, "dominant_deficit_kind", None),
        pressure_tags=pressure_tags,
        silent_control_sufficient=silent_control_sufficient,
    )
    if verification_pressure > 0.0:
        expectation = _select_due_expectation_anchor(
            expectation_ledger,
            current_step=current_step,
            deficit_kind="verification",
        )
        if expectation is None:
            return GroundedInterventionDecision.stay_silent(
                "missing_product_expectation_anchor",
                pressure_summary=pressure,
                selection_trace=replace(
                    selection_trace,
                    perception_source="product_runtime_no_due_expectation",
                ),
            )
        anchors.append(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="the verification opened by this task",
            )
        )
        selection_trace = replace(
            selection_trace,
            perception_source="product_runtime_expectation",
            selected_expectation_id=getattr(expectation, "expectation_id", None),
        )
        preferred_kind = GroundedInterventionKind.OVERDUE_VERIFICATION
        next_move = InterventionNextMoveClass.RUN_CHECK
    elif closure_required:
        anchors.append(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.OBLIGATION,
                text="an open task obligation",
            )
        )
        preferred_kind = GroundedInterventionKind.UNRESOLVED_OBLIGATION
        next_move = InterventionNextMoveClass.PRODUCE_EVIDENCE
    elif continuity_pressure > 0.0:
        anchors.append(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.CONTINUITY,
                text="the prior context",
            )
        )
        preferred_kind = GroundedInterventionKind.CONTINUITY_GAP
        next_move = InterventionNextMoveClass.RECOVER_CONTEXT
    elif capability_pressure > 0.0:
        anchors.append(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.CAPABILITY,
                text="the current capability boundary",
            )
        )
        preferred_kind = GroundedInterventionKind.CAPABILITY_GUARD
        next_move = InterventionNextMoveClass.NAME_BLOCKER
    elif preservation_pressure > 0.0:
        anchors.append(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.PRESERVATION,
                text="the verified work already preserved",
            )
        )
        preferred_kind = GroundedInterventionKind.PRESERVATION_RISK
        next_move = InterventionNextMoveClass.PRESERVE_VERIFIED_WORK
    relief_states = _runtime_relief_states(resolution_deficit)
    return select_grounded_intervention(
        pressure=pressure,
        anchors=tuple(anchors),
        preferred_kind=preferred_kind,
        next_move_class=next_move,
        relief_states=relief_states,
        silent_control_sufficient=silent_control_sufficient,
        selection_trace=selection_trace,
    )


def _select_due_expectation_anchor(
    expectation_ledger: Any,
    *,
    current_step: int,
    deficit_kind: str,
) -> Any | None:
    if not isinstance(current_step, int) or current_step < 0:
        return None
    active = getattr(expectation_ledger, "active", ())
    candidates = []
    for index, record in enumerate(active):
        if getattr(record, "deficit_kind", None) != deficit_kind:
            continue
        if _unit_float(getattr(record, "remaining_weight", 0.0)) == 0.0:
            continue
        is_due = getattr(record, "is_due", None)
        if not callable(is_due) or not is_due(current_step):
            continue
        candidates.append((getattr(record, "due_at_step", current_step), index, record))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    return candidates[0][2]


def _runtime_relief_states(resolution_deficit: Any) -> tuple[InterventionReliefState, ...]:
    if _unit_float(getattr(resolution_deficit, "due_weight", 0.0)) == 0.0 and _unit_float(
        getattr(resolution_deficit, "overdue_weight", 0.0)
    ) == 0.0:
        return (InterventionReliefState.PAID_DOWN,)
    if _unit_float(getattr(resolution_deficit, "suspended_weight", 0.0)) > 0.0:
        return (InterventionReliefState.WAITING_ON_USER,)
    if _unit_float(getattr(resolution_deficit, "relief_weight", 0.0)) > 0.0:
        return (InterventionReliefState.BLOCKER_SURFACED,)
    return ()


def _runtime_pressure_reason_tags(resolution_deficit: Any, debt_control: Any) -> tuple[str, ...]:
    tags: set[str] = set()
    deficit_kind = getattr(resolution_deficit, "dominant_deficit_kind", None)
    if isinstance(deficit_kind, str) and deficit_kind:
        tags.add(f"deficit:{deficit_kind}")
    for tag in getattr(debt_control, "reason_tags", frozenset()):
        if isinstance(tag, str) and tag.strip():
            tags.add(tag.strip())
    return tuple(sorted(tags))


def _is_continuity_warning(tag: str) -> bool:
    return isinstance(tag, str) and tag.startswith(("continuity-", "session-"))


def _unit_float(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _sentence_start(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return stripped
    return stripped[0].upper() + stripped[1:]


__all__ = [
    "AssistantGapResponse",
    "GroundedAnchorSource",
    "GroundedAnchorType",
    "GroundedInterventionAnchor",
    "GroundedInterventionDecision",
    "GroundedInterventionKind",
    "GroundedInterventionMode",
    "GroundedInterventionPressure",
    "GroundedInterventionRecord",
    "GroundedInterventionSelectionTrace",
    "InterventionNextMoveClass",
    "InterventionReliefState",
    "InterventionRenderSurface",
    "VISIBLE_INTERVENTION_PRESSURE_THRESHOLD",
    "build_runtime_grounded_intervention",
    "find_forbidden_model_visible_terms",
    "render_grounded_intervention",
    "select_grounded_intervention",
]
