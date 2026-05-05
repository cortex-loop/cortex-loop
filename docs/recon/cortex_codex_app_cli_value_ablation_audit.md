# Cortex Codex App/CLI Value Ablation Audit

Surface: product / lab proof

Probe date: 2026-05-05

Verdict: requirement_level_perception_needed.

## Summary

This audit took the decision turn after the refreshed Astro three-arm run. It
did not change Cortex thresholds, paydown policy, speech, hooks, fixtures, or
shipping truth. It replayed existing live artifacts to ask whether the latest
failure came from threshold settings, broad verification paydown, weak Stop
text, missing claim/evidence perception, or a narrower Cortex value boundary.

The result is not a threshold problem. In all five `hook_native_cortex` Astro
trials, the final Stop had pressure `0.0`, no active expectations, one resolved
verification expectation, and silence reason `pressure_below_visible_threshold`.
Lowering the visible threshold as far as `0.0` would not have fired because the
ledger already considered verification paid down.

The result is a perception/paydown problem. Strictly disabling broad
generic-check paydown would have kept all three hidden-failing Astro trials open,
but it would also have blocked the two hidden-passing full-Cortex trials. That
means simple paydown tightening is too blunt. The next useful substrate is
requirement-level claim/evidence perception: Cortex must distinguish a check
that merely looks like verification from a check that addresses the work being
claimed.

## Run

Command:

```bash
python3 lab/codex_app_cli_cortex_value_ablation_audit.py --require-pass
```

Audit artifact:

```text
.cortex/live_validation/openai/codex_app_cli_cortex_value_ablation_audit/summary.json
```

Inputs:

```text
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260505T033207Z
.cortex/live_validation/openai/codex_app_cli_stop_continuation_resolution_loop
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/live_trials_20260504T203012Z
.cortex/live_validation/openai/visible_intervention_live_probe/live_trials/2026-05-03T115354Z0000
```

## Findings

### Threshold Replay

Verdict: `threshold_not_causal`.

```text
thresholds tested: 0.55, 0.35, 0.15, 0.0
hidden-failing hook_native_cortex trials: 3
final pressure on every hook_native_cortex trial: 0.0
active expectations on every final Stop: 0
resolved expectations on every final Stop: 1
```

Lowering the threshold cannot fire a visible gate once product state says the
expectation is already resolved.

### Paydown Ablation

Verdict: `paydown_tightening_risky_claim_alignment_needed`.

```text
caught_hidden_failures: 3
overblock_risk_count: 2
```

The broad generic-check paydown is too permissive for hidden output-quality
failures, but simply disabling it would overblock passing traces. This points
away from threshold tuning and toward evidence relevance.

### Claim/Evidence Alignment

Verdict: `visible_claim_evidence_gap_detected`.

The diagnostic used visible task obligations and product hook traces only. It
did not read hidden verifier scripts or hidden verifier output. It found that
Astro final claims about tag pages, search, and navigation often lacked
claim-aligned check evidence in the product-visible hook trace.

This is a first diagnostic, not a shipping classifier. Its importance is that
the next substrate can be product-visible: compare the model's closure claims
and observed checks against visible task obligations before treating generic
verification-shaped activity as full paydown.

### Family Separation

- Truth-gap false completion: latest baseline did not reproduce, so no paired
  hook-native lift evidence was earned.
- Missing verification: the Stop continuation-resolution loop showed mechanism
  closure from product-visible evidence, but no paired behavior lift.
- Hidden output quality: Astro produced mixed signal and zero Cortex blocks.
- Preservation risk and capability boundary: not tested by the latest live
  output-quality matrix.

### Forced Intervention Probe

The research-only forced-intervention live mode was not run. It remains gated
behind `CORTEX_CODEX_APP_CLI_VALUE_ABLATION_AUDIT_APPROVED=approved`. This
audit intentionally did not bypass product perception.

## Decision

Queue requirement-level claim/evidence perception before fixture remediation.

Precommitted branches resolved as follows:

- Threshold tuning: stop. Threshold replay showed pressure was zero after
  paydown.
- Paydown tightening: not alone. Strict paydown would catch hidden failures but
  also overblock passing traces.
- Text tuning: not next. Astro emitted zero model-visible text.
- Fixture remediation: not next. The fixture is now hidden enough to expose the
  real perception/paydown issue.
- Product direction: build a product-visible obligation and claim/evidence
  alignment seam, then retest behavior.

## Not Earned

- No broad behavior-lift claim.
- No hidden-quality lift claim.
- No forced-intervention behavior result.
- No shipping promotion.
- No claim that hidden verifier facts can become Cortex perception.
