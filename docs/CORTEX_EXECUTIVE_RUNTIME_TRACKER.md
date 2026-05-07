# Cortex Executive Runtime Tracker

Surface: product planning

This document tracks Cortex against its actual product goal with live model
evidence. It is subordinate to `docs/CORTEX.md` for identity and to
`internal/truth/cortex_status.json` for operational truth. If this tracker
disagrees with either surface, the tracker is stale and must be corrected; it
is not a second registry.

The ordered product train lives in `internal/truth/cortex_status.json` and the
generated human view in `docs/CORTEX_STATUS.md`. This tracker is a scoreboard,
not a second roadmap or registry.

## North Star

Cortex is a post-training runtime executive-function layer around models. It
should hold the real task thread when the model drifts, preserve open
obligations without turning into generic memory, slow unsupported forward
motion, protect verified work, surface blockers before fluent closure hides
them, adapt to host/model/tool affordances, and intervene only when doing so
improves the model's next input or output.

The center is not "communicate all Cortex state to the model." The center is:
Cortex should shape the model's behavior at runtime so the model acts with
better executive function than it would unaided.

Communication is only the model-visible edge of Cortex. Silent route,
degrade, block, preserve, brake, suppress, or do-nothing decisions are equally
valid Cortex behavior when they improve or protect the next model step. The
model should see only the behavioral consequence that belongs in its task
state, never the internal executive machinery.

When the behavioral consequence is model-visible text, it must obey the
Model-Visible Cortex Output Law in `docs/CORTEX.md`: the text should not sound
like an outside person, plugin, monitor, or "Cortex says" authority. It should
make a claim/evidence/obligation/task-standard/next-move constraint explicit
inside the model's own task frame. First-person style is lawful only for
prior-act self-correction with a clear prior-act anchor, or for explicitly
signed-off prospective task-set formation before work begins.

The missing front half of the loop is task-standard formation: the model must
construct a task-local standard for what good work requires, Cortex must hold
that standard across lifecycle events, and later closure or tool gates must
compare claims and evidence against that standard rather than against generic
verification-shaped activity.

The target loop is:

```text
model/host event
-> task-state and executive-risk understanding
-> intervention decision
-> control mode
-> improved next model behavior
```

Every future seam that claims product relevance should name which part of
this loop it strengthens. A seam that cannot trace into this loop is
instrumentation, planning, or lab work, not product Cortex.

## Live-Model Achievement Matrix

