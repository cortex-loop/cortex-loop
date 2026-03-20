# CORTEX_V2_LOCAL_VERIFICATION

Date: 2026-03-20
Status: active local verification entry points for the landed v2 boundary

## Purpose

This document records the repo-local verification commands for the landed Cortex v2 MVP.
It does not add CI or evidence regeneration.
For routine repo-local verification, use the two entry points below: `make verify` for the canonical bundle and `make test-smoke` for the smaller smoke bundle.

## Canonical bundle

Direct commands:

```sh
python3 -m pytest tests/unit -q
python3 -m pytest tests/integration -q
python3 -m pytest tests/unit/test_import_smoke.py -q
```

Repo-local entry point:

```sh
make verify
```

## Smoke bundle

The smoke bundle is intentionally smaller than full verification.
It is useful for quick local confidence only and must not be treated as full-suite closure.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_core.py \
  tests/unit/test_correspondence_ports.py \
  tests/unit/test_correspondence_sre.py \
  tests/unit/test_correspondence_periphery.py \
  tests/integration/test_reference_host_vertical_gate.py \
  tests/integration/test_reference_lane_latency.py \
  tests/integration/test_reference_lane_packet_example.py \
  tests/integration/test_aux_claim_conservative.py \
  tests/unit/test_import_smoke.py -q
```

Repo-local entry point:

```sh
make test-smoke
```

## Reference-lane packet-example revalidation

This revalidates the committed reference-lane packet example doc against the already-landed live packet path.
It does not emit candidate refreshed evidence and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_lane_packet_example.py
```

Repo-local entry point:

```sh
make revalidate-reference-packet
```

## Reference-lane packet-example candidate refresh

This emits candidate refreshed packet-example evidence from the already-landed live packet path to stdout for manual inspection.
It is useful context for the proof-packet prerequisite gate recorded in `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`, but it does not update gate truth and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m tests.integration._reference_lane_packet_example
```

Repo-local entry point:

```sh
make emit-reference-packet-candidate
```

Exact committed-doc regeneration is still not part of normal verification and remains explicit/manual/out of scope unless separately requested.

## Latency-evidence revalidation

This revalidates the committed latency evidence doc against the already-landed live latency collector.
It checks the committed scope, targets, and measurement metadata rather than demanding exact replay of historical micro-latency values.
It does not produce candidate refreshed evidence and it does not regenerate or overwrite the committed latency doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_lane_latency.py
```

Repo-local entry point:

```sh
make revalidate-latency-evidence
```

## Latency-evidence candidate refresh

This emits candidate refreshed latency evidence from the already-landed live collector to stdout for manual inspection.
It is useful context for the landed latency evidence gate recorded in `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`, but it does not update gate truth and it does not overwrite the committed latency doc.

Direct command:

```sh
python3 -m tests.integration._reference_lane_latency_evidence
```

Repo-local entry point:

```sh
make emit-latency-evidence-candidate
```

Exact committed-doc regeneration is still explicit/manual/out of scope unless separately requested.

## Mediation-evidence package revalidation

This checks the committed mediation evidence scaffold for fair matched-pair accounting, host-split preseed coverage, conservative verdict defaults, and blocker truth.
It is check-only: it does not generate run packets, emit candidate evidence, or authorize mediation implementation.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_evidence_package.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-evidence-package
```

## Mediation reference host-realization admissibility revalidation

This checks that `scenario_host_reference_01` remains intentionally baseline-only until a lawful mediated comparator is actually admissible.
It validates the supporting admissibility note, the host baseline-anchor row, the absence of counted host-realization pairs, and the package blocker truth. It does not generate evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_host_realization_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-host-realization-basis
```

## Mediation run-packet revalidation

This checks the committed reference-host and Gemini-host baseline run indexes and the committed run-packet instances.
It validates packet metadata against the scenario catalog, confirms the canonical baseline anchors remain lawful, validates the full seven-packet reference baseline set, validates the Gemini uncertainty baseline anchor, and checks the six committed experimental mediated uncertainty and thrash packets.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_run_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-run-packets
```

## Live reference mediation-baseline revalidation

This revalidates the seven committed reference-host baseline mediation packets against live reference-host code paths.
It remains reference-first and baseline-only: it does not advance any paired counts and it does not add Gemini or OpenAI live packets.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediation_baseline_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediation-baselines
```

## Live Gemini mediation-baseline revalidation

This revalidates the committed Gemini-host uncertainty baseline anchor against the landed Gemini commitment-path slice.
It remains Gemini-only and baseline-only: it does not advance any paired counts and it does not add Gemini mediated packets.

Direct command:

```sh
python3 -m pytest tests/integration/test_gemini_mediation_baseline_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-mediation-baselines
```

## Gemini mediation-baseline candidate refresh

This emits the committed Gemini-host baseline mediation packet doc to stdout for manual inspection.
It prints markdown for the committed Gemini baseline anchor with the committed relative-path header, does not overwrite the committed packet doc, and does not authorize any paired comparison or mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._gemini_mediation_baseline_packets
```

Repo-local entry point:

```sh
make emit-gemini-mediation-baselines-candidate
```

## Reference mediation-baseline candidate refresh

This emits candidate refreshed reference-host baseline mediation packet docs to stdout for manual inspection.
It prints markdown for all seven committed reference baseline packet docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize any paired comparison or mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_baseline_packets
```

Repo-local entry point:

```sh
make emit-reference-mediation-baselines-candidate
```

## Experimental reference mediated-thrash revalidation

