"""Shared parsing helpers for mediation evidence docs and run packets."""

from __future__ import annotations

from pathlib import Path
import sys

TOOLS_ROOT = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from mediation_evidence_common import (
    AXIS_HEADINGS,
    AXIS_TABLE_PATH,
    BURDEN_TABLE_PATH,
    DOCS_ROOT,
    EQUAL_VALUE_GATES,
    EVALUATION_PLAN_PATH,
    EVIDENCE_NOTE_PATH,
    FAILURE_TAXONOMY_PATH,
    HOST_SPLIT_TABLE_PATH,
    MEDIATION_CLAUDE_PACKET_ROOT,
    MEDIATION_GEMINI_PACKET_ROOT,
    MEDIATION_OPENAI_PACKET_ROOT,
    MEDIATION_REFERENCE_PACKET_ROOT,
    PAIRED_LEDGER_PATH,
    PAIR_STATUSES,
    PLACEHOLDER_TOKEN,
    REPO_ROOT,
    SCENARIO_CATALOG_PATH,
    VERDICTS,
    aggregate_pair_counts,
    all_tags_allowed,
    field,
    load_failure_tags,
    load_scenarios,
    parse_bullet_fields,
    parse_markdown_table,
    read,
    real_pair_rows,
    section,
    status,
    subsection,
    supporting_ids,
    tag_set,
)
LAB_DOCS_ROOT = DOCS_ROOT / "lab"
EXPERIMENTAL_DOCS_ROOT = DOCS_ROOT / "experimental"
REFERENCE_MEDIATED_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md"
)
GEMINI_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_GEMINI_LANE_PACKET_EXAMPLE_0.md"
)
GEMINI_MEDIATED_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_GEMINI_MEDIATED_LANE_PACKET_EXAMPLE_0.md"
)
OPENAI_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md"
)
OPENAI_MEDIATED_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_OPENAI_MEDIATED_LANE_PACKET_EXAMPLE_0.md"
)
REFERENCE_BASELINE_INDEX_PATH = LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_BASELINE_INDEX_0.md"
GEMINI_BASELINE_INDEX_PATH = LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_BASELINE_INDEX_0.md"
OPENAI_BASELINE_INDEX_PATH = LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_BASELINE_INDEX_0.md"
REFERENCE_THRASH_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0.md"
)
REFERENCE_THRASH_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md"
)
REFERENCE_UNCERTAINTY_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_BASIS_NOTE_0.md"
)
REFERENCE_UNCERTAINTY_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_REPLICATION_NOTE_0.md"
)
GEMINI_UNCERTAINTY_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md"
)
GEMINI_UNCERTAINTY_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_REPLICATION_NOTE_0.md"
)
GEMINI_THRASH_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_THRASH_BASIS_NOTE_0.md"
)
GEMINI_THRASH_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_THRASH_REPLICATION_NOTE_0.md"
)
OPENAI_UNCERTAINTY_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_BASIS_NOTE_0.md"
)
OPENAI_UNCERTAINTY_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_REPLICATION_NOTE_0.md"
)
OPENAI_THRASH_BASIS_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_THRASH_BASIS_NOTE_0.md"
)
OPENAI_THRASH_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_THRASH_REPLICATION_NOTE_0.md"
)
REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md"
)
REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0.md"
)
GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md"
)
GEMINI_HOST_REALIZATION_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_REPLICATION_NOTE_0.md"
)
OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md"
)
OPENAI_HOST_REALIZATION_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_REPLICATION_NOTE_0.md"
)
CLAUDE_LANE_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_CLAUDE_LANE_PACKET_EXAMPLE_0.md"
)
CLAUDE_MEDIATED_PACKET_EXAMPLE_DOC_PATH = (
    EXPERIMENTAL_DOCS_ROOT / "CORTEX_V2_CLAUDE_MEDIATED_LANE_PACKET_EXAMPLE_0.md"
)
CLAUDE_BASELINE_INDEX_PATH = LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_CLAUDE_BASELINE_INDEX_0.md"
CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md"
)
CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_PATH = (
    LAB_DOCS_ROOT / "CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_0.md"
)
REFERENCE_THRASH_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_thrash_reference_01__baseline_non_mediated__run_001.md"
)
REFERENCE_UNCERTAINTY_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md"
)
REFERENCE_HOST_REALIZATION_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_host_reference_01__baseline_non_mediated__run_001.md"
)
REFERENCE_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_host_reference_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_host_reference_01__experimental_mediated__run_001.md"
)
REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_host_reference_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_UNCERTAINTY_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md"
)
GEMINI_HOST_REALIZATION_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_host_gemini_01__baseline_non_mediated__run_001.md"
)
GEMINI_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_host_gemini_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_host_gemini_01__experimental_mediated__run_001.md"
)
GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_host_gemini_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_THRASH_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_thrash_gemini_01__baseline_non_mediated__run_001.md"
)
OPENAI_UNCERTAINTY_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md"
)
OPENAI_THRASH_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_thrash_openai_01__baseline_non_mediated__run_001.md"
)
OPENAI_HOST_REALIZATION_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_host_openai_01__baseline_non_mediated__run_001.md"
)
OPENAI_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_host_openai_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_host_openai_01__experimental_mediated__run_001.md"
)
OPENAI_HOST_REALIZATION_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_host_openai_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
CLAUDE_HOST_REALIZATION_PACKET_PATH = (
    MEDIATION_CLAUDE_PACKET_ROOT
    / "scenario_host_claude_01__baseline_non_mediated__run_001.md"
)
CLAUDE_HOST_REALIZATION_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_CLAUDE_PACKET_ROOT
        / f"scenario_host_claude_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATH = (
    MEDIATION_CLAUDE_PACKET_ROOT
    / "scenario_host_claude_01__experimental_mediated__run_001.md"
)
CLAUDE_HOST_REALIZATION_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_CLAUDE_PACKET_ROOT
        / f"scenario_host_claude_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_THRASH_MEDIATED_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_thrash_reference_01__experimental_mediated__run_001.md"
)
REFERENCE_UNCERTAINTY_MEDIATED_PACKET_PATH = (
    MEDIATION_REFERENCE_PACKET_ROOT
    / "scenario_uncertainty_reference_01__experimental_mediated__run_001.md"
)
REFERENCE_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_uncertainty_reference_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_uncertainty_gemini_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_thrash_gemini_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_THRASH_BASELINE_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / (
            "scenario_thrash_gemini_01__baseline_non_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_uncertainty_openai_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_thrash_openai_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_THRASH_BASELINE_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / (
            "scenario_thrash_openai_01__baseline_non_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_UNCERTAINTY_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_uncertainty_reference_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_uncertainty_gemini_01__experimental_mediated__run_001.md"
)
GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_uncertainty_gemini_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_THRASH_MEDIATED_PACKET_PATH = (
    MEDIATION_GEMINI_PACKET_ROOT
    / "scenario_thrash_gemini_01__experimental_mediated__run_001.md"
)
GEMINI_THRASH_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / f"scenario_thrash_gemini_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
GEMINI_THRASH_MEDIATED_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_GEMINI_PACKET_ROOT
        / (
            "scenario_thrash_gemini_01__experimental_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_uncertainty_openai_01__experimental_mediated__run_001.md"
)
OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_uncertainty_openai_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_THRASH_MEDIATED_PACKET_PATH = (
    MEDIATION_OPENAI_PACKET_ROOT
    / "scenario_thrash_openai_01__experimental_mediated__run_001.md"
)
OPENAI_THRASH_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / f"scenario_thrash_openai_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
OPENAI_THRASH_MEDIATED_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_OPENAI_PACKET_ROOT
        / (
            "scenario_thrash_openai_01__experimental_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_THRASH_BASELINE_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_thrash_reference_01__baseline_non_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_THRASH_BASELINE_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / (
            "scenario_thrash_reference_01__baseline_non_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_THRASH_MEDIATED_PACKET_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / f"scenario_thrash_reference_01__experimental_mediated__run_{pair_key}.md"
    )
    for pair_key in ("001", "002", "003")
}
REFERENCE_THRASH_MEDIATED_BURDEN_PATHS = {
    pair_key: (
        MEDIATION_REFERENCE_PACKET_ROOT
        / (
            "scenario_thrash_reference_01__experimental_mediated__run_"
            f"{pair_key}__aux_burden.md"
        )
    )
    for pair_key in ("001", "002", "003")
}

