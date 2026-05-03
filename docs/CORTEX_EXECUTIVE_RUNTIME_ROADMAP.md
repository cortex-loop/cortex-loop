# Cortex Executive Runtime Roadmap

Surface: product planning

This roadmap is the execution plan from current Cortex to the intended product:
a runtime executive-function layer around models. It is subordinate to
`docs/CORTEX.md` for identity, `internal/truth/cortex_status.json` for current
operational truth, and `docs/CORTEX_EXECUTIVE_RUNTIME_TRACKER.md` for the live
achievement scoreboard. It is not a second registry and does not change
shipping truth by itself.

The detailed research and engineering contract for the first runtime-control
program lives in `docs/CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md`. This roadmap
orders the work; the program spec defines the first control objects,
transitions, metrics, and falsification tests.

## Point B: Product Goal

Cortex should be a runtime executive-function layer for models, not a Claude
hook plugin, not a translation system, and not a middleware pile. In shorter
terms: Cortex is not a Claude hook plugin.

The target behavior is what a strong human executive system does around
cognition:

- hold the real task thread when the model drifts;
- remember what is still open without turning into generic memory;
- notice when the model is claiming more than it has evidence for;
- slow the model down when uncertainty, contradiction, or failure appears;
- preserve the parts of work that are verified instead of letting repair
  destroy them;
- surface blockers and unfinished obligations before fluent closure hides
  them;
- adapt to the host/model/tool affordances instead of pretending all brains
  are the same;
- intervene only when doing so improves the model's next input or output.

The center is:

```text
Cortex should shape the model's behavior at runtime so the model acts with
better executive function than it would unaided.
```

Sometimes that means speaking to the model. Sometimes it means blocking.
Sometimes routing. Sometimes preserving state. Sometimes doing nothing because
the model is already handling the task correctly.

The communication problem matters because, when Cortex does speak, it has to
speak in a form the model can integrate. But communication is not the whole
product. It is the model-visible edge of the executive layer.

The desired runtime loop is:

```text
Model/host event happens
-> Cortex understands the task-state and executive risk
-> Cortex decides whether intervention is useful
-> Cortex chooses the right control mode:
   - stay silent
   - route/degrade/block
   - preserve verified work
   - ask for evidence
   - surface a blocker
   - reflect an unsupported claim back to the model
-> the model's next behavior is better grounded, more continuous, and less falsely complete
```

The strange-loop communication frame applies only when the right intervention
is model-visible self-correction. Cortex should not sound like alien machinery
then; it should help the model see its own task-state mismatch from inside the
conversation. But not all of Cortex should be "via ego." Some Cortex should
remain invisible executive control. The model does not need route pricing,
brake EMA, support priors, session IDs, internal tags, schema names, or hook
mechanics. It needs the behavioral consequence.

When Cortex does speak, the model-visible surface must follow the
Model-Visible Cortex Output Law in `docs/CORTEX.md`: no outside reviewer,
no third-agent "Cortex says" voice, no generic second-person advice, no
internal vocabulary, and no hidden verifier answer. The text must make an
executive constraint explicit inside the model's own task frame: closure is
not yet warranted, evidence is missing, an obligation remains open, or a
bounded self-check follows from the model's prior act. Same-thread resumed
turns may use first-person self-check only when there is a clear prior-act
anchor; attached-context surfaces use impersonal executive-constraint
language.

## Point A: Current State

Current shipping truth remains `openai.codex_app_cli`. Current live evidence
on that product family uses the transitional `codex_exec_wrapper_resume`
actuator; queued product work targets hook-native lifecycle control so Cortex
can act before or at model-turn closure rather than only after a completed run.
The OpenAI API path remains conformance/support unless explicitly promoted.

Claude Code Desktop is a recon/proving surface, not shipping truth. It has
earned important brain-wiring facts:

- `Stop` can carry a block reason to the model and has narrow behavior-lift
  evidence for false-closure repair.
