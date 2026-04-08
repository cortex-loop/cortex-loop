"""Focused tests for the Cortex-law conformance harness."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import cortex_conformance as conformance
from cortex.sre.verified_work import VerificationOutcome, WorkContract


def _work_contract() -> WorkContract:
    return WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )


def test_train_charter_requires_all_fields() -> None:
    with pytest.raises(ValueError, match="cortex_invariant"):
        conformance.TrainCharter(
            cortex_invariant="",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:service_api",
            conformance_surfaces=("openai:service_api",),
            kill_criteria=("cut if no lift",),
        )

    charter = conformance.TrainCharter(
        cortex_invariant="bounded verified-work law",
        borrowed_mechanism="tiny verifier",
        primary_proving_wiring="openai:service_api",
        conformance_surfaces=("openai:service_api", "claude:operator_cli"),
        kill_criteria=("cut if no lift",),
    )

    assert charter.as_payload()["primary_proving_wiring"] == "openai:service_api"


def test_contract_pack_exposes_required_train_charter() -> None:
    pack = conformance.ContractPack(
        contract_pack="verified_work_bookmarks_v1",
        prompt_text="build bookmarks app",
        work_contract=_work_contract(),
        train_charter=conformance.TrainCharter(
            cortex_invariant="bounded verified-work law",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:service_api",
            conformance_surfaces=("openai:service_api",),
            kill_criteria=("cut if no lift",),
        ),
        shipping_default="openai:service_api",
    )

    payload = pack.as_payload()

    assert payload["contract_pack"] == "verified_work_bookmarks_v1"
    assert payload["train_charter"]["cortex_invariant"] == "bounded verified-work law"


def test_strongest_native_surface_matches_current_wiring_order() -> None:
    pack = conformance.active_contract_pack()

    assert conformance.strongest_native_surface("openai", pack) == "service_api"
    assert conformance.strongest_native_surface("claude", pack) == "operator_cli"
    assert conformance.strongest_native_surface("gemini", pack) == "operator_cli"


def test_preflight_surface_distinguishes_env_blocked_and_unwired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(conformance, "api_key_presence", lambda: {"OPENAI_API_KEY": False, "GEMINI_API_KEY": False})
    monkeypatch.setattr(conformance, "command_exists", lambda command: command != "gemini")

    openai_probe = conformance.preflight_surface("openai", "service_api")
    gemini_probe = conformance.preflight_surface("gemini", "operator_cli")
    unknown_probe = conformance.preflight_surface("claude", "service_api")  # type: ignore[arg-type]

    assert openai_probe.status == "env_blocked"
    assert gemini_probe.status == "env_blocked"
    assert unknown_probe.status == "unwired"

    monkeypatch.setattr(conformance, "command_exists", lambda _command: True)
    gemini_ready_probe = conformance.preflight_surface("gemini", "operator_cli")
    assert gemini_ready_probe.status == "partial"


def test_classify_outcome_divergence_maps_surface_and_brain_failures() -> None:
    passed = VerificationOutcome(status="passed", failure_class=None)
    test_failed = VerificationOutcome(status="failed", failure_class="test_failed")
    output_invalid = VerificationOutcome(status="failed", failure_class="output_invalid", parse_error="bad prefix")

    assert conformance.classify_outcome_divergence(surface="service_api", outcome=passed) == (
        "conformant",
        None,
    )
    assert conformance.classify_outcome_divergence(surface="service_api", outcome=test_failed) == (
        "partial",
        "brain_wiring",
    )
    assert conformance.classify_outcome_divergence(surface="operator_cli", outcome=output_invalid) == (
        "divergent",
        "surface_wiring",
    )


def test_classify_shared_divergence_only_returns_cortex_law_for_repeated_same_failure() -> None:
    results = [
        conformance.ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=3,
            pytest_failed=8,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        ),
        conformance.ConformanceRunResult(
            brain="claude",
            surface="operator_cli",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=2,
            pytest_failed=9,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        ),
    ]

    assert conformance.classify_shared_divergence(results) == "cortex_law"


def test_decide_iteration_outcome_requires_revision_for_shipping_regression() -> None:
    results = [
        conformance.ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=4,
            pytest_failed=7,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        )
    ]

    assert (
        conformance.decide_iteration_outcome(results, shipping_default="openai:service_api")
        == "revise"
    )
