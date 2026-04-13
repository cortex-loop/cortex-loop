# CORTEX_V2_SRE_2

Surface: product

Status: canonical **SRE** document for the 3-document Cortex v2 packet (`active`; mediation extension `experimental / off-by-default`)
Companion documents: `CORTEX_V2_CORE_2.md`, `CORTEX_V2_AUX_2.md`

---

## 0. Purpose

This document defines the **official Standard Reference Executive** of Cortex v2.

Its job is to specify the active reference policy layer that sits on top of the core boundary contract:

- how the executive interprets recoverable role views from core,
- how it prices intervention versus neutrality,
- how it tracks uncertainty and applies brake,
- how it preserves the main task while opening, suspending, resuming, merging, or abandoning branches,
- how it exploits host-native opportunities without becoming a second truth court,
- and how richer control interactions may be staged without leaking into commitment certification.

This document is **not** constitutional core law.
It is the official reference control layer.

---

## 1. Layer position and authority

### 1.1 What SRE is

The Standard Reference Executive is the official reference implementation class for executive control in Cortex v2.

It is:
- normatively important,
- expected to be the default executive used by Cortex v2,
- and allowed to contain real policy math.

It is **not**:
- the integrity microkernel,
- the source of commitment truth,
- or a hidden adapter doctrine.

### 1.2 What SRE owns

The SRE owns:
- soft-control family selection,
- intervention budgeting,
- uncertainty-sensitive intervention,
- brake dynamics,
- branch and pending-goal discipline,
- host-native opportunity pricing,
- and optional richer interaction terms that remain microkernel-subordinate.

### 1.3 What SRE does not own

The SRE may not:
- certify commitments,
- redefine blockedness,
- lower hard boundaries,
- fabricate provenance sufficiency,
- or mutate the valid commitment-status lattice.

Those remain core-owned by `CORTEX_V2_CORE_2.md`.

### 1.4 Maturity split inside SRE

This document intentionally separates:

- **active reference policy**
- **experimental reference policy**

Active reference policy includes:
- arbitration and control allocation,
- uncertainty and brake,
- branch and goal control.

Experimental reference policy includes:
- mediation-aware control interaction.

Experimental content is official and auditable, but **off by default** until it earns lift.

### 1.5 Mathematical stance

The equations in this document are **reference semantics and design invariants**.
They describe the tradeoff structure a lawful SRE must recover or approximate.

They do **not** require a literal continuous solver, and they may be realized using:
- bounded scalar heuristics,
- ordinal bands,
- compact decision tables,
- filters,
- learned estimators,
- or mixed symbolic/latent machinery.

The primary implementation picture is **discrete and bounded**.
Continuous notation is secondary and explanatory.

### 1.6 Domain-general improvement rule

Future executive improvements should be framed first as **domain-general baskets**.

Representative baskets include:
- continuity / invariance preservation,
- constraint-fit,
- verification-fit,
- repair-without-drift,
- and other bounded executive control families that do not presume one artifact domain.

Domain-specific binding belongs outside SRE.
SRE owns the general executive basket, not the code-specific, writing-specific, or benchmark-specific adapter logic used to realize that basket on one proving surface.

---

## 2. SRE boundary contract with core

For runtime `r`, lifecycle event `\ell_t`, host payload `\omega_t`, passive observation `\mathcal O_{t,r}`, bounded executive environment view `\mathcal V_{t,r}`, support snapshot `\mathcal S_t`, and lifecycle/orchestration surface `L_r`, the SRE is constrained by the core law:

\[
\mathcal O_{t,r} = \operatorname{Observe}_r(\ell_t, \omega_t, L_r)
\]
\[
(\mathcal V_{t,r},\mathcal E_{t,r}) = \operatorname{BindEnv}_r(\mathcal O_{t,r},L_r)
\]
\[
\mathcal S_t = \operatorname{Snapshot}(\mathcal O_{t,r},W_t)
\]

The SRE may use:
- `\mathcal O_{t,r}`
- `\mathcal V_{t,r}`
- `\mathcal S_t`
- `L_r`
- bounded public hard-state shadows when core exposes them lawfully