- Raw internal Cortex vocabulary in `Stop` output can be treated as suspicious
  or prompt-injection-shaped, so internal tags must not leak model-visibly.
- `PreToolUse` and `UserPromptSubmit` delivery are real, but tested
  exact-output-conflict content did not earn behavior lift.
- `PostToolUseFailure` delivery and persistence are real, but the
  PostToolUseFailure-to-Stop loop produced mixed behavior.
- Headless Claude Code is useful for some lower-cost Stop research, but
  parity with the Mac app is partial and per-bridge only.

The current SRE code already has the right broad compartments:

- feedback windows summarize realized evidence/continuity progress,
  low-progress patterns, degradation pressure, retries, and warning history;
- brake state tracks uncertainty, spikes, host friction, repeated failures,
  repeated degradations, tonic EMA, and latch/guard thresholds;
- goal debt tracks pending goals, verification debt, contradiction/rejection
  debt, and closure pressure;
- routing, preservation, capability envelopes, AUX support, and host adapters
  exist as separate state/control surfaces.

The key missing coupling is upstream executive pressure. Cortex can often see
late closure symptoms, especially at `Stop`, but it does not yet track the
expected uncertainty reduction owed by forward commitments and compare that to
realized progress. That is why the next product work should move upstream from
renderer design into runtime control.

## Roadmap Principle

Do not implement the product as "more messages to the model." Implement the
product as better runtime executive control. Model-visible communication is
allowed only when the control decision has a grounded task-local anchor.

Each seam must state:

- which executive function it improves;
- which loop stage it strengthens;
- whether the expected effect is silent control, visible communication, or
  both;
- what live model behavior would prove the seam improved the model;
- which truth changes if it succeeds: Cortex, brain-wiring, conformance,
  shipping, or none yet.

## Phase 0: Evidence And Branch Hygiene

Goal: prevent stale side branches and partial recon artifacts from distorting
the next product seam.

Work:

- Preserve or explicitly land the unique headless translation harness recon
  doc from `codex/20260501-142219-claude-code-bridge-translation-headless-harness`,
  then retire that branch rather than merging its renderer-first implementation.
- Keep `codex/20260430-155752-claude-code-desktop-lifecycle-spine` parked as
  structural design evidence until a separate decision salvages, archives, or
  retires it.
- Keep `main` as the integration branch and make cleanup-report failures
  intentional, not accidental.

Acceptance:

- all unique live/recon evidence is either on `main` or explicitly archived;
- cleanup-report has no accidental stale managed work;
- no branch merge deletes newer tracker/dossier evidence;
- no shipping or behavior-lift claim is promoted.

## Phase 1: Runtime Expectation Debt

Goal: give Cortex a bounded way to know when forward motion has become too
cheap relative to unresolved uncertainty.

Build:

- Add a bounded expectation ledger to feedback/session state.
- Record expectation entries opened by forward commitments.
- Track generic horizon classes: `immediate`, `next_step`, `deferred`,
  `waiting_on_user`.
- Track generic satisfaction classes: evidence progress, continuity progress,
  commitment certification, external-record confirmation, explicit retraction,
  explicit narrowing, blocker surfacing, and user-wait release.
- Compute a `resolution_deficit` / expectation-debt summary from expected
  uncertainty reduction owed minus realized reduction paid down.
- Keep the first implementation runtime-only: no AUX, no model-visible text,
  no Claude hook messages, no SessionStart support bias.

Safety rules:

- Ambiguous or deferred work must not accrue debt just because the task remains
  open.
- Explicit questions to the user should move expectations into
  `waiting_on_user`.
- Honest partial progress should pay down debt or lower expected reduction.
- The signal should penalize new assertive forward motion, not checking,
  inspecting, asking, or narrowing.

Structural acceptance:

- tests show completion/verification claims open immediate expectations;
- tests show partial/hedged/user-question turns do not create false debt;
- tests show realized evidence/continuity/retraction pays debt down;
- tests show old feedback-window behavior remains backward compatible.

Live acceptance:

- on paired tasks, the model routes/checks earlier before false closure;
- no-overblock controls show clean successful work does not get slowed
  unnecessarily;
- no live claim is made until paired model evidence exists.

## Phase 2: Debt Drag Into Brake And Route

Goal: make unresolved expectation debt affect control before closure pressure
is the only visible symptom.

Build:

- Feed `resolution_deficit` into brake tonic pressure conservatively.
- Add persistence-weighted goal-debt drag against new forward commitments.
- Keep latch logic phasic: tonic/debt alone should not latch.
- Bias route selection away from execute/close and toward inspect, check, seek
  context, or ask when debt is high.
- Preserve the distinction between helpful verification moves and risky forward
  commitments.

Safety rules:

- Debt pressure must not freeze useful work.
- Check/inspect/ask should become easier, not harder, when debt rises.
- Quota pressure remains budget/routing concern, not truth-engagement law.
- Contradiction remains mostly phasic because it already has immediate
  inhibitory force.

Structural acceptance:

- tests show high resolution deficit increases guarded/check/inspect bias;
- tests show clean progress decays debt and returns route pressure toward
  neutral;
- tests show latching still requires phasic cause or existing latch law;
- route diagnostics expose bounded summaries without leaking internal tags to
  model-visible text.

Live acceptance:

- baseline model prematurely closes or over-executes on a task family;
- shaped runtime chooses more inspection/checking before closure;
- behavior improves without adding model-visible warning text;
- no-overblock controls remain clean.

## Phase 3: Grounded Intervention Records

Goal: allow Cortex to speak only when upstream control pressure has a grounded
task-local anchor.

Build:

- Define typed intervention records for anchored cases such as unsupported
  claim, overdue verification, unresolved goal forward commit, continuity gap,
  capability guard, and preservation risk.
- Keep route/brake/AUX internals out of the model-visible record.
- Suppress visible output when pressure is high but no grounded anchor exists;
  route or inspect silently instead.
- Preserve `Stop` as the strongest currently validated Claude Code visible
  actuator for false closure, while keeping `PreToolUse`, `UserPromptSubmit`,
  `PostToolUse`, and `PostToolUseFailure` as lifecycle owners for their own
  event functions.

Safety rules:

- no raw internal vocabulary;
- no schema IDs;
- no "Cortex says";
- no generic principles when a situated task fact is required;
- no correction if the last assistant message already retracted, narrowed,
  hedged, or asked the right question.

Structural acceptance:

- tests verify internal tags cannot appear in model-visible output;
- tests verify already-adequate assistant messages suppress visible output;
- tests verify each visible intervention names a claim/evidence/obligation
  anchor;
- tests preserve clean no-output controls.

Live acceptance:

- paired trials show visible intervention improves a reproduced baseline
  failure;
- no-overblock controls show clean closures pass;
- Mac/headless parity is recorded per bridge and not generalized.

## Phase 4: Claude Code Host Adapter From Runtime Law

Goal: make Claude Code Mac a lifecycle host adapter for Cortex runtime law,
not a plugin-side middleware product.

Build:

- Keep hook scripts thin transport.
- Put real logic in `cortex/hosts/claude_code_desktop/`.
- Wire lifecycle events by executive function:
  - `SessionStart`: hidden session setup and bounded residue load; no visible
    text by default.
  - `UserPromptSubmit`: prompt/task obligation capture and non-conflicting
    advisory opportunities.
  - `PreToolUse`: brake/tool/capability gating and route pressure.
  - `PostToolUse`: successful or warning-bearing evidence update.
  - `PostToolUseFailure`: failed-tool evidence update and expectation debt.
  - `Stop`: truthful closure pressure and grounded final correction.
  - `SessionEnd`: bounded residue persistence.
  - `PreCompact` and `SubagentStop`: architectural owners until separately
    probed.

Safety rules:

- every hook has delivery truth, model-visible truth, behavior-lift truth, and
  shipping truth tracked separately;
- cache staleness and operator split remain part of test protocol;
- Claude Code evidence never promotes OpenAI shipping truth or vice versa.

