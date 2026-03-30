# CORTEX_V2_LOCAL_VERIFICATION

Date: 2026-03-21
Status: active local verification entry points for the landed v2 boundary

## Purpose

This document records the repo-local verification commands for the landed Cortex v2 MVP.
It does not add CI or evidence regeneration.
For routine repo-local verification, use the two entry points below: `make verify` for the canonical bundle and `make test-smoke` for the smaller smoke bundle.

## Maintainer workflow

Maintainer branch/session hygiene is governed by `REPO_WORKFLOW.md`.
Use these direct commands for local workflow control:

```sh
python scripts/repo_workflow.py sync-main
python scripts/repo_workflow.py start-session --agent codex --slug task-name
python scripts/repo_workflow.py close-session --message "docs: end-state summary"
python scripts/repo_workflow.py finalize --message "docs: manual branch closeout"
python scripts/repo_workflow.py preserve-worktree --slug root-e1-verification
python scripts/repo_workflow.py audit-branches
python scripts/repo_workflow.py cleanup-report
```

These commands are workflow controls, not part of the canonical verification bundle.

Strict final-clean entry point:

```sh
make repo-hygiene
```

## Canonical bundle

Direct commands:

```sh
python3 -m pytest tests/unit -q
python3 -m pytest tests/integration -q
python3 -m pytest tests/unit/test_import_smoke.py -q
```

Repo-local entry point:

```sh
make verify
```

## Smoke bundle

The smoke bundle is intentionally smaller than full verification.
It is useful for quick local confidence only and must not be treated as full-suite closure.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_contract.py \
  tests/unit/test_correspondence_core.py \
  tests/unit/test_correspondence_ports.py \
  tests/unit/test_correspondence_sre.py \
  tests/unit/test_correspondence_periphery.py \
  tests/integration/test_reference_host_vertical_gate.py \
  tests/integration/test_reference_lane_latency.py \
  tests/integration/test_reference_lane_packet_example.py \
  tests/integration/test_reference_mediated_lane_packet_example.py \
  tests/integration/test_gemini_lane_packet_example.py \
  tests/integration/test_gemini_mediated_lane_packet_example.py \
  tests/integration/test_openai_lane_packet_example.py \
  tests/integration/test_openai_mediated_lane_packet_example.py \
  tests/integration/test_aux_claim_conservative.py \
  tests/unit/test_import_smoke.py -q