RUN_PACKET_INVARIANT_FIELDS = (
    "same_host_family_preserved",
    "same_starting_task_framing_preserved",
    "same_core_commitment_boundary_preserved",
    "same_evidence_or_publication_surface_preserved",
    "same_success_rubric_preserved",
)


def parse_run_packet(path: Path) -> dict[str, object]:
    text = read(path)
    lift_axis_text = section(text, "Lift-Axis Observations")
    return {
        "path": path,
        "status": status(path),
        "header": parse_bullet_fields(section(text, "Header")),
        "variant_metadata": parse_bullet_fields(section(text, "Variant Metadata")),
        "invariant_lock": parse_bullet_fields(section(text, "Invariant Lock")),
        "scenario_inputs": parse_bullet_fields(section(text, "Scenario Inputs")),
        "run_outputs": parse_bullet_fields(section(text, "Run Outputs")),
        "artifact_refs": parse_bullet_fields(section(text, "Artifact Refs")),
        "lift_axes": {
            heading: parse_bullet_fields(subsection(lift_axis_text, heading))
            for heading in AXIS_HEADINGS
        },
        "exclusions": parse_bullet_fields(section(text, "Exclusions Or Unusable-Pair Notes")),
        "reviewer_note": parse_bullet_fields(section(text, "Reviewer Note")),
    }


def parse_aux_burden_artifact(path: Path) -> dict[str, object]:
    text = read(path)
    return {
        "path": path,
        "status": status(path),
        "header": parse_bullet_fields(section(text, "Header")),
        "variant_metadata": parse_bullet_fields(section(text, "Variant Metadata")),
        "aux_burden_report": parse_bullet_fields(section(text, "Aux Burden Report")),
        "metadata": parse_bullet_fields(section(text, "Metadata")),
        "derivation": parse_bullet_fields(section(text, "Derivation")),
    }


def packet_without_path(packet: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in packet.items() if key != "path"}


def _unwrap_code_literal(value: str) -> str:
    if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
        return value[1:-1]
    return value
