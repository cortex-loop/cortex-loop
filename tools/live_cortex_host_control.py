"""Current loopback-service automation-lane probe for L2."""

from __future__ import annotations

import argparse
import json
import os
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
    MODEL_MATRIX,
    automation_auth_readiness,
    classify_failure,
    comparator_path,
    ensure_live_validation_dirs,
    live_evidence_fields,
    now_utc_iso,
    provider_root,
    resolve_auth_mode,
    write_json,
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

SMOKE_PROMPT = "Respond exactly with OK."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_cortex_host_control.py",
        description="Probe the current loopback-service automation lane.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    parser.add_argument(
        "--lane",
        choices=("automation",),
        default="automation",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    summary = _build_summary(
        lane=args.lane,
        provider_payloads={provider: _capture_provider(provider) for provider in providers},
    )
    if args.provider == "all":
        write_json(comparator_path("cortex_live_summary.json"), summary)
    else:
        write_json(comparator_path(f"cortex_live_summary_{args.provider}.json"), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _build_summary(
    *,
    lane: str,
    provider_payloads: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": now_utc_iso(),
        "surface": "cortex_live_host_control",
        "lane": lane,
        **live_evidence_fields(lane=lane),
        "providers": provider_payloads,
    }


def _capture_provider(provider: str) -> dict[str, Any]:
    root = provider_root(provider, "automation", "service")
    readiness = automation_auth_readiness(provider)
    auth_mode = readiness["auth_mode"]
    smoke_model = _service_model_for_scenario(provider, "service_smoke")
    continuity_model = _service_model_for_scenario(provider, "service_restart_continuity")
    if readiness["status"] != "ready":
        runs = [
            _blocked_service_run(provider, auth_mode=auth_mode, model=smoke_model, root=root, scenario_id="service_smoke", readiness=readiness),
            _blocked_service_run(provider, auth_mode=auth_mode, model=continuity_model, root=root, scenario_id="service_restart_continuity", readiness=readiness),
        ]
    else:
        runs = [
            _run_single_live_call(provider, auth_mode=auth_mode, model=smoke_model, root=root),
            _run_continuity_capture(provider, auth_mode=auth_mode, model=continuity_model, root=root),
        ]
    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_readiness": readiness,
        "runs": runs,
    }
    write_json(root / "service_runs.json", summary)
    return summary


def _service_model_for_scenario(provider: str, scenario_id: str) -> str:
    if provider == "openai" and scenario_id == "service_smoke":
        return "gpt-5.4-mini"
    return MODEL_MATRIX[provider]["automation"].preferred


def _blocked_service_run(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
    scenario_id: str,
    readiness: dict[str, Any],
) -> dict[str, Any]:
    artifact_path = root / f"{scenario_id}.blocked.json"
    failure_class = _service_failure_class_for_readiness(readiness["status"])
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "success": False,
        "failure_class": failure_class,
        "notes": f"Skipped live service proof because automation auth is `{readiness['status']}`.",
        "auth_readiness": readiness,
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
    return payload


def _run_single_live_call(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
) -> dict[str, Any]:
    stem = "service_smoke"
    request_path = root / f"{stem}.request.json"
    response_path = root / f"{stem}.response.json"
    export_path = root / f"{stem}.export.json"
    service_log_path = root / f"{stem}.service.stderr.log"
    payload = _action_payload(provider, SMOKE_PROMPT, model=model)
    write_json(request_path, payload)

    with _running_service(provider, service_log_path, auth_mode=auth_mode) as base_url:
        status_code, response_payload, request_started_at, response_received_at = _request_json(
            "POST",
            f"{base_url}{PROVIDER_CONFIG[provider]['action_path']}",
            payload,
        )
        export_status, export_payload, export_started_at, export_received_at = _request_json(
            "GET",
            f"{base_url}/v1/session/export",
            None,
        )
    write_json(response_path, response_payload)
    write_json(export_path, export_payload)
    failure_class = classify_failure(
        json.dumps(response_payload, sort_keys=True) + json.dumps(export_payload, sort_keys=True)
    )
    warning_classes: list[str] = []
    effective_failure_class = failure_class
    if status_code == 200 and export_status == 200 and failure_class in {"capacity_exhausted", "quota_exhausted"}:
        warning_classes = [failure_class]
        effective_failure_class = None
    records = response_payload.get("records")
    first_record_at = response_received_at if isinstance(records, list) and records else None
    final_record_at = response_received_at if isinstance(records, list) and records else None
    return {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": "service_smoke",
        "request_started_at": request_started_at,
        "first_record_at": first_record_at,
        "final_record_at": final_record_at,
        "export_received_at": export_received_at,
        "success": (
            status_code == 200
            and export_status == 200
            and effective_failure_class is None
            and isinstance(records, list)
        ),
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "http_statuses": {"action_status": status_code, "export_status": export_status},
        "request_path": str(request_path.relative_to(root.parents[4])),
        "response_path": str(response_path.relative_to(root.parents[4])),
        "export_path": str(export_path.relative_to(root.parents[4])),
        "service_log_path": str(service_log_path.relative_to(root.parents[4])),
        "record_count": len(records) if isinstance(records, list) else 0,
    }


