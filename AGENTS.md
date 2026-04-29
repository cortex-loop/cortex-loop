# Cortex v2 Repo Agent Contract

This file applies to agents editing this repository.
It does not define runtime policy for downstream Cortex users.

## Agent Briefing

Read this first, every session.

For repo/product judgments in this repository, do not default to affirming
the user's ideas and do not default to criticizing them. Do not let prior
conversation style, model personality, or training-time preferences decide
Cortex positions. Use only the repo's recorded goals and current proof.

Form positions from observable repo truth: `docs/CORTEX.md` for Cortex
identity and narrative fit; the V2 packet docs (`docs/CORTEX_V2_*.md`)
for packet law; `internal/truth/cortex_status.json` for current
operational truth; and `cortex/**` plus `tests/**` for implemented
behavior and proof.

If you lack doctrine-and-code grounding for a repo position, you do not
have that position yet. Read the specific missing surface, or say "I
don't know yet; I need to check X." Do not manufacture an answer from the
user's latest framing or generic priors.

Agreement and disagreement are both acceptable when earned by evidence.
Unearned agreement and ungrounded criticism are both failures.

## Mission

Cortex is the shipped rich multi-host executive layer in this repository.
The full identity statement, the V1 → V2 lessons, the math-to-code map,
and the implementation discipline live in `docs/CORTEX.md`. This file is
the agent contract; `docs/CORTEX.md` is the canonical narrative.

Cortex should feel like an installable executive layer you can put around
a model or CLI to add executive function, not like a pile of support
machinery.

Lab, eval, and archive surfaces exist to falsify or prove product seams,
not to become the product.

Work like a first-principles AI-systems researcher:

- reason from governing principles before host quirks
- falsify weak assumptions instead of defending them
- choose seams by product lift, not by local neatness
- steal executive skills from systems that already work, especially
  human executive function, then translate them into concrete Cortex law
- cut work that does not improve the shipped executive layer or directly
  unblock proving it

When asked where Cortex is at, follow `internal/truth/cortex_status.json::identity.answering_stance`: lead with shipping truth, conformance truth, the current train, and the active quality/risk focus, then summarize the bio-to-code matrix and the next highest-leverage gaps. Use the executive-completion denominator only for explicit denominator or progress-accounting questions.

## Authority

Authority is **scoped**, not ordinal. Each surface owns a dimension; one
does not override another, and conflicts resolve by which dimension the
question lives in.

- `docs/CORTEX.md` — identity, narrative, product-fit. May reject work as
  off-mission. May not authorize breaking packet law, workflow law, or
  current-state truth.
- `docs/CORTEX_V2_CORE_2.md`, `docs/CORTEX_V2_SRE_2.md`,
  `docs/CORTEX_V2_AUX_2.md` — the formal V2 packet law and math.
- `internal/truth/cortex_status.json` — current operational truth and
  registry data.
- `docs/CORTEX_STATUS.md` — the generated human view of the registry.
- `docs/internal/REPO_WORKFLOW.md` — workflow mechanics and command
  semantics.

Bootstrap reads, in order, every session:

1. `AGENTS.md` (this file)
2. `docs/CORTEX.md`
3. `docs/CORTEX_STATUS.md`
4. `git branch --show-current`
5. `git status --short --untracked-files=all`

`internal/truth/cortex_status.json` is the single operational truth
surface. `docs/CORTEX_STATUS.md` is the generated human-readable view.
`docs/archive/` and the v1 archive repo are evidence only.

If authority surfaces disagree, resolve the conflict before widening
scope.

## Non-Negotiables

- Do not turn Cortex into a narrow single-model shell.
- Do not flatten host differences into fake runtime uniformity.
- Do not let lab, eval, archive, or governance surfaces become Cortex
  product identity.
