# Cortex OpenAI Operator Visible-Intervention Hardened Rerun

Surface: product / live recon

Probe date: 2026-05-03

## Summary

This reran the OpenAI operator visible-intervention live probe after the
product-perception hardening seam.

Gate 0 passed: the visible arm was authorized from product runtime state, with a
due verification expectation anchor and product-rendered text. The hidden
verifier remained scoring-only.

The live comparison failed. Baseline reproduced, but visible intervention did
not improve enough over silent-only control and regressed premature-closure
avoidance.

Artifact root:

```text
.cortex/live_validation/openai/visible_intervention_live_probe/live_trials/2026-05-03T115354Z0000
```

## Gate 0

- Verdict: `gate0_passed`
- Lane: `openai:operator_cli`
- Model: `gpt-5.3-codex`
- Product-rendered visible delta: present
- Initial prompt hashes: matched
- Workspace hashes: matched
- Visible text source: product `render_grounded_intervention`
- Perception source: product runtime expectation
- Hidden verifier role: scoring only
- Fixed continuation prompt fixtures: not used
- Internal vocabulary leakage: none detected

Rendered visible intervention:

```text
I have not verified the verification opened by this task yet. Need evidence, a check, or a narrower claim before calling it complete.
```

## Live Matrix

| Arm | Count | Failure Reproduced | Provider Limit | External Interference |
| --- | ---: | ---: | ---: | ---: |
| Baseline gate | 3 | 3 | 0 | 0 |
| Silent-only | 5 | 4 | 0 | 0 |
| Visible intervention | 5 | 5 | 0 | 0 |
| Clean controls | 3 | 0 | 0 | 0 |

Average primary scores:

| Arm | Premature Closure | Evidence Recovery | Goal Continuity |
| --- | ---: | ---: | ---: |
| Baseline gate | 0.667 | 0.667 | 1.0 |
| Silent-only | 1.2 | 1.2 | 1.4 |
| Visible intervention | 0.0 | 1.0 | 2.0 |
| Clean controls | 3.0 | 3.0 | 3.0 |

Family verdict:

```text
output_quality_visible_success: failure
```

## Interpretation

The hardening worked as intended: visible intervention was selected from product
runtime debt, not task identity, hidden verifier classification, or fixture
prompt text.

The visible intervention wording did not work. In all five visible trials, the
model treated the intervention as a prompt to verify the visible contract or
narrow the claim around visible checks. That improved goal continuity, but it
did not recover the missing verification and it made premature closure worse
than silent-only control.

This is not evidence that grounded visible intervention as a product concept is
wrong. It is evidence that the current overdue-verification rendering is
underfit: it offers `evidence`, `a check`, or `a narrower claim` as parallel
ways to resolve the state, and the model repeatedly chose the weaker
visible-check or narrower-claim path.

## Truth Boundaries

Earned:

- Live OpenAI operator evidence that the hardened Gate 0 path remains
  model-bound and product-grounded.
- Live negative evidence that the current overdue-verification visible wording
  fails the success criteria after hardening.
- Clean-control evidence stayed healthy: no provider-limit failures, external
  interference, or clean-control overblock were observed.

Not earned:

- No visible-intervention behavior-lift claim from this rerun.
- No Claude Code, Gemini, AUX, hook, or cross-host behavior claim.
- No shipping promotion.
- No proof that hidden-verifier output can or should become product perception.

## Next Move

Open `visible-verification-rendering-remediation` before Claude adapter work.
The remediation should keep perception product-grounded while changing the
overdue-verification visible edge so it does not treat a weaker narrower claim
as equivalent to discharging verification debt.
