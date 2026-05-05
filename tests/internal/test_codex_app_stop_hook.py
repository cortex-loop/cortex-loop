"""Tests for the repo-local Codex App Cortex Mission Reflection Stop hook."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".codex" / "hooks" / "cortex_mission_reflection_stop_hook.py"

MISSION_FILL = (
    "This row cites `docs/CORTEX.md` and `tests/internal/test_codex_app_stop_hook.py` "
    "while making a causal Cortex Mission Reflection claim about Codex App hook behavior, "
    "model I/O boundaries, evidence quality, and next ownership."
)
CLOSURE_FILL = (
    "ending branch `codex/test`; commit `no commit`; verification no verification "
    "this turn; returned to main no; Status registry touched none; status doc "
    "regenerated no; CORTEX.md regenerated no"
)


def _canonical_grid(mode: str = "closeout") -> str:
    proc = subprocess.run(
        [sys.executable, "internal/workflow/repo_workflow.py", "grid", "--mode", mode],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _fill_graph(graph: str) -> str:
    graph = re.sub(r"_\[mission reflection — [^\]]+\]_", MISSION_FILL, graph)
    graph = re.sub(r"_\[closure metadata — [^\]]+\]_", CLOSURE_FILL, graph)
    return graph


def _run_hook(last_assistant_message: str | None) -> tuple[int, str, str]:
    hook_input: dict[str, object] = {
        "cwd": str(REPO_ROOT),
        "turn_id": "test-turn",
        "stop_hook_active": False,
    }
    if last_assistant_message is not None:
        hook_input["last_assistant_message"] = last_assistant_message
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(hook_input),
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO_ROOT),
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_codex_app_hook_blocks_missing_graph() -> None:
    returncode, stdout, _stderr = _run_hook("Plain response without the mission graph.")

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "missing graph header" in payload["reason"]
    assert "## Cortex Mission Reflection" in payload["reason"]


def test_codex_app_hook_blocks_unfilled_template() -> None:
    returncode, stdout, _stderr = _run_hook(_canonical_grid())

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "template still present" in payload["reason"]


def test_codex_app_hook_blocks_stale_dashboard_row() -> None:
    filled = _fill_graph(_canonical_grid())
    stale = filled.replace(
        "| **Verdict** |",
        "| **Progress: bio_to_code matrix** | stale fixed dashboard row |\n| **Verdict** |",
        1,
    )

    returncode, stdout, _stderr = _run_hook(stale)

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "stale dashboard row" in payload["reason"]


def test_codex_app_hook_blocks_short_mission_row() -> None:
    filled = _fill_graph(_canonical_grid())
    short = filled.replace(MISSION_FILL, "`docs/CORTEX.md` short", 1)

    returncode, stdout, _stderr = _run_hook(short)

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "too short" in payload["reason"]


def test_codex_app_hook_allows_filled_graph() -> None:
    returncode, stdout, stderr = _run_hook(_fill_graph(_canonical_grid()))

    assert returncode == 0
    assert stdout.strip() == ""
    assert stderr.strip() == ""


def test_codex_app_hook_allows_exploration_graph() -> None:
    returncode, stdout, stderr = _run_hook(_fill_graph(_canonical_grid("exploration")))

    assert returncode == 0
    assert stdout.strip() == ""
    assert stderr.strip() == ""


def test_codex_app_hook_fails_open_when_message_unavailable() -> None:
    returncode, stdout, stderr = _run_hook(None)

    assert returncode == 0
    assert stdout.strip() == ""
    assert "last_assistant_message" in stderr


def test_codex_config_disables_app_stop_hook_by_policy() -> None:
    config_path = REPO_ROOT / ".codex" / "config.toml"
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))

    assert config["features"]["codex_hooks"] is False
    assert "hooks" not in config


def test_codex_hook_docstring_records_current_lifecycle_terms() -> None:
    text = HOOK_SCRIPT.read_text(encoding="utf-8")

    assert "last_assistant_message" in text
    assert "[features].codex_hooks" in text
    assert "trusted project" in text
    assert "does not prove live" in text


def test_repo_workflow_codex_app_hook_health_passes() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "internal/workflow/repo_workflow.py",
            "codex-app-hook-health",
            "--json",
        ],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["codex_hooks_feature_enabled"] is False
    assert payload["chat_boundary_enforcement"] == "disabled_by_repo_policy"
    assert payload["known_bad_blocks"] is True
    assert payload["filled_graph_allows_stop"] is True
