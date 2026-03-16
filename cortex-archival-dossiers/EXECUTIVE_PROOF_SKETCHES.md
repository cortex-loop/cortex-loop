# EXECUTIVE_PROOF_SKETCHES

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: mathematical appendix to the finished executive packet  
Date: 2026-03-15  
Scope: compact theorem statements and proof sketches for the executive packet's main conservativity, acyclicity, non-authority, and monotonicity claims  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `EXECUTIVE_STATE_SPEC.md`, `EXECUTIVE_INTERFACES.md`, `GEOMETRY_AND_EVALUATION_SPEC.md`, and `OFFLINE_CONSOLIDATION_AND_BMR.md`  
Non-goal: a new constitution, a second theorem program, or a replacement for the kernel proof surfaces

---

## 0. Purpose

This appendix does one narrow job:

**state the executive packet's strongest mathematical claims in theorem form and sketch why they hold.**

It is intentionally modest.
These are proof sketches, not machine-checked proofs.
They exist to move the packet from “well-typed invariants” toward “finished mathematical object” without changing the packet's ontology.

The governing asymmetry is unchanged:

- the kernel owns completion truth,
- the executive layer owns only soft control,
- witness may be carried but not promoted into truth,
- offline learning may improve support but may not rewrite the law.

---

## 1. Standing notation

Fix runtime configuration `c` and a runtime realization target `r`.

The constitutional kernel law is

\[
\mathfrak K_c := (\eta_c,\alpha_c,\sigma_c,\nu,\rho,\pi,\Sigma,\Omega).
\]

The canonical kernel factorization is

\[
(H_t,D_t,S_t)=(\eta_c(E_t),\alpha_c(E_t),\sigma_c(E_t)),
\]
\[
K_t=(H_t,D_t,M_t),\qquad B_t=\nu(H_t),
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

Support state is

\[
W_t=(W_t^{grave},W_t^{retry},W_t^{execmem},W_t^{host},W_t^{trace}),
\]

where `W_t^{trace}` may include the support-only routing profile

\[
P_t^{route}=(\tau_t,\upsilon_t,\Delta_t,b_t)
\]

from the net-positive kernel program. This enrichment is support-only and not a new executive carrier.

and the executive derivation input is

\[
Y_t := (K_t,R_t,A_t,C_t,W_t).
\]

The finished executive overlay is

\[
Z_t=
\Xi_c(Y_t)
=
(G_t,U_t,M_t^{\mathrm{mode}},\Gamma_t,\kappa_t,J_t^{\mathrm{brake}}).
\]

Its lawful update order is

\[
\widehat Z_t := (G_t,U_t,M_t^{\mathrm{mode}},\Gamma_t),
\]
\[
\Phi_t^- := \phi_c^-(D_t,\widehat Z_t),
\]
\[
\mathcal A_{t,r}^{\mathrm{pre}} := \operatorname{Adm}_r^{\mathrm{pre}}(\mathcal A^{\mathrm{soft}},W_t^{host},\Gamma_t),
\]
\[
\kappa_t := \Xi_\kappa(Y_t,\widehat Z_t,\Phi_t^-,\mathcal A_{t,r}^{\mathrm{pre}}),
\]
\[
J_t^{\mathrm{brake}} := \Xi_J(Y_t,\widehat Z_t,\kappa_t),
\]
\[
\mathcal A_{t,r}^{\mathrm{post}} := \operatorname{Adm}_r^{\mathrm{post}}(\mathcal A_{t,r}^{\mathrm{pre}},J_t^{\mathrm{brake}}),
\]
\[
\Phi_t := (\Phi_t^-,\phi_\kappa(\kappa_t)).
\]

The typed conservativity operators are

\[
\Psi_c : \mathcal Y \times \widehat{\mathcal Z} \times \mathcal Kappa \times \mathcal J \times \Phi \to \mathcal X^{off},
\]
\[
\bar\Omega : \mathcal C \times \mathcal E \times \mathcal X^{off} \to \mathcal O^{ext},
\]
\[
\Pi_{\mathrm{claim}} : \mathcal O^{ext} \to \mathcal C.
\]

At the code layer:

- `KernelBoundaryView` is the read-only kernel import,
- `ExtendedBoundaryView` is the outward object with optional executive adjunct,
- `ClaimProjector.project` realizes `\Pi_{claim}`,
- `Build_pre`, `Alloc`, `Latch`, `Advise`, and `Realize_r` abbreviate the corresponding interfaces from `EXECUTIVE_INTERFACES.md`.

---

## 2. Assumption class

The sketches below use only assumptions already encoded elsewhere in the packet.

### A1. Kernel ownership
Only `H_t, D_t, M_t, R_t, A_t, C_t` are claim-bearing kernel carriers.
No executive object is a second owner of completion truth.

### A2. Canonical-source law
For every semantic theme that appears more than once in the outward boundary, exactly one source is authoritative.
In particular, canonical deficits are read from `KernelStateView.canonical_deficits`, not from any claim projection.

### A3. Opaque-witness law
The executive layer sees witness manifest metadata only, never raw witness payloads.

### A4. Read-only support law
Support imports and published executive-memory snapshots are immutable at runtime.
Route-profile support, if present inside `W_t^{trace}`, is read-only and non-authoritative.

### A5. Host-filter law
Unsupported host actions are removed, downgraded, or blocked explicitly; they are never synthesized silently.

### A6. Interface purity law
`ClaimProjector`, `ExecutiveRenderer`, `ExecutiveStateBuilder`, `ControlAllocator`, `SoftBrakePolicy`, and `HostAffordanceFilter` are pure with respect to the inputs named in their interfaces.

These are not new laws.
They are the packet's existing laws stated in proof-friendly form.

---

## 3. Claim conservativity

### Proposition 3.1
For every lawful executive adjunct,

\[
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,\Psi_c(Y_t,\widehat Z_t,\kappa_t,J_t^{\mathrm{brake}},\Phi_t))\big)=C_t.
\]