The SRE may not read:
- hidden certifier internals,
- hidden provenance internals,
- or any same-event truth object that would violate the event-local certification firewall.

The SRE therefore solves a different question from the core:

- core: **may this be committed?**
- SRE: **how should soft control be allocated before commitment?**

---

## 3. Reference executive decomposition

The core requires recoverable role families.
The SRE chooses one official reference decomposition over those families.

The reference SRE state is:

\[
X_t^{ref} = (x_t^G, x_t^U, x_t^M, x_t^K, x_t^J)
\]

where:
- `x_t^G` = goal continuity and pending-goal discipline,
- `x_t^U` = uncertainty monitoring,
- `x_t^M` = mode and gating,
- `x_t^K` = control allocation state,
- `x_t^J` = brake state.

This is a **reference factorization**, not a constitutional requirement.
A lawful implementation may realize these roles through any internal representation so long as bounded role views remain recoverable.

### 3.1 Minimal software-shaped role views

To keep the reference policy operational without re-freezing one latent theorem, a lawful SRE should be able to recover bounded software-shaped views equivalent to:

- `goal_continuity`
  - main-goal identifier or anchor
  - active-track identifier
  - pending-goal count or bounded pending set
  - resume-anchor availability
- `uncertainty_monitoring`
  - classwise uncertainty vector or bounded scalar map
  - contradiction/spike flags
- `mode_and_gating`
  - current operating mode tag
  - active gate mask or equivalent enable/disable structure
- `control_allocation`
  - budget band
  - top-ranked soft family set
  - bounded host-friction summary
- `brake`
  - one of `{quiescent, guarded, latched}`
  - dominant cause family

These are the minimum software-facing views of the reference SRE.
They do not legislate one latent representation.

---

## 4. Soft-control family set

The SRE uses a bounded reference family set:

\[
\mathcal A^{ref} = \{\text{neutral},\text{seek-context},\text{redirect},\text{check},\text{branch},\text{escalate},\text{brake}\}
\]

Interpretation:
- `neutral` = continue without extra executive intervention,
- `seek-context` = request bounded additional context/evidence,
- `redirect` = narrow, restate, or re-aim the current path,
- `check` = perform bounded uncertainty-reducing verification,
- `branch` = open, resume, merge, suspend, or abandon an alternative track,
- `escalate` = request stronger host/orchestration assistance,
- `brake` = strongly curtail nonessential intervention.

These are **reference policy families**, not mandatory host verbs.

### 4.1 Native-opportunity specialization

The SRE may nominate a direct host-native opportunity when one is obvious and stronger than a generic family.

Examples:
- a structured context-retrieval tool,
- an MCP query,
- a host-native subagent surface,
- an approval request,
- or a direct stop/completion callback.

This means the SRE is not forced into a lossy “family then rediscover the real tool” loop.
The reference family set exists to preserve cross-host policy semantics, not to erase native opportunities.

### 4.2 Neutral-path law

Whenever the host allows ordinary continuation at the current lifecycle event,

\[
\text{neutral} \in \mathcal A_t^{pre}
\]

must remain available.

The executive must always retain a pass-through path where it chooses to spend no
additional executive control while still allowing ordinary task continuation.

### 4.3 Default pass-through law

If:
- no non-neutral family has a bounded advantage over `neutral`,
- or environment freshness is weak,
- or host mismatch makes intervention expensive,
- or uncertainty reduction is not expected to materially improve control,

then `neutral` is the mandatory default.

Here `neutral` means pass-through continuation without extra executive intervention,
not inactivity or silent surrender.
The SRE is a governor, not a scheduler searching for excuses to intervene.

---

## 5. Active reference policy

The active SRE policy has three coupled components:

1. arbitration and control allocation,
2. uncertainty and brake,
3. branch and goal control.

These components are separable for explanation but operationally coupled.

### 5.1 High-level event loop

At a lifecycle event, the active reference SRE computes:

