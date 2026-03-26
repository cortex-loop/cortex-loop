"""Loopback-only HTTP service shell for raw OpenAI transcript ingress."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .openai import OpenAIRuntimeSession, run_openai_runtime_step
from .openai_cli import build_openai_cli_record
from .openai_ingress import parse_openai_host_event_envelope
from .openai_session_io import (
    build_openai_runtime_session_artifact,
    parse_openai_runtime_session_artifact,
    read_openai_runtime_session_artifact,
)

_LOOPBACK_HOST = "127.0.0.1"
_DEFAULT_PORT = 8765
_HEALTH_PATH = "/health"
_EVENTS_PATH = "/v1/events"
_EXPORT_PATH = "/v1/session/export"
_IMPORT_PATH = "/v1/session/import"
_KNOWN_PATHS = frozenset(
    {
        _HEALTH_PATH,
        _EVENTS_PATH,
        _EXPORT_PATH,
        _IMPORT_PATH,
    }
)


@dataclass(slots=True)
class OpenAIServiceState:
    session: OpenAIRuntimeSession = field(default_factory=OpenAIRuntimeSession)
    session_loaded: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.session, OpenAIRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "OpenAIServiceState.session must be OpenAIRuntimeSession, "
                f"got {actual_type}."
            )
        if not isinstance(self.session_loaded, bool):
            actual_type = type(self.session_loaded).__name__
            raise TypeError(
                "OpenAIServiceState.session_loaded must be bool, "
                f"got {actual_type}."
            )

    def replace_session(
        self,
        session: OpenAIRuntimeSession,
        *,
        session_loaded: bool = True,
    ) -> None:
        if not isinstance(session, OpenAIRuntimeSession):
            actual_type = type(session).__name__
            raise TypeError(
                "OpenAIServiceState.replace_session.session must be OpenAIRuntimeSession, "
                f"got {actual_type}."
            )
        if not isinstance(session_loaded, bool):
            actual_type = type(session_loaded).__name__
            raise TypeError(
                "OpenAIServiceState.replace_session.session_loaded must be bool, "
                f"got {actual_type}."
            )
        self.session = session
        self.session_loaded = session_loaded


def handle_openai_service_request(
    method: str,
    path: str,
    state: OpenAIServiceState,
    body: bytes | None = None,
) -> tuple[int, dict[str, Any]]:
    if not isinstance(method, str) or not method.strip():
        raise ValueError("OpenAI service request method must be a non-empty string.")
    if not isinstance(path, str) or not path.strip():
        raise ValueError("OpenAI service request path must be a non-empty string.")
    if not isinstance(state, OpenAIServiceState):
        actual_type = type(state).__name__
        raise TypeError(
            "OpenAI service request state must be OpenAIServiceState, "
            f"got {actual_type}."
        )

    normalized_method = method.upper()
    normalized_path = urlsplit(path).path

    try:
        if normalized_path == _HEALTH_PATH:
            if normalized_method != "GET":
                return _error_response(405, f"{normalized_method} is not allowed for {_HEALTH_PATH}.")
            return (
                200,
                {
                    "status": "ok",
                    "runtime": "openai-service",
                    "session_loaded": state.session_loaded,
                },
            )

        if normalized_path == _EVENTS_PATH:
            if normalized_method != "POST":
                return _error_response(405, f"{normalized_method} is not allowed for {_EVENTS_PATH}.")
            record = _parse_json_object(body, label="OpenAI service event body")
            return 200, _handle_openai_service_event(record, state)

        if normalized_path == _EXPORT_PATH:
            if normalized_method != "GET":
                return _error_response(405, f"{normalized_method} is not allowed for {_EXPORT_PATH}.")
            return 200, export_openai_service_session(state)

        if normalized_path == _IMPORT_PATH:
            if normalized_method != "POST":
                return _error_response(405, f"{normalized_method} is not allowed for {_IMPORT_PATH}.")
            payload = _parse_json_object(body, label="OpenAI service import body")
            return 200, import_openai_service_session(payload, state)

        return _error_response(404, f"Unknown path: {normalized_path}")
    except (TypeError, ValueError) as exc:
        return _error_response(400, str(exc))


def export_openai_service_session(state: OpenAIServiceState) -> dict[str, Any]:
    if not isinstance(state, OpenAIServiceState):
        actual_type = type(state).__name__
        raise TypeError(
            "export_openai_service_session.state must be OpenAIServiceState, "
            f"got {actual_type}."
        )
    return build_openai_runtime_session_artifact(state.session).as_payload()


def import_openai_service_session(
    payload: Mapping[str, Any],
    state: OpenAIServiceState,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "import_openai_service_session.payload must be a mapping, "
            f"got {actual_type}."
        )
    if not isinstance(state, OpenAIServiceState):
        actual_type = type(state).__name__
        raise TypeError(
            "import_openai_service_session.state must be OpenAIServiceState, "
            f"got {actual_type}."
        )
    session = parse_openai_runtime_session_artifact(payload)
    state.replace_session(session, session_loaded=True)
    return export_openai_service_session(state)


def build_openai_service_server(
    port: int = _DEFAULT_PORT,
    *,
    state: OpenAIServiceState | None = None,
) -> HTTPServer:
    resolved_state = state if state is not None else OpenAIServiceState()
    if not isinstance(resolved_state, OpenAIServiceState):
        actual_type = type(resolved_state).__name__
        raise TypeError(
            "build_openai_service_server.state must be OpenAIServiceState | None, "
            f"got {actual_type}."
        )
    if isinstance(port, bool) or not isinstance(port, int):
        actual_type = type(port).__name__
        raise TypeError(
            "build_openai_service_server.port must be an integer, "
            f"got {actual_type}."
        )
    if port < 0 or port > 65535:
        raise ValueError("build_openai_service_server.port must be between 0 and 65535.")
    return _OpenAIServiceHTTPServer((_LOOPBACK_HOST, port), resolved_state)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m cortex.runtime.openai_service",
        description="Run a loopback-only OpenAI transcript service shell.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        help=f"Loopback TCP port to bind. Defaults to {_DEFAULT_PORT}.",
    )
    parser.add_argument(
        "--load-session",
        type=Path,
        help="Load the initial OpenAI runtime session from an artifact file.",
    )
    args = parser.parse_args(argv)

    try:
        initial_session = (
            read_openai_runtime_session_artifact(args.load_session)
            if args.load_session is not None
            else OpenAIRuntimeSession()
        )
        state = OpenAIServiceState(
            session=initial_session,
            session_loaded=args.load_session is not None,
        )
        with build_openai_service_server(args.port, state=state) as server:
            print(
                f"openai_service listening on {_LOOPBACK_HOST}:{server.server_address[1]}",
                file=sys.stderr,
            )
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"openai_service error: {exc}", file=sys.stderr)
        return 1
    return 0


def _handle_openai_service_event(
    record: Mapping[str, Any],
    state: OpenAIServiceState,
) -> dict[str, Any]:
    envelope = parse_openai_host_event_envelope(record)
    step_result = run_openai_runtime_step(
        envelope.event_type,
        envelope.payload,
        state.session,
    )
    state.replace_session(step_result.session, session_loaded=True)
    return build_openai_cli_record(step_result)


def _parse_json_object(body: bytes | None, *, label: str) -> Mapping[str, Any]:
    if body is None or not body.strip():
        raise ValueError(f"{label} must be a JSON object.")
    try:
        payload = json.loads(body.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON.") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be valid JSON.") from exc
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must decode to a JSON object, got {actual_type}.")
    return payload


def _error_response(status_code: int, message: str) -> tuple[int, dict[str, str]]:
    return status_code, {"error": message}


class _OpenAIServiceHTTPServer(HTTPServer):
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        state: OpenAIServiceState,
    ) -> None:
        self.state = state
        super().__init__(server_address, _OpenAIServiceHandler)


class _OpenAIServiceHandler(BaseHTTPRequestHandler):
    server: _OpenAIServiceHTTPServer

    def do_GET(self) -> None:
        self._handle("GET")

    def do_POST(self) -> None:
        self._handle("POST")

    def do_DELETE(self) -> None:
        self._handle("DELETE")

    def do_HEAD(self) -> None:
        self._handle("HEAD")

    def do_OPTIONS(self) -> None:
        self._handle("OPTIONS")

    def do_PATCH(self) -> None:
        self._handle("PATCH")

    def do_PUT(self) -> None:
        self._handle("PUT")

    def _handle(self, method: str) -> None:
        body = None
        if method in {"POST", "PUT", "PATCH", "DELETE"}:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length) if content_length > 0 else b""
        status_code, payload = handle_openai_service_request(
            method,
            self.path,
            self.server.state,
            body,
        )
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(encoded)


__all__ = [
    "OpenAIServiceState",
    "build_openai_service_server",
    "export_openai_service_session",
    "handle_openai_service_request",
    "import_openai_service_session",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
