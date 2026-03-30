"""Mechanical SRE-scoped drift checks for landed correspondence rows."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PromisedTestSurface:
    test_file: str
    test_names: tuple[str, ...]


@dataclass(frozen=True)
class SreCorrespondenceExpectation:
    row_label: str
    module_path: str
    symbol_name: str
    promised_surfaces: tuple[PromisedTestSurface, ...]


EXPECTATIONS = (
    SreCorrespondenceExpectation(
        row_label="ReferenceExecutiveState",
        module_path="cortex.sre.state",
        symbol_name="ReferenceExecutiveState",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_reference_executive_state_exposes_minimum_software_facing_views",
                    "test_reference_executive_state_uses_canonical_uncertainty_and_brake_types",
                    "test_reference_state_surface_does_not_export_duplicate_uncertainty_carrier",
                ),
            ),
            PromisedTestSurface(
                test_file="tests/unit/test_sre_goals_branching.py",
                test_names=(
                    "test_reference_executive_state_uses_canonical_goal_carrier_directly",
                    "test_reference_state_surface_keeps_only_a_compatibility_alias_for_goal_view",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="ReferenceModeAndGatingView",
        module_path="cortex.sre.state",
        symbol_name="ReferenceModeAndGatingView",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_reference_executive_state_exposes_minimum_software_facing_views",
                    "test_reference_mode_and_gating_view_requires_non_empty_mode_tag",
                    "test_reference_mode_and_gating_view_requires_typed_family_mask",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="ReferenceControlAllocationView",
        module_path="cortex.sre.state",
        symbol_name="ReferenceControlAllocationView",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_reference_executive_state_exposes_minimum_software_facing_views",
                    "test_reference_control_allocation_view_requires_non_empty_budget_band",
                    "test_reference_control_allocation_view_requires_typed_top_family_set",
                    "test_reference_control_allocation_view_requires_non_empty_host_friction_tags",
                    "test_reference_control_allocation_view_requires_non_empty_feedback_pressure_tags",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="build_reference_executive_state",
        module_path="cortex.sre.reference_builder",
        symbol_name="build_reference_executive_state",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_reference_executive_builder.py",
                test_names=(
                    "test_build_reference_executive_state_for_cheap_event_stays_pass_through_and_low_budget",
                    "test_build_reference_executive_state_for_candidate_bearing_event_surfaces_review_mode",
                    "test_build_reference_executive_state_for_full_commitment_event_preserves_high_budget_band",
                    "test_build_reference_executive_state_surfaces_guarded_brake_when_snapshot_has_degradation",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="SoftControlFamily",
        module_path="cortex.sre.families",
        symbol_name="SoftControlFamily",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=("test_exact_soft_control_family_set_matches_the_packet",),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="AllocationScore",
        module_path="cortex.sre.allocation",
        symbol_name="AllocationScore",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_neutral_dominance_returns_neutral_when_margin_is_below_threshold",
                    "test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met",
                    "test_allocation_score_defaults_online_and_allocated_to_score",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="AllocationScorecard",
        module_path="cortex.sre.allocation",
        symbol_name="AllocationScorecard",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_neutral_dominance_returns_neutral_when_margin_is_below_threshold",
                    "test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met",
                    "test_allocation_scorecard_requires_alpha_in_unit_interval",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="build_reference_allocation_scorecard",
        module_path="cortex.sre.reference_scoring",
        symbol_name="build_reference_allocation_scorecard",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_reference_runtime_scoring.py",
                test_names=(
                    "test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold",
                    "test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked",
                    "test_reference_scoring_exposes_explicit_online_allocation_diagnostics",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="neutral_dominance_decision",
        module_path="cortex.sre.policy",
        symbol_name="neutral_dominance_decision",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_neutral_hinge.py",
                test_names=(
                    "test_neutral_dominance_returns_neutral_when_margin_is_below_threshold",
                    "test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met",
                    "test_neutral_path_law_rejects_scorecards_that_omit_neutral",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="ReferenceSoftControlSelection",
        module_path="cortex.sre.reference_scoring",
        symbol_name="ReferenceSoftControlSelection",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_reference_runtime_scoring.py",
                test_names=(
                    "test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold",
                    "test_reference_scoring_tightens_to_neutral_when_guarded_pressure_is_present",
                    "test_reference_scoring_promotes_branch_under_branch_pressure",
                    "test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="select_reference_soft_control",
        module_path="cortex.sre.reference_scoring",
        symbol_name="select_reference_soft_control",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_reference_runtime_scoring.py",
                test_names=(
                    "test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold",
                    "test_reference_scoring_tightens_to_neutral_when_guarded_pressure_is_present",
                    "test_reference_scoring_promotes_branch_under_branch_pressure",
                    "test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="UncertaintyEstimate",
        module_path="cortex.sre.uncertainty",
        symbol_name="UncertaintyEstimate",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_uncertainty_brake.py",
                test_names=(
                    "test_uncertainty_estimate_accepts_packet_class_tags_and_rejects_unknown_classes",
                    "test_uncertainty_estimate_enforces_bounded_values",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="BrakeState",
        module_path="cortex.sre.brake",
        symbol_name="BrakeState",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_uncertainty_brake.py",
                test_names=("test_brake_state_set_is_exact",),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="evaluate_brake_state",
        module_path="cortex.sre.brake",
        symbol_name="evaluate_brake_state",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_uncertainty_brake.py",
                test_names=(
                    "test_brake_evaluation_returns_quiescent_for_low_uncertainty_without_spikes",
                    "test_brake_evaluation_returns_guarded_for_elevated_uncertainty_or_mild_spike_pressure",
                    "test_brake_evaluation_returns_latched_for_strong_spike_or_failure_pressure",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="GoalContinuityView",
        module_path="cortex.sre.goals",
        symbol_name="GoalContinuityView",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_goals_branching.py",
                test_names=("test_goal_continuity_view_preserves_goal_and_pending_goal_fields",),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="BranchOperation",
        module_path="cortex.sre.branching",
        symbol_name="BranchOperation",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_goals_branching.py",
                test_names=("test_branch_operation_set_is_exact",),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="HostNativeOpportunity",
        module_path="cortex.sre.opportunities",
        symbol_name="HostNativeOpportunity",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_opportunities.py",
                test_names=(
                    "test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior",
                    "test_failed_specialization_surfaces_degradation_reason_and_safer_fallback",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="OpportunitySpecializationResult",
        module_path="cortex.sre.opportunities",
        symbol_name="OpportunitySpecializationResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_opportunities.py",
                test_names=(
                    "test_neutral_family_returns_no_direct_opportunity_specialization",
                    "test_failed_specialization_surfaces_degradation_reason_and_safer_fallback",
                    "test_selected_family_remains_distinct_from_direct_opportunity",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="specialize_host_native_opportunity",
        module_path="cortex.sre.opportunities",
        symbol_name="specialize_host_native_opportunity",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_sre_opportunities.py",
                test_names=(
                    "test_neutral_family_returns_no_direct_opportunity_specialization",
                    "test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior",
                    "test_family_is_retained_when_no_clearly_superior_opportunity_exists",
                    "test_failed_specialization_surfaces_degradation_reason_and_safer_fallback",
                    "test_selected_family_remains_distinct_from_direct_opportunity",
                ),
            ),
        ),
    ),
    SreCorrespondenceExpectation(
        row_label="select_operator_route",
        module_path="cortex.sre.operator_routing",
        symbol_name="select_operator_route",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_operator_routing.py",
                test_names=(
                    "test_operator_task_state_requires_bounded_numeric_axes",
                    "test_select_operator_route_prefers_default_execute_under_low_pressure",
                    "test_select_operator_route_can_choose_guarded_execute_under_higher_pressure",
                    "test_select_operator_route_prefers_guarded_continuity_for_resumptive_host_friction",
                    "test_select_operator_route_blocks_non_inspect_when_quota_is_high",
                    "test_build_operator_route_diagnostics_exposes_state_and_budget",
                ),
            ),
        ),
    ),
)


def _module_home(module_path: str) -> Path:
    return REPO_ROOT.joinpath(*module_path.split(".")).with_suffix(".py")


@pytest.mark.parametrize("expectation", EXPECTATIONS, ids=lambda item: item.row_label)
def test_sre_correspondence_registry_resolves_code_home_and_test_surface(
    expectation: SreCorrespondenceExpectation,
) -> None:
    module_home = _module_home(expectation.module_path)
    assert module_home.is_file(), (
        f"{expectation.row_label}: expected module home {module_home.relative_to(REPO_ROOT)}"
    )

    module = importlib.import_module(expectation.module_path)
    assert hasattr(module, expectation.symbol_name), (
        f"{expectation.row_label}: missing symbol {expectation.symbol_name} "
        f"in module {expectation.module_path}"
    )

    for promised_surface in expectation.promised_surfaces:
        test_file = REPO_ROOT / promised_surface.test_file
        assert test_file.is_file(), (
            f"{expectation.row_label}: expected promised test file {promised_surface.test_file}"
        )

        test_text = test_file.read_text(encoding="utf-8")
        for test_name in promised_surface.test_names:
            assert f"def {test_name}(" in test_text, (
                f"{expectation.row_label}: missing promised test function {test_name} "
                f"in {promised_surface.test_file}"
            )
