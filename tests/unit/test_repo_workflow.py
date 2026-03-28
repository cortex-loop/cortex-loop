from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _load_repo_workflow_module():
    script = ROOT / "scripts" / "repo_workflow.py"
    sys.path.insert(0, str(script.parent))
    spec = importlib.util.spec_from_file_location("repo_workflow", script)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _git_output(repo: Path, *args: str) -> str:
    run = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return run.stdout.strip()


def _prepare_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    remote = tmp_path / "origin.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True, text=True)

    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Cortex Test")
    _git(repo, "config", "user.email", "cortex@example.com")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "repo: initialize temp repo")
    _git(repo, "remote", "add", "origin", remote.as_uri())
    _git(repo, "push", "-u", "origin", "main")
    subprocess.run(
        ["git", f"--git-dir={remote}", "symbolic-ref", "HEAD", "refs/heads/main"],
        check=True,
        capture_output=True,
        text=True,
    )

    module = _load_repo_workflow_module()
    monkeypatch.setenv(module.ROOT_ENV_VAR, str(repo))
    return repo, remote, module


def _make_remote_commit(remote: Path, tmp_path: Path, filename: str, contents: str, message: str) -> None:
    worktree = tmp_path / f"remote-{filename.replace('.', '-')}"
    subprocess.run(["git", "clone", remote.as_uri(), str(worktree)], check=True, capture_output=True, text=True)
    _git(worktree, "config", "user.name", "Remote Test")
    _git(worktree, "config", "user.email", "remote@example.com")
    (worktree / filename).write_text(contents, encoding="utf-8")
    _git(worktree, "add", filename)
    _git(worktree, "commit", "-m", message)
    _git(worktree, "push", "origin", "main")


def test_start_session_from_clean_synced_main_creates_managed_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")

    module.cmd_start_session("codex", "repo-hygiene")

    assert _git_output(repo, "branch", "--show-current") == "codex/20260329-010203-repo-hygiene"
    assert capsys.readouterr().out.strip() == "codex/20260329-010203-repo-hygiene"


def test_start_session_refuses_on_dirty_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Working tree is not clean"):
        module.cmd_start_session("codex", "dirty-main")

    assert _git_output(repo, "branch", "--show-current") == "main"


def test_start_session_refuses_when_main_is_ahead(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    (repo / "local.txt").write_text("local\n", encoding="utf-8")
    _git(repo, "add", "local.txt")
    _git(repo, "commit", "-m", "docs: local only change")

    with pytest.raises(SystemExit, match="sync-main --adopt-origin"):
        module.cmd_start_session("codex", "ahead")


def test_start_session_refuses_when_main_diverges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, remote, module = _prepare_repo(tmp_path, monkeypatch)
    (repo / "local.txt").write_text("local\n", encoding="utf-8")
    _git(repo, "add", "local.txt")
    _git(repo, "commit", "-m", "docs: local only change")
    _make_remote_commit(remote, tmp_path, "remote.txt", "remote\n", "docs: remote update")

    with pytest.raises(SystemExit, match="sync-main --adopt-origin"):
        module.cmd_start_session("codex", "diverged")


def test_close_session_returns_to_main_and_deletes_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(module, "_run_verification_contract", lambda: None)
    module.cmd_start_session("codex", "closeout")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")

    module.cmd_close_session("docs: land managed session")

    assert _git_output(repo, "branch", "--show-current") == "main"
    assert _git_output(repo, "branch", "--list", branch) == ""
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "docs: land managed session"


def test_finalize_refuses_managed_session_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "managed")

    with pytest.raises(SystemExit, match="Use close-session"):
        module.cmd_finalize("docs: should fail")

    assert _git_output(repo, "branch", "--show-current") == "codex/20260329-010203-managed"


def test_finalize_commits_manual_branch_without_touching_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-work")
    monkeypatch.setattr(module, "_run_verification_contract", lambda: None)
    (repo / "manual.txt").write_text("manual\n", encoding="utf-8")

    module.cmd_finalize("docs: finalize manual branch")

    assert _git_output(repo, "branch", "--show-current") == "maint/manual-work"
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "docs: finalize manual branch"


def test_audit_branches_is_non_destructive_and_reports_categories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "codex/20260329-010203-merged")
    (repo / "merged.txt").write_text("merged\n", encoding="utf-8")
    _git(repo, "add", "merged.txt")
    _git(repo, "commit", "-m", "docs: merged branch")
    merged_branch = _git_output(repo, "branch", "--show-current")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--ff-only", merged_branch)

    _git(repo, "switch", "-c", "maint/manual-open")
    (repo / "manual.txt").write_text("manual\n", encoding="utf-8")
    _git(repo, "add", "manual.txt")
    _git(repo, "commit", "-m", "docs: manual branch")
    _git(repo, "switch", "main")

    worktree_path = tmp_path / "attached-worktree"
    _git(repo, "worktree", "add", "-b", "review/attached", str(worktree_path), "main")

    before_branches = _git_output(repo, "branch", "--format=%(refname:short)")
    module.cmd_audit_branches()
    after_branches = _git_output(repo, "branch", "--format=%(refname:short)")

    payload = json.loads(capsys.readouterr().out)
    assert payload["current_branch"] == "main"
    assert any(row["branch"] == merged_branch for row in payload["merged_local"])
    assert any(row["branch"] == "maint/manual-open" for row in payload["open_manual"])
    assert any(row["branch"] == "review/attached" for row in payload["worktree_attached"])
    assert before_branches == after_branches


def test_preserve_worktree_refuses_on_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    with pytest.raises(SystemExit, match="refuses on clean or dirty main"):
        module.cmd_preserve_worktree("main")


def test_preserve_worktree_creates_manual_preservation_branch_and_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "codex/dirty-work")
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")

    module.cmd_preserve_worktree("root-e1-verification")

    payload = json.loads(capsys.readouterr().out)
    assert payload["branch"] == "maint/preserved-20260329-010203-root-e1-verification"
    assert _git_output(repo, "branch", "--show-current") == payload["branch"]
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "docs: preserve worktree snapshot for root-e1-verification"
    assert (repo / "dirty.txt").exists()
    assert (repo / "untracked.txt").exists()


def test_preserve_worktree_excludes_nested_attached_worktrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "codex/dirty-work")
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    (repo / ".gitignore").write_text(".claude/worktrees/\n", encoding="utf-8")
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    attached_path = repo / ".claude" / "worktrees" / "attached"
    attached_path.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "-b", "review/attached", str(attached_path), "main")

    module.cmd_preserve_worktree("nested")

    payload = json.loads(capsys.readouterr().out)
    assert _git_output(repo, "branch", "--show-current") == payload["branch"]
    assert _git_output(repo, "ls-files", "--stage", "--", ".claude/worktrees/attached") == ""
    changed_files = _git_output(repo, "show", "--name-only", "--pretty=", payload["commit"]).splitlines()
    assert "dirty.txt" in changed_files
    assert ".claude/worktrees/attached" not in changed_files


def test_preserve_worktree_refuses_when_attached_worktree_paths_are_already_tracked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "codex/dirty-work")
    attached_path = repo / ".claude" / "worktrees" / "attached"
    attached_path.parent.mkdir(parents=True, exist_ok=True)
    _git(repo, "worktree", "add", "-b", "review/attached", str(attached_path), "main")
    _git(repo, "add", ".claude/worktrees/attached")

    with pytest.raises(SystemExit, match="attached worktree paths are already tracked"):
        module.cmd_preserve_worktree("nested")
