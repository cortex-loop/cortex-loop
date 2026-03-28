# CORTEX_V2_COVERAGE_BASELINE_NOTE_0

Date: 2026-03-21
Status: first committed repo-local coverage baseline for the landed v2 boundary

## Scope

This note records the first committed repo-local coverage baseline for the landed Cortex v2 MVP.
It is a verification artifact only.
It does not add a threshold, a pass/fail gate, CI enforcement, or any new product claim.

## Environment

- `python3 --version`: `Python 3.14.3`
- `python3 -m coverage --version`:
  - `Coverage.py, version 7.13.5 with C extension`
  - `Full documentation is at https://coverage.readthedocs.io/en/7.13.5`

## Commands

Direct commands:

```sh
python3 -m coverage run --rcfile=.coveragerc -m pytest
python3 -m coverage report --rcfile=.coveragerc
```

Repo-local entry point:

```sh
make coverage
```

## Coverage Scope

Current repo-local coverage scope from `.coveragerc`:

- executed Python under `cortex/`
- executed test code under `tests/`

This coverage surface does not cover:

- `docs/`, `.claude/`, or other non-Python repo content
- files outside `cortex/` and `tests/`
- any threshold, pass/fail gate, CI enforcement, or reinterpretation of MVP completeness from first coverage numbers

## Repeat Stability

- two consecutive `make coverage` runs were executed in the same environment
- the coverage report tables extracted from those two runs were byte-identical
- if future repeated `make coverage` runs produce different report tables, block note refresh until the drift is explained rather than silently updating the baseline

Observed run summary:

- first run: `558 passed in 0.73s`
- second run: `558 passed in 0.72s`

## Full Coverage Report From Second Run

