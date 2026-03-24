# CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE

Date: 2026-03-24
Status: `not justified yet`

## Scope

This note closes the Phase 16A justification audit only.
It does not start mediation implementation.

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

Phase 16 is only warranted if the repo already shows measurable lift on at least one required axis.
Current repo evidence is insufficient on every required axis:

| Required lift | Current repo state | Audit result |
| --- | --- | --- |
| reduced thrashing | Reference, Gemini, and OpenAI thrash comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| better branch discipline | Reference, Gemini, and OpenAI thrash comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| better uncertainty handling | Reference, Gemini, and OpenAI uncertainty comparisons now exist and produce cell-level signal, but package-level evidence remains too narrow. | insufficient evidence |
| lower visible burden at equal task value | Reference and Gemini thrash now carry burden cell-level signal, but package-level burden evidence remains too narrow. | insufficient evidence |
| better host-specialized realization | Three reference-only mediation-specific host-realization pairs are now recorded, three Gemini-only pairs are now recorded, and three OpenAI-only pairs are now recorded, but the package-level evidence still remains too narrow. | insufficient evidence |

## Decision

Phase 16 mediation is `not justified yet`.

The repo currently has:

- packet permission for a later experimental mediation extension, and
- live experimental evidence on several cells, but no package-level evidence strong enough to justify mediation.

Because that evidence is still too narrow at package level, mediation should remain unstarted.
Do not open a mediation implementation seam until broader comparative evidence is strong enough at package level, not just on isolated cells.
The required comparative evidence plan is recorded in `docs/CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md`.
