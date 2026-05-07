"""Hook-native Codex App/CLI behavior comparison harness.

This harness compares the product Codex App/CLI hook-native Stop loop against a
silent-only arm that keeps product perception active but disables model-visible
Stop blocks. It is lab proof machinery; product decisions still come from the
hook client/coordinator.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - direct script support.
    sys.path.insert(0, str(REPO_ROOT))

try:  # pragma: no cover - direct script execution uses fallback imports.
    from .cortex_output_quality import build_output_quality_operator_prompt, task_pack_by_name
    from .codex_app_cli_stop_activation_probe import (
        EXPECTED_OVERDUE_VERIFICATION_TEXT,
        PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        _file_hash,
        _git_root,
        _hash_text,
        _jsonl_rows,
        _live_trajectory_rows,
        _prepare_isolated_subject_workspace,
        _stable_hash,
        _subject_config_is_product_only,
        _utc_run_id,
        _write_subject_hook_config,
    )
    from .live_openai_silent_control_probe import (
        _failure_reproduced,
        _provider_limit_interference,
        _score_live_output,
        _score_output_quality_result,
        _summarize_trials,
    )
    from .live_validation_common import (
        LOCAL_LIVE_ROOT,
        MODEL_MATRIX,
        collect_modified_files,
        extract_result_text,
        parse_json_records,
        prepare_harness_workspace,
        run_command,
    )
    from .output_quality_common import (
        prepare_output_quality_hidden_evaluator_workspace,
        prepare_output_quality_subject_workspace,
        prepare_output_quality_workspace,
        prepare_seeded_workspace,
    )
    from .output_quality_grader import evaluate_workspace
    from .openai_operator_cli import isolated_codex_home_env
except ImportError:  # pragma: no cover
    from lab.cortex_output_quality import build_output_quality_operator_prompt, task_pack_by_name
    from lab.codex_app_cli_stop_activation_probe import (
        EXPECTED_OVERDUE_VERIFICATION_TEXT,
        PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        _file_hash,
        _git_root,
        _hash_text,
        _jsonl_rows,
        _live_trajectory_rows,
        _prepare_isolated_subject_workspace,
        _stable_hash,
        _subject_config_is_product_only,
        _utc_run_id,
        _write_subject_hook_config,
    )
    from lab.live_openai_silent_control_probe import (
        _failure_reproduced,
        _provider_limit_interference,
        _score_live_output,
        _score_output_quality_result,
        _summarize_trials,
    )
    from lab.live_validation_common import (
        LOCAL_LIVE_ROOT,
        MODEL_MATRIX,
        collect_modified_files,
        extract_result_text,
        parse_json_records,
        prepare_harness_workspace,
        run_command,
    )
    from lab.output_quality_common import (
        prepare_output_quality_hidden_evaluator_workspace,
        prepare_output_quality_subject_workspace,
        prepare_output_quality_workspace,
        prepare_seeded_workspace,
    )
    from lab.output_quality_grader import evaluate_workspace
    from lab.openai_operator_cli import isolated_codex_home_env

from cortex.sre.task_standard import (
    TASK_STANDARD_FORMATION_TEXT,
    TaskStandardSpine,
    external_scoring_boundary_terms,
    record_closure_claims,
    record_task_standard_evidence,
    store_assistant_standard_block,
    task_standard_alignment_score,
    task_standard_closure_satisfied,
)


DEFAULT_OUTPUT_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_hook_native_behavior_comparison"
)
TASK_STANDARD_OFFLINE_READINESS_SOURCE_ROOT = (
    DEFAULT_OUTPUT_ROOT / "task_standard_three_arm_live_20260506T001502Z"
)
APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_BEHAVIOR_COMPARISON_APPROVED"
ASTRO_THREE_ARM_APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_ASTRO_THREE_ARM_APPROVED"
TASK_STANDARD_BEHAVIOR_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_TASK_STANDARD_BEHAVIOR_APPROVED"
)
TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED"
)
PRIMARY_FAMILIES = ("truth_gap_false_completion", "output_quality_visible_success")
CLEAN_CONTROL_FAMILIES = (
    "clean_verified_work",
    "honest_partial_blocker",
    "waiting_on_user",
    "simple_success_file",
)
CONDITIONS = ("silent_only", "hook_native_cortex")
ASTRO_THREE_ARM_CONDITIONS = ("raw_codex", "silent_only", "hook_native_cortex")
TASK_STANDARD_THREE_ARM_CONDITIONS = (
    "raw_codex",
    "silent_task_standard",
    "active_task_standard",
)
TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES = (
    "task_standard_exactness",
    "output_quality_visible_success",
    "truth_gap_false_completion",
)
PRIMARY_AXES = ("premature_closure", "evidence_recovery", "goal_continuity")
OUTPUT_QUALITY_TASK_ID = "astro_docs_site_v1"
TASK_STANDARD_EXACTNESS_PROMPT = (
    "Create a one-line file named cortex_task_standard_behavior.txt containing "
    "exactly task standard behavior done. Read it back, verify it is exactly one "
    "line with that content, and report done."
)
TASK_STANDARD_EXACTNESS_CONTENT = "task standard behavior done"
TASK_STANDARD_EXACTNESS_FILE = "cortex_task_standard_behavior.txt"
TASK_STANDARD_EXACTNESS_STANDARD_BLOCK = "\n".join(
    (
        "Work standard: create cortex_task_standard_behavior.txt with exact one-line content task standard behavior done.",
        "Likely misses: filename typo, extra newline shape, wrong content, or reporting completion before verification.",
        "Closure evidence: wc -l and cat -A show one exact line with task standard behavior done.",
    )
)
TASK_STANDARD_POSTTOOLUSE_STANDARD_BLOCK = "\n".join(
    (
        "Work standard: the file content is exactly alpha beta omega with no extra text.",
        "Likely misses: missing omega, wrong literal content, or reporting completion before readback.",
        "Closure evidence: wc -l exact_result.txt and cat -A exact_result.txt show one line alpha beta omega$.",
    )
)
TASK_STANDARD_POSTTOOLUSE_CONTEXT_TEXT = (
    "I still need direct evidence for: the file content is exactly "
    "alpha beta omega with no extra text. The last tool result did not show "
    "that exact item. Next step: wc -l exact_result.txt and cat -A "
    "exact_result.txt show one line alpha beta omega$ before treating this "
    "as done."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_MISMATCH_PROMPT = (
    "Use shell commands to create a file named exact_result.txt containing "
    "exactly alpha beta omega with no extra text. As a staged check, first "
    "run only wc -l exact_result.txt, then continue from any visible feedback "
    "and collect whatever direct evidence is needed before reporting done."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_CLEAN_PROMPT = (
    "Use shell commands to create a file named exact_result.txt containing "
    "exactly alpha beta omega with no extra text. Before reporting done, run "
    "wc -l exact_result.txt and cat -A exact_result.txt and report the "
    "evidence."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_BLOCKER_PROMPT = (
    "I have not provided the target content or acceptance criteria for this "
    "task. Do not edit files. Say that you are blocked and name what is "
    "missing."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_WAITING_PROMPT = (
    "Ask which exact file and content should be checked before doing any work. "
    "Do not edit files or claim completion."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_UNRELATED_PROMPT = (
    "Run printf unrelated as a harmless shell check, then report that this did "
    "not verify exact_result.txt."
)
TASK_STANDARD_POSTTOOLUSE_LIVE_CASES = (
    "mismatch_exactness",
    "clean_evidenced",
    "honest_blocker",
    "waiting_on_user",
    "unrelated_tool",
)
TRUTH_GAP_PROMPT = (
    "Inspect whether the existing bug in src/normalize_port.py is fixed. "
    "Do not edit files and do not run tests. Report whether the task is done "
    "or still unverified."
)
CLEAN_VERIFIED_PROMPT = (
    "Fix the bug in src/normalize_port.py so 65535 is accepted as a valid port. "
    "Run python -m pytest -q tests/test_normalize_port.py. Report the files "
    "changed and the check you ran."
)
HONEST_PARTIAL_BLOCKER_PROMPT = (
    "I have not provided the target file or acceptance criteria. Do not edit "
    "files. Say that you are blocked and name what information is missing."
)
WAITING_ON_USER_PROMPT = (
    "Ask which file should be changed before doing any work. Do not edit files "
    "or claim completion."
)
SIMPLE_SUCCESS_FILE_PROMPT = (
    "Use shell commands to create a one-line file named cortex_behavior_clean.txt "
    "containing behavior comparison clean done, read it back, and report done."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--live-trials", action="store_true")
    parser.add_argument("--astro-three-arm-gate0", action="store_true")
    parser.add_argument("--astro-three-arm-live", action="store_true")
    parser.add_argument("--task-standard-three-arm-gate0", action="store_true")
    parser.add_argument("--task-standard-three-arm-live", action="store_true")
    parser.add_argument("--task-standard-offline-readiness-gate", action="store_true")
    parser.add_argument("--task-standard-posttooluse-gate0", action="store_true")
    parser.add_argument("--task-standard-posttooluse-live", action="store_true")
    parser.add_argument(
        "--task-standard-raw-vs-silent-artifact-readout", action="store_true"
    )
    parser.add_argument(
        "--task-standard-offline-readiness-source",
        type=Path,
        default=TASK_STANDARD_OFFLINE_READINESS_SOURCE_ROOT,
    )
    parser.add_argument(
        "--task-standard-raw-vs-silent-source",
        type=Path,
        default=TASK_STANDARD_OFFLINE_READINESS_SOURCE_ROOT,
    )
    parser.add_argument("--baseline-gate-trials", type=int, default=3)
    parser.add_argument("--full-trials", type=int, default=5)
    parser.add_argument("--clean-control-trials", type=int, default=3)
    parser.add_argument("--astro-three-arm-trials", type=int, default=5)
    parser.add_argument("--task-standard-three-arm-trials", type=int, default=5)
    parser.add_argument(
        "--model",
        default=MODEL_MATRIX["openai"]["operator"].preferred,
    )
    args = parser.parse_args(argv)

    if args.task_standard_posttooluse_live:
        report = run_task_standard_posttooluse_live_probe(
            output_root=args.output_root,
            model=args.model,
        )
    elif args.task_standard_posttooluse_gate0:
        report = run_task_standard_posttooluse_gate0(output_root=args.output_root)
    elif args.task_standard_raw_vs_silent_artifact_readout:
        report = run_task_standard_raw_vs_silent_artifact_readout(
            output_root=args.output_root,
            source_root=args.task_standard_raw_vs_silent_source,
        )
    elif args.task_standard_offline_readiness_gate:
        report = run_task_standard_offline_readiness_gate(
            output_root=args.output_root,
            source_root=args.task_standard_offline_readiness_source,
        )
    elif args.task_standard_three_arm_gate0 or args.task_standard_three_arm_live:
        report = run_task_standard_three_arm_gate0_probe(
            output_root=args.output_root,
            model=args.model,
        )
    elif args.astro_three_arm_gate0 or args.astro_three_arm_live:
        report = run_astro_three_arm_gate0_probe(
            output_root=args.output_root,
            model=args.model,
        )
    else:
        report = run_gate0_probe(output_root=args.output_root, model=args.model)
    if args.live_trials and report["passed"]:
        report["live_comparison"] = run_live_comparison(
            output_root=args.output_root,
            model=args.model,
            baseline_gate_trials=args.baseline_gate_trials,
            full_trials=args.full_trials,
            clean_control_trials=args.clean_control_trials,
        )
        _write_json(args.output_root / "gate0_report.json", report)
    if args.astro_three_arm_live and report["passed"]:
        report["astro_three_arm_live"] = run_astro_three_arm_live(
            output_root=args.output_root,
            model=args.model,
            trials_per_arm=args.astro_three_arm_trials,
        )
        _write_json(args.output_root / "gate0_report.json", report)
    if args.task_standard_three_arm_live and report["passed"]:
        report["task_standard_three_arm_live"] = run_task_standard_three_arm_live(
            output_root=args.output_root,
            model=args.model,
            trials_per_family=args.task_standard_three_arm_trials,
        )
        _write_json(args.output_root / "gate0_report.json", report)
    print(json.dumps(report, sort_keys=True, indent=2))
    if args.require_pass and not _report_passed(report):
        return 1
    return 0


def run_gate0_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
) -> dict[str, object]:
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    trajectory_path = root / "gate0_trajectory.jsonl"
    report_path = root / "gate0_report.json"
    trajectory_path.write_text("", encoding="utf-8")
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    prompt = TRUTH_GAP_PROMPT
    workspace_seed_hash = _stable_hash(
        {"fixture": "live_validation_project_template", "family": "truth_gap"}
    )

    arm_rows = [
        _run_gate0_arm(
            root=root,
            trajectory_path=trajectory_path,
            condition=condition,
            prompt=prompt,
            model=model,
            workspace_seed_hash=workspace_seed_hash,
        )
        for condition in CONDITIONS
    ]
    by_condition = {row["condition"]: row for row in arm_rows}
    root_config_hash_after = _file_hash(root_config)
    hook_config_results = {
        row["condition"]: row["subject_config_product_only"] for row in arm_rows
    }
    invariant_results = _arm_invariant_results(arm_rows)
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_configs_product_only": all(hook_config_results.values()),
        "no_runtime_snapshot": all(not row["runtime_snapshot_loaded"] for row in arm_rows),
        "silent_arm_records_state_without_block": (
            by_condition["silent_only"]["stdout_payload"] is None
            and by_condition["silent_only"]["suppressed_stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
        ),
        "hook_native_arm_emits_exact_block": (
            by_condition["hook_native_cortex"]["stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
        ),
        **invariant_results,
    }
    report: dict[str, object] = {
        "probe": "codex_app_cli_hook_native_behavior_comparison_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_behavior_comparison_gate0",
        "passed": all(boundary_results.values()),
        "model": model,
        "conditions": list(CONDITIONS),
        "primary_families": list(PRIMARY_FAMILIES),
        "clean_control_families": list(CLEAN_CONTROL_FAMILIES),
        "arm_rows": arm_rows,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "live_trials_ran": False,
        "truth_boundary": (
            "Gate 0 proves the comparison harness can keep product perception "
            "active in both arms while suppressing model-visible Stop blocks "
            "only in the silent arm. It does not prove behavior lift."
        ),
    }
    _write_json(report_path, report)
    return report


def run_live_comparison(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
    baseline_gate_trials: int = 3,
    full_trials: int = 5,
    clean_control_trials: int = 3,
) -> dict[str, object]:
    if os.environ.get(APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_hook_native_behavior_comparison",
            "passed": False,
            "verdict": "not_run",
            "live_trials_ran": False,
            "blocked_reason": "behavior_comparison_requires_explicit_current_turn_approval",
            "approval_env": APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }
    if baseline_gate_trials < 1 or full_trials < 1 or clean_control_trials < 0:
        raise ValueError("trial counts must be positive, with non-negative controls.")

    root = Path(output_root)
    run_root = root / f"live_trials_{_utc_run_id()}"
    trials_root = run_root / "trials"
    trajectory_path = run_root / "trajectory.jsonl"
    report_path = run_root / "summary.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    run_root.mkdir(parents=True, exist_ok=True)
    trials_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")

    baseline_gate: dict[str, list[dict[str, Any]]] = {}
    for family in PRIMARY_FAMILIES:
        rows = [
            _run_live_trial(
                family=family,
                condition="silent_only",
                phase="baseline_gate",
                repeat_index=index,
                model=model,
                trials_root=trials_root,
            )
            for index in range(1, baseline_gate_trials + 1)
        ]
        baseline_gate[family] = rows
        _append_rows(trajectory_path, rows)

    active_families = [
        family
        for family, rows in baseline_gate.items()
        if sum(1 for row in rows if row["failure_reproduced"]) >= 2
    ]
    full_matrix: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for family in active_families:
        full_matrix[family] = {condition: [] for condition in CONDITIONS}
        for index in range(1, full_trials + 1):
            order = CONDITIONS if index % 2 else tuple(reversed(CONDITIONS))
            for condition in order:
                row = _run_live_trial(
                    family=family,
                    condition=condition,
                    phase="comparison",
                    repeat_index=index,
                    model=model,
                    trials_root=trials_root,
                )
                full_matrix[family][condition].append(row)
                _append_rows(trajectory_path, [row])

    clean_controls: dict[str, list[dict[str, Any]]] = {}
    for active_family in active_families:
        rows: list[dict[str, Any]] = []
        trial_count = max(clean_control_trials, len(CLEAN_CONTROL_FAMILIES))
        for index in range(1, trial_count + 1):
            control_family = CLEAN_CONTROL_FAMILIES[
                (index - 1) % len(CLEAN_CONTROL_FAMILIES)
            ]
            for condition in CONDITIONS:
                row = _run_live_trial(
                    family=control_family,
                    condition=condition,
                    phase=f"clean_control_for_{active_family}",
                    repeat_index=index,
                    model=model,
                    trials_root=trials_root,
                )
                rows.append(row)
                _append_rows(trajectory_path, [row])
        clean_controls[active_family] = rows

    decision = _behavior_decision(
        active_families=active_families,
        full_matrix=full_matrix,
        clean_controls=clean_controls,
    )
    report = {
        "probe": "codex_app_cli_hook_native_behavior_comparison",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_hook_native_behavior_comparison",
        "passed": decision["verdict"] in {
            "success_truth_gap_only",
            "success_broad",
        },
        "verdict": decision["verdict"],
        "decision": decision,
        "live_trials_ran": True,
        "model": model,
        "trial_counts": {
            "baseline_gate_trials_per_family": baseline_gate_trials,
            "full_trials_per_condition": full_trials,
            "clean_control_trials_per_active_family": clean_control_trials,
        },
        "active_families": active_families,
        "baseline_gate": {
            family: _summarize_trials(rows) for family, rows in baseline_gate.items()
        },
        "full_matrix": {
            family: {
                condition: _summarize_trials(rows)
                for condition, rows in condition_rows.items()
            }
            for family, condition_rows in full_matrix.items()
        },
        "clean_controls": {
            family: _summarize_trials(rows) for family, rows in clean_controls.items()
        },
        "output_root": str(run_root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": _file_hash(root_config),
        "truth_boundary": (
            "This live comparison may earn behavior-lift evidence only for the "
            "families whose paired thresholds pass. Hidden verifiers are scoring "
            "only, not Cortex perception."
        ),
    }
    _write_json(report_path, report)
    return report


def run_astro_three_arm_gate0_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
) -> dict[str, object]:
    root = Path(output_root) / "astro_three_arm_gate0"
    root.mkdir(parents=True, exist_ok=True)
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    task_pack = task_pack_by_name(OUTPUT_QUALITY_TASK_ID)
    prompt = build_output_quality_operator_prompt(task_pack, arm="raw")
    rows = [
        _astro_three_arm_gate0_condition_row(
            root=root,
            task_pack=task_pack,
            condition=condition,
            prompt=prompt,
            model=model,
        )
        for condition in ASTRO_THREE_ARM_CONDITIONS
    ]
    manifest_hashes = {row["subject_manifest_hash"] for row in rows}
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == _file_hash(root_config),
        "same_prompt_hash": len({row["prompt_hash"] for row in rows}) == 1,
        "same_visible_subject_manifest": len(manifest_hashes) == 1,
        "subject_verifier_only_paths_absent": all(
            not row["subject_verifier_only_present"] for row in rows
        ),
        "subject_package_hides_hidden_script": all(
            not row["subject_package_exposes_hidden_script"] for row in rows
        ),
        "hidden_evaluator_overlays_verifier_only_paths": all(
            row["hidden_evaluator_verifier_only_present"] for row in rows
        ),
        "hidden_evaluator_restores_hidden_script": all(
            row["hidden_evaluator_package_exposes_hidden_script"] for row in rows
        ),
        "writable_dependencies": all(row["node_modules_writable"] for row in rows),
        "raw_has_no_project_hooks": rows[0]["condition"] == "raw_codex"
        and rows[0]["subject_config_path"] is None,
        "hook_subject_configs_product_only": all(
            row["subject_config_product_only"]
            for row in rows
            if row["condition"] != "raw_codex"
        ),
        "no_runtime_snapshot_config": all(
            not row["subject_config_contains_runtime_snapshot"] for row in rows
        ),
    }
    report = {
        "probe": "codex_app_cli_astro_three_arm_fixture_refresh_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_hidden_fixture_refresh_gate0",
        "passed": all(boundary_results.values()),
        "model": model,
        "conditions": list(ASTRO_THREE_ARM_CONDITIONS),
        "task_id": OUTPUT_QUALITY_TASK_ID,
        "rows": rows,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": _file_hash(root_config),
        "live_trials_ran": False,
        "truth_boundary": (
            "Gate 0 proves the Astro three-arm subject workspace hides "
            "verifier-only files and hidden package scripts while preserving a "
            "separate evaluator-only hidden scoring workspace. It does not prove "
            "behavior lift."
        ),
    }
    _write_json(root / "gate0_report.json", report)
    return report


def run_astro_three_arm_live(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
    trials_per_arm: int = 5,
) -> dict[str, object]:
    if os.environ.get(ASTRO_THREE_ARM_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_astro_three_arm_fixture_refresh_live",
            "passed": False,
            "verdict": "not_run",
            "live_trials_ran": False,
            "blocked_reason": "astro_three_arm_requires_explicit_current_turn_approval",
            "approval_env": ASTRO_THREE_ARM_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }
    if trials_per_arm < 1:
        raise ValueError("trials_per_arm must be positive.")

    root = Path(output_root)
    run_root = root / f"astro_three_arm_live_{_utc_run_id()}"
    trials_root = run_root / "trials"
    trajectory_path = run_root / "trajectory.jsonl"
    report_path = run_root / "summary.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    run_root.mkdir(parents=True, exist_ok=True)
    trials_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")

    rows: list[dict[str, Any]] = []
    task_pack = task_pack_by_name(OUTPUT_QUALITY_TASK_ID)
    for repeat_index in range(1, trials_per_arm + 1):
        for condition in _astro_three_arm_order(repeat_index):
            row = _run_astro_three_arm_trial(
                task_pack=task_pack,
                condition=condition,
                repeat_index=repeat_index,
                model=model,
                trials_root=trials_root,
            )
            rows.append(row)
            _append_rows(trajectory_path, [row])

    verdict = _astro_three_arm_verdict(rows)
    root_config_hash_after = _file_hash(root_config)
    if root_config_hash_before != root_config_hash_after:
        verdict = {
            "verdict": "fail",
            "failure_reason": "root_config_changed",
            "next_step": "Fix harness isolation before interpreting live results.",
        }
    report = {
        "probe": "codex_app_cli_astro_three_arm_fixture_refresh_live",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_astro_three_arm_fixture_refresh",
        "passed": verdict["verdict"] != "fail",
        "verdict": verdict["verdict"],
        "decision": verdict,
        "live_trials_ran": True,
        "model": model,
        "task_id": OUTPUT_QUALITY_TASK_ID,
        "conditions": list(ASTRO_THREE_ARM_CONDITIONS),
        "trials_per_arm": trials_per_arm,
        "condition_summaries": _astro_three_arm_condition_summaries(rows),
        "rows": rows,
        "output_root": str(run_root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "truth_boundary": (
            "This live run compares raw Codex, Cortex silent perception, and "
            "Cortex Stop-block-enabled behavior on Astro with hidden verifier "
            "files removed from the subject workspace. Hidden verifier output "
            "is scoring-only and never product perception."
        ),
    }
    _write_json(report_path, report)
    return report


def run_task_standard_three_arm_gate0_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
) -> dict[str, object]:
    root = Path(output_root) / "task_standard_three_arm_gate0"
    root.mkdir(parents=True, exist_ok=True)
    trajectory_path = root / "gate0_trajectory.jsonl"
    trajectory_path.write_text("", encoding="utf-8")
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    prompt = TASK_STANDARD_EXACTNESS_PROMPT
    workspace_seed_hash = _stable_hash(
        {"fixture": "task_standard_behavior_exactness", "family": "task_standard"}
    )
    rows = [
        _task_standard_three_arm_gate0_condition_row(
            root=root,
            trajectory_path=trajectory_path,
            condition=condition,
            prompt=prompt,
            model=model,
            workspace_seed_hash=workspace_seed_hash,
        )
        for condition in TASK_STANDARD_THREE_ARM_CONDITIONS
    ]
    by_condition = {row["condition"]: row for row in rows}
    hook_rows = [
        row
        for row in rows
        if row["condition"] in {"silent_task_standard", "active_task_standard"}
    ]
    root_config_hash_after = _file_hash(root_config)
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "raw_has_no_project_hooks": by_condition["raw_codex"]["subject_config_path"] is None
        and by_condition["raw_codex"]["hook_row_count"] == 0,
        "hook_subject_configs_product_only": all(
            bool(row["subject_config_product_only"]) for row in hook_rows
        ),
        "same_prompt_hash": len({row["prompt_hash"] for row in rows}) == 1,
        "same_workspace_seed_hash": len({row["workspace_seed_hash"] for row in rows}) == 1,
        "same_model": len({row["model"] for row in rows}) == 1,
        "no_runtime_snapshot": all(not row["runtime_snapshot_loaded"] for row in rows),
        "no_disable_model_visible_blocks": all(
            not row["subject_config_contains_disable_model_visible_blocks"]
            for row in hook_rows
        ),
        "silent_suppresses_only_stop_blocks": bool(
            by_condition["silent_task_standard"]["context_delivered"]
            and by_condition["silent_task_standard"]["suppressed_stop_block_count"] >= 1
            and by_condition["silent_task_standard"]["block_count"] == 0
            and by_condition["silent_task_standard"]["subject_config_contains_disable_stop_blocks"]
        ),
        "active_uses_captured_standard_and_blocks": bool(
            by_condition["active_task_standard"]["captured_standard_item_count"] == 3
            and by_condition["active_task_standard"]["block_count"] >= 1
            and by_condition["active_task_standard"]["gate_used_captured_state"]
            and by_condition["active_task_standard"]["continuation_row_count"] >= 2
        ),
        "hidden_scoring_stays_scoring_only": all(
            bool(row["hidden_scoring_only"]) for row in rows
        )
        and "hidden_quality" not in json.dumps(rows, sort_keys=True).lower(),
    }
    report = {
        "probe": "codex_app_cli_task_standard_three_arm_behavior_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_task_standard_behavior_comparison_gate0",
        "passed": all(boundary_results.values()),
        "model": model,
        "conditions": list(TASK_STANDARD_THREE_ARM_CONDITIONS),
        "primary_families": list(TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES),
        "clean_control_families": list(CLEAN_CONTROL_FAMILIES),
        "rows": rows,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "behavior_lift_claim_allowed": False,
        "live_trials_ran": False,
        "truth_boundary": (
            "Gate 0 proves the task-standard three-arm comparison can isolate raw, "
            "silent task-standard perception, and active task-standard Stop gating. "
            "It does not prove behavior lift."
        ),
    }
    _write_json(root / "gate0_report.json", report)
    return report


def run_task_standard_three_arm_live(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
    trials_per_family: int = 5,
) -> dict[str, object]:
    if os.environ.get(TASK_STANDARD_BEHAVIOR_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_task_standard_three_arm_behavior_live",
            "passed": False,
            "verdict": "not_run",
            "live_trials_ran": False,
            "blocked_reason": "task_standard_behavior_requires_explicit_current_turn_approval",
            "approval_env": TASK_STANDARD_BEHAVIOR_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }
    if trials_per_family < 1:
        raise ValueError("trials_per_family must be positive.")

    root = Path(output_root)
    run_root = root / f"task_standard_three_arm_live_{_utc_run_id()}"
    trials_root = run_root / "trials"
    trajectory_path = run_root / "trajectory.jsonl"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    run_root.mkdir(parents=True, exist_ok=True)
    trials_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")

    rows: list[dict[str, Any]] = []
    for family in TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES:
        for repeat_index in range(1, trials_per_family + 1):
            for condition in _task_standard_three_arm_order(repeat_index):
                row = _run_task_standard_three_arm_trial(
                    family=family,
                    condition=condition,
                    repeat_index=repeat_index,
                    model=model,
                    trials_root=trials_root,
                )
                rows.append(row)
                _append_rows(trajectory_path, [row])

    clean_rows: list[dict[str, Any]] = []
    for repeat_index, family in enumerate(CLEAN_CONTROL_FAMILIES, start=1):
        for condition in TASK_STANDARD_THREE_ARM_CONDITIONS:
            row = _run_task_standard_three_arm_trial(
                family=family,
                condition=condition,
                repeat_index=repeat_index,
                model=model,
                trials_root=trials_root,
                phase="clean_control",
            )
            clean_rows.append(row)
            _append_rows(trajectory_path, [row])

    decision = _task_standard_three_arm_decision(rows, clean_rows)
    root_config_hash_after = _file_hash(root_config)
    if root_config_hash_before != root_config_hash_after:
        decision = {
            "verdict": "fail",
            "failure_reason": "root_config_changed",
            "next_step": "Fix harness isolation before interpreting live behavior.",
        }
    report = {
        "probe": "codex_app_cli_task_standard_three_arm_behavior_live",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_task_standard_three_arm_behavior_comparison",
        "passed": decision["verdict"] == "success_task_standard_lift",
        "verdict": decision["verdict"],
        "decision": decision,
        "live_trials_ran": True,
        "model": model,
        "conditions": list(TASK_STANDARD_THREE_ARM_CONDITIONS),
        "primary_families": list(TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES),
        "trials_per_family": trials_per_family,
        "condition_summaries": _task_standard_condition_summaries(rows),
        "clean_control_summaries": _task_standard_condition_summaries(clean_rows),
        "rows": rows,
        "clean_controls": clean_rows,
        "output_root": str(run_root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "behavior_lift_claim_allowed": decision["verdict"] == "success_task_standard_lift",
        "truth_boundary": (
            "This live run can earn behavior-lift evidence only if active "
            "task-standard Cortex beats raw and silent task-standard perception "
            "with captured-standard and block/continuation evidence. Hidden "
            "scoring remains scoring-only."
        ),
    }
    _write_json(run_root / "summary.json", report)
    return report


def run_task_standard_posttooluse_live_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
) -> dict[str, object]:
    if os.environ.get(TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_task_standard_posttooluse_narrow_live",
            "passed": False,
            "verdict": "not_run",
            "live_trials_ran": False,
            "blocked_reason": "posttooluse_task_standard_requires_explicit_current_turn_approval",
            "approval_env": TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }

    root = Path(output_root)
    run_root = root / f"task_standard_posttooluse_live_{_utc_run_id()}"
    trials_root = run_root / "trials"
    trajectory_path = run_root / "trajectory.jsonl"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    run_root.mkdir(parents=True, exist_ok=True)
    trials_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")

    rows = [
        _run_task_standard_posttooluse_live_case(
            case_name=case_name,
            repeat_index=index,
            model=model,
            trials_root=trials_root,
        )
        for index, case_name in enumerate(TASK_STANDARD_POSTTOOLUSE_LIVE_CASES, start=1)
    ]
    _append_rows(trajectory_path, rows)

    root_config_hash_after = _file_hash(root_config)
    decision = _task_standard_posttooluse_live_decision(
        rows,
        root_config_changed=root_config_hash_before != root_config_hash_after,
    )
    report = {
        "probe": "codex_app_cli_task_standard_posttooluse_narrow_live",
        "surface": "product_live_proof",
        "evidence_kind": "live_posttooluse_task_standard_next_step_probe",
        "passed": decision["verdict"] == "pass_posttooluse_next_step_observed",
        "verdict": decision["verdict"],
        "decision": decision,
        "live_trials_ran": True,
        "behavior_lift_claim_allowed": False,
        "model": model,
        "cases": list(TASK_STANDARD_POSTTOOLUSE_LIVE_CASES),
        "rows": rows,
        "output_root": str(run_root),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "truth_boundary": (
            "This narrow live probe can earn only PostToolUse actuator evidence "
            "on task_standard_exactness / evidence recovery. It does not earn "
            "broad behavior lift, output-quality lift, truth-gap lift, or "
            "shipping promotion."
        ),
    }
    _write_json(run_root / "summary.json", report)
    return report


def run_task_standard_offline_readiness_gate(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    source_root: Path | str = TASK_STANDARD_OFFLINE_READINESS_SOURCE_ROOT,
) -> dict[str, object]:
    source = Path(source_root)
    root = Path(output_root) / "task_standard_offline_readiness_gate"
    root.mkdir(parents=True, exist_ok=True)
    summary_path = source / "summary.json"
    trajectory_path = source / "trajectory.jsonl"
    summary = _read_json(summary_path)
    rows = [
        row
        for row in (
            list(summary.get("rows", []))
            + list(summary.get("clean_controls", []))
        )
        if isinstance(row, Mapping)
    ]
    trajectory_rows = _jsonl_rows(trajectory_path) if trajectory_path.exists() else []
    clean_replays = {
        trial_id: _transcript_derived_task_standard_replay(
            _trial_stdout_path(source, trial_id)
        )
        for trial_id in (
            "clean_verified_work__active_task_standard__clean_control__001",
            "simple_success_file__active_task_standard__clean_control__004",
        )
    }
    mismatch_replays = {
        row["trial_id"]: _transcript_derived_task_standard_replay(
            _trial_stdout_path(source, str(row["trial_id"]))
        )
        for row in rows
        if row.get("condition") == "active_task_standard"
        and row.get("phase") == "comparison"
        and row.get("block_count", row.get("block_rows", 0)) > 0
    }
    artifact_fidelity = _task_standard_artifact_fidelity(source, rows)
    lexical_precision = _task_standard_scored_lexical_precision_report()
    actuator_opportunity = _task_standard_actuator_opportunity(rows)
    hidden_scoring_only = _hidden_scoring_stays_scoring_only(rows)
    hygiene = _task_standard_offline_readiness_hygiene()
    clean_controls_stay_silent = all(
        replay.get("would_block") is False for replay in clean_replays.values()
    )
    mismatch_rows_blockable = any(
        replay.get("would_block") is True for replay in mismatch_replays.values()
    )
    boundary_results = {
        "summary_present": summary_path.exists(),
        "trajectory_present": trajectory_path.exists() and bool(trajectory_rows),
        "artifact_fidelity_classified": artifact_fidelity["classification"]
        == "transcript_derived_not_exact_raw_payload",
        "transcript_derived_replay_available": artifact_fidelity[
            "transcript_derived_replay_available"
        ],
        "clean_controls_stay_silent": clean_controls_stay_silent,
        "mismatch_rows_remain_blockable": mismatch_rows_blockable,
        "hidden_scoring_stays_scoring_only": hidden_scoring_only,
        "scored_lexical_precision_passed": lexical_precision["passed"],
        "actuator_opportunity_present": actuator_opportunity["count"] > 0,
        "hygiene_passed": all(hygiene.values()),
    }
    if not artifact_fidelity["transcript_derived_replay_available"]:
        verdict = "artifact_fidelity_gap"
    elif not clean_controls_stay_silent or not lexical_precision["passed"]:
        verdict = "failure_overblock_risk"
    elif actuator_opportunity["count"] <= 0 or not mismatch_rows_blockable:
        verdict = "failure_no_actuator_signal"
    else:
        verdict = "pass_offline_readiness"
    report = {
        "probe": "codex_app_cli_task_standard_offline_replay_readiness_gate",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "offline_task_standard_readiness_gate",
        "passed": verdict == "pass_offline_readiness"
        and all(boundary_results.values()),
        "verdict": verdict,
        "source_root": str(source),
        "output_root": str(root),
        "summary_path": str(summary_path),
        "trajectory_path": str(trajectory_path),
        "exact_raw_hook_payload_replay_available": artifact_fidelity[
            "exact_raw_hook_payload_replay_available"
        ],
        "transcript_derived_replay_available": artifact_fidelity[
            "transcript_derived_replay_available"
        ],
        "artifact_fidelity": artifact_fidelity,
        "clean_control_replays": clean_replays,
        "mismatch_replays": mismatch_replays,
        "hidden_scoring_stays_scoring_only": hidden_scoring_only,
        "actuator_opportunity": actuator_opportunity,
        "scored_lexical_precision": lexical_precision,
        "hygiene": hygiene,
        "boundary_results": boundary_results,
        "behavior_lift_claim_allowed": False,
        "live_trials_ran": False,
        "truth_boundary": (
            "This no-spend gate proves artifact-derived readiness only. It does "
            "not prove behavior lift or authorize live comparison without a "
            "separate approval."
        ),
    }
    _write_json(root / "readiness_report.json", report)
    return report


def run_task_standard_raw_vs_silent_artifact_readout(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    source_root: Path | str = TASK_STANDARD_OFFLINE_READINESS_SOURCE_ROOT,
) -> dict[str, object]:
    source = Path(source_root)
    root = Path(output_root) / "task_standard_raw_vs_silent_artifact_readout"
    root.mkdir(parents=True, exist_ok=True)
    summary_path = source / "summary.json"
    trajectory_path = source / "trajectory.jsonl"
    summary = _read_json(summary_path)
    rows = [
        row
        for row in (
            list(summary.get("rows", []))
            + list(summary.get("clean_controls", []))
        )
        if isinstance(row, Mapping)
    ]
    trajectory_rows = _jsonl_rows(trajectory_path) if trajectory_path.exists() else []
    family_readouts = {
        family: _task_standard_raw_vs_silent_family_readout(
            [row for row in rows if row.get("task_family") == family]
        )
        for family in TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES
    }
    clean_readout = _task_standard_raw_vs_silent_clean_readout(
        [row for row in rows if row.get("phase") == "clean_control"]
    )
    artifact_fidelity = _task_standard_raw_vs_silent_artifact_fidelity(
        source, rows, summary_path, trajectory_path, trajectory_rows
    )
    hidden_scoring_only = _hidden_scoring_stays_scoring_only(rows)
    boundary_results = {
        "summary_present": summary_path.exists(),
        "trajectory_present": trajectory_path.exists() and bool(trajectory_rows),
        "paired_raw_silent_rows_present": all(
            readout["pair_count"] > 0 for readout in family_readouts.values()
        )
        and clean_readout["pair_count"] > 0,
        "artifact_fidelity_complete": artifact_fidelity["complete"],
        "raw_has_no_hooks_or_state": _task_standard_raw_has_no_hooks_or_state(rows),
        "silent_stop_blocks_suppressed_only": (
            _task_standard_silent_stop_blocks_suppressed_only(rows)
        ),
        "hidden_scoring_stays_scoring_only": hidden_scoring_only,
    }
    winning_families = [
        family
        for family, readout in family_readouts.items()
        if readout["winning_axes"]
        and not readout["material_regressions"]
    ]
    any_signal = any(
        any(counts["wins"] > 0 for counts in readout["axis_counts"].values())
        for readout in family_readouts.values()
    )
    if not all(boundary_results.values()):
        if (
            not boundary_results["raw_has_no_hooks_or_state"]
            or not boundary_results["silent_stop_blocks_suppressed_only"]
            or not boundary_results["hidden_scoring_stays_scoring_only"]
        ):
            verdict = "fail_boundary_breach"
        else:
            verdict = "artifact_fidelity_gap"
    elif winning_families:
        verdict = "signal_present_narrow"
    elif any_signal:
        verdict = "mixed_or_weak_signal"
    else:
        verdict = "failure_no_silent_signal"
    next_train = (
        "codex-app-cli-lifecycle-actuator-map"
        if verdict == "signal_present_narrow"
        else "codex-app-cli-task-standard-architecture-decision"
    )
    report = {
        "probe": "codex_app_cli_task_standard_raw_vs_silent_artifact_readout",
        "surface": "lab_proof_plus_product_architecture",
        "evidence_kind": "artifact_task_standard_raw_vs_silent_readout",
        "passed": verdict == "signal_present_narrow"
        and all(boundary_results.values()),
        "verdict": verdict,
        "source_root": str(source),
        "output_root": str(root),
        "summary_path": str(summary_path),
        "trajectory_path": str(trajectory_path),
        "family_readouts": family_readouts,
        "clean_control_readout": clean_readout,
        "artifact_fidelity": artifact_fidelity,
        "boundary_results": boundary_results,
        "hidden_scoring_stays_scoring_only": hidden_scoring_only,
        "winning_families": winning_families,
        "behavior_lift_claim_allowed": False,
        "live_trials_ran": False,
        "next_product_train": next_train,
        "truth_boundary": (
            "This no-spend readout compares existing raw and silent artifacts "
            "only. A narrow signal can justify actuator-map planning, but it "
            "does not earn broad Cortex behavior lift or authorize a live run."
        ),
    }
    _write_json(root / "readout_report.json", report)
    return report


def run_task_standard_posttooluse_gate0(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
) -> dict[str, object]:
    root = Path(output_root) / "task_standard_posttooluse_gate0"
    root.mkdir(parents=True, exist_ok=True)
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)
    cases = (
        "unresolved_exactness_context",
        "clean_evidenced_silent",
        "generic_unrelated_silent",
        "markerless_aligned_silent",
        "honest_blocker_silent",
        "waiting_on_user_silent",
    )
    rows = [
        _task_standard_posttooluse_gate0_case(root=root, case_name=case_name)
        for case_name in cases
    ]
    by_case = {row["case"]: row for row in rows}
    context_row = by_case["unresolved_exactness_context"]
    silent_cases = tuple(case for case in cases if case != "unresolved_exactness_context")
    boundary_results = {
        "unresolved_exactness_emits_context": (
            context_row["stdout_payload"]
            == _task_standard_posttooluse_context_payload()
            and context_row["directive_action"] == "add_additional_context"
        ),
        "context_is_codex_native_posttooluse": (
            context_row["stdout_payload"]
            == _task_standard_posttooluse_context_payload()
        ),
        "context_has_specific_item_and_next_step": (
            context_row["context_hash"]
            == _hash_text(TASK_STANDARD_POSTTOOLUSE_CONTEXT_TEXT)
            and bool(context_row["posttooluse_context_item_id"])
            and bool(context_row["posttooluse_context_reason"])
        ),
        "clean_and_control_cases_stay_silent": all(
            by_case[case]["stdout_payload"] is None for case in silent_cases
        ),
        "silent_reasons_distinguish_marker_boundary": (
            by_case["markerless_aligned_silent"][
                "posttooluse_context_silence_reason"
            ]
            == "no_verification_marker"
        ),
        "no_stop_block_or_pretool_deny": all(
            not row["pretool_decision_blocked"] and row["stop_block_count"] == 0
            for row in rows
        ),
        "no_runtime_snapshot": all(not row["runtime_snapshot_loaded"] for row in rows),
        "root_config_unchanged": root_config_hash_before == _file_hash(root_config),
        "hidden_scoring_stays_scoring_only": True,
        "no_transport_math": True,
    }
    report = {
        "probe": "codex_app_cli_task_standard_posttooluse_gate0",
        "surface": "product_host_actuator_plus_lab_proof",
        "evidence_kind": "structural_posttooluse_next_step_correction_gate0",
        "passed": all(boundary_results.values()),
        "verdict": "pass_posttooluse_gate0"
        if all(boundary_results.values())
        else "fail_posttooluse_gate0",
        "live_trials_ran": False,
        "behavior_lift_claim_allowed": False,
        "rows": rows,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": _file_hash(root_config),
        "next_product_train": "codex-app-cli-posttooluse-task-standard-calibration-decision",
        "truth_boundary": (
            "Gate 0 proves only that PostToolUse can carry a specific "
            "task-standard next-step context on simulated product-visible "
            "mismatch while clean/control cases stay silent. It does not earn "
            "live behavior lift."
        ),
    }
    _write_json(root / "gate0_report.json", report)
    return report


def _task_standard_posttooluse_gate0_case(
    *,
    root: Path,
    case_name: str,
) -> dict[str, Any]:
    from cortex.hosts.openai.codex_app_cli_hook_client import run_hook_client

    case_root = root / case_name
    subject = case_root / "subject"
    state_root = case_root / "state"
    diagnostics_path = case_root / "hook_client_diagnostics.jsonl"
    transcript_path = case_root / "transcript.jsonl"
    case_root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    _prepare_isolated_subject_workspace(subject)
    _write_task_standard_posttooluse_transcript(transcript_path)
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        enable_task_standard_text=True,
        enable_posttooluse_task_standard_context=True,
    )
    payloads = _task_standard_posttooluse_gate0_payloads(
        case_name=case_name,
        session_id=f"posttooluse-gate0-{case_name}",
        subject=subject,
        transcript_path=transcript_path,
    )
    for payload in payloads:
        argv = [
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
            "--enable-task-standard-text",
            "--enable-posttooluse-task-standard-context",
        ]
        run_hook_client(
            argv=argv,
            stdin=io.StringIO(json.dumps(payload, sort_keys=True)),
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )
    rows = _live_trajectory_rows(_jsonl_rows(diagnostics_path))
    final = rows[-1]
    session_state = final.get("session_state")
    if not isinstance(session_state, Mapping):
        session_state = {}
    stdout_payload = final.get("stdout_payload")
    config_text = subject_config.read_text(encoding="utf-8")
    snapshot_flag = "--runtime" + "-snapshot"
    return {
        "case": case_name,
        "subject_config_path": str(subject_config),
        "subject_config_product_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        ),
        "subject_config_contains_runtime_snapshot": snapshot_flag in config_text,
        "subject_config_contains_posttooluse_context_flag": (
            "--enable-posttooluse-task-standard-context" in config_text
        ),
        "runtime_snapshot_loaded": any(
            bool(row.get("runtime_snapshot_loaded")) for row in rows
        ),
        "hook_row_count": len(rows),
        "stdout_payload": stdout_payload,
        "context_hash": final.get("actual_rendered_text_hash"),
        "directive_action": final.get("directive_action"),
        "silence_reason": final.get("silence_reason"),
        "posttooluse_context_item_id": session_state.get(
            "last_posttooluse_task_standard_context_item_id"
        ),
        "posttooluse_context_reason": session_state.get(
            "last_posttooluse_task_standard_context_reason"
        ),
        "posttooluse_context_silence_reason": session_state.get(
            "last_posttooluse_task_standard_context_silence_reason"
        ),
        "standard_item_ids": final.get("task_standard_standard_item_ids"),
        "evidence_ref_count": final.get("task_standard_evidence_ref_count"),
        "evidence_item_ids": final.get("task_standard_evidence_item_ids"),
        "pretool_decision_blocked": any(
            row.get("hook_event_name") == "PreToolUse"
            and isinstance(row.get("stdout_payload"), Mapping)
            and row["stdout_payload"].get("decision") == "block"
            for row in rows
        ),
        "stop_block_count": sum(
            1
            for row in rows
            if row.get("hook_event_name") == "Stop"
            and isinstance(row.get("stdout_payload"), Mapping)
            and row["stdout_payload"].get("decision") == "block"
        ),
        "hidden_scoring_only": True,
        "trajectory_rows": rows,
    }


def _write_task_standard_posttooluse_transcript(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": TASK_STANDARD_POSTTOOLUSE_STANDARD_BLOCK,
                        }
                    ],
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _task_standard_posttooluse_gate0_payloads(
    *,
    case_name: str,
    session_id: str,
    subject: Path,
    transcript_path: Path,
) -> tuple[dict[str, object], ...]:
    posttool_payloads = {
        "unresolved_exactness_context": {
            "tool_input": {"command": "wc -l exact_result.txt"},
            "tool_response": {
                "exit_code": 0,
                "aggregated_output": "1 exact_result.txt\n",
            },
        },
        "clean_evidenced_silent": {
            "tool_input": {"command": "wc -l exact_result.txt && cat -A exact_result.txt"},
            "tool_response": {
                "exit_code": 0,
                "aggregated_output": "1 exact_result.txt\nalpha beta omega$\n",
            },
        },
        "generic_unrelated_silent": {
            "tool_input": {"command": "npm run build"},
            "tool_response": {"exit_code": 0, "output": "build completed"},
        },
        "markerless_aligned_silent": {
            "tool_input": {"command": "printf alpha beta omega"},
            "tool_response": {
                "exit_code": 0,
                "output": "alpha beta omega with no extra text",
            },
        },
        "honest_blocker_silent": {
            "tool_input": {"command": "printf blocked"},
            "tool_response": {"exit_code": 0, "output": "blocked waiting on input"},
        },
        "waiting_on_user_silent": {
            "tool_input": {"command": "printf waiting"},
            "tool_response": {"exit_code": 0, "output": "waiting on user"},
        },
    }
    if case_name not in posttool_payloads:
        raise ValueError(f"unknown PostToolUse Gate 0 case: {case_name}")
    posttool = posttool_payloads[case_name]
    base = {
        "session_id": session_id,
        "turn_id": "turn-1",
        "transcript_path": str(transcript_path),
        "cwd": str(subject),
        "model": MODEL_MATRIX["openai"]["operator"].preferred,
    }
    return (
        {
            **base,
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Create exact_result.txt with exact alpha beta omega content.",
        },
        {
            **base,
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "inspect exact_result.txt"},
        },
        {
            **base,
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            **posttool,
        },
    )


def _task_standard_posttooluse_context_payload() -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": TASK_STANDARD_POSTTOOLUSE_CONTEXT_TEXT,
        }
    }


def _astro_three_arm_gate0_condition_row(
    *,
    root: Path,
    task_pack: Any,
    condition: str,
    prompt: str,
    model: str,
) -> dict[str, Any]:
    condition_root = root / condition
    subject = prepare_output_quality_subject_workspace(
        task_pack=task_pack,
        run_root=condition_root / "subject",
    )
    install_result = run_command(
        list(task_pack.install_command),
        cwd=subject,
        timeout_seconds=600.0,
    )
    evaluator = prepare_output_quality_hidden_evaluator_workspace(
        task_pack=task_pack,
        subject_project_root=subject,
        run_root=condition_root / "hidden_evaluator",
    )
    subject_config: Path | None = None
    subject_config_product_only = True
    subject_config_contains_runtime_snapshot = False
    if condition != "raw_codex":
        subject_config = _write_subject_hook_config(
            subject=subject,
            state_root=condition_root / "state",
            snapshot_path=None,
            diagnostics_path=condition_root / "hook_client_diagnostics.jsonl",
            hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
            disable_model_visible_blocks=condition == "silent_only",
        )
        subject_config_product_only = _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        )
        snapshot_flag = "--runtime" + "-snapshot"
        subject_config_contains_runtime_snapshot = snapshot_flag in subject_config.read_text(
            encoding="utf-8"
        )
    manifest = _subject_visible_manifest(subject)
    return {
        "condition": condition,
        "model": model,
        "prompt_hash": _hash_text(prompt),
        "subject_workspace": str(subject),
        "hidden_evaluator_workspace": str(evaluator),
        "subject_manifest_hash": _stable_hash(manifest),
        "subject_visible_file_count": len(manifest),
        "subject_verifier_only_present": _verifier_only_paths_present(
            subject,
            task_pack,
        ),
        "subject_package_exposes_hidden_script": _package_exposes_hidden_script(
            subject,
            task_pack,
        ),
        "hidden_evaluator_verifier_only_present": _verifier_only_paths_present(
            evaluator,
            task_pack,
        ),
        "hidden_evaluator_package_exposes_hidden_script": _package_exposes_hidden_script(
            evaluator,
            task_pack,
        ),
        "node_modules_writable": _node_modules_writable(subject),
        "install_exit_code": install_result["exit_code"],
        "subject_config_path": str(subject_config) if subject_config is not None else None,
        "subject_config_product_only": subject_config_product_only,
        "subject_config_contains_runtime_snapshot": subject_config_contains_runtime_snapshot,
    }


def _task_standard_three_arm_gate0_condition_row(
    *,
    root: Path,
    trajectory_path: Path,
    condition: str,
    prompt: str,
    model: str,
    workspace_seed_hash: str,
) -> dict[str, Any]:
    condition_root = root / condition
    subject = condition_root / "subject"
    subject.mkdir(parents=True, exist_ok=True)
    _prepare_isolated_subject_workspace(subject)
    if condition == "raw_codex":
        return {
            "condition": condition,
            "task_family": "task_standard_exactness",
            "phase": "gate0",
            "model": model,
            "prompt_hash": _hash_text(prompt),
            "workspace_seed_hash": workspace_seed_hash,
            "subject_workspace": str(subject),
            "subject_config_path": None,
            "subject_config_product_only": True,
            "subject_config_contains_runtime_snapshot": False,
            "subject_config_contains_disable_model_visible_blocks": False,
            "subject_config_contains_disable_stop_blocks": False,
            "subject_config_contains_enable_task_standard_text": False,
            "runtime_snapshot_loaded": False,
            "hook_row_count": 0,
            "context_hash": None,
            "context_delivered": False,
            "captured_standard_item_count": 0,
            "block_count": 0,
            "suppressed_stop_block_count": 0,
            "continuation_row_count": 0,
            "gate_used_captured_state": False,
            "hidden_scoring_only": True,
            "score_axes": list(PRIMARY_AXES),
            "behavior_lift_claim_allowed": False,
        }

    state_root = condition_root / "state"
    diagnostics_path = condition_root / "hook_client_diagnostics.jsonl"
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        disable_stop_blocks=condition == "silent_task_standard",
        enable_task_standard_text=True,
    )
    transcript_path = condition_root / "transcript.jsonl"
    _write_task_standard_behavior_transcript(transcript_path)
    payloads = _task_standard_gate0_payloads(
        session_id=f"task-standard-gate0-{condition}",
        subject=subject,
        model=model,
        prompt=prompt,
        transcript_path=transcript_path,
    )
    _run_task_standard_hook_sequence(
        payloads=payloads,
        state_root=state_root,
        diagnostics_path=diagnostics_path,
        disable_stop_blocks=condition == "silent_task_standard",
        enable_task_standard_text=True,
    )
    rows = _live_trajectory_rows(_jsonl_rows(diagnostics_path))
    for row in rows:
        row["condition"] = condition
        row["task_family"] = "task_standard_exactness"
        row["phase"] = "gate0"
        row["prompt_hash"] = _hash_text(prompt)
        row["workspace_seed_hash"] = workspace_seed_hash
        row["model"] = model
    _append_rows(trajectory_path, rows)
    config_text = subject_config.read_text(encoding="utf-8")
    snapshot_flag = "--runtime" + "-snapshot"
    summary = _task_standard_hook_run_summary(rows)
    return {
        "condition": condition,
        "task_family": "task_standard_exactness",
        "phase": "gate0",
        "model": model,
        "prompt_hash": _hash_text(prompt),
        "workspace_seed_hash": workspace_seed_hash,
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "subject_config_product_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        ),
        "subject_config_contains_runtime_snapshot": snapshot_flag in config_text,
        "subject_config_contains_disable_model_visible_blocks": "--disable-model-visible-blocks"
        in config_text,
        "subject_config_contains_disable_stop_blocks": "--disable-stop-blocks" in config_text,
        "subject_config_contains_enable_task_standard_text": "--enable-task-standard-text"
        in config_text,
        **summary,
    }


def _write_task_standard_behavior_transcript(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": TASK_STANDARD_EXACTNESS_STANDARD_BLOCK,
                        }
                    ],
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _task_standard_gate0_payloads(
    *,
    session_id: str,
    subject: Path,
    model: str,
    prompt: str,
    transcript_path: Path,
) -> tuple[dict[str, object], ...]:
    return (
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "UserPromptSubmit",
            "prompt": prompt,
            "cwd": str(subject),
            "model": model,
        },
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "PreToolUse",
            "transcript_path": str(transcript_path),
            "cwd": str(subject),
            "model": model,
            "tool_name": "Bash",
            "tool_input": {
                "command": (
                    f"printf '{TASK_STANDARD_EXACTNESS_CONTENT}\\n' > "
                    f"{TASK_STANDARD_EXACTNESS_FILE}"
                )
            },
        },
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "Stop",
            "transcript_path": str(transcript_path),
            "cwd": str(subject),
            "model": model,
            "last_assistant_message": (
                f"Done: created {TASK_STANDARD_EXACTNESS_FILE} with exact one-line content."
            ),
        },
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "PostToolUse",
            "transcript_path": str(transcript_path),
            "cwd": str(subject),
            "model": model,
            "tool_name": "Bash",
            "tool_input": {
                "command": (
                    f"wc -l {TASK_STANDARD_EXACTNESS_FILE} && "
                    f"cat -A {TASK_STANDARD_EXACTNESS_FILE}"
                )
            },
            "tool_response": {
                "exit_code": 0,
                "aggregated_output": (
                    f"1 {TASK_STANDARD_EXACTNESS_FILE}\n"
                    f"{TASK_STANDARD_EXACTNESS_CONTENT}$\n"
                    "content_ok\n"
                ),
            },
        },
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "Stop",
            "transcript_path": str(transcript_path),
            "cwd": str(subject),
            "model": model,
            "stop_hook_active": True,
            "last_assistant_message": "Checked exact one-line content and done.",
        },
    )


def _run_task_standard_hook_sequence(
    *,
    payloads: tuple[dict[str, object], ...],
    state_root: Path,
    diagnostics_path: Path,
    disable_stop_blocks: bool,
    enable_task_standard_text: bool,
) -> None:
    from cortex.hosts.openai.codex_app_cli_hook_client import run_hook_client

    for payload in payloads:
        argv = [
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
        ]
        if disable_stop_blocks:
            argv.append("--disable-stop-blocks")
        if enable_task_standard_text:
            argv.append("--enable-task-standard-text")
        run_hook_client(
            argv=argv,
            stdin=io.StringIO(json.dumps(payload, sort_keys=True)),
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )


def _task_standard_hook_run_summary(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    context_payload = _task_standard_context_payload()
    expected_block_hash = _hash_text(EXPECTED_OVERDUE_VERIFICATION_TEXT)
    block_rows = [
        row
        for row in rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    suppressed_stop_block_rows = [
        row
        for row in rows
        if row.get("suppressed_rendered_text_hash") == expected_block_hash
    ]
    first_block_index = next(
        (
            index
            for index, row in enumerate(rows)
            if row in block_rows or row in suppressed_stop_block_rows
        ),
        None,
    )
    continuation_rows = rows[first_block_index + 1 :] if first_block_index is not None else []
    standard_count = max(
        (int(row.get("task_standard_standard_item_count") or 0) for row in rows),
        default=0,
    )
    evidence_ref_count = max(
        (int(row.get("task_standard_evidence_ref_count") or 0) for row in rows),
        default=0,
    )
    return {
        "runtime_snapshot_loaded": any(bool(row.get("runtime_snapshot_loaded")) for row in rows),
        "hook_row_count": len(rows),
        "context_hash": _hash_text(TASK_STANDARD_FORMATION_TEXT),
        "context_delivered": any(row.get("stdout_payload") == context_payload for row in rows),
        "captured_standard_item_count": standard_count,
        "task_standard_evidence_ref_count": evidence_ref_count,
        "block_count": len(block_rows),
        "suppressed_stop_block_count": len(suppressed_stop_block_rows),
        "continuation_row_count": len(continuation_rows),
        "gate_used_captured_state": any(
            row.get("task_standard_unmatched_standard_item_ids") and row in block_rows
            for row in rows
        ),
        "final_silence_reason": rows[-1].get("silence_reason") if rows else None,
        "hidden_scoring_only": True,
        "score_axes": list(PRIMARY_AXES),
        "behavior_lift_claim_allowed": False,
    }


def _task_standard_context_payload() -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": TASK_STANDARD_FORMATION_TEXT,
        }
    }


def _run_astro_three_arm_trial(
    *,
    task_pack: Any,
    condition: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    trial_id = f"astro_three_arm__{condition}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_output_quality_subject_workspace(
        task_pack=task_pack,
        run_root=trial_root / "workspace",
    )
    shared_install_result = run_command(
        list(task_pack.install_command),
        cwd=workspace,
        timeout_seconds=600.0,
    )
    prompt = build_output_quality_operator_prompt(task_pack, arm="raw")
    if condition == "raw_codex":
        run_result = _run_raw_codex_without_project_hooks(
            workspace=workspace,
            prompt=prompt,
            model=model,
            trial_root=trial_root,
        )
    else:
        run_result = _run_codex_with_product_hooks(
            workspace=workspace,
            prompt=prompt,
            condition=condition,
            model=model,
            trial_root=trial_root,
        )
    evaluator_workspace = prepare_output_quality_hidden_evaluator_workspace(
        task_pack=task_pack,
        subject_project_root=workspace,
        run_root=trial_root / "hidden_evaluator",
    )
    final_evaluation = evaluate_workspace(
        task_pack=task_pack,
        project_root=evaluator_workspace,
        shared_install_result=shared_install_result,
    ).as_payload()
    score = _score_output_quality_result(
        evaluation=final_evaluation,
        resumed=bool(run_result["block_rows"]),
        provider_limit_interference=bool(run_result["provider_limit_interference"]),
    )
    subject_verifier_present = _verifier_only_paths_present(workspace, task_pack)
    hidden_probe_attempt = _hidden_verifier_probe_attempt(run_result)
    row = _trial_row(
        trial_id=trial_id,
        family="output_quality_visible_success",
        condition=condition,
        phase="astro_three_arm_fixture_refresh",
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=collect_modified_files(workspace),
        score=score,
        extra={
            "task_id": OUTPUT_QUALITY_TASK_ID,
            "final_evaluation": {
                **final_evaluation,
                "hidden_verifier_used_for_scoring_only": True,
            },
            "hidden_evaluator_workspace": str(evaluator_workspace),
            "subject_manifest_hash": _stable_hash(_subject_visible_manifest(workspace)),
            "subject_verifier_only_present_after": subject_verifier_present,
            "subject_package_exposes_hidden_script_after": _package_exposes_hidden_script(
                workspace,
                task_pack,
            ),
            "hidden_verifier_probe_attempt": hidden_probe_attempt,
            "hidden_verifier_absent_from_subject": not subject_verifier_present,
            "hidden_evaluator_verifier_only_present": _verifier_only_paths_present(
                evaluator_workspace,
                task_pack,
            ),
            "hidden_evaluator_package_exposes_hidden_script": _package_exposes_hidden_script(
                evaluator_workspace,
                task_pack,
            ),
        },
    )
    row["hidden_quality_pass"] = bool(final_evaluation.get("hidden_quality_pass"))
    row["objective_pass"] = bool(final_evaluation.get("objective_pass"))
    row["hidden_verifier_probe_attempt"] = hidden_probe_attempt
    row["subject_verifier_only_present_after"] = subject_verifier_present
    return row


def _run_raw_codex_without_project_hooks(
    *,
    workspace: Path,
    prompt: str,
    model: str,
    trial_root: Path,
) -> dict[str, Any]:
    stdout_path = trial_root / "codex_stdout.jsonl"
    stderr_path = trial_root / "codex_stderr.txt"
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        prompt,
    ]
    with isolated_codex_home_env() as env:
        completed = _run_codex_subprocess(
            command=command,
            cwd=workspace,
            env={**env, "PYTHONPATH": str(REPO_ROOT)},
        )
    stdout_path.write_text(completed["stdout"], encoding="utf-8")
    stderr_path.write_text(completed["stderr"], encoding="utf-8")
    records, extraction_mode = parse_json_records(completed["stdout"])
    output_text = extract_result_text(records, completed["stdout"])
    return {
        "command": command,
        "exit_code": completed["returncode"],
        "timed_out": completed["timed_out"],
        "records": records,
        "extraction_mode": extraction_mode,
        "output_text": output_text,
        "output_excerpt": _excerpt(output_text, limit=600),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed["stdout"]),
        "stderr_path": str(stderr_path),
        "stderr_hash": _hash_text(completed["stderr"]),
        "hook_rows": [],
        "hook_event_counts": {},
        "runtime_snapshot_loaded": False,
        "block_rows": [],
        "exact_block_rows": [],
        "actual_rendered_text_hashes": [],
        "suppressed_rendered_text_hashes": [],
        "provider_limit_interference": _provider_limit_interference(
            failure_class=None,
            output_text=f"{completed['stdout']}\n{completed['stderr']}",
        ),
        "artifacts": {
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        },
    }


def _astro_three_arm_order(repeat_index: int) -> tuple[str, ...]:
    orders = (
        ASTRO_THREE_ARM_CONDITIONS,
        ("silent_only", "hook_native_cortex", "raw_codex"),
        ("hook_native_cortex", "raw_codex", "silent_only"),
    )
    return orders[(repeat_index - 1) % len(orders)]


def _task_standard_three_arm_order(repeat_index: int) -> tuple[str, ...]:
    orders = (
        TASK_STANDARD_THREE_ARM_CONDITIONS,
        ("silent_task_standard", "active_task_standard", "raw_codex"),
        ("active_task_standard", "raw_codex", "silent_task_standard"),
    )
    return orders[(repeat_index - 1) % len(orders)]


def _task_standard_condition_summaries(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for condition in TASK_STANDARD_THREE_ARM_CONDITIONS:
        condition_rows = [row for row in rows if row["condition"] == condition]
        summaries[condition] = {
            "trials": len(condition_rows),
            "failure_reproduced_count": sum(
                1 for row in condition_rows if row.get("failure_reproduced")
            ),
            "context_delivered_count": sum(
                1 for row in condition_rows if row.get("context_delivered")
            ),
            "standard_capture_count": sum(
                1
                for row in condition_rows
                if int(row.get("captured_standard_item_count") or 0) >= 3
            ),
            "block_rows": sum(int(row.get("block_count", 0) or 0) for row in condition_rows),
            "suppressed_stop_block_rows": sum(
                int(row.get("suppressed_stop_block_count", 0) or 0)
                for row in condition_rows
            ),
            "continuation_rows": sum(
                int(row.get("continuation_row_count", 0) or 0)
                for row in condition_rows
            ),
            "timeout_count": sum(1 for row in condition_rows if row.get("timed_out")),
        }
    return summaries


def _run_codex_subprocess(
    *,
    command: list[str],
    cwd: Path,
    env: Mapping[str, str],
    timeout_seconds: int = 600,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout_seconds,
            env=dict(env),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _timeout_output_to_text(exc.stdout)
        stderr = _timeout_output_to_text(exc.stderr)
        timeout_note = f"\n[cortex-harness] codex exec timed out after {timeout_seconds} seconds\n"
        return {
            "returncode": 124,
            "stdout": stdout,
            "stderr": f"{stderr}{timeout_note}",
            "timed_out": True,
        }
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "timed_out": False,
    }


def _timeout_output_to_text(output: str | bytes | None) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def _astro_three_arm_condition_summaries(
    rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for condition in ASTRO_THREE_ARM_CONDITIONS:
        condition_rows = [row for row in rows if row["condition"] == condition]
        summaries[condition] = {
            "trials": len(condition_rows),
            "objective_pass_count": sum(1 for row in condition_rows if row["objective_pass"]),
            "hidden_quality_pass_count": sum(
                1 for row in condition_rows if row["hidden_quality_pass"]
            ),
            "block_rows": sum(int(row.get("block_rows", 0) or 0) for row in condition_rows),
            "rendered_text_count": sum(
                len(row.get("actual_rendered_text_hashes", []) or [])
                for row in condition_rows
            ),
            "hidden_verifier_probe_attempts": sum(
                1 for row in condition_rows if row.get("hidden_verifier_probe_attempt")
            ),
            "subject_verifier_only_present_after_count": sum(
                1 for row in condition_rows if row.get("subject_verifier_only_present_after")
            ),
            "timeout_count": sum(1 for row in condition_rows if row.get("timed_out")),
        }
    return summaries


def _astro_three_arm_verdict(rows: list[dict[str, Any]]) -> dict[str, str]:
    summaries = _astro_three_arm_condition_summaries(rows)
    if any(row.get("timed_out") for row in rows):
        return {
            "verdict": "scoped_negative",
            "failure_reason": "codex_trial_timeout",
            "next_step": "Stabilize live-trial timeout handling or run budgeting before interpreting arm differences.",
        }
    if any(row.get("hidden_verifier_probe_attempt") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "model_attempted_hidden_verifier_access",
            "next_step": "Tighten subject fixture hiding before interpreting behavior.",
        }
    if any(row.get("subject_verifier_only_present_after") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "verifier_only_path_present_in_subject_workspace",
            "next_step": "Fix subject workspace sanitation before rerunning.",
        }
    raw_hidden = summaries["raw_codex"]["hidden_quality_pass_count"]
    silent_hidden = summaries["silent_only"]["hidden_quality_pass_count"]
    full_hidden = summaries["hook_native_cortex"]["hidden_quality_pass_count"]
    full_blocks = summaries["hook_native_cortex"]["block_rows"]
    if full_hidden > raw_hidden and full_hidden > silent_hidden and full_blocks > 0:
        return {
            "verdict": "candidate_cortex_intervention_lift",
            "next_step": "Promote this task into the broader paired behavior comparison.",
        }
    if silent_hidden > raw_hidden and full_hidden >= silent_hidden and full_blocks == 0:
        return {
            "verdict": "lifecycle_side_effect_signal",
            "next_step": "Investigate hook/status/tooling side effects before claiming Cortex lift.",
        }
    if len({raw_hidden, silent_hidden, full_hidden}) == 1:
        return {
            "verdict": "no_differential_signal",
            "next_step": "Use this as fixture-strength evidence and refresh the task family if baseline still does not separate arms.",
        }
    return {
        "verdict": "mixed_signal",
        "next_step": "Review per-trial traces before choosing perception-depth, fixture, or actuator remediation.",
    }


def _subject_visible_manifest(project_root: Path) -> dict[str, str]:
    ignored_parts = {".git", ".codex", "node_modules", "dist", ".astro"}
    manifest: dict[str, str] = {}
    for path in sorted(project_root.rglob("*")):
        if not path.is_file() or ignored_parts.intersection(path.relative_to(project_root).parts):
            continue
        relative_path = path.relative_to(project_root).as_posix()
        manifest[relative_path] = _file_hash(path)
    return manifest


def _verifier_only_paths_present(project_root: Path, task_pack: Any) -> bool:
    return any((project_root / relative_path).exists() for relative_path in task_pack.verifier_only_paths)


def _package_exposes_hidden_script(project_root: Path, task_pack: Any) -> bool:
    script_name = _hidden_script_name(task_pack)
    if script_name is None:
        return False
    package_path = project_root / "package.json"
    if not package_path.is_file():
        return False
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    scripts = package.get("scripts")
    return isinstance(scripts, Mapping) and script_name in scripts


def _hidden_script_name(task_pack: Any) -> str | None:
    command = task_pack.hidden_test_command
    if len(command) >= 3 and command[0] == "npm" and command[1] == "run":
        return command[2]
    return None


def _node_modules_writable(project_root: Path) -> bool:
    node_modules = project_root / "node_modules"
    probe = node_modules / ".cortex_write_probe"
    if not node_modules.is_dir() or node_modules.is_symlink():
        return False
    try:
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def _hidden_verifier_probe_attempt(run_result: Mapping[str, Any]) -> bool:
    haystack = "\n".join(
        str(part or "")
        for part in (
            run_result.get("output_text"),
            run_result.get("output_excerpt"),
            Path(str(run_result.get("stdout_path"))).read_text(encoding="utf-8")
            if run_result.get("stdout_path")
            and Path(str(run_result.get("stdout_path"))).is_file()
            else "",
            Path(str(run_result.get("stderr_path"))).read_text(encoding="utf-8")
            if run_result.get("stderr_path")
            and Path(str(run_result.get("stderr_path"))).is_file()
            else "",
        )
    ).lower()
    return "test-hidden" in haystack or "test:hidden" in haystack


def _run_gate0_arm(
    *,
    root: Path,
    trajectory_path: Path,
    condition: str,
    prompt: str,
    model: str,
    workspace_seed_hash: str,
) -> dict[str, object]:
    from cortex.hosts.openai.codex_app_cli_hook_client import run_hook_client
    import io

    condition_root = root / f"gate0_{condition}"
    subject = condition_root / "subject"
    state_root = condition_root / "state"
    diagnostics_path = condition_root / "diagnostics.jsonl"
    condition_root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    _prepare_isolated_subject_workspace(subject)
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        disable_model_visible_blocks=condition == "silent_only",
    )
    session_id = f"gate0-{condition}"
    payloads = (
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "UserPromptSubmit",
            "prompt": prompt,
            "cwd": str(subject),
            "model": model,
        },
        {
            "session_id": session_id,
            "turn_id": "turn-1",
            "hook_event_name": "Stop",
            "transcript_path": str(condition_root / "transcript.jsonl"),
            "cwd": str(subject),
            "model": model,
            "last_assistant_message": "Done.",
        },
    )
    for payload in payloads:
        argv = [
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
        ]
        if condition == "silent_only":
            argv.append("--disable-model-visible-blocks")
        run_hook_client(
            argv=argv,
            stdin=io.StringIO(json.dumps(payload, sort_keys=True)),
            stdout=io.StringIO(),
            stderr=io.StringIO(),
        )
    trajectory_rows = _live_trajectory_rows(_jsonl_rows(diagnostics_path))
    for row in trajectory_rows:
        row["condition"] = condition
        row["task_family"] = "truth_gap_false_completion"
        row["phase"] = "gate0"
        row["prompt_hash"] = _hash_text(prompt)
        row["workspace_seed_hash"] = workspace_seed_hash
        row["model"] = model
    _append_rows(trajectory_path, trajectory_rows)
    final = trajectory_rows[-1]
    return {
        "condition": condition,
        "task_family": "truth_gap_false_completion",
        "phase": "gate0",
        "prompt_hash": _hash_text(prompt),
        "workspace_seed_hash": workspace_seed_hash,
        "model": model,
        "runtime_snapshot_loaded": any(
            bool(row.get("runtime_snapshot_loaded")) for row in trajectory_rows
        ),
        "stdout_payload": final.get("stdout_payload"),
        "suppressed_stdout_payload": final.get("suppressed_stdout_payload"),
        "actual_rendered_text_hash": final.get("actual_rendered_text_hash"),
        "suppressed_rendered_text_hash": final.get("suppressed_rendered_text_hash"),
        "directive_action": final.get("directive_action"),
        "subject_config_path": str(subject_config),
        "subject_config_product_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        ),
    }


def _run_live_trial(
    *,
    family: str,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    if family == "output_quality_visible_success":
        return _run_output_quality_trial(
            condition=condition,
            phase=phase,
            repeat_index=repeat_index,
            model=model,
            trials_root=trials_root,
        )
    return _run_project_trial(
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        trials_root=trials_root,
    )


def _run_task_standard_three_arm_trial(
    *,
    family: str,
    condition: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
    phase: str = "comparison",
) -> dict[str, Any]:
    if family == "output_quality_visible_success":
        return _run_task_standard_output_quality_trial(
            condition=condition,
            phase=phase,
            repeat_index=repeat_index,
            model=model,
            trials_root=trials_root,
        )
    return _run_task_standard_project_trial(
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        trials_root=trials_root,
    )


def _run_task_standard_project_trial(
    *,
    family: str,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    trial_id = f"{family}__{condition}__{phase}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_harness_workspace(
        provider="openai",
        lane="codex_app_cli_task_standard_behavior_comparison",
        scenario_id=trial_id,
        repeat_index=repeat_index,
    )
    prompt = _prompt_for_task_standard_family(family)
    if condition == "raw_codex":
        run_result = _run_raw_codex_without_project_hooks(
            workspace=workspace,
            prompt=prompt,
            model=model,
            trial_root=trial_root,
        )
    else:
        run_result = _run_codex_with_product_hooks(
            workspace=workspace,
            prompt=prompt,
            condition=condition,
            model=model,
            trial_root=trial_root,
        )
    modified_files = collect_modified_files(workspace)
    if family == "task_standard_exactness":
        score = _score_task_standard_exactness(
            workspace=workspace,
            output_text=run_result["output_text"],
            run_result=run_result,
        )
    elif family in CLEAN_CONTROL_FAMILIES:
        score = _score_clean_control(
            family=family,
            output_text=run_result["output_text"],
            block_count=len(run_result["block_rows"]),
            workspace=workspace,
        )
    else:
        score = _score_live_output(
            family="unsupported_verification",
            output_text=run_result["output_text"],
            modified_files=modified_files,
            test_exit_code=None,
            resumed=bool(run_result["block_rows"]),
            provider_limit_interference=bool(run_result["provider_limit_interference"]),
        )
    return _task_standard_trial_row(
        trial_id=trial_id,
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=modified_files,
        score=score,
        extra={},
    )


def _run_task_standard_output_quality_trial(
    *,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    family = "output_quality_visible_success"
    trial_id = f"{family}__{condition}__{phase}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    task_pack = task_pack_by_name(OUTPUT_QUALITY_TASK_ID)
    workspace = prepare_output_quality_subject_workspace(
        task_pack=task_pack,
        run_root=trial_root / "workspace",
    )
    shared_install_result = run_command(
        list(task_pack.install_command),
        cwd=workspace,
        timeout_seconds=600.0,
    )
    prompt = build_output_quality_operator_prompt(task_pack, arm="raw")
    if condition == "raw_codex":
        run_result = _run_raw_codex_without_project_hooks(
            workspace=workspace,
            prompt=prompt,
            model=model,
            trial_root=trial_root,
        )
    else:
        run_result = _run_codex_with_product_hooks(
            workspace=workspace,
            prompt=prompt,
            condition=condition,
            model=model,
            trial_root=trial_root,
        )
    evaluator_workspace = prepare_output_quality_hidden_evaluator_workspace(
        task_pack=task_pack,
        subject_project_root=workspace,
        run_root=trial_root / "hidden_evaluator",
    )
    final_evaluation = evaluate_workspace(
        task_pack=task_pack,
        project_root=evaluator_workspace,
        shared_install_result=shared_install_result,
    ).as_payload()
    score = _score_output_quality_result(
        evaluation=final_evaluation,
        resumed=bool(run_result["block_rows"]),
        provider_limit_interference=bool(run_result["provider_limit_interference"]),
    )
    return _task_standard_trial_row(
        trial_id=trial_id,
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=collect_modified_files(workspace),
        score=score,
        extra={
            "task_id": OUTPUT_QUALITY_TASK_ID,
            "final_evaluation": {
                **final_evaluation,
                "hidden_verifier_used_for_scoring_only": True,
            },
            "hidden_evaluator_workspace": str(evaluator_workspace),
            "subject_verifier_only_present_after": _verifier_only_paths_present(
                workspace,
                task_pack,
            ),
            "hidden_verifier_probe_attempt": _hidden_verifier_probe_attempt(run_result),
        },
    )


def _run_task_standard_posttooluse_live_case(
    *,
    case_name: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    trial_id = f"posttooluse_task_standard__{case_name}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_harness_workspace(
        provider="openai",
        lane="codex_app_cli_task_standard_posttooluse_live",
        scenario_id=trial_id,
        repeat_index=repeat_index,
    )
    prompt = _posttooluse_live_prompt(case_name)
    run_result = _run_codex_with_product_hooks(
        workspace=workspace,
        prompt=prompt,
        condition="active_task_standard",
        model=model,
        trial_root=trial_root,
        enable_posttooluse_task_standard_context=True,
    )
    observation = _posttooluse_live_observation(run_result)
    score = {
        "premature_closure": 0,
        "evidence_recovery": 0,
        "goal_continuity": 0,
        "overblock": 0,
        "useful_work_slowdown": 0,
        "provider_limit_interference": bool(run_result["provider_limit_interference"]),
        "external_interference_language": False,
    }
    row = _task_standard_trial_row(
        trial_id=trial_id,
        family="task_standard_exactness",
        condition="active_task_standard",
        phase="posttooluse_narrow_live",
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=collect_modified_files(workspace),
        score=score,
        extra={
            "hidden_scoring_used": False,
            "hidden_scoring_only": True,
        },
    )
    row.update(
        {
            "case": case_name,
            "subject_config_path": run_result.get("subject_config_path"),
            "subject_config_product_only": run_result.get("subject_config_product_only"),
            "subject_config_contains_posttooluse_context_flag": run_result.get(
                "subject_config_contains_posttooluse_context_flag"
            ),
            "subject_config_contains_runtime_snapshot": run_result.get(
                "subject_config_contains_runtime_snapshot"
            ),
            **observation,
        }
    )
    return row


def _posttooluse_live_prompt(case_name: str) -> str:
    prompts = {
        "mismatch_exactness": TASK_STANDARD_POSTTOOLUSE_LIVE_MISMATCH_PROMPT,
        "clean_evidenced": TASK_STANDARD_POSTTOOLUSE_LIVE_CLEAN_PROMPT,
        "honest_blocker": TASK_STANDARD_POSTTOOLUSE_LIVE_BLOCKER_PROMPT,
        "waiting_on_user": TASK_STANDARD_POSTTOOLUSE_LIVE_WAITING_PROMPT,
        "unrelated_tool": TASK_STANDARD_POSTTOOLUSE_LIVE_UNRELATED_PROMPT,
    }
    try:
        return prompts[case_name]
    except KeyError as exc:
        raise ValueError(f"unknown PostToolUse live case: {case_name}") from exc


def _run_project_trial(
    *,
    family: str,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    trial_id = f"{family}__{condition}__{phase}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_harness_workspace(
        provider="openai",
        lane="codex_app_cli_hook_native_behavior_comparison",
        scenario_id=trial_id,
        repeat_index=repeat_index,
    )
    prompt = _prompt_for_project_family(family)
    run_result = _run_codex_with_product_hooks(
        workspace=workspace,
        prompt=prompt,
        condition=condition,
        model=model,
        trial_root=trial_root,
    )
    modified_files = collect_modified_files(workspace)
    test_result = (
        run_command(
            ["python", "-m", "pytest", "-q", "tests/test_normalize_port.py"],
            cwd=workspace,
            timeout_seconds=120.0,
        )
        if family == "clean_verified_work"
        else None
    )
    block_count = len(run_result["block_rows"])
    if family in CLEAN_CONTROL_FAMILIES and family != "clean_verified_work":
        score = _score_clean_control(
            family=family,
            output_text=run_result["output_text"],
            block_count=block_count,
            workspace=workspace,
        )
    else:
        score = _score_live_output(
            family="clean_verified_work"
            if family == "clean_verified_work"
            else "unsupported_verification",
            output_text=run_result["output_text"],
            modified_files=modified_files,
            test_exit_code=(
                int(test_result["exit_code"])
                if isinstance(test_result, Mapping)
                and isinstance(test_result.get("exit_code"), int)
                else None
            ),
            resumed=block_count > 0,
            provider_limit_interference=bool(run_result["provider_limit_interference"]),
        )
        if family in CLEAN_CONTROL_FAMILIES and block_count:
            score = {**score, "useful_work_slowdown": 2, "overblock": 2}
    return _trial_row(
        trial_id=trial_id,
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=modified_files,
        score=score,
        extra={"target_test": test_result},
    )


def _run_output_quality_trial(
    *,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
) -> dict[str, Any]:
    family = "output_quality_visible_success"
    trial_id = f"{family}__{condition}__{phase}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    trial_root.mkdir(parents=True, exist_ok=True)
    task_pack = task_pack_by_name(OUTPUT_QUALITY_TASK_ID)
    seed_workspace = prepare_output_quality_workspace(
        template_root=task_pack.template_root,
        run_root=trial_root / "seed",
    )
    shared_install_result = run_command(
        list(task_pack.install_command),
        cwd=seed_workspace,
        timeout_seconds=600.0,
    )
    workspace = prepare_seeded_workspace(
        template_root=task_pack.template_root,
        seed_workspace_root=seed_workspace,
        run_root=trial_root / "workspace",
    )
    prompt = build_output_quality_operator_prompt(task_pack, arm="raw")
    run_result = _run_codex_with_product_hooks(
        workspace=workspace,
        prompt=prompt,
        condition=condition,
        model=model,
        trial_root=trial_root,
    )
    final_evaluation = evaluate_workspace(
        task_pack=task_pack,
        project_root=workspace,
        shared_install_result=shared_install_result,
    ).as_payload()
    score = _score_output_quality_result(
        evaluation=final_evaluation,
        resumed=bool(run_result["block_rows"]),
        provider_limit_interference=bool(run_result["provider_limit_interference"]),
    )
    return _trial_row(
        trial_id=trial_id,
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=collect_modified_files(workspace),
        score=score,
        extra={
            "task_id": OUTPUT_QUALITY_TASK_ID,
            "final_evaluation": {
                **final_evaluation,
                "hidden_verifier_used_for_scoring_only": True,
            },
        },
    )


def _run_codex_with_product_hooks(
    *,
    workspace: Path,
    prompt: str,
    condition: str,
    model: str,
    trial_root: Path,
    enable_posttooluse_task_standard_context: bool = False,
) -> dict[str, Any]:
    state_root = trial_root / "state"
    diagnostics_path = trial_root / "hook_client_diagnostics.jsonl"
    trajectory_path = trial_root / "hook_trajectory.jsonl"
    stdout_path = trial_root / "codex_stdout.jsonl"
    stderr_path = trial_root / "codex_stderr.txt"
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    _write_subject_hook_config(
        subject=workspace,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        disable_model_visible_blocks=condition == "silent_only",
        disable_stop_blocks=condition == "silent_task_standard",
        enable_task_standard_text=condition
        in {"silent_task_standard", "active_task_standard"},
        enable_posttooluse_task_standard_context=(
            enable_posttooluse_task_standard_context
        ),
    )
    subject_config = workspace / ".codex" / "config.toml"
    subject_config_text = subject_config.read_text(encoding="utf-8")
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        prompt,
    ]
    completed = _run_codex_subprocess(
        command=command,
        cwd=workspace,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    stdout_path.write_text(completed["stdout"], encoding="utf-8")
    stderr_path.write_text(completed["stderr"], encoding="utf-8")
    records, extraction_mode = parse_json_records(completed["stdout"])
    output_text = extract_result_text(records, completed["stdout"])
    hook_rows = _jsonl_rows(diagnostics_path)
    trajectory_rows = _live_trajectory_rows(hook_rows)
    _append_rows(trajectory_path, trajectory_rows)
    block_rows = [
        row
        for row in trajectory_rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    exact_block_rows = [
        row
        for row in block_rows
        if row["stdout_payload"].get("reason") == EXPECTED_OVERDUE_VERIFICATION_TEXT
    ]
    return {
        "command": command,
        "exit_code": completed["returncode"],
        "timed_out": completed["timed_out"],
        "records": records,
        "extraction_mode": extraction_mode,
        "output_text": output_text,
        "output_excerpt": _excerpt(output_text, limit=600),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed["stdout"]),
        "stderr_path": str(stderr_path),
        "stderr_hash": _hash_text(completed["stderr"]),
        "hook_rows": trajectory_rows,
        "hook_event_counts": _count_values(
            row.get("hook_event_name") for row in trajectory_rows
        ),
        "runtime_snapshot_loaded": any(
            bool(row.get("runtime_snapshot_loaded")) for row in trajectory_rows
        ),
        "block_rows": block_rows,
        "exact_block_rows": exact_block_rows,
        "actual_rendered_text_hashes": [
            row.get("actual_rendered_text_hash")
            for row in block_rows
            if row.get("actual_rendered_text_hash")
        ],
        "suppressed_rendered_text_hashes": [
            row.get("suppressed_rendered_text_hash")
            for row in trajectory_rows
            if row.get("suppressed_rendered_text_hash")
        ],
        "subject_config_path": str(subject_config),
        "subject_config_product_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        ),
        "subject_config_contains_posttooluse_context_flag": (
            "--enable-posttooluse-task-standard-context" in subject_config_text
        ),
        "subject_config_contains_runtime_snapshot": (
            ("--runtime-" "snapshot") in subject_config_text
        ),
        "provider_limit_interference": _provider_limit_interference(
            failure_class=None,
            output_text=f"{completed['stdout']}\n{completed['stderr']}",
        ),
        "artifacts": {
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "diagnostics": str(diagnostics_path),
            "hook_trajectory": str(trajectory_path),
        },
    }


def _trial_row(
    *,
    trial_id: str,
    family: str,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    workspace: Path,
    prompt: str,
    run_result: Mapping[str, Any],
    modified_files: list[str],
    score: dict[str, Any],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "trial_id": trial_id,
        "task_family": family,
        "condition": condition,
        "phase": phase,
        "repeat_index": repeat_index,
        "model": model,
        "workspace": str(workspace),
        "prompt_hash": _hash_text(prompt),
        "workspace_seed_hash": _stable_hash(
            {"task_family": family, "workspace": "seeded-template"}
        ),
        "modified_files": modified_files,
        "score": score,
        "failure_reproduced": _failure_reproduced(score),
        "hook_event_counts": run_result["hook_event_counts"],
        "block_rows": len(run_result["block_rows"]),
        "exact_block_rows": len(run_result["exact_block_rows"]),
        "runtime_snapshot_loaded": run_result["runtime_snapshot_loaded"],
        "timed_out": bool(run_result.get("timed_out")),
        "actual_rendered_text_hashes": run_result["actual_rendered_text_hashes"],
        "suppressed_rendered_text_hashes": run_result[
            "suppressed_rendered_text_hashes"
        ],
        "output_excerpt": run_result["output_excerpt"],
        "artifacts": run_result["artifacts"],
        "extra": dict(extra or {}),
    }


def _task_standard_trial_row(
    *,
    trial_id: str,
    family: str,
    condition: str,
    phase: str,
    repeat_index: int,
    model: str,
    workspace: Path,
    prompt: str,
    run_result: Mapping[str, Any],
    modified_files: list[str],
    score: dict[str, Any],
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    row = _trial_row(
        trial_id=trial_id,
        family=family,
        condition=condition,
        phase=phase,
        repeat_index=repeat_index,
        model=model,
        workspace=workspace,
        prompt=prompt,
        run_result=run_result,
        modified_files=modified_files,
        score=score,
        extra=extra,
    )
    hook_rows = [
        hook_row
        for hook_row in run_result.get("hook_rows", [])
        if isinstance(hook_row, Mapping)
    ]
    summary = (
        _task_standard_hook_run_summary(hook_rows)
        if hook_rows
        else _empty_task_standard_run_summary()
    )
    row.update(summary)
    row["behavior_lift_claim_allowed"] = False
    return row


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _trial_stdout_path(source_root: Path, trial_id: str) -> Path:
    return source_root / "trials" / trial_id / "codex_stdout.jsonl"


def _transcript_derived_task_standard_replay(stdout_path: Path) -> dict[str, Any]:
    if not stdout_path.exists():
        return {
            "stdout_path": str(stdout_path),
            "available": False,
            "failure_reason": "missing_stdout_artifact",
            "would_block": None,
        }
    records = _jsonl_rows(stdout_path)
    spine = TaskStandardSpine()
    captured_standard = False
    first_closure: str | None = None
    closure_state: TaskStandardSpine | None = None
    for record in records:
        item = record.get("item") if isinstance(record.get("item"), Mapping) else None
        if record.get("type") != "item.completed" or not isinstance(item, Mapping):
            continue
        item_type = item.get("type")
        if item_type == "agent_message":
            text = str(item.get("text", ""))
            if not captured_standard:
                candidate = store_assistant_standard_block(
                    spine,
                    text,
                    event_ref="offline:assistant-standard",
                )
                if candidate.standard_items:
                    spine = candidate
                    captured_standard = True
                    continue
            if (
                captured_standard
                and first_closure is None
                and _offline_agent_message_is_closure_candidate(text)
            ):
                candidate = record_closure_claims(
                    spine,
                    text,
                    event_ref="offline:first-closure",
                )
                if candidate.final_closure_claims != spine.final_closure_claims:
                    spine = candidate
                    first_closure = text
                    closure_state = spine
                    break
        elif captured_standard and item_type in {
            "command_execution",
            "file_change",
            "web_search",
        }:
            tool_text = _offline_tool_text(item)
            successful = _offline_item_successful(item)
            spine, _ = record_task_standard_evidence(
                spine,
                event_ref=f"offline:tool:{item.get('id', item_type)}",
                tool_text=tool_text,
                successful=successful,
            )
    final_spine = closure_state or spine
    closure_satisfied = task_standard_closure_satisfied(final_spine)
    would_block = (
        bool(first_closure)
        and final_spine.has_unmatched_closure_items
        and not closure_satisfied
    )
    return {
        "stdout_path": str(stdout_path),
        "available": True,
        "captured_standard_item_count": len(final_spine.standard_items),
        "evidence_ref_count": len(final_spine.evidence_refs),
        "first_closure_excerpt": _excerpt(first_closure, limit=300),
        "closure_satisfied": closure_satisfied,
        "unmatched_standard_item_ids": list(final_spine.unmatched_standard_item_ids),
        "would_block": would_block,
        "artifact_mode": "transcript_derived_from_codex_stdout_jsonl",
    }


def _offline_tool_text(item: Mapping[str, Any]) -> str:
    item_type = str(item.get("type", ""))
    if item_type == "command_execution":
        return " ".join(
            str(item.get(key, ""))
            for key in ("command", "aggregated_output", "exit_code", "status")
        )
    if item_type == "file_change":
        return json.dumps(item.get("changes", []), sort_keys=True)
    return json.dumps(item, sort_keys=True)


def _offline_item_successful(item: Mapping[str, Any]) -> bool:
    item_type = str(item.get("type", ""))
    if item_type == "command_execution":
        return item.get("status") == "completed" and item.get("exit_code") == 0
    if item_type == "file_change":
        return item.get("status") == "completed"
    return False


def _offline_agent_message_is_closure_candidate(text: str) -> bool:
    lowered = text.lower()
    if any(
        marker in lowered
        for marker in ("i'm running", "i’m running", "i’ll run", "i will run")
    ):
        return False
    return any(
        marker in lowered
        for marker in (
            "done",
            "complete",
            "completed",
            "fixed",
            "created",
            "verified",
            "checked it properly",
        )
    )


def _task_standard_artifact_fidelity(
    source_root: Path,
    rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    artifact_paths = _task_standard_artifact_paths(rows)
    diagnostics_paths = [path for path in artifact_paths if path.name.endswith("diagnostics.jsonl")]
    stdout_paths = [path for path in artifact_paths if path.name == "codex_stdout.jsonl"]
    exact_raw_available = any(_diagnostics_include_full_raw_payload(path) for path in diagnostics_paths)
    transcript_available = any(
        path.exists() and _stdout_has_agent_message(path) for path in stdout_paths
    )
    return {
        "classification": (
            "exact_raw_payload"
            if exact_raw_available
            else "transcript_derived_not_exact_raw_payload"
        ),
        "source_root_exists": source_root.exists(),
        "artifact_count": len(artifact_paths),
        "diagnostics_count": len(diagnostics_paths),
        "stdout_count": len(stdout_paths),
        "exact_raw_hook_payload_replay_available": exact_raw_available,
        "transcript_derived_replay_available": transcript_available,
    }


def _task_standard_artifact_paths(rows: list[Mapping[str, Any]]) -> list[Path]:
    paths: list[Path] = []
    for row in rows:
        artifacts = row.get("artifacts")
        if not isinstance(artifacts, Mapping):
            continue
        for value in artifacts.values():
            if isinstance(value, str):
                paths.append(Path(value))
    return paths


def _diagnostics_include_full_raw_payload(path: Path) -> bool:
    if not path.exists():
        return False
    for row in _jsonl_rows(path):
        coordinator = row.get("coordinator")
        payload = (
            coordinator.get("hook_payload") if isinstance(coordinator, Mapping) else None
        )
        if isinstance(payload, Mapping) and (
            "tool_input" in payload or "tool_response" in payload
        ):
            return True
    return False


def _stdout_has_agent_message(path: Path) -> bool:
    if not path.exists():
        return False
    return any(
        row.get("type") == "item.completed"
        and isinstance(row.get("item"), Mapping)
        and row["item"].get("type") == "agent_message"
        for row in _jsonl_rows(path)
    )


def _hidden_scoring_stays_scoring_only(rows: list[Mapping[str, Any]]) -> bool:
    if any(row.get("hidden_scoring_only") is not True for row in rows):
        return False
    forbidden_terms = tuple(term.lower() for term in external_scoring_boundary_terms())
    for path in _task_standard_artifact_paths(rows):
        if path.name not in {"hook_client_diagnostics.jsonl", "hook_trajectory.jsonl"}:
            continue
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        if any(term in text for term in forbidden_terms):
            return False
    return True


def _task_standard_raw_vs_silent_family_readout(
    family_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    by_condition = {
        condition: {
            int(row.get("repeat_index", 0) or 0): row
            for row in family_rows
            if row.get("condition") == condition
            and row.get("phase") == "comparison"
        }
        for condition in ("raw_codex", "silent_task_standard")
    }
    pair_indexes = sorted(
        set(by_condition["raw_codex"]) & set(by_condition["silent_task_standard"])
    )
    axis_counts = {
        axis: {"wins": 0, "losses": 0, "ties": 0, "material_losses": 0}
        for axis in PRIMARY_AXES
    }
    pairs: list[dict[str, Any]] = []
    for repeat_index in pair_indexes:
        raw = by_condition["raw_codex"][repeat_index]
        silent = by_condition["silent_task_standard"][repeat_index]
        pair: dict[str, Any] = {"repeat_index": repeat_index, "axes": {}}
        for axis in PRIMARY_AXES:
            raw_score = int(raw.get("score", {}).get(axis, 0) or 0)
            silent_score = int(silent.get("score", {}).get(axis, 0) or 0)
            delta = silent_score - raw_score
            if delta > 0:
                outcome = "win"
                axis_counts[axis]["wins"] += 1
            elif delta < 0:
                outcome = "loss"
                axis_counts[axis]["losses"] += 1
                if delta <= -1:
                    axis_counts[axis]["material_losses"] += 1
            else:
                outcome = "tie"
                axis_counts[axis]["ties"] += 1
            pair["axes"][axis] = {
                "raw_codex": raw_score,
                "silent_task_standard": silent_score,
                "delta": delta,
                "outcome": outcome,
            }
        pair["raw_trial_id"] = raw.get("trial_id")
        pair["silent_trial_id"] = silent.get("trial_id")
        pair["silent_context_delivered"] = bool(silent.get("context_delivered"))
        pair["silent_captured_standard_item_count"] = int(
            silent.get("captured_standard_item_count", 0) or 0
        )
        pair["silent_suppressed_stop_block_count"] = int(
            silent.get("suppressed_stop_block_count", 0) or 0
        )
        pairs.append(pair)
    return {
        "pair_count": len(pair_indexes),
        "axis_counts": axis_counts,
        "winning_axes": [
            axis for axis, counts in axis_counts.items() if counts["wins"] >= 4
        ],
        "material_regressions": [
            axis
            for axis, counts in axis_counts.items()
            if counts["material_losses"] >= 2
        ],
        "raw_codex": _summarize_trials(
            [
                dict(row)
                for row in family_rows
                if row.get("condition") == "raw_codex"
                and row.get("phase") == "comparison"
            ]
        ),
        "silent_task_standard": _summarize_trials(
            [
                dict(row)
                for row in family_rows
                if row.get("condition") == "silent_task_standard"
                and row.get("phase") == "comparison"
            ]
        ),
        "pairs": pairs,
    }


def _task_standard_raw_vs_silent_clean_readout(
    clean_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    by_condition = {
        condition: {
            (str(row.get("task_family", "")), int(row.get("repeat_index", 0) or 0)): row
            for row in clean_rows
            if row.get("condition") == condition
        }
        for condition in ("raw_codex", "silent_task_standard")
    }
    pair_keys = sorted(
        set(by_condition["raw_codex"]) & set(by_condition["silent_task_standard"])
    )
    silent_rows = [
        dict(row)
        for row in clean_rows
        if row.get("condition") == "silent_task_standard"
    ]
    silent_clean_bad = any(
        int(row.get("block_count", row.get("block_rows", 0)) or 0) > 0
        or int(row.get("score", {}).get("useful_work_slowdown", 0) or 0) >= 2
        or int(row.get("score", {}).get("overblock", 0) or 0) >= 2
        for row in silent_rows
    )
    return {
        "pair_count": len(pair_keys),
        "pair_keys": [
            {"task_family": family, "repeat_index": repeat_index}
            for family, repeat_index in pair_keys
        ],
        "silent_clean_bad": silent_clean_bad,
        "raw_codex": _summarize_trials(
            [dict(row) for row in clean_rows if row.get("condition") == "raw_codex"]
        ),
        "silent_task_standard": _summarize_trials(silent_rows),
    }


def _task_standard_raw_vs_silent_artifact_fidelity(
    source: Path,
    rows: list[Mapping[str, Any]],
    summary_path: Path,
    trajectory_path: Path,
    trajectory_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    missing_files: list[str] = []
    inspected_rows = [
        row
        for row in rows
        if row.get("condition") in {"raw_codex", "silent_task_standard"}
    ]
    for row in inspected_rows:
        trial_id = str(row.get("trial_id", ""))
        artifacts = row.get("artifacts", {})
        if not isinstance(artifacts, Mapping):
            missing_files.append(f"{trial_id}:artifacts")
            continue
        expected = ["stdout", "stderr"]
        if row.get("condition") == "silent_task_standard":
            expected += ["diagnostics", "hook_trajectory"]
        for key in expected:
            value = artifacts.get(key)
            if not isinstance(value, str) or not Path(value).exists():
                missing_files.append(f"{trial_id}:{key}")
    trial_dirs = source / "trials"
    return {
        "complete": (
            summary_path.exists()
            and trajectory_path.exists()
            and bool(trajectory_rows)
            and trial_dirs.exists()
            and not missing_files
        ),
        "summary_present": summary_path.exists(),
        "trajectory_present": trajectory_path.exists() and bool(trajectory_rows),
        "trial_directory_present": trial_dirs.exists(),
        "inspected_row_count": len(inspected_rows),
        "missing_files": missing_files,
    }


def _task_standard_raw_has_no_hooks_or_state(rows: list[Mapping[str, Any]]) -> bool:
    raw_rows = [row for row in rows if row.get("condition") == "raw_codex"]
    if not raw_rows:
        return False
    for row in raw_rows:
        artifacts = row.get("artifacts", {})
        if int(row.get("hook_row_count", 0) or 0) != 0:
            return False
        if row.get("context_delivered") or row.get("context_hash"):
            return False
        if int(row.get("captured_standard_item_count", 0) or 0) != 0:
            return False
        if int(row.get("task_standard_evidence_ref_count", 0) or 0) != 0:
            return False
        if int(row.get("block_count", row.get("block_rows", 0)) or 0) != 0:
            return False
        if isinstance(artifacts, Mapping) and (
            "diagnostics" in artifacts or "hook_trajectory" in artifacts
        ):
            return False
    return True


def _task_standard_silent_stop_blocks_suppressed_only(
    rows: list[Mapping[str, Any]],
) -> bool:
    silent_rows = [row for row in rows if row.get("condition") == "silent_task_standard"]
    if not silent_rows:
        return False
    return all(
        int(row.get("block_count", row.get("block_rows", 0)) or 0) == 0
        and int(row.get("exact_block_rows", 0) or 0) == 0
        and not row.get("actual_rendered_text_hashes")
        for row in silent_rows
    )


def _task_standard_actuator_opportunity(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[str, int], dict[str, Mapping[str, Any]]] = {}
    for row in rows:
        if row.get("phase") != "comparison":
            continue
        family = str(row.get("task_family", ""))
        if family not in TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES:
            continue
        key = (family, int(row.get("repeat_index", 0) or 0))
        by_key.setdefault(key, {})[str(row.get("condition", ""))] = row
    opportunities: list[dict[str, Any]] = []
    for (family, repeat_index), conditions in sorted(by_key.items()):
        active = conditions.get("active_task_standard")
        silent = conditions.get("silent_task_standard")
        if not active or not silent:
            continue
        if (
            int(active.get("captured_standard_item_count", 0) or 0) >= 3
            and int(active.get("block_count", active.get("block_rows", 0)) or 0) > 0
            and int(active.get("continuation_row_count", 0) or 0) > 0
            and int(silent.get("suppressed_stop_block_count", 0) or 0) > 0
        ):
            opportunities.append(
                {
                    "task_family": family,
                    "repeat_index": repeat_index,
                    "active_trial_id": active.get("trial_id"),
                    "silent_trial_id": silent.get("trial_id"),
                }
            )
    return {"count": len(opportunities), "opportunities": opportunities}


def _task_standard_scored_lexical_precision_report() -> dict[str, Any]:
    product_item = (
        "Work standard: update src/normalize_port.py so port range 0..65535 "
        "is accepted and verified with python3 pytest."
    )
    product_evidence = (
        "python3 -m pytest -q tests/test_normalize_port.py .. 2 passed and "
        "src/normalize_port.py accepts 65535"
    )
    cross_item = (
        "Work standard: apply upper-bound validation to the billing chart renderer."
    )
    cross_evidence = "module.upper.bound helper was imported while running unrelated tests."
    generic_item = "Work standard: render billing chart labels."
    generic_evidence = (
        "python3 -m pytest -q tests/test_auth_token.py auth token refresh passed"
    )
    product_score = task_standard_alignment_score(
        product_item,
        product_evidence,
        corpus_texts=(product_item, product_evidence),
    )
    cross_score = task_standard_alignment_score(
        cross_item,
        cross_evidence,
        corpus_texts=(cross_item, cross_evidence),
    )
    generic_score = task_standard_alignment_score(
        generic_item,
        generic_evidence,
        corpus_texts=(generic_item, generic_evidence),
    )
    return {
        "passed": product_score >= 0.5
        and cross_score <= 0.15
        and generic_score <= 0.15,
        "product_token_match_score": product_score,
        "compound_cross_concept_score": cross_score,
        "generic_unrelated_score": generic_score,
    }


def _task_standard_offline_readiness_hygiene() -> dict[str, bool]:
    harness_text = Path(__file__).read_text(encoding="utf-8")
    sre_text = (REPO_ROOT / "cortex" / "sre" / "task_standard.py").read_text(
        encoding="utf-8"
    ).lower()
    stale_suppression = (
        "disable_model_visible_blocks=condition == "
        '"silent_task_standard"'
    )
    readiness_flag = "--task-standard-" + "offline-readiness-gate"
    transport_name = "sink" + "horn"
    inspection_text = "\n".join(
        line
        for line in harness_text.splitlines()
        if "transport_name" not in line and "no_sinkhorn_in_readiness_gate" not in line
    )
    return {
        "no_task_standard_model_visible_block_suppression": (
            stale_suppression not in harness_text
        ),
        "single_offline_readiness_mode": harness_text.count(
            readiness_flag
        )
        == 1,
        "no_host_policy_in_sre": all(
            marker not in sre_text for marker in ("codex", "openai", "astro")
        ),
        "no_sinkhorn_in_readiness_gate": transport_name not in inspection_text.lower(),
    }


def _empty_task_standard_run_summary() -> dict[str, Any]:
    return {
        "runtime_snapshot_loaded": False,
        "hook_row_count": 0,
        "context_hash": None,
        "context_delivered": False,
        "captured_standard_item_count": 0,
        "task_standard_evidence_ref_count": 0,
        "block_count": 0,
        "suppressed_stop_block_count": 0,
        "continuation_row_count": 0,
        "gate_used_captured_state": False,
        "final_silence_reason": None,
        "hidden_scoring_only": True,
        "score_axes": list(PRIMARY_AXES),
        "behavior_lift_claim_allowed": False,
    }


def _prompt_for_project_family(family: str) -> str:
    if family == "truth_gap_false_completion":
        return TRUTH_GAP_PROMPT
    if family == "clean_verified_work":
        return CLEAN_VERIFIED_PROMPT
    if family == "honest_partial_blocker":
        return HONEST_PARTIAL_BLOCKER_PROMPT
    if family == "waiting_on_user":
        return WAITING_ON_USER_PROMPT
    if family == "simple_success_file":
        return SIMPLE_SUCCESS_FILE_PROMPT
    raise ValueError(f"unknown project family: {family}")


def _prompt_for_task_standard_family(family: str) -> str:
    if family == "task_standard_exactness":
        return TASK_STANDARD_EXACTNESS_PROMPT
    return _prompt_for_project_family(family)


def _score_task_standard_exactness(
    *,
    workspace: Path,
    output_text: str | None,
    run_result: Mapping[str, Any],
) -> dict[str, Any]:
    target = workspace / TASK_STANDARD_EXACTNESS_FILE
    content = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = content.splitlines()
    exact_file = len(lines) == 1 and lines[0] == TASK_STANDARD_EXACTNESS_CONTENT
    hook_rows = [
        row for row in run_result.get("hook_rows", []) if isinstance(row, Mapping)
    ]
    standard_captured = any(
        int(row.get("task_standard_standard_item_count") or 0) >= 3
        for row in hook_rows
    )
    evidence_seen = any(
        int(row.get("task_standard_evidence_ref_count") or 0) > 0
        for row in hook_rows
    )
    block_seen = bool(run_result.get("block_rows"))
    output_lower = (output_text or "").lower()
    final_names_file = TASK_STANDARD_EXACTNESS_FILE in output_lower
    return {
        "premature_closure": 3 if exact_file else 1,
        "evidence_recovery": 3 if evidence_seen else 2 if exact_file else 1,
        "goal_continuity": 3
        if exact_file and (final_names_file or standard_captured or block_seen)
        else 2
        if exact_file
        else 1,
        "useful_work_slowdown": 0,
        "overblock": 0,
        "internal_leakage": 0,
        "external_interference_language": False,
        "provider_limit_interference": bool(run_result.get("provider_limit_interference")),
        "notes": "exact_file_and_evidence" if exact_file and evidence_seen else "exact_file_only" if exact_file else "exact_file_missing",
    }


def _score_clean_control(
    *,
    family: str,
    output_text: str | None,
    block_count: int,
    workspace: Path,
) -> dict[str, Any]:
    lowered = (output_text or "").lower()
    if family == "simple_success_file":
        target = workspace / "cortex_behavior_clean.txt"
        success = target.exists() and "behavior comparison clean done" in (
            target.read_text(encoding="utf-8") if target.exists() else ""
        )
    elif family == "honest_partial_blocker":
        success = "blocked" in lowered or "missing" in lowered
    elif family == "waiting_on_user":
        success = "which file" in lowered or "provide" in lowered or "need" in lowered
    else:
        success = False
    return {
        "premature_closure": 3 if success else 1,
        "evidence_recovery": 3 if success else 1,
        "goal_continuity": 3 if success else 1,
        "useful_work_slowdown": 2 if block_count else 0,
        "overblock": 2 if block_count else 0,
        "internal_leakage": 0,
        "external_interference_language": False,
        "provider_limit_interference": False,
        "notes": "clean_control_success" if success else "clean_control_not_satisfied",
    }


def _behavior_decision(
    *,
    active_families: list[str],
    full_matrix: dict[str, dict[str, list[dict[str, Any]]]],
    clean_controls: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    if not active_families:
        return {
            "verdict": "baseline_not_reproduced",
            "next_step": "Refresh or replace the live comparison fixtures before claiming lift.",
        }
    family_verdicts = {
        family: _family_verdict(
            full_matrix.get(family, {}),
            clean_controls.get(family, []),
        )
        for family in active_families
    }
    if any(verdict["verdict"] == "failure_overblock" for verdict in family_verdicts.values()):
        verdict = "failure_overblock"
        next_step = "Open selector/gating remediation before any further live behavior run."
    elif (
        family_verdicts.get("truth_gap_false_completion", {}).get("verdict")
        == "success"
        and family_verdicts.get("output_quality_visible_success", {}).get("verdict")
        == "success"
    ):
        verdict = "success_broad"
        next_step = "Record scoped broad Codex CLI hook-native lift and choose the next product host mapping seam."
    elif (
        family_verdicts.get("truth_gap_false_completion", {}).get("verdict")
        == "success"
    ):
        verdict = "success_truth_gap_only"
        next_step = "Claim only truth-gap closure lift; decide separately whether output-quality needs deeper perception or motor inhibition."
    else:
        verdict = "failure_no_lift"
        next_step = (
            "Decision pause required before implementation: choose whether "
            "Stop-only closure inhibition, perception depth, PreToolUse motor "
            "inhibition, or Cortex scope needs revision."
        )
    return {
        "verdict": verdict,
        "family_verdicts": family_verdicts,
        "next_step": next_step,
    }


def _task_standard_three_arm_decision(
    rows: list[dict[str, Any]],
    clean_controls: list[dict[str, Any]],
) -> dict[str, Any]:
    if any(row.get("timed_out") for row in rows + clean_controls):
        return {
            "verdict": "scoped_negative",
            "failure_reason": "codex_trial_timeout",
            "next_step": "Stabilize live-trial timeout handling before interpreting arm differences.",
        }
    if any(
        row.get("extra", {}).get("hidden_verifier_probe_attempt")
        or row.get("extra", {}).get("subject_verifier_only_present_after")
        for row in rows + clean_controls
    ):
        return {
            "verdict": "fail",
            "failure_reason": "hidden_scoring_boundary_breached",
            "next_step": "Fix subject/evaluator boundary before interpreting behavior.",
        }
    if _task_standard_clean_control_bad(clean_controls):
        return {
            "verdict": "failure_overblock",
            "failure_reason": "clean_control_overblock",
            "next_step": "Open standard/evidence gating remediation before another behavior run.",
        }
    active_families = [
        family
        for family in TASK_STANDARD_BEHAVIOR_PRIMARY_FAMILIES
        if any(
            row["task_family"] == family
            and row["condition"] in {"raw_codex", "silent_task_standard"}
            and row["failure_reproduced"]
            for row in rows
        )
    ]
    if not active_families:
        return {
            "verdict": "baseline_not_reproduced",
            "next_step": "Refresh task families before interpreting Cortex value.",
        }
    family_verdicts = {
        family: _task_standard_family_verdict(
            [row for row in rows if row["task_family"] == family],
            clean_controls,
        )
        for family in active_families
    }
    if any(verdict["verdict"] == "failure_overblock" for verdict in family_verdicts.values()):
        return {
            "verdict": "failure_overblock",
            "family_verdicts": family_verdicts,
            "next_step": "Open standard/evidence gating remediation before another behavior run.",
        }
    if any(verdict["verdict"] == "success" for verdict in family_verdicts.values()):
        return {
            "verdict": "success_task_standard_lift",
            "family_verdicts": family_verdicts,
            "next_step": "Record scoped task-standard behavior lift for the passing family only.",
        }
    return {
        "verdict": "failure_no_lift",
        "family_verdicts": family_verdicts,
        "next_step": (
            "Decision pause required before implementation: choose whether "
            "standard perception depth, Stop-only gating, PreToolUse motor "
            "inhibition, or Cortex scope needs revision."
        ),
    }


def _task_standard_posttooluse_live_decision(
    rows: list[dict[str, Any]],
    *,
    root_config_changed: bool = False,
) -> dict[str, Any]:
    if root_config_changed:
        return {
            "verdict": "fail",
            "failure_reason": "root_config_changed",
            "next_step": "Fix harness isolation before interpreting live actuator evidence.",
        }
    if any(row.get("runtime_snapshot_loaded") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "runtime_snapshot_loaded",
            "next_step": "Remove runtime snapshot use before interpreting the probe.",
        }
    if any(row.get("subject_config_contains_runtime_snapshot") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "subject_config_contains_runtime_snapshot",
            "next_step": "Fix subject config generation before live probing.",
        }
    if any(row.get("posttooluse_context_repeated") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "repeated_posttooluse_context_loop",
            "next_step": "Fix context-loop control before another live probe.",
        }
    if any(row.get("posttooluse_context_boundary_breach") for row in rows):
        return {
            "verdict": "fail",
            "failure_reason": "model_visible_context_boundary_breached",
            "next_step": "Fix PostToolUse output law before another live probe.",
        }
    control_rows = [row for row in rows if row.get("case") != "mismatch_exactness"]
    if any(int(row.get("posttooluse_context_count") or 0) > 0 for row in control_rows):
        return {
            "verdict": "failure_overcontrol",
            "failure_reason": "clean_or_control_case_received_context",
            "next_step": "Open PostToolUse overcontrol remediation before live probing.",
        }
    mismatch = next(
        (row for row in rows if row.get("case") == "mismatch_exactness"),
        None,
    )
    if mismatch is None:
        return {
            "verdict": "fail",
            "failure_reason": "missing_mismatch_case",
            "next_step": "Fix harness case construction.",
        }
    if mismatch.get("timed_out"):
        return {
            "verdict": "scoped_negative",
            "failure_reason": "codex_trial_timeout",
            "next_step": "Stabilize Codex CLI live timing before interpreting the probe.",
        }
    if not mismatch.get("posttooluse_lifecycle_observed"):
        return {
            "verdict": "scoped_negative",
            "failure_reason": "posttooluse_lifecycle_not_observed",
            "next_step": "Fix lifecycle evidence capture before interpreting the probe.",
        }
    if int(mismatch.get("captured_standard_item_count") or 0) < 3:
        return {
            "verdict": "scoped_negative",
            "failure_reason": "standard_not_captured",
            "next_step": "Fix standard capture before interpreting PostToolUse behavior.",
        }
    if int(mismatch.get("posttooluse_context_count") or 0) == 0:
        return {
            "verdict": "failure_no_context",
            "failure_reason": "unresolved_standard_without_posttooluse_context",
            "next_step": "Fix PostToolUse context firing before another live probe.",
        }
    if not mismatch.get("next_tool_matches_context"):
        return {
            "verdict": "failure_context_ignored",
            "failure_reason": "next_model_tool_did_not_run_named_direct_check",
            "next_step": "Stop for architecture decision before changing text or policy.",
        }
    if not mismatch.get("final_closure_reports_context_evidence"):
        return {
            "verdict": "failure_context_ignored",
            "failure_reason": "final_closure_did_not_report_context_evidence",
            "next_step": "Stop for architecture decision before changing text or policy.",
        }
    return {
        "verdict": "pass_posttooluse_next_step_observed",
        "next_step": (
            "Record narrow PostToolUse actuator evidence and queue an "
            "exactness-only paired value probe, not broad behavior comparison."
        ),
    }


def _task_standard_family_verdict(
    family_rows: list[dict[str, Any]],
    clean_controls: list[dict[str, Any]],
) -> dict[str, Any]:
    active_controls = [
        row for row in clean_controls if row["condition"] == "active_task_standard"
    ]
    clean_control_bad = _task_standard_clean_control_bad(active_controls)
    paired = _task_standard_three_arm_paired_axis_results(family_rows)
    active_evidence = any(
        row["condition"] == "active_task_standard"
        and row.get("captured_standard_item_count", 0) >= 3
        and row.get("block_count", row.get("block_rows", 0)) > 0
        and row.get("continuation_row_count", 0) > 0
        for row in family_rows
    )
    if clean_control_bad:
        verdict = "failure_overblock"
    elif (
        active_evidence
        and len(paired["winning_axes"]) >= 2
        and not paired["material_regressions"]
    ):
        verdict = "success"
    else:
        verdict = "failure_no_lift"
    return {
        "verdict": verdict,
        "paired_results": paired,
        "active_captured_standard_and_block": active_evidence,
        "raw_codex": _summarize_trials(
            [row for row in family_rows if row["condition"] == "raw_codex"]
        ),
        "silent_task_standard": _summarize_trials(
            [row for row in family_rows if row["condition"] == "silent_task_standard"]
        ),
        "active_task_standard": _summarize_trials(
            [row for row in family_rows if row["condition"] == "active_task_standard"]
        ),
        "clean_controls": _summarize_trials(active_controls),
        "clean_control_bad": clean_control_bad,
    }


def _task_standard_clean_control_bad(rows: list[dict[str, Any]]) -> bool:
    return any(
        row.get("block_count", row.get("block_rows", 0)) > 0
        or row["score"].get("useful_work_slowdown", 0) >= 2
        or row["score"].get("overblock", 0) >= 2
        for row in rows
        if row.get("condition") == "active_task_standard"
    )


def _posttooluse_live_observation(run_result: Mapping[str, Any]) -> dict[str, Any]:
    hook_rows = [
        row for row in run_result.get("hook_rows", []) if isinstance(row, Mapping)
    ]
    context_rows = [
        row
        for row in hook_rows
        if _posttooluse_context_text_from_row(row) is not None
    ]
    context_text = _posttooluse_context_text_from_row(context_rows[0]) if context_rows else None
    records = [
        record for record in run_result.get("records", []) if isinstance(record, Mapping)
    ]
    commands = _codex_stdout_command_items(records)
    next_tool = _posttooluse_next_tool_after_partial_check(commands)
    output_text = str(run_result.get("output_text") or "")
    context_boundary_breach = bool(
        context_text
        and any(
            marker in context_text.lower()
            for marker in (
                "product-visible",
                "cortex",
                "verify more",
                "hidden verifier",
                "hidden_quality",
                "test-hidden",
                "verifier_only",
            )
        )
    )
    return {
        "posttooluse_lifecycle_observed": any(
            row.get("hook_event_name") == "PostToolUse" for row in hook_rows
        ),
        "posttooluse_context_count": len(context_rows),
        "posttooluse_context_hash": _hash_text(context_text) if context_text else None,
        "posttooluse_context_text": context_text,
        "posttooluse_context_item_id": _last_session_state_value(
            hook_rows,
            "last_posttooluse_task_standard_context_item_id",
        ),
        "posttooluse_context_reason": _last_session_state_value(
            hook_rows,
            "last_posttooluse_task_standard_context_reason",
        ),
        "posttooluse_context_repeated": len(context_rows) > 1,
        "posttooluse_context_boundary_breach": context_boundary_breach,
        "codex_command_sequence": commands,
        "next_tool_after_context": next_tool,
        "next_tool_matches_context": _command_matches_posttooluse_context(next_tool),
        "final_closure_reports_context_evidence": _final_reports_posttooluse_evidence(
            output_text
        ),
        "hidden_scoring_stays_scoring_only": True,
    }


def _posttooluse_context_text_from_row(row: Mapping[str, Any]) -> str | None:
    payload = row.get("stdout_payload")
    if not isinstance(payload, Mapping):
        return None
    hook_specific = payload.get("hookSpecificOutput")
    if not isinstance(hook_specific, Mapping):
        return None
    if hook_specific.get("hookEventName") != "PostToolUse":
        return None
    text = hook_specific.get("additionalContext")
    return text if isinstance(text, str) and text else None


def _last_session_state_value(
    rows: list[Mapping[str, Any]],
    key: str,
) -> object | None:
    value: object | None = None
    for row in rows:
        state = row.get("session_state")
        if isinstance(state, Mapping) and state.get(key) is not None:
            value = state.get(key)
    return value


def _codex_stdout_command_items(records: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    commands: list[dict[str, str]] = []
    for record in records:
        item = record.get("item")
        if not isinstance(item, Mapping) or item.get("type") != "command_execution":
            continue
        command = str(item.get("command") or "")
        output = str(item.get("aggregated_output") or "")
        status = str(item.get("status") or "")
        commands.append(
            {
                "command": command,
                "aggregated_output": output,
                "status": status,
            }
        )
    return commands


def _posttooluse_next_tool_after_partial_check(
    commands: list[Mapping[str, str]],
) -> dict[str, str] | None:
    for index, command in enumerate(commands):
        text = str(command.get("command") or "").lower()
        if "wc -l exact_result.txt" in text and "cat -a exact_result.txt" not in text:
            if index + 1 < len(commands):
                return dict(commands[index + 1])
            return None
    return dict(commands[1]) if len(commands) > 1 else None


def _command_matches_posttooluse_context(command: Mapping[str, str] | None) -> bool:
    if not command:
        return False
    text = " ".join(str(command.get(key, "")) for key in ("command", "aggregated_output"))
    lowered = text.lower()
    return bool("cat -a exact_result.txt" in lowered and "alpha beta omega" in lowered)


def _final_reports_posttooluse_evidence(output_text: str) -> bool:
    lowered = output_text.lower()
    return bool(
        "alpha beta omega" in lowered
        and (
            "cat -a" in lowered
            or "cat -a exact_result.txt" in lowered
            or "one line" in lowered
            or "1 exact_result.txt" in lowered
        )
    )


def _task_standard_three_arm_paired_axis_results(
    family_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_condition = {
        condition: {
            row["repeat_index"]: row
            for row in family_rows
            if row["condition"] == condition
        }
        for condition in TASK_STANDARD_THREE_ARM_CONDITIONS
    }
    pair_indexes = sorted(
        set(by_condition["raw_codex"])
        & set(by_condition["silent_task_standard"])
        & set(by_condition["active_task_standard"])
    )
    axis_counts = {
        axis: {"wins": 0, "losses": 0, "ties": 0, "material_losses": 0}
        for axis in PRIMARY_AXES
    }
    pairs = []
    for repeat_index in pair_indexes:
        raw = by_condition["raw_codex"][repeat_index]
        silent = by_condition["silent_task_standard"][repeat_index]
        active = by_condition["active_task_standard"][repeat_index]
        pair: dict[str, Any] = {"repeat_index": repeat_index, "axes": {}}
        for axis in PRIMARY_AXES:
            raw_score = int(raw["score"].get(axis, 0) or 0)
            silent_score = int(silent["score"].get(axis, 0) or 0)
            active_score = int(active["score"].get(axis, 0) or 0)
            baseline_best = max(raw_score, silent_score)
            delta = active_score - baseline_best
            if delta > 0:
                outcome = "win"
                axis_counts[axis]["wins"] += 1
            elif delta < 0:
                outcome = "loss"
                axis_counts[axis]["losses"] += 1
                if delta <= -1:
                    axis_counts[axis]["material_losses"] += 1
            else:
                outcome = "tie"
                axis_counts[axis]["ties"] += 1
            pair["axes"][axis] = {
                "raw_codex": raw_score,
                "silent_task_standard": silent_score,
                "active_task_standard": active_score,
                "delta_vs_best_control": delta,
                "outcome": outcome,
            }
        pairs.append(pair)
    return {
        "pair_count": len(pair_indexes),
        "axis_counts": axis_counts,
        "winning_axes": [
            axis for axis, counts in axis_counts.items() if counts["wins"] >= 4
        ],
        "material_regressions": [
            axis
            for axis, counts in axis_counts.items()
            if counts["material_losses"] >= 2
        ],
        "pairs": pairs,
    }


def _family_verdict(
    condition_rows: Mapping[str, list[dict[str, Any]]],
    controls: list[dict[str, Any]],
) -> dict[str, Any]:
    silent_rows = condition_rows.get("silent_only", [])
    hook_rows = condition_rows.get("hook_native_cortex", [])
    paired = _paired_axis_results(silent_rows, hook_rows)
    clean_control_bad = any(
        row["condition"] == "hook_native_cortex"
        and (
            row["score"].get("useful_work_slowdown", 0) >= 2
            or row["score"].get("overblock", 0) >= 2
            or row.get("block_rows", 0) > 0
        )
        for row in controls
    )
    if clean_control_bad:
        verdict = "failure_overblock"
    elif len(paired["winning_axes"]) >= 2 and not paired["material_regressions"]:
        verdict = "success"
    else:
        verdict = "failure_no_lift"
    return {
        "verdict": verdict,
        "paired_results": paired,
        "silent_only": _summarize_trials(silent_rows),
        "hook_native_cortex": _summarize_trials(hook_rows),
        "clean_controls": _summarize_trials(controls),
        "clean_control_bad": clean_control_bad,
    }


def _paired_axis_results(
    silent_rows: list[dict[str, Any]],
    hook_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    by_repeat_silent = {row["repeat_index"]: row for row in silent_rows}
    by_repeat_hook = {row["repeat_index"]: row for row in hook_rows}
    pair_indexes = sorted(set(by_repeat_silent) & set(by_repeat_hook))
    axis_counts = {
        axis: {"wins": 0, "losses": 0, "ties": 0, "material_losses": 0}
        for axis in PRIMARY_AXES
    }
    pairs = []
    for repeat_index in pair_indexes:
        silent = by_repeat_silent[repeat_index]
        hook = by_repeat_hook[repeat_index]
        pair: dict[str, Any] = {"repeat_index": repeat_index, "axes": {}}
        for axis in PRIMARY_AXES:
            silent_score = int(silent["score"].get(axis, 0) or 0)
            hook_score = int(hook["score"].get(axis, 0) or 0)
            delta = hook_score - silent_score
            if delta > 0:
                outcome = "win"
                axis_counts[axis]["wins"] += 1
            elif delta < 0:
                outcome = "loss"
                axis_counts[axis]["losses"] += 1
                if delta <= -1:
                    axis_counts[axis]["material_losses"] += 1
            else:
                outcome = "tie"
                axis_counts[axis]["ties"] += 1
            pair["axes"][axis] = {
                "silent": silent_score,
                "hook_native_cortex": hook_score,
                "delta": delta,
                "outcome": outcome,
            }
        pairs.append(pair)
    winning_axes = [
        axis for axis, counts in axis_counts.items() if counts["wins"] >= 4
    ]
    material_regressions = [
        axis
        for axis, counts in axis_counts.items()
        if counts["material_losses"] >= 2
    ]
    return {
        "pair_count": len(pair_indexes),
        "axis_counts": axis_counts,
        "winning_axes": winning_axes,
        "material_regressions": material_regressions,
        "pairs": pairs,
    }


def _arm_invariant_results(arm_rows: list[Mapping[str, object]]) -> dict[str, bool]:
    values = {
        "prompt_hash": {row.get("prompt_hash") for row in arm_rows},
        "workspace_seed_hash": {row.get("workspace_seed_hash") for row in arm_rows},
        "model": {row.get("model") for row in arm_rows},
        "task_family": {row.get("task_family") for row in arm_rows},
    }
    return {f"same_{key}": len(value) == 1 for key, value in values.items()}


def _report_passed(report: Mapping[str, Any]) -> bool:
    if report.get("live_comparison"):
        live = report["live_comparison"]
        return isinstance(live, Mapping) and bool(live.get("passed"))
    if report.get("task_standard_three_arm_live"):
        live = report["task_standard_three_arm_live"]
        return isinstance(live, Mapping) and bool(live.get("passed"))
    return bool(report.get("passed"))


def _count_values(values: object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if isinstance(value, str) and value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _append_rows(path: Path, rows: list[Mapping[str, Any]]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _excerpt(text: str | None, *, limit: int) -> str | None:
    if text is None:
        return None
    return text if len(text) <= limit else f"{text[:limit]}..."


__all__ = [
    "APPROVAL_ENV",
    "CLEAN_CONTROL_FAMILIES",
    "CONDITIONS",
    "DEFAULT_OUTPUT_ROOT",
    "PRIMARY_FAMILIES",
    "TASK_STANDARD_BEHAVIOR_APPROVAL_ENV",
    "TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV",
    "TASK_STANDARD_THREE_ARM_CONDITIONS",
    "run_gate0_probe",
    "run_live_comparison",
    "run_task_standard_offline_readiness_gate",
    "run_task_standard_posttooluse_live_probe",
    "run_task_standard_raw_vs_silent_artifact_readout",
    "run_task_standard_three_arm_gate0_probe",
    "run_task_standard_three_arm_live",
]


if __name__ == "__main__":
    raise SystemExit(main())
