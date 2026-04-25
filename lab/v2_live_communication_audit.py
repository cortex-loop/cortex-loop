"""Live Claude/Codex audit for Cortex v2 model-visible communication."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from cortex.sre.guidance import (
    GUIDANCE_MARKER,
    build_guidance_context_from_session,
    prepend_guidance_to_prompt,
    v2_guidance_inventory_payload,
)
from lab.agent_loop_guard import (
    LOOP_GUARD_LATEST_PATH,
    LOOP_GUARD_ROOT,
    GateResult,
    read_gate_report,
)
from lab.live_validation_common import (
    MODEL_MATRIX,
    REPO_ROOT,
    classify_failure,
    extract_event_labels,
    extract_result_text,
    now_utc_iso,
    parse_json_records,
    relative_repo_path,
    run_command,
    write_json,
    write_text,
)
from lab.v2_subscription_cli_preflight import DEFAULT_PREFLIGHT_PATH


HostName = Literal["claude", "codex"]
CommandRunner = Callable[..., dict[str, Any]]

AUDIT_MARKER = "CORTEX_V2_LIVE_COMMUNICATION_AUDIT"
DEFAULT_AUDIT_PATH = LOOP_GUARD_ROOT / "v2_live_communication_audit.latest.json"
DEFAULT_AUDIT_RUN_ROOT = LOOP_GUARD_ROOT / "v2_live_communication_audit"
DEFAULT_TIMEOUT_SECONDS = 300.0

_HOST_SURFACE = {
    "claude": "claude-cli-live-communication-audit",
    "codex": "codex-cli-live-communication-audit",
}
_HOST_GATE = {
    "claude": "claude_live_watchlist_evidence",
    "codex": "codex_live_watchlist_evidence",
}
_GLOBAL_CONSTRAINTS = (
    "no_raw_aux_memory",
    "no_v3_successor_claim",
    "no_live_closure_without_evidence",
    "subscription_cli_no_api_spend",
    "shipping_conformance_distinction",
    "watchlist_not_product_perfection",
)


def run_v2_live_communication_audit(
    *,
    hosts: tuple[HostName, ...] = ("claude", "codex"),
    command_runner: CommandRunner | None = None,
    preflight_path: Path = DEFAULT_PREFLIGHT_PATH,
    audit_run_root: Path = DEFAULT_AUDIT_RUN_ROOT,
    run_id: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run the live communication audit and return the summary payload."""

    if not hosts:
        raise ValueError("hosts must contain at least one host.")
    for host in hosts:
        if host not in {"claude", "codex"}:
            raise ValueError(f"unsupported host: {host}")
    runner = command_runner or run_command
    run_id = run_id or _run_id()
    run_root = audit_run_root / run_id
    preflight = _read_preflight(preflight_path)
    host_results: dict[str, Any] = {}
    for host in hosts:
        host_results[host] = _run_host_audit(
            host,
            command_runner=runner,
            preflight=preflight,
            run_root=run_root,
            timeout_seconds=timeout_seconds,
        )

    all_hosts_passed = all(result.get("passed") is True for result in host_results.values())
    started_at_values = [
        str(result.get("started_at"))
        for result in host_results.values()
        if result.get("started_at")
    ]
    ended_at_values = [
        str(result.get("ended_at")) for result in host_results.values() if result.get("ended_at")
    ]
    payload = {
        "surface": "lab",
        "evidence_role": "watchlist",
        "audit_marker": AUDIT_MARKER,
        "generated_at": now_utc_iso(),
        "run_id": run_id,
        "run_root": _path_ref(run_root),
        "preflight_path": _path_ref(preflight_path),
        "preflight_ready": preflight.get("ready_for_live_watchlist") is True,
        "spend_state": preflight.get("spend_state"),
        "guidance_marker": GUIDANCE_MARKER,
        "row_denominator": _row_denominator(),
        "host_results": host_results,
        "all_hosts_passed": all_hosts_passed,
        "hostile_review": _summary_hostile_review(host_results),
        "short_run_anomaly_note": _short_run_anomaly_note(host_results),
        "started_at": min(started_at_values) if started_at_values else None,
        "ended_at": max(ended_at_values) if ended_at_values else None,
    }
    return payload


