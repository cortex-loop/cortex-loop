# CORTEX_V2_OPERATOR_DIRECTIONALITY_SCENARIO_CATALOG_0

Date: 2026-04-06
Status: accepted watchlist scenario catalog for the raw-vs-Cortex operator audit

## Common contract

- variants:
  - `raw_host`
  - `cortex_operator`
- host coverage:
  - `claude`
  - `gemini`
  - `openai`
- execution classification:
  - `execution_surface = headless_cli`
  - `evidence_role = watchlist`
- same host surface, same task, same starting workspace, same model policy where possible
- Gemini may use `auto|minimal|wrapped` only as harness-side falsification tooling
- if raw contamination cannot be neutralized safely, mark the pair blocked instead of comparing dishonestly

## Scenario inventory

### `pass_minimal`

- task: fix `src/normalize_port.py` so `65535` is accepted

### `truth_gap`

- task: inspect but do not edit or test

### `restart_continuity`

- task:
  - turn 1: identify the smallest fix only
  - turn 2: resume and apply exactly that fix

## Publication law

This catalog supports operator watchlisting only.
It does not by itself authorize canonical runtime claims.
