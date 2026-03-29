# CORTEX_V2_LIVE_SERVICE_PROOF_0

Date: 2026-03-28
Status: active capable-machine service-proof contract with current-machine blocker note

## Purpose

This note records the first bounded automation auth-alignment and service-lane live-proof train over the current Claude, Gemini, and OpenAI loopback service paths.
It is a testing/support surface and does not open new runtime doctrine.

## Capable-machine entry condition

Actual service proof belongs only on a machine that satisfies all of:

- clean synced `main`
- provider CLIs installed for the intended providers
- automation auth readiness reads `ready` for the intended providers
- explicit spend approval env is present where required
- the current repo and local live-validation tooling are available unchanged

If those conditions are not met, the lawful outcome is `blocked` or `partial`, not “implemented anyway.”

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

Current local machine state after the March 29 reruns and current-machine N2 contract/tooling reruns:

- Claude automation auth: `missing`
- Gemini automation auth: `missing`
- OpenAI automation auth: `missing`
- repeated automation baseline reruns now stop immediately on auth readiness instead of attempting direct provider probes when machine auth is absent
- repeated bounded service-lane reruns stay blocked on `auth_missing` for:
  - `service_smoke`
  - `service_restart_continuity`
- no local service-lane live proof is yet earned
- this machine is explicitly out of scope for actual service proof execution until machine auth is intentionally reopened
- `N2` therefore remains blocked pending a properly provisioned capable machine

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
