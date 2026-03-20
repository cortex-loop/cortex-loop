# CORTEX_V2_MEDIATION_REFERENCE_THRASH_BASIS_NOTE_0

Date: 2026-03-20
Status: `artifact_gap remains honest`

## Scope

This note records why `scenario_thrash_reference_01` still remains an explicit `artifact_gap`.
It does not justify mediation, activate mediation, or authorize a thrash baseline packet seam by itself.

## Current Audit Result

`scenario_thrash_reference_01` must remain `artifact_gap` in the current repo state.

The audited surfaces are insufficient for a committed reference thrash baseline packet:

- existing reference-host evidence is limited to single-path reference-host commitment and publication packets
- the committed reference baseline packet surfaces cover uncertainty and host realization only
- the SRE branch, goals, and brake tests are carrier and policy surfaces, not a bounded reference-host multi-step episode
- no current repo surface records a lawful repeated reopen/resume or branch-oscillation trace on a bounded reference-host task

## Audited Insufficient Surfaces

The current audit covered these surfaces and found them insufficient as a runnable basis:

- reference-host commitment/publication packet surfaces:
  - `tests/unit/test_reference_host_commitment.py`
  - `tests/integration/test_reference_lane_packet_example.py`
  - `tests/integration/test_reference_mediation_baseline_packets.py`
- SRE branch/goals/brake carrier tests:
  - `tests/unit/test_sre_goals_branching.py`
  - `tests/unit/test_sre_neutral_hinge.py`

Carrier or policy tests alone are insufficient.
They do not record a reference-host multi-step episode, a visible branch trajectory, or a lawful reopen/resume trace that could support a committed baseline mediation packet.

## Future Packet Readiness Checklist

All of the following must exist before a future `scenario_thrash_reference_01` packet seam may open:

- one bounded `reference`-host multi-step scenario, not a pure SRE unit test
- at least one candidate-bearing or full-commitment turn plus at least one follow-up turn on the same episode
- explicit branch trajectory evidence, including at least one reopen/resume, suspend/resume, or equivalent branch-control event that is visible in committed evidence
- explicit task-value completion outcome so thrash reduction cannot be claimed by abandoning the task
- the same commitment boundary and evidence/publication surface that future mediated comparison would use
- a live builder from code
- a committed markdown baseline packet
- a semantic revalidation test from live code
- a candidate-emission command that does not overwrite docs

## Non-Qualifying Anti-Patterns

These do not qualify as a future `scenario_thrash_reference_01` basis:

- pure carrier-type tests
- synthetic branch labels with no host episode
- single-turn packets with prose that merely mentions churn
- any packet that infers reopen/resume behavior without committed trace evidence

## Outcome

Until the readiness checklist is satisfied from live reference-host code, `scenario_thrash_reference_01` must stay `artifact_gap`.
