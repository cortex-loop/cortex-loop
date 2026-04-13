# CORTEX_V2_AUX_2

Surface: product

Status: canonical **AUX** document for the 3-document Cortex v2 packet (`active boundary`; geometry `evaluation-first / runtime-off-by-default`; offline support publication `evaluation-first / runtime-off-by-default`; runtime consolidation `deferred until active Core/SRE loop is stable`)
Companion documents: `CORTEX_V2_CORE_2.md`, `CORTEX_V2_SRE_2.md`

---

## 0. Purpose

This document defines the official but **removable** auxiliary modules of Cortex v2:

- geometry and evaluation,
- offline consolidation / BMR-like support learning,
- and any future adjunct modules that remain claim-conservative and microkernel-subordinate.

The AUX layer exists to improve:
- retrieval support,
- branch/resume support,
- uncertainty/brake diagnostics,
- contradiction-preserving host priors,
- support-memory compression,
- and evaluation of executive quality.

The AUX layer does **not** exist to:
- certify commitments,
- lower hard boundaries,
- become a second truth court,
- silently flatten host differences,
- or smuggle hidden completion heuristics into runtime behavior.

---

## 1. Layer position and authority

### 1.1 What AUX is

AUX is the official auxiliary layer of Cortex v2.

It is:
- official,
- packet-visible,
- auditable,
- and allowed to contain mathematically rich modules.

It is **not**:
- constitutional kernel law,
- the default owner of executive control,
- or mandatory for minimum lawful runtime behavior.

### 1.2 What AUX owns

AUX owns:
- optional geometry/evaluation machinery,
- optional geometry-derived retrieval and diagnostic support,
- offline support-memory consolidation,
- offline calibration publication,
- optional branch/review/retrieval priors,
- optional host contradiction summaries,
- and optional future adjunct modules that remain subordinate to core and SRE.

### 1.3 What AUX does not own

AUX may not:
- certify or deny commitments,
- define blockedness,
- change hard safety/integrity boundaries,
- redefine provenance sufficiency,
- mutate the valid commitment-status lattice,
- or silently replace SRE policy with hidden learned doctrine.

Those remain owned by:
- **Core** for commitment truth and boundary law,
- **SRE** for active executive control.

### 1.4 Maturity split inside AUX

AUX intentionally contains modules with different activation status.

#### Active as official packet members
- the AUX boundary laws in this document,
- the right for Cortex v2 to carry claim-conservative auxiliary support modules.

#### Evaluation-first / runtime-off-by-default
- geometry/evaluation.
- support-only offline publication and consolidation evaluation.

#### Deferred until the active core/SRE loop is stable
- runtime use of offline consolidation / BMR-like support publication on the control path.

This means the AUX layer is architecturally present now, but not every AUX mechanism is on the critical path for first working v2 runtime behavior.

### 1.5 Mathematical stance

The equations in this document are **architectural invariants and admissible-object definitions**, not a requirement that one exact continuous solver, one exact latent geometry, or one exact Bayesian engine must exist in Python.

AUX math is allowed to be richer than core law because AUX is removable.
That richer math remains lawful only if it stays:
- subordinate,
- auditable,
- cost-visible,
- and claim-conservative.

---

## 2. Governing auxiliary laws

### 2.1 Claim-conservative law

AUX may shape advisory control and support retrieval, but it may not change commitment truth.

Formally, if `Y_t` is the runtime trajectory and `\operatorname{Commit}_c(Y_t)` is the core commitment decision, then for any lawful auxiliary state `A_t^{aux}`:

\[
\operatorname{Commit}_c(Y_t \mid A_t^{aux}) = \operatorname{Commit}_c(Y_t)
\]

unless the same commitment result is already obtainable through lawful core evidence without AUX.

Interpretation:
- AUX may influence soft-control choices,
- AUX may not alter what counts as certified, uncertified, or blocked.

### 2.2 Removability law

Every AUX module must be removable without invalidating:
- the lifecycle-first runtime law,
- the integrity microkernel,
- the event-local certification firewall,
- or the minimum SRE control loop.

If removing an AUX module breaks commitment truth, that module was illegally acting as a hidden core.

### 2.3 Support-only write law

AUX may write only to support-side objects.
It may not write to:
- commitment certifiers,
- commitment extraction semantics,
- hard boundaries,
- or host capability truth.

