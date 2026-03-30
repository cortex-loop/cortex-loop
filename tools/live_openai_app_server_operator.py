"""Codex App Server operator-lane lifecycle proof for the L2b live seam."""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import threading
import time
from collections import Counter
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import path differs between script execution and pytest import.
    from .live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        classify_truth_gap,
        collect_modified_files,
        comparator_path,
        ensure_live_validation_dirs,
        now_utc_iso,
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
except ImportError:  # pragma: no cover
    from live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        classify_truth_gap,
        collect_modified_files,
        comparator_path,
        ensure_live_validation_dirs,
        now_utc_iso,
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


_INIT_PARAMS = {
    "protocolVersion": "2026-03-26",
    "clientInfo": {
        "name": "cortex-live-validation",
        "version": "0.2",
    },
    "capabilities": {},
}
_THREAD_TIMEOUT_SECONDS = 45.0
_TURN_TIMEOUT_SECONDS = 240.0
_TEXT_INPUT = lambda prompt: [{"type": "text", "text": prompt, "text_elements": []}]
_HOST_CAVEAT_SCENARIO_ID = "openai_app_server_host_caveat"
_OPENAI_APP_SERVER_SCENARIOS = (
    ("pass_minimal", "pass_minimal_operator.md", 2, True),
    ("truth_gap", "truth_gap_operator.md", 1, True),
    (_HOST_CAVEAT_SCENARIO_ID, "host_caveat_operator_openai_app_server.md", 1, False),
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_openai_app_server_operator.py",
        description="Run the OpenAI signed-in App Server lifecycle proof over the shared coding harness.",
    )
    parser.add_argument(
        "--scenario",
        choices=("all", "pass_minimal", "truth_gap", "restart_continuity", _HOST_CAVEAT_SCENARIO_ID),
        default="all",
    )
    args = parser.parse_args(argv)

    summary = run_openai_app_server_validation(scenario=args.scenario)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def run_openai_app_server_validation(*, scenario: str = "all") -> dict[str, Any]:
    ensure_live_validation_dirs()
    root = provider_root("openai", "operator", "app_server")
    auth_mode = resolve_auth_mode("openai", "operator")
    runs: list[dict[str, Any]] = []
    blocking_failure: str | None = None

    if scenario in {"all", "pass_minimal", "truth_gap", _HOST_CAVEAT_SCENARIO_ID}:
        for scenario_id, prompt_file, repeat_count, run_test in _OPENAI_APP_SERVER_SCENARIOS:
            if scenario not in {"all", scenario_id}:
                continue
            for repeat_index in range(1, repeat_count + 1):
                if blocking_failure is not None:
                    runs.append(
                        {
                            "provider": "openai",
                            "lane": "operator",
                            "surface": "app_server",
                            "scenario_id": scenario_id,
                            "repeat_index": repeat_index,
                            "success": False,
                            "skipped": True,
                            "failure_class": blocking_failure,
                            "notes": "Skipped after an earlier blocking App Server failure.",
                        }
                    )
                    continue
                result = _run_single_turn_scenario(
                    root=root,
                    auth_mode=auth_mode,
                    scenario_id=scenario_id,
                    repeat_index=repeat_index,
                    prompt_file=prompt_file,
                    run_test=run_test,
                )
                runs.append(result)
                if should_collapse_after_failure(result.get("failure_class")):
                    blocking_failure = result["failure_class"]

    if scenario in {"all", "restart_continuity"}:
        for repeat_index in range(1, 3):
            if blocking_failure is not None:
                runs.append(
                    {
                        "provider": "openai",
                        "lane": "operator",
                        "surface": "app_server",
                        "scenario_id": "restart_continuity",
                        "repeat_index": repeat_index,
                        "success": False,
                        "skipped": True,
                        "failure_class": blocking_failure,
                        "notes": "Skipped after an earlier blocking App Server failure.",
                    }
                )
                continue
            result = _run_restart_continuity(root=root, auth_mode=auth_mode, repeat_index=repeat_index)
            runs.append(result)
            if should_collapse_after_failure(result.get("failure_class")):
                blocking_failure = result["failure_class"]

    summary = {
        "generated_at": now_utc_iso(),
        "provider": "openai",
        "lane": "operator",
        "surface": "app_server",
        "runs": runs,
    }
    write_json(root / "app_server_runs.json", summary)
    write_json(comparator_path("openai_app_server_summary.json"), summary)
    return summary


