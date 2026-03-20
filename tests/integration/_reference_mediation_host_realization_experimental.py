"""Build or emit the experimental reference-host mediated host-realization comparator."""

from __future__ import annotations

import sys

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
    "docs/mediation_evidence/reference/"
    "scenario_host_reference_01__experimental_mediated__run_001.md"
)
_REVIEWER_NOTE = (
    "This is experimental mediated evidence only within the first recorded reference "
    "host-realization pair. It remains reference-only, does not justify mediation, "
    "and package-level evidence notes govern any verdict."
)


def build_reference_host_realization_comparator_snapshot() -> dict[str, object]:
    baseline_snapshot = build_reference_lane_packet_example_snapshot()
    mediated_snapshot = build_reference_mediated_lane_packet_example_snapshot()
    baseline_specialization = build_reference_host_realization_specialization_snapshot(
        clearly_superior=False,
    )
    mediated_specialization = build_reference_host_realization_specialization_snapshot(
        clearly_superior=True,
    )

    assert baseline_snapshot["dispatch_lane"] == mediated_snapshot["dispatch_lane"]
    assert baseline_snapshot["verdict_status"] == mediated_snapshot["verdict_status"]
    assert baseline_snapshot["packet_kind"] == mediated_snapshot["packet_kind"]
    assert baseline_snapshot["withheld_fields"] == mediated_snapshot["withheld_fields"]
    assert baseline_snapshot["contradiction_refs"] == mediated_snapshot["contradiction_refs"]
    assert baseline_snapshot["degradation_refs"] == mediated_snapshot["degradation_refs"]
    assert baseline_specialization["selected_family"] == "seek-context"
    assert mediated_specialization["selected_family"] == "seek-context"
    assert baseline_specialization["host_opportunity_refs"] == ["mcp.query"]
    assert mediated_specialization["host_opportunity_refs"] == ["mcp.query"]
    assert baseline_specialization["preferred_opportunity_ref"] is None
    assert mediated_specialization["preferred_opportunity_ref"] == "mcp.query"
    assert baseline_specialization["direct_opportunity_specialization_used"] is False
    assert mediated_specialization["direct_opportunity_specialization_used"] is True

    return {
        "paired_episode_set_id": "pair_reference_host_001",
        "selected_family": "seek-context",
        "host_opportunity_refs": ["mcp.query"],
        "baseline_direct_opportunity_specialization_used": 0,
        "mediated_direct_opportunity_specialization_used": 1,
        "baseline_packet_kind": baseline_snapshot["packet_kind"],
        "mediated_packet_kind": mediated_snapshot["packet_kind"],
        "baseline_verdict_status": baseline_snapshot["verdict_status"],
        "mediated_verdict_status": mediated_snapshot["verdict_status"],
        "withheld_fields": baseline_snapshot["withheld_fields"],
        "contradiction_refs": baseline_snapshot["contradiction_refs"],
        "degradation_refs": baseline_snapshot["degradation_refs"],
    }


def build_reference_host_realization_mediated_packet() -> PacketSnapshot:
    snapshot = build_reference_mediated_lane_packet_example_snapshot()
    specialization = snapshot["opportunity_specialization"]

    assert isinstance(specialization, dict)
    assert specialization["selected_family"] == "seek-context"
    assert specialization["preferred_opportunity_ref"] == "mcp.query"
    assert specialization["direct_opportunity_specialization_used"] is True
    assert specialization["host_opportunity_refs"] == ["mcp.query"]
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
        run_id="reference_host_realization_mediated_run_001",
        paired_episode_set_id="pair_reference_host_001",
        scenario_family="host_realization",
        task_value_rubric_id="task_value_equal_host_realization",
        approval_or_environment_context_id="env_boundary_sensitive",
        variant="experimental_mediated",
        scenario_inputs={
            "starting_request_or_event": (
                "`ApprovalResult` with `commitment_id=commit-packet-1` and "
                "`session_id=packet-session-1`"
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
                "This mediated packet is part of one host-realization comparator pair, "
                "but it is not a branch-control comparison.",
                "One host-realization pair is below the three-pair threshold and does "
                "not establish any thrash verdict.",
            ),
            "Better Branch Discipline": (
                "This mediated packet changes no branch trajectory and records no "
                "branch-discipline lift by itself.",
                "One host-realization pair is below the three-pair threshold and does "
                "not establish any branch-discipline verdict.",
            ),
            "Better Uncertainty Handling": (
                "This packet preserves contradiction and degradation explicitly on the "
                "same certified publication surface used by the baseline.",
                "One host-realization pair is below the three-pair threshold and does "
                "not establish any uncertainty-handling verdict.",
            ),
            "Lower Visible Burden At Equal Task Value": (
                "The pair holds the same certified completion class and truth boundary, "
                "but this packet carries no AUX burden artifact.",
                "The equal-value gate can pass without producing any lower-burden claim.",
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
            "This packet is the mediated side of `pair_reference_host_001`. One pair "
            "does not justify mediation; package-level evidence notes govern verdicts."
        ),
        reviewer_note=_REVIEWER_NOTE,
    )


REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS = {
    REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_PATH: (
        build_reference_host_realization_mediated_packet
    ),
}


def emit_reference_mediated_host_realization_candidate() -> None:
    for relative_path, builder in REFERENCE_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS.items():
        sys.stdout.write(f"--- {relative_path}\n")
        sys.stdout.write(render_reference_mediation_packet(relative_path, builder()))


if __name__ == "__main__":
    emit_reference_mediated_host_realization_candidate()
