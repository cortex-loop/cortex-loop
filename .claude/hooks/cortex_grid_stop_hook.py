#!/usr/bin/env python3
"""Claude Code Stop hook that enforces the Cortex Repo Hygiene Grid.

The grid is the per-turn hygiene contract documented in `AGENTS.md`
`## Handoff` and `docs/CORTEX.md` §6: every chat ends with the grid
output produced by ``python3 internal/workflow/repo_workflow.py grid``.

Without a chat-boundary intercept, the contract is doctrine-only and an
agent that forgets (or composes its own grid-shaped markdown) escapes
the gate. This hook closes that gap by:

1. Parsing the assistant's most recent message from the transcript JSONL.
2. Running ``grid`` itself to obtain the canonical markdown.
3. Checking that the assistant's message contains all three signature
   markers from ``internal/workflow/repo_workflow.py``:
   ``## Cortex Repo Hygiene Grid``, ``### State``, ``### Verdict``.
4. Running ``reflection-check --json`` to derive the verdict.
5. Returning a JSON decision:
   * Missing signature → ``decision: block`` with the canonical grid
     markdown injected as the reason.
   * Verdict ``FAIL`` → ``decision: block`` with the failures list.
   * Verdict ``PASS`` or ``GAPS`` and signature present → empty output
     (allow stop).

Hook semantics: Stop hooks cannot append to the assistant message. The
gate works by blocking the stop and re-prompting the agent until the
canonical grid output is detected in the transcript. See the
verification recorded in the closeout for this seam.

Fail-open behavior: any unexpected error (missing transcript, bad
JSON, grid command crash) prints a diagnostic and exits 0 so the hook
never locks the conversation; the visible failure is itself a drift
signal.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Signature markers — MUST match internal/workflow/repo_workflow.py
# constants ``GRID_HEADER_MARKER``, ``GRID_STATE_MARKER``,
# ``GRID_VERDICT_MARKER``. Tests pin both sides equal so drift between
# the grid format and the hook's signature check is structurally
# prevented.
GRID_HEADER_MARKER = "## Cortex Repo Hygiene Grid"
GRID_STATE_MARKER = "### State"
GRID_VERDICT_MARKER = "### Verdict"


def _allow_stop() -> None:
    """Exit silently to allow Claude Code to stop the turn."""
    sys.exit(0)


def _block(reason: str) -> None:
    """Emit a block decision JSON and exit successfully.

    Claude Code reads stdout; ``{"decision": "block", "reason": "..."}``
    re-prompts the agent without ending the turn. The reason is shown to
    the agent as feedback context.
    """
    payload = {"decision": "block", "reason": reason}
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()
    sys.exit(0)


def _repo_root(hook_input: dict[str, object]) -> Path:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd)
    # Fall back to the script's parent path — works for repo-local hooks.
    return Path(__file__).resolve().parents[2]


def _last_assistant_text(transcript_path: Path) -> str | None:
    """Read the JSONL transcript and concatenate the latest assistant message text."""
    try:
        lines = transcript_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    latest_text: str | None = None
    for raw in lines:
        if not raw.strip():
            continue
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        # Claude Code transcript entries wrap the SDK message in
        # ``{"type": "assistant", "message": {...}}``; fall back to
        # plain SDK shape if needed.
        message = entry.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            content = message.get("content")
            text = _content_to_text(content)
            if text:
                latest_text = text
            continue
        if entry.get("role") == "assistant":
            text = _content_to_text(entry.get("content"))
            if text:
                latest_text = text
    return latest_text


def _content_to_text(content: object) -> str:
    """Flatten the SDK message ``content`` field to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
                # Some transcripts emit thinking blocks; we deliberately
                # do NOT count thinking content toward the grid signature
                # because thinking is not surfaced to the user.
        return "\n".join(parts)
    return ""


def _signature_present(text: str) -> bool:
    """Return True when text contains all three grid markers."""
    return (
        GRID_HEADER_MARKER in text
        and GRID_STATE_MARKER in text
        and GRID_VERDICT_MARKER in text
    )


def _has_filled_goals_analysis(text: str) -> bool:
    """Return True when the agent appears to have filled in Goals Analysis fields.

    A heuristic: count Goals-Analysis bold labels followed by something
    other than the bracketed prompt template. The grid renders prompts
    as ``**Plan → implementation:** _[≥48 chars + cite a repo surface — ...]_``.
    A filled answer replaces or follows that bracket with substantive
    text. The hook does not enforce length here (the closeout contract's
    substantive-content rule handles that on close-session); the hook
    only checks that the agent did not paste the template verbatim.
    """
    template_count = len(re.findall(r"\[≥48 chars \+ cite a repo surface — ", text))
    # The grid template emits 5 such bracketed placeholders. If all 5
    # remain unmodified, the agent has not engaged with Goals Analysis.
    return template_count < 5


