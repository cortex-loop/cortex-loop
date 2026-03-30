# CORTEX_V2_OPERATOR_ROUTING_PROGRAM_0

Date: 2026-03-30
Status: active runtime-program brief for the first bounded SRE-owned operator routing train

## Purpose

This document opens one bounded SRE + harness train after the first round-2 stable-headless audit setup.

The chosen next move is:

- one SRE-owned operator route selector over low-dimensional task-state geometry,
- one bounded route/budget layer for headless operator testing,
- one all-host operator realization over Claude, Gemini, and OpenAI,
- and one explicit stop before model picking, service/auth widening, AUX activation, mediation, or Core changes.

This document does not authorize:

- named model routing,
- Core packet changes,
- AUX support-memory work,
- mediation work,
- or phase-gate promotion from operator-eval results alone.

## Locked contract

This train is:

- **SRE + harness**, not Core, not AUX,
- operator-only,
- route/budget selection only,
- no named-model selection,
- no service/auth widening,
- and contradiction-preserving.

Locked host defaults:

- Claude: normal `claude -p` headless path with the explicit stable GA model
- Gemini: `gemini -p` with no explicit `-m` model argument
- OpenAI: current `codex exec` smoke / `codex app-server` lifecycle split with the explicit stable model

Locked route profiles:

- `inspect_light`
- `execute_standard`
- `execute_guarded`
- `continuity_standard`
- `continuity_guarded`
- `blocked`

Locked state axes:

- task complexity
- continuity demand
- verification demand
- uncertainty
- host friction
- quota pressure

## First math realization

The route selector uses:

- a bounded task-state vector `z_t = [c_t, k_t, v_t, u_t, h_t, q_t]`
- fixed route prototypes for the five non-blocked profiles
- fixed axis weights over those six dimensions
- explicit gain priors
- one discrete gate against the task-mode default profile
- one hard quota-pressure block for non-inspect routes
- and one resumptive guarded-continuity preference under strong host friction

The route selector may choose:

- route profile
- retry budget
- continuity budget
- verification requirement
- and explicit blockedness

It may not choose:

- named models
- host surfaces beyond the already-locked OpenAI split
- service/auth strategy
- or packet-level commitment truth

## Integration target

The first implementation must integrate the route selector into:

- `tools/live_provider_baselines.py`
- `tools/live_host_native_product_paths.py`
- `tools/live_operator_directionality.py`

Required local artifact diagnostics:

- `route_profile`
- `route_budget`
- `route_reason_tags`
- `state_vector`
- `quota_pressure`
- `host_friction`
- `blocked_reason`

These diagnostics are local-only under `.cortex/live_validation/`.
They are not packet truth and may not be promoted into runtime/public doctrine by this train alone.

## Test and rerun contract

Minimum deterministic proof:

- `python3 -m pytest tests/unit/test_operator_routing.py -q`
- `python3 -m pytest tests/unit/test_live_validation_tools.py -q`
- `python3 -m pytest tests/unit/test_correspondence_sre.py -q`
- `python3 -m pytest tests/unit/test_verification_docs_sync.py -q`

Minimum live rerun:

- `make live-preflight`
- `make live-preflight`
- `make live-provider-baselines`
- `make live-operator-directionality`
- `make live-operator-directionality-audit`

Acceptance:

- no operator path silently falls back to another named model
- Gemini remains no-`-m` and no-`plan` on the operator/eval path
- Claude/OpenAI remain on the locked stable host defaults
- blocked results are explicit and attributable to route state / host state rather than hidden rerouting
