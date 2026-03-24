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
    assert "Re-audit before any `E6`." in text
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
