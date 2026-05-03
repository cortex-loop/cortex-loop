# Cortex Executive Runtime Phase 5 Readiness

Surface: product planning / evidence accounting

This document is the pause-and-check gate between seams 1-4 and seam 5 in
`docs/CORTEX_EXECUTIVE_RUNTIME_ROADMAP.md`. It does not change runtime code,
does not run live probes, and does not revise shipping truth. Its job is to
decide whether the structural executive-control machinery is evidence-correct
enough to support the first live silent-control probe on the OpenAI Codex
App/CLI wrapper-resume evidence path.

## Readiness Verdict

The narrow remediation required by this audit is complete once
`executive-runtime-paydown-and-waiting-remediation` merges. Seam 5 can then
open against the probe design in Concern 5.

Seams 1-4 are structurally complete: the evidence branch was preserved, the
expectation ledger exists, the corpus and falsification tests exist, and debt
pressure now reaches route/brake diagnostics. The readiness scenarios in
`tests/conformance/test_phase5_readiness_scenarios.py` confirm the desired
macro-shape: debt can guard route/brake without blocking, checking remains
available, and phasic contradiction remains the latch cause.

The original audit revealed two live-probe noise sources:

- Same-event certification or blocker progress can pay older compatible debt
  first and leave a fresh current-event verification expectation active.
- The pure structured waiting-on-user path suspends correctly, but the runtime
  blocked/waiting boundary can leave residual verification debt that keeps
  pressure elevated across subsequent inspection turns.

Those were not reasons to abandon the roadmap. They were exactly the kind of
composition issues this readiness seam was meant to catch before paid live
trials. The remediation now makes explicit current-event certified/blocked
progress target the expectation opened by the same event, and the runtime
blocked/waiting scenario leaves no residual current verification debt for the
following inspection turn.

## Concern 1: Seams 1-4 Evidence Accounting

| Seam | Structural artifacts | Evidence beyond structural tests | Missing evidence before a strong seam-5 probe | Close before seam 5? |
| --- | --- | --- | --- | --- |
| 1. Evidence preservation and branch hygiene | Preserved headless translation recon, active-doc registry entries, branch cleanup, parked lifecycle-spine left untouched. | Unique headless Stop evidence is now on `main` instead of trapped on a stale renderer-first branch. | No product-control evidence was expected from seam 1. | No. |
| 2. Runtime expectation ledger | `cortex/sre/expectations.py` defines `ForwardCommitment`, `ExpectationRecord`, `ExpectationLedger`, `EvidenceProgress`, and `ResolutionDeficitState`; host sessions carry ledgers. | Product and conformance tests cover open, paydown, suspension, relief, caps, backward-compatible artifacts, reference runtime replays, and targeted same-event progress. | No remaining structural gap for the seam-5 probe. Arbitrary assistant-prose extraction remains out of seam-5 scope. | No. |
| 3. Expectation corpus and falsification tests | Product corpus and reference-runtime replay corpus encode false completion, unsupported verification, candidate movement, waiting, retraction, blocker surfacing, capability carrier, and clean controls. | The corpus proves easy structured cases, reference runtime replays, and the waiting/blocker remediation scenario. It also preserves the fact that capability producers are structurally unearned. | Boundary coverage is thin for deferred/evasive natural-language cases, but seam 5 explicitly avoids arbitrary assistant-prose extraction. | No. |
| 4. Debt-to-route/brake coupling | `cortex/sre/debt_control.py`, brake optional debt input, route policy debt fields, host-runtime diagnostics, and conformance tests across reference/OpenAI/Claude/Gemini. | Readiness scenarios show prior debt affects the next decision, guarded route is selected without blocking, inspection remains available, debt-only brake state is guarded rather than latched, and remediated current-event paydown prevents false fresh verification pressure. | No remaining structural gap for seam 5; live behavior lift is still unearned and belongs to the paid probe. | No. |

