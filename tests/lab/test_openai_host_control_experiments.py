"""Focused tests for the internal-only OpenAI host-control ablation wrapper."""

from __future__ import annotations

import pytest

from cortex.hosts.openai.host_control import OpenAIHostControlRequest
from lab.openai_host_control_experiments import (
    OpenAIHostControlAblationConfig,
    run_openai_host_control_experiment,
)
from cortex.sre.verified_work import VerificationOutcome, WorkContract
from tests.product._verified_work_fixtures import VALID_FILE_MAP, render_full_files_result


def _work_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=max_repair_turns,
    )


def test_run_openai_host_control_experiment_defaults_to_accepted_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def _fake_run_openai_host_control(request, session=None, *, transport=None):
        seen["request"] = request
        seen["session"] = session
        seen["transport"] = transport
        return "result", "session"

    monkeypatch.setattr(
        "lab.openai_host_control_experiments.run_openai_host_control",
        _fake_run_openai_host_control,
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        work_contract=_work_contract(),
    )

    result = run_openai_host_control_experiment(
        request,
        ablation_config=OpenAIHostControlAblationConfig(),
    )

    assert result == ("result", "session")
    assert seen["request"] == request


def test_run_openai_host_control_experiment_can_disable_visible_contract_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered = render_full_files_result(VALID_FILE_MAP)
    seen: dict[str, object] = {}

    def transport(request, *, previous_response_id=None, input_text_override=None):
        seen["input_text"] = request.input_text
        seen["previous_response_id"] = previous_response_id
        seen["input_text_override"] = input_text_override
        return [
            {"type": "response.created", "session_id": "oa-ablate", "response_id": "resp-1"},
            {
                "type": "response.output_text.delta",
                "session_id": "oa-ablate",
                "response_id": "resp-1",
                "delta": rendered,
            },
            {"type": "response.completed", "session_id": "oa-ablate", "response_id": "resp-1"},
        ]

    monkeypatch.setattr(
        "lab.openai_host_control_experiments.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=tuple(VALID_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=11,
                pytest_failed=0,
            ),
        ),
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        work_contract=_work_contract(max_repair_turns=0),
    )

    result, session = run_openai_host_control_experiment(
        request,
        transport=transport,
        ablation_config=OpenAIHostControlAblationConfig(visible_contract_binding="off"),
    )

    assert seen["input_text"] == "build bookmarks app"
    assert result.attempt_count == 1
    assert session.next_recommended_move == "continue"


def test_run_openai_host_control_experiment_disables_repair_when_verification_binding_is_off(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    broken_result = render_full_files_result(
        {
            **VALID_FILE_MAP,
            "src/bookmarks_api/main.py": "from fastapi import FastAPI\napp = FastAPI(\n",
        }
    )
    calls: list[dict[str, object]] = []

    def transport(request, *, previous_response_id=None, input_text_override=None):
        calls.append(
            {
                "previous_response_id": previous_response_id,
                "input_text_override": input_text_override,
            }
        )
        return [
            {"type": "response.created", "session_id": "oa-ablate-repair", "response_id": "resp-1"},
            {
                "type": "response.output_text.delta",
                "session_id": "oa-ablate-repair",
                "response_id": "resp-1",
                "delta": broken_result,
            },
            {"type": "response.completed", "session_id": "oa-ablate-repair", "response_id": "resp-1"},
        ]

    monkeypatch.setattr(
        "lab.openai_host_control_experiments.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_FILE_MAP,
            VerificationOutcome(
                status="failed",
                failure_class="import_smoke_failed",
                parsed_paths=tuple(VALID_FILE_MAP),
                import_smoke_ok=False,
                import_smoke_excerpt="E   SyntaxError",
                first_failure_excerpt="E   SyntaxError",
            ),
        ),
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        work_contract=_work_contract(max_repair_turns=1),
    )

    result, _session = run_openai_host_control_experiment(
        request,
        transport=transport,
        ablation_config=OpenAIHostControlAblationConfig(
            verification_binding="off",
            repair_turn="on",
        ),
    )

    assert len(calls) == 1
    assert result.attempt_count == 1


def test_run_openai_host_control_experiment_uses_minimal_repair_ticket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_result = render_full_files_result(
        {
            **VALID_FILE_MAP,
            "src/bookmarks_api/main.py": "from fastapi import FastAPI\napp = FastAPI(\n",
        }
    )
    second_result = render_full_files_result(VALID_FILE_MAP)
    seen: list[str] = []

    def transport(request, *, previous_response_id=None, input_text_override=None):
        if input_text_override is not None:
            seen.append(input_text_override)
        if previous_response_id is None:
            return [
                {"type": "response.created", "session_id": "oa-ablate-ticket", "response_id": "resp-1"},
                {
                    "type": "response.output_text.delta",
                    "session_id": "oa-ablate-ticket",
                    "response_id": "resp-1",
                    "delta": first_result,
                },
                {"type": "response.completed", "session_id": "oa-ablate-ticket", "response_id": "resp-1"},
            ]
        return [
            {"type": "response.created", "session_id": "oa-ablate-ticket", "response_id": "resp-2"},
            {
                "type": "response.output_text.delta",
                "session_id": "oa-ablate-ticket",
                "response_id": "resp-2",
                "delta": second_result,
            },
            {"type": "response.completed", "session_id": "oa-ablate-ticket", "response_id": "resp-2"},
        ]

    outcomes = iter(
        (
            (
                VALID_FILE_MAP,
                VerificationOutcome(
                    status="failed",
                    failure_class="import_smoke_failed",
                    parsed_paths=("src/bookmarks_api/main.py",),
                    import_smoke_ok=False,
                    import_smoke_excerpt="E   SyntaxError",
                    first_failure_excerpt="E   SyntaxError",
                ),
            ),
            (
                VALID_FILE_MAP,
                VerificationOutcome(
                    status="passed",
                    failure_class=None,
                    parsed_paths=tuple(VALID_FILE_MAP),
                    import_smoke_ok=True,
                    pytest_ok=True,
                    pytest_exit_code=0,
                    pytest_passed=11,
                    pytest_failed=0,
                ),
            ),
        )
    )
    monkeypatch.setattr(
        "lab.openai_host_control_experiments.verify_verified_work_result",
        lambda result_text, contract, **kwargs: next(outcomes),
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        work_contract=_work_contract(max_repair_turns=1),
    )

    result, _session = run_openai_host_control_experiment(
        request,
        transport=transport,
        ablation_config=OpenAIHostControlAblationConfig(repair_ticket_style="minimal"),
    )

    assert result.attempt_count == 2
    assert len(seen) == 1
    assert "what failed: import_smoke_failed" in seen[0]
    assert "repair scope: src/bookmarks_api/main.py" in seen[0]
    assert "import_smoke_excerpt:" not in seen[0]
