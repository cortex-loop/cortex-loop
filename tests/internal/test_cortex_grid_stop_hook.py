"""Tests for the Cortex grid Stop hook (single-closure-grid enforcement).

The hook lives at ``.claude/hooks/cortex_grid_stop_hook.py`` and is the
chat-boundary mechanical gate for the per-turn hygiene contract. Five
gates run on every Stop event (the hook does NOT short-circuit on
``stop_hook_active``):

1. Required signature markers all present:
   ``## Cortex Repo Hygiene Grid``, ``### State``,
   ``### Standard Metadata``, ``### Final Handoff Mirror``,
   ``### Verdict``.
2. Closure-shaped substrings (``Ending branch``, ``Fixed now``, etc.)
   do NOT appear before the grid header (closure must live inside the
   grid).
3. Each Goals Analysis field is filled per-field (not just "fewer
   than 5 templates remain"); each field's body must NOT contain the
   literal template substring.
4. Standard Metadata and Final Handoff Mirror cells have no remaining
   ``<fill`` placeholder.
5. ``reflection-check --json`` returns verdict ``PASS`` or ``GAPS``
   (FAIL blocks).

Fail-open paths (intentional, infrastructure-only): missing transcript,
malformed hook input, ``grid``/``reflection-check`` command crash. The
``stop_hook_active`` short-circuit was removed in Session 4.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
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


def _hook_input(transcript: Path, *, stop_hook_active: bool = False) -> dict[str, object]:
    return {
        "transcript_path": str(transcript),
        "cwd": str(REPO_ROOT),
        "stop_hook_active": stop_hook_active,
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


def _fill_metadata_and_mirror(grid_markdown: str) -> str:
    """Replace each `<fill: ...>` placeholder with `n/a` so cells render filled."""
    return re.sub(r"<fill[^>]*>", "n/a (no work this turn)", grid_markdown)


def _fully_filled_grid() -> str:
    return _fill_metadata_and_mirror(_fill_goals_analysis(_canonical_grid()))


# ---------------------------------------------------------------------------
# Required-marker gate (Gate 1).
# ---------------------------------------------------------------------------


def test_hook_blocks_when_message_missing_grid_header(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path, "Plain assistant message; no grid.")

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "incomplete" in payload["reason"].lower() or "missing" in payload["reason"].lower()
    # Canonical grid markdown is injected as the reason context.
    assert "## Cortex Repo Hygiene Grid" in payload["reason"]


def test_hook_blocks_when_standard_metadata_marker_missing(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    # Strip the Standard Metadata header so the gate fires.
    mutated = canonical.replace("### Standard Metadata", "### NOT-METADATA")
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Standard Metadata" in payload["reason"]


def test_hook_blocks_when_final_handoff_mirror_marker_missing(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    mutated = canonical.replace("### Final Handoff Mirror", "### NOT-MIRROR")
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Final Handoff Mirror" in payload["reason"]


# ---------------------------------------------------------------------------
# Closure-leak gate (Gate 2).
# ---------------------------------------------------------------------------


def test_hook_blocks_when_closure_marker_appears_before_grid(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    # Prefix the response with a "Standard Metadata"-shaped block before
    # the grid — exactly the bypass pattern this gate prevents.
    leaked = "Ending branch: main\n\nFixed now: lots of stuff\n\n" + canonical
    transcript = _write_transcript(tmp_path, leaked)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "outside the grid" in payload["reason"].lower() or "before the grid" in payload["reason"].lower()


# ---------------------------------------------------------------------------
# Per-field Goals Analysis gate (Gate 3).
# ---------------------------------------------------------------------------


def test_hook_blocks_when_one_goals_analysis_field_unfilled(tmp_path: Path) -> None:
    canonical = _canonical_grid()
    # Fill 4 of the 5 Goals Analysis prompts; leave one unfilled.
    template_pattern = re.compile(r"_\[≥48 chars \+ cite a repo surface — [^\]]+\]_")
    matches = list(template_pattern.finditer(canonical))
    assert len(matches) == 5, "expected 5 Goals Analysis bracketed templates"
    # Replace the first 4; leave the 5th unfilled.
    filled = canonical
    for match in matches[:4]:
        filled = filled.replace(
            match.group(0),
            (
                "Filled answer with citation — see "
                "`docs/CORTEX.md` §1."
            ),
            1,
        )
    filled = _fill_metadata_and_mirror(filled)
    transcript = _write_transcript(tmp_path, filled)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Goals Analysis" in payload["reason"]
    assert "unfilled" in payload["reason"].lower() or "still showing" in payload["reason"].lower()


# ---------------------------------------------------------------------------
# Fill-placeholder gate (Gate 4) — Standard Metadata / Final Handoff Mirror.
# ---------------------------------------------------------------------------


def test_hook_blocks_when_metadata_has_unfilled_placeholder(tmp_path: Path) -> None:
    # Goals Analysis filled but Standard Metadata still has `<fill>` cells.
    canonical = _fill_goals_analysis(_canonical_grid())
    transcript = _write_transcript(tmp_path, canonical)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Standard Metadata" in payload["reason"] or "<fill" in payload["reason"]


# ---------------------------------------------------------------------------
# All-clear path: signature complete + closure inside grid + Goals Analysis
# filled + no <fill> placeholders + verdict PASS → allow stop.
# ---------------------------------------------------------------------------


def test_hook_allows_stop_when_all_gates_pass(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path, _fully_filled_grid())

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    # Empty stdout means no decision payload → Claude Code allows the stop.
    assert stdout.strip() == ""


# ---------------------------------------------------------------------------
# stop_hook_active no longer short-circuits (Session 4 hard-gate change).
# ---------------------------------------------------------------------------


def test_hook_does_not_short_circuit_on_stop_hook_active(tmp_path: Path) -> None:
    """Session 4 removed the unconditional allow on stop_hook_active.

    Persistent agent non-compliance must continue to block on every stop
    attempt, not just the first. Infrastructure failures still fail open
    via the diagnostic_exit paths.
    """
    transcript = _write_transcript(tmp_path, "no grid signature here")

    returncode, stdout, _ = _run_hook(_hook_input(transcript, stop_hook_active=True))

    assert returncode == 0
    # Block, not allow — the hard gate still fires.
    assert stdout.strip() != "", (
        "stop_hook_active should NOT short-circuit; the hook must still block"
    )
    payload = json.loads(stdout)
    assert payload["decision"] == "block"


# ---------------------------------------------------------------------------
# Fail-open paths (infrastructure failures only).
# ---------------------------------------------------------------------------


def test_hook_fails_open_on_missing_transcript_path(tmp_path: Path) -> None:
    bogus = tmp_path / "missing.jsonl"
    hook_input = {"transcript_path": str(bogus), "cwd": str(REPO_ROOT)}

    returncode, stdout, stderr = _run_hook(hook_input)

    assert returncode == 0
    assert stdout.strip() == ""
    assert "transcript" in stderr.lower() or "could not read" in stderr.lower()


def test_hook_fails_open_when_hook_input_missing_transcript_field() -> None:
    hook_input: dict[str, object] = {"cwd": str(REPO_ROOT)}

    returncode, stdout, stderr = _run_hook(hook_input)

    assert returncode == 0
    assert stdout.strip() == ""
    assert "transcript_path" in stderr.lower()


# ---------------------------------------------------------------------------
# Constants pinning: hook + repo_workflow signature markers stay equal.
# ---------------------------------------------------------------------------


def test_hook_signature_markers_match_repo_workflow_constants() -> None:
    text = HOOK_SCRIPT.read_text(encoding="utf-8")
    constants = {}
    for name in (
        "GRID_HEADER_MARKER",
        "GRID_STATE_MARKER",
        "GRID_STANDARD_METADATA_MARKER",
        "GRID_FINAL_HANDOFF_MIRROR_MARKER",
        "GRID_VERDICT_MARKER",
    ):
        match = re.search(rf'{name}\s*=\s*"([^"]+)"', text)
        assert match, f"hook script missing constant {name}"
        constants[name] = match.group(1)

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

    for name, hook_value in constants.items():
        assert hook_value == getattr(module, name), (
            f"{name} differs between hook and repo_workflow"
        )


def test_settings_json_declares_stop_hook() -> None:
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
    assert found_grid_hook
