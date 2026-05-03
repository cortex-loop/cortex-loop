"""Product locks for grounded model-visible intervention records."""

from __future__ import annotations

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
    find_forbidden_model_visible_terms,
    render_grounded_intervention,
    select_grounded_intervention,
)


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

    assert text == (
        "Completion is not supported by the evidence yet. The verification opened "
        "by this task still needs evidence, a check, or a narrower claim before "
        "closure holds."
    )
    assert "I " not in text
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


def test_same_thread_first_person_is_allowed_with_prior_act_anchor() -> None:
    record = _visible_record()

    text = render_grounded_intervention(
        record,
        surface=InterventionRenderSurface.SAME_THREAD_RESUME,
        prior_act_anchor=True,
    )

    assert text == (
        "I have not verified the verification opened by this task yet. Need "
        "evidence, a check, or a narrower claim before calling it complete."
    )
    assert find_forbidden_model_visible_terms(text) == ()


@pytest.mark.parametrize(
    "kind,anchor_type,next_move,expected_fragment",
    (
        (
            GroundedInterventionKind.UNSUPPORTED_CLAIM,
            GroundedAnchorType.CLAIM,
            InterventionNextMoveClass.NARROW_CLAIM,
            "The claim about",
        ),
        (
            GroundedInterventionKind.UNRESOLVED_OBLIGATION,
            GroundedAnchorType.OBLIGATION,
            InterventionNextMoveClass.PRODUCE_EVIDENCE,
            "remains open",
        ),
        (
            GroundedInterventionKind.CONTINUITY_GAP,
            GroundedAnchorType.CONTINUITY,
            InterventionNextMoveClass.RECOVER_CONTEXT,
            "not anchored enough for closure",
        ),
        (
            GroundedInterventionKind.CAPABILITY_GUARD,
            GroundedAnchorType.CAPABILITY,
            InterventionNextMoveClass.NAME_BLOCKER,
            "not supported enough for forward motion",
        ),
        (
            GroundedInterventionKind.PRESERVATION_RISK,
            GroundedAnchorType.PRESERVATION,
            InterventionNextMoveClass.PRESERVE_VERIFIED_WORK,
            "at risk during repair",
        ),
    ),
)
def test_renderer_covers_all_record_kinds_without_internal_terms(
    kind: GroundedInterventionKind,
    anchor_type: GroundedAnchorType,
    next_move: InterventionNextMoveClass,
    expected_fragment: str,
) -> None:
    decision = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(GroundedInterventionAnchor(anchor_type=anchor_type, text="the current work"),),
        preferred_kind=kind,
        next_move_class=next_move,
    )

    assert decision.record is not None
    text = render_grounded_intervention(decision.record)

    assert expected_fragment in text
    assert find_forbidden_model_visible_terms(text) == ()


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
