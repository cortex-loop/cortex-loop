# CORTEX_V2_OPERATOR_ROUTING_PROGRAM_0

Date: 2026-03-30
Status: accepted watchlist/reference brief for the first bounded SRE-owned operator routing train

After accepted X1, this document remains watchlist/reference only.
It is not part of the accepted OpenAI-only product runtime path.

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
- one compact executive summary over observable control inputs
- one compact tonic executive modulator bundle over that summary
- one compact executive policy view derived from summary + modulators
- fixed route prototypes for the five non-blocked profiles
- fixed axis weights over those six dimensions
- explicit gain priors
- one discrete gate against the task-mode default profile
- one hard quota-pressure block for non-inspect routes
- and one resumptive guarded-continuity preference under strong host friction

The summary layer uses:

- `S_t = [u_t, f_t, q_t, c_t, n_t, v_t]`
- bounded observable inputs only
- no hidden reward memory

The modulator layer uses:

- the current summary plus bounded prior tonic state
- fixed coefficients and fixed persistence
- hard clipping into `[0,1]`
- four tonic gains:
  - `focus_gain`
  - `explore_gain`
  - `stop_pressure`
  - `update_pressure`

The policy layer uses:

- one compact `ExecutivePolicyView`
- `default_profile_bonus`
- `switch_margin`
- `stop_threshold`
- `allow_extra_read_pass`
- `verification_intensity`

The route selector may choose:

- route profile
- retry budget
- continuity budget
- verification requirement
- and explicit blockedness

Budget note:

- `route_budget.max_turns` is the outer harness turn budget
- host-specific transport caps may still exist separately
- this train only claims host transport control where it is actually wired

The modulator layer may change:

- preference for default / continuity profiles
- the margin needed to switch away from default profile
- blocking pressure under quota / repeated failure
- one extra read pass on inspect routes when uncertainty is high and quota pressure is low

The policy layer is the only place where those behavior consequences should be expressed.

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
- `modulator_summary`
- `modulator_memory`
- `modulator_state`
- `modulator_reason_tags`
- `policy_view`

These diagnostics are local-only under `.cortex/live_validation/`.
They are not packet truth and may not be promoted into runtime/public doctrine by this train alone.

## Test and rerun contract

Minimum deterministic proof:

- `python3 -m pytest tests/unit/test_operator_routing.py -q`
- `python3 -m pytest tests/unit/test_sre_executive_summary.py -q`
- `python3 -m pytest tests/unit/test_sre_modulators.py -q`
- `python3 -m pytest tests/unit/test_sre_policy_view.py -q`
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
- the compact modulator bundle is SRE-owned, operational, and visibly changes route/budget behavior
- the executive summary, tonic modulator memory, and policy view are all explicit typed SRE objects
- the implementation stays abstract and does not use neurotransmitter names as code objects
