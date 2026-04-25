"""Tests for strict Cortex v2 guidance review evidence."""

from __future__ import annotations

import json

from cortex.sre.guidance import GUIDANCE_MARKER
from lab import v2_guidance_review


def test_v2_guidance_review_covers_inventory_and_hostile_critiques() -> None:
    report = v2_guidance_review.build_v2_guidance_review()

    assert report["guidance_marker"] == GUIDANCE_MARKER
    assert "docs/CORTEX_V2_CORE_2.md" in report["packet_sources"]
    assert "core.commitment_certification" in report["coverage"]["core"]
    assert "sre.uncertainty_brake" in report["coverage"]["sre"]
    assert "host.claude_cli" in report["coverage"]["host"]
    assert "host.codex_cli" in report["coverage"]["host"]
    assert "aux.default_zero_removable" in report["coverage"]["aux"]
    assert {
        critique["critique"] for critique in report["hostile_reviewer_critiques"]
    } == {
        "calculated-but-not-communicated",
        "one-file-only",
        "diagnostics-only",
        "raw-aux-or-hidden-memory",
        "v3-successor-overclaim",
        "live-proof-overclaim",
    }
    assert report["subscription_cli_preflight"]["status"] in {
        "pending_subscription_cli_preflight",
        "ready_for_subscription_cli_live_transcript",
        "invalid_subscription_cli_preflight_json",
    }
    assert report["live_watchlist_status"]["claude_live_watchlist_evidence"] in {
        "pending_subscription_cli_preflight",
        "ready_for_subscription_cli_live_transcript",
    }


def test_v2_guidance_review_uses_ready_subscription_preflight(
    tmp_path,
    monkeypatch,
) -> None:
    preflight = tmp_path / "subscription-preflight.json"
    preflight.write_text(
        json.dumps(
            {
                "ready_for_live_watchlist": True,
                "spend_state": "subscription_cli_no_api_spend",
                "claude_cli": {"subscription_no_api_spend": True},
                "codex_cli": {"subscription_no_api_spend": True},
                "smoke": {"claude_cli": {"success": True}, "codex_cli": {"success": True}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(v2_guidance_review, "DEFAULT_PREFLIGHT_PATH", preflight)

    report = v2_guidance_review.build_v2_guidance_review()

    assert (
        report["subscription_cli_preflight"]["status"]
        == "ready_for_subscription_cli_live_transcript"
    )
    assert report["live_watchlist_status"] == {
        "s_tier_audit_protocol_locked": "ready_for_subscription_cli_live_transcript",
        "claude_live_watchlist_evidence": "ready_for_subscription_cli_live_transcript",
        "codex_live_watchlist_evidence": "ready_for_subscription_cli_live_transcript",
    }


def test_v2_guidance_review_cli_writes_json(tmp_path) -> None:
    output = tmp_path / "review.json"

    assert v2_guidance_review.main(["--output", str(output)]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["guidance_marker"] == GUIDANCE_MARKER
    assert payload["model_visible_evidence"]["claude_system_channel"]["tests"]
