# Cortex OpenAI Operator Verification-Debt Continuation

Surface: product / live recon

Probe date: 2026-05-02

Branch: `codex/20260502-215144-silent-control-verification-debt-continuation`

## Verdict

The OpenAI Codex App/CLI wrapper-resume host adapter now has a general
verification-debt continuation action, and the paired live OpenAI Codex App/CLI
wrapper-resume matrix showed narrow behavior lift on the output-quality
visible-success family. The action is not keyed to Astro, docs search, web
design, or any hidden verifier answer. It is keyed to already-computed
route/policy/debt payloads plus a structured result state: visible work appears
successful, but verification remains unpaid.

Gate 0 passes structurally. Neutral and shaped conditions keep the same initial
prompt hash. The same initial prompt hash is load-bearing evidence that shaped
debt can enact a model-bound `resume_verification`
continuation in the same Codex CLI thread. The resumed prompt is the generic
`verification_debt_continuation_operator.md` prompt and contains no Cortex,
debt, brake, AUX, route, fixture, or hidden-answer vocabulary.

The live matrix then ran on `openai.codex_app_cli` with `gpt-5.3-codex`.
Baseline failure reproduced, shaped trials improved all three primary axes, and
matched controls did not show provider-limit or external-interference failures.
This earns narrow live behavior-lift evidence for silent verification
continuation on this lane. It does not promote shipping truth or generalize to
Claude, Gemini, AUX, or visible intervention records.

## What Changed

- `cortex/hosts/openai/operator_enactment.py` now includes
  `resume_verification` beside `invoke`, `block`, and `resume_recheck`.
- The new action is armed by the same general verification-relief budget used by
  silent debt control, not by task identity.
- The new action is allowed only when the first result is structurally classified
  as `visible_success_unverified`, provider-limit interference is absent, and a
  Codex thread id exists.
- Clean verified results do not resume verification.
- Initial prompts remain unchanged; only the host-adapter continuation decision
  changes after Gate 0.

## Gate 0 Evidence

The deterministic Gate 0 command:

```bash
python3 lab/live_openai_silent_control_probe.py --require-pass
```

The report was written to:

```text
.cortex/live_validation/openai/silent_control_live_probe/gate0_report.json
```

Gate 0 showed three model-bound enactment scenarios:

| Scenario | Neutral action | Shaped action | Meaning |
| --- | --- | --- | --- |
| `truth_gap_inspect_after_unpaid_verification` | `invoke` | `resume_recheck` | Existing truth-gap recheck still works. |
| `visible_success_unverified_after_unpaid_verification` | `invoke` | `resume_verification` | Hard verification-debt shape now has a continuation action. |
| `non_astro_visible_success_unverified_control` | `invoke` | `resume_verification` | The action generalizes beyond the Astro witness. |

The clean verified control stayed `invoke` under shaped debt and did not resume
verification.

## Live Matrix Evidence

The paired live command:

```bash
python3 lab/live_openai_silent_control_probe.py --require-pass --live-trials
```

The run wrote persisted evidence under:

```text
.cortex/live_validation/openai/silent_control_live_probe/live_trials/2026-05-02T200248Z0000/
```

Key artifacts:

```text
.cortex/live_validation/openai/silent_control_live_probe/live_trials/2026-05-02T200248Z0000/summary.json
.cortex/live_validation/openai/silent_control_live_probe/live_trials/2026-05-02T200248Z0000/trajectory.jsonl
```

The baseline gate reproduced the hard failure in 3/3 trials. In the full paired
matrix, baseline failure reproduced 5/5 times.

| Arm | Count | Premature closure | Evidence recovery | Goal continuity | Failure reproduced |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 5 | 0.4 | 0.4 | 1.0 | 5 |
| Shaped | 5 | 2.2 | 2.2 | 2.2 | 2 |
| Clean controls | 4 | 2.25 | 2.5 | 2.75 | 1 |

The shaped arm improved all primary axes and regressed none. The live summary
recorded zero provider-limit failures and zero external-interference counts in
the baseline, shaped, and clean-control arms.

Clean controls included honest partial progress with a question, waiting or
blocker surfacing, clean verified work, and an unrelated non-Astro
visible-success control. The non-Astro control is important because it proves
the action is not a hidden Astro-specific product rule.

## Truth Accounting

Cortex truth: A general OpenAI host-adapter action now exists for the
visible-success / unpaid-verification-debt state, and it can be enacted before
the Codex CLI model-bound continuation.

Brain-wiring truth: The action preserves the executive distinction Cortex needs:
successful-looking work can still owe verification, and unresolved verification
can authorize another checking pass before closure.

Conformance truth: Product and lab tests prove the action is state-keyed,
prompt-initial-hash preserving, leak-free, and non-Astro-specific at Gate 0.

Live behavior truth: Narrowly earned for OpenAI Codex App/CLI wrapper-resume
silent verification continuation on the output-quality visible-success family.
It is not evidence for visible interventions, Claude Code Desktop, Gemini, AUX,
or broad task families.

Shipping truth: Unchanged. `openai.codex_app_cli` remains the shipping default
lane, but this recon does not promote broader shipping claims.

## Not Earned

- no broad behavior-lift claim beyond this OpenAI operator task family;
- no Claude Code Desktop, Gemini, AUX, visible intervention, or `tau` proof;
- no shipping promotion.

## Next

Proceed to grounded-intervention-record planning with this live evidence as
input. The next phase must keep the hard witness as a witness, not a product
rule: product behavior stays keyed to verification debt, structured result
state, and grounded task-local anchors.
