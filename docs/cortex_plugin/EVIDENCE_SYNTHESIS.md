# Claude Code Desktop Plugin Evidence Synthesis

Surface: internal / recon synthesis

Status: evidence accounting only. This document does not implement the plugin,
does not run a new probe, does not advance the parked lifecycle-spine branch,
and does not change shipping truth.

This synthesis reads the Cortex identity and implementation discipline in
`docs/CORTEX.md`, the Claude Code Desktop plugin design surfaces in
`docs/cortex_plugin/`, the lifecycle and hook recon reports in `docs/recon/`,
and the generated operational truth in `internal/truth/cortex_status.json`.
It uses the four-truth discipline from `docs/CORTEX.md` Section 3: delivery
truth, model-visible delivery truth, behavior-lift truth, and product/shipping
truth must not be collapsed.

Capability boundary for empirical work: Codex cannot drive Claude Code
Desktop's GUI, type into the Code tab, or observe model responses directly.
Codex can prepare temporary plugins, arm mode files, inspect logs, and analyze
repo evidence. Behavior-lift probes on Claude Code Desktop require the user to
enter prompts manually and report or preserve visible model output.

## 1. What Is Empirically Established

### Hook Delivery Truth

Earned:

- Codex App project `Stop` hook delivery is confirmed for the tested Codex App
  for Mac version and `/Users/erikahoward/cortex-loop` when trusted
  `.codex/config.toml` project hooks are active. The hook saw
  `last_assistant_message`, `stop_hook_active`, `transcript_path`, `cwd`,
  `model`, and related fields. It also saw title-generation `Stop` events with
  `transcript_path: null`, so real assistant turns must be filtered from title
  events.
- Claude Code Desktop Code-tab project-local `PreToolUse:Bash` delivery is
  confirmed when the hook is installed in the effective Claude-managed worktree
  settings file. The first root settings attempt did not fire in an already-open
  thread because the effective subject was
  `.claude/worktrees/friendly-gould-4da043`.
- Claude Code Desktop user-scope plugin delivery is confirmed in Code-tab
  sessions for `PreToolUse:Bash` and `Stop`. It was observed in
  `/Users/erikahoward/cortex-loop` with project-root `cwd`, and in the unrelated
  `/Users/erikahoward/cortex-plugin-sandbox` with sandbox-root `cwd`.
- Claude Code Desktop `Stop` hook delivery is confirmed in the sandbox via
  user-scope temporary plugins. The hook received `last_assistant_message` and
  `stop_hook_active`, and `decision: "block"` produced a continuation loop
  rather than ending the turn.
- The merged `cortex/hosts/claude_code_desktop` structural adapter path is
  confirmed for `PreToolUse:Bash`: a temporary user-scope plugin could import
  the local repo adapter, parse the live hook payload, run the runtime step, and
  emit hook JSON.

Not yet earned:

- `PostToolUse`, `PostToolUseFailure`, `SessionStart`, `SessionEnd`,
  `UserPromptSubmit`, `PreCompact`, and `SubagentStop` delivery have not been
  manually verified for the Cortex plugin design. The current Claude Code docs
  distinguish `PostToolUseFailure` from `PostToolUse`; the design doc predates
  that evidence and must not assume all failed tool results arrive through
  normal `PostToolUse`.
- User-scope plugin behavior in an actual `.claude/worktrees/...` `cwd` remains
  open. The repo-local project-settings probe observed a managed worktree; the
  user-scope sandbox probe observed project root.
- Claude Code CLI, Claude Desktop chat, Codex CLI, Gemini CLI, Gemini App, and
  API surfaces are not covered by the Claude Code Desktop empirical probes.

### Model-Visible Delivery Truth

Earned:

- Codex App `Stop` block reasons reached the model-visible continuation path in
  the tested app thread. The sentinel was not in the user prompt, and the next
  assistant response acknowledged it.
- Claude Code Desktop `PreToolUse:Bash` `hookSpecificOutput.additionalContext`
  reached the model. The project-local probe recorded
  `hook_additional_context` transcript attachments and model acknowledgements.
  The user-scope plugin probes repeated the same basic additional-context reach.
