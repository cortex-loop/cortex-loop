PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
COVERAGE ?= $(PYTHON) -m coverage
COVERAGE_RC ?= .coveragerc

.PHONY: test-unit test-integration test-smoke verify seam-preflight revalidate-reference-runtime revalidate-reference-runtime-continuity revalidate-openai-runtime revalidate-openai-ingress revalidate-openai-service revalidate-openai-host-control revalidate-executive-loop revalidate-reference-packet emit-reference-packet-candidate revalidate-gemini-packet emit-gemini-packet-candidate revalidate-openai-packet emit-openai-packet-candidate revalidate-latency-evidence emit-latency-evidence-candidate revalidate-mediation-evidence-package revalidate-mediation-run-packets revalidate-reference-mediation-baselines emit-reference-mediation-baselines-candidate revalidate-gemini-mediation-baselines emit-gemini-mediation-baselines-candidate revalidate-openai-mediation-baselines emit-openai-mediation-baselines-candidate revalidate-reference-mediated-host-realization emit-reference-mediated-host-realization-candidate revalidate-gemini-mediated-host-realization emit-gemini-mediated-host-realization-candidate revalidate-openai-mediated-host-realization emit-openai-mediated-host-realization-candidate revalidate-reference-mediated-thrash emit-reference-mediated-thrash-candidate revalidate-reference-mediated-uncertainty emit-reference-mediated-uncertainty-candidate revalidate-gemini-mediated-uncertainty emit-gemini-mediated-uncertainty-candidate revalidate-gemini-mediated-thrash emit-gemini-mediated-thrash-candidate revalidate-openai-mediated-uncertainty emit-openai-mediated-uncertainty-candidate revalidate-openai-mediated-thrash emit-openai-mediated-thrash-candidate revalidate-mediation-reference-host-realization-basis revalidate-mediation-gemini-host-realization-basis revalidate-mediation-openai-host-realization-basis revalidate-mediation-reference-thrash-basis revalidate-mediation-reference-uncertainty-basis revalidate-mediation-gemini-thrash-basis revalidate-mediation-gemini-uncertainty-basis revalidate-mediation-openai-thrash-basis revalidate-mediation-openai-uncertainty-basis revalidate-mediation-evidence coverage test-correspondence-contract test-correspondence-core test-correspondence-ports test-correspondence-sre test-correspondence-periphery

test-unit:
	$(PYTEST) tests/unit

test-integration:
	$(PYTEST) tests/integration

test-smoke:
	$(PYTEST) tests/unit/test_correspondence_contract.py \
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

verify:
	$(PYTEST) tests/unit -q
	$(PYTEST) tests/integration -q
	$(PYTEST) tests/unit/test_import_smoke.py -q

revalidate-reference-runtime:
	$(PYTEST) tests/unit/test_reference_runtime_step.py -q
	$(PYTEST) tests/unit/test_reference_executive_builder.py -q
	$(PYTEST) tests/unit/test_reference_runtime_scoring.py -q
	$(PYTEST) tests/unit/test_reference_realization_feedback.py -q
	$(PYTEST) tests/unit/test_reference_feedback_window.py -q
	$(PYTEST) tests/integration/test_reference_runtime_cli.py -q

revalidate-reference-runtime-continuity:
	$(PYTEST) tests/unit/test_reference_runtime_session_io.py -q
	$(PYTEST) tests/integration/test_reference_runtime_cli.py -q
	$(PYTEST) tests/integration/test_reference_runtime_continuity.py -q

revalidate-openai-runtime:
	$(PYTEST) tests/unit/test_openai_runtime_session_io.py -q
	$(PYTEST) tests/unit/test_openai_runtime_step.py -q
	$(PYTEST) tests/unit/test_openai_runtime_ownership.py -q
	$(PYTEST) tests/integration/test_openai_runtime_cli.py -q
	$(PYTEST) tests/integration/test_openai_runtime_continuity.py -q

revalidate-openai-ingress:
	$(PYTEST) tests/unit/test_openai_ingress.py -q
	$(PYTEST) tests/integration/test_openai_ingress_cli.py -q
	$(PYTEST) tests/integration/test_openai_ingress_continuity.py -q