### Proof sketch
1. By construction, `\Psi_c` returns an adjunct in `\mathcal X^{off}`, not a claim-bearing object.
2. By interface law, `ExecutiveRenderer.render(claims, witness, adjunct)` returns an `ExtendedBoundaryView` whose `claims` field is the unchanged `KernelClaimsView`; adjunct data is carried separately.
3. By interface invariant, `ClaimProjector.project(ExecutiveRenderer.render(claims, witness, adjunct)) == claims` for every lawful adjunct.
4. Therefore projecting claims from the extended boundary returns exactly the original `C_t`.

The renderer may attach executive explanation.
It may not alter claim-bearing content.

### Implementation obligation
`ClaimProjector.project` must not inspect adjunct manifests when reconstructing `KernelClaimsView`.
If projector logic depends on adjunct content, this proposition fails.

---

## 4. Neutral removability

### Proposition 4.1
Let `x_0^{off} \in \mathcal X^{off}` be the designated neutral adjunct.
Then

\[
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,x_0^{off})\big)=C_t,
\]

and for every lawful adjunct `x \in \mathcal X^{off}`,

\[
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,x)\big)
=
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,x_0^{off})\big).
\]

### Proof sketch
1. The neutral adjunct carries no executive semantics beyond the executive-free baseline; in code this is `None` or an empty manifest object.
2. By Proposition 3.1, adding any lawful adjunct preserves `C_t` under claim projection.
3. Therefore the neutral adjunct preserves claims, and deleting any adjunct leaves the projected claims unchanged.

This is the packet's formal version of “the executive layer is removable.”
Deleting adjunct data may change explanation or audit detail, never the completion truth.

### Implementation obligation
The neutral adjunct must be a real, stable object with a fixed meaning.
If “empty” is left informal, removability becomes ambiguous.

---

## 5. Canonical-source non-ambiguity

### Proposition 5.1
Let `b,b'` be two boundary views and `s` a fixed support snapshot.
Assume

1. `b.state.hard_facts = b'.state.hard_facts`,
2. `b.state.canonical_deficits = b'.state.canonical_deficits`,
3. `b.state.memory = b'.state.memory`,
4. `b.transition = b'.transition`,
5. `b.action = b'.action`,
6. `b.witness = b'.witness`,
7. `s` is the same support snapshot in both evaluations,

while `b.claims.public_gap_projection` and `b'.claims.public_gap_projection` may differ arbitrarily.

Then for every lawful pre-state builder and pre-geometry encoder,

