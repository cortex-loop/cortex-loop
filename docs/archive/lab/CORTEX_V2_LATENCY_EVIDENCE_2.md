# CORTEX_V2_LATENCY_EVIDENCE_2

Surface: lab

Status: active latency evidence record for the first landed reference lane
Date: 2026-03-18

Scope:
- reference-host cheap path
- reference-host candidate-bearing path
- reference-host full commitment path
- reference SRE neutral-dominance scoring

Measurement note:
- environment: Darwin 25.3.0, Python 3.14.3
- method: `time.perf_counter_ns` over in-process warmup plus fixed iteration loops
- warmup count: 40
- measured iterations per row: 400
- p95 method: nearest-rank over recorded samples
- exclusions: host network/model latency and external tool runtime cost are excluded

Evidence summary:

| Gate row | Median (ms) | P95 (ms) | Target median (ms) | Target P95 (ms) | Target met |
| --- | ---: | ---: | ---: | ---: | --- |
| cheap-path latency evidence | 0.0171 | 0.0184 | 5.0000 | 20.0000 | yes |
| candidate-bearing latency evidence | 0.0215 | 0.0241 | 15.0000 | 50.0000 | yes |
| full commitment latency evidence | 0.0257 | 0.0285 | 75.0000 | 250.0000 | yes |
| neutral SRE scoring latency evidence | 0.0014 | 0.0015 | 2.0000 | 10.0000 | yes |

Measured surfaces:
- cheap path: `evaluate_reference_host_neutral("ContextLoad", ...)`
- candidate-bearing path: `evaluate_reference_host_commitment("ApprovalRequest", ...)`
- full commitment path: `evaluate_reference_host_commitment("ApprovalResult", ..., provenance_manifest=...)`
- neutral SRE scoring: `neutral_dominance_decision(...)`

Supporting test surface:
- `tests/integration/test_reference_lane_latency.py::test_reference_lane_latency_evidence_is_structurally_produced`
