# Cortex

Cortex is the executive layer for frontier models. The shipped product is the `cortex` package: a small integrity core plus the active runtime executive that improves model behavior during real work.

V2 remains the shipped package and product truth in this repo. V3 now exists in parallel as the `cortex_v3` incubation track: a host-neutral verified-work library with thin OpenAI, Claude, and Gemini adapters that can prove a cutover seam without rewriting V2 in place.

Current shipped surface:
- OpenAI product runtime on the CLI lane, with the direct service kept as a non-default backup surface
- executive control centered on bounded contracts, external verification, and constrained repair

Current repo truth:
- richer shared executive code lives in `cortex/sre`
- host-native realizations live in `cortex/hosts/*`
- shipping truth remains narrower than conformance truth and is tracked in `docs/CORTEX_STATUS.md`

Not the product:
- diagnostics
- train loops
- graders
- causal maps
- workflow ledgers
- governance records

Those supporting surfaces still exist in this repository, but they live in explicit non-product areas:
- `experimental/` for true off-by-default or not-yet-promoted experiments only
- `lab/` for evaluation and proving machinery
- `internal/` for workflow and the machine-backed status registry
- `docs/archive/` for historical runtime, lab, and governance material

Start here:
- [Current Status](docs/CORTEX_STATUS.md)
- [Product Charter](docs/CORTEX_PRODUCT_CHARTER.md)
- [Product Boundary](docs/CORTEX_PRODUCT_BOUNDARY.md)
- [V3 Incubation Track](docs/v3/README.md)
- [Docs Index](docs/README.md)
