"""Tracked integration gate debt placeholders.

These placeholders reserve the active-plan integration surfaces, but they do not
count as landed gate rows. See `docs/CORTEX_V2_PHASE_GATES_2.md`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass(frozen=True, slots=True)
class IntegrationGateDebt:
    status: str
    owner: str
    gate_row: str


_INTEGRATION_GATE_DEBT = {
    "cheap-path integration": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/cheap-path integration",
    ),
    "candidate-bearing integration": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/candidate-bearing integration",
    ),
    "full commitment integration": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/full commitment integration",
    ),
    "degradation roundtrip": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/degradation roundtrip",
    ),
    "firewall integration": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/firewall integration",
    ),
    "driver-to-core-to-sre smoke": IntegrationGateDebt(
        status="open",
        owner="host-integration closeout seam",
        gate_row="2:first-host-vertical/driver-to-core-to-sre smoke",
    ),
}


def _phase_gate_placeholder(surface_name: str) -> None:
    debt = _INTEGRATION_GATE_DEBT[surface_name]
    pytest.xfail(
        "Tracked phase-gate placeholder: "
        f"{surface_name} status={debt.status} "
        f"owner={debt.owner} gate_row={debt.gate_row}. "
        "See docs/CORTEX_V2_PHASE_GATES_2.md."
    )


def test_cheap_path_integration_placeholder() -> None:
    _phase_gate_placeholder("cheap-path integration")


def test_candidate_bearing_integration_placeholder() -> None:
    _phase_gate_placeholder("candidate-bearing integration")


def test_full_commitment_integration_placeholder() -> None:
    _phase_gate_placeholder("full commitment integration")


def test_degradation_roundtrip_placeholder() -> None:
    _phase_gate_placeholder("degradation roundtrip")


def test_firewall_integration_placeholder() -> None:
    _phase_gate_placeholder("firewall integration")


def test_driver_to_core_to_sre_smoke_placeholder() -> None:
    _phase_gate_placeholder("driver-to-core-to-sre smoke")
