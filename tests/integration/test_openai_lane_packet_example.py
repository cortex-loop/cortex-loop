"""Integration test for the committed OpenAI-lane packet example."""

from __future__ import annotations

import json
import re
from pathlib import Path

from tests.integration._openai_lane_packet_example import (
    build_openai_lane_packet_example_snapshot,
)

_DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md"
)


def test_openai_lane_current_pair_packet_example_matches_committed_doc() -> None:
    expected_snapshot = _load_committed_snapshot()
    actual_snapshot = build_openai_lane_packet_example_snapshot()

    assert actual_snapshot == expected_snapshot


def _load_committed_snapshot() -> dict[str, object]:
    text = _DOC_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"## Example Snapshot\s+```json\n(.*?)\n```",
        text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Example snapshot JSON block is missing from the committed doc.")
    return json.loads(match.group(1))
