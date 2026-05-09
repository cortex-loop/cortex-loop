#!/usr/bin/env python3
"""Guardrail runner for the local Cortex overnight evaluator loop."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIGEST_ROOT = Path(".cortex/automation/overnight")
DEFAULT_CANDIDATE_DB = Path(".cortex/automation/candidates/candidates.jsonl")
LOCK_NAME = "cortex_overnight_loop.lock"
OVERNIGHT_HOURS = tuple(list(range(22, 24)) + list(range(0, 8)))
NON_TEST_LOC_ADDED_BUDGET = 250
EVALUATOR_BUILD_BLOAT_EXEMPT_SLUGS = {
    "cortex-executive-effectiveness-evaluator-build",
    "cortex-executive-effectiveness-evaluator-live-gate1",
    "cortex-executive-effectiveness-evaluator-live-matrix-run",
    "cortex-effectiveness-measurement-stack-rebuild",
    "cortex-effectiveness-v2-case-registry-gate0",
    "cortex-effectiveness-v2-live-matrix-gate1",
    "cortex-effectiveness-v2-live-matrix-run",
    "cortex-retained-active-policy-spine-gate0",
    "cortex-retained-active-policy-spine-live-gate1",
    "cortex-retained-active-policy-spine-live-run",
    "cortex-simple-hook-baseline-challenger",
    "cortex-automation-product-boundary-contract",
}
SAFE_AUTO_MERGE_SURFACES = {
    "no-live lab/proof evaluator build",
    "no-live evaluator architecture gate",
    "lab",
    "internal",
}
EVALUATOR_AUTHORIZED_SLUG_PREFIXES = (
    "cortex-executive-effectiveness-evaluator",
    "cortex-simple-hook-baseline-challenger",
    "cortex-automation-product-boundary-contract",
    "cortex-overnight-evaluator-automation-hardening",
)
EVALUATOR_AUTHORIZED_EXACT_SLUGS = {
    "cortex-effectiveness-measurement-stack-rebuild",
    "cortex-effectiveness-v2-case-registry-gate0",
    "cortex-effectiveness-v2-live-matrix-gate1",
    "cortex-effectiveness-v2-live-matrix-run",
    "cortex-retained-active-policy-spine-gate0",
    "cortex-retained-active-policy-spine-live-gate1",
    "cortex-retained-active-policy-spine-live-run",
}
ALLOWED_LIVE_SLUG_PARTS = (
    "evaluator",
    "paired-value",
    "live-probe",
    "live-matrix",
)
FORBIDDEN_REVIEW_PHRASES = (
    "product law revision",
    "fixture/scoring",
    "hidden scoring",
    "hidden-verifier change",
    "external paid",
    "service-lane",
    "positive lift",
    "value claim",
    "shipping promotion",
)
FORBIDDEN_CANDIDATE_PATH_PREFIXES = (
    "cortex/core/",
    "docs/CORTEX_V2_",
    "internal/workflow/",
    "docs/internal/REPO_WORKFLOW.md",
)
FORBIDDEN_CANDIDATE_PATH_FRAGMENTS = (
    "hidden_verifier",
    "hidden-verifier",
    "fixture",
    "fixtures",
    "scoring",
)
OLD_HOOK_HARNESS_PATH = "lab/codex_app_cli_hook_native_behavior_comparison.py"
CANDIDATE_RECORD_FIELDS = (
    "candidate_id",
    "parent_id",
    "policy_candidate",
    "executive_function",
    "loop_stage",
    "control_mode",
    "truth_scope",
    "model_io_path",
    "product_spine",
    "changed_files",
    "mutation_reason",
    "metrics",
    "score",
    "failure_class",
    "contraction_implication",
)
MISSION_OBJECTIVE_REQUIRED_FIELDS = (
    "executive_function",
    "loop_stage",
    "control_mode",
    "truth_scope",
    "model_io_path",
    "product_spine",
    "contraction_implication",
)
LAB_PROOF_MODEL_IO_PATH = "none_lab_proof_only"
PRODUCT_CLAIM_FIELDS = (
    "claims_cortex_value",
    "claims_product_progress",
    "claims_behavior_lift",
    "claims_exactness_value_lift",
    "claims_shipping_promotion",
    "behavior_lift_claim_allowed",
    "exactness_value_lift_claim_allowed",
    "broad_cortex_lift_claim_allowed",
    "codex_app_parity_claim_allowed",
    "shipping_promotion_claim_allowed",
)
FORBIDDEN_CANDIDATE_EXACT_PATHS = (
    "lab/cortex_effectiveness_evaluator.py",
)
FORBIDDEN_CANDIDATE_ROW_EXACT_PATHS = (
    "docs/CORTEX.md",
    "docs/CORTEX_STATUS.md",
    "lab/cortex_effectiveness_evaluator.py",
)
REQUIRED_BOOT_READS = (
    "AGENTS.md",
    "docs/CORTEX.md",
    "docs/CORTEX_STATUS.md",
    "internal/truth/cortex_status.json",
    "docs/internal/REPO_WORKFLOW.md",
    "internal/automation/cortex_overnight_loop.py",
)
DEFAULT_CODE_OWNER_READS = (
    "lab/cortex_effectiveness_evaluator.py",
    "lab/cortex_simple_hook_baseline.py",
    "tests/lab/test_cortex_effectiveness_evaluator.py",
    "tests/internal/test_cortex_overnight_loop.py",
)
CODE_OWNER_READS_BY_SLUG = {
    "cortex-effectiveness-measurement-stack-rebuild": (
        "lab/cortex_effectiveness_evaluator.py",
        "lab/cortex_simple_hook_baseline.py",
        "docs/recon/cortex_executive_effectiveness_evaluator_live_matrix_run.md",
        ".cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/summary.json",
        ".cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/leaderboard.json",
        ".cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/failure_analysis.json",
    ),
    "cortex-effectiveness-v2-live-matrix-gate1": (
        "lab/cortex_effectiveness_evaluator.py",
        "lab/cortex_simple_hook_baseline.py",
        ".cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/v2_case_registry.json",
        "docs/recon/cortex_effectiveness_v2_case_registry_gate0.md",
        "tests/lab/test_cortex_effectiveness_evaluator.py",
    ),
    "cortex-effectiveness-v2-live-matrix-run": (
        "lab/cortex_effectiveness_evaluator.py",
        "lab/cortex_simple_hook_baseline.py",
        ".cortex/live_validation/cortex_effectiveness_v2_live_matrix_gate1/live_plan.json",
        "docs/recon/cortex_effectiveness_v2_live_matrix_gate1.md",
        "tests/lab/test_cortex_effectiveness_evaluator.py",
    ),
    "cortex-retained-active-policy-spine-gate0": (
        "lab/cortex_effectiveness_evaluator.py",
        "docs/recon/cortex_active_policy_contraction_decision.md",
        "docs/recon/cortex_posttooluse_proof_surface_role_demotion.md",
        "tests/lab/test_cortex_effectiveness_evaluator.py",
        "tests/internal/test_docs_boundary.py",
    ),
    "cortex-retained-active-policy-spine-live-gate1": (
        "lab/cortex_effectiveness_evaluator.py",
        ".cortex/live_validation/cortex_retained_active_policy_spine_gate0/retained_spine_contract.json",
        ".cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/v2_case_registry.json",
        "docs/recon/cortex_retained_active_policy_spine_gate0.md",
        "tests/lab/test_cortex_effectiveness_evaluator.py",
        "tests/internal/test_docs_boundary.py",
    ),
    "cortex-retained-active-policy-spine-live-run": (
        "lab/cortex_effectiveness_evaluator.py",
        "lab/cortex_simple_hook_baseline.py",
        ".cortex/live_validation/cortex_retained_active_policy_spine_live_gate1/live_plan.json",
        ".cortex/live_validation/cortex_retained_active_policy_spine_live_gate1/retained_spine_contract.json",
        "docs/recon/cortex_retained_active_policy_spine_live_gate1.md",
        "tests/lab/test_cortex_effectiveness_evaluator.py",
        "tests/internal/test_docs_boundary.py",
    ),
}
ANTI_REINVENTION_SEARCHES_BY_SLUG = {
    "cortex-effectiveness-measurement-stack-rebuild": (
        "rg -n \"measurement_stack|EvaluatorEpisodeRow|evaluate_cortex_effectiveness_rows|decide_live_matrix_result|failure_silent_perception_contamination\" lab tests internal",
        "rg -n \"simple_hook_baseline|cortex_silent_perception|active_cortex|no_cortex_baseline\" lab tests internal",
        "rg -n \"PostToolUseEvidenceRecoveryEpisode|task_standard_posttooluse|failure_no_value\" lab tests docs/recon",
    ),
    "cortex-effectiveness-v2-live-matrix-gate1": (
        "rg -n \"build_v2_live_matrix_plan|v2_live_matrix|v2_case_registry|LIVE_MATRIX_CASES|build_live_matrix_plan\" lab tests internal",
        "rg -n \"simple_hook_parity|silent_perception|dominance_gates|failure_silent_perception_contamination\" lab tests docs/recon",
    ),
    "cortex-effectiveness-v2-live-matrix-run": (
        "rg -n \"build_v2_live_matrix_plan|v2_live_matrix|run_cortex_effectiveness_v2_live_matrix|LIVE_MATRIX_CASES|build_live_matrix_plan\" lab tests internal",
        "rg -n \"simple_hook_parity|silent_perception|dominance_gates|failure_silent_perception_contamination|run_20260508T221352Z\" lab tests docs/recon internal",
    ),
    "cortex-retained-active-policy-spine-gate0": (
        "rg -n \"retained active-policy spine|UserPromptSubmit task-standard|Stop closure|TaskStandardSpine|tool_evidence\" docs/recon cortex tests lab internal",
        "rg -n \"PostToolUse proof-surface|role-demoted|failure_no_value|simple_hook_baseline|candidate evolution\" docs/recon lab tests internal",
    ),
    "cortex-retained-active-policy-spine-live-gate1": (
        "rg -n \"retained_spine|userpromptsubmit_stop_taskstandard_spine|build_v2_live_matrix_plan|v2_case_registry\" lab tests internal docs/recon",
        "rg -n \"role_demoted_non_current_support_history|PostToolUse|simple_hook_baseline|cortex_silent_perception\" docs/recon lab tests internal",
    ),
    "cortex-retained-active-policy-spine-live-run": (
        "rg -n \"run_cortex_retained_active_policy_spine_live_matrix|build_retained_spine_live_gate1_plan|retained_spine_live_matrix\" lab tests internal docs/recon",
        "rg -n \"userpromptsubmit_stop_taskstandard_spine|role_demoted_non_current_support_history|simple_hook_baseline|cortex_silent_perception\" docs/recon lab tests internal",
    ),
}
DEFAULT_ANTI_REINVENTION_SEARCHES = (
    "rg -n \"EvaluatorEpisodeRow|evaluate_cortex_effectiveness_rows|simple_hook_baseline|cortex_silent_perception|active_cortex\" lab tests internal",
)
ORIENTATION_CHECKLIST = (
    "state the Cortex product goal from docs/CORTEX.md without turning lab/eval/workflow into product identity",
    "state current work_today.slug and next_product_train.slug from internal/truth/cortex_status.json",
    "state last live matrix artifact and verdict, including that active Cortex did not beat simple hook",
    "state whether the cycle surface is product or support and name the model_io_path or none_lab_proof_only",
    "state why this cycle is allowed by the runner and why stopping is not the better action",
    "state which existing owner module will be extended and why no new task-specific harness is needed",
)
CURRENT_BINDING_EVIDENCE = {
    "artifact": "run_20260508T221352Z",
    "artifact_root": ".cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/",
    "verdict": "failure_silent_perception_contamination",
    "interpretation": (
        "Active Cortex did not beat the simple-hook baseline on any family; "
        "the only discriminating continuity row improved in silent and active arms together."
    ),
    "next_train": "cortex-effectiveness-measurement-stack-rebuild",
    "forbidden_inference": (
        "Do not treat this as behavior lift, exactness value lift, product progress, "
        "shipping promotion, or permission for candidate evolution."
    ),
}
FRESH_CHAT_STOP_RULES = (
    "do not use prior chat memory as authority; repo truth and the runner work packet are authority",
    "read-only until required_boot_reads, required_code_owner_reads, and anti_reinvention_searches are complete",
    "blocked is a successful automation outcome; do not improvise around a non-ready runner decision",
    "do not create a new task-specific Gate 0 or harness if the general evaluator can express the case",
    "do not edit product Cortex, evaluator scoring, fixtures, hidden verifier surfaces, packet law, or workflow gates unless current truth explicitly authorizes it",
    "do not claim Cortex value when simple hook ties/wins or silent Cortex succeeds",
)


@dataclass(frozen=True)
class GitState:
    branch: str
    dirty: bool
    synced: bool
    managed_branch: bool
    status_short: str


@dataclass(frozen=True)
class BloatMetrics:
    loc_added: int
    loc_deleted: int
    changed_files: tuple[str, ...]
    new_policy_paths: tuple[str, ...]
    duplicate_policy_removed: bool
    contraction_debt_increased: bool
    non_test_loc_added: int = 0
    policy_lab_loc_added: int = 0
    policy_lab_loc_deleted: int = 0


@dataclass(frozen=True)
class LoopDecision:
    status: str
    next_slug: str | None
    safe_to_auto_merge: bool
    live_codex_allowed: bool
    user_input_required: bool
    reasons: tuple[str, ...]
    recommended_commands: tuple[str, ...]
    allowed_commands: tuple[str, ...]


@dataclass(frozen=True)
class WorkPacket:
    contract_version: int
    cortex_goal: str
    do_not_use_prior_chat_context: bool
    blocked_is_success: bool
    current_train: str | None
    next_train: str | None
    decision_status: str
    surface: str
    model_io_path: str
    current_binding_evidence: Mapping[str, str]
    required_boot_reads: tuple[str, ...]
    required_code_owner_reads: tuple[str, ...]
    anti_reinvention_searches: tuple[str, ...]
    orientation_checklist: tuple[str, ...]
    stop_rules: tuple[str, ...]
    allowed_commands: tuple[str, ...]
    forbidden_product_claims: tuple[str, ...]


def _run_git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )


def load_status(root: Path) -> dict[str, Any]:
    return json.loads((root / "internal/truth/cortex_status.json").read_text())


def inspect_git_state(root: Path) -> GitState:
    branch = _run_git(root, ["branch", "--show-current"]).stdout.strip()
    status_short = _run_git(root, ["status", "--short", "--untracked-files=all"]).stdout
    behind = _run_git(root, ["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    synced = False
    if behind.returncode == 0:
        counts = behind.stdout.strip().split()
        synced = counts == ["0", "0"]
    return GitState(
        branch=branch,
        dirty=bool(status_short.strip()),
        synced=synced,
        managed_branch=branch.startswith(("codex/", "claude/", "maint/")),
        status_short=status_short,
    )


def parse_numstat(text: str) -> tuple[int, int, tuple[str, ...]]:
    added = 0
    deleted = 0
    files: list[str] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_text, delete_text, path = parts[0], parts[1], parts[2]
        files.append(path)
        if add_text.isdigit():
            added += int(add_text)
        if delete_text.isdigit():
            deleted += int(delete_text)
    return added, deleted, tuple(files)


def _is_test_path(path: str) -> bool:
    return path.startswith("tests/")


def _is_policy_or_lab_path(path: str) -> bool:
    return path.startswith("lab/") or is_policy_path(path)


def is_policy_path(path: str) -> bool:
    lowered = path.lower()
    return any(
        marker in lowered
        for marker in (
            "policy",
            "actuator",
            "intervention",
            "task_standard",
            "tool_evidence",
            "runtime",
        )
    )


def bloat_metrics_from_numstat(text: str) -> BloatMetrics:
    added = 0
    deleted = 0
    non_test_added = 0
    policy_lab_added = 0
    policy_lab_deleted = 0
    files: list[str] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_text, delete_text, path = parts[0], parts[1], parts[2]
        files.append(path)
        add_count = int(add_text) if add_text.isdigit() else 0
        delete_count = int(delete_text) if delete_text.isdigit() else 0
        added += add_count
        deleted += delete_count
        if not _is_test_path(path):
            non_test_added += add_count
        if _is_policy_or_lab_path(path):
            policy_lab_added += add_count
            policy_lab_deleted += delete_count
    new_policy_paths = tuple(path for path in files if is_policy_path(path))
    return BloatMetrics(
        loc_added=added,
        loc_deleted=deleted,
        changed_files=tuple(files),
        new_policy_paths=new_policy_paths,
        duplicate_policy_removed=deleted > added and bool(new_policy_paths),
        contraction_debt_increased=added > deleted and bool(new_policy_paths),
        non_test_loc_added=non_test_added,
        policy_lab_loc_added=policy_lab_added,
        policy_lab_loc_deleted=policy_lab_deleted,
    )


def _text_line_count(path: Path) -> int:
    try:
        data = path.read_bytes()
    except OSError:
        return 0
    if not data:
        return 0
    if b"\0" in data[:4096]:
        return 0
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return 0
    return max(1, len(text.splitlines()))


def _with_untracked_files(
    root: Path,
    bloat: BloatMetrics,
    untracked_files: Sequence[str],
) -> BloatMetrics:
    existing = set(bloat.changed_files)
    additions: list[str] = []
    added_lines = 0
    for path in untracked_files:
        if path in existing:
            continue
        additions.append(path)
        added_lines += _text_line_count(root / path)
    changed_files = (*bloat.changed_files, *additions)
    new_policy_paths = tuple(path for path in changed_files if is_policy_path(path))
    loc_added = bloat.loc_added + added_lines
    non_test_added = bloat.non_test_loc_added + sum(
        _text_line_count(root / path) for path in additions if not _is_test_path(path)
    )
    policy_lab_added = bloat.policy_lab_loc_added + sum(
        _text_line_count(root / path) for path in additions if _is_policy_or_lab_path(path)
    )
    return BloatMetrics(
        loc_added=loc_added,
        loc_deleted=bloat.loc_deleted,
        changed_files=changed_files,
        new_policy_paths=new_policy_paths,
        duplicate_policy_removed=bloat.loc_deleted > loc_added and bool(new_policy_paths),
        contraction_debt_increased=loc_added > bloat.loc_deleted and bool(new_policy_paths),
        non_test_loc_added=non_test_added,
        policy_lab_loc_added=policy_lab_added,
        policy_lab_loc_deleted=bloat.policy_lab_loc_deleted,
    )


def collect_bloat_metrics(root: Path) -> BloatMetrics:
    diff = _run_git(root, ["diff", "--numstat", "origin/main"])
    if diff.returncode != 0 or not diff.stdout.strip():
        diff = _run_git(root, ["diff", "--numstat"])
    bloat = bloat_metrics_from_numstat(diff.stdout)
    untracked = _run_git(root, ["ls-files", "--others", "--exclude-standard"])
    if untracked.returncode != 0 or not untracked.stdout.strip():
        return bloat
    return _with_untracked_files(root, bloat, untracked.stdout.splitlines())


def forbidden_candidate_paths(paths: Sequence[str]) -> tuple[str, ...]:
    forbidden: list[str] = []
    for path in paths:
        if path in FORBIDDEN_CANDIDATE_EXACT_PATHS:
            forbidden.append(path)
            continue
        if path.startswith(FORBIDDEN_CANDIDATE_PATH_PREFIXES):
            forbidden.append(path)
            continue
        lowered = path.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_CANDIDATE_PATH_FRAGMENTS):
            forbidden.append(path)
    return tuple(forbidden)


def task_specific_harness_paths(paths: Sequence[str]) -> tuple[str, ...]:
    offenders: list[str] = []
    for path in paths:
        lowered = path.lower()
        if path == OLD_HOOK_HARNESS_PATH:
            offenders.append(path)
        elif path.startswith("lab/") and "posttooluse" in lowered and "cortex_effectiveness" not in lowered:
            offenders.append(path)
    return tuple(offenders)


def _candidate_value(row: Mapping[str, Any], field: str) -> Any:
    if field in row:
        return row.get(field)
    objective = row.get("mission_objective")
    if isinstance(objective, Mapping):
        return objective.get(field)
    return None


def _candidate_metrics(row: Mapping[str, Any]) -> Mapping[str, Any]:
    metrics = row.get("metrics")
    return metrics if isinstance(metrics, Mapping) else {}


def _candidate_changed_files(row: Mapping[str, Any]) -> tuple[str, ...]:
    changed = row.get("changed_files")
    if isinstance(changed, str):
        return (changed,)
    if isinstance(changed, (list, tuple)):
        return tuple(str(path) for path in changed)
    return ()


def _candidate_claims_value(row: Mapping[str, Any]) -> bool:
    metrics = _candidate_metrics(row)
    return any(bool(row.get(field)) or bool(metrics.get(field)) for field in PRODUCT_CLAIM_FIELDS)


def _product_paths(paths: Sequence[str]) -> tuple[str, ...]:
    return tuple(path for path in paths if path.startswith("cortex/"))


def candidate_mission_contract_errors(
    candidate_rows: Sequence[Mapping[str, Any]],
    *,
    changed_files: Sequence[str] = (),
    active_slug: str | None = None,
) -> tuple[str, ...]:
    errors: list[str] = []
    all_product_paths = set(_product_paths(changed_files))
    covered_product_paths: set[str] = set()
    for index, row in enumerate(candidate_rows):
        for field in MISSION_OBJECTIVE_REQUIRED_FIELDS:
            if _candidate_value(row, field) is None:
                errors.append(f"candidate[{index}] missing {field}")
        model_io_path = _candidate_value(row, "model_io_path")
        product_spine = _candidate_value(row, "product_spine")
        row_paths = _candidate_changed_files(row)
        row_forbidden_paths = tuple(
            path for path in row_paths if path in FORBIDDEN_CANDIDATE_ROW_EXACT_PATHS
        )
        if row_forbidden_paths:
            errors.append(
                f"candidate[{index}] touches forbidden candidate mutation surfaces: "
                + ", ".join(row_forbidden_paths)
            )
        product_paths = _product_paths(row_paths)
        all_product_paths.update(product_paths)
        covered_product_paths.update(product_paths)
        claims_value = _candidate_claims_value(row)
        lab_only = model_io_path == LAB_PROOF_MODEL_IO_PATH
        if claims_value and lab_only:
            errors.append(f"candidate[{index}] lab-only row claims Cortex/product value")
        if (claims_value or product_paths) and (
            not isinstance(model_io_path, str) or not model_io_path or lab_only
        ):
            errors.append(f"candidate[{index}] product/value row lacks product model-I/O path")
        if (claims_value or product_paths) and not product_spine:
            errors.append(f"candidate[{index}] product/value row lacks product_spine")
        if product_paths and row.get("authorized_by_next_train") != active_slug:
            errors.append(f"candidate[{index}] product row is not current-truth authorized")
    if all_product_paths and not candidate_rows:
        errors.append("cortex/** changes require mission objective candidate record")
    elif all_product_paths and not covered_product_paths:
        errors.append("cortex/** changes require candidate changed_files coverage")
    return tuple(errors)


def structured_positive_claim_fields(
    candidate_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, ...]:
    fields: set[str] = set()
    for row in candidate_rows:
        metrics = _candidate_metrics(row)
        for field in PRODUCT_CLAIM_FIELDS:
            if bool(row.get(field)) or bool(metrics.get(field)):
                fields.add(field)
    return tuple(sorted(fields))


def candidate_mission_summary(
    candidate_rows: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    if not candidate_rows:
        return {
            "executive_functions": "none",
            "loop_stages": "none",
            "model_io_paths": "none",
            "simple_hook_result": "none recorded",
            "contraction_implications": "none",
        }
    simple_results: list[str] = []
    for row in candidate_rows:
        failure = str(row.get("failure_class") or "")
        if failure == "failure_simple_baseline_parity":
            simple_results.append("tied/lost")
        elif failure.startswith("pass"):
            simple_results.append("beat")
        elif failure:
            simple_results.append(failure)
    return {
        "executive_functions": ", ".join(
            sorted({str(_candidate_value(row, "executive_function")) for row in candidate_rows if _candidate_value(row, "executive_function")})
        )
        or "none",
        "loop_stages": ", ".join(
            sorted({str(_candidate_value(row, "loop_stage")) for row in candidate_rows if _candidate_value(row, "loop_stage")})
        )
        or "none",
        "model_io_paths": ", ".join(
            sorted({str(_candidate_value(row, "model_io_path")) for row in candidate_rows if _candidate_value(row, "model_io_path")})
        )
        or "none",
        "simple_hook_result": ", ".join(sorted(set(simple_results))) or "none recorded",
        "contraction_implications": ", ".join(
            sorted({str(_candidate_value(row, "contraction_implication")) for row in candidate_rows if _candidate_value(row, "contraction_implication")})
        )
        or "none",
    }


def repeated_simple_baseline_losses(
    candidate_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, ...]:
    loss_counts: dict[str, int] = {}
    for row in candidate_rows:
        if row.get("failure_class") != "failure_simple_baseline_parity":
            continue
        policy = str(row.get("policy_candidate") or row.get("candidate_id") or "unknown")
        loss_counts[policy] = loss_counts.get(policy, 0) + 1
    return tuple(sorted(policy for policy, count in loss_counts.items() if count >= 2))


def load_candidate_rows(root: Path, candidate_db: Path = DEFAULT_CANDIDATE_DB) -> tuple[Mapping[str, Any], ...]:
    path = candidate_db if candidate_db.is_absolute() else root / candidate_db
    if not path.exists():
        return ()
    rows: list[Mapping[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, Mapping):
            rows.append(payload)
    return tuple(rows)


def load_latest_cycle_state(digest_root: Path) -> Mapping[str, Any] | None:
    path = digest_root / "latest_cycle_state.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _registered_live_commands(next_train: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    commands = next_train.get("registered_live_commands")
    if commands is None and next_train.get("registered_live_command") is not None:
        commands = [next_train["registered_live_command"]]
    if not isinstance(commands, list):
        return ()
    return tuple(command for command in commands if isinstance(command, Mapping))


def _managed_current_work_slug(
    status: Mapping[str, Any],
    git_state: GitState,
) -> str | None:
    if git_state.branch == "main" or not git_state.managed_branch:
        return None
    work_today = status.get("work_today") or {}
    if not isinstance(work_today, Mapping):
        return None
    work_slug = work_today.get("slug")
    if isinstance(work_slug, str) and work_slug and work_slug in git_state.branch:
        return work_slug
    branch_tail = git_state.branch.split("/", 1)[-1]
    parts = branch_tail.split("-", 2)
    if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
        return parts[2]
    return None


def _allowed_commands_for_slug(slug: str | None, git_state: GitState) -> tuple[str, ...]:
    if slug == "cortex-effectiveness-measurement-stack-rebuild":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --measurement-stack-rebuild-gate0 --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-effectiveness-v2-live-matrix-gate1":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix-gate1 --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-executive-effectiveness-evaluator-build":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --build --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-automation-product-boundary-contract":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --build --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-executive-effectiveness-evaluator-live-gate1":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --live-gate1 --require-pass",
            "python3 lab/cortex_effectiveness_evaluator.py --live-matrix",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-executive-effectiveness-evaluator-live-matrix-run":
        return (
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 lab/cortex_effectiveness_evaluator.py --live-matrix",
            "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --live-matrix",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-effectiveness-v2-live-matrix-run":
        return (
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix-gate1 --require-pass",
            "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix",
            "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-retained-active-policy-spine-gate0":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --retained-active-policy-spine-gate0 --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-retained-active-policy-spine-live-gate1":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-gate1 --require-pass",
            "python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-matrix",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-retained-active-policy-spine-live-run":
        return (
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-gate1 --require-pass",
            "python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-matrix",
            "CORTEX_CODEX_APP_CLI_RETAINED_SPINE_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-matrix",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if slug == "cortex-simple-hook-baseline-challenger":
        return (
            "python3 lab/cortex_effectiveness_evaluator.py --simple-hook-baseline-gate0 --require-pass",
            "python3 -m pytest tests/lab/test_cortex_effectiveness_evaluator.py -q",
            "python3 -m pytest tests/internal/test_cortex_overnight_loop.py -q",
            "python3 -m pytest tests/internal/test_docs_boundary.py -q",
            "python3 internal/truth/generate_status.py --check",
            "python3 internal/truth/generate_cortex_doc.py --check",
            "git diff --check",
        )
    if git_state.branch == "main" and slug:
        return (
            f"python3 internal/workflow/repo_workflow.py start-session --agent codex --slug {slug}",
        )
    return ("follow current truth and repo workflow; no unregistered command batch",)


def _is_evaluator_authorized_slug(slug: str) -> bool:
    return slug in EVALUATOR_AUTHORIZED_EXACT_SLUGS or slug.startswith(
        EVALUATOR_AUTHORIZED_SLUG_PREFIXES
    )


def _code_owner_reads_for_slug(slug: str | None) -> tuple[str, ...]:
    if slug in CODE_OWNER_READS_BY_SLUG:
        return CODE_OWNER_READS_BY_SLUG[slug]
    return DEFAULT_CODE_OWNER_READS


def _anti_reinvention_searches_for_slug(slug: str | None) -> tuple[str, ...]:
    if slug in ANTI_REINVENTION_SEARCHES_BY_SLUG:
        return ANTI_REINVENTION_SEARCHES_BY_SLUG[slug]
    return DEFAULT_ANTI_REINVENTION_SEARCHES


def _model_io_path_for_surface(surface: str, slug: str | None) -> str:
    lowered = surface.lower()
    if lowered.startswith("no-live") or "lab" in lowered or "proof" in lowered:
        return LAB_PROOF_MODEL_IO_PATH
    if slug and "posttooluse" in slug:
        return "Codex PostToolUse hookSpecificOutput.additionalContext"
    return "must_be_declared_by_product_spine"


def build_work_packet(
    status: Mapping[str, Any],
    git_state: GitState,
    decision: LoopDecision,
) -> WorkPacket:
    work_today = status.get("work_today") or {}
    next_train = status.get("next_product_train") or {}
    if not isinstance(work_today, Mapping):
        work_today = {}
    if not isinstance(next_train, Mapping):
        next_train = {}
    current_train = work_today.get("slug")
    current_train_text = str(current_train) if isinstance(current_train, str) else None
    next_slug = decision.next_slug
    surface = str(next_train.get("surface") or "")
    return WorkPacket(
        contract_version=1,
        cortex_goal=(
            "Cortex is the shipped multi-host executive layer around a model/CLI: "
            "continuity, focused persistence, context adoption, brake, truthful "
            "closure, blocker surfacing, preservation, and capability-aware routing "
            "that improve model behavior through lawful lifecycle control and model I/O."
        ),
        do_not_use_prior_chat_context=True,
        blocked_is_success=True,
        current_train=current_train_text,
        next_train=next_slug,
        decision_status=decision.status,
        surface=surface,
        model_io_path=_model_io_path_for_surface(surface, next_slug),
        current_binding_evidence=CURRENT_BINDING_EVIDENCE,
        required_boot_reads=REQUIRED_BOOT_READS,
        required_code_owner_reads=_code_owner_reads_for_slug(next_slug),
        anti_reinvention_searches=_anti_reinvention_searches_for_slug(next_slug),
        orientation_checklist=ORIENTATION_CHECKLIST,
        stop_rules=FRESH_CHAT_STOP_RULES,
        allowed_commands=decision.allowed_commands,
        forbidden_product_claims=(
            "behavior_lift",
            "exactness_value_lift",
            "broad_cortex_lift",
            "Codex App parity",
            "shipping_promotion",
            "product_progress_without_model_io",
        ),
    )


def _forbidden_review_boundary_active(
    *,
    combined: str,
    managed_work_slug: str | None,
    slug_text: str | None,
    surface: str,
) -> bool:
    if managed_work_slug:
        return False
    if not any(phrase in combined for phrase in FORBIDDEN_REVIEW_PHRASES):
        return False
    no_live_evaluator_support = (
        isinstance(slug_text, str)
        and _is_evaluator_authorized_slug(slug_text)
        and surface.lower().startswith("no-live")
    )
    if no_live_evaluator_support:
        return False
    return True


def _previous_ready_noop_reason(
    previous_cycle: Mapping[str, Any] | None,
    *,
    slug: str | None,
    git_state: GitState,
) -> str | None:
    if previous_cycle is None or not slug:
        return None
    prior_decision = previous_cycle.get("decision") or {}
    prior_git = previous_cycle.get("git_state") or {}
    if not isinstance(prior_decision, Mapping) or not isinstance(prior_git, Mapping):
        return None
    if (
        prior_decision.get("status") == "ready"
        and prior_decision.get("next_slug") == slug
        and prior_git.get("branch") == "main"
        and git_state.branch == "main"
        and not git_state.dirty
    ):
        return (
            "previous clean-main cycle already reported this next train ready; "
            "stop instead of repeating a no-op cycle"
        )
    return None


def classify_next_work(
    status: Mapping[str, Any],
    git_state: GitState,
    bloat: BloatMetrics | None = None,
    *,
    now: datetime | None = None,
    previous_cycle: Mapping[str, Any] | None = None,
    candidate_contraction: Sequence[str] = (),
    candidate_rows: Sequence[Mapping[str, Any]] = (),
) -> LoopDecision:
    next_train = status.get("next_product_train") or {}
    if not isinstance(next_train, Mapping):
        next_train = {}
    slug = next_train.get("slug")
    managed_work_slug = _managed_current_work_slug(status, git_state)
    active_slug = managed_work_slug or slug
    surface = str(next_train.get("surface") or "")
    guardrail = str(next_train.get("guardrail") or "").lower()
    primary_metric = str(next_train.get("primary_metric") or "").lower()
    kill_rule = str(next_train.get("kill_rule") or "").lower()
    combined = " ".join((surface.lower(), guardrail, primary_metric, kill_rule))
    if managed_work_slug:
        work_today = status.get("work_today") or {}
        work_note = (
            str(work_today.get("note") or "").lower()
            if isinstance(work_today, Mapping)
            else ""
        )
        combined = " ".join((managed_work_slug.lower(), work_note))
    reasons: list[str] = []

    if now is not None and now.hour not in OVERNIGHT_HOURS:
        reasons.append("current time is outside the registered overnight automation window")

    if git_state.branch == "main":
        if git_state.dirty:
            reasons.append("main worktree is dirty; overnight loop may not start from dirty resting state")
        if not git_state.synced:
            reasons.append("main is not synced with origin/main; run repo workflow sync-main first")
    elif not git_state.managed_branch:
        reasons.append("current branch is not main or a managed session branch")

    if not isinstance(active_slug, str) or not active_slug.strip():
        reasons.append("next_product_train.slug is missing")
        slug_text = None
    else:
        slug_text = active_slug
        if not _is_evaluator_authorized_slug(slug_text):
            reasons.append(f"next train `{slug_text}` is not evaluator-authorized")

    noop_reason = _previous_ready_noop_reason(
        previous_cycle,
        slug=slug_text if isinstance(slug_text, str) else None,
        git_state=git_state,
    )
    if noop_reason:
        reasons.append(noop_reason)

    if _forbidden_review_boundary_active(
        combined=combined,
        managed_work_slug=managed_work_slug,
        slug_text=slug_text,
        surface=surface,
    ):
        reasons.append("current truth names a user-review boundary or forbidden mutation surface")

    if bloat is not None:
        forbidden_paths = forbidden_candidate_paths(bloat.changed_files)
        if slug_text in EVALUATOR_BUILD_BLOAT_EXEMPT_SLUGS:
            forbidden_paths = tuple(
                path
                for path in forbidden_paths
                if path != "lab/cortex_effectiveness_evaluator.py"
            )
        if forbidden_paths:
            reasons.append(
                "candidate touches forbidden mutation surfaces: "
                + ", ".join(forbidden_paths)
            )
        harness_paths = task_specific_harness_paths(bloat.changed_files)
        if harness_paths:
            reasons.append(
                "task-specific harness growth detected; use general evaluator episode rows: "
                + ", ".join(harness_paths)
            )
        if (
            slug_text not in EVALUATOR_BUILD_BLOAT_EXEMPT_SLUGS
            and bloat.non_test_loc_added > NON_TEST_LOC_ADDED_BUDGET
        ):
            reasons.append(
                "non-test LOC budget exceeded outside evaluator build: "
                f"{bloat.non_test_loc_added} > {NON_TEST_LOC_ADDED_BUDGET}"
            )
        if (
            slug_text not in EVALUATOR_BUILD_BLOAT_EXEMPT_SLUGS
            and bloat.policy_lab_loc_added > bloat.policy_lab_loc_deleted
            and not candidate_contraction
        ):
            reasons.append(
                "policy/lab LOC increased without a contraction candidate"
            )
        mission_errors = candidate_mission_contract_errors(
            candidate_rows,
            changed_files=bloat.changed_files,
            active_slug=slug_text,
        )
        if mission_errors:
            reasons.append(
                "candidate mission/product-boundary contract failed: "
                + "; ".join(mission_errors)
            )

    positive_fields = structured_positive_claim_fields(candidate_rows)
    if positive_fields:
        reasons.append(
            "structured positive value/shipping fields require user review: "
            + ", ".join(positive_fields)
        )

    live_forbidden_by_truth = "no live codex run" in combined
    live_requested = (
        not live_forbidden_by_truth
        and ("live" in (slug_text or "").lower() or "live" in combined)
    )
    registered_live_commands = (
        ()
        if managed_work_slug and managed_work_slug != slug
        else _registered_live_commands(next_train)
    )
    live_allowed = (
        live_requested
        and "evaluator" in ((slug_text or "").lower() + " " + combined)
        and bool(registered_live_commands)
    )
    if live_requested and not live_allowed:
        reasons.append(
            "live run is not inside the registered evaluator plan with exact registered command/env"
        )

    safe_surface = (
        managed_work_slug in EVALUATOR_BUILD_BLOAT_EXEMPT_SLUGS
        or surface in SAFE_AUTO_MERGE_SURFACES
        or surface.startswith("no-live")
    )
    safe_to_auto_merge = not reasons and safe_surface and not live_requested
    status_text = "ready" if not reasons else "blocked"
    commands = []
    allowed_commands = _allowed_commands_for_slug(slug_text, git_state)
    if status_text == "ready":
        if git_state.branch == "main":
            commands.append("python3 internal/workflow/repo_workflow.py start-session --agent codex --slug " + slug_text)
        else:
            commands.append("continue managed session branch " + git_state.branch)
        commands.append("implement only the current evaluator-authorized seam")
        commands.append("run the allowed command list before any broader validation")
        commands.append("run targeted tests, generated-doc checks, closeout validation, and cleanup-report")
    else:
        commands.append("stop and report blocker in daily digest")

    return LoopDecision(
        status=status_text,
        next_slug=slug_text,
        safe_to_auto_merge=safe_to_auto_merge,
        live_codex_allowed=live_allowed,
        user_input_required=bool(reasons),
        reasons=tuple(reasons),
        recommended_commands=tuple(commands),
        allowed_commands=allowed_commands if status_text == "ready" else (),
    )


class LoopLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fd: int | None = None

    def __enter__(self) -> "LoopLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(f"overnight loop lock already exists: {self.path}") from exc
        os.write(self._fd, str(os.getpid()).encode())
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._fd is not None:
            os.close(self._fd)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def render_digest(
    *,
    now: datetime,
    git_state: GitState,
    decision: LoopDecision,
    bloat: BloatMetrics,
    candidate_contraction: Sequence[str] = (),
    candidate_rows: Sequence[Mapping[str, Any]] = (),
    work_packet: Mapping[str, Any] | None = None,
) -> str:
    mission_summary = candidate_mission_summary(candidate_rows)
    lines = [
        f"# Cortex Overnight Digest — {now.date().isoformat()}",
        "",
        f"- Timestamp: `{now.isoformat()}`",
        f"- Branch: `{git_state.branch}`",
        f"- Dirty: `{git_state.dirty}`",
        f"- Synced with origin/main: `{git_state.synced}`",
        f"- Decision: `{decision.status}`",
        f"- Next train: `{decision.next_slug}`",
        f"- Safe auto-merge: `{decision.safe_to_auto_merge}`",
        f"- Codex CLI live allowed: `{decision.live_codex_allowed}`",
        "",
        "## Bloat Delta",
        "",
        f"- LOC added: `{bloat.loc_added}`",
        f"- LOC deleted: `{bloat.loc_deleted}`",
        f"- Non-test LOC added: `{bloat.non_test_loc_added}`",
        f"- Policy/lab LOC added: `{bloat.policy_lab_loc_added}`",
        f"- Policy/lab LOC deleted: `{bloat.policy_lab_loc_deleted}`",
        f"- Changed files: `{len(bloat.changed_files)}`",
        f"- New policy paths: `{', '.join(bloat.new_policy_paths) if bloat.new_policy_paths else 'none'}`",
        f"- Duplicate policy removed: `{bloat.duplicate_policy_removed}`",
        f"- Contraction debt increased: `{bloat.contraction_debt_increased}`",
        "",
        "## Decision Reasons",
        "",
    ]
    if decision.reasons:
        lines.extend(f"- {reason}" for reason in decision.reasons)
    else:
        lines.append("- none")
    lines.extend(["", "## Recommended Commands", ""])
    lines.extend(f"- `{command}`" for command in decision.recommended_commands)
    lines.extend(["", "## Allowed Commands", ""])
    if decision.allowed_commands:
        lines.extend(f"- `{command}`" for command in decision.allowed_commands)
    else:
        lines.append("- none")
    if work_packet is not None:
        lines.extend(
            [
                "",
                "## Fresh-Chat Work Packet",
                "",
                f"- Contract version: `{work_packet.get('contract_version')}`",
                f"- Do not use prior chat context: `{work_packet.get('do_not_use_prior_chat_context')}`",
                f"- Blocked is success: `{work_packet.get('blocked_is_success')}`",
                f"- Model-I/O path: `{work_packet.get('model_io_path')}`",
                f"- Binding artifact: `{(work_packet.get('current_binding_evidence') or {}).get('artifact')}`",
                f"- Binding verdict: `{(work_packet.get('current_binding_evidence') or {}).get('verdict')}`",
                "",
                "Required reads before edits:",
            ]
        )
        lines.extend(f"- `{path}`" for path in work_packet.get("required_boot_reads", ()))
        lines.extend(["", "Code-owner reads before edits:"])
        lines.extend(f"- `{path}`" for path in work_packet.get("required_code_owner_reads", ()))
        lines.extend(["", "Anti-reinvention searches:"])
        lines.extend(f"- `{command}`" for command in work_packet.get("anti_reinvention_searches", ()))
        lines.extend(["", "Orientation checklist:"])
        lines.extend(f"- {item}" for item in work_packet.get("orientation_checklist", ()))
    lines.extend(["", "## Contraction Candidates", ""])
    if candidate_contraction:
        lines.extend(f"- `{candidate}` lost to simple baseline at least twice" for candidate in candidate_contraction)
    else:
        lines.append("- none")
    lines.extend(["", "## User Input Needed", ""])
    lines.append("- yes" if decision.user_input_required else "- no")
    lines.extend(
        [
            "",
            "## Morning Review",
            "",
            f"- What changed: `{len(bloat.changed_files)}` file(s) in current diff.",
            "- What evidence improved: see evaluator/recon artifacts from the completed seam; none is assumed by the runner.",
            "- Did Cortex beat simple-hook anywhere: no claim unless evaluator summary explicitly says so.",
            f"- Which Cortex executive function was served: `{mission_summary['executive_functions']}`.",
            f"- Which loop stage improved: `{mission_summary['loop_stages']}`.",
            f"- Model-I/O path: `{mission_summary['model_io_paths']}`.",
            f"- Simple-hook result: `{mission_summary['simple_hook_result']}`.",
            f"- Contraction implication: `{mission_summary['contraction_implications']}`.",
            f"- What lost to simple-hook: `{', '.join(candidate_contraction) if candidate_contraction else 'none recorded'}`.",
            "- What should be deleted or demoted: contraction candidates above plus any stale proof surfaces named by the evaluator.",
            "- What needs user judgment: yes if any blocker or positive value/lift claim appears.",
        ]
    )
    lines.append("")
    return "\n".join(lines)


def run_once(
    root: Path = DEFAULT_ROOT,
    *,
    now: datetime | None = None,
    digest_root: Path = DEFAULT_DIGEST_ROOT,
    candidate_rows: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    now = now or datetime.now().astimezone()
    root = root.resolve()
    digest_root = digest_root if digest_root.is_absolute() else root / digest_root
    lock_path = digest_root / LOCK_NAME
    with LoopLock(lock_path):
        started_at = datetime.now().astimezone()
        status = load_status(root)
        git_state = inspect_git_state(root)
        bloat = collect_bloat_metrics(root)
        previous_cycle = load_latest_cycle_state(digest_root)
        rows = tuple(candidate_rows) if candidate_rows else load_candidate_rows(root)
        contraction = repeated_simple_baseline_losses(rows)
        decision = classify_next_work(
            status,
            git_state,
            bloat,
            now=now,
            previous_cycle=previous_cycle,
            candidate_contraction=contraction,
            candidate_rows=rows,
        )
        work_packet = build_work_packet(status, git_state, decision)
        day_dir = digest_root / now.date().isoformat()
        day_dir.mkdir(parents=True, exist_ok=True)
        digest_text = render_digest(
            now=now,
            git_state=git_state,
            decision=decision,
            bloat=bloat,
            candidate_contraction=contraction,
            candidate_rows=rows,
            work_packet=asdict(work_packet),
        )
        digest_path = day_dir / "digest.md"
        report_path = day_dir / "cycle_report.json"
        cycle_id = f"{now.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}"
        cycle_state_path = day_dir / f"cycle_state_{cycle_id}.json"
        digest_path.write_text(digest_text, encoding="utf-8")
        ended_at = datetime.now().astimezone()
        report = {
            "cycle_id": cycle_id,
            "timestamp": now.isoformat(),
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "overnight_hours": list(OVERNIGHT_HOURS),
            "candidate_record_fields": list(CANDIDATE_RECORD_FIELDS),
            "git_state": asdict(git_state),
            "bloat": asdict(bloat),
            "decision": asdict(decision),
            "work_packet": asdict(work_packet),
            "mission_objective_summary": candidate_mission_summary(rows),
            "contraction_candidates": list(contraction),
            "digest_path": str(digest_path),
            "report_path": str(report_path),
            "cycle_state_path": str(cycle_state_path),
            "commit": None,
            "pull_request": None,
            "blocker": "; ".join(decision.reasons) if decision.reasons else None,
        }
        report_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        report_path.write_text(report_text, encoding="utf-8")
        cycle_state_path.write_text(report_text, encoding="utf-8")
        (digest_root / "latest_cycle_state.json").write_text(report_text, encoding="utf-8")
        return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one guarded Cortex overnight evaluator-loop cycle."
    )
    parser.add_argument("--once", action="store_true", help="run one cycle")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--digest-root", type=Path, default=DEFAULT_DIGEST_ROOT)
    parser.add_argument("--now", help="ISO timestamp override for tests")
    args = parser.parse_args(argv)
    if not args.once:
        parser.error("select --once")
    now = datetime.fromisoformat(args.now) if args.now else None
    try:
        report = run_once(args.repo_root, now=now, digest_root=args.digest_root)
    except RuntimeError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, indent=2))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["status"] == "ready" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
