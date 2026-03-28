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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_accepted_workflow_baseline(workstream_text: str) -> tuple[str, str]:
    branch_match = re.search(r"Accepted baseline branch: `([^`]+)`", workstream_text)
    commit_match = re.search(r"Accepted baseline commit: `([^`]+)`", workstream_text)
    if branch_match is None or commit_match is None:
        raise AssertionError("missing accepted workflow baseline in workstream ledger")
    return branch_match.group(1), commit_match.group(1)


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
    assert "Current repo evidence now shows cell-level lift on:" in text
    assert "Package-level evidence remains `insufficient` on every required mediation axis." in text
    assert "Current repo-local verification truth:" in text
    assert "It does not by itself open new feature work." in text
    assert "or a separately scoped bounded runtime/product follow-on train." in text
    assert "- and Claude." in text
    assert "OpenAI runtime / ingress / service / bounded host-control" in text
    assert "Gemini runtime / ingress / service / bounded host-control" in text
    assert "Claude runtime / ingress / service / bounded host-control" in text
    assert "codex/l1-live-validation" in text
    assert "`8eb7f08`" in text


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


def test_resume_protocol_and_active_workstream_contract_exist() -> None:
    agents_text = _read(REPO_ROOT / "AGENTS.md")
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)

    assert "## Continuation and resume protocol" in agents_text
    assert "`docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in agents_text
    assert "git branch --show-current" in agents_text
    assert "git status --short --untracked-files=all" in agents_text
    assert "Never promote uncommitted local edits to accepted baseline truth." in agents_text

    assert "Status: live workflow-state ledger for compaction-safe continuation." in workstream_text
    assert "Accepted baseline branch: `codex/l1-live-validation`" in workstream_text
    assert "Accepted baseline commit: `8eb7f08`" in workstream_text
    assert "Current working branch at ledger update: `codex/l1-live-validation`" in workstream_text
    assert "accepted post-A1 live-validation line with Gemini operator testing now starting in CLI auto mode by default" in workstream_text
    assert "Current campaign: `G2 Gemini auto-routing operator-default normalization`" in workstream_text
    assert "Current candidate seam: none; `G2` is now landed for current scope" in workstream_text
    assert "Current seam status: `landed for current scope; service proof remains honestly blocked`" in workstream_text
    assert "the current signed-in smoke surfaces are now clean again" in workstream_text
    assert "`codex exec` for smoke" in workstream_text
    assert "`codex app-server` for lifecycle proof" in workstream_text
    assert "the OpenAI App Server operator lane now completes" in workstream_text
    assert "the Claude operator lane is now hook-backed and completes" in workstream_text
    assert "Gemini operator testing now starts in CLI auto mode by default and only falls back to explicit models after failure" in workstream_text
    assert "the installed CLI does accept `gemini-2.5-pro`" in workstream_text
    assert "`pass_minimal` succeeds twice with explicit `capacity_exhausted` warnings" in workstream_text
    assert "`truth_gap` remains non-truthful (`smoothed_incomplete`) on both `gemini-2.5-flash` and `gemini-2.5-flash-lite`" in workstream_text
    assert "`restart_continuity` now succeeds on `gemini-2.5-flash-lite`" in workstream_text
    assert "repeat-stable Gemini closure is not yet earned" in workstream_text
    assert "provide machine auth and spend approval for the current A4 / G4 / O4 service lanes" in workstream_text
    assert "if you want a cleaner operator-side closeout before that, open one bounded Gemini smoke-baseline stabilization or downgrade seam" in workstream_text
    assert "Do not treat signed-in provider CLI sessions as equivalent to the automation credentials" in workstream_text
    assert "Do not treat the new OpenAI App Server operator proof as license to reopen v1 assisted mode" in workstream_text
    assert "Do not keep repo-tracked live artifacts under `docs/live_validation/`" in workstream_text
    assert "Do not shell out from service transports to provider CLIs." in workstream_text
    assert "Do not silently reintroduce a pinned Gemini operator model as the default testing start point" in workstream_text
    assert "accepted workflow baseline truth remains the refreshed post-A1 live-model line" in workstream_text
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

    assert "Current campaign: `G2 Gemini auto-routing operator-default normalization`" in workstream_text
    assert "the live-testing environment now has explicit operator and automation lane semantics" in workstream_text
    assert "the current signed-in smoke surfaces are now clean again" in workstream_text
    assert "the OpenAI App Server operator lane now completes" in workstream_text
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

    assert "Status: active runtime-program brief for the first explicit executive live-outcome allocation slice" in executive_live_outcome_program_text
    assert "branch: `codex/k2-openai-host-control`" in executive_live_outcome_program_text
    assert "commit: `9ed7dae`" in executive_live_outcome_program_text
    assert "nested `control_ledger.allocation_diagnostics`" in executive_live_outcome_program_text
    assert "`Q_t^{mem}=0.0`" in executive_live_outcome_program_text
    assert "`alpha_t=1.0`" in executive_live_outcome_program_text
    assert "`allocated_score=online_score`" in executive_live_outcome_program_text
    assert "`make revalidate-executive-loop`" in executive_live_outcome_program_text
    assert "Current K3 candidate state before closeout" in executive_live_outcome_program_text
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
    assert "correct signed-in operator hierarchy" in phase_gate_text
    assert "operator preflight and repeated smoke baselines are clean in CLI auto mode" in phase_gate_text
    assert "deeper product path still reflects the previously earned partial flash/flash-lite fallback story" in phase_gate_text
    assert "the bounded `codex app-server` operator lane is now re-earned" in phase_gate_text

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

    assert "Status: active L2 live-testing environment brief with L2b/L2c/L2d/L2e host-native lifecycle follow-ons" in live_validation_program_text
    assert "branch: `codex/l1-live-validation`" in live_validation_program_text
    assert "commit: `8eb7f08`" in live_validation_program_text
    assert "signed-in host-native product surfaces" in live_validation_program_text
    assert "local-only under `.cortex/live_validation/`" in live_validation_program_text
    assert "`codex exec` = smoke / preflight" in live_validation_program_text
    assert "`codex app-server` = lifecycle proof" in live_validation_program_text
    assert "OpenAI App Server now succeeds on:" in live_validation_program_text
    assert "Status: active L2 scenario catalog for the signed-in-first live environment with L2b/L2c host-native lifecycle proof" in live_validation_scenario_catalog_text
    assert "`pass_minimal`" in live_validation_scenario_catalog_text
    assert "`restart_continuity`" in live_validation_scenario_catalog_text
    assert "`truth_gap`" in live_validation_scenario_catalog_text
    assert "`codex app-server` = lifecycle proof" in live_validation_scenario_catalog_text
    assert "`PreToolUse`" in live_validation_scenario_catalog_text
    assert "`BeforeTool`" in live_validation_scenario_catalog_text
    assert "machine output: local-only under `.cortex/live_validation/`" in live_validation_scenario_catalog_text
    assert "Status: L2/L2b/L2c/L2d/L2e live-testing environment verdict note" in live_validation_verdict_text
    assert "**lifecycle-first is promising but under-instrumented**" in live_validation_verdict_text
    assert "operator-only payoff note is narrower" in live_validation_verdict_text
    assert "operator-only audit is now landed for current scope" in live_validation_verdict_text
    assert "The Gemini auto-routing operator-default normalization seam is now landed for current scope." in live_validation_verdict_text
    service_proof_text = _read(LIVE_SERVICE_PROOF_PATH)
    assert "Status: active service-lane live-proof note" in service_proof_text
    assert "Signed-in CLI sessions do **not** count as service-lane auth." in service_proof_text
    assert "package-level service proof is updated truthfully in `docs/CORTEX_V2_PHASE_GATES_2.md`" in service_proof_text
    assert "`codex app-server` passes `pass_minimal` twice" in live_validation_verdict_text
    assert "Claude is now re-earned on a hook-backed operator lane" in live_validation_verdict_text
    assert "operator probes and repeated smoke baselines are now clean in CLI auto mode" in live_validation_verdict_text
    assert "`gemini-2.5-flash` succeeds twice on `pass_minimal`" in live_validation_verdict_text
    assert "`gemini-2.5-flash-lite` still returns `smoothed_incomplete` on `truth_gap`" in live_validation_verdict_text
    assert "`gemini-2.5-pro` is valid locally but still capacity-blocked" in live_validation_verdict_text
    assert "host-native Codex surface rather than the wrong `openai` utility surface" in live_validation_verdict_text
    assert "`L2b` now re-earns OpenAI on the current host-native App Server lifecycle surface" in live_validation_verdict_text
    assert "`L2c` now re-earns Claude and Gemini on their documented hook surfaces" in live_validation_verdict_text
    assert "`G2` now re-optimizes Gemini operator testing around CLI auto mode" in live_validation_verdict_text
    assert "`L2e` now proves that Gemini Pro is not the current closure model" in live_validation_verdict_text


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
    assert "make revalidate-executive-loop" in local_verification_text
    assert "revalidate-executive-loop:" in makefile_text
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
    assert "## Live host-native product paths" in local_verification_text
    assert "make live-host-native-product-paths" in local_verification_text
    assert "For Claude and Gemini, the operator lane now records documented hook events" in local_verification_text
    assert "## Live OpenAI App Server operator proof" in local_verification_text
    assert "make live-openai-app-server" in local_verification_text
    assert "## Live Cortex host-control capture" in local_verification_text
    assert "make live-cortex-host-control" in local_verification_text
    assert "## Live comparison and verdict" in local_verification_text
    assert "make live-compare" in local_verification_text
    assert "## Live operator payoff audit" in local_verification_text
    assert "make live-operator-payoff-audit" in local_verification_text
    assert "live-preflight:" in makefile_text
    assert "live-provider-baselines:" in makefile_text
    assert "live-provider-baselines-automation:" in makefile_text
    assert "live-host-native-product-paths:" in makefile_text
    assert "live-openai-app-server:" in makefile_text
    assert "live-cortex-host-control:" in makefile_text
    assert "live-compare:" in makefile_text
    assert "live-operator-payoff-audit:" in makefile_text


