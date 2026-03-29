"""Focused tests for direct OpenAI runtime-step behavior."""

import pytest

import cortex.runtime.openai as openai_runtime
from cortex.runtime.openai import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.reference_scoring import build_reference_allocation_scorecard
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


def test_openai_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw OpenAI host event name, not a canonical Cortex event name",
    ):
        run_openai_runtime_step(
            "external/observation",
            {"session_id": "oa-bad", "response_id": "resp-1", "delta": "hello"},
        )


def test_openai_runtime_step_enforces_guarded_feedback_pressure_to_check_when_evidence_dominates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        _guarded_state_with_feedback_pressure,
    )
    monkeypatch.setattr(
        openai_runtime,
        "select_reference_soft_control",
        lambda executive_state: _Selection(SoftControlFamily.BRANCH),
    )

    result = run_openai_runtime_step(
        "response.completed",
        {
            "session_id": "oa-guarded-feedback",
            "response_id": "resp-guarded-feedback",
            "commitment_id": "oa-guarded-feedback-commit",
            "externally_consequential": True,
            "result_artifact_ref": "oa-guarded-feedback-artifact",
        },
        OpenAIRuntimeSession(session_id="oa-guarded-feedback"),
    )

    assert result.selected_family is SoftControlFamily.BRANCH
    assert result.realized_family is SoftControlFamily.CHECK
    assert result.warnings == ("guarded-feedback-enforced:branch:check",)
    assert result.control_ledger_summary["primary_reason"] == (
        "guarded-feedback-enforced:branch:check"
    )
    assert result.commitment_result_kind == "certified"


class _Selection:
    def __init__(self, family: SoftControlFamily) -> None:
        self.selected_family = family
        self.scorecard = build_reference_allocation_scorecard(
            _guarded_state_with_feedback_pressure()
        )
        self.neutral_dominance = neutral_dominance_decision(self.scorecard)


def _guarded_state_with_feedback_pressure(
    *args: object,
    **kwargs: object,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="review-track"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="evidence", level=0.95),
                UncertaintyEstimate(class_tag="environment", level=0.75),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
                UncertaintyEstimate(class_tag="goal-progress", level=0.45),
            ),
            contradiction_spike_flags=frozenset({"prior-enforcement-override"}),
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="guarded_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="high",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRANCH,
                }
            ),
            feedback_pressure_tags=frozenset({"feedback:override-pressure"}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.GUARDED),
    )
