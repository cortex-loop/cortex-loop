# EXECUTIVE_STATE_SPEC

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: canonical specification for the finished derived executive overlay and its control-allocation law  
Date: 2026-03-15  
Scope: explicit executive state, pre/post admissible soft actions, arbitration as the update of `\kappa_t`, parameter governance, and computational limits  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `BIOLOGY_TO_MATH_TO_CODE.md`, `GEOMETRY_AND_EVALUATION_SPEC.md`, `EXECUTIVE_INTERFACES.md`, and `OFFLINE_CONSOLIDATION_AND_BMR.md`  
Non-goal: replacing kernel ontology, softening completion truth, or introducing a second semantic core

---

## 0. Purpose

This document answers one narrow question:

**If Cortex remains the sole claim-bearing completion kernel, what exact state must the executive layer carry, and how is that state used to allocate soft control without blurring truth?**

The answer is deliberately conservative:

- the kernel stays canonical,
- the overlay is derived,
- the overlay is fixed at six top-level carriers,
- arbitration is treated as the update law for `\kappa_t`, not as a second ontology,
- the admissible soft-action set is split into pre-brake and post-brake forms to keep the control law acyclic,
- explicit non-intervention is a first-class soft action rather than an exhaustion case,
- host asymmetry is handled explicitly through affordance filtering,
- catastrophic halts remain kernel-owned.

The exact code-facing contracts that realize this state live in `EXECUTIVE_INTERFACES.md`.

---

## 1. Kernel lock and derivation boundary

The executive layer begins only after the canonical kernel factorization:

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
W_t=(W_t^{grave},W_t^{retry},W_t^{execmem},W_t^{host},W_t^{trace})
\]

be non-claim-bearing support state.

Compatibility note for the net-positive kernel program:

\[
P_t^{route}=(\tau_t,\upsilon_t,\Delta_t,b_t)
\]

may be stored inside `W_t^{trace}` or a typed support-trace subfield only.
Here `\upsilon_t` is the kernel-campaign assurance class; executive `\chi_t` remains reserved for vigor inside `\kappa_t`.
`P_t^{route}` is advisory context only and is not a seventh executive carrier.

Define

\[
Y_t := (K_t,R_t,A_t,C_t,W_t).
\]

The executive overlay is

\[
Z_t=\Xi_c(Y_t)
\]
\[
Z_t=(G_t,U_t,M_t^{\mathrm{mode}},\Gamma_t,\kappa_t,J_t^{\mathrm{brake}}).
\]

The lawful acyclic factorization is

\[
\begin{aligned}
G_t &= \Xi_G(Y_t),\\
U_t &= \Xi_U(Y_t,G_t),\\
M_t^{\mathrm{mode}} &= \Xi_{\mathrm{mode}}(Y_t,G_t,U_t),\\
\Gamma_t &= \Xi_{\Gamma}(Y_t,G_t,U_t,M_t^{\mathrm{mode}}),\\
\widehat Z_t &:= (G_t,U_t,M_t^{\mathrm{mode}},\Gamma_t),\\
\Phi_t^- &= \phi_c^-(D_t,\widehat Z_t),\\
\mathcal A_{t,r}^{\mathrm{pre}} &= \operatorname{Adm}_r^{\mathrm{pre}}(\mathcal A^{\mathrm{soft}},W_t^{host},\Gamma_t),\\
\kappa_t &= \Xi_{\kappa}(Y_t,\widehat Z_t,\Phi_t^-,\mathcal A_{t,r}^{\mathrm{pre}}),\\
J_t^{\mathrm{brake}} &= \Xi_J(Y_t,\widehat Z_t,\kappa_t),\\
\mathcal A_{t,r}^{\mathrm{post}} &= \operatorname{Adm}_r^{\mathrm{post}}(\mathcal A_{t,r}^{\mathrm{pre}},J_t^{\mathrm{brake}}),\\
\Phi_t &= (\Phi_t^-,\phi_\kappa(\kappa_t)).
\end{aligned}
\]

There is no circular dependence.

---

## 2. Spaces and carrier types

Let

\[
\mathcal A^{\mathrm{soft}}=
\{\text{stay-course},\text{retrieve},\text{reorient},\text{review},\text{defer},\text{branch},\text{escalate},\text{halt-support}\}.
\]

The executive spaces are:

\[
\mathcal G,\quad
\mathcal U=[0,1]^3,\quad
\mathcal M^{mode}=\Delta(\{internal,external,mixed\}),
\]
\[
\Gamma=\Gamma^{write}\times\Gamma^{read}\times\Gamma^{influence},
\quad
\mathcal Kappa=[0,B_{max}] \times \Delta(\mathcal A_{t,r}^{pre}) \times [0,1],
\quad
\mathcal J=\{quiescent,guarded,latched\}.
\]

Thus

\[
\widehat{\mathcal Z} = \mathcal G \times \mathcal U \times \mathcal M^{mode} \times \Gamma,
\qquad
\mathcal Z = \widehat{\mathcal Z} \times \mathcal Kappa \times \mathcal J.
\]

The geometry spaces are

\[
\Phi^-=\Phi_D \times \Phi_G \times \Phi_U \times \Phi_M \times \Phi_\Gamma,
\qquad
\Phi=\Phi^- \times \Phi_\kappa.
\]

---

## 3. State-variable specifications

### 3.1 `G_t` — hierarchical goal state

| Property | Specification |
|---|---|
| Symbol | `G_t` |
| Intuitive meaning | active, pending, and alternative goals plus lawful resume structure |
| Formal type / domain | \(G_t \in \mathcal G = \mathcal G_{id} \times 2^{\mathcal G_{id}} \times 2^{\mathcal G_{id}} \times 2^{\mathcal G_{id}} \times \mathcal{POrd}(\mathcal G_{id}) \times \mathcal R^{goal}\) |
| Update law | \(G_t=\Xi_G(Y_t)\) |
| Producer | `ExecutiveStateBuilder` |
| Persistence policy | session-local and branch-local only |
| Allowed consumers | branch manager, control allocator, geometry |
| Forbidden consumers | `\nu`, `\Sigma`, requirements, invariants |
| Complexity notes | bounded by branch cap |

Invariants:
- active / pending / alternative sets are pairwise disjoint,
- the goal order is acyclic,
- every pending goal has a resume record.

### 3.2 `U_t` — factorized uncertainty state

| Property | Specification |
|---|---|
| Symbol | `U_t` |
| Intuitive meaning | explicit uncertainty over evidence, environment, and capability |
| Formal type / domain | \(U_t=(u_t^{evidence},u_t^{environment},u_t^{capability}) \in [0,1]^3\) |
| Update law | \(U_t=\Xi_U(Y_t,G_t)\) |
| Producer | `ExecutiveStateBuilder` |
| Persistence policy | recomputed each turn; optional bounded smoothing only |
| Allowed consumers | allocator, mode selection, gating, geometry |
| Forbidden consumers | `\nu`, `\Sigma`, requirements, invariants |
| Complexity notes | fixed-dimensional |

Invariant:
- uncertainty may increase advisory caution but may not lower hard completion thresholds.

### 3.3 `M_t^{mode}` — control-mode state

| Property | Specification |
|---|---|
| Symbol | `M_t^{mode}` |
| Intuitive meaning | internal / external / mixed control posture |
| Formal type / domain | \(M_t^{mode}\in\Delta(\{internal,external,mixed\})\) |
| Update law | \(M_t^{mode}=\Xi_{mode}(Y_t,G_t,U_t)\) |
| Producer | `ExecutiveStateBuilder` |
| Persistence policy | recomputed each turn with optional hysteresis |
| Allowed consumers | allocator, geometry |
| Forbidden consumers | `\nu`, `\Sigma`, requirements, invariants |
| Complexity notes | constant size |

Invariant:
- internal posture may reduce tool use, never waive required evidence.

### 3.4 `\Gamma_t` — selective gate state

| Property | Specification |
|---|---|
| Symbol | `\Gamma_t` |
| Intuitive meaning | selective write / read / influence gating over soft-control pathways |
| Formal type / domain | \(\Gamma_t=(\gamma_t^{write},\gamma_t^{read},\gamma_t^{influence})\) over a finite named channel set, each value in `[0,1]` |
| Update law | \(\Gamma_t=\Xi_\Gamma(Y_t,G_t,U_t,M_t^{mode})\) |
| Producer | `ExecutiveStateBuilder` |
| Persistence policy | ephemeral, with optional short anti-thrash counters |
| Allowed consumers | allocator, host affordance filter, memory write filter, geometry |
| Forbidden consumers | `\alpha_c`, `\eta_c`, `\nu`, `\Sigma`, requirements, invariants |
| Complexity notes | sparse in nonzero channels |

Invariant:
- gates may suppress advisory candidates, never real deficits or failed invariants.

### 3.5 `\kappa_t` — control-allocation state

