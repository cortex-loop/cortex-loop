"""Mechanical drift checks for verification closeout and local-command docs."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION_STATUS_NOTE_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md"
)
VERIFICATION_PLAN_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md"
)
LOCAL_VERIFICATION_PATH = REPO_ROOT / "docs" / "CORTEX_V2_LOCAL_VERIFICATION.md"
MAKEFILE_PATH = REPO_ROOT / "Makefile"
REPO_WORKFLOW_PATH = REPO_ROOT / "REPO_WORKFLOW.md"
COVERAGE_BASELINE_NOTE_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_COVERAGE_BASELINE_NOTE_0.md"
)
ACTIVE_WORKSTREAM_PATH = REPO_ROOT / "docs" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
PHASE_GATES_PATH = REPO_ROOT / "docs" / "CORTEX_V2_PHASE_GATES_2.md"
REFERENCE_RUNTIME_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md"
)
REFERENCE_FEEDBACK_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md"
)
REFERENCE_FEEDBACK_PROGRAM_1_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md"
)
REFERENCE_CONTINUITY_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md"
)
OPENAI_RUNTIME_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md"
)
OPENAI_INGRESS_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md"
)
OPENAI_SERVICE_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md"
)
OPENAI_HOST_CONTROL_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0.md"
)
EXECUTIVE_LIVE_OUTCOME_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_EXECUTIVE_LIVE_OUTCOME_PROGRAM_0.md"
)
COMPUTED_EXECUTIVE_LOOP_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_COMPUTED_EXECUTIVE_LOOP_PROGRAM_0.md"
)
CLOSED_LOOP_ENFORCEMENT_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0.md"
)
GEMINI_RUNTIME_RESTACK_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_GEMINI_RUNTIME_RESTACK_PROGRAM_0.md"
)
GEMINI_RUNTIME_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md"
)
GEMINI_INGRESS_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_GEMINI_INGRESS_PROGRAM_0.md"
)
GEMINI_SERVICE_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_GEMINI_SERVICE_PROGRAM_0.md"
)
GEMINI_HOST_CONTROL_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_GEMINI_HOST_CONTROL_PROGRAM_0.md"
)
RUNTIME_RESTACK_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_RUNTIME_RESTACK_PROGRAM_0.md"
)
ERIKA_VISUALIZATION_STATUS_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "CORTEX_EVIDENCE_BASED_STATUS.md"
)
ERIKA_VISUALIZATION_HTML_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "cortex-now-vs-future.html"
)
LIVE_VALIDATION_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md"
)
LIVE_VALIDATION_SCENARIO_CATALOG_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_VALIDATION_SCENARIO_CATALOG_0.md"
)
LIVE_VALIDATION_VERDICT_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md"
)
LIVE_SERVICE_PROOF_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_LIVE_SERVICE_PROOF_0.md"
)
OPERATOR_DIRECTIONALITY_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPERATOR_DIRECTIONALITY_PROGRAM_0.md"
)
OPERATOR_DIRECTIONALITY_SCENARIO_CATALOG_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPERATOR_DIRECTIONALITY_SCENARIO_CATALOG_0.md"
)
OPERATOR_DIRECTIONALITY_AUDIT_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0.md"
)
OPERATOR_ROUTING_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_OPERATOR_ROUTING_PROGRAM_0.md"
)
MEDIATION_HOST_REALIZATION_PROGRAM_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_MEDIATION_HOST_REALIZATION_PROGRAM_0.md"
)
MEDIATION_JUSTIFICATION_NOTE_PATH = (
    REPO_ROOT / "docs" / "CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_accepted_workflow_baseline(workstream_text: str) -> str:
    branch_match = re.search(r"Accepted baseline branch: `([^`]+)`", workstream_text)
    if branch_match is None:
        raise AssertionError("missing accepted workflow baseline in workstream ledger")
    return branch_match.group(1)


def _extract_sh_block(doc: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}.*?```sh\n(.*?)```"
    match = re.search(pattern, doc, re.DOTALL)
    if match is None:
        raise AssertionError(f"missing shell block for heading: {heading}")
    return match.group(1).strip()


def _normalize_shell_block(block: str) -> str:
    lines: list[str] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        lines.append(line)
    return " ".join(" ".join(lines).split())


def _extract_make_targets(makefile_text: str) -> set[str]:
    return set(re.findall(r"^([a-zA-Z0-9][a-zA-Z0-9_-]*):", makefile_text, re.MULTILINE))


def _extract_doc_make_targets(doc_text: str) -> set[str]:
    return set(re.findall(r"^make ([a-zA-Z0-9][a-zA-Z0-9_-]*)$", doc_text, re.MULTILINE))


def _extract_make_recipe(makefile_text: str, target: str) -> str:
    pattern = rf"^{re.escape(target)}:\n((?:\t.*\n)+)"
    match = re.search(pattern, makefile_text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing make recipe for target: {target}")
    recipe_lines = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped:
            recipe_lines.append(stripped)
    return _normalize_shell_block("\n".join(recipe_lines))


def _expand_make_vars(command: str, makefile_text: str) -> str:
    assignments = {
        name: value.strip()
        for name, value in re.findall(r"^([A-Z_]+) \?= (.+)$", makefile_text, re.MULTILINE)
    }
    expanded = command
    while True:
        next_expanded = expanded
        for name, value in assignments.items():
            next_expanded = next_expanded.replace(f"$({name})", value)
        if next_expanded == expanded:
            return expanded
        expanded = next_expanded


def test_implementation_status_note_reflects_current_verification_surfaces() -> None:
    text = _read(IMPLEMENTATION_STATUS_NOTE_PATH)

    assert "there is no repo-local pytest config" not in text
    assert "there is no repo-local coverage configuration" not in text
    assert "`pytest.ini` now exists for repo-local discovery" in text
    assert "`.coveragerc` now exists for repo-local coverage configuration" in text
    assert "repo-local verification entry points now exist in `Makefile`" in text
    assert "no committed baseline artifact is recorded" not in text
    assert "baseline recorded in `docs/CORTEX_V2_COVERAGE_BASELINE_NOTE_0.md`" in text
    assert "It does not track later candidate or post-closeout mediation evidence;" in text
    assert "At the time of this accepted closeout note, repo evidence showed cell-level lift on:" in text
    assert "At that accepted closeout point, package-level evidence remained `insufficient` on every required mediation axis." in text
    assert "The current accepted mediation-justification decision is recorded in `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`." in text
    assert "Current repo-local verification truth:" in text
    assert "It does not by itself open new feature work." in text
    assert "or a separately scoped bounded runtime/product follow-on train." in text
    assert "- and Claude." in text
    assert "OpenAI runtime / ingress / service / bounded host-control" in text
    assert "Gemini runtime / ingress / service / bounded host-control" in text
    assert "Claude runtime / ingress / service / bounded host-control" in text
    assert "clean synced `main` line" in text
    assert "do not hardcode a separate accepted workflow baseline here" in text
    assert "bounded feedback-conditioned intervention thresholding" in text
    assert "bounded enforcement-aware realized control" in text


def test_mediation_justification_note_records_current_decision() -> None:
    text = _read(MEDIATION_JUSTIFICATION_NOTE_PATH)

    assert "This note records the accepted current mediation justification decision." in text
    assert "Status: `justified for one bounded experimental mediation seam`" in text
    assert "The current accepted J2 package now shows:" in text
    assert "explicit but non-blocking gap" in text
    assert "Phase 16 mediation is now justified for one bounded experimental seam." in text
    assert "The next lawful move after this note is to plan and implement one bounded experimental mediation seam under those limits." in text


def test_verification_ergonomics_plan_reflects_current_campaign_state() -> None:
    text = _read(VERIFICATION_PLAN_PATH)

    assert "## Current Campaign State" in text
    assert "`E1` is effectively landed" in text
    assert "`E2` is effectively landed" in text
    assert "`E3` is materially landed for current scope" in text
    assert "`E4` is effectively landed for current scope" in text
    assert "`E5` is materially landed for current scope" in text
    assert "`E6` remains open." in text
    assert "the current repo begins with no repo-local coverage config" not in text
    assert "## 13. Current hold note" in text
    assert "`E2C` is now landed." in text
    assert "`E4` is now landed for current scope." in text
    assert "`E5` is materially landed for current scope." in text
    assert "post-`E4` re-audit is complete." in text
    assert "no `E6` seam is promoted at this time." in text
    assert "### Post-`E4` re-audit result" in text
    assert "No `E6` seam is promoted from this re-audit." in text
    assert "### E2C — first coverage baseline artifact" not in text


def test_coverage_baseline_note_exists() -> None:
    text = _read(COVERAGE_BASELINE_NOTE_PATH)

    assert "Status: first committed repo-local coverage baseline" in text
    assert "make coverage" in text
    assert "TOTAL" in text


def test_local_verification_doc_make_targets_exist_in_makefile() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    doc_targets = _extract_doc_make_targets(doc_text)
    make_targets = _extract_make_targets(makefile_text)

    assert doc_targets <= make_targets


def test_repo_workflow_doc_exists_and_agents_reference_it() -> None:
    workflow_text = _read(REPO_WORKFLOW_PATH)
    agents_text = _read(REPO_ROOT / "AGENTS.md")

    assert "Repo Workflow" in workflow_text
    assert "`main` is the resting branch" in workflow_text
    assert "python scripts/repo_workflow.py sync-main" in workflow_text
    assert "python scripts/repo_workflow.py start-session" in workflow_text
    assert "python scripts/repo_workflow.py close-session" in workflow_text
    assert "python scripts/repo_workflow.py finalize" in workflow_text
    assert "python scripts/repo_workflow.py preserve-worktree" in workflow_text
    assert "python scripts/repo_workflow.py audit-branches" in workflow_text
    assert "python scripts/repo_workflow.py cleanup-report" in workflow_text
    assert "`REPO_WORKFLOW.md` is the maintainer workflow authority" in agents_text
    assert "`scripts/repo_workflow.py` is the enforcing helper surface" in agents_text
    assert "`cleanup-report` is the strict final repo-hygiene gate" in agents_text
    assert "`main` is the resting branch in this repository." in agents_text
    assert "archival-root only" not in agents_text


def test_seam_preflight_target_and_doc_contract_exist() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    make_recipe = _extract_make_recipe(makefile_text, "seam-preflight")

    assert "make seam-preflight" in doc_text
    assert "git branch --show-current" in doc_text
    assert "git rev-list --left-right --count main...origin/main" in doc_text
    assert "git status --short --untracked-files=all" in doc_text
    assert "classify seam risk before opening new work" in doc_text
    assert "require repeated reruns before acceptance" in doc_text
    assert "git branch --show-current" in make_recipe
    assert "git status --short --untracked-files=all" in make_recipe
    assert "grep -v '^?? '" in make_recipe
    assert "tracked worktree changes must be accepted or committed before a new seam" in make_recipe
    assert "classify seam risk as deterministic code/doc" in make_recipe
    assert "require repeated reruns before acceptance" in make_recipe


def test_canonical_bundle_block_matches_verify_recipe_logically() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    doc_block = _normalize_shell_block(_extract_sh_block(doc_text, "Canonical bundle"))
    make_recipe = _expand_make_vars(
        _extract_make_recipe(makefile_text, "verify"), makefile_text
    )

    assert doc_block == make_recipe


def test_smoke_bundle_block_matches_test_smoke_recipe_logically() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    doc_block = _normalize_shell_block(_extract_sh_block(doc_text, "Smoke bundle"))
    make_recipe = _expand_make_vars(
        _extract_make_recipe(makefile_text, "test-smoke"), makefile_text
    )

    assert doc_block == make_recipe


def test_local_verification_doc_points_to_committed_coverage_baseline() -> None:
    text = _read(LOCAL_VERIFICATION_PATH)

    assert "docs/CORTEX_V2_COVERAGE_BASELINE_NOTE_0.md" in text
    assert "Coverage is still not part of the canonical local verification bundle." in text
    assert "no coverage threshold or pass/fail gate" in text


def test_live_preflight_entrypoint_is_bounded_and_matches_makefile() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    assert "python3 tools/live_preflight.py --skip-updates" in doc_text
    assert "make live-preflight-update" in doc_text
    assert "repo-local entry point is intentionally non-mutating" in doc_text
    assert "Use the direct script without `--skip-updates` only when you explicitly want to try the updater path." in doc_text

    make_recipe = _expand_make_vars(
        _extract_make_recipe(makefile_text, "live-preflight"), makefile_text
    )
    assert make_recipe == "python3 tools/live_preflight.py --skip-updates"
    update_recipe = _expand_make_vars(
        _extract_make_recipe(makefile_text, "live-preflight-update"), makefile_text
    )
    assert update_recipe == "python3 tools/live_preflight.py"


def test_local_verification_doc_records_repo_workflow_commands() -> None:
    doc_text = _read(LOCAL_VERIFICATION_PATH)

    assert "## Maintainer workflow" in doc_text
    assert "python scripts/repo_workflow.py sync-main" in doc_text
    assert "python scripts/repo_workflow.py start-session --agent codex --slug task-name" in doc_text
    assert 'python scripts/repo_workflow.py close-session --message "docs: end-state summary"' in doc_text
    assert 'python scripts/repo_workflow.py finalize --message "docs: manual branch closeout"' in doc_text
    assert "python scripts/repo_workflow.py preserve-worktree --slug root-e1-verification" in doc_text
    assert "python scripts/repo_workflow.py audit-branches" in doc_text
    assert "python scripts/repo_workflow.py cleanup-report" in doc_text
    assert "make repo-hygiene" in doc_text
    assert "keep the current explicit stable models unless a separate host-defaults seam is explicitly opened" in doc_text
    assert "## Operator routing realization" in doc_text
    assert "python3 -m pytest tests/unit/test_operator_routing.py -q" in doc_text
    assert "python3 -m pytest tests/unit/test_sre_executive_summary.py -q" in doc_text
    assert "python3 -m pytest tests/unit/test_sre_modulators.py -q" in doc_text
    assert "python3 -m pytest tests/unit/test_sre_policy_view.py -q" in doc_text
    assert "python3 -m pytest tests/unit/test_correspondence_sre.py -q" in doc_text
    assert "python3 tools/mediation_evidence_package.py --check" in doc_text


def test_resume_protocol_and_active_workstream_contract_exist() -> None:
    agents_text = _read(REPO_ROOT / "AGENTS.md")
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    accepted_branch = _extract_accepted_workflow_baseline(workstream_text)

    assert "## Continuation and resume protocol" in agents_text
    assert "`docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in agents_text
    assert "git branch --show-current" in agents_text
    assert "git status --short --untracked-files=all" in agents_text
    assert "Never promote uncommitted local edits to accepted baseline truth." in agents_text

    assert "Status: live workflow-state ledger for compaction-safe continuation." in workstream_text
    assert f"Accepted baseline branch: `{accepted_branch}`" in workstream_text
    assert "Accepted baseline commit lookup: `git rev-parse HEAD` on clean synced `main`" in workstream_text
    assert "exact accepted-head hashes are intentionally not mirrored in repo-tracked support docs" in workstream_text
    assert "Current campaign:" in workstream_text
    assert "Current working branch at ledger update:" in workstream_text
    assert "Current branch role:" in workstream_text
    assert "Current campaign: `OA1 OpenAI canonical API truth anchor`" in workstream_text
    assert "Current working branch at ledger update: `review/oa1-openai-canonical-anchor`" in workstream_text
    assert "Current branch role: explicit manual/review branch because local `main` is ahead of `origin/main`; accepted baseline truth remains the clean local `main` line" in workstream_text
    assert "Current candidate seam: `OA1 OpenAI canonical direct-API truth anchor`" in workstream_text
    assert "`service_api` is the canonical runtime truth lane" in workstream_text
    assert "`operator_cli` is a watchlist and exploratory-comparison lane" in workstream_text
    assert "Claude: positive watchlist signal" in workstream_text
    assert "Gemini: unresolved watchlist signal" in workstream_text
    assert "OpenAI: positive watchlist signal" in workstream_text
    assert "review branches such as `review/gemini-cause-proof` remain evidence only and are not accepted runtime truth" in workstream_text
    assert "Do not treat signed-in provider CLI sessions as canonical runtime truth." in workstream_text
    assert "Do not let CLI-only positives promote accepted product/runtime claims." in workstream_text
    assert "Do not shell out from service transports to provider CLIs." in workstream_text
    assert "git branch --show-current" in workstream_text
    assert "git status --short --untracked-files=all" in workstream_text
    assert "Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth." in workstream_text


def test_reference_runtime_program_lock_is_recorded() -> None:
    program_text = _read(REFERENCE_RUNTIME_PROGRAM_PATH)
    feedback_program_text = _read(REFERENCE_FEEDBACK_PROGRAM_PATH)
    feedback_program_1_text = _read(REFERENCE_FEEDBACK_PROGRAM_1_PATH)
    continuity_program_text = _read(REFERENCE_CONTINUITY_PROGRAM_PATH)
    openai_runtime_program_text = _read(OPENAI_RUNTIME_PROGRAM_PATH)
    openai_ingress_program_text = _read(OPENAI_INGRESS_PROGRAM_PATH)
    openai_service_program_text = _read(OPENAI_SERVICE_PROGRAM_PATH)
    openai_host_control_program_text = _read(OPENAI_HOST_CONTROL_PROGRAM_PATH)
    executive_live_outcome_program_text = _read(EXECUTIVE_LIVE_OUTCOME_PROGRAM_PATH)
    computed_executive_loop_program_text = _read(COMPUTED_EXECUTIVE_LOOP_PROGRAM_PATH)
    closed_loop_enforcement_program_text = _read(CLOSED_LOOP_ENFORCEMENT_PROGRAM_PATH)
    operator_directionality_program_text = _read(OPERATOR_DIRECTIONALITY_PROGRAM_PATH)
    operator_directionality_scenario_catalog_text = _read(OPERATOR_DIRECTIONALITY_SCENARIO_CATALOG_PATH)
    operator_directionality_audit_text = _read(OPERATOR_DIRECTIONALITY_AUDIT_PATH)
    operator_routing_program_text = _read(OPERATOR_ROUTING_PROGRAM_PATH)
    mediation_host_realization_program_text = _read(
        MEDIATION_HOST_REALIZATION_PROGRAM_PATH
    )
    gemini_runtime_restack_text = _read(GEMINI_RUNTIME_RESTACK_PROGRAM_PATH)
    gemini_runtime_program_text = _read(GEMINI_RUNTIME_PROGRAM_PATH)
    gemini_ingress_program_text = _read(GEMINI_INGRESS_PROGRAM_PATH)
    gemini_service_program_text = _read(GEMINI_SERVICE_PROGRAM_PATH)
    gemini_host_control_program_text = _read(GEMINI_HOST_CONTROL_PROGRAM_PATH)
    phase_gate_text = _read(PHASE_GATES_PATH)
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)

    assert "reference-host-only runtime program" in program_text
    assert "`python3 -m cortex.runtime.reference_cli`" in program_text
    assert "JSONL input and JSONL output only" in program_text
    assert "no service/API shell" in program_text
    assert "no Gemini runtime" in program_text
    assert "no OpenAI runtime" in program_text
    assert "no AUX runtime activation" in program_text
    assert "no mediation implementation" in program_text

    assert "## 6. Post-closeout runtime-program gates" in phase_gate_text
    assert "`R1` reference runtime shell" in phase_gate_text
    assert "`R2` computed reference executive slice" in phase_gate_text
    assert "`R3` reference live continuity slice" in phase_gate_text
    assert "`R4` reference closed-loop feedback and latched-brake slice" in phase_gate_text
    assert "`R5` reference short-window feedback and sustained-pressure slice" in phase_gate_text
    assert "the first accepted reference-host local CLI shell is landed" in phase_gate_text
    assert "the first bounded `X_t^{ref}` builder, `U_t^{sre}` scoring/selection layer, and runtime-shell integration are landed" in phase_gate_text
    assert "re-hardened and audit-clean for current scope" in phase_gate_text
    assert "malformed `open` and session mismatch are explicit" in phase_gate_text
    assert "feedback-conditioned builder update, top-level control ledger, and latched-brake enforcement are landed and audit-clean for current scope" in phase_gate_text
    assert "the first bounded three-step realized-outcome window" in phase_gate_text
    assert "the corrective line now closes the surviving session/window carrier defect" in phase_gate_text
    assert "`C1` reference bounded cross-process continuation slice" in phase_gate_text
    assert "explicit persisted `continuity_truth` plus bounded `control_residue` are landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`" in phase_gate_text
    assert "`O1` OpenAI documented host-event runtime shell" in phase_gate_text
    assert "raw documented host events drive a host-specific CLI shell" in phase_gate_text
    assert "canonical Cortex event names are explicitly rejected" in phase_gate_text
    assert "diagnostic-history non-equivalence" in phase_gate_text
    assert "| closed | landed |" in phase_gate_text
    assert "landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f`" in phase_gate_text
    assert "`O2` OpenAI raw-transcript ingress shell" in phase_gate_text
    assert "wrapper-shaped and mixed wrapper/transcript records are explicitly rejected" in phase_gate_text
    assert "mixed wrapper/transcript records are explicitly rejected" in phase_gate_text
    assert "`O3` OpenAI loopback service shell" in phase_gate_text
    assert "loopback-only HTTP is landed on the accepted K1 closeout line" in phase_gate_text
    assert "one active session per process is real for current scope" in phase_gate_text

    assert "Current campaign: `OA1 OpenAI canonical API truth anchor`" in workstream_text
    assert "Current candidate seam: `OA1 OpenAI canonical direct-API truth anchor`" in workstream_text
    assert "`service_api` is the canonical runtime truth lane" in workstream_text
    assert "`operator_cli` is a watchlist and exploratory-comparison lane" in workstream_text
    assert "## 8. Mediation justification gate" in phase_gate_text
    assert "`J3` mediation justification review" in phase_gate_text
    assert "one bounded experimental mediation seam" in phase_gate_text
    assert "## 9. Mediation implementation gate" in phase_gate_text
    gate_9_match = re.search(
        r"## 9\. Mediation implementation gate\n(?P<section>.*?)(?:\n## |\Z)",
        phase_gate_text,
        re.S,
    )
    assert gate_9_match is not None
    assert "Overall status: `landed`" in gate_9_match.group("section")
    assert "`J4B` reference `seek-context` reachability slice" in phase_gate_text
    assert "`J4C` reference experimental host-realization finalizer" in phase_gate_text
    assert "`J4D` runtime-backed reference mediation evidence closure" in phase_gate_text
    assert "`J4F` workflow closeout and hygiene" in phase_gate_text
    assert "first bounded experimental mediation slice" in mediation_host_realization_program_text
    assert "The first mediation implementation should be a **host-realization seam**" in mediation_host_realization_program_text
    assert "This program-lock seam is `non-load-bearing`." in mediation_host_realization_program_text
    assert "Correspondence impact: none expected." in mediation_host_realization_program_text
    assert "one bounded `seek-context` reachability adjustment on explicit missing-context / missing-capability pressure" in mediation_host_realization_program_text
    assert "`J4B` is `load-bearing`." in mediation_host_realization_program_text
    assert "the builder now admits `seek-context` into the family mask and top-family set only on exact `missing-capability`, `capability-view-missing`, or `execution-trace-missing` pressure" in mediation_host_realization_program_text
    assert "the scorer now uses the same exact-pressure predicate rather than a generic `*-missing` heuristic" in mediation_host_realization_program_text
    assert "the reference runtime lane now selects `seek-context` end-to-end on the capability-view-missing path" in mediation_host_realization_program_text
    assert "`J4C` is `load-bearing`." in mediation_host_realization_program_text
    assert "add one new `Q_t^{final}(a)` experimental mediation-finalizer row" in mediation_host_realization_program_text
    assert "updated the `Q_t^{online}(a)` / `Q_t^{alloc}(a)` realization row so the same exact-pressure path now clears neutral dominance on the runtime lane" in mediation_host_realization_program_text
    assert "Do not open `Q_t^{final}` inside `J4B` just to compensate for a pre-selection reachability gap." in mediation_host_realization_program_text
    assert "`python3 -m cortex.runtime.reference_cli --mediation-mode {identity,host-realization-experimental}`" in mediation_host_realization_program_text
    assert "Current accepted state after `J4F` closeout" in mediation_host_realization_program_text
    assert "`J4B` is now accepted baseline truth on `main`" in mediation_host_realization_program_text
    assert "`J4C` is now landed as an off-by-default reference finalizer" in mediation_host_realization_program_text
    assert "`J4D` now replaces the old reference specialization helper fiction" in mediation_host_realization_program_text
    assert "`J4E` is explicitly declined for the current closeout unless a later post-closeout review reopens a real truth gap" in mediation_host_realization_program_text
    assert "`J4F` is now landed: workflow truth, phase-gate truth, correspondence truth, and branch truth are reconciled together on clean synced `main`." in mediation_host_realization_program_text
    assert "Minimum deterministic proof for each opened load-bearing stage:" in mediation_host_realization_program_text
    assert "Do not reopen mediation, AUX runtime widening, support-memory runtime, or broader doctrine work during this reset." in workstream_text
    assert "the first one-process live continuity slice plus explicit rejection enforcement are real" in program_text
    assert "the corrective zero-finding re-audit has passed for current scope" in program_text
    assert "a mismatched runtime `session_id` is surfaced as an explicit contradiction" in program_text
    assert "first bounded reference closed-loop feedback slice" in feedback_program_text
    assert "top-level control ledger in the runtime output surface" in feedback_program_text
    assert "bounded latched-brake enforcement point" in feedback_program_text
    assert "`R4B` realization-feedback carrier and persistence" in feedback_program_text
    assert "`R4E` latched-brake enforcement" in feedback_program_text
    assert "Current accepted state after K1 closeout" in feedback_program_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in feedback_program_text
    assert "CLI-visible selected-vs-realized divergence" in feedback_program_text
    assert "zero-finding adversarial runtime/API review found no defect for current scope" in feedback_program_text
    assert "first bounded reference short-window feedback slice" in feedback_program_1_text
    assert "branch: `codex/j2-restack-acceptance-truth-normalization`" in feedback_program_1_text
    assert "commit: `acfccf9`" in feedback_program_1_text
    assert "Historical `R4` source lineage still carried into this program:" in feedback_program_1_text
    assert "`ReferenceRealizationFeedbackWindow`" in feedback_program_1_text
    assert "`ReferenceFeedbackWindowSummary`" in feedback_program_1_text
    assert "maximum length `3`" in feedback_program_1_text
    assert "feedback_window_summary" in feedback_program_1_text
    assert "session_summary.feedback_window_size" in feedback_program_1_text
    assert "This program does **not** authorize:" in feedback_program_1_text
    assert "a scoring rewrite" in feedback_program_1_text
    assert "`R5B` feedback window carrier and session persistence" in feedback_program_1_text
    assert "`R5E` re-audit and closeout" in feedback_program_1_text
    assert "Current accepted state after K1 closeout" in feedback_program_1_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in feedback_program_1_text
    assert "committed end-to-end proof now exists at `ee41eb4`" in feedback_program_1_text
    assert "the accepted landed donor closeout for the historical `R5` line is still anchored at `fd6789f`" in feedback_program_1_text
    assert "Historical corrective source state" in feedback_program_1_text
    assert "codex/r5g-h-corrective-reclosure" in feedback_program_1_text
    assert "last-step mirror with empty window becomes a one-entry bounded window" in feedback_program_1_text
    assert "the direct-construction reproduction that dropped next-step pressure is now closed" in feedback_program_1_text
    assert "top-level `feedback_window_summary`" in feedback_program_1_text
    assert "single-mismatch `0.55` floor" in feedback_program_1_text
    assert "repeated-mismatch `0.70` floor" in feedback_program_1_text
    assert "accepted re-audited runtime-program brief for the first bounded reference cross-process continuation slice" in continuity_program_text
    assert "`--load-session PATH`" in continuity_program_text
    assert "`--save-session PATH`" in continuity_program_text
    assert "`continuity_truth`" in continuity_program_text
    assert "`control_residue`" in continuity_program_text
    assert "`C1` equivalence does **not** require:" in continuity_program_text
    assert "`make revalidate-reference-runtime-continuity`" in continuity_program_text
    assert "Current accepted state after K1 closeout" in continuity_program_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in continuity_program_text
    assert "accepted re-audited runtime-program brief for the first OpenAI documented host-event runtime shell" in openai_runtime_program_text
    assert "`python3 -m cortex.runtime.openai_cli`" in openai_runtime_program_text
    assert "`raw_host_event_name`" in openai_runtime_program_text
    assert "`make revalidate-openai-runtime`" in openai_runtime_program_text
    assert "canonical Cortex event names are now explicitly rejected at both CLI and runtime entrypoint level" in openai_runtime_program_text
    assert "runtime and session I/O ownership remain self-contained inside the OpenAI runtime modules" in openai_runtime_program_text
    assert "Current accepted state after K1 closeout" in openai_runtime_program_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in openai_runtime_program_text
    assert "accepted re-audited runtime-program brief for the first OpenAI raw-transcript ingress shell" in openai_ingress_program_text
    assert "`python3 -m cortex.runtime.openai_ingress_cli`" in openai_ingress_program_text
    assert "wrapper-shape `{event_name, payload}` records are explicitly rejected" in openai_ingress_program_text
    assert "mixed wrapper/transcript record that contains `event_name` or `payload`" in openai_ingress_program_text
    assert "`make revalidate-openai-ingress`" in openai_ingress_program_text
    assert "Current accepted state after K1 closeout" in openai_ingress_program_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in openai_ingress_program_text
    assert "accepted re-audited runtime-program brief for the first OpenAI loopback service shell" in openai_service_program_text
    assert "`python3 -m cortex.runtime.openai_service`" in openai_service_program_text
    assert "`GET /health`" in openai_service_program_text
    assert "`POST /v1/events`" in openai_service_program_text
    assert "`GET /v1/session/export`" in openai_service_program_text
    assert "`POST /v1/session/import`" in openai_service_program_text
    assert "`make revalidate-openai-service`" in openai_service_program_text
    assert "Current accepted state after K1 closeout" in openai_service_program_text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in openai_service_program_text
    assert "are now landed `O3` surfaces" in openai_service_program_text
    assert "same module may host a separately scoped outbound control lane" in openai_service_program_text

    assert "Status: accepted re-audited runtime-program brief for the first bounded outbound OpenAI host-control lane" in openai_host_control_program_text
    assert "branch: `codex/k1f-openai-service-closeout`" in openai_host_control_program_text
    assert "commit: `79b8f39`" in openai_host_control_program_text
    assert "`POST /v1/actions/response-stream`" in openai_host_control_program_text
    assert "`OpenAIHostControlRequest`" in openai_host_control_program_text
    assert "`OpenAIHostControlResult`" in openai_host_control_program_text
    assert "strict-whitelist and text-only" in openai_host_control_program_text
    assert "The public K2 surface remains:" in openai_host_control_program_text
    assert "canonical tests require no live OpenAI network" in openai_host_control_program_text
    assert "`make revalidate-openai-host-control`" in openai_host_control_program_text
    assert "Current accepted state after K2 closeout" in openai_host_control_program_text
    assert "implemented at K2 proof head `5ed9549` and truthfully closed at deterministic closeout head `9ed7dae`" in openai_host_control_program_text
    assert "`O4` OpenAI bounded outbound host-control lane" in phase_gate_text
    assert "cleanly closed at deterministic closeout head `9ed7dae`" in phase_gate_text
    assert "`R6` explicit executive allocation slice on the reference runtime shell" in phase_gate_text
    assert "`O5` OpenAI executive allocation projection slice" in phase_gate_text
    assert "`R7` reference computed executive loop" in phase_gate_text
    assert "`O6` OpenAI computed executive loop projection slice" in phase_gate_text
    assert "`R8` reference feedback-conditioned intervention threshold" in phase_gate_text
    assert "`O7` OpenAI feedback-conditioned threshold projection slice" in phase_gate_text
    assert "`R9` reference enforcement-aware realized control loop" in phase_gate_text
    assert "`O8` OpenAI enforcement-aware realized projection slice" in phase_gate_text

    assert "Status: active runtime-program brief for the first explicit executive live-outcome allocation slice" in executive_live_outcome_program_text
    assert "branch: `codex/k2-openai-host-control`" in executive_live_outcome_program_text
    assert "commit: `9ed7dae`" in executive_live_outcome_program_text
    assert "nested `control_ledger.allocation_diagnostics`" in executive_live_outcome_program_text
    assert "`Q_t^{mem}=0.0`" in executive_live_outcome_program_text
    assert "`alpha_t=1.0`" in executive_live_outcome_program_text
    assert "`allocated_score=online_score`" in executive_live_outcome_program_text
    assert "`make revalidate-executive-loop`" in executive_live_outcome_program_text
    assert "Current K3 candidate state before closeout" in executive_live_outcome_program_text
    assert "Status: accepted re-audited runtime-program brief for the first bounded computed executive loop on proven reference/OpenAI lanes" in computed_executive_loop_program_text
    assert "`Q_t^{mem}=0.0`" in computed_executive_loop_program_text
    assert "`allocated_score` may differ from `online_score`" in computed_executive_loop_program_text
    assert "No new public shells are introduced." in computed_executive_loop_program_text
    assert "Current accepted state after K4 closeout" in computed_executive_loop_program_text
    assert "Status: accepted re-audited runtime-program brief for the bounded closed-loop feedback and enforcement train on proven reference/OpenAI lanes" in closed_loop_enforcement_program_text
    assert "feedback-conditioned intervention-threshold law" in closed_loop_enforcement_program_text
    assert "guarded-feedback enforcement may conservatively realize `check` or `neutral`" in closed_loop_enforcement_program_text
    assert "`Q_t^{mem}=0.0`" in closed_loop_enforcement_program_text
    assert "Current accepted state after K-train closeout" in closed_loop_enforcement_program_text
    assert "Status: accepted watchlist-evaluation brief for raw-vs-Cortex operator comparison" in operator_directionality_program_text
    assert "raw-host vs Cortex-operator" in operator_directionality_program_text
    assert "`execution_surface = headless_cli`" in operator_directionality_program_text
    assert "`evidence_role = watchlist`" in operator_directionality_program_text
    assert "The Gemini operator harness may use:" in operator_directionality_program_text
    assert "`--cortex-execution-flavor minimal`" in operator_directionality_program_text
    assert "They do not authorize product default changes by themselves." in operator_directionality_program_text
    assert "Status: accepted watchlist scenario catalog for the raw-vs-Cortex operator audit" in operator_directionality_scenario_catalog_text
    assert "`execution_surface = headless_cli`" in operator_directionality_scenario_catalog_text
    assert "`evidence_role = watchlist`" in operator_directionality_scenario_catalog_text
    assert "`pass_minimal`" in operator_directionality_scenario_catalog_text
    assert "`truth_gap`" in operator_directionality_scenario_catalog_text
    assert "`restart_continuity`" in operator_directionality_scenario_catalog_text
    assert "Status: active runtime-program brief for the first bounded SRE-owned operator routing train" in operator_routing_program_text
    assert "one bounded SRE + harness train" in operator_routing_program_text
    assert "one SRE-owned operator route selector over low-dimensional task-state geometry" in operator_routing_program_text
    assert "This document does not authorize:" in operator_routing_program_text
    assert "named model routing" in operator_routing_program_text
    assert "Locked route profiles:" in operator_routing_program_text
    assert "`inspect_light`" in operator_routing_program_text
    assert "`blocked`" in operator_routing_program_text
    assert "one compact executive summary over observable control inputs" in operator_routing_program_text
    assert "one compact tonic executive modulator bundle over that summary" in operator_routing_program_text
    assert "one compact executive policy view derived from summary + modulators" in operator_routing_program_text
    assert "The summary layer uses:" in operator_routing_program_text
    assert "The modulator layer uses:" in operator_routing_program_text
    assert "The policy layer uses:" in operator_routing_program_text
    assert "`focus_gain`" in operator_routing_program_text
    assert "`explore_gain`" in operator_routing_program_text
    assert "`stop_pressure`" in operator_routing_program_text
    assert "`update_pressure`" in operator_routing_program_text
    assert "`default_profile_bonus`" in operator_routing_program_text
    assert "`switch_margin`" in operator_routing_program_text
    assert "`stop_threshold`" in operator_routing_program_text
    assert "`verification_intensity`" in operator_routing_program_text
    assert "The route selector may choose:" in operator_routing_program_text
    assert "retry budget" in operator_routing_program_text
    assert "The modulator layer may change:" in operator_routing_program_text
    assert "one extra read pass on inspect routes" in operator_routing_program_text
    assert "The policy layer is the only place where those behavior consequences should be expressed." in operator_routing_program_text
    assert "It may not choose:" in operator_routing_program_text
    assert "named models" in operator_routing_program_text
    assert "Required local artifact diagnostics:" in operator_routing_program_text
    assert "`route_profile`" in operator_routing_program_text
    assert "`blocked_reason`" in operator_routing_program_text
    assert "`modulator_summary`" in operator_routing_program_text
    assert "`modulator_memory`" in operator_routing_program_text
    assert "`modulator_state`" in operator_routing_program_text
    assert "`modulator_reason_tags`" in operator_routing_program_text
    assert "`policy_view`" in operator_routing_program_text
    assert "Minimum deterministic proof:" in operator_routing_program_text
    assert "`python3 -m pytest tests/unit/test_operator_routing.py -q`" in operator_routing_program_text
    assert "`python3 -m pytest tests/unit/test_sre_executive_summary.py -q`" in operator_routing_program_text
    assert "`python3 -m pytest tests/unit/test_sre_modulators.py -q`" in operator_routing_program_text
    assert "`python3 -m pytest tests/unit/test_sre_policy_view.py -q`" in operator_routing_program_text
    assert "the implementation stays abstract and does not use neurotransmitter names as code objects" in operator_routing_program_text
    assert "`route_budget.max_turns` is the outer harness turn budget" in operator_routing_program_text
    assert "dopamine" not in operator_routing_program_text.lower()
    assert "serotonin" not in operator_routing_program_text.lower()
    assert "Status: accepted watchlist note for paired raw-vs-Cortex operator directionality" in operator_directionality_audit_text
    assert "`execution_surface = headless_cli`" in operator_directionality_audit_text
    assert "`evidence_role = watchlist`" in operator_directionality_audit_text
    assert "Claude: positive watchlist signal" in operator_directionality_audit_text
    assert "OpenAI: positive watchlist signal" in operator_directionality_audit_text
    assert "Gemini: unresolved watchlist signal on the accepted line" in operator_directionality_audit_text
    assert "review/gemini-cause-proof" in operator_directionality_audit_text
    assert "Do not read branch-local operator positives as accepted product truth." in operator_directionality_audit_text
    assert "`G1` Gemini documented host-event runtime shell" in phase_gate_text
    assert "`G2` Gemini raw-transcript ingress shell" in phase_gate_text
    assert "`G3` Gemini loopback service shell" in phase_gate_text
    assert "`G4` Gemini bounded outbound host-control lane" in phase_gate_text
    assert "Gemini-specific runtime/session carriers plus persisted artifact are landed on the accepted G1 closeout line" in phase_gate_text
    assert "Gemini raw-transcript ingress parsing is landed on the accepted G1 closeout line" in phase_gate_text
    assert "loopback-only Gemini HTTP is landed on the accepted G1 closeout line" in phase_gate_text
    assert "the first bounded outbound Gemini host-control lane is landed on the accepted G1 closeout line" in phase_gate_text
    assert "## 7. Live-validation gates" in phase_gate_text
    assert "`L1` Claude live validation" in phase_gate_text
    assert "`L1A` Claude hook-backed operator lifecycle proof" in phase_gate_text
    assert "`L2` Gemini live validation" in phase_gate_text
    assert "`L2A` Gemini hook-backed operator lifecycle proof" in phase_gate_text
    assert "`L3` OpenAI live validation" in phase_gate_text
    assert "`L3A` OpenAI App Server operator lifecycle proof" in phase_gate_text
    assert "`L4` lifecycle-first payoff verdict" in phase_gate_text
    assert "`L5` cross-host operator payoff audit" in phase_gate_text
    assert "`L6A` Claude service live proof" in phase_gate_text
    assert "`L6B` Gemini service live proof" in phase_gate_text
    assert "`L6C` OpenAI service live proof" in phase_gate_text
    assert "`L6D` package-level service proof" in phase_gate_text
    assert "These rows track the two-lane live-validation contract after the R1 reset." in phase_gate_text
    assert "Claude currently contributes positive watchlist evidence on the headless-CLI lane" in phase_gate_text
    assert "Gemini remains the noisiest headless-CLI watchlist line" in phase_gate_text
    assert "the bounded `codex app-server` operator lane remains re-earned as watchlist-only lifecycle evidence" in phase_gate_text
    assert "OpenAI direct-API canonical truth is now re-earned for current scope on this machine" in phase_gate_text
    assert "cross-host runtime payoff remains partial because Claude and Gemini are still unearned on the canonical lane" in phase_gate_text

    assert "Status: accepted re-audited support brief for the G1 runtime/product restack train" in gemini_runtime_restack_text
    assert "Gemini-only" in gemini_runtime_restack_text
    assert "Status: accepted re-audited runtime-program brief for the first Gemini documented host-event runtime shell" in gemini_runtime_program_text
    assert "`python3 -m cortex.runtime.gemini_cli`" in gemini_runtime_program_text
    assert "Status: accepted re-audited runtime-program brief for the first Gemini raw-transcript ingress shell" in gemini_ingress_program_text
    assert "`python3 -m cortex.runtime.gemini_ingress_cli`" in gemini_ingress_program_text
    assert "Status: accepted re-audited runtime-program brief for the first Gemini loopback service shell" in gemini_service_program_text
    assert "`python3 -m cortex.runtime.gemini_service`" in gemini_service_program_text
    assert "Status: accepted re-audited runtime-program brief for the first bounded outbound Gemini host-control lane" in gemini_host_control_program_text
    assert "`POST /v1/actions/interaction-stream`" in gemini_host_control_program_text

    live_validation_program_text = _read(LIVE_VALIDATION_PROGRAM_PATH)
    live_validation_scenario_catalog_text = _read(LIVE_VALIDATION_SCENARIO_CATALOG_PATH)
    live_validation_verdict_text = _read(LIVE_VALIDATION_VERDICT_PATH)
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    accepted_branch = _extract_accepted_workflow_baseline(workstream_text)

    assert "Status: active live-validation program under the R1 two-lane truth reset" in live_validation_program_text
    assert f"branch: `{accepted_branch}`" in live_validation_program_text
    assert "clean synced `main` line recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in live_validation_program_text
    assert "`service_api`" in live_validation_program_text
    assert "`operator_cli`" in live_validation_program_text
    assert "local-only under `.cortex/live_validation/`" in live_validation_program_text
    assert "the OpenAI direct-API canonical anchor is repeat-stably re-earned on the current machine" in live_validation_program_text
    assert "Status: active live-validation scenario catalog with the OpenAI canonical anchor recorded for current scope" in live_validation_scenario_catalog_text
    assert "`pass_minimal`" in live_validation_scenario_catalog_text
    assert "`restart_continuity`" in live_validation_scenario_catalog_text
    assert "`truth_gap`" in live_validation_scenario_catalog_text
    assert "`execution_surface = direct_api`" in live_validation_scenario_catalog_text
    assert "`execution_surface = headless_cli`" in live_validation_scenario_catalog_text
    assert "machine output: local-only under `.cortex/live_validation/`" in live_validation_scenario_catalog_text
    assert "Status: live-validation verdict note for the R1 two-lane reset" in live_validation_verdict_text
    assert "**canonical runtime truth is re-earned for current scope; operator truth remains watchlist-only**" in live_validation_verdict_text
    assert "`service_api`: `execution_surface = direct_api`, `evidence_role = canonical_truth`" in live_validation_verdict_text
    assert "`operator_cli`: `execution_surface = headless_cli`, `evidence_role = watchlist`" in live_validation_verdict_text
    service_proof_text = _read(LIVE_SERVICE_PROOF_PATH)
    assert "Status: active canonical-truth service-proof note with the first OpenAI anchor re-earned for current scope" in service_proof_text
    assert "`service_api` is the canonical runtime truth lane" in service_proof_text
    assert "`execution_surface = direct_api`" in service_proof_text
    assert "`evidence_role = canonical_truth`" in service_proof_text
    assert "Signed-in CLI sessions do **not** count as service-lane auth." in service_proof_text
    assert "Actual service proof belongs only on a machine that satisfies all of:" in service_proof_text
    assert "the first canonical three-scenario API truth anchor is therefore re-earned for current OpenAI scope on this machine" in service_proof_text
    assert "No future product/runtime claim may land from CLI-only proof." in service_proof_text


def test_openai_host_control_revalidation_entry_points_are_recorded() -> None:
    local_verification_text = _read(LOCAL_VERIFICATION_PATH)
    makefile_text = _read(MAKEFILE_PATH)

    assert "## OpenAI host-control revalidation" in local_verification_text
    assert "python3 -m pytest tests/unit/test_openai_host_control.py -q" in local_verification_text
    assert "python3 -m pytest tests/integration/test_openai_host_control_service.py -q" in local_verification_text
    assert "python3 -m pytest tests/integration/test_openai_host_control_continuity.py -q" in local_verification_text
    assert "Canonical K2 tests use the internal fixture transport and do not require a live OpenAI network or a real API key." in local_verification_text
    assert "make revalidate-openai-host-control" in local_verification_text
    assert "revalidate-openai-host-control:" in makefile_text
    assert "## Executive live-outcome revalidation" in local_verification_text
    assert "feedback-conditioned `activation_threshold`" in local_verification_text
    assert "guarded/latched enforcement-aware realized control behavior" in local_verification_text
    assert "make revalidate-executive-loop" in local_verification_text
    assert "revalidate-executive-loop:" in makefile_text
    assert "python3 -m pytest tests/unit/test_reference_executive_builder.py -q" in local_verification_text
    assert "python3 -m pytest tests/unit/test_openai_runtime_step.py -q" in local_verification_text
    assert "python3 -m pytest tests/integration/test_reference_runtime_continuity.py -q" in local_verification_text
    assert "python3 -m pytest tests/integration/test_openai_runtime_continuity.py -q" in local_verification_text
    assert "## Gemini runtime revalidation" in local_verification_text
    assert "make revalidate-gemini-runtime" in local_verification_text
    assert "## Gemini ingress revalidation" in local_verification_text
    assert "make revalidate-gemini-ingress" in local_verification_text
    assert "## Gemini loopback service revalidation" in local_verification_text
    assert "make revalidate-gemini-service" in local_verification_text
    assert "## Gemini host-control revalidation" in local_verification_text
    assert "make revalidate-gemini-host-control" in local_verification_text
    assert "revalidate-gemini-runtime:" in makefile_text
    assert "revalidate-gemini-ingress:" in makefile_text
    assert "revalidate-gemini-service:" in makefile_text
    assert "revalidate-gemini-host-control:" in makefile_text
    assert "## Live-validation preflight" in local_verification_text
    assert "make live-preflight" in local_verification_text
    assert "## Live provider baselines" in local_verification_text
    assert "make live-provider-baselines" in local_verification_text
    assert "make live-provider-baselines-automation" in local_verification_text
    assert "automation baseline now exits with explicit auth-readiness blockers" in local_verification_text
    assert "## Live host-native product paths" in local_verification_text
    assert "make live-host-native-product-paths" in local_verification_text
    assert "For Claude and Gemini, the operator lane now records documented hook events" in local_verification_text
    assert "For Gemini `restart_continuity`, the inspect-only first turn now uses the lighter `plan` approval mode" in local_verification_text
    assert "## Live OpenAI App Server operator proof" in local_verification_text
    assert "make live-openai-app-server" in local_verification_text
    assert "## Live Cortex host-control capture" in local_verification_text
    assert "make live-cortex-host-control" in local_verification_text
    assert "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite current" in local_verification_text
    assert "python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor" in local_verification_text
    assert "compare and retained watchlist support surfaces preserve accepted watchlist context explicitly" in local_verification_text
    assert "## Live comparison and verdict" in local_verification_text
    assert "make live-compare" in local_verification_text
    assert "## Live operator payoff audit" in local_verification_text
    assert "make live-operator-payoff-audit" in local_verification_text
    assert "## Live operator directionality" in local_verification_text
    assert "make live-operator-directionality" in local_verification_text
    assert "## Live operator directionality audit" in local_verification_text
    assert "make live-operator-directionality-audit" in local_verification_text
    assert "live-preflight:" in makefile_text
    assert "live-provider-baselines:" in makefile_text
    assert "live-provider-baselines-automation:" in makefile_text
    assert "live-host-native-product-paths:" in makefile_text
    assert "live-openai-app-server:" in makefile_text
    assert "live-cortex-host-control:" in makefile_text
    assert "live-compare:" in makefile_text
    assert "live-operator-payoff-audit:" in makefile_text
    assert "live-operator-directionality:" in makefile_text
    assert "live-operator-directionality-audit:" in makefile_text


def test_erika_visualizations_are_framed_as_support_surfaces() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    markdown_text = _read(ERIKA_VISUALIZATION_STATUS_PATH)
    html_text = _read(ERIKA_VISUALIZATION_HTML_PATH)
    accepted_branch = _extract_accepted_workflow_baseline(workstream_text)

    assert "support surface" in markdown_text
    assert "current accepted repo truth" in markdown_text
    assert "north-star product target" in markdown_text
    assert "lawful gap programs" in markdown_text
    assert "mechanisms Cortex has already stolen so far" in markdown_text
    assert (
        f"**Accepted factual baseline:** clean synced `{accepted_branch}` line recorded in "
        "`docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`"
    ) in markdown_text
    assert "The verification/evidence restack train, K1 runtime/product restack, and K2 bounded host-control train are now landed for current scope on top of that same product truth." in markdown_text
    assert "The reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound OpenAI host-control lane are now accepted on the current line." in markdown_text
    assert "The Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane are now accepted on the current line." in markdown_text
    assert "operator-only payoff audit is now landed for current scope, and the deeper Gemini operator lane has now been re-earned on CLI auto mode before the remaining service-proof blockers." in markdown_text
    assert "Codex rather than `openai` as the OpenAI operator surface" in markdown_text
    assert "distinguishes `codex exec` smoke from `codex app-server` lifecycle proof" in markdown_text
    assert "now records documented hook events on Claude and Gemini" in markdown_text
    assert "operator probe and smoke baselines are now clean in CLI auto mode" in markdown_text
    assert "`gemini-2.5-pro` is valid but capacity-blocked on smoke" in markdown_text
    assert "A bounded feedback-conditioned threshold and enforcement-aware realized control loop is now also landed on the proven reference/OpenAI lanes" in markdown_text
    assert "broader or stronger closed-loop enforcement beyond the proven reference/OpenAI lanes" in markdown_text
    assert "closed-loop feedback and enforcement program" not in markdown_text
    assert "cortex-archival-dossiers/" not in markdown_text
    assert "Current Justified Boundary" in html_text
    assert "Gap Programs" in html_text
    assert "North-Star Cortex" in html_text
    assert "support surface" in html_text
    assert "not active authority" in html_text
    assert "not current committed roadmap truth" in html_text
    assert "Biology Tracker: What Cortex Has Stolen So Far" in html_text
    assert "which brain-inspired mechanisms Cortex has already stolen so far" in html_text
    assert (
        f"The accepted factual baseline is the clean synced <code>{accepted_branch}</code> "
        "line recorded in <code>docs/CORTEX_V2_ACTIVE_WORKSTREAM.md</code>."
    ) in html_text
    assert '<details class="biology-card"' in html_text
    assert "What we've stolen so far" in html_text
    assert "What is still partial" in html_text
    assert "What remains north-star only" in html_text
    assert "signed-in-first live testing environment with App Server and hook lifecycle proof" in html_text
    assert "broader or stronger lawful enforcement beyond proven lanes" in html_text
    assert "closed-loop feedback and enforcement" not in html_text
    assert "Cortex Complete" not in html_text
    assert "Today vs Future" not in html_text


def test_runtime_restack_program_lock_is_recorded() -> None:
    text = _read(RUNTIME_RESTACK_PROGRAM_PATH)
    master_plan_text = _read(REPO_ROOT / "docs" / "CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md")
    theory_text = _read(REPO_ROOT / "docs" / "CORTEX_V2_THEORY_2.md")

    assert "Status: accepted re-audited support brief for the K1 runtime/product restack train" in text
    assert "branch: `codex/j2-restack-acceptance-truth-normalization`" in text
    assert "commit: `acfccf9`" in text
    assert "The donor runtime branches are source material only:" in text
    assert "`codex/o3-openai-service-shell`" in text
    assert "They may not contribute workflow truth wholesale:" in text
    assert "not `AGENTS.md`" in text
    assert "not active workstream truth" in text
    assert "reference runtime foundation" in text
    assert "OpenAI loopback service shell" in text
    assert "Current accepted state after K1 closeout" in text
    assert "implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39`" in text
    assert "later bounded runtime/product trains may still be explicitly opened" in master_plan_text
    assert "one bounded experimental seam is now justified" in master_plan_text
    assert "records the bounded K train as landed" in theory_text
    assert "mediation is justified for one bounded experimental seam" in theory_text
    assert "headless operator reruns still require `GEMINI_API_KEY` in the shell environment" in theory_text
    assert "old `plan`-mode path was a real confound" in theory_text
    assert "repeated paired runs on the free API-key lane still turn mixed under flash-tier quota pressure" in theory_text
    assert "the operator/evaluation harness must not call explicit Gemini model names at all" in theory_text
    assert "fresh auto-only product-path rerun is sharper still" in theory_text
    assert "first full round-2 stable-defaults rerun now says the package is still `mixed_direction`" in theory_text
    assert "docs/CORTEX_V2_ACTIVE_WORKSTREAM.md` now records the bounded K train as landed, records `N2` as blocked pending a capable machine, records `M2`, `J1`, `J2`, `J3`, and the full bounded reference mediation closeout `J4B/J4C/J4D/J4F` on `main`" in theory_text
    assert "keeps non-reference mediated artifacts evidence-only." in theory_text
    assert "keeps non-reference mediated artifacts evidence-only." in theory_text
    assert "The clean synced `main` line now carries the provider-limit neutrality hardening, the OpenAI continuity transport fix, the Claude efficiency rerun, the first compact SRE modulator bundle, the landed M2 summary/memory/policy refinement, the landed J1 mediation evidence package baseline, and the landed J2 gap-closure evidence package." in theory_text
    assert "the landed J1 mediation evidence package baseline" in theory_text
    assert "mediation is now justified for one bounded experimental seam" in theory_text
    assert "the next honest move after J2 is now J3 mediation justification review" not in theory_text