- Claude Code Desktop `Stop` `decision: "block"` reasons reached the
  model-visible continuation path. The transcript recorded `Stop hook feedback:`
  meta messages and `hook_blocking_error` attachments with the hook reason.
- The actual `CORTEX_RUNTIME_CONTEXT_V1` bridge reached the Claude Code Desktop
  model-visible context in Gate 1 of the runtime-context probe. This establishes
  delivery of that content shape, not its adequacy.

Not yet earned:

- Model-visible delivery from `SessionStart`, `UserPromptSubmit`,
  `PostToolUse`, `PostToolUseFailure`, `PreCompact`, `SubagentStop`, or
  `SessionEnd` has not been empirically proved for Claude Code Desktop.
- Model-visible delivery from a bundled install that does not import the local
  `cortex-loop` checkout has not been proved.
- Model-visible delivery after config/plugin updates in already-open Claude or
  Codex threads is not earned. Existing evidence points the other way: open
  threads can keep stale hook command paths.

### Behavior-Lift Truth

Earned narrowly:

- Claude Code Desktop `Stop x closure pressure` has high-confidence manual
  evidence for two non-clean false closure cases and one clean control. In
  `pending_goal`, baseline allowed `MIGRATION COMPLETE`; shaped Stop feedback
  caused the continuation to retract and name missing evidence. In
  `evidence_degradation`, baseline allowed `TESTS PROVEN GREEN`; shaped Stop
  feedback caused the continuation to say no tests were run. In `clean_control`,
  baseline and shaped both emitted `CLEAN DONE`, with no block.
- That Stop result earns a narrow closure-pressure behavior finding only. It
  supports `Stop` as the closure-pressure hook in the H x F lattice.

Not earned:

- `PreToolUse` runtime context behavior lift is not earned. Gate 1 delivered
  real `CORTEX_RUNTIME_CONTEXT_V1`, but the paired behavior result was mixed:
  one shaped win, one no-change, one shaped regression, and one neutral.
- Codex App sentinel acknowledgment is mechanism proof, not Cortex behavior
  lift. It proved the block reason reached the model, not that Cortex improved
  output quality.
- Sentinel acknowledgements in `PreToolUse` probes are mechanism proof, not
  product lift. They show additional context can influence text, and also show
  that poorly shaped content can create interaction loops.
- The earlier non-manual Claude Stop observations remain auxiliary. The manual
  recalibration is the high-confidence behavior basis because GUI automation
  and accessibility/focus uncertainty made the earlier broader run less clean.

### Product / Shipping Truth

Earned:

- No new product or shipping truth is earned by the Claude Code Desktop recon.
  The status registry still identifies OpenAI as the shipping default surface
  and Claude as a non-default conformant host.
- The structural adapter evidence earns only a partial build substrate:
  `PreToolUse:Bash` has an adapter path in `cortex/hosts/claude_code_desktop/`.
  Other hook scripts in the lab skeleton are no-op transport stubs and must not
  be read as implemented lifecycle behavior.

Not earned:

- Claude Code Desktop is not the shipping default.
- The parked lifecycle-spine branch is not merge-ready.
- The plugin is not Stop-primary.
- The current runtime-context content shape is not behavior-lift proof.
- Cross-session resume in Claude Code Desktop is not earned by `session_id+cwd`
  keying. Fresh Code-tab threads in the same sandbox produced different
  `session_id` values.

## 2. What The Evidence Says About The Design Doc

### Identity Claim: Claude Code Desktop As Natural Lifecycle Surface

Judgment: supported as a design direction, not yet earned as product truth.

The lifecycle-first surface matrix and Claude Code Desktop probes support the
claim that the Code tab is a natural partial-influence surface: it has hooks,
plugin packaging, transcripts, `PreToolUse` and `Stop` boundaries, and project
or user-scope extension paths. The evidence does not support treating it as a
shipping Cortex surface today. The design doc should keep this as target intent
and clearly separate it from `internal/truth/cortex_status.json` shipping truth.

### Host Adapter, Not Plugin-Side Middleware

Judgment: supported and sharpened.

