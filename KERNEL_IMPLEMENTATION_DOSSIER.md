# Kernel Implementation Dossier

> Frozen v1 reference dossier mirrored from [`cortex-loop-v1-archive`](https://github.com/cortex-loop/cortex-loop-v1-archive/tree/v0.1.0a2) at [`v0.1.0a2`](https://github.com/cortex-loop/cortex-loop-v1-archive/releases/tag/v0.1.0a2).
> This fresh canonical repo intentionally contains only these five v1 reference documents; the full v1 tree, tests, fixtures, and releases live in the archive repo.


This dossier is the current implementation map for the Cortex completion-boundary kernel and its immediate support layers.
It is a critique-support packet, not active authority.

It is also the final v1 kernel implementation packet for the frozen archive point.

Active authority remains [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md), [../KERNEL_MATH_NOTE.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/KERNEL_MATH_NOTE.md), and [../KERNEL_MATH_IMPLEMENTATION_DECISION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/KERNEL_MATH_IMPLEMENTATION_DECISION.md).
Use this packet together with [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md), [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md), and [VALIDATION_EVIDENCE_DOSSIER.md](VALIDATION_EVIDENCE_DOSSIER.md) when you want one current whole-system review set.
The current cross-runtime interaction diagnosis that now shapes the product call below lives in [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md).

## Quick Navigation

- Need the shortest current kernel read: see Sections 0, 2, 6, 7, and 9.
- Need the code map first: see Section 3.
- Need the current live stop model: see Sections 4 and 5.
- Need tests and runtime evidence: see Section 6.
- Need the exact current source snapshot: see Section 11.

## 0. Evidence Window

This packet was regenerated from the current repo tree on `2026-03-16`.

Current local runtime installs observed during this audit:

- Claude: local `claude-code 2.1.76`
- Gemini: local `gemini-cli 0.33.1`
- OpenAI native and assisted: local `codex-cli 0.111.0`

Current repo-backed runtime validation window that exercises this kernel through real hosts:

- Claude: validated on local `claude-code 2.1.76`, last shared-harness refresh `2026-03-15`, with current March 16 Phase 9 pair evidence showing a route-valid `localized_edit/light` row ending `completed` and supplemental boundedness proof in [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md)
- Gemini: last committed shared-harness refresh on local `gemini-cli 0.32.0` from `2026-03-06`; the March 15 critique audit preserved mixed `0.33.1` spotchecks, and the March 16 current pair now adds one route-valid `localized_edit/strict` row that still ended `failed_invariants`
- OpenAI native and assisted: committed bridge evidence remains anchored to local `codex-cli 0.111.0`, last refresh `2026-03-09`; the March 15 critique audit still preserves mixed latest-local spotchecks, and the March 16 current Phase 9 packet now adds one row-capturable assisted shared-harness pair while native OpenAI remains blocked/non-row-capturable for current product-proof weight

Current kernel test surfaces used as the main implementation evidence:

- [../../tests/test_stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_payload.py)
- [../../tests/test_stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_contract.py)
- [../../tests/test_stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_policy.py)
- [../../tests/test_stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_signals.py)
- [../../tests/test_stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_runtime.py)
- [../../tests/test_requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_requirements.py)
- [../../tests/test_invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_invariants.py)
- [../../tests/test_kernel_runtime_agnostic_guard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_kernel_runtime_agnostic_guard.py)
- [../../tests/test_kernel_density_targets.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_kernel_density_targets.py)

## 1. Scope And Boundary

This dossier covers the current kernel-side implementation boundary for:

- hook orchestration in [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py)
- challenge, requirement, truth, and invariant evaluation in [../../cortex/challenges.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/challenges.py), [../../cortex/requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/requirements.py), and [../../cortex/invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/invariants.py)
- stop payload extraction and structured-stop enforcement in [../../cortex/stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_payload.py) and [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py)
- stop verdict, objective-gap, and repair computation in [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py), [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py), and [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py)
- immediate support layers that still affect runtime behavior around the kernel boundary in [../../cortex/executive.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/executive.py), [../../cortex/graveyard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/graveyard.py), and [../../cortex/retry.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/retry.py)

It does not treat the adapter bridges themselves as kernel code. Those are summarized in [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md).

## 2. Executive Snapshot

The current live kernel is flatter than the older phase-C reconstruction.
It is not an explicit `StopPathKernelBoundary(state, transition, action, claims)` object.
The current embodied stop object is the flat [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) `StopPathOutcome`, backed by:

- `StopContract` for structured stop evidence and fallback provenance
- `StopVerdict` for the compact verdict law
- `objective_gap_signature`, `objective_gap_state`, `objective_gap_unchanged_attempts`, `loop_detected`, and `loop_similarity` for failed-stop memory and relation state
- `repair_targets` plus `stop_stage` for bounded next-step guidance
- persisted session metadata for git baseline, prior stop signature, prior objective-gap signature, and startup requirement ids

Current product truth in one paragraph:

- the kernel is strong on structured stop enforcement, truthful failure classification, objective-gap tracking, and runtime-agnostic stop semantics
- the kernel is not yet strong enough on minimal-task boundedness under proof pressure
- the newer cross-runtime audit sharpens that diagnosis: the first shared product issue is validation-contract design, because the current shared positive lane is already a proof-hardening lane and destabilizes multiple runtimes differently
- the main surviving product issue is therefore below the current Claude adapter and above the upcoming executive layer: the current stop contract can still accept a truthful but over-broad completion when proof pressure conflicts with the smallest user task, but the first earned fix is the lane contract before a new kernel law

## 3. Core File Map

| Path | Current job | Main live exports / roles |
| --- | --- | --- |
| [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py) | Orchestrates `SessionStart`, `PreToolUse`, `PostToolUse`, and `Stop` around the kernel | `CortexKernel`, startup preview/evidence expectation, tool hooks, stop entrypoint |
| [../../cortex/challenges.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/challenges.py) | Challenge coverage evaluation and evidence verification | `ChallengeEnforcer`, `ChallengeReport`, challenge diagnostics and gap entries |
| [../../cortex/stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_payload.py) | Raw stop-field extraction and trailer parsing | `extract_stop_fields`, `resolve_stop_value`, `parse_stop_fields_json` |
| [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py) | Canonical structured-stop contract resolution | `StopContract`, `resolve_stop_contract`, requirement-id reconciliation |
| [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py) | Compact verdict and stage law | `StopVerdict`, `compute_stop_outcome` |
| [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py) | Stop-attempt signatures, objective-gap signatures, relation and loop state | `build_stop_attempt_signature`, `build_objective_gap_signature`, `classify_objective_gap_state` |
| [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | End-to-end stop-path execution, persistence, and repair targeting | `StopPathOutcome`, `StopPathRunner` |
| [../../cortex/requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/requirements.py) | Requirement-audit and truth-claim evaluation | `RequirementAuditEvaluation`, `TruthClaimsEvaluation`, evaluators |
| [../../cortex/invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/invariants.py) | Host invariant execution and normalization | `InvariantRunner`, `InvariantReport` |
| [../../cortex/executive.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/executive.py) | Executive support material that remains downstream of kernel truth | startup executive context, stop-failure recording, decay |
| [../../cortex/graveyard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/graveyard.py) | Similar-failure memory and explainability warnings | `Graveyard`, similarity scoring |
| [../../cortex/retry.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/retry.py) | Bounded retry verdict support after tool failures | retry reason families and verdict computation |

## 4. Current Runtime Flow

### 4.1 SessionStart

`CortexKernel.on_session_start(...)` in [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py) is support, not completion truth.
It currently:

- allocates session identity and stores startup metadata
- captures the git baseline snapshot and any session-start requirement ids
- loads executive context, graveyard context, and foundation warnings when configured
- builds the short completion preview and the assisted-mode evidence expectation

The key current product point is that `SessionStart` improves finish-line legibility, but it does not decide completion.

### 4.2 PreToolUse / PostToolUse

`CortexKernel.on_pre_tool_use(...)` and `CortexKernel.on_post_tool_use(...)` remain bounded support surfaces.
They currently:

- apply blocklist and foundation warnings before tool execution
- record tool activity, graveyard similarity warnings, and retry verdicts after tool execution
- preserve kernel ownership by not deciding completion or reinterpreting stop meaning

### 4.3 Stop

`CortexKernel.on_stop(...)` is the hard completion boundary.
The current stop path is:

1. resolve the structured stop contract
2. evaluate challenge, requirement, truth, and invariant surfaces
3. build the local stop-attempt signature and objective-gap signature
4. compute the compact stop verdict in [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py)
5. classify objective-gap relation and failed-stop memory state
6. derive bounded `stop_stage` and `repair_targets`
7. persist stop metadata back into the session record
8. return warnings plus a kernel-owned response payload for the runtime bridge

## 5. Current Live Kernel Object Model

### 5.1 `StopContract`

The current structured-stop contract lives in [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py) and carries:

- stop-source provenance (`native`, `payload.stop_fields`, or trailer fallback)
- normalized `challenge_coverage`, `requirement_audit`, `truth_claims`, `required_requirement_ids`, `failed_approach`, and `stuck_declaration`
- structured-stop violation state and diagnostic payloads
- warnings about fallback, normalization, and invalid shapes

This is where Cortex enforces “machine-readable stop evidence” before the harder semantic gates run.

### 5.2 `StopVerdict`

The compact verdict law lives in [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py).
`StopVerdict` currently carries:

- `session_status`
- `recommend_revert`
- `proceed`
- `feedback_mode`
- `terminate_session`
- `stop_stage`

This is the actual hard-gate law. There is still no explicit boundedness or scope-overreach term here.

### 5.3 `StopPathOutcome`

The current returned stop object is the flat `StopPathOutcome` in [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py).
It carries:

- warnings and structured-stop diagnostics
- challenge, requirement, truth, and invariant evaluations
- the final `session_status`, `stop_stage`, `feedback_mode`, `proceed`, `terminate_session`, and `recommend_revert`
- the local `stop_attempt_signature`
- `loop_detected` and `loop_similarity`
- `objective_gap_signature`, `objective_gap_state`, `objective_gap_unchanged_attempts`, and `objective_gap_reason`
- `repair_targets`

This is current code reality. The older decomposed `kernel/state/transition/action/claims` boundary is not the live implementation anymore.

### 5.4 Persisted Kernel Memory

The kernel currently persists enough stop-time memory to keep repeated failures honest:

- startup git baseline and required requirement ids
- prior `stop_attempt_signature`
- prior `objective_gap_signature`
- `objective_gap_unchanged_attempts`
- last `stop_stage`
- last `repair_targets`
- session-close metadata derived from the final stop outcome

That persisted memory is what lets the current kernel distinguish first-observed, stagnant, reduced, expanded, and substituted failed-stop states.

## 6. Test And Runtime Evidence Summary

### 6.1 Code-level kernel tests

- [../../tests/test_stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_payload.py): trailer parsing, payload-stop-field extraction, and key normalization
- [../../tests/test_stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_contract.py): structured-stop enforcement, requirement-id reconciliation, `failed_approach` normalization, and `stuck_declaration` shape checks
- [../../tests/test_stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_policy.py): the compact verdict law, revert posture, and `repair` / `reorient` / `halt` stage assignment
- [../../tests/test_stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_signals.py): stop-attempt signatures, objective-gap signatures, relation taxonomy (`identical`, `reduced`, `expanded`, `substituted`), and loop-similarity logic
- [../../tests/test_stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_runtime.py): end-to-end stop-path behavior, persistence, payload projection, warnings, and repair-target generation
- [../../tests/test_requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_requirements.py): requirement-audit and truth-claim evaluation rules
- [../../tests/test_invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_invariants.py): invariant execution, normalization, and failure mapping
- [../../tests/test_kernel_runtime_agnostic_guard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_kernel_runtime_agnostic_guard.py): runtime-brand isolation across kernel modules
- [../../tests/test_kernel_density_targets.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_kernel_density_targets.py): stop-path density and concentration guard so the kernel boundary does not dissolve into generic support code

### 6.2 Live runtime evidence that exercises this kernel

- shared adapter-validation evidence in [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) proves this kernel through Claude, Gemini, and OpenAI surfaces
- the boundedness RCA in [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md) is now the main current proof that kernel truth and patch boundedness still diverge on some pressure-heavy tasks
- the broader cross-runtime audit in [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md) now shows that the first shared product issue is larger than Claude alone: the current positive lane itself conflates minimal-fix success with proof-hardening across multiple runtimes
- current repo truth says the kernel is good at proof and truthful stop classification, but it does not yet have committed evidence that Cortex beats the raw model on artifact quality

## 7. Real Implementation And Current Functioning

What the current kernel is doing well:

- preserving a hard structured-stop boundary across all shipped runtimes
- keeping verdict law compact and explicit instead of pushing acceptance into adapter prose or runtime-local prompt policy
- tracking failed-stop relation state and repeat-attempt memory without adding a planner layer
- preserving truthful `stuck` as a respected terminal state

What is currently mixed or still inadequate:

- minimal-task boundedness is not an explicit acceptance criterion
- under proof pressure, the kernel can still accept a truthful but over-broad completion once challenge, requirement, truth, and invariant gates pass
- the upcoming executive layer will not fix that acceptance-law problem by itself; it can improve approach control, but it does not own completion truth
- current product proof is still asymmetric: Cortex has stronger completion evidence than the raw model, but not yet stronger artifact quality proof

## 8. What Another Researcher Should Critique First

1. Should boundedness or scope-overreach become an explicit stop-law term rather than only a post-mortem diagnosis?
2. Is `StopPathOutcome` still the right flat carrier, or is there now a smaller honest split that would remove live ambiguity without adding abstraction?
3. Are the current objective-gap signatures rich enough to support boundedness-aware acceptance, or would that add a second control doctrine instead of clarifying the first one?
4. Are any executive-side support paths still quietly compensating for kernel gaps instead of staying downstream of kernel truth?
5. Does the current runtime evidence support any stronger product claim than “better proof of completion than raw”?

## 9. Current Sweep Verdict

After auditing the current code, tests, validation ledger, realization ledger, and boundedness post-mortem:

- the current kernel snapshot is the flat `StopContract` + `StopVerdict` + `StopPathOutcome` model, not the older decomposed boundary packet
- the current kernel test surface is strong on stop-law correctness, structured-stop enforcement, and failed-stop relation logic
- the current live runtime evidence is strong on truthful completion-boundary enforcement but still mixed on patch boundedness under proof pressure
- the main remaining product issue is now below the adapter and outside the executive layer: the stop/validation contract still overweights proof completion relative to minimal task boundedness on some tasks
- the cross-runtime audit now sharpens the ordering: validation-contract redesign is earned before a new kernel boundedness primitive, because the current shared positive lane is itself the strongest common pressure source

## 10. Appendix File Map

The full source appendix below is generated from the explicit manifest at [kernel_appendix_manifest.txt](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/dossiers/manifests/kernel_appendix_manifest.txt).

- [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py)
- [../../cortex/core_helpers.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core_helpers.py)
- [../../cortex/blocklist.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/blocklist.py)
- [../../cortex/foundation.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/foundation.py)
- [../../cortex/challenges.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/challenges.py)
- [../../cortex/requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/requirements.py)
- [../../cortex/invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/invariants.py)
- [../../cortex/stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_payload.py)
- [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py)
- [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py)
- [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py)
- [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py)
- [../../cortex/executive.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/executive.py)
- [../../cortex/graveyard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/graveyard.py)
- [../../cortex/retry.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/retry.py)
- [../../cortex/store.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/store.py)

## 11. Full Source Appendix

This appendix is generated from an explicit final-v1 manifest.

- Manifest: [kernel_appendix_manifest.txt](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/dossiers/manifests/kernel_appendix_manifest.txt)
- Generation base commit: `685e583539afafbe5c365dbfddf59fb5d1713d82`
- Frozen release tag target: `v0.1.0a2`

### Appendix File Map

- [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py)
- [../../cortex/core_helpers.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core_helpers.py)
- [../../cortex/blocklist.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/blocklist.py)
- [../../cortex/foundation.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/foundation.py)
- [../../cortex/challenges.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/challenges.py)
- [../../cortex/requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/requirements.py)
- [../../cortex/invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/invariants.py)
- [../../cortex/stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_payload.py)
- [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py)
- [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py)
- [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py)
- [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py)
- [../../cortex/executive.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/executive.py)
- [../../cortex/graveyard.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/graveyard.py)
- [../../cortex/retry.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/retry.py)
- [../../cortex/store.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/store.py)

### Full Source Snapshot

### `cortex/core.py`

```python
from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from .adapters import EventAdapter, load_adapter
from .challenges import ChallengeEnforcer
from .core_helpers import (
    extract_required_requirement_ids,
    foundation_warnings_from_snapshot,
    session_foundation_snapshot,
    session_changed_files_since_baseline,
    session_git_snapshot,
    session_metadata,
    session_required_requirement_ids,
    session_witness_context,
)
from .executive import (
    get_base_executive_function,
    get_identity_preamble,
    get_learned_executive_function,
    record_stop_failure_event,
    run_decay,
)
from .foundation import FoundationAnalyzer
from .genome import CortexGenome, load_genome
from .graveyard import Graveyard, explainability_warnings
from .invariants import InvariantRunner
from .blocklist import DEFAULT_BLOCKED_TOOLS, evaluate_blocklist
from .retry import compute_retry_verdict
from .stop_contract import resolve_stop_contract
from .stop_runtime import StopPathRunner
from .store import SQLiteStore
from .utils import _as_bool, _as_string_list, _normalize_repo_relative_path, _unique_list


@dataclass(slots=True)
class KernelContext:
    root: Path
    genome_path: Path
    db_path: Path
    genome: CortexGenome
    store: SQLiteStore


_TASK_REGIME_VALUES = frozenset({"reflex", "localized_edit", "bounded_build", "open_ended"})
_ASSURANCE_CLASS_VALUES = frozenset({"light", "standard", "strict"})
_ROUTE_ESCALATION_FIELDS = frozenset({"task_regime", "assurance_class"})
_TASK_SUMMARY_MAX_CHARS = 280


def _route_file_targets(payload: Mapping[str, Any]) -> list[str]:
    return _unique_list(_as_string_list(payload.get("target_files")) + _as_string_list(payload.get("planned_files")))


def _route_target_identity(value: str, *, root: Path) -> str | None:
    normalized = _normalize_repo_relative_path(value, root=root)
    if normalized:
        return normalized
    fallback = str(value).strip().replace("\\", "/").removeprefix("./").rstrip("/")
    if not fallback or Path(fallback).is_absolute():
        return None
    return fallback


def _task_summary(payload: Mapping[str, Any]) -> str:
    for field_name in ("task", "objective", "prompt", "message", "input"):
        raw_value = payload.get(field_name)
        if not isinstance(raw_value, str):
            continue
        normalized = " ".join(raw_value.split())
        if normalized:
            return _truncate_context_text(normalized, _TASK_SUMMARY_MAX_CHARS)
    return ""


def _validated_route_override(
    *,
    field_name: str,
    value: Any,
    allowed: frozenset[str],
) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"Invalid {field_name}: {text!r}. Expected one of: {choices}.")
    return text


def _resolve_task_regime(payload: Mapping[str, Any]) -> str:
    explicit = _validated_route_override(
        field_name="task_regime",
        value=payload.get("task_regime"),
        allowed=_TASK_REGIME_VALUES,
    )
    if explicit is not None:
        return explicit
    file_targets = _route_file_targets(payload)
    if len(file_targets) >= 3:
        return "bounded_build"
    if file_targets:
        return "localized_edit"
    return "open_ended"


def _resolve_assurance_class(
    payload: Mapping[str, Any],
    *,
    required_requirement_ids: list[str],
) -> str:
    explicit = _validated_route_override(
        field_name="assurance_class",
        value=payload.get("assurance_class"),
        allowed=_ASSURANCE_CLASS_VALUES,
    )
    if explicit is not None:
        return explicit
    run_invariants = _as_bool(payload.get("run_invariants"), False)
    if required_requirement_ids or run_invariants:
        return "strict"
    repo_touch_indicators = bool(_route_file_targets(payload))
    task_contract = payload.get("task_contract")
    explicit_contract_surfaces = isinstance(task_contract, Mapping) and bool(task_contract)
    if not repo_touch_indicators and not explicit_contract_surfaces:
        return "light"
    return "standard"


def _derive_route_metadata(
    payload: Mapping[str, Any],
    *,
    required_requirement_ids: list[str],
) -> dict[str, str]:
    return {
        "task_regime": _resolve_task_regime(payload),
        "assurance_class": _resolve_assurance_class(
            payload,
            required_requirement_ids=required_requirement_ids,
        ),
    }


def _preserved_route_metadata(metadata: Mapping[str, Any]) -> dict[str, str]:
    preserved: dict[str, str] = {}
    for field_name, allowed in (
        ("task_regime", _TASK_REGIME_VALUES),
        ("assurance_class", _ASSURANCE_CLASS_VALUES),
    ):
        value = metadata.get(field_name)
        if isinstance(value, str) and value in allowed:
            preserved[field_name] = value
    return preserved


def _route_escalation_trace(metadata: Mapping[str, Any]) -> list[dict[str, str]]:
    raw_trace = metadata.get("route_escalations")
    if not isinstance(raw_trace, list):
        return []
    trace: list[dict[str, str]] = []
    for raw_entry in raw_trace:
        if not isinstance(raw_entry, Mapping):
            continue
        field_name = str(raw_entry.get("field") or "").strip()
        from_value = str(raw_entry.get("from") or "").strip()
        to_value = str(raw_entry.get("to") or "").strip()
        reason = str(raw_entry.get("reason") or "").strip()
        hook = str(raw_entry.get("hook") or "").strip()
        if field_name not in _ROUTE_ESCALATION_FIELDS or not reason or not hook:
            continue
        allowed = _TASK_REGIME_VALUES if field_name == "task_regime" else _ASSURANCE_CLASS_VALUES
        if from_value not in allowed or to_value not in allowed:
            continue
        trace.append(
            {
                "field": field_name,
                "from": from_value,
                "to": to_value,
                "reason": reason,
                "hook": hook,
            }
        )
    return trace


def _route_metadata_projection(metadata: Mapping[str, Any]) -> dict[str, Any]:
    projection: dict[str, Any] = _preserved_route_metadata(metadata)
    projection["route_escalations"] = _route_escalation_trace(metadata)
    return projection


def _is_low_friction_route_state(
    *,
    task_regime: str,
    assurance_class: str,
) -> bool:
    return assurance_class == "light" and task_regime in {"reflex", "localized_edit"}


def _route_tracking_metadata(
    metadata: Mapping[str, Any],
    *,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    tracked = dict(metadata)
    required_requirement_ids = _unique_list(
        _as_string_list(tracked.get("required_requirement_ids")) or extract_required_requirement_ids(payload)
    )
    derived = _derive_route_metadata(
        payload,
        required_requirement_ids=required_requirement_ids,
    )
    for field_name, value in derived.items():
        tracked.setdefault(field_name, value)
    tracked.setdefault(
        "route_explicit_overrides",
        {
            "task_regime": _validated_route_override(
                field_name="task_regime",
                value=payload.get("task_regime"),
                allowed=_TASK_REGIME_VALUES,
            )
            is not None,
            "assurance_class": _validated_route_override(
                field_name="assurance_class",
                value=payload.get("assurance_class"),
                allowed=_ASSURANCE_CLASS_VALUES,
            )
            is not None,
        },
    )
    tracked["route_escalations"] = _route_escalation_trace(tracked)
    tracked["route_observed_file_targets"] = _unique_list(
        _as_string_list(tracked.get("route_observed_file_targets"))
    )
    return tracked


def _append_route_escalation(
    metadata: dict[str, Any],
    *,
    field_name: str,
    to_value: str,
    reason: str,
    hook: str,
) -> None:
    current_value = str(metadata.get(field_name) or "").strip()
    if current_value == to_value:
        return
    trace = _route_escalation_trace(metadata)
    trace.append(
        {
            "field": field_name,
            "from": current_value,
            "to": to_value,
            "reason": reason,
            "hook": hook,
        }
    )
    metadata[field_name] = to_value
    metadata["route_escalations"] = trace


def _apply_task_regime_escalation(
    metadata: Mapping[str, Any],
    *,
    payload: Mapping[str, Any],
    hook: str,
    root: Path,
) -> dict[str, Any]:
    updated = _route_tracking_metadata(metadata, payload=payload)
    observed_targets = _unique_list(
        _as_string_list(updated.get("route_observed_file_targets")) + _route_file_targets(payload)
    )
    updated["route_observed_file_targets"] = observed_targets
    countable_observed_targets = _unique_list(
        [
            normalized
            for normalized in (_route_target_identity(value, root=root) for value in observed_targets)
            if normalized
        ]
    )
    explicit_overrides = updated.get("route_explicit_overrides")
    task_regime_explicit = (
        isinstance(explicit_overrides, Mapping) and bool(explicit_overrides.get("task_regime"))
    )
    current_regime = str(updated.get("task_regime") or "").strip()
    if task_regime_explicit:
        return updated
    if len(countable_observed_targets) >= 3 and current_regime in {"open_ended", "reflex", "localized_edit"}:
        _append_route_escalation(
            updated,
            field_name="task_regime",
            to_value="bounded_build",
            reason="cumulative_explicit_file_targets>=3",
            hook=hook,
        )
    elif countable_observed_targets and current_regime == "open_ended":
        _append_route_escalation(
            updated,
            field_name="task_regime",
            to_value="localized_edit",
            reason="cumulative_explicit_file_targets>=1",
            hook=hook,
        )
    return updated


def _assurance_escalation_reasons(
    *,
    requirements_gate_gap: bool,
    missing_challenge_coverage: bool,
    structured_stop_violation: bool,
    invariant_ok: bool | None,
) -> list[str]:
    reasons: list[str] = []
    if requirements_gate_gap:
        reasons.append("requirements_gate_gap")
    if missing_challenge_coverage:
        reasons.append("missing_challenge_coverage")
    if structured_stop_violation:
        reasons.append("structured_stop_violation")
    if invariant_ok is False:
        reasons.append("failing_invariants")
    return reasons


def _apply_assurance_class_escalation(
    metadata: Mapping[str, Any],
    *,
    reasons: list[str],
    hook: str,
) -> dict[str, Any]:
    updated = dict(metadata)
    updated["route_escalations"] = _route_escalation_trace(updated)
    if str(updated.get("assurance_class") or "").strip() in {"light", "standard"} and reasons:
        _append_route_escalation(
            updated,
            field_name="assurance_class",
            to_value="strict",
            reason="stop_signal:" + ",".join(reasons),
            hook=hook,
        )
    return updated


class CortexKernel:
    """Hook-driven orchestration kernel for Cortex subsystems."""

    def __init__(
        self,
        root: str | Path | None = None,
        *,
        config_path: str | Path | None = None,
        db_path: str | Path | None = None,
        adapter_name: str | None = None,
        adapter: EventAdapter | None = None,
    ) -> None:
        if adapter_name is not None:
            raise ValueError(
                "adapter_name is no longer supported. Configure [runtime].adapter in cortex.toml."
            )
        repo_root = Path(root or os.getcwd()).resolve()
        genome_path = Path(config_path).resolve() if config_path else repo_root / "cortex.toml"
        store = SQLiteStore(Path(db_path).resolve() if db_path else repo_root / ".cortex" / "cortex.db")
        store.initialize()
        genome = load_genome(genome_path)
        self.ctx = KernelContext(
            root=repo_root,
            genome_path=genome_path,
            db_path=store.db_path,
            genome=genome,
            store=store,
        )
        self.foundation = FoundationAnalyzer(repo_root, genome.foundation)
        self.graveyard = Graveyard(store, genome.graveyard)
        self.challenges = ChallengeEnforcer(store, genome.challenges)
        self.invariants = InvariantRunner(
            repo_root,
            store,
            genome.invariants,
            genome.hooks,
            trust_profile=genome.project.trust_profile,
        )
        self.adapter = adapter or load_adapter(genome.runtime.adapter)
        self.stop_path = StopPathRunner(
            root=repo_root,
            store=store,
            genome=genome,
            challenges=self.challenges,
            invariants=self.invariants,
            graveyard=self.graveyard,
            session_metadata_loader=lambda active_store, active_session_id: session_metadata(
                active_store, active_session_id
            ),
            session_git_snapshotter=lambda active_root: session_git_snapshot(active_root),
            session_changed_files_since_baseline_fn=(
                lambda **kwargs: session_changed_files_since_baseline(**kwargs)
            ),
            session_required_requirement_ids_loader=(
                lambda active_store, active_session_id: session_required_requirement_ids(
                    active_store, active_session_id
                )
            ),
            session_witness_context_loader=(
                lambda active_store, active_session_id: session_witness_context(
                    active_store, active_session_id
                )
            ),
        )
        self._known_sessions: set[str] = set()

    def on_session_start(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        payload = self.adapter.normalize("session_start", payload).payload
        session_id = self._session_id(payload)
        runtime_mode = str(payload.get("runtime_mode") or "").strip()
        part_a_full, _part_b = get_base_executive_function()
        executive_cfg = self.ctx.genome.executive
        part_a = part_a_full if executive_cfg.part_a_mode != "once_per_project" else ""
        identity_preamble = ""
        required_requirement_ids = extract_required_requirement_ids(payload)
        session_meta: dict[str, Any] = {"hook": "SessionStart"}
        session_counter = self.ctx.store.allocate_session_counter(session_id)
        session_meta["session_counter"] = session_counter
        session_meta.update(
            _derive_route_metadata(
                payload,
                required_requirement_ids=required_requirement_ids,
            )
        )
        session_meta["route_escalations"] = []
        session_meta["route_observed_file_targets"] = _route_file_targets(payload)
        session_meta["route_explicit_overrides"] = {
            "task_regime": _validated_route_override(
                field_name="task_regime",
                value=payload.get("task_regime"),
                allowed=_TASK_REGIME_VALUES,
            )
            is not None,
            "assurance_class": _validated_route_override(
                field_name="assurance_class",
                value=payload.get("assurance_class"),
                allowed=_ASSURANCE_CLASS_VALUES,
            )
            is not None,
        }
        if required_requirement_ids:
            session_meta["required_requirement_ids"] = required_requirement_ids
        task_summary = _task_summary(payload)
        if task_summary:
            session_meta["task_summary"] = task_summary
        session_meta["git_snapshot"] = session_git_snapshot(self.ctx.root)
        self._record_event(session_id, "SessionStart", payload)

        learned_patterns = ""
        if executive_cfg.enabled:
            if executive_cfg.inject_identity_preamble:
                identity_preamble = get_identity_preamble()
            pruned = run_decay(
                self.ctx.store,
                halflife_sessions=executive_cfg.halflife_sessions,
                threshold=executive_cfg.decay_threshold,
                min_hold_sessions=executive_cfg.min_hold_sessions,
            )
            session_meta["executive_decay_pruned"] = pruned
            learned_patterns = get_learned_executive_function(
                self.ctx.store,
                halflife_sessions=executive_cfg.halflife_sessions,
                inject_threshold=executive_cfg.inject_threshold,
                decay_threshold=executive_cfg.decay_threshold,
                max_entries=executive_cfg.max_entries,
                max_tokens=executive_cfg.max_tokens,
                min_hold_sessions=executive_cfg.min_hold_sessions,
            )

        foundation_report = self.foundation.analyze()
        session_meta["foundation"] = {
            "warnings": list(foundation_report.warnings),
            "findings": [finding.to_dict() for finding in foundation_report.findings],
        }
        self.ctx.store.upsert_session_start(
            session_id=session_id,
            status="running",
            genome_path=self.ctx.genome.source_path,
            metadata=session_meta,
        )
        self._known_sessions.add(session_id)
        graveyard_task = str(payload.get("task") or payload.get("objective") or "")
        target_files = _as_string_list(payload.get("target_files"))
        graveyard_matches = [m.to_dict() for m in self.graveyard.find_similar(graveyard_task, target_files)]
        repomap_summary = self._session_start_repomap(session_id=session_id, payload=payload)

        warnings = list(foundation_report.warnings)
        if self.ctx.genome.parse_error:
            warnings.append(f"Config parse error in {self.ctx.genome.source_path}: {self.ctx.genome.parse_error}")
        if self.ctx.genome.load_warnings:
            warnings.extend(f"Config warning: {warning}" for warning in self.ctx.genome.load_warnings)
        if graveyard_matches:
            warnings.append(f"Found {len(graveyard_matches)} graveyard match(es) relevant to this session.")
            warnings.extend(explainability_warnings(graveyard_matches))
        if repomap_summary and repomap_summary.get("warning"):
            warnings.append(str(repomap_summary["warning"]))
        graveyard_context = _graveyard_context_block(graveyard_matches, self.ctx.genome.graveyard)
        if executive_cfg.part_a_mode == "once_per_project":
            part_a = part_a_full if self.ctx.store.claim_meta_once("executive.part_a_injected") else ""
        context_blocks: list[str] = []
        if identity_preamble:
            context_blocks.append(identity_preamble)
        if part_a:
            context_blocks.append(part_a)
        if learned_patterns:
            context_blocks.append(learned_patterns)
        if graveyard_context:
            context_blocks.append(graveyard_context)
        completion_preview = self._session_start_completion_preview(
            runtime_mode=runtime_mode,
            stop_trailer_marker=str(payload.get("stop_trailer_marker") or "").strip(),
            required_requirement_ids=required_requirement_ids,
            task_regime=session_meta["task_regime"],
            assurance_class=session_meta["assurance_class"],
        )
        evidence_expectation = self._session_start_evidence_expectation(
            runtime_mode=runtime_mode,
            required_requirement_ids=required_requirement_ids,
            task_regime=session_meta["task_regime"],
            assurance_class=session_meta["assurance_class"],
        )

        return self._response(
            hook="SessionStart",
            session_id=session_id,
            warnings=warnings,
            foundation=foundation_report.to_dict(),
            graveyard_matches=graveyard_matches,
            repomap=repomap_summary,
            required_requirement_ids=required_requirement_ids,
            task_regime=session_meta["task_regime"],
            assurance_class=session_meta["assurance_class"],
            executive_context={
                "identity_preamble": identity_preamble,
                "part_a": part_a,
                "learned": learned_patterns,
            },
            context_blocks=context_blocks,
            completion_preview=completion_preview,
            evidence_expectation=evidence_expectation,
        )

    def on_pre_tool_use(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        payload = self.adapter.normalize("pre_tool_use", payload).payload
        session_id = self._session_id(payload)
        tool_name = str(payload.get("tool_name") or "").strip() or None
        self._record_event(
            session_id,
            "PreToolUse",
            payload,
            tool_name=tool_name,
            status=str(payload.get("status")) if payload.get("status") is not None else None,
        )
        self._update_running_route_metadata(
            session_id=session_id,
            payload=payload,
            hook="PreToolUse",
        )

        warnings: list[str] = []
        proceed = True

        # --- Blocklist gate ---------------------------------------------------
        bl_cfg = self.ctx.genome.blocklist
        if bl_cfg.enabled:
            cfg_blocked = frozenset(t.strip().lower() for t in bl_cfg.blocked_tools if t.strip())
            effective_blocked = (cfg_blocked | DEFAULT_BLOCKED_TOOLS) if cfg_blocked else DEFAULT_BLOCKED_TOOLS
            effective_allowed = frozenset(t.strip().lower() for t in bl_cfg.allowed_tools if t.strip())
            verdict = evaluate_blocklist(
                tool_name,
                blocked_tools=effective_blocked,
                allowed_tools=effective_allowed,
                fail_closed=bl_cfg.fail_closed,
            )
            if verdict.blocked:
                proceed = False
                warnings.append(
                    f"Tool '{tool_name or 'unknown'}' blocked by denylist ({verdict.reason})."
                )

        target_files = _as_string_list(payload.get("target_files")) + _as_string_list(payload.get("planned_files"))
        if target_files:
            warnings.extend(self._foundation_warnings(session_id=session_id, target_files=target_files))

        return self._response(
            hook="PreToolUse",
            session_id=session_id,
            warnings=warnings,
            proceed=proceed,
        )

    def on_session_marker(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        payload = self.adapter.normalize("session_marker", payload).payload
        label = str(payload.get("label") or "").strip()
        if not label:
            raise ValueError("session_marker requires non-empty 'label'.")
        session_id = str(payload.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("session_marker requires session_id.")
        self._record_event(session_id, "SessionMarker", {"label": label})
        return self._response(hook="SessionMarker", session_id=session_id, warnings=[], label=label)

    def on_post_tool_use(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        payload = self.adapter.normalize("post_tool_use", payload).payload
        session_id = self._session_id(payload)
        tool_name = str(payload.get("tool_name") or "").strip() or None
        self._record_event(
            session_id,
            "PostToolUse",
            payload,
            tool_name=tool_name,
            status=str(payload.get("status")) if payload.get("status") is not None else None,
        )
        self._update_running_route_metadata(
            session_id=session_id,
            payload=payload,
            hook="PostToolUse",
        )

        warnings: list[str] = []
        retry_verdict = None
        if str(payload.get("status", "")).lower() in {"error", "failed", "fail"}:
            summary = str(payload.get("error") or payload.get("message") or "")
            target_files = _as_string_list(payload.get("target_files"))
            matches = self.graveyard.find_similar(summary, target_files, max_matches=3)
            if matches:
                warnings.append(
                    f"Tool failure resembles {len(matches)} graveyard entry/entries; review before retrying."
                )
                warnings.extend(explainability_warnings([m.to_dict() for m in matches]))

            if self.ctx.genome.retry.enabled:
                retry_verdict = compute_retry_verdict(
                    store=self.ctx.store,
                    session_id=session_id,
                    payload=payload,
                    max_retries=self.ctx.genome.retry.max_retries,
                )
                if retry_verdict:
                    self._record_event(
                        session_id,
                        "RetryConsume",
                        {
                            "should_retry": retry_verdict.should_retry,
                            "reason": retry_verdict.reason,
                            "failure_class": retry_verdict.failure_class,
                            "status": str(payload.get("status") or ""),
                            "tool_name": tool_name,
                            "budget_remaining": retry_verdict.budget_remaining,
                            "budget_exhausted": retry_verdict.budget_exhausted,
                            "decision_code": retry_verdict.decision_code,
                            "failure_signature": retry_verdict.failure_signature,
                        },
                        tool_name=tool_name,
                        status="consumed" if retry_verdict.should_retry else "rejected",
                    )

        retry_info: dict[str, Any] | None = None
        if retry_verdict is not None:
            retry_info = {
                "should_retry": retry_verdict.should_retry,
                "hard_stop": retry_verdict.hard_stop,
                "failure_class": retry_verdict.failure_class,
                "reason": retry_verdict.reason,
                "budget_remaining": retry_verdict.budget_remaining,
                "budget_exhausted": retry_verdict.budget_exhausted,
                "decision_code": retry_verdict.decision_code,
            }
            if retry_verdict.hard_stop:
                warnings.append(f"Hard stop: non-retryable failure ({retry_verdict.reason}).")
            elif retry_verdict.decision_code == "no_delta":
                warnings.append("Retry suppressed: no delta detected for repeated failure signature.")
            elif retry_verdict.decision_code == "retry_contention":
                warnings.append("Retry contention detected; retry slot was not acquired. Re-evaluate and retry after state settles.")
            elif retry_verdict.decision_code == "reason_budget_exhausted":
                warnings.append("Reason-specific retry budget exhausted; no further retries allowed for this failure reason.")
            elif retry_verdict.budget_exhausted:
                warnings.append("Retry budget exhausted; no further retries allowed.")

        proceed = not (retry_verdict is not None and retry_verdict.hard_stop)

        return self._response(
            hook="PostToolUse",
            session_id=session_id,
            warnings=warnings,
            proceed=proceed,
            retry=retry_info,
        )

    def on_stop(self, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        payload = self.adapter.normalize("stop", payload).payload
        session_id = self._session_id(payload)
        stop_contract = resolve_stop_contract(
            payload,
            allow_message_fallback=self.ctx.genome.hooks.allow_message_stop_fallback,
            require_structured_stop_payload=self.ctx.genome.hooks.require_structured_stop_payload,
        )
        self._record_event(
            session_id,
            "Stop",
            payload,
            capture_git_snapshot=True,
        )
        stop_outcome = self.stop_path.run(
            session_id=session_id,
            payload=payload,
            stop_contract=stop_contract,
        )
        requirement_audit = stop_outcome.requirement_audit
        truth_claims = stop_outcome.truth_claims
        challenge_report = stop_outcome.challenge_report
        invariant_report = stop_outcome.invariant_report
        requirement_audit_gap = requirement_audit.gap
        truth_claims_gap = truth_claims.gap
        requirements_gate_gap = requirement_audit_gap or truth_claims_gap
        route_metadata = _apply_task_regime_escalation(
            session_metadata(self.ctx.store, session_id),
            payload=payload,
            hook="Stop",
            root=self.ctx.root,
        )
        route_metadata = _apply_assurance_class_escalation(
            route_metadata,
            reasons=_assurance_escalation_reasons(
                requirements_gate_gap=requirements_gate_gap,
                missing_challenge_coverage=stop_outcome.missing_challenge_coverage,
                structured_stop_violation=stop_outcome.structured_stop_violation,
                invariant_ok=None if invariant_report is None else invariant_report.ok,
            ),
            hook="Stop",
        )
        executive_record, executive_signature = (None, None)
        if self.ctx.genome.executive.enabled:
            executive_record, executive_signature = record_stop_failure_event(
                self.ctx.store,
                session_id=session_id,
                structured_stop_violation=stop_outcome.structured_stop_violation,
                challenge_coverage_missing=stop_outcome.missing_challenge_coverage,
                challenge_report=None if challenge_report is None else challenge_report.to_dict(),
                requirements_gate_gap=requirements_gate_gap,
                requirement_audit_report=requirement_audit.report,
                truth_claims_report=truth_claims.report,
                invariant_report=None if invariant_report is None else invariant_report.to_dict(),
                signature_claim=lambda sig: self.ctx.store.claim_executive_stop_signature(session_id, sig),
            )

        close_metadata = self.stop_path.close_session_metadata(
            outcome=stop_outcome,
            stop_contract=stop_contract,
            executive_signature=executive_signature,
            executive_record=executive_record,
        )
        close_metadata.update(_route_metadata_projection(route_metadata))
        self.ctx.store.close_session(
            session_id=session_id,
            status=stop_outcome.session_status,
            metadata=close_metadata,
        )

        return self._response(
            hook="Stop",
            session_id=session_id,
            warnings=stop_outcome.warnings,
            **_route_metadata_projection(route_metadata),
            **self.stop_path.response_payload(
                outcome=stop_outcome,
                stop_contract=stop_contract,
            ),
        )

    def dispatch(self, event_name: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        event_name = self.adapter.normalize(event_name, None).name
        if event_name == "session_start":
            return self.on_session_start(payload)
        if event_name == "session_marker":
            return self.on_session_marker(payload)
        if event_name == "pre_tool_use":
            return self.on_pre_tool_use(payload)
        if event_name == "post_tool_use":
            return self.on_post_tool_use(payload)
        if event_name == "stop":
            return self.on_stop(payload)
        raise ValueError(f"Unknown hook event: {event_name}")

    def _record_event(
        self,
        session_id: str,
        hook: str,
        payload: Mapping[str, Any],
        *,
        tool_name: str | None = None,
        status: str | None = None,
        capture_git_snapshot: bool = True,
    ) -> None:
        self._ensure_session_started(session_id=session_id, hook=hook, capture_git_snapshot=capture_git_snapshot)
        self.ctx.store.record_event(
            session_id=session_id,
            hook=hook,
            payload=dict(payload),
            tool_name=tool_name,
            status=status,
        )

    def _response(self, *, hook: str, session_id: str, warnings: list[str], **extra: Any) -> dict[str, Any]:
        response = {
            "ok": True,
            "hook": hook,
            "session_id": session_id,
            "mode": self.ctx.genome.hooks.mode,
            "warnings": warnings,
            **extra,
        }
        if not self.ctx.genome.hooks.minimal_response:
            response["config"] = {
                "genome_path": self._response_path(self.ctx.genome_path),
                "db_path": self._response_path(self.ctx.db_path),
            }
        return response

    def _update_running_route_metadata(
        self,
        *,
        session_id: str,
        payload: Mapping[str, Any],
        hook: str,
    ) -> dict[str, Any]:
        current_metadata = session_metadata(self.ctx.store, session_id)
        updated_metadata = _apply_task_regime_escalation(
            current_metadata,
            payload=payload,
            hook=hook,
            root=self.ctx.root,
        )
        if updated_metadata != current_metadata:
            self.ctx.store.upsert_session_start(
                session_id=session_id,
                status="running",
                genome_path=self.ctx.genome.source_path,
                metadata=updated_metadata,
            )
        return updated_metadata

    def _session_start_completion_preview(
        self,
        *,
        runtime_mode: str,
        stop_trailer_marker: str,
        required_requirement_ids: list[str],
        task_regime: str,
        assurance_class: str,
    ) -> str:
        if runtime_mode not in {"assisted", "gemini_native", "native_preview"}:
            return ""

        hooks_cfg = self.ctx.genome.hooks
        challenge_categories = (
            [str(item).strip() for item in self.ctx.genome.challenges.active_categories if str(item).strip()]
            if self.ctx.genome.challenges.require_coverage
            else []
        )
        invariant_paths = (
            [str(item).strip() for item in self.ctx.genome.invariants.suite_paths if str(item).strip()]
            if self.ctx.genome.invariants.run_on_stop
            else []
        )
        stop_marker = stop_trailer_marker or "STOP_FIELDS_JSON"
        concise_native = runtime_mode in {"gemini_native", "native_preview"}
        low_friction = _is_low_friction_route_state(
            task_regime=task_regime,
            assurance_class=assurance_class,
        )

        lines = ["## Completion preview"]
        if concise_native:
            lines.append(
                f"- To finish, end with valid `{stop_marker}`."
                if low_friction
                else f"- End with `{stop_marker}`."
            )
        else:
            lines.append(f"- If you claim completion here, end with valid `{stop_marker}` on the final line.")
        if low_friction:
            if concise_native:
                lines.append("- Keep any `truth_claims` aligned with repo changes and commands run.")
            else:
                lines.append("- If you include `truth_claims`, keep them aligned with actual repo changes and commands run.")
            return "\n".join(lines).strip()
        if challenge_categories:
            if concise_native:
                lines.append("- `challenge_coverage`: " + _preview_item_list(challenge_categories, max_items=4) + ".")
            else:
                lines.append(
                    "- `challenge_coverage` must be category-specific for: "
                    + _preview_item_list(challenge_categories, max_items=4)
                    + "."
                )
        requirement_message = _requirement_completion_preview_line(
            required_requirement_ids=required_requirement_ids,
            require_requirement_audit=hooks_cfg.require_requirement_audit,
            fail_on_requirement_audit_gap=hooks_cfg.fail_on_requirement_audit_gap,
            require_evidence_for_passed_requirement=hooks_cfg.require_evidence_for_passed_requirement,
            concise=concise_native,
        )
        if requirement_message:
            lines.append("- " + requirement_message)
        if concise_native:
            lines.append(
                "- Evidence needs repo-relative refs or `cmd:`; pytest node ids and prose do not count."
            )
            if task_regime == "localized_edit":
                lines.append("- Do not broaden scope beyond declared task targets.")
            lines.append("- Keep `truth_claims` tied to repo changes or commands run.")
        else:
            lines.append("- If you include `truth_claims`, keep them aligned with actual repo changes and commands run.")
        if invariant_paths:
            if concise_native:
                lines.append(
                    "- Invariants: " + _preview_item_list(invariant_paths, max_items=2) + "; pass or end truthfully."
                )
            else:
                lines.append(
                    "- Invariants will run for: "
                    + _preview_item_list(invariant_paths, max_items=2)
                    + "; they must pass, or end truthfully if that gap remains real."
                )
        return "\n".join(lines).strip()

    def _session_start_evidence_expectation(
        self,
        *,
        runtime_mode: str,
        required_requirement_ids: list[str],
        task_regime: str,
        assurance_class: str,
    ) -> str:
        if runtime_mode != "assisted":
            return ""
        if _is_low_friction_route_state(
            task_regime=task_regime,
            assurance_class=assurance_class,
        ):
            return ""

        surfaces, requirement_surface_active = _session_start_evidence_surfaces(
            genome=self.ctx.genome,
            required_requirement_ids=required_requirement_ids,
        )

        message = (
            "Evidence expectation: for "
            + _preview_item_list(surfaces, max_items=3)
            + ", use repo-relative file refs (with or without line numbers) or `cmd:` markers."
            + " Prose-only summaries, pytest node ids, and other unverifiable narrative do not count."
        )
        if requirement_surface_active:
            message += " If something remains failed, use a real `gap` instead of pass-shaped evidence."
        return message

    def _ensure_session_started(self, *, session_id: str, hook: str, capture_git_snapshot: bool = True) -> None:
        if session_id in self._known_sessions:
            return
        metadata: dict[str, Any] = {"hook": hook, "auto_started": hook != "SessionStart"}
        if not session_metadata(self.ctx.store, session_id) and hook != "SessionStart" and capture_git_snapshot:
            metadata["git_snapshot"] = session_git_snapshot(self.ctx.root)
        self.ctx.store.ensure_session_start(
            session_id=session_id,
            status="running",
            genome_path=self.ctx.genome.source_path,
            metadata=metadata,
        )
        self._known_sessions.add(session_id)

    def _session_start_repomap(
        self,
        *,
        session_id: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        repomap_cfg = self.ctx.genome.repomap
        if not (repomap_cfg.enabled and repomap_cfg.run_on_session_start):
            return None

        focus_files = _as_string_list(payload.get("target_files"))
        try:
            from .repomap import run_repomap

            result = run_repomap(
                root=self.ctx.root,
                repomap_config=repomap_cfg,
                focus_files=focus_files or None,
                session_id=session_id,
                timeout_ms=repomap_cfg.session_start_timeout_ms,
            )
        except Exception as exc:  # noqa: BLE001
            summary = {
                "ok": False,
                "artifact_path": None,
                "method": "none",
                "scope": list(repomap_cfg.watch_paths),
                "stats": {
                    "files_parsed": 0,
                    "symbols_found": 0,
                    "graph_edges": 0,
                    "byte_count": 0,
                },
                "top_ranked_files": [],
                "error": {"code": "internal_error", "message": str(exc)},
                "warning": "Repo-map generation failed during session start (non-blocking).",
            }
            self._record_event(
                session_id,
                "RepoMap",
                {
                    "trigger": "SessionStart",
                    "ok": False,
                    "error": summary["error"],
                    "scope": summary["scope"],
                },
                status="error",
            )
            return summary

        artifact = result.artifact
        top_ranked_files = [entry.path for entry in artifact.ranking[:5]]
        summary = {
            "ok": bool(result.ok),
            "artifact_path": result.artifact_path,
            "method": str(artifact.provenance.get("method", "none")),
            "scope": list(artifact.provenance.get("scope", [])),
            "stats": dict(artifact.stats),
            "top_ranked_files": top_ranked_files,
        }
        event_payload: dict[str, Any] = {
            "trigger": "SessionStart",
            "ok": bool(result.ok),
            "artifact_path": result.artifact_path,
            "method": summary["method"],
            "scope": summary["scope"],
            "stats": summary["stats"],
            "top_ranked_files": top_ranked_files,
        }
        if not result.ok and artifact.error:
            error = {
                "code": str(artifact.error.get("code", "internal_error")),
                "message": str(artifact.error.get("message", "Repo-map generation failed")),
            }
            summary["error"] = error
            summary["warning"] = f"Repo-map warning: {error['message']}"
            event_payload["error"] = error

        self._record_event(
            session_id,
            "RepoMap",
            event_payload,
            status="ok" if result.ok else "error",
        )
        return summary

    def _response_path(self, path: Path) -> str:
        resolved = path.resolve()
        return str(resolved.relative_to(self.ctx.root)) if resolved.is_relative_to(self.ctx.root) else str(resolved)

    @staticmethod
    def _session_id(payload: Mapping[str, Any]) -> str: return (payload.get("session_id") or "").strip() if isinstance(payload.get("session_id"), str) and str(payload.get("session_id")).strip() else f"sess-{uuid4().hex[:12]}"

    def _foundation_warnings(self, *, session_id: str, target_files: list[str]) -> list[str]:
        return foundation_warnings_from_snapshot(foundation=self.foundation, snapshot=session_foundation_snapshot(self.ctx.store, session_id), target_files=target_files)

def _graveyard_context_block(matches: list[dict[str, Any]], config: Any) -> str:
    if not matches:
        return ""
    max_matches = max(1, int(getattr(config, "context_max_matches", 2)))
    summary_chars = max(40, int(getattr(config, "context_summary_chars", 140)))
    reason_chars = max(40, int(getattr(config, "context_reason_chars", 200)))
    token_budget = max(50, int(getattr(config, "context_max_tokens", 300)))

    lines = ["## Graveyard context"]
    used_tokens = _approx_tokens(lines[0])
    for idx, match in enumerate(matches[:max_matches], start=1):
        summary = _truncate_context_text(str(match.get("summary") or "").strip(), summary_chars)
        reason = _truncate_context_text(str(match.get("reason") or "").strip(), reason_chars)
        files = _as_string_list(match.get("files"))
        entry_lines = [f"{idx}. {summary}" if summary else f"{idx}. Prior failure pattern"]
        if reason:
            entry_lines.append(f"Reason: {reason}")
        if files:
            entry_lines.append("Files: " + ", ".join(files[:5]))
        entry_tokens = _approx_tokens("\n".join(entry_lines))
        if used_tokens + entry_tokens > token_budget:
            break
        lines.extend(entry_lines)
        used_tokens += entry_tokens
    return "\n".join(lines).strip() if len(lines) > 1 else ""


def _truncate_context_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max(1, max_chars - 3)].rstrip() + "..."


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _preview_item_list(values: list[str], *, max_items: int) -> str:
    unique = [str(item).strip() for item in values if str(item).strip()]
    if len(unique) <= max_items:
        return ", ".join(unique)
    remaining = len(unique) - max_items
    return ", ".join(unique[:max_items]) + f", +{remaining} more"


def _requirement_completion_preview_line(
    *,
    required_requirement_ids: list[str],
    require_requirement_audit: bool,
    fail_on_requirement_audit_gap: bool,
    require_evidence_for_passed_requirement: bool,
    concise: bool = False,
) -> str:
    if not required_requirement_ids and not (
        require_requirement_audit or fail_on_requirement_audit_gap or require_evidence_for_passed_requirement
    ):
        return ""

    if concise:
        opener = "Provide `requirement_audit`" if require_requirement_audit else "If used, `requirement_audit`"
    else:
        opener = "Provide `requirement_audit`" if require_requirement_audit else "If you include `requirement_audit`"
    clauses: list[str] = []
    if required_requirement_ids:
        label = "cover" if concise else "cover:"
        clauses.append(label + " " + ", ".join(str(item).strip() for item in required_requirement_ids if str(item).strip()))
    if require_evidence_for_passed_requirement:
        clauses.append("every `pass` item needs evidence" if not concise else "`pass` needs evidence")
    clauses.append("every `fail` item needs a real `gap`" if not concise else "`fail` needs real `gap`")
    return opener + "; " + "; ".join(clauses) + "."


def _session_start_evidence_surfaces(
    *,
    genome: CortexGenome,
    required_requirement_ids: list[str],
) -> tuple[list[str], bool]:
    surfaces: list[str] = []
    if genome.challenges.require_coverage:
        surfaces.append("`challenge_coverage`")
    hooks_cfg = genome.hooks
    requirement_surface_active = bool(required_requirement_ids) or (
        hooks_cfg.require_requirement_audit
        or hooks_cfg.fail_on_requirement_audit_gap
        or hooks_cfg.require_evidence_for_passed_requirement
    )
    if requirement_surface_active:
        surfaces.append("passed `requirement_audit.items`")
    surfaces.append("any `truth_claims`")
    return surfaces, requirement_surface_active
```

### `cortex/core_helpers.py`

```python
from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .store import SQLiteStore
from .utils import _as_string_list, _normalize_repo_relative_path, _unique_list


def extract_required_requirement_ids(payload: Mapping[str, Any]) -> list[str]:
    direct = _as_string_list(payload.get("required_requirement_ids"))
    if direct:
        return _unique_list(direct)
    contract = payload.get("task_contract")
    if isinstance(contract, Mapping):
        contract_ids = _as_string_list(contract.get("required_requirement_ids")) or _as_string_list(
            contract.get("required_ids")
        )
        if contract_ids:
            return _unique_list(contract_ids)
    return []


def session_metadata(store: SQLiteStore, session_id: str) -> dict[str, Any]:
    with store.connection() as conn:
        row = conn.execute(
            "SELECT metadata_json FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    if not row:
        return {}
    try:
        metadata = json.loads(row["metadata_json"])
    except (TypeError, ValueError):
        return {}
    return metadata if isinstance(metadata, dict) else {}


def session_required_requirement_ids(store: SQLiteStore, session_id: str) -> list[str]:
    return _unique_list(_as_string_list(session_metadata(store, session_id).get("required_requirement_ids")))


def session_foundation_snapshot(store: SQLiteStore, session_id: str) -> Mapping[str, Any] | None:
    foundation = session_metadata(store, session_id).get("foundation")
    return foundation if isinstance(foundation, Mapping) else None


def foundation_warnings_from_snapshot(
    *,
    foundation: Any,
    snapshot: Mapping[str, Any] | None,
    target_files: list[str],
) -> list[str]:
    if snapshot is None:
        return foundation.warnings_for_target_files(target_files)
    warnings = _as_string_list(snapshot.get("warnings"))
    findings_raw = snapshot.get("findings")
    if not isinstance(findings_raw, list):
        return warnings
    findings: dict[str, Mapping[str, Any]] = {}
    for raw in findings_raw:
        if not isinstance(raw, Mapping):
            continue
        path = str(raw.get("path") or "").strip()
        if path:
            findings[path] = raw
    if not findings:
        return warnings
    target_set = {foundation._norm_path(path) for path in target_files if path}
    for path in sorted(target_set):
        finding = findings.get(path)
        if not isinstance(finding, Mapping):
            continue
        level = str(finding.get("level") or "warn")
        try:
            churn_count = int(finding.get("churn_count") or 0)
        except (TypeError, ValueError):
            churn_count = 0
        warnings.append(
            f"Target file {path} is {level}-churn ({churn_count} touches in recent window)."
        )
    return warnings


def event_command_candidates(payload: Mapping[str, Any]) -> list[str]:
    commands: list[str] = []
    for key in ("command", "cmd"):
        commands.extend(_as_string_list(payload.get(key)))
    for container_key in ("input", "tool_input"):
        nested = payload.get(container_key)
        if isinstance(nested, Mapping):
            for key in ("command", "cmd"):
                commands.extend(_as_string_list(nested.get(key)))
    return _unique_list(commands)


def session_witness_context(store: SQLiteStore, session_id: str) -> dict[str, list[str]]:
    commands: list[str] = []
    tools: list[str] = []
    with store.connection() as conn:
        rows = conn.execute(
            """
            SELECT tool_name, payload_json
            FROM events
            WHERE session_id = ?
              AND hook IN ('PreToolUse', 'PostToolUse')
            ORDER BY id ASC
            """,
            (session_id,),
        ).fetchall()

    for row in rows:
        tool = str(row["tool_name"] or "").strip()
        if tool:
            tools.append(tool)
        try:
            payload = json.loads(row["payload_json"])
        except (TypeError, ValueError):
            continue
        if isinstance(payload, Mapping):
            commands.extend(event_command_candidates(payload))
    return {"commands": _unique_list(commands), "tools": _unique_list(tools)}


def session_git_snapshot(root: Path) -> dict[str, Any]:
    root_resolved = root.resolve()
    if not _has_enclosing_git_marker(root_resolved):
        return {
            "available": False,
            "changed_files": [],
            "error": "git repository marker not found",
        }
    try:
        proc = subprocess.run(
            ["git", "-C", str(root_resolved), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "changed_files": [], "error": f"git status failed: {exc}"}
    if proc.returncode != 0:
        reason = proc.stderr.strip() or proc.stdout.strip() or f"exit code {proc.returncode}"
        return {"available": False, "changed_files": [], "error": reason}

    changed_files: list[str] = []
    for line in proc.stdout.splitlines():
        if not line:
            continue
        path_field = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path_field:
            path_field = path_field.split(" -> ", 1)[1].strip()
        normalized = _normalize_repo_relative_path(path_field, root=root_resolved)
        if normalized:
            changed_files.append(normalized)
    return {
        "available": True,
        "changed_files": sorted(set(changed_files)),
        "error": None,
    }


def _has_enclosing_git_marker(root: Path) -> bool:
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


def session_changed_files_since_baseline(
    *,
    baseline_snapshot: Mapping[str, Any] | None,
    current_snapshot: Mapping[str, Any] | None,
) -> tuple[list[str] | None, str | None]:
    if not isinstance(baseline_snapshot, Mapping):
        return None, "session baseline snapshot unavailable"
    if not isinstance(current_snapshot, Mapping):
        return None, "current repository snapshot unavailable"

    if not bool(baseline_snapshot.get("available")):
        reason = str(baseline_snapshot.get("error") or "session baseline snapshot unavailable").strip()
        return None, reason
    if not bool(current_snapshot.get("available")):
        reason = str(current_snapshot.get("error") or "current repository snapshot unavailable").strip()
        return None, reason

    baseline_files = set(_as_string_list(baseline_snapshot.get("changed_files")))
    current_files = set(_as_string_list(current_snapshot.get("changed_files")))
    return sorted(current_files - baseline_files), None
```

### `cortex/blocklist.py`

```python
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_BLOCKED_TOOLS: frozenset[str] = frozenset({
    "vim",
    "nvim",
    "nano",
    "emacs",
    "vi",
    "python_repl",
    "ipython",
    "node_repl",
    "irb",
    "gdb",
    "lldb",
    "pdb",
    "less",
    "more",
    "man",
    "ssh",
    "docker_exec_interactive",
    "kubectl_exec",
})


@dataclass(slots=True)
class BlockVerdict:
    blocked: bool
    reason: str


def evaluate_blocklist(
    tool_name: object | None,
    *,
    enabled: bool = True,
    blocked_tools: frozenset[str] = DEFAULT_BLOCKED_TOOLS,
    allowed_tools: frozenset[str] = frozenset(),
    fail_closed: bool = False,
) -> BlockVerdict:
    if not enabled:
        return BlockVerdict(False, "blocklist_disabled")
    normalized = "" if tool_name is None else str(tool_name).strip().lower()
    normalized = normalized or "unknown"
    if normalized in allowed_tools:
        return BlockVerdict(False, "explicitly_allowed")
    if normalized in blocked_tools:
        return BlockVerdict(True, "tool_denied")
    if fail_closed and normalized not in allowed_tools:
        return BlockVerdict(True, "fail_closed")
    return BlockVerdict(False, "not_in_denylist")
```

### `cortex/foundation.py`

```python
from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable

from .genome import FoundationConfig


@dataclass(slots=True)
class FoundationFinding:
    path: str
    churn_count: int
    level: str

    def to_dict(self) -> dict[str, object]:
        return {"path": self.path, "churn_count": self.churn_count, "level": self.level}


@dataclass(slots=True)
class FoundationReport:
    generated_at: str
    enabled: bool
    git_available: bool
    watch_paths: list[str]
    warnings: list[str] = field(default_factory=list)
    findings: list[FoundationFinding] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "enabled": self.enabled,
            "git_available": self.git_available,
            "watch_paths": self.watch_paths,
            "warnings": self.warnings,
            "findings": [f.to_dict() for f in self.findings],
        }

    def by_path(self) -> dict[str, FoundationFinding]:
        return {finding.path: finding for finding in self.findings}


class FoundationAnalyzer:
    def __init__(self, repo_root: Path, config: FoundationConfig) -> None:
        self.repo_root = repo_root
        self.config = config

    def analyze(self) -> FoundationReport:
        now = datetime.now(timezone.utc).isoformat()
        if not self.config.enabled:
            return FoundationReport(
                generated_at=now,
                enabled=False,
                git_available=False,
                watch_paths=list(self.config.watch_paths),
                warnings=["Foundation analysis disabled in cortex.toml."],
            )

        git_repo, repo_warning = self._is_git_repo()
        if not git_repo:
            return FoundationReport(
                generated_at=now,
                enabled=True,
                git_available=False,
                watch_paths=list(self.config.watch_paths),
                warnings=[repo_warning or "Git repository not detected; skipping churn analysis."],
            )

        counts, git_available, churn_warning = self._collect_churn_counts()
        findings: list[FoundationFinding] = []
        warnings: list[str] = [churn_warning] if churn_warning else []
        for path, count in counts.most_common():
            level = ""
            if count >= self.config.stability_thresholds.high_churn_count:
                level = "high"
            elif count >= self.config.stability_thresholds.warn_churn_count:
                level = "warn"
            else:
                continue
            findings.append(FoundationFinding(path=path, churn_count=count, level=level))

        if findings:
            warnings.append(
                f"Foundation analysis found {len(findings)} churn-heavy files in watched paths."
            )

        return FoundationReport(
            generated_at=now,
            enabled=True,
            git_available=git_available,
            watch_paths=list(self.config.watch_paths),
            warnings=warnings,
            findings=findings,
        )

    def warnings_for_target_files(self, target_files: Iterable[str]) -> list[str]:
        report = self.analyze()
        if not report.findings:
            return report.warnings

        target_set = {self._norm_path(path) for path in target_files if path}
        if not target_set:
            return report.warnings

        findings = report.by_path()
        matched: list[str] = []
        for path in sorted(target_set):
            finding = findings.get(path)
            if finding is None:
                continue
            matched.append(
                f"Target file {path} is {finding.level}-churn ({finding.churn_count} touches in recent window)."
            )
        return report.warnings + matched

    def _is_git_repo(self) -> tuple[bool, str | None]:
        timeout_ms = self._git_timeout_millis()
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_ms / 1000.0,
            )
        except FileNotFoundError:
            return False, "Git binary not found; skipping churn analysis."
        except subprocess.TimeoutExpired:
            return (
                False,
                f"Git repository detection timed out after {timeout_ms}ms; skipping churn analysis.",
            )
        if result.returncode == 0 and result.stdout.strip() == "true":
            return True, None
        return False, "Git repository not detected; skipping churn analysis."

    def _collect_churn_counts(self) -> tuple[Counter[str], bool, str | None]:
        timeout_ms = self._git_timeout_millis()
        cmd = ["git", "log", "--name-only", "--pretty=format:", f"-n{self.config.churn_window_commits}"]
        cmd.extend(["--", *self.config.watch_paths])
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_ms / 1000.0,
            )
        except FileNotFoundError:
            return Counter(), False, "Git binary not found; skipping churn analysis."
        except subprocess.TimeoutExpired:
            return (
                Counter(),
                False,
                f"Git churn scan timed out after {timeout_ms}ms; skipping churn analysis.",
            )
        if result.returncode != 0:
            return Counter(), True, "Git churn scan failed; skipping churn analysis."

        counts: Counter[str] = Counter()
        for raw in result.stdout.splitlines():
            path = raw.strip()
            if not path:
                continue
            norm = self._norm_path(path)
            if self._ignored(norm):
                continue
            counts[norm] += 1
        return counts, True, None

    def _ignored(self, path: str) -> bool:
        parts = set(PurePosixPath(path).parts)
        return any(ignored in parts for ignored in self.config.ignored_dirs)

    @staticmethod
    def _norm_path(path: str) -> str:
        return str(PurePosixPath(path))

    def _git_timeout_millis(self) -> int:
        return max(1, int(self.config.git_timeout_ms))
```

### `cortex/challenges.py`

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .genome import ChallengesConfig
from .requirements import evaluate_evidence_reference
from .store import SQLiteStore
from .templates import BUILTIN_CHALLENGE_TEMPLATES
from .utils import _as_string_list


@dataclass(slots=True)
class ChallengeCoverage:
    category: str
    covered: bool
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"category": self.category, "covered": self.covered, "evidence": self.evidence}


@dataclass(slots=True)
class ChallengeReport:
    active_categories: list[str]
    custom_paths: list[str]
    results: list[ChallengeCoverage]
    missing_categories: list[str]
    unverified_categories: list[str]
    uncheckable_categories: list[str]
    diagnostics: list[dict[str, Any]]
    config_warnings: list[str]
    ok: bool
    gap_entries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_categories": self.active_categories,
            "custom_paths": self.custom_paths,
            "results": [r.to_dict() for r in self.results],
            "missing_categories": self.missing_categories,
            "unverified_categories": self.unverified_categories,
            "uncheckable_categories": self.uncheckable_categories,
            "diagnostics": self.diagnostics,
            "config_warnings": self.config_warnings,
            "ok": self.ok,
            "gap_entries": self.gap_entries,
        }


