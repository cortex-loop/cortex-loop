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

import cortex_conformance  # noqa: E402
from live_validation_common import now_utc_iso, run_command, write_json, write_text  # noqa: E402


LoopClass = Literal[
    "deterministic",
    "shared_verification_plumbing",
    "timing_env_sensitive",
]
LoopDecision = Literal["promote", "revise", "cut", "escalate"]

TRAIN_LOOP_ROOT = ROOT / ".cortex" / "train_loops"
PHASE_GATES_PATH = ROOT / "docs" / "CORTEX_V2_PHASE_GATES_2.md"
CONFORMANCE_SUMMARY_PATH = (
    ROOT / ".cortex" / "live_validation" / "conformance" / "summary.latest.json"
)


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
    shipping_default_ok = (
        isinstance(summary, dict)
        and isinstance(summary.get("shipping_truth"), dict)
        and summary["shipping_truth"].get("default") == "openai:service_api"
    )

    reasons: list[str] = []
    if not is_full_run:
        reasons.append("summary.latest does not represent a full tri-brain run")
    if not artifacts_exist:
        reasons.append("summary.latest references missing artifacts")
    if summary_next_decision != accepted_next_decision:
        reasons.append("summary.latest next_decision drifts from CT2 accepted truth")
    if not shipping_default_ok:
        reasons.append("shipping_default drifted away from openai:service_api")

    return {
        "primary_metric_value": 0 if reasons else 1,
        "guardrail_ok": shipping_default_ok,
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
        "python3 -m pytest -q tests/unit/test_cortex_conformance.py tests/unit/test_cortex_train_loop.py tests/unit/test_verification_docs_sync.py",
        "python3 tools/cortex_conformance.py --mode reconcile-latest",
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
            "openai:service_api",
            "claude:operator_cli",
            "gemini:operator_cli",
        ),
        baseline_result=baseline,
        primary_metric="conformance_summary_truth_alignment",
        guardrail_metric="shipping_default_preserved",
        baseline_proof_set=proof_commands,
        iteration_budget=2,
        rollback_surface="tools/cortex_conformance.py summary publication logic",
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
        f"- primary_metric_value: `{record.baseline_result['primary_metric_value']}`",
        f"- guardrail_ok: `{record.baseline_result['guardrail_ok']}`",
        f"- accepted_next_decision: `{record.baseline_result['accepted_next_decision']}`",
        f"- summary_next_decision: `{record.baseline_result['summary_next_decision']}`",
        "",
        "## Iterations",
        "",
    ]
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
        prog="python3 tools/cortex_train_loop.py",
        description="Record one bounded Cortex train loop over an existing repo proof surface.",
    )
    parser.add_argument(
        "--train",
        choices=("conformance-summary-truth",),
        default="conformance-summary-truth",
    )
    args = parser.parse_args(argv)

    if args.train == "conformance-summary-truth":
        payload = run_conformance_summary_truth_pilot().as_payload()
    else:  # pragma: no cover
        raise SystemExit(f"Unsupported train: {args.train}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _accepted_ct2_decision(phase_gates_path: Path) -> str:
    text = phase_gates_path.read_text(encoding="utf-8")
    match = re.search(
        r"^\| `CT2` .*?current shipping-default decision is `(?P<decision>[a-z_]+)`",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError("Unable to extract CT2 accepted next decision from phase gates.")
    return match.group("decision")


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
    return run_command(
        ["/bin/zsh", "-lc", command],
        cwd=cwd,
        timeout_seconds=600.0,
    )


__all__ = [
    "LoopDecision",
    "LoopIteration",
    "LoopClass",
    "TrainLoopRecord",
    "decide_loop_decision",
    "evaluate_conformance_summary_truth",
    "render_train_loop_markdown",
    "run_conformance_summary_truth_pilot",
]


if __name__ == "__main__":
    raise SystemExit(main())
