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
`PreCompact`, `SubagentStop`, `Stop`, and `SessionEnd`. Those are the natural
event boundaries for the lifecycle-first law in `docs/CORTEX.md` §3. The plugin
therefore wires Claude Code Desktop events into existing `cortex/**` state and
emits bounded hook outputs only when the Cortex state needs to change what the
assistant sees, does, or is allowed to close.

This design establishes Claude Code Desktop as the intended v1 shipping Cortex
surface parallel to the current OpenAI API/CLI lane. In short, it establishes
Claude Code Desktop as the intended v1 shipping Cortex surface, but current operational truth
remains unchanged until the build and live-eval seams land: `docs/CORTEX_STATUS.md`
still names `openai:operator_cli` as the shipping default, while Claude remains
conformant and non-default. Structural design earns the architecture; live paired evidence earns shipping lift.

## 2. The H x F Lattice

Legend:

- `ACTIVE: <trace>` means the hook contributes real v1 behavior for the failure
  mode. The trace names the shortest path from hook input to Cortex state to
  behavior.
- `DEFERRED: <reason>` means the hook is installed in v1 but has only a stub or
  metadata capture until a v2 promotion seam.
- `N/A: <reason>` means the failure mode does not naturally manifest at that
  hook; another hook covers the mode.

| Failure mode from `docs/CORTEX.md` §2 | SessionStart | UserPromptSubmit | PreToolUse | PostToolUse | PreCompact | SubagentStop | Stop | SessionEnd |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Truth-preserving commitments and bounded certification | ACTIVE: restore prior commitment summaries into `ClaudeRuntimeSession` for later certification. | ACTIVE: normalize prompt into event envelope and dispatch lane before model action. | ACTIVE: bind tool intent/provenance before execution; can block unsupported consequential action. | ACTIVE: bind tool result artifact/external record into commitment outcome. | DEFERRED: compaction provenance will need a packet-shaped summary in v2. | DEFERRED: subagent claims need separate provenance binding in v2. | ACTIVE: block closure that asserts unsupported or boundary-broken work. | ACTIVE: persist bounded commitment summaries, not raw transcript claims. |
| Bounded correction and verified-work preservation | ACTIVE: restore active work-contract and preservation residue if present. | ACTIVE: detect task/repair intent and set verification demand. | ACTIVE: protect allowed write surface before a tool mutates files. | ACTIVE: classify result evidence and update preservation state from observed checks. | DEFERRED: compaction can damage repair context; v2 will summarize verified structure. | DEFERRED: subagent repair provenance is a v2 seam. | ACTIVE: block finalization when verification debt or preserved structure is unresolved. | ACTIVE: preserve trusted/falsified structure summaries for the next session. |
| Uncertainty handling and brake | ACTIVE: restore brake tonic history and prior feedback pressure. | ACTIVE: price uncertainty from prompt context, missing anchors, and prior feedback. | ACTIVE: inject guarded constraints or block risky tool use under latched brake. | ACTIVE: update feedback window from tool failure, warning, or stream-only progress. | DEFERRED: compaction-time brake handoff needs live proof. | DEFERRED: subagent uncertainty import is v2. | ACTIVE: block closure or ask for evidence under guarded/latched brake. | ACTIVE: persist bounded brake history and discard raw uncertainty chatter. |
| Branch continuity, suspend/resume, and truthful closure | ACTIVE: restore branch registry, active track, pending goals, and reminders. | ACTIVE: update branch/goal state from user intent and transcript cues. | ACTIVE: inject active-goal constraints before tools that could drift or close prematurely. | ACTIVE: mark continuity progress from artifacts, branch close, or returned-to-main signals. | DEFERRED: compaction is a continuity edge case; v2 will preserve active anchors. | DEFERRED: subagent results need parent-branch re-entry law. | ACTIVE: block "done" when branch or goal debt remains unresolved. | ACTIVE: consolidate open/closed/abandoned branch state. |
| Intervention pricing versus neutrality | ACTIVE: restore budget, route, and modulator residue. | ACTIVE: choose inspect/execute/resume posture from user prompt plus state. | ACTIVE: route tool action as inspect, guarded execute, or blocked. | ACTIVE: feed host friction and evidence progress back into route pricing. | DEFERRED: compaction pricing is v2. | DEFERRED: subagent route pricing is v2. | ACTIVE: decide whether to allow stop, re-prompt, or require a check. | ACTIVE: publish only removable score-pricing support, never policy law. |
| Blocker surfacing and goal-debt management | ACTIVE: restore pending goal refs and closure pressure inputs. | ACTIVE: create/update goal debt from unresolved user requests. | ACTIVE: block irreversible tools or inject missing-evidence constraints. | ACTIVE: classify whether evidence/continuity moved after tool use. | DEFERRED: compaction blocker summaries are v2. | DEFERRED: subagent blockers must be re-owned in v2. | ACTIVE: surface blockers through `decision: block` rather than fluent closure. | ACTIVE: preserve unresolved blockers as bounded session state. |
| Multi-host executive continuity | ACTIVE: rehydrate a Claude host runtime session without flattening host differences. | ACTIVE: map Claude prompt event into shared Cortex runtime law. | ACTIVE: convert Claude hook affordance into Cortex route/brake behavior. | ACTIVE: convert Claude tool result into shared `ReferenceRealizationFeedback`. | DEFERRED: compaction semantics are host-specific and unearned. | DEFERRED: subagent semantics are host-specific and unearned. | ACTIVE: use Claude Stop semantics for Cortex closure pressure, not repo hygiene. | ACTIVE: persist host-local state in a portable Cortex shape. |
| Offline consolidation and support geometry | ACTIVE: restore only explicit `OfflineSupportPublication` entries and support priors. | ACTIVE: allow published support priors to bias score pricing when host-matched and fresh. | ACTIVE: apply support priors only as score-pricing inputs for eligible families. | ACTIVE: collect support-memory episode candidates from public support snapshots. | DEFERRED: compaction-publication law is v2. | DEFERRED: subagent publication law is v2. | N/A: Stop validates the current closure; raw AUX memory never validates closure. | ACTIVE: build support-memory episodes/publications and keep raw AUX support-side only. |

