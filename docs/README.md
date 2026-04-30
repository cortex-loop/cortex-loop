# Cortex Docs

Surface: product

This directory index is product-first and single-truth-first.

Active docs:
- [CORTEX](CORTEX.md) — canonical narrative authority
- [Current Status](CORTEX_STATUS.md)
- [CORTEX Core](CORTEX_V2_CORE_2.md)
- [CORTEX SRE](CORTEX_V2_SRE_2.md)
- [CORTEX AUX](CORTEX_V2_AUX_2.md)
- [Repo Workflow](internal/REPO_WORKFLOW.md)
- [Claude Code Desktop Cortex Plugin Design](cortex_plugin/DESIGN.md) —
  v1 full-lifecycle plugin architecture for Claude Code Desktop's Code tab
- [Claude Code Desktop Cortex Host Adapter](cortex_plugin/ADAPTER.md) —
  structural host-adapter pattern for the plugin build
- [Claude Code Desktop Plugin Evidence Synthesis](cortex_plugin/EVIDENCE_SYNTHESIS.md) —
  accounting of what Claude Code Desktop hook evidence has and has not earned
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

Historical runtime, lab, and governance material now lives under [archive/](archive/).