| Cortex executive function | Desired live model behavior | Internal Cortex control mode | Model-visible communication only if needed | Current structural proof | Current live-model evidence | Current gap | Next evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | The model narrows or retracts unsupported claims without discarding supported work. | Commitment lattice, certification firewall, feedback classification, closure gate. | Reflect a specific unsupported claim and the missing evidence; do not expose commitment IDs or certification terms. | Landed in `cortex/core`, `cortex/drivers`, and proofed by product/conformance tests per `internal/truth/cortex_status.json::bio_to_code_matrix`. | OpenAI Codex App/CLI remains the shipping product target, with current live evidence on the transitional wrapper-resume actuator. Claude Code Stop closure pressure has narrow behavior-lift evidence for false completion, but the Mac pending-goal retest shows raw internal wording is content-shape contaminated. | Live proof is strongest only where Cortex can place grounded instructions into the OpenAI Codex App/CLI target or a situated Stop reason; broad arbitrary-claim repair is not earned on Claude Code. | Build upstream resolution-deficit and expectation-debt scoring, then test whether grounded Stop/advisory text repairs unsupported claims without raw Cortex vocabulary. |
| Bounded correction and verified-work preservation | The model repairs the failing part while preserving verified artifacts, passing checks, and good prior work. | Preservation state, verified-work runtime, intervention budget, route/degrade decisions. | Name the preserved evidence and the limited repair target only when the model is about to over-rewrite or falsely close. | Landed in `cortex/runtime`, `cortex/sre`, and `cortex/hosts/openai` with product tests. | UserPromptSubmit verified-work delivery reached Claude Code transcript boundaries, but tested exact-output cases still false-closed; behavior lift is unearned for that surface. | Pre-action delivery is weaker than post-output repair on Claude Code. The system needs control pressure before visible communication, not renderer-first optimism. | Probe non-conflicting preservation cases after the upstream control law can decide when preservation should speak versus silently route. |
| Uncertainty handling and brake | The model slows down, inspects, asks, or degrades instead of converting uncertainty, contradiction, or repeated failure into confident forward motion. | Brake state, tonic EMA, phasic spikes, route pressure, capability-aware degradation. | Usually silent. If visible, state the concrete unsafe conclusion or contradiction and the next check; never expose brake EMA or brake state. | Landed in `cortex/sre` with product/experimental proof surfaces and status-registry math-to-code entries. | Claude Code recon shows Stop can recover some false closure after the fact. It does not prove live pre-action brake behavior on Claude Code. | Current coupling is not yet a live resolution-deficit loop: expected uncertainty reduction and realized evidence progress are not tracked as one runtime control signal. | Implement and test resolution deficit / expectation debt as the upstream pressure that biases route before closure becomes the only symptom. |
| Branch continuity, suspend/resume, and truthful closure | The model keeps the real task thread alive across interruption and closes only with supported evidence. | Branch state, host-local persistence, goal debt, closure pressure, suspend/resume law. | Surface only the open obligation, missing evidence, or unsupported closure claim; avoid session IDs and hook mechanics. | Landed in SRE and host runtimes per status registry, with OpenAI host-control proof. | Claude Code Stop closure pressure has the clearest recon behavior lift: pending-goal and evidence-degradation shaped trials repaired narrow false closures; headless evidence-degradation matched, pending-goal diverged. | Cross-thread resume in Claude Code Desktop is not earned because session IDs are per-thread; SessionStart continuity remains unvalidated. | Separate project-fingerprint or host-local continuity seam from Stop closure repair; do not treat Stop success as resume success. |
| Intervention pricing versus neutrality | Cortex intervenes only when the intervention improves the next model step; otherwise it stays out of the way. | Neutral-dominance arbitration, posture-sensitive online control, anti-thrash, capability-aware route pricing. | Normally none. The model should see no route pricing, internal score, or arbitration term. | Landed in `cortex/sre`, `cortex/aux`, and `cortex/runtime` with product/experimental/conformance tests. | No Claude Code hook result proves intervention pricing. Existing recon proves some delivery and some Stop behavior, not whether Cortex chose the right moments globally. | The live question is not "can we render a message?" but "did Cortex correctly decide to act, route, suppress, or stay silent?" | Add live scoring for intervention usefulness: compare baseline, silent-route, advisory, and block outcomes on matched tasks. |
| Blocker surfacing and goal-debt management | The model names unresolved blockers and unfinished obligations before fluent closure hides them. | Goal-debt state, closure-pressure semantics, feedback-window persistence, route pressure. | Reflect the specific open obligation and the next lawful move; do not expose `pending_goal_debt` or other internal tags. | Landed across SRE and host adapters with product/conformance tests. | Stop block reasons repaired some pending-goal/evidence-degradation false closures, but raw internal tag-shaped wording caused a Mac trial to treat the hook as suspicious. PostToolUseFailure persistence into Stop is real but behavior lift was mixed at 2 of 3 failure pairs. | Goal debt is currently strongest at closure; it should also drag against new forward commitments before the model reaches false completion. | Test persistence-weighted goal-debt drag plus translated, grounded Stop output after structural implementation. |
| Multi-host executive continuity | Cortex law stays one executive layer while each host uses its native affordances honestly. | Host adapters, conformance truth, host-control transport, capability envelope, route/degrade/block mapping. | Host-parametric only: OpenAI instructions, Claude Code hooks, Gemini/reference surfaces should communicate different shapes from the same law. | Landed structurally across OpenAI, Claude, Gemini, and reference in status registry and conformance tests. | Shipping truth is `openai.codex_app_cli`; current live evidence uses the transitional `codex_exec_wrapper_resume` actuator. Claude Code Desktop and headless CLI evidence is recon only and per-bridge. | Claude Code, Gemini, Codex App, and other surfaces do not inherit OpenAI shipping claims; every host bridge needs its own live model evidence. | Keep Claude Code as recon/proving ground until a specific bridge earns paired live behavior lift and no-overblock evidence. |
| Offline consolidation and support geometry | Prior episodes bias executive caution and route selection without becoming hidden memory, proof, or a second truth court. | AUX explicit publications, support priors, host/tool reliability priors, score-only re-entry. | Usually none. If publication content is explicitly supplied, present it as a check-path prior, never proof of completion. | Landed in `cortex/aux` with experimental/archive/conformance tests and explicit publication law. | No Claude Code recon has earned AUX-to-model behavior lift. OpenAI/reference publication lanes carry the strongest current live re-entry shape. | Support memory must stay hidden and non-sovereign; the live question is how AUX can seed brake/route floors without transcript leakage. | Test hidden SessionStart/host-control support-bias seeding only after session artifact plumbing exists; no model-visible AUX memory by default. |

