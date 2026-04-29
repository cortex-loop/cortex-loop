"""Tests for the Cortex Mission Reflection Stop hook.

The hook lives at ``.claude/hooks/cortex_grid_stop_hook.py`` and is the
Claude Code chat-boundary gate for the per-turn Cortex Repo Hygiene Grid.
The grid is one markdown table, but its semantic job is not status
recitation: it must force grounded Cortex Mission Reflection.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "cortex_grid_stop_hook.py"

MISSION_FILL = (
    "This row cites `docs/CORTEX.md` and `tests/internal/test_cortex_grid_stop_hook.py` "
    "while making a causal Cortex Mission Reflection claim about boundary, model I/O, "
    "evidence, and next ownership rather than reciting static dashboard status."
)

CLOSURE_FILL = (
    "ending branch `codex/test`; commit `no commit`; verification no verification "
    "this turn; returned to main no; Status registry touched none; status doc "
    "regenerated no; CORTEX.md regenerated no"
)


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


def _fill_mission_reflection(grid_markdown: str) -> str:
    return re.sub(
        r"_\[mission reflection — [^\]]+\]_",
        MISSION_FILL,
        grid_markdown,
    )


def _fill_closure_metadata(grid_markdown: str) -> str:
    return re.sub(
        r"_\[closure metadata — [^\]]+\]_",
        CLOSURE_FILL,
        grid_markdown,
    )


def _fully_filled_grid() -> str:
    return _fill_closure_metadata(_fill_mission_reflection(_canonical_grid()))


def test_hook_blocks_when_message_missing_grid_header(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path, "Plain assistant message; no grid.")

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "one-table shape" in payload["reason"].lower()
    assert "## Cortex Repo Hygiene Grid" in payload["reason"]


def test_hook_blocks_when_required_mission_row_missing(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    mutated = canonical.replace("**Mission: Cortex target**", "**NOT: Cortex target**")
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Mission: Cortex target" in payload["reason"]


def test_hook_blocks_when_closure_metadata_row_missing(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    mutated = canonical.replace("**Closure: Metadata**", "**NOT: Metadata**")
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Closure: Metadata" in payload["reason"]


def test_hook_blocks_when_grid_contains_legacy_subsection(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    mutated = canonical.replace("| Field | Value |", "### State\n\n| Field | Value |", 1)
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "forbidden" in payload["reason"].lower()


def test_hook_blocks_stale_dashboard_rows(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    stale_row = "| **Progress: bio_to_code matrix** | 8/8 landed stale dashboard row |"
    mutated = canonical.replace("| **Verdict** |", stale_row + "\n| **Verdict** |", 1)
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "stale dashboard" in payload["reason"].lower()
    assert "Progress: bio_to_code matrix" in payload["reason"]


def test_hook_blocks_when_closure_marker_appears_before_grid(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    leaked = "Ending branch: main\n\nFixed now: lots of stuff\n\n" + canonical
    transcript = _write_transcript(tmp_path, leaked)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "outside the grid" in payload["reason"].lower() or "before the grid" in payload["reason"].lower()


def test_hook_blocks_when_one_mission_reflection_row_unfilled(tmp_path: Path) -> None:
    canonical = _canonical_grid()
    template_pattern = re.compile(r"_\[mission reflection — [^\]]+\]_")
    matches = list(template_pattern.finditer(canonical))
    assert len(matches) == 10, "expected 10 Cortex Mission Reflection templates"
    filled = canonical
    for match in matches[:9]:
        filled = filled.replace(match.group(0), MISSION_FILL, 1)
    filled = _fill_closure_metadata(filled)
    transcript = _write_transcript(tmp_path, filled)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Cortex Mission Reflection" in payload["reason"]
    assert "template still present" in payload["reason"]


def test_hook_blocks_short_mission_reflection_row(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    mutated = canonical.replace(MISSION_FILL, "`docs/CORTEX.md` short", 1)
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "too short" in payload["reason"]


def test_hook_blocks_uncited_mission_reflection_row(tmp_path: Path) -> None:
    canonical = _fully_filled_grid()
    uncited = (
        "This is deliberately long enough to pass the minimum character threshold, "
        "but it avoids every allowed repository citation token so the hook can prove "
        "that mission reflection must be grounded in actual repo evidence."
    )
    mutated = canonical.replace(MISSION_FILL, uncited, 1)
    transcript = _write_transcript(tmp_path, mutated)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "missing repo-grounding citation" in payload["reason"]


def test_hook_blocks_when_closure_metadata_unfilled(tmp_path: Path) -> None:
    canonical = _fill_mission_reflection(_canonical_grid())
    transcript = _write_transcript(tmp_path, canonical)

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    payload = json.loads(stdout)
    assert payload["decision"] == "block"
    assert "Closure metadata" in payload["reason"]


def test_hook_allows_stop_when_all_gates_pass(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path, _fully_filled_grid())

    returncode, stdout, _ = _run_hook(_hook_input(transcript))

    assert returncode == 0
    assert stdout.strip() == ""


def test_hook_does_not_short_circuit_on_stop_hook_active(tmp_path: Path) -> None:
    transcript = _write_transcript(tmp_path, "no grid signature here")

    returncode, stdout, _ = _run_hook(_hook_input(transcript, stop_hook_active=True))

    assert returncode == 0
    assert stdout.strip() != ""
    payload = json.loads(stdout)
    assert payload["decision"] == "block"


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


def test_hook_signature_markers_match_repo_workflow_constants() -> None:
    text = HOOK_SCRIPT.read_text(encoding="utf-8")
    constants = {}
    for name in (
        "GRID_HEADER_MARKER",
        "GRID_TABLE_HEADER_MARKER",
        "GRID_TABLE_SEPARATOR_MARKER",
        "GRID_FORBIDDEN_SECTION_MARKER",
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

    labels_match = re.search(
        r"REQUIRED_GRID_ROW_LABELS: tuple\[str, \.\.\.\] = \((.*?)\)",
        text,
        re.DOTALL,
    )
    assert labels_match, "hook script missing REQUIRED_GRID_ROW_LABELS"
    hook_labels = re.findall(r'"([^"]+)"', labels_match.group(1))
    assert tuple(hook_labels) == module.REQUIRED_GRID_ROW_LABELS


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
