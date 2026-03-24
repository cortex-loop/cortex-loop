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
    assert "Accepted baseline branch: `codex/s0b-erika-support-closeout`" in workstream_text
    assert "Accepted baseline commit: `6218115`" in workstream_text
    assert "Current working branch at ledger update: `codex/r1a-reference-runtime-program-lock`" in workstream_text
    assert "clean runtime-program branch opened from the accepted support parent" in workstream_text
    assert "Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth." in workstream_text
    assert "git branch --show-current" in workstream_text
    assert "git status --short --untracked-files=all" in workstream_text
    assert "Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth." in workstream_text


def test_reference_runtime_program_lock_is_recorded() -> None:
    program_text = _read(REFERENCE_RUNTIME_PROGRAM_PATH)
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

    assert "Current campaign: reference runtime-shell opening" in workstream_text
    assert "Current candidate seam: runtime program lock for the reference-host local CLI shell" in workstream_text
    assert "After `R1A` is accepted, open `R1B` as the first runtime-code seam from a clean tree." in workstream_text


def test_erika_visualizations_are_framed_as_support_surfaces() -> None:
    markdown_text = _read(ERIKA_VISUALIZATION_STATUS_PATH)
    html_text = _read(ERIKA_VISUALIZATION_HTML_PATH)

    assert "support surface" in markdown_text
    assert "current accepted repo truth" in markdown_text
    assert "north-star product target" in markdown_text
    assert "lawful gap programs" in markdown_text
    assert "mechanisms Cortex has already stolen so far" in markdown_text
    assert "Selected next opening move: reference-host local CLI runtime shell" in markdown_text
    assert "cortex-archival-dossiers/" not in markdown_text
    assert "Current Justified Boundary" in html_text
    assert "Gap Programs" in html_text
    assert "North-Star Cortex" in html_text
    assert "support surface" in html_text
    assert "not active authority" in html_text
    assert "not current committed roadmap" in html_text
    assert "Biology Tracker: What Cortex Has Stolen So Far" in html_text
    assert "which brain-inspired mechanisms Cortex has already stolen so far" in html_text
    assert "Open the reference-host local CLI runtime shell locked by" in html_text
    assert '<details class="biology-card"' in html_text
    assert "What we've stolen so far" in html_text
    assert "What is still partial" in html_text
    assert "What remains north-star only" in html_text
    assert "Cortex Complete" not in html_text
    assert "Today vs Future" not in html_text
