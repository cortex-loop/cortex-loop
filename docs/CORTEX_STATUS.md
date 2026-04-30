# CORTEX Status

Surface: product

_Generated from `internal/truth/cortex_status.json`. Edit the registry, then run `python3 internal/truth/generate_status.py`._

## Resting State

- Branch: `main`
- Rule: Clean synced main is the only resting state; the richer Cortex executive remains the product goal, and archive or lab surfaces do not define live product truth.

## Bootstrap

- `AGENTS.md`
- `docs/CORTEX.md`
- `docs/CORTEX_STATUS.md`
- `git branch --show-current`
- `git status --short --untracked-files=all`

## Goal

**Rich Executive For AI**

Cortex should be a richer multi-host executive layer for AI work: lifecycle-first, verification-aware, continuity-preserving, and capable of bounded correction without collapsing into host-specific hacks.

Not product:
- `diagnostics`
- `train loops`
- `graders`
- `workflow ledgers`
- `governance records`

## Identity And Research Stance

Cortex is the installable executive layer that wraps a model or host surface and adds executive function to the underlying brain without redefining the brain itself as the product.

Research stance:
- Steal executive skills from systems that already work, especially human executive function, then translate them into small lawful operators, state, gates, and proof surfaces.
- Use first-principles reasoning and live evidence together: start from packet law, then challenge or revise that law explicitly when repeated runtime evidence disproves it.
- Prefer brilliant concrete code when it cleanly realizes the intended executive skill; do not preserve a worse abstraction just because it matched an earlier local framing.

Answering stance:
- When describing Cortex, lead with shipping truth, conformance truth, the current train, and the active quality/risk focus. Surface the executive-completion denominator only on explicit denominator or progress-accounting questions.
- Always distinguish Cortex truth, shipping truth, conformance truth, and the current train.

## Live Product Truth

- Shipping default: `openai:operator_cli`
- Conformance truth: `openai=conformant`, `claude=conformant`, `gemini=conformant`, `reference=conformant`
- Accepted conformance next decision: `promote`

## Current Focus

- Current tracked train: `brain-capability-aware-routing`
- Active quality/risk focus: The bounded AUX shadow surface still earns `full_cross_host`, durable support-memory distillation remains explicit and removable, posture-sensitive online control is S-tier closed on the live runtime path, anti-thrash remains an exact-family unchanged-condition repetition tax with bounded reopen, bounded live support-memory re-entry is S-tier closed on both the reference and OpenAI explicit-publication lanes with host-match, family-scoped invalidation, transcript-only raw `/v1/events`, locked `memory_reentry` diagnostics, shared conformance parity, and explicit proof that runtime use stays publication-only without AUX persistence or distillation, evidence-progress/probe calibration is S-tier closed with typed evidence-progress and continuity-progress classification across all four hosts, public `feedback_window_summary` reflecting the just-realized step, real probe success distinguished from family-local bounded unsupported surfaces, and stream-only churn stays visible but non-epistemic, bounded host/tool reliability and affordance priors are earned on the reference and OpenAI explicit-publication live lanes as explicit, offline-distilled, capability-scoped score modifiers carried on `OfflineSupportPublication.host_reliability_prior` with a single-site six-tag `q_mem-host:*` surface, stale-negative reopen under fresh success, locked `memory_reentry.selected_family_reliability_delta` diagnostics, and Claude/Gemini kept shadow-proof only, and asymmetric error cost and tonic hysteresis are now earned on the shared executive as bounded score-pricing carriers: `RiskWeight(fn_cost_weight, fp_cost_weight, dominant_risk_source, adjustment_sign)` derives from pending-goal depth, degradation, contradiction, budget band, productive-exploration confirmation, and published host-reliability evidence with a `0.10` dead-band and fp-signal gated on `productive_exploration_bonus > 0.0` so cold starts stay balanced, the asymmetric activation shift `(fp - fn) * 0.10` applies to CHECK and SEEK_CONTEXT only and is clipped inside `[0.05, 0.60]`, the brake tonic EMA damps single-tick flips with a locked `rho = 0.60` decay and `tonic_pressure >= 0.35` enter gate while phasic contradiction, latching, missing-anchor, and repeated-failure signals still flip immediately, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes with three-way backward-compat decoding. The brake-tonic-quiescence-exit-reconciliation train is closed via SRE_2 §7.5 path B: the doctrine is narrowed to threshold-hysteresis-only on the brake exit gate, and the rest-side EMA `tonic_quiescence` is retired from the BrakeTonic carrier, the SRE allocation diagnostics, and the host runtime serialization on all four host lanes (OpenAI, Claude, Gemini, reference); kill-rule-e remains green and no new memory carrier or host-specific exit policy fork was introduced. Brain-capability-aware routing is now earned as the active focus per SRE_2 §6.9: the executive carries an `OperatorBrainCapabilityEnvelope(continuity_tolerance, verification_tolerance, output_contract_tolerance)` and a bounded threshold ladder classifies the per-dimension max mismatch into NONE / DEGRADE / UNSUPPORTED; DEGRADE downshifts continuity-bearing profiles to inspect-light, zeroes max_retries and allow_extra_read_pass, and switches the contract binding profile to LEAN, while UNSUPPORTED routes to BLOCKED with `blocked_reason=brain_capability_mismatch`; the band registry is OpenAI-only at this landing and other hosts default to the standard envelope until per-host registries earn their own seam. The next product train is dynamic brain-capability inference from observed `ReferenceRealizationFeedback`: an observed-performance accumulator that publishes through AUX support side rather than mutating routing directly, replacing the static name-lookup with an evidence-backed envelope while keeping the same SRE assessment and routing math. Shipping and conformance default lanes still keep `Q_mem = 0`, default shipping behavior remains memory-off when no publication is supplied, live memory remains publication-only and score-only, raw SQLite episodes remain support-side only, route blockedness remains non-sovereign, reliability priors bias score pricing only and never harden into host myths or hidden policy forks, and risk_weight biases CHECK/SEEK_CONTEXT activation threshold only — never routing, posture, selection, certification, or blockedness law.
- Next product train after the current focus: `brain-capability-observation-and-inference`

