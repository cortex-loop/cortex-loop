# Codex App/CLI PostToolUse Task-Standard Phase-Aware Calibration Gate 0

Surface: product host actuator + lab proof

Date: 2026-05-07

## Verdict

Verdict: `pass_posttooluse_phase_aware_gate0`.

The no-live phase-aware calibration passed. PostToolUse task-standard context
now stays silent on missing/pre-artifact diagnostics and still emits one
Codex-native PostToolUse `additionalContext` after a successful candidate
artifact creation leaves required closure evidence unresolved.

## Evidence Basis

Structural report:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_phase_aware_gate0/gate0_report.json`

Observed Gate 0 results:

- pre-artifact check stayed silent with private reason
  `pre_artifact_candidate_missing`
- successful candidate artifact creation for `exact_result.txt` emitted one
  PostToolUse context
- the emitted context targeted unresolved closure evidence, including the
  named direct checks for `wc -l exact_result.txt` and
  `cat -A exact_result.txt`
- clean evidenced work stayed silent
- blocker, waiting-on-user, unrelated, generic output, and markerless
  literal-only controls stayed silent
- no Stop block, PreToolUse denial, PermissionRequest path, runtime snapshot,
  root-hook mutation, hidden-scoring perception, or Sinkhorn/transport path
  appeared
- no live Codex run was executed

The model-I/O path remains the Codex-native
`PostToolUse` `hookSpecificOutput.additionalContext` surface. The existing
PostToolUse context template, item selection, per-session cap, deduplication,
and JSON response shape were preserved.

## Calibration

The failed live run showed that context could be spent after a missing-file
readback, before the model had created the artifact the direct check needed.
This seam narrows the firing phase:

- failed missing-artifact diagnostics are treated as precondition work and do
  not receive PostToolUse context
- candidate artifact creation must be successful and must reference a
  path-like anchor captured from the visible task or model-derived standard
- literal-only generic output is not enough to establish the candidate phase
- after the candidate phase exists, unresolved required `WORK_STANDARD` or
  `CLOSURE_EVIDENCE` items may receive the existing PostToolUse context

The harness decision window now treats artifact creation before context as
prerequisite work. Closure after context before the named direct check still
fails.

## Not Earned

- no live behavior lift
- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no Codex App parity or shipping promotion
- no exactness value lift
- no proof that PostToolUse will change the next live model action
- no signed UserPromptSubmit text edit
- no PostToolUse text edit
- no Stop text edit
- no SRE law, scored matcher, threshold, fixture, scoring, root-hook,
  hidden-verifier, Sinkhorn/transport, PreToolUse denial, or PermissionRequest
  policy change

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-run`.

The next live seam remains approval-gated, must not use `--require-pass`, and
may only test the narrow task-standard exactness / evidence-recovery actuator
effect: after candidate artifact creation, does the delivered PostToolUse
context lead the model to perform the named direct check before closure while
clean controls stay silent.
