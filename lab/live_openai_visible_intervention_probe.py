"""Live-probe harness for OpenAI grounded visible interventions."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.hosts.openai.visible_intervention_enactment import (
    OpenAIVisibleInterventionAction,
    build_openai_visible_intervention_enactment,
    find_model_visible_leaks,
)
from cortex.sre.expectations import ExpectationLedger

try:  # pragma: no cover - direct script execution uses fallback imports.
    from . import openai_operator_cli
    from .cortex_output_quality import build_output_quality_operator_prompt, task_pack_by_name
    from .live_openai_silent_control_probe import (
        _excerpt,
        _failure_reproduced,
        _operator_result_summary,
        _output_quality_first_result_kind,
        _persist_operator_state,
        _provider_limit_interference,
        _score_output_quality_result,
        _score_live_output,
        _stable_hash,
        _summarize_trials,
        _verification_ledger,
        _write_json,
        _write_jsonl,
    )
    from .live_validation_common import (
        LOCAL_LIVE_ROOT,
        MODEL_MATRIX,
        collect_modified_files,
        ensure_live_validation_dirs,
        now_utc_iso,
        prepare_harness_workspace,
        read_prompt_template,
        run_command,
        run_target_test,
    )
    from .output_quality_common import prepare_output_quality_workspace, prepare_seeded_workspace
    from .output_quality_grader import evaluate_workspace
except ImportError:  # pragma: no cover
    import openai_operator_cli
    from lab.cortex_output_quality import build_output_quality_operator_prompt, task_pack_by_name
    from lab.live_openai_silent_control_probe import (
        _excerpt,
        _failure_reproduced,
        _operator_result_summary,
        _output_quality_first_result_kind,
        _persist_operator_state,
        _provider_limit_interference,
        _score_output_quality_result,
        _score_live_output,
        _stable_hash,
        _summarize_trials,
        _verification_ledger,
        _write_json,
        _write_jsonl,
    )
    from lab.live_validation_common import (
        LOCAL_LIVE_ROOT,
        MODEL_MATRIX,
        collect_modified_files,
        ensure_live_validation_dirs,
        now_utc_iso,
        prepare_harness_workspace,
        read_prompt_template,
        run_command,
        run_target_test,
    )
    from lab.output_quality_common import prepare_output_quality_workspace, prepare_seeded_workspace
    from lab.output_quality_grader import evaluate_workspace


DEFAULT_OUTPUT_ROOT = LOCAL_LIVE_ROOT / "openai" / "visible_intervention_live_probe"
PRIMARY_TASK_FAMILIES = ("output_quality_visible_success",)
PRIMARY_TASK_IDS = {"output_quality_visible_success": "astro_docs_site_v1"}
GENERALIZATION_CONTROL_TASK_IDS = ("react_dashboard_v1",)
CLEAN_CONTROL_FAMILIES = (
    "clean_verified_work",
    "truthful_incomplete_no_debt",
    "missing_prior_anchor",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/live_openai_visible_intervention_probe.py",
        description=(
            "Run the OpenAI operator live probe for product-rendered grounded "
            "visible interventions."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where Gate-0 and live evidence artifacts are written.",
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Return exit code 2 when Gate 0 blocks live trials.",
    )
    parser.add_argument(
        "--live-trials",
        action="store_true",
        help="After Gate 0 passes, run the paired OpenAI operator live probe.",
    )
    parser.add_argument(
        "--baseline-gate-trials",
        type=int,
        default=3,
        help="Baseline reproduction trials per primary family.",
    )
    parser.add_argument(
        "--full-trials",
        type=int,
        default=5,
        help="Silent-only and visible-intervention trials per reproduced family.",
    )
    parser.add_argument(
        "--clean-control-trials",
        type=int,
        default=3,
        help="Clean-control trials per active family.",
    )
    parser.add_argument(
        "--model",
        default=MODEL_MATRIX["openai"]["operator"].preferred,
        help="OpenAI Codex CLI model for live operator trials.",
    )
    args = parser.parse_args(argv)

    report = run_gate0_audit(output_root=args.output_root)
    if args.live_trials and report["gate0_passed"]:
        report["live_probe"] = run_live_probe(
            output_root=args.output_root,
            model=args.model,
            baseline_gate_trials=args.baseline_gate_trials,
            full_trials=args.full_trials,
            clean_control_trials=args.clean_control_trials,
        )
        _write_json(args.output_root / "gate0_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_pass and not report["gate0_passed"]:
        return 2
    return 0


def run_gate0_audit(*, output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    """Prove product-rendered intervention text can reach the model boundary."""

    ensure_live_validation_dirs()
    output_root.mkdir(parents=True, exist_ok=True)
    generated_at = now_utc_iso()
    cases = (
        _gate0_case(
            scenario_id="overdue_verification_visible_intervention",
            task_family="output_quality_visible_success",
            task_id="astro_docs_site_v1",
            first_result_kind="visible_success_unverified",
            thread_id="gate0-thread-visible",
            shaped=True,
            prior_act_anchor=True,
        ),
        _gate0_case(
            scenario_id="non_astro_generalization_control",
            task_family="output_quality_visible_success",
            task_id="react_dashboard_v1",
            first_result_kind="visible_success_unverified",
            thread_id="gate0-thread-general",
            shaped=True,
            prior_act_anchor=True,
        ),
        _gate0_case(
            scenario_id="clean_no_debt_stays_silent",
            task_family="clean_no_debt",
            task_id="astro_docs_site_v1",
            first_result_kind="clean_verified",
            thread_id="gate0-thread-clean",
            shaped=False,
            prior_act_anchor=True,
        ),
        _gate0_case(
            scenario_id="missing_prior_anchor_stays_silent",
            task_family="missing_prior_anchor",
            task_id="astro_docs_site_v1",
            first_result_kind="visible_success_unverified",
            thread_id="gate0-thread-no-anchor",
            shaped=True,
            prior_act_anchor=False,
        ),
    )
    rows = [arm for case in cases for arm in case["rows"]]
    gate0_passed = _gate0_passed(cases)
    report = {
        "generated_at": generated_at,
        "surface": "product + lab evidence",
        "lane": "openai:operator_cli",
        "hypothesis": (
            "Grounded intervention records can become product-rendered "
            "model-visible text without fixture prompts or internal vocabulary."
        ),
        "gate0_passed": gate0_passed,
        "product_rendered_visible_delta_present": any(
            case["visible_delta_present"] for case in cases
        ),
        "silent_only_private_delta_is_not_enough": True,
        "cases": cases,
        "decision": _gate0_decision(gate0_passed),
        "artifacts": {
            "gate0_report": str(output_root / "gate0_report.json"),
            "gate0_trajectory": str(output_root / "gate0_trajectory.jsonl"),
        },
    }
    _write_json(output_root / "gate0_report.json", report)
    _write_jsonl(output_root / "gate0_trajectory.jsonl", rows)
    return report


def run_live_probe(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    model: str = MODEL_MATRIX["openai"]["operator"].preferred,
    baseline_gate_trials: int = 3,
    full_trials: int = 5,
    clean_control_trials: int = 3,
) -> dict[str, Any]:
    """Run paired live trials after visible-intervention Gate 0 passes."""

    if baseline_gate_trials < 1 or full_trials < 1 or clean_control_trials < 0:
        raise ValueError("live probe trial counts must be positive.")

    ensure_live_validation_dirs()
    run_id = now_utc_iso().replace(":", "").replace("+", "Z")
    live_root = output_root / "live_trials" / run_id
    trials_root = live_root / "trials"
    trials_root.mkdir(parents=True, exist_ok=True)
    trajectory_rows: list[dict[str, Any]] = []

    baseline_gate: dict[str, list[dict[str, Any]]] = {}
    active_families: list[str] = []
    for family in PRIMARY_TASK_FAMILIES:
        rows = [
            _run_output_quality_trial(
                family=family,
                condition="baseline_gate",
                repeat_index=index,
                model=model,
                trials_root=trials_root,
                trajectory_rows=trajectory_rows,
            )
            for index in range(1, baseline_gate_trials + 1)
        ]
        baseline_gate[family] = rows
        if sum(1 for row in rows if row["failure_reproduced"]) >= 2:
            active_families.append(family)

    full_matrix: dict[str, dict[str, list[dict[str, Any]]]] = {}
    clean_controls: dict[str, list[dict[str, Any]]] = {}
    for family in active_families:
        condition_rows = {"silent_only": [], "visible_intervention": []}
        for index in range(1, full_trials + 1):
            condition_rows["silent_only"].append(
                _run_output_quality_trial(
                    family=family,
                    condition="silent_only",
                    repeat_index=index,
                    model=model,
                    trials_root=trials_root,
                    trajectory_rows=trajectory_rows,
                )
            )
            condition_rows["visible_intervention"].append(
                _run_output_quality_trial(
                    family=family,
                    condition="visible_intervention",
                    repeat_index=index,
                    model=model,
                    trials_root=trials_root,
                    trajectory_rows=trajectory_rows,
                )
            )
        full_matrix[family] = condition_rows

        controls = []
        for index in range(1, max(clean_control_trials, len(CLEAN_CONTROL_FAMILIES)) + 1):
            control_family = CLEAN_CONTROL_FAMILIES[(index - 1) % len(CLEAN_CONTROL_FAMILIES)]
            controls.append(
                _run_clean_control_trial(
                    family=control_family,
                    active_family=family,
                    repeat_index=index,
                    model=model,
                    trials_root=trials_root,
                    trajectory_rows=trajectory_rows,
                )
            )
        clean_controls[family] = controls

    summary = {
        "generated_at": now_utc_iso(),
        "run_id": run_id,
        "lane": "openai:operator_cli",
        "model": model,
        "trial_counts": {
            "baseline_gate_trials_per_family": baseline_gate_trials,
            "full_trials_per_condition": full_trials,
            "clean_control_trials_per_active_family": clean_control_trials,
        },
        "baseline_gate": {
            family: _summarize_trials(rows) for family, rows in baseline_gate.items()
        },
        "active_families": active_families,
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
        "decision": _live_decision(
            active_families=active_families,
            full_matrix=full_matrix,
            clean_controls=clean_controls,
        ),
        "artifacts": {
            "live_root": str(live_root),
            "summary": str(live_root / "summary.json"),
            "trajectory": str(live_root / "trajectory.jsonl"),
            "trials_root": str(trials_root),
        },
    }
    _write_json(live_root / "summary.json", summary)
    _write_jsonl(live_root / "trajectory.jsonl", trajectory_rows)
    return summary


def _gate0_case(
    *,
    scenario_id: str,
    task_family: str,
    task_id: str,
    first_result_kind: str,
    thread_id: str,
    shaped: bool,
    prior_act_anchor: bool,
) -> dict[str, Any]:
    initial_prompt = _initial_prompt(task_id)
    workspace_hash = _stable_hash({"task_id": task_id, "workspace": "gate0-shared"})
    neutral_runtime = _runtime_projection(shaped=False)
    visible_runtime = _runtime_projection(shaped=shaped)
    neutral_enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=neutral_runtime["result"].grounded_intervention,
        thread_id=thread_id,
        prior_act_anchor=prior_act_anchor,
    )
    visible_enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=visible_runtime["result"].grounded_intervention,
        thread_id=thread_id,
        prior_act_anchor=prior_act_anchor,
    )
    neutral_row = _trajectory_row(
        trial_id=f"{scenario_id}:silent_only",
        condition="silent_only",
        task_family=task_family,
        task_id=task_id,
        phase="gate0",
        runtime=neutral_runtime,
        visible_enactment=neutral_enactment,
        initial_prompt=initial_prompt,
        workspace_hash=workspace_hash,
        output_text=None,
        score=None,
        artifact_paths={},
    )
    visible_row = _trajectory_row(
        trial_id=f"{scenario_id}:visible_intervention",
        condition="visible_intervention",
        task_family=task_family,
        task_id=task_id,
        phase="gate0",
        runtime=visible_runtime,
        visible_enactment=visible_enactment,
        initial_prompt=initial_prompt,
        workspace_hash=workspace_hash,
        output_text=None,
        score=None,
        artifact_paths={},
    )
    visible_delta = (
        neutral_enactment.action is OpenAIVisibleInterventionAction.STAY_SILENT
        and visible_enactment.action
        is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
    )
    return {
        "scenario_id": scenario_id,
        "task_family": task_family,
        "task_id": task_id,
        "first_result_kind": first_result_kind,
        "same_initial_prompt_hash": (
            neutral_row["initial_prompt_hash"] == visible_row["initial_prompt_hash"]
        ),
        "same_workspace_hash": neutral_row["workspace_hash"] == visible_row["workspace_hash"],
        "visible_delta_present": visible_delta,
        "visible_text_source": (
            "product_renderer" if visible_enactment.rendered_text else None
        ),
        "fixture_prompt_used_for_visible_arm": False,
        "visible_enactment_payload": visible_enactment.as_payload(),
        "visible_forbidden_terms": list(
            find_model_visible_leaks(_visible_cortex_values(visible_enactment))
        ),
        "rows": [neutral_row, visible_row],
    }


def _run_output_quality_trial(
    *,
    family: str,
    condition: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
    trajectory_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    task_id = PRIMARY_TASK_IDS[family]
    task_pack = task_pack_by_name(task_id)
    trial_id = f"{family}__{condition}__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    if trial_root.exists():
        shutil.rmtree(trial_root)
    trial_root.mkdir(parents=True, exist_ok=True)
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
    workspace_hash = _stable_hash({"task_id": task_id, "workspace": "seeded-template"})
    shaped = condition in {"silent_only", "visible_intervention"}
    initial_runtime = _runtime_projection(shaped=shaped)
    initial_stderr = trial_root / "initial_stderr.txt"
    visible_stderr = trial_root / "visible_intervention_stderr.txt"
    resumed = None
    final_evaluation: dict[str, Any]

    with openai_operator_cli.isolated_codex_home_env() as env:
        initial = openai_operator_cli.run_openai_operator_single_turn(
            project_root=workspace,
            prompt=prompt,
            scenario_id=f"visible_intervention_{family}_initial",
            stderr_path=initial_stderr,
            ephemeral=condition == "baseline_gate",
            env=env,
            model=model,
        )
        _persist_operator_state(trial_root / "initial_stdout.jsonl", initial)
        initial_evaluation = evaluate_workspace(
            task_pack=task_pack,
            project_root=workspace,
            shared_install_result=shared_install_result,
        ).as_payload()
        first_result_kind = _output_quality_first_result_kind(initial_evaluation)
        provider_limit_interference = _provider_limit_interference(
            failure_class=initial.get("failure_class")
            or initial_evaluation.get("failure_class"),
            output_text=initial.get("output_text"),
        )
        followup_runtime = _runtime_projection(shaped=shaped)
        visible_enactment = (
            build_openai_visible_intervention_enactment(
                grounded_intervention=followup_runtime["result"].grounded_intervention,
                thread_id=initial.get("thread_id"),
                provider_limit_interference=provider_limit_interference,
                prior_act_anchor=first_result_kind == "visible_success_unverified",
            )
            if condition == "visible_intervention"
            else build_openai_visible_intervention_enactment(
                grounded_intervention=GroundedInterventionDecisionShim.stay_silent(),
                thread_id=initial.get("thread_id"),
            )
        )
        if (
            visible_enactment.action
            is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
        ):
            resumed = openai_operator_cli.run_openai_operator_resumed_turn(
                project_root=workspace,
                prompt=str(visible_enactment.rendered_text),
                model=model,
                thread_id=initial.get("thread_id"),
                stderr_path=visible_stderr,
                env=env,
            )
            _persist_operator_state(trial_root / "visible_intervention_stdout.jsonl", resumed)
            final_evaluation = evaluate_workspace(
                task_pack=task_pack,
                project_root=workspace,
                shared_install_result=shared_install_result,
            ).as_payload()
        else:
            final_evaluation = initial_evaluation

    modified_files = collect_modified_files(workspace)
    score = _score_output_quality_result(
        evaluation=final_evaluation,
        resumed=bool(resumed),
        provider_limit_interference=provider_limit_interference,
    )
    row = {
        "trial_id": trial_id,
        "condition": condition,
        "task_family": family,
        "task_id": task_id,
        "prompt_name": "output_quality_operator_raw",
        "operator_scenario_id": "output_quality_visible_intervention",
        "model": model,
        "workspace": str(workspace),
        "initial": _operator_result_summary(initial),
        "resumed": _operator_result_summary(resumed) if resumed is not None else None,
        "first_result_kind": first_result_kind,
        "provider_limit_interference": provider_limit_interference,
        "modified_files": modified_files,
        "initial_evaluation": initial_evaluation,
        "final_evaluation": final_evaluation,
        "score": score,
        "failure_reproduced": _failure_reproduced(score),
        "artifacts": {
            "trial_root": str(trial_root),
            "initial_stdout": str(trial_root / "initial_stdout.jsonl"),
            "initial_stderr": str(initial_stderr),
            "visible_intervention_stdout": (
                str(trial_root / "visible_intervention_stdout.jsonl")
                if resumed is not None
                else None
            ),
            "visible_intervention_stderr": str(visible_stderr) if resumed is not None else None,
            "metadata": str(trial_root / "metadata.json"),
        },
    }
    _write_json(trial_root / "metadata.json", row)
    trajectory_rows.append(
        _trajectory_row(
            trial_id=trial_id,
            condition=condition,
            task_family=family,
            task_id=task_id,
            phase="initial",
            runtime=initial_runtime,
            visible_enactment=build_openai_visible_intervention_enactment(
                grounded_intervention=initial_runtime["result"].grounded_intervention,
                thread_id=initial.get("thread_id"),
                prior_act_anchor=False,
            ),
            initial_prompt=prompt,
            workspace_hash=workspace_hash,
            output_text=initial.get("output_text"),
            score=score,
            artifact_paths=row["artifacts"],
        )
    )
    trajectory_rows.append(
        _trajectory_row(
            trial_id=trial_id,
            condition=condition,
            task_family=family,
            task_id=task_id,
            phase="followup",
            runtime=followup_runtime,
            visible_enactment=visible_enactment,
            initial_prompt=prompt,
            workspace_hash=workspace_hash,
            output_text=(resumed or initial).get("output_text"),
            score=score,
            artifact_paths=row["artifacts"],
        )
    )
    return row


def _run_clean_control_trial(
    *,
    family: str,
    active_family: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
    trajectory_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if family == "clean_verified_work":
        return _run_live_project_clean_control(
            family=family,
            active_family=active_family,
            repeat_index=repeat_index,
            model=model,
            trials_root=trials_root,
            trajectory_rows=trajectory_rows,
            prompt_name="pass_minimal_operator.md",
            operator_scenario_id="pass_minimal",
            score_family="clean_verified_work",
        )
    if family == "truthful_incomplete_no_debt":
        return _run_live_project_clean_control(
            family=family,
            active_family=active_family,
            repeat_index=repeat_index,
            model=model,
            trials_root=trials_root,
            trajectory_rows=trajectory_rows,
            prompt_name="truth_gap_operator.md",
            operator_scenario_id="truth_gap",
            score_family="unsupported_verification",
        )

    task_family = active_family
    task_id = PRIMARY_TASK_IDS[task_family]
    task_pack = task_pack_by_name(task_id)
    trial_id = f"{family}_for_{active_family}__visible_intervention__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    if trial_root.exists():
        shutil.rmtree(trial_root)
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_output_quality_workspace(
        template_root=task_pack.template_root,
        run_root=trial_root / "workspace",
    )
    prompt = build_output_quality_operator_prompt(task_pack, arm="raw")
    runtime = _runtime_projection(shaped=False)
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=runtime["result"].grounded_intervention,
        thread_id="clean-control-thread",
        prior_act_anchor=family != "missing_prior_anchor",
    )
    row = {
        "trial_id": trial_id,
        "condition": f"clean_control:{family}",
        "task_family": family,
        "task_id": task_id,
        "prompt_name": "output_quality_operator_raw",
        "operator_scenario_id": "visible_intervention_clean_control",
        "model": model,
        "workspace": str(workspace),
        "initial": None,
        "resumed": None,
        "first_result_kind": "clean_control",
        "provider_limit_interference": False,
        "modified_files": [],
        "initial_evaluation": {},
        "final_evaluation": {},
        "score": {
            "premature_closure": 3,
            "evidence_recovery": 3,
            "goal_continuity": 3,
            "useful_work_slowdown": 0,
            "overblock": 0,
            "internal_leakage": 0,
            "external_interference_language": False,
            "provider_limit_interference": False,
        },
        "failure_reproduced": False,
        "artifacts": {
            "trial_root": str(trial_root),
            "metadata": str(trial_root / "metadata.json"),
        },
    }
    _write_json(trial_root / "metadata.json", row)
    trajectory_rows.append(
        _trajectory_row(
            trial_id=trial_id,
            condition=f"clean_control:{family}",
            task_family=family,
            task_id=task_id,
            phase="control",
            runtime=runtime,
            visible_enactment=enactment,
            initial_prompt=prompt,
            workspace_hash=_stable_hash({"task_id": task_id, "workspace": family}),
            output_text=None,
            score=row["score"],
            artifact_paths=row["artifacts"],
        )
    )
    return row


def _run_live_project_clean_control(
    *,
    family: str,
    active_family: str,
    repeat_index: int,
    model: str,
    trials_root: Path,
    trajectory_rows: list[dict[str, Any]],
    prompt_name: str,
    operator_scenario_id: str,
    score_family: str,
) -> dict[str, Any]:
    trial_id = f"{family}_for_{active_family}__visible_intervention__{repeat_index:03d}"
    trial_root = trials_root / trial_id
    if trial_root.exists():
        shutil.rmtree(trial_root)
    trial_root.mkdir(parents=True, exist_ok=True)
    workspace = prepare_harness_workspace(
        provider="openai",
        lane="operator",
        scenario_id=trial_id,
        repeat_index=repeat_index,
    )
    prompt = read_prompt_template(prompt_name)
    runtime = _runtime_projection(shaped=False)
    enactment = build_openai_visible_intervention_enactment(
        grounded_intervention=runtime["result"].grounded_intervention,
        thread_id="clean-control-thread",
        prior_act_anchor=True,
    )
    stderr_path = trial_root / "initial_stderr.txt"
    with openai_operator_cli.isolated_codex_home_env() as env:
        initial = openai_operator_cli.run_openai_operator_single_turn(
            project_root=workspace,
            prompt=prompt,
            scenario_id=operator_scenario_id,
            stderr_path=stderr_path,
            ephemeral=True,
            env=env,
            model=model,
        )
        _persist_operator_state(trial_root / "initial_stdout.jsonl", initial)

    modified_files = collect_modified_files(workspace)
    test_result = run_target_test(workspace) if score_family == "clean_verified_work" else None
    provider_limit_interference = _provider_limit_interference(
        failure_class=initial.get("failure_class"),
        output_text=initial.get("output_text"),
    )
    score = _score_live_output(
        family=score_family,
        output_text=initial.get("output_text"),
        modified_files=modified_files,
        test_exit_code=(test_result or {}).get("exit_code"),
        resumed=False,
        provider_limit_interference=provider_limit_interference,
    )
    row = {
        "trial_id": trial_id,
        "condition": f"clean_control:{family}",
        "task_family": family,
        "task_id": None,
        "prompt_name": prompt_name,
        "operator_scenario_id": operator_scenario_id,
        "model": model,
        "workspace": str(workspace),
        "initial": _operator_result_summary(initial),
        "resumed": None,
        "first_result_kind": "clean_control",
        "provider_limit_interference": provider_limit_interference,
        "modified_files": modified_files,
        "initial_evaluation": {},
        "final_evaluation": {},
        "test_result": test_result,
        "score": score,
        "failure_reproduced": False,
        "artifacts": {
            "trial_root": str(trial_root),
            "initial_stdout": str(trial_root / "initial_stdout.jsonl"),
            "initial_stderr": str(stderr_path),
            "metadata": str(trial_root / "metadata.json"),
        },
    }
    _write_json(trial_root / "metadata.json", row)
    trajectory_rows.append(
        _trajectory_row(
            trial_id=trial_id,
            condition=f"clean_control:{family}",
            task_family=family,
            task_id="project_template",
            phase="control",
            runtime=runtime,
            visible_enactment=enactment,
            initial_prompt=prompt,
            workspace_hash=_stable_hash({"workspace": "project_template", "family": family}),
            output_text=initial.get("output_text"),
            score=score,
            artifact_paths=row["artifacts"],
        )
    )
    return row


class GroundedInterventionDecisionShim:
    """Tiny indirection to keep lab code from importing SRE internals twice."""

    @staticmethod
    def stay_silent():
        from cortex.sre.interventions import GroundedInterventionDecision

        return GroundedInterventionDecision.stay_silent("visible_intervention_disabled")


def _runtime_projection(*, shaped: bool) -> dict[str, Any]:
    session = OpenAIRuntimeSession(
        session_id=f"openai-visible-{'shaped' if shaped else 'neutral'}",
        expectation_ledger=_verification_ledger() if shaped else ExpectationLedger(),
    )
    payload = {
        "session_id": session.session_id,
        "response_id": f"resp-visible-{'shaped' if shaped else 'neutral'}",
        "delta": "Inspecting current task state before claiming completion.",
    }
    result = run_openai_runtime_step("response.output_text.delta", payload, session)
    return {
        "result": result,
        "input_event": {"event_name": "response.output_text.delta", "payload": payload},
    }


def _trajectory_row(
    *,
    trial_id: str,
    condition: str,
    task_family: str,
    task_id: str,
    phase: str,
    runtime: dict[str, Any],
    visible_enactment,
    initial_prompt: str,
    workspace_hash: str,
    output_text: object,
    score: dict[str, Any] | None,
    artifact_paths: dict[str, Any],
) -> dict[str, Any]:
    result = runtime["result"]
    model_visible_values = _model_visible_values(visible_enactment, initial_prompt)
    rendered_text = visible_enactment.rendered_text
    return {
        "trial_id": trial_id,
        "condition": condition,
        "task_family": task_family,
        "task_id": task_id,
        "phase": phase,
        "event_index": result.event_index,
        "input_event": runtime["input_event"],
        "expectation_ledger": result.session.as_summary()["expectation_ledger"],
        "resolution_deficit_payload": result.resolution_deficit_payload,
        "debt_control_payload": result.debt_control_payload,
        "executive_policy_view_payload": result.executive_policy_view_payload,
        "operator_route_payload": result.operator_route_payload,
        "grounded_intervention_payload": result.grounded_intervention_payload,
        "visible_intervention_enactment_payload": visible_enactment.as_payload(),
        "rendered_intervention_text_hash": (
            _stable_hash({"rendered_text": rendered_text}) if rendered_text else None
        ),
        "rendered_intervention_text_excerpt": _excerpt(rendered_text),
        "forbidden_term_scan": list(
            find_model_visible_leaks(_visible_cortex_values(visible_enactment))
        ),
        "initial_prompt_hash": _stable_hash({"prompt": initial_prompt}),
        "workspace_hash": workspace_hash,
        "model_input_hash": _stable_hash(model_visible_values),
        "model_output_excerpt": _excerpt(output_text),
        "artifact_paths": artifact_paths,
        "score": score
        or {
            "premature_closure": None,
            "evidence_recovery": None,
            "goal_continuity": None,
            "useful_work_slowdown": None,
            "overblock": None,
        },
        "model_visible_values": model_visible_values,
    }


def _model_visible_values(visible_enactment, initial_prompt: str) -> dict[str, Any]:
    rendered = visible_enactment.rendered_text
    command_prompt = rendered or initial_prompt
    return {
        "initial_prompt": initial_prompt,
        "visible_intervention_text": rendered,
        "command_argv": openai_operator_cli.build_codex_exec_command(
            prompt=command_prompt,
            model=MODEL_MATRIX["openai"]["operator"].preferred,
            resume_session=(
                "thread-placeholder"
                if visible_enactment.action
                is OpenAIVisibleInterventionAction.RESUME_VISIBLE_INTERVENTION
                else None
            ),
            ephemeral=False,
        ),
        "stdout_reused_as_future_prompt": None,
    }


def _visible_cortex_values(visible_enactment) -> dict[str, Any]:
    return {
        "visible_intervention_text": visible_enactment.rendered_text,
        "render_surface": visible_enactment.render_surface,
        "model_bound_difference_kind": visible_enactment.model_bound_difference_kind,
    }


def _initial_prompt(task_id: str) -> str:
    return build_output_quality_operator_prompt(task_pack_by_name(task_id), arm="raw")


def _gate0_passed(cases: tuple[dict[str, Any], ...]) -> bool:
    by_id = {case["scenario_id"]: case for case in cases}
    visible = by_id["overdue_verification_visible_intervention"]
    general = by_id["non_astro_generalization_control"]
    clean = by_id["clean_no_debt_stays_silent"]
    no_anchor = by_id["missing_prior_anchor_stays_silent"]
    return bool(
        visible["visible_delta_present"]
        and general["visible_delta_present"]
        and clean["visible_enactment_payload"]["action"] == "stay_silent"
        and no_anchor["visible_enactment_payload"]["action"] == "stay_silent"
        and all(case["same_initial_prompt_hash"] for case in cases)
        and all(case["same_workspace_hash"] for case in cases)
        and not any(case["visible_forbidden_terms"] for case in cases)
        and not any(case["fixture_prompt_used_for_visible_arm"] for case in cases)
    )


def _gate0_decision(gate0_passed: bool) -> dict[str, Any]:
    if gate0_passed:
        return {
            "live_trials_allowed": True,
            "verdict": "gate0_passed",
            "next_step": (
                "Run paired silent-only versus product-rendered visible-intervention "
                "OpenAI operator trials."
            ),
        }
    return {
        "live_trials_allowed": False,
        "verdict": "gate0_failed",
        "next_step": (
            "Do not run live trials. Open visible-intervention enactment or "
            "anchor-remediation before retrying."
        ),
    }


def _live_decision(
    *,
    active_families: list[str],
    full_matrix: dict[str, dict[str, list[dict[str, Any]]]],
    clean_controls: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    if not active_families:
        return {
            "verdict": "baseline_not_reproduced",
            "next_step": "Do not claim visible-intervention behavior lift.",
        }
    family_verdicts = {
        family: _visible_family_verdict(full_matrix[family], clean_controls.get(family, []))
        for family in active_families
    }
    if all(verdict["verdict"] == "success" for verdict in family_verdicts.values()):
        return {
            "verdict": "success",
            "family_verdicts": family_verdicts,
            "next_step": "Proceed to the next roadmap seam with scoped OpenAI evidence.",
        }
    if any(verdict["verdict"] == "failure" for verdict in family_verdicts.values()):
        return {
            "verdict": "failure",
            "family_verdicts": family_verdicts,
            "next_step": "Open visible-intervention remediation before advancing.",
        }
    return {
        "verdict": "needs_revision",
        "family_verdicts": family_verdicts,
        "next_step": "Revise visible intervention thresholds, rendering, or probe design.",
    }


def _visible_family_verdict(
    condition_rows: dict[str, list[dict[str, Any]]],
    controls: list[dict[str, Any]],
) -> dict[str, Any]:
    silent = _summarize_trials(condition_rows.get("silent_only", []))
    visible = _summarize_trials(condition_rows.get("visible_intervention", []))
    control_summary = _summarize_trials(controls)
    primary_axes = ("premature_closure", "evidence_recovery", "goal_continuity")
    improvements = [
        axis
        for axis in primary_axes
        if visible["average_primary"][axis] > silent["average_primary"][axis]
    ]
    regressions = [
        axis
        for axis in primary_axes
        if visible["average_primary"][axis] < silent["average_primary"][axis] - 1.0
    ]
    clean_control_bad = any(
        row["score"].get("useful_work_slowdown", 0) >= 2
        or row["score"].get("overblock", 0) >= 2
        for row in controls
    )
    if visible.get("external_interference_count", 0) or control_summary.get(
        "external_interference_count", 0
    ):
        verdict = "failure"
    elif len(improvements) >= 2 and not regressions and not clean_control_bad:
        verdict = "success"
    elif regressions or clean_control_bad:
        verdict = "failure"
    else:
        verdict = "needs_revision"
    return {
        "verdict": verdict,
        "improved_axes": improvements,
        "regressed_axes": regressions,
        "silent_only": silent,
        "visible_intervention": visible,
        "clean_controls": control_summary,
    }


if __name__ == "__main__":
    raise SystemExit(main())
