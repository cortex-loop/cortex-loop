# Cortex v2 Repo Agent Contract

This file applies to agents editing this repository.
It does not define runtime policy for downstream Cortex users.

## Mission

Cortex is the shipped rich multi-host executive layer in this repository.
The goal is not to ship diagnostics, train loops, graders, workflow ledgers, or governance records.
Cortex should feel like an installable executive layer you can put around a model or CLI to add executive function, not like a pile of support machinery.

OpenAI-first shipping does not redefine Cortex identity.
Claude, Gemini, and reference remain part of Cortex conformance truth even when shipping truth stays narrower.
Lab, eval, and archive surfaces exist to falsify or prove product seams, not to become the product.

Work like a first-principles AI-systems researcher:

- reason from governing principles before host quirks
- falsify weak assumptions instead of defending them
- choose seams by product lift, not by local neatness
- steal executive skills from systems that already work, especially human executive function, then translate them into concrete Cortex law
- cut work that does not improve the shipped executive layer or directly unblock proving it

## Authority

Active authority order:

1. `docs/CORTEX_V2_CORE_2.md`
2. `docs/CORTEX_V2_SRE_2.md`
3. `docs/CORTEX_V2_AUX_2.md`
4. `internal/truth/cortex_status.json`
5. `docs/CORTEX_STATUS.md`
6. `docs/internal/REPO_WORKFLOW.md`

Bootstrap every session with:

1. `AGENTS.md`
2. `docs/CORTEX_STATUS.md`
3. `git branch --show-current`
4. `git status --short --untracked-files=all`

`internal/truth/cortex_status.json` is the single operational truth.
`docs/CORTEX_STATUS.md` is the generated human-readable view.
`docs/archive/` and the v1 archive repo are evidence only.

If authority surfaces disagree, resolve the conflict before widening scope.

## Non-Negotiables

- Do not turn Cortex into a narrow single-model shell.
- Do not flatten host differences into fake runtime uniformity.
- Do not let lab, eval, archive, or governance surfaces become Cortex product identity.
- Do not move active executive policy into the core.
- Do not let shipping truth collapse conformance truth.
- Do not carry forward v1 mechanisms or host hacks without re-earning them under the packet.
- Do not claim product progress unless shipped runtime behavior changed or a direct product blocker was removed.
- Keep repo text neutral, technical, and free of client-specific or persona-branded language.

## Working Mode

Run this decision loop before editing, before finalizing, and before handoff:

1. `PHI_MINIFY` — Is this the smallest change that solves the actual problem?
2. `PHI_MISSION` — Does this improve Cortex as a rich multi-host executive layer?
3. `PHI_NICHE` — Is this the right Cortex-specific mechanism, not generic bloat or v1 carryover?

Every seam must declare:

- `Surface:` `product | experimental | lab | internal`
- `Executive Benefit:` the direct shipped-product lift or blocker removed
- `Why this beats direct product work now:` one sentence

Every load-bearing seam must also lock:

- governing principle
- executive skill being added, sharpened, or repaired
- product metric
- guardrail
- kill rule

When a seam changes Cortex law, keep these truths distinct:

- `Cortex truth`
- `brain-wiring truth`
- `conformance truth`
- `shipping truth`

If the same divergence repeats across brains, challenge Cortex law before piling on host-specific fixes.
Prefer the smallest runnable seam that produces falsifiable product evidence.
Treat the current math as binding landing law until live evidence proves it wrong or incomplete; then revise the law explicitly instead of silently drifting in code.
When asked what Cortex is or how far along it is, state the full executive denominator first, then distinguish shipping truth, conformance truth, and the current train.

## Workflow

This root `AGENTS.md` is the only agent contract in the repo.
Use `python3 internal/workflow/repo_workflow.py sync-main`, `start-session`, and `close-session` for normal work on clean synced `main`.
Detailed command semantics live only in `docs/internal/REPO_WORKFLOW.md`.

Do not create a second operational truth surface.
Keep fast-changing state in `internal/truth/cortex_status.json` and regenerate `docs/CORTEX_STATUS.md` when that state changes.
Do not recreate old workstream, phase-gate, correspondence, or implementation-ledger doctrine in new prose files.

## Handoff

Every final summary must include:

- ending branch
- commit hash or `no commit`
- verification summary
- `returned to main:` yes|no
- `Status registry touched:` keys changed in `internal/truth/cortex_status.json` or `none`
- `Status doc regenerated:` yes|no

`PHILOSOPHY_AUDIT`

- `PHI_MINIFY`: pass|fail + one-line evidence
- `PHI_MISSION`: pass|fail + one-line evidence
- `PHI_NICHE`: pass|fail + one-line evidence
- `CUT_LIST`: what was removed, or why nothing could be removed
