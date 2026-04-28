# CLAUDE Code Bootstrap

This file is the entry point for Claude Code sessions in this repository.

**The canonical agent contract is `AGENTS.md` at the repository root.** Read
that file in full before doing any work. This file does not duplicate its
content; it points at it and adds a small Claude Code–specific bootstrap
checklist.

## Bootstrap (read in order)

1. `AGENTS.md` — the canonical agent contract: mission, authority order,
   non-negotiables, working mode, seam declaration requirements, handoff
   format, philosophy audit.
2. `docs/CORTEX_STATUS.md` — the operational front door. Tells you what is
   currently shipped, what the active train is, and what is queued next.
3. `git branch --show-current` and
   `git status --short --untracked-files=all` — confirm you are on a
   managed session branch (or about to start one) and that the worktree is
   clean.
4. `internal/truth/cortex_status.json` — the machine-backed operational
   truth that backs `docs/CORTEX_STATUS.md`. Edit this file (not the
   generated doc) when registry truth changes; regenerate the doc with
   `python3 internal/truth/generate_status.py`.

## Workflow For Any Non-Trivial Edit

1. `python3 internal/workflow/repo_workflow.py sync-main` — confirm clean
   synced main is the resting state.
2. `python3 internal/workflow/repo_workflow.py start-session --agent claude --slug <descriptive-slug>`
   — open a managed session branch named to match the work being done. The
   branch slug must match the work; bundling unrelated changes onto a
   single branch is the drift pattern the bridge work fell into and has
   been added to AGENTS.md as a forbidden move.
3. Make the change.
4. Run the verification suite relevant to the reviewed paths (see
   `internal/Makefile` and `docs/CORTEX_STATUS.md` for the canonical
   commands: `make product-test`, `make conformance-test`,
   `make experimental-test`, `make -C internal test`, `make lab-test`,
   plus `python3 internal/truth/generate_status.py --check` and
   `python3 internal/archive/generate_archive_index.py --check`).
5. Initialize and fill the closeout contract:
   `python3 -m internal.closeout.contract init --mode close-session`,
   then edit
   `.cortex/closeout_contract/<branch>/closeout.json` to fill seam,
   residuals, hostile_review (3 lenses), claims, north_light_audit (4
   dimensions), and — for load-bearing changes — governing_locks and
   law_to_code_completeness.
6. `python3 -m internal.closeout.contract render` and
   `python3 -m internal.closeout.contract validate --mode close-session`.
7. `python3 internal/workflow/repo_workflow.py close-session --publish --message "<scope>: <end-state summary>"`
   to merge to main, or omit `--publish` to checkpoint locally.

## Handoff Format

Every final summary must mirror the rendered `Final Handoff Mirror` block
from the closeout contract: `Fixed now`, `Intentionally deferred`,
`Still underfit`, `Zeroed or stubbed terms`, `Hostile reviewer critiques`,
`Claim earned now`, `Claim still forbidden`. Plus the philosophy audit
(`PHI_MINIFY`, `PHI_MISSION`, `PHI_NICHE`, `CUT_LIST`).

## Cortex Identity Reminder

Cortex is the shipped multi-host executive layer in this repository. It is
NOT the benchmark harness, train loop, grader stack, lab tooling, or
governance apparatus. Lab/eval/archive surfaces exist to falsify or prove
product seams, not to become the product. When in doubt about whether a
change is in scope: ask whether it makes the shipped Cortex executive
layer better or directly unblocks proving it. If neither, cut it.

## Anti-Drift Discipline (See AGENTS.md §Anti-Drift)

If you observe any of these patterns in your work, stop and re-plan:

- A single session branch bundling multiple unrelated concerns. Bundling
  is what caused the operator_brain_capability work to be lost on the
  hostile-audit branch.
- A test fixture using a hardcoded ISO-8601 timestamp to test
  freshness-bearing logic. Use a runtime helper that returns a value
  relative to `datetime.now()`. The TTL drift in
  `tests/experimental/test_aux_support_priors.py` was caused by exactly
  this anti-pattern.
- An audit verdict written but not landed in the same session, or in a
  follow-up session within a session-pair. The Claude-era audit verdict
  sat on a side branch for 11 days because of this gap.
- A research line that exists in code but is neither active
  (`work_today`), queued (`next_product_train`), retired (archive
  manifest), nor under explicit evaluation
  (`research_lines_under_evaluation`). All four states must be exhaustive;
  no orphan research.
- A closeout contract introducing an `agent_loop_guard` payload with
  `allow_blocked: true` or `require_full_communication_closure: false`.
  These are the procedural shortcuts the bridge postmortem identified;
  the closeout contract validates against them.
- Claiming "full V2 communication", "fully model-visible",
  "live watchlist passed" without the agent_loop_guard payload + a
  passing report. The closeout contract rejects these claims without
  evidence.
