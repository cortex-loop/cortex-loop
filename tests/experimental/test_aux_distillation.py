"""Focused tests for store-backed AUX distillation over bounded episodes."""

from __future__ import annotations

from cortex.aux.distillation import distill_offline_support_publication
from cortex.aux.persistence import SqliteSupportMemoryStore, episode_from_support_snapshot
from cortex.aux.publication import augment_snapshot_with_offline_publication
from cortex.aux.support_priors import build_support_memory_prior_appendix
from cortex.sre.families import SoftControlFamily

from ._aux_test_support import make_aux_temporal_corpus, make_temporal_support_snapshot


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

    assert two_episode_publication.retrieval_prior_refs
    assert two_episode_publication.published_memory_summary_refs
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