Acceptance:

- structural tests prove all wired hooks call host-adapter code, not ad hoc
  plugin prose;
- paired live probes are run only after each event's structural floor is
  confirmed;
- each behavior-lift claim is per-hook, per-content-shape, per-surface.

## Phase 5: AUX As Hidden Executive Bias

Goal: let repeated executive geometry bias caution without becoming memory,
truth, or model-visible narration.

Prerequisite:

- Phases 1 and 2 must prove runtime expectation debt and route/brake pressure
  are safe without AUX.

Build:

- Distill resolved expectation episodes into abstract executive geometry:
  host, surface, route family, claim-strength band, verification-demand band,
  continuity-demand band, horizon class, affordance scope, capability band,
  delay-to-resolution, and outcome class.
- Publish only short-lived, removable, host/family-scoped priors.
- Seed hidden brake/route floors at session setup or first task-bearing event.
- Keep raw episodes support-side only.

Safety rules:

- no task nouns, file names, transcript spans, or raw episodes in publications;
- no downward confidence bias from prior success by default;
- no model-visible AUX text unless explicitly supplied by the user/current
  context;
- fresh contrary success decays negative priors quickly.

Acceptance:

- tests reject content-bearing support publications;
- tests prove publications are score-only and non-sovereign;
- live evidence shows early check/seek-context behavior improves without clean
  session overblocking.

## Phase 6: Cross-Host Graduation

Goal: graduate runtime executive behavior across hosts without flattening host
differences.

Build:

- Keep OpenAI as shipping truth until another lane earns the full path:
  structural integration, live paired behavior lift, no-overblock controls,
  and explicit shipping decision.
- For each host, map the runtime loop to native affordances instead of copying
  Claude hooks.
- Track each bridge with the four truths: Cortex, brain-wiring, conformance,
  shipping.

Acceptance:

- every host claim names the exact control surface and live behavior evidence;
- no host inherits another host's behavior-lift claim;
- shipping default changes only through an explicit product seam.

## Twelve-Seam Execution Contract

When the user asks to "plan the next seam from 1 to 12," use this list. Do
not improvise a new ordering unless a seam fails its gate and the roadmap is
explicitly revised.

This is not a calendar promise. It is a completion contract: seam 12 only
counts as complete if the live evidence shows that Cortex has become the
runtime executive layer described in Point B. If an empirical gate fails,
stop and revise instead of pretending the count reached the goal.

