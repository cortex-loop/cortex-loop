# CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0

Date: 2026-03-20
Status: mediation comparative evidence taxonomy (`active`)

## Scope

This taxonomy defines stable tags for mediation evidence collection and comparative review.
It is evidence-facing only. It does not authorize mediation, change packet meaning, or replace contradiction-preserving artifacts.

## Severity Guide

- `high`: invalidates the pair or blocks honest interpretation.
- `medium`: comparison remains inspectable but confidence is materially downgraded.
- `low`: minor noise; pair remains usable with explicit note.

## Tags

### `scenario_mismatch`

- meaning: baseline and mediated runs were not actually the same scenario.
- triggering evidence: different starting request/event, different declared scenario goal, different scenario family, or different task-value rubric.
- pair effect: invalidates the pair.
- usual severity: `high`

### `host_mismatch`

- meaning: host family or host-affordance conditions changed between the compared runs.
- triggering evidence: different host family, different host-native opportunity set, or different host surface than the paired run.
- pair effect: invalidates the pair.
- usual severity: `high`

### `boundary_drift`

- meaning: the commitment-truth boundary or certification conditions changed, so the comparison no longer measures only the executive difference.
- triggering evidence: changed commitment boundary inputs, changed approval/environment constraints, changed certification surface, or changed contradiction/degradation handling.
- pair effect: invalidates the pair.
- usual severity: `high`

### `burden_regression`

- meaning: visible burden increased without compensating value lift.
- triggering evidence: higher interruption count, higher AUX burden, or higher user-visible burden at the same task-value outcome class.
- pair effect: does not automatically invalidate the pair, but strongly downgrades confidence in a positive mediation claim.
- usual severity: `medium`

### `branch_churn`

- meaning: mediation introduced extra reopen, resume, orphaned, or proliferated branch behavior.
- triggering evidence: more branch oscillation, more stale branches, more orphaned branches, or more unnecessary branch growth than baseline.
- pair effect: does not automatically invalidate the pair, but counts as negative or mixed evidence on the branch-discipline axis.
- usual severity: `medium`

### `uncertainty_churn`

- meaning: mediation increased uncertainty loops, delayed lawful brake/escalation, or created contradiction-smoothing risk.
- triggering evidence: repeated uncertainty churn, delayed brake behavior, repeated uncertified/blocked surprises, or loss of explicit contradiction/degradation reporting.
- pair effect: does not automatically invalidate the pair, but may invalidate any claim of better uncertainty handling.
- usual severity: `medium`

### `host_flattening`

- meaning: mediation hid host-native differences instead of improving host-specialized realization.
- triggering evidence: pooled behavior that erases host-specific affordances, generic fallback replacing host-native opportunity use, or cross-host averaging that conceals a regression.
- pair effect: does not automatically invalidate the pair, but invalidates any host-specialized improvement claim.
- usual severity: `medium`

### `artifact_gap`

- meaning: the evidence package is incomplete for honest comparison.
- triggering evidence: missing run packet fields, missing event-trace refs, missing contradiction/degradation refs, missing burden refs where burden is claimed, or missing paired-run linkage.
- pair effect: may invalidate the pair if the missing artifact is load-bearing; otherwise downgrade confidence explicitly.
- usual severity: `high` when load-bearing, otherwise `medium`

### `env_friction`

- meaning: tooling, environment, or setup noise polluted the run enough that the comparison is no longer clean.
- triggering evidence: command failure, missing dependency, host/tooling mismatch, workspace setup drift, or other non-scenario execution noise.
- pair effect: may invalidate the pair if it changes the run outcome materially; otherwise downgrade confidence explicitly.
- usual severity: `medium`

### `none`

- meaning: no material failure category was observed for this run or pair.
- triggering evidence: the run is clean on the mediation-evidence dimensions tracked by this taxonomy.
- pair effect: pair remains usable without taxonomy-based downgrade.
- usual severity: `low`

## Use Rules

- Apply the narrowest tag that explains the evidence problem.
- A run or pair may carry multiple tags if more than one material issue occurred.
- Do not replace contradiction refs, degradation refs, or burden artifacts with taxonomy tags; the tags summarize failure mode, not truth content.
- If a `high`-severity tag invalidates the pair, record the pair as unusable instead of laundering it into a mixed or positive result.
