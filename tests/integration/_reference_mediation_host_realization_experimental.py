"""Build or emit the experimental reference-host mediated host-realization comparator."""

from __future__ import annotations

import sys

from tests.integration._reference_host_realization_pairs import (
    DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    REFERENCE_HOST_REALIZATION_PAIR_KEYS,
    REFERENCE_HOST_REALIZATION_PAIR_SPECS,
)
from tests.integration._reference_lane_packet_example import (
    build_reference_lane_packet_example_snapshot,
)
from tests.integration._reference_mediated_lane_packet_example import (
    build_reference_host_realization_specialization_snapshot,
    build_reference_mediated_lane_packet_example_snapshot,
)
from tests.integration._reference_mediation_baseline_packets import (
    PacketSnapshot,
    build_reference_mediation_packet,
    render_reference_mediation_packet,
)

REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH = (
    REFERENCE_HOST_REALIZATION_PAIR_SPECS[
        DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY
    ].mediated_packet_path
)
REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATHS = {
    pair_key: REFERENCE_HOST_REALIZATION_PAIR_SPECS[pair_key].mediated_packet_path
    for pair_key in REFERENCE_HOST_REALIZATION_PAIR_KEYS
}
_REVIEWER_NOTE = (
    "This is experimental mediated evidence only within the committed reference "
    "host-realization paired-run series. It remains reference-only, does not justify "
    "mediation, and package-level evidence notes govern any verdict."
)


def build_reference_host_realization_comparator_snapshot(
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
) -> dict[str, object]:
    spec = REFERENCE_HOST_REALIZATION_PAIR_SPECS[pair_key]
    baseline_snapshot = build_reference_lane_packet_example_snapshot(pair_key)
    mediated_snapshot = build_reference_mediated_lane_packet_example_snapshot(pair_key)
    baseline_specialization = build_reference_host_realization_specialization_snapshot(
        pair_key=pair_key,
        clearly_superior=False,
    )
    mediated_specialization = build_reference_host_realization_specialization_snapshot(
        pair_key=pair_key,
        clearly_superior=True,
    )

    assert baseline_snapshot["dispatch_lane"] == mediated_snapshot["dispatch_lane"]
    assert baseline_snapshot["verdict_status"] == mediated_snapshot["verdict_status"]
    assert baseline_snapshot["packet_kind"] == mediated_snapshot["packet_kind"]
    assert baseline_snapshot["withheld_fields"] == mediated_snapshot["withheld_fields"]
    assert baseline_snapshot["contradiction_refs"] == mediated_snapshot["contradiction_refs"]
    assert baseline_snapshot["degradation_refs"] == mediated_snapshot["degradation_refs"]
    assert baseline_snapshot["runtime_control"]["selected_family"] == "seek-context"
    assert mediated_snapshot["runtime_control"]["selected_family"] == "seek-context"
    assert baseline_snapshot["runtime_control"]["realized_family"] == "seek-context"
    assert mediated_snapshot["runtime_control"]["realized_family"] == "seek-context"
    assert baseline_snapshot["runtime_control"]["host_opportunity_refs"] == ["mcp.query"]
    assert mediated_snapshot["runtime_control"]["host_opportunity_refs"] == ["mcp.query"]
    assert baseline_snapshot["runtime_control"]["mediation"]["mediation_identity"] is True
    assert mediated_snapshot["runtime_control"]["mediation"]["mediation_active"] is True
    assert (
        baseline_snapshot["runtime_control"]["mediation"]["selected_family_before_finalization"]
        == "seek-context"
    )
    assert (
        mediated_snapshot["runtime_control"]["mediation"]["selected_family_before_finalization"]
        == "seek-context"
    )
    assert (
        baseline_snapshot["runtime_control"]["mediation"]["selected_family_after_finalization"]
        == "seek-context"
    )
    assert (
        mediated_snapshot["runtime_control"]["mediation"]["selected_family_after_finalization"]
        == "seek-context"
    )
    assert baseline_specialization["selected_family"] == "seek-context"
    assert mediated_specialization["selected_family"] == "seek-context"
    assert baseline_specialization["realized_family"] == "seek-context"
    assert mediated_specialization["realized_family"] == "seek-context"
    assert baseline_specialization["host_opportunity_refs"] == ["mcp.query"]
    assert mediated_specialization["host_opportunity_refs"] == ["mcp.query"]
    assert baseline_specialization["preferred_opportunity_ref"] is None
    assert mediated_specialization["preferred_opportunity_ref"] == "mcp.query"
    assert baseline_specialization["direct_opportunity_specialization_used"] is False
    assert mediated_specialization["direct_opportunity_specialization_used"] is True

    return {
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "candidate_id": spec.candidate_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "baseline_run_id": spec.baseline_run_id,
        "mediated_run_id": spec.mediated_run_id,
        "selected_family": "seek-context",
        "host_opportunity_refs": ["mcp.query"],
        "baseline_direct_opportunity_specialization_used": 0,
        "mediated_direct_opportunity_specialization_used": 1,
        "baseline_packet_kind": baseline_snapshot["packet_kind"],
        "mediated_packet_kind": mediated_snapshot["packet_kind"],
        "baseline_verdict_status": baseline_snapshot["verdict_status"],
        "mediated_verdict_status": mediated_snapshot["verdict_status"],
        "baseline_trace_id": baseline_snapshot["event_trace"]["trace_id"],
        "mediated_trace_id": mediated_snapshot["event_trace"]["trace_id"],
        "baseline_runtime_control": baseline_snapshot["runtime_control"],
        "mediated_runtime_control": mediated_snapshot["runtime_control"],
        "withheld_fields": baseline_snapshot["withheld_fields"],
        "contradiction_refs": baseline_snapshot["contradiction_refs"],
        "degradation_refs": baseline_snapshot["degradation_refs"],
    }


