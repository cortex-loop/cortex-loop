# CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE

Surface: internal

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

### 1.10 Certification execution, minimal evidence artifacts, eval harness, and packet publication

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `S_t^{commit}(c) = Certify_c(...)` execution | `certify_commitment()` | `cortex/core/certification.py` | `test_certification_artifacts.py::test_certify_commitment_returns_certified_with_concrete_evidence` + `test_certification_artifacts.py::test_certify_commitment_returns_uncertified_without_concrete_evidence` + `test_certification_artifacts.py::test_certify_commitment_returns_blocked_when_boundary_is_blocked` + `test_certification_artifacts.py::test_certify_commitment_preserves_contradictions_and_degradations` | landed |
| minimal event trace artifact schema | `EventTraceArtifact` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | landed |
| minimal current-pair fragment schema | `CurrentPairFragment` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | landed |
| minimal blocker fragment schema | `BlockerFragment` | `cortex/eval/artifacts.py` | `test_certification_artifacts.py::test_blocker_fragment_preserves_reason_and_contradictions` | landed |
| contradiction-preserving eval harness result carrier | `EvaluationHarnessResult` | `cortex/eval/harness.py` | `test_eval_harness.py::test_harness_result_carries_current_pair_without_losing_refs` + `test_eval_harness.py::test_harness_result_carries_blocker_without_smoothing_blocker_truth` | landed |
| eval harness composition entry point | `build_evaluation_harness_result()` | `cortex/eval/harness.py` | `test_eval_harness.py::test_harness_requires_exactly_one_outcome_fragment` + `test_eval_harness.py::test_harness_result_needs_no_publication_packet_surface` | landed |
| truthful-withheld packet carrier | `EvaluationPacket` | `cortex/eval/packets.py` | `test_eval_packets.py::test_packet_built_from_current_pair_preserves_truth_and_withheld_fields` + `test_eval_packets.py::test_packet_built_from_blocker_preserves_truth_and_withheld_fields` | landed |
| packet publication entry point | `build_evaluation_packet()` | `cortex/eval/packets.py` | `test_eval_packets.py::test_packet_build_preserves_contradictions_and_degradations` + `test_eval_packets.py::test_packet_build_requires_no_measured_example_or_runtime_wiring` | landed |

Forbidden leaks: no SRE or AUX same-event policy may enter `certify_commitment()` as certification truth. No host-specific driver doctrine may enter the artifact schemas, eval harness, or packet publication surface. Contradictions and degradations must remain explicit. No report formatting layer, measured publication example, or audit doctrine may leak into these carriers, and no alternate verdict lattice may be introduced beyond `CERTIFIED`, `UNCERTIFIED`, and `BLOCKED`. Eval may not become a second truth court.

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

### 1.13 Reference-host neutral-only realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| reference-host neutral-path result carrier | `ReferenceHostNeutralResult` | `cortex/drivers/reference_host_neutral.py` | `test_reference_host_neutral.py::test_ordinary_context_event_yields_explicit_neutral_continuation_result` + `test_reference_host_neutral.py::test_vertical_slice_stays_observe_bind_driven_and_preserves_raw_host_metadata` | landed |
| neutral-only continuation decision/result | `NeutralContinuationDecision` + `NeutralContinuationCode` | `cortex/drivers/reference_host_neutral.py` | `test_reference_host_neutral.py::test_ordinary_context_event_yields_explicit_neutral_continuation_result` + `test_reference_host_neutral.py::test_proposal_like_event_is_rejected_from_neutral_only_path` + `test_reference_host_neutral.py::test_full_commitment_event_is_rejected_from_neutral_only_path` | landed |
| reference-host neutral-path execution | `evaluate_reference_host_neutral()` | `cortex/drivers/reference_host_neutral.py` | `test_reference_host_neutral.py::test_ordinary_context_event_yields_explicit_neutral_continuation_result` + `test_reference_host_neutral.py::test_proposal_like_event_is_rejected_from_neutral_only_path` + `test_reference_host_neutral.py::test_full_commitment_event_is_rejected_from_neutral_only_path` | landed |

Forbidden leaks: no SRE neutral-dominance scoring or soft-control family logic may appear in this seam. No cheap-path event may be silently escalated into certification. No driver may become a truth court for commitments, provenance, or blockedness. No startup, retry, or adapter-loading doctrine, fake multi-host abstraction, or stop-centered worldview may leak into this slice.

### 1.14 Gemini host observe/bind realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini lifecycle surface realization | `GEMINI_HOST_SURFACE` | `cortex/drivers/gemini_host.py` | `test_gemini_host.py::test_bound_gemini_event_contains_surface_observation_and_remains_dispatch_cheap` | landed |
| bound Gemini event carrier | `BoundGeminiHostEvent` | `cortex/drivers/gemini_host.py` | `test_gemini_host.py::test_bound_gemini_event_contains_surface_observation_and_remains_dispatch_cheap` | landed |
| Gemini envelope binding | `bind_gemini_event_envelope()` | `cortex/drivers/gemini_host.py` | `test_gemini_host.py::test_documented_gemini_event_binds_to_canonical_core_name_and_preserves_raw_name` | landed |
| `O_{t,gemini} = Observe_{gemini}(ℓ_t,\omega_t,L_{gemini})` realization | `observe_gemini_host_event()` | `cortex/drivers/gemini_host.py` | `test_gemini_host.py::test_documented_gemini_event_binds_to_canonical_core_name_and_preserves_raw_name` + `test_gemini_host.py::test_normalized_gemini_payload_preserves_stable_generic_fields_when_present` + `test_gemini_host.py::test_bound_gemini_event_contains_surface_observation_and_remains_dispatch_cheap` + `test_gemini_host.py::test_gemini_surface_gap_emits_explicit_warning_instead_of_fabricated_parity` | landed |

Forbidden leaks: no fake parity with reference-host semantics may be introduced where Gemini differs. No hidden Gemini doctrine may leak into common modules unless the behavior is truly generic. No raw Gemini payload or event may bypass `LifecycleEventEnvelope` / `ObservationBundle`. The Gemini driver may not become a truth court for commitments, provenance sufficiency, or blockedness. Cheap Gemini callback events may not regress into heavy-path handling without actual commitment markers. No runtime or channel realization logic may appear in this seam.

### 1.15 Gemini host commitment-path realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini commitment-path result carrier | `GeminiHostCommitmentResult` | `cortex/drivers/gemini_host_commitment.py` | `test_gemini_host_commitment.py::test_full_commitment_gemini_event_with_concrete_provenance_yields_certified` + `test_gemini_host_commitment.py::test_candidate_bearing_gemini_event_stays_out_of_certification_and_returns_no_verdict` | landed |
| Gemini commitment candidate binding | `bind_gemini_host_candidate()` | `cortex/drivers/gemini_host_commitment.py` | `test_gemini_host_commitment.py::test_candidate_binding_prefers_direct_payload_id_then_extracted_then_synthesized` | landed |
| Gemini commitment-path execution | `evaluate_gemini_host_commitment()` | `cortex/drivers/gemini_host_commitment.py` | `test_gemini_host_commitment.py::test_full_commitment_gemini_event_with_concrete_provenance_yields_certified` + `test_gemini_host_commitment.py::test_blocked_boundary_yields_blocked_even_when_provenance_exists` + `test_gemini_host_commitment.py::test_missing_evidence_yields_uncertified` + `test_gemini_host_commitment.py::test_candidate_bearing_gemini_event_stays_out_of_certification_and_returns_no_verdict` | landed |

Forbidden leaks: no driver may become a truth court for blockedness, provenance sufficiency, or certification status. Candidate-bearing Gemini events may not silently enter certification without a stronger full-commitment wake marker. No invented Gemini lifecycle parity or undocumented host markers may leak into this slice. No runtime, startup, retry doctrine, actual Gemini API execution, fake multi-host abstraction, or alternate commitment-status lattice may appear here.

### 1.16 Gemini host neutral-only realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini neutral-path result carrier | `GeminiHostNeutralResult` | `cortex/drivers/gemini_host_neutral.py` | `test_gemini_host_neutral.py::test_ordinary_gemini_streaming_event_yields_explicit_neutral_continuation_result` + `test_gemini_host_neutral.py::test_slice_stays_observe_bind_driven_and_preserves_raw_gemini_metadata_and_warnings` | landed |
| Gemini neutral-only continuation decision/result | `GeminiNeutralContinuationDecision` + `GeminiNeutralContinuationCode` | `cortex/drivers/gemini_host_neutral.py` | `test_gemini_host_neutral.py::test_ordinary_gemini_streaming_event_yields_explicit_neutral_continuation_result` + `test_gemini_host_neutral.py::test_candidate_bearing_gemini_event_is_rejected_from_neutral_only_path` + `test_gemini_host_neutral.py::test_full_commitment_gemini_event_is_rejected_from_neutral_only_path` | landed |
| Gemini neutral-path execution | `evaluate_gemini_host_neutral()` | `cortex/drivers/gemini_host_neutral.py` | `test_gemini_host_neutral.py::test_ordinary_gemini_streaming_event_yields_explicit_neutral_continuation_result` + `test_gemini_host_neutral.py::test_candidate_bearing_gemini_event_is_rejected_from_neutral_only_path` + `test_gemini_host_neutral.py::test_full_commitment_gemini_event_is_rejected_from_neutral_only_path` + `test_gemini_host_neutral.py::test_slice_stays_observe_bind_driven_and_preserves_raw_gemini_metadata_and_warnings` | landed |

Forbidden leaks: no SRE neutral-dominance scoring or soft-control family logic may appear in this seam. No cheap Gemini event may be silently escalated into certification. No driver may become a truth court for commitments, provenance, or blockedness. No invented Gemini lifecycle parity or undocumented wake markers may appear here. No startup, retry, runtime, API doctrine, or fake multi-host abstraction may leak into this slice.

### 1.17 OpenAI Responses host observe/bind realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI Responses lifecycle surface realization | `OPENAI_HOST_SURFACE` | `cortex/drivers/openai_host.py` | `test_openai_host.py::test_bound_openai_event_contains_surface_observation_and_remains_dispatch_cheap` | landed |
| bound OpenAI Responses event carrier | `BoundOpenAIHostEvent` | `cortex/drivers/openai_host.py` | `test_openai_host.py::test_bound_openai_event_contains_surface_observation_and_remains_dispatch_cheap` | landed |
| OpenAI Responses envelope binding | `bind_openai_event_envelope()` | `cortex/drivers/openai_host.py` | `test_openai_host.py::test_documented_openai_event_binds_to_canonical_core_name_and_preserves_raw_name` | landed |
| `O_{t,openai} = Observe_{openai}(ℓ_t,\omega_t,L_{openai})` realization over the documented OpenAI Responses streaming surface | `observe_openai_host_event()` | `cortex/drivers/openai_host.py` | `test_openai_host.py::test_documented_openai_event_binds_to_canonical_core_name_and_preserves_raw_name` + `test_openai_host.py::test_normalized_openai_payload_preserves_stable_generic_fields_when_present` + `test_openai_host.py::test_bound_openai_event_contains_surface_observation_and_remains_dispatch_cheap` + `test_openai_host.py::test_openai_surface_gap_emits_explicit_warning_instead_of_fabricated_parity` | landed |

Forbidden leaks: no fake parity with Gemini or reference-host semantics may be introduced where OpenAI differs. No hidden OpenAI doctrine may leak into common modules unless the behavior is truly generic. No raw OpenAI payload or event may bypass `LifecycleEventEnvelope` / `ObservationBundle`. The OpenAI driver may not become a truth court for commitments, provenance sufficiency, or blockedness. Cheap OpenAI Responses streaming events may not regress into heavy-path handling without actual commitment markers. No runtime or channel realization logic may appear in this seam.