### 2.4 Contradiction-preserving law

AUX must preserve host contradictions and mixed evidence.
It may not smooth:
- native vs assisted behavior,
- degraded vs available capability,
- row-capturable vs non-row-capturable behavior,
- or contradictory host/runtime outcomes
into one false unified story.

### 2.5 No hidden completion heuristics

AUX may not learn or publish any rule that behaves like:

> “When support state looks enough like this, lower the bar and effectively call it complete.”

Equivalently, there must not exist an auxiliary shortcut:

\[
\operatorname{AuxShortcut}(A_t^{aux}) \Rightarrow \operatorname{Certify}
\]

that bypasses the lawful core commitment path.

### 2.6 No threshold-collapse learning

AUX may shape:
- uncertainty weighting,
- retrieval priors,
- branch priors,
- review priors,
- brake sensitivity,
- host mismatch penalties,
- or other soft-control settings.

AUX may not learn a policy that gradually lowers hard commitment standards merely because more time, more retries, or more repeated exposure has occurred.

### 2.7 Cost-visible law

Every AUX module must expose its own burden:

\[
C_t^{aux} \ge 0
\]

including any combination of:
- compute overhead,
- memory overhead,
- latency,
- extra environment-query cost,
- retrieval/indexing cost,
- or host-visible intervention burden.

AUX modules are unlawful in practice if they create runtime overhead without observable control/evaluation lift.

### 2.8 Domain-general law

AUX must be specified in domain-general terms.
Coding-agent environments are allowed as one important specialization, but the universal AUX language may not assume:
- filesystem-only state,
- command-line-only execution,
- code-diff-only provenance,
- or software-engineering-only branch structure.

Domain-specific environments may specialize AUX through extensions and metadata.

---

## 3. AUX factorization

For runtime `r`, support state `W_t`, executive state `X_t`, and auxiliary state `A_t^{aux}`, define:

\[
\text{AUX}
=
\text{GeomEval}
\oplus
\text{OfflineSupport}
\oplus
\text{FutureAdjuncts}
\]

where:
- `GeomEval` = optional geometry and evaluation support,
- `OfflineSupport` = optional offline support-memory consolidation and publication,
- `FutureAdjuncts` = any later official auxiliary module that remains lawful under Section 2.

---

## 4. Geometry and evaluation

Status: **evaluation-first / runtime-off-by-default**

### 4.1 Purpose

Geometry may be used to improve:
- executive-memory retrieval,
- branch/resume support,
- uncertainty/brake diagnostics,
- mediation diagnostics,
- and evaluation of executive separability or reuse.

It may not:
- certify commitments,
- replace provenance,
- lower hard boundaries,
- or become a hidden adapter policy.

### 4.2 Derived and removable

Geometry must be derived from lawful observations, support state, and executive state.
It may not introduce a second semantic court.
If geometry is disabled, the packet must remain fully lawful.

### 4.3 Runtime-off-by-default law

Geometry is **not** part of minimum live runtime behavior.
Runtime use of geometry must be explicitly enabled and must earn retention by demonstrating control or evaluation lift.

### 4.4 Evaluation-first law

The first use of geometry should be:
- diagnostics,
- evaluation,
- retrieval-shadow experiments,
- branch/resume matching experiments,
- uncertainty/brake analysis.

Promotion into runtime support is allowed only after those uses show clear utility.

### 4.5 Snapshot integration law

The core owns:

\[
\mathcal S_t = \operatorname{Snapshot}(\mathcal O_{t,r},W_t)
\]

AUX may only append or derive additional support by an explicit augmentation step:

\[
\mathcal S_t^{aux} = \operatorname{Augment}^{aux}(\mathcal S_t, A_t^{aux})
\]

AUX may not redefine the core snapshot constructor.

### 4.6 Retention law

A geometry module should remain enabled only if it improves at least one of:
- retrieval usefulness,
- branch/resume fidelity,
- uncertainty/brake diagnostics,
- contradiction-preserving clustering,
- evaluation quality.

Otherwise it should remain disabled or be removed.

---

## 5. Offline consolidation and BMR-like support learning

Status: **support-side evaluation-first / runtime-off-by-default**

### 5.1 Purpose

