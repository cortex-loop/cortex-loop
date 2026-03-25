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
| first bounded last-step realized shell outcome carrier | `ReferenceRealizationFeedback` | `cortex/sre/feedback.py` | `test_reference_realization_feedback.py::test_reference_realization_feedback_preserves_last_step_shell_outcome` + `test_reference_realization_feedback.py::test_reference_realization_feedback_rejects_noncanonical_commitment_kind` | landed |
| first bounded reference short-window realized-outcome carrier | `ReferenceRealizationFeedbackWindow` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_reference_realization_feedback_window_starts_empty` + `test_reference_feedback_window.py::test_reference_realization_feedback_window_keeps_only_three_most_recent_entries` | landed |
| reference-host live runtime session carrier with active-track continuity state, last-step feedback persistence, and bounded feedback-window persistence | `ReferenceRuntimeSession` | `cortex/runtime/reference.py` | `test_reference_runtime_step.py::test_reference_runtime_session_tracks_minimum_live_state` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session` | landed |
| reference-host runtime step result carrier with selected-family truth, realized-family truth, and prior-window feedback summary | `ReferenceRuntimeStepResult` | `cortex/runtime/reference.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates` | landed |
| first bounded runtime control-ledger carrier | `ReferenceControlLedger` | `cortex/runtime/reference.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_admissible_families_by_soft_control_enum` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag` + `test_reference_runtime_step.py::test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning` | landed |
| reference-host runtime step composition over observe/bind, dispatch, commitment carriers, landed executive builder/scorer surfaces, first one-process continuity law, explicit malformed-open rejection, explicit session-mismatch warning, last-step realization-feedback persistence, bounded feedback-window persistence, prior-window feedback summary projection, and bounded latched-brake enforcement | `run_reference_runtime_step()` | `cortex/runtime/reference.py` | `test_reference_runtime_step.py::test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind` + `test_reference_runtime_step.py::test_reference_runtime_step_result_keeps_candidate_bearing_event_candidate_only` + `test_reference_runtime_step.py::test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref` + `test_reference_runtime_step.py::test_reference_runtime_step_rejects_malformed_open_without_mutating_existing_anchor` + `test_reference_runtime_step.py::test_reference_runtime_step_rejects_mismatched_session_id_without_reassigning_shell` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_propagates_prior_enforcement_override_into_next_event_pressure` + `test_reference_runtime_step.py::test_reference_runtime_step_does_not_raise_feedback_pressure_after_clean_success` + `test_reference_runtime_step.py::test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_reports_prior_window_summary_for_repeated_rejection_sequence` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_admissible_families_by_soft_control_enum` + `test_reference_runtime_step.py::test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag` + `test_reference_runtime_step.py::test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates` + `test_reference_runtime_step.py::test_reference_runtime_step_enforces_latched_brake_to_neutral_without_evidence_or_environment` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session` + `test_reference_runtime_continuity.py::test_reference_runtime_cli_rejects_illegal_continuity_transitions_without_mutating_session_truth` | landed |
| `Y_{t,reference}` first accepted developer-facing runtime output projection with top-level control ledger and prior-window feedback summary | `build_reference_cli_record()` | `cortex/runtime/reference_cli.py` | `test_reference_runtime_cli.py::test_reference_runtime_cli_reads_event_file_and_emits_one_record_per_event` + `test_reference_runtime_cli.py::test_reference_runtime_cli_reads_stdin_and_preserves_locked_output_contract` + `test_reference_runtime_cli.py::test_reference_runtime_cli_in_process_surfaces_selected_vs_realized_divergence` + `test_reference_runtime_cli.py::test_reference_runtime_cli_emits_feedback_window_summary_for_real_session_mismatch_sequences` | landed |

