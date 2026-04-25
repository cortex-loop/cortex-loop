"""Focused tests for the Claude/Codex live loop Stop-hook guard."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from lab import agent_loop_guard


def test_decide_loop_guard_allows_stop_when_required_gates_pass() -> None:
    report = _report(
        gates=[
            _gate("active_train_reconciled", "pass"),
            _gate("executive_guidance_contract_present", "pass"),
        ],
        required_gates=("active_train_reconciled", "executive_guidance_contract_present"),
    )
    state = agent_loop_guard.LoopGuardState(session_id="s1", host="codex")

    decision = agent_loop_guard.decide_loop_guard(report, state)

    assert decision.action == "allow_stop"
    assert decision.as_hook_output(host="codex") == {"continue": True}


def test_decide_loop_guard_continues_on_missing_required_gate() -> None:
    report = _report(
        gates=[_gate("active_train_reconciled", "pass")],
        required_gates=("active_train_reconciled", "codex_live_watchlist_evidence"),
    )
    state = agent_loop_guard.LoopGuardState(
        session_id="s1",
        host="codex",
        continuation_count=2,
    )

    decision = agent_loop_guard.decide_loop_guard(
        report,
        state,
        gate_report_path=Path(".cortex/live_validation/agent_loop_guard/gates.latest.json"),
    )

    assert decision.action == "continue"
    assert decision.gate_id == "codex_live_watchlist_evidence"
    assert "do not stop yet" in decision.continuation_prompt
    assert "Run bounded Codex CLI live watchlist" in decision.continuation_prompt
    assert "Required evidence:" in decision.continuation_prompt
    assert "Continuation budget after this pass: 3/6" in decision.continuation_prompt
    hook_output = decision.as_hook_output(host="codex")
    assert hook_output["decision"] == "block"
    assert "codex_live_watchlist_evidence" in hook_output["reason"]


def test_decide_loop_guard_continues_on_failing_gate_with_specific_next_action() -> None:
    report = _report(
        gates=[
            _gate(
                "claude_guidance_fixture_passed",
                "fail",
                reason="fixture proves CHECK was calculated but not model-visible",
                next_action="wire CHECK guidance into the Claude fixture prompt",
            )
        ],
        required_gates=("claude_guidance_fixture_passed",),
    )
    state = agent_loop_guard.LoopGuardState(session_id="s1", host="claude")

    decision = agent_loop_guard.decide_loop_guard(report, state)

    assert decision.action == "continue"
    assert "wire CHECK guidance into the Claude fixture prompt" in decision.continuation_prompt
    assert decision.as_hook_output(host="claude")["decision"] == "block"


def test_decide_loop_guard_stops_for_operator_on_blocked_gate() -> None:
    report = _report(
        gates=[
            _gate(
                "claude_live_watchlist_evidence",
                "blocked",
                reason="Claude auth is missing",
                next_action="operator signs in or marks the live lane intentionally deferred",
            )
        ],
        required_gates=("claude_live_watchlist_evidence",),
    )
    state = agent_loop_guard.LoopGuardState(session_id="s1", host="claude")

    decision = agent_loop_guard.decide_loop_guard(report, state)

    assert decision.action == "stop_for_operator"
    assert decision.gate_id == "claude_live_watchlist_evidence"
    hook_output = decision.as_hook_output(host="claude")
    assert hook_output["continue"] is False
    assert "Claude auth is missing" in hook_output["stopReason"]


def test_decide_loop_guard_stops_at_max_continuations() -> None:
    report = _report(
        gates=[_gate("codex_live_watchlist_evidence", "missing")],
        required_gates=("codex_live_watchlist_evidence",),
        max_continuations=2,
    )
    state = agent_loop_guard.LoopGuardState(
        session_id="s1",
        host="codex",
        continuation_count=2,
    )

    decision = agent_loop_guard.decide_loop_guard(report, state)

    assert decision.action == "stop_for_operator"
    assert "max_continuations=2" in decision.reason


def test_decide_loop_guard_allows_non_stop_events() -> None:
    report = _report(
        gates=[_gate("codex_live_watchlist_evidence", "missing")],
        required_gates=("codex_live_watchlist_evidence",),
    )
    state = agent_loop_guard.LoopGuardState(
        session_id="s1",
        host="codex",
        event_name="PreToolUse",
    )

    decision = agent_loop_guard.decide_loop_guard(report, state)

    assert decision.action == "allow_stop"
    assert "not a supported stop gate" in decision.reason


def test_hook_command_increments_state_only_when_it_blocks_stop(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    report_path = tmp_path / "gates.json"
    state_path = tmp_path / "state.json"
    report = _report(
        gates=[_gate("codex_live_watchlist_evidence", "missing")],
        required_gates=("codex_live_watchlist_evidence",),
    )
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            json.dumps(
                {
                    "session_id": "codex-session",
                    "hook_event_name": "Stop",
                    "stop_hook_active": False,
                }
            )
        ),
    )

    assert (
        agent_loop_guard.main(
            [
                "hook",
                "--host",
                "codex",
                "--report",
                str(report_path),
                "--state",
                str(state_path),
            ]
        )
        == 0
    )

    hook_output = json.loads(capsys.readouterr().out)
    assert hook_output["decision"] == "block"
    state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_payload["continuation_count"] == 1
    assert state_payload["last_decision"]["action"] == "continue"


def test_hook_command_does_not_increment_state_when_stop_is_allowed(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    report_path = tmp_path / "gates.json"
    state_path = tmp_path / "state.json"
    report = _report(
        gates=[_gate("codex_live_watchlist_evidence", "pass")],
        required_gates=("codex_live_watchlist_evidence",),
    )
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(json.dumps({"session_id": "codex-session", "hook_event_name": "Stop"})),
    )

    assert (
        agent_loop_guard.main(
            [
                "hook",
                "--host",
                "codex",
                "--report",
                str(report_path),
                "--state",
                str(state_path),
            ]
        )
        == 0
    )

    hook_output = json.loads(capsys.readouterr().out)
    assert hook_output == {"continue": True}
    state_payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert state_payload["continuation_count"] == 0
    assert state_payload["last_decision"]["action"] == "allow_stop"


def test_init_report_and_render_hook_config_cli(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "gates.latest.json"

    assert (
        agent_loop_guard.main(
            [
                "init-report",
                "--output",
                str(report_path),
                "--max-continuations",
                "4",
            ]
        )
        == 0
    )
    assert str(report_path) in capsys.readouterr().out
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["max_continuations"] == 4
    assert payload["surface"] == "agent_loop_guard"
    assert payload["scope"] == "lab"
    assert payload["evidence_role"] == "watchlist"
    assert [step["gate_id"] for step in payload["plan_steps"]] == payload["required_gates"]
    assert payload["plan_steps"][0]["title"] == "Close the active brake-tonic reconciliation"
    assert (
        payload["plan_steps"][1]["title"]
        == "Inventory the full V2 communication denominator"
    )
    assert (
        payload["plan_steps"][6]["title"]
        == "Lock the S-tier live audit protocol"
    )
    assert payload["s_tier_audit_expectations"]["expected_runtime_minutes"] == "180-240"
    assert "Core lifecycle dispatch" in payload["communication_denominator"][0]
    assert "Do not mark pass from stale transcripts" in payload["plan_steps"][7]["stop_rule"]

    assert (
        agent_loop_guard.main(
            ["render-hook-config", "--host", "claude", "--report", str(report_path)]
        )
        == 0
    )
    config = json.loads(capsys.readouterr().out)
    command = config["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert "python3 -m lab.agent_loop_guard hook --host claude" in command
    assert str(report_path) in command


def test_render_plan_cli_includes_ordered_gate_requirements(capsys) -> None:
    assert agent_loop_guard.main(["render-plan"]) == 0

    output = capsys.readouterr().out
    assert "# V2 Executive Guidance Loop Plan" in output
    assert "1. `active_train_reconciled` - Close the active brake-tonic reconciliation" in output
    assert "Full V2 communication denominator:" in output
    assert (
        "2. `v2_packet_communication_inventory_complete` - "
        "Inventory the full V2 communication denominator"
    ) in output
    assert (
        "7. `s_tier_audit_protocol_locked` - Lock the S-tier live audit protocol"
        in output
    )
    assert "9. `codex_live_watchlist_evidence` - Run bounded Codex CLI live watchlist" in output
    assert "Expected runtime: 180-240 minutes" in output
    assert "unapproved paid service-lane calls" in output


def test_render_plan_cli_can_emit_json(capsys) -> None:
    assert agent_loop_guard.main(["render-plan", "--format", "json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["scope"] == "lab"
    assert payload["evidence_role"] == "watchlist"
    assert "Claude CLI" in payload["communication_denominator"][3]
    assert payload["required_gates"] == list(agent_loop_guard.DEFAULT_REQUIRED_GATES)
    assert payload["plan_steps"][4]["gate_id"] == "codex_guidance_fixture_passed"
    assert "short-run anomaly" in payload["s_tier_audit_expectations"]["runtime_rule"]


def test_evaluate_command_can_emit_hook_json(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "gates.json"
    report = _report(
        gates=[_gate("codex_live_watchlist_evidence", "missing")],
        required_gates=("codex_live_watchlist_evidence",),
    )
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")

    assert (
        agent_loop_guard.main(
            [
                "evaluate",
                "--host",
                "codex",
                "--report",
                str(report_path),
                "--format",
                "hook-json",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["decision"] == "block"
    assert "codex_live_watchlist_evidence" in payload["reason"]


def test_assert_closure_rejects_pending_full_communication_report() -> None:
    report = agent_loop_guard.default_gate_report()

    status = agent_loop_guard.closure_status(report)

    assert status.verdict == "pending"
    assert status.pending_gates[0].gate_id == "active_train_reconciled"
    with pytest.raises(SystemExit, match="full V2 communication closure is not proven"):
        agent_loop_guard.assert_closure(report)


def test_assert_closure_allows_only_when_required_gates_pass(tmp_path: Path, capsys) -> None:
    report_path = tmp_path / "gates.json"
    report = _report(
        gates=[
            _gate(gate_id, "pass", evidence=f"bounded evidence for {gate_id}")
            for gate_id in agent_loop_guard.DEFAULT_REQUIRED_GATES
        ],
        required_gates=agent_loop_guard.DEFAULT_REQUIRED_GATES,
    )
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")

    assert (
        agent_loop_guard.main(
            [
                "assert-closure",
                "--report",
                str(report_path),
                "--format",
                "json",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "pass"
    assert payload["pending_gates"] == []


def test_assert_closure_rejects_operator_blocked_stop_even_with_compat_flag(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "gates.json"
    gates = [
        _gate(gate_id, "pass", evidence=f"bounded evidence for {gate_id}")
        for gate_id in agent_loop_guard.DEFAULT_REQUIRED_GATES
        if gate_id != "claude_live_watchlist_evidence"
    ]
    gates.append(
        _gate(
            "claude_live_watchlist_evidence",
            "blocked",
            reason="Claude auth requires operator sign-in",
            next_action="operator signs in to Claude CLI",
        )
    )
    report = _report(
        gates=gates,
        required_gates=agent_loop_guard.DEFAULT_REQUIRED_GATES,
    )
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")

    with pytest.raises(SystemExit, match="blocked gates cannot satisfy closure"):
        agent_loop_guard.main(
            [
                "assert-closure",
                "--report",
                str(report_path),
                "--allow-blocked",
            ]
        )


def _report(
    *,
    gates: list[agent_loop_guard.GateResult],
    required_gates: tuple[str, ...],
    max_continuations: int = 6,
) -> agent_loop_guard.LoopGateReport:
    return agent_loop_guard.LoopGateReport(
        profile=agent_loop_guard.DEFAULT_PROFILE,
        required_gates=required_gates,
        gates=tuple(gates),
        max_continuations=max_continuations,
        plan_steps=agent_loop_guard.plan_steps_for_required_gates(required_gates),
    )


def _gate(
    gate_id: str,
    status: agent_loop_guard.GateStatus,
    *,
    reason: str | None = None,
    next_action: str | None = None,
    evidence: str | None = None,
) -> agent_loop_guard.GateResult:
    return agent_loop_guard.GateResult(
        gate_id=gate_id,
        status=status,
        reason=reason or f"{gate_id} is {status}",
        next_action=next_action or f"work the {gate_id} gate",
        evidence=evidence,
    )
