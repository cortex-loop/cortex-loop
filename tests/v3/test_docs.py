"""Docs guards for the Cortex v3 incubation seam."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_public_docs_point_to_v3_incubation_track() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    v3_doc = (REPO_ROOT / "docs" / "v3" / "README.md").read_text(encoding="utf-8")

    assert "V3 Incubation Track" in readme
    assert "CORTEX V3 Incubation" in docs_index
    assert "`cortex_v3/`" in v3_doc
    assert "thin OpenAI, Claude, and Gemini adapters" in v3_doc
