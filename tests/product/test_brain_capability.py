"""Focused tests for the operator brain-capability registry and envelope."""

from __future__ import annotations

import pytest

from cortex.runtime.operator_brain_capability import (
    OperatorBrainCapabilityBand,
    brain_capability_band_for_envelope,
    operator_brain_capability_band_for_openai_model,
    operator_brain_capability_for_band,
    operator_brain_capability_for_openai_model,
)
from cortex.sre.operator_routing import (
    OperatorBrainCapabilityAssessment,
    OperatorBrainCapabilityEnvelope,
    OperatorBrainCapabilityMismatchLevel,
    OperatorContractBindingProfile,
    OperatorRouteProfile,
    OperatorTaskMode,
    OperatorTaskState,
    assess_operator_brain_capability,
    select_operator_route,
)


# ---------------------------------------------------------------------------
# OperatorBrainCapabilityEnvelope: field validation
# ---------------------------------------------------------------------------


def test_envelope_requires_three_unit_interval_fields() -> None:
    envelope = OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.5,
        verification_tolerance=0.6,
        output_contract_tolerance=0.7,
    )

    assert envelope.as_payload() == {
        "continuity_tolerance": 0.5,
        "verification_tolerance": 0.6,
        "output_contract_tolerance": 0.7,
    }


@pytest.mark.parametrize(
    "field_name, bad_value",
    [
        ("continuity_tolerance", -0.01),
        ("continuity_tolerance", 1.01),
        ("verification_tolerance", -0.01),
        ("verification_tolerance", 1.01),
        ("output_contract_tolerance", -0.01),
        ("output_contract_tolerance", 1.01),
    ],
)
def test_envelope_rejects_out_of_range_fields(field_name: str, bad_value: float) -> None:
    kwargs = {
        "continuity_tolerance": 0.5,
        "verification_tolerance": 0.5,
        "output_contract_tolerance": 0.5,
    }
    kwargs[field_name] = bad_value
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        OperatorBrainCapabilityEnvelope(**kwargs)


def test_envelope_rejects_non_numeric_fields() -> None:
    with pytest.raises(TypeError, match="numeric"):
        OperatorBrainCapabilityEnvelope(
            continuity_tolerance="0.5",  # type: ignore[arg-type]
            verification_tolerance=0.5,
            output_contract_tolerance=0.5,
        )


# ---------------------------------------------------------------------------
# Registry: band-to-envelope and OpenAI-model-to-band lookup
# ---------------------------------------------------------------------------


def test_registry_returns_distinct_envelopes_for_each_band() -> None:
    frontier = operator_brain_capability_for_band("frontier")
    standard = operator_brain_capability_for_band("standard")
    bounded = operator_brain_capability_for_band("bounded")

    # Each band must be a distinct envelope; the bounded band must have
    # strictly lower tolerances than standard, which must have strictly lower
    # tolerances than frontier across every dimension.
    for dimension in (
        "continuity_tolerance",
        "verification_tolerance",
        "output_contract_tolerance",
    ):
        frontier_value = getattr(frontier, dimension)
        standard_value = getattr(standard, dimension)
        bounded_value = getattr(bounded, dimension)
        assert frontier_value > standard_value > bounded_value


def test_registry_rejects_unknown_band() -> None:
    with pytest.raises(ValueError, match="unsupported operator brain capability band"):
        operator_brain_capability_for_band("genius")  # type: ignore[arg-type]


def test_openai_model_lookup_returns_known_bands() -> None:
    assert operator_brain_capability_band_for_openai_model("gpt-5.4") == "frontier"
    assert (
        operator_brain_capability_band_for_openai_model("gpt-5.3-codex") == "standard"
    )
    assert (
        operator_brain_capability_band_for_openai_model("gpt-5.3-codex-spark")
        == "bounded"
    )


@pytest.mark.parametrize("unknown_input", ["", "   ", None, "gpt-99-fictitious"])
def test_openai_model_lookup_falls_through_to_standard(unknown_input: str | None) -> None:
    # Unknown / empty / None model names must default to standard rather than
    # raising; cold-start and forward-compat both depend on this.
    band = operator_brain_capability_band_for_openai_model(unknown_input)
    assert band == "standard"


def test_openai_model_lookup_returns_envelope_pair() -> None:
    band, envelope = operator_brain_capability_for_openai_model("gpt-5.3-codex-spark")
    assert band == "bounded"
    assert envelope == operator_brain_capability_for_band("bounded")


def test_envelope_to_band_round_trip() -> None:
    for band in ("frontier", "standard", "bounded"):
        envelope = operator_brain_capability_for_band(band)
        assert brain_capability_band_for_envelope(envelope) == band


def test_envelope_to_band_returns_standard_for_custom_envelope() -> None:
    custom = OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.55,
        verification_tolerance=0.55,
        output_contract_tolerance=0.55,
    )
    # A custom envelope that does not exactly match any registered band must
    # fall through to standard rather than raising; this preserves cold-start.
    assert brain_capability_band_for_envelope(custom) == "standard"


def test_envelope_to_band_rejects_non_envelope() -> None:
    with pytest.raises(TypeError, match="OperatorBrainCapabilityEnvelope"):
        brain_capability_band_for_envelope("frontier")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# assess_operator_brain_capability: threshold ladder boundaries
# ---------------------------------------------------------------------------


