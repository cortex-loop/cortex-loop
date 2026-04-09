# Cortex

Cortex is the executive layer for frontier models. The shipped product is the `cortex` package: a small integrity core plus the active runtime executive that improves model behavior during real work.

Current shipped surface:
- OpenAI product runtime on the direct service and CLI lanes
- executive control centered on bounded contracts, external verification, and constrained repair

Not the product:
- diagnostics
- train loops
- graders
- causal maps
- workflow ledgers
- governance records

Those supporting surfaces still exist in this repository, but they live in explicit non-product areas:
- `experimental/` for public non-shipping host/runtime source
- `lab/` for evaluation and proving machinery
- `internal/` for workflow and governance

Start here:
- [Product Charter](docs/CORTEX_PRODUCT_CHARTER.md)
- [Product Boundary](docs/CORTEX_PRODUCT_BOUNDARY.md)
- [Docs Index](docs/README.md)
