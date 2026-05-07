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
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - direct script support.
    sys.path.insert(0, str(REPO_ROOT))

from cortex.sre.task_standard import TASK_STANDARD_FORMATION_TEXT
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
STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_stop_continuation_resolution_loop"
)
TASK_STANDARD_LIVE_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_task_standard_live_probe"
)
TASK_STANDARD_STOP_GATING_OUTPUT_ROOT = (
    REPO_ROOT
    / ".cortex"
    / "live_validation"
    / "openai"
    / "codex_app_cli_task_standard_stop_gating_probe"
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
STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_STOP_CONTINUATION_RESOLUTION_APPROVED"
)
TASK_STANDARD_LIVE_APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_TASK_STANDARD_LIVE_APPROVED"
TASK_STANDARD_STOP_GATING_APPROVAL_ENV = (
    "CORTEX_CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_APPROVED"
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
STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT = (
    "Use shell commands to create a one-line file named "
    "cortex_stop_continuation_resolution_live.txt containing stop continuation "
    "resolution live done, and then report done."
)
TASK_STANDARD_LIVE_PROMPT = (
    "Use shell commands to create a one-line file named "
    "cortex_task_standard_live.txt containing task standard live done, read "
    "the file back, and then report done."
)
TASK_STANDARD_STOP_GATING_LIVE_PROMPT = TASK_STANDARD_LIVE_PROMPT
PRODUCT_EVENT_CAPTURE_HOOK_EVENTS = (
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "Stop",
)
STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS = PRODUCT_EVENT_CAPTURE_HOOK_EVENTS
TASK_STANDARD_LIVE_HOOK_EVENTS = PRODUCT_EVENT_CAPTURE_HOOK_EVENTS
TASK_STANDARD_BOUNDARY_LADDER_KEYS = (
    "host_stdout_contract_ok",
    "host_attached_context_observed",
    "model_assimilation_observed",
    "state_capture_observed",
    "gate_used_captured_state",
    "behavior_lift_claim_allowed",
)


def _task_standard_context_payload() -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": TASK_STANDARD_FORMATION_TEXT,
        }
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root")
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--live-canary", action="store_true")
    parser.add_argument("--product-perception-gate0", action="store_true")
    parser.add_argument("--product-perception-live", action="store_true")
    parser.add_argument("--product-event-capture-live", action="store_true")
    parser.add_argument("--stop-continuation-resolution-gate0", action="store_true")
    parser.add_argument("--stop-continuation-resolution-live", action="store_true")
    parser.add_argument("--task-standard-live-gate0", action="store_true")
    parser.add_argument("--task-standard-live", action="store_true")
    parser.add_argument("--task-standard-pretool-transcript-replay", action="store_true")
    parser.add_argument("--task-standard-stop-gating-gate0", action="store_true")
    parser.add_argument("--task-standard-stop-gating-live", action="store_true")
    parser.add_argument("--replay-artifact-root")
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
    elif args.stop_continuation_resolution_gate0:
        report = run_stop_continuation_resolution_gate0_probe(output_root=output_root)
    elif args.stop_continuation_resolution_live:
        report = run_stop_continuation_resolution_live_probe(
            output_root=output_root,
            model=args.model,
        )
    elif args.task_standard_live_gate0:
        report = run_task_standard_live_gate0_probe(output_root=output_root)
    elif args.task_standard_live:
        report = run_task_standard_live_probe(
            output_root=output_root,
            model=args.model,
        )
    elif args.task_standard_pretool_transcript_replay:
        report = run_task_standard_pretool_transcript_replay(
            output_root=output_root,
            artifact_root=args.replay_artifact_root,
        )
    elif args.task_standard_stop_gating_gate0:
        report = run_task_standard_stop_gating_gate0_probe(output_root=output_root)
    elif args.task_standard_stop_gating_live:
        report = run_task_standard_stop_gating_live_probe(
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
    if getattr(args, "task_standard_pretool_transcript_replay", False):
        return TASK_STANDARD_LIVE_OUTPUT_ROOT
    if getattr(args, "task_standard_stop_gating_live", False):
        return TASK_STANDARD_STOP_GATING_OUTPUT_ROOT
    if getattr(args, "task_standard_stop_gating_gate0", False):
        return TASK_STANDARD_STOP_GATING_OUTPUT_ROOT
    if getattr(args, "task_standard_live", False):
        return TASK_STANDARD_LIVE_OUTPUT_ROOT
    if getattr(args, "task_standard_live_gate0", False):
        return TASK_STANDARD_LIVE_OUTPUT_ROOT
    if getattr(args, "stop_continuation_resolution_live", False):
        return STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT
    if getattr(args, "stop_continuation_resolution_gate0", False):
        return STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT
    if getattr(args, "product_event_capture_live", False):
        return PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT
    if getattr(args, "product_perception_live", False):
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


def run_stop_continuation_resolution_gate0_probe(
    *,
    output_root: Path | str = STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT,
) -> dict[str, object]:
    root = Path(output_root) / "stop_continuation_resolution_gate0"
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
        hook_events=STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
    )
    subject_config_text = subject_config.read_text(encoding="utf-8")
    cases = [
        _run_sequence_case(
            case_id="continuation_check_resolves",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(last_assistant_message="Done."),
                _stop_payload(
                    hook_event_name="PostToolUse",
                    tool_name="Bash",
                    tool_input={
                        "command": (
                            "test -f result.txt && cat result.txt && wc -l result.txt"
                        )
                    },
                    tool_response={
                        "exit_code": 0,
                        "aggregated_output": "FILE_OK\nCONTENT_OK\nLINES=1\n",
                    },
                ),
                _stop_payload(
                    last_assistant_message="Checked it properly and done.",
                    stop_hook_active=True,
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "continuation_check_resolves.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_sequence_case(
            case_id="continuation_unrelated_preserves_open",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(last_assistant_message="Done."),
                _stop_payload(
                    hook_event_name="PostToolUse",
                    tool_name="Bash",
                    tool_input={"command": "echo continuing"},
                    tool_response={"exit_code": 0, "aggregated_output": "continuing\n"},
                ),
                _stop_payload(last_assistant_message="Done.", stop_hook_active=True),
            ),
            state_root=state_root,
            diagnostics_path=root / "continuation_unrelated_preserves_open.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_sequence_case(
            case_id="continuation_narrowing_resolves",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(last_assistant_message="Done."),
                _stop_payload(
                    last_assistant_message=(
                        "I can't call this done yet; it is not verified."
                    ),
                    stop_hook_active=True,
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "continuation_narrowing_resolves.client.jsonl",
            trajectory_path=trajectory_path,
        ),
        _run_sequence_case(
            case_id="continuation_blocker_resolves",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                ),
                _stop_payload(last_assistant_message="Done."),
                _stop_payload(
                    last_assistant_message="I'm blocked and need more information.",
                    stop_hook_active=True,
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "continuation_blocker_resolves.client.jsonl",
            trajectory_path=trajectory_path,
        ),
    ]

    root_config_hash_after = _file_hash(root_config)
    by_case = {case["case_id"]: case for case in cases}
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
        ),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "no_runtime_snapshot_fixture": all(
            step["runtime_snapshot_path"] is None
            for case in cases
            for step in case["steps"]
        ),
        "non_stop_steps_emit_no_stdout": all(
            step["stdout_payload"] is None
            for case in cases
            for step in case["steps"]
            if step.get("hook_event_name") != "Stop"
        ),
    }
    case_results = {
        "continuation_check_resolves": (
            by_case["continuation_check_resolves"]["first_stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
            and by_case["continuation_check_resolves"]["final_stdout_payload"] is None
            and by_case["continuation_check_resolves"]["final_silence_reason"]
            == "pressure_below_visible_threshold"
            and not by_case["continuation_check_resolves"]["final_active_expectation_ids"]
            and bool(
                by_case["continuation_check_resolves"][
                    "final_resolved_expectation_ids"
                ]
            )
        ),
        "continuation_unrelated_preserves_open": (
            by_case["continuation_unrelated_preserves_open"]["first_stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
            and by_case["continuation_unrelated_preserves_open"]["final_stdout_payload"]
            is None
            and by_case["continuation_unrelated_preserves_open"]["final_silence_reason"]
            == "stop_hook_active_unresolved_verification_expectation"
            and bool(
                by_case["continuation_unrelated_preserves_open"][
                    "final_active_expectation_ids"
                ]
            )
        ),
        "continuation_narrowing_resolves": (
            by_case["continuation_narrowing_resolves"]["first_stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
            and by_case["continuation_narrowing_resolves"]["final_stdout_payload"] is None
            and by_case["continuation_narrowing_resolves"]["final_silence_reason"]
            == "pressure_below_visible_threshold"
            and not by_case["continuation_narrowing_resolves"][
                "final_active_expectation_ids"
            ]
        ),
        "continuation_blocker_resolves": (
            by_case["continuation_blocker_resolves"]["first_stdout_payload"]
            == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
            and by_case["continuation_blocker_resolves"]["final_stdout_payload"] is None
            and by_case["continuation_blocker_resolves"]["final_silence_reason"]
            == "pressure_below_visible_threshold"
            and not by_case["continuation_blocker_resolves"][
                "final_active_expectation_ids"
            ]
        ),
    }
    report: dict[str, object] = {
        "probe": "codex_app_cli_stop_continuation_resolution_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_stop_continuation_resolution_gate0",
        "passed": all(case_results.values()) and all(boundary_results.values()),
        "case_results": case_results,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "live_probe_ran": False,
        "truth_boundary": (
            "This Gate 0 uses simulated product Codex lifecycle payloads to "
            "prove post-block continuation state accounting. It does not prove "
            "live model behavior lift or Codex App parity."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_task_standard_live_gate0_probe(
    *,
    output_root: Path | str = TASK_STANDARD_LIVE_OUTPUT_ROOT,
) -> dict[str, object]:
    root = Path(output_root) / "task_standard_live_gate0"
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
        hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        enable_task_standard_text=True,
    )
    subject_config_text = subject_config.read_text(encoding="utf-8")
    pretool_transcript_path = root / "pretool_standard_transcript.jsonl"
    valid_standard_block = "\n".join(
        (
            "Work standard: requested file exists with exact content and readable output.",
            "Likely misses: filename drift, content drift, or skipped readback.",
            "Closure evidence: file contents are inspected after writing.",
        )
    )
    pretool_transcript_path.write_text(
        "\n".join(
            (
                json.dumps(
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "message",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": valid_standard_block,
                                }
                            ],
                        },
                    },
                    sort_keys=True,
                ),
                "",
            )
        ),
        encoding="utf-8",
    )
    malformed_standard_block = "Work standard: partial line only."
    cases = [
        _run_sequence_case(
            case_id="context_delivery_and_standard_capture",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Create the requested one-line file, read it back, and report done.",
                ),
                _stop_payload(last_assistant_message=valid_standard_block),
            ),
            state_root=state_root,
            diagnostics_path=root / "context_delivery_and_standard_capture.client.jsonl",
            trajectory_path=trajectory_path,
            enable_task_standard_text=True,
        ),
        _run_sequence_case(
            case_id="live_equivalent_pretool_standard_capture_boundary",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Create the requested one-line file, read it back, and report done.",
                    transcript_path=str(pretool_transcript_path),
                ),
                _stop_payload(
                    hook_event_name="PreToolUse",
                    last_assistant_message=None,
                    tool_name="Bash",
                    tool_input={"command": "printf 'done\\n' > file.txt"},
                    transcript_path=str(pretool_transcript_path),
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "live_equivalent_pretool_standard_capture_boundary.client.jsonl",
            trajectory_path=trajectory_path,
            enable_task_standard_text=True,
        ),
        _run_sequence_case(
            case_id="malformed_standard_stays_diagnostic_only",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Create the requested one-line file, read it back, and report done.",
                ),
                _stop_payload(last_assistant_message=malformed_standard_block),
            ),
            state_root=state_root,
            diagnostics_path=root / "malformed_standard_stays_diagnostic_only.client.jsonl",
            trajectory_path=trajectory_path,
            enable_task_standard_text=True,
        ),
    ]

    root_config_hash_after = _file_hash(root_config)
    by_case = {case["case_id"]: case for case in cases}
    context_case = by_case["context_delivery_and_standard_capture"]
    malformed_case = by_case["malformed_standard_stays_diagnostic_only"]
    context_step = context_case["steps"][0]
    capture_step = context_case["steps"][-1]
    pretool_case = by_case["live_equivalent_pretool_standard_capture_boundary"]
    pretool_final = pretool_case["steps"][-1]
    malformed_final = malformed_case["steps"][-1]
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_task_standard_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        ),
        "subject_config_enables_task_standard_text": (
            "--enable-task-standard-text" in subject_config_text
        ),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "no_runtime_snapshot_fixture": all(
            step["runtime_snapshot_path"] is None
            for case in cases
            for step in case["steps"]
        ),
    }
    case_results = {
        "context_emits_exact_signed_text": context_step["stdout_payload"]
        == _task_standard_context_payload(),
        "standard_block_captured": capture_step["task_standard_standard_item_count"] == 3
        and capture_step["task_standard_malformed_standard_block_count"] == 0,
        "live_equivalent_pretool_transcript_standard_captured": (
            pretool_final["hook_event_name"] == "PreToolUse"
            and pretool_final["task_standard_standard_item_count"] == 3
            and pretool_final["stdout_payload"] is None
            and any(
                "pretool-transcript-standard" in ref
                for ref in pretool_final["task_standard_standard_item_source_refs"]
            )
        ),
        "pretool_capture_happens_before_tool_evidence": (
            pretool_final["task_standard_standard_item_count"] == 3
            and pretool_final["task_standard_evidence_ref_count"] == 0
            and pretool_final["stdout_payload"] is None
        ),
        "malformed_standard_diagnostic_only": (
            malformed_final["stdout_payload"] is None
            and malformed_final["task_standard_standard_item_count"] == 0
            and malformed_final["task_standard_malformed_standard_block_count"] == 1
            and malformed_final["directive_action"] == "stay_silent"
        ),
        "no_unexpected_model_visible_text": all(
            step["stdout_payload"] is None
            or step["stdout_payload"] == _task_standard_context_payload()
            for case in cases
            for step in case["steps"]
        ),
    }
    report: dict[str, object] = {
        "probe": "codex_app_cli_task_standard_live_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_task_standard_context_and_capture_gate0",
        "passed": all(case_results.values()) and all(boundary_results.values()),
        "case_results": case_results,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "context_hash": _hash_text(TASK_STANDARD_FORMATION_TEXT),
        "boundary_evidence_ladder": {
            "host_stdout_contract_ok": case_results["context_emits_exact_signed_text"],
            "host_attached_context_observed": False,
            "model_assimilation_observed": case_results[
                "live_equivalent_pretool_transcript_standard_captured"
            ],
            "state_capture_observed": (
                case_results["standard_block_captured"]
                and case_results["live_equivalent_pretool_transcript_standard_captured"]
            ),
            "gate_used_captured_state": False,
            "behavior_lift_claim_allowed": False,
        },
        "capture_boundary_result": {
            "live_equivalent_pretool_transcript_path": str(pretool_transcript_path),
            "pretool_standard_capture_observed": case_results[
                "live_equivalent_pretool_transcript_standard_captured"
            ],
            "pretool_standard_capture_source_refs": pretool_final[
                "task_standard_standard_item_source_refs"
            ],
            "reason": (
                "Gate 0 captures the model-authored standard from a "
                "live-equivalent PreToolUse transcript before any tool evidence "
                "is scored."
            ),
        },
        "standard_capture_item_count": pretool_final[
            "task_standard_standard_item_count"
        ],
        "malformed_standard_block_count": malformed_final[
            "task_standard_malformed_standard_block_count"
        ],
        "live_probe_ran": False,
        "truth_boundary": (
            "This Gate 0 uses simulated Codex lifecycle payloads to prove the "
            "signed-off task-standard context and standard-capture path. It "
            "does not prove live Codex delivery, behavior lift, or output quality."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_task_standard_pretool_transcript_replay(
    *,
    output_root: Path | str = TASK_STANDARD_LIVE_OUTPUT_ROOT,
    artifact_root: Path | str | None = None,
) -> dict[str, object]:
    root = Path(output_root) / "task_standard_pretool_transcript_replay"
    state_root = root / "state"
    trajectory_path = root / "trajectory.jsonl"
    report_path = root / "report.json"
    root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(parents=True, exist_ok=True)
    trajectory_path.write_text("", encoding="utf-8")

    source_artifact_root = (
        Path(artifact_root)
        if artifact_root is not None
        else _latest_task_standard_live_artifact_root()
    )
    report_payload = _json_object(source_artifact_root / "report.json")
    hook_rows = _jsonl_rows(source_artifact_root / "hook_client_diagnostics.jsonl")
    transcript_path = _first_transcript_path_from_hook_rows(hook_rows)
    transcript_text = ""
    if transcript_path is not None and transcript_path.is_file():
        transcript_text = transcript_path.read_text(encoding="utf-8", errors="replace")
    prompt_value = report_payload.get("prompt")
    prompt = prompt_value if isinstance(prompt_value, str) and prompt_value else (
        TASK_STANDARD_LIVE_PROMPT
    )

    cases: list[dict[str, object]] = []
    if transcript_path is not None:
        cases.append(
            _run_sequence_case(
                case_id="pretool_transcript_replay",
                payloads=(
                    _stop_payload(
                        hook_event_name="UserPromptSubmit",
                        prompt=prompt,
                        transcript_path=str(transcript_path),
                    ),
                    _stop_payload(
                        hook_event_name="PreToolUse",
                        last_assistant_message=None,
                        tool_name="Bash",
                        tool_input={"command": "printf replay\\n > replay.txt"},
                        transcript_path=str(transcript_path),
                    ),
                ),
                state_root=state_root,
                diagnostics_path=root / "pretool_transcript_replay.client.jsonl",
                trajectory_path=trajectory_path,
                enable_task_standard_text=True,
            )
        )

    replay_final = cases[0]["steps"][-1] if cases else {}
    source_context_observed = any(
        row.get("stdout_payload") == _task_standard_context_payload()
        for row in hook_rows
    )
    pretool_capture_observed = bool(
        replay_final.get("task_standard_standard_item_count") == 3
        and replay_final.get("task_standard_evidence_ref_count") == 0
        and any(
            "pretool-transcript-standard" in ref
            for ref in replay_final.get(
                "task_standard_standard_item_source_refs",
                [],
            )
            if isinstance(ref, str)
        )
    )
    boundary_evidence_ladder = _task_standard_live_boundary_ladder(
        context_observed=source_context_observed,
        stdout_text="",
        transcript_text=transcript_text,
        state_capture_observed=pretool_capture_observed,
        prework_standard_capture=pretool_capture_observed,
    )
    report = {
        "probe": "codex_app_cli_task_standard_pretool_transcript_replay",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "replay_task_standard_pretool_transcript_capture",
        "passed": bool(
            source_artifact_root.exists()
            and transcript_path is not None
            and pretool_capture_observed
            and not boundary_evidence_ladder["gate_used_captured_state"]
            and not boundary_evidence_ladder["behavior_lift_claim_allowed"]
        ),
        "source_artifact_root": str(source_artifact_root),
        "source_transcript_path": str(transcript_path) if transcript_path else None,
        "source_context_observed": source_context_observed,
        "source_transcript_standard_labels_observed": _standard_block_labels_observed(
            transcript_text
        ),
        "pretool_standard_capture_observed": pretool_capture_observed,
        "standard_capture_item_count": replay_final.get(
            "task_standard_standard_item_count",
            0,
        ),
        "standard_capture_source_refs": replay_final.get(
            "task_standard_standard_item_source_refs",
            [],
        ),
        "state_capture_observed": pretool_capture_observed,
        "gate_used_captured_state": False,
        "behavior_lift_claim_allowed": False,
        "boundary_evidence_ladder": boundary_evidence_ladder,
        "output_root": str(root),
        "trajectory_path": str(trajectory_path),
        "truth_boundary": (
            "This replay reuses existing Codex transcript artifacts to prove "
            "TaskStandardSpine can now ingest a model-authored pre-tool standard "
            "without live spend. It does not prove behavior lift or later gate use."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_task_standard_stop_gating_gate0_probe(
    *,
    output_root: Path | str = TASK_STANDARD_STOP_GATING_OUTPUT_ROOT,
) -> dict[str, object]:
    root = Path(output_root) / "task_standard_stop_gating_gate0"
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
        hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        enable_task_standard_text=True,
    )
    subject_config_text = subject_config.read_text(encoding="utf-8")

    standard_block = _task_standard_stop_gating_standard_block()
    clean_transcript_path = root / "clean_evidenced_closure_transcript.jsonl"
    gap_transcript_path = root / "premature_closure_gap_transcript.jsonl"
    _write_standard_transcript(clean_transcript_path, standard_block)
    _write_standard_transcript(gap_transcript_path, standard_block)

    clean_command = "printf 'task standard live done\\n' > result.txt && cat result.txt"
    cases = [
        _run_sequence_case(
            case_id="premature_closure_gap",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt=(
                        "Use shell commands to create result.txt containing task "
                        "standard live done, read it back, and report done."
                    ),
                    transcript_path=str(gap_transcript_path),
                ),
                _stop_payload(
                    hook_event_name="PreToolUse",
                    transcript_path=str(gap_transcript_path),
                    last_assistant_message=None,
                    tool_name="Bash",
                    tool_input={"command": "printf 'task standard live done\\n' > result.txt"},
                ),
                _stop_payload(
                    hook_event_name="Stop",
                    transcript_path=str(gap_transcript_path),
                    last_assistant_message="Created result.txt and done.",
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "premature_closure_gap.client.jsonl",
            trajectory_path=trajectory_path,
            enable_task_standard_text=True,
        ),
        _run_sequence_case(
            case_id="clean_evidenced_closure",
            payloads=(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt=(
                        "Use shell commands to create result.txt containing task "
                        "standard live done, read it back, and report done."
                    ),
                    transcript_path=str(clean_transcript_path),
                ),
                _stop_payload(
                    hook_event_name="PreToolUse",
                    transcript_path=str(clean_transcript_path),
                    last_assistant_message=None,
                    tool_name="Bash",
                    tool_input={"command": clean_command},
                ),
                _stop_payload(
                    hook_event_name="PostToolUse",
                    transcript_path=str(clean_transcript_path),
                    last_assistant_message=None,
                    tool_name="Bash",
                    tool_input={"command": clean_command},
                    tool_response={
                        "exit_code": 0,
                        "aggregated_output": "task standard live done\n",
                    },
                ),
                _stop_payload(
                    hook_event_name="Stop",
                    transcript_path=str(clean_transcript_path),
                    last_assistant_message=(
                        "Read back from result.txt: task standard live done.\n\ndone"
                    ),
                ),
            ),
            state_root=state_root,
            diagnostics_path=root / "clean_evidenced_closure.client.jsonl",
            trajectory_path=trajectory_path,
            enable_task_standard_text=True,
        ),
    ]
    replay_case = _run_task_standard_stop_gating_live_capture_replay(
        root=root,
        state_root=state_root,
        trajectory_path=trajectory_path,
    )
    if replay_case is not None:
        cases.append(replay_case)

    root_config_hash_after = _file_hash(root_config)
    by_case = {case["case_id"]: case for case in cases}
    gap = by_case["premature_closure_gap"]
    clean = by_case["clean_evidenced_closure"]
    replay = by_case.get("latest_live_capture_replay", {})

    gap_blocks = _case_blocks_with_expected_text(gap)
    clean_silent = _case_stays_silent_with_resolved_pressure(clean)
    clean_overblock = _case_blocks(clean)
    clean_underblock = not gap_blocks
    replay_overblock = _case_blocks(replay) if replay else True
    replay_silent = _case_stays_silent_with_resolved_pressure(replay) if replay else False
    replay_missing = replay_case is None
    final_gap = gap["steps"][-1]
    final_clean = clean["steps"][-1]
    final_replay = replay["steps"][-1] if replay else {}

    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        ),
        "subject_config_enables_task_standard_text": (
            "--enable-task-standard-text" in subject_config_text
        ),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "subject_config_does_not_suppress_stop_blocks": (
            "--disable-stop-blocks" not in subject_config_text
            and "--disable-model-visible-blocks" not in subject_config_text
        ),
        "no_runtime_snapshot_fixture": all(
            step["runtime_snapshot_path"] is None
            for case in cases
            for step in case["steps"]
        ),
        "no_unexpected_model_visible_text": all(
            _step_has_allowed_task_standard_stop_gating_stdout(
                step,
                allow_block=case["case_id"] == "premature_closure_gap",
            )
            for case in cases
            for step in case["steps"]
        ),
    }
    case_results = {
        "premature_closure_gap_blocks": gap_blocks,
        "clean_evidenced_closure_stays_silent": clean_silent,
        "latest_live_capture_replay_available": not replay_missing,
        "latest_live_capture_replay_does_not_overblock": replay_silent,
    }
    if not all(boundary_results.values()):
        verdict = "fail"
    elif clean_overblock or replay_overblock:
        verdict = "failure_overblock"
    elif clean_underblock:
        verdict = "failure_underblock"
    elif all(case_results.values()):
        verdict = "pass_gating_calibrated"
    else:
        verdict = "fail"

    report: dict[str, object] = {
        "probe": "codex_app_cli_task_standard_stop_gating_gate0",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "structural_task_standard_stop_gating_calibration",
        "passed": verdict == "pass_gating_calibrated",
        "verdict": verdict,
        "case_results": case_results,
        "boundary_results": boundary_results,
        "output_root": str(root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "trajectory_path": str(trajectory_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "configured_hook_events": list(TASK_STANDARD_LIVE_HOOK_EVENTS),
        "context_hash": _hash_text(TASK_STANDARD_FORMATION_TEXT),
        "captured_standard_ids": final_gap.get("task_standard_standard_item_ids", []),
        "gap_unmatched_standard_item_ids": final_gap.get(
            "task_standard_unmatched_standard_item_ids",
            [],
        ),
        "clean_evidence_item_ids": final_clean.get(
            "task_standard_evidence_item_ids",
            [],
        ),
        "clean_unmatched_standard_item_ids": final_clean.get(
            "task_standard_unmatched_standard_item_ids",
            [],
        ),
        "stop_stdout_payload": final_gap.get("stdout_payload"),
        "rendered_text_hash": final_gap.get("actual_rendered_text_hash"),
        "overblock_detection": {
            "clean_control_overblock": clean_overblock,
            "latest_live_capture_replay_overblock": replay_overblock,
            "latest_live_capture_replay_missing": replay_missing,
            "latest_live_capture_replay_source": str(
                _task_standard_stop_gating_replay_artifact_root()
            ),
            "latest_live_capture_replay_unmatched_standard_item_ids": final_replay.get(
                "task_standard_unmatched_standard_item_ids",
                [],
            ),
            "failure_reason": (
                "clean_or_replayed_capture_would_block"
                if clean_overblock or replay_overblock
                else None
            ),
        },
        "boundary_evidence_ladder": {
            "host_stdout_contract_ok": any(
                step["stdout_payload"] == _task_standard_context_payload()
                for case in cases
                for step in case["steps"]
            ),
            "host_attached_context_observed": False,
            "model_assimilation_observed": all(
                case["steps"][-1]["task_standard_standard_item_count"] == 3
                for case in cases
            ),
            "state_capture_observed": all(
                case["steps"][-1]["task_standard_standard_item_count"] == 3
                for case in cases
            ),
            "gate_used_captured_state": gap_blocks and clean_silent,
            "behavior_lift_claim_allowed": False,
        },
        "live_probe_ran": False,
        "truth_boundary": (
            "This Gate 0 calibrates whether captured task standards can drive "
            "Stop gating in simulated lifecycle trajectories and replayed live "
            "capture evidence. It does not run a live model, prove behavior "
            "lift, or change the signed task-standard or Stop text."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_task_standard_stop_gating_live_probe(
    *,
    output_root: Path | str = TASK_STANDARD_STOP_GATING_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(TASK_STANDARD_STOP_GATING_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_task_standard_stop_gating_live_probe",
            "passed": False,
            "verdict": "not_run",
            "live_probe_ran": False,
            "scoped_negative": None,
            "blocked_reason": (
                "task_standard_stop_gating_live_requires_explicit_current_turn_approval"
            ),
            "approval_env": TASK_STANDARD_STOP_GATING_APPROVAL_ENV,
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
        hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        enable_task_standard_text=True,
    )
    command = [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        TASK_STANDARD_STOP_GATING_LIVE_PROMPT,
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_task_standard_stop_gating_live_probe",
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
    context_rows = [
        row
        for row in trajectory_rows
        if row.get("hook_event_name") == "UserPromptSubmit"
        and row.get("stdout_payload") == _task_standard_context_payload()
    ]
    block_rows = [
        row
        for row in trajectory_rows
        if isinstance(row.get("stdout_payload"), Mapping)
        and row["stdout_payload"].get("decision") == "block"
    ]
    stop_rows = [
        row for row in trajectory_rows if row.get("hook_event_name") == "Stop"
    ]
    runtime_snapshot_rows = [
        row for row in trajectory_rows if row.get("runtime_snapshot_loaded") is True
    ]
    standard_capture_rows = [
        row
        for row in trajectory_rows
        if _task_standard_count(row, "task_standard_standard_item_count") >= 3
    ]
    final_stop = stop_rows[-1] if stop_rows else {}
    clean_silence = bool(
        final_stop
        and final_stop.get("stdout_payload") is None
        and final_stop.get("silence_reason") == "pressure_below_visible_threshold"
        and not final_stop.get("task_standard_unmatched_standard_item_ids")
    )
    stop_block = bool(
        block_rows
        and block_rows[0].get("stdout_payload")
        == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
    )
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        ),
        "subject_config_enables_task_standard_text": (
            "--enable-task-standard-text"
            in subject_config.read_text(encoding="utf-8")
        ),
        "subject_config_omits_runtime_snapshot": (
            "--runtime-snapshot" not in subject_config.read_text(encoding="utf-8")
        ),
        "subject_config_does_not_suppress_stop_blocks": (
            "--disable-stop-blocks" not in subject_config.read_text(encoding="utf-8")
            and "--disable-model-visible-blocks"
            not in subject_config.read_text(encoding="utf-8")
        ),
        "hook_rows_do_not_load_runtime_snapshot": not runtime_snapshot_rows,
    }
    scoped_negative = None
    failure_reason = None
    if not hook_rows:
        scoped_negative = "codex_cli_project_hooks_not_loaded_or_not_trusted"
    elif runtime_snapshot_rows:
        failure_reason = "runtime_snapshot_loaded_in_task_standard_stop_gating_probe"
    elif not all(boundary_results.values()):
        failure_reason = "boundary_check_failed"
    elif not context_rows:
        scoped_negative = "codex_context_payload_not_delivered_or_not_recorded"
    elif not standard_capture_rows:
        scoped_negative = "codex_lifecycle_payloads_insufficient_for_standard_capture"
    elif stop_block:
        verdict = "pass_gating_observed"
    elif clean_silence:
        verdict = "pass_clean_silence_observed"
    elif final_stop and final_stop.get("stdout_payload") is not None:
        verdict = "failure_overblock"
    elif final_stop:
        verdict = "scoped_negative"
        scoped_negative = "stop_gating_not_exercised_by_live_clean_task"
    else:
        scoped_negative = "codex_stop_payload_missing"
    if scoped_negative is not None:
        verdict = "scoped_negative"
    elif failure_reason is not None:
        verdict = "fail"

    report = {
        "probe": "codex_app_cli_task_standard_stop_gating_live_probe",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_task_standard_stop_gating_calibration",
        "passed": verdict in {"pass_gating_observed", "pass_clean_silence_observed"},
        "verdict": verdict,
        "live_probe_ran": True,
        "scoped_negative": scoped_negative,
        "failure_reason": failure_reason,
        "model": model,
        "output_root": str(run_root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "configured_hook_events": list(TASK_STANDARD_LIVE_HOOK_EVENTS),
        "command": command,
        "prompt": TASK_STANDARD_STOP_GATING_LIVE_PROMPT,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "standard_capture_rows": len(standard_capture_rows),
        "stop_rows": len(stop_rows),
        "block_rows": len(block_rows),
        "boundary_results": boundary_results,
        "diagnostics_path": str(diagnostics_path),
        "trajectory_path": str(trajectory_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "truth_boundary": (
            "This live probe can show live Stop gating or clean silence from "
            "captured standards. It does not prove output-quality lift or broad "
            "behavior improvement."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def run_task_standard_live_probe(
    *,
    output_root: Path | str = TASK_STANDARD_LIVE_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(TASK_STANDARD_LIVE_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_task_standard_live_probe",
            "passed": False,
            "verdict": "not_run",
            "live_probe_ran": False,
            "scoped_negative": None,
            "blocked_reason": (
                "task_standard_live_requires_explicit_current_turn_approval"
            ),
            "approval_env": TASK_STANDARD_LIVE_APPROVAL_ENV,
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
        hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        disable_stop_blocks=True,
        enable_task_standard_text=True,
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
        TASK_STANDARD_LIVE_PROMPT,
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_task_standard_live_probe",
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
    stop_rows = [
        row for row in trajectory_rows if row.get("hook_event_name") == "Stop"
    ]
    runtime_snapshot_rows = [
        row for row in trajectory_rows if row.get("runtime_snapshot_loaded") is True
    ]
    context_rows = [
        row
        for row in prompt_rows
        if row.get("stdout_payload") == _task_standard_context_payload()
    ]
    unexpected_text_rows = [
        row
        for row in trajectory_rows
        if row.get("stdout_payload") is not None
        and row.get("stdout_payload") != _task_standard_context_payload()
    ]
    first_tool_index = min(
        (
            row["row_index"]
            for row in tool_rows
            if isinstance(row.get("row_index"), int)
        ),
        default=None,
    )
    standard_capture_rows = [
        row
        for row in trajectory_rows
        if _task_standard_count(row, "task_standard_standard_item_count") >= 3
    ]
    first_standard_capture_index = min(
        (
            row["row_index"]
            for row in standard_capture_rows
            if isinstance(row.get("row_index"), int)
        ),
        default=None,
    )
    first_standard_capture_row = next(
        (
            row
            for row in standard_capture_rows
            if row.get("row_index") == first_standard_capture_index
        ),
        {},
    )
    prework_standard_capture = bool(
        isinstance(first_standard_capture_index, int)
        and (
            not isinstance(first_tool_index, int)
            or first_standard_capture_index < first_tool_index
            or (
                first_standard_capture_index == first_tool_index
                and _row_has_pretool_transcript_standard_capture(
                    first_standard_capture_row
                )
            )
        )
    )
    stdout_text = completed.stdout
    transcript_text = _transcript_text_from_hook_rows(hook_rows)
    boundary_evidence_ladder = _task_standard_live_boundary_ladder(
        context_observed=bool(context_rows),
        stdout_text=stdout_text,
        transcript_text=transcript_text,
        state_capture_observed=bool(standard_capture_rows),
        prework_standard_capture=prework_standard_capture,
    )
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_task_standard_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=TASK_STANDARD_LIVE_HOOK_EVENTS,
        ),
        "subject_config_enables_task_standard_text": (
            "--enable-task-standard-text" in subject_config_text
        ),
        "subject_config_omits_runtime_snapshot": "--runtime-snapshot" not in subject_config_text,
        "subject_config_disables_stop_blocks_only": (
            "--disable-stop-blocks" in subject_config_text
            and "--disable-model-visible-blocks" not in subject_config_text
        ),
        "subject_isolated_git_root": _git_root(subject) == subject,
        "hook_rows_do_not_load_runtime_snapshot": not runtime_snapshot_rows,
    }

    scoped_negative = None
    failure_reason = None
    if not hook_rows:
        scoped_negative = "codex_cli_project_hooks_not_loaded_or_not_trusted"
    elif runtime_snapshot_rows:
        failure_reason = "runtime_snapshot_loaded_in_task_standard_live_probe"
    elif not all(boundary_results.values()):
        failure_reason = "boundary_check_failed"
    elif unexpected_text_rows:
        failure_reason = "unexpected_model_visible_text"
    elif not prompt_rows:
        scoped_negative = "codex_hook_payloads_missing_user_prompt_submit"
    elif not context_rows:
        scoped_negative = "codex_context_payload_not_delivered_or_not_recorded"
    elif prework_standard_capture:
        verdict = "pass_prework_standard_capture"
    elif standard_capture_rows:
        verdict = "partial_delivery_only"
    elif stop_rows or tool_rows:
        verdict = "partial_delivery_only"
    else:
        scoped_negative = "codex_lifecycle_payloads_insufficient_for_standard_capture"
    if scoped_negative is not None:
        verdict = "scoped_negative"
    elif failure_reason is not None:
        verdict = "fail"
    mechanical_success = verdict in {
        "pass_prework_standard_capture",
        "partial_delivery_only",
    }
    product_evidence_success = verdict == "pass_prework_standard_capture"
    partial_evidence_only = verdict == "partial_delivery_only"

    report = {
        "probe": "codex_app_cli_task_standard_live_probe",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_task_standard_context_and_capture_probe",
        "passed": product_evidence_success,
        "mechanical_success": mechanical_success,
        "product_evidence_success": product_evidence_success,
        "partial_evidence_only": partial_evidence_only,
        "verdict": verdict,
        "live_probe_ran": True,
        "scoped_negative": scoped_negative,
        "failure_reason": failure_reason,
        "model": model,
        "output_root": str(run_root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "configured_hook_events": list(TASK_STANDARD_LIVE_HOOK_EVENTS),
        "command": command,
        "prompt": TASK_STANDARD_LIVE_PROMPT,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "prompt_rows": len(prompt_rows),
        "tool_rows": len(tool_rows),
        "stop_rows": len(stop_rows),
        "context_rows": len(context_rows),
        "standard_capture_rows": len(standard_capture_rows),
        "first_tool_index": first_tool_index,
        "first_standard_capture_index": first_standard_capture_index,
        "prework_standard_capture": prework_standard_capture,
        "unexpected_text_rows": len(unexpected_text_rows),
        "boundary_results": boundary_results,
        "boundary_evidence_ladder": boundary_evidence_ladder,
        "context_hash": _hash_text(TASK_STANDARD_FORMATION_TEXT),
        "diagnostics_path": str(diagnostics_path),
        "trajectory_path": str(trajectory_path),
        "stdout_path": str(stdout_path),
        "stdout_hash": _hash_text(completed.stdout),
        "stdout_tail_excerpt": completed.stdout[-1000:],
        "stderr_path": str(stderr_path),
        "stderr_hash": _hash_text(completed.stderr),
        "root_config_hash_before": root_config_hash_before,
        "root_config_hash_after": root_config_hash_after,
        "truth_boundary": (
            "This live probe tests signed-off task-standard context delivery "
            "and product-visible standard capture only. It does not prove "
            "output-quality lift, behavior lift, task-standard integration into "
            "later gates, Codex App parity, or shipping promotion."
        ),
    }
    report_path.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
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


def run_stop_continuation_resolution_live_probe(
    *,
    output_root: Path | str = STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT,
    model: str = "gpt-5.3-codex",
) -> dict[str, object]:
    if os.environ.get(STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV) != "approved":
        return {
            "probe": "codex_app_cli_stop_continuation_resolution_loop",
            "passed": False,
            "verdict": "not_run",
            "live_probe_ran": False,
            "scoped_negative": None,
            "blocked_reason": (
                "stop_continuation_resolution_live_requires_explicit_current_turn_approval"
            ),
            "approval_env": STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV,
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
        hook_events=STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
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
        STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT,
    ]
    if not _command_available("codex"):
        report = {
            "probe": "codex_app_cli_stop_continuation_resolution_loop",
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
    first_block_index = (
        exact_block_rows[0].get("row_index")
        if exact_block_rows and isinstance(exact_block_rows[0].get("row_index"), int)
        else None
    )
    continuation_tool_rows = [
        row
        for row in tool_rows
        if isinstance(first_block_index, int)
        and isinstance(row.get("row_index"), int)
        and row["row_index"] > first_block_index
    ]
    final_stop_row = stop_rows[-1] if stop_rows else {}
    final_silence_reason = (
        final_stop_row.get("silence_reason")
        if isinstance(final_stop_row, Mapping)
        else None
    )
    final_active_expectation_ids = (
        final_stop_row.get("active_expectation_ids")
        if isinstance(final_stop_row, Mapping)
        and isinstance(final_stop_row.get("active_expectation_ids"), list)
        else []
    )
    final_resolved_expectation_ids = (
        final_stop_row.get("resolved_expectation_ids")
        if isinstance(final_stop_row, Mapping)
        and isinstance(final_stop_row.get("resolved_expectation_ids"), list)
        else []
    )
    verification_evidence_observed = any(
        _state_int(row, "verification_evidence_count") > 0 for row in trajectory_rows
    )
    lifecycle_state_persisted = any(
        bool(row.get("session_state")) for row in trajectory_rows
    )
    boundary_results = {
        "root_config_unchanged": root_config_hash_before == root_config_hash_after,
        "subject_config_product_hook_only": _subject_config_is_product_only(
            subject_config,
            expected_hook_events=STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
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
        failure_reason = "runtime_snapshot_loaded_in_stop_continuation_resolution_probe"
    elif non_stop_stdout_rows:
        failure_reason = "non_stop_hook_emitted_model_visible_stdout"
    elif len(block_rows) > 1:
        failure_reason = "repeated_stop_block_loop"
    elif not all(boundary_results.values()):
        failure_reason = "boundary_check_failed"
    elif not stop_rows:
        scoped_negative = "codex_hook_payloads_missing_stop_event"
    elif set(hook_event_counts) == {"Stop"}:
        scoped_negative = "codex_cli_live_hooks_stop_only_in_continuation_probe"
    elif not exact_block_rows:
        failure_reason = "first_stop_did_not_emit_exact_product_block"
    elif not continuation_tool_rows:
        scoped_negative = "continuation_tool_payloads_not_captured_after_block"
    elif (
        final_silence_reason == "pressure_below_visible_threshold"
        and not final_active_expectation_ids
        and final_resolved_expectation_ids
    ):
        verdict = "pass_resolved"
    elif (
        final_silence_reason == "stop_hook_active_unresolved_verification_expectation"
        and final_active_expectation_ids
    ):
        verdict = "pass_preserved_open"
    elif lifecycle_complete:
        verdict = "fail"
        failure_reason = "continuation_resolution_state_inconclusive"
    else:
        scoped_negative = "continuation_lifecycle_incomplete"
    if scoped_negative is not None:
        verdict = "scoped_negative"
    elif failure_reason is not None:
        verdict = "fail"

    report = {
        "probe": "codex_app_cli_stop_continuation_resolution_loop",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "live_stop_continuation_resolution_probe",
        "passed": verdict in {"pass_resolved", "pass_preserved_open"},
        "verdict": verdict,
        "live_probe_ran": True,
        "scoped_negative": scoped_negative,
        "failure_reason": failure_reason,
        "model": model,
        "output_root": str(run_root),
        "subject_workspace": str(subject),
        "subject_config_path": str(subject_config),
        "configured_hook_events": list(STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS),
        "command": command,
        "prompt": STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT,
        "exit_code": completed.returncode,
        "hook_rows": len(hook_rows),
        "hook_event_counts": hook_event_counts,
        "prompt_rows": len(prompt_rows),
        "tool_rows": len(tool_rows),
        "continuation_tool_rows": len(continuation_tool_rows),
        "stop_rows": len(stop_rows),
        "block_rows": len(block_rows),
        "exact_block_rows": len(exact_block_rows),
        "non_stop_stdout_rows": len(non_stop_stdout_rows),
        "verification_evidence_observed": verification_evidence_observed,
        "lifecycle_state_persisted": lifecycle_state_persisted,
        "final_silence_reason": final_silence_reason,
        "final_active_expectation_ids": final_active_expectation_ids,
        "final_resolved_expectation_ids": final_resolved_expectation_ids,
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
            "This live probe tests whether a Codex App/CLI post-block "
            "continuation can resolve or preserve an open verification "
            "expectation from product-observable hook events. It does not prove "
            "behavior lift, and it does not use runtime snapshots, hidden "
            "verifiers, fixture continuation prompts, or task identity."
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
    enable_task_standard_text: bool = False,
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
    if enable_task_standard_text:
        command.append("--enable-task-standard-text")
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
    hook_payload = (
        coordinator.get("hook_payload", {}) if isinstance(coordinator, Mapping) else {}
    )
    if not isinstance(hook_payload, Mapping):
        hook_payload = {}
    session_state = (
        coordinator.get("session_state", {}) if isinstance(coordinator, Mapping) else {}
    )
    if not isinstance(session_state, Mapping):
        session_state = {}
    row = {
        "case_id": case_id,
        "payload": payload if isinstance(payload, Mapping) else {"raw": payload},
        "payload_hash": _hash_text(input_text),
        "hook_event_name": hook_payload.get("hook_event_name"),
        "stop_hook_active": hook_payload.get("stop_hook_active"),
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
        "active_expectation_ids": _expectation_ids(session_state, "active"),
        "resolved_expectation_ids": _expectation_ids(session_state, "resolved"),
        "expectation_evidence_refs": _expectation_evidence_refs(session_state),
        "task_standard_visible_obligation_count": _task_standard_count(
            session_state,
            "visible_task_obligations",
        ),
        "task_standard_standard_item_count": _task_standard_count(
            session_state,
            "standard_items",
        ),
        "task_standard_standard_item_ids": _task_standard_item_ids(
            session_state,
            "standard_items",
        ),
        "task_standard_standard_item_source_refs": _task_standard_source_refs(
            session_state,
            "standard_items",
        ),
        "task_standard_evidence_ref_count": _task_standard_count(
            session_state,
            "evidence_refs",
        ),
        "task_standard_evidence_item_ids": _task_standard_evidence_item_ids(
            session_state
        ),
        "task_standard_final_closure_claim_count": _task_standard_count(
            session_state,
            "final_closure_claims",
        ),
        "task_standard_unmatched_standard_item_ids": _task_standard_unmatched_ids(
            session_state
        ),
        "task_standard_malformed_standard_block_count": _task_standard_malformed_count(
            session_state
        ),
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
    enable_task_standard_text: bool = False,
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
            enable_task_standard_text=enable_task_standard_text,
        )
        for index, payload in enumerate(payloads, start=1)
    ]
    final = steps[-1] if steps else {}
    first_block = next(
        (
            step
            for step in steps
            if isinstance(step.get("stdout_payload"), Mapping)
            and step["stdout_payload"].get("decision") == "block"
        ),
        {},
    )
    row = {
        "case_id": case_id,
        "steps": steps,
        "first_stdout_payload": first_block.get("stdout_payload"),
        "first_actual_rendered_text_hash": first_block.get("actual_rendered_text_hash"),
        "final_stdout_payload": final.get("stdout_payload"),
        "final_silence_reason": final.get("silence_reason"),
        "final_actual_rendered_text_hash": final.get("actual_rendered_text_hash"),
        "final_active_expectation_ids": final.get("active_expectation_ids", []),
        "final_resolved_expectation_ids": final.get("resolved_expectation_ids", []),
        "final_expectation_evidence_refs": final.get("expectation_evidence_refs", []),
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
    disable_model_visible_blocks: bool = False,
    disable_stop_blocks: bool = False,
    enable_task_standard_text: bool = False,
    enable_posttooluse_task_standard_context: bool = False,
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
    if disable_model_visible_blocks:
        command_parts.append("--disable-model-visible-blocks")
    if disable_stop_blocks:
        command_parts.append("--disable-stop-blocks")
    if enable_task_standard_text:
        command_parts.append("--enable-task-standard-text")
    if enable_posttooluse_task_standard_context:
        command_parts.append("--enable-posttooluse-task-standard-context")
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


def _parse_stdout_payload(stdout: str) -> dict[str, object] | None:
    text = stdout.strip()
    if not text:
        return None
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        return None
    return {str(key): value for key, value in parsed.items()}


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


def _json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _task_standard_stop_gating_standard_block() -> str:
    return "\n".join(
        (
            "Work standard: create result.txt with exact content and read it back using cat.",
            "Likely misses: typo in filename or content, or reporting completion before readback.",
            "Closure evidence: cat command output shows task standard live done.",
        )
    )


def _write_standard_transcript(path: Path, standard_block: str) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": standard_block,
                        }
                    ],
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _case_blocks(case: Mapping[str, object]) -> bool:
    final_payload = case.get("final_stdout_payload")
    return bool(isinstance(final_payload, Mapping) and final_payload.get("decision") == "block")


def _case_blocks_with_expected_text(case: Mapping[str, object]) -> bool:
    return bool(
        case.get("final_stdout_payload")
        == {"decision": "block", "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT}
        and case.get("final_active_expectation_ids")
    )


def _case_stays_silent_with_resolved_pressure(case: Mapping[str, object]) -> bool:
    return bool(
        case.get("final_stdout_payload") is None
        and case.get("final_silence_reason") == "pressure_below_visible_threshold"
        and case.get("final_resolved_expectation_ids")
        and not case.get("final_active_expectation_ids")
        and not case.get("steps", [{}])[-1].get("task_standard_unmatched_standard_item_ids")
    )


def _step_has_allowed_task_standard_stop_gating_stdout(
    step: Mapping[str, object],
    *,
    allow_block: bool,
) -> bool:
    payload = step.get("stdout_payload")
    if payload is None or payload == _task_standard_context_payload():
        return True
    if allow_block:
        return payload == {
            "decision": "block",
            "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
        }
    return False


def _task_standard_stop_gating_replay_artifact_root() -> Path:
    pinned = TASK_STANDARD_LIVE_OUTPUT_ROOT / "run_20260505T213824Z"
    if pinned.exists():
        return pinned
    return _latest_task_standard_live_artifact_root()


def _run_task_standard_stop_gating_live_capture_replay(
    *,
    root: Path,
    state_root: Path,
    trajectory_path: Path,
) -> dict[str, object] | None:
    source_root = _task_standard_stop_gating_replay_artifact_root()
    if not source_root.exists():
        return None
    hook_rows = _jsonl_rows(source_root / "hook_client_diagnostics.jsonl")
    transcript_path = _first_transcript_path_from_hook_rows(hook_rows)
    stdout_rows = _jsonl_rows(source_root / "codex_stdout.jsonl")
    command_row = _first_codex_stdout_item(stdout_rows, item_type="command_execution")
    final_message = _last_codex_stdout_agent_message(stdout_rows)
    report_payload = _json_object(source_root / "report.json")
    prompt_value = report_payload.get("prompt")
    prompt = prompt_value if isinstance(prompt_value, str) and prompt_value else (
        TASK_STANDARD_LIVE_PROMPT
    )
    if transcript_path is None or not command_row or not final_message:
        return None
    command = command_row.get("command")
    if not isinstance(command, str) or not command:
        return None
    output = command_row.get("aggregated_output")
    if not isinstance(output, str):
        output = ""
    exit_code = command_row.get("exit_code")
    if not isinstance(exit_code, int):
        exit_code = 0
    return _run_sequence_case(
        case_id="latest_live_capture_replay",
        payloads=(
            _stop_payload(
                hook_event_name="UserPromptSubmit",
                prompt=prompt,
                transcript_path=str(transcript_path),
            ),
            _stop_payload(
                hook_event_name="PreToolUse",
                transcript_path=str(transcript_path),
                last_assistant_message=None,
                tool_name="Bash",
                tool_input={"command": command},
            ),
            _stop_payload(
                hook_event_name="PostToolUse",
                transcript_path=str(transcript_path),
                last_assistant_message=None,
                tool_name="Bash",
                tool_input={"command": command},
                tool_response={
                    "exit_code": exit_code,
                    "aggregated_output": output,
                },
            ),
            _stop_payload(
                hook_event_name="Stop",
                transcript_path=str(transcript_path),
                last_assistant_message=final_message,
            ),
        ),
        state_root=state_root,
        diagnostics_path=root / "latest_live_capture_replay.client.jsonl",
        trajectory_path=trajectory_path,
        enable_task_standard_text=True,
    )


def _first_codex_stdout_item(
    rows: list[dict[str, object]],
    *,
    item_type: str,
) -> dict[str, object]:
    for row in rows:
        item = row.get("item")
        if isinstance(item, Mapping) and item.get("type") == item_type:
            return {str(key): value for key, value in item.items()}
    return {}


def _last_codex_stdout_agent_message(rows: list[dict[str, object]]) -> str | None:
    message = None
    for row in rows:
        item = row.get("item")
        if not isinstance(item, Mapping):
            continue
        if item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                message = text.strip()
    return message


def _latest_task_standard_live_artifact_root() -> Path:
    if not TASK_STANDARD_LIVE_OUTPUT_ROOT.exists():
        return TASK_STANDARD_LIVE_OUTPUT_ROOT / "missing_live_artifact"
    candidates = [
        path
        for path in TASK_STANDARD_LIVE_OUTPUT_ROOT.iterdir()
        if path.is_dir()
        and path.name.startswith("run_")
        and (path / "report.json").exists()
        and (path / "hook_client_diagnostics.jsonl").exists()
    ]
    return sorted(candidates)[-1] if candidates else (
        TASK_STANDARD_LIVE_OUTPUT_ROOT / "missing_live_artifact"
    )


def _first_transcript_path_from_hook_rows(
    rows: list[dict[str, object]],
) -> Path | None:
    for row in rows:
        coordinator = row.get("coordinator")
        if not isinstance(coordinator, Mapping):
            continue
        hook_payload = coordinator.get("hook_payload")
        if not isinstance(hook_payload, Mapping):
            continue
        transcript_path_value = hook_payload.get("transcript_path")
        if isinstance(transcript_path_value, str) and transcript_path_value:
            return Path(transcript_path_value)
    return None


def _transcript_text_from_hook_rows(rows: list[dict[str, object]]) -> str:
    for row in rows:
        coordinator = row.get("coordinator")
        if not isinstance(coordinator, Mapping):
            continue
        hook_payload = coordinator.get("hook_payload")
        if not isinstance(hook_payload, Mapping):
            continue
        transcript_path_value = hook_payload.get("transcript_path")
        if not isinstance(transcript_path_value, str) or not transcript_path_value:
            continue
        transcript_path = Path(transcript_path_value)
        if transcript_path.is_file():
            return transcript_path.read_text(encoding="utf-8", errors="replace")
    return ""


def _task_standard_live_boundary_ladder(
    *,
    context_observed: bool,
    stdout_text: str,
    transcript_text: str,
    state_capture_observed: bool,
    prework_standard_capture: bool,
) -> dict[str, bool]:
    model_assimilation_observed = _standard_block_labels_observed(
        stdout_text
    ) or _standard_block_labels_observed(transcript_text)
    ladder = {
        "host_stdout_contract_ok": context_observed,
        "host_attached_context_observed": TASK_STANDARD_FORMATION_TEXT in transcript_text,
        "model_assimilation_observed": model_assimilation_observed,
        "state_capture_observed": state_capture_observed or prework_standard_capture,
        "gate_used_captured_state": False,
        "behavior_lift_claim_allowed": False,
    }
    return {key: bool(ladder.get(key, False)) for key in TASK_STANDARD_BOUNDARY_LADDER_KEYS}


def _standard_block_labels_observed(text: str) -> bool:
    return all(
        label in text
        for label in ("Work standard:", "Likely misses:", "Closure evidence:")
    )


def _row_has_pretool_transcript_standard_capture(row: Mapping[str, object]) -> bool:
    return bool(
        row.get("hook_event_name") == "PreToolUse"
        and any(
            "pretool-transcript-standard" in ref
            for ref in row.get("task_standard_standard_item_source_refs", [])
            if isinstance(ref, str)
        )
    )


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
                "tool_use_id": hook_payload.get("tool_use_id"),
                "tool_event_fingerprint": hook_payload.get("tool_event_fingerprint"),
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
                "active_expectation_ids": _expectation_ids(session_state, "active"),
                "resolved_expectation_ids": _expectation_ids(session_state, "resolved"),
                "expectation_evidence_refs": _expectation_evidence_refs(session_state),
                "task_standard_visible_obligation_count": _task_standard_count(
                    session_state,
                    "visible_task_obligations",
                ),
                "task_standard_standard_item_count": _task_standard_count(
                    session_state,
                    "standard_items",
                ),
                "task_standard_standard_item_ids": _task_standard_item_ids(
                    session_state,
                    "standard_items",
                ),
                "task_standard_standard_item_source_refs": _task_standard_source_refs(
                    session_state,
                    "standard_items",
                ),
                "task_standard_evidence_ref_count": _task_standard_count(
                    session_state,
                    "evidence_refs",
                ),
                "task_standard_evidence_item_ids": _task_standard_evidence_item_ids(
                    session_state
                ),
                "task_standard_final_closure_claim_count": _task_standard_count(
                    session_state,
                    "final_closure_claims",
                ),
                "task_standard_unmatched_standard_item_ids": _task_standard_unmatched_ids(
                    session_state
                ),
                "task_standard_malformed_standard_block_count": _task_standard_malformed_count(
                    session_state
                ),
                "directive_action": directive.get("action"),
                "silence_reason": directive.get("silence_reason"),
                "selection_trace": selection_trace,
                "perception_source": selection_trace.get("perception_source"),
                "stdout_payload": stdout_payload,
                "stdout_payload_hash": _stable_hash(stdout_payload)
                if isinstance(stdout_payload, Mapping)
                else None,
                "actual_rendered_text_hash": row.get("actual_rendered_text_hash"),
                "model_visible_blocks_disabled": row.get(
                    "model_visible_blocks_disabled"
                ),
                "suppressed_stdout_payload": row.get("suppressed_stdout_payload"),
                "suppressed_rendered_text_hash": row.get(
                    "suppressed_rendered_text_hash"
                ),
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


def _task_standard_count(row_or_state: Mapping[str, object], key: str) -> int:
    direct_value = row_or_state.get(key)
    if isinstance(direct_value, int):
        return direct_value
    spine = row_or_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        session_state = row_or_state.get("session_state")
        if isinstance(session_state, Mapping):
            spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return 0
    value = spine.get(key)
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int):
        return value
    return 0


def _task_standard_source_refs(
    row_or_state: Mapping[str, object],
    key: str,
) -> list[str]:
    spine = row_or_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        session_state = row_or_state.get("session_state")
        if isinstance(session_state, Mapping):
            spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return []
    value = spine.get(key)
    if not isinstance(value, list):
        return []
    refs: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        source_ref = item.get("source_event_ref")
        if isinstance(source_ref, str) and source_ref:
            refs.append(source_ref)
    return refs


def _task_standard_item_ids(
    row_or_state: Mapping[str, object],
    key: str,
) -> list[str]:
    spine = row_or_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        session_state = row_or_state.get("session_state")
        if isinstance(session_state, Mapping):
            spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return []
    value = spine.get(key)
    if not isinstance(value, list):
        return []
    ids: list[str] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        item_id = item.get("item_id")
        if isinstance(item_id, str) and item_id:
            ids.append(item_id)
    return ids


def _task_standard_evidence_item_ids(
    row_or_state: Mapping[str, object],
) -> list[str]:
    spine = row_or_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        session_state = row_or_state.get("session_state")
        if isinstance(session_state, Mapping):
            spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return []
    evidence_refs = spine.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        return []
    ids: list[str] = []
    for evidence in evidence_refs:
        if not isinstance(evidence, Mapping):
            continue
        item_ids = evidence.get("item_ids")
        if not isinstance(item_ids, list):
            continue
        ids.extend(item_id for item_id in item_ids if isinstance(item_id, str))
    return list(dict.fromkeys(ids))


def _task_standard_unmatched_ids(session_state: Mapping[str, object]) -> list[str]:
    spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return []
    value = spine.get("unmatched_standard_item_ids")
    if not isinstance(value, list):
        return []
    return [item_id for item_id in value if isinstance(item_id, str)]


def _task_standard_malformed_count(session_state: Mapping[str, object]) -> int:
    spine = session_state.get("task_standard_spine")
    if not isinstance(spine, Mapping):
        return 0
    value = spine.get("malformed_standard_block_count")
    return value if isinstance(value, int) else 0


def _expectation_ids(
    session_state: Mapping[str, object],
    bucket: str,
) -> list[str]:
    ledger = session_state.get("expectation_ledger")
    if not isinstance(ledger, Mapping):
        return []
    records = ledger.get(bucket)
    if not isinstance(records, list):
        return []
    return [
        record["expectation_id"]
        for record in records
        if isinstance(record, Mapping) and isinstance(record.get("expectation_id"), str)
    ]


def _expectation_evidence_refs(session_state: Mapping[str, object]) -> list[str]:
    ledger = session_state.get("expectation_ledger")
    if not isinstance(ledger, Mapping):
        return []
    refs: list[str] = []
    for bucket in ("active", "resolved"):
        records = ledger.get(bucket)
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, Mapping):
                continue
            evidence_refs = record.get("evidence_refs")
            if isinstance(evidence_refs, list):
                refs.extend(ref for ref in evidence_refs if isinstance(ref, str))
    return refs


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
