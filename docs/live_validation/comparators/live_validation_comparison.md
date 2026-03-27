# L1 Live Validation Comparison

- Generated at: `2026-03-27T13:53:26+00:00`
- Provider baseline successes: `0`
- Cortex live-path successes: `0`
- Verdict: **lifecycle-first is not yet paying off enough on real hosts**

The current line exposes live blockers honestly, but no provider completed a successful Cortex host-control validation run.

## Provider summary

### claude

- provider baseline successful runs: `0`
- provider baseline failure classes: `auth_expired`
- Cortex live successful runs: `0`
- Cortex live failure classes: `auth_missing`
- Cortex live total record count: `0`

### gemini

- provider baseline successful runs: `0`
- provider baseline failure classes: `capacity_exhausted`
- Cortex live successful runs: `0`
- Cortex live failure classes: `auth_missing`
- Cortex live total record count: `0`

### openai

- provider baseline successful runs: `0`
- provider baseline failure classes: `auth_missing`
- Cortex live successful runs: `0`
- Cortex live failure classes: `auth_missing`
- Cortex live total record count: `0`

## Next corrective seam

open one bounded live-auth alignment seam so the provider CLI sessions and the current A4/G4/O4 live transports can both prove fresh credentials without private-account drift
