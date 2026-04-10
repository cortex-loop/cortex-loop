"""Developer-facing local CLI for raw Claude transcript ingress."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

from .runtime import ClaudeRuntimeSession, run_claude_runtime_step
from .cli import build_claude_cli_record
from .ingress import parse_claude_host_event_envelope
from .session_io import (
    read_claude_runtime_session_artifact,
    write_claude_runtime_session_artifact,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m cortex.hosts.claude.ingress_cli",
        description="Process raw Claude transcript events from JSONL input.",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Read JSONL transcript records from a file instead of stdin.",
    )
    parser.add_argument(
        "--load-session",
        type=Path,
        help="Load the initial Claude runtime session from an artifact file.",
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        help="Persist the final Claude runtime session to an artifact file.",
    )
    args = parser.parse_args(argv)

    try:
        lines = _input_lines(args.event_file)
        initial_session = (
            read_claude_runtime_session_artifact(args.load_session)
            if args.load_session is not None
            else ClaudeRuntimeSession()
        )
        records, final_session = _run_claude_ingress_cli_lines_with_session(
            lines,
            initial_session,
        )
        if args.save_session is not None:
            write_claude_runtime_session_artifact(args.save_session, final_session)
        for record in records:
            print(json.dumps(record))
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"claude_ingress_cli error: {exc}", file=sys.stderr)
        return 1
    return 0


def _run_claude_ingress_cli_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    records, _ = _run_claude_ingress_cli_lines_with_session(lines)
    return records


def _run_claude_ingress_cli_lines_with_session(
    lines: Iterable[str],
    session: ClaudeRuntimeSession | None = None,
) -> tuple[list[dict[str, Any]], ClaudeRuntimeSession]:
    records: list[dict[str, Any]] = []
    current_session = _coerce_cli_session(session)

    for event_type, payload in _iter_claude_ingress_events(lines):
        step_result = run_claude_runtime_step(event_type, payload, current_session)
        records.append(build_claude_cli_record(step_result))
        current_session = step_result.session

    return records, current_session


def _input_lines(event_file: Path | None) -> Iterable[str]:
    if event_file is None:
        return sys.stdin
    with event_file.open("r", encoding="utf-8") as handle:
        return tuple(handle.readlines())


def _iter_claude_ingress_events(lines: Iterable[str]) -> Iterator[tuple[str, dict[str, Any]]]:
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON input") from exc
        envelope = parse_claude_host_event_envelope(record)
        yield envelope.event_type, envelope.payload


def _coerce_cli_session(session: ClaudeRuntimeSession | None) -> ClaudeRuntimeSession:
    if session is None:
        return ClaudeRuntimeSession()
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "claude_ingress_cli initial session must be ClaudeRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


if __name__ == "__main__":
    raise SystemExit(main())
