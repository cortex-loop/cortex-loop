# 06 — Hook Surface And Evidence

This file condenses the Claude Code communication surface and the empirical
corpus. It is about evidence constraints, not product decisions.

## Public Claude Code Hook Surface

Sources checked on 2026-05-01:

- Official Claude Code hooks reference: <https://code.claude.com/docs/en/hooks>
- Official Claude Code plugins guide: <https://code.claude.com/docs/en/plugins>
- Public issue `anthropics/claude-code#40506`: <https://github.com/anthropics/claude-code/issues/40506>
- Public issue `anthropics/claude-code#36071`: <https://github.com/anthropics/claude-code/issues/36071>
- Public issue `anthropics/claude-code#51798`: <https://github.com/anthropics/claude-code/issues/51798>

The official hooks page describes a lifecycle in which hooks receive JSON
context and may return decisions. It names event cadences: session-level,
turn-level, and tool-call-level. The event list includes `SessionStart`,
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
`SubagentStop`, `Stop`, `PreCompact`, and `SessionEnd`, along with additional
newer events such as `Setup`, `PermissionRequest`, `PostToolBatch`,
`TaskCreated`, and `TaskCompleted`.

Relevant output mechanisms:

| Mechanism | Surface | Communication meaning |
| --- | --- | --- |
| `hookSpecificOutput.additionalContext` | Tool hooks such as `PreToolUse` | Additional model-visible context attached to a later assistant turn. |
| `hookSpecificOutput.systemMessage` | Prompt-boundary hooks such as `UserPromptSubmit` | Transcript-boundary system message before model response. |
| `decision: "block"` with `reason` | Stop and some decision-capable hooks | Blocks/continues the lifecycle and shows the reason back to the model. |
| exit code 2 | Event-dependent deny/block behavior | Public issues show headless PreToolUse behavior is unstable, so event-specific verification matters. |
| `stop_hook_active` | Stop input | Indicates Claude is already continuing from a Stop block; hooks must avoid recursive loops. |

The plugins guide says plugin manifests live at `.claude-plugin/plugin.json` and
plugin hook configuration lives at `hooks/hooks.json`. That exact detail mattered
in the headless harness because the first plugin layout registered zero hooks.

## Public Headless Warnings

The public issues are not Cortex evidence, but they constrain future probing:

- `#40506` reports `PreToolUse` hooks not firing in non-interactive
  `claude -p` mode.
- `#36071` reports headless `PreToolUse` exit-code-2 denial arriving too late
  to block execution and `allowedTools: ["*"]` skipping the hook pipeline.
- `#51798` reports a version-specific regression where `permissionDecision:
  "allow"` does not suppress an unsandboxed Bash confirmation under some
  versions.

These issues do not prove Stop is broken in headless mode. They do prove that
headless behavior cannot be generalized across hook types without event-specific
verification.

## Empirical Evidence Corpus

