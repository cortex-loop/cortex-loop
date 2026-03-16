# EXECUTIVE_INTERFACES

> Historical v1 executive-packet document mirrored from the final 2026-03-15 executive packet source preserved during archive curation.
> Included here as background reference only. Unlike the evidence dossiers in this folder, these executive-packet documents preserve historical v1 constitutional/design material and are not evidence-only authority for v2.


Status: canonical software-interface specification for the finished executive packet  
Date: 2026-03-15  
Scope: exact code-facing contracts that realize the kernel-first executive packet without introducing a second truth layer  
Authority: subordinate to `EXECUTIVE_CONSTITUTION.md`, `BIOLOGY_TO_MATH_TO_CODE.md`, `EXECUTIVE_STATE_SPEC.md`, `GEOMETRY_AND_EVALUATION_SPEC.md`, `OFFLINE_CONSOLIDATION_AND_BMR.md`, `KERNEL_IMPLEMENTATION_DOSSIER.md`, and `ADAPTER_IMPLEMENTATION_DOSSIER.md`  
Non-goal: runtime implementation, host-specific policy invention, or a new semantic ontology

---

## 0. Purpose

This document answers one narrow question:

**Given the kernel law and the executive math, what exact software objects and protocols are allowed to exist, and how do they connect without blurring claim-bearing truth?**

The answer is deliberately conservative:

- the kernel boundary is imported as a read-only snapshot,
- support state is imported as typed read-only snapshots,
- executive state is derived from those snapshots,
- geometry and control allocation are explicit intermediate products,
- adapters realize only abstract soft advice filtered through host affordances and brake state,
- no executive interface may certify completion, mutate canonical claims, or overwrite kernel carriers.

In plain language:

**The interface layer exists to make the mathematics executable, not to create a second brain beside the kernel.**

---

## 1. Interface laws

Let the live stop boundary be

\[
\mathrm{StopPathOutcome}(kernel,witness).
\]

Define the read-only kernel projection

\[
\mathcal K_t^{view} := \operatorname{Proj}_{ker}(\mathrm{StopPathOutcome}(kernel,witness)),
\]

and the read-only support snapshot

\[
\mathcal W_t := \operatorname{Load}_{sup}(W_t^{grave},W_t^{retry},W_t^{execmem},W_t^{host},W_t^{trace}).
\]

The derived executive interfaces then satisfy

\[
\widehat Z_t = \operatorname{Build}_{pre}(\mathcal K_t^{view},\mathcal W_t),
\]
\[
\Phi_t^- = \operatorname{Encode}_{geom}^{pre}(\mathcal K_t^{view}.state.canonical_deficits,\widehat Z_t),
\]
\[
\mathcal A_{t,r}^{pre} = \operatorname{Adm}_r^{pre}(\mathcal W_t.host,\widehat Z_t.gates,\mathcal A^{soft}),
\]
\[
\kappa_t = \operatorname{Alloc}(\mathcal K_t^{view},\mathcal W_t,\widehat Z_t,\Phi_t^-,\mathcal A_{t,r}^{pre}),
\]
\[
J_t^{brake} = \operatorname{Latch}(\mathcal K_t^{view},\mathcal W_t,\widehat Z_t,\kappa_t),
\]
\[
\mathcal A_{t,r}^{post} = \operatorname{Adm}_r^{post}(\mathcal A_{t,r}^{pre},J_t^{brake}),
\]
\[
\Phi_t = \operatorname{Encode}_{geom}^{audit}(\Phi_t^-,\kappa_t),
\]
\[
\mathcal E_t^{adv} = \operatorname{Advise}(\mathcal K_t^{view},\mathcal W_t,\widehat Z_t,\kappa_t,J_t^{brake},\Phi_t,\mathcal A_{t,r}^{post}),
\]
\[
P_{t,r}^{exec} = \operatorname{Realize}_r(\mathcal E_t^{adv},\mathcal W_t.host).
\]

The forbidden arrows are the whole point:

\[
\mathcal K_t^{view} \not\leftarrow \mathcal E_t^{adv},
\qquad
(H_t,D_t,B_t,A_t,C_t) \not\leftarrow \widehat Z_t,\kappa_t,J_t^{brake},\Phi_t,\mathcal E_t^{adv},P_{t,r}^{exec}.
\]