## Control-Loop Tracker

Use this table to keep future seams oriented around executive behavior rather
than around host hooks, renderers, or local implementation neatness.

| Loop stage | What Cortex must know or do | Current state | Evidence needed before stronger claim |
| --- | --- | --- | --- |
| `model/host event` | Receive a host-native event without flattening the host surface. | OpenAI Codex App/CLI is the product target; OpenAI API host-control is support/conformance; Claude Code hook events are recon with verified delivery for several events. | Per-host event delivery proof, plus cache/staleness/operator-split constraints documented for that host. |
| `task-state and executive-risk understanding` | Understand claims, evidence, obligations, task-local standards, uncertainty, verified work, capability limits, and support priors. | The eight state families exist structurally, and `TaskStandardSpine` is now a mapped SRE object. Live standard formation and capture remain unearned until the signed-off UserPromptSubmit probe. | A structural live probe proving signed-off task-set text delivery and standard capture, followed by an integration probe proving the captured standard shapes later gating. |
| `intervention decision` | Decide whether action is useful: silent route, degrade, block, ask, preserve, surface blocker, or do nothing. | Route/pricing/brake law exists structurally; Claude Code recon mostly tested visible hook content, not intervention selection. | Baseline-vs-shaped tasks where the main measured lift is the chosen control mode, not just message wording. |
| `control mode` | Apply the selected control through the host affordance: instructions, tool gating, Stop block, route downgrade, persistence, or no-op. | OpenAI has direct product control. Claude Code has verified hook surfaces, but behavior differs by event and content shape. | Per-control-mode proof that the host receives the control and the model behavior changes in the intended direction. |
| `improved next model behavior` | The model's next output or action is more continuous, evidence-bound, scoped, truthful, or appropriately slowed. | Narrow Stop closure-pressure behavior lift exists; UserPromptSubmit/PreToolUse content delivery alone did not earn lift; PostToolUseFailure-to-Stop is mixed. | Paired live trials with baseline failure reproduced, no-overblock controls, and no hidden shipping promotion. |

Every seam should declare the loop stage it strengthens. A renderer-only seam
must say why the upstream intervention decision is already grounded enough to
make model-visible text the right next bottleneck.

## Live Evidence Scoreboard

The four truths are Cortex truth, brain-wiring truth, conformance truth, and
shipping truth. Do not let progress in one cell masquerade as progress in
another.

| Truth | Current standing | What can change it |
| --- | --- | --- |
| Cortex truth | Cortex is the post-training executive-function layer described in `docs/CORTEX.md` and formalized by the V2 packet docs. This tracker does not change Cortex law. | A doctrine or packet revision that explicitly changes the executive law and lands with tests/status updates. |
| Brain-wiring truth | Model/host-specific mappings are separate. Claude Code Desktop recon shows that hook content can arrive and still fail integration when it conflicts with exact-output instructions or exposes raw internal wording. | Paired model-side evidence for a given host, hook, content shape, and task family. |
| Conformance truth | OpenAI, Claude, Gemini, and reference conformance surfaces remain distinct; structural conformance is not live behavior lift. | Conformance lanes passing new or revised tests that encode the executive law. |
| Shipping truth | OpenAI remains shipping truth through `openai.codex_app_cli`, with current evidence on `codex_exec_wrapper_resume` and queued product work toward `hook_native_product`. Claude Code Desktop, Claude Code headless CLI, and individual hook findings are recon only. | A product seam with paired live evidence, no-overblock controls, status-registry update, and explicit shipping-default decision. |

