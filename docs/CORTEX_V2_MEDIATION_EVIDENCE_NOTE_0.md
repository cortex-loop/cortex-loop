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
`scenario_thrash_openai_01` / `openai` now also has `candidate_positive` cell-level signal for lower visible burden at equal task value, while the package-level burden axis remains `insufficient`.
Reference, Gemini, and OpenAI now carry the lower-visible-burden `candidate_positive` cells, but that burden signal remains too narrow at package level because it is still confined to the `thrash_control` scenario family.
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
Lower visible burden at equal task value remains package-insufficient because all current burden signal is still confined to the `thrash_control` scenario family.
If no mediation-vs-non-mediation axis shows measurable lift under this package, mediation remains blocked and no implementation seam may open.

## Exact Missing-Evidence Delta

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current signal comes from one family only and has no non-thrash corroboration. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better branch discipline | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current branch-discipline signal derives only from thrash_control and has no dedicated family. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal comes from one family only and still has no Claude expansion. | Record scenario_uncertainty_claude_01 with 3 usable pairs, or add one second uncertainty-sensitive family on stable hosts. |
| lower visible burden at equal task value | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current burden signal is confined to thrash_control and no non-thrash equal-value burden family is recorded. | Record scenario_burden_reference_01, scenario_burden_openai_01, and scenario_burden_claude_01 with burden refs and 3 usable pairs each. |
| better host-specialized realization | insufficient | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai | Current signal exists on one family only, Claude is missing, and future reruns should favor the most stable hosts first. | Record scenario_host_claude_01 with 3 usable pairs and refresh host_realization on reference and openai before promotion. |

host-specialized realization has cell-level signal but not enough package breadth.
branch-discipline evidence still derives only from `thrash_control`.
Gemini should remain explicit as partial/contaminated where needed, not hidden.

## Next Rerun Contract

| target_id | preferred_hosts | minimum_pairs | reason |
| --- | --- | --- | --- |
| branch_discipline_family | reference, openai, claude | 3 usable pairs per host | Current branch-discipline signal derives only from thrash_control. |
| non_thrash_equal_value_burden_family | reference, openai, claude | 3 usable pairs per host | Current burden signal is confined to thrash_control. |
| host_realization_expansion | reference, openai, claude | 3 usable pairs per host | Current host-realization signal lacks Claude breadth and should favor the most stable hosts first. |
| uncertainty_expansion_if_still_needed | claude first, then stable second-family expansion | 3 usable pairs | Current uncertainty signal comes from one family only and may still be too narrow after J2. |
