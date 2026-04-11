"""Repo-wide Codex App dogfood session helper."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from internal.workflow.repo_workflow import is_managed_session_branch
from lab.live_validation_common import (
    DOGFOOD_LATEST_PATH,
    DOGFOOD_SESSIONS_ROOT,
    PROMPTS_ROOT,
    REPO_ROOT,
    build_scenario_catalog,
    ensure_live_validation_dirs,
    now_utc_iso,
    read_json_file,
    relative_repo_path,
    run_command,
    write_json,
)


AGENTS_CONTRACT_PATH = REPO_ROOT / "AGENTS.md"
DOGFOOD_PROFILE_NAME = "repo_any_task"
DOGFOOD_CONTRACT_HEADING = "## Codex App Dogfood Mode"
DOGFOOD_START_TRIGGER = "start cortex dogfood mode"
DOGFOOD_REFRESH_TRIGGER = "refresh cortex dogfood mode"
DOGFOOD_STOP_TRIGGER = "stop cortex dogfood mode"
DOGFOOD_STATUS_TRIGGER = "show cortex dogfood status"
DOGFOOD_CLOSE_TRIGGER = "close cortex dogfood mode"
DOGFOOD_SIGNAL_KEYS = (
    "continuity_helped",
    "blocker_surfaced",
    "uncertainty_or_brake_used",
    "truthful_closure",
    "cortex_changed_next_action",
)
DOGFOOD_SURFACE = "codex_dogfood_session"
DOGFOOD_SCOPE = "lab"
DOGFOOD_EVIDENCE_ROLE = "watchlist"
UNSET_SIGNAL_VALUE = "unset"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.codex_dogfood_session",
        description="Manage repo-wide Codex App dogfood mode for the current worktree.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    activate_parser = subparsers.add_parser("activate")
    _add_session_args(activate_parser)

    refresh_parser = subparsers.add_parser("refresh")
    _add_session_args(refresh_parser)

    close_parser = subparsers.add_parser("close")
    close_parser.add_argument("--profile", choices=(DOGFOOD_PROFILE_NAME,), default=DOGFOOD_PROFILE_NAME)
    close_parser.add_argument("--thread-id")
    close_parser.add_argument("--handoff-summary")
    close_parser.add_argument("--verification-summary")
    close_parser.add_argument("--note")
    close_parser.add_argument("--abort", action="store_true")
    for key in DOGFOOD_SIGNAL_KEYS:
        close_parser.add_argument(f"--{key.replace('_', '-')}", choices=("yes", "no"))

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--profile", choices=(DOGFOOD_PROFILE_NAME,), default=DOGFOOD_PROFILE_NAME)

    args = parser.parse_args(argv)

    if args.command == "activate":
        result = activate_session(
            profile_name=args.profile,
            trigger_phrase=DOGFOOD_START_TRIGGER,
            task_summary=args.task_summary,
            thread_id=args.thread_id,
        )
        print(result["message"])
        return 0 if result["ok"] else 2

    if args.command == "refresh":
        result = refresh_session(
            profile_name=args.profile,
            trigger_phrase=DOGFOOD_REFRESH_TRIGGER,
            task_summary=args.task_summary,
            thread_id=args.thread_id,
        )
        print(result["message"])
        return 0 if result["ok"] else 2

    if args.command == "close":
        result = close_session(
            profile_name=args.profile,
            trigger_phrase=DOGFOOD_STOP_TRIGGER if args.abort else DOGFOOD_CLOSE_TRIGGER,
            thread_id=args.thread_id,
            handoff_summary=args.handoff_summary,
            verification_summary=args.verification_summary,
            note=args.note,
            dogfood_signal=_cli_dogfood_signal(args),
            abort=args.abort,
        )
        print(result["message"])
        return 0 if result["ok"] else 2

    result = status_session(profile_name=args.profile)
    print(result["message"])
    return 0 if result["ok"] else 2


def activate_session(
    *,
    profile_name: str = DOGFOOD_PROFILE_NAME,
    trigger_phrase: str = DOGFOOD_START_TRIGGER,
    task_summary: str | None = None,
    thread_id: str | None = None,
) -> dict[str, Any]:
    ensure_live_validation_dirs()
    profile = _load_profile(profile_name)
    repo_state = _repo_state()
    refusal = _activation_refusal(repo_state, profile)
    if refusal is not None:
        return refusal

    contract_payload = _contract_payload(profile_name)
    contract_revision_hash = compute_contract_revision_hash(contract_payload)
    activated_at = now_utc_iso()
    dogfood_id = _new_dogfood_id()
    activation_baseline = _activation_baseline(repo_state)
    artifact = {
        "dogfood_id": dogfood_id,
        "profile_name": profile_name,
        "surface": DOGFOOD_SURFACE,
        "scope": DOGFOOD_SCOPE,
        "evidence_role": DOGFOOD_EVIDENCE_ROLE,
        "mode_status": "active",
        "activated_at": activated_at,
        "last_refreshed_at": None,
        "closed_at": None,
        "repo_root": str(REPO_ROOT),
        "branch": repo_state["branch"],
        "head_commit": repo_state["head_commit"],
        "worktree_dirty": repo_state["worktree_dirty"],
        "workflow_mode": profile["workflow_mode"],
        "managed_session_branch": True,
        "contract_revision_hash": contract_revision_hash,
        "contract_source": "current_worktree",
        "trigger_phrase": trigger_phrase,
        "trigger_history": [
            {
                "trigger_phrase": trigger_phrase,
                "recorded_at": activated_at,
            }
        ],
        "task_summary": _resolved_task_summary(task_summary, repo_state["branch"]),
        "thread_id": thread_id,
        "activation_baseline": activation_baseline,
        "dogfood_signal": _empty_dogfood_signal(),
        "handoff_summary": None,
        "verification_summary": None,
        "changed_files": [],
        "end_commit": None,
        "returned_to_main": None,
        "prompt_profile_paths": contract_payload["prompt_profile_paths"],
        "artifact_path": relative_repo_path(_session_path(dogfood_id)),
        "contract_revision_history": [
            _revision_entry(
                contract_revision_hash=contract_revision_hash,
                repo_state=repo_state,
                recorded_at=activated_at,
            )
        ],
    }
    _write_session_artifact(artifact)
    return {
        "ok": True,
        "artifact": artifact,
        "message": render_dogfood_contract(artifact, contract_payload),
    }


def refresh_session(
    *,
    profile_name: str = DOGFOOD_PROFILE_NAME,
    trigger_phrase: str = DOGFOOD_REFRESH_TRIGGER,
    task_summary: str | None = None,
    thread_id: str | None = None,
) -> dict[str, Any]:
    ensure_live_validation_dirs()
    artifact = _load_active_session()
    if artifact is None:
        return _inactive_session_result(
            reason="no_active_session",
            message=(
                "No active dogfood session exists. Run "
                "`python3 -m lab.codex_dogfood_session activate` on a managed "
                "`codex/...` branch first."
            ),
        )

    profile = _load_profile(profile_name)
    repo_state = _repo_state()
    refusal = _activation_refusal(repo_state, profile)
    if refusal is not None:
        return refusal

    contract_payload = _contract_payload(profile_name)
    refreshed_at = now_utc_iso()
    contract_revision_hash = compute_contract_revision_hash(contract_payload)
    artifact["mode_status"] = "refreshed"
    artifact["last_refreshed_at"] = refreshed_at
    artifact["contract_revision_hash"] = contract_revision_hash
    artifact["trigger_phrase"] = trigger_phrase
    artifact["trigger_history"].append(
        {
            "trigger_phrase": trigger_phrase,
            "recorded_at": refreshed_at,
        }
    )
    artifact["task_summary"] = _resolved_task_summary(task_summary, repo_state["branch"], artifact["task_summary"])
    if thread_id is not None:
        artifact["thread_id"] = thread_id
    artifact["prompt_profile_paths"] = contract_payload["prompt_profile_paths"]
    artifact["contract_revision_history"].append(
        _revision_entry(
            contract_revision_hash=contract_revision_hash,
            repo_state=repo_state,
            recorded_at=refreshed_at,
        )
    )
    _write_session_artifact(artifact)
    return {
        "ok": True,
        "artifact": artifact,
        "message": render_dogfood_contract(artifact, contract_payload),
    }


def close_session(
    *,
    profile_name: str = DOGFOOD_PROFILE_NAME,
    trigger_phrase: str = DOGFOOD_CLOSE_TRIGGER,
    thread_id: str | None = None,
    handoff_summary: str | None = None,
    verification_summary: str | None = None,
    note: str | None = None,
    dogfood_signal: dict[str, str | None] | None = None,
    abort: bool = False,
) -> dict[str, Any]:
    ensure_live_validation_dirs()
    artifact = _load_active_session()
    if artifact is None:
        return _inactive_session_result(
            reason="no_active_session",
            message="No active dogfood session exists to close.",
        )

    _load_profile(profile_name)
    repo_state = _repo_state()
    closeout_supplied = _closeout_block_supplied(
        handoff_summary=handoff_summary,
        verification_summary=verification_summary,
        dogfood_signal=dogfood_signal,
        note=note,
    )
    closed_at = now_utc_iso()
    artifact["mode_status"] = "aborted" if abort else "closed"
    artifact["closed_at"] = closed_at
    artifact["trigger_phrase"] = trigger_phrase
    artifact["trigger_history"].append(
        {
            "trigger_phrase": trigger_phrase,
            "recorded_at": closed_at,
        }
    )
    if thread_id is not None:
        artifact["thread_id"] = thread_id
    if handoff_summary is not None:
        artifact["handoff_summary"] = handoff_summary
    if verification_summary is not None:
        artifact["verification_summary"] = verification_summary
    artifact["dogfood_signal"] = _merged_dogfood_signal(
        artifact.get("dogfood_signal"),
        dogfood_signal=dogfood_signal,
        note=note,
    )
    artifact["changed_files"] = _collect_session_changed_files(artifact)
    artifact["end_commit"] = repo_state["head_commit"]
    artifact["returned_to_main"] = repo_state["branch"] == "main"
    _write_session_artifact(artifact)
    return {
        "ok": True,
        "artifact": artifact,
        "message": render_close_result(
            artifact,
            include_signal_block=not abort or closeout_supplied,
        ),
    }


def status_session(
    *,
    profile_name: str = DOGFOOD_PROFILE_NAME,
) -> dict[str, Any]:
    ensure_live_validation_dirs()
    artifact = read_json_file(DOGFOOD_LATEST_PATH)
    if not artifact:
        return _inactive_session_result(
            reason="inactive",
            message="Dogfood mode is inactive. No local session artifact is present.",
        )

    contract_payload = _contract_payload(profile_name)
    current_worktree_hash = compute_contract_revision_hash(contract_payload)
    refresh_required = current_worktree_hash != artifact.get("contract_revision_hash")
    repo_state = _repo_state()
    return {
        "ok": True,
        "artifact": artifact,
        "current_worktree_contract_revision_hash": current_worktree_hash,
        "refresh_required": refresh_required,
        "message": render_status_result(
            artifact=artifact,
            current_worktree_hash=current_worktree_hash,
            refresh_required=refresh_required,
            repo_state=repo_state,
        ),
    }


def compute_contract_revision_hash(contract_payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(
        json.dumps(
            {
                "agents_dogfood_contract": contract_payload["agents_dogfood_contract"],
                "profile": contract_payload["profile"],
                "session_start_prompt": contract_payload["session_start_prompt"]["text"],
                "closeout_prompt": contract_payload["closeout_prompt"]["text"],
            },
            sort_keys=True,
        ).encode("utf-8")
    )
    return digest.hexdigest()


def render_dogfood_contract(artifact: dict[str, Any], contract_payload: dict[str, Any]) -> str:
    prompt_paths = artifact["prompt_profile_paths"]
    profile = contract_payload["profile"]
    activation_baseline = artifact["activation_baseline"]
    return "\n".join(
        [
            (
                f"dogfood mode {artifact['mode_status']}: `{artifact['dogfood_id']}` on "
                f"`{artifact['branch']}` at `{artifact['head_commit']}`."
            ),
            "evidence: `current_worktree` lab/watchlist only; not product truth",
            f"contract revision: `{artifact['contract_revision_hash']}` from `current_worktree`",
            f"task summary: `{artifact['task_summary']}`",
            (
                "activation baseline: "
                f"`dirty={activation_baseline['worktree_dirty']}`; initial dirty files: "
                f"`{', '.join(activation_baseline['dirty_files']) or 'none'}`"
            ),
            (
                "workflow remains unchanged: "
                f"`{profile['sync_main_command']}` then `{profile['start_session_command']}` when a new managed session is needed."
            ),
            f"close-session command: `{profile['close_session_command']}`",
            (
                "prompt profiles: "
                f"`{prompt_paths['session_start']}`, `{prompt_paths['closeout']}`"
            ),
            f"artifact: `{artifact['artifact_path']}`",
            "Do not rerun `make live-codex-dogfood` unless the user explicitly asks.",
            "",
            "Adopt this contract for the current Codex App chat/session only:",
            "",
            contract_payload["session_start_prompt"]["text"].rstrip(),
            "",
            "Closeout contract:",
            "",
            contract_payload["closeout_prompt"]["text"].rstrip(),
        ]
    )


def render_close_result(
    artifact: dict[str, Any],
    *,
    include_signal_block: bool,
) -> str:
    signal = artifact["dogfood_signal"]
    activation_baseline = artifact.get("activation_baseline", {})
    lines = [
        (
            f"dogfood mode {artifact['mode_status']}: `{artifact['dogfood_id']}` "
            f"recorded at `{artifact['artifact_path']}`."
        ),
        "evidence: `current_worktree` lab/watchlist only; not product truth",
        (
            "activation baseline: "
            f"`dirty={activation_baseline.get('worktree_dirty', False)}`; initial dirty files: "
            f"`{', '.join(activation_baseline.get('dirty_files', [])) or 'none'}`"
        ),
        f"end commit: `{artifact['end_commit'] or 'none'}`; returned to main: `{artifact['returned_to_main']}`",
        (
            "changed files beyond activation baseline: "
            f"`{', '.join(artifact['changed_files']) or 'none'}`"
        ),
    ]
    if artifact.get("handoff_summary"):
        lines.append(f"handoff summary: `{artifact['handoff_summary']}`")
    if artifact.get("verification_summary"):
        lines.append(f"verification summary: `{artifact['verification_summary']}`")
    if include_signal_block:
        lines.extend(["", _render_dogfood_signal_block(signal)])
    return "\n".join(lines)


def render_status_result(
    *,
    artifact: dict[str, Any],
    current_worktree_hash: str,
    refresh_required: bool,
    repo_state: dict[str, Any],
) -> str:
    refresh_state = "required" if refresh_required else "not required"
    activation_baseline = artifact.get("activation_baseline", {})
    return "\n".join(
        [
            (
                f"dogfood status: `{artifact['mode_status']}` for `{artifact['dogfood_id']}` "
                f"on activation branch `{artifact['branch']}`."
            ),
            "evidence: `current_worktree` lab/watchlist only; not product truth",
            f"current branch: `{repo_state['branch']}`; current head: `{repo_state['head_commit']}`",
            (
                "activation baseline: "
                f"`dirty={activation_baseline.get('worktree_dirty', False)}`; initial dirty files: "
                f"`{', '.join(activation_baseline.get('dirty_files', [])) or 'none'}`"
            ),
            f"recorded contract: `{artifact['contract_revision_hash']}`; current worktree contract: `{current_worktree_hash}`",
            f"refresh: `{refresh_state}`",
            f"artifact: `{artifact['artifact_path']}`",
        ]
    )


def _add_session_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", choices=(DOGFOOD_PROFILE_NAME,), default=DOGFOOD_PROFILE_NAME)
    parser.add_argument("--task-summary")
    parser.add_argument("--thread-id")


def _load_profile(profile_name: str) -> dict[str, Any]:
    catalog = build_scenario_catalog()
    profile = catalog.get("codex_dogfood_profiles", {}).get(profile_name)
    if not isinstance(profile, dict):
        raise ValueError(f"Unsupported dogfood profile: {profile_name}")
    return dict(profile)


def _contract_payload(profile_name: str) -> dict[str, Any]:
    profile = _load_profile(profile_name)
    session_start_path = PROMPTS_ROOT / profile["session_start_prompt"]
    closeout_path = PROMPTS_ROOT / profile["closeout_prompt"]
    return {
        "profile": profile,
        "agents_dogfood_contract": _read_agents_dogfood_contract(),
        "session_start_prompt": {
            "path": relative_repo_path(session_start_path),
            "text": session_start_path.read_text(encoding="utf-8"),
        },
        "closeout_prompt": {
            "path": relative_repo_path(closeout_path),
            "text": closeout_path.read_text(encoding="utf-8"),
        },
        "prompt_profile_paths": {
            "session_start": relative_repo_path(session_start_path),
            "closeout": relative_repo_path(closeout_path),
        },
    }


def _read_agents_dogfood_contract() -> str:
    return _extract_level_2_section(
        AGENTS_CONTRACT_PATH.read_text(encoding="utf-8"),
        DOGFOOD_CONTRACT_HEADING,
    )


def _extract_level_2_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start_index = index
            break
    if start_index is None:
        raise ValueError(f"Missing required AGENTS contract heading: {heading}")

    collected: list[str] = []
    for line in lines[start_index:]:
        if collected and line.startswith("## "):
            break
        collected.append(line.rstrip())
    return "\n".join(collected).strip()


def _activation_refusal(repo_state: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any] | None:
    branch = repo_state["branch"]
    worktree_dirty = repo_state["worktree_dirty"]
    if is_managed_session_branch(branch):
        return None
    if branch == "main" and not worktree_dirty:
        return _inactive_session_result(
            reason="needs_managed_session_branch",
            message=(
                "Dogfood mode activates only on a managed `codex/...` branch. "
                f"Current repo state is clean `main`. Run `{profile['sync_main_command']}` "
                f"then `{profile['start_session_command']}`."
            ),
        )
    return _inactive_session_result(
        reason="reconcile_repo_state",
        message=(
            "Dogfood mode refused on the current repo state. Reconcile the worktree "
            "and continue from a managed `codex/...` session branch before activating it."
        ),
    )


def _repo_state() -> dict[str, Any]:
    status = run_command(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=REPO_ROOT,
        timeout_seconds=30.0,
    )
    branch = run_command(
        ["git", "branch", "--show-current"],
        cwd=REPO_ROOT,
        timeout_seconds=30.0,
    )
    head_commit = run_command(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        timeout_seconds=30.0,
    )
    status_lines = [line for line in status["stdout"].splitlines() if line.strip()]
    return {
        "branch": branch["stdout"].strip(),
        "head_commit": head_commit["stdout"].strip(),
        "worktree_dirty": bool(status_lines),
        "status_lines": status_lines,
        "dirty_files": _dirty_files_from_status_lines(status_lines),
    }


def _new_dogfood_id() -> str:
    return f"dogfood-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"


def _resolved_task_summary(
    task_summary: str | None,
    branch: str,
    current: str | None = None,
) -> str:
    if task_summary is not None and task_summary.strip():
        return task_summary.strip()
    if current is not None and current.strip():
        return current.strip()
    if not is_managed_session_branch(branch):
        return "current repo work"
    _, _, suffix = branch.partition("/")
    normalized = suffix
    if len(suffix) > 16 and suffix[8] == "-" and suffix[15] == "-":
        normalized = suffix[16:]
    return normalized or "current repo work"


def _empty_dogfood_signal() -> dict[str, str | None]:
    signal = {key: None for key in DOGFOOD_SIGNAL_KEYS}
    signal["note"] = None
    return signal


def _merged_dogfood_signal(
    existing: Any,
    *,
    dogfood_signal: dict[str, str | None] | None,
    note: str | None,
) -> dict[str, str | None]:
    merged = _empty_dogfood_signal()
    if isinstance(existing, dict):
        for key in (*DOGFOOD_SIGNAL_KEYS, "note"):
            value = existing.get(key)
            if value in {"yes", "no"} or (key == "note" and isinstance(value, str)):
                merged[key] = value
    if isinstance(dogfood_signal, dict):
        for key in DOGFOOD_SIGNAL_KEYS:
            value = dogfood_signal.get(key)
            if value in {"yes", "no"}:
                merged[key] = value
    if note is not None:
        merged["note"] = note
    return merged


def _closeout_block_supplied(
    *,
    handoff_summary: str | None,
    verification_summary: str | None,
    dogfood_signal: dict[str, str | None] | None,
    note: str | None,
) -> bool:
    if handoff_summary or verification_summary or note:
        return True
    if not isinstance(dogfood_signal, dict):
        return False
    return any(dogfood_signal.get(key) in {"yes", "no"} for key in DOGFOOD_SIGNAL_KEYS)


def _revision_entry(
    *,
    contract_revision_hash: str,
    repo_state: dict[str, Any],
    recorded_at: str,
) -> dict[str, Any]:
    return {
        "contract_revision_hash": contract_revision_hash,
        "recorded_at": recorded_at,
        "branch": repo_state["branch"],
        "head_commit": repo_state["head_commit"],
        "worktree_dirty": repo_state["worktree_dirty"],
    }


def _session_path(dogfood_id: str) -> Path:
    return DOGFOOD_SESSIONS_ROOT / f"{dogfood_id}.json"


def _write_session_artifact(artifact: dict[str, Any]) -> None:
    write_json(_session_path(artifact["dogfood_id"]), artifact)
    write_json(DOGFOOD_LATEST_PATH, artifact)


def _load_active_session() -> dict[str, Any] | None:
    artifact = read_json_file(DOGFOOD_LATEST_PATH)
    if not artifact:
        return None
    if artifact.get("mode_status") not in {"active", "refreshed"}:
        return None
    dogfood_id = artifact.get("dogfood_id")
    if not isinstance(dogfood_id, str) or not dogfood_id:
        return None
    session_artifact = read_json_file(_session_path(dogfood_id))
    if not session_artifact:
        return None
    return session_artifact


def _collect_session_changed_files(artifact: dict[str, Any]) -> list[str]:
    activation_baseline = artifact.get("activation_baseline", {})
    baseline_dirty = {
        path
        for path in activation_baseline.get("dirty_files", [])
        if isinstance(path, str) and path
    }
    current_paths = _collect_current_changed_paths(str(artifact.get("head_commit", "")))
    return sorted(current_paths - baseline_dirty)


def _collect_current_changed_paths(start_head_commit: str) -> set[str]:
    changed: set[str] = set()
    if start_head_commit:
        between = run_command(
            ["git", "diff", "--name-only", f"{start_head_commit}..HEAD"],
            cwd=REPO_ROOT,
            timeout_seconds=30.0,
        )
        changed.update(_nonempty_lines(between["stdout"]))

    worktree = run_command(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        timeout_seconds=30.0,
    )
    changed.update(_nonempty_lines(worktree["stdout"]))

    untracked = run_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        timeout_seconds=30.0,
    )
    changed.update(_nonempty_lines(untracked["stdout"]))
    return changed


def _activation_baseline(repo_state: dict[str, Any]) -> dict[str, Any]:
    status_lines = [
        line
        for line in repo_state.get("status_lines", [])
        if isinstance(line, str) and line.strip()
    ]
    dirty_files = repo_state.get("dirty_files")
    if not isinstance(dirty_files, list):
        dirty_files = _dirty_files_from_status_lines(status_lines)
    return {
        "branch": repo_state["branch"],
        "head_commit": repo_state["head_commit"],
        "worktree_dirty": bool(repo_state.get("worktree_dirty")),
        "status_lines": status_lines,
        "dirty_files": [
            path
            for path in dirty_files
            if isinstance(path, str) and path
        ],
    }


def _dirty_files_from_status_lines(status_lines: list[str]) -> list[str]:
    dirty_files: set[str] = set()
    for line in status_lines:
        if not isinstance(line, str):
            continue
        raw_line = line.rstrip("\n")
        if len(raw_line) < 4:
            continue
        path = raw_line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            dirty_files.add(path)
    return sorted(dirty_files)


def _render_dogfood_signal_block(signal: dict[str, Any]) -> str:
    return "\n".join(
        [
            "DOGFOOD_SIGNAL",
            f"continuity_helped: {signal.get('continuity_helped') or UNSET_SIGNAL_VALUE}",
            f"blocker_surfaced: {signal.get('blocker_surfaced') or UNSET_SIGNAL_VALUE}",
            f"uncertainty_or_brake_used: {signal.get('uncertainty_or_brake_used') or UNSET_SIGNAL_VALUE}",
            f"truthful_closure: {signal.get('truthful_closure') or UNSET_SIGNAL_VALUE}",
            f"cortex_changed_next_action: {signal.get('cortex_changed_next_action') or UNSET_SIGNAL_VALUE}",
            f"note: {signal.get('note') or UNSET_SIGNAL_VALUE}",
        ]
    )


def _nonempty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _inactive_session_result(*, reason: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "reason": reason,
        "message": message,
    }


def _cli_dogfood_signal(args: argparse.Namespace) -> dict[str, str | None]:
    return {
        key: getattr(args, key)
        for key in DOGFOOD_SIGNAL_KEYS
    }


if __name__ == "__main__":
    raise SystemExit(main())
