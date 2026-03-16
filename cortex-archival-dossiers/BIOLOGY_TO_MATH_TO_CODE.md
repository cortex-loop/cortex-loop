# BIOLOGY_TO_MATH_TO_CODE

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: canonical biology -> math -> code map for the finished executive packet  
Date: 2026-03-15  
Scope: exact map from approved biological mechanisms to mathematical carriers and software seams around the current Cortex kernel  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `KERNEL_IMPLEMENTATION_DOSSIER.md`, `KERNEL_MATH_STATUS_DOSSIER.md`, and `ADAPTER_IMPLEMENTATION_DOSSIER.md`  
Non-goal: replacing kernel truth, overclaiming one-to-one neural equivalence, or duplicating the state / geometry / interface / consolidation specs

---

## 0. Method

This document preserves the design ethic that produced the base kernel.

The method is:

1. start from what must be checked,
2. identify where agents fail when checking is too brittle or too blunt,
3. import only the biological mechanism that fixes that failure mode,
4. map it to an owned mathematical carrier,
5. realize it in code only as a conservative extension of the kernel.

That is why Cortex grew from hard enforcement gates into a richer checking system.
The executive layer continues that same method.
It does not abandon it.

---

## 1. What the code is trying to do

### 1.1 What Cortex is trying to accomplish at the completion boundary

At the completion boundary, Cortex is trying to answer one question truthfully:

**What, exactly, may this agent stand behind as completed, and what bounded kernel action follows if completion is not yet truthful?**

That question is answered by the kernel factorization

\[
(H_t,D_t,S_t)=(\eta_c(E_t),\alpha_c(E_t),\sigma_c(E_t)),
\quad
K_t=(H_t,D_t,M_t),
\quad
B_t=\nu(H_t),
\]
\[
(R_t,M_{t+1})=\rho(H_t,D_t,S_t,M_t),
\quad
A_t=\pi(c,H_t,D_t,M_t,R_t),
\quad
C_t=\Sigma(H_t,D_t,M_t,R_t,A_t),
\quad
O_t=\Omega(C_t,E_t).
\]

In plain language: the kernel is a theory of checking, not a planner.

### 1.2 What the executive expansion is trying to accomplish

The executive expansion is trying to make the agent better **around** that boundary.

It exists to improve:

- hierarchical goal maintenance,
- pending-goal and branch discipline,
- explicit uncertainty handling,
- selective gating,
- control-mode selection,
- soft control allocation,
- bounded advisory braking,
- retrieval / reuse / evaluation geometry,
- offline consolidation of executive support memory.

In plain language: the executive layer is trying to improve how the agent approaches truthful closure, not to redefine truthful closure.

### 1.3 What the executive expansion is not trying to do

It is not trying to:

- replace the kernel with a soft controller,
- let confidence become truth,
- let elapsed time lower hard completion thresholds,
- replace canonical deficits with embeddings,
- let geometry certify completion,
- let offline learning rewrite kernel law,
- let adapters invent host-native semantics.

### 1.4 Which human-like properties are desirable

The desirable imports are:

- hierarchical goal structure,
- maintenance of pending goals,
- selective rather than global gating,
- explicit uncertainty,
- switching between internal reasoning and external checking,
- cost-sensitive control allocation,
- bounded advisory braking,
- factorized geometry that generalizes,
- offline consolidation of useful control habits.

### 1.5 Which human flaws are not to be imported

The forbidden imports are:

- confabulation,
- wishful completion,
- fatigue-style threshold collapse,
- self-serving bias,
- narrative drift,
- treating a feeling of knowing as proof,
- pretending a metaphor is a theorem.

The brain is the source of useful motifs, not the constitutional standard.

---

## 2. Kernel-to-code anchor

Current live embodied boundary:

\[
\mathrm{StopPathOutcome}(kernel,witness)
\]

with the split:

- `kernel.state`
- `kernel.transition`
- `kernel.action`
- `kernel.claims`
- optional `witness`

Current code-owned mathematical carriers:

| Carrier | Meaning | Current code seam | Status | Authority note |
|---|---|---|---|---|
| `E_t` | stop-time evidence | `stop_runtime` evidence gathering and check outputs | live | evidence-bearing only |
| `H_t` | hard facts / hard gate facts | `kernel.state` hard-fact surface | live | claim-bearing |
| `D_t` | canonical unresolved deficits | `kernel.state` unresolved obligation / gap surface | live | claim-bearing and authoritative |
| `S_t` | stop-attempt signature | attempt / transition signature in runtime state | live | evidence-bearing |
| `M_t` | bounded supervisory memory | persisted bounded stop memory | live | claim-bearing only where the kernel already uses it |
| `R_t` | transition classification / residue | `kernel.transition` | live | control-bearing |
| `A_t` | bounded kernel control action | `kernel.action` | live | control-bearing |
| `C_t` | canonical claims | `kernel.claims` | live | claim-bearing |
| `O_t` | outward rendering of `StopPathOutcome(kernel,witness)` | stop rendering / witness transport | live | witness-bearing only |

