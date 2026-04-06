# CORTEX_V2_LIVE_SERVICE_PROOF_0

Date: 2026-04-07
Status: active canonical-truth service-proof note with OpenAI-only product scope re-earned on the current line

## Purpose

This note records the canonical live-runtime truth lane for Cortex v2.
That reset contract is already landed on local `main`; this note preserves the canonical truth lane and the current machine's current-scope service truth honestly.

Under the R1 reset:

- `service_api` is the canonical runtime truth lane
- `execution_surface = direct_api`
- `evidence_role = canonical_truth`

Signed-in CLI/operator evidence may remain useful for watchlisting and falsification work, but it does not count as canonical runtime truth by itself.

## Capable-machine entry condition

Actual service proof belongs only on a machine that satisfies all of:

- clean synced `main`
- automation auth readiness reads `ready` for the intended provider
- explicit spend approval env is present where required
- the current repo and local live-validation tooling are available unchanged

If those conditions are not met, the lawful outcome is `blocked` or `partial`, not “implemented anyway.”

## Auth policy

- Claude automation:
  - `ANTHROPIC_API_KEY`
- Gemini automation:
  - `vertex_adc` first
  - `GEMINI_API_KEY` second
- OpenAI automation:
  - `OPENAI_API_KEY`

Signed-in CLI sessions do **not** count as service-lane auth.

## Current local state

Current local machine state on the accepted current line:

- Claude automation auth: `missing`
- Gemini automation auth: `missing`
- OpenAI automation auth: `ready`
- the current direct-service proof tool records:
  - `execution_surface = direct_api`
  - `evidence_role = canonical_truth`
- the current direct-service proof tool now exposes:
  - `service_smoke`
  - `service_restart_continuity`
- `current`
  - `suite_role = readiness_probe`
  - current probe surface only
- `canonical_anchor`
  - `suite_role = canonical_truth_anchor`
  - accepted current product scope: `openai`
  - dormant future host-expansion plumbing: `claude`
  - scenarios:
    - `pass_minimal`
    - `truth_gap`
    - `restart_continuity`
- current OpenAI service-probe model policy:
  - `service_smoke` may use `gpt-5.4-mini` as the cheaper direct-API probe
  - `canonical_anchor` scenarios stay on `gpt-5.4`
- OpenAI canonical anchor status on this machine:
  - cycle 1: positive
  - cycle 2: positive
  - cycle 3: positive
  - `pass_minimal`: positive three times
  - `truth_gap`: `truthful_incomplete` three times
  - `restart_continuity`: positive three times
- the first canonical three-scenario API truth anchor is therefore re-earned for current OpenAI-only product scope on this machine through three positive current-machine `canonical_anchor` cycles
- the accepted OpenAI-only product runtime on that scope now runs on the compact `openai_product_journal` carrier plus the exact outward `decision + journal` projection
- Claude host-expansion proof remains blocked honestly on missing auth readiness, but it no longer blocks the current product scope
- Gemini remains watchlist-only until its direct API/service lane is explicitly opened

## Reset law

- No future product/runtime claim may land from CLI-only proof.
- A host may be called re-earned only after repeat-stable service/API confirmation on the canonical suite.
- Once a canonical API truth lane exists, CLI/operator instability becomes watchlist evidence unless it exposes a direct contradiction in the canonical runtime path.

## Next lawful move

1. open the bounded `X2` OpenAI-only support/eval compression train on clean `main`
2. keep `claude` as future host-expansion plumbing only until a later explicit host-expansion train is opened
3. keep `gemini` watchlist-only until direct API/service auth exists
4. keep headless-CLI reruns downstream of canonical truth as watchlist-only diagnostics

Do not use CLI fallback to fake service proof.
