from __future__ import annotations

import json
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


def _write_loop_guard_report(
    repo: Path,
    *,
    relpath: str = ".cortex/live_validation/agent_loop_guard/gates.latest.json",
    status: str = "pass",
    include_evidence: bool = True,
) -> str:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = {
        "gate_id": "v2_packet_communication_inventory_complete",
        "status": status,
        "reason": f"gate is {status}",
        "next_action": "none",
    }
    if include_evidence:
        gate["evidence"] = "bounded transcript-backed evidence"
    path.write_text(
        json.dumps(
            {
                "required_gates": ["v2_packet_communication_inventory_complete"],
                "gates": [gate],
            }
        ),
        encoding="utf-8",
    )
    return relpath


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


def test_validate_payload_rejects_full_communication_claim_without_loop_guard() -> None:
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    payload["claims"]["earned_now"] = ["Full V2 communication closure is proven."]

    with pytest.raises(SystemExit, match="completion claims require agent_loop_guard"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md"],
        )


def test_validate_payload_rejects_full_communication_claim_with_pending_loop_gate(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    report_path = _write_loop_guard_report(repo, status="missing", include_evidence=False)
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    payload["claims"]["earned_now"] = ["Full V2 communication closure is proven."]
    payload["agent_loop_guard"] = {
        "report_path": report_path,
        "require_full_communication_closure": True,
    }

    with pytest.raises(SystemExit, match="not closed"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-work",
            expected_reviewed_paths=["README.md"],
            root=repo,
        )


def test_validate_payload_accepts_full_communication_claim_with_passing_loop_gate(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    report_path = _write_loop_guard_report(repo)
    payload = _filled_payload("maint/manual-work", "finalize", ["README.md"])
    payload["claims"]["earned_now"] = ["Full V2 communication closure is proven."]
    payload["agent_loop_guard"] = {
        "report_path": report_path,
        "require_full_communication_closure": True,
    }

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="finalize",
        expected_branch="maint/manual-work",
        expected_reviewed_paths=["README.md"],
        root=repo,
    )

    assert validated["agent_loop_guard"]["report_path"] == report_path


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
