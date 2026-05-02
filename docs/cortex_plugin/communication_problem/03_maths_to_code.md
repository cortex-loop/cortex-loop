# 03 — Maths To Code

This file extracts the structural math ledger from
`internal/truth/cortex_status.json` so a reasoning model can see what formal
objects Cortex already claims in code.

## `τ`-Relevant State Algebra

The full map below is intentionally complete. A solver should first compress it
into the state families that can legitimately affect model-visible
communication. This table is a reading map, not a replacement for the code or
registry data.

| State family | Cortex sources | Model-visible meaning `τ` may express | What must not leak |
| --- | --- | --- | --- |
| Claim state | `commitment_candidate`, `provenance_manifest`, `boundary_assessment`, last assistant message | The model made, refused, revised, or failed to support a specific claim. | Internal commitment ids, certification jargon, or provenance machinery names. |
| Evidence state | `observation_bundle`, `ReferenceRealizationFeedback`, tool result summaries, verified-work runtime results | A concrete command, file, artifact, or observation supports or fails to support the claim. | Feedback class names, schema ids, raw JSON, or harness labels. |
| Obligation state | `goal_debt_state`, branch/goal continuity records, closure-pressure state | A task, verification step, artifact, or user-requested goal remains unfinished. | Tags such as `pending_goal_debt`, closure-pressure internals, or branch-registry scaffolding. |
| Inhibition state | `executive_modulator_state`, brake state, risk weights, neutral-dominance decisions | The next action should slow down, ask, verify, or avoid closure because uncertainty or contradiction is high. | Brake labels, tonic/phasic implementation terms, or hidden policy wording. |
| Capability state | `operator_brain_capability_envelope`, operator routing, unsupported/degrade decisions | The requested task may exceed the current operator/tool affordance, so the model should narrow, ask, or route. | Model-band priors, route codes, or capability envelope identifiers. |
| Continuity state | host runtime sessions, persisted host-local state, feedback windows | The current response should account for what happened earlier in this bounded task/session. | Raw session ids, transcript paths, persistence implementation details, or cross-thread resume claims not earned live. |
| Support state | AUX publications, support priors, augmentation state | Published support evidence can bias a bounded decision when fresh, host-matched, and explicitly supplied. | Raw memory episodes, default-on memory implications, or support geometry internals. |
| Host-affordance state | Claude Code hook event, output shape, block/additional-context/system-message channel | The message must fit what the host can legally deliver at this lifecycle boundary. | Fictional uniform middleware assumptions or claims that a structural hook path already earned behavior lift. |

The function `τ` should map combinations of these families into task-local
claim/evidence/obligation/uncertainty language. It should not map internal
symbol names directly to the model. A candidate that cannot name which state
families it consumes is not yet solving the communication problem.

## Full `math_to_code_map`

