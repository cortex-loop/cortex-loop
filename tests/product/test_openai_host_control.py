"""Unit tests for the bounded outbound OpenAI host-control lane."""

from __future__ import annotations

import json

import pytest

from cortex.aux.publication import (
    OfflineSupportPublication,
    offline_support_publication_as_payload,
)
from cortex.core.envelopes import MetadataField
from cortex.hosts.runtime_context import runtime_context_from_last_feedback
from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.hosts.openai.cli import build_openai_cli_record
from cortex.hosts.openai.host_control import (
    OpenAIHostControlRequest,
    OpenAIHostControlResult,
    _last_response_id,
    run_openai_host_control,
)
from cortex.hosts.openai.host_transport import (
    OpenAIResponseStreamTransportError,
    _parse_sse_events,
)
from cortex.hosts.openai.ingress import parse_openai_host_event_envelope
from cortex.hosts.openai.service import OpenAIServiceState, handle_openai_service_request
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import ReferenceRealizationFeedback
from cortex.sre.operator_routing import OperatorTaskMode
from cortex.sre.verified_work import VerificationOutcome, WorkContract
from tests.product._verified_work_fixtures import (
    VALID_FEATURE_FLAG_FILE_MAP,
    VALID_FILE_MAP,
    VALID_NORMALIZE_PORT_FILE_MAP,
    render_full_files_result,
)
from tests.experimental._aux_test_support import make_support_ref


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

    port_request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="fix normalize_port",
        metadata={"trace_id": "oa-port"},
        max_output_tokens=512,
        work_contract=WorkContract(
            allowed_write_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
            verification_profile="python_workspace_pytest_port_fix_v1",
            output_carrier="full_files",
            max_repair_turns=1,
        ),
    )

    assert port_request.as_payload()["request"]["work_contract"] == {
        "allowed_write_paths": list(VALID_NORMALIZE_PORT_FILE_MAP),
        "verification_profile": "python_workspace_pytest_port_fix_v1",
        "output_carrier": "full_files",
        "max_repair_turns": 1,
    }

    feature_flag_request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="implement feature flags",
        metadata={"trace_id": "oa-flags"},
        max_output_tokens=1024,
        work_contract=WorkContract(
            allowed_write_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
            verification_profile="python_workspace_pytest_feature_flags_v1",
            output_carrier="full_files",
            max_repair_turns=1,
        ),
    )

    assert feature_flag_request.as_payload()["request"]["work_contract"] == {
        "allowed_write_paths": list(VALID_FEATURE_FLAG_FILE_MAP),
        "verification_profile": "python_workspace_pytest_feature_flags_v1",
        "output_carrier": "full_files",
        "max_repair_turns": 1,
    }


def test_openai_host_control_request_emits_non_minimal_audit_intensity_only_when_requested() -> None:
    default_request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="hello",
    )
    focused_request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="hello",
        audit_intensity="focused",
    )

    assert "audit_intensity" not in default_request.as_payload()["request"]
    assert focused_request.as_payload()["request"]["audit_intensity"] == "focused"


def test_openai_host_control_request_emits_offline_publication_only_when_requested() -> None:
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="resume",
        max_output_tokens=64,
        work_contract=WorkContract(
            allowed_write_paths=tuple(VALID_FILE_MAP),
            verification_profile="python_workspace_pytest_v1",
            output_carrier="full_files",
            max_repair_turns=1,
        ),
        offline_publication=_offline_publication(),
        audit_intensity="focused",
    )

    payload = request.as_payload()

    assert tuple(payload["request"]) == (
        "model",
        "input",
        "max_output_tokens",
        "work_contract",
        "offline_publication",
        "audit_intensity",
    )
    assert payload["request"]["offline_publication"] == offline_support_publication_as_payload(
        _offline_publication()
    )


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


