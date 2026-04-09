"""Check and summarize the committed mediation evidence package."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from lab.mediation_evidence_common import (
    AXIS_TABLE_PATH,
    BURDEN_TABLE_PATH,
    DEFAULT_LAYOUT,
    EVIDENCE_NOTE_PATH,
    FAILURE_TAXONOMY_PATH,
    HOST_SPLIT_TABLE_PATH,
    PAIRED_LEDGER_PATH,
    SCENARIO_CATALOG_PATH,
    PackageLayout,
    build_layout,
    parse_markdown_table,
    read,
    real_pair_rows,
    section,
)


ALLOWED_VERDICTS = {
    "negative",
    "neutral",
    "mixed",
    "candidate_positive",
    "insufficient",
}
ALLOWED_FAILURE_TAGS = {
    "scenario_mismatch",
    "host_mismatch",
    "boundary_drift",
    "burden_regression",
    "branch_churn",
    "uncertainty_churn",
    "host_flattening",
    "artifact_gap",
    "env_friction",
    "provider_limit_contamination",
    "host_capacity_contamination",
    "stale_evidence",
    "none",
}
EXPECTED_FAMILY_IDS = {
    "thrash_control": {"evidence_state": "current"},
    "uncertainty_boundary": {"evidence_state": "current"},
    "host_realization": {"evidence_state": "current"},
    "branch_discipline": {"evidence_state": "current"},
    "equal_value_burden_non_thrash": {"evidence_state": "current"},
    "uncertainty_expansion": {"evidence_state": "missing"},
}
EXPECTED_J2_TARGETS = {
    "scenario_branch_reference_01": {
        "scenario_family_id": "branch_discipline",
        "host_family": "reference",
    },
    "scenario_branch_openai_01": {
        "scenario_family_id": "branch_discipline",
        "host_family": "openai",
    },
    "scenario_branch_claude_01": {
        "scenario_family_id": "branch_discipline",
        "host_family": "claude",
    },
    "scenario_burden_reference_01": {
        "scenario_family_id": "equal_value_burden_non_thrash",
        "host_family": "reference",
    },
    "scenario_burden_openai_01": {
        "scenario_family_id": "equal_value_burden_non_thrash",
        "host_family": "openai",
    },
    "scenario_burden_claude_01": {
        "scenario_family_id": "equal_value_burden_non_thrash",
        "host_family": "claude",
    },
    "scenario_host_claude_01": {
        "scenario_family_id": "host_realization",
        "host_family": "claude",
    },
    "scenario_uncertainty_claude_01": {
        "scenario_family_id": "uncertainty_expansion",
        "host_family": "claude",
    },
}
EXPECTED_PACKAGE_VERDICTS = {
    "reduced thrashing": "candidate_positive",
    "better branch discipline": "candidate_positive",
    "better uncertainty handling": "insufficient",
    "lower visible burden at equal task value": "candidate_positive",
    "better host-specialized realization": "candidate_positive",
}
EXPECTED_HOST_MATRIX = {
    "reference": {
        "committed_package_state": "current",
        "j2_priority": "preferred",
    },
    "openai": {
        "committed_package_state": "current",
        "j2_priority": "preferred",
    },
    "claude": {
        "committed_package_state": "current",
        "j2_priority": "preferred",
    },
    "gemini": {
        "committed_package_state": "current",
        "j2_priority": "explicit_partial",
    },
}
EXPECTED_AXIS_FAMILIES = {
    "reduced thrashing": ("scenario_thrash_", "scenario_branch_"),
    "better branch discipline": ("scenario_thrash_", "scenario_branch_"),
    "better uncertainty handling": "scenario_uncertainty_",
    "lower visible burden at equal task value": ("scenario_thrash_", "scenario_burden_"),
    "better host-specialized realization": "scenario_host_",
}
EXPECTED_RERUN_TARGET_IDS = ["uncertainty_expansion_if_still_needed"]


def _section_rows(path: Path, heading: str) -> list[dict[str, str]]:
    return parse_markdown_table(section(read(path), heading))


def _candidate_cells(layout: PackageLayout, heading: str) -> list[str]:
    rows = _section_rows(layout.axis_table_path, heading)
    return [
        f"{row['scenario_id']}/{row['host_family']}"
        for row in rows
        if row["current_verdict"] == "candidate_positive"
    ]


def _normalize_cell_list(values: list[str]) -> str:
    return "; ".join(values)


def _check_package_doc_existence(layout: PackageLayout, errors: list[str]) -> None:
    for path in (
        layout.scenario_catalog_path,
        layout.paired_ledger_path,
        layout.axis_table_path,
        layout.burden_table_path,
        layout.host_split_table_path,
        layout.evidence_note_path,
        layout.failure_taxonomy_path,
    ):
        if not path.is_file():
            errors.append(f"missing package doc: {path}")


def _check_family_matrix(layout: PackageLayout, errors: list[str]) -> None:
    rows = _section_rows(layout.scenario_catalog_path, "Scenario Family Coverage Matrix")
    observed = {row["scenario_family_id"]: row for row in rows}
    if set(observed) != set(EXPECTED_FAMILY_IDS):
        errors.append("scenario family coverage ids drifted from the J1 contract")
        return
    for family_id, expected in EXPECTED_FAMILY_IDS.items():
        row = observed[family_id]
        if row["evidence_state"] != expected["evidence_state"]:
            errors.append(f"{family_id} evidence_state drifted to {row['evidence_state']}")
    if "thrash_control" in observed and "too narrow" not in observed["thrash_control"]["notes"]:
        errors.append("thrash_control row no longer states that burden is too narrow at package level")


def _check_j2_targets(layout: PackageLayout, errors: list[str]) -> None:
    rows = _section_rows(layout.scenario_catalog_path, "J2 Gap-Closure Target Inventory")
    observed = {row["proposed_scenario_id"]: row for row in rows}
    if set(observed) != set(EXPECTED_J2_TARGETS):
        errors.append("J2 target ids drifted from the agreed gap-closure inventory")
        return
    for target_id, expected in EXPECTED_J2_TARGETS.items():
        row = observed[target_id]
        if row["scenario_family_id"] != expected["scenario_family_id"]:
            errors.append(f"{target_id} family drifted to {row['scenario_family_id']}")
        if row["host_family"] != expected["host_family"]:
            errors.append(f"{target_id} host drifted to {row['host_family']}")
        expected_state = "missing" if target_id == "scenario_uncertainty_claude_01" else "current"
        if row["planned_evidence_state"] != expected_state:
            errors.append(f"{target_id} planned_evidence_state drifted to {row['planned_evidence_state']}")


def _check_recorded_pairs(layout: PackageLayout, errors: list[str]) -> None:
    rows = real_pair_rows(layout)
    if len(rows) != 48:
        errors.append(f"expected 48 recorded usable pairs, found {len(rows)}")
    expected_scenarios = {
        "scenario_thrash_reference_01",
        "scenario_thrash_gemini_01",
        "scenario_thrash_openai_01",
        "scenario_uncertainty_reference_01",
        "scenario_uncertainty_gemini_01",
        "scenario_uncertainty_openai_01",
        "scenario_host_reference_01",
        "scenario_host_gemini_01",
        "scenario_host_openai_01",
        "scenario_host_claude_01",
        "scenario_branch_reference_01",
        "scenario_branch_openai_01",
        "scenario_branch_claude_01",
        "scenario_burden_reference_01",
        "scenario_burden_openai_01",
        "scenario_burden_claude_01",
    }
    if {row["scenario_id"] for row in rows} != expected_scenarios:
        errors.append("recorded mediation pair coverage drifted from the current 9 scenario-host cells")
    for row in rows:
        if row["pair_status"] != "usable":
            errors.append(f"{row['paired_episode_set_id']} is no longer marked usable")
        if row["failure_tags"] != "none":
            errors.append(f"{row['paired_episode_set_id']} unexpectedly carries failure tags: {row['failure_tags']}")
        for ref_key in ("baseline_packet_ref", "mediated_packet_ref"):
            if not (layout.repo_root / row[ref_key]).is_file():
                errors.append(f"missing run packet ref for {row['paired_episode_set_id']}: {row[ref_key]}")


def _check_axis_tables(layout: PackageLayout, errors: list[str]) -> None:
    headings = (
        ("Reduced Thrashing", "reduced thrashing"),
        ("Better Branch Discipline", "better branch discipline"),
        ("Better Uncertainty Handling", "better uncertainty handling"),
        ("Lower Visible Burden At Equal Task Value", "lower visible burden at equal task value"),
        ("Better Host-Specialized Realization", "better host-specialized realization"),
    )
    for heading, axis_name in headings:
        rows = _section_rows(layout.axis_table_path, heading)
        if len(rows) != 16:
            errors.append(f"{heading} should have 16 scenario-host rows, found {len(rows)}")
        for row in rows:
            if row["current_verdict"] not in ALLOWED_VERDICTS:
                errors.append(
                    f"{heading} has invalid verdict {row['current_verdict']} for {row['scenario_id']}/{row['host_family']}"
                )
        candidate_cells = _candidate_cells(layout, heading)
        prefixes = EXPECTED_AXIS_FAMILIES[axis_name]
        if isinstance(prefixes, str):
            prefixes = (prefixes,)
        if any(
            not any(cell.split("/")[0].startswith(prefix) for prefix in prefixes)
            for cell in candidate_cells
        ):
            errors.append(f"{heading} candidate-positive cells drifted outside the expected scenario family")

    summary_rows = _section_rows(layout.axis_table_path, "Package Verdict Summary")
    gap_rows = _section_rows(layout.axis_table_path, "Exact Missing-Evidence Delta")
    note_gap_rows = _section_rows(layout.evidence_note_path, "Exact Missing-Evidence Delta")
    summary_verdicts = {row["axis"]: row["current_package_verdict"] for row in summary_rows}
    if summary_verdicts != EXPECTED_PACKAGE_VERDICTS:
        errors.append("package mediation verdict summary drifted from the accepted insufficient baseline")
    if [row["axis"] for row in gap_rows] != [row["axis"] for row in note_gap_rows]:
        errors.append("axis-table and evidence-note missing-evidence delta sections drifted on axis coverage")
    for row in gap_rows:
        axis = row["axis"]
        expected_cells = _normalize_cell_list(
            _candidate_cells(
                layout,
                {
                    "reduced thrashing": "Reduced Thrashing",
                    "better branch discipline": "Better Branch Discipline",
                    "better uncertainty handling": "Better Uncertainty Handling",
                    "lower visible burden at equal task value": "Lower Visible Burden At Equal Task Value",
                    "better host-specialized realization": "Better Host-Specialized Realization",
                }[axis],
            )
        )
        if row["current_candidate_positive_cells"] != expected_cells:
            errors.append(f"{axis} candidate-positive cell list drifted from the actual section rows")


def _check_burden_refs(layout: PackageLayout, errors: list[str]) -> None:
    rows = _section_rows(layout.burden_table_path, "Comparison Table")
    candidate_positive = [
        f"{row['scenario_id']}/{row['host_family']}"
        for row in rows
        if row["current_verdict"] == "candidate_positive"
    ]
    if not any(cell.split("/")[0].startswith("scenario_burden_") for cell in candidate_positive):
        errors.append("burden candidate-positive cells no longer include the dedicated non-thrash burden family")
    for row in rows:
        if row["current_verdict"] == "candidate_positive":
            for field_name in ("baseline_burden_refs", "mediated_burden_refs"):
                refs = [
                    ref.strip()
                    for ref in row[field_name].split(",")
                    if ref.strip() and ref.strip() != "none"
                ]
                if len(refs) != 3:
                    errors.append(
                        f"{row['scenario_id']}/{row['host_family']} should carry exactly 3 {field_name} refs"
                    )
                for ref in refs:
                    if not (layout.repo_root / ref).is_file():
                        errors.append(f"missing burden ref for {row['scenario_id']}/{row['host_family']}: {ref}")
    gap_rows = _section_rows(layout.burden_table_path, "Exact Burden Gap")
    if len(gap_rows) != 1 or gap_rows[0]["gap_id"] != "non_thrash_equal_value_burden_family":
        errors.append("exact burden gap section drifted from the single J1 burden blocker")


def _check_host_matrix(layout: PackageLayout, errors: list[str]) -> None:
    rows = _section_rows(layout.host_split_table_path, "Current Host Matrix")
    observed = {row["host_family"]: row for row in rows}
    if set(observed) != set(EXPECTED_HOST_MATRIX):
        errors.append("host matrix drifted from the expected four-host J1 surface")
        return
    for host_family, expected in EXPECTED_HOST_MATRIX.items():
        row = observed[host_family]
        if row["committed_package_state"] != expected["committed_package_state"]:
            errors.append(f"{host_family} committed_package_state drifted to {row['committed_package_state']}")
        if row["j2_priority"] != expected["j2_priority"]:
            errors.append(f"{host_family} j2_priority drifted to {row['j2_priority']}")
    if "partial_or_contaminated" not in observed["gemini"]["current_live_note"]:
        errors.append("gemini host matrix row no longer preserves explicit partial_or_contaminated live truth")
    if "current" != observed["claude"]["committed_package_state"]:
        errors.append("claude current mediation coverage is no longer explicit in the host matrix")


def _check_failure_taxonomy(layout: PackageLayout, errors: list[str]) -> None:
    observed = {
        row.strip()
        for row in read(layout.failure_taxonomy_path).splitlines()
        if row.startswith("### `")
    }
    observed = {row[5:-1] for row in observed}
    if observed != ALLOWED_FAILURE_TAGS:
        errors.append("mediation failure taxonomy tags drifted from the expected set")


def _check_evidence_note(layout: PackageLayout, errors: list[str]) -> None:
    text = read(layout.evidence_note_path)
    required_snippets = (
        "The accepted J3 decision is that mediation is now justified for one bounded experimental seam.",
        "The accepted package-level decision is recorded in `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`.",
        "Branch-discipline evidence no longer derives only from `thrash_control`.",
        "Lower-visible-burden evidence is no longer confined to the `thrash_control` scenario family.",
        "Gemini remains explicit as partial/contaminated where needed and is not hidden behind pooled summaries.",
    )
    for snippet in required_snippets:
        if snippet not in text:
            errors.append(f"evidence note missing snippet: {snippet}")
    rerun_rows = _section_rows(layout.evidence_note_path, "Next Rerun Contract")
    if [row["target_id"] for row in rerun_rows] != EXPECTED_RERUN_TARGET_IDS:
        errors.append("next rerun contract drifted from the agreed J2 target ids")


def check_package(layout: PackageLayout = DEFAULT_LAYOUT) -> list[str]:
    errors: list[str] = []
    _check_package_doc_existence(layout, errors)
    if errors:
        return errors
    _check_family_matrix(layout, errors)
    _check_j2_targets(layout, errors)
    _check_recorded_pairs(layout, errors)
    _check_axis_tables(layout, errors)
    _check_burden_refs(layout, errors)
    _check_host_matrix(layout, errors)
    _check_failure_taxonomy(layout, errors)
    _check_evidence_note(layout, errors)
    return errors


def emit_summary(layout: PackageLayout = DEFAULT_LAYOUT) -> str:
    summary_rows = _section_rows(layout.axis_table_path, "Package Verdict Summary")
    rerun_rows = _section_rows(layout.evidence_note_path, "Next Rerun Contract")
    lines = ["# Mediation Evidence Package Summary", "", "## Package Verdicts"]
    for row in summary_rows:
        lines.append(f"- {row['axis']}: `{row['current_package_verdict']}`")
    lines.extend(["", "## Next Rerun Contract"])
    for row in rerun_rows:
        lines.append(
            f"- `{row['target_id']}` on {row['preferred_hosts']}: {row['minimum_pairs']} because {row['reason']}"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check or summarize the committed mediation evidence package."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the mediation evidence package docs and refs.",
    )
    parser.add_argument(
        "--emit-summary",
        action="store_true",
        help="Print a normalized markdown summary of the current package.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Optional repo root override for checker tests.",
    )
    args = parser.parse_args(argv)

    layout = build_layout(args.repo_root) if args.repo_root is not None else DEFAULT_LAYOUT

    if not args.check and not args.emit_summary:
        args.check = True

    if args.check:
        errors = check_package(layout)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("mediation evidence package: ok")

    if args.emit_summary:
        print(emit_summary(layout), end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
