"""Focused tests for AUX-derived support-memory priors."""

from __future__ import annotations

import pytest

from cortex.aux.augmentation import AuxiliarySupportAppendix, augment_snapshot
from cortex.aux.publication import (
    augment_snapshot_with_offline_publication,
    build_offline_support_publication,
)
from cortex.aux.support_priors import build_support_memory_prior_appendix
from cortex.core.support import SupportState
from cortex.sre.families import SoftControlFamily

from ._aux_test_support import make_support_ref, make_support_snapshot


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
    assert "support-memory:branch" in appendix.score_for(SoftControlFamily.BRANCH).reason_tags
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
