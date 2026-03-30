"""Checks for the current mediation evidence package."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile

from tests._mediation_evidence import (
    AXIS_TABLE_PATH,
    EVALUATION_PLAN_PATH,
    EVIDENCE_NOTE_PATH,
    HOST_SPLIT_TABLE_PATH,
    PAIRED_LEDGER_PATH,
    SCENARIO_CATALOG_PATH,
    parse_markdown_table,
    read,
    section,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = REPO_ROOT / "tools" / "mediation_evidence_package.py"
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))


def _load_tool():
    spec = importlib.util.spec_from_file_location("mediation_evidence_package", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("failed to load mediation evidence package tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _temp_repo_copy() -> Path:
    temp_root = Path(tempfile.mkdtemp(prefix="mediation-package-"))
    shutil.copytree(REPO_ROOT / "docs", temp_root / "docs")
    return temp_root


def _replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"missing expected text in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_evaluation_plan_still_points_to_the_package_surface() -> None:
    text = read(EVALUATION_PLAN_PATH)

    assert "docs/CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md" in text
    assert "docs/CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0.md" in text
    assert "tests/unit/test_mediation_evidence_package.py" in text
    assert "docs/CORTEX_V2_LOCAL_VERIFICATION.md" in text


def test_mediation_package_checker_passes() -> None:
    tool = _load_tool()

    assert tool.check_package() == []


def test_mediation_package_tool_emits_normalized_summary() -> None:
    tool = _load_tool()

    summary = tool.emit_summary()

    assert "# Mediation Evidence Package Summary" in summary
    assert "- reduced thrashing: `candidate_positive`" in summary
    assert "- better branch discipline: `candidate_positive`" in summary
    assert "- better uncertainty handling: `insufficient`" in summary
    assert "- lower visible burden at equal task value: `candidate_positive`" in summary
    assert "- better host-specialized realization: `candidate_positive`" in summary
    assert "`uncertainty_expansion_if_still_needed` on claude first, then stable second-family expansion" in summary


def test_scenario_catalog_records_current_families_and_j2_targets() -> None:
    family_rows = parse_markdown_table(
        section(read(SCENARIO_CATALOG_PATH), "Scenario Family Coverage Matrix")
    )
    target_rows = parse_markdown_table(
        section(read(SCENARIO_CATALOG_PATH), "J2 Gap-Closure Target Inventory")
    )

    assert {row["scenario_family_id"] for row in family_rows} == {
        "thrash_control",
        "uncertainty_boundary",
        "host_realization",
        "branch_discipline",
        "equal_value_burden_non_thrash",
        "uncertainty_expansion",
    }
    assert {row["evidence_state"] for row in family_rows} == {"current", "missing"}
    thrash_row = next(row for row in family_rows if row["scenario_family_id"] == "thrash_control")
    assert thrash_row["burden_comparable_at_equal_task_value"] == "yes"
    assert "package-level burden remains too narrow" in thrash_row["notes"]

    assert [row["proposed_scenario_id"] for row in target_rows] == [
        "scenario_branch_reference_01",
        "scenario_branch_openai_01",
        "scenario_branch_claude_01",
        "scenario_burden_reference_01",
        "scenario_burden_openai_01",
        "scenario_burden_claude_01",
        "scenario_host_claude_01",
        "scenario_uncertainty_claude_01",
    ]
    assert {row["planned_evidence_state"] for row in target_rows} == {"current", "missing"}


def test_paired_ledger_keeps_current_pairs_and_planned_slots_separate() -> None:
    recorded_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "Recorded Paired Runs"))
    planned_rows = parse_markdown_table(section(read(PAIRED_LEDGER_PATH), "J2 Planned Pair Slots"))

    real_rows = [row for row in recorded_rows if row["paired_episode_set_id"] != "none_recorded_yet"]
    assert len(real_rows) == 48
    assert {row["pair_status"] for row in real_rows} == {"usable"}
    assert {row["failure_tags"] for row in real_rows} == {"none"}
    assert [row["proposed_scenario_id"] for row in planned_rows] == [
        "scenario_branch_reference_01",
        "scenario_branch_openai_01",
        "scenario_branch_claude_01",
        "scenario_burden_reference_01",
        "scenario_burden_openai_01",
        "scenario_burden_claude_01",
        "scenario_host_claude_01",
        "scenario_uncertainty_claude_01",
    ]
    assert {row["planned_status"] for row in planned_rows} == {"current", "missing"}


def test_axis_and_evidence_note_now_end_with_exact_missing_delta() -> None:
    axis_rows = parse_markdown_table(section(read(AXIS_TABLE_PATH), "Exact Missing-Evidence Delta"))
    note_rows = parse_markdown_table(section(read(EVIDENCE_NOTE_PATH), "Exact Missing-Evidence Delta"))
    rerun_rows = parse_markdown_table(section(read(EVIDENCE_NOTE_PATH), "Next Rerun Contract"))

    assert [row["axis"] for row in axis_rows] == [row["axis"] for row in note_rows]
    assert {row["current_package_verdict"] for row in axis_rows} == {
        "candidate_positive",
        "insufficient",
    }
    burden_row = next(row for row in axis_rows if row["axis"] == "lower visible burden at equal task value")
    assert "broadens the burden axis beyond" in burden_row["why_still_insufficient"]
    assert "one bounded experimental seam" in burden_row["minimum_additional_paired_evidence"]

    assert [row["target_id"] for row in rerun_rows] == ["uncertainty_expansion_if_still_needed"]


def test_host_split_matrix_makes_claude_missing_and_gemini_partial_explicit() -> None:
    rows = parse_markdown_table(section(read(HOST_SPLIT_TABLE_PATH), "Current Host Matrix"))

    assert [row["host_family"] for row in rows] == [
        "reference",
        "openai",
        "claude",
        "gemini",
    ]
    claude_row = next(row for row in rows if row["host_family"] == "claude")
    gemini_row = next(row for row in rows if row["host_family"] == "gemini")

    assert claude_row["committed_package_state"] == "current"
    assert claude_row["j2_priority"] == "preferred"
    assert gemini_row["committed_package_state"] == "current"
    assert gemini_row["j2_priority"] == "explicit_partial"
    assert "partial_or_contaminated" in gemini_row["current_live_note"]


def test_checker_fails_when_burden_ref_is_missing() -> None:
    tool = _load_tool()
    temp_root = _temp_repo_copy()
    burden_path = temp_root / "docs" / "CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md"
    _replace_once(
        burden_path,
        "docs/mediation_evidence/reference/scenario_burden_reference_01__baseline_non_mediated__run_001__aux_burden.md",
        "docs/mediation_evidence/reference/missing__aux_burden.md",
    )

    errors = tool.check_package(tool.build_layout(temp_root))

    assert any("missing burden ref" in error for error in errors)


def test_checker_fails_when_required_j2_target_is_removed() -> None:
    tool = _load_tool()
    temp_root = _temp_repo_copy()
    catalog_path = temp_root / "docs" / "CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md"
    text = catalog_path.read_text(encoding="utf-8")
    line = "| scenario_branch_claude_01 | branch_discipline | claude | better branch discipline | 3 | current | Adds the missing Claude branch-discipline line. |\n"
    if line not in text:
        raise AssertionError("missing expected J2 target line")
    catalog_path.write_text(text.replace(line, "", 1), encoding="utf-8")

    errors = tool.check_package(tool.build_layout(temp_root))

    assert any("J2 target ids drifted" in error for error in errors)


def test_checker_fails_when_forbidden_verdict_is_introduced() -> None:
    tool = _load_tool()
    temp_root = _temp_repo_copy()
    axis_path = temp_root / "docs" / "CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md"
    _replace_once(
        axis_path,
        "| scenario_branch_reference_01 | reference | 3 | 0 | 0 | candidate_positive |",
        "| scenario_branch_reference_01 | reference | 3 | 0 | 0 | positive |",
    )

    errors = tool.check_package(tool.build_layout(temp_root))

    assert any("invalid verdict positive" in error for error in errors)


def test_checker_fails_when_claude_missing_coverage_is_hidden() -> None:
    tool = _load_tool()
    temp_root = _temp_repo_copy()
    host_path = temp_root / "docs" / "CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md"
    _replace_once(
        host_path,
        "| claude | current | host_realization; branch_discipline; equal_value_burden_non_thrash | Claude is now present in the mediation package on deterministic evidence surfaces. | preferred | Claude is the only new host added in J2. |",
        "| claude | missing | host_realization; branch_discipline; equal_value_burden_non_thrash | Claude is now present in the mediation package on deterministic evidence surfaces. | preferred | Claude is the only new host added in J2. |",
    )

    errors = tool.check_package(tool.build_layout(temp_root))

    assert any("claude current mediation coverage" in error.lower() for error in errors)


def test_checker_fails_when_gemini_partial_status_is_hidden() -> None:
    tool = _load_tool()
    temp_root = _temp_repo_copy()
    host_path = temp_root / "docs" / "CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md"
    _replace_once(
        host_path,
        "| gemini | current | thrash_control; uncertainty_boundary; host_realization | Keep explicit as partial_or_contaminated for future live reruns. | explicit_partial | Do not hide current quota/capacity contamination behind pooled host averages. |",
        "| gemini | current | thrash_control; uncertainty_boundary; host_realization | Stable first rerun anchor on the current line. | preferred | Do not hide current quota/capacity contamination behind pooled host averages. |",
    )

    errors = tool.check_package(tool.build_layout(temp_root))

    assert any("gemini host matrix row no longer preserves explicit partial_or_contaminated" in error for error in errors)
