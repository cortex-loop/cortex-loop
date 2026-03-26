# CORTEX_V2_PHASE_GATES_2

Status: active cross-seam gate ledger for Cortex v2 (`active`, workflow authority)
Date: 2026-03-18

Purpose:
- track closure conditions that are broader than one implementation seam,
- separate phase-gate truth from correspondence-row truth,
- and keep historical gate misses explicit instead of silently forgotten.

This ledger does **not** override packet meaning or seam order.
It records whether cross-seam closure conditions are actually earned.

---

## 1. Status vocabulary

- `landed` = the gate row is satisfied with live evidence
- `partial` = some evidence exists, but the row is not honestly closed
- `open` = the row has no sufficient live evidence yet
- `blocked` = the row cannot currently close because an upstream dependency is missing
- `drifted` = the historical repo state already crossed a gate boundary without actually earning it

---

## 2. First-host-vertical gate

Source of truth:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Section 7

Overall status: `landed`

Historical note:
- this gate previously drifted while only placeholder tests existed,
- the missing rows are now closed with real reference-host vertical integration coverage.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| cheap-path integration | `tests/integration/test_reference_host_vertical_gate.py::test_cheap_path_integration_stays_cheap_and_neutral_allowed` | closed | landed | reference-host observe/bind -> dispatch -> neutral continuation stays cheap |
| candidate-bearing integration | `tests/integration/test_reference_host_vertical_gate.py::test_candidate_bearing_integration_binds_candidate_and_returns_no_verdict` | closed | landed | candidate-bearing event binds a candidate and stays out of certification |
| full commitment integration | `tests/integration/test_reference_host_vertical_gate.py::test_full_commitment_integration_reaches_certified_with_lawful_evidence` | closed | landed | reference-host commitment path reaches a real verdict under lawful evidence |
| degradation roundtrip | `tests/integration/test_reference_host_vertical_gate.py::test_degradation_roundtrip_preserves_degradation_and_contradictions` | closed | landed | degradation and contradiction refs survive the commitment path without flattening |
| firewall integration | `tests/integration/test_reference_host_vertical_gate.py::test_firewall_integration_rejects_executive_environment_view` | closed | landed | executive-side environment view is rejected by the certification boundary through the real host path |
| driver-to-core-to-sre smoke | `tests/integration/test_reference_host_vertical_gate.py::test_driver_to_core_to_sre_smoke_stays_observe_bind_dispatch_and_neutral` | closed | landed | driver event -> core dispatch -> SRE neutral decision smoke over landed carriers |

---

## 3. Latency evidence gate

Source of truth:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Section 8

Overall status: `landed`

Evidence location:
- `docs/CORTEX_V2_LATENCY_EVIDENCE_2.md`
- `tests/integration/test_reference_lane_latency.py`

The latency targets are now backed by measured in-process evidence over the landed reference-host/Core/SRE path.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| cheap-path latency evidence | `docs/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0171 ms; p95 0.0184 ms; target met |
| candidate-bearing latency evidence | `docs/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0215 ms; p95 0.0241 ms; target met |
| full commitment latency evidence | `docs/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0257 ms; p95 0.0285 ms; target met |
| neutral SRE scoring latency evidence | `docs/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0014 ms; p95 0.0015 ms; target met |

---

## 4. Proof-packet prerequisite gate

Source of truth:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Phase 13 and Phase 15 intent

Overall status: `landed`

