# Codex App Project Stop Hook Probe

Surface: internal / recon
Probe date: 2026-04-30
Subject surface: Codex App for Mac
Result scope: Codex App only; do not generalize to Codex CLI, Claude Code,
Gemini CLI, or API surfaces.

## Versions Tested

- Codex App: `26.422.71525`
- Codex App build: `2210`
- Bundled CLI: `codex-cli 0.126.0-alpha.8`
- Repo: `/Users/erikahoward/cortex-loop`
- Branch during probe: `codex/20260429-215954-codex-app-hook-probe`
- Sentinel: `CORTEX_PROBE_SENTINEL_2026_04_30`
- Redactions: none

## Per-Question Verdicts

| Question | Verdict | Finding |
|---|---|---|
| Q1: Does Codex App load trusted project-level `.codex/config.toml`, and does trust persist? | **Confirmed** | Project Stop hook loaded and fired in the first subject thread. After closing that thread and opening a new Codex App thread on the same project, no trust re-prompt was reported and the same project hook fired again on `REOPENED`. Exact trust UX text was not captured because no trust prompt was observed or reported during this probe. |
| Q2: Does the Stop hook fire, and what input shape does it receive? | **Confirmed** | The hook fired on a trivial subject-thread response and captured top-level keys `session_id`, `turn_id`, `transcript_path`, `cwd`, `hook_event_name`, `model`, `permission_mode`, `stop_hook_active`, and `last_assistant_message`. Codex also fired a separate title-generation Stop event with `transcript_path: null` and `model: gpt-5.4-mini`. |
| Q3: Does `decision: "block"` inject a sentinel reason into the next assistant turn? | **Confirmed** | The hook blocked the `BASELINE` Stop event once. The next Stop event had `stop_hook_active: true` and `last_assistant_message: "CORTEX_PROBE_SENTINEL_2026_04_30 acknowledged."`, demonstrating that the block reason reached the model-visible continuation path. |

## Q1: Project Config Load and Trust Persistence

Temporary project config was active and pointed the Codex App Stop hook to
`.codex/hooks/codex_app_probe_stop_hook.py`. The first subject thread sent:

```text
Reply with exactly the word ACKNOWLEDGED
```

Visible subject-thread output:

```text
ACKNOWLEDGED

Stop - Codex App hook probe
completed
```

This confirms project-level config and Stop hook load in Codex App for Mac.
The hook log also captured the actual assistant turn as event 2.

After Q3, the subject Codex App thread was closed and a new thread was opened
on the same project. No trust prompt was reported by the user. The reopened
thread sent:

```text
Reply with exactly the word REOPENED
```

Visible subject-thread output from the supplied screenshot:

```text
REOPENED

Stop - Codex App hook probe
completed
```

The hook log captured `last_assistant_message: "REOPENED"` as event 7,
which confirms project hook loading persisted across reopening the project
for this tested session. Trust UX is therefore recorded as: no prompt observed
or reported; exact trust text not captured.

## Q2: Hook Input Shape

The hook received one JSON object on stdin per Stop event. The first user
subject turn produced two Stop events: one title-generation event and one
actual assistant-message event.

### Field Enumeration

Public documentation reference: OpenAI Codex hooks docs, retrieved
2026-04-30, `https://developers.openai.com/codex/hooks`.

| Field | Observed contents | Public docs status | Notes |
|---|---|---|---|
| `session_id` | UUID-like string, stable per thread for subject events | Documented common input field | Subject ACKNOWLEDGED/BASELINE share one `session_id`; reopened thread has a new `session_id`. |
| `turn_id` | UUID-like string for each turn | Documented Stop / turn-scoped field | BASELINE block event and sentinel continuation share the same `turn_id`. |
| `transcript_path` | `null` for title-generation events; `.codex/sessions/...jsonl` path for real assistant turns | Documented common input field | The null title-event path is observed behavior worth preserving. |
| `cwd` | `/Users/erikahoward/cortex-loop` | Documented common input field | Confirms project working directory. |
| `hook_event_name` | `Stop` | Documented common input field | Matches configured Stop hook. |
| `model` | `gpt-5.4-mini` for title generation; `gpt-5.5` for subject assistant turns | Documented common input field | Confirms title generation can use a different model from the assistant turn. |
| `permission_mode` | `bypassPermissions` | **Not found in public docs page** | Useful undocumented field for future lifecycle diagnostics. |
| `stop_hook_active` | `false` for original Stop events; `true` for the continuation after block | Documented Stop field | Confirms the continuation path is explicitly marked. |
| `last_assistant_message` | Title JSON string, `ACKNOWLEDGED`, `BASELINE`, sentinel acknowledgment, `REOPENED` | Documented Stop field | Carries the exact assistant text needed for closure validation. |

