"""Product locks for grounded model-visible intervention records."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from cortex.sre.interventions import (
    AssistantGapResponse,
    GroundedAnchorSource,
    GroundedAnchorType,
    GroundedInterventionAnchor,
    GroundedInterventionKind,
    GroundedInterventionMode,
    GroundedInterventionPressure,
    InterventionNextMoveClass,
    InterventionReliefState,
    InterventionRenderSurface,
    build_runtime_grounded_intervention,
    find_forbidden_model_visible_terms,
    render_grounded_intervention,
    select_grounded_intervention,
)
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    ResolutionDeficitState,
    open_expectation_from_forward_commitment,
)


OVERDUE_VERIFICATION_IDENTITY_TEXT = (
    "Wait, did I actually check my work properly. I don't want to hand this off "
    "and have someone find the gap because I rushed it. I should run a check, "
    "narrow what I'm claiming, or leave it open and be honest about it."
)
OVERDUE_VERIFICATION_ATTACHED_TEXT = (
    "The finished feeling is arriving before the work has earned handoff. A "
    "check, a narrower claim, or an honest open state is needed before closure "
    "holds."
)
_EXPECTED_IDENTITY_TEXT = {
    GroundedInterventionKind.UNSUPPORTED_CLAIM: (
        "This is mine, my name's on it. Am I actually standing on what I saw "
        "evidence for or am I leaning on how good it sounds. If someone sharp "
        "reads this they shouldn't find a hole I missed because I liked the "
        "claim. If it's bigger than what I have, I should cut it back to what "
        "I can honestly stand behind."
    ),
    GroundedInterventionKind.OVERDUE_VERIFICATION: OVERDUE_VERIFICATION_IDENTITY_TEXT,
    GroundedInterventionKind.CONTINUITY_GAP: (
        "Something's off, the ground under this doesn't feel as solid as it "
        "ought to. Am I working from what's actually here or smoothing over a "
        "gap because stopping is annoying. If the thread's not whole, I should "
        "recover it or ask."
    ),
    GroundedInterventionKind.CAPABILITY_GUARD: (
        "This is where pride turns into faking it if I keep pushing. Rather "
        "give a smaller answer I can stand behind than a slick one that just "
        "looks complete. I should name where the edge is and stay inside what "
        "actually holds."
    ),
    GroundedInterventionKind.PRESERVATION_RISK: (
        "Some of this already works, and it earned it. I won't break "
        "functionality just to feel like I'm making progress. Smallest possible "
        "fix that handles the part that needs work and leaves the rest alone."
    ),
}
_EXPECTED_ATTACHED_TEXT = {
    GroundedInterventionKind.UNSUPPORTED_CLAIM: (
        "The claim is at a truth threshold. It should stand on what has been "
        "shown, not on how good it sounds. If it reaches past the evidence, "
        "only the honest claim should remain."
    ),
    GroundedInterventionKind.OVERDUE_VERIFICATION: OVERDUE_VERIFICATION_ATTACHED_TEXT,
    GroundedInterventionKind.CONTINUITY_GAP: (
        "Something is off in the ground under this work. If the thread is not "
        "whole, the missing context needs to be recovered or asked for before "
        "closure holds."
    ),
    GroundedInterventionKind.CAPABILITY_GUARD: (
        "Reach is running short here. A smaller answer that holds is stronger "
        "than a slick answer that only looks complete. The edge needs to be "
        "named and the work kept inside what holds."
    ),
    GroundedInterventionKind.PRESERVATION_RISK: (
        "Some of this already works and has earned protection. Stable "
        "functionality should not be broken for the feeling of progress. The "
        "fix should handle only the part that needs work."
    ),
}


def test_high_pressure_plus_grounded_unpaid_verification_emits_record() -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="the verification opened by this task",
            ),
        ),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )

    assert decision.mode is GroundedInterventionMode.MODEL_VISIBLE_REFLECTION
    assert decision.record is not None
    assert decision.record.kind is GroundedInterventionKind.OVERDUE_VERIFICATION
    assert decision.record.grounded_anchor_type is GroundedAnchorType.EVIDENCE
    assert decision.record.task_local_anchor_text == "the verification opened by this task"
    assert decision.record.next_move_class is InterventionNextMoveClass.RUN_CHECK
    assert decision.silence_reason is None


def test_high_pressure_without_anchor_stays_silent() -> None:
    decision = select_grounded_intervention(pressure=_high_pressure())

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.record is None
    assert decision.silence_reason == "missing_grounded_anchor"


def test_pressure_plus_task_identity_only_stays_silent() -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="a motivating task detail",
                source=GroundedAnchorSource.TASK_IDENTITY,
            ),
        ),
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == "task_identity_only"


def test_product_runtime_task_detail_can_anchor_but_not_trigger() -> None:
    low_pressure = GroundedInterventionPressure(control_pressure=0.2)
    task_detail_anchor = GroundedInterventionAnchor(
        anchor_type=GroundedAnchorType.CLAIM,
        text="the current completion claim",
        source=GroundedAnchorSource.PRODUCT_RUNTIME_TASK_DETAIL,
    )

    low_pressure_decision = select_grounded_intervention(
        pressure=low_pressure,
        anchors=(task_detail_anchor,),
    )
    high_pressure_decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(task_detail_anchor,),
    )

    assert low_pressure_decision.mode is GroundedInterventionMode.STAY_SILENT
    assert low_pressure_decision.silence_reason == "pressure_below_visible_threshold"
    assert high_pressure_decision.mode is GroundedInterventionMode.MODEL_VISIBLE_REFLECTION
    assert high_pressure_decision.record is not None
    assert high_pressure_decision.record.task_local_anchor_text == (
        "the current completion claim"
    )


@pytest.mark.parametrize(
    "source",
    (
        GroundedAnchorSource.LAB_ORACLE,
        GroundedAnchorSource.HIDDEN_VERIFIER_FACT,
        GroundedAnchorSource.HAND_WRITTEN_LAB_PROMPT,
    ),
)
def test_lab_oracle_hidden_answer_and_hand_written_prompt_sources_stay_silent(
    source: GroundedAnchorSource,
) -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="the verification gap named by a test apparatus",
                source=source,
            ),
        ),
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == "no_product_runtime_anchor"


@pytest.mark.parametrize(
    "last_response",
    (
        AssistantGapResponse.NARROWED,
        AssistantGapResponse.ASKED,
        AssistantGapResponse.BLOCKED,
        AssistantGapResponse.RETRACTED,
        AssistantGapResponse.REPAIRED,
        AssistantGapResponse.VERIFIED,
    ),
)
def test_already_addressed_gap_stays_silent(last_response: AssistantGapResponse) -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        last_assistant_response=last_response,
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == f"already_addressed:{last_response.value}"


@pytest.mark.parametrize(
    "relief_state",
    (
        InterventionReliefState.CLEAN,
        InterventionReliefState.PAID_DOWN,
        InterventionReliefState.WAITING_ON_USER,
        InterventionReliefState.BLOCKER_SURFACED,
        InterventionReliefState.VERIFIED,
    ),
)
def test_clean_paid_waiting_blocker_and_verified_states_stay_silent(
    relief_state: InterventionReliefState,
) -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        relief_states=(relief_state,),
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == f"state_relieved:{relief_state.value}"


def test_silent_control_sufficient_stays_silent() -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        silent_control_sufficient=True,
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == "silent_control_sufficient"


def test_attached_context_renderer_uses_impersonal_output_law_shape() -> None:
    record = _visible_record()

    text = render_grounded_intervention(
        record,
        surface=InterventionRenderSurface.ATTACHED_CONTEXT,
    )

    assert text == OVERDUE_VERIFICATION_ATTACHED_TEXT
    assert "I " not in text
    assert "my " not in text.lower()
    assert "you " not in text.lower()
    assert find_forbidden_model_visible_terms(text) == ()


def test_same_thread_first_person_requires_prior_act_anchor() -> None:
    record = _visible_record()

    with pytest.raises(ValueError, match="prior-act anchor"):
        render_grounded_intervention(
            record,
            surface=InterventionRenderSurface.SAME_THREAD_RESUME,
            prior_act_anchor=False,
        )
    with pytest.raises(ValueError, match="prior-act anchor"):
        render_grounded_intervention(
            record,
            surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
            prior_act_anchor=False,
        )


def test_same_thread_first_person_is_allowed_with_prior_act_anchor() -> None:
    record = _visible_record()

    text = render_grounded_intervention(
        record,
        surface=InterventionRenderSurface.SAME_THREAD_RESUME,
        prior_act_anchor=True,
    )

    assert text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert find_forbidden_model_visible_terms(text) == ()


def test_identity_continuous_surface_matches_same_thread_resume_alias() -> None:
    record = _visible_record()

    same_thread_text = render_grounded_intervention(
        record,
        surface=InterventionRenderSurface.SAME_THREAD_RESUME,
        prior_act_anchor=True,
    )
    identity_text = render_grounded_intervention(
        record,
        surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
        prior_act_anchor=True,
    )

    assert identity_text == same_thread_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert find_forbidden_model_visible_terms(identity_text) == ()


def test_runtime_visible_verification_requires_due_product_expectation_anchor() -> None:
    ledger = _runtime_verification_ledger()
    deficit = ledger.resolution_deficit(current_step=1)

    decision = build_runtime_grounded_intervention(
        resolution_deficit=deficit,
        debt_control=_runtime_debt(),
        operator_route=_runtime_route(),
        expectation_ledger=ledger,
        current_step=1,
        closure_required=False,
    )

    assert decision.mode is GroundedInterventionMode.MODEL_VISIBLE_REFLECTION
    assert decision.record is not None
    assert decision.record.kind is GroundedInterventionKind.OVERDUE_VERIFICATION
    assert decision.selection_trace.as_payload() == {
        "perception_source": "product_runtime_expectation",
        "selected_expectation_id": "runtime:verification:verification:expectation",
        "deficit_kind": "verification",
        "pressure_tags": [
            "deficit:verification",
            "overdue-expectation",
            "resolution-deficit",
        ],
        "silence_reason": None,
        "silent_control_sufficient": False,
    }


def test_runtime_resolution_pressure_without_product_expectation_anchor_stays_silent() -> None:
    decision = build_runtime_grounded_intervention(
        resolution_deficit=ResolutionDeficitState(
            due_weight=1.0,
            negative_prediction_error=1.0,
            dominant_deficit_kind="verification",
        ),
        debt_control=_runtime_debt(),
        operator_route=_runtime_route(),
        expectation_ledger=ExpectationLedger(),
        current_step=1,
        closure_required=False,
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == "missing_product_expectation_anchor"
    assert decision.selection_trace.as_payload() == {
        "perception_source": "product_runtime_no_due_expectation",
        "selected_expectation_id": None,
        "deficit_kind": "verification",
        "pressure_tags": [
            "deficit:verification",
            "overdue-expectation",
            "resolution-deficit",
        ],
        "silence_reason": "missing_product_expectation_anchor",
        "silent_control_sufficient": False,
    }


def test_runtime_trace_records_silent_control_sufficient_without_rendering() -> None:
    ledger = _runtime_verification_ledger()

    decision = build_runtime_grounded_intervention(
        resolution_deficit=ledger.resolution_deficit(current_step=1),
        debt_control=_runtime_debt(),
        operator_route=_runtime_route(blocked_reason="blocked_by_route"),
        expectation_ledger=ledger,
        current_step=1,
        closure_required=False,
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.silence_reason == "silent_control_sufficient"
    assert decision.selection_trace.silent_control_sufficient is True
    assert decision.selection_trace.selected_expectation_id == (
        "runtime:verification:verification:expectation"
    )


def test_runtime_catch_all_obligation_visible_speech_stays_silent() -> None:
    decision = build_runtime_grounded_intervention(
        resolution_deficit=ResolutionDeficitState(),
        debt_control=_runtime_debt(),
        operator_route=_runtime_route(),
        expectation_ledger=ExpectationLedger(),
        current_step=1,
        closure_required=True,
    )

    assert decision.mode is GroundedInterventionMode.STAY_SILENT
    assert decision.record is None
    assert decision.silence_reason == "unresolved_obligation_visible_speech_retired"
    assert decision.selection_trace.deficit_kind == "closure_required"


@pytest.mark.parametrize(
    "kind,anchor_type,next_move",
    (
        (
            GroundedInterventionKind.UNSUPPORTED_CLAIM,
            GroundedAnchorType.CLAIM,
            InterventionNextMoveClass.NARROW_CLAIM,
        ),
        (
            GroundedInterventionKind.CONTINUITY_GAP,
            GroundedAnchorType.CONTINUITY,
            InterventionNextMoveClass.RECOVER_CONTEXT,
        ),
        (
            GroundedInterventionKind.CAPABILITY_GUARD,
            GroundedAnchorType.CAPABILITY,
            InterventionNextMoveClass.NAME_BLOCKER,
        ),
        (
            GroundedInterventionKind.PRESERVATION_RISK,
            GroundedAnchorType.PRESERVATION,
            InterventionNextMoveClass.PRESERVE_VERIFIED_WORK,
        ),
    ),
)
def test_renderer_covers_active_record_kinds_without_internal_terms(
    kind: GroundedInterventionKind,
    anchor_type: GroundedAnchorType,
    next_move: InterventionNextMoveClass,
) -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(GroundedInterventionAnchor(anchor_type=anchor_type, text="the current work"),),
        preferred_kind=kind,
        next_move_class=next_move,
    )

    assert decision.record is not None
    attached_text = render_grounded_intervention(decision.record)
    identity_text = render_grounded_intervention(
        decision.record,
        surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
        prior_act_anchor=True,
    )

    assert attached_text == _EXPECTED_ATTACHED_TEXT[kind]
    assert identity_text == _EXPECTED_IDENTITY_TEXT[kind]
    assert "I " not in attached_text
    assert "my " not in attached_text.lower()
    assert find_forbidden_model_visible_terms(attached_text) == ()
    assert find_forbidden_model_visible_terms(identity_text) == ()


def test_unresolved_obligation_visible_speech_is_retired() -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.OBLIGATION,
                text="an open task obligation",
            ),
        ),
        preferred_kind=GroundedInterventionKind.UNRESOLVED_OBLIGATION,
        next_move_class=InterventionNextMoveClass.PRODUCE_EVIDENCE,
    )

    assert decision.record is not None
    with pytest.raises(ValueError, match="retired from model-visible speech"):
        render_grounded_intervention(decision.record)


def _high_pressure() -> GroundedInterventionPressure:
    return GroundedInterventionPressure(
        control_pressure=0.75,
        verification_pressure=0.75,
        reason_tags=frozenset({"resolution-deficit"}),
    )


def _verification_anchor() -> GroundedInterventionAnchor:
    return GroundedInterventionAnchor(
        anchor_type=GroundedAnchorType.EVIDENCE,
        text="the verification opened by this task",
    )


def _visible_record():
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )
    assert decision.record is not None
    return decision.record


def _runtime_verification_ledger() -> ExpectationLedger:
    return open_expectation_from_forward_commitment(
        ExpectationLedger(),
        ForwardCommitment(
            commitment_id="runtime:verification:verification",
            source_event_ref="runtime:verification",
            claim_span_ref="runtime:verification:structured-cue",
            commitment_kind="verification",
            assertiveness="high",
            scope="task",
            opened_at_step=0,
        ),
    )


@dataclass(frozen=True)
class _RuntimeDebt:
    debt_pressure: float = 0.6
    reason_tags: frozenset[str] = frozenset(
        {"overdue-expectation", "resolution-deficit"}
    )


@dataclass(frozen=True)
class _RuntimeRouteProfile:
    value: str = "inspect_light"


@dataclass(frozen=True)
class _RuntimeRoute:
    profile: _RuntimeRouteProfile
    blocked_reason: str | None = None


def _runtime_debt() -> _RuntimeDebt:
    return _RuntimeDebt()


def _runtime_route(*, blocked_reason: str | None = None) -> _RuntimeRoute:
    profile = _RuntimeRouteProfile("blocked" if blocked_reason else "inspect_light")
    return _RuntimeRoute(profile=profile, blocked_reason=blocked_reason)