```json
[
  {
    "id": "lifecycle_event_envelope",
    "label": "Lifecycle event envelope",
    "packet_ref": "CORE_2 §4.1",
    "code_refs": [
      "cortex/core/envelopes.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py"
    ],
    "status": "implemented"
  },
  {
    "id": "observation_bundle",
    "label": "Event-local observation bundle",
    "packet_ref": "CORE_2 §6.1",
    "code_refs": [
      "cortex/core/observation.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py"
    ],
    "status": "implemented"
  },
  {
    "id": "split_environment_handles",
    "label": "Executive vs commitment environment handles",
    "packet_ref": "CORE_2 §6.2",
    "code_refs": [
      "cortex/core/environment.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py"
    ],
    "status": "implemented"
  },
  {
    "id": "environment_query",
    "label": "Generalized environment query",
    "packet_ref": "CORE_2 §6.3",
    "code_refs": [
      "cortex/core/environment.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py"
    ],
    "status": "implemented"
  },
  {
    "id": "commitment_candidate",
    "label": "Commitment candidate and status lattice",
    "packet_ref": "CORE_2 §7.1, §7.2",
    "code_refs": [
      "cortex/core/commitments.py"
    ],
    "proof_refs": [
      "tests/product/test_certification_artifacts.py"
    ],
    "status": "implemented"
  },
  {
    "id": "provenance_manifest",
    "label": "Downward provenance dominance manifest",
    "packet_ref": "CORE_2 §7.3",
    "code_refs": [
      "cortex/core/commitments.py"
    ],
    "proof_refs": [
      "tests/product/test_certification_artifacts.py"
    ],
    "status": "implemented"
  },
  {
    "id": "wake_decision",
    "label": "Commitment wake decision and dispatch",
    "packet_ref": "CORE_2 §5, §7.4",
    "code_refs": [
      "cortex/core/dispatch.py"
    ],
    "proof_refs": [
      "tests/product/test_dispatch.py"
    ],
    "status": "implemented"
  },
  {
    "id": "boundary_assessment",
    "label": "Event-local certification firewall assessment",
    "packet_ref": "CORE_2 §8.1, §11.1",
    "code_refs": [
      "cortex/core/commitments.py"
    ],
    "proof_refs": [
      "tests/product/test_certification_artifacts.py"
    ],
    "status": "implemented"
  },
  {
    "id": "support_state",
    "label": "Recoverable executive role / support state",
    "packet_ref": "CORE_2 §8.2",
    "code_refs": [
      "cortex/core/support.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py"
    ],
    "status": "implemented"
  },
  {
    "id": "executive_signal_summary",
    "label": "Minimal software-shaped executive role view",
    "packet_ref": "SRE_2 §3.1",
    "code_refs": [
      "cortex/sre/executive_summary.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_uncertainty_brake.py"
    ],
    "status": "implemented"
  },
  {
    "id": "neutral_dominance_decision",
    "label": "Neutral-dominance arbitration",
    "packet_ref": "SRE_2 §6.6",
    "code_refs": [
      "cortex/sre/policy.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_neutral_hinge.py"
    ],
    "status": "implemented"
  },
  {
    "id": "risk_weight",
    "label": "Asymmetric error-cost RiskWeight carrier",
    "packet_ref": "SRE_2 §6.6.1",
    "code_refs": [
      "cortex/sre/state.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_neutral_hinge.py"
    ],
    "status": "implemented"
  },
  {
    "id": "operator_brain_capability_envelope",
    "label": "Operator brain capability envelope",
    "packet_ref": "SRE_2 §6.9",
    "code_refs": [
      "cortex/sre/operator_routing.py",
      "cortex/runtime/operator_brain_capability.py"
    ],
    "proof_refs": [
      "tests/product/test_brain_capability.py",
      "tests/conformance/test_brain_capability_parity.py"
    ],
    "status": "implemented"
  },
  {
    "id": "executive_modulator_state",
    "label": "Brake tonic EMA executive modulator state",
    "packet_ref": "SRE_2 §7.4, §7.5",
    "code_refs": [
      "cortex/sre/modulators.py",
      "cortex/sre/brake.py",
      "cortex/hosts/claude_code_desktop/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_uncertainty_brake.py",
      "tests/conformance/test_claude_code_desktop_runtime_session_io.py"
    ],
    "status": "implemented"
  },
  {
    "id": "goal_debt_state",
    "label": "Typed goal-debt and closure-pressure state",
    "packet_ref": "SRE_2 §8.1",
    "code_refs": [
      "cortex/sre/goal_debt.py",
      "cortex/sre/goals.py",
      "cortex/hosts/claude_code_desktop/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_goals_branching.py",
      "tests/product/test_sre_goal_branch.py",
      "tests/conformance/test_claude_code_desktop_runtime_session_io.py"
    ],
    "status": "implemented"
  },
  {
    "id": "preservation_state",
    "label": "Verified-work preservation and intervention budget",
    "packet_ref": "SRE_2 §6.7 (budget); CORE recovery firewall",
    "code_refs": [
      "cortex/sre/preservation.py",
      "cortex/hosts/claude_code_desktop/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_preservation_state.py",
      "tests/conformance/test_claude_code_desktop_runtime_session_io.py"
    ],
    "status": "implemented"
  },
  {
    "id": "host_reliability_prior",
    "label": "Bounded host/tool reliability prior",
    "packet_ref": "AUX_2 §4 (geometry/eval support); SRE_2 score-pricing",
    "code_refs": [
      "cortex/sre/memory_priors.py",
      "cortex/aux/support_priors.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_support_priors.py",
      "tests/experimental/test_aux_publication.py"
    ],
    "status": "implemented"
  },
  {
    "id": "support_memory_episode",
    "label": "Durable AUX support-memory episode",
    "packet_ref": "AUX_2 §3 offline support memory",
    "code_refs": [
      "cortex/aux/persistence.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_persistence.py"
    ],
    "status": "implemented"
  },
  {
    "id": "auxiliary_support_appendix",
    "label": "AUX runtime augmentation appendix and re-entry",
    "packet_ref": "AUX_2 §5 re-entry / SRE handoff",
    "code_refs": [
      "cortex/aux/augmentation.py",
      "cortex/aux/publication.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_publication.py"
    ],
    "status": "implemented"
  },
  {
    "id": "aux_lift_metric",
    "label": "AUX lift metric and evaluation report",
    "packet_ref": "AUX_2 §4 evaluation-first",
    "code_refs": [
      "cortex/aux/lift.py",
      "cortex/aux/evaluation.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_lift.py"
    ],
    "status": "implemented"
  },
  {
    "id": "aux_burden_report",
    "label": "AUX cost-visible burden report",
    "packet_ref": "AUX_2 §2.7",
    "code_refs": [
      "cortex/aux/cost.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_scaffolds.py"
    ],
    "status": "implemented"
  },
  {
    "id": "verified_work_profile_spec",
    "label": "Verified-work runtime profile specification",
    "packet_ref": "SRE_2 §5 / runtime law",
    "code_refs": [
      "cortex/runtime/verified_work_runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_openai_runtime_session_io.py"
    ],
    "status": "implemented"
  }
]
```