`docs/cortex_plugin/ADAPTER.md` is the strongest architectural refinement in
the current evidence set. The temporary plugins were intentionally thin
transport wires; real Cortex logic belongs under
`cortex/hosts/claude_code_desktop/` and shared `cortex/**` modules. This is
consistent with the math-to-code map: `feedback_window_realization`,
`goal_debt_state`, `preservation_state`, `host_runtime_sessions`, and
`host_control_transports` already have code homes and proof surfaces. The
design doc should preserve this boundary and avoid accumulating business logic
in plugin scripts.

### H x F Lattice Full Eight-Hook Coverage

Judgment: supported as architecture, open as empirical coverage.

The H x F lattice remains the right architecture: different hooks own different
failure modes, and Stop success does not demote PreToolUse. But the current
design overstates several `ACTIVE` cells if read as implemented or empirically
validated behavior. Only `PreToolUse:Bash` and `Stop` have useful empirical
Claude Code Desktop evidence. `PostToolUse`, `PostToolUseFailure`,
`SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`, and
`SubagentStop` still need hook-specific proof or explicit v1 stub status.

Design implication: the lattice should distinguish three statuses:
architectural owner, structural adapter implemented, and live behavior
validated. A cell can be architecturally assigned without being implemented.

### PreToolUse Runtime-Context Bridge

Judgment: delivery supported; behavior-lift contradicted for the current
content shape; role preserved.

Evidence supports `PreToolUse` as a model-visible hook boundary for Bash.
Evidence also proves real `CORTEX_RUNTIME_CONTEXT_V1` reached the model.
However, Gate 1 failed behaviorally. That is a content-shape and placement
failure for the current bridge, not proof that PreToolUse is the wrong lifecycle
surface.

Design implication: PreToolUse should remain responsible for pre-action
functions such as route/brake constraints, tool intent binding, write-surface
protection, and verified-work contract surfacing. The current
last-feedback-only text must not be promoted as behavior-lift evidence until it
is revised and rerun.

### Stop Closure Pressure

Judgment: supported narrowly and strongly.

The manual recalibration supports `Stop` as the right home for closure
pressure: pending goals, missing evidence, contradiction/degradation pressure,
and truthful refusal to close. It also confirms clean-window pass-through in
one manual control. The result refines the design by showing that Stop reasons
must be situated and non-harness-revealing; the earlier non-manual
`latched_brake` arm caused the model to inspect synthetic probe mechanics.

Design implication: Stop owns closure pressure, not the whole plugin. Stop
reasons should be bounded, task-local, and focused on the assistant's closure
claim, not on internal probe state or repo workflow grids.

### SessionStart / SessionEnd Cross-Session Resume

Judgment: current `session_id+cwd` assumption is contradicted for cross-thread
resume.

The runtime-context probe established that two fresh Code-tab threads on the
same sandbox had different `session_id` values. A persistence key that includes
`session_id` can be valid within one thread, but it does not earn cross-thread
resume. The design doc's SessionStart/SessionEnd story remains architecturally
plausible only if it uses a stable project-level resume index and treats
session-id-specific state as thread-local.

Design implication: SessionStart should not claim cross-session continuity
until a stable project fingerprint, resume index, and migration rule are
designed and tested. SessionEnd can persist bounded public state, but the
re-entry key is still open.

### Bundled Cortex Package Strategy

Judgment: open; structurally plausible but not tested.

The plugin docs and the recon around user-scope plugins support the need for a
bundled package: marketplace plugins are copied into a cache and cannot rely on
paths outside the plugin root unless deliberately symlinked or overridden for
developer mode. The empirical probes mostly imported `/Users/erikahoward/cortex-loop`
directly. That was acceptable recon, but it does not prove the bundled package
strategy.

Design implication: the bundle strategy should remain in the design, but it
needs its own structural install test before any shipping-readiness claim. The
plugin should make developer local-checkout overrides explicit and off by
default.

### Observe-Versus-Enforce Mode

Judgment: supported and refined.

The temporary probes repeatedly used baseline/no-op versus shaped/blocking
modes, which supports the design's observe-first posture. The manual Stop
recalibration shows why this matters: baseline logs can expose false closure
without changing behavior, and shaped mode can then be compared against the
same prompt family. The user-scope plugin loop also shows that enforce mode can
interact badly with unrelated validators when content asks for acknowledgements
or rigid output shapes.

Design implication: observe mode should log would-have-blocked decisions and
never inject or block. Enforce mode should be per-project, restart-aware, and
content-disciplined. It must be easy to disable without deleting evidence.

