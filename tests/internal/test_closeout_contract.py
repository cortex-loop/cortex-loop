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
    if branch.startswith("codex/"):
        payload["mission_reflection_graph"] = {
            "validator": closeout_contract.CODEX_MISSION_GRAPH_VALIDATOR_COMMAND,
            "validated": True,
            "note": "Codex final graph validator was run on the closure draft.",
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
        # When the load-bearing seam touches cortex/**, the connectivity-
        # trace contract requires articulation of the path from the change
        # to the model's input or output. Default the fixture to a
        # populated path so legacy tests continue to pass; tests that
        # exercise the closed-loop drift gate override this explicitly.
        if any(closeout_contract.is_cortex_path(path) for path in reviewed_paths):
            payload["connectivity_trace"] = {
                "claim": "Reference scoring updates flow into operator route decisions.",
                "path": [
                    "cortex/sre/reference_scoring.py::compute",
                    "cortex/sre/operator_routing.py::OperatorRouteDecision",
                    "cortex/hosts/openai/cli.py",
                    "openai chat completion request",
                ],
                "if_empty_why": None,
            }
            payload["product_spine"] = {
                "executive_capability": "Truthful route selection from scored runtime evidence.",
                "executive_shape": "unsupported forward motion after unresolved verification pressure",
                "state_law_path": [
                    "reference score state",
                    "operator route decision",
                    "host request shape",
                ],
                "enforcement_decision": "Route selection changes before model invocation.",
                "host_action": "The OpenAI host adapter receives a different request shape.",
                "model_io_effect": "The model receives host-control input selected by shared Cortex law.",
                "fixture_boundary": "No motivating fixture identity is encoded in product code.",
                "fixture_witnesses": ["generic route-selection fixture"],
                "non_fixture_controls": [
                    "clean reference-scoring control",
                    "non-fixture route-selection control",
                ],
                "perception_source": "product_runtime",
                "decision_source": "product",
                "action_source": "product",
                "rendering_source": "product_renderer",
                "claim_scope": "full_product_loop",
                "task_identity_examples_checked": True,
            }
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


def test_validate_payload_rejects_missing_product_spine_for_product_cortex_change() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    del payload["product_spine"]

    with pytest.raises(SystemExit, match="Product closeouts touching cortex"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_requires_non_fixture_controls_in_product_spine() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["product_spine"]["non_fixture_controls"] = []

    with pytest.raises(SystemExit, match="product_spine.non_fixture_controls"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_missing_executive_shape_in_product_spine() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["product_spine"]["executive_shape"] = ""

    with pytest.raises(SystemExit, match="product_spine.executive_shape"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_lab_oracle_full_product_loop_claim() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["product_spine"]["perception_source"] = "lab_oracle"
    payload["product_spine"]["claim_scope"] = "full_product_loop"

    with pytest.raises(SystemExit, match="cannot claim full_product_loop"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_lab_prompt_as_product_renderer_claim() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["product_spine"]["rendering_source"] = "lab_prompt_scaffold"
    payload["product_spine"]["claim_scope"] = "product_renderer_evidence"

    with pytest.raises(SystemExit, match="lab_prompt_scaffold"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_requires_task_identity_example_scan_acknowledgement() -> None:
    payload = _filled_payload(
        "codex/20260413-000000-load-bearing",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["product_spine"]["task_identity_examples_checked"] = False

    with pytest.raises(SystemExit, match="task_identity_examples_checked"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260413-000000-load-bearing",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


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


def test_validate_payload_requires_codex_mission_graph_validation() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-grid-validation",
        "close-session",
        ["README.md"],
    )
    del payload["mission_reflection_graph"]

    with pytest.raises(SystemExit, match="mission_reflection_graph"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-grid-validation",
            expected_reviewed_paths=["README.md"],
        )


def test_closeout_contract_does_not_claim_codex_has_no_stop_hook() -> None:
    source = Path(closeout_contract.__file__).read_text(encoding="utf-8")

    assert "Codex has no Stop hook" not in source
    assert "Codex App has a repo-local Stop hook" in source
    assert "trusted `.codex/`" in source


def test_validate_payload_rejects_unvalidated_codex_mission_graph() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-grid-unvalidated",
        "close-session",
        ["README.md"],
    )
    payload["mission_reflection_graph"]["validated"] = False

    with pytest.raises(SystemExit, match="validated must be true"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-grid-unvalidated",
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


# ---------------------------------------------------------------------------
# Substantive-content rule: handwave detection + minimum length on the
# load-bearing reflection fields. Replaces the v1 PHILOSOPHY_AUDIT
# rubber-stamp that tolerated single-word answers.
# ---------------------------------------------------------------------------


def test_is_handwave_phrase_detects_known_patterns() -> None:
    for phrase in (
        "yes",
        "no",
        "n/a",
        "N/A",
        "none",
        "fine",
        "good",
        "looks good",
        "looks fine",
        "looks clean",
        "no issues",
        "no concerns",
        "nothing to add",
        "see above",
        "ditto",
    ):
        assert closeout_contract.is_handwave_phrase(phrase), phrase


def test_is_handwave_phrase_accepts_substantive_answers() -> None:
    for phrase in (
        "Reference scoring threads commit-time decisions through SRE.",
        "The connectivity path lands at the openai cli adapter.",
        "No material critique remains because the seam is bounded.",
    ):
        assert not closeout_contract.is_handwave_phrase(phrase), phrase


def test_validate_payload_rejects_handwave_in_hostile_review() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-handwave-engineer",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["hostile_review"]["engineer"] = "looks good"

    with pytest.raises(SystemExit, match="hostile_review.engineer.*handwave"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-handwave-engineer",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_short_north_light_note() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-short-note",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["north_light_audit"]["microkernel_boundary"] = {
        "status": "pass",
        "note": "fine",
    }

    with pytest.raises(SystemExit, match="microkernel_boundary.note.*too short"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-short-note",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_handwave_governing_lock() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-handwave-lock",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["governing_locks"]["kill_rule"] = "n/a"

    with pytest.raises(SystemExit, match="governing_locks.kill_rule.*handwave"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-handwave-lock",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_handwave_in_residuals_fixed_now() -> None:
    payload = _filled_payload(
        "maint/manual-handwave",
        "finalize",
        ["README.md"],
    )
    payload["residuals"]["fixed_now"] = ["yes"]

    with pytest.raises(SystemExit, match="residuals.fixed_now.*handwave"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="finalize",
            expected_branch="maint/manual-handwave",
            expected_reviewed_paths=["README.md"],
        )


# ---------------------------------------------------------------------------
# Connectivity-trace rule: load-bearing seams that touch cortex/** must
# articulate the path from the change to the model's input or output;
# empty path on `product` surface is the closed-loop drift error and is
# rejected. Empty path on `lab` or `experimental` is allowed but
# requires `if_empty_why` to explain why monitoring/instrumentation is
# the correct framing.
# ---------------------------------------------------------------------------


def test_scaffold_seeds_connectivity_trace_for_cortex_paths() -> None:
    payload = closeout_contract.scaffold_payload(
        branch="codex/20260429-000000-cortex-seam",
        mode="close-session",
        reviewed_paths=["cortex/sre/reference_scoring.py"],
    )
    assert "connectivity_trace" in payload
    assert payload["connectivity_trace"]["claim"] == ""
    assert payload["connectivity_trace"]["path"] == []
    assert payload["connectivity_trace"]["if_empty_why"] is None


def test_scaffold_omits_connectivity_trace_for_non_cortex_paths() -> None:
    payload = closeout_contract.scaffold_payload(
        branch="codex/20260429-000000-doc-seam",
        mode="close-session",
        reviewed_paths=["AGENTS.md", "internal/closeout/contract.py"],
    )
    assert "connectivity_trace" not in payload


def test_validate_payload_rejects_missing_connectivity_trace_on_cortex_seam() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-cortex-no-trace",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    del payload["connectivity_trace"]

    with pytest.raises(SystemExit, match="connectivity_trace"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-cortex-no-trace",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_rejects_empty_path_on_product_surface() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-empty-path-product",
        "close-session",
        ["cortex/sre/reference_scoring.py"],
    )
    payload["seam"]["surface"] = "product"
    payload["connectivity_trace"] = {
        "claim": "We monitor reference scoring outputs from a sidecar.",
        "path": [],
        "if_empty_why": "It is purely diagnostic.",
    }

    with pytest.raises(SystemExit, match="closed-loop drift"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-empty-path-product",
            expected_reviewed_paths=["cortex/sre/reference_scoring.py"],
        )


def test_validate_payload_accepts_empty_path_on_lab_surface_with_reason() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-empty-path-lab",
        "close-session",
        ["cortex/aux/evaluation.py"],
    )
    payload["seam"]["surface"] = "lab"
    payload["connectivity_trace"] = {
        "claim": "AUX evaluation collects offline lift metrics; it does not feed runtime.",
        "path": [],
        "if_empty_why": "Pure offline evaluation; no runtime reach is intended for this seam.",
    }

    validated = closeout_contract.validate_payload(
        payload,
        expected_mode="close-session",
        expected_branch="codex/20260429-000000-empty-path-lab",
        expected_reviewed_paths=["cortex/aux/evaluation.py"],
    )
    assert validated["connectivity_trace"]["path"] == []


def test_validate_payload_rejects_empty_path_on_lab_without_reason() -> None:
    payload = _filled_payload(
        "codex/20260429-000000-empty-path-no-reason",
        "close-session",
        ["cortex/aux/evaluation.py"],
    )
    payload["seam"]["surface"] = "lab"
    payload["connectivity_trace"] = {
        "claim": "AUX evaluation collects offline lift metrics; it does not feed runtime.",
        "path": [],
        "if_empty_why": None,
    }

    with pytest.raises(SystemExit, match="if_empty_why"):
        closeout_contract.validate_payload(
            payload,
            expected_mode="close-session",
            expected_branch="codex/20260429-000000-empty-path-no-reason",
            expected_reviewed_paths=["cortex/aux/evaluation.py"],
        )