### 2.1 Canonical-source rule

The executive layer must read canonical deficits from the state-side owner only.

- Authoritative source for `D_t`: `kernel.state`
- Public projection of deficits inside claims: presentation only
- Witness content: manifest / transport only

That rule is what prevents a public projection from turning into a hidden second truth layer.

---

## 3. Executive quantities and code seams

The executive packet reads the boundary through the read-only input

\[
Y_t=(K_t,R_t,A_t,C_t,W_t),
\qquad
W_t=(W_t^{grave},W_t^{retry},W_t^{execmem},W_t^{host},W_t^{trace}).
\]

Compatibility with the net-positive kernel program:

\[
P_t^{route}=(\tau_t,\upsilon_t,\Delta_t,b_t)
\]

may live only inside `W_t^{trace}` or a typed support-trace subfield.
It is support-only, not a seventh executive carrier, and its `\upsilon_t` assurance class is distinct from executive vigor `\chi_t`.

The pre-control state is

\[
\widehat Z_t=(G_t,U_t,M_t^{mode},\Gamma_t),
\]

the full derived state is

\[
Z_t=(G_t,U_t,M_t^{mode},\Gamma_t,\kappa_t,J_t^{brake}),
\]

and the geometry is

\[
\Phi_t^-=\phi_c^-(D_t,\widehat Z_t),
\qquad
\Phi_t=(\Phi_t^-,\phi_\kappa(\kappa_t)).
\]

The exact code seams are:

| Quantity | Mathematical role | Software seam | Status | Notes |
|---|---|---|---|---|
| `G_t` | goal hierarchy, pending goals, branch resume | `GoalState`, `ExecutiveStateBuilder`, `executive_branching.py` | observational -> advisory | bounded and branch-capped |
| `U_t` | factorized uncertainty | `UncertaintyState`, `ExecutiveStateBuilder` | observational -> advisory | explicit and bounded |
| `M_t^{mode}` | internal / external / mixed posture | `ModeState`, `ExecutiveStateBuilder` | observational -> advisory | tool-use / reflection posture only |
| `\Gamma_t` | selective write / read / influence gates | `GateState`, `ExecutiveStateBuilder` | observational -> advisory | sparse and advisory only |
| `\mathcal A_{t,r}^{pre}` | pre-brake admissible soft actions | `HostAffordanceFilter.pre_admissible_actions` | advisory | host- and gate-filtered |
| `\kappa_t=(\beta_t,\lambda_t^{pre},\chi_t)` | budget, pre-brake soft allocation, vigor | `ControlAllocationState`, `ControlAllocator` | advisory | updated by explicit + memory scorers; `\chi_t` is vigor, not assurance |
| `J_t^{brake}` | advisory brake latch | `SoftBrakeState`, `SoftBrakePolicy` | advisory | not a hard halt surface |
| `\mathcal A_{t,r}^{post}` | post-brake admissible soft actions | `HostAffordanceFilter.post_admissible_actions` | advisory -> realized | brake-filtered |
| `\Phi_t^-` | pre-control geometry | `PreControlGeometry`, `GeometryEncoder` | observational -> advisory | used by memory scoring and audits |
| `\Phi_t` | full audit geometry | `AuditGeometry`, `GeometryEncoder` | advisory -> evaluation | adds allocation point post-allocation |
| `W_t^{execmem}` | read-only learned support memory | `ExecutiveMemorySnapshot` | offline -> live snapshot | published only by offline distillation |
| `\Psi_c` | non-claim-bearing executive adjunct builder | `ExecutiveAdjunctBuilder` | proposed / render-only | typed proof seam |
| `\bar\Omega` | outward extension with adjunct | `ExecutiveRenderer` | proposed / render-only | claim-conservative |
| `\Pi_{claim}` | claim projection from extended outward object | `ClaimProjector` | proposed / render-only | typed proof seam |

The code consequence is simple:

- the kernel owns truth,
- executive code owns advisory control,
- adapter code owns realization under preservation,
- offline consolidation owns learned support memory only.

---

## 4. Approved biological mechanism map

