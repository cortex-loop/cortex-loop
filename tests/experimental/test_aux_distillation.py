"""Focused tests for store-backed AUX distillation over bounded episodes."""

from __future__ import annotations

import dataclasses

import pytest

from cortex.aux.distillation import distill_offline_support_publication
from cortex.aux.persistence import SqliteSupportMemoryStore, episode_from_support_snapshot
from cortex.aux.publication import augment_snapshot_with_offline_publication
from cortex.aux.support_priors import build_support_memory_prior_appendix
from cortex.core.support import SupportSnapshot
from cortex.sre.families import SoftControlFamily

from ._aux_test_support import make_aux_temporal_corpus, make_temporal_support_snapshot


def _with_host_tags(
    snapshot: SupportSnapshot,
    *,
    affordance_tags: frozenset[str] | None = None,
    constraint_tags: frozenset[str] | None = None,
) -> SupportSnapshot:
    updates: dict[str, object] = {}
    if affordance_tags is not None:
        updates["affordance_tags"] = frozenset(affordance_tags)
    if constraint_tags is not None:
        updates["constraint_tags"] = frozenset(constraint_tags)
    if not updates:
        return snapshot
    return dataclasses.replace(
        snapshot,
        host=dataclasses.replace(snapshot.host, **updates),
    )


def test_distillation_requires_two_supporting_episodes_for_positive_priors() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    snapshot_a = make_temporal_support_snapshot(
        "source-distill-a",
        published_memory_refs=("normalize-port-memo",),
        artifact_refs=("normalize-port-artifact",),
    )
    snapshot_b = make_temporal_support_snapshot(
        "source-distill-b",
        published_memory_refs=("normalize-port-checklist",),
        artifact_refs=("normalize-port-result",),
    )

    store.insert_episode(
        episode_from_support_snapshot(
            snapshot_a,
            host_name="reference",
            source_label="tests/experimental/test_aux_distillation",
        )
    )
    single_episode_publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )

    assert single_episode_publication.retrieval_prior_refs == ()
    assert single_episode_publication.published_memory_summary_refs == ()

    store.insert_episode(
        episode_from_support_snapshot(
            snapshot_b,
            host_name="reference",
            source_label="tests/experimental/test_aux_distillation",
        )
    )
    two_episode_publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )

    assert {
        (reference.reference_kind, reference.reference_id)
        for reference in two_episode_publication.retrieval_prior_refs
    } == {
        ("memory", "normalize-port-memo"),
        ("artifact", "normalize-port-artifact"),
        ("memory", "normalize-port-checklist"),
        ("artifact", "normalize-port-result"),
    }
    assert {
        (reference.reference_kind, reference.reference_id)
        for reference in two_episode_publication.published_memory_summary_refs
    } == {
        ("memory", "normalize-port-memo"),
        ("memory", "normalize-port-checklist"),
    }
    assert any(field.key == "episode_count" and field.value == 2 for field in two_episode_publication.metadata)


def test_distillation_suppresses_positive_priors_for_burden_heavy_window() -> None:
    scenario = {
        item.scenario_id: item
        for item in make_aux_temporal_corpus()
    }["burden-heavy-counterexample"]
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot in scenario.source_snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    augmented = augment_snapshot_with_offline_publication(
        scenario.target_snapshot,
        publication,
    )
    appendix = build_support_memory_prior_appendix(augmented)

    assert publication.retrieval_prior_refs == ()
    assert publication.branch_prior_refs == ()
    assert publication.uncertainty_calibration_refs == ()
    assert publication.published_memory_summary_refs == ()
    assert publication.contradiction_summary_refs
    assert any(
        field.key == "positive_prior_state" and field.value == "suppressed:burden-heavy"
        for field in publication.metadata
    )
    assert appendix.active is False
    assert "q_mem-penalty:burden" in appendix.score_for(SoftControlFamily.CHECK).reason_tags


