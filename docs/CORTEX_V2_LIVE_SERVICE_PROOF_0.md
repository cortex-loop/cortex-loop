# CORTEX_V2_LIVE_SERVICE_PROOF_0

Date: 2026-04-06
Status: active canonical-truth service-proof contract with current-machine blocker note

## Purpose

This note records the canonical live-runtime truth lane for Cortex v2.
That reset contract is already landed on local `main`; this note preserves the canonical truth lane and the current-machine blocker honestly.

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

Current local machine state at the R1 reset:

- Claude automation auth: `missing`
- Gemini automation auth: `missing`
- OpenAI automation auth: `missing`
- current-machine service truth is therefore blocked honestly on auth readiness
- the current direct-service proof tool records:
  - `execution_surface = direct_api`
  - `evidence_role = canonical_truth`
- the current direct-service proof tool still only covers:
  - `service_smoke`
  - `service_restart_continuity`
- the first canonical three-scenario API truth anchor remains a later bounded seam:
  - `pass_minimal`
  - `truth_gap`
  - `restart_continuity`
- until that later seam is implemented and rerun on a capable machine, no host is re-earned on the canonical runtime lane

## Reset law

- No future product/runtime claim may land from CLI-only proof.
- A host may be called re-earned only after repeat-stable service/API confirmation on the canonical suite.
- Once a canonical API truth lane exists, CLI/operator instability becomes watchlist evidence unless it exposes a direct contradiction in the canonical runtime path.

## Next lawful move

On a capable machine:

1. re-earn the first API truth anchor on `openai`
2. add `claude` if auth is ready
3. keep `gemini` watchlist-only until direct API/service auth exists
4. keep headless-CLI reruns downstream of canonical truth as watchlist-only diagnostics

Do not use CLI fallback to fake service proof.