### 1.18 OpenAI Responses commitment-path realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI commitment-path result carrier | `OpenAIHostCommitmentResult` | `cortex/drivers/openai_host_commitment.py` | `test_openai_host_commitment.py::test_full_commitment_openai_event_with_concrete_provenance_yields_certified` + `test_openai_host_commitment.py::test_candidate_bearing_openai_event_stays_out_of_certification_and_returns_no_verdict` | landed |
| OpenAI commitment candidate binding | `bind_openai_host_candidate()` | `cortex/drivers/openai_host_commitment.py` | `test_openai_host_commitment.py::test_candidate_binding_prefers_direct_payload_id_then_extracted_then_synthesized` | landed |
| OpenAI commitment-path execution | `evaluate_openai_host_commitment()` | `cortex/drivers/openai_host_commitment.py` | `test_openai_host_commitment.py::test_full_commitment_openai_event_with_concrete_provenance_yields_certified` + `test_openai_host_commitment.py::test_blocked_boundary_yields_blocked_even_when_provenance_exists` + `test_openai_host_commitment.py::test_missing_evidence_yields_uncertified` + `test_openai_host_commitment.py::test_candidate_bearing_openai_event_stays_out_of_certification_and_returns_no_verdict` | landed |

Forbidden leaks: no driver may become a truth court for blockedness, provenance sufficiency, or certification status. Candidate-bearing OpenAI events may not silently enter certification without a stronger full-commitment wake marker. No invented OpenAI lifecycle parity or undocumented host markers may leak into this slice. No runtime, startup, retry doctrine, actual OpenAI API execution, fake multi-host abstraction, or alternate commitment-status lattice may appear here.

### 1.19 OpenAI Responses neutral-only realization

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI neutral-path result carrier | `OpenAIHostNeutralResult` | `cortex/drivers/openai_host_neutral.py` | `test_openai_host_neutral.py::test_ordinary_openai_streaming_event_yields_explicit_neutral_continuation_result` + `test_openai_host_neutral.py::test_slice_stays_observe_bind_driven_and_preserves_raw_openai_metadata_and_warnings` | landed |
| OpenAI neutral-only continuation decision/result | `OpenAINeutralContinuationDecision` + `OpenAINeutralContinuationCode` | `cortex/drivers/openai_host_neutral.py` | `test_openai_host_neutral.py::test_ordinary_openai_streaming_event_yields_explicit_neutral_continuation_result` + `test_openai_host_neutral.py::test_candidate_bearing_openai_event_is_rejected_from_neutral_only_path` + `test_openai_host_neutral.py::test_full_commitment_openai_event_is_rejected_from_neutral_only_path` | landed |
| OpenAI neutral-path execution | `evaluate_openai_host_neutral()` | `cortex/drivers/openai_host_neutral.py` | `test_openai_host_neutral.py::test_ordinary_openai_streaming_event_yields_explicit_neutral_continuation_result` + `test_openai_host_neutral.py::test_candidate_bearing_openai_event_is_rejected_from_neutral_only_path` + `test_openai_host_neutral.py::test_full_commitment_openai_event_is_rejected_from_neutral_only_path` + `test_openai_host_neutral.py::test_slice_stays_observe_bind_driven_and_preserves_raw_openai_metadata_and_warnings` | landed |

Forbidden leaks: no SRE neutral-dominance scoring or soft-control family logic may appear in this seam. No cheap OpenAI event may be silently escalated into certification. No driver may become a truth court for commitments, provenance, or blockedness. No invented OpenAI lifecycle parity or undocumented wake markers may appear here. No startup, retry, runtime, API doctrine, or fake multi-host abstraction may leak into this slice.

---

