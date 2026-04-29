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
and fill the optional `Dogfood:*` rows that `grid` emits; use `--publish`
only when explicitly requested. For a full dogfood closeout, run
`python3 -m lab.codex_dogfood_session close` and persist the handoff,
verification, and dogfood signal values inside Cortex Mission Reflection.

Kill rule: cut the mode if two dogfood sessions in a row fail to change a
concrete design or implementation decision beyond the normal workflow.

## Handoff

**Cortex Mission Reflection.** Every chat ends with Cortex Mission
Reflection as the single closure artifact. The point is mission
reflection, not status recitation. The agent must prove it
understands Cortex as a post-training executive-function layer and is
judging whether the turn advanced that mission. Normal response prose
may precede the grid; nothing closure-shaped may follow it or appear
before it.

The grid is generated by:
```
python3 internal/workflow/repo_workflow.py grid
```
It renders as exactly one two-column markdown table under the
`## Cortex Mission Reflection` header. Required rows:

- `Repo: State` — branch, worktree, closeout, drift in one compact cell.
- `Repo: Gates` — `reflection-check` verdict; failures/gaps only when present.
- mission rows: `Mission: Cortex target`, `Mission: Boundary judgment`,
  `Mission: Theory of improvement`, `Mission: Model I/O path`
- reflection/evidence rows: `Reflection: Plan vs actual`, `Reflection:
  Quality judgment`, `Reflection: Iteration evidence`, `Evidence:
  Earned`, `Evidence: Not earned / forbidden`, `Decision: Next
  ownership move`
- `Closure: Metadata`; optional `Dogfood:*` rows when Codex App dogfood
  mode is active; `Verdict`

Do not emit fixed dashboard rows in the end-of-chat artifact. Rows such
as `Progress:*`, `bio_to_code matrix`, hosts, shipping default, current
train, next train, and research-lines counts are stale closure shape.
Registry facts may be cited inside mission reflection only when they
support an argument.

**Workflow: paste the skeleton, fill brackets in place.** The agent
runs `grid`, pastes the generated markdown skeleton into the chat,
then edits the skeleton in place. Each Cortex Mission Reflection row
must replace the `mission reflection —` template with at least 120
characters of causal, repo-grounded judgment and at least one citation
to `docs/CORTEX.md`, `internal/truth/cortex_status.json`, `cortex/**`,
`tests/**`, or a `CORTEX_V2_*` packet. `Closure: Metadata` must replace
the `closure metadata —` template with branch, commit/no commit,
verification, returned-to-main, and registry/doc-regeneration facts.
Do not paste a verbatim skeleton with brackets remaining; do not write
a separate closure section outside the grid.

**No-mimicry rule.** Composing markdown that resembles graph content
but is not actual `grid` command output is a violation. The skeleton
is verbatim from the command; the agent's edits stay inside the
skeleton. Ad-hoc audit-shaped markdown headers (e.g. an "Audit
Findings" block written from scratch, or a separate metadata block
following the grid) do not satisfy this contract.

**Chat-boundary enforcement (Claude Code).** A Stop hook configured
at `.claude/settings.json` runs `.claude/hooks/cortex_grid_stop_hook.py`
on turn-completion. The hook reads the assistant's most recent message
from the transcript JSONL, runs `grid` itself, and blocks the stop
when any of the following hold:

1. Required one-table shape missing: `## Cortex Mission Reflection`,
   exactly one `| Field | Value |` table header, exactly one
   `|---|---|` separator, no `###` subsection inside the grid, and
   all required mission-reflection row labels.
2. Closure-shaped substrings (`Ending branch`, `Verification summary`,
   `Fixed now`, `Claim earned now`, `Status registry touched`,
   `Closure: Metadata`) appear in prose **before** the grid header.
3. Any stale dashboard row is present (`Progress:*`, `bio_to_code
   matrix`, hosts, shipping default, current train, next train, or
   research-lines as fixed rows).
4. Any Cortex Mission Reflection row still contains the literal
   `mission reflection —` template substring, is shorter than the
   meaningful threshold, or lacks a repo-grounding citation.
5. `Closure: Metadata` still contains `closure metadata —` or `<fill`.
6. `reflection-check --json` returns verdict `FAIL`.

When blocked, Claude Code re-prompts the agent with the reason as
feedback context; the agent generates another response and the hook
re-runs all gates. **The hook does not short-circuit on
`stop_hook_active`** — every stop attempt re-checks every gate, so
persistent non-compliance keeps blocking. The hook fails open (allows
the stop with a stderr diagnostic) on infrastructure failures only:
missing transcript, malformed hook input, or `grid` /
`reflection-check` command crash. Hooks cannot append to or modify
the assistant message; the agent must paste; the hook validates the
paste happened correctly.

**Codex App chat-boundary enforcement.** Codex App for Mac uses
repo-local `.codex/config.toml` (`[features].codex_hooks = true`) and
`.codex/hooks/cortex_mission_reflection_stop_hook.py`. The hook reads
`last_assistant_message`, runs `grid`/`reflection-check`, applies
`internal/workflow/mission_reflection.py`, and blocks on the same graph
contract as Claude Code. Before Cortex product work in Codex App, run
`python3 internal/workflow/repo_workflow.py codex-app-hook-health`; if
it fails, fix hook/config/runtime health or use a healthy gated surface.

**Codex fallback surfaces.** Codex surfaces that do not load repo-local
hooks still run `grid`, fill it in place, validate with
`python3 internal/workflow/repo_workflow.py grid-validate --stdin`, and
record non-no-op closeout evidence in `mission_reflection_graph`. This
fallback is session-boundary evidence, not chat-boundary parity.

**Hook health / seamless handoff readiness.** Before product work after
doctrine changes, run `python3 internal/workflow/repo_workflow.py
hook-health`, `python3 internal/workflow/repo_workflow.py
codex-app-hook-health`, and `python3 internal/workflow/repo_workflow.py
cleanup-report`. Product work should not start while hook health fails
or cleanup-report shows dangling worktrees, dirty main, unsynced main,
doc-generation drift, or missing graph validation.

**Grid auto-loop rule.** On turn verdict `FAIL` (any mechanical gate
failed) or unresolved gaps that cannot be moved to
`intentionally_deferred` with rationale, the agent MUST continue
working in the same chat until the grid clears. Do not close-session,
finalize, or publish on `FAIL`. The `Verdict` row separates turn verdict
from close-session eligibility; a no-closeout turn can pass without
claiming it is eligible to close-session. Handwave answers (e.g.
"fine", "looks good", "no issues") are rejected by
`reflection-check`'s substantive-content rule on close-session; the
Stop hook raises the per-turn floor by requiring mission-aware, cited,
120-character row answers before Claude Code can stop.

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