Coverage result: every Cortex failure mode has at least one v1 `ACTIVE` hook
with a named behavior path. `PreCompact` and `SubagentStop` are installed but
stubbed because their lifecycle cases are not universal and their semantics
need separate empirical proof. Their cells are not empty by accident.

## 3. Hook-by-Hook Design

### SessionStart

- Failure modes addressed: truth-preserving commitments, verified-work
  preservation, uncertainty brake, branch continuity, intervention pricing,
  blocker surfacing, multi-host continuity, offline consolidation.
- Input observation: `session_id`, `transcript_path`, `cwd`, model/version
  fields when present, project root, plugin config, and persisted per-session
  state under `CLAUDE_PLUGIN_DATA`.
- State transition: load or initialize `cortex/hosts/claude/runtime.py::ClaudeRuntimeSession`;
  restore branch registry, pending goals, brake tonic history, feedback window,
  preservation summaries, and explicit `OfflineSupportPublication` entries
  parsed by `cortex/aux/publication.py`.
- Model-visible output: observe mode emits nothing. Enforce mode may emit a
  bounded `CORTEX_SESSION_CONTEXT_V1` additional-context block only when
  restored state contains pending goal debt, a guarded/latched brake, or a
  host-matched publication that changes score pricing. Clean starts emit no
  block.
- Kill switch / observe mode: emit nothing when no prior state exists, when
  restored state is clean, or when `hooks.SessionStart=false`. Observe mode
  performs the restore and logs the would-have-emitted reason without
  additional context.