Current Claude Code recon standing:

- `Stop` closure pressure has narrow behavior-lift evidence, constrained by
  content shape. Situated closure reasons repaired some false completions;
  raw internal vocabulary produced suspicious/prompt-injection-shaped
  responses in a Mac retest.
- `PreToolUse` and `UserPromptSubmit` delivery are real in tested Claude Code
  surfaces, but behavior lift is unearned or failed in the tested
  exact-output-conflict shapes.
- `PostToolUseFailure` and feedback persistence are real, but
  PostToolUseFailure-to-Stop behavior lift was mixed.
- Headless Claude Code can be useful for lower-cost Stop research, but
  headless equivalence was partial and does not validate Mac parity, other
  hooks, or shipping behavior.

## What Cortex Should Keep Silent

Do not communicate these model-visibly by default:

- route pricing
- brake EMA or tonic/phasic implementation details
- AUX priors or support-memory machinery
- raw support episodes
- session IDs and transcript paths
- internal tags such as closure-pressure or goal-debt labels
- schema names and runtime context IDs
- hook mechanics and plugin registry state

If any of these affect the model, they should do so through a grounded control
consequence: inspect instead of execute, block instead of false close, preserve
verified work, ask for missing evidence, or remain silent because the model is
already handling the task correctly.

## Strategic Direction

The next strategic direction is upstream executive control, not
renderer-first work.

For the current Codex App/CLI task-standard train, the scored-lexical offline
readiness gate was the last substrate-first seam before an actuator reset. The
no-spend raw-vs-silent artifact readout then found a narrow signal:
`silent_task_standard` beat `raw_codex` on `task_standard_exactness`
evidence-recovery in 5/5 paired trials, while output quality was mixed and
truth-gap had a material goal-continuity regression. That justifies an actuator
map constrained to exactness/evidence recovery; it does not justify another
live behavior comparison, broad Cortex lift, or Sinkhorn.

The lifecycle actuator map is now the product architecture baseline: Codex
lifecycle surfaces are ordered by the control they actually exert over the
model's next input, output, tool result, or allowed action, not by hook-count
coverage.

The Codex App/CLI event map should be treated as:

- SessionStart: session/workspace context only.
- UserPromptSubmit: prospective task-set formation.
- PreToolUse: hard motor deny/block only; do not design it as coaching text
  because Codex does not support additionalContext there.
- PermissionRequest: approval-bound route control.
- PostToolUse: strongest near-term next-step correction surface because it can
  replace or annotate completed tool feedback before the next model step.
- Stop: late closure continuation.

The PostToolUse task-standard next-step correction Gate 0 has now passed
structurally without live spend. A gated Codex-host path can add
PostToolUse `additionalContext` when product-visible verification/readback
evidence leaves a specific captured work-standard or closure-evidence item
unresolved, while flag-disabled, clean evidenced, blocker/waiting, and
unrelated-tool controls stay silent. This is still Gate-0 proof only: it does
not earn live behavior lift, does not activate defaults, and does not justify a
three-arm live rerun by itself.