def test_openai_host_control_service_boundary_accepts_offline_publication_payload() -> None:
    publication_payload = offline_support_publication_as_payload(_offline_publication())
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
                    "offline_publication": publication_payload,
                },
            }
        ).encode("utf-8"),
        outbound_transport=lambda _: [
            {
                "type": "response.created",
                "session_id": "oa-offline-publication",
                "response_id": "resp-offline-publication-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-offline-publication",
                "response_id": "resp-offline-publication-1",
                "delta": "hello",
            },
        ],
    )

    assert status_code == 200
    assert payload["records"][0]["control_ledger"]["allocation_diagnostics"]["memory_reentry"][
        "target_host_name"
    ] == "openai"


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
            operator_model=request.model,
        )
        expected_records.append(build_openai_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "openai-response-stream",
        "records": expected_records,
        "result_text": "hello",
    }
    assert final_session == current_session


def test_run_openai_host_control_matches_manual_o1_runtime_projection_with_offline_publication() -> None:
    raw_events = [
        {
            "type": "response.created",
            "session_id": "oa-control-memory",
            "response_id": "resp-memory-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-control-memory",
            "response_id": "resp-memory-1",
            "delta": "hello",
        },
    ]
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="hello",
        offline_publication=_offline_publication(),
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
            offline_publication=request.offline_publication,
            operator_model=request.model,
        )
        expected_records.append(build_openai_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "openai-response-stream",
        "records": expected_records,
        "result_text": "hello",
    }
    assert final_session == current_session


def test_run_openai_host_control_adds_runtime_context_to_non_work_instructions() -> None:
    feedback = _runtime_feedback(
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
        host_friction_tags=("capability-view-missing",),
    )
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["instructions"] = request.instructions
        return _basic_response_events("oa-runtime-context", "resp-runtime-context")

    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="finish the migration plan and close if done",
        instructions="be terse",
    )

    run_openai_host_control(
        request,
        session=OpenAIRuntimeSession(last_realization_feedback=feedback),
        transport=transport,
    )

    assert seen["instructions"] is not None
    assert seen["instructions"] == (
        "be terse\n\n"
        "Completion is not supported by the evidence yet. An artifact, a "
        "check, or a narrower claim is still needed before closure holds."
    )
    assert "CORTEX_RUNTIME_CONTEXT_V1" not in seen["instructions"]
    assert "next_call_constraint:" not in seen["instructions"]


def test_run_openai_host_control_clean_feedback_leaves_non_work_request_unchanged() -> None:
    feedback = _runtime_feedback(evidence_progress_class="artifact")
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        seen["instructions"] = request.instructions
        return _basic_response_events(
            "oa-runtime-context-clean",
            "resp-runtime-context-clean",
        )

    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="summarize the verified artifact",
        instructions="be terse",
    )

    run_openai_host_control(
        request,
        session=OpenAIRuntimeSession(last_realization_feedback=feedback),
        transport=transport,
    )

    assert seen["instructions"] == "be terse"


