# Cortex v2 Repo Agent Contract

This file applies to agents editing this repository.
It does not define runtime policy for downstream Cortex users.

## Required decision loop

Run this loop three times: before editing, before finalizing a change, and before handoff.

1. `PHI_MINIFY` — Is this the smallest change that solves the actual problem?
2. `PHI_MISSION` — Does this improve the v2 mission directly: better output, better agency/memory/control, lifecycle-first execution, and a tiny integrity core?
3. `PHI_NICHE` — Is this the right mechanism for this repository, or generic bloat / v1 carryover?

If any answer is no, redesign or cut scope.

## Hard stops

- Do not reintroduce v1 stop-centered architecture by inertia.
- Do not expand the integrity microkernel beyond commitments, provenance, blockedness, and hard boundaries without explicit evidence.
- Do not move active executive policy into the core.
- Do not let AUX become a hidden second truth court.
- Do not flatten host differences just to preserve a fake uniform runtime.
- Do not treat the v1 archive as active authority.
- Do not add math that has no operational consequence.
- Do not add tunable weights unless changing them would plausibly change runtime behavior in a legible way.

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

Implementation/workflow documents:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/V1_CODE_PORT_DETERMINATION.md`

Supporting implementation authority (audit surface, not architectural authority):
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

Authority order:

1. Core
2. SRE
3. AUX
4. Implementation master plan
5. Phase gates (closure truth only; does not override packet meaning or seam order)
6. V1 code-port determination
7. Math-to-code correspondence (traceability only; does not override packet meaning or seam order)

If those documents disagree, fix the disagreement before widening scope.

## Archive authority

The v1 archive is evidence and reference only.
It is not normative authority for what v2 should be.

Use the archive only for:

- battle-proven narrow primitives,
- historical validation/evidence patterns,
- host/runtime behavior reference,
- and examples of what not to rebuild.

If a v1 mechanism is being carried over, re-earn it under the v2 packet instead of assuming continuity.

## Design guardrails for v2

- Lifecycle-first: organize around real host lifecycle/orchestration events.
- Packet-first internally: keep typed internal semantics.
- Host-native externally: prefer the strongest native host surface that exists.
- Executive-first: active intelligence belongs in SRE or later executive realizations, not in the core.
- Microkernel-limited: the hard center stays tiny.
- Contradiction-preserving: mixed, blocked, degraded, and host-specific outcomes must remain explicit.
- Neutral-by-default: the executive should not intervene just to justify itself.
- First host vertical slice before broad multi-host rollout.
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
- If you change the intended v1 carryover boundary, update `V1_CODE_PORT_DETERMINATION.md` in the same slice.

## Phase gate discipline

- `docs/CORTEX_V2_PHASE_GATES_2.md` is the live gate ledger for cross-seam closure conditions that are broader than one correspondence row.
- If a handoff claims a phase or sub-phase is `landed`, recheck the relevant gate rows in `docs/CORTEX_V2_PHASE_GATES_2.md` in the same turn.
- A phase may not be marked `landed` if a relevant gate row remains `open`, `partial`, or `drifted` unless the handoff explicitly keeps the phase `partial` or `blocked`.
- Correspondence truth and phase-gate truth are distinct. Passing one does not silently satisfy the other.

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
- Keep phase-specific subagent allowances and restrictions in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`.

## Git and workflow

- Canonical development repo: `github.com/cortex-loop/cortex-loop`.
- Canonical archive repo: `github.com/cortex-loop/cortex-loop-v1-archive`.
- Before editing, reconcile local `main` with `origin/main`.
- Do not develop on `main`; create an explicit branch with the `codex/` prefix.
- In this maintainer workspace, the expected public identity is `howaeri <32343362+howaeri@users.noreply.github.com>`.
- Do not bump package versions, create releases, or add publish workflows unless the task explicitly requires it.

## Required handoff block

Every final summary from an agent editing this repo should include:

- ending branch
- commit hash or `no commit`
- verification summary
- `Phase gate check:` rows added, updated, or rechecked in `docs/CORTEX_V2_PHASE_GATES_2.md` (or `none` if no phase gate applied)
- `Correspondence rows touched:` rows added, updated, or confirmed in `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md` (or `none` for non-load-bearing edits)

`PHILOSOPHY_AUDIT`
- `PHI_MINIFY`: pass|fail + one-line evidence
- `PHI_MISSION`: pass|fail + one-line evidence
- `PHI_NICHE`: pass|fail + one-line evidence
- `CUT_LIST`: what was removed, or why nothing could be removed
