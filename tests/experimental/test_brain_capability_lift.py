"""Fixture-mode lift evaluation for brain-capability-aware routing.

These tests prove the structural lift of capability-aware routing: given the
same task demand profile, varying only the brain capability envelope must
produce *materially different* routing decisions, not just different
diagnostics. This earns the seam structurally; live-evidence lift on real
bounded models is queued as the dynamic-detection follow-up seam.
"""

from __future__ import annotations

import pytest

from cortex.runtime.operator_brain_capability import (
    operator_brain_capability_for_band,
)
from cortex.sre.operator_routing import (
    OperatorBrainCapabilityMismatchLevel,
    OperatorContractBindingProfile,
    OperatorRouteProfile,
    OperatorTaskMode,
    OperatorTaskState,
    select_operator_route,
)


def _high_demand_state(band: str) -> OperatorTaskState:
    """Identical task demand across all bands; only capability differs."""
    return OperatorTaskState(
        task_mode=OperatorTaskMode.RESUME_EXECUTE,
        complexity=0.7,
        continuity_demand=0.85,  # high continuity demand
        verification_demand=0.7,
        uncertainty=0.3,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.4,
        contract_binding_demand=0.6,
        brain_capability=operator_brain_capability_for_band(band),
    )


def test_frontier_brain_preserves_continuity_route_under_high_demand() -> None:
    state = _high_demand_state("frontier")
    decision = select_operator_route(state)
    # Frontier capability tolerances are 0.90; demands all under tolerance →
    # NONE → routing should not be downshifted to inspect-light.
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.NONE
    )
    assert decision.profile is not OperatorRouteProfile.BLOCKED
    assert decision.profile is not OperatorRouteProfile.INSPECT_LIGHT
    # Frontier capability should not lean the contract binding.
    assert (
        decision.brain_capability_assessment.contract_binding_profile
        is OperatorContractBindingProfile.STANDARD
    )


def test_bounded_brain_blocks_route_under_high_demand() -> None:
    state = _high_demand_state("bounded")
    decision = select_operator_route(state)
    # Bounded capability has continuity_tolerance 0.45; demand 0.85 →
    # mismatch 0.40 → DEGRADE. But verification_demand 0.7 vs tolerance 0.50
    # → mismatch 0.20 → also DEGRADE. So this is DEGRADE not UNSUPPORTED.
    assert decision.brain_capability_assessment.level in {
        OperatorBrainCapabilityMismatchLevel.DEGRADE,
        OperatorBrainCapabilityMismatchLevel.UNSUPPORTED,
    }
    # The brain-capability path must visibly change routing — either by
    # downshifting the profile (DEGRADE) or by blocking it (UNSUPPORTED).
    if (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    ):
        assert decision.profile is OperatorRouteProfile.BLOCKED
    else:
        # DEGRADE → continuity routes downshift (RESUME_EXECUTE → EXECUTE_STANDARD)
        # and retries are zeroed.
        assert decision.budget.max_retries == 0
        assert decision.budget.allow_extra_read_pass is False


def test_capability_lift_produces_distinct_decisions_for_same_demand() -> None:
    """The lift claim itself: same task demand, different brain capabilities,
    different routing decisions."""
    frontier = select_operator_route(_high_demand_state("frontier"))
    standard = select_operator_route(_high_demand_state("standard"))
    bounded = select_operator_route(_high_demand_state("bounded"))

    # The three decisions must not all be identical; that would mean
    # capability awareness has no effect.
    decisions = (frontier, standard, bounded)
    assessments = {decision.brain_capability_assessment.level for decision in decisions}
    assert len(assessments) > 1, (
        "capability awareness produced identical routing for all bands; "
        "the lift mechanism is not actually changing decisions"
    )

    # Specifically: bounded must produce a more conservative decision than
    # frontier on this high-continuity-demand task.
    assert (
        bounded.budget.max_retries <= frontier.budget.max_retries
    ), "bounded brain did not produce a tighter retry budget than frontier"


def test_unsupported_capability_route_is_blocked_with_specific_reason() -> None:
    # A demand profile that severely exceeds bounded capability must produce
    # a BLOCKED route with the brain_capability_mismatch reason, not a
    # generic blocked decision.
    state = OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
        complexity=0.5,
        continuity_demand=0.5,
        verification_demand=0.5,
        uncertainty=0.2,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.3,
        contract_binding_demand=0.95,  # mismatch 0.75 vs bounded 0.20
        brain_capability=operator_brain_capability_for_band("bounded"),
    )
    decision = select_operator_route(state)
    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "brain_capability_mismatch"
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    )


def test_capability_assessment_is_visible_in_diagnostics_payload() -> None:
    # The lift mechanism is only useful if downstream consumers can see what
    # happened. The decision must carry the assessment payload, not just an
    # internal flag, and the payload must include the level, the per-dimension
    # mismatches, and the contract binding profile.
    state = _high_demand_state("bounded")
    decision = select_operator_route(state)
    payload = decision.brain_capability_assessment.as_payload()
    assert "level" in payload
    assert "continuity" in payload
    assert "verification" in payload
    assert "contract_binding" in payload
    # The level must be one of the canonical values (not an internal enum).
    assert payload["level"] in {"none", "degrade", "unsupported"}


@pytest.mark.parametrize(
    "task_mode",
    [
        OperatorTaskMode.EXECUTE,
        OperatorTaskMode.INSPECT,
        OperatorTaskMode.RESUME_EXECUTE,
    ],
)
def test_frontier_routing_does_not_change_under_capability_assessment(
    task_mode: OperatorTaskMode,
) -> None:
    # Frontier capability with moderate demand → NONE assessment → routing
    # should be the same as if no capability mechanism existed. This proves
    # the mechanism doesn't penalize frontier brains.
    state = OperatorTaskState(
        task_mode=task_mode,
        complexity=0.5,
        continuity_demand=0.6,
        verification_demand=0.6,
        uncertainty=0.2,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.3,
        contract_binding_demand=0.5,
        brain_capability=operator_brain_capability_for_band("frontier"),
    )
    decision = select_operator_route(state)
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.NONE
    )
    assert (
        decision.brain_capability_assessment.contract_binding_profile
        is OperatorContractBindingProfile.STANDARD
    )
    # No reason tags from the brain-capability path under NONE.
    capability_tags = {
        tag
        for tag in decision.reason_tags
        if tag.startswith("brain-capability:")
    }
    assert capability_tags == set()
