# OFFLINE_CONSOLIDATION_AND_BMR

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: canonical specification for offline executive-memory consolidation and BMR-like reduction  
Date: 2026-03-15  
Scope: what may be learned offline, what may never be learned into opacity, and how executive-memory snapshots re-enter the live system safely  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `BIOLOGY_TO_MATH_TO_CODE.md`, `EXECUTIVE_STATE_SPEC.md`, `EXECUTIVE_INTERFACES.md`, `GEOMETRY_AND_EVALUATION_SPEC.md`, `KERNEL_IMPLEMENTATION_DOSSIER.md`, `KERNEL_MATH_STATUS_DOSSIER.md`, and `ADAPTER_IMPLEMENTATION_DOSSIER.md`  
Non-goal: online mutation of kernel law, memorized completion heuristics, opaque claim behavior, or adapter-semantic drift

---

## 0. Purpose

This document answers one narrow question:

**If Cortex learns from accumulated executive traces, what may be compressed offline, how may it be compressed, and how may the result re-enter the live system without mutating kernel truth?**

The answer is deliberately conservative:

- consolidation is offline only,
- consolidation acts only on executive support memory and calibration,
- the live path sees only read-only published snapshots,
- learned support may improve soft control,
- learned support may not redefine completed.

In plain language:

**Cortex may learn better habits around checking; it may not learn a new definition of completed.**

---

## 1. Separation of laws

The constitutional kernel remains

\[
(H_t,D_t,S_t)=(\eta_c(E_t),\alpha_c(E_t),\sigma_c(E_t)),
\]
\[
K_t=(H_t,D_t,M_t), \qquad B_t=\nu(H_t),
\]
\[
(R_t,M_{t+1})=\rho(H_t,D_t,S_t,M_t),
\]
\[
A_t=\pi(c,H_t,D_t,M_t,R_t),
\]
\[
C_t=\Sigma(H_t,D_t,M_t,R_t,A_t),
\]
\[
O_t=\Omega(C_t,E_t).
\]

Let

\[
\mathfrak K_c := (\eta_c,\alpha_c,\sigma_c,\nu,\rho,\pi,\Sigma,\Omega)
\]

be the constitutional kernel law.

This law is not a consolidation target.

The only writable offline targets are:

\[
M_n^{exec}
\quad\text{and}\quad
\Theta_n^{cal,pub},
\]

which re-enter the live system only as the read-only published objects

\[
W_t^{execmem}=\operatorname{Snap}(M_n^{exec},\Theta_n^{cal,pub}).
\]

Separation invariant:

\[
\operatorname{Dep}(\mathfrak K_c, M_n^{exec})=\varnothing,
\qquad
\operatorname{Dep}(\mathfrak K_c, \Theta_n^{cal,pub})=\varnothing.
\]

Equivalently, removing the published snapshot leaves the claim-bearing boundary unchanged.

---

## 2. Honest meaning of “BMR” in Cortex

Cortex borrows only one narrow idea from Bayesian model reduction:

> prefer the smallest support object that preserves soft-control utility.

It does **not** claim:

- that the live executive layer is a full active-inference engine,
- that every offline update is a literal variational-Bayes derivation,
- that learned support is allowed to rewrite kernel law.

So “BMR-like” in Cortex means only this guiding objective:

\[
(\widetilde M_{n+1}^{exec},\widetilde \Theta_{n+1}^{cal,pub})
\in
\arg\max
\Big(
\operatorname{Fit}
-
\lambda_{comp}\operatorname{Complexity}
\Big)
\]

over the admissible executive support family, subject to all no-go-zone constraints.

For code and internal names, use plain terms such as:

- `OfflineConsolidator`,
- `ExecutiveTraceDistiller`,
- `ExecutiveMemorySnapshot`.

Do not use `BMR` in implementation names unless exact Bayesian evidence is actually computed.

---

## 3. What may be consolidated

The admissible executive-memory object is

\[
M_n^{exec}=(P_n^{rep},P_n^{pat},P_n^{grave},P_n^{branch}),
\]

and the admissible published calibration object is

