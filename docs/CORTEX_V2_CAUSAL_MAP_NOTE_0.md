# CORTEX_V2_CAUSAL_MAP_NOTE_0

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

resume from this review branch by rereading the pause artifacts above, then either:

1. rerun `python3 tools/cortex_train_loop.py --train causal-contribution-map-openai` cleanly from the start, or
2. open a tiny evaluation-only resume/caching seam first, because the current E18 train loop does not yet support mid-run resume and the full causal map is too expensive to finish comfortably in one interactive pass
