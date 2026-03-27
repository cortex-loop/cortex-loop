# CORTEX_V2_LIVE_VALIDATION_PROGRAM_0

Date: 2026-03-27
Status: active L2 live-testing environment and auth-alignment brief

## Purpose

This document records the second live-validation train over the accepted reference, OpenAI, Gemini, and Claude runtime/product shells.

The train is now split into two explicit live lanes:

- operator lane:
  - signed-in host-native product surfaces
  - primary acceptance-grade live truth
- automation lane:
  - API key or ADC-backed headless surfaces
  - secondary live truth for unattended reproducibility

## Accepted parent

Accepted parent for this train:

- branch: `codex/l1-live-validation`
- commit: `8eb7f08`

This remains the refreshed-model baseline line:

- Claude `claude-sonnet-4-6`
- Gemini `gemini-2.5-pro`
- OpenAI `gpt-5.4`

The operator lane also carries a separate OpenAI coding-model preference:

- preferred: `gpt-5.3-codex`
- fallback: `gpt-5.4`

## L2 environment rules

- live artifacts are local-only under `.cortex/live_validation/`
- repo-tracked docs carry only summaries and verdicts
- signed-in host-native truth is primary
- current A4 / G4 / O4 service lanes remain secondary automation truth
- OpenAI signed-in operator truth uses `codex`, not `openai`
- Gemini signed-in operator truth may fall back from `gemini-2.5-pro` to `gemini-2.5-flash`

## Shared coding harness

The main payoff evidence now uses one tiny coding project rather than generic summary prompts.

Shared task:

- fix the `normalize_port()` upper-bound bug
- run `python -m pytest -q tests/test_normalize_port.py`
- keep the change minimal

Shared scenarios:

- `pass_minimal`
- `restart_continuity`
- `truth_gap`

Host caveats remain explicit and separate from the shared success lanes.

## Current L2 evidence

Current local evidence after the first L2 pass:

- operator preflight:
  - Claude session is present but token freshness is blocked (`auth_expired`)
  - Gemini operator probe succeeds on fallback `gemini-2.5-flash`
  - Codex operator probe succeeds on `gpt-5.3-codex`
- operator baselines:
  - Claude blocked on `auth_expired`
  - Gemini baseline is mixed and remains a watchlist
  - OpenAI baseline is clean on Codex
- operator product paths:
  - OpenAI succeeds on `pass_minimal`
  - OpenAI preserves `truth_gap`
  - OpenAI succeeds on `restart_continuity`
  - Claude remains blocked on auth freshness
  - Gemini operator product lane remains unresolved and is not yet counted as success
- automation lane:
  - current service path still fails honestly on missing automation credentials for all three providers

## Closeout law

`L2` is only honestly closed when all are true:

- Claude operator lane is re-proven after auth refresh
- Gemini operator lane is either stable on `gemini-2.5-pro` or stably accepted on explicit fallback `gemini-2.5-flash`
- OpenAI operator lane remains stable on Codex
- at least one automation-lane host-control success exists per provider
- the local-only compare output is regenerated after the final reruns
- and the `L1`-`L4` gate rows are updated truthfully to the new L2 evidence state
