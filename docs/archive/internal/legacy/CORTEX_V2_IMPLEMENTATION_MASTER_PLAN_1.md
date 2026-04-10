# CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_1

Status: canonical implementation master plan for blank-repo Cortex v2 build (`active`)
Date: 2026-03-17
Primary objective: build Cortex v2 as a **lifecycle-first, packet-first internally / host-native externally, executive-first, host-affordance-native system** with a **tiny integrity microkernel**, using only the narrow battle-proven v1 code that fits the new Core / SRE / AUX packet.

Active packet authority:
- `CORTEX_V2_CORE_2.md`
- `CORTEX_V2_SRE_2.md`
- `CORTEX_V2_AUX_2.md`
- `V1_CODE_PORT_DETERMINATION.md`

Evidence/background authority:
- v1 archival dossiers under `cortex-archival-dossiers/`

Historical workflow scaffolds (structure only, not content authority):
- prior `MASTER_PLAN.md`
- prior architect/auditor prompt
- prior worker prompt template

---

## 0. One-paragraph final verdict

Do **not** rebuild v1 in a new repo.
Do **not** start with all hosts, all policy math, or all auxiliary systems live at once.
Build Cortex v2 in the following order:

1. **lock authority and close the remaining shared free variables** (`W_t`, executive role recoverability, commitment wake heuristics, mode/gating content, notation hygiene);
2. **build the smallest core substrate first**;
3. **port only the narrow v1 standard library that was genuinely battle-proven**;
4. **land one reference-host vertical slice** before broadening host support;
5. **add only active SRE policy next**;
6. **move contradiction-preserving evidence harnessing earlier than broad host rollout**;
7. **keep mediation experimental and AUX off the critical path** until the core/SRE loop is stable.

The architectural success condition is not “all math implemented.”
It is: **a host-native event loop with a tiny certifying microkernel, a neutral-by-default executive, explicit degradation honesty, and contradiction-preserving evidence discipline.**

---

## 1. Prime directive

Build the **smallest runnable Cortex v2** that preserves the packet’s authority boundaries.

That means:
- the **core** owns lifecycle law, commitment extraction/certification, provenance, degradation honesty, the observation/environment split, and the event-local certification firewall;
- the **SRE** owns active executive policy;
- **AUX** remains removable, support-only, and off the MVP critical path.

The v1 archive is a **standard library and evidence source**, not a base architecture.

---

## 2. Locked truths this plan preserves

Unless live implementation evidence forces a local blocker artifact, lock the following:

1. **Core / SRE / AUX is the governing architecture.**
2. **The integrity microkernel stays tiny.** It owns only irreversible commitments, provenance sufficiency, blocked/stuck truth, and hard safety/integrity boundaries.
3. **The executive is the active intelligence.** It may shape intervention, branching, review, retrieval, uncertainty response, and pacing, but may not certify truth.
4. **AUX is removable.** Geometry and offline consolidation may never become hidden truth owners.
5. **Native host affordances take precedence.** Tools, approvals, MCP, orchestration streams, and stop/turn callbacks are first-class.
6. **Internal typed semantics remain valuable.** Cortex should not collapse into prose-only behavior.
7. **v1’s strongest reusable result was the machine-readable commitment carrier plus witness-backed provenance**, not the full stop-centered architecture.
8. **Contradictions must be preserved.** Mixed, degraded, blocked, and unsupported host states must remain explicit.
9. **Neutral continuation is the default.** The executive must not act just to justify its existence.
10. **Mediation is experimental and off by default.** Geometry is evaluation-first and runtime-off-by-default. Offline consolidation is deferred until the active Core/SRE loop is stable.

---

## 3. Running reference example (used throughout this plan)

Use one narrow reference lane throughout the first implementation:

**Reference domain:** coding-agent lane
**Reference task:** fix one bounded bug in a small repository and truthfully report completion.
**Reference host for first vertical slice:** Claude.

The reference event story is:

1. `SessionStart` / equivalent host-start event arrives.
2. User asks: “Fix `normalize_port` so the target test passes.”
3. Cheap observation events stream while the model reasons.
4. A candidate-bearing event occurs when the host surfaces a durable write proposal or other externally consequential step.
5. Read-only tool results (for example test output) are observed cheaply and update environment views without forcing certification.
6. A full commitment event occurs when the model or host attempts to finalize a durable claim such as “fixed,” emits a structured completion payload, or crosses another configured commitment boundary.
7. Core collects downward provenance (for example changed file set plus test exit state), checks hard boundaries, certifies or withholds, and realizes the commitment result.

This reference example is **not** architecture law.
It is the concrete implementation lane used to keep early seams grounded.

---

## 4. Non-goals before the first stable vertical slice

Before the first stable vertical slice, do **not**:
- implement mediation-aware control as a required runtime dependency;
- make geometry load-bearing at runtime;
- enable offline consolidation in the active loop;
- build identity/self/social overlays;
- build broad learned control-weight adaptation;
- flatten all hosts into one generic execution model;
- port the old v1 `StopVerdict / StopPathOutcome / StopPathRunner` stack as architecture;
- port adapter-side retry doctrine or prompt-heavy compensation as doctrine;
- chase cross-host parity before the first host-native vertical slice works.

---

## 5. The implementation shape

### 5.1 Runtime layers

Implementation must preserve the packet’s three-way factorization:

#### Core
Owns:
- lifecycle/event envelopes
- observation vs environment split
- support snapshot boundary
- commitment extraction
- provenance collection
- hard-boundary checks
- certification lattice
- commitment wake law
- degradation and contradiction reporting
- host-native realization of commitments

