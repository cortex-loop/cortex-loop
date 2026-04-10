"""Helpers for the machine-backed Cortex status registry."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATUS_SOURCE = ROOT / "internal" / "truth" / "cortex_status.json"
STATUS_DOC = ROOT / "docs" / "CORTEX_STATUS.md"


def load_status(path: Path | None = None) -> dict[str, Any]:
    source = path or STATUS_SOURCE
    return json.loads(source.read_text(encoding="utf-8"))


def resting_branch(path: Path | None = None) -> str:
    resting_state = load_status(path)["resting_state"]
    return str(resting_state["branch"])


def read_baseline(path: Path | None = None) -> tuple[str, str]:
    branch = resting_branch(path)
    resolved = subprocess.run(
        ["git", "rev-parse", branch],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return branch, resolved.stdout.strip()


def accepted_conformance_next_decision(path: Path | None = None) -> str | None:
    conformance = load_status(path).get("conformance_summary", {})
    decision = conformance.get("accepted_next_decision")
    if decision is None:
        return None
    return str(decision)
