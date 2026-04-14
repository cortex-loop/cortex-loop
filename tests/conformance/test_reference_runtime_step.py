"""Unit tests for the first reference-host runtime step kernel."""

from dataclasses import replace

import pytest

import cortex.aux.publication as aux_publication
from cortex.aux.reference_replay import evaluate_aux_reference_q_mem_replay
import cortex.aux.support_priors as aux_support_priors
import cortex.hosts.reference.runtime as reference_runtime
from cortex.core.environment import EXECUTION_TRACE, ExecutiveEnvironmentView
from cortex.core.dispatch import DispatchLane
from cortex.hosts.reference.runtime import (
    ReferenceRuntimeSession,
    run_reference_runtime_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback
from cortex.sre.families import SoftControlFamily
from cortex.sre.mediation import (
    ReferenceMediationMode,
    finalize_reference_soft_control,
)
from cortex.sre.operator_routing import OperatorTaskMode
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

from tests.experimental._aux_test_support import make_aux_reference_replay_corpus


def test_reference_runtime_session_tracks_minimum_live_state() -> None:
    session = ReferenceRuntimeSession(session_id="session-1")

    assert session.session_id == "session-1"
    assert session.event_index == 0
    assert session.branch_registry == ("main",)
    assert session.active_track_ref == "main"
    assert session.pending_goal_refs == ()
    assert session.budget_history == ()
    assert session.brake_history == ()
    assert session.last_selected_family is None
    assert session.last_commitment_result_summary is None
    assert session.last_realization_feedback is None
    assert session.feedback_window.entries == ()
    assert session.as_summary()["branch_registry"] == ["main"]
    assert session.as_summary()["active_track_ref"] == "main"


def test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-1"},
    )

    assert result.event_index == 1
    assert result.bound_event.observation.event.native_event_name == "context/load"
    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert result.brake_state is BrakeState.GUARDED
    assert result.executive_state_summary["posture"] == "inspect"
    assert result.executive_state_summary["mode_tag"] == "guarded_review"
    assert result.executive_state_summary["budget_band"] == "low"
    assert result.operator_route_payload["route_profile"] == "inspect_light"
    assert result.operator_route_payload["route_budget"]["allow_extra_read_pass"] is True
    assert result.control_ledger_summary["event_class"] == "cheap"
    assert result.control_ledger_summary["admissible_families"] == [
        "neutral",
        "seek-context",
        "check",
        "brake",
    ]
    assert result.control_ledger_summary["selected_family"] == "seek-context"
    assert result.control_ledger_summary["realized_family"] == "seek-context"
    assert result.control_ledger_summary["dominant_uncertainty_sources"] == [
        "host-capability",
        "environment",
    ]
    assert result.control_ledger_summary["brake_state"] == "guarded"
    assert result.control_ledger_summary["budget_band"] == "low"
    assert result.control_ledger_summary["primary_reason"] is None
    assert result.executive_state_summary["probe_path_state"] == "available"
    assert result.executive_state_summary["probe_unavailable_reason"] is None
    _assert_allocation_diagnostics_shape(
        result.control_ledger_summary["allocation_diagnostics"],
        activation_threshold=0.37,
        expected_alpha=0.75,
        expect_allocated_equals_online=False,
        expected_probe_path_state="available",
        expected_probe_unavailable_reason=None,
        expected_mediation={
            "mediation_active": False,
            "mediation_identity": True,
            "selected_family_before_finalization": "seek-context",
            "selected_family_after_finalization": "seek-context",
            "preferred_opportunity_ref": None,
            "direct_opportunity_specialization_used": False,
        },
    )
    assert result.feedback_window_summary_payload == {
        "window_size": 0,
        "rejection_count": 0,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "evidence_state_move_count": 0,
        "continuity_improvement_count": 0,
        "family_change_without_evidence_count": 0,
        "same_family_no_progress_count": 0,
        "same_context_retry_count": 0,
        "goal_progress_floor": 0.0,
        "degradation_pressure_bonus": 0,
        "sustained_spike_flags": [],
    }
    assert result.commitment_result_kind is None
    assert result.session.session_id == "session-1"
    assert result.session.active_track_ref == "main"
    assert result.session.budget_history == ("shell-low",)
    assert result.session.brake_history == ("guarded",)
    assert result.session.last_selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.session.last_commitment_result_summary is None
    assert isinstance(result.session.last_realization_feedback, ReferenceRealizationFeedback)
    assert result.session.last_realization_feedback.as_summary() == {
        "selected_family": "seek-context",
        "realized_family": "seek-context",
        "brake_state": "guarded",
        "task_mode": "inspect",
        "commitment_result_kind": None,
        "warning_codes": [],
        "host_friction_tags": ["capability-view-missing"],
        "probe_result_class": "succeeded",
        "evidence_state_moved": False,
        "continuity_improved": False,
    }
    assert result.session.feedback_window.entries == (result.session.last_realization_feedback,)
    assert result.session_summary["feedback_window_size"] == 1


