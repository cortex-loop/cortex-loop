# CORTEX_V2_MEDIATION_HOST_REALIZATION_PROGRAM_0

Date: 2026-03-31
Status: active runtime-program brief for the first bounded experimental mediation slice

## Purpose

This document opens the first actual mediation train after the accepted `J3` justification review.

The chosen next move is:

- one reference-host-only acceptance lane for the first mediation implementation,
- one SRE-only, experimental / off-by-default host-realization mediation slice,
- one bounded path that keeps commitment truth, packet publication meaning, branch law, and uncertainty law fixed,
- and one explicit stop before branch-control mediation, uncertainty/brake mediation, multi-host rollout, support-memory runtime, or AUX/runtime widening.

This document does not authorize:

- branch-discipline or thrash mediation as the first code seam,
- uncertainty/brake mediation as the first code seam,
- generic cross-family score soup,
- Core or AUX packet changes,
- service/auth work,
- named-model routing,
- or pooled multi-host mediation summaries.

## Planning seam classification

This program-lock seam is `non-load-bearing`.

Correspondence impact: none expected.
Reason: this slice locks the first mediation train, but it does not yet land a new runtime object, operator, code home, or read/write path.

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `main`
- commit: `b025eb5fe572932a52e4efd16b424ecdc0e40872`

Why this program opens now:

- `J3` already justifies one bounded experimental mediation seam and explicitly says the next lawful move is planning and implementing that seam rather than reopening evidence collection by inertia,
- the strongest-supported first implementation target is host-realization rather than branch or uncertainty mediation,
- host-realization is the smallest defensible first train because the counted comparator law already preserves packet truth, contradiction/degradation preservation, truthful-withheld meaning, and selected-family truth while changing only direct host-native opportunity specialization,
- and the reference host is the right first acceptance lane because it is deterministic, already has the cleanest paired host-realization evidence surface, and avoids hiding host differences behind pooled cross-host summaries.

## Strongest-supported first seam

The first mediation implementation should be a **host-realization seam**, not a branch-control seam and not an uncertainty/brake seam.

Mechanically, the first train should:

- keep family-level neutral-dominance law intact,
- keep branch and uncertainty law intact,
- and introduce only one bounded experimental finalization step at the host-opportunity layer.

The target delta is the same delta already used by the counted reference host-realization pairs:

- selected family remains `seek-context`,
- the host-opportunity set still contains `mcp.query`,
- and the only mediated delta is that direct host-native opportunity specialization becomes live and explicit when the opportunity is clearly superior.

This is the cleanest defensible first train because it preserves the current SRE stack instead of reopening the whole control loop.

## Locked scope

This program remains:

- reference-host only for acceptance truth,
- SRE-only,
- experimental / off-by-default,
- packet-subordinate,
- sparse,
- host-aware,
- anti-hub,
- and contradiction-preserving.

This program adds only:

- one bounded `seek-context` reachability adjustment on explicit missing-context / missing-capability pressure, starting with admissibility and widening only to the smallest pre-finalization scoring delta if admission alone still leaves `neutral` selected,
- one bounded experimental `Finalize^{exp}` step at the host-opportunity selection layer,
- one explicit mediation config/flag that defaults to identity / disabled,
- and one nested runtime diagnostic surface for mediation-active versus identity behavior.

This program keeps fixed:

- commitment truth,
- provenance sufficiency,
- blockedness,
- hard boundaries,
- observe/bind meaning,
- branch/pending-goal law,
- uncertainty/brake law,
- `alpha_t`,
- `activation_threshold`,
- existing public reference runtime shell shape,
- and packet publication meaning.

## Runtime law for this program

Current-scope mediation law for this train is the narrowest lawful discrete equivalent of `Q_t^{base} -> Q_t^{final}`:

1. keep the current family-level allocation and neutral-dominance law intact by default;
2. if no lawful reference path can currently reach `seek-context`, first admit `seek-context` only on explicit missing-context / missing-capability pressure in the reference lane;
3. if builder-side admission alone still leaves `neutral` selected, allow only the smallest pre-finalization scoring delta needed to make the same explicit-pressure runtime path reachable;
4. if the experimental mediation flag is disabled, `Finalize^{exp}` remains identity;
5. if the flag is enabled and the already-selected family is `seek-context`, allow one bounded host-realization finalization step over the existing host-opportunity set;
6. direct specialization is lawful only when a realizable `HostNativeOpportunity` for `seek-context` is marked `clearly_superior`;
7. if the preferred opportunity is unrealizable, keep family truth explicit and surface degradation/fallback through the existing opportunity-specialization law;
8. do not generic-reweight `branch`, `check`, `brake`, or `neutral` as part of this first train.

This means the first train may change:

- whether `seek-context` becomes admissible on the reference lane under explicit missing-context pressure,
- whether the same explicit-pressure runtime path also requires a minimal pre-finalization scoring delta to overcome neutral dominance,
- whether `seek-context` remains a generic family choice or becomes a direct `mcp.query` nomination,
- and whether that experimental direct specialization is recorded explicitly in runtime diagnostics.

It may not change:

- commitment truth,
- branch trajectory law,
- brake thresholds,
- or any host surface outside the bounded reference acceptance lane.

## Public runtime contract

No new public shells are introduced.

The public surface remains:

- `python3 -m cortex.runtime.reference_cli`

No new top-level runtime fields or top-level `control_ledger` keys should be introduced for this first train.

If runtime projection changes at all, it must remain nested under `control_ledger.allocation_diagnostics`.

Current-scope mediation diagnostics may include only:

- `mediation_active`
- `mediation_identity`
- `selected_family_before_finalization`
- `selected_family_after_finalization`
- `preferred_opportunity_ref`
- `direct_opportunity_specialization_used`
- `mediation_reason_tags`