def _run_continuity_capture(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
) -> dict[str, Any]:
    stem = "service_restart_continuity"
    artifact_path = root / f"{stem}.json"
    first_request_path = root / f"{stem}.first.request.json"
    second_request_path = root / f"{stem}.second.request.json"
    first_response_path = root / f"{stem}.first.response.json"
    first_export_path = root / f"{stem}.first.export.json"
    import_response_path = root / f"{stem}.import.response.json"
    second_response_path = root / f"{stem}.second.response.json"
    final_export_path = root / f"{stem}.final.export.json"
    first_payload = _action_payload(provider, "first step", model=model)
    second_payload = _action_payload(provider, "second step", model=model)
    write_json(first_request_path, first_payload)
    write_json(second_request_path, second_payload)

    with _running_service(provider, root / f"{stem}.first.service.stderr.log", auth_mode=auth_mode) as first_url:
        first_status, first_response, first_request_started_at, first_response_received_at = _request_json(
            "POST",
            f"{first_url}{PROVIDER_CONFIG[provider]['action_path']}",
            first_payload,
        )
        export_status, exported_seed, first_export_started_at, first_export_received_at = _request_json(
            "GET", f"{first_url}/v1/session/export", None
        )
    write_json(first_response_path, first_response)
    write_json(first_export_path, exported_seed)

    if first_status != 200 or export_status != 200:
        payload = {
            "provider": provider,
            "lane": "automation",
            **live_evidence_fields(lane="automation"),
            "auth_mode": auth_mode,
            "model": model,
            "success": False,
            "failure_class": classify_failure(
                json.dumps(first_response, sort_keys=True) + json.dumps(exported_seed, sort_keys=True)
            ),
            "http_statuses": {"first_status": first_status, "export_status": export_status},
            "notes": "Continuity stopped at the first action/export boundary.",
            "first_request_path": str(first_request_path.relative_to(root.parents[4])),
            "first_response_path": str(first_response_path.relative_to(root.parents[4])),
            "first_export_path": str(first_export_path.relative_to(root.parents[4])),
            "request_started_at": first_request_started_at,
            "first_record_at": first_response_received_at
            if isinstance(first_response.get("records"), list) and first_response.get("records")
            else None,
            "final_record_at": first_response_received_at
            if isinstance(first_response.get("records"), list) and first_response.get("records")
            else None,
            "export_received_at": first_export_received_at,
            "warning_classes": [],
        }
        write_json(artifact_path, payload)
        payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
        payload["scenario_id"] = "service_restart_continuity"
        return payload

    with _running_service(provider, root / f"{stem}.second.service.stderr.log", auth_mode=auth_mode) as second_url:
        import_status, import_response, import_started_at, import_received_at = _request_json(
            "POST",
            f"{second_url}/v1/session/import",
            exported_seed,
        )
        second_status, second_response, second_request_started_at, second_response_received_at = _request_json(
            "POST",
            f"{second_url}{PROVIDER_CONFIG[provider]['action_path']}",
            second_payload,
        )
        final_export_status, final_export, final_export_started_at, final_export_received_at = _request_json(
            "GET",
            f"{second_url}/v1/session/export",
            None,
        )
    write_json(import_response_path, import_response)
    write_json(second_response_path, second_response)
    write_json(final_export_path, final_export)
    failure_class = classify_failure(
        json.dumps(import_response, sort_keys=True)
        + json.dumps(second_response, sort_keys=True)
        + json.dumps(final_export, sort_keys=True)
    )
    warning_classes: list[str] = []
    effective_failure_class = failure_class
    if (
        import_status == 200
        and second_status == 200
        and final_export_status == 200
        and failure_class in {"capacity_exhausted", "quota_exhausted"}
    ):
        warning_classes = [failure_class]
        effective_failure_class = None
    second_records = second_response.get("records")
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": "service_restart_continuity",
        "success": (
            import_status == 200
            and second_status == 200
            and final_export_status == 200
            and isinstance(second_records, list)
            and effective_failure_class is None
        ),
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "http_statuses": {
            "first_status": first_status,
            "export_status": export_status,
            "import_status": import_status,
            "second_status": second_status,
            "final_export_status": final_export_status,
        },
        "request_started_at": first_request_started_at,
        "first_record_at": first_response_received_at
        if isinstance(first_response.get("records"), list) and first_response.get("records")
        else None,
        "final_record_at": second_response_received_at
        if isinstance(second_records, list) and second_records
        else None,
        "import_received_at": import_received_at,
        "final_export_received_at": final_export_received_at,
        "record_count": len(first_response.get("records", [])) + len(second_records or [])
        if isinstance(first_response.get("records"), list) and isinstance(second_records, list)
        else 0,
        "first_request_path": str(first_request_path.relative_to(root.parents[4])),
        "second_request_path": str(second_request_path.relative_to(root.parents[4])),
        "first_response_path": str(first_response_path.relative_to(root.parents[4])),
        "first_export_path": str(first_export_path.relative_to(root.parents[4])),
        "import_response_path": str(import_response_path.relative_to(root.parents[4])),
        "second_response_path": str(second_response_path.relative_to(root.parents[4])),
        "final_export_path": str(final_export_path.relative_to(root.parents[4])),
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
    return payload


