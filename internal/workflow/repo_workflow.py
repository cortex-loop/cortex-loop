#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_ENV_VAR = "CORTEX_REPO_WORKFLOW_ROOT"
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
if str(DEFAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(DEFAULT_ROOT))

from internal.closeout import contract as closeout_contract

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
ALWAYS_VERIFICATION_COMMANDS: tuple[tuple[str, ...], ...] = (("git", "diff", "--check"),)
VERIFICATION_SCOPE_ORDER = ("product", "conformance", "experimental", "internal", "lab")
VERIFICATION_SCOPE_COMMANDS: dict[str, tuple[tuple[str, ...], ...]] = {
    "product": (("make", "product-test"),),
    "conformance": (("make", "conformance-test"),),
    "experimental": (("make", "experimental-test"),),
    "internal": (
        ("python3", "internal/truth/generate_status.py", "--check"),
        ("python3", "internal/archive/generate_archive_index.py", "--check"),
        ("make", "-C", "internal", "test"),
    ),
    "lab": (("make", "lab-test"),),
}
SAFE_INTERNAL_PATHS = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/README.md",
    "docs/CORTEX.md",
    "docs/CORTEX_V2_CORE_2.md",
    "docs/CORTEX_V2_SRE_2.md",
    "docs/CORTEX_V2_AUX_2.md",
    "docs/CORTEX_STATUS.md",
    "internal/truth/cortex_status.json",
    "scripts/repo_workflow.py",
}
FULL_BUNDLE_FALLBACK_PATHS = {
    "Makefile",
    "pyproject.toml",
}


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


def _command_text(command: tuple[str, ...]) -> str:
    return " ".join(command)


def _current_branch() -> str:
    return _capture(["git", "branch", "--show-current"]).strip()


def _tracked_status_lines() -> list[str]:
    output = _capture(["git", "status", "--porcelain=1", "--untracked-files=all"])
    return [line for line in output.splitlines() if line]