revalidate-openai-service:
	$(PYTEST) tests/unit/test_openai_service.py -q
	$(PYTEST) tests/integration/test_openai_service.py -q
	$(PYTEST) tests/integration/test_openai_service_continuity.py -q

revalidate-openai-host-control:
	$(PYTEST) tests/unit/test_openai_host_control.py -q
	$(PYTEST) tests/integration/test_openai_host_control_service.py -q
	$(PYTEST) tests/integration/test_openai_host_control_continuity.py -q

revalidate-executive-loop:
	$(PYTEST) tests/unit/test_sre_neutral_hinge.py -q
	$(PYTEST) tests/unit/test_reference_runtime_scoring.py -q
	$(PYTEST) tests/unit/test_reference_runtime_step.py -q
	$(PYTEST) tests/integration/test_reference_runtime_cli.py -q
	$(PYTEST) tests/integration/test_openai_runtime_cli.py -q
	$(PYTEST) tests/integration/test_openai_ingress_cli.py -q
	$(PYTEST) tests/integration/test_openai_service.py -q
	$(PYTEST) tests/integration/test_openai_host_control_service.py -q
	$(PYTEST) tests/integration/test_openai_host_control_continuity.py -q

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

revalidate-reference-packet:
	$(PYTEST) tests/integration/test_reference_lane_packet_example.py

emit-reference-packet-candidate:
	$(PYTHON) -m tests.integration._reference_lane_packet_example

revalidate-gemini-packet:
	$(PYTEST) tests/integration/test_gemini_lane_packet_example.py

emit-gemini-packet-candidate:
	$(PYTHON) -m tests.integration._gemini_lane_packet_example

revalidate-openai-packet:
	$(PYTEST) tests/integration/test_openai_lane_packet_example.py

emit-openai-packet-candidate:
	$(PYTHON) -m tests.integration._openai_lane_packet_example

revalidate-latency-evidence:
	$(PYTEST) tests/integration/test_reference_lane_latency.py

emit-latency-evidence-candidate:
	$(PYTHON) -m tests.integration._reference_lane_latency_evidence

revalidate-mediation-evidence-package:
	$(PYTEST) tests/unit/test_mediation_evidence_package.py -q

revalidate-mediation-reference-host-realization-basis:
	$(PYTEST) tests/unit/test_mediation_reference_host_realization_basis.py -q

revalidate-mediation-gemini-host-realization-basis:
	$(PYTEST) tests/unit/test_mediation_gemini_host_realization_basis.py -q

revalidate-mediation-openai-host-realization-basis:
	$(PYTEST) tests/unit/test_mediation_openai_host_realization_basis.py -q

revalidate-mediation-run-packets:
	$(PYTEST) tests/unit/test_mediation_run_packets.py -q

revalidate-reference-mediation-baselines:
	$(PYTEST) tests/integration/test_reference_mediation_baseline_packets.py -q

emit-reference-mediation-baselines-candidate:
	$(PYTHON) -m tests.integration._reference_mediation_baseline_packets

revalidate-reference-mediated-host-realization:
	$(PYTEST) tests/integration/test_reference_mediated_lane_packet_example.py -q
	$(PYTEST) tests/integration/test_reference_mediated_host_realization_comparator.py -q

emit-reference-mediated-host-realization-candidate:
	$(PYTHON) -m tests.integration._reference_mediation_host_realization_experimental

revalidate-gemini-mediated-host-realization:
	$(PYTEST) tests/integration/test_gemini_mediated_lane_packet_example.py -q
	$(PYTEST) tests/integration/test_gemini_mediated_host_realization_comparator.py -q

emit-gemini-mediated-host-realization-candidate:
	$(PYTHON) -m tests.integration._gemini_mediation_host_realization_experimental

revalidate-openai-mediated-host-realization:
	$(PYTEST) tests/integration/test_openai_mediated_lane_packet_example.py -q
	$(PYTEST) tests/integration/test_openai_mediated_host_realization_comparator.py -q

