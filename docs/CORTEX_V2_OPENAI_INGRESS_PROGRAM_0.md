# CORTEX_V2_OPENAI_INGRESS_PROGRAM_0

Date: 2026-03-26
Status: active runtime-program brief for the first OpenAI raw-transcript ingress shell

## Purpose

This document opens the next explicit one-agent product/runtime program after accepted `O1`.

The chosen next move is:

- one OpenAI raw-transcript ingress parser,
- one OpenAI ingress CLI over raw host transcript records,
- one bounded ingress continuity proof on top of accepted `O1`,
- and one re-audit closeout that keeps real host-shaped ingress ahead of broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/o1-openai-runtime-shell`
- commit: `93f7093`

Why this program opens now:

- accepted `O1` made one real OpenAI host-event shell lawful,
- the next one-agent north-star gap is host-shaped ingress rather than more wrapper-shaped local driving,
- this moves the product shell closer to real host traffic without opening outbound host control or service doctrine,
- and it is a smaller truthful step than Gemini breadth or multi-agent orchestration.

## Locked scope

This program remains:

- OpenAI only,
- single-agent only,
- local CLI only,
- ingress-only,
- packet-subordinate,
- and transcript-shaped.

This program adds only:

- `OpenAIHostEventEnvelope`
- `parse_openai_host_event_envelope()`
- `python3 -m cortex.runtime.openai_ingress_cli`
- raw-transcript fixtures and split-run ingress proof

This program does **not** authorize:

- live network/service doctrine,
- outbound OpenAI host control realization,
- generic runtime abstraction,
- Gemini runtime,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded ingress shell.

## Public runtime contract

The OpenAI ingress shell exposes:

- `python3 -m cortex.runtime.openai_ingress_cli`

Input remains JSONL via stdin or `--event-file`.

Each input line must be one raw OpenAI-style transcript object with:

- required field: `type`
- all remaining top-level fields interpreted as payload

Rejected input shapes:

- missing `type`
- non-string `type`
- canonical Cortex names such as `external/observation`
- the dev-shell wrapper shape `{event_name, payload}`
- any mixed wrapper/transcript record that contains `event_name` or `payload`

Output remains exactly the accepted `O1` OpenAI runtime record shape and field order.

## Runtime law for this program

The ingress shell may:

- parse raw transcript objects into `OpenAIHostEventEnvelope`,
- call accepted `run_openai_runtime_step(envelope.event_type, envelope.payload, session)`,
- reuse accepted `O1` session persistence unchanged,
- and emit the existing OpenAI runtime projection without widening the runtime shell itself.

It may not:

- bypass the raw-host-event validator,
- accept the dev-shell wrapper shape,
- accept mixed wrapper/transcript records,
- introduce live network/service doctrine,
- realize outbound OpenAI host actions,
- or introduce a shared ingress/runtime-common layer.

Undocumented-event law:

- undocumented raw `response.*` host events remain lawful input,
- they must still degrade to explicit conservative warnings,
- and the shell may not fabricate documented parity where none exists.

## O2 equivalence contract

For a transcript mechanically equivalent to an accepted `O1` dev-shell event stream, `O2` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

As in `C1` and `O1`, exact byte-for-byte replay of `session_summary.budget_history` and `session_summary.brake_history` is not required.
Those remain public diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `O2A` program lock
2. `O2B` raw-transcript parser boundary
3. `O2C` ingress CLI shell
4. `O2D` ingress continuity proof
5. `O2E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`O2` is only honestly closed when all are true:

- transcript records with `type` parse lawfully,
- wrapper-shape `{event_name, payload}` records are explicitly rejected,
- mixed wrapper/transcript records are explicitly rejected,
- canonical Cortex event names are explicitly rejected,
- documented raw transcript records drive the accepted `O1` shell without changing its output contract,
- split-run ingress continuity matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-openai-ingress`, `make test-smoke`, and `make verify` pass,
- and the `O2` phase-gate row is updated truthfully.

## Current branch-local state

On branch `codex/o2-openai-ingress-shell` opened from accepted `O1` closeout head `93f7093`:

- `OpenAIHostEventEnvelope` and `parse_openai_host_event_envelope()` now exist as branch-local `O2` candidate surfaces,
- `python3 -m cortex.runtime.openai_ingress_cli` now drives the accepted `O1` runtime shell from raw transcript records,
- wrapper-shaped and mixed wrapper/transcript records are explicitly rejected at ingress,
- canonical Cortex event names are explicitly rejected at ingress,
- split-run ingress continuity proof now exists against the `O2` contract,
- and `make revalidate-openai-ingress` now exists as the repo-local ingress revalidation entry point.

This is branch-local implementation truth.
It does **not** by itself promote accepted baseline truth.

## Explicitly blocked moves

This program does not authorize:

- outbound OpenAI host control,
- live network/service doctrine,
- Gemini ingress/runtime,
- generic ingress/runtime abstraction,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded raw-transcript ingress shell.