#### SRE
Owns:
- recoverable executive roles
- soft-control family selection
- uncertainty-sensitive intervention
- brake
- branch/pending-goal discipline
- control allocation / arbitration
- native-opportunity specialization
- mediation only if explicitly enabled

#### AUX
Owns:
- geometry/evaluation
- offline support-memory consolidation
- optional retrieval baselines
- support-only artifacts

### 5.2 Implementation principle

The implementation order is:

1. **Core substrate**
2. **v1 narrow standard library port into core / host drivers**
3. **minimal evidence harness primitives**
4. **neutral-only SRE + one reference host vertical slice**
5. **active SRE policy**
6. **additional hosts**
7. **full contradiction-preserving evidence packet**
8. **AUX scaffolds**

Not the reverse.

---

## 6. Blank-repo target structure

Use the smallest package structure that preserves layer boundaries.

Preferred target layout:

```text
cortex/
  core/
    lifecycle.py
    envelopes.py
    observation.py
    environment.py
    support.py
    commitments.py
    commitment_payload.py
    commitment_extract.py
    provenance.py
    boundaries.py
    certification.py
    realization.py
    errors.py
  sre/
    roles.py
    policy.py
    allocation.py
    uncertainty.py
    brake.py
    branching.py
    opportunities.py
    mediation.py            # experimental / off by default
  aux/
    geometry.py             # evaluation-first / runtime-off-by-default
    offline.py              # deferred
    retrieval.py            # optional baseline
  drivers/
    base.py
    common_normalization.py
    claude/
      driver.py
      normalize.py
      realize.py
    gemini/
      driver.py
      normalize.py
      realize.py
    openai/
      driver.py
      normalize.py
      realize.py
      app_server.py
  runtime/
    store.py
    wal.py
  eval/
    harness.py
    artifacts.py
    packets.py
    fixtures/
      synthetic_events/
      reference_domain/
tests/
  unit/
  integration/
  host/
docs/
  CORTEX_V2_CORE_2.md
  CORTEX_V2_SRE_2.md
  CORTEX_V2_AUX_2.md
  V1_CODE_PORT_DETERMINATION.md
  CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_1.md
  CORTEX_V2_PROGRESS.md   # only if truly needed
```

Law:
- file splits may be smaller or slightly merged if that keeps the slice tighter;
- the package boundary (`core` / `sre` / `aux` / `drivers`) may not be collapsed;
- experimental and deferred modules must remain physically and semantically separable.

---

## 7. V1 port map

### 7.1 Port now

Port these early because they are narrow, battle-proven, and directly useful under v2.

| v1 source | Keep | v2 destination | Port mode |
| --- | --- | --- | --- |
| `stop_payload.py` | `payload.stop_fields` handling, trailer fallback, key normalization | `cortex/core/commitment_payload.py` | port now |
| narrow `stop_contract.py` slice | structured-carrier resolution, source labeling, strict native/payload precedence | `cortex/core/commitment_extract.py` | port now |
| `core_helpers.py` provenance helpers | git snapshot, changed-files-since-baseline, witness context | `cortex/core/provenance.py` | port now |
| thin event normalization from `adapters.py` | vendor event normalization, field extraction | `cortex/drivers/common_normalization.py` and host drivers | port now |
| evidence discipline | current-pair artifacts, blocker truth, truthful-withheld logic | `cortex/eval/*` | port now in spirit, rewritten as v2 |

### 7.2 Port with rewrite

| v1 source | Keep | v2 destination | Port mode |
| --- | --- | --- | --- |
| `stop_signals.py` | attempt relation taxonomy (`identical`, `reduced`, `expanded`, `substituted`) | `cortex/sre/branching.py` or `experimental/sre/policy.py` | rewrite |
| `requirements.py` / truth-evidence leaves | leaf evidence-reference utilities | `cortex/core/provenance.py` | rewrite |
| `graveyard.py` | cheap retrieval baseline | `cortex/aux/retrieval.py` | rewrite |
| `store.py` | WAL / atomic persistence patterns | `cortex/runtime/store.py`, `cortex/runtime/wal.py` | rewrite |
| OpenAI event reconstruction | streamed event stitching / approval state ideas | `cortex/drivers/openai/*` | rewrite |

### 7.3 Do not port as architecture

| v1 source | Why rejected |
| --- | --- |
| `StopVerdict`, `StopPathOutcome`, `StopPathRunner` stack | proof-centered architecture, wrong product center |
| adapter-side retry doctrine | prompt-heavy compensation, not host-native doctrine |
| larger proof-centered stop worldview | wrong conceptual center for v2 |

### 7.4 Port-law example

Running example:
- Port `stop_payload.py` behavior into `commitment_payload.py`.
- Do **not** port `StopVerdict`.
- The worker should prove: “payload carrier extraction works on a synthetic commitment event,” not “the old stop stack runs in v2.”

---

## 8. Status vocabulary and maturity tags

Use these statuses only:
- `open`
- `active`
- `landed`
- `blocked`
- `strong_enough`
- `descoped`

Use one tiny progress board only if the repo truly needs it.

Use maturity tags consistently:
- **active** = required for MVP implementation path
- **experimental** = official but off by default; not required for MVP
- **deferred** = recognized but not on the active path
- **evaluation-first** = allowed for measurement and experiments before runtime activation

---

## 9. Shared-state and readiness law (must land before broad coding)

### 9.1 `W_t` canonical support-state families

For first implementation, treat support state as:

\[
W_t = (W_t^{trace}, W_t^{session}, W_t^{host}, W_t^{execmem,pub})
\]

with the following reference meanings:

- `W_t^{trace}`
  - rolling event-local trace window
  - ephemeral / session-local
  - may contain recent envelopes, extracted candidates, degradation notes, and lightweight observables
- `W_t^{session}`
  - mutable session support state
  - branch registry, budget/brake history, wake counters, current role snapshots, unresolved session-local reminders
- `W_t^{host}`
  - current host affordance snapshot and observed host constraints
  - not a hidden truth court
- `W_t^{execmem,pub}`
  - cross-session published support memory
  - read-only to Core and SRE
  - writable only by AUX through explicit augmentation flow

Write boundaries:
- **Drivers/Core** may write `W_t^{trace}` and host-observed portions of `W_t^{session}` / `W_t^{host}`.
- **SRE** may write session-local executive working state in `W_t^{session}`.
- **AUX** may only write `W_t^{execmem,pub}` and associated published support artifacts.
- No layer may silently rewrite another layer’s authority object.

Persistence boundaries:
- `W_t^{trace}`: per-session rolling window, not durable across sessions
- `W_t^{session}`: durable only for the current session/run
- `W_t^{host}`: session/config scoped
- `W_t^{execmem,pub}`: cross-session durable support memory

### 9.2 Minimal software-shaped executive role views

The SRE remains representation-flexible, but first implementation must be able to recover at least these software-facing views:

- `goal_view`
  - `main_goal_id`
  - `active_track_id`
  - `pending_goal_count`
  - `resume_anchor_available: bool`
- `uncertainty_view`
  - classwise uncertainty bands
  - spike flags
- `mode_gate_view`
  - `mode_tag`
  - `family_mask`
- `control_view`
  - `budget_band`
  - `top_family_ranking`
  - `recent_intervention_count`
- `brake_view`
  - `brake_state`
  - `dominant_cause`

These are role-recovery requirements, not a latent carrier theorem.

### 9.3 Mode/gating reference content

For first implementation, use the following reference mode tags:
- `pass_through`
- `verify`
- `branching`
- `recovery`
- `handoff`

For first implementation, `family_mask` must be able to admit or suppress at least:
- `neutral`
- `check`
- `seek_context`
- `redirect`
- `branch`
- `escalate`
- `brake`

Reference operational meaning:
- `pass_through`: default; only bounded low-cost interventions are admissible
- `verify`: checking/context-seeking favored; external effect families constrained
- `branching`: branch-family actions admissible when bounded advantage exists
- `recovery`: redirects/checks favored after contradiction or failure
- `handoff`: escalation/handoff actions admissible; low-value local retries suppressed

### 9.4 Commitment wake reference heuristic (coding reference lane)

For first implementation, a commitment wake must be triggered when at least one of the following is true:

- the current event is an explicit host commitment/completion region;
- the host surfaces a structured commitment candidate;
- a durable write or externally consequential action is about to occur;
- a human approval crossing an external boundary is being accepted;
- the model or host is asserting completion / success / externally visible claim state.

Reference decision table for the coding lane:

| Event surface | Example | Path |
| --- | --- | --- |
| stream token / chat chunk | ordinary generation text | cheap |
| read-only tool result | `pytest` output, file read, grep result | cheap |
| write proposal / apply patch proposal | `write_file`, `apply_patch`, durable write intent | candidate-bearing |
| durable write execution / external mutation | file write committed, external record mutation | full commitment |
| final completion claim | “fixed”, structured completion payload, task-complete callback | full commitment |
| branch bookkeeping | open/suspend/resume branch marker | cheap unless paired with commitment claim |

Law:
- over-waking is a bug;
- under-waking is a bug;
- the first implementation domain must ship with an explicit decision table.

### 9.5 Notation hygiene

For implementation-facing discussion and code, do **not** reuse one letter for multiple live objects.
Use:
- `Wsnap_t` or `SupportSnapshot_t` for support snapshots
- `CStat_t(c)` for commitment status
- `Wake_t` for wake decisions

Do not reuse bare `S_t` for multiple meanings.

### 9.6 Goal-scoring separation rule

To prevent double-counting, first implementation must distinguish:
- `q_goal_main(a)` = main-task preservation / goal continuity
- `q_goal_branch(a)` = branch-management fitness

Law:
- `q_goal_main(a)` may apply across all relevant families
- `q_goal_branch(a)` applies only to branch-bearing actions or explicit branch lifecycle decisions
- default reference implementation must **not** add both to the same candidate unless that combination is explicitly documented and normalized

### 9.7 Readiness-gate done-means

The readiness gate is landed only when:
- `W_t` is no longer a free variable
- role views are operational enough for code
- mode/gating has enough content to implement admissibility
- commitment wake has a reference heuristic and decision table
- naming is clean enough not to poison the codebase

### 9.8 Anti-drift

- do not reopen packet philosophy here
- do not broaden into mediation, geometry, or offline learning
- do not start runtime coding on unresolved shared-state assumptions

---

## 10. Error model and runtime budgets

### 10.1 Canonical recoverable runtime errors

First implementation must explicitly represent at least:
- `observation_malformed`
- `environment_unavailable`
- `commitment_extract_failed`
- `provenance_unavailable`
- `boundary_check_failed`
- `realization_rejected`
- `driver_timeout`
- `host_payload_unrecognized`

Law:
- these errors must degrade to explicit runtime states or blocker artifacts;
- they may not silently cross layer boundaries as hidden doctrine;
- the cheap path must stay cheap even when errors occur.

### 10.2 Performance budgets (first implementation targets)

Targets apply **excluding host network/model latency and excluding external tool runtime cost**. They are local Cortex overhead budgets on the small reference lane.

- **cheap path**
  - median <= 5 ms
  - p95 <= 20 ms