def _changed_paths_between(base_ref: str, head_ref: str) -> list[str]:
    output = _capture_optional(["git", "diff", "--name-only", f"{base_ref}..{head_ref}"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _staged_paths() -> list[str]:
    output = _capture_optional(["git", "diff", "--cached", "--name-only"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def _normalize_paths(paths: list[str]) -> list[str]:
    return sorted({path.strip() for path in paths if path.strip()})


def _ensure_clean_tree() -> None:
    lines = _tracked_status_lines()
    if lines:
        raise SystemExit("Working tree is not clean:\n" + "\n".join(lines))


def _ensure_clean_tree_after_verification() -> None:
    lines = _tracked_status_lines()
    if lines:
        raise SystemExit(
            "verification changed tracked paths after closeout contract validation:\n" + "\n".join(lines)
        )


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


def _publication_repo_slug() -> str:
    slug = _repo_slug_from_remote(_origin_url())
    if slug is not None:
        return slug
    if os.environ.get(ROOT_ENV_VAR):
        return CANONICAL_REPO_SLUG
    raise SystemExit("Unable to determine repo slug from remote `origin`.")


def _managed_publication_allowed() -> bool:
    return _repo_slug_from_remote(_origin_url()) == CANONICAL_REPO_SLUG


def _gh_executable() -> str:
    gh = shutil.which("gh")
    if gh is None:
        raise SystemExit("GitHub CLI `gh` is required for managed close-session publication.")
    return gh


def _gh_run(args: list[str], *, capture: bool = False) -> str:
    proc = subprocess.run(
        [_gh_executable(), *args],
        cwd=_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        suffix = f"\n{detail}" if detail else ""
        raise SystemExit(f"`gh {' '.join(args)}` failed.{suffix}")
    if capture:
        return proc.stdout.strip()
    return ""


def _ensure_gh_ready() -> None:
    _gh_executable()
    proc = subprocess.run(
        ["gh", "auth", "status"],
        cwd=_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        suffix = f"\n{detail}" if detail else ""
        raise SystemExit(f"GitHub CLI `gh` must be authenticated for managed close-session publication.{suffix}")


def _fetch_origin(*, quiet: bool = False) -> None:
    cmd = ["git", "fetch", "origin"]
    if quiet:
        subprocess.run(cmd, cwd=_root(), check=True, capture_output=True, text=True)
        return
    _run(cmd)


def _origin_main_exists() -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "origin/main"],
        cwd=_root(),
        check=False,
        capture_output=True,
        text=True,
    )
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
        return "Local `main` must track `origin/main` before starting a managed session. Run `python internal/workflow/repo_workflow.py sync-main`."
    if state == "behind":
        return "Local `main` is behind `origin/main`. Run `python internal/workflow/repo_workflow.py sync-main`."
    if state == "ahead":
        return (
            "Local `main` is ahead of `origin/main`. Publish the landed commit under a review branch or, "
            "after merge or deliberate abandonment, run `python internal/workflow/repo_workflow.py sync-main --adopt-origin`."
        )
    if state == "diverged":
        return (
            "Local `main` diverges from `origin/main`. Reconcile the review branch or, after the merged PR is authoritative, "
            "run `python internal/workflow/repo_workflow.py sync-main --adopt-origin`."
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


def _branch_merged_into_origin_main(branch: str) -> bool:
    """Return True iff `branch` is an ancestor of `origin/main`.

    The honest "merged" definition for branch-hygiene gating: a branch is
    merged when its tip is reachable from `origin/main` (i.e. its work is
    actually shipped on origin), not merely when it is an ancestor of the
    local `main` (which may be ahead of origin in unpublished local
    history). This makes `start-session` refuse new sessions while a
    pushed-but-unmerged branch with an open PR still represents in-flight
    work.
    """
    proc = subprocess.run(
        ["git", "merge-base", "--is-ancestor", branch, "origin/main"],
        cwd=_root(),
        check=False,
    )
    return proc.returncode == 0


def _list_unmerged_managed_branches() -> list[str]:
    """Local managed session branches whose tip is not on origin/main.

    A managed session branch matches `MANAGED_SESSION_BRANCH_RE`. The branch
    is considered unmerged when it is not an ancestor of `origin/main`;
    branches whose work is fully shipped on origin do not appear here.

    The current branch is included if applicable; callers that want to
    exclude themselves must filter by current branch.
    """
    return [
        branch
        for branch in _branch_heads()
        if is_managed_session_branch(branch)
        and not _branch_merged_into_origin_main(branch)
    ]


def _find_managed_branches_by_slug(slug: str) -> list[str]:
    """Local managed session branches whose name ends with `-<slug>`.

    Used by `resume-session` to disambiguate; the branch name format is
    `<agent>/<timestamp>-<slug>`, so anchoring at end-of-name on
    `-<slug>` matches all sessions with the same slug regardless of
    timestamp.
    """
    if not slug.strip():
        return []
    suffix = f"-{slug.strip()}"
    return sorted(
        branch
        for branch in _branch_heads()
        if is_managed_session_branch(branch) and branch.endswith(suffix)
    )


def _branch_merged_into_origin_main(branch: str) -> bool:
    proc = subprocess.run(["git", "merge-base", "--is-ancestor", branch, "origin/main"], cwd=_root(), check=False)
    return proc.returncode == 0


def _branch_has_unique_commits(branch: str, base_ref: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-list", "--count", f"{base_ref}..{branch}"],
        cwd=_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        suffix = f"\n{detail}" if detail else ""
        raise SystemExit(f"Unable to compare branch '{branch}' against '{base_ref}'.{suffix}")
    return int(proc.stdout.strip() or "0") > 0


def _verification_scopes_for_path(path: str) -> set[str] | None:
    normalized = path.strip()
    if not normalized:
        return set()
    if normalized in FULL_BUNDLE_FALLBACK_PATHS:
        return None
    if normalized in SAFE_INTERNAL_PATHS:
        return {"internal"}
    if normalized in {"docs/archive/README.md", "internal/archive/manifest.json"}:
        return {"internal"}
    if normalized.startswith(("internal/", "docs/internal/", "tests/internal/")):
        return {"internal"}
    if normalized.startswith(("docs/archive/", "tests/archive/")):
        return {"internal"}
    if normalized.startswith(("lab/", "tools/", "tests/lab/", "tests/fixtures/")):
        return {"lab"}
    if normalized.startswith(("experimental/", "tests/experimental/")):
        return {"experimental"}
    if normalized.startswith(("cortex/core/", "cortex/drivers/", "cortex/runtime/")):
        return {"product", "conformance"}
    if normalized.startswith("cortex/sre/"):
        return {"product", "experimental"}
    if normalized.startswith("cortex/hosts/openai/"):
        return {"product"}
    if normalized.startswith(("cortex/hosts/claude/", "cortex/hosts/gemini/", "cortex/hosts/reference/")):
        return {"conformance"}
    if normalized.startswith("tests/product/"):
        return {"product"}
    if normalized.startswith("tests/conformance/"):
        return {"conformance"}
    if normalized.startswith("docs/"):
        return {"internal"}
    if normalized.startswith("scripts/"):
        return None
    return None


def _verification_scopes_for_paths(paths: list[str]) -> tuple[str, ...]:
    scopes: set[str] = set()
    for path in paths:
        classified = _verification_scopes_for_path(path)
        if classified is None:
            return VERIFICATION_SCOPE_ORDER
        scopes.update(classified)
    if not scopes:
        return ("internal",)
    return tuple(scope for scope in VERIFICATION_SCOPE_ORDER if scope in scopes)


def _verification_commands_for_paths(paths: list[str]) -> tuple[tuple[str, ...], ...]:
    scopes = _verification_scopes_for_paths(paths)
    commands = list(ALWAYS_VERIFICATION_COMMANDS)
    for scope in scopes:
        commands.extend(VERIFICATION_SCOPE_COMMANDS[scope])
    return tuple(commands)


def _switch_to_main() -> None:
    _run(["git", "switch", "main"])


def _delete_branch(branch: str) -> None:
    _run(["git", "branch", "-d", branch])


def _run_verification_contract() -> None:
    for command in _verification_commands_for_paths(["Makefile"]):
        _run(list(command))


def _run_verification_for_paths(paths: list[str]) -> tuple[str, ...]:
    commands = _verification_commands_for_paths(paths)
    for command in commands:
        _run(list(command))
    return tuple(_command_text(command) for command in commands)


def _commit_has_staged_changes() -> bool:
    proc = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=_root(), check=False)
    return proc.returncode == 1


def _validate_closeout_contract_for_paths(mode: str, branch: str, reviewed_paths: list[str]) -> None:
    closeout_contract.validate_contract(
        root=_root(),
        mode=mode,
        branch=branch,
        reviewed_paths=reviewed_paths,
    )


def _revalidate_closeout_contract_after_verification(
    mode: str,
    branch: str,
    reviewed_paths: list[str],
    current_reviewed_paths: list[str],
) -> None:
    expected = _normalize_paths(reviewed_paths)
    current = _normalize_paths(current_reviewed_paths)
    if current != expected:
        raise SystemExit(
            "verification changed tracked paths after closeout contract validation:\n"
            f"reviewed_paths drifted during verification: expected {expected}, found {current}."
        )
    _validate_closeout_contract_for_paths(mode, branch, current_reviewed_paths)


def _finalize_current_branch(message: str, *, mode: str, branch: str) -> tuple[str | None, tuple[str, ...]]:
    _run(["git", "add", "-A"])
    if not _commit_has_staged_changes():
        _ensure_clean_tree()
        return None, ()
    reviewed_paths = _staged_paths()
    _validate_closeout_contract_for_paths(mode, branch, reviewed_paths)
    verification_commands = _run_verification_for_paths(reviewed_paths)
    _run(["git", "add", "-A"])
    _revalidate_closeout_contract_after_verification(mode, branch, reviewed_paths, _staged_paths())
    if not _commit_has_staged_changes():
        _ensure_clean_tree()
        return None, verification_commands
    _run(["git", "commit", "-m", message])
    _ensure_clean_tree()
    return _capture(["git", "rev-parse", "HEAD"]).strip(), verification_commands


def _managed_pr_body(branch: str, verification_commands: tuple[str, ...]) -> str:
    verification = "\n".join(f"- `{command}`" for command in verification_commands)
    return (
        "## Summary\n"
        f"- Managed session closeout for `{branch}`.\n\n"
        "## Verification\n"
        f"{verification}\n"
    )


def _session_pull_request(branch: str) -> dict[str, object] | None:
    output = _gh_run(
        [
            "pr",
            "list",
            "--repo",
            _publication_repo_slug(),
            "--head",
            branch,
            "--state",
            "all",
            "--json",
            "number,state,url,isDraft,headRefName,baseRefName",
        ],
        capture=True,
    )
    rows = json.loads(output or "[]")
    matches = [row for row in rows if row["headRefName"] == branch and row["baseRefName"] == "main"]
    if len(matches) > 1:
        raise SystemExit(f"Multiple pull requests exist for managed branch '{branch}'. Reconcile them manually.")
    return matches[0] if matches else None


def _push_session_branch(branch: str) -> None:
    _run(["git", "push", "-u", "origin", branch])


def _create_session_pull_request(branch: str, title: str, verification_commands: tuple[str, ...]) -> dict[str, object]:
    _gh_run(
        [
            "pr",
            "create",
            "--repo",
            _publication_repo_slug(),
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            title,
            "--body",
            _managed_pr_body(branch, verification_commands),
        ]
    )
    pr = _session_pull_request(branch)
    if pr is None:
        raise SystemExit(f"Managed close-session created no discoverable PR for branch '{branch}'.")
    return pr


def _mark_pull_request_ready(number: int) -> None:
    _gh_run(["pr", "ready", str(number), "--repo", _publication_repo_slug()])


def _merge_session_pull_request(number: int) -> None:
    _gh_run(["pr", "merge", str(number), "--repo", _publication_repo_slug(), "--merge", "--delete-branch"])


def _adopt_origin_main(*, require_canonical: bool = True) -> str:
    _ensure_clean_tree()
    if require_canonical:
        _ensure_canonical_origin()
    _fetch_origin()
    if not _origin_main_exists():
        raise SystemExit("Remote `origin/main` does not exist.")
    if _current_branch() != "main":
        _switch_to_main()
    if _main_upstream() != "origin/main":
        _set_main_upstream()
    _run(["git", "reset", "--hard", "origin/main"])
    return _capture(["git", "rev-parse", "main"]).strip()


def _publish_merge_sync_session(branch: str, title: str, verification_commands: tuple[str, ...]) -> dict[str, object]:
    _ensure_canonical_origin()
    _ensure_gh_ready()
    _fetch_origin(quiet=True)

    pr = _session_pull_request(branch)
    if pr is not None and str(pr["state"]).upper() == "MERGED":
        if not _branch_merged_into_origin_main(branch):
            raise SystemExit(
                f"Managed branch '{branch}' has an already-merged PR, but the local branch head is not contained in origin/main."
            )
        main_head = _adopt_origin_main()
        _delete_branch(branch)
        return {
            "status": "already_merged",
            "published_branch": branch,
            "pr_number": pr["number"],
            "pr_url": pr["url"],
            "main_head": main_head,
            "main_sync": _main_origin_state(),
        }
    if pr is not None and str(pr["state"]).upper() == "CLOSED":
        raise SystemExit(f"Managed branch '{branch}' already has a closed unmerged PR. Reconcile it manually.")

    _push_session_branch(branch)
    if pr is None:
        pr = _create_session_pull_request(branch, title, verification_commands)
    if bool(pr.get("isDraft")):
        _mark_pull_request_ready(int(pr["number"]))
    _merge_session_pull_request(int(pr["number"]))

    main_head = _adopt_origin_main()
    _delete_branch(branch)
    return {
        "status": "merged",
        "published_branch": branch,
        "pr_number": pr["number"],
        "pr_url": pr["url"],
        "main_head": main_head,
        "main_sync": _main_origin_state(),
    }


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


def _audit_payload() -> dict[str, object]:
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

    return {
        "current_branch": current_branch,
        "main_head": _capture_optional(["git", "rev-parse", "main"]),
        "origin_main_head": _capture_optional(["git", "rev-parse", "origin/main"]),
        "remote_managed_heads": _remote_managed_heads(),
        "remote_review_heads": _remote_review_heads(),
        "merged_local": sorted(merged_local, key=lambda row: row["branch"]),
        "worktree_attached": sorted(worktree_attached, key=lambda row: row["branch"]),
        "open_manual": sorted(open_manual, key=lambda row: row["branch"]),
        "open_managed": sorted(open_managed, key=lambda row: row["branch"]),
    }


def _remote_heads(*patterns: str) -> list[str]:
    output = _capture_optional(["git", "ls-remote", "--heads", "origin", *patterns])
    if not output:
        return []
    heads: list[str] = []
    for line in output.splitlines():
        _sha, ref = line.split("\t", 1)
        heads.append(ref.removeprefix("refs/heads/"))
    return sorted(heads)


def _remote_review_heads() -> list[str]:
    return _remote_heads("review/*")


def _remote_managed_heads() -> list[str]:
    return [head for head in _remote_heads("codex/*", "claude/*", "maint/*") if is_managed_session_branch(head)]


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


def _format_unmerged_block_message(unmerged: list[str]) -> str:
    """Branch-hygiene block message for start-session.

    Surfaces every unmerged managed session branch by name, points the agent
    at the three legitimate resolutions (merge / resume / delete), and
    explains why this gate exists. See AGENTS.md `## Anti-Drift` for the
    historical context: bridge work, audit verdicts, and operator-brain
    work all drifted because unmerged managed branches accumulated across
    sessions; this gate blocks that pattern at session-start time.
    """
    plural = "es" if len(unmerged) != 1 else ""
    lines = [
        f"Cannot start a new session: {len(unmerged)} unmerged managed session "
        f"branch{plural} exist:",
        "",
    ]
    for branch in unmerged:
        lines.append(f"  - {branch}")
    lines.extend(
        [
            "",
            "Resolve one of:",
            "  - Merge:   python3 internal/workflow/repo_workflow.py "
            "close-session --publish --message \"<scope>: <end-state>\"",
            "  - Resume:  python3 internal/workflow/repo_workflow.py "
            "resume-session <slug>",
            "  - Delete:  git branch -D <branch-name>  (only if abandoned)",
            "",
            "If you genuinely need parallel work (e.g. emergency hotfix during",
            "an in-flight investigation), use:",
            "  start-session --agent <agent> --slug <slug> --allow-stacked "
            "--stacked-reason \"<text>\"",
            "The `--stacked-reason` is recorded on the closeout contract for",
            "the new session so the override leaves an explicit audit trail.",
            "",
            "See AGENTS.md `## Anti-Drift` and CLAUDE.md for the discipline.",
        ]
    )
    return "\n".join(lines)


def cmd_start_session(
    agent: str,
    slug: str | None,
    *,
    allow_stacked: bool = False,
    stacked_reason: str | None = None,
) -> int:
    if allow_stacked and not (stacked_reason and stacked_reason.strip()):
        raise SystemExit(
            "start-session --allow-stacked requires --stacked-reason "
            "\"<text>\". The reason is recorded on the new session's "
            "closeout contract so the override leaves an audit trail."
        )

    branch = _current_branch()
    _ensure_clean_tree()
    if branch == "main":
        _ensure_startable_main()
        if not allow_stacked:
            unmerged = [
                candidate
                for candidate in _list_unmerged_managed_branches()
                if candidate != branch
            ]
            if unmerged:
                raise SystemExit(_format_unmerged_block_message(unmerged))
        next_branch = _session_branch_name(agent, slug)
        _run(["git", "switch", "-c", next_branch])
        if allow_stacked:
            _record_stacked_session_reason(next_branch, stacked_reason or "")
        print(next_branch)
        return 0
    if is_managed_session_branch(branch) and _branch_merged_into_main(branch):
        _switch_to_main()
        _delete_branch(branch)
        _ensure_startable_main()
        if not allow_stacked:
            unmerged = [
                candidate
                for candidate in _list_unmerged_managed_branches()
                if candidate != branch
            ]
            if unmerged:
                raise SystemExit(_format_unmerged_block_message(unmerged))
        next_branch = _session_branch_name(agent, slug)
        _run(["git", "switch", "-c", next_branch])
        if allow_stacked:
            _record_stacked_session_reason(next_branch, stacked_reason or "")
        print(next_branch)
        return 0
    raise SystemExit(
        f"Current branch '{branch}' is not clean synced main. Reconcile it manually before starting a managed session."
    )


def _record_stacked_session_reason(branch: str, reason: str) -> None:
    """Persist a `--stacked-reason` to a marker file under .cortex/closeout_contract/.

    The closeout contract `init` step picks this up automatically and seeds
    `stacked_session_reason` into the scaffolded payload. The marker is
    branch-scoped so concurrent stacked sessions cannot overwrite each
    other's reasons.
    """
    root = _root()
    branch_dir = root / ".cortex" / "closeout_contract" / Path(*branch.split("/"))
    branch_dir.mkdir(parents=True, exist_ok=True)
    marker = branch_dir / "stacked_session_reason.txt"
    marker.write_text(reason.strip() + "\n", encoding="utf-8")


def cmd_resume_session(slug: str | None, branch_name: str | None) -> int:
    """Check out an existing managed session branch by slug.

    Resolution order:
      1. If `branch_name` is provided, use it directly (must be a managed
         session branch and must exist locally).
      2. Otherwise, find local managed branches whose name ends with
         `-<slug>`. If exactly one matches, check it out. If zero or
         multiple match, surface a clear error message.

    A non-clean working tree blocks resume; the existing
    `_ensure_clean_tree` provides that check.
    """
    if not branch_name and not slug:
        raise SystemExit(
            "resume-session requires either --slug <slug> or --branch <full-name>."
        )
    _ensure_clean_tree()
    if branch_name:
        target = branch_name.strip()
        if not is_managed_session_branch(target):
            raise SystemExit(
                f"Branch '{target}' is not a managed session branch. "
                "resume-session targets `<agent>/<timestamp>-<slug>` branches only."
            )
        heads = _branch_heads()
        if target not in heads:
            raise SystemExit(
                f"Branch '{target}' does not exist locally. "
                "Available unmerged managed branches:\n"
                + "\n".join(f"  - {b}" for b in _list_unmerged_managed_branches())
            )
        candidates = [target]
    else:
        candidates = _find_managed_branches_by_slug(slug or "")
        if not candidates:
            available = _list_unmerged_managed_branches()
            available_lines = (
                "\n".join(f"  - {b}" for b in available)
                if available
                else "  (none)"
            )
            raise SystemExit(
                f"No managed session branch found with slug '{slug}'.\n"
                f"Available unmerged managed branches:\n{available_lines}"
            )
        if len(candidates) > 1:
            candidate_lines = "\n".join(f"  - {b}" for b in candidates)
            raise SystemExit(
                f"Multiple managed session branches match slug '{slug}':\n"
                f"{candidate_lines}\n"
                "Specify the full branch name with --branch <full-name>."
            )

    target = candidates[0]
    _run(["git", "switch", target])
    print(_resume_session_summary(target))
    return 0


def _resume_session_summary(branch: str) -> str:
    """One-line + counted summary: branch name, commits ahead of origin/main,
    files changed, and closeout contract status (none / partial / valid).
    Non-blocking; informational only.
    """
    ahead_count = _capture_optional(
        ["git", "rev-list", "--count", f"origin/main..{branch}"]
    ) or "?"
    files_changed = _capture_optional(
        ["git", "diff", "--name-only", f"origin/main...{branch}"]
    ) or ""
    file_count = len([line for line in files_changed.splitlines() if line.strip()])

    closeout_path = (
        _root() / ".cortex" / "closeout_contract" / Path(*branch.split("/")) / "closeout.json"
    )
    if closeout_path.exists():
        closeout_status = "present (run `python3 -m internal.closeout.contract validate --mode close-session` to verify)"
    else:
        closeout_status = "none (run `python3 -m internal.closeout.contract init --mode close-session` when ready to close)"

    return (
        f"Resumed: {branch}\n"
        f"  - {ahead_count} commit(s) ahead of origin/main\n"
        f"  - {file_count} file(s) changed since origin/main\n"
        f"  - closeout contract: {closeout_status}"
    )


def cmd_finalize(message: str, manual_exception: bool) -> int:
    branch = _current_branch()
    error = validate_finalize_branch(branch)
    if error is not None:
        raise SystemExit(error)
    if not manual_exception:
        raise SystemExit("Finalize on an explicit manual/review branch requires --manual-exception.")
    subject_error = validate_commit_subject(message)
    if subject_error is not None:
        raise SystemExit(subject_error)
    commit_hash, _verification_commands = _finalize_current_branch(message, mode="finalize", branch=branch)
    if commit_hash is None:
        print("no-op clean tree")
        return 0
    print(f"{branch} {commit_hash}")
    return 0


def cmd_close_session(message: str, publish: bool) -> int:
    branch = _current_branch()
    if not is_managed_session_branch(branch):
        raise SystemExit(f"Current branch '{branch}' is not a managed session branch.")
    subject_error = validate_commit_subject(message)
    if subject_error is not None:
        raise SystemExit(subject_error)
    commit_hash, verification_commands = _finalize_current_branch(message, mode="close-session", branch=branch)
    if publish:
        if not _managed_publication_allowed():
            raise SystemExit(
                "Managed close-session publication requires the canonical repo origin; "
                "use default close-session for a local checkpoint on this repo."
            )
        _ensure_canonical_origin()
        _fetch_origin(quiet=True)
        if commit_hash is None:
            if not _branch_has_unique_commits(branch, "origin/main"):
                main_head = _adopt_origin_main()
                _delete_branch(branch)
                print(
                    json.dumps(
                        {
                            "status": "no_op",
                            "published_branch": None,
                            "pr_number": None,
                            "pr_url": None,
                            "main_head": main_head,
                            "main_sync": _main_origin_state(),
                        },
                        sort_keys=True,
                    )
                )
                return 0
            base_ref = "origin/main"
            reviewed_paths = _changed_paths_between(base_ref, branch)
            _validate_closeout_contract_for_paths("close-session", branch, reviewed_paths)
            verification_commands = _run_verification_for_paths(reviewed_paths)
            _ensure_clean_tree_after_verification()
            _revalidate_closeout_contract_after_verification(
                "close-session",
                branch,
                reviewed_paths,
                _changed_paths_between(base_ref, branch),
            )
        result = _publish_merge_sync_session(branch, message, verification_commands)
        print(json.dumps(result, sort_keys=True))
        return 0
    if commit_hash is None:
        if not _branch_has_unique_commits(branch, "origin/main"):
            main_head = _adopt_origin_main(require_canonical=False)
            _delete_branch(branch)
            print(
                json.dumps(
                    {
                        "status": "no_op",
                        "published_branch": None,
                        "pr_number": None,
                        "pr_url": None,
                        "main_head": main_head,
                        "main_sync": _main_origin_state(),
                    },
                    sort_keys=True,
                )
            )
            return 0
        base_ref = "origin/main"
        reviewed_paths = _changed_paths_between(base_ref, branch)
        _validate_closeout_contract_for_paths("close-session", branch, reviewed_paths)
        verification_commands = _run_verification_for_paths(reviewed_paths)
        _ensure_clean_tree_after_verification()
        _revalidate_closeout_contract_after_verification(
            "close-session",
            branch,
            reviewed_paths,
            _changed_paths_between(base_ref, branch),
        )
    current_branch = _current_branch()
    if current_branch != branch:
        raise SystemExit(
            "Default close-session checkpointing must leave the managed session branch checked out."
        )
    print(
        json.dumps(
            {
                "status": "checkpointed_local",
                "published_branch": None,
                "pr_number": None,
                "pr_url": None,
                "main_head": _capture(["git", "rev-parse", "main"]).strip(),
                "main_sync": _main_origin_state(),
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_audit_branches() -> int:
    payload = _audit_payload()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_cleanup_report() -> int:
    _ensure_canonical_origin()
    _fetch_origin(quiet=True)
    payload = _audit_payload()
    dirty = _tracked_status_lines()
    main_sync = _main_origin_state()

    failures: dict[str, object] = {}
    if payload["current_branch"] != "main":
        failures["current_branch"] = payload["current_branch"]
    if dirty:
        failures["dirty"] = dirty
    if main_sync != "synced":
        failures["main_sync"] = main_sync
    for key in ("worktree_attached", "merged_local", "open_manual", "open_managed"):
        rows = payload[key]
        if rows:
            failures[key] = rows
    if payload["remote_managed_heads"]:
        failures["remote_managed_heads"] = payload["remote_managed_heads"]
    if payload["remote_review_heads"]:
        failures["remote_review_heads"] = payload["remote_review_heads"]

    if not failures:
        proc = subprocess.run(
            ["make", "-C", "internal", "closeout-test"],
            cwd=_root(),
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            failures["closeout_test"] = (proc.stderr or proc.stdout).strip()

    report = {
        "ok": not failures,
        "current_branch": payload["current_branch"],
        "main_head": payload["main_head"],
        "origin_main_head": payload["origin_main_head"],
        "main_sync": main_sync,
        "remote_managed_heads": payload["remote_managed_heads"],
        "remote_review_heads": payload["remote_review_heads"],
    }
    if failures:
        report["failures"] = failures
    else:
        report["status"] = "clean"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


# ---------------------------------------------------------------------------
# Hygiene grid: status-snapshot, reflection-check, grid
# ---------------------------------------------------------------------------
#
# These commands implement the per-turn hygiene discipline described in
# AGENTS.md `## Handoff` and docs/CORTEX.md §6. The grid surfaces the
# repo state, the Cortex progress dashboard, and a substantive reflection
# prompt at the end of every chat. When work has been performed in the
# turn (tracked-file changes since session start), the grid additionally
# surfaces mechanical checks (closeout schema, branch-slug match, etc.)
# and a Loop Decision: any FAIL or unresolved gap blocks close-session.
#
# The substantive validators (handwave detection, minimum length) are
# imported from internal.closeout.contract so the grid and the closeout
# share one definition.

DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_WARN = 30
DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_FAIL = 60


def _registry_payload() -> dict[str, object] | None:
    path = _root() / "internal" / "truth" / "cortex_status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _ahead_behind(branch: str) -> dict[str, int]:
    """Return {ahead, behind} counts vs origin/main. Zero if unavailable."""
    output = _capture_optional(
        ["git", "rev-list", "--left-right", "--count", f"origin/main...{branch}"]
    )
    if not output:
        return {"ahead": 0, "behind": 0}
    parts = output.split()
    if len(parts) != 2:
        return {"ahead": 0, "behind": 0}
    try:
        behind, ahead = int(parts[0]), int(parts[1])
    except ValueError:
        return {"ahead": 0, "behind": 0}
    return {"ahead": ahead, "behind": behind}


def _closeout_state(branch: str) -> dict[str, object]:
    """Inspect the closeout artifact directory for the current branch.

    Returns a {present, profile, validates} payload. `present` is one of
    'absent' | 'scaffolded' | 'rendered' | 'validated'. `validates` is a
    boolean indicating close-session validation passes; `profile` is the
    declared profile when known.
    """
    branch_dir = (
        _root() / ".cortex" / "closeout_contract" / Path(*branch.split("/"))
    )
    json_path = branch_dir / "closeout.json"
    md_path = branch_dir / "closeout.md"
    if not json_path.exists():
        return {"present": "absent", "profile": None, "validates": False}
    try:
        payload = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"present": "scaffolded", "profile": None, "validates": False}
    profile = payload.get("profile") if isinstance(payload, dict) else None
    presence = "rendered" if md_path.exists() else "scaffolded"
    validates = False
    try:
        closeout_contract.cli_validate(
            root=_root(), mode="close-session", branch=branch
        )
        validates = True
        presence = "validated"
    except SystemExit:
        validates = False
    return {"present": presence, "profile": profile, "validates": validates}


def _next_train_freshness_days(registry: dict[str, object] | None) -> int | None:
    """Return days since next_product_train.last_reviewed_at, or None."""
    if not registry:
        return None
    next_train = registry.get("next_product_train")
    if not isinstance(next_train, dict):
        return None
    raw = next_train.get("last_reviewed_at")
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        reviewed_at = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if reviewed_at.tzinfo is None:
        reviewed_at = reviewed_at.replace(tzinfo=dt.timezone.utc)
    now = dt.datetime.now(dt.timezone.utc)
    delta = now - reviewed_at
    return max(delta.days, 0)


_BUNDLING_SURFACE_GROUPS: tuple[tuple[str, ...], ...] = (
    ("cortex/core/",),
    ("cortex/sre/",),
    ("cortex/aux/",),
    ("cortex/runtime/",),
    ("cortex/hosts/",),
    ("cortex/drivers/", "cortex/eval/"),
    ("internal/workflow/", "internal/closeout/"),
    ("internal/truth/",),
    ("internal/archive/", "docs/archive/"),
    ("docs/CORTEX_V2_",),
    ("lab/",),
    ("tests/product/",),
    ("tests/conformance/",),
    ("tests/experimental/",),
    ("tests/lab/",),
    ("tests/internal/",),
)


def _bundling_surfaces(paths: list[str]) -> list[str]:
    """Return the named surface groups touched by the reviewed paths.

    Used as a coarse bundling-detection heuristic: a single concern
    typically touches one or two surface groups; when reviewed paths
    span four or more unrelated groups, that is a bundling signal worth
    surfacing as a gap. Doc / config / root files are intentionally
    excluded because they almost always co-touch with real work.
    """
    touched: list[str] = []
    for group in _BUNDLING_SURFACE_GROUPS:
        if any(any(path.startswith(prefix) for prefix in group) for path in paths):
            touched.append("|".join(group))
    return touched


def _drift_signals(branch: str, registry: dict[str, object] | None) -> list[str]:
    signals: list[str] = []
    # Stale next_train.
    days = _next_train_freshness_days(registry)
    if days is not None and days >= DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_FAIL:
        signals.append(
            f"next_product_train reviewed {days}d ago "
            f"(>= {DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_FAIL}d fail threshold)"
        )
    elif days is not None and days >= DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_WARN:
        signals.append(
            f"next_product_train reviewed {days}d ago "
            f"(>= {DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_WARN}d warn threshold)"
        )
    # Dirty main.
    if branch == "main" and _tracked_status_lines():
        signals.append("worktree dirty on main")
    # Unmerged managed branches present (informational; the gate fires on
    # start-session, but we surface here too so the user sees pending
    # work without running audit-branches).
    unmerged = _list_unmerged_managed_branches()
    others = [name for name in unmerged if name != branch]
    if others:
        signals.append(
            f"unmerged managed branches present: {', '.join(others[:3])}"
            + ("" if len(others) <= 3 else f" (+{len(others) - 3} more)")
        )
    # Dangling closeout: closeout exists for a branch that is no longer
    # checked out and is not main; the workflow keeps the artifact, but
    # if the branch exists locally and has not been merged, surface it.
    if branch != "main" and is_managed_session_branch(branch):
        state = _closeout_state(branch)
        if state["present"] == "scaffolded":
            signals.append(
                "closeout contract scaffolded but not validated for current branch"
            )
    return signals


def _branch_changed_paths(branch: str) -> list[str]:
    """Return paths changed by this session vs origin/main, plus dirty paths."""
    if branch == "main":
        return _normalize_paths(_tracked_status_lines_paths())
    base = "origin/main" if _origin_main_exists() else "main"
    paths = list(_changed_paths_between(base, branch))
    paths.extend(_tracked_status_lines_paths())
    return sorted({p for p in paths if p})


def _tracked_status_lines_paths() -> list[str]:
    """Strip status codes from `_tracked_status_lines` output."""
    paths: list[str] = []
    for line in _tracked_status_lines():
        body = line[3:].strip() if len(line) >= 4 else ""
        if " -> " in body:
            body = body.split(" -> ", 1)[1].strip()
        if body:
            paths.append(body)
    return paths


def _status_snapshot_payload() -> dict[str, object]:
    branch = _current_branch()
    ahead_behind = _ahead_behind(branch) if branch != "main" else {"ahead": 0, "behind": 0}
    if branch == "main":
        ahead_behind = _ahead_behind("HEAD")
    worktree_dirty = bool(_tracked_status_lines())
    closeout = _closeout_state(branch)
    registry = _registry_payload()
    work_today = (registry or {}).get("work_today", {}) if isinstance(registry, dict) else {}
    next_train = (registry or {}).get("next_product_train", {}) if isinstance(registry, dict) else {}
    next_train_days = _next_train_freshness_days(registry)
    drift = _drift_signals(branch, registry)
    return {
        "branch": branch,
        "ahead": ahead_behind["ahead"],
        "behind": ahead_behind["behind"],
        "worktree": "dirty" if worktree_dirty else "clean",
        "closeout": closeout,
        "work_today_slug": (work_today or {}).get("slug"),
        "next_train_slug": (next_train or {}).get("slug"),
        "next_train_reviewed_days_ago": next_train_days,
        "drift_signals": drift,
    }


def _state_rows(payload: dict[str, object]) -> list[tuple[str, str]]:
    """Return state snapshot rows for markdown-table renderers."""
    closeout = payload["closeout"]
    profile = closeout.get("profile")
    closeout_value = closeout["present"]
    if profile and closeout_value != "absent":
        closeout_value = f"{closeout_value} (`{profile}`)"
    drift = payload.get("drift_signals", [])
    drift_value = "none" if not drift else "; ".join(drift)
    return [
        ("Branch", f"`{payload['branch']}`"),
        ("vs origin/main", f"+{payload['ahead']} / -{payload['behind']}"),
        ("Worktree", str(payload["worktree"])),
        ("Closeout", closeout_value),
        ("Drift signals", drift_value),
    ]


def _format_state_table(payload: dict[str, object]) -> str:
    """Render the state snapshot as a 2-column markdown table."""
    rows = _state_rows(payload)
    lines = ["| Field | Value |", "|---|---|"]
    for label, value in rows:
        lines.append(f"| **{label}** | {value} |")
    return "\n".join(lines)


def _format_status_snapshot_markdown(payload: dict[str, object]) -> str:
    """Standalone markdown for status-snapshot command output."""
    return "## Cortex Repo State\n\n" + _format_state_table(payload)


def cmd_status_snapshot(emit_json: bool) -> int:
    payload = _status_snapshot_payload()
    if emit_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_status_snapshot_markdown(payload))
    return 0


def _reflection_check_payload() -> dict[str, object]:
    """Run all reflection-check gates and return PASS/GAPS/FAIL with reasons."""
    snapshot = _status_snapshot_payload()
    branch = snapshot["branch"]
    failures: list[str] = []
    gaps: list[str] = []

    # Mechanical gate 1: closeout schema validates (when artifact exists).
    closeout_state = snapshot["closeout"]
    if closeout_state["present"] != "absent":
        try:
            closeout_contract.cli_validate(
                root=_root(), mode="close-session", branch=branch
            )
        except SystemExit as exc:
            failures.append(f"closeout validate: {exc}")

    # Mechanical gate 2: status doc + cortex doc + archive index --check.
    for cmd, label in (
        (
            ["python3", "internal/truth/generate_status.py", "--check"],
            "generate_status.py --check",
        ),
        (
            ["python3", "internal/truth/generate_cortex_doc.py", "--check"],
            "generate_cortex_doc.py --check",
        ),
        (
            ["python3", "internal/archive/generate_archive_index.py", "--check"],
            "generate_archive_index.py --check",
        ),
    ):
        proc = subprocess.run(
            cmd, cwd=_root(), check=False, capture_output=True, text=True
        )
        if proc.returncode != 0:
            failures.append(f"{label}: {proc.stderr.strip() or proc.stdout.strip()}")

    # Mechanical gate 3: bundling heuristic — flag when reviewed paths
    # span four or more unrelated top-level surface groups, which is the
    # shape that produced the operator-brain-capability bundling drift.
    # A single concern typically touches one or two groups.
    paths = _branch_changed_paths(branch)
    surfaces = _bundling_surfaces(paths)
    if len(surfaces) >= 4:
        gaps.append(
            f"reviewed paths span {len(surfaces)} top-level surface groups "
            f"({', '.join(surfaces[:4])}{'...' if len(surfaces) > 4 else ''}); "
            "possible bundling — confirm the slug describes one concern"
        )

    # Mechanical gate 4: next_train freshness drift signal.
    days = snapshot.get("next_train_reviewed_days_ago")
    if isinstance(days, int) and days >= DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_FAIL:
        failures.append(
            f"next_product_train reviewed {days}d ago "
            f"(>= {DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_FAIL}d fail threshold); "
            "refresh last_reviewed_at or update the queued slot"
        )
    elif isinstance(days, int) and days >= DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_WARN:
        gaps.append(
            f"next_product_train reviewed {days}d ago "
            f"(>= {DRIFT_SIGNAL_STALE_NEXT_TRAIN_DAYS_WARN}d warn threshold)"
        )

    # Mechanical gate 5: hardcoded fixture timestamp grep on changed test files.
    fixture_drift_paths: list[str] = []
    for path in paths:
        if not path.endswith(".py"):
            continue
        if not path.startswith("tests/"):
            continue
        full = _root() / path
        if not full.exists():
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except OSError:
            continue
        # Look for hardcoded ISO-8601 timestamps that are NOT explicitly
        # the stale/expired fixture (2000-01-01) and are not produced by
        # the fresh_validated_at_iso() helper.
        suspicious = re.findall(
            r"\"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2})\"", text
        )
        for stamp in suspicious:
            if stamp.startswith("2000-01-01"):
                continue
            fixture_drift_paths.append(f"{path}: hardcoded ISO timestamp {stamp}")
    if fixture_drift_paths:
        gaps.append(
            "fixture timestamp drift candidates (use fresh_validated_at_iso() "
            "unless test wants stale data): " + "; ".join(fixture_drift_paths[:3])
        )

    if failures:
        verdict = "FAIL"
    elif gaps:
        verdict = "GAPS"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "failures": failures,
        "gaps": gaps,
        "snapshot": snapshot,
        "reviewed_paths": paths,
    }


def _mechanical_check_rows(check_payload: dict[str, object]) -> list[tuple[str, str]]:
    """Return mechanical-gate rows for markdown-table renderers.

    Each gate is named explicitly with its current status so the agent
    cannot fabricate the table from memory; the entries are derived from
    the failures/gaps lists in the reflection-check payload.
    """
    failures = [str(f) for f in check_payload.get("failures", [])]
    gaps = [str(g) for g in check_payload.get("gaps", [])]
    snapshot = check_payload.get("snapshot") or {}

    def _gate(label: str, fail_keywords: tuple[str, ...], gap_keywords: tuple[str, ...] = ()) -> str:
        if any(any(k in f.lower() for k in fail_keywords) for f in failures):
            return "❌ fail — see failures list"
        if gap_keywords and any(
            any(k in g.lower() for k in gap_keywords) for g in gaps
        ):
            return "⚠️ gap — see gaps list"
        return "✅"

    days = snapshot.get("next_train_reviewed_days_ago") if isinstance(snapshot, dict) else None
    if isinstance(days, int):
        if any("next_product_train" in f for f in failures):
            freshness = f"❌ {days}d (>= 60d fail)"
        elif any("next_product_train" in g for g in gaps):
            freshness = f"⚠️ {days}d (>= 30d warn)"
        else:
            freshness = f"✅ {days}d"
    else:
        freshness = "n/a"

    rows = [
        ("Closeout schema", _gate("Closeout schema", ("closeout",))),
        ("`generate_status.py --check`", _gate("status check", ("generate_status",))),
        ("`generate_cortex_doc.py --check`", _gate("cortex doc check", ("generate_cortex_doc",))),
        ("`generate_archive_index.py --check`", _gate("archive index", ("generate_archive_index",))),
        ("Bundling heuristic", _gate("Bundling", ("bundle", "surface group"), ("surface group",))),
        ("`next_train` freshness", freshness),
        ("Fixture timestamp drift", _gate("Fixtures", ("fixture",), ("fixture",))),
    ]
    if failures:
        rows.append(("Failures", "<br>".join(failures)))
    if gaps:
        rows.append(("Gaps", "<br>".join(gaps)))
    return rows


def _format_mechanical_checks_table(check_payload: dict[str, object]) -> str:
    """Render the mechanical-gate results as a 2-column markdown table."""
    rows = _mechanical_check_rows(check_payload)
    lines = ["| Gate | Status |", "|---|---|"]
    for label, status in rows:
        lines.append(f"| {label} | {status} |")
    return "\n".join(lines)


def _format_reflection_check_markdown(payload: dict[str, object]) -> str:
    """Standalone markdown for reflection-check command output."""
    verdict = payload.get("verdict", "?")
    emoji = {"PASS": "✅", "GAPS": "⚠️", "FAIL": "❌"}.get(str(verdict), "❔")
    lines = [
        "## Cortex Reflection-Check",
        "",
        f"**Verdict:** {emoji} `{verdict}`",
        "",
        _format_mechanical_checks_table(payload),
    ]
    return "\n".join(lines)


def cmd_reflection_check(emit_json: bool) -> int:
    payload = _reflection_check_payload()
    if emit_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_reflection_check_markdown(payload))
    return 0 if payload["verdict"] == "PASS" else (1 if payload["verdict"] == "FAIL" else 0)


# Cortex Mission Reflection prompt structure. These rows replace the
# stale dashboard-style progress rows and the weaker goals brief. Each
# filled answer should be causal and grounded: what Cortex
# mission goal this turn served, why the work was the right boundary,
# how the implementation fit the theory, what evidence was actually
# earned, and what remains forbidden.
MISSION_REFLECTION_FIELDS: tuple[tuple[str, str], ...] = (
    (
        "Mission: Cortex target",
        "which Cortex executive-function goal this turn served: continuity, focus, context adoption, brake, truthful closure, or capability-aware routing. Cite the mission surface.",
    ),
    (
        "Mission: Boundary judgment",
        "classify the turn as product Cortex, internal doctrine, lab/proof, monitor/scaffolding, or post-training territory, and justify why that boundary is correct.",
    ),
    (
        "Mission: Theory of improvement",
        "why this work should improve Cortex development or model behavior rather than merely changing repo machinery.",
    ),
    (
        "Mission: Model I/O path",
        "exact path to model input/output, or explicit 'none: internal/lab/governance only' with why that is acceptable.",
    ),
    (
        "Reflection: Plan vs actual",
        "planned intention mapped to realized implementation or analysis, with evidence from touched code/tests/docs when work happened.",
    ),
    (
        "Reflection: Quality judgment",
        "whether this was the best implementation, including tradeoffs and what would have made it better.",
    ),
    (
        "Reflection: Iteration evidence",
        "what failed, was caught, changed, or was corrected this turn; if nothing changed, explain why no iteration was needed.",
    ),
    (
        "Evidence: Earned",
        "structural or live evidence earned this turn, explicitly separating live-vs-structural claims.",
    ),
    (
        "Evidence: Not earned / forbidden",
        "claims still forbidden, especially model-output lift or product progress not actually earned.",
    ),
    (
        "Decision: Next ownership move",
        "continue, stop, split, revise, or return to product work, with reason.",
    ),
)


def _format_verdict(check_payload: dict[str, object]) -> str:
    verdict = check_payload.get("verdict")
    failures = [str(f) for f in check_payload.get("failures", [])]
    gaps = [str(g) for g in check_payload.get("gaps", [])]
    if verdict == "FAIL":
        items = "\n".join(f"- {item}" for item in (failures + gaps)[:10])
        return (
            "❌ **FAIL** — DO NOT close-session. Continue work on:\n\n"
            + items
        )
    if verdict == "GAPS":
        items = "\n".join(f"- {item}" for item in gaps[:10])
        return (
            "⚠️ **GAPS** — review; either resolve in this session or move "
            "to `intentionally_deferred` with rationale:\n\n"
            + items
        )
    return "✅ **PASS** — cleared for close-session."


# Distinctive markdown signature lines used by the Stop hook to detect
# whether the assistant's last message contained the canonical grid
# output. The grid is literally one table under the header: no ``###``
# subsections and no second table. Tests pin the hook's parallel
# constants byte-equal so format drift between the grid and the gate is
# structurally prevented.
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

# Closure markers — these substrings must appear ONLY inside the grid
# block (after GRID_HEADER_MARKER). If they appear before the grid
# header, the agent has emitted closure-shaped prose outside the
# consolidated grid, which violates the "single grid contains all
# closure" rule. The hook checks the prefix portion of the message
# (text before GRID_HEADER_MARKER) for these substrings.
CLOSURE_LEAK_MARKERS = (
    "Ending branch",
    "Verification summary",
    "Fixed now",
    "Claim earned now",
    "Status registry touched",
    "Closure: Metadata",
)


def _compact_repo_state(snapshot: dict[str, object]) -> str:
    """Return branch/worktree/closeout/drift in one compact cell."""
    closeout = snapshot["closeout"]
    closeout_value = str(closeout.get("present"))
    profile = closeout.get("profile")
    if profile and closeout_value != "absent":
        closeout_value = f"{closeout_value} ({profile})"
    drift = snapshot.get("drift_signals", [])
    drift_value = "none" if not drift else "; ".join(str(item) for item in drift)
    return (
        f"branch `{snapshot['branch']}`; vs origin/main +{snapshot['ahead']} / "
        f"-{snapshot['behind']}; worktree {snapshot['worktree']}; "
        f"closeout {closeout_value}; drift {drift_value}"
    )


def _compact_repo_gates(check_payload: dict[str, object]) -> str:
    """Return reflection-check verdict plus failures/gaps when present."""
    verdict = check_payload.get("verdict", "?")
    failures = [str(f) for f in check_payload.get("failures", [])]
    gaps = [str(g) for g in check_payload.get("gaps", [])]
    parts = [f"reflection-check `{verdict}`"]
    if failures:
        parts.append("failures: " + "; ".join(failures[:5]))
    if gaps:
        parts.append("gaps: " + "; ".join(gaps[:5]))
    if not failures and not gaps:
        parts.append("failures/gaps none")
    return "; ".join(parts)


def _closure_metadata_template(snapshot: dict[str, object]) -> str:
    """Return a compact metadata prompt for the agent to fill in place."""
    return (
        f"_[closure metadata — ending branch `{snapshot['branch']}`; commit hash "
        "or `no commit`; verification summary; returned to main yes/no; "
        "status registry touched keys or none; status doc regenerated yes/no; "
        "CORTEX.md regenerated yes/no]_"
    )


def _dogfood_active() -> bool:
    """Return True when Codex App dogfood mode is currently active.

    Reads ``.cortex/live_validation/dogfood/latest.json`` and checks
    ``mode_status``. Inactive (or missing file) returns False so the
    grid omits the Dogfood Signal section by default.
    """
    latest = _root() / ".cortex" / "live_validation" / "dogfood" / "latest.json"
    if not latest.exists():
        return False
    try:
        payload = json.loads(latest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(payload, dict):
        return False
    return payload.get("mode_status") in {"active", "refreshed"}


def _format_dogfood_signal_md() -> str:
    """Render the Dogfood Signal section template (only when dogfood active)."""
    fields = (
        ("continuity_helped", "yes|no"),
        ("blocker_surfaced", "yes|no"),
        ("uncertainty_or_brake_used", "yes|no"),
        ("truthful_closure", "yes|no"),
        ("cortex_changed_next_action", "yes|no"),
        ("note", "<one sentence>"),
    )
    lines = ["| Field | Value |", "|---|---|"]
    for label, placeholder in fields:
        lines.append(f"| **`{label}`** | <fill: {placeholder}> |")
    return "\n".join(lines)


def _table_cell(value: object) -> str:
    """Normalize a value for a single markdown table cell."""
    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")
    return text.replace("|", "\\|")


def _grid_table(rows: list[tuple[str, str]]) -> str:
    lines = [GRID_TABLE_HEADER_MARKER, GRID_TABLE_SEPARATOR_MARKER]
    for label, value in rows:
        lines.append(f"| **{_table_cell(label)}** | {_table_cell(value)} |")
    return "\n".join(lines)


def _dogfood_signal_rows() -> list[tuple[str, str]]:
    return [
        ("continuity_helped", "<fill: yes|no>"),
        ("blocker_surfaced", "<fill: yes|no>"),
        ("uncertainty_or_brake_used", "<fill: yes|no>"),
        ("truthful_closure", "<fill: yes|no>"),
        ("cortex_changed_next_action", "<fill: yes|no>"),
        ("note", "<fill: one sentence>"),
    ]


def _format_grid_markdown(
    snapshot: dict[str, object],
    check_payload: dict[str, object],
    work_performed: bool,
) -> str:
    """Render the per-turn Cortex Repo Hygiene Grid as one table.

    The grid is the **single closure artifact** for every chat: all
    closure / handoff material lives as rows inside the one markdown
    table under ``## Cortex Repo Hygiene Grid``. There are no ``###``
    subsections and no additional tables inside the grid.

    Row groups:
    - ``Repo:*`` rows summarize mechanical state without stale dashboards.
    - ``Mission:*``, ``Reflection:*``, ``Evidence:*``, and ``Decision:*``
      rows force causal mission ownership and are filled in place.
    - ``Closure: Metadata`` is the compact closure metadata row.
    - ``Dogfood:*`` rows are emitted only when dogfood mode is active.
    - ``Verdict`` always emitted.

    Bracketed reflection prompts are filled in place by the agent. The
    Stop hook rejects unmodified prompts, short or uncited mission rows,
    stale ``Progress:*`` rows, ``<fill`` placeholders, and FAIL verdicts.
    """
    rows: list[tuple[str, str]] = []
    rows.append(("Repo: State", _compact_repo_state(snapshot)))
    rows.append(("Repo: Gates", _compact_repo_gates(check_payload)))
    for label, prompt in MISSION_REFLECTION_FIELDS:
        rows.append((label, f"_[mission reflection — {prompt}]_"))
    rows.append(("Closure: Metadata", _closure_metadata_template(snapshot)))
    if _dogfood_active():
        rows.extend(
            (f"Dogfood: {label}", placeholder)
            for label, placeholder in _dogfood_signal_rows()
        )
    rows.append(("Verdict", _format_verdict(check_payload)))
    return "\n\n".join([GRID_HEADER_MARKER, _grid_table(rows)])


def cmd_grid() -> int:
    snapshot = _status_snapshot_payload()
    work_performed = bool(_branch_changed_paths(snapshot["branch"]))
    # Always run reflection-check so drift signals surface in verdict
    # even on no-work turns (stale next_train, dirty main, etc.).
    check_payload = _reflection_check_payload()
    print(_format_grid_markdown(snapshot, check_payload, work_performed))
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
    start_parser.add_argument(
        "--allow-stacked",
        action="store_true",
        help=(
            "Override the branch-hygiene gate: start a new session while "
            "other unmerged managed branches exist. Requires --stacked-reason. "
            "The reason is recorded on the new session's closeout contract."
        ),
    )
    start_parser.add_argument(
        "--stacked-reason",
        help=(
            "Required when --allow-stacked is used. Explains why parallel "
            "session work is necessary (e.g. emergency hotfix during an "
            "in-flight investigation). Logged to the closeout contract."
        ),
    )

    resume_parser = subparsers.add_parser(
        "resume-session",
        help=(
            "Check out an existing managed session branch instead of starting "
            "a new one. Used when the branch-hygiene gate blocks start-session "
            "because in-flight work needs to continue."
        ),
    )
    resume_parser.add_argument(
        "--slug",
        help=(
            "Match by slug-suffix; the branch name format is "
            "<agent>/<timestamp>-<slug>, so --slug <slug> selects the unique "
            "managed branch ending in -<slug>. If multiple match, --branch "
            "is required."
        ),
    )
    resume_parser.add_argument(
        "--branch",
        dest="branch_name",
        help=(
            "Resolve directly by full branch name; required when multiple "
            "managed branches share a slug suffix."
        ),
    )

    finalize_parser = subparsers.add_parser(
        "finalize",
        help="Verify and commit the current manual/review branch; requires --manual-exception.",
    )
    finalize_parser.add_argument("--message", required=True)
    finalize_parser.add_argument(
        "--manual-exception",
        action="store_true",
        help="Acknowledge that finalize is the explicit exception path for a non-session branch.",
    )

    close_parser = subparsers.add_parser(
        "close-session",
        help="Checkpoint a managed session locally by default; add --publish to publish, merge, sync main, and delete the branch.",
    )
    close_parser.add_argument("--message", required=True)
    close_parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish, merge, sync main, and delete the managed session branch instead of keeping a local checkpoint.",
    )

    subparsers.add_parser("audit-branches", help="Report local branch hygiene state without mutating refs.")
    subparsers.add_parser(
        "cleanup-report",
        help="Fail unless the repo is on clean synced main with no extra worktrees, non-main branches, or remote managed/review heads.",
    )

    preserve_parser = subparsers.add_parser(
        "preserve-worktree",
        help="Preserve a dirty non-main worktree onto an explicit manual branch without landing it onto main.",
    )
    preserve_parser.add_argument("--slug")

    snapshot_parser = subparsers.add_parser(
        "status-snapshot",
        help=(
            "Print the deterministic state-snapshot block: branch, "
            "ahead/behind origin/main, worktree, closeout state, current "
            "and queued trains, and any drift signals."
        ),
    )
    snapshot_parser.add_argument(
        "--json",
        action="store_true",
        dest="snapshot_json",
        help="Emit JSON instead of human-readable text.",
    )

    reflection_parser = subparsers.add_parser(
        "reflection-check",
        help=(
            "Run end-of-turn mechanical hygiene checks (closeout schema, "
            "regen --check guards, branch-slug↔paths heuristic, next_train "
            "freshness, hardcoded fixture timestamp grep) and return "
            "PASS / GAPS / FAIL with enumerated reasons."
        ),
    )
    reflection_parser.add_argument(
        "--json",
        action="store_true",
        dest="reflection_json",
        help="Emit JSON instead of human-readable text.",
    )

    subparsers.add_parser(
        "grid",
        help=(
            "Compose the per-turn Cortex Repo Hygiene Grid: state "
            "snapshot, Cortex progress dashboard, goals-analysis prompt, "
            "and (when work has been performed in the session) the "
            "mechanical reflection-check + work-reflection prompts + "
            "loop decision. Run before final handoff every chat."
        ),
    )

    args = parser.parse_args(argv)
    if args.command == "sync-main":
        return cmd_sync_main(args.adopt_origin)
    if args.command == "start-session":
        return cmd_start_session(
            args.agent,
            args.slug,
            allow_stacked=args.allow_stacked,
            stacked_reason=args.stacked_reason,
        )
    if args.command == "resume-session":
        return cmd_resume_session(args.slug, args.branch_name)
    if args.command == "finalize":
        return cmd_finalize(args.message, args.manual_exception)
    if args.command == "close-session":
        return cmd_close_session(args.message, args.publish)
    if args.command == "audit-branches":
        return cmd_audit_branches()
    if args.command == "cleanup-report":
        return cmd_cleanup_report()
    if args.command == "preserve-worktree":
        return cmd_preserve_worktree(args.slug)
    if args.command == "status-snapshot":
        return cmd_status_snapshot(args.snapshot_json)
    if args.command == "reflection-check":
        return cmd_reflection_check(args.reflection_json)
    if args.command == "grid":
        return cmd_grid()
    raise SystemExit(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
