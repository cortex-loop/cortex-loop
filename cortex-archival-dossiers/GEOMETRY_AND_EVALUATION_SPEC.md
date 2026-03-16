# GEOMETRY_AND_EVALUATION_SPEC

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: canonical specification for executive geometry and its evaluation program  
Date: 2026-03-15  
Scope: typed geometry derived from canonical deficit state and the pre-control executive state, together with the metrics and protocols that decide whether geometry is useful rather than decorative  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `EXECUTIVE_STATE_SPEC.md`, `EXECUTIVE_INTERFACES.md`, and `BIOLOGY_TO_MATH_TO_CODE.md`  
Non-goal: replacing canonical deficit state, certifying completion by vector proximity, or using embeddings as a second truth layer

---

## 0. Purpose

This document answers one narrow question:

**How may Cortex use LPFC/OFC-style factorization and geometry to improve advisory control and evaluation without allowing geometry to become a second truth language?**

The answer is:

- canonical truth remains discrete,
- geometry is derived,
- geometry is active in advisory control,
- geometry is subordinate to truth,
- geometry must continually earn its keep by control lift or evaluation lift.

In plain language:

**Geometry is a useful shadow of state, not the owner of state.**

---

## 1. The auxiliary-geometry law

Let the canonical kernel remain

\[
(H_t,D_t,S_t)=(\eta_c(E_t),\alpha_c(E_t),\sigma_c(E_t)),
\qquad
K_t=(H_t,D_t,M_t).
\]

Let the pre-control executive state be

\[
\widehat Z_t=(G_t,U_t,M_t^{mode},\Gamma_t).
\]

The lawful geometry map is

\[
\Phi_t^-=\phi_c^-(D_t,\widehat Z_t),
\qquad
\Phi_t=(\Phi_t^-,\phi_\kappa(\kappa_t)).
\]

Geometry therefore reads:

- canonical deficits `D_t`,
- pre-control executive state `\widehat Z_t`,
- allocation state `\kappa_t` only at the audit stage.

If route-profile support `P_t^{route}` exists inside `W_t^{trace}`, it does not become geometric truth by default and may influence geometry only through separately authorized pre-control executive state.

Geometry does **not** read:

- hard verdicts as an authority signal,
- canonical claims as a substitute for state,
- raw witness payloads.

### 1.1 Truth-subordination law

Geometry is auxiliary to truth but active in advisory control.

That means:

\[
\Phi_t^- \to Q_t^{MF} \to \kappa_t \to J_t^{brake} \to \mathcal A_{t,r}^{post} \to \mathcal E_t^{adv}
\]

is lawful,

provided that pre-admissibility is established first via
\[
\mathcal A_{t,r}^{pre}=\operatorname{Adm}_r^{pre}(\mathcal A^{soft},W_t^{host},\Gamma_t),
\]
so that allocation remains defined on a pre-brake action domain and the brake acts only as a later mask.

but

\[
\Phi_t^- \not\to \nu,\Sigma,\text{requirements},\text{invariants}
\]

is forbidden.

The exact claim-conservativity statement is still

\[
\Pi_{\mathrm{claim}}(\bar\Omega(C_t,E_t,\Psi_c(Y_t,\widehat Z_t,\kappa_t,J_t^{brake},\Phi_t)))=C_t.
\]

---

## 2. Typed geometry

The canonical product space is

\[
\Phi^- = \Phi_D \times \Phi_G \times \Phi_U \times \Phi_M \times \Phi_\Gamma.
\]

Accordingly,

\[
\Phi_t^- = (\Phi_t^D,\Phi_t^G,\Phi_t^U,\Phi_t^M,\Phi_t^\Gamma)
\]

with

\[
\Phi_t^D=\iota_D(D_t),\quad
\Phi_t^G=\phi_G(G_t),\quad
\Phi_t^U=\phi_U(U_t),\quad
\Phi_t^M=\phi_M(M_t^{mode}),\quad
\Phi_t^\Gamma=\phi_\Gamma(\Gamma_t).
\]

The full audit geometry adds

\[
\Phi_t^\kappa=\phi_\kappa(\kappa_t),
\qquad
\Phi_t=(\Phi_t^-,\Phi_t^\kappa).
\]

By default, `J_t^{brake}` is not embedded in the main geometry.
It is a categorical latch, not a useful similarity-bearing coordinate.

---

## 3. Typed distance

A lawful distance family has the form

\[
d_\Phi(x,y)=\sum_{j\in\{D,G,U,M,\Gamma,\kappa\}} \lambda_j d_j(x_j,y_j),
\qquad \lambda_j\ge 0,
\qquad \sum_j \lambda_j = 1.
\]

Recommended defaults:

- `d_D`: weighted Jaccard or Hamming over named deficit families,
- `d_G`: tree or set distance over goal structures,
- `d_U`: Euclidean or total-variation distance on `[0,1]^3`,
- `d_M`: total-variation on the mode simplex,
- `d_\Gamma`: weighted Hamming or sparse cosine over gate channels,
- `d_\kappa`: total-variation plus scalar budget penalty.

A lawful similarity is any monotone decreasing transform of `d_\Phi`, for example

