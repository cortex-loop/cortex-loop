# CORTEX_V2_CAUSAL_MAP_NOTE_0

Surface: lab

- train_name: `causal-contribution-map-openai`
- final_decision: `none`

## Component classifications

- none recorded
  - the deterministic E18 layer is green on `review/e18-causal-contribution-map`, but the live causal-map train has not completed yet on this branch
  - current pause point:
    - earlier pause artifacts remain preserved under `.cortex/live_validation/output_quality/openai/run_20260409T072136+0000`, `.cortex/live_validation/output_quality/openai/run_20260409T073300+0000`, and `.cortex/live_validation/output_quality/openai/run_20260409T074914+0000`
    - current deeper pause artifacts:
      - fresh rerun E12 baseline completed under `.cortex/live_validation/output_quality/openai/run_20260409T085424+0000` with `19` written `result.json` artifacts
      - `visible_contract_binding = off` initial rerun completed under `.cortex/live_validation/output_quality/openai/run_20260409T090634+0000` with `19` written `result.json` artifacts
      - `visible_contract_binding = off` repeat rerun completed under `.cortex/live_validation/output_quality/openai/run_20260409T092159+0000` with `19` written `result.json` artifacts
      - the next follow-on run was intentionally stopped under `.cortex/live_validation/output_quality/openai/run_20260409T093800+0000` after `1` written `result.json` artifact so the seam could pause again without losing evidence

## Next lawful move

the service-api E18 execution path is now frozen on the current review branch. do not resume the API train unless `CORTEX_LIVE_SERVICE_SPEND_APPROVED=1` is set explicitly.

next:

1. keep the preserved API artifacts above as historical partial evidence only
2. use the new `lab/cortex_output_quality.py --surface operator_cli` bridge to establish an OpenAI watchlist-native E12 baseline
3. extend the OpenAI verified-work/O4R side onto a CLI/watchlist surface before re-opening a full causal-map train