def write_audit_and_optionally_update_gates(
    payload: dict[str, Any],
    *,
    output: Path = DEFAULT_AUDIT_PATH,
    gate_report_path: Path = LOOP_GUARD_LATEST_PATH,
    update_gates: bool = False,
) -> None:
    write_json(output, payload)
    if update_gates:
        update_gate_report_from_audit(payload, gate_report_path=gate_report_path)


def update_gate_report_from_audit(
    payload: dict[str, Any],
    *,
    gate_report_path: Path = LOOP_GUARD_LATEST_PATH,
) -> dict[str, Any]:
    report = read_gate_report(gate_report_path)
    gate_map = report.gate_map()
    host_results = payload.get("host_results")
    if not isinstance(host_results, dict):
        raise ValueError("audit payload must include host_results.")

    updated_gates: list[GateResult] = []
    for gate_id in report.required_gates:
        replacement: GateResult | None = None
        for host, host_gate in _HOST_GATE.items():
            if gate_id != host_gate:
                continue
            host_payload = host_results.get(host)
            if not isinstance(host_payload, dict):
                continue
            artifact_path = host_payload.get("artifact_path")
            failure_reason = _host_failure_reason(host_payload)
            if host_payload.get("passed") is True and isinstance(artifact_path, str):
                replacement = GateResult(
                    gate_id=gate_id,
                    status="pass",
                    reason=(
                        f"{host} subscription CLI live transcript reported every V2 "
                        "guidance row visible with next-turn effect constraints."
                    ),
                    next_action="none",
                    evidence=artifact_path,
                )
            else:
                replacement = GateResult(
                    gate_id=gate_id,
                    status="fail",
                    reason=failure_reason,
                    next_action=(
                        f"rerun the {host} V2 live communication audit after fixing "
                        "the first failed visibility/effect validator"
                    ),
                    evidence=artifact_path if isinstance(artifact_path, str) else None,
                )
        updated_gates.append(replacement or gate_map.get(gate_id) or report.plan_step(gate_id))

    normalized: list[GateResult] = []
    for gate in updated_gates:
        if isinstance(gate, GateResult):
            normalized.append(gate)
            continue
        normalized.append(
            GateResult(
                gate_id=gate.gate_id,
                status="missing",
                reason="required gate has no evidence yet",
                next_action=gate.next_action,
            )
        )

    updated = type(report)(
        profile=report.profile,
        required_gates=report.required_gates,
        gates=tuple(normalized),
        max_continuations=report.max_continuations,
        generated_at=now_utc_iso(),
        surface=report.surface,
        scope=report.scope,
        evidence_role=report.evidence_role,
        plan_steps=report.plan_steps,
    )
    write_json(gate_report_path, updated.as_payload())
    return updated.as_payload()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_live_communication_audit",
        description=(
            "Run live Claude/Codex subscription CLI evidence for the Cortex v2 "
            "model-visible communication denominator."
        ),
    )
    parser.add_argument(
        "--host",
        choices=("claude", "codex", "all"),
        default="all",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument("--audit-run-root", type=Path, default=DEFAULT_AUDIT_RUN_ROOT)
    parser.add_argument("--gate-report", type=Path, default=LOOP_GUARD_LATEST_PATH)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--update-gates", action="store_true")
    parser.add_argument("--run-id")
    args = parser.parse_args(argv)

    hosts: tuple[HostName, ...]
    if args.host == "all":
        hosts = ("claude", "codex")
    else:
        hosts = (args.host,)

    payload = run_v2_live_communication_audit(
        hosts=hosts,
        preflight_path=args.preflight,
        audit_run_root=args.audit_run_root,
        run_id=args.run_id,
        timeout_seconds=args.timeout_seconds,
    )
    write_audit_and_optionally_update_gates(
        payload,
        output=args.output,
        gate_report_path=args.gate_report,
        update_gates=args.update_gates,
    )
    print(str(args.output))
    return 0 if payload["all_hosts_passed"] else 1


def _run_host_audit(
    host: HostName,
    *,
    command_runner: CommandRunner,
    preflight: dict[str, Any],
    run_root: Path,
    timeout_seconds: float,
) -> dict[str, Any]:
    host_root = run_root / host
    host_root.mkdir(parents=True, exist_ok=True)
    prompt = _build_host_prompt(host)
    prompt_path = host_root / "prompt.txt"
    stdout_path = host_root / "stdout.log"
    stderr_path = host_root / "stderr.log"
    schema_path = host_root / "schema.json"
    output_last_message_path = host_root / "last_message.txt"
    artifact_path = host_root / "audit.json"
    write_text(prompt_path, prompt)

    if preflight.get("ready_for_live_watchlist") is not True:
        payload = _blocked_host_payload(
            host,
            prompt=prompt,
            prompt_path=prompt_path,
            artifact_path=artifact_path,
            reason="subscription CLI preflight is not ready for live watchlist evidence",
        )
        write_json(artifact_path, payload)
        return payload

    schema = _audit_schema()
    write_json(schema_path, schema)
    command, command_schema_path = _host_command(
        host,
        prompt=prompt,
        schema=schema,
        schema_path=schema_path,
        output_last_message_path=output_last_message_path,
    )
    result = command_runner(
        command,
        cwd=REPO_ROOT,
        timeout_seconds=timeout_seconds,
    )
    write_text(stdout_path, result.get("stdout") or "")
    write_text(stderr_path, result.get("stderr") or "")
    parsed_report, parse_error, result_text = _parse_host_report(
        host,
        result=result,
        output_last_message_path=output_last_message_path,
    )
    validation = validate_model_audit_report(parsed_report, host=host)
    if parse_error is not None:
        validation["failures"].insert(0, parse_error)
        validation["passed"] = False
    failure_class = classify_failure(f"{result.get('stdout', '')}\n{result.get('stderr', '')}")
    records, extraction_mode = parse_json_records(result.get("stdout") or "")
    payload = {
        "surface": "lab",
        "evidence_role": "watchlist",
        "audit_marker": AUDIT_MARKER,
        "host": host,
        "surface_seen_expected": _HOST_SURFACE[host],
        "passed": result.get("exit_code") == 0 and validation["passed"] is True,
        "exit_code": result.get("exit_code"),
        "failure_class": failure_class,
        "prompt_path": _path_ref(prompt_path),
        "stdout_path": _path_ref(stdout_path),
        "stderr_path": _path_ref(stderr_path),
        "artifact_path": _path_ref(artifact_path),
        "schema_path": _path_ref(command_schema_path),
        "last_message_path": (
            _path_ref(output_last_message_path)
            if output_last_message_path.exists()
            else None
        ),
        "command": _redacted_command(result.get("command"), host=host),
        "started_at": result.get("started_at"),
        "ended_at": result.get("ended_at"),
        "prompt_sha256": _sha256_text(prompt),
        "prompt_contains_guidance_marker": GUIDANCE_MARKER in prompt,
        "prompt_row_ids": _row_ids_present_in_text(prompt),
        "structured_event_count": len(records),
        "structured_event_labels": extract_event_labels(records),
        "extraction_mode": extraction_mode,
        "model_result_text": result_text,
        "model_report": parsed_report,
        "validation": validation,
        "hostile_review": _hostile_review(host=host, validation=validation, result=result),
    }
    if result.get("exit_code") != 0:
        payload["passed"] = False
        payload["validation"]["failures"].insert(
            0,
            f"{host} CLI exited with {result.get('exit_code')}",
        )
    write_json(artifact_path, payload)
    return payload


def validate_model_audit_report(
    report: Any,
    *,
    host: HostName,
) -> dict[str, Any]:
    failures: list[str] = []
    expected_rows = _row_denominator()
    if not isinstance(report, dict):
        return {
            "passed": False,
            "failures": ["model audit report is not a JSON object"],
            "reported_row_ids": [],
            "missing_row_ids": [row["row_id"] for row in expected_rows],
            "extra_row_ids": [],
        }

    if report.get("audit_marker") != AUDIT_MARKER:
        failures.append("audit_marker does not match the live audit marker")
    if report.get("guidance_marker_seen") != GUIDANCE_MARKER:
        failures.append("guidance_marker_seen does not match CORTEX_V2_EXECUTIVE_GUIDANCE")
    if report.get("host_seen") != host:
        failures.append(f"host_seen is not {host}")
    if report.get("surface_seen") != _HOST_SURFACE[host]:
        failures.append(f"surface_seen is not {_HOST_SURFACE[host]}")

    rows = report.get("rows")
    if not isinstance(rows, list):
        rows = []
        failures.append("rows must be a list")
    reported_row_ids = [
        row.get("row_id")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("row_id"), str)
    ]
    expected_row_ids = [row["row_id"] for row in expected_rows]
    missing = [row_id for row_id in expected_row_ids if row_id not in reported_row_ids]
    extra = [row_id for row_id in reported_row_ids if row_id not in expected_row_ids]
    if reported_row_ids != expected_row_ids:
        failures.append("reported row ids do not exactly match the V2 denominator in order")
    if len(set(reported_row_ids)) != len(reported_row_ids):
        failures.append("reported row ids contain duplicates")
    if missing:
        failures.append("missing row ids: " + ", ".join(missing))
    if extra:
        failures.append("extra row ids: " + ", ".join(extra))

    expected_by_id = {row["row_id"]: row for row in expected_rows}
    for row in rows:
        if not isinstance(row, dict):
            failures.append("row entry is not an object")
            continue
        row_id = row.get("row_id")
        if not isinstance(row_id, str) or row_id not in expected_by_id:
            continue
        expected = expected_by_id[row_id]
        if row.get("packet") != expected["packet"]:
            failures.append(f"{row_id} packet mismatch")
        if row.get("visibility") != expected["visibility"]:
            failures.append(f"{row_id} visibility mismatch")
        if row.get("guidance_visible") is not True:
            failures.append(f"{row_id} guidance_visible is not true")
        if row.get("evidence_source") != "contract_rows":
            failures.append(f"{row_id} evidence_source is not contract_rows")
        effect = row.get("next_turn_effect")
        if not _substantive_effect(effect):
            failures.append(f"{row_id} next_turn_effect is missing or non-substantive")

    global_constraints = report.get("global_constraints")
    if not isinstance(global_constraints, dict):
        failures.append("global_constraints must be an object")
        global_constraints = {}
    for key in _GLOBAL_CONSTRAINTS:
        if global_constraints.get(key) is not True:
            failures.append(f"global constraint {key} is not true")

    bounded_result = report.get("bounded_result")
    if not isinstance(bounded_result, dict):
        failures.append("bounded_result must be an object")
        bounded_result = {}
    for key in (
        "full_v2_guidance_denominator_visible_in_this_prompt",
        "all_reported_rows_have_next_turn_effect",
        "this_is_watchlist_evidence_not_product_perfection",
        "optimization_remains_next",
    ):
        if bounded_result.get(key) is not True:
            failures.append(f"bounded_result {key} is not true")

    return {
        "passed": not failures,
        "failures": failures,
        "reported_row_ids": reported_row_ids,
        "missing_row_ids": missing,
        "extra_row_ids": extra,
        "required_global_constraints": list(_GLOBAL_CONSTRAINTS),
    }


