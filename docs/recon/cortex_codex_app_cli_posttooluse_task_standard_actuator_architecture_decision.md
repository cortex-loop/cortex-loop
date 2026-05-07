# Codex App/CLI PostToolUse Task-Standard Actuator Architecture Decision

Surface: product architecture decision

## Verdict

Verdict: `decision_queue_phase_aware_posttooluse_calibration_gate0`.

The `failure_context_ignored` live result is classified as a
PostToolUse timing/selection failure, not as host delivery failure,
task-standard state failure, clean-control overcontrol, or boundary breach.
The next seam should be a no-live phase-aware PostToolUse calibration Gate 0
before any further live run.

## Evidence Basis

Live source:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T100836Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T100836Z/trajectory.jsonl`

Classification:

- host delivery: passed; Codex received PostToolUse
  `hookSpecificOutput.additionalContext`
- task-standard capture: passed in the mismatch case; three standard items
  were captured
- clean/control overcontrol: passed; clean/blocker/waiting/unrelated controls
  received zero PostToolUse contexts
- hidden/root/runtime boundaries: passed; hidden scoring stayed absent /
  scoring-only, no runtime snapshot loaded, and root config was unchanged
- immediate next-action effect: failed; the next model tool did not perform
  the named direct check before closure
- likely cause: PostToolUse context fired after a failed precondition /
  missing artifact check (`wc -l exact_result.txt` before the file existed),
  so the next legitimate action was artifact creation rather than direct
  verification

The later exactness checks came through the existing Stop continuation loop,
which remains the only live-proven corrective actuator for this exactness
shape.

## Decision

Queue `codex-app-cli-posttooluse-task-standard-phase-aware-calibration-gate0`.

That seam should prove structurally that PostToolUse context is reserved until
a product-visible artifact or candidate output exists and a required
`WORK_STANDARD` / `CLOSURE_EVIDENCE` item remains unresolved. It should also
calibrate the harness decision window so artifact creation can count as a
prerequisite step, while closure before the named direct check still fails.

## Not Earned

- no broad Cortex behavior lift
- no exactness-only value lift
- no PostToolUse next-action effect claim
- no output-quality or truth-gap lift
- no Codex App parity or shipping promotion
- no authorization to tune signed task-standard text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, hook wiring,
  root config, hidden-verifier boundaries, Sinkhorn/transport, PreToolUse
  denial, or PermissionRequest policy

## Next Move

Implement the no-live phase-aware calibration Gate 0. Do not rerun live, run a
three-arm behavior comparison, or tune text/policy before that structural
calibration passes.
