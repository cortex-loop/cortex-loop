#!/usr/bin/env python3
"""Claude Code Stop hook that enforces the Cortex Repo Hygiene Grid.

The grid is the single closure artifact for every chat: all
closure / handoff material must live inside the
``## Cortex Repo Hygiene Grid`` markdown block. The hook is the
chat-boundary mechanical gate that prevents an agent from stopping
the turn without producing canonical grid output with all required
sections filled.

Hook behavior (mechanical gates, in order):

1. Read the assistant's most recent message from the transcript JSONL.
2. Run ``grid`` itself to obtain the canonical markdown for injection
   into block reasons.
3. Check the assistant message for the five canonical signature
   markers: ``## Cortex Repo Hygiene Grid``, ``### State``,
   ``### Standard Metadata``, ``### Final Handoff Mirror``,
   ``### Verdict``. Missing any → block.
4. Check that closure-shaped substrings (``Ending branch``,
   ``Verification summary``, ``Fixed now``, ``Claim earned now``,
   ``Status registry touched``, ``Final Handoff Mirror``) appear
   ONLY inside the grid block, not in prose before the grid header.
   Closure outside the grid → block.
5. Check that each Goals Analysis bracketed prompt has been replaced
   per-field. Any field whose body still contains the literal
   ``≥48 chars + cite a repo surface —`` template substring → block.
6. Check that Standard Metadata and Final Handoff Mirror fields have
   been filled (no remaining ``<fill`` placeholder substrings) → block
   if any unfilled.
7. Run ``reflection-check --json`` for the verdict. Verdict ``FAIL``
   → block with the failures list.

If all gates pass, the hook exits silently and Claude Code stops the
turn normally.

**Hard-gate honesty.** This hook does NOT short-circuit on
``stop_hook_active``: every stop attempt re-runs the gate, including
follow-up stops after a previous block. The previous version's
unconditional allow on ``stop_hook_active`` was a soft escape; this
version removes it so persistent non-compliance keeps blocking.

**Fail-open paths (documented in closeout).** The hook fails open
(allows the stop with a stderr diagnostic) on infrastructure failures
that the agent cannot fix by re-responding:

- transcript_path missing or unreadable
- hook input not valid JSON / missing transcript_path field
- ``grid`` or ``reflection-check`` command crash or timeout

These fail-open paths exist to prevent infrastructure-caused
conversation locks. Persistent agent non-compliance with the grid
contract is intentionally locked.

**Codex parity.** Codex does not support hooks. On Codex, the
contract is doctrinal-only; this hook does nothing there.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Signature markers — MUST match internal/workflow/repo_workflow.py
# constants ``GRID_HEADER_MARKER``, ``GRID_STATE_MARKER``,
# ``GRID_STANDARD_METADATA_MARKER``, ``GRID_FINAL_HANDOFF_MIRROR_MARKER``,
# ``GRID_VERDICT_MARKER``. Tests pin both sides byte-equal.
GRID_HEADER_MARKER = "## Cortex Repo Hygiene Grid"
GRID_STATE_MARKER = "### State"
GRID_STANDARD_METADATA_MARKER = "### Standard Metadata"
GRID_FINAL_HANDOFF_MIRROR_MARKER = "### Final Handoff Mirror"
GRID_VERDICT_MARKER = "### Verdict"

REQUIRED_MARKERS: tuple[str, ...] = (
    GRID_HEADER_MARKER,
    GRID_STATE_MARKER,
    GRID_STANDARD_METADATA_MARKER,
    GRID_FINAL_HANDOFF_MIRROR_MARKER,
    GRID_VERDICT_MARKER,
)

# Substrings that, if they appear in the message BEFORE
# GRID_HEADER_MARKER, indicate closure-shaped prose has leaked outside
# the consolidated grid (violation of the "single grid contains all
# closure" rule).
CLOSURE_LEAK_MARKERS: tuple[str, ...] = (
    "Ending branch",
    "Verification summary",
    "Fixed now",
    "Claim earned now",
    "Status registry touched",
    "Final Handoff Mirror",
)

# Goals Analysis field labels — must match
# repo_workflow.py::GOALS_ANALYSIS_FIELDS. The hook checks per-field
# that each field's body does NOT still contain the literal template
# substring.
GOALS_ANALYSIS_FIELD_LABELS: tuple[str, ...] = (
    "Plan → implementation",
    "Quality assessment",
    "Iteration moments this session",
    "Forward-looking confidence",
    "Tied to Cortex goals",
)

# The bracketed template substring inside every Goals Analysis prompt.
# An unfilled field still contains this substring; a filled field has
# replaced it with substantive prose.
GOALS_ANALYSIS_TEMPLATE_TOKEN = "≥48 chars + cite a repo surface —"

# `<fill` placeholder substring that appears in Standard Metadata and
# Final Handoff Mirror cells until the agent replaces them in place.
FILL_PLACEHOLDER_TOKEN = "<fill"


def _allow_stop() -> None:
    """Exit silently to allow Claude Code to stop the turn."""
    sys.exit(0)


def _block(reason: str) -> None:
    """Emit a block decision JSON and exit successfully."""
    payload = {"decision": "block", "reason": reason}
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()
    sys.exit(0)


def _repo_root(hook_input: dict[str, object]) -> Path:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd)
    return Path(__file__).resolve().parents[2]


def _last_assistant_text(transcript_path: Path) -> str | None:
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
        message = entry.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            text = _content_to_text(message.get("content"))
            if text:
                latest_text = text
            continue
        if entry.get("role") == "assistant":
            text = _content_to_text(entry.get("content"))
            if text:
                latest_text = text
    return latest_text


def _content_to_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
        return "\n".join(parts)
    return ""


def _missing_required_markers(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def _closure_leak_before_grid(text: str) -> list[str]:
    """Return closure markers that appear before the grid header."""
    grid_pos = text.find(GRID_HEADER_MARKER)
    if grid_pos == -1:
        return []
    prefix = text[:grid_pos]
    return [marker for marker in CLOSURE_LEAK_MARKERS if marker in prefix]


def _unfilled_goals_analysis_fields(text: str) -> list[str]:
    """Return Goals Analysis field labels whose body still contains the template.

    For each field, we look at the substring between
    ``**{label}:**`` and the next ``\n\n`` boundary (or the next bold
    label, whichever comes first). If that substring contains the
    template token, the field is unfilled.
    """
    unfilled: list[str] = []
    for label in GOALS_ANALYSIS_FIELD_LABELS:
        marker = f"**{label}:**"
        idx = text.find(marker)
        if idx == -1:
            # Field label missing entirely — count as unfilled.
            unfilled.append(label)
            continue
        body_start = idx + len(marker)
        # Find the end of this field's body: next double-newline OR next
        # bold-label OR next section header. Take the earliest.
        candidates: list[int] = []
        next_blank = text.find("\n\n", body_start)
        if next_blank != -1:
            candidates.append(next_blank)
        next_section = text.find("\n###", body_start)
        if next_section != -1:
            candidates.append(next_section)
        body_end = min(candidates) if candidates else len(text)
        body = text[body_start:body_end]
        if GOALS_ANALYSIS_TEMPLATE_TOKEN in body:
            unfilled.append(label)
    return unfilled


def _unfilled_metadata_or_mirror(text: str) -> bool:
    """Return True if any Standard Metadata or Final Handoff Mirror cell still has `<fill`.

    The agent is supposed to replace each ``<fill: ...>`` placeholder
    with the actual value in place. If any placeholder remains, the
    closure block was not filled.
    """
    grid_pos = text.find(GRID_HEADER_MARKER)
    if grid_pos == -1:
        return True
    grid_text = text[grid_pos:]
    return FILL_PLACEHOLDER_TOKEN in grid_text


def _run_grid(repo_root: Path) -> str | None:
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

    # Note: stop_hook_active is intentionally NOT short-circuited. The
    # previous version's unconditional allow on stop_hook_active was a
    # soft escape that let persistent non-compliance bypass the gate
    # after one block. This version re-runs every gate on every stop
    # attempt; only infrastructure failures (transcript missing, grid
    # crash) fail open via the diagnostic_exit paths below.

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

    # Gate 1: required signature markers must all be present.
    missing = _missing_required_markers(last_text)
    if missing:
        reason_parts = [
            "Cortex hygiene grid output is incomplete in your last message.",
            "Per AGENTS.md `## Handoff`, every chat must end with the grid"
            " produced by"
            " `python3 internal/workflow/repo_workflow.py grid`,"
            " with all required sections present and bracketed prompts"
            " filled in place.",
            "",
            f"Missing required markers: {', '.join(missing)}",
            "",
            "Canonical grid output for this turn:",
            "",
            grid_output,
        ]
        _block("\n".join(reason_parts))

    # Gate 2: closure markers must not appear before the grid header.
    leaks = _closure_leak_before_grid(last_text)
    if leaks:
        reason_parts = [
            "Closure-shaped content appears outside the grid in your"
            " last message. All closure / handoff material must live"
            " inside the single `## Cortex Repo Hygiene Grid` block at"
            " the bottom of the response. Normal response prose may"
            " precede the grid; closure content (Standard Metadata,"
            " Final Handoff Mirror, etc.) may NOT.",
            "",
            f"Closure markers detected before the grid header: {', '.join(leaks)}",
            "",
            "Move that content into the grid's `### Standard Metadata`"
            " and `### Final Handoff Mirror` sections (filling each"
            " bracketed `<fill>` placeholder in place) and re-respond.",
        ]
        _block("\n".join(reason_parts))

    # Gate 3: each Goals Analysis field must be filled per-field.
    unfilled_ga = _unfilled_goals_analysis_fields(last_text)
    if unfilled_ga:
        reason_parts = [
            "Goals Analysis has unfilled bracketed templates. Each"
            " field must replace its `[≥48 chars + cite a repo surface"
            " — ...]` template with substantive prose citing at least"
            " one repo surface (`docs/CORTEX.md`,"
            " `internal/truth/cortex_status.json`, `cortex/**`,"
            " `tests/**`, or `CORTEX_V2_*`).",
            "",
            f"Fields still showing the unfilled template: {', '.join(unfilled_ga)}",
        ]
        _block("\n".join(reason_parts))

    # Gate 4: Standard Metadata and Final Handoff Mirror fields filled.
    if _unfilled_metadata_or_mirror(last_text):
        reason_parts = [
            "Standard Metadata or Final Handoff Mirror has unfilled"
            " `<fill: ...>` placeholders. Replace each placeholder in"
            " place with the actual value (use `n/a` or"
            " `n/a (no work this turn)` where appropriate, but do not"
            " leave `<fill>` brackets in the rendered grid).",
        ]
        _block("\n".join(reason_parts))

    # Gate 5: reflection-check verdict.
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

    # All gates passed; allow the stop.
    _allow_stop()


if __name__ == "__main__":
    main()