def _state_with_demands(
    *,
    continuity_demand: float,
    verification_demand: float,
    contract_binding_demand: float,
    band: OperatorBrainCapabilityBand = "standard",
) -> OperatorTaskState:
    return OperatorTaskState(
        task_mode=OperatorTaskMode.EXECUTE,
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


def test_assessment_is_none_when_demand_well_below_tolerance() -> None:
    # Standard band tolerances: continuity 0.75, verification 0.75, contract 0.65.
    # All demands well below tolerance → mismatch ~ 0 → NONE.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.5,
            verification_demand=0.5,
            contract_binding_demand=0.4,
        )
    )
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.NONE
    assert assessment.contract_binding_profile is OperatorContractBindingProfile.STANDARD
    assert assessment.fallback_family is None


def test_assessment_is_none_at_zero_mismatch_boundary() -> None:
    # demand exactly equal to tolerance → mismatch == 0 → still NONE.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.75,
            verification_demand=0.75,
            contract_binding_demand=0.65,
        )
    )
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.NONE


def test_assessment_is_none_just_below_degrade_threshold() -> None:
    # max mismatch 0.19 → still under the 0.20 threshold → NONE.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.94,
            verification_demand=0.5,
            contract_binding_demand=0.4,
        )
    )
    assert assessment.continuity_mismatch == pytest.approx(0.19)
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.NONE


def test_assessment_degrades_at_threshold() -> None:
    # max mismatch >= 0.20 but < 0.50 → DEGRADE → LEAN contract binding.
    # Use 0.96 to clear the 0.20 threshold accounting for float precision.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.96,
            verification_demand=0.5,
            contract_binding_demand=0.4,
        )
    )
    assert assessment.continuity_mismatch == pytest.approx(0.21)
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.DEGRADE
    assert assessment.contract_binding_profile is OperatorContractBindingProfile.LEAN


def test_assessment_degrades_just_below_unsupported_threshold() -> None:
    # max mismatch 0.49 → still DEGRADE.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.5,
            verification_demand=0.5,
            contract_binding_demand=1.0,
            band="bounded",
        )
    )
    # bounded contract tolerance is 0.20; demand 1.0 → mismatch 0.80 → UNSUPPORTED.
    # Use a different demand for a precise DEGRADE-not-UNSUPPORTED case.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.5,
            verification_demand=0.5,
            contract_binding_demand=0.69,
            band="bounded",
        )
    )
    # bounded contract tolerance 0.20; demand 0.69 → mismatch 0.49 → DEGRADE.
    assert assessment.contract_mismatch == pytest.approx(0.49)
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.DEGRADE


def test_assessment_is_unsupported_at_threshold() -> None:
    # max mismatch >= 0.50 → UNSUPPORTED with fallback_family populated.
    # Use 0.71 to clear the 0.50 threshold accounting for float precision.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.5,
            verification_demand=0.5,
            contract_binding_demand=0.71,
            band="bounded",
        )
    )
    # bounded contract tolerance 0.20; demand 0.71 → mismatch 0.51 → UNSUPPORTED.
    assert assessment.contract_mismatch == pytest.approx(0.51)
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    assert assessment.fallback_family is not None
    assert "brain-capability:unsupported-floor" in assessment.reason_tags


def test_assessment_picks_max_dimension_for_threshold() -> None:
    # Mismatch is the per-dimension maximum, not a sum or average.
    # Use 0.96/0.96/0.86 to clear 0.20 threshold for each dimension under float precision.
    assessment = assess_operator_brain_capability(
        _state_with_demands(
            continuity_demand=0.96,  # mismatch 0.21 vs standard 0.75
            verification_demand=0.96,  # mismatch 0.21 vs standard 0.75
            contract_binding_demand=0.86,  # mismatch 0.21 vs standard 0.65
        )
    )
    # Three equal mismatches at 0.21 → DEGRADE, not UNSUPPORTED.
    assert assessment.level is OperatorBrainCapabilityMismatchLevel.DEGRADE


def test_assessment_rejects_non_state() -> None:
    with pytest.raises(TypeError, match="OperatorTaskState"):
        assess_operator_brain_capability("not-a-state")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Routing consequences: assessment actually changes routing, not just diagnostics
# ---------------------------------------------------------------------------


def test_unsupported_capability_routes_to_blocked() -> None:
    state = _state_with_demands(
        continuity_demand=0.5,
        verification_demand=0.5,
        contract_binding_demand=0.95,
        band="bounded",
    )
    decision = select_operator_route(state)
    # UNSUPPORTED capability must produce a BLOCKED route.
    assert decision.profile is OperatorRouteProfile.BLOCKED
    assert decision.blocked_reason == "brain_capability_mismatch"


def test_frontier_capability_does_not_degrade_routing() -> None:
    state = _state_with_demands(
        continuity_demand=0.85,
        verification_demand=0.85,
        contract_binding_demand=0.85,
        band="frontier",
    )
    # Frontier band tolerances are 0.90; demand 0.85 → mismatch 0.0 → NONE.
    decision = select_operator_route(state)
    assert (
        decision.brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.NONE
    )
    assert decision.profile is not OperatorRouteProfile.BLOCKED


def test_assessment_payload_shape_is_stable() -> None:
    # Diagnostics consumers depend on a locked payload key set; this guards
    # against silent shape drift.
    assessment = OperatorBrainCapabilityAssessment(
        continuity_mismatch=0.10,
        verification_mismatch=0.20,
        contract_mismatch=0.30,
        level=OperatorBrainCapabilityMismatchLevel.DEGRADE,
        contract_binding_profile=OperatorContractBindingProfile.LEAN,
    )
    payload = assessment.as_payload()
    assert set(payload) == {
        "continuity",
        "verification",
        "contract_binding",
        "level",
        "fallback_family",
    }
    assert payload["level"] == "degrade"
