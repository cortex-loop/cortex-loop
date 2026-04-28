from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from internal.closeout import contract as closeout_contract


def _filled_payload(branch: str, mode: str, reviewed_paths: list[str]) -> dict[str, object]:
    payload = closeout_contract.scaffold_payload(branch=branch, mode=mode, reviewed_paths=reviewed_paths)
    payload["seam"] = {
        "slug": "closeout-rigor",
        "surface": "product" if payload["profile"] == "load_bearing" else "internal",
        "executive_benefit": "Prevent overclaiming at closure.",
        "why_now": "The workflow now hard-gates residual rigor.",
    }
    payload["residuals"] = {
        "fixed_now": ["The scoped seam is complete and reviewable."],
        "intentionally_deferred": ["No broader architecture change in this helper."],
        "still_underfit": ["No residual issue remains in this test payload."],
        "zeroed_or_stubbed_terms": [],
    }
    payload["hostile_review"] = {
        "engineer": "No material critique remains.",
        "mathematician": "The active fields are explicit and typed.",
        "neuroscientist": "No false cognitive claim is introduced.",
    }
    payload["claims"] = {
        "earned_now": ["Closeout rigor is enforced for this seam."],
        "forbidden_still": ["No claim of broader product lift from this helper alone."],
    }
    payload["north_light_audit"] = {
        "microkernel_boundary": {"status": "pass", "note": "No core policy moved."},
        "repo_governance_leakage": {"status": "pass", "note": "This is internal workflow only."},
        "host_specific_policy_fork": {"status": "pass", "note": "No host runtime changed."},
        "generic_bloat": {"status": "pass", "note": "The contract is tied to workflow closeout only."},
    }
    if payload["profile"] == "load_bearing":
        payload["governing_locks"] = {
            "governing_principle": "Truthful closure outranks local green tests.",
            "executive_skill": "Residual rigor at handoff.",
            "product_metric": "No S-tier claim survives without explicit residual accounting.",
            "guardrail": "No second truth surface.",
            "kill_rule": "Cut any variant that allows silent overclaiming.",
        }
        payload["law_to_code_completeness"] = [
            {
                "term": "closeout rigor",
                "state": "implemented",
                "code_refs": [reviewed_paths[0]],
                "proof_refs": ["tests/internal/test_closeout_contract.py"],
                "note": "Representative load-bearing row for the touched path.",
            }
        ]
    return payload


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Cortex Test")
    _git(repo, "config", "user.email", "cortex@example.com")
    (repo / ".gitignore").write_text(".cortex/closeout_contract/\n", encoding="utf-8")
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", "README.md")
    _git(repo, "commit", "-m", "repo: initialize temp repo")
    return repo


def test_validate_payload_accepts_valid_standard_contract() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="finalize",
        expected_branch="maint/manual-work",
        expected_reviewed_paths=["README.md"],
    )

    assert validated["profile"] == "standard"


def test_validate_payload_accepts_valid_load_bearing_contract() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="close-session",
        expected_branch="codex/20260413-000000-load-bearing",
        expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
    )

    assert validated["profile"] == "load_bearing"


