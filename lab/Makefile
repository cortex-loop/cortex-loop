PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
COVERAGE ?= $(PYTHON) -m coverage
COVERAGE_RC ?= .coveragerc
ROOT := $(abspath $(CURDIR)/..)
ROOT_PYTEST = cd "$(ROOT)" && $(PYTEST)
ROOT_PYTHON = cd "$(ROOT)" && $(PYTHON)
ROOT_COVERAGE = cd "$(ROOT)" && $(COVERAGE)

.PHONY: test-unit test-integration test-smoke verify repo-hygiene seam-preflight agent-loop-guard-plan agent-loop-guard-init agent-loop-guard-evaluate agent-loop-guard-assert-closure live-preflight live-preflight-update live-provider-baselines live-provider-baselines-automation live-host-native-product-paths live-openai-app-server live-codex-dogfood live-cortex-host-control live-compare live-operator-payoff-audit live-operator-directionality live-operator-directionality-audit v2-adoption-review conformance-preflight conformance-fast conformance-active revalidate-reference-runtime revalidate-reference-runtime-continuity revalidate-openai-runtime revalidate-openai-ingress revalidate-openai-service revalidate-openai-host-control revalidate-executive-loop revalidate-gemini-runtime revalidate-gemini-ingress revalidate-gemini-service revalidate-gemini-host-control revalidate-claude-runtime revalidate-claude-ingress revalidate-claude-service revalidate-claude-host-control revalidate-reference-packet emit-reference-packet-candidate revalidate-gemini-packet emit-gemini-packet-candidate revalidate-openai-packet emit-openai-packet-candidate revalidate-latency-evidence emit-latency-evidence-candidate revalidate-mediation-evidence-package revalidate-mediation-run-packets revalidate-reference-mediation-baselines emit-reference-mediation-baselines-candidate revalidate-gemini-mediation-baselines emit-gemini-mediation-baselines-candidate revalidate-openai-mediation-baselines emit-openai-mediation-baselines-candidate revalidate-reference-mediated-host-realization emit-reference-mediated-host-realization-candidate revalidate-gemini-mediated-host-realization emit-gemini-mediated-host-realization-candidate revalidate-openai-mediated-host-realization emit-openai-mediated-host-realization-candidate revalidate-reference-mediated-thrash emit-reference-mediated-thrash-candidate revalidate-reference-mediated-uncertainty emit-reference-mediated-uncertainty-candidate revalidate-gemini-mediated-uncertainty emit-gemini-mediated-uncertainty-candidate revalidate-gemini-mediated-thrash emit-gemini-mediated-thrash-candidate revalidate-openai-mediated-uncertainty emit-openai-mediated-uncertainty-candidate revalidate-openai-mediated-thrash emit-openai-mediated-thrash-candidate revalidate-mediation-reference-host-realization-basis revalidate-mediation-gemini-host-realization-basis revalidate-mediation-openai-host-realization-basis revalidate-mediation-reference-thrash-basis revalidate-mediation-reference-uncertainty-basis revalidate-mediation-gemini-thrash-basis revalidate-mediation-gemini-uncertainty-basis revalidate-mediation-openai-thrash-basis revalidate-mediation-openai-uncertainty-basis revalidate-mediation-branch-discipline revalidate-mediation-non-thrash-burden revalidate-mediation-claude-host-realization revalidate-mediation-claude-uncertainty revalidate-mediation-evidence revalidate-mediation-justification coverage test-correspondence-contract test-correspondence-core test-correspondence-ports test-correspondence-sre test-correspondence-periphery

test-unit:
	$(ROOT_PYTEST) tests/product tests/conformance tests/experimental tests/lab tests/internal -q

test-integration:
	$(ROOT_PYTEST) tests/product/integration tests/conformance/integration tests/experimental/integration -q

test-smoke:
	$(ROOT_PYTEST) tests/product/test_import_smoke.py \
		tests/product/test_public_boundary.py \
		tests/conformance/test_host_import_smoke.py \
		tests/internal/test_docs_boundary.py \
		tests/internal/test_workflow_boundary.py \
		tests/lab/test_lab_surface.py -q

