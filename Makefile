PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
MAKE ?= make
ARGS ?=

LAB_ALIAS_TARGETS := test-unit test-integration test-smoke verify seam-preflight live-preflight live-preflight-update live-provider-baselines live-provider-baselines-automation live-host-native-product-paths live-openai-app-server live-cortex-host-control live-compare live-operator-payoff-audit live-operator-directionality live-operator-directionality-audit v2-adoption-review conformance-preflight conformance-fast conformance-active revalidate-reference-runtime revalidate-reference-runtime-continuity revalidate-openai-runtime revalidate-openai-ingress revalidate-openai-service revalidate-openai-host-control revalidate-executive-loop revalidate-gemini-runtime revalidate-gemini-ingress revalidate-gemini-service revalidate-gemini-host-control revalidate-claude-runtime revalidate-claude-ingress revalidate-claude-service revalidate-claude-host-control revalidate-reference-packet emit-reference-packet-candidate revalidate-gemini-packet emit-gemini-packet-candidate revalidate-openai-packet emit-openai-packet-candidate revalidate-latency-evidence emit-latency-evidence-candidate revalidate-mediation-evidence-package revalidate-mediation-run-packets revalidate-reference-mediation-baselines emit-reference-mediation-baselines-candidate revalidate-gemini-mediation-baselines emit-gemini-mediation-baselines-candidate revalidate-openai-mediation-baselines emit-openai-mediation-baselines-candidate revalidate-reference-mediated-host-realization emit-reference-mediated-host-realization-candidate revalidate-gemini-mediated-host-realization emit-gemini-mediated-host-realization-candidate revalidate-openai-mediated-host-realization emit-openai-mediated-host-realization-candidate revalidate-reference-mediated-thrash emit-reference-mediated-thrash-candidate revalidate-reference-mediated-uncertainty emit-reference-mediated-uncertainty-candidate revalidate-gemini-mediated-uncertainty emit-gemini-mediated-uncertainty-candidate revalidate-gemini-mediated-thrash emit-gemini-mediated-thrash-candidate revalidate-openai-mediated-uncertainty emit-openai-mediated-uncertainty-candidate revalidate-openai-mediated-thrash emit-openai-mediated-thrash-candidate revalidate-mediation-reference-host-realization-basis revalidate-mediation-gemini-host-realization-basis revalidate-mediation-openai-host-realization-basis revalidate-mediation-reference-thrash-basis revalidate-mediation-reference-uncertainty-basis revalidate-mediation-gemini-thrash-basis revalidate-mediation-gemini-uncertainty-basis revalidate-mediation-openai-thrash-basis revalidate-mediation-openai-uncertainty-basis revalidate-mediation-branch-discipline revalidate-mediation-non-thrash-burden revalidate-mediation-claude-host-realization revalidate-mediation-claude-uncertainty revalidate-mediation-evidence revalidate-mediation-justification coverage test-correspondence-contract test-correspondence-core test-correspondence-ports test-correspondence-sre test-correspondence-periphery

.PHONY: product-test conformance-test experimental-test lab-test archive-test product-openai-cli product-openai-service repo-hygiene $(LAB_ALIAS_TARGETS)

product-test:
	$(PYTEST) tests/product -q

conformance-test:
	$(PYTEST) tests/conformance -q

product-openai-cli:
	$(PYTHON) -m cortex.hosts.openai.cli $(ARGS)

product-openai-service:
	$(PYTHON) -m cortex.hosts.openai.service $(ARGS)

experimental-test:
	$(PYTEST) tests/experimental -q

lab-test:
	$(PYTEST) tests/lab -q

archive-test:
	$(PYTEST) tests/archive -q

repo-hygiene:
	@echo "make repo-hygiene is internal and deprecated; use make -C internal cleanup-report"
	@$(MAKE) -C internal cleanup-report

$(LAB_ALIAS_TARGETS):
	@echo "make $@ is internal and deprecated; use make -C lab $@"
	@$(MAKE) -C lab $@