- **candidate-bearing path (without full provenance gather)**
  - median <= 15 ms
  - p95 <= 50 ms
- **full commitment path**
  - median <= 75 ms
  - p95 <= 250 ms
- **neutral SRE scoring overhead**
  - median <= 2 ms
  - p95 <= 10 ms

Law:
- if a slice materially exceeds the relevant budget, it cannot be marked cleanly landed without an explicit performance blocker or budget exception artifact.

---

## 11. Integration-test surface (must exist before the first host vertical slice closes)

The hardest bugs are layer-seam bugs. Therefore the implementation must define explicit integration surfaces early.

Required integration tests:

1. **cheap-path integration**
   - driver normalization -> observation -> environment bind -> support snapshot -> neutral realization
2. **candidate-bearing integration**
   - event -> candidate extraction -> no premature provenance gather when no commitment is due
3. **full commitment integration**
   - event -> extraction -> provenance -> boundary check -> certification -> commitment realization
4. **degradation roundtrip**
   - malformed or unsupported host event becomes explicit degradation/blocked truth
5. **firewall integration**
   - executive may read bounded environment state but cannot directly certify truth
6. **driver-to-core-to-sre smoke**
   - real host-shaped synthetic fixture crosses the intended layer boundaries correctly

These tests must be seeded by Phase 5 and active by the time Phase 6 closes.

---

## 12. Architect / worker operating law

### 12.1 Architect / auditor

The architect must:
- establish the true repo boundary;
- keep the implementation aligned with the active packet;
- choose one exact seam at a time;
- emit exactly one worker prompt;
- verify the worker output itself;
- update status only if earned;
- stop truthfully when blocked.

The architect does **not** code by default.

### 12.2 Worker

The worker must:
- land one seam or one blocker artifact;
- stay within allowed surfaces;
- verify with real tests and `git diff --check`;
- not widen scope;
- not add architecture that the packet did not authorize.

### 12.3 One-seam rule

Every implementation slice must map to exactly one implementation phase/sub-phase and one exact seam.
No “continue the port” prompts.
No “implement the core” prompts.
No multi-host implementation slices.

---

## 13. Phase map

| Phase | Name | Goal | Initial status |
| --- | --- | --- | --- |
| 0 | Packet lock and repo authority | make the packet official in the blank repo | open |
| 1 | Readiness gate and shared-state closure | close `W_t`, role-view, wake, mode/gating, naming, and scoring-separation gaps | open |
| 2 | Repo skeleton and test scaffold | create the minimal package and test layout | open |
| 3 | Core typed substrate | implement lifecycle, observation, environment, support, commitment types, and error surfaces | open |
| 4 | Narrow v1 standard-library port | port machine-readable carrier, provenance helpers, thin event normalization | open |
| 5 | Core dispatch, commitment path, and minimal evidence harness | implement fast paths, wake law, error handling, certification lattice, realization, and minimal eval schema | open |
| 6A | Reference-host driver observe/bind slice | normalize one host and prove cheap-path integration | open |
| 6B | Reference-host commitment-path slice | prove candidate and full commitment paths end to end on one host | open |
| 6C | Reference-host neutral-only vertical slice | one host works end to end with neutral-only SRE and budget targets | open |
| 7A | Active SRE role views and neutral dominance | land role views, discrete scoring, and pass-through default | open |
| 7B | SRE uncertainty and brake | land uncertainty classes, brake, and anti-thrashing policy | open |
| 7C | SRE branch/goal and opportunity specialization | land branch control and direct host-opportunity use | open |
| 8 | Second host port | prove the architecture survives a structurally different host | open |
| 9 | Third host port | add the orchestration-heavy host honestly | open |
| 10 | Full evidence harness and contradiction packet | recreate v1’s strongest evidence discipline under v2 | open |
| 11 | AUX scaffolds | land geometry/offline shells with explicit off/default/deferred status | open |
| 12 | First implementation proof packet | current-pair style packet proving what is and is not earned | open |
| 13 | Experimental mediation (optional) | experimental SRE extension, off by default, only after active loop is stable | descoped |

---

## 14. Detailed phase plan

### Phase 0 — Packet lock and repo authority

#### Goal
Make the 3-doc packet and the v1 port determination the only active implementation authority.

#### Substeps
1. Add the minimal `AGENTS.md` update for architect/worker workflow.
2. Add the v2 packet docs, `V1_CODE_PORT_DETERMINATION.md`, and this implementation plan to active authority.
3. Add one tiny status board only if the repo truly needs one.
4. Record maturity tags:
   - Core = active
   - SRE = active; mediation experimental/off-by-default
   - AUX = geometry evaluation-first; offline deferred
   - v1 port determination = active porting authority

#### Example seam
- Add `AGENTS.md` plus a single authority section that points to these exact five docs and nothing else.

#### Specific checks
- no code yet
- no governance sprawl
- one canonical packet authority set only
- `V1_CODE_PORT_DETERMINATION.md` is physically present in the repo

#### Done means
- the blank repo has one clear v2 authority set
- the architect can select seams without reopening packet philosophy

#### Anti-drift
- do not add implementation heuristics to AGENTS
- do not create parallel packet docs

---

### Phase 1 — Readiness gate and shared-state closure

#### Goal
Close the readiness issues in Section 9.

#### Preferred output
One small authority note and/or thin code-facing type surface that defines:
- `W_t` families and write boundaries
- minimum role-view software shapes
- mode/gating reference content
- commitment wake reference heuristic and decision table
- naming/notation cleanup
- goal-term separation rule

