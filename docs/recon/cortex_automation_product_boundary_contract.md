# Cortex Automation Product-Boundary Contract

## Verdict

`pass_cortex_automation_product_boundary_contract`

This is a no-live automation/evaluator hardening seam. It does not change
product host behavior, model-visible text, packet law, matcher thresholds,
fixtures, scoring semantics, hidden-verifier surfaces, root hooks, or candidate
policy. It does not run live Codex.

## Boundary Decision

Cortex product remains the shipped runtime executive layer: lawful lifecycle
state, intervention decisions, control modes, host actions, and model I/O. The
overnight loop and evaluator are support surfaces. They may build proof, run
registered evaluators, and later search bounded lifecycle policies, but they are
not Cortex product identity and cannot claim product progress by improving lab,
eval, recon, or workflow machinery alone.

The evaluator now carries a mission objective contract on design and episode
rows:

- `executive_function`
- `loop_stage`
- `control_mode`
- `truth_scope`
- `model_io_path`
- `product_spine`
- `contraction_implication`

Rows with `model_io_path=none_lab_proof_only` are lab/proof-only rows. They
hard-fail if they claim Cortex product value, behavior lift, exactness value
lift, broad Cortex lift, Codex App parity, or shipping promotion. Product-facing claims require a non-empty model-I/O path and a product spine: capability -> state law -> enforcement decision -> host action -> model I/O.

## Automation Contract

`internal/automation/cortex_overnight_loop.py` now distinguishes support work
from product work mechanically:

- Lab/eval/workflow changes may be auto-merged only as proof/support, not as
  product progress.
- Candidate rows touching `cortex/**` must declare a product spine, a non-lab
  model-I/O path, and current-truth authorization.
- Candidate rows may not mutate evaluator scoring, fixtures, hidden verifier
  surfaces, Core law, packet law, workflow gates, or generated product docs as
  policy-search mutations.
- Structured positive value/shipping fields force user review even if prose is
  neutral.
- Morning digests must answer which executive function was served, which loop stage improved, what model-I/O path exists, whether the simple hook beat/tied or lost, and what should be contracted.

## Proof

Proof surfaces:

- `lab/cortex_effectiveness_evaluator.py`
- `tests/lab/test_cortex_effectiveness_evaluator.py`
- `internal/automation/cortex_overnight_loop.py`
- `tests/internal/test_cortex_overnight_loop.py`
- `tests/internal/test_docs_boundary.py`

The four-arm evaluator remains unchanged in purpose:
`no_cortex_baseline`, `simple_hook_baseline`, `cortex_silent_perception`, and
`cortex_active_policy`. Simple-hook parity and silent perception success remain no-value, not Cortex wins. The historical PostToolUse `failure_no_value` replay remains negative evidence.

## Next Train

Queue `cortex-executive-effectiveness-evaluator-live-gate1`.

That next seam may register the exact future live command/env pair and approval
refusal for the evaluator live matrix. It must not run live Codex, implement the
simple hook, mutate product policy, or start candidate evolution inside this
boundary seam.

## Forbidden Claims

This seam earns no behavior lift, exactness value lift, broad Cortex lift,
Codex App parity, shipping promotion, or product behavior progress. It earns a
support-surface boundary: the development loop is now constrained to serve
Cortex rather than becoming Cortex.