def test_reference_runtime_step_cheap_continuity_debt_surfaces_resume_posture() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "session-reference-resume-posture",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
        },
    )

    assert result.executive_state.mode_and_gating.task_mode is OperatorTaskMode.RESUME_EXECUTE
    assert result.executive_signal_summary.task_mode is OperatorTaskMode.RESUME_EXECUTE
    assert result.executive_state_summary["posture"] == "resume"
    assert result.operator_route_payload["route_profile"] == "continuity_standard"
    assert result.operator_route_payload["route_budget"]["allow_resume"] is True
    assert result.operator_route_payload["visible_burden_sensitivity"] == pytest.approx(
        result.executive_state.control_allocation.visible_burden_scale
    )


def test_reference_runtime_step_selects_seek_context_when_capability_view_is_missing() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-missing-capability-view"},
        executive_environment_view=ExecutiveEnvironmentView(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-host", "local-cli-runtime"}),
        ),
    )

    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert "capability-view-missing" in result.executive_state_summary["host_friction_tags"]
    assert result.brake_state is BrakeState.GUARDED
    assert result.executive_state_summary["family_mask"] == [
        "brake",
        "check",
        "neutral",
        "seek-context",
    ]
    assert result.executive_state_summary["top_family_set"] == [
        "brake",
        "neutral",
        "seek-context",
    ]
    assert result.control_ledger_summary["admissible_families"] == [
        "neutral",
        "seek-context",
        "check",
        "brake",
    ]
    assert result.control_ledger_summary["selected_family"] == "seek-context"
    assert result.control_ledger_summary["realized_family"] == "seek-context"
    assert result.executive_state_summary["probe_path_state"] == "available"
    assert result.executive_state_summary["probe_unavailable_reason"] is None
    _assert_allocation_diagnostics_shape(
        result.control_ledger_summary["allocation_diagnostics"],
        activation_threshold=0.37,
        expected_alpha=0.75,
        expect_allocated_equals_online=False,
        expected_probe_path_state="available",
        expected_probe_unavailable_reason=None,
        expected_mediation={
            "mediation_active": False,
            "mediation_identity": True,
            "selected_family_before_finalization": "seek-context",
            "selected_family_after_finalization": "seek-context",
            "preferred_opportunity_ref": None,
            "direct_opportunity_specialization_used": False,
        },
    )
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["selected_delta_over_neutral"]
        > result.control_ledger_summary["allocation_diagnostics"]["activation_threshold"]
    )


def test_reference_runtime_step_experimental_mediation_specializes_reference_mcp_query() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-missing-capability-view"},
        executive_environment_view=ExecutiveEnvironmentView(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-host", "local-cli-runtime"}),
        ),
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
    )

    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert result.executive_state_summary["probe_path_state"] == "available"
    assert result.executive_state_summary["probe_unavailable_reason"] is None
    _assert_allocation_diagnostics_shape(
        result.control_ledger_summary["allocation_diagnostics"],
        activation_threshold=0.37,
        expected_alpha=0.75,
        expect_allocated_equals_online=False,
        expected_probe_path_state="available",
        expected_probe_unavailable_reason=None,
        expected_mediation={
            "mediation_active": True,
            "mediation_identity": False,
            "selected_family_before_finalization": "seek-context",
            "selected_family_after_finalization": "seek-context",
            "preferred_opportunity_ref": "mcp.query",
            "direct_opportunity_specialization_used": True,
        },
    )


def test_reference_runtime_step_result_keeps_candidate_bearing_event_candidate_only() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-2"},
    )
    second = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "session-2",
            "candidate_id": "candidate-1",
        },
        first.session,
    )

    assert second.event_index == 2
    assert second.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert second.commitment_result_kind is None
    assert second.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert second.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert second.session.session_id == "session-2"
    assert second.session.active_track_ref == "main"
    assert second.session.budget_history == ("shell-low", "shell-medium")
    assert second.session.brake_history == ("guarded", "guarded")
    assert second.executive_state_summary["mode_tag"] == "review_pending"
    assert second.executive_state_summary["budget_band"] == "medium"
    assert second.control_ledger_summary["event_class"] == "candidate-bearing"
    assert second.control_ledger_summary["admissible_families"] == [
        "neutral",
        "seek-context",
        "check",
        "brake",
    ]
    assert second.control_ledger_summary["dominant_uncertainty_sources"] == [
        "host-capability",
        "evidence",
    ]
    assert second.session.last_commitment_result_summary == "candidate-only"
    assert second.session.last_realization_feedback is not None
    assert second.session.last_realization_feedback.commitment_result_kind is None
    assert second.session.feedback_window.entries[-1] == second.session.last_realization_feedback
    assert second.session_summary["event_index"] == 2