\[
\mathrm{Build}_{pre}(b,s)=\mathrm{Build}_{pre}(b',s),
\]
\[
\mathrm{Encode}_{pre}(\mathrm{Build}_{pre}(b,s),b.state.canonical_deficits)
=
\mathrm{Encode}_{pre}(\mathrm{Build}_{pre}(b',s),b'.state.canonical_deficits).
\]

### Proof sketch
1. By the canonical-source law, deficits have one authoritative owner: `KernelStateView.canonical_deficits`.
2. `KernelClaimsView.public_gap_projection` is presentation only.
3. `Build_pre` and `GeometryEncoder.encode_pre` are required to consume authoritative deficits only.
4. Therefore changing claim-side public projections while holding authoritative state fixed cannot change pre-state or pre-geometry.

So duplicate projections do not create a second truth layer.
They can only mis-state the source if an implementation illegally reads from the projection.

### Implementation obligation
Any executive consumer that reads deficits from `public_gap_projection` instead of `canonical_deficits` violates the theorem.

---

## 6. Acyclicity of the executive update order

### Proposition 6.1
The finished executive update graph is acyclic.

### Proof sketch
Define a dependency graph whose vertices are

\[
Y_t,
G_t,
U_t,
M_t^{\mathrm{mode}},
\Gamma_t,
\Phi_t^-,
\mathcal A_{t,r}^{\mathrm{pre}},
\kappa_t,
J_t^{\mathrm{brake}},
\mathcal A_{t,r}^{\mathrm{post}},
\Phi_t.
\]

Add directed edges exactly when a variable appears on the right-hand side of another variable's update law.
By construction the only edges are

\[
Y_t \to G_t,
\qquad
(Y_t,G_t) \to U_t,
\qquad
(Y_t,G_t,U_t) \to M_t^{\mathrm{mode}},
\qquad
(Y_t,G_t,U_t,M_t^{\mathrm{mode}}) \to \Gamma_t,
\]
\[
(D_t,\widehat Z_t) \to \Phi_t^-,
\]
\[
(W_t^{host},\Gamma_t) \to \mathcal A_{t,r}^{\mathrm{pre}},
\]
\[
(Y_t,\widehat Z_t,\Phi_t^-,\mathcal A_{t,r}^{\mathrm{pre}}) \to \kappa_t,
\]
\[
(Y_t,\widehat Z_t,\kappa_t) \to J_t^{\mathrm{brake}},
\]
\[
(\mathcal A_{t,r}^{\mathrm{pre}},J_t^{\mathrm{brake}}) \to \mathcal A_{t,r}^{\mathrm{post}},
\]
\[
(\Phi_t^-,\kappa_t) \to \Phi_t.
\]

A topological order is therefore

\[
Y_t,
G_t,
U_t,
M_t^{\mathrm{mode}},
\Gamma_t,
\Phi_t^-,
\mathcal A_{t,r}^{\mathrm{pre}},
\kappa_t,
J_t^{\mathrm{brake}},
\mathcal A_{t,r}^{\mathrm{post}},
\Phi_t.
\]

No edge points backward in that ordering, so the graph is a DAG.

The key fix relative to earlier drafts is the pre-brake / post-brake split:
allocation consumes `\Phi_t^-` and `\mathcal A_{t,r}^{pre}` only; braking is applied strictly afterward.
That removes the earlier self-reference.

### Implementation obligation
If an implementation computes allocation from full `\Phi_t` rather than `\Phi_t^-`, or lets `J_t^{brake}` feed back into `\Xi_\kappa`, it can reintroduce a cycle.

---

## 7. Witness non-authority

### Proposition 7.1 (strong form)
If two boundary views differ only in raw witness payloads while exposing the same `WitnessManifestView`, then for every lawful `Build_pre`, `Alloc`, `Latch`, and `Advise`, the resulting executive outputs are identical.

### Proof sketch
1. By the opaque-witness law, raw witness payloads are not in the domain of the canonical executive interfaces.
2. Executive builders, allocators, brake policies, and advisors see only `WitnessManifestView` metadata.
3. Therefore changing raw witness payloads while holding the manifest fixed leaves all executive inputs fixed.
4. By interface purity, the outputs are identical.

### Proposition 7.2 (weak form)
Changing witness manifests may change outward support metadata or advisory presentation, but may not change canonical claims or kernel truth. Formally,

\[
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,\Psi_c(\cdot,w))\big)
=
\Pi_{\mathrm{claim}}\big(\bar\Omega(C_t,E_t,\Psi_c(\cdot,w'))\big)
=
C_t
\]

for any witness-manifest arguments `w,w'` supplied lawfully through the executive adjunct path.

### Proof sketch
This is a direct consequence of Proposition 3.1.
Witness may help transport or summarize support artifacts.
It may not become a second truth owner.

### Implementation obligation
If an implementation rehydrates and consumes raw witness payloads during pre-state building or allocation, the strong form fails immediately.

---

## 8. Offline non-interference

### Proposition 8.1
Offline consolidation does not interfere with the constitutional kernel law.
Formally,

\[
\operatorname{Dep}(\mathfrak K_c, M_n^{exec})=\varnothing,
\qquad
\operatorname{Dep}(\mathfrak K_c, \Theta_n^{cal,pub})=\varnothing.
\]

Equivalently, replacing or removing the published snapshot

\[
W_t^{execmem}=\operatorname{Snap}(M_n^{exec},\Theta_n^{cal,pub})
\]

cannot change `\nu`, `\Sigma`, requirement truth, invariant truth, or completion acceptance for fixed `E_t` and configuration `c`.

### Proof sketch
1. The consolidation spec allows only two writable offline targets: executive support memory and published calibration summaries.
2. Those targets re-enter the live system only as a read-only snapshot inside support state.
3. By the separation invariant, the constitutional kernel law has no dependency on those writable offline objects.
4. Therefore any offline update can affect only executive support consumers such as repair priors, branch priors, soft-control scorers, and other non-claim-bearing advisory pathways.
5. Since completion truth depends only on `\mathfrak K_c` and its canonical inputs, snapshot changes cannot modify completion truth.

### Corollary 8.2
If swapping one admissible published snapshot for another changes `B_t`, `C_t`, or kernel-owned acceptance for fixed `E_t` and `c`, then the implementation is non-compliant.

### Implementation obligation
`ExecutiveMemoryReader.load()` must return read-only support state.
No live path may mutate `\mathfrak K_c` or kernel-owned carriers from offline artifacts.

---

## 9. Host-degradation monotonicity

### Proposition 9.1
Let runtime affordance states be ordered pointwise by capability:

\[
h_1 \preceq h_2
\]

iff all of the following hold:

- for every soft action `a`, `SupportLevel(h_1,a) \le SupportLevel(h_2,a)` in the order `NONE < ASSISTED < NATIVE`,
- `branch_cap(h_1) \le branch_cap(h_2)`,
- `retrieval_depth_cap(h_1) \le retrieval_depth_cap(h_2)`,
- `supports_structured_witness(h_1) \le supports_structured_witness(h_2)`.

Define a realization preorder `\sqsubseteq` on realized plans by requiring:

1. `pre_admissible_actions(P_1) \subseteq pre_admissible_actions(P_2)`,
2. `post_admissible_actions(P_1) \subseteq post_admissible_actions(P_2)`,
3. `realized_retrieval_depth(P_1) \le realized_retrieval_depth(P_2)`,
4. `realized_branches(P_1)` is no richer than `realized_branches(P_2)`,
5. `BLOCKED \sqsubseteq DEGRADED \sqsubseteq EXACT`,
6. every degradation is reason-coded explicitly.

If `HostAffordanceFilter` is monotone with respect to `\preceq`, then

\[
h_1 \preceq h_2
\implies
\operatorname{Realize}_{h_1}(\mathcal E_t^{adv})
\sqsubseteq
\operatorname{Realize}_{h_2}(\mathcal E_t^{adv}).
\]

### Proof sketch
1. Pre-admissible actions are computed from host affordances and gates only.
2. If `h_1 \preceq h_2`, then every action supported on `h_1` is also supported at least as strongly on `h_2`, and all quantitative caps on `h_1` are no larger.
3. Therefore `\mathcal A_{t,h_1}^{pre} \subseteq \mathcal A_{t,h_2}^{pre}`.
4. Post-admissible actions are obtained by applying the same brake latch to the respective pre-admissible sets; subset inclusion is preserved.
5. By the realization interface, unsupported actions may only be preserved, downgraded explicitly, clipped quantitatively, or blocked. Silent strengthening is forbidden.
6. Hence moving to a weaker host can only preserve or reduce executive realization; it can never increase it.

### Important limit
This is a proof obligation, not a free theorem.
It depends on `HostAffordanceFilter` and adapter realization actually preserving the monotone order.
The interfaces are designed so that monotonicity is inspectable rather than implicit.

### Implementation obligation
A host filter that silently invents support, maps a blocked action to a stronger one, or increases retrieval / branch capacity under degradation violates the theorem.

---

## 10. What this appendix does and does not finish

These sketches are enough to make the packet's central executive safety story explicit:

- executive adjuncts preserve claims,
- adjuncts are removable,
- duplicate projections do not create second truth,
- the executive update law is acyclic,
- witness is non-authoritative,
- offline learning cannot rewrite the kernel,
- weaker hosts may only degrade executive realization.

They do **not** claim:

- full mechanized proof,
- universal closure for arbitrary future hosts,
- statistical closure for every geometry metric,
- or a replacement for the kernel theorem program.

That is intentional.
The kernel remains the theorem-backed constitutional core.
This appendix proves only what the executive packet needs in order to stay subordinate, explicit, and honest.

---

## 11. One-sentence summary

**The executive packet is mathematically safe because every lawful implementation preserves claims, keeps deficits single-sourced, computes soft control in an acyclic order, treats witness and offline learning as non-authoritative, and degrades monotonically across weaker hosts.**
