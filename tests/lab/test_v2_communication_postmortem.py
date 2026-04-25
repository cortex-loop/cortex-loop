from __future__ import annotations

import json
from pathlib import Path

from lab import v2_communication_postmortem


def test_postmortem_records_early_checkpoint_root_causes() -> None:
    payload = v2_communication_postmortem.render_postmortem_payload(
        generated_at="2026-04-25T00:00:00+00:00",
    )

    findings = {finding["finding_id"]: finding for finding in payload["findings"]}
    assert payload["verdict"] == "prior_loop_checkpointed_before_live_claude_codex_proof"
    assert "pm-001-blocked-closure-escape" in findings
    assert "pm-002-closeout-opt-out" in findings
    assert "allow-blocked" in findings["pm-001-blocked-closure-escape"]["failure"]
    assert "require_full_communication_closure=false" in findings[
        "pm-002-closeout-opt-out"
    ]["failure"]
    assert (
        payload["minimum_next_session_bar"]["blocked_gate_policy"]
        == "operator block only; never closure"
    )
    assert payload["minimum_next_session_bar"]["expected_runtime_minutes"] == "180-240"


def test_postmortem_cli_writes_report(tmp_path: Path) -> None:
    output = tmp_path / "postmortem.json"

    assert v2_communication_postmortem.main(["--output", str(output)]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["surface"] == "lab"
    assert "Claude CLI live model-visible guidance transcript" in payload[
        "what_was_not_proven"
    ]
