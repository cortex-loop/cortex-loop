"""AUX-side builders for lawful support-memory priors."""

from __future__ import annotations

from collections import Counter

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference
from cortex.sre.families import SoftControlFamily
from cortex.sre.memory_priors import (
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)

from .augmentation import AugmentedSupportSnapshot


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _refs_by_kind(
    references: tuple[SupportReference, ...],
    *kinds: str,
) -> tuple[SupportReference, ...]:
    allowed = set(kinds)
    return tuple(reference for reference in references if reference.reference_kind in allowed)


def build_support_memory_prior_appendix(
    snapshot: AugmentedSupportSnapshot,
) -> SupportMemoryPriorAppendix:
    if not isinstance(snapshot, AugmentedSupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_support_memory_prior_appendix() requires AugmentedSupportSnapshot, "
            f"got {actual_type}.",
        )

    appendix = snapshot.auxiliary_support
    if "aux/offline-publication" not in appendix.derived_tags:
        return SupportMemoryPriorAppendix(
            appendix_tags=appendix.derived_tags,
            notes=("offline publication tag missing; Q_mem remains inactive",),
            metadata=appendix.metadata,
        )

    derived_refs = appendix.derived_support_refs
    kind_counts = Counter(reference.reference_kind for reference in derived_refs)
    branch_refs = _refs_by_kind(derived_refs, "branch")
    retrieval_refs = _refs_by_kind(derived_refs, "memory", "artifact")
    contradiction_refs = _refs_by_kind(derived_refs, "contradiction")
    uncertainty_refs = _refs_by_kind(derived_refs, "uncertainty", "wake")

    scores = (
        SupportMemoryPriorScore(
            family=SoftControlFamily.NEUTRAL,
            score=0.0,
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRANCH,
            score=_clip_unit((0.20 * len(branch_refs)) + (0.05 * len(retrieval_refs))),
            reason_tags=frozenset({"q_mem:active", "support-memory:branch"}),
            support_refs=branch_refs + retrieval_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.CHECK,
            score=_clip_unit(
                (0.25 * len(contradiction_refs))
                + (0.15 * len(uncertainty_refs))
                + (0.05 * len(retrieval_refs))
            ),
            reason_tags=frozenset({"q_mem:active", "support-memory:verification"}),
            support_refs=contradiction_refs + uncertainty_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.REDIRECT,
            score=_clip_unit(
                (0.15 * len(branch_refs))
                + (0.10 * len(retrieval_refs))
                + (0.05 * kind_counts.get("memory", 0))
            ),
            reason_tags=frozenset({"q_mem:active", "support-memory:redirect"}),
            support_refs=branch_refs[:1] + retrieval_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.SEEK_CONTEXT,
            score=_clip_unit((0.12 * len(uncertainty_refs)) + (0.08 * len(retrieval_refs))),
            reason_tags=frozenset({"q_mem:active", "support-memory:context"}),
            support_refs=uncertainty_refs[:2] + retrieval_refs[:1],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRAKE,
            score=_clip_unit((0.15 * len(contradiction_refs)) + (0.12 * len(uncertainty_refs))),
            reason_tags=frozenset({"q_mem:active", "support-memory:brake"}),
            support_refs=contradiction_refs[:2] + uncertainty_refs[:1],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.ESCALATE,
            score=_clip_unit(0.05 * len(contradiction_refs)),
            reason_tags=frozenset({"q_mem:active", "support-memory:escalate"}),
            support_refs=contradiction_refs[:1],
        ),
    )
    return SupportMemoryPriorAppendix(
        scores=scores,
        appendix_tags=appendix.derived_tags | frozenset({"q_mem:explicit-aux"}),
        notes=appendix.notes + ("memory-conditioned priors derived from AUX offline publication",),
        metadata=(MetadataField("source", "aux/support-priors"),) + appendix.metadata,
    )


__all__ = ["build_support_memory_prior_appendix"]