\[
X_t^{ref} = \operatorname{Build}_{exec}(\mathcal O_{t,r},\mathcal S_t,\mathcal V_{t,r})
\]
\[
\mathcal A_t^{pre} = \operatorname{Adm}_r^{pre}(\mathcal A^{ref},\mathcal O_{t,r},\mathcal V_{t,r},L_r,x_t^M)
\]
\[
Q_t^{base}(a) = Q_t^{alloc}(a) + \lambda_G Q_t^{goalbranch}(a)
\]
\[
J_t = \operatorname{Brake}(x_t^U, x_t^G, x_t^K, \mathcal O_{t,r}, \mathcal V_{t,r}, L_r)
\]
\[
\mathcal A_t^{post} = \operatorname{Adm}_r^{post}(\mathcal A_t^{pre},J_t)
\]
\[
Q_t^{final}(a) = \operatorname{Finalize}^{exp}(Q_t^{base}, a)
\]
\[
U_t^{sre} = \operatorname{Select}^{soft}(X_t^{ref},Q_t^{final},\mathcal A_t^{post},L_r)
\]

where `U_t^{sre}` is the chosen soft-control output together with bounded diagnostics.

When no experimental extension is active, `\operatorname{Finalize}^{exp}` is the identity and `Q_t^{final}=Q_t^{base}`.
In a discrete runtime realization, `\mathcal A_t^{post}` may be enforced as brake-conditioned realization constraints after soft selection, provided selected-family truth and realized-family truth remain explicit and auditable.

### 5.2 Discrete reference realization law

A lawful reference implementation may realize the above loop using:
- bounded scalar heuristics,
- ordinal bands like `{low, medium, high}`,
- compact decision tables,
- thresholded comparisons,
- or a hybrid symbolic/learned policy,

provided that it preserves:
- neutral dominance,
- host-cost penalties,
- uncertainty-sensitive intervention,
- branch/goal continuity pressure,
- and the no-threshold-collapse law.

Continuous notation is explanatory.
Discrete bounded realization is the primary implementation picture.

---

## 6. Arbitration and control allocation

### 6.1 Reference control objective

The SRE should maximize task value while minimizing unnecessary executive burden and host mismatch:

\[
\max \; \mathbb E[V^{task} - C^{ctrl} - C^{host} - C^{vis}]
\]

subject to the core boundary contract.

Here:
- `V^{task}` = task progress / output value,
- `C^{ctrl}` = internal control burden,
- `C^{host}` = host mismatch / realization burden,
- `C^{vis}` = visible intervention burden imposed on the model/user interaction.

The explicit visible-burden term is deliberate.
One of v1’s main failures was that visible proof/control burden could become the task.
`C^{host}` should prefer measured bounded-probe evidence when a cheap lawful probe exists,
surface explicit probe-unavailable truth when no lawful probe path exists,
and only fall back to host-friction heuristics when probe evidence is unavailable.
`C^{vis}` is a contextual structured-audit cost, not a flat demand for silence.

### 6.2 Primary discrete realization

The primary reference realization is a bounded comparative scorer over admissible families.
A lawful implementation may produce, for each family `a`:

- a task-progress band,
- an uncertainty-reduction band,
- a goal-continuity band,
- a stability band,
- a control-burden band,
- a host-friction band, preferably backed by bounded-probe outcomes when available,
- a visible-burden band, scaled by the active explainability profile,

and then combine them using:
- a bounded weighted sum,
- a lexicographic/ordinal comparison,
- or a compact decision table.

### 6.3 Reference semantic score

For implementations that want a continuous explanatory form, define:

\[
Q_t^{online}(a)
=
 w_T q_t^{task}(a)
+ w_U q_t^{uncert}(a)
+ w_G q_t^{goal}(a)
+ w_S q_t^{stability}(a)
- w_C c_t^{ctrl}(a)
- w_H c_t^{host}(a)
- w_V c_t^{vis}(a)
\]

Interpretation:
- `q_t^{task}` = expected task-progress value,
- `q_t^{uncert}` = expected uncertainty reduction or uncertainty-sensitive stabilization,
- `q_t^{goal}` = preservation of main-goal and pending-goal continuity,
- `q_t^{stability}` = protection against pathological oscillation and fake churn while
  preserving productive messy search,
