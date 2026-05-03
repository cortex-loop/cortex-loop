# Cortex Visible-Intervention Product-Perception Hardening

Surface: product / structural recon

## Summary

This seam tightened the grounded visible-intervention path so verification
speech depends on a due product-runtime expectation record, not only on a
synthetic resolution-deficit payload or lab-side outcome classification.

The hardening preserves the Seam 7 visible edge:

```text
product event stream -> expectation ledger -> resolution deficit -> grounded anchor -> intervention decision -> renderer/enactment
```

No new action vocabulary, prompt fixture, hidden verifier perception, task
identity trigger, or live behavior claim is added.

## What Changed

- `build_runtime_grounded_intervention` now receives the current
  `ExpectationLedger` and current step from OpenAI, Claude, Gemini, and
  reference runtime steps.
- Verification interventions require a due product-runtime expectation record.
  Resolution pressure without a matching due expectation stays silent with
  `missing_product_expectation_anchor`.
- `GroundedInterventionDecision.as_payload()` now includes a private
  `selection_trace` with perception source, selected expectation id, deficit
  kind, pressure tags, silence reason, and silent-control sufficiency.
- The OpenAI visible-intervention Gate 0 harness now builds the shaped state
  from a product event replay instead of a pre-seeded ledger projection.
- The live helper computes visible enactment before hidden verifier evaluation
  is read. Hidden verifier output remains scoring only.

## Structural Evidence

Focused checks:

```bash
python3 -m pytest tests/product/test_sre_grounded_interventions.py tests/conformance/test_runtime_grounded_interventions.py tests/lab/test_live_openai_visible_intervention_probe.py -q
python3 lab/live_openai_visible_intervention_probe.py --require-pass
```

What these prove:

- Product-visible runtime events can open unpaid verification debt and later
  produce a grounded visible intervention across reference, OpenAI, Claude,
  and Gemini runtime shells.
- The same runtime state across Astro and non-Astro task identities yields the
  same product-rendered visible intervention text.
- The same task identity with clean/no-debt or missing-prior-anchor state stays
  silent.
- The lab harness does not need hidden verifier output to decide whether Cortex
  may speak.

## Truth Boundaries

Earned:

- Structural product-perception hardening for grounded visible intervention.
- Gate 0 evidence that OpenAI visible intervention can be selected from product
  event replay and due expectation debt before scoring is read.
- Cross-runtime conformance evidence that the same expectation-ledger anchor
  shape exists for reference, OpenAI, Claude, and Gemini runtime steps.

Not earned:

- No new live behavior-lift claim.
- No Claude Code hook delivery or behavior evidence.
- No claim that Cortex detects every production verification gap.
- No claim that visible intervention should replace silent route/brake gates.

## Next Move

Proceed to `claude-code-adapter-from-runtime-law` with this hardening as a
precondition: Claude hook transport should consume runtime-law decisions and
product-rendered grounded text, not hook-local policy or fixture-shaped prompts.
