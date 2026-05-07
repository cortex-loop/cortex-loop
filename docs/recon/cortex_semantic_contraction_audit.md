# Cortex Semantic Contraction Audit

Surface: internal / recon audit

Date: 2026-05-07

Verdict: `contraction_candidates_identified`; no runtime contraction implemented.

## Summary

This audit is the first subtraction-oriented seam after semantic contraction
became a serious tracker discipline. It does not delete code, refactor runtime
paths, alter packet law, change `next_product_train`, run live tests, or claim
product behavior progress.

Semantic contraction is not minification. The target is duplicate policy,
stale proof scaffolding, inactive lab/recon/doc surfaces, and host/runtime
copy-paste that can be collapsed into one owner after behavior-preservation
proof or explicit retirement evidence.

## Size Baseline

Measured on the current branch before any contraction implementation:

| Surface | Python files | LOC |
| --- | ---: | ---: |
| `cortex/core` | 13 | 2,417 |
| `cortex/sre` | 27 | 10,241 |
| `cortex/aux` | 13 | 5,918 |
| `cortex/runtime` | 3 | 697 |
| `cortex/hosts` | 43 | 21,610 |

Highest-pressure files and clusters:

| Cluster | Evidence |
| --- | --- |
| Host runtimes | `openai/runtime.py` 2,814 LOC; `reference/runtime.py` 2,478 LOC; `gemini/runtime.py` 2,071 LOC; `claude/runtime.py` 2,071 LOC. |
| Host session I/O | `openai/session_io.py` 791 LOC; `reference/session_io.py` 781 LOC; `gemini/session_io.py` 769 LOC; `claude/session_io.py` 769 LOC. |
| Host drivers | `*_host_commitment.py` totals 858 LOC; `*_host_neutral.py` totals 396 LOC. Pairwise driver diffs are about 30 to 33 lines per host pair. |
| Codex App/CLI coordinator | `cortex/hosts/openai/codex_app_cli_hook_coordinator.py` is 1,228 LOC and is the current pressure point for actuator growth. |
| Large SRE/AUX modules | `expectations.py` 1,086 LOC; `interventions.py` 966 LOC; `operator_routing.py` 948 LOC; `support_priors.py` 963 LOC; `cross_host_shadow.py` 1,029 LOC; `reference_builder.py` 1,069 LOC. |
| Lab/recon surfaces | `lab/**` is 25,465 Python LOC; `docs/recon` currently has 35 recon docs before this audit. |

## Target Family Coverage

This audit covers the five requested contraction families:

- host runtime parallelism across
  `cortex/hosts/{openai,reference,claude,gemini}/runtime.py`;
- per-host driver/session I/O duplication;
- `codex_app_cli_hook_coordinator.py` growth and actuator-boundary pressure;
- large SRE/AUX modules that may contain duplicate policy paths;
- inactive lab/recon/doc active-surface retirement candidates that should be
  archived, role-demoted, or explicitly retained.

## Candidate Matrix

The action vocabulary is `delete`, `collapse`, `extract`, `archive`, and
`defer`. This audit identifies no immediate `delete` row; deletion remains a
future-seam result only after behavior-preservation proof or explicit
retirement.

| Candidate | Current owner(s) | Future owner | Shape | Proof before removal | Action | Risk / payoff |
| --- | --- | --- | --- | --- | --- | --- |
| Host runtime helper extraction | `cortex/hosts/{openai,reference,gemini,claude}/runtime.py` | `cortex/runtime/lifecycle_kernel.py` plus thin host adapters | Extract shared continuity, environment, support-snapshot, warning, family-admission, and realization helpers. Claude/Gemini share 36 of 38 runtime function names; reference/Gemini share 36 of 38; OpenAI/Gemini share 34 common runtime function names plus OpenAI-specific shipping paths. | Byte-equivalence or output-equivalence fixtures for helpers; conformance tests; migrate reference first, then non-default hosts, then OpenAI. | `extract` | High payoff, high risk. |
| Host driver/session I/O collapse | `cortex/drivers/*_host_commitment.py`, `cortex/drivers/*_host_neutral.py`, host `session_io.py` files | Shared driver/session helpers with host-specific declarations | Collapse triplicated commitment/neutral drivers and repeated session serialization shapes while keeping host-native terminology explicit. | Existing product/conformance/session I/O tests; fixture round-trips per host; no status or shipping-truth change. | `collapse` | Medium payoff, medium risk. |
| Codex App/CLI actuator boundary extraction | `cortex/hosts/openai/codex_app_cli_hook_coordinator.py` | Coordinator plus per-event actuator modules under the OpenAI host adapter | Keep the coordinator thin: normalize payload, update state, dispatch to event-specific actuator, render host response. Do not fold this into the generic host runtime. | Current coordinator/client product tests; lab Gate 0 tests for Stop and future PostToolUse/PreToolUse paths; no model-visible text change. | `extract` | Medium payoff, medium risk. |
| SRE/AUX duplicate-policy audit | Large SRE/AUX modules named above | Existing SRE/AUX owner modules, with duplicate policy removed only where one law already exists | Identify repeated pressure assembly, support-prior, reference-scoring, or cross-host shadow rules. Do not merge SRE and AUX; preserve AUX removability and non-sovereignty. | Focused product/experimental/conformance tests per module; packet-law citation for any owner move. | `defer` | Medium payoff, high risk until specific duplicates are named. |
| Lab/recon/doc retirement pass | `lab/**`, `docs/recon/**`, retained docs under `doc_roles` | `doc_roles`, future recon index, archive taxonomy | Archive or role-demote inactive proof paths only when status/recon says they are superseded or preserved. Keep narrative evidence unless a structured index proves it is safely archived. | `active_docs`/`doc_roles` tests, docs boundary tests, generated status/Cortex doc checks, and explicit status/recon retirement note. | `archive` | Medium payoff, low-to-medium risk after recon indexing. |

## Recommended Next Contraction Seams

1. `host-runtime-kernel-extraction-audit`: produce a helper-by-helper
   equivalence report and migration order before extracting any runtime code.
2. `coordinator-actuator-boundary-extraction`: split the Codex App/CLI
   coordinator by event actuator after current task-standard stack questions
   settle, with no behavior change.
3. `driver-session-io-common-kernel-audit`: compare host commitment,
   neutral, and session I/O paths and identify the smallest shared helper
   layer.
4. `recon-archive-retirement-pass`: after structured recon indexing, archive
   or role-demote inactive proof surfaces with explicit generated-doc updates.

## Claims Not Earned

- No product behavior changed.
- No runtime contraction, deletion, refactor, host-kernel migration, or
  coordinator extraction was implemented.
- No packet law, SRE law, AUX law, model-visible text, hook wiring, fixture,
  scoring, status `next_product_train`, or live evidence changed.
- No behavior lift, output-quality lift, Codex App parity, shipping promotion,
  or proof that any candidate is safe to delete was earned.

## Decision

Semantic contraction is now evidence-backed enough to remain a serious
planning discipline. The first implementation should still be an extraction
audit, not deletion. Code removal must wait for behavior-preservation proof or
explicit retirement evidence.
