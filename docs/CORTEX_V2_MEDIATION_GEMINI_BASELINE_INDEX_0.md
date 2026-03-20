# CORTEX_V2_MEDIATION_GEMINI_BASELINE_INDEX_0

Date: 2026-03-20
Status: `gemini mediation baseline run index (`active`, baseline-only)`

## Scope

This index records the canonical committed Gemini-host baseline anchors for mediation evidence review.
Version `0` is Gemini-first only: it does not record reference or OpenAI packets, it does not act as an exhaustive paired-run ledger, and it does not justify mediation.

## Row Rules

- `host_family` is fixed to `gemini` in this index version.
- `variant` is fixed to `baseline_non_mediated` in this index version.
- `evidence_status=baseline_packet_committed` means the anchor packet exists and is committed under `docs/mediation_evidence/gemini/`.
- additional repeated Gemini baseline packets belong in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, not as extra rows in this anchor index
- `scenario_uncertainty_gemini_01` is now backed by the satisfied basis note in `docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md`.
- `scenario_thrash_gemini_01` is now backed by the satisfied basis note in `docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_BASIS_NOTE_0.md` and the replication law in `docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_REPLICATION_NOTE_0.md`.

## Index Rows

| run_id | scenario_id | host_family | variant | paired_episode_set_id | evidence_status | packet_path | basis_surface | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gemini_thrash_baseline_run_001 | scenario_thrash_gemini_01 | gemini | baseline_non_mediated | pair_gemini_thrash_001 | baseline_packet_committed | docs/mediation_evidence/gemini/scenario_thrash_gemini_01__baseline_non_mediated__run_001.md | tests/integration/test_gemini_mediation_baseline_packets.py::test_gemini_thrash_baseline_packet_matches_committed_doc | none | Canonical Gemini thrash baseline anchor. Additional Gemini thrash baseline packets are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, and this anchor is backed by `docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_BASIS_NOTE_0.md`. |
| gemini_uncertainty_baseline_run_001 | scenario_uncertainty_gemini_01 | gemini | baseline_non_mediated | pair_gemini_uncertainty_001 | baseline_packet_committed | docs/mediation_evidence/gemini/scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md | tests/integration/test_gemini_mediation_baseline_packets.py::test_gemini_uncertainty_baseline_packet_matches_committed_doc | none | Canonical Gemini uncertainty baseline anchor. Additional Gemini baseline packets for this series are recorded through `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, and this anchor is backed by `docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md`. |
