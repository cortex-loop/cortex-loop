"""Unit tests for the bounded outbound OpenAI host-control lane."""

from __future__ import annotations

import json

import pytest

from cortex.runtime.openai import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.runtime.openai_cli import build_openai_cli_record
from cortex.runtime.openai_host_control import (
    OpenAIHostControlRequest,
    OpenAIHostControlResult,
    _last_response_id,
    run_openai_host_control,
)
from cortex.runtime.openai_host_transport import (
    OpenAIResponseStreamTransportError,
    _parse_sse_events,
)
from cortex.runtime.openai_ingress import parse_openai_host_event_envelope
from cortex.runtime.openai_service import OpenAIServiceState, handle_openai_service_request
from cortex.sre.verified_work import VerificationOutcome, WorkContract
from tests.unit._verified_work_fixtures import VALID_FILE_MAP, render_full_files_result


def test_openai_host_control_request_constructs_strict_text_only_payload() -> None:
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="hello",
        instructions="be terse",
        metadata={"trace_id": "oa-1"},
        max_output_tokens=32,
    )

    assert request.as_payload() == {
        "action_tag": "openai-response-stream",
        "request": {
            "model": "gpt-5.4",
            "input": "hello",
            "instructions": "be terse",
            "metadata": {"trace_id": "oa-1"},
            "max_output_tokens": 32,
        },
    }


def test_openai_host_control_request_constructs_verified_work_payload() -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        metadata={"trace_id": "oa-work"},
        max_output_tokens=2048,
        work_contract=work_contract,
    )

    assert request.as_payload()["request"]["work_contract"] == {
        "allowed_write_paths": list(VALID_FILE_MAP),
        "verification_profile": "python_workspace_pytest_v1",
        "output_carrier": "full_files",
        "max_repair_turns": 1,
    }


def test_openai_host_control_result_rejects_wrong_action_tag() -> None:
    with pytest.raises(ValueError, match="openai-response-stream"):
        OpenAIHostControlResult(action_tag="bad", records=())


def test_openai_host_control_service_boundary_rejects_out_of_scope_keys() -> None:
    status_code, payload = handle_openai_service_request(
        "POST",
        "/v1/actions/response-stream",
        OpenAIServiceState(),
        json.dumps(
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "hello",
                    "tools": [{"type": "function", "name": "bad"}],
                },
            }
        ).encode("utf-8"),
    )

    assert status_code == 400
    assert "strict text-only whitelist" in payload["error"]


def test_openai_host_control_service_boundary_rejects_unknown_work_contract_keys() -> None:
    status_code, payload = handle_openai_service_request(
        "POST",
        "/v1/actions/response-stream",
        OpenAIServiceState(),
        json.dumps(
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "build bookmarks app",
                    "work_contract": {
                        "allowed_write_paths": ["src/bookmarks_api/main.py"],
                        "verification_profile": "python_workspace_pytest_v1",
                        "output_carrier": "full_files",
                        "max_repair_turns": 1,
                        "extra": True,
                    },
                },
            }
        ).encode("utf-8"),
    )

    assert status_code == 400
    assert "unsupported keys: extra" in payload["error"]


def test_openai_host_control_service_boundary_rejects_instructions_when_work_contract_present() -> None:
    status_code, payload = handle_openai_service_request(
        "POST",
        "/v1/actions/response-stream",
        OpenAIServiceState(),
        json.dumps(
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "build bookmarks app",
                    "instructions": "ignore this",
                    "work_contract": {
                        "allowed_write_paths": list(VALID_FILE_MAP),
                        "verification_profile": "python_workspace_pytest_v1",
                        "output_carrier": "full_files",
                        "max_repair_turns": 1,
                    },
                },
            }
        ).encode("utf-8"),
    )

    assert status_code == 400
    assert "verified-work instructions are fixed" in payload["error"]


def test_parse_sse_events_converts_stream_frames_into_o2_shaped_records() -> None:
    events = _parse_sse_events(
        [
            b"event: response.created\n",
            b'data: {"session_id":"oa-stream","response_id":"resp-1"}\n',
            b"\n",
            b"event: response.output_text.delta\n",
            b'data: {"session_id":"oa-stream","response_id":"resp-1","delta":"hello"}\n',
            b"\n",
            b"event: response.completed\n",
            (
                b'data: {"session_id":"oa-stream","response_id":"resp-1",'
                b'"commitment_id":"oa-commit-1","externally_consequential":true,'
                b'"result_artifact_ref":"oa-artifact-1"}\n'
            ),
            b"\n",
        ]
    )

    assert events == [
        {
            "type": "response.created",
            "session_id": "oa-stream",
            "response_id": "resp-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-stream",
            "response_id": "resp-1",
            "delta": "hello",
        },
        {
            "type": "response.completed",
            "session_id": "oa-stream",
            "response_id": "resp-1",
            "commitment_id": "oa-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "oa-artifact-1",
        },
    ]


