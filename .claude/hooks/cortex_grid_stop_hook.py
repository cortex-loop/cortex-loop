#!/usr/bin/env python3
"""Claude Code Stop hook that enforces Cortex Mission Reflection.

The grid is the single closure artifact for every chat: all closure /
handoff material must live inside one markdown table under the
``## Cortex Mission Reflection`` header. The hook is the chat-boundary
mechanical gate that prevents an agent from stopping the turn without
producing the Cortex Mission Reflection rows with substantive,
repo-grounded content.

Hook behavior (mechanical gates, in order):

1. Read the assistant's most recent message from the transcript JSONL.
2. Run ``grid`` itself to obtain the canonical markdown for injection
   into block reasons.
3. Check the assistant message for the canonical one-table shape:
   ``## Cortex Mission Reflection``, exactly one ``| Field | Value |``
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

**Codex App parity.** Codex App uses a separate repo-local Stop hook at
``.codex/hooks/cortex_mission_reflection_stop_hook.py`` because Codex
Stop hooks provide ``last_assistant_message`` directly rather than a
Claude transcript path. Both hooks share
``internal.workflow.mission_reflection`` as the graph contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal.workflow import mission_reflection


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


def _run_grid(repo_root: Path, mode: str) -> str | None:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "internal/workflow/repo_workflow.py",
                "grid",
                "--mode",
                mode,
            ],
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

    validation_mode = mission_reflection.infer_graph_mode(last_text)
    grid_output = _run_grid(repo_root, validation_mode)
    check_payload = _run_reflection_check(repo_root)
    if grid_output is None or check_payload is None:
        _diagnostic_exit(
            "grid or reflection-check command failed to produce output; allowing stop"
        )
        return

    result = mission_reflection.validate_graph_text(
        last_text,
        check_payload=check_payload,
        require_filled=True,
        mode=validation_mode,
    )
    if not result.ok:
        reason_parts = [
            "Cortex Mission Reflection did not pass the shared graph validator.",
            "Per the mission-reflection contract, every chat must end with the"
            " graph produced by `python3 internal/workflow/repo_workflow.py grid"
            f" --mode {validation_mode}`,"
            " filled in place, as exactly one markdown table under"
            f" `{mission_reflection.GRAPH_HEADER_MARKER}`.",
            "",
            "Validation errors:",
            result.reason(),
            "",
            "Canonical graph skeleton for this turn:",
            "",
            grid_output,
        ]
        _block("\n".join(reason_parts))

    # All gates passed; allow the stop.
    _allow_stop()


if __name__ == "__main__":
    main()
