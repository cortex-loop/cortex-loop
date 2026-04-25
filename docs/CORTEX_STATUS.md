# CORTEX Status

Surface: product

_Generated from `internal/truth/cortex_status.json`. Edit the registry, then run `python3 internal/truth/generate_status.py`._

## Resting State

- Branch: `main`
- Rule: Clean synced main is the only resting state; the richer Cortex executive remains the product goal, and archive or lab surfaces do not define live product truth.

## Bootstrap

- `AGENTS.md`
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

- Current tracked train: `v2-communication-optimization`
- Active quality/risk focus: Initial V2 communication optimization is landed for the current Claude/OpenAI tranche without dropping the 17-row denominator: the guidance renderer now has explicit `raw`, `full`, and `compressed_dynamic` modes; compressed guidance renders a smaller active packet while `v2_guidance_denominator_coverage_payload` records every denominator row as always-on, dynamic-triggered, or silent-with-reason; intervention intent is exposed as CHECK, SEEK_CONTEXT, BRAKE, REPAIR, CONTINUE, or CLOSE without expanding SRE family law; and the operator directionality harness now compares `raw_host`, `full_v2_guidance`, and `compressed_dynamic_cortex` on six behavioral payoff scenarios. Live no-spend evidence is current: `.cortex/live_validation/agent_loop_guard/v2_live_communication_audit.latest.json` run `20260425T132046Z0000` passed for Claude and Codex CLI with all 17 rows visible; `.cortex/live_validation/operator_directionality/claude/summary/summary.json` and `.cortex/live_validation/operator_directionality/openai/summary/summary.json` record one-repeat 3-way behavioral matrices where Claude and the OpenAI/Codex-side harness are positive across premature closure/truth gap, verified-work repair, uncertainty/context, restart continuity, anti-thrash, and unsupported-claim refusal; and `.cortex/live_validation/comparators/v2_guidance_optimization_audit.latest.json` passes compression integrity, full-communication non-regression, and the provider-scoped causal payoff gate for `claude` plus `openai`. This is bounded optimization evidence, not Cortex perfection: Gemini/reference remain conformance truth but outside this first live behavioral tranche, OpenAI behavioral evidence is from the app-server/operator harness rather than the Codex CLI communication-audit surface, token-cost visibility remains host-dependent, and further intervention-policy tuning must use causal evidence rather than vibe-based threshold changes.
- Next product train after the current focus: `v2-intervention-policy-tuning`

## Bio-To-Code Matrix

