from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from internal.closeout import contract as closeout_contract


ROOT = Path(__file__).resolve().parents[2]


def _load_repo_workflow_module():
    script = ROOT / "internal" / "workflow" / "repo_workflow.py"
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
    (repo / ".gitignore").write_text(".cortex/closeout_contract/\n", encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", "README.md")
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


def _write_closeout_contract(
    repo: Path,
    *,
    branch: str,
    mode: str,
    reviewed_paths: list[str],
    surface: str = "internal",
    profile_override: str | None = None,
) -> None:
    payload = closeout_contract.scaffold_payload(branch=branch, mode=mode, reviewed_paths=reviewed_paths)
    if profile_override is not None:
        payload["profile"] = profile_override
        if profile_override == "standard":
            payload.pop("governing_locks", None)
            payload.pop("law_to_code_completeness", None)
    payload["seam"] = {
        "slug": "closeout-enforcement",
        "surface": surface,
        "executive_benefit": "Prevent overclaiming at closeout.",
        "why_now": "The workflow must gate S-tier closure rigor mechanically.",
    }
    payload["residuals"] = {
        "fixed_now": ["Workflow closeout rigor is explicit."],
        "intentionally_deferred": ["No broader runtime or doctrine change."],
        "still_underfit": ["No residual issue remains in this test fixture."],
        "zeroed_or_stubbed_terms": [],
    }
    payload["hostile_review"] = {
        "engineer": "No material workflow hole remains.",
        "mathematician": "The gate is explicit and typed.",
        "neuroscientist": "No false executive claim is introduced.",
    }
    payload["claims"] = {
        "earned_now": ["This closeout is reviewable and bounded."],
        "forbidden_still": ["No broader product lift is claimed from workflow alone."],
    }
    payload["north_light_audit"] = {
        "microkernel_boundary": {"status": "pass", "note": "No product policy moved into core."},
        "repo_governance_leakage": {"status": "pass", "note": "Internal workflow remains internal."},
        "host_specific_policy_fork": {"status": "pass", "note": "No host behavior changed."},
        "generic_bloat": {"status": "pass", "note": "The gate only applies at closure."},
    }
    if payload["profile"] == "load_bearing":
        payload["governing_locks"] = {
            "governing_principle": "Truthful closure outranks local confidence.",
            "executive_skill": "Residual rigor at workflow handoff is the load-bearing skill.",
            "product_metric": "No substantive closeout bypasses residual accounting.",
            "guardrail": "No second operational truth surface.",
            "kill_rule": "Cut any path that permits silent overclaiming.",
        }
        payload["law_to_code_completeness"] = [
            {
                "term": "workflow closeout rigor",
                "state": "implemented",
                "code_refs": [reviewed_paths[0]],
                "proof_refs": ["tests/internal/test_repo_workflow.py"],
                "note": "Representative row for the touched path set.",
            }
        ]
        if any(closeout_contract.is_cortex_path(path) for path in reviewed_paths):
            payload["connectivity_trace"] = {
                "claim": "Workflow closeout rigor protects cortex/** seams from drift.",
                "path": [
                    reviewed_paths[0],
                    "cortex/runtime adapter binding",
                    "model request shaping",
                ],
                "if_empty_why": None,
            }
    closeout_contract.write_artifacts(repo, payload)


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


def test_close_session_checkpoint_keeps_session_branch_and_main_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda _paths: ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    module.cmd_start_session("codex", "closeout")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    module.cmd_close_session("docs: land managed session", publish=False)

    assert _git_output(repo, "branch", "--show-current") == branch
    assert branch in _git_output(repo, "branch", "--list", branch)
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "docs: land managed session"
    assert _git_output(repo, "log", "main", "-1", "--pretty=%s") == "repo: initialize temp repo"
    assert _git_output(repo, "rev-list", "--left-right", "--count", f"{branch}...origin/main") == "1\t0"


def test_close_session_noop_deletes_empty_session_branch_without_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "noop")
    branch = _git_output(repo, "branch", "--show-current")

    module.cmd_close_session("docs: noop closeout", publish=False)

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "no_op"
    assert payload["published_branch"] is None
    assert _git_output(repo, "branch", "--show-current") == "main"
    assert _git_output(repo, "branch", "--list", branch) == ""


def test_close_session_noop_adopts_origin_main_when_upstream_advanced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "noop-upstream")
    branch = _git_output(repo, "branch", "--show-current")

    _make_remote_commit(remote, tmp_path, "remote.txt", "remote\n", "docs: remote update")

    module.cmd_close_session("docs: noop closeout", publish=False)

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "no_op"
    assert payload["published_branch"] is None
    assert payload["main_sync"] == "synced"
    assert payload["main_head"] == _git_output(repo, "rev-parse", "origin/main")
    assert _git_output(repo, "branch", "--show-current") == "main"
    assert _git_output(repo, "branch", "--list", branch) == ""
    assert _git_output(repo, "rev-list", "--left-right", "--count", "main...origin/main") == "0\t0"


