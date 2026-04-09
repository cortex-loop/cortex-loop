# CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0

Surface: product

Date: 2026-04-08
Status: accepted runtime-program brief for the default bounded outbound OpenAI host-control lane after verified-work restoration

## Purpose

This document opens the next explicit one-agent runtime/product program after accepted `O3`.

The chosen next move is:

- one bounded outbound OpenAI control lane,
- one text-only `openai-response-stream` request surface,
- one stdlib transport over the official OpenAI Responses create+stream surface,
- one loopback service action endpoint on top of the accepted `O3` shell,
- and one re-audit closeout that preserves K1 truth while opening the first bounded outbound host-control lane.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/k1f-openai-service-closeout`
- commit: `79b8f39`

Why this program opens now:

- accepted `O3` made a real loopback service shell lawful,
- the smallest remaining product gap is realized host action rather than more internal runtime math,
- the current OpenAI driver already names `openai-response-stream` as the relevant host lifecycle effect,
- and a bounded outbound lane is smaller and more truthful than tool-calling doctrine, cancel/update lanes, or executive-loop widening.

## Locked scope

This program remains:

- OpenAI only,
- one active session per process,
- loopback-only at the public service boundary,
- one outbound action family only: `openai-response-stream`,
- the default thin path when no `work_contract` is present,
- packet-subordinate,
- and host-specific without generic action/runtime/service doctrine.

This program adds only:

- `OpenAIHostControlRequest`
- `OpenAIHostControlResult`
- `execute_openai_response_stream()`
- `run_openai_host_control()`
- `POST /v1/actions/response-stream`
- outbound-action fixture transport and continuity proof

This program does **not** authorize:

- tools or tool-result submission,
- cancel/update lanes,
- remote hosting,
- multi-session or multi-client doctrine,
- Gemini runtime,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded text-only outbound lane.

Optional verified-work activation now exists, but it is governed separately by `docs/CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0.md`.
This document remains the owner of the default thin path only.

## Public service contract

The public K2 surface remains:

- `python3 -m cortex.runtime.openai_service`

New HTTP endpoint:

- `POST /v1/actions/response-stream`

Request body shape:

- top-level keys: `action_tag`, `request`
- `action_tag` must be `openai-response-stream`
- `request.model` required
- `request.input` required and must be one non-empty string
- optional request keys on the default thin path:
  - `instructions`
  - `metadata`
  - `max_output_tokens`
- `request.work_contract` is reserved for the separately scoped verified-work lane and is not part of the thin-path contract described here
- `stream` is implicit `true`; if present and not `true`, reject the request
- all other request keys are rejected on the default thin path

Response body shape:

- `action_tag`
- `records`

`records` is the ordered list of exact accepted `O1` runtime record objects produced from the returned host events.

All responses remain JSON.

Error contract:

- `400` invalid outbound request
- `502` upstream transport failure, malformed upstream stream, or zero-event result
- existing `404` and `405` remain unchanged
- response body shape remains `{"error":"<message>"}`

## Runtime law for this program

The K2 outbound lane may:

- reuse the accepted loopback `O3` service shell,
- keep exactly one active `OpenAIRuntimeSession` per process,
- validate one strict text-only outbound request carrier,
- execute one stdlib outbound Responses create+stream transport,
- parse returned upstream frames into the exact accepted `O2` raw transcript record shape,
- and feed every returned host event through accepted `parse_openai_host_event_envelope()` and accepted `run_openai_runtime_step()`.

It may not:

- accept tools or tool-result submission,
- accept content-part arrays or multimodal payloads,
- widen into cancel/update lanes,
- bypass the accepted `O2` parser,
- widen into remote hosting or multi-client doctrine,
- add an `openai` SDK dependency,
- require live network or a real API key in the canonical verification bundle,
- or introduce a generic control substrate.

Separately scoped verified-work activation may reuse the same public endpoint and module family, but it may not retroactively change the thin-path meaning recorded here.

Undocumented-event law:

- undocumented raw `response.*` events remain lawful downstream input,
- they must still degrade to explicit conservative warnings,
- and K2 may not fabricate documented parity where none exists.

## O4 equivalence contract

For the same ordered outbound action calls and the same returned host-event stream, `O4` equivalence means:

- same ordered current-line `O1` records with exact `decision + journal` projection
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same final persisted artifact with exact `openai_product_journal` v1 truth

## Program order

This program remains split into five bounded seams:

1. `O4A` program lock
2. `O4B` request/result carriers plus stdlib transport
3. `O4C` runtime composition over accepted `O2`/`O1`
4. `O4D` service endpoint and continuity proof
5. `O4E` re-audit and closeout

Every seam must end on a clean tree before the next opens.

## Acceptance gates

`O4` is only honestly closed when all are true:

- `POST /v1/actions/response-stream` is real on the loopback service shell
- the request boundary is strict-whitelist and text-only
- the outbound transport is stdlib-only and host-specific
- returned upstream host events re-enter through accepted `O2` parsing and accepted `O1` runtime composition
- export/import continuity preserves exact `openai_product_journal` v1 truth
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-openai-host-control`, `make revalidate-openai-service`, `make test-smoke`, and `make verify` pass
- and the `O4` phase-gate row is updated truthfully

## Historical accepted state before X1 compression

On the accepted K2 host-control closeout line implemented at K2 proof head `5ed9549` and truthfully closed at deterministic closeout head `9ed7dae` on branch `codex/k2-openai-host-control`:

- `OpenAIHostControlRequest`, `OpenAIHostControlResult`, `execute_openai_response_stream()`, `run_openai_host_control()`, and `POST /v1/actions/response-stream` are now landed `O4` surfaces
- the request boundary is strict-whitelist and text-only for current scope
- the stdlib transport has an internal fixture mode so canonical tests require no live OpenAI network
- returned host events now re-enter the accepted `O2` parser and accepted `O1` runtime shell directly
- `make revalidate-openai-host-control` now exists as the repo-local K2 revalidation entry point
- and targeted direct reruns, repeated repo-local revalidation, `make test-smoke`, and `make verify` all passed on the accepted K2 line

## Current accepted state after X1 compression

On the accepted X1 line:

- `run_openai_host_control()` still re-enters the accepted `O2` parser and compressed `O1` runtime shell directly,
- `OpenAIHostControlResult.records` now carry the exact compact `decision + journal` projection,
- export/import continuity across outbound actions now preserves `openai_product_journal` v1 only,
- and the older allocation/feedback story survives only as historical/reference evidence rather than the accepted OpenAI-only product runtime.

On the current accepted line after the verified-work restoration slice:

- the default thin path remains text-only and functionally unchanged when `work_contract` is absent,
- `run_openai_host_control()` still re-enters the accepted `O2` parser and compressed `O1` runtime shell directly on that thin path,
- and optional verified-work activation is now governed separately by `docs/CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0.md` rather than widening this thin-path brief.

On the current review line after the preservation-state candidate:

- verified-work activation now records a deterministic task anchor when no active goal is present,
- the repair turn is now preservation-centered and mechanical rather than failure-prose-only,
- repair requests now narrow `allowed_write_paths` to the lawful repair surface produced by runtime verification,
- repair verification now overlays the second-attempt file map onto the preserved first-attempt file map before re-running the verifier,
- and the thin `O4` path remains unchanged when `work_contract` is absent.

## Explicitly blocked moves

This program does not authorize:

- tools or tool-result submission,
- cancel/update lanes,
- content-part or multimodal request inputs,
- remote bind,
- multi-session or multi-client hosting,
- Gemini runtime,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded outbound lane.
