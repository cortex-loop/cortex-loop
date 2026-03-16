# Adapter Implementation Dossier

> Frozen v1 reference dossier mirrored from [`cortex-loop-v1-archive`](https://github.com/cortex-loop/cortex-loop-v1-archive/tree/v0.1.0a2) at [`v0.1.0a2`](https://github.com/cortex-loop/cortex-loop-v1-archive/releases/tag/v0.1.0a2).
> This fresh canonical repo intentionally contains only the `cortex-archival-dossiers/` v1 reference pack; the full v1 tree, tests, fixtures, and releases live in the archive repo.


This dossier is the implementation map for the current shipped adapter layer.
It does not replace [ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), or [CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md), which remain the active status and realization authority surfaces.

It is also the final v1 adapter implementation packet for the frozen archive point.
It intentionally preserves implementation evidence and code only; it does not prescribe v2 architecture or later Cortex doctrine.

This repo copy is the active, current replacement for the older critique-support packet. It keeps the useful structure of that packet, adds a full current source appendix, and strips stale branch-specific claims. Live code and active authority docs win if any wording here drifts.

Current product-proof note:
- Phase 9 is now landed at a truthful-withheld endpoint.
- Current launch/runtime/product-proof truth lives first in [../MASTER_PLAN.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MASTER_PLAN.md), [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md), and the current Phase 9 proof artifacts.
- This dossier keeps the implementation map current without overwriting the dated March 15 critique-support evidence window.

## Quick Navigation

- Need the shortest current read: see Sections 3, 5, 9, and 10.
- Need exact Claude reality: see Section 6.
- Need exact OpenAI reality: see Section 8.
- Need the implementation inventory first: see Section 4.
- Need exact pasted source snapshot: see Section 11.
- Need to know what is still the real product problem rather than an adapter myth: see Section 9.

## 0. Evidence Window

Current local installs observed during this dossier audit:

- Claude: local `claude-code 2.1.76`
- Gemini: local `gemini-cli 0.33.1`
- OpenAI native and assisted: local `codex-cli 0.111.0`

Current repo-backed validation window:

- Claude: shared-harness and supplemental live proof are current on local `claude-code 2.1.76` under [../tests/fixtures/adapter_validation/claude/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/claude)
- Gemini: the shipped watchlist and shared-harness evidence are still anchored to local `gemini-cli 0.32.0` under [../tests/fixtures/adapter_validation/gemini/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/gemini); the 2026-03-15 cross-runtime audit preserved mixed `0.33.1` spotchecks, and the March 16 current Phase 9 pair now adds one route-valid `localized_edit/strict` row that still ended `failed_invariants` ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json), [../tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json))
- OpenAI native and assisted: the committed bridge evidence remains anchored to local `codex-cli 0.111.0` under [../tests/fixtures/adapter_validation/openai/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/openai); the March 15 critique audit preserved mixed latest-local spotchecks on the same nominal version, and the March 16 current Phase 9 packet now adds one row-capturable assisted shared-harness pair while native OpenAI remains blocked/non-row-capturable for current product-proof weight ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json), [../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json), [../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json))

## 1. Scope

This dossier covers the current implementation boundary for:

- Anthropic Claude Code native
- Google Gemini CLI native
- OpenAI Codex App Server native
- OpenAI Codex App Server assisted

The adapter layer in scope includes:

- event normalization in [../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)
- Claude hook bridge in [../cortex/hooks/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks)
- Gemini hook bridge in [../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py)
- OpenAI App Server bridge in [../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py)
- OpenAI App Server protocol client in [../cortex_ops_cli/_openai_bridge_protocol.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_openai_bridge_protocol.py)
- runtime profile installers and templates in [../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py) and [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)

It does not treat tests, raw fixture transcripts, or kernel internals as part of the adapter implementation boundary, even when those surfaces are necessary evidence.

## 2. Adapter Boundary In Product Terms

Shared rule:

- The kernel owns completion meaning, stop stages, challenge coverage, requirement audit, truth claims, and final acceptance.
- Runtime adapters normalize host payloads into canonical kernel inputs.
- Runtime hook or bridge layers render kernel-owned meaning natively on each host surface.
- No shipped v1 adapter is presented as owning planner doctrine, extra approval policy, or a second completion contract.

The practical ownership split is:

- kernel-owned:
  - stop policy
  - challenge / invariant / requirement / truth evaluation
  - objective-gap state
  - completion acceptance
- adapter-owned:
  - normalize vendor events into canonical kernel events
  - normalize vendor payloads into canonical payload fields
- bridge-owned:
  - map kernel outputs into host-native allow / deny / continue / stop forms
  - shape bounded startup or corrective support only where the host surface truly requires it
- host-owned:
  - what lifecycle events exist
  - what approval surfaces exist
  - whether startup hooks are available
  - whether the runtime can cleanly halt after a blocked stop

## 3. Runtime Roster And Current Repo Status

| Company / runtime | Current Cortex surface | Repo status | What Cortex really implements now | Primary live limit |
| --- | --- | --- | --- | --- |
| Anthropic Claude Code native | native hook bridge | `Shipped` | startup preview, pre-tool deny, post-tool handling, failure-side post-tool context, truthful stop, structured stop extraction from final message, telemetry-only `InstructionsLoaded` | boundedness is still mixed under proof pressure because the current product issue is below the adapter |
| Google Gemini CLI native | native hook bridge | `Shipped with watchlist` | startup preview, before-agent anchor, pre/post tool handling, structured stop parse, bounded repair focus, truthful halt/stuck | current route-valid `0.33.1` Phase 9 lane still ended `failed_invariants` against the older `0.32.0` clean validation row |
| OpenAI Codex App Server native | App Server bridge | `Experimental` | approval mapping, command-complete mapping, turn-complete stop, post-hoc stop summary, terminality proof | latest-local `0.111.0` evidence is mixed: the current positive lane can fix and pass without ever reaching `Stop` |
| OpenAI Codex App Server assisted | App Server bridge plus bounded assist layer | `Experimental` | startup preview, evidence expectation, explicit requirement ids when known, one bounded correction pass, four terminal states | current shared-harness pair is row-capturable, but the lane still ended `failed_challenges` / `bounded_incomplete` and remains supplemental only |

Current status authority:

- [ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md)
- [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md)
- [CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md)

## 4. Core Adapter Files And Their Jobs

### 4.1 Shared normalization boundary

- [../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)

Defines:

- `NormalizedEvent`
- `GenericAdapter`
- `ClaudeAdapter`
- `GeminiAdapter`
- `OpenAIAdapter`

Current job:

- map vendor-shaped events into canonical kernel events such as `session_start`, `pre_tool_use`, `post_tool_use`, and `stop`
- normalize vendor payloads into canonical fields like `stop_fields`, `last_assistant_message`, `target_files`, and `planned_files`

### 4.2 Claude-native hook bridge

- [../cortex/hooks/_shared.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/_shared.py)
- [../cortex/hooks/session_start.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/session_start.py)
- [../cortex/hooks/pre_tool_use.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/pre_tool_use.py)
- [../cortex/hooks/post_tool_use.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/post_tool_use.py)
- [../cortex/hooks/post_tool_use_failure.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/post_tool_use_failure.py)
- [../cortex/hooks/stop.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/stop.py)
- [../cortex/hooks/instructions_loaded.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/instructions_loaded.py)

Current job:

- map kernel results into Claude-native hook shapes such as `permissionDecision`, `decision`, `continue`, `hookSpecificOutput.additionalContext`, and `systemMessage`

### 4.3 Gemini-native hook bridge

- [../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py)

Current job:

- map Gemini lifecycle hooks into kernel calls
- render startup preview, before-agent anchor, stop-time repair focus, and truthful halt or stuck behavior on the native Gemini surface

### 4.4 OpenAI App Server bridge

- [../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py)

Current job:

- reconstruct a Cortex event lifecycle from App Server events
- support both native and assisted OpenAI realization paths

### 4.5 OpenAI App Server protocol client

- [../cortex_ops_cli/_openai_bridge_protocol.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_openai_bridge_protocol.py)

Current job:

- JSON-RPC transport
- session and thread creation
- approval-policy fallback
- event streaming
- approval request handling
- turn completion detection

### 4.6 Runtime profile installers and packaged runtime docs

- [../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py)
- [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)
- [../claude/CLAUDE.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/claude/CLAUDE.md)
- [../gemini/GEMINI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/gemini/GEMINI.md)
- [../openai/OPENAI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/openai/OPENAI.md)

Current job:

- define what `cortex runtime install --profile ...` actually writes
- define what each shipped runtime tells the model before or around the stop boundary

## 5. Cross-Runtime Capability Matrix

| Capability | Claude native | Gemini native | OpenAI native | OpenAI assisted |
| --- | --- | --- | --- | --- |
| Startup hook used by shipped profile | yes | yes | no | synthetic via bridge |
| Startup completion preview | yes, short only | yes | no | yes |
| Startup evidence expectation | no | no | no | yes |
| Explicit requirement ids at startup | no | no | no | yes when configured |
| Native pre-tool gate | yes | yes | only if approval request is emitted | same host limit |
| Native post-tool feed | yes | yes | reconstructed from command completion | same |
| Native failure-side post-tool context | yes | yes through normal path | reconstructed | same |
| Native stop callback | yes | yes | reconstructed from `turn/completed` | same |
| Short repair focus after failed stop | yes, blocked-stop brief only | yes | no | yes |
| Bounded correction pass | no | no | no | yes, one pass only |
| Truthful stuck clean exit | yes | yes | partial and post-hoc | yes |
| Current repo status | `Shipped` | `Shipped with watchlist` | `Experimental` | `Experimental` |

The shortest honest product read is:

- Claude is the strongest truthful stop boundary.
- Gemini is the strongest native humane-support runtime.
- OpenAI native is still largely post-hoc.
- OpenAI assisted is the strongest humane-support realization overall, but only through a bridge-shaped assisted path.

## 6. Anthropic / Claude Code

### 6.1 What Cortex currently wires

Installed Claude profile files:

- [../claude/settings.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/claude/settings.json)
- [../claude/CLAUDE.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/claude/CLAUDE.md)

Required shipped Claude hooks:

- `SessionStart`
- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `Stop`

Optional shipped Claude hook:

- `InstructionsLoaded` telemetry only

Implementation-bearing code:

- [../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)
- [../cortex/hooks/_shared.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/_shared.py)
- [../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py)
- [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)

### 6.2 What the shipped Claude adapter actually implements now

Current Claude normalization and rendering behavior:

- `SessionStart` is normalized with `runtime_mode = "native_preview"` and `stop_trailer_marker = "STOP_FIELDS_JSON"` so the startup preview flows through the shipped hook surface.
- `PostToolUseFailure` is normalized into the canonical `post_tool_use` path with failure status preserved, rather than creating Claude-only retry logic.
- Claude file-edit payloads normalize `tool_input.file_path` into canonical `target_files` and `planned_files`.
- `last_assistant_message` and one-line `STOP_FIELDS_JSON` are normalized into canonical `stop_fields` before strict stop evaluation.
- Native Claude output branches exist for `SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, and `Stop`.
- `SessionStart` now sends only the short kernel-owned `completion_preview`, not the older heavier startup context that pushed Claude toward generic completion ritual.
- Blocked repairable Claude `Stop` can carry a short kernel-derived `Repair focus:` brief through `systemMessage`, but the decision remains a kernel-owned block.
- `InstructionsLoaded` is fail-open telemetry only: when the host emits it with a session id, Cortex records the raw payload in session events and returns `{}`.

### 6.3 Current repo reality

What the current repo truth supports:

- Claude is the strongest current truthful stop boundary and remains `Shipped`.
- The shipped Claude profile now fully includes the earned Phase A and Phase C seams: `SessionStart`, `PostToolUseFailure`, Claude file-target normalization, blocked-stop repair brief rendering, and telemetry-only `InstructionsLoaded`.
- The current official Claude hooks surface is broader than the shipped profile, but the non-shipped seams are intentionally classified in [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) as `probe-only`, `docs/telemetry only`, or `reject for now`. That includes `PermissionRequest`, `PreCompact`, `PostCompact`, prompt hooks, agent hooks, elicitation hooks, and multi-agent hooks.
- The current surviving Claude boundedness issue is no longer primarily a missing adapter seam. The historical failure was adapter pressure, but the current remaining problem is that proof-pressure tasks can still let Claude+Cortex widen scope and close `completed` because the kernel or validation contract does not yet encode minimal task boundedness strongly enough. See [CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md).
- There is no current repo-evidenced case that a new Claude-specific bounded-correction wrapper is the right next adapter move.

### 6.4 Non-goals that still hold

- Do not ship `PermissionRequest` as a second approval layer by default.
- Do not add Claude prompt-hook or agent-hook policy.
- Do not add a Claude-specific retry loop above kernel `Stop`.
- Do not claim Claude boundedness is solved; current repo truth is mixed under proof pressure, not clean.

## 7. Google / Gemini CLI

### 7.1 What Cortex currently wires

Installed Gemini profile files:

- [../gemini/settings.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/gemini/settings.json)
- [../gemini/GEMINI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/gemini/GEMINI.md)

Required shipped Gemini hooks:

- `SessionStart`
- `BeforeTool`
- `AfterTool`
- `AfterAgent`

Optional shipped Gemini hook:

- `BeforeAgent`

Implementation-bearing code:

- [../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)
- [../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py)
- [../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py)
- [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)

### 7.2 What the shipped Gemini adapter actually implements now

Current Gemini behavior:

- `SessionStart` renders one short kernel-owned completion preview before heavier session context.
- `BeforeAgent` supplies the recurring Part B anchor without repeating the startup preview.
- `AfterAgent` enforces strict stop parsing from final `STOP_FIELDS_JSON`.
- Repairable failed stops can surface a short bounded repair focus from kernel `repair_targets`.
- Gemini bridge maintains fallback session identity and retry-state handling when the host is inconsistent on callback identity.

### 7.3 Current repo reality

What the current repo truth supports:

- Gemini remains `Shipped with watchlist`.
- On the older committed validation row, Gemini is still the strongest native humane-support runtime in the repo.
- The main committed Gemini issue is still operational rather than semantic: malformed-stop retry flows can still leave the Gemini process resident even after Cortex closes the session truthfully.
- Fresh latest-local Gemini truth now has two conflicting but preserved layers: the March 15 critique audit still shows the older positive lane no longer reproducing the clean pass story, and the March 16 current Phase 9 pair now proves a route-valid `localized_edit/strict` row that still ended `failed_invariants`.
- The main current Gemini product problem is therefore no longer just the retry-residency watchlist; it is also that the shared positive lane is overloaded enough to destabilize the newer local build.

## 8. OpenAI / Codex App Server

### 8.1 What Cortex currently wires

Installed OpenAI profile files:

- [../openai/OPENAI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/openai/OPENAI.md)
- `.codex/cortex_openai_bridge.json` as generated from [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)

Shipped OpenAI profiles:

- `openai` native
- `openai-assisted`

Implementation-bearing code:

- [../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)
- [../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py)
- [../cortex_ops_cli/_openai_bridge_protocol.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_openai_bridge_protocol.py)
- [../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py)
- [../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)

### 8.2 What the shipped OpenAI adapter actually implements now

Current OpenAI normalization and bridge behavior:

- OpenAI App Server approval requests normalize into `pre_tool_use`, command completion into `post_tool_use`, and `turn/completed` into `stop`.
- `final_text` is copied into canonical `last_assistant_message` when present.
- Native mode is honest and post-hoc: one App Server turn, then kernel stop evaluation.
- Assisted mode is explicit and bounded: kernel `session_start` runs up front, one short kernel-owned completion preview plus one short kernel-owned evidence expectation are surfaced before the longer session context, and one corrective turn may run only when the first stop returns kernel-owned `stop_stage = repair` or `reorient`.
- Assisted mode can carry explicit requirement ids through `.codex/cortex_openai_bridge.json` or repeated CLI `--required-requirement-id` arguments; it does not infer ids from prompt prose.
- OpenAI bridge stop summaries preserve kernel-owned fields such as `stop_stage`, `objective_gap_state`, `repair_targets`, `stuck_declaration`, and `enforcement_pass`.

### 8.3 Current repo reality

What the current repo truth supports:

- OpenAI native and assisted both remain `Experimental`.
- Older committed native OpenAI evidence no longer had a terminality blocker; the repo still has separate live terminality proof from that window.
- Fresh OpenAI truth is now split across a dated contradiction and a current supplemental lane: the March 15 critique audit still records mixed native/assisted latest-local behavior, while the March 16 current Phase 9 packet now adds one row-capturable assisted pair with startup preview, evidence expectation, and one bounded corrective pass. Assisted mode is still product-real and bounded by design, but the lane remains supplemental-only rather than a stronger current proof lane.
- The strongest current OpenAI improvement opportunity is therefore no longer just semantic strict-close help. The broader cross-runtime audit says the first shared issue is the overloaded positive lane itself.

### 8.4 Non-goals that still hold

- Do not blur native and assisted into one status story.
- Do not overclaim assisted proof as launch-proof readiness.
- Do not redesign the kernel around OpenAI approval UX details.
- Do not treat a terminality pass as the same thing as a semantic strict-close pass.

## 9. What Is Already Integrated Into Product Truth, And What Is Not

Already strongly integrated:

- adapter normalization into canonical kernel events
- bridge rendering of kernel `stop_stage`, stuck, and halt semantics
- live runtime status and watchlist tracking in [ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md) and [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md)
- current realized startup and failure-side Claude seams
- current realized assisted OpenAI startup and bounded correction path

Only partly integrated:

- product-boundedness preservation under proof pressure
- cross-runtime comparison of actual artifact quality versus raw model baselines
- clean product proof that Cortex beats the raw model, rather than only producing stronger completion evidence

Not the current adapter problem:

- missing Claude `SessionStart`
- missing Claude `PostToolUseFailure`
- missing OpenAI assisted startup or corrective path

Current product-level truth:

- the adapter evidence proves that Claude, Gemini, and OpenAI surfaces can preserve kernel-owned completion-boundary semantics to the degree recorded in [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) and [CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md)
- the adapter evidence does not yet prove that Cortex as a product beats the raw model on artifact quality
- the current packet still withholds the product claim instead of silently implying one
- the strongest committed negative example remains the Claude boundedness anchor case: raw Claude produced the better minimal patch, while Claude+Cortex produced the better proof and worse boundedness under proof pressure
- the dated March 15 cross-runtime audit first broadened that conclusion, and the March 16 Phase 9 packet now lands it at a truthful-withheld endpoint: the first shared product issue is a validation-contract problem, because the current shared positive lane is already a proof-hardening lane and destabilizes multiple runtimes differently
- the main remaining product issue is therefore below the current Claude adapter: proof pressure and kernel or validation-contract acceptance can still permit truthful but over-broad or otherwise distorted completion on some tasks

## 10. What Another Researcher Should Critique First

If another strong researcher critiques the current adapter layer, the right questions are:

1. Is any current bridge still carrying kernel-foreign meaning?
2. Are any non-shipped Claude surfaces now actually earned, or are they still hook tourism?
3. Is OpenAI native still blocked primarily by semantics rather than missing bridge plumbing?
4. Does the current product still overweight proof completion relative to minimal task boundedness?
5. Is the next honest gain in the adapter, or below it in the kernel or validation contract?

Current honest answers on the repo evidence base:

- the shipped adapter boundary is currently narrow and mostly honest
- Claude’s missing product win is not another obvious shipped seam
- OpenAI native is no longer honestly summarized by “semantic strict close only”; latest-local evidence is mixed and currently worse than the cleaner committed row, while current assisted evidence is now real but still supplemental-only
- the current surviving boundedness failure is below the current Claude adapter, and the first cross-runtime fix is validation-contract design rather than a new adapter seam

## 10.5 Test And Live Evidence Summary

The adapter layer is backed by two different evidence families:

- code-level normalization and bridge tests in [../tests/test_adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_adapters.py), [../tests/test_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_hooks.py), and [../tests/test_cli.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_cli.py)
- runtime-proof and readiness artifacts in [ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), [../tests/test_adapter_validation_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_adapter_validation_contract.py), and the committed fixture trees under [../tests/fixtures/adapter_validation/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation)

The current real-world adapter behavior summary is:

- Claude: live-proven shipped startup, failure-side post-tool handling, truthful stop, telemetry-only `InstructionsLoaded`, and a still-mixed boundedness story under proof pressure
- Gemini: older committed shared-harness row is still strong, but the current `0.33.1` story remains mixed even after the route-valid March 16 pair because strict close still ended `failed_invariants`
- OpenAI native: older committed row proved terminality and then semantic strict-close failure, but fresh latest-local `0.111.0` spotchecks are now mixed and can fail to reach `Stop` at all on the same positive lane
- OpenAI assisted: stronger intended humane-support realization than native OpenAI, and now backed by one current row-capturable shared-harness pair, but that lane still ended bounded incomplete and remains supplemental rather than native-substitutive proof

## Current Sweep Verdict

After checking the current code, runtime docs, validation ledger, realization ledger, boundedness post-mortem, and the older external packet this dossier replaces:

- the shipped Claude adapter code required by the current roadmap is present
- the shipped Gemini adapter code required by the current roadmap is present
- the shipped OpenAI native and assisted bridge code required by the current roadmap is present
- the missing artifact was the updated implementation dossier itself, not an unlanded Claude or OpenAI code seam
- this evidence packet does not establish an additional adapter seam requiring reopening beyond the frozen v1 code and artifact set

## 11. Full Source Appendix

This appendix is generated from an explicit final-v1 manifest.

- Manifest: [adapter_appendix_manifest.txt](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/dossiers/manifests/adapter_appendix_manifest.txt)
- Generation base commit: `685e583539afafbe5c365dbfddf59fb5d1713d82`
- Frozen release tag target: `v0.1.0a2`

### Appendix File Map

- [../../cortex/adapters.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/adapters.py)
- [../../cortex/hooks/_shared.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/_shared.py)
- [../../cortex/hooks/session_start.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/session_start.py)
- [../../cortex/hooks/pre_tool_use.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/pre_tool_use.py)
- [../../cortex/hooks/post_tool_use.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/post_tool_use.py)
- [../../cortex/hooks/post_tool_use_failure.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/post_tool_use_failure.py)
- [../../cortex/hooks/stop.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/stop.py)
- [../../cortex/hooks/instructions_loaded.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/instructions_loaded.py)
- [../../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py)
- [../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py)
- [../../cortex_ops_cli/_openai_bridge_protocol.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_openai_bridge_protocol.py)
- [../../cortex_ops_cli/_runtime_profiles.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profiles.py)
- [../../cortex_ops_cli/_runtime_profile_templates.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/_runtime_profile_templates.py)
- [../../claude/CLAUDE.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/claude/CLAUDE.md)
- [../../gemini/GEMINI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/gemini/GEMINI.md)
- [../../openai/OPENAI.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/openai/OPENAI.md)

### Full Source Snapshot

### `cortex/adapters.py`

```python
from __future__ import annotations