## Bio-To-Code Matrix

| Executive Skill | What We Are Stealing | Status | Weight | Code Homes | Proof Surfaces | Next Move |
| --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | Truth maintenance and reality binding | `landed` | `12` | `cortex/core`, `cortex/drivers` | `tests/product`, `tests/conformance` | Keep this foundation stable while richer executive control builds on top. |
| Bounded correction and verified-work preservation | Error repair without losing the main task thread | `landed` | `15` | `cortex/runtime`, `cortex/sre`, `cortex/hosts/openai` | `tests/product` | Keep preservation-state repair stable while support-side experiments stay removable and off the shipping critical path. |
| Uncertainty handling and brake | Hesitation and uncertainty-aware inhibition | `landed` | `13` | `cortex/sre` | `tests/product`, `tests/experimental` | Keep reference-derived brake and uncertainty control stable while AUX remains advisory and runtime-off-by-default. |
| Branch continuity, suspend/resume, and truthful closure | Working memory across interruptions plus truthful closure | `landed` | `15` | `cortex/sre`, `cortex/hosts/openai` | `tests/product`, `tests/conformance` | Keep suspend/resume and truthful closure stable now that host-local branch continuity is repaired across Claude, Gemini, and reference; branch-local continuity may reopen only from branch-linked cues, and any future support memory must remain explicit, optional, and non-binding. |
| Intervention pricing versus neutrality | Deciding when to intervene, stay neutral, or stop | `landed` | `10` | `cortex/sre`, `cortex/aux`, `cortex/runtime` | `tests/product`, `tests/experimental`, `tests/conformance` | Hold calibrated intervention pricing stable now that posture-sensitive online control is S-tier closed, anti-thrash is landed on the live runtime path, and brain-capability-aware routing is earned as a host-agnostic SRE mechanism: the executive carries an `OperatorBrainCapabilityEnvelope` (continuity_tolerance, verification_tolerance, output_contract_tolerance) that drives a bounded threshold ladder (NONE / DEGRADE / UNSUPPORTED at 0.20 / 0.50 mismatch), where DEGRADE downshifts continuity profiles to inspect-light, suppresses retries, and switches contract binding to LEAN, and UNSUPPORTED routes to BLOCKED with `brain_capability_mismatch`; the per-host band registry is OpenAI-only at landing time and other hosts default to standard until per-host registries earn their own seam, and any future capability inference from observed `ReferenceRealizationFeedback` must publish through AUX support side rather than mutate routing directly. |
| Blocker surfacing and goal-debt management | Noticing unresolved blockers and unfinished intentions | `landed` | `10` | `cortex/sre`, `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Keep typed goal-debt and closure-pressure state stable across hosts while support-side augmentation remains explicit and non-sovereign. |
| Multi-host executive continuity | One executive across different brains and contexts | `landed` | `15` | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Hold one Cortex law across OpenAI, Claude, Gemini, and reference without flattening host-native realization. |
| Offline consolidation and support geometry | Sleep-like consolidation and support systems | `landed` | `10` | `cortex/aux` | `tests/experimental`, `tests/archive`, `tests/conformance` | Keep durable support-memory distillation explicit, removable, and non-sovereign now that reference and OpenAI both earn explicit publication-shaped live re-entry with host-match, family-scoped invalidation, publication-only runtime-boundary proof, S-tier evidence/probe calibration, bounded host/tool reliability and affordance priors that bias control pricing through host-scoped, capability-scoped score modifiers only, decay under fresh success, and never harden into host-wide superstition, cross-host projected reuse, or default-on memory, and asymmetric error cost and tonic hysteresis are earned on the shared executive so CHECK and SEEK_CONTEXT activation thresholds shift by `(fp - fn) * 0.10` inside the `[0.05, 0.60]` band, the brake tonic EMA damps single-tick flips with `rho = 0.60` and a `tonic_pressure >= 0.35` enter gate, phasic spikes still flip immediately, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes; default no-publication paths must stay memory-off, raw SQLite episodes must stay support-side only, live `Q_mem` stays zero on shipping and conformance default lanes, and the next active leverage now moves out of new skill expansion and into dead-weight elimination and doctrine/code reconciliation on the brake exit side. |

## Math To Code Rules

- Every load-bearing executive skill must land as explicit law, typed code, and at least one proof surface.
- Every packet-level mathematical object should map to exactly one typed code object or operator family with one owning module.
- Every typed load-bearing code object should have one clear home and one explicit test or proof surface.
- Forbidden leaks across Core, SRE, AUX, host wiring, and lab proof surfaces must be explicit.
- Law revision rule: The current math is binding landing law until live evidence disproves or narrows it. When that happens, revise the law explicitly and update the code and proof surfaces in the same seam; do not silently patch around stale math in implementation.

## System Map

```mermaid
flowchart TD
    hosts["Host Surfaces\nOpenAI / Claude / Gemini / Reference"]
    core["Core Microkernel\ncommitments / provenance / dispatch"]
    runtime["Shared Runtime Kernels\nverified-work runtime helpers"]
    sre["Shared Executive\nbranching / brake / reference policy"]
    shipping["Shipping Product Lane\nopenai:operator_cli"]
    lab["Proof And Data Tooling\nconformance / output-quality / train loops"]
    archive["Archive Evidence\nhistorical docs / retired proof surfaces"]
    hosts --> core
    core --> runtime
    core --> sre
    runtime --> shipping
    sre --> shipping
    lab -.-> core
    lab -.-> sre
    archive -.-> lab

    classDef good fill:#dff3e4,stroke:#2f855a,color:#1f2937;
    classDef warn fill:#fff3cd,stroke:#b7791f,color:#1f2937;
    classDef bad fill:#f8d7da,stroke:#c53030,color:#1f2937;
    classDef deferred fill:#e5e7eb,stroke:#6b7280,color:#1f2937;

    class hosts warn;
    class core good;
    class runtime good;
    class sre warn;
    class shipping good;
    class lab deferred;
    class archive deferred;
