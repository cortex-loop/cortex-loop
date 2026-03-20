# CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0

Date: 2026-03-20
Status: `reference thrash basis satisfied`

## Scope

This note records why `scenario_thrash_reference_01` now has a sufficient runnable basis for the committed reference-host thrash baseline series.
It does not justify mediation, activate mediation, or authorize any comparative implementation seam by itself.

## Basis Result

The reference thrash basis is now satisfied by the committed reference-host thrash baseline series.
The repo now contains lawful multi-step reference-host episodes with explicit branch-trajectory evidence, lawful task completion, live packet rebuilding from code, semantic packet revalidation, and candidate packet emission without overwrite.

## Sufficient Surfaces

The current sufficient surfaces for `scenario_thrash_reference_01` are:

- live episode builder:
  - `tests/integration/_reference_mediation_thrash_episode.py`
- live packet revalidation:
  - `tests/integration/test_reference_mediation_baseline_packets.py`
- committed packet docs:
  - `docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_001.md`
  - `docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_002.md`
  - `docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_003.md`
- replication law note:
  - `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md`

These surfaces are sufficient because they bind the reference-host commitment path to landed SRE goal, brake, allocation, and support-session carriers across one bounded four-step episode that ends in certified completion.

## Deterministic Branch Derivation Rules

- `open`: a non-main branch appears in `branch_registry` that was absent in the previous step, and the selected family for the current step is `branch`
- `suspend`: the previous step had `active_track_ref` equal to a non-main branch, the current step returns `active_track_ref` to `main`, and that branch still remains in `branch_registry`
- `resume`: the previous step had `active_track_ref="main"`, the current step switches to an existing non-main branch, and `resume_anchor_available=True`
- `merge`: a non-main branch present in the previous step disappears from `branch_registry` after the current step yields a `FULL_COMMITMENT` verdict of `CERTIFIED`

The committed reference thrash baseline packets are only lawful because the live builder derives the exact branch sequence `open -> suspend -> resume -> merge` from those rules rather than from hand-written prose.

## Non-Qualifying Anti-Patterns

These do not qualify as a `scenario_thrash_reference_01` basis:

- pure carrier-type tests
- synthetic branch labels with no host episode
- single-turn packets with prose that merely mentions churn
- any packet that infers reopen/resume behavior without committed trace evidence

## Outcome

`scenario_thrash_reference_01` is now satisfied by the committed baseline-only reference thrash series.
That baseline basis now supports the recorded three-pair reference-only experimental comparator set under `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md`, but package-level axis summaries still remain `insufficient`, and mediation remains blocked until qualifying comparative lift evidence exists.
