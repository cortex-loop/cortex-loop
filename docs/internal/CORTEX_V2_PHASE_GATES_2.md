# CORTEX_V2_PHASE_GATES_2

Surface: internal

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
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Section 7

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
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Section 8

Overall status: `landed`

Evidence location:
- `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md`
- `tests/integration/test_reference_lane_latency.py`

The latency targets are now backed by measured in-process evidence over the landed reference-host/Core/SRE path.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| cheap-path latency evidence | `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0171 ms; p95 0.0184 ms; target met |
| candidate-bearing latency evidence | `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0215 ms; p95 0.0241 ms; target met |
| full commitment latency evidence | `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0257 ms; p95 0.0285 ms; target met |
| neutral SRE scoring latency evidence | `docs/lab/CORTEX_V2_LATENCY_EVIDENCE_2.md` + `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced` | closed | landed | measured median 0.0014 ms; p95 0.0015 ms; target met |

---

## 4. Proof-packet prerequisite gate

Source of truth:
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Phase 13 and Phase 15 intent

Overall status: `landed`

Minimal schemas, the first contradiction-preserving harness, truthful-withheld packet publication logic, and a committed measured reference-lane publication example now exist.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| minimal event trace artifact schema | `cortex/eval/artifacts.py::EventTraceArtifact` + `tests/unit/test_certification_artifacts.py::test_event_trace_artifact_preserves_contradictions_and_degradations` | closed | landed | minimal schema is real |
| minimal current-pair fragment schema | `cortex/eval/artifacts.py::CurrentPairFragment` + `tests/unit/test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | closed | landed | minimal schema is real |
| minimal blocker fragment schema | `cortex/eval/artifacts.py::BlockerFragment` + `tests/unit/test_certification_artifacts.py::test_blocker_fragment_preserves_reason_and_contradictions` | closed | landed | minimal schema is real |
| contradiction-preserving eval harness | `cortex/eval/harness.py::build_evaluation_harness_result` + `tests/unit/test_eval_harness.py::test_harness_result_carries_current_pair_without_losing_refs` + `tests/unit/test_eval_harness.py::test_harness_result_carries_blocker_without_smoothing_blocker_truth` | closed | landed | minimal side-effect-free harness composes landed artifacts without flattening contradictions or degradations |
| truthful-withheld / packet publication logic | `cortex/eval/packets.py::build_evaluation_packet` + `tests/unit/test_eval_packets.py::test_packet_built_from_current_pair_preserves_truth_and_withheld_fields` + `tests/unit/test_eval_packets.py::test_packet_built_from_blocker_preserves_truth_and_withheld_fields` | closed | landed | minimal packet surface preserves current-pair versus blocker truth and exposes withheld fields explicitly |
| measured reference-lane publication example | `docs/experimental/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md` + `tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc` | closed | landed | committed reference-host full-commitment example preserves packet kind, withheld fields, contradiction refs, and degradation refs without report formatting |

---

## 5. Closeout law

- Any handoff that claims a phase or sub-phase is `landed` must include `Phase gate check:`.
- Correspondence rows do not silently satisfy phase-gate rows.
- A phase must remain `partial` or `blocked` if its relevant gate rows remain `open`, `partial`, or `drifted`.
- If a historical gate was missed, record the miss here rather than rewriting history.

---

## 6. Post-closeout runtime-program gates

Source of truth:

- `docs/experimental/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`

Overall status: `landed`