```text
Name                                                                       Stmts   Miss  Cover
----------------------------------------------------------------------------------------------
cortex/__init__.py                                                             1      0   100%
cortex/aux/__init__.py                                                         1      0   100%
cortex/aux/augmentation.py                                                    39      2    95%
cortex/aux/cost.py                                                            33      2    94%
cortex/core/__init__.py                                                        1      0   100%
cortex/core/certification.py                                                  36      0   100%
cortex/core/commitment_extract.py                                             94      2    98%
cortex/core/commitment_payload.py                                            117      5    96%
cortex/core/commitments.py                                                   141      0   100%
cortex/core/dispatch.py                                                      133      8    94%
cortex/core/envelopes.py                                                      45      0   100%
cortex/core/environment.py                                                    57      0   100%
cortex/core/errors.py                                                         46      0   100%
cortex/core/lifecycle.py                                                      43      0   100%
cortex/core/observation.py                                                    61      0   100%
cortex/core/provenance.py                                                    262     59    77%
cortex/core/support.py                                                       148      2    99%
cortex/drivers/__init__.py                                                     1      0   100%
cortex/drivers/_commitment_common.py                                          40      1    98%
cortex/drivers/_neutral_common.py                                             24      1    96%
cortex/drivers/common_normalization.py                                        66      3    95%
cortex/drivers/gemini_host.py                                                125      4    97%
cortex/drivers/gemini_host_commitment.py                                     101      4    96%
cortex/drivers/gemini_host_neutral.py                                         60      2    97%
cortex/drivers/openai_host.py                                                115      3    97%
cortex/drivers/openai_host_commitment.py                                     101      4    96%
cortex/drivers/openai_host_neutral.py                                         60      2    97%
cortex/drivers/reference_host.py                                              53      2    96%
cortex/drivers/reference_host_commitment.py                                   50      0   100%
cortex/drivers/reference_host_neutral.py                                      32      0   100%
cortex/eval/__init__.py                                                        1      0   100%
cortex/eval/artifacts.py                                                     105     15    86%
cortex/eval/harness.py                                                        54      6    89%
cortex/eval/packets.py                                                       100     14    86%
cortex/runtime/__init__.py                                                     1      0   100%
cortex/sre/__init__.py                                                         1      0   100%
cortex/sre/allocation.py                                                      33      0   100%
cortex/sre/brake.py                                                           65      6    91%
cortex/sre/branching.py                                                        9      0   100%
cortex/sre/families.py                                                        12      0   100%
cortex/sre/goals.py                                                           19      0   100%
cortex/sre/opportunities.py                                                   78     13    83%
cortex/sre/policy.py                                                          52      3    94%
cortex/sre/state.py                                                           72      0   100%
cortex/sre/uncertainty.py                                                     22      0   100%
tests/_mediation_evidence.py                                                 190     12    94%
tests/integration/_gemini_host_realization_pair.py                            26      0   100%
tests/integration/_gemini_lane_packet_example.py                              42      4    90%
tests/integration/_gemini_mediated_lane_packet_example.py                     58      4    93%
tests/integration/_gemini_mediation_baseline_packets.py                       78      1    99%
tests/integration/_gemini_mediation_host_realization_experimental.py          62      1    98%
tests/integration/_gemini_mediation_thrash_episode.py                        157      2    99%
tests/integration/_gemini_mediation_thrash_experimental.py                    78      2    97%
tests/integration/_gemini_mediation_uncertainty_episode.py                   122      0   100%
tests/integration/_gemini_mediation_uncertainty_experimental.py               60      1    98%
tests/integration/_openai_host_realization_pair.py                            26      0   100%
tests/integration/_openai_lane_packet_example.py                              42      4    90%
tests/integration/_openai_mediated_lane_packet_example.py                     58      4    93%
tests/integration/_openai_mediation_baseline_packets.py                       79      1    99%
tests/integration/_openai_mediation_host_realization_experimental.py          62      1    98%
tests/integration/_openai_mediation_thrash_episode.py                        159      2    99%
tests/integration/_openai_mediation_thrash_experimental.py                    77      2    97%
tests/integration/_openai_mediation_uncertainty_episode.py                   122      0   100%
tests/integration/_openai_mediation_uncertainty_experimental.py               62      1    98%
tests/integration/_reference_host_realization_pairs.py                        27      0   100%
tests/integration/_reference_lane.py                                          44      0   100%
tests/integration/_reference_lane_latency_evidence.py                         12      4    67%
tests/integration/_reference_lane_packet_example.py                           38      4    89%
tests/integration/_reference_mediated_lane_packet_example.py                  54      4    93%
tests/integration/_reference_mediation_baseline_packets.py                   107      1    99%
tests/integration/_reference_mediation_host_realization_experimental.py       62      1    98%
tests/integration/_reference_mediation_thrash_episode.py                     156      2    99%
tests/integration/_reference_mediation_thrash_experimental.py                 77      2    97%
tests/integration/_reference_mediation_uncertainty_episode.py                115      0   100%
tests/integration/_reference_mediation_uncertainty_experimental.py            61      1    98%
tests/integration/test_aux_claim_conservative.py                              54      0   100%
tests/integration/test_gemini_lane_packet_example.py                          16      1    94%
tests/integration/test_gemini_mediated_host_realization_comparator.py         89      0   100%
tests/integration/test_gemini_mediated_lane_packet_example.py                 16      1    94%
tests/integration/test_gemini_mediated_thrash_comparator.py                   71      0   100%
tests/integration/test_gemini_mediated_uncertainty_comparator.py              75      0   100%
tests/integration/test_gemini_mediation_baseline_packets.py                   89      0   100%
tests/integration/test_openai_lane_packet_example.py                          16      1    94%
tests/integration/test_openai_mediated_host_realization_comparator.py         89      0   100%
tests/integration/test_openai_mediated_lane_packet_example.py                 16      1    94%
tests/integration/test_openai_mediated_thrash_comparator.py                   71      0   100%
tests/integration/test_openai_mediated_uncertainty_comparator.py              75      0   100%
tests/integration/test_openai_mediation_baseline_packets.py                   86      0   100%
tests/integration/test_reference_host_neutral.py                              35      0   100%
tests/integration/test_reference_host_vertical_gate.py                        46      0   100%
tests/integration/test_reference_lane_latency.py                             176      4    98%
tests/integration/test_reference_lane_packet_example.py                       16      1    94%
tests/integration/test_reference_mediated_host_realization_comparator.py      88      0   100%
tests/integration/test_reference_mediated_lane_packet_example.py              16      1    94%
tests/integration/test_reference_mediated_thrash_comparator.py                71      0   100%
tests/integration/test_reference_mediated_uncertainty_comparator.py           75      0   100%
tests/integration/test_reference_mediation_baseline_packets.py                62      0   100%
tests/unit/test_aux_scaffolds.py                                             179      0   100%
tests/unit/test_certification_artifacts.py                                   121      0   100%
tests/unit/test_commitment_extract.py                                        106      0   100%
tests/unit/test_commitment_payload.py                                        120      0   100%
tests/unit/test_common_normalization.py                                       37      0   100%
tests/unit/test_core_substrate.py                                            540      1    99%
tests/unit/test_correspondence_contract.py                                    28      0   100%
tests/unit/test_correspondence_core.py                                        27      0   100%
tests/unit/test_correspondence_periphery.py                                   31      0   100%
tests/unit/test_correspondence_ports.py                                       30      0   100%
tests/unit/test_correspondence_sre.py                                         31      0   100%
tests/unit/test_dispatch.py                                                  135      0   100%
tests/unit/test_eval_harness.py                                               75      0   100%
tests/unit/test_eval_packets.py                                               86      0   100%
tests/unit/test_gemini_host.py                                                54      0   100%
tests/unit/test_gemini_host_commitment.py                                     96      0   100%
tests/unit/test_gemini_host_neutral.py                                        54      0   100%
tests/unit/test_import_smoke.py                                                7      0   100%
tests/unit/test_mediation_evidence_package.py                                223      6    97%
tests/unit/test_mediation_gemini_host_realization_basis.py                    73      0   100%
tests/unit/test_mediation_gemini_thrash_basis.py                              63      0   100%
tests/unit/test_mediation_gemini_uncertainty_basis.py                         69      0   100%
tests/unit/test_mediation_openai_host_realization_basis.py                    75      0   100%
tests/unit/test_mediation_openai_thrash_basis.py                              63      0   100%
tests/unit/test_mediation_openai_uncertainty_basis.py                         68      0   100%
tests/unit/test_mediation_reference_host_realization_basis.py                 70      0   100%
tests/unit/test_mediation_reference_thrash_basis.py                           67      0   100%
tests/unit/test_mediation_reference_uncertainty_basis.py                      60      0   100%
tests/unit/test_mediation_run_packets.py                                     331     11    97%
tests/unit/test_openai_host.py                                                54      0   100%
tests/unit/test_openai_host_commitment.py                                     96      0   100%
tests/unit/test_openai_host_neutral.py                                        55      0   100%
tests/unit/test_provenance_evidence.py                                        71      0   100%
tests/unit/test_provenance_helpers.py                                         78      0   100%
tests/unit/test_reference_host.py                                             36      0   100%
tests/unit/test_reference_host_commitment.py                                  59      0   100%
tests/unit/test_sre_goals_branching.py                                        56      0   100%
tests/unit/test_sre_neutral_hinge.py                                         147      1    99%
tests/unit/test_sre_opportunities.py                                          75      0   100%
tests/unit/test_sre_uncertainty_brake.py                                      99      9    91%
tests/unit/test_verification_docs_sync.py                                     92      3    97%
----------------------------------------------------------------------------------------------
TOTAL                                                                      10208    265    97%
```

## Non-Claims

- no coverage threshold
- no pass/fail gate
- no CI enforcement
- no reinterpretation of MVP completeness from first coverage numbers
- no claim that non-Python repo content is covered
