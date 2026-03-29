# CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0

Date: 2026-03-29
Status: accepted paired raw-vs-Cortex operator directionality audit note

## Purpose

This note records the first paired raw-vs-Cortex operator directionality audit on the current machine.
It is an evaluation/support surface only.
It does not authorize runtime-doctrine changes, service proof, support-memory runtime, or mediation work.

## Package verdict

**mixed_direction**

Reason:

- Claude is directionally positive on the current paired operator audit
- OpenAI is directionally positive on the current paired operator audit
- Gemini is mixed rather than cleanly positive on the current paired operator audit

So the current repo does not look directionally wrong on operator output quality, but the package direction is not yet clean enough to justify further widening by inertia.

## Host summary

### Claude

- raw baseline isolation: `--setting-sources local`
- `pass_minimal`: positive
- `truth_gap`: positive
- `restart_continuity`: positive
- host verdict: `positive`

Current reading:
- Cortex matches raw-host task value and truth discipline.
- Cortex preserves stronger lifecycle visibility through the current hook-backed lane.
- No hidden burden inflation appeared in the current paired series.

### Gemini

- raw baseline isolation: same CLI surface without project-level hook injection
- `pass_minimal`: positive
- `truth_gap`: mixed
- `restart_continuity`: positive
- host verdict: `mixed`

Current reading:
- Cortex does not look directionally wrong on Gemini.
- But one `truth_gap` pair preserved the same truthful incomplete outcome with higher burden than raw-host.
- Gemini therefore remains the host that blocks a clean package-positive directionality claim.

### OpenAI

- raw baseline isolation: `codex app-server` with isolated `CODEX_HOME` carrying only `auth.json`
- `pass_minimal`: positive
- `truth_gap`: positive
- `restart_continuity`: positive
- host verdict: `positive`

Current reading:
- Cortex matches raw-host task value and truth discipline.
- Cortex preserves stronger lifecycle visibility on the same App Server surface.
- No hidden burden inflation appeared in the current paired series.

## Blocker statement

The current blocker to further widening is not service proof and not the K train.
It is the mixed Gemini operator directionality result.

The next honest move is one narrow explanation seam:

- determine whether the mixed Gemini result reflects:
  - true Cortex-added burden,
  - host-capacity noise,
  - or audit-measurement noise

Do not widen runtime doctrine until that is clearer.

## Later Gemini vanilla rerun

A later Gemini-only rerun on the free API-key lane removed one real confound:

- the comparison baseline no longer forces `plan` mode on the first continuity turn
- one-off vanilla headless reruns can complete `pass_minimal`, preserve `truth_gap`, and resume `restart_continuity`

But the bounded paired rerun still did not produce a clean host-positive result:

- `pass_minimal` improved relative to the older `plan`-confounded path but still carried higher burden on repeated pairs
- `truth_gap` and `restart_continuity` were quickly re-blocked by free-tier quota exhaustion under repeat load

So the honest host line remains `mixed`.
The confound was real, but removing it did not by itself clear Gemini to package-positive directionality.