def test_distillation_does_not_publish_unrelated_retrieval_or_memory_summary_refs() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot_id, memory_ref, artifact_ref in (
        ("source-unrelated-a", "normalize-port-memo", "normalize-port-artifact"),
        ("source-unrelated-b", "totally-unrelated-memo", "totally-unrelated-artifact"),
    ):
        store.insert_episode(
            episode_from_support_snapshot(
                make_temporal_support_snapshot(
                    snapshot_id,
                    published_memory_refs=(memory_ref,),
                    artifact_refs=(artifact_ref,),
                ),
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )

    assert publication.retrieval_prior_refs == ()
    assert publication.published_memory_summary_refs == ()


def test_distillation_requires_exact_branch_repeat_for_branch_priors() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot_id, branch_ref in (
        ("source-branch-a", "review-track"),
        ("source-branch-b", "deploy-track"),
    ):
        store.insert_episode(
            episode_from_support_snapshot(
                make_temporal_support_snapshot(
                    snapshot_id,
                    branch_registry=("main", branch_ref),
                ),
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    assert publication.branch_prior_refs == ()

    store.insert_episode(
        episode_from_support_snapshot(
            make_temporal_support_snapshot(
                "source-branch-c",
                branch_registry=("main", "review-track"),
                published_memory_refs=("review-track-second-pass",),
            ),
            host_name="reference",
            source_label="tests/experimental/test_aux_distillation",
        )
    )
    repeated_publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    assert {
        (reference.reference_kind, reference.reference_id)
        for reference in repeated_publication.branch_prior_refs
    } == {("branch", "review-track")}


def test_distillation_requires_exact_wake_and_brake_repeat_for_uncertainty_refs() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot_id, wake_reason, brake_entry in (
        ("source-uncertainty-a", "resume-needed", "guarded"),
        ("source-uncertainty-b", "review-needed", "latched"),
    ):
        store.insert_episode(
            episode_from_support_snapshot(
                make_temporal_support_snapshot(
                    snapshot_id,
                    wake_reason_tags=(wake_reason,),
                    brake_history=(brake_entry,),
                ),
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    assert publication.uncertainty_calibration_refs == ()

    store.insert_episode(
        episode_from_support_snapshot(
            make_temporal_support_snapshot(
                "source-uncertainty-c",
                wake_reason_tags=("resume-needed",),
                brake_history=("guarded",),
                published_memory_refs=("guarded-review-second-pass",),
            ),
            host_name="reference",
            source_label="tests/experimental/test_aux_distillation",
        )
    )
    repeated_publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    assert {
        (reference.reference_kind, reference.reference_id)
        for reference in repeated_publication.uncertainty_calibration_refs
    } == {
        ("uncertainty", "guarded"),
        ("wake", "resume-needed"),
    }


def test_distillation_empty_window_keeps_baseline_inactive() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    target_snapshot = make_temporal_support_snapshot(
        "target-empty-window",
        candidate_refs=("candidate-alpha",),
    )
    appendix = build_support_memory_prior_appendix(
        augment_snapshot_with_offline_publication(target_snapshot, publication)
    )

    assert publication.support_refs() == ()
    assert appendix.active is False
    assert appendix.score_for(SoftControlFamily.CHECK).score == 0.0


def test_distill_builds_host_reliability_prior_from_episodes() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    snapshots = (
        _with_host_tags(
            make_temporal_support_snapshot(
                "source-reliability-timeout-a",
                degradation_reason="timeout",
                contradiction_evidence_tags=("capability-drift",),
            ),
            affordance_tags=frozenset({"tool/intercept", "write-files"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot(
                "source-reliability-timeout-b",
                degradation_reason="timeout",
                contradiction_evidence_tags=("capability-drift",),
            ),
            affordance_tags=frozenset({"tool/intercept", "read-files"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot(
                "source-reliability-clean",
            ),
            affordance_tags=frozenset({"tool/intercept"}),
        ),
    )
    for snapshot in snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    prior = publication.host_reliability_prior

    assert prior is not None
    assert prior.timeout_rate == pytest.approx(2 / 3)
    assert prior.degradation_rate == pytest.approx(2 / 3)
    assert prior.capability_availability == 1.0
    assert prior.contradiction_counter == 2
    assert prior.ttl_hours == 72
    assert prior.last_validated_at is not None
    assert prior.last_validated_at.strip() == prior.last_validated_at
    assert prior.probe_failure_classes == ("degraded", "timed-out")
    assert prior.affordance_scope_tags == ("tool/intercept",)


def test_distilled_prior_capability_availability_drops_on_missing_capability() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    snapshots = (
        _with_host_tags(
            make_temporal_support_snapshot("source-missing-capability-a"),
            constraint_tags=frozenset({"missing-capability"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot("source-missing-capability-b"),
            constraint_tags=frozenset({"missing-capability"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot("source-missing-capability-c"),
            constraint_tags=frozenset(),
        ),
        _with_host_tags(
            make_temporal_support_snapshot("source-missing-capability-d"),
            constraint_tags=frozenset(),
        ),
    )
    for snapshot in snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    prior = publication.host_reliability_prior

    assert prior is not None
    assert prior.capability_availability == pytest.approx(0.5)
    assert "unsupported" in prior.probe_failure_classes
    assert prior.degradation_rate == pytest.approx(0.5)


def test_distilled_prior_affordance_scope_single_episode_equals_tags() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    snapshot = _with_host_tags(
        make_temporal_support_snapshot("source-single-scope"),
        affordance_tags=frozenset({"write-files", "tool/intercept", "retrieval/read"}),
    )
    store.insert_episode(
        episode_from_support_snapshot(
            snapshot,
            host_name="reference",
            source_label="tests/experimental/test_aux_distillation",
        )
    )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    prior = publication.host_reliability_prior

    assert prior is not None
    assert prior.ttl_hours == 24
    assert prior.affordance_scope_tags == (
        "retrieval/read",
        "tool/intercept",
        "write-files",
    )


def test_distilled_prior_affordance_scope_multi_episode_is_intersection() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    snapshots = (
        _with_host_tags(
            make_temporal_support_snapshot("source-intersection-a"),
            affordance_tags=frozenset({"tool/intercept", "write-files", "retrieval/read"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot("source-intersection-b"),
            affordance_tags=frozenset({"tool/intercept", "retrieval/read", "review/claims"}),
        ),
        _with_host_tags(
            make_temporal_support_snapshot("source-intersection-c"),
            affordance_tags=frozenset({"tool/intercept", "retrieval/read"}),
        ),
    )
    for snapshot in snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    prior = publication.host_reliability_prior

    assert prior is not None
    assert prior.ttl_hours == 72
    assert prior.affordance_scope_tags == ("retrieval/read", "tool/intercept")


def test_distilled_prior_omitted_when_no_episodes() -> None:
    store = SqliteSupportMemoryStore(":memory:")
    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )

    assert publication.host_reliability_prior is None


def test_distilled_prior_still_published_under_contradiction_heavy_window() -> None:
    scenario = {
        item.scenario_id: item
        for item in make_aux_temporal_corpus()
    }["burden-heavy-counterexample"]
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot in scenario.source_snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name="reference",
                source_label="tests/experimental/test_aux_distillation",
            )
        )

    publication = distill_offline_support_publication(
        store=store,
        host_name="reference",
        source_label="tests/experimental/test_aux_distillation",
    )
    prior = publication.host_reliability_prior

    assert publication.retrieval_prior_refs == ()
    assert publication.branch_prior_refs == ()
    assert prior is not None
    assert prior.degradation_rate > 0.0
    assert "degraded" in prior.probe_failure_classes
