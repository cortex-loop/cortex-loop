"""Focused unit tests for SRE uncertainty and brake."""

import pytest

from cortex.sre.brake import BrakeEvaluation, BrakeState, BrakeTonic, evaluate_brake_state
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


def test_brake_evaluation_requires_typed_state() -> None:
    evaluation = BrakeEvaluation(state=BrakeState.GUARDED)

    assert evaluation.state is BrakeState.GUARDED

    try:
        BrakeEvaluation(state="guarded")
    except TypeError as exc:
        assert "BrakeEvaluation.state must be BrakeState" in str(exc)
    else:
        raise AssertionError("BrakeEvaluation accepted an untyped state.")


def test_brake_evaluation_requires_non_empty_dominant_cause_when_provided() -> None:
    evaluation = BrakeEvaluation(
        state=BrakeState.GUARDED,
        dominant_cause="repeated-failure",
    )

    assert evaluation.dominant_cause == "repeated-failure"

    try:
        BrakeEvaluation(
            state=BrakeState.GUARDED,
            dominant_cause="   ",
        )
    except ValueError as exc:
        assert "dominant_cause must be non-empty after trimming when provided" in str(exc)
    else:
        raise AssertionError("BrakeEvaluation accepted a blank dominant cause.")


def test_brake_evaluation_requires_non_empty_spike_tags() -> None:
    evaluation = BrakeEvaluation(
        state=BrakeState.GUARDED,
        spike_tags=frozenset({"environment-inconsistency"}),
    )

    assert evaluation.spike_tags == frozenset({"environment-inconsistency"})

    try:
        BrakeEvaluation(
            state=BrakeState.GUARDED,
            spike_tags=frozenset({"   "}),
        )
    except ValueError as exc:
        assert "spike_tags must contain only non-empty values after trimming" in str(exc)
    else:
        raise AssertionError("BrakeEvaluation accepted a blank spike tag.")


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


def test_brake_evaluation_requires_typed_uncertainty_estimates() -> None:
    evaluation = evaluate_brake_state(
        (UncertaintyEstimate(class_tag="evidence", level=0.15),)
    )

    assert evaluation.state is BrakeState.QUIESCENT

    try:
        evaluate_brake_state(("not-estimate",))
    except TypeError as exc:
        assert (
            "evaluate_brake_state.uncertainty_estimates must contain only "
            "UncertaintyEstimate instances"
        ) in str(exc)
    else:
        raise AssertionError("evaluate_brake_state accepted an untyped estimate entry.")


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


def test_brake_tonic_requires_bounded_values() -> None:
    # BrakeTonic carriers must keep pressure/quiescence inside [0, 1].
    for kwargs in (
        {"tonic_pressure": -0.01, "tonic_quiescence": 0.5},
        {"tonic_pressure": 1.01, "tonic_quiescence": 0.5},
        {"tonic_pressure": 0.5, "tonic_quiescence": -0.01},
        {"tonic_pressure": 0.5, "tonic_quiescence": 1.01},
    ):
        try:
            BrakeTonic(**kwargs)
        except ValueError as exc:
            assert "between 0.0 and 1.0" in str(exc)
        else:
            raise AssertionError(f"Expected ValueError for {kwargs!r}")


def test_brake_evaluation_carries_tonic_summary() -> None:
    # Tonic must surface on the evaluation as a bounded summary the host can thread.
    evaluation = evaluate_brake_state(
        (UncertaintyEstimate(class_tag="evidence", level=0.10),),
    )

    assert evaluation.tonic is not None
    assert 0.0 <= evaluation.tonic.tonic_pressure <= 1.0
    assert 0.0 <= evaluation.tonic.tonic_quiescence <= 1.0


