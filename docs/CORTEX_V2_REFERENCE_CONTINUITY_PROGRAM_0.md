# CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0

Date: 2026-03-26
Status: accepted re-audited runtime-program brief for the first bounded reference cross-process continuation slice

## Purpose

This document opens the next explicit runtime program after the bounded `R5` short-window feedback closeout.

The chosen next move is:

- one bounded persisted continuation artifact,
- one explicit CLI load/save surface,
- one cross-process equivalence contract,
- and one re-audit closeout that keeps truthful continuation ahead of broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`
- `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`

## Accepted parent and rationale

Parent for this program on the current line:

- branch: `codex/j2-restack-acceptance-truth-normalization`
- commit: `acfccf9`

Why this program opens now:

- the reference-host local CLI shell is already real,
- one-process continuity law is already real,
- bounded realization feedback is already real,
- but truthful continuation across fresh process boundaries is still not real,
- and that gap is closer to the v2 product center than richer local feedback math or broader runtime rollout.

## Locked scope

This program remains:

- reference-host only,
- local CLI only,
- explicit save/load only,
- packet-subordinate,
- and bounded to one persisted session artifact per continuation handoff.

This program adds only:

- runtime-owned `ReferenceRuntimeSessionArtifact`,
- `--load-session` / `--save-session` CLI control,
- bounded `continuity_truth` and bounded `control_residue`,
- and cross-process equivalence proof.

This program does **not** authorize:

- multi-host runtime,
- generic persistence doctrine,
- autosave,
- checkpoints,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- longer-than-three-step feedback history,
- scoring rewrite,
- or any network/service shell.

## Runtime-program carrier split

This program uses two runtime-program-owned carrier classes:

- `continuity_truth`
- `control_residue`

`continuity_truth` means the exact state required to resume lawfully.

`control_residue` means bounded prior-outcome residue that may influence later control without becoming a second truth court.

This split is runtime-program law only.
It is not packet doctrine.

Biological analogy may be used in brief prose for orientation only.
Artifact law remains mechanical.

## Public runtime contract

The runtime shell continues to expose:

- `python3 -m cortex.runtime.reference_cli`

New public additions in this program are:

- `--load-session PATH`
- `--save-session PATH`

The event-stream contract remains unchanged:

- JSONL input only
- JSONL output only
- no synthetic save/load events
- no output-key reordering

The persisted artifact is one versioned JSON object with exact top-level order:

1. `artifact_kind`
2. `artifact_version`
3. `continuity_truth`
4. `control_residue`

`continuity_truth` has exact field order:

- `session_id`
- `event_index`
- `branch_registry`
- `active_track_ref`
- `pending_goal_refs`

`control_residue` has exact field order:

- `last_budget_band`
- `last_commitment_result_summary`
- `last_realization_feedback`
- `feedback_window`

`feedback_window` remains oldest-to-newest and max length `3`.

## Runtime law for this program

The runtime shell may:

- persist exact continuation truth,
- persist bounded control residue,
- load a prior artifact explicitly,
- and continue the shell across CLI invocations without inventing new runtime doctrine.

It may not:

- persist shell-long `budget_history` or `brake_history`,
- treat one-process diagnostic history as cross-process continuation truth,
- silently rewrite malformed or contradictory saved state,
- widen into a generic store,
- or treat persistence success as permission for broader runtime rollout.

Artifact law:

- `artifact_kind` must equal `reference-runtime-session`
- `artifact_version` must equal `1`
- unknown keys are rejected everywhere for version `1`
- `last_realization_feedback` and `feedback_window[-1]` must agree when both are present
- loader must reconstruct through `ReferenceRuntimeSession(...)`
- derived projections such as `executive_state_summary`, `control_ledger`, `feedback_window_summary`, and full `session_summary` are not serialized

Bounded residue law:

- persist only `last_budget_band`, `last_commitment_result_summary`, `last_realization_feedback`, and `feedback_window`
- do **not** persist full `budget_history` or `brake_history`
- on load, bounded residue may seed singleton `budget_history` / `brake_history` diagnostics for the resumed shell

## Cross-process equivalence contract

`C1` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

`C1` equivalence does **not** require:

- exact byte-for-byte replay of `session_summary.budget_history`
- exact byte-for-byte replay of `session_summary.brake_history`

Those two histories remain public one-process diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `C1A` program lock
2. `C1B` bounded artifact carrier and serializer
3. `C1C` explicit CLI load/save
4. `C1D` cross-process equivalence proof
5. `C1E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`C1` is only honestly closed when all are true:

- persisted continuation truth is real,
- persisted control residue is bounded,
- full shell-long `budget_history` / `brake_history` are not persisted,
- the loader reconstructs through `ReferenceRuntimeSession(...)`,
- CLI load/save is explicit and emits no stdout on load/save failure,
- split-run equivalence matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-reference-runtime-continuity`, `make test-smoke`, and `make verify` pass,
- and the `C1` phase-gate row is updated truthfully.

## Current accepted state after K1 closeout

On the accepted K1 runtime closeout line implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39` on branch `codex/k1f-openai-service-closeout`:

- `ReferenceRuntimeSessionArtifact` is now landed as a bounded cross-process carrier,
- the reference CLI now supports explicit `--load-session` / `--save-session`,
- the artifact persists exact `continuity_truth` and bounded `control_residue`,
- split-run continuity proof now exists against the reference-host shell,
- `session_summary.budget_history` and `brake_history` remain public but are explicitly excluded from cross-process equivalence,
- `make revalidate-reference-runtime-continuity` now exists as the repo-local continuity revalidation entry point,
- and targeted reruns, repeated repo-local continuity revalidation, `make test-smoke`, and `make verify` all passed on the accepted K1 line.

## Explicitly blocked moves

This program does not authorize:

- auto-opening `R6`,
- cross-host runtime rollout,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- generic storage doctrine,
- checkpoint management,
- or broader runtime/product claims beyond this bounded continuation slice.