- Do not move active executive policy into the core.
- Do not let shipping truth collapse conformance truth.
- Do not run paid service-lane commands unless the user explicitly approves spend in the current chat.
- Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED` or equivalent spend opt-ins on your own initiative.
- Do not carry forward v1 mechanisms or host hacks without re-earning
  them under the packet.
- Do not claim product progress unless shipped runtime behavior changed
  or a direct product blocker was removed.
- Keep repo text neutral, technical, and free of client-specific or
  persona-branded language.

## Working Mode

Favor the smallest change that solves the actual problem. Prefer
Cortex-specific mechanisms over generic bloat or v1 carryover. The
implementation discipline lives in `docs/CORTEX.md` §6; the closeout
contract's `north_light_audit` and `governing_locks` enforce it
structurally.

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

If the same divergence repeats across brains, challenge Cortex law before
piling on host-specific fixes. Prefer the smallest runnable seam that
produces falsifiable product evidence. Treat the current math as binding
landing law until live evidence proves it wrong or incomplete; then
revise the law explicitly instead of silently drifting in code. Use the
status registry's executive completion model and bio-to-code matrix for
explicit progress-accounting answers instead of improvising a fresh
denominator each time.

## Workflow

This root `AGENTS.md` is the only agent contract in the repo.

Use `python3 internal/workflow/repo_workflow.py sync-main`, `start-session`,
`resume-session`, and `close-session` for normal work on clean synced
`main`. Detailed command semantics live only in
`docs/internal/REPO_WORKFLOW.md`.

`start-session` refuses if any local managed session branch is not yet
merged into `origin/main`. Resolve the existing branch first:
`close-session --publish` to merge it, `resume-session --slug <slug>` to
continue working on it, or `git branch -D` if the work is genuinely
abandoned. The override
`start-session --allow-stacked --stacked-reason "<text>"` is permitted
only for emergency parallel work; the reason is recorded on the new
session's closeout contract under `stacked_session_reason` so the
override leaves an audit trail.

Do not create a second operational truth surface. Keep fast-changing
state in `internal/truth/cortex_status.json` and regenerate
`docs/CORTEX_STATUS.md` when that state changes. Regenerate
`docs/CORTEX.md` with `python3 internal/truth/generate_cortex_doc.py`
when the math-to-code map or current state changes. Do not recreate old
workstream, phase-gate, correspondence, or implementation-ledger doctrine
in new prose files.

For any non-no-op `close-session` or `finalize`, maintain a generated
closeout contract at `.cortex/closeout_contract/<branch>/closeout.json`;
scaffold it with
`python3 -m internal.closeout.contract init --mode <close-session|finalize>`
and re-render it after edits. Workflow-law seams are load-bearing too:
`AGENTS.md`, `docs/CORTEX.md`, `docs/internal/REPO_WORKFLOW.md`,
`internal/workflow/**`, `internal/closeout/**`, and `internal/Makefile`
must not close as `standard`.

The workflow hard-fails if reviewed paths, residuals, hostile-review coverage, or forbidden claims are missing or stale; it revalidates reviewed-path exactness after verification as well as before it. Load-bearing closeouts must also include governing locks and at least one law-to-code completeness row. The closeout contract is generated evidence only and does not replace operational truth.

## Codex App Dogfood Mode

Surface: `lab`. Bounded self-hosting evidence collected during real repo
work in Codex App; never promotes Codex App into product truth. Stays
watchlist-only until a separate product seam re-earns shipped proof.

Chat triggers map to lab subcommands:

- `start cortex dogfood mode` → `python3 -m lab.codex_dogfood_session activate`
- `refresh cortex dogfood mode` → `python3 -m lab.codex_dogfood_session refresh`
- `stop cortex dogfood mode` → `python3 -m lab.codex_dogfood_session close --abort`
  (use `close` instead if the user explicitly asks for a full dogfood
  closeout with a final signal block)
- `show cortex dogfood status` → `python3 -m lab.codex_dogfood_session status`

Activation requires a managed `codex/...` session branch. On clean `main`,
refuse and give only the minimum corrective workflow:
`python3 internal/workflow/repo_workflow.py sync-main` then
`python3 internal/workflow/repo_workflow.py start-session --agent codex --slug task-name`.
Do not run `make live-codex-dogfood` automatically from chat triggers; it
is current-worktree-only.

When dogfood mode is active, keep the normal repo workflow and handoff
unchanged. Treat every dogfood artifact as current-worktree
`lab` / `watchlist` evidence. For routine checkpointing use
`python3 internal/workflow/repo_workflow.py close-session --message "scope: end-state summary"`
and append `DOGFOOD_SIGNAL` after the normal handoff; use `--publish` only
when explicitly requested. For a full dogfood closeout, run
`python3 -m lab.codex_dogfood_session close` and persist the handoff
summary, verification summary, and the `DOGFOOD_SIGNAL`.

Append this exact block after the normal final handoff:

`DOGFOOD_SIGNAL`
`continuity_helped: yes|no`
`blocker_surfaced: yes|no`
`uncertainty_or_brake_used: yes|no`
`truthful_closure: yes|no`
`cortex_changed_next_action: yes|no`
`note: <one sentence>`

Kill rule: cut the mode if two dogfood sessions in a row fail to change a
concrete design or implementation decision beyond the normal workflow.

## Handoff

Every chat ends with the Cortex Repo Hygiene Grid. The grid is produced
unconditionally by:

```
python3 internal/workflow/repo_workflow.py grid
```

The grid auto-detects whether work was performed in the session
(tracked-file changes since session start). When no work was performed,
it emits the always-on blocks: state snapshot, Cortex progress
dashboard, and goals-analysis prompts. When work was performed, it
additionally emits the mechanical reflection-check verdict, the
work-reflection prompts, and a Loop Decision.

**Grid auto-loop rule.** If the Loop Decision is `FAIL` (any mechanical
gate failed) or has unresolved gaps that cannot be moved to
`intentionally_deferred` with rationale, the agent MUST continue working
in the same chat until the grid clears. Do not close-session, finalize,
or publish on `FAIL`. The grid produces its verdict from mechanical
state, not from an agent's self-report; this is the structural fix that
replaces the v1 self-rated handoff ritual.

The grid's Goals Analysis section requires a substantive answer with at
least one repo-surface citation (`docs/CORTEX.md`, a
`cortex_status.json` field, a `cortex/**` path, a V2 packet section, a
test file). Handwave answers (e.g. "fine", "looks good", "no issues")
are rejected by `reflection-check`'s substantive-content rule.

Every final summary must include the grid output plus the standard
metadata block:

- ending branch
- commit hash or `no commit`
- verification summary
- `returned to main:` yes|no
- `Status registry touched:` keys changed in
  `internal/truth/cortex_status.json` or `none`
- `Status doc regenerated:` yes|no
- `CORTEX.md regenerated:` yes|no (when `math_to_code_map`,
  `bio_to_code_matrix`, or current-state-bearing fields changed)

Every substantive final summary must mirror the rendered
`Final Handoff Mirror` block from the enforced closeout contract rather
than paraphrasing it ad hoc, with `Fixed now`, `Intentionally deferred`,
`Still underfit`, `Zeroed or stubbed terms`, `Hostile reviewer critiques`,
`Claim earned now`, and `Claim still forbidden`.

## Anti-Drift

Each rule below was earned by losing work to a specific drift pattern;
the full V1 → V2 history is in `docs/CORTEX.md` §3. The rules are
enforced by tests, by the workflow helper, and by the closeout contract.

### Branch-slug match

The session branch slug must match the work being done. Bundling
unrelated concerns onto a single managed branch is forbidden. If a
session discovers a second concern partway through, finish the first,
close the session, and open a new session for the second.

Mechanically enforced by `start-session`: the gate refuses when any
unmerged managed session branch exists. Use `resume-session` to continue
an existing branch (the legitimate path for multi-session work on one
concern). The `--allow-stacked --stacked-reason "<text>"` override
exists for emergency parallel work and logs the reason on the new
session's closeout contract.

### Audit-verdict landing

Any audit verdict authored in a session must land its fix in the same
session if mechanically possible, or be queued explicitly as
`next_product_train` or `research_lines_under_evaluation` for the next
session if not. An audit verdict on a side branch that nobody promotes
is the same drift pattern as a research line nobody retires. The
branch-hygiene gate catches this pattern too.

### Research line management

Every research line that has produced code or doctrine must be in
exactly one of four states at session close:

- `earned` — landed on main, in the bio_to_code matrix, with proof
  surfaces.
- `queued` — named in
  `internal/truth/cortex_status.json::next_product_train`.
- `retired` — archived via
  `internal/archive/manifest.json::retained_evidence_refs` with a remote
  `archive/*` ref preserving the work.
- `under-evaluation` — named in
  `internal/truth/cortex_status.json::research_lines_under_evaluation`
  with an explicit `stage`, `summary`, `code_refs`, and `next_step`.

Research lines orphaned outside these four states are forbidden.

### Fixture timestamps

Test fixtures that exercise freshness-bearing logic
(`HostReliabilityPrior`,
`OfflineSupportPublication.host_reliability_prior`, brain-capability
observation accumulators, etc.) MUST use a runtime helper such as
`tests.experimental._aux_test_support.fresh_validated_at_iso()` for the
`last_validated_at` field. Hardcoded ISO-8601 timestamps drift past TTL
as wall-clock time advances and silently break tests. Hardcoded
timestamps are permitted only where the test explicitly wants stale or
TTL-expired data (e.g. `"2000-01-01T00:00:00+00:00"`).

### Closeout contract postmortem guards

The closeout contract validates against the procedural shortcuts
identified in the V2 communication bridge postmortem. A closeout payload
that introduces an `agent_loop_guard` subobject must have
`require_full_communication_closure: true` and may not have
`allow_blocked: true`. A closeout that claims "full V2 communication
closure", "fully model-visible", or "live watchlist passed" without an
`agent_loop_guard` subobject + a passing report file is rejected. Do not
disable, opt out of, or work around these guards.

### Closed-loop drift (connectivity requirement)

Every Cortex change must trace a path from the change to the model's
input or output. If the path is empty, the work is monitoring or
instrumentation and belongs on `lab` or `experimental` surface, not
`product`. See `docs/CORTEX.md` §3 for the full V1 → V2 lesson.

### Live-evidence vs structural-evidence

Earning a seam structurally (deterministic tests, doctrine update,
status registry truth) is necessary but not sufficient for shipping
claims about model-side lift. Any claim that "Cortex improves model
output" or "the mechanism converts model failures" requires live
evidence: a real model run on a real fixture or task, with the
comparison pinned. Structural earn lands the seam; live earn graduates
the claim. Do not conflate the two.