verify:
	$(ROOT_PYTEST) tests/product -q
	$(ROOT_PYTEST) tests/conformance -q
	$(ROOT_PYTEST) tests/experimental -q
	$(ROOT_PYTEST) tests/lab -q
	$(ROOT_PYTEST) tests/internal -q

repo-hygiene:
	$(ROOT_PYTHON) internal/workflow/repo_workflow.py cleanup-report

revalidate-reference-runtime:
	$(ROOT_PYTEST) tests/conformance/test_reference_runtime_step.py -q
	$(ROOT_PYTEST) tests/product/test_reference_executive_builder.py -q
	$(ROOT_PYTEST) tests/product/test_reference_runtime_scoring.py -q
	$(ROOT_PYTEST) tests/product/test_reference_realization_feedback.py -q
	$(ROOT_PYTEST) tests/product/test_reference_feedback_window.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_reference_runtime_cli.py -q

revalidate-reference-runtime-continuity:
	$(ROOT_PYTEST) tests/conformance/test_reference_runtime_session_io.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_reference_runtime_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_reference_runtime_continuity.py -q

revalidate-openai-runtime:
	$(ROOT_PYTEST) tests/product/test_openai_runtime_session_io.py -q
	$(ROOT_PYTEST) tests/product/test_openai_runtime_step.py -q
	$(ROOT_PYTEST) tests/product/test_openai_runtime_ownership.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_runtime_cli.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_runtime_continuity.py -q

revalidate-openai-ingress:
	$(ROOT_PYTEST) tests/product/test_openai_ingress.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_ingress_cli.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_ingress_continuity.py -q

revalidate-openai-service:
	$(ROOT_PYTEST) tests/product/test_openai_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_service_continuity.py -q

revalidate-openai-host-control:
	$(ROOT_PYTEST) tests/product/test_verified_work.py -q
	$(ROOT_PYTEST) tests/product/test_verified_work_runtime.py -q
	$(ROOT_PYTEST) tests/product/test_openai_runtime_step.py -q
	$(ROOT_PYTEST) tests/product/test_openai_host_control.py -q
	$(ROOT_PYTEST) tests/product/test_openai_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_host_control_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_host_control_continuity.py -q

revalidate-executive-loop:
	$(ROOT_PYTEST) tests/product/test_sre_neutral_hinge.py -q
	$(ROOT_PYTEST) tests/product/test_reference_executive_builder.py -q
	$(ROOT_PYTEST) tests/product/test_reference_runtime_scoring.py -q
	$(ROOT_PYTEST) tests/conformance/test_reference_runtime_step.py -q
	$(ROOT_PYTEST) tests/product/test_openai_runtime_step.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_reference_runtime_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_reference_runtime_continuity.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_runtime_cli.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_runtime_continuity.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_ingress_cli.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_host_control_service.py -q
	$(ROOT_PYTEST) tests/product/integration/test_openai_host_control_continuity.py -q

revalidate-gemini-runtime:
	$(ROOT_PYTEST) tests/conformance/test_gemini_runtime_session_io.py -q
	$(ROOT_PYTEST) tests/conformance/test_gemini_runtime_step.py -q
	$(ROOT_PYTEST) tests/conformance/test_gemini_runtime_ownership.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_runtime_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_runtime_continuity.py -q

revalidate-gemini-ingress:
	$(ROOT_PYTEST) tests/conformance/test_gemini_ingress.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_ingress_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_ingress_continuity.py -q

revalidate-gemini-service:
	$(ROOT_PYTEST) tests/conformance/test_gemini_service.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_service_http.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_service_continuity.py -q

revalidate-gemini-host-control:
	$(ROOT_PYTEST) tests/conformance/test_gemini_host_control.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_host_control_service.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_gemini_host_control_continuity.py -q

revalidate-claude-runtime:
	$(ROOT_PYTEST) tests/conformance/test_claude_runtime_session_io.py -q
	$(ROOT_PYTEST) tests/conformance/test_claude_runtime_step.py -q
	$(ROOT_PYTEST) tests/conformance/test_claude_runtime_ownership.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_runtime_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_runtime_continuity.py -q

