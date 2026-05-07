# Cortex Codex App/CLI PostToolUse Shared Tool-Evidence Classification

Surface: product host actuator plus SRE substrate proof

Verdict: `pass_posttooluse_shared_tool_evidence_gate0`.

Evidence basis:

- Shared classifier owner: `cortex/sre/tool_evidence.py`.
- SRE evidence consumer: `cortex/sre/task_standard.py`.
- Codex host actuator consumer:
  `cortex/hosts/openai/posttooluse_task_standard_actuator.py`.
- Lab proof owner: `lab/codex_app_cli_hook_native_behavior_comparison.py`.
- Gate 0 report:
  `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_shared_tool_evidence_gate0/gate0_report.json`.

## Decision

The PostToolUse task-standard live rerun is no longer blocked on duplicated
tool-evidence predicates. The SRE task-standard evidence path and the Codex
PostToolUse task-standard actuator now consume one SRE-owned typed classifier:
`ToolEvidenceObservation` and `ToolEvidencePhase`.

The shared classifier owns missing-artifact detection, line-shaped failed-check
diagnostics, failed-tool detection, markerless/generic output, successful
candidate artifact creation from caller-supplied path anchors, readback
completion, and response-presence completion.

## Gate 0 Result

`--task-standard-posttooluse-shared-tool-evidence-gate0 --require-pass` passed.

Pinned outcomes:

- pre-artifact missing checks classify as `pre_artifact_missing` and stay
  silent with private `pre_artifact_candidate_missing`;
- line-shaped `illegal option`, `invalid option`, and `usage:` diagnostics
  classify as failed checks and stay silent with private `phase_check_failed`;
- candidate artifact creation for captured path anchors remains context
  eligible;
- readback-shaped tool output remains context eligible;
- markerless generic output stays silent;
- SRE task-standard generic-check evidence remains `generic_check`;
- SRE task-standard aligned readback remains `standard_aligned`;
- status-only completion remains a generic SRE verification marker but is not a
  Codex host phase marker for PostToolUse context;
- prior overcontrol, firing-boundary, phase-aware, and causal-trace Gate 0
  outcomes remain passing;
- no Stop, PreToolUse, PermissionRequest, runtime snapshot, root hook mutation,
  hidden scoring perception, or transport path appeared.

## Unchanged

This seam did not change signed UserPromptSubmit text, PostToolUse text, Stop
text, SRE law, scored matcher thresholds, fixtures, scoring semantics, root
hooks, hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial,
PermissionRequest policy, output-law centralization, typed intervention
pressure, or host-runtime extraction.

## Earned

This earns structural predicate ownership: the Codex PostToolUse actuator and
host-agnostic SRE task-standard evidence path now use one typed tool-evidence
classifier for the exactness/evidence-recovery live rerun boundary.

## Not Earned

No live Codex run occurred. This earns no behavior lift, broad Cortex lift,
exactness value lift, output-quality lift, truth-gap lift, clean-control safety
claim in live use, Codex App parity, shipping promotion, centralized output
law, typed intervention pressure, host-runtime extraction, PreToolUse proof, or
Sinkhorn/transport proof.

## Next Train

Queue `codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun`.

The live rerun remains approval-gated, must not use `--require-pass`, and may
only earn narrow PostToolUse actuator evidence on `task_standard_exactness` /
evidence recovery.
