# CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1

Date: 2026-03-25
Status: accepted re-audited runtime-program brief for the first bounded reference short-window feedback slice after session/window carrier reclosure

## Purpose

This document opens the next intentional runtime program after the accepted `R4` reference closed-loop feedback closeout.

The chosen next opening move is:

- one bounded three-step realization-feedback window,
- one bounded prior-window summary,
- one runtime/CLI projection for that prior-window trace,
- and one re-audit closeout that stops again before any broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/j2-restack-acceptance-truth-normalization`
- commit: `acfccf9`

Historical `R4` source lineage still carried into this program:

- accepted proof head: `7672304`
- runtime landing inside that closeout history: `cecd82d`

Why this program opens now:

- the reference-host local CLI shell is already real,
- the first bounded computed executive slice is already real,
- the first one-process continuity law is already real and audit-clean for current scope,
- and the first bounded last-step realization-feedback path is already real and audit-clean for current scope,
- but the runtime shell still lacks any bounded short-window feedback law that preserves multiple recent realized outcomes without widening the runtime shell.

## Locked scope

This program remains:

- reference-host only,
- one-process only,
- local CLI only,
- packet-native,
- and bounded to a three-step short-window feedback horizon.

This program adds only:

- SRE-owned `ReferenceRealizationFeedbackWindow`,
- SRE-owned `ReferenceFeedbackWindowSummary`,
- `summarize_reference_feedback_window(window)`,
- `ReferenceRuntimeSession.feedback_window`,
- `ReferenceRuntimeStepResult.feedback_window_summary`,
- top-level CLI/runtime field `feedback_window_summary`,
- and `session_summary.feedback_window_size`.

This program does **not** authorize:

- a scoring rewrite,
- a new policy court,
- multi-host runtime,
- cross-process continuity,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or any network/service shell.

## Public runtime contract

The runtime shell continues to expose:

- `python3 -m cortex.runtime.reference_cli`

New public additions in this program are:

- SRE-owned `ReferenceRealizationFeedbackWindow`
- SRE-owned `ReferenceFeedbackWindowSummary`
- SRE entry point `summarize_reference_feedback_window(window)`
- `ReferenceRuntimeSession.feedback_window`
- `ReferenceRuntimeStepResult.feedback_window_summary`
- top-level CLI/runtime field `feedback_window_summary`
- `session_summary.feedback_window_size`

`ReferenceRealizationFeedbackWindow` is locked to:

- `entries: tuple[ReferenceRealizationFeedback, ...]`
- maximum length `3`
- oldest-to-newest ordering
- append behavior that keeps only the three most recent entries

`ReferenceFeedbackWindowSummary` has this locked field order:

- `window_size`
- `rejection_count`
- `override_count`
- `latched_count`
- `clean_success_streak`
- `goal_progress_floor`
- `degradation_pressure_bonus`
- `sustained_spike_flags`

`feedback_window_summary` always describes the prior window that influenced the current step.
`session_summary.feedback_window_size` always describes the post-step window size after the current realized outcome is appended.

## Runtime law for this program

The runtime shell may:

- retain the three most recent realized shell outcomes,
- summarize the prior realized-outcome window through one bounded SRE helper,
- feed that summary into the next executive-state build,
- and project the prior-window summary in the CLI/runtime output.

It may not:

- widen beyond a three-step window,
- consume hidden reward history,
- rewrite scorer law,
- invent a second continuity model,
- move policy ownership into Core,
- or smooth away contradiction when commitment truth, continuity rejection, and enforced realization coexist.

Corrective `R5` law:

- the builder may use the window summary only for goal-progress uncertainty floor, contradiction-spike preservation, and brake-pressure inputs,
- `R4` last-step behavior must remain a strict subset of the new window law when `window_size == 1`,
- `ReferenceRuntimeSession` may normalize lawful one-sided feedback state before any step consumes it:
  - last-step mirror with empty window becomes a one-entry window carrying that same realized outcome,
  - non-empty window with no last-step mirror adopts the newest window entry as the last-step mirror,
  - and a non-empty window whose newest entry disagrees with the explicit last-step mirror is rejected,
- the feedback window must persist runtime-realized outcomes only,
- `feedback_window_summary` must reflect the prior influencing window rather than the post-step window,
- and `control_ledger` shape and field ordering remain unchanged in this program.

## Program order

This program remains split into three bounded code seams plus closeout:

1. `R5B` feedback window carrier and session persistence
2. `R5C` SRE window summary and builder integration
3. `R5D` runtime/CLI projection for prior-window trace
4. `R5E` re-audit and closeout

Every cross-layer seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`R5` is only landed when all are true:

- the feedback window is bounded to three runtime-realized outcomes,
- `R4` last-step behavior remains a strict subset of the new window law,
- the live runtime session carrier normalizes lawful one-sided last/window state before any step consumes it and rejects divergent two-sided state explicitly,
- the builder uses the window summary only through bounded uncertainty floor, contradiction-spike, and brake-pressure updates,
- scorer law remains unchanged,
- the CLI exposes a top-level `feedback_window_summary` and post-step `session_summary.feedback_window_size`,
- targeted tests pass twice,
- `make seam-preflight`, `make test-smoke`, and `make verify` pass,
- and the `R5` phase-gate row is honestly closed.

## Current accepted state after K1 closeout

On the accepted K1 runtime closeout line implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39` on branch `codex/k1f-openai-service-closeout`:

