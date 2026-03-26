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
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
ACTIVE_WORKSTREAM_PATH = REPO_ROOT / "docs" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
THEORY_PATH = REPO_ROOT / "docs" / "CORTEX_V2_THEORY_2.md"
ERIKA_VISUALIZATION_STATUS_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "CORTEX_EVIDENCE_BASED_STATUS.md"
)
ERIKA_VISUALIZATION_HTML_PATH = (
    REPO_ROOT / "docs" / "erika-visualizations" / "cortex-now-vs-future.html"
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


def test_post_e4_live_parent_contract_is_recorded() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    local_verification_text = _read(LOCAL_VERIFICATION_PATH)
    implementation_status_text = _read(IMPLEMENTATION_STATUS_NOTE_PATH)
    agents_text = _read(AGENTS_PATH)

    accepted_branch, accepted_commit = _extract_accepted_workflow_baseline(workstream_text)
    assert f"Accepted baseline branch: `{accepted_branch}`" in workstream_text
    assert f"Accepted baseline commit: `{accepted_commit}`" in workstream_text
    assert "accepted post-`E4` verification baseline: `194a43f`" not in local_verification_text
    assert "temporary live parent branch: `codex/e4b-reference-contradiction-helpers`" not in local_verification_text
    assert "194a43f" not in local_verification_text
    assert "codex/e4b-reference-contradiction-helpers" not in local_verification_text
    assert "194a43f" not in agents_text
    assert "codex/e4b-reference-contradiction-helpers" not in agents_text
    assert "194a43f" not in implementation_status_text
    assert "codex/e4b-reference-contradiction-helpers" not in implementation_status_text
    assert "accepted workflow baseline branch and commit are recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in local_verification_text
    assert "new v2 seams should branch from the accepted workflow baseline recorded there" in local_verification_text
    assert "do not branch new v2 work from `codex/e1-verification-substrate-entrypoints`" in local_verification_text
    assert "do not branch new v2 work from `codex/closure-train-2026-03-24`" in local_verification_text
    assert "do not branch new v2 work from archival `main` / `origin/main`" in local_verification_text
    assert "future seam-parent truth is recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in implementation_status_text
    assert "`main` / `origin/main` are archival-root only" in agents_text
    assert "Branch new v2 work from the accepted workflow baseline recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`." in agents_text
    assert accepted_branch == "codex/j1-openai-host-realization-three-pair"
    assert accepted_commit == "21354ab"


def test_resume_protocol_and_active_workstream_contract_exist() -> None:
    agents_text = _read(AGENTS_PATH)
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)

    assert "## Continuation and resume protocol" in agents_text
    assert "`docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`" in agents_text
    assert "git branch --show-current" in agents_text
    assert "git status --short --untracked-files=all" in agents_text
    assert "Never promote uncommitted local edits to accepted baseline truth." in agents_text

    assert "Status: live workflow-state ledger for compaction-safe continuation." in workstream_text
    assert "Accepted baseline branch: `codex/j1-openai-host-realization-three-pair`" in workstream_text
    assert "Accepted baseline commit: `21354ab`" in workstream_text
    assert "Current working branch at ledger update: `codex/j2-restack-acceptance-truth-normalization`" in workstream_text
    assert "bounded workflow/support truth-normalization candidate over the accepted `j1` line" in workstream_text
    assert "Do not treat mixed local edits on the current working branch as accepted truth." in workstream_text
    assert "Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md`" in workstream_text
    assert "Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation." in workstream_text
    assert "Do not reinterpret a host-level `candidate_positive` cell as package-level justification." in workstream_text
    assert "git branch --show-current" in workstream_text
    assert "git status --short --untracked-files=all" in workstream_text
    assert "Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth." in workstream_text


def test_support_surfaces_are_present_and_framed_as_non_authority() -> None:
    workstream_text = _read(ACTIVE_WORKSTREAM_PATH)
    theory_text = _read(THEORY_PATH)
    markdown_text = _read(ERIKA_VISUALIZATION_STATUS_PATH)
    html_text = _read(ERIKA_VISUALIZATION_HTML_PATH)
    accepted_branch, accepted_commit = _extract_accepted_workflow_baseline(workstream_text)

    assert "Status: non-authority working memo" in theory_text
    assert "This file is not an authority surface." in theory_text
    assert "Do not open a new feature seam from this file." in theory_text
    assert f"The accepted workflow baseline is `{accepted_branch}` at `{accepted_commit}`." in theory_text
    assert "support surface" in markdown_text
    assert "current accepted repo truth" in markdown_text
    assert "north-star product target" in markdown_text
    assert "lawful gap programs" in markdown_text
    assert "Mechanisms Cortex has already stolen so far" in markdown_text
    assert f"**Accepted factual baseline:** `{accepted_branch}` at `{accepted_commit}`" in markdown_text
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
