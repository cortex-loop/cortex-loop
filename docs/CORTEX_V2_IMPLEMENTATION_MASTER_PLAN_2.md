# CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2

Status: canonical implementation master plan for the blank-repo Cortex v2 build (`active authority`, build-complete at current justified boundary, subagent-aware)
Date: 2026-03-18
Primary objective: build Cortex v2 as a **lifecycle-first, packet-first internally / host-native externally, executive-first, host-affordance-native system** with a **tiny integrity microkernel**, using only the narrow battle-proven v1 code that fits the new Core / SRE / AUX packet.

Active packet documents:
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`

Supporting implementation/port authority:
- `docs/V1_CODE_PORT_DETERMINATION.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
- `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`

Workflow authority:
- `AGENTS.md`

This plan supersedes the earlier implementation plan wherever they disagree on workflow.

Closeout status:
- the ordered roadmap is complete at the current justified boundary;
- the verified end-state snapshot is recorded in `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`;
- the `_2` packet documents remain the active architectural authority;
- AUX staging remains unchanged: geometry is evaluation-first / runtime-off-by-default, and offline consolidation remains deferred;
- mediation remains explicitly unjustified and unstarted unless future measurable lift evidence is earned, as recorded in `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`.

---

## 0. One-paragraph final verdict

Do **not** rebuild v1 in a new repo.
Do **not** start with all hosts, all policy math, or all auxiliary systems live at once.
Do **not** let subagents turn one bounded seam into parallel write chaos.

Build Cortex v2 in the following order:

1. **lock authority and seed subagent scaffolding**;
2. **close the remaining shared free variables** (`W_t`, executive role recoverability, commitment wake heuristics, mode/gating content, notation hygiene);
3. **build the smallest core substrate first**;
4. **port only the narrow v1 standard library that was genuinely battle-proven**;
5. **land one reference-host vertical slice** before broadening host support;
6. **add only active SRE policy next**;
7. **move contradiction-preserving evidence harnessing earlier than broad host rollout**;
8. **keep mediation experimental and AUX off the critical path** until the core/SRE loop is stable.

The architectural success condition is not “all math implemented.”
It is: **a host-native event loop with a tiny certifying microkernel, a neutral-by-default executive, explicit degradation honesty, contradiction-preserving evidence discipline, and a subagent workflow that reduces context pollution without creating multi-writer chaos.**

---

## 1. Prime directive

Build the **smallest runnable Cortex v2** that preserves the packet’s authority boundaries.

That means:
- the **core** owns lifecycle law, commitment extraction/certification, provenance, degradation honesty, the observation/environment split, and the event-local certification firewall;
- the **SRE** owns active executive policy;
- **AUX** remains removable, support-only, and off the MVP critical path.

The v1 archive is a **standard library and evidence source**, not a base architecture.

Subagents are a **workflow optimization**, not a fourth architecture layer.

Archive filename note:
- `cortex/core/boundaries.py`
- `cortex/core/realization.py`
- `cortex/eval/harness.py`

Those archive filenames are **not** active deliverables by default.
If their responsibilities are re-earned under v2, they may land under different code homes.
Missing those exact filenames is not, by itself, a phase-gap finding under this plan.

---

## 2. Subagent strategy

### 2.1 What subagents are for in this repo

Use subagents to keep the parent thread clean and focused on:
- architectural choices
- seam selection
- diff review
- phase/gate truth

Use subagents for:
- archive mining
- packet consistency audits
- host/runtime documentation research
- test/log triage
- one bounded implementation seam once the parent has already selected it

### 2.2 Parent-thread law

The parent thread remains the source of truth for:
- what seam is active
- whether a subagent result is accepted
- whether a phase gate is earned
- whether a blocker is real
- whether a diff lands

Subagents do not set status. They feed the parent.

### 2.3 Single-writer law

At most one workspace-write subagent may be active at once.

Parallel subagents should otherwise be read-only.

If a seam appears to need two concurrent write agents, the seam is too broad and must be split.

### 2.4 Subagent set

The default project-scoped custom agents are:
- `cortex_archivist` — read-only archive/packet miner
- `cortex_packet_auditor` — read-only layer/boundary auditor
- `cortex_host_researcher` — read-only external host/runtime researcher
- `cortex_worker` — one bounded implementation seam

### 2.5 Subagent maturity

- `cortex_archivist`: active
- `cortex_packet_auditor`: active
- `cortex_host_researcher`: active when external docs matter
- `cortex_worker`: active, but only one write-capable instance at a time

### 2.6 Default concurrency

Use:
- max depth = `1`
- max threads = `3`

That is enough for one parent plus a small number of bounded read-heavy children without creating context or approval chaos.

---

## 3. Strong default seam order

Unless live repo truth forces a blocker seam first, the architect should prefer seams in this order:

0A. Packet lock / AGENTS update / subagent scaffolding
0B. Readiness gate (`W_t`, wake, role views, mode/gating, naming, goal-term separation)
1. Repo skeleton + integration placeholders
2. Core typed substrate
3. v1 narrow standard-library port
4. Core dispatch/certification + minimal evidence schema
5. Reference-host observe/bind slice
6. Reference-host commitment-path slice
7. Reference-host neutral-only vertical slice
8. Active SRE role views + neutral dominance
9. Uncertainty / brake
10A. Goal continuity / branch carriers
10B. Host-native opportunity specialization
11A. Gemini observe/bind slice
11B. Gemini commitment-path slice
11C. Gemini neutral-only slice
12A. OpenAI observe/bind slice
12B. OpenAI commitment-path slice
12C. OpenAI neutral-only slice
13. Full evidence harness
14. AUX scaffolds
15. First implementation proof packet
16. Mediation only if explicitly justified and still experimentally warranted

