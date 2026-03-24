# CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0

Date: 2026-03-25
Status: active corrective runtime-program brief for the first live Cortex shell

## Purpose

This document opens the first post-closeout product/runtime program without reopening packet authority or silent roadmap expansion.

The chosen next opening move is:

- one reference-host-only runtime program,
- one developer-facing local CLI loop,
- one local in-process session model,
- and one bounded train that proves runtime shell, computed executive state, and first live continuity in that order.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/s0b-erika-support-closeout`
- commit: `6218115`

Why this program opens now:

- the accepted repo already has lawful host-native substrates, Core dispatch/certification, landed reference SRE policy seams, and contradiction-preserving evidence discipline,
- the largest north-star product gap is still the lack of a live runtime / product shell,
- and the reference host is the strongest lawful first anchor.

## Locked scope

This program is reference-host only.

The first accepted product-facing artifact is:

- `python3 -m cortex.runtime.reference_cli`

Locked first-shell rules:

- local CLI only
- JSONL input and JSONL output only
- one object per input event
- one object per processed event
- one in-process session only
- no service/API shell
- no persistence
- no Gemini runtime
- no OpenAI runtime
- no AUX runtime activation
- no mediation implementation

The first accepted CLI input contract is:

- each input line must contain `event_name: str`
- each input line must contain `payload: object`

The first accepted CLI output contract must include:

- `event_index`
- `native_event_name`
- `dispatch_lane`
- `selected_family`
- `brake_state`
- `warnings`
- `session_summary`
- `commitment_result_kind`

`commitment_result_kind` must be `null` when the full commitment path is not activated.

## Program order

This program remains split into three bounded program stages:

1. `R1` — reference runtime shell
2. `R2` — computed reference executive slice
3. `R3` — first live continuity slice

Ordering law:

- `R1` must land before `R2`
- `R2` must land before `R3`
- each runtime seam is one-session max
- every accepted seam must end on a clean tree

## Runtime shell law

The runtime shell must compose existing lawful substrates.

It may:

- call the landed reference observe/bind path,
- call `classify_dispatch()`,
- call the landed reference commitment-path helpers,
- call landed SRE policy helpers,
- and maintain minimal in-memory runtime session state

It may not:

- expand Core into a scheduler,
- bypass dispatch or certification,
- invent a second continuity model outside SRE/support law,
- fabricate commitment results for cheap or candidate-bearing events,
- or treat reference runtime success as permission for multi-host runtime rollout.

## Acceptance gates

`R1` is only landed when all are true:

- the runtime step kernel exists,
- the CLI contract exists,
- targeted unit and integration tests pass twice,
- `make test-smoke` passes,
- `make verify` passes,
- and the phase-gate row for `R1` is honestly closed

`R2` is only landed when all are true:

- computed executive state is built in SRE, not runtime,
- soft-control selection is computed from the built state,
- the CLI emits bounded executive-state summaries,
- repeated reruns pass,
- and the phase-gate row for `R2` is honestly closed

`R3` is only landed when all are true:

- open / suspend / resume / merge continuity works in one runtime session,
- illegal continuity transitions are explicitly rejected,
- continuity remains contradiction-preserving,
- repeated reruns pass,
- and the phase-gate row for `R3` is honestly closed

## Current corrective state after the audit findings

At corrective-train open from `012cc76`:

- the first accepted reference-host local CLI shell is real,
- the first bounded computed executive slice is real inside that shell,
- the first one-process live continuity slice plus explicit rejection enforcement are real enough to keep as the program center,
- but the closeout is temporarily reopened because the audit found one real runtime continuity bug and one living-correspondence drift issue,
- and the program is now in corrective re-hardening rather than widened scope.

Corrective hardening must additionally make these truths explicit:

- non-continuity events may merge pending-goal refs, but may not silently erase suspended resume anchors,
- malformed `open` requests must be explicitly rejected instead of clearing continuity anchors by accident,
- a mismatched runtime `session_id` is an explicit contradiction and may not silently reassign the one-process shell,
- and a lawful `commitment_result_kind` may coexist with a rejected continuity transition on the same event when certification evidence remains sufficient.

This closeout does **not** authorize:

- broader multi-agent runtime,
- cross-host runtime rollout,
- runtime AUX activation,
- offline consolidation,
- or mediation implementation.

## Explicitly blocked moves

This program does not authorize:

- reference-to-Gemini or reference-to-OpenAI runtime rollout,
- runtime AUX activation,
- offline consolidation,
- package-level mediation promotion,
- or a networked product shell

Broader runtime work must be opened later as a separate program from an accepted clean state.
