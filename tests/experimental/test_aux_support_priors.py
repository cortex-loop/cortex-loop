"""Focused tests for AUX-derived support-memory priors."""

from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import replace

import pytest

from cortex.aux.augmentation import AuxiliarySupportAppendix, augment_snapshot
from cortex.aux.distillation import _distill_offline_support_publication_from_snapshots
from cortex.aux.publication import (
    augment_snapshot_with_offline_publication,
    build_offline_support_publication,
)
from cortex.aux.support_priors import (
    SupportMemorySignalProfile,
    _build_signal_profile,
    build_support_memory_prior_appendix,
    filter_live_support_memory_prior_appendix,
)
from cortex.sre.memory_priors import HostReliabilityPrior
from cortex.core.support import SupportState
from cortex.sre.families import SoftControlFamily

from ._aux_test_support import make_aux_temporal_corpus, make_support_ref, make_support_snapshot


def test_build_support_memory_prior_appendix_requires_augmented_support_snapshot() -> None:
    with pytest.raises(TypeError, match="AugmentedSupportSnapshot"):
        build_support_memory_prior_appendix(SupportState())


def test_build_support_memory_prior_appendix_derives_nonzero_family_priors_from_offline_publication() -> None:
    snapshot = make_support_snapshot()
    publication = build_offline_support_publication(snapshot)
    augmented = augment_snapshot_with_offline_publication(snapshot, publication)

    appendix = build_support_memory_prior_appendix(augmented)

    assert appendix.active is True
    assert "q_mem:explicit-aux" in appendix.appendix_tags
    assert appendix.score_for(SoftControlFamily.BRANCH).score > 0.0
    assert appendix.score_for(SoftControlFamily.CHECK).score > 0.0
    assert "q_mem-signal:branch" in appendix.score_for(SoftControlFamily.BRANCH).reason_tags
    assert "q_mem-signal:contradiction" in appendix.score_for(SoftControlFamily.CHECK).reason_tags
    assert appendix.metadata[0].key == "source"


