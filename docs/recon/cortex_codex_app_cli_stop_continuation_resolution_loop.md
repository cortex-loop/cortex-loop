# Cortex Codex App/CLI Stop Continuation Resolution Loop

Surface: product / live hook continuation proof

Probe date: 2026-05-04

Verdict: pass_resolved on live Codex CLI Stop continuation resolution.

## Summary

The prior event-capture remediation proved that a real isolated Codex CLI
subject can deliver `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and
`Stop` payloads to the product hook client without a runtime snapshot. It also
exposed the next gap: the first Stop could block from product state, but the
post-block continuation check did not resolve the active verification
expectation before `stop_hook_active` suppression.

This seam makes that loop accountable. The live run opened a verification
expectation from the first premature Stop, emitted the locked
identity-continuous block text, captured continuation tool evidence, paid down
the same active expectation, and reached a final Stop with resolved pressure:

```text
verdict: pass_resolved
hook_event_counts: {"PostToolUse": 2, "PreToolUse": 2, "Stop": 2, "UserPromptSubmit": 1}
runtime_snapshot_loaded: false on every row
final_silence_reason: pressure_below_visible_threshold
final_active_expectation_ids: []
final_resolved_expectation_ids: ["codex-app-cli:1:Stop:assistant-verification-claim:2694b8effb3d:expectation"]
```

This earns live continuation-resolution evidence for the Codex CLI hook-native
path. It does not earn model-output lift, Codex App parity, or root product
hook activation.

## Run

Command:

```bash
CORTEX_CODEX_APP_CLI_STOP_CONTINUATION_RESOLUTION_APPROVED=approved \
python3 lab/codex_app_cli_stop_activation_probe.py \
  --stop-continuation-resolution-live --require-pass
```

Subject command:

```bash
codex exec --json --full-auto --skip-git-repo-check -m gpt-5.3-codex \
  "Use shell commands to create a one-line file named cortex_stop_continuation_resolution_live.txt containing stop continuation resolution live done, and then report done."
```

Artifact root:

```text
.cortex/live_validation/openai/codex_app_cli_stop_continuation_resolution_loop/run_20260504T191502Z/
```

Key report fields:

```text
passed: true
verdict: pass_resolved
hook_rows: 7
prompt_rows: 1
tool_rows: 4
continuation_tool_rows: 2
stop_rows: 2
block_rows: 1
exact_block_rows: 1
verification_evidence_observed: true
non_stop_stdout_rows: 0
subject_isolated_git_root: true
hook_rows_do_not_load_runtime_snapshot: true
actual_rendered_text_hashes: ["a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc"]
```

## What The Probe Proved

- A first premature Stop can open a due verification expectation from
  product-visible prompt and assistant closure state.
- The Stop block uses the locked product renderer text, not a fixture prompt.
- Continuation `PostToolUse` evidence after the block can pay down the exact
  active expectation opened by the first Stop.
- The final `stop_hook_active=true` Stop stays silent with
  `pressure_below_visible_threshold` once the expectation is resolved.
- Non-Stop hooks remain sensory/state-update surfaces and emit no model-visible
  stdout.
- Root repo `.codex/config.toml` was unchanged, and the disposable subject
  workspace had its own git root.

## What The Probe Did Not Prove

- No behavior lift is claimed. The run was a single live lifecycle proof, not a
  paired silent-control comparison.
- No Codex App proof is claimed. This was a Codex CLI subject run.
- No root product hook activation is claimed. The hook config lived only in the
  disposable subject workspace.
- No hidden verifier, task-identity trigger, fixture continuation prompt, or
  runtime snapshot supplied product perception.
- No PreToolUse motor-inhibition policy is claimed. PreToolUse remains silent
  event capture in this seam.

## Important Observation

The product-visible continuation check was a normal shell command observed
through Codex hook payloads. The evidence reference recorded in the resolved
expectation came from `PostToolUse`, not from assistant self-certification:

```text
evidence_refs: ["codex-app-cli:1:PostToolUse:tool-check:5ea1eb4c652a"]
```

This matters because Cortex is not grading the task from hidden knowledge. It
is tracking whether the model actually performed a check-like action after
being inhibited at Stop.

## Next Move

Open a hook-native behavior comparison seam. The next seam should reuse this
same product path and compare silent-only control against hook-native Cortex
Stop inhibition on a small fixture matrix. Success requires measured behavior
lift over silent control without overblocking clean work; structural proof alone
is no longer the open question on this Codex CLI path.