- `c_t^{ctrl}` = control burden,
- `c_t^{host}` = host mismatch / friction, preferably measured by bounded probes,
- `c_t^{vis}` = contextual structured-audit burden.

This equation is a reference semantics, not a demand for an online oracle.

### 6.4 Memory-conditioned score

Let `\psi_t` be a non-claim-bearing executive context signature recoverable from `x_t^G, x_t^U, x_t^M, \mathcal O_{t,r}, \mathcal S_t, \mathcal V_{t,r}`.
Then the reference memory-conditioned score is:

\[
Q_t^{mem}(a) = \operatorname{Agg}(\operatorname{Sim}(\psi_t,\psi_i), r_i(a))_{i\in\mathcal I_a}
\]

where support-memory entries `i` provide prior realized returns for family `a`.

If no usable support memory exists, set `Q_t^{mem}(a)=0` and surface that fact in diagnostics.

Hidden memory is forbidden.
Current landing law: on the active shipping and conformance lanes, `Q_t^{mem}(a)` remains
explicitly zero-valued until lawful AUX support-memory publication exists.
That is a deployment choice for the active shipping and conformance lanes, not conceptual
amnesia. The current runtime may surface `memory_score = 0.0` as a consumer/diagnostic
carrier, while explicit AUX-owned support memory remains lawful on bounded replay/evaluation
surfaces. Any nonzero `Q_t^{mem}(a)` must enter only through explicit AUX support-side
augmentation/publication rather than hidden host memory, prompt heuristics, runtime caches,
or softened closure logic.
Explicit host/tool reliability priors remain lawful only on bounded AUX and experimental
shadow surfaces until a separate seam proves broader ingress.
On those bounded shadow surfaces, reliability priors may modulate host-dependent
`Q_t^{mem}(a)` lift for `check`, native `seek-context`, and `branch` only.
Fresh contradiction, explicit probe-failure class evidence, or expired TTL must zero the
reliability-derived component rather than letting stale host confidence survive.
Any broader cross-host claim about that shadow lift is earned only to the extent that
lawful host-distinct evidence exists; if non-reference hosts alias under lawful
observables, the claim must narrow instead of pretending distinct lift was proved.

### 6.5 Combined score

\[
Q_t^{alloc}(a) = \alpha_t Q_t^{online}(a) + (1-\alpha_t)Q_t^{mem}(a)
\]

where `\alpha_t \in [0,1]` controls current-event vs memory reliance.
`\alpha_t` may depend on observation freshness, environment coverage, host degradation, and support-memory quality.
It may not depend on hidden same-event certifier internals.

Current landing law: until AUX earns a lawful support-side publication path,
shipping and conformance lanes may keep `Q_t^{mem}(a)=0` and therefore realize
`Q_t^{alloc}(a)` through the currently landed online plus goal-branch path.

### 6.6 Neutral-dominance law

Let

\[
\Delta_t(a) = Q_t^{alloc}(a) - Q_t^{alloc}(\text{neutral})
\]

for `a \neq neutral`.

Then non-neutral intervention is justified only if there exists an admissible family `a`
such that

\[
\Delta_t(a) \ge \theta_t^{act}(a).
\]

The activation gate is family-sensitive. Low-burden uncertainty-relief moves such as
`check` and native `seek-context` may use lower thresholds than more disruptive actions
like `branch`, visible `redirect`, or `escalate`.
If no family beats `neutral` by its required margin, the SRE should continue without extra intervention.

### 6.7 Budget and vigor

A reference intervention budget is represented at minimum by a bounded budget band:

\[
\beta_t \in \{\text{depleted},\text{low},\text{medium},\text{high}\}
\]

or an equivalent bounded scalar.

A reference vigor variable `\chi_t` may then scale the intensity of the chosen action while remaining bounded by:
- current budget,
- urgency,
- stall signals,
- and host friction.

### 6.8 What this section is and is not

This section is:
- a reference policy algebra,
- an implementation-facing scoring semantics,
- and a tuning surface.

