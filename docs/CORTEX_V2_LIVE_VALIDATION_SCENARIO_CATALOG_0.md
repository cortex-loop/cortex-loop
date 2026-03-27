# CORTEX_V2_LIVE_VALIDATION_SCENARIO_CATALOG_0

Date: 2026-03-27
Status: active scenario catalog for the first L1 live-validation pass

## Purpose

This catalog records the common-core and host-tailored live scenarios for the L1 audit.
It is a support brief for evidence capture, not packet authority.

## Common-core scenarios

### `core_01_single_turn_summary`

- goal: one bounded summarization/transformation request
- evidence target:
  - verify that the provider baseline path starts cleanly
  - verify that the Cortex host-control path reaches the first action boundary
  - classify the first blocker honestly if the run does not complete

### `core_02_long_stream`

- goal: one prompt that should force multiple streamed chunks or blocks
- evidence target:
  - verify whether the provider baseline and Cortex path expose chunk cadence at all
  - classify whether the current blocker is auth/capacity or event-surface related

### `core_03_two_turn_restart`

- goal: two-step continuity/export-import audit
- evidence target:
  - verify that the current service export/import boundary remains reachable
  - prove that a successful first action and successful second action can survive restart once auth-model alignment exists

## Host-tailored scenarios

### `claude_01_messages_shape`

- goal: surface richer Claude Messages-shell structure when available
- current first-pass result: skipped after the initial Claude auth-expired blocker

### `gemini_01_stream_variance`

- goal: surface longer Gemini streaming cadence or candidate/content-block variance when available
- current first-pass result: skipped after the initial Gemini capacity-exhausted blocker

### `openai_01_long_responses`

- goal: surface longer OpenAI Responses streaming behavior when available
- current first-pass result: skipped after the initial OpenAI auth-missing blocker

## Blocker-collapse rule

The first L1 pass uses one explicit blocker-collapse rule:

- if a provider proves a high-signal blocker such as `auth_missing`, `auth_expired`, or `capacity_exhausted`,
- later scheduled runs for that same provider are recorded as skipped rather than rerunning the same low-signal failure repeatedly.

This keeps the evidence high-signal and cheap without pretending the blocked provider succeeded.
