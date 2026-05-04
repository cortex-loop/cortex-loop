# Cortex Codex App/CLI Product Perception Loop

Surface: product / structural hook perception proof

Probe date: 2026-05-04

## Summary

This seam removed the canary-only dependency on a prewritten runtime snapshot
for the Codex App/CLI Stop path. The product hook coordinator can now derive a
bounded runtime snapshot from product-observable lifecycle state:

```text
UserPromptSubmit / tool / Stop payloads
-> private per-session state
-> ExpectationLedger + resolution deficit
-> grounded intervention selector
-> identity-continuous Stop block JSON or silence
```

The coordinator still accepts explicit runtime snapshots for actuator probes and
backward-compatible structural tests, but the product path no longer requires
one to select the overdue-verification Stop intervention.

## What Changed

- `UserPromptSubmit` starts task-local private state silently.
- Verification-like successful tool events are recorded as product-observed
  verification evidence.
- `PostToolUseFailure` continues to add private warning pressure without model
  text.
- A transcript-backed Stop closure claim opens a due verification expectation
  only when a product task-set anchor exists and no active verification
  expectation is already open.
- The Stop path derives `ResolutionDeficitState` and `DebtControlPressure` from
  the session `ExpectationLedger` when no caller snapshot is supplied.
- Waiting, blocked, narrowed, or retracted assistant responses stay silent.
- Live canary stdout is now captured for future response-analysis probes.

## Structural Evidence

Product tests now cover:

- prompt then closure claim, with no runtime snapshot, blocks with the locked
  identity-continuous overdue-verification text;
- observed verification command then closure claim stays silent and resolves the
  expectation;
- waiting/blocker response stays silent;
- Stop with no product perception state stays silent;
- explicit snapshot activation remains supported for actuator-only probes;
- hook client diagnostics distinguish caller snapshot stimuli from
  product-derived state.

Lab Gate 0:

```bash
python3 lab/codex_app_cli_stop_activation_probe.py --product-perception-gate0 --require-pass
```

Passed with:

- no runtime snapshot fixture;
- root `.codex/config.toml` unchanged;
- isolated subject config containing only the product hook client;
- prompt/tool/Stop simulated Codex payloads producing the expected block or
  silence decisions.

The product-perception Gate 0 report is under
`.cortex/live_validation/openai/codex_app_cli_stop_activation_probe/product_perception_gate0/`.

## Truth Boundaries

Earned:

- Structural product perception on the Codex App/CLI Stop path.
- Runtime state can be derived from product-observable lifecycle payloads rather
  than a generic canary snapshot.
- The derived state uses the existing `ExpectationLedger`,
  `ResolutionDeficitState`, `DebtControlPressure`, grounded intervention
  selector, and identity-continuous renderer.
- Clean controls for observed checks and blocker/waiting responses stay silent.

Not earned:

- No live model behavior lift.
- No live proof that a real Codex session emits enough `UserPromptSubmit`,
  `PostToolUse`, and Stop payloads for this derived state in the wild.
- No hidden-verifier, lab-oracle, task-identity, or fixture-prompt perception.
- No PreToolUse motor-inhibition policy beyond state collection scaffolding.
- No broad Codex App versus Codex CLI parity claim.

## Next Move

Run a narrow hook-native product-perception live probe without passing a runtime
snapshot. The probe should verify that real Codex lifecycle payloads populate
the private state, that Stop blocks only from the derived product state, and that
stdout/transcript artifacts capture what the model does after receiving the
block reason. Behavior lift remains a later comparison seam.