Do **not** skip straight to mediation, geometry runtime, offline learning, or broad host parity.

---

## 4. Phase 0A — Packet lock and subagent scaffolding

### Goal
Make the packet official and land the minimal subagent workflow files.

### Required files
- `AGENTS.md`
- `.codex/config.toml`
- `.codex/agents/cortex_archivist.toml`
- `.codex/agents/cortex_packet_auditor.toml`
- `.codex/agents/cortex_host_researcher.toml`
- `.codex/agents/cortex_worker.toml`

### Done means
- packet authority is explicit
- subagent roles are explicit
- no second workflow doctrine exists outside AGENTS + this plan
- one parent thread can immediately begin bounded subagent-guided implementation

### Anti-drift
- do not start core coding yet
- do not create extra agent files beyond the four named here
- do not encode runtime packet philosophy into agent files beyond what the core docs already authorize

---

## 5. Phase 0B — Readiness gate and shared-state closure

### Goal
Close the implementation free variables before broad coding.

Must resolve:
- `W_t` families and write boundaries
- minimum role-view software shapes
- mode/gating reference content
- commitment wake reference heuristic and coding-lane decision table
- naming / notation cleanup
- goal-term separation rule

### Preferred workflow
Parent may use:
- `cortex_packet_auditor` to check packet/plan consistency
- `cortex_archivist` to mine v1 examples relevant to the free variables

But the parent must land one bounded readiness artifact itself or through one bounded worker seam.

---

## 6. Subagent usage rules by phase

### Phases 0A–0B
Allowed:
- read-only packet audit
- read-only archive mining
Not allowed:
- parallel writing
- host research unless a missing official source blocks the seam

### Phases 1–4
Allowed:
- archive miner for v1 leaf-port references
- packet auditor for boundary checks
- one worker for the chosen write seam
Not allowed:
- multiple concurrent write workers
- host documentation research unless the seam is host-specific

### Phases 5–7
Allowed:
- one write worker
- one read-only test/log triage or auditor subagent in parallel if needed
Not allowed:
- multiple write workers
- multi-host subagent fan-out

### Phases 11–12
Allowed:
- host researcher for Gemini/OpenAI specific docs
- packet auditor for contradiction packet checks
- one write worker
Not allowed:
- parallel multi-host write changes

---

## 7. Integration-test surface (must exist before first host slice closes)

Required early integration tests:
1. cheap-path integration
2. candidate-bearing integration
3. full commitment integration
4. degradation roundtrip
5. firewall integration
6. driver-to-core-to-sre smoke

Subagents may help generate fixtures or triage failures, but the parent must verify final test truth.
Live row-by-row gate status is tracked in `docs/CORTEX_V2_PHASE_GATES_2.md`.
Placeholder tests reserve surfaces, but they do not satisfy this gate.

---

## 8. Latency budgets

Targets apply **excluding host network/model latency and excluding external tool runtime cost**.

- cheap path: median <= 5 ms; p95 <= 20 ms
- candidate-bearing path (without full provenance gather): median <= 15 ms; p95 <= 50 ms
- full commitment path: median <= 75 ms; p95 <= 250 ms
- neutral SRE scoring overhead: median <= 2 ms; p95 <= 10 ms

Subagent orchestration is never an excuse to ignore these budgets.
Defined targets are not the same as measured evidence.
Measurement status is tracked in `docs/CORTEX_V2_PHASE_GATES_2.md`.

---

## 9. Verification spine

Every seam must end with:
- `git diff --check`
- smallest relevant `pytest` subset
- explicit status: `landed`, `blocked`, `partial`, or `drifted`
- `Phase gate check:` listing rows added, updated, or rechecked in `docs/CORTEX_V2_PHASE_GATES_2.md` (or `none`)
- `PHILOSOPHY_AUDIT`
- `Correspondence rows touched:` listing rows added, updated, or confirmed in `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

No load-bearing seam may be marked `landed` if it introduces new mathematical objects or implementation homes without updating the correspondence ledger.
No phase or sub-phase may be marked `landed` if a relevant gate row remains `open`, `partial`, or `drifted` without the handoff explicitly keeping that phase `partial` or `blocked`.

Additional subagent-specific verification:
- parent confirms which subagent outputs were used
- parent confirms no hidden write-capable parallelism occurred
- parent confirms final seam still maps to one exact phase/sub-phase

---

## 10. First-seam recommendation

If the repo is blank except for packet docs and archive material, the strongest first seam is:

**Phase 0A — packet lock and subagent scaffolding**

That means:
1. update `AGENTS.md` to the subagent-aware contract
2. add `.codex/config.toml`
3. add the four project-scoped custom agent TOML files
4. verify the repo now has one explicit workflow doctrine before coding begins

This seam is stronger than jumping straight to code because subagents are only useful if they are constrained before the implementation loop starts.

---

## 11. Final recommendation

Use subagents the way the Codex docs suggest they are strongest:
- to keep noisy work off the main thread
- to parallelize bounded read-heavy work
- to return concise summaries to the parent
- and to avoid multi-writer chaos on write-heavy implementation

For this repo, the winning pattern is:

**parent architect thread + read-only specialist subagents + one bounded write worker**