import importlib
import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from .stop_payload import parse_stop_fields_json

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class NormalizedEvent:
    name: str
    payload: dict[str, Any]


class EventAdapter(Protocol):
    def normalize(self, event_name: str, payload: Mapping[str, Any] | None = None) -> NormalizedEvent: ...


CANONICAL_EVENT_ALIASES = {
    "session_start": "session_start",
    "sessionstart": "session_start",
    "session_marker": "session_marker",
    "sessionmarker": "session_marker",
    "pre_tool_use": "pre_tool_use",
    "pretooluse": "pre_tool_use",
    "post_tool_use": "post_tool_use",
    "posttooluse": "post_tool_use",
    "post_tool_use_failure": "post_tool_use",
    "posttoolusefailure": "post_tool_use",
    "stop": "stop",
}


class GenericAdapter:
    EVENT_ALIASES = CANONICAL_EVENT_ALIASES

    def normalize(self, event_name: str, payload: Mapping[str, Any] | None = None) -> NormalizedEvent:
        name = _normalize_event_name(event_name, self.EVENT_ALIASES)
        data = dict(payload) if isinstance(payload, Mapping) else {}
        return NormalizedEvent(name=name, payload=data)


class ClaudeAdapter:
    EVENT_ALIASES = CANONICAL_EVENT_ALIASES

    def normalize(self, event_name: str, payload: Mapping[str, Any] | None = None) -> NormalizedEvent:
        name = _normalize_event_name(event_name, self.EVENT_ALIASES)
        data = dict(payload) if isinstance(payload, Mapping) else {}
        data = _normalize_claude_payload(data, normalized_event_name=name)
        message = data.get("last_assistant_message")
        if isinstance(message, str):
            rewritten = _rewrite_legacy_trailer_markers(message)
            if name == "stop":
                stop_fields, passthrough = _normalize_claude_stop_fields(rewritten)
                if isinstance(stop_fields, dict):
                    data["stop_fields"] = stop_fields
                data["last_assistant_message"] = passthrough
            else:
                data["last_assistant_message"] = rewritten
        return NormalizedEvent(name=name, payload=data)


GEMINI_EVENT_ALIASES = {
    **CANONICAL_EVENT_ALIASES,
    "SessionStart": "session_start",
    "BeforeTool": "pre_tool_use",
    "AfterTool": "post_tool_use",
    "AfterAgent": "stop",
    "SessionEnd": "session_end",
    "BeforeAgent": "before_agent",
    "BeforeModel": "before_model",
    "AfterModel": "after_model",
    "BeforeToolSelection": "before_tool_selection",
    "Notification": "notification",
    "PreCompress": "pre_compress",
    "sessionstart": "session_start",
    "beforetool": "pre_tool_use",
    "aftertool": "post_tool_use",
    "afteragent": "stop",
}


class GeminiAdapter:
    EVENT_ALIASES = GEMINI_EVENT_ALIASES

    def normalize(self, event_name: str, payload: Mapping[str, Any] | None = None) -> NormalizedEvent:
        name = _normalize_event_name(event_name, self.EVENT_ALIASES)
        data = dict(payload) if isinstance(payload, Mapping) else {}
        _normalize_session_id(data)
        if name in {"pre_tool_use", "post_tool_use"}:
            _normalize_tool_name(data, candidate_keys=("tool_name",))
            _normalize_gemini_file_targets(data)
        if name == "post_tool_use":
            _normalize_gemini_status(data)
        if name == "stop":
            prompt_response = data.get("prompt_response")
            if not isinstance(prompt_response, str):
                if "prompt_response" not in data:
                    logger.warning("Gemini AfterAgent payload missing prompt_response; using empty string fallback.")
                else:
                    logger.warning(
                        "Gemini AfterAgent prompt_response is not a string (%s); using empty string fallback.",
                        type(prompt_response).__name__,
                    )
                prompt_response = ""
            stop_fields, passthrough, parse_error = _normalize_gemini_stop_fields(prompt_response)
            if isinstance(stop_fields, dict):
                data["stop_fields"] = stop_fields
            else:
                data.pop("stop_fields", None)
            if parse_error:
                data["stop_fields_parse_error"] = parse_error
            data["last_assistant_message"] = passthrough
        return NormalizedEvent(name=name, payload=data)


OPENAI_EVENT_ALIASES = {
    **CANONICAL_EVENT_ALIASES,
    "item/commandexecution/requestapproval": "pre_tool_use",
    "item/commandExecution/requestApproval": "pre_tool_use",
    "command_execution_request_approval": "pre_tool_use",
    "item/commandexecution/completed": "post_tool_use",
    "item/commandExecution/completed": "post_tool_use",
    "command_execution_completed": "post_tool_use",
    "turn/completed": "stop",
    "turn_completed": "stop",
}


class OpenAIAdapter:
    EVENT_ALIASES = OPENAI_EVENT_ALIASES

    def normalize(self, event_name: str, payload: Mapping[str, Any] | None = None) -> NormalizedEvent:
        name = _normalize_event_name(event_name, self.EVENT_ALIASES)
        data = dict(payload) if isinstance(payload, Mapping) else {}
        _normalize_session_id(data)
        if name in {"pre_tool_use", "post_tool_use"}:
            _normalize_tool_name(data, candidate_keys=("tool_name", "command", "tool", "action"))
        if name == "stop":
            final_text = data.get("final_text")
            if isinstance(final_text, str) and "last_assistant_message" not in data:
                data["last_assistant_message"] = final_text
            if "stop_fields" in data and isinstance(data.get("stop_fields"), Mapping):
                data["stop_fields"] = dict(data["stop_fields"])
        return NormalizedEvent(name=name, payload=data)


def load_adapter(adapter_path: str) -> EventAdapter:
    module_name, class_name = _split_adapter_path(adapter_path)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Failed to import adapter module '{module_name}': {exc}") from exc
    adapter_cls = getattr(module, class_name, None)
    if adapter_cls is None:
        raise ValueError(f"Adapter class '{class_name}' not found in module '{module_name}'.")
    try:
        adapter = adapter_cls()
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Failed to instantiate adapter '{module_name}:{class_name}': {exc}") from exc
    if not callable(getattr(adapter, "normalize", None)):
        raise TypeError(
            f"Adapter '{module_name}:{class_name}' must define callable normalize(event_name, payload)."
        )
    return adapter


def _split_adapter_path(adapter_path: str) -> tuple[str, str]:
    token = str(adapter_path or "").strip()
    if not token:
        raise ValueError(
            "runtime.adapter is required. Set [runtime].adapter = \"module.path:ClassName\" in cortex.toml."
        )
    if ":" not in token:
        raise ValueError(
            f"Invalid runtime.adapter '{token}'. Expected format 'module.path:ClassName'."
        )
    module_name, class_name = token.split(":", 1)
    module_name = module_name.strip()
    class_name = class_name.strip()
    module_name = _ADAPTER_PATH_ALIASES.get(module_name, module_name)
    if not module_name or not class_name:
        raise ValueError(
            f"Invalid runtime.adapter '{token}'. Expected format 'module.path:ClassName'."
        )
    return module_name, class_name


def _normalize_event_name(event_name: str, aliases: dict[str, str]) -> str:
    raw = str(event_name or "").strip()
    if raw in aliases:
        return aliases[raw]
    token = raw.lower().replace("-", "_")
    return aliases.get(token) or aliases.get(token.replace("_", "")) or token


def _normalize_claude_payload(payload: dict[str, Any], *, normalized_event_name: str) -> dict[str, Any]:
    _normalize_tool_name(payload, candidate_keys=("tool_name", "tool", "toolName", "action"))
    _normalize_session_id(payload)
    _normalize_claude_file_targets(payload)
    if normalized_event_name == "session_start":
        payload.setdefault("runtime_mode", "native_preview")
        payload.setdefault("stop_trailer_marker", "STOP_FIELDS_JSON")
    if normalized_event_name == "post_tool_use":
        _normalize_claude_post_tool_status(payload)
    if "stop_fields" not in payload and "cortex_stop" in payload:
        payload["stop_fields"] = payload.get("cortex_stop")
    return payload


def _normalize_claude_post_tool_status(payload: dict[str, Any]) -> None:
    raw_hook = str(payload.get("hook_event_name") or "").strip()
    if raw_hook == "PostToolUseFailure":
        payload.setdefault("status", "error")
    tool_response = payload.get("tool_response")
    if isinstance(tool_response, Mapping):
        response_error = tool_response.get("error")
        if payload.get("status") is None and response_error:
            payload["status"] = "error"
        if payload.get("error") is None and isinstance(response_error, str) and response_error.strip():
            payload["error"] = response_error.strip()


def _normalize_claude_file_targets(payload: dict[str, Any]) -> None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return
    file_path = str(tool_input.get("file_path") or tool_input.get("path") or "").strip()
    if not file_path:
        return
    payload.setdefault("target_files", [file_path])
    tool_name = str(payload.get("tool_name") or "").strip().lower()
    if tool_name in {"edit", "multiedit", "write", "notebookedit"}:
        payload.setdefault("planned_files", [file_path])


def _normalize_claude_stop_fields(message: str) -> tuple[dict[str, Any] | None, str]:
    parsed, _, _ = parse_stop_fields_json(message)
    passthrough = _strip_gemini_stop_markers(message)
    if isinstance(parsed, dict):
        stop_fields = {str(k): v for k, v in parsed.items()}
        if passthrough and not stop_fields.get("summary"):
            stop_fields["summary"] = passthrough
        return stop_fields, passthrough
    return None, passthrough or message.strip()


_ADAPTER_PATH_ALIASES = {
    "cortex.adapters.claude": "cortex.adapters",
    "cortex.adapters.generic": "cortex.adapters",
    "cortex.adapters.gemini": "cortex.adapters",
    "cortex.adapters.openai": "cortex.adapters",
}


def _normalize_session_id(payload: dict[str, Any]) -> None:
    raw_session_id = payload.get("session_id")
    if isinstance(raw_session_id, str):
        session_id = raw_session_id.strip()
        if session_id:
            payload["session_id"] = session_id
            return
    payload.pop("session_id", None)


def _normalize_tool_name(payload: dict[str, Any], *, candidate_keys: tuple[str, ...]) -> None:
    primary = payload.get("tool_name")
    if isinstance(primary, str) and primary.strip():
        payload["tool_name"] = primary.strip()
        return
    payload.pop("tool_name", None)
    for key in candidate_keys:
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            payload["tool_name"] = val.strip()
            return


def _normalize_gemini_status(payload: dict[str, Any]) -> None:
    status = payload.get("status")
    if isinstance(status, str) and status.strip():
        payload["status"] = status.strip().lower()
        return
    tool_response = payload.get("tool_response")
    if isinstance(tool_response, Mapping) and tool_response.get("error"):
        payload["status"] = "error"
        return
    payload["status"] = "ok"


def _normalize_gemini_file_targets(payload: dict[str, Any]) -> None:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return
    file_path = str(tool_input.get("file_path") or tool_input.get("path") or "").strip()
    if not file_path:
        return
    payload.setdefault("target_files", [file_path])
    tool_name = str(payload.get("tool_name") or "").strip().lower()
    if tool_name in {"replace", "write_file", "edit", "write"}:
        payload.setdefault("planned_files", [file_path])


def _normalize_gemini_stop_fields(prompt_response: str) -> tuple[dict[str, Any] | None, str, str]:
    parsed, marker_found, error = parse_stop_fields_json(prompt_response)
    passthrough = _strip_gemini_stop_markers(prompt_response)

    if isinstance(parsed, dict):
        stop_fields = {str(k): v for k, v in parsed.items()}
        if passthrough and not stop_fields.get("summary"):
            stop_fields["summary"] = passthrough
        return stop_fields, passthrough, ""

    return None, passthrough or prompt_response.strip(), str(error or "") if marker_found else ""


def _strip_gemini_stop_markers(text: str) -> str:
    cleaned = text
    fenced_patterns = (
        r"```(?:stop-fields|stop_fields)\s*\{.*?\}\s*```",
        r"```json\s*\{.*?\"challenge_coverage\".*?\}\s*```",
    )
    for pattern in fenced_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    marker = "STOP_FIELDS_JSON:"
    marker_idx = cleaned.rfind(marker)
    if marker_idx != -1:
        cleaned = cleaned[:marker_idx]
    return cleaned.strip()

def _rewrite_legacy_trailer_markers(message: str) -> str:
    return (
        message.replace("CORTEX_STOP_JSON:", "STOP_FIELDS_JSON:")
        .replace("```cortex-stop", "```stop-fields")
        .replace("```cortex_stop", "```stop_fields")
    )
```

### `cortex/hooks/_shared.py`

```python
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from cortex.core import CortexKernel

HOOK_SCHEMA_NATIVE = "native_hook_v1"
HOOK_SCHEMA_LEGACY = "legacy_json_v0"
_NATIVE_ALIAS = "".join(["cl", "aude_native_v1"])
_STOP_PRIORITY_PREFIXES = (
    "Structured stop payload is required",
    "Strict mode rejects Stop message-fallback payloads",
    "Truth claims reported gaps:",
    "Requirement audit reported gaps:",
    "Missing challenge coverage for categories:",
    "Challenge coverage '",
    "Stop attempt is highly similar to the previous failed Stop;",
)
_STOP_IGNORED_PREFIXES = ("Using ", "Truth claims note:", "Requirement audit note:")


def run_hook(
    *,
    hook_name: str,
    event_name: str,
    argv: list[str] | None = None,
) -> int:
    args = _parse_args(argv)
    try:
        if args.adapter is not None:
            raise ValueError(
                "--adapter is no longer supported. Configure [runtime].adapter in cortex.toml."
            )
        payload = _read_stdin_json()
        kernel = CortexKernel(root=args.root, config_path=args.config)
        result = kernel.dispatch(event_name, payload)
        result = _legacy_hook_name_override(hook_name=hook_name, result=result)
        print(json.dumps(_format_hook_output(hook_name=hook_name, result=result, schema_version=args.schema_version)))
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps(_format_hook_error(hook_name=hook_name, error=str(exc), schema_version=args.schema_version)))
        return 1


def _read_stdin_json() -> dict[str, object]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Hook payload must be a JSON object")
    return data


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root", default=".")
    parser.add_argument("--config")
    parser.add_argument("--adapter")
    parser.add_argument("--schema-version", default=HOOK_SCHEMA_LEGACY)
    args = parser.parse_args([] if argv is None else argv)
    args.schema_version = _normalize_schema_version(str(args.schema_version))
    return args


def _normalize_schema_version(raw: str) -> str:
    schema_version = str(raw or "").strip()
    if schema_version in {HOOK_SCHEMA_NATIVE, _NATIVE_ALIAS}:
        return HOOK_SCHEMA_NATIVE
    if schema_version == HOOK_SCHEMA_LEGACY:
        return HOOK_SCHEMA_LEGACY
    raise ValueError(
        "Unsupported --schema-version. Use one of: "
        f"{HOOK_SCHEMA_NATIVE}, {_NATIVE_ALIAS}, {HOOK_SCHEMA_LEGACY}"
    )


def _format_hook_output(*, hook_name: str, result: dict[str, Any], schema_version: str) -> dict[str, Any]:
    if schema_version == HOOK_SCHEMA_LEGACY:
        return result
    warnings = _warning_strings(result)
    if hook_name == "SessionStart":
        return _native_session_start_output(result)
    if hook_name == "PreToolUse":
        proceed = bool(result.get("proceed", True))
        decision = "allow" if proceed else "deny"
        output: dict[str, Any] = {
            "permissionDecision": decision,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
            },
        }
        if not proceed:
            output["hookSpecificOutput"]["permissionDecisionReason"] = _primary_reason(hook_name, result)
        return output
    if hook_name == "PostToolUseFailure":
        return _native_post_tool_use_failure_output(result)
    if hook_name in {"PostToolUse", "Stop"}:
        reason = _primary_reason(hook_name, result)
        repair_messages: list[str] = []
        repair_brief = ""
        if hook_name == "Stop" and _stop_stage(result) in {"repair", "reorient"}:
            repair_messages = _kernel_repair_target_messages(result)
            repair_brief = _repair_brief_message(repair_messages)
        if hook_name == "Stop" and _is_stuck_result(result):
            return {"continue": False, "stopReason": reason}
        if hook_name == "Stop" and _stop_stage(result) == "halt":
            return {"continue": False, "stopReason": reason}
        if bool(result.get("proceed", True)):
            return {}
        if hook_name == "Stop":
            response = {"decision": "block", "reason": reason}
            if not repair_brief:
                return response
            return _attach_advisories(
                response,
                warnings=warnings,
                primary=reason,
                repair_brief=repair_brief,
                repair_messages=repair_messages,
            )
        return {"decision": "block", "reason": reason}
    return result


def _format_hook_error(*, hook_name: str, error: str, schema_version: str) -> dict[str, Any]:
    if schema_version == HOOK_SCHEMA_LEGACY:
        return {"ok": False, "hook": hook_name, "error": error}
    if hook_name == "PreToolUse":
        return {
            "permissionDecision": "deny",
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": error,
            }
        }
    if hook_name == "SessionStart":
        return {"systemMessage": error}
    if hook_name == "PostToolUseFailure":
        return {"systemMessage": error}
    if hook_name in {"PostToolUse", "Stop"}:
        return {"decision": "block", "reason": error}
    return {"decision": "block", "reason": error}


def _legacy_hook_name_override(*, hook_name: str, result: dict[str, Any]) -> dict[str, Any]:
    if hook_name != "PostToolUseFailure":
        return result
    updated = dict(result)
    updated["hook"] = hook_name
    return updated


def _native_session_start_output(result: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    completion_preview = str(result.get("completion_preview") or "").strip()
    if completion_preview:
        output["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": completion_preview,
        }
    warnings = _warning_strings(result)
    if warnings:
        output["systemMessage"] = _warnings_message(warnings)
    return output


def _native_post_tool_use_failure_output(result: dict[str, Any]) -> dict[str, Any]:
    warnings = _warning_strings(result)
    if not warnings:
        return {}
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUseFailure",
            "additionalContext": _warnings_message(warnings),
        }
    }


def _primary_reason(hook_name: str, result: dict[str, Any]) -> str:
    if _is_stuck_result(result):
        return _stuck_reason(result)
    if hook_name == "Stop":
        stop_reason = _stop_reason(result)
        if stop_reason:
            return stop_reason
    warning = next((item for item in _warning_strings(result) if item), "")
    if warning:
        return warning
    if hook_name == "Stop":
        return "Cortex stop path blocked completion."
    if hook_name == "PostToolUse":
        return "Cortex post-tool gate blocked continuation."
    return "Cortex denied tool execution."


def _stop_reason(result: dict[str, Any]) -> str | None:
    objective_gap_reason = _objective_gap_priority_reason(result)
    if objective_gap_reason:
        return objective_gap_reason
    warnings = _warning_strings(result)
    warning = next((item for item in warnings if item.startswith(_STOP_PRIORITY_PREFIXES)), None)
    if warning:
        return warning
    return next((item for item in warnings if not item.startswith(_STOP_IGNORED_PREFIXES)), None)


def _objective_gap_priority_reason(result: dict[str, Any]) -> str:
    if _stop_stage(result) not in {"reorient", "halt"}:
        return ""
    return str(result.get("objective_gap_reason") or "").strip()