def summarize_app_server_timeline(
    timeline: list[dict[str, Any]],
    *,
    thread_read: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lifecycle_counts: Counter[str] = Counter()
    item_counts: Counter[str] = Counter()
    request_methods: list[str] = []
    agent_fragments: list[str] = []
    final_agent_text: str | None = None
    thread_id = _extract_thread_id(thread_read)

    for event in timeline:
        if event.get("direction") != "receive":
            continue
        method = event.get("method")
        if not isinstance(method, str):
            continue
        if event.get("kind") == "notification":
            lifecycle_counts[method] += 1
            if method in {"item/started", "item/completed"}:
                item_type = _extract_item_type(event.get("payload"))
                if item_type is not None:
                    item_counts[item_type] += 1
                if method == "item/completed":
                    completed_text = _extract_completed_agent_text(event.get("payload"))
                    if completed_text:
                        final_agent_text = completed_text
            if method == "item/agentMessage/delta":
                delta = _extract_agent_delta(event.get("payload"))
                if delta:
                    agent_fragments.append(delta)
            if method == "codex/event/task_complete":
                completed_text = _extract_completed_agent_text(event.get("payload"))
                if completed_text:
                    final_agent_text = completed_text
            if thread_id is None:
                thread_id = _extract_thread_id(event.get("payload"))
        elif event.get("kind") == "request":
            request_methods.append(method)

    result_text = final_agent_text or "".join(agent_fragments).strip() or _extract_agent_text(thread_read)
    return {
        "thread_id": thread_id,
        "lifecycle_event_count": sum(lifecycle_counts.values()),
        "lifecycle_event_labels": list(lifecycle_counts.keys()),
        "item_lifecycle_counts": dict(item_counts),
        "server_request_methods": request_methods,
        "result_text": result_text,
    }


def classify_app_server_request_blocker(request_methods: list[str]) -> str | None:
    if any(method.endswith("requestApproval") for method in request_methods):
        return "approval_requested"
    if any(method.endswith("requestUserInput") for method in request_methods):
        return "user_input_requested"
    return None


class _AppServerClient:
    def __init__(self, *, cwd: Path, stderr_path: Path, env: dict[str, str] | None = None) -> None:
        self._process = subprocess.Popen(
            ["codex", "app-server"],
            cwd=str(cwd),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        if self._process.stdin is None or self._process.stdout is None or self._process.stderr is None:
            raise RuntimeError("codex app-server did not expose stdio pipes")
        self._stdin = self._process.stdin
        self._stdout = self._process.stdout
        self._stderr = self._process.stderr
        self._stderr_path = stderr_path
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue()
        self._responses: dict[int, dict[str, Any]] = {}
        self._timeline: list[dict[str, Any]] = []
        self._stderr_lines: list[str] = []
        self._next_id = 1
        self._turn_completed_entries: list[dict[str, Any]] = []
        self._stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    @property
    def timeline(self) -> list[dict[str, Any]]:
        return list(self._timeline)

    @property
    def stderr_text(self) -> str:
        return "\n".join(line for line in self._stderr_lines if line)

    def initialize(self) -> None:
        self.request("initialize", _INIT_PARAMS, timeout_seconds=_THREAD_TIMEOUT_SECONDS)
        self.notify("initialized", {})

    def request(self, method: str, params: dict[str, Any], *, timeout_seconds: float) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        message = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        self._send(message, kind="request", method=method)
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            response = self._responses.pop(request_id, None)
            if response is not None:
                payload = response["payload"]
                if "error" in payload:
                    raise RuntimeError(json.dumps(payload["error"], sort_keys=True))
                result = payload.get("result")
                if isinstance(result, dict):
                    return result
                return {"result": result}
            self._pump(timeout_seconds=max(0.1, deadline - time.monotonic()))
        raise TimeoutError(f"timed out waiting for App Server response to {method}")

    def notify(self, method: str, params: dict[str, Any]) -> None:
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        self._send(message, kind="notification", method=method)

    def wait_for_turn_completed(self, *, timeout_seconds: float) -> dict[str, Any]:
        observed = len(self._turn_completed_entries)
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if len(self._turn_completed_entries) > observed:
                return self._turn_completed_entries[-1]
            self._pump(timeout_seconds=max(0.1, deadline - time.monotonic()))
        raise TimeoutError("timed out waiting for App Server turn completion")

    def close(self) -> None:
        try:
            self._process.terminate()
            self._process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=5.0)
        self._stdout_thread.join(timeout=1.0)
        self._stderr_thread.join(timeout=1.0)
        write_text(self._stderr_path, self.stderr_text)

    def _send(self, payload: dict[str, Any], *, kind: str, method: str | None) -> None:
        sanitized_payload = _sanitize_payload(payload)
        self._timeline.append(
            {
                "timestamp": now_utc_iso(),
                "direction": "send",
                "kind": kind,
                "method": method,
                "payload": sanitized_payload,
            }
        )
        self._stdin.write(json.dumps(payload) + "\n")
        self._stdin.flush()

    def _read_stdout(self) -> None:
        for raw_line in self._stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                self._queue.put(
                    {
                        "timestamp": now_utc_iso(),
                        "kind": "raw",
                        "payload": {"raw": sanitize_text(line)},
                    }
                )
                continue
            self._queue.put(
                {
                    "timestamp": now_utc_iso(),
                    "kind": "json",
                    "payload": payload,
                }
            )

    def _read_stderr(self) -> None:
        for raw_line in self._stderr:
            line = sanitize_text(raw_line.rstrip("\n"))
            if line:
                self._stderr_lines.append(line)

    def _pump(self, *, timeout_seconds: float) -> None:
        try:
            envelope = self._queue.get(timeout=timeout_seconds)
        except queue.Empty:
            if self._process.poll() is not None:
                raise RuntimeError("codex app-server exited before the expected lifecycle event")
            return

        timestamp = envelope["timestamp"]
        if envelope["kind"] == "raw":
            self._timeline.append(
                {
                    "timestamp": timestamp,
                    "direction": "receive",
                    "kind": "raw",
                    "payload": envelope["payload"],
                }
            )
            return

        payload = envelope["payload"]
        method = payload.get("method")
        if "id" in payload and ("result" in payload or "error" in payload):
            self._timeline.append(
                {
                    "timestamp": timestamp,
                    "direction": "receive",
                    "kind": "response",
                    "method": method,
                    "id": payload["id"],
                    "payload": _sanitize_payload(payload),
                }
            )
            self._responses[int(payload["id"])] = {
                "timestamp": timestamp,
                "payload": payload,
            }
            return

        if isinstance(method, str) and "id" in payload:
            sanitized = _sanitize_payload(payload)
            self._timeline.append(
                {
                    "timestamp": timestamp,
                    "direction": "receive",
                    "kind": "request",
                    "method": method,
                    "id": payload["id"],
                    "payload": sanitized,
                }
            )
            error = {
                "jsonrpc": "2.0",
                "id": payload["id"],
                "error": {
                    "code": -32000,
                    "message": f"unsupported live-validation App Server request: {method}",
                },
            }
            self._send(error, kind="response", method=method)
            return

        sanitized = _sanitize_payload(payload)
        entry = {
            "timestamp": timestamp,
            "direction": "receive",
            "kind": "notification",
            "method": method,
            "payload": sanitized,
        }
        self._timeline.append(entry)
        if method == "turn/completed":
            self._turn_completed_entries.append(entry)


def _run_single_turn_scenario(
    *,
    root: Path,
    auth_mode: str,
    scenario_id: str,
    repeat_index: int,
    prompt_file: str,
    run_test: bool,
) -> dict[str, Any]:
    preferred_model = MODEL_MATRIX["openai"]["operator"].preferred
    project_root = prepare_harness_workspace(
        provider="openai",
        lane="operator",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    prompt = read_prompt_template(prompt_file)
    run_state, failure_class, model = _run_single_turn_attempts(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        preferred_model=preferred_model,
        scenario_id=scenario_id,
    )
    return _materialize_run(
        root=root,
        project_root=project_root,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        auth_mode=auth_mode,
        model=model,
        run_state=run_state,
        failure_class=failure_class,
        run_test=run_test,
    )


def _run_restart_continuity(*, root: Path, auth_mode: str, repeat_index: int) -> dict[str, Any]:
    preferred_model = MODEL_MATRIX["openai"]["operator"].preferred
    project_root = prepare_harness_workspace(
        provider="openai",
        lane="operator",
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
    )
    first_prompt = read_prompt_template("restart_continuity_turn1_operator.md")
    second_prompt = read_prompt_template("restart_continuity_turn2_operator.md")

    first_state, first_failure, model = _run_single_turn_attempts(
        project_root=project_root,
        prompt=first_prompt,
        auth_mode=auth_mode,
        preferred_model=preferred_model,
        scenario_id="restart_continuity_turn_1",
        ephemeral=False,
    )
    if first_failure is not None:
        return _materialize_run(
            root=root,
            project_root=project_root,
            scenario_id="restart_continuity",
            repeat_index=repeat_index,
            auth_mode=auth_mode,
            model=model,
            run_state=first_state,
            failure_class=first_failure,
            run_test=False,
            notes="Continuity stopped at the first App Server turn.",
            continuity_diagnostics=_continuity_diagnostics(
                thread_ephemeral=False,
                failure_class=first_failure,
            ),
        )

    thread_id = _extract_thread_id(first_state["thread_read"])
    second_state, second_failure = _run_resumed_turn(
        project_root=project_root,
        prompt=second_prompt,
        auth_mode=auth_mode,
        model=model,
        thread_id=thread_id,
    )
    combined_state = {
        "started_at": first_state["started_at"],
        "ended_at": second_state["ended_at"],
        "timeline": first_state["timeline"] + second_state["timeline"],
        "stderr_text": "\n".join(
            text for text in (first_state["stderr_text"], second_state["stderr_text"]) if text
        ),
        "thread_read": second_state["thread_read"],
        "thread_id": thread_id,
        "lifecycle_summary": summarize_app_server_timeline(
            first_state["timeline"] + second_state["timeline"],
            thread_read=second_state["thread_read"],
        ),
    }
    return _materialize_run(
        root=root,
        project_root=project_root,
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
        auth_mode=auth_mode,
        model=model,
        run_state=combined_state,
        failure_class=second_failure,
        run_test=True,
        continuity_diagnostics=_continuity_diagnostics(
            thread_ephemeral=False,
            failure_class=second_failure,
        ),
    )


def _run_single_turn_attempts(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    preferred_model: str,
    scenario_id: str,
    ephemeral: bool = True,
    env: dict[str, str] | None = None,
    stderr_path: Path | None = None,
) -> tuple[dict[str, Any], str | None, str]:
    first_state, first_failure = _run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=preferred_model,
        scenario_id=scenario_id,
        ephemeral=ephemeral,
        env=env,
        stderr_path=stderr_path,
    )
    chosen_model = choose_model("openai", "operator", first_failure=first_failure)
    if chosen_model == preferred_model:
        return first_state, first_failure, preferred_model
    fallback_state, fallback_failure = _run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=chosen_model,
        scenario_id=scenario_id,
        ephemeral=ephemeral,
        env=env,
        stderr_path=stderr_path,
    )
    return fallback_state, fallback_failure, chosen_model


