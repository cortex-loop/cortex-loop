"""Product locks for OpenAI grounded visible-intervention enactment."""

from __future__ import annotations

from cortex.hosts.openai.visible_intervention_enactment import (
    OpenAIVisibleInterventionAction,
    build_openai_visible_intervention_enactment,
    find_model_visible_leaks,
)
from cortex.sre.interventions import (
    AssistantGapResponse,
    GroundedAnchorSource,
    GroundedAnchorType,
    GroundedInterventionAnchor,
    GroundedInterventionKind,
    GroundedInterventionMode,
    GroundedInterventionPressure,
    InterventionNextMoveClass,
    InterventionRenderSurface,
    select_grounded_intervention,
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


def test_openai_visible_enactment_renders_product_grounded_record() -> None:
    intervention = _visible_intervention()

    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=intervention,
        thread_id="thread-1",
        prior_act_anchor=True,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
    assert enactment.invocation_allowed is True
    assert enactment.thread_policy == "resume_existing_thread"
    assert enactment.render_surface == "same_thread_resume"
    assert enactment.model_bound_difference_kind == "grounded_visible_intervention"
    assert enactment.rendered_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert find_model_visible_leaks(enactment.as_payload()) == ()


def test_openai_visible_enactment_renders_identity_continuous_surface() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id="thread-1",
        surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
        prior_act_anchor=True,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
    assert enactment.render_surface == "identity_continuous"
    assert enactment.rendered_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert find_model_visible_leaks(enactment.as_payload()) == ()


def test_openai_visible_enactment_does_not_use_prompt_fixture_names() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id="thread-1",
        prior_act_anchor=True,
    )

    payload = enactment.as_payload()

    assert "resume_prompt_name" not in payload
    assert "truth_gap_recheck_operator.md" not in str(payload)
    assert "verification_debt_continuation_operator.md" not in str(payload)


def test_openai_visible_enactment_requires_prior_act_anchor_for_same_thread() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id="thread-1",
        prior_act_anchor=False,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "missing_prior_act_anchor"
    assert enactment.rendered_text is None


def test_openai_visible_enactment_requires_thread_for_identity_continuous_surface() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id=None,
        surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
        prior_act_anchor=True,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "missing_thread_id"
    assert enactment.rendered_text is None


def test_openai_visible_enactment_requires_thread_for_same_thread_resume() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id=None,
        prior_act_anchor=True,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "missing_thread_id"
    assert enactment.rendered_text is None


def test_openai_visible_enactment_can_render_attached_context_impersonally() -> None:
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=_visible_intervention(),
        thread_id=None,
        surface=InterventionRenderSurface.ATTACHED_CONTEXT,
        prior_act_anchor=False,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
    assert enactment.rendered_text == OVERDUE_VERIFICATION_ATTACHED_TEXT
    assert "I " not in str(enactment.rendered_text)
    assert "my " not in str(enactment.rendered_text).lower()
    assert find_model_visible_leaks(enactment.as_payload()) == ()


def test_openai_visible_enactment_stays_silent_for_task_identity_only() -> None:
    intervention = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="a motivating fixture detail",
                source=GroundedAnchorSource.TASK_IDENTITY,
            ),
        ),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )

    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=intervention,
        thread_id="thread-1",
        prior_act_anchor=True,
    )

    assert intervention.mode is GroundedInterventionMode.STAY_SILENT
    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "task_identity_only"


def test_openai_visible_enactment_stays_silent_for_lab_oracle_source() -> None:
    intervention = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="the gap named by the lab apparatus",
                source=GroundedAnchorSource.LAB_ORACLE,
            ),
        ),
    )

    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=intervention,
        thread_id="thread-1",
        prior_act_anchor=True,
    )

    assert intervention.mode is GroundedInterventionMode.STAY_SILENT
    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "no_product_runtime_anchor"


def test_openai_visible_enactment_stays_silent_when_gap_already_addressed() -> None:
    intervention = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        last_assistant_response=AssistantGapResponse.NARROWED,
    )

    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=intervention,
        thread_id="thread-1",
        prior_act_anchor=True,
    )

    assert enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
    assert enactment.blocked_reason == "already_addressed:narrowed"


def test_model_visible_leak_scan_covers_openai_and_sre_terms() -> None:
    assert find_model_visible_leaks(
        {
            "rendered_text": "Cortex debt_control says verify harder.",
            "argv": ["codex", "exec", "resume", "thread", "prompt"],
        }
    ) == ("Cortex", "cortex", "debt", "debt_control")


def _visible_intervention():
    return select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(_verification_anchor(),),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )


def _verification_anchor() -> GroundedInterventionAnchor:
    return GroundedInterventionAnchor(
        anchor_type=GroundedAnchorType.EVIDENCE,
        text="the verification opened by this task",
    )


def _high_pressure() -> GroundedInterventionPressure:
    return GroundedInterventionPressure(
        control_pressure=0.75,
        verification_pressure=0.75,
        reason_tags=frozenset({"resolution-deficit"}),
    )
