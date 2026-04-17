# V2/V3 Deterministic Parity Proof — 2026-04-17

## Surface under test
3 template surfaces × 5 row types (instructions, input text, repair ticket,
verification on V2 fixture, verification on V3 fixture) = 15 parity rows.
Harness: lab/v3/parity.py. Oracle: lab/v3/parity_oracle.py.

## Canonical format
V3's repair ticket follows the canonical spec documented at the head of
cortex_v3/verifier.py::build_verified_work_repair_ticket: alphabetically
sorted list fields (P2), derived falsified_checks (P3), fixed field order
(P4), "<none>" for empty lists (P5). V2 currently satisfies the same spec,
which the parity harness cross-validates by emitting identity rows on all
three repair_ticket cells.

## Decision rule for future V2/V3 divergences
Each parity row carries a `classification` field:
- `identity`: byte-for-byte equal. No action.
- `semantic`: different information content. V3 must close unless V3's
  content is demonstrably better, in which case a separate sprint narrows V2.
- `cosmetic-canonical`: same information, different surface form, both
  stable. Adopt the canonical form on both sides; write the canonical
  spec down as code-adjacent documentation.
- `redundancy-wart`: one side emits information that is redundant with
  another field. Narrow that side in a separate sprint.

Future divergences do not automatically trigger a full sprint. They are
classified first; the class determines whether action is needed.

## Actual outcome
divergence_count = 0. All 15 rows classified `identity`.
Fix is implemented in cortex_v3/verifier.py::build_verified_work_repair_ticket
with the module-level canonical-spec comment and the _falsified_checks
helper. No V2 code changed.

## What earns, what does not
Earns: V3 emits the canonical repair-ticket format across all three
templates; V2 cross-validates that it emits the same canonical form today.
Does not earn: any claim about V3 producing equal-or-better live model
behavior vs V2. That requires provider API keys in the executor
environment and is only the next experimental follow-up for this seam.
The repo's active train remains the V2 brake-tonic quiescence exit reconciliation.

## Recommendation for next V3 experimental sprint: v3-live-measurement-with-keys
Blocker: the Codex executor environment does not have OPENAI_API_KEY,
ANTHROPIC_API_KEY, or GEMINI_API_KEY exported. To unblock, the user must
either:
  1. Export one or more of those variables into the Codex session before
     launching the next sprint, OR
  2. Run `python3 -m lab.v3.measure --mode live --trials 10 --providers <p>
     --output tests/evidence/<date>_v3_first_measurement.json` locally and
     commit the output file via a review branch. The existing measure.py
     driver already handles all three providers; no code change required.

Once keys are present OR evidence is user-generated, the next V3 experimental
sprint closes out by aggregating rows into a 3×3 provider×template pass-rate
table and committing a decision note that compares verified_with_repair to
plain_feedback. This does not supersede the repo-wide active train.