## How To Read The Map

Each row is a load-bearing math object with:

- `id`: stable object id used in closeout law-to-code joins;
- `label`: human-readable concept;
- `packet_ref`: V2 packet source;
- `code_refs`: implementation surfaces;
- `proof_refs`: deterministic proof surfaces;
- `status`: whether the object is implemented, explicitly zeroed, or future-only.

The communication problem should not invent a new mathematical object if an
existing one already owns the state. But it may discover that a missing object
is needed for model-visible integration.

## Eight Cortex Skills Landed In Code

- **Truth-preserving commitments and bounded certification** — status `landed`; code homes: `cortex/core`, `cortex/drivers`; proof surfaces: `tests/product`, `tests/conformance`; math role: Truth maintenance and reality binding.
- **Bounded correction and verified-work preservation** — status `landed`; code homes: `cortex/runtime`, `cortex/sre`, `cortex/hosts/openai`; proof surfaces: `tests/product`; math role: Error repair without losing the main task thread.
- **Uncertainty handling and brake** — status `landed`; code homes: `cortex/sre`; proof surfaces: `tests/product`, `tests/experimental`; math role: Hesitation and uncertainty-aware inhibition.
- **Branch continuity, suspend/resume, and truthful closure** — status `landed`; code homes: `cortex/sre`, `cortex/hosts/openai`; proof surfaces: `tests/product`, `tests/conformance`; math role: Working memory across interruptions plus truthful closure.
- **Intervention pricing versus neutrality** — status `landed`; code homes: `cortex/sre`, `cortex/aux`, `cortex/runtime`; proof surfaces: `tests/product`, `tests/experimental`, `tests/conformance`; math role: Deciding when to intervene, stay neutral, or stop.
- **Blocker surfacing and goal-debt management** — status `landed`; code homes: `cortex/sre`, `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference`; proof surfaces: `tests/product`, `tests/conformance`; math role: Noticing unresolved blockers and unfinished intentions.
- **Multi-host executive continuity** — status `landed`; code homes: `cortex/hosts/openai`, `cortex/hosts/claude`, `cortex/hosts/gemini`, `cortex/hosts/reference`; proof surfaces: `tests/product`, `tests/conformance`; math role: One executive across different brains and contexts.
- **Offline consolidation and support geometry** — status `landed`; code homes: `cortex/aux`; proof surfaces: `tests/experimental`, `tests/archive`, `tests/conformance`; math role: Sleep-like consolidation and support systems.

## Relevant V2 Model-I/O Analysis

The status registry already separates `side_a_internal_logic` from
`side_b_model_visible_translation`. That separation is central to this dossier:
Cortex can be structurally correct internally and still fail to change model
behavior if Side B translation is wrong.

