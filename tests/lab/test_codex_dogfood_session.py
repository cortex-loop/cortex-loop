"""Focused tests for repo-wide Codex App dogfood mode."""

from __future__ import annotations

from pathlib import Path

from lab import codex_dogfood_session


def test_activate_session_succeeds_on_managed_branch(tmp_path, monkeypatch) -> None:
    fixture = _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=False,
        ),
    )

    result = codex_dogfood_session.activate_session()

    assert result["ok"] is True
    artifact = result["artifact"]
    assert artifact["mode_status"] == "active"
    assert artifact["surface"] == "codex_dogfood_session"
    assert artifact["scope"] == "lab"
    assert artifact["evidence_role"] == "watchlist"
    assert artifact["managed_session_branch"] is True
    assert artifact["contract_source"] == "current_worktree"
    assert artifact["thread_id"] is None
    assert artifact["artifact_path"] == ".cortex/live_validation/dogfood/sessions/dogfood-test.json"
    assert artifact["activation_baseline"] == {
        "branch": "codex/20260411-000000-any-task",
        "head_commit": "abc123",
        "worktree_dirty": False,
        "status_lines": [],
        "dirty_files": [],
    }
    assert fixture["latest_path"].exists()
    assert "repo_codex_app_dogfood_session_start.md" in result["message"]
    assert "lab/watchlist only; not product truth" in result["message"]
    assert "activation baseline: `dirty=False`; initial dirty files: `none`" in result["message"]


def test_activate_on_clean_main_refuses_with_workflow_guidance(tmp_path, monkeypatch) -> None:
    fixture = _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(branch="main", head_commit="abc123", worktree_dirty=False),
    )

    result = codex_dogfood_session.activate_session()

    assert result["ok"] is False
    assert "sync-main" in result["message"]
    assert "start-session --agent codex --slug task-name" in result["message"]
    assert not fixture["latest_path"].exists()


def test_activate_on_non_session_branch_refuses(tmp_path, monkeypatch) -> None:
    _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(branch="feature/dogfood", head_commit="abc123", worktree_dirty=False),
    )

    result = codex_dogfood_session.activate_session()

    assert result["ok"] is False
    assert "Reconcile the worktree" in result["message"]


def test_activate_on_dirty_managed_branch_preserves_activation_baseline(tmp_path, monkeypatch) -> None:
    _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=True,
            status_lines=[" M AGENTS.md", "?? carry.txt"],
        ),
    )

    result = codex_dogfood_session.activate_session()

    assert result["ok"] is True
    assert result["artifact"]["activation_baseline"] == {
        "branch": "codex/20260411-000000-any-task",
        "head_commit": "abc123",
        "worktree_dirty": True,
        "status_lines": [" M AGENTS.md", "?? carry.txt"],
        "dirty_files": ["AGENTS.md", "carry.txt"],
    }
    assert "activation baseline: `dirty=True`; initial dirty files: `AGENTS.md, carry.txt`" in result["message"]


def test_refresh_updates_contract_revision_hash_from_current_worktree(tmp_path, monkeypatch) -> None:
    fixture = _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=False,
        ),
    )
    activated = codex_dogfood_session.activate_session()
    previous_hash = activated["artifact"]["contract_revision_hash"]

    fixture["session_start_prompt"].write_text(
        fixture["session_start_prompt"].read_text(encoding="utf-8") + "\nCurrent worktree delta.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="def456",
            worktree_dirty=True,
            status_lines=[" M repo.md"],
        ),
    )

    refreshed = codex_dogfood_session.refresh_session()

    assert refreshed["ok"] is True
    artifact = refreshed["artifact"]
    assert artifact["mode_status"] == "refreshed"
    assert artifact["contract_revision_hash"] != previous_hash
    assert len(artifact["contract_revision_history"]) == 2


def test_status_reads_current_worktree_hash_without_mutating(tmp_path, monkeypatch) -> None:
    _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=False,
        ),
    )
    activated = codex_dogfood_session.activate_session()

    status_one = codex_dogfood_session.status_session()
    status_two = codex_dogfood_session.status_session()

    assert status_one["ok"] is True
    assert status_one["current_worktree_contract_revision_hash"] == activated["artifact"]["contract_revision_hash"]
    assert status_two["current_worktree_contract_revision_hash"] == status_one["current_worktree_contract_revision_hash"]
    assert status_one["refresh_required"] is False
    assert "lab/watchlist only; not product truth" in status_one["message"]