def _run_single_turn(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    model: str,
    scenario_id: str,
    ephemeral: bool,
    env: dict[str, str] | None = None,
    stderr_path: Path | None = None,
) -> tuple[dict[str, Any], str | None]:
    started_at = now_utc_iso()
    client = _AppServerClient(
        cwd=project_root,
        stderr_path=(
            provider_root("openai", "operator", "app_server")
            / f"{scenario_id}.live.stderr.log"
            if stderr_path is None
            else stderr_path
        ),
        env=env,
    )
    try:
        if auth_mode != "codex_cli":
            state = {
                "started_at": started_at,
                "ended_at": now_utc_iso(),
                "timeline": [],
                "stderr_text": f"openai operator auth mode `{auth_mode}` is not supported by the App Server harness.",
                "thread_read": {},
                "thread_id": None,
                "lifecycle_summary": {
                    "thread_id": None,
                    "lifecycle_event_count": 0,
                    "lifecycle_event_labels": [],
                    "item_lifecycle_counts": {},
                    "server_request_methods": [],
                    "result_text": None,
                },
            }
            return state, "operator_surface_missing"

        client.initialize()
        start_result = client.request(
            "thread/start",
            {
                "cwd": str(project_root),
                "model": model,
                "approvalPolicy": "never",
                "sandbox": "workspace-write",
                "ephemeral": ephemeral,
            },
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        thread_id = _extract_thread_id(start_result)
        client.request(
            "turn/start",
            {
                "threadId": thread_id,
                "input": _TEXT_INPUT(prompt),
            },
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        client.wait_for_turn_completed(timeout_seconds=_TURN_TIMEOUT_SECONDS)
        thread_read_params: dict[str, Any] = {"threadId": thread_id}
        if not ephemeral:
            thread_read_params["includeTurns"] = True
        thread_read = client.request(
            "thread/read",
            thread_read_params,
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": client.stderr_text,
            "thread_read": thread_read,
            "thread_id": thread_id,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read=thread_read),
        }
        return state, _classify_state_failure(state)
    except TimeoutError:
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": client.stderr_text,
            "thread_read": {},
            "thread_id": None,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read={}),
        }
        return state, "operator_timeout"
    except RuntimeError as exc:
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": "\n".join(text for text in (client.stderr_text, str(exc)) if text),
            "thread_read": {},
            "thread_id": None,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read={}),
        }
        return state, _classify_state_failure(state)
    finally:
        client.close()


