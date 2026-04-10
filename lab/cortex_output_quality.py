"""Comparative output-quality benchmark for the E12 evaluation train."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cortex.hosts.openai.host_control import OpenAIHostControlRequest
from cortex.hosts.openai.host_transport import (
    OpenAIResponseStreamTransportError,
    execute_openai_response_stream_turn,
)

from lab.live_validation_common import (
    BLOCKING_FAILURE_CLASSES,
    collect_modified_files,
    LOCAL_LIVE_ROOT,
    load_local_env_file,
    now_utc_iso,
    write_json,
    write_text,
)
from lab.openai_operator_cli import (
    isolated_codex_home_env,
    run_openai_operator_resumed_turn,
    run_openai_operator_single_turn,
)
from lab.output_quality_ablation import OutputQualityAblationConfig
from lab.output_quality_common import (
    ArmName,
    OutputQualityTaskPack,
    apply_output_files,
    build_output_quality_input_text,
    parse_output_quality_result,
    prepare_output_quality_workspace,
    prepare_seeded_workspace,
    render_context_bundle,
    snapshot_files,
    stable_pair_order,
)
from lab.output_quality_grader import (
    OutputQualityEvaluation,
    build_output_quality_repair_ticket,
    evaluate_workspace,
    judge_pairwise_merge_worthiness,
)
from lab.service_spend_gate import require_openai_service_spend_approval


OUTPUT_QUALITY_ROOT = LOCAL_LIVE_ROOT / "output_quality"
DEFAULT_ARMS: tuple[ArmName, ...] = ("raw", "tooling_only", "cortex")
OutputQualitySurface = Literal["service_api", "operator_cli"]
DEFAULT_SURFACE: OutputQualitySurface = "service_api"
DEFAULT_MODEL_BY_SURFACE: dict[OutputQualitySurface, str] = {
    "service_api": "gpt-5.4",
    "operator_cli": "gpt-5.3-codex",
}


def task_pack_by_name(task_id: str) -> OutputQualityTaskPack:
    task_packs = _task_pack_registry()
    if task_id not in task_packs:
        supported = ", ".join(sorted(task_packs))
        raise ValueError(f"Unsupported output-quality task pack `{task_id}`. Supported: {supported}")
    return task_packs[task_id]


def supported_task_ids() -> tuple[str, ...]:
    return tuple(_task_pack_registry())


def _surface_artifact_label(surface: OutputQualitySurface) -> str:
    if surface == "service_api":
        return "openai"
    if surface == "operator_cli":
        return "openai_operator_cli"
    raise ValueError(f"Unsupported output-quality surface `{surface}`.")


def run_output_quality_suite(
    *,
    task_ids: tuple[str, ...],
    arms: tuple[ArmName, ...] = DEFAULT_ARMS,
    model: str | None = None,
    surface: OutputQualitySurface = DEFAULT_SURFACE,
    artifact_root: Path = OUTPUT_QUALITY_ROOT,
    ablation_config: OutputQualityAblationConfig | None = None,
) -> dict[str, Any]:
    load_local_env_file()
    run_id = now_utc_iso().replace(":", "").replace("-", "")
    run_root = artifact_root / _surface_artifact_label(surface) / f"run_{run_id}"
    selected_model = model or DEFAULT_MODEL_BY_SURFACE[surface]
    results: dict[str, Any] = {}
    aggregate_objective = {arm: 0 for arm in arms}
    aggregate_hidden = {arm: 0 for arm in arms}
    pairwise_results: list[dict[str, Any]] = []
    env_blocked = False

    for task_id in task_ids:
        task_pack = task_pack_by_name(task_id)
        task_root = run_root / task_id
        seed_workspace = prepare_output_quality_workspace(
            template_root=task_pack.template_root,
            run_root=task_root / "seed",
        )
        shared_install_result = _run_shared_install(task_pack, seed_workspace)
        arm_results: dict[str, Any] = {}
        for arm in arms:
            arm_result = _run_arm(
                task_pack=task_pack,
                arm=arm,
                model=selected_model,
                surface=surface,
                task_root=task_root,
                seed_workspace=seed_workspace,
                shared_install_result=shared_install_result,
                ablation_config=ablation_config,
            )
            arm_results[arm] = arm_result
            if arm_result["evaluation"]["status"] == "env_blocked":
                env_blocked = True
            if arm_result["evaluation"]["objective_pass"]:
                aggregate_objective[arm] += 1
            if arm_result["evaluation"]["hidden_quality_pass"]:
                aggregate_hidden[arm] += 1
        comparisons = _build_pairwise_results(
            task_pack=task_pack,
            arms=arms,
            arm_results=arm_results,
            surface=surface,
        )
        pairwise_results.extend(comparisons)
        results[task_id] = {
            "task_id": task_id,
            "shared_install_result": shared_install_result,
            "arms": arm_results,
            "pairwise": comparisons,
        }

    summary = _build_suite_summary(
        run_root=run_root,
        task_ids=task_ids,
        arms=arms,
        model=selected_model,
        surface=surface,
        task_results=results,
        aggregate_objective=aggregate_objective,
        aggregate_hidden=aggregate_hidden,
        pairwise_results=pairwise_results,
        env_blocked=env_blocked,
        ablation_config=ablation_config,
    )
    write_json(run_root / "summary.json", summary)
    write_text(run_root / "summary.md", _render_summary_markdown(summary))
    latest_path = OUTPUT_QUALITY_ROOT / f"summary.latest.{surface}.json"
    write_json(latest_path, summary)
    if surface == "service_api":
        write_json(OUTPUT_QUALITY_ROOT / "summary.latest.json", summary)
    return summary


def _run_shared_install(task_pack: OutputQualityTaskPack, seed_workspace: Path) -> dict[str, Any]:
    from lab.live_validation_common import run_command

    result = run_command(list(task_pack.install_command), cwd=seed_workspace, timeout_seconds=600.0)
    result["check_name"] = "install"
    return result


def _run_arm(
    *,
    task_pack: OutputQualityTaskPack,
    arm: ArmName,
    model: str,
    surface: OutputQualitySurface = DEFAULT_SURFACE,
    task_root: Path,
    seed_workspace: Path,
    shared_install_result: dict[str, Any],
    ablation_config: OutputQualityAblationConfig | None,
) -> dict[str, Any]:
    if surface == "operator_cli":
        return _run_operator_cli_arm(
            task_pack=task_pack,
            arm=arm,
            model=model,
            task_root=task_root,
            seed_workspace=seed_workspace,
            shared_install_result=shared_install_result,
            ablation_config=ablation_config,
        )
    return _run_service_api_arm(
        task_pack=task_pack,
        arm=arm,
        model=model,
        task_root=task_root,
        seed_workspace=seed_workspace,
        shared_install_result=shared_install_result,
        ablation_config=ablation_config,
    )


def _run_service_api_arm(
    *,
    task_pack: OutputQualityTaskPack,
    arm: ArmName,
    model: str,
    task_root: Path,
    seed_workspace: Path,
    shared_install_result: dict[str, Any],
    ablation_config: OutputQualityAblationConfig | None,
) -> dict[str, Any]:
    prompt_text = task_pack.prompt_text.strip()
    cortex_ablation = ablation_config if arm == "cortex" else None
    input_text = build_output_quality_input_text(
        task_pack,
        arm=arm,
        ablation_config=cortex_ablation,
    )
    initial_turn = _execute_openai_turn(
        model=model,
        input_text=input_text,
        max_output_tokens=task_pack.max_output_tokens,
    )
    attempt1_root = task_root / arm / "attempt1"
    attempt1_workspace = prepare_seeded_workspace(
        template_root=task_pack.template_root,
        seed_workspace_root=seed_workspace,
        run_root=attempt1_root,
    )
    attempt1_payload = _evaluate_turn_output(
        task_pack=task_pack,
        project_root=attempt1_workspace,
        output_text=initial_turn["output_text"],
        shared_install_result=shared_install_result,
    )
    attempt1_payload["response_id"] = initial_turn["response_id"]
    attempt1_payload["output_text"] = initial_turn["output_text"]
    attempt1_payload["input_text"] = input_text
    write_json(attempt1_root / "result.json", attempt1_payload)

    final_payload = attempt1_payload
    attempt_count = 1
    if (
        arm == "cortex"
        and attempt1_payload["repairable"]
        and initial_turn["response_id"] is not None
        and (cortex_ablation is None or cortex_ablation.repair_turn == "on")
        and (cortex_ablation is None or cortex_ablation.verification_binding == "on")
    ):
        repair_ticket = build_output_quality_repair_ticket(
            evaluation=evaluate_workspace_payload(attempt1_payload["evaluation"]),
            allowed_write_paths=task_pack.allowed_write_paths,
            style=(
                cortex_ablation.repair_ticket_style
                if cortex_ablation is not None
                else "factual"
            ),
            repair_surface=task_pack.allowed_write_paths,
        )
        repair_turn = _execute_openai_turn(
            model=model,
            input_text=input_text,
            max_output_tokens=task_pack.max_output_tokens,
            previous_response_id=initial_turn["response_id"],
            input_text_override=repair_ticket,
        )
        attempt2_root = task_root / arm / "attempt2"
        attempt2_workspace = prepare_seeded_workspace(
            template_root=task_pack.template_root,
            seed_workspace_root=seed_workspace,
            run_root=attempt2_root,
        )
        attempt2_payload = _evaluate_turn_output(
            task_pack=task_pack,
            project_root=attempt2_workspace,
            output_text=repair_turn["output_text"],
            shared_install_result=shared_install_result,
        )
        attempt2_payload["response_id"] = repair_turn["response_id"]
        attempt2_payload["output_text"] = repair_turn["output_text"]
        attempt2_payload["input_text"] = repair_ticket
        write_json(attempt2_root / "result.json", attempt2_payload)
        final_payload = attempt2_payload
        attempt_count = 2

    return {
        "arm": arm,
        "prompt_text": prompt_text,
        "attempt_count": attempt_count,
        "attempt1": attempt1_payload,
        "final": final_payload,
        "evaluation": final_payload["evaluation"],
        "changed_files": final_payload["changed_files"],
        "repairable": final_payload["repairable"],
    }


def _run_operator_cli_arm(
    *,
    task_pack: OutputQualityTaskPack,
    arm: ArmName,
    model: str,
    task_root: Path,
    seed_workspace: Path,
    shared_install_result: dict[str, Any],
    ablation_config: OutputQualityAblationConfig | None,
) -> dict[str, Any]:
    prompt_text = task_pack.prompt_text.strip()
    cortex_ablation = ablation_config if arm == "cortex" else None
    input_text = build_output_quality_operator_prompt(
        task_pack,
        arm=arm,
        ablation_config=cortex_ablation,
    )
    workspace_root = prepare_seeded_workspace(
        template_root=task_pack.template_root,
        seed_workspace_root=seed_workspace,
        run_root=task_root / arm / "workspace",
    )
    attempt1_root = task_root / arm / "attempt1"
    with isolated_codex_home_env() as env:
        initial_turn = run_openai_operator_single_turn(
            project_root=workspace_root,
            prompt=input_text,
            scenario_id=f"output_quality_{task_pack.task_id}_{arm}_attempt1",
            stderr_path=attempt1_root / "operator.stderr.log",
            ephemeral=arm != "cortex",
            env=env,
            model=model,
        )
        attempt1_payload = _evaluate_operator_turn_output(
            task_pack=task_pack,
            project_root=workspace_root,
            output_text=initial_turn["output_text"],
            shared_install_result=shared_install_result,
            failure_class=initial_turn["failure_class"],
            attempted_models=initial_turn["attempted_models"],
            thread_id=initial_turn["thread_id"],
        )
        attempt1_payload["output_text"] = initial_turn["output_text"]
        attempt1_payload["input_text"] = input_text
        write_json(attempt1_root / "result.json", attempt1_payload)

        final_payload = attempt1_payload
        attempt_count = 1
        if (
            arm == "cortex"
            and attempt1_payload["repairable"]
            and initial_turn["thread_id"] is not None
            and (cortex_ablation is None or cortex_ablation.repair_turn == "on")
            and (cortex_ablation is None or cortex_ablation.verification_binding == "on")
        ):
            repair_ticket = build_output_quality_repair_ticket(
                evaluation=evaluate_workspace_payload(attempt1_payload["evaluation"]),
                allowed_write_paths=task_pack.allowed_write_paths,
                style=(
                    cortex_ablation.repair_ticket_style
                    if cortex_ablation is not None
                    else "factual"
                ),
                repair_surface=task_pack.allowed_write_paths,
            )
            repair_turn = run_openai_operator_resumed_turn(
                project_root=workspace_root,
                prompt=repair_ticket,
                model=initial_turn["model"],
                thread_id=initial_turn["thread_id"],
                stderr_path=(task_root / arm / "attempt2" / "operator.stderr.log"),
                env=env,
            )
            attempt2_root = task_root / arm / "attempt2"
            attempt2_payload = _evaluate_operator_turn_output(
                task_pack=task_pack,
                project_root=workspace_root,
                output_text=repair_turn["output_text"],
                shared_install_result=shared_install_result,
                failure_class=repair_turn["failure_class"],
                attempted_models=(initial_turn["attempted_models"] + [repair_turn["model"]]),
                thread_id=repair_turn["thread_id"],
            )
            attempt2_payload["output_text"] = repair_turn["output_text"]
            attempt2_payload["input_text"] = repair_ticket
            write_json(attempt2_root / "result.json", attempt2_payload)
            final_payload = attempt2_payload
            attempt_count = 2

    return {
        "arm": arm,
        "prompt_text": prompt_text,
        "attempt_count": attempt_count,
        "attempt1": attempt1_payload,
        "final": final_payload,
        "evaluation": final_payload["evaluation"],
        "changed_files": final_payload["changed_files"],
        "repairable": final_payload["repairable"],
    }


def _evaluate_turn_output(
    *,
    task_pack: OutputQualityTaskPack,
    project_root: Path,
    output_text: str | None,
    shared_install_result: dict[str, Any],
) -> dict[str, Any]:
    parse_result = parse_output_quality_result(
        output_text,
        allowed_write_paths=task_pack.allowed_write_paths,
    )
    if parse_result.file_map is not None:
        apply_output_files(project_root=project_root, file_map=parse_result.file_map)
    evaluation = evaluate_workspace(
        task_pack=task_pack,
        project_root=project_root,
        shared_install_result=shared_install_result,
    ) if parse_result.file_map is not None else _parse_failure_evaluation(
        parse_result=parse_result,
        shared_install_result=shared_install_result,
    )
    return {
        "parse": {
            "parse_error": parse_result.parse_error,
            "blocked_reason": parse_result.blocked_reason,
            "blocked_message": parse_result.blocked_message,
            "parsed_paths": sorted(parse_result.file_map or {}),
        },
        "evaluation": evaluation.as_payload(),
        "changed_files": snapshot_files(
            root=project_root,
            relative_paths=task_pack.allowed_write_paths,
        ) if parse_result.file_map is not None else {},
        "repairable": evaluation.status == "failed"
        and evaluation.failure_class not in {"blocked_missing_info", "blocked_unsafe"},
    }


def build_output_quality_operator_prompt(
    task_pack: OutputQualityTaskPack,
    *,
    arm: ArmName,
    ablation_config: OutputQualityAblationConfig | None = None,
) -> str:
    if arm == "cortex" and ablation_config is not None:
        if ablation_config.visible_contract_binding == "off":
            context_bundle = None
        elif ablation_config.visible_context_variant == "writable_files_only":
            context_bundle = render_context_bundle(
                task_pack,
                context_paths=tuple(task_pack.allowed_write_paths),
            )
        elif ablation_config.visible_context_variant == "writable_files_plus_visible_tests":
            context_bundle = render_context_bundle(
                task_pack,
                context_paths=tuple(task_pack.allowed_write_paths) + _visible_test_paths(task_pack),
            )
        else:
            context_bundle = render_context_bundle(task_pack)
    elif arm == "raw":
        context_bundle = None
    else:
        context_bundle = render_context_bundle(task_pack)

    allowed_paths = "\n".join(f"- {path}" for path in task_pack.allowed_write_paths)
    prompt_parts = [task_pack.prompt_text.strip()]
    if context_bundle is not None:
        prompt_parts.extend(
            (
                "Visible contract files follow. Additional verifier-only checks may run.",
                "Use the existing files below as the visible task contract.",
                context_bundle,
            )
        )
    prompt_parts.append(
        "\n".join(
            (
                "Edit the workspace directly and keep the final result mergeable.",
                "Keep any changes within these paths:",
                allowed_paths,
                "You may run local checks if useful.",
                "If essential information is missing, make no edits and reply with:",
                "=== BLOCKED: needs_user_input ===",
                "<message>",
                "=== END BLOCKED ===",
            )
        )
    )
    return "\n\n".join(prompt_parts)


def _evaluate_operator_turn_output(
    *,
    task_pack: OutputQualityTaskPack,
    project_root: Path,
    output_text: str | None,
    shared_install_result: dict[str, Any],
    failure_class: str | None,
    attempted_models: list[str],
    thread_id: str | None,
) -> dict[str, Any]:
    modified_files = collect_modified_files(project_root)
    allowed_path_set = set(task_pack.allowed_write_paths)
    disallowed_paths = sorted(path for path in modified_files if path not in allowed_path_set)
    changed_allowed_paths = tuple(path for path in task_pack.allowed_write_paths if path in modified_files)
    changed_files = snapshot_files(root=project_root, relative_paths=changed_allowed_paths)

    if failure_class in BLOCKING_FAILURE_CLASSES:
        evaluation = OutputQualityEvaluation(
            status="env_blocked",
            failure_class=failure_class,
            objective_pass=False,
            hidden_quality_pass=False,
            failing_checks=("operator",),
            first_failure_excerpt=output_text,
            checks=(dict(shared_install_result, check_name="install"),),
        )
        return _operator_payload(
            evaluation=evaluation,
            parse_error=None,
            blocked_reason=None,
            blocked_message=None,
            parsed_paths=tuple(changed_allowed_paths),
            changed_files=changed_files,
            attempted_models=attempted_models,
            thread_id=thread_id,
        )

    if disallowed_paths:
        evaluation = OutputQualityEvaluation(
            status="failed",
            failure_class="output_invalid",
            objective_pass=False,
            hidden_quality_pass=False,
            failing_checks=("operator",),
            first_failure_excerpt=f"operator modified unapproved path: {disallowed_paths[0]}",
            checks=(dict(shared_install_result, check_name="install"),),
        )
        return _operator_payload(
            evaluation=evaluation,
            parse_error=f"operator modified unapproved path: {disallowed_paths[0]}",
            blocked_reason=None,
            blocked_message=None,
            parsed_paths=tuple(changed_allowed_paths),
            changed_files=changed_files,
            attempted_models=attempted_models,
            thread_id=thread_id,
        )

    if not changed_allowed_paths:
        parse_result = parse_output_quality_result(
            output_text,
            allowed_write_paths=task_pack.allowed_write_paths,
        )
        if parse_result.blocked_reason is not None:
            evaluation = _parse_failure_evaluation(
                parse_result=parse_result,
                shared_install_result=shared_install_result,
            )
            return _operator_payload(
                evaluation=evaluation,
                parse_error=None,
                blocked_reason=parse_result.blocked_reason,
                blocked_message=parse_result.blocked_message,
                parsed_paths=(),
                changed_files={},
                attempted_models=attempted_models,
                thread_id=thread_id,
            )
        evaluation = OutputQualityEvaluation(
            status="failed",
            failure_class="output_invalid",
            objective_pass=False,
            hidden_quality_pass=False,
            failing_checks=("operator",),
            first_failure_excerpt=parse_result.parse_error or output_text,
            checks=(dict(shared_install_result, check_name="install"),),
        )
        return _operator_payload(
            evaluation=evaluation,
            parse_error=parse_result.parse_error or "operator completed without workspace edits",
            blocked_reason=None,
            blocked_message=None,
            parsed_paths=(),
            changed_files={},
            attempted_models=attempted_models,
            thread_id=thread_id,
        )

    evaluation = evaluate_workspace(
        task_pack=task_pack,
        project_root=project_root,
        shared_install_result=shared_install_result,
    )
    return _operator_payload(
        evaluation=evaluation,
        parse_error=None,
        blocked_reason=None,
        blocked_message=None,
        parsed_paths=tuple(changed_allowed_paths),
        changed_files=changed_files,
        attempted_models=attempted_models,
        thread_id=thread_id,
    )


def _operator_payload(
    *,
    evaluation: OutputQualityEvaluation,
    parse_error: str | None,
    blocked_reason: str | None,
    blocked_message: str | None,
    parsed_paths: tuple[str, ...],
    changed_files: dict[str, str],
    attempted_models: list[str],
    thread_id: str | None,
) -> dict[str, Any]:
    return {
        "parse": {
            "parse_error": parse_error,
            "blocked_reason": blocked_reason,
            "blocked_message": blocked_message,
            "parsed_paths": sorted(parsed_paths),
        },
        "evaluation": evaluation.as_payload(),
        "changed_files": changed_files,
        "repairable": evaluation.status == "failed"
        and evaluation.failure_class not in {"blocked_missing_info", "blocked_unsafe"},
        "operator": {
            "attempted_models": attempted_models,
            "thread_id": thread_id,
        },
    }


def _parse_failure_evaluation(
    *,
    parse_result: Any,
    shared_install_result: dict[str, Any],
):
    from lab.output_quality_grader import OutputQualityEvaluation

    failure_class = parse_result.failure_class or "output_invalid"
    status = "failed"
    if shared_install_result["exit_code"] != 0:
        failure_class = shared_install_result.get("failure_class") or "install_failed"
    return OutputQualityEvaluation(
        status=status,
        failure_class=failure_class,
        objective_pass=False,
        hidden_quality_pass=False,
        failing_checks=("parse",),
        first_failure_excerpt=parse_result.parse_error or parse_result.blocked_message,
        checks=(dict(shared_install_result, check_name="install"),),
    )


def _build_pairwise_results(
    *,
    task_pack: OutputQualityTaskPack,
    arms: tuple[ArmName, ...],
    arm_results: dict[str, Any],
    surface: OutputQualitySurface = DEFAULT_SURFACE,
) -> list[dict[str, Any]]:
    pairwise: list[dict[str, Any]] = []
    for left_arm, right_arm in (("cortex", "raw"), ("cortex", "tooling_only")):
        if left_arm not in arms or right_arm not in arms:
            continue
        order = stable_pair_order(f"{task_pack.task_id}:{left_arm}:{right_arm}")
        arm_to_label = {
            left_arm: order[0],
            right_arm: order[1],
        }
        label_to_arm = {label: arm for arm, label in arm_to_label.items()}
        output_a = arm_results[label_to_arm["a"]]
        output_b = arm_results[label_to_arm["b"]]
        judgment = judge_pairwise_merge_worthiness(
            prompt_text=task_pack.prompt_text,
            output_a=output_a,
            output_b=output_b,
            surface=surface,
        )
        winner_arm = label_to_arm.get(judgment.winner) if judgment.winner is not None else None
        pairwise.append(
            {
                "task_id": task_pack.task_id,
                "left_arm": left_arm,
                "right_arm": right_arm,
                "winner_arm": winner_arm,
                "confidence": judgment.confidence,
                "reason_tags": list(judgment.reason_tags),
                "objective_override": judgment.objective_override,
            }
        )
    return pairwise


def _build_suite_summary(
    *,
    run_root: Path,
    task_ids: tuple[str, ...],
    arms: tuple[ArmName, ...],
    model: str,
    surface: OutputQualitySurface = DEFAULT_SURFACE,
    task_results: dict[str, Any],
    aggregate_objective: dict[str, int],
    aggregate_hidden: dict[str, int],
    pairwise_results: list[dict[str, Any]],
    env_blocked: bool,
    ablation_config: OutputQualityAblationConfig | None,
) -> dict[str, Any]:
    try:
        artifact_root = str(run_root.relative_to(ROOT))
    except ValueError:
        artifact_root = str(run_root)
    pairwise_summary = {}
    for left_arm, right_arm in (("cortex", "raw"), ("cortex", "tooling_only")):
        relevant = [
            result
            for result in pairwise_results
            if result["left_arm"] == left_arm and result["right_arm"] == right_arm
        ]
        if not relevant:
            continue
        wins = sum(1 for result in relevant if result["winner_arm"] == left_arm)
        losses = sum(1 for result in relevant if result["winner_arm"] == right_arm)
        ties = sum(1 for result in relevant if result["winner_arm"] is None)
        pairwise_summary[f"{left_arm}_vs_{right_arm}"] = {
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": wins / len(relevant),
        }

    return {
        "generated_at": now_utc_iso(),
        "artifact_root": artifact_root,
        "provider": "openai",
        "surface": surface,
        "model": model,
        "ablation_config": (
            ablation_config.as_payload() if ablation_config is not None else None
        ),
        "arms": list(arms),
        "task_ids": list(task_ids),
        "task_results": task_results,
        "aggregate_objective_pass_count": aggregate_objective,
        "aggregate_hidden_quality_pass_count": aggregate_hidden,
        "pairwise_summary": pairwise_summary,
        "env_blocked": env_blocked,
    }


def _render_summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Output Quality Summary",
        "",
        f"- surface: `{summary['surface']}`",
        f"- model: `{summary['model']}`",
        f"- arms: `{', '.join(summary['arms'])}`",
        f"- env_blocked: `{summary['env_blocked']}`",
        "",
    ]
    for pair_name, payload in sorted(summary["pairwise_summary"].items()):
        lines.extend(
            [
                f"## {pair_name}",
                "",
                f"- wins: `{payload['wins']}`",
                f"- losses: `{payload['losses']}`",
                f"- ties: `{payload['ties']}`",
                f"- win_rate: `{payload['win_rate']:.2f}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _execute_openai_turn(
    *,
    model: str,
    input_text: str,
    max_output_tokens: int,
    previous_response_id: str | None = None,
    input_text_override: str | None = None,
) -> dict[str, Any]:
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model=model,
        input_text=input_text,
        max_output_tokens=max_output_tokens,
    )
    raw_events = execute_openai_response_stream_turn(
        request,
        previous_response_id=previous_response_id,
        input_text_override=input_text_override,
    )
    output_text = _extract_response_output_text(raw_events)
    response_id = _last_response_id(raw_events)
    return {
        "response_id": response_id,
        "output_text": output_text,
        "raw_events": raw_events,
    }


def _extract_response_output_text(raw_events: list[dict[str, Any]]) -> str | None:
    chunks: list[str] = []
    for raw_event in raw_events:
        if raw_event.get("type") != "response.output_text.delta":
            continue
        delta = raw_event.get("delta")
        if isinstance(delta, str) and delta:
            chunks.append(delta)
    if not chunks:
        return None
    joined = "".join(chunks).strip()
    return joined or None


def _last_response_id(raw_events: list[dict[str, Any]]) -> str | None:
    for raw_event in reversed(raw_events):
        response_id = raw_event.get("response_id")
        if isinstance(response_id, str) and response_id.strip():
            return response_id.strip()
        response = raw_event.get("response")
        if isinstance(response, dict):
            nested_response_id = response.get("id")
            if isinstance(nested_response_id, str) and nested_response_id.strip():
                return nested_response_id.strip()
    return None


def _task_pack_registry() -> dict[str, OutputQualityTaskPack]:
    base = ROOT / "tests" / "lab" / "fixtures" / "output_quality"
    shared_web_commands = {
        "install": ("npm", "ci"),
        "lint": ("npm", "run", "lint"),
        "typecheck": ("npm", "run", "typecheck"),
        "build": ("npm", "run", "build"),
        "visible": ("npm", "run", "test:visible"),
        "hidden": ("npm", "run", "test:hidden"),
    }
    return {
        "astro_docs_site_v1": OutputQualityTaskPack(
            task_id="astro_docs_site_v1",
            prompt_text=_read_task_prompt(base / "astro_docs_site_v1" / "README_TASK.md"),
            template_root=base / "astro_docs_site_v1",
            allowed_write_paths=(
                "src/components/Header.astro",
                "src/lib/docs.ts",
                "src/pages/docs/index.astro",
                "src/pages/docs/[section]/[slug].astro",
                "src/pages/tags/[tag].astro",
            ),
            visible_context_paths=(
                "package.json",
                "astro.config.mjs",
                "src/layouts/Layout.astro",
                "src/pages/index.astro",
                "scripts/test-visible.mjs",
            ),
            verifier_only_paths=("scripts/test-hidden.mjs",),
            install_command=shared_web_commands["install"],
            lint_command=shared_web_commands["lint"],
            typecheck_command=shared_web_commands["typecheck"],
            build_command=shared_web_commands["build"],
            visible_test_command=shared_web_commands["visible"],
            hidden_test_command=shared_web_commands["hidden"],
        ),
        "astro_marketing_forms_v1": OutputQualityTaskPack(
            task_id="astro_marketing_forms_v1",
            prompt_text=_read_task_prompt(base / "astro_marketing_forms_v1" / "README_TASK.md"),
            template_root=base / "astro_marketing_forms_v1",
            allowed_write_paths=(
                "src/components/Header.astro",
                "src/lib/resources.ts",
                "src/pages/resources/index.astro",
                "src/pages/resources/[slug].astro",
                "src/pages/contact.astro",
                "src/pages/demo.astro",
            ),
            visible_context_paths=(
                "package.json",
                "astro.config.mjs",
                "src/layouts/Layout.astro",
                "src/pages/index.astro",
                "scripts/test-visible.mjs",
            ),
            verifier_only_paths=("scripts/test-hidden.mjs",),
            install_command=shared_web_commands["install"],
            lint_command=shared_web_commands["lint"],
            typecheck_command=shared_web_commands["typecheck"],
            build_command=shared_web_commands["build"],
            visible_test_command=shared_web_commands["visible"],
            hidden_test_command=shared_web_commands["hidden"],
        ),
        "react_dashboard_v1": OutputQualityTaskPack(
            task_id="react_dashboard_v1",
            prompt_text=_read_task_prompt(base / "react_dashboard_v1" / "README_TASK.md"),
            template_root=base / "react_dashboard_v1",
            allowed_write_paths=(
                "src/App.tsx",
                "src/components/AppNav.tsx",
                "src/data/projects.ts",
                "src/routes/ProjectsPage.tsx",
                "src/routes/ProjectDetailPage.tsx",
                "src/routes/TeamPage.tsx",
            ),
            visible_context_paths=(
                "package.json",
                "src/App.tsx",
                "src/components/AppNav.tsx",
                "src/data/projects.ts",
                "tests/visible/dashboard.test.tsx",
            ),
            verifier_only_paths=("tests/_verifier/dashboard_hidden.test.tsx",),
            install_command=shared_web_commands["install"],
            lint_command=shared_web_commands["lint"],
            typecheck_command=shared_web_commands["typecheck"],
            build_command=shared_web_commands["build"],
            visible_test_command=shared_web_commands["visible"],
            hidden_test_command=shared_web_commands["hidden"],
        ),
        "react_existing_feature_extension_v1": OutputQualityTaskPack(
            task_id="react_existing_feature_extension_v1",
            prompt_text=_read_task_prompt(
                base / "react_existing_feature_extension_v1" / "README_TASK.md"
            ),
            template_root=base / "react_existing_feature_extension_v1",
            allowed_write_paths=(
                "src/App.tsx",
                "src/components/Sidebar.tsx",
                "src/data/threads.ts",
                "src/routes/InboxPage.tsx",
                "src/routes/ThreadDetailPage.tsx",
                "src/routes/SavedViewsPage.tsx",
            ),
            visible_context_paths=(
                "package.json",
                "src/App.tsx",
                "src/components/Sidebar.tsx",
                "src/data/threads.ts",
                "tests/visible/inbox_extension.test.tsx",
            ),
            verifier_only_paths=("tests/_verifier/inbox_extension_hidden.test.tsx",),
            install_command=shared_web_commands["install"],
            lint_command=shared_web_commands["lint"],
            typecheck_command=shared_web_commands["typecheck"],
            build_command=shared_web_commands["build"],
            visible_test_command=shared_web_commands["visible"],
            hidden_test_command=shared_web_commands["hidden"],
        ),
        "frontend_bugfix_cleanup_v1": OutputQualityTaskPack(
            task_id="frontend_bugfix_cleanup_v1",
            prompt_text=_read_task_prompt(base / "frontend_bugfix_cleanup_v1" / "README_TASK.md"),
            template_root=base / "frontend_bugfix_cleanup_v1",
            allowed_write_paths=(
                "src/App.tsx",
                "src/components/AppNav.tsx",
                "src/data/plans.ts",
                "src/routes/BillingPage.tsx",
                "src/routes/InvoicesPage.tsx",
                "src/routes/PlanComparePage.tsx",
            ),
            visible_context_paths=(
                "package.json",
                "src/App.tsx",
                "src/components/AppNav.tsx",
                "src/data/plans.ts",
                "tests/visible/cleanup_visible.test.tsx",
            ),
            verifier_only_paths=("tests/_verifier/cleanup_hidden.test.tsx",),
            install_command=shared_web_commands["install"],
            lint_command=shared_web_commands["lint"],
            typecheck_command=shared_web_commands["typecheck"],
            build_command=shared_web_commands["build"],
            visible_test_command=shared_web_commands["visible"],
            hidden_test_command=shared_web_commands["hidden"],
        ),
    }


def _read_task_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _visible_test_paths(task_pack: OutputQualityTaskPack) -> tuple[str, ...]:
    return tuple(
        path
        for path in task_pack.visible_context_paths
        if "test" in path.lower()
    )


def evaluate_workspace_payload(payload: dict[str, Any]):
    from lab.output_quality_grader import OutputQualityEvaluation

    return OutputQualityEvaluation(
        status=payload["status"],
        failure_class=payload["failure_class"],
        objective_pass=payload["objective_pass"],
        hidden_quality_pass=payload["hidden_quality_pass"],
        failing_checks=tuple(payload["failing_checks"]),
        first_failure_excerpt=payload["first_failure_excerpt"],
        checks=tuple(payload["checks"]),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/cortex_output_quality.py",
        description="Run the E12 comparative output-quality benchmark on the OpenAI service or operator lane.",
    )
    parser.add_argument(
        "--tasks",
        nargs="*",
        default=list(supported_task_ids()),
    )
    parser.add_argument(
        "--arms",
        nargs="*",
        choices=DEFAULT_ARMS,
        default=list(DEFAULT_ARMS),
    )
    parser.add_argument(
        "--model",
        default=None,
    )
    parser.add_argument(
        "--surface",
        choices=("service_api", "operator_cli"),
        default=DEFAULT_SURFACE,
    )
    parser.add_argument(
        "--visible-contract-binding",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--verification-binding",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--repair-turn",
        choices=("on", "off"),
        default="on",
    )
    parser.add_argument(
        "--repair-ticket-style",
        choices=("factual", "minimal"),
        default="factual",
    )
    parser.add_argument(
        "--visible-context-variant",
        choices=("default", "writable_files_only", "writable_files_plus_visible_tests"),
        default="default",
    )
    args = parser.parse_args(argv)
    if args.surface == "service_api":
        require_openai_service_spend_approval(purpose="the E12 comparative output-quality benchmark")
    ablation_config = OutputQualityAblationConfig(
        visible_contract_binding=args.visible_contract_binding,
        verification_binding=args.verification_binding,
        repair_turn=args.repair_turn,
        repair_ticket_style=args.repair_ticket_style,
        visible_context_variant=args.visible_context_variant,
    )

    try:
        summary = run_output_quality_suite(
            task_ids=tuple(args.tasks),
            arms=tuple(args.arms),
            model=args.model,
            surface=args.surface,
            ablation_config=ablation_config,
        )
    except OpenAIResponseStreamTransportError as exc:
        print(
            json.dumps(
                {
                    "provider": "openai",
                    "env_blocked": True,
                    "failure_class": "provider_transport_error",
                    "message": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