Forbidden leaks: the runtime shell may compose existing reference-host, core, and SRE carriers, but it may not expand Core, introduce multi-host abstraction, invent a second continuity model outside the landed branch/goal carriers, or launder provisional neutral selection into a computed executive loop. Cheap-path default must remain intact, commitment result kinds may only surface from the existing certification lattice, illegal continuity transitions may not silently mutate session truth, malformed `open` may not erase suspended anchors, and a non-empty runtime `session_id` may not be silently reassigned once the one-process shell is established. The first bounded realization-feedback carrier may persist only the immediately previous realized shell outcome; it may not become learned reward history, hidden branch state, or a second continuity court. The first bounded short-window carrier may persist only the three most recent runtime-realized outcomes in oldest-to-newest order; it may not widen into aggregate reward history, hidden executive state, or a second continuity court. The first control ledger may serialize only actual runtime truth: event class, admissible families, selected family, realized family, dominant uncertainty sources, brake state, budget band, and primary reason. It may not invent hidden reasoning, policy justifications, or synthetic confidence. The first prior-window summary may reflect only the already-persisted influencing window; it may not report post-step feedback as if it influenced the current event. Latched-brake enforcement may change runtime realization, but it may not move policy ownership into Core, suppress lawful commitment truth, or erase the distinction between selected family and realized family. The first outward projection may serialize landed runtime truth for local CLI use, including a compact executive-state summary, top-level control ledger, one-process continuity state, and a bounded prior-window summary, but it may not invent continuity, commit kinds, or runtime-on executive state that the step kernel did not actually produce. When a full-commitment event carries lawful certification evidence yet the surrounding continuity transition is rejected or latched enforcement overrides runtime realization, the shell must preserve both truths explicitly rather than smoothing either away.

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
| bounded reference short-window feedback summary carrier | `ReferenceFeedbackWindowSummary` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_zero_pressure_for_clean_window` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_repeated_rejection_floor_and_sustained_disruption` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_mixed_rejection_and_override_bonus` | landed |
| bounded short-window realized-outcome summary law | `summarize_reference_feedback_window()` | `cortex/sre/feedback.py` | `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_single_rejection_floor` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_repeated_override_floor` + `test_reference_feedback_window.py::test_summarize_reference_feedback_window_reports_mixed_rejection_and_override_bonus` | landed |
| `X_t^{ref}` first bounded event-to-state realization over runtime observation, support snapshot, executive environment view, and bounded short-window feedback summary | `build_reference_executive_state()` | `cortex/sre/reference_builder.py` | `test_reference_executive_builder.py::test_build_reference_executive_state_for_cheap_event_stays_pass_through_and_low_budget` + `test_reference_executive_builder.py::test_build_reference_executive_state_for_candidate_bearing_event_surfaces_review_mode` + `test_reference_executive_builder.py::test_build_reference_executive_state_for_full_commitment_event_preserves_high_budget_band` + `test_reference_executive_builder.py::test_build_reference_executive_state_surfaces_guarded_brake_when_snapshot_has_degradation` + `test_reference_executive_builder.py::test_build_reference_executive_state_raises_goal_progress_floor_after_session_rejection` + `test_reference_executive_builder.py::test_build_reference_executive_state_marks_prior_enforcement_override` + `test_reference_executive_builder.py::test_build_reference_executive_state_uses_repeated_rejection_window_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_uses_repeated_override_window_pressure` + `test_reference_executive_builder.py::test_build_reference_executive_state_clean_window_does_not_raise_pressure` | landed |
| `A^{ref}` (soft-control family set) | `SoftControlFamily` | `cortex/sre/families.py` | `test_sre_neutral_hinge.py::test_exact_soft_control_family_set_matches_the_packet` | landed |
| `Q_t^{alloc}(a)` (combined allocation score) | `AllocationScore` + `AllocationScorecard` | `cortex/sre/allocation.py` | `test_sre_neutral_hinge.py::test_neutral_dominance_returns_neutral_when_margin_is_below_threshold` + `test_sre_neutral_hinge.py::test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met` | landed |
| `Q_t^{alloc}(a)` first bounded scoring realization over landed executive state | `build_reference_allocation_scorecard()` | `cortex/sre/reference_scoring.py` | `test_reference_runtime_scoring.py::test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold` + `test_reference_runtime_scoring.py::test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked` | landed |
| `Δ_t*(a)` and `θ_t^{act}` (neutral-dominance law) | `neutral_dominance_decision()` | `cortex/sre/policy.py` | `test_sre_neutral_hinge.py::test_neutral_dominance_returns_neutral_when_margin_is_below_threshold` + `test_sre_neutral_hinge.py::test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met` + `test_sre_neutral_hinge.py::test_neutral_path_law_rejects_scorecards_that_omit_neutral` | landed |
| `U_t^{sre}` first bounded soft-control selection over landed executive state | `ReferenceSoftControlSelection` + `select_reference_soft_control()` | `cortex/sre/reference_scoring.py` | `test_reference_runtime_scoring.py::test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_brake_when_guarded_pressure_is_present` + `test_reference_runtime_scoring.py::test_reference_scoring_promotes_branch_under_branch_pressure` + `test_reference_runtime_scoring.py::test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked` | landed |
| `u_t(c)` (classwise uncertainty) | `UncertaintyEstimate` | `cortex/sre/uncertainty.py` | `test_sre_uncertainty_brake.py::test_uncertainty_estimate_accepts_packet_class_tags_and_rejects_unknown_classes` + `test_sre_uncertainty_brake.py::test_uncertainty_estimate_enforces_bounded_values` | landed |
| `B^{ref} = {quiescent, guarded, latched}` (brake states) | `BrakeState` | `cortex/sre/brake.py` | `test_sre_uncertainty_brake.py::test_brake_state_set_is_exact` | landed |
| `J_t = Brake(...)` (compact brake realization) | `evaluate_brake_state()` | `cortex/sre/brake.py` | `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_quiescent_for_low_uncertainty_without_spikes` + `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_guarded_for_elevated_uncertainty_or_mild_spike_pressure` + `test_sre_uncertainty_brake.py::test_brake_evaluation_returns_latched_for_strong_spike_or_failure_pressure` | landed |
| goal continuity / pending-goal discipline | `GoalContinuityView` | `cortex/sre/goals.py` | `test_sre_goals_branching.py::test_goal_continuity_view_preserves_goal_and_pending_goal_fields` | landed |
| branch operations (open/suspend/resume/merge/abandon) | `BranchOperation` | `cortex/sre/branching.py` | `test_sre_goals_branching.py::test_branch_operation_set_is_exact` | landed |
| host-native opportunity carrier | `HostNativeOpportunity` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` | landed |
| host-native opportunity specialization result | `OpportunitySpecializationResult` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_neutral_family_returns_no_direct_opportunity_specialization` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` + `test_sre_opportunities.py::test_selected_family_remains_distinct_from_direct_opportunity` | landed |
| host-native opportunity law / degradation honesty | `specialize_host_native_opportunity()` | `cortex/sre/opportunities.py` | `test_sre_opportunities.py::test_neutral_family_returns_no_direct_opportunity_specialization` + `test_sre_opportunities.py::test_matching_direct_host_native_opportunity_is_nominated_when_clearly_superior` + `test_sre_opportunities.py::test_family_is_retained_when_no_clearly_superior_opportunity_exists` + `test_sre_opportunities.py::test_failed_specialization_surfaces_degradation_reason_and_safer_fallback` + `test_sre_opportunities.py::test_selected_family_remains_distinct_from_direct_opportunity` | landed |

Forbidden leaks: SRE may not certify commitments, redefine blockedness, lower hard boundaries, or fabricate provenance sufficiency. No hidden same-event certifier internals or host-driver realization doctrine may enter these landed rows. `neutral_dominance_decision()` may not select a non-neutral family when the margin is below threshold. Uncertainty may increase brake or review pressure, but it may not lower commitment certification standards. `ReferenceExecutiveState` must use `UncertaintyEstimate`, `BrakeState`, and `GoalContinuityView` directly rather than shadow carriers. `build_reference_executive_state()` may assemble those views from runtime-visible observation, support, environment inputs, and bounded short-window feedback summary, but it may not import certification verdict law, multi-host runtime abstraction, or learned weights. The short-window carrier may persist only the three most recent runtime-realized outcomes. The summary law may only derive rejection count, override count, latched count, clean-success streak, goal-progress floor, bounded degradation pressure, and sustained spike flags; it may not become hidden reward history or a second continuity court. `build_reference_allocation_scorecard()` and `select_reference_soft_control()` may score and choose within SRE, but they may not bypass neutral-dominance law, smuggle inadmissible families through the family mask, or shift policy ownership into Core. Host-native opportunity specialization may nominate a preferred native opportunity, but it may not perform channel realization or hide degradation fallback. Do not pull later goal or branch specializations into these seams.

---

## 4. AUX correspondence

| Packet math | Is | Code home | Test surface | Status |
| --- | --- | --- | --- | --- |
| `S_t^{aux} = Augment^{aux}(S_t, A_t^{aux})` (snapshot augmentation) | `augment_snapshot()` | `cortex/aux/augmentation.py` | `test_aux_scaffolds.py::test_augment_snapshot_requires_explicit_support_snapshot_and_preserves_core_view` + `test_aux_scaffolds.py::test_augment_snapshot_appends_auxiliary_support_without_mutating_core_snapshot_semantics` | landed |
| `C_t^{aux}` (cost-visible burden) | `AuxBurdenReport` | `cortex/aux/cost.py` | `test_aux_scaffolds.py::test_aux_burden_report_enforces_non_negative_values` + `test_aux_scaffolds.py::test_aux_scaffold_types_remain_domain_general_and_removable` | landed |
| `Commit_c(Y_t | A_t^{aux}) = Commit_c(Y_t)` (claim-conservative law) | enforcement test | `tests/integration/test_aux_claim_conservative.py` | `test_aux_claim_conservative.py::test_certified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_blocked_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_uncertified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence` + `test_aux_claim_conservative.py::test_aux_objects_remain_support_side_and_do_not_enter_commitment_apis` | landed |

Forbidden leaks: AUX may not certify commitments, lower hard boundaries, become a second truth court, or learn hidden completion heuristics. `augment_snapshot()` may append or derive auxiliary support, but it may not redefine `SupportSnapshot`. `AuxBurdenReport` remains AUX-only burden rather than generic runtime metrics sprawl. Every AUX module must be removable without breaking core or SRE.

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