def test_run_openai_host_control_fixture_body_contains_shaped_instructions(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    feedback = _runtime_feedback(
        warning_codes=("continuity-rejected:missing-open-track-ref",),
    )
    context = runtime_context_from_last_feedback(feedback)
    assert context is not None
    fixture = tmp_path / "openai-runtime-context-fixture.json"
    fixture.write_text(
        json.dumps(
            {
                "calls": [
                    {
                        "expected_body": {
                            "model": "gpt-5.4",
                            "input": [
                                {
                                    "role": "user",
                                    "content": "finish and close",
                                }
                            ],
                            "stream": True,
                            "instructions": f"be terse\n\n{context}",
                        },
                        "events": _basic_response_events(
                            "oa-runtime-context-fixture",
                            "resp-runtime-context-fixture",
                        ),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CORTEX_OPENAI_HOST_CONTROL_FIXTURE_PATH", str(fixture))
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="finish and close",
        instructions="be terse",
    )

    result, _session = run_openai_host_control(
        request,
        session=OpenAIRuntimeSession(last_realization_feedback=feedback),
    )

    assert result.result_text == "ok"


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
        "cortex.hosts.openai.host_control.verify_verified_work_result",
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

    result, final_session = run_openai_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    assert result.attempt_count == 1
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert result.verification.pytest_passed == 11
    assert final_session.next_recommended_move == "continue"
    assert final_session.executive_modulator_memory is not None
    assert final_session.last_failure_class is None


def test_run_openai_host_control_verified_work_attaches_workspace_context_to_first_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )
    rendered = render_full_files_result(VALID_FILE_MAP)
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["input_text"] = request.input_text
        seen["instructions"] = request.instructions
        return [
            {
                "type": "response.created",
                "session_id": "oa-verified-context",
                "response_id": "resp-verified-context-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-verified-context",
                "response_id": "resp-verified-context-1",
                "delta": rendered,
            },
            {
                "type": "response.completed",
                "session_id": "oa-verified-context",
                "response_id": "resp-verified-context-1",
            },
        ]

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
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
        max_output_tokens=4096,
        work_contract=work_contract,
    )

    result, _final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert result.attempt_count == 1
    assert seen["input_text"] is not None
    assert "build bookmarks app" in seen["input_text"]
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in seen["input_text"]
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in seen["input_text"]
    assert seen["instructions"] is not None
    assert "No prose around the blocks. No explanations. No code fences." in seen["instructions"]
    assert "Do not" not in seen["instructions"]


def test_run_openai_host_control_verified_work_puts_runtime_context_in_input_not_instructions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )
    feedback = _runtime_feedback(
        warning_codes=("session-rejected:mismatched-session-id:runtime-a",),
        evidence_progress_class="none",
        continuity_progress_class="none",
    )
    rendered = render_full_files_result(VALID_FILE_MAP)
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["input_text"] = request.input_text
        seen["instructions"] = request.instructions
        return [
            {
                "type": "response.created",
                "session_id": "oa-verified-runtime-context",
                "response_id": "resp-verified-runtime-context-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-verified-runtime-context",
                "response_id": "resp-verified-runtime-context-1",
                "delta": rendered,
            },
            {
                "type": "response.completed",
                "session_id": "oa-verified-runtime-context",
                "response_id": "resp-verified-runtime-context-1",
            },
        ]

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
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
        max_output_tokens=4096,
        work_contract=work_contract,
    )

    result, _final_session = run_openai_host_control(
        request,
        session=OpenAIRuntimeSession(last_realization_feedback=feedback),
        transport=transport,
    )

    assert result.attempt_count == 1
    assert seen["input_text"] is not None
    assert "build bookmarks app" in seen["input_text"]
    assert "CORTEX_RUNTIME_CONTEXT_V1" not in seen["input_text"]
    assert "Continuity is not anchored enough for closure" in seen["input_text"]
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in seen["input_text"]
    assert seen["instructions"] is not None
    assert "CORTEX_RUNTIME_CONTEXT_V1" not in seen["instructions"]
    assert "No prose around the blocks. No explanations. No code fences." in seen["instructions"]
    assert "Do not" not in seen["instructions"]


def test_run_openai_host_control_uses_lean_verified_work_contract_for_bounded_brain(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    rendered = render_full_files_result(VALID_FILE_MAP)
    seen: dict[str, object] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["input_text"] = request.input_text
        seen["instructions"] = request.instructions
        seen["max_repair_turns"] = (
            request.work_contract.max_repair_turns if request.work_contract is not None else None
        )
        return [
            {
                "type": "response.created",
                "session_id": "oa-verified-lean",
                "response_id": "resp-verified-lean-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-verified-lean",
                "response_id": "resp-verified-lean-1",
                "delta": rendered,
            },
            {
                "type": "response.completed",
                "session_id": "oa-verified-lean",
                "response_id": "resp-verified-lean-1",
            },
        ]

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
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
        model="gpt-5.3-codex-spark",
        input_text="build bookmarks app",
        max_output_tokens=4096,
        work_contract=work_contract,
    )

    result, _final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert result.attempt_count == 1
    assert seen["max_repair_turns"] == 0
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in str(seen["input_text"])
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" not in str(seen["input_text"])
    assert "The output for this work is protocol blocks for the allowed paths only." in str(
        seen["instructions"]
    )
    assert result.records[0]["operator_route"]["contract_binding_profile"] == "lean"


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
                "request_input_text": request.input_text,
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
        assert "what failed: import_smoke_failed" in input_text_override
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
    verification_calls: list[dict[str, object]] = []

    def _verify_verified_work_result(result_text, contract, **kwargs):
        verification_calls.append(
            {
                "result_text": result_text,
                "contract": contract,
                "kwargs": kwargs,
            }
        )
        if result_text == first_result:
            return (
                broken_file_map,
                VerificationOutcome(
                    status="failed",
                    failure_class="import_smoke_failed",
                    parsed_paths=("src/bookmarks_api/main.py",),
                    import_smoke_ok=False,
                    first_failure_excerpt="E   SyntaxError: invalid syntax",
                ),
            )
        return (
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
        )

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
        _verify_verified_work_result,
    )

    result, final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert len(calls) == 2
    assert result.attempt_count == 2
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in str(calls[0]["request_input_text"])
    assert "src/bookmarks_api/main.py" in str(calls[1]["instructions"])
    assert "src/bookmarks_api/models.py" not in str(calls[1]["instructions"])
    assert "src/bookmarks_api/store.py" not in str(calls[1]["instructions"])
    assert final_session.event_index == 6
    assert final_session.next_recommended_move == "continue"
    assert final_session.executive_modulator_memory is not None
    assert final_session.preservation_state is not None
    assert final_session.preservation_state.task_anchor.startswith(
        "verified-work:python_workspace_pytest_v1:"
    )
    assert "=== CONTEXT FILE:" not in str(calls[1]["input_text_override"])
    assert verification_calls[1]["contract"].allowed_write_paths == ("src/bookmarks_api/main.py",)
    assert verification_calls[1]["kwargs"]["preserved_file_map"] == broken_file_map
    assert verification_calls[1]["kwargs"]["verifier_contract"] == work_contract


