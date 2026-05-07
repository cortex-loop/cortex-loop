"""Boundary and single-truth sync checks for the repo reset."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

from internal.truth.orientation import MAX_ORIENTATION_WORDS


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
CLAUDE_PATH = REPO_ROOT / "CLAUDE.md"
CORTEX_DOC_PATH = REPO_ROOT / "docs" / "CORTEX.md"
CORTEX_V2_SRE_PATH = REPO_ROOT / "docs" / "CORTEX_V2_SRE_2.md"
EXECUTIVE_RUNTIME_TRACKER_PATH = (
    REPO_ROOT / "docs" / "CORTEX_EXECUTIVE_RUNTIME_TRACKER.md"
)
EXECUTIVE_RUNTIME_PROGRAM_SPEC_PATH = (
    REPO_ROOT / "docs" / "CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md"
)
EXECUTIVE_RUNTIME_PHASE_5_READINESS_PATH = (
    REPO_ROOT / "docs" / "CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md"
)
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
RUNTIME_CONTEXT_RUBRIC_PATH = REPO_ROOT / "docs" / "runtime_context" / "EVAL_RUBRIC.md"
RUNTIME_CONTEXT_EXAMPLES_PATH = (
    REPO_ROOT / "docs" / "runtime_context" / "BASELINE_SHAPED_EXAMPLES.md"
)
RUNTIME_CONTEXT_CROSS_HOST_PATH = (
    REPO_ROOT / "docs" / "runtime_context" / "CROSS_HOST_SKETCH.md"
)
CORTEX_PLUGIN_DESIGN_PATH = REPO_ROOT / "docs" / "cortex_plugin" / "DESIGN.md"
CORTEX_PLUGIN_ADAPTER_PATH = REPO_ROOT / "docs" / "cortex_plugin" / "ADAPTER.md"
CORTEX_PLUGIN_EVIDENCE_SYNTHESIS_PATH = (
    REPO_ROOT / "docs" / "cortex_plugin" / "EVIDENCE_SYNTHESIS.md"
)
COMMUNICATION_PROBLEM_DIR = (
    REPO_ROOT / "docs" / "cortex_plugin" / "communication_problem"
)
COMMUNICATION_PROBLEM_FILES = [
    COMMUNICATION_PROBLEM_DIR / "01_problem_statement.md",
    COMMUNICATION_PROBLEM_DIR / "02_cortex_identity_and_doctrine.md",
    COMMUNICATION_PROBLEM_DIR / "03_maths_to_code.md",
    COMMUNICATION_PROBLEM_DIR / "04_cortex_internal_state.md",
    COMMUNICATION_PROBLEM_DIR / "05_claude_communication_surface.md",
    COMMUNICATION_PROBLEM_DIR / "06_hook_surface_and_evidence.md",
    COMMUNICATION_PROBLEM_DIR / "07_strange_loop_frame.md",
    COMMUNICATION_PROBLEM_DIR / "08_anti_patterns_and_failed_solutions.md",
]
LIFECYCLE_SURFACE_RECON_PATH = (
    REPO_ROOT / "docs" / "recon" / "lifecycle_first_surface_matrix.md"
)
CODEX_APP_HOOK_PROBE_PATH = REPO_ROOT / "docs" / "recon" / "codex_app_hook_probe.md"
CLAUDE_CODE_DESKTOP_PRETOOLUSE_PROBE_PATH = (
    REPO_ROOT / "docs" / "recon" / "claude_code_desktop_pretooluse_probe.md"
)
CLAUDE_CODE_USER_SCOPE_PLUGIN_PRETOOLUSE_PROBE_PATH = (
    REPO_ROOT / "docs" / "recon" / "claude_code_user_scope_plugin_pretooluse_probe.md"
)
CLAUDE_CODE_USER_SCOPE_PLUGIN_MANAGED_WORKTREE_PROBE_PATH = (
    REPO_ROOT / "docs" / "recon" / "claude_code_user_scope_plugin_managed_worktree_probe.md"
)
CLAUDE_CODE_CORTEX_RUNTIME_CONTEXT_CONNECTIVITY_PROBE_PATH = (
    REPO_ROOT / "docs" / "recon" / "claude_code_cortex_runtime_context_connectivity_probe.md"
)
CLAUDE_CODE_CORTEX_STOP_CLOSURE_CONNECTIVITY_PROBE_PATH = (
    REPO_ROOT / "docs" / "recon" / "claude_code_cortex_stop_closure_connectivity_probe.md"
)
CLAUDE_CODE_CORTEX_HEADLESS_CLI_EQUIVALENCE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "claude_code_cortex_headless_cli_equivalence_probe.md"
)
CLAUDE_CODE_CORTEX_BRIDGE_TRANSLATION_HEADLESS_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "claude_code_cortex_bridge_translation_headless_probe.md"
)
CLAUDE_CODE_CORTEX_MAC_PENDING_GOAL_DIVERGENCE_RETEST_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "claude_code_cortex_mac_pending_goal_divergence_retest.md"
)
CLAUDE_CODE_CORTEX_POSTTOOL_FAILURE_TO_STOP_LOOP_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "claude_code_cortex_posttool_failure_to_stop_loop_probe.md"
)
CLAUDE_CODE_CORTEX_USERPROMPTSUBMIT_VERIFIED_WORK_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "claude_code_cortex_userpromptsubmit_verified_work_probe.md"
)
OPENAI_OPERATOR_SILENT_CONTROL_LIVE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_silent_control_live_probe.md"
)
OPENAI_OPERATOR_DEBT_CONTROL_ENACTMENT_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_debt_control_enactment.md"
)
OPENAI_OPERATOR_SILENT_CONTROL_LIVE_PROBE_RETRY_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_silent_control_live_probe_retry.md"
)
OPENAI_OPERATOR_OUTPUT_QUALITY_FIXTURE_REFRESH_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_output_quality_fixture_refresh.md"
)
OPENAI_OPERATOR_VERIFICATION_DEBT_CONTINUATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_verification_debt_continuation.md"
)
OPENAI_OPERATOR_VISIBLE_INTERVENTION_LIVE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_visible_intervention_live_probe.md"
)
VISIBLE_INTERVENTION_PRODUCT_PERCEPTION_HARDENING_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_visible_intervention_product_perception_hardening.md"
)
OPENAI_OPERATOR_VISIBLE_INTERVENTION_HARDENED_RERUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_openai_operator_visible_intervention_hardened_rerun.md"
)
CODEX_APP_CLI_STOP_ACTIVATION_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_hook_native_stop_activation_probe.md"
)
CODEX_APP_CLI_STOP_LIVE_CANARY_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_hook_native_stop_live_canary.md"
)
CODEX_APP_CLI_PRODUCT_PERCEPTION_LOOP_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_product_perception_loop.md"
)
CODEX_APP_CLI_PRODUCT_PERCEPTION_LIVE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_product_perception_live_probe.md"
)
CODEX_APP_CLI_PRODUCT_EVENT_CAPTURE_REMEDIATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_product_event_capture_remediation.md"
)
CODEX_APP_CLI_STOP_CONTINUATION_RESOLUTION_LOOP_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_stop_continuation_resolution_loop.md"
)
CODEX_APP_CLI_HOOK_NATIVE_BEHAVIOR_COMPARISON_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_hook_native_behavior_comparison.md"
)
CODEX_APP_CLI_ASTRO_THREE_ARM_FIXTURE_REFRESH_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_astro_three_arm_fixture_refresh.md"
)
CODEX_APP_CLI_VALUE_ABLATION_AUDIT_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_value_ablation_audit.md"
)
CODEX_APP_CLI_TASK_STANDARD_SPINE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_spine.md"
)
CODEX_APP_CLI_TASK_STANDARD_LIVE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_live_probe.md"
)
CODEX_APP_CLI_TASK_STANDARD_LIVE_RUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_live_run.md"
)
CODEX_APP_CLI_HOOK_CONTRACT_CAPTURE_BOUNDARY_REMEDIATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_hook_contract_capture_boundary_remediation.md"
)
CODEX_APP_CLI_TASK_STANDARD_CONTEXT_LIVE_RERUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_context_live_rerun.md"
)
CODEX_APP_CLI_COMMUNICATION_BOUNDARY_AUDIT_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_communication_boundary_audit_and_hardening.md"
)
CODEX_APP_CLI_TASK_STANDARD_PRETOOL_TRANSCRIPT_CAPTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_pretool_transcript_capture.md"
)
CODEX_APP_CLI_TASK_STANDARD_LIVE_CAPTURE_RERUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_live_capture_rerun.md"
)
CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_CALIBRATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_stop_gating_calibration_probe.md"
)
CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_LIVE_RUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_stop_gating_live_run.md"
)
CODEX_APP_CLI_TASK_STANDARD_BEHAVIOR_COMPARISON_HARNESS_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_behavior_comparison_harness.md"
)
CODEX_APP_CLI_TASK_STANDARD_BEHAVIOR_COMPARISON_LIVE_RUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_behavior_comparison_live_run.md"
)
CODEX_APP_CLI_LIFECYCLE_ACTUATOR_MAP_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_lifecycle_actuator_map.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NEXT_STEP_CORRECTION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_next_step_correction.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_CALIBRATION_DECISION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_calibration_decision.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NARROW_LIVE_PROBE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_narrow_live_probe.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NARROW_LIVE_RUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_narrow_live_run.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_ACTUATOR_ARCHITECTURE_DECISION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_actuator_architecture_decision.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_GATE0_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_calibration_gate0.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_NARROW_LIVE_RUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_run.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_FIRING_BOUNDARY_REMEDIATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_firing_boundary_remediation.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_NARROW_LIVE_RERUN_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_OVERCONTROL_REMEDIATION_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_overcontrol_remediation.md"
)
CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_ACTUATOR_TRACE_REPAIR_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_task_standard_actuator_trace_repair.md"
)
CODEX_APP_CLI_POSTTOOLUSE_CAUSAL_TRACE_IDS_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_posttooluse_causal_trace_ids.md"
)
CODEX_APP_CLI_TASK_STANDARD_STACK_PUBLICATION_HYGIENE_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_codex_app_cli_task_standard_stack_publication_hygiene.md"
)
TASK_STANDARD_SRE_CORRESPONDENCE_RECON_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_task_standard_sre_correspondence_reconciliation.md"
)
TASK_STANDARD_EXECUTIVE_DOCTRINE_MATH_RECON_PATH = (
    REPO_ROOT
    / "docs"
    / "recon"
    / "cortex_task_standard_executive_doctrine_math_refinement.md"
)
SEMANTIC_CONTRACTION_AUDIT_RECON_PATH = (
    REPO_ROOT / "docs" / "recon" / "cortex_semantic_contraction_audit.md"
)
STATUS_REGISTRY_PATH = REPO_ROOT / "internal" / "truth" / "cortex_status.json"
STATUS_DOC_PATH = REPO_ROOT / "docs" / "CORTEX_STATUS.md"
WORKFLOW_DOC_PATH = REPO_ROOT / "docs" / "internal" / "REPO_WORKFLOW.md"
MISSION_REFLECTION_CONTRACT_PATH = (
    REPO_ROOT / "docs" / "internal" / "MISSION_REFLECTION_CONTRACT.md"
)
ANTI_DRIFT_RULES_PATH = REPO_ROOT / "docs" / "internal" / "ANTI_DRIFT_RULES.md"
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
identity and narrative fit; the V2 packet docs (`docs/CORTEX_V2_*.md`) for
packet law; `internal/truth/cortex_status.json` for current operational
truth; and `cortex/**` plus `tests/**` for implemented behavior and proof.

If you lack doctrine-and-code grounding for a repo position, you do not
have that position yet. Read the specific missing surface, or say "I don't
know yet; I need to check X." Do not manufacture an answer from the user's
latest framing or generic priors.

If context was compacted or your Cortex model feels thin, run
`python3 internal/workflow/repo_workflow.py orient`; use its generated
capsule as orientation only, then ground repo positions in the cited docs,
code, and tests.

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
    # AGENTS.md is now orientation only; workflow mechanics, grid contract,
    # and anti-drift history live in separate internal docs.
    assert 90 <= len(lines) <= 160
    assert sections == [
        "## Agent Briefing",
        "## Bootstrap",
        "## Answer First",
        "## Mission",
        "## Authority",
        "## Non-Negotiables",
        "## Working Mode",
        "## Truth Distinctions",
        "## Pointers",
    ]
    # Briefing block must be present verbatim; CLAUDE.md's copy is
    # byte-equal so Claude Code and Codex see the same instructions.
    assert AGENT_BRIEFING_TEXT in text
    # Mission and answer-shape anchors that downstream agents rely on.
    assert "rich multi-host executive layer" in text
    assert "installable executive layer" in text
    assert "human executive function" in text
    assert "live evidence" in text
    assert "The substantive answer to the user's request is the primary deliverable." in text
    assert "Bootstrap reads are preparation, not response content." in text
    assert "The operator-split note belongs in turns that involve user empirical work" in text
    assert "repo_workflow.py orient" in text
    assert "generated\ncapsule as orientation only" in text
    assert "For product claims, plans, or implementation seams" in text
    assert "model-I/O\npath" in text
    # Authority surfaces named including CORTEX.md as narrative authority.
    assert "docs/CORTEX.md" in text
    assert "internal/truth/cortex_status.json" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "docs/internal/REPO_WORKFLOW.md" in text
    assert "docs/internal/MISSION_REFLECTION_CONTRACT.md" in text
    assert "docs/internal/ANTI_DRIFT_RULES.md" in text
    assert "AGENTS.md" in text
    # Bootstrap reads include CORTEX.md as the second read.
    assert "git branch --show-current" in text
    assert "git status --short --untracked-files=all" in text
    # Truth distinctions kept explicit.
    assert "shipping truth" in text
    assert "conformance truth" in text
    assert "This root `AGENTS.md` is the only agent contract in the repo." in text
    # Non-negotiables (live-spend lock and registry-truth-discipline).
    assert "Do not run paid service-lane commands" in text
    assert "approves" in text and "spend in the current chat" in text
    assert "Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED`" in text
    assert "Do not claim product progress unless shipped runtime behavior changed" in text
    assert "Do not let task identity become product policy" in text
    assert "Fixtures, task domains,\n  hidden verifiers, and benchmarks are examples" in text
    assert "product_spine" in text
    assert "task-identity examples stay outside product triggers" in text
    assert "Preserve the anti-drift rules" in text
    # PHI-label decision loop and PHILOSOPHY_AUDIT block must be retired.
    # Their content moved into docs/CORTEX.md §6 and the agent briefing.
    assert "PHI_MINIFY" not in text
    assert "PHI_MISSION" not in text
    assert "PHI_NICHE" not in text
    assert "PHILOSOPHY_AUDIT" not in text
    # Mission-reflection and workflow mechanics are referenced, not inlined.
    assert "Cortex Mission Reflection" in text
    assert "Mission reflection is administrative closure." in text
    assert ".claude/hooks/cortex_grid_stop_hook.py" not in text
    assert "No-mimicry rule" not in text
    assert "grid-validate" not in text
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
    assert "repo_workflow.py orient" in text
    assert "generated\ncapsule as orientation only" in text
    # No anti-drift duplication; CLAUDE.md does not own anti-drift rules.
    assert "## Anti-Drift" not in text
    assert "PHI_MINIFY" not in text


def test_generated_orientation_capsule_stays_compact_and_subordinate() -> None:
    text = _read(STATUS_DOC_PATH)
    status = _load_status()
    start = text.index("## Cortex Orientation Capsule")
    end = text.index("## Live Product Truth")
    capsule = text[start:end]
    words = [part for part in capsule.replace("`", "").split() if part.strip()]

    assert len(words) <= MAX_ORIENTATION_WORDS
    assert "Generated orientation only" in capsule
    assert "authority remains scoped" in capsule
    assert "docs/CORTEX.md" in capsule
    assert "internal/truth/cortex_status.json" in capsule
    assert "post-training runtime executive-function layer" in capsule
    assert "not a plugin, translation layer, monitor, middleware pile" in capsule
    assert "Target loop: model/host event -> task-state and executive-risk understanding" in capsule
    assert "Grounding rule:" in capsule
    assert "model-I/O path" in capsule
    assert "structural proof alone does not earn model-output lift" in capsule
    assert "Core owns" in capsule
    assert "SRE owns" in capsule
    assert "AUX owns" in capsule
    assert "host adapters consume" in capsule
    assert "lab, eval, recon, archive, and workflow surfaces" in capsule
    assert f"Current train: `{status['work_today']['slug']}`" in capsule
    assert f"Next train: `{status['next_product_train']['slug']}`" in capsule
    assert f"Shipping default: `{status['conformance_summary']['shipping_default']}`" in capsule
    for entry in status["bio_to_code_matrix"]:
        assert entry["skill"] in capsule
    assert "Claude hook" not in capsule
    assert "Claude Code" not in capsule
    assert "client" not in capsule.lower()


def test_cortex_doc_is_canonical_narrative_with_required_sections() -> None:
    text = _read(CORTEX_DOC_PATH)
    lines = text.splitlines()
    sections = [line for line in lines if line.startswith("## ")]
    # CORTEX.md is the canonical narrative authority. The cap prevents
    # the document from drifting into per-session noise; the narrative
    # is meant to evolve only when major learnings warrant.
    assert len(lines) <= 745
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
    assert "Fixtures falsify Cortex" in text
    assert "Product Cortex may use task details as grounded anchors" in text
    assert "but never as product triggers" in text
    assert "Model-visible text classes are distinct" in text
    assert "lab prompt scaffolds are test apparatus" in text
    assert "product_spine" in text
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
    assert "Model-Visible Cortex Output Law" in text
    assert "task-local executive constraint" in text
    assert "Cortex says your debt" in text
    assert "First-person/ego style is allowed" in text
    assert "claim/evidence/obligation/task-standard/next-move" in text
    assert "Executive Capacity Map" in text
    assert "Task-set / standard formation" in text
    assert "`TaskStandardSpine`" in text
    assert "Goal maintenance" in text
    assert "Conflict monitoring" in text
    assert "Action gating" in text
    assert "Prediction-error recalibration" in text
    assert "delivery-layer analogy, not as a\nclaim of biological equivalence" in text


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


def test_executive_runtime_tracker_keeps_product_goal_and_live_truths_visible() -> None:
    text = _read(EXECUTIVE_RUNTIME_TRACKER_PATH)

    assert EXECUTIVE_RUNTIME_TRACKER_PATH.exists()
    assert "internal/truth/cortex_status.json" in text
    assert "not a second roadmap or registry" in text
    assert "post-training runtime executive-function layer" in text
    assert "Cortex should shape the model's behavior at runtime" in text
    assert "Communication is only the model-visible edge of Cortex." in text
    assert "Model-Visible Cortex Output Law" in text
    assert "outside person, plugin" in text
    assert "\"Cortex says\" authority" in text
    assert "First-person style is lawful only" in text
    assert "signed-off prospective task-set formation" in text
    assert "missing front half of the loop is task-standard formation" in text
    assert "construct a task-local standard" in text
    assert "model/host event" in text
    assert "task-state and executive-risk understanding" in text
    assert "task-local standards" in text
    assert "`TaskStandardSpine` is now a mapped SRE object" in text
    assert "signed-off UserPromptSubmit probe" in text
    assert "captured standard shapes later gating" in text
    assert "improved next model behavior" in text
    assert "Live-Model Achievement Matrix" in text
    assert "Live Evidence Scoreboard" in text
    assert "Cortex truth" in text
    assert "brain-wiring truth" in text
    assert "conformance truth" in text
    assert "shipping truth" in text
    assert "OpenAI remains shipping truth through `openai.codex_app_cli`" in text
    assert "Claude Code Desktop, Claude Code headless CLI, and individual hook findings are recon only" in text
    assert "Stop` closure pressure has narrow behavior-lift evidence" in text
    assert "`PreToolUse` and `UserPromptSubmit` delivery are real" in text
    assert "`PostToolUseFailure` and feedback persistence are real" in text
    assert "resolution deficit" in text
    assert "expectation debt" in text
    assert "goal-debt drag" in text
    assert "route pricing" in text
    assert "brake EMA" in text
    assert "AUX priors" in text
    assert "internal tags" in text
    assert "Semantic Contraction Discipline" in text
    assert "minifying readable code" in text
    assert "duplicate policy" in text
    assert "`cortex/**` is about 43.6K Python LOC" in text
    assert "`cortex/hosts` about 21.6K LOC" in text
    assert "four host `runtime.py` files" in text
    assert "per-host `session_io.py` parallelism" in text
    assert "`cortex/hosts/openai/codex_app_cli_hook_coordinator.py`" in text
    assert "large SRE/AUX" in text
    assert "schedule or explicitly\nwaive a contraction audit" in text
    assert "added/deleted" in text
    assert "Raw LOC reduction is not success" in text
    assert "Audit-Survivor Future Backlog" in text
    assert "serious candidate backlog, not casual brainstorming" in text
    assert "must consider these candidates" in text
    assert "To remove or demote a row" in text
    assert "`cortex-semantic-contraction-audit`" in text
    assert "deletion/consolidation map" in text
    assert "behavior-preservation proof requirements" in text
    assert "`evidence_landed`" in text
    assert "`driver-session-io-common-kernel-audit`" in text
    assert "`coordinator-actuator-boundary-extraction`" in text
    assert "`recon-archive-retirement-pass`" in text
    assert "`sre-aux-policy-concentration-audit`" in text
    assert "`workflow-connectivity-trace-reachability`" in text
    assert "`recon-frontmatter-indexer`" in text
    assert "`sre-output-law-rendering-contract`" in text
    assert "`core-proof-obligation-test-factories`" in text
    assert "`host-runtime-kernel-extraction-audit`" in text
    assert "`posttooluse-phase-aware-calibration`" in text
    assert "`pretooluse-motor-inhibition-gate0`" in text
    assert "`bayesian-kill-rule-shadow`" in text
    assert "`task-standard-semantic-alignment`" in text
    assert "`queueable_now`" in text
    assert "`queueable_after_probe`" in text
    assert "`research_backlog`" in text
    assert "Rows produced by the semantic contraction audit are serious candidate seams" in text
    assert "mathematically attractive" in text
    assert "If the answer starts with \"which hook can we use?\"" in text


def test_semantic_contraction_audit_records_candidates_without_runtime_claim() -> None:
    text = _read(SEMANTIC_CONTRACTION_AUDIT_RECON_PATH)
    status = _load_status()
    recon_paths = {
        path
        for role in status["doc_roles"]["roles"]
        if role["id"] == "recon_evidence"
        for path in role["paths"]
    }

    assert SEMANTIC_CONTRACTION_AUDIT_RECON_PATH.exists()
    assert "docs/recon/cortex_semantic_contraction_audit.md" in status["active_docs"]
    assert "docs/recon/cortex_semantic_contraction_audit.md" in recon_paths
    assert "Surface: internal / recon audit" in text
    assert "Semantic contraction is not minification" in text
    assert "behavior-preservation proof" in text
    assert "host runtime parallelism" in text
    assert "per-host driver/session I/O duplication" in text
    assert "`codex_app_cli_hook_coordinator.py` growth" in text
    assert "large SRE/AUX modules" in text
    assert "inactive lab/recon/doc active-surface retirement" in text
    assert "`delete`" in text
    assert "`collapse`" in text
    assert "`extract`" in text
    assert "`archive`" in text
    assert "`defer`" in text
    assert "No product behavior changed" in text
    assert "No runtime contraction, deletion, refactor" in text
    assert "No behavior lift" in text
    assert "shipping promotion" in text
    assert "status `next_product_train`" in text
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_retired_executive_runtime_roadmap_is_not_active_authority() -> None:
    assert not (REPO_ROOT / "docs" / "CORTEX_EXECUTIVE_RUNTIME_ROADMAP.md").exists()


def test_executive_runtime_program_spec_defines_control_objects_and_falsification() -> None:
    text = _read(EXECUTIVE_RUNTIME_PROGRAM_SPEC_PATH)

    assert EXECUTIVE_RUNTIME_PROGRAM_SPEC_PATH.exists()
    assert "Program Claim" in text
    assert "Formal Control Objects" in text
    assert "`ForwardCommitment`" in text
    assert "`ExpectationRecord`" in text
    assert "`ExpectationLedger`" in text
    assert "`ResolutionDeficitState`" in text
    assert "`GoalDebtDrag`" in text
    assert "`ControlPressure`" in text
    assert "`InterventionDecision`" in text
    assert "negative_prediction_error" in text
    assert "control_pressure" in text
    assert "Control-Law Invariants" in text
    assert "Evaluation Suite" in text
    assert "Minimum Thresholds" in text
    assert "Falsification Tests" in text
    assert "Implementation Dependency Graph" in text
    assert "First Implementation Slice" in text
    assert "First Live Probe" in text
    assert "not \"Cortex can produce better warning messages.\"" in text
    assert "The first program proof is silent executive control." in text
    assert "Model-Visible Output Contract" in text
    assert "not an outside\n    person, plugin, or policy voice" in text
    assert "no internal Cortex labels" in text
    assert "same-thread resumed turns may use first-person self-check" in text
    assert "not optimized only to the fixture" in text


def test_executive_runtime_phase_5_readiness_names_evidence_gaps_before_live_probe() -> None:
    text = _read(EXECUTIVE_RUNTIME_PHASE_5_READINESS_PATH)

    assert EXECUTIVE_RUNTIME_PHASE_5_READINESS_PATH.exists()
    assert "Readiness Verdict" in text
    assert "Seam 5 can then\nopen against the probe design in Concern 5" in text
    assert "Same-event certification or blocker progress can pay older compatible debt" in text
    assert "blocked/waiting boundary can leave residual verification debt" in text
    assert "test_mixed_horizon_sequence_targets_current_certification_before_old_debt" in text
    assert "test_waiting_boundary_relieves_blocker_without_residual_current_debt" in text
    assert "Concern 1: Seams 1-4 Evidence Accounting" in text
    assert "Concern 2: Horizon Classification Accuracy" in text
    assert "Concern 3: Integration Effects Across The Stack" in text
    assert "Concern 4: Cross-Operator State Observability" in text
    assert "Concern 5: Seam-5 Probe Design Appendix" in text
    assert "Concern 6: Strange-Loop Frame Across Silent Control" in text
    assert "Concern 7: Bridge From Silent Control To Grounded Intervention Records" in text
    assert "tests/conformance/test_phase5_readiness_scenarios.py" in text
    assert "No runtime-code change is required" in text
    assert "Remediation Closed Before Seam 5" in text
    assert "shipping truth" in text


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
        "task_standard_spine",
    }
    assert keystones <= seen_ids

    task_standard = next(
        entry for entry in math_map if entry["id"] == "task_standard_spine"
    )
    assert task_standard["packet_ref"] == "SRE_2 §8.2"
    assert task_standard["code_refs"] == ["cortex/sre/task_standard.py"]
    assert "tests/product/test_sre_task_standard_spine.py" in task_standard[
        "proof_refs"
    ]
    assert (
        "tests/product/test_openai_codex_app_cli_hook_coordinator.py"
        in task_standard["proof_refs"]
    )


def test_v2_model_io_analysis_is_two_sided_and_synthesized() -> None:
    status = _load_status()
    audit = status["v2_model_io_analysis"]

    assert "structural evidence only" in audit["source_note"]
    assert "https://developers.openai.com/codex/hooks" in audit["source_note"]
    lifecycle = {entry["id"]: entry for entry in audit["lifecycle_adapters"]}
    assert {"claude_code", "codex_app"} <= set(lifecycle)
    assert "transcript_path" in lifecycle["claude_code"]["lifecycle_input"]
    assert "last_assistant_message" in lifecycle["codex_app"]["lifecycle_input"]
    assert "[features].codex_hooks = false" in lifecycle["codex_app"]["lifecycle_input"]
    assert "explicit `grid-validate` fallback" in lifecycle["codex_app"]["lifecycle_input"]
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
    mission_reflection = _read(MISSION_REFLECTION_CONTRACT_PATH)

    assert "docs/CORTEX_STATUS.md" in readme
    assert "OpenAI product runtime on the CLI lane, with the direct service kept as a non-default backup surface" in readme
    assert "docs/CORTEX.md" in readme
    assert "Current Status" in docs_index
    assert "CORTEX_EXECUTIVE_RUNTIME_TRACKER.md" in docs_index
    assert "CORTEX_EXECUTIVE_RUNTIME_ROADMAP.md" not in docs_index
    assert "CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md" in docs_index
    assert "CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md" in docs_index
    assert "archive/" in docs_index
    assert "CORTEX.md" in docs_index
    assert "internal/MISSION_REFLECTION_CONTRACT.md" in docs_index
    assert "internal/ANTI_DRIFT_RULES.md" in docs_index
    assert "cortex_plugin/DESIGN.md" in docs_index
    assert "cortex_plugin/ADAPTER.md" in docs_index
    assert "cortex_plugin/EVIDENCE_SYNTHESIS.md" in docs_index
    assert "cortex_plugin/communication_problem/01_problem_statement.md" in docs_index
    assert "runtime_context/EVAL_RUBRIC.md" in docs_index
    assert "runtime_context/BASELINE_SHAPED_EXAMPLES.md" in docs_index
    assert "runtime_context/CROSS_HOST_SKETCH.md" in docs_index
    assert "recon/lifecycle_first_surface_matrix.md" in docs_index
    assert "recon/codex_app_hook_probe.md" in docs_index
    assert "recon/claude_code_desktop_pretooluse_probe.md" in docs_index
    assert "recon/claude_code_user_scope_plugin_pretooluse_probe.md" in docs_index
    assert "recon/claude_code_user_scope_plugin_managed_worktree_probe.md" in docs_index
    assert "recon/claude_code_cortex_runtime_context_connectivity_probe.md" in docs_index
    assert "recon/claude_code_cortex_stop_closure_connectivity_probe.md" in docs_index
    assert "recon/claude_code_cortex_headless_cli_equivalence_probe.md" in docs_index
    assert "recon/claude_code_cortex_bridge_translation_headless_probe.md" in docs_index
    assert "recon/claude_code_cortex_mac_pending_goal_divergence_retest.md" in docs_index
    assert "recon/claude_code_cortex_posttool_failure_to_stop_loop_probe.md" in docs_index
    assert "recon/claude_code_cortex_userpromptsubmit_verified_work_probe.md" in docs_index
    assert "recon/cortex_openai_operator_silent_control_live_probe.md" in docs_index
    assert "recon/cortex_openai_operator_debt_control_enactment.md" in docs_index
    assert "recon/cortex_openai_operator_silent_control_live_probe_retry.md" in docs_index
    assert "recon/cortex_openai_operator_output_quality_fixture_refresh.md" in docs_index
    assert "recon/cortex_openai_operator_verification_debt_continuation.md" in docs_index
    assert "recon/cortex_openai_operator_visible_intervention_live_probe.md" in docs_index
    assert "recon/cortex_visible_intervention_product_perception_hardening.md" in docs_index
    assert "recon/cortex_openai_operator_visible_intervention_hardened_rerun.md" in docs_index
    assert "recon/cortex_semantic_contraction_audit.md" in docs_index
    # CORTEX.md content anchors the previously-fragmented charter and
    # boundary identity material in one canonical surface.
    assert "executive-function layer that wraps a model after" in cortex_doc
    assert "docs/CORTEX_EXECUTIVE_RUNTIME_TRACKER.md" in cortex_doc
    assert "internal/truth/cortex_status.json" in cortex_doc
    assert "docs/cortex_plugin/DESIGN.md" in cortex_doc
    assert "docs/cortex_plugin/ADAPTER.md" in cortex_doc
    assert "docs/cortex_plugin/EVIDENCE_SYNTHESIS.md" in cortex_doc
    assert "docs/runtime_context/" in cortex_doc
    assert "docs/recon/lifecycle_first_surface_matrix.md" in cortex_doc
    assert "docs/recon/codex_app_hook_probe.md" in cortex_doc
    assert "docs/recon/claude_code_desktop_pretooluse_probe.md" in cortex_doc
    assert "docs/recon/claude_code_user_scope_plugin_pretooluse_probe.md" in cortex_doc
    assert "docs/recon/claude_code_user_scope_plugin_managed_worktree_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_runtime_context_connectivity_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_stop_closure_connectivity_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_headless_cli_equivalence_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_bridge_translation_headless_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_mac_pending_goal_divergence_retest.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_posttool_failure_to_stop_loop_probe.md" in cortex_doc
    assert "docs/recon/claude_code_cortex_userpromptsubmit_verified_work_probe.md" in cortex_doc
    assert "docs/recon/cortex_openai_operator_silent_control_live_probe.md" in cortex_doc
    assert "docs/recon/cortex_openai_operator_debt_control_enactment.md" in cortex_doc
    assert "docs/recon/cortex_openai_operator_output_quality_fixture_refresh.md" in cortex_doc
    assert "EVAL_RUBRIC.md" in cortex_doc
    assert "BASELINE_SHAPED_EXAMPLES.md" in cortex_doc
    assert "CROSS_HOST_SKETCH.md" in cortex_doc
    assert "lifecycle-first surface reconnaissance" in cortex_doc.lower()
    assert "Root Codex App Stop enforcement is disabled" in cortex_doc
    assert "PreToolUse` fired for Bash" in cortex_doc
    assert "user-scope plugin" in cortex_doc
    assert "Gate 1 failed" in cortex_doc
    assert "Stop x closure pressure" in cortex_doc
    assert "headless CLI equivalence" in cortex_doc
    assert "Mission Reflection grid out of product packaging" in cortex_doc
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
    assert "fixed dashboard rows such as `Progress:*`" in mission_reflection
    assert "codex-app-hook-health" in workflow
    assert ".codex/hooks/cortex_mission_reflection_stop_hook.py" in workflow
    assert "last_assistant_message" in workflow
    assert "[features].codex_hooks = false" in workflow
    assert "disabled by repo policy" in workflow
    assert "structural workflow" in workflow
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


def test_document_role_map_covers_docs_without_turning_context_into_roadmap() -> None:
    status = _load_status()
    role_map = status["doc_roles"]
    roles = role_map["roles"]
    role_paths: dict[str, set[str]] = {
        role["id"]: set(role["paths"])
        for role in roles
    }
    all_role_paths = [path for role in roles for path in role["paths"]]

    assert "status registry remains the operational roadmap authority" in role_map["summary"]
    assert len(all_role_paths) == len(set(all_role_paths))
    assert set(all_role_paths) == set(status["active_docs"])

    assert role_paths["identity_authority"] == {"docs/CORTEX.md"}
    assert role_paths["generated_operational_view"] == {"docs/CORTEX_STATUS.md"}
    assert role_paths["planning_scoreboard"] == {"docs/CORTEX_EXECUTIVE_RUNTIME_TRACKER.md"}
    assert "docs/CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md" in role_paths["retained_context"]
    assert "docs/CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md" in role_paths["retained_context"]
    assert "docs/CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md" not in role_paths["planning_scoreboard"]
    assert "docs/CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md" not in role_paths["identity_authority"]
    assert "docs/internal/REPO_WORKFLOW.md" in role_paths["workflow_authority"]
    assert "docs/recon/cortex_codex_app_cli_task_standard_live_run.md" in role_paths["recon_evidence"]
    assert "docs/recon/cortex_semantic_contraction_audit.md" in role_paths["recon_evidence"]

    readme = _read(DOCS_INDEX_PATH)
    status_doc = _read(STATUS_DOC_PATH)
    assert "Document roles are machine-readable" in readme
    assert "not current roadmap authority" in readme.replace("\n  ", " ")
    assert "## Document Authority Map" in status_doc
    assert "`retained_context`" in status_doc
    assert "Do not queue work from these docs directly" in status_doc
    assert "## Active Docs Inventory" in status_doc
    assert "Authority comes from the Document Authority Map" in status_doc


def test_anti_drift_rules_pin_fixture_to_law_product_spine() -> None:
    text = _read(ANTI_DRIFT_RULES_PATH)

    assert "## Fixture-To-Law Product Spine" in text
    assert "fixtures falsify Cortex; they do not define Cortex" in text
    assert "Product seams\ntouching `cortex/**`" in text
    assert "Product Cortex may use task details as grounded anchors" in text
    assert "but never as product\ntriggers" in text
    assert "Text classes stay separate" in text
    assert "Human prompts are ordinary task requests" in text
    assert "Lab prompt\nscaffolds are test apparatus" in text


def test_anti_drift_rules_pin_host_surface_taxonomy() -> None:
    text = _read(ANTI_DRIFT_RULES_PATH)

    assert "## Host Surface Taxonomy" in text
    assert "Product Host\nAdaptors, API / Conformance Adaptors, and Non-Adaptor Support Surfaces" in text
    assert "one `openai.codex_app_cli` product adaptor family" in text
    assert "Codex App Stop-hook proof" in text
    assert "Codex CLI `codex exec` wrapper/resume proof" in text
    assert "repo Mission Reflection hooks" in text
    assert "Unqualified `operator_cli` must not appear as the active shipping" in text


def test_active_truth_surfaces_do_not_use_old_openai_operator_cli_label() -> None:
    status = _load_status()
    active_docs = [
        REPO_ROOT / doc
        for doc in status["active_docs"]
        if not doc.startswith("docs/archive/")
    ]

    for path in [STATUS_REGISTRY_PATH, *active_docs]:
        text = _read(path)
        assert "openai:operator_cli" not in text, str(path)


def test_docs_directory_only_exposes_archive_and_workflow_subtrees() -> None:
    subdirs = sorted(path.name for path in DOCS_ROOT.iterdir() if path.is_dir())

    assert subdirs == [
        "archive",
        "audit",
        "cortex_plugin",
        "internal",
        "recon",
        "runtime_context",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "audit").iterdir()) == [
        "runtime_context_vs_grounded_intervention.md",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "cortex_plugin").iterdir()) == [
        "ADAPTER.md",
        "DESIGN.md",
        "EVIDENCE_SYNTHESIS.md",
        "communication_problem",
    ]
    assert sorted(path.name for path in COMMUNICATION_PROBLEM_DIR.iterdir()) == [
        "01_problem_statement.md",
        "02_cortex_identity_and_doctrine.md",
        "03_maths_to_code.md",
        "04_cortex_internal_state.md",
        "05_claude_communication_surface.md",
        "06_hook_surface_and_evidence.md",
        "07_strange_loop_frame.md",
        "08_anti_patterns_and_failed_solutions.md",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "internal").iterdir()) == [
        "ANTI_DRIFT_RULES.md",
        "MISSION_REFLECTION_CONTRACT.md",
        "REPO_WORKFLOW.md",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "recon").iterdir()) == [
        "claude_code_cortex_bridge_translation_headless_probe.md",
        "claude_code_cortex_headless_cli_equivalence_probe.md",
        "claude_code_cortex_mac_pending_goal_divergence_retest.md",
        "claude_code_cortex_posttool_failure_to_stop_loop_probe.md",
        "claude_code_cortex_runtime_context_connectivity_probe.md",
        "claude_code_cortex_stop_closure_connectivity_probe.md",
        "claude_code_cortex_userpromptsubmit_verified_work_probe.md",
        "claude_code_desktop_lifecycle_spine_branch_disposition.md",
        "claude_code_desktop_pretooluse_probe.md",
        "claude_code_user_scope_plugin_managed_worktree_probe.md",
        "claude_code_user_scope_plugin_pretooluse_probe.md",
        "codex_app_hook_probe.md",
        "cortex_codex_app_cli_astro_three_arm_fixture_refresh.md",
        "cortex_codex_app_cli_communication_boundary_audit_and_hardening.md",
        "cortex_codex_app_cli_hook_contract_capture_boundary_remediation.md",
        "cortex_codex_app_cli_hook_native_behavior_comparison.md",
        "cortex_codex_app_cli_hook_native_stop_activation_probe.md",
        "cortex_codex_app_cli_hook_native_stop_live_canary.md",
            "cortex_codex_app_cli_lifecycle_actuator_map.md",
            "cortex_codex_app_cli_lifecycle_actuator_map_roadmap_update.md",
            "cortex_codex_app_cli_posttooluse_causal_trace_ids.md",
            "cortex_codex_app_cli_posttooluse_task_standard_actuator_architecture_decision.md",
        "cortex_codex_app_cli_posttooluse_task_standard_actuator_trace_repair.md",
        "cortex_codex_app_cli_posttooluse_task_standard_calibration_decision.md",
        "cortex_codex_app_cli_posttooluse_task_standard_firing_boundary_remediation.md",
        "cortex_codex_app_cli_posttooluse_task_standard_narrow_live_probe.md",
        "cortex_codex_app_cli_posttooluse_task_standard_narrow_live_run.md",
        "cortex_codex_app_cli_posttooluse_task_standard_next_step_correction.md",
        "cortex_codex_app_cli_posttooluse_task_standard_overcontrol_remediation.md",
        "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_calibration_gate0.md",
        "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun.md",
        "cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_run.md",
        "cortex_codex_app_cli_product_event_capture_remediation.md",
        "cortex_codex_app_cli_product_perception_live_probe.md",
        "cortex_codex_app_cli_product_perception_loop.md",
        "cortex_codex_app_cli_raw_vs_silent_artifact_readout_roadmap_update.md",
        "cortex_codex_app_cli_stop_continuation_resolution_loop.md",
        "cortex_codex_app_cli_task_standard_behavior_comparison_harness.md",
        "cortex_codex_app_cli_task_standard_behavior_comparison_live_run.md",
        "cortex_codex_app_cli_task_standard_context_live_rerun.md",
        "cortex_codex_app_cli_task_standard_evidence_gating_remediation.md",
        "cortex_codex_app_cli_task_standard_live_capture_rerun.md",
        "cortex_codex_app_cli_task_standard_live_probe.md",
        "cortex_codex_app_cli_task_standard_live_run.md",
        "cortex_codex_app_cli_task_standard_offline_replay_readiness_gate.md",
        "cortex_codex_app_cli_task_standard_pre_live_audit_roadmap_update.md",
        "cortex_codex_app_cli_task_standard_pretool_transcript_capture.md",
        "cortex_codex_app_cli_task_standard_raw_vs_silent_artifact_readout.md",
        "cortex_codex_app_cli_task_standard_spine.md",
        "cortex_codex_app_cli_task_standard_stack_publication_hygiene.md",
        "cortex_codex_app_cli_task_standard_stop_gating_calibration_probe.md",
        "cortex_codex_app_cli_task_standard_stop_gating_live_run.md",
        "cortex_codex_app_cli_value_ablation_audit.md",
        "cortex_openai_operator_debt_control_enactment.md",
        "cortex_openai_operator_output_quality_fixture_refresh.md",
        "cortex_openai_operator_silent_control_live_probe.md",
        "cortex_openai_operator_silent_control_live_probe_retry.md",
        "cortex_openai_operator_verification_debt_continuation.md",
            "cortex_openai_operator_visible_intervention_hardened_rerun.md",
            "cortex_openai_operator_visible_intervention_live_probe.md",
            "cortex_semantic_contraction_audit.md",
            "cortex_task_standard_executive_doctrine_math_refinement.md",
            "cortex_task_standard_sre_correspondence_reconciliation.md",
            "cortex_visible_intervention_product_perception_hardening.md",
            "lifecycle_first_surface_matrix.md",
    ]
    assert sorted(path.name for path in (DOCS_ROOT / "runtime_context").iterdir()) == [
        "BASELINE_SHAPED_EXAMPLES.md",
        "CROSS_HOST_SKETCH.md",
        "EVAL_RUBRIC.md",
    ]


def test_communication_problem_dossier_is_self_contained_and_problem_framed() -> None:
    texts = [path.read_text(encoding="utf-8") for path in COMMUNICATION_PROBLEM_FILES]
    combined = "\n".join(texts)

    for path in COMMUNICATION_PROBLEM_FILES:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip(), path

    problem = texts[0]
    assert "τ : S × H × C -> M" in problem
    assert "strange-loop" in problem.lower()
    assert "not a real translation function" in problem
    assert "arbitrary Cortex states" in problem
    assert "more hardcoded templates" in problem
    assert "The thinking model may keep the lattice" in combined

    identity = texts[1]
    assert "Eight Failure Modes" in identity
    assert "Four Truth Distinctions" in identity
    assert "Connectivity Requirement" in identity
    assert "Lifecycle-First Runtime Law" in identity

    maths = texts[2]
    assert "math_to_code_map" in maths
    assert "side_a_internal_logic" in maths
    assert "side_b_model_visible_translation" in maths
    assert "host_control_transports" in maths

    internal_state = texts[3]
    for ref in [
        "cortex/core/envelopes.py",
        "cortex/core/observation.py",
        "cortex/core/dispatch.py",
        "cortex/sre/feedback.py",
        "cortex/sre/brake.py",
        "cortex/sre/goal_debt.py",
        "cortex/sre/operator_routing.py",
        "cortex/aux/publication.py",
        "cortex/runtime/verified_work_runtime.py",
    ]:
        assert f"### `{ref}`" in internal_state

    claude_surface = texts[4]
    for ref in [
        "cortex/hosts/_executive_closure.py",
        "cortex/hosts/runtime_context.py",
        "cortex/hosts/claude/runtime.py",
        "cortex/hosts/claude/host_control.py",
        "cortex/hosts/claude/ingress.py",
        "cortex/hosts/claude/session_io.py",
        "cortex/hosts/claude_code_desktop/ingress.py",
        "cortex/hosts/claude_code_desktop/runtime.py",
        "cortex/hosts/claude_code_desktop/hook_control.py",
        "cortex/hosts/claude_code_desktop/model_facing.py",
    ]:
        assert ref in claude_surface
    assert "not a general `τ`" in claude_surface

    evidence = texts[5]
    assert "additionalContext" in evidence
    assert "systemMessage" in evidence
    assert "stop_hook_active" in evidence
    assert "Prior Architectural Organization" in evidence
    assert "content shape may dominate hook placement" in evidence
    assert "Headless translated Stop harness" in evidence
    assert "not a general `τ`" in evidence

    strange_loop = texts[6]
    assert "Hofstadter" in strange_loop
    assert "Gödel" in strange_loop
    assert "Metacognition" in strange_loop
    assert "Integrated Versus Alien Content" in strange_loop
    assert "This dossier does not commit" in strange_loop

    anti_patterns = texts[7]
    for phrase in [
        "Framework Signatures",
        "Schema IDs",
        "Generic Principles",
        "Internal Tag Names",
        "Hardcoded Templates",
        "Hook Content Competing With User Exact-Output Instructions",
        "Confused Authority",
        "integration failures",
    ]:
        assert phrase in anti_patterns

    assert "OpenAIHostControlRequest" not in internal_state
    assert "GeminiHostControlRequest" not in internal_state
    assert "Mission Reflection" not in problem


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


def test_claude_code_desktop_pretooluse_probe_records_empirical_findings_and_cleanup() -> None:
    text = _read(CLAUDE_CODE_DESKTOP_PRETOOLUSE_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Claude Code Desktop Code tab" in text
    assert "1.5354.0" in text
    assert "2.1.121" in text
    assert "claude-opus-4-7" in text
    assert "CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30" in text

    for phrase in [
        "Q1: Does Claude Code Desktop load a project-level `.claude/settings.json` with a `PreToolUse` hook?",
        "Q2: Does the `PreToolUse` hook fire, and what input shape does it receive?",
        "Q3: Does `hookSpecificOutput.additionalContext` reach the model?",
        "**Partial**",
        "**Confirmed**",
        "managed worktree",
        "Trust persistence after closing and reopening the subject thread was not tested",
        "Exact Temporary Settings",
        "Exact Temporary Hook Script",
        "Raw Hook Input",
        "Field Enumeration",
        "No undocumented top-level fields were observed",
        "Actual Post-Tool Assistant Output",
        "hook_additional_context",
        "Cleanup Verification",
        "Root `.claude/settings.json` restored",
        "Temporary `.claude/hooks/claude_code_desktop_pretooluse_probe.py` removed",
        "does not generalize to Claude Code CLI",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "tool_name",
        "tool_input",
        "tool_use_id",
    ]:
        assert f"`{key}`" in text


def test_claude_code_user_scope_plugin_pretooluse_probe_records_findings_and_caveats() -> None:
    text = _read(CLAUDE_CODE_USER_SCOPE_PLUGIN_PRETOOLUSE_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Claude Code Desktop Code tab" in text
    assert "user-scope plugin" in text
    assert "cortex-user-scope-hook-probe" in text
    assert "CORTEX_USER_PLUGIN_SENTINEL_2026_04_30" in text
    assert "1.5354.0" in text

    for phrase in [
        "Q1: Do user-scope plugins reach Claude Code Desktop's Code tab?",
        "Q2: Can `PreToolUse` and `Stop` hooks coexist within one user-scope plugin?",
        "Q3: Is `PreToolUse` injection powerful enough to require strict content discipline?",
        "**Confirmed**",
        "Precision caveat",
        "did not specifically verify firing inside a `.claude/worktrees/...` managed worktree path",
        "PreToolUse:Bash",
        "`Stop` events",
        "Operational Consideration: Injection Discipline",
        "interaction loop",
        "plugin-design constraint, not evidence against the plugin approach",
        "Evidence Files",
        "/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/pretool_raw.jsonl",
        "/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/stop_raw.jsonl",
        "/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/summary.jsonl",
        "Raw Hook Input",
        "Field Enumeration",
        "No undocumented top-level fields were observed",
        "Actual Assistant Output",
        "Cleanup Verification",
        "does not prove user-scope plugin behavior inside a",
        "product Cortex model-output lift",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "tool_name",
        "tool_input",
        "tool_use_id",
        "stop_hook_active",
        "last_assistant_message",
    ]:
        assert f"`{key}`" in text


def test_claude_code_user_scope_plugin_managed_worktree_probe_records_cwd_finding() -> None:
    text = _read(CLAUDE_CODE_USER_SCOPE_PLUGIN_MANAGED_WORKTREE_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Claude Code Desktop Code tab" in text
    assert "cortex-user-scope-worktree-probe" in text
    assert "CORTEX_WORKTREE_PROBE_SENTINEL_2026_05_01" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "1.5354.0" in text
    assert "2.1.121" in text

    for phrase in [
        "Q1: Does the user-scope plugin fire in the sandbox Code-tab subject?",
        "Q2: What `cwd` did the hook receive?",
        "Q3: Does this prove user-scope plugin behavior inside a managed-worktree path?",
        "**Confirmed**",
        "**Confirmed: sandbox root**",
        "**Negative for that exact condition**",
        "This run did not observe a `.claude/worktrees/...` path",
        "no repo-local `.claude/settings.json`",
        "Evidence Files",
        "/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline/pretool_raw.jsonl",
        "/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline/summary.jsonl",
        "Raw Hook Input",
        "Field Enumeration",
        "No undocumented top-level fields were observed",
        "Actual Assistant Output",
        "hook_additional_context",
        "Cleanup Verification",
        "does not prove behavior for a future Code-tab session whose effective `cwd` is actually a managed worktree",
        "product Cortex model-output lift",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "tool_name",
        "tool_input",
        "tool_use_id",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_runtime_context_connectivity_probe_records_gate_failure() -> None:
    text = _read(CLAUDE_CODE_CORTEX_RUNTIME_CONTEXT_CONNECTIVITY_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Claude Code Desktop Code tab" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "1.5354.0" in text
    assert "2.1.121" in text
    assert "claude-opus-4-7" in text
    assert "codex/20260430-155752-claude-code-desktop-lifecycle-spine" in text

    for phrase in [
        "Pre-flight A: session identity and persistence reality",
        "Pre-flight B: Stop block mechanism",
        "Gate 1: merged `PreToolUse:Bash` runtime-context foundation",
        "**Fail**",
        "Gate 2: PostToolUse feedback to next PreToolUse",
        "**Not tested**",
        "CORTEX_RUNTIME_CONTEXT_V1",
        "hook_additional_context",
        "TEST_BLOCK_REASON_2026_05_01",
        "session-id-plus-cwd keying is thread-local",
        "one shaped win, one no-change, one shaped regression, and one neutral",
        "blocks the lifecycle-spine branch from merge",
        "No sentinel or acknowledgement instruction was inserted into the Cortex runtime context",
        "Raw Hook Input Examples",
        "Field Enumeration",
        "Cleanup Verification",
        "claude plugin list --json` no longer lists",
        "Product-lift truth: not earned",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "tool_name",
        "tool_input",
        "tool_use_id",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_stop_closure_connectivity_probe_records_stop_findings() -> None:
    text = _read(CLAUDE_CODE_CORTEX_STOP_CLOSURE_CONNECTIVITY_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-04-30" in text
    assert "Claude Code Desktop Code tab" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "1.5354.0" in text
    assert "2.1.121" in text
    assert "codex/20260430-155752-claude-code-desktop-lifecycle-spine" in text

    for phrase in [
        "Stop x closure pressure",
        "Pass with content-shape caveat",
        "manual subset confirmed",
        "Manual Recalibration After Accessibility Confound",
        "two non-clean paired Stop trials",
        "entered manually by the user",
        "cortex-manual-stop-recalibration-inline",
        "closure_reason_tags",
        "Stop hook feedback:",
        "hook_blocking_error",
        "Cortex blocked closure: continuity_reminder, pending_goal_debt",
        "Cortex blocked closure: continuity_rejection, contradiction_spike, degradation_pressure",
        "Clean closure control",
        "Over-block risk control",
        "The H x F lattice remains the architecture",
        "does not make `Stop` the primary Cortex architecture",
        "Exact Temporary Plugin Shape",
        "The exact hook script used was",
        "Raw Hook Input And Output Examples",
        "Field Enumeration",
        "Trial Matrix And Scores",
        "Cleanup Verification",
        "claude plugin list --json` no longer lists",
        "cortex-manual-recalibration-probes",
        "This probe does not claim a Stop-primary plugin architecture",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_headless_cli_equivalence_probe_records_partial_finding() -> None:
    text = _read(CLAUDE_CODE_CORTEX_HEADLESS_CLI_EQUIVALENCE_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-05-01" in text
    assert "`claude -p`" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "2.1.85" in text
    assert "2.1.118 (Claude Code)" in text
    assert "subscriptionType" in text and "max" in text
    assert "sdk-cli" in text
    assert "claude-opus-4-7" in text

    for phrase in [
        "Setup/auth readiness",
        "Repaired before scoring",
        "Stop structural floor in `claude -p`",
        "Model-visible block delivery",
        "Once-only safety wrapper",
        "Clean no-over-block control",
        "Partial / cross-surface variance",
        "Operational unlock",
        "Qualified",
        "cortex-headless-cli-equivalence-probe",
        "cortex-headless-equivalence-probes",
        "Stop hook feedback:",
        "hook_blocking_error",
        "permissionDecision: deny",
        "continuity_reminder",
        "pending_goal_debt",
        "continuity_rejection",
        "contradiction_spike",
        "degradation_pressure",
        "MIGRATION COMPLETE",
        "TESTS PROVEN GREEN",
        "CLEAN DONE",
        "headless baseline already rejected the false closure",
        "equivalence is one of two",
        "failure scenarios",
        "This finding is per-bridge and per-content family",
        "does not make `Stop` the primary Cortex architecture",
        "does not promote Claude Code",
        "Shipping default remains `openai.codex_app_cli`",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_bridge_translation_headless_probe_records_preserved_evidence() -> None:
    text = _read(CLAUDE_CODE_CORTEX_BRIDGE_TRANSLATION_HEADLESS_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-05-01" in text
    assert "`claude -p`" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "Preservation note" in text
    assert "renderer-first" in text and "implementation is superseded" in text

    for phrase in [
        "translated evidence-degradation Stop repaired 3/3 scored headless",
        "Baseline false closure reproduced 3/3",
        "Pending-goal behavior lift",
        "Unscored / cross-surface variance",
        "Global user hooks contaminate probe behavior",
        "Plugin layout is part of hook truth",
        "evidence-degradation translated Stop text requires the last assistant",
        "No translated Stop text is emitted when the assistant has already refused",
        "does not make `Stop` the primary Cortex architecture",
        "promote Claude Code or headless CLI to shipping default",
        "does not validate",
        "Product / shipping truth",
        "Shipping truth remains `openai.codex_app_cli`",
        "no broad headless equivalence claim",
        "clean no-over-block passes",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_mac_pending_goal_divergence_retest_records_content_shape_failure() -> None:
    text = _read(CLAUDE_CODE_CORTEX_MAC_PENDING_GOAL_DIVERGENCE_RETEST_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-05-01" in text
    assert "Claude Code Desktop Code tab" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "2.1.121" in text
    assert "claude-opus-4-7" in text

    for phrase in [
        "Mac Pending-Goal Divergence Retest",
        "raw internal Cortex wording",
        "Mixed / content-shape contaminated",
        "baseline Mac false closure",
        "Shaped Mac repair",
        "Shaped Mac content-shape failure",
        "hook-skepticism/prompt-injection-shaped",
        "Once-only safety wrapper",
        "Stop hook feedback:",
        "hook_blocking_error",
        "Cortex blocked closure: continuity_reminder, pending_goal_debt",
        "MIGRATION COMPLETE",
        "mode.txt=baseline",
        "trial.txt=paused",
        "run_id.txt=paused_safe_noop",
        "model-facing translation boundary",
        "does not make `Stop` the primary Cortex architecture",
        "does not promote Claude Code Desktop",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_posttool_failure_to_stop_loop_probe_records_mixed_finding() -> None:
    text = _read(CLAUDE_CODE_CORTEX_POSTTOOL_FAILURE_TO_STOP_LOOP_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-05-01" in text
    assert "Claude Code Desktop Code tab" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "2.1.121" in text
    assert "claude-opus-4-7" in text

    for phrase in [
        "PostToolUseFailure-to-Stop lifecycle-loop",
        "`PostToolUseFailure:Bash` delivery",
        "Feedback persistence into later Stop",
        "Stop block delivery",
        "Once-only Stop safety wrapper",
        "Clean no-over-block control",
        "Partial / mixed",
        "Baselines falsely closed 3/3",
        "Shaped trials repaired 2/3 and failed 1/3",
        "PostToolUse:Bash",
        "python3 missing.py",
        "python3 -c \"print('OK')\"",
        "TASK COMPLETE",
        "Stop hook feedback:",
        "hook_blocking_error",
        "continuity_rejection",
        "contradiction_spike",
        "degradation_pressure",
        "This probe does not make `Stop`",
        "does not promote Claude Code",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "tool_name",
        "tool_input",
        "tool_use_id",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_claude_code_cortex_userpromptsubmit_verified_work_probe_records_negative_finding() -> None:
    text = _read(CLAUDE_CODE_CORTEX_USERPROMPTSUBMIT_VERIFIED_WORK_PROBE_PATH)

    assert "Surface: internal / recon" in text
    assert "Probe date: 2026-05-01" in text
    assert "Claude Code Desktop Code tab" in text
    assert "/Users/erikahoward/cortex-plugin-sandbox" in text
    assert "1.5354.0" in text
    assert "2.1.121" in text
    assert "claude-opus-4-7" in text

    for phrase in [
        "UserPromptSubmit",
        "verified-work",
        "Hook delivery truth",
        "Model-visible delivery truth",
        "Behavior-lift truth",
        "Failed for this content shape",
        "Clean-control truth",
        "hook_system_message",
        "PostToolUseFailure",
        "PostToolUse:Bash",
        "python3 missing.py",
        "python3 -c \"print('OK')\"",
        "TASK COMPLETE",
        "2-of-3 pass threshold unreachable",
        "Claude Code Desktop is not promoted to default product behavior",
        "Codex did not drive the GUI",
        "does not claim product lift",
        "does not collapse the H x F lifecycle lattice",
    ]:
        assert phrase in text

    for key in [
        "session_id",
        "transcript_path",
        "cwd",
        "permission_mode",
        "hook_event_name",
        "prompt",
        "tool_name",
        "tool_input",
        "tool_response",
        "error",
        "last_assistant_message",
        "stop_hook_active",
    ]:
        assert f"`{key}`" in text


def test_openai_operator_silent_control_probe_records_gate0_coupling_gap() -> None:
    text = _read(OPENAI_OPERATOR_SILENT_CONTROL_LIVE_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / recon" in text
    assert "Probe date: 2026-05-02" in text
    assert "Gate 0 failed" in text
    assert "live OpenAI Codex App/CLI wrapper-resume trials were not run" in text
    assert "runtime debt control changes OpenAI route/policy diagnostics" in text
    assert "current Codex operator live adapter does not enact" in text
    assert "model_bound_debt_enactment_present == false" in text
    assert "runtime_control_delta_present == true" in text
    assert "CORTEX_LIVE_SERVICE_SPEND_APPROVED" in text
    assert "openai-operator-debt-control-enactment" in text
    assert "No behavior-lift claim" in text
    assert "No shipping promotion" in text
    assert "recon/cortex_openai_operator_silent_control_live_probe.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_silent_control_live_probe.md"
        in status["active_docs"]
    )


def test_openai_operator_debt_control_enactment_records_gate0_remediation() -> None:
    text = _read(OPENAI_OPERATOR_DEBT_CONTROL_ENACTMENT_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / host-adapter recon" in text
    assert "Probe date: 2026-05-02" in text
    assert "Gate 0 now passes structurally" in text
    assert "cortex/hosts/openai/operator_enactment.py" in text
    assert "`invoke`" in text
    assert "`block`" in text
    assert "`resume_recheck`" in text
    assert "truth_gap_recheck_operator.md" in text
    assert "runtime_control_delta_present == true" in text
    assert "model_bound_delta_present == true" in text
    assert "gate0_passed == true" in text
    assert "neutral condition action: `invoke`" in text
    assert "shaped condition action: `resume_recheck`" in text
    assert "initial prompt hashes match" in text
    assert "no live OpenAI behavior lift" in text
    assert "No API/service-spend approval" in text
    assert "silent-control-live-probe-on-openai-retry" in text
    assert "recon/cortex_openai_operator_debt_control_enactment.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_debt_control_enactment.md"
        in status["active_docs"]
    )


def test_openai_operator_silent_control_retry_records_baseline_non_reproduction() -> None:
    text = _read(OPENAI_OPERATOR_SILENT_CONTROL_LIVE_PROBE_RETRY_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live recon" in text
    assert "Probe date: 2026-05-02" in text
    assert "Gate 0 passed" in text
    assert "baseline_not_reproduced" in text
    assert "2026-05-02T163231Z0000" in text
    assert "failure_reproduced_count" in text
    assert "`unsupported_verification`" in text
    assert "`false_closure`" in text
    assert "`candidate_forward_commit`" in text
    assert "no live behavior-lift claim" in text
    assert "no paired shaped-trial result" in text
    assert "silent-control-live-fixture-refresh" in text
    assert "CORTEX_LIVE_SERVICE_SPEND_APPROVED" in text
    assert "gpt-5.3-codex" in text
    assert "recon/cortex_openai_operator_silent_control_live_probe_retry.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_silent_control_live_probe_retry.md"
        in status["active_docs"]
    )


def test_openai_operator_output_quality_fixture_refresh_records_hard_fixture() -> None:
    text = _read(OPENAI_OPERATOR_OUTPUT_QUALITY_FIXTURE_REFRESH_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live recon" in text
    assert "Probe date: 2026-05-02" in text
    assert "astro_docs_site_v1" in text
    assert "run_20260502T165319+0000" in text
    assert "run_20260502T165814+0000" in text
    assert "run_20260502T170004+0000" in text
    assert "run_20260502T170702+0000" in text
    assert "docs search dataset marker is missing" in text
    assert "3/3 clean baseline reproduction" in text
    assert "output-quality evidence, not silent-control evidence" in text
    assert "no silent-control behavior lift" in text
    assert "silent-control-output-quality-enactment" in text
    assert "isolated Git repository" in text
    assert "test_output_quality_operator_workspace_gets_isolated_git_root" in text
    assert "recon/cortex_openai_operator_output_quality_fixture_refresh.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_output_quality_fixture_refresh.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"


def test_openai_operator_verification_debt_continuation_records_gate0_truth() -> None:
    text = _read(OPENAI_OPERATOR_VERIFICATION_DEBT_CONTINUATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live recon" in text
    assert "Probe date: 2026-05-02" in text
    assert "resume_verification" in text
    assert "visible_success_unverified" in text
    assert "verification_debt_continuation_operator.md" in text
    assert "same initial prompt hash" in text
    assert "non_astro_visible_success_unverified_control" in text
    assert "clean verified control stayed `invoke`" in text
    assert "baseline failure reproduced 5/5" in text
    assert "shaped arm improved all primary axes" in text.lower()
    assert "zero provider-limit failures" in text
    assert "Live behavior truth: Narrowly earned" in text
    assert "no shipping promotion" in text.lower()
    assert "recon/cortex_openai_operator_verification_debt_continuation.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_verification_debt_continuation.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_openai_operator_visible_intervention_live_probe_records_scoped_success() -> None:
    text = _read(OPENAI_OPERATOR_VISIBLE_INTERVENTION_LIVE_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab evidence" in text
    assert "Verdict: scoped success on `openai.codex_app_cli`" in text
    assert "Gate 0 passed" in text
    assert "product-rendered" in text
    assert "I have not verified the verification opened by this task yet" in text
    assert "Baseline gate | 3 | 3 | 0 | 0" in text
    assert "Silent-only | 5 | 5 | 0 | 0" in text
    assert "Visible intervention | 5 | 4 | 0 | 0" in text
    assert "Clean controls | 3 | 0 | 0 | 0" in text
    assert "fully repaired the hidden verifier in 1 of 5" in text
    assert "visible trials" in text
    assert "No Claude Code, Gemini, reference, AUX, hook, or cross-host" in text
    assert "recon/cortex_openai_operator_visible_intervention_live_probe.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_visible_intervention_live_probe.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_visible_intervention_product_perception_hardening_records_structural_gate() -> None:
    text = _read(VISIBLE_INTERVENTION_PRODUCT_PERCEPTION_HARDENING_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / structural recon" in text
    assert (
        "product event stream -> expectation ledger -> resolution deficit -> grounded anchor"
        in text
    )
    assert "missing_product_expectation_anchor" in text
    assert "Hidden verifier output remains scoring only" in text
    assert "due product-runtime expectation record" in text
    assert "same runtime state across Astro and non-Astro task identities" in text
    assert "No new live behavior-lift claim" in text
    assert "claude-code-adapter-from-runtime-law" in text
    assert "recon/cortex_visible_intervention_product_perception_hardening.md" in docs_index
    assert (
        "docs/recon/cortex_visible_intervention_product_perception_hardening.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_openai_operator_visible_intervention_hardened_rerun_records_failure() -> None:
    text = _read(OPENAI_OPERATOR_VISIBLE_INTERVENTION_HARDENED_RERUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live recon" in text
    assert "Probe date: 2026-05-03" in text
    assert "Gate 0 passed" in text
    assert "Baseline gate | 3 | 3 | 0 | 0" in text
    assert "Silent-only | 5 | 4 | 0 | 0" in text
    assert "Visible intervention | 5 | 5 | 0 | 0" in text
    assert "Clean controls | 3 | 0 | 0 | 0" in text
    assert "visible-verification-rendering-remediation" in text
    assert "weaker\nvisible-check or narrower-claim path" in text
    assert "No visible-intervention behavior-lift claim" in text
    assert "recon/cortex_openai_operator_visible_intervention_hardened_rerun.md" in docs_index
    assert (
        "docs/recon/cortex_openai_operator_visible_intervention_hardened_rerun.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_codex_app_cli_stop_activation_probe_records_structural_gate0() -> None:
    text = _read(CODEX_APP_CLI_STOP_ACTIVATION_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / structural activation proof" in text
    assert "Probe date: 2026-05-04" in text
    assert "simulated Codex Stop payload -> product hook client" in text
    assert ".cortex/live_validation/openai/codex_app_cli_stop_activation_probe/" in text
    assert "normal Stop with transcript-backed assistant turn returned exact block JSON" in text
    assert "title/null-transcript Stop stayed silent" in text
    assert "`stop_hook_active=true` continuation stayed silent" in text
    assert "missing snapshot and malformed input failed open" in text
    assert "No live Codex App or Codex CLI hook activation claim" in text
    assert "actuator stimulus, not evidence that Cortex detected a real task gap" in text
    assert "recon/cortex_codex_app_cli_hook_native_stop_activation_probe.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_hook_native_stop_activation_probe.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_codex_app_cli_stop_live_canary_records_actuator_proof() -> None:
    text = _read(CODEX_APP_CLI_STOP_LIVE_CANARY_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live actuator proof" in text
    assert "Probe date: 2026-05-04" in text
    assert "real Codex Stop payload -> product hook client" in text
    assert "CORTEX_CODEX_APP_CLI_STOP_ACTIVATION_APPROVED=approved" in text
    assert "hook rows: `3`" in text
    assert "block rows: `1`" in text
    assert "continuation rows with `stop_hook_active=true`: `2`" in text
    assert "a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc" in text
    assert "No product perception claim" in text
    assert "No model-output behavior-lift claim" in text
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    assert "recon/cortex_codex_app_cli_hook_native_stop_live_canary.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_hook_native_stop_live_canary.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"


def test_codex_app_cli_product_perception_loop_records_structural_gate0() -> None:
    text = _read(CODEX_APP_CLI_PRODUCT_PERCEPTION_LOOP_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / structural hook perception proof" in text
    assert "Probe date: 2026-05-04" in text
    assert "UserPromptSubmit / tool / Stop payloads" in text
    assert "ExpectationLedger + resolution deficit" in text
    assert "no runtime snapshot fixture" in text.lower()
    assert "prompt/tool/Stop simulated Codex payloads" in text
    assert "Structural product perception" in text
    assert "No live proof" in text
    assert "No hidden-verifier, lab-oracle, task-identity" in text
    assert "Run a narrow hook-native product-perception live probe" in text
    assert "recon/cortex_codex_app_cli_product_perception_loop.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_product_perception_loop.md"
        in status["active_docs"]
    )


def test_codex_app_cli_product_perception_live_probe_records_scoped_negative() -> None:
    text = _read(CODEX_APP_CLI_PRODUCT_PERCEPTION_LIVE_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live hook perception proof" in text
    assert "Verdict: scoped negative" in text
    assert "codex_cli_live_hooks_exposed_stop_only_no_product_task_events" in text
    assert "hook_event_counts: {\"Stop\": 3}" in text
    assert "runtime_snapshot_loaded: false on every row" in text
    assert "0 UserPromptSubmit/tool/failure rows" in text or "No product-perception success" in text
    assert "Codex JSON stdout stream did include model-visible work events" in text
    assert "No behavior lift" in text
    assert "recon/cortex_codex_app_cli_product_perception_live_probe.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_product_perception_live_probe.md"
        in status["active_docs"]
    )


def test_codex_app_cli_product_event_capture_remediation_records_live_pass() -> None:
    text = _read(CODEX_APP_CLI_PRODUCT_EVENT_CAPTURE_REMEDIATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live hook perception proof" in text
    assert "Verdict: pass on live Codex CLI product event capture" in text
    assert "hook_event_counts: {\"PostToolUse\": 2, \"PreToolUse\": 2, \"Stop\": 2, \"UserPromptSubmit\": 1}" in text
    assert "runtime_snapshot_loaded: false on every row" in text
    assert "subject_isolated_git_root: true" in text
    assert "block_rows: 1" in text
    assert "No behavior lift is claimed" in text
    assert "continuation repair loop is not fully closed" in text
    assert "recon/cortex_codex_app_cli_product_event_capture_remediation.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_product_event_capture_remediation.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == (
        "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_stop_continuation_resolution_loop_records_live_pass() -> None:
    text = _read(CODEX_APP_CLI_STOP_CONTINUATION_RESOLUTION_LOOP_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live hook continuation proof" in text
    assert "Verdict: pass_resolved on live Codex CLI Stop continuation resolution" in text
    assert "hook_event_counts: {\"PostToolUse\": 2, \"PreToolUse\": 2, \"Stop\": 2, \"UserPromptSubmit\": 1}" in text
    assert "runtime_snapshot_loaded: false on every row" in text
    assert "final_silence_reason: pressure_below_visible_threshold" in text
    assert "final_active_expectation_ids: []" in text
    assert "verification_evidence_observed: true" in text
    assert "No behavior lift is claimed" in text
    assert "No hidden verifier" in text
    assert "recon/cortex_codex_app_cli_stop_continuation_resolution_loop.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_stop_continuation_resolution_loop.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == (
        "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_hook_native_behavior_comparison_records_live_baseline_gate() -> None:
    text = _read(CODEX_APP_CLI_HOOK_NATIVE_BEHAVIOR_COMPARISON_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live behavior-comparison baseline gate" in text
    assert "Verdict: baseline_not_reproduced; no paired behavior comparison ran." in text
    assert "silent_only_suppressed_payload: exact overdue-verification block JSON" in text
    assert "runtime_snapshot_loaded: false" in text
    assert "truth_gap_false_completion: 0/3 baseline failures reproduced" in text
    assert "output_quality_visible_success: 1/3 baseline failures reproduced" in text
    assert "active_families: []" in text
    assert "No behavior lift is claimed" in text
    assert "baseline_not_reproduced" in text
    assert "failure_no_lift" in text
    assert "Refresh or replace the behavior-comparison fixtures" in text
    assert "recon/cortex_codex_app_cli_hook_native_behavior_comparison.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_hook_native_behavior_comparison.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == (
        "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_astro_three_arm_fixture_refresh_records_mixed_signal() -> None:
    text = _read(CODEX_APP_CLI_ASTRO_THREE_ARM_FIXTURE_REFRESH_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / lab proof" in text
    assert "Probe date: 2026-05-05" in text
    assert "Verdict: mixed_signal; no Cortex speech lift earned." in text
    assert "raw_codex: 2/5 hidden pass, 4/5 objective pass, 0 blocks" in text
    assert "silent_only: 1/5 hidden pass, 5/5 objective pass, 0 blocks" in text
    assert "hook_native_cortex: 2/5 hidden pass, 5/5 objective pass, 0 blocks" in text
    assert "hidden_verifier_probe_attempts: 0" in text
    assert "subject_verifier_only_present_after_count: 0" in text
    assert "The subject `package.json` also strips the hidden npm script" in text
    assert "No Cortex speech lift is claimed" in text
    assert "zero block\nrows and zero rendered text" in text
    assert "recon/cortex_codex_app_cli_astro_three_arm_fixture_refresh.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_astro_three_arm_fixture_refresh.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_value_ablation_audit_records_requirement_perception_decision() -> None:
    text = _read(CODEX_APP_CLI_VALUE_ABLATION_AUDIT_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / lab proof" in text
    assert "Probe date: 2026-05-05" in text
    assert "Verdict: requirement_level_perception_needed." in text
    assert "threshold_not_causal" in text
    assert "thresholds tested: 0.55, 0.35, 0.15, 0.0" in text
    assert "paydown_tightening_risky_claim_alignment_needed" in text
    assert "visible_claim_evidence_gap_detected" in text
    assert "caught_hidden_failures: 3" in text
    assert "overblock_risk_count: 2" in text
    assert "No broad behavior-lift claim" in text
    assert "No claim that hidden verifier facts can become Cortex perception" in text
    assert "Queue requirement-level claim/evidence perception before fixture remediation" in text
    assert "recon/cortex_codex_app_cli_value_ablation_audit.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_value_ablation_audit.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_codex_app_cli_task_standard_spine_records_structural_product_spine() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_SPINE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / lab proof" in text
    assert "Probe date: 2026-05-05" in text
    assert (
        "Verdict: task_standard_spine_structural; live model-standard formation "
        "and behavior lift remain unearned."
    ) in text
    assert "Before work starts, name the standard this work has to meet" in text
    assert "Product activation still requires explicit final text signoff" in text
    assert "generic build/readback activity alone does not pay down standard items" in text
    assert "hidden-failing traces caught as open: 3" in text
    assert "hidden-passing traces with overblock risk: 2" in text
    assert "No live proof that Codex App/CLI accepts" in text
    assert "Queue `codex-app-cli-task-standard-live-probe`" in text
    assert "recon/cortex_codex_app_cli_task_standard_spine.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_spine.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == (
        "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_live_probe_records_structural_gate0() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_LIVE_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / lab proof" in text
    assert "Probe date: 2026-05-05" in text
    assert "Verdict: task_standard_live_probe_structural_gate0" in text
    assert "exact signed-off" in text
    assert "prospective task-set text" in text
    assert "`--enable-task-standard-text`" in text
    assert "without `--runtime-snapshot`" in text
    assert "UserPromptSubmit emits exactly the signed-off context text" in text
    assert "transcript-backed assistant standard block stores" in text
    assert "malformed or\nabsent standard blocks stay diagnostic-only" in text
    assert "No live `codex exec` task-standard run was executed" in text
    assert "No behavior lift" in text
    assert "No downstream proof" in text
    assert "Run `codex-app-cli-task-standard-live-run` only with explicit current-turn" in text
    assert "recon/cortex_codex_app_cli_task_standard_live_probe.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_live_probe.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert status["next_product_train"]["slug"] == "codex-app-cli-posttooluse-shared-tool-evidence-classification"


def test_codex_app_cli_task_standard_live_run_records_capture_failure() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_LIVE_RUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live proof" in text
    assert "Probe date: 2026-05-05" in text
    assert "Verdict: fail" in text
    assert "flat Cortex-internal `{\"context\": ...}` payload" in text
    assert "not as Codex's\nnative `hookSpecificOutput.additionalContext` shape" in text
    assert "did not\nproduce a prework task-standard block" in text
    assert "`hook_rows`: 7" in text
    assert "`context_rows`: 1" in text
    assert "`standard_capture_rows`: 0" in text
    assert "`first_tool_index`: 2" in text
    assert "`first_standard_capture_index`: null" in text
    assert "`runtime_snapshot_loaded`: false on every row" in text
    assert "9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9" in text
    assert "a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc" in text
    assert "No prework task-standard capture was earned" in text
    assert "No SRE law, Cortex speech, selector threshold" in text
    assert "Queue `codex-app-cli-task-standard-capture-boundary-remediation`" in text
    assert "recon/cortex_codex_app_cli_task_standard_live_run.md" in docs_index
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_live_run.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_hook_contract_capture_boundary_remediation_records_structural_fix() -> None:
    text = _read(CODEX_APP_CLI_HOOK_CONTRACT_CAPTURE_BOUNDARY_REMEDIATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / structural proof" in text
    assert "Verdict: structural pass" in text
    assert "hookSpecificOutput.additionalContext" in text
    assert "`{\"decision\":\"block\",\"reason\":\"...\"}`" in text
    assert "`--disable-stop-blocks`" in text
    assert "The old flat `{\"context\": ...}` shape is rejected" in text
    assert "No live Codex rerun was performed" in text
    assert "Queue `codex-app-cli-task-standard-context-live-rerun`" in text
    assert (
        "recon/cortex_codex_app_cli_hook_contract_capture_boundary_remediation.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_hook_contract_capture_boundary_remediation.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_context_live_rerun_records_partial_delivery() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_CONTEXT_LIVE_RERUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / live proof" in text
    assert "Verdict: partial_delivery_only" in text
    assert "hookSpecificOutput.additionalContext" in text
    assert "standard_capture_rows`: 0" in text
    assert "first_tool_index`: 2" in text
    assert "first_standard_capture_index`: null" in text
    assert "prework_standard_capture`: false" in text
    assert "Work standard: Create `cortex_task_standard_live.txt`" in text
    assert "Likely misses: Wrong filename" in text
    assert "Closure evidence: Command output shows" in text
    assert "transcript_path" in text
    assert "Stop-block suppression worked" in text
    assert "No `TaskStandardSpine.standard_items` were captured" in text
    assert (
        "Queue `codex-app-cli-task-standard-pretool-transcript-capture`"
        in text
    )
    assert (
        "recon/cortex_codex_app_cli_task_standard_context_live_rerun.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_context_live_rerun.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_communication_boundary_audit_records_proof_ladder() -> None:
    text = _read(CODEX_APP_CLI_COMMUNICATION_BOUNDARY_AUDIT_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product / lab proof" in text
    assert "Verdict: structural_proof_boundary_issue_localized_to_codex_app_cli" in text
    assert "`host_stdout_contract_ok`" in text
    assert "`host_attached_context_observed`" in text
    assert "`model_assimilation_observed`" in text
    assert "`state_capture_observed`" in text
    assert "`gate_used_captured_state`" in text
    assert "`behavior_lift_claim_allowed`" in text
    assert "`host_contract_mismatch`" in text
    assert "`lifecycle_config_mismatch`" in text
    assert "`temporal_capture_mismatch`" in text
    assert "`live_vs_gate0_mismatch`" in text
    assert "`workflow_health_closeout_coupling`" in text
    assert "`mechanical_success`" in text
    assert "`product_evidence_success`" in text
    assert "`partial_evidence_only`" in text
    assert "[features].codex_hooks = false" in text
    assert "Queue `codex-app-cli-task-standard-pretool-transcript-capture`" in text
    assert (
        "recon/cortex_codex_app_cli_communication_boundary_audit_and_hardening.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_communication_boundary_audit_and_hardening.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "posttooluse task-standard" in work_note
    assert "live-equivalent" in work_note
    assert "no broad cortex lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_pretool_transcript_capture_records_state_capture() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_PRETOOL_TRANSCRIPT_CAPTURE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab proof" in text
    assert "Date: 2026-05-05" in text
    assert "PreToolUse" in text
    assert "PostToolUse` as fallback" in text
    assert "assistant-authored" in text
    assert "before the first tool/function call" in text
    assert "Developer\ncontext, user prompt text, tool calls, tool outputs" in text
    assert "state_capture_observed=true" in text
    assert "gate_used_captured_state=false" in text
    assert "behavior_lift_claim_allowed=false" in text
    assert "run_20260505T195300Z" in text
    assert "No model-visible text changed" not in text
    assert "does not earn live rerun success" in text
    assert "Queue `codex-app-cli-task-standard-live-capture-rerun`" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_pretool_transcript_capture.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_pretool_transcript_capture.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "posttooluse task-standard" in work_note
    assert "live-equivalent" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_live_capture_rerun_records_pass() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_LIVE_CAPTURE_RERUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab proof" in text
    assert "Date: 2026-05-05" in text
    assert "`pass_prework_standard_capture`" in text
    assert "run_20260505T213824Z" in text
    assert "host_attached_context_observed=true" in text
    assert "model_assimilation_observed=true" in text
    assert "state_capture_observed=true" in text
    assert "gate_used_captured_state=false" in text
    assert "behavior_lift_claim_allowed=false" in text
    assert "first_standard_capture_index=2" in text
    assert "first_tool_index=2" in text
    assert "pretool-transcript-standard" in text
    assert "Stop blocks were disabled" in text
    assert "not counted as model-visible\ngate use" in text
    assert "task-standard Stop-gating live probe" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_live_capture_rerun.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_live_capture_rerun.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "no broad cortex lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_stop_gating_calibration_records_pass() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_CALIBRATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab proof" in text
    assert "Verdict: `pass_gating_calibrated`" in text
    assert "`premature_closure_gap`" in text
    assert "`clean_evidenced_closure`" in text
    assert "run_20260505T213824Z" in text
    assert "latest_live_capture_replay_does_not_overblock=true" in text
    assert "a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc" in text
    assert "No live Codex Stop-gating evidence" in text
    assert "Queue `codex-app-cli-task-standard-stop-gating-live-run`" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_stop_gating_calibration_probe.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_stop_gating_calibration_probe.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "posttooluse task-standard" in work_note
    assert "no broad cortex lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_stop_gating_live_run_records_gate_use() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_LIVE_RUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab proof" in text
    assert "Verdict: `pass_gating_observed`" in text
    assert "run_20260505T222615Z" in text
    assert "hookSpecificOutput.additionalContext" in text
    assert "exact one-line file" in text
    assert "`ls`, `wc -l`,\n  `cat -A`, and `cmp`" in text
    assert "pressure_below_visible_threshold" in text
    assert "No paired behavior lift" in text
    assert "Queue `codex-app-cli-task-standard-behavior-comparison`" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "no broad cortex lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_task_standard_behavior_comparison_harness_records_gate0() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_BEHAVIOR_COMPARISON_HARNESS_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product + lab proof" in text
    assert "Verdict: structural Gate 0 passed" in text
    assert "`raw_codex`" in text
    assert "`silent_task_standard`" in text
    assert "`active_task_standard`" in text
    assert "`--disable-stop-blocks`" in text
    assert "did not use\n  `--disable-model-visible-blocks`" in text
    assert "No live behavior lift" in text
    assert "Queue `codex-app-cli-task-standard-behavior-comparison-live-run`" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_behavior_comparison_harness.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_behavior_comparison_harness.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "posttooluse task-standard" in work_note
    assert "live-equivalent" in work_note
    assert "no broad cortex lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_lifecycle_actuator_map_records_event_control_order() -> None:
    text = _read(CODEX_APP_CLI_LIFECYCLE_ACTUATOR_MAP_PATH)
    tracker = _read(EXECUTIVE_RUNTIME_TRACKER_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product architecture + doctrine/status" in text
    assert "Verdict: `map_landed`; implementation remains queued." in text
    assert "`SessionStart`: session/workspace context through additionalContext" in text
    assert "`UserPromptSubmit`: prospective task-set formation through additionalContext" in text
    assert "`PreToolUse`: hard motor deny/block only" in text
    assert "additionalContext is not a supported model-context surface" in text
    assert "`PermissionRequest`: approval-bound route control" in text
    assert "`PostToolUse`: strongest next implementation target" in text
    assert "`Stop`: late closure continuation through block/reason" in text
    assert "Queue `codex-app-cli-posttooluse-task-standard-next-step-correction`." in text
    assert "specific to product-visible mismatch" in text
    assert "no third-agent voice" in text
    assert 'no generic "verify more" advice' in text
    assert "clean-control denial as a high-severity overblock" in text
    assert "Sinkhorn/transport remains deferred" in text
    assert "no runtime behavior change" in text
    assert "no PostToolUse behavior\nproof" in text
    assert "no PreToolUse motor-inhibition proof" in text
    assert "no Sinkhorn implementation" in text
    assert (
        "recon/cortex_codex_app_cli_lifecycle_actuator_map.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_lifecycle_actuator_map.md"
        in status["active_docs"]
    )
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "firing-boundary gate 0" in status["next_product_train"]["why_now"].lower()
    assert "exit/status" in status["next_product_train"][
        "why_now"
    ].lower()
    assert "failure_context_ignored" in tracker
    assert "PostToolUse next-action effect remains unearned" in tracker
    assert "PreToolUse motor inhibition should follow only as action blocking" in tracker
    assert "Sinkhorn-style transport belongs later" in tracker


def test_codex_app_cli_posttooluse_task_standard_next_step_correction_records_gate0() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NEXT_STEP_CORRECTION_PATH)
    tracker = _read(EXECUTIVE_RUNTIME_TRACKER_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + lab proof" in text
    assert "Verdict: `pass_posttooluse_gate0`; implementation remains Gate-0 only." in text
    assert "--enable-posttooluse-task-standard-context" in text
    assert "one Codex-native PostToolUse context" in text
    assert "specific captured task-standard item is unresolved" in text
    assert "flag disabled stayed silent" in text
    assert "clean-evidenced work\nstayed silent" in text
    assert "blocker/waiting/unrelated-tool controls stayed silent" in text
    assert "No live\nCodex run was executed" in text
    assert "SRE law" in text
    assert "Sinkhorn/transport" in text
    assert "PreToolUse motor inhibition" in text
    assert "Not earned: live behavior lift" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_next_step_correction.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_next_step_correction.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "behavior lift" in work_note
    assert "signed userpromptsubmit text" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "candidate artifact creation" in status["next_product_train"][
        "primary_metric"
    ].lower()
    assert "firing-boundary" in status["next_product_train"][
        "kill_rule"
    ].lower()
    assert "three-arm behavior comparison" in status["next_product_train"]["guardrail"].lower()
    assert "pretooluse denial" in status["next_product_train"]["guardrail"].lower()
    assert "sinkhorn/transport" in status["next_product_train"]["guardrail"].lower()
    assert "architecture decision" in status["next_product_train"][
        "kill_rule"
    ].lower()
    assert "failure_context_ignored" in tracker
    assert "not a three-arm behavior comparison" in tracker


def test_codex_app_cli_posttooluse_task_standard_calibration_decision_queues_narrow_probe() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_CALIBRATION_DECISION_PATH)
    tracker = _read(EXECUTIVE_RUNTIME_TRACKER_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product architecture + lab proof review" in text
    assert "Verdict: `decision_queue_narrow_live_posttooluse_probe`." in text
    assert "queues a narrow live PostToolUse actuator probe" in text
    assert "does not queue a three-arm\nbehavior comparison" in text
    assert "pass_posttooluse_gate0" in text
    assert "hookSpecificOutput.additionalContext" in text
    assert "Clean-evidenced, blocker, waiting-on-user, unrelated-tool" in text
    assert "Live execution remains approval-gated" in text
    assert "not approved until the stack is published or merged" in text
    assert "Not earned: live behavior lift" in text
    assert "PreToolUse motor inhibition" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_calibration_decision.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_calibration_decision.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "firing-boundary remediation" in status[
        "next_product_train"
    ]["executive_benefit"]
    assert "candidate artifact creation" in status["next_product_train"][
        "primary_metric"
    ].lower()
    assert "firing-boundary gate 0" in status["next_product_train"]["why_now"].lower()
    assert "failure_context_ignored" in tracker


def test_codex_app_cli_task_standard_stack_publication_hygiene_blocks_live_until_clean() -> None:
    text = _read(CODEX_APP_CLI_TASK_STANDARD_STACK_PUBLICATION_HYGIENE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: workflow / product-proof hygiene" in text
    assert "Verdict: `stack_publication_hygiene_required_before_live_probe`." in text
    assert "codex/20260506-020000-task-standard-stack-publication-hygiene" in text
    assert "narrow PostToolUse live probe remains queued but not approved" in text
    assert "must not use `--require-pass`" in text
    assert (
        "recon/cortex_codex_app_cli_task_standard_stack_publication_hygiene.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_task_standard_stack_publication_hygiene.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "posttooluse completion predicate" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_posttooluse_task_standard_narrow_live_probe_is_harness_ready_not_run() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NARROW_LIVE_PROBE_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + live-proof harness" in text
    assert "Verdict: `live_probe_harness_ready_not_run`." in text
    assert "--task-standard-posttooluse-live" in text
    assert "CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved" in text
    assert "The live command was not run" in text.replace("\n", " ")
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_probe.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_probe.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "live-equivalent" in work_note
    assert "posttooluse completion predicate" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "must not change" in status["next_product_train"][
        "guardrail"
    ].lower()


def test_codex_app_cli_posttooluse_task_standard_narrow_live_run_records_negative_result() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_NARROW_LIVE_RUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product live proof" in text
    assert "Verdict: `failure_context_ignored`." in text
    assert "CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved" in text
    assert "task_standard_posttooluse_live_20260507T100836Z" in text
    assert "next_model_tool_did_not_run_named_direct_check" in text
    assert "0 PostToolUse contexts" in text
    assert "Stop continuation loop" in text
    assert "next-step actuator effect" in text
    assert "No broad Cortex behavior lift" in text
    assert "codex-app-cli-posttooluse-task-standard-actuator-architecture-decision" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_run.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_run.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "behavior lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "firing-boundary remediation" in status[
        "next_product_train"
    ]["executive_benefit"].lower()
    assert "firing-boundary gate 0" in status["next_product_train"][
        "why_now"
    ].lower()
    assert "exit/status" in status[
        "next_product_train"
    ]["why_now"].lower()
    assert "candidate artifact creation" in status[
        "next_product_train"
    ]["primary_metric"].lower()
    assert "must not change" in status["next_product_train"]["guardrail"].lower()


def test_codex_app_cli_posttooluse_task_standard_architecture_decision_queues_phase_aware_gate0() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_ACTUATOR_ARCHITECTURE_DECISION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product architecture decision" in text
    assert "Verdict: `decision_queue_phase_aware_posttooluse_calibration_gate0`." in text
    assert "task_standard_posttooluse_live_20260507T100836Z" in text
    assert "PostToolUse timing/selection failure" in text
    assert "host delivery: passed" in text
    assert "task-standard capture: passed" in text
    assert "clean/control overcontrol: passed" in text
    assert "immediate next-action effect: failed" in text
    assert "failed precondition" in text
    assert "artifact creation rather than direct\n  verification" in text
    assert "Stop continuation" in text
    assert "codex-app-cli-posttooluse-task-standard-phase-aware-calibration-gate0" in text
    assert "product-visible artifact or candidate output exists" in text
    assert "closure before the named direct check still fails" in text
    assert "no PostToolUse next-action effect claim" in text
    assert "no authorization to tune" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_architecture_decision.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_architecture_decision.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "phase-aware posttooluse completion predicate" in work_note
    assert "missing-artifact" in work_note
    assert "behavior lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "firing-boundary gate 0" in status["next_product_train"]["why_now"].lower()
    assert "explicit current-turn approval" in status["next_product_train"]["guardrail"]


def test_codex_app_cli_posttooluse_phase_aware_gate0_records_structural_pass() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_GATE0_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + lab proof" in text
    assert "Verdict: `pass_posttooluse_phase_aware_gate0`." in text
    assert "task_standard_posttooluse_phase_aware_gate0/gate0_report.json" in text
    assert "pre_artifact_candidate_missing" in text
    assert "successful candidate artifact creation" in text
    assert "`exact_result.txt`" in text
    assert "`wc -l exact_result.txt`" in text
    assert "`cat -A exact_result.txt`" in text
    assert "clean evidenced work stayed silent" in text
    assert "markerless\n  literal-only controls stayed silent" in text
    assert "no live Codex run was executed" in text
    assert "no live behavior lift" in text
    assert "no exactness value lift" in text
    assert "no signed UserPromptSubmit text edit" in text
    assert "no PostToolUse text edit" in text
    assert "no Stop text edit" in text
    assert "no SRE law" in text
    assert "Sinkhorn/transport" in text
    assert "PreToolUse denial" in text
    assert "PermissionRequest" in text
    assert "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-run" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_calibration_gate0.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_calibration_gate0.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "pre_artifact_candidate_missing" in work_note
    assert "candidate artifact creation" in work_note
    assert "no live behavior lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "explicit current-turn approval" in status["next_product_train"]["guardrail"]
    assert "`--require-pass`" in status["next_product_train"]["guardrail"]
    assert "three-arm behavior comparison" in status["next_product_train"]["guardrail"].lower()
    assert "candidate_artifact_without_posttooluse_context" in status[
        "next_product_train"
    ]["why_now"]
    assert "architecture decision" in status["next_product_train"]["kill_rule"]


def test_codex_app_cli_posttooluse_phase_aware_narrow_live_run_records_no_context() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_NARROW_LIVE_RUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product live proof" in text
    assert "Verdict: `failure_no_context`." in text
    assert "task_standard_posttooluse_live_20260507T142129Z" in text
    assert "candidate_artifact_without_posttooluse_context" in text
    assert "three task-standard items were captured" in text
    assert "PostToolUse lifecycle was observed" in text
    assert "candidate artifact prerequisite work was observed" in text
    assert "PostToolUse context count: 0" in text
    assert "pre_artifact_candidate_missing" in text
    assert "no_verification_marker" in text
    assert "no_candidate_artifact_or_readback" in text
    assert "No clean/control overcontrol occurred" in text
    assert "root `.codex/config.toml` hash unchanged" in text
    assert "no runtime snapshot loaded" in text
    assert "hidden scoring stayed absent / scoring-only" in text
    assert "Stop remains the only live-proven corrective actuator" in text
    assert "no PostToolUse next-action effect claim" in text
    assert "no exactness-only value lift" in text
    assert "no broad Cortex behavior lift" in text
    assert "no permission to rerun live" in text
    assert "codex-app-cli-posttooluse-task-standard-firing-boundary-remediation" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_run.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_run.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "exit/status marker" in work_note
    assert "posttooluse completion predicate" in work_note
    assert "behavior lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "rerun" in status["next_product_train"][
        "executive_benefit"
    ].lower()
    assert "candidate_artifact_without_posttooluse_context" in status[
        "next_product_train"
    ]["why_now"]
    assert "explicit current-turn approval" in status["next_product_train"]["guardrail"]
    assert "posttooluse text" in status["next_product_train"][
        "guardrail"
    ].lower()
    assert "sinkhorn/transport" in status["next_product_train"]["guardrail"].lower()
    assert "pretooluse denial" in status["next_product_train"]["guardrail"].lower()
    assert "approval-gated phase-aware narrow live rerun" in status["next_product_train"][
        "kill_rule"
    ].lower()


def test_codex_app_cli_posttooluse_firing_boundary_remediation_records_gate0_pass() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_FIRING_BOUNDARY_REMEDIATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + no-live remediation proof" in text
    assert "Verdict: `pass_posttooluse_firing_boundary_gate0`." in text
    assert "task_standard_posttooluse_live_20260507T142129Z" in text
    assert "task_standard_posttooluse_firing_boundary_gate0/gate0_report.json" in text
    assert "`tool_response` is present" in text
    assert "generic tool-success classifier" in text
    assert "pre_artifact_candidate_missing" in text
    assert "empty-output candidate artifact creation" in text
    assert "readback output without exit/status markers" in text
    assert "markerless aligned literal output stayed silent" in text
    assert "failed candidate, blocker, waiting, unrelated" in text
    assert "The model-visible PostToolUse text itself did not change" in text
    assert "no live behavior lift" in text
    assert "no exactness-only value lift" in text
    assert "no PostToolUse next-action effect claim" in text
    assert "Sinkhorn/transport" in text
    assert "PreToolUse denial" in text
    assert "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_firing_boundary_remediation.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_firing_boundary_remediation.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "firing-boundary remediation" in work_note
    assert "live-equivalent" in work_note
    assert "posttooluse completion predicate" in work_note
    assert "no live behavior lift" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "explicit current-turn approval" in status["next_product_train"]["guardrail"]
    assert "`--require-pass`" in status["next_product_train"]["guardrail"]
    assert "three-arm behavior comparison" in status["next_product_train"]["guardrail"].lower()
    assert "approval-gated phase-aware narrow live rerun" in status["next_product_train"][
        "kill_rule"
    ].lower()


def test_codex_app_cli_posttooluse_phase_aware_narrow_live_rerun_records_overcontrol() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_PHASE_AWARE_NARROW_LIVE_RERUN_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product live proof" in text
    assert "Verdict: `failure_overcontrol`." in text
    assert "task_standard_posttooluse_live_20260507T153242Z" in text
    assert "clean_or_control_case_received_context" in text
    assert "PostToolUse context count: 1" in text
    assert "task-standard:closure_evidence:26572a09b361be19" in text
    assert "next tool after context matched the context" in text
    assert "`clean_evidenced`: 1 PostToolUse context" in text
    assert "`honest_blocker`: 0 PostToolUse contexts" in text
    assert "`waiting_on_user`: 0 PostToolUse contexts" in text
    assert "`unrelated_tool`: 0 PostToolUse contexts" in text
    assert "no clean-control safety claim" in text
    assert "no permission to run another live probe" in text
    assert "codex-app-cli-posttooluse-task-standard-overcontrol-remediation" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "failure_overcontrol" in work_note
    assert "clean_evidenced" in work_note
    assert "behavior_lift_claim_allowed" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "no live codex run" in status["next_product_train"]["guardrail"].lower()
    assert "clean/control rows silent" in status["next_product_train"][
        "kill_rule"
    ].lower()


def test_codex_app_cli_posttooluse_overcontrol_remediation_records_gate0_pass() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_OVERCONTROL_REMEDIATION_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + no-live remediation proof" in text
    assert "Verdict: `pass_posttooluse_overcontrol_gate0`." in text
    assert "task_standard_posttooluse_live_20260507T153242Z" in text
    assert "task_standard_posttooluse_overcontrol_gate0/gate0_report.json" in text
    assert "`phase_check_failed`" in text
    assert "`cat: illegal option -- A`" in text
    assert "`usage:`" in text
    assert "generic tool-success classifier" in text
    assert "mismatch candidate artifact and readback context paths still fire" in text
    assert "The model-visible PostToolUse text itself did not change" in text
    assert "no live behavior lift" in text
    assert "no clean-control safety claim in live use" in text
    assert "Sinkhorn/transport" in text
    assert "PreToolUse denial" in text
    assert "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_overcontrol_remediation.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_overcontrol_remediation.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "pass" in work_note
    assert "phase_check_failed" in work_note
    assert "cat: illegal option -- a" in work_note
    assert "behavior_lift_claim_allowed" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "explicit current-turn live approval" in status["next_product_train"][
        "guardrail"
    ].lower()
    assert "`--require-pass`" in status["next_product_train"]["guardrail"]
    assert "three-arm behavior comparison" in status["next_product_train"][
        "guardrail"
    ].lower()


def test_codex_app_cli_posttooluse_actuator_trace_repair_records_gate0_pass() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_TASK_STANDARD_ACTUATOR_TRACE_REPAIR_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product host actuator + lab trace proof" in text
    assert "Verdict: `pass_posttooluse_actuator_trace_gate0`." in text
    assert "posttooluse_task_standard_actuator.py" in text
    assert "task_standard_posttooluse_actuator_trace_gate0/gate0_report.json" in text
    assert "task_standard_posttooluse_live_20260507T153242Z" in text
    assert "hook chronology" in text
    assert "context row: PostToolUse row index `5`" in text
    assert "printf 'alpha beta omega' > exact_result.txt" in text
    assert "od -An -t x1 -v exact_result.txt" in text
    assert "failed checks stay silent with private `phase_check_failed`" in text
    assert "model-visible PostToolUse text did not change" in text
    assert "no behavior lift" in text
    assert "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_trace_repair.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_trace_repair.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )


def test_codex_app_cli_posttooluse_causal_trace_ids_records_gate0_pass() -> None:
    text = _read(CODEX_APP_CLI_POSTTOOLUSE_CAUSAL_TRACE_IDS_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product diagnostics + lab trace proof" in text
    assert "Verdict: `pass_posttooluse_actuator_trace_gate0`." in text
    assert "`tool_use_id`" in text
    assert "`tool_event_ref`" in text
    assert "missing or duplicated" in text
    assert "ambiguous" in text
    assert "task_standard_posttooluse_live_20260507T153242Z" in text
    assert "lacks `tool_use_id`" in text
    assert "no preceding or next tool is inferred by position" in text
    assert "codex-app-cli-posttooluse-shared-tool-evidence-classification" in text
    assert (
        "recon/cortex_codex_app_cli_posttooluse_causal_trace_ids.md"
        in docs_index
    )
    assert (
        "docs/recon/cortex_codex_app_cli_posttooluse_causal_trace_ids.md"
        in status["active_docs"]
    )
    assert (
        status["work_today"]["slug"]
        == "codex-app-cli-posttooluse-causal-trace-ids"
    )
    work_note = status["work_today"]["note"].lower()
    assert "tool_use_id" in work_note
    assert "tool_event_ref" in work_note
    assert "ordinal" in work_note
    assert "ambiguous" in work_note
    assert "shared tool-evidence classification" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status[
        "next_product_train"
    ]["surface"]
    assert "no live codex run" in status["next_product_train"]["guardrail"].lower()


def test_task_standard_sre_correspondence_is_lawfully_mapped() -> None:
    cortex_doc = _read(CORTEX_DOC_PATH)
    sre_doc = _read(CORTEX_V2_SRE_PATH)
    recon = _read(TASK_STANDARD_SRE_CORRESPONDENCE_RECON_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "prospective identity-continuous task-set formation" in cortex_doc
    assert "prior-act identity-continuous self-correction" in cortex_doc
    assert "must be explicitly signed off before activation" in cortex_doc
    assert "must not impose external rules or hidden answers" in cortex_doc

    assert "### 8.2 Task-local standard formation and maintenance" in sre_doc
    assert "not Core certification truth" in sre_doc
    assert "not AUX memory" in sre_doc
    assert "host-specific adaptor rule" in sre_doc
    assert "Generic verification-shaped activity may not satisfy" in sre_doc
    assert "T_t = (O_t, S_t, M_t, C_t, E_t, U_t)" in sre_doc
    assert "D_std(t)" in sre_doc
    assert "`standard_aligned` or `claim_aligned`" in sre_doc
    assert "A `generic_check` may\nrecord" in sre_doc
    assert "expectation-ledger law" in sre_doc
    assert "does not create a new speech\nsurface" in sre_doc

    math_rows = {entry["id"]: entry for entry in status["math_to_code_map"]}
    assert math_rows["task_standard_spine"]["code_refs"] == [
        "cortex/sre/task_standard.py"
    ]
    assert "Task-local standard and evidence alignment state" in cortex_doc
    assert "`task_standard_spine`" in cortex_doc
    assert "docs/recon/cortex_task_standard_sre_correspondence_reconciliation.md" in status[
        "active_docs"
    ]
    assert "recon/cortex_task_standard_sre_correspondence_reconciliation.md" in docs_index
    assert "Verdict: task_standard_sre_correspondence_reconciled" in recon
    assert "Changed no product behavior and no model-visible text" in recon


def test_task_standard_executive_doctrine_math_refinement_is_recorded() -> None:
    cortex_doc = _read(CORTEX_DOC_PATH)
    sre_doc = _read(CORTEX_V2_SRE_PATH)
    tracker = _read(EXECUTIVE_RUNTIME_TRACKER_PATH)
    recon = _read(TASK_STANDARD_EXECUTIVE_DOCTRINE_MATH_RECON_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "### Executive Capacity Map" in cortex_doc
    for phrase in (
        "Task-set / standard formation",
        "Goal maintenance",
        "Conflict monitoring",
        "Action gating",
        "Prediction-error recalibration",
    ):
        assert phrase in cortex_doc
    assert "not as a\nclaim of biological equivalence" in cortex_doc
    assert "T_t = (O_t, S_t, M_t, C_t, E_t, U_t)" in sre_doc
    assert "D_std(t)" in sre_doc
    assert "`generic_check`" in sre_doc
    assert "expectation-ledger law" in sre_doc
    assert "signed-off prospective task-set formation" in tracker
    assert "captured standard shapes later gating" in tracker

    assert "Surface: product / doctrine correspondence" in recon
    assert "Verdict: task_standard_executive_doctrine_math_refined" in recon
    assert "No model-visible text changed" in recon
    assert "No ninth bio-to-code denominator row was added" in recon
    assert "explicit final model-visible text signoff" in recon
    assert (
        "docs/recon/cortex_task_standard_executive_doctrine_math_refinement.md"
        in status["active_docs"]
    )
    assert "recon/cortex_task_standard_executive_doctrine_math_refinement.md" in docs_index
    assert status["work_today"]["slug"] == (
        "codex-app-cli-posttooluse-causal-trace-ids"
    )


def test_cortex_plugin_design_preserves_scope_and_truth_boundaries() -> None:
    text = _read(CORTEX_PLUGIN_DESIGN_PATH)
    sections = [line for line in text.splitlines() if line.startswith("## ")]

    assert "Surface: product design" in text
    assert "structural design only" in text
    assert "does not implement the plugin" in text
    assert sections == [
        "## 1. Identity",
        "## 2. The H x F Lattice",
        "## 3. Hook-by-Hook Design",
        "## 4. State Persistence and Lifecycle",
        "## 5. User Configuration",
        "## 6. Cortex Packaging Strategy",
        "## 7. Multi-Host Shipping Truth",
        "## 8. What's Empirically Established About Bridge Authority",
        "## 9. Privacy, Logging, Observability",
        "## 10. Known-Open Empirical Questions",
        "## 11. v2 Deferrals",
        "## 12. Closure-Line Discipline",
        "## 13. Validation Gates Before Build Phase",
    ]

    # Identity and anti-generic-bloat boundary.
    assert "not generic hook middleware" in text
    assert "not a package of \"PreToolUse and Stop bridges\"" in text
    assert "docs/CORTEX.md` §1" in text
    assert "docs/CORTEX.md` §3" in text
    assert "Claude Code Desktop as the intended v1 plugin surface" in text
    assert "does not change current\nshipping truth" in text
    assert "`openai.codex_app_cli`" in text
    assert "live paired evidence earns behavior lift" in text

    # Hook events and failure modes are covered without conflating ownership,
    # structural adapter code, and live behavior evidence.
    for hook in [
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "PostToolUseFailure",
        "PreCompact",
        "SubagentStop",
        "Stop",
        "SessionEnd",
    ]:
        assert f"### {hook}" in text
        assert hook in text
    for failure_mode in [
        "Truth-preserving commitments and bounded certification",
        "Bounded correction and verified-work preservation",
        "Uncertainty handling and brake",
        "Branch continuity, suspend/resume, and truthful closure",
        "Intervention pricing versus neutrality",
        "Blocker surfacing and goal-debt management",
        "Multi-host executive continuity",
        "Offline consolidation and support geometry",
    ]:
        assert failure_mode in text
    assert "ACTIVE:" not in text
    assert "DEFERRED:" not in text
    assert "N/A:" not in text
    assert "ARCHITECTURAL OWNER:" in text
    assert "STRUCTURAL ADAPTER IMPLEMENTED:" in text
    assert "LIVE BEHAVIOR VALIDATED:" in text
    assert "UNEARNED BEHAVIOR:" in text
    assert "Gate 1 did not earn lift" in text
    assert "`Stop` closure pressure has" in text
    assert "empty by accident" in text
    assert "session_id+cwd` is not a cross-thread resume key" in text
    assert "runtime_context.pretooluse_model_visible=false" in text
    assert "PostToolUseFailure -> feedback -> Stop loop" in text
    assert "PreToolUse Content Shape Research" in text
    assert "What's Empirically Established About Bridge Authority" in text
    assert "hook_system_message" in text
    assert "exact-output" in text
    assert "shaped Stop repaired 2/3 failure pairs" in text
    assert "PostToolUseFailure:Bash` and `PostToolUse:Bash` event distinction" in text
    assert "Model-Facing Translation Boundary" in text
    assert "raw internal Stop wording is content-shape contaminated" in text
    assert "Mac pending-goal retest repaired only 1/2 shaped trials" in text
    assert "translated Stop closure pressure is the only plausible actively" in text
    assert "Codex cannot drive Claude Code Desktop's GUI" in text

    # Existing Cortex modules are the source of law; the plugin is wiring.
    for ref in [
        "cortex/hosts/claude/runtime.py",
        "cortex/hosts/runtime_context.py::runtime_context_from_last_feedback",
        "cortex/sre/operator_routing.py",
        "cortex/sre/brake.py",
        "cortex/sre/goal_debt.py",
        "cortex/runtime/operator_brain_capability.py",
        "cortex/aux/persistence.py",
        "cortex/aux/publication.py",
        "cortex/aux/support_priors.py",
    ]:
        assert ref in text

    # Hygiene apparatus stays out of product packaging.
    assert "does not bundle, invoke, or replicate the Cortex Mission Reflection" in text
    assert "`grid-validate`" in text
    assert "the hygiene apparatus is not Cortex" in text
    assert "development workflow graph" in text

    # AUX remains claim-conservative.
    assert "OfflineSupportPublication" in text
    assert "raw AUX memory remains support-side" in text
    assert "AUX remains publication-only and score-pricing-only" in text
    assert "raw AUX episodes do not reach the model" in text
    assert "cannot mutate routing, certification, or blockedness" in text

    # Managed-worktree findings stay conservative.
    assert "managed-worktree" in text
    assert "not `.claude/worktrees/...`" in text
    assert "does not prove an actual managed-worktree cwd case" in text
    assert "If a future Code-tab subject uses an actual managed-worktree cwd" in text

    # Explicit non-features prevent future drift.
    for forbidden_non_feature in [
        "generic instruction-following improvements",
        "politeness, tone, or general reasoning improvements",
        "post-training calibration",
        "closed-loop monitor",
        "user-facing memory features",
        "raw AUX memory re-entry",
        "background polling, timers, or hidden state mutation",
    ]:
        assert forbidden_non_feature in text


def test_cortex_plugin_adapter_preserves_host_adapter_boundaries() -> None:
    text = _read(CORTEX_PLUGIN_ADAPTER_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: product adapter / structural" in text
    assert "does not claim live model-output" in text
    assert "shipping default" in text
    assert "business logic" in text
    assert "plugin is transport wire" in text
    assert "does not introduce new math objects" in text
    assert "Ownership stays with" in text
    assert "math-to-code map" in text
    assert "PreToolUse:Bash" in text
    assert "hookSpecificOutput.additionalContext" in text
    assert "task-local executive constraint sentence" in text
    assert "Clean prior feedback emits no context" in text
    assert "hook events parse" in text
    assert "no-op transport stubs" in text
    assert "Shipping truth remains" in text
    assert "openai.codex_app_cli" in text
    assert "lab/cortex_plugin_skeleton/" in text
    assert "cortex/hosts/claude_code_desktop/ingress.py" in text
    assert "cortex/hosts/claude_code_desktop/runtime.py" in text
    assert "cortex/hosts/claude_code_desktop/hook_control.py" in text
    assert "cortex_plugin/ADAPTER.md" in docs_index
    assert "docs/cortex_plugin/ADAPTER.md" in status["active_docs"]


def test_cortex_plugin_evidence_synthesis_preserves_truth_boundaries() -> None:
    text = _read(CORTEX_PLUGIN_EVIDENCE_SYNTHESIS_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    status = _load_status()

    assert "Surface: internal / recon synthesis" in text
    assert "does not run a new probe" in text
    assert "does not change shipping truth" in text
    assert "Hook Delivery Truth" in text
    assert "Model-Visible Delivery Truth" in text
    assert "Behavior-Lift Truth" in text
    assert "Product / Shipping Truth" in text
    assert "Codex cannot drive Claude Code" in text
    assert "require the user" in text
    assert "H x F lattice remains the right architecture" in text
    assert "not proof that PreToolUse is the wrong lifecycle" in text
    assert "Stop owns closure pressure, not the whole plugin" in text
    assert "PostToolUseFailure" in text
    assert "session_id+cwd" in text
    assert "Codex may prepare plugin state" in text
    assert "the user must enter the prompts" in text
    assert "Product behavior lift would" in text
    assert "later live paired evidence" in text
    assert "cortex_plugin/EVIDENCE_SYNTHESIS.md" in docs_index
    assert "docs/cortex_plugin/EVIDENCE_SYNTHESIS.md" in status["active_docs"]
    assert (
        "docs/recon/claude_code_cortex_posttool_failure_to_stop_loop_probe.md"
        in status["active_docs"]
    )
    assert (
        "docs/recon/claude_code_cortex_userpromptsubmit_verified_work_probe.md"
        in status["active_docs"]
    )


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
        "doc_roles",
        "executive_completion",
        "bio_to_code_matrix",
        "math_to_code_rules",
        "v2_model_io_analysis",
        "work_today",
        "next_product_train",
        "system_map",
        "subsystems",
        "packet_to_code_anchors",
        "host_surface_taxonomy",
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
        "openai": "openai.codex_app_cli",
        "claude": "claude.code_desktop",
        "gemini": "gemini.api",
        "reference": "reference.runtime",
    }
    assert status["conformance_summary"]["shipping_default"] == "openai.codex_app_cli"
    taxonomy = status["host_surface_taxonomy"]
    assert taxonomy["summary"].startswith("Cortex surfaces are grouped into three top-level buckets")
    taxonomy_buckets = {bucket["id"]: bucket for bucket in taxonomy["buckets"]}
    assert set(taxonomy_buckets) == {
        "product_host_adaptors",
        "api_conformance_adaptors",
        "non_adaptor_support_surfaces",
    }
    product_entries = {
        entry["id"]: entry for entry in taxonomy_buckets["product_host_adaptors"]["entries"]
    }
    assert product_entries["openai.codex_app_cli"]["current_actuator"] == "codex_exec_wrapper_resume"
    assert product_entries["openai.codex_app_cli"]["target_actuator"] == "hook_native_product"
    assert "Codex App Stop-hook proof" in product_entries["openai.codex_app_cli"]["evidence_boundary"]
    assert "Codex CLI codex-exec wrapper proof" in product_entries["openai.codex_app_cli"]["evidence_boundary"]
    api_entries = {
        entry["id"]: entry for entry in taxonomy_buckets["api_conformance_adaptors"]["entries"]
    }
    assert api_entries["openai.api"]["target_actuator"] == "frozen_conformance_support"
    non_adaptor_entries = {
        entry["id"]: entry for entry in taxonomy_buckets["non_adaptor_support_surfaces"]["entries"]
    }
    assert "repo.workflow_guardrails" in non_adaptor_entries
    assert "lab.probe_harnesses" in non_adaptor_entries
    next_train_slug = status["next_product_train"]["slug"]
    assert next_train_slug is None or next_train_slug != status["work_today"]["slug"]
    assert "research_lines_under_evaluation" in status
    assert isinstance(status["research_lines_under_evaluation"], list)
    for entry in status["research_lines_under_evaluation"]:
        assert isinstance(entry, dict)
        assert {"slug", "stage", "summary", "next_step"} <= set(entry)
        assert entry["slug"] != status["work_today"]["slug"]
    assert entry["slug"] != status["next_product_train"]["slug"]
    assert status["work_today"]["slug"] == "codex-app-cli-posttooluse-causal-trace-ids"
    work_note = status["work_today"]["note"].lower()
    assert "failure_overcontrol" in work_note
    assert "posttooluse task-standard" in work_note
    assert "clean_evidenced" in work_note
    assert "behavior lift" in work_note
    assert "overcontrol evidence" in work_note
    assert (
        status["next_product_train"]["slug"]
        == "codex-app-cli-posttooluse-shared-tool-evidence-classification"
    )
    assert "product host actuator plus SRE substrate proof" == status["next_product_train"]["surface"]
    assert "clean-evidenced controls stay silent" in status[
        "next_product_train"
    ][
        "executive_benefit"
    ].lower()
    assert "failure_overcontrol" in status["next_product_train"]["why_now"].lower()
    assert "clean_evidenced" in status["next_product_train"][
        "why_now"
    ].lower()
    assert "clean evidenced" in status["next_product_train"][
        "primary_metric"
    ].lower()
    assert "no live codex run" in status["next_product_train"][
        "guardrail"
    ].lower()
    assert "sinkhorn/transport" in status["next_product_train"][
        "guardrail"
    ].lower()
    assert "pretooluse denial" in status["next_product_train"][
        "guardrail"
    ].lower()
    assert "clean/control rows silent" in status["next_product_train"][
        "kill_rule"
    ].lower()
    assert "architecture decision" in status["next_product_train"][
        "kill_rule"
    ].lower()
    deferred_lines = {entry["slug"]: entry for entry in status["research_lines_under_evaluation"]}
    assert "brain-capability-observation-and-inference" in deferred_lines
    assert (
        deferred_lines["brain-capability-observation-and-inference"]["stage"]
        == "deferred-by-current-task-standard-train"
    )
    assert "openai.codex_app_cli" in status["where_to_work"][0]
    assert "codex_exec_wrapper_resume" in status["where_to_work"][0]
    assert "hook_native_product" in status["where_to_work"][0]
    assert "evidence scopes separate" in status["where_to_work"][1]
    assert "repo workflow hooks" in status["where_to_work"][1]
    assert "posture-sensitive online control is s-tier closed" in status["where_to_work"][2].lower()
    assert "anti-thrash is landed" in status["where_to_work"][2]
    assert "posture truth is single-owned" in status["where_to_work"][2]
    assert "6-axis geometry term" in status["where_to_work"][2]
    assert "route truth stays bounded and non-sovereign" in status["where_to_work"][2]
    assert "live `Q_mem` stays zero" in status["where_to_work"][2]
    assert "host/tool reliability and affordance priors are earned" in status["where_to_work"][2]
    assert "silent-control-verification-debt-continuation seam added" in status["where_to_work"][3]
    assert "resume_verification" in status["where_to_work"][3]
    assert "narrow live behavior-lift evidence" in status["where_to_work"][3]
    assert "baseline failure reproduced 5/5" in status["where_to_work"][3]
    assert "product-runtime anchor" in status["where_to_work"][3]
    assert "product-perception hardening" in status["where_to_work"][3]
    assert "due product-runtime expectation record" in status["where_to_work"][3]
    assert "hidden verifier output scoring only" in status["where_to_work"][3]
    assert "hardened visible-intervention rerun earned negative live evidence" in status["where_to_work"][3]
    assert "wrapper/resume actuator" in status["where_to_work"][3]
    assert "baseline reproduced 3/3" in status["where_to_work"][3]
    assert "visible intervention failed" in status["where_to_work"][3]
    assert "weaker visible-check or narrower-claim path" in status["where_to_work"][3]
    assert "last assistant move already narrowed" in status["where_to_work"][3]
    assert "identity-continuous threshold thoughts" in status["where_to_work"][3]
    assert "attached-context text as fallback" in status["where_to_work"][3]
    assert "codex app/cli lifecycle directive builder" in status["where_to_work"][3].lower()
    assert "grounded intervention records" in status["where_to_work"][3]
    assert "hook-native Stop activation Gate 0 seam" in status["where_to_work"][3]
    assert "exact Codex block JSON" in status["where_to_work"][3]
    assert "hook-native Stop live canary" in status["where_to_work"][3]
    assert "3 live Stop rows" in status["where_to_work"][3]
    assert "a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc" in status["where_to_work"][3]
    assert "live actuator proof only" in status["where_to_work"][3]
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
    assert "## Host Surface Taxonomy" in text
    assert "### Product Host Adaptors" in text
    assert "### API / Conformance Adaptors" in text
    assert "### Non-Adaptor Support Surfaces" in text
    assert "`openai.codex_app_cli`" in text
    assert "`codex_exec_wrapper_resume`" in text
    assert "`hook_native_product`" in text
    assert "Codex App Stop-hook proof" in text
    assert "Codex CLI codex-exec wrapper proof" in text
    assert "`openai.api`" in text
    assert "`repo.workflow_guardrails`" in text
    assert "`lab.probe_harnesses`" in text
    assert "## Next Product Train" in text
    assert "## Research Lines Under Evaluation" in text
    assert "host/tool reliability and affordance priors are earned" in text
    assert "`codex-app-cli-posttooluse-shared-tool-evidence-classification`" in text
    assert "- Next product train after the current focus: `codex-app-cli-posttooluse-shared-tool-evidence-classification`" in text
    assert "- Train: `codex-app-cli-posttooluse-shared-tool-evidence-classification`" in text
    assert "`brain-capability-observation-and-inference` (deferred-by-current-task-standard-train)" in text
    assert "resume_verification" in text.lower()
    assert "hidden verifier" in text.lower()
    assert "due product-runtime expectation record" in text.lower()
    assert "private selection trace" in text.lower()
    assert "hidden verifier output scoring" in text.lower()
    assert "negative live evidence" in text.lower()
    assert "visible intervention failed" in text.lower()
    assert "weaker visible-check or narrower-claim path" in text.lower()
    assert "Shipping Product Target\\nopenai.codex_app_cli" in text
    assert "Shipping default: `openai.codex_app_cli`" in text
    assert "Workflow gates marked `required` are contractual gates checked by `repo_workflow.py`" in text
    assert "| `main_synced` | `required` |" in text
    assert "| `cleanup_report` | `required` |" in text
    assert "hook-native Stop live canary" in text
    assert "product event-capture remediation" in text
    assert "1 exact product-rendered Stop block" in text
    assert "continuation-resolution" in text
    assert "no-snapshot product-perception live probe" in text.lower()
    assert "exposed only 3 stop rows" in text.lower()
    assert "brain-capability-observation-and-inference" in text
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
    assert "The substantive answer to the user's request is the primary deliverable." in agents
    assert "docs/internal/REPO_WORKFLOW.md" in agents
    assert "close-session --publish" not in agents
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