- Connectivity trace: `SessionStart` payload -> `ClaudeRuntimeSession` restore
  -> later `UserPromptSubmit`/`PreToolUse` route and `Stop` closure decisions
  -> additional context or block reason visible to the model.
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
  verification demand. If the prior newest feedback is noisy, the block reuses
  `cortex/hosts/runtime_context.py::runtime_context_from_last_feedback` so the
  bridge stays last-feedback-only.
- Kill switch / observe mode: clean prompt plus clean state emits no block.
  Observe mode updates state and logs route/closure pressure but leaves the
  prompt unshaped.
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
- Model-visible output: enforce mode either allows the tool with
  `hookSpecificOutput.additionalContext` carrying a bounded route/brake
  constraint, or blocks the tool when the route is `BLOCKED`, the tool would
  violate a verified-work allowed write surface, or a latched brake requires
  user/evidence recovery first.
- Kill switch / observe mode: emit nothing for low-risk inspect tools under
  clean state. Observe mode never blocks and records the would-have-blocked
  reason.
- Connectivity trace: PreToolUse payload -> Cortex route/brake/preservation
  assessment -> `additionalContext` or block decision -> the model's next
  post-tool message changes or the tool is prevented.
- Bounded outputs: context is imperative and local to the tool call, no
  acknowledgement requests, no generic advice, capped by `max_context_chars`.

### PostToolUse

- Failure modes addressed: commitments, verified-work preservation, uncertainty
  brake, continuity/closure, intervention pricing, blockers, multi-host
  continuity, offline consolidation.
- Input observation: `tool_name`, `tool_input`, tool result/status/stdout/stderr
  when exposed, `tool_use_id`, `cwd`, `session_id`, and transcript pointer.
- State transition: classify concrete artifacts, external records, evidence
  progress, continuity progress, warning codes, host friction, and probe status
  into `ReferenceRealizationFeedback`; append through
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
  `runtime_context_from_last_feedback` or `Stop` closure pressure -> next
  model-visible constraint/block.
- Bounded outputs: newest feedback only; no accumulation beyond the three-entry
  internal window; raw stdout is not persisted unless user opts into raw logs.

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
- Kill switch / observe mode: allow clean stops when no closure pressure,
  no blocker, no verification debt, and no guarded/latched brake exists. Observe
  mode records the would-have-blocked reason but returns continue.
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
  when a later `SessionStart`, `UserPromptSubmit`, or `PreToolUse` consumes the
  publication-shaped state.
- Kill switch / observe mode: if the session has no meaningful state change,
  write no episode and no publication. Observe mode persists diagnostic state
  but does not make publications eligible for score pricing.
- Connectivity trace: SessionEnd public support snapshot -> bounded episode /
  `OfflineSupportPublication` -> next session score pricing or closure pressure
  -> later additional context/block decision.
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

`project_fingerprint` is derived from the normalized project root and never
from a managed worktree suffix alone. The managed-worktree probes show two
realities that the build must handle: project-local settings can fire inside
`.claude/worktrees/...`, while user-scope plugins in the sandbox saw the
project root as `cwd`. The plugin therefore normalizes the project root from
the best available tuple: `cwd`, `transcript_path`, and configured repo root
allowlist.

Within a session, `ClaudeRuntimeSession` is the spine. Hooks load, update, and
persist that session at event boundaries only. No background timers, polling,
or opportunistic state mutation are allowed. `ReferenceRealizationFeedback`
entries remain bounded to the newest internal window; model-visible runtime
context uses only the newest feedback object.

Across sessions, `SessionEnd` consolidates only bounded public support state:
branch/goal refs, brake history summaries, commitment summaries, verified-work
preservation summaries, support references, and publication tags. Raw
transcript text, raw tool output, personal file contents, and raw AUX SQLite
episodes are not model-visible and are not re-entered directly. `SessionStart`
restores session state and publication-shaped support only; raw AUX memory remains support-side.

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
    "PreCompact": false,
    "SubagentStop": false,
    "Stop": true,
    "SessionEnd": true
  },
  "max_context_chars": 720,
  "logging_level": "redacted",
  "repo_roots": [],
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
additional context and block decisions. Users should install in observe mode,
review logs, then opt into enforce mode per repo root.