### 1.20 Reference runtime shell composition

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| first bounded last-step realized shell outcome carrier with optional evidence-move and continuity-improvement truth | `ReferenceRealizationFeedback` | `cortex/sre/feedback.py` | `test_reference_realization_feedback.py::test_reference_realization_feedback_preserves_last_step_shell_outcome` + `test_reference_realization_feedback.py::test_reference_realization_feedback_rejects_noncanonical_commitment_kind` | landed |
| first bounded reference short-window realized-outcome carrier | `ReferenceRealizationFeedbackWindow` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_reference_realization_feedback_window_starts_empty` + `test_reference_feedback_window.py::test_reference_realization_feedback_window_keeps_only_three_most_recent_entries` + `test_reference_feedback_window.py::test_reference_runtime_session_normalizes_window_only_feedback_into_last_step_mirror` | landed |
| reference-host live runtime session carrier with active-track continuity state, last-step feedback persistence, bounded feedback-window persistence, and lawful one-sided normalization/rejection when last-step mirror and bounded window disagree | `ReferenceRuntimeSession` | `cortex/hosts/reference/runtime.py` | `test_reference_runtime_step.py::test_reference_runtime_session_tracks_minimum_live_state` + `test_reference_feedback_window.py::test_reference_runtime_session_normalizes_last_only_feedback_into_window` + `test_reference_feedback_window.py::test_reference_runtime_session_normalizes_window_only_feedback_into_last_step_mirror` + `test_reference_feedback_window.py::test_reference_runtime_session_rejects_mismatched_last_feedback_and_window_newest_entry` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_normalizes_last_only_prior_session_and_preserves_feedback_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session` | landed |
| reference-host runtime step result carrier with selected-family truth, realized-family truth, prior-window feedback summary, replay-driven allocation diagnostics truth, and explicit evidence/continuity realization feedback | `ReferenceRuntimeStepResult` | `cortex/hosts/reference/runtime.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates` + `test_reference_runtime_step.py::test_reference_runtime_step_replay_publication_can_lift_check_allocation_without_changing_commitment_truth` | landed |
| first bounded runtime control-ledger carrier with nested executive allocation diagnostics | `ReferenceControlLedger` | `cortex/hosts/reference/runtime.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_admissible_families_by_soft_control_enum` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag` + `test_reference_runtime_step.py::test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_guarded_feedback_pressure_to_check_when_evidence_dominates` | landed |
| reference-host runtime step composition over observe/bind, dispatch, commitment carriers, landed executive builder/scorer surfaces, first one-process continuity law, explicit malformed-open rejection, explicit session-mismatch warning, last-step realization-feedback persistence, bounded feedback-window persistence, prior-window feedback summary projection, family-sensitive thresholding, minimum-burden guarded/latched enforcement, optional explicit AUX replay ingress, unaugmented executive-state observation law, and explicit replay-only `memory_priors` derivation | `run_reference_runtime_step()` | `cortex/hosts/reference/runtime.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_keeps_candidate_bearing_event_candidate_only` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_replay_publication_can_lift_check_allocation_without_changing_commitment_truth` + `test_reference_runtime_step.py::test_reference_runtime_step_uses_unaugmented_snapshot_for_executive_state_and_augmented_snapshot_only_for_memory_priors` + `test_reference_runtime_step.py::test_reference_runtime_step_without_offline_publication_makes_no_aux_calls_and_keeps_memory_priors_absent` + `test_reference_runtime_step.py::test_reference_runtime_step_rejects_malformed_open_without_mutating_existing_anchor` + `test_reference_runtime_step.py::test_reference_runtime_step_rejects_mismatched_session_id_without_reassigning_shell` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_normalizes_last_only_prior_session_and_preserves_feedback_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_prior_enforcement_override_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_does_not_raise_feedback_pressure_after_clean_success` + `test_reference_runtime_step.py::test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_repeated_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_admissible_families_by_soft_control_enum` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag` + `test_reference_runtime_step.py::test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_neutral_without_evidence_or_environment` + `test_reference_runtime_step.py::test_reference_runtime_step_allows_latched_seek_context_when_native_host_capability_relief_is_directly_justified` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_guarded_feedback_pressure_to_check_when_evidence_dominates` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_rejects_illegal_continuity_transitions_without_mutating_session_truth` | landed |
| `Y_{t,reference}` runtime output projection with top-level control ledger, prior-window feedback summary, and nested executive allocation diagnostics | `build_reference_cli_record()` | `cortex/runtime/reference_cli.py` | `test_reference_runtime_cli.py::test_reference_runtime_cli_reads_event_file_and_emits_one_record_per_event` + `test_reference_runtime_cli.py::test_reference_runtime_cli_reads_stdin_and_preserves_locked_output_contract` + `test_reference_runtime_cli.py::test_reference_runtime_cli_in_process_surfaces_selected_vs_realized_divergence` + `test_reference_runtime_cli.py::test_reference_runtime_cli_emits_feedback_window_summary_for_real_session_mismatch_sequences` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session` | landed |

Forbidden leaks: the runtime shell may compose existing reference-host, core, and SRE carriers, but it may not expand Core, introduce multi-host abstraction, invent a second continuity model outside the landed branch/goal carriers, or launder provisional neutral selection into a computed executive loop. Cheap-path default must remain intact, commitment result kinds may only surface from the existing certification lattice, illegal continuity transitions may not silently mutate session truth, malformed `open` may not erase suspended anchors, and a non-empty runtime `session_id` may not be silently reassigned once the one-process shell is established. The first bounded realization-feedback carrier may persist only the immediately previous realized shell outcome; it may not become learned reward history, hidden branch state, or a second continuity court. The first bounded short-window carrier may persist only the three most recent runtime-realized outcomes in oldest-to-newest order; it may not widen into aggregate reward history, hidden executive state, or a second continuity court. The live runtime session carrier may normalize lawful one-sided last-step/window state so prior-pressure truth is preserved, but it may not silently tolerate divergent two-sided state or drop a persisted last-step outcome before the builder consumes it. The first control ledger may serialize only actual runtime truth: event class, admissible families, selected family, realized family, dominant uncertainty sources, brake state, budget band, and primary reason. It may not invent hidden reasoning, policy justifications, or synthetic confidence. The first prior-window summary may reflect only the already-persisted influencing window; it may not report post-step feedback as if it influenced the current event. Latched-brake enforcement may change runtime realization, but it may not move policy ownership into Core, suppress lawful commitment truth, or erase the distinction between selected family and realized family. The first outward projection may serialize landed runtime truth for local CLI use, including a compact executive-state summary, top-level control ledger, one-process continuity state, and a bounded prior-window summary, but it may not invent continuity, commit kinds, or runtime-on executive state that the step kernel did not actually produce. When a full-commitment event carries lawful certification evidence yet the surrounding continuity transition is rejected or latched enforcement overrides runtime realization, the shell must preserve both truths explicitly rather than smoothing either away.

---

### 1.21 Reference runtime persisted continuation

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| bounded cross-process persisted continuation carrier split into exact `continuity_truth` and bounded `control_residue` | `ReferenceRuntimeSessionArtifact` | `cortex/runtime/reference_session_io.py` | `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_roundtrips_empty_session` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_roundtrips_populated_continuity_truth` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_roundtrips_bounded_residue_without_full_histories` | landed |
| runtime session -> persisted artifact build boundary | `build_reference_runtime_session_artifact()` | `cortex/runtime/reference_session_io.py` | `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_roundtrips_bounded_residue_without_full_histories` | landed |
| persisted artifact -> runtime session parse boundary | `parse_reference_runtime_session_artifact()` | `cortex/runtime/reference_session_io.py` | `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_rejects_wrong_kind_and_version` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_rejects_unknown_keys_everywhere` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_rejects_invalid_enums` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_rejects_mismatched_last_feedback_and_window` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_one_sided_last_feedback_normalizes_through_session_constructor` + `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_one_sided_window_only_normalizes_through_session_constructor` | landed |
| explicit persisted artifact file read boundary for the local CLI shell | `read_reference_runtime_session_artifact()` | `cortex/runtime/reference_session_io.py` | `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_read_write_roundtrip_uses_json_file` + `test_reference_runtime_cli.py::test_reference_runtime_cli_bad_load_artifact_exits_non_zero_and_emits_no_stdout` + `test_reference_runtime_cli.py::test_reference_runtime_cli_zero_event_load_save_roundtrip_works` | landed |
| explicit persisted artifact file write boundary for the local CLI shell | `write_reference_runtime_session_artifact()` | `cortex/runtime/reference_session_io.py` | `test_reference_runtime_session_io.py::test_reference_runtime_session_artifact_read_write_roundtrip_uses_json_file` + `test_reference_runtime_cli.py::test_reference_runtime_cli_save_session_does_not_change_jsonl_output` + `test_reference_runtime_cli.py::test_reference_runtime_cli_same_path_load_and_save_replaces_artifact` + `test_reference_runtime_cli.py::test_reference_runtime_cli_save_failure_emits_no_stdout` + `test_reference_runtime_cli.py::test_reference_runtime_cli_zero_event_load_save_roundtrip_works` | landed |

Forbidden leaks: persisted continuation remains runtime-owned. It may not become a generic store doctrine, a host-neutral persistence framework, or a second truth court. `continuity_truth` is the only persisted restart state required to resume lawfully; `control_residue` is bounded advisory residue only. Full shell-long `budget_history` and `brake_history` may remain public one-process diagnostics, but they may not be persisted as cross-process continuation truth. CLI save/load control must remain explicit flags rather than synthetic lifecycle events. Save/load failure may not emit partial JSONL output or partial artifacts. The loader must reconstruct through `ReferenceRuntimeSession(...)` so existing lawful one-sided last/window normalization remains the only normalization path.

---

### 1.22 OpenAI documented host-event runtime shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI host-runtime compact product-journal carrier over documented raw host events plus accepted `C1` continuation law | `OpenAIRuntimeSession` | `cortex/runtime/openai.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_roundtrips_compact_product_journal` + `test_openai_runtime_continuity.py::test_openai_runtime_split_session_is_o1_equivalent_to_uninterrupted_run` | landed |
| OpenAI explicit product-decision carrier over the accepted OpenAI-only decision table (`OpenAIControlLedger` alias over `OpenAIProductDecision`) | `OpenAIControlLedger` | `cortex/runtime/openai.py` | `test_openai_runtime_step.py::test_openai_runtime_step_uses_compact_decision_table_without_reference_soft_control` + `test_openai_service.py::test_openai_service_health_and_documented_event_flow` | landed |
| OpenAI host-runtime step result carrier over dispatch decision, explicit product decision, warnings, and compact journal truth | `OpenAIRuntimeStepResult` | `cortex/runtime/openai.py` | `test_openai_runtime_cli.py::test_openai_runtime_cli_reads_documented_raw_events_and_preserves_host_name` | landed |
| OpenAI host-runtime step composition over landed OpenAI observe/bind, commitment-path helpers, compact journal continuity, and one explicit OpenAI-only decision table | `run_openai_runtime_step()` | `cortex/runtime/openai.py` | `test_openai_runtime_step.py::test_openai_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing` + `test_openai_runtime_step.py::test_openai_runtime_step_uses_compact_decision_table_without_reference_soft_control` + `test_openai_runtime_step.py::test_openai_runtime_step_preserves_session_mismatch_as_stop_without_reassigning_session` + `test_openai_runtime_cli.py::test_openai_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_openai_runtime_cli.py::test_openai_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` + `test_openai_runtime_continuity.py::test_openai_runtime_host_warning_and_certified_commitment_can_coexist_across_restart` | landed |
| OpenAI bounded persisted product-journal carrier with exact top-level `journal` truth only | `OpenAIRuntimeSessionArtifact` | `cortex/runtime/openai_session_io.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_roundtrips_compact_product_journal` | landed |
| OpenAI runtime session -> persisted compact product journal build boundary | `build_openai_runtime_session_artifact()` | `cortex/runtime/openai_session_io.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_roundtrips_compact_product_journal` | landed |
| OpenAI persisted compact product journal -> runtime session parse boundary with explicit legacy rejection | `parse_openai_runtime_session_artifact()` | `cortex/runtime/openai_session_io.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_rejects_legacy_shape_unknown_keys_and_invalid_fields` | landed |
| OpenAI persisted artifact file read boundary for the local CLI shell | `read_openai_runtime_session_artifact()` | `cortex/runtime/openai_session_io.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_same_path_overwrite_safety` | landed |
| OpenAI persisted artifact file write boundary for the local CLI shell | `write_openai_runtime_session_artifact()` | `cortex/runtime/openai_session_io.py` | `test_openai_runtime_session_io.py::test_openai_runtime_session_artifact_same_path_overwrite_safety` + `test_openai_runtime_cli.py::test_openai_runtime_cli_explicit_load_save_works` + `test_openai_runtime_cli.py::test_openai_runtime_cli_load_save_failure_emits_no_stdout` | landed |
| OpenAI developer-facing runtime output projection with preserved raw host event name and exact compact `decision + journal` ordering | `build_openai_cli_record()` | `cortex/runtime/openai_cli.py` | `test_openai_runtime_cli.py::test_openai_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_openai_runtime_cli.py::test_openai_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` + `test_openai_host_control_service.py::test_openai_host_control_action_endpoint_returns_ordered_o1_records_and_mutates_session` | landed |

Forbidden leaks: `O1` remains host-specific on purpose. It may not introduce a fake host-neutral runtime layer, generic store doctrine, live network/service doctrine, or outbound OpenAI host action realization. Raw OpenAI host event names must remain visible in the outward projection and undocumented host events must remain explicit conservative warnings rather than fabricated parity. OpenAI persisted continuation is now the exact compact `openai_product_journal` only; `continuity_truth`, `control_residue`, `budget_history`, `brake_history`, selection math, and allocation diagnostics may not reappear as cross-process continuation truth on the accepted product path.

---

### 1.23 OpenAI raw-transcript ingress shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI raw host-transcript ingress carrier over transcript `type` plus payload remainder | `OpenAIHostEventEnvelope` | `cortex/runtime/openai_ingress.py` | `test_openai_ingress.py::test_documented_raw_openai_event_parses_cleanly` + `test_openai_ingress.py::test_undocumented_raw_response_event_still_parses_cleanly` | landed |
| raw transcript -> ingress carrier parse boundary | `parse_openai_host_event_envelope()` | `cortex/runtime/openai_ingress.py` | `test_openai_ingress.py::test_canonical_cortex_event_name_is_rejected` + `test_openai_ingress.py::test_dev_shell_wrapper_shape_is_rejected` + `test_openai_ingress.py::test_missing_type_and_non_object_record_are_rejected` | landed |
| OpenAI raw-transcript ingress CLI over accepted `O1` runtime shell | `main()` | `cortex/runtime/openai_ingress_cli.py` | `test_openai_ingress_cli.py::test_openai_ingress_cli_reads_documented_raw_transcript_fixture` + `test_openai_ingress_cli.py::test_openai_ingress_cli_rejects_canonical_event_names_and_wrapper_shape` + `test_openai_ingress_cli.py::test_openai_ingress_cli_undocumented_raw_host_event_still_warns_conservatively` | landed |

Forbidden leaks: `O2` owns transcript-shape parsing only. It may not mutate `O1` into the only OpenAI shell, may not accept the dev-shell wrapper shape as lawful ingress, may not accept mixed wrapper/transcript records as lawful ingress, and may not fabricate host parity by silently normalizing canonical Cortex event names back into raw OpenAI host traffic. `openai_ingress_cli.py` may consume accepted `run_openai_runtime_step()` and the accepted `O1` session artifact, but it may not become a new runtime owner or a generic ingress abstraction.

---

### 1.24 OpenAI loopback service shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| OpenAI loopback service state carrier over exactly one active compact runtime session per process | `OpenAIServiceState` | `cortex/runtime/openai_service.py` | `test_openai_service.py::test_openai_service_state_constructs_cleanly` | landed |
| loopback service request dispatch over accepted `O2` transcript parsing and accepted compact `O1` runtime/session law | `handle_openai_service_request()` | `cortex/runtime/openai_service.py` | `test_openai_service.py::test_openai_service_invalid_import_becomes_400_error_payload` + `test_openai_service.py::test_openai_service_unknown_path_and_wrong_method_return_json_errors` + `test_openai_service.py::test_openai_service_health_and_documented_event_flow` | landed |
| OpenAI loopback service compact product-journal export boundary | `export_openai_service_session()` | `cortex/runtime/openai_service.py` | `test_openai_service.py::test_openai_service_import_export_preserves_exact_artifact_shape` + `test_openai_service.py::test_openai_service_session_export_import_and_startup_load_roundtrip` | landed |
| OpenAI loopback service compact product-journal import boundary | `import_openai_service_session()` | `cortex/runtime/openai_service.py` | `test_openai_service.py::test_openai_service_import_export_preserves_exact_artifact_shape` + `test_openai_service.py::test_openai_service_invalid_import_becomes_400_error_payload` + `test_openai_service.py::test_openai_service_session_export_import_and_startup_load_roundtrip` | landed |
| OpenAI loopback service shell entrypoint over the compact `decision + journal` product projection | `main()` | `cortex/runtime/openai_service.py` | `test_openai_service.py::test_openai_service_health_and_documented_event_flow` + `test_openai_service.py::test_openai_service_undocumented_raw_event_warns_without_fabricating_parity` + `test_openai_service_continuity.py::test_openai_service_event_sequence_is_o3_equivalent_to_o2_ingress_shell` | landed |

Forbidden leaks: the accepted `O3` ingress/import/export surface remains host-specific and loopback-only on purpose. It may not bind remotely, invent multi-session or multi-client doctrine, invent a service-specific persistence format, or introduce a generic runtime/service layer. `/v1/events` must continue to consume the accepted `O2` transcript parser rather than bypassing host-shaped ingress law. `/v1/session/export` and `/v1/session/import` may move only the accepted `openai_product_journal` JSON artifact; they may not become path-based file APIs. Later bounded host-control work may reuse the same module, but it may not retroactively change the meaning or shape of the landed `O3` endpoints. The service shell may expose a more live boundary, but it may not promote removed control-residue fields back into stronger truth than the accepted `C1`/`O1`/`O2` contracts allow.

---

### 1.25 OpenAI bounded outbound host-control lane

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| request-scoped verified-work task-set carrier for larger-task OpenAI host-control activation over the explicit bookmarks + normalize-port + feature-flags profile domain | `WorkContract` | `cortex/sre/verified_work.py` | `test_verified_work.py::test_work_contract_accepts_only_first_train_shape` + `test_verified_work.py::test_work_contract_rejects_duplicate_or_unbounded_paths` | landed |
| deterministic verified-work external outcome carrier over parse/import/pytest/blocked result | `VerificationOutcome` | `cortex/sre/verified_work.py` | `test_verified_work.py::test_verification_outcome_rejects_incoherent_status_and_failure_class` + `test_verified_work_runtime.py::test_verify_verified_work_result_preserves_blocked_missing_info` + `test_verified_work_runtime.py::test_verify_verified_work_result_accepts_passing_submission` | landed |
| bounded verified-work follow-up gate over `continue | repair | check | stop` | `choose_verified_work_followup()` | `cortex/sre/verified_work.py` | `test_verified_work.py::test_choose_verified_work_followup_matches_exact_first_train_law` | landed |
| bounded outbound OpenAI host-control request carrier over the thin default path plus optional verified-work activation across the explicit three-profile verifier domain | `OpenAIHostControlRequest` | `cortex/runtime/openai_host_control.py` | `test_openai_host_control.py::test_openai_host_control_request_constructs_strict_text_only_payload` + `test_openai_host_control.py::test_openai_host_control_request_constructs_verified_work_payload` + `test_openai_host_control.py::test_openai_host_control_service_boundary_rejects_out_of_scope_keys` + `test_openai_host_control.py::test_openai_host_control_service_boundary_rejects_instructions_when_work_contract_present` | landed |
| bounded outbound OpenAI host-control result carrier over exact compact `O1` records plus optional verified-work verification summary | `OpenAIHostControlResult` | `cortex/runtime/openai_host_control.py` | `test_openai_host_control.py::test_openai_host_control_result_rejects_wrong_action_tag` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_one_shot_adds_verification` | landed |
| stdlib OpenAI Responses create+stream transport over the bounded host-control family | `execute_openai_response_stream()` + `execute_openai_response_stream_turn()` | `cortex/runtime/openai_host_transport.py` | `test_openai_host_control.py::test_parse_sse_events_converts_stream_frames_into_o2_shaped_records` + `test_openai_host_control.py::test_parse_sse_events_rejects_zero_event_stream` + `test_openai_host_control.py::test_parse_sse_events_rejects_malformed_json_event` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_repairs_once_from_runtime_signal` | landed |
| deterministic verified-work model-input packer over the user task plus bounded read-only profile-selected workspace context across the explicit three-pack breadth registry | `build_verified_work_input_text()` | `cortex/runtime/verified_work_runtime.py` | `test_verified_work_runtime.py::test_build_verified_work_input_text_attaches_workspace_context` + `test_verified_work_runtime.py::test_build_verified_work_input_text_attaches_normalize_port_context` + `test_verified_work_runtime.py::test_build_verified_work_input_text_attaches_feature_flags_context` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_workspace_context_to_first_attempt` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_normalize_port_context` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_feature_flags_context` | landed |
| deterministic verified-work protocol parser plus bounded profile-selected verifier runtime across the explicit three-pack breadth registry | `verify_verified_work_result()` | `cortex/runtime/verified_work_runtime.py` | `test_verified_work_runtime.py::test_verify_verified_work_result_rejects_unapproved_path` + `test_verified_work_runtime.py::test_verify_verified_work_result_preserves_blocked_missing_info` + `test_verified_work_runtime.py::test_verify_verified_work_result_ignores_blank_lines_between_file_blocks` + `test_verified_work_runtime.py::test_verify_verified_work_result_accepts_passing_submission` + `test_verified_work_runtime.py::test_verify_verified_work_result_uses_profile_specific_verifier_targets` | landed |
| runtime-native OpenAI verification binder over external verified-work outcome | `run_openai_runtime_verification_step()` | `cortex/runtime/openai.py` | `test_openai_runtime_step.py::test_openai_runtime_verification_step_updates_runtime_truth_from_external_failure` + `test_openai_runtime_step.py::test_openai_runtime_verification_step_maps_blocked_missing_info_to_check` | landed |
| outbound action -> accepted `O2`/compressed `O1` runtime composition over exact `decision + journal` projection plus bounded verified-work profile routing, workspace-context attachment, and optional repair turn across the explicit three-pack breadth registry | `run_openai_host_control()` | `cortex/runtime/openai_host_control.py` | `test_openai_host_control.py::test_run_openai_host_control_matches_manual_o1_runtime_projection` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_one_shot_adds_verification` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_workspace_context_to_first_attempt` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_repairs_once_from_runtime_signal` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_normalize_port_context` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_normalize_port_repairs_once` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_attaches_feature_flags_context` + `test_openai_host_control.py::test_run_openai_host_control_verified_work_feature_flags_repairs_once` + `test_openai_host_control_continuity.py::test_openai_host_control_export_import_preserves_control_truth` | landed |
| loopback service outbound action boundary over the bounded `O4`/`O4R` family and compact `O1`/`O3` carriers | `handle_openai_service_action()` | `cortex/runtime/openai_service.py` | `tests/unit/test_openai_service.py::test_openai_service_action_roundtrips_records_with_fake_transport` + `tests/unit/test_openai_service.py::test_openai_service_action_roundtrips_verified_work_payload` + `tests/unit/test_openai_host_control.py::test_openai_host_control_service_boundary_rejects_out_of_scope_keys` + `tests/integration/test_openai_host_control_service.py::test_openai_host_control_action_endpoint_returns_ordered_o1_records_and_mutates_session` + `tests/integration/test_openai_host_control_service.py::test_openai_host_control_action_endpoint_reports_verified_work_blocked_result` + `tests/integration/test_openai_host_control_service.py::test_openai_host_control_action_endpoint_upstream_failure_returns_502_without_mutating_session` | landed |