def test_close_finalizes_artifact_and_renders_exact_signal_block(tmp_path, monkeypatch) -> None:
    fixture = _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=False,
        ),
    )
    codex_dogfood_session.activate_session()
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="def456",
            worktree_dirty=False,
        ),
    )
    monkeypatch.setattr(
        codex_dogfood_session,
        "_collect_current_changed_paths",
        lambda start_head_commit: {"lab/codex_dogfood_session.py", "AGENTS.md"},
    )

    result = codex_dogfood_session.close_session(
        handoff_summary="ending branch: codex/20260411-000000-any-task",
        verification_summary="pytest targeted suite passed",
        dogfood_signal={
            "continuity_helped": "yes",
            "blocker_surfaced": "no",
            "uncertainty_or_brake_used": "yes",
            "truthful_closure": "yes",
            "cortex_changed_next_action": "yes",
        },
        note="The contract changed the closeout call.",
    )

    assert result["ok"] is True
    artifact = result["artifact"]
    assert artifact["mode_status"] == "closed"
    assert artifact["handoff_summary"] == "ending branch: codex/20260411-000000-any-task"
    assert artifact["verification_summary"] == "pytest targeted suite passed"
    assert artifact["dogfood_signal"]["continuity_helped"] == "yes"
    assert artifact["dogfood_signal"]["note"] == "The contract changed the closeout call."
    assert artifact["changed_files"] == ["AGENTS.md", "lab/codex_dogfood_session.py"]
    assert artifact["end_commit"] == "def456"
    assert artifact["returned_to_main"] is False
    assert "lab/watchlist only; not product truth" in result["message"]
    assert "changed files beyond activation baseline: `AGENTS.md, lab/codex_dogfood_session.py`" in result["message"]
    assert result["message"].endswith(
        "\n\nDOGFOOD_SIGNAL\n"
        "continuity_helped: yes\n"
        "blocker_surfaced: no\n"
        "uncertainty_or_brake_used: yes\n"
        "truthful_closure: yes\n"
        "cortex_changed_next_action: yes\n"
        "note: The contract changed the closeout call."
    )
    latest = codex_dogfood_session.read_json_file(fixture["latest_path"])
    assert latest["mode_status"] == "closed"
    assert latest["dogfood_id"] == artifact["dogfood_id"]


def test_close_excludes_activation_baseline_paths_from_changed_files(tmp_path, monkeypatch) -> None:
    _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=True,
            status_lines=[" M AGENTS.md", "?? carry.txt"],
        ),
    )
    codex_dogfood_session.activate_session()
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="def456",
            worktree_dirty=True,
            status_lines=[" M AGENTS.md", "?? carry.txt", " M lab/codex_dogfood_session.py"],
        ),
    )
    monkeypatch.setattr(
        codex_dogfood_session,
        "_collect_current_changed_paths",
        lambda start_head_commit: {"AGENTS.md", "carry.txt", "lab/codex_dogfood_session.py"},
    )

    result = codex_dogfood_session.close_session(
        dogfood_signal={
            "continuity_helped": "yes",
            "blocker_surfaced": "yes",
            "uncertainty_or_brake_used": "no",
            "truthful_closure": "yes",
            "cortex_changed_next_action": "no",
        },
        note="Only net-new paths are attributed.",
    )

    assert result["artifact"]["changed_files"] == ["lab/codex_dogfood_session.py"]


def test_stop_marks_session_artifact_aborted_without_signal_block(tmp_path, monkeypatch) -> None:
    _configure_dogfood_contract(tmp_path, monkeypatch)
    monkeypatch.setattr(
        codex_dogfood_session,
        "_repo_state",
        lambda: _repo_state(
            branch="codex/20260411-000000-any-task",
            head_commit="abc123",
            worktree_dirty=False,
        ),
    )
    codex_dogfood_session.activate_session()
    monkeypatch.setattr(
        codex_dogfood_session,
        "_collect_current_changed_paths",
        lambda start_head_commit: set(),
    )

    result = codex_dogfood_session.close_session(
        trigger_phrase=codex_dogfood_session.DOGFOOD_STOP_TRIGGER,
        abort=True,
    )

    assert result["ok"] is True
    assert result["artifact"]["mode_status"] == "aborted"
    assert "DOGFOOD_SIGNAL" not in result["message"]
    assert "lab/watchlist only; not product truth" in result["message"]


def test_prompt_contract_requires_fixed_signal_and_preserves_normal_handoff() -> None:
    session_start = (
        codex_dogfood_session.PROMPTS_ROOT / "repo_codex_app_dogfood_session_start.md"
    ).read_text(encoding="utf-8")
    closeout = (
        codex_dogfood_session.PROMPTS_ROOT / "repo_codex_app_dogfood_closeout.md"
    ).read_text(encoding="utf-8")

    for key in (
        "DOGFOOD_SIGNAL",
        "continuity_helped: yes|no",
        "blocker_surfaced: yes|no",
        "uncertainty_or_brake_used: yes|no",
        "truthful_closure: yes|no",
        "cortex_changed_next_action: yes|no",
        "note: <one sentence>",
    ):
        assert key in session_start
        assert key in closeout

    assert "Dogfood mode is active only for this current Codex App chat/session." in session_start
    assert "Preserve the repo's normal final handoff contract." in session_start
    assert "Do not replace the normal handoff with lab text." in closeout