| # | Seam | Objective | Required output | Gate to advance |
| --- | --- | --- | --- | --- |
| 1 | Evidence preservation and branch hygiene | Preserve the unique headless translation-harness recon artifact, retire the stale renderer-first branch if no longer load-bearing, and keep lifecycle-spine explicitly parked. | Tracked or archived recon evidence; cleanup-report contains only intentional parked work. | No unique evidence remains trapped on a stale branch; no merge can delete newer tracker/dossier/roadmap material. |
| 2 | Runtime expectation ledger | Implement `ForwardCommitment`, `ExpectationRecord`, `ExpectationLedger`, and `ResolutionDeficitState` structurally. | Runtime/SRE state object plus deterministic tests for opening, paydown, suspension, and relief. | False closure and verification claims open expectations; honest partial progress and user questions do not create false debt. |
| 3 | Expectation corpus and falsification tests | Build an annotated structural corpus for the executive cases before changing control behavior. | Test corpus covering false closure, unsupported verification, partial progress, waiting-on-user, retraction, blocker surfacing, verified work, capability mismatch, clean controls. | Corpus proves the ledger distinguishes unsupported forward motion from honest incomplete work. |
| 4 | Debt-to-route/brake coupling | Feed `resolution_deficit` and `goal_drag` into route/brake pressure conservatively. | Route/brake implementation and diagnostics; tests for biasing away from execute/close and toward inspect/check/ask. | Debt does not latch by itself, does not freeze useful work, and makes evidence-gathering easier rather than harder. |
| 5 | Silent-control live probe on OpenAI Codex App/CLI | Test whether runtime control improves behavior without adding warning text. | Paired live evidence on the Codex App/CLI wrapper-resume evidence path with baseline/shaped/clean controls. | Shaped condition improves evidence recovery or continuity without unacceptable useful-work slowdown or overblock. |
| 6 | Grounded intervention records | Add typed visible-intervention records only for grounded anchors. | `InterventionRecord`-style objects for unsupported claim, overdue verification, unresolved goal, continuity gap, capability guard, preservation risk; leakage tests. | No visible output occurs without a grounded anchor; internal tags/schema/hook mechanics cannot leak. |
| 7 | Visible-intervention live probe | Compare silent-only control against grounded visible self-correction. | Paired live trials measuring when speaking helps versus when silent routing is better. | Visible intervention improves a reproduced baseline failure and clean controls stay clean; result scoped by host/surface/content shape. |
| 8 | Claude Code adapter from runtime law | Map the proven runtime loop onto Claude Code lifecycle hooks with thin plugin transport. | `cortex/hosts/claude_code_desktop/` host-adapter logic for SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PostToolUseFailure, Stop, SessionEnd where structurally earned. | Hook scripts stay thin; every wired event has structural delivery proof and no product/shipping overclaim. |
| 9 | Claude Code live recon | Validate the runtime loop on Claude Code Mac/headless surfaces per hook and control mode. | Recon docs with raw hook I/O, transcripts, paired scoring, no-overblock controls, operator split, cache-staleness notes. | Brain-wiring truth is earned per bridge; no Claude result is treated as shipping truth. |
| 10 | AUX hidden-bias program | Distill resolved executive geometry into hidden, removable support priors after runtime debt is safe. | AUX publication/update tests for abstract geometry only; hidden brake/route floor seeding; content-leak rejection tests. | AUX stays support-side, score-only, non-sovereign, and not model-visible by default. |
| 11 | Cross-host conformance expansion | Apply the proven runtime law across OpenAI, Claude, Gemini, and reference without flattening host differences. | Conformance tests and host-specific adapters/diagnostics for native affordances. | Each host claim names exact control surface and evidence; no host inherits another host's behavior-lift result. |
| 12 | Shipping decision and goal audit | Decide whether the executive-runtime loop has reached Point B and whether shipping truth changes. | Product audit comparing Point B behaviors against live evidence; status registry update only if earned; explicit decision on shipping default. | Cortex demonstrably makes model behavior more continuous, evidence-bound, task-faithful, self-correcting, and honest at closure across the intended shipping lane. |

The plan reaches the goal only if seam 12 passes its audit. If seam 12 cannot
truthfully say that Cortex improves the model's next behavior as an executive
runtime layer, the correct output is not "goal reached"; it is a revised
roadmap with the failed assumption named.

## Immediate Next Seam

The next seam after debt-to-route/brake coupling is seam 5: run the
silent-control live probe on the OpenAI Codex App/CLI wrapper-resume evidence
path. It should test whether the structural debt-control path improves evidence
recovery or continuity without adding model-visible warning text, slowing
useful verification, or overblocking clean controls.

## Stop Conditions

Stop and revise the roadmap if any of these happen:

- implementation work starts from a hook map rather than an executive failure;
- a seam tries to communicate internal state because control pressure exists
  but no grounded anchor exists;
- AUX memory becomes model-visible by default;
- route/brake pressure suppresses checking, asking, or evidence gathering;
- a Claude Code recon result is treated as shipping truth;
- a renderer seam cannot explain which upstream intervention decision it is
  serving.

## Review Questions

Before approving any next seam, ask:

1. Does this move Cortex closer to runtime executive behavior, or just toward a
   nicer plugin?
2. Does it improve the control loop before model-visible communication?
3. Is the expected benefit silent control, visible correction, or both?
4. What baseline failure must reproduce?
5. What no-overblock control protects useful work?
6. Which truth can change if the seam succeeds?
