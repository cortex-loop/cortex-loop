# Cortex V3

Surface: experimental

`cortex_v3/` is the in-repo incubation track for a parallel verified-work library.

Current V3 scope:
- shared provider-neutral verified-work contracts, preservation law, verifier runner, and engine
- thin OpenAI, Claude, and Gemini adapters
- self-contained repair turns with full visible workspace context and narrowed write authority
- no runtime imports from V2 `cortex.runtime`, `cortex.sre`, or `cortex.aux`
- no V2 host-event runtime shell, ledger, or telemetry ported forward

Current V2/V3 boundary:
- V2 remains the shipped `cortex` package and the repo's shipping truth
- V3 is an extraction seam that must earn any future cutover through replay and verification evidence
- multi-provider support remains explicit in V3 through separate thin adapters, not fake host uniformity
- repair stays fully self-contained across providers; there is no continuation-token dependency in the V3 engine

Proof surface:
- `tests/v3`
- `lab/v3`