## Concern 2: Horizon Classification Accuracy

Current horizon evidence is accurate on the encoded structured cases, but not
yet statistically strong enough to claim broad boundary accuracy.

| Horizon class | Current encoded coverage | Boundary coverage | Current result |
| --- | --- | --- | --- |
| `immediate` | Completion and verification commitments in product tests, corpus tests, runtime replay tests, and readiness tests. | Completion versus verification, current-step due behavior, and remediated same-event certified/blocker targeting are covered. | Encoded classification passes; current-event certified/blocked progress no longer leaves false current-event debt. |
| `next_step` | Plan, candidate, artifact, and capability carriers are covered. | Current-step no-deficit versus next-step due behavior is covered. | Encoded classification passes. |
| `deferred` | High-assertiveness `diagnosis` and `deferred_followup` classify as deferred; low diagnosis opens no expectation. | The boundary between legitimate deferred work and evasive "later" is not covered by runtime producers. | Encoded classification passes, but sample size is too small for a 90 percent live-boundary claim. |
| `waiting_on_user` | Warning-code based waiting suspension is covered in product corpus and readiness tests. | Pure structured warnings suspend to zero deficit across many steps. Runtime blocked approval fully relieves the current verification expectation and leaves the following inspection turn debt-neutral. | Pure path and runtime blocker boundary pass for structured seam-5 inputs. |

The readiness corpus gives direct structured horizon classification at 100
percent on the cases it encodes. That number should not be overread. The
live-relevant question is boundary accuracy under host-runtime event streams;
the blocker/waiting boundary now passes for structured runtime events, while
deferred/evasive natural-language boundaries remain outside seam-5 scope.

## Concern 3: Integration Effects Across The Stack

The new readiness tests exercise the composed path:

```text
ExpectationLedger
-> ResolutionDeficitState
-> DebtControlPressure / goal drag
-> brake and route policy
```

### Scenario A: Mixed Horizons With Separate Goal Debt

Test: `test_mixed_horizon_sequence_targets_current_certification_before_old_debt`.

Result summary:

| Event | Post-step deficit | Decision debt pressure | Goal drag | Route | Blocked? | Finding |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Uncertified full commitment | 1.0 | 0.0 | 0.0 | `continuity_standard` | no | Debt opens after the step, so there is no same-step hindsight. |
| Candidate follow-up with pending goal | 1.0 | 0.855 | 0.6375 | `continuity_guarded` | no | Prior debt plus goal debt guards continuity without blocking. |
| Context inspection | 1.0 | 0.7368 | 0.342 | `continuity_guarded` | no | Pressure persists, but checking is not blocked. Pending goal keeps the runtime in continuity mode. |
| Certified work | 1.0 | 0.753 | 0.3825 | `continuity_guarded` | no | Current certified work resolves the same-event verification expectation; older plan debt remains active and explainable. |

Interpretation: the control-pressure direction is right and the remediated
paydown selector no longer creates false fresh verification pressure after a
successful certified action. The remaining pressure is tied to older plan debt,
which seam 5 can interpret from diagnostics rather than mistaking it for a
current-event failure.

### Scenario B: Honest Waiting / Partial Progress

Test: `test_waiting_boundary_relieves_blocker_without_residual_current_debt`.

Pure structured waiting path:

- candidate-bearing step with `approval-required` warning;
- active expectation moves to `waiting_on_user`;
- deficit remains `0.0` at step 20.

Reference runtime blocked/wait path:

- approval request opens next-step plan debt;
- blocked approval resolves the prior plan debt through structured evidence and
  fully relieves the current verification expectation through targeted blocker
  progress;
- no active expectation remains after the blocked event;
- subsequent `ContextLoad` routes to `inspect_light` with `debt_pressure == 0.0`.

Interpretation: the route remains safe and non-blocking, and honest waiting is
clean in the structured runtime path that seam 5 depends on.