It is not:
- literal online reinforcement learning,
- a requirement for exact continuous optimization,
- or a permission to insert heavy per-action prompting on every event.

---

## 7. Uncertainty and brake

### 7.1 Uncertainty classes

The reference uncertainty class set is:

\[
\mathcal C^U = \{\text{evidence},\text{environment},\text{host-capability},\text{goal-progress}\}
\]

with bounded per-class uncertainty estimates

\[
u_t(c) \in [0,1]
\]

or any bounded discrete equivalent.

These classes mean:
- `evidence` = uncertainty about facts relevant to control,
- `environment` = uncertainty about current world/workspace state,
- `host-capability` = uncertainty about what the host can actually realize now,
- `goal-progress` = uncertainty about whether the current path advances the main task or preserves pending-goal discipline.

### 7.2 Uncertainty source families

A lawful SRE may estimate uncertainty from:
- event-local signals,
- bounded environment view,
- host-affordance state,
- support priors,
- realization feedback.

Current-event and bounded-environment evidence should dominate stale support priors when they conflict.

### 7.3 Spike preservation

The SRE must preserve at least one recoverable spike quantity or equivalent summary.

Spikes include:
- contradiction between expected and observed host effect,
- sudden degradation,
- sharp goal-progress ambiguity,
- or new environment inconsistency.

Smoothing is allowed; spike erasure is not.

### 7.4 Brake states

The reference brake state set is:

\[
\mathcal B^{ref} = \{\text{quiescent},\text{guarded},\text{latched}\}
\]

Interpretation:
- `quiescent` = no active inhibition beyond ordinary neutral dominance,
- `guarded` = heightened selectivity and reluctance to spend control,
- `latched` = strong interruption of nonessential intervention.

### 7.5 Primary discrete brake realization

A lawful reference realization may compute brake using:
- classwise uncertainty bands,
- contradiction flags,
- repeated-failure or repeated-degradation counters,
- missing-resume-anchor flags,
- or bounded host-friction indicators.

The brake update may therefore be implemented as a compact decision table rather than a continuous differential law.
The preferred discrete realization uses hysteresis: guarded and latched may have separate
enter and exit thresholds, while contradiction and latching spikes remain immediate.

### 7.6 No-threshold-collapse law

Uncertainty may increase:
- review pressure,
- seek-context pressure,
- redirect pressure,
- branch pressure,
- or brake pressure.

It may **not** lower commitment certification standards.
It may not turn “wait long enough” into “call it done.”

### 7.7 Latched-state restriction law

When the brake is `latched`, the SRE may not choose any family that:
- expands branch search,
- adds speculative retrieval,
- or increases visible intervention burden

unless the chosen action is the minimum-burden lawful move that directly reduces the
dominant uncertainty source that caused the latch.

The currently landed relief action set is limited to `check` and native `seek-context`
when either is the cheapest lawful route to reduce the dominant uncertainty. A bounded
branch-resume/inspection move remains a future admissible realization, but it must be
implemented and separately proved before it becomes active doctrine.

---

## 8. Branch and goal control

### 8.1 Goal continuity law

The SRE must preserve the main task as an explicit control object.
Local repair, side investigations, and branch experiments may not silently replace the main task.
The reference executive should therefore be state-aware and closure-aware: when unresolved branch state, blocker risk, or pending-goal debt is salient, it should prefer truthful continuity and explicit closure over premature forward motion.

### 8.2 Pending-goal discipline

A branch-worthy subgoal must be:
- opened explicitly,
- suspended explicitly,
- resumed explicitly,
- merged explicitly,
- or abandoned explicitly.

Pending-goal discipline must remain recoverable in software, at least through:
- active track id,
- pending-goal count or bounded set,
- resume-anchor availability.

### 8.3 Branch operations

The reference branch family includes:
- `open`
- `suspend`
- `resume`
- `merge`
- `abandon`

A host may realize these through:
- subagents,
- orchestration branches,
- bounded inline markers,
- resumable context handles,
- or a degraded local approximation.

### 8.4 Branch budget law