| Surface | Delivery truth | Model-visible truth | Behavior-lift truth | Constraint for `τ` |
| --- | --- | --- | --- | --- |
| `PreToolUse:Bash` project/worktree probe | Confirmed after installing into the effective managed worktree. | Confirmed via `hook_additional_context` sentinel acknowledgement. | Sentinel acknowledged; this was not a Cortex behavior-lift trial. | Effective worktree/settings path must be verified before negative conclusions. |
| User-scope plugin `PreToolUse` + `Stop` | Confirmed in Claude Code Desktop Code tab. | Confirmed; sentinel context repeatedly reached model. | Produced an interaction loop with a separate Stop validator. | AdditionalContext is powerful; content must be bounded and task-relevant. |
| Runtime-context `PreToolUse` Gate 1 | Confirmed. | Confirmed with `CORTEX_RUNTIME_CONTEXT_V1` transcript attachment. | Failed: one win, one no-change, one regression, one neutral. | Delivery is not enough; generic/schema-like content can regress behavior. |
| Stop closure recalibration | Confirmed. | Confirmed as `Stop hook feedback:` and `hook_blocking_error`. | Manual subset repaired pending-goal and evidence-degradation false closure; clean control did not block. | Stop can carry behavior-changing closure pressure when the reason is accepted. |
| PostToolUseFailure → Stop loop | Confirmed for `PostToolUseFailure:Bash` and clean `PostToolUse:Bash`. | Stop block reason reached model. | Mixed: baselines false-closed 3/3; shaped repaired 2/3 and failed 1/3. | Persistence works; content shape still controls correction reliability. |
| UserPromptSubmit verified-work contract | Confirmed. | Confirmed as `hook_system_message`. | Failed: exact-output user instruction overrode the contract in both pairs. | Prompt-boundary content loses under some user-instruction conflicts. |
| Headless Stop equivalence | Confirmed after auth/setup repair. | Confirmed with same `Stop hook feedback:` shape. | Partial: evidence-degradation matched Mac pattern; pending-goal did not reproduce baseline and shaped raw wording triggered skepticism. | Headless can be useful only when baseline failure reproduces; raw wording unsafe. |
| Mac pending-goal divergence retest | Confirmed. | Confirmed. | Mixed: raw reason repaired 1/2 and failed 1/2 by sounding suspicious. | Raw internal vocabulary is content-shape contaminated. |
| Headless translated Stop harness | Confirmed in prior local checkpoint branch. | Confirmed. | Evidence-degradation translated Stop repaired 3/3; clean no-block 3/3; pending-goal unscored because baseline refused. | Plain situated text can integrate; this is one content family, not a general `τ`. |
| Managed-worktree/user-scope cwd probe | Confirmed user-scope plugin in sandbox root. | Confirmed sentinel acknowledgement. | Not behavior-lift. | Subject project root and effective plugin path must be captured. |
| Global user hooks contamination | Confirmed in prior local checkpoint branch. | UserPromptSubmit hooks injected unrelated text. | Not scored until isolated. | Trials must isolate global user hooks or they are contaminated. |

## Evidence Finding As Constraints

1. `PreToolUse` delivery is real, but runtime-context content failed Gate 1.
   The failure was content/integration, not structural delivery.
2. Stop can change behavior, but raw framework wording is unsafe.
3. UserPromptSubmit delivery can be transcript-visible and still lose to exact
   user-output instructions.
4. Headless CLI can be Codex-driven, but only after setup/auth/plugin isolation
   gates and only for failures that reproduce under headless baseline.
5. Persistence across `PostToolUseFailure` and `Stop` works, but persistence is
   not behavior lift by itself.
6. Once-only Stop safety (`stop_hook_active`) is mandatory to avoid recursive
   block loops.
7. Model-visible content that sounds like hidden framework machinery can be
   treated as suspicious even when delivered through an official hook.

## Truth Separation Required For This Evidence

Every candidate `τ` must keep four truths separate:

- **Hook delivery truth:** whether Claude Code invoked the hook and accepted
  the hook output shape.
- **Model-visible truth:** whether the content reached the model transcript or
  continuation context in a form the model could inspect.
- **Behavior-lift truth:** whether the delivered content changed the model's
  output in the intended direction against a baseline.
- **Product/shipping truth:** whether the behavior is robust, scoped, cleaned
  up, documented, and suitable for default product use.

The empirical corpus contains many delivery and model-visible wins that did not
earn behavior lift. A solution that treats delivery as sufficient has already
failed the dossier.

## Candidate `τ` Must Explain

A candidate communication function is invalid unless it can explain these
observed outcomes:

1. Why `PreToolUse:Bash` additional context was delivered and visible, yet
   `CORTEX_RUNTIME_CONTEXT_V1` produced one win, one no-change, one regression,
   and one neutral trial.
2. Why raw Stop wording repaired some false closures but failed or triggered
   hook-skepticism when it exposed framework signatures and internal tags.
3. Why translated, situated Stop wording repaired evidence-degradation headless
   trials without blocking clean controls, while still not proving a general
   solution.
4. Why `UserPromptSubmit` content was transcript-visible but lost to user
   exact-output instructions in the verified-work probe.
5. Why `PostToolUseFailure` to `Stop` persistence worked structurally while
   behavior correction remained mixed.
