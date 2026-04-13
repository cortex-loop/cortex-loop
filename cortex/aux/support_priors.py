"""AUX-side builders for lawful support-memory priors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference
from cortex.sre.families import SoftControlFamily
from cortex.sre.memory_priors import (
    HostReliabilityPrior,
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)

from ._support_match import (
    _dedupe_support_refs,
    _match_score,
    _reference_tokens,
    _source_refs_for_retrieval,
)
from .augmentation import AugmentedSupportSnapshot


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _clip_prior_score(value: float) -> float:
    return max(0.0, min(0.75, float(value)))


@dataclass(frozen=True, slots=True)
class _HostReliabilityAdjustment:
    weight: float
    invalidated: bool = False
    ttl_expired: bool = False

    @property
    def active(self) -> bool:
        return self.weight > 0.0 and not self.invalidated and not self.ttl_expired


def _refs_by_kind(
    references: tuple[SupportReference, ...],
    *kinds: str,
) -> tuple[SupportReference, ...]:
    allowed = set(kinds)
    return tuple(reference for reference in references if reference.reference_kind in allowed)


def _metadata_int(
    metadata: tuple[MetadataField, ...],
    key: str,
) -> int:
    for field in metadata:
        if field.key != key:
            continue
        try:
            return int(field.value)
        except (TypeError, ValueError):
            return 0
    return 0


def _normalized_candidate(reference: SupportReference) -> SupportReference:
    normalized_kind = {
        "retrieval-prior": "memory",
        "memory-summary": "memory",
        "branch-prior": "branch",
        "contradiction-summary": "contradiction",
        "uncertainty-calibration": "uncertainty",
    }.get(reference.reference_kind, reference.reference_kind)
    if normalized_kind == reference.reference_kind:
        return reference
    return SupportReference(
        normalized_kind,
        reference.reference_id,
        tags=reference.tags,
        metadata=reference.metadata,
    )


def _best_match_signal(
    source_refs: tuple[SupportReference, ...],
    candidate_refs: tuple[SupportReference, ...],
    *,
    base_score: float,
) -> float:
    best = 0.0
    for source_ref in source_refs:
        for candidate_ref in candidate_refs:
            normalized_candidate = _normalized_candidate(candidate_ref)
            token_overlap = _reference_tokens(source_ref) & _reference_tokens(normalized_candidate)
            if not token_overlap:
                continue
            best = max(
                best,
                _match_score(source_ref, normalized_candidate, base_score=base_score),
            )
    return _clip_unit(best)


def _target_branch_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    branch_refs = tuple(
        SupportReference("branch", branch_ref, tags=frozenset({"resume-track"}))
        for branch_ref in snapshot.core_snapshot.session.branch_registry
        if branch_ref != "main"
    )
    reminder_refs = tuple(
        SupportReference("reminder", reminder, tags=frozenset({"continuity-reminder"}))
        for reminder in snapshot.core_snapshot.session.reminders
    )
    goal_refs = tuple(
        SupportReference("goal", goal_ref, tags=frozenset({"pending-goal"}))
        for goal_ref in snapshot.core_snapshot.session.pending_goal_refs
    )
    return _dedupe_support_refs(branch_refs + reminder_refs + goal_refs)


def _target_contradiction_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    refs: list[SupportReference] = []
    for record in snapshot.core_snapshot.trace.degradation_records:
        tags = set(record.capability_tags | {record.reason_code})
        for contradiction in record.contradiction_records:
            tags.add(contradiction.source_tag)
            tags.update(contradiction.evidence_tags)
        refs.append(
            SupportReference(
                "contradiction",
                record.reason_code,
                tags=frozenset(tags),
            )
        )
    return _dedupe_support_refs(tuple(refs))


def _target_uncertainty_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    refs = tuple(
        SupportReference("uncertainty", brake_entry, tags=frozenset({"brake-history"}))
        for brake_entry in snapshot.core_snapshot.session.brake_history
    ) + tuple(
        SupportReference("wake", receipt.reason_tag, tags=frozenset({"wake-receipt"}))
        for receipt in snapshot.core_snapshot.trace.wake_receipts
    )
    return _dedupe_support_refs(refs)


def _has_token(signal_tokens: frozenset[str], token: str) -> bool:
    return token in signal_tokens


def _host_reliability_prior(
    snapshot: AugmentedSupportSnapshot,
    signal_profile: SupportMemorySignalProfile,
) -> HostReliabilityPrior:
    degradation_records = snapshot.core_snapshot.trace.degradation_records
    contradiction_counter = sum(
        len(record.contradiction_records) for record in degradation_records
    )
    reason_code_tokens = {
        token
        for record in degradation_records
        for token in record.reason_code.replace("-", "_").split("_")
    }
    constraint_tags = snapshot.core_snapshot.host.constraint_tags
    timeout_rate = 1.0 if "timeout" in reason_code_tokens else 0.0
    degradation_rate = _clip_unit(
        (0.20 * len(degradation_records))
        + (0.15 if constraint_tags else 0.0)
        + (0.10 * signal_profile.burden_penalty)
    )
    capability_availability = 1.0
    if "missing-capability" in constraint_tags:
        capability_availability = 0.35
    elif constraint_tags:
        capability_availability = 0.65
    failure_classes: list[str] = []
    if timeout_rate > 0.0:
        failure_classes.append("timed-out")
    if degradation_records:
        failure_classes.append("degraded")
    if "missing-capability" in constraint_tags:
        failure_classes.append("unsupported")
    source_snapshot_count = _metadata_int(
        snapshot.auxiliary_support.metadata,
        "source_snapshot_count",
    )
    ttl_hours = 72 if source_snapshot_count > 1 else 24
    return HostReliabilityPrior(
        timeout_rate=timeout_rate,
        degradation_rate=degradation_rate,
        capability_availability=capability_availability,
        contradiction_counter=contradiction_counter,
        ttl_hours=ttl_hours,
        last_validated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        probe_failure_classes=tuple(sorted(set(failure_classes))),
    )


def _parse_validated_at(timestamp: str | None) -> datetime | None:
    if timestamp is None:
        return None
    candidate = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _host_reliability_adjustment(
    prior: HostReliabilityPrior,
    *,
    now: datetime | None = None,
) -> _HostReliabilityAdjustment:
    current_time = now or datetime.now(timezone.utc)
    last_validated = _parse_validated_at(prior.last_validated_at)
    if last_validated is not None:
        if current_time - last_validated > timedelta(hours=prior.ttl_hours):
            return _HostReliabilityAdjustment(weight=0.0, ttl_expired=True)

    if prior.contradiction_counter > 0 or prior.probe_failure_classes:
        return _HostReliabilityAdjustment(weight=0.0, invalidated=True)

    weight = _clip_unit(
        (0.70 * prior.capability_availability)
        - (0.45 * prior.timeout_rate)
        - (0.25 * prior.degradation_rate)
    )
    return _HostReliabilityAdjustment(weight=weight)


def _reliability_signal_for_family(
    profile: SupportMemorySignalProfile,
    family: SoftControlFamily,
) -> float:
    if family is SoftControlFamily.BRANCH:
        return max(profile.branch_resume_signal, profile.retrieval_reuse_signal * 0.40)
    if family is SoftControlFamily.CHECK:
        return max(
            profile.contradiction_review_signal,
            profile.uncertainty_calibration_signal * 0.60,
        )
    if family is SoftControlFamily.SEEK_CONTEXT:
        return max(
            profile.retrieval_reuse_signal,
            profile.uncertainty_calibration_signal,
        )
    return 0.0


def _apply_host_reliability_weight(
    family: SoftControlFamily,
    *,
    base_score: float,
    reason_tags: frozenset[str],
    profile: SupportMemorySignalProfile,
    reliability_prior: HostReliabilityPrior,
) -> tuple[float, frozenset[str]]:
    if family not in {
        SoftControlFamily.BRANCH,
        SoftControlFamily.CHECK,
        SoftControlFamily.SEEK_CONTEXT,
    }:
        return base_score, reason_tags

    signal_strength = _reliability_signal_for_family(profile, family)
    adjustment = _host_reliability_adjustment(reliability_prior)
    if adjustment.ttl_expired:
        return base_score, reason_tags | frozenset({"q_mem-host:ttl-expired"})
    if adjustment.invalidated:
        return base_score, reason_tags | frozenset({"q_mem-host:contradiction-invalidated"})
    if base_score <= 0.0 or signal_strength <= 0.0 or adjustment.weight <= 0.0:
        return base_score, reason_tags | frozenset({"q_mem-host:reliability-zeroed"})

    reliability_bonus = 0.36 * adjustment.weight * max(signal_strength, 0.20)
    adjusted_score = _clip_prior_score(base_score + reliability_bonus)
    return adjusted_score, reason_tags | frozenset({"q_mem-host:reliability-active"})


@dataclass(frozen=True, slots=True)
class SupportMemorySignalProfile:
    retrieval_reuse_signal: float
    branch_resume_signal: float
    contradiction_review_signal: float
    uncertainty_calibration_signal: float
    burden_penalty: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "retrieval_reuse_signal",
            _clip_unit(self.retrieval_reuse_signal),
        )
        object.__setattr__(
            self,
            "branch_resume_signal",
            _clip_unit(self.branch_resume_signal),
        )
        object.__setattr__(
            self,
            "contradiction_review_signal",
            _clip_unit(self.contradiction_review_signal),
        )
        object.__setattr__(
            self,
            "uncertainty_calibration_signal",
            _clip_unit(self.uncertainty_calibration_signal),
        )
        object.__setattr__(
            self,
            "burden_penalty",
            _clip_unit(self.burden_penalty),
        )


def _build_signal_profile(snapshot: AugmentedSupportSnapshot) -> SupportMemorySignalProfile:
    appendix = snapshot.auxiliary_support
    derived_refs = appendix.derived_support_refs

    retrieval_refs = _refs_by_kind(derived_refs, "memory", "artifact", "result-artifact")
    branch_candidate_refs = _refs_by_kind(derived_refs, "branch", "memory", "artifact")
    contradiction_refs = _refs_by_kind(derived_refs, "contradiction")
    uncertainty_refs = _refs_by_kind(derived_refs, "uncertainty", "wake")

    retrieval_signal = _best_match_signal(
        _source_refs_for_retrieval(snapshot.core_snapshot),
        retrieval_refs,
        base_score=0.18,
    )

    branch_signal = _best_match_signal(
        _target_branch_refs(snapshot),
        branch_candidate_refs,
        base_score=0.16,
    )
    if branch_signal > 0.0 and snapshot.core_snapshot.session.reminders:
        branch_signal = _clip_unit(branch_signal + 0.05)

    contradiction_signal = _best_match_signal(
        _target_contradiction_refs(snapshot),
        contradiction_refs,
        base_score=0.20,
    )
    if contradiction_signal > 0.0 and snapshot.core_snapshot.trace.degradation_records:
        contradiction_signal = _clip_unit(contradiction_signal + 0.15)

    uncertainty_signal = _best_match_signal(
        _target_uncertainty_refs(snapshot),
        uncertainty_refs,
        base_score=0.18,
    )
    guarded_history = {
        entry
        for entry in snapshot.core_snapshot.session.brake_history
        if entry in {"guarded", "latched"}
    }
    if uncertainty_signal > 0.0 and guarded_history:
        uncertainty_signal = _clip_unit(uncertainty_signal + 0.12)
    if uncertainty_signal > 0.0 and snapshot.core_snapshot.trace.wake_receipts:
        uncertainty_signal = _clip_unit(uncertainty_signal + 0.08)

    token_pool = frozenset(
        token
        for reference in derived_refs
        for token in _reference_tokens(reference)
    )
    source_snapshot_count = _metadata_int(appendix.metadata, "source_snapshot_count")
    fanout_penalty = max(0.0, 0.05 * (len(derived_refs) - 4))
    source_penalty = max(0.0, 0.10 * (source_snapshot_count - 1))
    burden_tag_penalty = 0.15 if _has_token(token_pool, "burden") else 0.0
    drift_tag_penalty = 0.10 if _has_token(token_pool, "drift") else 0.0
    burden_penalty = _clip_unit(
        fanout_penalty + source_penalty + burden_tag_penalty + drift_tag_penalty
    )

    return SupportMemorySignalProfile(
        retrieval_reuse_signal=retrieval_signal,
        branch_resume_signal=branch_signal,
        contradiction_review_signal=contradiction_signal,
        uncertainty_calibration_signal=uncertainty_signal,
        burden_penalty=burden_penalty,
    )


def _reason_tags(
    profile: SupportMemorySignalProfile,
    *,
    include_retrieval: bool = False,
    include_branch: bool = False,
    include_contradiction: bool = False,
    include_uncertainty: bool = False,
) -> frozenset[str]:
    tags = {"q_mem:active"}
    if include_retrieval and profile.retrieval_reuse_signal > 0.0:
        tags.add("q_mem-signal:retrieval")
    if include_branch and profile.branch_resume_signal > 0.0:
        tags.add("q_mem-signal:branch")
    if include_contradiction and profile.contradiction_review_signal > 0.0:
        tags.add("q_mem-signal:contradiction")
    if include_uncertainty and profile.uncertainty_calibration_signal > 0.0:
        tags.add("q_mem-signal:uncertainty")
    if profile.burden_penalty > 0.0:
        tags.add("q_mem-penalty:burden")
    return frozenset(tags)


def build_support_memory_prior_appendix(
    snapshot: AugmentedSupportSnapshot,
    *,
    enable_host_reliability: bool = True,
) -> SupportMemoryPriorAppendix:
    if not isinstance(snapshot, AugmentedSupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_support_memory_prior_appendix() requires AugmentedSupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(enable_host_reliability, bool):
        actual_type = type(enable_host_reliability).__name__
        raise TypeError(
            "build_support_memory_prior_appendix().enable_host_reliability must be bool, "
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
    branch_refs = _refs_by_kind(derived_refs, "branch")
    retrieval_refs = _refs_by_kind(derived_refs, "memory", "artifact")
    contradiction_refs = _refs_by_kind(derived_refs, "contradiction")
    uncertainty_refs = _refs_by_kind(derived_refs, "uncertainty", "wake")
    signal_profile = _build_signal_profile(snapshot)
    reliability_prior = _host_reliability_prior(snapshot, signal_profile)

    branch_base_score = _clip_prior_score(
        (0.55 * signal_profile.branch_resume_signal)
        + (0.15 * signal_profile.retrieval_reuse_signal)
        - (0.25 * signal_profile.burden_penalty)
    )
    branch_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_branch=True,
    )
    if enable_host_reliability:
        branch_score, branch_reason_tags = _apply_host_reliability_weight(
            SoftControlFamily.BRANCH,
            base_score=branch_base_score,
            reason_tags=branch_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
        )
    else:
        branch_score = branch_base_score

    check_base_score = _clip_prior_score(
        (0.50 * signal_profile.contradiction_review_signal)
        + (0.20 * signal_profile.uncertainty_calibration_signal)
        + (0.10 * signal_profile.retrieval_reuse_signal)
        - (0.15 * signal_profile.burden_penalty)
    )
    check_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_contradiction=True,
        include_uncertainty=True,
    )
    if enable_host_reliability:
        check_score, check_reason_tags = _apply_host_reliability_weight(
            SoftControlFamily.CHECK,
            base_score=check_base_score,
            reason_tags=check_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
        )
    else:
        check_score = check_base_score

    seek_context_base_score = _clip_prior_score(
        (0.35 * signal_profile.retrieval_reuse_signal)
        + (0.25 * signal_profile.uncertainty_calibration_signal)
        - (0.15 * signal_profile.burden_penalty)
    )
    seek_context_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_uncertainty=True,
    )
    if enable_host_reliability:
        seek_context_score, seek_context_reason_tags = _apply_host_reliability_weight(
            SoftControlFamily.SEEK_CONTEXT,
            base_score=seek_context_base_score,
            reason_tags=seek_context_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
        )
    else:
        seek_context_score = seek_context_base_score

    scores = (
        SupportMemoryPriorScore(
            family=SoftControlFamily.NEUTRAL,
            score=0.0,
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRANCH,
            score=branch_score,
            reason_tags=branch_reason_tags,
            support_refs=branch_refs + retrieval_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.CHECK,
            score=check_score,
            reason_tags=check_reason_tags,
            support_refs=contradiction_refs + uncertainty_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.REDIRECT,
            score=_clip_prior_score(
                (0.30 * signal_profile.retrieval_reuse_signal)
                + (0.20 * signal_profile.branch_resume_signal)
                + (0.10 * signal_profile.contradiction_review_signal)
                - (0.20 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_retrieval=True,
                include_branch=True,
                include_contradiction=True,
            ),
            support_refs=branch_refs[:1] + retrieval_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.SEEK_CONTEXT,
            score=seek_context_score,
            reason_tags=seek_context_reason_tags,
            support_refs=uncertainty_refs[:2] + retrieval_refs[:1],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRAKE,
            score=_clip_prior_score(
                (0.35 * signal_profile.contradiction_review_signal)
                + (0.35 * signal_profile.uncertainty_calibration_signal)
                - (0.20 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_contradiction=True,
                include_uncertainty=True,
            ),
            support_refs=contradiction_refs[:2] + uncertainty_refs[:1],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.ESCALATE,
            score=_clip_prior_score(
                (0.20 * signal_profile.contradiction_review_signal)
                + (0.15 * signal_profile.uncertainty_calibration_signal)
                - (0.25 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_contradiction=True,
                include_uncertainty=True,
            ),
            support_refs=contradiction_refs[:1],
        ),
    )
    return SupportMemoryPriorAppendix(
        scores=scores,
        appendix_tags=appendix.derived_tags | frozenset({"q_mem:explicit-aux"}),
        notes=appendix.notes
        + (
            "memory-conditioned priors derived from AUX offline publication",
            "host/tool reliability prior remains explicit, removable, shadow-only, and contradiction-first",
        ),
        metadata=(MetadataField("source", "aux/support-priors"),) + appendix.metadata,
        host_reliability_prior=reliability_prior,
    )


__all__ = ["build_support_memory_prior_appendix"]