#### Example seam
- Land `docs/internal/CORTEX_V2_IMPLEMENTATION_READINESS_NOTE.md` and optionally a tiny `support.py` / `roles.py` type scaffold that reflects the note.

#### Specific checks
- `W_t` is no longer a free variable
- wake logic is explicit enough to implement and test
- role views are operational enough for code, but still representation-flexible
- no policy math broadening

#### Done means
- workers can implement Core and SRE without inventing shared state ad hoc

#### Anti-drift
- do not move scoring law into core
- do not implement runtime loops yet

---

### Phase 2 — Repo skeleton and test scaffold

#### Goal
Land the minimal package skeleton, test layout, and integration-test placeholders so implementation slices have stable homes.

#### Substeps
1. Create the package boundaries from Section 6.
2. Create empty or thin module shells only where the next phases need them.
3. Seed unit and integration test layout.
4. Seed minimal eval/harness schema files sufficient for later contradiction-preserving packets.

#### Example seam
- Add package directories, `__init__` files, import smoke tests, and `tests/integration/test_pipeline_smoke.py` placeholders.

#### Specific checks
- no large code bodies yet
- no accidental architecture in empty shells
- tests/imports run cleanly

#### Done means
- package boundaries exist
- the next worker seams can land directly into stable modules

#### Anti-drift
- do not implement host-specific doctrine in common modules
- do not add AUX runtime dependencies

---

### Phase 3 — Core typed substrate

#### Goal
Implement the minimal typed substrate of the core, including explicit error surfaces.

#### Main surfaces
- `cortex/core/lifecycle.py`
- `cortex/core/envelopes.py`
- `cortex/core/observation.py`
- `cortex/core/environment.py`
- `cortex/core/support.py`
- `cortex/core/commitments.py`
- `cortex/core/errors.py`

#### Substeps
1. Implement lifecycle/event envelope types.
2. Implement observation bundle types.
3. Implement bounded executive environment view vs commitment environment handle.
4. Implement support snapshot types.
5. Implement commitment candidate, provenance manifest, boundary state, and certification lattice.
6. Implement error and degradation state carriers.
7. Keep the event-local certification firewall type-visible.

#### Example seam
- Implement `LifecycleEventEnvelope`, `ObservationBundle`, and `CommitmentStatus` plus tests proving the executive cannot call the certifier directly.

#### Specific checks
- the executive cannot directly call certification with its own state
- environment access is split correctly
- support state is typed and bounded
- host/event tags remain extensible
- error states exist without smuggling host doctrine into the core

#### Done means
- the core typed substrate is real and testable

#### Anti-drift
- do not add scoring law
- do not add host-driver behavior yet beyond abstract types

---

### Phase 4 — Narrow v1 standard-library port

#### Goal
Import the small v1 library that genuinely fits v2.

#### Main surfaces
- `cortex/core/commitment_payload.py`
- `cortex/core/commitment_extract.py`
- `cortex/core/provenance.py`
- `cortex/drivers/common_normalization.py`

#### Substeps
1. Port `stop_payload.py` behavior.
2. Port the narrow carrier-resolution slice from `stop_contract.py`.
3. Port the provenance helpers.
4. Port thin event normalization.
5. Rewrite leaf evidence-reference utilities where useful.

#### Example seam
- Port `payload.stop_fields` extraction with strict native/structured precedence and bounded trailer fallback.

#### Specific checks
- v1 architecture is not being reintroduced
- trailer parsing remains bounded fallback
- machine-readable carriers remain preferred
- provenance remains downward and host-observable

#### Done means
- the strongest battle-proven v1 primitives are available inside v2 core/driver code

#### Anti-drift
- do not port `StopVerdict` stack
- do not port old adapter retry doctrine

---

### Phase 5 — Core dispatch, commitment path, and minimal evidence harness

#### Goal
Implement the cheap path / candidate path / full commitment path split, plus minimal contradiction-preserving evidence schemas.

#### Main surfaces
- `cortex/core/lifecycle.py`
- `cortex/core/commitment_extract.py`
- `cortex/core/provenance.py`
- `cortex/core/boundaries.py`
- `cortex/core/certification.py`
- `cortex/core/realization.py`
- `cortex/core/errors.py`
- `cortex/eval/artifacts.py`
- `cortex/eval/harness.py`

#### Substeps
1. Implement the cheap non-commit path.
2. Implement the candidate-bearing path.
3. Implement the full commitment path.
4. Implement the commitment wake law and coding-lane decision table.
5. Implement canonical error/degradation flows.
6. Implement commitment realization states (`certified`, `uncertified`, `blocked`).
7. Define minimal artifact schemas for:
   - event trace
   - current-pair fragment
   - blocker fragment
8. Seed integration tests from Section 11.

#### Example seam
- Add a test where a `write_file` proposal enters the candidate-bearing path, and a later completion event plus passing test result enters the full commitment path.

#### Specific checks
- non-commit events skip heavy provenance
- candidate extraction does not force certification when no commitment is on the line
- commitment wake is neither too eager nor too lax on the first target domain
- certification is still downward-provenance dominated
- minimal evidence artifacts already preserve contradictions rather than smoothing them away

#### Done means
- the core runtime path is real, sparse, measurable, and testable
- minimal evidence schema exists before the first host vertical slice closes

#### Anti-drift
- do not fold SRE policy into the core dispatch
- do not make every event run the full path
- do not wait until late phases to introduce evidence artifacts

---

### Phase 6A — Reference-host driver observe/bind slice

#### Goal
Normalize one host and prove cheap-path integration only.

#### Preferred host
Claude unless live repo truth forces another first host.

