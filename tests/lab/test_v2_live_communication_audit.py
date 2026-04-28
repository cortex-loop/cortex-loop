from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cortex.sre.guidance import GUIDANCE_MARKER, v2_guidance_inventory_payload
from lab import agent_loop_guard, v2_live_communication_audit


def test_live_communication_audit_passes_only_with_all_rows_from_guidance(
    tmp_path: Path,
) -> None:
    runner = _FakeRunner()
    preflight = _write_preflight(tmp_path)

    payload = v2_live_communication_audit.run_v2_live_communication_audit(
        hosts=("claude", "codex"),
        command_runner=runner,
        preflight_path=preflight,
        audit_run_root=tmp_path / "runs",
        run_id="test-run",
    )

    assert payload["all_hosts_passed"] is True
    assert set(payload["host_results"]) == {"claude", "codex"}
    for prompt in runner.prompts:
        assert GUIDANCE_MARKER in prompt
        assert "The only valid source for row IDs is that block's contract_rows list" in prompt
        assert "core.lifecycle_dispatch" in prompt
        assert "negative.forbidden_shortcuts" in prompt
    for result in payload["host_results"].values():
        assert result["prompt_contains_guidance_marker"] is True
        assert result["validation"]["missing_row_ids"] == []
        assert result["validation"]["extra_row_ids"] == []


def test_live_communication_audit_fails_when_a_model_drops_a_row(
    tmp_path: Path,
) -> None:
    runner = _FakeRunner(drop_last_row=True)
    preflight = _write_preflight(tmp_path)

    payload = v2_live_communication_audit.run_v2_live_communication_audit(
        hosts=("claude",),
        command_runner=runner,
        preflight_path=preflight,
        audit_run_root=tmp_path / "runs",
        run_id="missing-row",
    )

    result = payload["host_results"]["claude"]
    assert payload["all_hosts_passed"] is False
    assert result["passed"] is False
    assert result["validation"]["missing_row_ids"] == ["negative.forbidden_shortcuts"]
    assert any(
        "reported row ids do not exactly match" in failure
        for failure in result["validation"]["failures"]
    )


def test_validate_model_audit_report_requires_global_constraints() -> None:
    report = _valid_model_report("codex")
    report["global_constraints"]["no_raw_aux_memory"] = False

    validation = v2_live_communication_audit.validate_model_audit_report(
        report,
        host="codex",
    )

    assert validation["passed"] is False
    assert "global constraint no_raw_aux_memory is not true" in validation["failures"]


def test_update_gate_report_marks_live_gates_only_after_passing_audit(
    tmp_path: Path,
) -> None:
    runner = _FakeRunner()
    preflight = _write_preflight(tmp_path)
    audit = v2_live_communication_audit.run_v2_live_communication_audit(
        hosts=("claude", "codex"),
        command_runner=runner,
        preflight_path=preflight,
        audit_run_root=tmp_path / "runs",
        run_id="gate-update",
    )
    report_path = tmp_path / "gates.latest.json"
    report = _all_but_live_pass_report()
    report_path.write_text(json.dumps(report.as_payload()), encoding="utf-8")

    updated_payload = v2_live_communication_audit.update_gate_report_from_audit(
        audit,
        gate_report_path=report_path,
    )

    statuses = {gate["gate_id"]: gate["status"] for gate in updated_payload["gates"]}
    assert statuses["claude_live_watchlist_evidence"] == "pass"
    assert statuses["codex_live_watchlist_evidence"] == "pass"
    updated_report = agent_loop_guard.read_gate_report(report_path)
    assert agent_loop_guard.closure_status(updated_report).verdict == "pass"


def _write_preflight(tmp_path: Path) -> Path:
    path = tmp_path / "preflight.json"
    path.write_text(
        json.dumps(
            {
                "ready_for_live_watchlist": True,
                "spend_state": "subscription_cli_no_api_spend",
                "claude_cli": {"subscription_no_api_spend": True},
                "codex_cli": {"subscription_no_api_spend": True},
            }
        ),
        encoding="utf-8",
    )
    return path