def test_close_session_keeps_session_branch_when_publication_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda _paths: ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    monkeypatch.setattr(module, "_managed_publication_allowed", lambda: True)
    module.cmd_start_session("codex", "gh-fail")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    def fail_publish_merge_sync_session(_branch: str, _title: str, _verification_commands: tuple[str, ...]) -> dict[str, object]:
        raise SystemExit("gh auth status failed")

    monkeypatch.setattr(module, "_publish_merge_sync_session", fail_publish_merge_sync_session)

    with pytest.raises(SystemExit, match="gh auth status failed"):
        module.cmd_close_session("docs: publication fail", publish=True)

    assert _git_output(repo, "branch", "--show-current") == branch
    assert _git_output(repo, "log", "main", "-1", "--pretty=%s") == "repo: initialize temp repo"
    assert _git_output(repo, "log", "HEAD", "-1", "--pretty=%s") == "docs: publication fail"


def test_close_session_with_existing_unique_commit_checkpoints_locally_when_tree_is_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda _paths: ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    module.cmd_start_session("codex", "existing-commit")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "docs: preexisting session commit")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    verification_paths: list[list[str]] = []

    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda paths: verification_paths.append(paths) or ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    monkeypatch.setattr(
        module,
        "_fetch_origin",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("default checkpoint should not fetch origin")),
    )
    monkeypatch.setattr(
        module,
        "_publish_merge_sync_session",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("default checkpoint should not publish managed sessions")
        ),
    )

    module.cmd_close_session("docs: close existing session commit", publish=False)

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "checkpointed_local"
    assert payload["published_branch"] is None
    assert payload["pr_number"] is None
    assert payload["pr_url"] is None
    assert verification_paths == [["README.md"]]
    assert _git_output(repo, "branch", "--show-current") == branch
    assert branch in _git_output(repo, "branch", "--list", branch)
    assert payload["main_head"] == _git_output(repo, "rev-parse", "main")


def test_close_session_keeps_session_branch_when_pr_creation_fails_after_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda _paths: ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    monkeypatch.setattr(module, "_managed_publication_allowed", lambda: True)
    module.cmd_start_session("codex", "pr-fail")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    def fail_after_push(session_branch: str, _title: str, _verification_commands: tuple[str, ...]) -> dict[str, object]:
        _git(repo, "push", "-u", "origin", session_branch)
        raise SystemExit("PR creation failed")

    monkeypatch.setattr(module, "_publish_merge_sync_session", fail_after_push)

    with pytest.raises(SystemExit, match="PR creation failed"):
        module.cmd_close_session("docs: pr creation fail", publish=True)

    assert _git_output(repo, "branch", "--show-current") == branch
    assert _git_output(repo, "log", "main", "-1", "--pretty=%s") == "repo: initialize temp repo"
    assert _git_output(repo, "log", "HEAD", "-1", "--pretty=%s") == "docs: pr creation fail"


def test_finalize_refuses_managed_session_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "managed")

    with pytest.raises(SystemExit, match="Use close-session"):
        module.cmd_finalize("docs: should fail", manual_exception=True)

    assert _git_output(repo, "branch", "--show-current") == "codex/20260329-010203-managed"


def test_finalize_requires_manual_exception_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-work")

    with pytest.raises(SystemExit, match="requires --manual-exception"):
        module.cmd_finalize("docs: finalize manual branch", manual_exception=False)

    assert _git_output(repo, "branch", "--show-current") == "maint/manual-work"


def test_finalize_commits_manual_branch_without_touching_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-work")
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check", "make product-test"))
    (repo / "manual.txt").write_text("manual\n", encoding="utf-8")
    _write_closeout_contract(repo, branch="maint/manual-work", mode="finalize", reviewed_paths=["manual.txt"])

    module.cmd_finalize("docs: finalize manual branch", manual_exception=True)

    assert _git_output(repo, "branch", "--show-current") == "maint/manual-work"
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "docs: finalize manual branch"


def test_finalize_requires_valid_closeout_contract_before_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-work")
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check", "make product-test"))
    (repo / "manual.txt").write_text("manual\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Closeout contract is missing"):
        module.cmd_finalize("docs: finalize manual branch", manual_exception=True)

    assert _git_output(repo, "branch", "--show-current") == "maint/manual-work"
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "repo: initialize temp repo"


def test_close_session_requires_valid_closeout_contract_before_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "closeout-rigor")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Closeout contract is missing"):
        module.cmd_close_session("docs: closeout rigor", publish=False)

    assert _git_output(repo, "branch", "--show-current") == branch
    assert _git_output(repo, "log", "main", "-1", "--pretty=%s") == "repo: initialize temp repo"


def test_close_session_load_bearing_paths_require_load_bearing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/load-bearing")
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check", "make product-test"))
    target = repo / "cortex" / "sre" / "persistence.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("pass\n", encoding="utf-8")
    _write_closeout_contract(
        repo,
        branch="maint/load-bearing",
        mode="finalize",
        reviewed_paths=["cortex/sre/persistence.py"],
        surface="product",
        profile_override="standard",
    )

    with pytest.raises(SystemExit, match="profile mismatch: expected 'load_bearing'"):
        module.cmd_finalize("docs: finalize manual branch", manual_exception=True)


