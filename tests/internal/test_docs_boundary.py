"""Boundary and single-truth sync checks for the repo reset."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
CORTEX_DOC_PATH = REPO_ROOT / "docs" / "CORTEX.md"
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
RUNTIME_CONTEXT_RUBRIC_PATH = REPO_ROOT / "docs" / "runtime_context" / "EVAL_RUBRIC.md"
RUNTIME_CONTEXT_EXAMPLES_PATH = (
    REPO_ROOT / "docs" / "runtime_context" / "BASELINE_SHAPED_EXAMPLES.md"
)
RUNTIME_CONTEXT_CROSS_HOST_PATH = (
    REPO_ROOT / "docs" / "runtime_context" / "CROSS_HOST_SKETCH.md"
)
LIFECYCLE_SURFACE_RECON_PATH = (
    REPO_ROOT / "docs" / "recon" / "lifecycle_first_surface_matrix.md"
)
CODEX_APP_HOOK_PROBE_PATH = REPO_ROOT / "docs" / "recon" / "codex_app_hook_probe.md"
STATUS_REGISTRY_PATH = REPO_ROOT / "internal" / "truth" / "cortex_status.json"
STATUS_DOC_PATH = REPO_ROOT / "docs" / "CORTEX_STATUS.md"
WORKFLOW_DOC_PATH = REPO_ROOT / "docs" / "internal" / "REPO_WORKFLOW.md"
ARCHIVE_MANIFEST_PATH = REPO_ROOT / "internal" / "archive" / "manifest.json"
ARCHIVE_INDEX_PATH = REPO_ROOT / "docs" / "archive" / "README.md"
ARCHIVED_CHARTER_PATH = REPO_ROOT / "docs" / "archive" / "product" / "CORTEX_PRODUCT_CHARTER.md"
ARCHIVED_BOUNDARY_PATH = REPO_ROOT / "docs" / "archive" / "product" / "CORTEX_PRODUCT_BOUNDARY.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
ROOT_MAKEFILE_PATH = REPO_ROOT / "Makefile"
DOCS_ROOT = REPO_ROOT / "docs"
SKIP_WALK_DIRS = {".git", ".cortex", ".claude", "node_modules", "__pycache__"}

# The AGENTS.md and CLAUDE.md agent briefing block must be byte-equal so
# Claude Code and Codex see the same instructions; the briefing replaces
# the v1-era PHI-label decision loop and the PHILOSOPHY_AUDIT handoff
# block. Drift between the two would re-create the original asymmetry.
AGENT_BRIEFING_TEXT = """## Agent Briefing

Read this first, every session.

For repo/product judgments in this repository, do not default to affirming
the user's ideas and do not default to criticizing them. Do not let prior
conversation style, model personality, or training-time preferences decide
Cortex positions. Use only the repo's recorded goals and current proof.

Form positions from observable repo truth: `docs/CORTEX.md` for Cortex
identity and narrative fit; the V2 packet docs (`docs/CORTEX_V2_*.md`)
for packet law; `internal/truth/cortex_status.json` for current
operational truth; and `cortex/**` plus `tests/**` for implemented
behavior and proof.

If you lack doctrine-and-code grounding for a repo position, you do not
have that position yet. Read the specific missing surface, or say "I
don't know yet; I need to check X." Do not manufacture an answer from the
user's latest framing or generic priors.

