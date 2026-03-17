# CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE

Status: active supporting authority for implementation
Date: 2026-03-18
Rule: **no load-bearing implementation seam may land without a correspondence row in this document.**

This artifact recovers v1's math-to-code discipline for the v2 architecture.

Every important v2 law has one named code object, one implementation home, one test surface, and documented forbidden leaks.

---

## 0. Governing principle

v1's strongest organizational property was that every mathematical object had exactly one code surface. That property made the system auditable and made defects (including the boundedness gap) precisely diagnosable.

v1's failure was not the existence of clean math-to-code correspondence. It was that the most carefully embodied math was centered on completion-proof truth instead of bounded task quality.

v2 keeps the correspondence discipline. v2 changes the content: lifecycle-first, executive-first, host-affordance-native, and microkernel-limited.

The rule is:

- every packet-level mathematical object **is** exactly one typed code object
- every typed code object lives in exactly one module
- every correspondence has at least one test surface
- forbidden leaks are explicit

---

## 1. Core substrate correspondence

### 1.1 Lifecycle surface law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `L_r = (E_r, A_r^{ctx}, A_r^{tool}, A_r^{turn}, A_r^{orch}, A_r^{mcp}, R_r)` | `LifecycleSurface` | `cortex/core/lifecycle.py` | `test_core_substrate.py::test_lifecycle_event_and_observation_carriers_construct_cleanly` | landed |
| `R_r` (host effect map) | `LifecycleEffectBinding` (tuple in `LifecycleSurface.effect_map`) | `cortex/core/lifecycle.py` | same test | landed |

Forbidden leaks: no adapter may define its own lifecycle surface type. All host realizations must construct a `LifecycleSurface`.

### 1.2 Event envelope law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `ℓ_t` (lifecycle event) | `LifecycleEventEnvelope` | `cortex/core/envelopes.py` | `test_core_substrate.py::test_lifecycle_event_and_observation_carriers_construct_cleanly` | landed |
| event payload handle | `EventPayloadHandle` | `cortex/core/envelopes.py` | same test | landed |
| extensible metadata | `MetadataField` | `cortex/core/envelopes.py` | same test | landed |

Forbidden leaks: no code surface may bypass `LifecycleEventEnvelope` to pass raw host events into the core dispatch path.

### 1.3 Observation law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `O_{t,r} = Observe_r(ℓ_t, ω_t, L_r)` | `ObservationBundle` | `cortex/core/observation.py` | `test_core_substrate.py::test_lifecycle_event_and_observation_carriers_construct_cleanly` | landed |
| payload view within observation | `PayloadView` | `cortex/core/observation.py` | same test | landed |
| already-produced runtime records | `RuntimeRecord` | `cortex/core/observation.py` | same test | landed |
| already-attached structured observations | `StructuredObservation` | `cortex/core/observation.py` | same test | landed |

Forbidden leaks: `ObservationBundle` must stay lightweight. It must not eagerly gather global state.

### 1.4 Environment split law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `V_{t,r}` (executive environment view) | `ExecutiveEnvironmentView` | `cortex/core/environment.py` | `test_core_substrate.py::test_certification_context_rejects_executive_environment_view` | landed |
| `E_{t,r}` (commitment environment handle) | `CommitmentEnvironmentHandle` | `cortex/core/environment.py` | `test_core_substrate.py::test_certification_context_accepts_commitment_environment_handle` | landed |
| domain-agnostic query kinds | `STATE_SNAPSHOT`, `STATE_DIFF`, `EXECUTION_TRACE`, `RESULT_ARTIFACT`, `CAPABILITY_VIEW`, `EXTERNAL_RECORD` constants + `EnvironmentQuery` | `cortex/core/environment.py` | same tests | landed |

Forbidden leaks: `ExecutiveEnvironmentView` may never be passed where `CommitmentEnvironmentHandle` is required. This is the **event-local certification firewall** and is enforced by `CertificationContext.__post_init__`.