```

Repo-local entry point:

```sh
make test-smoke
```

## Reference runtime revalidation

This revalidates the accepted reference runtime shell plus the bounded feedback/runtime-state chain before cross-process continuation is layered on top.
It checks the runtime step kernel, executive builder, soft-control scoring, realization-feedback carriers, bounded short-window feedback behavior, and the reference runtime CLI shell.
It does not authorize cross-process continuation, multi-host runtime, runtime AUX activation, offline consolidation, or mediation.

Direct commands:

```sh
python3 -m pytest tests/unit/test_reference_runtime_step.py -q
python3 -m pytest tests/unit/test_reference_executive_builder.py -q
python3 -m pytest tests/unit/test_reference_runtime_scoring.py -q
python3 -m pytest tests/unit/test_reference_realization_feedback.py -q
python3 -m pytest tests/unit/test_reference_feedback_window.py -q
python3 -m pytest tests/integration/test_reference_runtime_cli.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-runtime
```

## Reference runtime continuity revalidation

This revalidates the bounded reference-host cross-process continuation slice against the already-landed one-process shell plus the explicit session-artifact boundary.
It checks the bounded artifact carrier, explicit CLI load/save behavior, and cross-process continuity equivalence.
It does not authorize multi-host runtime, generic persistence doctrine, or longer-horizon feedback widening.

Direct commands:

```sh
python3 -m pytest tests/unit/test_reference_runtime_session_io.py -q
python3 -m pytest tests/integration/test_reference_runtime_cli.py -q
python3 -m pytest tests/integration/test_reference_runtime_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-runtime-continuity
```

## OpenAI runtime revalidation

This revalidates the first OpenAI documented host-event runtime shell against the landed OpenAI driver slices, the active SRE loop, and the accepted `C1` continuation law.
It checks bounded OpenAI session persistence, raw-host-event preservation, explicit CLI load/save behavior, and split-run OpenAI continuity equivalence.
It does not authorize live network/service doctrine, outbound OpenAI host control, Gemini runtime, or generic runtime abstraction.

Direct commands:

```sh
python3 -m pytest tests/unit/test_openai_runtime_session_io.py -q
python3 -m pytest tests/unit/test_openai_runtime_step.py -q
python3 -m pytest tests/unit/test_openai_runtime_ownership.py -q
python3 -m pytest tests/integration/test_openai_runtime_cli.py -q
python3 -m pytest tests/integration/test_openai_runtime_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-runtime
```

## OpenAI ingress revalidation

This revalidates the first raw-transcript OpenAI ingress shell on top of the accepted `O1` runtime shell.
It checks transcript-shape parsing, ingress CLI behavior, split-run ingress continuity equivalence, and explicit rejection of the dev-shell wrapper shape and canonical Cortex event names.
It does not authorize live network/service doctrine, outbound OpenAI host control, Gemini runtime, or generic runtime abstraction.

Direct commands:

```sh
python3 -m pytest tests/unit/test_openai_ingress.py -q
python3 -m pytest tests/integration/test_openai_ingress_cli.py -q
python3 -m pytest tests/integration/test_openai_ingress_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-ingress
```

## OpenAI loopback service revalidation

This revalidates the first loopback-only OpenAI service shell on top of the accepted `O2` raw-transcript parser and accepted `O1` runtime/session artifact.
It checks loopback-only HTTP behavior, JSON artifact import/export, event processing over `/v1/events`, and service continuity equivalence without widening into outbound host control or generic service doctrine.
It does not authorize remote bind, multi-session doctrine, Gemini runtime, or generic runtime/service abstraction.

Direct commands:

```sh
python3 -m pytest tests/unit/test_openai_service.py -q
python3 -m pytest tests/integration/test_openai_service.py -q
python3 -m pytest tests/integration/test_openai_service_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-service
```

## OpenAI host-control revalidation

This revalidates the first bounded outbound OpenAI host-control lane on top of the accepted `O3` loopback shell, accepted `O2` ingress law, and accepted `O1` runtime/session law.
It checks the strict text-only request boundary, stdlib transport parsing, loopback action endpoint behavior, and export/import continuity across multiple outbound actions.
It does not authorize tools, tool-result submission, cancel/update lanes, remote hosting, multi-session doctrine, Gemini runtime, executive-loop rewrite, or generic runtime/service abstraction.
Canonical K2 tests use the internal fixture transport and do not require a live OpenAI network or a real API key.

Direct commands:

```sh
python3 -m pytest tests/unit/test_openai_host_control.py -q
python3 -m pytest tests/integration/test_openai_host_control_service.py -q
python3 -m pytest tests/integration/test_openai_host_control_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-host-control
```

## Executive live-outcome revalidation

This revalidates the bounded proven-lane executive loop over the accepted reference/OpenAI runtime shells and the accepted K2 host-control lane.
It now checks:
- explicit `Q_t^{online}` / `Q_t^{alloc}` diagnostics
- computed `alpha_t`
- `Q_t^{mem}=0.0`
- feedback-conditioned `activation_threshold`
- nested `control_ledger.allocation_diagnostics`
- bounded guarded/latched enforcement-aware realized control behavior
- and live-outcome-conditioned pressure over the already-landed feedback window

It does not authorize support-memory runtime, mediation, new host-control lanes, Gemini runtime shell, tools, vigor scaling, or generic reward-learning doctrine.

Direct commands:

```sh
python3 -m pytest tests/unit/test_sre_neutral_hinge.py -q
python3 -m pytest tests/unit/test_reference_executive_builder.py -q
python3 -m pytest tests/unit/test_reference_runtime_scoring.py -q
python3 -m pytest tests/unit/test_reference_runtime_step.py -q
python3 -m pytest tests/unit/test_openai_runtime_step.py -q
python3 -m pytest tests/integration/test_reference_runtime_cli.py -q
python3 -m pytest tests/integration/test_reference_runtime_continuity.py -q
python3 -m pytest tests/integration/test_openai_runtime_cli.py -q
python3 -m pytest tests/integration/test_openai_runtime_continuity.py -q
python3 -m pytest tests/integration/test_openai_ingress_cli.py -q
python3 -m pytest tests/integration/test_openai_service.py -q
python3 -m pytest tests/integration/test_openai_host_control_service.py -q
python3 -m pytest tests/integration/test_openai_host_control_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-executive-loop
```

## Gemini runtime revalidation

This revalidates the first Gemini documented host-event runtime shell on top of the landed Gemini driver slices, the accepted K3 executive allocation diagnostics, and the accepted `C1` continuity law.
It checks bounded Gemini session persistence, raw-host-event preservation, explicit CLI load/save behavior, and split-run Gemini continuity equivalence.
It does not authorize live network/service doctrine, multi-host abstraction, or support-memory runtime.

Direct commands:

```sh
python3 -m pytest tests/unit/test_gemini_runtime_session_io.py -q
python3 -m pytest tests/unit/test_gemini_runtime_step.py -q
python3 -m pytest tests/unit/test_gemini_runtime_ownership.py -q
python3 -m pytest tests/integration/test_gemini_runtime_cli.py -q
python3 -m pytest tests/integration/test_gemini_runtime_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-runtime
```

## Gemini ingress revalidation

This revalidates the first Gemini raw-transcript ingress shell on top of the accepted current-line `G1` runtime shell.
It checks transcript-shape parsing, ingress CLI behavior, split-run ingress continuity equivalence, and explicit rejection of wrapper and canonical Cortex event-name misuse.

Direct commands:

```sh
python3 -m pytest tests/unit/test_gemini_ingress.py -q
python3 -m pytest tests/integration/test_gemini_ingress_cli.py -q
python3 -m pytest tests/integration/test_gemini_ingress_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-ingress
```

## Gemini loopback service revalidation

This revalidates the first Gemini loopback-only service shell on top of the accepted current-line `G2` ingress parser and accepted current-line `G1` runtime/session artifact.
It checks loopback-only HTTP behavior, JSON artifact import/export, event processing over `/v1/events`, and service continuity equivalence without widening into remote hosting or generic service doctrine.

Direct commands:

```sh
python3 -m pytest tests/unit/test_gemini_service.py -q
python3 -m pytest tests/integration/test_gemini_service_http.py -q
python3 -m pytest tests/integration/test_gemini_service_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-service
```

## Gemini host-control revalidation

This revalidates the first bounded outbound Gemini host-control lane on top of the accepted current-line `G3` loopback shell, accepted current-line `G2` ingress law, and accepted current-line `G1` runtime/session law.
It checks the strict text-only request boundary, stdlib Gemini transport parsing, loopback action endpoint behavior, and export/import continuity across multiple outbound actions.
Canonical Gemini tests use the internal fixture transport and do not require a live Gemini network or a real API key.

Direct commands:

```sh
python3 -m pytest tests/unit/test_gemini_host_control.py -q
python3 -m pytest tests/integration/test_gemini_host_control_service.py -q
python3 -m pytest tests/integration/test_gemini_host_control_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-host-control
```

## Claude runtime revalidation

This revalidates the first Claude documented host-event runtime shell on top of the landed Claude driver slices, the accepted K3 executive allocation diagnostics, and the accepted `C1` continuity law.
It checks bounded Claude session persistence, raw-host-event preservation, top-level `message_id` projection, explicit CLI load/save behavior, and split-run Claude continuity equivalence.
It does not authorize live network/service doctrine, multi-host abstraction, or support-memory runtime.

Direct commands:

```sh
python3 -m pytest tests/unit/test_claude_runtime_session_io.py -q
python3 -m pytest tests/unit/test_claude_runtime_step.py -q
python3 -m pytest tests/unit/test_claude_runtime_ownership.py -q
python3 -m pytest tests/integration/test_claude_runtime_cli.py -q
python3 -m pytest tests/integration/test_claude_runtime_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-claude-runtime
```

## Claude ingress revalidation

This revalidates the first Claude raw-transcript ingress shell on top of the current-line Claude runtime shell.
It checks transcript-shape parsing, ingress CLI behavior, split-run ingress continuity equivalence, and explicit rejection of wrapper, canonical Cortex event-name, `ping`, and `error` misuse.

Direct commands:

```sh
python3 -m pytest tests/unit/test_claude_ingress.py -q
python3 -m pytest tests/integration/test_claude_ingress_cli.py -q
python3 -m pytest tests/integration/test_claude_ingress_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-claude-ingress
```

## Claude loopback service revalidation

This revalidates the first Claude loopback-only service shell on top of the current-line Claude ingress parser and Claude runtime/session artifact.
It checks loopback-only HTTP behavior, JSON artifact import/export, event processing over `/v1/events`, and service continuity equivalence without widening into remote hosting or generic service doctrine.

Direct commands:

```sh
python3 -m pytest tests/unit/test_claude_service.py -q
python3 -m pytest tests/integration/test_claude_service_http.py -q
python3 -m pytest tests/integration/test_claude_service_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-claude-service
```

## Claude host-control revalidation

This revalidates the first bounded outbound Claude host-control lane on top of the current-line Claude loopback shell, current-line Claude ingress law, and current-line Claude runtime/session law.
It checks the strict text-only request boundary, stdlib Anthropic Messages transport parsing, loopback action endpoint behavior, and export/import continuity across multiple outbound actions.
Canonical Claude tests use the internal fixture transport and do not require a live Anthropic network or a real API key.

Direct commands:

```sh
python3 -m pytest tests/unit/test_claude_host_control.py -q
python3 -m pytest tests/integration/test_claude_host_control_service.py -q
python3 -m pytest tests/integration/test_claude_host_control_continuity.py -q
```

Repo-local entry point:

```sh
make revalidate-claude-host-control
```

## Live-validation preflight

This verifies the current live-testing toolchain, records install channels, operator-lane auth freshness, automation-lane credential availability, and writes the local-only preflight report under `.cortex/live_validation/`.
The repo-local entry point is intentionally non-mutating and skips provider self-updates so the bounded service-proof train can rerun it reliably.
Use the direct script without `--skip-updates` only when you explicitly want to try the updater path.
It is an environment-sensitive evidence command, not part of the canonical verification bundle.

Direct command:

```sh
python3 tools/live_preflight.py --skip-updates
```

Repo-local entry point:

```sh
make live-preflight
```

Optional explicit updater path:

```sh
make live-preflight-update
```

## Live provider baselines

This captures provider smoke baselines.
By default it runs the signed-in operator lane.
The automation lane remains available as a separate optional comparison path.
Machine output is local-only under `.cortex/live_validation/`.
These smoke baselines are environment-sensitive and may fail honestly on host capacity pressure even when deeper operator lifecycle evidence remains usable.
For Gemini operator testing, the baseline now starts in CLI auto mode by default and only falls back to an explicit model after a real failure or timeout.

Direct command:

```sh
python3 tools/live_provider_baselines.py --lane operator
```

Repo-local entry point:

```sh
make live-provider-baselines
```

Optional automation comparison:

```sh
python3 tools/live_provider_baselines.py --lane automation
make live-provider-baselines-automation
```

When machine auth is absent, the automation baseline now exits with explicit auth-readiness blockers instead of attempting direct provider probes.
For actual N2 service proof, use a capable machine rather than treating current-machine blocked output as closure evidence.

## Live host-native product paths

This is the primary acceptance-grade live lane.
It runs the shared coding harness against signed-in host-native provider surfaces, keeps artifacts local-only, and measures `pass_minimal`, `restart_continuity`, and `truth_gap`.
For OpenAI, the focused lifecycle proof now lives in the separate `codex app-server` entry point below; the generic host-native target still helps as the cross-host umbrella, but `make live-openai-app-server` is the stronger OpenAI rerun surface.
For Claude and Gemini, the operator lane now records documented hook events alongside the CLI transcript artifacts.
While Claude and Gemini still carry operator-harness drift, do not treat the aggregate cross-host entrypoint by itself as the clean closure signal.
For focused Gemini reruns, use the direct script with `--provider gemini --scenario ... --max-attempts ... --cooldown-seconds ...` rather than relying on the umbrella target alone.
The Gemini-focused reruns now also accept `--preferred-model`, `--fallback-model`, `--disable-auto-probe`, and `--exploratory-probe` when a bounded local model split or Pro sidecar is needed.
Without an explicit override, Gemini operator testing now starts in CLI auto mode rather than a pinned `-m` model.
For Gemini `restart_continuity`, the inspect-only first turn now uses the lighter `plan` approval mode and the resumed edit/test turn keeps `yolo`.

Direct command:

```sh
python3 tools/live_host_native_product_paths.py
```

Repo-local entry point:

```sh
make live-host-native-product-paths
```

## Live OpenAI App Server operator proof

This is the preferred OpenAI operator-lifecycle proof for current scope.
It keeps `codex exec` as the smoke lane and uses `codex app-server` for the repeated shared coding harness and lifecycle-event capture.
Machine output is local-only under `.cortex/live_validation/`.

Direct command:

```sh
python3 tools/live_openai_app_server_operator.py
```

Repo-local entry point:

```sh
make live-openai-app-server
```

## Live Cortex host-control capture

This captures the current automation-side loopback service plus A4 / G4 / O4 host-control lanes.
It is no longer the primary live truth; it is the secondary unattended lane.
Machine output is local-only under `.cortex/live_validation/`.
This is also the bounded service-proof entry point for the automation train.
On this machine it is currently contract/readiness-only and not a lawful closure surface.
Rerun it per provider only on a capable machine where machine auth is intentionally ready and spend approval is explicitly present when required.
When the current train reruns only automation artifacts, the compare and operator-payoff support surfaces preserve the already-accepted operator truth rather than zeroing it out.

Direct command:

```sh
python3 tools/live_cortex_host_control.py --lane automation
```

Repo-local entry point:

```sh
make live-cortex-host-control
```

## Live comparison and verdict

This builds the current L2 comparison report and payoff verdict from the local-only preflight, operator baseline, signed-in operator lifecycle artifacts, and automation service artifacts.
It is a support-surface summarizer only and does not change runtime behavior.

Direct command:

```sh
python3 tools/live_compare.py
```

Repo-local entry point:

```sh
make live-compare
```

## Live operator payoff audit

This builds the operator-only payoff audit from the already-captured live operator artifacts.
It does not rerun any hosts by itself and does not change runtime behavior.

Direct command:

```sh
python3 tools/live_operator_payoff_audit.py
```

Repo-local entry point:

```sh
make live-operator-payoff-audit
```

## Operator routing realization

This revalidates the first bounded SRE-owned operator routing layer over the live-testing harness.
It checks the bounded task-state builder, the executive summary carrier, persistent tonic modulator update law, policy-view derivation, geometric route selector, quota-pressure blocking, guarded continuity preference, one extra inspect read-pass law, and route/modulator/policy diagnostics carried into live artifacts.
It does not authorize named model routing, service/auth widening, AUX activation, or packet-level runtime changes.

Direct commands:

```sh
python3 -m pytest tests/unit/test_operator_routing.py -q
python3 -m pytest tests/unit/test_sre_executive_summary.py -q
python3 -m pytest tests/unit/test_sre_modulators.py -q
python3 -m pytest tests/unit/test_sre_policy_view.py -q
python3 -m pytest tests/unit/test_live_validation_tools.py -q
python3 -m pytest tests/unit/test_correspondence_sre.py -q
```

## Live operator directionality

This runs the paired raw-vs-Cortex operator audit on the current machine.
It is operator-only and does not reopen service proof.
If a host's raw baseline cannot be isolated safely, the run must mark that pair blocked instead of comparing dishonestly.
For Gemini on the free API-key lane, keep the comparison on the vanilla headless execution path with no explicit `-m` model argument and no forced `plan` baseline.
For Claude and OpenAI, keep the current explicit stable models unless a separate host-defaults seam is explicitly opened.

Direct command:

```sh
python3 tools/live_operator_directionality.py
```

Repo-local entry point:

```sh
make live-operator-directionality
```

## Live operator directionality audit

This reduces the paired raw-vs-Cortex operator artifacts into per-host and package directionality truth.
It is an evaluation/support surface only.

Direct command:

```sh
python3 tools/live_operator_directionality_audit.py
```

Repo-local entry point:

```sh
make live-operator-directionality-audit
```

## Reference-lane packet-example revalidation

This revalidates the committed reference-lane packet example doc against the already-landed live packet path.
It does not emit candidate refreshed evidence and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_lane_packet_example.py
```