These rows track the first intentional product/runtime opening after the accepted v2 closeout boundary.
They do not authorize multi-host runtime, runtime AUX activation, offline consolidation, or mediation implementation.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `R1` reference runtime shell | `docs/experimental/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first accepted reference-host local CLI shell is landed; cheap-path default and commitment-kind truth are preserved |
| `R2` computed reference executive slice | `docs/experimental/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded `X_t^{ref}` builder, `U_t^{sre}` scoring/selection layer, and runtime-shell integration are landed on the reference-host CLI shell |
| `R3` reference live continuity slice | `docs/experimental/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`; `tests/integration/test_reference_runtime_continuity.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first one-process live continuity law and explicit rejection enforcement are re-hardened and audit-clean for current scope; malformed `open` and session mismatch are explicit, pending-goal anchors are preserved, and broader multi-agent runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `R4` reference closed-loop feedback and latched-brake slice | `docs/experimental/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`; `tests/unit/test_reference_realization_feedback.py`; `tests/unit/test_reference_runtime_step.py`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded last-step realization feedback, feedback-conditioned builder update, top-level control ledger, and latched-brake enforcement are landed and audit-clean for current scope; committed end-to-end proof now covers feedback propagation, deterministic control-ledger ordering, and CLI-visible selected-vs-realized divergence, and a zero-finding adversarial runtime/API review found no defect; selected-family truth and realized-family truth remain distinct, lawful commitment truth may coexist with enforcement warnings, and broader multi-agent runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `R5` reference short-window feedback and sustained-pressure slice | `docs/experimental/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`; `tests/unit/test_reference_feedback_window.py`; `tests/unit/test_reference_runtime_step.py`; `tests/unit/test_reference_executive_builder.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the first bounded three-step realized-outcome window, bounded prior-window summary law, runtime-step summary projection, top-level CLI `feedback_window_summary`, and post-step `session_summary.feedback_window_size` are landed and audit-clean for current scope again; the corrective line now closes the surviving session/window carrier defect by normalizing lawful one-sided last/window state, rejecting divergent two-sided state, and preserving prior-pressure truth through direct-construction paths, while `R4` last-step behavior remains a strict subset, scorer law remains unchanged, and broader runtime, runtime AUX activation, offline consolidation, and mediation remain unopened |
| `C1` reference bounded cross-process continuation slice | `docs/experimental/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`; `tests/unit/test_reference_runtime_session_io.py`; `tests/integration/test_reference_runtime_cli.py`; `tests/integration/test_reference_runtime_continuity.py` | closed | landed | explicit persisted `continuity_truth` plus bounded `control_residue` are landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; CLI load/save is explicit, split-run equivalence is proven against the recorded `C1` contract, targeted unit/integration reruns plus repeated `make revalidate-reference-runtime-continuity` passed, and shell-long `budget_history` / `brake_history` remain public one-process diagnostics rather than cross-process truth |
| `O1` OpenAI documented host-event runtime shell | `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`; `tests/unit/test_openai_runtime_session_io.py`; `tests/unit/test_openai_runtime_step.py`; `tests/unit/test_openai_runtime_ownership.py`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_runtime_continuity.py` | closed | landed | on the current review line, raw documented host events still drive the compressed OpenAI-only product shell: the persisted artifact remains `openai_product_journal` v1 only, the outward record remains exact `decision + journal`, verified-work sessions may now carry optional `preservation_state` inside that same journal, canonical Cortex event names remain explicitly rejected, undocumented host events remain explicit conservative warnings, the OpenAI path still does not transit reference-soft-control selection or allocation diagnostics, and targeted unit/integration reruns remain green |
| `O2` OpenAI raw-transcript ingress shell | `docs/CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md`; `tests/unit/test_openai_ingress.py`; `tests/integration/test_openai_ingress_cli.py`; `tests/integration/test_openai_ingress_continuity.py` | closed | landed | raw-transcript ingress parsing is landed on the accepted K1 closeout line, implemented at K1 proof head `d4c311f` and cleanly closed at deterministic closeout head `79b8f39`; transcript records with `type` drive the current-line `O1` shell, wrapper-shaped and mixed wrapper/transcript records are explicitly rejected, canonical Cortex event names are explicitly rejected at ingress, split-run ingress continuity is proven against the recorded `O2` contract, and repeated direct reruns plus repeated `make revalidate-openai-ingress` passed |
| `O3` OpenAI loopback service shell | `docs/CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md`; `tests/unit/test_openai_service.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_service_continuity.py` | closed | landed | on the current review line, loopback-only HTTP remains real while `POST /v1/events` returns the compact current-line `O1` `decision + journal` record, `GET /v1/session/export` and `POST /v1/session/import` still move only `openai_product_journal` v1, verified-work sessions may now include optional `preservation_state` in that same journal, one active session per process remains real for current scope, and repeated direct reruns plus repeated `make revalidate-openai-service` remain the closure truth |
| `O4` OpenAI bounded outbound host-control lane | `docs/CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0.md`; `make revalidate-openai-host-control` | closed | landed | on the current review line, `POST /v1/actions/response-stream` remains thin and text-only by default when no `work_contract` is present, returned host events still re-enter the current-line `O2` parser and compressed `O1` runtime shell directly, ordered result records preserve the exact compact `decision + journal` projection, export/import continuity keeps `openai_product_journal` v1 only, and the separately scoped verified-work lane still does not retroactively widen the landed thin-path contract |
| `O4R` OpenAI verified-work restoration lane | `docs/CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0.md`; `make revalidate-openai-host-control`; `make -C lab revalidate-openai-operator-cli`; repeated `python3 lab/cortex_conformance.py --mode active --brain openai`; `.cortex/train_loops/verified-work-breadth-openai/summary.json`; `.cortex/train_loops/verified-work-repair-yield-openai/summary.json` | closed | landed | on the current review line, the shared verified-work law now includes a minimal preservation-state machine over task anchor, trusted structure, falsified structure, lawful repair surface, and intervention budget; runtime-native verification now persists optional preservation state inside the compact OpenAI journal on verified-work sessions only; the OpenAI verified-work path now derives the next move from that state, records a deterministic verified-work task anchor when no active goal exists, narrows the repair contract to the lawful repair surface, and verifies the second attempt on top of the preserved first-attempt file map; the thin `O4` path remains unchanged, the deterministic `full_files` verifier/profile registry and one bounded repair turn remain intact, the accepted product/runtime proof remains the historical OpenAI `service_api` line, and E24 now records OpenAI `operator_cli` as the active proving-default lane for new conformance and train-loop iteration without repurposing the historical `CT2` anchor |
| `R6` explicit executive allocation slice on the reference runtime shell | `docs/lab/CORTEX_V2_EXECUTIVE_LIVE_OUTCOME_PROGRAM_0.md`; `tests/unit/test_sre_neutral_hinge.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | explicit `online_score`, `memory_score`, `allocated_score`, `alpha_t`, and nested `control_ledger.allocation_diagnostics` are landed on the accepted K3 closeout line, implemented at K3 proof head `5087d36` and cleanly closed at deterministic closeout head `efe003e`; current scope keeps `Q_t^{mem}=0.0`, `alpha_t=1.0`, and `allocated_score=online_score`, and repeated direct reruns plus repeated `make revalidate-executive-loop` passed |
| `O5` OpenAI executive allocation projection slice | `docs/lab/CORTEX_V2_EXECUTIVE_LIVE_OUTCOME_PROGRAM_0.md`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_ingress_cli.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_host_control_service.py`; `tests/integration/test_openai_host_control_continuity.py` | closed | landed | landed historical/reference evidence only after X1: the older OpenAI runtime, ingress, O3 service, and K2 host-control projections did surface nested `control_ledger.allocation_diagnostics`, but that payload is no longer part of the accepted OpenAI-only product runtime after X1 |
| `R7` reference computed executive loop | `docs/internal/CORTEX_V2_COMPUTED_EXECUTIVE_LOOP_PROGRAM_0.md`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | the reference lane now runs on a bounded computed allocation loop rather than diagnostics-first freeze alone: `alpha_t` is computed from runtime-visible pressure, `Q_t^{mem}=0.0` remains fixed, `allocated_score` can differ from `online_score`, selection runs on allocated-score semantics, and the public reference runtime projection keeps the same top-level shape while surfacing the stronger nested `allocation_diagnostics` law |
| `O6` OpenAI computed executive loop projection slice | `docs/internal/CORTEX_V2_COMPUTED_EXECUTIVE_LOOP_PROGRAM_0.md`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_ingress_cli.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_host_control_service.py`; `tests/integration/test_openai_host_control_continuity.py` | closed | landed | landed historical/reference evidence only after X1: the older OpenAI runtime, ingress, service, and host-control projections did surface the bounded computed allocation law coherently, but `allocation_diagnostics` is no longer part of the accepted OpenAI-only product runtime |
| `R8` reference feedback-conditioned intervention threshold | `docs/internal/CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0.md`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py`; `tests/integration/test_reference_runtime_continuity.py` | closed | landed | the reference lane now uses a bounded feedback-conditioned `activation_threshold` rather than budget-band baseline alone: current visible pressure and bounded prior-feedback pressure can tighten intervention conservatively, `Q_t^{mem}=0.0` remains fixed, `alpha_t` law remains the accepted K4 law, and no public shell shape changed |
| `O7` OpenAI feedback-conditioned threshold projection slice | `docs/internal/CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0.md`; `tests/unit/test_openai_runtime_step.py`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_runtime_continuity.py`; `tests/integration/test_openai_ingress_cli.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_host_control_service.py`; `tests/integration/test_openai_host_control_continuity.py` | closed | landed | landed historical/reference evidence only after X1: the older OpenAI runtime, ingress, service, and host-control projections did surface the bounded feedback-conditioned threshold coherently, but that threshold projection is no longer part of the accepted OpenAI-only product runtime |
| `R9` reference enforcement-aware realized control loop | `docs/internal/CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0.md`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py`; `tests/integration/test_reference_runtime_continuity.py` | closed | landed | the reference runtime shell now closes a bounded enforcement-aware realized control loop: guarded-feedback and latched-brake enforcement may conservatively realize `check` or `neutral`, but selected-family truth, realized-family truth, lawful commitment truth, and enforcement warnings remain explicit and audit-clean for current scope |
| `O8` OpenAI enforcement-aware realized projection slice | `docs/internal/CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0.md`; `tests/unit/test_openai_runtime_step.py`; `tests/integration/test_openai_runtime_cli.py`; `tests/integration/test_openai_runtime_continuity.py`; `tests/integration/test_openai_service.py`; `tests/integration/test_openai_host_control_continuity.py` | closed | landed | landed historical/reference evidence only after X1: the older OpenAI runtime, ingress, service, and host-control projections did preserve the stronger bounded enforcement-aware realization law coherently, but that realized-control story is no longer part of the accepted OpenAI-only product runtime |
| `G1` Gemini documented host-event runtime shell | `docs/experimental/CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md`; `tests/unit/test_gemini_runtime_session_io.py`; `tests/unit/test_gemini_runtime_step.py`; `tests/unit/test_gemini_runtime_ownership.py`; `tests/integration/test_gemini_runtime_cli.py`; `tests/integration/test_gemini_runtime_continuity.py` | closed | landed | Gemini-specific runtime/session carriers plus persisted artifact are landed on the accepted G1 closeout line, implemented at G1 proof head `fe33a7e`; raw documented Gemini host events drive a host-specific CLI shell, canonical Cortex event names are explicitly rejected, nested allocation diagnostics reuse accepted K3 truth without opening a second SRE doctrine, and repeated direct reruns plus repeated `make revalidate-gemini-runtime` passed |
| `G2` Gemini raw-transcript ingress shell | `docs/experimental/CORTEX_V2_GEMINI_INGRESS_PROGRAM_0.md`; `tests/unit/test_gemini_ingress.py`; `tests/integration/test_gemini_ingress_cli.py`; `tests/integration/test_gemini_ingress_continuity.py` | closed | landed | Gemini raw-transcript ingress parsing is landed on the accepted G1 closeout line; transcript records with `type` drive the current-line Gemini runtime shell, wrapper-shaped and mixed wrapper/transcript records are explicitly rejected, split-run ingress continuity is proven for current scope, and repeated direct reruns plus repeated `make revalidate-gemini-ingress` passed |
| `G3` Gemini loopback service shell | `docs/experimental/CORTEX_V2_GEMINI_SERVICE_PROGRAM_0.md`; `tests/unit/test_gemini_service.py`; `tests/integration/test_gemini_service_http.py`; `tests/integration/test_gemini_service_continuity.py` | closed | landed | loopback-only Gemini HTTP is landed on the accepted G1 closeout line; `POST /v1/events` drives the current-line Gemini ingress parser and Gemini runtime shell, artifact import/export remains JSON-only, one active session per process is real for current scope, and repeated direct reruns plus repeated `make revalidate-gemini-service` passed |
| `G4` Gemini bounded outbound host-control lane | `docs/experimental/CORTEX_V2_GEMINI_HOST_CONTROL_PROGRAM_0.md`; `tests/unit/test_gemini_host_control.py`; `tests/integration/test_gemini_host_control_service.py`; `tests/integration/test_gemini_host_control_continuity.py` | closed | landed | the first bounded outbound Gemini host-control lane is landed on the accepted G1 closeout line, implemented at G1 proof head `fe33a7e`; `POST /v1/actions/interaction-stream` is text-only and strict-whitelist for current scope, returned host events re-enter the current-line Gemini ingress parser and Gemini runtime shell directly, the stdlib transport has an internal fixture mode so the canonical bundle requires no live network, and repeated direct reruns plus repeated `make revalidate-gemini-host-control` passed |
| `A1` Claude documented host-event runtime shell | `docs/experimental/CORTEX_V2_CLAUDE_RUNTIME_PROGRAM_0.md`; `tests/unit/test_claude_runtime_session_io.py`; `tests/unit/test_claude_runtime_step.py`; `tests/unit/test_claude_runtime_ownership.py`; `tests/integration/test_claude_runtime_cli.py`; `tests/integration/test_claude_runtime_continuity.py` | closed | landed | Claude-specific runtime/session carriers plus persisted artifact are landed on the accepted G1 closeout line, implemented at G1 proof head `fe33a7e`; raw documented Claude host events drive a host-specific CLI shell, canonical Cortex event names are explicitly rejected, top-level `message_id` remains visible in the outward record projection, nested allocation diagnostics reuse accepted K3 truth without opening a second SRE doctrine, and repeated direct reruns plus repeated `make revalidate-claude-runtime` passed |
| `A2` Claude raw-transcript ingress shell | `docs/experimental/CORTEX_V2_CLAUDE_INGRESS_PROGRAM_0.md`; `tests/unit/test_claude_ingress.py`; `tests/integration/test_claude_ingress_cli.py`; `tests/integration/test_claude_ingress_continuity.py` | closed | landed | Claude raw-transcript ingress parsing is landed on the accepted G1 closeout line; transcript records with `type` drive the current-line Claude runtime shell, wrapper-shaped and mixed wrapper/transcript records are explicitly rejected, `ping` and `error` remain transport-only rather than lawful ingress records, split-run ingress continuity is proven for current scope, and repeated direct reruns plus repeated `make revalidate-claude-ingress` passed |
| `A3` Claude loopback service shell | `docs/experimental/CORTEX_V2_CLAUDE_SERVICE_PROGRAM_0.md`; `tests/unit/test_claude_service.py`; `tests/integration/test_claude_service_http.py`; `tests/integration/test_claude_service_continuity.py` | closed | landed | loopback-only Claude HTTP is landed on the accepted G1 closeout line; `POST /v1/events` drives the current-line Claude ingress parser and Claude runtime shell, artifact import/export remains JSON-only, one active session per process is real for current scope, and repeated direct reruns plus repeated `make revalidate-claude-service` passed |
| `A4` Claude bounded outbound host-control lane | `docs/experimental/CORTEX_V2_CLAUDE_HOST_CONTROL_PROGRAM_0.md`; `tests/unit/test_claude_host_control.py`; `tests/integration/test_claude_host_control_service.py`; `tests/integration/test_claude_host_control_continuity.py` | closed | landed | the first bounded outbound Claude host-control lane is landed on the accepted G1 closeout line, implemented at G1 proof head `fe33a7e`; `POST /v1/actions/message-stream` is text-only and strict-whitelist for current scope, returned host events re-enter the current-line Claude ingress parser and Claude runtime shell directly, the stdlib transport has an internal fixture mode so the canonical bundle requires no live network, and repeated direct reruns plus repeated `make revalidate-claude-host-control` passed |

---

## 7. Live-validation gates

Source of truth:

- `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`
- `docs/lab/CORTEX_V2_LIVE_VALIDATION_SCENARIO_CATALOG_0.md`
- `docs/lab/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`

Overall status: `landed` for the accepted OpenAI-only product scope

These rows track the two-lane live-validation contract after the R1 reset.
They do not authorize runtime widening, CLI-backed transport substitution, tool-use expansion, or packet reinterpretation.
Shipping truth may remain OpenAI-only without blocking the current product claim, but later Cortex-law seams still require explicit OpenAI, Claude, and Gemini conformance status on their strongest available native surfaces.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `L1` Claude live validation | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-preflight`; `make live-provider-baselines`; focused Claude operator reruns; `python3 lab/live_cortex_host_control.py --lane automation --provider claude --suite canonical_anchor` | conformance-required on the strongest native Claude surface; reopen Claude direct-API shipping truth only in a later explicit Claude shipping train on a capable machine | blocked | Claude currently contributes positive watchlist evidence on the headless-CLI lane, the shared `canonical_anchor` direct-API suite remains implemented for Claude future host-expansion plumbing, and canonical service truth remains blocked on missing `ANTHROPIC_API_KEY`; this does not block the accepted OpenAI-only shipping scope |
| `L1A` Claude hook-backed operator lifecycle proof | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0.md`; focused Claude operator reruns | closed | landed | the documented Claude hook surface remains re-earned as watchlist-only lifecycle evidence: `SessionStart`, `PreToolUse`, `PostToolUse`, and `SessionEnd` are recorded on the signed-in operator lane, and the bounded shared coding harness closes on `pass_minimal`, `truth_gap`, and `restart_continuity` |
| `L2` Gemini live validation | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-preflight`; `make live-provider-baselines`; focused Gemini operator reruns; `make live-cortex-host-control` | conformance-required on the strongest native Gemini surface; reopen Gemini direct-API shipping truth only in a later explicit Gemini shipping train | blocked | Gemini remains the noisiest headless-CLI watchlist line, current local reruns may drift from the accepted watchlist baseline, and Gemini remains outside the accepted OpenAI-only shipping scope until a later shipping train deliberately opens its service lane |
| `L2A` Gemini hook-backed operator lifecycle proof | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0.md`; focused Gemini operator reruns | keep partial unless the accepted watchlist line is re-earned cleanly | partial | the documented Gemini hook surface is still only partially re-earned as watchlist evidence: `SessionStart`, `BeforeTool`, `AfterTool`, and `SessionEnd` are captured, but the accepted line remains unresolved rather than cleanly landed |
| `L3` OpenAI live validation | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-preflight`; `python3 lab/live_cortex_host_control.py --lane automation --provider openai --suite current`; `python3 lab/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor`; `make live-compare` | closed | landed | OpenAI direct-API canonical truth is repeat-stably re-earned for current scope on this machine; exact cycle count remains local-artifact truth under `.cortex/live_validation/automation/openai/service/service_runs.json`, the active current-line proof bundle is now intentionally compact around preflight, direct OpenAI host-control reruns, `make live-compare`, and deterministic support checks, the accepted OpenAI-only product runtime still uses the compact `openai_product_journal` carrier plus the exact outward `decision + journal` projection, and retained App Server or cross-host watchlist tools remain diagnostics only |
| `L3A` OpenAI App Server operator lifecycle proof | `docs/lab/CORTEX_V2_LIVE_VALIDATION_PROGRAM_0.md`; `docs/lab/CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0.md`; `make live-openai-app-server` | closed | landed | the bounded `codex app-server` operator lane remains re-earned as watchlist-only lifecycle evidence: repeated `pass_minimal` and repeated `restart_continuity` succeed, `truth_gap` remains truthful, and `codex exec` is preserved as the smoke lane |
| `L4` lifecycle-first payoff verdict | `docs/lab/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`; `make live-compare` | closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens | landed | after the R1 reset, the later OpenAI-only scope narrowing seam, and accepted X1 runtime compression, lifecycle-first payoff is read from the canonical direct-API lane first and is repeat-stably re-earned for the accepted current scope on OpenAI; exact cycle count remains local-artifact truth, the compact OpenAI product carrier is now the accepted runtime truth, and Claude/Gemini remain conformance-required rather than shipping-default |
| `L5` cross-host operator payoff audit | `docs/lab/CORTEX_V2_LIVE_OPERATOR_PAYOFF_AUDIT_0.md`; `make live-compare`; `make live-operator-payoff-audit` | historical/watchlist-only; do not use for runtime closure | landed | retained only as a secondary watchlist diagnostic after the R1 reset; it is explicitly outside the active OpenAI-only current-line proof bundle and no longer carries runtime-payoff closure truth |
| `L6A` Claude service live proof | `docs/lab/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`; `make live-preflight`; `python3 lab/live_cortex_host_control.py --lane automation --provider claude --suite canonical_anchor`; `make live-compare` | service proof remains blocked until a later explicit Claude shipping train opens on a capable machine | blocked | the current machine remains out of scope for actual Claude service proof because machine auth readiness is not yet satisfied; the shared `canonical_anchor` direct-API suite is implemented for Claude future host-expansion plumbing, but signed-in Claude CLI truth still does not count as service-lane auth and the row is non-blocking to the accepted OpenAI-only shipping scope |
| `L6B` Gemini service live proof | `docs/lab/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`; `make live-preflight`; `python3 lab/live_cortex_host_control.py --lane automation --provider gemini`; `make live-compare` | service proof remains blocked until a later explicit Gemini shipping train opens on a capable machine | blocked | the current machine remains out of scope for actual Gemini service proof because machine auth readiness is not yet satisfied; signed-in Gemini CLI truth still does not count as service-lane auth, and the row is non-blocking to the accepted OpenAI-only shipping scope |
| `L6C` OpenAI service live proof | `docs/lab/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`; `make live-preflight`; `python3 lab/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor`; `make live-compare` | closed | landed | the current machine now satisfies the bounded OpenAI service-proof contract: auth readiness is `ready`, spend approval is explicit, the first current-scope direct-API truth anchor is repeat-stably re-earned on the `canonical_anchor` suite without relying on CLI fallback, exact cycle count remains local-artifact truth, the active service-proof bundle is intentionally compact around preflight, direct OpenAI host-control reruns, `make live-compare`, and deterministic support checks, and the accepted OpenAI-only product runtime still uses the compact `openai_product_journal` carrier plus exact outward `decision + journal` projection |
| `L6D` package-level service proof | `docs/lab/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`; `make live-compare` | closed for the accepted OpenAI-only product scope; reopen only if product scope intentionally widens | landed | package-level service proof is now earned for the accepted OpenAI-only product scope because `L6C` lands repeat-stably on the canonical direct-API lane and X1 keeps that truth on the compact product carrier; Claude and Gemini remain outside shipping truth but no longer disappear behind generic backlog wording for later Cortex-law work |

