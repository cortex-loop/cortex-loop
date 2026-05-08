"""No-live Cortex executive effectiveness evaluator design gate."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_OUTPUT_ROOT = Path(
    ".cortex/live_validation/cortex_effectiveness_evaluator_gate0"
)

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


@dataclass(frozen=True)
class EvaluatorEpisodeRow:
    """One future evaluator episode row, intentionally arm-neutral."""

    task_family: str
    case_id: str
    repeat_index: int
    arm: str
    policy_candidate: str
    metrics: Mapping[str, Any]

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


def run_cortex_effectiveness_evaluator_gate0(
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
) -> dict[str, Any]:
    """Write the no-live Gate 0 design artifact and return the report."""

    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    design = cortex_effectiveness_evaluator_design()
    scenarios = gate0_synthetic_scenarios()
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
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="directory for Gate 0 artifacts",
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="return non-zero if Gate 0 does not pass",
    )
    args = parser.parse_args(argv)
    if not args.gate0:
        parser.error("select --gate0")

    report = run_cortex_effectiveness_evaluator_gate0(args.output_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_pass and not report["passed"]:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
