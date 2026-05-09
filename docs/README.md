# Cortex Docs

Surface: product

This directory index is product-first and single-truth-first.

Document roles are machine-readable in `internal/truth/cortex_status.json`.
The generated status view explains which docs are authority, retained
context, planning scoreboard, workflow law, support context, or recon
evidence; retained context is not current roadmap authority.

Active docs:
- [CORTEX](CORTEX.md) — canonical narrative authority
- [Cortex Executive Runtime Tracker](CORTEX_EXECUTIVE_RUNTIME_TRACKER.md) —
  product planning tracker for live-model executive-function achievement
- [Cortex Executive Runtime Program Spec](CORTEX_EXECUTIVE_RUNTIME_PROGRAM_SPEC.md) —
  control-object, metric, and falsification spec for the first runtime program
- [Cortex Executive Runtime Phase 5 Readiness](CORTEX_EXECUTIVE_RUNTIME_PHASE_5_READINESS.md) —
  evidence-accounting gate before the OpenAI silent-control live probe
- [Current Status](CORTEX_STATUS.md)
- [CORTEX Core](CORTEX_V2_CORE_2.md)
- [CORTEX SRE](CORTEX_V2_SRE_2.md)
- [CORTEX AUX](CORTEX_V2_AUX_2.md)
- [Repo Workflow](internal/REPO_WORKFLOW.md)
- [Mission Reflection Contract](internal/MISSION_REFLECTION_CONTRACT.md)
- [Anti-Drift Rules](internal/ANTI_DRIFT_RULES.md)
- [Claude Code Desktop Cortex Plugin Design](cortex_plugin/DESIGN.md) —
  v1 full-lifecycle plugin architecture for Claude Code Desktop's Code tab
- [Claude Code Desktop Cortex Host Adapter](cortex_plugin/ADAPTER.md) —
  structural host-adapter pattern for the plugin build
- [Claude Code Desktop Plugin Evidence Synthesis](cortex_plugin/EVIDENCE_SYNTHESIS.md) —
  accounting of what Claude Code Desktop hook evidence has and has not earned
- [Cortex Communication Problem Dossier](cortex_plugin/communication_problem/01_problem_statement.md) —
  research dossier framing the strange-loop communication problem and the
  search for a general model-facing translation function
- Runtime context bridge eval artifacts:
  [rubric](runtime_context/EVAL_RUBRIC.md),
  [baseline-vs-shaped examples](runtime_context/BASELINE_SHAPED_EXAMPLES.md),
  [cross-host sketch](runtime_context/CROSS_HOST_SKETCH.md)
- [Lifecycle-first Surface Matrix Recon](recon/lifecycle_first_surface_matrix.md) —
  current host/API/CLI/app extension-surface map
- [Codex App Hook Probe](recon/codex_app_hook_probe.md) —
  empirical project Stop-hook load/fire/block evidence
- [Claude Code Desktop PreToolUse Probe](recon/claude_code_desktop_pretooluse_probe.md) —
  empirical Code-tab PreToolUse fire/additionalContext evidence
- [Claude Code User-Scope Plugin PreToolUse Probe](recon/claude_code_user_scope_plugin_pretooluse_probe.md) —
  empirical user-scope plugin PreToolUse/Stop coexistence evidence
- [Claude Code User-Scope Plugin Managed-Worktree Probe](recon/claude_code_user_scope_plugin_managed_worktree_probe.md) —
  empirical sandbox Code-tab cwd evidence for user-scope plugin hooks
- [Claude Code Cortex Runtime-Context Connectivity Probe](recon/claude_code_cortex_runtime_context_connectivity_probe.md) —
  empirical paired baseline-vs-shaped evidence for the merged runtime-context bridge
- [Claude Code Cortex Stop Closure Connectivity Probe](recon/claude_code_cortex_stop_closure_connectivity_probe.md) —
  empirical paired baseline-vs-shaped evidence for Cortex closure pressure through Stop block reasons
- [Claude Code Cortex Headless CLI Equivalence Probe](recon/claude_code_cortex_headless_cli_equivalence_probe.md) —
  empirical partial-equivalence evidence for Stop closure pressure through `claude -p`
- [Claude Code Cortex Bridge Translation Headless Probe](recon/claude_code_cortex_bridge_translation_headless_probe.md) —
  preserved headless evidence for translated Stop closure-pressure behavior and setup constraints
