"""Focused tests for support-only offline publication contracts."""

from __future__ import annotations

import pytest

from cortex.aux.augmentation import AugmentedSupportSnapshot
from cortex.aux.publication import (
    OfflineSupportPublication,
    augment_snapshot_with_offline_publication,
    build_offline_support_publication,
    offline_support_publication_as_payload,
    parse_offline_support_publication_payload,
)
from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportState
from cortex.sre.memory_priors import HostReliabilityPrior

from ._aux_test_support import (
    fresh_validated_at_iso,
    make_support_ref,
    make_support_snapshot,
)


def test_offline_support_publication_augments_snapshot_only_through_explicit_aux_appendix() -> None:
    snapshot = make_support_snapshot()
    publication = OfflineSupportPublication(
        retrieval_prior_refs=(make_support_ref("retrieval-prior", "retrieval-1"),),
        branch_prior_refs=(make_support_ref("branch-prior", "branch-1"),),
        contradiction_summary_refs=(
            make_support_ref("contradiction-summary", "contradiction-1"),
        ),
        uncertainty_calibration_refs=(
            make_support_ref("uncertainty-calibration", "uncertainty-1"),
        ),
        published_memory_summary_refs=(make_support_ref("memory-summary", "memory-1"),),
        publication_tags=frozenset({"aux/offline-summary"}),
        notes=("offline summary remains support-side only",),
        metadata=(MetadataField("source", "offline-eval"),),
    )

    augmented = augment_snapshot_with_offline_publication(snapshot, publication)

    assert isinstance(augmented, AugmentedSupportSnapshot)
    assert augmented.core_snapshot is snapshot
    assert len(augmented.auxiliary_support.derived_support_refs) == 5
    assert "aux/offline-publication" in augmented.auxiliary_support.derived_tags


def test_build_offline_support_publication_derives_only_support_side_refs_from_snapshot() -> None:
    snapshot = make_support_snapshot()
    publication = build_offline_support_publication(snapshot)
    augmented = augment_snapshot_with_offline_publication(snapshot, publication)

    assert publication.retrieval_prior_refs
    assert publication.branch_prior_refs
    assert publication.contradiction_summary_refs
    assert publication.uncertainty_calibration_refs
    assert publication.published_memory_summary_refs
    assert "aux/offline-publication" in publication.publication_tags
    assert publication.notes[0].startswith("support-only publication")
    assert "aux/offline-publication" in augmented.auxiliary_support.derived_tags
    assert augmented.auxiliary_support.metadata[0].key == "source"

    with pytest.raises(TypeError, match="SupportSnapshot"):
        augment_snapshot_with_offline_publication(SupportState(), publication)


def test_offline_support_publication_requires_typed_support_refs_and_metadata() -> None:
    with pytest.raises(TypeError, match="retrieval_prior_refs"):
        OfflineSupportPublication(retrieval_prior_refs=("retrieval-1",))

    with pytest.raises(TypeError, match="metadata"):
        OfflineSupportPublication(metadata=("not-field",))

    with pytest.raises(ValueError, match="publication_tags"):
        OfflineSupportPublication(publication_tags=frozenset({"   "}))


def test_offline_support_publication_payload_roundtrips_with_locked_shape() -> None:
    publication = OfflineSupportPublication(
        retrieval_prior_refs=(make_support_ref("retrieval-prior", "retrieval-1"),),
        branch_prior_refs=(make_support_ref("branch-prior", "branch-1"),),
        contradiction_summary_refs=(
            make_support_ref("contradiction-summary", "contradiction-1"),
        ),
        uncertainty_calibration_refs=(
            make_support_ref("uncertainty-calibration", "uncertainty-1"),
        ),
        published_memory_summary_refs=(make_support_ref("memory-summary", "memory-1"),),
        publication_tags=frozenset({"aux/offline-summary", "claim-conservative"}),
        notes=("support-side only",),
        metadata=(MetadataField("source", "offline-eval"), MetadataField("host_name", "openai")),
    )

    payload = offline_support_publication_as_payload(publication)
    restored = parse_offline_support_publication_payload(payload)

    assert tuple(payload) == (
        "retrieval_prior_refs",
        "branch_prior_refs",
        "contradiction_summary_refs",
        "uncertainty_calibration_refs",
        "published_memory_summary_refs",
        "publication_tags",
        "notes",
        "metadata",
        "host_reliability_prior",
    )
    assert tuple(payload["retrieval_prior_refs"][0]) == (
        "reference_kind",
        "reference_id",
        "tags",
        "metadata",
    )
    assert tuple(payload["metadata"][0]) == ("key", "value")
    assert restored == publication


