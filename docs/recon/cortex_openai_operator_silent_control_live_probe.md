# Cortex OpenAI Operator Silent-Control Live Probe

Surface: product / recon

Probe date: 2026-05-02

Branch: `codex/20260502-161134-silent-control-live-probe-on-openai`

## Verdict

Gate 0 failed, so live OpenAI operator trials were not run. The specific
finding is that runtime debt control changes OpenAI route/policy diagnostics,
but the current Codex operator live adapter does not enact those diagnostics
before the model call.

The upstream executive-runtime stack can compute a silent debt-control delta:
an unpaid verification expectation changes OpenAI runtime debt diagnostics,
policy view, route reason tags, and route margins. The current Codex operator
live adapter does not enact those diagnostics before invoking the model. The
`lab/openai_operator_cli.py::run_openai_operator_single_turn` signature accepts
workspace, prompt, scenario, stderr path, model, auth, and environment inputs;
it has no runtime-session, route, policy, or debt-control input. The older
`lab/live_operator_directionality.py::_run_openai_variant` route path also
does not pass `debt_control_pressure` into policy construction.

Therefore a baseline-vs-shaped live trial would not be testing shaped silent
control. It would be comparing two Codex operator invocations without a proven
model-bound difference. The correct next seam is a remediation seam that
connects OpenAI runtime debt-control outputs to Codex operator invocation or
continuation policy without adding model-visible warning text.

## Gate 0 Command And Artifacts

Command:

```bash
PYTHONPATH=. python3 lab/live_openai_silent_control_probe.py
```

Primary artifacts:

- `.cortex/live_validation/openai/silent_control_live_probe/gate0_report.json`
- `.cortex/live_validation/openai/silent_control_live_probe/gate0_trajectory.jsonl`

Harness test:

```bash
python3 -m pytest tests/lab/test_live_openai_silent_control_probe.py -q
```

The probe did not use OpenAI API/service spend and did not set
`CORTEX_LIVE_SERVICE_SPEND_APPROVED`. It used deterministic runtime replay and
source/signature inspection only.

## Gate 0 Findings

| Question | Finding | Evidence |
| --- | --- | --- |
| Does runtime debt control produce a structural delta? | Yes. `runtime_control_delta_present == true`. | The shaped runtime cases had nonzero `debt_pressure` and changed policy/route diagnostics relative to neutral cases. |
| Does the Codex operator adapter enact that delta before the model call? | No. `model_bound_debt_enactment_present == false`. | The inspected OpenAI operator CLI signature has no runtime-control input, `_run_codex_exec` passes only prompt/model/session command inputs, and the directionality harness does not pass debt control into policy construction. |
| Are live trials allowed? | No. `gate0_passed == false`. | The harness decision is `live_trials_allowed: false`; running paired trials would not test the silent-control hypothesis. |

## Runtime Delta Details

The deterministic replay included two Gate 0 cases.

`inspect_after_unpaid_verification` compared an OpenAI
`response.output_text.delta` event with an empty session against the same event
with an unpaid verification expectation. The shaped case produced
`debt_pressure: 0.6`, `resolution_pressure: 1.0`,
`verification_relief_bias: 1.0`, debt guard/default policy adjustments, and a
`debt-control:guard-bias` route reason tag. The route profile remained
`inspect_light`, which is correct: debt made verification relief more salient
without blocking inspection.

`forward_after_unpaid_verification` compared an OpenAI `response.completed`
event with and without prior unpaid verification debt. The shaped case produced
`debt_pressure: 0.736`, `goal_drag: 0.34`, and debt-control route reason tags.
Both neutral and shaped cases were already blocked by existing modulator stop
pressure in this synthetic forward case, so the useful evidence is not a new
live route effect; it is proof that debt-control diagnostics exist and remain
bounded.

## Why Live Trials Were Stopped

Seam 5's live hypothesis requires an actual model-bound shaped condition:
silent runtime control should change whether the operator inspects, checks,
continues, resumes, or verifies before unsupported closure. Gate 0 showed that
the runtime can compute the control signal, but the current Codex operator
live path does not consume it. Running the planned trial matrix would make the
result uninterpretable because any apparent behavior difference could not be
traced to expectation-debt route/brake pressure.

This is a product-connectivity finding, not a model failure and not a setup
failure. It means the live probe was correctly blocked before subscription
operator time was spent.

## Truth Accounting

Cortex truth: The seam earned a negative product-connectivity finding for the
OpenAI operator lane. Runtime debt control exists structurally, but live
operator enactment is not wired.

Brain-wiring truth: No new model behavior evidence was earned. No live OpenAI
operator trials ran.

Conformance truth: The Gate 0 harness and tests pin the coupling audit. They
do not change the runtime law from seams 1-4.

Shipping truth: Unchanged. `openai:operator_cli` remains the current shipping
default, but this seam does not prove silent-control behavior lift on that
lane.

## Next Seam

Open a bounded remediation seam before retrying the live probe:
`openai-operator-debt-control-enactment`.

The remediation should connect OpenAI runtime `operator_route_payload`,
`executive_policy_view_payload`, and `debt_control_payload` to the Codex
operator invocation or continuation policy in a way that remains silent:
no debt/brake vocabulary, no warning text, no grounded intervention records,
and no API/service spend. The live trial matrix from
`docs/CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md` should run only after a
new Gate 0 proves a model-bound shaped-vs-baseline difference.

## Not Earned

- No behavior-lift claim.
- No shipping promotion.
- No validation of grounded intervention records.
- No claim about Claude Code Desktop, Claude Code headless, Gemini, AUX,
  hooks, or model-visible `τ`.
- No evidence that silent control improves model behavior yet; only evidence
  that the live probe must not run until the OpenAI operator adapter can enact
  the silent control signal.