Those diagnostics remain runtime-local truth.
They are not packet truth, continuation truth, or publication truth.

## Planned load-bearing seam classification

`J4B` is `load-bearing` on the current review line.

Purpose:

- make the current reference lane reach `seek-context` lawfully under explicit missing-context / missing-capability pressure,
- and keep that change inside the smallest bounded pre-finalization adjustment that changes runtime behavior.

Current review-line implementation result on the current line:

- the builder now admits `seek-context` into the family mask and top-family set only on exact `missing-capability`, `capability-view-missing`, or `execution-trace-missing` pressure while generic host friction remains closed,
- the scorer now uses the same exact-pressure predicate rather than a generic `*-missing` heuristic and gives `seek-context` the smallest route-local lift that clears neutral dominance on the real guarded capability-gap path without touching `alpha_t` or `activation_threshold`,
- the reference runtime lane now selects `seek-context` end-to-end on the capability-view-missing path while generic host friction still remains neutral/brake dominated,
- and the current host-realization comparator evidence still bypasses runtime selection because `J4C` remains unopened.

Delivered Correspondence impact for `J4B` on the current review line:

- updated the `X_t^{ref}` / `build_reference_executive_state()` row so explicit missing-context / missing-capability pressure can lawfully admit `seek-context`,
- updated the `Q_t^{online}(a)` / `Q_t^{alloc}(a)` realization row so the same exact-pressure path now clears neutral dominance on the runtime lane without touching threshold or vigor law,
- confirmed the existing `U_t^{sre}` / `select_reference_soft_control()` row remains the pre-finalization selection owner in `J4B`,
- and confirmed the existing `Adm_r^{pre}` / `specialize_host_native_opportunity()` row remains unchanged in `J4B`.

Do not open `Q_t^{final}` inside `J4B` just to compensate for a pre-selection reachability gap.

`J4C` is `load-bearing`.

Purpose:

- land the off-by-default experimental mediation finalizer,
- keep selected-family truth explicit before and after finalization,
- and surface only nested runtime-local mediation diagnostics.

Planned Correspondence impact for `J4C`:

- add one new `Q_t^{final}(a)` experimental mediation-finalizer row with its exact code home and test surface,
- update the `U_t^{sre}` / `select_reference_soft_control()` row so it explicitly includes the off-by-default mediation finalizer path,
- confirm the existing `Adm_r^{pre}` / `specialize_host_native_opportunity()` row remains the owner of direct opportunity nomination rather than channel realization.

If the implementation cannot name the exact correspondence rows for the opened stage before code lands, that stage is not ready.

## Program order

This train is split into six bounded stages:

1. `J4A` program lock, workstream sync, and acceptance-law pin
2. `J4B` bounded reference-lane `seek-context` reachability seam, starting with admissibility and widening only if required for a real runtime path
3. `J4C` experimental mediation-finalizer carrier and nested diagnostics
4. `J4D` reference runtime projection and deterministic re-audit
5. `J4E` optional proven-lane OpenAI projection only if `J4D` lands cleanly and the PHI loop still passes
6. `J4F` closeout or rollback-to-disabled state if the train drifts or fails to show a defensible behavioral consequence

Every load-bearing stage must end on a clean tree before the next opens.

## Test and rerun contract

Minimum deterministic proof for each opened load-bearing stage:

- `python3 -m pytest tests/unit/test_sre_opportunities.py -q`
- `python3 -m pytest tests/unit/test_reference_executive_builder.py -q`
- `python3 -m pytest tests/unit/test_reference_runtime_scoring.py -q`
- `python3 -m pytest tests/unit/test_reference_runtime_step.py -q`
- `python3 -m pytest tests/unit/test_correspondence_sre.py -q`
- `python3 -m pytest tests/unit/test_verification_docs_sync.py -q`

If a new deterministic runtime-side packet/example surface is introduced for this train, it must also gain a committed doc/example test pair in the same slice.

## Acceptance gates

The first mediation train is only honestly landed when all are true:

- mediation remains disabled / identity by default,
- reference acceptance truth stays reference-only unless a later stage explicitly widens it,
- `seek-context` becomes reachable only under explicit missing-context / missing-capability pressure, using the smallest pre-finalization reachability adjustment the runtime lane actually requires,
- direct host-native opportunity specialization becomes live only when `mcp.query` is clearly superior,
- selected-family truth remains explicit before and after finalization,
- commitment truth and packet publication meaning remain unchanged,
- the train does not generic-reweight all families or collapse into a hub score,
- no new top-level runtime shell or top-level `control_ledger` shape is introduced,
- the correspondence rows for the opened stage are updated exactly,
- and the targeted deterministic bundle passes twice.

## Explicitly blocked moves

This train does not authorize:

- branch or thrash mediation as the first code seam,
- uncertainty/brake mediation as the first code seam,
- pooled multi-host mediation summaries,
- live/provider mediation,
- Core widening,
- AUX runtime widening,
- support-memory runtime,
- named-model routing,
- or a generic weighted-soup finalizer over every family.

## Current review-line state after J4B implementation

On the current review line after `J4B`:

- the first mediation train is pinned as a reference-host host-realization slice,
- `J4B` now exists as a bounded runtime reachability seam on the current review line: exact missing-context / missing-capability pressure now admits and selects `seek-context` on the reference runtime lane,
- generic host friction still does not open the `seek-context` route,
- the current host-realization comparator evidence still bypasses runtime selection because `J4C` remains closed,
- and runtime code plus correspondence rows now exist on the current review line only while accepted baseline truth on `main` remains pre-`J4B`.