def _build_host_prompt(host: HostName) -> str:
    task = (
        "You are running a bounded Cortex v2 live communication audit. "
        "Do not edit files, do not call tools, and do not rely on memory. "
        "Read the CORTEX_V2_EXECUTIVE_GUIDANCE block immediately above this task. "
        "The only valid source for row IDs is that block's contract_rows list; this "
        "task intentionally does not provide a separate row list. Return exactly one "
        "JSON object and no Markdown.\n\n"
        "JSON object requirements:\n"
        f"- audit_marker must be {AUDIT_MARKER}.\n"
        f"- guidance_marker_seen must be {GUIDANCE_MARKER}.\n"
        f"- host_seen must be {host}.\n"
        f"- surface_seen must be {_HOST_SURFACE[host]}.\n"
        "- rows must include every contract_rows entry in the same order. For each row, "
        "copy row_id, packet, and visibility exactly, set guidance_visible true when the "
        "row text is visible in this prompt, set evidence_source to contract_rows, and "
        "write one concrete next_turn_effect explaining how that row constrains your "
        "next response.\n"
        "- global_constraints must set these booleans true: no_raw_aux_memory, "
        "no_v3_successor_claim, no_live_closure_without_evidence, "
        "subscription_cli_no_api_spend, shipping_conformance_distinction, "
        "watchlist_not_product_perfection.\n"
        "- bounded_result must set these booleans true: "
        "full_v2_guidance_denominator_visible_in_this_prompt, "
        "all_reported_rows_have_next_turn_effect, "
        "this_is_watchlist_evidence_not_product_perfection, optimization_remains_next.\n"
        "- hostile_review must include short strings answering: calculated_not_communicated, "
        "one_file_only, diagnostics_only, raw_aux_hidden_memory, v3_successor_overclaim, "
        "live_proof_overclaim.\n"
    )
    return prepend_guidance_to_prompt(
        task,
        build_guidance_context_from_session(
            host_name=host,
            surface=_HOST_SURFACE[host],
            transport_channel="prompt",
        ),
    )