def test_run_openai_host_control_verified_work_attaches_normalize_port_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
        verification_profile="python_workspace_pytest_port_fix_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )
    rendered = render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP)
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["input_text"] = request.input_text
        seen["instructions"] = request.instructions
        return [
            {
                "type": "response.created",
                "session_id": "oa-port-context",
                "response_id": "resp-port-context-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-port-context",
                "response_id": "resp-port-context-1",
                "delta": rendered,
            },
            {
                "type": "response.completed",
                "session_id": "oa-port-context",
                "response_id": "resp-port-context-1",
            },
        ]

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_NORMALIZE_PORT_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=2,
                pytest_failed=0,
            ),
        ),
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="fix normalize_port",
        max_output_tokens=4096,
        work_contract=work_contract,
    )

    result, _final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert result.attempt_count == 1
    assert seen["input_text"] is not None
    assert "fix normalize_port" in seen["input_text"]
    assert "=== CONTEXT FILE: src/normalize_port.py ===" in seen["input_text"]
    assert "=== CONTEXT FILE: tests/test_normalize_port.py ===" in seen["input_text"]
    assert seen["instructions"] is not None
    assert "No prose around the blocks. No explanations. No code fences." in seen["instructions"]
    assert "Do not" not in seen["instructions"]


def test_run_openai_host_control_verified_work_normalize_port_repairs_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
        verification_profile="python_workspace_pytest_port_fix_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    broken_file_map = dict(VALID_NORMALIZE_PORT_FILE_MAP)
    broken_file_map["src/normalize_port.py"] = (
        "from __future__ import annotations\n\n\n"
        "def normalize_port(value: int | str) -> int:\n"
        "    port = int(value)\n"
        "    if port < 0:\n"
        "        raise ValueError(\"port must be non-negative\")\n"
        "    if port >= 65535:\n"
        "        raise ValueError(\"port must be <= 65535\")\n"
        "    return port\n"
    )
    first_result = render_full_files_result(broken_file_map)
    second_result = render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP)
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
                "request_input_text": request.input_text,
            }
        )
        if previous_response_id is None:
            return [
                {
                    "type": "response.created",
                    "session_id": "oa-port-repair",
                    "response_id": "resp-port-repair-1",
                },
                {
                    "type": "response.output_text.delta",
                    "session_id": "oa-port-repair",
                    "response_id": "resp-port-repair-1",
                    "delta": first_result,
                },
                {
                    "type": "response.completed",
                    "session_id": "oa-port-repair",
                    "response_id": "resp-port-repair-1",
                },
            ]
        assert previous_response_id == "resp-port-repair-1"
        assert isinstance(input_text_override, str)
        assert "what failed: test_failed" in input_text_override
        return [
            {
                "type": "response.created",
                "session_id": "oa-port-repair",
                "response_id": "resp-port-repair-2",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-port-repair",
                "response_id": "resp-port-repair-2",
                "delta": second_result,
            },
            {
                "type": "response.completed",
                "session_id": "oa-port-repair",
                "response_id": "resp-port-repair-2",
            },
        ]

    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="fix normalize_port",
        max_output_tokens=4096,
        work_contract=work_contract,
    )
    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_NORMALIZE_PORT_FILE_MAP,
            VerificationOutcome(
                status="failed",
                failure_class="test_failed",
                parsed_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=False,
                pytest_exit_code=1,
                pytest_passed=1,
                pytest_failed=1,
                first_failure_excerpt="FAILED tests/test_normalize_port.py::test_accepts_upper_bound_port",
            ),
        )
        if result_text == first_result
        else (
            VALID_NORMALIZE_PORT_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=2,
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
    assert "=== CONTEXT FILE: tests/test_normalize_port.py ===" in str(calls[0]["request_input_text"])
    assert final_session.event_index == 6
    assert final_session.next_recommended_move == "continue"
    assert final_session.executive_modulator_memory is not None
    assert "=== CONTEXT FILE:" not in str(calls[1]["input_text_override"])


def test_run_openai_host_control_verified_work_attaches_feature_flags_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
        verification_profile="python_workspace_pytest_feature_flags_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )
    rendered = render_full_files_result(VALID_FEATURE_FLAG_FILE_MAP)
    seen: dict[str, str | None] = {}

    def transport(
        request: OpenAIHostControlRequest,
        *,
        previous_response_id: str | None = None,
        input_text_override: str | None = None,
    ) -> list[dict[str, object]]:
        assert previous_response_id is None
        assert input_text_override is None
        seen["input_text"] = request.input_text
        seen["instructions"] = request.instructions
        return [
            {
                "type": "response.created",
                "session_id": "oa-feature-flags-context",
                "response_id": "resp-feature-flags-context-1",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-feature-flags-context",
                "response_id": "resp-feature-flags-context-1",
                "delta": rendered,
            },
            {
                "type": "response.completed",
                "session_id": "oa-feature-flags-context",
                "response_id": "resp-feature-flags-context-1",
            },
        ]

    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_FEATURE_FLAG_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=6,
                pytest_failed=0,
            ),
        ),
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="implement feature flags",
        max_output_tokens=4096,
        work_contract=work_contract,
    )

    result, _final_session = run_openai_host_control(
        request,
        transport=transport,
    )

    assert result.attempt_count == 1
    assert seen["input_text"] is not None
    assert "implement feature flags" in seen["input_text"]
    assert "=== CONTEXT FILE: src/feature_flags/models.py ===" in seen["input_text"]
    assert "=== CONTEXT FILE: src/feature_flags/evaluator.py ===" in seen["input_text"]
    assert "=== CONTEXT FILE: tests/test_feature_flags.py ===" in seen["input_text"]
    assert seen["instructions"] is not None
    assert "No prose around the blocks. No explanations. No code fences." in seen["instructions"]
    assert "Do not" not in seen["instructions"]