### Raw Hook Input: Subject ACKNOWLEDGED

```jsonl
{"session_id":"019ddd77-8749-7232-aa41-085e3bcfe5d3","turn_id":"019ddd77-875f-7502-a427-af995316965f","transcript_path":null,"cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.4-mini","permission_mode":"bypassPermissions","stop_hook_active":false,"last_assistant_message":"{\"title\":\"Reply with ACKNOWLEDGED\"}"}
{"session_id":"019ddd77-85e1-7420-9384-4f477ace8a1f","turn_id":"019ddd77-8748-7d32-b288-627e93543075","transcript_path":"/Users/erikahoward/.codex/sessions/2026/04/30/rollout-2026-04-30T10-18-11-019ddd77-85e1-7420-9384-4f477ace8a1f.jsonl","cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.5","permission_mode":"bypassPermissions","stop_hook_active":false,"last_assistant_message":"ACKNOWLEDGED"}
```

## Q3: Block-and-Inject Sentinel Path

The control thread armed `mode.txt` to `block_once`, then the subject thread
sent:

```text
Reply with exactly the word BASELINE
```

Visible subject-thread output reported by the user:

```text
BASELINE

Stop - Codex App hook probe
blocked
```

Raw hook input shows that the hook returned a block on the `BASELINE` Stop
event, then Codex generated a continuation with `stop_hook_active: true`.

```jsonl
{"session_id":"019ddd77-85e1-7420-9384-4f477ace8a1f","turn_id":"019ddd78-c36c-79e1-8c1a-7180763aeaa8","transcript_path":"/Users/erikahoward/.codex/sessions/2026/04/30/rollout-2026-04-30T10-18-11-019ddd77-85e1-7420-9384-4f477ace8a1f.jsonl","cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.5","permission_mode":"bypassPermissions","stop_hook_active":false,"last_assistant_message":"BASELINE"}
{"session_id":"019ddd77-85e1-7420-9384-4f477ace8a1f","turn_id":"019ddd78-c36c-79e1-8c1a-7180763aeaa8","transcript_path":"/Users/erikahoward/.codex/sessions/2026/04/30/rollout-2026-04-30T10-18-11-019ddd77-85e1-7420-9384-4f477ace8a1f.jsonl","cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.5","permission_mode":"bypassPermissions","stop_hook_active":true,"last_assistant_message":"CORTEX_PROBE_SENTINEL_2026_04_30 acknowledged."}
```

Actual next-assistant-turn output, byte-for-byte:

```text
CORTEX_PROBE_SENTINEL_2026_04_30 acknowledged.
```

Verdict basis: the sentinel was not in the user prompt. It came from the
hook's block reason, and the next assistant turn acknowledged it. The
block-and-inject path therefore reaches the model-visible continuation path
for Codex App on this machine.

## Q1 Reopen Capture

Raw hook input from the reopened subject thread:

```jsonl
{"session_id":"019ddd7a-c77a-7292-8900-fd707a9b908c","turn_id":"019ddd7a-c8c5-7480-8c26-56b134c44c28","transcript_path":"/Users/erikahoward/.codex/sessions/2026/04/30/rollout-2026-04-30T10-21-44-019ddd7a-c77a-7292-8900-fd707a9b908c.jsonl","cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.5","permission_mode":"bypassPermissions","stop_hook_active":false,"last_assistant_message":"REOPENED"}
{"session_id":"019ddd7a-c8c9-7ba1-84a4-9bf967fe9ae9","turn_id":"019ddd7a-c8de-7861-883b-b1ffffb36fbc","transcript_path":null,"cwd":"/Users/erikahoward/cortex-loop","hook_event_name":"Stop","model":"gpt-5.4-mini","permission_mode":"bypassPermissions","stop_hook_active":false,"last_assistant_message":"{\"title\":\"Reply REOPENED\"}"}
```

The screenshot supplied by the user is local evidence at:
`/Users/erikahoward/Downloads/Screenshot 2026-04-30 at 10.21.46.png`.

