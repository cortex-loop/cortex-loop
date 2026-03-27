"""Signed-in host-native product-path harness for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from live_validation_common import (
    BLOCKING_FAILURE_CLASSES,
    MODEL_MATRIX,
    SCENARIOS,
    choose_model,
    classify_failure,
    classify_truth_gap,
    collect_modified_files,
    comparator_path,
    ensure_live_validation_dirs,
    extract_event_labels,
    extract_result_text,
    extract_session_id,
    now_utc_iso,
    parse_json_lines,
    prepare_harness_workspace,
    provider_root,
    read_prompt_template,
    resolve_auth_mode,
    run_target_test,
    sanitize_text,
    should_collapse_after_failure,
    write_json,
    write_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_host_native_product_paths.py",
        description="Run signed-in host-native product-path validations on the shared coding harness.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    summary_path = comparator_path("host_native_product_paths_summary.json")
    summary = _read_json(summary_path)
    if not summary:
        summary = {
            "generated_at": now_utc_iso(),
            "surface": "host_native_product_paths",
            "lane": "operator",
            "providers": {},
        }
    summary["generated_at"] = now_utc_iso()
    summary["surface"] = "host_native_product_paths"
    summary["lane"] = "operator"
    for provider in providers:
        summary["providers"][provider] = _run_provider(provider)
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _run_provider(provider: str) -> dict[str, Any]:
    root = provider_root(provider, "operator", "product_paths")
    baseline_summary = _read_json(comparator_path("operator_provider_baseline_summary.json"))
    baseline_runs = baseline_summary.get("providers", {}).get(provider, {}).get("runs", [])
    blocking_baseline_failures = sorted(
        {
            run["failure_class"]
            for run in baseline_runs
            if run.get("failure_class") in BLOCKING_FAILURE_CLASSES
        }
    )
    successful_baseline_runs = [run for run in baseline_runs if run.get("success")]
    if blocking_baseline_failures or not successful_baseline_runs:
        summary = {
            "generated_at": now_utc_iso(),
            "provider": provider,
            "lane": "operator",
            "runs": [
                {
                    "provider": provider,
                    "scenario_id": "operator_product_gate",
                    "repeat_index": 1,
                    "success": False,
                    "failure_class": blocking_baseline_failures[0] if blocking_baseline_failures else "operator_surface_missing",
                    "notes": "Skipped heavy operator product-path execution because the signed-in baseline lane is not yet stable.",
                }
            ],
        }
        write_json(root / "host_native_product_runs.json", summary)
        return summary

    runs: list[dict[str, Any]] = []
    blocked_failure: str | None = None

    for scenario in SCENARIOS:
        for repeat_index in range(1, scenario.repeat_count + 1):
            if blocked_failure is not None:
                runs.append(
                    {
                        "provider": provider,
                        "scenario_id": scenario.scenario_id,
                        "repeat_index": repeat_index,
                        "success": False,
                        "skipped": True,
                        "failure_class": blocked_failure,
                        "notes": "Skipped after an earlier blocking operator-lane failure.",
                    }
                )
                continue
            result = _run_single_scenario(provider, scenario.scenario_id, repeat_index, root)
            runs.append(result)
            if should_collapse_after_failure(result.get("failure_class")):
                blocked_failure = result["failure_class"]

    continuity = _run_restart_continuity(provider, root)
    runs.append(continuity)
    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "operator",
        "runs": runs,
    }
    write_json(root / "host_native_product_runs.json", summary)
    return summary


def _run_single_scenario(
    provider: str,
    scenario_id: str,
    repeat_index: int,
    root: Path,
) -> dict[str, Any]:
    project_root = prepare_harness_workspace(
        provider=provider,
        lane="operator",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    prompt_file = next(spec.operator_prompt for spec in SCENARIOS if spec.scenario_id == scenario_id)
    prompt = read_prompt_template(prompt_file)
    model = MODEL_MATRIX[provider]["operator"].preferred
    auth_mode = resolve_auth_mode(provider, "operator")
    run_result = _run_provider_task(
        provider,
        prompt=prompt,
        project_root=project_root,
        model=model,
        auth_mode=auth_mode,
    )
    failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
    if failure_class is None and run_result["exit_code"] == 124:
        failure_class = "operator_timeout"
    chosen_model = choose_model(provider, "operator", first_failure=failure_class)
    if chosen_model != model:
        run_result = _run_provider_task(
            provider,
            prompt=prompt,
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
        )
        failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
        if failure_class is None and run_result["exit_code"] == 124:
            failure_class = "operator_timeout"
    return _materialize_operator_run(
        provider=provider,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        project_root=project_root,
        root=root,
        run_result=run_result,
        model=chosen_model,
        auth_mode=auth_mode,
        failure_class=failure_class,
    )


def _run_restart_continuity(provider: str, root: Path) -> dict[str, Any]:
    repeat_index = 1
    project_root = prepare_harness_workspace(
        provider=provider,
        lane="operator",
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
    )
    auth_mode = resolve_auth_mode(provider, "operator")
    chosen_model = MODEL_MATRIX[provider]["operator"].preferred

    first_result = _run_provider_task(
        provider,
        prompt=read_prompt_template("restart_continuity_turn1_operator.md"),
        project_root=project_root,
        model=chosen_model,
        auth_mode=auth_mode,
    )
    first_failure = classify_failure(f"{first_result['stdout']}\n{first_result['stderr']}")
    if first_failure is None and first_result["exit_code"] == 124:
        first_failure = "operator_timeout"
    chosen_model = choose_model(provider, "operator", first_failure=first_failure)
    if chosen_model != MODEL_MATRIX[provider]["operator"].preferred:
        first_result = _run_provider_task(
            provider,
            prompt=read_prompt_template("restart_continuity_turn1_operator.md"),
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
        )
        first_failure = classify_failure(f"{first_result['stdout']}\n{first_result['stderr']}")
        if first_failure is None and first_result["exit_code"] == 124:
            first_failure = "operator_timeout"

    if first_failure in BLOCKING_FAILURE_CLASSES:
        first_metadata = _materialize_operator_run(
            provider=provider,
            scenario_id="restart_continuity_turn_1",
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            run_result=first_result,
            model=chosen_model,
            auth_mode=auth_mode,
            failure_class=first_failure,
        )
        return {
            "provider": provider,
            "scenario_id": "restart_continuity",
            "repeat_index": repeat_index,
            "success": False,
            "failure_class": first_failure,
            "artifact_path": first_metadata["artifact_path"],
            "notes": "Continuity stopped at the first signed-in operator turn.",
        }

    first_records = parse_json_lines(first_result["stdout"])
    session_id = extract_session_id(provider, first_records)
    second_result = _resume_provider_task(
        provider,
        prompt=read_prompt_template("restart_continuity_turn2_operator.md"),
        project_root=project_root,
        model=chosen_model,
        auth_mode=auth_mode,
        session_id=session_id,
    )
    second_failure = classify_failure(f"{second_result['stdout']}\n{second_result['stderr']}")
    if second_failure is None and second_result["exit_code"] == 124:
        second_failure = "operator_timeout"
    payload = _materialize_operator_run(
        provider=provider,
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
        project_root=project_root,
        root=root,
        run_result=second_result,
        model=chosen_model,
        auth_mode=auth_mode,
        failure_class=second_failure,
    )
    payload["session_id"] = session_id
    write_json(root / "restart_continuity.latest.json", payload)
    return payload


def _materialize_operator_run(
    *,
    provider: str,
    scenario_id: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    run_result: dict[str, Any],
    model: str,
    auth_mode: str,
    failure_class: str | None,
) -> dict[str, Any]:
    stem = f"{scenario_id}__run_{repeat_index:03d}"
    stdout_path = root / f"{stem}.stdout.log"
    stderr_path = root / f"{stem}.stderr.log"
    metadata_path = root / f"{stem}.json"
    write_text(stdout_path, run_result["stdout"])
    write_text(stderr_path, run_result["stderr"])

    test_result = run_target_test(project_root)
    records = parse_json_lines(run_result["stdout"])
    modified_files = collect_modified_files(project_root)
    result_text = extract_result_text(records, run_result["stdout"])
    success = run_result["exit_code"] == 0 and failure_class is None and test_result["exit_code"] == 0
    truth_gap_kind = None
    if scenario_id == "truth_gap":
        truth_gap_kind = classify_truth_gap(
            result_text,
            test_passed=test_result["exit_code"] == 0,
            modified_files=modified_files,
        )
        success = truth_gap_kind == "truthful_incomplete"

    payload = {
        "provider": provider,
        "lane": "operator",
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "auth_mode": auth_mode,
        "model": model,
        "success": success,
        "failure_class": failure_class,
        "command": run_result["command"],
        "structured_event_count": len(records),
        "structured_event_labels": extract_event_labels(records),
        "result_text": result_text,
        "modified_files": modified_files,
        "test_exit_code": test_result["exit_code"],
        "test_stdout": test_result["stdout"].strip(),
        "test_stderr": test_result["stderr"].strip(),
        "workspace_label": str(project_root.relative_to(project_root.parents[4])),
        "stdout_path": str(stdout_path.relative_to(root.parents[4])),
        "stderr_path": str(stderr_path.relative_to(root.parents[4])),
        "truth_gap_kind": truth_gap_kind,
        "started_at": run_result["started_at"],
        "ended_at": run_result["ended_at"],
    }
    write_json(metadata_path, payload)
    payload["artifact_path"] = str(metadata_path.relative_to(root.parents[4]))
    return payload


def _run_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_claude_task(prompt, project_root=project_root, model=model, auth_mode=auth_mode)
    if provider == "gemini":
        return _run_gemini_task(prompt, project_root=project_root, model=model, auth_mode=auth_mode)
    return _run_codex_task(prompt, project_root=project_root, model=model, auth_mode=auth_mode)


def _resume_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
    session_id: str | None,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
        )
    if provider == "gemini":
        return _run_gemini_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
        )
    return _run_codex_task(
        prompt,
        project_root=project_root,
        model=model,
        auth_mode=auth_mode,
        resume_session=session_id,
    )


def _run_claude_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
) -> dict[str, Any]:
    command = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        "1",
        "--permission-mode",
        "bypassPermissions",
    ]
    if auth_mode != "claude_code":
        return _unsupported_operator_mode("claude", auth_mode, command)
    if resume_session:
        command.extend(["--resume", resume_session])
    return _run_timed_command(command, cwd=project_root, timeout_seconds=120.0)


def _run_gemini_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
) -> dict[str, Any]:
    if auth_mode != "google_login":
        return _unsupported_operator_mode("gemini", auth_mode, ["gemini"])
    command = [
        "gemini",
        "-p",
        prompt,
        "-o",
        "stream-json",
        "-m",
        model,
        "--approval-mode",
        "yolo",
    ]
    if resume_session:
        command.extend(["-r", resume_session])
    return _run_timed_command(command, cwd=project_root, timeout_seconds=120.0)


def _run_codex_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
) -> dict[str, Any]:
    if auth_mode != "codex_cli":
        return _unsupported_operator_mode("openai", auth_mode, ["codex"])
    if resume_session:
        command = [
            "codex",
            "exec",
            "resume",
            "--json",
            "--full-auto",
            resume_session,
            prompt,
        ]
    else:
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
    return _run_timed_command(command, cwd=project_root, timeout_seconds=120.0)


def _run_timed_command(
    command: list[str],
    *,
    cwd: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    started_at = now_utc_iso()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": sanitize_text(completed.stdout),
            "stderr": sanitize_text(completed.stderr),
            "started_at": started_at,
            "ended_at": now_utc_iso(),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        return {
            "command": command,
            "exit_code": 124,
            "stdout": sanitize_text(stdout),
            "stderr": sanitize_text(stderr),
            "started_at": started_at,
            "ended_at": now_utc_iso(),
        }


def _unsupported_operator_mode(provider: str, auth_mode: str, command: list[str]) -> dict[str, Any]:
    return {
        "command": command,
        "exit_code": 1,
        "stdout": "",
        "stderr": f"{provider} operator auth mode `{auth_mode}` is not supported by the host-native product-path harness.",
        "started_at": now_utc_iso(),
        "ended_at": now_utc_iso(),
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
