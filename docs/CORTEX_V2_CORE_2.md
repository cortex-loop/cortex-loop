# CORTEX_V2_CORE_2

Surface: product

Status: canonical **core** document for the 3-document Cortex v2 packet (`active`)
Companion documents: `CORTEX_V2_SRE_2.md`, `CORTEX_V2_AUX_2.md`

---

## 0. Purpose

This document defines the smallest universal law of Cortex v2.

The core owns only what must remain stable across hosts and executive implementations:

- lifecycle-first runtime law,
- internal typed semantics and external native-realization precedence,
- the integrity microkernel,
- commitment extraction / certification law,
- bounded observation and environment access,
- the event-local certification firewall,
- degradation and contradiction preservation,
- minimal recoverability requirements for executive role views,
- and the proof obligations that keep those boundaries intact.

The core is intentionally **sparse**.
It is not the active intelligence of Cortex.
It is the integrity-preserving operating substrate around which the executive runs.

---

## 1. The 3-document packet

Cortex v2 is organized as exactly three packet documents.

### 1.1 Core

This document.

The core owns:
- lifecycle-first runtime law,
- internal typed semantics and external native-realization precedence,
- the integrity microkernel,
- commitment extraction/certification law,
- bounded environment access,
- the executive/non-executive firewall,
- degradation and contradiction preservation,
- minimal recoverability requirements for executive role views,
- and the proof obligations that keep those boundaries intact.

### 1.2 SRE

The Standard Reference Executive document owns:
- soft-control family policy,
- uncertainty-sensitive intervention,
- branch and goal control,
- brake dynamics,
- control allocation and arbitration,
- and any official reference executive strategy.

The SRE is the **official reference executive intelligence** of Cortex v2.
It is normatively important but not constitutional truth.

### 1.3 AUX

The auxiliary document owns:
- geometry/evaluation,
- offline consolidation / BMR-like support learning,
- and any other official but removable modules.

Auxiliary modules may shape advisory control and evaluation.
They may not become a second truth court.

---

## 2. Governing design laws

### 2.1 Lifecycle-first

Cortex v2 is organized around real host lifecycle/orchestration events, not around a monolithic final-stop object and not around one abstract central planner.

### 2.2 Packet-first, internally

Inside Cortex, observations, commitment candidates, provenance manifests, executive views, and realization plans are typed semantic objects.

### 2.3 Native-transport precedence, externally

Outside Cortex, the strongest native host surface takes precedence:
- tools,
- tool intercepts,
- approvals,
- stop/completion callbacks,
- MCP-style context/tool protocols,
- orchestration streams,
- bounded prose/context injection when no better structured surface exists.

Cortex v2 does **not** require the model to speak one proprietary external Cortex packet language.

### 2.4 Executive-first

Active intelligence lives in the executive layer, not in a large enforcement core.
The core constrains and certifies. The executive paces, routes, queries, branches, and reviews.

### 2.5 Microkernel-limited

The hard center is limited to:
- irreversible commitments,
- provenance sufficiency,
- blocked/stuck truth,
- and hard safety/integrity boundaries.

### 2.6 Host-affordance-native

One coherent system may have different host-native realizations.
Model-agnostic means shared law with different native realizations, not identical runtime behavior.

### 2.7 Sparse and governing

The core should stay short, decision-useful, and structurally constraining.
If a mechanism can be removed without changing commitment truth or lifecycle law, it does not belong here.

---

## 3. Core factorization

For host/runtime `r`, lifecycle event `\ell_t`, host payload `\omega_t`, support state `W_t`, and realized interaction `Y_t`, the governing factorization is:

\[
\text{Cortex v2}
=
\text{Core}
\oplus
\text{SRE}
\oplus
\text{AUX}
\]

with

\[
\text{Core}
=
(L_r,\; \mathfrak I_c,\; \mathfrak B_c)
\]

where:
- `L_r` = lifecycle/orchestration surface of runtime `r`,
- `\mathfrak I_c` = integrity microkernel,
- `\mathfrak B_c` = boundary contract between the core and all executive/auxiliary policy.

The core-level objective is:

