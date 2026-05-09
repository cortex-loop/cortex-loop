# Cortex PostToolUse Proof-Surface Role-Demotion

Surface: no-live archive / role-demotion

## Summary

Verdict: `decision_role_demote_posttooluse_specific_proof_train`.

This seam implements the contraction decision from
`docs/recon/cortex_active_policy_contraction_decision.md`. The v2 evaluator
artifact `run_20260509T112542Z` produced `failure_no_value`: `60 live rows`
ran across `no_cortex_baseline`, `simple_hook_baseline`,
`cortex_silent_perception`, and `cortex_active_policy`; all arms tied on every
v2 family; active Cortex had `family_wins=0`; and no dominance boundary failed.

The PostToolUse paired-value artifact
`task_standard_posttooluse_paired_value_live_20260508T120907Z` already produced
`failure_no_value`: active PostToolUse context beat silent in `0/5` exactness
mismatch pairs. The earlier narrow PostToolUse live artifacts remain preserved
as historical evidence:

- `task_standard_posttooluse_live_20260507T100836Z`
- `task_standard_posttooluse_live_20260507T142129Z`
- `task_standard_posttooluse_live_20260507T153242Z`
- `task_standard_posttooluse_live_20260507T213732Z`
- `task_standard_posttooluse_live_20260507T225019Z`

Role-demotion means the old PostToolUse-specific proof train remains available
for historical replay, failure analysis, and regression reference, but it is
no longer roadmap authority, current value strategy, product progress, or a
reason to run another PostToolUse-specific live probe. The general four-arm
evaluator now owns value comparison.

## Role-Demotion Table

| Surface | Current owner | Evidence preserved by the general evaluator | Historical recon / artifact retained | New role | Forbidden action | Future removal proof |
| --- | --- | --- | --- | --- | --- | --- |
| PostToolUse-specific Gate 0 modes | `lab/codex_app_cli_hook_native_behavior_comparison.py` | The general evaluator preserves the paired PostToolUse `failure_no_value` through `historical_posttooluse_failure_no_value_rows(...)`. | Phase-aware, firing-boundary, overcontrol, actuator-trace, shared-tool-evidence, context-loop, measurement-stack, final-closure, and paired-value Gate 0 recons stay as historical proof. | Non-current support/history. | Do not treat Gate 0 pass results as current product value or queue live reruns from them. | Prove every referenced failure class is represented by the general evaluator replay or a stronger archive index before deleting modes. |
| PostToolUse narrow live / rerun modes | `lab/codex_app_cli_hook_native_behavior_comparison.py` | The general evaluator supersedes hook-local next-action readouts for value comparison. | The five live artifacts listed above remain historical failure evidence. | Non-current live-history support. | Do not run these modes as the next strategy, and do not reinterpret old negatives as lift. | Preserve artifact id, verdict, failing conjunct, and boundary status in a replayable table before removing CLI modes. |
| PostToolUse paired-value live mode | `lab/codex_app_cli_hook_native_behavior_comparison.py` | `lab/cortex_effectiveness_evaluator.py::historical_posttooluse_failure_no_value_rows(...)` mirrors the silent control into the simple-hook arm and preserves `failure_no_value`. | `task_standard_posttooluse_paired_value_live_20260508T120907Z` remains the paired exactness negative artifact. | Historical value-negative replay source. | Do not rerun the same exactness-only paired probe or count it as candidate-evolution permission. | Keep a passing test proving `registered_verdict == preserved_verdict == failure_no_value` before deleting the old live command. |
| PostToolUse repair recons and artifacts | `docs/recon/cortex_codex_app_cli_posttooluse_*.md`; `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/` | The general evaluator retains only the value-negative outcome; repair-chain details remain in recon history. | Repair recons preserve the phase, firing-boundary, overcontrol, trace, context-loop, and readout failure chain. | Historical evidence, not roadmap authority. | Do not remove or hide negative evidence; do not cite repair success as product progress. | Add an archive manifest or generated replay summary that names every artifact before moving docs out of active recon roles. |
| General evaluator historical replay ownership | `lab/cortex_effectiveness_evaluator.py` | Current owner for value comparison and historical PostToolUse no-value replay. | `docs/recon/cortex_executive_effectiveness_evaluator_build.md` records this transfer. | Current proof owner for value comparison. | Do not weaken the replay, omit the simple-hook challenger, or score silent success as Cortex value. | Replacement evaluator must preserve no-Cortex, simple-hook, silent, and active arms plus the historical PostToolUse no-value row. |
| Product PostToolUse actuator code | `cortex/hosts/openai/posttooluse_task_standard_actuator.py`; `cortex/hosts/openai/codex_app_cli_hook_coordinator.py` | None in this seam; product code is explicitly untouched. | Product actuator evidence remains historical and value-unearned. | Redesign-only product candidate. | Do not delete code, change runtime behavior, alter model-visible text, or reactivate PostToolUse as earned active policy. | Before renewed activation or removal, prove a non-task-specific evaluator case where a redesigned post-observation context beats the simple hook without overcontrol. |

## Decision

The PostToolUse-specific proof train is role-demoted to historical support.
Current value comparison belongs to the general four-arm evaluator. Product
PostToolUse runtime code remains untouched and value-unearned.

The next train is `cortex-retained-active-policy-spine-gate0`: a no-live proof
gate for the smaller retained spine identified by the contraction decision:
UserPromptSubmit task-standard formation, Stop closure/continuation,
`TaskStandardSpine`, and the shared SRE tool-evidence classifier.

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
- No Cortex value, behavior lift, exactness value lift, broad Cortex lift,
  Codex App parity, shipping promotion, product progress, or AlphaEvolve
  candidate-evolution permission.
