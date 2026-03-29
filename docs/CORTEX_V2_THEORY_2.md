# CORTEX_V2_THEORY_2

Status: non-authority working memo
Date: 2026-03-26

## Scope

This file is not an authority surface.
It is a short evidence-first memo for choosing the next plan without widening scope by accident.

Active authority remains:

1. `docs/CORTEX_V2_CORE_2.md`
2. `docs/CORTEX_V2_SRE_2.md`
3. `docs/CORTEX_V2_AUX_2.md`
4. `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
5. `docs/CORTEX_V2_PHASE_GATES_2.md`
6. `docs/V1_CODE_PORT_DETERMINATION.md`
7. `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Current repo evidence

- The accepted workflow baseline is the clean synced `main` line recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`.
- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md` says the current v2 roadmap is complete at the justified boundary.
- `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md` says mediation is still `not justified yet`.
- `docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md` shows cell-level signal on thrash, uncertainty, and host-realization, but every package-level axis remains `insufficient`.
- `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md` still defines the active non-feature follow-on campaign.
- `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md` now records the bounded K train as landed, records `N2` as blocked pending a capable machine, and records the landed `Q1` directionality audit: Claude and OpenAI are positive, Gemini is mixed, and the next honest move is a narrow Gemini explanation seam rather than further widening.
- The current Gemini auth-path recheck also says not to overread a settings-only API-key switch: on the current CLI, headless operator reruns still require `GEMINI_API_KEY` in the shell environment before new Gemini directionality evidence can be collected honestly.
- `pytest.ini`, `Makefile`, and `docs/CORTEX_V2_LOCAL_VERIFICATION.md` now provide repo-local verification entry points, including `make verify`, `make test-smoke`, evidence revalidation commands, and mediation evidence revalidation commands.
- `.coveragerc`, `make coverage`, and `docs/CORTEX_V2_COVERAGE_BASELINE_NOTE_0.md` now exist as repo-local coverage hygiene surfaces.

## What this means

- Do not open a new feature seam from this file alone.
- Do not use this file to justify mediation.
- Do not add new theory machinery, scoring formulas, or confidence claims.
- Prefer the smallest verification-ergonomics or evidence seam that improves trust in the landed repo.

## Working conclusion

The next honest work remains whichever explicitly bounded seam the active workstream records next, with strong bias toward the smallest truthful move.

1. broader evidence collection where package-level mediation blockers remain real,
2. later non-feature verification cleanup where a new explicit seam is justified,
3. or a separately scoped bounded runtime/product follow-on train when the active workstream has already opened one.

Do not use this memo to justify:

- mediation implementation,
- new runtime/product behavior,
- packet reinterpretation,
- or authority-surface widening.
