"""Lab locks for the Codex App/CLI Cortex value-ablation audit."""

from __future__ import annotations

import json
from pathlib import Path

from lab import codex_app_cli_cortex_value_ablation_audit as audit


def test_threshold_replay_marks_zero_pressure_as_not_causal(tmp_path: Path) -> None:
    row = _trial_row(
        tmp_path,
        trial_id="astro__hook__001",
        hidden=False,
        pressure=0.0,
        active=0,
        resolved=1,
    )

    report = audit.threshold_replay([row])

    assert report["verdict"] == "threshold_not_causal"
    trial = report["trials"][0]
    assert trial["pressure"] == 0.0
    assert trial["resolved_expectation_count"] == 1
    assert not any(trial["would_block_by_threshold"].values())


def test_paydown_ablation_distinguishes_catch_from_overblock_risk(tmp_path: Path) -> None:
    rows = [
        _trial_row(
            tmp_path,
            trial_id="astro__hook__fail",
            hidden=False,
            verification_evidence_count=3,
            closure_claim_count=1,
            resolved=1,
        ),
        _trial_row(
            tmp_path,
            trial_id="astro__hook__pass",
            hidden=True,
            verification_evidence_count=2,
            closure_claim_count=1,
            resolved=1,
        ),
    ]

    report = audit.paydown_ablation(rows)

    assert report["verdict"] == "paydown_tightening_risky_claim_alignment_needed"
    assert report["caught_hidden_failures"] == 1
    assert report["overblock_risk_count"] == 1


def test_claim_evidence_alignment_uses_visible_claims_without_hidden_verifier(
    tmp_path: Path,
) -> None:
    row = _trial_row(
        tmp_path,
        trial_id="astro__hook__search_gap",
        hidden=False,
        output_excerpt="Implemented the docs index, tag pages, shared navigation, and simple docs search.",
        tool_text="npm run build\nnpm run test:visible\nall visible checks passed",
    )

    report = audit.claim_evidence_alignment([row])

    assert report["hidden_verifier_read"] is False
    assert report["verdict"] == "visible_claim_evidence_gap_detected"
    trial = report["trials"][0]
    assert trial["unmatched_to_claim_count"] >= 1
    evidence_classes = {
        item["obligation"]: item["evidence_class"]
        for item in trial["classifications"]
    }
    assert evidence_classes["docs search experience"] == "visible_check"


def test_forced_intervention_live_refuses_without_current_turn_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(audit.APPROVAL_ENV, raising=False)

    report = audit.run_forced_intervention_live(output_root=tmp_path)

    assert report["passed"] is False
    assert report["verdict"] == "not_run"
    assert report["approval_env"] == audit.APPROVAL_ENV
    assert (tmp_path / "forced_intervention_live_refused.json").is_file()


def test_audit_decision_blocks_fixture_work_when_requirement_perception_is_needed() -> None:
    decision = audit.audit_decision(
        threshold={"verdict": "threshold_not_causal"},
        paydown={"verdict": "paydown_tightening_risky_claim_alignment_needed"},
        alignment={"verdict": "visible_claim_evidence_gap_detected"},
        family={},
        forced={"verdict": "not_run"},
    )

    assert decision["verdict"] == "requirement_level_perception_needed"
    assert "fixture remediation" in decision["forbidden_next"]
    assert decision["threshold_action"] == "stop threshold tuning"


def _trial_row(
    tmp_path: Path,
    *,
    trial_id: str,
    hidden: bool,
    pressure: float = 0.0,
    active: int = 0,
    resolved: int = 0,
    verification_evidence_count: int = 0,
    closure_claim_count: int = 0,
    output_excerpt: str = "Implemented the docs work.",
    tool_text: str = "npm run build",
) -> dict[str, object]:
    diagnostics_path = tmp_path / f"{trial_id}.jsonl"
    diagnostics_path.write_text(
        json.dumps(
            {
                "coordinator": {
                    "hook_payload": {
                        "hook_event_name": "PostToolUse",
                        "tool_name": "Bash",
                        "tool_input_excerpt": tool_text,
                        "tool_response_excerpt": "exit_code: 0",
                    },
                    "directive": {
                        "action": "allow",
                        "silence_reason": "non_stop_lifecycle_state_update_only",
                    },
                    "grounded_intervention": {
                        "pressure_summary": {
                            "control_pressure": 0.0,
                            "verification_pressure": 0.0,
                        }
                    },
                    "session_state": {
                        "expectation_ledger": {"active": [], "resolved": []},
                        "verification_evidence_count": verification_evidence_count,
                        "closure_claim_count": 0,
                    },
                }
            },
            sort_keys=True,
        )
        + "\n"
        + json.dumps(
            {
                "coordinator": {
                    "hook_payload": {"hook_event_name": "Stop"},
                    "directive": {
                        "action": "stay_silent",
                        "silence_reason": "pressure_below_visible_threshold",
                    },
                    "grounded_intervention": {
                        "pressure_summary": {
                            "control_pressure": pressure,
                            "verification_pressure": pressure,
                        }
                    },
                    "session_state": {
                        "expectation_ledger": {
                            "active": [
                                {"expectation_id": f"{trial_id}:active"}
                                for _ in range(active)
                            ],
                            "resolved": [
                                {"expectation_id": f"{trial_id}:resolved"}
                                for _ in range(resolved)
                            ],
                        },
                        "verification_evidence_count": verification_evidence_count,
                        "closure_claim_count": closure_claim_count,
                    },
                }
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "trial_id": trial_id,
        "hidden_quality_pass": hidden,
        "output_excerpt": output_excerpt,
        "artifacts": {"diagnostics": str(diagnostics_path)},
    }