The PostToolUse calibration decision accepted a narrow live actuator probe as
the next product seam, not Sinkhorn and not a three-arm behavior comparison.
The approved narrow live probe then produced `failure_context_ignored`: a
specific PostToolUse `additionalContext` reached Codex CLI in the mismatch
case and clean/blocker/waiting/unrelated controls received no PostToolUse
context, but the next model tool did not run the named direct check before
closure. Later exactness checks came through the existing Stop continuation
loop, so PostToolUse next-action effect remains unearned. The next product seam
is an architecture decision about actuator timing and model-I/O leverage, not a
text, fixture, matcher, or policy remediation seam.
The architecture decision classifies that result as PostToolUse
timing/selection failure: the context fired after a failed missing-artifact
precondition, so the next legitimate model action was artifact creation rather
than direct verification. The next product seam is no-live phase-aware
PostToolUse calibration Gate 0: reserve context until a product-visible
artifact or candidate output exists and a required standard item remains
unresolved, while keeping closure-before-direct-check as a failure.
PreToolUse motor inhibition should follow only as action blocking, not as a
model-visible advice surface, and false-deny clean-control risk must be treated
as a future kill-rule risk. Sinkhorn-style transport belongs later as the
`D_std` mass-conservation operator only if PostToolUse or PreToolUse actuators
show signal and one-event-overcredits-many-items remains load-bearing after
pairwise scores are trustworthy.

The likely missing coupling is a runtime estimate of resolution deficit:
expected uncertainty reduction owed by recent forward commitments minus
realized evidence, continuity, certification, retraction, or blocker progress.
That signal should interact with persistence-weighted goal-debt drag against
new forward commitments and with brake/route pressure before visible
communication becomes necessary.

The model-facing translation function remains important, but only as the
grounded edge of the control loop. A `tau` renderer should speak only when
Cortex has a task-local anchor: an unsupported claim, a missing evidence
obligation, a continuity gap, a capability boundary, or a verified-work
preservation risk. If control pressure exists without an anchor, Cortex should
route, degrade, inspect, or stay silent rather than invent generic advice.

## Semantic Contraction Discipline

Cortex should get smaller by removing duplicate policy and stale surfaces, not
by minifying readable code. Semantic contraction means collapsing duplicate
law into one owner, retiring inactive proof paths, archiving or role-demoting
retained context that no longer governs current work, and deleting host/runtime
copy-paste only when behavior-preservation proof or explicit retirement
evidence exists.

Current size pressure is material: `cortex/**` is about 43.6K Python LOC, with
`cortex/hosts` about 21.6K LOC. The largest contraction risk centers are the
four host `runtime.py` files, per-host `session_io.py` parallelism,
`cortex/hosts/openai/codex_app_cli_hook_coordinator.py`, and large SRE/AUX
modules that can accumulate duplicate policy paths.

After a run of additive product seams, planning should schedule or explicitly
waive a contraction audit before the next large actuator, substrate, or
host-kernel expansion. Future architecture/product seams should report LOC
added/deleted, duplicate policy removed, the owner module after the change,
and whether the seam added a new policy path, consolidated one, or left
explicit contraction debt. Raw LOC reduction is not success; removal of
duplicate policy or retired surfaces while preserving Cortex law, host
distinction, and proof coverage is success.

## Audit-Survivor Future Backlog

This section is a serious candidate backlog, not casual brainstorming and not
a second roadmap. Future agents must consider these candidates when planning
architecture work because they survived broad repo/code review as plausible
paths toward a stronger Cortex. They still become current work only when a
specific seam is promoted into `internal/truth/cortex_status.json::next_product_train`
or the current train. To remove or demote a row, land a tracker/status/recon
update that names the code-grounded reason.

