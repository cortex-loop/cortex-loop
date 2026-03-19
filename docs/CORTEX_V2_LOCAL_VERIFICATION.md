# CORTEX_V2_LOCAL_VERIFICATION

Date: 2026-03-18
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