Repo-local entry point:

```sh
make revalidate-reference-packet
```

## Reference-lane packet-example candidate refresh

This emits candidate refreshed packet-example evidence from the already-landed live packet path to stdout for manual inspection.
It is useful context for the proof-packet prerequisite gate recorded in `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`, but it does not update gate truth and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m tests.integration._reference_lane_packet_example
```

Repo-local entry point:

```sh
make emit-reference-packet-candidate
```

Exact committed-doc regeneration is still not part of normal verification and remains explicit/manual/out of scope unless separately requested.

## Gemini-lane packet-example revalidation

This revalidates the committed Gemini-lane packet example doc against the already-landed live Gemini packet/publication path.
It does not emit candidate refreshed evidence and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_gemini_lane_packet_example.py
```

Repo-local entry point:

```sh
make revalidate-gemini-packet
```

## Gemini-lane packet-example candidate refresh

This emits candidate refreshed Gemini packet-example evidence from the already-landed live packet/publication path to stdout for manual inspection.
It does not update blocker truth and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m tests.integration._gemini_lane_packet_example
```

Repo-local entry point:

```sh
make emit-gemini-packet-candidate
```

## OpenAI-lane packet-example revalidation

This revalidates the committed OpenAI-lane packet example doc against the already-landed live OpenAI packet/publication path.
It does not emit candidate refreshed evidence and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_openai_lane_packet_example.py
```