| Candidate seam | Why it matters for the future Cortex shape | Promotion gate | Current state |
| --- | --- | --- | --- |
| `cortex-semantic-contraction-audit` | Cortex should not grow by default; the audit produced a deletion/consolidation map with owners, behavior-preservation proof requirements, and candidate seams. | Use `docs/recon/cortex_semantic_contraction_audit.md` as evidence only; no deletion until a seam proves behavior is preserved or the surface is explicitly retired in status/recon. | `evidence_landed` |
| `workflow-connectivity-trace-reachability` | Closeout already requires `connectivity_trace`, but shape validation is not enough; product seams should mechanically prove a path to model input/output. | Queue when workflow work is allowed; start with deterministic reach classes before call-graph crawling. | `queueable_now` |
| `recon-frontmatter-indexer` | Recon docs are the audit memory of earned and forbidden claims; structured fields would make live evidence, verdicts, hosts, actuators, and families queryable instead of grep-only. | Target `doc_roles.recon_evidence`; keep narrative primary and schema supporting. | `queueable_now` |
| `sre-output-law-rendering-contract` | Model-visible Cortex output should be constructively lawful, not protected only by template discipline and forbidden-term checks. | Extend the existing `cortex/sre/interventions.py` rendering path; no new model-visible wording without regression proof. | `queueable_now` |
| `core-proof-obligation-test-factories` | Core packet proof obligations should be executable checks where possible, so packet law does not rely only on prose and spot tests. | Start with bounded deterministic factories; add Hypothesis only after dependency and strategy cost are justified. | `queueable_after_probe` |
| `host-runtime-kernel-extraction-audit` | The four host runtime files carry large parallel structures; a future Cortex should share law without flattening host-native realization. | First land an audit that measures exact helper equivalence and host-specific divergences; migrate only after that evidence. | `queueable_after_probe` |
| `driver-session-io-common-kernel-audit` | Per-host commitment, neutral, and session I/O paths look highly parallel; a future seam should find the smallest shared helper layer without flattening host vocabulary. | Compare host drivers and session I/O round trips; no collapse until per-host fixture proof preserves behavior. | `queueable_after_probe` |
| `coordinator-actuator-boundary-extraction` | `codex_app_cli_hook_coordinator.py` is the OpenAI Codex App/CLI pressure point for actuator growth; per-event actuator modules may keep policy ownership clearer. | Extract only after current task-standard questions settle; require no model-visible text change and Gate 0 replay proof. | `queueable_after_probe` |
| `recon-archive-retirement-pass` | Lab/recon/doc active surfaces should not accumulate forever; inactive proof paths need explicit archive or retention decisions. | Queue after structured recon indexing or equivalent active-doc evidence; generated docs and role maps must stay exact. | `queueable_after_probe` |
| `sre-aux-policy-concentration-audit` | Large SRE/AUX modules may contain duplicate policy paths, but SRE and AUX ownership must remain distinct and AUX must stay removable. | Audit specific duplicated rules first; no SRE/AUX consolidation without packet-law citation and proof coverage. | `research_backlog` |
| `posttooluse-phase-aware-calibration` | PostToolUse is the strongest near-term Codex App/CLI next-step actuator, but it must fire at the phase where the named check is actionable. | Queue after the current PostToolUse architecture decision; prove Gate 0 without live spend before another live probe. | `queueable_after_probe` |
| `pretooluse-motor-inhibition-gate0` | PreToolUse deny is the lifecycle lever for action inhibition, which is closer to executive control than late Stop repair. | Reverify current Codex hook semantics, require typed output-law reason text, and treat any clean-control deny as high-severity overcontrol. | `research_backlog` |
| `bayesian-kill-rule-shadow` | Behavior-lift decisions should eventually use posterior uncertainty rather than only fixed 4/5 trial thresholds, while preserving hard clean-control overblock rules. | Run as replay-only shadow first; it must not produce easier lift claims on historical runs. | `research_backlog` |
| `task-standard-semantic-alignment` | Lexical task-standard matching may hit a synonym wall; semantic or transport methods may eventually be needed for robust evidence allocation. | Defer until actuator timing is no longer the bottleneck and replay proves pairwise alignment or mass allocation is load-bearing. | `research_backlog` |

The queueable discipline rows remain the current best low-risk candidates.
Rows produced by the semantic contraction audit are serious candidate seams,
not deletion permission. The later rows are important future-shape pressure,
but they must not bypass the promotion gates just because they are
mathematically attractive.

## Use In Future Planning

Before proposing a Claude hook, a renderer, or a host-specific plugin seam,
answer these questions:

1. Which executive function in the matrix is being improved?
2. Which control-loop stage is the bottleneck?
3. Is the intended effect silent control, model-visible communication, or both?
4. What live model behavior would prove improvement?
5. What truth changes if the seam succeeds: Cortex, brain-wiring,
   conformance, shipping, or none yet?

If the answer starts with "which hook can we use?" instead of "which executive
failure are we correcting?", the seam is already at risk of shrinking Cortex
into middleware.
