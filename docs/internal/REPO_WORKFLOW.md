# Repo Workflow

Surface: internal

This file is the maintainer workflow contract for this repository.
It governs how humans and AI agents should work in the canonical repo, how they
should leave the repo after each work session, and how local branch state is
kept legible.

## Canonical Repo Home

Active development belongs in:

- `github.com/cortex-loop/cortex-loop`

This clone should treat `main` as the resting branch.
In short: `main` is the resting branch.

## Bootstrap

Every new session should start from exactly these four reads:

1. `AGENTS.md`
2. `docs/CORTEX_STATUS.md`
3. `git branch --show-current`
4. `git status --short --untracked-files=all`

## Goal

Managed sessions should end in one of these states:

- clean synced `main` with no tracked changes
- clean synced `main` after managed closeout published, merged, and adopted `origin/main`

Intentional manual/review branch work is the narrow exception:

- clean non-session branch with a verified local commit finalized for manual merge
- no `start-session` / `close-session` used in that chat
- the exception is chosen explicitly up front because the task requires staying on that branch

## Branch Model

- `main` is the resting branch.
- Active managed work happens on fresh session branches created by `start-session`.
- `close-session` verifies the work, publishes the session branch, merges it, adopts `origin/main`, and deletes the session branch.
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
python internal/workflow/repo_workflow.py sync-main
```

Adopt `origin/main` after a merged PR or deliberate abandonment of local
unpublished `main` history:

```bash
python internal/workflow/repo_workflow.py sync-main --adopt-origin
```

Start a fresh managed session from clean synced `main`:

```bash
python internal/workflow/repo_workflow.py start-session --agent codex --slug task-name
```

Close a managed session, publish it, and return to clean synced `main`:

```bash
python internal/workflow/repo_workflow.py close-session --message "docs: tighten workflow wording"
```

Finalize an explicit manual/review branch without touching `main`:

```bash
python internal/workflow/repo_workflow.py finalize --manual-exception --message "docs: manual branch closeout"
```

Preserve a dirty non-main worktree before cleanup:

```bash
python internal/workflow/repo_workflow.py preserve-worktree --slug root-e1-verification
```

Audit local branch hygiene without mutating refs:

```bash
python internal/workflow/repo_workflow.py audit-branches
```

Scaffold the enforced closeout contract for the current branch:

```bash
python -m internal.closeout.contract init --mode close-session
```

Render the closeout contract markdown after editing the JSON:

```bash
python -m internal.closeout.contract render
```

Validate the closeout contract explicitly before closeout:

```bash
python -m internal.closeout.contract validate --mode close-session
```

Require the strict final-clean contract:

```bash
python internal/workflow/repo_workflow.py cleanup-report
```

## Session Workflow

1. Start from clean `main`.
2. Run `python internal/workflow/repo_workflow.py sync-main` if needed.
3. Run `python internal/workflow/repo_workflow.py start-session --agent <codex|claude|maint> [--slug <text>]`.
4. Do the work on the managed session branch.
5. Scaffold or refresh the closeout contract with `python -m internal.closeout.contract init --mode close-session`, then fill the generated JSON under `.cortex/closeout_contract/<branch>/closeout.json`.
6. End with `python internal/workflow/repo_workflow.py close-session --message "<scope>: <end-state summary>"`.
7. After `close-session` succeeds, the repo is back on clean synced `main`, the merged session branch is gone locally and remotely, and no separate publication step remains.

Manual/review branch workflow:

1. Confirm the task explicitly requires staying on the current non-session branch.
2. Do not run `start-session`.
3. Do the work on that branch.
4. Scaffold or refresh the closeout contract with `python -m internal.closeout.contract init --mode finalize`, then fill the generated JSON under `.cortex/closeout_contract/<branch>/closeout.json`.
5. End with `python internal/workflow/repo_workflow.py finalize --manual-exception --message "<scope>: <end-state summary>"`.
6. Leave merge/reconciliation to the manual branch owner.

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
- hard-fails if a substantive closeout is missing a valid closeout contract artifact
- runs the smallest surface-aware verification bundle for the staged or branch-unique paths before landing
- validates the closeout contract against the exact reviewed path set that will be landed
- revalidates the closeout contract after verification so tracked-path drift during verification cannot slip through to publication or landing
- infers `load_bearing` when reviewed paths touch `cortex/**`, `lab/**`, `docs/CORTEX_V2_*.md`, `internal/truth/cortex_status.json`, `docs/CORTEX_STATUS.md`, `AGENTS.md`, `docs/internal/REPO_WORKFLOW.md`, `internal/workflow/**`, `internal/closeout/**`, or `internal/Makefile`
- hard-fails if the contract self-declares `standard` where reviewed paths require `load_bearing`
- on the canonical repo, requires authenticated `gh` and a canonical `origin`
- if the branch has no unique commits relative to `origin/main`, it still adopts `origin/main`, deletes the local session branch, and returns `status: "no_op"`
- the no-op exemption is the only path that bypasses the closeout contract gate
- publishes the same managed session branch to `origin`
- creates or reuses a PR against `main`
- merges with a merge commit and deletes the remote branch
- adopts `origin/main`, returns HEAD to `main`, and deletes the local session branch
- leaves the managed session branch intact if publication or merge fails, and the repo is not back at resting truth
- prints a JSON payload with `status`, `published_branch`, `pr_number`, `pr_url`, `main_head`, and `main_sync`

`finalize`:

- only works on explicit non-session branches
- requires `--manual-exception` so the exception path is always explicit
- hard-fails if a substantive closeout is missing a valid closeout contract artifact
- runs the smallest surface-aware verification bundle for the staged paths before committing
- validates the closeout contract against the exact staged path set before verification and commit
- revalidates the closeout contract after verification and restaging so tracked-path drift cannot slip into the committed closeout
- leaves the branch in place for manual merge

Closeout contract artifact:

- lives under `.cortex/closeout_contract/<branch>/` with `closeout.json`, `closeout.md`, `latest.json`, and `latest.md`
- is generated evidence only, not operational truth
- always requires:
  - seam identity and rationale
  - residuals: fixed now, intentionally deferred, still underfit, zeroed or stubbed terms
  - hostile review from engineer, mathematician, and neuroscientist lenses
  - claims earned now and claims still forbidden
  - north-light audit for microkernel boundary, repo-governance leakage, host-specific policy fork, and generic bloat
- additionally requires for `load_bearing`:
  - governing principle, executive skill, product metric, guardrail, and kill rule
  - non-empty law-to-code completeness rows for active doctrinal, math, or workflow-law terms touched
- hard-fails on stale reviewed paths, reviewed-path drift during verification, missing forbidden claims, missing hostile-review coverage, or missing zeroed/stubbed-term review
- renders one deterministic `Final Handoff Mirror` section; agents should mirror that block in the final chat handoff instead of paraphrasing it ad hoc

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
- fails if any remote managed-session head or remote `review/*` head remains
- is the final repo-hygiene gate for declaring the repo fully clean

Managed verification is purpose-first and surface-aware:

- always: `git diff --check`
- `product` changes: `make product-test`
- `conformance` changes: `make conformance-test`
- `experimental` changes: `make experimental-test`
- `internal` and active-doc truth changes: `python3 internal/truth/generate_status.py --check`, `python3 internal/archive/generate_archive_index.py --check`, `make -C internal test`
- `lab` changes: `make lab-test`
- unknown or root/config changes fall back to the full active bundle
- paid OpenAI service-lane proof is never part of the default bundle
- any command that relies on `CORTEX_LIVE_SERVICE_SPEND_APPROVED` requires explicit user approval in the current chat; agents may not set that opt-in on their own initiative

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

Do not start a new managed session from an ahead/diverged `main`.