This revalidates the three committed experimental reference-only mediated thrash comparators against live reference-host code paths.
It checks that each mediated packet stays reference-only, preserves the same completion class and truth boundary as baseline, and reduces branch oscillation without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediated_thrash_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediated-thrash
```

## Experimental reference mediated-thrash candidate refresh

This emits the committed experimental reference-only mediated thrash packet docs to stdout for manual inspection.
It prints markdown for all three committed thrash comparator docs with committed relative-path headers, does not overwrite the committed docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_thrash_experimental
```

Repo-local entry point:

```sh
make emit-reference-mediated-thrash-candidate
```

## Experimental reference mediated-uncertainty revalidation

This revalidates the three committed experimental reference-only mediated uncertainty comparators against live reference-host code paths.
It checks that each mediated packet stays reference-only, preserves contradiction/degradation handling and the same certified completion class as baseline, and reduces redundant uncertified loops without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediated_uncertainty_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediated-uncertainty
```

## Experimental reference mediated-uncertainty candidate refresh

This emits the committed experimental reference-only mediated uncertainty packet docs to stdout for manual inspection.
It prints markdown for all three committed uncertainty comparator docs with committed relative-path headers, does not overwrite the committed docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_uncertainty_experimental
```

Repo-local entry point:

```sh
make emit-reference-mediated-uncertainty-candidate
```

## Mediation Gemini uncertainty-basis revalidation

This checks that `scenario_uncertainty_gemini_01` now has one lawful committed non-reference baseline anchor.
It validates the Gemini baseline index, the Gemini uncertainty basis note, the committed Gemini packet doc, the absence of any Gemini mediated packet, and the package blocker truth. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_gemini_uncertainty_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-gemini-uncertainty-basis
```

## Mediation reference-uncertainty basis revalidation

This checks that `scenario_uncertainty_reference_01` now has a satisfied committed basis and replication law.
It validates the supporting basis note, the replication note, the committed uncertainty packet series, the live uncertainty builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_uncertainty_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-uncertainty-basis
```

## Mediation reference-thrash basis revalidation

This checks that `scenario_thrash_reference_01` now has a satisfied committed basis and replication law.
It validates the supporting basis note, the replication note, the committed thrash packet series, the live thrash builder set, and the deterministic branch-derivation and cross-pair distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_thrash_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-thrash-basis
```

## Aggregate mediation-evidence revalidation

This runs all current mediation-evidence checks together:
- package scaffold validation
- host-realization admissibility validation
- run-packet instance validation
- live reference baseline packet revalidation
- live Gemini baseline packet revalidation
- live experimental reference mediated-uncertainty revalidation
- live experimental reference mediated-thrash revalidation
- Gemini uncertainty baseline validation
- reference uncertainty basis and replication validation
- reference thrash basis and replication validation

It remains check-only and does not generate evidence or authorize mediation implementation.

Repo-local entry point:

```sh
make revalidate-mediation-evidence
```

## Individual entry points

```sh
make test-unit
make test-integration
make test-smoke
make verify
```

## Core correspondence drift check

This is the first Core-scoped correspondence drift check only.
It does not cover drivers, SRE, eval, AUX, or full correspondence parsing yet.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_core.py
```

Repo-local entry point:

```sh
make test-correspondence-core
```

## Ports correspondence drift check

This covers the landed Section 2 ports/provenance/normalization rows that remain outside the Section 1 Core audit.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_ports.py
```

Repo-local entry point:

```sh
make test-correspondence-ports
```

## SRE correspondence drift check

This is the SRE-scoped follow-on to the Core drift check.
It still does not cover drivers, eval, AUX, or full correspondence parsing.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_sre.py
```

Repo-local entry point:

```sh
make test-correspondence-sre
```

## Periphery correspondence drift check

Together with the Core, ports, and SRE checks, this completes the currently landed correspondence drift surface across Core, Section 2 ports, SRE, drivers, eval, and AUX.
The currently landed correspondence ledger is now mechanically covered short of full prose-ledger parsing.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_periphery.py
```

Repo-local entry point:

```sh
make test-correspondence-periphery
```

## Notes

- `pytest.ini` is intentionally minimal and only anchors discovery to `tests`.
- Packet-example evidence revalidation is limited to the committed reference-lane doc and remains separate from regeneration.
- Latency evidence revalidation is limited to checking the committed doc against live collection and remains separate from regeneration.
- `python3 -m pytest` also passes in the current repo, but the canonical local bundle remains the split closeout bundle above.

## Coverage prerequisite

This repo now has repo-local coverage configuration in `.coveragerc`.
This seam adds one local coverage invocation and one matching repo-local entry point.

Coverage is still not part of the canonical local verification bundle.
Minimal local prerequisite: install a package that provides `python3 -m coverage`.
Coverage tooling is not installed by default in the current repo environment, so `make coverage` will fail until that prerequisite is present.

Current repo-local coverage scope from `.coveragerc`:

- executed Python under `cortex/`
- executed test code under `tests/`

This coverage surface does not cover:

- `docs/`, `.claude/`, or other non-Python repo content
- files outside `cortex/` and `tests/`
- any threshold, pass/fail gate, or reinterpretation of MVP completeness from first coverage numbers

Direct command:

```sh
python3 -m coverage run --rcfile=.coveragerc -m pytest
python3 -m coverage report --rcfile=.coveragerc
```

Repo-local entry point:

```sh
make coverage
```

If the tool is unavailable, `make coverage` fails with a short actionable message instead of silently succeeding.

Still intentionally not included in this seam:

- no coverage baseline artifact
- no coverage threshold or pass/fail gate
