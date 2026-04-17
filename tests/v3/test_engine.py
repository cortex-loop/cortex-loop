"""Engine and provider-equivalence tests for Cortex v3."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from cortex_v3.contracts import (
    ProviderTurnRequest,
    ProviderTurnResponse,
    VerificationOutcome,
    VerifiedTurnRequest,
    WorkContract,
)
from cortex_v3.engine import run_verified_turn
from cortex_v3.providers.base import ProviderAdapter
from cortex_v3.providers.claude import ClaudeAdapter
from cortex_v3.providers.gemini import GeminiAdapter
from cortex_v3.providers.openai import OpenAIAdapter
from tests.product._verified_work_fixtures import (
    VALID_FILE_MAP,
    VALID_NORMALIZE_PORT_FILE_MAP,
    render_full_files_result,
)


def _bookmarks_request(max_repair_turns: int = 1) -> VerifiedTurnRequest:
    return VerifiedTurnRequest(
        model="test-model",
        task_prompt="build bookmarks app",
        work_contract=WorkContract(
            allowed_write_paths=(
                "src/bookmarks_api/main.py",
                "src/bookmarks_api/models.py",
                "src/bookmarks_api/store.py",
            ),
            verification_profile="python_workspace_pytest_v1",
            max_repair_turns=max_repair_turns,
        ),
        instructions="Return protocol blocks only.",
        max_output_tokens=512,
    )


def _normalize_port_request(max_repair_turns: int = 1) -> VerifiedTurnRequest:
    return VerifiedTurnRequest(
        model="test-model",
        task_prompt="fix normalize_port",
        work_contract=WorkContract(
            allowed_write_paths=("src/normalize_port.py",),
            verification_profile="python_workspace_pytest_port_fix_v1",
            max_repair_turns=max_repair_turns,
        ),
        instructions="Return protocol blocks only.",
        max_output_tokens=512,
    )


@dataclass
class _StaticAdapter:
    provider: str
    responses: list[ProviderTurnResponse]
    seen_requests: list[ProviderTurnRequest] | None = None

    def __post_init__(self) -> None:
        if self.seen_requests is None:
            self.seen_requests = []

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        assert self.seen_requests is not None
        self.seen_requests.append(request)
        if not self.responses:
            raise AssertionError("Static adapter response queue exhausted.")
        return self.responses.pop(0)


def test_run_verified_turn_passes_without_repair_with_real_verifier() -> None:
    request = _normalize_port_request()
    result_text = render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP)
    adapter = _StaticAdapter(
        provider="openai",
        responses=[
            ProviderTurnResponse(
                provider="openai",
                output_text=result_text,
                raw_events=({"type": "response.output_text.delta", "delta": result_text},),
            )
        ],
    )

    result = run_verified_turn(adapter, request)

    assert result.provider == "openai"
    assert result.attempt_count == 1
    assert result.decision == "continue"
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert result.parsed_paths == ("src/normalize_port.py",)


def test_run_verified_turn_repairs_once_with_full_visible_context_and_narrowed_write_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request = _bookmarks_request()
    broken_main = "from fastapi import FastAPI\napp = FastAPI(\n"
    first_result = render_full_files_result({"src/bookmarks_api/main.py": broken_main})
    second_result = render_full_files_result(
        {"src/bookmarks_api/main.py": VALID_FILE_MAP["src/bookmarks_api/main.py"]}
    )
    adapter = _StaticAdapter(
        provider="openai",
        responses=[
            ProviderTurnResponse(
                provider="openai",
                output_text=first_result,
                raw_events=({"type": "response.output_text.delta", "delta": first_result},),
            ),
            ProviderTurnResponse(
                provider="openai",
                output_text=second_result,
                raw_events=({"type": "response.output_text.delta", "delta": second_result},),
            ),
        ],
    )

    calls: list[tuple[str | None, tuple[str, ...]]] = []

    def _fake_verify(result_text: str | None, work_contract: WorkContract, **kwargs):
        calls.append((result_text, work_contract.allowed_write_paths))
        if len(calls) == 1:
            return (
                {"src/bookmarks_api/main.py": broken_main},
                VerificationOutcome(
                    status="failed",
                    failure_class="import_smoke_failed",
                    parsed_paths=("src/bookmarks_api/main.py",),
                    import_smoke_ok=False,
                    import_smoke_excerpt="SyntaxError: '(' was never closed",
                    first_failure_excerpt="SyntaxError: '(' was never closed",
                ),
            )
        return (
            VALID_FILE_MAP,
            VerificationOutcome(
                status="passed",
                failure_class=None,
                parsed_paths=("src/bookmarks_api/main.py",),
                import_smoke_ok=True,
                pytest_ok=True,
                pytest_exit_code=0,
                pytest_passed=12,
                pytest_failed=0,
            ),
        )

    monkeypatch.setattr("cortex_v3.engine.verify_verified_work_result", _fake_verify)

    result = run_verified_turn(adapter, request)

    assert result.attempt_count == 2
    assert result.decision == "continue"
    assert len(adapter.seen_requests or []) == 2
    second_request = adapter.seen_requests[1]
    assert "src/bookmarks_api/main.py" in second_request.instructions
    assert "src/bookmarks_api/models.py" not in second_request.instructions
    assert "src/bookmarks_api/store.py" not in second_request.instructions
    assert set(second_request.as_payload()) == {
        "provider",
        "model",
        "prompt",
        "instructions",
        "max_output_tokens",
    }
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in second_request.prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/models.py ===" in second_request.prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/store.py ===" in second_request.prompt
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in second_request.prompt
    assert broken_main.strip() in second_request.prompt


def test_run_verified_turn_repairs_once_with_real_verifier() -> None:
    request = _normalize_port_request()
    broken_result = render_full_files_result(
        {"src/normalize_port.py": "def normalize_port(value: int | str) -> int:\n    return int(\n"}
    )
    repaired_result = render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP)
    adapter = _StaticAdapter(
        provider="openai",
        responses=[
            ProviderTurnResponse(
                provider="openai",
                output_text=broken_result,
                raw_events=({"type": "response.output_text.delta", "delta": broken_result},),
            ),
            ProviderTurnResponse(
                provider="openai",
                output_text=repaired_result,
                raw_events=({"type": "response.output_text.delta", "delta": repaired_result},),
            ),
        ],
    )

    result = run_verified_turn(adapter, request)

    assert result.attempt_count == 2
    assert result.decision == "continue"
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert result.parsed_paths == ("src/normalize_port.py",)


@pytest.mark.parametrize(
    ("blocked_text", "expected_decision"),
    [
        (
            "=== BLOCKED: needs_user_input ===\nNeed the archive retention policy.\n=== END BLOCKED ===",
            "check",
        ),
        (
            "=== BLOCKED: unsafe_request ===\nDeleting production data is unsafe.\n=== END BLOCKED ===",
            "stop",
        ),
    ],
)
def test_run_verified_turn_handles_blocked_results_with_real_verifier(
    blocked_text: str,
    expected_decision: str,
) -> None:
    request = _bookmarks_request()
    adapter = _StaticAdapter(
        provider="claude",
        responses=[
            ProviderTurnResponse(
                provider="claude",
                output_text=blocked_text,
                raw_events=({"type": "content_block_delta", "delta": blocked_text},),
            )
        ],
    )

    result = run_verified_turn(adapter, request)

    assert result.attempt_count == 1
    assert result.decision == expected_decision
    assert result.verification is not None
    assert result.verification.status == "blocked"


@pytest.mark.parametrize(
    "adapter",
    [
        OpenAIAdapter(
            transport=lambda request: [
                {"type": "response.created", "response_id": "resp-v3-1"},
                {
                    "type": "response.output_text.delta",
                    "response_id": "resp-v3-1",
                    "delta": render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP),
                },
            ]
        ),
        ClaudeAdapter(
            transport=lambda request: [
                {
                    "type": "content_block_delta",
                    "message_id": "msg-v3-1",
                    "delta": render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP),
                },
                {"type": "message_stop", "message_id": "msg-v3-1"},
            ]
        ),
        GeminiAdapter(
            transport=lambda request: [
                {
                    "type": "content.delta",
                    "interaction_id": "gm-v3-1",
                    "delta": {
                        "type": "text",
                        "text": render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP),
                    },
                },
                {"type": "interaction.complete", "interaction_id": "gm-v3-1"},
            ]
        ),
    ],
)
def test_provider_adapters_share_verified_turn_semantics(adapter: ProviderAdapter) -> None:
    request = _normalize_port_request()

    result = run_verified_turn(adapter, request)

    assert result.provider == adapter.provider
    assert result.decision == "continue"
    assert result.verification is not None
    assert result.verification.status == "passed"
    assert result.parsed_paths == ("src/normalize_port.py",)