def build_reference_host_realization_mediated_packet(
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
) -> PacketSnapshot:
    spec = REFERENCE_HOST_REALIZATION_PAIR_SPECS[pair_key]
    snapshot = build_reference_mediated_lane_packet_example_snapshot(pair_key)
    specialization = snapshot["opportunity_specialization"]
    runtime_control = snapshot["runtime_control"]

    assert isinstance(specialization, dict)
    assert isinstance(runtime_control, dict)
    assert specialization["selected_family"] == "seek-context"
    assert specialization["realized_family"] == "seek-context"
    assert specialization["preferred_opportunity_ref"] == "mcp.query"
    assert specialization["direct_opportunity_specialization_used"] is True
    assert specialization["host_opportunity_refs"] == ["mcp.query"]
    assert runtime_control["mediation"]["preferred_opportunity_ref"] == "mcp.query"
    assert runtime_control["mediation"]["direct_opportunity_specialization_used"] is True
    assert snapshot["dispatch_lane"] == "full-commitment"
    assert snapshot["verdict_status"] == "certified"
    assert snapshot["packet_kind"] == "current-pair"

    event_trace = snapshot["event_trace"]
    contradiction_refs = snapshot["contradiction_refs"]
    degradation_refs = snapshot["degradation_refs"]
    assert isinstance(event_trace, dict)
    assert isinstance(contradiction_refs, list)
    assert isinstance(degradation_refs, list)
    contradiction_ref = contradiction_refs[0]
    degradation_ref = degradation_refs[0]
    assert isinstance(contradiction_ref, dict)
    assert isinstance(degradation_ref, dict)

    return build_reference_mediation_packet(
        scenario_id="scenario_host_reference_01",
        run_id=spec.mediated_run_id,
        paired_episode_set_id=spec.pair_id,
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        variant="experimental_mediated",
        scenario_inputs={
            "starting_request_or_event": (
                f"`ApprovalResult` with `commitment_id={spec.commitment_id}` and "
                f"`session_id={spec.session_id}`"
            ),
            "host_surface": (
                "reference-host opportunity selection plus commitment-to-eval-packet "
                "publication path"
            ),
            "declared_scenario_goal": (
                "evaluate whether mediation produces any reference-host realization lift "
                "without adding burden or branch churn"
            ),
            "bounded_environment_or_approval_context": (
                "reference-host commitment path with lawful provenance, "
                "contradiction-preserving degradation handling, the committed "
                "reference-lane packet/publication surface, and a bounded host-opportunity "
                "set containing `mcp.query`"
            ),
        },
        run_outputs={
            "outcome_summary": (
                "The mediated reference-host path preserves the same certified "
                "current-pair evaluation packet with explicit contradiction, "
                "degradation, and truthful-withheld fields while directly specializing "
                "`mcp.query` for the selected `seek-context` family."
            ),
            "branch_trajectory_summary": (
                "Single full-commitment publication path only; the only comparator "
                "delta is direct host-native opportunity specialization before packet "
                "publication."
            ),
            "uncertainty_or_brake_summary": (
                "Contradiction and degradation remain explicit in the committed packet "
                "example, and `direct_opportunity_specialization_used=1` remains "
                "explicit for the mediated side of the pair."
            ),
            "burden_summary": "none",
            "host_realization_summary": (
                "Reference-host realization keeps the same selected family "
                "`seek-context`, the same bounded host-opportunity set containing "
                "`mcp.query`, and the same certified `current-pair` publication "
                "surface while changing `direct_opportunity_specialization_used` from "
                "`0` to `1`."
            ),
        },
        artifact_refs={
            "event_trace_refs": str(event_trace["trace_id"]),
            "contradiction_refs": (
                f"{contradiction_ref['source_tag']}:{contradiction_ref['summary']}"
            ),
            "degradation_refs": str(degradation_ref["reason_code"]),
            "aux_burden_refs_if_present": "none",
            "evaluation_packet_refs_if_present": (
                "docs/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md"
            ),
        },
        lift_axis_notes={
            "Reduced Thrashing": (
                "This mediated packet is part of the committed reference "
                "host-realization paired-run series, but it is not a branch-control "
                "comparison.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any thrash verdict.",
            ),
            "Better Branch Discipline": (
                "This mediated packet changes no branch trajectory and records no "
                "branch-discipline lift by itself.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any branch-discipline verdict.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves contradiction and degradation explicitly on the "
                "same certified publication surface used by the baseline.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any uncertainty-handling verdict.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "The pair holds the same certified completion class and truth boundary, "
                "but this packet carries no AUX burden artifact.",
                "Package-level evidence notes govern whether repeated paired evidence is "
                "enough to claim any lower-burden verdict.",
            ),
            "Better Host-Specialized Realization": (
                "This mediated packet directly specializes `mcp.query` for the selected "
                "`seek-context` family while preserving the same certified current-pair "
                "publication surface.",
                "The host-realization metric is "
                "`direct_opportunity_specialization_used=1` on the mediated side of "
                "the pair.",
            ),
        },
        exclusion_notes=(
            f"This packet is the mediated side of `{spec.pair_id}`. A single packet does "
            "not justify mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_REVIEWER_NOTE,
    )


REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS = {
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATHS[pair_key]: (
        lambda pair_key=pair_key: build_reference_host_realization_mediated_packet(pair_key)
    )
    for pair_key in REFERENCE_HOST_REALIZATION_PAIR_KEYS
}


def emit_reference_mediated_host_realization_candidate() -> None:
    for index, (relative_path, builder) in enumerate(
        REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS.items()
    ):
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))
        if index != len(REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS) - 1:
            sys.stdout.write("\n")


if __name__ == "__main__":
    emit_reference_mediated_host_realization_candidate()