def test_finalize_workflow_law_paths_require_load_bearing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/workflow-law")
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check", "make -C internal test"))
    (repo / "AGENTS.md").write_text("workflow law\n", encoding="utf-8")
    _write_closeout_contract(
        repo,
        branch="maint/workflow-law",
        mode="finalize",
        reviewed_paths=["AGENTS.md"],
        profile_override="standard",
    )

    with pytest.raises(SystemExit, match="profile mismatch: expected 'load_bearing'"):
        module.cmd_finalize("docs: finalize manual branch", manual_exception=True)


def test_finalize_fails_when_verification_changes_reviewed_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-work")
    (repo / "manual.txt").write_text("manual\n", encoding="utf-8")
    _write_closeout_contract(repo, branch="maint/manual-work", mode="finalize", reviewed_paths=["manual.txt"])

    def mutate_paths(_paths: list[str]) -> tuple[str, ...]:
        (repo / "verification.txt").write_text("drift\n", encoding="utf-8")
        return ("git diff --check",)

    monkeypatch.setattr(module, "_run_verification_for_paths", mutate_paths)

    with pytest.raises(SystemExit, match="verification changed tracked paths after closeout contract validation"):
        module.cmd_finalize("docs: finalize manual branch", manual_exception=True)

    assert _git_output(repo, "branch", "--show-current") == "maint/manual-work"
    assert _git_output(repo, "log", "-1", "--pretty=%s") == "repo: initialize temp repo"


def test_close_session_with_existing_unique_commit_revalidates_after_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "revalidate-existing-commit")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "docs: preexisting session commit")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    calls: list[tuple[str, str, tuple[str, ...]]] = []
    original_validate = module._validate_closeout_contract_for_paths

    def record_validate(mode: str, branch_name: str, reviewed_paths: list[str]) -> None:
        calls.append((mode, branch_name, tuple(reviewed_paths)))
        original_validate(mode, branch_name, reviewed_paths)

    monkeypatch.setattr(module, "_validate_closeout_contract_for_paths", record_validate)
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check",))

    module.cmd_close_session("docs: close existing session commit", publish=False)

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "checkpointed_local"
    assert calls == [
        ("close-session", branch, ("README.md",)),
        ("close-session", branch, ("README.md",)),
    ]
    assert _git_output(repo, "branch", "--show-current") == branch


def test_close_session_existing_unique_commit_fails_when_verification_dirties_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    module.cmd_start_session("codex", "verification-drift")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "docs: preexisting session commit")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    def mutate_tree(_paths: list[str]) -> tuple[str, ...]:
        (repo / "verification.txt").write_text("drift\n", encoding="utf-8")
        return ("git diff --check",)

    monkeypatch.setattr(module, "_run_verification_for_paths", mutate_tree)

    with pytest.raises(SystemExit, match="verification changed tracked paths after closeout contract validation"):
        module.cmd_close_session("docs: close existing session commit", publish=False)

    assert _git_output(repo, "branch", "--show-current") == branch


def test_publish_merge_sync_session_reuses_existing_open_pr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(module, "_ensure_canonical_origin", lambda: None)
    monkeypatch.setattr(module, "_ensure_gh_ready", lambda: None)
    monkeypatch.setattr(module, "_fetch_origin", lambda quiet=False: calls.append(("fetch", quiet)))
    monkeypatch.setattr(
        module,
        "_session_pull_request",
        lambda branch: {
            "number": 11,
            "state": "OPEN",
            "url": f"https://example.test/{branch}",
            "isDraft": False,
        },
    )
    monkeypatch.setattr(module, "_push_session_branch", lambda branch: calls.append(("push", branch)))
    monkeypatch.setattr(
        module,
        "_create_session_pull_request",
        lambda branch, title, verification_commands: calls.append(("create", branch, title, verification_commands)),
    )
    monkeypatch.setattr(module, "_mark_pull_request_ready", lambda number: calls.append(("ready", number)))
    monkeypatch.setattr(module, "_merge_session_pull_request", lambda number: calls.append(("merge", number)))
    monkeypatch.setattr(
        module,
        "_adopt_origin_main",
        lambda: calls.append(("adopt", None)) or "abc123",
    )
    monkeypatch.setattr(module, "_delete_branch", lambda branch: calls.append(("delete", branch)))
    monkeypatch.setattr(module, "_main_origin_state", lambda: "synced")

    payload = module._publish_merge_sync_session(
        "codex/20260329-010203-test", "docs: test", ("git diff --check", "make product-test")
    )

    assert payload == {
        "status": "merged",
        "published_branch": "codex/20260329-010203-test",
        "pr_number": 11,
        "pr_url": "https://example.test/codex/20260329-010203-test",
        "main_head": "abc123",
        "main_sync": "synced",
    }
    assert ("push", "codex/20260329-010203-test") in calls
    assert ("merge", 11) in calls
    assert not any(call[0] == "create" for call in calls)


