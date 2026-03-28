# CORTEX_V2_GEMINI_HOST_CONTROL_PROGRAM_0

Date: 2026-03-27
Status: accepted re-audited runtime-program brief for the first bounded outbound Gemini host-control lane

## Purpose

This document records the bounded outbound host-control slice inside the accepted G1 Gemini runtime/product parity line.

The chosen next move is:

- one bounded outbound Gemini control lane,
- one text-only `gemini-interaction-stream` request surface,
- one stdlib transport over the official Gemini `streamGenerateContent` surface,
- one loopback service action endpoint on top of the current-line `G3` shell,
- and one re-audit closeout that preserves G1 truth while opening the first bounded outbound host-control lane.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_INGRESS_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_SERVICE_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/k3-executive-live-outcome`
- commit: `efe003e`

Why this program opens now:

- the current line now includes a real loopback service shell,
- the smallest remaining product gap is realized host action rather than more internal runtime math,
- the current Gemini driver already names `gemini-interaction-stream` as the relevant host lifecycle effect,
- and a bounded outbound lane is smaller and more truthful than tool-calling doctrine, cancel/update lanes, or executive-loop widening.

## Locked scope

This program remains:

- Gemini only,
- one active session per process,
- loopback-only at the public service boundary,
- one outbound action family only: `gemini-interaction-stream`,
- text-only and strict-whitelist on the request surface,
- packet-subordinate,
- and host-specific without generic action/runtime/service doctrine.

This program adds only:

- `GeminiHostControlRequest`
- `GeminiHostControlResult`
- `execute_gemini_interaction_stream()`
- `run_gemini_host_control()`
- `POST /v1/actions/interaction-stream`
- outbound-action fixture transport and continuity proof

This program does **not** authorize:

- tools or tool-result submission,
- cancel/update lanes,
- remote hosting,
- multi-session or multi-client doctrine,
- more Gemini host-control widening,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded text-only outbound lane.

## Public service contract

The public G1 surface remains:

- `python3 -m cortex.runtime.gemini_service`

New HTTP endpoint:

- `POST /v1/actions/interaction-stream`

Request body shape:

- top-level keys: `action_tag`, `request`
- `action_tag` must be `gemini-interaction-stream`
- `request.model` required
- `request.input` required and must be one non-empty string
- optional request keys:
  - `instructions`
  - `metadata`
  - `max_output_tokens`
- `stream` is implicit `true`; if present and not `true`, reject the request
- all other request keys are rejected

Response body shape:

- `action_tag`
- `records`

`records` is the ordered list of exact current-line `G1` runtime record objects produced from the returned host events.

All responses remain JSON.

Error contract:

- `400` invalid outbound request
- `502` upstream transport failure, malformed upstream stream, or zero-event result
- existing `404` and `405` remain unchanged
- response body shape remains `{"error":"<message>"}`

## Runtime law for this program

The G1 outbound lane may:

- reuse the current-line loopback `G3` service shell,
- keep exactly one active `GeminiRuntimeSession` per process,
- validate one strict text-only outbound request carrier,
- execute one stdlib outbound `streamGenerateContent` transport,
- parse returned upstream frames into the exact current-line `G2` raw transcript record shape,
- and feed every returned host event through the current-line `parse_gemini_host_event_envelope()` and `run_gemini_runtime_step()`.

It may not:

- accept tools or tool-result submission,
- accept content-part arrays or multimodal payloads,
- widen into cancel/update lanes,
- bypass the current-line `G2` parser,
- widen into remote hosting or multi-client doctrine,
- add an `gemini` SDK dependency,
- require live network or a real API key in the canonical verification bundle,
- or introduce a generic control substrate.

Undocumented-event law:

- undocumented raw `content.*` or `interaction.*` events remain lawful downstream input,
- they must still degrade to explicit conservative warnings,
- and G1 may not fabricate documented parity where none exists.

## G4 equivalence contract

For the same ordered outbound action calls and the same returned host-event stream, `G4` equivalence means:

- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted artifact with exact `continuity_truth` and `control_residue`

Exact replay of one-process diagnostic `budget_history` and `brake_history` remains out of scope for cross-process equivalence.

## Program order

This program remains split into five bounded seams:

1. `G4A` program lock
2. `G4B` request/result carriers plus stdlib transport
3. `G4C` runtime composition over current-line `G2`/`G1`
4. `G4D` service endpoint and continuity proof
5. `G4E` re-audit and closeout

Every seam must end on a clean tree before the next opens.

## Acceptance gates

`G4` is only honestly closed when all are true:

- `POST /v1/actions/interaction-stream` is real on the loopback service shell
- the request boundary is strict-whitelist and text-only
- the outbound transport is stdlib-only and host-specific
- returned upstream host events re-enter through the current-line `G2` parsing and current-line `G1` runtime composition
- export/import continuity preserves exact `continuity_truth` plus bounded `control_residue`
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-gemini-host-control`, `make revalidate-gemini-service`, `make test-smoke`, and `make verify` pass
- and the `G4` phase-gate row is updated truthfully

## Current accepted state after G1 closeout

On the accepted G1 closeout line over accepted K3 baseline `efe003e`:

- `GeminiHostControlRequest`, `GeminiHostControlResult`, `execute_gemini_interaction_stream()`, `run_gemini_host_control()`, and `POST /v1/actions/interaction-stream` are now landed `G4` surfaces, implemented at G1 proof head `fe33a7e`
- the request boundary is strict-whitelist and text-only for current scope
- the stdlib transport has an internal fixture mode so canonical tests require no live Gemini network
- returned host events now re-enter the current-line `G2` parser and `G1` runtime shell directly
- repeated direct reruns plus repeated `make revalidate-gemini-host-control` passed for current scope

## Explicitly blocked moves

This program does not authorize:

- tools or tool-result submission,
- cancel/update lanes,
- content-part or multimodal request inputs,
- remote bind,
- multi-session or multi-client hosting,
- more Gemini host-control widening,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded outbound lane.
