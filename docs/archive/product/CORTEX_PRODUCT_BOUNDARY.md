# CORTEX Product Boundary

Surface: product

This repository has four explicit surfaces.

`product`
- the shipped `cortex` package
- active shared Cortex law in `cortex/core`, `cortex/sre`, `cortex/runtime`, and `cortex/hosts/*`
- the active docs listed in `docs/CORTEX_STATUS.md`

`lab`
- evaluation, conformance, train loops, grading, and evidence tooling
- generated evidence in `.cortex/`
- useful for iteration and falsification, but not part of the shipped product

`internal`
- workflow helpers
- `internal/truth/cortex_status.json`, the machine-backed operational truth
- `docs/internal/REPO_WORKFLOW.md`, the active workflow contract

`archive`
- historical runtime briefs, status notes, lab narratives, and superseded governance material
- archival tests that validate preserved evidence or retired doctrine

`experimental`
- true off-by-default or not-yet-promoted experiments only
- experimental status is tracked in `docs/CORTEX_STATUS.md`, not by hiding active Cortex code outside `cortex/`

Boundary rules:
- public packaging exposes only `cortex`
- public console scripts expose only `cortex-openai-cli` and `cortex-openai-service`
- the operational front door is `AGENTS.md` + `docs/CORTEX_STATUS.md`
- archived docs do not act as live truth
- product code must not depend on `experimental`, `lab`, or `internal`