---

## 7A. Cortex-law conformance gates

Source of truth:

- `AGENTS.md`
- `docs/internal/CORTEX_V2_ACTIVE_WORKSTREAM.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `lab/cortex_conformance.py`

Overall status: `landed`

These rows track development conformance for Cortex-law changes.
They do not widen shipping truth or canonical runtime proof by themselves.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `CT1` conformance harness readiness | `AGENTS.md`; `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`; `lab/cortex_conformance.py`; `lab/cortex_train_loop.py`; `tests/unit/test_cortex_conformance.py`; `tests/unit/test_cortex_train_loop.py` | closed | landed | Cortex-law trains now require explicit truth taxonomy, expanded `Train Charter` fields, locked baseline / metric / rollback / escalation inputs, strongest-native-surface selection, one reusable tri-brain conformance harness, and one thin maintainer-only loop recorder over existing proof entrypoints |
| `CT2` active verified-work tri-brain conformance | `docs/internal/CORTEX_V2_ACTIVE_WORKSTREAM.md`; `make conformance-preflight`; `make conformance-fast`; `make -C lab revalidate-openai-operator-cli`; `python3 lab/cortex_conformance.py --mode reconcile-latest`; local artifacts under `.cortex/live_validation/conformance/` | closed on local `main` for the historical bookmarks anchor pack; recheck only if a later runtime/product seam changes the anchor pack, the unchanged non-shipping operator surfaces, or the conformance publication law | landed | the corrected active bookmarks verified-work pack historically reads OpenAI `service_api` conformant on three repeated targeted reruns because bounded read-only workspace context closed the old shipping-default gap, `summary.latest` still publishes only from full tri-brain runs for the bookmarks anchor pack, and the clean full rerun under `.cortex/live_validation/conformance/run_20260408T074128+0000` re-earned the historical tri-brain reading with OpenAI `service_api` conformant, Claude `operator_cli` conformant after one lawful repair, and Gemini `operator_cli` conformant; E24 now splits `product_runtime_claim` from `active_proving_default`, so new maintainer iteration defaults, conformance fast-paths, and train-loop proof wiring point to OpenAI `operator_cli` while the historical bookmarks anchor remains recorded service-lane evidence, and the carried-forward active proving-default decision is `promote` on that retained historical reading rather than the stale `improve_shipping_default` wording |
| `CT3` strongest-native-surface fallback law | `AGENTS.md`; `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`; `lab/cortex_conformance.py`; `tests/unit/test_cortex_conformance.py` | closed | landed | product/runtime truth remains separate from proving truth: OpenAI `service_api` stays the historical product/runtime claim, while the strongest available native surface now governs development conformance by default and OpenAI proving therefore defaults to `operator_cli` unless maintainers explicitly override back to the historical service lane |

---

## 8. Mediation justification gate

Source of truth:

- `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
- `docs/lab/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md`
- `docs/lab/CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md`
- `docs/lab/CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md`
- `docs/lab/CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md`