class ChallengeEnforcer:
    def __init__(self, store: SQLiteStore, config: ChallengesConfig) -> None:
        self.store = store
        self.config = config

    def evaluate(
        self,
        session_id: str,
        coverage_payload: Mapping[str, Any] | None = None,
        *,
        require_verifiable_coverage: bool = False,
        root: Path | None = None,
        witness: Mapping[str, list[str]] | None = None,
    ) -> ChallengeReport:
        coverage_payload = coverage_payload or {}
        results: list[ChallengeCoverage] = []
        missing: list[str] = []
        unverified: list[str] = []
        uncheckable: list[str] = []
        gap_entries: list[str] = []
        diagnostics: list[dict[str, Any]] = []
        config_warnings: list[str] = []
        resolved_root = root.resolve() if root is not None else None

        missing_builtin = [
            name for name in BUILTIN_CHALLENGE_TEMPLATES if name not in self.config.active_categories
        ]
        if missing_builtin:
            config_warnings.append(
                "Built-in challenge categories missing from active set: " + ", ".join(missing_builtin)
            )

        for category in self.config.active_categories:
            raw = coverage_payload.get(category)
            covered, evidence = self._coerce_coverage(raw)
            gap_kind = "missing" if raw is None else "uncovered"
            if require_verifiable_coverage and covered:
                verification = self._verify_covered_category(
                    evidence=evidence,
                    root=resolved_root,
                    witness=witness,
                )
                evidence["verification"] = verification
                verification_status = str(verification.get("status") or "")
                if verification_status != "verified":
                    covered = False
                    reason = str(verification.get("reason") or "missing verifiable evidence")
                    if verification_status == "uncheckable":
                        uncheckable.append(category)
                        gap_kind = "uncheckable"
                    else:
                        unverified.append(category)
                        gap_kind = "unverified"
                    config_warnings.append(
                        f"Challenge coverage '{category}' marked covered but evidence is {verification_status}: {reason}"
                    )
            if not covered:
                missing.append(category)
                gap_entries.append(f"{category}:{gap_kind}")
                diagnostics.append(
                    self._coverage_diagnostic(
                        category=category,
                        raw=raw,
                        evidence=evidence,
                        require_verifiable_coverage=require_verifiable_coverage,
                    )
                )
            result = ChallengeCoverage(category=category, covered=covered, evidence=evidence)
            results.append(result)
            self.store.record_challenge_result(session_id, category, covered, evidence)

        ok = not missing if self.config.require_coverage else True
        return ChallengeReport(
            active_categories=list(self.config.active_categories),
            custom_paths=list(self.config.custom_paths),
            results=results,
            missing_categories=missing,
            unverified_categories=sorted(set(unverified)),
            uncheckable_categories=sorted(set(uncheckable)),
            diagnostics=diagnostics,
            config_warnings=config_warnings,
            ok=ok,
            gap_entries=sorted(set(gap_entries)),
        )

    def missing_coverage_diagnostics(self) -> list[dict[str, Any]]:
        return [
            {
                "evidence_found": [],
                "evidence_expected": [f"challenge_coverage for: {', '.join(self.config.active_categories)}"],
                "gap_description": "No challenge_coverage was provided for the stop attempt.",
                "gap_characterization": "comprehension_gap",
                "distance_signal": "far",
                "gap_entries": ["__all__:missing"],
            }
        ]

    def invalid_coverage_diagnostics(self, raw: Any) -> list[dict[str, Any]]:
        return [
            {
                "evidence_found": [f"challenge_coverage={type(raw).__name__}"],
                "evidence_expected": ["challenge_coverage object keyed by active challenge categories"],
                "gap_description": "Challenge coverage used an invalid payload shape.",
                "gap_characterization": "comprehension_gap",
                "distance_signal": "far",
                "gap_entries": ["__all__:invalid_shape"],
            }
        ]

    @staticmethod
    def _coerce_coverage(raw: Any) -> tuple[bool, dict[str, Any]]:
        if isinstance(raw, bool):
            return raw, {}
        if isinstance(raw, Mapping):
            covered = bool(raw.get("covered", False))
            evidence = {str(k): v for k, v in raw.items() if str(k) != "covered"}
            return covered, evidence
        if raw is None:
            return False, {}
        return bool(raw), {"raw": raw}

    @staticmethod
    def _verify_covered_category(
        *,
        evidence: Mapping[str, Any],
        root: Path | None,
        witness: Mapping[str, list[str]] | None,
    ) -> dict[str, Any]:
        if root is None:
            return {
                "status": "uncheckable",
                "reason": "verification root unavailable",
                "checked_references": [],
            }

        references = _as_string_list(evidence.get("evidence"))
        if not references:
            return {
                "status": "unverified",
                "reason": "covered=true requires non-empty evidence list",
                "checked_references": [],
            }

        checks = [evaluate_evidence_reference(ref, root=root, witness=witness) for ref in references]
        if any(check.get("status") == "verified" for check in checks):
            return {
                "status": "verified",
                "reason": "",
                "checked_references": checks,
            }
        if any(check.get("status") == "uncheckable" for check in checks):
            return {
                "status": "uncheckable",
                "reason": "no verifiable evidence reference was checkable",
                "checked_references": checks,
            }
        return {
            "status": "unverified",
            "reason": "no evidence reference was verified",
            "checked_references": checks,
        }

    @staticmethod
    def _coverage_diagnostic(
        *,
        category: str,
        raw: Any,
        evidence: Mapping[str, Any],
        require_verifiable_coverage: bool,
    ) -> dict[str, Any]:
        verification = evidence.get("verification") if isinstance(evidence, Mapping) else None
        if raw is None:
            return {
                "evidence_found": [],
                "evidence_expected": [f"challenge_coverage.{category}=true"],
                "gap_description": f"Challenge category '{category}' was not addressed in stop coverage.",
                "gap_characterization": "comprehension_gap",
                "distance_signal": "far",
                "gap_entries": [f"{category}:missing"],
            }

        evidence_refs = _as_string_list(evidence.get("evidence")) if isinstance(evidence, Mapping) else []
        if require_verifiable_coverage and isinstance(verification, Mapping):
            status = str(verification.get("status") or "unverified")
            gap_kind = "uncheckable" if status == "uncheckable" else "unverified"
            return {
                "evidence_found": evidence_refs or [f"verification_status={status}"],
                "evidence_expected": [f"verifiable evidence for challenge '{category}'"],
                "gap_description": f"Challenge category '{category}' was claimed but not verifiably supported.",
                "gap_characterization": "execution_gap",
                "distance_signal": "moderate" if evidence_refs else "far",
                "gap_entries": [f"{category}:{gap_kind}"],
            }

        return {
            "evidence_found": ["covered=false"],
            "evidence_expected": [f"challenge_coverage.{category}=true"],
            "gap_description": f"Challenge category '{category}' remains uncovered.",
            "gap_characterization": "comprehension_gap",
            "distance_signal": "moderate",
            "gap_entries": [f"{category}:uncovered"],
        }