| Property | Specification |
|---|---|
| Symbol | `\kappa_t=(\beta_t,\lambda_t^{pre},\chi_t)` |
| Intuitive meaning | soft budget, pre-brake soft-action allocation, and control vigor |
| Formal type / domain | \(\beta_t \in [0,B_{max}], \; \lambda_t^{pre}\in\Delta(\mathcal A_{t,r}^{pre}), \; \chi_t\in[0,1]\) |
| Update law | Sections 5.1–5.6 |
| Producer | `ControlAllocator` |
| Persistence policy | session-local only; cross-session use is summary-only through executive memory |
| Allowed consumers | executive policy, geometry (`\phi_\kappa`), brake policy |
| Forbidden consumers | completion acceptance, canonical claim synthesis, requirements, invariants |
| Complexity notes | linear in `|\mathcal A_{t,r}^{pre}|` plus bounded memory lookup |

Invariants:
- no mass may ever correspond to completion acceptance,
- `\chi_t` regulates vigor, not truth or assurance,
- the kernel-campaign assurance class is `\upsilon_t`, not `\chi_t`.

### 3.6 `J_t^{brake}` — advisory brake latch

| Property | Specification |
|---|---|
| Symbol | `J_t^{brake}` |
| Intuitive meaning | bounded latch for stopping soft exploration, aborting futile branches, or forcing review / escalation |
| Formal type / domain | \(J_t^{brake}\in\{quiescent,guarded,latched\}\) |
| Update law | \(J_t^{brake}=\Xi_J(Y_t,\widehat Z_t,\kappa_t)\) |
| Producer | `SoftBrakePolicy` |
| Persistence policy | sticky within session until reset / acknowledgment |
| Allowed consumers | executive policy, host-affordance filter |
| Forbidden consumers | `\nu`, `\Sigma`, completion certification, kernel safety halt semantics |
| Complexity notes | constant time |

Invariants:
- `quiescent` with dominant `stay-course` expresses “no extra support needed” and is distinct from exhaustion,
- `latched` may stop soft exploration,
- `latched` may not declare completion,
- catastrophic safety or integrity halts belong in `H_t`, not here.

---

## 4. Soft-action domain and host-affordance law

The abstract soft-control family is

\[
\mathcal A^{soft}=
\{\text{stay-course},\text{retrieve},\text{reorient},\text{review},\text{defer},\text{branch},\text{escalate},\text{halt-support}\}.
\]

Repair ranking and retrieval depth are auxiliary advisory outputs, not claim-bearing actions.

Because hosts differ, the executive layer never assumes all soft actions are equally realizable.

### 4.1 Pre-brake admissible set

\[
\mathcal A_{t,r}^{pre}=
\operatorname{Adm}_r^{pre}(\mathcal A^{soft},W_t^{host},\Gamma_t).
\]

This set excludes actions unsupported by the host or already suppressed by gates.
`stay-course` is admissible whenever the executive layer is allowed to publish advice; hosts may realize it as an explicit no-extra-support recommendation or a typed no-op.

### 4.2 Post-brake admissible set

\[
\mathcal A_{t,r}^{post}=
\operatorname{Adm}_r^{post}(\mathcal A_{t,r}^{pre},J_t^{brake}).
\]

This set applies the brake latch after control allocation.

### 4.3 Post-brake advisory distribution

Let \(m_t^J : \mathcal A_{t,r}^{pre}\to\{0,1\}\) be the brake mask corresponding to `J_t^{brake}`.
Define