### Lifecycle adapters

This subsection is copied from the status registry to illustrate the
Side A/Side B boundary and lifecycle-adapter vocabulary. It includes
repo-development adapters because they are in the registry, but those adapters
are not the target Claude Code product communication surface. Do not import
mission-reflection mechanics, repo closeout validators, or Codex App workflow
rules into `τ`.

```json
[
  {
    "id": "claude_code",
    "adapter": "Claude Code repo lifecycle adapter",
    "lifecycle_input": "Stop hook reads `transcript_path` JSONL and extracts the latest assistant message.",
    "enforcement": "`.claude/settings.json` runs `.claude/hooks/cortex_grid_stop_hook.py`; block decisions re-prompt Claude until the Cortex Mission Reflection graph validates; fail-open is limited to missing transcript, malformed hook input, or command crash.",
    "proof_refs": [
      ".claude/settings.json",
      ".claude/hooks/cortex_grid_stop_hook.py",
      "tests/internal/test_cortex_grid_stop_hook.py"
    ]
  },
  {
    "id": "codex_app",
    "adapter": "Codex App repo lifecycle adapter",
    "lifecycle_input": "Stop hook receives `last_assistant_message` directly; project-local hooks require trusted `.codex/` config and `[features].codex_hooks = true`.",
    "enforcement": "`.codex/config.toml` runs `.codex/hooks/cortex_mission_reflection_stop_hook.py`; `decision: block` asks Codex App to continue with corrective context; `codex-app-hook-health` proves structural config/script behavior, not live model-side product lift.",
    "proof_refs": [
      ".codex/config.toml",
      ".codex/hooks/cortex_mission_reflection_stop_hook.py",
      "tests/internal/test_codex_app_stop_hook.py"
    ]
  }
]
```


### Side A — Internal executive logic