- [Claude Code Cortex Mac Pending-Goal Divergence Retest](recon/claude_code_cortex_mac_pending_goal_divergence_retest.md) —
  empirical Mac-app evidence that raw internal Stop wording is content-shape contaminated for pending-goal closure
- [Claude Code Cortex PostToolUseFailure To Stop Loop Probe](recon/claude_code_cortex_posttool_failure_to_stop_loop_probe.md) —
  empirical mixed evidence for failed-tool feedback persistence into Stop closure pressure
- [Claude Code Cortex UserPromptSubmit Verified-Work Probe](recon/claude_code_cortex_userpromptsubmit_verified_work_probe.md) —
  empirical baseline-vs-shaped evidence for prompt-boundary verified-work contracts
- [Cortex OpenAI Operator Silent-Control Live Probe](recon/cortex_openai_operator_silent_control_live_probe.md) —
  Gate 0 evidence that runtime debt control is structural but not yet enacted
  by the Codex operator live adapter
- [Cortex OpenAI Operator Debt-Control Enactment](recon/cortex_openai_operator_debt_control_enactment.md) —
  Gate 0 remediation evidence that the OpenAI host adapter now enacts SRE
  debt-control decisions before the Codex CLI runner
- [Cortex OpenAI Operator Silent-Control Live Probe Retry](recon/cortex_openai_operator_silent_control_live_probe_retry.md) —
  live OpenAI operator retry evidence: Gate 0 passed, but the accepted baseline
  gate did not reproduce the target failures, so shaped trials did not run
- [Cortex OpenAI Operator Output-Quality Fixture Refresh](recon/cortex_openai_operator_output_quality_fixture_refresh.md) —
  live OpenAI operator fixture-refresh evidence: isolated output-quality
  workspaces and `astro_docs_site_v1` reproduces the hidden-verifier failure
  shape needed before another silent-control retry
- [Cortex OpenAI Operator Verification-Debt Continuation](recon/cortex_openai_operator_verification_debt_continuation.md) —
  structural Gate 0 evidence that OpenAI operator silent control can enact a
  general same-thread verification continuation for visible-success / unpaid
  verification-debt states without fixture-specific product law
- [Cortex OpenAI Operator Visible-Intervention Live Probe](recon/cortex_openai_operator_visible_intervention_live_probe.md) —
  live OpenAI operator evidence that product-rendered grounded visible
  intervention can improve closure, evidence recovery, and continuity over
  silent-only control on a reproduced output-quality failure family
- [Cortex Visible-Intervention Product-Perception Hardening](recon/cortex_visible_intervention_product_perception_hardening.md) —
  structural evidence that grounded visible intervention now requires a due
  product-runtime expectation anchor before model-visible verification speech
- [Cortex OpenAI Operator Visible-Intervention Hardened Rerun](recon/cortex_openai_operator_visible_intervention_hardened_rerun.md) —
  live OpenAI operator evidence that the hardened visible-intervention path
  remains product-grounded but current overdue-verification wording fails the
  paired success criteria
- [Cortex Codex App/CLI Hook-Native Stop Activation Probe](recon/cortex_codex_app_cli_hook_native_stop_activation_probe.md) —
  structural Gate 0 evidence that the product Stop hook client maps grounded
  identity-continuous text to Codex block JSON without reusing repo workflow
  guardrails or claiming live behavior lift
- [Cortex Codex App/CLI Hook-Native Stop Live Canary](recon/cortex_codex_app_cli_hook_native_stop_live_canary.md) —
  live actuator evidence that the product Stop hook client receives a real
  Codex Stop payload and returns exact Cortex block JSON, without claiming
  product perception or behavior lift
- [Cortex Codex App/CLI Product Perception Loop](recon/cortex_codex_app_cli_product_perception_loop.md) —
  structural evidence that Codex App/CLI prompt, tool, failure, and Stop
  lifecycle payloads can derive grounded Stop intervention state without a
  runtime snapshot fixture
- [Cortex Codex App/CLI Product Perception Live Probe](recon/cortex_codex_app_cli_product_perception_live_probe.md) —
  live scoped-negative evidence that project-local Codex CLI hooks loaded but
  exposed only Stop payloads, leaving no product task or tool events for
  no-snapshot Stop perception
- [Cortex Codex App/CLI Product Event-Capture Remediation](recon/cortex_codex_app_cli_product_event_capture_remediation.md) —
  live Codex CLI evidence that a full-lifecycle subject hook config captures
  UserPromptSubmit, PreToolUse, PostToolUse, and Stop payloads before Stop
  without runtime snapshots or parent repo workflow guardrails