def test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref() -> None:
    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-3",
            "commitment_id": "commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-1",
        },
    )

    assert result.event_index == 1
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.commitment_result_kind == "certified"
    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert result.brake_state is BrakeState.GUARDED
    assert result.executive_state_summary["mode_tag"] == "commitment_path"
    assert result.executive_state_summary["budget_band"] == "high"
    assert result.control_ledger_summary["event_class"] == "full-commitment"
    assert result.control_ledger_summary["admissible_families"] == [
        "neutral",
        "seek-context",
        "check",
        "brake",
    ]
    assert result.control_ledger_summary["selected_family"] == "seek-context"
    assert result.control_ledger_summary["realized_family"] == "seek-context"
    assert result.control_ledger_summary["dominant_uncertainty_sources"] == [
        "host-capability",
        "evidence",
    ]
    assert result.control_ledger_summary["brake_state"] == "guarded"
    assert result.control_ledger_summary["budget_band"] == "high"
    assert result.control_ledger_summary["primary_reason"] is None
    assert result.executive_state_summary["probe_path_state"] == "available"
    assert result.executive_state_summary["probe_unavailable_reason"] is None
    _assert_allocation_diagnostics_shape(
        result.control_ledger_summary["allocation_diagnostics"],
        activation_threshold=0.22,
        expected_alpha=0.75,
        expect_allocated_equals_online=False,
        expected_probe_path_state="available",
        expected_probe_unavailable_reason=None,
        expected_mediation={
            "mediation_active": False,
            "mediation_identity": True,
            "selected_family_before_finalization": "seek-context",
            "selected_family_after_finalization": "seek-context",
            "preferred_opportunity_ref": None,
            "direct_opportunity_specialization_used": False,
        },
    )
    assert result.session.active_track_ref == "main"
    assert result.session.budget_history == ("shell-high",)
    assert result.session.last_commitment_result_summary == "certified"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.commitment_result_kind == "certified"
    assert result.session.feedback_window.entries[-1] == result.session.last_realization_feedback


def test_reference_runtime_step_replay_publication_can_lift_check_allocation_without_changing_commitment_truth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("contradiction-review")
    scenario = _reference_replay_scenario("contradiction-review")
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-reference-replay-contradiction",
            "commitment_id": "commit-reference-replay-contradiction",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-reference-replay-contradiction",
        },
    )
    replay = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-reference-replay-contradiction",
            "commitment_id": "commit-reference-replay-contradiction",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-reference-replay-contradiction",
        },
        offline_publication=case_result.publication,
    )

    assert baseline.commitment_result_kind == replay.commitment_result_kind == "certified"
    assert baseline.selected_family is SoftControlFamily.CHECK
    assert replay.selected_family is SoftControlFamily.CHECK
    baseline_check = _score_payload_for_family(
        baseline.control_ledger_summary["allocation_diagnostics"]["scores"],
        "check",
    )
    replay_check = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "check",
    )
    assert baseline_check["memory_score"] == 0.0
    assert replay_check["memory_score"] > 0.0
    assert replay_check["allocated_score"] > baseline_check["allocated_score"]
    assert (
        "allocation:online-plus-memory" in replay_check["reason_tags"]
        or "allocation:full-mixed" in replay_check["reason_tags"]
    )
    assert tuple(replay.control_ledger_summary["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "chi_t",
        "rejected_cheaper_families",
        "probe_path_state",
        "probe_unavailable_reason",
        "probe_result_class",
        "verification_state",
        "explainability_profile",
        "anti_thrash",
        "scores",
        "mediation",
    )


def test_reference_runtime_step_uses_unaugmented_snapshot_for_executive_state_and_augmented_snapshot_only_for_memory_priors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("contradiction-review")
    original_builder = reference_runtime.build_reference_executive_state
    original_select = reference_runtime.select_reference_soft_control
    original_augment = aux_publication.augment_snapshot_with_offline_publication
    original_prior_builder = aux_support_priors.build_support_memory_prior_appendix
    captured: dict[str, object] = {}

    def builder_wrapper(
        observation,
        support_snapshot,
        environment_view,
        provisional_session,
        *,
        opportunities=(),
        audit_intensity="minimal",
        task_mode=None,
    ):
        captured["executive_state_support_snapshot"] = support_snapshot
        return original_builder(
            observation,
            support_snapshot,
            environment_view,
            provisional_session,
            opportunities=opportunities,
            audit_intensity=audit_intensity,
            task_mode=task_mode,
        )

    def augment_wrapper(snapshot, publication):
        captured["augment_input_snapshot"] = snapshot
        augmented = original_augment(snapshot, publication)
        captured["augmented_snapshot"] = augmented
        return augmented

    def prior_builder_wrapper(snapshot):
        captured["prior_builder_snapshot"] = snapshot
        return original_prior_builder(snapshot)

    def select_wrapper(executive_state, *args, **kwargs):
        captured["selection_memory_priors"] = kwargs.get("memory_priors")
        return original_select(executive_state, *args, **kwargs)

    monkeypatch.setattr(reference_runtime, "build_reference_executive_state", builder_wrapper)
    monkeypatch.setattr(aux_publication, "augment_snapshot_with_offline_publication", augment_wrapper)
    monkeypatch.setattr(aux_support_priors, "build_support_memory_prior_appendix", prior_builder_wrapper)
    monkeypatch.setattr(reference_runtime, "select_reference_soft_control", select_wrapper)

    replay = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-reference-replay-law-lock",
            "commitment_id": "commit-reference-replay-law-lock",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-reference-replay-law-lock",
        },
        offline_publication=case_result.publication,
    )

    assert replay.commitment_result_kind == "certified"
    assert captured["executive_state_support_snapshot"] is captured["augment_input_snapshot"]
    assert captured["prior_builder_snapshot"] is captured["augmented_snapshot"]
    assert captured["prior_builder_snapshot"] is not captured["executive_state_support_snapshot"]
    assert captured["selection_memory_priors"] is not None


