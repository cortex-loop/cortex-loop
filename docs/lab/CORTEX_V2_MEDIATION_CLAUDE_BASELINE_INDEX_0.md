# CORTEX_V2_MEDIATION_CLAUDE_BASELINE_INDEX_0

Surface: lab

Date: 2026-03-30
Status: `claude mediation baseline run index (active, baseline-only)`

## Scope

This index records the canonical committed Claude-host baseline anchors for mediation evidence review.
Version `0` is Claude-first only: it records the new Claude host-realization baseline anchor and does not by itself justify mediation.

## Row Rules

- `host_family` is fixed to `claude` in this index version.
- `variant` is fixed to `baseline_non_mediated` in this index version.
- `evidence_status=baseline_packet_committed` means the anchor packet exists and is committed under `docs/lab/mediation_evidence/claude/`.
- `scenario_host_claude_01` is the canonical baseline anchor for the counted Claude host-realization paired-run series, grounded in the committed Claude packet/publication example recorded in `docs/experimental/CORTEX_V2_CLAUDE_LANE_PACKET_EXAMPLE_0.md`.

## Index Rows

| run_id | scenario_id | host_family | variant | paired_episode_set_id | evidence_status | packet_path | basis_surface | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude_host_realization_baseline_run_001 | scenario_host_claude_01 | claude | baseline_non_mediated | pair_claude_host_001 | baseline_packet_committed | docs/lab/mediation_evidence/claude/scenario_host_claude_01__baseline_non_mediated__run_001.md | tests/integration/test_claude_lane_packet_example.py::test_claude_lane_current_pair_packet_example_matches_committed_doc | none | Canonical baseline anchor for the counted Claude host-realization paired-run series. Three paired runs are now recorded through `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`, and admissibility/fairness remain constrained by `docs/lab/CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_ADMISSIBILITY_NOTE_0.md` and `docs/lab/CORTEX_V2_MEDIATION_CLAUDE_HOST_REALIZATION_REPLICATION_NOTE_0.md`. |