```json
[
  {
    "id": "event_dispatch_and_commitments",
    "executive_goal": "truth-preserving commitments and bounded certification",
    "state_owned": "event-local envelopes, observation bundles, commitment candidates, provenance manifests, certification firewall assessments, and wake/dispatch decisions",
    "decisions_made": "normalizes raw host events, decides which commitment lane wakes, rejects malformed or provenance-breaking assertions, and projects dispatch/certification warnings",
    "code_refs": [
      "cortex/core/envelopes.py",
      "cortex/core/observation.py",
      "cortex/core/dispatch.py",
      "cortex/core/commitments.py"
    ],
    "proof_refs": [
      "tests/product/test_core_substrate.py",
      "tests/product/test_dispatch.py",
      "tests/product/test_certification_artifacts.py"
    ]
  },
  {
    "id": "goal_branch_continuity",
    "executive_goal": "continuity, focused persistence, and truthful closure",
    "state_owned": "branch registries, active track/goal references, pending goals, confirmed artifacts, goal-debt state, and closure-pressure summaries",
    "decisions_made": "keeps the main task resumable across host events, prices unfinished goal debt, and surfaces closure pressure rather than silently treating incomplete work as done",
    "code_refs": [
      "cortex/sre/goals.py",
      "cortex/sre/goal_branch.py",
      "cortex/sre/goal_debt.py",
      "cortex/hosts/openai/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_goals_branching.py",
      "tests/product/test_sre_goal_branch.py",
      "tests/product/test_openai_runtime_step.py",
      "tests/conformance/integration/test_claude_runtime_continuity.py"
    ]
  },
  {
    "id": "brake_uncertainty_modulators",
    "executive_goal": "uncertainty-aware brake and bounded correction",
    "state_owned": "brake state, brake tonic history, executive signal summaries, modulation memory, risk weights, and policy views",
    "decisions_made": "raises or lowers intervention pressure, damps single-tick flips with tonic hysteresis, and prevents contradiction or repeated failure from being treated as ordinary forward progress",
    "code_refs": [
      "cortex/sre/brake.py",
      "cortex/sre/modulators.py",
      "cortex/sre/executive_summary.py",
      "cortex/sre/policy_view.py"
    ],
    "proof_refs": [
      "tests/product/test_sre_uncertainty_brake.py",
      "tests/product/test_sre_modulators.py",
      "tests/product/test_sre_neutral_hinge.py"
    ]
  },
  {
    "id": "operator_routing_and_capability",
    "executive_goal": "capability-aware routing and intervention pricing versus neutrality",
    "state_owned": "operator task state, route profiles, route budgets, visible burden sensitivity, capability envelopes, mismatch assessment, and blocked reasons",
    "decisions_made": "chooses execute versus inspect/guarded/blocked routes, downshifts continuity-heavy work under capability mismatch, and blocks unsupported model/task envelopes",
    "code_refs": [
      "cortex/sre/operator_routing.py",
      "cortex/runtime/operator_brain_capability.py"
    ],
    "proof_refs": [
      "tests/product/test_operator_routing.py",
      "tests/product/test_brain_capability.py",
      "tests/conformance/test_brain_capability_parity.py"
    ]
  },
  {
    "id": "aux_support_publications",
    "executive_goal": "offline consolidation and support geometry without sovereign AUX claims",
    "state_owned": "durable support-memory episodes, offline publications, host/tool reliability priors, auxiliary appendices, lift reports, and burden reports",
    "decisions_made": "distills removable support evidence that may bias score pricing only through explicit publications; raw AUX episodes remain support-side and cannot directly mutate routing or blockedness",
    "code_refs": [
      "cortex/aux/persistence.py",
      "cortex/aux/publication.py",
      "cortex/aux/support_priors.py",
      "cortex/sre/memory_priors.py"
    ],
    "proof_refs": [
      "tests/experimental/test_aux_persistence.py",
      "tests/experimental/test_aux_publication.py",
      "tests/experimental/test_aux_support_priors.py"
    ]
  },
  {
    "id": "verified_work_preservation",
    "executive_goal": "bounded correction and verified-work preservation",
    "state_owned": "work contracts, contract binding profiles, verified-work instructions, preservation state, repair attempts, verification outcomes, and trusted-structure summaries",
    "decisions_made": "attaches a bounded work contract to model calls, verifies output, preserves trusted structure, and scopes repair attempts instead of rerunning or discarding all work",
    "code_refs": [
      "cortex/runtime/verified_work_runtime.py",
      "cortex/sre/preservation.py",
      "cortex/hosts/openai/host_control.py"
    ],
    "proof_refs": [
      "tests/product/test_verified_work_runtime.py",
      "tests/product/test_preservation_state.py",
      "tests/product/test_openai_host_control.py"
    ]
  },
  {
    "id": "feedback_window_realization",
    "executive_goal": "context adoption, continuity progress, and truthful closure from realized outcomes",
    "state_owned": "reference realization feedback, feedback windows, evidence-progress class, continuity-progress class, recent probe failure class, and just-realized public summaries",
    "decisions_made": "classifies realized model progress, distinguishes stream-only churn from evidence progress, and feeds recent failures back into future routing/brake decisions",
    "code_refs": [
      "cortex/sre/feedback.py",
      "cortex/hosts/_executive_closure.py",
      "cortex/hosts/runtime_context.py",
      "cortex/hosts/openai/host_control.py",
      "cortex/hosts/openai/runtime.py",
      "cortex/hosts/claude_code_desktop/runtime.py",
      "cortex/hosts/claude_code_desktop/hook_control.py",
      "cortex/hosts/reference/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_reference_feedback_window.py",
      "tests/product/test_runtime_context_bridge.py",
      "tests/product/test_runtime_context_eval_rubric.py",
      "tests/product/test_openai_host_control.py",
      "tests/product/test_openai_runtime_step.py",
      "tests/conformance/test_claude_code_desktop_host_control.py",
      "tests/conformance/integration/test_reference_runtime_cli.py"
    ]
  },
  {
    "id": "host_runtime_sessions",
    "executive_goal": "multi-host executive continuity without flattening host differences",
    "state_owned": "host-local runtime sessions for OpenAI, Claude, Gemini, and reference, including branch/goal state, budget/brake history, feedback windows, modulator memory, failure class, next recommended move, and preservation state",
    "decisions_made": "carries Cortex state across events and process boundaries, serializes only accepted control residue, and keeps host-native realization separate from shared law",
    "code_refs": [
      "cortex/hosts/openai/runtime.py",
      "cortex/hosts/claude/runtime.py",
      "cortex/hosts/claude_code_desktop/runtime.py",
      "cortex/hosts/gemini/runtime.py",
      "cortex/hosts/reference/runtime.py"
    ],
    "proof_refs": [
      "tests/product/test_openai_runtime_session_io.py",
      "tests/conformance/test_claude_runtime_session_io.py",
      "tests/conformance/test_claude_code_desktop_runtime_session_io.py",
      "tests/conformance/test_gemini_runtime_session_io.py",
      "tests/conformance/test_reference_runtime_session_io.py"
    ]
  },
  {
    "id": "host_control_transports",
    "executive_goal": "model I/O boundary where Cortex can actually wrap a model",
    "state_owned": "strict host-control request objects, text/system/instructions fields, optional offline publications, audit intensity, and transport results",
    "decisions_made": "coerces host-control requests, rejects out-of-scope keys, sends only host-legal request bodies, and updates session state from transport outputs",
    "code_refs": [
      "cortex/hosts/openai/host_control.py",
      "cortex/hosts/openai/host_transport.py",
      "cortex/hosts/claude/host_control.py",
      "cortex/hosts/claude/host_transport.py",
      "cortex/hosts/claude_code_desktop/hook_control.py",
      "cortex/hosts/gemini/host_control.py",
      "cortex/hosts/gemini/host_transport.py"
    ],
    "proof_refs": [
      "tests/product/test_openai_host_control.py",
      "tests/conformance/test_claude_host_control.py",
      "tests/conformance/test_claude_code_desktop_host_control.py",
      "tests/conformance/test_gemini_host_control.py",
      "tests/conformance/integration/test_openai_host_control_service.py"
    ]
  }
]
```