Every interface in this document obeys eight laws.

### 1.1 Kernel-first law
The executive layer may observe the kernel boundary, never own it.

### 1.2 Canonical-source law
Executive builders must read canonical deficits from `KernelStateView.canonical_deficits` only.

### 1.3 Opaque-witness law
Witness payloads do not enter executive state-building or allocation.
Only witness manifest metadata is visible inside the canonical executive interfaces.

### 1.4 Read-only law
All boundary and support imports are immutable snapshots or read-only views.

### 1.5 Acyclic law
`\widehat Z_t` is built before `\Phi_t^-`; `\kappa_t` is built before `J_t^{brake}`; post-admissible actions are built after the brake.

### 1.6 Phase law
Observational, advisory, realized, and offline interfaces are distinct.

### 1.7 Soft-control law
Executive outputs range only over
\[
\mathcal A^{soft}=\{stay\text{-}course,retrieve,reorient,review,defer,branch,escalate,halt\text{-}support\}.
\]

### 1.8 Adapter-preservation law
Adapters may realize soft advice only through runtime affordances and may never add claim-bearing semantics.

---

## 2. Phase gates

### 2.1 Phase O — observational only
Allowed interfaces:
- `KernelBoundaryProjector`
- `SupportStateReader`
- `ExecutiveStateBuilder.build_pre`
- `GeometryEncoder.encode_pre`
- diagnostics computation

Forbidden in Phase O:
- live consumption of advice,
- host realization,
- mutation of support memory.

### 2.2 Phase A — advisory only
Allowed interfaces:
- `ControlAllocator`
- `SoftBrakePolicy`
- `HostAffordanceFilter.pre_admissible_actions`
- `HostAffordanceFilter.post_admissible_actions`
- `ExecutivePolicy.advise`

### 2.3 Phase R — realized advisory control
Allowed interfaces:
- `HostAffordanceFilter.realize`
- `AdapterExecutiveConsumer.consume`

Phase R still remains non-claim-bearing.

### 2.4 Phase L — offline only
Offline consolidation interfaces are specified in `OFFLINE_CONSOLIDATION_AND_BMR.md`.
No live executive interface may mutate executive-memory snapshots.

---

## 3. Read-only kernel boundary interfaces

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping, Protocol, TypeAlias

GapFamily: TypeAlias = str
GoalId: TypeAlias = str
FiniteVec: TypeAlias = tuple[float, ...]
```

### 3.1 Canonical boundary object

```python
@dataclass(frozen=True)
class KernelBoundaryView:
    state: "KernelStateView"
    transition: "KernelTransitionView"
    action: "KernelActionView"
    claims: "KernelClaimsView"
    witness: "WitnessManifestView | None" = None
```

This is the sole executive import point for the stop boundary.

### 3.2 State view

```python
@dataclass(frozen=True)
class KernelStateView:
    hard_facts: "StopPathHardFacts"  # H_t
    canonical_deficits: Mapping[GapFamily, tuple["ObjectiveGapEntry", ...]]  # D_t
    memory: "MemoryState"  # M_t
```

Invariants:
- `canonical_deficits` is the only authoritative deficit source in the executive packet.
- it is immutable and structurally frozen.

### 3.3 Transition / action / claims view

```python
@dataclass(frozen=True)
class KernelTransitionView:
    objective_gap_state: "ObjectiveGapState"  # R_t label / residue owner
    next_memory: "MemoryState"

@dataclass(frozen=True)
class KernelActionView:
    recommend_revert: bool
    stop_stage: str  # A_t

@dataclass(frozen=True)
class KernelClaimsView:
    session_status: str
    contract_gap_kind: str | None
    challenge_ok: bool
    challenge_coverage_missing: tuple[str, ...]
    invariant_ok: bool
    requirements_gate_gap: bool
    requirement_audit_missing: tuple[str, ...]
    stuck_declared: bool
    public_gap_projection: Mapping[GapFamily, tuple["ObjectiveGapEntry", ...]]