### 1.5 Support state law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `W_t` (mutable support state) | `SupportState` | `cortex/core/support.py` | `test_core_substrate.py::test_support_state_and_snapshot_are_distinct_types` | landed |
| `S_t = Snapshot(O_{t,r}, W_t)` (read-only snapshot) | `SupportSnapshot` | `cortex/core/support.py` | same test | landed |
| trace-level support | `SupportTraceState` | `cortex/core/support.py` | same test | landed |
| session-level support | `SupportSessionState` | `cortex/core/support.py` | same test | landed |
| host-level support | `SupportHostState` | `cortex/core/support.py` | same test | landed |
| published exec memory | `SupportExecMemoryState` | `cortex/core/support.py` | same test | landed |
| wake receipts | `WakeReceipt` | `cortex/core/support.py` | same test | landed |

Forbidden leaks: `SupportState` and `SupportSnapshot` are distinct types — mutable support state must never be confused with read-only snapshots. AUX may augment snapshots; it may not redefine the snapshot constructor.

### 1.6 Commitment status lattice

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `S^{valid} = {CERTIFIED, UNCERTIFIED, BLOCKED}` | `CommitmentStatus` (Enum) | `cortex/core/commitments.py` | `test_core_substrate.py::test_commitment_status_is_the_exact_three_state_lattice` | landed |

Forbidden leaks: no SRE or AUX module may add values to this lattice or redefine what `CERTIFIED`, `UNCERTIFIED`, or `BLOCKED` mean.

### 1.7 Commitment extraction and certification

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `K_t = Extract_{commit}(O_{t,r}, L_r)` (commitment candidate) | `CommitmentCandidate` | `cortex/core/commitments.py` | `test_core_substrate.py::test_commitment_verdict_holds_typed_certification_references` | landed |
| `P_t(c) = Collect_{prov}(...)` (provenance manifest) | `ProvenanceManifest` | `cortex/core/commitments.py` | same test + `test_core_substrate.py::test_provenance_manifest_supports_multiple_domain_agnostic_source_families` | landed |
| provenance evidence references | `ProvenanceEvidenceRef` | `cortex/core/commitments.py` | same tests | landed |
| `H_t(c) = Check_{boundary}(...)` (boundary assessment) | `BoundaryAssessment` | `cortex/core/commitments.py` | `test_core_substrate.py::test_boundary_assessment_keeps_blockedness_separate_from_commitment_status` | landed |
| `S_t^{commit}(c) = Certify_c(...)` (commitment verdict) | `CommitmentVerdict` | `cortex/core/commitments.py` | `test_core_substrate.py::test_commitment_verdict_holds_typed_certification_references` | landed |
| certification context (firewall carrier) | `CertificationContext` | `cortex/core/commitments.py` | `test_core_substrate.py::test_certification_context_rejects_executive_environment_view` and `test_core_substrate.py::test_certification_context_accepts_commitment_environment_handle` | landed |

Forbidden leaks: `CertificationContext` enforces the firewall at construction time. No executive view may reach the certifier.

### 1.8 Degradation and contradiction preservation

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| contradiction records | `ContradictionRecord` | `cortex/core/errors.py` | `test_core_substrate.py::test_degradation_and_error_records_preserve_reason_and_capabilities` | landed |
| degradation records | `DegradationRecord` | `cortex/core/errors.py` | same test | landed |
| core error records | `CoreErrorRecord` | `cortex/core/errors.py` | same test | landed |

Forbidden leaks: contradictions must be preserved, not smoothed. No adapter or AUX module may flatten contradictory host evidence into one unified story.

### 1.9 Dispatch and wake law

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| dispatch lane over `{cheap, candidate-bearing, full-commitment}` | `DispatchLane` (Enum) | `cortex/core/dispatch.py` | `test_dispatch.py::test_cheap_event_stays_cheap_with_no_evidence_burden` + `test_dispatch.py::test_proposal_like_event_becomes_candidate_bearing` + `test_dispatch.py::test_explicit_full_commitment_wake_becomes_full_commitment` | landed |
| event-local routing decision for the current event | `DispatchDecision` | `cortex/core/dispatch.py` | `test_dispatch.py::test_candidate_presence_alone_becomes_candidate_bearing` | landed |
| `Wake_t` (wake decision plus reason set) | `WakeDecision` | `cortex/core/dispatch.py` | `test_dispatch.py::test_boundary_required_marker_forces_full_commitment` + `test_dispatch.py::test_candidate_presence_alone_does_not_overwake_to_full_commitment` | landed |
| minimal evidence requirement object for the dispatched lane | `EvidencePlan` | `cortex/core/dispatch.py` | `test_dispatch.py::test_evidence_plan_matches_the_dispatched_lane` | landed |
| runtime dispatch law over the current event using existing extraction helpers | `classify_dispatch()` | `cortex/core/dispatch.py` | `test_dispatch.py::test_cheap_event_stays_cheap_with_no_evidence_burden` + `test_dispatch.py::test_candidate_presence_alone_becomes_candidate_bearing` + `test_dispatch.py::test_candidate_presence_alone_does_not_overwake_to_full_commitment` | landed |

