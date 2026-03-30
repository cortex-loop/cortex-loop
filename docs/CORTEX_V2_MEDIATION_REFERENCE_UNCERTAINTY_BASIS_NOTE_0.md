# CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_BASIS_NOTE_0

Date: 2026-03-20
Status: `reference uncertainty basis satisfied`

## Scope

This note records why `scenario_uncertainty_reference_01` now has a lawful committed reference-only mediation basis.
It does not justify mediation, activate mediation, or widen the allowed comparison surface.

## Prior Gap

The old single-step anchor packet was lawful but too thin for a fair uncertainty comparator.
It showed only one uncertified reference-host commitment outcome and did not provide repeated loop evidence, a matched certified-resolution comparator surface, or a counted paired-run series that would survive adversarial review.

## Satisfied Basis

The basis is now satisfied by the committed reference-host uncertainty paired-run series.
The sufficient supporting surfaces are:

- `tests/integration/_reference_mediation_uncertainty_episode.py`
- `tests/integration/_reference_mediation_uncertainty_experimental.py`
- `tests/integration/test_reference_mediation_baseline_packets.py`
- `tests/integration/test_reference_mediated_uncertainty_comparator.py`
- `docs/mediation_evidence/reference/scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md`
- `docs/mediation_evidence/reference/scenario_uncertainty_reference_01__experimental_mediated__run_001.md`
- `docs/CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_REPLICATION_NOTE_0.md`

## Basis Law

The committed uncertainty series is only countable because it preserves all of the following:

- the same reference-host commitment semantics
- the same contradiction-bearing degradation law
- the same evidence/publication surface
- the same final certified completion class
- the same `task_value_equal_truth_preservation` rubric
- the same `env_uncertainty_sensitive` context

The counted comparator difference is only the removal of one redundant uncertified retry after the first guarded uncertainty signal.

## Anti-Patterns

The following remain non-qualifying for this basis:

- a single uncertified anchor packet with no matched comparator
- a comparator that changes blockedness or final truth class
- any run that hides contradiction or degradation evidence
- any run that changes reference-host commitment semantics to make mediation look better
- any run that infers uncertainty improvement without a committed multi-step trace and loop count

## Outcome

`scenario_uncertainty_reference_01` now has a satisfied reference-only basis for comparative evidence review.
Even with the satisfied basis, this remains cell-local evidence only. The accepted package-level justification decision is recorded in `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`, and this note does not by itself authorize implementation.
