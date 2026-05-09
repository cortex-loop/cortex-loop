# Cortex Retained Active-Policy Spine Gate 0

Surface: no-live retained-spine proof gate

## Summary

Verdict: `pass_cortex_retained_active_policy_spine_gate0`.

This seam defines the smallest retained active-policy spine after
`docs/recon/cortex_active_policy_contraction_decision.md` and
`docs/recon/cortex_posttooluse_proof_surface_role_demotion.md`.

The retained spine is `userpromptsubmit_stop_taskstandard_spine`:
UserPromptSubmit task-standard formation, Stop closure/continuation,
`TaskStandardSpine` state law, and shared SRE tool-evidence classification.
The seam wrote the no-live artifact set:
`retained_spine_contract.json`, `gate0_report.json`, and `summary.json` under
`.cortex/live_validation/cortex_retained_active_policy_spine_gate0/`.

This is not value evidence. It is a retained-spine ownership and proof gate.
The v2 live matrix artifact `run_20260509T112542Z` remains `failure_no_value`:
`60 live rows`, all arms tied, active `family_wins=0`, and no dominance
boundary failure. The PostToolUse paired-value artifact
`task_standard_posttooluse_paired_value_live_20260508T120907Z` remains
`failure_no_value`: active PostToolUse beat silent in `0/5` exactness mismatch
pairs.

## Retained Spine Table

| Component | Owner modules | Retained role | Product model-I/O path | Existing proof surfaces | Value status | Simple-hook parity rule |
| --- | --- | --- | --- | --- | --- | --- |
| `UserPromptSubmit task-standard formation` | `cortex/hosts/openai/codex_app_cli_hook_coordinator.py`; `cortex/hosts/openai/codex_app_cli_hook_client.py` | Prospective task-set formation | Codex `UserPromptSubmit` `hookSpecificOutput.additionalContext` | `docs/recon/cortex_codex_app_cli_task_standard_live_capture_rerun.md`; `docs/recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md`; product hook tests | `retained_but_value_unearned` | No Cortex value unless retained active policy beats `simple_hook_baseline` and `no_cortex_baseline`. |
| `Stop closure/continuation gate` | `cortex/hosts/openai/codex_app_cli_hook_coordinator.py`; `cortex/hosts/openai/codex_app_cli_hook_client.py` | Late truthful-closure and continuation gate | Codex `Stop` `hookSpecificOutput` or block stdout continuation | `docs/recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md`; task-standard behavior comparison evidence; product hook tests | `retained_but_value_unearned` | Stop may remain safety law, but simple-hook parity blocks value and candidate evolution. |
| `TaskStandardSpine` state law | `cortex/sre/task_standard.py` | Shared task-local standard and closure state law | No direct model-I/O; reaches the model only through UserPromptSubmit or Stop host decisions | `docs/recon/cortex_codex_app_cli_task_standard_spine.md`; `docs/recon/cortex_task_standard_sre_correspondence_reconciliation.md`; SRE/product tests | `retained_state_law_not_active_value` | State-only or silent success is no-value or measurement contamination. |
| `SRE tool-evidence classifier` | `cortex/sre/tool_evidence.py` | Shared tool-evidence observation and phase law | No direct model-I/O; reaches the model only through host policy decisions | `docs/recon/cortex_codex_app_cli_posttooluse_shared_tool_evidence_classification.md`; SRE/tool-evidence/product tests | `retained_support_law_not_active_value` | Classifier consistency is proof hygiene, not Cortex value by itself. |

## Explicitly Excluded

PostToolUse task-standard context remains
`role_demoted_non_current_support_history`. It is not reactivated as current
strategy, current value proof, product progress, or an earned active policy in
this seam. Its product code is untouched. Future re-entry requires a redesigned
non-task-specific evaluator case where post-observation context beats the
simple hook without overcontrol.

## Decision

The retained spine is small enough to test once, but not yet worth evolving.
The next train is `cortex-retained-active-policy-spine-live-gate1`: a no-live
dry-run evaluator gate for this retained spine against `no_cortex_baseline`,
`simple_hook_baseline`, and `cortex_silent_perception`.

If that later retained-spine live run ties or loses to the simple hook, active
policy growth stops and Cortex should contract or rebuild rather than start
AlphaEvolve-style candidate generation around zero signal.

## Forbidden Moves

- No live Codex run.
- No product code deletion.
- No product host behavior change.
- No model-visible Cortex text change.
- No evaluator scoring or fixture change.
- No hidden-verifier boundary change.
- No root hook change.
- No SRE law change.
- No active policy or candidate-policy mutation.
- No PostToolUse task-standard context reactivation as earned active policy.
- No Cortex value, behavior lift, exactness value lift, broad Cortex lift,
  Codex App parity, shipping promotion, product progress, or AlphaEvolve
  candidate-evolution permission.