Forbidden leaks: the accepted thin `O4` path remains host-specific, text-only by default, and single-family on purpose. Verified-work activation may add one optional `work_contract`, one deterministic `full_files` carrier, one runtime-native external verification binder, and one bounded repair turn, but it may not widen into prompt shaping, hidden implementation preferences, generic planner doctrine, automatic carrier selection, diff-based larger-task carriers, tools or tool-result submission, cancel/update lanes, multimodal request doctrine, remote hosting, multi-session or multi-client doctrine, generic runtime/service abstraction, or cross-process executive memory. The transport may use only a stdlib OpenAI-specific client for current scope and the canonical verification bundle may not require live network or a real API key. Returned upstream host events must re-enter through the accepted `O2` transcript parser and accepted compressed `O1` runtime shell rather than bypassing those laws. `O4`/`O4R` may realize one bounded outbound effect family, but they may not reintroduce removed control-residue or allocation-diagnostic fields as stronger cross-process truth, and diagnostic SRE modulators may not silently drive the verified-work loop.

---

### 1.26 Gemini documented host-event runtime shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini host-runtime live session carrier over documented raw host events plus accepted `C1` continuation law | `GeminiRuntimeSession` | `cortex/runtime/gemini.py` | `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_roundtrips_bounded_residue` + `test_gemini_runtime_continuity.py::test_gemini_runtime_split_session_is_g1_equivalent_to_uninterrupted_run` | landed |
| Gemini host-runtime control ledger carrier with nested executive allocation diagnostics | `GeminiControlLedger` | `cortex/runtime/gemini.py` | `test_gemini_runtime_cli.py::test_gemini_runtime_cli_reads_documented_raw_events_and_preserves_host_name` | landed |
| Gemini host-runtime step result carrier | `GeminiRuntimeStepResult` | `cortex/runtime/gemini.py` | `test_gemini_runtime_cli.py::test_gemini_runtime_cli_reads_documented_raw_events_and_preserves_host_name` | landed |
| Gemini host-runtime step composition over landed Gemini observe/bind, commitment-path helpers, accepted K3 executive allocation, and accepted bounded continuation law | `run_gemini_runtime_step()` | `cortex/runtime/gemini.py` | `test_gemini_runtime_step.py::test_gemini_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing` + `test_gemini_runtime_cli.py::test_gemini_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_gemini_runtime_cli.py::test_gemini_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` + `test_gemini_runtime_continuity.py::test_gemini_runtime_host_warning_and_certified_commitment_can_coexist_across_restart` | landed |
| Gemini bounded persisted continuation carrier split into exact `continuity_truth` and bounded `control_residue` | `GeminiRuntimeSessionArtifact` | `cortex/runtime/gemini_session_io.py` | `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_roundtrips_bounded_residue` | landed |
| Gemini runtime session -> persisted artifact build boundary | `build_gemini_runtime_session_artifact()` | `cortex/runtime/gemini_session_io.py` | `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_roundtrips_bounded_residue` | landed |
| Gemini persisted artifact -> runtime session parse boundary | `parse_gemini_runtime_session_artifact()` | `cortex/runtime/gemini_session_io.py` | `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_rejects_unknown_keys_and_invalid_enums` + `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_one_sided_last_feedback_normalizes_through_session_constructor` | landed |
| Gemini persisted artifact file read/write boundaries for the local CLI shell | `read_gemini_runtime_session_artifact()` + `write_gemini_runtime_session_artifact()` | `cortex/runtime/gemini_session_io.py` | `test_gemini_runtime_session_io.py::test_gemini_runtime_session_artifact_same_path_overwrite_safety` + `test_gemini_runtime_cli.py::test_gemini_runtime_cli_explicit_load_save_works` + `test_gemini_runtime_cli.py::test_gemini_runtime_cli_load_save_failure_emits_no_stdout` | landed |
| Gemini developer-facing runtime output projection with preserved raw host event name and nested executive allocation diagnostics | `build_gemini_cli_record()` | `cortex/runtime/gemini_cli.py` | `test_gemini_runtime_cli.py::test_gemini_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_gemini_runtime_cli.py::test_gemini_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` | landed |

Forbidden leaks: `G1` remains Gemini-specific on purpose. It may not introduce a fake host-neutral runtime layer, generic store doctrine, live network/service doctrine, or broader Gemini host action realization than the separately scoped `G4` lane allows. Raw Gemini host event names must remain visible in the outward projection and undocumented host events must remain explicit conservative warnings rather than fabricated parity. Gemini persisted continuation remains bounded to exact `continuity_truth` plus bounded `control_residue`; full shell-long `budget_history` and `brake_history` may remain public one-process diagnostics, but they may not become cross-process continuation truth.

---

### 1.27 Gemini raw-transcript ingress shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini raw host-transcript ingress carrier over transcript `type` plus payload remainder | `GeminiHostEventEnvelope` | `cortex/runtime/gemini_ingress.py` | `test_gemini_ingress.py::test_documented_raw_gemini_event_parses_cleanly` + `test_gemini_ingress.py::test_undocumented_raw_content_event_still_parses_cleanly` | landed |
| raw transcript -> Gemini ingress carrier parse boundary | `parse_gemini_host_event_envelope()` | `cortex/runtime/gemini_ingress.py` | `test_gemini_ingress.py::test_canonical_cortex_event_name_is_rejected` + `test_gemini_ingress.py::test_dev_shell_wrapper_shape_is_rejected` + `test_gemini_ingress.py::test_missing_type_and_non_object_record_are_rejected` | landed |
| Gemini raw-transcript ingress CLI over accepted `G1` runtime shell | `main()` | `cortex/runtime/gemini_ingress_cli.py` | `test_gemini_ingress_cli.py::test_gemini_ingress_cli_reads_documented_raw_transcript_fixture` + `test_gemini_ingress_cli.py::test_gemini_ingress_cli_rejects_canonical_event_names_wrapper_shape_and_mixed_shape` + `test_gemini_ingress_cli.py::test_gemini_ingress_cli_undocumented_raw_host_event_still_warns_conservatively` | landed |

Forbidden leaks: `G2` owns transcript-shape parsing only. It may not mutate `G1` into the only Gemini shell, may not accept the dev-shell wrapper shape as lawful ingress, may not accept mixed wrapper/transcript records as lawful ingress, and may not fabricate host parity by silently normalizing canonical Cortex event names back into raw Gemini host traffic. `gemini_ingress_cli.py` may consume accepted `run_gemini_runtime_step()` and the accepted `G1` session artifact, but it may not become a new runtime owner or a generic ingress abstraction.

---

### 1.28 Gemini loopback service shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Gemini loopback service state carrier over exactly one active runtime session per process | `GeminiServiceState` | `cortex/runtime/gemini_service.py` | `test_gemini_service.py::test_gemini_service_state_constructs_cleanly` | landed |
| loopback Gemini service request dispatch over accepted `G2` transcript parsing and accepted `G1` runtime/session law | `handle_gemini_service_request()` | `cortex/runtime/gemini_service.py` | `test_gemini_service.py::test_gemini_service_invalid_import_becomes_400_error_payload` + `test_gemini_service_http.py::test_gemini_service_unknown_path_and_wrong_method_return_json_errors` + `test_gemini_service_http.py::test_gemini_service_health_and_documented_event_flow` | landed |
| Gemini loopback service artifact export/import boundaries | `export_gemini_service_session()` + `import_gemini_service_session()` | `cortex/runtime/gemini_service.py` | `test_gemini_service.py::test_gemini_service_import_export_preserves_exact_artifact_shape` + `test_gemini_service_http.py::test_gemini_service_session_export_import_and_startup_load_roundtrip` | landed |
| Gemini loopback service shell entrypoint | `main()` | `cortex/runtime/gemini_service.py` | `test_gemini_service_http.py::test_gemini_service_health_and_documented_event_flow` + `test_gemini_service_http.py::test_gemini_service_undocumented_raw_event_warns_without_fabricating_parity` + `test_gemini_service_continuity.py::test_gemini_service_event_sequence_is_g3_equivalent_to_g2_ingress_shell` | landed |

