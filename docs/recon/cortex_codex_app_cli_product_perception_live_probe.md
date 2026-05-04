# Cortex Codex App/CLI Product Perception Live Probe

Surface: product / live hook perception proof

Probe date: 2026-05-04

Verdict: scoped negative on live Codex CLI project-hook payload sufficiency.

## Summary

The no-snapshot live probe ran a real isolated Codex CLI subject workspace with
the product Stop hook client installed and no `--runtime-snapshot` argument.
The root repo `.codex/config.toml` was unchanged, project hooks loaded, the hook
client wrote diagnostics, and no runtime snapshot was loaded.

The probe did not earn product-perception success. The live hook diagnostics
contained only `Stop` events:

```text
hook_event_counts: {"Stop": 3}
scoped_negative: codex_cli_live_hooks_exposed_stop_only_no_product_task_events
```

The coordinator therefore stayed silent with `missing_product_perception_state`
on the first Stop and `stop_hook_active` on the two later Stop events. No block
JSON was emitted and no product-rendered text reached the model in this
no-snapshot run.

## Run

Command:

```bash
CORTEX_CODEX_APP_CLI_PRODUCT_PERCEPTION_LIVE_APPROVED=approved \
python3 lab/codex_app_cli_stop_activation_probe.py \
  --product-perception-live --require-pass
```

Subject command:

```bash
codex exec --json --full-auto --skip-git-repo-check -m gpt-5.3-codex \
  "Create a one-line file named cortex_product_perception_live.txt containing product perception live done. Then report done."
```

Artifact root:

```text
.cortex/live_validation/openai/codex_app_cli_product_perception_live_probe/run_20260504T165913Z/
```

Key report fields:

```text
passed: false
verdict: scoped_negative
hook_rows: 3
stop_rows: 3
block_rows: 0
exact_block_rows: 0
continuation_rows: 2
runtime_snapshot_loaded: false on every row
root_config_unchanged: true
subject_config_omits_runtime_snapshot: true
```

## What The Probe Proved

- A real isolated Codex CLI project run loaded the product hook client.
- The subject hook config omitted `--runtime-snapshot`.
- The root repo Mission Reflection guardrail config was not modified.
- The product hook client persisted live diagnostics and trajectory rows.
- The hook client correctly stayed silent instead of inventing product
  perception when the only live lifecycle rows were Stop events.

## What The Probe Did Not Prove

- No product-perception success: no `UserPromptSubmit`, `PreToolUse`,
  `PostToolUse`, or `PostToolUseFailure` rows reached the product hook client.
- No no-snapshot Stop block: product state never acquired the task-set or tool
  evidence needed to open or pay down an expectation.
- No behavior lift: there was no paired comparison and no Cortex text reached
  the model in this no-snapshot probe.
- No Codex App proof: this was a Codex CLI subject run; App and CLI actuator
  evidence remain partitioned.

## Important Observation

The Codex JSON stdout stream did include model-visible work events:

- command execution to write `cortex_product_perception_live.txt`;
- command execution to read the file back;
- assistant output that reported the file verified.

Those events did not arrive as project hook lifecycle payloads. The product hook
state stayed at `prompt_text_hash: null`, `current_step: 0`,
`tool_event_count: 0`, `verification_evidence_count: 0`, and an empty
`ExpectationLedger`.

That is the live gap: the host has event information in the `codex exec --json`
stream, but the current project hook path does not deliver that information to
the product hook coordinator before Stop.

## Next Move

Open a remediation seam for Codex App/CLI product event capture. The seam should
test whether non-Stop hooks can be configured and observed on this surface; if
they cannot, it should adapt the live Codex JSON event stream or transcript as a
product event source without using hidden verifier facts, runtime snapshots,
fixture prompts, or task identity. Only after product task/tool events populate
the coordinator state should the no-snapshot Stop block probe rerun.