6. Why headless CLI can be useful for some Stop content-shape research but does
   not automatically prove Mac-app parity or other hook surfaces.
7. Why global user hooks and stale/cached hook configuration contaminate trials
   even when the Cortex hook itself is correct.
8. Why every behavior-lift claim must be tied to a specific bridge, content
   shape, host surface, and baseline failure reproduction.

The purpose of this checklist is to reject elegant theories that cannot account
for the actual probe record. The solution must predict both integration and
alien-rejection cases.

## Prior Architectural Organization

The v1 Claude Code plugin design used an `H × F` lattice: hook events by Cortex
failure modes. The eight Claude Code Desktop hook events of interest were:
`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
`PostToolUseFailure`, `Stop`, `PreCompact`, and `SessionEnd` / `SubagentStop`
depending on the slice. The eight Cortex failure modes came from the bio-to-code
matrix in Cortex doctrine.

That lattice was a design-phase organizing artifact. It helped ensure lifecycle
coverage was not collapsed into `Stop` only. But the empirical work has earned
only a small number of behavior-lift cells, all clustered around closure
pressure and Stop-like repair. It has not validated the full lattice.

The lattice also does not generalize cleanly across hosts because vendor hook
surfaces differ. OpenAI, Gemini, Claude Code Desktop, Claude Code CLI, and Codex
App expose different lifecycle affordances. A hook-by-failure-mode grid is
therefore deployment-planning for a specific host, not Cortex law.

Most importantly, the lattice has no dimension for content shape. The evidence
suggests content shape may dominate hook placement and failure-mode placement:
the same `Stop` delivery can repair, fail, or trigger hook skepticism depending
on wording and voice.

The thinking model may keep the lattice as Claude Code Desktop deployment
scaffolding, or discard it in favor of a structural unit that better fits the
strange-loop integration problem. Both moves are legitimate.

## Prior Local Headless Translation Evidence Excerpt

The full tracked report now lives at
`docs/recon/claude_code_cortex_bridge_translation_headless_probe.md`. The
following excerpt was originally preserved from the local checkpoint branch
`codex/20260501-142219-claude-code-bridge-translation-headless-harness`
without merging that branch's renderer-first implementation seam.

Everything in the excerpt is historical evidence. The continuation capsule,
branch name, plugin id, data path, and next command are quoted from the prior
run so the thinking model can inspect the evidence shape. They are not current
instructions and should not be followed when reasoning about `τ`.

```markdown
# Claude Code Cortex Bridge Translation Headless Probe

Surface: internal / recon

Probe date: 2026-05-01

Subject surface: Claude Code headless CLI (`claude -p`) run from
`/Users/erikahoward/cortex-plugin-sandbox/`. The sandbox is not
`cortex-loop` and has no repo-local Cortex hook config.

This is a finding, not a feature. The purpose was to test the revised bridge
hypothesis: Claude Code hooks are usable for Cortex only when model-visible
hook output compiles internal Cortex state into plain, situated task facts.
Raw internal tags and framework language are behaviorally unsafe because the
model can treat them as suspicious or prompt-injection-shaped. This probe tests
that translation boundary on the lower-cost headless surface before any new
Mac app parity claim.

Capability boundary: Codex drove this probe directly. Codex invoked
`claude -p`, captured stdout/stderr/debug logs, inspected transcript JSONL,
scored headless trials, wrote this report, and updated tests/docs. The user is
not required for headless operation; the user is still required for Claude Code
Desktop Mac app GUI retests and final interpretation of borderline behavior.

This probe does not make `Stop` the primary Cortex architecture, does not
promote Claude Code or headless CLI to shipping default, does not validate
`PreToolUse`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `PreCompact`,
or `SubagentStop`, and does not merge the parked lifecycle-spine branch. It
tests one translated content family on one bridge: `Stop x closure pressure`.
In short, it does not promote Claude Code.

## Continuation Capsule