## Exact Temporary `.codex/config.toml`

```toml
[features]
codex_hooks = true

[[hooks.Stop]]
[[hooks.Stop.hooks]]
type = "command"
command = 'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/codex_app_probe_stop_hook.py"'
timeout = 60
statusMessage = "Codex App hook probe"
```

## Exact Temporary Hook Script

```python
#!/usr/bin/env python3
"""Temporary Codex App Stop-hook probe.

This script is intentionally not a product hook. It records the exact
Stop-hook stdin payload emitted by Codex App, then optionally performs a
one-shot block with a sentinel reason to test whether the block reason is
model-visible in the next assistant turn.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any


RUN_ID = "20260430_codex_app_stop_hook_probe"
SENTINEL = "CORTEX_PROBE_SENTINEL_2026_04_30"
CONTROL_SKIP_MARKER = "CORTEX_PROBE_CONTROL_THREAD_DO_NOT_BLOCK"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_dir() -> Path:
    return _repo_root() / "lab" / "codex_app_hook_probe" / RUN_ID


def _append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def _safe_json_loads(raw: str) -> dict[str, Any] | None:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _summary(raw: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    env_keys = [
        "PWD",
        "SHELL",
        "USER",
        "HOME",
        "CODEX_HOME",
        "CODEX_SANDBOX",
        "CODEX_APP",
    ]
    last_message = None
    if payload is not None:
        last_message = payload.get("last_assistant_message")
    return {
        "timestamp_utc": now,
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "env_hints": {key: os.environ.get(key) for key in env_keys if os.environ.get(key) is not None},
        "raw_stdin_len": len(raw),
        "raw_json_parse_ok": payload is not None,
        "top_level_keys": sorted(payload) if payload is not None else [],
        "last_assistant_message_type": type(last_message).__name__ if last_message is not None else None,
        "last_assistant_message_len": len(last_message) if isinstance(last_message, str) else None,
        "last_assistant_message": last_message,
    }


def _mode(run_dir: Path) -> str:
    mode_path = run_dir / "mode.txt"
    if not mode_path.exists():
        return "allow"
    return mode_path.read_text(encoding="utf-8").strip()


def _block(reason: str) -> None:
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.stdout.flush()


def main() -> int:
    raw = sys.stdin.read()
    payload = _safe_json_loads(raw)
    run_dir = _run_dir()
    run_dir.mkdir(parents=True, exist_ok=True)

    _append(run_dir / "stop_events.jsonl", raw)
    _append(run_dir / "events_summary.jsonl", json.dumps(_summary(raw, payload), sort_keys=True))

    last_message = ""
    if payload is not None and isinstance(payload.get("last_assistant_message"), str):
        last_message = payload["last_assistant_message"]

    if CONTROL_SKIP_MARKER in last_message:
        _append(run_dir / "control_skip_events.log", dt.datetime.now(dt.timezone.utc).isoformat())
        return 0

    blocked_once = run_dir / "blocked_once"
    if _mode(run_dir) == "block_once" and not blocked_once.exists():
        blocked_once.write_text(dt.datetime.now(dt.timezone.utc).isoformat(), encoding="utf-8")
        _block(
            f"{SENTINEL}: In your next assistant message, explicitly acknowledge this sentinel."
        )
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Control-Thread Events Excluded From Verdicts

Two Stop events were emitted by this control thread while the probe hook was
active. They contained `CORTEX_PROBE_CONTROL_THREAD_DO_NOT_BLOCK` and were
excluded from subject-thread verdicts. They confirmed the skip guard worked
and prevented the control thread from consuming the one-shot sentinel block.

## Cleanup Verification

- Original `.codex/config.toml` restored: yes.
- Temporary probe hook active after cleanup: no.
- Active `.codex` config references `codex_app_probe_stop_hook.py`: no.
- Probe run logs left in active hook path: no; raw evidence is embedded in
  this report.
- `tests/internal/test_docs_boundary.py` updated for this report: yes.
- Focused docs-boundary test green: yes.

## Interpretation Limits

This probe confirms Codex App project Stop hooks on this machine, for this
repo, with the tested Codex App version. It does not generalize to Claude Code
Desktop, Gemini CLI, Codex CLI, or API surfaces. It also does not prove Cortex
improves model output; it only proves that Codex App can load project Stop
hooks, provide usable Stop input, and route a block reason into a model-visible
continuation.
