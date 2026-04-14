"""Conformance locks for the OpenAI runtime-step memory re-entry law."""

from __future__ import annotations

from dataclasses import replace

import cortex.hosts.openai.runtime as openai_runtime
import cortex.hosts.reference.runtime as reference_runtime
from cortex.aux.reference_replay import evaluate_aux_reference_q_mem_replay
from cortex.core.envelopes import MetadataField
from cortex.hosts.openai.runtime import run_openai_runtime_step
from cortex.hosts.reference.runtime import run_reference_runtime_step
from cortex.sre.operator_routing import OperatorTaskMode
from cortex.sre.state import ReferenceExecutiveState

from tests.experimental._aux_test_support import (
    make_aux_reference_replay_corpus,
    make_support_snapshot,
)


def test_openai_runtime_step_matches_reference_default_memory_inactivity_without_publication(
    monkeypatch,
) -> None:
    scenario = _reference_replay_scenario("branch-resume-recovery")
    _patch_shared_replay_scenario(monkeypatch, scenario)

    reference = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-no-publication"},
    )
    openai = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "openai-no-publication",
            "response_id": "resp-openai-no-publication",
            "delta": "hello",
        },
    )

    assert _normalized_memory_reentry(
        reference.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    ) == _normalized_memory_reentry(
        openai.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    )
    assert (
        reference.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
            "selected_family_memory_score"
        ]
        == 0.0
    )
    assert (
        openai.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
            "selected_family_memory_score"
        ]
        == 0.0
    )


def test_openai_runtime_step_matches_reference_active_branch_memory_reentry_projection(
    monkeypatch,
) -> None:
    scenario = _reference_replay_scenario("branch-resume-recovery")
    reference_case = _reference_replay_case_result("branch-resume-recovery")
    _patch_shared_replay_scenario(monkeypatch, scenario)

    reference = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-branch-replay"},
        offline_publication=reference_case.publication,
    )
    openai = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "openai-branch-replay",
            "response_id": "resp-openai-branch-replay",
            "delta": "hello",
        },
        offline_publication=_publication_for_host(reference_case.publication, "openai"),
    )

    assert _normalized_memory_reentry(
        reference.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    ) == _normalized_memory_reentry(
        openai.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    )
    assert (
        reference.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
            "selected_family_memory_score"
        ]
        > 0.0
    )
    assert (
        openai.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
            "selected_family_memory_score"
        ]
        > 0.0
    )


def test_openai_runtime_step_matches_reference_resume_contradiction_invalidation_projection(
    monkeypatch,
) -> None:
    scenario = _reference_replay_scenario("branch-resume-recovery")
    reference_case = _reference_replay_case_result("branch-resume-recovery")
    contradiction_snapshot = replace(
        scenario.target_snapshot,
        trace=replace(
            scenario.target_snapshot.trace,
            degradation_records=make_support_snapshot().trace.degradation_records,
        ),
    )
    _patch_shared_replay_scenario(monkeypatch, scenario, support_snapshot=contradiction_snapshot)

    reference = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-branch-contradiction"},
        offline_publication=reference_case.publication,
    )
    openai = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "openai-branch-contradiction",
            "response_id": "resp-openai-branch-contradiction",
            "delta": "hello",
        },
        offline_publication=_publication_for_host(reference_case.publication, "openai"),
    )

    assert _normalized_memory_reentry(
        reference.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    ) == _normalized_memory_reentry(
        openai.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    )


def _patch_shared_replay_scenario(
    monkeypatch,
    scenario,
    *,
    support_snapshot=None,
) -> None:
    resolved_snapshot = (
        support_snapshot if support_snapshot is not None else scenario.target_snapshot
    )
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        reference_runtime,
        "_build_support_snapshot",
        lambda **kwargs: resolved_snapshot,
    )
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: resolved_snapshot,
    )


def _normalized_memory_reentry(memory_reentry: dict[str, object]) -> dict[str, object]:
    return {
        "state": memory_reentry["state"],
        "eligible_families": memory_reentry["eligible_families"],
        "invalidated_families": memory_reentry["invalidated_families"],
        "selected_family_support_refs": memory_reentry["selected_family_support_refs"],
    }


def _publication_for_host(publication, host_name: str):
    return replace(
        publication,
        metadata=tuple(
            MetadataField("host_name", host_name) if field.key == "host_name" else field
            for field in publication.metadata
        ),
    )


def _reference_replay_scenario(scenario_id: str):
    for scenario in make_aux_reference_replay_corpus():
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"Unknown replay scenario {scenario_id!r}.")


def _reference_replay_case_result(scenario_id: str):
    scenario = _reference_replay_scenario(scenario_id)
    return evaluate_aux_reference_q_mem_replay((scenario,)).case_results[0]


def _scenario_executive_state_with_task_mode(
    scenario,
    task_mode: OperatorTaskMode,
) -> ReferenceExecutiveState:
    return replace(
        scenario.executive_state,
        mode_and_gating=replace(
            scenario.executive_state.mode_and_gating,
            task_mode=task_mode,
        ),
    )
