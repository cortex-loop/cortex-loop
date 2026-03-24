"""Developer-facing local CLI for the accepted reference-host runtime shell."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

from .reference import ReferenceRuntimeStepResult, ReferenceRuntimeSession, run_reference_runtime_step

_OUTPUT_KEYS = (
    "event_index",
    "native_event_name",
    "dispatch_lane",
    "selected_family",
    "brake_state",
    "warnings",
    "session_summary",
    "commitment_result_kind",
)


def build_reference_cli_record(step_result: ReferenceRuntimeStepResult) -> dict[str, Any]:
    if not isinstance(step_result, ReferenceRuntimeStepResult):
        actual_type = type(step_result).__name__
        raise TypeError(
            "build_reference_cli_record.step_result must be ReferenceRuntimeStepResult, "
            f"got {actual_type}."
        )

    return {
        "event_index": step_result.event_index,
        "native_event_name": step_result.bound_event.observation.event.native_event_name,
        "dispatch_lane": step_result.dispatch_decision.lane.value,
        "selected_family": step_result.selected_family.value,
        "brake_state": step_result.brake_state.value,
        "warnings": list(step_result.warnings),
        "session_summary": step_result.session_summary,
        "commitment_result_kind": step_result.commitment_result_kind,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m cortex.runtime.reference_cli",
        description="Process reference-host runtime events from JSONL input.",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Read JSONL events from a file instead of stdin.",
    )
    args = parser.parse_args(argv)

    try:
        lines = _input_lines(args.event_file)
        for record in _run_reference_cli_lines(lines):
            print(json.dumps(record, sort_keys=True))
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"reference_cli error: {exc}", file=sys.stderr)
        return 1

    return 0


def _run_reference_cli_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    session = ReferenceRuntimeSession()

    for event_name, payload in _iter_reference_cli_events(lines):
        step_result = run_reference_runtime_step(event_name, payload, session)
        record = build_reference_cli_record(step_result)
        if tuple(record) != _OUTPUT_KEYS:
            raise ValueError("Reference CLI record must preserve the locked output field order.")
        records.append(record)
        session = step_result.session

    return records


def _input_lines(event_file: Path | None) -> Iterable[str]:
    if event_file is None:
        return sys.stdin
    with event_file.open("r", encoding="utf-8") as handle:
        return tuple(handle.readlines())


def _iter_reference_cli_events(lines: Iterable[str]) -> Iterator[tuple[str, dict[str, Any]]]:
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
        if not isinstance(event_payload, dict):
            raise ValueError(f"line {line_number}: payload must be an object.")

        yield event_name, event_payload


if __name__ == "__main__":
    raise SystemExit(main())
