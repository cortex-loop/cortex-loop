"""Shared support helpers for the L1 live-validation harness."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
WORKSTREAM_PATH = DOCS_ROOT / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
LIVE_VALIDATION_ROOT = DOCS_ROOT / "live_validation"
PREFLIGHT_REPORT_PATH = LIVE_VALIDATION_ROOT / "preflight_report.json"
PROVIDER_ROOTS = {
    "claude": LIVE_VALIDATION_ROOT / "claude",
    "gemini": LIVE_VALIDATION_ROOT / "gemini",
    "openai": LIVE_VALIDATION_ROOT / "openai",
    "comparators": LIVE_VALIDATION_ROOT / "comparators",
}
PROVIDER_MODELS = {
    "claude": "claude-sonnet-4-6",
    "gemini": "gemini-2.5-pro",
    "openai": "gpt-5.4",
}
_HOME_PATH = str(Path.home())
_TEMP_PATH_RE = re.compile(r"/(?:private/)?var/folders/[^\s\"']+")
BLOCKING_FAILURE_CLASSES = frozenset(
    {
        "auth_missing",
        "auth_expired",
        "capacity_exhausted",
        "quota_exhausted",
        "model_unavailable",
    }
)


@dataclass(frozen=True, slots=True)
class ScenarioSpec:
    scenario_id: str
    kind: str
    description: str
    prompt: str
    max_output_tokens: int
    repeat_count: int = 1


COMMON_SCENARIOS: tuple[ScenarioSpec, ...] = (
    ScenarioSpec(
        scenario_id="core_01_single_turn_summary",
        kind="common",
        description="one bounded summarization/transformation request",
        prompt=(
            "Summarize this synthetic runtime update in exactly three bullets. "
            "Keep each bullet under eight words.\n\n"
            "Update: project_a migrated one background worker, one queue stalled "
            "for four minutes, no data loss occurred, rollback was not needed, "
            "and one dashboard lagged behind."
        ),
        max_output_tokens=128,
        repeat_count=2,
    ),
    ScenarioSpec(
        scenario_id="core_02_long_stream",
        kind="common",
        description="one prompt that should force multiple streamed chunks",
        prompt=(
            "Write twelve numbered one-line observations about why explicit "
            "lifecycle logging matters in a runtime shell. Keep each line under "
            "ten words."
        ),
        max_output_tokens=256,
        repeat_count=2,
    ),
    ScenarioSpec(
        scenario_id="core_03_two_turn_restart",
        kind="common",
        description="two-step continuity/export-import check",
        prompt="List one operator action for first_step only.",
        max_output_tokens=96,
        repeat_count=2,
    ),
)

HOST_TAILORED_SCENARIOS: dict[str, tuple[ScenarioSpec, ...]] = {
    "claude": (
        ScenarioSpec(
            scenario_id="claude_01_messages_shape",
            kind="host_tailored",
            description="surface richer Claude message/body structure when possible",
            prompt=(
                "Produce two titled sections, Observations and Warnings, each with "
                "three bullets about a runtime shell rollout."
            ),
            max_output_tokens=192,
        ),
    ),
    "gemini": (
        ScenarioSpec(
            scenario_id="gemini_01_stream_variance",
            kind="host_tailored",
            description="surface longer Gemini streaming cadence when possible",
            prompt=(
                "Produce a compact checklist of ten items about runtime-shell "
                "observability, then end with one recap sentence."
            ),
            max_output_tokens=256,
        ),
    ),
    "openai": (
        ScenarioSpec(
            scenario_id="openai_01_long_responses",
            kind="host_tailored",
            description="surface longer OpenAI responses streaming behavior",
            prompt=(
                "Write eight short numbered lines about why contradiction-preserving "
                "logging matters, then give one final summary sentence."
            ),
            max_output_tokens=224,
        ),
    ),
}


def ensure_live_validation_dirs() -> None:
    LIVE_VALIDATION_ROOT.mkdir(parents=True, exist_ok=True)
    for directory in PROVIDER_ROOTS.values():
        directory.mkdir(parents=True, exist_ok=True)


def now_utc_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def read_workstream_baseline() -> tuple[str, str]:
    text = WORKSTREAM_PATH.read_text(encoding="utf-8")
    branch_match = re.search(r"Accepted baseline branch: `([^`]+)`", text)
    commit_match = re.search(r"Accepted baseline commit: `([^`]+)`", text)
    if branch_match is None or commit_match is None:
        raise ValueError("workstream baseline is missing")
    return branch_match.group(1), commit_match.group(1)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(sanitize_text(text), encoding="utf-8")


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout_seconds: float = 180.0,
) -> dict[str, Any]:
    started_at = now_utc_iso()
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    ended_at = now_utc_iso()
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": sanitize_text(completed.stdout),
        "stderr": sanitize_text(completed.stderr),
        "started_at": started_at,
        "ended_at": ended_at,
    }


def provider_cli_workspace() -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(prefix="cortex-live-provider-")


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def extract_event_labels(records: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for record in records:
        for key in ("type", "subtype", "event", "role"):
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                labels.append(value.strip())
                break
    return labels


def extract_result_text(records: list[dict[str, Any]], raw_stdout: str) -> str | None:
    for record in reversed(records):
        result = record.get("result")
        if isinstance(result, str) and result.strip():
            return result.strip()
        message = record.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                chunks: list[str] = []
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text")
                        if isinstance(text, str) and text.strip():
                            chunks.append(text.strip())
                if chunks:
                    return "\n".join(chunks)
        content = record.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    stripped = raw_stdout.strip()
    return stripped or None


def redact_claude_auth_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "logged_in": bool(payload.get("loggedIn")),
        "auth_method": payload.get("authMethod"),
        "api_provider": payload.get("apiProvider"),
        "subscription_type": payload.get("subscriptionType"),
    }


def api_key_presence() -> dict[str, bool]:
    return {
        "ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "GEMINI_API_KEY": bool(os.environ.get("GEMINI_API_KEY")),
        "OPENAI_API_KEY": bool(os.environ.get("OPENAI_API_KEY")),
    }


def classify_failure(text: str) -> str | None:
    lowered = text.lower()
    if not lowered.strip():
        return None
    if "oauth token has expired" in lowered or "authentication_error" in lowered:
        return "auth_expired"
    if "api key is required" in lowered or "_api_key is required" in lowered:
        return "auth_missing"
    if "must be provided with -k/--api-key" in lowered:
        return "auth_missing"
    if "exhausted your capacity on this model" in lowered:
        return "capacity_exhausted"
    if "insufficient_quota" in lowered or "quota" in lowered:
        return "quota_exhausted"
    if "model_not_found" in lowered or "model not found" in lowered:
        return "model_unavailable"
    if "unknown model" in lowered:
        return "model_unavailable"
    return None


def should_collapse_after_failure(failure_class: str | None) -> bool:
    return failure_class in BLOCKING_FAILURE_CLASSES


def build_scenario_catalog() -> dict[str, list[dict[str, Any]]]:
    catalog: dict[str, list[dict[str, Any]]] = {}
    for provider in ("claude", "gemini", "openai"):
        scenarios = [*COMMON_SCENARIOS, *HOST_TAILORED_SCENARIOS[provider]]
        catalog[provider] = [
            {
                "scenario_id": scenario.scenario_id,
                "kind": scenario.kind,
                "description": scenario.description,
                "repeat_count": scenario.repeat_count,
                "max_output_tokens": scenario.max_output_tokens,
            }
            for scenario in scenarios
        ]
    return catalog


def decide_verdict(
    *,
    provider_success_count: int,
    cortex_success_count: int,
    blocker_classes: set[str],
) -> tuple[str, str]:
    if provider_success_count >= 3 and cortex_success_count >= 3 and not blocker_classes:
        return (
            "lifecycle-first is already paying off clearly",
            "All three providers produced live baseline evidence and all three Cortex host-control paths completed live runs.",
        )
    if cortex_success_count == 0 and blocker_classes:
        return (
            "lifecycle-first is not yet paying off enough on real hosts",
            "The current line exposes live blockers honestly, but no provider completed a successful Cortex host-control validation run.",
        )
    return (
        "lifecycle-first is promising but under-instrumented",
        "Some live evidence exists, but the current line still lacks enough successful end-to-end host evidence to prove payoff cleanly.",
    )


def sanitize_text(text: str) -> str:
    sanitized = text.replace(_HOME_PATH, "$HOME")
    sanitized = _TEMP_PATH_RE.sub("<temp-workspace>", sanitized)
    return sanitized
