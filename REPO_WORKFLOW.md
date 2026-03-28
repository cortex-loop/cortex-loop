# Repo Workflow

This file is the maintainer workflow contract for this repository.
It governs how humans and AI agents should work in the canonical repo, how they
should leave the repo after each work session, and how local branch state is
kept legible.

## Canonical Repo Home

Active development belongs in:

- `github.com/cortex-loop/cortex-loop`

This clone should treat `main` as the resting branch.
In short: `main` is the resting branch.

## Goal

Managed sessions should end in one of these states:

- clean `main` with no tracked changes
- clean `main` with a verified local commit landed from a managed session branch

Intentional manual/review branch work is the narrow exception:

- clean non-session branch with a verified local commit finalized for manual merge
- no `start-session` / `close-session` used in that chat
- the exception is chosen explicitly up front because the task requires staying on that branch

## Branch Model

- `main` is the resting branch.
- Active managed work happens on fresh session branches created by `start-session`.
- `close-session` verifies the work, lands it onto local `main`, and deletes the session branch.
- Historical branch lines may remain locally, but they should not remain the de facto trunk.

Managed session branch format:

- `codex/<YYYYMMDD-HHMMSS>-<slug>`
- `claude/<YYYYMMDD-HHMMSS>-<slug>`
- `maint/<YYYYMMDD-HHMMSS>-<slug>`

Manual/review branches remain explicit exceptions, for example:

- `review/<slug>`
- `maint/<slug>`

## Canonical Commands

Reconcile local `main` with `origin/main`:

```bash
python scripts/repo_workflow.py sync-main
```

Adopt `origin/main` after a merged PR or deliberate abandonment of local
unpublished `main` history:

```bash
python scripts/repo_workflow.py sync-main --adopt-origin
```

Start a fresh managed session from clean synced `main`:

```bash
python scripts/repo_workflow.py start-session --agent codex --slug task-name
```

Close a managed session and return to clean `main`:

```bash
python scripts/repo_workflow.py close-session --message "docs: tighten workflow wording"
```

Finalize an explicit manual/review branch without touching `main`:

```bash
python scripts/repo_workflow.py finalize --message "docs: manual branch closeout"
```

Preserve a dirty non-main worktree before cleanup:

```bash
python scripts/repo_workflow.py preserve-worktree --slug root-e1-verification
```

Audit local branch hygiene without mutating refs:

```bash
python scripts/repo_workflow.py audit-branches
```

Require the strict final-clean contract:

```bash
python scripts/repo_workflow.py cleanup-report
```

## Session Workflow

1. Start from clean `main`.
2. Run `python scripts/repo_workflow.py sync-main` if needed.
3. Run `python scripts/repo_workflow.py start-session --agent <codex|claude|maint> [--slug <text>]`.
4. Do the work on the managed session branch.
5. End with `python scripts/repo_workflow.py close-session --message "<scope>: <end-state summary>"`.
6. After `close-session` succeeds, the repo is back on clean local `main` and the session branch is gone.

Manual/review branch workflow:

1. Confirm the task explicitly requires staying on the current non-session branch.
2. Do not run `start-session`.
3. Do the work on that branch.
4. End with `python scripts/repo_workflow.py finalize --message "<scope>: <end-state summary>"`.
5. Leave merge/reconciliation to the manual branch owner.

## Rules

`start-session`:

- refuses unless the tree is clean
- refuses unless local `main` tracks and matches `origin/main`
- creates a fresh managed session branch
- refuses on non-`main` branches unless the current branch is already a merged managed session branch that can be safely replaced

`sync-main`:

- requires a clean tree
- fetches `origin`
- no-ops if local `main` is synced
- fast-forwards if local `main` is only behind
- refuses on ahead/diverged `main` unless `--adopt-origin` is used

`close-session`:

- only works on managed session branches
- runs verification before committing
- lands onto local `main` with fast-forward only
- returns HEAD to `main`
- deletes the managed session branch
- refuses deletion if `main` moved and fast-forward is no longer possible

`finalize`:

- only works on explicit non-session branches
- runs verification before committing
- leaves the branch in place for manual merge

`preserve-worktree`:

- only works on dirty non-`main` worktrees
- creates an explicit preservation branch if needed
- captures tracked and untracked work in a safety snapshot commit
- does not try to land onto `main`
- is the only explicit exception to the normal verification-before-commit rule because its purpose is work preservation, not landing

`audit-branches`:

- is read-only
- reports merged local branches, worktree-attached branches, and non-merged manual/managed branches
- does not delete anything

`cleanup-report`:

- is read-only
- fails unless the repo is on clean synced `main`
- fails if any non-root worktree remains attached
- fails if any merged local branch, open manual branch, or open managed branch remains
- fails if any remote `review/*` head remains
- is the final repo-hygiene gate for declaring the repo fully clean

## Commit Message Contract

Commit subject format:

`<scope>: <end-state summary>`

Allowed scopes:

- `repo`
- `docs`
- `kernel`
- `adapter`
- `pack`
- `eval`
- `tests`
- `build`
- `release`

Avoid process-noise subjects such as:

- `scrubbed`
- `final polish`
- `quick fix`
- `temp`
- `WIP`

## Remote Publication

This workflow script manages local branch hygiene only.
Remote publication remains separate:

- push the landed local `main` commit under a review branch
- open the PR
- after merge, run `python scripts/repo_workflow.py sync-main --adopt-origin`

Do not start a new managed session from an ahead/diverged `main` until that
reconciliation is complete.
