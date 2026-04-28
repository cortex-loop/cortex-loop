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
- when asked where Cortex is at, lead with shipping truth, conformance truth, the current train, and the active quality/risk focus, then the bio-to-code matrix and next highest-leverage gaps; use the executive-completion denominator only for explicit denominator or progress-accounting questions

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
- Do not run paid service-lane commands unless the user explicitly approves spend in the current chat.
- Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED` or equivalent spend opt-ins on your own initiative.
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
When asked what Cortex is or how far along it is, lead with shipping truth, conformance truth, the current train, and the active quality/risk focus. Only surface the executive-completion denominator when the question is explicitly about denominator accounting or row-based progress.
Use the status registry's executive completion model and bio-to-code matrix for explicit progress-accounting answers instead of improvising a fresh denominator each time.

## Workflow

This root `AGENTS.md` is the only agent contract in the repo.
Use `python3 internal/workflow/repo_workflow.py sync-main`, `start-session`, `resume-session`, and `close-session` for normal work on clean synced `main`.
Detailed command semantics live only in `docs/internal/REPO_WORKFLOW.md`.

`start-session` refuses if any local managed session branch is not yet merged into `origin/main`. Resolve the existing branch first: `close-session --publish` to merge it, `resume-session --slug <slug>` to continue working on it, or `git branch -D` if the work is genuinely abandoned. The override `start-session --allow-stacked --stacked-reason "<text>"` is permitted only for emergency parallel work; the reason is recorded on the new session's closeout contract under `stacked_session_reason` so the override leaves an audit trail.

Do not create a second operational truth surface.
Keep fast-changing state in `internal/truth/cortex_status.json` and regenerate `docs/CORTEX_STATUS.md` when that state changes.
Do not recreate old workstream, phase-gate, correspondence, or implementation-ledger doctrine in new prose files.
For any non-no-op `close-session` or `finalize`, maintain a generated closeout contract at `.cortex/closeout_contract/<branch>/closeout.json`; scaffold it with `python3 -m internal.closeout.contract init --mode <close-session|finalize>` and re-render it after edits.
Workflow-law seams are load-bearing too: `AGENTS.md`, `docs/internal/REPO_WORKFLOW.md`, `internal/workflow/**`, `internal/closeout/**`, and `internal/Makefile` must not close as `standard`.
The workflow hard-fails if reviewed paths, residuals, hostile-review coverage, or forbidden claims are missing or stale; it revalidates reviewed-path exactness after verification as well as before it. Load-bearing closeouts must also include governing locks and at least one law-to-code completeness row.
The closeout contract is generated evidence only and does not replace operational truth.

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
- For normal managed-session checkpointing, keep using `python3 internal/workflow/repo_workflow.py close-session --message "scope: end-state summary"` and append `DOGFOOD_SIGNAL` after the normal handoff; use `close-session --publish` only when the user explicitly wants publication or resting-truth return.
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

Every substantive final summary must mirror the rendered `Final Handoff Mirror` block from the enforced closeout contract rather than paraphrasing it ad hoc, with `Fixed now`, `Intentionally deferred`, `Still underfit`, `Zeroed or stubbed terms`, `Hostile reviewer critiques`, `Claim earned now`, and `Claim still forbidden`.

`PHILOSOPHY_AUDIT`

- `PHI_MINIFY`: pass|fail + one-line evidence
- `PHI_MISSION`: pass|fail + one-line evidence
- `PHI_NICHE`: pass|fail + one-line evidence
- `CUT_LIST`: what was removed, or why nothing could be removed

## Anti-Drift

The following rules exist because each one was violated in past work and the
violation produced visible drift (work lost on side branches, stealth
main-broken state from stale fixtures, audit verdicts that never landed,
research lines that accumulated without explicit retire/promote decisions).
These rules are enforced by tests, by the workflow helper, and by the
closeout contract; they are also enforced socially by every agent reading
this file before starting work.

### Branch-slug match

The session branch slug must match the work being done. Bundling unrelated
concerns onto a single managed branch is forbidden. If a session discovers
a second concern partway through, finish the first concern, close the
session, and open a new session for the second. The
`operator_brain_capability` work was lost for ~11 days because it was
bundled onto a `claude-era-hostile-audit-and-recovery` branch whose slug
named only the audit. Bundling makes the work invisible to future agents
reading the branch list.

This rule is mechanically enforced by `start-session`: the gate refuses
when any unmerged managed session branch exists. Use `resume-session` to
continue an existing branch (the legitimate path for multi-session work
on one concern). The `--allow-stacked --stacked-reason "<text>"` override
exists for emergency parallel work and logs the reason on the new
session's closeout contract.

### Audit-verdict landing

Any audit verdict authored in a session must land its fix in the same
session if mechanically possible, or be queued explicitly as
`next_product_train` or `research_lines_under_evaluation` for the next
session if not. An audit verdict on a side branch that nobody promotes is
the same drift pattern as a research line nobody retires. The Claude-era
queue-truth dedup audit sat on a side branch for 11 days because of this
gap.

The branch-hygiene gate above mechanically catches this pattern too: an
audit verdict that lands on a managed session branch and is not merged
or resumed will block the next `start-session` until resolved.

### Research line management

Every research line that has produced code or doctrine must be in exactly
one of four states at session close:

- `earned` — landed on main, in the bio_to_code matrix, with proof surfaces.
- `queued` — named in `internal/truth/cortex_status.json::next_product_train`.
- `retired` — archived via `internal/archive/manifest.json::retained_evidence_refs`
  with a remote `archive/*` ref preserving the work.
- `under-evaluation` — named in
  `internal/truth/cortex_status.json::research_lines_under_evaluation` with
  an explicit `stage`, `summary`, `code_refs`, and `next_step`. This slot
  exists for research that does not yet fit one of the other three states.

Research lines orphaned outside these four states are forbidden. If you
introduce a research line, you must classify it before close-session.

### Fixture timestamps

Test fixtures that exercise freshness-bearing logic
(`HostReliabilityPrior`, `OfflineSupportPublication.host_reliability_prior`,
brain-capability observation accumulators when they earn their seam, etc.)
MUST use a runtime helper such as
`tests.experimental._aux_test_support.fresh_validated_at_iso()` for the
`last_validated_at` field. Hardcoded ISO-8601 timestamps drift past TTL
as wall-clock time advances and silently break tests. Hardcoded
timestamps are permitted only where the test explicitly wants stale or
TTL-expired data (e.g. `"2000-01-01T00:00:00+00:00"`).

### Closeout contract postmortem guards

The closeout contract validates against the procedural shortcuts
identified in the V2 communication bridge postmortem. Specifically: a
closeout payload that introduces an `agent_loop_guard` subobject must
have `require_full_communication_closure: true` and may not have
`allow_blocked: true`; a closeout that claims "full V2 communication
closure", "fully model-visible", or "live watchlist passed" without an
`agent_loop_guard` subobject + a passing report file is rejected. Do not
disable, opt out of, or work around these guards — they exist because
their absence let real work be checkpointed before the live evidence
that would have graduated it.

### Live-evidence vs structural-evidence

Earning a seam structurally (deterministic tests, doctrine update, status
registry truth) is necessary but not sufficient for shipping claims about
model-side lift. Any claim that "Cortex improves model output" or "the
mechanism converts model failures" requires live evidence: a real model
run on a real fixture or task, with the comparison pinned. Structural
earn lands the seam; live earn graduates the claim. Do not conflate the
two.
