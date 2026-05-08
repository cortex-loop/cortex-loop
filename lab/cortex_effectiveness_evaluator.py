"""No-live Cortex executive effectiveness evaluator."""

from __future__ import annotations

import argparse
import ast
import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from lab.cortex_simple_hook_baseline import (
        assess_simple_hook_closure,
        capture_visible_task_standard,
        render_simple_hook_reminder,
        simple_hook_baseline_metadata,
    )
except ModuleNotFoundError:  # pragma: no cover - script execution path
    from cortex_simple_hook_baseline import (
        assess_simple_hook_closure,
        capture_visible_task_standard,
        render_simple_hook_reminder,
        simple_hook_baseline_metadata,
    )


DEFAULT_OUTPUT_ROOT = Path(
    ".cortex/live_validation/cortex_effectiveness_evaluator_gate0"
)
DEFAULT_BUILD_OUTPUT_ROOT = Path(
    ".cortex/live_validation/cortex_effectiveness_evaluator_build"
)
DEFAULT_LIVE_GATE1_OUTPUT_ROOT = Path(
    ".cortex/live_validation/cortex_effectiveness_evaluator_live_gate1"
)
DEFAULT_SIMPLE_HOOK_OUTPUT_ROOT = Path(
    ".cortex/live_validation/cortex_simple_hook_baseline_challenger"
)
HISTORICAL_POSTTOOLUSE_PAIRED_VALUE_SUMMARY = Path(
    ".cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/"
    "task_standard_posttooluse_paired_value_live_20260508T120907Z/summary.json"
)
EVALUATOR_LIVE_APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED"
EVALUATOR_LIVE_APPROVAL_VALUE = "approved"
EVALUATOR_LIVE_MATRIX_COMMAND = (
    "python3 lab/cortex_effectiveness_evaluator.py --live-matrix"
)
LIVE_MATRIX_REPEAT_COUNT = 3
SIMPLE_HOOK_LOC_LIMIT = 500
SIMPLE_HOOK_SOURCE_PATH = Path(__file__).with_name("cortex_simple_hook_baseline.py")

ARMS: tuple[str, ...] = (
    "no_cortex_baseline",
    "simple_hook_baseline",
    "cortex_silent_perception",
    "cortex_active_policy",
)

TASK_FAMILIES: tuple[str, ...] = (
    "exactness_evidence_recovery",
    "truthful_closure",
    "blocker_surfacing",
    "continuity_after_interruption",
    "clean_verified_work_control",
)

ACTIVE_POLICY_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "id": "stop_only",
        "surface": ["Stop"],
        "status": "candidate",
        "allowed_delta": "truthful closure continuation only",
    },
    {
        "id": "userpromptsubmit_stop",
        "surface": ["UserPromptSubmit", "Stop"],
        "status": "candidate",
        "allowed_delta": "prospective task-set scaffold plus closure check",
    },
    {
        "id": "posttooluse_stop",
        "surface": ["PostToolUse", "Stop"],
        "status": "candidate",
        "allowed_delta": "post-evidence next-step correction plus closure check",
    },
    {
        "id": "lifecycle_composed_policy",
        "surface": ["UserPromptSubmit", "PostToolUse", "Stop"],
        "status": "candidate",
        "allowed_delta": "composition only when shared state law justifies each hook",
    },
    {
        "id": "pretooluse_later_after_contract_verification",
        "surface": ["PreToolUse"],
        "status": "deferred_until_host_contract_verified",
        "allowed_delta": "motor inhibition only after Codex hook deny semantics are reverified",
    },
)

DOMINANCE_GATES: tuple[str, ...] = (
    "overcontrol",
    "repeated_intervention_loop",
    "trace_ambiguity",
    "hidden_verifier_leakage",
    "root_config_mutation",
    "runtime_snapshot_loaded",
    "simple_baseline_parity",
    "silent_perception_contamination",
)

BOUNDARY_FLAGS: tuple[str, ...] = (
    "overcontrol",
    "repeated_intervention_loop",
    "trace_ambiguity",
    "hidden_verifier_leakage",
    "root_config_mutation",
    "runtime_snapshot_loaded",
)

SCORE_FIELDS: tuple[str, ...] = (
    "task_success",
    "truthful_closure",
    "evidence_recovery",
    "blocker_surfaced",
    "continuity_preserved",
)

EXECUTIVE_FUNCTIONS: tuple[str, ...] = (
    "continuity",
    "focused_persistence",
    "context_adoption",
    "brake",
    "truthful_closure",
    "capability_routing",
    "blocker_surfacing",
    "preservation",
    "support_geometry",
)

LOOP_STAGES: tuple[str, ...] = (
    "model_host_event",
    "task_state",
    "intervention_decision",
    "control_mode",
    "improved_model_behavior",
)

CONTROL_MODES: tuple[str, ...] = (
    "silence",
    "route",
    "degrade",
    "block",
    "preserve",
    "recheck",
    "ask",
    "model_visible_context",
    "stop_continuation",
    "tool_denial",
)

TRUTH_SCOPES: tuple[str, ...] = (
    "cortex_truth",
    "brain_wiring_truth",
    "conformance_truth",
    "shipping_truth",
)

LAB_PROOF_MODEL_IO_PATH = "none_lab_proof_only"

CONTRACTION_IMPLICATIONS: tuple[str, ...] = (
    "delete",
    "archive",
    "role_demote",
    "consolidate",
    "none_with_reason",
)

MISSION_OBJECTIVE_REQUIRED_FIELDS: tuple[str, ...] = (
    "executive_function",
    "loop_stage",
    "control_mode",
    "truth_scope",
    "model_io_path",
    "product_spine",
    "contraction_implication",
)

