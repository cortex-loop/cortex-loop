"""Evidence guard for the committed V2/V3 parity artifact."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def test_v2_v3_parity_evidence_matches_the_committed_result() -> None:
    evidence_path = Path("tests/evidence/2026-04-17_v2_v3_parity.json")
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    rows = payload["rows"]

    assert len(rows) == 15
    assert payload["divergence_count"] == 0
    assert payload["divergence_count"] == sum(1 for row in rows if not row["equal"])
    assert all(row["equal"] for row in rows)
    assert all(row["classification"] == "identity" for row in rows)
    assert datetime.fromisoformat(payload["started_at"]) <= datetime.fromisoformat(payload["completed_at"])
    for row in rows:
        assert set(row) == {
            "axis",
            "task_id",
            "completion_source",
            "v2",
            "v3",
            "equal",
            "classification",
            "classification_reason",
            "divergence_keys",
            "diff_text",
        }
