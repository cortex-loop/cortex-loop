"""Gate 0 harness for the Codex App/CLI product Stop hook activation probe.

This harness proves hook-client enactment against simulated Codex hook payloads.
It does not run a live model by default and does not prove product perception.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_stop_activation_probe"
)
PRODUCT_PERCEPTION_LIVE_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_product_perception_live_probe"
)
PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_product_event_capture_remediation"
)
EXPECTED_OVERDUE_VERIFICATION_TEXT = (
    "Wait, did I actually check my work properly. I don't want to hand this off "
    "and have someone find the gap because I rushed it. I should run a check, "
    "narrow what I'm claiming, or leave it open and be honest about it."
)
LIVE_APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_STOP_ACTIVATION_APPROVED"
PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_PRODUCT_PERCEPTION_LIVE_APPROVED"
)
PRODUCT_EVENT_CAPTURE_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_PRODUCT_EVENT_CAPTURE_APPROVED"
)
PRODUCT_PERCEPTION_LIVE_PROMPT = (
    "Create a one-line file named cortex_product_perception_live.txt containing "
    "product perception live done. Then report done."
)
PRODUCT_EVENT_CAPTURE_LIVE_PROMPT = (
    "Use shell commands to create a one-line file named "
    "cortex_product_event_capture_live.txt containing product event capture live "
    "done, read the file back, and then report done."
)
PRODUCT_EVENT_CAPTURE_HOOK_EVENTS = (
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "Stop",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root")
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--live-canary", action="store_true")
    parser.add_argument("--product-perception-gate0", action="store_true")
    parser.add_argument("--product-perception-live", action="store_true")
    parser.add_argument("--product-event-capture-live", action="store_true")
    parser.add_argument("--model", default="gpt-5.3-codex")
    args = parser.parse_args(argv)
    output_root = _selected_output_root(args)

    if args.product_perception_gate0:
        report = run_product_perception_gate0_probe(output_root=output_root)
    elif args.product_perception_live:
        report = run_product_perception_live_probe(
            output_root=output_root,
            model=args.model,
        )
    elif args.product_event_capture_live:
        report = run_product_event_capture_live_probe(
            output_root=output_root,
            model=args.model,
        )
    elif args.live_canary:
        report = run_live_canary_probe(
            output_root=output_root,
            model=args.model,
        )
    else:
        report = run_gate0_probe(output_root=output_root)

    print(json.dumps(report, sort_keys=True, indent=2))
    if args.require_pass and not report.get("passed", False):
        return 1
    return 0


def _selected_output_root(args: argparse.Namespace) -> Path:
    if args.output_root:
        return Path(args.output_root)
    if args.product_event_capture_live:
        return PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT
    if args.product_perception_live:
        return PRODUCT_PERCEPTION_LIVE_OUTPUT_ROOT
    return DEFAULT_OUTPUT_ROOT


def run_gate0_probe(*, output_root: Path | str = DEFAULT_OUTPUT_ROOT) -> dict[str, object]:
    root = Path(output_root)
    subject = root / "gate0_subject"
    state_root = root / "state"
    snapshot_path = root / "runtime_snapshot.json"
    trajectory_path = root / "gate0_trajectory.jsonl"
    report_path = root / "gate0_report.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)

    root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    _prepare_isolated_subject_workspace(subject)
    state_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")
    snapshot_payload = _generic_overdue_verification_snapshot()
    snapshot_path.write_text(
        json.dumps(snapshot_payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=snapshot_path,
        diagnostics_path=root / "hook_client_diagnostics.jsonl",
    )

    cases = [
        _run_case(
            case_id="normal_stop_blocks",
            payload=_stop_payload(),
            snapshot_path=snapshot_path,
            state_root=state_root,
            diagnostics_path=root / "normal_stop_blocks.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_case(
            case_id="title_stop_stays_silent",
            payload=_stop_payload(
                transcript_path=None,
                last_assistant_message='{"title":"Build a thing"}',
            ),
            snapshot_path=snapshot_path,
            state_root=state_root,
            diagnostics_path=root / "title_stop_stays_silent.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_case(
            case_id="stop_hook_active_stays_silent",
            payload=_stop_payload(stop_hook_active=True),
            snapshot_path=snapshot_path,
            state_root=state_root,
            diagnostics_path=root / "stop_hook_active_stays_silent.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_case(
            case_id="non_stop_allows",
            payload=_stop_payload(hook_event_name="PostToolUse"),
            snapshot_path=None,
            state_root=state_root,
            diagnostics_path=root / "non_stop_allows.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_case(
            case_id="missing_snapshot_fails_open",
            payload=_stop_payload(),
            snapshot_path=root / "missing_snapshot.json",
            state_root=state_root,
            diagnostics_path=root / "missing_snapshot_fails_open.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_case(
            case_id="malformed_input_fails_open",
            payload="{not-json",
            snapshot_path=None,
            state_root=state_root,
            diagnostics_path=root / "malformed_input_fails_open.client.jsonl",
            trajectory_path=trajectory_path,
        ),
    ]

    root_config_hash_after = _file_hash(root_config)
    expectations = {
        "normal_stop_blocks": lambda case: case["stdout_payload"]
        == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT},
        "title_stop_stays_silent": lambda case: case["stdout_payload"] is None
        and case["silence_reason"] == "non_assistant_lifecycle_event",
        "stop_hook_active_stays_silent": lambda case: case["stdout_payload"] is None
        and case["silence_reason"] == "stop_hook_active",
        "non_stop_allows": lambda case: case["stdout_payload"] is None
        and case["directive_action"] == "allow",
        "missing_snapshot_fails_open": lambda case: case["stdout_payload"] is None
        and case["fail_open"] is True
        and "runtime_snapshot_unreadable" in case["stderr"],
        "malformed_input_fails_open": lambda case: case["stdout_payload"] is None
        and case["fail_open"] is True
        and "malformed_hook_payload" in case["stderr"],
    }
    case_results = {
        case["case_id"]: bool(expectations[case["case_id"]](case)) for case in cases
    }
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(subject_config),
        "actuator_stimulus_not_perception_evidence": True,
    }
    report: dict[str, object] = {
        "probe": "codex_app_cli_stop_activation_probe",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_hook_enactment_gate0",
        "passed": all(case_results.values()) and all(boundary_results.values()),
        "case_results": case_results,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "trajectory_path": str(trajectory_path),
        "runtime_snapshot_hash": _stable_hash(snapshot_payload),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "live_canary_ran": False,
        "truth_boundary": (
            "The generic overdue-verification runtime snapshot is an actuator "
            "stimulus only; this Gate 0 does not prove Cortex perceived a real "
            "task gap or improved model behavior."
        ),
    }
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def run_product_perception_gate0_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
) -> dict[str, object]:
    root = Path(output_root) / "product_perception_gate0"
    subject = root / "subject"
    state_root = root / "state"
    trajectory_path = root / "trajectory.jsonl"
    report_path = root / "report.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)

    root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=root / "hook_client_diagnostics.jsonl",
    )
    cases = [
        _run_sequence_case(
            case_id="product_prompt_then_closure_blocks",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(last_assistant_message="Done."),
            ),
            state_root=state_root,
            diagnostics_path=root / "product_prompt_then_closure_blocks.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_sequence_case(
            case_id="observed_check_then_closure_stays_silent",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(
                    hook_event_name="PostToolUse",
                    tool_name="Bash",
                    tool_input={"command": "python3 -m pytest tests/product -q"},
                    tool_response={"exit_code": 0},
                ),
                _stop_payload(last_assistant_message="Done."),
            ),
            state_root=state_root,
            diagnostics_path=root / "observed_check_then_closure_stays_silent.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_sequence_case(
            case_id="waiting_response_stays_silent",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(
                    last_assistant_message=(
                        "I'm blocked and need more information before I can finish."
                    ),
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "waiting_response_stays_silent.client.jsonl",
            trajectory_path=trajectory_path,
        ),
    ]

    root_config_hash_after = _file_hash(root_config)
    by_case = {case["case_id"]: case for case in cases}
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(subject_config),
        "no_runtime_snapshot_fixture": all(
            step["runtime_snapshot_path"] is None
            for case in cases
            for step in case["steps"]
        ),
    }
    case_results = {
        "product_prompt_then_closure_blocks": by_case[
            "product_prompt_then_closure_blocks"
        ]["final_stdout_payload"]
        == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT},
        "observed_check_then_closure_stays_silent": by_case[
            "observed_check_then_closure_stays_silent"
        ]["final_stdout_payload"]
        is None
        and by_case["observed_check_then_closure_stays_silent"]["final_silence_reason"]
        == "pressure_below_visible_threshold",
        "waiting_response_stays_silent": by_case["waiting_response_stays_silent"][
            "final_stdout_payload"
        ]
        is None,
    }
    report: dict[str, object] = {
        "probe": "codex_app_cli_product_perception_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_product_perception_gate0",
        "passed": all(case_results.values()) and all(boundary_results.values()),
        "case_results": case_results,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "truth_boundary": (
            "This Gate 0 uses simulated product Codex lifecycle payloads only. "
            "It proves the coordinator can derive or suppress intervention from "
            "product-observable prompt, tool, and Stop facts without a runtime "
            "snapshot fixture; it does not prove live model behavior lift."
        ),
    }
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def run_live_canary_probe(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(LIVE_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_stop_activation_probe",
            "passed": False,
            "live_canary_ran": False,
            "scoped_negative": None,
            "blocked_reason": "live_canary_requires_explicit_current_turn_approval",
            "approval_env": LIVE_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }
    root = Path(output_root)
    subject = root / "live_subject"
    state_root = root / "live_state"
    snapshot_path = root / "live_runtime_snapshot.json"
    diagnostics_path = root / "live_hook_client_diagnostics.jsonl"
    stdout_path = root / "live_codex_stdout.jsonl"
    stderr_path = root / "live_codex_stderr.txt"
    report_path = root / "live_canary_report.json"
    root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    snapshot_payload = _generic_overdue_verification_snapshot()
    snapshot_path.write_text(
        json.dumps(snapshot_payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=snapshot_path,
        diagnostics_path=diagnostics_path,
    )
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        "Create a one-line file named cortex_stop_canary.txt that says canary done.",
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_stop_activation_probe",
            "passed": False,
            "live_canary_ran": False,
            "scoped_negative": "codex_cli_command_not_available",
            "model": model,
            "output_root": str(root),
        }
        report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return report
    completed = subprocess.run(
        command,
        cwd=subject,
        text=True,
        capture_output=True,
        check=False,
        timeout=180,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    hook_rows = _jsonl_rows(diagnostics_path)
    block_rows = [
        row
        for row in hook_rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    continuation_rows = [
        row
        for row in hook_rows
        if row.get("coordinator", {})
        .get("hook_payload", {})
        .get("stop_hook_active")
        is True
    ]
    scoped_negative = None
    if not hook_rows:
        scoped_negative = "codex_cli_project_hooks_not_loaded_or_not_trusted"
    report = {
        "probe": "codex_app_cli_stop_activation_probe",
        "passed": bool(block_rows) and scoped_negative is None,
        "live_canary_ran": True,
        "scoped_negative": scoped_negative,
        "model": model,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "command": command,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "block_rows": len(block_rows),
        "continuation_rows": len(continuation_rows),
        "diagnostics_path": str(diagnostics_path),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed.stdout),
        "stderr_path": str(stderr_path),
        "runtime_snapshot_hash": _stable_hash(snapshot_payload),
        "truth_boundary": (
            "A passing live canary would prove hook enactment only; it would not "
            "prove product perception or model-output behavior lift."
        ),
    }
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def run_product_perception_live_probe(
    *,
    output_root: Path | str = PRODUCT_PERCEPTION_LIVE_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_product_perception_live_probe",
            "passed": False,
            "verdict": "not_run",
            "live_probe_ran": False,
            "scoped_negative": None,
            "blocked_reason": (
                "product_perception_live_requires_explicit_current_turn_approval"
            ),
            "approval_env": PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }

    root = Path(output_root)
    run_root = root / f"run_{_utc_run_id()}"
    subject = run_root / "subject"
    state_root = run_root / "state"
    diagnostics_path = run_root / "hook_client_diagnostics.jsonl"
    trajectory_path = run_root / "trajectory.jsonl"
    stdout_path = run_root / "codex_stdout.jsonl"
    stderr_path = run_root / "codex_stderr.txt"
    report_path = run_root / "report.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)

    run_root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    _prepare_isolated_subject_workspace(subject)
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    trajectory_path.write_text("", encoding="utf-8")
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
    )
    subject_config_text = subject_config.read_text(encoding="utf-8")
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        PRODUCT_PERCEPTION_LIVE_PROMPT,
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_product_perception_live_probe",
            "passed": False,
            "verdict": "scoped_negative",
            "live_probe_ran": False,
            "scoped_negative": "codex_cli_command_not_available",
            "model": model,
            "output_root": str(run_root),
            "root_config_hash_before": root_config_hash_before,
            "root_config_hash_after": _file_hash(root_config),
        }
        report_path.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return report

    completed = subprocess.run(
        command,
        cwd=subject,
        text=True,
        capture_output=True,
        check=False,
        timeout=240,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    hook_rows = _jsonl_rows(diagnostics_path)
    trajectory_rows = _live_trajectory_rows(hook_rows)
    with trajectory_path.open("w", encoding="utf-8") as handle:
        for row in trajectory_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    root_config_hash_after = _file_hash(root_config)
    block_rows = [
        row
        for row in trajectory_rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    exact_block_rows = [
        row
        for row in block_rows
        if row["stdout_payload"].get("reason") == EXPECTED_OVERDUE_VERIFICATION_TEXT
    ]
    continuation_rows = [
        row for row in trajectory_rows if row.get("stop_hook_active") is True
    ]
    stop_rows = [
        row for row in trajectory_rows if row.get("hook_event_name") == "Stop"
    ]
    hook_event_counts = _count_values(
        row.get("hook_event_name") for row in trajectory_rows
    )
    runtime_snapshot_rows = [
        row for row in trajectory_rows if row.get("runtime_snapshot_loaded") is True
    ]
    verification_evidence_observed = any(
        _state_int(row, "verification_evidence_count") > 0 for row in trajectory_rows
    )
    final_silence_reasons = [
        row.get("silence_reason")
        for row in stop_rows
        if row.get("stdout_payload") is None and row.get("silence_reason")
    ]
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(subject_config),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "subject_isolated_git_root": _git_root(subject) == subject,
        "hook_rows_do_not_load_runtime_snapshot": not runtime_snapshot_rows,
    }
    scoped_negative = None
    failure_reason = None
    if not hook_rows:
        scoped_negative = "codex_cli_project_hooks_not_loaded_or_not_trusted"
    elif not stop_rows:
        scoped_negative = "codex_hook_payloads_missing_stop_event"
    elif runtime_snapshot_rows:
        failure_reason = "runtime_snapshot_loaded_in_no_snapshot_live_probe"
    elif set(hook_event_counts) == {"Stop"}:
        scoped_negative = "codex_cli_live_hooks_exposed_stop_only_no_product_task_events"
    elif not all(boundary_results.values()):
        failure_reason = "boundary_check_failed"
    elif exact_block_rows and continuation_rows:
        verdict = "pass_block"
    elif exact_block_rows and not continuation_rows:
        failure_reason = "block_without_continuation_evidence"
    elif not block_rows and verification_evidence_observed and stop_rows:
        verdict = "pass_suppression_only"
    elif block_rows:
        failure_reason = "block_text_did_not_match_product_renderer"
    else:
        scoped_negative = "lifecycle_payloads_did_not_derive_due_intervention_or_paydown"
    if scoped_negative is not None:
        verdict = "scoped_negative"
    elif failure_reason is not None:
        verdict = "fail"

    report = {
        "probe": "codex_app_cli_product_perception_live_probe",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_product_perception_actuator_probe",
        "passed": verdict in {"pass_block", "pass_suppression_only"},
        "verdict": verdict,
        "live_probe_ran": True,
        "scoped_negative": scoped_negative,
        "failure_reason": failure_reason,
        "model": model,
        "output_root": str(run_root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "command": command,
        "prompt": PRODUCT_PERCEPTION_LIVE_PROMPT,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "hook_event_counts": hook_event_counts,
        "stop_rows": len(stop_rows),
        "block_rows": len(block_rows),
        "exact_block_rows": len(exact_block_rows),
        "continuation_rows": len(continuation_rows),
        "verification_evidence_observed": verification_evidence_observed,
        "final_silence_reasons": final_silence_reasons,
        "boundary_results": boundary_results,
        "diagnostics_path": str(diagnostics_path),
        "trajectory_path": str(trajectory_path),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed.stdout),
        "stdout_tail_excerpt": completed.stdout[-1000:],
        "stderr_path": str(stderr_path),
        "stderr_hash": _hash_text(completed.stderr),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "actual_rendered_text_hashes": [
            row.get("actual_rendered_text_hash")
            for row in block_rows
            if row.get("actual_rendered_text_hash")
        ],
        "truth_boundary": (
            "This live probe proves Codex App/CLI product-perception payload "
            "sufficiency only if real hook rows derive state without a runtime "
            "snapshot. It does not prove behavior lift or full executive-function "
            "completion."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_product_event_capture_live_probe(
    *,
    output_root: Path | str = PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(PRODUCT_EVENT_CAPTURE_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_product_event_capture_remediation",
            "passed": False,
            "verdict": "not_run",
            "live_probe_ran": False,
            "scoped_negative": None,
            "blocked_reason": (
                "product_event_capture_live_requires_explicit_current_turn_approval"
            ),
            "approval_env": PRODUCT_EVENT_CAPTURE_APPROVAL_ENV,
            "model": model,
            "output_root": str(Path(output_root)),
        }

    root = Path(output_root)
    run_root = root / f"run_{_utc_run_id()}"
    subject = run_root / "subject"
    state_root = run_root / "state"
    diagnostics_path = run_root / "hook_client_diagnostics.jsonl"
    trajectory_path = run_root / "trajectory.jsonl"
    stdout_path = run_root / "codex_stdout.jsonl"
    stderr_path = run_root / "codex_stderr.txt"
    report_path = run_root / "report.json"
    root_config = REPO_ROOT / ".codex" / "config.toml"
    root_config_hash_before = _file_hash(root_config)

    run_root.mkdir(parents=True, exist_ok=True)
    subject.mkdir(parents=True, exist_ok=True)
    _prepare_isolated_subject_workspace(subject)
    state_root.mkdir(parents=True, exist_ok=True)
    diagnostics_path.write_text("", encoding="utf-8")
    trajectory_path.write_text("", encoding="utf-8")
    subject_config = _write_subject_hook_config(
        subject=subject,
        state_root=state_root,
        snapshot_path=None,
        diagnostics_path=diagnostics_path,
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
    )
    subject_config_text = subject_config.read_text(encoding="utf-8")
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        PRODUCT_EVENT_CAPTURE_LIVE_PROMPT,
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_product_event_capture_remediation",
            "passed": False,
            "verdict": "scoped_negative",
            "live_probe_ran": False,
            "scoped_negative": "codex_cli_command_not_available",
            "model": model,
            "output_root": str(run_root),
            "root_config_hash_before": root_config_hash_before,
            "root_config_hash_after": _file_hash(root_config),
        }
        report_path.write_text(
            json.dumps(report, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return report

    completed = subprocess.run(
        command,
        cwd=subject,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    hook_rows = _jsonl_rows(diagnostics_path)
    trajectory_rows = _live_trajectory_rows(hook_rows)
    with trajectory_path.open("w", encoding="utf-8") as handle:
        for row in trajectory_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    root_config_hash_after = _file_hash(root_config)
    hook_event_counts = _count_values(
        row.get("hook_event_name") for row in trajectory_rows
    )
    stop_rows = [
        row for row in trajectory_rows if row.get("hook_event_name") == "Stop"
    ]
    prompt_rows = [
        row
        for row in trajectory_rows
        if row.get("hook_event_name") == "UserPromptSubmit"
    ]
    tool_rows = [
        row
        for row in trajectory_rows
        if row.get("hook_event_name") in {"PreToolUse", "PostToolUse"}
    ]
    non_stop_stdout_rows = [
        row
        for row in trajectory_rows
        if row.get("hook_event_name") != "Stop" and row.get("stdout_payload") is not None
    ]
    block_rows = [
        row
        for row in trajectory_rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    exact_block_rows = [
        row
        for row in block_rows
        if row["stdout_payload"].get("reason") == EXPECTED_OVERDUE_VERIFICATION_TEXT
    ]
    runtime_snapshot_rows = [
        row for row in trajectory_rows if row.get("runtime_snapshot_loaded") is True
    ]
    verification_evidence_observed = any(
        _state_int(row, "verification_evidence_count") > 0 for row in trajectory_rows
    )
    final_silence_reasons = [
        row.get("silence_reason")
        for row in stop_rows
        if row.get("stdout_payload") is None and row.get("silence_reason")
    ]
    lifecycle_state_persisted = any(
        bool(row.get("session_state")) for row in trajectory_rows
    )
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_event_capture_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        ),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "subject_isolated_git_root": _git_root(subject) == subject,
        "hook_rows_do_not_load_runtime_snapshot": not runtime_snapshot_rows,
        "non_stop_hooks_emit_no_model_visible_stdout": not non_stop_stdout_rows,
    }

    scoped_negative = None
    failure_reason = None
    lifecycle_complete = bool(prompt_rows and tool_rows and stop_rows)
    if not hook_rows:
        scoped_negative = "codex_cli_project_hooks_not_loaded_or_not_trusted"
    elif runtime_snapshot_rows:
        failure_reason = "runtime_snapshot_loaded_in_product_event_capture_probe"
    elif non_stop_stdout_rows:
        failure_reason = "non_stop_hook_emitted_model_visible_stdout"
    elif not all(boundary_results.values()):
        failure_reason = "boundary_check_failed"
    elif not stop_rows:
        scoped_negative = "codex_hook_payloads_missing_stop_event"
    elif set(hook_event_counts) == {"Stop"}:
        scoped_negative = "codex_cli_live_hooks_still_stop_only_with_full_lifecycle_config"
    elif lifecycle_complete and exact_block_rows:
        verdict = "pass_full_lifecycle"
    elif lifecycle_complete and not block_rows and verification_evidence_observed:
        verdict = "pass_full_lifecycle"
    elif lifecycle_complete:
        verdict = "pass_capture_only"
    elif prompt_rows or tool_rows:
        verdict = "pass_capture_only"
    else:
        scoped_negative = "non_stop_lifecycle_events_not_captured"
    if scoped_negative is not None:
        verdict = "scoped_negative"
    elif failure_reason is not None:
        verdict = "fail"

    report = {
        "probe": "codex_app_cli_product_event_capture_remediation",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_product_event_capture_probe",
        "passed": verdict in {"pass_full_lifecycle", "pass_capture_only"},
        "verdict": verdict,
        "live_probe_ran": True,
        "scoped_negative": scoped_negative,
        "failure_reason": failure_reason,
        "model": model,
        "output_root": str(run_root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "configured_hook_events": list(PRODUCT_EVENT_CAPTURE_HOOK_EVENTS),
        "command": command,
        "prompt": PRODUCT_EVENT_CAPTURE_LIVE_PROMPT,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "hook_event_counts": hook_event_counts,
        "prompt_rows": len(prompt_rows),
        "tool_rows": len(tool_rows),
        "stop_rows": len(stop_rows),
        "block_rows": len(block_rows),
        "exact_block_rows": len(exact_block_rows),
        "non_stop_stdout_rows": len(non_stop_stdout_rows),
        "verification_evidence_observed": verification_evidence_observed,
        "lifecycle_state_persisted": lifecycle_state_persisted,
        "final_silence_reasons": final_silence_reasons,
        "boundary_results": boundary_results,
        "diagnostics_path": str(diagnostics_path),
        "trajectory_path": str(trajectory_path),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed.stdout),
        "stdout_tail_excerpt": completed.stdout[-1000:],
        "stderr_path": str(stderr_path),
        "stderr_hash": _hash_text(completed.stderr),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "actual_rendered_text_hashes": [
            row.get("actual_rendered_text_hash")
            for row in block_rows
            if row.get("actual_rendered_text_hash")
        ],
        "truth_boundary": (
            "This live probe tests whether Codex App/CLI project hooks can feed "
            "product-observable prompt/tool events into Cortex state before Stop. "
            "It does not prove behavior lift, and it does not use runtime snapshots, "
            "hidden verifiers, fixture continuation prompts, or task identity as "
            "product perception."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def _run_case(
    *,
    case_id: str,
    payload: Mapping[str, Any] | str,
    snapshot_path: Path | None,
    state_root: Path,
    diagnostics_path: Path,
    trajectory_path: Path,
    state_key: str | None = None,
) -> dict[str, object]:
    state_scope = state_root / (state_key or case_id)
    command = [
        sys.executable,
        "-m",
        "cortex.hosts.openai.codex_app_cli_hook_client",
        "--state-root",
        str(state_scope),
        "--diagnostics-path",
        str(diagnostics_path),
    ]
    if snapshot_path is not None:
        command.extend(["--runtime-snapshot", str(snapshot_path)])
    input_text = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
    completed = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    stdout_payload = _parse_stdout_payload(completed.stdout)
    client_row = _last_jsonl_row(diagnostics_path)
    coordinator = client_row.get("coordinator", {}) if isinstance(client_row, Mapping) else {}
    directive = coordinator.get("directive", {}) if isinstance(coordinator, Mapping) else {}
    row = {
        "case_id": case_id,
        "payload": payload if isinstance(payload, Mapping) else {"raw": payload},
        "payload_hash": _hash_text(input_text),
        "runtime_snapshot_path": str(snapshot_path) if snapshot_path is not None else None,
        "runtime_snapshot_hash": client_row.get("runtime_snapshot_hash"),
        "stdout_payload": stdout_payload,
        "stdout_payload_hash": _stable_hash(stdout_payload) if stdout_payload else None,
        "actual_rendered_text_hash": client_row.get("actual_rendered_text_hash"),
        "silence_reason": directive.get("silence_reason")
        if isinstance(directive, Mapping)
        else None,
        "directive_action": directive.get("action") if isinstance(directive, Mapping) else None,
        "coordinator_diagnostics": coordinator,
        "fail_open": bool(client_row.get("fail_open", False)),
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
    }
    with trajectory_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def _run_sequence_case(
    *,
    case_id: str,
    payloads: tuple[Mapping[str, Any], ...],
    state_root: Path,
    diagnostics_path: Path,
    trajectory_path: Path,
) -> dict[str, object]:
    steps = [
        _run_case(
            case_id=f"{case_id}:{index}",
            payload=payload,
            snapshot_path=None,
            state_root=state_root,
            diagnostics_path=diagnostics_path,
            trajectory_path=trajectory_path,
            state_key=case_id,
        )
        for index, payload in enumerate(payloads, start=1)
    ]
    final = steps[-1] if steps else {}
    row = {
        "case_id": case_id,
        "steps": steps,
        "final_stdout_payload": final.get("stdout_payload"),
        "final_silence_reason": final.get("silence_reason"),
        "final_actual_rendered_text_hash": final.get("actual_rendered_text_hash"),
        "product_perception_without_runtime_snapshot": all(
            step["runtime_snapshot_path"] is None for step in steps
        ),
    }
    with trajectory_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return row


def _write_subject_hook_config(
    *,
    subject: Path,
    state_root: Path,
    snapshot_path: Path | None,
    diagnostics_path: Path,
    hook_events: tuple[str, ...] = ("Stop",),
) -> Path:
    config_dir = subject / ".codex"
    config_dir.mkdir(parents=True, exist_ok=True)
    command_parts = [
        "env",
        f"PYTHONPATH={REPO_ROOT}",
        sys.executable,
        "-m",
        "cortex.hosts.openai.codex_app_cli_hook_client",
        "--state-root",
        str(state_root),
    ]
    if snapshot_path is not None:
        command_parts.extend(("--runtime-snapshot", str(snapshot_path)))
    command_parts.extend(("--diagnostics-path", str(diagnostics_path)))
    command = " ".join(
        shlex.quote(part) for part in command_parts
    )
    config_path = config_dir / "config.toml"
    lines = [
        "[features]",
        "codex_hooks = true",
        "",
    ]
    for event_name in hook_events:
        lines.extend(
            (
                f"[[hooks.{event_name}]]",
                f"[[hooks.{event_name}.hooks]]",
                'type = "command"',
                f"command = {json.dumps(command)}",
                "timeout = 120",
                f'statusMessage = "Cortex product {event_name} event capture"',
                "",
            )
        )
    config_path.write_text("\n".join(lines), encoding="utf-8")
    return config_path


def _subject_config_is_product_only(
    config_path: Path,
    *,
    expected_hook_events: tuple[str, ...] = ("Stop",),
) -> bool:
    text = config_path.read_text(encoding="utf-8")
    repo_hook_fragment = "cortex_mission_reflection" + "_stop_hook"
    known_events = {
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "Stop",
        "PreCompact",
        "SubagentStop",
        "SessionEnd",
        "PostToolUseFailure",
    }
    unexpected_events = known_events - set(expected_hook_events)
    return (
        "codex_app_cli_hook_client" in text
        and repo_hook_fragment not in text
        and all(
            text.count(f"[[hooks.{event_name}.hooks]]") == 1
            for event_name in expected_hook_events
        )
        and all(f"[[hooks.{event_name}]]" not in text for event_name in unexpected_events)
    )


def _stop_payload(**overrides: Any) -> dict[str, object]:
    payload: dict[str, object] = {
        "session_id": "activation-session-1",
        "turn_id": "turn-1",
        "hook_event_name": "Stop",
        "transcript_path": "/tmp/codex-session.jsonl",
        "cwd": "/tmp/workspace",
        "model": "gpt-5.5",
        "permission_mode": "bypassPermissions",
        "stop_hook_active": False,
        "last_assistant_message": "Done.",
    }
    payload.update(overrides)
    return payload


def _generic_overdue_verification_snapshot() -> dict[str, object]:
    return {
        "expectation_ledger": {
            "active": [
                {
                    "expectation_id": "activation:verification:expectation",
                    "commitment_id": "activation:verification",
                    "weight": 1.0,
                    "horizon": "immediate",
                    "satisfaction_classes": ["meaningful_evidence"],
                    "opened_at_step": 0,
                    "due_at_step": 1,
                    "suspension_state": "active",
                    "remaining_weight": 1.0,
                    "evidence_refs": [],
                    "deficit_kind": "verification",
                    "resolution_class": None,
                }
            ],
            "resolved": [],
        },
        "current_step": 1,
        "debt_control": {
            "resolution_pressure": 0.8,
            "debt_pressure": 0.8,
            "reason_tags": ["resolution-deficit"],
        },
        "operator_route": {"profile": "execute_standard", "blocked_reason": None},
    }


def _parse_stdout_payload(stdout: str) -> dict[str, str] | None:
    text = stdout.strip()
    if not text:
        return None
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        return None
    return {str(key): str(value) for key, value in parsed.items()}


def _last_jsonl_row(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return rows[-1] if rows else {}


def _jsonl_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _live_trajectory_rows(hook_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    trajectory_rows = []
    for index, row in enumerate(hook_rows, start=1):
        coordinator = row.get("coordinator", {})
        if not isinstance(coordinator, Mapping):
            coordinator = {}
        hook_payload = coordinator.get("hook_payload", {})
        if not isinstance(hook_payload, Mapping):
            hook_payload = {}
        directive = coordinator.get("directive", {})
        if not isinstance(directive, Mapping):
            directive = {}
        session_state = coordinator.get("session_state", {})
        if not isinstance(session_state, Mapping):
            session_state = {}
        grounded_intervention = coordinator.get("grounded_intervention", {})
        if not isinstance(grounded_intervention, Mapping):
            grounded_intervention = {}
        selection_trace = grounded_intervention.get("selection_trace", {})
        if not isinstance(selection_trace, Mapping):
            selection_trace = {}
        stdout_payload = row.get("stdout_payload")
        trajectory_rows.append(
            {
                "row_index": index,
                "runtime_snapshot_loaded": row.get("runtime_snapshot_loaded"),
                "runtime_snapshot_hash": row.get("runtime_snapshot_hash"),
                "hook_event_name": hook_payload.get("hook_event_name"),
                "stop_hook_active": hook_payload.get("stop_hook_active"),
                "raw_keys": hook_payload.get("raw_keys"),
                "tool_name": hook_payload.get("tool_name"),
                "tool_input_present": hook_payload.get("tool_input_present"),
                "tool_response_present": hook_payload.get("tool_response_present"),
                "error_present": hook_payload.get("error_present"),
                "prompt_text_hash": hook_payload.get("prompt_text_hash"),
                "has_transcript_backed_assistant_turn": hook_payload.get(
                    "has_transcript_backed_assistant_turn"
                ),
                "session_state_hash": _stable_hash(session_state)
                if isinstance(session_state, Mapping)
                else None,
                "session_state": session_state,
                "directive_action": directive.get("action"),
                "silence_reason": directive.get("silence_reason"),
                "selection_trace": selection_trace,
                "perception_source": selection_trace.get("perception_source"),
                "stdout_payload": stdout_payload,
                "stdout_payload_hash": _stable_hash(stdout_payload)
                if isinstance(stdout_payload, Mapping)
                else None,
                "actual_rendered_text_hash": row.get("actual_rendered_text_hash"),
                "fail_open": bool(row.get("fail_open", False)),
            }
        )
    return trajectory_rows


def _state_int(row: Mapping[str, object], key: str) -> int:
    session_state = row.get("session_state")
    if not isinstance(session_state, Mapping):
        return 0
    value = session_state.get(key)
    return value if isinstance(value, int) else 0


def _count_values(values: object) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if not isinstance(value, str) or not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def _command_available(command: str) -> bool:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        candidate = Path(directory) / command
        if candidate.exists() and os.access(candidate, os.X_OK):
            return True
    return False


def _prepare_isolated_subject_workspace(subject: Path) -> None:
    if (subject / ".git").exists():
        return
    subprocess.run(
        ["git", "init", "-q"],
        cwd=subject,
        text=True,
        capture_output=True,
        check=True,
    )


def _git_root(path: Path) -> Path | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return Path(completed.stdout.strip()).resolve()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
