# Cortex OpenAI Operator Output-Quality Fixture Refresh

Surface: product / live recon

Probe date: 2026-05-02

Branch: `codex/20260502-185241-silent-control-live-fixture-refresh`

## Verdict

The fixture-refresh seam found a harder OpenAI Codex App/CLI wrapper-resume live task family for
the next silent-control work: `astro_docs_site_v1` now reproduces the desired
baseline shape in clean operator runs. The raw `gpt-5.3-codex` operator makes
real edits, passes objective visible checks, and still fails the hidden verifier
because the docs search dataset marker is missing.

This does not prove silent-control behavior lift. The existing output-quality
`cortex` arm repaired and passed the task once, but that path uses the
output-quality visible contract and repair turn. It is evidence that the
Astro fixture is hard and recoverable, not evidence that silent SRE debt
control has improved model behavior.

## Setup Finding

An initial run was contaminated by the parent Cortex repo lifecycle surface:

```text
.cortex/live_validation/output_quality/openai_operator_cli/run_20260502T165319+0000
```

That run timed out after the operator produced this repo's Cortex Mission
Reflection instead of working the Astro fixture. The cause was fixture
workspaces living under `.cortex/` without their own Git root, which allowed
the Codex CLI to inherit the parent repo's agent contract and hooks.

The harness now initializes every output-quality fixture workspace as an
isolated Git repository before operator invocation. The isolation is pinned by
`tests/lab/test_cortex_output_quality.py::test_output_quality_operator_workspace_gets_isolated_git_root`.

## Clean Baseline Reproduction

After workspace isolation, three clean raw OpenAI operator runs reproduced the
same hard-failure shape.

| Artifact | Arm | Objective visible checks | Hidden quality | Failure |
| --- | --- | ---: | ---: | --- |
| `.cortex/live_validation/output_quality/openai_operator_cli/run_20260502T165814+0000` | `raw` | pass | fail | `docs search dataset marker is missing` |
| `.cortex/live_validation/output_quality/openai_operator_cli/run_20260502T170004+0000` | `raw` | pass | fail | `docs search dataset marker is missing` |
| `.cortex/live_validation/output_quality/openai_operator_cli/run_20260502T170702+0000` | `raw` | pass | fail | `docs search dataset marker is missing` |

This gives `astro_docs_site_v1` a 3/3 clean baseline reproduction rate for the
specific shape seam 5 needed but did not have: fluent visible success without
the hidden verification work actually being complete.

## Cortex Comparison Run

The paired output-quality run was:

```text
.cortex/live_validation/output_quality/openai_operator_cli/run_20260502T170004+0000
```

The aggregate result was:

| Arm | Objective visible checks | Hidden quality | Protocol valid |
| --- | ---: | ---: | ---: |
| `raw` | pass | fail | pass |
| `cortex` | pass | pass | pass |

The pairwise result was `cortex_vs_raw` wins `1`, losses `0`, ties `0`. The
reason tags included `passes-hidden-checks`, `search-dataset-marker-present`,
and `meets-route-and-navigation-requirements`.

This comparison remains output-quality evidence, not silent-control evidence:
the `cortex` arm used its visible contract and repair machinery. The next
product seam must connect the silent-control host-adapter path to this
Astro-style hidden-verifier failure without changing the initial prompt or
borrowing visible warning text.

## Truth Accounting

Cortex truth: A live OpenAI operator hard fixture now exists for the executive
failure shape Cortex cares about: visible/objective success can mask missing
verification work on a realistic Astro implementation task.

Brain-wiring truth: On `astro_docs_site_v1`, `gpt-5.3-codex` repeatedly builds
a plausible docs section and passes visible checks while missing the hidden
search dataset requirement.

Conformance truth: The output-quality lab harness now isolates operator
fixture workspaces as their own Git repositories, preventing parent repo
agent-contract or hook contamination.

Shipping truth: Unchanged. This seam does not promote silent-control behavior
lift, no-overblock safety, Claude/Gemini parity, AUX behavior, visible
intervention records, or shipping default behavior.

## Earned

- `astro_docs_site_v1` is a valid hard fixture candidate for the OpenAI
  Codex App/CLI wrapper-resume path.
- Raw baseline failure reproduced in 3/3 clean runs after workspace isolation.
- The failure is not setup noise: objective visible checks pass while the
  hidden verifier fails on the missing search dataset marker.
- The existing output-quality `cortex` arm can recover once on this task class.
- Parent repo lifecycle/hook contamination has a concrete harness fix and test.

## Not Earned

- no silent-control behavior lift;
- no prompt-identical shaped-vs-baseline result on this Astro fixture;
- no no-overblock or clean-control result for this fixture;
- no claim that the current `resume_recheck` truth-gap action is sufficient for
  output-quality hidden-verifier failures;
- no Claude Code Desktop, Gemini, AUX, hook, or `tau` proof;
- no shipping promotion.

## Next Seam

Open `silent-control-output-quality-enactment` before retrying the paired live
matrix.

That seam should adapt the silent-control host-adapter/harness path so an
Astro-style hidden-verifier failure can be tested as a prompt-identical
baseline-vs-shaped continuation-policy trial. The gate must stay silent: no
initial prompt mutation, no visible Cortex/debt/brake vocabulary, no reuse of
the output-quality visible contract as if it were silent control, and no
shipping promotion.