```

Invariants:
- `public_gap_projection` is presentation only,
- no executive logic may treat it as a truth source.

### 3.4 Witness manifest view

```python
class WitnessArtifactKind(StrEnum):
    CHALLENGE = "challenge"
    INVARIANT = "invariant"
    REQUIREMENT = "requirement"
    CLAIM = "claim"

@dataclass(frozen=True)
class WitnessArtifactMeta:
    kind: WitnessArtifactKind
    present: bool
    schema_version: str | None = None
    payload_hash: str | None = None
    payload_bytes: int | None = None

@dataclass(frozen=True)
class WitnessManifestView:
    artifacts: tuple[WitnessArtifactMeta, ...]
```

Invariants:
- the executive packet sees witness metadata only;
- no pre-state, allocation, brake, or advice implementation may dereference raw witness payloads.

### 3.5 Projector protocol

```python
class KernelBoundaryProjector(Protocol):
    def project(self, outcome: "StopPathOutcome") -> KernelBoundaryView: ...
```

---

## 4. Support-state interfaces

Support state is the non-claim-bearing input family

\[
W_t=(W_t^{grave},W_t^{retry},W_t^{execmem},W_t^{host},W_t^{trace}).
\]

### 4.1 Support read context

```python
@dataclass(frozen=True)
class SupportReadContext:
    runtime_id: str
    session_key: str | None
    branch_key: str | None
    turn_index: int
```

### 4.2 Snapshots

```python
@dataclass(frozen=True)
class GraveyardMatch:
    key: str
    score: float
    tags: tuple[str, ...] = ()

@dataclass(frozen=True)
class GraveyardSnapshot:
    matches: tuple[GraveyardMatch, ...]
    capped: bool = False

@dataclass(frozen=True)
class RetrySnapshot:
    stagnant_run: int
    retry_budget_remaining: int | None
    last_retry_keys: tuple[str, ...] = ()

class SupportLevel(StrEnum):
    NONE = "none"
    ASSISTED = "assisted"
    NATIVE = "native"

class RuntimeId(StrEnum):
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI_ASSISTED = "openai-assisted"
    OTHER = "other"

@dataclass(frozen=True)
class RuntimeAffordanceState:
    runtime_id: RuntimeId
    theorem_backed: bool
    lifecycle_events: frozenset[str]
    soft_action_support: Mapping["SoftActionKind", SupportLevel]
    branch_cap: int
    retrieval_depth_cap: float
    supports_structured_witness: bool = False

class TaskRegime(StrEnum):
    REFLEX = "reflex"
    LOCALIZED_EDIT = "localized_edit"
    BOUNDED_BUILD = "bounded_build"
    OPEN_ENDED = "open_ended"

class AssuranceClass(StrEnum):
    LIGHT = "light"
    STANDARD = "standard"
    STRICT = "strict"

class ScopeDiagnostic(StrEnum):
    WITHIN_EXPECTED_SCOPE = "within_expected_scope"
    EXPANDED_BUT_ADJACENT = "expanded_but_adjacent"
    OVERBROAD = "overbroad"
    UNASSESSABLE = "unassessable"

@dataclass(frozen=True)
class RoutingProfileSnapshot:
    task_regime: TaskRegime
    assurance_class: AssuranceClass
    scope_diagnostic: ScopeDiagnostic | None = None
    observed_targets: tuple[str, ...] = ()

@dataclass(frozen=True)
class TraceWindow:
    branch_load: int
    recent_soft_actions: tuple["SoftActionKind", ...]
    recent_soft_returns: tuple[float, ...]
    recent_signatures: tuple[str, ...] = ()
    routing_profile: RoutingProfileSnapshot | None = None

@dataclass(frozen=True)
class ExecutiveMemorySnapshot:
    version: str
    repair_priors: Mapping[str, float]
    pattern_priors: Mapping[str, float]
    graveyard_priors: Mapping[str, float]
    branch_priors: Mapping[str, float]
    calibration: Mapping[str, float]
    provenance: tuple[str, ...] = ()

@dataclass(frozen=True)
class SupportState:
    graveyard: GraveyardSnapshot
    retry: RetrySnapshot
    executive_memory: ExecutiveMemorySnapshot
    host: RuntimeAffordanceState
    trace: TraceWindow
```

### 4.3 Support readers

```python
class SupportStateReader(Protocol):
    def read(self, context: SupportReadContext) -> SupportState: ...

