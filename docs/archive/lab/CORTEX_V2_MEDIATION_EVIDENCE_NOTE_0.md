# CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0

Surface: lab

Date: 2026-03-30
Status: `j2_gap_closure_reference_openai_claude_recorded`

## Scope

This note summarizes the current state of the mediation evidence package after the mandatory J2 gap-closure reruns.
Version `0` remains evidence-only; it supports the accepted J3 justification decision but does not by itself authorize mediation implementation.

## Current Evidence State

All current reference-host, Gemini-host, OpenAI-host, and Claude-host committed mediation packet surfaces are now present on the current line.
Three reference-only mediation-specific host-realization pairs are now recorded for `scenario_host_reference_01`.
Three Gemini-only mediation-specific host-realization pairs are now recorded for `scenario_host_gemini_01`.
Three OpenAI-only mediation-specific host-realization pairs are now recorded for `scenario_host_openai_01`.
Three reference-only branch-discipline pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three OpenAI-only branch-discipline pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three Claude-only branch-discipline pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three reference-only non-thrash burden pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three OpenAI-only non-thrash burden pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three Claude-only non-thrash burden pairs are now recorded in `docs/lab/CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0.md`.
Three Claude-only mediation-specific host-realization pairs are now recorded for `scenario_host_claude_01`.
`scenario_branch_reference_01` / `reference` now has `candidate_positive` signal for better branch discipline and repeated lower reopen/resume counts.
`scenario_branch_openai_01` / `openai` now has `candidate_positive` signal for better branch discipline and repeated lower reopen/resume counts.
`scenario_branch_claude_01` / `claude` now has `candidate_positive` signal for better branch discipline and repeated lower reopen/resume counts.
`scenario_host_reference_01` / `reference` now has `candidate_positive` signal for better host-specialized realization.
`scenario_host_gemini_01` / `gemini` now has `candidate_positive` signal for better host-specialized realization.
`scenario_host_openai_01` / `openai` now has `candidate_positive` signal for better host-specialized realization.
`scenario_burden_reference_01` / `reference` now has `candidate_positive` signal for lower visible burden at equal task value on a non-thrash family.
`scenario_burden_openai_01` / `openai` now has `candidate_positive` signal for lower visible burden at equal task value on a non-thrash family.
`scenario_burden_claude_01` / `claude` now has `candidate_positive` signal for lower visible burden at equal task value on a non-thrash family.
`scenario_host_claude_01` / `claude` now has `candidate_positive` signal for better host-specialized realization.
Reference, Gemini, OpenAI, and Claude now carry the host-realization `candidate_positive` cells.
Branch-discipline evidence no longer derives only from `thrash_control`.
Lower-visible-burden evidence is no longer confined to the `thrash_control` scenario family.
Gemini remains explicit as partial/contaminated where needed and is not hidden behind pooled summaries.

## Per-Axis Status

- reduced thrashing: `candidate_positive`
- better branch discipline: `candidate_positive`
- better uncertainty handling: `insufficient`
- lower visible burden at equal task value: `candidate_positive`
- better host-specialized realization: `candidate_positive`

## Per-Host Status

- `reference`: `baseline_and_paired_series_recorded`
- `gemini`: `baseline_and_three_paired_series_recorded`
- `openai`: `baseline_and_paired_series_recorded`
- `claude`: `baseline_and_paired_series_recorded`

## Blocker Statement

The accepted J3 decision is that mediation is now justified for one bounded experimental seam.
Better uncertainty handling remains the one still-package-insufficient axis because the current uncertainty signal still comes from one family only and still lacks Claude expansion, but that gap is explicit and non-blocking for one first bounded seam.
The accepted package-level decision is recorded in `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`.
This evidence package is not a second truth court and does not by itself authorize implementation.

## Exact Missing-Evidence Delta

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family with repeated lower reopen/resume counts on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better branch discipline | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal still comes from one family only and still lacks Claude expansion. | optionally record scenario_uncertainty_claude_01 if the remaining uncertainty gap still matters after J2 |
| lower visible burden at equal task value | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_burden_reference_01/reference; scenario_burden_openai_01/openai; scenario_burden_claude_01/claude | J2 broadens the burden axis beyond `thrash_control` on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better host-specialized realization | candidate_positive | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai; scenario_host_claude_01/claude | Claude host-realization is now present and the refreshed reference/openai lines remain positive. | no mandatory additional paired evidence before one bounded experimental seam |

## Next Rerun Contract

| target_id | preferred_hosts | minimum_pairs | reason |
| --- | --- | --- | --- |
| uncertainty_expansion_if_still_needed | claude first, then stable second-family expansion | 3 usable pairs | Current uncertainty signal comes from one family only and may still be too narrow after J2. |
