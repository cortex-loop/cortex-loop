"""Latency evidence collection for landed reference-host/Core/SRE paths."""

from __future__ import annotations

import math
import platform
import re
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.drivers.reference_host_neutral import evaluate_reference_host_neutral
from cortex.sre.policy import neutral_dominance_decision
from tests.conformance.integration._reference_lane_latency_evidence import (
    serialize_reference_lane_latency_snapshot,
)
from tests.conformance.integration._reference_lane import (
    assert_reference_candidate_bearing_without_verdict,
    assert_reference_cheap_path_neutral_allowed,
    assert_reference_full_commitment_certified,
    assert_reference_neutral_sre_selected,
    candidate_bearing_event,
    cheap_path_event,
    evaluate_reference_candidate_bearing_case,
    evaluate_reference_cheap_path_case,
    evaluate_reference_full_commitment_case,
    full_commitment_event,
    provenance_manifest_for,
    reference_neutral_scorecard,
    reference_environment_handle,
)

ITERATION_COUNT = 400
WARMUP_COUNT = 40
MEASUREMENT_DATE = "2026-03-18"
MEASUREMENT_METHOD = "time.perf_counter_ns over in-process warmup plus fixed iteration loops"
P95_METHOD = "nearest-rank over recorded samples"
EXCLUSIONS_NOTE = (
    "host network/model latency and external tool runtime cost are excluded"
)
SUPPORTING_TEST_SURFACE = (
    "tests/integration/test_reference_lane_latency.py::"
    "test_reference_lane_latency_evidence_is_structurally_produced"
)
LATENCY_DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "lab"
    / "CORTEX_V2_LATENCY_EVIDENCE_2.md"
)
MEASURED_SURFACES = (
    'cheap path: `evaluate_reference_host_neutral("ContextLoad", ...)`',
    'candidate-bearing path: `evaluate_reference_host_commitment("ApprovalRequest", ...)`',
    'full commitment path: `evaluate_reference_host_commitment("ApprovalResult", ..., provenance_manifest=...)`',
    "neutral SRE scoring: `neutral_dominance_decision(...)`",
)

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


@dataclass(frozen=True, slots=True)
class CommittedLatencyRow:
    gate_row: str
    median_ms: float
    p95_ms: float
    target_median_ms: float
    target_p95_ms: float
    target_met: bool


@dataclass(frozen=True, slots=True)
class CommittedLatencyEvidence:
    measurement_date: str
    environment: str
    method: str
    warmup_count: int
    measured_iterations_per_row: int
    p95_method: str
    exclusions: str
    rows: tuple[CommittedLatencyRow, ...]
    measured_surfaces: tuple[str, ...]
    supporting_test_surface: str


def collect_reference_lane_latency() -> LatencyEvidenceSnapshot:
    environment_handle = reference_environment_handle()
    provenance_manifest = provenance_manifest_for("artifact-1")
    scorecard = reference_neutral_scorecard()

    assert_reference_cheap_path_neutral_allowed(evaluate_reference_cheap_path_case())
    assert_reference_candidate_bearing_without_verdict(
        evaluate_reference_candidate_bearing_case()
    )
    assert_reference_full_commitment_certified(
        evaluate_reference_full_commitment_case(
            commitment_id="commit-1",
            provenance_reference_id="artifact-1",
        )
    )
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
        measurement_date=MEASUREMENT_DATE,
        measurement_method=MEASUREMENT_METHOD,
        environment_note=(
            f"{platform.system()} {platform.release()}, "
            f"Python {platform.python_version()}, "
            f"in-process only; excludes {EXCLUSIONS_NOTE}."
        ),
        rows=rows,
    )


def test_reference_lane_latency_evidence_is_structurally_produced() -> None:
    snapshot = collect_reference_lane_latency()

    assert snapshot.measurement_date == MEASUREMENT_DATE
    assert snapshot.measurement_method == MEASUREMENT_METHOD
    assert "excludes host network/model latency" in snapshot.environment_note
    assert {row.gate_row for row in snapshot.rows} == set(LATENCY_TARGETS_MS)
    assert all(row.iteration_count == ITERATION_COUNT for row in snapshot.rows)
    assert all(row.warmup_count == WARMUP_COUNT for row in snapshot.rows)
    assert all(row.median_ms > 0.0 for row in snapshot.rows)
    assert all(row.p95_ms >= row.median_ms for row in snapshot.rows)