class ExecutiveMemoryReader(Protocol):
    def load(self) -> ExecutiveMemorySnapshot: ...
```

Required invariants:
- support snapshots are read-only,
- support snapshots are non-claim-bearing,
- `TraceWindow.routing_profile` is support-only and may never overwrite kernel truth,
- unknown host capability degrades to `SupportLevel.NONE`, never wishful support.

---

## 5. Executive-state interfaces

### 5.1 Pre-control state

```python
@dataclass(frozen=True)
class GoalState:
    active_goal: GoalId
    active: tuple[GoalId, ...]
    pending: tuple[GoalId, ...]
    alternatives: tuple[GoalId, ...]
    order: tuple[tuple[GoalId, GoalId], ...]
    resume_keys: Mapping[GoalId, str]

@dataclass(frozen=True)
class UncertaintyState:
    evidence: float
    environment: float
    capability: float

@dataclass(frozen=True)
class ModeState:
    internal: float
    external: float
    mixed: float

@dataclass(frozen=True)
class GateState:
    write: Mapping[str, float]
    read: Mapping[str, float]
    influence: Mapping[str, float]

@dataclass(frozen=True)
class ExecutivePreState:
    goals: GoalState
    uncertainty: UncertaintyState
    mode: ModeState
    gates: GateState
```

Local invariants:
- goal partitions are disjoint and acyclic,
- all uncertainty and gate values are finite and in `[0,1]`,
- mode weights are finite, nonnegative, and sum to one within tolerance.

### 5.2 Action kinds and brake levels

```python
class SoftActionKind(StrEnum):
    STAY_COURSE = "stay-course"
    RETRIEVE = "retrieve"
    REORIENT = "reorient"
    REVIEW = "review"
    DEFER = "defer"
    BRANCH = "branch"
    ESCALATE = "escalate"
    HALT_SUPPORT = "halt-support"

class BrakeLevel(StrEnum):
    QUIESCENT = "quiescent"
    GUARDED = "guarded"
    LATCHED = "latched"
```

### 5.3 Allocation and brake state

```python
@dataclass(frozen=True)
class ControlAllocationState:
    pre_admissible_actions: frozenset[SoftActionKind]
    budget: float  # beta_t
    action_distribution_pre: Mapping[SoftActionKind, float]  # lambda_t^pre
    vigor: float  # chi_t

@dataclass(frozen=True)
class SoftBrakeState:
    level: BrakeLevel
```

Local invariants:
- `pre_admissible_actions` is explicit and finite,
- `action_distribution_pre` is a simplex over `pre_admissible_actions`,
- no key may represent completion acceptance,
- `SoftBrakeState` is advisory only.

### 5.4 Full executive state

```python
@dataclass(frozen=True)
class ExecutiveState:
    pre: ExecutivePreState
    allocation: ControlAllocationState
    brake: SoftBrakeState
```

### 5.5 Diagnostics are not state

```python
@dataclass(frozen=True)
class ControlDiagnostics:
    q_explicit: Mapping[SoftActionKind, float]
    q_memory: Mapping[SoftActionKind, float]
    q_mixed: Mapping[SoftActionKind, float]
    reliability_explicit: float
    reliability_memory: float
    explicit_weight: float
    expected_control_cost: float
```

Diagnostics rules:
- diagnostics may be logged,
- diagnostics may be audited,
- diagnostics may not be persisted into live executive state,
- diagnostics may re-enter only through offline aggregated calibration summaries.

---

## 6. Geometry interfaces

```python
@dataclass(frozen=True)
class DeficitGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class GoalGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class UncertaintyGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class ModeGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class GateGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class AllocationGeometryPoint:
    values: FiniteVec

@dataclass(frozen=True)
class PreControlGeometry:
    deficits: DeficitGeometryPoint
    goals: GoalGeometryPoint
    uncertainty: UncertaintyGeometryPoint
    mode: ModeGeometryPoint
    gates: GateGeometryPoint

@dataclass(frozen=True)
class AuditGeometry:
    precontrol: PreControlGeometry
    allocation: AllocationGeometryPoint

@dataclass(frozen=True)
class GeometryBundle:
    precontrol: PreControlGeometry
    audit: AuditGeometry | None = None
