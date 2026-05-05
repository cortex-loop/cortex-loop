# Cortex Codex App/CLI Communication Boundary Audit And Hardening

Surface: product / lab proof

Verdict: structural_proof_boundary_issue_localized_to_codex_app_cli

Date: 2026-05-05

## What This Seam Did

This seam audited the recent Codex App/CLI hook-native trickle failures as a
communication-boundary problem rather than a Cortex doctrine problem. The audit
reads existing live artifacts only and separates the full product evidence
chain:

1. `host_stdout_contract_ok`
2. `host_attached_context_observed`
3. `model_assimilation_observed`
4. `state_capture_observed`
5. `gate_used_captured_state`
6. `behavior_lift_claim_allowed`

The ladder is now explicit in proof reports so product success cannot be inferred
from an internal Cortex payload or from host stdout alone.

## Classified Failure Classes

The audit records five distinct failure classes:

- `host_contract_mismatch`: the original task-standard live run emitted flat
  `{"context": ...}` instead of Codex-native
  `hookSpecificOutput.additionalContext`.
- `lifecycle_config_mismatch`: the first no-snapshot live probe loaded project
  hooks but exposed Stop-only rows because the subject config did not register
  the full lifecycle hooks.
- `temporal_capture_mismatch`: the Codex-native rerun delivered context and the
  model produced the Work standard / Likely misses / Closure evidence block, but
  Cortex did not ingest that pre-tool transcript message into
  `TaskStandardSpine`.
- `live_vs_gate0_mismatch`: Gate 0 proved standard capture through Stop
  `last_assistant_message`, while live evidence needed pre-tool transcript/event
  ingestion.
- `workflow_health_closeout_coupling`: direct Mission Reflection hook mechanics
  are now separated from stale closeout/reflection-check readiness.

## Report Hardening

Task-standard live reports now separate:

- `mechanical_success`
- `product_evidence_success`
- `partial_evidence_only`

For `partial_delivery_only`, mechanical execution can be recorded without
claiming product evidence success. The live rerun earned context delivery and
model assimilation only; it did not earn state capture, downstream gate use, or
behavior lift.

Gate 0 now also records a live-equivalent pre-tool transcript boundary case. It
continues to prove Codex-native context serialization and simulated Stop capture,
but it explicitly records that pre-tool transcript ingestion is not implemented
yet.

## Hook Health Split

The repo Codex App Mission Reflection hook is still disabled in root
`.codex/config.toml` by `[features].codex_hooks = false`. The direct hook-health
checks for both the Codex App hook and the older `.claude` Stop hook now test
hook mechanics in structural-only mode while separately reporting current
closeout/reflection-check readiness. A stale closeout can no longer be misread
as "the Codex App hook turned itself back on," or as a direct hook-mechanics
failure.

## Evidence Earned

Structural/lab evidence earned:

- `lab/codex_app_cli_communication_boundary_audit.py --require-pass` classifies
  all five known failure classes from existing artifacts.
- `tests/lab/test_codex_app_cli_communication_boundary_audit.py` locks the
  evidence ladder and prevents partial delivery from becoming a product-success
  claim.
- `tests/lab/test_codex_app_cli_stop_activation_probe.py` locks the
  live-equivalent Gate 0 capture-boundary row.
- `tests/internal/test_codex_app_stop_hook.py` and
  `tests/internal/test_cortex_grid_stop_hook.py` lock direct Mission Reflection
  hook mechanics without requiring current branch closeout readiness.

## Not Earned

This seam does not earn product runtime progress, model-output lift,
task-standard state capture, gate use of the captured standard, Codex App parity,
shipping promotion, new Cortex speech, SRE law changes, selector changes, root
hook activation, or a live Codex rerun.

## Next Move

Queue `codex-app-cli-task-standard-pretool-transcript-capture`.

That seam should implement product-visible transcript/event-stream ingestion for
the pre-tool assistant standard block. It should not tune the signed text, alter
Stop text, change SRE law, or broaden behavior-lift claims.