\[
\lambda_t^{post}(a)=
\frac{m_t^J(a)\lambda_t^{pre}(a)}
{\varepsilon+\sum_{a'\in\mathcal A_{t,r}^{pre}} m_t^J(a')\lambda_t^{pre}(a')}.
\]

Then \(\lambda_t^{post}\in\Delta(\mathcal A_{t,r}^{post})\) whenever the denominator is nonzero.
If the denominator is zero, the policy falls back to a brake-conditioned template over \(\mathcal A_{t,r}^{post}\):
- quiescent -> prefer `stay-course`,
- guarded -> prefer `review` / `escalate`,
- latched -> prefer `halt-support` / `review` / `escalate`.

This split removes the final circularity in the earlier draft.

---

## 5. The update law for `\kappa_t`

The arbitration layer is not a second ontology.
It is the lawful update of the control-allocation carrier.

### 5.1 Realized soft return

For an executed soft action `a_t`, define realized soft return

\[
r_t^{soft} =
 w_D \Delta_t^{obs,D}
+ w_U \Delta_t^{obs,U}
+ w_G \Delta_t^{obs,G}
- w_C C_t^{obs}
- w_L L_t^{obs},
\]

where:

- `\Delta_t^{obs,D}` = observed improvement in deficit-handling progress,
- `\Delta_t^{obs,U}` = observed uncertainty reduction,
- `\Delta_t^{obs,G}` = observed goal / branch preservation benefit,
- `C_t^{obs}` = observed control cost,
- `L_t^{obs}` = observed loop / thrash cost.

A lawful decomposition of control cost is

\[
C_t^{obs}=C_t^{tool}+C_t^{delay}+C_t^{burden}+C_t^{risk}.
\]

Humane considerations therefore enter as explicit cost terms, not as a top-level social ontology.

### 5.2 Explicit one-step control score

The explicit scorer is

\[
Q_t^{EX} : \mathcal A_{t,r}^{pre} \to \mathbb R
\]

with

\[
Q_t^{EX}(a)=
 w_D q_t^D(a)
+ w_U q_t^U(a)
+ w_G q_t^G(a)
- w_C c_t^{ctrl}(a)
- w_L c_t^{loop}(a).
\]

These are current-state action features, not a forward simulation of latent rollouts.

### 5.3 Memory-conditioned control score

The memory lane is

\[
Q_t^{MF}(a)=
\frac{\sum_{i\in\mathcal I_a} s(\Phi_t^-,\Phi_i^-)\,r_i^{soft}}
{\varepsilon+\sum_{i\in\mathcal I_a} s(\Phi_t^-,\Phi_i^-)}
\]

where:

- `\Phi_t^-` is current pre-control geometry,
- `s` is a lawful similarity from the geometry spec,
- `\mathcal I_a` are prior traces for action `a`,
- `r_i^{soft}` is realized soft return for prior trace `i`,
- the memory source is the read-only `ExecutiveMemorySnapshot` published offline.

A discrete fallback key may be used if geometry is disabled.

### 5.4 Reliability and arbitration

Define controller errors

\[
e_t^{EX}:=r_{t-1}^{soft}-Q_{t-1}^{EX}(a_{t-1}),
\qquad
e_t^{MF}:=r_{t-1}^{soft}-Q_{t-1}^{MF}(a_{t-1}).
\]

Define bounded reliabilities

\[
u_t^{EX}:=
 s_t^{obs}\exp\!\left(-\frac{|e_t^{EX}|}{\sigma_{EX}}\right)
\left(1-\frac{u_t^{environment}+u_t^{capability}}{2}\right),
\]
\[
u_t^{MF}:=
 cov_t^{MF}\exp\!\left(-\frac{|e_t^{MF}|}{\sigma_{MF}}\right)
(1-u_t^{environment}),
\]

clipped into `[0,1]`.

Then the smoothed explicit-lane weight is

\[
\widetilde p_t^{EX}:=
\frac{u_t^{EX}}{u_t^{EX}+u_t^{MF}+\varepsilon},
\qquad
p_t^{EX}:=(1-\rho_p)p_{t-1}^{EX}+\rho_p\widetilde p_t^{EX}.
\]

The transient arbitration bundle is

\[
\mathfrak A_t := (Q_t^{EX},Q_t^{MF},u_t^{EX},u_t^{MF},p_t^{EX}),
\]

which is diagnostics, not top-level state.

### 5.5 Mixed control score and pre-brake allocation

For each pre-admissible soft action:

\[
Q_t^{ctl}(a)=p_t^{EX}Q_t^{EX}(a)+(1-p_t^{EX})Q_t^{MF}(a).
\]

Then:

\[
\lambda_t^{pre}(a)=
\frac{\exp(\tau_\lambda Q_t^{ctl}(a))}
{\sum_{a'\in\mathcal A_{t,r}^{pre}}\exp(\tau_\lambda Q_t^{ctl}(a'))},
\qquad
\lambda_t^{pre}\in\Delta(\mathcal A_{t,r}^{pre}).
\]

Let expected control cost be

\[
\overline C_t=
\sum_{a\in\mathcal A_{t,r}^{pre}}\lambda_t^{pre}(a)c_t^{ctrl}(a).
\]

Then the budget update is

\[
\beta_t=
\operatorname{clip}
\left(
\sum_{a\in\mathcal A_{t,r}^{pre}}\lambda_t^{pre}(a)[Q_t^{ctl}(a)]_+
-\zeta_C\overline C_t,
0,B_{max}
\right).
\]

And vigor is

\[
\chi_t=
\operatorname{clip}
\left(
\chi_0+\chi_1\beta_t
-\chi_2\mathbf 1\{R_t=\mathrm{stagnant}\},
0,1
\right).
\]

This is the only lawful way the arbitration layer enters persistent state:
through the update of `\kappa_t=(\beta_t,\lambda_t^{pre},\chi_t)`.

### 5.6 Brake update

The advisory brake is a function of soft-control failure or exhaustion, not of kernel safety facts:

\[
J_t^{brake}=
\begin{cases}
\mathrm{latched}, & \beta_t=0 \;\text{or}\; \operatorname{stagnationrun}_t\ge m_{stop} \;\text{or}\; \operatorname{branchload}_t>B_{branch},\\
\mathrm{guarded}, & \beta_t\le \beta_{guard} \;\text{or}\; \chi_t\le \chi_{guard},\\
\mathrm{quiescent}, & \text{otherwise}.
\end{cases}
\]

### 5.7 Auxiliary advisory outputs

From \((\lambda_t^{post},Q_t^{ctl})\) the policy may emit:

- repair ranking,
- retrieval depth,
- branch proposals,
- stay-course score,
- reorient score,
- review score,
- defer score,
- escalate score,
- halt-support score.

Allowed influence surface:

- repair ranking,
- retrieval depth,
- explicit stay-course / no-extra-support posture,
- reorient vs continue posture,
- bounded branch opening or resumption,
- review / defer / escalate recommendations,
- halt-support recommendation,
- soft budget and vigor.

Forbidden influence surface:

- completion acceptance,
- hard-fact extraction,
- canonical deficit deletion,
- bounded kernel action ownership,
- canonical claim mutation,
- requirement or invariant override,
- adapter-preservation law.

---

## 6. Parameter governance

The finished packet distinguishes four parameter families.

### 6.1 Constitutional parameters `Θ^{const}`

Examples:
- the soft-action alphabet,
- brake levels,
- required invariants,
- no-go-zone laws,
- packet-defined object names.

Change authority: new constitution only.

### 6.2 Calibrated parameters `Θ^{cal}`

Examples:
- `w_D,w_U,w_G,w_C,w_L`,
- `\sigma_{EX}, \sigma_{MF}, \rho_p, \tau_\lambda, \zeta_C`,
- `\chi_i, \beta_{guard}, \chi_{guard}, \delta_i`,
- geometry weights and evaluation thresholds.

Change authority: offline audited calibration release only.

### 6.3 Published executive-memory parameters `Θ^{mem}`

Examples:
- repair priors,
- pattern priors,
- branch priors,
- calibration summaries packaged in the read-only executive-memory snapshot.

Change authority: offline consolidation publish only.

### 6.4 Ephemeral run quantities `Θ_t^{run}`

Examples:
- diagnostics,
- current score tables,
- current reliabilities,
- cache-local similarity computations.

Change authority: live turn-local computation only.
Never persisted directly into the live packet.

---

## 7. Complexity budget

Target online complexity:

- `G_t`: bounded by branch cap,
- `U_t`: linear in touched kernel / support features,
- `M_t^{mode}`: constant size,
- `\Gamma_t`: sparse in nonzero gates,
- `\kappa_t`: linear in `|\mathcal A_{t,r}^{pre}|`,
- `J_t^{brake}`: constant size,
- memory lookup: bounded fanout,
- geometry: bounded subspace dimension.

Disallowed complexity patterns:

- unconstrained branch trees,
- dense all-to-all gating,
- arbitration whose bookkeeping dominates the control lift,
- hidden planners required just to interpret the executive state.

---

## 8. Phase consequences

- **Phase O:** build `G_t`, `U_t`, `M_t^{mode}`, `\Gamma_t`, and `\Phi_t^-`; log only.
- **Phase A:** build `\mathcal A_{t,r}^{pre}`, `\kappa_t`, `J_t^{brake}`, `\mathcal A_{t,r}^{post}`, and advisory outputs.
- **Phase R:** realize only the host-admissible post-brake subset.
- **Phase L:** publish read-only executive-memory snapshots offline.

No phase allows the executive layer to redefine truth.

---

## 9. One-sentence summary

**The finished executive overlay is a fixed six-carrier derived state with an acyclic pre-brake/post-brake control law, and the only lawful place for arbitration is inside the update of `\kappa_t`, where it may allocate soft control but may never touch completion truth.**
