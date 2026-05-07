# Codex App/CLI Task-Standard Evidence-Gating Remediation

Verdict: task_standard_evidence_gating_remediated_structurally; live behavior
lift remains unearned.

## Summary

The task-standard three-arm live comparison produced `failure_overblock` because
active Cortex blocked clean controls after successful standard capture. This
seam repairs the product evidence/gating relation without changing signed
task-standard text, Stop text, selector thresholds, fixtures, scoring, hook
configuration, SRE doctrine, or live behavior claims.

## What Changed

- Added `task_standard_closure_satisfied(...)` in
  `cortex/sre/task_standard.py` as the direct SRE bridge from captured
  `TaskStandardSpine` state into verification-fit.
- Updated the Codex App/CLI coordinator so Stop still opens a verification
  expectation for closure claims, but immediately pays it down when the
  captured task standard already has aligned evidence and no unmatched claimed
  standard items.
- Tightened `likely_miss` claim semantics so risk items are claimed only by
  explicit risk-closure language such as `no`, `without`, `verified`, or
  `confirmed`, not incidental token overlap with ordinary closure claims.
- Expanded task-standard tokenization for compound/range terms so product-
  visible evidence such as `0..65535`, `TCP/UDP`, and `upper-bound` can align
  with patch and test evidence without task identity or hidden verifier facts.

## Replay Evidence

Product tests now cover the two clean-control overblock shapes from the live
run:

- `simple_success_file`: aligned task-standard evidence was present and
  `unmatched_standard_item_ids` was empty, but the old
  `verification_evidence_count` counter remained zero. The replay now stays
  silent by consuming `TaskStandardSpine` directly.
- `clean_verified_work`: patch and test evidence for the `65535` port-bound
  fix now aligns to the claimed work standard and closure evidence, while the
  likely-miss risk line is not treated as an explicit closure claim from
  incidental overlap.

Existing mismatch tests still require real premature closure gaps to block, and
generic checks still cannot satisfy a task standard by themselves.

## Evidence Earned

Structural/product evidence only: deterministic product tests replay the live
overblock failure classes and keep the captured-standard premature-gap case
blockable. This does not earn output-quality lift, behavior lift, Codex App
parity, or permission to change model-visible text.

## Next

Only after full validation, the next product move may be a pinned task-standard
three-arm behavior comparison rerun under the existing no-tuning rules. If the
rerun produces `failure_no_lift` or another clean-control overblock, stop for an
architecture decision rather than tuning text, thresholds, hooks, fixtures, or
hidden scoring.
