# CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0

Date: 2026-03-20
Status: `gemini uncertainty baseline basis satisfied`

## Scope

This note records why `scenario_uncertainty_gemini_01` is the first lawful non-reference baseline seam for mediation evidence.
It does not justify mediation, activate mediation, or widen the allowed comparison surface.

## Why Gemini Uncertainty First

The mediation package is still too reference-local, but the Gemini host now has landed observe/bind, commitment-path, and neutral-only slices.
Gemini uncertainty is the strongest non-reference baseline seam because it can preserve contradiction-bearing uncertified truth on a landed commitment path without forcing host-realization claims or inventing a mediated comparator prematurely.

## Supporting Surfaces

The current sufficient surfaces for this Gemini baseline anchor are:

- `tests/unit/test_gemini_host.py`
- `tests/unit/test_gemini_host_commitment.py`
- `tests/unit/test_gemini_host_neutral.py`
- `tests/integration/_gemini_mediation_baseline_packets.py`
- `tests/integration/test_gemini_mediation_baseline_packets.py`
- `docs/CORTEX_V2_MEDIATION_GEMINI_BASELINE_INDEX_0.md`
- `docs/mediation_evidence/gemini/scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md`

## Basis Law

The committed Gemini uncertainty baseline anchor is only lawful because it preserves all of the following:

- the same Gemini observe/bind meaning
- the same commitment truth boundary
- an explicit uncertified full-commitment outcome
- explicit contradiction and degradation preservation on the verdict
- the same `task_value_equal_truth_preservation` rubric
- the same `env_uncertainty_sensitive` context

This seam records only a Gemini baseline anchor.
No Gemini mediated comparator is committed yet, no Gemini pair is counted yet, and no Gemini verdict may move off `insufficient` in this slice.

## Anti-Patterns

The following remain non-qualifying for this Gemini baseline seam:

- any Gemini mediated packet
- any Gemini paired-ledger row
- any Gemini verdict change inferred from one baseline packet
- any host-realization claim inferred from uncertified Gemini commitment evidence alone
- any OpenAI broadening in the same slice

## Outcome

`scenario_uncertainty_gemini_01` now has one lawful committed non-reference baseline anchor.
Even with that anchor, mediation remains blocked until broader counted non-reference comparative evidence exists.
