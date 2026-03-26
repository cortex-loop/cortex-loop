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
ERIKA_VISUALIZATION_STATUS_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "CORTEX_EVIDENCE_BASED_STATUS.md"
)
ERIKA_VISUALIZATION_HTML_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "cortex-now-vs-future.html"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def test_resume_protocol_and_active_workstream_contract_exist() -> None:
    agents_text = _read(REPO_ROOT / "AGENTS.md")
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)

    assert "## Continuation and resume protocol" in agents_text
    assert "`docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in agents_text
    assert "git branch --show-current" in agents_text
    assert "git status --short --untracked-files=all" in agents_text
    assert "Never promote uncommitted local edits to accepted baseline truth." in agents_text

    assert "Status: live workflow-state ledger for compaction-safe continuation." in workstream_text
    assert "Accepted baseline branch: `codex/r5e-short-window-feedback-reaudit`" in workstream_text
    assert "Accepted `R5` opening parent: `9d07c5b`" in workstream_text
    assert "Accepted `R5` proof head: `ee41eb4`" in workstream_text
    assert "Accepted `R5` deterministic closeout head: `fd6789f`" in workstream_text
    assert "Accepted baseline commit: `ee41eb4`" not in workstream_text
    assert "The accepted `R5` proof head `ee41eb4` and deterministic closeout head `fd6789f` remain the accepted baseline truth until a later committed acceptance updates them." in workstream_text
    assert "Current working branch at ledger update: `codex/c1-reference-continuation`" in workstream_text
    assert "bounded runtime/docs/test train that adds explicit persisted `continuity_truth`, bounded `control_residue`, explicit CLI load/save, and cross-process continuity proof without widening into generic persistence or broader runtime rollout" in workstream_text
    assert "Current candidate seam: `C1A` through `C1E`" in workstream_text
    assert "Current seam status: `C1 candidate implemented and locally verified / accepted baseline unchanged until commit or explicit acceptance`" in workstream_text
    assert "Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth." in workstream_text
    assert "Do not treat the first landed `R5` slice as permission for longer-than-three-step feedback history" in workstream_text
    assert "Do not auto-open `R6` or any broader runtime/product program from the success of this corrective `R5` reclosure." in workstream_text
    assert "Do not widen `C1` into autosave, checkpoints, generic persistence doctrine, multi-host runtime, runtime AUX activation, offline consolidation, or mediation." in workstream_text
    assert "git branch --show-current" in workstream_text
    assert "git status --short --untracked-files=all" in workstream_text
    assert "Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth." in workstream_text


def test_reference_runtime_program_lock_is_recorded() -> None:
    program_text = _read(REFERENCE_RUNTIME_PROGRAM_PATH)
    feedback_program_text = _read(REFERENCE_FEEDBACK_PROGRAM_PATH)
    feedback_program_1_text = _read(REFERENCE_FEEDBACK_PROGRAM_1_PATH)
    continuity_program_text = _read(REFERENCE_CONTINUITY_PROGRAM_PATH)
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
    assert "explicit persisted `continuity_truth` plus bounded `control_residue` now exist on `codex/c1-reference-continuation`" in phase_gate_text
    assert "accepted baseline truth is unchanged until this branch is accepted/committed" in phase_gate_text

    assert "Current campaign: `C1` bounded reference cross-process continuation implementation is now present on the working branch as a local candidate seam" in workstream_text
    assert "persisted continuation truth is split into exact `continuity_truth` and bounded `control_residue`" in workstream_text
    assert "repo-local revalidation now includes `make revalidate-reference-runtime-continuity`" in workstream_text
    assert "the first one-process live continuity slice plus explicit rejection enforcement are real" in program_text
    assert "the corrective zero-finding re-audit has passed for current scope" in program_text
    assert "a mismatched runtime `session_id` is surfaced as an explicit contradiction" in program_text
    assert "first bounded reference closed-loop feedback slice" in feedback_program_text
    assert "top-level control ledger in the runtime output surface" in feedback_program_text
    assert "bounded latched-brake enforcement point" in feedback_program_text
    assert "`R4B` realization-feedback carrier and persistence" in feedback_program_text
    assert "`R4E` latched-brake enforcement" in feedback_program_text
    assert "Current accepted state after `R4` senior closure" in feedback_program_text
    assert "accepted senior-critique proof head `7672304` (runtime landing `cecd82d` inside the same closeout line)" in feedback_program_text
    assert "CLI-visible selected-vs-realized divergence" in feedback_program_text
    assert "zero-finding adversarial runtime/API review found no defect for current scope" in feedback_program_text
    assert "first bounded reference short-window feedback slice" in feedback_program_1_text
    assert "branch: `codex/s3-r4-senior-closeout`" in feedback_program_1_text
    assert "commit: `9d07c5b`" in feedback_program_1_text
    assert "accepted proof head: `7672304`" in feedback_program_1_text
    assert "`ReferenceRealizationFeedbackWindow`" in feedback_program_1_text
    assert "`ReferenceFeedbackWindowSummary`" in feedback_program_1_text
    assert "maximum length `3`" in feedback_program_1_text
    assert "feedback_window_summary" in feedback_program_1_text
    assert "session_summary.feedback_window_size" in feedback_program_1_text
    assert "This program does **not** authorize:" in feedback_program_1_text
    assert "a scoring rewrite" in feedback_program_1_text
    assert "`R5B` feedback window carrier and session persistence" in feedback_program_1_text
    assert "`R5E` re-audit and closeout" in feedback_program_1_text
    assert "Current accepted state after `R5` closeout" in feedback_program_1_text
    assert "opened from `9d07c5b`, proven at `ee41eb4`, and truthfully closed at deterministic closeout head `fd6789f`" in feedback_program_1_text
    assert "committed end-to-end proof now exists at `ee41eb4`" in feedback_program_1_text
    assert "the accepted landed closeout for that same `R5` line is anchored at `fd6789f`" in feedback_program_1_text
    assert "Current corrective state after session-carrier reclosure" in feedback_program_1_text
    assert "codex/r5g-h-corrective-reclosure" in feedback_program_1_text
    assert "last-step mirror with empty window becomes a one-entry bounded window" in feedback_program_1_text
    assert "the direct-construction reproduction that dropped next-step pressure is now closed" in feedback_program_1_text
    assert "R5` is landed again for current scope on the corrective line" in feedback_program_1_text
    assert "top-level `feedback_window_summary`" in feedback_program_1_text
    assert "single-mismatch `0.55` floor" in feedback_program_1_text
    assert "repeated-mismatch `0.70` floor" in feedback_program_1_text
    assert "first bounded reference cross-process continuation slice" in continuity_program_text
    assert "`--load-session PATH`" in continuity_program_text
    assert "`--save-session PATH`" in continuity_program_text
    assert "`continuity_truth`" in continuity_program_text
    assert "`control_residue`" in continuity_program_text
    assert "`C1` equivalence does **not** require:" in continuity_program_text
    assert "`make revalidate-reference-runtime-continuity`" in continuity_program_text


