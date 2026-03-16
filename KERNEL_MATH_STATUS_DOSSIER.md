# Kernel Math Status Dossier

> Frozen v1 reference dossier mirrored from [`cortex-loop-v1-archive`](https://github.com/cortex-loop/cortex-loop-v1-archive/tree/v0.1.0a2) at [`v0.1.0a2`](https://github.com/cortex-loop/cortex-loop-v1-archive/releases/tag/v0.1.0a2).
> This fresh canonical repo intentionally contains only these five v1 reference documents; the full v1 tree, tests, fixtures, and releases live in the archive repo.


This dossier is the current math-status and critique packet for the live Cortex kernel.
It is a critique-support packet, not active authority.

It is the final v1 theorem/status packet for the frozen truthful-withheld endpoint.

Active authority remains [../KERNEL_MATH_NOTE.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/KERNEL_MATH_NOTE.md), [../KERNEL_MATH_IMPLEMENTATION_DECISION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/KERNEL_MATH_IMPLEMENTATION_DECISION.md), [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), and [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md).
Use this packet with [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md) and [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md) when you want the current whole-system critique set.
The broader cross-runtime interaction diagnosis that now sharpens the boundedness allocation lives in [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md).

## Quick Navigation

- Need the shortest current read: see Sections 0, 2, 4, 6, and 8.
- Need the live math-to-code map: see Section 2.
- Need the strongest test and runtime proof summary: see Section 5.
- Need the current root-cause allocation for boundedness: see Section 6.

## 0. Evidence Window

This packet was refreshed against the current repo tree on `2026-03-16`.
It is anchored to the current code in [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md), the current adapter/runtime proof in [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md), the current boundedness RCA in [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md), and the broader cross-runtime audit in [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md).

Important freshness note:

- the older phase-C math reconstruction that talked in terms of an explicit `StopPathKernelBoundary(state, transition, action, claims)` carrier is no longer the live code shape
- the current embodied kernel is flatter: a compact verdict law, a flat `StopPathOutcome`, and persisted session metadata carrying the rest of the state needed for failed-stop memory
- this dossier intentionally describes the current implementation rather than preserving closed-program wording

## 1. Governing Mathematical Question

The current mathematical question is no longer “can we invent a richer formalism?”
It is:

- what is the smallest mathematically honest description of the kernel that the current code actually implements
- which parts of that description are well supported by tests and runtime evidence
- which remaining product failures are kernel-law failures rather than adapter or executive failures

Current product mission in math terms:

- Cortex must decide whether a completion claim is acceptable with machine-readable, evidence-bearing, runtime-preserving truth
- humane support and adapters must remain downstream of that same truth
- no amount of prettier proof formatting counts as success if the system still produces a worse patch than the raw model on the same task

## 2. Current Live Math-To-Code Reconstruction

The current kernel is best read as a distributed bounded state/control system, not a single elegant object.

| Mathematical role | Current embodiment | Main code surfaces | Honest status |
| --- | --- | --- | --- |
| Evidence `E_t` | stop payload, trailer fallback provenance, witness commands/tools, git baseline/current snapshot, invariant subprocess output, session metadata | [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py), [../../cortex/invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/invariants.py), [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py) | explicit and live |
| Hard gate facts `H_t` | inputs to `compute_stop_outcome(...)`: challenge status, invariant status, requirement-audit gap state, structured-stop violation, stuck declaration, strict-mode gates | [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit and strong |
| Deficit state `D_t` | `objective_gap_signature: dict[str, list[str]]` over contract, challenges, requirements, truth claims, invariants | [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit but still string-coded |
| Stop signature `S_t` | `stop_attempt_signature` with challenge shape, witnessed commands, and file signal | [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit and live |
| Memory `M_t` | persisted session metadata: prior stop signature, prior objective-gap signature, unchanged-attempt counter, git baseline, startup requirement ids | [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit but distributed |
| Verdict law `B_t` | `StopVerdict` | [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py) | explicit and compact |
| Transition / residue `R_t` | `objective_gap_state`, `objective_gap_reason`, `objective_gap_unchanged_attempts`, `loop_detected`, `loop_similarity` | [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit and useful |
| Action / control `A_t` | `stop_stage`, `recommend_revert`, `feedback_mode`, `terminate_session`, `repair_targets` | [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py), [../../cortex/stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_runtime.py) | explicit and bounded |
| Outward projection `O_t` | runtime-facing response payloads, session-close metadata, adapter stop projections | [../../cortex/core.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/core.py), [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md) | explicit and runtime-preserving on current evidence |

The most important current correction to older kernel-math wording is this:

- the live code no longer has the older typed deficit-entry layer or the decomposed `kernel/state/transition/action/claims` carrier that some earlier critique packets described
- current math must be honest about the flatter, string-coded, distributed state that actually shipped

## 3. What Is Mathematically Explicit And Earned

### 3.1 Structured-stop law

The kernel now has an explicit machine-readable stop contract.
That law is embodied in [../../cortex/stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_payload.py) and [../../cortex/stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_contract.py).
It distinguishes:

- native structured stop evidence
- `payload.stop_fields`
- trailer fallback
- strict-mode rejection of fallback-only completion claims

This is not just prose. It is directly test-backed by [../../tests/test_stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_payload.py) and [../../tests/test_stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_contract.py).

### 3.2 Verdict law

The verdict law is compact and explicit in [../../cortex/stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_policy.py).
It decides among:

- `completed`
- `failed_invariants`
- `failed_stop_contract`
- `failed_requirements`
- `failed_challenges`
- `missing_challenge_coverage`
- `stuck`

with bounded control outputs `repair`, `reorient`, `halt`, or `None`.
This is the clearest mathematically clean part of the current kernel.

### 3.3 Failed-stop relation state

The kernel now has a real relation taxonomy over repeated failed stops.
It can distinguish:

- `identical`
- `reduced`
- `expanded`
- `substituted`
- first-observed / stagnant / misaligned control states derived from those relations

This is materially better than the earlier “changed vs unchanged” story and is directly encoded in [../../cortex/stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/stop_signals.py).

### 3.4 Runtime preservation

The kernel’s stop meaning is now preserved across the shipped runtime set as documented in [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) and [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md).
Current bounded theorem-like support is strongest for:

- Claude native on truthful stop and structured failure semantics
- Gemini native on truthful stop plus stronger humane support
- OpenAI assisted on bounded humane-support realization

Native OpenAI remains outside the strongest preservation story because semantic strict close is still not solved.

## 4. What Is Not Yet Final Or Fully Proved

### 4.1 Boundedness is not in the stop law

This is the main current mathematical defect.
The kernel has no explicit acceptance term for “truthful but over-broad relative to the smallest user task.”
The newer cross-runtime audit sharpens the ordering around that defect: before adding new kernel law, the product first needs a validation-lane split because the current shared positive lane is already a proof-hardening benchmark rather than a clean minimal-fix benchmark.

### 4.2 The current deficit carrier is still coarse

`objective_gap_signature` is explicit, but it is still a normalized string map rather than a typed deficit algebra.
That is mathematically acceptable for the current system description, but it is not final-minimal or maximally expressive.

### 4.3 The product claim is still unearned

The current repo evidence does not yet prove that Cortex as a product beats the raw model on actual artifact quality.
It proves stronger completion evidence and stronger truthful-stop discipline.
That is useful, but it is not the same thing.

### 4.4 The executive layer is not the fix for this defect

The upcoming executive layer can improve approach control, task legibility, and humane support.
It does not own completion truth.
So the current boundedness failure is not something to defer to the executive layer.
If the kernel or validation contract rewards proof completion more strongly than minimal-task boundedness, a stronger executive would only optimize the wrong objective harder.

## 5. Test And Runtime Proof Summary

Code-backed mathematical evidence:

- [../../tests/test_stop_policy.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_policy.py): verdict law and bounded action stages
- [../../tests/test_stop_signals.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_signals.py): objective-gap signatures, relation taxonomy, and loop similarity
- [../../tests/test_stop_runtime.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_runtime.py): end-to-end stop path, persistence, and repair-target generation
- [../../tests/test_stop_contract.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_contract.py) and [../../tests/test_stop_payload.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_stop_payload.py): structured-stop law
- [../../tests/test_requirements.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_requirements.py) and [../../tests/test_invariants.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_invariants.py): per-surface evidence gates

Runtime-backed preservation evidence:

- [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) plus the fixture trees under [../../tests/fixtures/adapter_validation/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation) show the kernel carried through live Claude, Gemini, and OpenAI host surfaces
- [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md) plus [../../tests/fixtures/postmortem/claude_boundedness_postmortem.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/postmortem/claude_boundedness_postmortem.json) show the current mixed boundedness story directly rather than by inference
- [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md) plus [../../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json) now show that the same overloaded positive lane destabilizes multiple runtimes differently, so the first shared issue is validation-contract design rather than a new adapter seam

## 6. Root-Cause Allocation For The Current Product Failure

Current repo truth now supports this allocation:

- historical primary cause: Claude adapter startup pressure
- current primary cause: validation-contract design first, with kernel / validation-contract failure to preserve minimal-task boundedness under proof pressure as the surviving product defect
- secondary amplifier: the strict proof contract can still make broadening look like the easiest path to valid completion
- rejected as primary cause on current evidence: a missing Claude-native bounded-correction layer

That is why the next honest product fix is below the adapter and below the upcoming executive layer.

## 7. What Another Researcher Should Critique First

1. Is the next honest kernel change a boundedness-aware stop or acceptance term, or would that create a second soft control doctrine instead of a cleaner hard law?
2. Can boundedness be derived from existing canonical state, or would it require new kernel-owned evidence?
3. Is the current flat `StopPathOutcome` the right embodiment, or is there now a smaller honest split?
4. Are any current runtime-preservation claims stronger in the dossiers than in the actual fixture ledger?
5. What A/B evidence would be sufficient to claim that Cortex beats the raw model on actual task output rather than only on proof quality?

## 8. Current Sweep Verdict

After auditing current code, tests, runtime validation, and the boundedness RCA:

- the current kernel-math story is no longer the old explicit carrier story; it is a flatter, distributed state/control story
- the kernel has earned strong local support for structured-stop enforcement, verdict law, and repeated-failure relation tracking
- the main remaining product defect is not “missing more math” and not “missing more hooks”; it is the absence of minimal-task boundedness as an explicit acceptance concern
- the broader cross-runtime audit adds one more correction: before introducing new kernel law for boundedness, Cortex should first separate a true minimal-fix lane from the current proof-hardening lane
- the upcoming executive layer should not be treated as the fix for that defect
- Cortex still does not have repo-backed proof that it outperforms the raw model on artifact quality
