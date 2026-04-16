"""Integration tests for the OpenAI documented host-event runtime CLI shell."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cortex.aux.publication import (
    OfflineSupportPublication,
    offline_support_publication_as_payload,
)
from cortex.core.envelopes import MetadataField
from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step

from tests.experimental._aux_test_support import make_support_ref


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "openai_runtime_cli_session.jsonl"
)
EXPECTED_RECORD_KEYS = (
    "event_index",
    "raw_host_event_name",
    "native_event_name",
    "dispatch_lane",
    "decision",
    "warnings",
    "journal",
    "executive_state",
    "selected_family",
    "realized_family",
    "brake_state",
    "control_ledger",
    "feedback_window_summary",
    "executive_signal_summary",
    "executive_modulator_state",
    "executive_policy_view",
    "operator_route",
    "closure_required",
    "closure_reason_tags",
    "commitment_result_kind",
)


def test_openai_runtime_cli_explicit_publication_matches_direct_runtime_memory_projection(
    tmp_path: Path,
) -> None:
    publication_path = tmp_path / "offline-publication.json"
    publication_path.write_text(
        json.dumps(offline_support_publication_as_payload(_offline_publication())),
        encoding="utf-8",
    )

    completed = _run_openai_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--offline-publication-file",
        str(publication_path),
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)
    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert tuple(records[0]["control_ledger"]["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "chi_t",
        "risk_weight",
        "brake_tonic",
        "rejected_cheaper_families",
        "probe_path_state",
        "probe_unavailable_reason",
        "probe_result_class",
        "verification_state",
        "explainability_profile",
        "anti_thrash",
        "memory_reentry",
        "scores",
        "mediation",
    )

    direct_records = _direct_runtime_records(_offline_publication())
    assert [
        record["control_ledger"]["allocation_diagnostics"]["memory_reentry"]
        for record in records
    ] == [
        record["control_ledger"]["allocation_diagnostics"]["memory_reentry"]
        for record in direct_records
    ]


def _run_openai_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.openai.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _fixture_events() -> list[tuple[str, dict[str, object]]]:
    events: list[tuple[str, dict[str, object]]] = []
    for line in FIXTURE_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        events.append((payload["event_name"], payload["payload"]))
    return events


def _direct_runtime_records(
    offline_publication: OfflineSupportPublication,
) -> list[dict[str, object]]:
    session = OpenAIRuntimeSession()
    records: list[dict[str, object]] = []
    for event_name, payload in _fixture_events():
        step_result = run_openai_runtime_step(
            event_name,
            payload,
            session,
            offline_publication=offline_publication,
        )
        records.append(
            {
                "control_ledger": step_result.control_ledger_summary,
            }
        )
        session = step_result.session
    return records


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