- the runtime session still persists `last_realization_feedback` as the direct last-step mirror, and it now also persists `feedback_window` as the bounded three-step oldest-to-newest realized-outcome window,
- the window persists runtime-realized outcomes only and truncates to the three most recent entries,
- the SRE summary law now derives rejection count, override count, latched count, clean-success streak, goal-progress floor, bounded degradation-pressure bonus, and sustained spike flags from the prior window only,
- the executive builder now consumes that prior-window summary only through bounded goal-progress uncertainty, contradiction-spike, and brake-pressure updates,
- scorer law is unchanged from `R4`,
- the runtime step result now carries `feedback_window_summary` for the prior influencing window,
- the CLI exposes top-level `feedback_window_summary` while `session_summary.feedback_window_size` reports the post-step window size after the current realized outcome is appended,
- lawful `commitment_result_kind` may remain visible even when continuity rejection or `latched-brake-enforced:*` warnings are also present,
- committed end-to-end proof now exists at `ee41eb4` for clean-window zero pressure, single-mismatch `0.55` floor, repeated-mismatch `0.70` floor, and oldest-entry truncation on the fourth append,
- the accepted landed donor closeout for the historical `R5` line is still anchored at `fd6789f` rather than treating `ee41eb4` as the sole accepted clean baseline,
- and a zero-finding re-audit passed for current scope on the accepted K1 line.

## Historical corrective source state

On corrective source branch `codex/r5g-h-corrective-reclosure` opened from accepted normalization head `7eac5e8`:

- `ReferenceRuntimeSession` now normalizes lawful one-sided last/window state before any step consumes it:
  - last-step mirror with empty window becomes a one-entry bounded window,
  - non-empty bounded window with no explicit last-step mirror adopts the newest entry as that mirror,
  - and divergent two-sided state is rejected explicitly,
- the direct-construction reproduction that dropped next-step pressure is now closed on the corrective line,
- the corrective seam stayed limited to carrier normalization/rejection law plus re-audit; it did not widen feedback horizon, scorer law, runtime scope, or policy ownership,
- and `R5` is landed again for current scope on the historical corrective line because the repeat-stability audit bundle passed after the carrier invariant was closed.

## Explicitly blocked moves

This program does not authorize:

- broader feedback history than three realized outcomes,
- a scoring rewrite,
- a new policy court,
- cross-host runtime rollout,
- cross-process continuity,
- runtime AUX activation,
- offline consolidation,
- package-level mediation promotion,
- or a service shell.

Success here only closes one bounded short-window feedback slice.
