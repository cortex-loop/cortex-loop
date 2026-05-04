# Cortex Codex App/CLI Hook-Native Stop Activation Probe

Surface: product / structural activation proof

Probe date: 2026-05-04

## Summary

This seam added the product hook client and isolated Gate 0 harness for the
OpenAI Codex App/CLI Stop actuator. The proof is enactment-only:

```text
simulated Codex Stop payload -> product hook client -> coordinator -> renderer
-> Codex Stop block JSON
```

The Gate 0 harness writes a disposable subject workspace under
`.cortex/live_validation/openai/codex_app_cli_stop_activation_probe/` with a
product-only Stop hook command. Root `.codex/config.toml` remains unchanged, so
the repo Mission Reflection guardrail is not reused as product Cortex.

Official Codex hook behavior makes that isolation load-bearing: matching hooks
can run together, and Stop hook block JSON is the model-visible continuation
surface. Product activation cannot be tested by placing a second product Stop
hook beside the repo workflow guardrail.

## What Changed

- `cortex.hosts.openai.codex_app_cli_hook_client` now reads Codex hook JSON from
  stdin, loads a caller-provided private runtime snapshot, calls the existing
  product coordinator, and emits no stdout on allow or silence.
- For a selected Stop directive it writes exactly:

```json
{"decision":"block","reason":"<identity-continuous text>"}
```

- Runtime snapshots decode product-shaped `ExpectationLedger`, `current_step`,
  optional `DebtControlPressure`, optional `ResolutionDeficitState`,
  closure/warning fields, and a minimal operator-route view. If the deficit is
  absent, the client computes it from the ledger and step.
- Client diagnostics record payload/coordinator state, runtime snapshot hash,
  actual rendered-text hash, stdout payload, and silence/fail-open reasons. The
  expectation id and selection trace remain private diagnostics only.
- Seam 1 text drift was corrected before activation: unsupported-claim text now
  cuts the claim back to what can honestly be stood behind, and capability-guard
  text now uses first-person self-check phrasing instead of "let's".

## Gate 0 Evidence

Command:

```bash
python3 lab/codex_app_cli_stop_activation_probe.py --require-pass
```

Artifact root:

```text
.cortex/live_validation/openai/codex_app_cli_stop_activation_probe/
```

Gate 0 passed:

- normal Stop with transcript-backed assistant turn returned exact block JSON;
- title/null-transcript Stop stayed silent;
- `stop_hook_active=true` continuation stayed silent;
- non-Stop lifecycle event emitted no stdout;
- missing snapshot and malformed input failed open with stderr diagnostics;
- subject config contained only the product hook command;
- root `.codex/config.toml` hash stayed unchanged.

## Truth Boundaries

Earned:

- Structural product hook-client enactment for the Codex App/CLI Stop actuator.
- Proof that selected identity-continuous Cortex text can be mapped to Codex Stop
  block JSON through the product coordinator.
- Proof that allow/silence paths emit no stdout and infrastructure failures fail
  open.
- Proof that root repo workflow guardrails are not imported, reused, or
  activated as product Cortex.

Not earned:

- No live Codex App or Codex CLI hook activation claim.
- No product perception claim. The generic overdue-verification snapshot is an
  actuator stimulus, not evidence that Cortex detected a real task gap.
- No model-output behavior lift.
- No Codex App to Codex CLI evidence transfer.
- No PreToolUse, PostToolUse, or full lifecycle hook-native product proof.

## Next Move

Run an explicitly approved live Stop canary as a separate evidence seam. That
canary should use the isolated subject config, preserve Codex App versus Codex
CLI evidence rows separately, and stop with a scoped negative finding if Codex
CLI does not load project hooks.