def test_close_session_publish_preserves_current_remote_merge_flow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(
        module,
        "_run_verification_for_paths",
        lambda _paths: ("git diff --check", "python3 internal/truth/generate_status.py --check"),
    )
    monkeypatch.setattr(module, "_managed_publication_allowed", lambda: True)
    module.cmd_start_session("codex", "publish-closeout")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    def fake_publish_merge_sync_session(
        session_branch: str, title: str, verification_commands: tuple[str, ...]
    ) -> dict[str, object]:
        assert session_branch == branch
        assert title == "docs: publish managed session"
        assert verification_commands
        _git(repo, "push", "-u", "origin", session_branch)
        _git(repo, "switch", "main")
        _git(repo, "merge", "--ff-only", session_branch)
        _git(repo, "push", "origin", "main")
        _git(repo, "branch", "-D", session_branch)
        return {
            "status": "merged",
            "published_branch": session_branch,
            "pr_number": 22,
            "pr_url": "https://example.test/pr/22",
            "main_head": _git_output(repo, "rev-parse", "main"),
            "main_sync": "synced",
        }

    monkeypatch.setattr(module, "_publish_merge_sync_session", fake_publish_merge_sync_session)

    module.cmd_close_session("docs: publish managed session", publish=True)

    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "merged"
    assert _git_output(repo, "branch", "--show-current") == "main"
    assert _git_output(repo, "branch", "--list", branch) == ""


def test_close_session_publish_requires_canonical_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260329-010203")
    monkeypatch.setattr(module, "_managed_publication_allowed", lambda: False)
    monkeypatch.setattr(module, "_run_verification_for_paths", lambda _paths: ("git diff --check",))
    module.cmd_start_session("codex", "publish-gate")
    branch = _git_output(repo, "branch", "--show-current")
    (repo / "README.md").write_text("changed\n", encoding="utf-8")
    _write_closeout_contract(repo, branch=branch, mode="close-session", reviewed_paths=["README.md"])

    with pytest.raises(SystemExit, match="requires the canonical repo origin"):
        module.cmd_close_session("docs: publish managed session", publish=True)

    assert _git_output(repo, "branch", "--show-current") == branch


def test_publish_merge_sync_session_creates_pr_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(module, "_ensure_canonical_origin", lambda: None)
    monkeypatch.setattr(module, "_ensure_gh_ready", lambda: None)
    monkeypatch.setattr(module, "_fetch_origin", lambda quiet=False: None)
    monkeypatch.setattr(module, "_session_pull_request", lambda _branch: None)
    monkeypatch.setattr(module, "_push_session_branch", lambda branch: calls.append(("push", branch)))
    monkeypatch.setattr(
        module,
        "_create_session_pull_request",
        lambda branch, title, verification_commands: calls.append(("create", branch, title, verification_commands))
        or {"number": 14, "state": "OPEN", "url": "https://example.test/pr/14", "isDraft": False},
    )
    monkeypatch.setattr(module, "_merge_session_pull_request", lambda number: calls.append(("merge", number)))
    monkeypatch.setattr(module, "_adopt_origin_main", lambda: "created123")
    monkeypatch.setattr(module, "_delete_branch", lambda branch: calls.append(("delete", branch)))
    monkeypatch.setattr(module, "_main_origin_state", lambda: "synced")

    payload = module._publish_merge_sync_session(
        "codex/20260329-010203-create", "docs: create", ("git diff --check", "make conformance-test")
    )

    assert payload["pr_number"] == 14
    assert ("push", "codex/20260329-010203-create") in calls
    assert ("create", "codex/20260329-010203-create", "docs: create", ("git diff --check", "make conformance-test")) in calls
    assert ("merge", 14) in calls


def test_publish_merge_sync_session_skips_push_when_pr_is_already_merged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(module, "_ensure_canonical_origin", lambda: None)
    monkeypatch.setattr(module, "_ensure_gh_ready", lambda: None)
    monkeypatch.setattr(module, "_fetch_origin", lambda quiet=False: calls.append(("fetch", quiet)))
    monkeypatch.setattr(
        module,
        "_session_pull_request",
        lambda _branch: {"number": 12, "state": "MERGED", "url": "https://example.test/pr/12", "isDraft": False},
    )
    monkeypatch.setattr(module, "_branch_merged_into_origin_main", lambda _branch: True)
    monkeypatch.setattr(module, "_push_session_branch", lambda branch: calls.append(("push", branch)))
    monkeypatch.setattr(module, "_merge_session_pull_request", lambda number: calls.append(("merge", number)))
    monkeypatch.setattr(module, "_adopt_origin_main", lambda: calls.append(("adopt", None)) or "merged123")
    monkeypatch.setattr(module, "_delete_branch", lambda branch: calls.append(("delete", branch)))
    monkeypatch.setattr(module, "_main_origin_state", lambda: "synced")

    payload = module._publish_merge_sync_session(
        "codex/20260329-010203-test", "docs: merged", ("git diff --check", "make product-test")
    )

    assert payload["status"] == "already_merged"
    assert payload["pr_number"] == 12
    assert ("push", "codex/20260329-010203-test") not in calls
    assert ("adopt", None) in calls