Repo-local entry point:

```sh
make revalidate-openai-packet
```

## OpenAI-lane packet-example candidate refresh

This emits candidate refreshed OpenAI packet-example evidence from the already-landed live packet/publication path to stdout for manual inspection.
It does not update blocker truth and it does not overwrite the committed example doc.

Direct command:

```sh
python3 -m tests.integration._openai_lane_packet_example
```

Repo-local entry point:

```sh
make emit-openai-packet-candidate
```

## Latency-evidence revalidation

This revalidates the committed latency evidence doc against the already-landed live latency collector.
It checks the committed scope, targets, and measurement metadata rather than demanding exact replay of historical micro-latency values.
It does not produce candidate refreshed evidence and it does not regenerate or overwrite the committed latency doc.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_lane_latency.py
```

Repo-local entry point:

```sh
make revalidate-latency-evidence
```

## Latency-evidence candidate refresh

This emits candidate refreshed latency evidence from the already-landed live collector to stdout for manual inspection.
It is useful context for the landed latency evidence gate recorded in `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`, but it does not update gate truth and it does not overwrite the committed latency doc.

Direct command:

```sh
python3 -m tests.integration._reference_lane_latency_evidence
```

Repo-local entry point:

```sh
make emit-latency-evidence-candidate
```

Exact committed-doc regeneration is still explicit/manual/out of scope unless separately requested.

## Mediation-evidence package revalidation

This checks the committed mediation evidence scaffold for fair matched-pair accounting, host-split preseed coverage, conservative verdict defaults, and blocker truth.
It is check-only: it does not generate run packets, emit candidate evidence, or authorize mediation implementation.

Direct commands:

```sh
python3 -m pytest tests/unit/test_mediation_evidence_package.py -q
python3 tools/mediation_evidence_package.py --check
```

Repo-local entry point:

```sh
make revalidate-mediation-evidence-package
```

## Mediation branch-discipline revalidation

This revalidates the new J2 branch-discipline family on the preferred deterministic hosts.
It checks the new reference/OpenAI/Claude branch-discipline basis notes and the committed mediated comparator packet series.
It remains evidence-only and does not authorize mediation implementation.

Repo-local entry point:

```sh
make revalidate-mediation-branch-discipline
```

## Mediation non-thrash burden revalidation

This revalidates the new J2 non-thrash burden family on the preferred deterministic hosts.
It checks the new reference/OpenAI/Claude burden basis notes, the committed comparator packet series, and the committed AUX burden artifacts.
It remains evidence-only and does not authorize mediation implementation.

Repo-local entry point:

```sh
make revalidate-mediation-non-thrash-burden
```

## Mediation Claude host-realization revalidation

This revalidates the new J2 Claude host-realization expansion.
It checks the committed Claude lane packet example, the committed Claude mediated packet example, the Claude host-realization basis note, and the full three-pair Claude host-realization comparator series.
It remains Claude-only and evidence-only, and it does not authorize mediation implementation.

Repo-local entry point:

```sh
make revalidate-mediation-claude-host-realization
```

## Optional Claude uncertainty revalidation

This target is reserved for the optional J2 Claude uncertainty expansion only if that narrower rerun is explicitly opened later.
On the current line, no committed Claude uncertainty package exists yet.

Repo-local entry point:

```sh
make revalidate-mediation-claude-uncertainty
```

## Mediation reference host-realization admissibility revalidation

This checks that `scenario_host_reference_01` now has three lawful reference-only host-realization comparator pairs, that the cell now has `candidate_positive` signal for better host-specialized realization, and that the package still supports the accepted J3 justification decision without becoming a second truth court.
It validates the supporting admissibility note, the updated baseline-anchor row, the recorded paired-ledger rows, and the package-level decision wording. It does not generate evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_host_realization_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-host-realization-basis
```

