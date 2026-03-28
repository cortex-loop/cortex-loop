# CORTEX_V2_LIVE_VALIDATION_PROGRAM_0

Date: 2026-03-28
Status: active L2 live-testing environment brief with L2b/L2c host-native lifecycle follow-ons

## Purpose

This document records the second live-validation train over the accepted reference, OpenAI, Gemini, and Claude runtime/product shells.

The train is now split into two explicit live lanes:

- operator lane:
  - signed-in host-native product surfaces
  - primary acceptance-grade live truth
- automation lane:
  - API key or ADC-backed headless surfaces
  - secondary live truth for unattended reproducibility

The current bounded follow-on seam inside `L2` is:

- `L2b` OpenAI Codex App Server operator lifecycle proof
- `L2c` Claude and Gemini hook-backed operator lanes

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
- OpenAI signed-in operator truth is now explicitly split:
  - `codex exec` = smoke / preflight
  - `codex app-server` = lifecycle proof
- Claude and Gemini signed-in operator truth now records documented hook events alongside the CLI transcript surfaces
- Gemini signed-in operator truth may fall back from `gemini-2.5-pro` to `gemini-2.5-flash`
- no assisted retry loop, corrective second-pass intervention, or v1 bridge doctrine belongs in `L2b`

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

Current local evidence after the March 28 reruns:

- operator preflight:
  - Claude operator probe succeeds on `claude-sonnet-4-6`
  - Gemini operator probe succeeds on fallback `gemini-2.5-flash`
  - OpenAI/Codex operator probe succeeds on `gpt-5.3-codex`
- operator baselines:
  - Claude baseline succeeds twice on `claude-sonnet-4-6`
  - Gemini baseline succeeds twice on fallback `gemini-2.5-flash`
  - OpenAI baseline succeeds twice on `codex exec`
- operator product paths:
  - OpenAI App Server now succeeds on:
    - `pass_minimal` twice
    - `truth_gap`
    - `restart_continuity` twice
  - OpenAI lifecycle proof is now earned from the App Server event timeline; ephemeral `thread/read` remains lossy and is treated as a host caveat rather than a failed operator lane
  - Claude is now hook-backed and succeeds on:
    - `pass_minimal` twice
    - `truth_gap`
    - `restart_continuity`
  - Gemini is now hook-backed as well; at least one full `pass_minimal` run succeeds on explicit fallback `gemini-2.5-flash`, but quota/capacity retries still prevent repeat-stable Gemini closure
- automation lane:
  - current service path still fails honestly on missing automation credentials for all three providers

## Closeout law

`L2` is only honestly closed when all are true:

- Claude operator lane remains repeat-stable on the hook-backed path
- Gemini operator lane is either stable on `gemini-2.5-pro` or stably accepted on explicit fallback `gemini-2.5-flash`
- OpenAI operator lane remains stable on both:
  - `codex exec` smoke
  - `codex app-server` lifecycle proof
- at least one automation-lane host-control success exists per provider
- the local-only compare output is regenerated after the final reruns
- the OpenAI App Server follow-on row is updated truthfully under the live-validation gate section
- and the `L1`-`L4` gate rows are updated truthfully to the new L2 evidence state