def test_publish_merge_sync_session_already_merged_payload_deletes_local_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(module, "_ensure_canonical_origin", lambda: None)
    monkeypatch.setattr(module, "_ensure_gh_ready", lambda: None)
    monkeypatch.setattr(module, "_fetch_origin", lambda quiet=False: None)
    monkeypatch.setattr(
        module,
        "_session_pull_request",
        lambda _branch: {"number": 21, "state": "MERGED", "url": "https://example.test/pr/21", "isDraft": False},
    )
    monkeypatch.setattr(module, "_branch_merged_into_origin_main", lambda _branch: True)
    monkeypatch.setattr(module, "_adopt_origin_main", lambda: "merged456")
    monkeypatch.setattr(module, "_delete_branch", lambda branch: calls.append(("delete", branch)))
    monkeypatch.setattr(module, "_main_origin_state", lambda: "synced")

    payload = module._publish_merge_sync_session(
        "codex/20260329-010203-already-merged", "docs: merged", ("git diff --check", "make product-test")
    )

    assert payload == {
        "status": "already_merged",
        "published_branch": "codex/20260329-010203-already-merged",
        "pr_number": 21,
        "pr_url": "https://example.test/pr/21",
        "main_head": "merged456",
        "main_sync": "synced",
    }
    assert ("delete", "codex/20260329-010203-already-merged") in calls


def test_publish_merge_sync_session_refuses_closed_unmerged_pr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    monkeypatch.setattr(module, "_ensure_canonical_origin", lambda: None)
    monkeypatch.setattr(module, "_ensure_gh_ready", lambda: None)
    monkeypatch.setattr(module, "_fetch_origin", lambda quiet=False: None)
    monkeypatch.setattr(
        module,
        "_session_pull_request",
        lambda _branch: {"number": 13, "state": "CLOSED", "url": "https://example.test/pr/13", "isDraft": False},
    )

    with pytest.raises(SystemExit, match="closed unmerged PR"):
        module._publish_merge_sync_session(
            "codex/20260329-010203-test", "docs: closed", ("git diff --check", "make product-test")
        )


def test_verification_commands_for_internal_paths_stay_internal_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    commands = module._verification_commands_for_paths(
        ["internal/workflow/repo_workflow.py", "docs/internal/REPO_WORKFLOW.md", "tests/internal/test_repo_workflow.py"]
    )

    assert tuple(module._command_text(command) for command in commands) == (
        "git diff --check",
        "python3 internal/truth/generate_status.py --check",
        "python3 internal/archive/generate_archive_index.py --check",
        "make -C internal test",
    )


def test_verification_commands_for_shared_sre_paths_cover_product_and_experimental(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    commands = module._verification_commands_for_paths(["cortex/sre/preservation.py"])

    assert tuple(module._command_text(command) for command in commands) == (
        "git diff --check",
        "make product-test",
        "make experimental-test",
    )


def test_verification_commands_for_unknown_root_path_fall_back_to_full_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    commands = module._verification_commands_for_paths(["pyproject.toml"])

    assert tuple(module._command_text(command) for command in commands) == (
        "git diff --check",
        "make product-test",
        "make conformance-test",
        "make experimental-test",
        "python3 internal/truth/generate_status.py --check",
        "python3 internal/archive/generate_archive_index.py --check",
        "make -C internal test",
        "make lab-test",
    )


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


def test_cleanup_report_passes_on_clean_synced_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    real_run = module.subprocess.run

    def run_with_closeout_stub(*args, **kwargs):
        command = args[0] if args else kwargs.get("args")
        if command == ["make", "-C", "internal", "closeout-test"]:
            return module.subprocess.CompletedProcess(command, 0, "", "")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", run_with_closeout_stub)

    result = module.cmd_cleanup_report()

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["ok"] is True
    assert payload["current_branch"] == "main"
    assert payload["main_sync"] == "synced"
    assert payload["remote_managed_heads"] == []
    assert payload["status"] == "clean"


def test_cleanup_report_fails_when_repo_has_residual_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "maint/manual-open")
    (repo / "manual-committed.txt").write_text("manual\n", encoding="utf-8")
    _git(repo, "add", "manual-committed.txt")
    _git(repo, "commit", "-m", "docs: manual branch")
    (repo / "manual-dirty.txt").write_text("dirty\n", encoding="utf-8")

    worktree_path = tmp_path / "attached-worktree"
    _git(repo, "worktree", "add", "-b", "review/attached", str(worktree_path), "main")
    _git(repo, "push", "origin", "main:codex/20260329-010203-leftover")
    _git(repo, "push", "origin", "main:review/leftover")

    result = module.cmd_cleanup_report()

    payload = json.loads(capsys.readouterr().out)
    assert result == 1
    assert payload["ok"] is False
    assert payload["current_branch"] == "maint/manual-open"
    assert payload["main_sync"] == "synced"
    failures = payload["failures"]
    assert failures["current_branch"] == "maint/manual-open"
    assert any("manual-dirty.txt" in line for line in failures["dirty"])
    assert any(row["branch"] == "maint/manual-open" for row in failures["open_manual"])
    assert any(row["branch"] == "review/attached" for row in failures["worktree_attached"])
    assert "codex/20260329-010203-leftover" in failures["remote_managed_heads"]
    assert "review/leftover" in failures["remote_review_heads"]


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


# ---------------------------------------------------------------------------
# Branch-hygiene gate: start-session blocks on unmerged managed branches;
# resume-session is the legitimate continuation path. See AGENTS.md
# `## Anti-Drift` for the historical context.
# ---------------------------------------------------------------------------


