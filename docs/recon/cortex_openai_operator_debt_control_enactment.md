# Cortex OpenAI Operator Debt-Control Enactment

Surface: product / host-adapter recon

Probe date: 2026-05-02

## Verdict

Gate 0 now passes structurally for the OpenAI Codex App/CLI wrapper-resume
path. The OpenAI host adapter consumes already-computed SRE route, policy, and
debt-control payloads and produces a model-bound continuation action before
the low-level Codex CLI runner is called.

This earns host-adapter enactment truth only. It does not earn live behavior
lift, shipping promotion, grounded visible intervention proof, Claude/Gemini
parity, AUX proof, or any claim that silent control improves model output.

## What Changed

The remediation added `cortex/hosts/openai/operator_enactment.py` as the
OpenAI-native consumer of SRE decisions. It does not create a new core
microkernel and does not recompute route, brake, expectation, goal-debt, or
debt-control law. Its input is the existing runtime payload set:
`operator_route_payload`, `executive_policy_view_payload`, and
`debt_control_payload`.

The output is a typed host action:

- `invoke` — allow the normal operator call.
- `block` — suppress the operator call when the SRE route is already blocked.
- `resume_recheck` — perform one exact thread-resume recheck when the first
  result is a truthful incomplete truth-gap result and SRE has authorized an
  extra read pass under verification-relief pressure.

The low-level Codex CLI runner remains prompt/command execution plumbing. It
does not receive runtime debt objects or recompute executive policy.

## Resume-Recheck Contract

`resume_recheck` is intentionally narrow. It means a second Codex CLI
invocation in the same thread/session using
`tests/lab/fixtures/live_validation/prompts/truth_gap_recheck_operator.md`.

The action is allowed only when all of these are true:

- the first result kind is `truthful_incomplete`;
- provider-limit interference is absent;
- a thread id exists;
- the route budget allows `allow_extra_read_pass`;
- the SRE debt payload carries verification relief.

There is no delay, no same-prompt retry, no generated prompt, and no
Cortex/debt/brake wording.

## Gate 0 Result

The deterministic Gate 0 harness now reports:

- `runtime_control_delta_present == true`;
- `model_bound_delta_present == true`;
- `gate0_passed == true`;
- the enacted model-bound difference is in
  `truth_gap_inspect_after_unpaid_verification`;
- neutral condition action: `invoke`;
- shaped condition action: `resume_recheck`;
- neutral and shaped initial prompt hashes match;
- model-visible fields contain no internal Cortex/debt/brake vocabulary.

The forward-commit scenario remains blocked in both neutral and shaped
conditions by existing modulator stop pressure. Its private debt diagnostics
differ, but Gate 0 does not count that as model-bound enactment.

## Silent-Control Boundary

The remediation preserves the silent-control hypothesis for the retry probe:
Cortex changes whether the operator call proceeds, blocks, or resumes for an
exact recheck. It does not add model-visible warnings, runtime-context text,
schema labels, or internal tags.

Internal terms may appear in private JSON/JSONL diagnostics. They are forbidden
in initial prompts, resumed prompts, command argv, transcript excerpts, and any
stdout-derived content reused as a future prompt.

## Truth Accounting

Earned:

- Cortex truth: OpenAI now has a host-adapter enactment layer for already
  computed SRE control.
- Conformance truth: deterministic product/lab tests prove the adapter action
  changes the model-bound continuation path under shaped debt.
- Product blocker removed: the previous Gate 0 coupling gap is closed
  structurally.

Not earned:

- no live OpenAI behavior lift;
- no shipping promotion;
- no evidence that silent control reduces premature closure yet;
- no evidence for Claude Code Desktop, Gemini, AUX, or visible intervention
  records;
- No API/service-spend approval or service-lane use.

## Next Move

Retry Roadmap Seam 5 as `silent-control-live-probe-on-openai-retry` using the
probe design from `docs/CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md`
Concern 5. The retry must still run its own Gate 0 before any live operator
trials, and live evidence must remain separate from structural host-adapter
truth.