```

## Subsystems

| Subsystem | Status | Code Homes | Note |
| --- | --- | --- | --- |
| Core Microkernel | `green` | `cortex/core`, `cortex/drivers` | Active product law for commitments, provenance, dispatch, and host binding. |
| Shared Runtime Kernels | `green` | `cortex/runtime` | Only shared runtime kernels belong here. |
| Shared Executive | `yellow` | `cortex/sre` | Richer shared executive is active Cortex code; mediation remains experimental/off-by-default even though it lives beside the active SRE family. |
| Host Realizations | `yellow` | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | Host-native shells are part of Cortex reality; shipping truth stays OpenAI-first while Claude, Gemini, and reference remain explicit conformance surfaces. |
| Proof And Data Tooling | `gray` | `lab`, `lab/eval`, `tools` | Proof, evaluation, and maintainer tooling. Useful for falsification, not product truth. |

## Packet To Code

| Packet | Responsibility | Code Homes | Proof Surfaces |
| --- | --- | --- | --- |
| `Core` | Lifecycle-first dispatch, commitment extraction, provenance, certification, and bounded environment access. | `cortex/core`, `cortex/drivers` | `tests/product`, `tests/conformance` |
| `SRE` | Reference control policy, branching, brake, uncertainty, verified-work preservation, and reference scoring. | `cortex/sre` | `tests/product`, `tests/experimental` |
| `Host Wiring` | Host-native runtime shells and transport/service bindings for OpenAI, Claude, Gemini, and reference. | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` |
| `Lab Proof` | Conformance runners, output-quality tooling, and train-loop evidence used to falsify or prove product seams. | `lab`, `lab/eval` | `tests/lab`, `tests/internal` |