- [Cortex Codex App/CLI Stop Continuation Resolution Loop](recon/cortex_codex_app_cli_stop_continuation_resolution_loop.md) —
  live Codex CLI evidence that a post-block continuation check can resolve
  the exact active verification expectation from product-visible hook events
- [Cortex Codex App/CLI Hook-Native Behavior Comparison](recon/cortex_codex_app_cli_hook_native_behavior_comparison.md) —
  structural Gate 0 evidence for a paired silent-only versus hook-native
  behavior comparison harness; live behavior lift remains unearned
- [Cortex Codex App/CLI Astro Three-Arm Fixture Refresh](recon/cortex_codex_app_cli_astro_three_arm_fixture_refresh.md) —
  live three-arm evidence that the Astro hidden verifier is now hidden from
  subject workspaces, while raw, silent, and full Cortex arms produced mixed
  output-quality results with no Cortex speech lift
- [Cortex Codex App/CLI Value Ablation Audit](recon/cortex_codex_app_cli_value_ablation_audit.md) —
  offline audit evidence that the Astro failure is not threshold-caused and
  next needs product-visible claim/evidence perception rather than fixture or
  text remediation
- [Cortex Codex App/CLI Task Standard Spine](recon/cortex_codex_app_cli_task_standard_spine.md) —
  structural product evidence for task-standard formation/tracking, with the
  gated UserPromptSubmit text still requiring final signoff and live behavior
  lift unearned
- [Cortex Task-Standard SRE Correspondence Reconciliation](recon/cortex_task_standard_sre_correspondence_reconciliation.md) —
  doctrine correspondence evidence that `TaskStandardSpine` is host-agnostic
  SRE law, while Codex App/CLI remains only the current product realization
- [Cortex Task-Standard Executive Doctrine Math Refinement](recon/cortex_task_standard_executive_doctrine_math_refinement.md) —
  doctrine/math evidence that task-standard formation is the task-set front
  half of Cortex's runtime executive loop before live activation
- [Cortex Codex App/CLI Task-Standard Live Probe](recon/cortex_codex_app_cli_task_standard_live_probe.md) —
  structural Gate 0 evidence for signed-off task-standard context delivery and
  standard capture before an explicitly approved live run
- [Cortex Codex App/CLI Task-Standard Live Run](recon/cortex_codex_app_cli_task_standard_live_run.md) —
  live Codex CLI evidence that the signed text was emitted through a flat
  Cortex-internal context payload, but no prework task-standard block was
  captured
- [Cortex Codex App/CLI Hook Contract Capture Boundary Remediation](recon/cortex_codex_app_cli_hook_contract_capture_boundary_remediation.md) —
  structural evidence that UserPromptSubmit task-standard context now uses
  Codex-native `hookSpecificOutput.additionalContext`, with Stop blocks isolated
  for the next live capture rerun
- [Cortex Codex App/CLI Task-Standard Context Live Rerun](recon/cortex_codex_app_cli_task_standard_context_live_rerun.md) —
  live evidence that Codex-native task-standard context reached the model and
  produced a pre-tool standard block, but Cortex did not capture it into
  `TaskStandardSpine` from hook-visible state
- [Cortex Codex App/CLI Communication Boundary Audit And Hardening](recon/cortex_codex_app_cli_communication_boundary_audit_and_hardening.md) —
  structural audit evidence that recent Codex App/CLI trickle failures are
  proof-boundary failures across host contract, lifecycle config, temporal
  capture, Gate 0/live mismatch, and workflow-health coupling, not SRE doctrine
  failure
- [Cortex Codex App/CLI Task-Standard PreTool Transcript Capture](recon/cortex_codex_app_cli_task_standard_pretool_transcript_capture.md) —
  structural and replay evidence that assistant-authored pre-tool standard
  blocks from Codex transcripts now populate `TaskStandardSpine` before tool
  evidence is scored
- [Cortex Codex App/CLI Task-Standard Live Capture Rerun](recon/cortex_codex_app_cli_task_standard_live_capture_rerun.md) —
  live Codex CLI evidence that signed task-standard context reaches the model,
  the model writes a pre-tool standard block, and Cortex captures it into
  `TaskStandardSpine` before tool evidence scoring
- [Cortex Codex App/CLI Task-Standard Stop-Gating Calibration Probe](recon/cortex_codex_app_cli_task_standard_stop_gating_calibration_probe.md) —
  structural calibration evidence that captured task standards can block
  premature Stop closure while clean readback evidence stays silent, with the
  latest live capture replay no longer overblocking