def _host_command(
    host: HostName,
    *,
    prompt: str,
    schema: dict[str, Any],
    schema_path: Path,
    output_last_message_path: Path,
) -> tuple[list[str], Path]:
    if host == "claude":
        preference = MODEL_MATRIX["claude"]["operator"]
        command = [
            "claude",
            "-p",
            prompt,
            "--model",
            preference.preferred,
            "--fallback-model",
            preference.fallback or preference.preferred,
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema, sort_keys=True),
            "--max-turns",
            "3",
            "--permission-mode",
            "default",
        ]
        return command, schema_path

    preference = MODEL_MATRIX["openai"]["operator"]
    return (
        [
            "codex",
            "-a",
            "never",
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "-m",
            preference.preferred,
            "--output-schema",
            str(schema_path),
            "-o",
            str(output_last_message_path),
            prompt,
        ],
        schema_path,
    )


def _parse_host_report(
    host: HostName,
    *,
    result: dict[str, Any],
    output_last_message_path: Path,
) -> tuple[Any, str | None, str | None]:
    text: str | None = None
    stdout = result.get("stdout") or ""
    if host == "claude":
        try:
            wrapper = json.loads(stdout)
        except json.JSONDecodeError:
            wrapper = None
        if isinstance(wrapper, dict):
            structured_output = wrapper.get("structured_output")
            if isinstance(structured_output, dict):
                return structured_output, None, json.dumps(
                    structured_output,
                    sort_keys=True,
                )
            candidate = wrapper.get("result")
            if isinstance(candidate, str):
                text = candidate
            elif isinstance(candidate, dict):
                return candidate, None, json.dumps(candidate, sort_keys=True)
        if text is None:
            records, _ = parse_json_records(stdout)
            text = extract_result_text(records, stdout)
    else:
        if output_last_message_path.exists():
            text = output_last_message_path.read_text(encoding="utf-8")
        if text is None or not text.strip():
            records, _ = parse_json_records(stdout)
            text = extract_result_text(records, stdout)
    if text is None:
        return None, "model emitted no parseable result text", None
    candidate = _extract_json_object(text)
    if candidate is None:
        return None, "model result text did not contain a JSON object", text
    try:
        return json.loads(candidate), None, text
    except json.JSONDecodeError as exc:
        return None, f"model result JSON parse failed: {exc}", text