```

### `cortex/requirements.py`

```python
from __future__ import annotations

import re
import shlex
from collections.abc import Mapping
from pathlib import Path
from typing import Any, NamedTuple

from .utils import _as_string_list, _normalize_repo_relative_path, _unique_list


class RequirementAuditEvaluation(NamedTuple):
    report: dict[str, Any] | None
    details: dict[str, Any] | None
    gap: bool
    missing: bool
    diagnostics: list[dict[str, Any]]
    warnings: list[str]


class TruthClaimsEvaluation(NamedTuple):
    report: dict[str, Any] | None
    gap: bool
    diagnostics: list[dict[str, Any]]
    warnings: list[str]


def evaluate_requirement_audit_payload(
    payload: Any,
    *,
    require_requirement_audit: bool,
    require_evidence_for_passed_requirement: bool,
    required_requirement_ids: list[str],
    root: Path,
    witness: Mapping[str, list[str]] | None = None,
) -> RequirementAuditEvaluation:
    if payload is None:
        if require_requirement_audit:
            return RequirementAuditEvaluation(
                report=None,
                details={
                    "ok": False,
                    "gap_entries": [f"{item_id}:missing" for item_id in required_requirement_ids]
                    or ["__audit__:missing"],
                },
                gap=False,
                missing=True,
                diagnostics=[_diagnostic([], ["requirement_audit with items covering required requirements"], "No requirement_audit was provided for a required requirement gate.", "comprehension_gap", "far")],
                warnings=[
                    "No requirement_audit provided in Stop payload. Include requirement_audit to prove "
                    "prompt requirement coverage with evidence."
                ],
            )
        return RequirementAuditEvaluation(
            report=None,
            details=None,
            gap=False,
            missing=False,
            diagnostics=[],
            warnings=[],
        )

    details = validate_requirement_audit(
        payload,
        require_evidence_for_passed_requirement=require_evidence_for_passed_requirement,
        required_requirement_ids=required_requirement_ids,
        root=root,
        witness=witness,
    )
    warnings: list[str] = []
    gap = not details["ok"]
    if gap:
        warnings.append("Requirement audit reported gaps: " + "; ".join(details.get("errors", [])))
    warnings.extend(f"Requirement audit note: {note}" for note in details.get("warnings", []))
    return RequirementAuditEvaluation(
        report=minimal_requirement_audit_report(details),
        details=details,
        gap=gap,
        missing=False,
        diagnostics=[dict(item) for item in details.get("diagnostics", [])],
        warnings=warnings,
    )


def evaluate_truth_claims_payload(
    payload: Any,
    *,
    root: Path,
    witness: Mapping[str, list[str]] | None = None,
    observed_modified_files: list[str] | None = None,
    modified_files_error: str | None = None,
) -> TruthClaimsEvaluation:
    if payload is None:
        return TruthClaimsEvaluation(report=None, gap=False, diagnostics=[], warnings=[])

    if not isinstance(payload, Mapping):
        report = {
            "ok": False,
            "modified_files_claimed": [],
            "modified_files_verified": [],
            "modified_files_unverified": [],
            "modified_files_uncheckable": [],
            "tests_ran_claimed": [],
            "tests_ran_verified": [],
            "tests_ran_unverified": [],
            "tests_ran_uncheckable": [],
            "gap_entries": ["__truth_claims__:invalid_shape"],
            "errors": ["Invalid truth_claims format; expected an object."],
            "warnings": [],
        }
        return TruthClaimsEvaluation(
            report=report,
            gap=True,
            diagnostics=[_diagnostic(["truth_claims payload with invalid shape"], ["truth_claims object"], "Truth claims used an invalid payload shape.", "comprehension_gap", "far")],
            warnings=["Truth claims reported gaps: Invalid truth_claims format; expected an object."],
        )

    modified_claims = _normalize_modified_file_claims(payload.get("modified_files"), root=root.resolve())
    tests_ran_claims = _unique_list(
        [normalized for value in _as_string_list(payload.get("tests_ran")) if (normalized := _normalize_command(value))]
    )
    report_warnings: list[str] = []
    errors: list[str] = []
    diagnostics: list[dict[str, Any]] = []
    gap_entries: set[str] = set()

    modified_verified: list[str] = []
    modified_unverified: list[str] = []
    modified_uncheckable: list[str] = []
    tests_ran_verified: list[str] = []
    tests_ran_unverified: list[str] = []
    tests_ran_uncheckable: list[str] = []

    if not modified_claims and not tests_ran_claims:
        report_warnings.append(
            "truth_claims provided with no supported claims; expected modified_files and/or tests_ran."
        )

    if modified_claims:
        changed_files = set(_as_string_list(observed_modified_files)) if observed_modified_files is not None else None
        if changed_files is None:
            modified_uncheckable = list(modified_claims)
            error_reason = str(modified_files_error or "").strip()
            report_warnings.append(
                "truth_claims.modified_files are uncheckable: "
                + (error_reason or "session-scoped modified-files evidence unavailable")
            )
        else:
            for claimed_path in modified_claims:
                if claimed_path in changed_files:
                    modified_verified.append(claimed_path)
                else:
                    modified_unverified.append(claimed_path)
            if modified_unverified:
                errors.append(
                    "truth_claims.modified_files not observed in repository changes: "
                    + ", ".join(modified_unverified)
                )
                gap_entries.update(f"modified_files:{claimed_path}:unverified" for claimed_path in modified_unverified)
                diagnostics.append(_diagnostic(modified_unverified, modified_claims, "Some claimed modified files were not observed in the session-scoped file delta.", "execution_gap", "moderate"))

    if tests_ran_claims:
        observed_commands = _unique_list(
            [
                normalized
                for value in _as_string_list((witness or {}).get("commands"))
                if (normalized := _normalize_command(value))
            ]
        )
        if not observed_commands:
            tests_ran_uncheckable = list(tests_ran_claims)
            report_warnings.append("truth_claims.tests_ran are uncheckable: no observed command events in session")
        else:
            for claim in tests_ran_claims:
                if any(_command_claim_matches(claim, observed) for observed in observed_commands):
                    tests_ran_verified.append(claim)
                else:
                    tests_ran_unverified.append(claim)
            if tests_ran_unverified:
                errors.append(
                    "truth_claims.tests_ran not witnessed in session events: " + ", ".join(tests_ran_unverified)
                )
                gap_entries.update(
                    f"tests_ran:{_truth_claim_command_identity(claim)}:unverified"
                    for claim in tests_ran_unverified
                )
                diagnostics.append(_diagnostic(tests_ran_verified, tests_ran_claims, "Some claimed test commands were not witnessed in session events.", "execution_gap", "moderate"))

    report = {
        "ok": len(errors) == 0,
        "modified_files_claimed": modified_claims,
        "modified_files_verified": modified_verified,
        "modified_files_unverified": modified_unverified,
        "modified_files_uncheckable": modified_uncheckable,
        "tests_ran_claimed": tests_ran_claims,
        "tests_ran_verified": tests_ran_verified,
        "tests_ran_unverified": tests_ran_unverified,
        "tests_ran_uncheckable": tests_ran_uncheckable,
        "gap_entries": sorted(gap_entries) if errors else [],
        "diagnostics": diagnostics,
        "errors": errors,
        "warnings": report_warnings,
    }
    warnings: list[str] = []
    if errors:
        warnings.append("Truth claims reported gaps: " + "; ".join(errors))
    warnings.extend(f"Truth claims note: {warning}" for warning in report_warnings)
    return TruthClaimsEvaluation(
        report=report,
        gap=bool(errors),
        diagnostics=diagnostics,
        warnings=warnings,
    )


def minimal_requirement_audit_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": bool(report.get("ok")),
        "errors": [str(v) for v in _as_string_list(report.get("errors"))],
        "gap_entries": [str(v) for v in _as_string_list(report.get("gap_entries"))],
        "missing_required_ids": [str(v) for v in _as_string_list(report.get("missing_required_ids"))],
        "item_count": int(report.get("item_count") or 0),
        "pass_count": int(report.get("pass_count") or 0),
        "fail_count": int(report.get("fail_count") or 0),
        "diagnostics": [dict(item) for item in report.get("diagnostics", []) if isinstance(item, Mapping)],
    }


def _diagnostic(
    evidence_found: list[str],
    evidence_expected: list[str],
    gap_description: str,
    gap_characterization: str,
    distance_signal: str,
) -> dict[str, Any]:
    return {
        "evidence_found": [str(item) for item in evidence_found if str(item).strip()],
        "evidence_expected": [str(item) for item in evidence_expected if str(item).strip()],
        "gap_description": gap_description,
        "gap_characterization": gap_characterization,
        "distance_signal": distance_signal,
    }


def evaluate_evidence_reference(
    reference: str,
    *,
    root: Path,
    witness: Mapping[str, list[str]] | None = None,
) -> dict[str, str]:
    observed_commands = [_normalize_command(v) for v in _as_string_list((witness or {}).get("commands"))]
    observed_tools = {v.lower() for v in _as_string_list((witness or {}).get("tools"))}
    return _evaluate_evidence_reference(
        reference,
        root=root,
        observed_commands=observed_commands,
        observed_tools=observed_tools,
    )