#### Substeps
1. Land the reference host driver.
2. Normalize host events into observation bundles.
3. Bind bounded executive environment view and commitment environment handle.
4. Prove cheap-path dispatch on real and synthetic host-shaped events.

#### Example seam
- Normalize a Claude tool-intercept read-only event and prove it runs only the cheap path with neutral realization.

#### Specific checks
- no certification unless wake/candidate conditions are met
- no hidden host doctrine in common modules
- cheap-path budget is measured on the reference lane

#### Done means
- one host can reach `Observe -> BindEnv -> Snapshot -> Select^soft -> Realize^soft` honestly

#### Anti-drift
- do not add active SRE policy yet
- do not broaden into all hosts

---

### Phase 6B — Reference-host commitment-path slice

#### Goal
Prove candidate-bearing and full commitment paths end to end on the reference host.

#### Substeps
1. Run candidate-bearing events through extraction without premature full provenance gather.
2. Run full commitment events through extraction, provenance, boundary check, certification, and commitment realization.
3. Verify explicit degraded/blocked behavior on malformed or unsupported commitment surfaces.

#### Example seam
- On Claude, a durable write followed by a task-complete event triggers a full commitment path with downward provenance from changed files plus test result.

#### Specific checks
- commitment wake works on real host events
- candidate-bearing path and full path are distinct in practice
- degradation and contradiction states propagate to artifacts

#### Done means
- one host proves the commitment path is implementable end to end

#### Anti-drift
- do not add active arbitration yet
- do not smooth over unsupported host events

---

### Phase 6C — Reference-host neutral-only vertical slice

#### Goal
Get one host fully through the core with a neutral-only SRE and pass the initial latency gates.

#### Substeps
1. Keep SRE fixed to neutral-only/pass-through.
2. Run the full reference lane end to end on the reference host.
3. Record first current-pair fragment and any blocker/degradation fragments.
4. Measure cheap-path / candidate-path / commitment-path budgets.

#### Example seam
- Run the bounded `normalize_port` reference task on Claude with neutral-only SRE and record one truthful current-pair fragment.

#### Specific checks
- no active SRE intervention logic yet
- host-native realization is real, not fake-uniform
- commitment path works on actual host events
- latency budgets are measured and recorded

#### Done means
- one reference host proves the packet is implementable end to end with neutral-only SRE

#### Anti-drift
- do not jump to all-host parity
- do not add arbitration yet

---

### Phase 7A — Active SRE role views and neutral dominance

#### Goal
Land the active SRE role views, discrete scoring, and neutral-by-default behavior.

#### Main surfaces
- `cortex/sre/roles.py`
- `experimental/sre/policy.py`
- `experimental/sre/allocation.py`
- `experimental/sre/opportunities.py`

#### Substeps
1. Implement recoverable role views in software.
2. Implement discrete reference control scoring / ranking.
3. Implement neutral-dominance/default pass-through.
4. Implement host-native opportunity specialization.
5. Enforce goal-term separation (`q_goal_main` vs `q_goal_branch`).

#### Example seam
- If the host surfaces a cheap native context lookup opportunity but bounded advantage over neutral is absent, the selected family must still be `neutral`.

#### Specific checks
- all scoring compiles to bounded heuristics / tables / estimators, not literal calculus
- `neutral` wins when bounded advantage is absent
- executive can read bounded environment state but cannot certify truth
- direct host opportunities can short-circuit abstract detours when lawful

#### Done means
- the active SRE can rank soft-control families discretely without violating core boundaries

#### Anti-drift
- do not enable uncertainty/brake yet
- do not make SRE depend on AUX

---

### Phase 7B — SRE uncertainty and brake

#### Goal
Land uncertainty classes, brake state, and anti-thrashing policy.

#### Main surfaces
- `experimental/sre/uncertainty.py`
- `experimental/sre/brake.py`

#### Substeps
1. Implement classwise uncertainty bands and spike flags.
2. Implement `quiescent / guarded / latched` brake states.
3. Implement discrete brake-pressure update logic.
4. Enforce no-threshold-collapse and no commitment relaxation.

#### Example seam
- Repeated contradictory test results raise a spike, move the brake to `guarded` or `latched`, and suppress repeated high-cost retries.

#### Specific checks
- brake suppresses thrashing without lowering commitment standards
- uncertainty affects soft-control policy only
- latched state can force neutral / escalate when warranted

#### Done means
- SRE can slow, halt, or redirect bad local loops without becoming a truth court

#### Anti-drift
- do not lower commitment thresholds
- do not use AUX geometry in the active path

---

### Phase 7C — SRE branch/goal and opportunity specialization

#### Goal
Land branch lifecycle control and main-goal preservation.

#### Main surfaces
- `cortex/sre/branching.py`
- `experimental/sre/policy.py`
- `experimental/sre/opportunities.py`

#### Substeps
1. Implement branch open / suspend / resume / merge / abandon.
2. Implement pending-goal discipline and resume anchors.
3. Implement branch budgets.
4. Connect branch decisions to direct host opportunities where lawful.

#### Example seam
- After one failed strategy branch, the SRE suspends it, preserves the main task, and records a resume anchor instead of looping locally.

#### Specific checks
- branch actions do not erase the main task
- resume anchors remain explicit
- branch explosion is bounded
- opportunity specialization remains host-native

#### Done means
- the reference executive can preserve goals while exploring bounded alternatives

#### Anti-drift
- do not enable mediation yet
- do not make branching dependent on AUX memory

---

### Phase 8 — Second host port

#### Goal
Prove the architecture survives a host with different lifecycle behavior.

#### Preferred target
Gemini.

#### Substeps
1. Land the Gemini driver.
2. Bind synchronous callback semantics honestly.
3. Verify that the same core + active SRE meaning still holds under this host.
4. Preserve explicit degradation where surfaces differ.