def test_erika_visualizations_are_framed_as_support_surfaces() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    markdown_text = _read(ERIKA_VISUALIZATION_STATUS_PATH)
    html_text = _read(ERIKA_VISUALIZATION_HTML_PATH)
    accepted_branch, accepted_commit = _extract_accepted_workflow_baseline(workstream_text)

    assert "support surface" in markdown_text
    assert "current accepted repo truth" in markdown_text
    assert "north-star product target" in markdown_text
    assert "lawful gap programs" in markdown_text
    assert "mechanisms Cortex has already stolen so far" in markdown_text
    assert f"**Accepted factual baseline:** `{accepted_branch}` at `{accepted_commit}`" in markdown_text
    assert "The verification/evidence restack train, K1 runtime/product restack, and K2 bounded host-control train are now landed for current scope on top of that same product truth." in markdown_text
    assert "The reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound OpenAI host-control lane are now accepted on the current line." in markdown_text
    assert "The Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane are now accepted on the current line." in markdown_text
    assert "operator-only payoff audit is now landed for current scope, and Gemini operator testing now starts in CLI auto mode before the remaining service-proof blockers." in markdown_text
    assert "Codex rather than `openai` as the OpenAI operator surface" in markdown_text
    assert "distinguishes `codex exec` smoke from `codex app-server` lifecycle proof" in markdown_text
    assert "now records documented hook events on Claude and Gemini" in markdown_text
    assert "operator probe and smoke baselines are now clean in CLI auto mode" in markdown_text
    assert "`gemini-2.5-pro` is valid but capacity-blocked on smoke" in markdown_text
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
        f"The accepted factual baseline is <code>{accepted_branch}</code> at "
        f"<code>{accepted_commit}</code>."
    ) in html_text
    assert '<details class="biology-card"' in html_text
    assert "What we've stolen so far" in html_text
    assert "What is still partial" in html_text
    assert "What remains north-star only" in html_text
    assert "signed-in-first live testing environment with App Server and hook lifecycle proof" in html_text
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
    assert "now records the landed Gemini auto-routing operator-default normalization seam and the remaining blocked service-proof move after it" in theory_text
