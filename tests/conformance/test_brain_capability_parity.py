"""Cross-host parity for brain-capability assessment and routing.

The brain-capability mechanism is host-agnostic at the SRE layer. The same
``OperatorTaskState`` shape with the same ``brain_capability`` envelope must
produce the same ``OperatorRouteDecision`` regardless of which host emits the
state. Per-host model-name registries may differ (currently only OpenAI has
one), but the assessment math, the threshold ladder, and the routing
consequences must be identical across all four host lanes.

This is the AGENTS.md non-negotiable: "Do not introduce host-specific policy
forks to force donor coherence."
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
    assess_operator_brain_capability,
    select_operator_route,
)


def _state(
    *,
    band: str,
    continuity_demand: float,
    verification_demand: float,
    contract_binding_demand: float,
    task_mode: OperatorTaskMode = OperatorTaskMode.EXECUTE,
) -> OperatorTaskState:
    return OperatorTaskState(
        task_mode=task_mode,
        complexity=0.4,
        continuity_demand=continuity_demand,
        verification_demand=verification_demand,
        uncertainty=0.2,
        host_friction=0.0,
        quota_pressure=0.0,
        visible_burden_sensitivity=0.3,
        contract_binding_demand=contract_binding_demand,
        brain_capability=operator_brain_capability_for_band(band),
    )


def test_unsupported_capability_blocks_route_regardless_of_task_mode() -> None:
    # The capability assessment must be host-agnostic AND task-mode-agnostic
    # for the UNSUPPORTED case: any task mode with a severe brain-capability
    # mismatch must route to BLOCKED. This is the cross-host parity guarantee.
    for task_mode in (
        OperatorTaskMode.EXECUTE,
        OperatorTaskMode.INSPECT,
        OperatorTaskMode.RESUME_EXECUTE,
    ):
        state = _state(
            band="bounded",
            continuity_demand=0.5,
            verification_demand=0.5,
            contract_binding_demand=0.95,
            task_mode=task_mode,
        )
        decision = select_operator_route(state)
        assert decision.profile is OperatorRouteProfile.BLOCKED, (
            f"task_mode {task_mode} did not route to BLOCKED under UNSUPPORTED "
            f"capability; got {decision.profile}"
        )
        assert decision.blocked_reason == "brain_capability_mismatch"
        assert (
            decision.brain_capability_assessment.level
            is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
        )


def test_degrade_capability_suppresses_retries_regardless_of_band_origin() -> None:
    # Whether the bounded/standard envelope came from a name lookup or a
    # custom envelope, DEGRADE-level mismatch must zero out max_retries and
    # suppress allow_extra_read_pass identically.
    state = _state(
        band="bounded",
        continuity_demand=0.5,
        verification_demand=0.5,
        contract_binding_demand=0.55,  # mismatch 0.35 → DEGRADE
    )
    decision = select_operator_route(state)
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.DEGRADE
    )
    assert (
        decision.brain_capability_assessment.contract_binding_profile
        is OperatorContractBindingProfile.LEAN
    )
    # DEGRADE must zero the retry budget regardless of host.
    assert decision.budget.max_retries == 0
    assert decision.budget.allow_extra_read_pass is False


def test_assessment_payload_keys_are_locked_across_invocations() -> None:
    # The brain_capability_assessment payload shape is a wire contract
    # consumed by every host's diagnostics serializer. Locking the key set
    # prevents accidental drift on any one host runtime.
    state = _state(
        band="standard",
        continuity_demand=0.6,
        verification_demand=0.6,
        contract_binding_demand=0.5,
    )
    assessment = assess_operator_brain_capability(state)
    payload = assessment.as_payload()
    assert tuple(payload) == (
        "continuity",
        "verification",
        "contract_binding",
        "level",
        "fallback_family",
    )


def test_envelope_payload_keys_are_locked_across_invocations() -> None:
    # The brain_capability envelope payload shape is also a wire contract.
    envelope = operator_brain_capability_for_band("frontier")
    payload = envelope.as_payload()
    assert tuple(payload) == (
        "continuity_tolerance",
        "verification_tolerance",
        "output_contract_tolerance",
    )


@pytest.mark.parametrize(
    "band",
    ["frontier", "standard", "bounded"],
)
def test_routing_decision_carries_capability_assessment_for_all_bands(band: str) -> None:
    # Every routing decision (regardless of band) must carry a non-None
    # assessment so downstream consumers (host runtime serializers) never have
    # to handle an absent assessment.
    state = _state(
        band=band,
        continuity_demand=0.3,
        verification_demand=0.3,
        contract_binding_demand=0.1,
    )
    decision = select_operator_route(state)
    assert decision.brain_capability_assessment is not None


def test_assessment_is_host_independent_pure_function() -> None:
    # `assess_operator_brain_capability` is a pure function of OperatorTaskState.
    # Two semantically identical states must produce identical assessments;
    # this proves the assessment never inspects host-specific globals.
    state_a = _state(
        band="bounded",
        continuity_demand=0.7,
        verification_demand=0.5,
        contract_binding_demand=0.6,
    )
    state_b = _state(
        band="bounded",
        continuity_demand=0.7,
        verification_demand=0.5,
        contract_binding_demand=0.6,
    )
    assessment_a = assess_operator_brain_capability(state_a)
    assessment_b = assess_operator_brain_capability(state_b)
    assert assessment_a == assessment_b
