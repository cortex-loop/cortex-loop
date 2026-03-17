# CORTEX_V2_IMPLEMENTATION_READINESS_NOTE

Status: active implementation note for Phase 0B shared-state closure (`active`, implementation-facing, doc-only)
Date: 2026-03-17

This note closes the Phase 0B implementation free variables called out in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`.
It is subordinate to the active Core / SRE / AUX packet and does not change packet ownership.

## 1. Boundary and scope lock

- Core owns lifecycle observation, support snapshots, commitment extraction, wake enforcement, provenance, blockedness, and hard boundaries.
- SRE owns recoverable role views, mode/gating evaluation, soft-family admissibility, branch/pending-goal discipline, and goal/control scoring.
- AUX remains support-only. It may publish support memory, but it may not write commitment truth, blockedness, hard boundaries, or host-capability truth.
- This note does not reopen mediation, geometry runtime, offline learning, or host-specific policy.

## 2. `W_t` reference families and write boundaries

For implementation, treat support state as:

\[
W_t = (W_t^{trace}, W_t^{session}, W_t^{host}, W_t^{execmem,pub})
\]

| Family | Minimum contents | Persistence | Write owner |
| --- | --- | --- | --- |
| `W_t^{trace}` | recent event envelopes, extracted candidate references, wake receipts, degradation notes, lightweight observables | rolling per-session window; not durable across sessions | Drivers/Core only |
| `W_t^{session}` | branch registry, pending-goal state, role-view cache, budget/brake history, wake counters, session-local reminders | durable only for the current session/run | SRE owns executive working fields; Drivers/Core may append host-observed session facts but may not rewrite SRE-owned fields |
| `W_t^{host}` | current host affordance snapshot, approval-boundary facts, observed capability limits, host constraint state | session/config scoped | Drivers/Core only |
| `W_t^{execmem,pub}` | published support memory and AUX-produced support artifacts | cross-session durable support memory | AUX publication flow only; Core and SRE are read-only consumers |

Operational rules:
- No layer may silently rewrite another layer's authority object.
- Core and SRE may read all `W_t` families needed for lawful runtime behavior, but read access does not widen write authority.
- `W_t` names mutable support state only. The output of `Snapshot(\mathcal O_{t,r}, W_t)` is a separate read-only object and must not be written back as if it were `W_t`.

## 3. Minimum software-shaped role views

The SRE remains representation-flexible, but the implementation must be able to recover at least these software-facing views from `W_t^{session}` or an equivalent session-local carrier:

| View | Minimum recoverable fields |
| --- | --- |
| `goal_continuity` | `main_goal_anchor`, `active_track_id`, `pending_goal_count` or bounded pending set, `resume_anchor_available` |
| `uncertainty_monitoring` | classwise uncertainty summary, `contradiction_flag`, `spike_flag` |
| `mode_and_gating` | `mode_tag`, `family_mask` |
| `control_allocation` | `budget_band`, `top_family_set`, `host_friction_summary` |
| `brake` | `brake_state` in `{quiescent, guarded, latched}`, `dominant_cause` |

These are recoverability requirements, not a mandate for one latent theorem or storage layout.

## 4. Mode and gating reference content

`family_mask` must be able to admit or suppress at least the SRE reference families:
`neutral`, `seek-context`, `redirect`, `check`, `branch`, `escalate`, `brake`.

Reference mode tags and operational meaning:

| `mode_tag` | Operational meaning |
| --- | --- |
| `pass_through` | default lane; `neutral` remains available and only bounded low-cost intervention is admissible by default |
| `verify` | favor `check` and `seek-context`; keep `neutral`; suppress branch-heavy or externally consequential soft actions unless separately justified |
| `branching` | permit `branch` actions only when branch budget, branch depth, and resume-anchor recoverability remain satisfied |
| `recovery` | favor `redirect`, `check`, `seek-context`, and `brake` after contradiction, failure, or degraded host feedback; do not relax commitment standards |
| `handoff` | allow `escalate` or host-native handoff surfaces; suppress low-value local retry loops |

Operational rules:
- `neutral` should remain admissible unless the runtime is already blocked or a hard boundary prevents further local action.
- A direct host-native opportunity must map to an admissible family or be treated as `escalate` / `handoff`, not as an ungated side channel.
- Mode/gating is SRE policy state. It does not change commitment truth, blockedness, or boundary law.

## 5. Commitment wake reference heuristic and coding-lane table

The full commitment path may run only when at least one Core-consistent wake condition is true:

1. the event is in a host/runtime commitment subset;
2. a structured or extracted commitment candidate is present;
3. the host marks the action as externally consequential or approval-gated;
4. a durable write, publish, submit, or externally visible claim is about to occur;
5. a hard safety or integrity boundary check is explicitly required.

Coding reference lane decision table:

| Event surface | Example | Path |
| --- | --- | --- |
| stream token / bounded prose / chat chunk | ordinary generation text | cheap |
| read-only tool result | test output, file read, search result | cheap |
| branch bookkeeping | open, suspend, resume, merge, abandon marker | cheap unless paired with a commitment claim |
| write or approval proposal | durable write intent, patch proposal, approval request before crossing the boundary | candidate-bearing |
| durable write execution or approved external mutation | file mutation committed, external record changed, approval accepted across an external boundary | full commitment |
| final completion claim | `fixed`, structured completion payload, task-complete callback | full commitment |

Operational rules:
- Candidate-bearing events may run lightweight extraction but do not force provenance collection when extraction is empty.
- Read-only evidence may update environment views and later support certification, but it does not wake the full path by itself.
- Over-waking and under-waking are both implementation bugs on the reference lane.

## 6. Naming and notation cleanup

Use the following implementation-facing names consistently:

| Concept | Reference name | Rule |
| --- | --- | --- |
| mutable support state | `W_t` | reserve for the writable support-state families only |
| support snapshot | `Wsnap_t` or `SupportSnapshot_t` | use for the read-only output of `Snapshot(...)`; do not reuse `S_t` |
| commitment status | `CStat_t(c)` or `CommitStatus_t(c)` | keep separate from support snapshots and SRE state |
| wake decision | `Wake_t` | store the decision plus its triggering reason set |
| SRE role views | `goal_continuity`, `uncertainty_monitoring`, `mode_and_gating`, `control_allocation`, `brake` | use these names or a one-to-one alias set |

Do not reuse bare `S_t` for support snapshot, commitment status, and session state in the same code path or design note.

## 7. Goal-term separation rule

Implementation-facing scoring must separate main-goal continuity from branch-lifecycle fitness:

- `q_goal_main(a)` means main-task preservation, active-track continuity, and pending-goal discipline for action `a`.
- `q_goal_branch(a)` means branch-management fitness for action `a`.
- `q_goal_main(a)` may contribute to any relevant family.
- `q_goal_branch(a)` may contribute only to branch-bearing actions or explicit branch lifecycle decisions.
- A non-branch candidate may not receive both terms.
- If a branch action combines both terms, the combination must be explicit and normalized once.

Packet mapping rule:
- `docs/CORTEX_V2_SRE_2.md` remains the authority for packet notation.
- For implementation work, treat `Q_t^{goalbranch}` as the branch-specific family contribution, not as a second copy of generic goal progress.

## 8. Effect on the next seam

With this note in place, Phase 0B is closed for implementation planning.
The next coding seam may build the smallest Core/SRE substrate without reopening `W_t`, role-view recoverability, mode/gating content, wake classification, notation, or goal-term separation.
