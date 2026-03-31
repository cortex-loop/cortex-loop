# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline commit lookup: `git rev-parse HEAD` on clean synced `main`
- Accepted baseline note:
  - exact accepted-head hashes are intentionally not mirrored in repo-tracked support docs because they self-stale on the next accepted closure commit
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - mediation is now justified for one bounded experimental seam, and the full first bounded reference mediation train `J4B/J4C/J4D/J4F` is now landed on the accepted line
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - accepted workflow baseline truth now rests on `main` rather than a long-lived working branch
  - final repo closure is now landed on the current line:
    - one clean synced local checkout only
    - one local branch only: `main`
    - no attached non-root worktrees
    - no residual local non-main branches
    - no remote `review/*` heads
    - retired non-main lines preserved under pushed `archive/final-repo-closeout/*` tags
  - `N1` service-lane proof is now landed for current machine truth:
    - automation preflight reruns remain all-`missing`
    - automation baseline reruns now block honestly on readiness rather than faking direct network probes
    - service-lane reruns remain all-blocked on `auth_missing`
    - operator proof remains the accepted current line and is preserved in compare/audit support surfaces when this seam reruns automation-only artifacts
  - `K4` bounded computed executive loop is now landed on the proven reference/OpenAI lanes:
    - `alpha_t` is computed from runtime-visible pressure rather than fixed
    - `Q_t^{mem}` remains `0.0`
    - `allocated_score` can differ from `online_score`
    - selection now runs on allocated-score semantics
    - the existing public runtime projection shapes remain unchanged
  - the bounded K train is now landed on the proven reference/OpenAI lanes:
    - `activation_threshold` is now feedback-conditioned rather than fixed to budget-band baseline alone
    - bounded prior-feedback pressure is now explicit through internal `feedback_pressure_tags`
    - guarded-feedback and latched-brake realization remain explicit rather than smoothing selected-family, realized-family, or lawful commitment truth
    - no support-memory runtime, mediation, service/auth widening, or broader host rollout was introduced
  - `M2` is now landed on the canonical line:
    - `ExecutiveSignalSummary`
    - persistent tonic `ExecutiveModulatorMemory`
    - `ExecutivePolicyView`
    - live `modulator_summary`, `modulator_memory`, and `policy_view` diagnostics on the operator path
    - the stop-threshold law is now decoupled from self-referential `stop_pressure` comparison
  - `J1` is now landed on the canonical line:
    - one checked mediation evidence package now exists on `main`
    - package verdict remains `insufficient` on every mediation axis
    - the remaining mediation gap is now explicit rather than rhetorical
    - J2 rerun targets are now recorded without opening mediation implementation
  - `J2` is now landed on the canonical line:
    - dedicated branch-discipline families now exist on `reference`, `openai`, and `claude`
    - dedicated non-thrash burden families now exist on `reference`, `openai`, and `claude`
    - the first Claude host-realization line is now committed on the canonical line
    - package-level evidence is no longer `insufficient` everywhere:
      - reduced thrashing is `candidate_positive`
      - better branch discipline is `candidate_positive`
      - lower visible burden at equal task value is `candidate_positive`
      - better host-specialized realization is `candidate_positive`
      - better uncertainty handling remains `insufficient`
    - J2 now serves as the historical enabling evidence later accepted by J3
  - `J3` is now landed on the canonical line:
    - mediation is now justified for one bounded experimental seam
    - better uncertainty handling remains `insufficient`, but that gap is explicit and non-blocking for one first bounded seam
    - at `J3` acceptance time the next lawful move became one bounded experimental SRE-only mediation seam rather than reopening evidence collection by inertia
  - `J4` bounded reference mediation closeout is now landed on the canonical line:
    - `J4B`: exact missing-capability / missing-context pressure now admits `seek-context` in `X_t^{ref}`
    - `J4B`: the same exact-pressure predicate now makes `seek-context` beat neutral on the real guarded capability-gap path while generic host friction still does not open the route
    - `J4C`: `ReferenceMediationMode` defaults to identity, experimental mode finalizes only already-selected `seek-context`, and `Q_t^{final}(a)` is now implemented as an explicit bounded SRE-owned finalizer
    - `J4D`: the committed reference baseline/mediated packet examples plus the host-realization comparator now use the real runtime path rather than a specialization-only helper
    - `J4F`: workflow truth, phase-gate truth, correspondence truth, and branch truth now match on clean synced `main`
    - non-reference mediated artifacts remain evidence-only and `J4E` is explicitly declined for the current closeout
  - `Q1` raw-vs-Cortex operator directionality audit is now landed on the current machine:
    - Claude is `positive`
    - OpenAI is `positive`
    - Gemini is `mixed`
    - package verdict is `mixed_direction`
    - the current blocker is now the mixed Gemini directionality result rather than an abstract “evaluate later” placeholder
  - Gemini restart-continuity repeat-stability re-audit is now landed for current machine truth:
    - local Gemini settings already match current best practice:
      - no pinned default model
      - `modelRouting=true`
      - explicit project-scoped resume IDs remain valid on the current CLI
    - the Gemini continuity harness now preserves repeated continuity artifacts instead of overwriting them
    - the first inspect-only Gemini continuity turn now uses `plan` approval mode and the resumed edit/test turn keeps `yolo`
    - current local Gemini continuity truth remains mixed on `auto`:
      - successful resumed completions exist
      - first-turn `capacity_exhausted` failures still recur
    - an exploratory `gemini-2.5-flash` sidecar also failed on first-turn `capacity_exhausted`
    - the remaining Gemini continuity blocker now looks host-capacity-driven rather than a settings or resume-semantics mistake
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, bounded outbound OpenAI host-control lane, and explicit executive allocation diagnostics remain accepted on the current line
  - the Gemini documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Gemini host-control lane remain accepted on the current line
  - the Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane remain accepted on the current line
  - refreshed live models on the current line are `claude-sonnet-4-6`, `gemini-2.5-pro`, and `gpt-5.4`
  - `R6`, `R7`, `R8`, `R9`, `O5`, `O6`, `O7`, `O8`, `G1`, `G2`, `G3`, `G4`, `A1`, `A2`, `A3`, and `A4` are landed on the current line
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `No active mediation seam; first bounded reference mediation closeout landed`
- Current working branch at ledger update: `main`
- Current branch role: clean synced resting branch after merged `J4` closeout and `cleanup-report`
- Current candidate seam: `none open`
- Current seam status: the first bounded reference mediation train is now accepted baseline truth on `main`: `J4B` exact-pressure `seek-context` reachability is landed, `J4C` identity-default reference finalization is landed, `J4D` runtime-backed reference packet/comparator evidence closure is landed, and `J4F` workflow/authority closure is landed. Reference lifecycle surfaces advertise bounded `mcp.query` affordance truth, the runtime derives the typed host opportunity set from lifecycle-visible data rather than tests, and nested mediation diagnostics remain live under `control_ledger.allocation_diagnostics.mediation`.
- the reference-only acceptance boundary remains explicit: non-reference mediated artifacts remain evidence-only, `J4E` is explicitly declined for current closeout unless a later post-closeout review reopens a real truth gap, and `N2` remains a separate capable-machine blocker rather than part of this train.
- the compare surface and live-validation truth from earlier seams remain accepted ancestor input and are not being reopened after this landed `J4` closeout.
- Seam risk: none active; last closed seam was a deterministic code/doc seam