def test_parse_offline_support_publication_payload_rejects_wrong_key_order() -> None:
    with pytest.raises(ValueError, match="locked key order"):
        parse_offline_support_publication_payload(
            {
                "branch_prior_refs": [],
                "retrieval_prior_refs": [],
                "contradiction_summary_refs": [],
                "uncertainty_calibration_refs": [],
                "published_memory_summary_refs": [],
                "publication_tags": [],
                "notes": [],
                "metadata": [],
                "host_reliability_prior": None,
            }
        )


def test_offline_publication_payload_always_includes_host_reliability_prior_key() -> None:
    publication_without_prior = OfflineSupportPublication()
    publication_with_prior = OfflineSupportPublication(
        host_reliability_prior=HostReliabilityPrior(
            timeout_rate=0.1,
            degradation_rate=0.2,
            capability_availability=0.9,
            contradiction_counter=1,
            ttl_hours=48,
            last_validated_at=fresh_validated_at_iso(),
            probe_failure_classes=("timed-out",),
            affordance_scope_tags=("tool/intercept",),
        ),
    )

    payload_absent = offline_support_publication_as_payload(publication_without_prior)
    payload_present = offline_support_publication_as_payload(publication_with_prior)

    assert "host_reliability_prior" in payload_absent
    assert payload_absent["host_reliability_prior"] is None
    assert "host_reliability_prior" in payload_present
    assert payload_present["host_reliability_prior"] is not None


def test_offline_publication_payload_round_trips_reliability_prior_with_affordance_scope() -> None:
    publication = OfflineSupportPublication(
        host_reliability_prior=HostReliabilityPrior(
            timeout_rate=0.25,
            degradation_rate=0.5,
            capability_availability=0.75,
            contradiction_counter=3,
            ttl_hours=72,
            last_validated_at=fresh_validated_at_iso(),
            probe_failure_classes=("degraded", "timed-out"),
            affordance_scope_tags=("retrieval/read", "tool/intercept"),
        ),
    )

    payload = offline_support_publication_as_payload(publication)
    restored = parse_offline_support_publication_payload(payload)

    assert tuple(payload["host_reliability_prior"]) == (
        "timeout_rate",
        "degradation_rate",
        "capability_availability",
        "contradiction_counter",
        "ttl_hours",
        "last_validated_at",
        "probe_failure_classes",
        "affordance_scope_tags",
    )
    assert payload["host_reliability_prior"]["affordance_scope_tags"] == [
        "retrieval/read",
        "tool/intercept",
    ]
    assert payload["host_reliability_prior"]["probe_failure_classes"] == [
        "degraded",
        "timed-out",
    ]
    assert restored == publication


def test_offline_publication_payload_rejects_legacy_8_key_tuple() -> None:
    with pytest.raises(ValueError, match="locked key order"):
        parse_offline_support_publication_payload(
            {
                "retrieval_prior_refs": [],
                "branch_prior_refs": [],
                "contradiction_summary_refs": [],
                "uncertainty_calibration_refs": [],
                "published_memory_summary_refs": [],
                "publication_tags": [],
                "notes": [],
                "metadata": [],
            }
        )


def test_offline_publication_payload_rejects_reliability_prior_with_wrong_inner_key_order() -> None:
    with pytest.raises(ValueError, match="locked key order"):
        parse_offline_support_publication_payload(
            {
                "retrieval_prior_refs": [],
                "branch_prior_refs": [],
                "contradiction_summary_refs": [],
                "uncertainty_calibration_refs": [],
                "published_memory_summary_refs": [],
                "publication_tags": [],
                "notes": [],
                "metadata": [],
                "host_reliability_prior": {
                    "degradation_rate": 0.1,
                    "timeout_rate": 0.1,
                    "capability_availability": 0.9,
                    "contradiction_counter": 0,
                    "ttl_hours": 24,
                    "last_validated_at": None,
                    "probe_failure_classes": [],
                    "affordance_scope_tags": [],
                },
            }
        )


def test_augment_snapshot_threads_published_reliability_prior_onto_auxiliary_support() -> None:
    snapshot = make_support_snapshot()
    prior = HostReliabilityPrior(
        timeout_rate=0.1,
        degradation_rate=0.2,
        capability_availability=0.85,
        contradiction_counter=1,
        ttl_hours=48,
        last_validated_at=fresh_validated_at_iso(),
        probe_failure_classes=("timed-out",),
        affordance_scope_tags=("tool/intercept",),
    )
    publication = OfflineSupportPublication(host_reliability_prior=prior)

    augmented = augment_snapshot_with_offline_publication(snapshot, publication)

    assert augmented.auxiliary_support.published_host_reliability_prior is prior

    publication_without_prior = OfflineSupportPublication()
    augmented_without_prior = augment_snapshot_with_offline_publication(
        snapshot,
        publication_without_prior,
    )
    assert augmented_without_prior.auxiliary_support.published_host_reliability_prior is None