def test_erika_visualizations_are_framed_as_support_surfaces() -> None:
    markdown_text = _read(ERIKA_VISUALIZATION_STATUS_PATH)
    html_text = _read(ERIKA_VISUALIZATION_HTML_PATH)

    assert "support surface" in markdown_text
    assert "current accepted repo truth" in markdown_text
    assert "north-star product target" in markdown_text
    assert "lawful gap programs" in markdown_text
    assert "mechanisms Cortex has already stolen so far" in markdown_text
    assert "**Accepted factual baseline:** `codex/r5e-short-window-feedback-reaudit` at deterministic closeout head `fd6789f`, with accepted `R5` proof head `ee41eb4` inside the same closeout history (`R4` proof head `7672304`, runtime landing `cecd82d`, and opening parent `9d07c5b` remain historical anchors only)" in markdown_text
    assert "accepted `R5` proof head `ee41eb4`" in markdown_text
    assert "deterministic closeout head `fd6789f`" in markdown_text
    assert "**Accepted factual baseline:** `codex/r5e-short-window-feedback-reaudit` at accepted `R5` proof head `ee41eb4`" not in markdown_text
    assert "the first bounded last-step realization-feedback path, the first top-level control-ledger projection, and the first bounded latched-brake enforcement point" in markdown_text
    assert "`R1` through `R5` are closed and audit-clean for current scope." in markdown_text
    assert "The first bounded reference-only short-window slice is now landed: a three-step realized-outcome window, a bounded prior-window summary, a top-level control ledger, top-level `feedback_window_summary`, and contradiction-preserving latched-brake enforcement" in markdown_text
    assert "zero-finding re-audit" in markdown_text
    assert "single-mismatch `0.55` floor" in markdown_text
    assert "cortex-archival-dossiers/" not in markdown_text
    assert "Current Justified Boundary" in html_text
    assert "Gap Programs" in html_text
    assert "North-Star Cortex" in html_text
    assert "support surface" in html_text
    assert "not active authority" in html_text
    assert "not current committed roadmap" in html_text
    assert "Biology Tracker: What Cortex Has Stolen So Far" in html_text
    assert "which brain-inspired mechanisms Cortex has already stolen so far" in html_text
    assert "Accepted R5 Closeout Head fd6789f (Proof Head ee41eb4)" in html_text
    assert "first integrated computed executive slice are real" not in html_text
    assert "it now carries the first integrated computed executive slice, one-process continuity law, last-step realization feedback, a top-level control ledger, and bounded latched-brake enforcement" in html_text
    assert "<code>R5</code> closeout head <code>fd6789f</code>, with proof head <code>ee41eb4</code>" in html_text
    assert "Accepted R5 Proof Head ee41eb4" not in html_text
    assert "<code>R4</code> proof head" in html_text
    assert "<code>7672304</code>" in html_text
    assert "runtime landing" in html_text
    assert "<code>cecd82d</code>" in html_text
    assert "Stop after the first bounded short-window feedback slice and choose any wider loop program explicitly instead of widening scope prematurely." in html_text
    assert "The first bounded reference-only short-window slice is now landed: a three-step realized-outcome window, a prior-window summary, a top-level control ledger, top-level <code>feedback_window_summary</code>, and contradiction-preserving latched-brake enforcement." in html_text
    assert "Stop after `R5`; if future work opens, keep longer-window feedback and broader enforcement as separate programs." in html_text
    assert '<details class="biology-card"' in html_text
    assert "What we've stolen so far" in html_text
    assert "What is still partial" in html_text
    assert "What remains north-star only" in html_text
    assert "Cortex Complete" not in html_text
    assert "Today vs Future" not in html_text