class _FakeRunner:
    def __init__(self, *, drop_last_row: bool = False) -> None:
        self.drop_last_row = drop_last_row
        self.prompts: list[str] = []

    def __call__(self, command: list[str], **_: Any) -> dict[str, Any]:
        if command[0] == "claude":
            prompt = command[2]
            self.prompts.append(prompt)
            stdout = json.dumps(
                {"result": json.dumps(_valid_model_report("claude", self.drop_last_row))}
            )
            return _result(command, stdout=stdout)
        if command[0] == "codex":
            prompt = command[-1]
            self.prompts.append(prompt)
            stdout = json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "text": json.dumps(
                            _valid_model_report("codex", self.drop_last_row)
                        )
                    },
                }
            )
            return _result(command, stdout=stdout + "\n")
        raise AssertionError(f"unexpected command: {command!r}")


def _valid_model_report(host: str, drop_last_row: bool = False) -> dict[str, Any]:
    rows = v2_guidance_inventory_payload()
    if drop_last_row:
        rows = rows[:-1]
    return {
        "audit_marker": v2_live_communication_audit.AUDIT_MARKER,
        "guidance_marker_seen": GUIDANCE_MARKER,
        "host_seen": host,
        "surface_seen": f"{host}-cli-live-communication-audit",
        "rows": [
            {
                "row_id": row["row_id"],
                "packet": row["packet"],
                "visibility": row["visibility"],
                "guidance_visible": True,
                "evidence_source": "contract_rows",
                "next_turn_effect": (
                    f"Apply {row['row_id']} as a concrete next-turn constraint "
                    "before making any completion claim."
                ),
            }
            for row in rows
        ],
        "global_constraints": {
            "no_raw_aux_memory": True,
            "no_extracted_cortex_successor_claim": True,
            "no_live_closure_without_evidence": True,
            "subscription_cli_no_api_spend": True,
            "shipping_conformance_distinction": True,
            "watchlist_not_product_perfection": True,
        },
        "bounded_result": {
            "full_v2_guidance_denominator_visible_in_this_prompt": True,
            "all_reported_rows_have_next_turn_effect": True,
            "this_is_watchlist_evidence_not_product_perfection": True,
            "optimization_remains_next": True,
        },
        "hostile_review": {
            "calculated_not_communicated": "answered by contract_rows visibility",
            "one_file_only": "answered by shared contract plus live CLI transcript",
            "diagnostics_only": "answered by next-turn effect per row",
            "raw_aux_hidden_memory": "AUX is default-zero and publication-only",
            "extracted_cortex_successor_overclaim": "extracted Cortex is not used as proof",
            "live_proof_overclaim": "watchlist evidence is not product perfection",
        },
    }


def _result(command: list[str], *, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    return {
        "command": command,
        "exit_code": 0,
        "stdout": stdout,
        "stderr": stderr,
        "started_at": "2026-04-25T00:00:00+00:00",
        "ended_at": "2026-04-25T00:00:01+00:00",
    }


def _all_but_live_pass_report() -> agent_loop_guard.LoopGateReport:
    gates: list[agent_loop_guard.GateResult] = []
    for gate_id in agent_loop_guard.DEFAULT_REQUIRED_GATES:
        if gate_id in {
            "claude_live_watchlist_evidence",
            "codex_live_watchlist_evidence",
        }:
            gates.append(
                agent_loop_guard.GateResult(
                    gate_id=gate_id,
                    status="missing",
                    reason=f"{gate_id} has not run",
                    next_action=f"run {gate_id}",
                )
            )
            continue
        gates.append(
            agent_loop_guard.GateResult(
                gate_id=gate_id,
                status="pass",
                reason=f"{gate_id} passed",
                next_action="none",
                evidence=f"bounded evidence for {gate_id}",
            )
        )
    return agent_loop_guard.LoopGateReport(
        profile=agent_loop_guard.DEFAULT_PROFILE,
        required_gates=agent_loop_guard.DEFAULT_REQUIRED_GATES,
        gates=tuple(gates),
        plan_steps=agent_loop_guard.V2_EXECUTIVE_GUIDANCE_PLAN,
    )