\[
\max\;\mathbb E[V^{task} - C^{ctrl} - C^{host}]
\quad\text{subject to}\quad
\operatorname{CommitStatus}(Y_t)\in\mathcal S^{valid}
\]

Interpretation:
- `V^{task}` = output/task value,
- `C^{ctrl}` = executive intervention burden,
- `C^{host}` = host mismatch / realization cost,
- `\mathcal S^{valid}` = the valid commitment-status lattice.

Only the SRE and AUX may use weights to trade off control burden, uncertainty, retrieval, branching, or review pressure.
The core may not treat commitment truth as an ordinary ranking weight.

---

## 4. Lifecycle surface law

For each runtime `r`, define a lifecycle/orchestration surface:

\[
L_r=(E_r, A_r^{ctx}, A_r^{tool}, A_r^{turn}, A_r^{orch}, A_r^{mcp}, R_r)
\]

where:
- `E_r` = host event substrate,
- `A_r^{ctx}` = startup/session context injection affordance,
- `A_r^{tool}` = tool and tool-intercept affordance,
- `A_r^{turn}` = stop/turn-completion affordance,
- `A_r^{orch}` = orchestration affordance (streaming control, branching, subagents, approvals, handoff, or equivalent),
- `A_r^{mcp}` = external tool/context protocol affordance,
- `R_r` = host effect map from realized packets/actions to runtime consequences.

Core laws:

1. Cortex may only realize control through surfaces present in `L_r`.
2. Unsupported capability degrades to explicit `degraded`, `uncertified`, or `blocked` with reasons.
3. No host may silently inherit missing surfaces through undocumented adapter compensation.
4. Stop/completion is one lifecycle region among several, not the conceptual center of the system.

### 4.1 Extensible event law

The core does **not** define a closed universal host timeline.
Each event envelope must support:
- the host’s native event name,
- a set of canonical facets,
- optional host-specific extension tags.

Canonical facets are intentionally small and extensible, for example:
- `session/start`
- `context/load`
- `tool/pre`
- `tool/post`
- `turn/complete`
- `approval/request`
- `approval/result`
- `external/observation`

No lawful implementation may require all host events to collapse exhaustively into a fixed enum.

### 4.2 Extensible channel law

Channel semantics are tag-based rather than locked to one closed enum.
A realization may be tagged with canonical classes such as:
- `tool`
- `mcp`
- `hook_payload`
- `orchestration_rpc`
- `approval`
- `bounded_prose`

plus host-specific extension tags.

---

## 5. Runtime dispatch law

The core runtime law is **event-dispatched**, not a mandatory synchronous gauntlet.
All lifecycle events pass through cheap observation.
Only commitment-relevant events traverse the full microkernel path.

### 5.1 Canonical cheap path

Every event must support the cheap path:

\[
\mathcal O_{t,r}=\operatorname{Observe}_r(\ell_t,\omega_t,L_r)
\]
\[
(\mathcal V_{t,r},\mathcal E_{t,r})=\operatorname{BindEnv}_r(\mathcal O_{t,r},L_r)
\]
\[
\mathcal S_t=\operatorname{Snapshot}(\mathcal O_{t,r},W_t)
\]
\[
X_t=\operatorname{Build}_{exec}(\mathcal O_{t,r},\mathcal S_t,\mathcal V_{t,r})
\]
\[
U_t^{soft}=\operatorname{Select}^{soft}(X_t,\mathcal O_{t,r},\mathcal S_t,\mathcal V_{t,r},L_r)
\]
\[
Y_{t,r}^{soft}=\operatorname{Realize}^{soft}_r(U_t^{soft},\mathcal O_{t,r},L_r)
\]

This cheap path is the default runtime path for ordinary events.

### 5.2 Cheap non-commit events

For ordinary stream, context, observation, non-risk tool, or other non-commitment events:
- the system runs the cheap path only,
- no default commitment extraction is required,
- no default provenance gathering is required,
- no default certification is required.

### 5.3 Pre-risk or candidate-bearing events

For events that may imply a later commitment:
- the system still begins with the cheap path,
- then may run lightweight candidate extraction,

\[
K_t=\operatorname{Extract}_{commit}(\mathcal O_{t,r},L_r)
\]

