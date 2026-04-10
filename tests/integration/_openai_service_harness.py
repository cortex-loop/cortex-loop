"""Test harness helpers for the loopback OpenAI service shell."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_RECORD_KEYS = (
    "event_index",
    "raw_host_event_name",
    "native_event_name",
    "dispatch_lane",
    "decision",
    "warnings",
    "journal",
    "commitment_result_kind",
)


@dataclass(slots=True)
class OpenAIServiceHarness:
    port: int
    process: subprocess.Popen[str]

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=2.0) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def terminate(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

    def stderr_text(self) -> str:
        if self.process.stderr is None or self.process.poll() is None:
            return ""
        return self.process.stderr.read()


@contextmanager
def run_openai_service(
    *args: str,
    env: Mapping[str, str] | None = None,
) -> Iterator[OpenAIServiceHarness]:
    port = _unused_tcp_port()
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    process = subprocess.Popen(
        [sys.executable, "-m", "cortex.hosts.openai.service", "--port", str(port), *args],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=process_env,
    )
    harness = OpenAIServiceHarness(port=port, process=process)
    try:
        _wait_for_service(harness)
        yield harness
    finally:
        harness.terminate()
        stderr_text = harness.stderr_text()
        if process.returncode not in (None, 0, -15):
            raise AssertionError(
                "OpenAI service subprocess exited unexpectedly.\n"
                f"returncode={process.returncode}\n"
                f"stderr={stderr_text}"
            )


def _wait_for_service(harness: OpenAIServiceHarness) -> None:
    deadline = time.time() + 10.0
    last_error: Exception | None = None
    while time.time() < deadline:
        if harness.process.poll() is not None:
            raise AssertionError(
                "OpenAI service subprocess exited before health check succeeded.\n"
                f"stderr={harness.stderr_text()}"
            )
        try:
            status, payload = harness.request("GET", "/health")
        except Exception as exc:  # pragma: no cover - retry loop
            last_error = exc
            time.sleep(0.05)
            continue
        if status == 200 and payload.get("status") == "ok":
            return
        time.sleep(0.05)
    raise AssertionError(f"OpenAI service failed to become healthy: {last_error}")


def _unused_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