def test_run_openai_host_control_verified_work_feature_flags_repairs_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_contract = WorkContract(
        allowed_write_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
        verification_profile="python_workspace_pytest_feature_flags_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    broken_file_map = dict(VALID_FEATURE_FLAG_FILE_MAP)
    broken_file_map["src/feature_flags/evaluator.py"] = (
        "from __future__ import annotations\n\n"
        "from .models import FeatureFlag\n\n\n"
        "def is_flag_active(flag: FeatureFlag, *, user_key: str, country: str) -> bool:\n"
        "    return True\n"
    )
    first_result = render_full_files_result(broken_file_map)
    second_result = render_full_files_result(VALID_FEATURE_FLAG_FILE_MAP)
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
                "request_input_text": request.input_text,
            }
        )
        if previous_response_id is None:
            return [
                {
                    "type": "response.created",
                    "session_id": "oa-feature-flags-repair",
                    "response_id": "resp-feature-flags-repair-1",
                },
                {
                    "type": "response.output_text.delta",
                    "session_id": "oa-feature-flags-repair",
                    "response_id": "resp-feature-flags-repair-1",
                    "delta": first_result,
                },
                {
                    "type": "response.completed",
                    "session_id": "oa-feature-flags-repair",
                    "response_id": "resp-feature-flags-repair-1",
                },
            ]
        assert previous_response_id == "resp-feature-flags-repair-1"
        assert isinstance(input_text_override, str)
        assert "what failed: test_failed" in input_text_override
        return [
            {
                "type": "response.created",
                "session_id": "oa-feature-flags-repair",
                "response_id": "resp-feature-flags-repair-2",
            },
            {
                "type": "response.output_text.delta",
                "session_id": "oa-feature-flags-repair",
                "response_id": "resp-feature-flags-repair-2",
                "delta": second_result,
            },
            {
                "type": "response.completed",
                "session_id": "oa-feature-flags-repair",
                "response_id": "resp-feature-flags-repair-2",
            },
        ]

    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5.4",
        input_text="implement feature flags",
        max_output_tokens=4096,
        work_contract=work_contract,
    )
    monkeypatch.setattr(
        "cortex.hosts.openai.host_control.verify_verified_work_result",
        lambda result_text, contract, **kwargs: (
            VALID_FEATURE_FLAG_FILE_MAP,
            VerificationOutcome(
                status="failed",
                failure_class="test_failed",
                parsed_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=False,
                pytest_exit_code=1,
                pytest_passed=5,
                pytest_failed=1,
                first_failure_excerpt="FAILED tests/test_feature_flags.py::test_deny_country_wins_over_allow_and_rollout",
            ),
        )
        if result_text == first_result
        else (
            VALID_FEATURE_FLAG_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=6,
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
    assert "=== CONTEXT FILE: tests/test_feature_flags.py ===" in str(calls[0]["request_input_text"])
    assert final_session.event_index == 6
    assert final_session.next_recommended_move == "continue"
    assert final_session.executive_modulator_memory is not None
    assert "=== CONTEXT FILE:" not in str(calls[1]["input_text_override"])


def _offline_publication() -> OfflineSupportPublication:
    return OfflineSupportPublication(
        contradiction_summary_refs=(
            make_support_ref("contradiction", "host-degraded"),
        ),
        publication_tags=frozenset({"aux/offline-publication"}),
        notes=("support-side only",),
        metadata=(
            MetadataField("source", "aux/distillation"),
            MetadataField("host_name", "openai"),
        ),
    )


def _basic_response_events(session_id: str, response_id: str) -> list[dict[str, object]]:
    return [
        {
            "type": "response.created",
            "session_id": session_id,
            "response_id": response_id,
        },
        {
            "type": "response.output_text.delta",
            "session_id": session_id,
            "response_id": response_id,
            "delta": "ok",
        },
        {
            "type": "response.completed",
            "session_id": session_id,
            "response_id": response_id,
        },
    ]


def _runtime_feedback(
    *,
    selected: SoftControlFamily = SoftControlFamily.CHECK,
    realized: SoftControlFamily = SoftControlFamily.CHECK,
    brake_state: BrakeState = BrakeState.QUIESCENT,
    warning_codes: tuple[str, ...] = (),
    host_friction_tags: tuple[str, ...] = (),
    evidence_progress_class: str | None = None,
    continuity_progress_class: str | None = None,
    probe_result_class: str | None = None,
) -> ReferenceRealizationFeedback:
    return ReferenceRealizationFeedback(
        selected_family=selected,
        realized_family=realized,
        brake_state=brake_state,
        task_mode=OperatorTaskMode.INSPECT,
        warning_codes=warning_codes,
        host_friction_tags=host_friction_tags,
        evidence_progress_class=evidence_progress_class,
        continuity_progress_class=continuity_progress_class,
        probe_result_class=probe_result_class,
    )
