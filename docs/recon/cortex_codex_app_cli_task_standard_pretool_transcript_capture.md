# Codex App/CLI Task-Standard PreTool Transcript Capture

Surface: product + lab proof

Date: 2026-05-05

## Summary

This seam completes the task-standard capture boundary exposed by the prior
live run. Codex-native `UserPromptSubmit` context reached the model and the
model wrote the requested `Work standard` / `Likely misses` / `Closure
evidence` block before the first command, but Cortex did not ingest that
assistant-authored transcript message into `TaskStandardSpine`.

The fix adds product-visible transcript ingestion to the OpenAI Codex App/CLI
coordinator. On `PreToolUse`, with `PostToolUse` as fallback, Cortex reads the
Codex `transcript_path`, extracts assistant-authored standard messages that
appear before the first tool/function call, and stores the first valid block
through the existing SRE `store_assistant_standard_block(...)` path. Developer
context, user prompt text, tool calls, tool outputs, hidden verifier data, and
task identity are ignored.

This seam is stacked on the unmerged communication-boundary remediation branch
because the implementation depends on its Codex-native `additionalContext`
contract and proof ladder hardening.

## Product Boundary

This is product Cortex because it repairs a direct model-I/O path:

Codex `UserPromptSubmit` `hookSpecificOutput.additionalContext` -> model
prework standard message in the Codex transcript -> `PreToolUse` hook reads
product-visible `transcript_path` -> `TaskStandardSpine.standard_items` stores
the model-derived standard before tool evidence is scored.

It does not change signed task-standard text, Stop text, SRE law, selector
thresholds, root hook configuration, PreToolUse blocking, runtime snapshots, or
behavior-lift claims.

## What Changed

- `cortex/hosts/openai/codex_app_cli_hook_coordinator.py` now ingests
  pre-tool transcript messages for task-standard capture on `PreToolUse`, with
  `PostToolUse` fallback.
- Transcript capture accepts assistant `response_item` messages and `event_msg`
  agent messages only.
- Capture stops at the first tool/function boundary and refuses standard blocks
  that appear after tool use begins.
- Missing, unreadable, or malformed transcript data stays private and silent.
- Existing Stop `last_assistant_message` standard capture remains supported and
  idempotent.
- `lab/codex_app_cli_stop_activation_probe.py --task-standard-live-gate0`
  now requires the live-equivalent `PreToolUse` transcript case to capture all
  three standard items before tool evidence is scored.
- `lab/codex_app_cli_stop_activation_probe.py --task-standard-pretool-transcript-replay`
  replays the prior live Codex transcript shape without live spend and proves
  state capture from product-visible transcript data.

## Evidence

Structural proof:

- Product coordinator tests cover valid pre-tool transcript capture, developer
  context exclusion, post-tool fallback, standards after first function call,
  malformed transcript data, and evidence alignment after capture.
- Lab Gate 0 now reports:
  - `host_stdout_contract_ok=true`
  - `model_assimilation_observed=true`
  - `state_capture_observed=true`
  - `gate_used_captured_state=false`
  - `behavior_lift_claim_allowed=false`
- The replay harness reads
  `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T195300Z`
  and captures three standard items from the live Codex transcript before tool
  evidence, without running Codex again.

Validation commands run:

- `python3 -m pytest tests/product/test_openai_codex_app_cli_hook_coordinator.py -q`
- `python3 -m pytest tests/lab/test_codex_app_cli_stop_activation_probe.py -q`
- `python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-live-gate0 --require-pass`
- `python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-pretool-transcript-replay --require-pass`

## Not Earned

This seam does not earn live rerun success, downstream gating integration,
PreToolUse motor inhibition, output-quality lift, behavior lift, Codex App
parity, or shipping promotion. The replay proves that the previous live
transcript shape is now ingestible; a live rerun is still needed to record fresh
end-to-end capture under the current code.

## Next

Queue `codex-app-cli-task-standard-live-capture-rerun`. The next seam should
run the already-built live task-standard probe again with the transcript capture
fix in place. If it records `pass_prework_standard_capture`, the following
implementation seam may connect captured standards to Stop gating. If it still
fails, treat that as a host timing/capture finding rather than text tuning.
