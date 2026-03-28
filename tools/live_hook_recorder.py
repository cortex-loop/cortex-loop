"""Minimal stdin-to-jsonl hook recorder for local live-validation harnesses."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def main(argv: list[str] | None = None) -> int:
    _ = argv
    payload_text = sys.stdin.read()
    log_path = os.environ.get("CORTEX_LIVE_HOOK_LOG_PATH")
    if not log_path:
        print("{}", flush=True)
        return 0

    entry: dict[str, Any] = {}
    if payload_text.strip():
        try:
            parsed = json.loads(payload_text)
        except json.JSONDecodeError:
            entry["raw"] = payload_text
        else:
            if isinstance(parsed, dict):
                entry.update(parsed)
            else:
                entry["payload"] = parsed
    entry["provider"] = os.environ.get("CORTEX_LIVE_HOOK_PROVIDER")
    entry["scenario_id"] = os.environ.get("CORTEX_LIVE_HOOK_SCENARIO_ID")

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")

    print("{}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