Overall status: `landed`

This row records whether package-level evidence is strong enough to justify one bounded experimental mediation seam.
It does not authorize implementation by itself, and it does not widen packet meaning, rollout scope, or runtime defaults.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `J3` mediation justification review | `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`; `docs/lab/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md`; `docs/lab/CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0.md`; `docs/lab/CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0.md`; `docs/lab/CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0.md` | closed | landed | J2 earned package-level `candidate_positive` signal on reduced thrashing, better branch discipline, lower visible burden at equal task value, and better host-specialized realization; uncertainty remains `insufficient` but explicit and non-blocking for one first bounded experimental seam. `J3` itself does not authorize rollout or default-on mediation, and later `J4` rows carry the actual implementation truth under the same SRE-only, experimental, `Q_t^{base} -> Q_t^{final}` limits. |

---

## 9. Mediation implementation gate

Source of truth:

- `docs/lab/CORTEX_V2_MEDIATION_HOST_REALIZATION_PROGRAM_0.md`
- `docs/experimental/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md`
- `docs/experimental/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md`

Overall status: `partial`

These rows track the first bounded mediation implementation after `J3`.
They do not authorize Core widening, AUX runtime widening, multi-host runtime rollout, or default-on mediation.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| `J4B` reference `seek-context` reachability slice | `docs/lab/CORTEX_V2_MEDIATION_HOST_REALIZATION_PROGRAM_0.md`; `tests/unit/test_reference_executive_builder.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py` | closed | landed | exact missing-capability / missing-context pressure now admits and selects `seek-context` on the real reference runtime lane while generic host friction still stays closed; `Q_t^{final}(a)` remains identity on accepted baseline truth |
| `J4C` reference experimental host-realization finalizer | `docs/lab/CORTEX_V2_MEDIATION_HOST_REALIZATION_PROGRAM_0.md`; `experimental/sre/mediation.py`; `tests/unit/test_sre_mediation.py`; `tests/unit/test_reference_runtime_scoring.py`; `tests/unit/test_reference_runtime_step.py`; `tests/integration/test_reference_runtime_cli.py` | closed | landed | explicit `mediation_mode` now defaults to identity; experimental mode finalizes only already-selected `seek-context` and only specializes clearly superior runtime-visible `mcp.query` opportunities |
| `J4D` runtime-backed reference mediation evidence closure | `docs/experimental/CORTEX_V2_REFERENCE_LANE_PACKET_EXAMPLE_2.md`; `docs/experimental/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md`; `tests/integration/test_reference_lane_packet_example.py`; `tests/integration/test_reference_mediated_lane_packet_example.py`; `tests/integration/test_reference_mediated_host_realization_comparator.py` | closed | landed | the reference baseline and mediated packet examples plus the host-realization comparator now use the real reference runtime path; packet truth remains unchanged while the comparator delta is only nested mediation diagnostics plus direct specialization |
| `J4F` workflow closeout and hygiene | `docs/internal/CORTEX_V2_ACTIVE_WORKSTREAM.md`; `docs/internal/REPO_WORKFLOW.md`; `python3 internal/workflow/repo_workflow.py close-session --message ...`; `python3 internal/workflow/repo_workflow.py sync-main`; `python3 internal/workflow/repo_workflow.py cleanup-report` | origin/main reconciliation only | partial | workflow truth, correspondence truth, and phase-gate truth now match on the accepted local `main` line; the older local `review/*` backlog has been archived to local `archive/review--*` tags and removed, but strict repo hygiene remains partial because local `main` is still ahead of `origin/main` |