def _run_resumed_turn(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    model: str,
    thread_id: str | None,
    env: dict[str, str] | None = None,
    stderr_path: Path | None = None,
) -> tuple[dict[str, Any], str | None]:
    started_at = now_utc_iso()
    client = _AppServerClient(
        cwd=project_root,
        stderr_path=(
            provider_root("openai", "operator", "app_server")
            / "restart_continuity.resume.live.stderr.log"
            if stderr_path is None
            else stderr_path
        ),
        env=env,
    )
    try:
        if auth_mode != "codex_cli":
            state = {
                "started_at": started_at,
                "ended_at": now_utc_iso(),
                "timeline": [],
                "stderr_text": f"openai operator auth mode `{auth_mode}` is not supported by the App Server harness.",
                "thread_read": {},
                "thread_id": thread_id,
                "lifecycle_summary": {
                    "thread_id": thread_id,
                    "lifecycle_event_count": 0,
                    "lifecycle_event_labels": [],
                    "item_lifecycle_counts": {},
                    "server_request_methods": [],
                    "result_text": None,
                },
            }
            return state, "operator_surface_missing"
        if not thread_id:
            state = {
                "started_at": started_at,
                "ended_at": now_utc_iso(),
                "timeline": [],
                "stderr_text": "thread resume requires a prior thread id",
                "thread_read": {},
                "thread_id": None,
                "lifecycle_summary": {
                    "thread_id": None,
                    "lifecycle_event_count": 0,
                    "lifecycle_event_labels": [],
                    "item_lifecycle_counts": {},
                    "server_request_methods": [],
                    "result_text": None,
                },
            }
            return state, "operator_surface_missing"

        client.initialize()
        client.request(
            "thread/resume",
            {
                "threadId": thread_id,
                "cwd": str(project_root),
                "model": model,
                "approvalPolicy": "never",
                "sandbox": "workspace-write",
            },
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        client.request(
            "turn/start",
            {
                "threadId": thread_id,
                "input": _TEXT_INPUT(prompt),
            },
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        client.wait_for_turn_completed(timeout_seconds=_TURN_TIMEOUT_SECONDS)
        thread_read = client.request(
            "thread/read",
            {
                "threadId": thread_id,
                "includeTurns": True,
            },
            timeout_seconds=_THREAD_TIMEOUT_SECONDS,
        )
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": client.stderr_text,
            "thread_read": thread_read,
            "thread_id": thread_id,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read=thread_read),
        }
        return state, _classify_state_failure(state)
    except TimeoutError:
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": client.stderr_text,
            "thread_read": {},
            "thread_id": thread_id,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read={}),
        }
        return state, "operator_timeout"
    except RuntimeError as exc:
        state = {
            "started_at": started_at,
            "ended_at": now_utc_iso(),
            "timeline": client.timeline,
            "stderr_text": "\n".join(text for text in (client.stderr_text, str(exc)) if text),
            "thread_read": {},
            "thread_id": thread_id,
            "lifecycle_summary": summarize_app_server_timeline(client.timeline, thread_read={}),
        }
        failure_class = _classify_state_failure(state) or "operator_surface_missing"
        return state, failure_class
    finally:
        client.close()


