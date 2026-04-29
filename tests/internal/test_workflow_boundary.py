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
    workflow_doc = (REPO_ROOT / "docs" / "internal" / "REPO_WORKFLOW.md").read_text(encoding="utf-8")

    assert "cleanup-report:" in internal_makefile
    assert "audit-branches:" in internal_makefile
    assert "closeout-test:" in internal_makefile
    assert "closeout-init:" in internal_makefile
    assert "closeout-render:" in internal_makefile
    assert "closeout-validate:" in internal_makefile
    assert "finalize --manual-exception --message" in internal_makefile
    assert "scripts/repo_workflow.py is deprecated" in shim
    assert "internal/workflow/repo_workflow.py" in shim
    assert 'DEFAULT_ROOT = Path(__file__).resolve().parents[2]' in canonical
    assert 'help="Verify and commit the current manual/review branch; requires --manual-exception."' in canonical
    assert 'help="Checkpoint a managed session locally by default; add --publish to publish, merge, sync main, and delete the branch."' in canonical
    assert 'GitHub CLI `gh` is required for managed close-session publication.' in canonical
    assert 'def _publish_merge_sync_session(' in canonical
    assert 'def _managed_publication_allowed(' in canonical
    assert 'def _branch_has_unique_commits(' in canonical
    assert 'from internal.closeout import contract as closeout_contract' in canonical
    assert 'def _validate_closeout_contract_for_paths(' in canonical
    assert 'def _revalidate_closeout_contract_after_verification(' in canonical
    assert 'def _ensure_clean_tree_after_verification(' in canonical
    assert 'VERIFICATION_SCOPE_COMMANDS' in canonical
    assert 'def _verification_commands_for_paths(' in canonical
    assert 'def _run_verification_for_paths(' in canonical
    assert 'remote_managed_heads' in canonical
    assert '("make", "product-test")' in canonical
    assert '("make", "conformance-test")' in canonical
    assert '("make", "experimental-test")' in canonical
    assert '("python3", "internal/truth/generate_status.py", "--check")' in canonical
    assert '("python3", "internal/archive/generate_archive_index.py", "--check")' in canonical
    assert '("make", "-C", "internal", "test")' in canonical
    assert '("make", "lab-test")' in canonical
    assert '["make", "-C", "internal", "closeout-test"]' in canonical
    assert 'help="Fail unless the repo is on clean synced main with no extra worktrees, non-main branches, or remote managed/review heads."' in canonical
    assert "closeout contract" in workflow_doc.lower()
    assert "no-op exemption" in workflow_doc.lower()
    assert "reviewed-path drift during verification" in workflow_doc
    assert "closeout mirror" in workflow_doc
    assert "`AGENTS.md`, `docs/internal/REPO_WORKFLOW.md`, `internal/workflow/**`, `internal/closeout/**`, or `internal/Makefile`" in workflow_doc
    assert "Remote publication remains separate" not in workflow_doc
    assert "Checkpoint a managed session locally and keep the session branch open" in workflow_doc
    assert "close-session --publish" in workflow_doc
    assert 'returns `status: "checkpointed_local"`' in workflow_doc
    assert "Default to local-first checkpointing and make publication explicit." in workflow_doc
    assert "[skip ci]" in workflow_doc
    assert "skipped `push` or `pull_request` workflows can leave required checks pending and block merges" in workflow_doc
    assert "publishes the session branch, merges it, adopts `origin/main`" not in workflow_doc
    assert "smallest surface-aware verification bundle" in workflow_doc
    assert "Live CLI invocation contract" in workflow_doc
    assert "use the repo harness entrypoints" in workflow_doc
    assert "Gemini operator-lane auth defaults to `google_login`" in workflow_doc
    assert '`gemini -p "<prompt>" -o stream-json --approval-mode yolo`' in workflow_doc
    assert "interactive `gemini` only for sign-in or auth repair" in workflow_doc
    assert "--manual-exception" in workflow_doc
    assert 'no unique commits relative to `origin/main`' in workflow_doc
    assert 'repo is not back at resting truth' in workflow_doc
    assert '`status`, `published_branch`, `pr_number`, `pr_url`, `main_head`, and `main_sync`' in workflow_doc
    assert '`python3 internal/archive/generate_archive_index.py --check`' in workflow_doc
    assert "clean synced `main`" in workflow_doc


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
