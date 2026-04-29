#!/usr/bin/env python3
"""Claude Code Stop hook that enforces the Cortex Repo Hygiene Grid.

The grid is the single closure artifact for every chat: all closure /
handoff material must live inside one markdown table under the
``## Cortex Repo Hygiene Grid`` header. The hook is the chat-boundary
mechanical gate that prevents an agent from stopping the turn without
producing the Cortex Mission Reflection rows with substantive,
repo-grounded content.

Hook behavior (mechanical gates, in order):

1. Read the assistant's most recent message from the transcript JSONL.
2. Run ``grid`` itself to obtain the canonical markdown for injection
   into block reasons.
3. Check the assistant message for the canonical one-table shape:
   ``## Cortex Repo Hygiene Grid``, exactly one ``| Field | Value |``
   table header, exactly one ``|---|---|`` separator, no ``###``
   subsections inside the grid, and required row labels such as
   ``Repo: State``, ``Mission: Cortex target``, ``Closure: Metadata``,
   and ``Verdict``. Missing any → block. Stale dashboard rows such as
   ``Progress:*`` or a fixed ``bio_to_code matrix`` row also block.
4. Check that closure-shaped substrings (``Ending branch``,
   ``Verification summary``, ``Fixed now``, ``Claim earned now``,
   ``Status registry touched``, ``Closure: Metadata``) appear
   ONLY inside the grid block, not in prose before the grid header.
   Closure outside the grid → block.
5. Check that each Cortex Mission Reflection row has been replaced
   per-field. Any row whose body still contains the literal
   ``mission reflection —`` template substring or lacks a repo-grounding
   citation or is too short → block.
6. Check that closure metadata has been filled (no remaining
   ``closure metadata —`` template or ``<fill`` placeholder substrings)
   → block if unfilled.
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
# constants ``GRID_HEADER_MARKER``, ``GRID_TABLE_HEADER_MARKER``,
# ``GRID_TABLE_SEPARATOR_MARKER``, ``GRID_FORBIDDEN_SECTION_MARKER``,
# and ``REQUIRED_GRID_ROW_LABELS``. Tests pin both sides byte-equal.
GRID_HEADER_MARKER = "## Cortex Repo Hygiene Grid"
GRID_TABLE_HEADER_MARKER = "| Field | Value |"
GRID_TABLE_SEPARATOR_MARKER = "|---|---|"
GRID_FORBIDDEN_SECTION_MARKER = "### "

REQUIRED_GRID_ROW_LABELS: tuple[str, ...] = (
    "Repo: State",
    "Repo: Gates",
    "Mission: Cortex target",
    "Mission: Boundary judgment",
    "Mission: Model I/O path",
    "Reflection: Quality judgment",
    "Evidence: Earned",
    "Evidence: Not earned / forbidden",
    "Decision: Next ownership move",
    "Closure: Metadata",
    "Verdict",
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
    "Closure: Metadata",
)

# Cortex Mission Reflection labels — must match
# repo_workflow.py::MISSION_REFLECTION_FIELDS. The hook checks per-row
# that each field is filled with a substantive, repo-grounded answer.
MISSION_REFLECTION_ROW_LABELS: tuple[str, ...] = (
    "Mission: Cortex target",
    "Mission: Boundary judgment",
    "Mission: Theory of improvement",
    "Mission: Model I/O path",
    "Reflection: Plan vs actual",
    "Reflection: Quality judgment",
    "Reflection: Iteration evidence",
    "Evidence: Earned",
    "Evidence: Not earned / forbidden",
    "Decision: Next ownership move",
)

# Template substrings. An unfilled reflection row still contains the
# mission token; unfilled closure still contains the closure token.
MISSION_REFLECTION_TEMPLATE_TOKEN = "mission reflection —"
CLOSURE_METADATA_TEMPLATE_TOKEN = "closure metadata —"

MISSION_REFLECTION_MIN_CHARS = 120

REPO_CITATION_PATTERN = re.compile(
    r"(docs/CORTEX\.md|internal/truth/cortex_status\.json|cortex/|tests/|CORTEX_V2_)"
)

# `<fill` placeholder substring should not appear in filled output.
FILL_PLACEHOLDER_TOKEN = "<fill"

STALE_DASHBOARD_ROW_PREFIX = "Progress:"
STALE_DASHBOARD_ROW_LABELS: tuple[str, ...] = (
    "bio_to_code matrix",
    "hosts",
    "shipping default",
    "current train",
    "next train",
    "research lines u/eval",
)


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


def _grid_text(text: str) -> str | None:
    grid_pos = text.find(GRID_HEADER_MARKER)
    if grid_pos == -1:
        return None
    return text[grid_pos:]


def _grid_shape_errors(text: str) -> list[str]:
    """Return missing or forbidden one-table-grid shape elements."""
    grid_text = _grid_text(text)
    if grid_text is None:
        return [GRID_HEADER_MARKER]
    errors: list[str] = []
    if f"\n{GRID_FORBIDDEN_SECTION_MARKER}" in grid_text:
        errors.append("forbidden `###` subsection inside grid")
    if grid_text.count(GRID_TABLE_HEADER_MARKER) != 1:
        errors.append(f"expected exactly one `{GRID_TABLE_HEADER_MARKER}` table header")
    if grid_text.count(GRID_TABLE_SEPARATOR_MARKER) != 1:
        errors.append(f"expected exactly one `{GRID_TABLE_SEPARATOR_MARKER}` table separator")
    for label in REQUIRED_GRID_ROW_LABELS:
        if f"**{label}**" not in grid_text:
            errors.append(f"missing row `{label}`")
    return errors


def _table_rows(text: str) -> dict[str, str]:
    """Parse the one-table grid into {row_label: cell_text}."""
    grid_text = _grid_text(text)
    if grid_text is None:
        return {}
    rows: dict[str, str] = {}
    pattern = re.compile(r"^\| \*\*(?P<label>.*?)\*\* \| (?P<body>.*?) \|$", re.MULTILINE)
    for match in pattern.finditer(grid_text):
        rows[match.group("label")] = match.group("body")
    return rows


def _clean_cell_text(text: str) -> str:
    """Normalize markdown-table cell text for validation checks."""
    text = text.replace("<br>", " ")
    text = text.replace("\\|", "|")
    text = re.sub(r"[_`*]", "", text)
    return " ".join(text.split())


def _stale_dashboard_rows(rows: dict[str, str]) -> list[str]:
    stale: list[str] = []
    for label in rows:
        if label.startswith(STALE_DASHBOARD_ROW_PREFIX):
            stale.append(label)
        if any(label.endswith(item) for item in STALE_DASHBOARD_ROW_LABELS):
            stale.append(label)
    return sorted(set(stale))


def _closure_leak_before_grid(text: str) -> list[str]:
    """Return closure markers that appear before the grid header."""
    grid_pos = text.find(GRID_HEADER_MARKER)
    if grid_pos == -1:
        return []
    prefix = text[:grid_pos]
    return [marker for marker in CLOSURE_LEAK_MARKERS if marker in prefix]


def _mission_reflection_errors(rows: dict[str, str]) -> list[str]:
    """Return Mission Reflection rows that are missing, short, uncited, or templated."""
    unfilled: list[str] = []
    for label in MISSION_REFLECTION_ROW_LABELS:
        body = rows.get(label)
        if body is None:
            unfilled.append(f"{label}: missing")
            continue
        clean_body = _clean_cell_text(body)
        if MISSION_REFLECTION_TEMPLATE_TOKEN in body:
            unfilled.append(f"{label}: template still present")
            continue
        if len(clean_body) < MISSION_REFLECTION_MIN_CHARS:
            unfilled.append(
                f"{label}: too short ({len(clean_body)} chars; minimum {MISSION_REFLECTION_MIN_CHARS})"
            )
        if not REPO_CITATION_PATTERN.search(body):
            unfilled.append(f"{label}: missing repo-grounding citation")
    return unfilled


def _unfilled_metadata_or_mirror(rows: dict[str, str]) -> bool:
    """Return True if closure rows still have template placeholders.

    The agent is supposed to replace each closure placeholder with the
    actual value in place. If any placeholder remains, the closure row
    was not filled.
    """
    closure = rows.get("Closure: Metadata")
    if closure is None:
        return True
    return (
        FILL_PLACEHOLDER_TOKEN in closure
        or CLOSURE_METADATA_TEMPLATE_TOKEN in closure
    )


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

    # Gate 1: one-table grid shape must be present.
    grid_shape_errors = _grid_shape_errors(last_text)
    if grid_shape_errors:
        reason_parts = [
            "Cortex hygiene grid output is not the required one-table shape.",
            "Per AGENTS.md `## Handoff`, every chat must end with the grid"
            " produced by"
            " `python3 internal/workflow/repo_workflow.py grid`,"
            " as exactly one markdown table under"
            " `## Cortex Repo Hygiene Grid`. No `###` subsections are"
            " allowed inside the grid.",
            "",
            "Shape errors:",
            *(f"- {item}" for item in grid_shape_errors),
            "",
            "Canonical grid output for this turn:",
            "",
            grid_output,
        ]
        _block("\n".join(reason_parts))

    rows = _table_rows(last_text)

    # Gate 1b: stale dashboard rows are forbidden.
    stale_rows = _stale_dashboard_rows(rows)
    if stale_rows:
        reason_parts = [
            "Cortex hygiene grid contains stale dashboard rows. The"
            " closing artifact is now Cortex Mission Reflection, not"
            " a status dashboard. Remove fixed `Progress:*` rows and"
            " use registry facts only inside causal reflection when"
            " they support an argument.",
            "",
            "Stale rows detected:",
            *(f"- {item}" for item in stale_rows),
        ]
        _block("\n".join(reason_parts))

    # Gate 2: closure markers must not appear before the grid header.
    leaks = _closure_leak_before_grid(last_text)
    if leaks:
        reason_parts = [
            "Closure-shaped content appears outside the grid in your"
            " last message. All closure / handoff material must live"
            " inside the single table under"
            " `## Cortex Repo Hygiene Grid` at the bottom of the"
            " response. Normal response prose may precede the grid;"
            " closure content (standard metadata, final mirror, etc.)"
            " may NOT.",
            "",
            f"Closure markers detected before the grid header: {', '.join(leaks)}",
            "",
            "Move that content into the appropriate mission reflection"
            " or `Closure: Metadata` row and re-respond.",
        ]
        _block("\n".join(reason_parts))

    # Gate 3: each Cortex Mission Reflection row must be substantive.
    reflection_errors = _mission_reflection_errors(rows)
    if reflection_errors:
        reason_parts = [
            "Cortex Mission Reflection rows are not substantive enough."
            " Each mission/reflection/evidence/decision row must replace"
            " the template, be at least"
            f" {MISSION_REFLECTION_MIN_CHARS} characters, and cite at"
            " least one repo surface (`docs/CORTEX.md`,"
            " `internal/truth/cortex_status.json`, `cortex/**`,"
            " `tests/**`, or `CORTEX_V2_*`).",
            "",
            "Rows to fix:",
            *(f"- {item}" for item in reflection_errors),
        ]
        _block("\n".join(reason_parts))

    # Gate 4: compact closure metadata row filled.
    if _unfilled_metadata_or_mirror(rows):
        reason_parts = [
            "Closure metadata still has an unfilled template. Replace"
            " the `Closure: Metadata` row in place with ending branch,"
            " commit/no commit, verification summary, returned-to-main,"
            " and registry/doc regeneration facts.",
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
