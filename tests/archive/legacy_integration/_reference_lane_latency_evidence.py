"""Emit candidate refreshed latency evidence for the landed reference lane."""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.archive.legacy_integration.test_reference_lane_latency import LatencyEvidenceSnapshot


def serialize_reference_lane_latency_snapshot(
    snapshot: "LatencyEvidenceSnapshot",
    *,
    warmup_count: int,
    measured_iterations_per_row: int,
    p95_method: str,
    exclusions: str,
    measured_surfaces: tuple[str, ...],
    supporting_test_surface: str,
) -> dict[str, object]:
    return {
        "measurement_date": snapshot.measurement_date,
        "environment": snapshot.environment_note,
        "method": snapshot.measurement_method,
        "warmup_count": warmup_count,
        "measured_iterations_per_row": measured_iterations_per_row,
        "p95_method": p95_method,
        "exclusions": exclusions,
        "measured_surfaces": list(measured_surfaces),
        "supporting_test_surface": supporting_test_surface,
        "rows": [
            {
                "gate_row": row.gate_row,
                "median_ms": round(row.median_ms, 4),
                "p95_ms": round(row.p95_ms, 4),
                "target_median_ms": row.target_median_ms,
                "target_p95_ms": row.target_p95_ms,
                "target_met": row.target_met,
            }
            for row in snapshot.rows
        ],
    }


def emit_reference_lane_latency_candidate() -> None:
    from tests.archive.legacy_integration.test_reference_lane_latency import (
        EXCLUSIONS_NOTE,
        ITERATION_COUNT,
        MEASURED_SURFACES,
        P95_METHOD,
        WARMUP_COUNT,
        SUPPORTING_TEST_SURFACE,
        collect_reference_lane_latency,
    )

    json.dump(
        serialize_reference_lane_latency_snapshot(
            collect_reference_lane_latency(),
            warmup_count=WARMUP_COUNT,
            measured_iterations_per_row=ITERATION_COUNT,
            p95_method=P95_METHOD,
            exclusions=EXCLUSIONS_NOTE,
            measured_surfaces=MEASURED_SURFACES,
            supporting_test_surface=SUPPORTING_TEST_SURFACE,
        ),
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")


if __name__ == "__main__":
    emit_reference_lane_latency_candidate()