revalidate-claude-ingress:
	$(ROOT_PYTEST) tests/conformance/test_claude_ingress.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_ingress_cli.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_ingress_continuity.py -q

revalidate-claude-service:
	$(ROOT_PYTEST) tests/conformance/test_claude_service.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_service_http.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_service_continuity.py -q

revalidate-claude-host-control:
	$(ROOT_PYTEST) tests/conformance/test_claude_host_control.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_host_control_service.py -q
	$(ROOT_PYTEST) tests/conformance/integration/test_claude_host_control_continuity.py -q

seam-preflight:
	@branch="$$(git branch --show-current)"; \
	echo "branch: $$branch"; \
	if [ "$$branch" = "main" ]; then \
		echo "seam-preflight: refuse to start a seam on main"; \
		exit 1; \
	fi; \
	divergence="$$(git rev-list --left-right --count main...origin/main 2>/dev/null || true)"; \
	if [ -n "$$divergence" ]; then \
		echo "main_vs_origin_main: $$divergence"; \
	else \
		echo "main_vs_origin_main: unavailable"; \
	fi; \
	status="$$(git status --short --untracked-files=all)"; \
	if [ -n "$$status" ]; then \
		echo "worktree_status:"; \
		printf '%s\n' "$$status"; \
	else \
		echo "worktree_status: clean"; \
	fi; \
	tracked_dirty="$$(git status --porcelain=v1 --untracked-files=all | grep -v '^?? ' || true)"; \
	if [ -n "$$tracked_dirty" ]; then \
		echo "seam-preflight: tracked worktree changes must be accepted or committed before a new seam"; \
		echo "classify dirty paths as current seam / unrelated noise / blocker before continuing"; \
		exit 1; \
	fi; \
	echo "seam-preflight: classify seam risk as deterministic code/doc, parser/doc-sync, timing or environment-sensitive, or shared verification-plumbing"; \
	echo "seam-preflight: timing, environment-sensitive, and shared verification-plumbing seams require repeated reruns before acceptance"

agent-loop-guard-plan:
	$(ROOT_PYTHON) -m lab.agent_loop_guard render-plan

agent-loop-guard-init:
	$(ROOT_PYTHON) -m lab.agent_loop_guard init-report

agent-loop-guard-evaluate:
	$(ROOT_PYTHON) -m lab.agent_loop_guard evaluate --host codex --format summary

agent-loop-guard-assert-closure:
	$(ROOT_PYTHON) -m lab.agent_loop_guard assert-closure

live-v2-communication-audit:
	$(ROOT_PYTHON) -m lab.v2_live_communication_audit --update-gates

live-preflight:
	$(ROOT_PYTHON) lab/live_preflight.py --skip-updates

live-preflight-update:
	$(ROOT_PYTHON) lab/live_preflight.py

live-provider-baselines:
	$(ROOT_PYTHON) lab/live_provider_baselines.py --lane operator

live-provider-baselines-automation:
	$(ROOT_PYTHON) lab/live_provider_baselines.py --lane automation

live-host-native-product-paths:
	$(ROOT_PYTHON) lab/live_host_native_product_paths.py

live-openai-app-server:
	$(ROOT_PYTHON) lab/live_openai_app_server_operator.py

live-codex-dogfood:
	$(ROOT_PYTHON) -m lab.live_codex_dogfood

live-cortex-host-control:
	$(ROOT_PYTHON) lab/live_cortex_host_control.py --lane automation

live-compare:
	$(ROOT_PYTHON) lab/live_compare.py

conformance-preflight:
	$(ROOT_PYTHON) lab/cortex_conformance.py --mode preflight

conformance-fast:
	$(ROOT_PYTHON) lab/cortex_conformance.py --mode fast --contract-pack verified_work_bookmarks_v1

conformance-active:
	$(ROOT_PYTHON) lab/cortex_conformance.py --mode active --contract-pack verified_work_bookmarks_v1

live-operator-payoff-audit:
	$(ROOT_PYTHON) lab/live_operator_payoff_audit.py

