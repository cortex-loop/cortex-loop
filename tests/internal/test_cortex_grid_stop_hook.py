"""Tests for the Cortex grid Stop hook.

The hook lives at ``.claude/hooks/cortex_grid_stop_hook.py`` and is
invoked by Claude Code when an agent attempts to stop the turn. It
reads the assistant's most recent message from the transcript JSONL,
runs ``grid`` itself, and:

- blocks the stop with the canonical grid markdown if the message is
  missing the grid signature markers,
- blocks the stop if the Goals Analysis bracketed templates were
  pasted unmodified (no substantive fill),
- blocks the stop with a failures list if ``reflection-check --json``
  returns verdict ``FAIL``,
- allows the stop otherwise.

The hook is the chat-boundary mechanical gate that closes the bypass
pattern (``run grid for inspection, then compose ad-hoc audit-shaped
markdown without the canonical signature``).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "cortex_grid_stop_hook.py"


def _run_hook(hook_input: dict[str, object]) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(hook_input),
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO_ROOT),
    )
    return proc.returncode, proc.stdout, proc.stderr


def _canonical_grid() -> str:
    proc = subprocess.run(
        [sys.executable, "internal/workflow/repo_workflow.py", "grid"],
        cwd=str(REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _write_transcript(tmp_path: Path, assistant_text: str) -> Path:
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(
        json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": assistant_text},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return transcript


def _hook_input(transcript: Path) -> dict[str, object]:
    return {
        "transcript_path": str(transcript),
        "cwd": str(REPO_ROOT),
        "stop_hook_active": False,
    }


def _fill_goals_analysis(grid_markdown: str) -> str:
    """Replace each Goals Analysis bracketed template with a filled answer."""
    return re.sub(
        r"_\[≥48 chars \+ cite a repo surface — [^\]]+\]_",
        (
            "Filled Goals Analysis answer with substantive content — "
            "cites `docs/CORTEX.md` §1 and `cortex_status.json::"
            "executive_completion` for grounding evidence."
        ),
        grid_markdown,
    )


def test_hook_blocks_when_assistant_message_lacks_grid_signature(tmp_path: Path) -> None:
    transcript = _write_transcript(
        tmp_path,
        "Just a plain assistant message without the grid signature.",
    )

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0  # hook exits 0 even when blocking
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "grid output not detected" in payload["reason"].lower()
    # Canonical grid markdown is injected as the reason context.
    assert "## Cortex Repo Hygiene Grid" in payload["reason"]


def test_hook_blocks_when_goals_analysis_template_unfilled(tmp_path: Path) -> None:
    canonical = _canonical_grid()
    # Paste canonical without filling in the Goals Analysis prompts —
    # the bracketed template stays verbatim.
    transcript = _write_transcript(tmp_path, canonical)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Goals Analysis" in payload["reason"]
    assert "bracketed template" in payload["reason"]


def test_hook_allows_stop_when_signature_present_and_goals_filled(tmp_path: Path) -> None:
    canonical = _canonical_grid()
    filled = _fill_goals_analysis(canonical)
    transcript = _write_transcript(tmp_path, filled)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    # Empty stdout means no decision payload → Claude Code allows the stop.
    assert stdout.strip() == ""


def test_hook_fails_open_on_missing_transcript_path(tmp_path: Path) -> None:
    # transcript_path points to a file that does not exist; the hook
    # must allow the stop so the conversation cannot lock.
    bogus = tmp_path / "missing.jsonl"
    hook_input = {"transcript_path": str(bogus), "cwd": str(REPO_ROOT)}

    returncode, stdout, stderr = _run_hook(hook_input)

    assert returncode == 0
    assert stdout.strip() == ""
    # Diagnostic should appear on stderr.
    assert "transcript" in stderr.lower() or "could not read" in stderr.lower()


def test_hook_fails_open_when_hook_input_missing_transcript_field() -> None:
    hook_input: dict[str, object] = {"cwd": str(REPO_ROOT)}

    returncode, stdout, stderr = _run_hook(hook_input)

    assert returncode == 0
    assert stdout.strip() == ""
    assert "transcript_path" in stderr.lower()


def test_hook_short_circuits_when_already_in_stop_hook_loop(tmp_path: Path) -> None:
    # ``stop_hook_active: true`` means Claude Code is already inside a
    # re-prompt loop triggered by this hook; the hook must allow the
    # stop to avoid infinite blocking when the agent cannot satisfy
    # the gate.
    transcript = _write_transcript(tmp_path, "no grid")
    hook_input = {
        "transcript_path": str(transcript),
        "cwd": str(REPO_ROOT),
        "stop_hook_active": True,
    }

    returncode, stdout, _ = _run_hook(hook_input)

    assert returncode == 0
    assert stdout.strip() == ""


def test_hook_signature_markers_match_repo_workflow_constants() -> None:
    """The hook's signature markers must equal repo_workflow's exports."""
    # Read the hook source and parse out the constants.
    text = HOOK_SCRIPT.read_text(encoding="utf-8")
    header_match = re.search(r'GRID_HEADER_MARKER\s*=\s*"([^"]+)"', text)
    state_match = re.search(r'GRID_STATE_MARKER\s*=\s*"([^"]+)"', text)
    verdict_match = re.search(r'GRID_VERDICT_MARKER\s*=\s*"([^"]+)"', text)
    assert header_match and state_match and verdict_match

    # Import repo_workflow and compare to its constants.
    sys.path.insert(0, str(REPO_ROOT / "internal" / "workflow"))
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "repo_workflow", REPO_ROOT / "internal" / "workflow" / "repo_workflow.py"
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(REPO_ROOT / "internal" / "workflow"))

    assert header_match.group(1) == module.GRID_HEADER_MARKER
    assert state_match.group(1) == module.GRID_STATE_MARKER
    assert verdict_match.group(1) == module.GRID_VERDICT_MARKER


def test_settings_json_declares_stop_hook() -> None:
    """The repo's .claude/settings.json must wire the Stop hook."""
    settings_path = REPO_ROOT / ".claude" / "settings.json"
    assert settings_path.exists()
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    stop_hooks = settings.get("hooks", {}).get("Stop", [])
    assert stop_hooks, "settings.json must declare at least one Stop hook"
    found_grid_hook = False
    for entry in stop_hooks:
        for hook in entry.get("hooks", []):
            if hook.get("type") == "command" and "cortex_grid_stop_hook" in hook.get("command", ""):
                found_grid_hook = True
    assert found_grid_hook, (
        "Stop hook for cortex_grid_stop_hook.py must be declared in "
        ".claude/settings.json"
    )