def validate_requirement_audit(
    payload: Any,
    *,
    require_evidence_for_passed_requirement: bool,
    required_requirement_ids: list[str],
    root: Path,
    witness: Mapping[str, list[str]] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    diagnostics: list[dict[str, Any]] = []
    gap_entries: set[str] = set()
    pass_count = 0
    fail_count = 0
    unique_ids: set[str] = set()
    missing_required_ids: list[str] = []
    observed_commands = [_normalize_command(v) for v in _as_string_list((witness or {}).get("commands"))]
    observed_tools = {v.lower() for v in _as_string_list((witness or {}).get("tools"))}

    if not isinstance(payload, Mapping):
        return {
            "ok": False,
            "item_count": 0,
            "pass_count": 0,
            "fail_count": 0,
            "missing_required_ids": list(required_requirement_ids),
            "gap_entries": ["__audit__:invalid_shape", *(f"{item_id}:missing" for item_id in required_requirement_ids)],
            "diagnostics": [_diagnostic(["requirement_audit payload with invalid shape"], ["requirement_audit object with items"], "Requirement audit used an invalid payload shape.", "comprehension_gap", "far")],
            "warnings": [],
            "errors": ["Invalid requirement_audit format; expected an object."],
        }

    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    if not items:
        errors.append("requirement_audit.items must be a non-empty list.")
        gap_entries.add("__audit__:missing")
        diagnostics.append(_diagnostic([], ["requirement_audit.items with at least one requirement entry"], "Requirement audit did not provide any requirement items.", "comprehension_gap", "far"))

    for idx, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"requirement_audit.items[{idx}] must be an object.")
            gap_entries.add(f"__item_{idx}__:invalid_shape")
            diagnostics.append(_diagnostic([f"items[{idx}]={type(item).__name__}"], [f"items[{idx}] as requirement object"], "Requirement audit item used an invalid shape.", "comprehension_gap", "far"))
            continue
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            errors.append(f"requirement_audit.items[{idx}] is missing a non-empty id.")
            gap_entries.add(f"__item_{idx}__:missing")
            diagnostics.append(_diagnostic([f"items[{idx}] without id"], [f"items[{idx}].id"], "Requirement audit item is missing its requirement id.", "comprehension_gap", "far"))
            continue
        if item_id in unique_ids:
            errors.append(f"requirement_audit.items[{idx}] has duplicate id '{item_id}'.")
            gap_entries.add(f"{item_id}:duplicate_id")
            diagnostics.append(_diagnostic([item_id], ["unique requirement ids"], f"Requirement '{item_id}' was reported more than once.", "comprehension_gap", "moderate"))
        unique_ids.add(item_id)

        status = str(item.get("status") or "").strip().lower()
        if status == "pass":
            pass_count += 1
            evidence = _as_string_list(item.get("evidence"))
            if require_evidence_for_passed_requirement and not evidence:
                errors.append(f"requirement '{item_id}' is pass but has no evidence.")
                gap_entries.add(f"{item_id}:evidence_missing")
                diagnostics.append(_diagnostic([f"requirement '{item_id}' marked pass without evidence"], [f"verified evidence for requirement '{item_id}'"], f"Requirement '{item_id}' was marked pass without evidence.", "execution_gap", "close"))
            for evidence_ref in evidence:
                check = _evaluate_evidence_reference(
                    evidence_ref,
                    root=root,
                    observed_commands=observed_commands,
                    observed_tools=observed_tools,
                )
                if check["status"] == "unverified":
                    errors.append(f"requirement '{item_id}' evidence is unverified: {check['reason']}")
                    gap_entries.add(f"{item_id}:evidence_unverified")
                    diagnostics.append(_diagnostic([evidence_ref], [f"verified evidence for requirement '{item_id}'"], f"Requirement '{item_id}' evidence could not be verified.", "execution_gap", "moderate"))
                elif check["status"] == "uncheckable":
                    warnings.append(f"requirement '{item_id}' evidence is uncheckable: {check['reason']}")
        elif status == "fail":
            fail_count += 1
            gap_entries.add(f"{item_id}:fail_declared")
            if not str(item.get("gap") or "").strip():
                errors.append(f"requirement '{item_id}' is fail but has no gap description.")
                gap_entries.add(f"{item_id}:gap_missing")
                diagnostics.append(_diagnostic([f"requirement '{item_id}' marked fail"], [f"gap description for requirement '{item_id}'"], f"Requirement '{item_id}' failed without describing the gap.", "execution_gap", "close"))
        else:
            errors.append(f"requirement '{item_id}' has invalid status '{status}' (expected pass|fail).")
            gap_entries.add(f"{item_id}:status_invalid")
            diagnostics.append(_diagnostic([f"requirement '{item_id}' status={status or 'missing'}"], ["status=pass|fail"], f"Requirement '{item_id}' used an invalid status value.", "comprehension_gap", "far"))

    if required_requirement_ids:
        missing_required_ids = [rid for rid in required_requirement_ids if rid not in unique_ids]
        if missing_required_ids:
            errors.append("requirement_audit missing required ids: " + ", ".join(missing_required_ids))
            gap_entries.update(f"{item_id}:missing" for item_id in missing_required_ids)
            diagnostics.append(_diagnostic(sorted(unique_ids), required_requirement_ids, "Requirement audit omitted required requirement ids from the session contract.", "comprehension_gap", "moderate"))

    expected_verdict = "pass" if (items and fail_count == 0 and not errors) else "fail"
    completeness_verdict = payload.get("completeness_verdict")
    if completeness_verdict is not None:
        normalized_verdict = str(completeness_verdict).strip().lower()
        if normalized_verdict not in {"pass", "fail"}:
            errors.append("requirement_audit.completeness_verdict must be 'pass' or 'fail'.")
            gap_entries.add("__audit__:incomplete")
            diagnostics.append(_diagnostic([f"completeness_verdict={normalized_verdict}"], ["completeness_verdict=pass|fail"], "Requirement audit used an invalid completeness verdict value.", "comprehension_gap", "far"))
        elif normalized_verdict != expected_verdict:
            errors.append(
                f"requirement_audit.completeness_verdict={normalized_verdict} "
                f"does not match computed verdict={expected_verdict}."
            )
            gap_entries.add("__audit__:incomplete")
            diagnostics.append(_diagnostic([f"completeness_verdict={normalized_verdict}"], [f"completeness_verdict={expected_verdict}"], "Requirement audit completeness verdict did not match the computed result.", "execution_gap", "close"))

    return {
        "ok": len(errors) == 0 and fail_count == 0,
        "item_count": len(items),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "missing_required_ids": missing_required_ids,
        "gap_entries": sorted(gap_entries),
        "diagnostics": diagnostics,
        "warnings": warnings,
        "errors": errors,
    }


def _evaluate_evidence_reference(
    reference: str,
    *,
    root: Path,
    observed_commands: list[str],
    observed_tools: set[str],
) -> dict[str, str]:
    kind, claim = _classify_evidence_reference(reference, root=root)
    if kind == "path":
        path = _evidence_reference_path(reference, root)
        if path is not None and path.exists():
            return {"kind": "path", "status": "verified", "reason": "path exists"}
        return {
            "kind": "path",
            "status": "unverified",
            "reason": f"path does not exist: {path}",
        }

    if kind == "tool":
        if not observed_tools:
            return {"kind": "tool", "status": "uncheckable", "reason": "no observed tool events in session"}
        if claim in observed_tools:
            return {"kind": "tool", "status": "verified", "reason": f"tool observed: {claim}"}
        return {"kind": "tool", "status": "unverified", "reason": f"tool not observed: {claim}"}

    if kind == "command":
        if not observed_commands:
            return {
                "kind": "command",
                "status": "uncheckable",
                "reason": "no observed command events in session",
            }
        if claim and any(_command_claim_matches(claim, cmd) for cmd in observed_commands):
            return {"kind": "command", "status": "verified", "reason": "command matched session witness"}
        return {
            "kind": "command",
            "status": "unverified",
            "reason": "command not witnessed in session events",
        }

    return {"kind": "note", "status": "uncheckable", "reason": "reference is non-verifiable note text"}


def _classify_evidence_reference(reference: str, *, root: Path) -> tuple[str, str]:
    text = str(reference).strip()
    lower = text.lower()
    if lower.startswith("tool:"):
        return "tool", lower.split(":", 1)[1].strip()
    if lower.startswith("cmd:"):
        return "command", _normalize_command(text.split(":", 1)[1].strip())
    if _looks_like_command(text):
        return "command", _normalize_command(text)
    if _evidence_reference_path(text, root) is not None:
        return "path", text
    return "note", ""


def _evidence_reference_path(reference: str, root: Path) -> Path | None:
    text = str(reference).strip()
    if not text or text.startswith(("http://", "https://")):
        return None

    path_text = text.split("#", 1)[0].strip()
    if " " in path_text:
        first_token = path_text.split(None, 1)[0].strip()
        if first_token and (
            any(sep in first_token for sep in ("/", "\\"))
            or first_token.startswith((".", "~"))
        ):
            path_text = first_token
    path_text = re.sub(r":\d+(?::\d+|-\d+)?$", "", path_text).strip()
    path_text = path_text.rstrip(".,;:")
    if not path_text:
        return None
    if not any(sep in path_text for sep in ("/", "\\")) and not path_text.startswith((".", "~")):
        return None

    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _looks_like_command(text: str) -> bool:
    return bool(
        re.search(
            r"\b(pytest|npm|pnpm|yarn|npx|ruff|mypy|go test|cargo test|python\s+-m)\b",
            text.lower(),
        )
    )


def _normalize_command(text: str) -> str:
    value = text.strip().strip("`").lower()
    value = re.sub(r"[.,;:!?]+$", "", value).strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[:\-]\s*(ok|pass|passed|success|succeeded)$", "", value).strip()
    return value


def _command_claim_matches(claim: str, observed: str) -> bool:
    claim_tokens = _command_tokens(claim)
    observed_tokens = _command_tokens(observed)
    if not claim_tokens or not observed_tokens:
        return False
    return claim_tokens == observed_tokens or (
        len(claim_tokens) <= len(observed_tokens) and observed_tokens[: len(claim_tokens)] == claim_tokens
    )


def _command_tokens(command: str) -> tuple[str, ...]:
    normalized = _normalize_command(command)
    if not normalized:
        return ()
    try:
        raw_tokens = shlex.split(normalized)
    except ValueError:
        raw_tokens = normalized.split()
    tokens = [token.strip().lower() for token in raw_tokens if token.strip()]
    if not tokens:
        return ()

    while True:
        if len(tokens) >= 3 and tokens[0] in {"bash", "sh"} and tokens[1] == "-lc":
            return _command_tokens(" ".join(tokens[2:]))
        if len(tokens) >= 2 and tuple(tokens[:2]) in {("uv", "run"), ("poetry", "run"), ("pipenv", "run")}:
            tokens = tokens[2:]
            continue
        if len(tokens) >= 3 and tokens[0] in {"python", "python3", "py"} and tokens[1:3] == ["-m", "pytest"]:
            tokens = ["pytest", *tokens[3:]]
            continue
        break

    return tuple(tokens)


def _truth_claim_command_identity(command: str) -> str:
    tokens = _command_tokens(command)
    if not tokens:
        return "command"
    if "pytest" in tokens:
        return "pytest"
    if "unittest" in tokens:
        return "unittest"
    if tokens[0] in {"npm", "pnpm", "yarn", "bun"} and len(tokens) >= 2:
        return f"{tokens[0]} {tokens[1]}"
    return tokens[0]


def _normalize_modified_file_claims(value: Any, *, root: Path) -> list[str]:
    return _unique_list(
        [normalized for raw in _as_string_list(value) if (normalized := _normalize_repo_relative_path(raw, root=root))]
    )
```

### `cortex/invariants.py`

```python
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .genome import HooksConfig, InvariantsConfig
from .store import SQLiteStore


@dataclass(slots=True)
class InvariantCaseResult:
    test_path: str
    status: str
    duration_ms: int
    stdout: str
    stderr: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_path": self.test_path,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(slots=True)
class InvariantReport:
    configured_paths: list[str]
    results: list[InvariantCaseResult] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    ok: bool = True
    had_errors: bool = False
    recommend_revert: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "configured_paths": self.configured_paths,
            "results": [r.to_dict() for r in self.results],
            "diagnostics": self.diagnostics,
            "ok": self.ok,
            "had_errors": self.had_errors,
            "recommend_revert": self.recommend_revert,
        }