def test_start_session_blocks_when_an_unmerged_managed_branch_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    # Pre-create a managed session branch with unique work so it is not an
    # ancestor of origin/main.
    _git(repo, "switch", "-c", "claude/20260101-010101-prior-work")
    (repo / "prior.txt").write_text("prior\n", encoding="utf-8")
    _git(repo, "add", "prior.txt")
    _git(repo, "commit", "-m", "tests: stage prior session artifact")
    _git(repo, "switch", "main")

    with pytest.raises(SystemExit) as excinfo:
        module.cmd_start_session("codex", "fresh-work")

    message = str(excinfo.value)
    assert "Cannot start a new session" in message
    assert "claude/20260101-010101-prior-work" in message
    assert "resume-session" in message
    assert "--allow-stacked" in message
    assert _git_output(repo, "branch", "--show-current") == "main"


def test_start_session_succeeds_on_clean_main_with_no_unmerged_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260601-010203")

    module.cmd_start_session("codex", "clean-start")

    assert _git_output(repo, "branch", "--show-current") == "codex/20260601-010203-clean-start"


def test_start_session_excludes_current_branch_when_already_on_managed_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the agent is already on a merged managed branch, start-session's
    existing path (switch to main, delete the branch, start fresh) must not
    block on the branch the agent is leaving."""
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260601-010204")
    # Create + merge a managed branch so it is an ancestor of origin/main.
    _git(repo, "switch", "-c", "claude/20260101-020202-merged-prior")
    (repo / "merged.txt").write_text("merged\n", encoding="utf-8")
    _git(repo, "add", "merged.txt")
    _git(repo, "commit", "-m", "tests: prior merged work")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--ff-only", "claude/20260101-020202-merged-prior")
    _git(repo, "push", "origin", "main")
    _git(repo, "switch", "claude/20260101-020202-merged-prior")

    module.cmd_start_session("codex", "fresh-after-merged")

    assert _git_output(repo, "branch", "--show-current") == "codex/20260601-010204-fresh-after-merged"


def test_start_session_allow_stacked_requires_stacked_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    with pytest.raises(SystemExit, match="--stacked-reason"):
        module.cmd_start_session(
            "codex",
            "stacked-without-reason",
            allow_stacked=True,
            stacked_reason=None,
        )

    assert _git_output(repo, "branch", "--show-current") == "main"


def test_start_session_allow_stacked_with_reason_bypasses_block_and_records_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260601-010205")
    _git(repo, "switch", "-c", "claude/20260101-030303-blocking-prior")
    (repo / "blocker.txt").write_text("blocker\n", encoding="utf-8")
    _git(repo, "add", "blocker.txt")
    _git(repo, "commit", "-m", "tests: blocking prior work")
    _git(repo, "switch", "main")

    module.cmd_start_session(
        "codex",
        "emergency-hotfix",
        allow_stacked=True,
        stacked_reason="emergency hotfix while investigation is in flight",
    )

    branch = "codex/20260601-010205-emergency-hotfix"
    assert _git_output(repo, "branch", "--show-current") == branch
    marker = (
        repo
        / ".cortex"
        / "closeout_contract"
        / Path(*branch.split("/"))
        / "stacked_session_reason.txt"
    )
    assert marker.exists()
    assert "emergency hotfix while investigation is in flight" in marker.read_text(encoding="utf-8")


def test_resume_session_requires_slug_or_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)

    with pytest.raises(SystemExit, match="--slug"):
        module.cmd_resume_session(None, None)


def test_resume_session_checks_out_unique_slug_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "claude/20260101-040404-resume-target")
    (repo / "resume.txt").write_text("resume\n", encoding="utf-8")
    _git(repo, "add", "resume.txt")
    _git(repo, "commit", "-m", "tests: resume-target work")
    _git(repo, "switch", "main")

    module.cmd_resume_session("resume-target", None)

    assert _git_output(repo, "branch", "--show-current") == "claude/20260101-040404-resume-target"
    captured = capsys.readouterr().out
    assert "Resumed: claude/20260101-040404-resume-target" in captured
    assert "commit(s) ahead of origin/main" in captured
    assert "closeout contract:" in captured


def test_resume_session_lists_available_when_slug_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "claude/20260101-050505-existing")
    (repo / "existing.txt").write_text("existing\n", encoding="utf-8")
    _git(repo, "add", "existing.txt")
    _git(repo, "commit", "-m", "tests: existing work")
    _git(repo, "switch", "main")

    with pytest.raises(SystemExit) as excinfo:
        module.cmd_resume_session("nonexistent-slug", None)

    message = str(excinfo.value)
    assert "No managed session branch found with slug 'nonexistent-slug'" in message
    assert "claude/20260101-050505-existing" in message


def test_resume_session_disambiguates_when_multiple_slug_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    for stamp in ("20260101-060601", "20260201-060602"):
        branch = f"claude/{stamp}-shared-slug"
        _git(repo, "switch", "-c", branch, "main")
        (repo / f"{stamp}.txt").write_text(f"{stamp}\n", encoding="utf-8")
        _git(repo, "add", f"{stamp}.txt")
        _git(repo, "commit", "-m", f"tests: {stamp} work")
    _git(repo, "switch", "main")

    with pytest.raises(SystemExit) as excinfo:
        module.cmd_resume_session("shared-slug", None)

    message = str(excinfo.value)
    assert "Multiple managed session branches match slug 'shared-slug'" in message
    assert "--branch <full-name>" in message


def test_resume_session_with_explicit_branch_flag_bypasses_slug_matching(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "claude/20260101-070707-explicit-target")
    (repo / "explicit.txt").write_text("explicit\n", encoding="utf-8")
    _git(repo, "add", "explicit.txt")
    _git(repo, "commit", "-m", "tests: explicit-target work")
    _git(repo, "switch", "main")

    module.cmd_resume_session(None, "claude/20260101-070707-explicit-target")

    assert _git_output(repo, "branch", "--show-current") == "claude/20260101-070707-explicit-target"


def test_resume_session_rejects_non_managed_branch_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "review/some-branch")
    (repo / "review.txt").write_text("review\n", encoding="utf-8")
    _git(repo, "add", "review.txt")
    _git(repo, "commit", "-m", "tests: review work")
    _git(repo, "switch", "main")

    with pytest.raises(SystemExit, match="not a managed session branch"):
        module.cmd_resume_session(None, "review/some-branch")


def test_resume_session_refuses_dirty_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _git(repo, "switch", "-c", "claude/20260101-080808-resume-dirty")
    (repo / "drift.txt").write_text("drift\n", encoding="utf-8")
    _git(repo, "add", "drift.txt")
    _git(repo, "commit", "-m", "tests: target work")
    _git(repo, "switch", "main")
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Working tree is not clean"):
        module.cmd_resume_session("resume-dirty", None)


# ---------------------------------------------------------------------------
# Hygiene grid commands: status-snapshot / reflection-check / grid.
# ---------------------------------------------------------------------------


def _seed_registry(repo: Path) -> None:
    """Write and commit a minimal cortex_status.json with grid-reading fields."""
    registry_path = repo / "internal" / "truth" / "cortex_status.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        json.dumps(
            {
                "work_today": {"slug": "active-train"},
                "next_product_train": {
                    "slug": "queued-train",
                    "last_reviewed_at": "2026-04-29T00:00:00+00:00",
                },
                "research_lines_under_evaluation": [],
                "executive_completion": {"shippable_threshold_percent": 85},
                "bio_to_code_matrix": [
                    {
                        "skill": "Truth-preserving commitments",
                        "stolen_skill": "Truth maintenance",
                        "status": "landed",
                        "weight": 100,
                        "code_homes": ["cortex/core"],
                        "proof_surfaces": ["tests/product"],
                        "next_move": "hold steady",
                    }
                ],
                "hosts": [
                    {"name": "openai", "conformance": "conformant", "shipping": "default", "strongest_surface": "operator_cli", "code_home": "cortex/hosts/openai"}
                ],
                "conformance_summary": {
                    "shipping_default": "openai:operator_cli",
                    "accepted_next_decision": "promote",
                },
                "where_to_work": ["Hold the shipped lane stable."],
            }
        ),
        encoding="utf-8",
    )
    _git(repo, "add", "internal/truth/cortex_status.json")
    _git(repo, "commit", "-m", "tests: seed registry for grid")
    _git(repo, "push", "origin", "main")


def test_status_snapshot_returns_branch_state_and_drift_signals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)

    payload = module._status_snapshot_payload()

    assert payload["branch"] == "main"
    assert payload["worktree"] == "clean"
    assert payload["closeout"]["present"] == "absent"
    assert payload["work_today_slug"] == "active-train"
    assert payload["next_train_slug"] == "queued-train"
    assert isinstance(payload["next_train_reviewed_days_ago"], int)
    assert payload["next_train_reviewed_days_ago"] >= 0


def test_status_snapshot_emits_markdown_format(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)

    module.cmd_status_snapshot(False)
    out = capsys.readouterr().out

    # Markdown styling (Session 3): header + 2-column table.
    assert "## Cortex Repo State" in out
    assert "| Field | Value |" in out
    assert "|---|---|" in out
    assert "| **Branch** | `main` |" in out
    assert "| **Worktree** | clean |" in out
    assert "| **Drift signals** | none |" in out
    # Old box-drawing format must not appear.
    assert "▌" not in out


def test_status_snapshot_flags_dirty_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    payload = module._status_snapshot_payload()

    assert payload["worktree"] == "dirty"
    assert any("dirty on main" in signal for signal in payload["drift_signals"])


def test_reflection_check_returns_pass_on_clean_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    # Create stub generate scripts so reflection-check's --check guards pass.
    _seed_generate_scripts(repo)

    payload = module._reflection_check_payload()

    assert payload["verdict"] == "PASS", payload
    assert payload["failures"] == []


def _seed_generate_scripts(repo: Path) -> None:
    """Write and commit no-op generate_*.py --check stubs for reflection-check."""
    truth_dir = repo / "internal" / "truth"
    archive_dir = repo / "internal" / "archive"
    truth_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    stub = "import sys\nsys.exit(0)\n"
    (truth_dir / "generate_status.py").write_text(stub, encoding="utf-8")
    (truth_dir / "generate_cortex_doc.py").write_text(stub, encoding="utf-8")
    (archive_dir / "generate_archive_index.py").write_text(stub, encoding="utf-8")
    _git(
        repo,
        "add",
        "internal/truth/generate_status.py",
        "internal/truth/generate_cortex_doc.py",
        "internal/archive/generate_archive_index.py",
    )
    _git(repo, "commit", "-m", "tests: seed generate stubs")
    _git(repo, "push", "origin", "main")


def test_reflection_check_fails_on_stale_next_train(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    _seed_generate_scripts(repo)
    # Override last_reviewed_at to >60 days ago.
    registry_path = repo / "internal" / "truth" / "cortex_status.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    data["next_product_train"]["last_reviewed_at"] = "2025-01-01T00:00:00+00:00"
    registry_path.write_text(json.dumps(data), encoding="utf-8")

    payload = module._reflection_check_payload()

    assert payload["verdict"] == "FAIL"
    assert any(
        "next_product_train" in failure for failure in payload["failures"]
    )


def test_reflection_check_warns_on_warn_threshold_next_train(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    _seed_generate_scripts(repo)
    # Override last_reviewed_at to >30 days ago but <60 days.
    registry_path = repo / "internal" / "truth" / "cortex_status.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    import datetime as dt
    data["next_product_train"]["last_reviewed_at"] = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=45)
    ).isoformat()
    registry_path.write_text(json.dumps(data), encoding="utf-8")

    payload = module._reflection_check_payload()

    assert payload["verdict"] == "GAPS"
    assert any(
        "next_product_train" in gap for gap in payload["gaps"]
    )


def test_grid_emits_markdown_with_full_sections_when_work_performed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    _seed_generate_scripts(repo)
    # Switch to a session branch and create a change so the grid detects work.
    monkeypatch.setattr(module, "_session_timestamp", lambda: "20260429-100000")
    module.cmd_start_session("codex", "grid-work")
    (repo / "README.md").write_text("session change\n", encoding="utf-8")

    module.cmd_grid()
    out = capsys.readouterr().out

    # Canonical signature markers (also pinned by the Stop hook).
    assert module.GRID_HEADER_MARKER in out
    assert module.GRID_STATE_MARKER in out
    assert module.GRID_VERDICT_MARKER in out
    # Markdown styling: the state and progress are 2-column tables.
    assert "| Field | Value |" in out
    assert "|---|---|" in out
    assert "### Cortex Progress" in out
    # Goals Analysis fields expected (5 substantive prompts).
    for label, _ in module.GOALS_ANALYSIS_FIELDS:
        assert f"**{label}:**" in out
    # Work-performed-only sections should appear.
    assert "### Mechanical Checks" in out
    assert "### Work Reflection" in out
    # No box-drawing chars from the prior format.
    assert "═══" not in out
    assert "▌" not in out


def test_grid_emits_markdown_minimal_when_no_work_performed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _remote, module = _prepare_repo(tmp_path, monkeypatch)
    _seed_registry(repo)
    _seed_generate_scripts(repo)

    module.cmd_grid()
    out = capsys.readouterr().out

    # Always-on sections present.
    assert module.GRID_HEADER_MARKER in out
    assert module.GRID_STATE_MARKER in out
    assert "### Cortex Progress" in out
    assert "### Goals Analysis" in out
    assert module.GRID_VERDICT_MARKER in out
    # Work-only sections must NOT appear when no tracked-file changes exist.
    assert "### Mechanical Checks" not in out
    assert "### Work Reflection" not in out
    # The verdict is still emitted (PASS by default on clean main).
    assert "PASS" in out or "GAPS" in out or "FAIL" in out


def test_grid_signature_markers_are_distinct_constants() -> None:
    """The Stop hook regex relies on these exact strings; pin them."""
    module = _load_repo_workflow_module()
    assert module.GRID_HEADER_MARKER == "## Cortex Repo Hygiene Grid"
    assert module.GRID_STATE_MARKER == "### State"
    assert module.GRID_VERDICT_MARKER == "### Verdict"


def test_goals_analysis_fields_demand_substantive_prompts() -> None:
    """Goals Analysis must enumerate the five depth-prompt fields."""
    module = _load_repo_workflow_module()
    labels = [label for label, _ in module.GOALS_ANALYSIS_FIELDS]
    assert labels == [
        "Plan → implementation",
        "Quality assessment",
        "Iteration moments this session",
        "Forward-looking confidence",
        "Tied to Cortex goals",
    ]


def test_bundling_surfaces_flags_unrelated_top_level_groups() -> None:
    module = _load_repo_workflow_module()
    paths = [
        "cortex/sre/foo.py",
        "cortex/aux/bar.py",
        "tests/lab/baz.py",
        "lab/qux.py",
        "tests/product/test_x.py",
    ]
    surfaces = module._bundling_surfaces(paths)
    assert len(surfaces) >= 4


def test_bundling_surfaces_does_not_flag_one_concern() -> None:
    module = _load_repo_workflow_module()
    paths = [
        "cortex/sre/foo.py",
        "tests/product/test_x.py",
        "AGENTS.md",
    ]
    surfaces = module._bundling_surfaces(paths)
    # AGENTS.md / docs are intentionally excluded from the surface list,
    # so the result is at most 2 (cortex/sre + tests/product).
    assert len(surfaces) <= 2
