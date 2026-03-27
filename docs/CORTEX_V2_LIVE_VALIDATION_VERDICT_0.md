# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-03-27
Status: first L1 live-validation verdict note

## Verdict

**lifecycle-first is not yet paying off enough on real hosts**

Reason:

- the current line exposes live blockers honestly,
- but zero providers completed a successful Cortex host-control validation run on this pass.

## Evidence summary

### Claude

- direct provider baseline: `auth_expired`
- Cortex live product path: `auth_missing`
- interpretation:
  - the CLI session exists, but it is not fresh enough for a real provider call
  - the current A4 live product path still requires `ANTHROPIC_API_KEY`

### Gemini

- direct provider baseline: `capacity_exhausted`
- Cortex live product path: `auth_missing`
- interpretation:
  - the installed CLI is current, but `gemini-2.5-pro` is not currently runnable through the provider baseline path
  - the current G4 live product path still requires `GEMINI_API_KEY`

### OpenAI

- direct provider baseline: `auth_missing`
- Cortex live product path: `auth_missing`
- interpretation:
  - the OpenAI CLI is installed, but both the baseline and the current O4 live product path still require `OPENAI_API_KEY`

## What the first pass still proves

The first pass is not valueless.
It proves:

- the toolchain-update step is real and repeatable,
- the direct-provider and Cortex live-product harnesses are real,
- the current shells fail with explicit typed blockers rather than silent hangs or fabricated parity,
- and the continuity/export boundary remains reachable even when the live action itself fails.

That is useful, but it is still below the threshold needed to claim that lifecycle-first is already paying off on real hosts.

## Next corrective seam

Open one bounded **live-auth alignment** seam that:

- refreshes the Claude CLI token or equivalent live auth surface,
- supplies the env-key auth the accepted A4 / G4 / O4 transports actually require,
- and picks a subscription-runnable Gemini live model if `gemini-2.5-pro` remains capacity-blocked.

After that seam lands, rerun:

- `make live-preflight`
- `make live-provider-baselines`
- `make live-cortex-host-control`
- `make live-compare`
