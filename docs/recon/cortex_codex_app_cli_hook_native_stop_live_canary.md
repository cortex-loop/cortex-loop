# Cortex Codex App/CLI Hook-Native Stop Live Canary

Surface: product / live actuator proof

Probe date: 2026-05-04

## Summary

This seam ran the isolated Codex App/CLI product Stop-hook live canary. The
proof is actuator-only:

```text
real Codex Stop payload -> product hook client -> coordinator -> renderer
-> Codex Stop block JSON -> stop-hook continuation
```

The canary used the disposable subject workspace under
`.cortex/live_validation/openai/codex_app_cli_stop_activation_probe/` and left
root `.codex/config.toml` unchanged. The generic overdue-verification runtime
snapshot remained an actuator stimulus only; it was not evidence that Cortex
perceived a real task gap.

## Command

Structural Gate 0:

```bash
python3 lab/codex_app_cli_stop_activation_probe.py --require-pass
```

Live canary:

```bash
CORTEX_CODEX_APP_CLI_STOP_ACTIVATION_APPROVED=approved python3 lab/codex_app_cli_stop_activation_probe.py --live-canary --require-pass
```

No general live-spend approval environment variable was set, and the root repo
Mission Reflection hook configuration was not modified or reused.

## Evidence

Gate 0 passed again before the live run:

- normal Stop with transcript-backed assistant turn returned exact block JSON;
- title/null-transcript Stop stayed silent;
- `stop_hook_active=true` continuation stayed silent;
- non-Stop lifecycle event emitted no stdout;
- missing snapshot and malformed input failed open with stderr diagnostics;
- root `.codex/config.toml` hash stayed unchanged.

The live canary passed:

- model: `gpt-5.3-codex`;
- command: `codex exec --json --full-auto --skip-git-repo-check -m gpt-5.3-codex`;
- hook rows: `3`;
- block rows: `1`;
- continuation rows with `stop_hook_active=true`: `2`;
- runtime snapshot hash: `78ec21f05804e266159d6df31cf7d8aa83dd4293c6a87f989a3609ac69680436`;
- actual rendered-text hash: `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`;
- scoped negative: none.

The first live Stop row returned exact block JSON with the locked
identity-continuous text:

```json
{"decision":"block","reason":"Wait, did I actually check my work properly. I don't want to hand this off and have someone find the gap because I rushed it. I should run a check, narrow what I'm claiming, or leave it open and be honest about it."}
```

The two later Stop rows were continuation events with `stop_hook_active=true`
and stayed silent.

## Truth Boundaries

Earned:

- Live Codex App/CLI Stop actuator proof for the product hook client.
- Proof that a real host Stop payload can reach
  `cortex.hosts.openai.codex_app_cli_hook_client`.
- Proof that selected identity-continuous Cortex text can become Codex Stop
  block JSON on a live canary run.
- Proof that Stop-hook continuation events are detected and stay silent.

Not earned:

- No product perception claim. The runtime snapshot was a canary stimulus, not
  runtime state derived from real task evidence.
- No model-output behavior-lift claim.
- No proof for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, or
  `PostToolUseFailure` product perception.
- No broad Codex App versus Codex CLI parity claim beyond this isolated
  `codex exec` subject run.
- No shipping promotion beyond the already-recorded `openai.codex_app_cli`
  product target.

## Next Move

Build the Codex App/CLI product perception loop. The next seam should derive the
runtime snapshot from product-observable lifecycle events rather than a generic
canary stimulus, while preserving the same Stop actuator boundaries proven here.