## Live reference mediated host-realization revalidation

This revalidates the committed mediated reference lane packet example and all three recorded reference host-realization comparator pairs against live code.
It remains reference-only and evidence-only, and it does not justify mediation.

Direct commands:

```sh
python3 -m pytest tests/integration/test_reference_mediated_lane_packet_example.py -q
python3 -m pytest tests/integration/test_reference_mediated_host_realization_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediated-host-realization
```

## Reference mediated host-realization candidate refresh

This emits the committed mediated reference host-realization packet docs to stdout for manual inspection.
It does not overwrite the committed docs and it does not authorize mediation implementation.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_host_realization_experimental
```

Repo-local entry point:

```sh
make emit-reference-mediated-host-realization-candidate
```

## Mediation Gemini host-realization admissibility revalidation

This checks that `scenario_host_gemini_01` now has three lawful Gemini-only host-realization comparator pairs recorded and that the exact Gemini host-realization cell now has `candidate_positive` signal for better host-specialized realization while the package still supports the accepted J3 decision without becoming a second truth court.
It validates the Gemini admissibility note, the committed Gemini baseline and mediated packet examples, the committed Gemini baseline and mediated host packets, the Gemini replication law, the rebound baseline-index row, the recorded paired-ledger row, and the package-level decision wording. It does not generate evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_gemini_host_realization_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-gemini-host-realization-basis
```

## Live Gemini mediated host-realization revalidation

This revalidates the committed mediated Gemini lane packet example and the full three-pair Gemini host-realization comparator series against live Gemini code.
It remains Gemini-only and evidence-only, and it does not justify mediation.

Direct commands:

```sh
python3 -m pytest tests/integration/test_gemini_mediated_lane_packet_example.py -q
python3 -m pytest tests/integration/test_gemini_mediated_host_realization_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-mediated-host-realization
```

## Gemini mediated host-realization candidate refresh

This emits the committed mediated Gemini host-realization packet docs to stdout for manual inspection.
It does not overwrite the committed docs and it does not authorize mediation implementation.

Direct command:

```sh
python3 -m tests.integration._gemini_mediation_host_realization_experimental
```

Repo-local entry point:

```sh
make emit-gemini-mediated-host-realization-candidate
```