def test_build_support_memory_prior_appendix_stays_inactive_without_offline_publication_tag() -> None:
    augmented = augment_snapshot(
        make_support_snapshot(),
        auxiliary_support=AuxiliarySupportAppendix(
            derived_support_refs=(make_support_ref("memory", "memo-1"),),
            derived_tags=frozenset({"aux/geometry-only"}),
            notes=("geometry only",),
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    assert appendix.active is False
    assert appendix.score_for(SoftControlFamily.CHECK).score == 0.0
    assert appendix.notes == ("offline publication tag missing; Q_mem remains inactive",)


def test_support_memory_signal_profile_derives_match_based_signals_from_augmented_target_snapshots() -> None:
    branch_augmented = _augmented_temporal_case("branch-resume-recovery")
    contradiction_augmented = _augmented_temporal_case("contradiction-review")
    uncertainty_augmented = _augmented_temporal_case("uncertainty-brake-calibration")

    branch_profile = _build_signal_profile(branch_augmented)
    contradiction_profile = _build_signal_profile(contradiction_augmented)
    uncertainty_profile = _build_signal_profile(uncertainty_augmented)

    assert isinstance(branch_profile, SupportMemorySignalProfile)
    assert branch_profile.branch_resume_signal > 0.0
    assert branch_profile.retrieval_reuse_signal > 0.0
    assert contradiction_profile.contradiction_review_signal > 0.0
    assert uncertainty_profile.uncertainty_calibration_signal > 0.0
    assert uncertainty_profile.burden_penalty == pytest.approx(0.0)


def test_support_memory_signal_profile_applies_burden_penalties_without_creating_false_positive_priors() -> None:
    augmented = _augmented_temporal_case("burden-heavy-counterexample")

    profile = _build_signal_profile(augmented)
    appendix = build_support_memory_prior_appendix(augmented)

    assert profile.burden_penalty > 0.5
    assert appendix.active is False
    assert appendix.score_for(SoftControlFamily.CHECK).score == 0.0
    assert appendix.score_for(SoftControlFamily.BRANCH).score == 0.0
    assert "q_mem-penalty:burden" in appendix.score_for(SoftControlFamily.CHECK).reason_tags


def test_build_support_memory_prior_appendix_applies_reliability_weight_to_host_dependent_family_scores() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert appendix.host_reliability_prior is not None
    assert appendix.host_reliability_prior.capability_availability == pytest.approx(1.0)
    assert "q_mem-host:reliability-active" in branch_score.reason_tags
    assert branch_score.score > 0.0


def test_build_support_memory_prior_appendix_invalidates_reliability_weight_on_fresh_contradiction() -> None:
    augmented = _augmented_temporal_case("contradiction-review")

    appendix = build_support_memory_prior_appendix(augmented)

    check_score = appendix.score_for(SoftControlFamily.CHECK)
    assert len(augmented.core_snapshot.trace.degradation_records) > 0
    assert appendix.host_reliability_prior is not None
    assert "q_mem-host:current-contradiction-invalidated" in check_score.reason_tags
    assert "q_mem-host:reliability-active" not in check_score.reason_tags


def test_build_support_memory_prior_appendix_zeroes_reliability_weight_when_ttl_expires() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=1,
            last_validated_at="2000-01-01T00:00:00+00:00",
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert "q_mem-host:ttl-expired" in branch_score.reason_tags
    assert "q_mem-host:reliability-active" not in branch_score.reason_tags


def test_build_support_memory_prior_appendix_can_disable_host_reliability_without_changing_support_signals() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")

    appendix = build_support_memory_prior_appendix(augmented)
    appendix_without_reliability = build_support_memory_prior_appendix(
        augmented,
        enable_host_reliability=False,
    )

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    branch_score_without_reliability = appendix_without_reliability.score_for(
        SoftControlFamily.BRANCH
    )

    assert appendix.host_reliability_prior == appendix_without_reliability.host_reliability_prior
    assert branch_score.score > branch_score_without_reliability.score
    assert "q_mem-host:reliability-active" in branch_score.reason_tags
    assert "q_mem-host:reliability-active" not in branch_score_without_reliability.reason_tags
    assert "q_mem-signal:branch" in branch_score_without_reliability.reason_tags


def test_filter_live_support_memory_prior_appendix_keeps_only_reference_first_eligible_families() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    appendix = build_support_memory_prior_appendix(augmented)

    live_appendix = filter_live_support_memory_prior_appendix(
        augmented.core_snapshot,
        appendix,
        target_host_name="test-support-priors",
    )

    assert live_appendix.active is True
    assert live_appendix.score_for(SoftControlFamily.BRANCH).score > 0.0
    assert live_appendix.score_for(SoftControlFamily.CHECK).score == 0.0
    assert live_appendix.score_for(SoftControlFamily.BRAKE).score == 0.0
    assert "q_mem-live:family-ineligible" in live_appendix.score_for(
        SoftControlFamily.BRAKE
    ).reason_tags
    assert "q_mem-live:eligible" in live_appendix.score_for(
        SoftControlFamily.BRANCH
    ).reason_tags


def test_filter_live_support_memory_prior_appendix_blocks_host_mismatch() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    appendix = build_support_memory_prior_appendix(augmented)

    live_appendix = filter_live_support_memory_prior_appendix(
        augmented.core_snapshot,
        appendix,
        target_host_name="reference",
    )

    assert live_appendix.active is False
    assert live_appendix.score_for(SoftControlFamily.BRANCH).score == 0.0
    assert "q_mem-live:invalidated:host-mismatch" in live_appendix.score_for(
        SoftControlFamily.BRANCH
    ).reason_tags
    assert any(
        field.key == "live_reentry_state" and field.value == "host-mismatch"
        for field in live_appendix.metadata
    )


def test_filter_live_support_memory_prior_appendix_zeroes_ttl_expired_family_on_live_path() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=1,
            last_validated_at="2000-01-01T00:00:00+00:00",
        ),
    )
    appendix = build_support_memory_prior_appendix(augmented)

    live_appendix = filter_live_support_memory_prior_appendix(
        augmented.core_snapshot,
        appendix,
        target_host_name="test-support-priors",
    )

    assert live_appendix.score_for(SoftControlFamily.BRANCH).score == 0.0
    assert "q_mem-live:invalidated:ttl-expired" in live_appendix.score_for(
        SoftControlFamily.BRANCH
    ).reason_tags
    assert live_appendix.score_for(SoftControlFamily.REDIRECT).score > 0.0


