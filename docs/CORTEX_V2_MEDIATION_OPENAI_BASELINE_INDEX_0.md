# CORTEX_V2_MEDIATION_OPENAI_BASELINE_INDEX_0

Date: 2026-03-20
Status: `openai mediation baseline run index (`active`, baseline-only)`

## Scope

This index records the canonical committed OpenAI-host baseline anchors for mediation evidence review.
Version `0` is OpenAI-first only: it does not record reference or Gemini packets, it remains a canonical anchor index rather than an exhaustive paired-run ledger, and it does not justify mediation.

## Row Rules

- `host_family` is fixed to `openai` in this index version.
- `variant` is fixed to `baseline_non_mediated` in this index version.
- `evidence_status=baseline_packet_committed` means the anchor packet exists and is committed under `docs/mediation_evidence/openai/`.
- additional repeated OpenAI baseline packets belong in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, not as extra rows in this anchor index
- `scenario_host_openai_01` is now baseline-only and grounded in the committed OpenAI packet/publication example recorded in `docs/CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md`; comparator admissibility remains constrained by `docs/CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`.
- `scenario_uncertainty_openai_01` is now backed by the OpenAI uncertainty basis and replication notes in `docs/CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_REPLICATION_NOTE_0.md`.
- `scenario_thrash_openai_01` is now backed by the OpenAI thrash basis and replication notes in `docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_REPLICATION_NOTE_0.md`.

## Index Rows

| run_id | scenario_id | host_family | variant | paired_episode_set_id | evidence_status | packet_path | basis_surface | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| openai_host_realization_baseline_run_001 | scenario_host_openai_01 | openai | baseline_non_mediated | pending_pair_openai_host_001 | baseline_packet_committed | docs/mediation_evidence/openai/scenario_host_openai_01__baseline_non_mediated__run_001.md | tests/integration/test_openai_lane_packet_example.py::test_openai_lane_current_pair_packet_example_matches_committed_doc | none | Baseline-only OpenAI packet/publication anchor grounded in the committed OpenAI-lane example. Comparator admissibility remains constrained by `docs/CORTEX_V2_MEDIATION_OPENAI_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md`. |
| openai_thrash_baseline_run_001 | scenario_thrash_openai_01 | openai | baseline_non_mediated | pair_openai_thrash_001 | baseline_packet_committed | docs/mediation_evidence/openai/scenario_thrash_openai_01__baseline_non_mediated__run_001.md | tests/integration/test_openai_mediation_baseline_packets.py::test_openai_thrash_baseline_packet_matches_committed_doc | none | Canonical OpenAI thrash baseline anchor. Additional OpenAI thrash baseline packets are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, not duplicated in this index. |
| openai_uncertainty_baseline_run_001 | scenario_uncertainty_openai_01 | openai | baseline_non_mediated | pair_openai_uncertainty_001 | baseline_packet_committed | docs/mediation_evidence/openai/scenario_uncertainty_openai_01__baseline_non_mediated__run_001.md | tests/integration/test_openai_mediation_baseline_packets.py::test_openai_uncertainty_baseline_packet_matches_committed_doc | none | Canonical OpenAI uncertainty baseline anchor. Additional OpenAI uncertainty baseline packets are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, not duplicated in this index. |
