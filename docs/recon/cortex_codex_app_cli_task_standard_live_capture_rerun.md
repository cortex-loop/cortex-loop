# Cortex Codex App/CLI Task-Standard Live Capture Rerun

Surface: product + lab proof

Date: 2026-05-05

## Summary

The fresh Codex CLI task-standard live rerun passed the capture boundary that
previous runs missed. The isolated subject workspace loaded only the product
hook client for `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`.
The signed prospective task-set context reached the model through Codex-native
`hookSpecificOutput.additionalContext`, the model wrote a compact
`Work standard` / `Likely misses` / `Closure evidence` block before tool
execution, and Cortex captured those three assistant-authored standard items
from `transcript_path` on the `PreToolUse` row.

This earns live context delivery, model assimilation, and product-visible
state capture for the task-standard spine. It does not earn behavior lift,
output-quality lift, Codex App parity, shipping promotion, or a claim that
captured standards have already improved model behavior.

## Live Command

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_LIVE_APPROVED=approved \
  python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-live
```

The live command was run without `--require-pass` so partial and negative
outcomes would have remained valid evidence.

## Artifact

- Output root:
  `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z`
- Report:
  `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z/report.json`
- Trajectory:
  `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z/trajectory.jsonl`
- Hook diagnostics:
  `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z/hook_client_diagnostics.jsonl`

## Verdict

`pass_prework_standard_capture`

Evidence fields:

- `host_stdout_contract_ok=true`
- `host_attached_context_observed=true`
- `model_assimilation_observed=true`
- `state_capture_observed=true`
- `gate_used_captured_state=false`
- `behavior_lift_claim_allowed=false`
- `prework_standard_capture=true`
- `standard_capture_rows=3`
- `first_standard_capture_index=2`
- `first_tool_index=2`
- `unexpected_text_rows=0`
- `runtime_snapshot_loaded=false` on hook rows
- root `.codex/config.toml` hash unchanged

The equal first-standard and first-tool indices reflect Codex's `PreToolUse`
boundary: the standard was captured on the pre-tool hook row for the first
tool call, before the tool executed and before `PostToolUse` evidence scoring.

## What Reached The Model

The signed context hash was:

`9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`

The subject model then produced the expected prework standard block in the
Codex JSON stream and session transcript before running the shell command.
Cortex captured the three standard items from the transcript path on
`PreToolUse` with source refs containing:

`pretool-transcript-standard`

## What Cortex Captured

The captured standard items were task-local and model-authored:

- `Work standard`: create `cortex_task_standard_live.txt` by shell with the
  exact one-line content, then read it back with shell.
- `Likely misses`: filename/content typo, trailing newline mismatch, or
  reporting completion without reading output.
- `Closure evidence`: shell output from `cat` shows the exact line and the
  assistant then reports done.

The following `PostToolUse` row then recorded claim-aligned evidence against
the visible obligation and work-standard item. The later `Stop` row surfaced
unmatched standard items in private diagnostics, but Stop blocks were disabled
for this probe. That suppressed Stop signal is not counted as model-visible
gate use.

## Boundary

Earned:

- real Codex CLI delivery of signed task-standard context;
- real model assimilation of the context into a prework standard block;
- product-visible transcript capture into `TaskStandardSpine` before tool
  evidence scoring;
- unchanged root repo hook configuration;
- no runtime snapshots or hidden verifier input.

Not earned:

- model-output lift;
- output-quality improvement;
- downstream Stop or PreToolUse gate effectiveness;
- Codex App parity;
- shipping promotion;
- any change to signed task-standard text, Stop text, SRE law, selector
  thresholds, or root repo hooks.

## Next Decision

The next product train should be a task-standard Stop-gating live probe: keep
the captured-standard path intact, enable the existing Stop block path, and
test whether captured standard/evidence mismatch can produce a lawful
model-visible closure intervention and continuation resolution. That next
probe must still avoid behavior-lift claims until a paired comparison beats
raw and silent controls.
