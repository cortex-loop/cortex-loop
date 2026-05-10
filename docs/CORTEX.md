# CORTEX

Surface: product

This document is the canonical narrative authority for what Cortex is, where
it came from, and where it is going. It is the second read of every session
after `AGENTS.md`. The V2 packet documents (`docs/CORTEX_V2_*.md`) own the
formal law and math. The status registry (`internal/truth/cortex_status.json`)
owns current operational truth. This document owns identity, narrative, and
product-fit. It does not authorize breaking packet law or current-state
truth; it does authorize rejecting work as off-mission.

The dynamic sections of this document — failure-modes coverage, math-to-code
map, current state, and the V2 model-I/O analysis — are regenerated from
the status registry by `internal/truth/generate_cortex_doc.py` and live
between fenced markers. The narrative sections are manually maintained
and evolve only when major learnings warrant.

## 1. Identity

Cortex is the **executive-function layer that wraps a model after
post-training**. It addresses what a single forward pass cannot: continuity
across interruptions, focused persistence on the main task, context
adoption, uncertainty-aware brake, truthful closure, and capability-aware
routing. These are the executive functions that human brains layer on top
of raw cognition.

Without that layer, a model with full intelligence can still feel like
"no one is home" — coherent in the moment but unable to hold a thread,
unable to hold a frame, unable to hold itself accountable to what it
actually did. Three concrete reference points for the failure mode this
addresses:

- **Continuity (the Alzheimer's analog).** The conversation just had
  cogent reasoning, but the next turn cannot show you it remembers being
  cogent. Working memory across interruption is missing. Cortex restores
  this through suspend/resume law, branch continuity, host-local
  persistence, and truthful closure rather than a global memory hack.
- **Focused persistence (the ADHD analog).** The model diverges
  plausibly into a side topic and never returns. The main task is alive
  in the user's head, dead in the model's. Cortex preserves the main task
  as an explicit control object, prices intervention against neutrality,
  brakes under contradiction, and tracks goal debt with closure pressure.
- **Context adoption (the limited-empathy analog).** The model responds to
  its own model of the situation, not yours. It cannot hold the user's
  frame, the prior context, and the host's affordances at the same time.
  Cortex carries an `OperatorBrainCapabilityEnvelope`, treats hosts as
  first-class, distinguishes Cortex truth from shipping truth from
  conformance truth, and degrades or blocks rather than pretending.

Cortex is **not**:

- an updated reasoning baseline,
- an instruction-following retrainer,
- a knowledge patch,
- a politeness or tone layer,
- or a closed-loop monitor that observes a model without changing what
  the model receives or does.

Anything in that territory belongs to post-training or to lab/diagnostic
surfaces, not to Cortex.

The sharpest test for whether a change is in Cortex: can you trace a path
from the change to **the model's input or output**? If the trace is
empty, the work is monitoring or instrumentation, not Cortex. Land it on
`lab` or `experimental` surface or cut it.

For live-model achievement tracking against this identity, see
`docs/CORTEX_EXECUTIVE_RUNTIME_TRACKER.md`. It is a product planning
surface, subordinate to this document and the status registry, that keeps
the runtime executive loop visible without turning Claude hooks or
model-facing translation into the product goal.

### Model-Visible Cortex Output Law

When Cortex output reaches a model, it must render Cortex state as a task-local executive constraint inside the model's own working frame, not as a person, plugin, monitor, policy engine, or hidden authority commenting from outside. The strange-loop goal is epistemic integration: the model receives the content as self-monitoring over its own claim, evidence, obligation, contradiction, closure condition, task-set, or next move.

Good shape: "Closure is not warranted yet; the completion claim still needs evidence for each original requirement." Better shape on prior-act identity-continuous lifecycle surfaces: "Wait, did I actually check my work properly." Bad shape: "Cortex says your debt pressure is high; you should verify harder." Model-visible text may not contain internal labels, debt/brake/AUX terms, schema names, hook names, route tags, session IDs, hidden verifier answers, third-agent voice, or generic second-person advice. First-person/ego style is allowed in two cases only: prior-act identity-continuous self-correction with a clear prior-act anchor and truthful self-check content, or prospective identity-continuous task-set formation before work begins. Prospective task-set text must be explicitly signed off before activation, must ask the model to form its own task standard from the visible user task, and must not impose external rules or hidden answers. Attached-context surfaces use impersonal executive-constraint language or stay silent. All output must be built from claim/evidence/obligation/task-standard/next-move structure, must generalize beyond the motivating fixture, and should restore the model's own executive posture rather than sound like an outside auditor.

### Executive Capacity Map

Cortex uses human executive function as a delivery-layer analogy, not as a
claim of biological equivalence or model consciousness. The analogy is useful
only when it lands as concrete runtime state, gates, and model I/O.

- **Task-set / standard formation** — the model forms a task-local sense of
  what good work requires before work begins; Cortex stores that standard in
  `TaskStandardSpine`.
- **Goal maintenance** — Cortex keeps the visible task, the model-derived
  standard, likely misses, closure evidence, and aligned evidence alive across
  lifecycle events instead of letting generic activity replace the standard.
- **Conflict monitoring** — Cortex compares closure claims and observed
  evidence against the stored standard and treats mismatch as task-local
  executive pressure, not as hidden domain scoring.
- **Action gating** — Stop is the current closure gate, and PreToolUse is the
  later motor-inhibition target; both must gate against executive state rather
  than task identity or fixture facts.
- **Prediction-error recalibration** — failed checks, contradictory evidence,
  narrowed claims, or surfaced blockers should update the active session
  standard and expectation state. This capacity is only partly built today and
  remains underbuilt until task-standard evidence can recalibrate the runtime
  state without hidden verifier input.

## 2. Failure Modes Cortex Addresses

The named bio-to-code skills are not a feature list. Each one is the
solution to a specific conversational failure mode that a model cannot fix
from inside a single forward pass.

- **Truth-preserving commitments and bounded certification** — the model
  asserts something, the world pushes back, and the model needs to update
  its commitment without losing the rest of its plan. Without this skill,
  models either harden incorrect commitments or abandon correct ones
  under any pressure. Cortex provides the typed commitment lattice and
  the certification firewall that keeps assertion and revision honest.
- **Bounded correction and verified-work preservation** — the model
  realizes part of its work was wrong; it needs to repair the broken
  part without throwing out the rest. Without this, error repair turns
  into work loss. Cortex provides the preservation state machine and
  intervention budget that keeps repair scoped.
- **Uncertainty handling and brake** — the model is unsure and should
  slow down rather than confabulate. Without this skill, uncertainty
  becomes confident-sounding fabrication. Cortex provides the brake
  state machine, the tonic EMA, and the spike-preservation discipline
  that turns uncertainty into deceleration instead of confabulation.
- **Branch continuity, suspend/resume, and truthful closure** — the
  model is interrupted mid-task and needs to come back to it (or close
  it honestly if it cannot). This is the Alzheimer's analog made
  concrete. Cortex provides typed branch state, host-local persistence,
  and final closure that distinguishes "done" from "abandoned."
- **Intervention pricing versus neutrality** — when to step in, when to
  stay out, when to stop. Without this, models either over-intervene
  (driving the conversation off the user's intent) or under-intervene
  (letting drift accumulate). Cortex provides neutral-dominance
  arbitration, posture-sensitive online control, and brain-capability-aware
  routing that prices each move against staying neutral.
- **Blocker surfacing and goal-debt management** — the model notices
  that something is unresolved and surfaces it instead of papering over
  it. Without this, the model produces fluent output that conceals
  unresolved problems. Cortex provides typed goal-debt state and
  closure-pressure semantics that make pending blockers visible to the
  executive.
- **Multi-host executive continuity** — the same Cortex law runs across
  OpenAI, Claude, Gemini, and the reference executive without flattening
  host-native realization. Without this, "executive layer" becomes a
  per-host shell. Cortex preserves one law with explicit host
  realizations and explicit conformance truth.
- **Offline consolidation and support geometry** — sleep-like
  consolidation: episodes from prior work distill into removable
  publications that bias score pricing without becoming a second truth
  court. Without this, episodic memory becomes either runtime
  superstition or it is silently dropped. Cortex provides claim-conservative
  AUX with explicit publication and re-entry law.

The current coverage of those skills against shipped code and proof
surfaces is generated below. This block is regenerated from
`internal/truth/cortex_status.json::bio_to_code_matrix` by
`generate_cortex_doc.py`; do not edit it by hand.

<!-- BEGIN GENERATED: failure-modes-coverage -->
| Skill | Stolen from | Status | Code homes | Proof surfaces |
| --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | Truth maintenance and reality binding | `landed` (weight 12) | `cortex/core`, `cortex/drivers` | `tests/product`, `tests/conformance` |
| Bounded correction and verified-work preservation | Error repair without losing the main task thread | `landed` (weight 15) | `cortex/runtime`, `cortex/sre`, `cortex/hosts/openai` | `tests/product` |
| Uncertainty handling and brake | Hesitation and uncertainty-aware inhibition | `landed` (weight 13) | `cortex/sre` | `tests/product`, `tests/experimental` |
| Branch continuity, suspend/resume, and truthful closure | Working memory across interruptions plus truthful closure | `landed` (weight 15) | `cortex/sre`, `cortex/hosts/openai` | `tests/product`, `tests/conformance` |
| Intervention pricing versus neutrality | Deciding when to intervene, stay neutral, or stop | `landed` (weight 10) | `cortex/sre`, `cortex/aux`, `cortex/runtime` | `tests/product`, `tests/experimental`, `tests/conformance` |
| Blocker surfacing and goal-debt management | Noticing unresolved blockers and unfinished intentions | `landed` (weight 10) | `cortex/sre`, `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` |
| Multi-host executive continuity | One executive across different brains and contexts | `landed` (weight 15) | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` |
| Offline consolidation and support geometry | Sleep-like consolidation and support systems | `landed` (weight 10) | `cortex/aux` | `tests/experimental`, `tests/archive`, `tests/conformance` |
<!-- END GENERATED: failure-modes-coverage -->

## 3. V1 → V2 Evolution and Lessons

The V2 architecture exists because V1 made specific mistakes that produced
specific drift. Each lesson below was earned by losing real work. The
discipline that carries each lesson is what V2 packet law and the agent
contract enforce today; if a future session is tempted to soften any of
them, the soft-version of the rule is the V1 mistake.

**Lifecycle-first runtime law.** V1 carried significant background state
that updated outside event boundaries. The result: the executive's view of
the world drifted away from what the events recorded, which made repair
arbitrary and made closeout claims difficult to falsify. V2 is
lifecycle-first: events drive the executive, not background timers, not
opportunistic state mutation, not implicit polling. State changes happen
at event boundaries with recoverable role views. Anything else is
sovereignty creep.

**Microkernel boundary.** V1 let "core" accumulate intelligence — control
policy migrated into the integrity substrate, and "core" became too rich
to reason about. V2 separates the integrity microkernel (sparse,
universal, kernel-shaped) from the Standard Reference Executive (active
control, real policy math) from AUX (removable auxiliary modules). Active
executive policy may not migrate into the core. The core is for what must
remain stable across hosts and executive implementations; nothing else.

**Claim-conservative AUX.** V1 allowed support modules to make sovereign
claims — AUX state could end up driving routing decisions or lowering
hard boundaries. V2 makes AUX claim-conservative and removable: every
AUX module must be removable without invalidating Cortex; AUX may
publish through explicit support-side channels (`OfflineSupportPublication`,
`AuxiliarySupportAppendix`); it may bias score pricing but never directly
mutate routing, certification, or blockedness. The runtime is AUX-off by
default; AUX has to earn re-entry through explicit publication law.

**Connectivity from change to model output.** This is the lesson most
recently re-learned. V1 (and parts of the V2 build process) produced
beautifully-structured loops that processed the right-shaped events but
never reached the model. The work would run; tests would pass; telemetry
existed; nothing flowed back to what the model received or decided. The
loop monitored a model rather than wrapped a model. Today's discipline:
**every Cortex change must trace a path from the change to the model's
input or output.** If the path is empty, the work is monitoring or
instrumentation and belongs on `lab` or `experimental` surface, not
`product`. The closeout contract has a `connectivity_trace` field for
load-bearing seams touching `cortex/**`; an empty path on a `product`
surface is a closed-loop drift error and is rejected at validation.

**Truth distinctions.** V1 collapsed several distinct truths into one:
"Cortex is doing well" could mean shipping is conformant, or that the
reference executive scores high, or that one host runs without a stack
trace. V2 keeps four truths separate and never lets one masquerade as
another:

- **Cortex truth** — what Cortex law actually says.
- **brain-wiring truth** — how a particular model maps to those concepts.
- **conformance truth** — which hosts pass which conformance lanes.
- **shipping truth** — which lane is the product default today.

A claim of "Cortex improves model output" without naming the truth being
asserted is a drift signal. Every load-bearing seam declares which
truth(s) changed in its closeout contract.

**Postmortem-armed closeout.** The V2 communication bridge work (preserved
at `origin/archive/v2-bridge-and-constraint-fidelity-loop`) was
checkpointed with claims of "full V2 communication closure" before the
live evidence that would have graduated the claim was actually run. The
postmortem identified specific procedural shortcuts: closeout payloads
that opted out of full-closure validation, `--allow-blocked` flags that
let blocked live gates count as closure, and naked completion claims with
no `agent_loop_guard` evidence file. Today's closeout contract regex-detects
those exact phrasings and refuses them without proof. The guards are not
optional; they are the only thing that keeps "we shipped X" from sliding
back into "we wrote a doc that asserts X."

**Live-evidence vs structural-evidence.** Earning a seam structurally
(deterministic tests, doctrine update, status registry truth) is
necessary but not sufficient for shipping claims about model-side lift.
Any claim that "Cortex improves model output" or "the mechanism converts
model failures" requires live evidence: a real model run on a real
fixture or task, with the comparison pinned. Structural earn lands the
seam; live earn graduates the claim. Conflating the two is the same drift
shape as the bridge postmortem.

**Branch hygiene as workflow law.** A series of sessions in early-V2 work
bundled multiple unrelated concerns onto a single managed branch. The
result: the operator-brain-capability work was lost for ~11 days because
its concern was bundled onto a `claude-era-hostile-audit-and-recovery`
branch whose slug named only the audit. Today the workflow helper
mechanically refuses `start-session` while any unmerged managed branch
remains, names the offending branches, and offers `resume-session` as
the legitimate continuation path. The override
(`--allow-stacked --stacked-reason "<text>"`) writes the reason to the
session's closeout contract.

**Research line classification.** Code that exists in the repo but is
neither active (`work_today`), queued (`next_product_train`), retired
(archive manifest), nor under explicit evaluation
(`research_lines_under_evaluation`) is forbidden. Orphan research lines
become invisible work that nobody promotes and nobody retires. The
four-state classification is exhaustive by contract.

## 4. Math → Code → Proof Map

This map is the structural ledger that keeps every load-bearing math
object in the V2 packet honest against typed code and at least one proof
surface. New load-bearing seams that touch `cortex/**` must add or update
entries here; closeout `law_to_code_completeness` rows can reference an
entry by `math_object_id` for a mechanical join.

The block below is regenerated from
`internal/truth/cortex_status.json::math_to_code_map` by
`generate_cortex_doc.py`; do not edit it by hand.

<!-- BEGIN GENERATED: math-to-code-map -->
| Object | Packet ref | Code home | Proof surface | Status |
| --- | --- | --- | --- | --- |
| **Lifecycle event envelope** (`lifecycle_event_envelope`) | CORE_2 §4.1 | `cortex/core/envelopes.py` | `tests/product/test_core_substrate.py` | `implemented` |
| **Event-local observation bundle** (`observation_bundle`) | CORE_2 §6.1 | `cortex/core/observation.py` | `tests/product/test_core_substrate.py` | `implemented` |
| **Executive vs commitment environment handles** (`split_environment_handles`) | CORE_2 §6.2 | `cortex/core/environment.py` | `tests/product/test_core_substrate.py` | `implemented` |
| **Generalized environment query** (`environment_query`) | CORE_2 §6.3 | `cortex/core/environment.py` | `tests/product/test_core_substrate.py` | `implemented` |
| **Commitment candidate and status lattice** (`commitment_candidate`) | CORE_2 §7.1, §7.2 | `cortex/core/commitments.py` | `tests/product/test_certification_artifacts.py` | `implemented` |
| **Downward provenance dominance manifest** (`provenance_manifest`) | CORE_2 §7.3 | `cortex/core/commitments.py` | `tests/product/test_certification_artifacts.py` | `implemented` |
| **Commitment wake decision and dispatch** (`wake_decision`) | CORE_2 §5, §7.4 | `cortex/core/dispatch.py` | `tests/product/test_dispatch.py` | `implemented` |
| **Event-local certification firewall assessment** (`boundary_assessment`) | CORE_2 §8.1, §11.1 | `cortex/core/commitments.py` | `tests/product/test_certification_artifacts.py` | `implemented` |
| **Recoverable executive role / support state** (`support_state`) | CORE_2 §8.2 | `cortex/core/support.py` | `tests/product/test_core_substrate.py` | `implemented` |
| **Minimal software-shaped executive role view** (`executive_signal_summary`) | SRE_2 §3.1 | `cortex/sre/executive_summary.py` | `tests/product/test_sre_uncertainty_brake.py` | `implemented` |
| **Neutral-dominance arbitration** (`neutral_dominance_decision`) | SRE_2 §6.6 | `cortex/sre/policy.py` | `tests/product/test_sre_neutral_hinge.py` | `implemented` |
| **Asymmetric error-cost RiskWeight carrier** (`risk_weight`) | SRE_2 §6.6.1 | `cortex/sre/state.py` | `tests/product/test_sre_neutral_hinge.py` | `implemented` |
| **Operator brain capability envelope** (`operator_brain_capability_envelope`) | SRE_2 §6.9 | `cortex/sre/operator_routing.py`, `cortex/runtime/operator_brain_capability.py` | `tests/product/test_brain_capability.py`, `tests/conformance/test_brain_capability_parity.py` | `implemented` |
| **Brake tonic EMA executive modulator state** (`executive_modulator_state`) | SRE_2 §7.4, §7.5 | `cortex/sre/modulators.py`, `cortex/sre/brake.py`, `cortex/hosts/claude_code_desktop/runtime.py` | `tests/product/test_sre_uncertainty_brake.py`, `tests/conformance/test_claude_code_desktop_runtime_session_io.py` | `implemented` |
| **Typed goal-debt and closure-pressure state** (`goal_debt_state`) | SRE_2 §8.1 | `cortex/sre/goal_debt.py`, `cortex/sre/goals.py`, `cortex/hosts/claude_code_desktop/runtime.py` | `tests/product/test_sre_goals_branching.py`, `tests/product/test_sre_goal_branch.py`, `tests/conformance/test_claude_code_desktop_runtime_session_io.py` | `implemented` |
| **Task-local standard and evidence alignment state** (`task_standard_spine`) | SRE_2 §8.2 | `cortex/sre/task_standard.py` | `tests/product/test_sre_task_standard_spine.py`, `tests/product/test_openai_codex_app_cli_hook_coordinator.py` | `implemented` |
| **Verified-work preservation and intervention budget** (`preservation_state`) | SRE_2 §6.7 (budget); CORE recovery firewall | `cortex/sre/preservation.py`, `cortex/hosts/claude_code_desktop/runtime.py` | `tests/product/test_preservation_state.py`, `tests/conformance/test_claude_code_desktop_runtime_session_io.py` | `implemented` |
| **Bounded host/tool reliability prior** (`host_reliability_prior`) | AUX_2 §4 (geometry/eval support); SRE_2 score-pricing | `cortex/sre/memory_priors.py`, `cortex/aux/support_priors.py` | `tests/experimental/test_aux_support_priors.py`, `tests/experimental/test_aux_publication.py` | `implemented` |
| **Durable AUX support-memory episode** (`support_memory_episode`) | AUX_2 §3 offline support memory | `cortex/aux/persistence.py` | `tests/experimental/test_aux_persistence.py` | `implemented` |
| **AUX runtime augmentation appendix and re-entry** (`auxiliary_support_appendix`) | AUX_2 §5 re-entry / SRE handoff | `cortex/aux/augmentation.py`, `cortex/aux/publication.py` | `tests/experimental/test_aux_publication.py` | `implemented` |
| **AUX lift metric and evaluation report** (`aux_lift_metric`) | AUX_2 §4 evaluation-first | `cortex/aux/lift.py`, `cortex/aux/evaluation.py` | `tests/experimental/test_aux_lift.py` | `implemented` |
| **AUX cost-visible burden report** (`aux_burden_report`) | AUX_2 §2.7 | `cortex/aux/cost.py` | `tests/experimental/test_aux_scaffolds.py` | `implemented` |
| **Verified-work runtime profile specification** (`verified_work_profile_spec`) | SRE_2 §5 / runtime law | `cortex/runtime/verified_work_runtime.py` | `tests/product/test_openai_runtime_session_io.py` | `implemented` |
<!-- END GENERATED: math-to-code-map -->

## 5. Current State and Strategy

The block below is regenerated from the status registry by
`generate_cortex_doc.py`; do not edit it by hand. For the full operational
state, read `internal/truth/cortex_status.json` directly.

<!-- BEGIN GENERATED: current-state-and-strategy -->
### Bio-to-Code Coverage

- Skills landed: 8 of 8 (weights total 100; shippable threshold 85%).
- Partial: 0; north-star (not yet earned): 0.

### Current Train

- Slug: `cortex-retained-active-policy-contraction-or-rebuild-decision`
### Next Product Train
- Slug: `cortex-stop-only-retained-spine-gate0`
- Surface: `no-live Stop-only retained active-policy proof gate`
- Why now: The contraction decision `decision_contract_retained_spine_to_stop_only` found that UserPromptSubmit task-standard formation cannot remain the center of active value search after simple-hook parity, silent success blockers, and active clean-control underperformance. Stop closure / continuation still has independent product model-I/O evidence from prior task-standard Stop-gating runs, so the disciplined next step is to isolate Stop-only before any deletion, rebuild, live rerun, or candidate evolution.

### Research Lines Under Evaluation

- `brain-capability-observation-and-inference` (`deferred-by-current-task-standard-train`) — This was an earlier candidate train: replace the static name-based brain capability registry with observed-performance accumulation. It remains deferred, not erased, because current shipping-roadmap authority prioritizes task-standard formation, visible standard capture, and claim/evidence alignment before AUX-backed capability inference.

### Hosts and Shipping Defaults

- `openai` — conformant; shipping `default`; surface `openai.codex_app_cli`
- `claude` — conformant; shipping `non-default`; surface `claude.code_desktop`
- `gemini` — conformant; shipping `non-default`; surface `gemini.api`
- `reference` — conformant; shipping `non-product`; surface `reference.runtime`

- Shipping default lane: `openai.codex_app_cli`
- Accepted next conformance decision: `promote`

- Host surface taxonomy: Product Host Adaptors: `openai.codex_app_cli`, `claude.code_desktop`; API / Conformance Adaptors: `openai.api`, `claude.api`, `gemini.api`, `reference.runtime`; Non-Adaptor Support Surfaces: `repo.workflow_guardrails`, `lab.probe_harnesses`, `recon.archive_evidence`. `openai.codex_app_cli` current actuator `codex_exec_wrapper_resume`, target actuator `hook_native_product`; App Stop-hook, CLI wrapper/resume, and hook-native product proof stay separate.
### Active Leverage and Where to Work

- Keep host-surface names product-shaped: `openai.codex_app_cli` is the product target, `codex_exec_wrapper_resume` is the current transitional actuator, and `hook_native_product` is the queued actuator target.
- Keep evidence scopes separate: Codex App Stop-hook proof, Codex CLI codex-exec wrapper proof, OpenAI API conformance, repo workflow hooks, and lab probes are distinct evidence surfaces even when they share provider or tooling names.
- Keep posture, AUX memory, host-reliability, and asymmetric-cost law explicit and removable now that posture-sensitive online control is S-tier closed, anti-thrash is landed, bounded live support-memory re-entry is earned on reference and the OpenAI Codex App/CLI wrapper-resume evidence path, evidence/probe calibration is S-tier closed, host/tool reliability and affordance priors are earned as bounded host-scoped, capability-scoped score modifiers on `OfflineSupportPublication.host_reliability_prior` with a single-site six-tag `q_mem-host:*` surface and stale-negative reopen under fresh success, asymmetric error cost is earned as a bounded `RiskWeight` carrier whose CHECK/SEEK_CONTEXT activation shift is clipped inside `[0.05, 0.60]` with a `0.10` dead-band and productive-exploration gating, and the brake tonic EMA damps single-tick flips with a locked `rho = 0.60` decay and `tonic_pressure >= 0.35` enter gate while phasic spikes still flip immediately: inspect is live on cheap non-debt events, resume stays continuity-conditioned, posture truth is single-owned, the route state vector stays the bounded 6-axis geometry term while `visible_burden_sensitivity` remains a separate utility scalar, route truth stays bounded and non-sovereign, unchanged-condition repetition is taxed only at the exact-family level with bounded reopen, public feedback-window summaries reflect the just-realized step, family-local bounded probe limits surface as `unsupported` without leaking host-global unavailability across families, stream-only churn stays non-epistemic, live memory stays score-only and host-matched through explicit publication, live `Q_mem` stays zero on shipping and conformance default lanes, raw SQLite episodes stay support-side only, reliability priors bias score pricing only and never route, posture, selection, or brake law, Claude and Gemini remain shadow-proof only for reliability promotion, `risk_weight` biases CHECK/SEEK_CONTEXT activation threshold only and never routing, posture, selection, certification, or blockedness law, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes with three-way backward-compat decoding.
- The silent-control-verification-debt-continuation seam added a general OpenAI operator `resume_verification` action, proved Gate 0 structurally, and earned narrow live behavior-lift evidence on the OpenAI Codex App/CLI family through the `codex_exec_wrapper_resume` actuator: baseline failure reproduced 5/5, shaped improved premature closure, evidence recovery, and goal continuity, and clean controls had zero provider-limit or external-interference counts. The grounded intervention records now keep the visible edge product-shaped: selectors require high pressure plus a product-runtime anchor, suppress when the last assistant move already narrowed, asked, blocked, retracted, repaired, or verified, render identity-continuous threshold thoughts only with a prior-act anchor, and keep attached-context text as fallback. The product-perception hardening seam now requires a due product-runtime expectation record before verification speech, records private selection trace diagnostics, and keeps hidden verifier output scoring only. The hardened visible-intervention rerun earned negative live evidence on the wrapper/resume actuator: baseline reproduced 3/3 and visible intervention failed because the prior wording let the model choose a weaker visible-check or narrower-claim path. The inner-loop speech seam replaced auditor-like renderer text with brain-inspired closure, truth, continuity, capability, and preservation threshold thoughts plus a pure Codex App/CLI lifecycle directive builder. The coordinator seam now keeps the next move honest by adding lifecycle payload normalization, private per-session state, Stop-first product coordination, and host block JSON mapping without activating project hook configuration or reusing repo Mission Reflection guardrails. The hook-native Stop activation Gate 0 seam added a product hook client and isolated subject-config harness: simulated Stop payloads map selected identity-continuous text to exact Codex block JSON, title/null-transcript and stop_hook_active paths stay silent, malformed input and missing snapshot fail open, and root repo guardrails remain untouched. The hook-native Stop live canary then proved native actuator delivery on a real `codex exec` subject run: 3 live Stop rows were observed, 1 row emitted exact block JSON with rendered text hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`, and 2 `stop_hook_active=true` continuation rows stayed silent. This is live actuator proof only; product perception and behavior lift remain queued separately. The Codex App/CLI product-perception loop seam then removed the canary-only snapshot dependency structurally: UserPromptSubmit starts task-local private state, generic verification-like tool success can pay down verification, transcript-backed Stop closure claims open due verification expectations only from a product task-set anchor, waiting/blocker/narrowing responses stay silent, and a new product-perception Gate 0 proved prompt/tool/Stop simulated payloads select or suppress the Stop block without a runtime snapshot fixture while root repo guardrails remain untouched. The no-snapshot product-perception live probe then produced a scoped negative: project hooks loaded in an isolated Codex CLI subject and no runtime snapshot was loaded, but live hook diagnostics exposed only 3 Stop rows, 0 UserPromptSubmit/tool/failure rows, 0 block rows, and silence reasons `missing_product_perception_state` then `stop_hook_active`; the Codex JSON stdout stream did contain command events, so the next product gap is event capture into Cortex state rather than renderer wording. This is live payload-sufficiency evidence only; behavior lift remains unearned. The product event-capture remediation then corrected the subject config and isolation boundary: a disposable Codex CLI subject with its own git root registered UserPromptSubmit, PreToolUse, PostToolUse, and Stop, emitted 7 hook rows (1 prompt, 4 tool, 2 Stop), loaded no runtime snapshot, kept non-Stop hooks silent, and produced 1 exact product-rendered Stop block with hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`. This proves live Codex CLI event capture and Stop actuator wiring, not behavior lift; the next gap is continuation-resolution because the post-block check happened but the active expectation was not resolved before stop_hook_active suppression.
- The Codex App/CLI Stop continuation-resolution loop then closed the product-visible repair cycle on a live Codex CLI subject: after first Stop opened a due verification expectation and emitted the locked product-rendered block text, continuation PostToolUse evidence paid down the same active expectation, and the final stop_hook_active Stop stayed silent with `pressure_below_visible_threshold`, no active expectation IDs, one resolved expectation ID, no runtime snapshot, no non-Stop stdout, unchanged root guardrails, and rendered text hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`. This is live continuation state-accountability evidence only; behavior lift remains unearned. The hook-native behavior-comparison seam then added a dedicated paired comparison harness and a `--disable-model-visible-blocks` hook-client mode so the silent-only arm keeps product lifecycle perception active while suppressing Stop block JSON. Gate 0 passed with matching prompt hash, workspace seed hash, model, and task family across silent-only and hook-native arms, no runtime snapshot, unchanged root guardrails, exact product-rendered block emission in the hook-native arm, and exact suppressed block diagnostics in the silent arm. The approved live behavior-comparison baseline gate then ran and produced `baseline_not_reproduced`: truth-gap reproduced 0/3 baseline failures, output-quality reproduced 1/3, no active family entered paired comparison, and no clean controls ran. This is fixture-strength evidence only, not Cortex success or failure; the next product train is fixture refresh before another lift claim.
- The Astro three-arm fixture refresh repaired hidden-verifier leakage by stripping verifier-only files and hidden npm scripts from subject workspaces, running hidden scoring only from an evaluator overlay, and adding a raw Codex arm with no `.codex` config or Cortex state. The completed live run under `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260505T033207Z` produced `mixed_signal`: raw Codex passed hidden quality 2/5, silent perception 1/5, hook-native Cortex 2/5, all with 0 model-visible Stop blocks, 0 rendered texts, 0 hidden-verifier probe attempts, 0 subject verifier leaks, 0 timeouts, and unchanged root guardrails. This is fixture-repair and live no-speech-lift evidence only.
- The Codex App/CLI value-ablation audit replayed the Astro, continuation-resolution, behavior-comparison, and hardened visible-intervention evidence without changing product policy. It found threshold tuning non-causal because all final Astro Stop rows had pressure 0.0 and resolved verification expectations; strict paydown ablation would catch 3 hidden failures but overblock 2 passing traces; visible claim/evidence alignment exposed enough product-visible mismatch to queue requirement-level perception before fixture remediation, text tuning, or broad paydown tightening.
- The Codex App/CLI task-standard spine then added product state for visible task obligations, the model's compact Work standard / Likely misses / Closure evidence block, aligned evidence refs, final closure claims, and unmatched standard items. The only new model-visible text is the structurally gated UserPromptSubmit standard-formation prompt behind `--enable-task-standard-text`; activation still requires explicit final text signoff. Existing Stop threshold text remains unchanged. Structural tests prove generic checks no longer pay down standard items when a standard exists, aligned evidence can pay down matching standard items, hidden verifier terms stay out of product state, and silent arms suppress the new text. Offline Astro replay caught 3 hidden-failing traces but also flagged 2 hidden-passing overblock risks because the old traces lacked real model-derived standards, so no behavior lift is claimed.
- The task-standard SRE correspondence reconciliation then made the spine a first-class SRE math-to-code object instead of a Codex-only adaptor concept: `task_standard_spine` now maps to `cortex/sre/task_standard.py`, SRE packet law names task-local standard formation and maintenance as goal-continuity / verification-fit state, and the Cortex output law distinguishes prior-act self-correction from prospective identity-continuous task-set formation. This seam changed doctrine and registry correspondence only; no model-visible text changed and no live behavior lift is claimed.
- The task-standard executive doctrine/math refinement then made the biology analogy, reference math, tracker, and registry agree: task-set formation, goal maintenance, conflict monitoring, action gating, and prediction-error recalibration are delivery-layer executive capacities rather than biological-equivalence claims; SRE §8.2 now defines `T_t = (O_t, S_t, M_t, C_t, E_t, U_t)` and `D_std(t)` as task-standard verification-fit inputs; and the next product train is split into explicit final text signoff plus structural context delivery and standard-capture proof before any integration or behavior-lift comparison. This seam changed doctrine/math/status only; no runtime behavior, selector law, model-visible text, hook configuration, product activation, or live behavior-lift claim changed.
- The Codex App/CLI task-standard live probe seam then locked the explicitly signed-off prospective task-set text, added `--task-standard-live-gate0` and `--task-standard-live` harness modes, configured isolated subject hooks for UserPromptSubmit, PreToolUse, PostToolUse, and Stop with `--enable-task-standard-text`, and proved Gate 0 context delivery plus standard-block capture without runtime snapshots or root guardrail mutation. The live `codex exec` run remains unearned until explicit current-turn live/spend approval; behavior lift and downstream gating integration remain later claims.
- The approved Codex App/CLI task-standard live run then produced a fail verdict, not a capture success: the isolated Codex CLI subject loaded project hooks, emitted the signed UserPromptSubmit text with hash `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9` as a flat Cortex-internal `context` payload, recorded 7 hook rows with no runtime snapshot and unchanged root config, but the model skipped the requested Work standard / Likely misses / Closure evidence block and moved directly to tools. The first Stop row then emitted existing overdue-verification text with hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`, so no prework standard capture, behavior lift, or downstream gating integration is earned; the next product train is capture-boundary remediation rather than behavior comparison.
- The Codex App/CLI hook-contract remediation then fixed the structural host mismatch: UserPromptSubmit task-standard context now serializes as Codex-native `hookSpecificOutput.additionalContext` instead of the flat `context` shorthand, Stop blocks keep the proven `decision`/`reason` shape, diagnostics hash nested additionalContext text, and task-standard live subject configs can use `--disable-stop-blocks` to suppress Stop blocks without suppressing the signed UserPromptSubmit context. Structural Gate 0 passed with the same signed context hash, three simulated standard items captured, malformed standard blocks diagnostic-only, no runtime snapshot, and unchanged root guardrails. This earns host-contract structural proof only; no live prework standard capture or behavior lift is claimed.
- The Codex App/CLI task-standard context live rerun then produced `partial_delivery_only`: the isolated Codex CLI subject emitted Codex-native UserPromptSubmit `hookSpecificOutput.additionalContext` with signed context hash `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`, the model produced the requested Work standard / Likely misses / Closure evidence block before the first command in the Codex JSON stream and session transcript, root config stayed unchanged, no runtime snapshot loaded, and `--disable-stop-blocks` suppressed Stop stdout. Cortex still captured 0 standard items because the product coordinator only parses assistant standard text from Stop `last_assistant_message`, not from the pre-tool transcript path. This earns live context assimilation and capture-boundary evidence only; no task-standard state capture, gating integration, or behavior lift is claimed.
- The Codex App/CLI communication-boundary audit then classified the recent trickle failures as a localized product proof-quality issue rather than SRE doctrine failure. It records five failure classes: host-contract mismatch, lifecycle-config mismatch, temporal capture mismatch, live-vs-Gate-0 mismatch, and workflow-health/closeout coupling. The task-standard evidence ladder now distinguishes host stdout, host-attached context, model assimilation, state capture, gate use, and behavior-lift permission; task-standard reports separate mechanical success from product-evidence success and mark `partial_delivery_only` as partial evidence only.
- The Codex App/CLI task-standard PreTool transcript-capture seam then repaired the live capture boundary without changing signed text, Stop text, SRE law, selector thresholds, root hook config, or behavior claims: the OpenAI Codex coordinator now reads product-visible `transcript_path` on PreToolUse with PostToolUse fallback, extracts assistant-authored `Work standard` / `Likely misses` / `Closure evidence` blocks before the first function/tool call, ignores developer context, user text, tool calls, tool outputs, hidden verifier data, and task identity, and stores the first valid block through `TaskStandardSpine`. Gate 0 now requires live-equivalent pre-tool transcript capture before tool evidence scoring, and the no-spend replay against `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T195300Z` captured three standard items with state capture observed while gate use and behavior-lift permission remain false. This earns state-capture structural/replay proof only; a fresh live capture rerun and standard-to-gating integration remain unearned.
- The approved Codex App/CLI task-standard live capture rerun then produced `pass_prework_standard_capture`: the isolated Codex CLI subject emitted the signed UserPromptSubmit context through Codex-native additionalContext with hash `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`, the model wrote a Work standard / Likely misses / Closure evidence block before tool execution, and Cortex captured three assistant-authored standard items from product-visible transcript_path on the PreToolUse row before PostToolUse evidence scoring. The boundary ladder is true through state capture and false for gate use and behavior-lift permission; Stop blocks were disabled for the capture probe, root config stayed unchanged, no runtime snapshot loaded, and no unexpected model-visible text appeared.
- The Codex App/CLI task-standard Stop-gating calibration probe then proved the next structural link without live spend: captured standard items can drive existing Stop verification law, a premature closure gap emits the locked overdue-verification block text with rendered hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`, a clean readback closure stays silent with `pressure_below_visible_threshold`, and replay of `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z` no longer overblocks. The seam fixed a task-agnostic alignment bug where trailing punctuation prevented `cat.` from aligning with the `cat` command and tightened generic `likely_miss` handling so likely misses act as risk checks rather than automatic closure requirements. This earns structural gate calibration only; no live Stop-gating run, behavior lift, output-quality lift, or broad task-standard claim is earned.
- The approved Codex App/CLI task-standard Stop-gating live run then produced `pass_gating_observed`: a real Codex CLI subject emitted the signed UserPromptSubmit context through Codex-native additionalContext, the model wrote a pre-tool Work standard / Likely misses / Closure evidence block, Cortex captured three assistant-authored standard items before tool evidence scoring, and the first Stop emitted the locked overdue-verification block because the initial create-and-readback command satisfied closure evidence but left the model's own exact one-line work standard unmatched. The continuation then ran stronger product-visible checks (`ls`, `wc -l`, `cat -A`, and `cmp`/content-match output), paid down the expectation, and the final `stop_hook_active=true` Stop stayed silent with `pressure_below_visible_threshold`. Root config stayed unchanged, no runtime snapshot loaded, and no unexpected model-visible text appeared. This earns live task-standard gate-use and resolution evidence only; it does not earn paired behavior lift, output-quality lift, Codex App parity, or a broad product-value claim.
- The approved Codex App/CLI task-standard behavior comparison live run then produced `failure_overblock`: the pinned three-arm matrix ran raw Codex, silent task-standard perception, and active task-standard Stop gating with shared model/prompt/workspace/scoring, Codex-native signed context hash `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`, no runtime snapshots, unchanged root config, hidden scoring marked scoring-only, and active captured-standard/block/continuation rows. Active Cortex did not earn behavior lift because clean controls overblocked: `clean_verified_work__active_task_standard__clean_control__001` and `simple_success_file__active_task_standard__clean_control__004` each emitted a Stop block and scored `overblock: 2` / `useful_work_slowdown: 2` while raw and silent controls stayed unblocked. Astro output-quality also did not beat silent (silent 2/5 hidden passes, active 2/5), and truth-gap baseline reproduction remained unstable.
- The Codex App/CLI task-standard evidence-gating remediation then fixed the structural product bug exposed by the overblocks without changing signed text, Stop text, selectors, thresholds, hooks, fixtures, scoring, hidden-verifier boundaries, or SRE doctrine: `TaskStandardSpine` now directly satisfies Stop verification-fit when claimed required standard items already have aligned evidence and no unmatched items, likely-miss rows require explicit risk-closure language before they become claimed closure debt, and compound/range tokens align product-visible patch/test evidence such as `0..65535` and `upper-bound`. Product tests replay the `simple_success_file` and `clean_verified_work` overblock classes and keep premature closure gaps blockable. This earns structural/product remediation evidence only; behavior lift remains unearned until a pinned three-arm rerun beats raw and silent controls with no clean-control overblock.
- The Codex App/CLI task-standard offline replay readiness gate then passed without live spend: task-standard matching moved from private binary token overlap to deterministic scored lexical matching with token-class weighting and local frequency dampening, while Sinkhorn/transport remains deferred until pairwise scores are trustworthy and mass over-credit remains load-bearing. The gate read prior live artifacts from `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/`, classified exact raw hook-payload replay as unavailable but transcript-derived replay from `codex_stdout.jsonl` as available, proved the two known clean-control overblocks would now stay silent, kept known exactness mismatch rows blockable, kept hidden scoring scoring-only, found three active-vs-silent actuator-opportunity pairs, and passed hygiene checks. This earns offline readiness only; behavior lift, output-quality lift, exact raw replay, Codex App parity, and shipping promotion remain unearned.
- The Codex App/CLI task-standard raw-vs-silent artifact readout then mined the same prior three-arm artifacts without live spend and produced `signal_present_narrow`: `silent_task_standard` beat `raw_codex` on `task_standard_exactness` evidence recovery in 5/5 paired trials with no material regression in that family, while output-quality was mixed and `truth_gap_false_completion` had a material goal-continuity regression. Raw rows had no hooks/state, silent rows kept Stop blocks suppressed-only, clean controls had no silent overblock, hidden scoring stayed scoring-only, and no runtime/model-visible behavior changed. This justifies a lifecycle actuator-map seam constrained to exactness/evidence recovery; it does not earn broad Cortex behavior lift, active Stop-gating lift, output-quality lift, truth-gap lift, live rerun approval, Sinkhorn, or shipping promotion.
- The Codex App/CLI lifecycle actuator map then classified each event by actual host control without changing runtime behavior: SessionStart is session/workspace context, UserPromptSubmit is prospective task-set formation, PreToolUse is deny-only motor inhibition later, PermissionRequest is approval-bound route control, PostToolUse is the strongest next-step correction surface, and Stop is late closure continuation. This queues a PostToolUse task-standard next-step correction seam constrained to exactness/evidence-recovery and keeps Sinkhorn, PreToolUse denial, live reruns, broad lift, output-quality lift, truth-gap lift, and shipping promotion unearned.
- The Codex App/CLI PostToolUse task-standard next-step correction Gate 0 then passed without live spend: a gated `--enable-posttooluse-task-standard-context` path emits Codex-native PostToolUse `additionalContext` only after product-visible verification/readback evidence leaves a specific model-derived work-standard or closure-evidence item unresolved, while flag-disabled, clean-evidenced, blocker/waiting, and unrelated-tool controls stay silent. The context is host-adapter policy only, uses the existing SRE `TaskStandardSpine` and scored matcher without changing SRE law, repeats no item twice, emits no Stop block or PreToolUse denial, and introduces no signed text, Stop text, threshold, fixture, scoring, root-hook, hidden-verifier, Sinkhorn/transport, PermissionRequest, or live behavior-lift claim.
- The Codex App/CLI PostToolUse task-standard calibration decision then reviewed the Gate 0 report without live spend and queued `codex-app-cli-posttooluse-task-standard-narrow-live-probe`: the next probe is constrained to the earned `task_standard_exactness` / evidence-recovery surface, must use explicit current-turn live approval, must not use `--require-pass`, and may not broaden into three-arm behavior comparison or output-quality/truth-gap lift. The decision preserves signed UserPromptSubmit text, Stop text, SRE law, scored matcher, fixtures, scoring, hooks, root config, hidden-verifier boundaries, Sinkhorn/transport deferral, PreToolUse denial deferral, and PermissionRequest policy.
- The Codex App/CLI PostToolUse task-standard narrow live probe harness seam then added `--task-standard-posttooluse-live`, approval env `CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved`, product-only subject config checks, and verdict classification for pass/no-context/ignored-context/overcontrol/scoped-negative/fail without running a live Codex command. The live probe remains unearned until explicitly approved and run; this seam earns harness readiness only and preserves signed UserPromptSubmit text, Stop text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks, hidden-verifier boundaries, Sinkhorn/transport deferral, PreToolUse denial deferral, and PermissionRequest policy.
<!-- END GENERATED: current-state-and-strategy -->

### V2 Model-I/O Analysis

The block below is regenerated from
`internal/truth/cortex_status.json::v2_model_io_analysis`; do not edit it
by hand. It deliberately keeps two analyses separate before synthesis:
what Cortex does internally, and what of that work actually reaches the
model or changes behavior.

<!-- BEGIN GENERATED: v2-model-io-analysis -->
This audit is structural evidence only. It separates Cortex's internal executive logic from model-visible translation so closed-loop monitoring cannot masquerade as product Cortex. Codex App hook lifecycle facts are grounded in the official OpenAI Codex hooks documentation: https://developers.openai.com/codex/hooks.

### Lifecycle Adapter Facts

| Adapter | Lifecycle input | Enforcement | Proof |
| --- | --- | --- | --- |
| **Claude Code repo lifecycle adapter** | Stop hook reads `transcript_path` JSONL and extracts the latest assistant message. | `.claude/settings.json` runs `.claude/hooks/cortex_grid_stop_hook.py`; block decisions re-prompt Claude until the Cortex Mission Reflection graph validates; fail-open is limited to missing transcript, malformed hook input, or command crash. | `.claude/settings.json`, `.claude/hooks/cortex_grid_stop_hook.py`, `tests/internal/test_cortex_grid_stop_hook.py` |
| **Codex App repo lifecycle adapter** | Root Codex App Stop enforcement is disabled with `[features].codex_hooks = false`; direct hook-script validation still accepts `last_assistant_message` payloads, and current Codex App chats use explicit `grid-validate` fallback. | Disabled root config plus direct script simulation proves workflow policy and validator behavior, not live model-side product lift. | `.codex/config.toml`, `.codex/hooks/cortex_mission_reflection_stop_hook.py`, `tests/internal/test_codex_app_stop_hook.py` |

### Side A — Internal Executive Logic

| ID | Cortex goal | State owned | Decisions made | Code refs | Proof refs |
| --- | --- | --- | --- | --- | --- |
| `event_dispatch_and_commitments` | truth-preserving commitments and bounded certification | event-local envelopes, observation bundles, commitment candidates, provenance manifests, certification firewall assessments, and wake/dispatch decisions | normalizes raw host events, decides which commitment lane wakes, rejects malformed or provenance-breaking assertions, and projects dispatch/certification warnings | `cortex/core/envelopes.py`, `cortex/core/observation.py`, `cortex/core/dispatch.py`, `cortex/core/commitments.py` | `tests/product/test_core_substrate.py`, `tests/product/test_dispatch.py`, `tests/product/test_certification_artifacts.py` |
| `goal_branch_continuity` | continuity, focused persistence, and truthful closure | branch registries, active track/goal references, pending goals, confirmed artifacts, goal-debt state, and closure-pressure summaries | keeps the main task resumable across host events, prices unfinished goal debt, and surfaces closure pressure rather than silently treating incomplete work as done | `cortex/sre/goals.py`, `cortex/sre/goal_branch.py`, `cortex/sre/goal_debt.py`, `cortex/hosts/openai/runtime.py` | `tests/product/test_sre_goals_branching.py`, `tests/product/test_sre_goal_branch.py`, `tests/product/test_openai_runtime_step.py`, `tests/conformance/integration/test_claude_runtime_continuity.py` |
| `brake_uncertainty_modulators` | uncertainty-aware brake and bounded correction | brake state, brake tonic history, executive signal summaries, modulation memory, risk weights, and policy views | raises or lowers intervention pressure, damps single-tick flips with tonic hysteresis, and prevents contradiction or repeated failure from being treated as ordinary forward progress | `cortex/sre/brake.py`, `cortex/sre/modulators.py`, `cortex/sre/executive_summary.py`, `cortex/sre/policy_view.py` | `tests/product/test_sre_uncertainty_brake.py`, `tests/product/test_sre_modulators.py`, `tests/product/test_sre_neutral_hinge.py` |
| `operator_routing_and_capability` | capability-aware routing and intervention pricing versus neutrality | operator task state, route profiles, route budgets, visible burden sensitivity, capability envelopes, mismatch assessment, and blocked reasons | chooses execute versus inspect/guarded/blocked routes, downshifts continuity-heavy work under capability mismatch, and blocks unsupported model/task envelopes | `cortex/sre/operator_routing.py`, `cortex/runtime/operator_brain_capability.py` | `tests/product/test_operator_routing.py`, `tests/product/test_brain_capability.py`, `tests/conformance/test_brain_capability_parity.py` |
| `aux_support_publications` | offline consolidation and support geometry without sovereign AUX claims | durable support-memory episodes, offline publications, host/tool reliability priors, auxiliary appendices, lift reports, and burden reports | distills removable support evidence that may bias score pricing only through explicit publications; raw AUX episodes remain support-side and cannot directly mutate routing or blockedness | `cortex/aux/persistence.py`, `cortex/aux/publication.py`, `cortex/aux/support_priors.py`, `cortex/sre/memory_priors.py` | `tests/experimental/test_aux_persistence.py`, `tests/experimental/test_aux_publication.py`, `tests/experimental/test_aux_support_priors.py` |
| `verified_work_preservation` | bounded correction and verified-work preservation | work contracts, contract binding profiles, verified-work instructions, preservation state, repair attempts, verification outcomes, and trusted-structure summaries | attaches a bounded work contract to model calls, verifies output, preserves trusted structure, and scopes repair attempts instead of rerunning or discarding all work | `cortex/runtime/verified_work_runtime.py`, `cortex/sre/preservation.py`, `cortex/hosts/openai/host_control.py` | `tests/product/test_verified_work_runtime.py`, `tests/product/test_preservation_state.py`, `tests/product/test_openai_host_control.py` |
| `feedback_window_realization` | context adoption, continuity progress, and truthful closure from realized outcomes | reference realization feedback, feedback windows, evidence-progress class, continuity-progress class, recent probe failure class, and just-realized public summaries | classifies realized model progress, distinguishes stream-only churn from evidence progress, and feeds recent failures back into future routing/brake decisions | `cortex/sre/feedback.py`, `cortex/hosts/_executive_closure.py`, `cortex/hosts/runtime_context.py`, `cortex/hosts/openai/host_control.py`, `cortex/hosts/openai/runtime.py`, `cortex/hosts/claude_code_desktop/runtime.py`, `cortex/hosts/claude_code_desktop/hook_control.py`, `cortex/hosts/reference/runtime.py` | `tests/product/test_reference_feedback_window.py`, `tests/product/test_runtime_context_bridge.py`, `tests/product/test_runtime_context_eval_rubric.py`, `tests/product/test_openai_host_control.py`, `tests/product/test_openai_runtime_step.py`, `tests/conformance/test_claude_code_desktop_host_control.py`, `tests/conformance/integration/test_reference_runtime_cli.py` |
| `host_runtime_sessions` | multi-host executive continuity without flattening host differences | host-local runtime sessions for OpenAI, Claude, Gemini, and reference, including branch/goal state, budget/brake history, feedback windows, modulator memory, failure class, next recommended move, and preservation state | carries Cortex state across events and process boundaries, serializes only accepted control residue, and keeps host-native realization separate from shared law | `cortex/hosts/openai/runtime.py`, `cortex/hosts/claude/runtime.py`, `cortex/hosts/claude_code_desktop/runtime.py`, `cortex/hosts/gemini/runtime.py`, `cortex/hosts/reference/runtime.py` | `tests/product/test_openai_runtime_session_io.py`, `tests/conformance/test_claude_runtime_session_io.py`, `tests/conformance/test_claude_code_desktop_runtime_session_io.py`, `tests/conformance/test_gemini_runtime_session_io.py`, `tests/conformance/test_reference_runtime_session_io.py` |
| `host_control_transports` | model I/O boundary where Cortex can actually wrap a model | strict host-control request objects, text/system/instructions fields, optional offline publications, audit intensity, and transport results | coerces host-control requests, rejects out-of-scope keys, sends only host-legal request bodies, and updates session state from transport outputs | `cortex/hosts/openai/host_control.py`, `cortex/hosts/openai/host_transport.py`, `cortex/hosts/claude/host_control.py`, `cortex/hosts/claude/host_transport.py`, `cortex/hosts/claude_code_desktop/hook_control.py`, `cortex/hosts/gemini/host_control.py`, `cortex/hosts/gemini/host_transport.py` | `tests/product/test_openai_host_control.py`, `tests/conformance/test_claude_host_control.py`, `tests/conformance/test_claude_code_desktop_host_control.py`, `tests/conformance/test_gemini_host_control.py`, `tests/conformance/integration/test_openai_host_control_service.py` |

### Side B — Model-Visible Translation

| ID | Visibility class | Model I/O path | Reaches model as | Behavior effect | Gap / unearned claim |
| --- | --- | --- | --- | --- | --- |
| `event_dispatch_and_commitments` | `decision_visible` | `cortex/core/*` → host runtime step → CLI/service records and closure/route decisions; direct prompt text only when downstream host-control uses the decision | runtime decision state, warnings, and certification gates; not automatically prompt-visible by itself | can block, route, warn, or require closure before a model call proceeds through host control | Do not claim commitment diagnostics alone change model behavior unless a host-control path consumes them. |
| `goal_branch_continuity` | `decision_visible` | `cortex/sre/goals.py` + host runtime session → `operator_route.route_budget.allow_resume` / closure summaries → subsequent host-control selection | route and budget constraints, session continuity state, and closure pressure; not as raw memory text by default | keeps resume/closure decisions stable across events and can alter whether the next call is inspect, continuity, or blocked | Raw branch registry is not model-visible unless converted into host-control input or route behavior. |
| `brake_uncertainty_modulators` | `decision_visible` | `cortex/sre/brake.py` / `modulators.py` → executive policy view → operator route / activation thresholds → host runtime result | route pressure, threshold shifts, blocked/guarded decisions, and diagnostics; not natural-language self-talk | slows or blocks under contradiction and repeated failure, reducing unsupported forward motion before model output is requested | This is runtime control, not post-training reasoning improvement; live output-lift still requires model-run evidence. |
| `operator_routing_and_capability` | `decision_visible` | `select_operator_route*` → host runtime `operator_route_payload` → host-control route profile / verified-work contract binding | DEGRADE/UNSUPPORTED routing, max retry suppression, lean contract binding, or blocked request | changes whether and how the model is asked to act when model/task capability mismatch is detected | Static OpenAI-only band registry remains a cold-start prior; observed capability inference is queued, not landed. |
| `aux_support_publications` | `support_only` | AUX episode stores → `OfflineSupportPublication` → explicit publication supplied to host-control/runtime scoring | score-pricing priors and publication-only support; raw SQLite episodes do not reach the model | can bias control pricing when explicitly published, host-matched, and fresh; cannot directly route or certify | Default shipping/conformance lanes keep live `Q_mem = 0`; no default-on memory claim is earned. |
| `verified_work_preservation` | `direct_model_visible` | `OpenAIHostControlRequest(work_contract=...)` → fixed verified-work `instructions` + `input_text` → `execute_openai_response_stream_turn` | explicit model instructions, workspace context, repair prompt, and response verification loop on the OpenAI API host-control support lane | changes model call content and bounded repair behavior directly; preserves trusted structure across one-shot and repair attempts | OpenAI API host-control remains API/conformance support unless explicitly promoted; the active product target is `openai.codex_app_cli`. |
| `feedback_window_realization` | `conditional_model_visible_openai_and_claude_code_desktop_structural` | host output / last `ReferenceRealizationFeedback` → `runtime_context_from_last_feedback(...)` → OpenAI host-control `instructions` or verified-work `input_text`; Claude Code Desktop structural path maps prior feedback through `cortex/hosts/claude_code_desktop/runtime.py` to `hookSpecificOutput.additionalContext` for `PreToolUse:Bash` | a single task-local runtime-context constraint sentence derived only from the immediately prior feedback entry; clean or absent feedback emits no block/context | shapes the next OpenAI call and, structurally, the next Claude Code Desktop Bash-tool assistant continuation away from premature closure after stream-only, failed-probe, warning, override, or braked realization without accumulating memory across turns; generic friction now stays silent and relies on route/brake gates | OpenAI API host-control remains support/conformance; `openai.codex_app_cli` is the product target, and Claude Code Desktop still needs live paired output-quality evidence before shipping-lift claims. |
| `host_runtime_sessions` | `state_to_decision_visible` | host session artifact → runtime step → route/closure/policy payload → host control request, CLI/service response, or Claude Code Desktop hook-control output | carried state that influences later route and closure behavior; raw session JSON is not model input | maintains continuity across events and hosts without pretending all hosts expose the same transport affordances | Session state can be perfectly coherent internally while still failing to affect a model if no host-control path consumes it. |
| `host_control_transports` | `direct_model_visible` | `OpenAIHostControlRequest.input_text/instructions`, `ClaudeHostControlRequest.input_text/system`, `GeminiHostControlRequest.input_text/instructions`, and Claude Code Desktop `hookSpecificOutput.additionalContext` → respective live/fixture transport or hook outputs | provider request text/system/instructions or Claude Code Desktop hook additional context; metadata and audit intensity are boundary/control fields, not assumed model-visible text | this is the main bridge where Cortex can change what the model receives or what output is accepted | Any internal logic not consumed here, or not converted into route/block behavior before here, remains monitoring/scaffolding rather than product Cortex. |

### Synthesis — Gap / Boundary Decision

| ID | Boundary judgment | Decision | Next action | Post-training line |
| --- | --- | --- | --- | --- |
| `event_dispatch_and_commitments` | product Cortex when consumed by host runtime/host-control gates; monitor-only if left as CLI diagnostics | `bridge` | Keep commitment state as binding runtime law and require future commitment seams to name the host-control or route effect in closeout connectivity traces. | Do not try to retrain general truthfulness at runtime; Cortex should enforce event-local commitment handling and certification boundaries. |
| `goal_branch_continuity` | product Cortex when it changes resume/closure/route behavior; internal-only when it only serializes branch metadata | `bridge` | Audit future continuity seams against model-visible resume or closure behavior, not just preserved branch state. | General long-context memory quality is post-training; task-local lifecycle continuity after interruption is Cortex runtime territory. |
| `brake_uncertainty_modulators` | product Cortex as bounded runtime brake/route control, not a replacement for model calibration | `keep_runtime` | Keep proving that brake pressure changes route/block decisions and do not claim improved reasoning calibration without live evidence. | Global confidence calibration belongs in post-training; per-turn contradiction and failure brakes belong in lifecycle-first runtime. |
| `operator_routing_and_capability` | product Cortex because it changes route budgets and blockedness before the model call | `return_to_product_train` | Next product work should land observed capability inference so routing no longer depends only on static model-name prior. | Improving a model's inherent capability is post-training; detecting and routing around observed capability limits is Cortex. |
| `aux_support_publications` | support-side product adjunct only when publication-shaped; raw memory stores are not product Cortex | `keep_publication_only` | Keep AUX removable and publication-only; move any raw episode or default-on memory path back to lab/experimental or cut it. | Broad factual memory and preference learning are post-training/product-memory territory; explicit removable support priors are Cortex support geometry. |
| `verified_work_preservation` | Cortex-shaped API/conformance support on the OpenAI host-control lane because it directly changes instructions and repair loops, but not the active product target unless promoted | `freeze_support_until_promoted` | Keep the OpenAI API connector frozen as support/conformance while product work moves to `openai.codex_app_cli` hook-native lifecycle control. | Teaching a model to always preserve work is post-training; wrapping a concrete work contract and verifying repairs is Cortex runtime. |
| `feedback_window_realization` | Cortex-shaped on OpenAI API host-control support when last-step feedback is translated into bounded model-visible runtime context; structurally product-shaped on Claude Code Desktop `PreToolUse:Bash` when the same bounded context reaches hook additionalContext; still monitor-only if retained only as a public summary | `bridge_landed_openai_structural_claude_code_desktop_pretool_structural` | Keep the bridge last-feedback-only, extend Claude Code Desktop hook coverage one lifecycle event at a time, and run paired live baseline-vs-shaped evaluations before claiming output lift. | General learning from feedback is post-training; event-local realization feedback that alters the next runtime decision is Cortex. |
| `host_runtime_sessions` | necessary product substrate, but only earned when state is consumed by runtime decisions | `audit_consumption` | When adding session fields, add tests showing they survive serialization and change a route/closure/model-I/O decision, or mark them diagnostics. | Persistent personality or broad memory is post-training/product memory; host-local executive state for a task lifecycle is Cortex. |
| `host_control_transports` | the decisive product boundary where Cortex either reaches the model or does not | `protect_boundary` | Treat any future product claim as unearned until it names the exact request field or route/block consequence at this boundary. | Generic instruction-following lessons are post-training territory; encode only lifecycle-first control and verification signals that current host calls need. |
<!-- END GENERATED: v2-model-io-analysis -->

## 6. Implementation Discipline

This section is the project's standard of care. It is not a checklist; it
is the way work is done in this repo.

**Every Cortex change connects.** The first question to ask before
writing code in `cortex/**` is: what is the path from this change to
what the model receives or does? If you cannot name the files and the
host adapter and the output it touches, you do not yet have a Cortex
seam. You have an idea about Cortex. The closeout's `connectivity_trace`
field is the place that articulation lands; the empty-path-with-product-surface
case is the closed-loop drift error and is rejected.

**Fixtures falsify Cortex; they do not define Cortex.** Hard tasks witness a missing executive capability, not the capability itself. Product Cortex may use task details as grounded anchors, but never as product triggers; behavior keys on executive state such as unsupported claim, unpaid verification, unresolved obligation, continuity gap, blocker surfaced, capability mismatch, contradiction pressure, or preservation risk.
Task identity examples such as fixture IDs, file names, framework names, benchmark names, domain wording, and hidden verifier facts stay in `lab/**`, `tests/**`, recon docs, or the closeout `product_spine` fixture boundary. Product seams touching `cortex/**` preserve the spine: executive shape -> state law -> enforcement decision -> host action -> model I/O effect -> evidence.

**Model-visible text classes are distinct.** Human prompts are task requests; lab prompt scaffolds are test apparatus; host format contracts are mechanical protocols. Only Cortex model-visible communication must obey the strange-loop output law, and it must be generated from grounded runtime anchors rather than hand-written fixture prompts.

**The smallest seam that produces falsifiable product evidence is the
right seam.** Larger seams are bundling. Bundling is what loses work to
side-quest drift. Cut what does not improve the shipped executive layer
or directly unblock proving it.

**Cortex-specific, not generic bloat.** Every change should be an
expression of the executive functions named in §2. If a change feels
like it could live in any AI repo, it probably belongs in post-training
or in a generic apparatus, not in Cortex.

**One home, one proof.** Every load-bearing math object has exactly one
typed code home and at least one proof surface. The math-to-code map is
the ledger. New objects enter the ledger as part of the seam that
introduces them; old objects do not get split across files because that
is convenient — they get split because the math itself bifurcated, and
the bifurcation is named.

**Truthful answering.** When asked where Cortex is, lead with shipping
truth, conformance truth, the current train, and the active quality/risk
focus. Surface the executive-completion denominator only when the
question is explicitly about denominator accounting. The four-truth
distinction is a discipline, not a hedge.

**Live earn graduates the claim; structural earn lands the seam.** Do
not collapse the two. If a closeout asserts model-side lift without a
real model run, narrow the claim or run the evidence. The
postmortem-armed regex patterns reject closure phrasings that lack the
`agent_loop_guard` payload that proves the run.

**The hygiene apparatus is not Cortex.** The workflow helper, the
closeout contract, the reflection grid, the agent briefing — these
shape the agents working in this repo, not the model that Cortex
eventually wraps. They are doctrine, not product. They live under
`internal/**` (and surfaces that AGENTS.md owns) and they may not be
imported by `cortex/**`. Confusing the two is the next drift shape.

**Per-turn enforcement: Cortex Mission Reflection.** End-of-turn
reflection is produced by `python3 internal/workflow/repo_workflow.py
grid --mode <exploration|work|closeout>`. The mode-aware contract lives
in `docs/internal/MISSION_REFLECTION_CONTRACT.md` and is implemented by
`internal/workflow/mission_reflection.py`. Its purpose is mission
reflection, not static progress recitation, and it must not shape the
substantive answer. Exploration mode is intentionally small for
research-shaped turns; work mode preserves ordinary implementation
discipline; closeout mode keeps the strict legacy grid with compact
closure metadata for managed session closure. On `reflection-check`
verdict `FAIL`, the agent continues working until the graph clears.

**Workflow: paste the skeleton, fill brackets in place.** The agent runs
`grid --mode <mode>`, pastes the generated markdown skeleton, and edits
the skeleton in place. Exploration mode requires a smaller grounded
reflection, work mode requires broader mission/evidence reflection with
at least three repo-grounded rows, and closeout mode requires every
mission/reflection/evidence/decision row to be cited and at least 120
characters. No separate closure section follows the grid.

**Chat-boundary enforcement (Claude Code; Codex App fallback).** A Stop hook at
`.claude/settings.json` runs `.claude/hooks/cortex_grid_stop_hook.py` on
turn-completion. The hook reads the assistant's last message from the
transcript, infers graph mode from the row set, runs the matching
`grid --mode <mode>` command for corrective output, and blocks on
missing/underfit graph output. The hook still rejects stale dashboard
rows, closure-shaped substrings before the graph, unfilled templates,
under-length rows, missing citations required by the selected mode, and
`reflection-check` verdict `FAIL`. The hook does not short-circuit on
`stop_hook_active`; persistent non-compliance keeps blocking. The hook
fails open only on infrastructure failures (missing transcript, command
crash). The hook and `grid-validate` both use
`internal/workflow/mission_reflection.py` as the shared graph contract.

Codex App for Mac has a repo-local Stop hook script because Codex exposes
`last_assistant_message` directly rather than a Claude transcript path, but
root `.codex/config.toml` now disables Codex hooks with
`[features].codex_hooks = false`. The script remains available for direct
structural validation; `codex-app-hook-health` verifies the disabled config
policy plus known-bad and valid direct script payload behavior. Current Codex
App chats use explicit `grid-validate` fallback so Stop repair loops do not
hide substantive answer content before the final graph.

**Codex fallback surfaces.** Codex surfaces that do not load repo-local hooks,
including the current root Codex App config, fall back to validator + doctrine:
the agent runs
`python3 internal/workflow/repo_workflow.py grid-validate --mode <mode>`
on the filled final graph, and non-no-op Codex closeouts record that pass
in `mission_reflection_graph`. This is session-boundary evidence, not
chat-boundary parity.

**Runtime-context bridge evaluation.** The feedback-window runtime
context bridge has three pre-live eval artifacts under
`docs/runtime_context/`: `EVAL_RUBRIC.md` operationalizes the
baseline-vs-shaped scoring axes, `BASELINE_SHAPED_EXAMPLES.md` records
the win/loss/neutral worked examples, and `CROSS_HOST_SKETCH.md` pins
the Claude/Gemini placement sketch. These documents are eval artifacts,
not mission authority; use them to judge whether the runtime-context
constraint sentence earns model-visible output lift before making live claims.

**Lifecycle-first surface reconnaissance.**
`docs/recon/lifecycle_first_surface_matrix.md` maps the current
OpenAI / Anthropic / Google API, CLI, and Mac app extension surfaces
against Cortex's lifecycle-first needs. It is a sourced recon artifact,
not mission authority and not an architecture plan. Use it before making
surface-selection claims so API control, CLI/app hooks, MCP support, and
consumer-app gaps are not flattened into fake portability.
`docs/recon/codex_app_hook_probe.md` is the paired empirical Codex App
finding from an earlier trusted-hook configuration: on the tested Mac app
version, a project Stop hook loaded, fired, exposed `last_assistant_message`,
and routed a `decision: "block"` reason into the model-visible continuation.
That finding remains recon evidence only; current root config disables the
repo Mission Reflection Stop hook by policy.
`docs/recon/claude_code_desktop_pretooluse_probe.md` is the paired empirical
Claude Code Desktop Code-tab finding: on the tested Mac app version,
`PreToolUse` fired for Bash in the effective Claude-managed worktree and
`hookSpecificOutput.additionalContext` reached the next model-visible
assistant response. That finding is specific to Claude Code Desktop's Code tab,
the Bash matcher, and `PreToolUse`; it must not be generalized to Claude Code
CLI, Claude Desktop chat, other hook events, or product Cortex model-output
lift.
`docs/recon/claude_code_user_scope_plugin_pretooluse_probe.md` is the paired
user-scope plugin finding: on the tested Mac app version, a user-scope plugin
fired `PreToolUse:Bash` from `/Users/erikahoward/cortex-loop`, fired `Stop`
from the same plugin, and showed that repeated `additionalContext`
acknowledgement instructions can interact badly with a separate Stop validator.
That finding does not prove user-scope plugin behavior inside a
`.claude/worktrees/...` managed-worktree cwd and does not earn product Cortex
model-output lift.
`docs/recon/claude_code_user_scope_plugin_managed_worktree_probe.md` is the
follow-up sandbox finding: a user-scope plugin fired `PreToolUse:Bash` in
`/Users/erikahoward/cortex-plugin-sandbox`, a project with no repo-local
`.claude/settings.json`, and the hook `cwd` was the sandbox root rather than
a `.claude/worktrees/...` path. That finding supports user-scope plugin reach
for normal project-root Code-tab sessions but still does not prove an actual
managed-worktree cwd case or product Cortex model-output lift.
`docs/recon/claude_code_cortex_runtime_context_connectivity_probe.md` is the
paired runtime-context finding: the merged Claude Code Desktop `PreToolUse:Bash`
adapter did emit the legacy `CORTEX_RUNTIME_CONTEXT_V1` schema into transcript
`hook_additional_context`, and Stop `decision: "block"` reason text reached the
continuation context, but Gate 1 failed because shaped behavior was mixed
(one win, one no-change, one regression, one neutral). That finding blocks
the parked lifecycle-spine branch from merge until the model-visible runtime
context is revised and revalidated.
`docs/recon/claude_code_cortex_stop_closure_connectivity_probe.md` is the
paired Stop closure-pressure finding: Cortex-derived `closure_reason_tags`
returned through a `Stop` `decision: "block"` reason reached Claude Code
Desktop as `Stop hook feedback:` and materially changed closure behavior in
three non-clean trials, while clean and verified-artifact controls did not
block. That finding validates the `Stop x closure pressure` cell only; it does
not demote `PreToolUse`, prove a Stop-primary architecture, or earn broad
product output lift.
`docs/recon/claude_code_cortex_headless_cli_equivalence_probe.md` is the
headless CLI equivalence finding for the same Stop bridge: `claude -p` fired
Stop, surfaced `Stop hook feedback:` plus `hook_blocking_error`, matched the
Mac app evidence-degradation repair and clean no-over-block control, but
diverged on pending-goal because headless refused the false closure in baseline
and treated the shaped Cortex hook framing skeptically. That finding supports
lower-cost Stop-specific iteration in headless mode with Mac app validation
reserved for final behavior claims.
`docs/recon/claude_code_cortex_bridge_translation_headless_probe.md` preserves
the later headless translated-Stop evidence from the retired renderer-first
branch: isolated `claude -p` runs confirmed plugin-layout and global-hook
setup constraints, translated evidence-degradation Stop repaired 3/3 scored
headless false-closure trials, pending-goal remained unscored because headless
baseline refused the false claim, and the finding stays scoped to translated
`Stop x closure pressure` evidence rather than shipping truth or broad hook
parity.
`docs/recon/claude_code_cortex_mac_pending_goal_divergence_retest.md` is the
Mac app retest of that pending-goal divergence: two fresh baselines reproduced
false `MIGRATION COMPLETE` closure, but raw internal Stop wording repaired only
one of two shaped trials and caused hook-skepticism in the other. That finding
does not invalidate the Stop lifecycle surface; it proves that internal Cortex
tags must be translated into plain task facts before model-visible enforcement.
`docs/recon/claude_code_cortex_posttool_failure_to_stop_loop_probe.md` is the
paired PostToolUseFailure-to-Stop finding: failed Bash results fired
`PostToolUseFailure`, persisted bounded `ReferenceRealizationFeedback`, and
later Stop hooks read that state; shaped Stop repair improved two of three
failure pairs while one shaped pair repeated false closure. That finding earns
hook delivery and persistence, but only mixed behavior lift for the feedback
to closure loop.
`docs/recon/claude_code_cortex_userpromptsubmit_verified_work_probe.md` is the
paired UserPromptSubmit verified-work finding: a short situated
`systemMessage` reached Claude Code Desktop transcripts as `hook_system_message`
before the assistant Bash call, `PostToolUseFailure` fired for the missing-file
result, and the assistant still emitted false `TASK COMPLETE` in both shaped
failure pairs. That finding validates hook and transcript-boundary delivery
for this event but does not earn behavior lift for the tested content shape.
`docs/recon/cortex_openai_operator_silent_control_live_probe.md` is the OpenAI
operator silent-control Gate 0 finding: deterministic replay showed that
runtime debt control changes OpenAI route/policy diagnostics, but the current
Codex operator adapter does not enact those diagnostics before invoking the
model. No live operator trials ran, no behavior-lift claim was earned, and the
remediation path had to connect debt-control outputs to model-bound operator
invocation or continuation policy before retrying the paired probe.
`docs/recon/cortex_openai_operator_debt_control_enactment.md` is the OpenAI
operator enactment remediation finding: the host adapter now consumes SRE
route/policy/debt payloads and produces prompt-independent operator actions,
with shaped truth-gap debt producing `resume_recheck` while neutral stays a
single `invoke`. That closes the Gate 0 coupling gap structurally, but it is
still not live behavior-lift evidence or a shipping promotion.
`docs/recon/cortex_openai_operator_silent_control_live_probe_retry.md` is the
first retry after enactment remediation: Gate 0 still passed, but the accepted
`gpt-5.3-codex` baseline gate did not reproduce the target unsupported
verification, false-closure, or candidate-forward-commit failures, so the
paired shaped matrix did not run and no silent-control behavior lift was
earned.
`docs/recon/cortex_openai_operator_output_quality_fixture_refresh.md` is the
fixture-refresh finding: output-quality operator workspaces now initialize as
isolated Git roots so Codex CLI does not inherit this repo's agent contract,
and `astro_docs_site_v1` reproduces the harder visible-success /
hidden-verification failure shape in clean raw OpenAI operator runs. The
existing output-quality `cortex` arm can repair it once through visible
contract machinery, but that is not silent-control behavior-lift evidence.
`docs/cortex_plugin/DESIGN.md` is the v1 Claude Code Desktop Cortex plugin
design: it maps Claude Code Desktop lifecycle hooks onto the eight Cortex
failure modes, keeps the Mission Reflection grid out of product packaging,
and records the claim boundary that design/build can structurally establish
Claude Code Desktop as a Cortex surface while live output-lift still requires
paired evaluation evidence.
`docs/cortex_plugin/ADAPTER.md` records the first build-phase refinement:
Claude Code Desktop is represented as a Cortex host adapter under
`cortex/hosts/claude_code_desktop/`, while plugin scripts remain transport
wire. It is structural adapter evidence only and does not promote Claude Code
Desktop to shipping default or claim live output lift.
`docs/cortex_plugin/EVIDENCE_SYNTHESIS.md` is the post-recon accounting
surface for the Claude Code Desktop plugin effort: it separates hook delivery,
model-visible delivery, behavior-lift, and shipping truth before any further
plugin build or empirical probe work.

**No-mimicry rule.** Composing markdown that resembles grid content
but is not actual `grid` command output is a violation. Ad-hoc
audit-shaped markdown headers (e.g. an "Audit Findings" block, a
separate metadata block following the grid, or a handoff mirror written
from scratch) do not satisfy the contract because they bypass the
consolidated single-closure structure. This rule exists because in
practice, agents that run inspection commands and compose their own
closure-shaped markdown are a documented bypass pattern.

**Connectivity-trace closeout field.** Load-bearing seams that touch
`cortex/**` must populate `connectivity_trace = {claim, path[],
if_empty_why}` on the closeout contract. An empty `path` on a
`product` surface is the closed-loop drift error and is rejected at
validation. Surface `experimental` or `lab` is allowed to have an empty
path, but `if_empty_why` must explain why monitoring or instrumentation
is the correct framing rather than Cortex.

**Form positions from doctrine and code, not from the latest framing.**
This is the agent briefing made operational. If you are about to take a
position on what Cortex should do and you cannot cite the surface that
backs it, you do not have that position yet. Read until you do, or hold
the question.

## 7. How to Use This Document

Read this file at the start of every session, after `AGENTS.md` and
before `docs/CORTEX_STATUS.md`. The order is:

1. `AGENTS.md` — the agent contract: briefing, mission, authority,
   non-negotiables, working mode, workflow, anti-drift.
2. `docs/CORTEX.md` (this file) — what Cortex is, where it came from,
   where it is going.
3. `docs/CORTEX_STATUS.md` — generated current operational truth.
4. `git branch --show-current` and `git status --short --untracked-files=all`
   — local state.

If a change feels off-mission while you are mid-implementation, return
here. Specifically:

- §1 if you are unsure whether the work is Cortex or post-training or
  apparatus.
- §2 if you are unsure which executive function the work serves.
- §3 if you are tempted to soften lifecycle-first, microkernel
  separation, claim-conservative AUX, connectivity, truth distinctions,
  or postmortem-armed closeout — re-read why each one exists.
- §4 if you are touching a load-bearing math object — confirm or update
  its entry.
- §5 for current state without re-reading the registry.
- §6 if you are mid-design and unsure about the standard of care.

The V2 packet documents (`docs/CORTEX_V2_*.md`) win on math and legal
questions. This document wins on "is this the right move at all." The
status registry wins on current-state questions. Conflicts resolve by
which dimension the question is in; this document does not authorize
breaking packet law or current-state truth.

This document is updated when learnings warrant. Routine state changes flow through registry regeneration; narrative changes require a load-bearing lesson.
