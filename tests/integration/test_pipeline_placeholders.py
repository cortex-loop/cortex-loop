"""Non-operative integration placeholders required before the first host slice."""

import pytest


def _phase_1_placeholder(surface_name: str) -> None:
    pytest.xfail(f"Phase 1 placeholder: {surface_name} is reserved but not implemented yet.")


def test_cheap_path_integration_placeholder() -> None:
    _phase_1_placeholder("cheap-path integration")


def test_candidate_bearing_integration_placeholder() -> None:
    _phase_1_placeholder("candidate-bearing integration")


def test_full_commitment_integration_placeholder() -> None:
    _phase_1_placeholder("full commitment integration")


def test_degradation_roundtrip_placeholder() -> None:
    _phase_1_placeholder("degradation roundtrip")


def test_firewall_integration_placeholder() -> None:
    _phase_1_placeholder("firewall integration")


def test_driver_to_core_to_sre_smoke_placeholder() -> None:
    _phase_1_placeholder("driver-to-core-to-sre smoke")
