# Cortex Codex App/CLI Hook Contract And Capture Boundary Remediation

Surface: product / structural proof

Remediation date: 2026-05-05

Verdict: structural pass. The Codex App/CLI product hook client now serializes
prospective task-standard context with Codex's native
`hookSpecificOutput.additionalContext` shape for `UserPromptSubmit`, while Stop
blocks continue to use the already-proven `{"decision":"block","reason":"..."}`
shape.

## What Changed

- `UserPromptSubmit` task-standard context now emits:
  `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"..."}}`.
- The old flat `{"context": ...}` shape is rejected by product and lab tests.
- Hook diagnostics extract rendered-text hashes from either Stop `reason` or
  nested `additionalContext`, while preserving the raw stdout payload.
- `--disable-stop-blocks` was added so task-standard capture probes can allow
  `UserPromptSubmit` context while suppressing Stop block output.
- `--disable-model-visible-blocks` remains available for silent comparison arms
  that must suppress every model-visible hook payload.

## Evidence

The structural task-standard Gate 0 passed after the contract fix:

```bash
python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-live-gate0 --require-pass
```

The report preserved the signed context hash
`9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`,
captured three standard items from simulated assistant output, kept malformed
standard blocks diagnostic-only, loaded no runtime snapshot, and left root
`.codex/config.toml` unchanged.

## Not Earned

- No live Codex rerun was performed in this seam.
- No prework task-standard capture from a real model turn is earned.
- No behavior lift, output-quality lift, downstream task-standard gating,
  signed-text change, Stop-text change, SRE law change, parser change, selector
  change, hidden-verifier perception, root-hook activation, or shipping
  promotion is earned.

## Next Decision

Queue `codex-app-cli-task-standard-context-live-rerun`. The next seam should run
the isolated live task-standard probe with Codex-native
`hookSpecificOutput.additionalContext` and `--disable-stop-blocks`. If the model
still does not produce a pre-tool standard block, the next decision is a lawful
delivery-path decision rather than text tuning or SRE-law weakening.
