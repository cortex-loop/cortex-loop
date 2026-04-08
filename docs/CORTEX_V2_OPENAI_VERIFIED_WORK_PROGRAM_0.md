# CORTEX_V2_OPENAI_VERIFIED_WORK_PROGRAM_0

Date: 2026-04-08
Status: accepted bounded runtime-program brief for the first verified-work restoration slice; `O4R` remains partial on the current line

## Purpose

This document opens one bounded larger-task restoration slice inside the accepted OpenAI host-control family.

The chosen move is:

- keep the accepted thin `O4` path unchanged when no `work_contract` is present,
- add one optional request-scoped `work_contract`,
- bind external verification into runtime truth,
- allow at most one runtime-driven repair turn,
- and keep the resulting lane explicitly outside the current canonical-anchor proof bundle until local value is re-earned.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0.md`
- `docs/CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- the accepted X1/X2 OpenAI-only product shell plus the keep/cut/restore decision recorded in `docs/CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md`

Why this program opens now:

- larger-task exploratory runs showed that prompt shaping is the wrong axis,
- the shared missing mechanism is runtime-native verification truth rather than more support doctrine,
- one bounded `work_contract` is smaller and more lawful than a second large task-specific subsystem,
- and OpenAI is the only accepted live product host today, so it is the first lawful realization surface.

## Locked scope

This program remains:

- OpenAI only as the first host realization
- one optional extension of the existing `POST /v1/actions/response-stream` family
- request-scoped rather than persisted executive state
- `full_files` only
- one deterministic verifier profile only: `python_workspace_pytest_v1`
- one repair budget only: `0 | 1`
- packet-subordinate and host-specific at the adapter layer

This program adds only:

- shared `WorkContract`
- shared `VerificationOutcome`
- shared `choose_verified_work_followup()`
- optional `request.work_contract` on `OpenAIHostControlRequest`
- `run_openai_runtime_verification_step()`
- deterministic `full_files` parsing plus the bounded bookmarks verifier
- one native `previous_response_id` continuation on the verified-work path

This program does **not** authorize:

- prompt rewriting
- hidden build briefs
- automatic carrier selection
- diff-based verified-work carriers
- repeated-failure `AttemptRelation` / NoGo promotion
- tools or tool-result submission
- cancel/update lanes
- remote hosting
- multi-session or multi-client doctrine
- Gemini or Claude rollout
- generic runtime/service abstraction
- runtime AUX activation
- offline consolidation
- or broader product claims beyond this bounded verified-work lane

## Public contract

The public endpoint and action tag remain unchanged:

- `POST /v1/actions/response-stream`
- `action_tag = "openai-response-stream"`

When `request.work_contract` is absent:

- behavior remains the accepted thin `O4` text-only path

When `request.work_contract` is present:

- accepted keys are exactly:
  - `allowed_write_paths`
  - `verification_profile`
  - `output_carrier`
  - `max_repair_turns`
- `output_carrier` must be `full_files`
- `verification_profile` must be `python_workspace_pytest_v1`
- `max_repair_turns` must be `0` or `1`
- caller-supplied `instructions` are rejected because the verified-work instructions are fixed by the runtime

Verified-work output protocol:

- file blocks only:
  - `=== FILE: relative/path ===`
  - `<full file contents>`
  - `=== END FILE ===`
- or one blocked marker only:
  - `=== BLOCKED: needs_user_input ===`
  - `<message>`
  - `=== END BLOCKED ===`
  - `=== BLOCKED: unsafe_request ===`
  - `<message>`
  - `=== END BLOCKED ===`
- no prose
- no code fences
- no model-run tests

When verified-work is active, the result payload may additionally include:

- `verification`
- `attempt_count`

## Runtime law for this program

The verified-work lane may:

- keep the original user `input` literal
- inject only the fixed mechanical `full_files` protocol instructions
- parse returned file blocks or blocked markers
- verify the result externally against the bounded bookmarks workload
- bind that `VerificationOutcome` into `OpenAIRuntimeSession.last_failure_class`
- drive `next_recommended_move` through `choose_verified_work_followup()`
- and perform exactly one native continuation attempt when runtime truth says `repair` and budget remains

It may not:

- widen runtime persistence beyond the compact `openai_product_journal`
- turn diagnostic SRE modulators into the live loop driver
- invent a second host-control family
- widen into a generic planner or generic verifier framework
- or silently promote local exploratory value checks into canonical runtime proof

## Proof boundary

This program is intentionally outside the current compact canonical proof bundle:

- `L3`, `L6C`, and `canonical_anchor` remain unchanged in this train
- the verified-work lane is deterministic-test-covered and locally rerunnable
- live larger-task value checks remain local exploratory evidence until the row is re-earned repeat-stably

## Acceptance gates

`O4R` is only honestly closed when all are true:

- the default thin `O4` path remains unchanged when no `work_contract` is present
- verified-work requests bind external verification into runtime truth
- runtime truth, not a benchmark-local controller, decides whether the repair turn happens
- only one repair turn is possible
- deterministic tests and repo-local revalidation pass
- repeated local bookmarks reruns show the runtime-driven one-repair path is not worse than one-shot and yields at least one failure-to-pass repair
- and the `O4R` phase-gate row is updated truthfully

## Current state on the accepted line

On the current line:

- the shared verified-work law is implemented
- the shared verified-work runtime helpers now live in the neutral `cortex/runtime/verified_work_runtime.py` home
- the OpenAI host-control family now accepts an optional bounded `work_contract`
- external verification now updates runtime truth through `run_openai_runtime_verification_step()`
- the verified-work path can perform exactly one native continuation attempt
- the default thin `O4` path remains unchanged when `work_contract` is absent
- deterministic tests and repo-local revalidation are real
- the corrected tri-brain conformance rerun removed Gemini's false raw-JSON-wrapper `output_invalid` classification without widening shipping truth
- but `O4R` remains partial because live larger-task lift has not yet been re-earned repeat-stably

## Explicitly blocked moves

This program does not authorize:

- prompt shaping
- hidden implementation preferences
- automatic carrier selection
- diff-based verified-work carriers
- repeated-failure inhibition promotion
- multi-host rollout
- or canonical-anchor widening