## Hosts

| Host | Shipping | Conformance | Strongest Surface | Daily Iteration | Code Home |
| --- | --- | --- | --- | --- | --- |
| `openai` | `default` | `conformant` | `operator_cli` | `operator_cli` | `cortex/hosts/openai` |
| `claude` | `non-default` | `conformant` | `operator_cli` | `operator_cli` | `cortex/hosts/claude` |
| `gemini` | `non-default` | `conformant` | `operator_cli` | `operator_cli` | `cortex/hosts/gemini` |
| `reference` | `non-product` | `conformant` | `reference_cli` | `reference_cli` | `cortex/hosts/reference` |

## Shipping And Conformance Truth

- Shipping default: `openai:operator_cli`
- Accepted conformance next decision: `promote`

## Closure Gates

Workflow gates marked `required` are contractual gates checked by `repo_workflow.py`, not a claim about every attached local worktree at render time.

| Gate | Status | Note |
| --- | --- | --- |
| `main_synced` | `required` | Required workflow gate: resting truth is enforced through clean synced main and the workflow helper. |
| `cleanup_report` | `required` | Required workflow gate: cleanup-report is the strict final hygiene gate for the resting repo state. |
| `single_truth` | `passed` | The status registry and generated status doc are the only live operational truth surfaces. |
| `legacy_test_buckets_removed` | `passed` | tests/unit and tests/integration are retired in favor of purpose-first active buckets. |

## Next Product Train

- Train: `brain-capability-observation-and-inference`
- Surface: product + experimental + aux
- Executive benefit: Replace the static name-based brain capability registry with an observed-performance accumulator: per-(host, model, task_class) running aggregates of continuity, verification, and contract-binding pass rates, derived into an `OperatorBrainCapabilityEnvelope` at runtime. The SRE-side assessment math and routing consequences from the brain-capability-aware-routing seam are reusable unchanged; only the source of the envelope changes from name-lookup to inference. Static name-based bands remain the cold-start prior until sufficient observations accumulate.
- Why now: The static registry maps known model names to bands but cold-starts to standard for unknown models and never updates as a model's actual behavior drifts. An observed-performance accumulator (mirroring how `HostReliabilityPrior` works for host-tool reliability) lets the executive learn capability rather than assume it, and lets new model variants be detected automatically without registry edits.
- Primary metric: A `BrainCapabilityObservation` carrier per (host, model, task_class) with continuity_observed, verification_observed, contract_observed, sample_count, and last_validated_at; an inference function that derives `OperatorBrainCapabilityEnvelope` from the accumulator with hybrid prior-plus-update behavior; AUX-side publication through `OfflineSupportPublication.host_capability_envelope`; the SRE-side assessment math and routing consequences remain unchanged.
- Guardrail: Capability inference must publish through AUX support side per AUX_2 claim-conservative law; observations must not mutate routing directly. TTL must expire stale observations under fresh contradiction (matching the `q_mem-host:reliability-active` vs `ttl-expired` pattern). The cold-start prior must remain the static band-name registry until sufficient samples accumulate.
- Kill rule: Cut the seam if observed inference admits a route that should have been BLOCKED, lowers commitment certification standards, drifts away from the static band prior under low sample counts, or hardens a capability into a host-wide superstition that fresh contradiction cannot widen.