Forbidden leaks: `classify_dispatch()` consumes `ObservationBundle`, not raw host events. The classifier preserves the no-gauntlet cheap default and may not import executive/SRE same-event policy state as commitment truth. `candidate-present` may justify `candidate-bearing`, but it may not silently upgrade the event to `full-commitment` without a stronger wake marker. No host-driver doctrine, startup doctrine, or adapter loading logic may leak into Core dispatch.

### 1.10 Certification execution and minimal evidence artifacts

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `S_t^{commit}(c) = Certify_c(...)` execution | `certify_commitment()` | `cortex/core/certification.py` | `test_certification_artifacts.py::test_certify_commitment_returns_certified_with_concrete_evidence` + `test_certification_artifacts.py::test_certify_commitment_returns_uncertified_without_concrete_evidence` + `test_certification_artifacts.py::test_certify_commitment_returns_blocked_when_boundary_is_blocked` + `test_certification_artifacts.py::test_certify_commitment_preserves_contradictions_and_degradations` | landed |
| minimal event trace artifact schema | `EventTraceArtifact` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | landed |
| minimal current-pair fragment schema | `CurrentPairFragment` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | landed |
| minimal blocker fragment schema | `BlockerFragment` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_blocker_fragment_preserves_reason_and_contradictions` | landed |

Forbidden leaks: no SRE or AUX same-event policy may enter `certify_commitment()` as certification truth. No host-specific driver doctrine may enter the artifact schemas. Contradictions and degradations must remain explicit. No full proof packet, withheld logic, or audit doctrine may leak into these carriers, and no alternate verdict lattice may be introduced beyond `CERTIFIED`, `UNCERTIFIED`, and `BLOCKED`.

### 1.11 Reference-host observe/bind realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| reference-host lifecycle surface realization | `REFERENCE_HOST_SURFACE` | `cortex/drivers/reference_host.py` | `test_reference_host.py::test_bound_event_carrier_contains_surface_observation_and_normalized_payload` | landed |
| bound reference-host event carrier | `BoundReferenceHostEvent` | `cortex/drivers/reference_host.py` | `test_reference_host.py::test_bound_event_carrier_contains_surface_observation_and_normalized_payload` | landed |
| reference-host envelope binding | `bind_reference_event_envelope()` | `cortex/drivers/reference_host.py` | `test_reference_host.py::test_alias_event_name_binds_to_canonical_core_name_and_preserves_raw_name` | landed |
| `O_{t,reference} = Observe_{reference}(ℓ_t,\omega_t,L_{reference})` realization | `observe_reference_host_event()` | `cortex/drivers/reference_host.py` | `test_reference_host.py::test_proposal_like_raw_host_event_binds_cleanly_and_is_dispatch_ready` + `test_reference_host.py::test_ordinary_context_event_binds_without_commitment_time_work` | landed |

Forbidden leaks: no raw host event or payload dict may bypass `LifecycleEventEnvelope` / `ObservationBundle` through ad hoc core paths. The reference host may not become a truth court for commitments, provenance sufficiency, or blockedness. No startup, retry, or adapter-loading doctrine may leak into this seam. No fake multi-host abstraction, SRE/AUX same-event policy state, or stop-centered prompt doctrine may appear here.

### 1.12 Reference-host commitment-path realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| reference-host commitment-path result carrier | `ReferenceHostCommitmentResult` | `cortex/drivers/reference_host_commitment.py` | `test_reference_host_commitment.py::test_full_commitment_reference_host_event_with_concrete_provenance_yields_certified` + `test_reference_host_commitment.py::test_proposal_like_event_stays_out_of_certification_and_returns_no_verdict` | landed |
| reference-host commitment candidate binding | `bind_reference_host_candidate()` | `cortex/drivers/reference_host_commitment.py` | `test_reference_host_commitment.py::test_candidate_binding_prefers_direct_payload_id_over_extracted_structured_id` + `test_reference_host_commitment.py::test_candidate_binding_falls_back_to_extracted_structured_id` + `test_reference_host_commitment.py::test_candidate_binding_synthesizes_deterministic_local_id_when_none_is_present` | landed |
| reference-host commitment-path execution | `evaluate_reference_host_commitment()` | `cortex/drivers/reference_host_commitment.py` | `test_reference_host_commitment.py::test_full_commitment_reference_host_event_with_concrete_provenance_yields_certified` + `test_reference_host_commitment.py::test_blocked_boundary_yields_blocked_even_when_provenance_exists` + `test_reference_host_commitment.py::test_missing_evidence_yields_uncertified` | landed |

Forbidden leaks: no driver may become a truth court for blockedness, provenance sufficiency, or certification status. Candidate-bearing events may not silently enter certification without a stronger full-commitment wake marker. No SRE/AUX same-event policy state, startup/retry/adapter-loading doctrine, fake multi-host abstraction, stop-centered worldview, proof doctrine, or alternate commitment-status lattice may leak into this slice.

---

## 2. V1 standard-library port correspondence

### 2.1 Commitment payload extraction (v1 `stop_payload.py`)

| V1 origin | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| structured stop-field extraction | `CommitmentPayloadExtraction` + `extract_commitment_payload()` | `cortex/core/commitment_payload.py` | `test_commitment_payload.py::test_native_commitment_carrier_wins_when_present` + `test_commitment_payload.py::test_message_fallback_only_runs_when_allowed_and_normalizes_keys` | landed |

Forbidden leaks: trailer/message-body fallback must remain explicitly weaker than native/payload carriers. The `source` field preserves carrier provenance.

### 2.2 Commitment carrier resolution (v1 narrow `stop_contract.py` slice)

| V1 origin | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| carrier-resolution + source labeling | `CommitmentExtractionResult` + `resolve_commitment_extract()` | `cortex/core/commitment_extract.py` | `test_commitment_extract.py::test_source_labeling_matches_resolution_path` + `test_commitment_extract.py::test_strict_mode_rejects_fallback_only_structured_claims` | landed |
| field reconciliation | `CommitmentFieldResolution` + `reconcile_commitment_field()` | `cortex/core/commitment_extract.py` | `test_commitment_extract.py::test_reconcile_commitment_field_prefers_direct_payload_value` + `test_commitment_extract.py::test_reconcile_commitment_field_falls_back_to_extracted_fields_when_missing` | landed |

Forbidden leaks: `FALLBACK_COMMITMENT_SOURCE` must never be silently promoted to native-equivalent. `structured_payload_violation` preserves strict-mode rejection.

### 2.3 Provenance helpers (v1 `core_helpers.py`)

| V1 origin | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `session_git_snapshot(...)` | `RepositorySnapshot` + `repository_snapshot()` | `cortex/core/provenance.py` | `test_provenance_helpers.py::test_repository_snapshot_reports_unavailable_without_git_marker` | landed |
| `session_changed_files_since_baseline(...)` | `ChangedFilesDelta` + `changed_files_since_baseline()` | `cortex/core/provenance.py` | `test_provenance_helpers.py::test_changed_files_since_baseline_returns_delta_when_snapshots_are_available` + `test_provenance_helpers.py::test_changed_files_since_baseline_returns_reason_when_snapshot_unavailable` | landed |
| requirement-id extraction | `extract_requirement_ids()` | `cortex/core/provenance.py` | `test_provenance_helpers.py::test_requirement_id_extraction_prefers_direct_ids_and_deduplicates` + `test_provenance_helpers.py::test_requirement_id_extraction_falls_back_to_nested_contract_ids` | landed |

### 2.4 Evidence-reference evaluation (v1 `requirements.py` leaf utilities)

| V1 origin | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| evidence-reference checking | `EvidenceReferenceEvaluation` + `evaluate_evidence_reference()` | `cortex/core/provenance.py` | `test_provenance_evidence.py::test_path_reference_verifies_when_file_exists_and_fails_when_missing` + `test_provenance_evidence.py::test_tool_reference_verifies_or_becomes_uncheckable_without_tool_evidence` | landed |
| command-claim normalization | `normalize_command_claim()` + `command_claim_matches()` | `cortex/core/provenance.py` | `test_provenance_evidence.py::test_command_reference_matches_normalized_wrapper_variants` | landed |
| file-claim normalization | `normalize_repo_relative_file_claims()` | `cortex/core/provenance.py` | `test_provenance_evidence.py::test_repo_relative_file_claim_normalization_dedupes_and_strips_suffixes` | landed |

Forbidden leaks: evidence-reference evaluation is domain-general. It must not assume coding-only paths.

### 2.5 Thin event normalization (v1 `adapters.py`)

| V1 origin | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| vendor event normalization | `NormalizedDriverEvent` + `normalize_driver_event()` | `cortex/drivers/common_normalization.py` | `test_common_normalization.py::test_event_name_alias_and_casing_normalization` + `test_common_normalization.py::test_normalized_event_carrier_returns_normalized_name_and_payload_copy` | landed |
| payload normalization | `normalize_driver_payload()` | `cortex/drivers/common_normalization.py` | `test_common_normalization.py::test_payload_normalization_keeps_existing_native_commitment_fields_intact` + `test_common_normalization.py::test_generic_payload_normalization_does_not_impose_host_specific_doctrine` | landed |
| canonical event alias map | `CANONICAL_EVENT_ALIASES` | `cortex/drivers/common_normalization.py` | `test_common_normalization.py::test_event_name_alias_and_casing_normalization` | landed |

Forbidden leaks: drivers normalize; they do not own truth. No driver may become a second truth court or invent hidden semantic owners.

---

## 3. SRE correspondence (not yet landed — reference mapping)

These rows are the target correspondence for the SRE implementation phases. They are not yet code-backed.

| Packet math | Target code object | Target home | Status |
| --- | --- | --- | --- |
| `X_t^{ref} = (x_t^G, x_t^U, x_t^M, x_t^K, x_t^J)` (reference executive state) | `ReferenceExecutiveState` | `cortex/sre/state.py` | not started |
| `A^{ref}` (soft-control family set) | `SoftControlFamily` (Enum or equivalent) | `cortex/sre/families.py` | not started |
| `Q_t^{alloc}(a)` (combined allocation score) | `AllocationScore` or decision table | `cortex/sre/allocation.py` | not started |
| `Δ_t*(a)` and `θ_t^{act}` (neutral-dominance law) | neutral-dominance check function | `cortex/sre/policy.py` | not started |
| `u_t(c)` (classwise uncertainty) | `UncertaintyEstimate` | `cortex/sre/uncertainty.py` | not started |
| `B^{ref} = {quiescent, guarded, latched}` (brake states) | `BrakeState` (Enum) | `cortex/sre/brake.py` | not started |
| goal continuity / pending-goal discipline | `GoalContinuityView` | `cortex/sre/goals.py` | not started |
| branch operations (open/suspend/resume/merge/abandon) | `BranchOperation` | `cortex/sre/branching.py` | not started |

Forbidden leaks: SRE may not certify commitments, redefine blockedness, lower hard boundaries, or fabricate provenance sufficiency.

---

## 4. AUX correspondence (not yet landed — reference mapping)

| Packet math | Target code object | Target home | Status |
| --- | --- | --- | --- |
| `S_t^{aux} = Augment^{aux}(S_t, A_t^{aux})` (snapshot augmentation) | `augment_snapshot()` | `cortex/aux/augmentation.py` | not started |
| `C_t^{aux}` (cost-visible burden) | `AuxBurdenReport` | `cortex/aux/cost.py` | not started |
| `Commit_c(Y_t | A_t^{aux}) = Commit_c(Y_t)` (claim-conservative law) | enforcement test | `tests/integration/test_aux_claim_conservative.py` | not started |

Forbidden leaks: AUX may not certify commitments, lower hard boundaries, become a second truth court, or learn hidden completion heuristics. Every AUX module must be removable without breaking core or SRE.

---

## 5. What this document is not

This document is **not**:

- a replacement constitution or a second packet
- a second implementation master plan
- a theorem stack that code must literally mirror as one monolithic object
- a permission slip to reintroduce v1's stop-centered product architecture
- a place to smuggle SRE or AUX policy into Core

The packet docs still govern architecture. The master plan still governs seam order. This document governs **math-to-code traceability** only.

---

## 6. Correspondence discipline rules

### 6.1 Landing rule

No load-bearing implementation seam may land without adding or updating a row in this document.

### 6.2 One-home rule

Every packet-level mathematical object **is** exactly one typed code object in exactly one module. If a concept needs two modules, the correspondence table must say which module owns truth and which consumes it.

### 6.3 Test rule

Every correspondence row must name at least one test function. If the test does not yet exist, the row must say `not started` and the seam is not considered landed.

### 6.4 Forbidden-leak rule

Every section must document what may not leak across its boundary. Forbidden leaks are as important as the correspondence itself — they are what prevent v2 from drifting into the same failure mode as v1.

### 6.5 Audit rule

This document is an auditable artifact. A packet auditor subagent should be able to verify every row against the actual repo tree.

### 6.6 Minimality rule

Do not let this document become a second theory packet. Keep it implementation-facing, sparse, row-based, and phase-aware. If a row cannot be kept short and concrete, it belongs in the packet docs or tests, not here.

---

## 7. Update law

### 7.1 Architect responsibility

The architect must:

- keep this document consistent with the live repo
- require updates whenever a seam adds or moves a load-bearing implementation home
- refuse to mark a seam fully landed if the seam creates a new load-bearing surface without either updating this document or explicitly justifying why no update is needed

### 7.2 Worker responsibility

A worker may update this document only when:

- the seam actually lands a new implementation home or changes a read/write/verification boundary
- the prompt explicitly authorizes the update

Workers include only the 1–5 correspondence rows in scope for their seam, plus the relevant forbidden leaks. Not the whole document.

### 7.3 Phase-gate use

Before a phase may close, all rows that the phase claims to own must be either `landed` or explicitly `deferred` / `blocked` with reason.

No phase may be declared complete while its key laws remain floating without a code home.

### 7.4 Handoff line

Every seam completion must include: `Correspondence rows touched:` listing the rows added, updated, or confirmed.

---

## 8. V1 comparison

For reference, here is how v2's correspondence recovers v1's math dossier (Section 2) while changing the content:

| V1 math role | V1 embodiment | V2 equivalent math | V2 embodiment |
| --- | --- | --- | --- |
| Evidence `E_t` | `stop_payload.py`, `stop_contract.py`, `invariants.py`, `core.py` | `P_t(c)` provenance manifest + `O_{t,r}` observation | `ProvenanceManifest`, `ObservationBundle`, `EvidenceReferenceEvaluation` |
| Hard gate facts `H_t` | `stop_policy.py`, `stop_runtime.py` | `H_t(c)` boundary assessment | `BoundaryAssessment` |
| Deficit state `D_t` | `stop_signals.py` objective_gap_signature | `u_t(c)` uncertainty classes (SRE-owned) | `UncertaintyEstimate` (not yet landed) |
| Stop signature `S_t` | `stop_signals.py` stop_attempt_signature | `K_t` commitment candidate | `CommitmentCandidate` |
| Memory `M_t` | persisted session metadata | `W_t` support state | `SupportState` |
| Verdict law `B_t` | `StopVerdict` in `stop_policy.py` | `S_t^{commit}` commitment verdict | `CommitmentVerdict` |
| Transition / residue `R_t` | objective_gap_state, loop_detected | `X_t^{ref}` executive state (SRE-owned) | `ReferenceExecutiveState` (not yet landed) |
| Action / control `A_t` | stop_stage, recommend_revert, feedback_mode | `U_t^{sre}` soft-control output | soft-control selection (not yet landed) |
| Outward projection `O_t` | runtime-facing payloads, adapter projections | `Y_{t,r}` realized interaction via `Realize_r()` | host-native realization (not yet landed) |

Key difference: v1 had one stop-centered carrier story. v2 has an ownership-and-correspondence story across Core / SRE / AUX with the same level of rigor applied to a better center.
