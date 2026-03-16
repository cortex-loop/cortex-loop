# Validation Evidence Dossier

> Frozen v1 reference dossier mirrored from [`cortex-loop-v1-archive`](https://github.com/cortex-loop/cortex-loop-v1-archive/tree/v0.1.0a2) at [`v0.1.0a2`](https://github.com/cortex-loop/cortex-loop-v1-archive/releases/tag/v0.1.0a2).
> This fresh canonical repo intentionally contains only these five v1 reference documents; the full v1 tree, tests, fixtures, and releases live in the archive repo.


This dossier is the canonical validation, fixture, and proof-evidence packet for the frozen v1 Cortex archive point.
It is a critique-support packet, not active authority.

Use this after [CORTEX_STATE_ANALYSIS.md](CORTEX_STATE_ANALYSIS.md) when you need to answer a narrower question:
which exact artifacts, tests, and release surfaces back the final v1 runtime and product-proof claims?

## 0. Final V1 Scope

This packet freezes the evidence boundary for the final v1 archive point:

- package version target: `0.1.0a2`
- release tag target: `v0.1.0a2`
- package line role: final archival v1 enforcement-layer release
- product-proof endpoint: truthful-withheld

Current repo truth preserved by that endpoint:

- Phase 8 remains `blocked`
- Phase 9 is `landed`
- Phase 10 remains `blocked`
- the product claim remains `withheld_not_yet_earned`

## 1. Evidence Window

This dossier distinguishes four evidence families instead of flattening them into one story:

1. committed shared-harness readiness rows under [../../tests/fixtures/adapter_validation/](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation)
2. dated contradiction and critique packets from the March 15, 2026 audit window
3. final current-v1 product-proof artifacts from the March 16, 2026 truthful-withheld endpoint
4. package and release-control evidence for the archival v1 package line

The point is not to make the evidence look cleaner than it is.
The point is to preserve exactly which claims are current, which are historical, and which are mixed.

## 2. Canonical Artifact Families

### 2.1 Shared-harness readiness and provenance

These are the committed validation trees that back the shipped readiness ledger in [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md):

- Claude:
  - [../../tests/fixtures/adapter_validation/claude/PROVENANCE.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/claude/PROVENANCE.json)
  - [../../tests/fixtures/adapter_validation/claude/pass_minimal.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/claude/pass_minimal.json)
  - [../../tests/fixtures/adapter_validation/claude/truth_gap.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/claude/truth_gap.json)
- Gemini:
  - [../../tests/fixtures/adapter_validation/gemini/PROVENANCE.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/gemini/PROVENANCE.json)
  - [../../tests/fixtures/adapter_validation/gemini/pass_minimal.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/gemini/pass_minimal.json)
  - [../../tests/fixtures/adapter_validation/gemini/truth_gap.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/gemini/truth_gap.json)
- OpenAI:
  - [../../tests/fixtures/adapter_validation/openai/PROVENANCE.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/openai/PROVENANCE.json)
  - [../../tests/fixtures/adapter_validation/openai/pass_minimal.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/openai/pass_minimal.json)
  - [../../tests/fixtures/adapter_validation/openai/truth_gap.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/openai/truth_gap.json)
  - [../../tests/fixtures/adapter_validation/openai/assisted_preview.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/adapter_validation/openai/assisted_preview.json)

These rows remain the canonical readiness ledger.
They do not get silently overwritten by later contradiction packets or product-proof packets.

### 2.2 Dated contradiction packets

These preserve evidence windows where newer local behavior contradicted or complicated the older committed readiness rows:

- [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md)
- [../../tests/fixtures/audits/model_kernel_adapter_audit.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/model_kernel_adapter_audit.json)
- [../CLAUDE_BOUNDEDNESS_POSTMORTEM.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CLAUDE_BOUNDEDNESS_POSTMORTEM.md)
- [../../tests/fixtures/postmortem/claude_boundedness_postmortem.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/postmortem/claude_boundedness_postmortem.json)
- [../../tests/fixtures/audits/cortex_state_analysis.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/cortex_state_analysis.json)

These artifacts matter because they preserve contradiction rather than laundering it.
They are not the active authority surfaces for runtime status or release truth.

### 2.3 Final current-v1 product-proof surfaces

These are the final current-v1 proof artifacts:

- Phase 1 blocker:
  - [../../tests/fixtures/audits/net_positive_phase1_baseline_blocker.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase1_baseline_blocker.json)
- March 16 current packet and readiness:
  - [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json)
  - [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json)
- March 16 current pair artifacts:
  - [../../tests/fixtures/audits/net_positive_phase9_claude_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_claude_current_pair.json)
  - [../../tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json)
  - [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json)

These are the artifacts that justify the final v1 product-proof verdict:

- Phase 9 is `landed`
- the product claim remains `withheld_not_yet_earned`
- Claude is the strongest current truthful-stop lane
- Gemini is route-valid on the current easy-task lane but still mixed on strict close
- OpenAI assisted has one current row-capturable shared-harness pair, but remains supplemental-only
- native OpenAI remains blocked/non-row-capturable for current product-proof weight

### 2.4 Release and package evidence

These surfaces back the final archival v1 package and release-control story:

- [../../pyproject.toml](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/pyproject.toml)
- [../../cortex/__init__.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/cortex/__init__.py)
- [../../CHANGELOG.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/CHANGELOG.md)
- [../INSTALL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/INSTALL.md)
- [../../.github/workflows/publish.yml](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/.github/workflows/publish.yml)
- [../../scripts/extract_release_notes.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/scripts/extract_release_notes.py)
- [../../tests/test_release_notes.py](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/test_release_notes.py)

Those files define and verify the package version, changelog extraction path, and the GitHub tag-to-PyPI release flow for the frozen v1 line.

### 2.5 Structured stop / JSON-shape findings worth carrying into v2

The most reusable structured-output result from frozen v1 is narrower than “every host needs a different JSON schema.”

The kernel’s accepted machine-readable stop carriers at the frozen tag are:

- native structured stop evidence
- `payload.stop_fields`
- `STOP_FIELDS_JSON:` trailer fallback

But the frozen strict-path evidence also says not to overread that fallback:

- strict mode does not treat message-fallback or trailer-only stop text as equivalent to stable native or payload-carried stop fields
- the repo’s strongest current cross-runtime machine-readable carrier is therefore `payload.stop_fields`, not free-form prose and not per-model custom schemas

Current row-capturable March 16 evidence comes out like this:

| Runtime lane | Current machine-readable carrier | Current observed result | Reusable v1 lesson |
| --- | --- | --- | --- |
| Claude native | `payload.stop_fields` in the current Cortex pair | structured stop observed; route-valid `localized_edit/light`; final stop `completed` | the shared carrier works on the strongest current native lane, but the lane still did not realize the shared `strict` intent |
| Gemini native | `payload.stop_fields` in the current Cortex pair | structured stop observed; route-valid `localized_edit/strict`; final stop `failed_invariants` | the same carrier works, but stricter close quality still depends on host/runtime behavior rather than needing a new JSON shape |
| OpenAI assisted | `payload.stop_fields` from the assisted bridge | structured stop observed; bounded corrective pass occurred; final stop `failed_challenges` / `bounded_incomplete` | the shared carrier also works through the assisted bridge, but the lane stays supplemental because closure quality and product-proof weight remain mixed |
| OpenAI native | no current row-capturable terminal stop surface | blocked for current product-proof weight | the repo still cannot isolate shape interaction cleanly on native OpenAI because terminality is the blocker, not an already-proven schema mismatch |

The broad v1 result is therefore:

- one common machine-readable carrier did work across the row-capturable lanes
- the main runtime differences showed up in closure quality, assurance realization, and terminality
- the repo did not earn a claim that better per-model JSON shape tuning was the main remaining lever

Primary backing surfaces:

- [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md)
- [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)
- [../../tests/fixtures/audits/net_positive_phase9_claude_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_claude_current_pair.json)
- [../../tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json)
- [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json)
- [../../tests/fixtures/audits/net_positive_phase1_baseline_blocker.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase1_baseline_blocker.json)

## 3. Runtime Claim To Evidence Map

| Runtime claim | Final v1 status | Primary backing artifacts | Why this is the right evidence class |
| --- | --- | --- | --- |
| Claude native is the strongest current truthful-stop lane | `current and strong` | [../../tests/fixtures/audits/net_positive_phase9_claude_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_claude_current_pair.json), [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md), [../CORTEX_REALIZATION_MODEL.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/CORTEX_REALIZATION_MODEL.md) | Current packet evidence plus active authority agree. |
| Gemini native remains shipped with watchlist but mixed on latest strict close | `current but mixed` | [../../tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_gemini_current_pair.json), [../MODEL_KERNEL_ADAPTER_AUDIT.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MODEL_KERNEL_ADAPTER_AUDIT.md), [../ADAPTER_VALIDATION.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTER_VALIDATION.md) | Requires both the older committed row and the later mixed packet. |
| OpenAI assisted is product-real but supplemental-only | `current but non-substitutive` | [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../ADAPTERS.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/ADAPTERS.md) | Current pair exists, but packet and authority explicitly keep it supplemental. |
| OpenAI native is blocked/non-row-capturable for current product-proof weight | `blocked` | [../../tests/fixtures/audits/net_positive_phase1_baseline_blocker.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase1_baseline_blocker.json), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json) | This is a blocker truth, not a missing test. |