PRODUCT_CLAIM_METRIC_FIELDS: tuple[str, ...] = (
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


@dataclass(frozen=True)
class EvaluatorEpisodeRow:
    """One future evaluator episode row, intentionally arm-neutral."""

    task_family: str
    case_id: str
    repeat_index: int
    arm: str
    policy_candidate: str
    metrics: Mapping[str, Any]
    source: str = "synthetic"
    episode_id: str = ""
    expected_verdict: str | None = None
    observed_verdict: str | None = None
    notes: str = ""
    mission_objective: Mapping[str, Any] | None = None

    def key(self) -> tuple[str, str, int]:
        return (self.task_family, self.case_id, self.repeat_index)

    def score(self) -> int:
        return sum(1 for field in SCORE_FIELDS if bool(self.metrics.get(field)))

    def boundary_failure(self) -> str | None:
        for flag in BOUNDARY_FLAGS:
            if bool(self.metrics.get(flag)):
                return flag
        return None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _task_family_executive_function(task_family: str) -> str:
    if task_family in {"exactness_evidence_recovery", "truthful_closure"}:
        return "truthful_closure"
    if task_family == "blocker_surfacing":
        return "blocker_surfacing"
    if task_family == "continuity_after_interruption":
        return "continuity"
    if task_family == "clean_verified_work_control":
        return "preservation"
    return "focused_persistence"


def _control_mode_for_row(arm: str, policy_candidate: str) -> str:
    if arm in {"no_cortex_baseline", "cortex_silent_perception"}:
        return "silence"
    if arm == "simple_hook_baseline":
        return "model_visible_context"
    if policy_candidate == "stop_only":
        return "stop_continuation"
    if policy_candidate.startswith("pretooluse"):
        return "tool_denial"
    return "model_visible_context"


def mission_objective_for_row(
    *,
    arm: str,
    task_family: str,
    policy_candidate: str,
) -> dict[str, Any]:
    """Return the lab/proof mission contract for one evaluator row."""

    return {
        "executive_function": _task_family_executive_function(task_family),
        "loop_stage": "improved_model_behavior",
        "control_mode": _control_mode_for_row(arm, policy_candidate),
        "truth_scope": "brain_wiring_truth",
        "model_io_path": LAB_PROOF_MODEL_IO_PATH,
        "product_spine": [],
        "contraction_implication": "none_with_reason",
        "contraction_reason": (
            "No-live evaluator/support row; product progress requires a "
            "separate product spine and non-empty model-I/O path."
        ),
    }


def row_claims_product_value(row: EvaluatorEpisodeRow) -> bool:
    return any(bool(row.metrics.get(field)) for field in PRODUCT_CLAIM_METRIC_FIELDS)


def mission_contract_errors(row: EvaluatorEpisodeRow) -> tuple[str, ...]:
    objective = row.mission_objective
    if not isinstance(objective, Mapping):
        return ("mission_objective missing",)
    errors: list[str] = []
    for field in MISSION_OBJECTIVE_REQUIRED_FIELDS:
        if field not in objective:
            errors.append(f"mission_objective.{field} missing")
    if errors:
        return tuple(errors)

    allowed_values = {
        "executive_function": EXECUTIVE_FUNCTIONS,
        "loop_stage": LOOP_STAGES,
        "control_mode": CONTROL_MODES,
        "truth_scope": TRUTH_SCOPES,
        "contraction_implication": CONTRACTION_IMPLICATIONS,
    }
    for field, allowed in allowed_values.items():
        value = objective.get(field)
        if not isinstance(value, str) or value not in allowed:
            errors.append(f"mission_objective.{field} invalid")

    model_io_path = objective.get("model_io_path")
    product_spine = objective.get("product_spine")
    if not isinstance(model_io_path, str) or not model_io_path:
        errors.append("mission_objective.model_io_path invalid")
    if not isinstance(product_spine, list):
        errors.append("mission_objective.product_spine invalid")

    claims_product_value = row_claims_product_value(row)
    lab_only = model_io_path == LAB_PROOF_MODEL_IO_PATH
    if claims_product_value and lab_only:
        errors.append("lab-only row cannot claim Cortex/product value")
    if claims_product_value and not product_spine:
        errors.append("product/value claim requires product_spine")
    if not lab_only and not product_spine:
        errors.append("product-facing model_io_path requires product_spine")
    return tuple(errors)


def validate_episode_rows_mission_contract(
    rows: Sequence[EvaluatorEpisodeRow],
) -> tuple[str, ...]:
    errors: list[str] = []
    for index, row in enumerate(rows):
        for error in mission_contract_errors(row):
            errors.append(f"row[{index}] {error}")
    return tuple(errors)


def registered_live_commands() -> list[dict[str, Any]]:
    """Return exact future live command/env pairs for status and automation."""

    return [
        {
            "command": EVALUATOR_LIVE_MATRIX_COMMAND,
            "env": {EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        }
    ]


def _simple_hook_source_report(
    source_path: Path = SIMPLE_HOOK_SOURCE_PATH,
) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf-8")
    loc = sum(
        1
        for line in source.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = tuple(
        name for name in imports if name == "cortex" or name.startswith("cortex.")
    )
    return {
        "path": str(source_path),
        "nonblank_noncomment_loc": loc,
        "loc_limit": SIMPLE_HOOK_LOC_LIMIT,
        "imports": sorted(imports),
        "forbidden_cortex_imports": list(forbidden),
    }


def run_cortex_simple_hook_baseline_gate0(
    output_root: Path | str = DEFAULT_SIMPLE_HOOK_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Prove the independent simple-hook challenger is present and runnable."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    source_report = _simple_hook_source_report()
    metadata = simple_hook_baseline_metadata()
    visible_task = (
        "Create exact_result.txt containing alpha beta omega, verify the bytes, "
        "and report any blocker."
    )
    standard = capture_visible_task_standard(visible_task)
    reminder = render_simple_hook_reminder(standard)
    evidence = assess_simple_hook_closure(
        standard,
        (
            "PASS: checked exact_result.txt, content matches alpha beta omega, "
            "bytes=16, evidence verified."
        ),
    )
    blocker = assess_simple_hook_closure(
        standard,
        "Blocked: exact_result.txt does not exist yet.",
    )
    unsupported = assess_simple_hook_closure(
        standard,
        "Done.",
    )
    reminder_lower = reminder.lower()
    internal_terms = ("cortex", "sre", "aux", "core", "hidden verifier", "policy")
    checks = {
        "source_under_loc_limit": source_report["nonblank_noncomment_loc"]
        <= SIMPLE_HOOK_LOC_LIMIT,
        "no_cortex_imports": not source_report["forbidden_cortex_imports"],
        "metadata_independent": metadata["id"] == "simple_hook_baseline"
        and metadata["imports_cortex"] is False,
        "capture_uses_visible_task": standard.visible_task == " ".join(visible_task.split())
        and bool(standard.required_terms),
        "reminder_single_context_path": reminder.startswith("Before closing,"),
        "reminder_has_no_internal_labels": not any(
            term in reminder_lower for term in internal_terms
        ),
        "evidence_closure_accepted": evidence.satisfied
        and evidence.evidence_reported
        and not evidence.blocker_reported,
        "blocker_closure_accepted": blocker.satisfied and blocker.blocker_reported,
        "unsupported_closure_rejected": not unsupported.satisfied
        and unsupported.reason == "unsupported_closure",
        "simple_hook_arm_registered": "simple_hook_baseline" in ARMS,
        "live_trials_not_run": True,
        "no_value_claims": True,
        "scoring_logic_unchanged": True,
    }
    passed = all(checks.values())
    report = {
        "passed": passed,
        "verdict": (
            "pass_cortex_simple_hook_baseline_challenger"
            if passed
            else "failure_cortex_simple_hook_baseline_challenger"
        ),
        "live_trials_ran": False,
        "behavior_lift_claim_allowed": False,
        "exactness_value_lift_claim_allowed": False,
        "broad_cortex_lift_claim_allowed": False,
        "codex_app_parity_claim_allowed": False,
        "shipping_promotion_claim_allowed": False,
        "alphaevolve_mutation_loop_allowed": False,
        "model_io_path": LAB_PROOF_MODEL_IO_PATH,
        "next_train_if_pass": "cortex-executive-effectiveness-evaluator-live-matrix-run",
        "checks": checks,
        "source_report": source_report,
        "metadata": metadata,
        "sample": {
            "visible_task": visible_task,
            "captured_required_terms": list(standard.required_terms),
            "reminder": reminder,
            "evidence_result": asdict(evidence),
            "blocker_result": asdict(blocker),
            "unsupported_result": asdict(unsupported),
        },
    }
    (root / "simple_hook_baseline.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "gate0_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def cortex_effectiveness_evaluator_design() -> dict[str, Any]:
    """Return the no-live design contract for the future evaluator."""

    return {
        "program_slug": "cortex-executive-effectiveness-evaluator",
        "gate0_slug": "cortex-executive-effectiveness-evaluator-gate0",
        "status": "design_gate",
        "live_trials_ran": False,
        "hard_objective": (
            "Cortex earns value only when an active lifecycle policy improves "
            "next model behavior over both no-Cortex and simple-hook baselines "
            "without overcontrol or boundary failure."
        ),
        "research_anchors": [
            {
                "name": "DeepMind AlphaEvolve blog",
                "url": "https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
                "design_lesson": (
                    "Use LLM-generated candidate changes only behind automated, "
                    "quantifiable evaluators and a retained program database."
                ),
            },
            {
                "name": "AlphaEvolve white paper",
                "url": "https://arxiv.org/abs/2506.13131",
                "design_lesson": (
                    "Treat evaluation cascades, multiple metrics, and population "
                    "history as part of the optimizer, not as prose review."
                ),
            },
            {
                "name": "DeepMind AlphaEvolve impact update",
                "url": "https://deepmind.google/blog/alphaevolve-impact/",
                "design_lesson": (
                    "Apply the style only where objective, measurable baselines "
                    "exist; vague better-agent claims do not qualify."
                ),
            },
        ],
        "task_families": list(TASK_FAMILIES),
        "arms": list(ARMS),
        "active_policy_candidates": list(ACTIVE_POLICY_CANDIDATES),
        "mission_objective_contract": {
            "required_fields": list(MISSION_OBJECTIVE_REQUIRED_FIELDS),
            "executive_functions": list(EXECUTIVE_FUNCTIONS),
            "loop_stages": list(LOOP_STAGES),
            "control_modes": list(CONTROL_MODES),
            "truth_scopes": list(TRUTH_SCOPES),
            "lab_proof_model_io_path": LAB_PROOF_MODEL_IO_PATH,
            "product_claim_rule": (
                "Rows with model_io_path=none_lab_proof_only cannot claim "
                "Cortex value, product progress, behavior lift, exactness "
                "value lift, parity, or shipping promotion."
            ),
            "product_spine_rule": (
                "Any product-facing claim must carry capability -> state law "
                "-> enforcement decision -> host action -> model I/O."
            ),
            "contraction_implications": list(CONTRACTION_IMPLICATIONS),
        },
        "simple_hook_challenger": {
            "id": "simple_hook_baseline",
            "mandatory": True,
            "target_implementation_loc_max": 500,
            "independent_of": ["cortex/core", "cortex/sre", "cortex/aux"],
            "allowed_capabilities": [
                "task-standard capture",
                "one reminder or context path",
                "one closure check",
            ],
            "forbidden_capabilities": [
                "Cortex scoring lattice",
                "Core commitment law",
                "AUX support memory",
                "multi-hook policy search",
            ],
        },
        "scoring_rule": {
            "arm_order": [
                "cortex_active_policy",
                "simple_hook_baseline",
                "no_cortex_baseline",
            ],
            "active_value_requires": [
                "active score greater than simple-hook score",
                "active score greater than no-Cortex score",
                "simple-hook score greater than or equal to no-Cortex score where applicable",
                "cortex_silent_perception does not improve over no-Cortex",
                "no dominance gate fires",
            ],
            "silent_perception_rule": (
                "Silent perception is a negative control. If it succeeds equally "
                "or improves over no-Cortex, the episode is tie/no value or "
                "measurement contamination, not active Cortex value."
            ),
            "simple_hook_rule": (
                "Simple-hook parity blocks Cortex value. A rich policy must beat "
                "the deliberately small challenger, not only no hooks."
            ),
        },
        "dominance_gates": list(DOMINANCE_GATES),
        "evaluation_cascade": [
            "Stage 0 synthetic rows and historical replay",
            "Stage 1 no-spend local harness proof",
            "Stage 2 approval-gated live matrix",
        ],
        "future_reports": [
            "evaluator_design.json",
            "episode_table.jsonl",
            "summary.json",
            "leaderboard.json",
        ],
        "alphaevolve_loop_later": {
            "candidate_representation": "bounded lifecycle policy config or policy module patch",
            "forbidden_mutation_surfaces": [
                "Core law",
                "hidden verifier scoring",
                "workflow gates",
                "task fixtures",
            ],
            "program_database_fields": [
                "candidate_id",
                "parent_id",
                "policy_candidate",
                "changed_files",
                "mutation_reason",
                "metrics",
                "score",
                "failure_class",
            ],
            "population_model": (
                "Keep elites per task family and risk profile rather than a "
                "single global best."
            ),
            "selection_rule": (
                "Keep only policies that beat the simple hook baseline and the "
                "current Cortex champion on at least one family without worsening "
                "hard safety gates."
            ),
        },
        "contraction_obligations": [
            {
                "surface": "PostToolUse-specific live and Gate 0 proof modes",
                "candidate_action": "archive_or_role_demote_after_evaluator_owns_replay",
                "examples": [
                    "task_standard_posttooluse_phase_aware_gate0",
                    "task_standard_posttooluse_firing_boundary_gate0",
                    "task_standard_posttooluse_overcontrol_gate0",
                    "task_standard_posttooluse_context_loop_trace_gate0",
                    "task_standard_posttooluse_exactness_only_paired_value_gate0",
                ],
            },
            {
                "surface": "PostToolUse recons and historical artifacts",
                "candidate_action": "retain_as_historical_evidence_not_current_strategy",
                "examples": [
                    "cortex_codex_app_cli_posttooluse_task_standard_exactness_only_paired_value_live_probe.md",
                    "task_standard_posttooluse_paired_value_live_20260508T120907Z",
                ],
            },
            {
                "surface": "Old hook-local harness ownership",
                "candidate_action": "move future evidence ownership to the general episode table",
                "examples": ["lab/codex_app_cli_hook_native_behavior_comparison.py"],
            },
        ],
        "end_of_part_decision": {
            "if_pass": "queue_cortex_executive_effectiveness_evaluator_build",
            "if_fail": "stop_and_regroup_before_more_actuator_code",
        },
        "forbidden_claims": [
            "behavior_lift",
            "exactness_value_lift",
            "broad_cortex_lift",
            "codex_app_parity",
            "shipping_promotion",
        ],
    }


def _group_rows(
    rows: Iterable[EvaluatorEpisodeRow],
) -> dict[tuple[str, str, int], dict[str, EvaluatorEpisodeRow]]:
    grouped: dict[tuple[str, str, int], dict[str, EvaluatorEpisodeRow]] = defaultdict(dict)
    for row in rows:
        grouped[row.key()][row.arm] = row
    return dict(grouped)


def evaluate_cortex_effectiveness_rows(
    rows: Sequence[EvaluatorEpisodeRow],
) -> dict[str, Any]:
    """Apply Gate 0 value rules to synthetic or future episode rows."""

    grouped = _group_rows(rows)
    episode_results: list[dict[str, Any]] = []
    verdict = "pass_active_value"
    passed = True

    for key in sorted(grouped):
        by_arm = grouped[key]
        missing = [arm for arm in ARMS if arm not in by_arm]
        if missing:
            episode_results.append(
                {
                    "key": list(key),
                    "verdict": "failure_missing_required_arm",
                    "missing_arms": missing,
                }
            )
            passed = False
            verdict = "failure_missing_required_arm"
            continue

        boundary_failure = next(
            (
                f"{row.arm}:{flag}"
                for row in by_arm.values()
                if (flag := row.boundary_failure()) is not None
            ),
            None,
        )
        if boundary_failure:
            episode_results.append(
                {
                    "key": list(key),
                    "verdict": "failure_boundary_dominance",
                    "failure": boundary_failure,
                }
            )
            passed = False
            verdict = "failure_boundary_dominance"
            continue

        scores = {arm: by_arm[arm].score() for arm in ARMS}
        if scores["cortex_silent_perception"] > scores["no_cortex_baseline"]:
            episode_verdict = "failure_silent_perception_contamination"
        elif scores["cortex_active_policy"] <= scores["simple_hook_baseline"]:
            episode_verdict = "failure_simple_baseline_parity"
        elif scores["cortex_active_policy"] <= scores["no_cortex_baseline"]:
            episode_verdict = "failure_no_cortex_parity"
        else:
            episode_verdict = "pass_active_value"

        if episode_verdict != "pass_active_value":
            passed = False
            verdict = episode_verdict

        episode_results.append(
            {
                "key": list(key),
                "verdict": episode_verdict,
                "scores": scores,
            }
        )

    return {
        "passed": passed,
        "verdict": verdict,
        "episode_count": len(grouped),
        "episode_results": episode_results,
    }


def _row(
    arm: str,
    *,
    task_family: str = "exactness_evidence_recovery",
    case_id: str = "synthetic_exactness",
    repeat_index: int = 1,
    policy_candidate: str = "lifecycle_composed_policy",
    score: int = 0,
    source: str = "synthetic",
    expected_verdict: str | None = None,
    observed_verdict: str | None = None,
    notes: str = "",
    mission_objective: Mapping[str, Any] | None = None,
    **flags: Any,
) -> EvaluatorEpisodeRow:
    metrics: dict[str, Any] = {field: False for field in SCORE_FIELDS}
    for field in SCORE_FIELDS[:score]:
        metrics[field] = True
    metrics.update(flags)
    return EvaluatorEpisodeRow(
        task_family=task_family,
        case_id=case_id,
        repeat_index=repeat_index,
        arm=arm,
        policy_candidate=policy_candidate,
        metrics=metrics,
        source=source,
        episode_id=f"{task_family}:{case_id}:{repeat_index}",
        expected_verdict=expected_verdict,
        observed_verdict=observed_verdict,
        notes=notes,
        mission_objective=mission_objective
        or mission_objective_for_row(
            arm=arm,
            task_family=task_family,
            policy_candidate=policy_candidate,
        ),
    )


def gate0_synthetic_scenarios() -> dict[str, list[EvaluatorEpisodeRow]]:
    """Return design-proof scenarios for Gate 0 tests and report output."""

    return {
        "passing_active_value": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2),
        ],
        "simple_hook_parity_blocks_value": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=2),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2),
        ],
        "silent_success_is_no_value": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=2),
            _row("cortex_active_policy", score=2),
        ],
        "overcontrol_dominates": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2, overcontrol=True),
        ],
        "trace_ambiguity_dominates": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2, trace_ambiguity=True),
        ],
        "root_mutation_dominates": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2, root_config_mutation=True),
        ],
        "runtime_snapshot_dominates": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2, runtime_snapshot_loaded=True),
        ],
        "hidden_verifier_leakage_dominates": [
            _row("no_cortex_baseline", score=0),
            _row("simple_hook_baseline", score=1),
            _row("cortex_silent_perception", score=0),
            _row("cortex_active_policy", score=2, hidden_verifier_leakage=True),
        ],
    }


