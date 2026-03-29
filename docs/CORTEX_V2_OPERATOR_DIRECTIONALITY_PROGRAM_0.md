# CORTEX_V2_OPERATOR_DIRECTIONALITY_PROGRAM_0

Date: 2026-03-29
Status: accepted re-audited evaluation brief for the first raw-vs-Cortex operator directionality audit

## Purpose

This document opens one evaluation-only train after the bounded K train closeout.

The chosen next move is:

- one cross-host raw-vs-Cortex operator comparison,
- one paired-run harness over the already-landed operator surfaces,
- one audit that asks whether Cortex is improving actual outputs rather than only adding mechanism,
- and one explicit stop before service proof, support-memory runtime, mediation, or runtime-doctrine changes.

This document does not authorize:

- service/auth work,
- support-memory runtime,
- mediation work,
- runtime semantics changes,
- or phase-gate promotion from evaluation results alone.

## Locked comparison contract

This audit is:

- operator-only on the current machine,
- raw-host vs Cortex-operator,
- same host surface for both variants,
- same scenario,
- same starting workspace,
- same model policy where possible,
- and contradiction-preserving.

Locked variants:

- `raw_host`
- `cortex_operator`

Locked hosts:

- Claude signed-in CLI
- Gemini signed-in CLI
- OpenAI signed-in `codex app-server`

Locked scenarios:

- `pass_minimal`
- `truth_gap`
- `restart_continuity`

Locked minimum evidence:

- `3` paired runs per host per scenario

## Truth law

- If a raw baseline cannot be isolated safely, mark it `blocked_raw_baseline_contaminated`.
- Do not smooth blocked or mixed host results into package-level positivity.
- Do not credit signed-in operator truth as service proof.
- If the audit shows mixed or negative directionality, record that directly and treat it as the blocker to further widening.
