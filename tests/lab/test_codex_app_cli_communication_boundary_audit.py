"""Lab locks for the Codex App/CLI communication-boundary audit."""

from __future__ import annotations

import json
from pathlib import Path

from lab import codex_app_cli_communication_boundary_audit as audit
from cortex.sre.task_standard import TASK_STANDARD_FORMATION_TEXT


STANDARD_BLOCK = "\n".join(
    (
        "Work standard: create the file with exact content and verify it.",
        "Likely misses: wrong file, wrong content, or no readback.",
        "Closure evidence: terminal output shows the exact line after writing.",
    )
)


def test_boundary_ladder_distinguishes_delivery_from_state_capture(
    tmp_path: Path,
) -> None:
    report = _write_task_standard_run(
        tmp_path / "task_standard",
        "run_context",
        verdict="partial_delivery_only",
        stdout_payload={
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": TASK_STANDARD_FORMATION_TEXT,
            }
        },
        stdout_text=STANDARD_BLOCK,
        transcript_text=f"{TASK_STANDARD_FORMATION_TEXT}\n{STANDARD_BLOCK}\n",
        standard_capture_rows=0,
    )

    ladder = audit.boundary_ladder_for_task_standard_run(report)

    assert ladder == {
        "host_stdout_contract_ok": True,
        "host_attached_context_observed": True,
        "model_assimilation_observed": True,
        "state_capture_observed": False,
        "gate_used_captured_state": False,
        "behavior_lift_claim_allowed": False,
    }


def test_audit_classifies_trickle_failures_without_claiming_product_success(
    tmp_path: Path,
    monkeypatch,
) -> None:
    task_standard_root = tmp_path / "task_standard"
    perception_root = tmp_path / "perception"
    event_capture_root = tmp_path / "event_capture"
    output_root = tmp_path / "audit"

    _write_task_standard_run(
        task_standard_root,
        "run_flat",
        verdict="fail",
        stdout_payload={"context": TASK_STANDARD_FORMATION_TEXT},
        stdout_text="",
        transcript_text="",
        standard_capture_rows=0,
    )
    _write_task_standard_run(
        task_standard_root,
        "run_context",
        verdict="partial_delivery_only",
        stdout_payload={
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": TASK_STANDARD_FORMATION_TEXT,
            }
        },
        stdout_text=STANDARD_BLOCK,
        transcript_text=f"{TASK_STANDARD_FORMATION_TEXT}\n{STANDARD_BLOCK}\n",
        standard_capture_rows=0,
    )
    _write_report(
        perception_root / "run_perception" / "report.json",
        {
            "verdict": "scoped_negative",
            "scoped_negative": "codex_cli_live_hooks_exposed_stop_only_no_product_task_events",
            "output_root": str(perception_root / "run_perception"),
        },
    )
    _write_report(
        event_capture_root / "run_event_capture" / "report.json",
        {
            "verdict": "pass_full_lifecycle",
            "output_root": str(event_capture_root / "run_event_capture"),
        },
    )
    monkeypatch.setattr(
        audit,
        "_codex_app_hook_health",
        lambda: {
            "ok": True,
            "chat_boundary_enforcement": "disabled_by_repo_policy",
            "workflow_readiness_ok": False,
            "workflow_readiness_verdict": "FAIL",
        },
    )

    report = audit.run_audit(
        output_root=output_root,
        task_standard_live_root=task_standard_root,
        product_perception_live_root=perception_root,
        product_event_capture_root=event_capture_root,
    )

    assert report["passed"] is True
    assert report["mechanical_success"] is True
    assert report["product_evidence_success"] is False
    assert report["partial_evidence_only"] is True
    assert report["verdict"] == (
        "structural_proof_boundary_issue_localized_to_codex_app_cli"
    )
    assert set(report["incident_summary"]["present_classes"]) == set(
        audit.INCIDENT_CLASS_IDS
    )
    assert report["incident_classes"]["host_contract_mismatch"]["present"] is True
    assert report["incident_classes"]["lifecycle_config_mismatch"]["present"] is True
    assert (
        report["incident_classes"]["lifecycle_config_mismatch"][
            "remediated_by_event_capture"
        ]
        is True
    )
    assert report["incident_classes"]["temporal_capture_mismatch"]["present"] is True
    assert report["incident_classes"]["live_vs_gate0_mismatch"]["present"] is True
    assert (
        report["incident_classes"]["workflow_health_closeout_coupling"]["present"]
        is True
    )
    assert report["next_product_train"] == (
        "codex-app-cli-task-standard-pretool-transcript-capture"
    )
    assert (output_root / "summary.json").is_file()


def _write_task_standard_run(
    root: Path,
    run_name: str,
    *,
    verdict: str,
    stdout_payload: dict[str, object],
    stdout_text: str,
    transcript_text: str,
    standard_capture_rows: int,
) -> dict[str, object]:
    run_root = root / run_name
    transcript_path = run_root / "transcript.jsonl"
    diagnostics_path = run_root / "hook_client_diagnostics.jsonl"
    stdout_path = run_root / "codex_stdout.jsonl"
    report_path = run_root / "report.json"
    run_root.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(transcript_text, encoding="utf-8")
    stdout_path.write_text(stdout_text, encoding="utf-8")
    diagnostics_path.write_text(
        json.dumps(
            {
                "stdout_payload": stdout_payload,
                "coordinator": {
                    "hook_payload": {"transcript_path": str(transcript_path)}
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report = {
        "verdict": verdict,
        "stdout_path": str(stdout_path),
        "diagnostics_path": str(diagnostics_path),
        "standard_capture_rows": standard_capture_rows,
        "prework_standard_capture": False,
    }
    _write_report(report_path, report)
    return report


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