| Mechanism name | Strongest biological claim we can honestly make | Evidence strength | Why this helps an agent | Mathematical analogue | Software analogue | Allowed influence surface | Forbidden influence surface |
|---|---|---|---|---|---|---|---|
| Abstraction gradient / frontopolar pending-goal management | human control is hierarchically organized; pending goals can be maintained while a subgoal is pursued | strong | prevents goal loss during local repair | `G_t` | `GoalState`, branch manager | branch proposal, pending-goal resume, reorient ranking | `H_t`, `D_t`, `B_t`, `C_t` |
| Dynamic control-network coupling | internally focused and externally focused control modes differ and can be switched | strong | lets the agent shift between reflection and external checking | `M_t^{mode}` | `ModeState` | tool-use posture, retrieval preference | waiving required evidence |
| Selective corticostriatal gating | gating in working control is selective, not just global | strong | prevents repeated useless reads/writes and supports anti-thrash behavior | `\Gamma_t` | `GateState` | advisory read/write/influence gating | suppressing real deficits or failed invariants |
| Gain control / inverted-U stability metaphor | control quality degrades under under-control and over-control regimes | analogy only | justifies vigor / budget regulation without diagnosis theater | `\chi_t` inside `\kappa_t` | `ControlAllocationState.vigor` | advisory intensity and retry restraint | completion truth, safety verdicts |
| dACC expected value of control | control allocation depends on cost, payoff, and difficulty | strong | gives a principled soft budget | `Q_t^{EX}`, `Q_t^{MF}`, `\kappa_t` | `ControlAllocator` | ranking, search depth, review / defer / branch budget | completion acceptance |
| IFG/preSMA/STN fast global brake | brains have fast interrupt circuitry distinct from selective gating | strong | motivates a bounded advisory brake for soft exploration | `J_t^{brake}` | `SoftBrakeState`, `SoftBrakePolicy` | stop soft exploration, escalate, handoff | safety / integrity hard halt |
| Uncertainty / threshold / checking dynamics | uncertainty affects decision thresholds and checking style | strong | prevents both rashness and endless futile checking | `U_t`, `\beta_t`, `\lambda_t^{pre}` | `UncertaintyState`, allocator | review pressure, search depth, defer pressure | lowering hard completion thresholds |
| Self-referential evaluation | self-evaluation shapes control, but not via one magical locus | strong | helps explicit self-audit and explanation discipline | explicit cost terms in `Q_t^{EX}` and rendering support | `SelfAuditPenalty`, `ExplanationPlanner` | review recommendation, explanation support | hidden mental-state claims, canonical claims |
| TPJ self-other distinction | self-other distinction helps perspective switching and social constraints | strong | useful as review / handoff perspective support | explanation and handoff support only | `PerspectiveReviewHint` | explanation / review support | truth mutation |
| vmPFC social value | value integrates harm/cost considerations in social contexts | strong | supports humane control-cost terms | explicit terms in `c_t^{ctrl}` | `RiskBurdenCostModel` | burden / risk / delay costs | pseudo-moral truth state |
| LPFC/OFC factorized geometry | goal and uncertainty can be factorized in representational space | promising | supports reusable similarity and robust evaluation | `\phi_c^-`, `d_\Phi` | `GeometryEncoder`, `GeometryAudit` | memory similarity, audits, branch similarity | truth certification |
| Active-inference precision as normative language | precision weighting is a useful language for uncertainty and policy weighting, but not a one-to-one map to transformers | analogy only | disciplines interpretation of uncertainty weighting | weighting rules in `U_t`, `\kappa_t` | design vocabulary only | parameter interpretation and evaluation language | claims of mechanistic equivalence |
| Bayesian model reduction as offline consolidation only | the useful import is offline utility-minus-complexity reduction of support memory | analogy only | compresses support memory without touching kernel law | `\operatorname{Distill}_{off}` over executive memory | `OfflineConsolidator` | repair priors, pattern priors, branch priors, calibration summaries | completion law, canonical claims, adapter semantics |

---

## 5. Explicit-control, memory-control, and realization seams

### 5.1 Explicit one-step control score

The explicit lane is

\[
Q_t^{EX} : \mathcal A_{t,r}^{pre}\to\mathbb R,
\]

where `Q_t^{EX}` is an explicit one-step control scorer over current-state features.
It is **not** a full predictive planner unless a real transition model is later implemented.

Software seam: `ControlAllocator.allocate`.

### 5.2 Memory-conditioned control score

The memory lane is

\[
Q_t^{MF} : \mathcal A_{t,r}^{pre}\to\mathbb R,
\]

where `Q_t^{MF}` uses the current pre-control geometry, or a discrete fallback key, to read soft-return priors from read-only executive memory.

Software seams: `GeometryEncoder.encode_pre`, `ExecutiveMemorySnapshot`, `ControlAllocator.allocate`.

### 5.3 Pre/post admissible action sets

The finished packet uses two admissible sets:

\[
\mathcal A_{t,r}^{pre}=\operatorname{Adm}_r^{pre}(\mathcal A^{soft},W_t^{host},\Gamma_t),
\]
\[
\mathcal A_{t,r}^{post}=\operatorname{Adm}_r^{post}(\mathcal A_{t,r}^{pre},J_t^{brake}).
\]

This keeps control allocation acyclic.

Software seams: `HostAffordanceFilter.pre_admissible_actions`, `HostAffordanceFilter.post_admissible_actions`.

### 5.4 Typed conservativity seam

The finished packet treats render-time conservativity as a first-class typed seam:

- `ExecutiveAdjunctBuilder.build` realizes `\Psi_c`,
- `ExecutiveRenderer.render` realizes `\bar\Omega`,
- `ClaimProjector.project` realizes `\Pi_{claim}`.

These interfaces exist to make the claim-conservativity law inspectable in code rather than only in prose.

---

## 6. One-sentence summary

**Every approved biological import is now mapped to one explicit mathematical owner and one explicit software seam, and every such seam is constrained to improve soft control without creating a second truth layer.**
