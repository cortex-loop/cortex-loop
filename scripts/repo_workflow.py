#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT_ENV_VAR = "CORTEX_REPO_WORKFLOW_ROOT"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MANAGED_SESSION_AGENTS = ("codex", "claude", "maint")
ALLOWED_SCOPES = ("repo", "docs", "kernel", "adapter", "pack", "eval", "tests", "build", "release")
BANNED_SUBJECT_TOKENS = ("scrubbed", "final polish", "quick fix", "temp", "wip", "public-ready")
CANONICAL_REPO_SLUG = "cortex-loop/cortex-loop"
MANAGED_SESSION_BRANCH_RE = re.compile(
    r"^(codex|claude|maint)/(?P<stamp>\d{8}-\d{6})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
CANONICAL_ORIGIN_PATTERNS = (
    re.compile(r"^git@github\.com:(?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"),
    re.compile(r"^https://github\.com/(?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"),
    re.compile(r"^ssh://git@github\.com/(?P<slug>[^/\s]+/[^/\s]+?)(?:\.git)?/?$"),
)


def _root() -> Path:
    configured = os.environ.get(ROOT_ENV_VAR)
    if configured:
        return Path(configured).resolve()
    return DEFAULT_ROOT


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=cwd or _root(), check=False, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def _capture(cmd: list[str], *, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=cwd or _root(),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout


def _capture_optional(cmd: list[str], *, cwd: Path | None = None) -> str | None:
    proc = subprocess.run(
        cmd,
        cwd=cwd or _root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _current_branch() -> str:
    return _capture(["git", "branch", "--show-current"]).strip()


def _tracked_status_lines() -> list[str]:
    output = _capture(["git", "status", "--porcelain=1", "--untracked-files=all"])
    return [line for line in output.splitlines() if line]


def _ensure_clean_tree() -> None:
    lines = _tracked_status_lines()
    if lines:
        raise SystemExit("Working tree is not clean:\n" + "\n".join(lines))


def _origin_url() -> str | None:
    return _capture_optional(["git", "remote", "get-url", "origin"])


def _repo_slug_from_remote(url: str | None) -> str | None:
    if not url:
        return None
    for pattern in CANONICAL_ORIGIN_PATTERNS:
        match = pattern.fullmatch(url.strip())
        if match is not None:
            return match.group("slug")
    return None


def _ensure_canonical_origin() -> None:
    if os.environ.get(ROOT_ENV_VAR):
        return
    origin = _origin_url()
    if origin is None:
        raise SystemExit("Remote `origin` is not configured.")
    slug = _repo_slug_from_remote(origin)
    if slug != CANONICAL_REPO_SLUG:
        raise SystemExit(
            f"Remote `origin` points at '{origin}', not the canonical repo `github.com/{CANONICAL_REPO_SLUG}`."
        )


def _fetch_origin() -> None:
    _run(["git", "fetch", "origin"])


def _origin_main_exists() -> bool:
    proc = subprocess.run(["git", "rev-parse", "--verify", "origin/main"], cwd=_root(), check=False)
    return proc.returncode == 0


def _main_upstream() -> str | None:
    return _capture_optional(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "main@{upstream}"])


def _set_main_upstream() -> None:
    _run(["git", "branch", "--set-upstream-to", "origin/main", "main"])


def _main_origin_state() -> str:
    if _main_upstream() != "origin/main":
        return "missing-upstream"
    if not _origin_main_exists():
        return "missing-upstream"
    counts = _capture(["git", "rev-list", "--left-right", "--count", "main...origin/main"]).strip()
    ahead, behind = (int(token) for token in counts.split())
    if ahead == 0 and behind == 0:
        return "synced"
    if ahead == 0:
        return "behind"
    if behind == 0:
        return "ahead"
    return "diverged"


def _sync_guidance(state: str) -> str:
    if state == "missing-upstream":
        return "Local `main` must track `origin/main` before starting a managed session. Run `python scripts/repo_workflow.py sync-main`."
    if state == "behind":
        return "Local `main` is behind `origin/main`. Run `python scripts/repo_workflow.py sync-main`."
    if state == "ahead":
        return (
            "Local `main` is ahead of `origin/main`. Publish the landed commit under a review branch or, "
            "after merge or deliberate abandonment, run `python scripts/repo_workflow.py sync-main --adopt-origin`."
        )
    if state == "diverged":
        return (
            "Local `main` diverges from `origin/main`. Reconcile the review branch or, after the merged PR is authoritative, "
            "run `python scripts/repo_workflow.py sync-main --adopt-origin`."
        )
    raise SystemExit(f"Unsupported main/origin state: {state}")


def _ensure_startable_main() -> None:
    _ensure_canonical_origin()
    _fetch_origin()
    state = _main_origin_state()
    if state != "synced":
        raise SystemExit(_sync_guidance(state))


def _normalize_slug(raw: str | None) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", (raw or "session").strip().lower()).strip("-")
    return normalized or "session"


def _session_timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _session_branch_name(agent: str, slug: str | None) -> str:
    return f"{agent}/{_session_timestamp()}-{_normalize_slug(slug)}"


def _preservation_branch_name(slug: str | None) -> str:
    return f"maint/preserved-{_session_timestamp()}-{_normalize_slug(slug)}"


def is_managed_session_branch(branch: str) -> bool:
    return MANAGED_SESSION_BRANCH_RE.fullmatch(branch.strip()) is not None


def validate_branch_name(branch: str, *, allow_main: bool = True) -> str | None:
    normalized = branch.strip()
    if not normalized:
        return "Branch name is empty."
    if allow_main and normalized == "main":
        return None
    if is_managed_session_branch(normalized):
        return None
    if normalized.startswith("review/") or normalized.startswith("maint/"):
        return None
    return f"Branch '{normalized}' is not allowed for this workflow."


def validate_finalize_branch(branch: str) -> str | None:
    error = validate_branch_name(branch, allow_main=False)
    if error is not None:
        return error
    if is_managed_session_branch(branch):
        return (
            f"Current branch '{branch}' is a managed session branch. "
            "Use close-session for managed branches and finalize only for explicit manual/review branches."
        )
    return None


def validate_commit_subject(subject: str) -> str | None:
    first_line = subject.strip().splitlines()[0].strip() if subject.strip() else ""
    if not first_line:
        return "Commit subject is empty."
    if ": " not in first_line:
        return "Commit subject must use '<scope>: <end-state summary>'."
    scope, summary = first_line.split(": ", 1)
    if scope not in ALLOWED_SCOPES:
        return f"Commit scope '{scope}' is not allowed."
    if not summary.strip():
        return "Commit summary is empty."
    lowered = first_line.lower()
    for token in BANNED_SUBJECT_TOKENS:
        if token in lowered:
            return f"Commit subject contains banned narration: '{token}'."
    return None


def _branch_merged_into_main(branch: str) -> bool:
    proc = subprocess.run(["git", "merge-base", "--is-ancestor", branch, "main"], cwd=_root(), check=False)
    return proc.returncode == 0


def _switch_to_main() -> None:
    _run(["git", "switch", "main"])


def _delete_branch(branch: str) -> None:
    _run(["git", "branch", "-d", branch])


def _run_verification_contract() -> None:
    _run(["git", "diff", "--check"])
    _run(["make", "test-smoke"])
    _run(["make", "verify"])


def _commit_has_staged_changes() -> bool:
    proc = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=_root(), check=False)
    return proc.returncode == 1


def _finalize_current_branch(message: str) -> str | None:
    _run(["git", "add", "-A"])
    if not _commit_has_staged_changes():
        _ensure_clean_tree()
        return None
    _run_verification_contract()
    _run(["git", "add", "-A"])
    if not _commit_has_staged_changes():
        _ensure_clean_tree()
        return None
    _run(["git", "commit", "-m", message])
    _ensure_clean_tree()
    return _capture(["git", "rev-parse", "HEAD"]).strip()


def _land_session_branch(branch: str) -> str:
    _switch_to_main()
    proc = subprocess.run(
        ["git", "merge", "--ff-only", branch],
        cwd=_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        _run(["git", "switch", branch])
        detail = (proc.stderr or proc.stdout).strip()
        suffix = f"\n{detail}" if detail else ""
        raise SystemExit(
            f"Unable to fast-forward main from session branch '{branch}'. "
            f"main moved since the session started; resolve the divergence manually and retry.{suffix}"
        )
    _delete_branch(branch)
    return _capture(["git", "rev-parse", "main"]).strip()


def _worktree_branch_map() -> dict[str, str]:
    output = _capture(["git", "worktree", "list", "--porcelain"])
    lines = output.splitlines()
    mapping: dict[str, str] = {}
    current_path = ""
    for line in lines:
        if line.startswith("worktree "):
            current_path = line.split(" ", 1)[1].strip()
            continue
        if line.startswith("branch refs/heads/"):
            branch = line.removeprefix("branch refs/heads/").strip()
            mapping[branch] = current_path
    return mapping


def _branch_heads() -> dict[str, str]:
    output = _capture(["git", "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"])
    mapping: dict[str, str] = {}
    for line in output.splitlines():
        branch, head = line.strip().split(" ", 1)
        mapping[branch] = head
    return mapping


def _nested_attached_worktree_paths() -> list[str]:
    root = _root()
    current_root = str(root)
    relpaths: list[str] = []
    for path in _worktree_branch_map().values():
        if not path or path == current_root:
            continue
        candidate = Path(path)
        try:
            rel = candidate.relative_to(root)
        except ValueError:
            continue
        relpaths.append(str(rel))
    return sorted(set(relpaths))


def _tracked_nested_worktree_paths() -> list[str]:
    tracked: list[str] = []
    for relpath in _nested_attached_worktree_paths():
        output = _capture_optional(["git", "ls-files", "-s", "--", relpath])
        if output:
            tracked.append(relpath)
    return tracked


def cmd_sync_main(adopt_origin: bool) -> int:
    _ensure_clean_tree()
    _ensure_canonical_origin()
    _fetch_origin()
    if not _origin_main_exists():
        raise SystemExit("Remote `origin/main` does not exist.")
    if _current_branch() != "main":
        _switch_to_main()
    if _main_upstream() != "origin/main":
        _set_main_upstream()
    state = _main_origin_state()
    if state == "synced":
        print(f"main synced {_capture(['git', 'rev-parse', 'main']).strip()}")
        return 0
    if adopt_origin:
        _run(["git", "reset", "--hard", "origin/main"])
        print(f"main adopted {_capture(['git', 'rev-parse', 'main']).strip()}")
        return 0
    if state == "behind":
        _run(["git", "merge", "--ff-only", "origin/main"])
        print(f"main fast-forwarded {_capture(['git', 'rev-parse', 'main']).strip()}")
        return 0
    raise SystemExit(_sync_guidance(state))


def cmd_start_session(agent: str, slug: str | None) -> int:
    branch = _current_branch()
    _ensure_clean_tree()
    if branch == "main":
        _ensure_startable_main()
        next_branch = _session_branch_name(agent, slug)
        _run(["git", "switch", "-c", next_branch])
        print(next_branch)
        return 0
    if is_managed_session_branch(branch) and _branch_merged_into_main(branch):
        _switch_to_main()
        _delete_branch(branch)
        _ensure_startable_main()
        next_branch = _session_branch_name(agent, slug)
        _run(["git", "switch", "-c", next_branch])
        print(next_branch)
        return 0
    raise SystemExit(
        f"Current branch '{branch}' is not clean synced main. Reconcile it manually before starting a managed session."
    )


def cmd_finalize(message: str) -> int:
    branch = _current_branch()
    error = validate_finalize_branch(branch)
    if error is not None:
        raise SystemExit(error)
    subject_error = validate_commit_subject(message)
    if subject_error is not None:
        raise SystemExit(subject_error)
    commit_hash = _finalize_current_branch(message)
    if commit_hash is None:
        print("no-op clean tree")
        return 0
    print(f"{branch} {commit_hash}")
    return 0


def cmd_close_session(message: str) -> int:
    branch = _current_branch()
    if not is_managed_session_branch(branch):
        raise SystemExit(f"Current branch '{branch}' is not a managed session branch.")
    subject_error = validate_commit_subject(message)
    if subject_error is not None:
        raise SystemExit(subject_error)
    commit_hash = _finalize_current_branch(message)
    if commit_hash is None and _branch_merged_into_main(branch):
        _switch_to_main()
        _delete_branch(branch)
        print("no-op clean tree")
        return 0
    landed_hash = _land_session_branch(branch)
    print(f"main {landed_hash}")
    return 0


def cmd_audit_branches() -> int:
    branch_heads = _branch_heads()
    current_branch = _current_branch()
    worktree_map = _worktree_branch_map()
    current_root = str(_root())
    merged_local: list[dict[str, str]] = []
    worktree_attached: list[dict[str, str]] = []
    open_manual: list[dict[str, str]] = []
    open_managed: list[dict[str, str]] = []

    for branch, head in branch_heads.items():
        if branch == "main":
            continue
        worktree_path = worktree_map.get(branch)
        info = {"branch": branch, "head": head}
        if worktree_path and worktree_path != current_root:
            worktree_attached.append({**info, "path": worktree_path})
            continue
        if _branch_merged_into_main(branch):
            merged_local.append(info)
            continue
        if is_managed_session_branch(branch):
            open_managed.append(info)
            continue
        open_manual.append(info)

    payload = {
        "current_branch": current_branch,
        "main_head": _capture_optional(["git", "rev-parse", "main"]),
        "origin_main_head": _capture_optional(["git", "rev-parse", "origin/main"]),
        "merged_local": sorted(merged_local, key=lambda row: row["branch"]),
        "worktree_attached": sorted(worktree_attached, key=lambda row: row["branch"]),
        "open_manual": sorted(open_manual, key=lambda row: row["branch"]),
        "open_managed": sorted(open_managed, key=lambda row: row["branch"]),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_preserve_worktree(slug: str | None) -> int:
    branch = _current_branch()
    if branch == "main":
        raise SystemExit("preserve-worktree refuses on clean or dirty main; use it only on dirty non-main worktrees.")
    lines = _tracked_status_lines()
    if not lines:
        raise SystemExit("preserve-worktree requires a dirty non-main worktree.")
    tracked_nested = _tracked_nested_worktree_paths()
    if tracked_nested:
        raise SystemExit(
            "preserve-worktree refuses when attached worktree paths are already tracked:\n"
            + "\n".join(tracked_nested)
        )
    target_branch = branch if branch.startswith("maint/") or branch.startswith("review/") else _preservation_branch_name(slug)
    if target_branch != branch:
        _run(["git", "switch", "-c", target_branch])
    _run(["git", "add", "-A"])
    nested_paths = _nested_attached_worktree_paths()
    if nested_paths:
        _run(["git", "reset", "-q", "HEAD", "--", *nested_paths])
    if not _commit_has_staged_changes():
        raise SystemExit("preserve-worktree found no staged changes after adding tracked and untracked work.")
    message = f"docs: preserve worktree snapshot for {_normalize_slug(slug)}"
    _run(["git", "commit", "-m", message])
    commit_hash = _capture(["git", "rev-parse", "HEAD"]).strip()
    print(json.dumps({"branch": target_branch, "commit": commit_hash}, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repo workflow helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync-main", help="Reconcile local main with origin/main.")
    sync_parser.add_argument(
        "--adopt-origin",
        action="store_true",
        help="Reset local main to origin/main after a merged PR or deliberate abandonment of local unpublished main history.",
    )

    start_parser = subparsers.add_parser("start-session", help="Create a fresh managed session branch.")
    start_parser.add_argument("--agent", choices=MANAGED_SESSION_AGENTS, required=True)
    start_parser.add_argument("--slug")

    finalize_parser = subparsers.add_parser("finalize", help="Verify and commit the current manual/review branch.")
    finalize_parser.add_argument("--message", required=True)

    close_parser = subparsers.add_parser("close-session", help="Verify, land, and delete a managed session branch.")
    close_parser.add_argument("--message", required=True)

    subparsers.add_parser("audit-branches", help="Report local branch hygiene state without mutating refs.")

    preserve_parser = subparsers.add_parser(
        "preserve-worktree",
        help="Preserve a dirty non-main worktree onto an explicit manual branch without landing it onto main.",
    )
    preserve_parser.add_argument("--slug")

    args = parser.parse_args(argv)
    if args.command == "sync-main":
        return cmd_sync_main(args.adopt_origin)
    if args.command == "start-session":
        return cmd_start_session(args.agent, args.slug)
    if args.command == "finalize":
        return cmd_finalize(args.message)
    if args.command == "close-session":
        return cmd_close_session(args.message)
    if args.command == "audit-branches":
        return cmd_audit_branches()
    if args.command == "preserve-worktree":
        return cmd_preserve_worktree(args.slug)
    raise SystemExit(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