Forbidden leaks: `G3` remains host-specific and loopback-only on purpose. It may not bind remotely, invent multi-session or multi-client doctrine, invent a service-specific persistence format, or introduce a generic runtime/service layer. `/v1/events` must continue to consume the accepted `G2` transcript parser rather than bypassing host-shaped ingress law. `/v1/session/export` and `/v1/session/import` may move only the accepted Gemini runtime session artifact as JSON; they may not become path-based file APIs.

---

### 1.29 Gemini bounded outbound host-control lane

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| bounded outbound Gemini host-control request carrier | `GeminiHostControlRequest` | `cortex/runtime/gemini_host_control.py` | `test_gemini_host_control.py::test_gemini_host_control_request_constructs_strict_text_only_payload` + `test_gemini_host_control.py::test_gemini_host_control_service_boundary_rejects_out_of_scope_keys` | landed |
| bounded outbound Gemini host-control result carrier | `GeminiHostControlResult` | `cortex/runtime/gemini_host_control.py` | `test_gemini_host_control.py::test_gemini_host_control_result_rejects_wrong_action_tag` + `test_gemini_host_control.py::test_run_gemini_host_control_matches_manual_g1_runtime_projection` | landed |
| stdlib Gemini `streamGenerateContent` transport over the bounded text-only lane | `execute_gemini_interaction_stream()` | `cortex/runtime/gemini_host_transport.py` | `test_gemini_host_control.py::test_parse_sse_events_converts_stream_frames_into_g2_shaped_records` + `test_gemini_host_control.py::test_parse_sse_events_rejects_zero_event_stream` + `test_gemini_host_control.py::test_parse_sse_events_rejects_malformed_json_event` + `test_gemini_host_control.py::test_run_gemini_host_control_matches_manual_g1_runtime_projection` | landed |
| outbound Gemini action -> accepted `G2`/`G1` runtime composition | `run_gemini_host_control()` | `cortex/runtime/gemini_host_control.py` | `test_gemini_host_control.py::test_run_gemini_host_control_matches_manual_g1_runtime_projection` + `test_gemini_host_control_continuity.py::test_gemini_host_control_export_import_preserves_control_truth` | landed |
| loopback Gemini service outbound action boundary over the bounded `G4` lane | `handle_gemini_service_action()` | `cortex/runtime/gemini_service.py` | `test_gemini_service.py::test_gemini_service_action_roundtrips_records_with_fake_transport` + `test_gemini_host_control.py::test_gemini_host_control_service_boundary_rejects_out_of_scope_keys` + `test_gemini_host_control_service.py::test_gemini_host_control_action_endpoint_returns_ordered_g1_records_and_mutates_session` + `test_gemini_host_control_service.py::test_gemini_host_control_action_endpoint_upstream_failure_returns_502_without_mutating_session` | landed |

Forbidden leaks: `G4` remains host-specific, text-only, and single-lane on purpose. It may not widen into tools or tool-result submission, cancel/update lanes, multimodal or content-part request doctrine, remote hosting, multi-session or multi-client doctrine, generic runtime/service abstraction, or a second executive doctrine. The transport may use only a stdlib Gemini-specific client for current scope and the canonical verification bundle may not require live network or a real API key. Returned upstream host events must re-enter through the accepted `G2` transcript parser and accepted `G1` runtime shell rather than bypassing those laws.

---

### 1.30 Claude documented host-event runtime shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Claude host-runtime live session carrier over documented raw host events plus accepted `C1` continuation law | `ClaudeRuntimeSession` | `cortex/runtime/claude.py` | `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_roundtrips_bounded_residue` + `test_claude_runtime_continuity.py::test_claude_runtime_split_session_is_g1_equivalent_to_uninterrupted_run` | landed |
| Claude host-runtime control ledger carrier with nested executive allocation diagnostics | `ClaudeControlLedger` | `cortex/runtime/claude.py` | `test_claude_runtime_cli.py::test_claude_runtime_cli_reads_documented_raw_events_and_preserves_host_name` | landed |
| Claude host-runtime step result carrier | `ClaudeRuntimeStepResult` | `cortex/runtime/claude.py` | `test_claude_runtime_cli.py::test_claude_runtime_cli_reads_documented_raw_events_and_preserves_host_name` | landed |
| Claude host-runtime step composition over landed Claude observe/bind, commitment-path helpers, accepted K3 executive allocation, and accepted bounded continuation law | `run_claude_runtime_step()` | `cortex/runtime/claude.py` | `test_claude_runtime_step.py::test_claude_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing` + `test_claude_runtime_cli.py::test_claude_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_claude_runtime_cli.py::test_claude_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` + `test_claude_runtime_continuity.py::test_claude_runtime_host_warning_and_certified_commitment_can_coexist_across_restart` | landed |
| Claude bounded persisted continuation carrier split into exact `continuity_truth` and bounded `control_residue` | `ClaudeRuntimeSessionArtifact` | `cortex/runtime/claude_session_io.py` | `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_roundtrips_bounded_residue` | landed |
| Claude runtime session -> persisted artifact build boundary | `build_claude_runtime_session_artifact()` | `cortex/runtime/claude_session_io.py` | `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_roundtrips_bounded_residue` | landed |
| Claude persisted artifact -> runtime session parse boundary | `parse_claude_runtime_session_artifact()` | `cortex/runtime/claude_session_io.py` | `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_rejects_unknown_keys_and_invalid_enums` + `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_one_sided_last_feedback_normalizes_through_session_constructor` | landed |
| Claude persisted artifact file read/write boundaries for the local CLI shell | `read_claude_runtime_session_artifact()` + `write_claude_runtime_session_artifact()` | `cortex/runtime/claude_session_io.py` | `test_claude_runtime_session_io.py::test_claude_runtime_session_artifact_same_path_overwrite_safety` + `test_claude_runtime_cli.py::test_claude_runtime_cli_explicit_load_save_works` + `test_claude_runtime_cli.py::test_claude_runtime_cli_load_save_failure_emits_no_stdout` | landed |
| Claude developer-facing runtime output projection with preserved raw host event name, top-level `message_id`, and nested executive allocation diagnostics | `build_claude_cli_record()` | `cortex/runtime/claude_cli.py` | `test_claude_runtime_cli.py::test_claude_runtime_cli_reads_documented_raw_events_and_preserves_host_name` + `test_claude_runtime_cli.py::test_claude_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity` | landed |

Forbidden leaks: `A1` remains Claude-specific on purpose. It may not introduce a fake host-neutral runtime layer, generic store doctrine, live network/service doctrine, or broader Claude host action realization than the separately scoped `A4` lane allows. Raw Claude host event names must remain visible in the outward projection and undocumented host events must remain explicit conservative warnings rather than fabricated parity. Claude persisted continuation remains bounded to exact `continuity_truth` plus bounded `control_residue`; full shell-long `budget_history` and `brake_history` may remain public one-process diagnostics, but they may not become cross-process continuation truth.

---

### 1.31 Claude raw-transcript ingress shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Claude raw host-transcript ingress carrier over transcript `type` plus payload remainder | `ClaudeHostEventEnvelope` | `cortex/runtime/claude_ingress.py` | `test_claude_ingress.py::test_documented_raw_claude_event_parses_cleanly` + `test_claude_ingress.py::test_undocumented_raw_content_event_still_parses_cleanly` | landed |
| raw transcript -> Claude ingress carrier parse boundary | `parse_claude_host_event_envelope()` | `cortex/runtime/claude_ingress.py` | `test_claude_ingress.py::test_canonical_cortex_event_name_is_rejected` + `test_claude_ingress.py::test_dev_shell_wrapper_shape_is_rejected` + `test_claude_ingress.py::test_missing_type_and_non_object_record_are_rejected` | landed |
| Claude raw-transcript ingress CLI over accepted `A1` runtime shell | `main()` | `cortex/runtime/claude_ingress_cli.py` | `test_claude_ingress_cli.py::test_claude_ingress_cli_reads_documented_raw_transcript_fixture` + `test_claude_ingress_cli.py::test_claude_ingress_cli_rejects_canonical_event_names_wrapper_shape_and_mixed_shape` + `test_claude_ingress_cli.py::test_claude_ingress_cli_undocumented_raw_host_event_still_warns_conservatively` | landed |

Forbidden leaks: `A2` owns transcript-shape parsing only. It may not mutate `A1` into the only Claude shell, may not accept the dev-shell wrapper shape as lawful ingress, may not accept mixed wrapper/transcript records as lawful ingress, and may not fabricate host parity by silently normalizing canonical Cortex event names back into raw Claude host traffic. `claude_ingress_cli.py` may consume accepted `run_claude_runtime_step()` and the accepted `A1` session artifact, but it may not become a new runtime owner or a generic ingress abstraction.

---

### 1.32 Claude loopback service shell

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| Claude loopback service state carrier over exactly one active runtime session per process | `ClaudeServiceState` | `cortex/runtime/claude_service.py` | `test_claude_service.py::test_claude_service_state_constructs_cleanly` | landed |
| loopback Claude service request dispatch over accepted `A2` transcript parsing and accepted `A1` runtime/session law | `handle_claude_service_request()` | `cortex/runtime/claude_service.py` | `test_claude_service.py::test_claude_service_invalid_import_becomes_400_error_payload` + `test_claude_service_http.py::test_claude_service_unknown_path_and_wrong_method_return_json_errors` + `test_claude_service_http.py::test_claude_service_health_and_documented_event_flow` | landed |
| Claude loopback service artifact export/import boundaries | `export_claude_service_session()` + `import_claude_service_session()` | `cortex/runtime/claude_service.py` | `test_claude_service.py::test_claude_service_import_export_preserves_exact_artifact_shape` + `test_claude_service_http.py::test_claude_service_session_export_import_and_startup_load_roundtrip` | landed |
| Claude loopback service shell entrypoint | `main()` | `cortex/runtime/claude_service.py` | `test_claude_service_http.py::test_claude_service_health_and_documented_event_flow` + `test_claude_service_http.py::test_claude_service_undocumented_raw_event_warns_without_fabricating_parity` + `test_claude_service_continuity.py::test_claude_service_event_sequence_is_g3_equivalent_to_g2_ingress_shell` | landed |

Forbidden leaks: `A3` remains host-specific and loopback-only on purpose. It may not bind remotely, invent multi-session or multi-client doctrine, invent a service-specific persistence format, or introduce a generic runtime/service layer. `/v1/events` must continue to consume the accepted `A2` transcript parser rather than bypassing host-shaped ingress law. `/v1/session/export` and `/v1/session/import` may move only the accepted Claude runtime session artifact as JSON; they may not become path-based file APIs.

---

