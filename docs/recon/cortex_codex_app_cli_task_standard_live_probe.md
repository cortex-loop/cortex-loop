# Cortex Codex App/CLI Task-Standard Live Probe

Surface: product / lab proof

Probe date: 2026-05-05

Verdict: task_standard_live_probe_structural_gate0; signed-off context delivery
and standard capture are structurally proven, while live Codex delivery,
behavior lift, and downstream gating integration remain unearned.

## What Landed

- Replaced the gated `TASK_STANDARD_FORMATION_TEXT` with the exact signed-off
  prospective task-set text.
- Added `--task-standard-live-gate0` and `--task-standard-live` modes to the
  Codex App/CLI live-probe harness.
- Added isolated subject config support for UserPromptSubmit, PreToolUse,
  PostToolUse, and Stop using the product hook client with
  `--enable-task-standard-text` and without `--runtime-snapshot`.
- Extended trajectory rows with task-standard state counts so the probe can
  distinguish context delivery, standard capture, malformed standard blocks,
  and capture order relative to tool events.

## Evidence Earned

Gate 0 proves, through simulated product lifecycle payloads, that
UserPromptSubmit emits exactly the signed-off context text, visible obligations
initialize in state, a transcript-backed assistant standard block stores
`Work standard`, `Likely misses`, and `Closure evidence`, and malformed or
absent standard blocks stay diagnostic-only without immediate model-visible
blocking.

The probe harness also records root config hashes, subject config path,
trajectory path, context hash, runtime-snapshot absence, standard capture
counts, and malformed-standard counts.

## Not Earned

- No live `codex exec` task-standard run was executed in this seam.
- No behavior lift, output-quality lift, shipping promotion, or Codex App parity
  is earned.
- No downstream proof is earned that captured standards shape later Stop or
  PreToolUse gating decisions.
- No hidden verifier facts, task identity triggers, runtime snapshots, or root
  repo hooks are used.

## Next Decision

Run `codex-app-cli-task-standard-live-run` only with explicit current-turn
live/spend approval. The live run should record either
`pass_prework_standard_capture`, `partial_delivery_only`, `scoped_negative`, or
`fail` without changing text, SRE law, parsing, thresholds, or hook policy.