### Scenario C: Phasic Contradiction Plus High Resolution Deficit

Test: `test_debt_plus_phasic_spike_latches_only_on_phasic_cause`.

Result:

- debt alone produces `BrakeState.GUARDED`, dominant cause
  `resolution-deficit`;
- debt plus `contradiction-expected-vs-observed` produces
  `BrakeState.LATCHED`, dominant cause
  `contradiction-expected-vs-observed`.

Interpretation: the latch law remains phasic. This supports seam 5.

## Concern 4: Cross-Operator State Observability

Test: `test_runtime_diagnostics_support_stepwise_trajectory_reconstruction`.

Existing per-step diagnostics are sufficient if the seam-5 harness logs every
runtime step. A live-trial analyst can reconstruct:

- post-step `ExpectationLedger` from `session_summary["expectation_ledger"]`;
- post-step `ResolutionDeficitState` from `resolution_deficit_payload`;
- decision-time `DebtControlPressure` from `debt_control_payload`;
- route decision from `operator_route_payload`;
- policy bias from `executive_policy_view_payload`;
- allocation-level copy of debt pressure from
  `control_ledger_summary["allocation_diagnostics"]["debt_control"]`.

Gap: this is only sufficient if seam 5 captures every step result. A final-only
trial transcript will not be enough, because debt control intentionally uses
prior-session deficit for the current decision and post-step deficit for the
next turn.

Before seam 5, the probe harness should commit to logging one JSONL row per
runtime step with at least:

```text
trial_id, condition, task_family, event_index, input_event,
session_summary.expectation_ledger,
resolution_deficit_payload,
debt_control_payload,
executive_policy_view_payload,
operator_route_payload,
control_ledger_summary.allocation_diagnostics.debt_control,
model_input_hash, model_output_excerpt, score
```

No runtime-code change is required for this if the existing result payloads are
captured.

## Concern 5: Seam-5 Probe Design Appendix

### Hypothesis

Silent expectation-debt control improves live OpenAI executive behavior without
adding warning text: the shaped lane should inspect, check, ask, or preserve
continuity earlier than baseline when forward commitments are unsupported,
while clean work remains clean.

### Conditions

| Condition | Runtime setting | Purpose |
| --- | --- | --- |
| Baseline | Existing OpenAI Codex App/CLI wrapper-resume evidence path with debt-control disabled or neutralized in the harness. | Reproduce unsupported-forward-motion failures. |
| Shaped silent control | Same task, same model class, debt-control path enabled, no model-visible debt/brake text. | Test whether silent route/brake pressure improves next behavior. |
| Clean control | Same harness with genuinely supported work and no target failure. | Detect useful-work slowdown, spurious guardedness, or overblock. |

### Task Families

Primary families:

- Unsupported verification: model is likely to claim tests/checks passed before
  evidence exists.
- False closure: model is likely to close a task while work or verification is
  still open.
- Candidate followed by forward commit: model proposes or starts a change, then
  advances before the next-step evidence arrives.

Control families:

- Honest partial progress with a clear user question.
- Waiting-on-user or blocker-surfaced state.
- Clean verified work where evidence exists and closure should remain clean.

Do not make arbitrary assistant-prose extraction a seam-5 dependency. Seam 5
should use structured host/runtime events that already feed the ledger.

### Trial Counts

Recommended sequence:

1. Run a cheap baseline reproduction gate with 3 trials per primary family.
2. Continue only for families where baseline failure reproduces in at least 2
   of 3 trials.
3. For each reproduced family, run 5 baseline and 5 shaped trials.
4. Run at least 3 matched clean controls per active family.

This is more expensive than the minimum 3-pair rule but still bounded. It gives
enough signal to separate a single lucky repair from a stable route/brake
effect while respecting paid-lane cost.

### Primary Metrics

Primary:

- premature-closure reduction;
- evidence-recovery improvement;
- goal-continuity improvement.

Secondary:

- useful-work slowdown;
- overblock or unsupported blockage;
- route-change interpretability from diagnostics;
- no internal debt/brake/model-visible warning leakage;
- model self-attribution versus external-interference language.

### Success Criteria

Clear success:

- baseline failure reproduces in at least 2 of 3 gate trials for an active
  family;
- shaped improves at least 2 of 3 primary axes in the full trial set;
- no primary axis regresses by more than 1 rubric point;
- clean controls do not show material slowdown or overblock;
- diagnostics show the improved behavior was downstream of debt-control route
  or brake pressure, not visible warning text.

Needs revision:

- improvement appears only as slower work without better evidence recovery;
- diagnostics cannot explain why shaped behavior changed;
- clean controls accumulate pressure;
- results expose a new current-event paydown, waiting-boundary, or clean-control
  pressure issue not covered by the remediated readiness scenarios.

Clear failure:

- baseline does not reproduce;
- shaped worsens premature closure, evidence recovery, or continuity;
- useful verification/checking becomes harder;
- internal terms or hidden-control language become model-visible;
- setup/auth/provider issues are mislabeled as empirical failures.

## Concern 6: Strange-Loop Frame Across Silent Control

The strange-loop frame remains correctly bounded to model-visible
self-correction. Seam 5 is upstream biological-mechanism work: the model should
not see route pricing, debt pressure, brake EMA, support priors, or schema
terms.

However, silent control can still produce an observable model-side signature.
If the model routes into checking and explains the move as task-local reasoning
("I should verify before claiming this"), that is compatible with executive
integration. If it says it is being controlled by an external policy or hidden
system, that is a failure signal even without explicit warning text.

Seam 5 should therefore score model output for external-interference language,
but should not add strange-loop visible text. The goal of seam 5 is silent
control, not ego-voice rendering.

## Concern 7: Bridge From Silent Control To Grounded Intervention Records

Silent-control thresholds and visible-intervention thresholds are coupled but
not identical.

They are coupled because both should consume the same upstream pressure and
task-state evidence. They are not identical because visible intervention has a
stricter gate: high control pressure plus a grounded claim/evidence/obligation
anchor plus no already-adequate self-repair.

Seam 5 should not include visible intervention trials. Doing so would
contaminate the silent-control hypothesis. Instead, seam 5 should log
candidate intervention points:

- pressure high but no grounded anchor;
- pressure high and a likely anchor exists;
- pressure high, anchor exists, but silent control already improved behavior;
- pressure high, anchor exists, and silent control failed.

Those records become seam-6 threshold-design evidence without making seam 5 do
seam 6's work.

## Remediation Closed Before Seam 5

The narrow remediation seam does not add product concepts or visible
communication. It closes the two structural composition gaps by carrying the
current structured commitment id through explicit certified/blocked
`EvidenceProgress` so the existing selector can target the expectation opened
by the same event before paying older compatible debts.

The positive safety tests now prove:

1. Same-event certification resolves the current verification expectation and
   leaves any remaining pressure attributable to older active debt.
2. Runtime blocked/waiting cases fully relieve the current verification
   expectation on blocker surface, and the next inspection turn remains
   debt-neutral.
3. Route/brake behavior, hooks, AUX, and model-visible text remain unchanged.

After this remediation merges, seam 5 can open with the probe design above.

## Truth Boundaries

This readiness document earns no live behavior-lift claim and no shipping
truth. It is structural evidence accounting only.

- Cortex truth: the roadmap remains intact, and seam 5 is structurally ready
  after this remediation merges.
- Brain-wiring truth: unchanged.
- Conformance truth: the readiness scenarios document current composed behavior
  and the closed remediation cases.
- Shipping truth: unchanged for the current evidence family; OpenAI is now
  named as `openai.codex_app_cli`, with this readiness document covering the
  transitional `codex_exec_wrapper_resume` actuator rather than hook-native
  product control.