## 3. Next lawful move

- Current blocker shape:
  - there is no open `J4` mediation blocker on accepted baseline truth
  - service-lane `N2` remains blocked on a capable machine and is not part of the current mediation closeout
  - non-reference mediated artifacts remain evidence-only and must not be upgraded inside this train
- Next lawful move:
  - keep the first bounded reference mediation train closed on clean synced `main` unless a new bounded program explicitly reopens it
  - do not open `J4E` absent a real post-closeout truth gap on the already-proven OpenAI lane
  - continue non-mediation follow-on work on its own authority surface rather than treating mediation as partially open

## 4. Explicitly blocked moves

- Do not treat signed-in provider CLI sessions as equivalent to the automation credentials the current A4 / G4 / O4 service paths require.
- Do not flatten provider auth into a generic shared credential broker.
- Do not shell out from current A4 / G4 / O4 transports to provider CLIs without an explicit host-owned re-audit.
- Do not treat the new OpenAI App Server operator proof as license to reopen v1 assisted mode, bounded corrective retry, or App Server bridge doctrine inside `L2b`.
- Do not flatten Claude/Gemini hook events into a fake OpenAI-style lifecycle vocabulary or vice versa.
- Do not reopen K3 into new executive-allocation widening beyond the accepted current-scope law.
- Do not open support-memory runtime, mediation / `Q_t^{final}` experimentation, tool-result submission, multimodal widening, runtime AUX activation, offline consolidation, or generic reward-learning doctrine from `L2`.
- Do not keep repo-tracked live artifacts under `docs/live_validation/`; live machine output is local-only now.
- Do not interpret the current Gemini operator-lane instability as proof that the signed-in-first design is wrong; it is a host/watchlist issue until repeated reruns say otherwise.
- Do not overread ephemeral OpenAI `thread/read` emptiness as if the App Server lifecycle proof failed; for current scope the event timeline is the authoritative lifecycle surface and the persisted thread view remains a caveat.
- Do not silently discard Gemini capacity warnings when a run otherwise succeeds; preserve them as warnings rather than pretending the host was perfectly stable.
- Do not silently reintroduce a pinned Gemini operator model as the default testing start point; current local truth is that CLI auto mode is the intended default.
- Do not pass explicit Gemini operator model names anywhere on the operator/evaluation harness; let the installed CLI default auto route decide.
- Do not silently promote `gemini-2.5-pro` from exploratory sidecar to closure-path truth while it is still capacity-blocked on smoke.
- Do not treat selecting `gemini-api-key` in `.gemini/settings.json` as sufficient for headless Gemini operator proof; the current CLI still requires `GEMINI_API_KEY` in the shell environment or a loaded `.env`.
- Do not use Gemini `plan` mode as the default comparison baseline on the operator/evaluation path.
- Do not use Gemini `plan` mode as the default comparison baseline on the free API-key operator lane; it changes the routed quota/model path and contaminates the audit.
- Do not reopen Gemini model chasing or assisted-mode speculation inside the active `L4` service-proof train.
- Do not shell out from service transports to provider CLIs.
- Do not overread the current auto-mode improvement as full Gemini closure while `restart_continuity` is still not repeat-stable.
- Do not overread provider-limit interference as a product-quality defeat for Cortex by itself.
- Do not widen `K4` into support-memory runtime, mediation, service/auth work, or broader host rollout.
- Do not unfreeze threshold law in `K4`; the current budget-band activation-threshold law stays fixed.
- Do not widen the landed K train into support-memory runtime, mediation, vigor scaling, service/auth work on this machine, or broader host rollout.
- Do not implement mediation in `J3`; this seam is justification/workflow/evidence interpretation only.
- Do not treat `J3` as license for broad rollout, default-on mediation, live/provider mediation, Core widening, or AUX runtime widening.
- Do not widen `J4` into branch/thrash mediation, uncertainty/brake mediation, or pooled cross-host mediation before the reference host-realization slice is either landed or rejected.
- Do not let `J4` generic-reweight every family or collapse into a hub-style mediation score; the first train must stay sparse and host-realization-specific.
- Do not let `J4` alter observe/bind meaning, packet publication meaning, or commitment truth to make mediation look better.
- Do not pretend a builder-only `seek-context` mask widening is sufficient if the runtime lane still selects `neutral` under the accepted threshold law.
- Do not reintroduce a generic `*-missing` `seek-context` heuristic; keep the exact runtime-visible pressure tags explicit.
- Do not reintroduce extra long-lived local worktrees or non-main branch residue without an explicit new seam.
- Do not leave remote `review/*` heads behind after future publication cleanup.

## 5. Acknowledged worktree noise at ledger creation

- `.cortex/live_validation/` now contains local-only generated evidence for the current L2 pass and is expected to churn across reruns.
- Re-read `git status --short --untracked-files=all` before opening any new seam; this summary is only the continuity reminder, not the canonical file list.

## 6. Resume checklist

Before resuming or opening work:

1. Read `AGENTS.md`.
2. Read this workstream ledger.
3. Read the accepted-baseline authority anchors listed in Section 1.
4. Run `git branch --show-current`.
5. Run `git status --short --untracked-files=all`.
6. Compare the current repo state against the accepted baseline and current seam state recorded here.
7. Restate:
   - accepted baseline branch and commit
   - current seam status
   - next lawful move
   - blocked moves
   - acknowledged workspace noise
8. If the ledger and repo state disagree, record or resolve that drift before widening scope.

## 7. Update triggers

Update this ledger in the same slice whenever any of these change:

- accepted baseline branch or commit
- current campaign
- current seam or seam status
- next lawful move
- blocked moves
- acknowledged worktree noise

Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth.