def test_filter_live_support_memory_prior_appendix_invalidates_resume_context_families_on_fresh_contradiction() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    appendix = build_support_memory_prior_appendix(augmented)
    contradiction_trace = replace(
        augmented.core_snapshot.trace,
        degradation_records=make_support_snapshot().trace.degradation_records,
    )
    contradiction_snapshot = replace(
        augmented.core_snapshot,
        trace=contradiction_trace,
    )

    live_appendix = filter_live_support_memory_prior_appendix(
        contradiction_snapshot,
        appendix,
        target_host_name="test-support-priors",
    )

    assert live_appendix.score_for(SoftControlFamily.BRANCH).score == 0.0
    assert live_appendix.score_for(SoftControlFamily.REDIRECT).score == 0.0
    assert live_appendix.score_for(SoftControlFamily.SEEK_CONTEXT).score > 0.0
    assert "q_mem-live:invalidated:contradiction" in live_appendix.score_for(
        SoftControlFamily.BRANCH
    ).reason_tags
    assert "q_mem-live:invalidated:contradiction" in live_appendix.score_for(
        SoftControlFamily.REDIRECT
    ).reason_tags
    assert "q_mem-live:eligible" in live_appendix.score_for(
        SoftControlFamily.SEEK_CONTEXT
    ).reason_tags


def test_filter_live_support_memory_prior_appendix_invalidates_uncertainty_families_after_probe_failure() -> None:
    augmented = _augmented_temporal_case("uncertainty-brake-calibration")
    appendix = build_support_memory_prior_appendix(augmented)

    live_appendix = filter_live_support_memory_prior_appendix(
        augmented.core_snapshot,
        appendix,
        target_host_name="test-support-priors",
        recent_probe_failure_class="timed-out",
    )

    assert live_appendix.score_for(SoftControlFamily.CHECK).score == 0.0
    assert live_appendix.score_for(SoftControlFamily.SEEK_CONTEXT).score == 0.0
    assert "q_mem-live:invalidated:probe-failure" in live_appendix.score_for(
        SoftControlFamily.SEEK_CONTEXT
    ).reason_tags


def test_historical_contradiction_alone_no_longer_auto_zeros() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    historical_prior = HostReliabilityPrior(
        timeout_rate=0.0,
        degradation_rate=0.0,
        capability_availability=1.0,
        contradiction_counter=3,
        ttl_hours=72,
        last_validated_at=_fresh_validated_at(),
        probe_failure_classes=("timed-out",),
    )
    augmented = _replace_published_reliability_prior(augmented, historical_prior)

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert branch_score.score > 0.0
    assert "q_mem-host:reliability-active" in branch_score.reason_tags
    assert "q_mem-host:success-reopened" in branch_score.reason_tags


def test_host_reliability_prior_published_from_publication_wins_over_synthesis() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    published_prior = HostReliabilityPrior(
        timeout_rate=0.0,
        degradation_rate=0.0,
        capability_availability=0.5,
        contradiction_counter=0,
        ttl_hours=72,
        last_validated_at=_fresh_validated_at(),
    )
    augmented_with_published = _replace_published_reliability_prior(
        augmented,
        published_prior,
    )

    appendix = build_support_memory_prior_appendix(augmented_with_published)

    assert appendix.host_reliability_prior is published_prior
    assert appendix.host_reliability_prior.capability_availability == pytest.approx(0.5)


def test_affordance_gating_mismatch_emits_tag_and_zeros_bonus() -> None:
    augmented = _augmented_temporal_case("contradiction-review")
    # Use a clean target snapshot (without degradation records) so the
    # current-contradiction gate does not mask the affordance gate.
    clean_trace = replace(
        augmented.core_snapshot.trace,
        degradation_records=(),
    )
    clean_core = replace(augmented.core_snapshot, trace=clean_trace)
    augmented = replace(augmented, core_snapshot=clean_core)
    augmented = _replace_host_affordance_tags(augmented, {"read-files"})
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=72,
            last_validated_at=_fresh_validated_at(),
            affordance_scope_tags=("write-files",),
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    check_score = appendix.score_for(SoftControlFamily.CHECK)
    seek_score = appendix.score_for(SoftControlFamily.SEEK_CONTEXT)
    assert "q_mem-host:affordance-mismatch" in check_score.reason_tags
    assert "q_mem-host:affordance-mismatch" in seek_score.reason_tags
    assert "q_mem-host:reliability-active" not in check_score.reason_tags
    assert "q_mem-host:reliability-active" not in seek_score.reason_tags


