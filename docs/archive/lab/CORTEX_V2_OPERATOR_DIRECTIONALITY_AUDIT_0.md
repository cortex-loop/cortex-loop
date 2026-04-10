# CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0

Surface: lab

Date: 2026-04-06
Status: accepted watchlist note for paired raw-vs-Cortex operator directionality

## Purpose

This note records the meaning of the operator directionality audit after the R1 reset.

The operator audit is:

- `execution_surface = headless_cli`
- `evidence_role = watchlist`
- useful for packaging/confound detection and wrapper-burden falsification
- not canonical runtime truth

## Current accepted reading on `main`

On the accepted line, operator evidence remains informative but non-authoritative.

- Claude: positive watchlist signal
- OpenAI: positive watchlist signal
- Gemini: unresolved watchlist signal on the accepted line

This does **not** mean the canonical runtime layer is negative.
It means the headless-CLI watchlist still contains unresolved host-boundary noise.

## Review-branch evidence rule

Archived Gemini recoveries, including the preserved `archive/review--gemini-cause-proof` tag, remain non-authority evidence until they are re-earned under the reset contract.

Do not read branch-local operator positives as accepted product truth.

## Next lawful use

Use this audit to answer narrow questions such as:

- is the wrapper adding burden on a given host?
- is the comparison contaminated by packaging or baseline setup?
- did a host default path drift?
- do current local watchlist readings drift from the accepted watchlist line?

Do not use this audit alone to publish runtime payoff claims.