## Research Lines Under Evaluation

- `<none>` — no research lines are currently under evaluation. Per AGENTS.md Anti-Drift, every research line that has produced code or doctrine must be in exactly one of four states at session close: earned (landed), queued (next_product_train), retired (archive manifest), or under-evaluation (this list).

## Where To Work Next

- Keep the bounded audit surface compact and truthful on the shipped lane: selected versus realized family, uncertainty, threshold, delta, verification, and probe truth only.
- Keep the no-spend live evidence current and explicit: fast conformance is green, the deeper directionality and host-native watchlists are refreshed, and non-shipping auth or env caveats must stay explicit instead of silently stale.
- Keep posture, AUX memory, host-reliability, and asymmetric-cost law explicit and removable now that posture-sensitive online control is S-tier closed, anti-thrash is landed, bounded live support-memory re-entry is earned on reference and the OpenAI operator lane, evidence/probe calibration is S-tier closed, host/tool reliability and affordance priors are earned as bounded host-scoped, capability-scoped score modifiers on `OfflineSupportPublication.host_reliability_prior` with a single-site six-tag `q_mem-host:*` surface and stale-negative reopen under fresh success, asymmetric error cost is earned as a bounded `RiskWeight` carrier whose CHECK/SEEK_CONTEXT activation shift is clipped inside `[0.05, 0.60]` with a `0.10` dead-band and productive-exploration gating, and the brake tonic EMA damps single-tick flips with a locked `rho = 0.60` decay and `tonic_pressure >= 0.35` enter gate while phasic spikes still flip immediately: inspect is live on cheap non-debt events, resume stays continuity-conditioned, posture truth is single-owned, the route state vector stays the bounded 6-axis geometry term while `visible_burden_sensitivity` remains a separate utility scalar, route truth stays bounded and non-sovereign, unchanged-condition repetition is taxed only at the exact-family level with bounded reopen, public feedback-window summaries reflect the just-realized step, family-local bounded probe limits surface as `unsupported` without leaking host-global unavailability across families, stream-only churn stays non-epistemic, live memory stays score-only and host-matched through explicit publication, live `Q_mem` stays zero on shipping and conformance default lanes, raw SQLite episodes stay support-side only, reliability priors bias score pricing only and never route, posture, selection, or brake law, Claude and Gemini remain shadow-proof only for reliability promotion, `risk_weight` biases CHECK/SEEK_CONTEXT activation threshold only and never routing, posture, selection, certification, or blockedness law, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes with three-way backward-compat decoding.
- The brain-capability-aware-routing seam is the active focus per SRE_2 §6.9: the executive carries an `OperatorBrainCapabilityEnvelope` and a bounded threshold ladder classifies the per-dimension max mismatch into NONE / DEGRADE / UNSUPPORTED at 0.20 / 0.50; DEGRADE downshifts continuity-bearing profiles to inspect-light, suppresses retries, and switches contract binding to LEAN, while UNSUPPORTED routes to BLOCKED with `brain_capability_mismatch`. The mechanism is host-agnostic at the SRE layer; the band registry is OpenAI-only and other hosts default to standard until per-host registries earn their own seam. The brake-tonic-quiescence-exit-reconciliation seam (closed via SRE_2 §7.5 path B) is no longer active; doctrine and code agree on threshold-hysteresis-only on the brake exit gate, and the locked `rho = 0.60` EMA regression is preserved.

## Canonical Proof

**Default**

- `make product-test`
- `make conformance-test`
- `make experimental-test`
- `make -C internal test`
- `make lab-test`

**Status**

- `python3 internal/truth/generate_status.py --check`
- `python3 internal/archive/generate_archive_index.py --check`

**Workflow**

- `python3 internal/workflow/repo_workflow.py sync-main`
- `python3 internal/workflow/repo_workflow.py start-session --agent codex --slug task-name`
- `python3 internal/workflow/repo_workflow.py close-session --message "scope: end-state summary"`
- `python3 internal/workflow/repo_workflow.py close-session --publish --message "scope: end-state summary"`
- `python3 internal/workflow/repo_workflow.py cleanup-report`

## Retained Data