Minimal schemas, the first contradiction-preserving harness, truthful-withheld packet publication logic, and a committed measured reference-lane publication example now exist.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| minimal event trace artifact schema | `cortex/eval/artifacts.py::EventTraceArtifact` + `tests/unit/test_certification_artifacts.py::test_event_trace_artifact_preserves_contradictions_and_degradations` | closed | landed | minimal schema is real |
| minimal current-pair fragment schema | `cortex/eval/artifacts.py::CurrentPairFragment` + `tests/unit/test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | closed | landed | minimal schema is real |
| minimal blocker fragment schema | `cortex/eval/artifacts.py::BlockerFragment` + `tests/unit/test_certification_artifacts.py::test_blocker_fragment_preserves_reason_and_contradictions` | closed | landed | minimal schema is real |
| contradiction-preserving eval harness | `cortex/eval/harness.py::build_evaluation_harness_result` + `tests/unit/test_eval_harness.py::test_harness_result_carries_current_pair_without_losing_refs` + `tests/unit/test_eval_harness.py::test_harness_result_carries_blocker_without_smoothing_blocker_truth` | closed | landed | minimal side-effect-free harness composes landed artifacts without flattening contradictions or degradations |
| truthful-withheld / packet publication logic | `cortex/eval/packets.py::build_evaluation_packet` + `tests/unit/test_eval_packets.py::test_packet_built_from_current_pair_preserves_truth_and_withheld_fields` + `tests/unit/test_eval_packets.py::test_packet_built_from_blocker_preserves_truth_and_withheld_fields` | closed | landed | minimal packet surface preserves current-pair versus blocker truth and exposes withheld fields explicitly |
| measured reference-lane publication example | `docs/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md` + `tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc` | closed | landed | committed reference-host full-commitment example preserves packet kind, withheld fields, contradiction refs, and degradation refs without report formatting |

---

## 5. Closeout law

- Any handoff that claims a phase or sub-phase is `landed` must include `Phase gate check:`.
- Correspondence rows do not silently satisfy phase-gate rows.
- A phase must remain `partial` or `blocked` if its relevant gate rows remain `open`, `partial`, or `drifted`.
- If a historical gate was missed, record the miss here rather than rewriting history.

---

## 6. Post-closeout runtime-program gates

Source of truth:

- `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`

Overall status: `partial`

These rows track the first intentional product/runtime opening after the accepted v2 closeout boundary.
They do not authorize multi-host runtime, runtime AUX activation, offline consolidation, or mediation implementation.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `R1` reference runtime shell | `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first accepted reference-host local CLI shell is landed; cheap-path default and commitment-kind truth are preserved |
| `R2` computed reference executive slice | `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded `X_t^{ref}` builder, `U_t^{sre}` scoring/selection layer, and runtime-shell integration are landed on the reference-host CLI shell |
| `R3` reference live continuity slice | `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/integration/test_reference_runtime_continuity.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first one-process live continuity law and explicit rejection enforcement are re-hardened and audit-clean for current scope; malformed `open` and session mismatch are explicit, pending-goal anchors are preserved, and broader multi-agent runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `R4` reference closed-loop feedback and latched-brake slice | `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`; `tests/unit/test_reference_realization_feedback.py`; `tests/unit/test_reference_runtime_step.py`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded last-step realization feedback, feedback-conditioned builder update, top-level control ledger, and latched-brake enforcement are landed and audit-clean for current scope; committed end-to-end proof now covers feedback propagation, deterministic control-ledger ordering, and CLI-visible selected-vs-realized divergence, and a zero-finding adversarial runtime/API review found no defect; selected-family truth and realized-family truth remain distinct, lawful commitment truth may coexist with enforcement warnings, and broader multi-agent runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `R5` reference short-window feedback and sustained-pressure slice | `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`; `tests/unit/test_reference_feedback_window.py`; `tests/unit/test_reference_runtime_step.py`; `tests/unit/test_reference_executive_builder.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded three-step realized-outcome window, bounded prior-window summary law, runtime-step summary projection, top-level CLI `feedback_window_summary`, and post-step `session_summary.feedback_window_size` are landed and audit-clean for current scope again; the corrective line now closes the surviving session/window carrier defect by normalizing lawful one-sided last/window state, rejecting divergent two-sided state, and preserving prior-pressure truth through direct-construction paths, while `R4` last-step behavior remains a strict subset, scorer law remains unchanged, and broader runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `C1` reference bounded cross-process continuation slice | `docs/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`; `tests/unit/test_reference_runtime_session_io.py`; `tests/integration/test_reference_runtime_cli.py`; `tests/integration/test_reference_runtime_continuity.py` | closed | landed | explicit persisted `continuity_truth` plus bounded `control_residue` are landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; CLI load/save is explicit, split-run equivalence is proven against the recorded `C1` contract, targeted unit/integration reruns plus repeated `make revalidate-reference-runtime-continuity` passed, and shell-long `budget_history` / `brake_history` remain public one-process diagnostics rather than cross-process truth |
| `O1` OpenAI documented host-event runtime shell | `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`; `tests/unit/test_openai_runtime_session_io.py`; `tests/unit/test_openai_runtime_step.py`; `tests/unit/test_openai_runtime_ownership.py`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_runtime_continuity.py` | closed | landed | OpenAI-specific runtime/session carriers plus persisted artifact are landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; raw documented host events drive a host-specific CLI shell, canonical Cortex event names are explicitly rejected, undocumented host events remain explicit conservative warnings, OpenAI runtime/session ownership is self-contained, split-run OpenAI equivalence is proven against the recorded `O1` contract with explicit diagnostic-history non-equivalence, and targeted unit/integration reruns plus repeated `make revalidate-openai-runtime` passed |
| `O2` OpenAI raw-transcript ingress shell | `docs/CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md`; `tests/unit/test_openai_ingress.py`; `tests/integration/test_openai_ingress_cli.py`; `tests/integration/test_openai_ingress_continuity.py` | closed | landed | raw-transcript ingress parsing is landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; transcript records with `type` drive the current-line `O1` shell, wrapper-shaped and mixed wrapper/transcript records are explicitly rejected, canonical Cortex event names are explicitly rejected at ingress, split-run ingress continuity is proven against the recorded `O2` contract, and repeated direct reruns plus repeated `make revalidate-openai-ingress` passed |
| `O3` OpenAI loopback service shell | `docs/CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md`; `tests/unit/test_openai_service.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_service_continuity.py` | closed | landed | loopback-only HTTP is landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; `POST /v1/events` drives the current-line `O2` parser and current-line `O1` runtime shell, `GET /v1/session/export` and `POST /v1/session/import` move the current-line OpenAI runtime artifact as JSON, one active session per process is real for current scope, and repeated direct reruns plus repeated `make revalidate-openai-service` passed |
| `O4` OpenAI bounded outbound host-control lane | `docs/CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0.md`; `tests/unit/test_openai_host_control.py`; `tests/integration/test_openai_host_control_service.py`; `tests/integration/test_openai_host_control_continuity.py` | local branch closeout pending acceptance | partial | the first bounded outbound OpenAI host-control lane is real on branch-local K2 candidate truth over accepted K1 baseline `79b8f39`; `POST /v1/actions/response-stream` is text-only and strict-whitelist for current scope, returned host events re-enter the current-line `O2` parser and current-line `O1` runtime shell directly, the stdlib transport has an internal fixture mode so the canonical bundle requires no live network, and tools, cancel/update lanes, remote hosting, and generic control doctrine remain unopened |
