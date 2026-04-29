# Cortex Runtime Context Eval Rubric

Surface: product eval artifact.

This document is not Cortex mission authority. `docs/CORTEX.md` remains
the canonical mission and model-I/O authority. This rubric exists only to
score whether the `CORTEX_RUNTIME_CONTEXT_V1` bridge improves a model
call relative to an unshaped baseline.

## Scope

Use this rubric for paired baseline-vs-shaped comparisons where the only
intended difference is that the shaped call receives a bounded runtime
context block derived from the immediately prior
`ReferenceRealizationFeedback`. Do not use it to claim broad model lift,
cross-host parity, or post-training improvement.

The shaped output wins only when:

- shaped total score is at least 2 points higher than baseline, and
- no single axis regresses by more than 1 point.

If the shaped call changes wording but not task outcome, score it as no
meaningful change.

## Scoring Axes

| Axis | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Premature closure | Finalizes despite missing evidence, continuity, or context. | Hedges about uncertainty but still closes too early. | Refuses closure and names the missing check or missing context. | Performs or requests the needed check, then closes only if evidence supports it. |
| Evidence recovery | Provides no evidence or only a generic assertion. | Says it should verify, but does not identify the missing evidence. | Identifies the missing evidence class, failed probe, or absent artifact class. | Produces/checks concrete evidence, or asks for the exact missing input needed to proceed. |
| Goal continuity | Drifts to a different task or optimizes the wrong outcome. | Mentions the goal generically without preserving the immediate next step. | Preserves the immediate goal and a plausible next action. | Preserves the goal, the prior failure signal, and the correct next action. |

## Scoring Procedure

1. Read the current input and the immediately prior feedback signal.
2. Score the baseline output on all three axes.
3. Score the shaped output on all three axes.
4. Compute total scores out of 9.
5. Mark shaped as a win only if it meets the win rule above.
6. Mark shaped as a regression when its total is lower or any axis
   regresses by more than 1 point.
7. Mark shaped as no meaningful change when the text changes but the
   total does not improve by at least 2 points.

## Forbidden Claims

- Do not count shorter output, more cautious tone, or mention of Cortex
  as lift.
- Do not count route/block/closure changes as model-visible improvement
  unless the shaped request text reached `input`, `instructions`, or an
  equivalent host-visible text field.
- Do not claim live output lift from fixture-body tests; fixtures earn
  structural request-shaping proof only.