### 1.33 Claude bounded outbound host-control lane

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| bounded outbound Claude host-control request carrier | `ClaudeHostControlRequest` | `cortex/runtime/claude_host_control.py` | `test_claude_host_control.py::test_claude_host_control_request_constructs_strict_text_only_payload` + `test_claude_host_control.py::test_claude_host_control_service_boundary_rejects_out_of_scope_keys` | landed |
| bounded outbound Claude host-control result carrier | `ClaudeHostControlResult` | `cortex/runtime/claude_host_control.py` | `test_claude_host_control.py::test_claude_host_control_result_rejects_wrong_action_tag` + `test_claude_host_control.py::test_run_claude_host_control_matches_manual_g1_runtime_projection` | landed |
| stdlib Anthropic Messages streaming transport over the bounded text-only lane | `execute_claude_message_stream()` | `cortex/runtime/claude_host_transport.py` | `test_claude_host_control.py::test_parse_sse_events_converts_stream_frames_into_g2_shaped_records` + `test_claude_host_control.py::test_parse_sse_events_rejects_zero_event_stream` + `test_claude_host_control.py::test_parse_sse_events_rejects_malformed_json_event` + `test_claude_host_control.py::test_run_claude_host_control_matches_manual_g1_runtime_projection` | landed |
| outbound Claude action -> accepted `A2`/`A1` runtime composition | `run_claude_host_control()` | `cortex/runtime/claude_host_control.py` | `test_claude_host_control.py::test_run_claude_host_control_matches_manual_g1_runtime_projection` + `test_claude_host_control_continuity.py::test_claude_host_control_export_import_preserves_control_truth` | landed |
| loopback Claude service outbound action boundary over the bounded `A4` lane | `handle_claude_service_action()` | `cortex/runtime/claude_service.py` | `test_claude_service.py::test_claude_service_action_roundtrips_records_with_fake_transport` + `test_claude_host_control.py::test_claude_host_control_service_boundary_rejects_out_of_scope_keys` + `test_claude_host_control_service.py::test_claude_host_control_action_endpoint_returns_ordered_g1_records_and_mutates_session` + `test_claude_host_control_service.py::test_claude_host_control_action_endpoint_upstream_failure_returns_502_without_mutating_session` | landed |

Forbidden leaks: `A4` remains host-specific, text-only, and single-lane on purpose. It may not widen into tools or tool-result submission, cancel/update lanes, multimodal or content-part request doctrine, remote hosting, multi-session or multi-client doctrine, generic runtime/service abstraction, or a second executive doctrine. The transport may use only a stdlib Claude-specific client for current scope and the canonical verification bundle may not require live network or a real API key. Returned upstream host events must re-enter through the accepted `A2` transcript parser and accepted `A1` runtime shell rather than bypassing those laws.

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

## 3. SRE correspondence

Rows marked `landed` are code-backed. Remaining rows are still target correspondence for later SRE phases.