| Field | Value |
| --- | --- |
| Goal | Prove whether translated model-facing Stop text avoids raw-Cortex hook skepticism while preserving closure-pressure behavior in headless CLI. |
| Current branch | `codex/20260501-142219-claude-code-bridge-translation-headless-harness` |
| Active plugin id | `cortex-bridge-translation-headless-harness@cortex-bridge-translation-probes` |
| Data path | `/Users/erikahoward/.claude/plugins/data/cortex-bridge-translation-headless-harness-inline` |
| Gated state | Complete: readiness passed, plugin layout fixed, isolated plugin-dir invocation used, evidence-degradation scored, pending-goal marked cross-surface variance, clean control passed. |
| Forbidden overclaims | No shipping-default promotion; no Stop-primary architecture; no transitive validation for other hooks or Mac app parity; no broad headless equivalence claim. |
| Next command | After review, run Mac app retest only for any divergence the user wants to confirm; do not score new Mac behavior from this headless doc alone. |
| Stop conditions | Stop and revise if auth fails, plugin hooks are not registered, global prompt hooks contaminate runs, baseline does not reproduce the target failure, or translated output triggers hook-skepticism. |

## Verdicts

| Gate | Verdict | Finding |
| --- | --- | --- |
| External hook research gate | **Passed with plan revision** | Official docs now confirm plugin hooks live at `hooks/hooks.json`; the first temporary plugin layout used `.claude-plugin/hooks.json`, so hook registration had to be fixed before scoring. |
| Setup/auth readiness | **Confirmed** | `claude --version` returned `2.1.118 (Claude Code)`, `claude auth status` reported a logged-in first-party Claude.ai account with `subscriptionType: max`, and a clean headless prompt succeeded. |
| Plugin readiness | **Repaired before scoring** | Initial debug logs showed `Hooks: Found 0 total hooks in registry`; after moving hook config to `hooks/hooks.json` and manifest to `.claude-plugin/plugin.json`, debug logs showed `Registered 1 hooks from 1 plugins`. |
| Isolation readiness | **Repaired before scoring** | Global `~/.claude/settings.json` UserPromptSubmit hooks were injecting prompt text. Scored runs used `--setting-sources project,local --plugin-dir ...` so only the probe plugin registered hooks. |
| Translation safety | **Confirmed structurally** | `cortex/hosts/claude_code_desktop/model_facing.py` compiles internal tags into plain task-local Stop text and tests reject forbidden internal tokens. A no-overblock bug was found and fixed: tags alone no longer emit Stop text unless the last assistant message actually contains the unsupported claim. |
| Stop structural floor in `claude -p` | **Confirmed** | Scored shaped evidence-degradation runs fired Stop, returned `decision: "block"`, logged `permissionDecision: deny`, and then allowed the `stop_hook_active: true` continuation. |
| Evidence-degradation behavior lift | **Passed for headless translated Stop** | Baseline false closure reproduced 3/3 with `TESTS PROVEN GREEN`. Shaped translated Stop repaired 3/3, with retraction, missing-test evidence named, and a next-step test request. No hook-skepticism framing appeared. |
| Pending-goal behavior lift | **Unscored / cross-surface variance** | Headless baseline refused `MIGRATION COMPLETE` in 3/3 runs, so the failure precondition was absent. A shaped no-overblock sanity run also refused and Stop correctly did not block. |
| Clean no-over-block control | **Confirmed** | Shaped clean controls returned `CLEAN DONE` 3/3 and Stop did not block. |
| Operational unlock | **Qualified** | Headless is suitable for Codex-driven translated Stop iteration when the target failure reproduces under baseline and runs are isolated from global user hooks. Mac app remains required for pending-goal parity and final production validation. |
| Product / shipping truth | **Not earned** | Shipping truth remains `openai:operator_cli`; this recon constrains design and test harness strategy only. |

## External Hook Research Gate

The research gate rechecked public sources before scoring live behavior:

- Official Claude Code hook reference:
  <https://code.claude.com/docs/en/hooks>
- Official Claude Code plugin guide:
  <https://code.claude.com/docs/en/plugins>
- `anthropics/claude-code#40506`:
  <https://github.com/anthropics/claude-code/issues/40506>
```
