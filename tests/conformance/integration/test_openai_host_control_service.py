"""Integration tests for the bounded outbound OpenAI host-control lane."""

from __future__ import annotations

import json
from pathlib import Path

from cortex.aux.publication import (
    OfflineSupportPublication,
    offline_support_publication_as_payload,
)
from cortex.core.envelopes import MetadataField
from cortex.hosts.openai import host_transport as openai_host_transport
from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step

from tests.conformance.integration._openai_service_harness import (
    EXPECTED_RECORD_KEYS,
    run_openai_service,
)
from tests.experimental._aux_test_support import make_support_ref


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


def test_openai_host_control_action_endpoint_keeps_default_memory_path_inactive() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_single_call.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "hello from k2",
                },
            },
        )

    assert status_code == 200
    assert [tuple(record) for record in payload["records"]] == [
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
    ]
    assert [
        record["control_ledger"]["allocation_diagnostics"]["memory_reentry"]["state"]
        for record in payload["records"]
    ] == ["inactive", "inactive", "inactive"]


def test_openai_host_control_action_endpoint_roundtrips_explicit_publication_memory_projection() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_single_call_publication.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "hello from k2",
                    "offline_publication": offline_support_publication_as_payload(
                        _offline_publication()
                    ),
                },
            },
        )

    assert status_code == 200
    assert [tuple(record) for record in payload["records"]] == [
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
    ]
    assert [
        record["control_ledger"]["allocation_diagnostics"]["memory_reentry"]
        for record in payload["records"]
    ] == _direct_runtime_memory_projection(
        FIXTURE_DIR / "openai_host_control_single_call_publication.json",
        _offline_publication(),
    )


def _direct_runtime_memory_projection(
    fixture_path: Path,
    offline_publication: OfflineSupportPublication,
) -> list[dict[str, object]]:
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    events = payload["calls"][0]["events"]
    session = OpenAIRuntimeSession()
    projections: list[dict[str, object]] = []
    for event in events:
        raw_event = dict(event)
        event_name = raw_event.pop("type")
        step_result = run_openai_runtime_step(
            event_name,
            raw_event,
            session,
            offline_publication=offline_publication,
        )
        projections.append(
            step_result.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
        )
        session = step_result.session
    return projections


def _offline_publication() -> OfflineSupportPublication:
    return OfflineSupportPublication(
        contradiction_summary_refs=(make_support_ref("contradiction", "host-degraded"),),
        publication_tags=frozenset({"aux/offline-publication"}),
        notes=("support-side only",),
        metadata=(
            MetadataField("source", "aux/distillation"),
            MetadataField("host_name", "openai"),
        ),
    )
