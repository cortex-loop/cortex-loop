"""Focused unit tests for SRE uncertainty and brake."""

from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.uncertainty import REFERENCE_UNCERTAINTY_CLASSES, UncertaintyEstimate


def test_uncertainty_estimate_accepts_packet_class_tags_and_rejects_unknown_classes() -> None:
    assert REFERENCE_UNCERTAINTY_CLASSES == frozenset(
        {
            "evidence",
            "environment",
            "host-capability",
            "goal-progress",
        }
    )
    estimate = UncertaintyEstimate(class_tag="evidence", level=0.25)

    assert estimate.class_tag == "evidence"
    assert estimate.level == 0.25

    try:
        UncertaintyEstimate(class_tag="unknown-class", level=0.25)
    except ValueError as exc:
        assert "Unknown uncertainty class" in str(exc)
    else:
        raise AssertionError("UncertaintyEstimate accepted an unknown class tag.")


def test_uncertainty_estimate_enforces_bounded_values() -> None:
    try:
        UncertaintyEstimate(class_tag="environment", level=1.1)
    except ValueError as exc:
        assert "between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError("UncertaintyEstimate accepted an out-of-range value.")


def test_uncertainty_estimate_requires_numeric_level() -> None:
    estimate = UncertaintyEstimate(class_tag="evidence", level=0.25)

    assert estimate.level == 0.25

    try:
        UncertaintyEstimate(class_tag="evidence", level="0.25")
    except TypeError as exc:
        assert "level must be a numeric value between 0.0 and 1.0" in str(exc)
    else:
        raise AssertionError("UncertaintyEstimate accepted a non-numeric level.")


def test_uncertainty_estimate_requires_non_empty_source_tags() -> None:
    estimate = UncertaintyEstimate(
        class_tag="evidence",
        level=0.25,
        source_tags=frozenset({"runtime-record"}),
    )

    assert estimate.source_tags == frozenset({"runtime-record"})

    try:
        UncertaintyEstimate(
            class_tag="evidence",
            level=0.25,
            source_tags=frozenset({"   "}),
        )
    except ValueError as exc:
        assert "source_tags must contain only non-empty values after trimming" in str(exc)
    else:
        raise AssertionError("UncertaintyEstimate accepted a blank source tag.")


def test_uncertainty_estimate_requires_non_empty_spike_tags() -> None:
    estimate = UncertaintyEstimate(
        class_tag="environment",
        level=0.6,
        spike_tags=frozenset({"environment-inconsistency"}),
    )

    assert estimate.spike_tags == frozenset({"environment-inconsistency"})

    try:
        UncertaintyEstimate(
            class_tag="environment",
            level=0.6,
            spike_tags=frozenset({"   "}),
        )
    except ValueError as exc:
        assert "spike_tags must contain only non-empty values after trimming" in str(exc)
    else:
        raise AssertionError("UncertaintyEstimate accepted a blank spike tag.")


def test_brake_state_set_is_exact() -> None:
    assert {state.value for state in BrakeState} == {
        "quiescent",
        "guarded",
        "latched",
    }


def test_brake_evaluation_returns_quiescent_for_low_uncertainty_without_spikes() -> None:
    evaluation = evaluate_brake_state(
        (
            UncertaintyEstimate(class_tag="evidence", level=0.15),
            UncertaintyEstimate(class_tag="goal-progress", level=0.2),
        )
    )

    assert evaluation.state is BrakeState.QUIESCENT
    assert evaluation.dominant_cause is None
    assert evaluation.spike_tags == frozenset()


def test_brake_evaluation_returns_guarded_for_elevated_uncertainty_or_mild_spike_pressure() -> None:
    evaluation = evaluate_brake_state(
        (
            UncertaintyEstimate(
                class_tag="host-capability",
                level=0.6,
                spike_tags=frozenset({"goal-progress-ambiguity"}),
            ),
        )
    )

    assert evaluation.state is BrakeState.GUARDED
    assert evaluation.dominant_cause == "goal-progress-ambiguity"
    assert evaluation.spike_tags == frozenset({"goal-progress-ambiguity"})


def test_brake_evaluation_reports_repeated_failure_as_guarded_dominant_cause() -> None:
    evaluation = evaluate_brake_state((), repeated_failures=1)

    assert evaluation.state is BrakeState.GUARDED
    assert evaluation.dominant_cause == "repeated-failure"


def test_brake_evaluation_reports_repeated_degradation_as_guarded_dominant_cause() -> None:
    evaluation = evaluate_brake_state((), repeated_degradations=1)

    assert evaluation.state is BrakeState.GUARDED
    assert evaluation.dominant_cause == "repeated-degradation"


def test_brake_evaluation_returns_latched_for_strong_spike_or_failure_pressure() -> None:
    evaluation = evaluate_brake_state(
        (
            UncertaintyEstimate(
                class_tag="environment",
                level=0.9,
                spike_tags=frozenset({"environment-inconsistency"}),
            ),
        ),
        repeated_failures=2,
    )

    assert evaluation.state is BrakeState.LATCHED
    assert evaluation.dominant_cause == "environment-inconsistency"
    assert evaluation.spike_tags == frozenset({"environment-inconsistency"})