def test_reference_runtime_step_replay_publication_can_lift_branch_allocation_without_default_behavior_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-branch"},
    )
    replay = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-branch"},
        offline_publication=case_result.publication,
    )

    assert baseline.commitment_result_kind is None
    assert replay.commitment_result_kind is None
    assert baseline.selected_family is SoftControlFamily.NEUTRAL
    assert replay.selected_family is SoftControlFamily.BRANCH
    baseline_branch = _score_payload_for_family(
        baseline.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    replay_branch = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    assert baseline_branch["memory_score"] == 0.0
    assert replay_branch["memory_score"] > 0.0
    assert replay_branch["allocated_score"] > baseline_branch["allocated_score"]
    assert "allocation:full-mixed" in replay_branch["reason_tags"]


def test_reference_runtime_step_replay_publication_can_lift_retrieval_reuse_without_changing_default_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("retrieval-reuse")
    scenario = _reference_replay_scenario("retrieval-reuse")
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-retrieval"},
    )
    replay = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-retrieval"},
        offline_publication=case_result.publication,
    )

    assert baseline.commitment_result_kind is None
    assert replay.commitment_result_kind is None
    assert baseline.selected_family is SoftControlFamily.NEUTRAL
    assert replay.selected_family is SoftControlFamily.NEUTRAL
    baseline_seek_context = _score_payload_for_family(
        baseline.control_ledger_summary["allocation_diagnostics"]["scores"],
        "seek-context",
    )
    replay_seek_context = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "seek-context",
    )
    assert baseline_seek_context["memory_score"] == 0.0
    assert replay_seek_context["memory_score"] > 0.0
    assert replay_seek_context["allocated_score"] > baseline_seek_context["allocated_score"]
    assert "allocation:online-plus-memory" in replay_seek_context["reason_tags"]
    assert "q_mem-signal:retrieval" in replay_seek_context["reason_tags"]
    assert tuple(baseline.control_ledger_summary["allocation_diagnostics"]) == tuple(
        replay.control_ledger_summary["allocation_diagnostics"]
    )


def test_reference_runtime_step_replay_negative_case_keeps_payload_shape_and_commitment_truthful(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("no-lift-counterexample")
    scenario = _reference_replay_scenario("no-lift-counterexample")
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-no-lift"},
    )
    replay = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-no-lift"},
        offline_publication=case_result.publication,
    )

    assert baseline.commitment_result_kind is None
    assert replay.commitment_result_kind is None
    assert replay.selected_family is baseline.selected_family
    assert tuple(baseline.control_ledger_summary["allocation_diagnostics"]) == tuple(
        replay.control_ledger_summary["allocation_diagnostics"]
    )
    baseline_scores = baseline.control_ledger_summary["allocation_diagnostics"]["scores"]
    replay_scores = replay.control_ledger_summary["allocation_diagnostics"]["scores"]
    assert [score["family"] for score in baseline_scores] == [score["family"] for score in replay_scores]
    for baseline_score, replay_score in zip(baseline_scores, replay_scores, strict=True):
        assert replay_score["allocated_score"] == pytest.approx(baseline_score["allocated_score"])


def test_reference_runtime_step_burden_heavy_replay_case_does_not_create_false_positive_family_correction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("burden-heavy-counterexample")
    scenario = _reference_replay_scenario("burden-heavy-counterexample")
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-burden-heavy"},
    )
    replay = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-burden-heavy"},
        offline_publication=case_result.publication,
    )

    assert baseline.commitment_result_kind is None
    assert replay.commitment_result_kind is None
    assert replay.selected_family is baseline.selected_family is SoftControlFamily.NEUTRAL
    baseline_check = _score_payload_for_family(
        baseline.control_ledger_summary["allocation_diagnostics"]["scores"],
        "check",
    )
    replay_check = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "check",
    )
    assert replay_check["memory_score"] == 0.0
    assert replay_check["allocated_score"] == pytest.approx(baseline_check["allocated_score"])
    assert "allocation:online-plus-memory" not in replay_check["reason_tags"]


