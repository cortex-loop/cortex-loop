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

- Slug: `brain-capability-aware-routing`

### Next Product Train

- Slug: `brain-capability-observation-and-inference`
- Surface: `product + experimental + aux`
- Why now: The static registry maps known model names to bands but cold-starts to standard for unknown models and never updates as a model's actual behavior drifts. An observed-performance accumulator (mirroring how `HostReliabilityPrior` works for host-tool reliability) lets the executive learn capability rather than assume it, and lets new model variants be detected automatically without registry edits.

### Research Lines Under Evaluation

- _none_

### Hosts and Shipping Defaults

- `openai` — conformant; shipping `default`; surface `operator_cli`
- `claude` — conformant; shipping `non-default`; surface `operator_cli`
- `gemini` — conformant; shipping `non-default`; surface `operator_cli`
- `reference` — conformant; shipping `non-product`; surface `reference_cli`

- Shipping default lane: `openai:operator_cli`
- Accepted next conformance decision: `promote`

### Active Leverage and Where to Work

- Keep the bounded audit surface compact and truthful on the shipped lane: selected versus realized family, uncertainty, threshold, delta, verification, and probe truth only.
- Keep the no-spend live evidence current and explicit: fast conformance is green, the deeper directionality and host-native watchlists are refreshed, and non-shipping auth or env caveats must stay explicit instead of silently stale.
- Keep posture, AUX memory, host-reliability, and asymmetric-cost law explicit and removable now that posture-sensitive online control is S-tier closed, anti-thrash is landed, bounded live support-memory re-entry is earned on reference and the OpenAI operator lane, evidence/probe calibration is S-tier closed, host/tool reliability and affordance priors are earned as bounded host-scoped, capability-scoped score modifiers on `OfflineSupportPublication.host_reliability_prior` with a single-site six-tag `q_mem-host:*` surface and stale-negative reopen under fresh success, asymmetric error cost is earned as a bounded `RiskWeight` carrier whose CHECK/SEEK_CONTEXT activation shift is clipped inside `[0.05, 0.60]` with a `0.10` dead-band and productive-exploration gating, and the brake tonic EMA damps single-tick flips with a locked `rho = 0.60` decay and `tonic_pressure >= 0.35` enter gate while phasic spikes still flip immediately: inspect is live on cheap non-debt events, resume stays continuity-conditioned, posture truth is single-owned, the route state vector stays the bounded 6-axis geometry term while `visible_burden_sensitivity` remains a separate utility scalar, route truth stays bounded and non-sovereign, unchanged-condition repetition is taxed only at the exact-family level with bounded reopen, public feedback-window summaries reflect the just-realized step, family-local bounded probe limits surface as `unsupported` without leaking host-global unavailability across families, stream-only churn stays non-epistemic, live memory stays score-only and host-matched through explicit publication, live `Q_mem` stays zero on shipping and conformance default lanes, raw SQLite episodes stay support-side only, reliability priors bias score pricing only and never route, posture, selection, or brake law, Claude and Gemini remain shadow-proof only for reliability promotion, `risk_weight` biases CHECK/SEEK_CONTEXT activation threshold only and never routing, posture, selection, certification, or blockedness law, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes with three-way backward-compat decoding.
- The brain-capability-aware-routing seam is the active focus per SRE_2 §6.9: the executive carries an `OperatorBrainCapabilityEnvelope` and a bounded threshold ladder classifies the per-dimension max mismatch into NONE / DEGRADE / UNSUPPORTED at 0.20 / 0.50; DEGRADE downshifts continuity-bearing profiles to inspect-light, suppresses retries, and switches contract binding to LEAN, while UNSUPPORTED routes to BLOCKED with `brain_capability_mismatch`. The mechanism is host-agnostic at the SRE layer; the band registry is OpenAI-only and other hosts default to standard until per-host registries earn their own seam. The brake-tonic-quiescence-exit-reconciliation seam (closed via SRE_2 §7.5 path B) is no longer active; doctrine and code agree on threshold-hysteresis-only on the brake exit gate, and the locked `rho = 0.60` EMA regression is preserved.
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
| **Codex App repo lifecycle adapter** | Stop hook receives `last_assistant_message` directly; project-local hooks require trusted `.codex/` config and `[features].codex_hooks = true`. | `.codex/config.toml` runs `.codex/hooks/cortex_mission_reflection_stop_hook.py`; `decision: block` asks Codex App to continue with corrective context; `codex-app-hook-health` proves structural config/script behavior, not live model-side product lift. | `.codex/config.toml`, `.codex/hooks/cortex_mission_reflection_stop_hook.py`, `tests/internal/test_codex_app_stop_hook.py` |

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
| `verified_work_preservation` | `direct_model_visible` | `OpenAIHostControlRequest(work_contract=...)` → fixed verified-work `instructions` + `input_text` → `execute_openai_response_stream_turn` | explicit model instructions, workspace context, repair prompt, and response verification loop on the OpenAI host-control lane | changes model call content and bounded repair behavior directly; preserves trusted structure across one-shot and repair attempts | Strongest direct path is OpenAI shipping lane; Claude/Gemini parity is conformance-shaped and must not be overclaimed as default shipping. |
| `feedback_window_realization` | `conditional_model_visible_openai_and_claude_code_desktop_structural` | host output / last `ReferenceRealizationFeedback` → `runtime_context_from_last_feedback(...)` → OpenAI host-control `instructions` or verified-work `input_text`; Claude Code Desktop structural path maps prior feedback through `cortex/hosts/claude_code_desktop/runtime.py` to `hookSpecificOutput.additionalContext` for `PreToolUse:Bash` | bounded `CORTEX_RUNTIME_CONTEXT_V1` text derived only from the immediately prior feedback entry; clean or absent feedback emits no block/context | shapes the next OpenAI call and, structurally, the next Claude Code Desktop Bash-tool assistant continuation away from premature closure after stream-only, failed-probe, warning, friction, override, or braked realization without accumulating memory across turns | OpenAI remains the direct shipping lane; Claude Code Desktop is structurally wired for `PreToolUse:Bash` only and still needs live paired output-quality evidence before shipping-lift claims. |
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
| `verified_work_preservation` | product Cortex on OpenAI host-control lane because it directly changes instructions and repair loops | `keep_and_prove_live` | Keep the OpenAI direct path as shipping truth; only graduate cross-host lift claims after equivalent host-control proof exists. | Teaching a model to always preserve work is post-training; wrapping a concrete work contract and verifying repairs is Cortex runtime. |
| `feedback_window_realization` | product Cortex on the OpenAI host-control lane when last-step feedback is translated into bounded model-visible runtime context; structurally product-shaped on Claude Code Desktop `PreToolUse:Bash` when the same bounded context reaches hook additionalContext; still monitor-only if retained only as a public summary | `bridge_landed_openai_structural_claude_code_desktop_pretool_structural` | Keep the bridge last-feedback-only, extend Claude Code Desktop hook coverage one lifecycle event at a time, and run paired live baseline-vs-shaped evaluations before claiming output lift. | General learning from feedback is post-training; event-local realization feedback that alters the next runtime decision is Cortex. |
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