\[
s_\Phi(x,y)=\exp(-\tau_\Phi d_\Phi(x,y)).
\]

Distance is lawful only if:

1. each subspace and its metric are named,
2. weights are explicit,
3. distance never substitutes for canonical truth,
4. a discrete fallback key exists when geometry is disabled.

---

## 4. What should separate geometrically

Geometry should make the following factors easier to read and reuse:

1. goal identity,
2. uncertainty profile,
3. mode posture,
4. gate posture,
5. in audit geometry only, allocation family,
6. runtime-invariant goal structure.

---

## 5. What remains canonical and non-geometric

The following remain authoritative in their native discrete or structured form:

- `H_t` hard facts,
- `D_t` canonical deficits,
- `B_t` hard verdict,
- `A_t` bounded kernel action,
- `C_t` canonical claims,
- requirements and invariants,
- adapter-preservation semantics.

Geometry may shadow these for evaluation.
It may not replace them.

---

## 6. Metrics

### 6.1 Separability

For factor \(f\), separability is measured by balanced linear decode accuracy on held-out data:

\[
\operatorname{Sep}(f) := \operatorname{BalAcc}(\widehat f(\Phi),f)
\]

using a regularized linear decoder.

### 6.2 Cross-condition generalization performance (CCGP)

For factor \(f\) and nuisance split \(c\),

\[
\operatorname{CCGP}(f;c)
=
\frac{1}{|\mathcal S|}
\sum_{(S_{train},S_{test})\in \mathcal S}
\operatorname{BalAcc}(\widehat f_{train}(\Phi_{S_{train}}),f_{S_{test}}).
\]

Interpretation:
train a decoder on one condition family, test on another.
This is the right measure for whether factorization generalizes rather than merely memorizes.

### 6.3 Parallelism

For binary factor contrasts, let \(v_{ab}\) be the mean contrast vector.
Then

\[
\operatorname{Par}(f)=
\operatorname{mean}_{(ab),(cd)}
\cos(v_{ab},v_{cd}).
\]

High parallelism means the same factor is encoded in a stable direction across nuisance conditions.

### 6.4 Cross-runtime goal robustness (CRGR)

Let \(r\neq r'\) index runtimes in the current closed set.
Define

\[
\operatorname{CRGR}
=
\frac{1}{|R(R-1)|}
\sum_{r\neq r'}
\operatorname{BalAcc}(\widehat g_r(\Phi_r),g_{r'}).
\]

Interpretation:
train a goal decoder on one runtime, test on another.
A high CRGR means the same goal remains readable across honest runtime realization differences.

### 6.5 Uncertainty-robust goal decoding (URGD)

Partition examples into low/high uncertainty bins using `U_t`.
Then

\[
\operatorname{URGD}
=
\frac{1}{2}
\left[
\operatorname{BalAcc}(\widehat g_{\mathrm{low}}(\Phi),g_{\mathrm{high}})
+
\operatorname{BalAcc}(\widehat g_{\mathrm{high}}(\Phi),g_{\mathrm{low}})
\right].
\]

Interpretation:
goals remain decodable even when uncertainty conditions change.

### 6.6 Advisory usefulness

Define

\[
U_{\mathrm{geom}}
=
\Delta_{\mathrm{ctl}}
+
\lambda_{\mathrm{eval}}\Delta_{\mathrm{eval}}
-
\lambda_{\mathrm{cost}}\Delta_{\mathrm{cost}},
\]

where:

- `Δ_ctl` = advisory-control lift from geometry over discrete fallback,
- `Δ_eval` = evaluation lift from geometry,
- `Δ_cost` = runtime or complexity overhead.

Geometry is useful only if \(U_{geom} > 0\) over audited review windows.

---

## 7. Evaluation protocol

The finished packet fixes a minimal evaluation protocol so geometry is not merely rhetorical.

### 7.1 Decoder class
Use a regularized linear decoder by default.

### 7.2 Splits
Use balanced train/test splits over:

- runtime,
- uncertainty condition,
- branch family where applicable.

### 7.3 Variance reporting
Report bootstrap confidence intervals for all primary metrics.

### 7.4 Ablation
For every geometry-enabled evaluation, report the matched discrete fallback baseline.

### 7.5 Review rule
A geometry subspace is retained only if:

- it improves at least one primary metric or advisory-control outcome,
- it does not degrade claim conservativity,
- its computational overhead is justified.

---

## 8. Decorative-geometry detection

Geometry has become decorative rather than useful if any of the following hold over the review window:

1. `Sep` is high but `CCGP` and `CRGR` are poor,
2. advisory outcomes do not improve over the discrete fallback,
3. overhead grows while `U_geom \le 0`,
4. embeddings are retained solely because they look elegant,
5. any path begins to treat geometry as a verdict source.

A decorative subspace must be pruned, not defended aesthetically.

---

## 9. One-sentence summary

**The finished geometry program encodes only a typed auxiliary shadow of canonical state, uses CCGP / parallelism / separability / CRGR / URGD to audit whether that shadow is genuinely useful, and prunes any geometry that does not earn advisory or evaluative lift.**
