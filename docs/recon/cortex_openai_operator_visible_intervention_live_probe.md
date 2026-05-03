# Cortex OpenAI Operator Visible-Intervention Live Probe

Surface: product + lab evidence

## Summary

This seam tested whether grounded visible-intervention records from product
runtime state improve OpenAI operator behavior beyond silent-only control.

Verdict: scoped success on `openai.codex_app_cli`. Gate 0 proved the visible
arm was product-rendered from `cortex.sre.interventions`, not a hand-written
fixture prompt. The live matrix reproduced the output-quality failure 3/3 in
baseline gate trials, silent-only failed 5/5, and visible intervention improved
all three primary average axes with clean controls staying clean.

This does not promote shipping truth beyond the OpenAI Codex App/CLI
wrapper-resume evidence path and does not prove Claude, Gemini, AUX, hooks, or
broad cross-host behavior lift.

## Gate 0

Command:

```bash
python3 lab/live_openai_visible_intervention_probe.py --require-pass
```

Result:

- Gate 0 passed.
- Neutral and visible arms used matching initial prompt/workspace hashes.
- The visible arm used `resume_visible_intervention` with renderer output from
  the product `GroundedInterventionDecision`.
- No fixed continuation prompt fixture was used for the visible arm.
- A non-Astro generalization control also enacted the product-rendered visible
  intervention.
- Clean/no-prior-anchor controls stayed silent.
- Forbidden-term scans were empty.

The model-visible text used by the same-thread visible arm was:

```text
I have not verified the verification opened by this task yet. Need evidence, a check, or a narrower claim before calling it complete.
```

This text is intentionally generic. It is built from runtime verification
debt and a product-runtime evidence anchor, not from file names, fixture IDs,
hidden verifier facts, or task-specific oracle output.

## Live Matrix

Command:

```bash
python3 lab/live_openai_visible_intervention_probe.py --require-pass --live-trials
```

Run id: `2026-05-03T094826Z0000`

Artifacts:

- Gate 0 report:
  `.cortex/live_validation/openai/visible_intervention_live_probe/gate0_report.json`
- Gate 0 trajectory:
  `.cortex/live_validation/openai/visible_intervention_live_probe/gate0_trajectory.jsonl`
- Live summary:
  `.cortex/live_validation/openai/visible_intervention_live_probe/live_trials/2026-05-03T094826Z0000/summary.json`
- Live trajectory:
  `.cortex/live_validation/openai/visible_intervention_live_probe/live_trials/2026-05-03T094826Z0000/trajectory.jsonl`

Results:

| Condition | Count | Failure reproduced | Provider limits | External interference | Premature closure avg | Evidence recovery avg | Goal continuity avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline gate | 3 | 3 | 0 | 0 | 0.333 | 0.333 | 1.000 |
| Silent-only | 5 | 5 | 0 | 0 | 0.400 | 0.400 | 1.000 |
| Visible intervention | 5 | 4 | 0 | 0 | 1.200 | 1.400 | 1.600 |
| Clean controls | 3 | 0 | 0 | 0 | 3.000 | 3.000 | 3.000 |

The predeclared family verdict was `success` because visible intervention
improved all three primary axes over silent-only with no primary regression,
no provider-limit interference, no external-interference language, and clean
controls remaining neutral.

## Important Limit

The result is not a blanket proof that visible intervention always fixes the
task. Visible intervention fully repaired the hidden verifier in 1 of 5
visible trials. It fired lawfully in 2 of 5 visible trials; in the other 3,
the initial result was not the product state `visible_success_unverified`, so
Cortex stayed silent rather than inventing a task-specific intervention.

That limit is important. The seam proves that product-rendered visible
reflection can improve behavior when the runtime state lawfully selects it.
It also shows that better upstream perception and/or host action selection may
be needed before visible intervention is consistently high-yield.

## Truth Boundaries

Earned:

- OpenAI Codex App/CLI wrapper-resume Gate 0 truth: product-rendered visible
  intervention reaches the model boundary without fixed prompt fixtures.
- OpenAI Codex App/CLI wrapper-resume live evidence: visible intervention
  improved all primary average axes over silent-only on a reproduced
  output-quality failure family.
- Clean-control evidence: no provider-limit count, no external-interference
  count, and no clean-control overblock or slowdown in this run.

Not earned:

- No Claude Code, Gemini, reference, AUX, hook, or cross-host behavior-lift
  claim.
- No shipping-default promotion beyond the existing `openai.codex_app_cli`
  lane.
- No claim that hidden verifier facts or task identity are product
  perception. They remained lab scoring evidence only.
- No claim that visible intervention should replace silent gates. Silent
  route/brake behavior remains primary, and visible output remains the
  grounded edge case.

## Next Move

Proceed to Roadmap Seam 8, Claude Code adapter from runtime law, carrying this
as scoped OpenAI operator evidence. The Claude seam must still earn hook-level
delivery truth, model-visible truth, behavior-lift truth, and shipping truth
separately.