live-operator-directionality:
	$(ROOT_PYTHON) lab/live_operator_directionality.py

live-operator-directionality-audit:
	$(ROOT_PYTHON) lab/live_operator_directionality_audit.py

v2-guidance-optimization-audit:
	$(ROOT_PYTHON) -m lab.v2_guidance_optimization_audit

v2-adoption-review:
	$(ROOT_PYTHON) -m lab.v2_adoption_review

revalidate-reference-packet:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_lane_packet_example.py

emit-reference-packet-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_lane_packet_example

revalidate-gemini-packet:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_lane_packet_example.py

emit-gemini-packet-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._gemini_lane_packet_example

revalidate-openai-packet:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_lane_packet_example.py

emit-openai-packet-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._openai_lane_packet_example

revalidate-latency-evidence:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_lane_latency.py

emit-latency-evidence-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_lane_latency_evidence

revalidate-mediation-evidence-package:
	$(ROOT_PYTEST) tests/archive/test_mediation_evidence_package.py -q
	$(ROOT_PYTHON) lab/mediation_evidence_package.py --check

revalidate-mediation-reference-host-realization-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_reference_host_realization_basis.py -q

revalidate-mediation-gemini-host-realization-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_gemini_host_realization_basis.py -q

revalidate-mediation-openai-host-realization-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_openai_host_realization_basis.py -q

revalidate-mediation-run-packets:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_run_packets.py -q

revalidate-reference-mediation-baselines:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediation_baseline_packets.py -q

emit-reference-mediation-baselines-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_mediation_baseline_packets

revalidate-reference-mediated-host-realization:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_lane_packet_example.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_host_realization_comparator.py -q

emit-reference-mediated-host-realization-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_mediation_host_realization_experimental

revalidate-gemini-mediated-host-realization:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_mediated_lane_packet_example.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_mediated_host_realization_comparator.py -q

emit-gemini-mediated-host-realization-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._gemini_mediation_host_realization_experimental

revalidate-openai-mediated-host-realization:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_lane_packet_example.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_host_realization_comparator.py -q

emit-openai-mediated-host-realization-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._openai_mediation_host_realization_experimental

revalidate-gemini-mediation-baselines:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_mediation_baseline_packets.py -q

emit-gemini-mediation-baselines-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._gemini_mediation_baseline_packets

revalidate-openai-mediation-baselines:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediation_baseline_packets.py -q

emit-openai-mediation-baselines-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._openai_mediation_baseline_packets

revalidate-openai-mediated-uncertainty:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_uncertainty_comparator.py -q

emit-openai-mediated-uncertainty-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._openai_mediation_uncertainty_experimental

revalidate-openai-mediated-thrash:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_thrash_comparator.py -q

emit-openai-mediated-thrash-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._openai_mediation_thrash_experimental

revalidate-gemini-mediated-uncertainty:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_mediated_uncertainty_comparator.py -q

emit-gemini-mediated-uncertainty-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._gemini_mediation_uncertainty_experimental

revalidate-gemini-mediated-thrash:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_gemini_mediated_thrash_comparator.py -q

emit-gemini-mediated-thrash-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._gemini_mediation_thrash_experimental

revalidate-reference-mediated-thrash:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_thrash_comparator.py -q

emit-reference-mediated-thrash-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_mediation_thrash_experimental

revalidate-reference-mediated-uncertainty:
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_uncertainty_comparator.py -q

emit-reference-mediated-uncertainty-candidate:
	$(ROOT_PYTHON) -m tests.archive.legacy_integration._reference_mediation_uncertainty_experimental

revalidate-mediation-reference-thrash-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_reference_thrash_basis.py -q

revalidate-mediation-reference-uncertainty-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_reference_uncertainty_basis.py -q

revalidate-mediation-gemini-uncertainty-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_gemini_uncertainty_basis.py -q

revalidate-mediation-gemini-thrash-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_gemini_thrash_basis.py -q

revalidate-mediation-openai-uncertainty-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_openai_uncertainty_basis.py -q

revalidate-mediation-openai-thrash-basis:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_openai_thrash_basis.py -q