emit-openai-mediated-host-realization-candidate:
	$(PYTHON) -m tests.integration._openai_mediation_host_realization_experimental

revalidate-gemini-mediation-baselines:
	$(PYTEST) tests/integration/test_gemini_mediation_baseline_packets.py -q

emit-gemini-mediation-baselines-candidate:
	$(PYTHON) -m tests.integration._gemini_mediation_baseline_packets

revalidate-openai-mediation-baselines:
	$(PYTEST) tests/integration/test_openai_mediation_baseline_packets.py -q

emit-openai-mediation-baselines-candidate:
	$(PYTHON) -m tests.integration._openai_mediation_baseline_packets

revalidate-openai-mediated-uncertainty:
	$(PYTEST) tests/integration/test_openai_mediated_uncertainty_comparator.py -q

emit-openai-mediated-uncertainty-candidate:
	$(PYTHON) -m tests.integration._openai_mediation_uncertainty_experimental

revalidate-openai-mediated-thrash:
	$(PYTEST) tests/integration/test_openai_mediated_thrash_comparator.py -q

emit-openai-mediated-thrash-candidate:
	$(PYTHON) -m tests.integration._openai_mediation_thrash_experimental

revalidate-gemini-mediated-uncertainty:
	$(PYTEST) tests/integration/test_gemini_mediated_uncertainty_comparator.py -q

emit-gemini-mediated-uncertainty-candidate:
	$(PYTHON) -m tests.integration._gemini_mediation_uncertainty_experimental

revalidate-gemini-mediated-thrash:
	$(PYTEST) tests/integration/test_gemini_mediated_thrash_comparator.py -q

emit-gemini-mediated-thrash-candidate:
	$(PYTHON) -m tests.integration._gemini_mediation_thrash_experimental

revalidate-reference-mediated-thrash:
	$(PYTEST) tests/integration/test_reference_mediated_thrash_comparator.py -q

emit-reference-mediated-thrash-candidate:
	$(PYTHON) -m tests.integration._reference_mediation_thrash_experimental

revalidate-reference-mediated-uncertainty:
	$(PYTEST) tests/integration/test_reference_mediated_uncertainty_comparator.py -q

emit-reference-mediated-uncertainty-candidate:
	$(PYTHON) -m tests.integration._reference_mediation_uncertainty_experimental

revalidate-mediation-reference-thrash-basis:
	$(PYTEST) tests/unit/test_mediation_reference_thrash_basis.py -q

revalidate-mediation-reference-uncertainty-basis:
	$(PYTEST) tests/unit/test_mediation_reference_uncertainty_basis.py -q

revalidate-mediation-gemini-uncertainty-basis:
	$(PYTEST) tests/unit/test_mediation_gemini_uncertainty_basis.py -q

revalidate-mediation-gemini-thrash-basis:
	$(PYTEST) tests/unit/test_mediation_gemini_thrash_basis.py -q

revalidate-mediation-openai-uncertainty-basis:
	$(PYTEST) tests/unit/test_mediation_openai_uncertainty_basis.py -q

revalidate-mediation-openai-thrash-basis:
	$(PYTEST) tests/unit/test_mediation_openai_thrash_basis.py -q

revalidate-mediation-evidence:
	$(MAKE) revalidate-mediation-evidence-package
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

coverage:
	$(COVERAGE) --version >/dev/null 2>&1 || { \
		echo "coverage tool unavailable: install a package that provides 'python3 -m coverage'"; \
		exit 1; \
	}
	$(COVERAGE) run --rcfile=$(COVERAGE_RC) -m pytest
	$(COVERAGE) report --rcfile=$(COVERAGE_RC)

test-correspondence-core:
	$(PYTEST) tests/unit/test_correspondence_core.py

test-correspondence-contract:
	$(PYTEST) tests/unit/test_correspondence_contract.py

test-correspondence-ports:
	$(PYTEST) tests/unit/test_correspondence_ports.py

test-correspondence-sre:
	$(PYTEST) tests/unit/test_correspondence_sre.py

test-correspondence-periphery:
	$(PYTEST) tests/unit/test_correspondence_periphery.py