## Live OpenAI mediated host-realization revalidation

This revalidates the committed mediated OpenAI lane packet example and the counted three-pair OpenAI host-realization comparator series against live OpenAI code.
It remains OpenAI-only and evidence-only, and it does not justify mediation.

Direct commands:

```sh
python3 -m pytest tests/integration/test_openai_mediated_lane_packet_example.py -q
python3 -m pytest tests/integration/test_openai_mediated_host_realization_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-mediated-host-realization
```

## OpenAI mediated host-realization candidate refresh

This emits the committed mediated OpenAI host-realization packet docs to stdout for manual inspection.
It does not overwrite the committed docs and it does not authorize mediation implementation.

Direct command:

```sh
python3 -m tests.integration._openai_mediation_host_realization_experimental
```

Repo-local entry point:

```sh
make emit-openai-mediated-host-realization-candidate
```

## Mediation OpenAI host-realization admissibility revalidation

This checks that `scenario_host_openai_01` now has three lawful OpenAI host-realization comparator pairs recorded and that the OpenAI host-realization cell is now `candidate_positive` while the package still supports the accepted J3 decision without becoming a second truth court.
It validates the OpenAI admissibility note, the committed OpenAI baseline and mediated packet examples, the committed OpenAI baseline and mediated host packets, the OpenAI baseline-index guardrail, the paired-ledger rows, and the package-level decision wording. It does not generate evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_openai_host_realization_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-openai-host-realization-basis
```

## Mediation run-packet revalidation

This checks the committed reference-host, Gemini-host, OpenAI-host, and Claude-host run-packet instances against the current scenario catalog.
It validates packet metadata against the scenario catalog, confirms the canonical baseline anchors remain lawful, validates the current committed baseline sets for all four hosts, and checks the full committed mediated packet surface for thrash, uncertainty, branch-discipline, non-thrash burden, and host-realization.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_run_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-run-packets
```

## Live reference mediation-baseline revalidation

This revalidates the nine committed reference-host baseline mediation packets against live reference-host code paths.
It remains reference-first and baseline-only: it does not advance any paired counts and it does not add Gemini or OpenAI live packets.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediation_baseline_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediation-baselines
```

## Live Gemini mediation-baseline revalidation

This revalidates the committed Gemini-host baseline packet series against the landed Gemini commitment-path slice.
It covers the full three-pair Gemini host-realization baseline series, the three Gemini uncertainty baselines, and the three Gemini thrash baselines, remains Gemini-only and baseline-only, and does not by itself justify any paired verdict.

Direct command:

```sh
python3 -m pytest tests/integration/test_gemini_mediation_baseline_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-mediation-baselines
```

## Gemini mediation-baseline candidate refresh

This emits the committed Gemini-host baseline mediation packet docs to stdout for manual inspection.
It prints markdown for all nine committed Gemini baseline docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize any paired comparison or mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._gemini_mediation_baseline_packets
```

Repo-local entry point:

```sh
make emit-gemini-mediation-baselines-candidate
```

## Live OpenAI mediation-baseline revalidation

This revalidates the committed OpenAI-host baseline packet series against the landed OpenAI carrier slices.
It remains OpenAI-only and baseline-only: it covers the one OpenAI host-realization baseline anchor, the three committed OpenAI uncertainty baseline docs, and the three committed OpenAI thrash baseline docs and does not by itself justify any verdict.

Direct command:

```sh
python3 -m pytest tests/integration/test_openai_mediation_baseline_packets.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-mediation-baselines
```

## OpenAI mediation-baseline candidate refresh

This emits the committed OpenAI-host baseline mediation packet docs to stdout for manual inspection.
It prints markdown for all seven committed OpenAI baseline docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize any paired comparison or mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._openai_mediation_baseline_packets
```

Repo-local entry point:

```sh
make emit-openai-mediation-baselines-candidate
```

## Experimental OpenAI mediated-thrash revalidation

This revalidates the three committed experimental OpenAI-only mediated thrash comparators against live OpenAI lifecycle code.
It checks that each mediated packet stays OpenAI-only, preserves the same certified completion class and commitment boundary as baseline, and removes one redundant `resume` without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_openai_mediated_thrash_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-mediated-thrash
```

## Experimental OpenAI mediated-thrash candidate refresh

This emits the committed experimental OpenAI-only mediated thrash packet docs to stdout for manual inspection.
It prints markdown for all three committed OpenAI thrash mediated packet docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._openai_mediation_thrash_experimental
```

Repo-local entry point:

```sh
make emit-openai-mediated-thrash-candidate
```

## Experimental OpenAI mediated-uncertainty revalidation

This revalidates the three committed experimental OpenAI-only mediated uncertainty comparators against live OpenAI commitment-path code.
It checks that each mediated packet stays OpenAI-only, preserves the same completion class and truth boundary as baseline, and removes one redundant uncertified loop without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_openai_mediated_uncertainty_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-openai-mediated-uncertainty
```

## Experimental OpenAI mediated-uncertainty candidate refresh

This emits the committed experimental OpenAI-only mediated uncertainty packet docs to stdout for manual inspection.
It prints markdown for the three committed OpenAI mediated docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._openai_mediation_uncertainty_experimental
```

Repo-local entry point:

```sh
make emit-openai-mediated-uncertainty-candidate
```

## Experimental Gemini mediated-uncertainty revalidation

This revalidates the three committed experimental Gemini-only mediated uncertainty comparators against live Gemini commitment-path code.
It checks that each mediated packet stays Gemini-only, preserves the same completion class and truth boundary as baseline, and removes one redundant uncertified loop without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_gemini_mediated_uncertainty_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-mediated-uncertainty
```