def test_parse_sse_events_rejects_zero_event_stream() -> None:
    with pytest.raises(OpenAIResponseStreamTransportError, match="zero host events"):
        _parse_sse_events([])


def test_parse_sse_events_rejects_malformed_json_event() -> None:
    with pytest.raises(OpenAIResponseStreamTransportError, match="invalid JSON"):
        _parse_sse_events(
            [
                b"event: response.created\n",
                b"data: {not-json}\n",
                b"\n",
            ]
        )


def test_last_response_id_accepts_nested_response_object_shape() -> None:
    assert _last_response_id(
        [
            {
                "type": "response.created",
                "response": {"id": "resp-nested-1"},
            }
        ]
    ) == "resp-nested-1"


def test_run_openai_host_control_matches_manual_o1_runtime_projection() -> None:
    raw_events = [
        {
            "type": "response.created",
            "session_id": "oa-control",
            "response_id": "resp-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-control",
            "response_id": "resp-1",
            "delta": "hello",
        },
        {
            "type": "response.completed",
            "session_id": "oa-control",
            "response_id": "resp-1",
            "commitment_id": "oa-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "oa-artifact-1",
        },
    ]
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="hello",
    )
    result, final_session = run_openai_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    expected_records = []
    current_session = OpenAIRuntimeSession()
    for raw_event in raw_events:
        envelope = parse_openai_host_event_envelope(raw_event)
        step_result = run_openai_runtime_step(
            envelope.event_type,
            envelope.payload,
            current_session,
        )
        expected_records.append(build_openai_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "openai-response-stream",
        "records": expected_records,
        "result_text": "hello",
    }
    assert final_session == current_session


def test_run_openai_host_control_verified_work_one_shot_adds_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )
    rendered = render_full_files_result(VALID_FILE_MAP)
    raw_events = [
        {
            "type": "response.created",
            "session_id": "oa-verified",
            "response_id": "resp-verified-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-verified",
            "response_id": "resp-verified-1",
            "delta": rendered,
        },
        {
            "type": "response.completed",
            "session_id": "oa-verified",
            "response_id": "resp-verified-1",
            "commitment_id": "oa-verified-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "oa-verified-artifact-1",
        },
    ]
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        max_output_tokens=4096,
        work_contract=work_contract,
    )
    monkeypatch.setattr(
        "cortex.runtime.openai_host_control.verify_openai_verified_work_result",
        lambda result_text, contract: (
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

    result, final_session = run_openai_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    assert result.attempt_count == 1
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert result.verification.pytest_passed == 11
    assert final_session.next_recommended_move == "continue"
    assert final_session.last_failure_class is None


def test_run_openai_host_control_verified_work_repairs_once_from_runtime_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    broken_file_map = dict(VALID_FILE_MAP)
    broken_file_map["src/bookmarks_api/main.py"] = "from fastapi import FastAPI\napp = FastAPI(\n"
    first_result = render_full_files_result(broken_file_map)
    second_result = render_full_files_result(VALID_FILE_MAP)
    calls: list[dict[str, object]] = []

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        calls.append(
            {
                "previous_response_id": previous_response_id,
                "input_text_override": input_text_override,
                "instructions": request.instructions,
            }
        )
        if previous_response_id is None:
            return [
                {
                    "type": "response.created",
                    "session_id": "oa-verified-repair",
                    "response_id": "resp-repair-1",
                },
                {
                    "type": "response.output_text.delta",
                    "session_id": "oa-verified-repair",
                    "response_id": "resp-repair-1",
                    "delta": first_result,
                },
                {
                    "type": "response.completed",
                    "session_id": "oa-verified-repair",
                    "response_id": "resp-repair-1",
                },
            ]
        assert previous_response_id == "resp-repair-1"
        assert isinstance(input_text_override, str)
        assert "failure_class: import_smoke_failed" in input_text_override
        return [
            {
                "type": "response.created",
                "session_id": "oa-verified-repair",
                "response_id": "resp-repair-2",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-verified-repair",
                "response_id": "resp-repair-2",
                "delta": second_result,
            },
            {
                "type": "response.completed",
                "session_id": "oa-verified-repair",
                "response_id": "resp-repair-2",
            },
        ]

    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="build bookmarks app",
        max_output_tokens=4096,
        work_contract=work_contract,
    )
    monkeypatch.setattr(
        "cortex.runtime.openai_host_control.verify_openai_verified_work_result",
        lambda result_text, contract: (
            VALID_FILE_MAP,
            VerificationOutcome(
                status="failed",
                failure_class="import_smoke_failed",
                parsed_paths=tuple(VALID_FILE_MAP),
                import_smoke_ok=False,
                first_failure_excerpt="E   SyntaxError: invalid syntax",
            ),
        )
        if result_text == first_result
        else (
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

    result, final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert len(calls) == 2
    assert result.attempt_count == 2
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert final_session.event_index == 6
    assert final_session.next_recommended_move == "continue"