def test_validate_payload_rejects_missing_forbidden_claims() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    payload["claims"]["forbidden_still"] = []

    with pytest.raises(SystemExit, match="claims.forbidden_still"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_missing_zeroed_or_stubbed_terms() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    del payload["residuals"]["zeroed_or_stubbed_terms"]

    with pytest.raises(SystemExit, match="residuals.zeroed_or_stubbed_terms"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_missing_hostile_review_lens() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    payload["hostile_review"]["mathematician"] = ""

    with pytest.raises(SystemExit, match="hostile_review.mathematician"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_stale_reviewed_paths() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])

    with pytest.raises(SystemExit, match="reviewed_paths are stale or incomplete"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md", "notes.txt"],
        )


def test_workflow_law_paths_infer_load_bearing() -> None:
    assert closeout_contract.infer_profile(["AGENTS.md"]) == "load_bearing"
    assert closeout_contract.infer_profile(["docs/internal/REPO_WORKFLOW.md"]) == "load_bearing"
    assert closeout_contract.infer_profile(["internal/workflow/repo_workflow.py"]) == "load_bearing"
    assert closeout_contract.infer_profile(["internal/closeout/contract.py"]) == "load_bearing"
    assert closeout_contract.infer_profile(["internal/Makefile"]) == "load_bearing"
    assert closeout_contract.infer_profile(["tests/internal/test_repo_workflow.py"]) == "standard"


def test_validate_payload_rejects_invalid_law_to_code_state() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["law_to_code_completeness"][0]["state"] = "half_done"

    with pytest.raises(SystemExit, match="law_to_code_completeness entries must use state"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_missing_governing_locks() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["internal/workflow/repo_workflow.py"],
    )
    del payload["governing_locks"]

    with pytest.raises(SystemExit, match="must include governing_locks"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["internal/workflow/repo_workflow.py"],
        )


def test_validate_payload_rejects_empty_law_to_code_completeness() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["internal/workflow/repo_workflow.py"],
    )
    payload["law_to_code_completeness"] = []

    with pytest.raises(SystemExit, match="at least one law_to_code_completeness row"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["internal/workflow/repo_workflow.py"],
        )


def test_validate_payload_rejects_missing_completeness_refs_or_note() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["internal/workflow/repo_workflow.py"],
    )
    payload["law_to_code_completeness"][0]["proof_refs"] = []

    with pytest.raises(SystemExit, match="law_to_code_completeness\\[0\\]\\.proof_refs"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["internal/workflow/repo_workflow.py"],
        )


def test_render_markdown_includes_final_handoff_mirror() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])

    rendered = closeout_contract.render_markdown(payload)

    assert "## Final Handoff Mirror" in rendered
    assert "### Fixed now" in rendered
    assert "### Intentionally deferred" in rendered
    assert "### Still underfit" in rendered
    assert "### Zeroed or stubbed terms" in rendered
    assert "### Hostile reviewer critiques" in rendered
    assert "### Claim earned now" in rendered
    assert "### Claim still forbidden" in rendered


def test_init_contract_writes_branch_and_latest_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "switch", "-c", "maint/manual-work")
    (repo / "notes.txt").write_text("notes\n", encoding="utf-8")
    _git(repo, "add", "notes.txt")
    monkeypatch.setenv(closeout_contract.ROOT_ENV_VAR, str(repo))

    result = closeout_contract.init_contract(root=repo, mode="finalize", branch="maint/manual-work")

    assert result["reviewed_paths"] == ["notes.txt"]
    paths = closeout_contract.resolve_artifact_paths(repo, "maint/manual-work")
    assert paths["json_path"].exists()
    assert paths["markdown_path"].exists()
    assert paths["latest_json_path"].exists()
    assert paths["latest_markdown_path"].exists()


def test_init_contract_uses_dirty_worktree_paths_when_nothing_is_staged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_repo(tmp_path)
    _git(repo, "switch", "-c", "maint/manual-work")
    (repo / "notes.txt").write_text("notes\n", encoding="utf-8")
    monkeypatch.setenv(closeout_contract.ROOT_ENV_VAR, str(repo))

    result = closeout_contract.init_contract(root=repo, mode="finalize", branch="maint/manual-work")

    assert result["reviewed_paths"] == ["notes.txt"]