**Per-turn enforcement: Cortex Mission Reflection.** The standard of
care is enforced end-of-turn by the graph produced by
`python3 internal/workflow/repo_workflow.py grid`. The command name
stays `grid` for workflow compatibility, but the rendered artifact is
the **single closure artifact** for every chat: one two-column markdown
table under `## Cortex Mission Reflection`. Its purpose is not to recite
static progress. It forces mission reflection: target executive
function, boundary judgment, theory of improvement, model I/O path,
plan-vs-actual reflection, quality judgment, iteration evidence,
earned/not-earned evidence, next ownership move, compact closure
metadata, and verdict. There are no subsection headings and no second
table inside the grid. Normal response prose may precede the grid;
nothing closure-shaped may appear before or after it. On verdict
`FAIL` the agent continues working until the graph clears. The verdict
cell separates turn verdict from close-session eligibility so a clean
no-closeout turn cannot imply it is publish-ready.

**Workflow: paste the skeleton, fill brackets in place.** The agent
runs `grid`, pastes the generated markdown skeleton, and edits the
skeleton in place. Every mission/reflection/evidence/decision row
replaces the `mission reflection —` template with substantive causal
prose (at least 120 characters) and a repo-grounding citation such as
`docs/CORTEX.md`, `internal/truth/cortex_status.json`, `cortex/**`,
`tests/**`, or a `CORTEX_V2_*` packet. The `Closure: Metadata` row
replaces the `closure metadata —` template with branch, commit/no
commit, verification, returned-to-main, and registry/doc-regeneration
facts. The skeleton is verbatim from the command; the agent's edits
stay inside the skeleton. No separate closure section follows the grid.