only if the event surface plausibly proposes a commitment candidate.

A failed or empty extraction does **not** trigger heavy provenance collection.

### 5.4 Full commitment path

Only commitment-woken events may traverse the full path:

\[
K_t=\operatorname{Extract}_{commit}(\mathcal O_{t,r},L_r)
\]
\[
P_t(c)=\operatorname{Collect}_{prov}(c,\mathcal O_{t,r},\mathcal E_{t,r})
\]
\[
H_t(c)=\operatorname{Check}_{boundary}(c,\mathcal O_{t,r},\mathcal E_{t,r})
\]
\[
S_t^{commit}(c)=\operatorname{Certify}_c(c,P_t(c),H_t(c))
\]
\[
Y_{t,r}^{commit}=\operatorname{Realize}^{commit}_r(S_t^{commit},\mathcal O_{t,r},L_r)
\]

### 5.5 No-gauntlet law

No lawful implementation may require every event — especially streaming chunks, light tool hooks, or passive observations — to execute the full commitment path by default.

---

## 6. Observation vs environment law

### 6.1 Event-local observation

`\mathcal O_{t,r}` must stay lightweight.
It may include:
- current host payload,
- current event metadata,
- already-produced runtime records,
- already-attached structured observations.

It must **not** require eager global state gathering on every event.

### 6.2 Split environment handles

`BindEnv_r(...)` must yield two read-only environment surfaces.

#### Executive environment view `\mathcal V_{t,r}`
A bounded read-only environment view for soft control.
It may support cheap or selectively bounded queries relevant to:
- uncertainty,
- routing,
- context-seeking,
- branch fit,
- host affordance checks,
- and pacing.

It may not certify commitments.

#### Commitment environment handle `\mathcal E_{t,r}`
A stronger read-only handle for:
- provenance gathering,
- hard-boundary checks,
- and commitment-time evidence collection.

This handle may be more expensive.
It is not handed directly to soft control for truth decisions.

### 6.3 Generalized query language

The core query vocabulary must stay domain-agnostic.
Canonical query kinds include:
- `STATE_SNAPSHOT`
- `STATE_DIFF`
- `EXECUTION_TRACE`
- `RESULT_ARTIFACT`
- `CAPABILITY_VIEW`
- `EXTERNAL_RECORD`

Domain-specific environments may refine these through metadata or extension tags.
No lawful core may assume a coding-only world.

---

## 7. Integrity microkernel

The integrity microkernel is the only hard owner of commitment truth.

### 7.1 Commitments

A commitment candidate is any event-local proposal or host-native surface that could imply:
- task completion,
- irreversible submission,
- durable write/commit,
- external effect with policy relevance,
- or an explicit claim that must be certifiable.

### 7.2 Commitment status lattice

The valid lattice is:
- `CERTIFIED`
- `UNCERTIFIED`
- `BLOCKED`

Interpretation:
- `CERTIFIED`: commitment supported by sufficient provenance and no violated hard boundary.
- `UNCERTIFIED`: insufficient support for certification, but not necessarily a hard stop on ordinary conversation/control.
- `BLOCKED`: hard boundary violation, mandatory stop condition, or impossible/forbidden commitment.

### 7.3 Downward provenance dominance

Provenance must be gathered downward first, in priority order from:
- lifecycle traces,
- tool outputs,
- state diffs,
- execution traces,
- approvals,
- MCP/external artifacts,
- structured runtime records,
- and only then model statements as fallback.

### 7.4 Commitment wake law

The full commitment path may run only when at least one wake condition is true.

A commitment wake occurs when:
1. the current event belongs to a host/runtime commitment subset `E_r^{commit}`,
2. a structured or extracted commitment candidate is present,
3. the host marks the action as externally consequential or approval-gated,
4. a durable write / publish / submit / externally visible claim is about to occur,
5. or a hard safety/integrity boundary check is explicitly required by policy.

Absent one of these conditions, the core must not force heavy commitment-time processing.

### 7.5 Commitment-event sparsity

The microkernel is event-sparse by law.
Its full certifier path should activate on commitment events, not on every tick of the runtime.

---

## 8. Core boundary contract with the executive

### 8.1 Firewall law