#### Example seam
- A Gemini synchronous callback event triggers the cheap path and remains within the cheap-path budget envelope or records a performance blocker honestly.

#### Specific checks
- no fake parity
- no hidden host doctrine in common modules
- no heavy-path regression on cheap events caused by callback model differences

#### Done means
- v2 is no longer “Claude-only by accident”

#### Anti-drift
- do not rewrite core for one host’s quirks

---

### Phase 9 — Third host port

#### Goal
Add the orchestration-heavy host honestly.

#### Preferred target
OpenAI.

#### Substeps
1. Land the OpenAI driver.
2. Use App Server / streamed event reconstruction where necessary.
3. Keep native transport precedence.
4. Preserve blocked/degraded truth where the host surface is weaker or different.

#### Example seam
- Reconstruct an OpenAI streamed event sequence into a valid observation bundle without pretending unsupported surfaces are native.

#### Specific checks
- no fake native parity claims
- no assisted/bridge doctrine smuggled into core law

#### Done means
- the packet has survived all three current host families

#### Anti-drift
- do not let OpenAI path redesign the whole architecture

---

### Phase 10 — Full evidence harness and contradiction packet

#### Goal
Recreate the strongest discipline from v1: contradiction-preserving evaluation.

#### Main surfaces
- `cortex/eval/harness.py`
- `cortex/eval/artifacts.py`
- `cortex/eval/packets.py`
- tests around evaluation schema

#### Substeps
1. Extend minimal artifact schemas into full current-pair / blocker / withheld packet logic.
2. Define truthful-withheld packet logic.
3. Implement host contradiction preservation.
4. Recreate a minimal shared-harness discipline.
5. Attach performance evidence and degradation evidence to packet publication.

#### Example seam
- Publish a packet where one host is current, one is degraded, and one is blocked, without smoothing the differences.

#### Specific checks
- no smoothing over mixed/degraded outcomes
- current packet can say “not yet earned” honestly
- evidence discipline is independent of one host’s optimism

#### Done means
- implementation proof can be reported honestly, even while mixed

#### Anti-drift
- do not add marketing summaries
- do not turn evaluation into product theater

---

### Phase 11 — AUX scaffolds

#### Goal
Land the auxiliary shells without making them runtime dependencies.

#### Substeps
1. Land geometry shell as evaluation-first and off by default.
2. Land offline support-memory shell as deferred.
3. Optionally land retrieval baseline shell.
4. Keep all AUX outputs support-only and removable.

#### Example seam
- Land `aux/geometry.py` with no active runtime imports from Core or SRE and one evaluation-only smoke test.

#### Specific checks
- no runtime dependency from core or active SRE
- no hidden completion heuristics
- contradiction preservation remains intact

#### Done means
- AUX exists as official but subordinate infrastructure

#### Anti-drift
- do not enable geometry runtime by default
- do not enable offline consolidation in the active loop

---

### Phase 12 — First implementation proof packet

#### Goal
Publish the first truthful packet showing what v2 implementation has earned.

#### Substeps
1. Capture one reference-host current pair.
2. Capture additional host statuses honestly.
3. Publish blocker truth for anything still degraded or unearned.
4. Decide what is:
   - landed
   - blocked
   - strong_enough
   - not yet earned

#### Example seam
- Publish the first v2 packet for the coding reference lane with one reference-host current pair and explicit status for the other hosts.

#### Specific checks
- the packet does not overclaim
- mixed reality remains explicit
- the v2 architecture, not v1 nostalgia, is what is being evaluated

#### Done means
- the new repo can tell the truth about its own state

#### Anti-drift
- do not claim product superiority yet unless genuinely earned

---

### Phase 13 — Experimental mediation (optional)

#### Goal
Implement mediation only as a clearly experimental SRE extension after the active loop is stable.

#### Specific checks
- disabled by default
- no core dependency
- no MVP dependency
- must earn lift relative to simpler active SRE policy

#### Done means
- either a clean experimental extension exists, or it remains honestly descoped

#### Anti-drift
- do not move mediation into core or mandatory SRE path

---

## 15. Strong default seam order

Unless live repo truth forces a blocker seam first, the architect should prefer seams in this order:

1. Phase 0 packet lock / AGENTS update
2. Phase 1 readiness gate (`W_t`, wake, role views, mode/gating, naming, goal-term separation)
3. Phase 2 repo skeleton + integration placeholders
4. Phase 3 core typed substrate
5. Phase 4 v1 narrow port
6. Phase 5 core dispatch/certification + minimal evidence schema
7. Phase 6A reference-host observe/bind slice
8. Phase 6B reference-host commitment-path slice
9. Phase 6C reference-host neutral-only vertical slice
10. Phase 7A active SRE role views + neutral dominance
11. Phase 7B uncertainty/brake
12. Phase 7C branch/goal + opportunity specialization
13. Phase 8 Gemini host port
14. Phase 9 OpenAI host port
15. Phase 10 full evidence harness
16. Phase 11 AUX scaffolds
17. Phase 12 first implementation proof packet
18. Phase 13 mediation only if explicitly chosen and justified later

Do **not** skip straight to mediation, geometry runtime, offline learning, or broad host parity.

---

## 16. Verification spine

For every worker seam:
- `git diff --check`
- smallest relevant `pytest` subset
- explicit closeout status: `landed`, `blocked`, `partial`, or `drifted`
- update status board only if earned
- include `PHILOSOPHY_AUDIT`

### Minimum verification expectations by phase

**Phase 0–1**
- docs/authority coherence checks
- no code required unless the seam intentionally creates type scaffolds

