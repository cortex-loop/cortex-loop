# CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0

Date: 2026-03-24
Status: `reference_three_series_with_gemini_three_series_and_openai_three_series_recorded`

## Scope

This note summarizes the current state of the mediation evidence package.
Version `0` is a reporting scaffold only; it does not justify mediation, activate mediation, or authorize implementation work.

## Current Evidence State

All current reference-host scenario families now have committed baseline run packets in `docs/CORTEX_V2_MEDIATION_REFERENCE_BASELINE_INDEX_0.md`.
Three experimental reference-only baseline-versus-mediated thrash pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three experimental Gemini-only baseline-versus-mediated thrash pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three experimental OpenAI-only baseline-versus-mediated thrash pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three experimental reference-only uncertainty pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three experimental Gemini-only uncertainty pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three experimental OpenAI-only uncertainty pairs are now recorded in `docs/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
The current package is preseeded from the scenario catalog so future evidence cannot cherry-pick only favorable scenario-host cells.
The reference thrash baseline series is now backed by `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_REFERENCE_THRASH_REPLICATION_NOTE_0.md`, which record the committed baseline series, the live episode builder, the deterministic derivation rules, and the counted three-pair replication law.
The reference uncertainty baseline series is now backed by `docs/CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_REFERENCE_UNCERTAINTY_REPLICATION_NOTE_0.md`, which record the committed baseline series, the live episode builder, and the counted three-pair replication law.
The Gemini thrash series is now backed by `docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_GEMINI_THRASH_REPLICATION_NOTE_0.md`, which record the committed Gemini baseline series, the live episode builder, and the counted three-pair replication law.
The Gemini uncertainty series is now backed by `docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_GEMINI_UNCERTAINTY_REPLICATION_NOTE_0.md`, which record the committed Gemini baseline series, the live episode builder, and the counted three-pair replication law.
The OpenAI thrash series is now backed by `docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_OPENAI_THRASH_REPLICATION_NOTE_0.md`, which record the committed OpenAI baseline series, the live episode builder, and the counted three-pair replication law.
The OpenAI uncertainty series is now backed by `docs/CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_BASIS_NOTE_0.md` and `docs/CORTEX_V2_MEDIATION_OPENAI_UNCERTAINTY_REPLICATION_NOTE_0.md`, which record the committed OpenAI baseline series, the live episode builder, and the counted three-pair replication law.
The reference host-realization series is now backed by `docs/CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0.md`, which records the counted three-pair reference host-realization fairness law.
The Gemini host-realization series is now backed by `docs/CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_REPLICATION_NOTE_0.md`, which records the counted three-pair Gemini host-realization fairness law.
Three reference-only mediation-specific host-realization pairs are now recorded for `scenario_host_reference_01`.
Three Gemini-only mediation-specific host-realization pairs are now recorded for `scenario_host_gemini_01`.
Three OpenAI-only mediation-specific host-realization pairs are now recorded for `scenario_host_openai_01`.
`scenario_host_reference_01` / `reference` now has `candidate_positive` signal for better host-specialized realization, while package-level host-specialized realization remains `insufficient`.
`scenario_host_gemini_01` / `gemini` now has `candidate_positive` signal for better host-specialized realization, while package-level host-specialized realization remains `insufficient`.
`scenario_host_openai_01` / `openai` now has `candidate_positive` signal for better host-specialized realization, while package-level host-specialized realization remains `insufficient`.
reference, Gemini, and OpenAI now carry the host-realization `candidate_positive` cells.
`scenario_thrash_reference_01` / `reference` now has `candidate_positive` cell-level signal for reduced thrashing and better branch discipline, while package-level axis summaries remain globally `insufficient`.
`scenario_thrash_reference_01` / `reference` now also has `candidate_positive` cell-level signal for lower visible burden at equal task value, while the package-level burden axis remains `insufficient`.
`scenario_thrash_gemini_01` / `gemini` now has `candidate_positive` cell-level signal for reduced thrashing and better branch discipline, while package-level axis summaries remain globally `insufficient`.
`scenario_thrash_gemini_01` / `gemini` now also has `candidate_positive` cell-level signal for lower visible burden at equal task value, while the package-level burden axis remains `insufficient`.
`scenario_thrash_openai_01` / `openai` now has `candidate_positive` cell-level signal for reduced thrashing and better branch discipline, while package-level axis summaries remain globally `insufficient`.
`scenario_uncertainty_reference_01` / `reference` now has `candidate_positive` cell-level signal for better uncertainty handling, while package-level axis summaries remain globally `insufficient`.
`scenario_uncertainty_gemini_01` / `gemini` now has `candidate_positive` cell-level signal for better uncertainty handling, while package-level axis summaries remain globally `insufficient`.
`scenario_uncertainty_openai_01` / `openai` now has `candidate_positive` cell-level signal for better uncertainty handling, while package-level axis summaries remain globally `insufficient`.

## Per-Axis Status

- reduced thrashing: `insufficient`
- better branch discipline: `insufficient`
- better uncertainty handling: `insufficient`
- lower visible burden at equal task value: `insufficient`
- better host-specialized realization: `insufficient`

## Per-Host Status

- `reference`: `baseline_and_three_paired_series_recorded`
- `gemini`: `baseline_and_three_paired_series_recorded`
- `openai`: `baseline_and_three_paired_series_recorded`

## Blocker Statement

Mediation remains blocked because the current evidence is still too narrow across axes and hosts to justify implementation.
If no mediation-vs-non-mediation axis shows measurable lift under this package, mediation remains blocked and no implementation seam may open.
