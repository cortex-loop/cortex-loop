# V2/V3 Deterministic Parity Proof — 2026-04-17

## Surface under test
3 template surfaces × 5 checks = 15 parity rows.

Verification runs twice per template: once with the lab-owned V2 known-good completion and once with the lab-owned V3 known-good completion. Instruction and input-text axes run once per template because they are completion-independent. Repair-ticket runs once per template from a shared lab-owned broken completion that is verified on both sides before the ticket is built.

## Pre-registered analysis
- If `divergence_count == 0`: V3 has earned drop-in parity claim on the deterministic fixture-level surface. The next sprint may proceed to live measurement without first closing any parity gap.
- If `1 <= divergence_count <= 5`: V3 has partial drop-in parity; each divergence is a concrete, named code-level gap. The next sprint closes exactly those gaps and re-runs this harness.
- If `divergence_count > 5`: the divergence is systemic. V3 has not earned drop-in claim. Investigation precedes any further V3 investment; the investigation result will determine whether V3 is repositioned or repaired.
- Divergences on the verification axis with V2's fixture but not V3's fixture, or vice versa, are marked as fixture asymmetries rather than implementation bugs and listed separately.

## Raw rows
| axis | task_id | completion_source | equal | divergence_keys |
|---|---|---|---|---|
| input_text | bookmarks_app_template | shared | yes | <none> |
| instructions | bookmarks_app_template | shared | yes | <none> |
| repair_ticket | bookmarks_app_template | shared | no | text |
| verification | bookmarks_app_template | v2 | yes | <none> |
| verification | bookmarks_app_template | v3 | yes | <none> |
| input_text | feature_flags_template | shared | yes | <none> |
| instructions | feature_flags_template | shared | yes | <none> |
| repair_ticket | feature_flags_template | shared | no | text |
| verification | feature_flags_template | v2 | yes | <none> |
| verification | feature_flags_template | v3 | yes | <none> |
| input_text | project_template | shared | yes | <none> |
| instructions | project_template | shared | yes | <none> |
| repair_ticket | project_template | shared | no | text |
| verification | project_template | v2 | yes | <none> |
| verification | project_template | v3 | yes | <none> |

## Divergence summary
- `divergence_count = 3`
- Per-axis breakdown: `repair_ticket = 3`
- Instruction parity: 3/3 equal
- Input-text parity: 3/3 equal
- Verification parity: 6/6 equal
- Fixture asymmetries: none

## Actual outcome
`divergence_count = 3`.

All three divergences are on the `repair_ticket` axis: `bookmarks_app_template`, `project_template`, and `feature_flags_template`. They are now earned from real template-grounded failing completions, not a synthetic failure state.

The per-template diffs are:
- `bookmarks_app_template`: V2 emits `falsified_checks: import_smoke` and V3 omits that line. The remaining repair-ticket lines match.
- `project_template`: V2 emits `falsified_checks: pytest` and orders `trusted_checks` as `import_smoke, parse`; V3 omits `falsified_checks` and orders `trusted_checks` as `parse, import_smoke`.
- `feature_flags_template`: V2 emits `falsified_checks: pytest`, orders `trusted_checks` and `trusted_paths` differently, and lists the same failing tests in a different order from V3.

No instruction, input-text, or verification row diverged. Both verifiers produced the same normalized outcomes on both lab-owned passing completions for all three template surfaces.

## Recommendation for next sprint
`v3-close-divergence-repair_ticket`
