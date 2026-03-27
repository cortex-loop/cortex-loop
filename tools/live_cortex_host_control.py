"""Loopback-service live host-control capture for L1."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from live_validation_common import (
    COMMON_SCENARIOS,
    HOST_TAILORED_SCENARIOS,
    PROVIDER_MODELS,
    PROVIDER_ROOTS,
    classify_failure,
    ensure_live_validation_dirs,
    now_utc_iso,
    should_collapse_after_failure,
    write_json,
    write_text,
)


PROVIDER_CONFIG = {
    "claude": {
        "module": "cortex.runtime.claude_service",
        "runtime_label": "claude-service",
        "action_path": "/v1/actions/message-stream",
        "action_tag": "claude-message-stream",
    },
    "gemini": {
        "module": "cortex.runtime.gemini_service",
        "runtime_label": "gemini-service",
        "action_path": "/v1/actions/interaction-stream",
        "action_tag": "gemini-interaction-stream",
    },
    "openai": {
        "module": "cortex.runtime.openai_service",
        "runtime_label": "openai-service",
        "action_path": "/v1/actions/response-stream",
        "action_tag": "openai-response-stream",
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_cortex_host_control.py",
        description="Capture live Cortex loopback-service host-control runs for L1.",
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
        "surface": "cortex_live_host_control",
        "providers": {},
    }
    for provider in providers:
        overall_summary["providers"][provider] = _capture_provider(provider)
    write_json(
        PROVIDER_ROOTS["comparators"] / "cortex_live_summary.json",
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
                        "notes": "Skipped after an earlier blocking Cortex live-path failure.",
                    }
                )
                continue
            result = _run_single_live_call(
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

    continuity_result = _run_continuity_capture(provider, provider_root)
    runs.append(continuity_result)
    summary = {
        "provider": provider,
        "generated_at": now_utc_iso(),
        "runs": runs,
    }
    write_json(provider_root / "cortex_live_runs.json", summary)
    return summary


def _run_single_live_call(
    *,
    provider: str,
    scenario_id: str,
    prompt: str,
    max_output_tokens: int,
    repeat_index: int,
    provider_root: Path,
) -> dict[str, Any]:
    stem = f"cortex_live__{scenario_id}__run_{repeat_index:03d}"
    request_path = provider_root / f"{stem}.request.json"
    response_path = provider_root / f"{stem}.response.json"
    service_log_path = provider_root / f"{stem}.service.stderr.log"

    payload = _action_payload(provider, prompt, max_output_tokens=max_output_tokens)
    write_json(request_path, payload)

    started_at = now_utc_iso()
    with _running_service(provider, service_log_path) as base_url:
        status_code, response_payload = _request_json(
            "POST",
            f"{base_url}{PROVIDER_CONFIG[provider]['action_path']}",
            payload,
        )
        export_status, export_payload = _request_json(
            "GET",
            f"{base_url}/v1/session/export",
            None,
        )
    ended_at = now_utc_iso()

    response_payload["export_status"] = export_status
    response_payload["export_payload"] = export_payload
    write_json(response_path, response_payload)
    failure_class = classify_failure(json.dumps(response_payload, sort_keys=True))
    return {
        "provider": provider,
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": status_code == 200 and failure_class is None and "records" in response_payload,
        "failure_class": failure_class,
        "http_status": status_code,
        "request_path": str(request_path.relative_to(provider_root.parents[2])),
        "response_path": str(response_path.relative_to(provider_root.parents[2])),
        "service_log_path": str(service_log_path.relative_to(provider_root.parents[2])),
        "record_count": len(response_payload.get("records", [])) if isinstance(response_payload.get("records"), list) else 0,
    }


def _run_continuity_capture(provider: str, provider_root: Path) -> dict[str, Any]:
    stem = "cortex_live__core_03_two_turn_restart__continuity"
    first_request_path = provider_root / f"{stem}.first.request.json"
    second_request_path = provider_root / f"{stem}.second.request.json"
    continuity_path = provider_root / f"{stem}.json"
    service_log_path = provider_root / f"{stem}.service.stderr.log"

    first_payload = _action_payload(provider, "first step", max_output_tokens=96)
    second_payload = _action_payload(provider, "second step", max_output_tokens=96)
    write_json(first_request_path, first_payload)
    write_json(second_request_path, second_payload)

    started_at = now_utc_iso()
    with _running_service(provider, service_log_path) as first_url:
        first_status, first_response = _request_json(
            "POST",
            f"{first_url}{PROVIDER_CONFIG[provider]['action_path']}",
            first_payload,
        )
        export_status, exported_seed = _request_json("GET", f"{first_url}/v1/session/export", None)

    if first_status != 200 or export_status != 200:
        payload = {
            "provider": provider,
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "success": False,
            "failure_class": classify_failure(
                json.dumps(first_response, sort_keys=True) + json.dumps(exported_seed, sort_keys=True)
            ),
            "http_statuses": {
                "first_status": first_status,
                "export_status": export_status,
            },
            "notes": "Continuity capture stopped at the first action/export boundary.",
        }
        write_json(continuity_path, payload)
        return {
            "provider": provider,
            "scenario_id": "core_03_two_turn_restart__continuity",
            "repeat_index": 1,
            **payload,
            "artifact_path": str(continuity_path.relative_to(provider_root.parents[2])),
        }

    with _running_service(provider, service_log_path) as second_url:
        import_status, import_response = _request_json(
            "POST",
            f"{second_url}/v1/session/import",
            exported_seed,
        )
        second_status, second_response = _request_json(
            "POST",
            f"{second_url}{PROVIDER_CONFIG[provider]['action_path']}",
            second_payload,
        )
        final_export_status, final_export = _request_json(
            "GET",
            f"{second_url}/v1/session/export",
            None,
        )
    ended_at = now_utc_iso()
    payload = {
        "provider": provider,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": (
            import_status == 200
            and second_status == 200
            and final_export_status == 200
            and isinstance(second_response.get("records"), list)
        ),
        "failure_class": classify_failure(
            json.dumps(import_response, sort_keys=True)
            + json.dumps(second_response, sort_keys=True)
            + json.dumps(final_export, sort_keys=True)
        ),
        "http_statuses": {
            "first_status": first_status,
            "export_status": export_status,
            "import_status": import_status,
            "second_status": second_status,
            "final_export_status": final_export_status,
        },
        "record_count": len(first_response.get("records", [])) + len(second_response.get("records", []))
        if isinstance(first_response.get("records"), list) and isinstance(second_response.get("records"), list)
        else 0,
        "first_response": first_response,
        "second_response": second_response,
        "final_export": final_export,
    }
    write_json(continuity_path, payload)
    return {
        "provider": provider,
        "scenario_id": "core_03_two_turn_restart__continuity",
        "repeat_index": 1,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": payload["success"],
        "failure_class": payload["failure_class"],
        "artifact_path": str(continuity_path.relative_to(provider_root.parents[2])),
        "record_count": payload["record_count"],
    }


def _action_payload(provider: str, prompt: str, *, max_output_tokens: int) -> dict[str, Any]:
    config = PROVIDER_CONFIG[provider]
    request_payload: dict[str, Any] = {
        "model": PROVIDER_MODELS[provider],
        "input": prompt,
    }
    if provider == "claude":
        request_payload["max_output_tokens"] = max_output_tokens
    else:
        request_payload["max_output_tokens"] = max_output_tokens
    return {
        "action_tag": config["action_tag"],
        "request": request_payload,
    }


@contextmanager
def _running_service(provider: str, log_path: Path) -> Iterator[str]:
    port = _free_port()
    module = PROVIDER_CONFIG[provider]["module"]
    command = [sys.executable, "-m", module, "--port", str(port)]
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=log_file,
            cwd=str(Path(__file__).resolve().parents[1]),
            text=True,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            _wait_for_health(base_url, expected_runtime=PROVIDER_CONFIG[provider]["runtime_label"])
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_health(base_url: str, *, expected_runtime: str) -> None:
    deadline = time.time() + 10.0
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            status_code, payload = _request_json("GET", f"{base_url}/health", None)
            if status_code == 200 and payload.get("runtime") == expected_runtime:
                return
        except Exception as exc:  # pragma: no cover - best-effort readiness loop
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"service at {base_url} did not become healthy: {last_error}")


def _request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None,
) -> tuple[int, dict[str, Any]]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            data = response.read().decode("utf-8")
            return response.getcode(), json.loads(data)
    except urllib.error.HTTPError as exc:
        data = exc.read().decode("utf-8")
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            payload = {"error": data or exc.reason}
        return exc.code, payload


if __name__ == "__main__":
    raise SystemExit(main())
