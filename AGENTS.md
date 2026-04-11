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
- when asked where Cortex is at, answer with the full-executive completion percent versus the shippable threshold first, then the bio-to-code matrix, then the next highest-leverage gaps

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
Use the status registry's executive completion model and bio-to-code matrix for progress answers instead of improvising a fresh denominator each time.

## Workflow

This root `AGENTS.md` is the only agent contract in the repo.
Use `python3 internal/workflow/repo_workflow.py sync-main`, `start-session`, and `close-session` for normal work on clean synced `main`.
Detailed command semantics live only in `docs/internal/REPO_WORKFLOW.md`.

Do not create a second operational truth surface.
Keep fast-changing state in `internal/truth/cortex_status.json` and regenerate `docs/CORTEX_STATUS.md` when that state changes.
Do not recreate old workstream, phase-gate, correspondence, or implementation-ledger doctrine in new prose files.

## Codex App Dogfood Mode

Surface: `lab`
Executive Benefit: collect bounded self-hosting evidence during real repo work in Codex App without promoting Codex App into product truth.
Why this beats direct product work now: it lets real managed-session work test continuity, blocker surfacing, uncertainty/brake, and truthful closure on the operator surface we are actively using.

Governing principle: dogfood evidence can challenge Cortex law, but it stays watchlist-only until a separate product seam re-earns shipped proof.
Executive skill: branch continuity, blocker surfacing, uncertainty-aware braking, and truthful closure during real repo work.
Product metric: `repair-conversion improvement on the bounded OpenAI verified-work repair bundle`
Guardrail: current-worktree dogfood only; no automatic `make live-codex-dogfood` run and no product-truth changes from chat triggers.
Kill rule: cut the mode if two dogfood sessions in a row fail to change a concrete design or implementation decision beyond the normal workflow.

Exact Codex App chat triggers:

- `start cortex dogfood mode`
- `refresh cortex dogfood mode`
- `stop cortex dogfood mode`
- `show cortex dogfood status`

Trigger handling:

- `start cortex dogfood mode`: run `python3 -m lab.codex_dogfood_session activate` and adopt the printed contract for the current chat/session only.
- `refresh cortex dogfood mode`: run `python3 -m lab.codex_dogfood_session refresh` and replace the current chat/session contract with the refreshed current-worktree contract.
- `stop cortex dogfood mode`: run `python3 -m lab.codex_dogfood_session close --abort` unless the user explicitly asks for a full dogfood closeout with a final signal block.
- `show cortex dogfood status`: run `python3 -m lab.codex_dogfood_session status`.

Activation rules:

- Activate only on a managed `codex/...` session branch.
- Refuse activation on clean `main` and give only the minimum corrective workflow: `python3 internal/workflow/repo_workflow.py sync-main` then `python3 internal/workflow/repo_workflow.py start-session --agent codex --slug task-name`.
- Refuse activation on any non-session branch or dirty unsupported state until the repo is reconciled.
- Do not run `make live-codex-dogfood` automatically from these chat triggers.

When dogfood mode is active:

- Keep the normal repo workflow and handoff unchanged.
- Dogfood mode is bound to the current worktree contract until refreshed.
- Treat every dogfood artifact and helper message as current-worktree `lab` / `watchlist` evidence, never as product truth.
- For normal managed-session closure, keep using `python3 internal/workflow/repo_workflow.py close-session --message "scope: end-state summary"` and append `DOGFOOD_SIGNAL` after the normal handoff.
- If the user asks for a full dogfood closeout, run `python3 -m lab.codex_dogfood_session close` and persist the normal handoff summary, verification summary, and the final `DOGFOOD_SIGNAL`.
- Append this exact block after the normal final handoff:

`DOGFOOD_SIGNAL`
`continuity_helped: yes|no`
`blocker_surfaced: yes|no`
`uncertainty_or_brake_used: yes|no`
`truthful_closure: yes|no`
`cortex_changed_next_action: yes|no`
`note: <one sentence>`

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
