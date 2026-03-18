"""Latency evidence collection for landed reference-host/Core/SRE paths."""

from __future__ import annotations

import math
import platform
import statistics
import time
from dataclasses import dataclass

from cortex.core.commitments import (
    CommitmentStatus,
)
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.drivers.reference_host_neutral import (
    NeutralContinuationCode,
    evaluate_reference_host_neutral,
)
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from tests.integration._reference_lane import (
    candidate_bearing_event,
    cheap_path_event,
    full_commitment_event,
    provenance_manifest_for,
    reference_environment_handle,
)

ITERATION_COUNT = 400
WARMUP_COUNT = 40

LATENCY_TARGETS_MS = {
    "cheap-path latency evidence": {"median_ms": 5.0, "p95_ms": 20.0},
    "candidate-bearing latency evidence": {"median_ms": 15.0, "p95_ms": 50.0},
    "full commitment latency evidence": {"median_ms": 75.0, "p95_ms": 250.0},
    "neutral SRE scoring latency evidence": {"median_ms": 2.0, "p95_ms": 10.0},
}


@dataclass(frozen=True, slots=True)
class LatencyRowEvidence:
    gate_row: str
    iteration_count: int
    warmup_count: int
    median_ms: float
    p95_ms: float
    target_median_ms: float
    target_p95_ms: float
    target_met: bool


@dataclass(frozen=True, slots=True)
class LatencyEvidenceSnapshot:
    measurement_date: str
    measurement_method: str
    environment_note: str
    rows: tuple[LatencyRowEvidence, ...]


def collect_reference_lane_latency() -> LatencyEvidenceSnapshot:
    environment_handle = reference_environment_handle()
    provenance_manifest = provenance_manifest_for("artifact-1")
    scorecard = AllocationScorecard(
        scores=(
            AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
            AllocationScore(SoftControlFamily.CHECK, 1.05),
            AllocationScore(SoftControlFamily.SEEK_CONTEXT, 0.9),
        ),
        activation_threshold=0.1,
    )

    _assert_cheap_path()
    _assert_candidate_bearing_path(environment_handle)
    _assert_full_commitment_path(environment_handle, provenance_manifest)
    _assert_neutral_sre_path(scorecard)

    rows = (
        _measure_row(
            "cheap-path latency evidence",
            lambda: evaluate_reference_host_neutral(*cheap_path_event()),
        ),
        _measure_row(
            "candidate-bearing latency evidence",
            lambda: evaluate_reference_host_commitment(
                *candidate_bearing_event(),
                environment_handle=environment_handle,
            ),
        ),
        _measure_row(
            "full commitment latency evidence",
            lambda: evaluate_reference_host_commitment(
                *full_commitment_event(commitment_id="commit-1"),
                environment_handle=environment_handle,
                provenance_manifest=provenance_manifest,
            ),
        ),
        _measure_row(
            "neutral SRE scoring latency evidence",
            lambda: neutral_dominance_decision(scorecard),
        ),
    )

    return LatencyEvidenceSnapshot(
        measurement_date="2026-03-18",
        measurement_method="time.perf_counter_ns over in-process warmup + fixed iteration loops",
        environment_note=(
            f"{platform.system()} {platform.release()}, "
            f"Python {platform.python_version()}, "
            "in-process only; excludes host network/model latency and external tool runtime cost."
        ),
        rows=rows,
    )


def test_reference_lane_latency_evidence_is_structurally_produced() -> None:
    snapshot = collect_reference_lane_latency()

    assert snapshot.measurement_date == "2026-03-18"
    assert snapshot.measurement_method.startswith("time.perf_counter_ns")
    assert "excludes host network/model latency" in snapshot.environment_note
    assert {row.gate_row for row in snapshot.rows} == set(LATENCY_TARGETS_MS)
    assert all(row.iteration_count == ITERATION_COUNT for row in snapshot.rows)
    assert all(row.warmup_count == WARMUP_COUNT for row in snapshot.rows)
    assert all(row.median_ms > 0.0 for row in snapshot.rows)
    assert all(row.p95_ms >= row.median_ms for row in snapshot.rows)


def _measure_row(gate_row: str, fn: callable) -> LatencyRowEvidence:
    for _ in range(WARMUP_COUNT):
        fn()

    samples_ns = [_measure_once(fn) for _ in range(ITERATION_COUNT)]
    samples_ms = [sample / 1_000_000 for sample in samples_ns]
    targets = LATENCY_TARGETS_MS[gate_row]
    median_ms = statistics.median(samples_ms)
    p95_ms = _percentile(samples_ms, 0.95)

    return LatencyRowEvidence(
        gate_row=gate_row,
        iteration_count=ITERATION_COUNT,
        warmup_count=WARMUP_COUNT,
        median_ms=median_ms,
        p95_ms=p95_ms,
        target_median_ms=targets["median_ms"],
        target_p95_ms=targets["p95_ms"],
        target_met=median_ms <= targets["median_ms"] and p95_ms <= targets["p95_ms"],
    )


def _measure_once(fn: callable) -> int:
    start_ns = time.perf_counter_ns()
    fn()
    end_ns = time.perf_counter_ns()
    return end_ns - start_ns


def _percentile(samples: list[float], percentile: float) -> float:
    ordered = sorted(samples)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def _assert_cheap_path() -> None:
    result = evaluate_reference_host_neutral(*cheap_path_event())
    assert result.neutral_decision.allowed is True
    assert result.neutral_decision.result_code is NeutralContinuationCode.NEUTRAL_ALLOWED


def _assert_candidate_bearing_path(environment_handle: object) -> None:
    result = evaluate_reference_host_commitment(
        *candidate_bearing_event(),
        environment_handle=environment_handle,
    )
    assert result.candidate is not None
    assert result.verdict is None


def _assert_full_commitment_path(
    environment_handle: object,
    provenance_manifest: object,
) -> None:
    result = evaluate_reference_host_commitment(
        *full_commitment_event(commitment_id="commit-1"),
        environment_handle=environment_handle,
        provenance_manifest=provenance_manifest,
    )
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED


def _assert_neutral_sre_path(scorecard: AllocationScorecard) -> None:
    decision = neutral_dominance_decision(scorecard)
    assert decision.selected_family is SoftControlFamily.NEUTRAL
