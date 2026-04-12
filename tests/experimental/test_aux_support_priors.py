"""Focused tests for AUX-derived support-memory priors."""

from __future__ import annotations

import pytest

from cortex.aux._temporal_publication import _merge_temporal_publication
from cortex.aux.augmentation import AuxiliarySupportAppendix, augment_snapshot
from cortex.aux.publication import (
    augment_snapshot_with_offline_publication,
    build_offline_support_publication,
)
from cortex.aux.support_priors import (
    SupportMemorySignalProfile,
    _build_signal_profile,
    build_support_memory_prior_appendix,
)
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


def _augmented_temporal_case(scenario_id: str):
    scenario = {
        scenario.scenario_id: scenario
        for scenario in make_aux_temporal_corpus()
    }[scenario_id]
    publication = _merge_temporal_publication(
        scenario.source_snapshots,
        source_label="tests/experimental/test_aux_support_priors",
        extra_tags=frozenset({"aux/offline-publication", "aux/reference-replay"}),
        extra_notes=("test support-memory prior derivation",),
    )
    return augment_snapshot_with_offline_publication(
        scenario.target_snapshot,
        publication,
    )