**Phase 2–3**
- import/type tests
- core type invariants
- certification firewall tests
- error-carrier smoke tests

**Phase 4–5**
- commitment payload extraction tests
- provenance helper tests
- wake law tests
- certification lattice tests
- integration tests from Section 11
- cheap-path / candidate-path / commitment-path latency measurements on the reference lane

**Phase 6A–6C**
- host driver smoke tests
- normalization tests
- realization-path tests
- contradiction/degradation tests
- reference-host end-to-end current-pair fragment

**Phase 7A–7C**
- neutral-dominance tests
- discrete scoring tests
- uncertainty/brake tests
- branch/resume tests
- bounded-latency checks for SRE overhead

**Phase 8–9**
- host driver smoke tests
- normalization tests
- degradation honesty tests
- no-fake-parity checks

**Phase 10–12**
- artifact schema tests
- packet consistency tests
- blocker/current-pair packet tests

---

## 17. Architect output format

Every architect cycle should return exactly these sections:

1. `SECTION 1 — RECONFIRMED BASELINE`
2. `SECTION 2 — IMPLEMENTATION STATUS BOARD`
3. `SECTION 3 — NEXT-SEAM COMPARISON`
4. `SECTION 4 — WINNER`
5. `SECTION 5 — WORKER PROMPT`
6. `SECTION 6 — ACCEPTANCE CHECK`
7. `SECTION 7 — PLAN / AGENTS / LEDGER SYNC`
8. `SECTION 8 — IMPLEMENTATION CONSEQUENCE`

And end with:

- `CURRENT PHASE: ...`
- `NEXT EXACT SEAM: ...`
- `WORKER PROMPT READY: yes|no`
- `BLOCKED OR NOT: ...`
- `WHY THIS IS THE STRONGEST HONEST NEXT MOVE: ...`

---

## 18. Worker prompt contract

Every worker prompt must include these sections, in order:

1. Repo/workflow lock
2. Governing goal
3. Current phase and exact seam
4. Locked prior wins
5. Canonical packet law
6. Exact success condition
7. Allowed touch surfaces
8. Do-not-drift rules
9. Implementation-or-blocker honesty
10. Verification required
11. Doc/progress sync
12. Closeout requirements

### Canonical packet law to preserve in worker prompts

At minimum, every worker prompt must preserve:

- Core / SRE / AUX separation
- integrity microkernel smallness
- event-local certification firewall
- observation vs environment split
- native-realization precedence
- degradation / contradiction honesty
- mediation experimental/off-by-default
- geometry evaluation-first/runtime-off-by-default
- offline consolidation deferred
- v1 standard library as library, not architecture

---

## 19. Phase-specific gates

### Gate A — Before Core coding
Must be true:
- packet authority locked
- readiness gate landed
- package boundary known

### Gate B — Before host drivers
Must be true:
- core typed substrate landed
- v1 narrow port landed
- core dispatch/certification landed
- minimal evidence schema landed
- integration surfaces from Section 11 are live

### Gate C — Before active SRE policy
Must be true:
- one reference host vertical slice works with neutral-only SRE
- commitment path is real
- degradation truth is visible
- latency budgets are measured on the reference lane

### Gate D — Before second/third host ports
Must be true:
- active SRE landed on the reference host
- no hidden core/SRE boundary leaks remain

### Gate E — Before AUX runtime experiments
Must be true:
- core + active SRE loop is stable
- contradiction-preserving evaluation harness is live
- runtime profiling says there is spare budget

### Gate F — Before first public implementation proof packet
Must be true:
- at least one host has a real current-pair artifact
- other hosts are either current, degraded, or blocked with explicit reasons
- no deferred module is pretending to be active

---

## 20. What not to do

1. Do not port v1 architecture.
2. Do not let host-specific compensation enter the core.
3. Do not implement all three hosts at once.
4. Do not let mediation become MVP runtime doctrine.
5. Do not let geometry become a hidden truth court.
6. Do not let offline memory publish hidden completion heuristics.
7. Do not let the SRE act by default without bounded advantage over neutral.
8. Do not let every event pay full provenance/certification cost.
9. Do not create a second packet authority set.
10. Do not treat mixed/degraded host evidence as an embarrassment to smooth over.

---

## 21. Suggested first worker seams

If the blank repo truly starts empty, the strongest early seams are:

1. **Minimal AGENTS.md packet/workflow authority update**
2. **Readiness gate artifact** resolving `W_t`, role views, wake law, mode/gating, naming, and goal-term separation
3. **Package skeleton + test scaffold + integration placeholders**
4. **Core typed substrate types + error carriers**
5. **Port `stop_payload.py` into `commitment_payload.py`**
6. **Port provenance helpers into `provenance.py`**
7. **Implement core dispatch with explicit fast paths + commitment wake table**
8. **Land minimal evidence schemas and integration tests**
9. **Land Claude observe/bind slice**
10. **Land Claude commitment-path slice**
11. **Land Claude neutral-only vertical slice**

Do not skip to SRE allocation, mediation, geometry, or OpenAI event reconstruction before those seams are landed.

---

## 22. Final recommendation

The implementation strategy is:

> **Build the smallest event-native certifying core first, seed contradiction-preserving evidence early, then wrap the core in a neutral-by-default reference executive, then broaden hosts, then publish truthful current/blocker packets, and only then attach optional auxiliary cognition.**

That is the cleanest way to exploit the battle-proven parts of v1 without importing its architecture, the cleanest way to avoid v1’s proof gauntlet, and the cleanest way to give the architect/auditor a sequence of narrow, defensible seams to supervise.
