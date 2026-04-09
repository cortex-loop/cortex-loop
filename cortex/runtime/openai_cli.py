"""Developer-facing local CLI for the OpenAI documented host-event runtime shell."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

from cortex.drivers.openai_host import is_raw_openai_host_event_name

from .openai import OpenAIRuntimeSession, OpenAIRuntimeStepResult, run_openai_runtime_step
from .openai_session_io import (
    read_openai_runtime_session_artifact,
    write_openai_runtime_session_artifact,
)

_OUTPUT_KEYS = (
    "event_index",
    "raw_host_event_name",
    "native_event_name",
    "dispatch_lane",
    "decision",
    "warnings",
    "journal",
    "commitment_result_kind",
)


def build_openai_cli_record(step_result: OpenAIRuntimeStepResult) -> dict[str, Any]:
    if not isinstance(step_result, OpenAIRuntimeStepResult):
        actual_type = type(step_result).__name__
        raise TypeError(
            "build_openai_cli_record.step_result must be OpenAIRuntimeStepResult, "
            f"got {actual_type}."
        )
    payload_metadata = {
        field.key: field.value for field in step_result.bound_event.observation.event.payload_metadata
    }
    return {
        "event_index": step_result.event_index,
        "raw_host_event_name": payload_metadata.get("raw_host_event_name"),
        "native_event_name": step_result.bound_event.observation.event.native_event_name,
        "dispatch_lane": step_result.dispatch_decision.lane.value,
        "decision": step_result.product_decision.decision,
        "warnings": list(step_result.warnings),
        "journal": step_result.journal,
        "commitment_result_kind": step_result.commitment_result_kind,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m cortex.runtime.openai_cli",
        description="Process raw OpenAI-host runtime events from JSONL input.",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Read JSONL events from a file instead of stdin.",
    )
    parser.add_argument(
        "--load-session",
        type=Path,
        help="Load the initial OpenAI runtime session from an artifact file.",
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        help="Persist the final OpenAI runtime session to an artifact file.",
    )
    args = parser.parse_args(argv)

    try:
        lines = _input_lines(args.event_file)
        initial_session = (
            read_openai_runtime_session_artifact(args.load_session)
            if args.load_session is not None
            else OpenAIRuntimeSession()
        )
        records, final_session = _run_openai_cli_lines_with_session(lines, initial_session)
        if args.save_session is not None:
            write_openai_runtime_session_artifact(args.save_session, final_session)
        for record in records:
            print(json.dumps(record))
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"openai_cli error: {exc}", file=sys.stderr)
        return 1
    return 0


def _run_openai_cli_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    records, _ = _run_openai_cli_lines_with_session(lines)
    return records


def _run_openai_cli_lines_with_session(
    lines: Iterable[str],
    session: OpenAIRuntimeSession | None = None,
) -> tuple[list[dict[str, Any]], OpenAIRuntimeSession]:
    records: list[dict[str, Any]] = []
    current_session = _coerce_cli_session(session)

    for event_name, payload in _iter_openai_cli_events(lines):
        step_result = run_openai_runtime_step(event_name, payload, current_session)
        record = build_openai_cli_record(step_result)
        if tuple(record) != _OUTPUT_KEYS:
            raise ValueError("OpenAI CLI record must preserve the locked output field order.")
        records.append(record)
        current_session = step_result.session

    return records, current_session


def _input_lines(event_file: Path | None) -> Iterable[str]:
    if event_file is None:
        return sys.stdin
    with event_file.open("r", encoding="utf-8") as handle:
        return tuple(handle.readlines())


def _iter_openai_cli_events(lines: Iterable[str]) -> Iterator[tuple[str, dict[str, Any]]]:
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON input") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"line {line_number}: expected a JSON object.")

        event_name = payload.get("event_name")
        event_payload = payload.get("payload")
        if not isinstance(event_name, str) or not event_name.strip():
            raise ValueError(f"line {line_number}: event_name must be a non-empty string.")
        if not is_raw_openai_host_event_name(event_name):
            raise ValueError(
                f"line {line_number}: event_name must be a raw OpenAI host event name, "
                "not a canonical Cortex event name."
            )
        if not isinstance(event_payload, dict):
            raise ValueError(f"line {line_number}: payload must be an object.")
        yield event_name, event_payload


def _coerce_cli_session(session: OpenAIRuntimeSession | None) -> OpenAIRuntimeSession:
    if session is None:
        return OpenAIRuntimeSession()
    if not isinstance(session, OpenAIRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "openai_cli initial session must be OpenAIRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


if __name__ == "__main__":
    raise SystemExit(main())