- [Cortex Codex App/CLI Task-Standard Stop-Gating Live Run](recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md) —
  live Codex CLI evidence that captured task standards can drive an existing
  Stop block, the model can run stronger aligned continuation checks, and final
  Stop can resolve silently without claiming behavior lift
- [Cortex Codex App/CLI Task-Standard Behavior Comparison Harness](recon/cortex_codex_app_cli_task_standard_behavior_comparison_harness.md) —
  structural Gate 0 evidence for the pinned raw, silent task-standard, and
  active task-standard behavior-comparison harness, without live behavior-lift
  claims
- [Cortex Codex App/CLI Task-Standard Behavior Comparison Live Run](recon/cortex_codex_app_cli_task_standard_behavior_comparison_live_run.md) —
  live three-arm evidence that active task-standard Stop gating overblocked
  clean controls and did not earn behavior lift over silent perception
- [Cortex Codex App/CLI Task-Standard Evidence-Gating Remediation](recon/cortex_codex_app_cli_task_standard_evidence_gating_remediation.md) —
  structural remediation evidence that Stop verification-fit can consume
  captured `TaskStandardSpine` satisfaction directly while preserving gap blocks
- [Cortex Codex App/CLI Task-Standard Pre-Live Audit Roadmap Update](recon/cortex_codex_app_cli_task_standard_pre_live_audit_roadmap_update.md) —
  roadmap evidence that another live comparison is blocked until an offline
  readiness gate proves clean-control safety and actuator opportunity
- [Cortex Codex App/CLI Task-Standard Offline Replay Readiness Gate](recon/cortex_codex_app_cli_task_standard_offline_replay_readiness_gate.md) —
  no-spend proof that scored lexical matching, clean-control replay, mismatch
  blockability, and artifact fidelity are ready before another live run
- [Cortex Codex App/CLI Task-Standard Raw-vs-Silent Artifact Readout](recon/cortex_codex_app_cli_task_standard_raw_vs_silent_artifact_readout.md) —
  no-spend readout showing a narrow silent-over-raw signal on
  `task_standard_exactness` evidence recovery, not broad Cortex lift
- [Cortex Codex App/CLI Lifecycle Actuator Map Roadmap Update](recon/cortex_codex_app_cli_lifecycle_actuator_map_roadmap_update.md) —
  roadmap update pausing live tests and Sinkhorn until the Codex lifecycle
  actuator map is explicit
- [Cortex Codex App/CLI Lifecycle Actuator Map](recon/cortex_codex_app_cli_lifecycle_actuator_map.md) —
  doctrine/status map of SessionStart, UserPromptSubmit, PreToolUse,
  PermissionRequest, PostToolUse, and Stop by actual model-control surface
- [Cortex Codex App/CLI PostToolUse Task-Standard Next-Step Correction](recon/cortex_codex_app_cli_posttooluse_task_standard_next_step_correction.md) —
  structural Gate 0 evidence that PostToolUse can attach a specific
  task-standard next-step context after product-visible mismatch
- [Cortex Codex App/CLI PostToolUse Task-Standard Calibration Decision](recon/cortex_codex_app_cli_posttooluse_task_standard_calibration_decision.md) —
  no-spend decision queuing a narrow live PostToolUse actuator probe, not a
  three-arm behavior comparison
- [Cortex Codex App/CLI Raw-vs-Silent Artifact Readout Roadmap Update](recon/cortex_codex_app_cli_raw_vs_silent_artifact_readout_roadmap_update.md) —
  roadmap update queuing the raw-vs-silent artifact readout before implementing
  PostToolUse or PreToolUse actuators
- [Cortex Codex App/CLI Task-Standard Stack Publication Hygiene](recon/cortex_codex_app_cli_task_standard_stack_publication_hygiene.md) —
  workflow/product-proof hygiene record keeping the narrow PostToolUse live
  probe queued but unapproved until the task-standard stack is cleanly landed
- [Cortex Codex App/CLI PostToolUse Task-Standard Narrow Live Probe](recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_probe.md) —
  approval-gated live probe harness for narrow PostToolUse exactness evidence,
  not a live run or broad behavior-lift claim
- [Cortex Codex App/CLI PostToolUse Task-Standard Narrow Live Run](recon/cortex_codex_app_cli_posttooluse_task_standard_narrow_live_run.md) —
  live negative evidence that PostToolUse context was delivered without
  earning immediate next-action repair, queuing an architecture decision
