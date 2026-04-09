"""Developer-facing local CLI for raw Gemini transcript ingress."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

from .gemini import GeminiRuntimeSession, run_gemini_runtime_step
from .gemini_cli import build_gemini_cli_record
from .gemini_ingress import parse_gemini_host_event_envelope
from .gemini_session_io import (
    read_gemini_runtime_session_artifact,
    write_gemini_runtime_session_artifact,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m experimental.runtime.gemini_ingress_cli",
        description="Process raw Gemini transcript events from JSONL input.",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Read JSONL transcript records from a file instead of stdin.",
    )
    parser.add_argument(
        "--load-session",
        type=Path,
        help="Load the initial Gemini runtime session from an artifact file.",
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        help="Persist the final Gemini runtime session to an artifact file.",
    )
    args = parser.parse_args(argv)

    try:
        lines = _input_lines(args.event_file)
        initial_session = (
            read_gemini_runtime_session_artifact(args.load_session)
            if args.load_session is not None
            else GeminiRuntimeSession()
        )
        records, final_session = _run_gemini_ingress_cli_lines_with_session(
            lines,
            initial_session,
        )
        if args.save_session is not None:
            write_gemini_runtime_session_artifact(args.save_session, final_session)
        for record in records:
            print(json.dumps(record))
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"gemini_ingress_cli error: {exc}", file=sys.stderr)
        return 1
    return 0


def _run_gemini_ingress_cli_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    records, _ = _run_gemini_ingress_cli_lines_with_session(lines)
    return records


def _run_gemini_ingress_cli_lines_with_session(
    lines: Iterable[str],
    session: GeminiRuntimeSession | None = None,
) -> tuple[list[dict[str, Any]], GeminiRuntimeSession]:
    records: list[dict[str, Any]] = []
    current_session = _coerce_cli_session(session)

    for event_type, payload in _iter_gemini_ingress_events(lines):
        step_result = run_gemini_runtime_step(event_type, payload, current_session)
        records.append(build_gemini_cli_record(step_result))
        current_session = step_result.session

    return records, current_session


def _input_lines(event_file: Path | None) -> Iterable[str]:
    if event_file is None:
        return sys.stdin
    with event_file.open("r", encoding="utf-8") as handle:
        return tuple(handle.readlines())


def _iter_gemini_ingress_events(lines: Iterable[str]) -> Iterator[tuple[str, dict[str, Any]]]:
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON input") from exc
        envelope = parse_gemini_host_event_envelope(record)
        yield envelope.event_type, envelope.payload


def _coerce_cli_session(session: GeminiRuntimeSession | None) -> GeminiRuntimeSession:
    if session is None:
        return GeminiRuntimeSession()
    if not isinstance(session, GeminiRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "gemini_ingress_cli initial session must be GeminiRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


if __name__ == "__main__":
    raise SystemExit(main())
