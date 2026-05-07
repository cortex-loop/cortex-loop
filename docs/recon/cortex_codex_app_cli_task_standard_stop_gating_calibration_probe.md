# Codex App/CLI Task-Standard Stop-Gating Calibration Probe

Surface: product + lab proof

Verdict: `pass_gating_calibrated`; live Stop-gating remains unearned.

## Summary

This seam tested the next task-standard product link without live spend:
captured `TaskStandardSpine` state can drive existing Stop verification law,
while clean, adequately evidenced closure stays silent.

The probe did not change the signed task-standard text, the locked Stop text,
SRE law, selector thresholds, root hook configuration, or behavior-lift claims.

## What Changed

- Added `--task-standard-stop-gating-gate0` and
  `--task-standard-stop-gating-live` modes to
  `lab/codex_app_cli_stop_activation_probe.py`.
- Added an isolated product subject config for UserPromptSubmit, PreToolUse,
  PostToolUse, and Stop with `--enable-task-standard-text`, no
  `--runtime-snapshot`, and no Stop suppression in the active gating config.
- Added structural trajectories for:
  - `premature_closure_gap`, where captured standards exist but closure outruns
    aligned evidence;
  - `clean_evidenced_closure`, where tool evidence satisfies the work standard
    and closure evidence;
  - replay of the latest live capture artifact
    `.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T213824Z`.
- Fixed task-agnostic alignment bugs that would have produced false overblock:
  - trailing punctuation no longer prevents a standard token like `cat.` from
    aligning with a product-visible `cat` command;
  - `likely_miss` items are risk checks and are not automatically claimed by a
    generic `done` unless the final closure claim explicitly outruns them;
  - closure-evidence items can align to product-visible command/readback
    evidence when the tool event also touches the task standard or contains a
    verification marker.

## Evidence

Command:

```bash
python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-stop-gating-gate0 --require-pass
```

Result:

- `premature_closure_gap_blocks=true`
- `clean_evidenced_closure_stays_silent=true`
- `latest_live_capture_replay_available=true`
- `latest_live_capture_replay_does_not_overblock=true`
- root `.codex/config.toml` unchanged
- no runtime snapshot fixture
- no unexpected model-visible text
- rendered Stop text hash:
  `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`

Gate 0 output:

`.cortex/live_validation/openai/codex_app_cli_task_standard_stop_gating_probe/task_standard_stop_gating_gate0/report.json`

## What This Earns

- Structural evidence that captured task standards can feed the existing Stop
  verification expectation path.
- Structural evidence that the clean file-readback task from the latest live
  capture artifact no longer overblocks under current alignment semantics.
- Proof that the active gating subject config does not suppress Stop blocks and
  still uses only the product hook client.

## What This Does Not Earn

- No live Codex Stop-gating evidence.
- No behavior lift, output-quality lift, paired comparison, Codex App parity, or
  shipping promotion.
- No permission to tune task-standard text, Stop text, SRE law, selector
  thresholds, hidden-verifier boundaries, or task-identity triggers.

## Next Move

Queue `codex-app-cli-task-standard-stop-gating-live-run`. The next seam should
run the already-built live mode only with explicit current-turn approval:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_APPROVED=approved python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-stop-gating-live
```

That live run should record whether a real Codex CLI turn uses captured
standards at Stop without overclaiming behavior lift.
