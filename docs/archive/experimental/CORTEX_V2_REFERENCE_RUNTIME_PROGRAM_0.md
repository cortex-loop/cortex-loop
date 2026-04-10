# CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0

Surface: experimental

Date: 2026-03-25
Status: accepted re-audited runtime-program brief for the first live Cortex shell on the K1 closeout line

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
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/j2-restack-acceptance-truth-normalization`
- commit: `acfccf9`

Why this program opens now:

- the accepted repo already has lawful host-native substrates, Core dispatch/certification, landed reference SRE policy seams, and contradiction-preserving evidence discipline,
- the largest north-star product gap is still the lack of a live runtime / product shell,
- and the reference host is the strongest lawful first anchor.

## Locked scope

This program is reference-host only.

The first accepted product-facing artifact is:

- `python3 -m cortex.hosts.reference.cli`

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
- silently reassign a non-empty runtime `session_id`,
- silently erase suspended pending-goal anchors through malformed `open` or non-continuity events,
- or treat reference runtime success as permission for multi-host runtime rollout.

Corrective ordering law:

- continuity rejection must remain explicit and contradiction-preserving,
- malformed `open` and session-id mismatch must surface explicit warnings without rewriting shell truth,
- and lawful commitment certification may still coexist with a rejected continuity transition on the same event when certification evidence remains sufficient.

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

## Current accepted state after K1 runtime closeout

On the accepted K1 runtime closeout line implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39` on branch `codex/k1f-openai-service-closeout`:

- the first accepted reference-host local CLI shell is real,
- the first bounded computed executive slice is real inside that shell,
- the first one-process live continuity slice plus explicit rejection enforcement are real,
- the corrective runtime hardening now preserves suspended pending-goal anchors across non-continuity events,
- malformed `open` requests are explicitly rejected instead of clearing continuity anchors by accident,
- a mismatched runtime `session_id` is surfaced as an explicit contradiction and does not silently reassign the one-process shell,
- a lawful `commitment_result_kind` may coexist with a rejected continuity transition on the same event when certification evidence remains sufficient,
- and the corrective zero-finding re-audit has passed for current scope on the accepted K1 line.

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
