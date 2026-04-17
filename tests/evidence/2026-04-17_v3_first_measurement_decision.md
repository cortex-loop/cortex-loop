# V3 First Measurement — 2026-04-17

## Cells
| provider | template | arm | N | pass_rate | mean attempts | cost ($) | NA reason |
|---|---|---|---|---|---|---|---|
| openai | bookmarks_app_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| openai | bookmarks_app_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| openai | project_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| openai | project_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| openai | feature_flags_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| openai | feature_flags_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| claude | bookmarks_app_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| claude | bookmarks_app_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| claude | project_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| claude | project_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| claude | feature_flags_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| claude | feature_flags_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| gemini | bookmarks_app_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| gemini | bookmarks_app_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| gemini | project_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| gemini | project_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |
| gemini | feature_flags_template | verified_with_repair | 0 | NA | NA | NA | missing_api_key |
| gemini | feature_flags_template | plain_feedback | 0 | NA | NA | NA | missing_api_key |

## Deltas (verified_with_repair vs plain_feedback, same provider+template)
| provider | template | Δ pass_rate (verified − plain) |
|---|---|---|
| openai | bookmarks_app_template | NA |
| openai | project_template | NA |
| openai | feature_flags_template | NA |
| claude | bookmarks_app_template | NA |
| claude | project_template | NA |
| claude | feature_flags_template | NA |
| gemini | bookmarks_app_template | NA |
| gemini | project_template | NA |
| gemini | feature_flags_template | NA |

## Pre-registered analysis
- If `verified_with_repair` pass_rate ≥ 0.5 on at least one (provider, template) cell: V3 has shipped working verified work; next sprint registers cortex-v3-openai-cli, cortex-v3-claude-cli, cortex-v3-gemini-cli and writes migration docs.
- If `verified_with_repair` pass_rate ≥ `plain_feedback` pass_rate + 0.10 on median across cells: V3's repair ticket + file-block protocol is earning measurable lift over a raw feedback loop on its own codebase; the verified-work design is validated.
- If `verified_with_repair` pass_rate ≤ `plain_feedback` pass_rate across every cell: the verified-work protocol is not helping on this task class; next sprint investigates whether the protocol is too restrictive for the models under test or the tasks are too small to see the effect.
- If any provider column is all-NA due to missing key: that provider's row marked `unmeasured`; next sprint is a re-run with keys present. No architectural conclusion is drawn from a missing-key row.

## Actual outcome
All 18 cells are `NA`. The live artifact contains 180 rows, but every row is marked `error=missing_api_key` because `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY` were all absent in this environment at run time. No provider produced a usable measurement, so no pass-rate or delta claim is earned from this sprint.

## Recommendation for next sprint
`rerun-with-full-keys`

This sprint still earned two useful things:
- the V3 incubation seam is now banked on its own branch with green product, conformance, and V3 proof surfaces
- the cross-provider measurement driver and dry run exist and can be re-used unchanged once keys are present
