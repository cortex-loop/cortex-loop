# CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0

Date: 2026-03-25
Status: accepted re-audited runtime-program brief for the first bounded reference closed-loop feedback slice

## Purpose

This document opens and records the closeout of the next intentional runtime program after the accepted `R1` through `R3` reference shell closeout.

The chosen next opening move is:

- one bounded realization-feedback carrier,
- one bounded control-ledger projection,
- one bounded latched-brake enforcement point,
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

Why this program opens now:

- the reference-host local CLI shell is already real,
- the first bounded computed executive slice is already real,
- the first one-process continuity law is already real and audit-clean for current scope,
- and the smallest remaining live-loop gap is still the lack of any bounded outcome-to-control feedback and any bounded runtime enforcement of the packet's latched-brake law.

## Locked scope

This program remains:

- reference-host only,
- one-process only,
- local CLI only,
- and packet-native.

This program adds only:

- last-step realization feedback,
- a top-level control ledger in the runtime output surface,
- and bounded latched-brake enforcement in runtime/SRE composition.

This program does **not** authorize:

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

- SRE-owned `ReferenceRealizationFeedback`
- runtime-owned `ReferenceControlLedger`
- `ReferenceRuntimeSession.last_realization_feedback`
- `ReferenceRuntimeStepResult.realized_family`
- top-level CLI/runtime field `control_ledger`
- enforcement warning `latched-brake-enforced:<selected>:<realized>`

`ReferenceRealizationFeedback` is last-step only.
It records:

- `selected_family`
- `realized_family`
- `brake_state`
- `commitment_result_kind`
- `warning_codes`
- `host_friction_tags`

`control_ledger` is a bounded top-level output surface with this locked field order:

- `event_class`
- `admissible_families`
- `selected_family`
- `realized_family`
- `dominant_uncertainty_sources`
- `brake_state`
- `budget_band`
- `primary_reason`

## Runtime law for this program

The runtime shell may:

- retain the immediately previous realized shell outcome,
- feed that bounded outcome into the next executive-state build,
- project a compact control ledger,
- and enforce the packet's latched-brake restriction at runtime realization time.

It may not:

- import certification law into SRE,
- invent a second continuity model,
- invent learned weights or aggregate reward history,
- move policy ownership into Core,
- or smooth away contradiction when selection and realization diverge.

Corrective `R4` law:

- prior feedback may only influence goal-progress uncertainty, contradiction spike preservation, and brake pressure,
- `selected_family` and `realized_family` must remain distinct when enforcement overrides behavior,
- lawful `commitment_result_kind` must remain visible even when an enforcement warning is also present,
- and the first control ledger must serialize only runtime truth actually produced by the step kernel.

## Program order

This program remains split into four bounded code seams plus closeout:

1. `R4B` realization-feedback carrier and persistence
2. `R4C` feedback-conditioned executive builder
3. `R4D` control-ledger projection
4. `R4E` latched-brake enforcement
5. `R4F` re-audit and closeout

Every cross-layer seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`R4` is only landed when all are true:

- last-step realization feedback is real and persisted in the runtime session,
- the builder uses that feedback only through the bounded law recorded in this brief,
- the CLI exposes a top-level `control_ledger`,
- `latched` brake enforcement is real and contradiction-preserving,
- targeted tests pass twice,
- `make seam-preflight`, `make test-smoke`, and `make verify` pass,
- and the `R4` phase-gate row is honestly closed.

## Current K1 candidate state before closeout

On branch `codex/k1f-openai-service-closeout` rooted at K1 proof head `d4c311f`:

- the runtime session persists only the immediately previous realized shell outcome as `ReferenceRealizationFeedback`,
- the executive builder uses that last-step feedback only through bounded goal-progress uncertainty, contradiction-spike, and brake-pressure updates,
- the CLI exposes a top-level `control_ledger` with event class, admissible families, selected family, realized family, dominant uncertainty sources, brake state, budget band, and primary reason,
- `latched` brake enforcement is real at runtime realization time and keeps `selected_family` distinct from `realized_family` when behavior is overridden,
- lawful `commitment_result_kind` may remain visible even when a `latched-brake-enforced:*` warning is also present,
- committed end-to-end proof now exists for session-rejection feedback propagation, prior-enforcement-override pressure, clean-success no false pressure, deterministic control-ledger ordering, and CLI-visible selected-vs-realized divergence,
- and a zero-finding adversarial runtime/API review found no defect for current scope on this candidate line.

This is branch-local K1 implementation truth.
It does **not** by itself promote accepted baseline truth.

## Explicitly blocked moves

This program does not authorize:

- cross-host runtime rollout,
- cross-process continuity,
- runtime AUX activation,
- offline consolidation,
- package-level mediation promotion,
- or a service shell.

Success here only closes one bounded feedback/enforcement slice.