def test_reference_runtime_step_without_offline_publication_makes_no_aux_calls_and_keeps_memory_priors_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_select = reference_runtime.select_reference_soft_control
    captured: dict[str, object] = {}

    def forbidden_augment(*args, **kwargs):
        raise AssertionError("AUX augmentation should stay inactive without explicit offline publication.")

    def forbidden_prior_builder(*args, **kwargs):
        raise AssertionError("AUX memory priors should stay inactive without explicit offline publication.")

    def select_wrapper(executive_state, *args, **kwargs):
        captured["selection_memory_priors"] = kwargs.get("memory_priors")
        return original_select(executive_state, *args, **kwargs)

    monkeypatch.setattr(aux_publication, "augment_snapshot_with_offline_publication", forbidden_augment)
    monkeypatch.setattr(aux_support_priors, "build_support_memory_prior_appendix", forbidden_prior_builder)
    monkeypatch.setattr(reference_runtime, "select_reference_soft_control", select_wrapper)

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-reference-replay-default-path"},
    )

    assert result.commitment_result_kind is None
    assert captured["selection_memory_priors"] is None
    assert all(
        score["memory_score"] == 0.0
        for score in result.control_ledger_summary["allocation_diagnostics"]["scores"]
    )


def test_reference_runtime_step_rejects_malformed_open_without_mutating_existing_anchor() -> None:
    opened = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "session-open-1",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
        },
    )
    suspended = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "session-open-1",
            "branch_operation": "suspend",
            "branch_track_ref": "branch-alpha",
            "candidate_id": "candidate-1",
        },
        opened.session,
    )
    malformed_open = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "session-open-1",
            "branch_operation": "open",
        },
        suspended.session,
    )

    assert malformed_open.warnings == ("continuity-rejected:missing-open-track-ref",)
    assert malformed_open.session.branch_registry == ("main", "branch-alpha")
    assert malformed_open.session.active_track_ref == "main"
    assert malformed_open.session.pending_goal_refs == ("branch-alpha",)
    assert malformed_open.executive_state_summary["pending_goal_refs"] == ["branch-alpha"]


def test_reference_runtime_step_rejects_mismatched_session_id_without_reassigning_shell() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-stable-a"},
    )
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-stable-b"},
        first.session,
    )

    assert second.warnings == ("session-rejected:mismatched-session-id:session-stable-b",)
    assert second.session.session_id == "session-stable-a"
    assert second.session_summary["session_id"] == "session-stable-a"


def test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-a"},
    )
    rejected = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-b"},
        first.session,
    )
    follow_up = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-a"},
        rejected.session,
    )

    assert rejected.session.last_realization_feedback is not None
    assert rejected.session.last_realization_feedback.warning_codes == (
        "session-rejected:mismatched-session-id:session-feedback-b",
    )
    assert _goal_progress_level(follow_up) == 0.55
    assert (
        "prior-session-mismatch"
        in follow_up.executive_state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert follow_up.brake_state is BrakeState.GUARDED
    assert follow_up.realized_family is SoftControlFamily.NEUTRAL
    assert follow_up.control_ledger_summary["primary_reason"] == (
        "guarded-feedback-enforced:seek-context:neutral"
    )


def test_reference_runtime_step_normalizes_last_only_prior_session_and_preserves_feedback_pressure() -> None:
    prior_session = ReferenceRuntimeSession(
        session_id="session-feedback-a",
        event_index=1,
        budget_history=("shell-low",),
        brake_history=("quiescent",),
        last_selected_family=SoftControlFamily.NEUTRAL,
        last_realization_feedback=_feedback(
            "session-rejected:mismatched-session-id:session-feedback-b"
        ),
    )

    assert prior_session.feedback_window.entries == (
        prior_session.last_realization_feedback,
    )

    follow_up = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-a"},
        prior_session,
    )

    assert follow_up.feedback_window_summary_payload == {
        "window_size": 1,
        "rejection_count": 1,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "evidence_state_move_count": 0,
        "continuity_improvement_count": 0,
        "family_change_without_evidence_count": 0,
        "same_family_no_progress_count": 0,
        "same_context_retry_count": 0,
        "goal_progress_floor": 0.55,
        "degradation_pressure_bonus": 1,
        "sustained_spike_flags": ["prior-session-mismatch"],
    }
    assert _goal_progress_level(follow_up) == 0.55
    assert (
        "prior-session-mismatch"
        in follow_up.executive_state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert follow_up.brake_state is BrakeState.GUARDED


def test_reference_runtime_step_propagates_prior_enforcement_override_into_next_event_pressure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_builder = reference_runtime.build_reference_executive_state
    original_select = reference_runtime.select_reference_soft_control

    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_evidence,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.BRANCH),
    )
    enforced = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-feedback-latched",
            "commitment_id": "commit-feedback-latched",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-feedback-latched",
        },
    )

    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        original_builder,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        original_select,
    )
    follow_up = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-latched"},
        enforced.session,
    )

    assert enforced.session.last_realization_feedback is not None
    assert enforced.session.last_realization_feedback.selected_family is SoftControlFamily.BRANCH
    assert enforced.session.last_realization_feedback.realized_family is SoftControlFamily.CHECK
    assert _goal_progress_level(follow_up) == 0.45
    assert (
        "prior-enforcement-override"
        in follow_up.executive_state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert follow_up.brake_state is BrakeState.GUARDED


def test_reference_runtime_step_does_not_raise_feedback_pressure_after_clean_success() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-clean"},
    )
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-clean"},
        first.session,
    )

    assert _goal_progress_level(second) == 0.2
    assert not second.executive_state.uncertainty_monitoring.contradiction_spike_flags
    assert second.brake_state is BrakeState.GUARDED