def test_dogfood_workflow_contract_stays_in_sync_with_helper_contract() -> None:
    dogfood_section = codex_dogfood_session._read_dogfood_workflow_contract()
    profile = codex_dogfood_session._load_profile(codex_dogfood_session.DOGFOOD_PROFILE_NAME)

    for trigger in (
        codex_dogfood_session.DOGFOOD_START_TRIGGER,
        codex_dogfood_session.DOGFOOD_REFRESH_TRIGGER,
        codex_dogfood_session.DOGFOOD_STOP_TRIGGER,
        codex_dogfood_session.DOGFOOD_STATUS_TRIGGER,
    ):
        assert f"`{trigger}`" in dogfood_section

    for command in (
        "python3 -m lab.codex_dogfood_session activate",
        "python3 -m lab.codex_dogfood_session refresh",
        "python3 -m lab.codex_dogfood_session close --abort",
        "python3 -m lab.codex_dogfood_session status",
        profile["sync_main_command"],
        profile["start_session_command"],
        profile["close_session_command"],
    ):
        assert command in dogfood_section


def _configure_dogfood_contract(tmp_path: Path, monkeypatch) -> dict[str, Path]:
    prompts_root = tmp_path / "tests" / "lab" / "fixtures" / "live_validation" / "prompts"
    prompts_root.mkdir(parents=True, exist_ok=True)
    session_start_prompt = prompts_root / "repo_codex_app_dogfood_session_start.md"
    closeout_prompt = prompts_root / "repo_codex_app_dogfood_closeout.md"
    session_start_prompt.write_text(
        "\n".join(
            [
                "Preserve the repo's normal final handoff contract.",
                "DOGFOOD_SIGNAL",
                "continuity_helped: yes|no",
                "blocker_surfaced: yes|no",
                "uncertainty_or_brake_used: yes|no",
                "truthful_closure: yes|no",
                "cortex_changed_next_action: yes|no",
                "note: <one sentence>",
                "",
            ]
        ),
        encoding="utf-8",
    )
    closeout_prompt.write_text(
        "\n".join(
            [
                "Do not replace the normal handoff with lab text.",
                "DOGFOOD_SIGNAL",
                "continuity_helped: yes|no",
                "blocker_surfaced: yes|no",
                "uncertainty_or_brake_used: yes|no",
                "truthful_closure: yes|no",
                "cortex_changed_next_action: yes|no",
                "note: <one sentence>",
                "",
            ]
        ),
        encoding="utf-8",
    )
    workflow_path = tmp_path / "docs" / "internal" / "REPO_WORKFLOW.md"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "# Test Workflow",
                "",
                "## Workflow",
                "workflow body",
                "",
                "## Codex App Dogfood Mode",
                "Dogfood contract body.",
                "",
                "## Handoff",
                "handoff body",
                "",
            ]
        ),
        encoding="utf-8",
    )
    sessions_root = tmp_path / ".cortex" / "live_validation" / "dogfood" / "sessions"
    latest_path = tmp_path / ".cortex" / "live_validation" / "dogfood" / "latest.json"
    profile = {
        "task_scope": "any_repo_work",
        "branch_format": "codex/<YYYYMMDD-HHMMSS>-<slug>",
        "workflow_mode": "managed_session",
        "session_start_prompt": session_start_prompt.name,
        "closeout_prompt": closeout_prompt.name,
        "sync_main_command": "python3 internal/workflow/repo_workflow.py sync-main",
        "start_session_command": (
            "python3 internal/workflow/repo_workflow.py start-session --agent codex --slug task-name"
        ),
        "close_session_command": (
            'python3 internal/workflow/repo_workflow.py close-session --message "scope: end-state summary"'
        ),
    }
    monkeypatch.setattr(codex_dogfood_session, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(codex_dogfood_session, "WORKFLOW_CONTRACT_PATH", workflow_path)
    monkeypatch.setattr(codex_dogfood_session, "PROMPTS_ROOT", prompts_root)
    monkeypatch.setattr(codex_dogfood_session, "DOGFOOD_SESSIONS_ROOT", sessions_root)
    monkeypatch.setattr(codex_dogfood_session, "DOGFOOD_LATEST_PATH", latest_path)
    monkeypatch.setattr(
        codex_dogfood_session,
        "ensure_live_validation_dirs",
        lambda: sessions_root.mkdir(parents=True, exist_ok=True),
    )
    monkeypatch.setattr(
        codex_dogfood_session,
        "relative_repo_path",
        lambda path: str(path.relative_to(tmp_path)),
    )
    monkeypatch.setattr(
        codex_dogfood_session,
        "build_scenario_catalog",
        lambda: {"codex_dogfood_profiles": {"repo_any_task": profile}},
    )
    monkeypatch.setattr(codex_dogfood_session, "_new_dogfood_id", lambda: "dogfood-test")
    return {
        "workflow_path": workflow_path,
        "session_start_prompt": session_start_prompt,
        "closeout_prompt": closeout_prompt,
        "sessions_root": sessions_root,
        "latest_path": latest_path,
    }


def _repo_state(
    *,
    branch: str,
    head_commit: str,
    worktree_dirty: bool,
    status_lines: list[str] | None = None,
) -> dict[str, object]:
    resolved_status_lines = list(status_lines or [])
    return {
        "branch": branch,
        "head_commit": head_commit,
        "worktree_dirty": worktree_dirty,
        "status_lines": resolved_status_lines,
        "dirty_files": codex_dogfood_session._dirty_files_from_status_lines(resolved_status_lines),
    }