def test_reference_lane_latency_evidence_matches_committed_doc() -> None:
    committed = _load_committed_latency_evidence()
    snapshot = collect_reference_lane_latency()
    candidate = serialize_reference_lane_latency_snapshot(
        snapshot,
        warmup_count=WARMUP_COUNT,
        measured_iterations_per_row=ITERATION_COUNT,
        p95_method=P95_METHOD,
        exclusions=EXCLUSIONS_NOTE,
        measured_surfaces=MEASURED_SURFACES,
        supporting_test_surface=SUPPORTING_TEST_SURFACE,
    )
    live_rows = {row["gate_row"]: row for row in candidate["rows"]}

    assert committed.measurement_date == candidate["measurement_date"]
    assert committed.method == candidate["method"]
    assert committed.environment in str(candidate["environment"])
    assert committed.warmup_count == candidate["warmup_count"]
    assert committed.measured_iterations_per_row == candidate["measured_iterations_per_row"]
    assert committed.p95_method == candidate["p95_method"]
    assert committed.exclusions == candidate["exclusions"]
    assert committed.measured_surfaces == tuple(candidate["measured_surfaces"])
    assert committed.supporting_test_surface == candidate["supporting_test_surface"]
    assert tuple(live_rows) == tuple(row.gate_row for row in committed.rows)

    for row in committed.rows:
        live_row = live_rows[row.gate_row]
        assert row.target_median_ms == live_row["target_median_ms"]
        assert row.target_p95_ms == live_row["target_p95_ms"]
        assert row.target_met is live_row["target_met"]
        _assert_latency_row_satisfies_committed_targets(
            gate_row=row.gate_row,
            median_ms=row.median_ms,
            p95_ms=row.p95_ms,
            target_median_ms=row.target_median_ms,
            target_p95_ms=row.target_p95_ms,
        )
        _assert_latency_row_satisfies_committed_targets(
            gate_row=str(live_row["gate_row"]),
            median_ms=float(live_row["median_ms"]),
            p95_ms=float(live_row["p95_ms"]),
            target_median_ms=float(live_row["target_median_ms"]),
            target_p95_ms=float(live_row["target_p95_ms"]),
        )


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


def _assert_neutral_sre_path(scorecard) -> None:
    assert_reference_neutral_sre_selected(neutral_dominance_decision(scorecard))


def _load_committed_latency_evidence() -> CommittedLatencyEvidence:
    text = LATENCY_DOC_PATH.read_text(encoding="utf-8")
    rows = tuple(_parse_committed_latency_rows(text))

    return CommittedLatencyEvidence(
        measurement_date=_extract_field(text, "Date"),
        environment=_extract_measurement_note(text, "environment"),
        method=_normalize_doc_measurement_text(_extract_measurement_note(text, "method")),
        warmup_count=int(_extract_measurement_note(text, "warmup count")),
        measured_iterations_per_row=int(
            _extract_measurement_note(text, "measured iterations per row")
        ),
        p95_method=_extract_measurement_note(text, "p95 method"),
        exclusions=_extract_measurement_note(text, "exclusions"),
        rows=rows,
        measured_surfaces=_extract_bullets(text, "Measured surfaces"),
        supporting_test_surface=_strip_wrapping_backticks(
            _extract_single_bullet(text, "Supporting test surface")
        ),
    )


def _parse_committed_latency_rows(text: str) -> list[CommittedLatencyRow]:
    pattern = re.compile(
        r"^\| (?P<gate_row>.+?) \| (?P<median_ms>\d+\.\d{4}) \| (?P<p95_ms>\d+\.\d{4}) "
        r"\| (?P<target_median_ms>\d+\.\d{4}) \| (?P<target_p95_ms>\d+\.\d{4}) "
        r"\| (?P<target_met>yes|no) \|$",
        re.MULTILINE,
    )
    return [
        CommittedLatencyRow(
            gate_row=match.group("gate_row"),
            median_ms=float(match.group("median_ms")),
            p95_ms=float(match.group("p95_ms")),
            target_median_ms=float(match.group("target_median_ms")),
            target_p95_ms=float(match.group("target_p95_ms")),
            target_met=match.group("target_met") == "yes",
        )
        for match in pattern.finditer(text)
    ]


def _extract_field(text: str, field_name: str) -> str:
    match = re.search(rf"^{re.escape(field_name)}: (.+)$", text, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Missing field in committed latency doc: {field_name}")
    return match.group(1).strip()


def _extract_measurement_note(text: str, label: str) -> str:
    match = re.search(
        rf"^-\s+{re.escape(label)}: (.+)$",
        _extract_section(text, "Measurement note"),
        re.MULTILINE,
    )
    if match is None:
        raise AssertionError(
            f"Missing measurement note field in committed latency doc: {label}"
        )
    return match.group(1).strip()


def _extract_bullets(text: str, heading: str) -> tuple[str, ...]:
    section = _extract_section(text, heading)
    return tuple(
        line.removeprefix("- ").strip()
        for line in section.splitlines()
        if line.startswith("- ")
    )


def _extract_single_bullet(text: str, heading: str) -> str:
    bullets = _extract_bullets(text, heading)
    if len(bullets) != 1:
        raise AssertionError(
            f"Expected exactly one bullet under '{heading}', found {len(bullets)}"
        )
    return bullets[0]


def _extract_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^{re.escape(heading)}:\n(?P<section>.*?)(?:\n\n[A-Z][^\n]*:|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Missing section in committed latency doc: {heading}")
    return match.group("section").strip()


def _normalize_doc_measurement_text(value: str) -> str:
    return value.replace("`", "")


def _strip_wrapping_backticks(value: str) -> str:
    return value.removeprefix("`").removesuffix("`")


def _assert_latency_row_satisfies_committed_targets(
    *,
    gate_row: str,
    median_ms: float,
    p95_ms: float,
    target_median_ms: float,
    target_p95_ms: float,
) -> None:
    assert median_ms > 0.0, f"{gate_row} median_ms must stay positive"
    assert p95_ms >= median_ms, f"{gate_row} p95_ms must stay >= median_ms"
    assert median_ms <= target_median_ms, (
        f"{gate_row} median_ms exceeded committed target: "
        f"{median_ms:.4f}ms > {target_median_ms:.4f}ms"
    )
    assert p95_ms <= target_p95_ms, (
        f"{gate_row} p95_ms exceeded committed target: "
        f"{p95_ms:.4f}ms > {target_p95_ms:.4f}ms"
    )