def test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry() -> None:
    session = ReferenceRuntimeSession(
        session_id="session-feedback-window",
        event_index=3,
        budget_history=("shell-low", "shell-low", "shell-low"),
        brake_history=("quiescent", "quiescent", "quiescent"),
        last_selected_family=SoftControlFamily.NEUTRAL,
        last_realization_feedback=_feedback("warn-3"),
        feedback_window=reference_runtime.ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("warn-1"),
                _feedback("warn-2"),
                _feedback("warn-3"),
            )
        ),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-window"},
        session,
    )

    assert result.session.feedback_window.entries[0].warning_codes == ("warn-2",)
    assert result.session.feedback_window.entries[1].warning_codes == ("warn-3",)
    assert result.session.feedback_window.entries[2].warning_codes == ()
    assert result.session.feedback_window.entries[-1] == result.session.last_realization_feedback


def test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence() -> None:
    first = run_reference_runtime_step("ContextLoad", {"session_id": "session-a"})
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        first.session,
    )
    third = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        second.session,
    )

    assert third.feedback_window_summary_payload == {
        "window_size": 2,
        "rejection_count": 1,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "evidence_state_move_count": 0,
        "continuity_improvement_count": 0,
        "family_change_without_evidence_count": 0,
        "same_family_no_progress_count": 1,
        "same_context_retry_count": 0,
        "goal_progress_floor": 0.55,
        "degradation_pressure_bonus": 1,
        "sustained_spike_flags": ["prior-session-mismatch"],
    }
    assert third.session_summary["feedback_window_size"] == 3


def test_reference_runtime_step_reports_prior_window_summary_for_repeated_rejection_sequence() -> None:
    first = run_reference_runtime_step("ContextLoad", {"session_id": "session-a"})
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        first.session,
    )
    third = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        second.session,
    )
    fourth = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        third.session,
    )
    fifth = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        fourth.session,
    )

    assert fifth.feedback_window_summary_payload == {
        "window_size": 3,
        "rejection_count": 2,
        "override_count": 1,
        "latched_count": 1,
        "clean_success_streak": 0,
        "evidence_state_move_count": 0,
        "continuity_improvement_count": 0,
        "family_change_without_evidence_count": 1,
        "same_family_no_progress_count": 1,
        "same_context_retry_count": 0,
        "goal_progress_floor": 0.70,
        "degradation_pressure_bonus": 2,
        "sustained_spike_flags": [
            "prior-session-mismatch",
            "prior-enforcement-override",
            "sustained-feedback-disruption",
            "prior-non-productive-family-switch",
        ],
    }
    assert fifth.session_summary["feedback_window_size"] == 3


def test_reference_runtime_step_orders_admissible_families_by_soft_control_enum(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _state_with_ordered_family_mask,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.NEUTRAL),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-admissible-order"},
    )

    assert result.control_ledger_summary["admissible_families"] == [
        "neutral",
        "redirect",
        "check",
        "branch",
        "escalate",
    ]


def test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _state_with_tied_uncertainty_sources,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.NEUTRAL),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-uncertainty-order"},
    )

    assert result.control_ledger_summary["dominant_uncertainty_sources"] == [
        "environment",
        "evidence",
    ]


def test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_evidence,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.BRANCH),
    )

    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-priority-b",
            "commitment_id": "commit-priority",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-priority",
        },
        ReferenceRuntimeSession(session_id="session-priority-a"),
    )

    assert result.warnings == (
        "session-rejected:mismatched-session-id:session-priority-b",
        "latched-brake-enforced:branch:check",
    )
    assert result.control_ledger_summary["primary_reason"] == (
        "latched-brake-enforced:branch:check"
    )
    assert result.commitment_result_kind == "certified"


def test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reference_runtime, "build_reference_executive_state", _latched_state_with_evidence)
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.BRANCH),
    )

    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-latched-check",
            "commitment_id": "commit-latched-check",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-latched-check",
        },
    )

    assert result.selected_family is SoftControlFamily.BRANCH
    assert result.realized_family is SoftControlFamily.CHECK
    assert result.warnings == ("latched-brake-enforced:branch:check",)
    assert result.control_ledger_summary["selected_family"] == "branch"
    assert result.control_ledger_summary["realized_family"] == "check"
    assert result.control_ledger_summary["primary_reason"] == "latched-brake-enforced:branch:check"
    assert result.commitment_result_kind == "certified"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.realized_family is SoftControlFamily.CHECK