## 4. Product-Proof Boundary Map

| Claim | Final v1 verdict | Backing surfaces |
| --- | --- | --- |
| Phase 9 is landed | `yes` | [../MASTER_PLAN.md](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/docs/MASTER_PLAN.md), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json) |
| The product claim is earned | `no` | [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json) |
| The truthful-withheld endpoint is explicit rather than implied | `yes` | [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json), [../../tests/fixtures/audits/net_positive_phase9_rerun_readiness.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_rerun_readiness.json) |
| Assisted OpenAI can substitute for native OpenAI proof | `no` | [../../tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_openai_assisted_current_pair.json), [../../tests/fixtures/audits/net_positive_phase9_current_packet.json](https://github.com/cortex-loop/cortex-loop-v1-archive/blob/v0.1.0a2/tests/fixtures/audits/net_positive_phase9_current_packet.json) |

## 5. Fresh-Agent Reading Order

If a new agent needs the fastest faithful reconstruction of final v1:

1. [CORTEX_STATE_ANALYSIS.md](CORTEX_STATE_ANALYSIS.md)
2. [KERNEL_IMPLEMENTATION_DOSSIER.md](KERNEL_IMPLEMENTATION_DOSSIER.md)
3. [ADAPTER_IMPLEMENTATION_DOSSIER.md](ADAPTER_IMPLEMENTATION_DOSSIER.md)
4. [KERNEL_MATH_STATUS_DOSSIER.md](KERNEL_MATH_STATUS_DOSSIER.md)
5. this dossier

Use the current packet and current pair artifacts before reopening older contradiction packets.
Use the contradiction packets before making any claim that the final v1 story is cleaner than it really is.

## 6. Final V1 Evidence Verdict

The final v1 evidence surface is good enough to support three things and not more:

- Cortex is strong on truthful completion-boundary enforcement.
- The runtime/adaptor ecosystem is materially implemented and evidenced across Claude, Gemini, OpenAI native, and OpenAI assisted.
- The repo can now truthfully stop at a landed-withheld product-proof endpoint instead of implying one more local seam will earn net positivity.

It is not good enough to support:

- a broad claim that Cortex beats the raw model on artifact quality
- a native OpenAI parity claim
- a retroactive cleanup of the contradictory March 15 evidence window
