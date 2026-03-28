# CORTEX_V2_THEORY_2

Status: non-authority working memo
Date: 2026-03-21

## Scope

This file is not an authority surface.
It is a short evidence-first memo for choosing the next plan without reopening feature work by accident.

Active authority remains:

1. `docs/CORTEX_V2_CORE_2.md`
2. `docs/CORTEX_V2_SRE_2.md`
3. `docs/CORTEX_V2_AUX_2.md`
4. `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
5. `docs/CORTEX_V2_PHASE_GATES_2.md`
6. `docs/V1_CODE_PORT_DETERMINATION.md`
7. `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Current repo evidence

- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md` says the current v2 roadmap is complete at the justified boundary.
- `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md` says mediation is still `not justified yet`.
- `docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md` shows cell-level signal on thrash, uncertainty, and host-realization, but every package-level axis remains `insufficient`.
- `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md` says the active follow-on campaign is verification ergonomics, not new architecture or runtime behavior.
- `pytest.ini`, `Makefile`, and `docs/CORTEX_V2_LOCAL_VERIFICATION.md` now provide repo-local verification entry points, including `make verify`, `make test-smoke`, evidence revalidation commands, and mediation evidence revalidation commands.
- `.coveragerc` and `make coverage` now exist, but `python3 -m coverage` is not installed in the current environment.
- Correspondence drift already has mechanical test surfaces in:
  - `tests/unit/test_correspondence_contract.py`
  - `tests/unit/test_correspondence_core.py`
  - `tests/unit/test_correspondence_ports.py`
  - `tests/unit/test_correspondence_sre.py`
  - `tests/unit/test_correspondence_periphery.py`

## Exact stale facts that matter

- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md` still says there is no repo-local pytest config, but `pytest.ini` exists.
- the same status note still says there is no repo-local coverage configuration, but `.coveragerc` exists.
- the same status note still records the old closeout counts:
  - unit: `136 passed`
  - integration: `16 passed`
  - import smoke: `16 passed`
  - full suite: `152 passed`
- current repo-local verification surfaces are substantially larger:
  - `make test-smoke`
  - `make verify`
  - packet-example revalidation commands
  - latency revalidation commands
  - mediation evidence revalidation commands
- `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md` still describes E1, E2, and E3 as future work in places even though large parts of those surfaces are already landed.

## What this means

- Do not open a new feature seam from this file.
- Do not use this file to justify mediation.
- Do not add new theory machinery, scoring formulas, or confidence claims.
- Prefer the smallest verification-ergonomics seam that improves trust in the landed repo.

## Most effective next plan

The most effective next plan is:

### Verification Ergonomics Truth-Sync

Goal:
- resync the active status and planning documents to the repo that now exists,
- then lock the next verification-ergonomics seam against that refreshed truth.

Why this wins now:
- the live repo has moved past parts of the current status text;
- planning from stale closeout text is more dangerous than the remaining technical gaps;
- the feature roadmap is already closed, so the highest-leverage work is keeping verification authority honest and current.

Why this is more effective than any new feature seam:
- it reduces governance drift before more docs and evidence are layered on top of stale statements;
- it lowers the chance of selecting the wrong next seam from outdated roadmap text;
- it improves every later verification-ergonomics seam without touching runtime behavior.

## Evidence for choosing this plan

- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md` still says there is no repo-local coverage configuration, but `.coveragerc` now exists.
- the same status note still reports the old closeout test counts, while the current canonical verification bundle is much larger.
- `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md` still presents early verification seams as the first recommendation, but repo-local verification commands, correspondence checks, packet-example revalidation, latency revalidation, and mediation evidence revalidation are already landed.
- `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md` and `docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md` still block mediation at package level, so more theory or more mediation implementation planning would drift from active evidence.

## First seam inside this plan

### Verification Closeout Resync

Target outcome:
- one honest status sync across:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_LOCAL_VERIFICATION.md` only if wording drift remains
- one explicit statement of what is already landed in verification ergonomics
- one explicit statement of what is still missing

Exact touch surface:
- status-note maintainability-debt section
- status-note verification snapshot section
- verification-ergonomics plan phase ordering and first-recommended-seam wording where it is now historically stale
- local-verification wording only if it still mismatches the actual `Makefile` entry points

Required edits:
- replace the stale "no repo-local pytest config" statement with the current truth
- replace the stale "no repo-local coverage configuration" statement with the current truth
- keep the "coverage tool not installed in the current environment" statement unless that environment fact changes in the same seam
- replace old verification counts with the current committed repo-local bundle results, or explicitly reframe them as historical closeout counts if the note should preserve history
- update the verification-ergonomics plan so E1 is treated as effectively landed, E2 is partially landed, and the next recommended seam becomes the first still-unfinished high-leverage gap rather than the first historical gap

Acceptance criteria:
- a new reader cannot infer that `pytest.ini` or `.coveragerc` are missing
- a new reader cannot infer that mediation is newly justified
- a new reader can see that the feature roadmap is closed and verification ergonomics is the active campaign
- the next seam recommended by the docs matches the highest-leverage unfinished verification gap

Required truth after the seam:
- feature roadmap remains closed at the current justified boundary
- mediation remains blocked and unjustified
- verification ergonomics remains the active follow-on campaign
- repo-local verification commands, correspondence checks, and evidence revalidation surfaces are recorded as landed where true
- coverage support is recorded accurately:
  - repo-local config exists
  - repo-local command exists
  - tool is not installed by default in the current environment
  - no coverage gate or baseline artifact exists yet unless one is added in the same seam

Out of scope:
- Core / SRE / AUX behavior changes
- mediation work
- host behavior changes
- runtime dedup

Verification for this seam:
- readback of all touched docs against:
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_LOCAL_VERIFICATION.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_MEDIATION_EVIDENCE_NOTE_0.md`
- `git diff --check`

## Next seam after the resync

If the truth-sync seam lands cleanly, the next best seam is:

### First Coverage Baseline Artifact

Goal:
- finish the remaining high-value part of E2 without changing behavior.

Why it is next:
- E1 is effectively landed.
- correspondence drift detection is already real.
- packet and evidence revalidation paths are already real.
- the remaining missing verification surface with the highest leverage is a committed first coverage baseline artifact built from the existing `.coveragerc` and `make coverage` path.

Current blocker:
- the current environment does not have `python3 -m coverage`.

Exact plan shape:
- do not change runtime behavior
- do not add a coverage threshold
- do not treat first coverage numbers as a feature gate
- either:
  - install the documented coverage prerequisite in the environment and record the first baseline honestly, or
  - keep the environment unchanged and land only the truth-sync seam first

Minimum success condition:
- coverage can be run locally from repo-local config,
- the prerequisite is stated plainly,
- and the first committed baseline, if added, is treated as hygiene evidence rather than a feature gate.

## Why not other plans first

- Not mediation: active package evidence still says `insufficient`.
- Not new host work: all three current hosts are already landed at the justified boundary.
- Not more theory: the packet and evidence surfaces already decide the next move.
- Not dedup first: dedup is lower leverage until the status and verification truth are fully synchronized.

## End state this memo is aiming at

The next work should make the repo easier to trust, easier to revalidate, and harder to misdescribe.

That means:
- accurate status surfaces,
- accurate verification instructions,
- accurate evidence boundaries,
- and no accidental reopening of feature work.

## Final recommendation

If one seam is chosen next, choose:

1. `Verification Closeout Resync`

If two seams are chosen in order, choose:

1. `Verification Closeout Resync`
2. `First Coverage Baseline Artifact`

Do not choose a new feature seam before those two are either landed or explicitly rejected by new authority or new evidence.