### Side B — Model-visible translation

```json
[
  {
    "id": "event_dispatch_and_commitments",
    "visibility_class": "decision_visible",
    "model_io_path": "`cortex/core/*` → host runtime step → CLI/service records and closure/route decisions; direct prompt text only when downstream host-control uses the decision",
    "reaches_model_as": "runtime decision state, warnings, and certification gates; not automatically prompt-visible by itself",
    "behavior_effect": "can block, route, warn, or require closure before a model call proceeds through host control",
    "gap_or_unearned": "Do not claim commitment diagnostics alone change model behavior unless a host-control path consumes them."
  },
  {
    "id": "goal_branch_continuity",
    "visibility_class": "decision_visible",
    "model_io_path": "`cortex/sre/goals.py` + host runtime session → `operator_route.route_budget.allow_resume` / closure summaries → subsequent host-control selection",
    "reaches_model_as": "route and budget constraints, session continuity state, and closure pressure; not as raw memory text by default",
    "behavior_effect": "keeps resume/closure decisions stable across events and can alter whether the next call is inspect, continuity, or blocked",
    "gap_or_unearned": "Raw branch registry is not model-visible unless converted into host-control input or route behavior."
  },
  {
    "id": "brake_uncertainty_modulators",
    "visibility_class": "decision_visible",
    "model_io_path": "`cortex/sre/brake.py` / `modulators.py` → executive policy view → operator route / activation thresholds → host runtime result",
    "reaches_model_as": "route pressure, threshold shifts, blocked/guarded decisions, and diagnostics; not natural-language self-talk",
    "behavior_effect": "slows or blocks under contradiction and repeated failure, reducing unsupported forward motion before model output is requested",
    "gap_or_unearned": "This is runtime control, not post-training reasoning improvement; live output-lift still requires model-run evidence."
  },
  {
    "id": "operator_routing_and_capability",
    "visibility_class": "decision_visible",
    "model_io_path": "`select_operator_route*` → host runtime `operator_route_payload` → host-control route profile / verified-work contract binding",
    "reaches_model_as": "DEGRADE/UNSUPPORTED routing, max retry suppression, lean contract binding, or blocked request",
    "behavior_effect": "changes whether and how the model is asked to act when model/task capability mismatch is detected",
    "gap_or_unearned": "Static OpenAI-only band registry remains a cold-start prior; observed capability inference is queued, not landed."
  },
  {
    "id": "aux_support_publications",
    "visibility_class": "support_only",
    "model_io_path": "AUX episode stores → `OfflineSupportPublication` → explicit publication supplied to host-control/runtime scoring",
    "reaches_model_as": "score-pricing priors and publication-only support; raw SQLite episodes do not reach the model",
    "behavior_effect": "can bias control pricing when explicitly published, host-matched, and fresh; cannot directly route or certify",
    "gap_or_unearned": "Default shipping/conformance lanes keep live `Q_mem = 0`; no default-on memory claim is earned."
  },
  {
    "id": "verified_work_preservation",
    "visibility_class": "direct_model_visible",
    "model_io_path": "`OpenAIHostControlRequest(work_contract=...)` → fixed verified-work `instructions` + `input_text` → `execute_openai_response_stream_turn`",
    "reaches_model_as": "explicit model instructions, workspace context, repair prompt, and response verification loop on the OpenAI host-control lane",
    "behavior_effect": "changes model call content and bounded repair behavior directly; preserves trusted structure across one-shot and repair attempts",
    "gap_or_unearned": "Strongest direct path is OpenAI shipping lane; Claude/Gemini parity is conformance-shaped and must not be overclaimed as default shipping."
  },
  {
    "id": "feedback_window_realization",
    "visibility_class": "conditional_model_visible_openai_and_claude_code_desktop_structural",
    "model_io_path": "host output / last `ReferenceRealizationFeedback` → `runtime_context_from_last_feedback(...)` → OpenAI host-control `instructions` or verified-work `input_text`; Claude Code Desktop structural path maps prior feedback through `cortex/hosts/claude_code_desktop/runtime.py` to `hookSpecificOutput.additionalContext` for `PreToolUse:Bash`",
    "reaches_model_as": "a single task-local runtime-context constraint sentence derived only from the immediately prior feedback entry; clean or absent feedback emits no block/context",
    "behavior_effect": "shapes the next OpenAI call and, structurally, the next Claude Code Desktop Bash-tool assistant continuation away from premature closure after stream-only, failed-probe, warning, override, or braked realization without accumulating memory across turns; generic friction now stays silent and relies on route/brake gates",
    "gap_or_unearned": "OpenAI remains the direct shipping lane; Claude Code Desktop is structurally wired for `PreToolUse:Bash` only and still needs live paired output-quality evidence before shipping-lift claims."
  },
  {
    "id": "host_runtime_sessions",
    "visibility_class": "state_to_decision_visible",
    "model_io_path": "host session artifact → runtime step → route/closure/policy payload → host control request, CLI/service response, or Claude Code Desktop hook-control output",
    "reaches_model_as": "carried state that influences later route and closure behavior; raw session JSON is not model input",
    "behavior_effect": "maintains continuity across events and hosts without pretending all hosts expose the same transport affordances",
    "gap_or_unearned": "Session state can be perfectly coherent internally while still failing to affect a model if no host-control path consumes it."
  },
  {
    "id": "host_control_transports",
    "visibility_class": "direct_model_visible",
    "model_io_path": "`OpenAIHostControlRequest.input_text/instructions`, `ClaudeHostControlRequest.input_text/system`, `GeminiHostControlRequest.input_text/instructions`, and Claude Code Desktop `hookSpecificOutput.additionalContext` → respective live/fixture transport or hook outputs",
    "reaches_model_as": "provider request text/system/instructions or Claude Code Desktop hook additional context; metadata and audit intensity are boundary/control fields, not assumed model-visible text",
    "behavior_effect": "this is the main bridge where Cortex can change what the model receives or what output is accepted",
    "gap_or_unearned": "Any internal logic not consumed here, or not converted into route/block behavior before here, remains monitoring/scaffolding rather than product Cortex."
  }
]
```


### Synthesis — gap / boundary decisions

```json
[
  {
    "id": "event_dispatch_and_commitments",
    "boundary_judgment": "product Cortex when consumed by host runtime/host-control gates; monitor-only if left as CLI diagnostics",
    "decision": "bridge",
    "next_action": "Keep commitment state as binding runtime law and require future commitment seams to name the host-control or route effect in closeout connectivity traces.",
    "post_training_boundary": "Do not try to retrain general truthfulness at runtime; Cortex should enforce event-local commitment handling and certification boundaries."
  },
  {
    "id": "goal_branch_continuity",
    "boundary_judgment": "product Cortex when it changes resume/closure/route behavior; internal-only when it only serializes branch metadata",
    "decision": "bridge",
    "next_action": "Audit future continuity seams against model-visible resume or closure behavior, not just preserved branch state.",
    "post_training_boundary": "General long-context memory quality is post-training; task-local lifecycle continuity after interruption is Cortex runtime territory."
  },
  {
    "id": "brake_uncertainty_modulators",
    "boundary_judgment": "product Cortex as bounded runtime brake/route control, not a replacement for model calibration",
    "decision": "keep_runtime",
    "next_action": "Keep proving that brake pressure changes route/block decisions and do not claim improved reasoning calibration without live evidence.",
    "post_training_boundary": "Global confidence calibration belongs in post-training; per-turn contradiction and failure brakes belong in lifecycle-first runtime."
  },
  {
    "id": "operator_routing_and_capability",
    "boundary_judgment": "product Cortex because it changes route budgets and blockedness before the model call",
    "decision": "return_to_product_train",
    "next_action": "Next product work should land observed capability inference so routing no longer depends only on static model-name prior.",
    "post_training_boundary": "Improving a model's inherent capability is post-training; detecting and routing around observed capability limits is Cortex."
  },
  {
    "id": "aux_support_publications",
    "boundary_judgment": "support-side product adjunct only when publication-shaped; raw memory stores are not product Cortex",
    "decision": "keep_publication_only",
    "next_action": "Keep AUX removable and publication-only; move any raw episode or default-on memory path back to lab/experimental or cut it.",
    "post_training_boundary": "Broad factual memory and preference learning are post-training/product-memory territory; explicit removable support priors are Cortex support geometry."
  },
  {
    "id": "verified_work_preservation",
    "boundary_judgment": "product Cortex on OpenAI host-control lane because it directly changes instructions and repair loops",
    "decision": "keep_and_prove_live",
    "next_action": "Keep the OpenAI direct path as shipping truth; only graduate cross-host lift claims after equivalent host-control proof exists.",
    "post_training_boundary": "Teaching a model to always preserve work is post-training; wrapping a concrete work contract and verifying repairs is Cortex runtime."
  },
  {
    "id": "feedback_window_realization",
    "boundary_judgment": "product Cortex on the OpenAI host-control lane when last-step feedback is translated into bounded model-visible runtime context; structurally product-shaped on Claude Code Desktop `PreToolUse:Bash` when the same bounded context reaches hook additionalContext; still monitor-only if retained only as a public summary",
    "decision": "bridge_landed_openai_structural_claude_code_desktop_pretool_structural",
    "next_action": "Keep the bridge last-feedback-only, extend Claude Code Desktop hook coverage one lifecycle event at a time, and run paired live baseline-vs-shaped evaluations before claiming output lift.",
    "post_training_boundary": "General learning from feedback is post-training; event-local realization feedback that alters the next runtime decision is Cortex."
  },
  {
    "id": "host_runtime_sessions",
    "boundary_judgment": "necessary product substrate, but only earned when state is consumed by runtime decisions",
    "decision": "audit_consumption",
    "next_action": "When adding session fields, add tests showing they survive serialization and change a route/closure/model-I/O decision, or mark them diagnostics.",
    "post_training_boundary": "Persistent personality or broad memory is post-training/product memory; host-local executive state for a task lifecycle is Cortex."
  },
  {
    "id": "host_control_transports",
    "boundary_judgment": "the decisive product boundary where Cortex either reaches the model or does not",
    "decision": "protect_boundary",
    "next_action": "Treat any future product claim as unearned until it names the exact request field or route/block consequence at this boundary.",
    "post_training_boundary": "Generic instruction-following lessons are post-training territory; encode only lifecycle-first control and verification signals that current host calls need."
  }
]
```


## Communication Implication

The function `τ` is a Side B problem constrained by Side A. It must consume real
Cortex objects such as `goal_debt_state`, `executive_modulator_state`,
`operator_brain_capability_envelope`, `support_memory_episode`, and
`verified_work_profile_spec`, but it must not expose those object names merely
because they are mathematically meaningful inside Cortex.
