"""Provider baseline capture for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from live_validation_common import (
    GEMINI_OPERATOR_FULL_LADDER,
    MODEL_MATRIX,
    classify_failure,
    choose_model,
    comparator_path,
    ensure_live_validation_dirs,
    extract_event_labels,
    extract_result_text,
    now_utc_iso,
    parse_json_lines,
    provider_cli_workspace,
    provider_root,
    resolve_auth_mode,
    run_command,
    sanitize_text,
    should_collapse_after_failure,
    vertex_adc_available,
    write_json,
    write_text,
)


_SMOKE_PROMPT = "Respond exactly with OK."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_provider_baselines.py",
        description="Capture provider baseline runs for the selected lane.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    parser.add_argument(
        "--lane",
        choices=("operator", "automation"),
        default="operator",
    )
    parser.add_argument(
        "--preferred-model",
        default=None,
    )
    parser.add_argument(
        "--fallback-model",
        default=None,
    )
    parser.add_argument(
        "--disable-auto-probe",
        action="store_true",
    )
    parser.add_argument(
        "--exploratory-probe",
        action="store_true",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    summary_name = (
        f"{args.lane}_provider_baseline_summary__exploratory.json"
        if args.exploratory_probe
        else f"{args.lane}_provider_baseline_summary.json"
    )
    summary_path = comparator_path(summary_name)
    overall_summary = _read_json(summary_path)
    if not overall_summary:
        overall_summary = {
            "generated_at": now_utc_iso(),
            "surface": "provider_baseline",
            "lane": args.lane,
            "providers": {},
        }
    overall_summary["generated_at"] = now_utc_iso()
    overall_summary["surface"] = "provider_baseline"
    overall_summary["lane"] = args.lane
    for provider in providers:
        overall_summary["providers"][provider] = _capture_provider(
            provider,
            lane=args.lane,
            preferred_model_override=args.preferred_model,
            fallback_model_override=args.fallback_model,
            disable_auto_probe=args.disable_auto_probe,
            exploratory_probe=args.exploratory_probe,
        )
    write_json(summary_path, overall_summary)
    print(json.dumps(overall_summary, indent=2, sort_keys=True))
    return 0


def _capture_provider(
    provider: str,
    *,
    lane: str,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
    exploratory_probe: bool,
) -> dict[str, Any]:
    root = provider_root(provider, lane, "baselines_exploratory" if exploratory_probe else "baselines")
    runs: list[dict[str, Any]] = []
    blocked_failure: str | None = None

    for repeat_index in (1, 2):
        if blocked_failure is not None:
            runs.append(
                {
                    "provider": provider,
                    "lane": lane,
                    "repeat_index": repeat_index,
                    "success": False,
                    "skipped": True,
                    "failure_class": blocked_failure,
                    "notes": "Skipped after an earlier blocking provider failure.",
                }
            )
            continue
        result = _run_single_provider_baseline(
            provider=provider,
            lane=lane,
            repeat_index=repeat_index,
            provider_root_path=root,
            preferred_model_override=preferred_model_override,
            fallback_model_override=fallback_model_override,
            disable_auto_probe=disable_auto_probe,
        )
        runs.append(result)
        if should_collapse_after_failure(result.get("failure_class")):
            blocked_failure = result["failure_class"]

    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": lane,
        "runs": runs,
    }
    write_json(root / "provider_baseline_runs.json", summary)
    return summary


def _run_single_provider_baseline(
    *,
    provider: str,
    lane: str,
    repeat_index: int,
    provider_root_path: Path,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> dict[str, Any]:
    stem = f"provider_baseline__smoke__run_{repeat_index:03d}"
    stdout_path = provider_root_path / f"{stem}.stdout.log"
    stderr_path = provider_root_path / f"{stem}.stderr.log"
    metadata_path = provider_root_path / f"{stem}.json"

    auth_mode = resolve_auth_mode(provider, lane)
    preferred_model = choose_model(provider, lane)
    auto_supported: bool | None = None
    ladder = _requested_model_ladder(
        provider=provider,
        lane=lane,
        preferred_model_override=preferred_model_override,
        fallback_model_override=fallback_model_override,
        disable_auto_probe=disable_auto_probe,
    )
    first_model = ladder[0]
    preferred_model = first_model
    started_at = now_utc_iso()
    run_result = _run_provider_probe(provider, lane=lane, auth_mode=auth_mode, model=first_model)
    failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
    if failure_class is None and run_result["exit_code"] == 124:
        failure_class = "operator_timeout" if lane == "operator" else "quota_exhausted"
    attempted_models = [first_model]
    if provider == "gemini" and lane == "operator":
        auto_supported = run_result["exit_code"] == 0 and failure_class != "model_unavailable"
        preferred_model = first_model if auto_supported or run_result["exit_code"] == 0 else GEMINI_OPERATOR_FULL_LADDER[1]
    chosen_model = first_model
    if run_result["exit_code"] != 0:
        chosen_model = choose_model(
            provider,
            lane,
            first_failure=failure_class,
            current_model=first_model,
            auto_supported=auto_supported,
            ladder=ladder,
        )
    while chosen_model != attempted_models[-1]:
        run_result = _run_provider_probe(provider, lane=lane, auth_mode=auth_mode, model=chosen_model)
        failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
        if failure_class is None and run_result["exit_code"] == 124:
            failure_class = "operator_timeout" if lane == "operator" else "quota_exhausted"
        attempted_models.append(chosen_model)
        chosen_model = choose_model(
            provider,
            lane,
            first_failure=failure_class,
            current_model=chosen_model,
            auto_supported=auto_supported,
            ladder=ladder,
        )
    ended_at = now_utc_iso()

    stdout_text = sanitize_text(run_result.pop("stdout"))
    stderr_text = sanitize_text(run_result.pop("stderr"))
    write_text(stdout_path, stdout_text)
    write_text(stderr_path, stderr_text)

    records = parse_json_lines(stdout_text)
    warning_classes: list[str] = []
    effective_failure_class = failure_class
    if provider == "gemini" and lane == "operator" and run_result["exit_code"] == 0 and failure_class in {"capacity_exhausted", "quota_exhausted"}:
        warning_classes = [failure_class]
        effective_failure_class = None
    payload = {
        "provider": provider,
        "lane": lane,
        "repeat_index": repeat_index,
        "auth_mode": auth_mode,
        "preferred_model": preferred_model,
        "model": attempted_models[-1],
        "auto_supported": auto_supported,
        "attempted_models": attempted_models,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": run_result["exit_code"] == 0 and effective_failure_class is None,
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "command": run_result["command"],
        "stdout_path": str(stdout_path.relative_to(provider_root_path.parents[4])),
        "stderr_path": str(stderr_path.relative_to(provider_root_path.parents[4])),
        "structured_event_count": len(records),
        "structured_event_labels": extract_event_labels(records),
        "result_text": extract_result_text(records, stdout_text),
        "notes": run_result.get("notes"),
    }
    write_json(metadata_path, payload)
    return payload


def _run_provider_probe(
    provider: str,
    *,
    lane: str,
    auth_mode: str,
    model: str,
) -> dict[str, Any]:
    if lane == "operator":
        if provider == "claude":
            return _run_claude_operator_probe(model)
        if provider == "gemini":
            return _run_gemini_operator_probe(model)
        return _run_openai_operator_probe(model)
    if provider == "claude":
        return _run_claude_automation_probe(model, auth_mode=auth_mode)
    if provider == "gemini":
        return _run_gemini_automation_probe(model, auth_mode=auth_mode)
    return _run_openai_automation_probe(model, auth_mode=auth_mode)


def _run_claude_operator_probe(model: str) -> dict[str, Any]:
    with provider_cli_workspace() as workspace:
        return run_command(
            [
                "claude",
                "-p",
                _SMOKE_PROMPT,
                "--model",
                model,
                "--output-format",
                "stream-json",
                "--verbose",
                "--max-turns",
                "1",
                "--permission-mode",
                "plan",
            ],
            cwd=Path(workspace),
            timeout_seconds=30.0,
        )


def _run_gemini_operator_probe(model: str) -> dict[str, Any]:
    with provider_cli_workspace() as workspace:
        command = [
            "gemini",
            "-p",
            _SMOKE_PROMPT,
            "-o",
            "stream-json",
            "--approval-mode",
            "plan",
        ]
        if model != "auto":
            command[5:5] = ["-m", model]
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                text=True,
                capture_output=True,
                timeout=45.0,
                check=False,
            )
            return {
                "command": command,
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
            stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
            return {
                "command": command,
                "exit_code": 124,
                "stdout": stdout,
                "stderr": stderr,
                "notes": "provider CLI timed out; partial output preserved for blocker classification",
            }


def _run_openai_operator_probe(model: str) -> dict[str, Any]:
    with provider_cli_workspace() as workspace:
        return run_command(
            [
                "codex",
                "exec",
                "--json",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "-m",
                model,
                _SMOKE_PROMPT,
            ],
            cwd=Path(workspace),
            timeout_seconds=30.0,
        )


def _run_claude_automation_probe(model: str, *, auth_mode: str) -> dict[str, Any]:
    if auth_mode != "api_key":
        return _unsupported_auth_mode("claude", auth_mode)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _missing_key_probe("ANTHROPIC_API_KEY")
    body = {
        "model": model,
        "max_tokens": 16,
        "messages": [{"role": "user", "content": _SMOKE_PROMPT}],
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    return _run_json_http_probe(request, note="Direct Anthropic Messages JSON probe.")


def _run_gemini_automation_probe(model: str, *, auth_mode: str) -> dict[str, Any]:
    if auth_mode == "vertex_adc":
        if not vertex_adc_available():
            return {
                "command": ["gcloud", "auth", "application-default", "print-access-token"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "Vertex ADC is not available for the Gemini automation lane.",
                "notes": "Expected GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION plus a valid ADC token.",
            }
        token = run_command(["gcloud", "auth", "application-default", "print-access-token"], timeout_seconds=30.0)
        project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION") or os.environ.get("VERTEX_LOCATION")
        request = urllib.request.Request(
            (
                f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}"
                f"/publishers/google/models/{model}:generateContent"
            ),
            data=json.dumps({"contents": [{"role": "user", "parts": [{"text": _SMOKE_PROMPT}]}]}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token['stdout'].strip()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        return _run_json_http_probe(request, note="Direct Vertex Gemini JSON probe.")
    if auth_mode != "api_key":
        return _unsupported_auth_mode("gemini", auth_mode)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _missing_key_probe("GEMINI_API_KEY")
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        data=json.dumps({"contents": [{"role": "user", "parts": [{"text": _SMOKE_PROMPT}]}]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return _run_json_http_probe(request, note="Direct Gemini JSON probe.")


def _run_openai_automation_probe(model: str, *, auth_mode: str) -> dict[str, Any]:
    if auth_mode != "api_key":
        return _unsupported_auth_mode("openai", auth_mode)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _missing_key_probe("OPENAI_API_KEY")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps({"model": model, "input": _SMOKE_PROMPT}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return _run_json_http_probe(request, note="Direct OpenAI Responses JSON probe.")


def _run_json_http_probe(request: urllib.request.Request, *, note: str) -> dict[str, Any]:
    started_at = now_utc_iso()
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            payload = response.read().decode("utf-8")
        ended_at = now_utc_iso()
        return {
            "command": [request.full_url],
            "exit_code": 0,
            "stdout": payload,
            "stderr": "",
            "started_at": started_at,
            "ended_at": ended_at,
            "notes": note,
        }
    except urllib.error.HTTPError as exc:
        ended_at = now_utc_iso()
        body = exc.read().decode("utf-8")
        return {
            "command": [request.full_url],
            "exit_code": 1,
            "stdout": "",
            "stderr": f"HTTP {exc.code}: {body}",
            "started_at": started_at,
            "ended_at": ended_at,
            "notes": note,
        }
    except urllib.error.URLError as exc:
        ended_at = now_utc_iso()
        return {
            "command": [request.full_url],
            "exit_code": 1,
            "stdout": "",
            "stderr": f"connection failed: {exc.reason}",
            "started_at": started_at,
            "ended_at": ended_at,
            "notes": note,
        }


def _missing_key_probe(key_name: str) -> dict[str, Any]:
    return {
        "command": [key_name],
        "exit_code": 1,
        "stdout": "",
        "stderr": f"{key_name} is required for the selected automation lane.",
    }


def _unsupported_auth_mode(provider: str, auth_mode: str) -> dict[str, Any]:
    return {
        "command": [provider, auth_mode],
        "exit_code": 1,
        "stdout": "",
        "stderr": f"{provider} automation auth mode `{auth_mode}` is not supported by this probe.",
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _requested_model_ladder(
    *,
    provider: str,
    lane: str,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> tuple[str, ...]:
    if preferred_model_override:
        ladder = [preferred_model_override]
        if fallback_model_override and fallback_model_override.lower() != "none" and fallback_model_override != preferred_model_override:
            ladder.append(fallback_model_override)
        return tuple(ladder)
    if provider == "gemini" and lane == "operator" and disable_auto_probe:
        ladder = ["gemini-2.5-flash"]
        if fallback_model_override and fallback_model_override.lower() != "none" and fallback_model_override not in ladder:
            ladder.append(fallback_model_override)
        elif "gemini-2.5-flash-lite" not in ladder:
            ladder.append("gemini-2.5-flash-lite")
        return tuple(ladder)
    return (MODEL_MATRIX[provider][lane].preferred,) if MODEL_MATRIX[provider][lane].fallback is None else (
        MODEL_MATRIX[provider][lane].preferred,
        MODEL_MATRIX[provider][lane].fallback,
    )


if __name__ == "__main__":
    raise SystemExit(main())