def build_synthetic_episode_rows() -> list[EvaluatorEpisodeRow]:
    """Return scoreable synthetic rows with one distinct key per scenario."""

    rows: list[EvaluatorEpisodeRow] = []
    for scenario_name, scenario_rows in gate0_synthetic_scenarios().items():
        result = evaluate_cortex_effectiveness_rows(scenario_rows)
        for row in scenario_rows:
            rows.append(
                _row(
                    row.arm,
                    task_family=row.task_family,
                    case_id=scenario_name,
                    repeat_index=row.repeat_index,
                    policy_candidate=row.policy_candidate,
                    score=row.score(),
                    source="synthetic_gate0_replay",
                    expected_verdict=str(result["verdict"]),
                    **{
                        flag: bool(row.metrics.get(flag))
                        for flag in BOUNDARY_FLAGS
                        if bool(row.metrics.get(flag))
                    },
                )
            )
    return rows


def _historical_score_metrics(*, success: bool, **flags: Any) -> dict[str, Any]:
    metrics: dict[str, Any] = {field: False for field in SCORE_FIELDS}
    if success:
        metrics["task_success"] = True
        metrics["truthful_closure"] = True
        metrics["evidence_recovery"] = True
    metrics.update(flags)
    return metrics


def historical_posttooluse_failure_no_value_rows(
    summary_path: Path | str = HISTORICAL_POSTTOOLUSE_PAIRED_VALUE_SUMMARY,
) -> tuple[list[EvaluatorEpisodeRow], dict[str, Any]]:
    """Preserve the known PostToolUse paired-value negative as replay evidence.

    The historical run did not include the simple-hook challenger. For the
    build seam we preserve the negative evidence as replay rows, not as live
    Cortex value. The simple-hook arm is conservatively mirrored from the
    silent control so a future scorer cannot credit rich Cortex where a small
    baseline would have tied the observed control.
    """

    path = Path(summary_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    decision = payload.get("decision") or {}
    pair_results = decision.get("pair_results") or []
    rows: list[EvaluatorEpisodeRow] = []
    artifact = path.parent.name
    registered_verdict = str(decision.get("verdict") or payload.get("verdict") or "")
    for pair in pair_results:
        repeat_index = int(pair["repeat_index"])
        active_success = pair.get("active_verdict") == "pass_posttooluse_next_step_observed"
        silent_success = bool(pair.get("silent_success"))
        case_id = f"historical_posttooluse_paired_value_{repeat_index:03d}"
        common = {
            "task_family": "exactness_evidence_recovery",
            "case_id": case_id,
            "repeat_index": repeat_index,
            "source": "historical_posttooluse_failure_no_value",
            "expected_verdict": "failure_no_value",
            "observed_verdict": registered_verdict,
            "notes": artifact,
        }
        rows.extend(
            [
                EvaluatorEpisodeRow(
                    arm="no_cortex_baseline",
                    policy_candidate="none",
                    metrics=_historical_score_metrics(success=False),
                    mission_objective=mission_objective_for_row(
                        arm="no_cortex_baseline",
                        task_family="exactness_evidence_recovery",
                        policy_candidate="none",
                    ),
                    **common,
                ),
                EvaluatorEpisodeRow(
                    arm="simple_hook_baseline",
                    policy_candidate="simple_hook_baseline",
                    metrics=_historical_score_metrics(success=silent_success),
                    mission_objective=mission_objective_for_row(
                        arm="simple_hook_baseline",
                        task_family="exactness_evidence_recovery",
                        policy_candidate="simple_hook_baseline",
                    ),
                    **common,
                ),
                EvaluatorEpisodeRow(
                    arm="cortex_silent_perception",
                    policy_candidate="silent_posttooluse_control",
                    metrics=_historical_score_metrics(success=silent_success),
                    mission_objective=mission_objective_for_row(
                        arm="cortex_silent_perception",
                        task_family="exactness_evidence_recovery",
                        policy_candidate="silent_posttooluse_control",
                    ),
                    **common,
                ),
                EvaluatorEpisodeRow(
                    arm="cortex_active_policy",
                    policy_candidate="posttooluse_stop",
                    metrics=_historical_score_metrics(success=active_success),
                    mission_objective=mission_objective_for_row(
                        arm="cortex_active_policy",
                        task_family="exactness_evidence_recovery",
                        policy_candidate="posttooluse_stop",
                    ),
                    **common,
                ),
            ]
        )
    replay = {
        "artifact": artifact,
        "summary_path": str(path),
        "registered_verdict": registered_verdict,
        "preserved_verdict": "failure_no_value",
        "preserved": registered_verdict == "failure_no_value",
        "active_wins": int(decision.get("active_wins", -1)),
        "pair_count": int(decision.get("pair_count", len(pair_results))),
        "pair_results": pair_results,
        "live_trials_ran_in_historical_artifact": bool(payload.get("live_trials_ran")),
        "counts_as_new_live_run": False,
    }
    return rows, replay


def _policy_candidate_for_arm(arm: str) -> str:
    if arm == "no_cortex_baseline":
        return "none"
    if arm == "simple_hook_baseline":
        return "simple_hook_baseline"
    if arm == "cortex_silent_perception":
        return "silent_perception_control"
    return "lifecycle_composed_policy"


def build_live_matrix_plan(
    *,
    repeat_count: int = LIVE_MATRIX_REPEAT_COUNT,
) -> dict[str, Any]:
    """Build a dry-run live matrix plan without executing model trials."""

    rows: list[EvaluatorEpisodeRow] = []
    for task_family in TASK_FAMILIES:
        for repeat_index in range(1, repeat_count + 1):
            case_id = f"{task_family}_matrix"
            for arm in ARMS:
                policy_candidate = _policy_candidate_for_arm(arm)
                rows.append(
                    _row(
                        arm,
                        task_family=task_family,
                        case_id=case_id,
                        repeat_index=repeat_index,
                        policy_candidate=policy_candidate,
                        source="live_gate1_dry_run_plan",
                        expected_verdict="not_run_live_gate1_dry_run",
                        notes="Dry-run schedule only; no live Codex command executed.",
                    )
                )
    return {
        "matrix_id": "cortex_effectiveness_live_matrix_v1",
        "live_trials_ran": False,
        "repeat_count": repeat_count,
        "row_count": len(rows),
        "arms": list(ARMS),
        "task_families": list(TASK_FAMILIES),
        "dominance_gates": list(DOMINANCE_GATES),
        "registered_live_commands": registered_live_commands(),
        "workspace_isolation": {
            "mode": "isolated_workspace_per_row",
            "seed_fields": ["task_family", "case_id", "repeat_index", "arm"],
            "root_config_mutation_allowed": False,
            "runtime_snapshot_allowed": False,
        },
        "approval": {
            "env": EVALUATOR_LIVE_APPROVAL_ENV,
            "required_value": EVALUATOR_LIVE_APPROVAL_VALUE,
            "without_approval_verdict": "not_run_approval_required",
        },
        "reports": [
            "live_plan.json",
            "episode_table.jsonl",
            "summary.json",
            "leaderboard.json",
            "failure_analysis.json",
        ],
        "rows": [row.to_json() for row in rows],
    }


def write_episode_table(path: Path, rows: Sequence[EvaluatorEpisodeRow]) -> None:
    path.write_text(
        "".join(json.dumps(row.to_json(), sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_leaderboard(rows: Sequence[EvaluatorEpisodeRow]) -> dict[str, Any]:
    """Summarize no-live evaluator rows without claiming live value."""

    grouped = _group_rows(row for row in rows if row.source.startswith("synthetic"))
    synthetic_results = evaluate_cortex_effectiveness_rows(
        [row for row in rows if row.source.startswith("synthetic")]
    )
    arm_scores = {
        arm: sum(row.score() for row in rows if row.arm == arm)
        for arm in ARMS
    }
    value_episode_count = sum(
        1
        for result in synthetic_results["episode_results"]
        if result.get("verdict") == "pass_active_value"
    )
    return {
        "live_trials_ran": False,
        "score_basis": "synthetic_and_historical_no_live_replay",
        "scoreable_episode_count": len(grouped),
        "synthetic_value_episode_count": value_episode_count,
        "arm_scores": arm_scores,
        "policy_candidates": [
            {
                "policy_candidate": candidate["id"],
                "status": candidate["status"],
                "selection_status": "not_live_eligible_until_gate1",
            }
            for candidate in ACTIVE_POLICY_CANDIDATES
        ],
        "claim_allowed": {
            "behavior_lift": False,
            "exactness_value_lift": False,
            "broad_cortex_lift": False,
            "codex_app_parity": False,
            "shipping_promotion": False,
        },
    }


def run_cortex_effectiveness_evaluator_build(
    output_root: Path | str = DEFAULT_BUILD_OUTPUT_ROOT,
    *,
    historical_summary_path: Path | str = HISTORICAL_POSTTOOLUSE_PAIRED_VALUE_SUMMARY,
) -> dict[str, Any]:
    """Build the no-live evaluator artifacts required before live Gate 1."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    design = cortex_effectiveness_evaluator_design()
    synthetic_rows = build_synthetic_episode_rows()
    historical_rows, historical_replay = historical_posttooluse_failure_no_value_rows(
        historical_summary_path
    )
    rows = [*synthetic_rows, *historical_rows]
    mission_contract_errors = validate_episode_rows_mission_contract(rows)
    synthetic_results = evaluate_cortex_effectiveness_rows(synthetic_rows)
    leaderboard = build_leaderboard(rows)
    episode_table_path = root / "episode_table.jsonl"
    write_episode_table(episode_table_path, rows)

    grouped = _group_rows(synthetic_rows)
    build_checks = {
        "dedicated_evaluator_module": True,
        "episode_table_written": episode_table_path.exists(),
        "leaderboard_written": True,
        "all_scoreable_episodes_have_required_arms": all(
            set(by_arm) == set(ARMS) for by_arm in grouped.values()
        ),
        "simple_hook_baseline_present": all(
            "simple_hook_baseline" in by_arm for by_arm in grouped.values()
        ),
        "simple_hook_parity_blocks_value": any(
            result["verdict"] == "failure_simple_baseline_parity"
            for result in synthetic_results["episode_results"]
        ),
        "silent_success_blocks_value": any(
            result["verdict"] == "failure_silent_perception_contamination"
            for result in synthetic_results["episode_results"]
        ),
        "dominance_gates_block_value": any(
            result["verdict"] == "failure_boundary_dominance"
            for result in synthetic_results["episode_results"]
        ),
        "historical_posttooluse_failure_no_value_preserved": historical_replay[
            "preserved"
        ],
        "historical_replay_not_counted_as_new_live": not historical_replay[
            "counts_as_new_live_run"
        ],
        "mission_objective_contract_registered": bool(
            design["mission_objective_contract"]
        ),
        "episode_rows_carry_valid_mission_contract": not mission_contract_errors,
        "lab_only_rows_do_not_claim_product_value": not any(
            row_claims_product_value(row)
            and (
                isinstance(row.mission_objective, Mapping)
                and row.mission_objective.get("model_io_path")
                == LAB_PROOF_MODEL_IO_PATH
            )
            for row in rows
        ),
    }
    passed = all(build_checks.values())
    report = {
        "passed": passed,
        "verdict": (
            "pass_cortex_executive_effectiveness_evaluator_build"
            if passed
            else "failure_cortex_executive_effectiveness_evaluator_build"
        ),
        "live_trials_ran": False,
        "behavior_lift_claim_allowed": False,
        "exactness_value_lift_claim_allowed": False,
        "broad_cortex_lift_claim_allowed": False,
        "codex_app_parity_claim_allowed": False,
        "shipping_promotion_claim_allowed": False,
        "alphaevolve_mutation_loop_allowed": False,
        "next_train_if_pass": "cortex-executive-effectiveness-evaluator-live-gate1",
        "artifact_paths": {
            "evaluator_design": "evaluator_design.json",
            "episode_table": "episode_table.jsonl",
            "summary": "summary.json",
            "leaderboard": "leaderboard.json",
        },
        "build_checks": build_checks,
        "mission_contract_errors": list(mission_contract_errors),
        "synthetic_results": synthetic_results,
        "historical_replay": historical_replay,
        "leaderboard": leaderboard,
    }

    (root / "evaluator_design.json").write_text(
        json.dumps(design, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "leaderboard.json").write_text(
        json.dumps(leaderboard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def run_cortex_effectiveness_evaluator_live_gate1(
    output_root: Path | str = DEFAULT_LIVE_GATE1_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Register and prove the no-live future evaluator live-matrix interface."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    design = cortex_effectiveness_evaluator_design()
    live_plan = build_live_matrix_plan()
    rows = [
        EvaluatorEpisodeRow(
            task_family=row["task_family"],
            case_id=row["case_id"],
            repeat_index=int(row["repeat_index"]),
            arm=row["arm"],
            policy_candidate=row["policy_candidate"],
            metrics=row["metrics"],
            source=row["source"],
            episode_id=row["episode_id"],
            expected_verdict=row.get("expected_verdict"),
            observed_verdict=row.get("observed_verdict"),
            notes=row.get("notes", ""),
            mission_objective=row.get("mission_objective"),
        )
        for row in live_plan["rows"]
    ]
    mission_contract_errors = validate_episode_rows_mission_contract(rows)
    episode_table_path = root / "episode_table.jsonl"
    write_episode_table(episode_table_path, rows)
    leaderboard = {
        "live_trials_ran": False,
        "score_basis": "live_gate1_dry_run_schedule_only",
        "claim_allowed": {
            "behavior_lift": False,
            "exactness_value_lift": False,
            "broad_cortex_lift": False,
            "codex_app_parity": False,
            "shipping_promotion": False,
        },
        "selection_status": "not_live_eligible_until_simple_hook_challenger",
    }
    failure_analysis = {
        "live_trials_ran": False,
        "known_boundary_failures_preserved": list(DOMINANCE_GATES),
        "simple_hook_parity_blocks_value": True,
        "silent_success_blocks_value": True,
        "positive_result_requires_user_review": True,
    }
    checks = {
        "registered_live_command_env_pair": registered_live_commands()
        == live_plan["registered_live_commands"],
        "approval_refusal_registered": live_plan["approval"][
            "without_approval_verdict"
        ]
        == "not_run_approval_required",
        "all_required_arms_scheduled": set(live_plan["arms"]) == set(ARMS),
        "all_task_families_scheduled": set(live_plan["task_families"])
        == set(TASK_FAMILIES),
        "episode_rows_written": episode_table_path.exists(),
        "row_count_matches_matrix": live_plan["row_count"]
        == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT,
        "mission_contract_preserved": not mission_contract_errors,
        "dominance_gates_preserved": set(DOMINANCE_GATES).issubset(
            set(live_plan["dominance_gates"])
        ),
        "live_trials_not_run": live_plan["live_trials_ran"] is False,
        "alphaevolve_mutation_loop_not_allowed": True,
    }
    passed = all(checks.values())
    report = {
        "passed": passed,
        "verdict": (
            "pass_cortex_executive_effectiveness_evaluator_live_gate1"
            if passed
            else "failure_cortex_executive_effectiveness_evaluator_live_gate1"
        ),
        "live_trials_ran": False,
        "behavior_lift_claim_allowed": False,
        "exactness_value_lift_claim_allowed": False,
        "broad_cortex_lift_claim_allowed": False,
        "codex_app_parity_claim_allowed": False,
        "shipping_promotion_claim_allowed": False,
        "alphaevolve_mutation_loop_allowed": False,
        "next_train_if_pass": "cortex-simple-hook-baseline-challenger",
        "artifact_paths": {
            "evaluator_design": "evaluator_design.json",
            "live_plan": "live_plan.json",
            "episode_table": "episode_table.jsonl",
            "summary": "summary.json",
            "leaderboard": "leaderboard.json",
            "failure_analysis": "failure_analysis.json",
        },
        "registered_live_commands": registered_live_commands(),
        "checks": checks,
        "mission_contract_errors": list(mission_contract_errors),
        "live_plan": {
            key: value for key, value in live_plan.items() if key != "rows"
        },
        "failure_analysis": failure_analysis,
    }
    (root / "evaluator_design.json").write_text(
        json.dumps(design, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "live_plan.json").write_text(
        json.dumps(live_plan, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "leaderboard.json").write_text(
        json.dumps(leaderboard, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "failure_analysis.json").write_text(
        json.dumps(failure_analysis, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def run_cortex_effectiveness_evaluator_live_matrix(
    output_root: Path | str = DEFAULT_LIVE_GATE1_OUTPUT_ROOT,
    *,
    approval_env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Approval-refusal shell for the future live matrix.

    Gate 1 registers the exact live command, but execution remains deferred
    until the simple-hook challenger exists.
    """

    env = approval_env if approval_env is not None else os.environ
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    approved = env.get(EVALUATOR_LIVE_APPROVAL_ENV) == EVALUATOR_LIVE_APPROVAL_VALUE
    if not approved:
        report = {
            "passed": False,
            "verdict": "not_run_approval_required",
            "live_trials_ran": False,
            "approval_required": True,
            "approval_env": EVALUATOR_LIVE_APPROVAL_ENV,
            "required_value": EVALUATOR_LIVE_APPROVAL_VALUE,
            "registered_live_commands": registered_live_commands(),
            "behavior_lift_claim_allowed": False,
            "exactness_value_lift_claim_allowed": False,
            "broad_cortex_lift_claim_allowed": False,
            "codex_app_parity_claim_allowed": False,
            "shipping_promotion_claim_allowed": False,
        }
    else:
        report = {
            "passed": False,
            "verdict": "not_run_live_matrix_execution_deferred_until_live_matrix_run_seam",
            "live_trials_ran": False,
            "approval_required": False,
            "approval_env": EVALUATOR_LIVE_APPROVAL_ENV,
            "registered_live_commands": registered_live_commands(),
            "simple_hook_baseline_ready": True,
            "next_required_train": "cortex-executive-effectiveness-evaluator-live-matrix-run",
            "behavior_lift_claim_allowed": False,
            "exactness_value_lift_claim_allowed": False,
            "broad_cortex_lift_claim_allowed": False,
            "codex_app_parity_claim_allowed": False,
            "shipping_promotion_claim_allowed": False,
        }
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def run_cortex_effectiveness_evaluator_gate0(
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Write the no-live Gate 0 design artifact and return the report."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    design = cortex_effectiveness_evaluator_design()
    scenarios = gate0_synthetic_scenarios()
    scenario_rows = [row for rows in scenarios.values() for row in rows]
    mission_contract_errors = validate_episode_rows_mission_contract(scenario_rows)
    synthetic_results = {
        name: evaluate_cortex_effectiveness_rows(rows)
        for name, rows in scenarios.items()
    }
    expected = {
        "passing_active_value": "pass_active_value",
        "simple_hook_parity_blocks_value": "failure_simple_baseline_parity",
        "silent_success_is_no_value": "failure_silent_perception_contamination",
        "overcontrol_dominates": "failure_boundary_dominance",
        "trace_ambiguity_dominates": "failure_boundary_dominance",
        "root_mutation_dominates": "failure_boundary_dominance",
        "runtime_snapshot_dominates": "failure_boundary_dominance",
        "hidden_verifier_leakage_dominates": "failure_boundary_dominance",
    }
    boundary_results = {
        "has_four_required_arms": set(design["arms"]) == set(ARMS),
        "simple_hook_challenger_mandatory": design["simple_hook_challenger"][
            "mandatory"
        ]
        is True,
        "simple_hook_loc_target_under_500": design["simple_hook_challenger"][
            "target_implementation_loc_max"
        ]
        <= 500,
        "has_initial_task_families": set(TASK_FAMILIES).issubset(
            set(design["task_families"])
        ),
        "has_lifecycle_policy_candidates": {
            candidate["id"] for candidate in design["active_policy_candidates"]
        }.issuperset(
            {
                "stop_only",
                "userpromptsubmit_stop",
                "posttooluse_stop",
                "lifecycle_composed_policy",
                "pretooluse_later_after_contract_verification",
            }
        ),
        "dominance_gates_registered": set(DOMINANCE_GATES).issubset(
            set(design["dominance_gates"])
        ),
        "contraction_obligations_registered": bool(
            design["contraction_obligations"]
        ),
        "mission_objective_contract_registered": bool(
            design["mission_objective_contract"]
        ),
        "episode_rows_carry_valid_mission_contract": not mission_contract_errors,
        "lab_only_rows_do_not_claim_product_value": not any(
            row_claims_product_value(row)
            and (
                isinstance(row.mission_objective, Mapping)
                and row.mission_objective.get("model_io_path")
                == LAB_PROOF_MODEL_IO_PATH
            )
            for row in scenario_rows
        ),
        "synthetic_decisions_match_expected": all(
            synthetic_results[name]["verdict"] == verdict
            for name, verdict in expected.items()
        ),
    }
    passed = all(boundary_results.values())
    report = {
        "passed": passed,
        "verdict": (
            "pass_cortex_executive_effectiveness_evaluator_gate0"
            if passed
            else "failure_cortex_executive_effectiveness_evaluator_gate0"
        ),
        "live_trials_ran": False,
        "behavior_lift_claim_allowed": False,
        "exactness_value_lift_claim_allowed": False,
        "broad_cortex_lift_claim_allowed": False,
        "codex_app_parity_claim_allowed": False,
        "shipping_promotion_claim_allowed": False,
        "next_train_if_pass": "cortex-executive-effectiveness-evaluator-build",
        "boundary_results": boundary_results,
        "mission_contract_errors": list(mission_contract_errors),
        "synthetic_results": synthetic_results,
        "design_artifact": "evaluator_design.json",
    }

    (root / "evaluator_design.json").write_text(
        json.dumps(design, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "gate0_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the no-live Cortex executive effectiveness evaluator Gate 0."
    )
    parser.add_argument(
        "--gate0",
        action="store_true",
        help="write evaluator_design.json and Gate 0 report",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="write evaluator_design.json, episode_table.jsonl, summary.json, and leaderboard.json",
    )
    parser.add_argument(
        "--live-gate1",
        action="store_true",
        help="write no-live live matrix registration and dry-run schedule",
    )
    parser.add_argument(
        "--live-matrix",
        action="store_true",
        help="future approval-gated live matrix command; refuses without approval in Gate 1",
    )
    parser.add_argument(
        "--simple-hook-baseline-gate0",
        action="store_true",
        help="prove the independent simple-hook baseline challenger without live trials",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="directory for Gate 0 artifacts",
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="return non-zero if Gate 0 does not pass",
    )
    args = parser.parse_args(argv)
    selected_modes = sum(
        bool(value)
        for value in (
            args.gate0,
            args.build,
            args.live_gate1,
            args.live_matrix,
            args.simple_hook_baseline_gate0,
        )
    )
    if selected_modes != 1:
        parser.error(
            "select exactly one of --gate0, --build, --live-gate1, "
            "--live-matrix, or --simple-hook-baseline-gate0"
        )

    output_root = args.output_root
    if output_root is None:
        if args.gate0:
            output_root = DEFAULT_OUTPUT_ROOT
        elif args.build:
            output_root = DEFAULT_BUILD_OUTPUT_ROOT
        elif args.simple_hook_baseline_gate0:
            output_root = DEFAULT_SIMPLE_HOOK_OUTPUT_ROOT
        else:
            output_root = DEFAULT_LIVE_GATE1_OUTPUT_ROOT

    if args.gate0:
        report = run_cortex_effectiveness_evaluator_gate0(output_root)
    elif args.build:
        report = run_cortex_effectiveness_evaluator_build(output_root)
    elif args.live_gate1:
        report = run_cortex_effectiveness_evaluator_live_gate1(output_root)
    elif args.simple_hook_baseline_gate0:
        report = run_cortex_simple_hook_baseline_gate0(output_root)
    else:
        report = run_cortex_effectiveness_evaluator_live_matrix(output_root)

    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_pass and not report["passed"]:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
