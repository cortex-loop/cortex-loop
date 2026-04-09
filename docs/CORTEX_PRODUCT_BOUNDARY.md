# CORTEX Product Boundary

Surface: product

This repository has four explicit surfaces.

`product`
- the shipped `cortex` package
- public product docs
- public OpenAI console entrypoints

`experimental`
- public non-shipping host/runtime source
- Claude, Gemini, and reference realizations that remain visible but are not the shipped default

`lab`
- evaluation, conformance, train loops, grading, and evidence tooling
- useful for iteration and falsification, but not part of the shipped product

`internal`
- workflow helpers
- phase gates
- correspondence
- active workstream state
- governance and planning records

Boundary rules:
- public packaging exposes only `cortex`
- public console scripts expose only `cortex-openai-cli` and `cortex-openai-service`
- product docs do not treat lab or governance surfaces as product identity
- product code must not depend on `experimental`, `lab`, or `internal`
