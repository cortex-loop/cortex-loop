"""Tests for the bounded live-code Cortex quality audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal.audit import cortex_quality_audit


def test_live_code_audit_covers_full_scope_with_only_allowed_findings() -> None:
    audit = cortex_quality_audit.build_live_code_audit(REPO_ROOT)
    expected_modules = cortex_quality_audit._iter_live_code_modules(REPO_ROOT)
    records = audit["records"]

    assert audit["scope"] == "live-code"
    assert audit["module_count"] == len(expected_modules)
    assert tuple(record["module_path"] for record in records) == expected_modules
    assert {
        record["finding"] for record in records
    } <= set(cortex_quality_audit.VALID_FINDINGS)
    assert audit["summary"]["by_finding"]["broken-or-hanging"] == 0
    assert audit["summary"]["by_finding"]["dead-weight"] == 0
    assert "cortex/sre/mediation.py" in expected_modules
    for record in records:
        assert record["executive_mechanism"]
        assert record["proof_surfaces"]
        assert record["executable_paths"]
        assert record["removal_effect"]
        assert record["rationale"]


def test_live_code_audit_detects_live_tree_junk() -> None:
    # Build a tiny fake repo root to exercise junk detection without mutating the workspace.
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "cortex" / "core").mkdir(parents=True)
        (root / "cortex" / "runtime").mkdir(parents=True)
        (root / "cortex" / "sre").mkdir(parents=True)
        (root / "cortex" / "hosts").mkdir(parents=True)
        (root / "cortex" / "aux").mkdir(parents=True)
        (root / "cortex" / "core" / ".DS_Store").write_text("junk", encoding="utf-8")

        assert cortex_quality_audit._junk_paths(root) == ("cortex/core/.DS_Store",)


def test_live_code_audit_writes_generated_evidence_only() -> None:
    audit = cortex_quality_audit.build_live_code_audit(REPO_ROOT)
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        json_path, markdown_path = cortex_quality_audit.write_live_code_audit(
            audit,
            output_dir=output_dir,
        )

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")

        assert payload["scope"] == "live-code"
        assert payload["module_count"] == audit["module_count"]
        assert "Cortex Live Code Quality Audit" in markdown
        assert "## Summary" in markdown
        assert "## Host realizations" in markdown