- [Cortex Codex App/CLI PostToolUse Task-Standard Actuator Architecture Decision](recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_architecture_decision.md) —
  decision classifying the negative live result as PostToolUse timing/selection
  failure and queuing no-live phase-aware calibration
- [Cortex Codex App/CLI PostToolUse Task-Standard Phase-Aware Calibration Gate 0](recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_calibration_gate0.md) —
  no-live structural proof that PostToolUse context waits for candidate
  artifact creation and keeps pre-artifact/control cases silent
- [Cortex Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Run](recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_run.md) —
  live negative evidence that the phase-aware actuator did not emit
  PostToolUse context after candidate artifact work, queuing firing-boundary
  remediation
- [Cortex Codex App/CLI PostToolUse Task-Standard Firing-Boundary Remediation](recon/cortex_codex_app_cli_posttooluse_task_standard_firing_boundary_remediation.md) —
  no-live proof that live-equivalent candidate artifact and readback payloads
  without exit/status markers can fire phase-aware PostToolUse context while
  pre-artifact and control cases stay silent
- [Cortex Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun](recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun.md) —
  live negative evidence that the remediated phase-aware actuator now emits in
  the mismatch case but overcontrols a clean-evidenced control, queuing no-live
  overcontrol remediation
- [Cortex Codex App/CLI PostToolUse Task-Standard Overcontrol Remediation](recon/cortex_codex_app_cli_posttooluse_task_standard_overcontrol_remediation.md) —
  no-live proof that live-equivalent failed verification/readback diagnostics
  stay silent while mismatch candidate/readback PostToolUse contexts still fire
- [Cortex Codex App/CLI PostToolUse Actuator Boundary and Trace Repair](recon/cortex_codex_app_cli_posttooluse_task_standard_actuator_trace_repair.md) —
  structural proof that the PostToolUse task-standard actuator decision has a
  host-owned module and the live harness reads next action from hook chronology
- [Cortex Codex App/CLI PostToolUse Causal Trace IDs](recon/cortex_codex_app_cli_posttooluse_causal_trace_ids.md) —
  structural proof that PostToolUse live readout joins context rows to stdout
  commands by stable tool-event reference and marks missing historical joins
  ambiguous instead of inferring by ordinal position
- [Cortex Codex App/CLI PostToolUse Shared Tool-Evidence Classification](recon/cortex_codex_app_cli_posttooluse_shared_tool_evidence_classification.md) —
  no-live proof that SRE task-standard evidence and the Codex PostToolUse
  actuator consume one typed classifier for missing, failed, candidate,
  readback, markerless, and completion phases before the next live rerun
- [Cortex Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun After Shared Tool Evidence](recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun_after_shared_tool_evidence.md) —
  live negative evidence that the shared-classifier rerun failed on repeated
  PostToolUse context and ambiguous hook/stdout event-ref joining, queuing
  no-live context-loop and trace remediation
- [Cortex Codex App/CLI PostToolUse Task-Standard Context-Loop Trace Remediation](recon/cortex_codex_app_cli_posttooluse_task_standard_context_loop_trace_remediation.md) —
  no-live proof that PostToolUse task-standard context opens one active repair
  lease and future trace joins use exact refs or unique diagnostic fingerprints
  without ordinal fallback
- [Cortex Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun After Context-Loop Trace Remediation](recon/cortex_codex_app_cli_posttooluse_task_standard_phase_aware_narrow_live_rerun_after_context_loop_trace_remediation.md) —
  live negative evidence that context delivery, unique-fingerprint trace
  joining, and next-tool direct checking worked, but final closure did not
  report the context evidence
- [Cortex Codex App/CLI PostToolUse Task-Standard Closure-Reporting Architecture Decision](recon/cortex_codex_app_cli_posttooluse_task_standard_closure_reporting_architecture_decision.md) —
  architecture decision that classifies the latest closure-reporting failure
  as lab final-closure readout underfit and queues no-live readout remediation
- [Cortex Codex App/CLI PostToolUse Strategy Failure Audit](recon/cortex_codex_app_cli_posttooluse_strategy_failure_audit.md) —
  strategic audit of the five PostToolUse live failures, queuing a no-live
  measurement-stack rebuild before another live rerun or value probe
- [Cortex Codex App/CLI PostToolUse Task-Standard Measurement-Stack Rebuild Gate 0](recon/cortex_codex_app_cli_posttooluse_task_standard_measurement_stack_rebuild_gate0.md) —
  no-live measurement table replaying all five PostToolUse live artifacts and
  preserving historical failures while isolating final-closure metric underfit
