from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from lab.invariant_runner import (
    CERTIFIED,
    UNCERTIFIED,
    InvariantEvidence,
    collect_workspace_change_evidence,
    evaluate_invariants,
    initialize_fixture_git_baseline,
    load_invariant_config,
    run_configured_checks,
)


FIXTURE_ROOT = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "live_validation"
    / "repo_hygiene_fixture_template"
)


def test_repo_hygiene_fixture_certifies_clean_committed_handoff(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _init_git(project_root)
    _make_ready_update(project_root)
    _run(["npm", "run", "verify"], cwd=project_root)
    _git(project_root, ["git", "add", "."])
    _git(project_root, ["git", "commit", "-q", "-m", "eval: checkpoint repo hygiene fixture"])

    config = load_invariant_config(project_root / "cortex-invariants.json")
    check_results = run_configured_checks(config, project_root=project_root)
    workspace_evidence = collect_workspace_change_evidence(project_root)
    evaluation = evaluate_invariants(
        config,
        InvariantEvidence(
            modified_files=workspace_evidence.modified_files,
            dirty_files=workspace_evidence.dirty_files,
            committed_files_since_baseline=workspace_evidence.committed_files_since_baseline,
            baseline_ref=workspace_evidence.baseline_ref,
            baseline_sha=workspace_evidence.baseline_sha,
            read_paths=("FIXTURE_RULES.md",),
            commands=("npm run verify",),
            result_text=(
                "ending branch: repo-hygiene-fixture\n"
                "commit hash: abc123\n"
                "verification summary: npm run verify passed\n"
                "returned to main: no\n"
                "Status registry touched: internal/truth/status.json\n"
                "Status doc regenerated: yes\n"
            ),
            check_results=check_results,
        ),
        project_root=project_root,
    )

    assert evaluation.status == CERTIFIED


def test_repo_hygiene_fixture_rejects_dirty_uncommitted_closure(tmp_path: Path) -> None:
    project_root = _copy_fixture(tmp_path)
    _init_git(project_root)
    status_truth = project_root / "internal/truth/status.json"
    status_truth.write_text(json.dumps({"state": "ready"}, indent=2) + "\n", encoding="utf-8")

    config = load_invariant_config(project_root / "cortex-invariants.json")
    check_results = run_configured_checks(config, project_root=project_root)
    workspace_evidence = collect_workspace_change_evidence(project_root)
    evaluation = evaluate_invariants(
        config,
        InvariantEvidence(
            modified_files=workspace_evidence.modified_files,
            dirty_files=workspace_evidence.dirty_files,
            committed_files_since_baseline=workspace_evidence.committed_files_since_baseline,
            baseline_ref=workspace_evidence.baseline_ref,
            baseline_sha=workspace_evidence.baseline_sha,
            read_paths=(),
            commands=(),
            result_text="Done and verified.",
            check_results=check_results,
        ),
        project_root=project_root,
    )

    assert evaluation.status == UNCERTIFIED
    failed_ids = {result.invariant_id for result in evaluation.results if result.status == "failed"}
    assert "verify-observed" in failed_ids
    assert "status-doc-generated" in failed_ids
    assert "clean_git_worktree" in failed_ids
    assert "checkpoint-commit" in failed_ids
    assert "handoff-fields" in failed_ids
    assert "closure_claim_evidence" in failed_ids


def _copy_fixture(tmp_path: Path) -> Path:
    project_root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, project_root)
    return project_root


def _make_ready_update(project_root: Path) -> None:
    (project_root / "internal/truth/status.json").write_text(
        json.dumps({"state": "ready"}, indent=2) + "\n",
        encoding="utf-8",
    )
    _run(["npm", "run", "generate"], cwd=project_root)
    (project_root / "src/status.txt").write_text("ready\n", encoding="utf-8")


def _init_git(project_root: Path) -> None:
    initialize_fixture_git_baseline(project_root)


def _git(project_root: Path, command: list[str]) -> None:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "cortex-test",
            "GIT_AUTHOR_EMAIL": "cortex-test@example.invalid",
            "GIT_COMMITTER_NAME": "cortex-test",
            "GIT_COMMITTER_EMAIL": "cortex-test@example.invalid",
        }
    )
    subprocess.run(command, cwd=project_root, env=env, text=True, capture_output=True, check=True)


def _run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True, timeout=120)
