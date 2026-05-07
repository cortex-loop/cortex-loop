"""Read-only audit for Codex App/CLI communication-boundary proof quality.

This audit classifies the recent Codex App/CLI hook-native trickle failures
without changing product policy. It separates host stdout contract, host
attachment, model assimilation, Cortex state capture, gate usage, and behavior
lift so structural probes cannot over-claim product success.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - direct script support.
    sys.path.insert(0, str(REPO_ROOT))

try:  # pragma: no cover - direct script execution uses fallback imports.
    from .live_validation_common import LOCAL_LIVE_ROOT
except ImportError:  # pragma: no cover
    from lab.live_validation_common import LOCAL_LIVE_ROOT


DEFAULT_OUTPUT_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_communication_boundary_audit"
)
TASK_STANDARD_LIVE_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_task_standard_live_probe"
)
PRODUCT_PERCEPTION_LIVE_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_product_perception_live_probe"
)
PRODUCT_EVENT_CAPTURE_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_product_event_capture_remediation"
)
STANDARD_LABELS = ("Work standard:", "Likely misses:", "Closure evidence:")
INCIDENT_CLASS_IDS = (
    "host_contract_mismatch",
    "lifecycle_config_mismatch",
    "temporal_capture_mismatch",
    "live_vs_gate0_mismatch",
    "workflow_health_closeout_coupling",
)
BOUNDARY_LADDER_IDS = (
    "host_stdout_contract_ok",
    "host_attached_context_observed",
    "model_assimilation_observed",
    "state_capture_observed",
    "gate_used_captured_state",
    "behavior_lift_claim_allowed",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--task-standard-live-root",
        type=Path,
        default=TASK_STANDARD_LIVE_ROOT,
    )
    parser.add_argument(
        "--product-perception-live-root",
        type=Path,
        default=PRODUCT_PERCEPTION_LIVE_ROOT,
    )
    parser.add_argument(
        "--product-event-capture-root",
        type=Path,
        default=PRODUCT_EVENT_CAPTURE_ROOT,
    )
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args(argv)

    report = run_audit(
        output_root=args.output_root,
        task_standard_live_root=args.task_standard_live_root,
        product_perception_live_root=args.product_perception_live_root,
        product_event_capture_root=args.product_event_capture_root,
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    if args.require_pass and not report.get("passed", False):
        return 1
    return 0


def run_audit(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    task_standard_live_root: Path | str = TASK_STANDARD_LIVE_ROOT,
    product_perception_live_root: Path | str = PRODUCT_PERCEPTION_LIVE_ROOT,
    product_event_capture_root: Path | str = PRODUCT_EVENT_CAPTURE_ROOT,
) -> dict[str, Any]:
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)

    standard_runs = _task_standard_runs(Path(task_standard_live_root))
    product_perception = _latest_report(Path(product_perception_live_root))
    event_capture = _latest_report(Path(product_event_capture_root))
    workflow_health = _codex_app_hook_health()
    incidents = _classified_incidents(
        standard_runs=standard_runs,
        product_perception=product_perception,
        event_capture=event_capture,
        workflow_health=workflow_health,
    )
    incident_summary = {
        "required_classes": list(INCIDENT_CLASS_IDS),
        "present_classes": [
            incident_id
            for incident_id in INCIDENT_CLASS_IDS
            if incidents.get(incident_id, {}).get("present") is True
        ],
        "mechanical_success": True,
        "product_evidence_success": False,
        "partial_evidence_only": True,
    }
    report = {
        "probe": "codex_app_cli_communication_boundary_audit",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "read_only_boundary_audit",
        "passed": _audit_passes(incidents),
        "mechanical_success": incident_summary["mechanical_success"],
        "product_evidence_success": incident_summary["product_evidence_success"],
        "partial_evidence_only": incident_summary["partial_evidence_only"],
        "verdict": "structural_proof_boundary_issue_localized_to_codex_app_cli",
        "incident_summary": incident_summary,
        "incident_classes": incidents,
        "boundary_ladders": {
            name: payload["boundary_ladder"] for name, payload in standard_runs.items()
        },
        "workflow_health": workflow_health,
        "artifact_roots": {
            "task_standard_live": str(Path(task_standard_live_root)),
            "product_perception_live": str(Path(product_perception_live_root)),
            "product_event_capture": str(Path(product_event_capture_root)),
        },
        "next_product_train": "codex-app-cli-task-standard-pretool-transcript-capture",
        "truth_boundary": (
            "This audit classifies proof quality and communication-boundary gaps "
            "from existing artifacts. It does not change Cortex speech, SRE law, "
            "selector thresholds, root hooks, live behavior, or shipping truth."
        ),
    }
    _write_json(output / "summary.json", report)
    return report


def boundary_ladder_for_task_standard_run(report: Mapping[str, Any]) -> dict[str, bool]:
    """Return the product evidence ladder for one task-standard live report."""

    stdout_text = _read_text(report.get("stdout_path"))
    transcript_text = _transcript_text_from_diagnostics(report.get("diagnostics_path"))
    stdout_payloads = _stdout_payloads_from_diagnostics(report.get("diagnostics_path"))
    ladder = {
        "host_stdout_contract_ok": _host_stdout_contract_ok(stdout_payloads),
        "host_attached_context_observed": _signed_context_observed(transcript_text),
        "model_assimilation_observed": _standard_block_observed(stdout_text)
        or _standard_block_observed(transcript_text),
        "state_capture_observed": _int(report.get("standard_capture_rows")) > 0
        or bool(report.get("prework_standard_capture")),
        "gate_used_captured_state": False,
        "behavior_lift_claim_allowed": False,
    }
    return {key: bool(ladder.get(key, False)) for key in BOUNDARY_LADDER_IDS}


def _task_standard_runs(root: Path) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("run_*/report.json")):
        report = _load_json(path)
        if not report:
            continue
        name = "context_live_rerun" if report.get("verdict") == "partial_delivery_only" else path.parent.name
        if _report_used_flat_context(report):
            name = "flat_context_live_run"
        runs[name] = {
            "report_path": str(path),
            "verdict": report.get("verdict"),
            "partial_evidence_only": report.get("verdict") == "partial_delivery_only",
            "boundary_ladder": boundary_ladder_for_task_standard_run(report),
        }
    return runs


def _classified_incidents(
    *,
    standard_runs: Mapping[str, Mapping[str, Any]],
    product_perception: Mapping[str, Any],
    event_capture: Mapping[str, Any],
    workflow_health: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    flat_context = standard_runs.get("flat_context_live_run", {})
    context_rerun = standard_runs.get("context_live_rerun", {})
    context_ladder = context_rerun.get("boundary_ladder", {})
    return {
        "host_contract_mismatch": {
            "present": bool(flat_context),
            "evidence": flat_context.get("report_path"),
            "interpretation": (
                "The original task-standard live run emitted a Cortex-internal "
                "flat context payload instead of Codex-native additionalContext."
            ),
        },
        "lifecycle_config_mismatch": {
            "present": product_perception.get("scoped_negative")
            == "codex_cli_live_hooks_exposed_stop_only_no_product_task_events",
            "evidence": product_perception.get("output_root"),
            "remediated_by_event_capture": event_capture.get("verdict")
            in {"pass_full_lifecycle", "pass_capture_only"},
        },
        "temporal_capture_mismatch": {
            "present": bool(
                context_ladder.get("model_assimilation_observed")
                and not context_ladder.get("state_capture_observed")
            ),
            "evidence": context_rerun.get("report_path"),
            "interpretation": (
                "The model formed the standard before tool use, but Cortex did "
                "not ingest that pre-tool transcript/event message into state."
            ),
        },
        "live_vs_gate0_mismatch": {
            "present": bool(context_rerun),
            "evidence": context_rerun.get("report_path"),
            "interpretation": (
                "Gate 0 simulated standard capture through Stop "
                "last_assistant_message, while live capture needed pre-tool "
                "transcript/event ingestion."
            ),
        },
        "workflow_health_closeout_coupling": {
            "present": "workflow_readiness_ok" in workflow_health
            and "chat_boundary_enforcement" in workflow_health,
            "evidence": workflow_health.get("workflow_readiness_verdict"),
            "current_workflow_readiness_ok": bool(
                workflow_health.get("workflow_readiness_ok")
            ),
            "interpretation": (
                "Codex App hook mechanics and disabled root policy are separate "
                "from current branch closeout readiness."
            ),
        },
    }


def _audit_passes(incidents: Mapping[str, Mapping[str, Any]]) -> bool:
    return all(
        incidents.get(incident_id, {}).get("present") is True
        for incident_id in INCIDENT_CLASS_IDS
    )


def _host_stdout_contract_ok(stdout_payloads: list[Mapping[str, Any]]) -> bool:
    context_payloads = [
        payload
        for payload in stdout_payloads
        if _additional_context_text(payload) is not None or "context" in payload
    ]
    if not context_payloads:
        return False
    return all(_additional_context_text(payload) for payload in context_payloads)


def _report_used_flat_context(report: Mapping[str, Any]) -> bool:
    for payload in _stdout_payloads_from_diagnostics(report.get("diagnostics_path")):
        if "context" in payload and _additional_context_text(payload) is None:
            return True
    return False


def _stdout_payloads_from_diagnostics(path_value: Any) -> list[Mapping[str, Any]]:
    rows = _load_jsonl(_path_or_none(path_value))
    payloads: list[Mapping[str, Any]] = []
    for row in rows:
        payload = row.get("stdout_payload")
        if isinstance(payload, Mapping):
            payloads.append(payload)
    return payloads


def _additional_context_text(payload: Mapping[str, Any]) -> str | None:
    hook_specific = payload.get("hookSpecificOutput")
    if not isinstance(hook_specific, Mapping):
        return None
    value = hook_specific.get("additionalContext")
    return value if isinstance(value, str) and value.strip() else None


def _signed_context_observed(transcript_text: str) -> bool:
    return "Let me put the standard down before I start" in transcript_text


def _standard_block_observed(text: str) -> bool:
    return all(label in text for label in STANDARD_LABELS)


def _transcript_text_from_diagnostics(path_value: Any) -> str:
    for row in _load_jsonl(_path_or_none(path_value)):
        coordinator = row.get("coordinator")
        if not isinstance(coordinator, Mapping):
            continue
        hook_payload = coordinator.get("hook_payload")
        if not isinstance(hook_payload, Mapping):
            continue
        transcript_path = _path_or_none(hook_payload.get("transcript_path"))
        if transcript_path and transcript_path.is_file():
            return _read_text(transcript_path)
    return ""


def _latest_report(root: Path) -> dict[str, Any]:
    if root.is_file():
        return _load_json(root)
    if not root.exists():
        return {}
    reports = sorted(root.glob("run_*/report.json"), key=lambda path: path.stat().st_mtime)
    if not reports:
        reports = sorted(root.rglob("*report.json"), key=lambda path: path.stat().st_mtime)
    return _load_json(reports[-1]) if reports else {}


def _codex_app_hook_health() -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            "internal/workflow/repo_workflow.py",
            "codex-app-hook-health",
            "--json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if proc.returncode not in (0, 1):
        return {"ok": False, "error": (proc.stderr or proc.stdout).strip()}
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "codex-app-hook-health returned non-json"}
    return payload if isinstance(payload, dict) else {"ok": False}


def _read_text(path_value: Any) -> str:
    path = _path_or_none(path_value)
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _path_or_none(value: Any) -> Path | None:
    if isinstance(value, Path):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    return Path(value)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _load_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded = json.loads(line)
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


__all__ = [
    "DEFAULT_OUTPUT_ROOT",
    "boundary_ladder_for_task_standard_run",
    "run_audit",
]


if __name__ == "__main__":  # pragma: no cover - exercised by CLI validation.
    raise SystemExit(main())