Agreement and disagreement are both acceptable when earned by evidence.
Unearned agreement and ungrounded criticism are both failures."""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_status() -> dict[str, object]:
    return json.loads(_read(STATUS_REGISTRY_PATH))


def _find_repo_files(filename: str) -> list[str]:
    matches: list[str] = []
    for current_root, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in SKIP_WALK_DIRS]
        if filename not in filenames:
            continue
        path = Path(current_root) / filename
        matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(matches)


def test_agents_records_mission_lock_and_single_truth_bootstrap() -> None:
    text = _read(AGENTS_PATH)
    lines = text.splitlines()
    sections = [line for line in lines if line.startswith("## ")]
    all_agents = _find_repo_files("AGENTS.md")

    assert all_agents == ["AGENTS.md"]
    # AGENTS.md grew when the Agent Briefing block was added (2026-04)
    # to replace the v1-era PHI-label decision loop and the
    # PHILOSOPHY_AUDIT handoff ritual; further when the Stop hook
    # discipline and no-mimicry rule landed; further when the
    # single-grid-closure rule consolidated metadata + mirror inside the
    # grid, then Codex App hook parity landed. The cap stays bounded so
    # AGENTS.md does not sprawl into a wiki; the narrative lives in
    # docs/CORTEX.md.
    assert len(lines) <= 430
    assert sections == [
        "## Agent Briefing",
        "## Mission",
        "## Authority",
        "## Non-Negotiables",
        "## Working Mode",
        "## Workflow",
        "## Codex App Dogfood Mode",
        "## Handoff",
        "## Anti-Drift",
    ]
    # Briefing block must be present verbatim; CLAUDE.md's copy is
    # byte-equal so Claude Code and Codex see the same instructions.
    assert AGENT_BRIEFING_TEXT in text
    # Mission and identity anchors that downstream agents rely on.
    assert "rich multi-host executive layer" in text
    assert "installable executive layer" in text
    assert "human executive function" in text
    assert "live evidence" in text
    assert "lead with shipping truth, conformance truth, the current train, and the active quality/risk focus" in text
    assert "bio-to-code matrix" in text
    # Authority surfaces named including CORTEX.md as narrative authority.
    assert "docs/CORTEX.md" in text
    assert "internal/truth/cortex_status.json" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "AGENTS.md" in text
    # Bootstrap reads include CORTEX.md as the second read.
    assert "git branch --show-current" in text
    assert "git status --short --untracked-files=all" in text
    # Truth distinctions kept explicit.
    assert "shipping truth" in text
    assert "conformance truth" in text
    assert "This root `AGENTS.md` is the only agent contract in the repo." in text
    # Non-negotiables (live-spend lock and registry-truth-discipline).
    assert "Do not run paid service-lane commands unless the user explicitly approves spend in the current chat." in text
    assert "Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED`" in text
    assert ".cortex/closeout_contract/" in text
    assert "Workflow-law seams are load-bearing too" in text
    assert "revalidates reviewed-path exactness after verification" in text
    assert "at least one law-to-code completeness row" in text
    # Closure is now compact metadata inside Cortex Mission Reflection,
    # not a separate Final Handoff Mirror surface.
    assert "Cortex Mission Reflection" in text
    assert "Closure: Metadata" in text
    # PHI-label decision loop and PHILOSOPHY_AUDIT block must be retired.
    # Their content moved into docs/CORTEX.md §6 and the agent briefing.
    assert "PHI_MINIFY" not in text
    assert "PHI_MISSION" not in text
    assert "PHI_NICHE" not in text
    assert "PHILOSOPHY_AUDIT" not in text
    # Mission-reflection handoff anchors. Every chat ends with the grid; on
    # FAIL the agent continues working and does not close-session.
    assert "internal/workflow/repo_workflow.py grid" in text
    assert "Cortex Mission Reflection" in text
    assert "Grid auto-loop rule" in text
    assert "do not close-session" in text.lower() or "DO NOT close-session" in text
    assert "substantive" in text.lower()
    # No-mimicry rule and Stop hook discipline — Session 3 additions.
    assert "No-mimicry rule" in text
    assert ".claude/hooks/cortex_grid_stop_hook.py" in text
    assert ".claude/settings.json" in text
    assert "## Cortex Mission Reflection" in text
    assert "| Field | Value |" in text
    assert "Repo: State" in text
    assert "Mission: Cortex target" in text
    assert "Mission: Model I/O path" in text
    assert "Verdict" in text
    # Codex App now has its own hook path; fallback surfaces remain honest.
    assert "Codex" in text
    assert "Codex App chat-boundary enforcement" in text
    assert ".codex/hooks/cortex_mission_reflection_stop_hook.py" in text
    assert "codex-app-hook-health" in text
    assert "grid-validate --stdin" in text
    assert "mission_reflection_graph" in text
    assert "project layer is trusted" in text
    assert "last_assistant_message" in text
    assert "structural lifecycle evidence" in text
    # Single-table mission-reflection rule. Stale dashboard rows are
    # explicitly forbidden; mission rows must be cited and substantive.
    assert "Cortex Mission Reflection" in text
    assert "Do not emit fixed dashboard rows" in text
    assert "mission reflection —" in text
    assert "120" in text
    assert "no `###` subsection inside the grid" in text
    assert "fill brackets in place" in text or "edits the skeleton in place" in text
    # The hard-gate honesty: stop_hook_active no longer short-circuits.
    assert "stop_hook_active" in text
    # The old separate-block doctrine must NOT remain.
    assert "Every final summary must include the grid output plus the" not in text
    assert "Every substantive final summary must mirror the rendered" not in text
    assert "Goals Analysis" not in text
    assert "State: Branch" not in text
    assert "Std: Ending branch" not in text
    assert "Mirror: Fixed now" not in text
    # Old retired doctrine names must not creep back.
    assert "CORTEX_V2_ACTIVE_WORKSTREAM" not in text
    assert "CORTEX_V2_PHASE_GATES_2" not in text
    assert "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE" not in text
    assert "CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2" not in text
    assert "V1_CODE_PORT_DETERMINATION" not in text


def test_claude_md_carries_briefing_and_redirects_to_agents() -> None:
    text = _read(CLAUDE_PATH)
    lines = text.splitlines()
    # CLAUDE.md must stay short enough to be a redirect carrying only the
    # agent briefing and bootstrap reads. Drift back into duplication of
    # AGENTS.md content is the failure mode this cap exists to prevent.
    assert len(lines) <= 60
    # Briefing must be byte-equal to AGENTS.md briefing so Claude Code
    # and Codex see identical instructions.
    assert AGENT_BRIEFING_TEXT in text
    assert "AGENTS.md" in text
    assert "canonical agent contract" in text
    assert "docs/CORTEX.md" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "git branch --show-current" in text
    assert "git status --short --untracked-files=all" in text
    # No anti-drift duplication; CLAUDE.md does not own anti-drift rules.
    assert "## Anti-Drift" not in text
    assert "PHI_MINIFY" not in text


def test_cortex_doc_is_canonical_narrative_with_required_sections() -> None:
    text = _read(CORTEX_DOC_PATH)
    lines = text.splitlines()
    sections = [line for line in lines if line.startswith("## ")]
    # CORTEX.md is the canonical narrative authority. The cap prevents
    # the document from drifting into per-session noise; the narrative
    # is meant to evolve only when major learnings warrant.
    assert len(lines) <= 700
    assert sections == [
        "## 1. Identity",
        "## 2. Failure Modes Cortex Addresses",
        "## 3. V1 → V2 Evolution and Lessons",
        "## 4. Math → Code → Proof Map",
        "## 5. Current State and Strategy",
        "## 6. Implementation Discipline",
        "## 7. How to Use This Document",
    ]
    # Identity anchors: post-training boundary + four failure-mode anchors.
    assert "post-training" in text
    assert "no one is home" in text
    assert "Alzheimer's analog" in text
    assert "ADHD analog" in text
    assert "limited-empathy analog" in text
    # Connectivity discipline (closed-loop drift trap) is named.
    assert "closed-loop drift" in text
    assert "trace a path from the change" in text
    # Per-turn enforcement (Session 3): Stop hook + markdown grid + no-mimicry rule.
    assert "Stop hook" in text
    assert "No-mimicry rule" in text
    assert "Chat-boundary enforcement" in text
    # V1 → V2 lessons are carried.
    assert "lifecycle-first" in text.lower()
    assert "microkernel boundary" in text.lower() or "microkernel" in text.lower()
    assert "claim-conservative" in text.lower()
    assert "postmortem" in text.lower()
    # Generated fences must be present so generate_cortex_doc.py can splice.
    assert "<!-- BEGIN GENERATED: failure-modes-coverage -->" in text
    assert "<!-- END GENERATED: failure-modes-coverage -->" in text
    assert "<!-- BEGIN GENERATED: math-to-code-map -->" in text
    assert "<!-- END GENERATED: math-to-code-map -->" in text
    assert "<!-- BEGIN GENERATED: current-state-and-strategy -->" in text
    assert "<!-- END GENERATED: current-state-and-strategy -->" in text
    assert "<!-- BEGIN GENERATED: v2-model-io-analysis -->" in text
    assert "<!-- END GENERATED: v2-model-io-analysis -->" in text
    assert "### Side A — Internal Executive Logic" in text
    assert "### Side B — Model-Visible Translation" in text
    assert "### Synthesis — Gap / Boundary Decision" in text
    assert text.index("### Side A — Internal Executive Logic") < text.index(
        "### Side B — Model-Visible Translation"
    )
    assert text.index("### Side B — Model-Visible Translation") < text.index(
        "### Synthesis — Gap / Boundary Decision"
    )
    assert "host_control_transports" in text
    assert "direct_model_visible" in text


def test_generated_cortex_doc_is_current() -> None:
    proc = subprocess.run(
        [sys.executable, "internal/truth/generate_cortex_doc.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert CORTEX_DOC_PATH.exists()


def test_math_to_code_map_schema() -> None:
    status = _load_status()
    math_map = status.get("math_to_code_map")
    # The math_to_code_map is the structural ledger for load-bearing math
    # objects. Each entry must have id, label, packet_ref, code_refs,
    # proof_refs, status; closeout law_to_code_completeness rows can
    # reference an entry via math_object_id for a mechanical join.
    assert isinstance(math_map, list) and math_map, "math_to_code_map must be a non-empty list"
    valid_states = {"implemented", "explicit_zero", "future_not_active"}
    seen_ids: set[str] = set()
    for entry in math_map:
        assert isinstance(entry, dict)
        assert {"id", "label", "packet_ref", "code_refs", "proof_refs", "status"} <= set(entry)
        assert isinstance(entry["id"], str) and entry["id"].strip()
        assert entry["id"] not in seen_ids, f"duplicate math_to_code_map id: {entry['id']}"
        seen_ids.add(entry["id"])
        assert isinstance(entry["label"], str) and entry["label"].strip()
        assert isinstance(entry["packet_ref"], str) and entry["packet_ref"].strip()
        assert isinstance(entry["code_refs"], list) and entry["code_refs"]
        assert all(isinstance(ref, str) and ref.strip() for ref in entry["code_refs"])
        assert isinstance(entry["proof_refs"], list) and entry["proof_refs"]
        assert all(isinstance(ref, str) and ref.strip() for ref in entry["proof_refs"])
        assert entry["status"] in valid_states
    # Keystone objects every load-bearing seam may reference must be present
    # so closeout law_to_code rows can join via math_object_id.
    keystones = {
        "operator_brain_capability_envelope",
        "risk_weight",
        "host_reliability_prior",
        "preservation_state",
        "goal_debt_state",
    }
    assert keystones <= seen_ids


def test_v2_model_io_analysis_is_two_sided_and_synthesized() -> None:
    status = _load_status()
    audit = status["v2_model_io_analysis"]

    assert "structural evidence only" in audit["source_note"]
    assert "https://developers.openai.com/codex/hooks" in audit["source_note"]
    lifecycle = {entry["id"]: entry for entry in audit["lifecycle_adapters"]}
    assert {"claude_code", "codex_app"} <= set(lifecycle)
    assert "transcript_path" in lifecycle["claude_code"]["lifecycle_input"]
    assert "last_assistant_message" in lifecycle["codex_app"]["lifecycle_input"]
    assert "[features].codex_hooks = true" in lifecycle["codex_app"]["lifecycle_input"]
    assert "trusted `.codex/`" in lifecycle["codex_app"]["lifecycle_input"]
    assert "not live model-side product lift" in lifecycle["codex_app"]["enforcement"]

    side_a = {entry["id"]: entry for entry in audit["side_a_internal_logic"]}
    side_b = {entry["id"]: entry for entry in audit["side_b_model_visible_translation"]}
    synthesis = {entry["id"]: entry for entry in audit["synthesis_gap_boundary_decisions"]}
    assert side_a
    assert set(side_a) == set(side_b) == set(synthesis)
    assert {
        "event_dispatch_and_commitments",
        "goal_branch_continuity",
        "brake_uncertainty_modulators",
        "operator_routing_and_capability",
        "aux_support_publications",
        "verified_work_preservation",
        "feedback_window_realization",
        "host_runtime_sessions",
        "host_control_transports",
    } <= set(side_a)
    assert side_b["host_control_transports"]["visibility_class"] == "direct_model_visible"
    assert side_b["aux_support_publications"]["visibility_class"] == "support_only"
    assert "post-training" in synthesis["host_control_transports"]["post_training_boundary"]

    for entry in side_a.values():
        assert entry["code_refs"]
        assert entry["proof_refs"]
        for ref in entry["code_refs"] + entry["proof_refs"]:
            assert (REPO_ROOT / ref).exists(), ref


def test_charter_and_boundary_are_archived_under_product() -> None:
    # CORTEX_PRODUCT_CHARTER.md and CORTEX_PRODUCT_BOUNDARY.md were
    # subsumed by docs/CORTEX.md and moved to docs/archive/product/ so
    # the existing archive taxonomy stays preserved (charter and boundary
    # are product-surface docs, hence archive/product/, not archive root).
    assert ARCHIVED_CHARTER_PATH.exists()
    assert ARCHIVED_BOUNDARY_PATH.exists()
    assert not (REPO_ROOT / "docs" / "CORTEX_PRODUCT_CHARTER.md").exists()
    assert not (REPO_ROOT / "docs" / "CORTEX_PRODUCT_BOUNDARY.md").exists()


def test_public_docs_point_to_status_and_keep_archive_out_of_the_front_door() -> None:
    readme = _read(README_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    cortex_doc = _read(CORTEX_DOC_PATH)
    workflow = _read(WORKFLOW_DOC_PATH)

    assert "docs/CORTEX_STATUS.md" in readme
    assert "OpenAI product runtime on the CLI lane, with the direct service kept as a non-default backup surface" in readme
    assert "docs/CORTEX.md" in readme
    assert "Current Status" in docs_index
    assert "archive/" in docs_index
    assert "CORTEX.md" in docs_index
    assert "runtime_context/EVAL_RUBRIC.md" in docs_index
    assert "runtime_context/BASELINE_SHAPED_EXAMPLES.md" in docs_index
    assert "runtime_context/CROSS_HOST_SKETCH.md" in docs_index
    assert "recon/lifecycle_first_surface_matrix.md" in docs_index
    assert "recon/codex_app_hook_probe.md" in docs_index
    # CORTEX.md content anchors the previously-fragmented charter and
    # boundary identity material in one canonical surface.
    assert "executive-function layer that wraps a model after" in cortex_doc
    assert "internal/truth/cortex_status.json" in cortex_doc
    assert "docs/runtime_context/" in cortex_doc
    assert "docs/recon/lifecycle_first_surface_matrix.md" in cortex_doc
    assert "docs/recon/codex_app_hook_probe.md" in cortex_doc
    assert "EVAL_RUBRIC.md" in cortex_doc
    assert "BASELINE_SHAPED_EXAMPLES.md" in cortex_doc
    assert "CROSS_HOST_SKETCH.md" in cortex_doc
    assert "lifecycle-first surface reconnaissance" in cortex_doc.lower()
    assert "trusted project Stop hook loaded" in cortex_doc
    # Workflow rules unchanged.
    assert "paid OpenAI service-lane proof is never part of the default bundle" in workflow
    assert "requires explicit user approval in the current chat" in workflow
    assert "closeout contract artifact" in workflow
    assert "load_bearing" in workflow
    assert "hard-fails" in workflow
    assert "workflow-law terms touched" in workflow
    assert "reviewed-path drift during verification" in workflow
    assert "Cortex Mission Reflection" in workflow
    assert "Closure: Metadata" in workflow
    assert "fixed rows for `Progress:*`" in workflow
    assert "codex-app-hook-health" in workflow
    assert ".codex/hooks/cortex_mission_reflection_stop_hook.py" in workflow
    assert "last_assistant_message" in workflow
    assert "[features].codex_hooks = true" in workflow
    assert "`.codex/` layer is trusted" in workflow
    assert "structural lifecycle" in workflow
    assert "Goals Analysis" not in workflow
    for text in (readme, docs_index, cortex_doc):
        assert "CORTEX_V2_ACTIVE_WORKSTREAM" not in text
        assert "CORTEX_V2_PHASE_GATES_2" not in text
        assert "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE" not in text


def test_active_doc_allowlist_matches_status_registry() -> None:
    status = _load_status()
    expected = set(status["active_docs"])
    actual = {
        str(path.relative_to(REPO_ROOT))
        for path in DOCS_ROOT.rglob("*.md")
        if not path.is_relative_to(DOCS_ROOT / "archive")
    }

    assert actual == expected


def test_docs_directory_only_exposes_archive_and_workflow_subtrees() -> None:
    subdirs = sorted(path.name for path in DOCS_ROOT.iterdir() if path.is_dir())

    assert subdirs == ["archive", "internal", "recon", "runtime_context"]
    assert [path.name for path in (DOCS_ROOT / "internal").iterdir()] == ["REPO_WORKFLOW.md"]
    assert sorted(path.name for path in (DOCS_ROOT / "recon").iterdir()) == [
        "codex_app_hook_probe.md",
        "lifecycle_first_surface_matrix.md",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "runtime_context").iterdir()) == [
        "BASELINE_SHAPED_EXAMPLES.md",
        "CROSS_HOST_SKETCH.md",
        "EVAL_RUBRIC.md",
    ]


def test_runtime_context_eval_artifacts_are_documented_and_operationalized() -> None:
    rubric = _read(RUNTIME_CONTEXT_RUBRIC_PATH)
    examples = _read(RUNTIME_CONTEXT_EXAMPLES_PATH)
    cross_host = _read(RUNTIME_CONTEXT_CROSS_HOST_PATH)

    assert "docs/CORTEX.md` remains" in rubric
    assert "baseline-vs-shaped" in rubric
    assert "Premature closure" in rubric
    assert "Evidence recovery" in rubric
    assert "Goal continuity" in rubric
    assert "0 | 1 | 2 | 3" in rubric
    assert "out of 9" in rubric
    assert "at least 2 points higher" in rubric
    assert "regresses by more than 1" in rubric
    assert "route/block/closure changes" in rubric

    assert "Example 1: Clear Shaped Win" in examples
    assert "Example 2: Shaped Loss / Regression" in examples
    assert "Example 3: Changed But Not Meaningful" in examples
    assert "probe=unsupported" in examples
    assert "over-constraint risk" in examples
    assert "Baseline output" in examples
    assert "Shaped output" in examples
    assert "| Premature closure |" in examples
    assert "Shaped wins by +7" in examples
    assert "Shaped regresses by -3" in examples
    assert "No score improvement" in examples

    assert "OpenAIHostControlRequest.instructions" in cross_host
    assert "ClaudeHostControlRequest.system" in cross_host
    assert "GeminiHostControlRequest.instructions" in cross_host
    assert "systemInstruction" in cross_host
    assert "does not implement Claude or Gemini" in cross_host


def test_lifecycle_surface_recon_has_required_matrix_and_caveats() -> None:
    text = _read(LIFECYCLE_SURFACE_RECON_PATH)

    assert "Surface: internal / recon" in text
    assert "Retrieved: 2026-04-29" in text
    assert "Target date: state of the world as of 2026-04-28" in text
    assert "This is reconnaissance, not architecture" in text

    for heading in [
        "### OpenAI: API (Responses)",
        "### OpenAI: Codex CLI",
        "### OpenAI: Codex App for Mac",
        "### Anthropic: API (Messages)",
        "### Anthropic: Claude Code CLI",
        "### Anthropic: Claude Code App for Mac",
        "### Google: API (Gemini)",
        "### Google: Gemini CLI",
        "### Google: Gemini App for Mac",
    ]:
        assert heading in text

    for phrase in [
        "**Extension surfaces.**",
        "**Mechanism strength.**",
        "**Lifecycle-first fit.**",
        "**Pros / cons.**",
        "Where Verified-Work Preservation Survives",
        "CLI / App Relationships",
        "MCP Convergence",
        "Realistic Shape of Cortex as an External Process",
        "Questions Requiring Empirical Verification",
        "Stale or Missing Documentation",
        "## Sources",
    ]:
        assert phrase in text

    assert "Codex `Stop` hooks expose `last_assistant_message`" in text
    assert "Gemini CLI has recent hook documentation" in text
    assert "full wrap" in text
    assert "partial influence" in text
    assert "observation-only" in text
    assert "doesn't port" in text
    assert "Retrieved" in text and "Last updated" in text
    assert "older than six months" in text


def test_codex_app_hook_probe_records_empirical_findings_and_cleanup() -> None:
    text = _read(CODEX_APP_HOOK_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Codex App for Mac" in text
    assert "26.422.71525" in text
    assert "2210" in text
    assert "codex-cli 0.126.0-alpha.8" in text
    assert "CORTEX_PROBE_SENTINEL_2026_04_30" in text

    for phrase in [
        "Q1: Does Codex App load trusted project-level `.codex/config.toml`, and does trust persist?",
        "Q2: Does the Stop hook fire, and what input shape does it receive?",
        "Q3: Does `decision: \"block\"` inject a sentinel reason into the next assistant turn?",
        "**Confirmed**",
        "Field Enumeration",
        "Operational Considerations",
        "title-generation Stop event",
        "`transcript_path != null`",
        "Discovered Behaviors",
        "cache project Stop-hook configuration at the thread",
        "updates to hook config or hook files require closing and reopening Codex App",
        "Not found in public docs page",
        "Raw Hook Input: Subject ACKNOWLEDGED",
        "Actual next-assistant-turn output, byte-for-byte",
        "Exact Temporary `.codex/config.toml`",
        "Exact Temporary Hook Script",
        "Cleanup Verification",
        "Original `.codex/config.toml` restored: yes",
        "Temporary probe hook active after cleanup: no",
        "Active `.codex` config references `codex_app_probe_stop_hook.py`: no",
        "Focused docs-boundary test green: yes",
        "does not generalize to Claude Code",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "stop_hook_active",
        "last_assistant_message",
    ]:
        assert f"`{key}`" in text

    assert "ACKNOWLEDGED" in text
    assert "BASELINE" in text
    assert "REOPENED" in text
    assert "Stop - Codex App hook probe" in text


def test_generated_status_doc_is_current() -> None:
    proc = subprocess.run(
        [sys.executable, "internal/truth/generate_status.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert STATUS_DOC_PATH.exists()


def test_status_registry_is_complete_and_stable() -> None:
    status = _load_status()

    assert set(status) >= {
        "resting_state",
        "bootstrap",
        "product_goal",
        "identity",
        "executive_completion",
        "bio_to_code_matrix",
        "math_to_code_rules",
        "v2_model_io_analysis",
        "work_today",
        "next_product_train",
        "system_map",
        "subsystems",
        "packet_to_code_anchors",
        "hosts",
        "conformance_summary",
        "closure_gates",
        "retained_evidence_refs",
        "proof_commands",
        "retained_data",
        "where_to_work",
        "blocked_moves",
        "active_docs",
    }
    assert status["resting_state"]["branch"] == "main"
    assert "installable executive layer" in status["identity"]["statement"]
    assert status["executive_completion"]["shippable_threshold_percent"] == 85
    assert status["bio_to_code_matrix"]
    assert status["math_to_code_rules"]["law_revision_rule"]
    assert sum(item["weight"] for item in status["bio_to_code_matrix"]) == 100
    current_percent = round(
        sum(
            status["executive_completion"]["status_fraction"][item["status"]] * item["weight"]
            for item in status["bio_to_code_matrix"]
        )
    )
    assert current_percent == 100
    assert current_percent >= status["executive_completion"]["shippable_threshold_percent"]
    matrix_status = {
        item["skill"]: item["status"] for item in status["bio_to_code_matrix"]
    }
    status_mix = {
        key: sum(1 for item in status["bio_to_code_matrix"] if item["status"] == key)
        for key in ("landed", "partial", "north_star")
    }
    assert status_mix == {"landed": 8, "partial": 0, "north_star": 0}
    assert matrix_status["Uncertainty handling and brake"] == "landed"
    assert (
        matrix_status["Branch continuity, suspend/resume, and truthful closure"]
        == "landed"
    )
    assert matrix_status["Intervention pricing versus neutrality"] == "landed"
    assert matrix_status["Blocker surfacing and goal-debt management"] == "landed"
    assert matrix_status["Multi-host executive continuity"] == "landed"
    assert matrix_status["Offline consolidation and support geometry"] == "landed"
    assert status["executive_completion"]["next_raise"] == [
        {
            "skill": "No remaining denominator row",
            "expected_points_if_landed": 0,
            "why": "The full executive denominator is already landed, so the active leverage is code-quality, proof-confidence, dead-weight elimination, and live-run reliability rather than score expansion.",
        }
    ]
    host_status = {
        item["name"]: item["conformance"] for item in status["hosts"]
    }
    host_surfaces = {
        item["name"]: item["strongest_surface"] for item in status["hosts"]
    }
    assert host_status == {
        "openai": "conformant",
        "claude": "conformant",
        "gemini": "conformant",
        "reference": "conformant",
    }
    assert host_surfaces == {
        "openai": "operator_cli",
        "claude": "operator_cli",
        "gemini": "operator_cli",
        "reference": "reference_cli",
    }
    assert status["conformance_summary"]["shipping_default"] == "openai:operator_cli"
    next_train_slug = status["next_product_train"]["slug"]
    assert next_train_slug is None or next_train_slug != status["work_today"]["slug"]
    assert "research_lines_under_evaluation" in status
    assert isinstance(status["research_lines_under_evaluation"], list)
    for entry in status["research_lines_under_evaluation"]:
        assert isinstance(entry, dict)
        assert {"slug", "stage", "summary", "next_step"} <= set(entry)
        assert entry["slug"] != status["work_today"]["slug"]
        assert entry["slug"] != status["next_product_train"]["slug"]
    assert status["work_today"]["slug"] == "brain-capability-aware-routing"
    assert "full_cross_host" in status["work_today"]["note"]
    assert "posture-sensitive online control is s-tier closed" in status["work_today"]["note"].lower()
    assert "exact-family unchanged-condition repetition tax" in status["work_today"]["note"]
    assert "reference and openai explicit-publication lanes" in status["work_today"]["note"].lower()
    assert "memory-off when no publication is supplied" in status["work_today"]["note"]
    assert "Q_mem = 0" in status["work_today"]["note"]
    assert "asymmetric error cost and tonic hysteresis are now earned" in status["work_today"]["note"].lower()
    assert "brain-capability-aware routing is now earned" in status["work_today"]["note"].lower()
    assert "operatorbraincapabilityenvelope" in status["work_today"]["note"].lower()
    assert status["next_product_train"]["slug"] == "brain-capability-observation-and-inference"
    assert "product + experimental + aux" == status["next_product_train"]["surface"]
    assert "observed-performance accumulator" in status["next_product_train"]["executive_benefit"].lower()
    assert "publish through aux support side" in status["next_product_train"]["guardrail"].lower()
    assert "ttl must expire stale observations" in status["next_product_train"]["guardrail"].lower()
    assert "Keep the bounded audit surface compact and truthful" in status["where_to_work"][0]
    assert "no-spend live evidence current and explicit" in status["where_to_work"][1]
    assert "posture-sensitive online control is s-tier closed" in status["where_to_work"][2].lower()
    assert "anti-thrash is landed" in status["where_to_work"][2]
    assert "posture truth is single-owned" in status["where_to_work"][2]
    assert "6-axis geometry term" in status["where_to_work"][2]
    assert "route truth stays bounded and non-sovereign" in status["where_to_work"][2]
    assert "live `Q_mem` stays zero" in status["where_to_work"][2]
    assert "host/tool reliability and affordance priors are earned" in status["where_to_work"][2]
    assert "brain-capability-aware-routing seam is the active focus" in status["where_to_work"][3]
    closure_gates = {gate["id"]: gate for gate in status["closure_gates"]}
    assert closure_gates["main_synced"]["status"] == "required"
    assert closure_gates["cleanup_report"]["status"] == "required"
    assert closure_gates["single_truth"]["status"] == "passed"
    assert "Required workflow gate" in closure_gates["main_synced"]["note"]
    assert "Required workflow gate" in closure_gates["cleanup_report"]["note"]


def test_generated_status_doc_includes_system_map_and_next_product_train() -> None:
    text = _read(STATUS_DOC_PATH)

    assert "## System Map" in text
    assert "```mermaid" in text
    assert "## Identity And Research Stance" in text
    assert "## Live Product Truth" in text
    assert "## Current Focus" in text
    assert "## Bio-To-Code Matrix" in text
    assert "## Math To Code Rules" in text
    assert "human executive function" in text
    assert text.index("## Live Product Truth") < text.index("## Bio-To-Code Matrix")
    assert "## Denominator / Completion Context" not in text
    assert "Current full-executive completion:" not in text
    assert "Shippable threshold for the full executive:" not in text
    assert "When user asks where Cortex is at now:" not in text
    assert "background completion context" not in text
    assert "Active quality/risk focus" in text
    assert "## Packet To Code" in text
    assert "## Next Product Train" in text
    assert "## Research Lines Under Evaluation" in text
    assert "host/tool reliability and affordance priors are earned" in text
    assert "`brain-capability-aware-routing`" in text
    assert "- Next product train after the current focus: `brain-capability-observation-and-inference`" in text
    assert "- Train: `brain-capability-observation-and-inference`" in text
    assert "memory-off when no publication is supplied" in text
    assert "Shipping Product Lane\\nopenai:operator_cli" in text or "Shipping Product Lane" in text
    assert "Shipping default: `openai:operator_cli`" in text
    assert "Workflow gates marked `required` are contractual gates checked by `repo_workflow.py`" in text
    assert "| `main_synced` | `required` |" in text
    assert "| `cleanup_report` | `required` |" in text
    assert "exact-family unchanged-condition repetition tax" in text
    assert "full_cross_host" in text
    assert "posture-sensitive online control is s-tier closed" in text.lower()
    assert "stream-only churn stays visible but non-epistemic" in text
    assert "`visible_burden_sensitivity`" in text


def test_next_product_train_sentence_fields_render_without_outer_backtick_wrap() -> None:
    """Render-quality pin: ``primary_metric``, ``guardrail``, and ``kill_rule`` are
    sentence-form fields whose values may contain inner backticks for inline code
    spans (for example, ``\\`tonic_quiescence\\```). Wrapping the entire value in
    outer backticks would create nested code spans that Markdown renders as
    alternating and reversed code regions (the inverse of intent). The renderer
    at ``internal/truth/generate_status.py`` must emit these three fields without
    an outer backtick wrap, matching the ``executive_benefit`` and ``why_now``
    pattern. Bare-identifier fields (``slug``, ``surface``) stay wrapped."""
    text = _read(STATUS_DOC_PATH)
    lines = text.splitlines()
    for prefix in ("- Primary metric: ", "- Guardrail: ", "- Kill rule: "):
        line = next((line for line in lines if line.startswith(prefix)), None)
        assert line is not None, f"missing {prefix!r} line in CORTEX_STATUS.md"
        first_char = line[len(prefix) : len(prefix) + 1]
        assert first_char != "`", (
            f"render regression: {prefix!r} line is outer-backtick-wrapped, which "
            f"creates nested code spans when the value contains inner backticks. "
            f"Drop the outer wrap in internal/truth/generate_status.py so this "
            f"field matches the executive_benefit / why_now pattern."
        )


def test_next_product_train_truth_never_silently_duplicates_current_train() -> None:
    status = _load_status()
    next_train_slug = status["next_product_train"]["slug"]
    assert next_train_slug is None or next_train_slug != status["work_today"]["slug"]


def test_front_door_surfaces_point_to_local_first_and_explicit_publish_closeout() -> None:
    agents = _read(AGENTS_PATH)
    status = _read(STATUS_DOC_PATH)

    assert 'close-session --message "scope: end-state summary"' in status
    assert 'close-session --publish --message "scope: end-state summary"' in status
    assert "cleanup-report" in status
    assert "explicit denominator or progress-accounting questions" in agents
    assert "close-session --publish" in agents
    assert "manual publication" not in agents.lower()
    assert "manual publication" not in status.lower()
    assert "separate publication step" not in status.lower()


def test_generated_archive_index_is_current() -> None:
    proc = subprocess.run(
        [sys.executable, "internal/archive/generate_archive_index.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert ARCHIVE_INDEX_PATH.exists()


def test_archive_manifest_tracks_retained_refs_and_offloaded_payloads() -> None:
    manifest = json.loads(_read(ARCHIVE_MANIFEST_PATH))

    assert manifest["retained_evidence_refs"]
    assert manifest["offloaded_payloads"]
    assert any(entry["ref"] == "archive/e23-preservation-state-machine" for entry in manifest["retained_evidence_refs"])


def test_no_active_code_homes_remain_under_experimental() -> None:
    experimental_python = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "experimental").rglob("*.py")
        if path.name != "__init__.py"
    )

    assert experimental_python == []


def test_legacy_test_buckets_are_removed() -> None:
    assert not (REPO_ROOT / "tests" / "unit").exists()
    assert not (REPO_ROOT / "tests" / "integration").exists()


def test_lab_output_quality_fixtures_are_source_only() -> None:
    forbidden = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "tests" / "lab" / "fixtures" / "output_quality").rglob("*")
        if path.is_dir() and path.name in {"node_modules", "dist", ".astro"}
    )

    assert forbidden == []


def test_product_package_does_not_import_non_product_surfaces() -> None:
    forbidden_patterns = (
        "from experimental",
        "import experimental",
        "from lab",
        "import lab",
        "from internal",
        "import internal",
    )

    for path in (REPO_ROOT / "cortex").rglob("*.py"):
        text = _read(path)
        for pattern in forbidden_patterns:
            assert pattern not in text, f"{path} imports non-product surface via {pattern!r}"


def test_public_packaging_surface_is_explicit() -> None:
    config = tomllib.loads(_read(PYPROJECT_PATH))

    scripts = config["project"]["scripts"]
    assert scripts == {
        "cortex-openai-cli": "cortex.hosts.openai.cli:main",
        "cortex-openai-service": "cortex.hosts.openai.service:main",
    }


def test_root_makefile_is_purpose_first() -> None:
    text = _read(ROOT_MAKEFILE_PATH)

    assert "product-test:" in text
    assert "conformance-test:" in text
    assert "experimental-test:" in text
    assert "lab-test:" in text
    assert "archive-test:" in text
    assert "make repo-hygiene is internal and deprecated; use make -C internal cleanup-report" in text