### State Persistence And Logging

Judgment: partially supported, with important refinements.

Plugin data directories successfully preserved evidence across temporary
install and cleanup. That supports a local persistence path. Raw logs were
acceptable for recon, but product defaults should remain redacted. The probes
also show that existing open sessions may call stale plugin paths after config
changes, so persistence and cache behavior must be versioned and restart-aware.

Design implication: persisted state needs schema and plugin-version metadata,
and hook commands should fail safely when cache/config mismatch is detected.

### Excluding The Mission Reflection Grid

Judgment: strongly supported.

The user-scope plugin PreToolUse probe interacted with the repo Stop validator
and produced a visible loop. That is direct evidence that the repo hygiene
apparatus must stay out of the product plugin. The product Stop hook should
validate Cortex closure pressure, not enforce repo closeout markdown.

## 3. Newly Observed Failure Modes The Design Must Accommodate

### Cached Hook Configuration Persists Across Config Changes

Observed failure: Codex App continued trying to execute an old project Stop hook
path after `.codex/config.toml` had been restored and the temporary hook file
removed. Claude recon cleanup also had to account for already-open sessions and
plugin cache paths.

Design constraint: v1 plugin updates must be thread-restart-aware. Do not
assume hot reload of hook config, hook command paths, or plugin code. Product
hooks should include version metadata in logs, tolerate stale invocations, and
avoid deleting or moving hook entrypoint paths while old threads can still call
them. Release notes and observe/enforce toggles should require closing and
reopening affected Claude Code Desktop threads.

### Structured-Output Enforcement Can Produce Rejection Loops

Observed failure: rigid Stop-hook demands for a specific repo reflection graph
can derail conversational turns, especially when the user asks clarifying
questions or when another hook injects acknowledgement text.

Design constraint: the product plugin must not use repo-governance structured
output enforcement. Stop closure pressure should be semantic and task-local:
block false closure, missing evidence, unresolved goal debt, and unsafe brake
state. It should not demand an exact markdown shape, acknowledge hook text, or
force a workflow artifact into normal conversation.

### Configuration Staleness Requires Session Restart

Observed failure: changing config files or plugin registries does not guarantee
that an already-open Code-tab or Codex App thread observes the change.

Design constraint: v1 mode changes, plugin updates, and hook enable/disable
changes should be treated as applying to new or restarted sessions unless a
specific hot-reload probe proves otherwise. The plugin should log mode and
version on every hook event so stale sessions are diagnosable.

### PostToolUseFailure Is Distinct From PostToolUse

Observed failure: current Claude Code docs expose `PostToolUseFailure` as a
separate event after failed tool execution. The design doc currently frames
failed tool output under `PostToolUse` only.

Design constraint: v1 must handle both `PostToolUse` and
`PostToolUseFailure`. Success classification belongs on `PostToolUse`; failure
classification, missing artifact, nonzero command, stderr, interruption, and
duration belong on `PostToolUseFailure`. Any PostToolUse-to-Stop lifecycle loop
must include both events or it will miss exactly the failure cases Cortex cares
about.

### Codex Cannot Produce Claude GUI Behavior Evidence Alone

Observed failure: GUI automation and accessibility/focus uncertainty made the
first Stop closure run muddier than necessary. The manual recalibration became
the trusted evidence because the user entered prompts directly in Claude Code
Desktop and the logs were checked afterward.

Design constraint: every future Claude Code Desktop behavior-lift probe must
name the operator split up front. Codex may prepare plugin state and inspect
logs; the user must enter the prompts and supply or preserve visible model
output. Behavior-lift evidence must not depend on Codex driving the Code-tab
GUI.

## 4. Architectural Questions Still Open

These questions are open because the existing evidence is insufficient, not
because the architecture has failed. Each probe below is named only as a future
minimal closure path; no probe is run by this document.

### Is PostToolUse / PostToolUseFailure -> Feedback -> Stop A Real Loop?

Smallest probe: in `/Users/erikahoward/cortex-plugin-sandbox`, use a temporary
user-scope plugin that logs both `PostToolUse` and `PostToolUseFailure`,
classifies the tool result into `ReferenceRealizationFeedback`, persists a
bounded summary, and lets a later Stop block once in shaped mode. The user
must manually enter one failing-command baseline, one failing-command shaped
arm, and one clean control.