| Executive Skill | What We Are Stealing | Status | Weight | Code Homes | Proof Surfaces | Next Move |
| --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | Truth maintenance and reality binding | `landed` | `12` | `cortex/core`, `cortex/drivers` | `tests/product`, `tests/conformance` | Keep this foundation stable while richer executive control builds on top. |
| Bounded correction and verified-work preservation | Error repair without losing the main task thread | `landed` | `15` | `cortex/runtime`, `cortex/sre`, `cortex/hosts/openai` | `tests/product` | Keep preservation-state repair stable while support-side experiments stay removable and off the shipping critical path. |
| Uncertainty handling and brake | Hesitation and uncertainty-aware inhibition | `landed` | `13` | `cortex/sre` | `tests/product`, `tests/experimental` | Keep reference-derived brake and uncertainty control stable while AUX remains advisory and runtime-off-by-default. |
| Branch continuity, suspend/resume, and truthful closure | Working memory across interruptions plus truthful closure | `landed` | `15` | `cortex/sre`, `cortex/hosts/openai` | `tests/product`, `tests/conformance` | Keep suspend/resume and truthful closure stable now that host-local branch continuity is repaired across Claude, Gemini, and reference; branch-local continuity may reopen only from branch-linked cues, and any future support memory must remain explicit, optional, and non-binding. |
| Intervention pricing versus neutrality | Deciding when to intervene, stay neutral, or stop | `landed` | `10` | `cortex/sre`, `cortex/aux` | `tests/product`, `tests/experimental` | Hold calibrated intervention pricing stable now that posture-sensitive online control is S-tier closed and anti-thrash is landed on the live runtime path: posture truth is single-owned, the 6-axis route geometry stays bounded, `visible_burden_sensitivity` is surfaced as a separate utility scalar, unchanged-condition repetition is taxed only at the exact-family level with bounded reopen, and any later live memory re-entry must remain explicit, bounded, and separately earned. |
| Blocker surfacing and goal-debt management | Noticing unresolved blockers and unfinished intentions | `landed` | `10` | `cortex/sre`, `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Keep typed goal-debt and closure-pressure state stable across hosts while support-side augmentation remains explicit and non-sovereign. |
| Multi-host executive continuity | One executive across different brains and contexts | `landed` | `15` | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Hold one Cortex law across OpenAI, Claude, Gemini, and reference without flattening host-native realization. |
| Offline consolidation and support geometry | Sleep-like consolidation and support systems | `landed` | `10` | `cortex/aux` | `tests/experimental`, `tests/archive`, `tests/conformance` | Keep durable support-memory distillation explicit, removable, and non-sovereign now that reference and OpenAI both earn explicit publication-shaped live re-entry with host-match, family-scoped invalidation, publication-only runtime-boundary proof, S-tier evidence/probe calibration, bounded host/tool reliability and affordance priors that bias control pricing through host-scoped, capability-scoped score modifiers only, decay under fresh success, and never harden into host-wide superstition, cross-host projected reuse, or default-on memory, and asymmetric error cost and tonic hysteresis are earned on the shared executive so CHECK and SEEK_CONTEXT activation thresholds shift by `(fp - fn) * 0.10` inside the `[0.05, 0.60]` band, the brake tonic EMA damps single-tick flips with `rho = 0.60`, a `tonic_pressure >= 0.35` enter gate, and a `tonic_quiescence >= 0.65` guarded-exit gate while phasic spikes still flip immediately, and `brake_tonic_history` persists the pressure tail across resume with quiescence reconstructed from that bounded pressure tail and no new carrier; default no-publication paths must stay memory-off, raw SQLite episodes must stay support-side only, live `Q_mem` stays zero on shipping and conformance default lanes, and the next active leverage moves into V2 communication optimization now that the Claude/Codex CLI live watchlist closure proof is captured. |

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

- Train: `v2-intervention-policy-tuning`
- Surface: `product + conformance + lab`
- Executive benefit: Tune when Cortex should CHECK, SEEK_CONTEXT, BRAKE, REPAIR, CONTINUE, or CLOSE so the active packet improves executive timing rather than merely adding guidance.
- Why now: The first compressed/dynamic guidance tranche now preserves the full denominator and earns positive Claude/OpenAI behavioral payoff. The next risk is mistimed intervention: unnecessary control burden when neutral continuation would work, or missed brakes/context seeks when the host would otherwise close prematurely.
- Primary metric: a repeated causal evidence bundle where compressed/dynamic guidance keeps or improves task success, truthful closure, blocker surfacing, verification quality, token/latency cost, and unnecessary-intervention rate against raw and full V2 variants on Claude plus OpenAI/Codex-side surfaces
- Guardrail: do not tune intervention thresholds from vibes, do not collapse Gemini/reference conformance truth into the first Claude/OpenAI tranche, do not treat app-server watchlist behavior as Codex CLI behavioral proof, and do not lower guidance burden by hiding denominator rows without coverage artifacts
- Kill rule: stop tuning if compressed/dynamic guidance regresses below full V2 on target scenarios, raises burden without payoff, hides blockedness/certification truth, or produces host-specific policy forks instead of shared Cortex law

## Where To Work Next

- Keep the bounded audit surface compact and truthful on the shipped lane: selected versus realized family, uncertainty, threshold, delta, verification, and probe truth only.
- Keep the no-spend live evidence current and explicit: fast conformance is green, the deeper directionality and host-native watchlists are refreshed, and non-shipping auth or env caveats must stay explicit instead of silently stale.
- Keep posture, AUX memory, host-reliability, asymmetric-cost law, and brake tonic law explicit and removable now that posture-sensitive online control is S-tier closed, anti-thrash is landed, bounded live support-memory re-entry is earned on reference and the OpenAI operator lane, evidence/probe calibration is S-tier closed, host/tool reliability and affordance priors are earned as bounded host-scoped, capability-scoped score modifiers, asymmetric error cost is earned as a bounded `RiskWeight` carrier, and the brake tonic EMA now gates both `tonic_pressure >= 0.35` guarded entry and `tonic_quiescence >= 0.65` guarded exit while persisting only the pressure tail across resume; inspect is live on cheap non-debt events, resume stays continuity-conditioned, posture truth is single-owned, route truth stays bounded and non-sovereign, live memory stays score-only and host-matched through explicit publication, live `Q_mem` stays zero on shipping and conformance default lanes, raw SQLite episodes stay support-side only, reliability priors bias score pricing only, and `risk_weight` biases CHECK/SEEK_CONTEXT activation threshold only.
- Tune the now-live compressed/dynamic V2 communication seam using causal evidence: preserve the 17-row denominator coverage artifact, repeat Claude/OpenAI behavioral matrices before threshold changes, reduce unnecessary intervention rate without losing blocker surfacing or truthful closure, and keep Gemini/reference conformance truth explicit instead of treating the first Claude/OpenAI tranche as all-host behavioral proof.

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
- Do not let brake tonic hysteresis become sticky guardedness under sustained calm, drift the locked `rho = 0.60` EMA coefficient, silently persist `tonic_quiescence` across resume, gate phasic contradiction/latching/missing-anchor/repeated-failure spikes behind tonic smoothing, or introduce a host-specific brake policy fork; the tonic must stay a bounded damping of single-tick flips only.

## Active Docs

- `docs/README.md`
- `docs/CORTEX_PRODUCT_CHARTER.md`
- `docs/CORTEX_PRODUCT_BOUNDARY.md`
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_STATUS.md`
- `docs/internal/REPO_WORKFLOW.md`