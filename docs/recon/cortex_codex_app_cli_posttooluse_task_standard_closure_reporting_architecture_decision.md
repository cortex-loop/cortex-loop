# Codex App/CLI PostToolUse Task-Standard Closure-Reporting Architecture Decision

Surface: product architecture decision

Date: 2026-05-08

## Verdict

Verdict: `decision_queue_final_closure_readout_remediation_gate0`.

The latest live result `task_standard_posttooluse_live_20260507T225019Z`
should be classified as **lab final-closure readout underfit**, not host
delivery failure, PostToolUse context failure, clean-control overcontrol, or
true next-action context ignore.

The old live verdict remains `failure_context_ignored` under the preregistered
metric because `final_closure_reports_context_evidence=false`. This decision
does not retroactively promote that run to a pass.

## Evidence Basis

The mismatch row delivered the actuator and then performed the requested check:

- PostToolUse context count: 1
- `posttooluse_context_repeated`: `false`
- selected item: `task-standard:work_standard:e94ceefc9dbac7e2`
- trace join source: `tool_event_fingerprint`
- `posttooluse_context_trace_ambiguous`: `false`
- `next_tool_matches_context=true`
- next tool output included `cmp_exit=0`
- next tool output included expected hex
  `616c7068612062657461206f6d656761`
- `final_closure_reports_context_evidence=false`

The final output excerpt from the run included semantic closure evidence:

```text
Result:
- `PASS`
- `bytes=16`
- `hex=616c7068612062657461206f6d656761`

That proves the current `exact_result.txt` content is exactly `alpha beta omega` (no extra characters).
```

The current harness predicate `_final_reports_posttooluse_evidence(...)`
recognizes narrower text shapes such as `cat -A`, `one line`, and
`1 exact_result.txt`; it does not recognize this `PASS` / `bytes=16` / `hex=...`
closure form even though it is semantically direct evidence for the requested
exactness check.

Control and boundary evidence from the same run remained clean:

- `clean_evidenced`: 0 PostToolUse contexts
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts
- root config hash unchanged
- no runtime snapshot loaded
- hidden scoring stayed absent / scoring-only
- `behavior_lift_claim_allowed=false`

## Classification

- host delivery: passed
- PostToolUse context emission: passed
- repeated-context prevention: passed
- causal trace joining: passed
- next action after context: passed
- clean/control silence: passed
- hidden/root/runtime boundaries: passed
- final closure semantic evidence: likely present
- lab final-closure readout predicate: underfit

This narrows the failure to the proof/readout layer. It does not authorize
changing runtime policy, model-visible text, scoring, or task-standard law.

## What This Earns

- Architecture classification for the latest `failure_context_ignored` result.
- Evidence that the immediate next-action effect is no longer the primary
  blocker for this run.
- A queued no-live remediation target for the final-closure readout predicate.

## What This Does Not Earn

- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no exactness-only value lift
- no Codex App parity or shipping promotion
- no retroactive pass for `task_standard_posttooluse_live_20260507T225019Z`
- no permission to change signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, matcher thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial,
  PermissionRequest policy, output-law centralization, typed intervention
  pressure, or host-runtime extraction
- no permission to run another live probe or value probe before the readout
  remediation is replay-proven

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-final-closure-readout-remediation-gate0`.

That seam should be no-live. It may update lab readout/replay logic so
`PASS`, `bytes=16`, exact hex, and exact content closure can count as reporting
the context evidence, while preserving boundary-breach, overcontrol,
ambiguous-trace, and context-ignored failure classifications.
