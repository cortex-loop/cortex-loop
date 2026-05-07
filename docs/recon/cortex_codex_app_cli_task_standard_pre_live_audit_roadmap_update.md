# Codex App/CLI Task-Standard Pre-Live Audit Roadmap Update

Surface: product + lab proof planning

## Summary

The pre-live audit decision is to pause the task-standard behavior comparison
rerun and insert a no-spend offline readiness gate first. The evidence-gating
remediation is structurally correct, but behavior lift remains unearned and the
prior live comparison still warns against spending on another live matrix before
checking the captured artifacts.

The roadmap authority remains `internal/truth/cortex_status.json`, with
generated views in `docs/CORTEX_STATUS.md` and generated sections of
`docs/CORTEX.md`. This recon records why `next_product_train` now points to
`codex-app-cli-task-standard-offline-replay-readiness-gate` instead of the live
behavior-comparison rerun.

## Audit Findings Extracted

- Live comparisons stay paused until a no-spend readiness gate passes.
- The evidence-gating remediation is the right product/SRE direction: Stop can
  consume captured `TaskStandardSpine` satisfaction directly instead of relying
  only on `verification_evidence_count`.
- Behavior lift remains unearned. The previous Astro family was silent-equals-
  active on hidden quality, and truth-gap baseline reproduction was unstable.
- The product goal remains Cortex's runtime executive loop, not a lab score:
  model-derived task standard -> host-visible evidence -> SRE verification-fit
  decision -> lawful model I/O.
- Existing comparison artifacts support transcript-derived replay from
  `codex_stdout.jsonl`; they do not prove exact raw hook-payload replay because
  `hook_trajectory.jsonl` and `hook_client_diagnostics.jsonl` are summarized
  product diagnostics.
- Future live runs that need exact deterministic replay should persist sanitized
  raw hook payloads as first-class artifacts.
- A compound-token precision regression should land before live spend so the
  widened task-standard tokenization does not create cross-concept overmatch.
- The immediate alignment upgrade should be scored lexical matching, not
  transport: use token-class weighting first for identifiers, file paths,
  numbers, commands, and exact literals, then local frequency dampening for
  terms that appear across many items/events.
- Sinkhorn-style transport is the elegant later home if the next gate proves
  mass conservation is still load-bearing after pairwise scores are trustworthy:
  one product-visible evidence event should not be able to over-credit unrelated
  standard items.
- The implementation must keep task-standard law host-agnostic in SRE and keep
  Codex artifact/replay mechanics in lab or host surfaces.
- The readiness seam should remove or retire proven-dead code in touched
  alignment/harness surfaces rather than layering more flags or duplicate paths.

## Required Next Gate

The next seam should add a lab readiness mode that reads the prior live run at
`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/`
and reports:

- whether the two known clean-control overblocks would now stay silent;
- whether known premature-closure or mismatch rows remain blockable;
- whether hidden scoring remains scoring-only;
- whether current artifacts contain enough raw payload for exact replay, or only
  transcript-derived replay;
- whether compound-token cross-concept overlap and one-event-overcredits-many-
  items cases are caught before live spend;
- whether active Cortex has at least one meaningful actuator-opportunity signal
  beyond silent before live spend.
- whether touched code remains hygienic: no stale task-standard flags, no
  duplicate replay paths, no host-specific policy inside SRE, and any proven-
  dead touched code removed with tests preserving artifact compatibility.

If the gate shows no active-vs-silent actuator opportunity, cannot prove the
clean controls stay silent, overstates artifact replay fidelity, or shows that
scored lexical alignment still over-credits unrelated standard items, the next
move is an architecture, proof-boundary, or Sinkhorn/transport-deficit decision,
not a live rerun.

## Claims Not Earned

This roadmap update does not earn behavior lift, output-quality lift, Codex App
parity from Codex CLI evidence, shipping promotion, truth-gap baseline
stability, exact raw hook-payload replay, or permission to tune signed
task-standard text, Stop text, SRE law, selector thresholds, fixtures, scoring,
hook wiring, or hidden-verifier boundaries.
