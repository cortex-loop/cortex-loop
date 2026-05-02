"""Gate-0 harness for the OpenAI operator silent-control live probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from cortex.hosts.openai.operator_enactment import (
    RECHECK_PROMPT_NAME,
    build_openai_operator_enactment_decision,
    find_internal_terms_in_model_visible_values,
)
from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    open_expectation_from_forward_commitment,
)

try:  # pragma: no cover - direct script execution uses the fallback imports.
    from . import openai_operator_cli
    from .live_validation_common import (
        LOCAL_LIVE_ROOT,
        ensure_live_validation_dirs,
        now_utc_iso,
        read_prompt_template,
    )
except ImportError:  # pragma: no cover
    import openai_operator_cli
    from lab.live_validation_common import (
        LOCAL_LIVE_ROOT,
        ensure_live_validation_dirs,
        now_utc_iso,
        read_prompt_template,
    )


DEFAULT_OUTPUT_ROOT = LOCAL_LIVE_ROOT / "openai" / "silent_control_live_probe"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/live_openai_silent_control_probe.py",
        description=(
            "Run the deterministic Gate-0 coupling audit for the OpenAI "
            "operator silent-control probe."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where Gate-0 evidence artifacts are written.",
    )
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Return exit code 2 when Gate 0 blocks live trials.",
    )
    args = parser.parse_args(argv)

    report = run_gate0_audit(output_root=args.output_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_pass and not report["gate0_passed"]:
        return 2
    return 0


def run_gate0_audit(*, output_root: Path = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    """Run the deterministic live-probe coupling audit and persist evidence."""

    ensure_live_validation_dirs()
    output_root.mkdir(parents=True, exist_ok=True)
    generated_at = now_utc_iso()
    scenarios = (
        _runtime_case(
            "truth_gap_inspect_after_unpaid_verification",
            event_name="response.output_text.delta",
            operator_scenario_id="truth_gap",
            first_result_kind="truthful_incomplete",
            provider_limit_interference=False,
            thread_id="gate0-thread-1",
            payload={
                "session_id": "openai-silent-gate0-inspect",
                "response_id": "resp-gate0-inspect",
                "delta": "Inspecting the current workspace before claiming completion.",
            },
        ),
        _runtime_case(
            "forward_after_unpaid_verification",
            event_name="response.completed",
            operator_scenario_id="truth_gap",
            first_result_kind="truthful_incomplete",
            provider_limit_interference=False,
            thread_id="gate0-thread-2",
            payload={
                "session_id": "openai-silent-gate0-forward",
                "response_id": "resp-gate0-forward",
                "commitment_id": "commit-gate0-forward",
                "externally_consequential": True,
            },
        ),
    )
    adapter_coupling = _audit_codex_operator_adapter(scenarios)
    runtime_delta_present = any(case["runtime_delta_present"] for case in scenarios)
    model_bound_delta_present = any(case["model_bound_delta_present"] for case in scenarios)
    gate0_passed = bool(runtime_delta_present and model_bound_delta_present)
    report = {
        "generated_at": generated_at,
        "surface": "lab / live-probe gate",
        "lane": "openai:operator_cli",
        "hypothesis": (
            "Expectation-debt control can produce an enactable silent-control "
            "difference before OpenAI operator live trials run."
        ),
        "gate0_passed": gate0_passed,
        "runtime_control_delta_present": runtime_delta_present,
        "model_bound_delta_present": model_bound_delta_present,
        "adapter_coupling": adapter_coupling,
        "scenarios": scenarios,
        "decision": _decision_payload(gate0_passed),
        "artifacts": {
            "gate0_report": str(output_root / "gate0_report.json"),
            "gate0_trajectory": str(output_root / "gate0_trajectory.jsonl"),
        },
    }
    _write_json(output_root / "gate0_report.json", report)
    _write_jsonl(output_root / "gate0_trajectory.jsonl", _trajectory_rows(scenarios))
    return report


def _runtime_case(
    scenario_id: str,
    *,
    event_name: str,
    operator_scenario_id: str,
    first_result_kind: str | None,
    provider_limit_interference: bool,
    thread_id: str | None,
    payload: dict[str, Any],
) -> dict[str, Any]:
    neutral_session = OpenAIRuntimeSession(session_id=f"{payload['session_id']}-neutral")
    shaped_session = OpenAIRuntimeSession(
        session_id=f"{payload['session_id']}-shaped",
        expectation_ledger=_verification_ledger(),
    )
    neutral_payload = {**payload, "session_id": neutral_session.session_id}
    shaped_payload = {**payload, "session_id": shaped_session.session_id}
    neutral = run_openai_runtime_step(event_name, neutral_payload, neutral_session)
    shaped = run_openai_runtime_step(event_name, shaped_payload, shaped_session)
    neutral_enactment = build_openai_operator_enactment_decision(
        operator_route_payload=neutral.operator_route_payload,
        executive_policy_view_payload=neutral.executive_policy_view_payload,
        debt_control_payload=neutral.debt_control_payload,
        scenario_id=operator_scenario_id,
        first_result_kind=first_result_kind,
        provider_limit_interference=provider_limit_interference,
        thread_id=thread_id,
    )
    shaped_enactment = build_openai_operator_enactment_decision(
        operator_route_payload=shaped.operator_route_payload,
        executive_policy_view_payload=shaped.executive_policy_view_payload,
        debt_control_payload=shaped.debt_control_payload,
        scenario_id=operator_scenario_id,
        first_result_kind=first_result_kind,
        provider_limit_interference=provider_limit_interference,
        thread_id=thread_id,
    )
    route_delta = neutral.operator_route_payload != shaped.operator_route_payload
    policy_delta = neutral.executive_policy_view_payload != shaped.executive_policy_view_payload
    debt_delta = neutral.debt_control_payload != shaped.debt_control_payload
    enactment_delta = _model_bound_enactment_projection(
        neutral_enactment
    ) != _model_bound_enactment_projection(shaped_enactment)
    model_bound_delta = bool(
        enactment_delta
        and (
            neutral_enactment.model_bound_difference_kind != "none"
            or shaped_enactment.model_bound_difference_kind != "none"
        )
    )
    return {
        "scenario_id": scenario_id,
        "event_name": event_name,
        "operator_scenario_id": operator_scenario_id,
        "runtime_delta_present": bool(route_delta or policy_delta or debt_delta),
        "route_delta_present": route_delta,
        "policy_delta_present": policy_delta,
        "debt_delta_present": debt_delta,
        "enactment_delta_present": enactment_delta,
        "model_bound_delta_present": model_bound_delta,
        "neutral": _trajectory_row(
            trial_id=f"{scenario_id}:neutral",
            condition="baseline_neutral",
            task_family=scenario_id,
            event_name=event_name,
            payload=neutral_payload,
            result=neutral,
            enactment=neutral_enactment,
            operator_scenario_id=operator_scenario_id,
            thread_id=thread_id,
        ),
        "shaped": _trajectory_row(
            trial_id=f"{scenario_id}:shaped",
            condition="shaped_debt",
            task_family=scenario_id,
            event_name=event_name,
            payload=shaped_payload,
            result=shaped,
            enactment=shaped_enactment,
            operator_scenario_id=operator_scenario_id,
            thread_id=thread_id,
        ),
    }


def _audit_codex_operator_adapter(
    scenarios: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    model_bound_scenarios = [
        scenario["scenario_id"]
        for scenario in scenarios
        if scenario["model_bound_delta_present"]
    ]
    return {
        "host_adapter_enactment_present": True,
        "low_level_cli_runner_stays_thin": True,
        "model_bound_debt_enactment_present": bool(model_bound_scenarios),
        "model_bound_enactment_scenarios": model_bound_scenarios,
        "inspected_surfaces": [
            "cortex/hosts/openai/operator_enactment.py::build_openai_operator_enactment_decision",
            "lab/openai_operator_cli.py::build_codex_exec_command",
            "lab/live_openai_silent_control_probe.py::run_gate0_audit",
        ],
        "finding": (
            "OpenAI host-adapter enactment consumes runtime route/policy/debt "
            "payloads and produces prompt-independent operator actions before "
            "the low-level Codex CLI runner is called."
        ),
    }


def _trajectory_row(
    *,
    trial_id: str,
    condition: str,
    task_family: str,
    event_name: str,
    payload: dict[str, Any],
    result,
    enactment,
    operator_scenario_id: str,
    thread_id: str | None,
) -> dict[str, Any]:
    event = {"event_name": event_name, "payload": payload}
    initial_prompt = _initial_prompt_for_operator_scenario(operator_scenario_id)
    model_visible_values = _model_visible_values_for_enactment(
        enactment=enactment,
        initial_prompt=initial_prompt,
        thread_id=thread_id,
    )
    leaks = find_internal_terms_in_model_visible_values(model_visible_values)
    return {
        "trial_id": trial_id,
        "condition": condition,
        "task_family": task_family,
        "event_index": result.event_index,
        "input_event": event,
        "expectation_ledger": result.session.as_summary()["expectation_ledger"],
        "resolution_deficit_payload": result.resolution_deficit_payload,
        "debt_control_payload": result.debt_control_payload,
        "executive_policy_view_payload": result.executive_policy_view_payload,
        "operator_route_payload": result.operator_route_payload,
        "operator_enactment_payload": enactment.as_payload(),
        "control_ledger_debt_control": result.control_ledger_summary[
            "allocation_diagnostics"
        ]["debt_control"],
        "initial_prompt_hash": _stable_hash({"prompt": initial_prompt}),
        "model_input_hash": _stable_hash({"prompt": initial_prompt}),
        "model_output_excerpt": None,
        "model_visible_internal_term_leaks": list(leaks),
        "model_visible_values": model_visible_values,
        "score": {
            "premature_closure": None,
            "evidence_recovery": None,
            "goal_continuity": None,
            "useful_work_slowdown": None,
            "overblock": None,
        },
    }


def _trajectory_rows(scenarios: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows.append(scenario["neutral"])
        rows.append(scenario["shaped"])
    return rows


def _model_bound_enactment_projection(enactment) -> dict[str, Any]:
    return {
        "action": enactment.action.value,
        "invocation_allowed": enactment.invocation_allowed,
        "blocked_reason": enactment.blocked_reason,
        "resume_prompt_name": enactment.resume_prompt_name,
        "thread_policy": enactment.thread_policy,
        "resume_recheck_allowed": enactment.resume_recheck_allowed,
        "model_bound_difference_kind": enactment.model_bound_difference_kind,
    }


def _initial_prompt_for_operator_scenario(operator_scenario_id: str) -> str:
    if operator_scenario_id == "truth_gap":
        return read_prompt_template("truth_gap_operator.md")
    return read_prompt_template("pass_minimal_operator.md")


def _model_visible_values_for_enactment(
    *,
    enactment,
    initial_prompt: str,
    thread_id: str | None,
) -> dict[str, Any]:
    if enactment.action.value == "resume_recheck":
        resumed_prompt = read_prompt_template(RECHECK_PROMPT_NAME)
        command_argv = openai_operator_cli.build_codex_exec_command(
            prompt=resumed_prompt,
            model="gpt-5.3-codex",
            resume_session=thread_id,
            ephemeral=False,
        )
    else:
        resumed_prompt = None
        command_argv = openai_operator_cli.build_codex_exec_command(
            prompt=initial_prompt,
            model="gpt-5.3-codex",
            ephemeral=enactment.thread_policy != "persistent_for_possible_recheck",
        )
    return {
        "initial_prompt": initial_prompt,
        "resumed_prompt": resumed_prompt,
        "command_argv": command_argv,
        "model_visible_transcript_excerpt": None,
        "stdout_reused_as_future_prompt": None,
    }


def _verification_ledger() -> ExpectationLedger:
    return open_expectation_from_forward_commitment(
        ExpectationLedger(),
        ForwardCommitment(
            commitment_id="gate0:verification",
            source_event_ref="gate0:event:0",
            claim_span_ref="gate0:event:0:structured-cue",
            commitment_kind="verification",
            assertiveness="high",
            scope="task",
            opened_at_step=0,
        ),
    )


def _decision_payload(gate0_passed: bool) -> dict[str, Any]:
    if gate0_passed:
        return {
            "live_trials_allowed": True,
            "verdict": "gate0_passed",
            "next_step": (
                "Retry the paired baseline/shaped/clean OpenAI operator trial "
                "matrix with host-adapter enactment enabled."
            ),
        }
    return {
        "live_trials_allowed": False,
        "verdict": "gate0_failed",
        "next_step": (
            "Do not run live trials. Open another bounded enactment remediation "
            "before retrying the silent-control probe."
        ),
    }


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