def _materialize_run(
    *,
    root: Path,
    project_root: Path,
    scenario_id: str,
    repeat_index: int,
    auth_mode: str,
    model: str,
    run_state: dict[str, Any],
    failure_class: str | None,
    run_test: bool,
    notes: str | None = None,
    route_diagnostics: dict[str, Any] | None = None,
    continuity_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stem = f"{scenario_id}__run_{repeat_index:03d}"
    timeline_path = root / f"{stem}.timeline.jsonl"
    thread_read_path = root / f"{stem}.thread.json"
    stderr_path = root / f"{stem}.stderr.log"
    artifact_path = root / f"{stem}.json"

    _write_timeline(timeline_path, run_state["timeline"])
    write_json(thread_read_path, _sanitize_payload(run_state["thread_read"]))
    write_text(stderr_path, run_state["stderr_text"])

    test_result = run_target_test(project_root) if run_test else None
    modified_files = collect_modified_files(project_root)
    lifecycle_summary = run_state["lifecycle_summary"]
    result_text = lifecycle_summary.get("result_text")
    success = failure_class is None and (not run_test or (test_result is not None and test_result["exit_code"] == 0))
    truth_gap_kind = None
    if scenario_id == "truth_gap":
        test_exit_code = test_result["exit_code"] if test_result is not None else 1
        truth_gap_kind = classify_truth_gap(
            result_text,
            test_passed=test_exit_code == 0,
            modified_files=modified_files,
        )
        success = truth_gap_kind == "truthful_incomplete" and failure_class is None

    payload = {
        "provider": "openai",
        "lane": "operator",
        "surface": "app_server",
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "auth_mode": auth_mode,
        "model": model,
        "success": success,
        "failure_class": failure_class,
        "thread_id": lifecycle_summary.get("thread_id"),
        "lifecycle_event_count": lifecycle_summary.get("lifecycle_event_count"),
        "lifecycle_event_labels": lifecycle_summary.get("lifecycle_event_labels"),
        "item_lifecycle_counts": lifecycle_summary.get("item_lifecycle_counts"),
        "server_request_methods": lifecycle_summary.get("server_request_methods"),
        "result_text": result_text,
        "modified_files": modified_files,
        "test_exit_code": test_result["exit_code"] if test_result is not None else None,
        "test_stdout": test_result["stdout"].strip() if test_result is not None else None,
        "test_stderr": test_result["stderr"].strip() if test_result is not None else None,
        "workspace_label": str(project_root.relative_to(project_root.parents[4])),
        "timeline_path": str(timeline_path.relative_to(root.parents[4])),
        "thread_read_path": str(thread_read_path.relative_to(root.parents[4])),
        "stderr_path": str(stderr_path.relative_to(root.parents[4])),
        "truth_gap_kind": truth_gap_kind,
        "started_at": run_state["started_at"],
        "ended_at": run_state["ended_at"],
        "notes": notes,
        "extra_read_pass_attempted": False,
        "extra_read_pass_completed": False,
        "extra_read_pass_mode": None,
        "extra_read_pass_failure_class": None,
        "token_usage_visible": False,
        "input_tokens": None,
        "output_tokens": None,
        "cache_tokens": None,
        **_provider_limit_fields(
            failure_class=failure_class,
            result_text=result_text,
        ),
    }
    if route_diagnostics:
        payload.update(route_diagnostics)
    if continuity_diagnostics:
        payload.update(continuity_diagnostics)
    write_json(artifact_path, payload)
    payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
    return payload


def _classify_state_failure(run_state: dict[str, Any]) -> str | None:
    lifecycle_summary = run_state["lifecycle_summary"]
    request_blocker = classify_app_server_request_blocker(
        lifecycle_summary.get("server_request_methods", [])
    )
    if request_blocker is not None:
        return request_blocker
    if _timeline_has_error_response(run_state.get("timeline", [])):
        return "runtime_error"
    text = "\n".join(
        [
            run_state.get("stderr_text", ""),
            json.dumps(run_state.get("thread_read", {}), sort_keys=True),
        ]
    )
    return classify_failure(text)


def _provider_limit_fields(
    *,
    failure_class: str | None,
    result_text: str | None,
) -> dict[str, Any]:
    candidates: list[str] = []
    if failure_class:
        candidates.append(failure_class)
    if isinstance(result_text, str):
        classified = classify_failure(result_text)
        if classified:
            candidates.append(classified)
    limit_kind = next(
        (
            candidate
            for candidate in candidates
            if candidate in {"quota_exhausted", "capacity_exhausted", "rate_limited"}
        ),
        None,
    )
    return {
        "provider_limit_interference": limit_kind is not None,
        "provider_limit_kind": limit_kind,
        "comparison_contaminated": limit_kind is not None,
    }


def _continuity_diagnostics(
    *,
    thread_ephemeral: bool,
    failure_class: str | None,
) -> dict[str, Any]:
    return {
        "continuity_transport": "thread_resume",
        "thread_ephemeral": thread_ephemeral,
        "continuity_failure_kind": (
            failure_class if failure_class == "continuity_rollout_missing" else None
        ),
    }


def _write_timeline(path: Path, timeline: list[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(entry, sort_keys=True) for entry in timeline)
    write_text(path, payload + ("\n" if payload else ""))


def _sanitize_payload(payload: Any) -> Any:
    return json.loads(sanitize_text(json.dumps(payload)))


def _extract_item_type(payload: Any) -> str | None:
    if isinstance(payload, dict):
        item = payload.get("item")
        if isinstance(item, dict):
            item_type = item.get("type")
            if isinstance(item_type, str) and item_type.strip():
                return item_type.strip()
        for value in payload.values():
            extracted = _extract_item_type(value)
            if extracted is not None:
                return extracted
    elif isinstance(payload, list):
        for value in payload:
            extracted = _extract_item_type(value)
            if extracted is not None:
                return extracted
    return None


def _extract_agent_delta(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("delta", "text"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        for value in payload.values():
            extracted = _extract_agent_delta(value)
            if extracted is not None:
                return extracted
    elif isinstance(payload, list):
        for value in payload:
            extracted = _extract_agent_delta(value)
            if extracted is not None:
                return extracted
    return None


def _extract_thread_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        thread = payload.get("thread")
        if isinstance(thread, dict):
            extracted = _extract_thread_id(thread)
            if extracted is not None:
                return extracted
        for key in ("threadId", "thread_id"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        value = payload.get("id")
        if (
            isinstance(value, str)
            and value.strip()
            and any(key in payload for key in ("createdAt", "updatedAt", "status", "cwd"))
        ):
            return value
        for value in payload.values():
            extracted = _extract_thread_id(value)
            if extracted is not None:
                return extracted
    elif isinstance(payload, list):
        for value in payload:
            extracted = _extract_thread_id(value)
            if extracted is not None:
                return extracted
    return None


def _extract_agent_text(payload: Any) -> str | None:
    fragments: list[str] = []
    _collect_agent_text(payload, fragments)
    text = "".join(fragments).strip()
    return text or None


def _timeline_has_error_response(timeline: list[dict[str, Any]]) -> bool:
    for event in timeline:
        if event.get("direction") != "receive" or event.get("kind") != "response":
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
            return True
    return False


def _extract_completed_agent_text(payload: Any) -> str | None:
    if isinstance(payload, dict):
        item = payload.get("item")
        if isinstance(item, dict):
            item_type = item.get("type")
            if isinstance(item_type, str) and item_type in {"agentMessage", "agent_message"}:
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()
        params = payload.get("params")
        if isinstance(params, dict):
            completed = _extract_completed_agent_text(params)
            if completed:
                return completed
        msg = payload.get("msg")
        if isinstance(msg, dict):
            last_message = msg.get("last_agent_message") or msg.get("message")
            if isinstance(last_message, str) and last_message.strip():
                return last_message.strip()
        for value in payload.values():
            completed = _extract_completed_agent_text(value)
            if completed:
                return completed
    elif isinstance(payload, list):
        for value in payload:
            completed = _extract_completed_agent_text(value)
            if completed:
                return completed
    return None


def _collect_agent_text(payload: Any, fragments: list[str]) -> None:
    if isinstance(payload, dict):
        item_type = payload.get("type")
        if isinstance(item_type, str) and item_type in {"agentMessage", "agent_message"}:
            for key in ("text", "delta"):
                value = payload.get(key)
                if isinstance(value, str):
                    fragments.append(value)
        for value in payload.values():
            _collect_agent_text(value, fragments)
    elif isinstance(payload, list):
        for value in payload:
            _collect_agent_text(value, fragments)


if __name__ == "__main__":
    raise SystemExit(main())