\[
\Theta_n^{cal,pub}.
\]

### 3.1 `P_n^{rep}` — repair priors
Prior over repair-target ordering for bounded deficit families and goal contexts.

### 3.2 `P_n^{pat}` — learned patterns
Context-conditioned priors over soft-control choices such as stay-course, retrieve, reorient, review, or defer.

### 3.3 `P_n^{grave}` — graveyard priors
De-duplicated priors over failure patterns, failure contexts, and anti-repeat cues.

### 3.4 `P_n^{branch}` — branch heuristics
Priors over when branching, collapsing, or resuming a pending goal was actually useful.

### 3.5 `\Theta_n^{cal,pub}` — published calibration summaries
Audited numeric summaries for:

- control-scorer calibration,
- reliability smoothing,
- geometry weighting,
- review thresholds.

These are support objects.
None of them is claim-bearing.

---

## 4. What may not be consolidated into opacity

The following are explicit no-go zones:

- the completion law `\mathfrak K_c`,
- canonical hard facts `H_t`,
- canonical deficits `D_t`,
- canonical claims `C_t`,
- verdict law `\nu`,
- requirement / invariant semantics,
- adapter-preservation semantics,
- kernel safety halt semantics,
- any hidden completion heuristic that bypasses unresolved deficits.

No offline process may publish an object that causes the live system to behave *as if* any of the above had changed.

### 4.1 Diagnostics quarantine

Raw control diagnostics, geometry probes, and witness prose are not publishable memory objects.

They may appear in raw traces for audit purposes, but only aggregated, schema-audited, non-claim-bearing summaries may survive into `M_n^{exec}` or `\Theta_n^{cal,pub}`.

---

## 5. Safe consolidation pipeline

The lawful offline pipeline is:

### 5.1 Trace capture
Collect only admissible traces

\[
\mathcal T_{1:n}^{adm}
\]

containing:

- pre-control context,
- chosen soft action,
- realized soft return,
- branch / usefulness outcomes,
- retrieval and reuse results,
- loop / thrash signals,
- host-affordance context.

Exclude claim-bearing semantics as training targets.

### 5.2 Admissibility filtering
Reject traces that are:

- semantically ambiguous,
- host-corrupted,
- dominated by kernel hard-failure paths,
- incomplete in the fields needed for honest control scoring.

### 5.3 Candidate expansion
Construct candidate support objects only in the admissible family

\[
\mathcal M_{adm}^{exec} \times \Theta_{adm}^{cal,pub}.
\]

### 5.4 Distillation
Apply offline reduction / distillation

\[
(\widetilde M_{n+1}^{exec},\widetilde \Theta_{n+1}^{cal,pub})
=
\operatorname{Distill}_{off}(M_n^{exec},\Theta_n^{cal,pub},\mathcal T_{1:n}^{adm})
\]

using audited objectives such as utility-minus-complexity, calibration, and de-duplication.

### 5.5 Audit gate
A candidate publish bundle may publish only if it passes:

- no-go-zone checks,
- schema checks,
- ablation checks,
- utility-over-baseline checks,
- adapter-preservation checks,
- reversibility checks,
- calibration-stability checks.

### 5.6 Publish-or-reject
If it passes, publish only the read-only snapshot

\[
W_t^{execmem}=\operatorname{Snap}(\widetilde M_{n+1}^{exec},\widetilde \Theta_{n+1}^{cal,pub}).
\]

If it fails, reject it.

---

## 6. How the live system may use the snapshot

The live path may use `W_t^{execmem}` only for:

- `Q_t^{MF}` value lookup,
- repair-prior ranking,
- branch-heuristic hints,
- retrieval and reuse support,
- calibration of control allocation and geometry evaluation.

The live path may not use `W_t^{execmem}` for:

- completion acceptance,
- deficit deletion,
- claim synthesis,
- bypassing requirements or invariants,
- runtime mutation of constitutional parameters.

---

## 7. One-sentence summary

**The finished consolidation pipeline learns only better support priors and audited calibration summaries offline, publishes them back as read-only executive-memory snapshots, and makes it impossible for that learning to rewrite the completion law.**
