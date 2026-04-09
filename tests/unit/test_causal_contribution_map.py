"""Focused tests for causal contribution classification."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from causal_contribution_map import (
    ContributionRunReading,
    OutputQualityMetrics,
    VerifiedWorkMetrics,
    classify_component,
    has_material_delta,
)


def _baseline() -> ContributionRunReading:
    return ContributionRunReading(
        label="baseline",
        output_quality=OutputQualityMetrics(
            cortex_vs_raw=0.4,
            cortex_vs_tooling_only=0.4,
            cortex_objective_pass_count=3,
            cortex_hidden_quality_pass_count=2,
        ),
        verified_work=VerifiedWorkMetrics(
            conformant_pack_count=3,
            first_attempt_pass_count=3,
            repair_conversion_count=0,
        ),
    )


def test_has_material_delta_obeys_locked_thresholds() -> None:
    baseline = _baseline()
    candidate = ContributionRunReading(
        label="candidate",
        output_quality=OutputQualityMetrics(
            cortex_vs_raw=0.6,
            cortex_vs_tooling_only=0.4,
            cortex_objective_pass_count=3,
            cortex_hidden_quality_pass_count=2,
        ),
        verified_work=baseline.verified_work,
    )

    assert has_material_delta(baseline=baseline, candidate=candidate) is True


def test_classify_component_positive_when_turning_off_repeat_stably_hurts() -> None:
    baseline = _baseline()
    degraded = ContributionRunReading(
        label="candidate",
        output_quality=OutputQualityMetrics(
            cortex_vs_raw=0.0,
            cortex_vs_tooling_only=0.2,
            cortex_objective_pass_count=2,
            cortex_hidden_quality_pass_count=1,
        ),
        verified_work=VerifiedWorkMetrics(
            conformant_pack_count=2,
            first_attempt_pass_count=2,
            repair_conversion_count=0,
        ),
    )

    assert classify_component(baseline=baseline, runs=(degraded, degraded)) == "positive"


def test_classify_component_mixed_when_one_surface_helps_and_another_hurts() -> None:
    baseline = _baseline()
    mixed = ContributionRunReading(
        label="candidate",
        output_quality=OutputQualityMetrics(
            cortex_vs_raw=0.6,
            cortex_vs_tooling_only=0.4,
            cortex_objective_pass_count=3,
            cortex_hidden_quality_pass_count=2,
        ),
        verified_work=VerifiedWorkMetrics(
            conformant_pack_count=2,
            first_attempt_pass_count=2,
            repair_conversion_count=0,
        ),
    )

    assert classify_component(baseline=baseline, runs=(mixed,)) == "mixed"