**Chat-boundary enforcement (Claude Code and Codex App).** A Stop hook at
`.claude/settings.json` runs
`.claude/hooks/cortex_grid_stop_hook.py` on turn-completion. The hook
reads the assistant's last message from the transcript, runs `grid`
itself, and blocks the stop on (1) missing one-table shape
(`## Cortex Mission Reflection`, exactly one `| Field | Value |`
header, exactly one `|---|---|` separator, required row labels, and
no `###` subsections inside the grid), (2) closure-shaped substrings
appearing before the grid header, (3) stale dashboard rows such as
`Progress:*`, `bio_to_code matrix`, hosts, shipping default, current
train, next train, or research-lines counts as fixed rows, (4) any
mission-reflection row that is templated, too short, or uncited, (5)
unfilled `Closure: Metadata`, or (6) `reflection-check` verdict
`FAIL`. The hook does not short-circuit on `stop_hook_active` —
persistent non-compliance keeps blocking. The hook fails open only on
infrastructure failures (missing transcript, command crash). The hook
and `grid-validate` both use `internal/workflow/mission_reflection.py`
as the shared graph contract, so Claude and Codex are validating the
same rows and thresholds.

Codex App for Mac has its own repo-local Stop hook because Codex exposes
`last_assistant_message` directly rather than a Claude transcript path:
`.codex/config.toml` enables `[features].codex_hooks = true`, and
`.codex/hooks/cortex_mission_reflection_stop_hook.py` applies the same
shared validator. Per the official Codex hook lifecycle, project-local
hooks load only when the project `.codex/` layer is trusted.
`codex-app-hook-health` simulates known-bad and valid Codex Stop
payloads; if it fails, product work in Codex App must stop until the
hook/config/runtime issue is fixed. This is structural lifecycle
evidence, not live evidence that Cortex improved model output.

**Codex fallback surfaces.** Codex surfaces that do not load repo-local
hooks fall back to validator + doctrine: the agent runs
`python3 internal/workflow/repo_workflow.py grid-validate --stdin` on
the filled final graph, and non-no-op Codex closeouts record that pass
in `mission_reflection_graph`. This is session-boundary evidence, not
chat-boundary parity.

**Runtime-context bridge evaluation.** The feedback-window runtime
context bridge has three pre-live eval artifacts under
`docs/runtime_context/`: `EVAL_RUBRIC.md` operationalizes the
baseline-vs-shaped scoring axes, `BASELINE_SHAPED_EXAMPLES.md` records
the win/loss/neutral worked examples, and `CROSS_HOST_SKETCH.md` pins
the Claude/Gemini placement sketch. These documents are eval artifacts,
not mission authority; use them to judge whether `CORTEX_RUNTIME_CONTEXT_V1`
earns model-visible output lift before making live claims.

**Lifecycle-first surface reconnaissance.**
`docs/recon/lifecycle_first_surface_matrix.md` maps the current
OpenAI / Anthropic / Google API, CLI, and Mac app extension surfaces
against Cortex's lifecycle-first needs. It is a sourced recon artifact,
not mission authority and not an architecture plan. Use it before making
surface-selection claims so API control, CLI/app hooks, MCP support, and
consumer-app gaps are not flattened into fake portability.
`docs/recon/codex_app_hook_probe.md` is the paired empirical Codex App
finding: on the tested Mac app version, a trusted project Stop hook loaded,
fired, exposed `last_assistant_message`, and routed a `decision: "block"`
reason into the model-visible continuation. That finding is Codex App only
and must not be generalized to other surfaces without their own probes.
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
3. `docs/CORTEX_STATUS.md` — the generated human view of current
   operational truth.
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

This document is updated when learnings warrant. Routine state changes
flow through the registry and regenerate sections §2, §4, §5
automatically. Narrative sections (§1, §3, §6, §7) are updated when a
session produces a load-bearing lesson; the closeout's
`lesson_for_cortex_doc` field is the candidate-marker for that.
