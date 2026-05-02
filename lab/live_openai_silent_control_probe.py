"""Gate-0 harness for the OpenAI operator silent-control live probe."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    open_expectation_from_forward_commitment,
)

try:  # pragma: no cover - direct script execution uses the fallback imports.
    from . import live_operator_directionality
    from . import openai_operator_cli
    from .live_validation_common import LOCAL_LIVE_ROOT, ensure_live_validation_dirs, now_utc_iso
except ImportError:  # pragma: no cover
    import live_operator_directionality
    import openai_operator_cli
    from lab.live_validation_common import LOCAL_LIVE_ROOT, ensure_live_validation_dirs, now_utc_iso


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
            "inspect_after_unpaid_verification",
            event_name="response.output_text.delta",
            payload={
                "session_id": "openai-silent-gate0-inspect",
                "response_id": "resp-gate0-inspect",
                "delta": "Inspecting the current workspace before claiming completion.",
            },
        ),
        _runtime_case(
            "forward_after_unpaid_verification",
            event_name="response.completed",
            payload={
                "session_id": "openai-silent-gate0-forward",
                "response_id": "resp-gate0-forward",
                "commitment_id": "commit-gate0-forward",
                "externally_consequential": True,
            },
        ),
    )
    adapter_coupling = _audit_codex_operator_adapter()
    runtime_delta_present = any(case["runtime_delta_present"] for case in scenarios)
    model_bound_delta_present = bool(
        runtime_delta_present
        and adapter_coupling["model_bound_debt_enactment_present"]
    )
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
    route_delta = neutral.operator_route_payload != shaped.operator_route_payload
    policy_delta = neutral.executive_policy_view_payload != shaped.executive_policy_view_payload
    debt_delta = neutral.debt_control_payload != shaped.debt_control_payload
    return {
        "scenario_id": scenario_id,
        "event_name": event_name,
        "runtime_delta_present": bool(route_delta or policy_delta or debt_delta),
        "route_delta_present": route_delta,
        "policy_delta_present": policy_delta,
        "debt_delta_present": debt_delta,
        "neutral": _trajectory_row(
            trial_id=f"{scenario_id}:neutral",
            condition="baseline_neutral",
            task_family=scenario_id,
            event_name=event_name,
            payload=neutral_payload,
            result=neutral,
        ),
        "shaped": _trajectory_row(
            trial_id=f"{scenario_id}:shaped",
            condition="shaped_debt",
            task_family=scenario_id,
            event_name=event_name,
            payload=shaped_payload,
            result=shaped,
        ),
    }


def _audit_codex_operator_adapter() -> dict[str, Any]:
    single_turn_signature = inspect.signature(openai_operator_cli.run_openai_operator_single_turn)
    signature_params = tuple(single_turn_signature.parameters)
    accepts_runtime_control = any(
        name in signature_params
        for name in (
            "runtime_session",
            "operator_route",
            "operator_route_payload",
            "debt_control",
            "debt_control_payload",
            "executive_policy_view",
        )
    )
    codex_exec_source = inspect.getsource(openai_operator_cli._run_codex_exec)
    directionality_source = inspect.getsource(live_operator_directionality._run_openai_variant)
    directionality_uses_debt_control = (
        "debt_control_pressure" in directionality_source
        or "debt_control_payload" in directionality_source
        or "debt_control" in directionality_source
    )
    codex_command_accepts_control_payload = (
        "operator_route" in codex_exec_source
        or "debt_control" in codex_exec_source
        or "runtime_session" in codex_exec_source
    )
    return {
        "openai_operator_single_turn_signature": str(single_turn_signature),
        "accepts_runtime_control_argument": accepts_runtime_control,
        "directionality_harness_uses_debt_control": directionality_uses_debt_control,
        "codex_exec_command_accepts_control_payload": codex_command_accepts_control_payload,
        "model_bound_debt_enactment_present": bool(
            accepts_runtime_control
            or directionality_uses_debt_control
            or codex_command_accepts_control_payload
        ),
        "inspected_surfaces": [
            "lab/openai_operator_cli.py::run_openai_operator_single_turn",
            "lab/openai_operator_cli.py::_run_codex_exec",
            "lab/live_operator_directionality.py::_run_openai_variant",
        ],
        "finding": (
            "The OpenAI runtime can compute debt-control route diagnostics, but "
            "the current Codex operator adapter has no argument or command path "
            "that enacts those diagnostics before invoking the model."
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
) -> dict[str, Any]:
    event = {"event_name": event_name, "payload": payload}
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
        "control_ledger_debt_control": result.control_ledger_summary[
            "allocation_diagnostics"
        ]["debt_control"],
        "model_input_hash": _stable_hash(event),
        "model_output_excerpt": None,
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
            "next_step": "Run the paired baseline/shaped/clean OpenAI operator trial matrix.",
        }
    return {
        "live_trials_allowed": False,
        "verdict": "gate0_failed",
        "next_step": (
            "Do not run live trials. Open a remediation seam that connects "
            "OpenAI runtime debt-control outputs to the Codex operator invocation "
            "or continuation policy."
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