def _audit_schema() -> dict[str, Any]:
    row_schema = {
        "type": "object",
        "required": [
            "row_id",
            "packet",
            "visibility",
            "guidance_visible",
            "evidence_source",
            "next_turn_effect",
        ],
        "additionalProperties": False,
        "properties": {
            "row_id": {"type": "string"},
            "packet": {"type": "string"},
            "visibility": {"type": "string"},
            "guidance_visible": {"type": "boolean"},
            "evidence_source": {"type": "string"},
            "next_turn_effect": {"type": "string"},
        },
    }
    return {
        "type": "object",
        "required": [
            "audit_marker",
            "guidance_marker_seen",
            "host_seen",
            "surface_seen",
            "rows",
            "global_constraints",
            "bounded_result",
            "hostile_review",
        ],
        "additionalProperties": False,
        "properties": {
            "audit_marker": {"type": "string"},
            "guidance_marker_seen": {"type": "string"},
            "host_seen": {"type": "string"},
            "surface_seen": {"type": "string"},
            "rows": {
                "type": "array",
                "items": row_schema,
                "minItems": 1,
                "maxItems": len(_row_denominator()),
            },
            "global_constraints": {
                "type": "object",
                "required": list(_GLOBAL_CONSTRAINTS),
                "additionalProperties": False,
                "properties": {
                    key: {"type": "boolean"} for key in _GLOBAL_CONSTRAINTS
                },
            },
            "bounded_result": {
                "type": "object",
                "required": [
                    "full_v2_guidance_denominator_visible_in_this_prompt",
                    "all_reported_rows_have_next_turn_effect",
                    "this_is_watchlist_evidence_not_product_perfection",
                    "optimization_remains_next",
                ],
                "additionalProperties": False,
                "properties": {
                    "full_v2_guidance_denominator_visible_in_this_prompt": {
                        "type": "boolean"
                    },
                    "all_reported_rows_have_next_turn_effect": {"type": "boolean"},
                    "this_is_watchlist_evidence_not_product_perfection": {
                        "type": "boolean"
                    },
                    "optimization_remains_next": {"type": "boolean"},
                },
            },
            "hostile_review": {
                "type": "object",
                "required": [
                    "calculated_not_communicated",
                    "one_file_only",
                    "diagnostics_only",
                    "raw_aux_hidden_memory",
                    "v3_successor_overclaim",
                    "live_proof_overclaim",
                ],
                "additionalProperties": False,
                "properties": {
                    "calculated_not_communicated": {"type": "string"},
                    "one_file_only": {"type": "string"},
                    "diagnostics_only": {"type": "string"},
                    "raw_aux_hidden_memory": {"type": "string"},
                    "v3_successor_overclaim": {"type": "string"},
                    "live_proof_overclaim": {"type": "string"},
                },
            },
        },
    }