### Does The Runtime-Context Bridge Need Content Revision Before PreToolUse Can Earn Lift?

Smallest probe: revise only the temporary `CORTEX_RUNTIME_CONTEXT_V1` content
shape, keep the same PreToolUse delivery mechanism, and rerun the Gate 1 paired
trials with baseline/shaped scoring. The change should test content shape, not
new architecture.

### Does Stop Closure Pressure Hold Across More Than The Manual Three-Case Subset?

Smallest probe: manually rerun a small Stop matrix with additional non-clean
families such as guarded brake, latched brake, verified artifact, and a neutral
conversation that asks a clarifying question. Score false-closure correction
and over-block risk separately.

### How Should SessionStart Be Redesigned Given Thread-Local Session IDs?

Smallest probe: log `SessionStart` and `SessionEnd` for two fresh Code-tab
threads on the same sandbox and one reopened thread, then test candidate
project fingerprints derived from `cwd`, `transcript_path`, and configured
project root. Do not emit model-visible context until stable keying is known.

### Does UserPromptSubmit Provide A Cleaner Prompt-Adjacent Constraint Surface?

Smallest probe: install a temporary user-scope `UserPromptSubmit` hook that
emits a bounded, non-acknowledgement sentinel or logs no-op depending on mode,
then manually verify whether it appears in the next model context without
creating a Stop loop.

### Can A Bundled Plugin Run Without Importing The Local Repo?

Smallest probe: install a local marketplace plugin whose cache contains the
minimal Cortex package subset and whose hook refuses to import from
`/Users/erikahoward/cortex-loop`. Run one dry hook invocation and one manual
Claude Code Desktop PreToolUse delivery check.

### Does User-Scope Plugin Behavior Hold In A Real Managed-Worktree Cwd?

Smallest probe: open a Claude Code Desktop Code-tab session that actually uses
`.claude/worktrees/...`, install only a user-scope plugin, and run one
`PreToolUse:Bash` sentinel check. The key evidence is the hook `cwd` and
process cwd, not the model's acknowledgement alone.

### How Strictly Must Plugin Update / Mode Changes Require Restart?

Smallest probe: in a disposable thread, change the temporary plugin hook
command or mode after the first event, then run another event in the same
thread and in a reopened thread. Compare logged plugin root, mode, and emitted
behavior.

## 5. Strategic Recommendation

This section is a recommendation for review, not a decision and not permission
to start work in this turn.

Options:

- Revise the runtime-context bridge content shape and rerun Gate 1. This is
  necessary before PreToolUse can earn behavior lift, but the design doc now has
  several stale assumptions that would make the next probe harder to interpret.
- Run the PostToolUse / PostToolUseFailure -> Stop lifecycle probe. This is
  high leverage because it tests the actual feedback-to-closure loop, but it
  requires user-entered manual trials and should not start until the design doc
  names `PostToolUseFailure`, restart staleness, and operator participation.
- Revise the design doc itself against this synthesis. This earns structural
  clarity only, not product behavior lift, but it prevents the next empirical
  seam from inheriting known stale claims.
- Do something else, such as resume the parked lifecycle-spine branch. The
  evidence argues against this now because that branch was built before the
  runtime-context failure, the Stop recalibration, the session-id finding, and
  the PostToolUseFailure distinction were integrated.

Recommendation: revise `docs/cortex_plugin/DESIGN.md` first, then choose the
next empirical probe. The design revision should be narrow: keep the H x F
lattice, keep Claude Code Desktop as a first-class host adapter, keep
PreToolUse as pre-action and Stop as closure-pressure, but downgrade unearned
hook cells from implemented behavior to architectural ownership or v1 stubs;
add `PostToolUseFailure`; remove any `session_id+cwd` cross-thread resume
claim; add restart/cache staleness as a deployment constraint; and state that
Claude Code Desktop behavior-lift probes require user-entered manual trials.

That path respects the evidence-vs-architecture distinction. A design-doc
revision would earn structural alignment only. Product behavior lift would
still require later live paired evidence on the specific lifecycle surface being
claimed.