def _run_grid(repo_root: Path) -> str | None:
    """Run ``grid`` and return its markdown stdout. None on failure."""
    try:
        proc = subprocess.run(
            [sys.executable, "internal/workflow/repo_workflow.py", "grid"],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _run_reflection_check(repo_root: Path) -> dict[str, object] | None:
    try:
        proc = subprocess.run(
            [sys.executable, "internal/workflow/repo_workflow.py", "reflection-check", "--json"],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    # reflection-check exits non-zero on FAIL; parse stdout regardless.
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _diagnostic_exit(message: str) -> None:
    """Fail-open: print a diagnostic to stderr and allow the stop."""
    sys.stderr.write(f"cortex_grid_stop_hook: {message}\n")
    _allow_stop()


def main() -> None:
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        _diagnostic_exit("empty hook input on stdin; allowing stop")
    try:
        hook_input = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        _diagnostic_exit(f"hook input is not valid JSON: {exc}; allowing stop")
        return  # unreachable

    if hook_input.get("stop_hook_active"):
        # Already inside a stop-hook re-prompt loop; allow stop to
        # avoid infinite loops if the agent cannot satisfy the gate.
        _allow_stop()

    repo_root = _repo_root(hook_input)
    transcript_path_str = hook_input.get("transcript_path")
    if not isinstance(transcript_path_str, str) or not transcript_path_str.strip():
        _diagnostic_exit("hook input missing transcript_path; allowing stop")
        return
    transcript_path = Path(transcript_path_str)

    last_text = _last_assistant_text(transcript_path)
    if last_text is None:
        _diagnostic_exit(
            f"could not read transcript at {transcript_path}; allowing stop"
        )
        return

    grid_output = _run_grid(repo_root)
    check_payload = _run_reflection_check(repo_root)
    if grid_output is None or check_payload is None:
        _diagnostic_exit(
            "grid or reflection-check command failed to produce output; allowing stop"
        )
        return

    # Gate 1: signature must be present in the assistant message.
    if not _signature_present(last_text):
        reason_parts = [
            "Cortex hygiene grid output not detected in your last message.",
            "Per AGENTS.md `## Handoff`, every chat must end with the grid"
            " output produced by"
            " `python3 internal/workflow/repo_workflow.py grid`.",
            "Paste the canonical output below verbatim, fill in the Goals"
            " Analysis fields with substantive answers (each ≥48 chars,"
            " citing at least one repo surface), then conclude.",
            "",
            "Canonical grid output for this turn:",
            "",
            grid_output,
        ]
        _block("\n".join(reason_parts))

    # Gate 2: Goals Analysis must be filled (template not pasted verbatim).
    if not _has_filled_goals_analysis(last_text):
        reason_parts = [
            "Cortex hygiene grid signature is present, but the Goals"
            " Analysis fields appear to still contain the bracketed"
            " template prompts instead of substantive answers.",
            "Each Goals Analysis field must be filled with ≥48 chars"
            " of substantive reflection citing at least one repo"
            " surface (`docs/CORTEX.md`,"
            " `internal/truth/cortex_status.json`, `cortex/**`,"
            " `tests/**`, or `CORTEX_V2_*`).",
        ]
        _block("\n".join(reason_parts))

    # Gate 3: reflection-check verdict.
    verdict = check_payload.get("verdict")
    if verdict == "FAIL":
        failures = check_payload.get("failures") or []
        gaps = check_payload.get("gaps") or []
        items = [str(item) for item in (list(failures) + list(gaps))[:10]]
        reason_parts = [
            "Cortex Repo Hygiene Grid: reflection-check verdict is FAIL.",
            "Per AGENTS.md `## Handoff`, do not close-session, finalize,"
            " or publish on FAIL. Continue work to address the failures"
            " listed below, then re-run grid.",
            "",
            "Failures and gaps:",
            *(f"- {item}" for item in items),
        ]
        _block("\n".join(reason_parts))

    # Verdict is PASS or GAPS and signature is present; allow the stop.
    _allow_stop()


if __name__ == "__main__":
    main()
