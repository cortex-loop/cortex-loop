# CORTEX_V2_CLAUDE_SERVICE_PROGRAM_0

Date: 2026-03-27
Status: accepted re-audited runtime-program brief for the first Claude loopback service shell

## Purpose

This document records the loopback service slice inside the accepted G1 Claude runtime/product parity line.

The chosen next move is:

- one loopback-only Claude service shell,
- one HTTP event ingress path over the current-line `A2` transcript parsing,
- one JSON artifact import/export surface over the current-line `A1` session carrier,
- and one re-audit closeout that keeps local service reality ahead of outbound host control or broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_INGRESS_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/g1-gemini-runtime-product-parity`
- commit: `9dfe38a`

Why this program opens now:

- the current line now includes a landed raw Claude transcript ingress slice,
- the next one-agent north-star gap is a real local service shell rather than another CLI,
- loopback-only HTTP is a smaller truthful step than outbound host control,
- and it remains narrower than remote hosting, multi-session doctrine, or multi-agent orchestration.

## Locked scope

This program remains:

- Claude only,
- single-agent only,
- loopback-only,
- one active session per process,
- ingress-only,
- packet-subordinate,
- and service-shaped without remote bind.

This program adds only:

- `ClaudeServiceState`
- `handle_claude_service_request()`
- `export_claude_service_session()`
- `import_claude_service_session()`
- `python3 -m cortex.runtime.claude_service`
- loopback HTTP fixtures and service continuity proof

This program does **not** by itself authorize:

- remote or multi-client hosting,
- outbound Claude host control realization,
- Claude host-control doctrine beyond this bounded service shell,
- generic runtime/service abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded loopback service shell.

## Public service contract

The Claude loopback service shell exposes:

- `python3 -m cortex.runtime.claude_service`

CLI flags:

- `--port`
- `--load-session PATH`

Bound address:

- `127.0.0.1` only

HTTP surface:

- `GET /health`
- `POST /v1/events`
- `GET /v1/session/export`
- `POST /v1/session/import`

`GET /health` returns:

- `status`
- `runtime`
- `session_loaded`

`POST /v1/events` accepts one raw Claude transcript object in the current-line `A2` shape:

- required field: `type`
- all remaining top-level fields become payload

`POST /v1/events` returns exactly the current-line `A1` runtime record shape and field order.

`GET /v1/session/export` returns exactly the current-line `ClaudeRuntimeSessionArtifact` JSON object.

`POST /v1/session/import` accepts exactly the current-line `ClaudeRuntimeSessionArtifact` JSON object and returns the resulting artifact JSON after import.

All responses are JSON.

Error contract:

- `400` for invalid transcript records or invalid session artifacts
- `404` for unknown paths
- `405` for unsupported methods
- response body shape: `{"error":"<message>"}`

## Runtime law for this program

The loopback service shell may:

- bind only to `127.0.0.1`,
- keep exactly one active `ClaudeRuntimeSession` per process,
- parse `POST /v1/events` bodies through the current-line `parse_claude_host_event_envelope()`,
- run the current-line `run_claude_runtime_step()` over the in-memory session,
- import/export the current-line `ClaudeRuntimeSessionArtifact` as JSON,
- and expose a more live local service boundary without widening the runtime owner.

It may not:

- bind remotely,
- create multi-session or multi-client doctrine,
- bypass the current-line `A2` parser,
- invent a service-specific persistence format,
- expose path-based import/export HTTP endpoints,
- autosave on shutdown,
- realize outbound Claude host actions,
- or introduce a generic service substrate.

Undocumented-event law:

- undocumented raw `message_*` or `content_block_*` events remain lawful input,
- they must still degrade to explicit conservative warnings,
- and the service shell may not fabricate documented parity where none exists.

## G3 equivalence contract

For a transcript mechanically equivalent to the current-line `A2` ingress shell, `A3` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

As in `C1`, `A1`, and `A2`, exact byte-for-byte replay of `session_summary.budget_history` and `session_summary.brake_history` is not required.
Those remain public diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `A3A` program lock
2. `A3B` loopback service carrier and request boundary
3. `A3C` HTTP shell and artifact transport
4. `A3D` service continuity proof
5. `A3E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`A3` is only honestly closed when all are true:

- loopback-only HTTP is real at `127.0.0.1`
- `POST /v1/events` drives the current-line `A2` transcript parsing and the current-line `A1` runtime shell
- `GET /v1/session/export` and `POST /v1/session/import` move the current-line artifact JSON without inventing a service-specific persistence format
- one active session per process is real
- split-run service continuity matches the contract recorded above
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-claude-service`, `make test-smoke`, and `make verify` pass
- and the `A3` phase-gate row is updated truthfully

## Current accepted state after A1 closeout

On the accepted A1 closeout line, implemented at A1 proof head `9d6186c` over accepted G1 baseline `9dfe38a`:

- `ClaudeServiceState`, `handle_claude_service_request()`, `export_claude_service_session()`, `import_claude_service_session()`, and `python3 -m cortex.runtime.claude_service` are now landed `A3` surfaces, implemented at A1 proof head `9d6186c`
- `GET /health`, `POST /v1/events`, `GET /v1/session/export`, and `POST /v1/session/import` now exist over loopback-only HTTP
- `/v1/events` now drives the current-line `A2` transcript parser and current-line `A1` runtime shell directly
- loopback bind is fixed to `127.0.0.1`
- one active session per process is real for current scope
- repeated direct reruns plus repeated `make revalidate-claude-service` passed for current scope

## Explicitly blocked moves

This program does not authorize:

- remote bind,
- multi-session or multi-client hosting,
- outbound Claude host control realization,
- Claude host-control doctrine beyond this bounded service shell,
- generic runtime/service abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded loopback service shell.
