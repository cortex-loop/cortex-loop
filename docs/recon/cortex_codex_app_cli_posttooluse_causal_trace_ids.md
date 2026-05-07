# Cortex Codex App/CLI PostToolUse Causal Trace IDs

Surface: product diagnostics + lab trace proof

Verdict: `pass_posttooluse_actuator_trace_gate0`.

Evidence basis:

- Product diagnostics owner: `cortex/hosts/openai/codex_app_cli_hook_coordinator.py`.
- Lab trace owner: `lab/codex_app_cli_hook_native_behavior_comparison.py`.
- Shared trajectory projection: `lab/codex_app_cli_stop_activation_probe.py`.
- Gate 0 report: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_actuator_trace_gate0/gate0_report.json`.
- Historical replay artifact: `task_standard_posttooluse_live_20260507T153242Z`.

## Decision

The PostToolUse live readout is now gated on a causal tool-event reference
instead of ordinal alignment between PostToolUse hook rows and terminal command
rows. Codex hook diagnostics preserve `tool_use_id`; stdout-derived command
records preserve the matching command item id as `tool_event_ref`; and
`_posttooluse_context_trace(...)` joins the context-emitting PostToolUse row to
the stdout command record only through that reference.

If the stable reference is missing or duplicated, the trace is marked
`ambiguous` and no preceding or next tool is inferred by position. That makes
old artifacts without the persisted id conservative instead of overgenerous.

## Gate 0 Result

`--task-standard-posttooluse-actuator-trace-gate0 --require-pass` passed.

Pinned outcomes:

- a synthetic event-ref trace is non-ambiguous and uses `tool_event_ref`;
- the context source command is `printf 'alpha beta omega' > exact_result.txt`;
- the next tool after that context is the later direct check
  `od -An -t x1 -v exact_result.txt`;
- replay of `task_standard_posttooluse_live_20260507T153242Z` is marked
  ambiguous because the historical artifact lacks `tool_use_id`;
- the historical replay no longer counts artifact creation as the next action
  after the context that followed it;
- failed checks, missing artifacts, markerless rows, clean controls, blocker,
  waiting-on-user, and unrelated controls retain the existing silence behavior;
- no runtime snapshot, Stop block, PreToolUse denial, PermissionRequest policy,
  hidden scoring perception, or transport path appeared.

## Unchanged

This seam did not change signed UserPromptSubmit text, PostToolUse text, Stop
text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial, or
PermissionRequest policy.

## Earned

This earns structural trace safety: future PostToolUse live interpretation must
have a non-ambiguous tool-event join before it can claim a next action after
context.

## Not Earned

No live Codex run occurred. This earns no behavior lift, broad Cortex lift,
exactness value lift, clean-control safety claim in live use, Codex App parity,
shipping promotion, shared tool-evidence classification, typed intervention
pressure, centralized output law, host-runtime extraction, PreToolUse proof, or
Sinkhorn/transport proof.

## Next Train

Queue `codex-app-cli-posttooluse-shared-tool-evidence-classification`.

The phase-aware narrow live rerun remains blocked until the second live-readout
blocker is fixed: the SRE task-standard evidence path and Codex PostToolUse
actuator must consume one shared typed tool-evidence classifier.
