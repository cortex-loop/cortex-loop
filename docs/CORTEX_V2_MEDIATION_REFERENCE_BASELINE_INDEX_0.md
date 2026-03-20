# CORTEX_V2_MEDIATION_REFERENCE_BASELINE_INDEX_0

Date: 2026-03-20
Status: reference mediation baseline run index (`active`, baseline-only)

## Scope

This index records the committed reference-host baseline run packets that currently exist for mediation evidence review.
Version `0` is reference-first only: it does not record Gemini or OpenAI packets, it does not record any baseline-versus-mediated pair, and it does not justify mediation.

## Row Rules

- `host_family` is fixed to `reference` in this index version.
- `variant` is fixed to `baseline_non_mediated` in this index version.
- `evidence_status=baseline_packet_committed` means the packet exists and is committed under `docs/mediation_evidence/reference/`.
- `evidence_status=artifact_gap` means the scenario is intentionally kept open because the repo does not yet contain an honest committed baseline packet for it.

## Index Rows

| run_id | scenario_id | host_family | variant | paired_episode_set_id | evidence_status | packet_path | basis_surface | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reference_uncertainty_baseline_run_001 | scenario_uncertainty_reference_01 | reference | baseline_non_mediated | pending_pair_reference_uncertainty_001 | baseline_packet_committed | docs/mediation_evidence/reference/scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md | tests/unit/test_reference_host_commitment.py::test_missing_evidence_yields_uncertified | none | Baseline-only uncertified reference-host commitment packet. |
| reference_host_realization_baseline_run_001 | scenario_host_reference_01 | reference | baseline_non_mediated | pending_pair_reference_host_001 | baseline_packet_committed | docs/mediation_evidence/reference/scenario_host_reference_01__baseline_non_mediated__run_001.md | tests/integration/test_reference_lane_packet_example.py::test_reference_lane_current_pair_packet_example_matches_committed_doc | none | Baseline-only reference packet/publication packet grounded in the committed reference-lane example. |
| reference_thrash_baseline_run_001 | scenario_thrash_reference_01 | reference | baseline_non_mediated | pending_pair_reference_thrash_001 | artifact_gap | none | none | artifact_gap | No honest repeated branch-churn reference packet is committed yet; keep this gap explicit until a defensible runnable basis exists. |
