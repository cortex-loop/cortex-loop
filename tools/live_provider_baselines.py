"""Terminal-backed provider baseline capture for L1 live validation."""

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
    COMMON_SCENARIOS,
    HOST_TAILORED_SCENARIOS,
    PROVIDER_MODELS,
    PROVIDER_ROOTS,
    classify_failure,
    ensure_live_validation_dirs,
    extract_event_labels,
    extract_result_text,
    now_utc_iso,
    parse_json_lines,
    provider_cli_workspace,
    sanitize_text,
    should_collapse_after_failure,
    write_json,
    write_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_provider_baselines.py",
        description="Capture direct terminal-backed provider baseline runs for L1.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)

    overall_summary: dict[str, Any] = {
        "generated_at": now_utc_iso(),
        "surface": "provider_baseline",
        "providers": {},
    }
    for provider in providers:
        overall_summary["providers"][provider] = _capture_provider(provider)

    write_json(
        PROVIDER_ROOTS["comparators"] / "provider_baseline_summary.json",
        overall_summary,
    )
    print(json.dumps(overall_summary, indent=2, sort_keys=True))
    return 0


def _capture_provider(provider: str) -> dict[str, Any]:
    provider_root = PROVIDER_ROOTS[provider]
    schedule = [*COMMON_SCENARIOS, *HOST_TAILORED_SCENARIOS[provider]]
    runs: list[dict[str, Any]] = []
    blocked_failure: str | None = None

    for scenario in schedule:
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
                        "notes": "Skipped after an earlier blocking provider failure.",
                    }
                )
                continue
            result = _run_single_provider_baseline(
                provider=provider,
                scenario_id=scenario.scenario_id,
                prompt=scenario.prompt,
                max_output_tokens=scenario.max_output_tokens,
                repeat_index=repeat_index,
                provider_root=provider_root,
            )
            runs.append(result)
            if should_collapse_after_failure(result.get("failure_class")):
                blocked_failure = result["failure_class"]

    summary = {
        "provider": provider,
        "generated_at": now_utc_iso(),
        "runs": runs,
    }
    write_json(provider_root / "provider_baseline_runs.json", summary)
    return summary


def _run_single_provider_baseline(
    *,
    provider: str,
    scenario_id: str,
    prompt: str,
    max_output_tokens: int,
    repeat_index: int,
    provider_root: Path,
) -> dict[str, Any]:
    stem = f"provider_baseline__{scenario_id}__run_{repeat_index:03d}"
    stdout_path = provider_root / f"{stem}.stdout.log"
    stderr_path = provider_root / f"{stem}.stderr.log"
    metadata_path = provider_root / f"{stem}.json"

    started_at = now_utc_iso()
    if provider == "openai":
        run_result = _run_openai_baseline(prompt, max_output_tokens=max_output_tokens)
    else:
        run_result = _run_cli_baseline(provider, prompt)
    ended_at = now_utc_iso()

    stdout_text = sanitize_text(run_result.pop("stdout"))
    stderr_text = sanitize_text(run_result.pop("stderr"))
    write_text(stdout_path, stdout_text)
    write_text(stderr_path, stderr_text)

    records = parse_json_lines(stdout_text)
    failure_class = classify_failure(f"{stdout_text}\n{stderr_text}")
    payload = {
        "provider": provider,
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": run_result["exit_code"] == 0 and failure_class is None,
        "failure_class": failure_class,
        "command": run_result["command"],
        "stdout_path": str(stdout_path.relative_to(provider_root.parents[2])),
        "stderr_path": str(stderr_path.relative_to(provider_root.parents[2])),
        "structured_event_count": len(records),
        "structured_event_labels": extract_event_labels(records),
        "result_text": extract_result_text(records, stdout_text),
        "notes": run_result.get("notes"),
    }
    write_json(metadata_path, payload)
    return payload


def _run_cli_baseline(provider: str, prompt: str) -> dict[str, Any]:
    with provider_cli_workspace() as workspace:
        cwd = Path(workspace)
        if provider == "claude":
            command = [
                "claude",
                "-p",
                prompt,
                "--model",
                PROVIDER_MODELS[provider],
                "--output-format",
                "stream-json",
                "--verbose",
                "--max-turns",
                "1",
                "--permission-mode",
                "plan",
            ]
        elif provider == "gemini":
            command = [
                "gemini",
                "-p",
                prompt,
                "-o",
                "stream-json",
                "-m",
                PROVIDER_MODELS[provider],
                "--approval-mode",
                "plan",
            ]
        else:
            raise ValueError(f"unsupported provider: {provider}")

        try:
            process = subprocess.run(
                command,
                cwd=str(cwd),
                text=True,
                capture_output=True,
                check=False,
                timeout=45.0,
            )
            return {
                "command": command,
                "exit_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
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


def _run_openai_baseline(prompt: str, *, max_output_tokens: int) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "command": [
                "urllib.request",
                "POST",
                "https://api.openai.com/v1/responses",
            ],
            "exit_code": 1,
            "stdout": "",
            "stderr": "OPENAI_API_KEY is required for the direct OpenAI baseline capture.",
            "notes": "The installed OpenAI CLI is present, but the baseline uses the Responses API directly for structured event capture.",
        }

    request_body = {
        "model": PROVIDER_MODELS["openai"],
        "input": [{"role": "user", "content": prompt}],
        "max_output_tokens": max_output_tokens,
        "stream": True,
    }
    http_request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=60.0) as response:
            raw_chunks = [line.decode("utf-8", errors="replace") for line in response]
        return {
            "command": [
                "urllib.request",
                "POST",
                "https://api.openai.com/v1/responses",
            ],
            "exit_code": 0,
            "stdout": "".join(raw_chunks),
            "stderr": "",
            "notes": "Direct Responses SSE capture over stdlib urllib.",
        }
    except urllib.error.HTTPError as exc:
        return {
            "command": [
                "urllib.request",
                "POST",
                "https://api.openai.com/v1/responses",
            ],
            "exit_code": 1,
            "stdout": "",
            "stderr": f"HTTP {exc.code}: {_http_error_message(exc)}",
            "notes": "Direct Responses SSE capture over stdlib urllib.",
        }
    except urllib.error.URLError as exc:
        return {
            "command": [
                "urllib.request",
                "POST",
                "https://api.openai.com/v1/responses",
            ],
            "exit_code": 1,
            "stdout": "",
            "stderr": f"connection failed: {exc.reason}",
            "notes": "Direct Responses SSE capture over stdlib urllib.",
        }


def _http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return exc.reason or "unknown upstream error"
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        if isinstance(error, str) and error.strip():
            return error.strip()
    return exc.reason or "unknown upstream error"


if __name__ == "__main__":
    raise SystemExit(main())