## 6. Cortex Packaging Strategy

The plugin bundles the Cortex Python package. This is Option A: users installing
the plugin do not need a `cortex-loop` checkout, and the hook scripts do not
import from the host repo. The plugin distribution includes:

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

Truth distinctions from `docs/CORTEX.md` §3:

- Cortex truth: the lifecycle-first law and hook mapping are defined here.
- Brain-wiring truth: how Claude's model responds to injected constraints is
  empirical and must be measured.
- Conformance truth: existing Claude conformance remains about the operator
  CLI lane unless plugin conformance tests are added.
- Shipping truth: status registry changes only after build + validation +
  live-evidence gates.

Required evidence before any live shipping-lift claim:

- structural hook tests for every active v1 hook;
- empirical proof that each model-visible emit reaches the Code-tab model;
- paired baseline-vs-shaped tasks scored against premature closure, evidence
  recovery, and goal continuity;
- no over-constraint regression beyond the runtime-context rubric threshold;
- explicit proof that AUX remains publication-only and score-pricing-only.

## 8. Privacy, Logging, Observability

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

## 9. Known-Open Empirical Questions

1. Managed-worktree user-scope cwd. `docs/recon/claude_code_user_scope_plugin_managed_worktree_probe.md`
   confirmed user-scope plugin firing in an unrelated sandbox whose `cwd` was
   the project root, not `.claude/worktrees/...`; it therefore does not prove an actual managed-worktree cwd case. If a future Code-tab subject uses an actual managed-worktree cwd, the design changes by requiring stronger root normalization and state-key migration tests.
2. Hook output semantics beyond `PreToolUse:Bash` and `Stop`. Empirical probes
   confirmed `PreToolUse` additional context and Stop block continuation. If
   `SessionStart`, `UserPromptSubmit`, or `PostToolUse` cannot emit
   additionalContext in practice, their v1 content remains state-update-only
   and the model-visible path must route through `PreToolUse` and `Stop`.
3. Non-Bash tool coverage. Current probes exercised Bash. If other tools expose
   different payload shapes, the build must add per-tool observation adapters
   before enforcing on those tools.
4. Plugin update hot reload. If Claude Code Desktop caches plugin hook commands
   per thread, updates require thread restart. The plugin must log version skew
   and avoid assuming hot reload.
5. Live over-constraint risk. If runtime context causes correct outputs to be
   refused under irrelevant prior warnings, enforce mode must narrow emit
   predicates before any shipping-lift claim.

## 10. v2 Deferrals

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

## 11. Closure-Line Discipline

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

## 12. Validation Gates Before Build Phase

No plugin code should be written until this design passes these gates:

- Every `ACTIVE` lattice cell has a connectivity trace from hook payload through
  existing `cortex/**` state to model-visible additional context, block
  decision, route behavior, or later lifecycle consumption.
- Every failure mode in `docs/CORTEX.md` §2 has v1 coverage from at least one
  active hook.
- `PreCompact` and `SubagentStop` are explicitly stubbed with v2 promotion
  paths; no other hook is empty by accident.
- The design keeps live-evidence and structural-evidence claims separate.
- The design does not update shipping truth before build/eval evidence.
- AUX remains publication-only and score-pricing-only; raw AUX episodes do not reach the model and cannot mutate routing, certification, or blockedness.
- The plugin uses existing `cortex/**` modules and does not reimplement Cortex
  law in hook scripts.
- Every model-visible emit has a bounded output discipline and a clean-window
  kill switch.
- The plugin excludes the repo hygiene apparatus from product packaging.
- Known empirical questions are named with design-change consequences.
