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

Overall status: `drifted`

This gate should have been satisfied before the first host slice was considered closed.
That did not happen, so the miss remains visible here until the missing rows are landed.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| cheap-path integration | `tests/integration/test_pipeline_placeholders.py::test_cheap_path_integration_placeholder` | host-integration closeout seam | open | placeholder only |
| candidate-bearing integration | `tests/integration/test_pipeline_placeholders.py::test_candidate_bearing_integration_placeholder` | host-integration closeout seam | open | placeholder only |
| full commitment integration | `tests/integration/test_pipeline_placeholders.py::test_full_commitment_integration_placeholder` | host-integration closeout seam | open | placeholder only |
| degradation roundtrip | `tests/integration/test_pipeline_placeholders.py::test_degradation_roundtrip_placeholder` | host-integration closeout seam | open | placeholder only |
| firewall integration | `tests/integration/test_pipeline_placeholders.py::test_firewall_integration_placeholder` | host-integration closeout seam | open | placeholder only |
| driver-to-core-to-sre smoke | `tests/integration/test_pipeline_placeholders.py::test_driver_to_core_to_sre_smoke_placeholder` | host-integration closeout seam | open | placeholder only |

Supporting note:
- `tests/integration/test_reference_host_neutral.py` is real integration evidence, but it does not retire any of the six named gate rows by itself.

---

## 3. Latency evidence gate

Source of truth:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Section 8

Overall status: `open`

Targets exist, but the repo does not yet carry measured evidence for them.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| cheap-path latency evidence | none | latency-evidence seam | open | target exists, no measurement recorded |
| candidate-bearing latency evidence | none | latency-evidence seam | open | target exists, no measurement recorded |
| full commitment latency evidence | none | latency-evidence seam | open | target exists, no measurement recorded |
| neutral SRE scoring latency evidence | none | latency-evidence seam | open | target exists, no measurement recorded |

---

## 4. Proof-packet prerequisite gate

Source of truth:
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`, Phase 13 and Phase 15 intent

Overall status: `partial`

Minimal schemas exist, but the harness/publication side is not yet earned.

| Gate row | Current evidence | Owner / next closeout | Status | Notes |
| --- | --- | --- | --- | --- |
| minimal event trace artifact schema | `cortex/eval/artifacts.py::EventTraceArtifact` + `tests/unit/test_certification_artifacts.py::test_event_trace_artifact_preserves_contradictions_and_degradations` | closed | landed | minimal schema is real |
| minimal current-pair fragment schema | `cortex/eval/artifacts.py::CurrentPairFragment` + `tests/unit/test_certification_artifacts.py::test_current_pair_fragment_carries_event_trace_and_verdict_summary` | closed | landed | minimal schema is real |
| minimal blocker fragment schema | `cortex/eval/artifacts.py::BlockerFragment` + `tests/unit/test_certification_artifacts.py::test_blocker_fragment_preserves_reason_and_contradictions` | closed | landed | minimal schema is real |
| contradiction-preserving eval harness | none | Phase 13 full evidence harness | open | `cortex/eval/harness.py` is not yet re-earned under the active plan |
| truthful-withheld / packet publication logic | none | Phase 15 first implementation proof packet | open | later proof-packet work |
| measured reference-lane publication example | none | Phase 15 first implementation proof packet | open | requires real packet publication evidence |

---

## 5. Closeout law

- Any handoff that claims a phase or sub-phase is `landed` must include `Phase gate check:`.
- Correspondence rows do not silently satisfy phase-gate rows.
- A phase must remain `partial` or `blocked` if its relevant gate rows remain `open`, `partial`, or `drifted`.
- If a historical gate was missed, record the miss here rather than rewriting history.