revalidate-mediation-branch-discipline:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_reference_branch_discipline_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_openai_branch_discipline_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_claude_branch_discipline_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_branch_discipline_comparator.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_branch_discipline_comparator.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_claude_mediated_branch_discipline_comparator.py -q

revalidate-mediation-non-thrash-burden:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_reference_non_thrash_burden_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_openai_non_thrash_burden_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_claude_non_thrash_burden_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_reference_mediated_non_thrash_burden_comparator.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_openai_mediated_non_thrash_burden_comparator.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_claude_mediated_non_thrash_burden_comparator.py -q

revalidate-mediation-claude-host-realization:
	$(ROOT_PYTEST) tests/archive/legacy_unit/test_mediation_claude_host_realization_basis.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_claude_lane_packet_example.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_claude_mediated_lane_packet_example.py -q
	$(ROOT_PYTEST) tests/archive/legacy_integration/test_claude_mediated_host_realization_comparator.py -q

revalidate-mediation-claude-uncertainty:
	@echo "revalidate-mediation-claude-uncertainty: no committed Claude uncertainty package on the current line"

revalidate-mediation-evidence:
	$(MAKE) revalidate-mediation-evidence-package
	$(MAKE) revalidate-mediation-branch-discipline
	$(MAKE) revalidate-mediation-non-thrash-burden
	$(MAKE) revalidate-mediation-claude-host-realization
	$(MAKE) revalidate-mediation-reference-host-realization-basis
	$(MAKE) revalidate-mediation-gemini-host-realization-basis
	$(MAKE) revalidate-mediation-openai-host-realization-basis
	$(MAKE) revalidate-reference-mediated-host-realization
	$(MAKE) revalidate-gemini-mediated-host-realization
	$(MAKE) revalidate-openai-mediated-host-realization
	$(MAKE) revalidate-gemini-packet
	$(MAKE) revalidate-openai-packet
	$(MAKE) revalidate-mediation-run-packets
	$(MAKE) revalidate-reference-mediation-baselines
	$(MAKE) revalidate-gemini-mediation-baselines
	$(MAKE) revalidate-openai-mediation-baselines
	$(MAKE) revalidate-gemini-mediated-thrash
	$(MAKE) revalidate-gemini-mediated-uncertainty
	$(MAKE) revalidate-openai-mediated-uncertainty
	$(MAKE) revalidate-openai-mediated-thrash
	$(MAKE) revalidate-reference-mediated-uncertainty
	$(MAKE) revalidate-reference-mediated-thrash
	$(MAKE) revalidate-mediation-gemini-thrash-basis
	$(MAKE) revalidate-mediation-gemini-uncertainty-basis
	$(MAKE) revalidate-mediation-openai-thrash-basis
	$(MAKE) revalidate-mediation-openai-uncertainty-basis
	$(MAKE) revalidate-mediation-reference-uncertainty-basis
	$(MAKE) revalidate-mediation-reference-thrash-basis

revalidate-mediation-justification:
	$(MAKE) revalidate-mediation-evidence
	$(ROOT_PYTEST) tests/internal/test_docs_boundary.py -q

coverage:
	$(ROOT_COVERAGE) --version >/dev/null 2>&1 || { \
		echo "coverage tool unavailable: install a package that provides 'python3 -m coverage'"; \
		exit 1; \
	}
	$(ROOT_COVERAGE) run --rcfile=$(COVERAGE_RC) -m pytest
	$(ROOT_COVERAGE) report --rcfile=$(COVERAGE_RC)

test-correspondence-core:
	$(ROOT_PYTEST) tests/archive/test_correspondence_core.py

test-correspondence-contract:
	$(ROOT_PYTEST) tests/archive/test_correspondence_contract.py

test-correspondence-ports:
	$(ROOT_PYTEST) tests/archive/test_correspondence_ports.py

test-correspondence-sre:
	$(ROOT_PYTEST) tests/archive/test_correspondence_sre.py

test-correspondence-periphery:
	$(ROOT_PYTEST) tests/archive/test_correspondence_periphery.py
