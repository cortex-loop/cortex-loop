# CORTEX_V2_GEMINI_INGRESS_PROGRAM_0

Surface: experimental

Date: 2026-03-27
Status: accepted re-audited runtime-program brief for the first Gemini raw-transcript ingress shell

## Purpose

This document records the raw-transcript ingress slice inside the accepted G1 Gemini runtime/product parity line.

The chosen next move is:

- one Gemini raw-transcript ingress parser,
- one Gemini ingress CLI over raw host transcript records,
- one bounded ingress continuity proof on top of the current-line Gemini runtime shell,
- and one re-audit closeout that keeps real host-shaped ingress ahead of broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/experimental/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`
- `docs/experimental/CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/k3-executive-live-outcome`
- commit: `efe003e`

Why this program opens now:

- the current line now includes one real Gemini host-event shell,
- the next one-agent north-star gap is host-shaped ingress rather than more wrapper-shaped local driving,
- this moves the product shell closer to real host traffic without opening outbound host control or service doctrine,
- and it is a smaller truthful step than Gemini breadth or multi-agent orchestration.

## Locked scope

This program remains:

- Gemini only,
- single-agent only,
- local CLI only,
- ingress-only,
- packet-subordinate,
- and transcript-shaped.

This program adds only:

- `GeminiHostEventEnvelope`
- `parse_gemini_host_event_envelope()`
- `python3 -m cortex.hosts.gemini.ingress_cli`
- raw-transcript fixtures and split-run ingress proof

This program does **not** authorize:

- live network/service doctrine,
- outbound Gemini host control realization,
- generic runtime abstraction,
- Gemini service doctrine,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded ingress shell.

## Public runtime contract

The Gemini ingress shell exposes:

- `python3 -m cortex.hosts.gemini.ingress_cli`

Input remains JSONL via stdin or `--event-file`.

Each input line must be one raw Gemini-style transcript object with:

- required field: `type`
- all remaining top-level fields interpreted as payload

Rejected input shapes:

- missing `type`
- non-string `type`
- canonical Cortex names such as `external/observation`
- the dev-shell wrapper shape `{event_name, payload}`
- any mixed wrapper/transcript record that contains `event_name` or `payload`

Output remains exactly the current-line Gemini runtime record shape and field order.

## Runtime law for this program

The ingress shell may:

- parse raw transcript objects into `GeminiHostEventEnvelope`,
- call accepted `run_gemini_runtime_step(envelope.event_type, envelope.payload, session)`,
- reuse the current-line Gemini session persistence unchanged,
- and emit the existing Gemini runtime projection without widening the runtime shell itself.

It may not:

- bypass the raw-host-event validator,
- accept the dev-shell wrapper shape,
- accept mixed wrapper/transcript records,
- introduce live network/service doctrine,
- realize outbound Gemini host actions,
- or introduce a shared ingress/runtime-common layer.

Undocumented-event law:

- undocumented raw `response.*` host events remain lawful input,
- they must still degrade to explicit conservative warnings,
- and the shell may not fabricate documented parity where none exists.

## G2 equivalence contract

For a transcript mechanically equivalent to the current-line Gemini dev-shell event stream, `G2` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

As in `C1` and `G1`, exact byte-for-byte replay of `session_summary.budget_history` and `session_summary.brake_history` is not required.
Those remain public diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `G2A` program lock
2. `G2B` raw-transcript parser boundary
3. `G2C` ingress CLI shell
4. `G2D` ingress continuity proof
5. `G2E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`G2` is only honestly closed when all are true:

- transcript records with `type` parse lawfully,
- wrapper-shape `{event_name, payload}` records are explicitly rejected,
- mixed wrapper/transcript records are explicitly rejected,
- canonical Cortex event names are explicitly rejected,
- documented raw transcript records drive the current-line `G1` shell without changing its output contract,
- split-run ingress continuity matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-gemini-ingress`, `make test-smoke`, and `make verify` pass,
- and the `G2` phase-gate row is updated truthfully.

## Current accepted state after G1 closeout

On the accepted G1 closeout line over accepted K3 baseline `efe003e`:

- `GeminiHostEventEnvelope` and `parse_gemini_host_event_envelope()` are now landed `G2` surfaces, implemented at G1 proof head `fe33a7e`
- `python3 -m cortex.hosts.gemini.ingress_cli` now drives the current-line `G1` runtime shell from raw transcript records
- wrapper-shaped and mixed wrapper/transcript records are explicitly rejected at ingress
- canonical Cortex event names are explicitly rejected at ingress
- repeated direct reruns plus repeated `make revalidate-gemini-ingress` passed for current scope

## Explicitly blocked moves

This program does not authorize:

- outbound Gemini host control,
- live network/service doctrine,
- Gemini ingress/runtime,
- generic ingress/runtime abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded raw-transcript ingress shell.
