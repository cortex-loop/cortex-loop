# CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE

Date: 2026-03-24
Status: `not justified yet`

## Scope

This note records the last accepted Phase 16A justification decision only.
It does not start mediation implementation.
It does not track later candidate or post-closeout mediation evidence; use `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md` and the mediation evidence package surfaces for that later branch truth.

## Authority audited

- `docs/CORTEX_V2_SRE_2.md`, Section 9
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Packet and plan guardrails

The active packet and plan already constrain mediation tightly:

- mediation is `experimental / off-by-default`
- mediation is not constitutional and not required for lawful SRE
- mediation is not required for MVP runtime
- mediation may not affect commitment truth
- mediation may only modify `Q_t^{base}` into `Q_t^{final}`
- mediation must remain sparse, host-aware, and neutral-dominance-preserving
- mediation must satisfy the anti-hub law
- the implementation plan says not to skip straight to mediation

## Evidence audit

Phase 16 was only warranted if the repo already showed measurable lift on at least one required axis.
At the time of this accepted audit, repo evidence was insufficient on every required axis:

| Required lift | Current repo state | Audit result |
| --- | --- | --- |
| reduced thrashing | Reference, Gemini, and OpenAI thrash comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| better branch discipline | Reference, Gemini, and OpenAI thrash comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| better uncertainty handling | Reference, Gemini, and OpenAI uncertainty comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| lower visible burden at equal task value | Reference, Gemini, and OpenAI thrash now carry burden cell-level signal, but that evidence remains too narrow at package level because it is confined to the `thrash_control` scenario family. | insufficient evidence |
| better host-specialized realization | Three reference-only mediation-specific host-realization pairs are now recorded, three Gemini-only pairs are now recorded, and three OpenAI-only pairs are now recorded, but the package-level evidence still remains too narrow. | insufficient evidence |

## Decision

At that accepted audit point, Phase 16 mediation was `not justified yet`.

The accepted audit line had:

- packet permission for a later experimental mediation extension, and
- live experimental evidence on several cells, but no package-level evidence strong enough to justify mediation.

Because that accepted evidence was still too narrow at package level, mediation should remain unstarted.
Three positive thrash-host burden cells did not justify package-level burden promotion by themselves because they still came from one scenario family only.
Do not open a mediation implementation seam until broader comparative evidence is strong enough at package level, not just on isolated cells.
The required comparative evidence plan is recorded in `docs/CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md`.
Later candidate evidence may change the blocker shape, but that requires a dedicated follow-on justification update rather than reinterpreting this accepted audit note.