## Experimental Gemini mediated-uncertainty candidate refresh

This emits candidate refreshed experimental Gemini-only mediated uncertainty packet docs to stdout for manual inspection.
It prints markdown for all three committed Gemini mediated uncertainty packet docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._gemini_mediation_uncertainty_experimental
```

Repo-local entry point:

```sh
make emit-gemini-mediated-uncertainty-candidate
```

## Experimental Gemini mediated-thrash revalidation

This revalidates the three committed experimental Gemini-only mediated thrash comparators against live Gemini lifecycle code.
It checks that each mediated packet stays Gemini-only, preserves the same certified completion class and commitment boundary as baseline, and removes one redundant `resume` without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_gemini_mediated_thrash_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-gemini-mediated-thrash
```

## Experimental Gemini mediated-thrash candidate refresh

This emits candidate refreshed experimental Gemini-only mediated thrash packet docs to stdout for manual inspection.
It prints markdown for all three committed Gemini mediated thrash packet docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._gemini_mediation_thrash_experimental
```

Repo-local entry point:

```sh
make emit-gemini-mediated-thrash-candidate
```

## Reference mediation-baseline candidate refresh

This emits candidate refreshed reference-host baseline mediation packet docs to stdout for manual inspection.
It prints markdown for all nine committed reference baseline packet docs with committed relative-path headers, does not overwrite the committed packet docs, and does not authorize any paired comparison or mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_baseline_packets
```

Repo-local entry point:

```sh
make emit-reference-mediation-baselines-candidate
```

## Experimental reference mediated-thrash revalidation

This revalidates the three committed experimental reference-only mediated thrash comparators against live reference-host code paths.
It checks that each mediated packet stays reference-only, preserves the same completion class and truth boundary as baseline, and reduces branch oscillation without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediated_thrash_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediated-thrash
```

## Experimental reference mediated-thrash candidate refresh

This emits the committed experimental reference-only mediated thrash packet docs to stdout for manual inspection.
It prints markdown for all three committed thrash comparator docs with committed relative-path headers, does not overwrite the committed docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_thrash_experimental
```

Repo-local entry point:

```sh
make emit-reference-mediated-thrash-candidate
```

## Experimental reference mediated-uncertainty revalidation

This revalidates the three committed experimental reference-only mediated uncertainty comparators against live reference-host code paths.
It checks that each mediated packet stays reference-only, preserves contradiction/degradation handling and the same certified completion class as baseline, and reduces redundant uncertified loops without widening package-level verdicts.

Direct command:

```sh
python3 -m pytest tests/integration/test_reference_mediated_uncertainty_comparator.py -q
```

Repo-local entry point:

```sh
make revalidate-reference-mediated-uncertainty
```

## Experimental reference mediated-uncertainty candidate refresh

This emits the committed experimental reference-only mediated uncertainty packet docs to stdout for manual inspection.
It prints markdown for all three committed uncertainty comparator docs with committed relative-path headers, does not overwrite the committed docs, and does not authorize mediation implementation work.

Direct command:

```sh
python3 -m tests.integration._reference_mediation_uncertainty_experimental
```

Repo-local entry point:

```sh
make emit-reference-mediated-uncertainty-candidate
```

## Mediation Gemini uncertainty-basis revalidation

This checks that `scenario_uncertainty_gemini_01` now has a satisfied committed Gemini uncertainty basis and replication law.
It validates the Gemini baseline index, the Gemini uncertainty basis note, the Gemini uncertainty replication note, the committed Gemini packet series, the live Gemini builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_gemini_uncertainty_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-gemini-uncertainty-basis
```

## Mediation Gemini thrash-basis revalidation

This checks that `scenario_thrash_gemini_01` now has a satisfied committed Gemini thrash basis and replication law.
It validates the Gemini baseline index, the Gemini thrash basis note, the Gemini thrash replication note, the committed Gemini thrash packet series, the live Gemini thrash builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_gemini_thrash_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-gemini-thrash-basis
```

## Mediation OpenAI uncertainty-basis revalidation

This checks that `scenario_uncertainty_openai_01` now has a satisfied committed OpenAI basis and replication law.
It validates the OpenAI baseline index, the OpenAI uncertainty basis note, the replication note, the committed OpenAI packet series, the live OpenAI builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_openai_uncertainty_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-openai-uncertainty-basis
```

## Mediation OpenAI thrash-basis revalidation

This checks that `scenario_thrash_openai_01` now has a satisfied committed OpenAI thrash basis and replication law.
It validates the OpenAI baseline index, the OpenAI thrash basis note, the replication note, the committed OpenAI thrash packet series, the live OpenAI thrash builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_openai_thrash_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-openai-thrash-basis
```

## Mediation reference-uncertainty basis revalidation

