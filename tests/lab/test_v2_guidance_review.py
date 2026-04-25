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
    assert (
        report["live_watchlist_status"]["claude_live_watchlist_evidence"]
        == "blocked_without_explicit_spend_or_no_spend_transcript"
    )


def test_v2_guidance_review_cli_writes_json(tmp_path) -> None:
    output = tmp_path / "review.json"

    assert v2_guidance_review.main(["--output", str(output)]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["guidance_marker"] == GUIDANCE_MARKER
    assert payload["model_visible_evidence"]["claude_system_channel"]["tests"]
