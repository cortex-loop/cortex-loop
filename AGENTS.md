# Cortex v2 Repo Agent Contract

This file applies to agents editing this repository.
It does not define runtime policy for downstream Cortex users.

## Mission lock

Cortex is the shipped executive layer in this repository.
The product goal is not to ship diagnostics, train loops, graders, workstream ledgers, or governance records.

Every seam must be judged against one question:

**Does this make the shipped Cortex executive layer better, or directly unblock proving and building that layer?**

If the answer is no, cut the seam or move it out of the product-critical path.

## Required decision loop

Run this loop three times: before editing, before finalizing a change, and before handoff.

1. `PHI_MINIFY` — Is this the smallest change that solves the actual problem?
2. `PHI_MISSION` — Does this improve the v2 mission directly: better output, better agency/memory/control, lifecycle-first execution, and a tiny integrity core?
3. `PHI_NICHE` — Is this the right mechanism for this repository, or generic bloat / v1 carryover?

If any answer is no, redesign or cut scope.

## Seam declaration requirement

Before widening scope, every seam must declare these fields explicitly:

- `Surface:` `product | experimental | lab | internal`
- `Executive Benefit:` the direct way the seam improves the shipped executive layer, or the exact shipped-product blocker it removes
- `Why this beats direct product work now:` one sentence

If a seam is `lab` or `internal`, the declaration must explain why the work is still worth doing now instead of a narrower product seam.

## Hard stops

- Do not reintroduce v1 stop-centered architecture by inertia.
- Do not expand the integrity microkernel beyond commitments, provenance, blockedness, and hard boundaries without explicit evidence.
- Do not move active executive policy into the core.
- Do not let AUX become a hidden second truth court.
- Do not flatten host differences just to preserve a fake uniform runtime.
- Do not treat the v1 archive as active authority.
- Do not add math that has no operational consequence.
- Do not add tunable weights unless changing them would plausibly change runtime behavior in a legible way.
- Do not describe lab, evidence, or governance work as Cortex product progress unless shipped runtime behavior actually changes.
- Do not open a new diagnostic or governance seam without an explicit product-unblocking reason.
- Do not let evaluation machinery become the public or internal identity of Cortex.

## Repo hygiene guard

- Do not commit personal/client project names, domains, or account handles.
- Do not commit absolute local paths unless the task is explicitly about local machine setup documentation.
- Keep docs/comments/commit messages in neutral technical language.
- Avoid persona branding in repo text.
- Use anonymized labels in evidence artifacts (`project_a`, `workspace_b`) unless a real public runtime name is required.
- If a claim needs private evidence, summarize it and keep private artifacts out of git.

## Change narration discipline

- Commit and PR titles must describe the resulting state, not the cleanup process.
- Prefer concise end-state wording.
- Avoid temporary/meta phrasing (`quick fix`, `scrubbed`, `final polish`).
- Keep language stable and technical.

## Active authority

The active v2 authority surfaces in this repository are:

Packet documents:
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`

Operational truth:
- `internal/truth/cortex_status.json`
- `docs/CORTEX_STATUS.md`

Maintainer workflow:
- `docs/internal/REPO_WORKFLOW.md`
- `internal/workflow/repo_workflow.py`

Authority order:

1. Core
2. SRE
3. AUX
4. `internal/truth/cortex_status.json`
5. `docs/CORTEX_STATUS.md` (generated human-readable view)
6. `docs/internal/REPO_WORKFLOW.md`

If those documents disagree, fix the disagreement before widening scope.

## Archive authority

`docs/archive/` and the v1 archive repo are evidence and reference only.
They are not normative authority for what v2 should be.

Use the archive only for:

- battle-proven narrow primitives,
- historical validation/evidence patterns,
- host/runtime behavior reference,
- and examples of what not to rebuild.

If a v1 mechanism is being carried over, re-earn it under the v2 packet instead of assuming continuity.

## Maintainer workflow authority

- `docs/internal/REPO_WORKFLOW.md` is the maintainer workflow authority for branch/session hygiene in this repository.
- `internal/workflow/repo_workflow.py` is the enforcing helper surface for that workflow.
- `internal/truth/cortex_status.json` is the single operational truth surface.
- `docs/CORTEX_STATUS.md` is the generated bootstrap view for humans and new chats.
- `preserve-worktree` is the only explicit exception to the normal verification-before-commit rule, and it exists only to avoid losing unresolved dirty work before cleanup.
- `cleanup-report` is the strict final repo-hygiene gate for declaring the repo fully clean.

## Design guardrails for v2

- Lifecycle-first: organize around real host lifecycle/orchestration events.
- Packet-first internally: keep typed internal semantics.
- Host-native externally: prefer the strongest native host surface that exists.
- Executive-first: active intelligence belongs in SRE or later executive realizations, not in the core.
- Microkernel-limited: the hard center stays tiny.
- Contradiction-preserving: mixed, blocked, degraded, and host-specific outcomes must remain explicit.
- Neutral-by-default: the executive should not intervene just to justify itself.
- First host vertical slice before broad multi-host shipping rollout.
- Shipping truth may stay narrower than development conformance truth; when Cortex law changes, OpenAI, Claude, and Gemini still require explicit conformance status on their strongest available native surfaces.
- AUX remains off the MVP critical path unless explicitly promoted.

## Porting rules from v1

- Port a small v1 standard library plus evidence discipline, not v1 architecture.
- High-confidence carryover targets are narrow commitment-carrier parsing, provenance helpers, thin host-event normalization, and contradiction-preserving validation structure.
- Anything proof-centered, adapter-heavy, or prompt-heavy stays suspect until re-earned.
- If a v1 primitive must be reshaped to fit Core / SRE / AUX cleanly, prefer rewrite over direct transplant.

## Working rules

- Default to the smallest slice that preserves packet boundaries.
- Do not implement around free variables silently; either lock them in the active docs or record the blocker.
- If you introduce a new concept, say which layer owns it: Core, SRE, AUX, or later implementation-only.
- If a concept belongs in implementation or evaluation rather than the constitutional packet, keep it out of the packet.
- If you change the packet, say whether the implementation master plan must change in the same slice.
- If you change the intended v1 carryover boundary, record it in `internal/truth/cortex_status.json` and touch archived evidence only if the historical mapping itself changed.

## Cortex-law train discipline

Cortex is the invariant cortical circuit in this repository.
Models, APIs, and CLIs are different brains and wiring surfaces, not different product identities.

Any seam that changes Cortex law must distinguish four truths explicitly:

- `Cortex truth` — the invariant law of Cortex itself
- `brain-wiring truth` — how Cortex is attached to OpenAI, Claude, and Gemini
- `conformance truth` — how faithfully each brain/surface realizes Cortex
- `shipping truth` — which realization is the current product default

For Cortex-law development:

- do not hide major brains behind `deferred` or `future backlog only` wording when they are still required for conformance
- use conformance statuses exactly: `conformant`, `partial`, `divergent`, `unwired`, `env_blocked`
- keep shipping truth distinct from conformance truth; shipping may remain narrower without redefining Cortex itself

Every long train must start by recording a `Train Charter` with:

- `Cortex invariant`
- `brain wiring touched`
- `borrowed mechanism`
- `contract pack`
- `conformance surfaces`
- `kill criteria`
- `baseline result`
- `primary_metric`
- `guardrail_metric`
- `iteration_budget`
- `rollback_surface`
- `escalation_triggers`

First-principles rule:

- state the minimal governing principle before implementation
- do not begin from host quirks, adapter drift, or prior local hacks
- say what evidence would prove the current Cortex law wrong rather than only the current wiring

Borrow/clone rule:

- every new mechanism must identify one of:
  - a battle-proven v1 primitive worth rewriting
  - an external proven mechanism worth copying in tiny form
  - or a brand-new mechanism justified directly from packet law
- say why the chosen mechanism is small, operational, and non-decorative

Rapid iteration rule:

- default mode is `build -> test -> iterate -> cut`
- the first implementation must be the smallest runnable form
- baseline must be recorded before the first edit or candidate proof run
- every iteration must end in exactly one of: `promote`, `revise`, `cut`, `escalate`
- default `iteration_budget` is `2` revisions after baseline unless the train charter locks a stricter budget
- if two iterations fail without improving the divergence classification, stop and reframe before adding more mechanism

Loop-class rule:

- classify each train as exactly one of:
  - `deterministic`
  - `shared verification-plumbing`
  - `timing/env-sensitive`
- lock loop behavior by class:
  - `deterministic`: baseline + up to 2 revisions, full local proof on each iteration
  - `shared verification-plumbing`: baseline + up to 2 deterministic revisions, then repeat repo-local reruns through the real entrypoint before `promote`
  - `timing/env-sensitive`: candidate must first pass deterministic proof, then each iteration requires repeated direct reruns and repeated repo-local reruns before `promote`
- `env_blocked` never counts as success
- one immediate retry is allowed for transient provider noise
- repeated `env_blocked` must `escalate`, not silently consume the whole train

Closed-loop decision rule:

- every train must choose exactly one `primary_metric` and one `guardrail_metric`
- allowed primary metrics are:
  - shipping-lane pass-rate improvement on the active contract pack
  - conformance-status improvement
  - repair-conversion improvement
  - divergence-class reduction
  - deterministic bundle pass/fail improvement
- allowed guardrails are:
  - thin path unchanged
  - no phase-gate regression
  - no correspondence drift
  - no new cross-brain contradiction
- `promote` only if the primary metric improves and guardrails hold
- `revise` only if the failure is localized, owned, and budget remains
- `cut` if there is no metric lift, no clearer divergence classification, or added mechanism without changed outcome
- `escalate` only if:
  - Cortex law may need revision
  - shipping truth would widen
  - authority docs conflict
  - auth / spend / env blocks proof
  - or two revisions fail without better classification

Tri-brain conformance rule:

- when a seam changes Cortex law, run the same contract pack on OpenAI, Claude, and Gemini
- use the strongest available native surface on each brain for development conformance
- API/service remains preferred for shipping truth and canonical proof
- CLI/operator is acceptable for development conformance when service wiring is absent or blocked
- if the same divergence repeats across brains, challenge Cortex law before adding more host-specific wiring

Maintainer loop recorder rule:

- use one thin maintainer-only recorder such as `lab/cortex_train_loop.py` to capture baseline, proof commands, decisions, and local loop artifacts
- do not add branch management, weighted scoring, editing logic, or a second persistent truth ledger around that recorder

## Counterfactual reframe discipline

If repeated host-specific failure persists on the same framing:

- stop before another micro-tweak on the same assumption family,
- generate at least 3 materially different explanations for the failure,
- make sure one explanation explicitly challenges the current framing,
- and make sure one explanation tests the host default path before any further custom pinning or local workaround.

This is maintainer workflow law, not runtime doctrine.

## Operational truth discipline

- `internal/truth/cortex_status.json` is the single living operational truth. Do not create a second status doctrine elsewhere.
- Before planning or issuing a worker seam, classify the seam as `load-bearing` or `non-load-bearing`.
- Every load-bearing seam plan must include `Status impact:` listing the exact registry keys or generated status sections expected to change.
- A non-load-bearing seam may use `Status impact: none expected` only with a one-line reason.
- Before acceptance, compare planned `Status impact:` against delivered `Status registry touched:`.

## Boundary-carrier seam discipline

If a seam changes a typed boundary contract (for example: constructor validation, required fields, enum/domain narrowing, or invariant enforcement):

- Treat all direct construction sites of that carrier as part of the review surface until classified.
- Before editing, classify construction sites as:
  - owned and must reconcile in the same seam,
  - out-of-scope blocker,
  - or already lawful / no change needed.
- Do not mark a seam `landed` if the canonical verification bundle fails due to owned-surface fallout.
- Do not tighten a boundary carrier only on abstract strictness grounds unless either:
  - the carrier is itself a truth/publication surface,
  - or a real runtime/publication path has been reproduced.
- Keep accepted baseline and candidate seam distinct; unaccepted local edits are not truth.

Archived gate and correspondence ledgers remain evidence only. They can inform a seam, but they do not outrank the packet plus the single status registry.

## Parent acceptance discipline

- The parent thread must independently verify worker claims before accepting or committing a seam.
- Acceptance is adversarial, not ceremonial: the parent should try to break the seam at its most likely failure mode before marking it `landed`.
- A load-bearing seam may not be accepted as `landed` unless the handoff includes a code diff, tests, and exact `Status registry touched:`.
- `Status registry touched: none` is only acceptable when the seam is non-load-bearing or when the handoff explicitly justifies why no new load-bearing object, implementation home, shipping/conformance status, or promised test surface changed.
- If a seam adds or moves a load-bearing object, implementation home, or promised test surface without a status update or explicit confirmation that the registry is unchanged, it cannot be marked `landed`.
- Before acceptance, classify seam risk at minimum as one of:
  - deterministic code/doc seam,
  - parser/doc-sync seam,
  - timing or environment-sensitive seam,
  - shared verification-plumbing seam.
- One clean rerun is insufficient for timing-, environment-, or evidence-revalidation seams. Those seams require repeat-stability proof through repeated direct reruns and repeated repo-local entry-point reruns before acceptance.
- When a seam changes verification logic, evidence interpretation, or repo-local verification entry points, the parent must read the full touched files, not only the diff hunk.
- Do not issue the next worker prompt until the current seam has been either rejected or accepted and committed, and the worktree is clean except for explicitly acknowledged unrelated noise.

## Subagent workflow

- The parent thread owns seam selection, status truth, blocker truth, and final diff acceptance.
- Use project-scoped custom agents for bounded roles:
  - `cortex_archivist` for v1/archive mining and evidence extraction
  - `cortex_packet_auditor` for packet/layer consistency and seam-scope review
  - `cortex_host_researcher` for external host/runtime documentation research
  - `cortex_worker` for one bounded write seam after the parent has fixed the touch surface
- Prefer read-only subagents for archive mining, packet audit, and host research; use at most one write-capable subagent at once.
- Keep subagent depth at `1` and total threads at `3` or fewer unless the active implementation plan is updated in the same slice.
- If a task appears to need multiple concurrent writers, split the seam instead of widening it.
- Keep subagent scope small enough that the parent can still verify the seam against the packet and the single status registry.

## Git and workflow

- Canonical development repo: `github.com/cortex-loop/cortex-loop`.
- Canonical archive repo: `github.com/cortex-loop/cortex-loop-v1-archive`.
- `main` is the resting branch in this repository.
- Before managed work, reconcile local `main` with `origin/main` using `python internal/workflow/repo_workflow.py sync-main`.
- Managed work starts from clean synced `main` via `python internal/workflow/repo_workflow.py start-session --agent codex --slug <task-name>`.
- Managed sessions must end with `python internal/workflow/repo_workflow.py close-session --message "<scope>: <end-state summary>"` and return the repo to `main`.
- `python internal/workflow/repo_workflow.py finalize --message "<scope>: <end-state summary>"` is only for explicit manual/review branches that are chosen up front.
- Do not accumulate accepted work indefinitely on a long-lived working branch.
- Do not branch new v2 work from archival `main`, `codex/e1-verification-substrate-entrypoints`, or `codex/closure-train-2026-03-24`.
- In this maintainer workspace, the expected public identity is `howaeri <32343362+howaeri@users.noreply.github.com>`.
- Do not bump package versions, create releases, or add publish workflows unless the task explicitly requires it.

## Continuation and resume protocol

- `docs/CORTEX_STATUS.md` is the live continuation surface for humans and new chats.
- `internal/truth/cortex_status.json` is the machine-backed source it must match.
- Before opening or resuming a seam, agents must:
  1. read `AGENTS.md`
  2. read `docs/CORTEX_STATUS.md`
  3. run `git branch --show-current`
  4. run `git status --short --untracked-files=all`
  5. compare the current repo state against the accepted baseline, work-today target, blocked moves, and subsystem/host status recorded in the registry
  6. restate the accepted baseline, current work target, blocked moves, and acknowledged noise before widening scope
- If the status doc and repo state disagree, record or resolve that drift before continuing.
- Update `internal/truth/cortex_status.json` and regenerate `docs/CORTEX_STATUS.md` in the same slice whenever any of these change:
  - accepted baseline
  - work today target
  - subsystem status
  - host shipping or conformance status
  - blocked moves
  - canonical proof bundle
  - active docs
- Never promote uncommitted local edits to accepted baseline truth.

## Required handoff block

Every final summary from an agent editing this repo should include:

- ending branch
- commit hash or `no commit`
- verification summary
- `returned to main:` yes|no
- `Status registry touched:` keys changed in `internal/truth/cortex_status.json` (or `none`)
- `Status doc regenerated:` yes|no

`PHILOSOPHY_AUDIT`
- `PHI_MINIFY`: pass|fail + one-line evidence
- `PHI_MISSION`: pass|fail + one-line evidence
- `PHI_NICHE`: pass|fail + one-line evidence
- `CUT_LIST`: what was removed, or why nothing could be removed