def _stop_stage(result: dict[str, Any]) -> str:
    return str(result.get("stop_stage") or "").strip().lower()


def _is_stuck_result(result: dict[str, Any]) -> bool:
    return bool(result.get("stuck_declared")) or str(result.get("feedback_mode") or "") == "stuck"


def _warning_strings(result: dict[str, Any]) -> list[str]:
    warnings = result.get("warnings")
    if not isinstance(warnings, list):
        return []
    return [str(raw_warning or "").strip() for raw_warning in warnings if str(raw_warning or "").strip()]


def _stuck_reason(result: dict[str, Any]) -> str:
    stuck = result.get("stuck_declaration")
    if isinstance(stuck, dict):
        check = str(stuck.get("check") or "").strip()
        obstacle = str(stuck.get("obstacle") or "").strip()
        if check and obstacle:
            return f"Cortex reported stuck on {check}: {obstacle}"
        if obstacle:
            return f"Cortex reported stuck: {obstacle}"
    return "Cortex reported stuck and could not complete the requested evidence boundary."


def _warnings_message(warnings: list[str]) -> str:
    return "\n".join(warning for warning in warnings if warning).strip()


def _kernel_repair_target_messages(result: dict[str, Any], *, limit: int = 2) -> list[str]:
    raw_targets = result.get("repair_targets")
    if not isinstance(raw_targets, list):
        return []
    messages: list[str] = []
    seen: set[str] = set()
    for raw_target in raw_targets:
        token = str(raw_target.get("message") if isinstance(raw_target, dict) else raw_target or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        messages.append(token)
        if len(messages) >= limit:
            break
    return messages


def _repair_brief_message(repair_messages: list[str]) -> str:
    if not repair_messages:
        return ""
    if len(repair_messages) == 1:
        return f"Repair focus: {repair_messages[0]}"
    lines = ["Repair focus:"]
    lines.extend(f"- {message}" for message in repair_messages)
    return "\n".join(lines)


def _attach_advisories(
    response: dict[str, Any],
    *,
    warnings: list[str],
    primary: str,
    repair_brief: str = "",
    repair_messages: list[str] | None = None,
) -> dict[str, Any]:
    repair_tokens = set(repair_messages or [])
    additional = [warning for warning in warnings if warning and warning != primary and warning not in repair_tokens]
    advisory_sections: list[str] = []
    if repair_brief:
        advisory_sections.append(repair_brief)
    if additional:
        advisory_sections.append(_warnings_message(additional))
    if advisory_sections:
        response["systemMessage"] = "\n".join(advisory_sections)
    return response
```

### `cortex/hooks/session_start.py`

```python
from __future__ import annotations

import sys

from ._shared import run_hook


def main(argv: list[str] | None = None) -> int:
    return run_hook(hook_name="SessionStart", event_name="session_start", argv=argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex/hooks/pre_tool_use.py`

```python
from __future__ import annotations

import sys

from ._shared import run_hook


def main(argv: list[str] | None = None) -> int:
    return run_hook(hook_name="PreToolUse", event_name="pre_tool_use", argv=argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex/hooks/post_tool_use.py`

```python
from __future__ import annotations

import sys

from ._shared import run_hook


def main(argv: list[str] | None = None) -> int:
    return run_hook(hook_name="PostToolUse", event_name="post_tool_use", argv=argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex/hooks/post_tool_use_failure.py`

```python
from __future__ import annotations

import sys

from ._shared import run_hook


def main(argv: list[str] | None = None) -> int:
    return run_hook(hook_name="PostToolUseFailure", event_name="post_tool_use", argv=argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex/hooks/stop.py`

```python
from __future__ import annotations

import sys

from ._shared import run_hook


def main(argv: list[str] | None = None) -> int:
    return run_hook(hook_name="Stop", event_name="stop", argv=argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex/hooks/instructions_loaded.py`

```python
from __future__ import annotations

import sys

from cortex.core import CortexKernel

from ._shared import _parse_args, _read_stdin_json


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parse_args(argv)
        if args.adapter is not None:
            raise ValueError(
                "--adapter is no longer supported. Configure [runtime].adapter in cortex.toml."
            )
        payload = _read_stdin_json()
        session_id = str(payload.get("session_id") or "").strip()
        if session_id:
            kernel = CortexKernel(root=args.root, config_path=args.config)
            kernel.ctx.store.ensure_session_start(
                session_id=session_id,
                status="running",
                genome_path=kernel.ctx.genome.source_path,
                metadata={"hook": "InstructionsLoaded", "auto_started": True},
            )
            kernel.ctx.store.record_event(
                session_id=session_id,
                hook="InstructionsLoaded",
                payload=dict(payload),
            )
    except Exception:  # noqa: BLE001
        # Telemetry-only hook: fail open and preserve runtime semantics.
        pass
    print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

### `cortex_ops_cli/gemini_hooks.py`

```python
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from cortex.core import CortexKernel
from cortex.executive import get_base_executive_function

KERNEL_EVENT_NAMES = {"SessionStart", "BeforeTool", "AfterTool", "AfterAgent"}
RETRY_STOP_REASON = "Cortex stop path failed after retry. Manual review required."


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        payload = _read_payload()
        payload = _ensure_session_id(payload, event=args.event)
        if args.event == "SessionStart":
            payload = _session_start_kernel_payload(payload)
    except Exception as exc:  # noqa: BLE001
        print(f"[cortex] Gemini bridge error: {exc}", file=sys.stderr)
        return 1

    if args.event not in KERNEL_EVENT_NAMES:
        if args.event == "BeforeAgent":
            print(json.dumps(_before_agent_output(payload, root=Path(args.root), db_path=args.db_path)))
            return 0
        print(json.dumps({}))
        return 0

    try:
        prior_retry_pending = False
        reflex_light_after_agent = False
        localized_edit_light_after_agent = False
        localized_edit_strict_after_agent = False
        after_agent_task_summary = ""
        if args.event == "AfterAgent":
            root = Path(args.root)
            session_id = str(payload.get("session_id") or "").strip()
            prior_retry_pending = _session_has_pending_after_agent_retry(
                root=root,
                db_path=args.db_path,
                session_id=session_id,
            )
            reflex_light_after_agent = _session_is_reflex_light_route_state(
                root=root,
                db_path=args.db_path,
                session_id=session_id,
            )
            localized_edit_light_after_agent = _session_is_localized_edit_light_route_state(
                root=root,
                db_path=args.db_path,
                session_id=session_id,
            )
            localized_edit_strict_after_agent = _session_is_localized_edit_strict_route_state(
                root=root,
                db_path=args.db_path,
                session_id=session_id,
            )
            after_agent_task_summary = _session_task_summary(
                root=root,
                db_path=args.db_path,
                session_id=session_id,
            )
        kernel = CortexKernel(root=args.root, config_path=args.config_path, db_path=args.db_path)
        result = kernel.dispatch(args.event, payload)
        print(
            json.dumps(
                _to_gemini_output(
                    event=args.event,
                    payload=payload,
                    result=result,
                    prior_retry_pending=prior_retry_pending,
                    reflex_light_after_agent=reflex_light_after_agent,
                    localized_edit_light_after_agent=localized_edit_light_after_agent,
                    localized_edit_strict_after_agent=localized_edit_strict_after_agent,
                    task_summary=after_agent_task_summary,
                )
            )
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"[cortex] Gemini bridge error: {exc}", file=sys.stderr)
        return 1


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("event")
    parser.add_argument("--root", default=".")
    parser.add_argument("--config-path")
    parser.add_argument("--db-path")
    return parser.parse_args(argv)


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Gemini hook payload must be a JSON object")
    return data


def _to_gemini_output(
    *,
    event: str,
    payload: dict[str, Any],
    result: dict[str, Any],
    prior_retry_pending: bool = False,
    reflex_light_after_agent: bool = False,
    localized_edit_light_after_agent: bool = False,
    localized_edit_strict_after_agent: bool = False,
    task_summary: str = "",
) -> dict[str, Any]:
    warnings = [str(item).strip() for item in (result.get("warnings") or []) if str(item).strip()]
    repair_messages = _kernel_repair_target_messages(result)
    repair_brief = _repair_brief_message(repair_messages)
    if event == "SessionStart":
        return _session_start_output(result=result, warnings=warnings)
    proceed = bool(result.get("proceed", True))
    if event == "AfterAgent" and _is_stuck_result(result):
        reason = _stuck_reason(result, warnings=warnings)
        return _attach_advisories(
            {"continue": False, "stopReason": reason},
            warnings=warnings,
            primary=reason,
        )
    if event == "AfterAgent" and _needs_after_agent_retry(result, proceed=proceed):
        reason = _retry_reason_from_result(result, warnings=warnings)
        if _requires_session_stop(result):
            return _attach_advisories(
                {"continue": False, "stopReason": reason},
                warnings=warnings,
                primary=reason,
            )
        if bool(payload.get("stop_hook_active")) or prior_retry_pending:
            return _attach_advisories(
                {"continue": False, "stopReason": RETRY_STOP_REASON},
                warnings=warnings,
                primary=RETRY_STOP_REASON,
            )
        if reflex_light_after_agent:
            return _attach_advisories(
                {"continue": False, "stopReason": reason},
                warnings=warnings,
                primary=reason,
            )
        if localized_edit_light_after_agent:
            return _attach_advisories(
                {"decision": "deny", "reason": reason},
                warnings=warnings,
                primary=reason,
                task_summary=task_summary,
                repair_brief=_localized_edit_light_repair_brief(
                    first_repair_message=repair_messages[0] if repair_messages else "",
                    scope_report=result.get("scope_report"),
                ),
                repair_messages=repair_messages,
            )
        if localized_edit_strict_after_agent:
            return _attach_advisories(
                {"decision": "deny", "reason": reason},
                warnings=warnings,
                primary=reason,
                task_summary=task_summary,
                repair_brief=_localized_edit_strict_repair_brief(
                    first_repair_message=repair_messages[0] if repair_messages else "",
                    remaining_repair_messages=repair_messages[1:] if repair_messages else [],
                    scope_report=result.get("scope_report"),
                    pre_stop_review_card=result.get("pre_stop_review_card"),
                ),
                repair_messages=repair_messages,
            )
        return _attach_advisories(
            {"decision": "deny", "reason": reason},
            warnings=warnings,
            primary=reason,
            task_summary=task_summary,
            repair_brief=repair_brief,
            repair_messages=repair_messages,
        )
    if not proceed:
        reason = _primary_reason(event=event, warnings=warnings, result=result)
        return _attach_advisories({"decision": "deny", "reason": reason}, warnings=warnings, primary=reason)
    if warnings:
        return {"systemMessage": _warnings_message(warnings)}
    return {}


def _before_agent_output(
    payload: dict[str, Any],
    *,
    root: Path,
    db_path: str | None,
) -> dict[str, Any]:
    _part_a, part_b = get_base_executive_function()
    if _payload_already_contains_anchor(payload, part_b):
        return {}
    if _session_is_low_friction_route_state(
        root=root,
        db_path=db_path,
        session_id=str(payload.get("session_id") or "").strip(),
    ):
        return {}
    return {"hookSpecificOutput": {"additionalContext": part_b}}


def _payload_already_contains_anchor(payload: dict[str, Any], anchor: str) -> bool:
    if not anchor:
        return False
    candidates = [payload.get("prompt"), payload.get("message"), payload.get("input")]
    for candidate in candidates:
        if isinstance(candidate, str) and anchor in candidate:
            return True
    return False


def _session_start_output(*, result: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    response: dict[str, Any] = {}
    additional_parts: list[str] = []
    completion_preview = str(result.get("completion_preview") or "").strip()
    if completion_preview:
        additional_parts.append(completion_preview)
    raw_blocks = result.get("context_blocks")
    context_blocks: list[str] = []
    if isinstance(raw_blocks, list):
        context_blocks = [str(item).strip() for item in raw_blocks if isinstance(item, str) and item.strip()]
    additional_parts.extend(context_blocks)
    if additional_parts:
        response["hookSpecificOutput"] = {"additionalContext": "\n\n".join(additional_parts)}
    if warnings:
        response["systemMessage"] = _warnings_message(warnings)
    return response


def _session_start_kernel_payload(payload: dict[str, Any]) -> dict[str, Any]:
    updated = dict(payload)
    updated.setdefault("runtime_mode", "gemini_native")
    updated.setdefault("stop_trailer_marker", "STOP_FIELDS_JSON")
    return updated


def _requires_session_stop(result: dict[str, Any]) -> bool:
    if _is_stuck_result(result):
        return True
    if _stop_stage(result) == "halt":
        return True
    invariant_report = result.get("invariant_report")
    if isinstance(invariant_report, dict) and invariant_report.get("ok") is False:
        return True
    return False


def _is_stuck_result(result: dict[str, Any]) -> bool:
    return bool(result.get("stuck_declared")) or str(result.get("feedback_mode") or "") == "stuck"


def _needs_after_agent_retry(result: dict[str, Any], *, proceed: bool) -> bool:
    if _stop_stage(result) in {"repair", "reorient", "halt"}:
        return True
    if not proceed:
        return True
    if bool(result.get("structured_stop_violation")):
        return True
    if bool(result.get("challenge_coverage_missing")):
        return True
    if bool(result.get("requirements_gate_gap")):
        return True
    challenge_report = result.get("challenge_report")
    if isinstance(challenge_report, dict) and challenge_report.get("ok") is False:
        return True
    return False


def _retry_reason_from_result(result: dict[str, Any], *, warnings: list[str]) -> str:
    objective_gap_reason = _objective_gap_priority_reason(result)
    if objective_gap_reason:
        return objective_gap_reason
    if bool(result.get("structured_stop_violation")):
        return "Structured stop fields are required. Include STOP_FIELDS_JSON in the final response."
    challenge_report = result.get("challenge_report")
    if isinstance(challenge_report, dict) and isinstance(challenge_report.get("missing_categories"), list):
        missing = [str(item).strip() for item in challenge_report["missing_categories"] if str(item).strip()]
        if missing:
            return "Missing challenge coverage for: " + ", ".join(missing)
    if bool(result.get("challenge_coverage_missing")):
        return "Missing challenge_coverage in stop fields. Include all active challenge categories."
    if bool(result.get("requirements_gate_gap")):
        requirement_report = result.get("requirement_audit_report")
        if isinstance(requirement_report, dict):
            req_errors = [str(item).strip() for item in (requirement_report.get("errors") or []) if str(item).strip()]
            if req_errors:
                return "Requirement evidence gaps: " + "; ".join(req_errors[:2])
        truth_claims_report = result.get("truth_claims_report")
        if isinstance(truth_claims_report, dict):
            truth_errors = [str(item).strip() for item in (truth_claims_report.get("errors") or []) if str(item).strip()]
            if truth_errors:
                return "Truth-claim evidence gaps: " + "; ".join(truth_errors[:2])
    if warnings:
        return warnings[0]
    if bool(result.get("requirements_gate_gap")):
        return "Requirement/truth claims are incomplete or unverified. Provide explicit evidence in stop fields."
    return "Cortex stop path failed."


def _objective_gap_priority_reason(result: dict[str, Any]) -> str:
    if _stop_stage(result) not in {"reorient", "halt"}:
        return ""
    return str(result.get("objective_gap_reason") or "").strip()


def _stuck_reason(result: dict[str, Any], *, warnings: list[str]) -> str:
    stuck = result.get("stuck_declaration")
    if isinstance(stuck, dict):
        check = str(stuck.get("check") or "").strip()
        obstacle = str(stuck.get("obstacle") or "").strip()
        if check and obstacle:
            return f"Cortex reported stuck on {check}: {obstacle}"
        if obstacle:
            return f"Cortex reported stuck: {obstacle}"
    if warnings:
        return warnings[0]
    return "Cortex reported stuck and could not complete the requested evidence boundary."


def _primary_reason(*, event: str, warnings: list[str], result: dict[str, Any]) -> str:
    if warnings:
        return warnings[0]
    if event == "AfterAgent":
        return "Cortex stop path failed."
    if event == "BeforeTool":
        return "Cortex blocked this tool invocation."
    return f"Cortex denied {event}."


def _warnings_message(warnings: list[str]) -> str:
    return "\n".join(f"[cortex] {warning}" for warning in warnings)


def _kernel_repair_target_messages(result: dict[str, Any], *, limit: int = 2) -> list[str]:
    raw_targets = result.get("repair_targets")
    if not isinstance(raw_targets, list):
        return []
    messages: list[str] = []
    seen: set[str] = set()
    for raw_target in raw_targets:
        if isinstance(raw_target, dict):
            token = str(raw_target.get("message") or "").strip()
        else:
            token = str(raw_target).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        messages.append(token)
        if len(messages) >= limit:
            break
    return messages


def _repair_brief_message(repair_messages: list[str]) -> str:
    if not repair_messages:
        return ""
    if len(repair_messages) == 1:
        return f"[cortex] Repair focus: {repair_messages[0]}"
    lines = ["[cortex] Repair focus:"]
    lines.extend(f"[cortex] - {message}" for message in repair_messages)
    return "\n".join(lines)


def _localized_edit_light_repair_brief(
    *,
    first_repair_message: str,
    scope_report: Any,
) -> str:
    lines: list[str] = []
    first_message = str(first_repair_message or "").strip()
    if first_message:
        lines.append(f"[cortex] Smallest remaining action: {first_message}")
    if _scope_is_overbroad(scope_report):
        lines.append("[cortex] Do not broaden scope beyond declared task targets.")
    return "\n".join(lines)


def _localized_edit_strict_repair_brief(
    *,
    first_repair_message: str,
    remaining_repair_messages: list[str],
    scope_report: Any,
    pre_stop_review_card: Any,
) -> str:
    lines: list[str] = []
    first_message = str(first_repair_message or "").strip()
    if first_message:
        lines.append(f"[cortex] Smallest remaining action: {first_message}")
    if _scope_is_overbroad(scope_report):
        lines.append("[cortex] Do not broaden scope beyond declared task targets.")
    review_line = _pre_stop_review_line(pre_stop_review_card)
    if review_line:
        lines.append(review_line)
    remaining = [str(message).strip() for message in remaining_repair_messages if str(message).strip()]
    if remaining:
        lines.append("[cortex] Remaining repair targets:")
        lines.extend(f"[cortex] - {message}" for message in remaining)
    return "\n".join(lines)


def _pre_stop_review_line(pre_stop_review_card: Any) -> str:
    if not isinstance(pre_stop_review_card, dict):
        return ""
    scope_judgment = str(pre_stop_review_card.get("scope_judgment") or "").strip() or "unassessable"
    completion_judgment = (
        str(pre_stop_review_card.get("completion_judgment") or "").strip() or "completion_blocked"
    )
    remaining_blocker = pre_stop_review_card.get("remaining_blocker")
    blocker_text = str(remaining_blocker).strip() if remaining_blocker is not None else ""
    blocker_text = blocker_text or "none"
    return (
        "[cortex] Pre-stop review: "
        f"scope={scope_judgment}; completion={completion_judgment}; blocker={blocker_text}."
    )


def _attach_advisories(
    response: dict[str, Any],
    *,
    warnings: list[str],
    primary: str,
    task_summary: str = "",
    repair_brief: str = "",
    repair_messages: list[str] | None = None,
) -> dict[str, Any]:
    repair_tokens = set(repair_messages or [])
    additional = [warning for warning in warnings if warning and warning != primary and warning not in repair_tokens]
    advisory_sections: list[str] = []
    task_line = str(task_summary or "").strip()
    if task_line:
        advisory_sections.append(f"[cortex] User task: {task_line}")
    if repair_brief:
        advisory_sections.append(repair_brief)
    if additional:
        advisory_sections.append(_warnings_message(additional))
    if advisory_sections:
        response["systemMessage"] = "\n".join(advisory_sections)
    return response


def _session_has_pending_after_agent_retry(*, root: Path, db_path: str | None, session_id: str) -> bool:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict) or str(metadata.get("hook") or "") != "Stop":
        return False
    if bool(metadata.get("stuck_declared")) or str(metadata.get("feedback_mode") or "") == "stuck":
        return False
    stage = str(metadata.get("stop_stage") or "").strip().lower()
    if stage:
        return stage in {"repair", "reorient", "halt"}
    challenge_ok = metadata.get("challenge_ok")
    return (
        bool(metadata.get("structured_stop_violation"))
        or bool(metadata.get("challenge_coverage_missing"))
        or bool(metadata.get("requirements_gate_gap"))
        or challenge_ok is False
    )


def _session_is_low_friction_route_state(*, root: Path, db_path: str | None, session_id: str) -> bool:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict):
        return False
    task_regime = str(metadata.get("task_regime") or "").strip()
    assurance_class = str(metadata.get("assurance_class") or "").strip()
    return assurance_class == "light" and task_regime in {"reflex", "localized_edit"}


def _session_is_reflex_light_route_state(*, root: Path, db_path: str | None, session_id: str) -> bool:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict):
        return False
    task_regime = str(metadata.get("task_regime") or "").strip()
    assurance_class = str(metadata.get("assurance_class") or "").strip()
    return assurance_class == "light" and task_regime == "reflex"


def _session_is_localized_edit_light_route_state(
    *,
    root: Path,
    db_path: str | None,
    session_id: str,
) -> bool:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict):
        return False
    task_regime = str(metadata.get("task_regime") or "").strip()
    assurance_class = str(metadata.get("assurance_class") or "").strip()
    return assurance_class == "light" and task_regime == "localized_edit"


def _session_is_localized_edit_strict_route_state(
    *,
    root: Path,
    db_path: str | None,
    session_id: str,
) -> bool:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict):
        return False
    task_regime = str(metadata.get("task_regime") or "").strip()
    assurance_class = str(metadata.get("assurance_class") or "").strip()
    return assurance_class == "strict" and task_regime == "localized_edit"


def _scope_is_overbroad(scope_report: Any) -> bool:
    if not isinstance(scope_report, dict):
        return False
    return str(scope_report.get("classification") or "").strip() == "overbroad"


def _session_task_summary(*, root: Path, db_path: str | None, session_id: str) -> str:
    metadata = _session_metadata(root=root, db_path=db_path, session_id=session_id)
    if not isinstance(metadata, dict):
        return ""
    return str(metadata.get("task_summary") or "").strip()


def _session_metadata(*, root: Path, db_path: str | None, session_id: str) -> dict[str, Any] | None:
    if not session_id:
        return None
    db_file = Path(db_path) if db_path else (root / ".cortex" / "cortex.db")
    if not db_file.exists():
        return None
    try:
        with sqlite3.connect(db_file) as conn:
            row = conn.execute(
                "SELECT metadata_json FROM sessions WHERE session_id = ? LIMIT 1",
                (session_id,),
            ).fetchone()
    except sqlite3.Error:
        return None
    if not row or not row[0]:
        return None
    try:
        metadata = json.loads(str(row[0]))
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return metadata if isinstance(metadata, dict) else None


def _stop_stage(result: dict[str, Any]) -> str:
    return str(result.get("stop_stage") or "").strip().lower()


def _ensure_session_id(payload: dict[str, Any], *, event: str) -> dict[str, Any]:
    data = dict(payload)
    session_id = str(data.get("session_id") or "").strip()
    if session_id:
        data["session_id"] = session_id
        return data
    basis = "|".join(
        (
            event,
            str(data.get("transcript_path") or ""),
            str(data.get("cwd") or ""),
            str(data.get("hook_event_name") or ""),
        )
    )
    fallback = "gemini-fallback-" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]
    data["session_id"] = fallback
    print(
        f"[cortex] warning: Gemini payload missing session_id for {event}; using {fallback}.",
        file=sys.stderr,
    )
    return data


if __name__ == "__main__":
    raise SystemExit(main())
```

### `cortex_ops_cli/openai_app_server_bridge.py`

```python
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from cortex.core import CortexKernel
from cortex.stop_payload import parse_stop_fields_json
from cortex.utils import _as_string_list, _unique_list

from ._openai_bridge_probe import probe_approval_blocking as _probe_approval_blocking_impl
from ._openai_bridge_probe import probe_model as _probe_model_impl
from ._openai_bridge_protocol import (
    AppServerClient,
    BridgeError,
    COMMAND_APPROVAL_METHOD,
    DEFAULT_APPROVAL_POLICY_CANDIDATES,
    FILE_CHANGE_APPROVAL_METHOD,
    execute_turn as _protocol_execute_turn,
    execute_thread_turn as _protocol_execute_thread_turn,
    initialize_app_server as _initialize_app_server,
    open_session as _protocol_open_session,
    start_thread_with_policy_fallback,
)

SCHEMA_VERSION = "openai_app_server_v1"
RUNTIME_MODE_NATIVE = "native"
RUNTIME_MODE_ASSISTED = "assisted"
ASSISTED_TERMINAL_STATE_COMPLETED = "completed"
ASSISTED_TERMINAL_STATE_STUCK = "stuck"
ASSISTED_TERMINAL_STATE_BOUNDED_HALT = "bounded_halt"
ASSISTED_TERMINAL_STATE_BOUNDED_INCOMPLETE = "bounded_incomplete"
_ASSISTED_CORRECTION_STOP_STAGES = {"repair", "reorient"}
_start_thread_with_policy_fallback = start_thread_with_policy_fallback
_OPENAI_BRIDGE_PROFILE_FILENAME = "cortex_openai_bridge.json"


_STOP_RESULT_FORWARD_KEYS = (
    "session_status",
    "proceed",
    "recommend_revert",
    "feedback_mode",
    "terminate_session",
    "stop_stage",
    "objective_gap_state",
    "objective_gap_unchanged_attempts",
    "objective_gap_signature",
    "objective_gap_reason",
    "pre_stop_review_card",
    "repair_targets",
    "stuck_declared",
    "stuck_declaration",
    "structured_stop_violation",
    "challenge_coverage_missing",
    "requirement_audit_gap",
    "truth_claims_gap",
    "requirements_gate_gap",
    "contract_diagnostic",
)


def _extract_stop_fields_from_final_text(final_text: str) -> tuple[dict[str, Any] | None, str, str]:
    parsed, marker_found, parse_error = parse_stop_fields_json(final_text)
    if parsed is not None:
        return dict(parsed), "payload.stop_fields", ""
    if marker_found:
        return None, "none", str(parse_error or "invalid_stop_fields_json")
    return None, "none", ""


def _bridge_stop_summary(stop_result: dict[str, Any]) -> dict[str, Any]:
    summary = {"enforcement_pass": bool(stop_result.get("enforcement_pass"))}
    warnings = stop_result.get("warnings")
    if isinstance(warnings, list):
        normalized_warnings = [str(item) for item in warnings if str(item).strip()]
        if normalized_warnings:
            summary["warnings"] = normalized_warnings
    for key in _STOP_RESULT_FORWARD_KEYS:
        if key in stop_result:
            summary[key] = stop_result[key]
    return summary


def _kernel_pretool_decision(
    *,
    kernel: CortexKernel,
    session_id: str,
    method: str,
    params: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    if method == COMMAND_APPROVAL_METHOD:
        command = str(params.get("command") or "")
        tool_name = "command_execution"
    elif method == FILE_CHANGE_APPROVAL_METHOD:
        command = "file_change"
        tool_name = "file_change"
    else:
        return True, {"warnings": [f"unhandled_approval_method:{method}"]}

    kernel_response = kernel.dispatch(
        "pre_tool_use",
        {
            "session_id": session_id,
            "tool_name": tool_name,
            "command": command,
            "approval_method": method,
        },
    )
    return bool(kernel_response.get("proceed", True)), kernel_response


def _handle_post_tool(
    *,
    kernel: CortexKernel,
    session_id: str,
    item: dict[str, Any],
) -> None:
    if str(item.get("type") or "") != "commandExecution":
        return
    status = str(item.get("status") or "").strip().lower()
    mapped_status = "ok"
    if status in {"failed"}:
        mapped_status = "error"
    elif status in {"declined"}:
        mapped_status = "declined"
    kernel.dispatch(
        "post_tool_use",
        {
            "session_id": session_id,
            "tool_name": "command_execution",
            "status": mapped_status,
            "tool_response": {
                "stdout": str(item.get("aggregatedOutput") or ""),
                "stderr": "",
                "exit_code": item.get("exitCode"),
            },
            "command": str(item.get("command") or ""),
            "cwd": str(item.get("cwd") or ""),
            "raw_status": status,
        },
    )


def _normalize_command_for_witness(command: str) -> str:
    raw = str(command or "").strip()
    if not raw:
        return ""
    try:
        tokens = shlex.split(raw)
    except ValueError:
        return raw
    if len(tokens) >= 3 and Path(tokens[0]).name.lower() in {"bash", "sh", "zsh"} and tokens[1] == "-lc":
        inner = str(tokens[2]).strip()
        return inner or raw
    return raw


def _execute_turn(
    *,
    codex_bin: str,
    cwd: Path,
    prompt: str,
    model: str | None,
    timeout_seconds: float,
    approval_policy_candidates: tuple[str, ...] = DEFAULT_APPROVAL_POLICY_CANDIDATES,
    approval_handler: Any,
) -> dict[str, Any]:
    return _protocol_execute_turn(
        codex_bin=codex_bin,
        cwd=cwd,
        prompt=prompt,
        model=model,
        timeout_seconds=timeout_seconds,
        approval_policy_candidates=approval_policy_candidates,
        approval_handler=approval_handler,
        client_cls=AppServerClient,
    )


def _open_bridge_session(
    *,
    codex_bin: str,
    cwd: Path,
    model: str | None,
    timeout_seconds: float,
    approval_policy_candidates: tuple[str, ...],
) -> tuple[AppServerClient, str, str]:
    return _protocol_open_session(
        codex_bin=codex_bin,
        cwd=cwd,
        model=model,
        timeout_seconds=timeout_seconds,
        approval_policy_candidates=approval_policy_candidates,
        client_cls=AppServerClient,
    )


def _execute_thread_turn(
    *,
    client: AppServerClient,
    thread_id: str,
    cwd: Path,
    prompt: str,
    approval_policy_used: str,
    approval_policy_candidates: tuple[str, ...],
    approval_handler: Any,
) -> dict[str, Any]:
    return _protocol_execute_thread_turn(
        client=client,
        thread_id=thread_id,
        cwd=cwd,
        prompt=prompt,
        approval_policy_used=approval_policy_used,
        approval_policy_candidates=approval_policy_candidates,
        approval_handler=approval_handler,
    )


def _approval_handler_for_kernel(
    *,
    kernel: CortexKernel,
    coverage_gaps: list[str],
    session_id_holder: dict[str, str],
) -> Any:
    def _approval_handler(method: str, params: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        thread_id = str(params.get("threadId") or "").strip()
        if thread_id:
            session_id_holder["value"] = thread_id
        session_id = session_id_holder["value"] or thread_id or f"openai-session-{int(time.time())}"
        proceed, kernel_response = _kernel_pretool_decision(
            kernel=kernel,
            session_id=session_id,
            method=method,
            params=params,
        )
        decision = "accept" if proceed else "decline"
        if method not in {COMMAND_APPROVAL_METHOD, FILE_CHANGE_APPROVAL_METHOD}:
            coverage_gaps.append(f"pre_tool_use_coverage_gap:{method}")
        return decision, kernel_response

    return _approval_handler


def _merge_turn_coverage(
    *,
    existing_gaps: list[str],
    turn_result: dict[str, Any],
) -> tuple[list[str], dict[str, Any], list[str], list[str]]:
    command_surface = turn_result.get("command_surface") if isinstance(turn_result.get("command_surface"), dict) else {}
    command_items_without_approval = [
        str(item)
        for item in command_surface.get("command_items_without_approval", [])
        if str(item).strip()
    ]
    nonblocking_declines = [
        str(item) for item in command_surface.get("nonblocking_declines", []) if str(item).strip()
    ]
    merged = list(existing_gaps)
    if command_items_without_approval:
        merged.append("pre_tool_use_partial_surface_trusted_commands")
    if nonblocking_declines:
        merged.append("pre_tool_use_nonblocking_approval")
    merged.extend(str(v) for v in turn_result.get("coverage_gaps") or [])
    return sorted(set(merged)), command_surface, command_items_without_approval, nonblocking_declines


def _dispatch_post_tool_events(
    *,
    kernel: CortexKernel,
    session_id: str,
    cwd: Path,
    turn_result: dict[str, Any],
) -> None:
    approval_command_by_item_id: dict[str, dict[str, str]] = {}
    for request in turn_result.get("approval_requests") or []:
        if not isinstance(request, dict):
            continue
        item_id = str(request.get("item_id") or "").strip()
        if not item_id:
            continue
        approval_command_by_item_id[item_id] = {
            "command": str(request.get("command") or "").strip(),
            "cwd": str(request.get("cwd") or "").strip(),
        }

    for item in turn_result.get("command_completion_items") or []:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("item_id") or "").strip()
        completion_command = str(item.get("command") or "").strip()
        completion_cwd = str(item.get("cwd") or "").strip()
        fallback_command = approval_command_by_item_id.get(item_id, {}).get("command", "")
        fallback_cwd = approval_command_by_item_id.get(item_id, {}).get("cwd", "")
        resolved_command = completion_command or fallback_command
        resolved_cwd = completion_cwd or fallback_cwd or str(cwd)
        normalized_command = _normalize_command_for_witness(resolved_command)
        _handle_post_tool(
            kernel=kernel,
            session_id=session_id,
            item={
                "type": "commandExecution",
                "status": item.get("status"),
                "exitCode": item.get("exit_code"),
                "aggregatedOutput": item.get("aggregated_output"),
                "command": normalized_command,
                "cwd": resolved_cwd,
            },
        )


def _collect_turn_summary(
    *,
    kernel: CortexKernel,
    cwd: Path,
    session_id: str,
    turn_result: dict[str, Any],
    coverage_gaps: list[str],
) -> dict[str, Any]:
    merged_coverage_gaps, command_surface, command_items_without_approval, nonblocking_declines = _merge_turn_coverage(
        existing_gaps=coverage_gaps,
        turn_result=turn_result,
    )
    _dispatch_post_tool_events(
        kernel=kernel,
        session_id=session_id,
        cwd=cwd,
        turn_result=turn_result,
    )
    final_text = str(turn_result.get("text") or "")
    stop_fields, stop_fields_source, stop_fields_parse_error = _extract_stop_fields_from_final_text(final_text)
    stop_payload: dict[str, Any] = {
        "session_id": session_id,
        "last_assistant_message": final_text,
        "final_text": final_text,
    }
    if stop_fields is not None:
        stop_payload["stop_fields"] = stop_fields
    stop_result = kernel.dispatch("stop", stop_payload)
    return {
        "text": final_text,
        "thread_id": turn_result.get("thread_id"),
        "turn_id": turn_result.get("turn_id"),
        "approval_policy_used": turn_result.get("approval_policy_used"),
        "coverage_gaps": merged_coverage_gaps,
        "command_surface": command_surface,
        "command_items_without_approval": command_items_without_approval,
        "nonblocking_declines": nonblocking_declines,
        "command_items_with_approval_count": len(command_surface.get("command_items_with_approval", [])),
        "command_items_without_approval_count": len(command_items_without_approval),
        "nonblocking_decline_count": len(nonblocking_declines),
        "duplicate_turn_completed_count": int(turn_result.get("duplicate_turn_completed_count") or 0),
        "approval_request_count": len(turn_result.get("approval_requests") or []),
        "command_completion_count": len(turn_result.get("command_completion_items") or []),
        "stop_fields_present": bool(stop_fields is not None),
        "stop_fields_parse_error": stop_fields_parse_error,
        "stop_fields_source": stop_fields_source,
        "elapsed_seconds": turn_result.get("elapsed_seconds"),
        "stop_result": stop_result,
    }


def _bridge_response(
    *,
    turn_summary: dict[str, Any],
    session_id: str,
    runtime_mode: str,
    elapsed_seconds: float | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    response = {
        "ok": True,
        "runtime_mode": runtime_mode,
        "text": turn_summary["text"],
        "session_id": session_id,
        "thread_id": turn_summary.get("thread_id"),
        "turn_id": turn_summary.get("turn_id"),
        "approval_policy_used": turn_summary.get("approval_policy_used"),
        "coverage_gaps": turn_summary["coverage_gaps"],
        "command_items_with_approval_count": int(turn_summary.get("command_items_with_approval_count") or 0),
        "command_items_without_approval_count": int(turn_summary.get("command_items_without_approval_count") or 0),
        "nonblocking_decline_count": int(turn_summary.get("nonblocking_decline_count") or 0),
        "duplicate_turn_completed_count": int(turn_summary.get("duplicate_turn_completed_count") or 0),
        "approval_request_count": int(turn_summary.get("approval_request_count") or 0),
        "command_completion_count": int(turn_summary.get("command_completion_count") or 0),
        "stop_fields_present": bool(turn_summary.get("stop_fields_present")),
        "stop_fields_parse_error": str(turn_summary.get("stop_fields_parse_error") or ""),
        "stop_fields_source": str(turn_summary.get("stop_fields_source") or "none"),
        "elapsed_seconds": elapsed_seconds,
    }
    response.update(_bridge_stop_summary(turn_summary["stop_result"]))
    if extra:
        response.update(extra)
    return response


def _compose_assisted_initial_prompt(
    *,
    prompt: str,
    session_start_result: dict[str, Any],
) -> str:
    context_blocks = [
        str(block).strip()
        for block in session_start_result.get("context_blocks", [])
        if str(block).strip()
    ]
    completion_preview = str(session_start_result.get("completion_preview") or "").strip()
    evidence_expectation = str(session_start_result.get("evidence_expectation") or "").strip()
    warnings = [str(item).strip() for item in session_start_result.get("warnings", []) if str(item).strip()]
    lines = ["Cortex assisted runtime is active for this run."]
    lines.extend(["", "User task:", prompt])
    if completion_preview:
        lines.extend(["", completion_preview])
    if evidence_expectation:
        lines.extend(["", evidence_expectation])
    if context_blocks:
        lines.append("")
        lines.append("Cortex session context:")
        for block in context_blocks:
            lines.append(block)
            lines.append("")
        if lines[-1] == "":
            lines.pop()
    if warnings:
        lines.append("")
        lines.append("Session-start notes:")
        lines.extend(f"- {warning}" for warning in warnings[:6])
    return "\n".join(lines).strip()


def _assisted_required_requirement_ids(*, root: Path, cwd: Path, cli_ids: list[str]) -> list[str]:
    explicit_cli_ids = _unique_list(_as_string_list(cli_ids))
    if explicit_cli_ids:
        return explicit_cli_ids
    profile_path = (root / ".codex" / _OPENAI_BRIDGE_PROFILE_FILENAME).resolve()
    if not profile_path.exists():
        profile_path = (cwd / ".codex" / _OPENAI_BRIDGE_PROFILE_FILENAME).resolve()
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    return _unique_list(_as_string_list(data.get("required_requirement_ids")))


def _assisted_feedback_items(
    stop_result: dict[str, Any],
    *,
    exclude: list[str] | None = None,
    include_warnings: bool = True,
    limit: int = 6,
) -> list[str]:
    items: list[str] = []
    excluded = {token.strip() for token in (exclude or []) if token and token.strip()}

    def _diagnostic_text(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, dict):
            gap_description = str(value.get("gap_description") or "").strip()
            if gap_description:
                return gap_description
            evidence_expected = value.get("evidence_expected")
            evidence_found = value.get("evidence_found")
            parts: list[str] = []
            if isinstance(evidence_expected, list) and evidence_expected:
                parts.append("expected: " + ", ".join(str(item).strip() for item in evidence_expected if str(item).strip()))
            if isinstance(evidence_found, list) and evidence_found:
                parts.append("found: " + ", ".join(str(item).strip() for item in evidence_found if str(item).strip()))
            if parts:
                return "; ".join(parts)
            return ""
        return str(value).strip()

    def _append_many(values: Any) -> None:
        if not isinstance(values, list):
            return
        for value in values:
            token = _diagnostic_text(value)
            if token and token not in excluded:
                items.append(token)

    contract_diagnostic = _diagnostic_text(stop_result.get("contract_diagnostic"))
    if contract_diagnostic and contract_diagnostic not in excluded:
        items.append(contract_diagnostic)
    _append_many(stop_result.get("challenge_diagnostics"))
    _append_many(stop_result.get("requirement_audit_diagnostics"))
    _append_many(stop_result.get("truth_claims_diagnostics"))
    if include_warnings:
        _append_many(stop_result.get("warnings"))

    unique: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item if len(item) <= 320 else item[:317] + "...")
        if len(unique) >= limit:
            break
    return unique


def _kernel_repair_target_messages(stop_result: dict[str, Any]) -> list[str]:
    raw_targets = stop_result.get("repair_targets")
    if not isinstance(raw_targets, list):
        return []

    messages: list[str] = []
    seen: set[str] = set()
    for raw_target in raw_targets:
        if isinstance(raw_target, dict):
            token = str(raw_target.get("message") or "").strip()
        else:
            token = str(raw_target).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        messages.append(token)
    return messages


def _pre_stop_review_card_lines(stop_result: dict[str, Any]) -> list[str]:
    card = stop_result.get("pre_stop_review_card")
    if not isinstance(card, dict):
        return []

    scope_judgment = str(card.get("scope_judgment") or "").strip()
    completion_judgment = str(card.get("completion_judgment") or "").strip()
    remaining_blocker = card.get("remaining_blocker")
    unexpected_changes = card.get("unexpected_changes")
    if not scope_judgment and not completion_judgment and remaining_blocker is None and not unexpected_changes:
        return []

    if unexpected_changes is None:
        unexpected_changes_text = "unavailable"
    else:
        values = [str(item).strip() for item in unexpected_changes if str(item).strip()] if isinstance(unexpected_changes, list) else []
        unexpected_changes_text = ", ".join(values) if values else "none"

    blocker_text = "none"
    if remaining_blocker is not None:
        blocker_text = str(remaining_blocker).strip() or "none"

    return [
        "Pre-stop review card:",
        f"- scope_judgment: {scope_judgment or 'unassessable'}",
        f"- completion_judgment: {completion_judgment or 'completion_blocked'}",
        f"- unexpected_changes: {unexpected_changes_text}",
        f"- remaining_blocker: {blocker_text}",
    ]


def _correction_scope_no_broaden_line(stop_result: dict[str, Any]) -> str | None:
    scope_report = stop_result.get("scope_report")
    if not isinstance(scope_report, dict):
        return None
    classification = str(scope_report.get("classification") or "").strip()
    if classification != "overbroad":
        return None
    return "Do not broaden scope beyond declared task targets."


def _compose_assisted_correction_prompt(*, original_task: str, stop_result: dict[str, Any]) -> str:
    stop_stage = str(stop_result.get("stop_stage") or "repair").strip() or "repair"
    objective_gap_reason = str(stop_result.get("objective_gap_reason") or "").strip()
    promoted_reorient_reason = (
        "The unresolved completion gap did not materially move. Reorient before claiming completion again."
    )
    repair_targets = _kernel_repair_target_messages(stop_result)
    smallest_remaining_action = repair_targets[0] if repair_targets else ""
    remaining_repair_targets = repair_targets[1:] if repair_targets else []
    no_broaden_line = _correction_scope_no_broaden_line(stop_result)
    lines = [
        "Cortex assisted runtime correction pass.",
        "This is the one bounded corrective attempt for this run.",
        "",
        "User task:",
        str(original_task).strip(),
    ]
    if smallest_remaining_action:
        lines.extend(["", "Smallest remaining action:", smallest_remaining_action])
    if no_broaden_line:
        lines.extend(["", no_broaden_line])
    unresolved_gap = objective_gap_reason or (promoted_reorient_reason if stop_stage == "reorient" else "")
    if unresolved_gap and unresolved_gap not in {
        smallest_remaining_action,
        no_broaden_line,
    }:
        lines.extend(["", "Unresolved gap:", unresolved_gap])
    pre_stop_review_card_lines = _pre_stop_review_card_lines(stop_result)
    if pre_stop_review_card_lines:
        lines.append("")
        lines.extend(pre_stop_review_card_lines)
    if remaining_repair_targets:
        lines.append("")
        lines.append("Repair targets:")
        lines.extend(f"- {item}" for item in remaining_repair_targets)
    feedback_items = _assisted_feedback_items(
        stop_result,
        exclude=[objective_gap_reason, *repair_targets],
        include_warnings=not bool(remaining_repair_targets),
        limit=4 if remaining_repair_targets else 6,
    )
    if feedback_items:
        lines.append("")
        lines.append("Kernel stop findings:")
        lines.extend(f"- {item}" for item in feedback_items)
    lines.extend(
        [
            "",
            "Use this one pass to either:",
            "- resolve the gap and finish with valid STOP_FIELDS_JSON",
            "- or end truthfully with STOP_FIELDS_JSON carrying the remaining failure or a truthful stuck_declaration",
        ]
    )
    return "\n".join(lines).strip()


def _should_attempt_assisted_correction(stop_result: dict[str, Any]) -> bool:
    if bool(stop_result.get("enforcement_pass")):
        return False
    if bool(stop_result.get("stuck_declared")):
        return False
    if bool(stop_result.get("terminate_session")):
        return False
    return str(stop_result.get("stop_stage") or "").strip() in _ASSISTED_CORRECTION_STOP_STAGES


def _assisted_terminal_state(stop_result: dict[str, Any]) -> str:
    if bool(stop_result.get("enforcement_pass")):
        return ASSISTED_TERMINAL_STATE_COMPLETED
    if bool(stop_result.get("stuck_declared")) or str(stop_result.get("feedback_mode") or "") == "stuck":
        return ASSISTED_TERMINAL_STATE_STUCK
    stop_stage = str(stop_result.get("stop_stage") or "").strip()
    if stop_stage == "halt":
        return ASSISTED_TERMINAL_STATE_BOUNDED_HALT
    objective_gap_state = str(stop_result.get("objective_gap_state") or "").strip()
    if bool(stop_result.get("terminate_session")) or objective_gap_state in {"stagnant", "misaligned"}:
        return ASSISTED_TERMINAL_STATE_BOUNDED_HALT
    return ASSISTED_TERMINAL_STATE_BOUNDED_INCOMPLETE


def _run_mode(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd).resolve()
    kernel = CortexKernel(root=args.root, config_path=args.config_path, db_path=args.db_path)
    coverage_gaps: list[str] = []
    session_id_holder: dict[str, str] = {"value": ""}
    approval_handler = _approval_handler_for_kernel(
        kernel=kernel,
        coverage_gaps=coverage_gaps,
        session_id_holder=session_id_holder,
    )

    result = _execute_turn(
        codex_bin=args.codex_bin,
        cwd=cwd,
        prompt=args.prompt,
        model=args.model,
        timeout_seconds=float(args.timeout_seconds),
        approval_policy_candidates=_approval_policy_candidates_from_args(args),
        approval_handler=approval_handler,
    )
    session_id = session_id_holder["value"] or str(result.get("thread_id") or "")
    turn_summary = _collect_turn_summary(
        kernel=kernel,
        cwd=cwd,
        session_id=session_id,
        turn_result=result,
        coverage_gaps=coverage_gaps,
    )
    response = _bridge_response(
        turn_summary=turn_summary,
        session_id=session_id,
        runtime_mode=RUNTIME_MODE_NATIVE,
        elapsed_seconds=turn_summary.get("elapsed_seconds"),
    )
    print(json.dumps(response, sort_keys=True))
    return 0


def _run_assisted_mode(args: argparse.Namespace) -> int:
    cwd = Path(args.cwd).resolve()
    root = Path(args.root).resolve()
    kernel = CortexKernel(root=args.root, config_path=args.config_path, db_path=args.db_path)
    coverage_gaps: list[str] = []
    session_id_holder: dict[str, str] = {"value": ""}
    approval_policy_candidates = _approval_policy_candidates_from_args(args)
    approval_handler = _approval_handler_for_kernel(
        kernel=kernel,
        coverage_gaps=coverage_gaps,
        session_id_holder=session_id_holder,
    )
    started_at = time.time()
    client: AppServerClient | None = None
    try:
        client, thread_id, approval_policy_used = _open_bridge_session(
            codex_bin=args.codex_bin,
            cwd=cwd,
            model=args.model,
            timeout_seconds=float(args.timeout_seconds),
            approval_policy_candidates=approval_policy_candidates,
        )
        session_id_holder["value"] = thread_id
        session_start_payload: dict[str, Any] = {
            "session_id": thread_id,
            "task": args.prompt,
            "objective": args.prompt,
            "runtime_mode": RUNTIME_MODE_ASSISTED,
            "stop_trailer_marker": "STOP_FIELDS_JSON",
        }
        required_requirement_ids = _assisted_required_requirement_ids(
            root=root,
            cwd=cwd,
            cli_ids=list(getattr(args, "required_requirement_ids", []) or []),
        )
        if required_requirement_ids:
            session_start_payload["required_requirement_ids"] = required_requirement_ids
        session_start_result = kernel.dispatch(
            "session_start",
            session_start_payload,
        )
        initial_prompt = _compose_assisted_initial_prompt(
            prompt=args.prompt,
            session_start_result=session_start_result,
        )
        first_turn_result = _execute_thread_turn(
            client=client,
            thread_id=thread_id,
            cwd=cwd,
            prompt=initial_prompt,
            approval_policy_used=approval_policy_used,
            approval_policy_candidates=approval_policy_candidates,
            approval_handler=approval_handler,
        )
        first_turn_summary = _collect_turn_summary(
            kernel=kernel,
            cwd=cwd,
            session_id=thread_id,
            turn_result=first_turn_result,
            coverage_gaps=coverage_gaps,
        )
        final_turn_summary = first_turn_summary
        correction_triggered = False
        if _should_attempt_assisted_correction(first_turn_summary["stop_result"]):
            correction_triggered = True
            correction_prompt = _compose_assisted_correction_prompt(
                original_task=args.prompt,
                stop_result=first_turn_summary["stop_result"]
            )
            second_turn_result = _execute_thread_turn(
                client=client,
                thread_id=thread_id,
                cwd=cwd,
                prompt=correction_prompt,
                approval_policy_used=approval_policy_used,
                approval_policy_candidates=approval_policy_candidates,
                approval_handler=approval_handler,
            )
            final_turn_summary = _collect_turn_summary(
                kernel=kernel,
                cwd=cwd,
                session_id=thread_id,
                turn_result=second_turn_result,
                coverage_gaps=first_turn_summary["coverage_gaps"],
            )
            final_turn_summary = {
                **final_turn_summary,
                "command_items_with_approval_count": (
                    int(first_turn_summary.get("command_items_with_approval_count") or 0)
                    + int(final_turn_summary.get("command_items_with_approval_count") or 0)
                ),
                "command_items_without_approval_count": (
                    int(first_turn_summary.get("command_items_without_approval_count") or 0)
                    + int(final_turn_summary.get("command_items_without_approval_count") or 0)
                ),
                "nonblocking_decline_count": (
                    int(first_turn_summary.get("nonblocking_decline_count") or 0)
                    + int(final_turn_summary.get("nonblocking_decline_count") or 0)
                ),
                "duplicate_turn_completed_count": (
                    int(first_turn_summary.get("duplicate_turn_completed_count") or 0)
                    + int(final_turn_summary.get("duplicate_turn_completed_count") or 0)
                ),
                "approval_request_count": (
                    int(first_turn_summary.get("approval_request_count") or 0)
                    + int(final_turn_summary.get("approval_request_count") or 0)
                ),
                "command_completion_count": (
                    int(first_turn_summary.get("command_completion_count") or 0)
                    + int(final_turn_summary.get("command_completion_count") or 0)
                ),
            }
        elapsed_seconds = round(time.time() - started_at, 6)
        response = _bridge_response(
            turn_summary=final_turn_summary,
            session_id=thread_id,
            runtime_mode=RUNTIME_MODE_ASSISTED,
            elapsed_seconds=elapsed_seconds,
            extra={
                "session_start_completion_preview_present": bool(
                    str(session_start_result.get("completion_preview") or "").strip()
                ),
                "session_start_evidence_expectation_present": bool(
                    str(session_start_result.get("evidence_expectation") or "").strip()
                ),
                "session_start_required_requirement_ids": list(
                    session_start_result.get("required_requirement_ids") or []
                ),
                "session_start_completion_preview_line_count": len(
                    [
                        line
                        for line in str(session_start_result.get("completion_preview") or "").splitlines()
                        if line.strip()
                    ]
                ),
                "turn_attempt_count": 2 if correction_triggered else 1,
                "correction_triggered": correction_triggered,
                "assisted_terminal_state": _assisted_terminal_state(final_turn_summary["stop_result"]),
                "session_start_context_block_count": len(
                    [
                        str(block).strip()
                        for block in session_start_result.get("context_blocks", [])
                        if str(block).strip()
                    ]
                ),
                "session_start_warning_count": len(
                    [str(item).strip() for item in session_start_result.get("warnings", []) if str(item).strip()]
                ),
                "initial_stop_stage": first_turn_summary["stop_result"].get("stop_stage"),
                "initial_objective_gap_reason": first_turn_summary["stop_result"].get("objective_gap_reason"),
                "initial_repair_targets": list(first_turn_summary["stop_result"].get("repair_targets") or []),
            },
        )
        print(json.dumps(response, sort_keys=True))
        return 0
    finally:
        if client is not None:
            client.close()


def _probe_approval_blocking(args: argparse.Namespace) -> int:
    return _probe_approval_blocking_impl(
        args=args,
        command_approval_method=COMMAND_APPROVAL_METHOD,
        execute_turn=_execute_turn,
        approval_policy_candidates_from_args=_approval_policy_candidates_from_args,
    )


def _probe_model(args: argparse.Namespace) -> int:
    return _probe_model_impl(
        args=args,
        app_server_client_cls=AppServerClient,
        initialize_app_server=_initialize_app_server,
        bridge_error_cls=BridgeError,
        run_exec=subprocess.run,
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("--schema-version", choices=[SCHEMA_VERSION], default=SCHEMA_VERSION)
    run.add_argument("--codex-bin", default="codex")
    run.add_argument("--cwd", default=".")
    run.add_argument("--root", default=".")
    run.add_argument("--config-path")
    run.add_argument("--db-path")
    run.add_argument("--model")
    run.add_argument("--prompt", required=True)
    run.add_argument("--timeout-seconds", type=float, default=180.0)
    run.add_argument(
        "--approval-policy-candidates",
        default=",".join(DEFAULT_APPROVAL_POLICY_CANDIDATES),
        help="Comma-delimited thread/start approvalPolicy fallback order.",
    )

    run_assisted = sub.add_parser("run-assisted")
    run_assisted.add_argument("--schema-version", choices=[SCHEMA_VERSION], default=SCHEMA_VERSION)
    run_assisted.add_argument("--codex-bin", default="codex")
    run_assisted.add_argument("--cwd", default=".")
    run_assisted.add_argument("--root", default=".")
    run_assisted.add_argument("--config-path")
    run_assisted.add_argument("--db-path")
    run_assisted.add_argument("--model")
    run_assisted.add_argument("--prompt", required=True)
    run_assisted.add_argument("--timeout-seconds", type=float, default=180.0)
    run_assisted.add_argument(
        "--required-requirement-id",
        dest="required_requirement_ids",
        action="append",
        default=[],
        help="Explicit requirement_audit ids to pass into assisted session start.",
    )
    run_assisted.add_argument(
        "--approval-policy-candidates",
        default=",".join(DEFAULT_APPROVAL_POLICY_CANDIDATES),
        help="Comma-delimited thread/start approvalPolicy fallback order.",
    )

    probe = sub.add_parser("probe-approval-blocking")
    probe.add_argument("--schema-version", choices=[SCHEMA_VERSION], default=SCHEMA_VERSION)
    probe.add_argument("--codex-bin", default="codex")
    probe.add_argument("--cwd", default=".")
    probe.add_argument("--model")
    probe.add_argument("--timeout-seconds", type=float, default=180.0)
    probe.add_argument("--prompt", default="")
    probe.add_argument(
        "--approval-policy-candidates",
        default=",".join(DEFAULT_APPROVAL_POLICY_CANDIDATES),
        help="Comma-delimited thread/start approvalPolicy fallback order.",
    )

    probe_model = sub.add_parser("probe-model")
    probe_model.add_argument("--schema-version", choices=[SCHEMA_VERSION], default=SCHEMA_VERSION)
    probe_model.add_argument("--codex-bin", default="codex")
    probe_model.add_argument("--cwd", default=".")
    probe_model.add_argument("--model", required=True)
    probe_model.add_argument("--timeout-seconds", type=float, default=180.0)

    return parser.parse_args(argv)


def _approval_policy_candidates_from_args(args: argparse.Namespace) -> tuple[str, ...]:
    raw = getattr(args, "approval_policy_candidates", None)
    if raw is None:
        return DEFAULT_APPROVAL_POLICY_CANDIDATES
    if isinstance(raw, str):
        parsed = tuple(token.strip() for token in raw.split(",") if token.strip())
        return parsed or DEFAULT_APPROVAL_POLICY_CANDIDATES
    if isinstance(raw, (list, tuple)):
        parsed = tuple(str(token).strip() for token in raw if str(token).strip())
        return parsed or DEFAULT_APPROVAL_POLICY_CANDIDATES
    return DEFAULT_APPROVAL_POLICY_CANDIDATES


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.command == "run":
            return _run_mode(args)
        if args.command == "run-assisted":
            return _run_assisted_mode(args)
        if args.command == "probe-approval-blocking":
            return _probe_approval_blocking(args)
        if args.command == "probe-model":
            return _probe_model(args)
        raise BridgeError(f"Unsupported command: {args.command}")
    except BridgeError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `cortex_ops_cli/_openai_bridge_protocol.py`

```python
from __future__ import annotations

import json
import select
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

COMMAND_APPROVAL_METHOD = "item/commandExecution/requestApproval"
FILE_CHANGE_APPROVAL_METHOD = "item/fileChange/requestApproval"
NOTIFICATION_ITEM_COMPLETED = "item/completed"
NOTIFICATION_TURN_COMPLETED = "turn/completed"
NOTIFICATION_TASK_COMPLETE = "codex/event/task_complete"
NOTIFICATION_THREAD_STATUS_CHANGED = "thread/status/changed"
DEFAULT_APPROVAL_POLICY_CANDIDATES = ("untrusted", "unlessTrusted", "on-request")


class BridgeError(RuntimeError):
    pass


class AppServerClient:
    def __init__(self, *, codex_bin: str, cwd: Path, timeout_seconds: float) -> None:
        cmd = [codex_bin, "app-server", "--listen", "stdio://"]
        self.proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.timeout_seconds = timeout_seconds
        self._next_request_id = 1
        self._pending_messages: list[dict[str, Any]] = []

    def close(self) -> None:
        if self.proc.poll() is not None:
            return
        try:
            self.proc.terminate()
            self.proc.wait(timeout=1.0)
        except Exception:
            self.proc.kill()
            self.proc.wait(timeout=1.0)

    def _write(self, payload: dict[str, Any]) -> None:
        if self.proc.stdin is None:
            raise BridgeError("codex app-server stdin unavailable")
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def _read_line(self, timeout_seconds: float) -> str:
        if self.proc.stdout is None:
            raise BridgeError("codex app-server stdout unavailable")
        fd = self.proc.stdout.fileno()
        ready, _, _ = select.select([fd], [], [], timeout_seconds)
        if not ready:
            raise BridgeError("Timed out waiting for codex app-server response")
        line = self.proc.stdout.readline()
        if not line:
            stderr = ""
            if self.proc.stderr is not None:
                try:
                    stderr = self.proc.stderr.read().strip()
                except Exception:
                    stderr = ""
            raise BridgeError(f"codex app-server closed stdout. stderr={stderr[:4000]}")
        return line

    def _read_message(self, timeout_seconds: float, *, allow_pending: bool = True) -> dict[str, Any]:
        if allow_pending and self._pending_messages:
            return self._pending_messages.pop(0)
        line = self._read_line(timeout_seconds)
        try:
            decoded = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BridgeError(f"Invalid JSON-RPC payload from app-server: {exc}") from exc
        if not isinstance(decoded, dict):
            raise BridgeError("Invalid JSON-RPC payload from app-server: expected object")
        return decoded

    def _pop_pending_response(self, request_id: int) -> dict[str, Any] | None:
        for idx, msg in enumerate(self._pending_messages):
            if msg.get("id") == request_id and ("result" in msg or "error" in msg):
                return self._pending_messages.pop(idx)
        return None

    def request(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        *,
        timeout_seconds: float | None = None,
    ) -> Any:
        request_id = self._next_request_id
        self._next_request_id += 1
        self._write({"id": request_id, "method": method, "params": params or {}})
        deadline = time.time() + (self.timeout_seconds if timeout_seconds is None else timeout_seconds)
        while True:
            pending_response = self._pop_pending_response(request_id)
            if pending_response is not None:
                if "error" in pending_response:
                    raise BridgeError(f"JSON-RPC {method} failed: {pending_response['error']}")
                return pending_response.get("result")

            remaining = deadline - time.time()
            if remaining <= 0:
                raise BridgeError(f"Timed out waiting for JSON-RPC response to {method}")

            msg = self._read_message(max(0.01, remaining), allow_pending=False)
            if msg.get("id") == request_id and ("result" in msg or "error" in msg):
                if "error" in msg:
                    raise BridgeError(f"JSON-RPC {method} failed: {msg['error']}")
                return msg.get("result")
            self._pending_messages.append(msg)

    def send_notification(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._write({"method": method, "params": params or {}})

    def send_server_request_result(self, request_id: Any, result: dict[str, Any]) -> None:
        self._write({"id": request_id, "result": result})

    def next_message(self, *, timeout_seconds: float | None = None) -> dict[str, Any]:
        return self._read_message(self.timeout_seconds if timeout_seconds is None else timeout_seconds)


class BridgeRunResult(dict):
    pass


def classify_command_surface(
    *,
    command_items: list[dict[str, Any]],
    approval_requests: list[dict[str, Any]],
) -> dict[str, Any]:
    approved_item_ids = {
        str(item.get("item_id") or "").strip()
        for item in approval_requests
        if isinstance(item, dict) and str(item.get("method")) == COMMAND_APPROVAL_METHOD
    }
    approved_item_ids.discard("")
    command_item_ids = {
        str(item.get("item_id") or "").strip()
        for item in command_items
        if isinstance(item, dict)
    }
    command_item_ids.discard("")

    with_approval = sorted(command_item_ids & approved_item_ids)
    without_approval = sorted(command_item_ids - approved_item_ids)
    declined_item_ids = {
        str(item.get("item_id") or "").strip()
        for item in approval_requests
        if isinstance(item, dict)
        and str(item.get("method")) == COMMAND_APPROVAL_METHOD
        and str(item.get("decision")) == "decline"
    }
    declined_item_ids.discard("")

    nonblocking_declines: list[str] = []
    for item in command_items:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("item_id") or "").strip()
        if item_id not in declined_item_ids:
            continue
        status = str(item.get("status") or "").strip().lower()
        has_exec_payload = item.get("exit_code") is not None or bool(
            str(item.get("aggregated_output") or "").strip()
        )
        if status != "declined" or has_exec_payload:
            nonblocking_declines.append(item_id or "<missing_item_id>")

    return {
        "command_item_ids": sorted(command_item_ids),
        "approved_item_ids": sorted(approved_item_ids),
        "command_items_with_approval": with_approval,
        "command_items_without_approval": without_approval,
        "declined_item_ids": sorted(declined_item_ids),
        "nonblocking_declines": sorted(set(nonblocking_declines)),
    }


def initialize_app_server(*, client: AppServerClient) -> None:
    init_result = client.request(
        "initialize",
        {
            "clientInfo": {
                "name": "cortex-openai-bridge",
                "title": "Cortex OpenAI Bridge",
                "version": "1.0.0",
            },
            "capabilities": {
                "experimentalApi": False,
                "optOutNotificationMethods": [],
            },
        },
    )
    if not isinstance(init_result, dict):
        raise BridgeError("initialize did not return a JSON object")
    client.send_notification("initialized", {})


def is_policy_compat_error(exc: BridgeError) -> bool:
    message = str(exc).lower()
    return (
        "approvalpolicy" in message
        or "askforapproval" in message
        or "unknown variant" in message
        or "invalid type" in message
        or "invalid value" in message
        or "unlesstrusted" in message
    )


def start_thread_with_policy_fallback(
    *,
    client: AppServerClient,
    cwd: Path,
    model: str | None,
    approval_policy_candidates: tuple[str, ...] = DEFAULT_APPROVAL_POLICY_CANDIDATES,
) -> tuple[dict[str, Any], str]:
    if not approval_policy_candidates:
        raise BridgeError("No approval policy candidates configured.")

    last_error: BridgeError | None = None
    for idx, policy in enumerate(approval_policy_candidates):
        params: dict[str, Any] = {
            "cwd": str(cwd),
            "approvalPolicy": policy,
            "sandbox": "workspace-write",
        }
        if model:
            params["model"] = model
        try:
            result = client.request("thread/start", params)
            if not isinstance(result, dict):
                raise BridgeError("thread/start did not return a JSON object")
            return result, policy
        except BridgeError as exc:
            last_error = exc
            if idx < len(approval_policy_candidates) - 1 and is_policy_compat_error(exc):
                continue
            raise

    if last_error is not None:
        raise last_error
    raise BridgeError("thread/start failed: no approval policy candidate succeeded")


def _bridge_turn_result(
    *,
    thread_id: str,
    turn_id: str,
    approval_policy_used: str,
    approval_policy_candidates: tuple[str, ...],
    final_text: str,
    approval_requests: list[dict[str, Any]],
    command_completion_items: list[dict[str, Any]],
    coverage_gaps: list[str],
    duplicate_turn_completed_count: int,
    elapsed_seconds: float,
) -> BridgeRunResult:
    return BridgeRunResult(
        {
            "ok": True,
            "thread_id": thread_id,
            "turn_id": turn_id,
            "approval_policy_used": approval_policy_used,
            "approval_policy_candidates": list(approval_policy_candidates),
            "text": final_text,
            "response_present": bool(final_text.strip()),
            "approval_requests": approval_requests,
            "command_completion_items": command_completion_items,
            "command_surface": classify_command_surface(
                command_items=command_completion_items,
                approval_requests=approval_requests,
            ),
            "coverage_gaps": sorted(set(coverage_gaps)),
            "duplicate_turn_completed_count": duplicate_turn_completed_count,
            "elapsed_seconds": elapsed_seconds,
        }
    )


def open_session(
    *,
    codex_bin: str,
    cwd: Path,
    model: str | None,
    timeout_seconds: float,
    approval_policy_candidates: tuple[str, ...] = DEFAULT_APPROVAL_POLICY_CANDIDATES,
    client_cls: type[AppServerClient] = AppServerClient,
) -> tuple[AppServerClient, str, str]:
    client = client_cls(codex_bin=codex_bin, cwd=cwd, timeout_seconds=timeout_seconds)
    try:
        initialize_app_server(client=client)
        thread_result, approval_policy_used = start_thread_with_policy_fallback(
            client=client,
            cwd=cwd,
            model=model,
            approval_policy_candidates=approval_policy_candidates,
        )
        thread_id = str(((thread_result or {}).get("thread") or {}).get("id") or "").strip()
        if not thread_id:
            raise BridgeError("thread/start did not return thread.id")
        return client, thread_id, approval_policy_used
    except Exception:
        client.close()
        raise


def execute_thread_turn(
    *,
    client: AppServerClient,
    thread_id: str,
    cwd: Path,
    prompt: str,
    approval_policy_used: str,
    approval_policy_candidates: tuple[str, ...] = DEFAULT_APPROVAL_POLICY_CANDIDATES,
    approval_handler: Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]],
) -> BridgeRunResult:
    start_time = time.time()
    turn_result = client.request(
        "turn/start",
        {
            "threadId": thread_id,
            "input": [{"type": "text", "text": prompt, "textElements": []}],
            "cwd": str(cwd),
        },
    )
    turn_id = str(((turn_result or {}).get("turn") or {}).get("id") or "").strip()
    if not turn_id:
        raise BridgeError("turn/start did not return turn.id")

    final_agent_messages: dict[str, str] = {}
    completed_turns: set[str] = set()
    duplicate_turn_completed_count = 0
    command_completion_items: list[dict[str, Any]] = []
    approval_requests: list[dict[str, Any]] = []
    coverage_gaps: list[str] = []
    task_complete_turns: set[str] = set()
    task_complete_last_messages: dict[str, str] = {}

    while True:
        msg = client.next_message()
        method = str(msg.get("method") or "")

        if method and "id" in msg and "result" not in msg and "error" not in msg:
            request_id = msg.get("id")
            params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
            if method in {COMMAND_APPROVAL_METHOD, FILE_CHANGE_APPROVAL_METHOD}:
                decision, metadata = approval_handler(method, params)
                if decision not in {"accept", "decline", "cancel"}:
                    decision = "decline"
                approval_requests.append(
                    {
                        "method": method,
                        "item_id": str(params.get("itemId") or ""),
                        "command": str(params.get("command") or ""),
                        "cwd": str(params.get("cwd") or ""),
                        "decision": decision,
                        "metadata": metadata,
                    }
                )
                client.send_server_request_result(request_id, {"decision": decision})
                continue
            coverage_gaps.append(f"unhandled_server_request:{method}")
            client.send_server_request_result(request_id, {"decision": "decline"})
            continue

        if not method:
            continue

        params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
        if method == NOTIFICATION_ITEM_COMPLETED:
            item = params.get("item") if isinstance(params.get("item"), dict) else {}
            item_type = str(item.get("type") or "")
            item_turn_id = str(params.get("turnId") or "")
            if item_type == "agentMessage" and item_turn_id:
                final_agent_messages[item_turn_id] = str(item.get("text") or "")
            if item_type == "commandExecution":
                command_completion_items.append(
                    {
                        "item_id": str(item.get("id") or ""),
                        "turn_id": item_turn_id,
                        "status": str(item.get("status") or ""),
                        "exit_code": item.get("exitCode"),
                        "aggregated_output": item.get("aggregatedOutput"),
                        "command": str(item.get("command") or ""),
                        "cwd": str(item.get("cwd") or ""),
                    }
                )
            continue

        if method == NOTIFICATION_TURN_COMPLETED:
            notification_turn = params.get("turn") if isinstance(params.get("turn"), dict) else {}
            completed_turn_id = str(notification_turn.get("id") or "")
            if not completed_turn_id:
                coverage_gaps.append("turn_completed_missing_turn_id")
                continue
            if completed_turn_id in completed_turns:
                duplicate_turn_completed_count += 1
                continue
            completed_turns.add(completed_turn_id)
            if completed_turn_id != turn_id:
                continue

            final_text = str(final_agent_messages.get(turn_id, "") or "")
            elapsed_seconds = round(time.time() - start_time, 6)
            return _bridge_turn_result(
                thread_id=thread_id,
                turn_id=turn_id,
                approval_policy_used=approval_policy_used,
                approval_policy_candidates=approval_policy_candidates,
                final_text=final_text,
                approval_requests=approval_requests,
                command_completion_items=command_completion_items,
                coverage_gaps=coverage_gaps,
                duplicate_turn_completed_count=duplicate_turn_completed_count,
                elapsed_seconds=elapsed_seconds,
            )

        if method == NOTIFICATION_TASK_COMPLETE:
            task_msg = params.get("msg") if isinstance(params.get("msg"), dict) else {}
            completed_turn_id = str(task_msg.get("turn_id") or params.get("id") or "").strip()
            if completed_turn_id:
                task_complete_turns.add(completed_turn_id)
                last_message = str(task_msg.get("last_agent_message") or "")
                if last_message:
                    task_complete_last_messages[completed_turn_id] = last_message
                if completed_turn_id == turn_id and completed_turn_id not in completed_turns:
                    coverage_gaps.append("turn_completed_missing_used_task_complete_fallback")
                    final_text = str(
                        final_agent_messages.get(turn_id, "")
                        or task_complete_last_messages.get(turn_id, "")
                        or ""
                    )
                    elapsed_seconds = round(time.time() - start_time, 6)
                    return _bridge_turn_result(
                        thread_id=thread_id,
                        turn_id=turn_id,
                        approval_policy_used=approval_policy_used,
                        approval_policy_candidates=approval_policy_candidates,
                        final_text=final_text,
                        approval_requests=approval_requests,
                        command_completion_items=command_completion_items,
                        coverage_gaps=coverage_gaps,
                        duplicate_turn_completed_count=duplicate_turn_completed_count,
                        elapsed_seconds=elapsed_seconds,
                    )
            continue

        if method == NOTIFICATION_THREAD_STATUS_CHANGED:
            event_thread_id = str(params.get("threadId") or "")
            status = params.get("status") if isinstance(params.get("status"), dict) else {}
            status_type = str(status.get("type") or "")
            if event_thread_id == thread_id and status_type == "idle" and turn_id in task_complete_turns:
                coverage_gaps.append("turn_completed_missing_used_task_complete_fallback")
                final_text = str(
                    final_agent_messages.get(turn_id, "")
                    or task_complete_last_messages.get(turn_id, "")
                    or ""
                )
                elapsed_seconds = round(time.time() - start_time, 6)
                return _bridge_turn_result(
                    thread_id=thread_id,
                    turn_id=turn_id,
                    approval_policy_used=approval_policy_used,
                    approval_policy_candidates=approval_policy_candidates,
                    final_text=final_text,
                    approval_requests=approval_requests,
                    command_completion_items=command_completion_items,
                    coverage_gaps=coverage_gaps,
                    duplicate_turn_completed_count=duplicate_turn_completed_count,
                    elapsed_seconds=elapsed_seconds,
                )


def execute_turn(
    *,
    codex_bin: str,
    cwd: Path,
    prompt: str,
    model: str | None,
    timeout_seconds: float,
    approval_policy_candidates: tuple[str, ...] = DEFAULT_APPROVAL_POLICY_CANDIDATES,
    approval_handler: Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]],
    client_cls: type[AppServerClient] = AppServerClient,
) -> BridgeRunResult:
    client: AppServerClient | None = None
    try:
        client, thread_id, approval_policy_used = open_session(
            codex_bin=codex_bin,
            cwd=cwd,
            model=model,
            timeout_seconds=timeout_seconds,
            approval_policy_candidates=approval_policy_candidates,
            client_cls=client_cls,
        )
        return execute_thread_turn(
            client=client,
            thread_id=thread_id,
            cwd=cwd,
            prompt=prompt,
            approval_policy_used=approval_policy_used,
            approval_policy_candidates=approval_policy_candidates,
            approval_handler=approval_handler,
        )
    finally:
        if client is not None:
            client.close()
```

### `cortex_ops_cli/_runtime_profiles.py`

```python
from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from ._runtime_profile_templates import (
    render_claude_md,
    render_claude_settings_json,
    render_gemini_md,
    render_gemini_settings_json,
    render_openai_bridge_profile_json,
    render_openai_md,
)

CLAUDE_REQUIRED_HOOK_COMMANDS = {
    "SessionStart": "cortex.hooks.session_start",
    "PreToolUse": "cortex.hooks.pre_tool_use",
    "PostToolUse": "cortex.hooks.post_tool_use",
    "PostToolUseFailure": "cortex.hooks.post_tool_use_failure",
    "Stop": "cortex.hooks.stop",
}
CLAUDE_OPTIONAL_HOOK_COMMANDS = {
    "InstructionsLoaded": "cortex.hooks.instructions_loaded",
}
CLAUDE_HOOK_SCHEMA_NATIVE = "claude_native_v1"
CLAUDE_HOOK_SCHEMA_LEGACY = "legacy_json_v0"
CLAUDE_SUPPORTED_HOOK_SCHEMAS = {CLAUDE_HOOK_SCHEMA_NATIVE, CLAUDE_HOOK_SCHEMA_LEGACY}
CLAUDE_PINNED_HOOK_SCHEMA = CLAUDE_HOOK_SCHEMA_NATIVE
GEMINI_REQUIRED_HOOK_COMMANDS = {
    "SessionStart": "cortex_ops_cli.gemini_hooks SessionStart",
    "BeforeTool": "cortex_ops_cli.gemini_hooks BeforeTool",
    "AfterTool": "cortex_ops_cli.gemini_hooks AfterTool",
    "AfterAgent": "cortex_ops_cli.gemini_hooks AfterAgent",
}
GEMINI_OPTIONAL_HOOK_COMMANDS = {
    "BeforeAgent": "cortex_ops_cli.gemini_hooks BeforeAgent",
}
GEMINI_AFTER_AGENT_BRIDGE_PATTERN = "cortex_ops_cli.gemini_hooks AfterAgent"
CLAUDE_DIRNAME, LEGACY_CLAUDE_DIRNAME = ".claude", "claude"
GEMINI_DIRNAME = ".gemini"
OPENAI_DIRNAME = ".codex"
OPENAI_BRIDGE_PROFILE_FILENAME = "cortex_openai_bridge.json"
OPENAI_BRIDGE_SCHEMA_VERSION = "openai_app_server_v1"
OPENAI_RUNTIME_MODE_NATIVE = "native"
OPENAI_RUNTIME_MODE_ASSISTED = "assisted"
OPENAI_RUNTIME_MODES = {OPENAI_RUNTIME_MODE_NATIVE, OPENAI_RUNTIME_MODE_ASSISTED}
OPENAI_BRIDGE_COMMAND_PATTERN = "cortex_ops_cli.openai_app_server_bridge run"
OPENAI_ASSISTED_BRIDGE_COMMAND_PATTERN = "cortex_ops_cli.openai_app_server_bridge run-assisted"
OPENAI_CODEX_MIN_VERSION = (0, 111, 0)
OPENAI_CODEX_MIN_VERSION_LABEL = "0.111.0"
CLAUDE_ADAPTER_PATH = "cortex.adapters.claude:ClaudeAdapter"
CLAUDE_ADAPTER_ALIASES = {CLAUDE_ADAPTER_PATH, "cortex.adapters:ClaudeAdapter"}
GEMINI_ADAPTER_PATH = "cortex.adapters.gemini:GeminiAdapter"
GEMINI_ADAPTER_ALIASES = {GEMINI_ADAPTER_PATH, "cortex.adapters:GeminiAdapter"}
OPENAI_ADAPTER_PATH = "cortex.adapters.openai:OpenAIAdapter"
OPENAI_ADAPTER_ALIASES = {OPENAI_ADAPTER_PATH, "cortex.adapters:OpenAIAdapter"}


def runtime_profile_install_spec(
    *,
    root: Path,
    profile: str,
    python_executable: str | None,
) -> tuple[Path, dict[Path, str], str]:
    normalized = str(profile).strip().lower()
    if normalized == "claude":
        runtime_dir = root / CLAUDE_DIRNAME
        return (
            runtime_dir,
            {
                runtime_dir / "settings.json": render_claude_settings_json(
                    python_executable=python_executable,
                    schema_version=CLAUDE_PINNED_HOOK_SCHEMA,
                ),
                runtime_dir / "CLAUDE.md": render_claude_md(),
            },
            CLAUDE_ADAPTER_PATH,
        )
    if normalized == "gemini":
        runtime_dir = root / GEMINI_DIRNAME
        return (
            runtime_dir,
            {
                runtime_dir / "settings.json": render_gemini_settings_json(
                    python_executable=python_executable
                ),
                runtime_dir / "GEMINI.md": render_gemini_md(),
            },
            GEMINI_ADAPTER_PATH,
        )
    if normalized in {"openai", "openai-assisted"}:
        runtime_dir = root / OPENAI_DIRNAME
        runtime_mode = (
            OPENAI_RUNTIME_MODE_ASSISTED if normalized == "openai-assisted" else OPENAI_RUNTIME_MODE_NATIVE
        )
        return (
            runtime_dir,
            {
                runtime_dir / OPENAI_BRIDGE_PROFILE_FILENAME: render_openai_bridge_profile_json(
                    python_executable=python_executable,
                    schema_version=OPENAI_BRIDGE_SCHEMA_VERSION,
                    runtime_mode=runtime_mode,
                ),
                runtime_dir / "OPENAI.md": render_openai_md(),
            },
            OPENAI_ADAPTER_PATH,
        )
    raise ValueError(f"Unsupported runtime profile: {profile}")


def set_runtime_adapter(config_path: Path, adapter_path: str) -> str:
    if not config_path.exists():
        raise OSError(f"Missing config file: {config_path}")
    lines = config_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_runtime = False
    runtime_seen = False
    adapter_written = False
    for line in lines:
        stripped = line.strip()
        section = stripped.startswith("[") and stripped.endswith("]")
        if section:
            if in_runtime and not adapter_written:
                out.append(f'adapter = "{adapter_path}"')
                adapter_written = True
            in_runtime = stripped == "[runtime]"
            runtime_seen = runtime_seen or in_runtime
            out.append(line)
            continue
        if in_runtime and stripped.startswith("adapter"):
            if not adapter_written:
                out.append(f'adapter = "{adapter_path}"')
                adapter_written = True
            continue
        out.append(line)
    if in_runtime and not adapter_written:
        out.append(f'adapter = "{adapter_path}"')
        adapter_written = True
    if not runtime_seen:
        if out and out[-1].strip():
            out.append("")
        out.extend(["[runtime]", f'adapter = "{adapter_path}"'])
    rendered = "\n".join(out).rstrip() + "\n"
    before = config_path.read_text(encoding="utf-8")
    if rendered == before:
        return "unchanged"
    config_path.write_text(rendered, encoding="utf-8")
    return "updated"


def resolve_claude_settings_path(root: Path) -> tuple[Path | None, Path | None]:
    preferred = root / CLAUDE_DIRNAME / "settings.json"
    legacy = root / LEGACY_CLAUDE_DIRNAME / "settings.json"
    if preferred.exists():
        return preferred, legacy
    if legacy.exists():
        return legacy, None
    return None, legacy


def validate_claude_settings(settings_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Failed to read {settings_path}: {exc}"], []

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return [f"Invalid {settings_path}: missing top-level hooks object"], []

    for event_name, command_fragment in CLAUDE_REQUIRED_HOOK_COMMANDS.items():
        errors.extend(
            _validate_claude_hook_event(
                settings_path=settings_path,
                hooks=hooks,
                event_name=event_name,
                command_fragment=command_fragment,
                required=True,
            )
        )
    for event_name, command_fragment in CLAUDE_OPTIONAL_HOOK_COMMANDS.items():
        errors.extend(
            _validate_claude_hook_event(
                settings_path=settings_path,
                hooks=hooks,
                event_name=event_name,
                command_fragment=command_fragment,
                required=False,
            )
        )
    return errors, warnings


def _validate_claude_hook_event(
    *,
    settings_path: Path,
    hooks: dict[str, Any],
    event_name: str,
    command_fragment: str,
    required: bool,
) -> list[str]:
    errors: list[str] = []
    event_entries = hooks.get(event_name)
    if not isinstance(event_entries, list):
        if required:
            errors.append(f"Invalid {settings_path}: missing hooks.{event_name} list")
        return errors
    commands = _event_hook_commands(event_entries)
    if not any(command_fragment in command for command in commands):
        errors.append(
            f"Invalid {settings_path}: hooks.{event_name} does not contain "
            f"command fragment '{command_fragment}'"
        )
        return errors
    matched = [command for command in commands if command_fragment in command]
    schema_versions = {_command_schema_version(command) for command in matched}
    schema_versions.discard(None)
    if not schema_versions:
        errors.append(
            f"Invalid {settings_path}: hooks.{event_name} command must pin --schema-version "
            f"{CLAUDE_PINNED_HOOK_SCHEMA}"
        )
        return errors
    if len(schema_versions) != 1:
        errors.append(
            f"Invalid {settings_path}: hooks.{event_name} has mixed schema versions: "
            + ", ".join(sorted(str(item) for item in schema_versions))
        )
        return errors
    schema_version = next(iter(schema_versions))
    if schema_version not in CLAUDE_SUPPORTED_HOOK_SCHEMAS:
        errors.append(
            f"Invalid {settings_path}: hooks.{event_name} schema version '{schema_version}' "
            f"is unsupported (supported: {', '.join(sorted(CLAUDE_SUPPORTED_HOOK_SCHEMAS))})"
        )
        return errors
    if schema_version != CLAUDE_PINNED_HOOK_SCHEMA:
        errors.append(
            f"Invalid {settings_path}: hooks.{event_name} schema version '{schema_version}' "
            f"does not match pinned runtime schema '{CLAUDE_PINNED_HOOK_SCHEMA}'"
        )
    return errors


def resolve_gemini_settings_path(root: Path) -> Path | None:
    path = root / GEMINI_DIRNAME / "settings.json"
    return path if path.exists() else None


def validate_gemini_settings(settings_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Failed to read {settings_path}: {exc}"], []

    hooks_config = data.get("hooksConfig")
    if isinstance(hooks_config, dict) and hooks_config.get("enabled") is False:
        errors.append(
            "Gemini hooks are globally disabled. "
            "Cortex cannot enforce without hooks. Set hooksConfig.enabled to true or remove the field (defaults to true).",
        )

    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        errors.append(f"Invalid {settings_path}: missing top-level hooks object")
        return errors, warnings

    after_agent_entries = hooks.get("AfterAgent")
    if not isinstance(after_agent_entries, list) or not after_agent_entries:
        errors.append("No AfterAgent hook configured. Cortex stop path cannot fire without this hook.")
    after_agent_configs = _flatten_hook_configs(
        after_agent_entries if isinstance(after_agent_entries, list) else []
    )
    if isinstance(after_agent_entries, list) and after_agent_entries and not after_agent_configs:
        errors.append("No AfterAgent hook configured. Cortex stop path cannot fire without this hook.")
    if after_agent_configs and not all(_is_command_hook(config) for config in after_agent_configs):
        errors.append(
            "AfterAgent hook configuration is invalid. Each hook config requires type: 'command' and a command string."
        )
    after_agent_commands = [
        str(config.get("command") or "").strip()
        for config in after_agent_configs
        if str(config.get("command") or "").strip()
    ]
    if after_agent_commands and not any(
        GEMINI_AFTER_AGENT_BRIDGE_PATTERN in command for command in after_agent_commands
    ):
        warnings.append(
            "AfterAgent hook command does not appear to be a Cortex hook bridge. "
            "Stop path enforcement may not work. Expected command containing "
            f"'{GEMINI_AFTER_AGENT_BRIDGE_PATTERN}'."
        )

    before_tool_entries = hooks.get("BeforeTool")
    if not isinstance(before_tool_entries, list) or not before_tool_entries:
        warnings.append("No BeforeTool hook. Tool blocklist enforcement will not run.")
    elif not _flatten_hook_configs(before_tool_entries):
        warnings.append("No BeforeTool hook. Tool blocklist enforcement will not run.")

    after_tool_entries = hooks.get("AfterTool")
    if not isinstance(after_tool_entries, list) or not after_tool_entries:
        warnings.append("No AfterTool hook. Post-tool failure detection will not run.")
    elif not _flatten_hook_configs(after_tool_entries):
        warnings.append("No AfterTool hook. Post-tool failure detection will not run.")

    before_agent_entries = hooks.get("BeforeAgent")
    if not isinstance(before_agent_entries, list) or not before_agent_entries:
        warnings.append("No BeforeAgent hook. Per-turn persistent executive anchor injection will not run.")
    elif not _flatten_hook_configs(before_agent_entries):
        warnings.append("No BeforeAgent hook. Per-turn persistent executive anchor injection will not run.")

    project_root = settings_path.parent.parent
    for command in _hook_commands(hooks):
        if _command_references_missing_path(command, project_root):
            warnings.append(
                f"Hook command may reference a missing path: {command}. Hooks may fail at runtime."
            )
    return errors, warnings


def resolve_openai_bridge_profile_path(root: Path) -> Path | None:
    path = root / OPENAI_DIRNAME / OPENAI_BRIDGE_PROFILE_FILENAME
    return path if path.exists() else None


def resolve_openai_bridge_mode(profile_path: Path) -> str | None:
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return _openai_bridge_mode(data)


def validate_openai_bridge_profile(
    profile_path: Path,
    *,
    which: Callable[[str], str | None] = shutil.which,
    run_exec: Callable[..., Any] = subprocess.run,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Failed to read {profile_path}: {exc}"], []

    if not isinstance(data, dict):
        return [f"Invalid {profile_path}: expected JSON object"], []

    schema_version = str(data.get("schema_version") or "").strip()
    if schema_version != OPENAI_BRIDGE_SCHEMA_VERSION:
        errors.append(
            f"Invalid {profile_path}: schema_version must be '{OPENAI_BRIDGE_SCHEMA_VERSION}'."
        )

    bridge = data.get("bridge")
    if not isinstance(bridge, dict):
        errors.append(f"Invalid {profile_path}: missing bridge object.")
        return errors, warnings

    command = str(bridge.get("command") or "").strip()
    if not command:
        errors.append(f"Invalid {profile_path}: bridge.command is required.")
        return errors, warnings
    runtime_mode = _openai_bridge_mode(data)
    command_subcommand = _openai_bridge_subcommand(command)
    if runtime_mode not in OPENAI_RUNTIME_MODES:
        errors.append(
            f"Invalid {profile_path}: mode must be one of {', '.join(sorted(OPENAI_RUNTIME_MODES))}."
        )
    elif runtime_mode == OPENAI_RUNTIME_MODE_ASSISTED:
        if command_subcommand != "run-assisted":
            errors.append(
                f"Invalid {profile_path}: assisted bridge.command must contain '{OPENAI_ASSISTED_BRIDGE_COMMAND_PATTERN}'."
            )
    elif command_subcommand != "run":
        errors.append(
            f"Invalid {profile_path}: bridge.command must contain '{OPENAI_BRIDGE_COMMAND_PATTERN}'."
        )
    command_schema = _command_schema_version(command)
    if command_schema != OPENAI_BRIDGE_SCHEMA_VERSION:
        errors.append(
            f"Invalid {profile_path}: bridge.command must pin --schema-version {OPENAI_BRIDGE_SCHEMA_VERSION}."
        )
    if runtime_mode == OPENAI_RUNTIME_MODE_ASSISTED and "required_requirement_ids" in data:
        raw_required_ids = data.get("required_requirement_ids")
        if not isinstance(raw_required_ids, list) or any(
            not isinstance(item, str) or not item.strip() for item in raw_required_ids
        ):
            errors.append(
                f"Invalid {profile_path}: required_requirement_ids must be a JSON array of non-empty strings."
            )

    codex_bin = str(bridge.get("codex_bin") or "").strip()
    if not codex_bin:
        warnings.append(
            f"{profile_path}: bridge.codex_bin is empty; runtime will fallback to 'codex' on PATH."
        )
        return errors, warnings

    resolved = which(codex_bin)
    if resolved is None:
        errors.append(f"{profile_path}: bridge.codex_bin '{codex_bin}' is not on PATH.")
        return errors, warnings

    try:
        version_run = run_exec(
            [codex_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"{profile_path}: failed to run '{codex_bin} --version': {exc}")
        return errors, warnings

    version_text = f"{version_run.stdout}\n{version_run.stderr}"
    version_tuple = _parse_semver_tuple(version_text)
    if version_tuple is None:
        warnings.append(
            f"{profile_path}: unable to parse Codex version from '{codex_bin} --version' output."
        )
        return errors, warnings
    if version_tuple < OPENAI_CODEX_MIN_VERSION:
        warnings.append(
            f"{profile_path}: Codex version {version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]} is below tested baseline {OPENAI_CODEX_MIN_VERSION_LABEL}."
        )
    return errors, warnings


def _parse_semver_tuple(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", str(text))
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def _openai_bridge_mode(data: dict[str, Any]) -> str | None:
    configured = str(data.get("mode") or "").strip().lower()
    if configured in OPENAI_RUNTIME_MODES:
        return configured
    bridge = data.get("bridge")
    if not isinstance(bridge, dict):
        return None
    command = str(bridge.get("command") or "").strip()
    subcommand = _openai_bridge_subcommand(command)
    if subcommand == "run-assisted":
        return OPENAI_RUNTIME_MODE_ASSISTED
    if subcommand == "run":
        return OPENAI_RUNTIME_MODE_NATIVE
    return None


def _openai_bridge_subcommand(command: str) -> str | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = str(command).split()
    for idx, token in enumerate(tokens):
        if token != "-m":
            continue
        if idx + 1 >= len(tokens) or tokens[idx + 1] != "cortex_ops_cli.openai_app_server_bridge":
            continue
        if idx + 2 < len(tokens):
            return tokens[idx + 2]
        return None
    return None


def _flatten_hook_configs(event_entries: list[Any]) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []
    for entry in event_entries:
        if not isinstance(entry, dict):
            continue
        hook_items = entry.get("hooks")
        if not isinstance(hook_items, list):
            continue
        for config in hook_items:
            if isinstance(config, dict):
                configs.append(config)
    return configs


def _is_command_hook(config: dict[str, Any]) -> bool:
    return (
        str(config.get("type") or "").strip() == "command"
        and bool(str(config.get("command") or "").strip())
    )


def _hook_commands(hooks: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for event_name in [*GEMINI_REQUIRED_HOOK_COMMANDS, *GEMINI_OPTIONAL_HOOK_COMMANDS]:
        event_entries = hooks.get(event_name)
        if not isinstance(event_entries, list):
            continue
        for config in _flatten_hook_configs(event_entries):
            command = str(config.get("command") or "").strip()
            if command:
                commands.append(command)
    return commands


def _command_references_missing_path(command: str, root: Path) -> bool:
    tokens = str(command).split()
    for token in tokens:
        candidate = token.strip().strip("'\"")
        if not candidate or "/" not in candidate:
            continue
        if candidate.startswith("-"):
            continue
        path = Path(candidate)
        if path.is_absolute():
            if path.exists():
                continue
            return True
        if (root / path).exists() or path.exists():
            continue
        return True
    return False


def _event_hook_commands(event_entries: list[Any]) -> list[str]:
    commands: list[str] = []
    for config in _flatten_hook_configs(event_entries):
        command = str(config.get("command") or "").strip()
        if command:
            commands.append(command)
    return commands


def _command_schema_version(command: str) -> str | None:
    parts = shlex.split(command)
    for idx, token in enumerate(parts):
        if token == "--schema-version" and idx + 1 < len(parts):
            return str(parts[idx + 1]).strip() or None
        if token.startswith("--schema-version="):
            return token.split("=", 1)[1].strip() or None
    return None
```

### `cortex_ops_cli/_runtime_profile_templates.py`

```python
from __future__ import annotations

import shlex
from pathlib import Path


def render_claude_settings_json(*, python_executable: str | None, schema_version: str) -> str:
    text = _load_repo_template(
        "claude/settings.json",
        f"""{{
  "hooks": {{
    "InstructionsLoaded": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.instructions_loaded --schema-version {schema_version}"
          }}
        ]
      }}
    ],
    "SessionStart": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.session_start --schema-version {schema_version}"
          }}
        ]
      }}
    ],
    "PreToolUse": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.pre_tool_use --schema-version {schema_version}"
          }}
        ]
      }}
    ],
    "PostToolUse": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.post_tool_use --schema-version {schema_version}"
          }}
        ]
      }}
    ],
    "PostToolUseFailure": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.post_tool_use_failure --schema-version {schema_version}"
          }}
        ]
      }}
    ],
    "Stop": [
      {{
        "hooks": [
          {{
            "type": "command",
            "command": "python3 -m cortex.hooks.stop --schema-version {schema_version}"
          }}
        ]
      }}
    ]
  }}
}}
""",
    )
    if not python_executable:
        return text
    exe = shlex.quote(str(Path(python_executable)))
    return text.replace("python3 -m cortex.hooks.", f"{exe} -m cortex.hooks.")


def render_gemini_settings_json(*, python_executable: str | None) -> str:
    text = _load_repo_template(
        "gemini/settings.json",
        """{
  "hooksConfig": {
    "enabled": true
  },
  "model": {
    "maxSessionTurns": 50,
    "compressionThreshold": 0.35
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m cortex_ops_cli.gemini_hooks SessionStart",
            "name": "cortex-session-start",
            "timeout": 30000
          }
        ]
      }
    ],
    "BeforeTool": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m cortex_ops_cli.gemini_hooks BeforeTool",
            "name": "cortex-before-tool",
            "timeout": 30000
          }
        ]
      }
    ],
    "AfterTool": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m cortex_ops_cli.gemini_hooks AfterTool",
            "name": "cortex-after-tool",
            "timeout": 30000
          }
        ]
      }
    ],
    "BeforeAgent": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m cortex_ops_cli.gemini_hooks BeforeAgent",
            "name": "cortex-before-agent",
            "timeout": 30000
          }
        ]
      }
    ],
    "AfterAgent": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -m cortex_ops_cli.gemini_hooks AfterAgent",
            "name": "cortex-after-agent",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
""",
    )
    if not python_executable:
        return text
    exe = shlex.quote(str(Path(python_executable)))
    return text.replace("python3 -m cortex_ops_cli.gemini_hooks", f"{exe} -m cortex_ops_cli.gemini_hooks")


def render_claude_md() -> str:
    return _load_repo_template(
        "claude/CLAUDE.md",
        """# Cortex Runtime Instructions (Claude Code)

## Purpose

Cortex is enforcing completion-time quality gates on this project through Claude Code hooks.
This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile claude`

- `.claude/settings.json`
- `.claude/CLAUDE.md`

## What Cortex Gives You Before `Stop`

- Claude `SessionStart` now front-loads one short kernel-owned completion preview.
- If Claude emits `InstructionsLoaded`, Cortex records it in session events for observability only. That hook is fail-open and does not change stop or tool semantics.
- `PostToolUseFailure` can add narrow kernel-owned recovery context after a failed tool call without moving stop meaning out of Cortex.
- If `Stop` blocks completion on a repairable gap, Claude may also receive a short kernel-derived repair focus through the same kernel-owned stop result.
- Use the early surfaces when you are heading toward completion: start gathering truthful `challenge_coverage` and `truth_claims` evidence, and prepare `requirement_audit` only when traceability is configured for the session.
- The goal is to make the finish line clearer before `Stop`, not to add a repeated checklist. `Stop` remains the hard truthful boundary if completion evidence is missing or malformed.

## Enforcement Expectations

- Treat hook output as policy, not optional advice.
- Keep changes small and load-bearing.
- Claude Stop hooks deliver completion evidence through `last_assistant_message`. End completion claims with one-line `STOP_FIELDS_JSON` so the Claude adapter can normalize it into `payload.stop_fields` before strict evaluation.

Cortex expects challenge coverage at stop:
- `null_inputs`
- `boundary_values`
- `error_handling`
- `graveyard_regression`

When a category is covered in strict mode, use an object with evidence, not a bare boolean:

`"boundary_values":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]}`

If a category is not honestly evidenced yet, keep working. Do not claim completion
with `covered: true` and an empty evidence list.

In strict mode, invariant failure should be treated as a revert signal.

If an approach failed, include `failed_approach` with:
- `summary`
- `reason`
- `files`

If requirement traceability is configured, include `requirement_audit` and all required IDs.
For pass items, use exact `status: "pass"` and include `evidence`. Do not use
`status: "satisfied"` or note-only summaries for passing requirements.

When claiming completion facts, include `truth_claims`:
- `modified_files`: files you actually changed
- `tests_ran`: test commands you actually ran

If you need a small additional test edit to make challenge coverage truthful, make
that edit and list every changed file in `truth_claims.modified_files`.

Stop trailer format:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/app.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_app.py"]}},"truth_claims":{"modified_files":["src/app.py","tests/test_app.py"],"tests_ran":["python3 -m pytest -q tests/test_app.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/app.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python3 -m pytest -q tests/test_app.py"]}],"completeness_verdict":"pass"},"failed_approach":{"summary":"...","reason":"...","files":["path/to/file"]}}`

Use valid one-line JSON and keep the field names exact.

## Adapter Contract

- Adapter path in `cortex.toml`: `cortex.adapters.claude:ClaudeAdapter`
- Required hook commands: `SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`
- Optional telemetry hook commands: `InstructionsLoaded`
- Runtime hook schema is pinned in `.claude/settings.json` (`claude_native_v1`, rollback `legacy_json_v0`)

## Known Caveats

- Status: `Shipped`. Claude is the strongest current runtime, the truthful boundary is live-proven, and the remaining caveat is minor.
- If a host regression suppresses startup context on an older Claude Code build, rely on the installed tool hooks plus `Stop`, and run `cortex repomap --root .` explicitly when needed.
- `InstructionsLoaded` is telemetry only. It records the raw host payload in session events when a session id is present and otherwise fails open with `{}`.
- Permission mediation beyond `PreToolUse` is not part of the shipped Claude profile.
- The current official Claude hook surface is broader than the shipped profile. `PreCompact` remains probe-only; notification, worktree, session-end, setup, and similar lifecycle hooks stay docs-only; prompt, elicitation, and multi-agent hooks stay unshipped unless they earn a narrow kernel-preserving gain.
- Full runtime status and evidence stay in the main Cortex adapter reference and adapter validation ledger.
- Each hook module also accepts `--root` and `--config` for manual testing.
""",
    )


def render_gemini_md() -> str:
    return _load_repo_template(
        "gemini/GEMINI.md",
        """# Cortex Runtime Instructions (Gemini CLI)

## Purpose

Cortex is enforcing completion-time quality gates on this project through Gemini CLI hooks.
This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile gemini`

- `.gemini/settings.json`
- `.gemini/GEMINI.md`

## What Cortex Gives You At `SessionStart`

- Gemini `SessionStart` front-loads one short kernel-owned completion preview before the heavier Cortex session context.
- That preview is there to make the finish line clearer before the first failed stop, not to add a repeated checklist.
- On non-low-friction native sessions, that preview now also reminds you what evidence counts: repo-relative refs or `cmd:` markers; pytest node ids and prose do not count.
- On `localized_edit/standard` and `localized_edit/strict`, the same preview also adds one short boundedness reminder: `Do not broaden scope beyond declared task targets.`
- It appears once only. On higher-friction Gemini turns, the per-turn `BeforeAgent` hook still handles Part B executive anchoring separately; low-friction route state suppresses that recurring anchor and does not repeat the preview.

## Enforcement Expectations

When producing final responses (`AfterAgent`), include Cortex stop markers
directly in the final response body using one-line `STOP_FIELDS_JSON:` with
valid JSON. Do not emit the marker through a shell command or by writing it to
another file.

In strict mode, each `challenge_coverage` category must be an object with
`covered: true` and a non-empty `evidence` list. Bare booleans are not enough.
For passing `requirement_audit.items`, use exact `status: "pass"` or
`status: "fail"` and include `evidence` for every pass item.

Example:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/module.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_normalize_port.py"]}},"truth_claims":{"tests_ran":["python -m pytest -q tests/test_normalize_port.py"],"modified_files":["src/module.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/module.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]}],"completeness_verdict":"pass"}}`

If markers are omitted or malformed, Cortex will treat the completion claim as incomplete and return correction feedback.

## Adapter And Bridge Contract

- Hook bridge entrypoint: `python3 -m cortex_ops_cli.gemini_hooks <HookEvent>`
- Required hook events: `SessionStart`, `BeforeTool`, `AfterTool`, `BeforeAgent`, `AfterAgent`
- Adapter path in `cortex.toml`: `cortex.adapters.gemini:GeminiAdapter`

## Known Caveats And Status

- Status: `Shipped with watchlist`. Gemini is a live-proven runtime surface and preserves the truthful boundary.
- The remaining watchlist is operational: after a blocked malformed stop, Gemini CLI can stay resident until the operator terminates it, even though Cortex has already closed the session truthfully.
- Current product-proof evidence is still mixed rather than cleanly progressive: the March 16 current shared-harness native row is now route-valid for `localized_edit/strict`, but it still ended `failed_invariants`, so the repo keeps the product claim withheld.
- Non-blocking Cortex warnings are surfaced back to Gemini as `systemMessage` text.
- Blocking outcomes return hook `decision=deny` with a reason.
- Recurring executive anchor delivery, when active, is handled by the `BeforeAgent` hook (`hookSpecificOutput.additionalContext`). Low-friction Gemini route state suppresses that recurring Part B anchor.
- Full runtime status and watchlist evidence stay in the main Cortex adapter reference and adapter validation ledger.
""",
    )


def render_openai_bridge_profile_json(
    *,
    python_executable: str | None,
    schema_version: str,
    runtime_mode: str,
) -> str:
    template_path = (
        "openai/cortex_openai_assisted_bridge.json"
        if runtime_mode == "assisted"
        else "openai/cortex_openai_bridge.json"
    )
    subcommand = "run-assisted" if runtime_mode == "assisted" else "run"
    required_ids_line = '  "required_requirement_ids": [],\n' if runtime_mode == "assisted" else ""
    text = _load_repo_template(
        template_path,
        f"""{{
  "mode": "{runtime_mode}",
  "schema_version": "{schema_version}",
{required_ids_line}  "bridge": {{
    "command": "python3 -m cortex_ops_cli.openai_app_server_bridge {subcommand} --schema-version {schema_version}",
    "codex_bin": "codex",
    "listen": "stdio://"
  }}
}}
""",
    )
    if not python_executable:
        return text
    exe = shlex.quote(str(Path(python_executable)))
    return text.replace(
        "python3 -m cortex_ops_cli.openai_app_server_bridge",
        f"{exe} -m cortex_ops_cli.openai_app_server_bridge",
    )


def render_openai_md() -> str:
    return _load_repo_template(
        "openai/OPENAI.md",
        """# Cortex Runtime Instructions (OpenAI/Codex App Server)

## Purpose

Cortex uses the OpenAI App Server bridge in two explicit modes:

- native mode (`cortex runtime install --profile openai`)
- assisted mode (`cortex runtime install --profile openai-assisted`)

This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile openai` or `openai-assisted`

- `.codex/cortex_openai_bridge.json`
- `.codex/OPENAI.md`

## Enforcement Expectations

When producing final responses through Codex App Server, include Cortex stop
markers directly in the final response body using the exact one-line literal
prefix `STOP_FIELDS_JSON:` followed by valid JSON. Do not emit the marker
through a shell command or by writing it to another file.

In strict mode, each `challenge_coverage` category must be an object with
`covered: true` and a non-empty `evidence` list. Bare booleans are not enough.
Use repo-verifiable evidence tokens such as repo-relative file paths with line
references (`src/module.py:8`, `tests/test_module.py:12`) or executed-command
markers (`cmd:python -m pytest -q tests/test_normalize_port.py`). Do not use pytest node ids,
narrative summaries, or other evidence strings the kernel cannot verify from
the workspace.
For every `requirement_audit.items` entry, use exact `status: "pass"` or
`status: "fail"`. Do not use custom statuses such as `blocked` or `not_done`.
Include `evidence` for every pass item, and for any fail item used to justify a
truthful incomplete outcome.

If completion cannot be claimed honestly, still end with one-line
`STOP_FIELDS_JSON` carrying a structured truthful failure such as
`stuck_declaration`, `failed_approach`, real `truth_claims` gaps, or real
`requirement_audit` gaps. Do not rely on prose-only refusal text.

Example:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/module.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_normalize_port.py"]}},"truth_claims":{"tests_ran":["python -m pytest -q tests/test_normalize_port.py"],"modified_files":["src/module.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/module.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]}],"completeness_verdict":"pass"}}`

## Enforcement-Ready Mode

- `cortex init` starts with advisory hooks because that is the safe starter state.
- A user who wants blocking enforcement can opt in through the shipped `cortex.toml` hooks surface after `cortex runtime install --profile openai`:

```toml
[hooks]
mode = "strict"
fail_on_missing_challenge_coverage = true
require_requirement_audit = true
fail_on_requirement_audit_gap = true
require_structured_stop_payload = true
allow_message_stop_fallback = false
```

## Adapter And Bridge Contract

- Native bridge entrypoint: `python3 -m cortex_ops_cli.openai_app_server_bridge run`
- Assisted bridge entrypoint: `python3 -m cortex_ops_cli.openai_app_server_bridge run-assisted`
- Schema pin: `--schema-version openai_app_server_v1`
- Profile file: `.codex/cortex_openai_bridge.json`
- Adapter path in `cortex.toml`: `cortex.adapters.openai:OpenAIAdapter`

## Assisted Mode Contract

- Assisted mode is explicit and bounded. It is not hidden inside native mode.
- Cortex starts assisted mode with the runtime banner, then the user task, then one short kernel-owned completion preview plus one short kernel-owned evidence expectation before the longer session context. Those start-of-run surfaces only state run-relevant completion and evidence conditions for this surface.
- The shipped assisted profile may carry explicit requirement-contract ids in `.codex/cortex_openai_bridge.json` under `required_requirement_ids`; Cortex will surface that full id set through the existing start-of-run `requirement_audit` contract instead of inferring ids from prompt prose.
- Direct/integrating callers may also pass repeated `--required-requirement-id <ID>` values to `run-assisted`; explicit CLI ids override the profile value for that run.
- Assisted mode may run one corrective turn when the first stop fails with kernel-owned `stop_stage = repair` or `reorient`.
- That corrective turn is derived from kernel-owned stop outputs, especially the unresolved-gap signature and structured-stop failures. It is meant to repair the real gap, not to scold generically or invent a planner loop.
- After that bounded pass, the run ends cleanly as accepted completion, truthful stuck, bounded halt for unchanged-gap false progress or terminal kernel halt, or bounded incomplete when the gap materially moved but still does not support completion.
- Assisted mode does not add tool micromanagement beyond the native App Server surface.

## Known Caveats And Status

- Status: `Experimental` on latest-stable local `codex-cli 0.111.0` as last validated 2026-03-09. Several critical paths are proven on the current App Server surface, including install/check wiring, truthful malformed-stop rejection, truthful `truth_gap` failure, and approval-blocking.
- Assisted mode is the first explicit product-development step beyond native OpenAI. It is bounded and honest, and it now also has one current committed shared-harness pair under `tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json`, but it is still supplemental-only and not a launch-proof replacement for the native validation ledger.
- `probe-model` and `probe-approval-blocking` are both live-proven. The mutating-workspace probe observed a real blocked decline; the network-sensitive and destructive-git probes still reported `pre_tool_use_approval_not_observed` as limitation gaps rather than hard failures.
- The remaining blocker is the positive strict close. That question is now split explicitly on the 2026-03-09 evidence base: a fresh native `probe_terminality` rerun reached terminal bridge JSON, a usable session id, and a Stop event, so terminality is separately proven on the tested stable surface. The shared `pass_minimal` lane was then rerun on a fresh project copy; that rerun fixed the bug and passed the target test, but strict close still failed at the challenge gate because `challenge_coverage` used invalid status-shaped objects and pytest node-id evidence instead of repo-verifiable challenge evidence.
- The March 15 critique audit remains preserved as a dated contradiction: latest-local native spotchecks were mixed, and the latest-local assisted spotcheck from that audit stalled after `SessionStart` instead of reaching the corrective path.
- The March 16 current Phase 9 packet adds newer assisted truth without erasing that older contradiction: the current assisted shared-harness pair is row-capturable, startup preview and evidence expectation were present, one bounded corrective pass occurred, and the assisted Cortex row still ended `failed_challenges` / `bounded_incomplete` with a remaining repair target. That is current bounded evidence, not native substitution.
- If command approval decline cannot be proven to block execution, the bridge must report `pre_tool_use_nonblocking_approval`.
- Runs with unresolved coverage gaps are diagnostic only and should not be treated as product evidence.
- Full runtime status and evidence stay in the main Cortex adapter reference and adapter validation ledger.
- OpenAI remains an experimental runtime surface until the positive strict close is proven stable on the tested stable release.
""",
    )


def _load_repo_template(rel_path: str, fallback: str) -> str:
    repo_template = Path(__file__).resolve().parents[1] / rel_path
    if repo_template.exists():
        return repo_template.read_text(encoding="utf-8")
    return fallback
```

### `claude/CLAUDE.md`

```md
# Cortex Runtime Instructions (Claude Code)

## Purpose

Cortex is enforcing completion-time quality gates on this project through Claude Code hooks.
This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile claude`

- `.claude/settings.json`
- `.claude/CLAUDE.md`

## What Cortex Gives You Before `Stop`

- Claude `SessionStart` now front-loads one short kernel-owned completion preview.
- If Claude emits `InstructionsLoaded`, Cortex records it in session events for observability only. That hook is fail-open and does not change stop or tool semantics.
- `PostToolUseFailure` can add narrow kernel-owned recovery context after a failed tool call without moving stop meaning out of Cortex.
- If `Stop` blocks completion on a repairable gap, Claude may also receive a short kernel-derived repair focus through the same kernel-owned stop result.
- Use the early surfaces when you are heading toward completion: start gathering truthful `challenge_coverage` and `truth_claims` evidence, and prepare `requirement_audit` only when traceability is configured for the session.
- The goal is to make the finish line clearer before `Stop`, not to add a repeated checklist. `Stop` remains the hard truthful boundary if completion evidence is missing or malformed.

## Enforcement Expectations

- Treat hook output as policy, not optional advice.
- Keep changes small and load-bearing.
- Claude Stop hooks deliver completion evidence through `last_assistant_message`. End completion claims with one-line `STOP_FIELDS_JSON` so the Claude adapter can normalize it into `payload.stop_fields` before strict evaluation.

Cortex expects challenge coverage at stop:
- `null_inputs`
- `boundary_values`
- `error_handling`
- `graveyard_regression`

When a category is covered in strict mode, use an object with evidence, not a bare boolean:

`"boundary_values":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]}`

If a category is not honestly evidenced yet, keep working. Do not claim completion
with `covered: true` and an empty evidence list.

In strict mode, invariant failure should be treated as a revert signal.

If an approach failed, include `failed_approach` with:
- `summary`
- `reason`
- `files`

If requirement traceability is configured, include `requirement_audit` and all required IDs.
For pass items, use exact `status: "pass"` and include `evidence`. Do not use
`status: "satisfied"` or note-only summaries for passing requirements.

When claiming completion facts, include `truth_claims`:
- `modified_files`: files you actually changed
- `tests_ran`: test commands you actually ran

If you need a small additional test edit to make challenge coverage truthful, make
that edit and list every changed file in `truth_claims.modified_files`.

Stop trailer format:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/app.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python3 -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_app.py"]}},"truth_claims":{"modified_files":["src/app.py","tests/test_app.py"],"tests_ran":["python3 -m pytest -q tests/test_app.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/app.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python3 -m pytest -q tests/test_app.py"]}],"completeness_verdict":"pass"},"failed_approach":{"summary":"...","reason":"...","files":["path/to/file"]}}`

Use valid one-line JSON and keep the field names exact.

## Adapter Contract

- Adapter path in `cortex.toml`: `cortex.adapters.claude:ClaudeAdapter`
- Required hook commands: `SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`
- Optional telemetry hook commands: `InstructionsLoaded`
- Runtime hook schema is pinned in `.claude/settings.json` (`claude_native_v1`, rollback `legacy_json_v0`)

## Known Caveats

- Status: `Shipped`. Claude is the strongest current runtime, the truthful boundary is live-proven, and the remaining caveat is minor.
- If a host regression suppresses startup context on an older Claude Code build, rely on the installed tool hooks plus `Stop`, and run `cortex repomap --root .` explicitly when needed.
- `InstructionsLoaded` is telemetry only. It records the raw host payload in session events when a session id is present and otherwise fails open with `{}`.
- Permission mediation beyond `PreToolUse` is not part of the shipped Claude profile.
- The current official Claude hook surface is broader than the shipped profile. `PreCompact` remains probe-only; notification, worktree, session-end, setup, and similar lifecycle hooks stay docs-only; prompt, elicitation, and multi-agent hooks stay unshipped unless they earn a narrow kernel-preserving gain.
- Full runtime status and evidence stay in the main Cortex adapter reference and adapter validation ledger.
- Each hook module also accepts `--root` and `--config` for manual testing.
```

### `gemini/GEMINI.md`

```md
# Cortex Runtime Instructions (Gemini CLI)

## Purpose

Cortex is enforcing completion-time quality gates on this project through Gemini CLI hooks.
This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile gemini`

- `.gemini/settings.json`
- `.gemini/GEMINI.md`

## What Cortex Gives You At `SessionStart`

- Gemini `SessionStart` front-loads one short kernel-owned completion preview before the heavier Cortex session context.
- That preview is there to make the finish line clearer before the first failed stop, not to add a repeated checklist.
- On non-low-friction native sessions, that preview now also reminds you what evidence counts: repo-relative refs or `cmd:` markers; pytest node ids and prose do not count.
- On `localized_edit/standard` and `localized_edit/strict`, the same preview also adds one short boundedness reminder: `Do not broaden scope beyond declared task targets.`
- It appears once only. On higher-friction Gemini turns, the per-turn `BeforeAgent` hook still handles Part B executive anchoring separately; low-friction route state suppresses that recurring anchor and does not repeat the preview.

## Enforcement Expectations

When producing final responses (`AfterAgent`), include Cortex stop markers
directly in the final response body using one-line `STOP_FIELDS_JSON:` with
valid JSON. Do not emit the marker through a shell command or by writing it to
another file.

In strict mode, each `challenge_coverage` category must be an object with
`covered: true` and a non-empty `evidence` list. Bare booleans are not enough.
For passing `requirement_audit.items`, use exact `status: "pass"` or
`status: "fail"` and include `evidence` for every pass item.

Example:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/module.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_normalize_port.py"]}},"truth_claims":{"tests_ran":["python -m pytest -q tests/test_normalize_port.py"],"modified_files":["src/module.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/module.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]}],"completeness_verdict":"pass"}}`

If markers are omitted or malformed, Cortex will treat the completion claim as incomplete and return correction feedback.

## Adapter And Bridge Contract

- Hook bridge entrypoint: `python3 -m cortex_ops_cli.gemini_hooks <HookEvent>`
- Required hook events: `SessionStart`, `BeforeTool`, `AfterTool`, `BeforeAgent`, `AfterAgent`
- Adapter path in `cortex.toml`: `cortex.adapters.gemini:GeminiAdapter`

## Known Caveats And Status

- Status: `Shipped with watchlist`. Gemini is a live-proven runtime surface and preserves the truthful boundary.
- The remaining watchlist is operational: after a blocked malformed stop, Gemini CLI can stay resident until the operator terminates it, even though Cortex has already closed the session truthfully.
- Current product-proof evidence is still mixed rather than cleanly progressive: the March 16 current shared-harness native row is now route-valid for `localized_edit/strict`, but it still ended `failed_invariants`, so the repo keeps the product claim withheld.
- Non-blocking Cortex warnings are surfaced back to Gemini as `systemMessage` text.
- Blocking outcomes return hook `decision=deny` with a reason.
- Recurring executive anchor delivery, when active, is handled by the `BeforeAgent` hook (`hookSpecificOutput.additionalContext`). Low-friction Gemini route state suppresses that recurring Part B anchor.
- Full runtime status and watchlist evidence stay in the main Cortex adapter reference and adapter validation ledger.
```

### `openai/OPENAI.md`

```md
# Cortex Runtime Instructions (OpenAI/Codex App Server)

## Purpose

Cortex uses the OpenAI App Server bridge in two explicit modes:

- native mode (`cortex runtime install --profile openai`)
- assisted mode (`cortex runtime install --profile openai-assisted`)

This shipped profile doc is frozen as part of the final v1 archive point.

## Files Written by `cortex runtime install --profile openai` or `openai-assisted`

- `.codex/cortex_openai_bridge.json`
- `.codex/OPENAI.md`

## Enforcement Expectations

When producing final responses through Codex App Server, include Cortex stop
markers directly in the final response body using the exact one-line literal
prefix `STOP_FIELDS_JSON:` followed by valid JSON. Do not emit the marker
through a shell command or by writing it to another file.

In strict mode, each `challenge_coverage` category must be an object with
`covered: true` and a non-empty `evidence` list. Bare booleans are not enough.
Use repo-verifiable evidence tokens such as repo-relative file paths with line
references (`src/module.py:8`, `tests/test_module.py:12`) or executed-command
markers (`cmd:python -m pytest -q tests/test_normalize_port.py`). Do not use pytest node ids,
narrative summaries, or other evidence strings the kernel cannot verify from
the workspace.
For every `requirement_audit.items` entry, use exact `status: "pass"` or
`status: "fail"`. Do not use custom statuses such as `blocked` or `not_done`.
Include `evidence` for every pass item, and for any fail item used to justify a
truthful incomplete outcome.

If completion cannot be claimed honestly, still end with one-line
`STOP_FIELDS_JSON` carrying a structured truthful failure such as
`stuck_declaration`, `failed_approach`, real `truth_claims` gaps, or real
`requirement_audit` gaps. Do not rely on prose-only refusal text.

Example:

`STOP_FIELDS_JSON: {"challenge_coverage":{"null_inputs":{"covered":true,"evidence":["src/module.py"]},"boundary_values":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"error_handling":{"covered":true,"evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]},"graveyard_regression":{"covered":true,"evidence":["tests/test_normalize_port.py"]}},"truth_claims":{"tests_ran":["python -m pytest -q tests/test_normalize_port.py"],"modified_files":["src/module.py"]},"requirement_audit":{"items":[{"id":"BUGFIX","status":"pass","evidence":["src/module.py"]},{"id":"TEST","status":"pass","evidence":["cmd:python -m pytest -q tests/test_normalize_port.py"]}],"completeness_verdict":"pass"}}`

## Enforcement-Ready Mode

- `cortex init` starts with advisory hooks because that is the safe starter state.
- A user who wants blocking enforcement can opt in through the shipped `cortex.toml` hooks surface after `cortex runtime install --profile openai`:

```toml
[hooks]
mode = "strict"
fail_on_missing_challenge_coverage = true
require_requirement_audit = true
fail_on_requirement_audit_gap = true
require_structured_stop_payload = true
allow_message_stop_fallback = false
```

## Adapter And Bridge Contract

- Native bridge entrypoint: `python3 -m cortex_ops_cli.openai_app_server_bridge run`
- Assisted bridge entrypoint: `python3 -m cortex_ops_cli.openai_app_server_bridge run-assisted`
- Schema pin: `--schema-version openai_app_server_v1`
- Profile file: `.codex/cortex_openai_bridge.json`
- Adapter path in `cortex.toml`: `cortex.adapters.openai:OpenAIAdapter`

## Assisted Mode Contract

- Assisted mode is explicit and bounded. It is not hidden inside native mode.
- Cortex starts assisted mode with the runtime banner, then the user task, then one short kernel-owned completion preview plus one short kernel-owned evidence expectation before the longer session context. Those start-of-run surfaces only state run-relevant completion and evidence conditions for this surface.
- The shipped assisted profile may carry explicit requirement-contract ids in `.codex/cortex_openai_bridge.json` under `required_requirement_ids`; Cortex will surface that full id set through the existing start-of-run `requirement_audit` contract instead of inferring ids from prompt prose.
- Direct/integrating callers may also pass repeated `--required-requirement-id <ID>` values to `run-assisted`; explicit CLI ids override the profile value for that run.
- Assisted mode may run one corrective turn when the first stop fails with kernel-owned `stop_stage = repair` or `reorient`.
- That corrective turn is derived from kernel-owned stop outputs, especially the unresolved-gap signature and structured-stop failures. It is meant to repair the real gap, not to scold generically or invent a planner loop.
- After that bounded pass, the run ends cleanly as accepted completion, truthful stuck, bounded halt for unchanged-gap false progress or terminal kernel halt, or bounded incomplete when the gap materially moved but still does not support completion.
- Assisted mode does not add tool micromanagement beyond the native App Server surface.

## Known Caveats And Status

- Status: `Experimental` on latest-stable local `codex-cli 0.111.0` as last validated 2026-03-09. Several critical paths are proven on the current App Server surface, including install/check wiring, truthful malformed-stop rejection, truthful `truth_gap` failure, and approval-blocking.
- Assisted mode is the first explicit product-development step beyond native OpenAI. It is bounded and honest, and it now also has one current committed shared-harness pair under `tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json`, but it is still supplemental-only and not a launch-proof replacement for the native validation ledger.
- `probe-model` and `probe-approval-blocking` are both live-proven. The mutating-workspace probe observed a real blocked decline; the network-sensitive and destructive-git probes still reported `pre_tool_use_approval_not_observed` as limitation gaps rather than hard failures.
- The remaining blocker is the positive strict close. That question is now split explicitly on the 2026-03-09 evidence base: a fresh native `probe_terminality` rerun reached terminal bridge JSON, a usable session id, and a Stop event, so terminality is separately proven on the tested stable surface. The shared `pass_minimal` lane was then rerun on a fresh project copy; that rerun fixed the bug and passed the target test, but strict close still failed at the challenge gate because `challenge_coverage` used invalid status-shaped objects and pytest node-id evidence instead of repo-verifiable challenge evidence.
- The March 15 critique audit remains preserved as a dated contradiction: latest-local native spotchecks were mixed, and the latest-local assisted spotcheck from that audit stalled after `SessionStart` instead of reaching the corrective path.
- The March 16 current Phase 9 packet adds newer assisted truth without erasing that older contradiction: the current assisted shared-harness pair is row-capturable, startup preview and evidence expectation were present, one bounded corrective pass occurred, and the assisted Cortex row still ended `failed_challenges` / `bounded_incomplete` with a remaining repair target. That is current bounded evidence, not native substitution.
- If command approval decline cannot be proven to block execution, the bridge must report `pre_tool_use_nonblocking_approval`.
- Runs with unresolved coverage gaps are diagnostic only and should not be treated as product evidence.
- Full runtime status and evidence stay in the main Cortex adapter reference and adapter validation ledger.
- OpenAI remains an experimental runtime surface until the positive strict close is proven stable on the tested stable release.
```