- `conformance` at `.cortex/live_validation/conformance` keeps `accepted_baseline`, `current_candidate`, `latest`
  Policy: Timestamped runs are generated evidence only; manifests and summaries outrank raw timestamp directories.
- `train_loops` at `.cortex/train_loops` keeps `accepted_baseline`, `current_candidate`, `latest`
  Policy: Compact summaries are the maintained view; old train narratives are archival.

## Retained Evidence Refs

- `E23 preservation-state evidence` -> `archive/e23-preservation-state-machine`
  Purpose: Preserved review evidence for the landed preservation-state kernel extract and later provenance checks.

## Blocked Moves

- Do not let archived docs or train notes act as live truth.
- Do not treat lab or evaluation output as product progress unless shipped runtime behavior changes.
- Do not hide Claude or Gemini behind backlog language when reporting conformance.
- Do not route raw AUX SQLite episodes directly into runtime action selection; only distilled removable publications may re-enter.
- Do not let a generic second unrelated episode smuggle a positive AUX prior into retrieval, branch, memory-summary, or uncertainty output.
- Do not let anti-thrash become a global retry ban or a creativity collapse.
- Do not silently widen the 6-axis operator-route geometry vector or hide utility inputs that affect route selection.
- Do not introduce host-specific policy forks to force donor coherence.
- Do not let generic pending-goal debt, plain-English reminder text, or generic `resume*` wake cues act as branch-specific continuity anchors.
- Do not let live memory re-entry drift into cross-host projected reuse, background AUX loading, raw `/v1/events` transcript widening, or default-on operator behavior.
- Do not let stale branch or redirect replay survive fresh contradiction or degradation on the same active resume context.
- Do not let host/tool reliability priors harden into host-wide superstition, cross-host projected reuse, default-on memory behavior, hidden policy forks, or route/posture/brake law drift; reliability must stay explicit, host-matched, capability-scoped, contradiction-first, and removable, biasing score pricing only.
- Do not let asymmetric error cost widen beyond CHECK and SEEK_CONTEXT activation thresholds, shift outside the `[0.05, 0.60]` clip band, default caution on cold/fresh sessions, or route/posture/selection/certification/blockedness law drift through `RiskWeight`; risk-sensitive pricing must stay bounded, profile-derived, dead-band-protected, and backward-compat to zero-shift on balanced snapshots.
- Do not let brake tonic hysteresis become sticky guardedness under sustained calm, drift the locked `rho = 0.60` EMA coefficient, gate phasic contradiction/latching/missing-anchor/repeated-failure spikes behind tonic smoothing, or introduce a host-specific brake policy fork; the tonic must stay a bounded damping of single-tick `quiescent`/`guarded` flips on `tonic_pressure` only, and a parallel rest-side EMA carrier (`tonic_quiescence`) must not be reintroduced under SRE_2 §7.5 path B.
- Do not let brain-capability adaptation become hidden inference (capability must come from an explicit `OperatorBrainCapabilityEnvelope`, not an undocumented model heuristic), a host-specific routing fork (the SRE-side assessment and threshold ladder must be host-agnostic; only per-host band registries may differ), a commitment-relaxation surface (the assessment biases routing and budget only; it must never lower commitment certification standards or admit a soft route that should have been hard-blocked), or a stale-band stickiness (when dynamic inference earns its seam, fresh contradictory evidence must be able to widen or narrow the envelope).

## Active Docs

- `docs/README.md`
- `docs/CORTEX.md`
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_STATUS.md`
- `docs/internal/REPO_WORKFLOW.md`
- `docs/cortex_plugin/DESIGN.md`
- `docs/cortex_plugin/ADAPTER.md`
- `docs/runtime_context/EVAL_RUBRIC.md`
- `docs/runtime_context/BASELINE_SHAPED_EXAMPLES.md`
- `docs/runtime_context/CROSS_HOST_SKETCH.md`
- `docs/recon/lifecycle_first_surface_matrix.md`
- `docs/recon/codex_app_hook_probe.md`
- `docs/recon/claude_code_desktop_pretooluse_probe.md`
- `docs/recon/claude_code_user_scope_plugin_pretooluse_probe.md`
- `docs/recon/claude_code_user_scope_plugin_managed_worktree_probe.md`
- `docs/recon/claude_code_cortex_runtime_context_connectivity_probe.md`