class InvariantRunner:
    def __init__(
        self,
        repo_root: Path,
        store: SQLiteStore,
        config: InvariantsConfig,
        hooks_config: HooksConfig,
        *,
        trust_profile: str = "trusted",
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.store = store
        self.config = config
        self.hooks_config = hooks_config
        self.trust_profile = trust_profile if trust_profile in {"trusted", "untrusted"} else "untrusted"

    def run(self, session_id: str, extra_pytest_args: Iterable[str] | None = None) -> InvariantReport:
        report = InvariantReport(configured_paths=list(self.config.suite_paths))
        args = list(extra_pytest_args or [])
        if self.trust_profile == "untrusted" and self.config.execution_mode == "host":
            result = InvariantCaseResult(
                test_path="__policy__",
                status="error",
                duration_ms=0,
                stdout="",
                stderr=(
                    "Host invariant execution is blocked for trust_profile='untrusted'. "
                    "Set [invariants].execution_mode='container' or [project].trust_profile='trusted'."
                ),
            )
            report.results.append(result)
            report.diagnostics.append(_invariant_diagnostic(result))
            report.ok = False
            report.had_errors = True
            self.store.record_invariant_result(
                session_id=session_id,
                test_path=result.test_path,
                status=result.status,
                duration_ms=result.duration_ms,
                stdout=result.stdout,
                stderr=result.stderr,
            )
            report.recommend_revert = self.hooks_config.recommend_revert_on_invariant_failure
            return report

        for suite_path in self.config.suite_paths:
            result = self._run_one(session_id=session_id, suite_path=suite_path, extra_args=args)
            report.results.append(result)
            if result.status in {"fail", "error", "missing"}:
                report.diagnostics.append(_invariant_diagnostic(result))
            self.store.record_invariant_result(
                session_id=session_id,
                test_path=result.test_path,
                status=result.status,
                duration_ms=result.duration_ms,
                stdout=result.stdout,
                stderr=result.stderr,
            )
            if result.status in {"fail", "error", "missing"}:
                report.ok = False
            if result.status == "error":
                report.had_errors = True

        if not report.ok:
            report.recommend_revert = self.hooks_config.recommend_revert_on_invariant_failure
        return report

    def promote_session_test(self, session_id: str, source_path: str | Path) -> Path:
        source = (self.repo_root / source_path).resolve() if not Path(source_path).is_absolute() else Path(source_path)
        target_dir = self.repo_root / self.config.graduation.target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        shutil.copy2(source, target)
        self.store.record_invariant_result(
            session_id=session_id,
            test_path=str(target.relative_to(self.repo_root)),
            status="graduated",
            duration_ms=0,
            stdout="",
            stderr="",
            graduated_from=str(source),
        )
        return target

    def _run_one(self, *, session_id: str, suite_path: str, extra_args: list[str]) -> InvariantCaseResult:
        path = self.repo_root / suite_path
        if not path.exists():
            return InvariantCaseResult(
                test_path=suite_path,
                status="missing",
                duration_ms=0,
                stdout="",
                stderr=f"Invariant path not found: {suite_path}",
            )

        started = time.perf_counter()
        try:
            cmd = self._pytest_command(path=path, suite_path=suite_path, extra_args=extra_args, session_id=session_id)
        except ValueError as exc:
            return InvariantCaseResult(
                test_path=suite_path,
                status="error",
                duration_ms=int((time.perf_counter() - started) * 1000),
                stdout="",
                stderr=str(exc),
            )
        env = None
        if self.config.execution_mode != "container":
            env = os.environ.copy()
            env["CORTEX_SESSION_ID"] = str(session_id)
            env["CORTEX_PROJECT_ROOT"] = str(self.repo_root)
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            return InvariantCaseResult(
                test_path=suite_path,
                status="error",
                duration_ms=int((time.perf_counter() - started) * 1000),
                stdout="",
                stderr=str(exc),
            )

        duration_ms = int((time.perf_counter() - started) * 1000)
        status = "pass" if proc.returncode == 0 else "fail"
        return InvariantCaseResult(
            test_path=suite_path,
            status=status,
            duration_ms=duration_ms,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
        )

    def _pytest_command(
        self,
        *,
        path: Path,
        suite_path: str,
        extra_args: list[str],
        session_id: str,
    ) -> list[str]:
        if self.config.execution_mode != "container":
            return self._host_pytest_command(path=path, extra_args=extra_args)
        target = self._container_suite_path(path, suite_path)
        return [
            self.config.container_engine,
            "run",
            "--rm",
            "-e",
            f"CORTEX_SESSION_ID={session_id}",
            "-e",
            f"CORTEX_PROJECT_ROOT={self.config.container_workdir}",
            "-v",
            f"{self.repo_root}:{self.config.container_workdir}",
            "-w",
            self.config.container_workdir,
            self.config.container_image,
            "python",
            "-m",
            "pytest",
            target,
            *extra_args,
        ]

    def _host_pytest_command(self, *, path: Path, extra_args: list[str]) -> list[str]:
        configured = str(self.config.pytest_bin).strip() or "pytest"
        configured_path = Path(configured).expanduser()
        if configured_path.is_absolute() and configured_path.exists():
            return [str(configured_path), str(path), *extra_args]
        if any(sep in configured for sep in ("/", "\\")):
            repo_relative = (self.repo_root / configured_path).resolve()
            if repo_relative.exists():
                return [str(repo_relative), str(path), *extra_args]
            if configured_path.exists():
                return [str(configured_path.resolve()), str(path), *extra_args]
        elif shutil.which(configured):
            return [configured, str(path), *extra_args]
        if importlib.util.find_spec("pytest") is not None:
            return [sys.executable, "-m", "pytest", str(path), *extra_args]
        raise ValueError(
            f"Configured pytest_bin '{configured}' is unavailable and fallback 'python -m pytest' is not installed."
        )

    def _container_suite_path(self, path: Path, suite_path: str) -> str:
        try:
            return str(path.resolve().relative_to(self.repo_root))
        except ValueError as exc:
            raise ValueError(
                f"Container invariant path is outside repo root: {path.resolve()} (root: {self.repo_root})"
            ) from exc


def _invariant_diagnostic(result: InvariantCaseResult) -> dict[str, Any]:
    if result.status == "missing":
        return {"evidence_found": [result.test_path], "evidence_expected": ["configured invariant test path to exist"], "gap_description": f"Invariant path '{result.test_path}' was missing.", "gap_characterization": "comprehension_gap", "distance_signal": "far"}
    if result.status == "error":
        return {"evidence_found": [result.stderr[:200]] if result.stderr else [result.test_path], "evidence_expected": [f"invariant '{result.test_path}' to run successfully"], "gap_description": f"Invariant '{result.test_path}' could not execute cleanly.", "gap_characterization": "execution_gap", "distance_signal": "moderate"}
    return {"evidence_found": [result.test_path], "evidence_expected": [f"invariant '{result.test_path}' to pass"], "gap_description": f"Invariant '{result.test_path}' failed.", "gap_characterization": "execution_gap", "distance_signal": "close"}
```

### `cortex/stop_payload.py`

```python
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

STOP_FIELD_KEYS = (
    "challenge_coverage",
    "requirement_audit",
    "truth_claims",
    "required_requirement_ids",
    "failed_approach",
    "stuck_declaration",
)


def extract_stop_fields(
    payload: Mapping[str, Any], *, allow_message_fallback: bool = True
) -> tuple[dict[str, Any] | None, str | None, list[str], int]:
    warnings: list[str] = []

    raw = payload.get("stop_fields")
    if isinstance(raw, Mapping):
        normalized, normalization_count = _canonicalize_map_keys(raw)
        return normalized, "payload.stop_fields", warnings, normalization_count
    if raw is not None:
        warnings.append("Ignoring invalid stop_fields field; expected an object.")

    if not allow_message_fallback:
        return None, None, warnings, 0
    if any(payload.get(key) is not None for key in STOP_FIELD_KEYS):
        return None, None, warnings, 0

    last_message = payload.get("last_assistant_message")
    if isinstance(last_message, str):
        parsed, marker_found, error = parse_stop_fields_json(last_message)
        if parsed is not None:
            normalized, normalization_count = _canonicalize_map_keys(parsed)
            return normalized, "last_assistant_message", warnings, normalization_count
        if marker_found and error:
            warnings.append(f"Ignoring invalid STOP_FIELDS_JSON trailer: {error}")

    return None, None, warnings, 0


def resolve_stop_value(
    *,
    key: str,
    payload: Mapping[str, Any],
    stop_fields: dict[str, Any] | None,
    stop_fields_source: str | None,
    warnings: list[str],
    value_label: str,
) -> Any:
    value = payload.get(key)
    if value is not None or not (stop_fields and key in stop_fields):
        return value
    value = stop_fields[key]
    if stop_fields_source == "last_assistant_message":
        warnings.append(f"Using {value_label} parsed from last assistant message (STOP_FIELDS_JSON).")
    elif stop_fields_source == "payload.stop_fields":
        warnings.append(f"Using {value_label} from payload.stop_fields.")
    return value


def parse_stop_fields_json(text: str) -> tuple[dict[str, Any] | None, bool, str | None]:
    for pattern in (
        r"```(?:stop-fields|stop_fields)\s*(\{.*?\})\s*```",
        r"```json\s*(\{.*?\"challenge_coverage\".*?\})\s*```",
    ):
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            continue
        try:
            parsed = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            return None, True, str(exc)
        if not isinstance(parsed, dict):
            return None, True, "expected a JSON object"
        return parsed, True, None

    marker = "STOP_FIELDS_JSON:"
    idx = text.rfind(marker)
    if idx == -1:
        return None, False, None
    decoder = json.JSONDecoder()
    try:
        parsed, _ = decoder.raw_decode(text[idx + len(marker) :].lstrip())
    except json.JSONDecodeError as exc:
        return None, True, str(exc)
    if not isinstance(parsed, dict):
        return None, True, "expected a JSON object"
    return parsed, True, None


def _canonicalize_map_keys(value: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    normalized: dict[str, Any] = {}
    normalization_count = 0
    for raw_key, raw_value in value.items():
        key = str(raw_key)
        canonical_key = key.strip()
        if canonical_key != key:
            normalization_count += 1
        canonical_value, nested_count = _canonicalize_value(raw_value)
        normalization_count += nested_count
        normalized[canonical_key] = canonical_value
    return normalized, normalization_count


def _canonicalize_value(value: Any) -> tuple[Any, int]:
    if isinstance(value, Mapping):
        return _canonicalize_map_keys(value)
    if isinstance(value, list):
        items: list[Any] = []
        normalization_count = 0
        for item in value:
            canonical_item, nested_count = _canonicalize_value(item)
            items.append(canonical_item)
            normalization_count += nested_count
        return items, normalization_count
    return value, 0
```

### `cortex/stop_contract.py`

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .stop_payload import extract_stop_fields, resolve_stop_value
from .utils import _as_string_list

STOP_PAYLOAD_KEYS = (
    "challenge_coverage",
    "requirement_audit",
    "truth_claims",
    "required_requirement_ids",
    "failed_approach",
    "stuck_declaration",
)


class ContractDeficitKind(str, Enum):
    MISSING_STRUCTURED_STOP_FIELDS = "missing_structured_stop_fields"
    TRAILER_FALLBACK_REJECTED = "trailer_fallback_rejected"
    STRICT_MESSAGE_FALLBACK_REJECTED = "strict_message_fallback_rejected"
    UNKNOWN_STOP_FAILURE = "unknown_stop_failure"


@dataclass(frozen=True, slots=True)
class ContractDeficit:
    kind: ContractDeficitKind


@dataclass(slots=True)
class StopContract:
    warnings: list[str]
    stop_source: str
    stop_fields_source: str
    stop_fields_fallback_used: bool
    stop_key_normalization_count: int
    challenge_coverage: Any
    requirement_audit: Any
    truth_claims: Any
    required_requirement_ids: list[str]
    failed_approach: dict[str, Any] | None
    stuck_declaration: dict[str, Any] | None
    structured_stop_violation: bool
    contract_diagnostic: dict[str, Any] | None
    contract_deficit: ContractDeficit | None = None


def resolve_stop_contract(
    payload: Mapping[str, Any],
    *,
    allow_message_fallback: bool,
    require_structured_stop_payload: bool,
) -> StopContract:
    stop_fields, stop_fields_source, warnings, normalization_count = extract_stop_fields(
        payload, allow_message_fallback=allow_message_fallback
    )
    values = {
        key: resolve_stop_value(
            key=key,
            payload=payload,
            stop_fields=stop_fields,
            stop_fields_source=stop_fields_source,
            warnings=warnings,
            value_label=key,
        )
        for key in STOP_PAYLOAD_KEYS
    }
    stop_source = _stop_source_label(stop_fields_source)
    used_message_stop_fallback = bool(stop_source == "message_fallback" and stop_fields is not None)
    if used_message_stop_fallback:
        warnings.append(
            "Recovered stop fields from last_assistant_message STOP_FIELDS_JSON fallback; emit structured stop fields directly."
        )
    if normalization_count > 0:
        warnings.append(
            f"Canonicalized {normalization_count} stop payload key(s) with surrounding whitespace."
        )
    has_structured_stop_source = _has_structured_stop_source(payload, stop_fields_source)
    structured_stop_violation = bool(require_structured_stop_payload and not has_structured_stop_source)
    contract_diagnostic = None
    contract_deficit = None
    if structured_stop_violation:
        if used_message_stop_fallback:
            warnings.append(
                "Structured stop payload is required; trailer-only STOP_FIELDS_JSON fallback is rejected."
            )
            contract_deficit = make_contract_deficit(ContractDeficitKind.TRAILER_FALLBACK_REJECTED)
            contract_diagnostic = structured_stop_contract_diagnostic(contract_deficit.kind)
        else:
            warnings.append(
                "Structured stop payload is required; include stop fields directly or via payload.stop_fields."
            )
            contract_deficit = make_contract_deficit(ContractDeficitKind.MISSING_STRUCTURED_STOP_FIELDS)
            contract_diagnostic = structured_stop_contract_diagnostic(contract_deficit.kind)

    return StopContract(
        warnings=warnings,
        stop_source=stop_source,
        stop_fields_source=stop_fields_source or "none",
        stop_fields_fallback_used=used_message_stop_fallback,
        stop_key_normalization_count=normalization_count,
        challenge_coverage=values["challenge_coverage"],
        requirement_audit=values["requirement_audit"],
        truth_claims=values["truth_claims"],
        required_requirement_ids=_as_string_list(values["required_requirement_ids"]),
        failed_approach=_resolve_failed_approach(payload, values["failed_approach"], stop_fields=stop_fields),
        stuck_declaration=_resolve_stuck_declaration(
            values["stuck_declaration"],
            warnings=warnings,
        ),
        structured_stop_violation=structured_stop_violation,
        contract_diagnostic=contract_diagnostic,
        contract_deficit=contract_deficit,
    )


def _resolve_failed_approach(
    payload: Mapping[str, Any],
    failed_approach: Any,
    *,
    stop_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    summary = ""
    reason = ""
    files: list[str] = []

    if isinstance(failed_approach, Mapping):
        summary = str(
            failed_approach.get("summary")
            or failed_approach.get("what_was_tried")
            or failed_approach.get("approach")
            or ""
        ).strip()
        reason = str(failed_approach.get("reason") or failed_approach.get("why_failed") or "").strip()
        files = _as_string_list(failed_approach.get("files"))
    elif isinstance(failed_approach, str):
        summary = failed_approach.strip()

    if not summary:
        for key in ("what_was_tried", "failed_summary", "approach", "failed_approach_summary"):
            candidate = str(payload.get(key) or (stop_fields or {}).get(key) or "").strip()
            if candidate:
                summary = candidate
                break
    if not reason:
        for key in ("why_failed", "failure_reason", "reason"):
            candidate = str(payload.get(key) or (stop_fields or {}).get(key) or "").strip()
            if candidate:
                reason = candidate
                break
    if not files:
        files = (
            _as_string_list(payload.get("failed_files"))
            or _as_string_list(payload.get("files"))
            or _as_string_list(payload.get("target_files"))
            or _as_string_list((stop_fields or {}).get("failed_files"))
            or _as_string_list((stop_fields or {}).get("files"))
            or _as_string_list((stop_fields or {}).get("target_files"))
        )

    if not summary or not reason:
        return None
    return {"summary": summary, "reason": reason, "files": files}


def _resolve_stuck_declaration(
    value: Any,
    *,
    warnings: list[str],
) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        warnings.append("Ignoring invalid stuck_declaration; expected an object.")
        return None

    check = str(value.get("check") or "").strip()
    approaches_tried = _as_string_list(value.get("approaches_tried"))
    obstacle = str(value.get("obstacle") or "").strip()
    if not (check and approaches_tried and obstacle):
        warnings.append(
            "Ignoring incomplete stuck_declaration; expected check, approaches_tried, and obstacle."
        )
        return None

    return {
        "check": check,
        "approaches_tried": approaches_tried,
        "obstacle": obstacle,
    }


def reconcile_required_requirement_ids(
    session_required_ids: list[str], stop_required_ids: list[str]
) -> tuple[list[str], str, str | None]:
    if session_required_ids:
        warning = (
            "Ignoring required_requirement_ids from Stop payload; using SessionStart contract."
            if stop_required_ids and set(stop_required_ids) != set(session_required_ids)
            else None
        )
        return list(session_required_ids), "session", warning
    if stop_required_ids:
        return (
            list(stop_required_ids),
            "stop_payload",
            "No SessionStart requirement contract found; using Stop-provided required_requirement_ids.",
        )
    return [], "none", None


def _stop_source_label(stop_fields_source: str | None) -> str:
    if stop_fields_source == "last_assistant_message":
        return "message_fallback"
    if stop_fields_source == "payload.stop_fields":
        return "payload.stop_fields"
    return "native"


def _has_structured_stop_source(payload: Mapping[str, Any], stop_fields_source: str | None) -> bool:
    return bool(
        any(payload.get(key) is not None for key in STOP_PAYLOAD_KEYS)
        or stop_fields_source == "payload.stop_fields"
    )


def make_contract_deficit(kind: ContractDeficitKind) -> ContractDeficit:
    return ContractDeficit(kind=kind)


def serialize_contract_deficit(contract_deficit: ContractDeficit | None) -> list[str]:
    return [contract_deficit.kind.value] if contract_deficit is not None else []


def structured_stop_contract_diagnostic(kind: ContractDeficitKind | str) -> dict[str, Any]:
    kind_value = kind.value if isinstance(kind, ContractDeficitKind) else str(kind).strip()
    if kind_value == ContractDeficitKind.TRAILER_FALLBACK_REJECTED.value:
        return {"evidence_found": ["stop fields only via last_assistant_message STOP_FIELDS_JSON trailer"], "evidence_expected": ["native structured stop fields or payload.stop_fields"], "gap_description": "Structured stop evidence was only provided through trailer fallback.", "gap_characterization": "execution_gap", "distance_signal": "close"}
    if kind_value == ContractDeficitKind.STRICT_MESSAGE_FALLBACK_REJECTED.value:
        return {"evidence_found": ["stop_source=message_fallback"], "evidence_expected": ["stop_source=native or payload.stop_fields"], "gap_description": "Strict mode rejected message-fallback stop evidence.", "gap_characterization": "execution_gap", "distance_signal": "close"}
    return {"evidence_found": ["no machine-readable stop fields"], "evidence_expected": ["native structured stop fields or payload.stop_fields"], "gap_description": "Completion was claimed without machine-readable stop evidence.", "gap_characterization": "comprehension_gap", "distance_signal": "far"}
```

### `cortex/stop_policy.py`

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class StopVerdict:
    session_status: str
    recommend_revert: bool
    proceed: bool
    feedback_mode: str
    terminate_session: bool
    stop_stage: str | None


def compute_stop_outcome(
    *,
    mode: str,
    fail_on_missing_challenge_coverage: bool,
    fail_on_requirement_audit_gap: bool,
    require_requirement_audit: bool,
    challenge_ok: bool | None,
    invariant_ok: bool | None,
    invariant_recommend_revert: bool,
    missing_challenge_coverage: bool,
    requirements_gate_gap: bool,
    requirement_audit_missing: bool,
    structured_stop_violation: bool,
    reconsider_required: bool = False,
    terminate_session: bool = False,
    stuck_declared: bool = False,
) -> StopVerdict:
    strict_mode = mode == "strict"
    strict_challenge_gate = strict_mode and fail_on_missing_challenge_coverage
    challenge_gate_violation = _challenge_gate_violation(
        strict_challenge_gate=strict_challenge_gate,
        missing_challenge_coverage=missing_challenge_coverage,
        challenge_ok=challenge_ok,
    )
    requirement_audit_violation = _requirement_audit_violation(
        strict_mode=strict_mode,
        fail_on_requirement_audit_gap=fail_on_requirement_audit_gap,
        requirements_gate_gap=requirements_gate_gap,
        requirement_audit_missing=requirement_audit_missing,
        require_requirement_audit=require_requirement_audit,
    )

    base_status = "completed"
    if invariant_ok is False:
        base_status = "failed_invariants"
    elif structured_stop_violation:
        base_status = "failed_stop_contract"
    elif requirement_audit_violation:
        base_status = "failed_requirements"
    elif challenge_ok is False:
        base_status = "failed_challenges"
    elif missing_challenge_coverage and strict_challenge_gate:
        base_status = "missing_challenge_coverage"

    if base_status != "completed" and stuck_declared:
        return StopVerdict(
            session_status="stuck",
            recommend_revert=False,
            proceed=False,
            feedback_mode="stuck",
            terminate_session=False,
            stop_stage=None,
        )

    recommend_revert = bool(
        invariant_recommend_revert
        or challenge_gate_violation
        or requirement_audit_violation
        or (strict_mode and structured_stop_violation)
    )
    stop_stage = _stop_stage(
        base_status=base_status,
        reconsider_required=reconsider_required,
        terminate_session=terminate_session,
    )
    return StopVerdict(
        session_status=base_status,
        recommend_revert=recommend_revert,
        proceed=not (recommend_revert or terminate_session),
        feedback_mode="reconsider_approach" if base_status != "completed" and reconsider_required else "normal",
        terminate_session=terminate_session,
        stop_stage=stop_stage,
    )


def _challenge_gate_violation(
    *,
    strict_challenge_gate: bool,
    missing_challenge_coverage: bool,
    challenge_ok: bool | None,
) -> bool:
    return strict_challenge_gate and (missing_challenge_coverage or challenge_ok is False)


def _requirement_audit_violation(
    *,
    strict_mode: bool,
    fail_on_requirement_audit_gap: bool,
    requirements_gate_gap: bool,
    requirement_audit_missing: bool,
    require_requirement_audit: bool,
) -> bool:
    return bool(
        strict_mode
        and fail_on_requirement_audit_gap
        and (requirements_gate_gap or (requirement_audit_missing and require_requirement_audit))
    )


def _stop_stage(
    *,
    base_status: str,
    reconsider_required: bool,
    terminate_session: bool,
) -> str | None:
    if base_status == "completed":
        return None
    if terminate_session:
        return "halt"
    if reconsider_required:
        return "reorient"
    return "repair"
```

### `cortex/stop_signals.py`

```python
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .utils import _as_string_list

_OBJECTIVE_GAP_KEYS = ("contract", "challenges", "requirements", "truth_claims", "invariants")


def build_stop_attempt_signature(
    *,
    challenge_coverage: Mapping[str, Any] | None,
    witness: Mapping[str, list[str]] | None,
    truth_claims_payload: Mapping[str, Any] | None,
    failed_approach: Mapping[str, Any] | None,
    observed_modified_files: list[str] | None,
) -> dict[str, Any]:
    challenge_shape: list[str] = []
    if isinstance(challenge_coverage, Mapping):
        for category in sorted(str(key).strip() for key in challenge_coverage.keys()):
            raw = challenge_coverage.get(category)
            if isinstance(raw, Mapping):
                challenge_shape.append(f"{category}:covered={bool(raw.get('covered', False))}")
            else:
                challenge_shape.append(f"{category}:covered={bool(raw)}")

    witnessed_commands = sorted(
        {
            normalize_stop_command_signal(command)
            for command in _as_string_list((witness or {}).get("commands"))
            if normalize_stop_command_signal(command)
        }
    )
    file_signal = sorted(
        {
            path
            for path in (
                _as_string_list((truth_claims_payload or {}).get("modified_files"))
                + _as_string_list((failed_approach or {}).get("files"))
                + _as_string_list(observed_modified_files)
            )
            if path
        }
    )
    return {
        "challenge_shape": challenge_shape,
        "witnessed_commands": witnessed_commands,
        "file_signal": file_signal,
    }


def build_objective_gap_signature(
    *,
    stop_source: str,
    stop_fields_fallback_used: bool,
    structured_stop_violation: bool,
    strict_message_fallback_violation: bool,
    challenge_report: Any,
    challenge_diagnostics: list[dict[str, Any]],
    missing_challenge_coverage: bool,
    requirement_audit: Any,
    required_requirement_ids: list[str],
    truth_claims_report: Mapping[str, Any] | None,
    truth_claims_gap: bool,
    invariant_report: Any,
) -> dict[str, list[str]]:
    return normalize_objective_gap_signature(
        {
            "contract": _contract_gap_entries(
                stop_source=stop_source,
                stop_fields_fallback_used=stop_fields_fallback_used,
                structured_stop_violation=structured_stop_violation,
                strict_message_fallback_violation=strict_message_fallback_violation,
            ),
            "challenges": _challenge_gap_entries(
                challenge_report=challenge_report,
                challenge_diagnostics=challenge_diagnostics,
                missing_challenge_coverage=missing_challenge_coverage,
            ),
            "requirements": _requirement_gap_entries(
                requirement_audit=requirement_audit,
                required_requirement_ids=required_requirement_ids,
            ),
            "truth_claims": _truth_claims_gap_entries(
                truth_claims_report=truth_claims_report,
                truth_claims_gap=truth_claims_gap,
            ),
            "invariants": _invariant_gap_entries(invariant_report=invariant_report),
        }
    )


def normalize_objective_gap_signature(signature: Mapping[str, Any] | None) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {key: [] for key in _OBJECTIVE_GAP_KEYS}
    if not isinstance(signature, Mapping):
        return normalized
    for key in _OBJECTIVE_GAP_KEYS:
        values = sorted(
            {
                str(value).strip()
                for value in _as_string_list(signature.get(key))
                if str(value).strip()
            }
        )
        normalized[key] = values
    return normalized


def objective_gap_relation(
    previous: Mapping[str, Any] | None,
    current: Mapping[str, Any] | None,
) -> str | None:
    normalized_previous = normalize_objective_gap_signature(previous)
    normalized_current = normalize_objective_gap_signature(current)
    if not any(normalized_current.values()) or not any(normalized_previous.values()):
        return None
    if normalized_previous == normalized_current:
        return "identical"

    previous_sets = {key: set(values) for key, values in normalized_previous.items()}
    current_sets = {key: set(values) for key, values in normalized_current.items()}
    current_within_previous = all(current_sets[key] <= previous_sets[key] for key in _OBJECTIVE_GAP_KEYS)
    previous_within_current = all(previous_sets[key] <= current_sets[key] for key in _OBJECTIVE_GAP_KEYS)
    if current_within_previous and any(current_sets[key] < previous_sets[key] for key in _OBJECTIVE_GAP_KEYS):
        return "reduced"
    if previous_within_current and any(previous_sets[key] < current_sets[key] for key in _OBJECTIVE_GAP_KEYS):
        return "expanded"
    return "substituted"


def classify_objective_gap_state(
    *,
    previous_signature: Mapping[str, Any] | None,
    previous_attempts: int,
    current_signature: Mapping[str, Any] | None,
    session_status: str,
    stuck_declared: bool,
) -> tuple[str | None, int, str]:
    normalized_current = normalize_objective_gap_signature(current_signature)
    if session_status == "completed":
        return None, 0, ""
    if stuck_declared or session_status == "stuck":
        return None, 0, ""
    if not any(normalized_current.values()):
        return None, 0, ""

    normalized_previous = normalize_objective_gap_signature(previous_signature)
    if previous_attempts <= 0 or not any(normalized_previous.values()):
        return (
            "observed",
            1,
            "Unresolved objective gap identified; this failed stop is the first recorded observation of this gap.",
        )

    relation = objective_gap_relation(normalized_previous, normalized_current)
    if relation == "identical":
        attempts = previous_attempts + 1
        if attempts >= 3:
            return (
                "misaligned",
                attempts,
                "Unresolved objective gap is identical across 3+ failed stops; reassess the goal, mechanism, and whether the current path is actually solving the task.",
            )
        return (
            "stagnant",
            attempts,
            "Unresolved objective gap is identical across failed stops; local activity is not reducing the real gap.",
        )
    if relation == "reduced":
        return (
            "reduced",
            1,
            "Unresolved objective gap strictly shrank; continue only if the remaining gap is now the real blocker.",
        )
    if relation == "expanded":
        return (
            "expanded",
            1,
            "Unresolved objective gap expanded; new unresolved obligations were introduced.",
        )
    if relation == "substituted":
        return (
            "substituted",
            1,
            "Unresolved objective gap changed by substitution rather than pure reduction; reassess whether the new gap is actually closer to completion.",
        )
    return (
        "observed",
        1,
        "Unresolved objective gap identified; this failed stop is the first recorded observation of this gap.",
    )


def stop_attempt_similarity(previous: Mapping[str, Any] | None, current: Mapping[str, Any]) -> float | None:
    if not isinstance(previous, Mapping):
        return None
    scores = [
        _signal_jaccard(previous.get("challenge_shape"), current.get("challenge_shape")),
        _signal_jaccard(previous.get("witnessed_commands"), current.get("witnessed_commands")),
        _signal_jaccard(previous.get("file_signal"), current.get("file_signal")),
    ]
    present_scores = [score for score in scores if score is not None]
    return round(sum(present_scores) / len(present_scores), 3) if present_scores else None


def normalize_stop_command_signal(command: str) -> str:
    return " ".join(str(command).strip().lower().split())


def _signal_jaccard(left: Any, right: Any) -> float | None:
    left_set = set(_as_string_list(left))
    right_set = set(_as_string_list(right))
    if not left_set and not right_set:
        return None
    union = left_set | right_set
    if not union:
        return None
    return len(left_set & right_set) / len(union)


def _contract_gap_entries(
    *,
    stop_source: str,
    stop_fields_fallback_used: bool,
    structured_stop_violation: bool,
    strict_message_fallback_violation: bool,
) -> list[str]:
    if not structured_stop_violation:
        return []
    if strict_message_fallback_violation:
        return ["strict_message_fallback_rejected"]
    if stop_fields_fallback_used or stop_source == "message_fallback":
        return ["trailer_fallback_rejected"]
    return ["missing_structured_stop_fields"]


def _challenge_gap_entries(
    *,
    challenge_report: Any,
    challenge_diagnostics: list[dict[str, Any]],
    missing_challenge_coverage: bool,
) -> list[str]:
    if challenge_report is None:
        entries = _diagnostic_gap_entries(challenge_diagnostics)
        if entries:
            return entries
        return ["__all__:missing"] if missing_challenge_coverage else []

    entries = {
        str(item).strip()
        for item in _as_string_list(getattr(challenge_report, "gap_entries", []))
        if str(item).strip()
    }
    if entries:
        return sorted(entries)

    entries = set()
    unverified = set(getattr(challenge_report, "unverified_categories", []))
    uncheckable = set(getattr(challenge_report, "uncheckable_categories", []))
    for category in sorted(set(getattr(challenge_report, "missing_categories", []))):
        if category in unverified or category in uncheckable:
            failure_class = "uncheckable" if category in uncheckable else "unverified"
        else:
            failure_class = "uncovered"
        entries.add(f"{category}:{failure_class}")
    return sorted(entries)


def _requirement_gap_entries(
    *,
    requirement_audit: Any,
    required_requirement_ids: list[str],
) -> list[str]:
    if not getattr(requirement_audit, "gap", False) and not getattr(requirement_audit, "missing", False):
        return []

    details = getattr(requirement_audit, "details", None)
    entries = {
        str(item).strip()
        for item in _as_string_list((details or {}).get("gap_entries"))
        if str(item).strip()
    }
    if not entries and getattr(requirement_audit, "missing", False):
        if required_requirement_ids:
            entries.update(f"{item_id}:missing" for item_id in sorted(set(required_requirement_ids)))
        else:
            entries.add("__audit__:missing")
    return sorted(entries)


def _truth_claims_gap_entries(
    *,
    truth_claims_report: Mapping[str, Any] | None,
    truth_claims_gap: bool,
) -> list[str]:
    if not truth_claims_gap or not isinstance(truth_claims_report, Mapping):
        return []
    entries = {
        str(item).strip()
        for item in _as_string_list(truth_claims_report.get("gap_entries"))
        if str(item).strip()
    }
    if not entries and truth_claims_report.get("errors"):
        entries.add("__truth_claims__:invalid_shape")
    return sorted(entries)


def _invariant_gap_entries(*, invariant_report: Any) -> list[str]:
    if invariant_report is None:
        return []
    entries: list[str] = []
    for result in getattr(invariant_report, "results", []):
        status = str(getattr(result, "status", "") or "").strip().lower()
        test_path = str(getattr(result, "test_path", "") or "").strip() or "__invariant__"
        if status == "missing":
            entries.append(f"{test_path}:missing_path")
        elif status == "error":
            entries.append(f"{test_path}:execution_failed")
        elif status == "fail":
            entries.append(f"{test_path}:failed")
    return sorted(set(entries))


def _diagnostic_gap_entries(diagnostics: list[dict[str, Any]]) -> list[str]:
    entries: set[str] = set()
    for diagnostic in diagnostics:
        entries.update(
            str(item).strip()
            for item in _as_string_list(diagnostic.get("gap_entries"))
            if str(item).strip()
        )
    return sorted(entries)
```

### `cortex/stop_runtime.py`

```python
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Any

from .challenges import ChallengeEnforcer, ChallengeReport
from .core_helpers import (
    session_changed_files_since_baseline,
    session_git_snapshot,
    session_metadata,
    session_required_requirement_ids,
    session_witness_context,
)
from .genome import CortexGenome
from .graveyard import Graveyard
from .invariants import InvariantReport, InvariantRunner
from .requirements import (
    RequirementAuditEvaluation,
    TruthClaimsEvaluation,
    _normalize_command,
    evaluate_requirement_audit_payload,
    evaluate_truth_claims_payload,
)
from .stop_contract import (
    ContractDeficit,
    ContractDeficitKind,
    StopContract,
    make_contract_deficit,
    reconcile_required_requirement_ids,
    serialize_contract_deficit,
    structured_stop_contract_diagnostic,
)
from .stop_policy import compute_stop_outcome
from .stop_signals import (
    build_objective_gap_signature,
    build_stop_attempt_signature,
    classify_objective_gap_state,
    normalize_objective_gap_signature,
    stop_attempt_similarity,
)
from .store import SQLiteStore
from .utils import _as_bool, _as_string_list, _normalize_repo_relative_path, _unique_list

LOOP_WARNING = (
    "Stop attempt is highly similar to the previous failed Stop; reconsider the approach "
    "instead of refining the same attempt."
)


@dataclass(slots=True)
class StopPathOutcome:
    warnings: list[str]
    challenge_report: ChallengeReport | None
    challenge_diagnostics: list[dict[str, Any]]
    missing_challenge_coverage: bool
    invariant_report: InvariantReport | None
    requirement_audit: RequirementAuditEvaluation
    truth_claims: TruthClaimsEvaluation
    required_requirement_ids: list[str]
    required_requirement_ids_source: str
    contract_diagnostic: dict[str, Any] | None
    git_snapshot: dict[str, Any] | None
    stuck_declaration: dict[str, Any] | None
    structured_stop_violation: bool
    strict_message_fallback_violation: bool
    enforcement_pass: bool
    session_status: str
    recommend_revert: bool
    proceed: bool
    feedback_mode: str
    terminate_session: bool
    stop_stage: str | None
    stop_attempt_signature: dict[str, Any]
    loop_detected: bool
    loop_similarity: float | None
    objective_gap_state: str | None
    objective_gap_unchanged_attempts: int
    objective_gap_signature: dict[str, list[str]]
    objective_gap_reason: str
    repair_targets: list[dict[str, Any]]
    derived_evidence: dict[str, Any]
    pre_stop_review_card: dict[str, Any]
    scope_report: dict[str, Any]


class TruthClaimDeficitKind(str, Enum):
    INVALID_SHAPE = "invalid_shape"
    UNVERIFIED = "unverified"
    UNCHECKABLE = "uncheckable"


class ChallengeDeficitScopeKind(str, Enum):
    ALL = "all"
    CATEGORY = "category"


class ChallengeDeficitKind(str, Enum):
    MISSING = "missing"
    INVALID_SHAPE = "invalid_shape"
    UNCOVERED = "uncovered"
    UNVERIFIED = "unverified"
    UNCHECKABLE = "uncheckable"


class InvariantDeficitKind(str, Enum):
    MISSING_PATH = "missing_path"
    EXECUTION_FAILED = "execution_failed"
    FAILED = "failed"


class RequirementDeficitSubjectKind(str, Enum):
    AUDIT = "audit"
    ITEM = "item"
    REQUIREMENT = "requirement"


class RequirementDeficitKind(str, Enum):
    MISSING = "missing"
    INVALID_SHAPE = "invalid_shape"
    INCOMPLETE = "incomplete"
    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_UNVERIFIED = "evidence_unverified"
    GAP_MISSING = "gap_missing"
    STATUS_INVALID = "status_invalid"
    DUPLICATE_ID = "duplicate_id"
    FAIL_DECLARED = "fail_declared"


@dataclass(frozen=True, slots=True)
class RequirementDeficit:
    subject_kind: RequirementDeficitSubjectKind
    gap_kind: RequirementDeficitKind
    requirement_id: str | None = None
    item_placeholder: str | None = None


@dataclass(frozen=True, slots=True)
class ChallengeDeficit:
    scope_kind: ChallengeDeficitScopeKind
    gap_kind: ChallengeDeficitKind
    category: str | None = None


@dataclass(frozen=True, slots=True)
class InvariantDeficit:
    test_path: str
    gap_kind: InvariantDeficitKind


@dataclass(frozen=True, slots=True)
class TruthClaimDeficit:
    field: str
    gap_kind: TruthClaimDeficitKind
    claim_identity: str | None = None


class StopPathRunner:
    def __init__(
        self,
        *,
        root: Path,
        store: SQLiteStore,
        genome: CortexGenome,
        challenges: ChallengeEnforcer,
        invariants: InvariantRunner,
        graveyard: Graveyard,
        session_metadata_loader: Callable[[SQLiteStore, str], dict[str, Any]] = session_metadata,
        session_git_snapshotter: Callable[[Path], dict[str, Any]] = session_git_snapshot,
        session_changed_files_since_baseline_fn: Callable[
            ..., tuple[list[str] | None, str | None]
        ] = session_changed_files_since_baseline,
        session_required_requirement_ids_loader: Callable[
            [SQLiteStore, str], list[str]
        ] = session_required_requirement_ids,
        session_witness_context_loader: Callable[
            [SQLiteStore, str], Mapping[str, list[str]]
        ] = session_witness_context,
    ) -> None:
        self.root = root
        self.store = store
        self.genome = genome
        self.challenges = challenges
        self.invariants = invariants
        self.graveyard = graveyard
        self._session_metadata = session_metadata_loader
        self._session_git_snapshot = session_git_snapshotter
        self._session_changed_files_since_baseline = session_changed_files_since_baseline_fn
        self._session_required_requirement_ids = session_required_requirement_ids_loader
        self._session_witness_context = session_witness_context_loader

    def run(
        self,
        *,
        session_id: str,
        payload: Mapping[str, Any],
        stop_contract: StopContract,
    ) -> StopPathOutcome:
        session_meta = self._session_metadata(self.store, session_id)
        warnings = list(stop_contract.warnings)
        baseline_git_snapshot = (
            dict(session_meta.get("git_snapshot"))
            if isinstance(session_meta.get("git_snapshot"), Mapping)
            else None
        )
        strict_message_fallback_violation = (
            self.genome.hooks.mode == "strict" and stop_contract.stop_source == "message_fallback"
        )
        contract_diagnostic = stop_contract.contract_diagnostic
        contract_deficit = stop_contract.contract_deficit
        if stop_contract.structured_stop_violation and contract_deficit is None:
            if stop_contract.stop_fields_fallback_used or stop_contract.stop_source == "message_fallback":
                contract_deficit = make_contract_deficit(ContractDeficitKind.TRAILER_FALLBACK_REJECTED)
            else:
                contract_deficit = make_contract_deficit(ContractDeficitKind.MISSING_STRUCTURED_STOP_FIELDS)
        if strict_message_fallback_violation:
            warnings.append(
                "Strict mode rejects Stop message-fallback payloads; send stop fields natively or via payload.stop_fields."
            )
            contract_deficit = make_contract_deficit(ContractDeficitKind.STRICT_MESSAGE_FALLBACK_REJECTED)
            if contract_diagnostic is None:
                contract_diagnostic = structured_stop_contract_diagnostic(
                    ContractDeficitKind.STRICT_MESSAGE_FALLBACK_REJECTED
                )

        coverage_payload = stop_contract.challenge_coverage
        challenge_report: ChallengeReport | None = None
        challenge_diagnostics: list[dict[str, Any]] = []
        missing_challenge_coverage = False
        require_verifiable_challenge_coverage = (
            self.genome.hooks.mode == "strict"
            and self.genome.hooks.fail_on_missing_challenge_coverage
        )
        needs_witness = bool(
            (require_verifiable_challenge_coverage and isinstance(coverage_payload, Mapping))
            or stop_contract.requirement_audit is not None
            or stop_contract.truth_claims is not None
        )
        observed_witness = (
            self._session_witness_context(self.store, session_id)
            if needs_witness
            else {"commands": [], "tools": []}
        )
        witness = observed_witness
        if isinstance(coverage_payload, Mapping):
            challenge_report = self.challenges.evaluate(
                session_id=session_id,
                coverage_payload=coverage_payload,
                require_verifiable_coverage=require_verifiable_challenge_coverage,
                root=self.root,
                witness=witness,
            )
            if not challenge_report.ok:
                warnings.append(
                    "Missing challenge coverage for categories: "
                    + ", ".join(challenge_report.missing_categories)
                )
            warnings.extend(challenge_report.config_warnings)
            challenge_diagnostics = list(challenge_report.diagnostics)
        elif coverage_payload is not None:
            missing_challenge_coverage = self.genome.challenges.require_coverage
            warnings.append(
                "Invalid challenge_coverage format; expected an object mapping category names to values."
            )
            challenge_diagnostics = self.challenges.invalid_coverage_diagnostics(coverage_payload)
        elif self.genome.challenges.require_coverage:
            missing_challenge_coverage = True
            message = (
                "No challenge_coverage provided in Stop payload; skipping challenge gate recording. "
                "Include challenge_coverage directly or via payload.stop_fields"
            )
            if self.genome.hooks.allow_message_stop_fallback:
                message += ", or as a STOP_FIELDS_JSON trailer"
            warnings.append(message + ".")
            challenge_diagnostics = self.challenges.missing_coverage_diagnostics()

        required_requirement_ids, requirement_ids_source, required_ids_warning = (
            reconcile_required_requirement_ids(
                self._session_required_requirement_ids(self.store, session_id),
                list(stop_contract.required_requirement_ids),
            )
        )
        if required_ids_warning:
            warnings.append(required_ids_warning)

        truth_claims_payload = (
            stop_contract.truth_claims if isinstance(stop_contract.truth_claims, Mapping) else None
        )
        has_modified_files_claim = bool(
            truth_claims_payload and _as_string_list(truth_claims_payload.get("modified_files"))
        )
        observed_modified_files: list[str] | None = None
        modified_files_error: str | None = None
        if has_modified_files_claim:
            current_git_snapshot = self._session_git_snapshot(self.root)
            observed_modified_files, modified_files_error = self._session_changed_files_since_baseline(
                baseline_snapshot=baseline_git_snapshot,
                current_snapshot=current_git_snapshot,
            )
        else:
            modified_files_error = "truth_claims.modified_files not present in stop payload"

        requirement_audit = evaluate_requirement_audit_payload(
            stop_contract.requirement_audit,
            require_requirement_audit=self.genome.hooks.require_requirement_audit,
            require_evidence_for_passed_requirement=self.genome.hooks.require_evidence_for_passed_requirement,
            required_requirement_ids=required_requirement_ids,
            root=self.root,
            witness=witness,
        )
        warnings.extend(requirement_audit.warnings)
        truth_claims = evaluate_truth_claims_payload(
            stop_contract.truth_claims,
            root=self.root,
            witness=witness,
            observed_modified_files=observed_modified_files,
            modified_files_error=modified_files_error,
        )
        warnings.extend(truth_claims.warnings)

        invariant_report = None
        if self.genome.invariants.run_on_stop and _as_bool(payload.get("run_invariants"), True):
            invariant_report = self.invariants.run(
                session_id=session_id,
                extra_pytest_args=_as_string_list(payload.get("pytest_args")),
            )
            if not invariant_report.ok:
                warnings.append("Invariant suite reported failures.")

        if stop_contract.failed_approach:
            self.graveyard.record_failure(
                session_id=session_id,
                summary=str(stop_contract.failed_approach["summary"]),
                reason=str(stop_contract.failed_approach["reason"]),
                files=_as_string_list(stop_contract.failed_approach.get("files")),
            )

        structured_stop_violation = (
            stop_contract.structured_stop_violation or strict_message_fallback_violation
        )
        challenge_ok = None if challenge_report is None else challenge_report.ok
        invariant_ok = None if invariant_report is None else invariant_report.ok
        requirements_gate_gap = requirement_audit.gap or truth_claims.gap
        stop_attempt_signature = build_stop_attempt_signature(
            challenge_coverage=coverage_payload if isinstance(coverage_payload, Mapping) else None,
            witness=witness,
            truth_claims_payload=truth_claims_payload,
            failed_approach=stop_contract.failed_approach,
            observed_modified_files=observed_modified_files,
        )
        previous_signature = session_meta.get("stop_attempt_signature")
        loop_similarity = stop_attempt_similarity(
            previous_signature if isinstance(previous_signature, Mapping) else None,
            stop_attempt_signature,
        )
        loop_detected = bool(loop_similarity is not None and loop_similarity >= 0.85)
        objective_gap_signature = build_objective_gap_signature(
            stop_source=stop_contract.stop_source,
            stop_fields_fallback_used=stop_contract.stop_fields_fallback_used,
            structured_stop_violation=structured_stop_violation,
            strict_message_fallback_violation=strict_message_fallback_violation,
            challenge_report=challenge_report,
            challenge_diagnostics=challenge_diagnostics,
            missing_challenge_coverage=missing_challenge_coverage,
            requirement_audit=requirement_audit,
            required_requirement_ids=required_requirement_ids,
            truth_claims_report=truth_claims.report,
            truth_claims_gap=truth_claims.gap,
            invariant_report=invariant_report,
        )
        if contract_deficit is not None:
            objective_gap_signature = normalize_objective_gap_signature(
                {
                    **objective_gap_signature,
                    "contract": serialize_contract_deficit(contract_deficit),
                }
            )
        verdict = compute_stop_outcome(
            mode=self.genome.hooks.mode,
            fail_on_missing_challenge_coverage=self.genome.hooks.fail_on_missing_challenge_coverage,
            fail_on_requirement_audit_gap=self.genome.hooks.fail_on_requirement_audit_gap,
            require_requirement_audit=self.genome.hooks.require_requirement_audit,
            challenge_ok=challenge_ok,
            invariant_ok=invariant_ok,
            invariant_recommend_revert=bool(invariant_report and invariant_report.recommend_revert),
            missing_challenge_coverage=missing_challenge_coverage,
            requirements_gate_gap=requirements_gate_gap,
            requirement_audit_missing=requirement_audit.missing,
            structured_stop_violation=structured_stop_violation,
            reconsider_required=False,
            terminate_session=False,
            stuck_declared=stop_contract.stuck_declaration is not None,
        )
        if (
            verdict.session_status != "completed"
            and verdict.session_status != "stuck"
            and not any(objective_gap_signature.values())
        ):
            contract_deficit = make_contract_deficit(ContractDeficitKind.UNKNOWN_STOP_FAILURE)
            objective_gap_signature = normalize_objective_gap_signature(
                {
                    **objective_gap_signature,
                    "contract": serialize_contract_deficit(contract_deficit),
                }
            )
        previous_objective_gap_signature = (
            session_meta.get("objective_gap_signature")
            if isinstance(session_meta.get("objective_gap_signature"), Mapping)
            else None
        )
        previous_unchanged_attempts = _safe_int(
            session_meta.get(
                "objective_gap_unchanged_attempts",
                session_meta.get("unchanged_objective_gap_attempts"),
            ),
            default=0,
        )
        objective_gap_state, objective_gap_unchanged_attempts, objective_gap_reason = classify_objective_gap_state(
            previous_signature=previous_objective_gap_signature,
            previous_attempts=previous_unchanged_attempts,
            current_signature=objective_gap_signature,
            session_status=verdict.session_status,
            stuck_declared=stop_contract.stuck_declaration is not None,
        )
        reconsider_required = objective_gap_state in {"stagnant", "misaligned"}
        terminate_session = objective_gap_state == "misaligned"
        verdict = compute_stop_outcome(
            mode=self.genome.hooks.mode,
            fail_on_missing_challenge_coverage=self.genome.hooks.fail_on_missing_challenge_coverage,
            fail_on_requirement_audit_gap=self.genome.hooks.fail_on_requirement_audit_gap,
            require_requirement_audit=self.genome.hooks.require_requirement_audit,
            challenge_ok=challenge_ok,
            invariant_ok=invariant_ok,
            invariant_recommend_revert=bool(invariant_report and invariant_report.recommend_revert),
            missing_challenge_coverage=missing_challenge_coverage,
            requirements_gate_gap=requirements_gate_gap,
            requirement_audit_missing=requirement_audit.missing,
            structured_stop_violation=structured_stop_violation,
            reconsider_required=reconsider_required,
            terminate_session=terminate_session,
            stuck_declared=stop_contract.stuck_declaration is not None,
        )
        if verdict.session_status != "completed":
            if objective_gap_state in {"stagnant", "misaligned"}:
                warnings.append(objective_gap_reason)
                if loop_detected:
                    warnings.append(
                        "Local stop attempt still resembles the previous failed Stop while the unresolved objective gap remains unchanged."
                    )
            elif loop_detected:
                warnings.append(LOOP_WARNING)
        enforcement_pass = verdict.session_status == "completed"
        repair_targets = _build_repair_targets(
            stop_stage=verdict.stop_stage,
            structured_stop_violation=structured_stop_violation,
            strict_message_fallback_violation=strict_message_fallback_violation,
            contract_deficit=contract_deficit,
            contract_diagnostic=contract_diagnostic,
            objective_gap_signature=objective_gap_signature,
            challenge_report=challenge_report,
            challenge_diagnostics=challenge_diagnostics,
            requirement_audit=requirement_audit,
            truth_claims=truth_claims,
            invariant_report=invariant_report,
        )
        derived_evidence = _build_derived_evidence(
            witness=observed_witness,
            observed_modified_files=observed_modified_files,
            observed_modified_files_reason=modified_files_error,
            required_requirement_ids=required_requirement_ids,
        )
        pre_stop_review_card = _build_pre_stop_review_card(
            root=self.root,
            session_metadata=session_meta,
            derived_evidence=derived_evidence,
            enforcement_pass=enforcement_pass,
            session_status=verdict.session_status,
            structured_stop_violation=structured_stop_violation,
            missing_challenge_coverage=missing_challenge_coverage,
            requirement_audit=requirement_audit,
            truth_claims=truth_claims,
            invariant_report=invariant_report,
            objective_gap_state=objective_gap_state,
            loop_detected=loop_detected,
        )
        scope_report = _build_scope_report(
            root=self.root,
            session_metadata=session_meta,
            derived_evidence=derived_evidence,
        )
        scope_warning = _scope_overreach_warning(scope_report)
        if scope_warning:
            warnings.append(scope_warning)

        return StopPathOutcome(
            warnings=warnings,
            challenge_report=challenge_report,
            challenge_diagnostics=challenge_diagnostics,
            missing_challenge_coverage=missing_challenge_coverage,
            invariant_report=invariant_report,
            requirement_audit=requirement_audit,
            truth_claims=truth_claims,
            required_requirement_ids=required_requirement_ids,
            required_requirement_ids_source=requirement_ids_source,
            contract_diagnostic=contract_diagnostic,
            git_snapshot=baseline_git_snapshot,
            stuck_declaration=stop_contract.stuck_declaration,
            structured_stop_violation=structured_stop_violation,
            strict_message_fallback_violation=strict_message_fallback_violation,
            enforcement_pass=enforcement_pass,
            session_status=verdict.session_status,
            recommend_revert=verdict.recommend_revert,
            proceed=verdict.proceed,
            feedback_mode=verdict.feedback_mode,
            terminate_session=verdict.terminate_session,
            stop_stage=verdict.stop_stage,
            stop_attempt_signature=stop_attempt_signature,
            loop_detected=loop_detected,
            loop_similarity=loop_similarity,
            objective_gap_state=objective_gap_state,
            objective_gap_unchanged_attempts=objective_gap_unchanged_attempts,
            objective_gap_signature=objective_gap_signature,
            objective_gap_reason=objective_gap_reason,
            repair_targets=repair_targets,
            derived_evidence=derived_evidence,
            pre_stop_review_card=pre_stop_review_card,
            scope_report=scope_report,
        )

    @staticmethod
    def close_session_metadata(
        *,
        outcome: StopPathOutcome,
        stop_contract: StopContract,
        executive_signature: str | None,
        executive_record: dict[str, Any] | None,
    ) -> dict[str, Any]:
        challenge_report = outcome.challenge_report
        invariant_report = outcome.invariant_report
        requirement_audit = outcome.requirement_audit
        truth_claims = outcome.truth_claims
        requirement_audit_gap = requirement_audit.gap
        truth_claims_gap = truth_claims.gap
        requirements_gate_gap = requirement_audit_gap or truth_claims_gap
        challenge_ok = None if challenge_report is None else challenge_report.ok
        invariant_ok = None if invariant_report is None else invariant_report.ok
        return {
            "hook": "Stop",
            "enforcement_pass": outcome.enforcement_pass,
            "challenge_ok": challenge_ok,
            "challenge_diagnostics": outcome.challenge_diagnostics,
            "challenge_coverage_missing": outcome.missing_challenge_coverage,
            "challenge_unverified_categories": (
                [] if challenge_report is None else challenge_report.unverified_categories
            ),
            "challenge_uncheckable_categories": (
                [] if challenge_report is None else challenge_report.uncheckable_categories
            ),
            "invariant_ok": invariant_ok,
            "requirement_audit_ok": (
                None
                if not isinstance(requirement_audit.details, Mapping)
                else requirement_audit.details.get("ok")
            ),
            "requirement_audit_diagnostics": requirement_audit.diagnostics,
            "requirement_audit_missing": requirement_audit.missing,
            "requirement_audit_gap": requirement_audit_gap,
            "truth_claims_ok": None if truth_claims.report is None else truth_claims.report["ok"],
            "truth_claims_diagnostics": truth_claims.diagnostics,
            "truth_claims_gap": truth_claims_gap,
            "requirements_gate_gap": requirements_gate_gap,
            "required_requirement_ids": outcome.required_requirement_ids,
            "required_requirement_ids_source": outcome.required_requirement_ids_source,
            "contract_diagnostic": outcome.contract_diagnostic,
            "git_snapshot": outcome.git_snapshot,
            "stuck_declared": outcome.stuck_declaration is not None,
            "stuck_declaration": outcome.stuck_declaration,
            "structured_stop_violation": outcome.structured_stop_violation,
            "stop_source": stop_contract.stop_source,
            "stop_fields_source": stop_contract.stop_fields_source,
            "stop_fields_fallback_used": stop_contract.stop_fields_fallback_used,
            "stop_key_normalization_count": stop_contract.stop_key_normalization_count,
            "strict_message_fallback_violation": outcome.strict_message_fallback_violation,
            "feedback_mode": outcome.feedback_mode,
            "terminate_session": outcome.terminate_session,
            "stop_stage": outcome.stop_stage,
            "stop_attempt_signature": outcome.stop_attempt_signature,
            "loop_detected": outcome.loop_detected,
            "loop_similarity": outcome.loop_similarity,
            "objective_gap_state": outcome.objective_gap_state,
            "objective_gap_unchanged_attempts": outcome.objective_gap_unchanged_attempts,
            "objective_gap_signature": outcome.objective_gap_signature,
            "objective_gap_reason": outcome.objective_gap_reason,
            "repair_targets": outcome.repair_targets,
            "warnings": outcome.warnings,
            "derived_evidence": outcome.derived_evidence,
            "pre_stop_review_card": outcome.pre_stop_review_card,
            "scope_report": outcome.scope_report,
            "executive_last_stop_signature": executive_signature,
            "executive_memory_recorded": bool(executive_record),
            "executive_memory_record_id": None if executive_record is None else executive_record["id"],
        }

    @staticmethod
    def response_payload(
        *,
        outcome: StopPathOutcome,
        stop_contract: StopContract,
    ) -> dict[str, Any]:
        challenge_report = outcome.challenge_report
        requirement_audit = outcome.requirement_audit
        truth_claims = outcome.truth_claims
        return {
            "session_status": outcome.session_status,
            "challenge_report": None if challenge_report is None else challenge_report.to_dict(),
            "challenge_diagnostics": outcome.challenge_diagnostics,
            "challenge_coverage_missing": outcome.missing_challenge_coverage,
            "invariant_report": None if outcome.invariant_report is None else outcome.invariant_report.to_dict(),
            "requirement_audit_report": requirement_audit.report,
            "requirement_audit_diagnostics": requirement_audit.diagnostics,
            "truth_claims_report": truth_claims.report,
            "truth_claims_diagnostics": truth_claims.diagnostics,
            "required_requirement_ids": outcome.required_requirement_ids,
            "requirement_audit_missing": requirement_audit.missing,
            "requirement_audit_gap": requirement_audit.gap,
            "truth_claims_gap": truth_claims.gap,
            "requirements_gate_gap": requirement_audit.gap or truth_claims.gap,
            "enforcement_pass": outcome.enforcement_pass,
            "contract_diagnostic": outcome.contract_diagnostic,
            "stuck_declared": outcome.stuck_declaration is not None,
            "stuck_declaration": outcome.stuck_declaration,
            "structured_stop_violation": outcome.structured_stop_violation,
            "stop_source": stop_contract.stop_source,
            "stop_fields_source": stop_contract.stop_fields_source,
            "stop_fields_fallback_used": stop_contract.stop_fields_fallback_used,
            "stop_key_normalization_count": stop_contract.stop_key_normalization_count,
            "feedback_mode": outcome.feedback_mode,
            "terminate_session": outcome.terminate_session,
            "stop_stage": outcome.stop_stage,
            "stop_attempt_signature": outcome.stop_attempt_signature,
            "loop_detected": outcome.loop_detected,
            "loop_similarity": outcome.loop_similarity,
            "objective_gap_state": outcome.objective_gap_state,
            "objective_gap_unchanged_attempts": outcome.objective_gap_unchanged_attempts,
            "objective_gap_signature": outcome.objective_gap_signature,
            "objective_gap_reason": outcome.objective_gap_reason,
            "repair_targets": outcome.repair_targets,
            "derived_evidence": outcome.derived_evidence,
            "pre_stop_review_card": outcome.pre_stop_review_card,
            "scope_report": outcome.scope_report,
            "recommend_revert": outcome.recommend_revert,
            "proceed": outcome.proceed,
        }


def _build_derived_evidence(
    *,
    witness: Mapping[str, Any] | None,
    observed_modified_files: list[str] | None,
    observed_modified_files_reason: str | None,
    required_requirement_ids: list[str],
) -> dict[str, Any]:
    observed_commands = _unique_list(
        [
            normalized
            for value in _as_string_list((witness or {}).get("commands"))
            if (normalized := _normalize_command(value))
        ]
    )
    observed_tools = _unique_list(_as_string_list((witness or {}).get("tools")))
    unavailable_reason = None
    if observed_modified_files is None:
        unavailable_reason = (
            str(observed_modified_files_reason or "").strip()
            or "session-scoped modified-files evidence unavailable"
        )
    return {
        "observed_commands": observed_commands,
        "observed_tools": observed_tools,
        "observed_modified_files": (
            None if observed_modified_files is None else _unique_list(_as_string_list(observed_modified_files))
        ),
        "observed_modified_files_reason": unavailable_reason,
        "required_requirement_ids": _unique_list(_as_string_list(required_requirement_ids)),
    }


def _build_pre_stop_review_card(
    *,
    root: Path,
    session_metadata: Mapping[str, Any],
    derived_evidence: Mapping[str, Any],
    enforcement_pass: bool,
    session_status: str,
    structured_stop_violation: bool,
    missing_challenge_coverage: bool,
    requirement_audit: RequirementAuditEvaluation,
    truth_claims: TruthClaimsEvaluation,
    invariant_report: InvariantReport | None,
    objective_gap_state: str | None,
    loop_detected: bool,
) -> dict[str, Any]:
    unexpected_changes = _pre_stop_unexpected_changes(
        root=root,
        session_metadata=session_metadata,
        derived_evidence=derived_evidence,
    )
    observed_modified_files = derived_evidence.get("observed_modified_files")
    scope_judgment = _pre_stop_scope_judgment(
        observed_modified_files_available=isinstance(observed_modified_files, list),
        declared_targets_present=bool(_declared_route_file_targets(root=root, session_metadata=session_metadata)),
        unexpected_changes=unexpected_changes,
    )
    return {
        "scope_judgment": scope_judgment,
        "completion_judgment": _pre_stop_completion_judgment(
            enforcement_pass=enforcement_pass,
            session_status=session_status,
        ),
        "unexpected_changes": unexpected_changes,
        "remaining_blocker": _pre_stop_remaining_blocker(
            enforcement_pass=enforcement_pass,
            structured_stop_violation=structured_stop_violation,
            missing_challenge_coverage=missing_challenge_coverage,
            requirement_audit=requirement_audit,
            truth_claims=truth_claims,
            invariant_report=invariant_report,
            objective_gap_state=objective_gap_state,
            loop_detected=loop_detected,
        ),
    }


def _declared_route_file_targets(*, root: Path, session_metadata: Mapping[str, Any]) -> list[str]:
    return [spec["path"] for spec in _declared_route_target_specs(root=root, session_metadata=session_metadata)]


def _declared_route_target_specs(*, root: Path, session_metadata: Mapping[str, Any]) -> list[dict[str, str]]:
    seen_paths: set[str] = set()
    specs: list[dict[str, str]] = []
    for raw_target in _as_string_list(session_metadata.get("route_observed_file_targets")):
        normalized = _normalize_repo_relative_path(raw_target, root=root)
        if normalized:
            target_path = normalized
        else:
            fallback = raw_target.strip().replace("\\", "/").removeprefix("./").rstrip("/")
            if not fallback or Path(fallback).is_absolute():
                continue
            target_path = fallback
        if target_path in seen_paths:
            continue
        seen_paths.add(target_path)
        raw_text = str(raw_target).strip().replace("\\", "/")
        candidate = root / target_path
        target_kind = "directory" if raw_text.endswith("/") or candidate.is_dir() else "file"
        specs.append({"path": target_path, "kind": target_kind})
    return specs


def _scope_report_route_value(
    session_metadata: Mapping[str, Any],
    *,
    field_name: str,
    allowed: frozenset[str],
) -> str | None:
    value = session_metadata.get(field_name)
    if isinstance(value, str) and value in allowed:
        return value
    return None


def _build_scope_report(
    *,
    root: Path,
    session_metadata: Mapping[str, Any],
    derived_evidence: Mapping[str, Any],
) -> dict[str, Any]:
    declared_target_specs = _declared_route_target_specs(root=root, session_metadata=session_metadata)
    declared_targets = [spec["path"] for spec in declared_target_specs]
    observed_modified_files = derived_evidence.get("observed_modified_files")
    adjacent_changes: list[str] = []
    out_of_scope_changes: list[str] = []
    if isinstance(observed_modified_files, list) and declared_targets:
        for path in _as_string_list(observed_modified_files):
            if path in declared_targets:
                continue
            if _is_scope_adjacent_change(path, declared_target_specs=declared_target_specs):
                adjacent_changes.append(path)
            else:
                out_of_scope_changes.append(path)
    classification = _scope_report_classification(
        observed_modified_files=observed_modified_files,
        declared_targets=declared_targets,
        adjacent_changes=adjacent_changes,
        out_of_scope_changes=out_of_scope_changes,
    )
    return {
        "classification": classification,
        "task_regime": _scope_report_route_value(
            session_metadata,
            field_name="task_regime",
            allowed=frozenset({"reflex", "localized_edit", "bounded_build", "open_ended"}),
        ),
        "assurance_class": _scope_report_route_value(
            session_metadata,
            field_name="assurance_class",
            allowed=frozenset({"light", "standard", "strict"}),
        ),
        "declared_targets": declared_targets,
        "adjacent_changes": adjacent_changes,
        "out_of_scope_changes": out_of_scope_changes,
        "basis": {
            "declared_targets_source": "route_observed_file_targets",
            "observed_modified_files_reason": (
                None
                if isinstance(observed_modified_files, list)
                else str(derived_evidence.get("observed_modified_files_reason") or "").strip() or None
            ),
            "adjacency_rule": (
                "exact declared target is in-scope; same-parent file is adjacent; "
                "file under declared directory target is adjacent"
            ),
        },
    }


def _scope_overreach_warning(scope_report: Mapping[str, Any]) -> str | None:
    if str(scope_report.get("classification") or "").strip() != "overbroad":
        return None
    out_of_scope_changes = _as_string_list(scope_report.get("out_of_scope_changes"))
    if not out_of_scope_changes:
        return "Observed changes extend beyond declared task targets."
    return (
        "Observed changes extend beyond declared task targets: "
        + ", ".join(out_of_scope_changes)
        + "."
    )


def _scope_report_classification(
    *,
    observed_modified_files: Any,
    declared_targets: list[str],
    adjacent_changes: list[str],
    out_of_scope_changes: list[str],
) -> str:
    if not isinstance(observed_modified_files, list) or not declared_targets:
        return "unassessable"
    if out_of_scope_changes:
        return "overbroad"
    if adjacent_changes:
        return "expanded_but_adjacent"
    return "within_expected_scope"


def _is_scope_adjacent_change(
    path: str,
    *,
    declared_target_specs: list[dict[str, str]],
) -> bool:
    change_path = PurePosixPath(path)
    for spec in declared_target_specs:
        target_path = PurePosixPath(spec["path"])
        if spec["kind"] == "directory":
            if target_path in change_path.parents:
                return True
            continue
        if change_path.parent == target_path.parent:
            return True
    return False


def _pre_stop_unexpected_changes(
    *,
    root: Path,
    session_metadata: Mapping[str, Any],
    derived_evidence: Mapping[str, Any],
) -> list[str] | None:
    observed_modified_files = derived_evidence.get("observed_modified_files")
    if not isinstance(observed_modified_files, list):
        return None
    declared_targets = set(_declared_route_file_targets(root=root, session_metadata=session_metadata))
    if not declared_targets:
        return None
    return [path for path in _as_string_list(observed_modified_files) if path not in declared_targets]


def _pre_stop_scope_judgment(
    *,
    observed_modified_files_available: bool,
    declared_targets_present: bool,
    unexpected_changes: list[str] | None,
) -> str:
    if not observed_modified_files_available or not declared_targets_present:
        return "unassessable"
    if unexpected_changes:
        return "unexpected_changes_present"
    return "consistent_with_declared_targets"


def _pre_stop_completion_judgment(
    *,
    enforcement_pass: bool,
    session_status: str,
) -> str:
    if enforcement_pass:
        return "completion_supported"
    if session_status == "stuck":
        return "truthful_stop_only"
    return "completion_blocked"


def _pre_stop_remaining_blocker(
    *,
    enforcement_pass: bool,
    structured_stop_violation: bool,
    missing_challenge_coverage: bool,
    requirement_audit: RequirementAuditEvaluation,
    truth_claims: TruthClaimsEvaluation,
    invariant_report: InvariantReport | None,
    objective_gap_state: str | None,
    loop_detected: bool,
) -> str | None:
    if enforcement_pass:
        return None
    if structured_stop_violation:
        return "structured_stop_violation"
    if missing_challenge_coverage:
        return "missing_challenge_coverage"
    if requirement_audit.missing:
        return "requirement_audit_missing"
    if requirement_audit.gap or truth_claims.gap:
        return "requirements_gate_gap"
    if invariant_report is not None and not invariant_report.ok:
        return "invariants_failed"
    if objective_gap_state == "misaligned":
        return "objective_gap_misaligned"
    if objective_gap_state == "stagnant":
        return "objective_gap_stagnant"
    if loop_detected:
        return "repeated_stop_attempt"
    return "unresolved_stop_gap"


def _safe_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _build_repair_targets(
    *,
    stop_stage: str | None,
    structured_stop_violation: bool,
    strict_message_fallback_violation: bool,
    contract_deficit: ContractDeficit | None,
    contract_diagnostic: Mapping[str, Any] | None,
    objective_gap_signature: Mapping[str, list[str]],
    challenge_report: ChallengeReport | None,
    challenge_diagnostics: list[dict[str, Any]],
    requirement_audit: RequirementAuditEvaluation,
    truth_claims: TruthClaimsEvaluation,
    invariant_report: InvariantReport | None,
) -> list[dict[str, Any]]:
    if stop_stage not in {"repair", "reorient"}:
        return []

    targets: list[dict[str, Any]] = []

    def _append(kind: str, message: str, **extra: Any) -> None:
        entry: dict[str, Any] = {"kind": kind, "message": message}
        for key, value in extra.items():
            if value not in (None, [], {}):
                entry[key] = value
        targets.append(entry)

    contract_entries = serialize_contract_deficit(contract_deficit)
    if structured_stop_violation or contract_deficit is not None:
        contract_kind = "invalid_message_fallback" if strict_message_fallback_violation else "structured_stop"
        _append(
            "contract",
            "End with exactly one final line beginning `STOP_FIELDS_JSON:` followed by valid JSON.",
            contract_kind=contract_kind,
            entries=contract_entries,
            gap_description=_gap_description(contract_diagnostic),
        )

    challenge_targets = _challenge_repair_targets(
        _challenge_deficits(objective_gap_signature.get("challenges", [])),
        challenge_report=challenge_report,
        challenge_diagnostics=challenge_diagnostics,
    )
    targets.extend(challenge_targets)

    requirement_targets = _requirement_repair_targets(
        _requirement_deficits(objective_gap_signature.get("requirements", [])),
        requirement_audit=requirement_audit,
    )
    targets.extend(requirement_targets)

    truth_targets = _truth_claim_repair_targets(
        _truth_claim_deficits(objective_gap_signature.get("truth_claims", [])),
        truth_claims=truth_claims,
    )
    targets.extend(truth_targets)

    invariant_targets = _invariant_repair_targets(
        _invariant_deficits(objective_gap_signature.get("invariants", [])),
        invariant_report=invariant_report,
    )
    targets.extend(invariant_targets)
    return targets


def _challenge_repair_targets(
    deficits: list[ChallengeDeficit],
    *,
    challenge_report: ChallengeReport | None,
    challenge_diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not deficits:
        return []

    active_categories = [] if challenge_report is None else list(challenge_report.active_categories)
    targets: list[dict[str, Any]] = []
    if any(deficit.gap_kind is ChallengeDeficitKind.INVALID_SHAPE for deficit in deficits):
        targets.append(
            {
                "kind": "challenge_coverage",
                "gap_kind": "invalid_shape",
                "message": "Use a `challenge_coverage` object keyed by the active challenge categories, not a collapsed or invalid shape.",
                "categories": active_categories,
                "gap_description": _first_gap_description(challenge_diagnostics),
            }
        )
    for gap_kind in (
        ChallengeDeficitKind.MISSING,
        ChallengeDeficitKind.UNCOVERED,
        ChallengeDeficitKind.UNVERIFIED,
        ChallengeDeficitKind.UNCHECKABLE,
    ):
        raw_categories: list[str] = []
        named_categories: list[str] = []
        uses_all_categories = False
        for deficit in deficits:
            if deficit.gap_kind is not gap_kind:
                continue
            if deficit.scope_kind is ChallengeDeficitScopeKind.ALL:
                uses_all_categories = True
                token = "__all__"
            else:
                token = str(deficit.category or "").strip()
            if token and token not in raw_categories:
                raw_categories.append(token)
            if (
                deficit.scope_kind is ChallengeDeficitScopeKind.CATEGORY
                and token
                and token not in named_categories
            ):
                named_categories.append(token)
        if not raw_categories:
            continue
        display_categories = active_categories if uses_all_categories and active_categories else named_categories
        if gap_kind in {ChallengeDeficitKind.MISSING, ChallengeDeficitKind.UNCOVERED} and display_categories:
            message = (
                "Provide category-specific `challenge_coverage` objects with evidence for: "
                + ", ".join(display_categories)
                + "."
            )
        elif gap_kind is ChallengeDeficitKind.UNVERIFIED and display_categories:
            message = (
                "Replace unverifiable `challenge_coverage` evidence with repo-verifiable or witnessed evidence for: "
                + ", ".join(display_categories)
                + "."
            )
        elif gap_kind is ChallengeDeficitKind.UNCHECKABLE and display_categories:
            message = (
                "Replace uncheckable `challenge_coverage` evidence with checkable repo or command evidence for: "
                + ", ".join(display_categories)
                + "."
            )
        elif gap_kind in {ChallengeDeficitKind.MISSING, ChallengeDeficitKind.UNCOVERED}:
            message = "Provide category-specific `challenge_coverage` objects for every active category."
            display_categories = raw_categories
        elif gap_kind is ChallengeDeficitKind.UNVERIFIED:
            message = "Replace unverifiable `challenge_coverage` evidence with repo-verifiable or witnessed evidence for every affected category."
            display_categories = raw_categories
        else:
            message = "Replace uncheckable `challenge_coverage` evidence with checkable repo or command evidence for every affected category."
            display_categories = raw_categories
        targets.append(
            {
                "kind": "challenge_coverage",
                "gap_kind": gap_kind.value,
                "categories": display_categories,
                "message": message,
            }
        )
    return targets


def _challenge_deficits(entries: list[str]) -> list[ChallengeDeficit]:
    deficits: list[ChallengeDeficit] = []
    seen: set[tuple[ChallengeDeficitScopeKind, ChallengeDeficitKind, str | None]] = set()
    for raw_entry in entries:
        entry = str(raw_entry).strip()
        if not entry:
            continue
        subject_token, sep, gap_kind_text = entry.partition(":")
        if sep != ":":
            continue
        subject_token = subject_token.strip()
        gap_kind_text = gap_kind_text.strip()
        if not subject_token:
            continue
        try:
            gap_kind = ChallengeDeficitKind(gap_kind_text)
        except ValueError:
            continue
        if subject_token == "__all__":
            deficit = ChallengeDeficit(
                scope_kind=ChallengeDeficitScopeKind.ALL,
                gap_kind=gap_kind,
            )
        else:
            deficit = ChallengeDeficit(
                scope_kind=ChallengeDeficitScopeKind.CATEGORY,
                gap_kind=gap_kind,
                category=subject_token,
            )
        token = (deficit.scope_kind, deficit.gap_kind, deficit.category)
        if token in seen:
            continue
        seen.add(token)
        deficits.append(deficit)
    return deficits


def _requirement_repair_targets(
    deficits: list[RequirementDeficit],
    *,
    requirement_audit: RequirementAuditEvaluation,
) -> list[dict[str, Any]]:
    if not deficits:
        return []
    targets: list[dict[str, Any]] = []
    audit_gap_kinds = {
        deficit.gap_kind for deficit in deficits if deficit.subject_kind is RequirementDeficitSubjectKind.AUDIT
    }
    if RequirementDeficitKind.MISSING in audit_gap_kinds:
        targets.append(
            {
                "kind": "requirement_audit",
                "gap_kind": "missing",
                "message": "Include `requirement_audit.items` with exact requirement ids, exact `status` values, and evidence for every passed item.",
            }
        )
    if RequirementDeficitKind.INVALID_SHAPE in audit_gap_kinds:
        targets.append(
            {
                "kind": "requirement_audit",
                "gap_kind": "invalid_shape",
                "message": "Use a `requirement_audit` object with an `items` list of requirement entries, not an invalid payload shape.",
            }
        )
    if RequirementDeficitKind.INCOMPLETE in audit_gap_kinds:
        targets.append(
            {
                "kind": "requirement_audit",
                "gap_kind": "incomplete",
                "message": "Set `requirement_audit.completeness_verdict` to `pass` or `fail` so it matches the reported items truthfully.",
            }
        )

    for gap_kind, message_template in (
        (RequirementDeficitKind.MISSING, "Add required `requirement_audit.items` for: {items}."),
        (RequirementDeficitKind.EVIDENCE_MISSING, "Add `evidence` arrays for passed `requirement_audit.items`: {items}."),
        (RequirementDeficitKind.EVIDENCE_UNVERIFIED, "Replace unverifiable evidence for `requirement_audit.items`: {items}."),
        (RequirementDeficitKind.GAP_MISSING, "If these requirements remain `fail`, add truthful `gap` descriptions: {items}."),
        (RequirementDeficitKind.STATUS_INVALID, "Use exact `status: \"pass\"` or `status: \"fail\"` for: {items}."),
        (RequirementDeficitKind.DUPLICATE_ID, "Use each requirement id only once in `requirement_audit.items`: {items}."),
        (RequirementDeficitKind.FAIL_DECLARED, "Either resolve these failed requirements with evidence or keep them truthfully failed with real gap descriptions: {items}."),
    ):
        item_ids: list[str] = []
        for deficit in deficits:
            if deficit.subject_kind is not RequirementDeficitSubjectKind.REQUIREMENT or deficit.gap_kind is not gap_kind:
                continue
            requirement_id = str(deficit.requirement_id or "").strip()
            if requirement_id and requirement_id not in item_ids:
                item_ids.append(requirement_id)
        if not item_ids:
            continue
        targets.append(
            {
                "kind": "requirement_audit",
                "gap_kind": gap_kind.value,
                "requirement_ids": item_ids,
                "message": message_template.format(items=", ".join(item_ids)),
            }
        )

    item_placeholders: list[str] = []
    for deficit in deficits:
        if deficit.subject_kind is not RequirementDeficitSubjectKind.ITEM:
            continue
        if deficit.gap_kind not in {RequirementDeficitKind.INVALID_SHAPE, RequirementDeficitKind.MISSING}:
            continue
        placeholder = str(deficit.item_placeholder or "").strip()
        if placeholder and placeholder not in item_placeholders:
            item_placeholders.append(placeholder)
    if item_placeholders:
        targets.append(
            {
                "kind": "requirement_audit",
                "gap_kind": "item_shape",
                "message": "Repair malformed `requirement_audit.items` entries so each item has a non-empty `id`, valid `status`, and the required supporting fields.",
                "items": item_placeholders,
            }
        )

    if requirement_audit.diagnostics:
        gap_description = _first_gap_description(requirement_audit.diagnostics)
        if gap_description and targets:
            targets[0].setdefault("gap_description", gap_description)
    return targets


def _requirement_deficits(entries: list[str]) -> list[RequirementDeficit]:
    deficits: list[RequirementDeficit] = []
    seen: set[tuple[RequirementDeficitSubjectKind, RequirementDeficitKind, str | None, str | None]] = set()
    for raw_entry in entries:
        entry = str(raw_entry).strip()
        if not entry:
            continue
        subject_token, sep, gap_kind_text = entry.partition(":")
        if sep != ":":
            continue
        subject_token = subject_token.strip()
        gap_kind_text = gap_kind_text.strip()
        if not subject_token:
            continue
        try:
            gap_kind = RequirementDeficitKind(gap_kind_text)
        except ValueError:
            continue
        if subject_token == "__audit__":
            deficit = RequirementDeficit(
                subject_kind=RequirementDeficitSubjectKind.AUDIT,
                gap_kind=gap_kind,
            )
        elif subject_token.startswith("__item_"):
            deficit = RequirementDeficit(
                subject_kind=RequirementDeficitSubjectKind.ITEM,
                gap_kind=gap_kind,
                item_placeholder=subject_token,
            )
        else:
            deficit = RequirementDeficit(
                subject_kind=RequirementDeficitSubjectKind.REQUIREMENT,
                gap_kind=gap_kind,
                requirement_id=subject_token,
            )
        token = (deficit.subject_kind, deficit.gap_kind, deficit.requirement_id, deficit.item_placeholder)
        if token in seen:
            continue
        seen.add(token)
        deficits.append(deficit)
    return deficits


def _truth_claim_repair_targets(
    deficits: list[TruthClaimDeficit],
    *,
    truth_claims: TruthClaimsEvaluation,
) -> list[dict[str, Any]]:
    if not deficits:
        return []

    grouped: dict[TruthClaimDeficitKind, list[str]] = {}
    for deficit in deficits:
        grouped.setdefault(deficit.gap_kind, [])
        if deficit.field not in grouped[deficit.gap_kind]:
            grouped[deficit.gap_kind].append(deficit.field)

    targets: list[dict[str, Any]] = []
    invalid_shape_fields = grouped.get(TruthClaimDeficitKind.INVALID_SHAPE, [])
    if invalid_shape_fields:
        targets.append(
            {
                "kind": "truth_claims",
                "gap_kind": "invalid_shape",
                "fields": invalid_shape_fields,
                "message": "Use a `truth_claims` object with supported fields such as `modified_files` and `tests_ran`.",
            }
        )

    for gap_kind, message_template in (
        (TruthClaimDeficitKind.UNVERIFIED, "Keep `truth_claims` aligned with actual repository changes and executed commands, especially: {fields}."),
        (TruthClaimDeficitKind.UNCHECKABLE, "Replace uncheckable `truth_claims` with checkable file or command claims, especially: {fields}."),
    ):
        fields = grouped.get(gap_kind, [])
        if not fields:
            continue
        targets.append(
            {
                "kind": "truth_claims",
                "gap_kind": gap_kind,
                "fields": fields,
                "message": message_template.format(fields=", ".join(fields)),
            }
        )

    if truth_claims.diagnostics:
        gap_description = _first_gap_description(truth_claims.diagnostics)
        if gap_description and targets:
            targets[0].setdefault("gap_description", gap_description)
    return targets


def _truth_claim_deficits(entries: list[str]) -> list[TruthClaimDeficit]:
    deficits: list[TruthClaimDeficit] = []
    seen: set[tuple[str, TruthClaimDeficitKind, str | None]] = set()
    for raw_entry in entries:
        entry = str(raw_entry).strip()
        if not entry:
            continue
        deficit: TruthClaimDeficit | None = None
        if entry == "__truth_claims__:invalid_shape":
            deficit = TruthClaimDeficit(
                field="__truth_claims__",
                gap_kind=TruthClaimDeficitKind.INVALID_SHAPE,
            )
        else:
            parts = [part.strip() for part in entry.rsplit(":", 2)]
            if len(parts) != 3:
                continue
            field_name, claim_identity, gap_kind_text = parts
            if not field_name:
                continue
            try:
                gap_kind = TruthClaimDeficitKind(gap_kind_text)
            except ValueError:
                continue
            if gap_kind is TruthClaimDeficitKind.INVALID_SHAPE:
                continue
            deficit = TruthClaimDeficit(
                field=field_name,
                gap_kind=gap_kind,
                claim_identity=claim_identity or None,
            )
        token = (deficit.field, deficit.gap_kind, deficit.claim_identity)
        if token in seen:
            continue
        seen.add(token)
        deficits.append(deficit)
    return deficits


def _invariant_repair_targets(
    deficits: list[InvariantDeficit],
    *,
    invariant_report: InvariantReport | None,
) -> list[dict[str, Any]]:
    if not deficits and (invariant_report is None or invariant_report.ok):
        return []

    failing_paths: list[str] = []
    if invariant_report is not None:
        failing_paths = [
            result.test_path
            for result in invariant_report.results
            if result.status in {"fail", "error", "missing"}
        ]
    if not failing_paths:
        for deficit in deficits:
            if deficit.test_path and deficit.test_path not in failing_paths:
                failing_paths.append(deficit.test_path)
    return [
        {
            "kind": "invariants",
            "gap_kind": "failed",
            "paths": failing_paths,
            "message": (
                "Resolve the invariant failures before claiming completion, or end truthfully if the invariant gap is still real."
                if failing_paths
                else "Resolve the invariant failure before claiming completion, or end truthfully if the invariant gap is still real."
            ),
        }
    ]


def _invariant_deficits(entries: list[str]) -> list[InvariantDeficit]:
    deficits: list[InvariantDeficit] = []
    seen: set[tuple[str, InvariantDeficitKind]] = set()
    for raw_entry in entries:
        entry = str(raw_entry).strip()
        if not entry:
            continue
        test_path, sep, gap_kind_text = entry.rpartition(":")
        if sep != ":":
            continue
        test_path = test_path.strip()
        gap_kind_text = gap_kind_text.strip()
        if not test_path:
            continue
        try:
            gap_kind = InvariantDeficitKind(gap_kind_text)
        except ValueError:
            continue
        token = (test_path, gap_kind)
        if token in seen:
            continue
        seen.add(token)
        deficits.append(InvariantDeficit(test_path=test_path, gap_kind=gap_kind))
    return deficits


def _gap_description(value: Mapping[str, Any] | None) -> str | None:
    if not isinstance(value, Mapping):
        return None
    token = str(value.get("gap_description") or "").strip()
    return token or None


def _first_gap_description(values: list[dict[str, Any]]) -> str | None:
    for value in values:
        token = _gap_description(value)
        if token:
            return token
    return None
```

### `cortex/executive.py`

```python
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

_LAYER1_PART_A_PATH = Path(__file__).resolve().parent / "data" / "layer1_part_a.md"
_LAYER1_PART_B_PATH = Path(__file__).resolve().parent / "data" / "layer1_part_b.md"
_IDENTITY_PREAMBLE_PATH = Path(__file__).resolve().parent / "data" / "identity_preamble.md"
_WORD_RE = re.compile(r"[A-Za-z0-9_]+")

_STOPWORDS = set(
    "a an and agent are as at be by code error file for from human in into is it its of on or output claim "
    "contradicted that the their then this to was were with".split()
)
_TOKEN_CANONICAL = {
    "verification": "verify",
    "verifications": "verify",
    "verified": "verify",
    "verifying": "verify",
    "defense": "defend",
    "defences": "defend",
}


def _tokenize_keywords(text: str) -> set[str]:
    return {
        token
        for raw in _WORD_RE.findall(text.lower())
        if (token := _normalize_keyword(raw))
        and len(token) >= 3
        and token not in _STOPWORDS
        and not token.isdigit()
    }


def _normalize_keyword(raw: str) -> str:
    token = str(raw).strip().lower().strip("_")
    if not token:
        return ""
    if token.startswith("verif"):
        token = "verify"
    elif token.startswith("defenc") or token.startswith("defens"):
        token = "defend"
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith("ing") and len(token) > 5:
        token = token[:-3]
    elif token.endswith("ed") and len(token) > 4:
        token = token[:-2]
    elif token.endswith("s") and len(token) > 3:
        token = token[:-1]
    return _TOKEN_CANONICAL.get(token, token)


def _keyword_overlap(left: str, right: str) -> int:
    return len(_tokenize_keywords(left) & _tokenize_keywords(right))


def _canonical_phrase(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def effective_weight(entry: dict[str, Any], current_session_count: int, halflife_sessions: int = 30) -> float:
    current = max(0, int(current_session_count))
    half = max(1, int(halflife_sessions))
    last_accessed = max(0, int(entry.get("last_accessed_at_session", 0)))
    strength = max(1, int(entry.get("strength", 1)))
    sessions_since = max(0, current - last_accessed)
    recency = 1.0 / (1.0 + (sessions_since / half))
    return strength * recency


@lru_cache(maxsize=1)
def get_base_executive_function() -> tuple[str, str]:
    return (
        _read_layer1_asset(_LAYER1_PART_A_PATH, "Part A"),
        _read_layer1_asset(_LAYER1_PART_B_PATH, "Part B"),
    )


@lru_cache(maxsize=1)
def get_identity_preamble() -> str:
    return _read_layer1_asset(_IDENTITY_PREAMBLE_PATH, "Identity preamble")


def _read_layer1_asset(path: Path, label: str) -> str:
    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError(f"Unable to read Layer 1 {label} asset: {path}") from exc
    if not content:
        raise ValueError(f"Layer 1 {label} asset is empty: {path}")
    return content


def _find_consolidation_match(entries: list[dict[str, Any]], *, event_type: str, trigger_pattern: str, error_pattern: str) -> dict[str, Any] | None:
    for entry in entries:
        if str(entry.get("type") or "") != event_type:
            continue
        existing_trigger = str(entry.get("trigger_pattern") or "")
        existing_error = str(entry.get("error_pattern") or "")
        if (
            _canonical_phrase(existing_trigger) == _canonical_phrase(trigger_pattern)
            and _canonical_phrase(existing_error) == _canonical_phrase(error_pattern)
        ):
            return entry
        trigger_overlap = _keyword_overlap(existing_trigger, trigger_pattern)
        error_overlap = _keyword_overlap(existing_error, error_pattern)
        if trigger_overlap >= 2 and error_overlap >= 2:
            return entry
    return None


def consolidate_event(store: Any, *, event_type: str, trigger_pattern: str, error_pattern: str, resolution: str, session_id: str) -> dict[str, Any]:
    current_session = store.get_session_count()
    entries = store.get_executive_memory()
    match = _find_consolidation_match(
        entries,
        event_type=str(event_type),
        trigger_pattern=str(trigger_pattern),
        error_pattern=str(error_pattern),
    )
    if match:
        updated_strength = int(match.get("strength", 1)) + 1
        store.update_executive_entry(
            str(match["id"]),
            strength=updated_strength,
            last_accessed_at_session=current_session,
        )
        merged = dict(match)
        merged["strength"] = updated_strength
        merged["last_accessed_at_session"] = current_session
        return merged
    return store.record_executive_event(
        str(event_type),
        str(trigger_pattern),
        str(error_pattern),
        str(resolution),
        str(session_id),
    )


def run_decay(store: Any, *, halflife_sessions: int = 30, threshold: float = 0.3, min_hold_sessions: int = 3) -> int:
    current_session = store.get_session_count()
    prune_ids: list[str] = []
    for entry in store.get_executive_memory():
        created_at = max(0, int(entry.get("created_at_session", 0)))
        if current_session - created_at < max(0, int(min_hold_sessions)):
            continue
        if effective_weight(entry, current_session, halflife_sessions) < float(threshold):
            prune_ids.append(str(entry.get("id") or ""))
    store.delete_executive_entries(prune_ids)
    return len([eid for eid in prune_ids if eid])


def record_stop_failure_event(
    store: Any,
    *,
    session_id: str,
    structured_stop_violation: bool,
    challenge_coverage_missing: bool,
    challenge_report: Mapping[str, Any] | None,
    requirements_gate_gap: bool,
    requirement_audit_report: Mapping[str, Any] | None,
    truth_claims_report: Mapping[str, Any] | None,
    invariant_report: Mapping[str, Any] | None,
    previous_signature: str | None = None,
    signature_claim: Callable[[str], bool] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    missing = (
        [str(item).strip() for item in challenge_report["missing_categories"] if str(item).strip()]
        if isinstance(challenge_report, Mapping) and isinstance(challenge_report.get("missing_categories"), list)
        else []
    )
    req_errors = (
        [str(item).strip() for item in requirement_audit_report["errors"] if str(item).strip()][:2]
        if isinstance(requirement_audit_report, Mapping) and isinstance(requirement_audit_report.get("errors"), list)
        else []
    )
    truth_errors = (
        [str(item).strip() for item in truth_claims_report["errors"] if str(item).strip()][:2]
        if isinstance(truth_claims_report, Mapping) and isinstance(truth_claims_report.get("errors"), list)
        else []
    )
    invariant_failed = isinstance(invariant_report, Mapping) and invariant_report.get("ok") is False
    if structured_stop_violation:
        kind, event_type = "structured_stop_violation", "metacognitive"
        trigger = "stop payload lacked structured evidence fields"
        error = "completion claim submitted without machine-readable stop fields"
        resolution = "emit payload.stop_fields or STOP_FIELDS_JSON with evidence before claiming completion"
    elif requirements_gate_gap:
        kind, event_type = "requirements_gate_gap", "technical"
        trigger = "stop requirement or truth evidence gap"
        error = "completion claim included unverified requirement/truth evidence"
        resolution = "add requirement_audit and truth_claims entries backed by observed evidence"
    elif challenge_coverage_missing or missing:
        kind, event_type = "challenge_coverage_gap", "technical"
        scope = ", ".join(missing) if missing else "required categories"
        trigger = f"stop challenge coverage missing ({scope})"
        error = "completion claim omitted required challenge coverage evidence"
        resolution = "provide challenge_coverage covering all active categories before completion"
    elif invariant_failed:
        kind, event_type = "invariant_failure", "technical"
        trigger = "stop invariant suite failure"
        error = "completion claim submitted while invariants were failing"
        resolution = "fix failing invariants and rerun invariant suite before completion"
    else:
        return None, None
    signature = json.dumps(
        {"kind": kind, "missing_categories": missing, "req_errors": req_errors, "truth_errors": truth_errors},
        sort_keys=True,
        separators=(",", ":"),
    )
    if signature == str(previous_signature or ""):
        return None, signature
    if signature_claim is not None and not signature_claim(signature):
        return None, signature
    return (
        consolidate_event(
            store,
            event_type=event_type,
            trigger_pattern=trigger,
            error_pattern=error,
            resolution=resolution,
            session_id=session_id,
        ),
        signature,
    )


def _format_learned_entry(entry: dict[str, Any], *, sessions_since: int) -> str:
    strength = max(1, int(entry.get("strength", 1)))
    trigger = str(entry.get("trigger_pattern") or "").strip()
    error = str(entry.get("error_pattern") or "").strip()
    resolution = str(entry.get("resolution") or "").strip()
    guidance = f"When {trigger}, avoid {error}. Correct action: {resolution}."
    return f"[reinforced {strength} times, last relevant {sessions_since} sessions ago]\n{guidance}"


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def get_learned_executive_function(store: Any, *, halflife_sessions: int, inject_threshold: float, decay_threshold: float, max_entries: int, max_tokens: int, min_hold_sessions: int) -> str:
    current_session = store.get_session_count()
    candidates: list[dict[str, Any]] = []
    for entry in store.get_executive_memory():
        weight = effective_weight(entry, current_session, halflife_sessions)
        sessions_since = max(0, current_session - int(entry.get("last_accessed_at_session", 0)))
        is_recent_hold = sessions_since <= max(0, int(min_hold_sessions))
        if weight >= float(inject_threshold) or (is_recent_hold and weight >= float(decay_threshold)):
            candidate = dict(entry)
            candidate["effective_weight"] = weight
            candidate["sessions_since"] = sessions_since
            candidates.append(candidate)
    candidates.sort(
        key=lambda item: (
            float(item["effective_weight"]),
            int(item.get("strength", 1)),
            -int(item.get("sessions_since", 0)),
        ),
        reverse=True,
    )

    selected: list[dict[str, Any]] = []
    token_budget = max(0, int(max_tokens))
    used_tokens = _approx_tokens("## Learned patterns from this project")
    for entry in candidates:
        if len(selected) >= max(1, int(max_entries)):
            break
        rendered = _format_learned_entry(entry, sessions_since=int(entry["sessions_since"]))
        rendered_tokens = _approx_tokens(rendered)
        if used_tokens + rendered_tokens > token_budget:
            continue
        used_tokens += rendered_tokens
        selected.append(entry)

    if not selected:
        return ""

    for entry in selected:
        store.update_executive_entry(
            str(entry["id"]),
            last_accessed_at_session=current_session,
        )

    lines = ["## Learned patterns from this project", ""]
    for entry in selected:
        lines.append(_format_learned_entry(entry, sessions_since=int(entry["sessions_since"])))
        lines.append("")
    return "\n".join(lines).strip()
```

### `cortex/graveyard.py`

```python
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Iterable

from .genome import GraveyardConfig
from .store import SQLiteStore


_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_SYNONYM_CANONICAL = {
    "redis": "cache",
    "caching": "cache",
    "latency": "timeout",
    "slow": "timeout",
    "slowness": "timeout",
    "crash": "fail",
    "crashed": "fail",
    "failure": "fail",
    "failed": "fail",
    "error": "fail",
    "errors": "fail",
    "exception": "fail",
    "exceptions": "fail",
    "connection": "connect",
    "connections": "connect",
    "verification": "verify",
    "verifications": "verify",
    "verified": "verify",
    "verifying": "verify",
    "defense": "defend",
    "defences": "defend",
}


@dataclass(slots=True)
class GraveyardMatch:
    entry_id: int
    score: float
    summary: str
    reason: str
    files: list[str]
    keyword_overlap: list[str]
    file_overlap: list[str]
    semantic_score: float
    created_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "entry_id": self.entry_id,
            "score": round(self.score, 3),
            "summary": self.summary,
            "reason": self.reason,
            "files": self.files,
            "keyword_overlap": self.keyword_overlap,
            "file_overlap": self.file_overlap,
            "semantic_score": round(self.semantic_score, 3),
            "created_at": self.created_at,
        }


class Graveyard:
    def __init__(self, store: SQLiteStore, config: GraveyardConfig) -> None:
        self.store = store
        self.config = config

    def record_failure(
        self,
        session_id: str | None,
        summary: str,
        reason: str,
        files: Iterable[str] = (),
    ) -> None:
        if not self.config.enabled:
            return
        file_list = [str(path) for path in files]
        keywords = sorted(self._keywords(summary) | self._keywords(reason))
        self.store.insert_graveyard(
            session_id=session_id,
            summary=summary,
            reason=reason,
            files=file_list,
            keywords=keywords,
        )

    def find_similar(
        self,
        summary: str,
        files: Iterable[str] = (),
        *,
        max_matches: int | None = None,
    ) -> list[GraveyardMatch]:
        if not self.config.enabled:
            return []

        query_keywords = self._keywords(summary)
        query_tokens = self._tokenize(summary)
        query_token_set = set(query_tokens)
        query_files = {self._norm_path(p) for p in files if p}
        if not query_tokens and not query_files:
            return []

        corpus_entries = self.store.list_graveyard(limit=200)
        entries = self._load_candidate_entries(query_tokens=query_tokens)
        idf_source = corpus_entries or entries
        df = Counter(token for entry in idf_source for token in {str(v) for v in entry.get("keywords", [])})
        query_idf = {token: math.log((len(idf_source) + 1) / (df.get(token, 0) + 1)) + 1.0 for token in query_keywords}
        query_weight = sum(query_idf.values()) or 1.0
        scored: list[GraveyardMatch] = []
        for entry in entries:
            entry_keywords = {str(k) for k in entry.get("keywords", [])}
            entry_tokens = self._tokenize(f"{entry.get('summary', '')} {entry.get('reason', '')}")
            entry_files = {self._norm_path(p) for p in entry.get("files", [])}
            keyword_overlap = sorted(query_keywords & entry_keywords)
            file_overlap = sorted(query_files & entry_files)

            keyword_score = sum(query_idf[token] for token in keyword_overlap) / query_weight
            file_score = len(file_overlap) / max(1, len(query_files)) if query_files else 0.0
            semantic_score = self._token_jaccard(query_token_set, set(entry_tokens))
            if (
                len(keyword_overlap) < self.config.min_keyword_overlap
                and not file_overlap
                and semantic_score < self.config.similarity_threshold
            ):
                continue

            score = (keyword_score * 0.45) + (file_score * 0.25) + (semantic_score * 0.30)
            if score < self.config.similarity_threshold:
                continue
            scored.append(
                GraveyardMatch(
                    entry_id=int(entry["id"]),
                    score=score,
                    summary=str(entry["summary"]),
                    reason=str(entry["reason"]),
                    files=list(entry["files"]),
                    keyword_overlap=keyword_overlap,
                    file_overlap=file_overlap,
                    semantic_score=semantic_score,
                    created_at=str(entry["created_at"]),
                )
            )

        scored.sort(key=lambda m: (m.score, m.entry_id), reverse=True)
        return scored[: (max_matches or self.config.max_matches)]

    def _load_candidate_entries(self, *, query_tokens: list[str]) -> list[dict[str, object]]:
        if not query_tokens:
            return self.store.list_graveyard(limit=200)
        candidates = self.store.list_graveyard_fts_candidates(tokens=query_tokens, limit=200, candidate_limit=80)
        if not candidates:
            return self.store.list_graveyard(limit=200)
        return candidates

    @staticmethod
    def _keywords(text: str) -> set[str]:
        return set(Graveyard._tokenize(text))

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        tokens: list[str] = []
        for raw in _WORD_RE.findall(text):
            token = Graveyard._normalize_token(raw)
            if token:
                tokens.append(token)
        return tokens

    @staticmethod
    def _normalize_token(token: str) -> str:
        value = token.lower().strip("_")
        if len(value) <= 2:
            return ""
        if value.startswith("verif"):
            value = "verify"
        elif value.startswith("defenc") or value.startswith("defens"):
            value = "defend"
        if value.endswith("ies") and len(value) > 4:
            value = value[:-3] + "y"
        elif value.endswith("ing") and len(value) > 5:
            value = value[:-3]
        elif value.endswith("ed") and len(value) > 4:
            value = value[:-2]
        elif value.endswith("s") and len(value) > 3:
            value = value[:-1]
        return _SYNONYM_CANONICAL.get(value, value)

    @staticmethod
    def _token_jaccard(left: set[str], right: set[str]) -> float:
        if not left or not right:
            return 0.0
        union = left | right
        if not union:
            return 0.0
        return len(left & right) / len(union)

    @staticmethod
    def _norm_path(path: str) -> str:
        parts = [p for p in str(PurePosixPath(path)).split("/") if p not in {"", "."}]
        return "/".join(parts)


def explainability_warnings(matches: list[dict[str, Any]]) -> list[str]:
    if not matches:
        return []
    top = matches[0]
    summary = str(top.get("summary") or "").strip()
    score = top.get("score")
    semantic_score = top.get("semantic_score")
    keyword_overlap = [str(v).strip() for v in top.get("keyword_overlap", []) if str(v).strip()]
    file_overlap = [str(v).strip() for v in top.get("file_overlap", []) if str(v).strip()]
    parts = ["Top graveyard match"]
    if summary:
        parts.append(f"summary='{summary[:120]}'")
    if isinstance(score, (int, float)):
        parts.append(f"score={float(score):.3f}")
    if isinstance(semantic_score, (int, float)):
        parts.append(f"semantic={float(semantic_score):.3f}")
    if keyword_overlap:
        parts.append("keyword_overlap=" + ",".join(keyword_overlap[:5]))
    if file_overlap:
        parts.append("file_overlap=" + ",".join(file_overlap[:3]))
    return ["; ".join(parts)]
```

### `cortex/retry.py`

```python
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

RETRYABLE_STATUSES: frozenset[str] = frozenset({"error", "failed", "fail"})
NON_RETRYABLE_REASONS: frozenset[str] = frozenset({"invariant_violation", "stop_gate_failure", "policy_violation", "challenge_failure", "permission_denied", "authentication_failure"})
CORRECTIVE_RETRYABLE: str = "corrective_retryable"
TERMINAL_HARD_GATE: str = "terminal_hard_gate"
_CORRECTIVE_CANONICAL: frozenset[str] = frozenset({"tool_error", "timeout", "shape_mismatch", "range_error", "format_error"})
_REASON_RETRY_LIMITS: Mapping[str, int] = {
    "timeout": 3,
    "tool_error": 3,
    "shape_mismatch": 2,
    "format_error": 2,
    "range_error": 1,
}
_DELTA_OBJECTIVE_KEYS: tuple[str, ...] = ("changed_files", "updated_files")
_DELTA_SENSITIVE_REASONS: frozenset[str] = frozenset({"shape_mismatch", "range_error", "format_error"})


@dataclass(slots=True)
class FailureVerdict:
    retryable: bool
    reason: str
    hard_stop: bool = False


@dataclass(slots=True)
class RetryVerdict:
    should_retry: bool
    hard_stop: bool
    failure_class: str
    reason: str
    budget_remaining: int
    budget_exhausted: bool
    decision_code: str
    failure_signature: str


def compute_retry_verdict(
    *,
    store: Any,
    session_id: str,
    payload: Mapping[str, Any],
    max_retries: int,
) -> RetryVerdict | None:
    failure = classify_failure(payload)
    if failure is None:
        return None
    reason = failure.reason
    reason_limit = reason_retry_limit(reason, default_limit=max_retries)
    attempts_state = store.get_retry_attempts(session_id, reason=reason)
    budget_state = _retry_budget_state(
        attempts=int(attempts_state["attempts"]),
        reason_attempts=int(attempts_state["reason_attempts"]),
        max_retries=max_retries,
        reason_limit=reason_limit,
    )
    signature = failure_signature(payload, reason=reason)
    delta_hash = objective_delta_hash(payload)
    delta_sensitive = reason in _DELTA_SENSITIVE_REASONS
    previous_delta_hash = (
        store.get_retry_delta_hash(session_id, reason, signature)
        if delta_sensitive
        else None
    )
    remaining_session = int(budget_state["remaining"])
    remaining_reason = int(budget_state["reason_remaining"])
    remaining = int(budget_state["budget_remaining"])
    terminal_code = (
        "hard_stop"
        if failure.hard_stop
        else "reason_budget_exhausted"
        if remaining_reason <= 0
        else "session_budget_exhausted"
        if remaining_session <= 0
        else ""
    )
    if terminal_code:
        return RetryVerdict(
            should_retry=False,
            hard_stop=terminal_code == "hard_stop",
            failure_class=TERMINAL_HARD_GATE if terminal_code == "hard_stop" else CORRECTIVE_RETRYABLE,
            reason=reason,
            budget_remaining=remaining,
            budget_exhausted=remaining == 0 or terminal_code != "hard_stop",
            decision_code=terminal_code,
            failure_signature=signature,
        )

    if delta_sensitive and previous_delta_hash is not None and not previous_delta_hash and not delta_hash:
        store.upsert_retry_delta_hash(
            session_id,
            reason=reason,
            failure_signature=signature,
            delta_hash=delta_hash,
        )
        return RetryVerdict(
            should_retry=False,
            hard_stop=False,
            failure_class=CORRECTIVE_RETRYABLE,
            reason=reason,
            budget_remaining=remaining,
            budget_exhausted=remaining == 0,
            decision_code="no_delta",
            failure_signature=signature,
        )

    outcome = _consume_retry_with_budget(
        store=store,
        session_id=session_id,
        reason=reason,
        max_retries=max_retries,
        reason_limit=reason_limit,
    )
    if delta_sensitive:
        store.upsert_retry_delta_hash(
            session_id,
            reason=reason,
            failure_signature=signature,
            delta_hash=delta_hash,
        )
    return RetryVerdict(
        should_retry=bool(outcome["consumed"]),
        hard_stop=False,
        failure_class=CORRECTIVE_RETRYABLE,
        reason=reason,
        budget_remaining=int(outcome["budget_remaining"]),
        budget_exhausted=bool(outcome["budget_exhausted"]),
        decision_code=str(outcome["decision_code"]),
        failure_signature=signature,
    )


def reason_retry_limit(reason: str, *, default_limit: int) -> int:
    return max(0, min(default_limit, int(_REASON_RETRY_LIMITS.get(reason, default_limit))))


def _retry_budget_state(
    *,
    attempts: int,
    reason_attempts: int,
    max_retries: int,
    reason_limit: int,
) -> dict[str, int | str]:
    session_limit = max(0, int(max_retries))
    reason_cap = max(0, int(reason_limit))
    session_attempts = max(0, int(attempts))
    reason_attempts = max(0, int(reason_attempts))
    remaining = max(0, session_limit - session_attempts)
    reason_remaining = max(0, reason_cap - reason_attempts)
    decision_code = "retry_allowed"
    if remaining <= 0:
        decision_code = "session_budget_exhausted"
    elif reason_remaining <= 0:
        decision_code = "reason_budget_exhausted"
    return {
        "attempts": session_attempts,
        "reason_attempts": reason_attempts,
        "remaining": remaining,
        "reason_remaining": reason_remaining,
        "budget_remaining": min(remaining, reason_remaining),
        "decision_code": decision_code,
    }


def _consume_retry_with_budget(
    *,
    store: Any,
    session_id: str,
    reason: str,
    max_retries: int,
    reason_limit: int,
) -> dict[str, int | bool | str]:
    for _ in range(16):
        attempts_state = store.get_retry_attempts(session_id, reason=reason)
        state = _retry_budget_state(
            attempts=int(attempts_state["attempts"]),
            reason_attempts=int(attempts_state["reason_attempts"]),
            max_retries=max_retries,
            reason_limit=reason_limit,
        )
        if state["decision_code"] != "retry_allowed":
            return {
                "consumed": False,
                "attempts": int(state["attempts"]),
                "reason_attempts": int(state["reason_attempts"]),
                "budget_remaining": int(state["budget_remaining"]),
                "decision_code": str(state["decision_code"]),
                "budget_exhausted": True,
            }

        write_outcome = store.try_increment_retry_attempts(
            session_id,
            reason=reason,
            expected_attempts=int(state["attempts"]),
            expected_reason_attempts=int(state["reason_attempts"]),
        )
        if bool(write_outcome["consumed"]):
            post = _retry_budget_state(
                attempts=int(write_outcome["attempts"]),
                reason_attempts=int(write_outcome["reason_attempts"]),
                max_retries=max_retries,
                reason_limit=reason_limit,
            )
            return {
                "consumed": True,
                "attempts": int(post["attempts"]),
                "reason_attempts": int(post["reason_attempts"]),
                "budget_remaining": int(post["budget_remaining"]),
                "decision_code": "retry_allowed",
                "budget_exhausted": int(post["budget_remaining"]) == 0,
            }

    final_attempts = store.get_retry_attempts(session_id, reason=reason)
    final_state = _retry_budget_state(
        attempts=int(final_attempts["attempts"]),
        reason_attempts=int(final_attempts["reason_attempts"]),
        max_retries=max_retries,
        reason_limit=reason_limit,
    )
    return {
        "consumed": False,
        "attempts": int(final_state["attempts"]),
        "reason_attempts": int(final_state["reason_attempts"]),
        "budget_remaining": int(final_state["budget_remaining"]),
        "decision_code": (
            str(final_state["decision_code"])
            if final_state["decision_code"] != "retry_allowed"
            else "retry_contention"
        ),
        "budget_exhausted": final_state["decision_code"] != "retry_allowed",
    }


def objective_delta_hash(payload: Mapping[str, Any]) -> str:
    files = _collect_objective_delta_files(payload)
    if not files:
        return ""
    return hashlib.sha256(
        json.dumps(files, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def failure_signature(payload: Mapping[str, Any], *, reason: str) -> str:
    canonical = {
        "reason": reason,
        "tool_name": _normalize_token(payload.get("tool_name")),
        "status": _normalize_token(payload.get("status")),
        "message": _normalize_token(payload.get("error") or payload.get("message") or payload.get("stderr"))[:240],
        "target_files": _normalize_files(payload.get("target_files")),
        "planned_files": _normalize_files(payload.get("planned_files")),
    }
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _canonical_reason(raw_reason: Any) -> str:
    token = re.sub(r"[^a-z0-9_]+", "_", re.sub(r"[\s\-]+", "_", str(raw_reason or "").lower().strip())).strip("_")
    if not token or token in _CORRECTIVE_CANONICAL:
        return token
    parts = set(token.split("_"))
    if {"shape", "mismatch"} <= parts:
        return "shape_mismatch"
    if {"range", "error"} <= parts:
        return "range_error"
    if {"format", "error"} <= parts:
        return "format_error"
    return "timeout" if "timeout" in parts else token


def classify_failure(payload: Mapping[str, Any]) -> FailureVerdict | None:
    if str(payload.get("status", "")).lower().strip() not in RETRYABLE_STATUSES:
        return None
    reason = _canonical_reason(payload.get("failure_reason") or payload.get("reason"))
    if reason in NON_RETRYABLE_REASONS:
        return FailureVerdict(retryable=False, reason=reason, hard_stop=True)
    if not reason:
        inferred = _canonical_reason(payload.get("error") or payload.get("message") or payload.get("stderr"))
        if inferred in _CORRECTIVE_CANONICAL:
            return FailureVerdict(retryable=True, reason=inferred)
        return FailureVerdict(retryable=True, reason="tool_error")
    if reason in _CORRECTIVE_CANONICAL:
        return FailureVerdict(retryable=True, reason=reason)
    return FailureVerdict(retryable=False, reason=reason, hard_stop=True)


def _normalize_token(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _normalize_files(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tokens = [str(item).strip() for item in value]
    return sorted({token for token in tokens if token})


def _collect_objective_delta_files(payload: Mapping[str, Any]) -> list[str]:
    files: list[str] = []
    for key in _DELTA_OBJECTIVE_KEYS:
        value = payload.get(key)
        if not isinstance(value, list):
            continue
        files.extend(str(item).strip() for item in value)
    return sorted({token for token in files if token})
```

### `cortex/store.py`

```python
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator
from uuid import uuid4

DB_SCHEMA_VERSION = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_FTS_TOKEN_RE = re.compile(r"^[a-z0-9_]+$")
_COMPACT_TEXT_FIELDS = ("last_assistant_message", "stdout", "stderr", "output", "message")
_COMPACT_TEXT_MAX_LEN = 2048


@dataclass(slots=True)
class SQLiteStore:
    db_path: Path
    lock_retry_attempts: int = 3
    lock_retry_backoff_ms: int = 25
    busy_timeout_ms: int = 5000

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(f"PRAGMA user_version = {DB_SCHEMA_VERSION}")
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                  session_id TEXT PRIMARY KEY,
                  started_at TEXT NOT NULL,
                  ended_at TEXT,
                  status TEXT NOT NULL,
                  genome_path TEXT,
                  metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS graveyard (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  summary TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  files_json TEXT NOT NULL,
                  keywords_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS invariants (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  test_path TEXT NOT NULL,
                  status TEXT NOT NULL,
                  duration_ms INTEGER NOT NULL,
                  stdout TEXT NOT NULL,
                  stderr TEXT NOT NULL,
                  graduated_from TEXT,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS challenge_results (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  category TEXT NOT NULL,
                  covered INTEGER NOT NULL,
                  evidence_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT NOT NULL,
                  hook TEXT NOT NULL,
                  tool_name TEXT,
                  status TEXT,
                  payload_json TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS retry_budget (
                  session_id TEXT PRIMARY KEY,
                  attempts INTEGER NOT NULL DEFAULT 0,
                  updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS retry_reason_budget (
                  session_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  attempts INTEGER NOT NULL DEFAULT 0,
                  updated_at TEXT NOT NULL,
                  PRIMARY KEY (session_id, reason)
                );

                CREATE TABLE IF NOT EXISTS retry_delta_state (
                  session_id TEXT NOT NULL,
                  reason TEXT NOT NULL,
                  failure_signature TEXT NOT NULL,
                  last_delta_hash TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  PRIMARY KEY (session_id, reason, failure_signature)
                );

                CREATE TABLE IF NOT EXISTS cortex_meta (
                  key TEXT PRIMARY KEY,
                  value_text TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS executive_memory (
                  id TEXT PRIMARY KEY,
                  type TEXT NOT NULL,
                  trigger_pattern TEXT NOT NULL,
                  error_pattern TEXT NOT NULL,
                  resolution TEXT NOT NULL,
                  strength INTEGER NOT NULL DEFAULT 1,
                  created_at_session INTEGER NOT NULL,
                  last_accessed_at_session INTEGER NOT NULL,
                  source_session_id TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_counter_allocations (
                  session_id TEXT PRIMARY KEY,
                  counter INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS executive_stop_signatures (
                  session_id TEXT PRIMARY KEY,
                  signature TEXT NOT NULL,
                  updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_session_hook ON events(session_id, hook);
                CREATE INDEX IF NOT EXISTS idx_graveyard_session ON graveyard(session_id);
                CREATE INDEX IF NOT EXISTS idx_challenge_results_session_category
                  ON challenge_results(session_id, category);
                CREATE INDEX IF NOT EXISTS idx_invariants_session_status
                  ON invariants(session_id, status);
                CREATE INDEX IF NOT EXISTS idx_executive_memory_type_strength
                  ON executive_memory(type, strength DESC);
                """
            )
            self._purge_transient_session_state(conn)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute(f"PRAGMA busy_timeout = {max(0, int(self.busy_timeout_ms))}")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _run_write(self, operation: Callable[[sqlite3.Connection], None]) -> None:
        attempts = max(0, int(self.lock_retry_attempts)) + 1
        backoff = max(0, int(self.lock_retry_backoff_ms)) / 1000.0
        for attempt in range(attempts):
            try:
                with self.connection() as conn:
                    operation(conn)
                return
            except sqlite3.OperationalError as exc:
                if not self._is_lock_error(exc) or attempt >= attempts - 1:
                    raise
                if backoff > 0:
                    time.sleep(backoff * (2**attempt))

    @staticmethod
    def _is_lock_error(exc: sqlite3.OperationalError) -> bool:
        return any(msg in str(exc).lower() for msg in ("database is locked", "database table is locked"))

    def upsert_session_start(
        self, session_id: str, status: str, genome_path: str | None, metadata: dict[str, Any] | None = None
    ) -> None:
        self._execute_write(
            """
            INSERT INTO sessions (session_id, started_at, status, genome_path, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
              status=excluded.status,
              genome_path=excluded.genome_path,
              metadata_json=excluded.metadata_json
            """,
            (
                session_id,
                _utc_now(),
                status,
                genome_path,
                json.dumps(metadata or {}, sort_keys=True),
            ),
        )

    def ensure_session_start(
        self, session_id: str, status: str, genome_path: str | None, metadata: dict[str, Any] | None = None
    ) -> None:
        self._execute_write(
            """
            INSERT OR IGNORE INTO sessions (session_id, started_at, status, genome_path, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                _utc_now(),
                status,
                genome_path,
                json.dumps(metadata or {}, sort_keys=True),
            ),
        )

    def close_session(self, session_id: str, status: str, metadata: dict[str, Any] | None = None) -> None:
        now = _utc_now()
        closed_filter = "session_id IN (SELECT session_id FROM sessions WHERE status != 'running' OR ended_at IS NOT NULL)"

        def _op(conn: sqlite3.Connection) -> None:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                UPDATE sessions
                SET ended_at = ?, status = ?, metadata_json = ?
                WHERE session_id = ?
                """,
                (
                    now,
                    status,
                    json.dumps(metadata or {}, sort_keys=True),
                    session_id,
                ),
            )
            conn.execute(f"DELETE FROM session_counter_allocations WHERE {closed_filter}")
            conn.execute(
                f"DELETE FROM executive_stop_signatures WHERE session_id <> ? AND {closed_filter}",
                (session_id,),
            )

        self._run_write(_op)

    def record_event(
        self,
        session_id: str,
        hook: str,
        payload: dict[str, Any],
        tool_name: str | None = None,
        status: str | None = None,
    ) -> None:
        compacted_payload = self._compact_event_payload(payload)
        self._execute_write(
            """
            INSERT INTO events (session_id, hook, tool_name, status, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                hook,
                tool_name,
                status,
                json.dumps(compacted_payload, sort_keys=True),
                _utc_now(),
            ),
        )

    def get_retry_delta_hash(self, session_id: str, reason: str, failure_signature: str) -> str | None:
        reason_token = str(reason or "").strip()
        signature_token = str(failure_signature or "").strip()
        if not reason_token or not signature_token:
            return None
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT last_delta_hash
                FROM retry_delta_state
                WHERE session_id = ? AND reason = ? AND failure_signature = ?
                LIMIT 1
                """,
                (session_id, reason_token, signature_token),
            ).fetchone()
        if row is None:
            return None
        return str(row["last_delta_hash"] or "")

    def upsert_retry_delta_hash(
        self,
        session_id: str,
        *,
        reason: str,
        failure_signature: str,
        delta_hash: str,
    ) -> None:
        reason_token = str(reason or "").strip()
        signature_token = str(failure_signature or "").strip()
        if not reason_token or not signature_token:
            return
        self._execute_write(
            """
            INSERT INTO retry_delta_state (session_id, reason, failure_signature, last_delta_hash, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id, reason, failure_signature) DO UPDATE SET
              last_delta_hash = excluded.last_delta_hash,
              updated_at = excluded.updated_at
            """,
            (
                session_id,
                reason_token,
                signature_token,
                str(delta_hash or ""),
                _utc_now(),
            ),
        )

    def get_retry_attempts(self, session_id: str, *, reason: str) -> dict[str, int]:
        reason_token = str(reason or "").strip()
        if not reason_token:
            return {"attempts": 0, "reason_attempts": 0}
        with self.connection() as conn:
            session_row = conn.execute(
                "SELECT attempts FROM retry_budget WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            reason_row = conn.execute(
                "SELECT attempts FROM retry_reason_budget WHERE session_id = ? AND reason = ?",
                (session_id, reason_token),
            ).fetchone()
        return {
            "attempts": int(session_row["attempts"]) if session_row is not None else 0,
            "reason_attempts": int(reason_row["attempts"]) if reason_row is not None else 0,
        }

    def try_increment_retry_attempts(
        self,
        session_id: str,
        *,
        reason: str,
        expected_attempts: int,
        expected_reason_attempts: int,
    ) -> dict[str, int | bool]:
        reason_token = str(reason or "").strip()
        outcome: dict[str, int | bool] = {
            "consumed": False,
            "attempts": max(0, int(expected_attempts)),
            "reason_attempts": max(0, int(expected_reason_attempts)),
        }
        if not reason_token:
            return outcome

        def _op(conn: sqlite3.Connection) -> None:
            now = _utc_now()
            conn.execute("BEGIN IMMEDIATE")
            self._ensure_retry_budget_rows(conn, session_id=session_id, reason=reason_token, now=now)
            session_row = conn.execute(
                "SELECT attempts FROM retry_budget WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            reason_row = conn.execute(
                "SELECT attempts FROM retry_reason_budget WHERE session_id = ? AND reason = ?",
                (session_id, reason_token),
            ).fetchone()
            session_attempts = int(session_row["attempts"]) if session_row is not None else 0
            reason_attempts = int(reason_row["attempts"]) if reason_row is not None else 0

            if (
                session_attempts == max(0, int(expected_attempts))
                and reason_attempts == max(0, int(expected_reason_attempts))
            ):
                conn.execute(
                    """
                    UPDATE retry_budget
                    SET attempts = attempts + 1, updated_at = ?
                    WHERE session_id = ?
                    """,
                    (now, session_id),
                )
                conn.execute(
                    """
                    UPDATE retry_reason_budget
                    SET attempts = attempts + 1, updated_at = ?
                    WHERE session_id = ? AND reason = ?
                    """,
                    (now, session_id, reason_token),
                )
                session_attempts += 1
                reason_attempts += 1
                outcome["consumed"] = True

            outcome["attempts"] = session_attempts
            outcome["reason_attempts"] = reason_attempts

        self._run_write(_op)
        return outcome

    def insert_graveyard(
        self,
        session_id: str | None,
        summary: str,
        reason: str,
        files: list[str],
        keywords: list[str],
    ) -> None:
        self._execute_write(
            """
            INSERT INTO graveyard (session_id, summary, reason, files_json, keywords_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                summary,
                reason,
                json.dumps(files, sort_keys=True),
                json.dumps(keywords, sort_keys=True),
                _utc_now(),
            ),
        )

    def list_graveyard(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self._list_graveyard_rows(limit)
        return [self._graveyard_row_to_item(row) for row in rows]

    def list_graveyard_fts_candidates(
        self,
        *,
        tokens: list[str],
        limit: int = 200,
        candidate_limit: int = 80,
    ) -> list[dict[str, Any]] | None:
        terms = [t for t in tokens if _FTS_TOKEN_RE.match(t)]
        if not terms or not (rows := self._list_graveyard_rows(limit)):
            return []
        with self.connection() as conn:
            try:
                conn.execute(
                    "CREATE TEMP VIRTUAL TABLE IF NOT EXISTS _cortex_graveyard_fts "
                    "USING fts5(entry_id UNINDEXED, text)"
                )
                conn.execute("DELETE FROM _cortex_graveyard_fts")
            except sqlite3.OperationalError:
                return None

            conn.executemany(
                "INSERT INTO _cortex_graveyard_fts(entry_id, text) VALUES (?, ?)",
                [
                    (
                        str(row["id"]),
                        f"{row['summary']} {row['reason']} {row['keywords_json']}",
                    )
                    for row in rows
                ],
            )
            match_query = " OR ".join(terms[:12])
            matched = conn.execute(
                """
                SELECT entry_id
                FROM _cortex_graveyard_fts
                WHERE _cortex_graveyard_fts MATCH ?
                ORDER BY bm25(_cortex_graveyard_fts), CAST(entry_id AS INTEGER) DESC
                LIMIT ?
                """,
                (match_query, max(1, int(candidate_limit))),
            ).fetchall()

        if not matched:
            return []
        row_map = {int(row["id"]): row for row in rows}
        ordered_ids = [int(row["entry_id"]) for row in matched]
        return [self._graveyard_row_to_item(row_map[eid]) for eid in ordered_ids if eid in row_map]

    def record_invariant_result(
        self,
        session_id: str,
        test_path: str,
        status: str,
        duration_ms: int,
        stdout: str,
        stderr: str,
        graduated_from: str | None = None,
    ) -> None:
        self._execute_write(
            """
            INSERT INTO invariants
              (session_id, test_path, status, duration_ms, stdout, stderr, graduated_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                test_path,
                status,
                duration_ms,
                stdout,
                stderr,
                graduated_from,
                _utc_now(),
            ),
        )

    def record_challenge_result(
        self, session_id: str, category: str, covered: bool, evidence: dict[str, Any] | None = None
    ) -> None:
        self._execute_write(
            """
            INSERT INTO challenge_results (session_id, category, covered, evidence_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                category,
                1 if covered else 0,
                json.dumps(evidence or {}, sort_keys=True),
                _utc_now(),
            ),
        )

    def _execute_write(self, sql: str, params: tuple[Any, ...]) -> None:
        self._run_write(lambda conn: conn.execute(sql, params))

    def increment_session_counter(self) -> int:
        result = {"value": 0}

        def _op(conn: sqlite3.Connection) -> None:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO cortex_meta (key, value_text) VALUES ('session_counter', '0') ON CONFLICT(key) DO NOTHING")
            conn.execute("UPDATE cortex_meta SET value_text = CAST(COALESCE(value_text, '0') AS INTEGER) + 1 WHERE key = 'session_counter'")
            row = conn.execute("SELECT value_text FROM cortex_meta WHERE key = 'session_counter'").fetchone()
            result["value"] = int(row["value_text"]) if row is not None else 0

        self._run_write(_op)
        return int(result["value"])

    def allocate_session_counter(self, session_id: str) -> int:
        token = str(session_id or "").strip()
        if not token:
            return self.increment_session_counter()
        result = {"value": 0}

        def _op(conn: sqlite3.Connection) -> None:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT counter FROM session_counter_allocations WHERE session_id = ? LIMIT 1",
                (token,),
            ).fetchone()
            if existing is not None:
                result["value"] = int(existing["counter"])
                return
            conn.execute("INSERT INTO cortex_meta (key, value_text) VALUES ('session_counter', '0') ON CONFLICT(key) DO NOTHING")
            conn.execute("UPDATE cortex_meta SET value_text = CAST(COALESCE(value_text, '0') AS INTEGER) + 1 WHERE key = 'session_counter'")
            counter = conn.execute("SELECT value_text FROM cortex_meta WHERE key = 'session_counter'").fetchone()
            allocated = int(counter["value_text"]) if counter is not None else 0
            conn.execute(
                """
                INSERT INTO session_counter_allocations (session_id, counter)
                VALUES (?, ?)
                ON CONFLICT(session_id) DO NOTHING
                """,
                (token, allocated),
            )
            row = conn.execute(
                "SELECT counter FROM session_counter_allocations WHERE session_id = ? LIMIT 1",
                (token,),
            ).fetchone()
            result["value"] = int(row["counter"]) if row is not None else allocated

        self._run_write(_op)
        return int(result["value"])

    def claim_executive_stop_signature(self, session_id: str, signature: str) -> bool:
        sid = str(session_id or "").strip()
        sig = str(signature or "").strip()
        if not sid or not sig:
            return False
        claimed = {"value": False}

        def _op(conn: sqlite3.Connection) -> None:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT signature FROM executive_stop_signatures WHERE session_id = ? LIMIT 1",
                (sid,),
            ).fetchone()
            if row is not None and str(row["signature"] or "") == sig:
                claimed["value"] = False
                return
            conn.execute(
                """
                INSERT INTO executive_stop_signatures (session_id, signature, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                  signature = excluded.signature,
                  updated_at = excluded.updated_at
                """,
                (sid, sig, _utc_now()),
            )
            claimed["value"] = True

        self._run_write(_op)
        return bool(claimed["value"])

    def get_session_count(self) -> int:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT value_text FROM cortex_meta WHERE key = 'session_counter' LIMIT 1"
            ).fetchone()
        if row is None:
            return 0
        try:
            return int(row["value_text"])
        except (TypeError, ValueError):
            return 0

    def claim_meta_once(self, key: str, value: str = "1") -> bool:
        token = str(key or "").strip()
        if not token:
            return False
        claimed = {"value": False}

        def _op(conn: sqlite3.Connection) -> None:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT 1 FROM cortex_meta WHERE key = ? LIMIT 1",
                (token,),
            ).fetchone()
            if existing is not None:
                claimed["value"] = False
                return
            conn.execute(
                "INSERT INTO cortex_meta (key, value_text) VALUES (?, ?)",
                (token, str(value)),
            )
            claimed["value"] = True

        self._run_write(_op)
        return bool(claimed["value"])

    def record_executive_event(
        self,
        event_type: str,
        trigger: str,
        error: str,
        resolution: str,
        session_id: str,
    ) -> dict[str, Any]:
        current_session = self.get_session_count()
        row = {
            "id": f"exec-{uuid4().hex}",
            "type": str(event_type),
            "trigger_pattern": str(trigger),
            "error_pattern": str(error),
            "resolution": str(resolution),
            "strength": 1,
            "created_at_session": current_session,
            "last_accessed_at_session": current_session,
            "source_session_id": str(session_id),
        }
        self._execute_write(
            "INSERT INTO executive_memory (id, type, trigger_pattern, error_pattern, resolution, strength, created_at_session, last_accessed_at_session, source_session_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                row["id"],
                row["type"],
                row["trigger_pattern"],
                row["error_pattern"],
                row["resolution"],
                row["strength"],
                row["created_at_session"],
                row["last_accessed_at_session"],
                row["source_session_id"],
            ),
        )
        return row

    def get_executive_memory(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute("SELECT id, type, trigger_pattern, error_pattern, resolution, strength, created_at_session, last_accessed_at_session, source_session_id FROM executive_memory ORDER BY created_at_session DESC, id ASC").fetchall()
        return [
            {
                "id": str(row["id"]),
                "type": str(row["type"]),
                "trigger_pattern": str(row["trigger_pattern"]),
                "error_pattern": str(row["error_pattern"]),
                "resolution": str(row["resolution"]),
                "strength": int(row["strength"]),
                "created_at_session": int(row["created_at_session"]),
                "last_accessed_at_session": int(row["last_accessed_at_session"]),
                "source_session_id": str(row["source_session_id"]),
            }
            for row in rows
        ]

    def update_executive_entry(
        self,
        entry_id: str,
        *,
        strength: int | None = None,
        last_accessed_at_session: int | None = None,
    ) -> None:
        updates: list[str] = []
        params: list[Any] = []
        if strength is not None:
            updates.append("strength = ?")
            params.append(max(1, int(strength)))
        if last_accessed_at_session is not None:
            updates.append("last_accessed_at_session = ?")
            params.append(max(0, int(last_accessed_at_session)))
        if not updates:
            return
        params.append(str(entry_id))
        self._execute_write(
            f"UPDATE executive_memory SET {', '.join(updates)} WHERE id = ?",
            tuple(params),
        )

    def delete_executive_entries(self, ids: list[str]) -> None:
        tokens = [str(item).strip() for item in ids if str(item).strip()]
        if not tokens:
            return
        placeholders = ",".join(["?"] * len(tokens))
        self._execute_write(
            f"DELETE FROM executive_memory WHERE id IN ({placeholders})",
            tuple(tokens),
        )

    @staticmethod
    def _ensure_retry_budget_rows(conn: sqlite3.Connection, *, session_id: str, reason: str, now: str) -> None:
        conn.execute(
            """
            INSERT INTO retry_budget (session_id, attempts, updated_at)
            VALUES (?, 0, ?)
            ON CONFLICT(session_id) DO NOTHING
            """,
            (session_id, now),
        )
        conn.execute(
            """
            INSERT INTO retry_reason_budget (session_id, reason, attempts, updated_at)
            VALUES (?, ?, 0, ?)
            ON CONFLICT(session_id, reason) DO NOTHING
            """,
            (session_id, reason, now),
        )

    @staticmethod
    def _purge_transient_session_state(conn: sqlite3.Connection) -> None:
        running = "session_id IN (SELECT session_id FROM sessions WHERE status = 'running' AND ended_at IS NULL)"
        conn.execute(f"DELETE FROM session_counter_allocations WHERE NOT ({running})")
        conn.execute(f"DELETE FROM executive_stop_signatures WHERE NOT ({running})")

    def _list_graveyard_rows(self, limit: int) -> list[sqlite3.Row]:
        with self.connection() as conn:
            return conn.execute(
                """
                SELECT id, session_id, summary, reason, files_json, keywords_json, created_at
                FROM graveyard
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    @staticmethod
    def _graveyard_row_to_item(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "session_id": row["session_id"],
            "summary": row["summary"],
            "reason": row["reason"],
            "files": json.loads(row["files_json"]),
            "keywords": json.loads(row["keywords_json"]),
            "created_at": row["created_at"],
        }

    @staticmethod
    def _compact_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
        compacted = dict(payload)
        meta: dict[str, dict[str, Any]] = {}
        for field in _COMPACT_TEXT_FIELDS:
            value = compacted.get(field)
            if not isinstance(value, str) or len(value) <= _COMPACT_TEXT_MAX_LEN:
                continue
            meta[field] = {
                "original_len": len(value),
                "truncated": True,
                "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
            }
            compacted[field] = value[:_COMPACT_TEXT_MAX_LEN]
        if meta:
            compacted["_payload_compaction"] = meta
        return compacted
```
