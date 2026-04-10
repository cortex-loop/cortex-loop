"""Maintainer-only closed-loop recorder for bounded Cortex train iterations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lab.cortex_conformance as cortex_conformance  # noqa: E402
from lab.causal_contribution_map import (  # noqa: E402
    ContributionRunReading,
    OutputQualityMetrics,
    VerifiedWorkMetrics,
    classify_component,
    has_material_delta,
    render_causal_map_note,
)
from lab.live_validation_common import now_utc_iso, run_command, write_json, write_text  # noqa: E402


LoopClass = Literal[
    "deterministic",
    "shared_verification_plumbing",
    "timing_env_sensitive",
]
LoopDecision = Literal["promote", "revise", "cut", "escalate"]

TRAIN_LOOP_ROOT = ROOT / ".cortex" / "train_loops"
PHASE_GATES_PATH = ROOT / "docs" / "internal" / "CORTEX_V2_PHASE_GATES_2.md"
CONFORMANCE_SUMMARY_PATH = (
    ROOT / ".cortex" / "live_validation" / "conformance" / "summary.latest.json"
)
OPENAI_BREADTH_PACKS = (
    cortex_conformance.ACTIVE_CONTRACT_PACK,
    cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK,
    cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK,
)
REPAIR_GUARDRAIL_PACK = cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK
OPENAI_PRODUCT_RUNTIME_CLAIM = cortex_conformance.OPENAI_PRODUCT_RUNTIME_CLAIM
OPENAI_ACTIVE_PROVING_DEFAULT = cortex_conformance.OPENAI_ACTIVE_PROVING_DEFAULT


@dataclass(frozen=True, slots=True)
class LoopIteration:
    index: int
    candidate_label: str
    proof_commands: tuple[str, ...]
    primary_metric_before: int
    primary_metric_after: int
    guardrail_ok: bool
    localized_failure: bool
    better_classification: bool
    budget_remaining: int
    decision: LoopDecision
    reason: str
    command_results: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    escalation_reasons: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.index <= 0:
            raise ValueError("LoopIteration.index must be positive.")
        if not self.candidate_label.strip():
            raise ValueError("LoopIteration.candidate_label must be non-empty after trimming.")
        if not self.reason.strip():
            raise ValueError("LoopIteration.reason must be non-empty after trimming.")

    def as_payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "candidate_label": self.candidate_label,
            "proof_commands": list(self.proof_commands),
            "primary_metric_before": self.primary_metric_before,
            "primary_metric_after": self.primary_metric_after,
            "guardrail_ok": self.guardrail_ok,
            "localized_failure": self.localized_failure,
            "better_classification": self.better_classification,
            "budget_remaining": self.budget_remaining,
            "decision": self.decision,
            "reason": self.reason,
            "command_results": list(self.command_results),
            "escalation_reasons": list(self.escalation_reasons),
        }


@dataclass(frozen=True, slots=True)
class TrainLoopRecord:
    train_name: str
    seam_class: LoopClass
    cortex_invariant: str
    brain_wiring_touched: str
    borrowed_mechanism: str
    contract_pack: str
    conformance_surfaces: tuple[str, ...]
    baseline_result: dict[str, Any]
    primary_metric: str
    guardrail_metric: str
    baseline_proof_set: tuple[str, ...]
    iteration_budget: int
    rollback_surface: str
    escalation_triggers: tuple[str, ...]
    analysis: dict[str, Any] = field(default_factory=dict)
    iterations: tuple[LoopIteration, ...] = field(default_factory=tuple)
    final_decision: LoopDecision | None = None

    def __post_init__(self) -> None:
        for label, value in (
            ("train_name", self.train_name),
            ("cortex_invariant", self.cortex_invariant),
            ("brain_wiring_touched", self.brain_wiring_touched),
            ("borrowed_mechanism", self.borrowed_mechanism),
            ("contract_pack", self.contract_pack),
            ("primary_metric", self.primary_metric),
            ("guardrail_metric", self.guardrail_metric),
            ("rollback_surface", self.rollback_surface),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"TrainLoopRecord.{label} must be non-empty after trimming.")
        if self.iteration_budget <= 0:
            raise ValueError("TrainLoopRecord.iteration_budget must be positive.")
        if not self.conformance_surfaces or any(
            not isinstance(surface, str) or not surface.strip()
            for surface in self.conformance_surfaces
        ):
            raise ValueError(
                "TrainLoopRecord.conformance_surfaces must contain non-empty labels."
            )
        if not self.baseline_proof_set or any(
            not isinstance(command, str) or not command.strip()
            for command in self.baseline_proof_set
        ):
            raise ValueError(
                "TrainLoopRecord.baseline_proof_set must contain non-empty commands."
            )
        if not self.escalation_triggers or any(
            not isinstance(trigger, str) or not trigger.strip()
            for trigger in self.escalation_triggers
        ):
            raise ValueError(
                "TrainLoopRecord.escalation_triggers must contain non-empty triggers."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "train_name": self.train_name,
            "seam_class": self.seam_class,
            "cortex_invariant": self.cortex_invariant,
            "brain_wiring_touched": self.brain_wiring_touched,
            "borrowed_mechanism": self.borrowed_mechanism,
            "contract_pack": self.contract_pack,
            "conformance_surfaces": list(self.conformance_surfaces),
            "baseline_result": dict(self.baseline_result),
            "primary_metric": self.primary_metric,
            "guardrail_metric": self.guardrail_metric,
            "baseline_proof_set": list(self.baseline_proof_set),
            "iteration_budget": self.iteration_budget,
            "rollback_surface": self.rollback_surface,
            "escalation_triggers": list(self.escalation_triggers),
            "analysis": dict(self.analysis),
            "iterations": [iteration.as_payload() for iteration in self.iterations],
            "final_decision": self.final_decision,
        }


def decide_loop_decision(
    *,
    primary_metric_before: int,
    primary_metric_after: int,
    guardrail_ok: bool,
    localized_failure: bool,
    better_classification: bool,
    budget_remaining: int,
    previous_no_lift_cuts: int = 0,
    escalation_reasons: tuple[str, ...] = (),
) -> tuple[LoopDecision, str]:
    if escalation_reasons:
        return "escalate", ", ".join(escalation_reasons)
    if primary_metric_after > primary_metric_before and guardrail_ok:
        return "promote", "primary metric improved and guardrails held"
    if not guardrail_ok:
        return "cut", "guardrail regressed"
    if previous_no_lift_cuts >= 1 and not better_classification:
        return "escalate", "two no-lift revisions finished without better classification"
    if localized_failure and budget_remaining > 0:
        return "revise", "failure is localized and iteration budget remains"
    return "cut", "no metric lift or clearer classification"


def evaluate_conformance_summary_truth(
    *,
    repo_root: Path = ROOT,
    summary_path: Path = CONFORMANCE_SUMMARY_PATH,
    phase_gates_path: Path = PHASE_GATES_PATH,
) -> dict[str, Any]:
    accepted_next_decision = _accepted_ct2_decision(phase_gates_path)
    if not summary_path.exists():
        return {
            "primary_metric_value": 0,
            "guardrail_ok": False,
            "accepted_next_decision": accepted_next_decision,
            "summary_next_decision": None,
            "is_full_run": False,
            "artifacts_exist": False,
            "reasons": ["summary.latest.json is missing"],
        }

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    results = summary.get("results") if isinstance(summary, dict) else None
    is_full_run = isinstance(results, list) and {
        result.get("brain")
        for result in results
        if isinstance(result, dict) and isinstance(result.get("brain"), str)
    } == {"openai", "claude", "gemini"}
    artifacts_exist = _summary_artifacts_exist(summary, repo_root=repo_root)
    summary_next_decision = summary.get("next_decision")
    active_proving_default_ok = (
        isinstance(summary, dict)
        and _summary_active_proving_default(summary) == OPENAI_ACTIVE_PROVING_DEFAULT
    )
    product_runtime_claim_ok = (
        isinstance(summary, dict)
        and _summary_product_runtime_claim(summary) == OPENAI_PRODUCT_RUNTIME_CLAIM
    )

    reasons: list[str] = []
    if not is_full_run:
        reasons.append("summary.latest does not represent a full tri-brain run")
    if not artifacts_exist:
        reasons.append("summary.latest references missing artifacts")
    if summary_next_decision != accepted_next_decision:
        reasons.append("summary.latest next_decision drifts from CT2 accepted truth")
    if not active_proving_default_ok:
        reasons.append(
            "active_proving_default drifted away from openai:operator_cli"
        )
    if not product_runtime_claim_ok:
        reasons.append(
            "product_runtime_claim drifted away from openai:service_api"
        )

    return {
        "primary_metric_value": 0 if reasons else 1,
        "guardrail_ok": active_proving_default_ok and product_runtime_claim_ok,
        "accepted_next_decision": accepted_next_decision,
        "summary_next_decision": summary_next_decision,
        "is_full_run": is_full_run,
        "artifacts_exist": artifacts_exist,
        "reasons": reasons,
    }


def run_conformance_summary_truth_pilot(
    *,
    loop_root: Path = TRAIN_LOOP_ROOT,
) -> TrainLoopRecord:
    baseline = evaluate_conformance_summary_truth()
    proof_commands = (
        "python3 -m pytest -q tests/unit/test_cortex_conformance.py tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py",
        "python3 lab/cortex_conformance.py --mode reconcile-latest",
    )
    command_results = tuple(_run_shell_command(command, cwd=ROOT) for command in proof_commands)
    post_result = evaluate_conformance_summary_truth()
    escalation_reasons = tuple(
        f"proof command failed: {result['command']}"
        for result in command_results
        if result["exit_code"] != 0
    )
    baseline_already_aligned = (
        int(baseline["primary_metric_value"]) == 1
        and bool(baseline["guardrail_ok"])
        and not baseline["reasons"]
    )
    candidate_preserved_alignment = (
        int(post_result["primary_metric_value"]) == 1
        and bool(post_result["guardrail_ok"])
        and not post_result["reasons"]
    )
    if not escalation_reasons and baseline_already_aligned and candidate_preserved_alignment:
        decision, reason = (
            "promote",
            "baseline was already aligned and the proof rerun preserved that alignment",
        )
    else:
        decision, reason = decide_loop_decision(
            primary_metric_before=int(baseline["primary_metric_value"]),
            primary_metric_after=int(post_result["primary_metric_value"]),
            guardrail_ok=bool(post_result["guardrail_ok"]),
            localized_failure=True,
            better_classification=bool(
                post_result["primary_metric_value"] > baseline["primary_metric_value"]
            ),
            budget_remaining=1,
            escalation_reasons=escalation_reasons,
        )

    iteration = LoopIteration(
        index=1,
        candidate_label="conformance-summary-truth-reconcile",
        proof_commands=proof_commands,
        primary_metric_before=int(baseline["primary_metric_value"]),
        primary_metric_after=int(post_result["primary_metric_value"]),
        guardrail_ok=bool(post_result["guardrail_ok"]),
        localized_failure=True,
        better_classification=bool(post_result["primary_metric_value"] > baseline["primary_metric_value"]),
        budget_remaining=1,
        decision=decision,
        reason=reason,
        command_results=command_results,
        escalation_reasons=escalation_reasons,
    )
    record = TrainLoopRecord(
        train_name="conformance-summary-truth",
        seam_class="shared_verification_plumbing",
        cortex_invariant=(
            "accepted conformance truth must remain mechanically aligned with local summary artifacts"
        ),
        brain_wiring_touched="none; local conformance summary publication only",
        borrowed_mechanism=(
            "reuse the existing conformance harness and accepted CT2 truth instead of adding a second ledger"
        ),
        contract_pack="verified_work_bookmarks_v1",
        conformance_surfaces=(
            OPENAI_ACTIVE_PROVING_DEFAULT,
            "claude:operator_cli",
            "gemini:operator_cli",
        ),
        baseline_result=baseline,
        primary_metric="conformance_summary_truth_alignment",
        guardrail_metric="product_runtime_claim_preserved_and_proving_default_aligned",
        baseline_proof_set=proof_commands,
        iteration_budget=2,
        rollback_surface="lab/cortex_conformance.py summary publication logic",
        escalation_triggers=(
            "Cortex law may need revision",
            "shipping truth would widen",
            "authority docs conflict",
            "auth/spend/env blocks proof",
            "two revisions fail without better classification",
        ),
        iterations=(iteration,),
        final_decision=decision,
    )
    artifact_dir = loop_root / record.train_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "summary.json", record.as_payload())
    write_text(artifact_dir / "summary.md", render_train_loop_markdown(record))
    return record


def run_verified_work_breadth_openai_train(
    *,
    loop_root: Path = TRAIN_LOOP_ROOT,
) -> TrainLoopRecord:
    baseline_pack_statuses = {
        cortex_conformance.ACTIVE_CONTRACT_PACK: "conformant",
        cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK: "conformant",
        cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK: "unsupported",
    }
    baseline = {
        "primary_metric_value": 2,
        "guardrail_ok": True,
        "pack_statuses": dict(baseline_pack_statuses),
        "tri_brain_guardrail_pack": cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK,
        "tri_brain_guardrail_status": "unmeasured",
        "reasons": [],
    }
    proof_commands: list[str] = [
        "python3 -m pytest -q tests/unit/test_verified_work.py tests/unit/test_verified_work_runtime.py tests/unit/test_openai_host_control.py tests/unit/test_cortex_conformance.py tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.ACTIVE_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.ACTIVE_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --brain openai --contract-pack {cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK}",
        f"python3 lab/cortex_conformance.py --mode active --contract-pack {cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK}",
    ]
    command_results: list[dict[str, Any]] = [
        _run_shell_command(command, cwd=ROOT) for command in proof_commands
    ]

    tri_brain_summary: dict[str, Any] | None = None
    tri_brain_initial_result = command_results[-1]
    if tri_brain_initial_result["exit_code"] == 0:
        tri_brain_summary = _command_result_json(tri_brain_initial_result)
        if _has_non_shipping_env_block(tri_brain_summary, shipping_brain="openai"):
            retry_command = (
                f"python3 lab/cortex_conformance.py --mode active --contract-pack "
                f"{cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK}"
            )
            proof_commands.append(retry_command)
            retry_result = _run_shell_command(retry_command, cwd=ROOT)
            command_results.append(retry_result)
            if retry_result["exit_code"] == 0:
                tri_brain_summary = _command_result_json(retry_result)

    summaries = [
        _command_result_json(result)
        for result in command_results[1:]
        if result["exit_code"] == 0
    ]
    pack_summaries = {
        cortex_conformance.ACTIVE_CONTRACT_PACK: summaries[:2],
        cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK: summaries[2:4],
        cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK: summaries[4:6],
    }
    if tri_brain_summary is None:
        tri_brain_summary = summaries[-1] if len(summaries) >= 7 else None

    pack_statuses: dict[str, str] = {}
    for pack_name, pack_runs in pack_summaries.items():
        is_conformant = len(pack_runs) == 2 and all(
            _summary_brain_status(summary, brain="openai") == "conformant"
            for summary in pack_runs
        )
        pack_statuses[pack_name] = "conformant" if is_conformant else "not_conformant"
    primary_metric_after = sum(
        1 for status in pack_statuses.values() if status == "conformant"
    )
    tri_brain_status = (
        tri_brain_summary.get("next_decision")
        if isinstance(tri_brain_summary, dict)
        else "unmeasured"
    )
    guardrail_ok = (
        command_results[0]["exit_code"] == 0
        and pack_statuses.get(cortex_conformance.ACTIVE_CONTRACT_PACK) == "conformant"
        and pack_statuses.get(cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK) == "conformant"
        and tri_brain_status == "promote"
    )
    repeated_env_block = sum(
        1
        for summary in pack_summaries[cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK]
        if _summary_brain_status(summary, brain="openai") == "env_blocked"
    ) >= 2
    repeated_non_shipping_guardrail_env_block = (
        isinstance(tri_brain_summary, dict)
        and _has_non_shipping_env_block(tri_brain_summary, shipping_brain="openai")
    )
    escalation_reasons = tuple(
        reason
        for reason in (
            *(
                f"proof command failed: {result['command']}"
                for result in command_results
                if result["exit_code"] != 0
            ),
            "repeated provider/env block on feature-flags OpenAI proof"
            if repeated_env_block
            else None,
            "repeated provider/env block on feature-flags tri-brain guardrail"
            if repeated_non_shipping_guardrail_env_block
            else None,
        )
        if reason is not None
    )
    localized_failure = (
        pack_statuses.get(cortex_conformance.ACTIVE_CONTRACT_PACK) == "conformant"
        and pack_statuses.get(cortex_conformance.NORMALIZE_PORT_CONTRACT_PACK) == "conformant"
        and pack_statuses.get(cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK)
        != "conformant"
    )
    better_classification = (
        pack_statuses.get(cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK) == "conformant"
    )

    decision, reason = decide_loop_decision(
        primary_metric_before=int(baseline["primary_metric_value"]),
        primary_metric_after=primary_metric_after,
        guardrail_ok=guardrail_ok,
        localized_failure=localized_failure,
        better_classification=better_classification,
        budget_remaining=1,
        escalation_reasons=escalation_reasons,
    )
    iteration = LoopIteration(
        index=1,
        candidate_label="verified-work-breadth-openai-third-pack",
        proof_commands=tuple(proof_commands),
        primary_metric_before=int(baseline["primary_metric_value"]),
        primary_metric_after=primary_metric_after,
        guardrail_ok=guardrail_ok,
        localized_failure=localized_failure,
        better_classification=better_classification,
        budget_remaining=1,
        decision=decision,
        reason=reason,
        command_results=tuple(command_results),
        escalation_reasons=escalation_reasons,
    )
    record = TrainLoopRecord(
        train_name="verified-work-breadth-openai",
        seam_class="timing_env_sensitive",
        cortex_invariant=(
            "optional work contract, runtime-native verification truth, and one bounded repair turn"
        ),
        brain_wiring_touched=(
            "OpenAI verified-work profile routing, conformance contract-pack registry, and breadth-train proof wiring"
        ),
        borrowed_mechanism=(
            "reuse the landed verified-work profile registry and add one middle-weight pure-Python evaluator pack"
        ),
        contract_pack=cortex_conformance.FEATURE_FLAGS_CONTRACT_PACK,
        conformance_surfaces=(
            OPENAI_ACTIVE_PROVING_DEFAULT,
            "claude:operator_cli",
            "gemini:operator_cli",
        ),
        baseline_result=baseline,
        primary_metric="openai_verified_work_breadth_score",
        guardrail_metric="bookmarks_stays_conformant_and_no_o4r_regression",
        baseline_proof_set=tuple(proof_commands),
        iteration_budget=2,
        rollback_surface=(
            "verified-work profile routing plus third-pack conformance wiring"
        ),
        escalation_triggers=(
            "Cortex law may need revision",
            "shipping truth would widen",
            "authority docs conflict",
            "auth/spend/env blocks proof",
            "two revisions fail without better classification",
        ),
        iterations=(iteration,),
        final_decision=decision,
    )
    artifact_dir = loop_root / record.train_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "summary.json", record.as_payload())
    write_text(artifact_dir / "summary.md", render_train_loop_markdown(record))
    return record


def run_verified_work_repair_yield_openai_train(
    *,
    loop_root: Path = TRAIN_LOOP_ROOT,
) -> TrainLoopRecord:
    deterministic_command = (
        "python3 -m pytest -q tests/unit/test_verified_work.py tests/unit/test_verified_work_runtime.py "
        "tests/unit/test_openai_host_control.py tests/unit/test_cortex_conformance.py "
        "tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py"
    )
    proof_commands: list[str] = [
        deterministic_command,
        "make -C lab revalidate-openai-operator-cli",
    ]
    command_results: list[dict[str, Any]] = [
        _run_shell_command(command, cwd=ROOT) for command in proof_commands
    ]
    deterministic_proof_count = len(command_results)
    control_summaries: list[dict[str, Any]] = []
    candidate_summaries: list[dict[str, Any]] = []
    rounds_executed = 0

    for round_index in (1, 2):
        rounds_executed = round_index
        control_results = _run_openai_pack_round(
            packs=OPENAI_BREADTH_PACKS,
            max_repair_turns=0,
        )
        proof_commands.extend(_command_text(result) for result in control_results)
        command_results.extend(control_results)
        control_summaries.extend(
            _command_result_json(result)
            for result in control_results
            if result["exit_code"] == 0
        )

        candidate_results = _run_openai_pack_round(
            packs=OPENAI_BREADTH_PACKS,
            max_repair_turns=1,
        )
        proof_commands.extend(_command_text(result) for result in candidate_results)
        command_results.extend(candidate_results)
        candidate_summaries.extend(
            _command_result_json(result)
            for result in candidate_results
            if result["exit_code"] == 0
        )
        if _count_repair_opportunities(candidate_summaries) > 0:
            break

    successful_repairs = _count_recovered_repairs(candidate_summaries)
    repair_opportunities = _count_repair_opportunities(candidate_summaries)
    control_pass_count = _count_openai_conformant_runs(control_summaries)
    candidate_pass_count = _count_openai_conformant_runs(candidate_summaries)
    repeated_openai_env_block = (
        _count_openai_env_blocks(control_summaries)
        + _count_openai_env_blocks(candidate_summaries)
    ) >= 2

    guardrail_ok = (
        all(result["exit_code"] == 0 for result in command_results[:deterministic_proof_count])
        and candidate_pass_count >= control_pass_count
    )
    guardrail_summary: dict[str, Any] | None = None
    if successful_repairs > 0:
        guardrail_results = _run_nonshipping_guardrail(REPAIR_GUARDRAIL_PACK)
        proof_commands.extend(_command_text(result) for result in guardrail_results)
        command_results.extend(guardrail_results)
        for guardrail_result in reversed(guardrail_results):
            if guardrail_result["exit_code"] == 0:
                guardrail_summary = _command_result_json(guardrail_result)
                break
        guardrail_ok = guardrail_ok and _guardrail_summary_ok(guardrail_summary)

    escalation_reasons = tuple(
        reason
        for reason in (
            *(
                f"proof command failed: {result['command']}"
                for result in command_results
                if result["exit_code"] != 0
            ),
            "repeated provider/env block on OpenAI repair-yield proof"
            if repeated_openai_env_block
            else None,
            "insufficient natural failures to measure repair yield"
            if repair_opportunities == 0 and rounds_executed == 2
            else None,
            "repeated provider/env block on non-shipping repair guardrail"
            if successful_repairs > 0
            and not _guardrail_summary_ok(guardrail_summary)
            and _has_non_shipping_env_block(guardrail_summary or {}, shipping_brain="openai")
            else None,
        )
        if reason is not None
    )

    decision, reason = decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=successful_repairs,
        guardrail_ok=guardrail_ok,
        localized_failure=repair_opportunities > 0,
        better_classification=successful_repairs > 0,
        budget_remaining=0,
        escalation_reasons=escalation_reasons,
    )
    iteration = LoopIteration(
        index=1,
        candidate_label="verified-work-repair-yield-openai-factual-ticket",
        proof_commands=tuple(proof_commands),
        primary_metric_before=0,
        primary_metric_after=successful_repairs,
        guardrail_ok=guardrail_ok,
        localized_failure=repair_opportunities > 0,
        better_classification=successful_repairs > 0,
        budget_remaining=0,
        decision=decision,
        reason=reason,
        command_results=tuple(command_results),
        escalation_reasons=escalation_reasons,
    )
    record = TrainLoopRecord(
        train_name="verified-work-repair-yield-openai",
        seam_class="timing_env_sensitive",
        cortex_invariant=(
            "optional work contract, runtime-native verification truth, and one bounded repair turn"
        ),
        brain_wiring_touched=(
            "OpenAI repair-ticket construction, verified-work outcome extraction, conformance repair-budget override, and repair-yield proof wiring"
        ),
        borrowed_mechanism=(
            "reuse the landed three-pack verified-work lane and existing failure facts while comparing one-shot control against the bounded repair path"
        ),
        contract_pack="verified_work_bookmarks_v1,verified_work_normalize_port_v1,verified_work_feature_flags_v1",
        conformance_surfaces=(
            OPENAI_ACTIVE_PROVING_DEFAULT,
            "claude:operator_cli",
            "gemini:operator_cli",
        ),
        baseline_result={
            "primary_metric_value": 0,
            "control_max_repair_turns": 0,
            "candidate_max_repair_turns": 1,
            "control_pass_count": control_pass_count,
            "candidate_pass_count": candidate_pass_count,
            "repair_opportunities": repair_opportunities,
            "rounds_executed": rounds_executed,
            "guardrail_pack": REPAIR_GUARDRAIL_PACK,
        },
        primary_metric="successful_failure_to_pass_repairs",
        guardrail_metric="candidate_pass_count_gte_control_and_no_ct2_o4r_regression",
        baseline_proof_set=tuple(proof_commands),
        iteration_budget=2,
        rollback_surface=(
            "verified-work repair-ticket text plus conformance/train-loop proof wiring"
        ),
        escalation_triggers=(
            "Cortex law may need revision",
            "shipping truth would widen",
            "authority docs conflict",
            "auth/spend/env blocks proof",
            "two revisions fail without better classification",
        ),
        iterations=(iteration,),
        final_decision=decision,
    )
    artifact_dir = loop_root / record.train_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "summary.json", record.as_payload())
    write_text(artifact_dir / "summary.md", render_train_loop_markdown(record))
    return record


def run_output_quality_comparison_openai_train(
    *,
    loop_root: Path = TRAIN_LOOP_ROOT,
) -> TrainLoopRecord:
    deterministic_command = (
        "python3 -m pytest -q tests/unit/test_output_quality_common.py "
        "tests/unit/test_output_quality_grader.py tests/unit/test_cortex_output_quality.py "
        "tests/unit/test_verified_work.py tests/unit/test_verified_work_runtime.py "
        "tests/unit/test_openai_host_control.py tests/unit/test_cortex_train_loop.py "
        "tests/internal/test_docs_boundary.py"
    )
    proof_commands: list[str] = [
        deterministic_command,
        "make -C lab revalidate-openai-operator-cli",
        "python3 lab/cortex_output_quality.py",
        "python3 lab/cortex_output_quality.py",
    ]
    command_results: list[dict[str, Any]] = [
        _run_shell_command(proof_commands[0], cwd=ROOT),
        _run_shell_command(proof_commands[1], cwd=ROOT),
        _run_long_shell_command(proof_commands[2], cwd=ROOT),
        _run_long_shell_command(proof_commands[3], cwd=ROOT),
    ]

    benchmark_summaries = [
        _command_result_json(result)
        for result in command_results[2:]
        if result["exit_code"] == 0
    ]
    repeat_summaries = tuple(
        _pairwise_payload(summary, "cortex_vs_raw") for summary in benchmark_summaries
    )
    tooling_repeat_summaries = tuple(
        _pairwise_payload(summary, "cortex_vs_tooling_only") for summary in benchmark_summaries
    )
    total_raw_objective = sum(
        _aggregate_output_quality_count(summary, "aggregate_objective_pass_count", "raw")
        for summary in benchmark_summaries
    )
    total_cortex_objective = sum(
        _aggregate_output_quality_count(summary, "aggregate_objective_pass_count", "cortex")
        for summary in benchmark_summaries
    )
    total_raw_hidden = sum(
        _aggregate_output_quality_count(summary, "aggregate_hidden_quality_pass_count", "raw")
        for summary in benchmark_summaries
    )
    total_cortex_hidden = sum(
        _aggregate_output_quality_count(summary, "aggregate_hidden_quality_pass_count", "cortex")
        for summary in benchmark_summaries
    )
    total_pairwise_wins = sum(payload["wins"] for payload in repeat_summaries)
    total_pairwise_losses = sum(payload["losses"] for payload in repeat_summaries)
    total_pairwise_ties = sum(payload["ties"] for payload in repeat_summaries)
    average_win_rate = (
        sum(payload["win_rate"] for payload in repeat_summaries) / len(repeat_summaries)
        if repeat_summaries
        else 0.0
    )
    repeat_stable = bool(repeat_summaries) and all(
        payload["wins"] >= payload["losses"] for payload in repeat_summaries
    )
    positive_hidden_signal = total_cortex_hidden > total_raw_hidden
    objective_not_worse = total_cortex_objective >= total_raw_objective
    positive_pairwise_signal = total_pairwise_wins > total_pairwise_losses
    env_blocked = any(
        bool(summary.get("env_blocked")) for summary in benchmark_summaries
    )

    escalation_reasons = tuple(
        reason
        for reason in (
            *(
                f"proof command failed: {result['command']}"
                for result in command_results
                if result["exit_code"] != 0
            ),
            "output-quality benchmark env/auth blocked on the OpenAI lane"
            if env_blocked
            else None,
            "output-quality benchmark did not return two clean repeat summaries"
            if len(benchmark_summaries) != 2
            else None,
        )
        if reason is not None
    )

    guardrail_ok = (
        len(benchmark_summaries) == 2
        and all(result["exit_code"] == 0 for result in command_results[:2])
        and objective_not_worse
        and positive_hidden_signal
        and repeat_stable
        and not env_blocked
    )
    primary_metric_after = round(average_win_rate * 100) if positive_pairwise_signal else 0

    decision, reason = decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=primary_metric_after,
        guardrail_ok=guardrail_ok,
        localized_failure=False,
        better_classification=positive_pairwise_signal,
        budget_remaining=0,
        escalation_reasons=escalation_reasons,
    )
    iteration = LoopIteration(
        index=1,
        candidate_label="output-quality-comparison-openai",
        proof_commands=tuple(proof_commands),
        primary_metric_before=0,
        primary_metric_after=primary_metric_after,
        guardrail_ok=guardrail_ok,
        localized_failure=False,
        better_classification=positive_pairwise_signal,
        budget_remaining=0,
        decision=decision,
        reason=reason,
        command_results=tuple(command_results),
        escalation_reasons=escalation_reasons,
    )
    record = TrainLoopRecord(
        train_name="output-quality-comparison-openai",
        seam_class="timing_env_sensitive",
        cortex_invariant=(
            "optional work contract, runtime-native verification truth, and one bounded repair turn"
        ),
        brain_wiring_touched=(
            "OpenAI comparative evaluation task routing, hidden output-quality grading, and repeat-run proof wiring"
        ),
        borrowed_mechanism=(
            "reuse the repo's verified-work artifact discipline, visible-vs-withheld context split, and paired comparison method without widening runtime law"
        ),
        contract_pack=(
            "astro_docs_site_v1,react_dashboard_v1,astro_marketing_forms_v1,"
            "react_existing_feature_extension_v1,frontend_bugfix_cleanup_v1"
        ),
        conformance_surfaces=(OPENAI_ACTIVE_PROVING_DEFAULT,),
        baseline_result={
            "primary_metric_value": 0,
            "pairwise_runs": len(repeat_summaries),
            "total_pairwise_wins": total_pairwise_wins,
            "total_pairwise_losses": total_pairwise_losses,
            "total_pairwise_ties": total_pairwise_ties,
            "total_raw_objective_pass_count": total_raw_objective,
            "total_cortex_objective_pass_count": total_cortex_objective,
            "total_raw_hidden_quality_pass_count": total_raw_hidden,
            "total_cortex_hidden_quality_pass_count": total_cortex_hidden,
            "repeat_stable": repeat_stable,
            "tooling_pairwise_runs": len(
                [payload for payload in tooling_repeat_summaries if payload["total"] > 0]
            ),
            "tooling_pairwise_summary": [payload for payload in tooling_repeat_summaries],
        },
        primary_metric="pairwise_win_rate_cortex_vs_raw",
        guardrail_metric="cortex_objective_not_worse_and_hidden_quality_positive",
        baseline_proof_set=tuple(proof_commands),
        iteration_budget=1,
        rollback_surface=(
            "output-quality task packs, hidden grader, and comparative train-loop wiring"
        ),
        escalation_triggers=(
            "authority docs conflict",
            "shipping truth would widen",
            "auth/spend/env blocks proof",
            "benchmark harness instability",
            "repeat run did not return two clean summaries",
        ),
        iterations=(iteration,),
        final_decision=decision,
    )
    artifact_dir = loop_root / record.train_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "summary.json", record.as_payload())
    write_text(artifact_dir / "summary.md", render_train_loop_markdown(record))
    return record


def run_causal_contribution_map_openai_train(
    *,
    loop_root: Path = TRAIN_LOOP_ROOT,
    note_path: Path | None = None,
) -> TrainLoopRecord:
    deterministic_command = (
        "python3 -m pytest -q tests/unit/test_verified_work.py "
        "tests/unit/test_verified_work_runtime.py tests/unit/test_openai_host_control.py "
        "tests/unit/test_cortex_conformance.py tests/unit/test_output_quality_common.py "
        "tests/unit/test_output_quality_grader.py tests/unit/test_output_quality_ablation.py "
        "tests/unit/test_cortex_output_quality.py tests/unit/test_causal_contribution_map.py "
        "tests/unit/test_cortex_train_loop.py tests/internal/test_docs_boundary.py "
        "tests/product/test_import_smoke.py"
    )
    proof_commands: list[str] = [
        deterministic_command,
        "make -C lab revalidate-openai-operator-cli",
    ]
    command_results: list[dict[str, Any]] = [
        _run_shell_command(deterministic_command, cwd=ROOT),
        _run_shell_command("make -C lab revalidate-openai-operator-cli", cwd=ROOT),
    ]

    baseline = _run_contribution_reading(label="baseline")
    proof_commands.extend(baseline["proof_commands"])
    command_results.extend(baseline["command_results"])
    baseline_reading = baseline["reading"]

    stage_results: dict[str, dict[str, Any]] = {}
    stage_repeats: dict[str, dict[str, Any]] = {}
    component_classifications: dict[str, dict[str, Any]] = {}

    for label, flags in (
        ("visible_contract_binding", {"visible_contract_binding": "off"}),
        (
            "revision_loop_off",
            {"verification_binding": "off", "repair_turn": "off"},
        ),
    ):
        stage = _run_contribution_reading(label=label, ablation_flags=flags)
        stage_results[label] = stage
        proof_commands.extend(stage["proof_commands"])
        command_results.extend(stage["command_results"])
        if has_material_delta(baseline=baseline_reading, candidate=stage["reading"]):
            repeat = _run_contribution_reading(label=f"{label}_repeat", ablation_flags=flags)
            stage_repeats[label] = repeat
            proof_commands.extend(repeat["proof_commands"])
            command_results.extend(repeat["command_results"])
            component_classifications[label] = _classification_payload(
                label=label,
                baseline=baseline_reading,
                runs=(stage["reading"], repeat["reading"]),
            )
        else:
            component_classifications[label] = _classification_payload(
                label=label,
                baseline=baseline_reading,
                runs=(stage["reading"],),
            )

    if _classification_requires_stage_two(component_classifications.get("revision_loop_off")):
        stage2_flags = {
            "verification_binding": {"verification_binding": "off", "repair_turn": "on"},
            "repair_turn": {"verification_binding": "on", "repair_turn": "off"},
        }
        for label, flags in stage2_flags.items():
            stage = _run_contribution_reading(label=label, ablation_flags=flags)
            stage_results[label] = stage
            proof_commands.extend(stage["proof_commands"])
            command_results.extend(stage["command_results"])
            if has_material_delta(baseline=baseline_reading, candidate=stage["reading"]):
                repeat = _run_contribution_reading(label=f"{label}_repeat", ablation_flags=flags)
                stage_repeats[label] = repeat
                proof_commands.extend(repeat["proof_commands"])
                command_results.extend(repeat["command_results"])
                component_classifications[label] = _classification_payload(
                    label=label,
                    baseline=baseline_reading,
                    runs=(stage["reading"], repeat["reading"]),
                )
            else:
                component_classifications[label] = _classification_payload(
                    label=label,
                    baseline=baseline_reading,
                    runs=(stage["reading"],),
                )
        repair_turn_payload = component_classifications.get("repair_turn")
        if repair_turn_payload is not None and repair_turn_payload["classification"] in {
            "positive",
            "negative",
            "mixed",
        }:
            flags = {
                "verification_binding": "on",
                "repair_turn": "on",
                "repair_ticket_style": "minimal",
            }
            stage = _run_contribution_reading(label="repair_ticket_style", ablation_flags=flags)
            stage_results["repair_ticket_style"] = stage
            proof_commands.extend(stage["proof_commands"])
            command_results.extend(stage["command_results"])
            if has_material_delta(baseline=baseline_reading, candidate=stage["reading"]):
                repeat = _run_contribution_reading(
                    label="repair_ticket_style_repeat",
                    ablation_flags=flags,
                )
                stage_repeats["repair_ticket_style"] = repeat
                proof_commands.extend(repeat["proof_commands"])
                command_results.extend(repeat["command_results"])
                component_classifications["repair_ticket_style"] = _classification_payload(
                    label="repair_ticket_style",
                    baseline=baseline_reading,
                    runs=(stage["reading"], repeat["reading"]),
                )
            else:
                component_classifications["repair_ticket_style"] = _classification_payload(
                    label="repair_ticket_style",
                    baseline=baseline_reading,
                    runs=(stage["reading"],),
                )

    if _classification_requires_stage_two(component_classifications.get("visible_contract_binding")):
        stage2_flags = {
            "writable_files_only_context": {
                "visible_contract_binding": "on",
                "visible_context_variant": "writable_files_only",
            },
            "writable_files_plus_visible_tests": {
                "visible_contract_binding": "on",
                "visible_context_variant": "writable_files_plus_visible_tests",
            },
        }
        for label, flags in stage2_flags.items():
            stage = _run_contribution_reading(label=label, ablation_flags=flags)
            stage_results[label] = stage
            proof_commands.extend(stage["proof_commands"])
            command_results.extend(stage["command_results"])
            if has_material_delta(baseline=baseline_reading, candidate=stage["reading"]):
                repeat = _run_contribution_reading(label=f"{label}_repeat", ablation_flags=flags)
                stage_repeats[label] = repeat
                proof_commands.extend(repeat["proof_commands"])
                command_results.extend(repeat["command_results"])
                component_classifications[label] = _classification_payload(
                    label=label,
                    baseline=baseline_reading,
                    runs=(stage["reading"], repeat["reading"]),
                )
            else:
                component_classifications[label] = _classification_payload(
                    label=label,
                    baseline=baseline_reading,
                    runs=(stage["reading"],),
                )

    positive_or_negative = [
        payload
        for payload in component_classifications.values()
        if payload["classification"] in {"positive", "negative"}
    ]
    unresolved_env = [
        payload
        for payload in component_classifications.values()
        if payload["classification"] == "unresolved_env"
    ]
    final_decision: LoopDecision
    if positive_or_negative:
        final_decision = "promote"
    elif unresolved_env and len(unresolved_env) == len(component_classifications):
        final_decision = "escalate"
    else:
        final_decision = "cut"

    primary_before = round(baseline_reading.output_quality.cortex_vs_tooling_only * 100)
    best_after = max(
        [primary_before]
        + [
            round(payload["average_metrics"]["output_quality"]["cortex_vs_tooling_only"] * 100)
            for payload in component_classifications.values()
        ]
    )
    iteration = LoopIteration(
        index=1,
        candidate_label="causal-contribution-map-openai",
        proof_commands=tuple(proof_commands),
        primary_metric_before=primary_before,
        primary_metric_after=best_after,
        guardrail_ok=all(result["exit_code"] == 0 for result in command_results[:2]),
        localized_failure=False,
        better_classification=bool(positive_or_negative),
        budget_remaining=0,
        decision=final_decision,
        reason=_causal_map_reason(final_decision, component_classifications),
        command_results=tuple(command_results),
        escalation_reasons=tuple(),
    )
    analysis = {
        "baseline_metrics": _reading_payload(baseline_reading),
        "component_classifications": component_classifications,
        "stage_results": {
            label: {
                "reading": _reading_payload(payload["reading"]),
                "ablation_flags": payload["ablation_flags"],
            }
            for label, payload in stage_results.items()
        },
        "stage_repeats": {
            label: {
                "reading": _reading_payload(payload["reading"]),
                "ablation_flags": payload["ablation_flags"],
            }
            for label, payload in stage_repeats.items()
        },
        "next_lawful_move": (
            "open one narrow runtime/product seam that strengthens the positive component and cuts the negative one"
            if positive_or_negative
            else "open a broader invariance/preservation reframe instead of another prompt-control train"
        ),
    }
    record = TrainLoopRecord(
        train_name="causal-contribution-map-openai",
        seam_class="timing_env_sensitive",
        cortex_invariant=(
            "optional work contract, runtime-native verification truth, and one bounded repair turn"
        ),
        brain_wiring_touched=(
            "evaluation-only OpenAI verified-work ablation wrapper, output-quality ablation wiring, and causal-map proof reporting"
        ),
        borrowed_mechanism=(
            "reuse the accepted O4R verified-work lane and the fixed E12 benchmark, then ablate existing interventions instead of proposing a new mechanism"
        ),
        contract_pack=(
            "verified_work_bookmarks_v1,verified_work_normalize_port_v1,verified_work_feature_flags_v1,"
            "astro_docs_site_v1,react_dashboard_v1,astro_marketing_forms_v1,"
            "react_existing_feature_extension_v1,frontend_bugfix_cleanup_v1"
        ),
        conformance_surfaces=(OPENAI_ACTIVE_PROVING_DEFAULT,),
        baseline_result={
            "primary_metric_value": primary_before,
            "component_count": len(component_classifications),
        },
        primary_metric="cortex_vs_tooling_only_delta_with_causal_classification",
        guardrail_metric="repeat_stable_component_classification",
        baseline_proof_set=tuple(proof_commands),
        iteration_budget=1,
        rollback_surface=(
            "evaluation-only ablation plumbing for openai_host_control, cortex_conformance, output-quality runner, and train-loop reporting"
        ),
        escalation_triggers=(
            "authority docs conflict",
            "shipping truth would widen",
            "auth/spend/env blocks proof",
            "benchmark or conformance harness instability",
        ),
        analysis=analysis,
        iterations=(iteration,),
        final_decision=final_decision,
    )
    artifact_dir = loop_root / record.train_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = record.as_payload()
    write_json(artifact_dir / "summary.json", payload)
    write_text(artifact_dir / "summary.md", render_train_loop_markdown(record))
    note_output_path = note_path or (ROOT / "docs" / "CORTEX_V2_CAUSAL_MAP_NOTE_0.md")
    write_text(note_output_path, render_causal_map_note(payload))
    return record


def render_train_loop_markdown(record: TrainLoopRecord) -> str:
    lines = [
        f"# Cortex Train Loop: {record.train_name}",
        "",
        f"- generated_at: `{now_utc_iso()}`",
        f"- seam_class: `{record.seam_class}`",
        f"- primary_metric: `{record.primary_metric}`",
        f"- guardrail_metric: `{record.guardrail_metric}`",
        f"- final_decision: `{record.final_decision or 'none'}`",
        "",
        "## Baseline",
        "",
    ]
    for key, value in record.baseline_result.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Iterations",
            "",
        ]
    )
    for iteration in record.iterations:
        lines.extend(
            [
                f"### Iteration {iteration.index}",
                "",
                f"- candidate: `{iteration.candidate_label}`",
                f"- decision: `{iteration.decision}`",
                f"- reason: {iteration.reason}",
                f"- primary_metric_before: `{iteration.primary_metric_before}`",
                f"- primary_metric_after: `{iteration.primary_metric_after}`",
                f"- guardrail_ok: `{iteration.guardrail_ok}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/cortex_train_loop.py",
        description="Record one bounded Cortex train loop over an existing repo proof surface.",
    )
    parser.add_argument(
        "--train",
        choices=(
            "conformance-summary-truth",
            "verified-work-breadth-openai",
            "verified-work-repair-yield-openai",
            "output-quality-comparison-openai",
            "causal-contribution-map-openai",
        ),
        default="conformance-summary-truth",
    )
    args = parser.parse_args(argv)

    if args.train == "conformance-summary-truth":
        payload = run_conformance_summary_truth_pilot().as_payload()
    elif args.train == "verified-work-breadth-openai":
        payload = run_verified_work_breadth_openai_train().as_payload()
    elif args.train == "verified-work-repair-yield-openai":
        payload = run_verified_work_repair_yield_openai_train().as_payload()
    elif args.train == "output-quality-comparison-openai":
        payload = run_output_quality_comparison_openai_train().as_payload()
    elif args.train == "causal-contribution-map-openai":
        payload = run_causal_contribution_map_openai_train().as_payload()
    else:  # pragma: no cover
        raise SystemExit(f"Unsupported train: {args.train}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _accepted_ct2_decision(phase_gates_path: Path) -> str:
    text = phase_gates_path.read_text(encoding="utf-8")
    match = re.search(
        r"^\| `CT2` .*?current (?:shipping-default|active proving-default) decision is `(?P<decision>[a-z_]+)`",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Unable to extract CT2 accepted next decision from phase gates.")
    return match.group("decision")


def _summary_active_proving_default(summary: dict[str, Any]) -> str | None:
    proving_truth = summary.get("proving_truth")
    if isinstance(proving_truth, dict):
        value = proving_truth.get("active_default")
        if isinstance(value, str) and value.strip():
            return value
    shipping_truth = summary.get("shipping_truth")
    if isinstance(shipping_truth, dict):
        value = shipping_truth.get("default")
        if isinstance(value, str) and value.strip():
            return value
    return None


def _summary_product_runtime_claim(summary: dict[str, Any]) -> str | None:
    product_truth = summary.get("product_truth")
    if isinstance(product_truth, dict):
        value = product_truth.get("runtime_claim")
        if isinstance(value, str) and value.strip():
            return value
    shipping_truth = summary.get("shipping_truth")
    if isinstance(shipping_truth, dict):
        value = shipping_truth.get("default")
        if isinstance(value, str) and value.strip():
            return value
    return None


def _summary_artifacts_exist(summary: Any, *, repo_root: Path) -> bool:
    if not isinstance(summary, dict):
        return False
    results = summary.get("results")
    if not isinstance(results, list):
        return False
    for result in results:
        if not isinstance(result, dict):
            return False
        artifact_relpath = result.get("artifact_relpath")
        if artifact_relpath is None:
            continue
        if not isinstance(artifact_relpath, str) or not artifact_relpath.strip():
            return False
        if not (repo_root / artifact_relpath).exists():
            return False
    return True


def _run_shell_command(command: str, *, cwd: Path) -> dict[str, Any]:
    result = run_command(
        ["/bin/zsh", "-lc", command],
        cwd=cwd,
        timeout_seconds=600.0,
    )
    result["command_text"] = command
    return result


def _run_long_shell_command(command: str, *, cwd: Path) -> dict[str, Any]:
    result = run_command(
        ["/bin/zsh", "-lc", command],
        cwd=cwd,
        timeout_seconds=1800.0,
    )
    result["command_text"] = command
    return result


def _command_text(command_result: dict[str, Any]) -> str:
    command_text = command_result.get("command_text")
    if isinstance(command_text, str) and command_text.strip():
        return command_text
    command = command_result.get("command")
    if isinstance(command, str) and command.strip():
        return command
    if isinstance(command, list) and len(command) >= 3 and command[0] == "/bin/zsh" and command[1] == "-lc":
        shell_command = command[2]
        if isinstance(shell_command, str) and shell_command.strip():
            return shell_command
    raise ValueError("command_result does not contain a usable command string.")


def _command_result_json(command_result: dict[str, Any]) -> dict[str, Any]:
    stdout = str(command_result.get("stdout", "") or "")
    return json.loads(stdout)


def _summary_brain_status(summary: dict[str, Any], *, brain: str) -> str | None:
    results = summary.get("results")
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("brain") == brain:
            status = result.get("status")
            return status if isinstance(status, str) else None
    return None


def _summary_brain_result(summary: dict[str, Any], *, brain: str) -> dict[str, Any] | None:
    results = summary.get("results")
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("brain") == brain:
            return result
    return None


def _count_openai_conformant_runs(summaries: list[dict[str, Any]]) -> int:
    return sum(
        1
        for summary in summaries
        if _summary_brain_status(summary, brain="openai") == "conformant"
    )


def _count_openai_env_blocks(summaries: list[dict[str, Any]]) -> int:
    return sum(
        1
        for summary in summaries
        if _summary_brain_status(summary, brain="openai") == "env_blocked"
    )


def _count_recovered_repairs(summaries: list[dict[str, Any]]) -> int:
    return sum(
        1
        for summary in summaries
        if (
            (_summary_brain_result(summary, brain="openai") or {}).get("repair_conversion")
            == "recovered_after_repair"
        )
    )


def _count_repair_opportunities(summaries: list[dict[str, Any]]) -> int:
    return sum(
        1
        for summary in summaries
        if (
            (_summary_brain_result(summary, brain="openai") or {}).get("repair_conversion")
            in {"recovered_after_repair", "repair_attempt_no_recovery"}
        )
    )


def _run_openai_pack_round(
    *,
    packs: tuple[str, ...],
    max_repair_turns: int,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for pack in packs:
        for _ in range(2):
            command = (
                "python3 lab/cortex_conformance.py --mode active --brain openai "
                f"--contract-pack {pack} --max-repair-turns {max_repair_turns}"
            )
            results.append(_run_shell_command(command, cwd=ROOT))
    return results


def _run_nonshipping_guardrail(contract_pack: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for attempt in range(2):
        command = (
            "python3 lab/cortex_conformance.py --mode active "
            f"--contract-pack {contract_pack}"
        )
        result = _run_shell_command(command, cwd=ROOT)
        results.append(result)
        if result["exit_code"] != 0:
            break
        summary = _command_result_json(result)
        if _guardrail_summary_ok(summary):
            break
        if not _has_non_shipping_env_block(summary, shipping_brain="openai") or attempt == 1:
            break
    return results


def _guardrail_summary_ok(summary: dict[str, Any] | None) -> bool:
    if not isinstance(summary, dict):
        return False
    results = summary.get("results")
    if not isinstance(results, list):
        return False
    return not any(
        isinstance(result, dict)
        and result.get("brain") != "openai"
        and result.get("status") in {"divergent", "env_blocked"}
        for result in results
    )


def _has_non_shipping_env_block(summary: dict[str, Any], *, shipping_brain: str) -> bool:
    results = summary.get("results")
    if not isinstance(results, list):
        return False
    return any(
        isinstance(result, dict)
        and result.get("brain") != shipping_brain
        and result.get("status") == "env_blocked"
        for result in results
    )


def _pairwise_payload(summary: dict[str, Any], pair_name: str) -> dict[str, Any]:
    pairwise_summary = summary.get("pairwise_summary")
    if not isinstance(pairwise_summary, dict):
        return {"wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0, "total": 0}
    payload = pairwise_summary.get(pair_name)
    if not isinstance(payload, dict):
        return {"wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0, "total": 0}
    wins = int(payload.get("wins", 0) or 0)
    losses = int(payload.get("losses", 0) or 0)
    ties = int(payload.get("ties", 0) or 0)
    win_rate = float(payload.get("win_rate", 0.0) or 0.0)
    return {
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": win_rate,
        "total": wins + losses + ties,
    }


def _aggregate_output_quality_count(summary: dict[str, Any], key: str, arm: str) -> int:
    payload = summary.get(key)
    if not isinstance(payload, dict):
        return 0
    value = payload.get(arm, 0)
    return int(value or 0)


def _run_contribution_reading(
    *,
    label: str,
    ablation_flags: dict[str, str] | None = None,
) -> dict[str, Any]:
    output_quality_command = _build_output_quality_ablation_command(ablation_flags=ablation_flags)
    output_quality_result = _run_long_shell_command(output_quality_command, cwd=ROOT)
    output_quality_summary = (
        _command_result_json(output_quality_result) if output_quality_result["exit_code"] == 0 else {}
    )

    conformance_results: list[dict[str, Any]] = []
    conformance_summaries: list[dict[str, Any]] = []
    for pack in OPENAI_BREADTH_PACKS:
        command = _build_openai_conformance_ablation_command(
            contract_pack=pack,
            ablation_flags=ablation_flags,
        )
        result = _run_shell_command(command, cwd=ROOT)
        conformance_results.append(result)
        if result["exit_code"] == 0:
            conformance_summaries.append(_command_result_json(result))

    proof_commands = [output_quality_command, *(_command_text(result) for result in conformance_results)]
    command_results = [output_quality_result, *conformance_results]
    reading = ContributionRunReading(
        label=label,
        output_quality=_output_quality_metrics_from_summary(output_quality_summary),
        verified_work=_verified_work_metrics_from_summaries(conformance_summaries),
    )
    return {
        "label": label,
        "ablation_flags": dict(ablation_flags or {}),
        "proof_commands": proof_commands,
        "command_results": command_results,
        "reading": reading,
    }


def _build_output_quality_ablation_command(*, ablation_flags: dict[str, str] | None) -> str:
    command = "python3 lab/cortex_output_quality.py"
    if not ablation_flags:
        return command
    return f"{command} {_ablation_flags_text(ablation_flags)}"


def _build_openai_conformance_ablation_command(
    *,
    contract_pack: str,
    ablation_flags: dict[str, str] | None,
) -> str:
    command = (
        "python3 lab/cortex_conformance.py --mode active --brain openai "
        f"--contract-pack {contract_pack}"
    )
    if not ablation_flags:
        return command
    return f"{command} {_ablation_flags_text(ablation_flags)}"


def _ablation_flags_text(ablation_flags: dict[str, str]) -> str:
    return " ".join(
        f"--{key.replace('_', '-')} {value}"
        for key, value in ablation_flags.items()
    )


def _output_quality_metrics_from_summary(summary: dict[str, Any]) -> OutputQualityMetrics:
    return OutputQualityMetrics(
        cortex_vs_raw=_pairwise_payload(summary, "cortex_vs_raw")["win_rate"],
        cortex_vs_tooling_only=_pairwise_payload(summary, "cortex_vs_tooling_only")["win_rate"],
        cortex_objective_pass_count=_aggregate_output_quality_count(
            summary,
            "aggregate_objective_pass_count",
            "cortex",
        ),
        cortex_hidden_quality_pass_count=_aggregate_output_quality_count(
            summary,
            "aggregate_hidden_quality_pass_count",
            "cortex",
        ),
        env_blocked=bool(summary.get("env_blocked")),
    )


def _verified_work_metrics_from_summaries(summaries: list[dict[str, Any]]) -> VerifiedWorkMetrics:
    openai_results = [
        _summary_brain_result(summary, brain="openai")
        for summary in summaries
    ]
    cleaned = [result for result in openai_results if isinstance(result, dict)]
    return VerifiedWorkMetrics(
        conformant_pack_count=sum(1 for result in cleaned if result.get("status") == "conformant"),
        first_attempt_pass_count=sum(
            1
            for result in cleaned
            if result.get("status") == "conformant" and int(result.get("attempt_count", 0) or 0) == 1
        ),
        repair_conversion_count=sum(
            1 for result in cleaned if result.get("repair_conversion") == "recovered_after_repair"
        ),
        env_blocked=any(result.get("status") == "env_blocked" for result in cleaned),
    )


def _classification_requires_stage_two(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    return payload.get("classification") in {"positive", "negative", "mixed"}


def _classification_payload(
    *,
    label: str,
    baseline: ContributionRunReading,
    runs: tuple[ContributionRunReading, ...],
) -> dict[str, Any]:
    classification = classify_component(
        baseline=baseline,
        runs=runs,
    )
    average_output_quality = {
        "cortex_vs_raw": sum(run.output_quality.cortex_vs_raw for run in runs) / len(runs),
        "cortex_vs_tooling_only": (
            sum(run.output_quality.cortex_vs_tooling_only for run in runs) / len(runs)
        ),
        "cortex_objective_pass_count": (
            sum(run.output_quality.cortex_objective_pass_count for run in runs) / len(runs)
        ),
        "cortex_hidden_quality_pass_count": (
            sum(run.output_quality.cortex_hidden_quality_pass_count for run in runs) / len(runs)
        ),
    }
    average_verified_work = {
        "conformant_pack_count": (
            sum(run.verified_work.conformant_pack_count for run in runs) / len(runs)
        ),
        "first_attempt_pass_count": (
            sum(run.verified_work.first_attempt_pass_count for run in runs) / len(runs)
        ),
        "repair_conversion_count": (
            sum(run.verified_work.repair_conversion_count for run in runs) / len(runs)
        ),
    }
    return {
        "label": label,
        "classification": classification,
        "reason": _classification_reason(classification),
        "run_count": len(runs),
        "average_metrics": {
            "output_quality": average_output_quality,
            "verified_work": average_verified_work,
        },
        "runs": [_reading_payload(run) for run in runs],
    }


def _classification_reason(classification: str) -> str:
    return {
        "positive": "turning this component off repeat-stably made results materially worse",
        "negative": "turning this component off repeat-stably made results materially better",
        "neutral": "turning this component off produced no material delta",
        "mixed": "turning this component off materially helped one metric or surface and hurt another",
        "unresolved_env": "env/provider instability prevented honest classification",
    }[classification]


def _reading_payload(reading: ContributionRunReading) -> dict[str, Any]:
    return {
        "label": reading.label,
        "output_quality": {
            "cortex_vs_raw": reading.output_quality.cortex_vs_raw,
            "cortex_vs_tooling_only": reading.output_quality.cortex_vs_tooling_only,
            "cortex_objective_pass_count": reading.output_quality.cortex_objective_pass_count,
            "cortex_hidden_quality_pass_count": reading.output_quality.cortex_hidden_quality_pass_count,
            "env_blocked": reading.output_quality.env_blocked,
        },
        "verified_work": {
            "conformant_pack_count": reading.verified_work.conformant_pack_count,
            "first_attempt_pass_count": reading.verified_work.first_attempt_pass_count,
            "repair_conversion_count": reading.verified_work.repair_conversion_count,
            "env_blocked": reading.verified_work.env_blocked,
        },
    }


def _causal_map_reason(
    decision: LoopDecision,
    component_classifications: dict[str, dict[str, Any]],
) -> str:
    if decision == "promote":
        winners = ", ".join(
            sorted(
                label
                for label, payload in component_classifications.items()
                if payload["classification"] in {"positive", "negative"}
            )
        )
        return f"repeat-stable component classifications earned a causal map: {winners}"
    if decision == "escalate":
        return "repeated env/provider instability prevented honest component classification"
    return "the train ran cleanly but no component earned a repeat-stable positive or negative classification"


__all__ = [
    "LoopDecision",
    "LoopIteration",
    "LoopClass",
    "TrainLoopRecord",
    "decide_loop_decision",
    "evaluate_conformance_summary_truth",
    "render_train_loop_markdown",
    "run_causal_contribution_map_openai_train",
    "run_conformance_summary_truth_pilot",
    "run_output_quality_comparison_openai_train",
    "run_verified_work_breadth_openai_train",
    "run_verified_work_repair_yield_openai_train",
]


if __name__ == "__main__":
    raise SystemExit(main())
