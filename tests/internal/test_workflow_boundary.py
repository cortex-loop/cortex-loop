"""Internal-surface checks for the repo workflow boundary."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INTERNAL_MAKEFILE_PATH = REPO_ROOT / "internal" / "Makefile"
REPO_WORKFLOW_SHIM_PATH = REPO_ROOT / "scripts" / "repo_workflow.py"
REPO_WORKFLOW_CANONICAL_PATH = REPO_ROOT / "internal" / "workflow" / "repo_workflow.py"


def test_internal_workflow_surfaces_exist() -> None:
    internal_makefile = INTERNAL_MAKEFILE_PATH.read_text(encoding="utf-8")
    shim = REPO_WORKFLOW_SHIM_PATH.read_text(encoding="utf-8")
    canonical = REPO_WORKFLOW_CANONICAL_PATH.read_text(encoding="utf-8")

    assert "cleanup-report:" in internal_makefile
    assert "audit-branches:" in internal_makefile
    assert "scripts/repo_workflow.py is deprecated" in shim
    assert "internal/workflow/repo_workflow.py" in shim
    assert 'DEFAULT_ROOT = Path(__file__).resolve().parents[2]' in canonical
    assert '_run(["make", "product-test"])' in canonical
    assert '_run(["make", "conformance-test"])' in canonical
    assert '_run(["make", "experimental-test"])' in canonical
    assert '_run(["python3", "internal/truth/generate_status.py", "--check"])' in canonical
    assert '_run(["make", "-C", "internal", "test"])' in canonical
    assert '_run(["make", "lab-test"])' in canonical


def test_compatibility_wrappers_remain_callable_for_one_transition_cycle() -> None:
    commands = (
        [sys.executable, "tools/cortex_train_loop.py", "--help"],
        [sys.executable, "tools/cortex_output_quality.py", "--help"],
        [sys.executable, "scripts/repo_workflow.py", "audit-branches"],
    )

    for command in commands:
        proc = subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr or proc.stdout
