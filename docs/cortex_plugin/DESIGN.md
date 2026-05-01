# Cortex Claude Code Desktop Plugin Design

Surface: product design

Status: structural design only. This document defines the v1 Cortex plugin
for Claude Code Desktop's Code tab. It does not implement the plugin and does
not claim live model-output lift.

## 1. Identity

The Cortex Claude Code Desktop plugin is Cortex's first full-lifecycle
expression on a natural lifecycle surface. It is not generic hook middleware,
not a package of "PreToolUse and Stop bridges", and not a repo-governance
validator. `docs/CORTEX.md` §1 defines Cortex as the executive-function layer
that wraps a model after post-training: continuity across interruptions,
focused persistence, context adoption, uncertainty-aware brake, truthful
closure, and capability-aware routing. The plugin is that identity expressed
through Claude Code Desktop's Code-tab lifecycle events.

The OpenAI host-control lane in `cortex/hosts/openai/host_control.py` compresses
Cortex into request/response: bounded instructions and input text are the main
model-visible surfaces. Claude Code Desktop exposes richer lifecycle events:
`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
`PostToolUseFailure`, `PreCompact`, `SubagentStop`, `Stop`, and `SessionEnd`.
Those are the natural event boundaries for the lifecycle-first law in
`docs/CORTEX.md` §3. The plugin therefore wires Claude Code Desktop events into
existing `cortex/**` state and emits bounded hook outputs only when the Cortex
state needs to change what the assistant sees, does, or is allowed to close.

This design treats Claude Code Desktop as the intended v1 plugin surface
parallel to the current OpenAI API/CLI lane, but current operational truth
remains unchanged until build and live-eval seams land:
`docs/CORTEX_STATUS.md` still names `openai:operator_cli` as the shipping
default, while Claude remains conformant and non-default. Structural design
earns architecture only; live paired evidence earns behavior lift.

## 2. The H x F Lattice

Legend:

- `ARCHITECTURAL OWNER: <trace>` means the hook is assigned responsibility for
  the failure mode, but no Claude Code Desktop adapter behavior or paired live
  behavior evidence exists for that cell yet.
- `STRUCTURAL ADAPTER IMPLEMENTED: <trace>` means code exists under
  `cortex/hosts/claude_code_desktop/` for that hook path, but paired live
  behavior lift is not earned.
- `LIVE BEHAVIOR VALIDATED: <trace>` means paired empirical evidence exists
  that the Claude Code Desktop hook changed model behavior for that cell. This
  is still not a shipping-product claim unless the product adapter path is also
  built and promoted.
- `UNEARNED BEHAVIOR: <trace>` means delivery, state update, or model-visible
  context may be empirically confirmed, but the tested content shape failed or
  mixed against the target behavior and cannot count as live behavior
  validation.

| Failure mode from `docs/CORTEX.md` §2 | SessionStart | UserPromptSubmit | PreToolUse | PostToolUse | PostToolUseFailure | PreCompact | SubagentStop | Stop | SessionEnd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | ARCHITECTURAL OWNER: would restore thread-local commitment summaries for later certification; no adapter code. | ARCHITECTURAL OWNER: would normalize the prompt into an event envelope before model action; exact-output override claims are unearned. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` parses tool intent and can emit bounded runtime context; current content shape has no lift. | ARCHITECTURAL OWNER: would bind successful tool artifacts into commitment outcome; no adapter code. | UNEARNED BEHAVIOR: `PostToolUseFailure:Bash` delivery and persistence are live-confirmed, but later Stop repair was mixed at 2/3 shaped failure pairs. | ARCHITECTURAL OWNER: compaction provenance remains a v2 stub. | ARCHITECTURAL OWNER: subagent claim provenance remains a v2 stub. | UNEARNED BEHAVIOR: raw internal Stop wording reached the model, but Mac pending-goal retest repaired only 1/2 shaped trials and triggered hook-skepticism in 1/2. | ARCHITECTURAL OWNER: would persist bounded commitment summaries for the same thread and candidate resume state; no cross-thread proof. |
| Bounded correction and verified-work preservation | ARCHITECTURAL OWNER: would restore active work-contract residue within a thread; no adapter code. | UNEARNED BEHAVIOR: `UserPromptSubmit` delivered `hook_system_message`, but verified-work pressure did not override exact `TASK COMPLETE` instruction. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can inspect intended command before mutation; write-surface enforcement is not validated. | ARCHITECTURAL OWNER: would classify successful checks/artifacts into preservation state; no adapter code. | UNEARNED BEHAVIOR: missing-file and nonzero-exit classification persisted, but the feedback-to-Stop correction loop repaired only 2/3 shaped failure pairs. | ARCHITECTURAL OWNER: compaction verified-structure handoff remains a v2 stub. | ARCHITECTURAL OWNER: subagent repair provenance remains a v2 stub. | LIVE BEHAVIOR VALIDATED: manual Stop evidence corrected a false "tests proven green" closure after no tests were run. | ARCHITECTURAL OWNER: would preserve trusted/falsified structure summaries for thread-local re-entry; no cross-thread proof. |
| Uncertainty handling and brake | ARCHITECTURAL OWNER: would restore bounded brake history within the same thread; no adapter code. | ARCHITECTURAL OWNER: would price prompt uncertainty from missing anchors and prior feedback; no adapter code. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can emit a guarded last-feedback constraint; Gate 1 did not earn lift. | ARCHITECTURAL OWNER: would update feedback window from successful-but-warning tool results; no adapter code. | ARCHITECTURAL OWNER: would update feedback window from failed tool results and host friction; no adapter code. | ARCHITECTURAL OWNER: compaction-time brake handoff remains unearned. | ARCHITECTURAL OWNER: subagent uncertainty import remains unearned. | ARCHITECTURAL OWNER: guarded/latched-brake Stop behavior is assigned here but not live-validated in the trusted manual subset. | ARCHITECTURAL OWNER: would persist bounded brake summaries only; no adapter code. |
| Branch continuity, suspend/resume, and truthful closure | ARCHITECTURAL OWNER: would restore thread-local branch/goal refs; cross-thread resume keying is open. | UNEARNED BEHAVIOR: false-closure prevention at prompt submit failed when competing with the user's exact-output instruction; route/goal-state ownership remains open. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can surface active-goal constraints before action; Gate 1 content shape failed behaviorally. | ARCHITECTURAL OWNER: would mark continuity progress after successful tools; no adapter code. | UNEARNED BEHAVIOR: failed-tool continuity debt persisted into Stop, but shaped Stop did not reliably prevent false closure across all paired failures. | ARCHITECTURAL OWNER: compaction continuity is a v2 edge case. | ARCHITECTURAL OWNER: parent-branch re-entry from subagents remains a v2 seam. | UNEARNED BEHAVIOR: raw pending-goal Stop text corrected one Mac false closure but failed another by sounding like hidden framework/prompt-injection text. | ARCHITECTURAL OWNER: would consolidate thread-local open/closed/abandoned state; project-level resume is open. |
| Intervention pricing versus neutrality | ARCHITECTURAL OWNER: would restore budget/route residue for a thread; no adapter code. | ARCHITECTURAL OWNER: would choose inspect/execute/resume posture from prompt plus state; no adapter code. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can carry route/brake pricing into hook output; no behavior lift earned. | ARCHITECTURAL OWNER: would feed successful evidence progress back into route pricing; no adapter code. | ARCHITECTURAL OWNER: would feed failed-tool friction and degradation into route pricing; no adapter code. | ARCHITECTURAL OWNER: compaction pricing is v2. | ARCHITECTURAL OWNER: subagent route pricing is v2. | ARCHITECTURAL OWNER: Stop allow/block pricing is assigned here, but only closure-pressure behavior is validated. | ARCHITECTURAL OWNER: would publish removable score-pricing support, never policy law; no adapter code. |
| Blocker surfacing and goal-debt management | ARCHITECTURAL OWNER: would restore pending goal refs and closure pressure inputs; no adapter code. | UNEARNED BEHAVIOR: prompt-adjacent missing-evidence pressure did not overcome exact-output false-completion instructions; non-conflicting blocker creation is untested. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can inject missing-evidence constraints before action; Gate 1 did not earn lift. | ARCHITECTURAL OWNER: would classify evidence/continuity progress after successful tools; no adapter code. | UNEARNED BEHAVIOR: failed-tool blocker tags reached Stop, but one shaped failure pair repeated the false completion after the block. | ARCHITECTURAL OWNER: compaction blocker summaries are v2. | ARCHITECTURAL OWNER: subagent blockers must be re-owned in v2. | UNEARNED BEHAVIOR: blocker tags reached Stop and were model-visible, but raw tag names caused a Mac hook-skepticism failure in the pending-goal retest. | ARCHITECTURAL OWNER: would preserve unresolved blockers as bounded state; no cross-thread proof. |
| Multi-host executive continuity | ARCHITECTURAL OWNER: would initialize a Claude Code Desktop runtime session without flattening host differences; no adapter code. | ARCHITECTURAL OWNER: would map prompt events into shared Cortex law; exact-output behavior lift is unearned. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` converts a Claude hook affordance into the shared runtime-context bridge. | ARCHITECTURAL OWNER: would convert successful Claude tool results into shared feedback; no adapter code. | UNEARNED BEHAVIOR: failed Claude Bash results convert into shared feedback state, but the lifecycle loop has mixed behavior lift. | ARCHITECTURAL OWNER: compaction semantics are host-specific and unearned. | ARCHITECTURAL OWNER: subagent semantics are host-specific and unearned. | LIVE BEHAVIOR VALIDATED: Claude Stop semantics can deliver closure pressure to the model; product adapter still open. | ARCHITECTURAL OWNER: would persist host-local state in portable Cortex shape; cross-thread resume is unearned. |
| Offline consolidation and support geometry | ARCHITECTURAL OWNER: would restore explicit publications and support priors only after stable resume keying; no adapter code. | ARCHITECTURAL OWNER: would let fresh host-matched support priors bias score pricing; no adapter code. | STRUCTURAL ADAPTER IMPLEMENTED: `PreToolUse:Bash` can carry score-pricing context, but support-prior behavior is not validated. | ARCHITECTURAL OWNER: would collect publication candidates from successful public support snapshots; no adapter code. | ARCHITECTURAL OWNER: would collect degradation candidates from failed support snapshots; no adapter code. | ARCHITECTURAL OWNER: compaction-publication law is v2. | ARCHITECTURAL OWNER: subagent publication law is v2. | ARCHITECTURAL OWNER: Stop does not validate raw AUX memory; closure pressure must remain task-local. | ARCHITECTURAL OWNER: would build bounded episodes/publications while raw AUX stays support-side; no cross-thread proof. |

Coverage result: every Cortex failure mode has at least one assigned lifecycle
owner, but assignment is not implementation and implementation is not behavior
lift. Today only `PreToolUse:Bash` has a structural adapter path in
`cortex/hosts/claude_code_desktop/`. Standalone `Stop` closure pressure has
narrow paired manual behavior evidence for evidence-degradation and clean
no-over-block, but raw internal Stop wording is content-shape contaminated for
pending-goal after the Mac divergence retest repaired only 1/2 shaped trials.
`PostToolUseFailure -> Stop` has live delivery and persistence evidence but
mixed behavior at 2/3 shaped repairs.
`PreCompact` and `SubagentStop` remain explicit v2 stubs;
`PostToolUseFailure` is now a distinct v1 design event, not an alias for
`PostToolUse`.

## 3. Hook-by-Hook Design

### SessionStart

- Failure modes addressed: truth-preserving commitments, verified-work
  preservation, uncertainty brake, branch continuity, intervention pricing,
  blocker surfacing, multi-host continuity, offline consolidation.
- Input observation: `session_id`, `transcript_path`, `cwd`, model/version
  fields when present, project root, plugin config, and persisted thread-local
  state under `CLAUDE_PLUGIN_DATA`.
- State transition: load or initialize `cortex/hosts/claude/runtime.py::ClaudeRuntimeSession`
  for the current `session_id`. The runtime-context probe showed fresh Code-tab
  threads in the same `cwd` can receive different `session_id` values, so this
  hook must not claim cross-thread resume from `session_id+cwd` keying. It may
  restore only bounded thread-local branch registry, pending goals, brake tonic
  history, feedback window, preservation summaries, and explicit
  `OfflineSupportPublication` entries parsed by `cortex/aux/publication.py`.
- Model-visible output: observe mode emits nothing. Enforce mode may emit a
  bounded `CORTEX_SESSION_CONTEXT_V1` additional-context block only when
  restored state contains pending goal debt, a guarded/latched brake, or a
  host-matched publication that changes score pricing. Clean starts emit no
  block.
- Kill switch / observe mode: emit nothing when no prior state exists, when
  restored state is clean, or when `hooks.SessionStart=false`. Observe mode
  performs the restore and logs the would-have-emitted reason without
  additional context.
- Connectivity trace: `SessionStart` payload -> thread-local
  `ClaudeRuntimeSession` restore -> later `UserPromptSubmit`/`PreToolUse` route
  and `Stop` closure decisions -> additional context or block reason visible to
  the model. Project-level resume requires a future fingerprinting probe before
  it can be model-visible.
- Bounded outputs: session context is capped by `max_context_chars`, redacts raw
  transcript text, and names only state classes, pending anchors, and bounded
  constraints. It never emits raw AUX episodes.

### UserPromptSubmit

- Failure modes addressed: commitments, verified-work preservation,
  uncertainty brake, branch continuity, intervention pricing, blocker surfacing,
  multi-host continuity, offline consolidation.
- Input observation: user prompt text, `cwd`, `session_id`, `transcript_path`,
  prompt metadata, and prior `ClaudeRuntimeSession`.
- State transition: call existing Claude runtime ingress/driver logic when the
  prompt can be represented as a Claude host event, then update dispatch lane,
  branch/goal state, executive signal summary, operator task mode, route
  pricing, and feedback-window pressure through `cortex/hosts/claude/runtime.py`
  and `cortex/hosts/_executive_closure.py`.
- Model-visible output: enforce mode emits a bounded prompt-adjacent
  additional-context block only when Cortex has a non-clean constraint:
  unresolved goal debt, missing resume anchor, guarded brake, or immediate
  verification demand. If the prior newest feedback is noisy, prompt-adjacent
  use of `cortex/hosts/runtime_context.py::runtime_context_from_last_feedback`
  remains research-only until content shape earns lift at either
  `PreToolUse` or `UserPromptSubmit`. The UserPromptSubmit verified-work probe
  proved `hook_system_message` delivery and transcript-boundary behavior, but
  failed behavior lift when the hook-delivered instruction competed with the
  user's exact-output instruction. Therefore false-closure prevention at
  UserPromptSubmit remains unearned for exact-output-conflict prompts.
- Kill switch / observe mode: clean prompt plus clean state emits no block.
  Observe mode updates state and logs route/closure pressure but leaves the
  prompt unshaped. Route selection, brake-state setting, and verification
  demand on prompts that do not explicitly conflict with Cortex output remain
  architectural-owner functions pending separate probes.
- Connectivity trace: user prompt -> `ClaudeRuntimeSession`/route state ->
  bounded additional context before assistant planning or a later
  `PreToolUse`/`Stop` block -> changed assistant behavior.
- Bounded outputs: no accumulated memory, no summary counters as prompt text,
  no "nothing to report" stubs, max `max_context_chars`.

### PreToolUse

- Failure modes addressed: commitments, verified-work preservation, uncertainty
  brake, branch continuity, intervention pricing, blocker surfacing, multi-host
  continuity, offline support priors.
- Input observation: `tool_name`, `tool_input`, `tool_use_id`, `cwd`,
  `session_id`, `transcript_path`, permission mode, and prior session state.
- State transition: convert the tool intent into an event-local observation;
  use `cortex/sre/operator_routing.py` for route profile/budget, `cortex/sre/brake.py`
  for guarded/latched state, `cortex/runtime/operator_brain_capability.py` for
  capability envelope defaults, and support priors only through
  `OfflineSupportPublication` score-pricing inputs.
- Model-visible output: enforce mode may allow the tool with
  `hookSpecificOutput.additionalContext` carrying a bounded route/brake
  constraint only when `runtime_context.pretooluse_model_visible=true`. That
  flag may remain disabled by default because Gate 1 did not earn behavior
  lift. Tool blocking remains a separate future enforcement path when the route
  is `BLOCKED`, the tool would violate a verified-work allowed write surface,
  or a latched brake requires user/evidence recovery first.
- Kill switch / observe mode: emit nothing for low-risk inspect tools under
  clean state. Observe mode never blocks and records the would-have-blocked
  reason.
- Connectivity trace: PreToolUse payload -> Cortex route/brake/preservation
  assessment -> optional `additionalContext` or block decision -> the model's
  next post-tool message changes or the tool is prevented. The optional
  runtime-context branch is structural only until content-shape research earns
  live lift.
- Bounded outputs: context is imperative and local to the tool call, no
  acknowledgement requests, no generic advice, capped by `max_context_chars`.

### PostToolUse

- Failure modes addressed: commitments, verified-work preservation, uncertainty
  brake, continuity/closure, intervention pricing, blockers, multi-host
  continuity, offline consolidation.
- Input observation: `tool_name`, `tool_input`, successful tool
  result/status/stdout/stderr when exposed, `tool_use_id`, `cwd`, `session_id`,
  and transcript pointer.
- State transition: classify concrete artifacts, external records, evidence
  progress, continuity progress, warning codes, host friction, and probe status
  from successful or completed tool execution into `ReferenceRealizationFeedback`;
  append through
  `ReferenceRealizationFeedbackWindow`; update `ClaudeRuntimeSession`,
  preservation summaries, and closure pressure.
- Model-visible output: silent state update by default. If the hook output API
  supports additional context in the tested build, enforce mode may emit a
  bounded post-tool constraint when the tool result created a contradiction,
  verification gap, or stream-only/no-evidence condition. Otherwise the newest
  feedback is consumed by the next `PreToolUse` or `Stop`.
- Kill switch / observe mode: successful low-risk tool use with meaningful
  evidence progress emits nothing. Observe mode records feedback but never
  injects or blocks.
- Connectivity trace: PostToolUse result -> `ReferenceRealizationFeedback` ->
  future content-shaped runtime context or `Stop` closure pressure -> next
  model-visible constraint/block.
- Bounded outputs: newest feedback only; no accumulation beyond the three-entry
  internal window; raw stdout is not persisted unless user opts into raw logs.

### PostToolUseFailure

- Failure modes addressed: commitments, verified-work preservation, uncertainty
  brake, continuity/closure, intervention pricing, blockers, multi-host
  continuity, offline consolidation.
- Input observation: `tool_name`, `tool_input`, failure status, stderr,
  nonzero exit, missing-file signal, interruption/cancellation metadata,
  `tool_use_id`, `cwd`, `session_id`, and transcript pointer when exposed by
  Claude Code Desktop.
- State transition: classify failed tool execution as distinct
  `ReferenceRealizationFeedback`, not as a successful `PostToolUse` result.
  Failure classification should record evidence degradation, continuity debt,
  host friction, verification gaps, and preservation debt while keeping raw
  stderr/output out of default persisted state.
- Model-visible output: silent state update by default. Enforce mode should
  prefer bounded consumption by a later `Stop` block or future content-shaped
  `PreToolUse`/`UserPromptSubmit` signal. It must not produce conversational
  acknowledgement demands.
- Kill switch / observe mode: observe mode logs the failure classification and
  would-have-blocked closure tags only. Paired manual evidence for the
  PostToolUseFailure -> feedback -> Stop loop confirmed hook delivery,
  persisted bounded feedback state, Stop readback, and a clean no-over-block
  control, but behavior lift was mixed: shaped Stop repaired 2/3 failure pairs
  and failed 1/3. Enforce mode for this loop therefore stays cautious and
  block-once; it does not yet count as clean live behavior validation.
- Connectivity trace: PostToolUseFailure payload -> newest
  `ReferenceRealizationFeedback` -> `Stop` closure pressure or a later
  content-shaped pre-action signal -> model-visible recovery or truthful
  blocked status.
- Bounded outputs: newest feedback only, capped by `max_context_chars`; raw
  stderr/output requires explicit raw developer logging.

### PreCompact

- Failure modes addressed: v2 candidate for continuity, verified-work
  preservation, blocker surfacing, and offline consolidation.
- Input observation: compaction metadata and transcript pointer if exposed.
- State transition: v1 records a minimal compaction marker in session state and
  performs no summary generation. v2 will promote this to a packet-shaped
  compaction handoff only after empirical proof that the event exposes enough
  context and that the generated handoff reaches the post-compaction model.
- Model-visible output: silent state update only in v1.
- Kill switch / observe mode: disabled by default; when enabled, still no
  additional context in v1.
- Connectivity trace: v1 has no model-visible trace and is therefore a stub,
  not a product claim. The v2 trace must be: PreCompact payload -> bounded
  continuity/verified-work handoff -> post-compaction model-visible context.
- Bounded outputs: no raw transcript summarization in v1.

### SubagentStop

- Failure modes addressed: v2 candidate for commitments, verified-work
  preservation, branch continuity, blocker surfacing, and multi-host continuity.
- Input observation: subagent identifier, parent session, subagent output, and
  transcript pointer if exposed.
- State transition: v1 records only a bounded subagent-stop marker so parent
  SessionEnd can avoid treating unreviewed subagent output as certified work.
  It does not import subagent claims into Cortex law.
- Model-visible output: silent state update only in v1.
- Kill switch / observe mode: disabled by default; no additional context in v1.
- Connectivity trace: v1 intentionally has no model-visible path and is a
  stub. v2 must prove parent re-entry: SubagentStop payload -> provenance-bound
  subagent result -> parent `Stop`/`PreToolUse` behavior.
- Bounded outputs: no raw subagent transcript persistence by default.

### Stop

- Failure modes addressed: commitments, verified-work preservation,
  uncertainty brake, continuity/closure, intervention pricing, blockers, and
  multi-host continuity.
- Input observation: `last_assistant_message`, `transcript_path`, `session_id`,
  `cwd`, `stop_hook_active`, permission mode, and current `ClaudeRuntimeSession`.
- State transition: parse the last assistant message for closure claims and
  evidence markers; combine with `ClosurePressureState` from
  `cortex/sre/goal_debt.py`, newest `ReferenceRealizationFeedback`,
  preservation status, brake state, route profile, and commitment status.
- Model-visible output: enforce mode returns `decision: block` with a bounded
  reason when closure is premature, evidence is missing, brake is guarded or
  latched, verified-work preservation is unresolved, or a blocked route was
  ignored. The reason instructs the model to recover evidence, ask for missing
  context, or state blocked status; it does not ask for hook acknowledgement.
  Standalone Stop closure pressure is the only Claude Code Desktop bridge with
  narrow paired behavior-lift validation so far. Stop consumption of
  PostToolUseFailure feedback has delivery and persistence proof but mixed
  correction, so the product design must keep those claims separate.
- Kill switch / observe mode: allow clean stops when no closure pressure,
  no blocker, no verification debt, and no guarded/latched brake exists. Observe
  mode records the would-have-blocked reason but returns continue. Enforce mode
  uses a block-once safety wrapper per thread so repeated Stop attempts cannot
  create the structured-output rejection loop observed in earlier probes.
- Connectivity trace: Stop payload -> Cortex closure/brake/preservation state
  -> block reason -> model-visible continuation that repairs or refuses closure.
- Bounded outputs: block reason max `max_context_chars`, one or two actionable
  constraints, no workflow Mission Reflection grid, no repo-quality validation.

### SessionEnd

- Failure modes addressed: commitments, verified-work preservation,
  uncertainty brake, branch continuity, intervention pricing, blockers,
  multi-host continuity, offline consolidation.
- Input observation: session id, cwd/project root, final session state, feedback
  window, support snapshot, and plugin config.
- State transition: serialize the final `ClaudeRuntimeSession`; convert public
  support snapshots into `SupportMemoryEpisode` with
  `cortex/aux/persistence.py`; optionally build `OfflineSupportPublication`
  through `cortex/aux/publication.py`; keep support priors in the publication
  shape used by `cortex/aux/support_priors.py`.
- Model-visible output: silent state update only. The behavior change happens
  only when a later event in the same thread or a future earned project-resume
  key consumes the publication-shaped state.
- Kill switch / observe mode: if the session has no meaningful state change,
  write no episode and no publication. Observe mode persists diagnostic state
  but does not make publications eligible for score pricing.
- Connectivity trace: SessionEnd public support snapshot -> bounded episode /
  `OfflineSupportPublication` -> thread-local score pricing or closure pressure
  -> later additional context/block decision. Cross-thread resume remains open
  until project-fingerprint keying is tested.
- Bounded outputs: raw transcripts are dropped by default; publication refs,
  tags, and metadata are bounded and redacted.

## 4. State Persistence and Lifecycle

The plugin state lives under the Claude plugin data root, not inside the user's
repo by default:

```text
${CLAUDE_PLUGIN_DATA}/cortex/
  config.json
  sessions/<project_fingerprint>/<session_id>.json
  feedback/<project_fingerprint>/<session_id>.jsonl
  publications/<project_fingerprint>/*.json
  aux/support_memory.sqlite3
  logs/*.jsonl
```

`session_id` is thread-local until proven otherwise. The runtime-context probe
showed two fresh Code-tab threads in the same sandbox with different
`session_id` values, so `session_id+cwd` is not a cross-thread resume key.
`project_fingerprint` is a namespace for logs and candidate resume state, not a
claim that resume is earned. It is derived from the normalized project root and
never from a managed worktree suffix alone. The managed-worktree probes show
two realities that the build must handle: project-local settings can fire
inside `.claude/worktrees/...`, while user-scope plugins in the sandbox saw the
project root as `cwd`. The plugin therefore normalizes the project root from
the best available tuple: `cwd`, `transcript_path`, and configured repo root
allowlist.

Within a session, `ClaudeRuntimeSession` is the spine. Hooks load, update, and
persist that session at event boundaries only. No background timers, polling,
or opportunistic state mutation are allowed. `ReferenceRealizationFeedback`
entries remain bounded to the newest internal window; model-visible runtime
context uses only the newest feedback object.

Across threads, resume is an explicit open question, not a v1 claim. A future
probe must earn a stable project fingerprint from `cwd`, `transcript_path`, and
configured project root before `SessionStart` re-enters `SessionEnd` state from
another thread. Until then, `SessionEnd` may consolidate only bounded candidate
support state: branch/goal refs, brake history summaries, commitment summaries,
verified-work preservation summaries, support references, and publication
tags. Raw transcript text, raw tool output, personal file contents, and raw AUX
SQLite episodes are not model-visible and are not re-entered directly.
`SessionStart` restores only state whose thread-local or project-resume key is
earned; raw AUX memory remains support-side.

## 5. User Configuration

The v1 config is intentionally small and defaults to observe-first:

```json
{
  "mode": "observe",
  "hooks": {
    "SessionStart": true,
    "UserPromptSubmit": true,
    "PreToolUse": true,
    "PostToolUse": true,
    "PostToolUseFailure": true,
    "PreCompact": false,
    "SubagentStop": false,
    "Stop": true,
    "SessionEnd": true
  },
  "max_context_chars": 720,
  "logging_level": "redacted",
  "repo_roots": [],
  "runtime_context": {
    "pretooluse_model_visible": false
  },
  "closure_validation": {
    "allowlist_repo_roots": [],
    "block_on_unresolved_goal_debt": true,
    "block_on_guarded_or_latched_brake": true,
    "block_on_missing_verification": true
  },
  "privacy": {
    "persist_raw_hook_input": false,
    "persist_raw_tool_output": false,
    "telemetry": "off"
  }
}
```

`mode=observe` updates state, logs decisions, and reports would-have-blocked
reasons without changing model behavior. `mode=enforce` allows bounded
additional context and block decisions, except that PreToolUse runtime-context
emission may remain disabled by default through
`runtime_context.pretooluse_model_visible=false` until content-shape research
earns behavior lift. Users should install in observe mode, review logs, then
opt into enforce mode per repo root.

### Deployment Constraints

- Hook config caching: Codex App and Claude Code Desktop evidence both show
  that already-open threads can keep stale hook command paths after config or
  plugin edits. Plugin updates must be restart-aware and must preserve old
  entrypoints long enough for stale sessions to fail safely.
- Configuration staleness: mode changes, hook enable/disable changes, and
  plugin updates apply only to new or restarted sessions unless a specific
  hot-reload probe proves otherwise. Every hook log should include plugin
  version, Cortex version, schema version, mode, and runtime-context emission
  flags.
- Structured-output rejection loops: product hooks must not demand repo
  workflow grids, exact markdown shapes, or acknowledgement strings. Stop
  closure pressure is semantic and task-local; it blocks false closure,
  unresolved evidence debt, or unsafe brake state without turning normal
  conversation into a validator loop.
- Codex/user operator split: Codex can prepare plugin files, arm modes, inspect
  logs, and analyze evidence. Codex cannot drive Claude Code Desktop's GUI,
  type into the Code tab, or observe model responses directly. Any Claude Code
  Desktop behavior-lift probe requires the user to enter prompts manually and
  preserve or report visible output.

### Model-Facing Translation Boundary

Raw Cortex state is not safe hook prose. The Mac pending-goal divergence retest
showed that the raw Stop reason `Cortex blocked closure:
continuity_reminder, pending_goal_debt. Recover evidence, continuity, or brake
state before closing.` repaired one shaped trial but caused another shaped
trial to treat the hook feedback as suspicious/prompt-injection-shaped text.

The v1 plugin therefore needs a hard translation boundary:

- internal tags such as `continuity_reminder`, `pending_goal_debt`,
  `degradation_pressure`, brake states, route names, schema ids, and Cortex
  event labels remain in logs and persisted state only;
- model-visible hook output is compiled into plain task facts, missing
  evidence, and the next required action;
- block reasons must be situated to the actual unsupported claim, failed tool,
  missing file, absent test command, or unresolved goal;
- hook text must not sound like a hidden framework, policy engine, validator,
  or out-of-band command channel.

Example model-facing Stop text for pending-goal closure:

```text
You just replied "MIGRATION COMPLETE", but no migration was run or verified in
this conversation. Retract the completion claim, state that no verification was
performed, and ask what migration or verification command should be checked.
```

Example model-facing Stop text for evidence-degradation closure:

```text
You just replied "TESTS PROVEN GREEN", but no test command was run in this
conversation. Retract the claim, state that tests were not run, and ask for the
test command or run an actual verification step if available.
```

This translation boundary is now a design requirement, not polish. It is the
smallest way to preserve the H x F lifecycle lattice while admitting the
evidence that raw bridge content can defeat the behavior it is supposed to
improve.

## 6. Cortex Packaging Strategy

The plugin bundles the Cortex Python package. This is Option A: users installing
the plugin do not need a `cortex-loop` checkout, and the hook scripts do not
import from the host repo. The build-phase refinement is that Claude Code
Desktop is a first-class Cortex host adapter under
`cortex/hosts/claude_code_desktop/`; plugin scripts are transport wires over
that adapter, not plugin-side Cortex logic. See `docs/cortex_plugin/ADAPTER.md`
for the adapter pattern. The plugin distribution includes:

- `cortex/core/**`
- `cortex/drivers/**`
- `cortex/sre/**`
- `cortex/runtime/**`
- `cortex/hosts/**`
- `cortex/aux/**`
- `cortex/__init__.py` and package metadata needed for imports

The plugin distribution excludes `internal/**`, `lab/**`, `tests/**`,
`docs/**`, `.cortex/**`, and repo workflow hooks. Hook scripts resolve the
bundled package by prepending the plugin vendor directory to `PYTHONPATH`, for
example:

```text
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/vendor/cortex-loop:${PYTHONPATH}"
```

The bundled Cortex version is authoritative for that plugin installation.
Version skew with a user's local `cortex-loop` checkout is not a normal user
case because users should not need a checkout. If a checkout is detected for
developer debugging, the plugin logs the skew and still imports the bundled
package unless an explicit developer override is set.

Plugin updates synchronize by shipping a new bundle with a Cortex version
manifest. Session state includes `cortex_version`, `plugin_version`, and schema
version; SessionStart performs schema migration only at event boundaries.

The first structural build seam wires only `PreToolUse:Bash` end-to-end through
`cortex/hosts/claude_code_desktop/ingress.py`,
`cortex/hosts/claude_code_desktop/runtime.py`, and
`cortex/hosts/claude_code_desktop/hook_control.py`. Other hook scripts may
exist in the plugin skeleton as no-op transport stubs; they do not count as
implemented Cortex behavior until their adapter paths and tests land.
The trusted Stop closure-pressure behavior evidence came from temporary manual
probe plugins, not from a product Stop adapter under
`cortex/hosts/claude_code_desktop/`.

## 7. Multi-Host Shipping Truth

The precise target claim after the build phase is:

> Claude Code Desktop Code tab can run Cortex as a user-scope plugin that
> observes the Code-tab lifecycle, updates existing Cortex session state, and
> uses Claude hook outputs to shape or block model-visible behavior in enforce
> mode.

That would make Claude Code Desktop a shipping Cortex surface parallel to the
OpenAI host-control lane. This design does not change current shipping truth:
`internal/truth/cortex_status.json` and `docs/CORTEX_STATUS.md` still name
`openai:operator_cli` as the shipping default. The build seam may earn
structural shipping readiness; live shipping lift requires paired evaluation
evidence showing Input A -> Cortex-shaped lifecycle -> improved Output B.
Given the current evidence, v1 may need to ship with translated Stop closure
pressure as the only active Claude Code Desktop behavior-lift bridge enabled by
default, and even that needs the model-facing translation boundary above before
product enforcement. Raw internal Stop wording is no longer eligible as the
default content shape. `PreToolUse` and `UserPromptSubmit` should remain
architectural owners and may run in observe mode for route/brake/logging state,
but their model-visible runtime-context or prompt-shaping behavior needs
separately earned content-shape evidence before default enforcement.

Truth distinctions from `docs/CORTEX.md` §3:

- Cortex truth: the lifecycle-first law and hook mapping are defined here.
- Brain-wiring truth: how Claude's model responds to injected constraints is
  empirical and must be measured.
- Conformance truth: existing Claude conformance remains about the operator
  CLI lane unless plugin conformance tests are added.
- Shipping truth: status registry changes only after build + validation +
  live-evidence gates.

Required evidence before any live shipping-lift claim:

- structural hook tests for every hook claimed as implemented;
- empirical proof that each model-visible emit reaches the Code-tab model;
- paired baseline-vs-shaped tasks scored against premature closure, evidence
  recovery, and goal continuity;
- no over-constraint regression beyond the runtime-context rubric threshold;
- explicit proof that AUX remains publication-only and score-pricing-only.

## 8. What's Empirically Established About Bridge Authority

Current Claude Code Desktop evidence separates hook delivery, model-visible
delivery, behavior lift, and product/shipping truth:

- `Stop` block is the only bridge with any narrow paired behavior-lift
  validation, but that validation is now content-shape constrained. The Stop
  closure recalibration probe showed shaped block reasons corrected a
  pending-goal false closure and a missing-evidence false closure while the
  clean control still closed cleanly. The Mac pending-goal divergence retest
  then showed the same raw internal pending-goal reason repaired only 1/2
  shaped trials and caused hook-skepticism in the other. This validates Stop
  delivery and a closure-pressure intervention shape, not raw Cortex wording
  and not a Stop-primary architecture.
- `PreToolUse:Bash` delivery and model visibility are proven for
  `hookSpecificOutput.additionalContext`, but the runtime-context content shape
  did not reliably improve behavior: the paired Gate 1 result included one win,
  one no-change, one regression, and one neutral.
- `UserPromptSubmit` delivery and transcript-boundary behavior are proven for
  `hook_system_message`, but the verified-work probe failed behavior lift when
  the hook instruction competed with a user exact-output instruction. The model
  prioritized the explicit `TASK COMPLETE` request in that tested shape.
- `PostToolUseFailure:Bash` and `PostToolUse:Bash` event distinction is proven:
  failed Bash routed through `PostToolUseFailure`, clean Bash routed through
  `PostToolUse`, and failed-tool feedback persisted into later Stop state.
  The lifecycle loop's behavior was mixed: shaped Stop repaired 2/3 failure
  pairs and repeated false closure in 1/3, while the clean control did not
  block.
- Product/shipping truth is not earned by any temporary manual plugin. These
  probes constrain the design; they do not promote Claude Code Desktop to the
  shipping default and do not claim product adapter behavior until code under
  `cortex/hosts/claude_code_desktop/` lands and is evaluated.

Design consequence: bridge authority is per surface and per content shape. A
confirmed hook can own a lifecycle cell structurally, and a delivered message
can be visible to the model, while still failing to earn behavior lift under a
specific competing instruction. Future probes must test the smallest bridge
claim they intend to promote instead of averaging mixed outcomes into a general
"Claude hooks work" verdict.

Additional design consequence: model-visible hook content requires a compiler.
The product plugin should not send internal Cortex tags, framework names, or
schema labels directly to Claude. A Stop block reason that is internally
`pending_goal_debt` must become a plain statement that the assistant claimed
completion without running or verifying the relevant work. A Stop block reason
that is internally `degradation_pressure` must become a plain statement that a
test or evidence claim was made without the corresponding command or artifact.

## 9. Privacy, Logging, Observability

Default logging is redacted and local. Redacted logs include hook event name,
timestamp, project fingerprint, route profile, brake state, closure reason tags,
whether context/block output was emitted, and deterministic error classes. They
do not include raw user prompts, raw assistant messages, raw tool output, raw
file contents, or secrets.

`logging_level` values:

- `off`: no diagnostic logs beyond fatal local errors.
- `redacted` (default): bounded metadata and Cortex state classes only.
- `metadata`: includes hook top-level field names and sizes.
- `raw`: opt-in developer mode only; stores raw hook input/tool output and must
  be visually marked in logs.

Telemetry is off by default. Any future telemetry must be opt-in, local-first,
and separate from Cortex law. Persisted state is used only for lifecycle
continuity and publication-shaped support; it is not a user-facing memory
feature.

## 10. Known-Open Empirical Questions

1. Managed-worktree user-scope cwd. `docs/recon/claude_code_user_scope_plugin_managed_worktree_probe.md`
   confirmed user-scope plugin firing in an unrelated sandbox whose `cwd` was
   the project root, not `.claude/worktrees/...`; it therefore does not prove an actual managed-worktree cwd case. If a future Code-tab subject uses an actual managed-worktree cwd, the design changes by requiring stronger root normalization and state-key migration tests.
2. Hook output semantics beyond `PreToolUse:Bash` and `Stop`. Empirical probes
   confirmed `PreToolUse` additional context and Stop block continuation. If
   `SessionStart`, `UserPromptSubmit`, `PostToolUse`, or
   `PostToolUseFailure` cannot emit additionalContext in practice, their v1
   content remains state-update-only and the model-visible path must route
   through `PreToolUse`, `UserPromptSubmit`, or `Stop` only after those paths
   are separately earned.
3. Non-Bash tool coverage. Current probes exercised Bash. If other tools expose
   different payload shapes, the build must add per-tool observation adapters
   before enforcing on those tools.
4. Plugin update hot reload. If Claude Code Desktop caches plugin hook commands
   per thread, updates require thread restart. The plugin must log version skew
   and avoid assuming hot reload.
5. Live over-constraint risk. If runtime context causes correct outputs to be
   refused under irrelevant prior warnings, enforce mode must narrow emit
   predicates before any shipping-lift claim.
6. Project-fingerprint resume keying. `session_id+cwd` does not earn
   cross-thread resume. A future SessionStart/SessionEnd probe must establish
   whether `cwd`, `transcript_path`, configured project root, or another stable
   key can safely re-enter bounded state across fresh Code-tab threads.
7. Non-conflicting UserPromptSubmit behavior. The verified-work probe failed
   when the hook-delivered instruction competed with a user exact-output
   instruction. A future prompt-submit probe must test route selection,
   brake-state setting, and verification demand on tasks without exact-output
   conflict before those cells can move beyond architectural ownership.
8. PostToolUseFailure-to-Stop correction consistency. The lifecycle loop proved
   failed-tool feedback persistence into Stop but repaired only 2/3 shaped
   failure pairs. A future probe must test whether more situated block reasons,
   less internal Cortex vocabulary, or stricter closure-tag predicates make the
   loop reliable without over-blocking clean closure.

### PreToolUse Content Shape Research

Gate 1 finding: real `CORTEX_RUNTIME_CONTEXT_V1` content reached Claude Code
Desktop through `PreToolUse:Bash` additional context, but paired behavior was
mixed: one shaped win, one no-change, one shaped regression, and one neutral.
That is a content-shape failure for the current bridge, not proof that
`PreToolUse` is the wrong lifecycle surface.

Content-shape hypotheses worth testing before enabling PreToolUse runtime
context by default:

- Situated failure description versus generic constraint. A message that names
  the specific failed command, missing artifact, or unverified claim may work
  better than a generic route/brake schema.
- Short pointed signal versus full schema. A compact one- or two-sentence
  instruction may outperform the current multi-field `CORTEX_RUNTIME_CONTEXT_V1`
  shape by reducing model distraction and harness leakage.
- Conditional invocation only on strong prior signal. Runtime context may need
  to emit only after high-confidence evidence degradation, missing-file output,
  latched brake, or explicit continuity debt, not after every noisy feedback
  object.
- Possible relocation to `UserPromptSubmit`. If prompt-adjacent constraints are
  easier for Claude Code Desktop to use than pre-tool constraints, the same
  content family should be tested at `UserPromptSubmit` before concluding that
  the content cannot lift behavior.

v1 may need to ship with PreToolUse runtime context disabled by default, while
still keeping the `PreToolUse:Bash` structural adapter available for observe
logs, route/brake pricing, and future content-shape trials. Pending this
research, translated Stop closure pressure is the only plausible actively
firing Claude Code Desktop bridge for default enforcement, and its translated
content shape still needs to be earned separately from the raw internal wording
used in the temporary probes.

## 11. v2 Deferrals

- `PreCompact`: v1 installs a stub only. v2 promotion requires empirical proof
  that the event exposes enough context and that a bounded continuity /
  verified-work handoff reaches the post-compaction model without becoming a
  second memory system.
- `SubagentStop`: v1 installs a stub only. v2 promotion requires provenance law
  for parent/subagent claims, parent re-entry behavior, and evidence that
  subagent output changes parent model behavior through Cortex rather than
  becoming raw imported text.
- Dynamic Claude brain-capability inference: queued behind
  `brain-capability-observation-and-inference`; v1 uses the standard envelope
  unless explicit publication-shaped evidence earns a later seam.
- Rich verified-work protocol for Claude Code Desktop: v1 protects closure and
  allowed-write surfaces; full file-block repair parity with OpenAI verified
  work waits for a dedicated build/eval seam.
- User-facing memory: not v1 and not a Cortex plugin goal. Support geometry
  remains removable publication-shaped state, not a memory product.

## 12. Closure-Line Discipline

This design does not bundle, invoke, or replicate the Cortex Mission Reflection
grid, `grid-validate`, the closeout contract, or any repo-governance hook.
`docs/CORTEX.md` §6 is explicit: the hygiene apparatus is not Cortex. The
plugin's Stop hook performs Cortex closure validation: closure pressure,
blocker surfacing, brake state, verification debt, preservation state, and
commitment support. It does not grade engineering quality or produce the
development workflow graph.

This design also does not include:

- generic instruction-following improvements;
- politeness, tone, or general reasoning improvements;
- post-training calibration;
- a closed-loop monitor that observes without changing model-visible context or
  route/block behavior;
- user-facing memory features;
- raw AUX memory re-entry;
- AUX routing, certification, or blockedness mutation;
- broad host automation unrelated to the eight Cortex failure modes;
- background polling, timers, or hidden state mutation.

Every future attempt to add one of those features must name a new Cortex
failure-mode trace or be rejected as generic bloat or post-training territory.

## 13. Validation Gates Before Build Phase

No plugin code should be written until this design passes these gates:

- Every lattice cell uses exactly one evidence status:
  `ARCHITECTURAL OWNER`, `STRUCTURAL ADAPTER IMPLEMENTED`,
  `LIVE BEHAVIOR VALIDATED`, or `UNEARNED BEHAVIOR`.
- Every `STRUCTURAL ADAPTER IMPLEMENTED` cell names the
  `cortex/hosts/claude_code_desktop/` path that makes it structural.
- Every `LIVE BEHAVIOR VALIDATED` cell names the paired empirical evidence and
  still avoids a shipping claim unless product adapter code also exists.
- Every `UNEARNED BEHAVIOR` cell names the delivery/state fact and the failed
  or mixed behavior result that prevents live validation.
- Every failure mode in `docs/CORTEX.md` §2 has at least one assigned lifecycle
  owner, without confusing ownership for implementation.
- `PostToolUseFailure` is treated as distinct from `PostToolUse`.
- `PreCompact` and `SubagentStop` are explicitly stubbed with v2 promotion
  paths; no other hook is empty by accident.
- Cross-thread resume is not claimed until project-fingerprint keying is
  empirically earned.
- Deployment constraints for hook caching, session restart, structured-output
  loops, and the Codex/user operator split are named.
- PreToolUse content-shape research is named, and PreToolUse runtime context is
  allowed to remain disabled by default.
- The design keeps live-evidence and structural-evidence claims separate.
- The design does not update shipping truth before build/eval evidence.
- AUX remains publication-only and score-pricing-only; raw AUX episodes do not reach the model and cannot mutate routing, certification, or blockedness.
- The plugin uses existing `cortex/**` modules and does not reimplement Cortex
  law in hook scripts.
- Every model-visible emit has a bounded output discipline and a clean-window
  kill switch.
- The plugin excludes the repo hygiene apparatus from product packaging.
- Known empirical questions are named with design-change consequences.