Offline consolidation exists to improve support-side priors such as:
- retrieval priors,
- review priors,
- branch priors,
- host contradiction summaries,
- uncertainty/brake calibration summaries,
- optional published memory summaries.

It does not exist to mutate commitment truth.

### 5.2 Runtime deferral law

Offline support publication may be evaluated and retained on the support side now.
It is still not on the critical path for first working v2 runtime behavior, and runtime use should remain deferred until:
- the core event loop is stable,
- the active SRE loop is stable,
- support-memory publication has time-separated evaluation evidence rather than same-snapshot smoke evidence,
- and retention is earned without hiding runtime defects.

### 5.3 Support-only publication law

Offline publication may write only to support-side public objects.
It may not publish directly into:
- certifier state,
- hard-boundary state,
- host capability truth,
- or any object that can bypass commitment certification.

### 5.4 Contradiction-preserving publication

Offline support memory must preserve contradictions rather than collapsing them into one smoothed host story.

### 5.5 Re-entry law

When offline outputs are reintroduced into runtime support, they must do so through explicit augmentation:

\[
W_t^{pub+} = \operatorname{Augment}^{aux}(W_t^{pub}, M_t^{offline})
\]

They may not redefine core observation or commitment semantics.

### 5.6 SRE handoff law

Any future nonzero support-conditioned priors intended to influence `Q_t^{mem}(a)`
must be published only as support-side public objects and must re-enter runtime support
only through explicit AUX augmentation.

They may not come from:
- hidden host memory,
- prompt heuristics,
- runtime caches,
- softened closure logic,
- or any object that changes commitment truth.

Until that publication path exists and earns retention, shipping and conformance lanes
may keep `Q_t^{mem}(a)=0` while AUX remains removable and runtime-off-by-default.
AUX owns the bounded `claude|gemini|reference` cross-host shadow evaluator over that
explicit publication path.
Fresh contradiction must invalidate any reliability-derived shadow lift before the next
selection pass; stale host confidence may not outrank current contradiction evidence.
That evaluator may compare `host_local` and `reference_projected` continuity bases on
branch-resume cases to determine whether an apparent branch gap is a shared shadow limit
or only a local continuity-basis weakness.
If lawful non-reference host observables still alias on that bounded shadow surface, AUX
must narrow the earned claim to a shared documented non-reference shell rather than
fabricating host-distinct lift.
That evaluator must keep the overall shadow `claim_mode` separate from
`non_reference_evidence_mode`: lawful non-reference host distinction may be earned from
bounded structural trace observables even while the broader cross-host shadow claim stays
narrow because host-local continuity still fails.

---

## 6. Interaction with core and SRE

### 6.1 AUX ↔ Core

AUX may observe:
- public support snapshots,
- public contradiction records,
- public host-affordance summaries,
- and public commitment outcomes.

AUX may not:
- inspect hidden certifier internals,
- or alter commitment law.

### 6.2 AUX ↔ SRE

AUX may support SRE by providing:
- retrieval priors,
- branch priors,
- contradiction summaries,
- uncertainty/brake calibration hints,
- optional geometry-derived diagnostics.

The SRE may ignore AUX entirely and remain lawful.

### 6.3 No sovereignty by accumulation

No amount of accumulated auxiliary memory, geometry, or calibration may become de facto commitment authority.

---

## 7. Explicitly out of AUX

Out of AUX by law:
- commitment certification,
- blockedness truth,
- provenance sufficiency,
- hard safety/integrity boundaries,
- hidden adapter doctrine,
- mandatory runtime dependence,
- or any rule that makes AUX required for minimum lawful Cortex behavior.

---

## 8. Promotion, retention, and pruning

### 8.1 Promotion law

An AUX module may be promoted from deferred/evaluation-first to active runtime support only if it demonstrates:
- clear control/evaluation lift,
- bounded overhead,
- contradiction preservation,
- and zero leakage into commitment truth.

### 8.2 Pruning law

If an AUX module:
- adds overhead without lift,
- becomes a hidden semantic owner,
- smooths contradictory host evidence,
- or becomes operationally load-bearing for commitment truth,

it must be pruned or demoted.

---

## 9. Final layer law

The AUX layer is the official quarantine and support layer of Cortex v2.

Its job is to make Cortex smarter where removable, support-side, and experimentally justified mechanisms help.
Its job is not to quietly become the real kernel.
