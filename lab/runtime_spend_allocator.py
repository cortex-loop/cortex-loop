"""Internal-only runtime spend allocator over existing train and proof artifacts."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Protocol


ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_SUMMARY_PATH = (
    ROOT / ".cortex" / "live_validation" / "conformance" / "summary.latest.json"
)
OUTPUT_QUALITY_SUMMARY_PATH = (
    ROOT / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json"
)
TRAIN_LOOP_ROOT = ROOT / ".cortex" / "train_loops"
WORKSTREAM_PATH = ROOT / "docs" / "internal" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"

SignalSourceKind = Literal["conformance", "output_quality", "train_loop", "workstream"]
SignalSurface = Literal["operator_cli", "service_api", "none"]
MetricFamily = Literal[
    "pass_rate",
    "repair_conversion",
    "env_blocked",
    "divergence",
    "workflow_block",
]
RecommendationConsequence = Literal["promote", "revise", "cut", "escalate", "keep", "block"]
CandidateKind = Literal["product", "proving_plumbing", "workflow"]


@dataclass(frozen=True, slots=True)
class RuntimeSpendSignal:
    source_kind: SignalSourceKind
    host: str
    surface: SignalSurface
    metric_family: MetricFamily
    consequence: RecommendationConsequence
    summary: str
    artifact_refs: tuple[str, ...]
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("RuntimeSpendSignal.host must be non-empty after trimming.")
        if not self.summary.strip():
            raise ValueError("RuntimeSpendSignal.summary must be non-empty after trimming.")
        if not self.artifact_refs or any(
            not isinstance(ref, str) or not ref.strip() for ref in self.artifact_refs
        ):
            raise ValueError(
                "RuntimeSpendSignal.artifact_refs must contain non-empty references."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "source_kind": self.source_kind,
            "host": self.host,
            "surface": self.surface,
            "metric_family": self.metric_family,
            "consequence": self.consequence,
            "summary": self.summary,
            "artifact_refs": list(self.artifact_refs),
            "payload": dict(self.payload),
        }


@dataclass(frozen=True, slots=True)
class CandidateSpec:
    slug: str
    candidate_kind: CandidateKind
    host: str
    target_metric: str
    runtime_budget: int
    kill_condition: str
    guardrail: str
    proof_commands: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        for label, value in (
            ("slug", self.slug),
            ("host", self.host),
            ("target_metric", self.target_metric),
            ("kill_condition", self.kill_condition),
            ("guardrail", self.guardrail),
            ("rationale", self.rationale),
        ):
            if not value.strip():
                raise ValueError(f"CandidateSpec.{label} must be non-empty after trimming.")
        if self.runtime_budget <= 0:
            raise ValueError("CandidateSpec.runtime_budget must be positive.")
        if not self.proof_commands or any(
            not isinstance(command, str) or not command.strip()
            for command in self.proof_commands
        ):
            raise ValueError(
                "CandidateSpec.proof_commands must contain non-empty commands."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "candidate_kind": self.candidate_kind,
            "host": self.host,
            "target_metric": self.target_metric,
            "runtime_budget": self.runtime_budget,
            "kill_condition": self.kill_condition,
            "guardrail": self.guardrail,
            "proof_commands": list(self.proof_commands),
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class CandidateAssessment:
    spec: CandidateSpec
    consequence: RecommendationConsequence
    rank: int
    reason: str
    supporting_artifact_refs: tuple[str, ...]
    blocked_reasons: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, Any]:
        return {
            **self.spec.as_payload(),
            "consequence": self.consequence,
            "rank": self.rank,
            "reason": self.reason,
            "supporting_artifact_refs": list(self.supporting_artifact_refs),
            "blocked_reasons": list(self.blocked_reasons),
        }


@dataclass(frozen=True, slots=True)
class RuntimeSpendRecommendation:
    host: str
    signals: tuple[RuntimeSpendSignal, ...]
    recommended_candidate: CandidateAssessment
    ranked_candidates: tuple[CandidateAssessment, ...]
    blocked_candidates: tuple[CandidateAssessment, ...]

    @property
    def artifact_refs_used(self) -> tuple[str, ...]:
        refs: set[str] = set()
        for signal in self.signals:
            refs.update(signal.artifact_refs)
        refs.update(self.recommended_candidate.supporting_artifact_refs)
        for candidate in self.blocked_candidates:
            refs.update(candidate.supporting_artifact_refs)
        return tuple(sorted(refs))

    def as_payload(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "recommended_train_slug": self.recommended_candidate.spec.slug,
            "target_metric": self.recommended_candidate.spec.target_metric,
            "runtime_budget": self.recommended_candidate.spec.runtime_budget,
            "kill_condition": self.recommended_candidate.spec.kill_condition,
            "guardrail": self.recommended_candidate.spec.guardrail,
            "proof_commands": list(self.recommended_candidate.spec.proof_commands),
            "artifact_refs_used": list(self.artifact_refs_used),
            "signals": [signal.as_payload() for signal in self.signals],
            "recommended_candidate": self.recommended_candidate.as_payload(),
            "ranked_candidates": [
                candidate.as_payload() for candidate in self.ranked_candidates
            ],
            "blocked_candidates": [
                candidate.as_payload() for candidate in self.blocked_candidates
            ],
        }


class RuntimeSpendSignalLoader(Protocol):
    def load(self, *, repo_root: Path) -> tuple[RuntimeSpendSignal, ...]:
        ...


class OpenAIArtifactSignalLoader:
    """OpenAI-first loader over deterministic local artifact summaries."""

    def load(self, *, repo_root: Path) -> tuple[RuntimeSpendSignal, ...]:
        signals: list[RuntimeSpendSignal] = []
        signals.extend(_load_conformance_signal(repo_root=repo_root))
        signals.extend(_load_output_quality_signal(repo_root=repo_root))
        signals.extend(_load_train_loop_signals(repo_root=repo_root))
        signals.extend(_load_workstream_signals(repo_root=repo_root))
        return tuple(signals)


class RuntimeSpendAllocator:
    """Host-agnostic recommendation law with provider-specific artifact loaders."""

    def __init__(self, *, loaders: dict[str, RuntimeSpendSignalLoader]) -> None:
        if not loaders:
            raise ValueError("RuntimeSpendAllocator.loaders must be non-empty.")
        self._loaders = dict(loaders)

    def recommend(
        self,
        *,
        host: str,
        repo_root: Path = ROOT,
        candidate_specs: tuple[CandidateSpec, ...] | None = None,
    ) -> RuntimeSpendRecommendation:
        loader = self._loaders.get(host)
        if loader is None:
            raise ValueError(f"No runtime spend loader is registered for host: {host}")
        signals = loader.load(repo_root=repo_root)
        specs = candidate_specs or default_candidate_specs(host=host)
        return recommend_from_signals(host=host, signals=signals, candidate_specs=specs)


def default_candidate_specs(*, host: str = "openai") -> tuple[CandidateSpec, ...]:
    if host != "openai":
        raise ValueError("default_candidate_specs currently supports only the OpenAI host.")
    return (
        CandidateSpec(
            slug="real-work-replay-pack-openai",
            candidate_kind="product",
            host="openai",
            target_metric=(
                "repair_conversion_lift_or_first_attempt_failure_replay_coverage"
            ),
            runtime_budget=2,
            kill_condition="cut after 2 non-lift iterations or no clearer divergence classification",
            guardrail=(
                "no regression on accepted verified-work packs and no shipping-truth widening"
            ),
            proof_commands=(
                "python3 -m pytest -q tests/unit/test_cortex_output_quality.py tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py",
                "make -C lab revalidate-openai-operator-cli",
                "python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack verified_work_bookmarks_v1",
                "python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack verified_work_normalize_port_v1",
                "python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack verified_work_feature_flags_v1",
            ),
            rationale=(
                "create a small replayable failure pack from real OpenAI work traces instead of spending more runtime on broad operator watch runs"
            ),
        ),
        CandidateSpec(
            slug="shared-openai-operator-proof-plumbing",
            candidate_kind="proving_plumbing",
            host="openai",
            target_metric="repeat_stable_operator_resume_repair_pressure_proof",
            runtime_budget=2,
            kill_condition="cut after 2 reruns without clearer crash classification",
            guardrail=(
                "no regression on accepted verified-work packs and no Cortex-law reinterpretation"
            ),
            proof_commands=(
                "python3 -m pytest -q tests/unit/test_live_openai_app_server_operator.py tests/unit/test_cortex_conformance.py tests/unit/test_cortex_train_loop.py",
                "python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack verified_work_normalize_port_v1",
                "python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack verified_work_normalize_port_v1",
            ),
            rationale=(
                "open one localized proof-plumbing seam only if the operator resume crash becomes repeatable enough to block honest repair-pressure classification"
            ),
        ),
        CandidateSpec(
            slug="e24-truth-closure",
            candidate_kind="workflow",
            host="openai",
            target_metric="accepted_baseline_and_proving_default_truth_alignment",
            runtime_budget=1,
            kill_condition="cut after one attempt if publication or reconciliation remains externally blocked",
            guardrail=(
                "keep shipping truth unchanged while reconciling local accepted history and proving-default truth"
            ),
            proof_commands=(
                "python3 -m pytest -q tests/unit/test_cortex_conformance.py tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py",
                "python3 lab/cortex_train_loop.py --train conformance-summary-truth",
            ),
            rationale=(
                "reconcile the review-branch and local accepted-history blockage only after the higher-yield product-bearing seam is chosen"
            ),
        ),
    )


def recommend_from_signals(
    *,
    host: str,
    signals: tuple[RuntimeSpendSignal, ...],
    candidate_specs: tuple[CandidateSpec, ...],
) -> RuntimeSpendRecommendation:
    if not candidate_specs:
        raise ValueError("candidate_specs must be non-empty.")
    ranked: list[CandidateAssessment] = []
    for spec in candidate_specs:
        score, reason, refs = _candidate_score(spec=spec, signals=signals)
        ranked.append(
            CandidateAssessment(
                spec=spec,
                consequence="keep",
                rank=score,
                reason=reason,
                supporting_artifact_refs=refs,
            )
        )
    ranked.sort(key=lambda candidate: (-candidate.rank, candidate.spec.runtime_budget, candidate.spec.slug))
    recommended = ranked[0]
    ranked[0] = CandidateAssessment(
        spec=recommended.spec,
        consequence="promote",
        rank=recommended.rank,
        reason=recommended.reason,
        supporting_artifact_refs=recommended.supporting_artifact_refs,
    )
    blocked = blocked_candidate_assessments(host=host, signals=signals)
    return RuntimeSpendRecommendation(
        host=host,
        signals=signals,
        recommended_candidate=ranked[0],
        ranked_candidates=tuple(ranked),
        blocked_candidates=blocked,
    )


def blocked_candidate_assessments(
    *,
    host: str,
    signals: tuple[RuntimeSpendSignal, ...],
) -> tuple[CandidateAssessment, ...]:
    if host != "openai":
        raise ValueError("blocked_candidate_assessments currently supports only the OpenAI host.")

    workstream_refs = _collect_refs(
        signals,
        lambda signal: signal.source_kind == "workstream",
    )
    blocked: list[CandidateAssessment] = []
    if _has_service_spend_block(signals):
        blocked.append(
            CandidateAssessment(
                spec=CandidateSpec(
                    slug="openai-service-api-runtime-train",
                    candidate_kind="workflow",
                    host="openai",
                    target_metric="service_api_runtime_progress",
                    runtime_budget=1,
                    kill_condition="blocked while service spend remains deferred",
                    guardrail="do not reopen service spend by habit",
                    proof_commands=("python3 lab/cortex_conformance.py --mode active --brain openai",),
                    rationale="historical service-lane truth must not be reopened by habit",
                ),
                consequence="block",
                rank=0,
                reason="current workstream defers new OpenAI service_api spend by policy",
                supporting_artifact_refs=workstream_refs,
                blocked_reasons=("service_api spend remains deferred under current policy",),
            )
        )
    if _has_e23_keep_signal(signals):
        blocked.append(
            CandidateAssessment(
                spec=CandidateSpec(
                    slug="e23-broad-watch-reopen",
                    candidate_kind="workflow",
                    host="openai",
                    target_metric="broad_operator_watch_signal",
                    runtime_budget=1,
                    kill_condition="blocked while E23 remains locally kept",
                    guardrail="do not reopen broad E23 watch surfaces by habit",
                    proof_commands=("make -C lab live-openai-operator-repair-pressure",),
                    rationale="E23 is already locally kept on the operator proving lane",
                ),
                consequence="block",
                rank=0,
                reason="E23 is locally kept and broader watch reruns are explicitly cut",
                supporting_artifact_refs=workstream_refs,
                blocked_reasons=("do not reopen E23 broad watch surfaces by habit",),
            )
        )
    blocked.extend(
        (
            CandidateAssessment(
                spec=CandidateSpec(
                    slug="host-expansion-train",
                    candidate_kind="workflow",
                    host="openai",
                    target_metric="cross_host_shipping_scope",
                    runtime_budget=1,
                    kill_condition="blocked while current product scope remains OpenAI-only",
                    guardrail="do not widen current product scope without a separate host train",
                    proof_commands=("python3 lab/cortex_conformance.py --mode active",),
                    rationale="host expansion is outside the current product scope",
                ),
                consequence="block",
                rank=0,
                reason="current product scope remains OpenAI-only and host expansion requires a separate train",
                supporting_artifact_refs=workstream_refs,
                blocked_reasons=("host expansion is intentionally outside the current product scope",),
            ),
            CandidateAssessment(
                spec=CandidateSpec(
                    slug="repeated-failure-inhibition-train",
                    candidate_kind="workflow",
                    host="openai",
                    target_metric="repeated_failure_inhibition",
                    runtime_budget=1,
                    kill_condition="blocked until new evidence earns repeated-failure inhibition",
                    guardrail="do not promote repeated-failure inhibition without new evidence",
                    proof_commands=("python3 lab/cortex_conformance.py --mode repair-pressure --brain openai",),
                    rationale="repeated-failure inhibition remains deferred on the accepted line",
                ),
                consequence="block",
                rank=0,
                reason="repeated-failure inhibition remains explicitly deferred until new evidence earns it",
                supporting_artifact_refs=workstream_refs,
                blocked_reasons=("repeated-failure inhibition remains deferred",),
            ),
            CandidateAssessment(
                spec=CandidateSpec(
                    slug="carrier-inference-train",
                    candidate_kind="workflow",
                    host="openai",
                    target_metric="automatic_carrier_selection",
                    runtime_budget=1,
                    kill_condition="blocked until new evidence earns carrier inference",
                    guardrail="do not promote carrier inference without new evidence",
                    proof_commands=("python3 lab/cortex_conformance.py --mode active --brain openai",),
                    rationale="carrier inference remains explicitly deferred on the accepted line",
                ),
                consequence="block",
                rank=0,
                reason="carrier inference remains explicitly deferred until new evidence earns it",
                supporting_artifact_refs=workstream_refs,
                blocked_reasons=("carrier inference remains deferred",),
            ),
        )
    )
    return tuple(blocked)


def build_default_allocator() -> RuntimeSpendAllocator:
    return RuntimeSpendAllocator(loaders={"openai": OpenAIArtifactSignalLoader()})


def recommend_runtime_spend(
    *,
    host: str = "openai",
    repo_root: Path = ROOT,
) -> RuntimeSpendRecommendation:
    return build_default_allocator().recommend(host=host, repo_root=repo_root)


def render_runtime_spend_markdown(recommendation: RuntimeSpendRecommendation) -> str:
    lines = [
        f"# Runtime Spend Recommendation: {recommendation.host}",
        "",
        "## Recommendation",
        "",
        f"- recommended_train_slug: `{recommendation.recommended_candidate.spec.slug}`",
        f"- target_metric: `{recommendation.recommended_candidate.spec.target_metric}`",
        f"- runtime_budget: `{recommendation.recommended_candidate.spec.runtime_budget}`",
        f"- kill_condition: {recommendation.recommended_candidate.spec.kill_condition}",
        f"- guardrail: {recommendation.recommended_candidate.spec.guardrail}",
        f"- rationale: {recommendation.recommended_candidate.reason}",
        "",
        "## Proof Commands",
        "",
    ]
    lines.extend(f"- `{command}`" for command in recommendation.recommended_candidate.spec.proof_commands)
    lines.extend(["", "## Ranked Candidates", ""])
    for candidate in recommendation.ranked_candidates:
        lines.extend(
            [
                f"### {candidate.spec.slug}",
                "",
                f"- consequence: `{candidate.consequence}`",
                f"- rank: `{candidate.rank}`",
                f"- candidate_kind: `{candidate.spec.candidate_kind}`",
                f"- runtime_budget: `{candidate.spec.runtime_budget}`",
                f"- reason: {candidate.reason}",
                f"- supporting_artifact_refs: `{', '.join(candidate.supporting_artifact_refs)}`",
                "",
            ]
        )
    lines.extend(["## Blocked Candidates", ""])
    for candidate in recommendation.blocked_candidates:
        blocked_reasons = ", ".join(candidate.blocked_reasons) or candidate.reason
        lines.extend(
            [
                f"### {candidate.spec.slug}",
                "",
                f"- consequence: `{candidate.consequence}`",
                f"- reason: {candidate.reason}",
                f"- blocked_reasons: `{blocked_reasons}`",
                f"- supporting_artifact_refs: `{', '.join(candidate.supporting_artifact_refs)}`",
                "",
            ]
        )
    lines.extend(["## Artifact Refs Used", ""])
    lines.extend(f"- `{ref}`" for ref in recommendation.artifact_refs_used)
    return "\n".join(lines).rstrip() + "\n"


def _candidate_score(
    *,
    spec: CandidateSpec,
    signals: tuple[RuntimeSpendSignal, ...],
) -> tuple[int, str, tuple[str, ...]]:
    refs: list[str] = []
    score = _candidate_kind_weight(spec.candidate_kind)

    if spec.slug == "real-work-replay-pack-openai":
        if _has_e23_keep_signal(signals):
            score += 20
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: signal.source_kind == "workstream",
                )
            )
        if _has_repair_yield_gap(signals):
            score += 90
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: signal.payload.get("train_name")
                    == "verified-work-repair-yield-openai",
                )
            )
        if _has_zero_lift_output_quality_env_block(signals):
            score += 80
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: signal.source_kind == "output_quality",
                )
            )
        score -= spec.runtime_budget * 2
        reason = (
            "current accepted packs do not produce enough natural repair opportunities and the broad operator output-quality watch is env_blocked / zero-lift, so the next train should create a smaller replayable failure pack"
        )
        return score, reason, tuple(sorted(set(refs)))

    if spec.slug == "shared-openai-operator-proof-plumbing":
        if _has_repeated_plumbing_crash(signals):
            score += 140
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: bool(signal.payload.get("repeated_plumbing_crash")),
                )
            )
            reason = (
                "a repeatable operator-resume plumbing defect is now the highest-yield blocker on the OpenAI proving lane"
            )
        else:
            score += 5
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: signal.source_kind == "workstream"
                    and "payload-sanitization crash" in signal.summary,
                )
            )
            reason = (
                "shared proof plumbing stays available as a localized seam, but the current crash evidence is unreproduced and does not beat the replay-pack train"
            )
        score -= spec.runtime_budget
        return score, reason, tuple(sorted(set(refs)))

    if spec.slug == "e24-truth-closure":
        if _has_publication_block(signals):
            score += 50
            refs.extend(
                _collect_refs(
                    signals,
                    lambda signal: bool(signal.payload.get("publication_blocked")),
                )
            )
        score -= spec.runtime_budget
        reason = (
            "truth closure remains useful, but it is workflow-only and should follow the higher-yield product-bearing replay-pack train"
        )
        return score, reason, tuple(sorted(set(refs)))

    raise ValueError(f"Unsupported candidate slug: {spec.slug}")


def _candidate_kind_weight(candidate_kind: CandidateKind) -> int:
    return {
        "product": 200,
        "proving_plumbing": 120,
        "workflow": 60,
    }[candidate_kind]


def _load_conformance_signal(*, repo_root: Path) -> list[RuntimeSpendSignal]:
    path = repo_root / CONFORMANCE_SUMMARY_PATH.relative_to(ROOT)
    if not path.exists():
        return [
            RuntimeSpendSignal(
                source_kind="conformance",
                host="openai",
                surface="none",
                metric_family="workflow_block",
                consequence="block",
                summary="conformance summary.latest is missing",
                artifact_refs=(_relpath(repo_root, path),),
                payload={"missing": True},
            )
        ]
    summary = json.loads(path.read_text(encoding="utf-8"))
    openai_result = _result_for_brain(summary, brain="openai")
    status = openai_result.get("status") if isinstance(openai_result, dict) else None
    artifact_refs = [_relpath(repo_root, path)]
    artifact_relpath = (
        openai_result.get("artifact_relpath") if isinstance(openai_result, dict) else None
    )
    if isinstance(artifact_relpath, str) and artifact_relpath.strip():
        artifact_refs.append(artifact_relpath)
    surface = _surface_from_value(
        _nested_string(summary, ("proving_truth", "active_default"))
    )
    consequence: RecommendationConsequence = "promote" if status == "conformant" else "keep"
    return [
        RuntimeSpendSignal(
            source_kind="conformance",
            host="openai",
            surface=surface,
            metric_family="pass_rate",
            consequence=consequence,
            summary=(
                f"current OpenAI conformance summary reads {status or 'unknown'} on the active proving-default lane"
            ),
            artifact_refs=tuple(artifact_refs),
            payload={
                "status": status,
                "next_decision": summary.get("next_decision"),
                "active_default": _nested_string(summary, ("proving_truth", "active_default")),
                "runtime_claim": _nested_string(summary, ("product_truth", "runtime_claim")),
            },
        )
    ]


def _load_output_quality_signal(*, repo_root: Path) -> list[RuntimeSpendSignal]:
    path = repo_root / OUTPUT_QUALITY_SUMMARY_PATH.relative_to(ROOT)
    if not path.exists():
        return [
            RuntimeSpendSignal(
                source_kind="output_quality",
                host="openai",
                surface="none",
                metric_family="workflow_block",
                consequence="block",
                summary="output-quality summary.latest is missing",
                artifact_refs=(_relpath(repo_root, path),),
                payload={"missing": True},
            )
        ]
    summary = json.loads(path.read_text(encoding="utf-8"))
    objective_counts = summary.get("aggregate_objective_pass_count", {})
    hidden_counts = summary.get("aggregate_hidden_quality_pass_count", {})
    pairwise_summary = summary.get("pairwise_summary", {})
    zero_lift = (
        isinstance(objective_counts, dict)
        and isinstance(hidden_counts, dict)
        and int(objective_counts.get("cortex", 0) or 0) == 0
        and int(hidden_counts.get("cortex", 0) or 0) == 0
        and _pairwise_payload(pairwise_summary, "cortex_vs_raw").get("wins", 0) == 0
        and _pairwise_payload(pairwise_summary, "cortex_vs_tooling_only").get("wins", 0) == 0
    )
    env_blocked = bool(summary.get("env_blocked"))
    consequence: RecommendationConsequence = "cut" if env_blocked else "keep"
    return [
        RuntimeSpendSignal(
            source_kind="output_quality",
            host="openai",
            surface=_surface_from_value(summary.get("surface")),
            metric_family="env_blocked" if env_blocked else "pass_rate",
            consequence=consequence,
            summary=(
                "broad OpenAI operator output-quality watch is env_blocked with zero objective and hidden-quality passes"
                if env_blocked and zero_lift
                else "current OpenAI output-quality summary exists without a repeated env block"
            ),
            artifact_refs=(
                _relpath(repo_root, path),
                str(summary.get("artifact_root") or _relpath(repo_root, path)),
            ),
            payload={
                "env_blocked": env_blocked,
                "zero_lift": zero_lift,
                "aggregate_objective_pass_count": objective_counts,
                "aggregate_hidden_quality_pass_count": hidden_counts,
            },
        )
    ]


def _load_train_loop_signals(*, repo_root: Path) -> list[RuntimeSpendSignal]:
    signals: list[RuntimeSpendSignal] = []
    root = repo_root / TRAIN_LOOP_ROOT.relative_to(ROOT)
    if not root.exists():
        return signals
    for summary_path in sorted(root.glob("*/summary.json")):
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        train_name = str(summary.get("train_name") or summary_path.parent.name)
        host = _host_from_train_name(train_name)
        metric_family = _metric_family_from_train_summary(summary)
        consequence = _consequence_from_train_summary(summary)
        summary_text = f"{train_name} currently reads {consequence}"
        payload: dict[str, Any] = {
            "train_name": train_name,
            "final_decision": summary.get("final_decision"),
            "primary_metric": summary.get("primary_metric"),
        }
        if train_name == "verified-work-repair-yield-openai":
            repair_opportunities = int(
                (summary.get("baseline_result") or {}).get("repair_opportunities", 0) or 0
            )
            payload["repair_opportunities"] = repair_opportunities
            if (
                summary.get("final_decision") == "escalate"
                and repair_opportunities == 0
            ):
                summary_text = (
                    "verified-work repair-yield train escalated because the accepted packs produced zero natural repair opportunities"
                )
        signals.append(
            RuntimeSpendSignal(
                source_kind="train_loop",
                host=host,
                surface="none",
                metric_family=metric_family,
                consequence=consequence,
                summary=summary_text,
                artifact_refs=(_relpath(repo_root, summary_path),),
                payload=payload,
            )
        )
    return signals


def _load_workstream_signals(*, repo_root: Path) -> list[RuntimeSpendSignal]:
    path = repo_root / WORKSTREAM_PATH.relative_to(ROOT)
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    refs = (_relpath(repo_root, path),)
    signals: list[RuntimeSpendSignal] = []
    if "treat E23 as a local `keep`" in text:
        signals.append(
            RuntimeSpendSignal(
                source_kind="workstream",
                host="openai",
                surface="operator_cli",
                metric_family="divergence",
                consequence="keep",
                summary="E23 is locally kept on the OpenAI operator_cli proving lane and should not be reopened by habit",
                artifact_refs=refs,
                payload={"e23_local_keep": True},
            )
        )
    if "keep new OpenAI `service_api` spend deferred under the current policy" in text:
        signals.append(
            RuntimeSpendSignal(
                source_kind="workstream",
                host="openai",
                surface="service_api",
                metric_family="workflow_block",
                consequence="block",
                summary="new OpenAI service_api spend remains deferred under the current policy",
                artifact_refs=refs,
                payload={"service_spend_deferred": True},
            )
        )
    if "publication and reconciliation remain blocked" in text:
        signals.append(
            RuntimeSpendSignal(
                source_kind="workstream",
                host="openai",
                surface="none",
                metric_family="workflow_block",
                consequence="revise",
                summary="publication and reconciliation remain blocked on the local accepted-history line",
                artifact_refs=refs,
                payload={"publication_blocked": True},
            )
        )
    if "payload-sanitization crash" in text:
        unreproduced = "did not recur on two fresh direct reruns" in text
        signals.append(
            RuntimeSpendSignal(
                source_kind="workstream",
                host="openai",
                surface="operator_cli",
                metric_family="divergence",
                consequence="keep" if unreproduced else "revise",
                summary=(
                    "operator-resume payload-sanitization crash is currently unreproduced shared proof-plumbing noise"
                    if unreproduced
                    else "operator-resume payload-sanitization crash remains an unresolved shared proof-plumbing risk"
                ),
                artifact_refs=refs,
                payload={
                    "payload_sanitization_crash": True,
                    "unreproduced_plumbing_crash": unreproduced,
                    "repeated_plumbing_crash": not unreproduced,
                },
            )
        )
    return signals


def _result_for_brain(summary: dict[str, Any], *, brain: str) -> dict[str, Any] | None:
    results = summary.get("results")
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("brain") == brain:
            return result
    return None


def _nested_string(payload: dict[str, Any], path: tuple[str, ...]) -> str | None:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, str) and current.strip() else None


def _surface_from_value(value: Any) -> SignalSurface:
    if isinstance(value, str):
        if value.endswith(":operator_cli") or value == "operator_cli":
            return "operator_cli"
        if value.endswith(":service_api") or value == "service_api":
            return "service_api"
    return "none"


def _pairwise_payload(pairwise_summary: Any, pair_name: str) -> dict[str, int]:
    if not isinstance(pairwise_summary, dict):
        return {"wins": 0, "losses": 0, "ties": 0}
    payload = pairwise_summary.get(pair_name)
    if not isinstance(payload, dict):
        return {"wins": 0, "losses": 0, "ties": 0}
    return {
        "wins": int(payload.get("wins", 0) or 0),
        "losses": int(payload.get("losses", 0) or 0),
        "ties": int(payload.get("ties", 0) or 0),
    }


def _host_from_train_name(train_name: str) -> str:
    match = re.search(r"(openai|claude|gemini)", train_name)
    return match.group(1) if match is not None else "unknown"


def _metric_family_from_train_summary(summary: dict[str, Any]) -> MetricFamily:
    train_name = str(summary.get("train_name") or "")
    primary_metric = str(summary.get("primary_metric") or "")
    text = f"{train_name} {primary_metric}"
    if "repair" in text:
        return "repair_conversion"
    if "pass" in text or "breadth" in text or "pairwise" in text:
        return "pass_rate"
    if "env" in text:
        return "env_blocked"
    return "divergence"


def _consequence_from_train_summary(summary: dict[str, Any]) -> RecommendationConsequence:
    final_decision = summary.get("final_decision")
    if final_decision in {"promote", "revise", "cut", "escalate", "keep", "block"}:
        return final_decision
    return "keep"


def _collect_refs(
    signals: tuple[RuntimeSpendSignal, ...],
    predicate,
) -> tuple[str, ...]:
    refs: set[str] = set()
    for signal in signals:
        if predicate(signal):
            refs.update(signal.artifact_refs)
    return tuple(sorted(refs))


def _has_repair_yield_gap(signals: tuple[RuntimeSpendSignal, ...]) -> bool:
    return any(
        signal.payload.get("train_name") == "verified-work-repair-yield-openai"
        and signal.consequence == "escalate"
        and int(signal.payload.get("repair_opportunities", 1) or 0) == 0
        for signal in signals
    )


def _has_zero_lift_output_quality_env_block(
    signals: tuple[RuntimeSpendSignal, ...],
) -> bool:
    return any(
        signal.source_kind == "output_quality"
        and bool(signal.payload.get("env_blocked"))
        and bool(signal.payload.get("zero_lift"))
        for signal in signals
    )


def _has_e23_keep_signal(signals: tuple[RuntimeSpendSignal, ...]) -> bool:
    return any(bool(signal.payload.get("e23_local_keep")) for signal in signals)


def _has_service_spend_block(signals: tuple[RuntimeSpendSignal, ...]) -> bool:
    return any(bool(signal.payload.get("service_spend_deferred")) for signal in signals)


def _has_publication_block(signals: tuple[RuntimeSpendSignal, ...]) -> bool:
    return any(bool(signal.payload.get("publication_blocked")) for signal in signals)


def _has_repeated_plumbing_crash(signals: tuple[RuntimeSpendSignal, ...]) -> bool:
    return any(bool(signal.payload.get("repeated_plumbing_crash")) for signal in signals)


def _relpath(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/runtime_spend_allocator.py",
        description="Recommend the next runtime-spend train from deterministic local artifact summaries.",
    )
    parser.add_argument("--host", default="openai")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
    )
    args = parser.parse_args(argv)
    recommendation = recommend_runtime_spend(
        host=args.host,
        repo_root=Path(args.repo_root).resolve(),
    )
    if args.format == "markdown":
        print(render_runtime_spend_markdown(recommendation), end="")
    else:
        print(json.dumps(recommendation.as_payload(), indent=2, sort_keys=True))
    return 0


__all__ = [
    "CandidateAssessment",
    "CandidateKind",
    "CandidateSpec",
    "MetricFamily",
    "OpenAIArtifactSignalLoader",
    "RecommendationConsequence",
    "RuntimeSpendAllocator",
    "RuntimeSpendRecommendation",
    "RuntimeSpendSignal",
    "RuntimeSpendSignalLoader",
    "SignalSourceKind",
    "SignalSurface",
    "blocked_candidate_assessments",
    "build_default_allocator",
    "default_candidate_specs",
    "main",
    "render_runtime_spend_markdown",
    "recommend_from_signals",
    "recommend_runtime_spend",
]