- [Cortex Codex App/CLI PostToolUse Task-Standard Final-Closure Readout Remediation Gate 0](recon/cortex_codex_app_cli_posttooluse_task_standard_final_closure_readout_remediation_gate0.md) —
  no-live readout remediation proving semantic exactness closure evidence
  makes only the latest PostToolUse live artifact pass while preserving the
  earlier historical failure classes
- [Cortex Codex App/CLI PostToolUse Task-Standard Exactness-Only Paired Value Probe Gate 0](recon/cortex_codex_app_cli_posttooluse_task_standard_exactness_only_paired_value_probe_gate0.md) —
  no-live paired-value design gate registering active/silent exactness arms,
  4/5 active-beats-silent threshold, dominance failures, and future live
  approval without claiming value lift
- [Cortex Codex App/CLI PostToolUse Task-Standard Exactness-Only Paired Value Live Probe](recon/cortex_codex_app_cli_posttooluse_task_standard_exactness_only_paired_value_live_probe.md) —
  approval-gated paired live probe producing `failure_no_value`: active
  PostToolUse context beat silent in 0/5 exactness mismatch pairs
- [Cortex Effectiveness Strategy Reset](recon/cortex_effectiveness_strategy_reset.md) —
  no-live regroup that freezes the PostToolUse-only value path and queues a
  Cortex-level effectiveness evaluator Gate 0
- [Cortex Executive Effectiveness Evaluator Gate 0](recon/cortex_executive_effectiveness_evaluator_gate0.md) —
  no-live design gate defining the hard objective, four evaluator arms,
  mandatory simple-hook challenger, dominance gates, and contraction
  obligations before any more actuator work
- [Cortex Executive Effectiveness Evaluator Build](recon/cortex_executive_effectiveness_evaluator_build.md) —
  no-live evaluator build emitting the episode table, leaderboard, summary,
  historical PostToolUse no-value replay, and stricter overnight runner
  execution contract before any live matrix or candidate mutation
- [Cortex Automation Product-Boundary Contract](recon/cortex_automation_product_boundary_contract.md) —
  no-live hardening seam that keeps overnight automation and evaluator work as
  proof/support surfaces unless a row declares a product spine, non-lab
  model-I/O path, and current-truth authorization
- [Cortex Executive Effectiveness Evaluator Live Gate 1](recon/cortex_executive_effectiveness_evaluator_live_gate1.md) —
  no-live live-interface gate registering the future four-arm evaluator matrix,
  approval refusal, dry-run schedule, and next simple-hook dependency
- [Cortex Simple-Hook Baseline Challenger](recon/cortex_simple_hook_baseline_challenger.md) —
  no-live independent small baseline for the four-arm evaluator: under 500 LOC,
  no `cortex/**` imports, visible-task capture, one reminder/context path, and
  one closure check
- [Cortex Executive Effectiveness Evaluator Live Matrix Run](recon/cortex_executive_effectiveness_evaluator_live_matrix_run.md) —
  approval-gated 60-row four-arm evaluator run producing
  `failure_silent_perception_contamination`: active Cortex did not beat the
  simple-hook baseline, and the only discriminating continuity repeat was
  matched by silent Cortex
- [Cortex Effectiveness Measurement-Stack Rebuild Gate 0](recon/cortex_effectiveness_measurement_stack_rebuild_gate0.md) —
  no-live diagnosis of the first four-arm evaluator matrix, preserving
  `failure_silent_perception_contamination`, naming baseline-parity and
  silent-contamination causes, and queueing the v2 case registry
- [Cortex Overnight Evaluator Automation Hardening](recon/cortex_overnight_evaluator_automation_hardening.md) —
  internal guardrail seam adding a local overnight runner contract, digest,
  bloat metrics, safe auto-merge boundaries, and evaluator-only automation
  checks
- [Cortex Semantic Contraction Audit](recon/cortex_semantic_contraction_audit.md) —
  internal audit evidence for high-confidence deletion/consolidation
  candidates; no runtime contraction or product behavior change is claimed
- [Claude Code Desktop Lifecycle Spine Branch Disposition](recon/claude_code_desktop_lifecycle_spine_branch_disposition.md) —
  branch-hygiene disposition preserving the parked Claude lifecycle spine head
  before retiring the stale managed branch

Historical runtime, lab, and governance material now lives under [archive/](archive/).
