# CORTEX_V2_OPENAI_SERVICE_PROGRAM_0

Date: 2026-03-26
Status: active runtime-program brief for the first OpenAI loopback service shell

## Purpose

This document opens the next explicit one-agent runtime/product program after accepted `O2`.

The chosen next move is:

- one loopback-only OpenAI service shell,
- one HTTP event ingress path over accepted `O2` transcript parsing,
- one JSON artifact import/export surface over the accepted `O1` session carrier,
- and one re-audit closeout that keeps local service reality ahead of outbound host control or broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/o2-openai-ingress-shell`
- commit: `d91f504`

Why this program opens now:

- accepted `O2` made raw OpenAI transcript ingress lawful,
- the next one-agent north-star gap is a real local service shell rather than another CLI,
- loopback-only HTTP is a smaller truthful step than outbound host control,
- and it remains narrower than remote hosting, multi-session doctrine, or multi-agent orchestration.

## Locked scope

This program remains:

- OpenAI only,
- single-agent only,
- loopback-only,
- one active session per process,
- ingress-only,
- packet-subordinate,
- and service-shaped without remote bind.

This program adds only:

- `OpenAIServiceState`
- `handle_openai_service_request()`
- `export_openai_service_session()`
- `import_openai_service_session()`
- `python3 -m cortex.runtime.openai_service`
- loopback HTTP fixtures and service continuity proof

This program does **not** authorize:

- remote or multi-client hosting,
- outbound OpenAI host control realization,
- Gemini runtime,
- generic runtime/service abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded loopback service shell.

## Public service contract

The OpenAI loopback service shell exposes:

- `python3 -m cortex.runtime.openai_service`

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

`POST /v1/events` accepts one raw OpenAI transcript object in the accepted `O2` shape:

- required field: `type`
- all remaining top-level fields become payload

`POST /v1/events` returns exactly the accepted `O1` runtime record shape and field order.

`GET /v1/session/export` returns exactly the accepted `OpenAIRuntimeSessionArtifact` JSON object.

`POST /v1/session/import` accepts exactly the accepted `OpenAIRuntimeSessionArtifact` JSON object and returns the resulting artifact JSON after import.

All responses are JSON.

Error contract:

- `400` for invalid transcript records or invalid session artifacts
- `404` for unknown paths
- `405` for unsupported methods
- response body shape: `{"error":"<message>"}`

## Runtime law for this program

The loopback service shell may:

- bind only to `127.0.0.1`,
- keep exactly one active `OpenAIRuntimeSession` per process,
- parse `POST /v1/events` bodies through accepted `parse_openai_host_event_envelope()`,
- run accepted `run_openai_runtime_step()` over the in-memory session,
- import/export the accepted `OpenAIRuntimeSessionArtifact` as JSON,
- and expose a more live local service boundary without widening the runtime owner.

It may not:

- bind remotely,
- create multi-session or multi-client doctrine,
- bypass the accepted `O2` parser,
- invent a service-specific persistence format,
- expose path-based import/export HTTP endpoints,
- autosave on shutdown,
- realize outbound OpenAI host actions,
- or introduce a generic service substrate.

Undocumented-event law:

- undocumented raw `response.*` events remain lawful input,
- they must still degrade to explicit conservative warnings,
- and the service shell may not fabricate documented parity where none exists.

## O3 equivalence contract

For a transcript mechanically equivalent to the accepted `O2` ingress shell, `O3` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

As in `C1`, `O1`, and `O2`, exact byte-for-byte replay of `session_summary.budget_history` and `session_summary.brake_history` is not required.
Those remain public diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `O3A` program lock
2. `O3B` loopback service carrier and request boundary
3. `O3C` HTTP shell and artifact transport
4. `O3D` service continuity proof
5. `O3E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`O3` is only honestly closed when all are true:

- loopback-only HTTP is real at `127.0.0.1`
- `POST /v1/events` drives accepted `O2` transcript parsing and the accepted `O1` runtime shell
- `GET /v1/session/export` and `POST /v1/session/import` move the accepted artifact JSON without inventing a service-specific persistence format
- one active session per process is real
- split-run service continuity matches the contract recorded above
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-openai-service`, `make test-smoke`, and `make verify` pass
- and the `O3` phase-gate row is updated truthfully

## Current branch-local state

On branch `codex/o3-openai-service-shell` opened from accepted `O2` closeout head `d91f504`:

- `OpenAIServiceState`, `handle_openai_service_request()`, `export_openai_service_session()`, `import_openai_service_session()`, and `python3 -m cortex.runtime.openai_service` now exist as branch-local `O3` candidate surfaces
- `GET /health`, `POST /v1/events`, `GET /v1/session/export`, and `POST /v1/session/import` now exist over loopback-only HTTP
- `/v1/events` now drives the accepted `O2` transcript parser and accepted `O1` runtime shell directly
- loopback bind is fixed to `127.0.0.1`
- one active session per process is real for current scope
- service continuity proof now exists against the recorded `O3` contract, including explicit diagnostic-history non-equivalence
- and `make revalidate-openai-service` now exists as the repo-local service revalidation entry point

This is branch-local implementation truth.
It does **not** by itself promote accepted baseline truth.

## Explicitly blocked moves

This program does not authorize:

- remote bind,
- multi-session or multi-client hosting,
- outbound OpenAI host control realization,
- Gemini runtime,
- generic runtime/service abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded loopback service shell.