```

```python
class GeometryEncoder(Protocol):
    def encode_pre(
        self,
        deficits: Mapping[GapFamily, tuple["ObjectiveGapEntry", ...]],
        pre: ExecutivePreState,
    ) -> PreControlGeometry: ...

    def encode_audit(
        self,
        pre_geometry: PreControlGeometry,
        allocation: ControlAllocationState,
    ) -> AuditGeometry: ...
```

Required invariants:
- `encode_pre` consumes authoritative deficits only,
- `encode_pre` does not consume `\kappa_t`,
- `encode_audit` is downstream of `\kappa_t`.

---

## 7. Advice and realization interfaces

### 7.1 Advisory outputs

```python
@dataclass(frozen=True)
class BranchProposal:
    branch_key: str
    parent_goal: GoalId
    priority: float

@dataclass(frozen=True)
class ExecutiveAdvice:
    post_admissible_actions: frozenset[SoftActionKind]
    repair_ranking: tuple[str, ...]
    retrieval_depth: float
    soft_distribution_post: Mapping[SoftActionKind, float]
    preferred_action: SoftActionKind | None
    stay_course_score: float
    branch_proposals: tuple[BranchProposal, ...]
    reorient_score: float
    review_score: float
    defer_score: float
    escalate_score: float
    halt_support_score: float

@dataclass(frozen=True)
class AdvisoryComputation:
    advice: ExecutiveAdvice
    diagnostics: ControlDiagnostics | None = None
```

Required invariants:
- `soft_distribution_post` is a simplex over `post_admissible_actions`,
- `preferred_action` is `None` or the argmax of `soft_distribution_post` up to tie-breaking,
- `branch_proposals` may be nonempty only if `BRANCH` is post-admissible,
- high `stay_course_score` suppresses branch proposals and retrieval-depth inflation by policy,
- high `halt_support_score` suppresses branch proposals and caps retrieval depth by policy,
- `ExecutiveAdvice` contains no verdict, no claims, and no completion fields.

`stay-course` means only:
- no additional executive intervention beyond quiescent monitoring,
- preserve the current kernel trajectory,
- never certify completion,
- never stand in for missing kernel evidence.

`halt-support` means only:
- stop further executive exploration,
- recommend review / escalation / handoff,
- never certify completion,
- never act as a safety halt,
- never replace a kernel verdict,
- remain distinct from `stay-course`.

### 7.2 Realized host plan

```python
class RealizationStatus(StrEnum):
    EXACT = "exact"
    DEGRADED = "degraded"
    BLOCKED = "blocked"

class RealizationReasonCode(StrEnum):
    HOST_UNSUPPORTED = "host-unsupported"
    GATE_SUPPRESSED = "gate-suppressed"
    BRAKE_LATCHED = "brake-latched"
    NO_ADMISSIBLE_ACTION = "no-admissible-action"
    DEPTH_CLIPPED = "depth-clipped"
    BRANCH_CAP_REACHED = "branch-cap-reached"
    PHASE_LOCKED = "phase-locked"
    THEOREM_NOT_BACKED = "theorem-not-backed"

@dataclass(frozen=True)
class ExecutiveRealizationPlan:
    pre_admissible_actions: frozenset[SoftActionKind]
    post_admissible_actions: frozenset[SoftActionKind]
    requested_action: SoftActionKind | None
    realized_action: SoftActionKind | None
    realized_retrieval_depth: float
    realized_branches: tuple[BranchProposal, ...]
    status: RealizationStatus
    degraded_from: SoftActionKind | None = None
    reason_codes: tuple[RealizationReasonCode, ...] = ()
```

Required invariants:
- `status == EXACT` implies `requested_action == realized_action`,
- `status == DEGRADED` implies at least one reason code,
- `status == BLOCKED` implies `realized_action is None`,
- host degradation must be explicit, never silent.

### 7.3 Policy and realization protocols

```python
class HostAffordanceFilter(Protocol):
    def pre_admissible_actions(
        self,
        host: RuntimeAffordanceState,
        gates: GateState,
        actions: frozenset[SoftActionKind],
    ) -> frozenset[SoftActionKind]: ...

    def post_admissible_actions(
        self,
        pre_actions: frozenset[SoftActionKind],
        brake: SoftBrakeState,
    ) -> frozenset[SoftActionKind]: ...

    def realize(
        self,
        host: RuntimeAffordanceState,
        advice: ExecutiveAdvice,
    ) -> ExecutiveRealizationPlan: ...