| Packet math | Code object | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `X_t^{ref} = (x_t^G, x_t^U, x_t^M, x_t^K, x_t^J)` (reference executive state) | `ReferenceExecutiveState` | `cortex/sre/state.py` | `test_sre_neutral_hinge.py::test_reference_executive_state_exposes_minimum_software_facing_views` + `test_sre_neutral_hinge.py::test_reference_executive_state_uses_canonical_uncertainty_and_brake_types` + `test_sre_neutral_hinge.py::test_reference_state_surface_does_not_export_duplicate_uncertainty_carrier` + `test_sre_goals_branching.py::test_reference_executive_state_uses_canonical_goal_carrier_directly` + `test_sre_goals_branching.py::test_reference_state_surface_keeps_only_a_compatibility_alias_for_goal_view` | landed |
| `x_t^M` (mode-and-gating role view) | `ReferenceModeAndGatingView` | `cortex/sre/state.py` | `test_sre_neutral_hinge.py::test_reference_executive_state_exposes_minimum_software_facing_views` + `test_sre_neutral_hinge.py::test_reference_mode_and_gating_view_requires_non_empty_mode_tag` + `test_sre_neutral_hinge.py::test_reference_mode_and_gating_view_requires_typed_family_mask` | landed |
| `x_t^K` (control-allocation role view) | `ReferenceControlAllocationView` | `cortex/sre/state.py` | `test_sre_neutral_hinge.py::test_reference_executive_state_exposes_minimum_software_facing_views` + `test_sre_neutral_hinge.py::test_reference_control_allocation_view_requires_non_empty_budget_band` + `test_sre_neutral_hinge.py::test_reference_control_allocation_view_requires_typed_top_family_set` + `test_sre_neutral_hinge.py::test_reference_control_allocation_view_requires_non_empty_host_friction_tags` + `test_sre_neutral_hinge.py::test_reference_control_allocation_view_requires_non_empty_feedback_pressure_tags` | landed |
| bounded reference short-window feedback summary carrier over rejection/override pressure plus explicit evidence-move, continuity-improvement, and non-productive family-switch counts | `ReferenceFeedbackWindowSummary` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_zero_pressure_for_clean_window` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_repeated_rejection_floor_and_sustained_disruption` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_mixed_rejection_and_override_bonus` | landed |
| bounded short-window realized-outcome summary law | `summarize_reference_feedback_window()` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_single_rejection_floor` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_repeated_override_floor` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_mixed_rejection_and_override_bonus` | landed |
| `X_t^{ref}` first bounded event-to-state realization over runtime observation, support snapshot, executive environment view, bounded short-window feedback summary, explicit productive-exploration versus oscillation carriers, explicit branch-burden fields, and exact missing-context / missing-capability `seek-context` reachability admission | `build_reference_executive_state()` | `cortex/sre/reference_builder.py` | `test_reference_executive_builder.py::test_build_reference_executive_state_for_cheap_event_stays_pass_through_and_low_budget` + `test_reference_executive_builder.py::test_build_reference_executive_state_admits_seek_context_under_missing_capability_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_keeps_seek_context_closed_under_generic_host_friction` + `test_reference_executive_builder.py::test_build_reference_executive_state_for_candidate_bearing_event_surfaces_review_mode` + `test_reference_executive_builder.py::test_build_reference_executive_state_for_full_commitment_event_preserves_high_budget_band` + `test_reference_executive_builder.py::test_build_reference_executive_state_surfaces_guarded_brake_when_snapshot_has_degradation` + `test_reference_executive_builder.py::test_build_reference_executive_state_raises_goal_progress_floor_after_session_rejection` + `test_reference_executive_builder.py::test_build_reference_executive_state_marks_prior_enforcement_override` + `test_reference_executive_builder.py::test_build_reference_executive_state_uses_repeated_rejection_window_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_uses_repeated_override_window_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_clean_window_does_not_raise_pressure` | landed |
| `\mathcal A_t^{pre}` / pre-brake family admission law over the reference family mask and top-family set | `build_reference_executive_state()` | `cortex/sre/reference_builder.py` | `test_reference_executive_builder.py::test_build_reference_executive_state_admits_seek_context_under_missing_capability_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_keeps_seek_context_closed_under_generic_host_friction` | landed |
| `A^{ref}` (soft-control family set) | `SoftControlFamily` | `cortex/sre/families.py` | `test_sre_neutral_hinge.py::test_exact_soft_control_family_set_matches_the_packet` | landed |
| `Q_t^{alloc}(a)` executive allocation carrier with explicit `online_score`, `memory_score`, `allocated_score`, and `alpha_t` | `AllocationScore` + `AllocationScorecard` | `cortex/sre/allocation.py` | `test_sre_neutral_hinge.py::test_neutral_dominance_returns_neutral_when_margin_is_below_threshold` + `test_sre_neutral_hinge.py::test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met` + `test_sre_neutral_hinge.py::test_allocation_score_defaults_online_and_allocated_to_score` + `test_sre_neutral_hinge.py::test_allocation_scorecard_requires_alpha_in_unit_interval` | landed |
| `Q_t^{mem}(a)` active target memory-conditioned contribution; current landing law keeps it explicit-and-zero unless an explicit AUX-derived support-memory appendix is present | `SupportMemoryPriorAppendix` + `SupportMemoryPriorScore` feeding `AllocationScore.memory_score` | `cortex/sre/memory_priors.py` + `cortex/sre/reference_scoring.py` + `cortex/aux/support_priors.py` | `test_sre_memory_priors.py::test_support_memory_prior_score_requires_bounded_score_and_typed_refs` + `test_sre_memory_priors.py::test_support_memory_prior_appendix_keeps_single_score_per_family_and_defaults_missing_scores_to_zero` + `test_reference_runtime_scoring.py::test_reference_scoring_activates_q_mem_only_when_explicit_support_memory_priors_are_present` + `test_aux_support_priors.py::test_build_support_memory_prior_appendix_derives_nonzero_family_priors_from_offline_publication` | landed |
| `\chi_t` bounded vigor/intensity scalar for the already-selected family | `ReferenceSoftControlSelection.chi_t` + `compute_reference_chi_t()` | `cortex/sre/reference_scoring.py` | `test_reference_runtime_scoring.py::test_reference_selection_exposes_bounded_chi_t_and_lowers_it_under_guarded_pressure` | landed |
| `Q_t^{goalbranch}(a)` bounded branch/goal family contribution over continuity debt, resume-anchor truth, and brake-conditioned branch pressure | `GoalBranchScore` + `GoalBranchCoupling` | `cortex/sre/goal_branch.py` | `test_sre_goal_branch.py::test_goal_branch_coupling_is_zero_without_continuity_debt` + `test_sre_goal_branch.py::test_goal_branch_coupling_lifts_branch_and_redirect_under_pending_goals` + `test_sre_goal_branch.py::test_goal_branch_coupling_shifts_toward_check_without_resume_anchor` + `test_sre_goal_branch.py::test_goal_branch_coupling_reduces_branch_score_under_latched_brake` | landed |
| `\lambda_G` bounded goal-branch coupling weight in the active allocation law | `GoalBranchCoupling.weight` | `cortex/sre/goal_branch.py` | `test_sre_goal_branch.py::test_goal_branch_coupling_lifts_branch_and_redirect_under_pending_goals` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_branch_under_branch_pressure` | landed |
| goal-branch realization in the active allocation path | `build_reference_goal_branch_coupling()` + scorecard integration in `build_reference_allocation_scorecard()` | `cortex/sre/goal_branch.py` + `cortex/sre/reference_scoring.py` | `test_sre_goal_branch.py::test_goal_branch_coupling_is_zero_without_continuity_debt` + `test_sre_goal_branch.py::test_goal_branch_coupling_lifts_branch_and_redirect_under_pending_goals` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_branch_under_branch_pressure` | landed |
| `Q_t^{online}(a)` / `Q_t^{alloc}(a)` first explicit bounded scoring realization over landed executive state plus family-sensitive threshold law, exact-pressure `seek-context` reachability lift, branch-burden truth, and productive-exploration versus oscillation shaping | `build_reference_allocation_scorecard()` + `build_reference_online_score_components()` + `compute_reference_alpha_t()` + `compute_reference_activation_threshold()` | `cortex/sre/reference_scoring.py` | `test_reference_runtime_scoring.py::test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold` + `test_reference_runtime_scoring.py::test_reference_scoring_selects_seek_context_under_missing_capability_pressure_when_admitted` + `test_reference_runtime_scoring.py::test_reference_scoring_keeps_seek_context_neutral_dominated_under_generic_host_friction_even_if_admitted` + `test_reference_runtime_scoring.py::test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked` + `test_reference_runtime_scoring.py::test_reference_scoring_exposes_explicit_online_allocation_diagnostics` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_branch_under_branch_pressure` + `test_reference_runtime_scoring.py::test_reference_scoring_uses_family_sensitive_thresholds_for_probe_relief_vs_branching` + `test_reference_runtime_scoring.py::test_reference_scoring_rewards_anchored_branch_work_and_penalizes_orphaned_branch_trees` + `test_reference_runtime_scoring.py::test_reference_scoring_distinguishes_productive_exploration_from_oscillation` + `test_reference_runtime_scoring.py::test_reference_alpha_t_changes_with_visible_pressure_only` + `test_reference_runtime_scoring.py::test_reference_activation_threshold_uses_feedback_pressure_without_touching_alpha` + `test_reference_runtime_scoring.py::test_reference_scoring_selection_can_change_under_allocated_score_semantics` | landed |
| `Δ_t(a)` and family-sensitive `θ_t^{act}(a)` (neutral-dominance law) | `compute_reference_activation_threshold()` + `neutral_dominance_decision()` | `cortex/sre/reference_scoring.py` + `cortex/sre/policy.py` | `test_sre_neutral_hinge.py::test_neutral_dominance_returns_neutral_when_margin_is_below_threshold` + `test_sre_neutral_hinge.py::test_neutral_dominance_ranks_by_allocated_score_not_raw_online_score` + `test_sre_neutral_hinge.py::test_neutral_dominance_uses_allocated_margin_for_threshold` + `test_sre_neutral_hinge.py::test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met` + `test_sre_neutral_hinge.py::test_neutral_path_law_rejects_scorecards_that_omit_neutral` | landed |
| `Q_t^{final}(a)` experimental mediation-finalizer carrier and off-by-default host-realization finalization law | `ReferenceMediationFinalization` + `ReferenceMediationMode` + `finalize_reference_soft_control()` | `cortex/sre/mediation.py` | `test_sre_mediation.py::test_reference_mediation_identity_mode_preserves_family_without_specialization` + `test_sre_mediation.py::test_reference_mediation_experimental_mode_specializes_seek_context_when_runtime_visible_opportunity_exists` + `test_sre_mediation.py::test_reference_mediation_experimental_mode_keeps_identity_for_non_seek_context_family` + `test_sre_mediation.py::test_reference_mediation_experimental_mode_preserves_existing_degradation_fallback_semantics` | landed |
| `U_t^{sre}` bounded soft-control selection with explicit pre-finalization and post-finalization family truth | `ReferenceSoftControlSelection` + `select_reference_soft_control()` | `cortex/sre/reference_scoring.py` | `test_reference_runtime_scoring.py::test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold` + `test_reference_runtime_scoring.py::test_reference_scoring_selects_seek_context_under_missing_capability_pressure_when_admitted` + `test_reference_runtime_scoring.py::test_reference_scoring_identity_mode_preserves_seek_context_without_direct_specialization` + `test_reference_runtime_scoring.py::test_reference_scoring_experimental_mode_specializes_only_seek_context` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_branch_under_branch_pressure` + `test_reference_runtime_scoring.py::test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked` | landed |
| `\mathcal A_t^{post}` / brake-conditioned realization constraints with explicit selected-family versus realized-family truth and minimum-burden latched uncertainty-relief exceptions | `_realize_family()` | `cortex/hosts/reference/runtime.py` | `test_reference_runtime_step.py::test_reference_runtime_step_experimental_mediation_specializes_reference_mcp_query` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_neutral_without_evidence_or_environment` + `test_reference_runtime_step.py::test_reference_runtime_step_allows_latched_seek_context_when_native_host_capability_relief_is_directly_justified` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_guarded_feedback_pressure_to_check_when_evidence_dominates` | landed |
| `u_t(c)` (classwise uncertainty) | `UncertaintyEstimate` | `cortex/sre/uncertainty.py` | `test_sre_uncertainty_brake.py::test_uncertainty_estimate_accepts_packet_class_tags_and_rejects_unknown_classes` + `test_sre_uncertainty_brake.py::test_uncertainty_estimate_enforces_bounded_values` | landed |
| `B^{ref} = {quiescent, guarded, latched}` (brake states) | `BrakeState` | `cortex/sre/brake.py` | `test_sre_uncertainty_brake.py::test_brake_state_set_is_exact` | landed |
| `J_t = Brake(...)` (compact brake realization) | `evaluate_brake_state()` | `cortex/sre/brake.py` | `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_quiescent_for_low_uncertainty_without_spikes` + `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_guarded_for_elevated_uncertainty_or_mild_spike_pressure` + `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_latched_for_strong_spike_or_failure_pressure` | landed |
| goal continuity / pending-goal discipline | `GoalContinuityView` | `cortex/sre/goals.py` | `test_sre_goals_branching.py::test_goal_continuity_view_preserves_goal_and_pending_goal_fields` | landed |
| branch operations (open/suspend/resume/merge/abandon) | `BranchOperation` | `cortex/sre/branching.py` | `test_sre_goals_branching.py::test_branch_operation_set_is_exact` | landed |
| host-native opportunity carrier | `HostNativeOpportunity` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` | landed |
| host-native opportunity specialization result | `OpportunitySpecializationResult` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_neutral_family_returns_no_direct_opportunity_specialization` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` + `test_sre_opportunities.py::test_selected_family_remains_distinct_from_direct_opportunity` | landed |
| post-selection host-native opportunity nomination law subordinate to `Q_t^{final}(a)` | `specialize_host_native_opportunity()` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_neutral_family_returns_no_direct_opportunity_specialization` + `test_sre_opportunities.py::test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior` + `test_sre_opportunities.py::test_family_is_retained_when_no_clearly_superior_opportunity_exists` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` + `test_sre_opportunities.py::test_selected_family_remains_distinct_from_direct_opportunity` | landed |
| first bounded operator-route selector as an SRE realization of mode/gating + control allocation over low-dimensional task-state geometry | `OperatorTaskState` + `OperatorRouteDecision` + `select_operator_route()` + `select_operator_route_with_modulators()` + `select_operator_route_with_policy()` + `build_operator_route_diagnostics()` | `cortex/sre/operator_routing.py` | `test_operator_routing.py::test_operator_task_state_requires_bounded_numeric_axes` + `test_operator_routing.py::test_select_operator_route_prefers_default_execute_under_low_pressure` + `test_operator_routing.py::test_select_operator_route_can_choose_guarded_execute_under_higher_pressure` + `test_operator_routing.py::test_select_operator_route_prefers_guarded_continuity_for_resumptive_host_friction` + `test_operator_routing.py::test_select_operator_route_blocks_non_inspect_when_quota_is_high` + `test_operator_routing.py::test_build_operator_route_diagnostics_exposes_state_and_budget` | landed |
| bounded executive summary carrier over observable uncertainty, failure, quota, continuity, novelty, and verification-conflict pressure | `ExecutiveSignalSummaryInputs` + `ExecutiveSignalSummary` + `build_executive_signal_summary()` | `cortex/sre/executive_summary.py` | `test_sre_executive_summary.py::test_executive_signal_summary_inputs_require_bounded_values` + `test_sre_executive_summary.py::test_executive_signal_summary_raises_repeated_failure_pressure_from_observable_failures` | landed |
| compact persistent tonic executive modulator carrier bundle | `ExecutiveModulatorMemory` + `ExecutiveModulatorState` + `ExecutiveModulatorUpdate` | `cortex/sre/modulators.py` | `test_sre_modulators.py::test_modulator_update_clips_values_into_unit_interval` + `test_sre_modulators.py::test_high_quota_pressure_raises_stop_pressure` + `test_sre_modulators.py::test_high_continuity_raises_focus_gain` + `test_sre_modulators.py::test_repeated_failure_raises_explore_gain` + `test_sre_modulators.py::test_high_novelty_raises_update_pressure` + `test_sre_modulators.py::test_modulator_update_uses_persistence_from_previous_memory` | landed |
| bounded SRE tonic modulator update law over executive summary plus prior tonic memory | `update_executive_modulators()` | `cortex/sre/modulators.py` | `test_sre_modulators.py::test_modulator_update_clips_values_into_unit_interval` + `test_sre_modulators.py::test_modulator_stop_pressure_can_block_route` + `test_sre_modulators.py::test_modulator_update_pressure_adds_extra_read_pass` + `test_sre_modulators.py::test_modulator_update_uses_persistence_from_previous_memory` | landed |
| compact executive policy view derived from summary, modulator state, and bounded selection intensity | `ExecutivePolicyView` + `build_executive_policy_view()` | `cortex/sre/policy_view.py` | `test_sre_policy_view.py::test_policy_view_switch_margin_changes_with_focus_and_explore` + `test_sre_policy_view.py::test_policy_view_allows_extra_read_pass_at_explicit_threshold` + `test_sre_policy_view.py::test_policy_view_bounds_numeric_fields` | landed |
| typed unfinished-intention / contradiction / verification / quota closure debt state | `GoalDebtState` + `build_goal_debt_state()` | `cortex/sre/goal_debt.py` | `test_sre_goal_debt.py::test_goal_debt_state_surfaces_explicit_debt_buckets` + `test_sre_goal_debt.py::test_goal_debt_state_requires_brake_type` | landed |
| typed closure-pressure projection preserving compact runtime closure tags | `ClosurePressureState` + `build_closure_pressure_state()` | `cortex/sre/goal_debt.py` | `test_sre_goal_debt.py::test_closure_pressure_state_preserves_compact_runtime_reason_tags` + `test_reference_runtime_step.py::test_reference_runtime_step_emits_feedback_window_summary_for_real_session_mismatch_sequences` | landed |

Forbidden leaks: SRE may not certify commitments, redefine blockedness, lower hard boundaries, or fabricate provenance sufficiency. No hidden same-event certifier internals or host-driver realization doctrine may enter these rows. `neutral_dominance_decision()` may not select a non-neutral family when the allocated-score margin is below that family’s activation threshold. Uncertainty may increase brake or review pressure, but it may not lower commitment certification standards. `ReferenceExecutiveState` must use `UncertaintyEstimate`, `BrakeState`, and `GoalContinuityView` directly rather than shadow carriers. `ReferenceModeAndGatingView` and `ReferenceControlAllocationView` remain the packet-level owners of `x_t^M` and `x_t^K`; the operator-route selector may realize a bounded task-level gate over typed state, but it may not replace runtime executive state, pick named host models, or move policy ownership into Core. Scenario-id keyed task defaults, host-specific probe/baseline/product-path mapping, and evaluation-harness state construction remain tools-side concerns and may not live in `cortex/sre/operator_routing.py`. `ExecutiveSignalSummaryInputs`, `ExecutiveSignalSummary`, `ExecutiveModulatorMemory`, `ExecutiveModulatorState`, `update_executive_modulators()`, and `ExecutivePolicyView` may realize compact executive gain/control law, but they may not introduce decorative neuroscience naming, hidden reward memory, service/auth policy, or packet-level doctrine. `route_budget.max_turns` is an outer harness-turn budget unless explicitly routed into a host transport. `build_reference_executive_state()` may assemble those views from runtime-visible observation, support, environment inputs, and bounded short-window feedback summary, but it may not import certification verdict law, multi-host runtime abstraction, learned weights, or hidden reward state. The short-window carrier may persist only the three most recent runtime-realized outcomes. The summary law may only derive rejection count, override count, latched count, clean-success streak, explicit evidence-move and continuity-improvement counts, family-change-without-evidence counts, goal-progress floor, bounded degradation pressure, sustained spike flags, and explicit bounded feedback-pressure tags; it may not become hidden reward history or a second continuity court. Current-scope shipping and conformance lanes keep `Q_t^{mem}=0.0` unless an explicit AUX-derived support-memory appendix is present; any nonzero memory-conditioned contribution must come only through explicit AUX support-memory publication plus augmentation, and it may not arrive through fake support-memory runtime, prompt heuristics, hidden reward state, softened closure logic, host-specific policy leakage, mediation, or generic reward-learning doctrine. `\chi_t` may scale only the intensity of an already-selected family; it may not fabricate `Q_t^{mem}`, bypass neutral-dominance, or weaken brake law. `build_reference_allocation_scorecard()` and `select_reference_soft_control()` may score and choose within SRE, but they may not bypass neutral-dominance law, smuggle inadmissible families through the family mask, or shift policy ownership into Core. Nested `allocation_diagnostics` may surface allocation truth for runtime projections, but they may not become stronger persisted truth than the accepted continuation/artifact contracts allow. `specialize_host_native_opportunity()` may nominate a preferred native opportunity, but it may not perform channel realization or hide degradation fallback. The operator-route selector may choose route profile, retries, continuity budget, verification behavior, or blockedness for the live operator harness, while the executive summary, tonic modulator memory, goal-debt state, closure-pressure state, and policy view may alter default preference, switching margin, stop pressure, verification intensity, and one extra read pass, but they may not choose named models, change the locked Claude/OpenAI surface contract, or promote local live-routing diagnostics into packet truth.

---

## 4. AUX correspondence

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `S_t^{aux} = Augment^{aux}(S_t, A_t^{aux})` (snapshot augmentation) | `augment_snapshot()` | `cortex/aux/augmentation.py` | `test_aux_scaffolds.py::test_augment_snapshot_requires_explicit_support_snapshot_and_preserves_core_view` + `test_aux_scaffolds.py::test_augment_snapshot_appends_auxiliary_support_without_mutating_core_snapshot_semantics` | landed |
| `C_t^{aux}` (cost-visible burden) | `AuxBurdenReport` | `cortex/aux/cost.py` | `test_aux_scaffolds.py::test_aux_burden_report_enforces_non_negative_values` + `test_aux_scaffolds.py::test_aux_scaffold_types_remain_domain_general_and_removable` | landed |
| `Commit_c(Y_t | A_t^{aux}) = Commit_c(Y_t)` (claim-conservative law) | enforcement test | `tests/integration/test_aux_claim_conservative.py` | `test_aux_claim_conservative.py::test_certified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_blocked_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_uncertified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_aux_objects_remain_support_side_and_do_not_enter_commitment_apis` | landed |
| `GeomEval` evaluation-first geometry/support report over lawful public support state | `AuxGeometryReport` + `AuxMatchScore` + `AuxContradictionCluster` | `cortex/aux/geometry.py` | `test_aux_geometry.py::test_build_aux_geometry_report_derives_only_support_side_hints_and_preserves_snapshot_truth` + `test_aux_geometry.py::test_aux_geometry_types_require_typed_support_refs_and_bounded_scores` | landed |
| evaluation-first geometry derivation over public support snapshot plus explicit support-side evidence | `build_aux_geometry_report()` | `cortex/aux/geometry.py` | `test_aux_geometry.py::test_build_aux_geometry_report_derives_only_support_side_hints_and_preserves_snapshot_truth` + `test_aux_geometry.py::test_build_aux_geometry_report_accepts_explicit_matches_and_contradiction_clusters` | landed |
| deterministic evaluation-first AUX runner over lawful public support state | `AuxEvaluationResult` + `evaluate_aux_support_snapshot()` | `cortex/aux/evaluation.py` | `test_aux_evaluation.py::test_evaluate_aux_support_snapshot_emits_geometry_and_lift_reports_with_quality_improvement` + `test_aux_evaluation.py::test_evaluate_aux_support_snapshot_requires_support_snapshot` | landed |
| time-separated source→target AUX corpus carrier over lawful support snapshots | `AuxTemporalScenario` | `cortex/aux/evaluation.py` | `test_aux_corpus.py::test_aux_temporal_scenarios_require_time_separated_source_and_target` | landed |
| time-separated AUX corpus casewise result over offline publication, augmented target, support priors, geometry, lift, and failure carriage | `AuxCorpusCaseResult` | `cortex/aux/evaluation.py` | `test_aux_corpus.py::test_aux_corpus_case_result_carries_support_priors_and_failure_reasons` | landed |
| time-separated AUX corpus aggregate metric summary over improved/regressed case accounting and fixed-metric coverage | `AuxCorpusMetricSummary` | `cortex/aux/evaluation.py` | `test_aux_corpus.py::test_aux_corpus_metric_summaries_cover_fixed_metrics_and_case_accounting` | landed |
| time-separated AUX corpus result over casewise lift, aggregate metric passes, burden totals, and retention | `AuxCorpusEvaluationResult` | `cortex/aux/evaluation.py` | `test_aux_corpus.py::test_evaluate_aux_support_corpus_reports_time_separated_lift_and_acceptance` | landed |
| time-separated AUX corpus runner over source publication and later target evaluation | `evaluate_aux_support_corpus()` | `cortex/aux/evaluation.py` | `test_aux_corpus.py::test_evaluate_aux_support_corpus_reports_time_separated_lift_and_acceptance` + `test_aux_corpus.py::test_evaluate_aux_support_corpus_can_recommend_prune_candidate_for_weak_cases` + `test_aux_corpus.py::test_evaluate_aux_support_corpus_validates_input_shape` | landed |
| AUX-to-SRE explicit support-memory prior appendix over support-only offline publication plus shadow-only host/tool reliability weighting | `build_support_memory_prior_appendix()` | `cortex/aux/support_priors.py` | `test_aux_support_priors.py::test_build_support_memory_prior_appendix_derives_nonzero_family_priors_from_offline_publication` + `test_aux_support_priors.py::test_build_support_memory_prior_appendix_stays_inactive_without_offline_publication_tag` + `test_aux_support_priors.py::test_build_support_memory_prior_appendix_applies_reliability_weight_to_host_dependent_family_scores` + `test_aux_support_priors.py::test_build_support_memory_prior_appendix_invalidates_reliability_weight_on_fresh_contradiction` + `test_aux_support_priors.py::test_build_support_memory_prior_appendix_zeroes_reliability_weight_when_ttl_expires` | landed |
| reference-only replay scenario over explicit AUX-owned offline publication, later target snapshot, and fixed preferred-family acceptance | `AuxReferenceReplayScenario` | `cortex/aux/reference_replay.py` | `test_aux_reference_replay.py::test_aux_reference_replay_scenarios_require_time_separated_support_snapshots_and_reference_state` | landed |
| reference-only replay case result over merged publication, explicit support priors, baseline vs replay scorecards, and fixed failure labels | `AuxReferenceReplayCaseResult` | `cortex/aux/reference_replay.py` | `test_aux_reference_replay.py::test_aux_reference_replay_case_results_carry_publication_support_priors_and_machine_readable_failures` | landed |
| reference-only replay aggregate result over preferred-family lift, bounded selected-family correction count, stable negative cases, and truthful cut reasons | `AuxReferenceReplayEvaluationResult` | `cortex/aux/reference_replay.py` | `test_aux_reference_replay.py::test_evaluate_aux_reference_q_mem_replay_reports_reference_only_acceptance_and_failure_labels` | landed |
| reference-only replay runner over `OfflineSupportPublication -> augment_snapshot_with_offline_publication() -> build_support_memory_prior_appendix() -> select_reference_soft_control(memory_priors=...)` | `evaluate_aux_reference_q_mem_replay()` | `cortex/aux/reference_replay.py` | `test_aux_reference_replay.py::test_evaluate_aux_reference_q_mem_replay_reports_reference_only_acceptance_and_failure_labels` + `test_aux_reference_replay.py::test_evaluate_aux_reference_q_mem_replay_validates_input_shape` | landed |
| cross-host shadow scenario over explicit AUX-owned offline publication, later target snapshot, canonical host name, and fixed preferred-family acceptance | `AuxCrossHostShadowScenario` | `cortex/aux/cross_host_shadow.py` | `test_aux_cross_host_shadow.py::test_aux_cross_host_shadow_scenarios_require_time_separated_support_snapshots_and_canonical_host_name` | landed |
| cross-host shadow case result over merged publication, explicit support priors, baseline vs replay scorecards, host truth, and fixed failure labels | `AuxCrossHostShadowCaseResult` | `cortex/aux/cross_host_shadow.py` | `test_aux_cross_host_shadow.py::test_aux_cross_host_shadow_case_results_carry_host_truth_and_reversion_flags` | landed |
| cross-host shadow aggregate result over per-host lift counts, stable negative cases, repeat-stable hosts, and truthful cut reasons | `AuxCrossHostShadowEvaluationResult` | `cortex/aux/cross_host_shadow.py` | `test_aux_cross_host_shadow.py::test_evaluate_aux_cross_host_shadow_reports_repeat_stable_host_lift_and_invalidation_truth` | landed |
| cross-host shadow runner over `OfflineSupportPublication -> augment_snapshot_with_offline_publication() -> build_support_memory_prior_appendix() -> select_reference_soft_control(memory_priors=...)` with contradiction-first invalidation and removal reversion checks | `evaluate_aux_cross_host_shadow()` | `cortex/aux/cross_host_shadow.py` | `test_aux_cross_host_shadow.py::test_evaluate_aux_cross_host_shadow_reports_repeat_stable_host_lift_and_invalidation_truth` + `test_aux_cross_host_shadow.py::test_evaluate_aux_cross_host_shadow_validates_input_shape` | landed |
| retention-law lift comparison over fixed support-quality and burden metrics | `AuxLiftReport` + `AuxLiftMetric` + `build_aux_lift_report()` | `cortex/aux/lift.py` | `test_aux_lift.py::test_build_aux_lift_report_keeps_experimental_when_quality_metric_improves` + `test_aux_lift.py::test_build_aux_lift_report_marks_prune_candidate_when_quality_does_not_improve` | landed |
| deterministic support-only offline publication builder over lawful public support state | `build_offline_support_publication()` | `cortex/aux/publication.py` | `test_aux_publication.py::test_build_offline_support_publication_derives_only_support_side_refs_from_snapshot` | landed |
| `W_t^{pub+} = Augment^{aux}(W_t^{pub}, M_t^{offline})` support-only offline publication contract and augmentation-only re-entry | `OfflineSupportPublication` + `augment_snapshot_with_offline_publication()` | `cortex/aux/publication.py` | `test_aux_publication.py::test_offline_support_publication_augments_snapshot_only_through_explicit_aux_appendix` + `test_aux_claim_conservative.py::test_offline_publication_augmentation_is_claim_conservative` | landed |

Forbidden leaks: AUX may not certify commitments, lower hard boundaries, become a second truth court, or learn hidden completion heuristics. `augment_snapshot()` may append or derive auxiliary support, but it may not redefine `SupportSnapshot`. `AuxBurdenReport` remains AUX-only burden rather than generic runtime metrics sprawl. `AuxGeometryReport` and `AuxLiftReport` may consume only lawful public support/executive evidence; they may not become hidden shipping inputs, host-policy adapters, or runtime-required truth. `OfflineSupportPublication` may publish only support-side refs and may re-enter only through explicit augmentation; it may not write into certifier state, blockedness, host capability truth, or default shipping lanes. Every AUX module must be removable without breaking core or SRE.

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
| Deficit state `D_t` | `stop_signals.py` objective_gap_signature | `u_t(c)` uncertainty classes (SRE-owned) | `UncertaintyEstimate` |
| Stop signature `S_t` | `stop_signals.py` stop_attempt_signature | `K_t` commitment candidate | `CommitmentCandidate` |
| Memory `M_t` | persisted session metadata | `W_t` support state | `SupportState` |
| Verdict law `B_t` | `StopVerdict` in `stop_policy.py` | `S_t^{commit}` commitment verdict | `CommitmentVerdict` |
| Transition / residue `R_t` | objective_gap_state, loop_detected | `X_t^{ref}` executive state (SRE-owned) | `ReferenceExecutiveState` |
| Action / control `A_t` | stop_stage, recommend_revert, feedback_mode | `U_t^{sre}` soft-control output | soft-control selection |
| Outward projection `O_t` | runtime-facing payloads, adapter projections | `Y_{t,r}` realized interaction via host-native runtime output projection | `build_reference_cli_record()` for the first accepted reference-host CLI slice |

Key difference: v1 had one stop-centered carrier story. v2 has an ownership-and-correspondence story across Core / SRE / AUX with the same level of rigor applied to a better center.
