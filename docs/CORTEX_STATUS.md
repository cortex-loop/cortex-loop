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

- Current tracked train: `persistent-support-memory-distillation`
- Active quality/risk focus: The bounded AUX cross-host shadow surface now earns `full_cross_host`: Claude, Gemini, and reference all hold host-local and reference-projected branch continuity, lawful non-reference host distinction remains explicit, and negative counterexamples stay stable. The next highest-leverage gap is durable support-memory distillation: store raw support-side episodes, publish compact removable priors offline, and keep `Q_mem = 0` on shipping and conformance lanes until live re-entry is separately earned.
- Next product train after the current focus: `inspect-execute-resume-posture-control`

## Bio-To-Code Matrix

| Executive Skill | What We Are Stealing | Status | Weight | Code Homes | Proof Surfaces | Next Move |
| --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | Truth maintenance and reality binding | `landed` | `12` | `cortex/core`, `cortex/drivers` | `tests/product`, `tests/conformance` | Keep this foundation stable while richer executive control builds on top. |
| Bounded correction and verified-work preservation | Error repair without losing the main task thread | `landed` | `15` | `cortex/runtime`, `cortex/sre`, `cortex/hosts/openai` | `tests/product` | Keep preservation-state repair stable while support-side experiments stay removable and off the shipping critical path. |
| Uncertainty handling and brake | Hesitation and uncertainty-aware inhibition | `landed` | `13` | `cortex/sre` | `tests/product`, `tests/experimental` | Keep reference-derived brake and uncertainty control stable while AUX remains advisory and runtime-off-by-default. |
| Branch continuity, suspend/resume, and truthful closure | Working memory across interruptions plus truthful closure | `landed` | `15` | `cortex/sre`, `cortex/hosts/openai` | `tests/product`, `tests/conformance` | Keep suspend/resume and truthful closure stable now that host-local branch continuity is repaired across Claude, Gemini, and reference; any future support memory must remain explicit, optional, and non-binding. |
| Intervention pricing versus neutrality | Deciding when to intervene, stay neutral, or stop | `landed` | `10` | `cortex/sre`, `cortex/aux` | `tests/product`, `tests/experimental` | Hold calibrated intervention pricing stable now that the bounded AUX shadow surface earns `full_cross_host`; keep bounded audit compact on the shipped lane while any future support-memory lift stays explicit and separately earned. |
| Blocker surfacing and goal-debt management | Noticing unresolved blockers and unfinished intentions | `landed` | `10` | `cortex/sre`, `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Keep typed goal-debt and closure-pressure state stable across hosts while support-side augmentation remains explicit and non-sovereign. |
| Multi-host executive continuity | One executive across different brains and contexts | `landed` | `15` | `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference` | `tests/product`, `tests/conformance` | Hold one Cortex law across OpenAI, Claude, Gemini, and reference without flattening host-native realization. |
| Offline consolidation and support geometry | Sleep-like consolidation and support systems | `landed` | `10` | `cortex/aux` | `tests/experimental`, `tests/archive`, `tests/conformance` | Keep offline publication explicit, removable, and non-sovereign now that the bounded AUX shadow surface earns `full_cross_host`; the next leverage is durable support-memory distillation rather than widening live `Q_mem`. |

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

- Train: `inspect-execute-resume-posture-control`
- Surface: `product + conformance + internal`
- Executive benefit: Make Cortex use a compact inspect/execute/resume posture so verification intensity, read allowance, and stop thresholds match task state instead of one control profile everywhere.
- Why now: Cross-host host-local continuity and the broader AUX shadow claim are now earned, so persistent support-memory distillation is the active train and posture-sensitive online control is the next queued leverage after durable support priors exist.
- Primary metric: `inspect-heavy tasks request more verification, execute tasks stay compact, and resume tasks favor continuity reconstruction without posture churn`
- Guardrail: `no large mode taxonomy, no host-specific posture semantics, and no verbosity inflation`
- Kill rule: `cut any seam that adds posture bureaucracy without improving task-state-sensitive control allocation`

## Where To Work Next

- Keep the bounded audit surface compact and truthful on the shipped lane: selected versus realized family, uncertainty, threshold, delta, verification, and probe truth only.
- Keep the no-spend live evidence current and explicit: fast conformance is green, the deeper directionality and host-native watchlists are refreshed, and non-shipping auth or env caveats must stay explicit instead of silently stale.
- Keep the next AUX memory seam explicit and removable now that bounded cross-host shadow acceptance is earned: durable support-memory distillation may publish compact priors offline, but live `Q_mem` stays zero on shipping and conformance lanes until separate proof earns re-entry.

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
- Do not route raw AUX persistence or future SQLite episodes directly into runtime action selection; only distilled removable publications may re-enter.
- Do not introduce host-specific policy forks to force donor coherence.

## Active Docs

- `docs/README.md`
- `docs/CORTEX_PRODUCT_CHARTER.md`
- `docs/CORTEX_PRODUCT_BOUNDARY.md`
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_STATUS.md`
- `docs/internal/REPO_WORKFLOW.md`