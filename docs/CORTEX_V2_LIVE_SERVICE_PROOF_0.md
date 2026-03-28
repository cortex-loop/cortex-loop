# CORTEX_V2_LIVE_SERVICE_PROOF_0

Date: 2026-03-28
Status: active service-lane live-proof note

## Purpose

This note records the first bounded automation auth-alignment and service-lane live-proof train over the current Claude, Gemini, and OpenAI loopback service paths.
It is a testing/support surface and does not open new runtime doctrine.

## Auth policy

- Claude automation:
  - `ANTHROPIC_API_KEY`
- Gemini automation:
  - `vertex_adc` first
  - `GEMINI_API_KEY` second
- OpenAI automation:
  - `OPENAI_API_KEY`

Signed-in CLI sessions do **not** count as service-lane auth.

## Current local state

Current local machine state after the first service-proof pass:

- Claude automation auth: `missing`
- Gemini automation auth: `missing`
- OpenAI automation auth: `missing`
- no local service-lane live proof is yet earned

## Closeout law

The service-proof train is only honestly closed when all are true:

- Claude automation lane lands on:
  - one successful smoke action
  - one successful restart/import/export continuity run
- Gemini automation lane lands on:
  - one successful smoke action
  - one successful restart/import/export continuity run
- OpenAI automation lane lands on:
  - one successful smoke action
  - one successful restart/import/export continuity run
- package-level service proof is updated truthfully in `docs/CORTEX_V2_PHASE_GATES_2.md`

If any host remains blocked on auth, spend policy, quota, or transport failure:

- keep the host row partial or blocked
- keep package-level service proof partial or blocked
- do not use that as justification to open assistance