class ControlAllocator(Protocol):
    def allocate(
        self,
        boundary: KernelBoundaryView,
        support: SupportState,
        pre: ExecutivePreState,
        pre_geometry: PreControlGeometry,
        pre_actions: frozenset[SoftActionKind],
    ) -> tuple[ControlAllocationState, ControlDiagnostics]: ...

class SoftBrakePolicy(Protocol):
    def latch(
        self,
        boundary: KernelBoundaryView,
        support: SupportState,
        pre: ExecutivePreState,
        allocation: ControlAllocationState,
    ) -> SoftBrakeState: ...

class ExecutivePolicy(Protocol):
    def advise(
        self,
        boundary: KernelBoundaryView,
        support: SupportState,
        pre: ExecutivePreState,
        allocation: ControlAllocationState,
        brake: SoftBrakeState,
        geometry: GeometryBundle,
        post_actions: frozenset[SoftActionKind],
        diagnostics: ControlDiagnostics | None = None,
    ) -> AdvisoryComputation: ...

class ExecutiveStateBuilder(Protocol):
    def build_pre(
        self,
        boundary: KernelBoundaryView,
        support: SupportState,
    ) -> ExecutivePreState: ...

    def build_state(
        self,
        pre: ExecutivePreState,
        allocation: ControlAllocationState,
        brake: SoftBrakeState,
    ) -> ExecutiveState: ...
```

---

## 8. Typed conservativity interfaces

These interfaces make the conservativity operators from the constitution inspectable in code.

```python
@dataclass(frozen=True)
class ExecutiveAdjunct:
    advice_manifest: tuple[str, ...]
    realization_manifest: tuple[str, ...]
    geometry_manifest: tuple[str, ...]
    diagnostics_manifest: tuple[str, ...] = ()

@dataclass(frozen=True)
class ExtendedBoundaryView:
    claims: KernelClaimsView
    witness: WitnessManifestView | None
    adjunct: ExecutiveAdjunct | None = None
```

```python
class ExecutiveAdjunctBuilder(Protocol):
    def build(
        self,
        boundary: KernelBoundaryView,
        state: ExecutiveState,
        geometry: GeometryBundle,
        advice: AdvisoryComputation | None,
        realization: ExecutiveRealizationPlan | None,
    ) -> ExecutiveAdjunct: ...

class ExecutiveRenderer(Protocol):
    def render(
        self,
        claims: KernelClaimsView,
        witness: WitnessManifestView | None,
        adjunct: ExecutiveAdjunct | None,
    ) -> ExtendedBoundaryView: ...

class ClaimProjector(Protocol):
    def project(self, extended: ExtendedBoundaryView) -> KernelClaimsView: ...
```

Required invariants:
- `ClaimProjector.project(ExecutiveRenderer.render(claims, witness, adjunct)) == claims`,
- the neutral adjunct leaves claim projection unchanged,
- adjunct data is non-claim-bearing and may be deleted without changing `claims`.

---

## 9. Adapter-facing consequences

Adapters are not allowed to consume the executive packet as if it were a second kernel.
They may consume only the realized soft plan.

The lawful adapter chain is

\[
\mathcal E_t^{adv}
\xrightarrow{\operatorname{Realize}_r}
P_{t,r}^{exec}
\xrightarrow{\text{host bridge}}
\text{runtime-specific soft realization}.
\]

An adapter may:

- clip retrieval depth,
- block unsupported branch operations,
- degrade `branch` to `review` or `escalate` with explicit reason codes,
- carry structured witness support where the host honestly offers it.

An adapter may not:

- reinterpret completion,
- fabricate host support,
- smuggle claims into executive fields.

---

## 10. One-sentence summary

**The finished interface layer is a fully typed, read-only, phase-gated bridge from kernel boundary to soft advisory realization, with explicit pre/post action sets and typed conservativity operators so a weaker implementer cannot accidentally build a second truth layer.**