The executive may influence future observations only through lawful realized control.
It may not directly alter same-event commitment certification inputs except through:
- choosing a lawful soft action,
- causing later host/runtime consequences,
- and then letting those later consequences be observed normally.

This is the event-local certification firewall.

### 8.2 Executive role recoverability

The core does **not** legislate one exact executive carrier theorem.
A lawful executive need only expose recoverable views for these role families:

- goal continuity / pending-goal discipline,
- uncertainty monitoring,
- mode/gating,
- control allocation,
- brake state.

The core requires recoverability, not one exact latent factorization.

### 8.3 Soft-control capability-family law

The core does **not** define fixed executive verbs.
It requires only that a lawful executive can represent capability families equivalent in function to:

- zero-intervention continuation,
- context-seeking or evidence-seeking,
- local redirection / narrowing,
- bounded checking or verification,
- branch-track manipulation,
- escalation to stronger host assistance,
- and control curtailment / brake.

The exact family names and internal scoring belong to the SRE, not the core.

---

## 9. Realization law

For any soft or commitment-side result, realization is host-native and effect-preserving.

\[
\operatorname{Realize}^{soft}_r(\cdot)
\]
and
\[
\operatorname{Realize}^{commit}_r(\cdot)
\]

must:

1. preserve the core distinction between soft control and commitment outcomes,
2. use the strongest native host surface available,
3. record degradation explicitly when a desired surface is unavailable,
4. avoid inventing hidden semantic owners inside the adapter.

No adapter may become a second truth court.

---

## 10. Degradation and contradiction law

Unsupported or partially supported host behavior must degrade explicitly with:
- reason codes,
- capability tags,
- and contradiction-preserving records.

The core must preserve, not smooth over:
- native vs assisted differences,
- available vs degraded capability,
- row-capturable vs non-row-capturable behavior,
- and mixed evidence over time.

---

## 11. Core proof obligations

A lawful core must preserve the following obligations.

### 11.1 Event-local certification firewall
Same-event executive preference may not directly certify commitment truth.

### 11.2 Downward provenance dominance
Host/tool/environment evidence outranks model prose for commitment support.

### 11.3 Native-realization conservativity
Realization may degrade or re-channel control; it may not silently change commitment semantics.

### 11.4 Adapter non-sovereignty
Adapters may realize; they may not own truth.

### 11.5 Commitment-event sparsity
The full certifier path is commitment-woken, not globally mandatory.

### 11.6 Support-memory non-sovereignty
Support state and later auxiliary memories may bias soft control; they may not rewrite commitment law.

### 11.7 Contradiction preservation
Mixed host evidence must remain representable.

---

## 12. Parameter discipline

The core should expose only sparse, boundary-level parameters.
Permissible core parameters include:
- hard-boundary constants,
- commitment wake thresholds or equivalent wake rules,
- provenance sufficiency constants,
- and commitment-status cut lines.

The following do **not** belong to core parameterization:
- executive tradeoff weights,
- retrieval/branch/check preferences,
- uncertainty heuristics,
- visible burden penalties,
- or memory-conditioned policy weights.

Those belong to the SRE or AUX.

---

## 13. What is explicitly out of core

The following are out of core by law:

- executive scoring and arbitration formulas,
- uncertainty policy,
- brake dynamics beyond the existence of a recoverable brake role,
- branch/goal policy,
- mediation-aware policy,
- geometry/evaluation,
- offline consolidation / BMR-like support learning,
- any hidden adapter doctrine,
- and any “completion by aesthetic confidence” rule.

---

## 14. Naming and migration rule

This document replaces the need to treat earlier v2 constitution/interface/state/proof documents as separate core authorities.
Those earlier drafts remain historical inputs.
This document is the packet-level core source of truth for the `_2` packet.

---

## 15. Final core statement

Cortex v2 core is a lifecycle-first, packet-typed, host-native operating substrate with a tiny integrity microkernel.

Its job is not to think for the agent.
Its job is to ensure that:
- lifecycle control is lawful,
- host-native realization is honest,
- commitment truth remains certifiable,
- executive control remains non-sovereign over truth,
- and the rest of the architecture can become richer without re-growing a monolithic enforcement core.