def _action_payload(provider: str, prompt: str, *, model: str) -> dict[str, Any]:
    return {
        "action_tag": PROVIDER_CONFIG[provider]["action_tag"],
        "request": {
            "model": model,
            "input": prompt,
            "max_output_tokens": 96,
        },
    }


@contextmanager
def _running_service(provider: str, log_path: Path, *, auth_mode: str) -> Iterator[str]:
    port = _free_port()
    module = PROVIDER_CONFIG[provider]["module"]
    env = os.environ.copy()
    if provider == "claude":
        env["CORTEX_CLAUDE_LIVE_AUTH_MODE"] = auth_mode
    elif provider == "gemini":
        env["CORTEX_GEMINI_LIVE_AUTH_MODE"] = auth_mode
    else:
        env["CORTEX_OPENAI_LIVE_AUTH_MODE"] = auth_mode
    command = [sys.executable, "-m", module, "--port", str(port)]
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=log_file,
            cwd=str(Path(__file__).resolve().parents[1]),
            env=env,
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
            status_code, payload, _started_at, _ended_at = _request_json("GET", f"{base_url}/health", None)
            if status_code == 200 and payload.get("runtime") == expected_runtime:
                return
        except Exception as exc:  # pragma: no cover
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"service at {base_url} did not become healthy: {last_error}")


def _request_json(method: str, url: str, payload: dict[str, Any] | None) -> tuple[int, dict[str, Any], str, str]:
    started_at = now_utc_iso()
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            data = response.read().decode("utf-8")
            return response.getcode(), json.loads(data), started_at, now_utc_iso()
    except urllib.error.HTTPError as exc:
        data = exc.read().decode("utf-8")
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            payload = {"error": data or exc.reason}
        return exc.code, payload, started_at, now_utc_iso()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _service_failure_class_for_readiness(status: str) -> str:
    if status == "blocked_by_spend_policy":
        return "blocked_by_spend_policy"
    if status == "mis_scoped":
        return "mis_scoped"
    return "auth_missing"


if __name__ == "__main__":
    raise SystemExit(main())
