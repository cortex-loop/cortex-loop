# Cortex State Analysis

> Frozen v1 reference dossier mirrored from [`cortex-loop-v1-archive`](https://github.com/cortex-loop/cortex-loop-v1-archive/tree/v0.1.0a2) at [`v0.1.0a2`](https://github.com/cortex-loop/cortex-loop-v1-archive/releases/tag/v0.1.0a2).
> This fresh canonical repo intentionally contains only these five v1 reference documents; the full v1 tree, tests, fixtures, and releases live in the archive repo.


This dossier is the concise whole-system state snapshot for Cortex.
It is a critique-support packet, not an authority surface. Active status and release truth still live in [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), and [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md).

This is the final v1 state snapshot for the truthful-withheld endpoint.
Use this first when a new human or agent needs the shortest faithful read of frozen v1.

This document is intentionally synthesis-first:

- it summarizes current product state rather than restating full implementation details
- it points back to the other four canonical dossiers for code-depth and evidence review
- it keeps every nontrivial claim either directly backed, explicitly inferred, or explicitly mixed

The machine-readable companion artifact is [../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json).

## 0. Evidence Window

Current state summarized here is grounded in:

- current active authority docs through `2026-03-16`
- current code on the checked-out repo state
- current Phase 9 proof artifacts in:
  - [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json)
  - [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json)
- committed cross-runtime audit evidence in [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md) and [../../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json)
- committed Claude boundedness RCA in [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md) and [../../tests/fixtures/postmortem/claude_boundedness_postmortem.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/postmortem/claude_boundedness_postmortem.json)
- committed implementation snapshots in:
  - [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md)
  - [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md)
  - [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)
  - [VALIDATION_EVIDENCE_DOSSIER.md](VALIDATION_EVIDENCE_DOSSIER.md)

This dossier also includes one fresh committed supplemental live comparison between current Cortex and the older published PyPI `0.1.0a1` release. The final archival v1 package target is `0.1.0a2`; the older release comparison remains historical support evidence and is not treated as a release authority surface.

## 1. Executive Verdict

Cortex is currently strong at truthful completion-boundary enforcement, strongest on Claude native, and materially implemented across Claude, Gemini, OpenAI native, and OpenAI assisted. That is real and repo-backed.

Cortex is strong on truthful completion-boundary enforcement and strongest on Claude native, but still lacks repo-backed proof that it improves artifact quality over the raw model. The strongest current repo-backed diagnosis is that the main remaining product defect is below the current Claude adapter and above the future executive layer: the shared validation contract and kernel acceptance shape still overweight proof completion relative to minimal-task boundedness on some tasks ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md), [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py#L16-L127)).

The repo has now landed Phase 9 at a truthful-withheld endpoint. Current shared-harness evidence includes current Claude native, Gemini native, and OpenAI-assisted pairs; native OpenAI remains blocked/non-row-capturable; and the product claim remains `withheld_not_yet_earned` rather than silently deferred ([../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json), [../MASTER_PLAN.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MASTER_PLAN.md)).

The fresh committed current-vs-PyPI comparison does not support a broad regression claim from the latest kernel-math era. It does show one likely regression signal on Gemini boundedness, continued mixed OpenAI behavior, and clear Claude improvement on the minimal positive lane. That comparison is supplemental evidence, not a proof that the current product is broadly better than raw or broadly better than `0.1.0a1`.

One especially reusable v1 lesson for a fresh v2 agent is that the final evidence does not point to “every host needs a different JSON stop schema.” The strongest row-capturable March 16 packet shows one shared machine-readable carrier, `payload.stop_fields`, working across Claude native, Gemini native, and OpenAI assisted; the runtime differences show up later in assurance, closure quality, and terminality rather than in the base carrier shape itself ([VALIDATION_EVIDENCE_DOSSIER.md](VALIDATION_EVIDENCE_DOSSIER.md), [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md)).

## 2. Current System State

### Kernel state

- The kernel owns completion meaning, challenge evaluation, requirement audit, truth-claim evaluation, objective-gap tracking, and final acceptance ([KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py#L250-L399)).
- The current embodied stop law is still proof-centered. `compute_stop_outcome(...)` has no explicit boundedness or scope-overreach term; it only reasons over invariants, structured stop validity, requirement audit, and challenge coverage ([../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py#L16-L127)).
- The kernel therefore distinguishes truthful proof from false proof more clearly than it preserves minimal patch boundedness under proof pressure. That is the strongest current kernel-side limitation ([../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md), [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)).

### Adapter and runtime state

- Claude native is the strongest truthful stop lane and the cleanest current shipped adapter surface ([ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md), [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md)).
- Gemini native remains shipped but current strict-close evidence is still mixed against the older committed pass row: the current route-valid `localized_edit/strict` pair still ended `failed_invariants` ([../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../../tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json)).
- OpenAI native remains blocked/non-row-capturable for current product-proof weight, so the repo still cannot use native OpenAI as a clean current packet lane ([../../tests/fixtures/audits/net_positive_phase1_baseline_blocker.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase1_baseline_blocker.json), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json)).
- OpenAI assisted is a real additional realization path, not just a thought experiment, and it now has one current row-capturable shared-harness pair. That lane is still experimental and supplemental-only rather than a launch-proof positive lane ([ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md), [../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py#L629-L756), [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json)).

### Validation-contract state

- The current shared positive lane is already a proof-hardening lane, not a clean minimal-fix product lane. That is the strongest broad cross-runtime pattern in the repo-backed evidence ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json)).
- That diagnosis remains historically important, but it is no longer the repo’s active next seam. The repo-local campaign has already landed Phase 9 at a truthful-withheld endpoint, so further movement is contingent on a new evidence window or external/runtime change rather than another local campaign slice ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../MASTER_PLAN.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MASTER_PLAN.md)).

### Executive-layer relevance boundary

- The upcoming executive layer is not the fix for the current boundedness defect.
- The current repo-backed diagnosis is that if the kernel or validation contract rewards proof completion more strongly than minimal-task boundedness, a stronger executive would optimize the wrong target more effectively rather than correcting the target itself ([KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)).

## 3. What Is Currently Working

- Truthful completion-boundary enforcement is real and well-backed in the kernel and runtime docs, especially on Claude native ([KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md)).
- The stop path is explicit, auditable, and machine-readable across the core product surfaces ([../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py#L402-L518)).
- Claude native now realizes startup preview, failure-side tool handling, truthful stop, and telemetry-only `InstructionsLoaded` without needing a broader runtime doctrine shift ([ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md), [../../cortex/hooks/_shared.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/hooks/_shared.py#L81-L170)).
- OpenAI assisted exists as a bounded, explicit runtime mode with one corrective pass in code; that is now backed by a current row-capturable shared-harness pair, even though the current close still ended bounded incomplete and remains supplemental-only ([../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py#L527-L756), [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md), [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json)).

## 4. Main Current Defects

### Kernel-Wide Anti-Patterns

1. No first-class boundedness term in the stop law.
   Evidence: `compute_stop_outcome(...)` does not encode scope overreach or minimal-task boundedness as an acceptance concern ([../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py#L16-L127)).

2. Startup and stop semantics are better at teaching proof closure than bounded minimal completion.
   Evidence: the session-start completion preview pushes global challenge and requirement completion surfaces even on native preview lanes ([../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py#L469-L565)).

3. Objective-gap tracking models proof-gap dynamics, not task-scope drift.
   Evidence: the objective-gap signature is built from contract, challenge, requirement, truth-claim, and invariant state only ([../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py#L269-L345)).

4. Repair targets are proof-repair instructions, not boundedness-preserving instructions.
   Evidence: repair targets tell the model how to fix stop fields, challenge coverage, requirement audit, truth claims, and invariants, but not how to prefer truthful bounded non-completion over scope broadening ([../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py#L528-L699)).

### Adapter-Specific Anti-Patterns

1. Gemini still amplifies proof pressure into retries and broader edits.
   Evidence: `AfterAgent` retry logic is wide, and `SessionStart` still carries completion preview plus context blocks ([../../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py#L91-L121), [../../cortex_ops_cli/gemini_hooks.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/gemini_hooks.py#L147-L169), [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md)).

2. OpenAI native remains too brittle to cleanly separate host issues from kernel issues.
   Evidence: native mode is still a one-turn post-hoc bridge without an in-run correction path, and current evidence remains mixed on whether positive lanes reach a clean terminal stop ([../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py#L591-L625), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md)).

3. OpenAI assisted is real but still prompt-heavy.
   Evidence: the assisted layer composes startup and correction prompts with significant bridge-authored explanatory content; that is acceptable as a bounded experimental realization, but it is not a clean shared runtime law ([../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py#L400-L431), [../../cortex_ops_cli/openai_app_server_bridge.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex_ops_cli/openai_app_server_bridge.py#L527-L564)).

4. Claude is no longer the main adapter bottleneck.
   Evidence: the current surviving Claude boundedness issue is below the adapter on the current evidence base ([../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md), [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md)).

### Cross-Runtime Symptoms

- Claude can still widen scope and close `completed` under explicit proof pressure ([../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md)).
- Gemini latest-local positive behavior is mixed and no longer reproduces the older clean shared-harness pass ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md)).
- OpenAI native and assisted latest-local evidence remains mixed and partly contradictory even on the same nominal CLI version ([../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md)).
- The fresh current-vs-PyPI comparison adds one more honest constraint: it does not support a broad regression story, but it also does not provide repo-backed proof that current Cortex is now broadly better than the release package on end-product quality ([../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json)).

## 5. Proven vs Unproven Claims

### Repo-backed and current

- Cortex is strong on truthful completion-boundary enforcement.
- Claude native is the strongest current truthful stop lane.
- Phase 9 is landed at a truthful-withheld endpoint rather than an earned product-proof win.
- The current-vs-PyPI comparison does not support a broad cross-runtime regression claim from the latest kernel-math era.

### Repo-backed but mixed or stale

- Gemini current latest-local strict-close behavior is mixed against the older committed shared-harness pass row.
- OpenAI native remains blocked/non-row-capturable for current product-proof weight, and OpenAI assisted current behavior remains supplemental-only rather than native-substitutive.
- The current-vs-PyPI comparison suggests a likely Gemini boundedness regression signal, but that is still one supplemental live matrix rather than a full release-readiness ledger.

### Not yet proven

- Cortex beats the raw model on artifact quality as a product.
- The latest kernel-math work improved end-product output quality rather than only internal truthfulness structure.
- The executive layer will solve the current boundedness defect.
- A new kernel boundedness primitive is the first earned fix.

## 6. Evidence and Confidence

| Claim | Status | Backing sources | Confidence note |
| --- | --- | --- | --- |
| Cortex is strong on truthful completion-boundary enforcement | `observed` | [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) | Strong repo-backed implementation and runtime proof |
| Claude native is the strongest current truthful stop lane | `observed` | [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md) | Strong and current |
| Phase 9 is landed at a truthful-withheld endpoint | `observed` | [../MASTER_PLAN.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MASTER_PLAN.md), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json) | Strong repo-backed current authority and packet evidence |
| Kernel stop law still lacks a boundedness term | `observed` | [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py#L16-L127) | Direct code fact |
| Current-vs-PyPI comparison does not support a broad regression claim | `live` | [../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json) | Supplemental single current local matrix only |
| Gemini current likely regressed on boundedness relative to PyPI `0.1.0a1` | `mixed` | [../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json), [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md) | Supported by the fresh release comparison, but not yet a full release ledger |
| OpenAI native current behavior is still too unstable to isolate kernel-math effects cleanly, and assisted evidence remains supplemental-only | `mixed` | [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json) | Real contradiction preserved, not resolved into a cleaner product-proof story |
| Cortex beats the raw model on artifact quality | `unsupported` | no repo-backed proof | This is still the central product proof gap |

## 7. Evidence Comfort Check

- **Directly observed:** the kernel stop law, the repair-target logic, the runtime bridge surfaces, and the current cross-runtime audit verdict are all directly backed by current code or committed artifacts.
- **Mixed:** Gemini latest-local positive behavior, OpenAI latest-local behavior, and the fresh current-vs-PyPI comparison all contain real contradictions or limited-scope evidence and are presented that way here.
- **Still not proven:** current Cortex product superiority over the raw model on artifact quality, and any claim that the upcoming executive layer will fix the present boundedness problem.

## 8. Where To Go Deeper

- [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md)
- [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md)
- [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)
- [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md)
- [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md)
