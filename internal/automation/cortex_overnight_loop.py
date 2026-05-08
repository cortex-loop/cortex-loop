#!/usr/bin/env python3
"""Guardrail runner for the local Cortex overnight evaluator loop."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIGEST_ROOT = Path(".cortex/automation/overnight")
LOCK_NAME = "cortex_overnight_loop.lock"
OVERNIGHT_HOURS = tuple(list(range(22, 24)) + list(range(0, 8)))
SAFE_AUTO_MERGE_SURFACES = {
    "no-live lab/proof evaluator build",
    "no-live evaluator architecture gate",
    "lab",
    "internal",
}
EVALUATOR_AUTHORIZED_SLUG_PREFIXES = (
    "cortex-executive-effectiveness-evaluator",
    "cortex-overnight-evaluator-automation-hardening",
)
ALLOWED_LIVE_SLUG_PARTS = (
    "evaluator",
    "paired-value",
    "live-probe",
    "live-matrix",
)
FORBIDDEN_REVIEW_PHRASES = (
    "product law revision",
    "fixture/scoring",
    "hidden scoring",
    "hidden-verifier change",
    "external paid",
    "service-lane",
    "positive lift",
    "value claim",
    "shipping promotion",
)
FORBIDDEN_CANDIDATE_PATH_PREFIXES = (
    "cortex/core/",
    "docs/CORTEX_V2_",
    "internal/workflow/",
    "docs/internal/REPO_WORKFLOW.md",
)
FORBIDDEN_CANDIDATE_PATH_FRAGMENTS = (
    "hidden_verifier",
    "hidden-verifier",
    "fixture",
    "fixtures",
    "scoring",
)
OLD_HOOK_HARNESS_PATH = "lab/codex_app_cli_hook_native_behavior_comparison.py"
CANDIDATE_RECORD_FIELDS = (
    "candidate_id",
    "parent_id",
    "policy_candidate",
    "changed_files",
    "mutation_reason",
    "metrics",
    "score",
    "failure_class",
    "contraction_implication",
)


@dataclass(frozen=True)
class GitState:
    branch: str
    dirty: bool
    synced: bool
    managed_branch: bool
    status_short: str


@dataclass(frozen=True)
class BloatMetrics:
    loc_added: int
    loc_deleted: int
    changed_files: tuple[str, ...]
    new_policy_paths: tuple[str, ...]
    duplicate_policy_removed: bool
    contraction_debt_increased: bool


@dataclass(frozen=True)
class LoopDecision:
    status: str
    next_slug: str | None
    safe_to_auto_merge: bool
    live_codex_allowed: bool
    user_input_required: bool
    reasons: tuple[str, ...]
    recommended_commands: tuple[str, ...]


def _run_git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )


def load_status(root: Path) -> dict[str, Any]:
    return json.loads((root / "internal/truth/cortex_status.json").read_text())


def inspect_git_state(root: Path) -> GitState:
    branch = _run_git(root, ["branch", "--show-current"]).stdout.strip()
    status_short = _run_git(root, ["status", "--short", "--untracked-files=all"]).stdout
    behind = _run_git(root, ["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    synced = False
    if behind.returncode == 0:
        counts = behind.stdout.strip().split()
        synced = counts == ["0", "0"]
    return GitState(
        branch=branch,
        dirty=bool(status_short.strip()),
        synced=synced,
        managed_branch=branch.startswith(("codex/", "claude/", "maint/")),
        status_short=status_short,
    )


def parse_numstat(text: str) -> tuple[int, int, tuple[str, ...]]:
    added = 0
    deleted = 0
    files: list[str] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_text, delete_text, path = parts[0], parts[1], parts[2]
        files.append(path)
        if add_text.isdigit():
            added += int(add_text)
        if delete_text.isdigit():
            deleted += int(delete_text)
    return added, deleted, tuple(files)


def is_policy_path(path: str) -> bool:
    lowered = path.lower()
    return any(
        marker in lowered
        for marker in (
            "policy",
            "actuator",
            "intervention",
            "task_standard",
            "tool_evidence",
            "runtime",
        )
    )


def bloat_metrics_from_numstat(text: str) -> BloatMetrics:
    added, deleted, files = parse_numstat(text)
    new_policy_paths = tuple(path for path in files if is_policy_path(path))
    return BloatMetrics(
        loc_added=added,
        loc_deleted=deleted,
        changed_files=files,
        new_policy_paths=new_policy_paths,
        duplicate_policy_removed=deleted > added and bool(new_policy_paths),
        contraction_debt_increased=added > deleted and bool(new_policy_paths),
    )


def _text_line_count(path: Path) -> int:
    try:
        data = path.read_bytes()
    except OSError:
        return 0
    if not data:
        return 0
    if b"\0" in data[:4096]:
        return 0
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return 0
    return max(1, len(text.splitlines()))


def _with_untracked_files(
    root: Path,
    bloat: BloatMetrics,
    untracked_files: Sequence[str],
) -> BloatMetrics:
    existing = set(bloat.changed_files)
    additions: list[str] = []
    added_lines = 0
    for path in untracked_files:
        if path in existing:
            continue
        additions.append(path)
        added_lines += _text_line_count(root / path)
    changed_files = (*bloat.changed_files, *additions)
    new_policy_paths = tuple(path for path in changed_files if is_policy_path(path))
    loc_added = bloat.loc_added + added_lines
    return BloatMetrics(
        loc_added=loc_added,
        loc_deleted=bloat.loc_deleted,
        changed_files=changed_files,
        new_policy_paths=new_policy_paths,
        duplicate_policy_removed=bloat.loc_deleted > loc_added and bool(new_policy_paths),
        contraction_debt_increased=loc_added > bloat.loc_deleted and bool(new_policy_paths),
    )


def collect_bloat_metrics(root: Path) -> BloatMetrics:
    diff = _run_git(root, ["diff", "--numstat", "origin/main"])
    if diff.returncode != 0 or not diff.stdout.strip():
        diff = _run_git(root, ["diff", "--numstat"])
    bloat = bloat_metrics_from_numstat(diff.stdout)
    untracked = _run_git(root, ["ls-files", "--others", "--exclude-standard"])
    if untracked.returncode != 0 or not untracked.stdout.strip():
        return bloat
    return _with_untracked_files(root, bloat, untracked.stdout.splitlines())


def forbidden_candidate_paths(paths: Sequence[str]) -> tuple[str, ...]:
    forbidden: list[str] = []
    for path in paths:
        if path.startswith(FORBIDDEN_CANDIDATE_PATH_PREFIXES):
            forbidden.append(path)
            continue
        lowered = path.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_CANDIDATE_PATH_FRAGMENTS):
            forbidden.append(path)
    return tuple(forbidden)


def task_specific_harness_paths(paths: Sequence[str]) -> tuple[str, ...]:
    offenders: list[str] = []
    for path in paths:
        lowered = path.lower()
        if path == OLD_HOOK_HARNESS_PATH:
            offenders.append(path)
        elif path.startswith("lab/") and "posttooluse" in lowered and "cortex_effectiveness" not in lowered:
            offenders.append(path)
    return tuple(offenders)


def repeated_simple_baseline_losses(
    candidate_rows: Sequence[Mapping[str, Any]],
) -> tuple[str, ...]:
    loss_counts: dict[str, int] = {}
    for row in candidate_rows:
        if row.get("failure_class") != "failure_simple_baseline_parity":
            continue
        policy = str(row.get("policy_candidate") or row.get("candidate_id") or "unknown")
        loss_counts[policy] = loss_counts.get(policy, 0) + 1
    return tuple(sorted(policy for policy, count in loss_counts.items() if count >= 2))


def classify_next_work(
    status: Mapping[str, Any],
    git_state: GitState,
    bloat: BloatMetrics | None = None,
) -> LoopDecision:
    next_train = status.get("next_product_train") or {}
    if not isinstance(next_train, Mapping):
        next_train = {}
    slug = next_train.get("slug")
    surface = str(next_train.get("surface") or "")
    guardrail = str(next_train.get("guardrail") or "").lower()
    primary_metric = str(next_train.get("primary_metric") or "").lower()
    kill_rule = str(next_train.get("kill_rule") or "").lower()
    combined = " ".join((surface.lower(), guardrail, primary_metric, kill_rule))
    reasons: list[str] = []

    if git_state.branch == "main":
        if git_state.dirty:
            reasons.append("main worktree is dirty; overnight loop may not start from dirty resting state")
        if not git_state.synced:
            reasons.append("main is not synced with origin/main; run repo workflow sync-main first")
    elif not git_state.managed_branch:
        reasons.append("current branch is not main or a managed session branch")

    if not isinstance(slug, str) or not slug.strip():
        reasons.append("next_product_train.slug is missing")
        slug_text = None
    else:
        slug_text = slug
        if not slug.startswith(EVALUATOR_AUTHORIZED_SLUG_PREFIXES):
            reasons.append(f"next train `{slug}` is not evaluator-authorized")

    if any(phrase in combined for phrase in FORBIDDEN_REVIEW_PHRASES):
        reasons.append("current truth names a user-review boundary or forbidden mutation surface")

    if bloat is not None:
        forbidden_paths = forbidden_candidate_paths(bloat.changed_files)
        if forbidden_paths:
            reasons.append(
                "candidate touches forbidden mutation surfaces: "
                + ", ".join(forbidden_paths)
            )
        harness_paths = task_specific_harness_paths(bloat.changed_files)
        if harness_paths:
            reasons.append(
                "task-specific harness growth detected; use general evaluator episode rows: "
                + ", ".join(harness_paths)
            )

    live_forbidden_by_truth = "no live codex run" in combined
    live_requested = (
        not live_forbidden_by_truth
        and ("live" in (slug_text or "").lower() or "live" in combined)
    )
    live_allowed = live_requested and all(
        part in (slug_text or "").lower() or part in combined
        for part in ("evaluator",)
    )
    if live_requested and not live_allowed:
        reasons.append("live run is not inside the registered evaluator plan")

    safe_surface = surface in SAFE_AUTO_MERGE_SURFACES or surface.startswith("no-live")
    no_positive_claim = not any(
        phrase in combined
        for phrase in ("positive lift", "value claim", "shipping promotion")
    )
    safe_to_auto_merge = not reasons and safe_surface and no_positive_claim and not live_requested
    status_text = "ready" if not reasons else "blocked"
    commands = []
    if status_text == "ready":
        if git_state.branch == "main":
            commands.append("python3 internal/workflow/repo_workflow.py start-session --agent codex --slug " + slug_text)
        else:
            commands.append("continue managed session branch " + git_state.branch)
        commands.append("implement only the current evaluator-authorized seam")
        commands.append("run targeted tests, generated-doc checks, closeout validation, and cleanup-report")
    else:
        commands.append("stop and report blocker in daily digest")

    return LoopDecision(
        status=status_text,
        next_slug=slug_text,
        safe_to_auto_merge=safe_to_auto_merge,
        live_codex_allowed=live_allowed,
        user_input_required=bool(reasons),
        reasons=tuple(reasons),
        recommended_commands=tuple(commands),
    )


class LoopLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fd: int | None = None

    def __enter__(self) -> "LoopLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(f"overnight loop lock already exists: {self.path}") from exc
        os.write(self._fd, str(os.getpid()).encode())
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._fd is not None:
            os.close(self._fd)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def render_digest(
    *,
    now: datetime,
    git_state: GitState,
    decision: LoopDecision,
    bloat: BloatMetrics,
    candidate_contraction: Sequence[str] = (),
) -> str:
    lines = [
        f"# Cortex Overnight Digest — {now.date().isoformat()}",
        "",
        f"- Timestamp: `{now.isoformat()}`",
        f"- Branch: `{git_state.branch}`",
        f"- Dirty: `{git_state.dirty}`",
        f"- Synced with origin/main: `{git_state.synced}`",
        f"- Decision: `{decision.status}`",
        f"- Next train: `{decision.next_slug}`",
        f"- Safe auto-merge: `{decision.safe_to_auto_merge}`",
        f"- Codex CLI live allowed: `{decision.live_codex_allowed}`",
        "",
        "## Bloat Delta",
        "",
        f"- LOC added: `{bloat.loc_added}`",
        f"- LOC deleted: `{bloat.loc_deleted}`",
        f"- Changed files: `{len(bloat.changed_files)}`",
        f"- New policy paths: `{', '.join(bloat.new_policy_paths) if bloat.new_policy_paths else 'none'}`",
        f"- Duplicate policy removed: `{bloat.duplicate_policy_removed}`",
        f"- Contraction debt increased: `{bloat.contraction_debt_increased}`",
        "",
        "## Decision Reasons",
        "",
    ]
    if decision.reasons:
        lines.extend(f"- {reason}" for reason in decision.reasons)
    else:
        lines.append("- none")
    lines.extend(["", "## Recommended Commands", ""])
    lines.extend(f"- `{command}`" for command in decision.recommended_commands)
    lines.extend(["", "## Contraction Candidates", ""])
    if candidate_contraction:
        lines.extend(f"- `{candidate}` lost to simple baseline at least twice" for candidate in candidate_contraction)
    else:
        lines.append("- none")
    lines.extend(["", "## User Input Needed", ""])
    lines.append("- yes" if decision.user_input_required else "- no")
    lines.append("")
    return "\n".join(lines)


def run_once(
    root: Path = DEFAULT_ROOT,
    *,
    now: datetime | None = None,
    digest_root: Path = DEFAULT_DIGEST_ROOT,
    candidate_rows: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    now = now or datetime.now().astimezone()
    root = root.resolve()
    digest_root = digest_root if digest_root.is_absolute() else root / digest_root
    lock_path = digest_root / LOCK_NAME
    with LoopLock(lock_path):
        status = load_status(root)
        git_state = inspect_git_state(root)
        bloat = collect_bloat_metrics(root)
        decision = classify_next_work(status, git_state, bloat)
        contraction = repeated_simple_baseline_losses(candidate_rows)
        day_dir = digest_root / now.date().isoformat()
        day_dir.mkdir(parents=True, exist_ok=True)
        digest_text = render_digest(
            now=now,
            git_state=git_state,
            decision=decision,
            bloat=bloat,
            candidate_contraction=contraction,
        )
        digest_path = day_dir / "digest.md"
        report_path = day_dir / "cycle_report.json"
        digest_path.write_text(digest_text, encoding="utf-8")
        report = {
            "timestamp": now.isoformat(),
            "overnight_hours": list(OVERNIGHT_HOURS),
            "candidate_record_fields": list(CANDIDATE_RECORD_FIELDS),
            "git_state": asdict(git_state),
            "bloat": asdict(bloat),
            "decision": asdict(decision),
            "contraction_candidates": list(contraction),
            "digest_path": str(digest_path),
            "report_path": str(report_path),
        }
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one guarded Cortex overnight evaluator-loop cycle."
    )
    parser.add_argument("--once", action="store_true", help="run one cycle")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--digest-root", type=Path, default=DEFAULT_DIGEST_ROOT)
    parser.add_argument("--now", help="ISO timestamp override for tests")
    args = parser.parse_args(argv)
    if not args.once:
        parser.error("select --once")
    now = datetime.fromisoformat(args.now) if args.now else None
    try:
        report = run_once(args.repo_root, now=now, digest_root=args.digest_root)
    except RuntimeError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, indent=2))
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["decision"]["status"] == "ready" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
