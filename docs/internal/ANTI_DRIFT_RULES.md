# Anti-Drift Rules

Surface: internal

These rules were earned by losing work to specific V1 to V2 drift patterns.
They are enforced by tests, workflow helpers, or closeout contracts. `AGENTS.md`
points here so the first-read agent contract can stay focused on orientation
instead of carrying the full operational history.

## Branch-Slug Match

Drift pattern: unrelated concerns bundled onto one managed branch became a
de facto side trunk.

Rule: the session branch slug must match the work being done. If a session
discovers a second concern, finish or preserve the first concern, then open a
separate session for the second. Emergency stacked work must record a
`stacked_session_reason`.

## Audit-Verdict Landing

Drift pattern: audit findings authored on a side branch did not land their
fixes and silently became orphaned doctrine.

Rule: an audit verdict authored in a session lands its fix in the same session
when mechanically possible. If not, it is explicitly queued in
`internal/truth/cortex_status.json::next_product_train` or
`research_lines_under_evaluation`.

## Research Line Management

Drift pattern: research branches produced code or doctrine but never became
earned, queued, retired, or under-evaluation truth.

Rule: every research line that has produced code or doctrine must end in
exactly one state at session close:

- `earned` — landed on main, in the bio-to-code matrix, with proof surfaces.
- `queued` — named in `internal/truth/cortex_status.json::next_product_train`.
- `retired` — preserved through `internal/archive/manifest.json` and an
  `archive/*` ref.
- `under-evaluation` — named in
  `internal/truth/cortex_status.json::research_lines_under_evaluation` with
  stage, summary, code refs, and next step.

## Fixture Timestamps

Drift pattern: freshness-bearing tests used hardcoded timestamps that aged past
TTL and failed as wall-clock time advanced.

Rule: tests exercising freshness-bearing logic use runtime helpers such as
`tests.experimental._aux_test_support.fresh_validated_at_iso()` for
`last_validated_at`. Hardcoded timestamps are allowed only when the test wants
explicit stale or TTL-expired data, such as `2000-01-01T00:00:00+00:00`.

## Closeout Contract Postmortem Guards

Drift pattern: V2 communication-bridge closeouts claimed full model-visible or
live-watchlist closure without the loop guard evidence that would make the
claim true.

Rule: closeout payloads that introduce `agent_loop_guard` must require full
communication closure and may not allow blocked closure. Claims such as "full
V2 communication closure", "fully model-visible", or "live watchlist passed"
require the guard object and a passing report file.

## Closed-Loop Connectivity

Drift pattern: monitoring and instrumentation work was treated as Cortex
product progress even when it never changed model input or output.

Rule: every Cortex product change traces a path from the change to the model's
input or output. If the path is empty, the work is lab, experimental, or
workflow support, not product Cortex.

## Fixture-To-Law Product Spine

Drift pattern: a hard fixture or task domain became the thing optimized,
instead of the broad executive capability the fixture was supposed to witness.

Rule: fixtures falsify Cortex; they do not define Cortex. Product seams
touching `cortex/**` must translate the motivating evidence into the product
spine: executive capability, state-law path, enforcement decision, host action,
model I/O effect, fixture boundary, and non-fixture controls. Product code may
not branch on lab fixture identities or hidden verifier terms. Those details
belong in `lab/**`, `tests/**`, recon docs, or the closeout fixture boundary.

## Live Evidence Versus Structural Evidence

Drift pattern: deterministic tests, doctrine updates, and structural wiring
were promoted into claims that Cortex improved model behavior.

Rule: structural evidence can land a seam, but claims that Cortex improves
model output require live evidence: a real model run on a real fixture or task,
with the comparison pinned. Structural earn and live earn stay separate.
