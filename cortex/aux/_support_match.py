"""Private AUX support-reference matching helpers shared by geometry and corpus evaluation."""

from __future__ import annotations

import re

from cortex.core.support import SupportReference, SupportSnapshot


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(*values: str) -> frozenset[str]:
    tokens: set[str] = set()
    for value in values:
        tokens.update(_TOKEN_PATTERN.findall(value.lower()))
    return frozenset(tokens)


def _reference_tokens(reference: SupportReference) -> frozenset[str]:
    tokens = set(_tokenize(reference.reference_kind, reference.reference_id))
    for tag in reference.tags:
        tokens.update(_tokenize(tag))
    for field in reference.metadata:
        tokens.update(_tokenize(field.key, str(field.value)))
    return frozenset(tokens)


def _dedupe_support_refs(references: tuple[SupportReference, ...]) -> tuple[SupportReference, ...]:
    ordered: list[SupportReference] = []
    seen: set[tuple[str, str]] = set()
    for reference in references:
        key = (reference.reference_kind, reference.reference_id)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(reference)
    return tuple(ordered)


def _source_refs_for_retrieval(snapshot: SupportSnapshot) -> tuple[SupportReference, ...]:
    refs: list[SupportReference] = [
        SupportReference("candidate", candidate_ref, tags=frozenset({"trace-candidate"}))
        for candidate_ref in snapshot.trace.candidate_refs
    ]
    refs.extend(
        SupportReference("goal", goal_ref, tags=frozenset({"pending-goal"}))
        for goal_ref in snapshot.session.pending_goal_refs
    )
    refs.extend(
        SupportReference("wake", receipt.reason_tag, tags=frozenset({"wake-receipt"}))
        for receipt in snapshot.trace.wake_receipts
    )
    refs.extend(
        SupportReference("reminder", reminder, tags=frozenset({"continuity-reminder"}))
        for reminder in snapshot.session.reminders
    )
    return _dedupe_support_refs(tuple(refs))


def _retrieval_candidate_pool(snapshot: SupportSnapshot) -> tuple[SupportReference, ...]:
    return _dedupe_support_refs(
        snapshot.exec_memory_pub.published_memory_refs + snapshot.exec_memory_pub.artifact_refs
    )


def _match_score(
    source_ref: SupportReference,
    candidate_ref: SupportReference,
    *,
    base_score: float,
) -> float:
    source_tokens = _reference_tokens(source_ref)
    candidate_tokens = _reference_tokens(candidate_ref)
    overlap = source_tokens & candidate_tokens
    token_union = source_tokens | candidate_tokens
    overlap_score = (len(overlap) / len(token_union)) if token_union else 0.0
    kind_bonus = 0.15 if source_ref.reference_kind == candidate_ref.reference_kind else 0.0
    artifact_bonus = (
        0.10
        if candidate_ref.reference_kind in {"artifact", "memory", "result-artifact"}
        else 0.0
    )
    return min(1.0, base_score + (0.55 * overlap_score) + kind_bonus + artifact_bonus)
