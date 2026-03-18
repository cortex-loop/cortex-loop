PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
COVERAGE ?= $(PYTHON) -m coverage
COVERAGE_RC ?= .coveragerc

.PHONY: test-unit test-integration test-smoke verify coverage test-correspondence-core test-correspondence-sre test-correspondence-periphery

test-unit:
	$(PYTEST) tests/unit

test-integration:
	$(PYTEST) tests/integration

test-smoke:
	$(PYTEST) tests/unit/test_import_smoke.py \
		tests/integration/test_reference_host_vertical_gate.py::test_driver_to_core_to_sre_smoke_stays_observe_bind_dispatch_and_neutral

verify:
	$(PYTEST) tests/unit
	$(PYTEST) tests/integration
	$(PYTEST) tests/unit/test_import_smoke.py

coverage:
	$(COVERAGE) --version >/dev/null 2>&1 || { \
		echo "coverage tool unavailable: install a package that provides 'python3 -m coverage'"; \
		exit 1; \
	}
	$(COVERAGE) run --rcfile=$(COVERAGE_RC) -m pytest
	$(COVERAGE) report --rcfile=$(COVERAGE_RC)

test-correspondence-core:
	$(PYTEST) tests/unit/test_correspondence_core.py

test-correspondence-sre:
	$(PYTEST) tests/unit/test_correspondence_sre.py

test-correspondence-periphery:
	$(PYTEST) tests/unit/test_correspondence_periphery.py
