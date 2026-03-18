# CORTEX_V2_LOCAL_VERIFICATION

Date: 2026-03-18
Status: active local verification entry points for the landed v2 boundary

## Purpose

This document records the repo-local verification commands for the landed Cortex v2 MVP.
It does not add coverage, CI, evidence regeneration, or correspondence audit tooling.

## Canonical bundle

Direct commands:

```sh
python3 -m pytest tests/unit
python3 -m pytest tests/integration
python3 -m pytest tests/unit/test_import_smoke.py
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
python3 -m pytest tests/unit/test_import_smoke.py \
  tests/integration/test_reference_host_vertical_gate.py::test_driver_to_core_to_sre_smoke_stays_observe_bind_dispatch_and_neutral
```

Repo-local entry point:

```sh
make test-smoke
```

## Individual entry points

```sh
make test-unit
make test-integration
make test-smoke
make verify
```

## Notes

- `pytest.ini` is intentionally minimal and only anchors discovery to `tests`.
- There is still no repo-local coverage configuration in this seam.
- This seam does not add evidence revalidation or correspondence audit tooling.
- `python3 -m pytest` also passes in the current repo, but the canonical local bundle remains the split closeout bundle above.