def test_brake_tonic_single_noisy_tick_does_not_enter_guarded_from_quiescent() -> None:
    # SRE_2 §7.5 tonic gate: from an established quiescent tonic, one borderline
    # soft-pressure tick must not flip into guarded — the pressure EMA has to cross
    # the enter threshold first.
    quiescent_prior = BrakeTonic(tonic_pressure=0.0, tonic_quiescence=1.0)
    evaluation = evaluate_brake_state(
        (UncertaintyEstimate(class_tag="evidence", level=0.56),),
        prior_state=BrakeState.QUIESCENT,
        prior_tonic=quiescent_prior,
    )

    assert evaluation.state is BrakeState.QUIESCENT
    assert evaluation.tonic is not None
    # EMA with rho=0.60: next = 0.60*0.0 + 0.40*0.56 = 0.224 < 0.35 enter gate.
    assert evaluation.tonic.tonic_pressure < 0.35


def test_brake_tonic_sustained_pressure_eventually_enters_guarded() -> None:
    # Sustained soft pressure (without spikes) should clear the tonic enter gate.
    tonic: BrakeTonic | None = None
    state: BrakeState = BrakeState.QUIESCENT
    for _tick in range(8):
        evaluation = evaluate_brake_state(
            (UncertaintyEstimate(class_tag="evidence", level=0.58),),
            prior_state=state,
            prior_tonic=tonic,
        )
        tonic = evaluation.tonic
        state = evaluation.state
        if state is BrakeState.GUARDED:
            break

    assert state is BrakeState.GUARDED
    assert tonic is not None
    assert tonic.tonic_pressure >= 0.35


def test_brake_tonic_spike_flips_immediately_regardless_of_tonic() -> None:
    # Contradiction/latching spikes must not wait for tonic confirmation.
    evaluation = evaluate_brake_state(
        (
            UncertaintyEstimate(
                class_tag="environment",
                level=0.60,
                spike_tags=frozenset({"contradiction"}),
            ),
        ),
        prior_state=BrakeState.QUIESCENT,
        prior_tonic=BrakeTonic(tonic_pressure=0.0, tonic_quiescence=1.0),
    )

    assert evaluation.state in {BrakeState.GUARDED, BrakeState.LATCHED}
    assert evaluation.tonic is not None


def test_brake_tonic_rejects_non_tonic_prior() -> None:
    try:
        evaluate_brake_state(
            (UncertaintyEstimate(class_tag="evidence", level=0.10),),
            prior_tonic="not-a-tonic",  # type: ignore[arg-type]
        )
    except TypeError as exc:
        assert "BrakeTonic | None" in str(exc)
    else:
        raise AssertionError("Expected TypeError for non-BrakeTonic prior_tonic")


def test_brake_tonic_pressure_ema_uses_locked_zero_point_six_rho_coefficient() -> None:
    # SRE_2 §7.5 coefficient lock: the tonic-pressure EMA must use rho = 0.60.
    # A 0.80 prior with current_pressure = 0.00 must yield next = 0.60 * 0.80 +
    # 0.40 * 0.00 = 0.48. Any drift in the decay coefficient would shift this
    # to a different value — this test is a unit-level regression guard that
    # ignores the enter/exit thresholds and focuses purely on the EMA math.
    prior = BrakeTonic(tonic_pressure=0.80, tonic_quiescence=0.20)
    evaluation = evaluate_brake_state(
        (UncertaintyEstimate(class_tag="evidence", level=0.0),),
        prior_state=BrakeState.GUARDED,
        prior_tonic=prior,
    )

    assert evaluation.tonic is not None
    # next = 0.60 * 0.80 + 0.40 * 0.00 = 0.48
    assert evaluation.tonic.tonic_pressure == pytest.approx(0.48)
    # quiescence EMA is the parallel mirror; current_quiescence = 1.0 - 0.0 = 1.0
    # next = 0.60 * 0.20 + 0.40 * 1.00 = 0.52
    assert evaluation.tonic.tonic_quiescence == pytest.approx(0.52)


def test_brake_tonic_single_clean_tick_does_not_exit_guarded_without_sustained_quiescence() -> None:
    # SRE_2 §7.5 exit-side gate: a guarded state with elevated tonic pressure
    # needs sustained rest-side evidence before returning to quiescent.
    prior = BrakeTonic(tonic_pressure=0.80, tonic_quiescence=0.20)
    evaluation = evaluate_brake_state(
        (UncertaintyEstimate(class_tag="evidence", level=0.0),),
        prior_state=BrakeState.GUARDED,
        prior_tonic=prior,
    )

    assert evaluation.state is BrakeState.GUARDED
    assert evaluation.tonic is not None
    assert evaluation.tonic.tonic_pressure == pytest.approx(0.48)
    assert evaluation.tonic.tonic_quiescence == pytest.approx(0.52)