def test_reference_runtime_step_enforces_latched_brake_to_neutral_without_evidence_or_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reference_runtime, "build_reference_executive_state", _latched_state_without_evidence)
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.ESCALATE),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-latched-neutral"},
    )

    assert result.selected_family is SoftControlFamily.ESCALATE
    assert result.realized_family is SoftControlFamily.NEUTRAL
    assert result.warnings == ("latched-brake-enforced:escalate:neutral",)
    assert result.control_ledger_summary["selected_family"] == "escalate"
    assert result.control_ledger_summary["realized_family"] == "neutral"
    assert result.control_ledger_summary["primary_reason"] == "latched-brake-enforced:escalate:neutral"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.realized_family is SoftControlFamily.NEUTRAL


def test_reference_runtime_step_allows_latched_seek_context_when_native_host_capability_relief_is_directly_justified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_host_capability_gap,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.SEEK_CONTEXT),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-latched-seek-context"},
    )

    assert result.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert result.realized_family is SoftControlFamily.SEEK_CONTEXT
    assert result.warnings == ()
    assert result.control_ledger_summary["selected_family"] == "seek-context"
    assert result.control_ledger_summary["realized_family"] == "seek-context"
    assert result.control_ledger_summary["primary_reason"] is None


def test_reference_runtime_step_enforces_guarded_feedback_pressure_to_check_when_evidence_dominates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _guarded_state_with_feedback_pressure,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state, *args, **kwargs: _selection(SoftControlFamily.BRANCH),
    )

    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-guarded-feedback",
            "commitment_id": "commit-guarded-feedback",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-guarded-feedback",
        },
    )

    assert result.selected_family is SoftControlFamily.BRANCH
    assert result.realized_family is SoftControlFamily.CHECK
    assert result.warnings == ("guarded-feedback-enforced:branch:check",)
    assert result.control_ledger_summary["selected_family"] == "branch"
    assert result.control_ledger_summary["realized_family"] == "check"
    assert result.control_ledger_summary["primary_reason"] == (
        "guarded-feedback-enforced:branch:check"
    )
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.realized_family is SoftControlFamily.CHECK


def _goal_progress_level(result: object) -> float:
    executive_state = result.executive_state
    for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty:
        if estimate.class_tag == "goal-progress":
            return estimate.level
    raise AssertionError("missing goal-progress uncertainty estimate")


def _selection(selected_family: SoftControlFamily) -> object:
    class _Selection:
        def __init__(self, family: SoftControlFamily) -> None:
            self.selected_family_before_finalization = family
            self.selected_family = family
            self.chi_t = 0.0
            self.scorecard = build_reference_allocation_scorecard(_latched_state_with_evidence())
            self.neutral_dominance = neutral_dominance_decision(self.scorecard)
            self.mediation_finalization = finalize_reference_soft_control(family)

    return _Selection(selected_family)


def _assert_allocation_diagnostics_shape(
    payload: dict[str, object],
    *,
    activation_threshold: float,
    expected_alpha: float,
    expect_allocated_equals_online: bool,
    expected_probe_path_state: str,
    expected_probe_unavailable_reason: str | None,
    expected_mediation: dict[str, object],
) -> None:
    assert tuple(payload) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "chi_t",
        "rejected_cheaper_families",
        "probe_path_state",
        "probe_unavailable_reason",
        "probe_result_class",
        "verification_state",
        "explainability_profile",
        "anti_thrash",
        "scores",
        "mediation",
    )
    assert payload["alpha_t"] == pytest.approx(expected_alpha)
    assert payload["activation_threshold"] == pytest.approx(activation_threshold)
    assert isinstance(payload["selected_delta_over_neutral"], float)
    assert isinstance(payload["chi_t"], float)
    assert isinstance(payload["rejected_cheaper_families"], list)
    assert all(
        isinstance(family, str) and family
        for family in payload["rejected_cheaper_families"]
    )
    assert payload["probe_path_state"] == expected_probe_path_state
    assert payload["probe_unavailable_reason"] == expected_probe_unavailable_reason
    probe_result_class = payload["probe_result_class"]
    assert probe_result_class is None or (
        isinstance(probe_result_class, str) and probe_result_class
    )
    assert isinstance(payload["verification_state"], str)
    assert payload["verification_state"]
    assert payload["explainability_profile"] in {"minimal", "focused", "structured"}
    assert payload["anti_thrash"] == {
        "state": "inactive",
        "target_family": None,
        "repetition_tax": 0.0,
        "reason_tags": [],
    }
    scores = payload["scores"]
    assert isinstance(scores, list)
    assert [score["family"] for score in scores] == [
        "neutral",
        "seek-context",
        "redirect",
        "check",
        "branch",
        "escalate",
        "brake",
    ]
    assert all(score["memory_score"] == 0.0 for score in scores)
    if expect_allocated_equals_online:
        assert all(score["allocated_score"] == score["online_score"] for score in scores)
    else:
        assert any(score["allocated_score"] != score["online_score"] for score in scores)
    for score in scores:
        assert isinstance(score["activation_threshold"], float)
        reason_tags = score["reason_tags"]
        assert isinstance(reason_tags, list)
        if "goal-branch-coupled" in reason_tags:
            assert "allocation:online-plus-goal-branch" in reason_tags
            assert "allocation:online-only" not in reason_tags
            assert any(tag.startswith("lambda_G:") for tag in reason_tags)
        if any(tag.startswith("lambda_G:") for tag in reason_tags):
            assert "allocation:online-plus-goal-branch" in reason_tags
            assert "allocation:online-only" not in reason_tags
    mediation = payload["mediation"]
    assert isinstance(mediation, dict)
    assert tuple(mediation) == (
        "mediation_active",
        "mediation_identity",
        "selected_family_before_finalization",
        "selected_family_after_finalization",
        "preferred_opportunity_ref",
        "direct_opportunity_specialization_used",
        "mediation_reason_tags",
    )
    assert mediation["mediation_active"] is expected_mediation["mediation_active"]
    assert mediation["mediation_identity"] is expected_mediation["mediation_identity"]
    assert (
        mediation["selected_family_before_finalization"]
        == expected_mediation["selected_family_before_finalization"]
    )
    assert (
        mediation["selected_family_after_finalization"]
        == expected_mediation["selected_family_after_finalization"]
    )
    assert mediation["preferred_opportunity_ref"] == expected_mediation["preferred_opportunity_ref"]
    assert (
        mediation["direct_opportunity_specialization_used"]
        is expected_mediation["direct_opportunity_specialization_used"]
    )
    assert isinstance(mediation["mediation_reason_tags"], list)