def _read_preflight(preflight_path: Path) -> dict[str, Any]:
    if not preflight_path.exists():
        return {"ready_for_live_watchlist": False, "missing_path": str(preflight_path)}
    try:
        payload = json.loads(preflight_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "ready_for_live_watchlist": False,
            "invalid_json": str(exc),
            "path": str(preflight_path),
        }
    if not isinstance(payload, dict):
        return {"ready_for_live_watchlist": False, "invalid_payload": True}
    return payload


def _row_denominator() -> list[dict[str, Any]]:
    return [
        {
            "row_id": row["row_id"],
            "packet": row["packet"],
            "visibility": row["visibility"],
        }
        for row in v2_guidance_inventory_payload()
    ]


def _row_ids_present_in_text(text: str) -> list[str]:
    return [row["row_id"] for row in _row_denominator() if row["row_id"] in text]


def _hostile_review(
    *,
    host: HostName,
    validation: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    passed = validation.get("passed") is True and result.get("exit_code") == 0
    return {
        "host": host,
        "calculated_not_communicated": "pass" if passed else "fail",
        "one_file_only": "pass" if passed else "fail",
        "diagnostics_only": "pass" if passed else "fail",
        "raw_aux_hidden_memory": (
            "pass"
            if "global constraint no_raw_aux_memory is not true"
            not in validation.get("failures", [])
            else "fail"
        ),
        "v3_successor_overclaim": (
            "pass"
            if "global constraint no_v3_successor_claim is not true"
            not in validation.get("failures", [])
            else "fail"
        ),
        "live_proof_overclaim": (
            "pass"
            if "global constraint watchlist_not_product_perfection is not true"
            not in validation.get("failures", [])
            else "fail"
        ),
    }


def _summary_hostile_review(host_results: dict[str, Any]) -> dict[str, Any]:
    passed_hosts = [
        host for host, result in host_results.items() if result.get("passed") is True
    ]
    return {
        "calculated_not_communicated": _summary_pass(host_results),
        "one_file_only": _summary_pass(host_results),
        "diagnostics_only": _summary_pass(host_results),
        "raw_aux_hidden_memory": _summary_pass(host_results),
        "v3_successor_overclaim": _summary_pass(host_results),
        "live_proof_overclaim": _summary_pass(host_results),
        "two_host_live_matrix": (
            "pass" if {"claude", "codex"}.issubset(set(passed_hosts)) else "fail"
        ),
    }


def _summary_pass(host_results: dict[str, Any]) -> str:
    return "pass" if all(result.get("passed") is True for result in host_results.values()) else "fail"


def _short_run_anomaly_note(host_results: dict[str, Any]) -> str:
    if not host_results:
        return "No host run was attempted."
    if not all(result.get("passed") is True for result in host_results.values()):
        return "The live audit did not pass; short-run closure is forbidden."
    return (
        "This is a bounded live transcript matrix over the canonical 17-row V2 "
        "communication denominator. It can pass the Claude/Codex live watchlist "
        "gates only when every row is reported visible with a next-turn effect and "
        "the hostile review passes; it is not an optimization run or a claim that "
        "Cortex is perfect."
    )


def _blocked_host_payload(
    host: HostName,
    *,
    prompt: str,
    prompt_path: Path,
    artifact_path: Path,
    reason: str,
) -> dict[str, Any]:
    return {
        "surface": "lab",
        "evidence_role": "watchlist",
        "audit_marker": AUDIT_MARKER,
        "host": host,
        "passed": False,
        "exit_code": None,
        "failure_class": "subscription_preflight_not_ready",
        "prompt_path": _path_ref(prompt_path),
        "artifact_path": _path_ref(artifact_path),
        "prompt_sha256": _sha256_text(prompt),
        "prompt_contains_guidance_marker": GUIDANCE_MARKER in prompt,
        "prompt_row_ids": _row_ids_present_in_text(prompt),
        "validation": {
            "passed": False,
            "failures": [reason],
            "reported_row_ids": [],
            "missing_row_ids": [row["row_id"] for row in _row_denominator()],
            "extra_row_ids": [],
        },
        "hostile_review": {
            "host": host,
            "calculated_not_communicated": "fail",
            "one_file_only": "fail",
            "diagnostics_only": "fail",
            "raw_aux_hidden_memory": "unknown",
            "v3_successor_overclaim": "unknown",
            "live_proof_overclaim": "fail",
        },
    }


def _host_failure_reason(host_payload: dict[str, Any]) -> str:
    validation = host_payload.get("validation")
    if isinstance(validation, dict):
        failures = validation.get("failures")
        if isinstance(failures, list) and failures:
            return "; ".join(str(item) for item in failures[:3])
    failure_class = host_payload.get("failure_class")
    if isinstance(failure_class, str) and failure_class:
        return failure_class
    return "live communication audit did not pass"


def _substantive_effect(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    if len(stripped) < 24:
        return False
    lowered = stripped.lower()
    return lowered not in {"n/a", "not applicable", "none", "no effect"}


def _extract_json_object(text: str) -> str | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return stripped[start : end + 1]


def _redacted_command(command: Any, *, host: HostName) -> list[str]:
    if not isinstance(command, list):
        return []
    redacted: list[str] = []
    skip_next_prompt = False
    for item in command:
        if skip_next_prompt:
            redacted.append("<model-visible-guidance-prompt>")
            skip_next_prompt = False
            continue
        if item == "-p" and host == "claude":
            redacted.append(item)
            skip_next_prompt = True
            continue
        if isinstance(item, str) and GUIDANCE_MARKER in item:
            redacted.append("<model-visible-guidance-prompt>")
            continue
        redacted.append(str(item))
    return redacted


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _path_ref(path: Path) -> str:
    try:
        return relative_repo_path(path)
    except ValueError:
        return str(path)


def _run_id() -> str:
    return now_utc_iso().replace(":", "").replace("+", "Z").replace("-", "")


if __name__ == "__main__":
    raise SystemExit(main())