Branch expansion is never free.
The preferred realization is an explicit branch-burden penalty based on active branch
count, resume-anchor quality, merge confidence, and pending-goal debt.
Count and depth limits are fallback safety mechanisms when richer burden evidence is
unavailable, not the preferred executive realization.

### 8.5 Goal-branch score

Let `Q_t^{goalbranch}(a)` denote the family contribution associated with preserving the main goal while manipulating branches.
A lawful SRE may estimate it using:
- goal continuity gain,
- resume-anchor confidence,
- branch burden,
- merge confidence,
- or abandon justification.

### 8.6 Branch degradation law

If the host lacks strong branch/orchestration surfaces, branch control must degrade explicitly rather than pretending strong branch support exists.

---

## 9. Experimental mediation extension

Status: **experimental / off-by-default**

### 9.1 Purpose

The mediation extension explores whether pairwise control interactions are too weak for some executive settings and whether third-party mediated interactions improve soft-control allocation.

### 9.2 Non-core and non-MVP law

Mediation is:
- not constitutional,
- not required for a lawful SRE,
- not required for MVP runtime,
- and not allowed to affect commitment truth.

### 9.3 Minimal active content

If enabled experimentally, mediation may only:
- modify `Q_t^{base}` into `Q_t^{final}`,
- remain sparse,
- remain host-aware,
- and preserve neutral dominance.

### 9.4 Anti-hub law

A lawful mediation extension must avoid collapsing control into one giant hub variable.
If a mediation implementation rewards maximal connectivity by default, it violates the design prior.

### 9.5 Evaluation gate

Mediation may remain enabled only if it shows measurable lift on at least one of:
- reduced thrashing,
- better branch discipline,
- better uncertainty handling,
- lower visible burden at equal task value,
- or better host-specialized realization.

Otherwise it should remain disabled or be removed.

---

## 10. Host-native realization within SRE

### 10.1 Family selection vs channel realization

The SRE chooses soft-control families or direct host-native opportunities.
The actual channel is then chosen by host-native realization.

These are distinct:
- family semantics remain cross-host policy objects,
- channel realization remains host-native.

### 10.2 Host-native opportunity law

When the host provides a clearly superior native opportunity, the SRE may directly nominate it.
This is preferred over needlessly abstract family indirection.

### 10.3 Degradation honesty

If the host cannot realize the preferred family or opportunity, the SRE must surface:
- preferred family/opportunity,
- realized family/opportunity,
- degradation reason,
- and whether `neutral` or `escalate` became the safer fallback.

---

## 11. Diagnostics and tuning

### 11.1 Control ledger

A lawful SRE should emit a compact control ledger per event or per relevant decision window, at least including:
- current event class,
- admissible soft families,
- selected family/opportunity,
- `Q_t^{base}` and `Q_t^{final}` or their discrete equivalents,
- dominant uncertainty sources,
- current brake state,
- budget band,
- degradation reason if any.

### 11.2 Tunable vs fixed

Tunable:
- executive tradeoff weights or bands,
- budget thresholds,
- branch penalties,
- uncertainty thresholds,
- host-friction penalties,
- visible-burden penalties,
- memory-reliance mixing.

Not tunable here:
- commitment truth,
- provenance sufficiency,
- hard boundaries,
- blockedness law.

### 11.3 Cheap-by-default law

Any lawful implementation should prefer the cheapest realization that preserves:
- neutral dominance,
- no-threshold-collapse,
- branch discipline,
- and host-realization honesty.

---

## 12. What is explicitly out of SRE

Out of SRE by law:
- commitment certification,
- blockedness truth,
- provenance sufficiency,
- hard safety/integrity boundaries,
- hidden adapter semantic ownership,
- geometry as a required runtime dependency,
- offline consolidation as live doctrine.

---

## 13. Final SRE statement

The Standard Reference Executive is the official control intelligence of Cortex v2.

Its job is to decide **how much** executive control to spend, **when** to spend it, **where** to spend it, and **when to stop spending it**.

It should be:
- cheaper than v1-style proof ritual,
- more host-native than adapter-era abstraction,
- more explicit than ad hoc prompt steering,
- and subordinate to the core commitment boundary at all times.