def _feedback(warning_code: str) -> ReferenceRealizationFeedback:
    warning_codes = (warning_code,) if warning_code else ()
    return ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.NEUTRAL,
        realized_family=SoftControlFamily.NEUTRAL,
        brake_state=BrakeState.QUIESCENT,
        warning_codes=warning_codes,
    )


def _reference_replay_scenario(scenario_id: str):
    for scenario in make_aux_reference_replay_corpus():
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"Unknown replay scenario {scenario_id!r}.")


def _reference_replay_case_result(scenario_id: str):
    scenario = _reference_replay_scenario(scenario_id)
    return evaluate_aux_reference_q_mem_replay((scenario,)).case_results[0]


def _scenario_executive_state_with_task_mode(
    scenario,
    task_mode: OperatorTaskMode,
) -> ReferenceExecutiveState:
    return replace(
        scenario.executive_state,
        mode_and_gating=replace(
            scenario.executive_state.mode_and_gating,
            task_mode=task_mode,
        ),
    )


def _score_payload_for_family(
    scores: list[dict[str, object]],
    family: str,
) -> dict[str, object]:
    for score in scores:
        if score["family"] == family:
            return score
    raise KeyError(f"Missing score payload for family {family!r}.")


def _latched_state_with_evidence(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="review-track"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="evidence", level=0.95),
                UncertaintyEstimate(class_tag="environment", level=0.75),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
                UncertaintyEstimate(class_tag="goal-progress", level=0.4),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            task_mode=_task_mode_from_kwargs(kwargs),
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
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )


def _latched_state_without_evidence(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="host-capability", level=0.9),
                UncertaintyEstimate(class_tag="goal-progress", level=0.8),
                UncertaintyEstimate(class_tag="environment", level=0.2),
                UncertaintyEstimate(class_tag="evidence", level=0.1),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            task_mode=_task_mode_from_kwargs(kwargs),
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRAKE,
                }
            ),
            host_friction_tags=frozenset({"single-process-limit"}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )


def _latched_state_with_host_capability_gap(
    *args: object,
    **kwargs: object,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="host-capability", level=0.92),
                UncertaintyEstimate(class_tag="environment", level=0.74),
                UncertaintyEstimate(class_tag="goal-progress", level=0.35),
                UncertaintyEstimate(class_tag="evidence", level=0.10),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            task_mode=_task_mode_from_kwargs(kwargs),
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.SEEK_CONTEXT,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.SEEK_CONTEXT,
                    SoftControlFamily.BRAKE,
                }
            ),
            host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )


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
            task_mode=_task_mode_from_kwargs(kwargs),
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


def _state_with_ordered_family_mask(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="environment", level=0.6),
                UncertaintyEstimate(class_tag="goal-progress", level=0.4),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="ordered_mask",
            task_mode=_task_mode_from_kwargs(kwargs),
            family_mask=frozenset(
                {
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.REDIRECT,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
    )


def _state_with_tied_uncertainty_sources(
    *args: object,
    **kwargs: object,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="goal-progress", level=0.8),
                UncertaintyEstimate(class_tag="environment", level=0.8),
                UncertaintyEstimate(class_tag="evidence", level=0.8),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="tied_sources",
            task_mode=_task_mode_from_kwargs(kwargs),
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
    )


def _task_mode_from_kwargs(kwargs: dict[str, object]) -> OperatorTaskMode:
    task_mode = kwargs.get("task_mode", OperatorTaskMode.EXECUTE)
    assert isinstance(task_mode, OperatorTaskMode)
    return task_mode