def test_affordance_gating_overlap_passes_through() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    augmented = _replace_host_affordance_tags(
        augmented,
        {"tool/intercept", "write-files"},
    )
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=72,
            last_validated_at=_fresh_validated_at(),
            affordance_scope_tags=("write-files",),
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert "q_mem-host:affordance-mismatch" not in branch_score.reason_tags
    assert "q_mem-host:reliability-active" in branch_score.reason_tags


def test_affordance_empty_scope_is_transparent() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=72,
            last_validated_at=_fresh_validated_at(),
            affordance_scope_tags=(),
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert "q_mem-host:affordance-mismatch" not in branch_score.reason_tags
    assert "q_mem-host:reliability-active" in branch_score.reason_tags


def test_affordance_gate_skipped_for_branch() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")
    augmented = _replace_host_affordance_tags(augmented, {"read-files"})
    augmented = _replace_published_reliability_prior(
        augmented,
        HostReliabilityPrior(
            timeout_rate=0.0,
            degradation_rate=0.0,
            capability_availability=1.0,
            contradiction_counter=0,
            ttl_hours=72,
            last_validated_at=_fresh_validated_at(),
            affordance_scope_tags=("write-files",),
        ),
    )

    appendix = build_support_memory_prior_appendix(augmented)

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    assert "q_mem-host:affordance-mismatch" not in branch_score.reason_tags
    assert "q_mem-host:reliability-active" in branch_score.reason_tags


def test_recent_probe_failure_invalidates_check_and_seek_context_only() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")

    appendix = build_support_memory_prior_appendix(
        augmented,
        recent_probe_failure_class="timed-out",
    )

    branch_score = appendix.score_for(SoftControlFamily.BRANCH)
    check_score = appendix.score_for(SoftControlFamily.CHECK)
    seek_score = appendix.score_for(SoftControlFamily.SEEK_CONTEXT)
    assert "q_mem-host:recent-probe-failure-invalidated" in check_score.reason_tags
    assert "q_mem-host:recent-probe-failure-invalidated" in seek_score.reason_tags
    assert (
        "q_mem-host:recent-probe-failure-invalidated"
        not in branch_score.reason_tags
    )


def test_reliability_delta_recorded_in_score_metadata() -> None:
    augmented = _augmented_temporal_case("branch-resume-recovery")

    appendix = build_support_memory_prior_appendix(augmented)

    for family in (
        SoftControlFamily.BRANCH,
        SoftControlFamily.CHECK,
        SoftControlFamily.SEEK_CONTEXT,
    ):
        score = appendix.score_for(family)
        delta_fields = [
            field
            for field in score.metadata
            if field.key == "q_mem-host:reliability_delta"
        ]
        assert len(delta_fields) == 1
        assert isinstance(delta_fields[0].value, float)


def _augmented_temporal_case(scenario_id: str):
    scenario = {
        scenario.scenario_id: scenario
        for scenario in make_aux_temporal_corpus()
    }[scenario_id]
    publication = _distill_offline_support_publication_from_snapshots(
        scenario.source_snapshots,
        host_name="test-support-priors",
        source_label="tests/experimental/test_aux_support_priors",
        publication_tags=frozenset({"aux/offline-publication", "aux/reference-replay"}),
        notes=("test support-memory prior derivation",),
    )
    return augment_snapshot_with_offline_publication(
        scenario.target_snapshot,
        publication,
    )


def _fresh_validated_at() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _replace_published_reliability_prior(augmented, prior):
    return replace(
        augmented,
        auxiliary_support=replace(
            augmented.auxiliary_support,
            published_host_reliability_prior=prior,
        ),
    )


def _replace_host_affordance_tags(augmented, affordance_tags):
    new_host = replace(
        augmented.core_snapshot.host,
        affordance_tags=frozenset(affordance_tags),
    )
    new_core = replace(augmented.core_snapshot, host=new_host)
    return replace(augmented, core_snapshot=new_core)
