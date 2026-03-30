# CORTEX_V2_OPERATOR_DIRECTIONALITY_AUDIT_0

Date: 2026-03-29
Status: accepted paired raw-vs-Cortex operator directionality audit note

## Purpose

This note records the first paired raw-vs-Cortex operator directionality audit on the current machine.
It is an evaluation/support surface only.
It does not authorize runtime-doctrine changes, service proof, support-memory runtime, or mediation work.

The audit now distinguishes:

- quality failure
- burden / efficiency
- provider-limit interference

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

## Round 2 Stable-Defaults Rerun

Round 2 reran the operator audit under a stricter cross-host contract:

- Claude stayed on the normal headless print surface with the current explicit stable model
- Gemini stayed on the headless CLI default auto route with no explicit `-m` model argument
- OpenAI stayed on the current `codex exec` smoke / `codex app-server` lifecycle split with the current explicit stable model

Round 2 result:

- Claude: `positive`
- OpenAI: `positive`
- Gemini: `blocked`
- package verdict: `mixed_direction`

Current reading:

- the earlier Gemini `plan`/named-model confounds were real and are now removed
- but the true `auto` route on the free API-key lane still blocks repeated paired runs with `quota_exhausted`
- so the remaining Gemini problem is now more honestly a stability/quota problem on the real default path, not a harness-side model chase

## S1 Routing Candidate

On the review branch, the first SRE-owned operator route selector now sits above the live harness and governs:

- route profile
- retry budget
- continuity budget
- verification requirement
- and explicit blockedness under observed host friction / quota pressure

Under the corrected reducer and fresh closure rerun, the current review-branch audit now returns:

- Claude: `negative`
- OpenAI: `positive`
- Gemini: `positive`
- package verdict: `not_yet_positive`

Current reading:

- the earlier branch-local `promising_positive` line was an overclaim and is now withdrawn
- Gemini remains positive on the current audit surface without named-model fallback or `plan`-mode confounds
- OpenAI remains positive on the same isolated App Server surface
- Claude is now the real blocker:
  - one fresh `pass_minimal` pair is negative because `raw_host` completed while the hook-backed `cortex_operator` lane returned a rate-limit result and made no change
- so the next honest move is not publication as package-positive and not more widening
- the next honest move is one narrow Claude explanation seam for the negative `pass_minimal` pair on the hook-backed lane

## S1G Provider-Limit Neutrality Candidate

The current explanation branch hardens the audit further:

- Anthropic `"You've hit your limit"` results are now normalized as provider-limit interference
- one-sided provider-limit hits are now treated as non-comparable blocking evidence rather than automatic directional loss
- pair order now alternates by repeat index to reduce shared-budget bias
- the merged comparator summary now rebuilds from provider-local summaries instead of preserving stale merged truth
- local artifacts now expose:
  - `token_usage_visible`
  - `input_tokens`
  - `output_tokens`
  - `cache_tokens`
  - `provider_limit_interference`
  - `provider_limit_kind`
  - `comparison_contaminated`

Current local neutrality-hardened reread:

- Claude: `positive`
- Gemini: `positive`
- OpenAI: `positive`
- package verdict: `promising_positive`

Current reading:

- the earlier apparent Claude regression was mostly an evidence problem:
  - one-sided provider usage-window interference had been read as a true negative
  - after neutrality hardening and the Claude efficiency seam, Claude is now positive again on the current local audit
- the OpenAI explanation seam then removed the real continuity transport artifact:
  - the directionality harness now starts the first App Server continuity turn with `thread_ephemeral: false`
  - `no rollout found for thread id` is now normalized as `continuity_rollout_missing`
  - fresh OpenAI reruns now land `restart_continuity` positively on both variants
- the Claude efficiency seam then re-earned the remaining host line:
  - lower scenario-specific Claude turn caps are now in place for the audit lane
  - SessionStart no longer injects meaningless `{}` into Claude context
  - the candidate Claude audit hook surface now omits `Stop`
  - fresh Claude reruns land all three scenarios positively without provider-window contamination
- so all three hosts are now positive on the current candidate branch
- the next honest move is to publish/review this branch as the candidate package-positive operator directionality line rather than widen further