This checks that `scenario_uncertainty_reference_01` now has a satisfied committed basis and replication law.
It validates the supporting basis note, the replication note, the committed uncertainty packet series, the live uncertainty builder set, and the repeated paired-run distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_uncertainty_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-uncertainty-basis
```

## Mediation reference-thrash basis revalidation

This checks that `scenario_thrash_reference_01` now has a satisfied committed basis and replication law.
It validates the supporting basis note, the replication note, the committed thrash packet series, the live thrash builder set, and the deterministic branch-derivation and cross-pair distinctness rules. It does not generate any new evidence.

Direct command:

```sh
python3 -m pytest tests/unit/test_mediation_reference_thrash_basis.py -q
```

Repo-local entry point:

```sh
make revalidate-mediation-reference-thrash-basis
```

## Aggregate mediation-evidence revalidation

This runs all current mediation-evidence checks together:
- package scaffold validation
- host-realization admissibility validation
- live Gemini packet-example revalidation
- run-packet instance validation
- live reference baseline packet revalidation
- live Gemini baseline packet revalidation
- live OpenAI baseline packet revalidation
- live experimental OpenAI mediated-thrash revalidation
- live experimental Gemini mediated-thrash revalidation
- live experimental Gemini mediated-uncertainty revalidation
- live experimental reference mediated-uncertainty revalidation
- live experimental reference mediated-thrash revalidation
- Gemini thrash basis and replication validation
- Gemini uncertainty basis and replication validation
- OpenAI thrash basis and replication validation
- OpenAI baseline validation
- live experimental OpenAI mediated-uncertainty revalidation
- OpenAI uncertainty basis and replication validation
- reference uncertainty basis and replication validation
- reference thrash basis and replication validation

It remains check-only and does not generate evidence or authorize mediation implementation.

Repo-local entry point:

```sh
make revalidate-mediation-evidence
```

## Mediation justification revalidation

This reruns the full mediation evidence package and then checks that the current justification/workflow truth is synced to that accepted J3 decision.
It remains check-only and does not authorize implementation by itself.

Repo-local entry point:

```sh
make revalidate-mediation-justification
```

## Individual entry points

```sh
make seam-preflight
make test-unit
make test-integration
make test-smoke
make verify
```

## Seam preflight

Use this before opening a new seam.
It is a workflow guard, not a test bundle.

Direct commands:

```sh
git branch --show-current
git rev-list --left-right --count main...origin/main
git status --short --untracked-files=all
```

Repo-local entry point:

```sh
make seam-preflight
```

The target:

- prints the current branch
- prints `main...origin/main` divergence when that comparison is available
- prints full worktree status
- fails on `main`
- fails when tracked worktree changes are still present
- reminds the operator to classify seam risk before opening new work
- reminds the operator that timing-, environment-sensitive, and shared verification-plumbing seams require repeated reruns before acceptance

It does not fail on untracked noise by itself.
Its purpose is to stop “next seam” work when the current seam is still open.

## Current live parent baseline

In this maintainer workspace:

- accepted post-`E4` verification baseline: `194a43f`
- temporary live parent branch: `codex/e4b-reference-contradiction-helpers`
- until a separate non-archival integration branch is explicitly declared, new v2 seams should branch from `codex/e4b-reference-contradiction-helpers` or a later fast-forward descendant of that accepted baseline
- do not branch new v2 work from `codex/e1-verification-substrate-entrypoints`
- do not branch new v2 work from `codex/closure-train-2026-03-24`
- do not branch new v2 work from archival `main` / `origin/main`

## Core correspondence drift check

This is the first Core-scoped correspondence drift check only.
It does not cover drivers, SRE, eval, AUX, or full correspondence parsing yet.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_core.py
```

Repo-local entry point:

```sh
make test-correspondence-core
```

## Correspondence contract drift check

This checks that the correspondence landing rule stays aligned across the living correspondence authority, the implementation master plan, and the repo agent contract.
It is a policy-sync check only. It does not validate individual correspondence rows or runtime behavior.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_contract.py
```

Repo-local entry point:

```sh
make test-correspondence-contract
```

## Ports correspondence drift check

This covers the landed Section 2 ports/provenance/normalization rows that remain outside the Section 1 Core audit.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_ports.py
```

Repo-local entry point:

```sh
make test-correspondence-ports
```

## SRE correspondence drift check

This is the SRE-scoped follow-on to the Core drift check.
It still does not cover drivers, eval, AUX, or full correspondence parsing.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_sre.py
```

Repo-local entry point:

```sh
make test-correspondence-sre
```

## Periphery correspondence drift check

Together with the Core, ports, and SRE checks, this completes the currently landed correspondence drift surface across Core, Section 2 ports, SRE, drivers, eval, and AUX.
The currently landed correspondence ledger is now mechanically covered short of full prose-ledger parsing.

Direct command:

```sh
python3 -m pytest tests/unit/test_correspondence_periphery.py
```

Repo-local entry point:

```sh
make test-correspondence-periphery
```

## Notes

- `pytest.ini` is intentionally minimal and only anchors discovery to `tests`.
- Packet-example evidence revalidation is limited to the committed reference-lane doc and remains separate from regeneration.
- Latency evidence revalidation is limited to checking the committed doc against live collection and remains separate from regeneration.
- `python3 -m pytest` also passes in the current repo, but the canonical local bundle remains the split closeout bundle above.

## Coverage prerequisite

This repo now has repo-local coverage configuration in `.coveragerc`.
This seam adds one local coverage invocation and one matching repo-local entry point.

Coverage is still not part of the canonical local verification bundle.
Minimal local prerequisite: install a package that provides `python3 -m coverage`.
The first committed baseline in `docs/CORTEX_V2_COVERAGE_BASELINE_NOTE_0.md` was captured in an environment where that prerequisite was present.

Current repo-local coverage scope from `.coveragerc`:

- executed Python under `cortex/`
- executed test code under `tests/`

This coverage surface does not cover:

- `docs/`, `.claude/`, or other non-Python repo content
- files outside `cortex/` and `tests/`
- any threshold, pass/fail gate, or reinterpretation of MVP completeness from first coverage numbers

Direct command:

```sh
python3 -m coverage run --rcfile=.coveragerc -m pytest
python3 -m coverage report --rcfile=.coveragerc
```

Repo-local entry point:

```sh
make coverage
```

If the tool is unavailable in another environment, `make coverage` fails with a short actionable message instead of silently succeeding.

Still intentionally not included in this coverage surface:

- coverage remains outside the canonical local verification bundle
- no coverage threshold or pass/fail gate
