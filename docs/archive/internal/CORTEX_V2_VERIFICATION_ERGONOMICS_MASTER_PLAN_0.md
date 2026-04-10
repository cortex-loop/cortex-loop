# CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0

Surface: internal

Status: canonical follow-on master plan for non-feature verification ergonomics (`active`)
Date: 2026-03-21
Primary objective: improve **verification usability, reproducibility, coverage visibility, correspondence auditability, and evidence revalidation ergonomics** for the landed Cortex v2 MVP **without changing Core / SRE / AUX behavior**.

Active authority this plan assumes:
- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
- `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
- `docs/internal/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`
- `docs/internal/CORTEX_V2_PHASE_GATES_2.md`
- `docs/experimental/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md`
- `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md`
- `AGENTS.md`

This plan is a **follow-on campaign**, not an extension of the feature roadmap that ended at the current justified v2 boundary.

---

## Current Campaign State

- `E1` is effectively landed:
  - `pytest.ini` exists,
  - `Makefile` exposes the canonical and smoke bundles,
  - `make seam-preflight` now blocks new seam work on `main` or a tracked-dirty worktree,
  - and `docs/internal/CORTEX_V2_LOCAL_VERIFICATION.md` records the repo-local entry points.
- `E2` is effectively landed:
  - `.coveragerc` exists,
  - `make coverage` exists,
  - and the first committed baseline artifact is now recorded.
- `E3` is materially landed for current scope:
  - mechanical correspondence checks already exist for contract, Core, ports, SRE, and periphery surfaces.
- `E4` is effectively landed for current scope:
  - the reference-lane running example now has shared outcome helpers, shared contradiction/degradation assertions, and shared neutral verification helpers,
  - and no broader gate-test dedup is promoted without a separate re-audit.
- `E5` is materially landed for current scope:
  - packet-example and latency evidence revalidation paths are documented,
  - repo-local entry points exist in `Makefile`,
  - and the phase-gate ledger already treats those evidence surfaces as landed.
- `E6` remains open.

---

## 0. One-paragraph verdict

The current Cortex v2 MVP is complete at the presently justified boundary. The next honest work is not new architecture or new runtime behavior. It is **verification ergonomics**: make the landed system easier to verify, easier to reproduce, easier to inspect, easier to audit against the packet, and easier to evolve later without losing correspondence or contradiction-preserving evidence. This campaign must not silently reopen feature work. If a seam changes Core / SRE / AUX behavior rather than verification usability, it is the wrong campaign.

---

## 1. Prime directive

Improve the **verification layer around the landed MVP** without moving the product boundary.

That means:
- no new Core semantics
- no new SRE semantics
- no AUX activation
- no mediation implementation
- no host-parity expansion
- no hidden packet reinterpretation

The success condition is not “more tests exist.”
The success condition is:
- one reproducible local verification surface,
- one reproducible coverage surface,
- one reproducible evidence revalidation surface,
- one reproducible correspondence-audit surface,
- and no behavior drift.

---

## 2. Campaign type and scope

### 2.1 This is a non-feature campaign

Allowed:
- repo-local test runner ergonomics
- repo-local coverage ergonomics
- fixture and helper cleanup that reduces verification duplication
- evidence revalidation and carefully-scoped regeneration tooling
- correspondence-audit tooling
- report/packet consistency tooling
- behavior-preserving deduplication only when directly justified by verification ergonomics

Not allowed:
- Core dispatch/certification logic changes
- SRE policy changes
- AUX runtime activation
- mediation work
- geometry runtime work
- offline consolidation work
- new host behavior
- new product claims

### 2.2 Supporting evidence sources

Use as truth anchors:
- `docs/internal/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
- `docs/internal/CORTEX_V2_PHASE_GATES_2.md`
- `docs/experimental/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md`
- `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md`
- `docs/internal/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

These are verification artifacts, not optional commentary.

---

## 3. Guiding example

Every phase in this campaign should stay grounded in one running example:

### Reference lane example
- one cheap-path reference-host event
- one candidate-bearing reference-host event
- one full-commitment reference-host event
- one truthful packet/publication example
- one latency evidence example
- one contradiction-preserving example

This campaign should make those six surfaces:
- easy to rerun,
- easy to inspect,
- easy to compare,
- and hard to falsify accidentally.

If a seam cannot explain how it improves verification around this running example, it is probably not a verification-ergonomics seam.

---

## 4. Global anti-drift rules

- Do not change packet authority.
- Do not reinterpret the closeout note as permission for new features.
- Do not change Core / SRE / AUX semantics unless the seam is explicitly reclassified out of this campaign.
- Do not weaken contradiction preservation to make reporting prettier.
- Do not weaken latency gates to make verification easier.
- Do not weaken the math-to-code correspondence artifact into vague ownership prose.
- Do not introduce CI-only logic that cannot be reproduced locally.
- Do not add a second parallel test taxonomy if the existing unit/integration/gate surfaces are sufficient.
- Do not add broad cleanup unrelated to verification ergonomics.
- Do not deduplicate runtime code unless the verification benefit is explicit and the seam proves behavior preservation.

---

## 5. Success metrics

The campaign is successful when all of the following are true:

1. A new contributor can run the canonical verification bundle from the repo with one documented local command sequence.
2. Coverage can be generated from the repo with repo-local configuration and documented scope.
3. The reference lane packet example and latency evidence can be revalidated or regenerated through documented repo-local commands.
4. The math-to-code correspondence surface can be mechanically checked enough to catch drift in load-bearing objects.
5. The contradiction-preserving gate ledger remains current and reproducible.
6. No behavior drift is introduced.

---

## 6. Phase order

### E0 — Campaign lock and authority sync

#### Goal
Make this campaign explicit and prevent accidental reopening of the feature roadmap.

#### Done means
- the current closeout/sync seam is landed
- the current implementation master plan is marked completed at the justified boundary
- this plan is added as the active follow-on plan for non-feature verification ergonomics
- architect workflow knows this is a separate campaign

#### Anti-drift
- no runtime code changes
- no test harness widening yet
- no new packet claims

---

### E1 — Repo-local verification substrate

#### Goal
Make the landed verification surfaces runnable and discoverable from repo-local configuration.

#### Required outcomes
- repo-local pytest configuration
- stable marker taxonomy only if needed for the existing suite
- one documented canonical local verification bundle
- one documented smaller smoke bundle
- no behavior changes to the system under test

#### Preferred surfaces
- `pytest.ini`
- one small local entry point such as `Makefile`, `justfile`, or `scripts/verify.py`
- minimal docs update for command entry points

#### Done means
- a contributor can run unit + integration + smoke from the repo without reconstructing commands from status notes
- the canonical bundle matches the landed closeout scope
- local reproducibility no longer depends on operator memory

#### Anti-drift
- do not add coverage here unless required for config coherence
- do not change test semantics
- do not add CI yet unless it is strictly needed for local reproducibility
- do not introduce project metadata unrelated to verification ergonomics if `pytest.ini` plus one small entry point is enough

---

### E2 — Coverage baseline ergonomics

#### Goal
Add repo-local coverage generation without changing the closeout truth.

#### Required outcomes
- repo-local coverage configuration and command are already landed
- one documented coverage command and the minimal local prerequisite needed to run it
- one committed baseline artifact built from live repeated local runs
- explicit statement of what is and is not covered
- zero reinterpretation of MVP completeness based on first coverage numbers

#### Done means
- coverage can be generated locally using the landed repo-local configuration plus documented local prerequisites
- the output is stable enough to use as future hygiene evidence
- the config/command layer and the first committed baseline artifact are both landed

#### Anti-drift
- do not turn coverage into a new feature gate immediately
- do not fake coverage precision
- do not widen the codebase just to make percentages prettier

---

### E3 — Correspondence audit surface

#### Goal
Make the math-to-code correspondence artifact mechanically useful.

#### Required outcomes
- one repo-local checker or test surface for landed correspondence rows in scope
- explicit treatment of:
  - canonical object exists
  - canonical module home exists
  - read/write/test surfaces exist where promised
- failure mode must be drift-detecting, not philosophy-policing

#### Done means
- landed rows can be checked mechanically enough to catch missing object homes or moved code homes
- scope is prioritized in this order:
  - Core
  - SRE
  - drivers
  - eval
  - AUX

#### Anti-drift
- do not force a brittle one-to-one parser over every prose row
- do not encode packet architecture in tests more narrowly than the packet itself
- do not expand this into a static-analysis research project

---

### E4 — Integration fixture ergonomics

#### Goal
Reduce duplication and friction in the existing integration and gate tests.

#### Required outcomes
- helper fixtures/builders for the reference lane
- reusable event/factories for:
  - cheap-path
  - candidate-bearing
  - full-commitment
- helpers for contradiction/degradation assertions
- no behavior changes to the reference lane itself

#### Done means
- reference-lane and gate tests become easier to extend without changing what they assert

#### Anti-drift
- do not generalize prematurely to all hosts if the reference lane can carry the helper model
- do not rewrite working tests just for style

---

### E5 — Evidence revalidation ergonomics

#### Goal
Make the key evidence artifacts reproducible from code, not only from one historical landing.

#### Required outcomes
- one documented path to revalidate first, then optionally regenerate:
  - `CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md`
  - `CORTEX_V2_LATENCY_EVIDENCE_2.md`
- relevant phase-gate rows
- clear distinction between:
  - revalidate against committed doc
  - produce candidate refreshed evidence without auto-overwriting
  - regenerate exactly only when explicitly requested

#### Done means
- the repo has a stable, documented mechanism for checking whether committed evidence docs still match the landed system

#### Anti-drift
- do not auto-rewrite evidence docs on normal test runs
- do not overwrite contradiction-preserving evidence silently
- do not let regeneration logic mutate packet authority or gate status directly

---

### E6 — Optional behavior-preserving deduplication

#### Goal
Only after E1–E5, reduce duplicated verification-adjacent code if it materially lowers maintenance burden.

#### Candidate areas
- host commitment composition modules
- host neutral-only modules
- shared verification helpers

#### Done means
- behavior-preserving dedup is demonstrated by the canonical verification bundle
- no packet semantics changed

#### Anti-drift
- if the seam smells like runtime redesign, stop
- do not let dedup become architecture work in disguise

---

## 7. Cross-phase gates

### Gate VE-A — No behavior drift

Must remain true in every phase.

Evidence:
- canonical verification bundle still passes
- reference lane packet example still matches or truthfully revalidates
- latency evidence remains within current committed targets unless explicitly re-measured and recorded

### Gate VE-B — Local reproducibility

Must close by E1.

Evidence:
- repo-local commands documented
- repo-local config present
- no dependence on operator memory for canonical bundles

### Gate VE-C — Correspondence drift detection

Must close by E3.

Evidence:
- landed correspondence rows in scope have a real verification surface
- missing canonical code homes are detectable

### Gate VE-D — Evidence reproducibility

Must close by E5.

Evidence:
- reference lane packet example and latency evidence can be revalidated or regenerated through documented repo-local paths

---

## 8. Preferred seam order inside phases

### E0
- E0A closeout sync
- E0B campaign registration

### E1
- E1A repo-local pytest config
- E1B canonical verify command(s)
- E1C smoke command(s) and docs

### E2
- E2A coverage config and prerequisite note
- E2B coverage command and docs
- E2C optional first baseline artifact

Current next-work note:
- E1 is effectively complete.
- E2 is effectively complete.
- E4 is effectively landed for current scope.
- E5 is materially landed for current scope.
- post-`E4` re-audit is complete.
- no `E6` seam is promoted at this time.

### E3
- E3A landed Core correspondence checks
- E3B landed SRE correspondence checks
- E3C landed driver/eval/AUX correspondence checks if justified

### E4
- E4A reference-lane event fixture builders
- E4B contradiction/degradation assertion helpers
- E4C gate-test dedup helpers

### E5
- E5A packet example revalidation path
- E5B latency evidence revalidation path
- E5C optional candidate regeneration helpers

### E6
- E6A neutral-module dedup if justified
- E6B commitment-composition dedup if justified

One seam at a time still applies.

---

## 9. Verification spine

Every seam in this campaign should declare the smallest honest verification set from this spine:

### Minimum
- `git diff --check`
- relevant unit tests
- `git status --short --untracked-files=all`

### Campaign canonical bundle
- `python3 -m pytest tests/unit`
- `python3 -m pytest tests/integration`
- `python3 -m pytest tests/unit/test_import_smoke.py`
- any new verification-ergonomics test surface added by this campaign

### Additional when relevant
- coverage command
- packet-example revalidation command
- latency-evidence revalidation command
- correspondence-check command

No seam should run more than necessary, but any seam that touches shared verification plumbing must re-earn the canonical bundle.

### 9.1 Parent acceptance discipline

The parent thread must independently re-audit every worker seam before accepting it.

Minimum parent acceptance law:
- classify the seam risk before acceptance
- read the full touched files, not only the diff hunk, when the seam changes verification logic, evidence interpretation, or repo-local verification entry points
- rerun the worker's claimed verification independently
- stress the seam at its most likely failure mode before calling it `landed`

Risk-shape guidance:
- deterministic code/doc seam:
  one honest rerun may be enough if the seam has no timing or environment sensitivity
- parser/doc-sync seam:
  parent should read the source doc plus the parser/checker code and try at least one adversarial rerun
- timing or environment-sensitive seam:
  one clean rerun is not enough; acceptance requires repeat-stability proof through repeated direct reruns and repeated repo-local entry-point reruns
- shared verification-plumbing seam:
  re-earn the campaign canonical bundle after the seam-specific checks

No next worker prompt should be issued until the current seam has been either rejected or accepted and committed.

---

## 10. Running example requirements

Every phase should use the same running example set unless the seam explicitly justifies otherwise:
- reference-host cheap path
- reference-host candidate-bearing path
- reference-host full commitment path
- contradiction-preserving packet example
- latency evidence rows

This keeps the campaign grounded in one stable proof surface rather than diffuse aspirations.

---

## 11. Architect selection rules

When choosing the next seam in this campaign, prefer:
1. the smallest seam that improves verification reproducibility
2. then the smallest seam that improves drift detection
3. then the smallest seam that reduces verification duplication without behavior change

Do not choose:
- new feature seams
- broad refactors
- multi-host behavioral changes
- mediation work
- geometry runtime activation
- offline consolidation activation

If a seam seems to require those, it is the wrong campaign.

---

## 12. Worker prompt style for this campaign

Every worker prompt should include:
- explicit statement that this is a **non-feature verification-ergonomics seam**
- exact touched files
- exact existing verification surfaces to preserve
- explicit anti-drift rules against behavior change
- explicit statement of whether the seam must re-earn the canonical bundle
- closeout fields for:
  - verification consequence
  - drift consequence
  - evidence consequence
  - correspondence consequence (if relevant)

---

## 13. Current hold note

`E2C` is now landed.
`E5` is materially landed for current scope.

`E4` is now landed for current scope.

### Post-`E4` re-audit result

- Remaining reference-local duplication still exists:
  - mainly repeated reference mediation scorecard-selection builders in uncertainty/thrash episode builders,
  - plus a small number of empty-ref and candidate-bearing assertions in thrash-only helpers.
- That remaining duplication is **not yet material enough** to justify `E6`:
  - the live overlap is narrow,
  - the current reference helper surface already covers the highest-value repeated outcome checks,
  - and further dedup would start trading locality and failure readability for modest line-count savings.
- A future `E6` seam could still stay verification-local and behavior-preserving:
  - but only if a later maintenance pass shows a larger repeated reference-only helper shape than the repo currently has.
- No `E6` seam is promoted from this re-audit.

No broader refactor is promoted from this slice.
That follow-on choice must remain non-feature, behavior-preserving, and verification-first.

---

## 14. End condition

This campaign is complete when:
- local verification is reproducible,
- coverage is reproducible,
- correspondence drift is checkable,
- evidence docs are revalidatable or regenerable under explicit control,
- and no behavior drift has been introduced.

It does **not** need to end in new features.
It should end with a repo that is easier to trust, easier to audit, and easier to evolve later.
