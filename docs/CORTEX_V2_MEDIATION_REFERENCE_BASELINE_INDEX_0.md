# CORTEX_V2_MEDIATION_REFERENCE_BASELINE_INDEX_0

Date: 2026-03-20
Status: reference mediation baseline run index (`active`, baseline-only)

## Scope

This index records the canonical committed reference-host baseline anchor packets for mediation evidence review.
Version `0` is reference-first only: it does not record Gemini or OpenAI packets, it does not act as an exhaustive paired-run ledger, and it does not justify mediation.

## Row Rules

- `host_family` is fixed to `reference` in this index version.
- `variant` is fixed to `baseline_non_mediated` in this index version.
- `evidence_status=baseline_packet_committed` means the anchor packet exists and is committed under `docs/mediation_evidence/reference/`.
- `evidence_status=artifact_gap` means the scenario is intentionally kept open because the repo does not yet contain an honest committed baseline packet for it.
- additional repeated baseline packets belong in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, not as extra rows in this anchor index
- `scenario_host_reference_01` is now the baseline side of the first recorded reference host-realization pair, governed by `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0.md`.
- `scenario_uncertainty_reference_01` is now backed by the satisfied-basis note in `docs/CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_BASIS_NOTE_0.md` and the replication law in `docs/CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_REPLICATION_NOTE_0.md`.
- `scenario_thrash_reference_01` is now backed by the satisfied-basis note in `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0.md` and the replication law in `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md`.

## Index Rows

| run_id | scenario_id | host_family | variant | paired_episode_set_id | evidence_status | packet_path | basis_surface | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reference_uncertainty_baseline_run_001 | scenario_uncertainty_reference_01 | reference | baseline_non_mediated | pair_reference_uncertainty_001 | baseline_packet_committed | docs/mediation_evidence/reference/scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md | tests/integration/test_reference_mediation_baseline_packets.py::test_reference_uncertainty_baseline_packet_matches_committed_doc | none | Canonical baseline anchor for the reference uncertainty series. Additional uncertainty baseline packets are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, while this anchor remains backed by the satisfied basis note and replication law. |
| reference_host_realization_baseline_run_001 | scenario_host_reference_01 | reference | baseline_non_mediated | pair_reference_host_001 | baseline_packet_committed | docs/mediation_evidence/reference/scenario_host_reference_01__baseline_non_mediated__run_001.md | tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc | none | Baseline side of the first recorded reference host-realization pair, grounded in the committed reference-lane example. Comparator admissibility remains constrained by `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md` and the pair fairness law is recorded in `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0.md`. |
| reference_thrash_baseline_run_001 | scenario_thrash_reference_01 | reference | baseline_non_mediated | pair_reference_thrash_001 | baseline_packet_committed | docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_001.md | tests/integration/test_reference_mediation_baseline_packets.py::test_reference_thrash_baseline_packet_matches_committed_doc | none | Canonical baseline anchor for the reference thrash series. Additional thrash baseline packets are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, while this anchor remains backed by the satisfied basis note and replication law. |