def test_validate_payload_rejects_agent_loop_guard_with_allow_blocked() -> None:
    """Bridge-postmortem guard: agent_loop_guard.allow_blocked = true is forbidden.

    The postmortem identified --allow-blocked as the procedural escape hatch
    that let the V2 communication bridge work be checkpointed before live
    Claude/Codex proof was completed.
    """
    payload = _filled_payload("claude/20260101-000000-test-allow-blocked", "close-session", ["README.md"])
    payload["agent_loop_guard"] = {
        "report_path": ".cortex/live_validation/agent_loop_guard/gates.latest.json",
        "require_full_communication_closure": True,
        "allow_blocked": True,
    }

    with pytest.raises(SystemExit, match="allow_blocked"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="claude/20260101-000000-test-allow-blocked",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_agent_loop_guard_opt_out_of_full_communication_closure() -> None:
    """Bridge-postmortem guard: require_full_communication_closure = false is forbidden.

    The postmortem identified this opt-out as the second procedural escape
    hatch that allowed the V2 bridge work to checkpoint without proof.
    """
    payload = _filled_payload("claude/20260101-000000-test-opt-out", "close-session", ["README.md"])
    payload["agent_loop_guard"] = {
        "report_path": ".cortex/live_validation/agent_loop_guard/gates.latest.json",
        "require_full_communication_closure": False,
        "allow_blocked": False,
    }

    with pytest.raises(SystemExit, match="require_full_communication_closure"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="claude/20260101-000000-test-opt-out",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_full_communication_claim_without_agent_loop_guard() -> None:
    """Naked claims of full V2 communication closure require an agent_loop_guard payload."""
    payload = _filled_payload("claude/20260101-000000-test-naked-claim", "close-session", ["README.md"])
    payload["claims"]["earned_now"] = [
        "Cortex fully communicates V2 doctrine to the model on every turn.",
    ]

    with pytest.raises(SystemExit, match="agent_loop_guard"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="claude/20260101-000000-test-naked-claim",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_accepts_agent_loop_guard_with_safe_defaults() -> None:
    """A closeout that includes an agent_loop_guard with the postmortem-safe
    defaults (require_full_communication_closure=True, allow_blocked=False)
    must still validate; the guard is forward-armed, not punitive."""
    payload = _filled_payload("claude/20260101-000000-test-safe-guard", "close-session", ["README.md"])
    payload["agent_loop_guard"] = {
        "report_path": ".cortex/live_validation/agent_loop_guard/gates.latest.json",
        "require_full_communication_closure": True,
        "allow_blocked": False,
    }

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="close-session",
        expected_branch="claude/20260101-000000-test-safe-guard",
        expected_reviewed_paths=["README.md"],
    )
    assert validated["agent_loop_guard"]["allow_blocked"] is False


def test_validate_payload_accepts_optional_stacked_session_reason() -> None:
    """The stacked_session_reason field is recorded on closeouts whose
    session was started with start-session --allow-stacked. It is optional
    (most sessions don't use the override); when present it must be a
    non-empty string."""
    payload = _filled_payload(
        "claude/20260601-010205-stacked-test",
        "close-session",
        ["README.md"],
    )
    payload["stacked_session_reason"] = "emergency hotfix while investigation in flight"

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="close-session",
        expected_branch="claude/20260601-010205-stacked-test",
        expected_reviewed_paths=["README.md"],
    )
    assert (
        validated["stacked_session_reason"]
        == "emergency hotfix while investigation in flight"
    )


def test_validate_payload_rejects_empty_stacked_session_reason() -> None:
    """If stacked_session_reason is present, it must be non-empty.
    A blank string is meaningless as an audit trail."""
    payload = _filled_payload(
        "claude/20260601-010206-stacked-empty",
        "close-session",
        ["README.md"],
    )
    payload["stacked_session_reason"] = ""

    with pytest.raises(SystemExit, match="stacked_session_reason"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="claude/20260601-010206-stacked-empty",
            expected_reviewed_paths=["README.md"],
        )


def test_scaffold_payload_seeds_stacked_session_reason_from_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When start-session --allow-stacked writes the marker file, the
    closeout scaffold reads it back and seeds stacked_session_reason
    automatically. The agent should never need to copy the reason
    manually into the closeout JSON."""
    repo = _init_repo(tmp_path)
    monkeypatch.setenv(closeout_contract.ROOT_ENV_VAR, str(repo))
    branch = "claude/20260601-010207-stacked-marker"
    marker_dir = repo / ".cortex" / "closeout_contract" / Path(*branch.split("/"))
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker = marker_dir / "stacked_session_reason.txt"
    marker.write_text(
        "investigation in flight; need parallel hotfix branch", encoding="utf-8"
    )

    payload = closeout_contract.scaffold_payload(
        branch=branch, mode="close-session", reviewed_paths=["README.md"]
    )

    assert (
        payload["stacked_session_reason"]
        == "investigation in flight; need parallel hotfix branch"
    )
