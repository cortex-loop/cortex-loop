"""Import smoke tests for active host conformance surfaces."""

from importlib import import_module

import pytest


IMPORT_TARGETS = [
    "cortex.drivers",
    "cortex.drivers.claude_host",
    "cortex.drivers.claude_host_commitment",
    "cortex.drivers.claude_host_neutral",
    "cortex.drivers.gemini_host",
    "cortex.drivers.gemini_host_commitment",
    "cortex.drivers.gemini_host_neutral",
    "cortex.drivers.reference_host",
    "cortex.drivers.reference_host_commitment",
    "cortex.drivers.reference_host_neutral",
    "cortex.hosts",
    "cortex.sre",
    "cortex.sre.allocation",
    "cortex.sre.brake",
    "cortex.sre.executive_summary",
    "cortex.sre.families",
    "cortex.sre.feedback",
    "cortex.sre.goals",
    "cortex.sre.mediation",
    "cortex.sre.modulators",
    "cortex.sre.operator_routing",
    "cortex.sre.opportunities",
    "cortex.sre.policy",
    "cortex.sre.policy_view",
    "cortex.sre.reference_builder",
    "cortex.sre.reference_scoring",
    "cortex.sre.state",
    "cortex.sre.uncertainty",
    "cortex.hosts.openai.runtime",
    "cortex.hosts.openai.service",
    "cortex.hosts.claude.runtime",
    "cortex.hosts.claude.host_control",
    "cortex.hosts.claude.ingress",
    "cortex.hosts.claude.service",
    "cortex.hosts.claude.session_io",
    "cortex.hosts.gemini.runtime",
    "cortex.hosts.gemini.host_control",
    "cortex.hosts.gemini.ingress",
    "cortex.hosts.gemini.service",
    "cortex.hosts.gemini.session_io",
    "cortex.hosts.reference.runtime",
    "cortex.hosts.reference.session_io",
]


@pytest.mark.parametrize("module_name", IMPORT_TARGETS)
def test_host_import_smoke(module_name: str) -> None:
    module = import_module(module_name)

    assert module.__name__ == module_name
