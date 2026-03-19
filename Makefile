PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
COVERAGE ?= $(PYTHON) -m coverage
COVERAGE_RC ?= .coveragerc

.PHONY: test-unit test-integration test-smoke verify revalidate-reference-packet emit-reference-packet-candidate revalidate-latency-evidence emit-latency-evidence-candidate coverage test-correspondence-core test-correspondence-ports test-correspondence-sre test-correspondence-periphery

test-unit:
	$(PYTEST) tests/unit

test-integration:
	$(PYTEST) tests/integration

test-smoke:
	$(PYTEST) tests/unit/test_correspondence_core.py \
		tests/unit/test_correspondence_ports.py \
		tests/unit/test_correspondence_sre.py \
		tests/unit/test_correspondence_periphery.py \
		tests/integration/test_reference_host_vertical_gate.py \
		tests/integration/test_reference_lane_latency.py \
		tests/integration/test_reference_lane_packet_example.py \
		tests/integration/test_aux_claim_conservative.py \
		tests/unit/test_import_smoke.py -q

verify:
	$(PYTEST) tests/unit -q
	$(PYTEST) tests/integration -q
	$(PYTEST) tests/unit/test_import_smoke.py -q

revalidate-reference-packet:
	$(PYTEST) tests/integration/test_reference_lane_packet_example.py

emit-reference-packet-candidate:
	$(PYTHON) -m tests.integration._reference_lane_packet_example

revalidate-latency-evidence:
	$(PYTEST) tests/integration/test_reference_lane_latency.py

emit-latency-evidence-candidate:
	$(PYTHON) -m tests.integration._reference_lane_latency_evidence

coverage:
	$(COVERAGE) --version >/dev/null 2>&1 || { \
		echo "coverage tool unavailable: install a package that provides 'python3 -m coverage'"; \
		exit 1; \
	}
	$(COVERAGE) run --rcfile=$(COVERAGE_RC) -m pytest
	$(COVERAGE) report --rcfile=$(COVERAGE_RC)

test-correspondence-core:
	$(PYTEST) tests/unit/test_correspondence_core.py

test-correspondence-ports:
	$(PYTEST) tests/unit/test_correspondence_ports.py

test-correspondence-sre:
	$(PYTEST) tests/unit/test_correspondence_sre.py

test-correspondence-periphery:
	$(PYTEST) tests/unit/test_correspondence_periphery.py