def test_brake_tonic_sustained_quiescence_exits_guarded() -> None:
    # The rest-side EMA must be load-bearing without hardening into sticky
    # guardedness: sustained calm exits once tonic_quiescence clears the gate.
    tonic: BrakeTonic | None = BrakeTonic(tonic_pressure=0.80, tonic_quiescence=0.20)
    state: BrakeState = BrakeState.GUARDED
    ticks_to_exit = 0
    for _tick in range(8):
        evaluation = evaluate_brake_state(
            (UncertaintyEstimate(class_tag="evidence", level=0.0),),
            prior_state=state,
            prior_tonic=tonic,
        )
        tonic = evaluation.tonic
        state = evaluation.state
        ticks_to_exit += 1
        if state is BrakeState.QUIESCENT:
            break

    assert state is BrakeState.QUIESCENT
    assert tonic is not None
    assert tonic.tonic_quiescence >= 0.65
    assert ticks_to_exit <= 4


def test_brake_tonic_decays_toward_quiescence_after_sustained_calm() -> None:
    # SRE_2 §7.5 kill-rule-e: the tonic gate must not harden. A guarded burst
    # must decay back to quiescent once sustained calm returns, otherwise the
    # brake layer accumulates dead weight and the agent stops being productive.
    # Start from an elevated tonic pressure in the guarded state, then apply
    # sustained low-uncertainty ticks with no spikes, and assert the tonic
    # pressure decays below the exit threshold and the state returns to
    # quiescent within a bounded number of ticks.
    tonic: BrakeTonic | None = BrakeTonic(tonic_pressure=0.80, tonic_quiescence=0.20)
    state: BrakeState = BrakeState.GUARDED
    ticks_to_decay = 0
    for _tick in range(24):
        evaluation = evaluate_brake_state(
            (UncertaintyEstimate(class_tag="evidence", level=0.00),),
            prior_state=state,
            prior_tonic=tonic,
        )
        tonic = evaluation.tonic
        state = evaluation.state
        ticks_to_decay += 1
        if state is BrakeState.QUIESCENT and tonic is not None and tonic.tonic_pressure < 0.10:
            break

    assert state is BrakeState.QUIESCENT, (
        "tonic gate must decay to quiescent under sustained calm; "
        f"stuck at {state!r} after {ticks_to_decay} ticks"
    )
    assert tonic is not None
    assert tonic.tonic_pressure < 0.10
    # The 0.60 rho means decay is bounded — must not need more than ~16 ticks.
    assert ticks_to_decay <= 16


def test_brake_tonic_quiet_productive_flow_does_not_raise_tonic_pressure() -> None:
    # SRE_2 §7.5 kill-rule-e orthogonality: the tonic gate is driven by
    # uncertainty and spike signals, not by risk-weight posture. A quiet
    # productive flow (low uncertainty, no spikes, fresh prior) must keep the
    # tonic pressure well below the enter threshold regardless of how many
    # steps run. This prevents the tonic gate from slowly ramping up on its
    # own during healthy execution.
    tonic: BrakeTonic | None = None
    state: BrakeState = BrakeState.QUIESCENT
    pressure_peak = 0.0
    for _tick in range(16):
        evaluation = evaluate_brake_state(
            (UncertaintyEstimate(class_tag="evidence", level=0.10),),
            prior_state=state,
            prior_tonic=tonic,
        )
        tonic = evaluation.tonic
        state = evaluation.state
        if tonic is not None:
            pressure_peak = max(pressure_peak, tonic.tonic_pressure)

    assert state is BrakeState.QUIESCENT
    # Must stay strictly below the 0.35 enter threshold across the full run.
    assert pressure_peak < 0.35
