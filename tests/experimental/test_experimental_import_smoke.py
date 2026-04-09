"""Import smoke tests for the public non-shipping experimental surface."""

from importlib import import_module

import pytest


IMPORT_TARGETS = [
    "experimental",
    "experimental.drivers",
    "experimental.drivers.claude_host",
    "experimental.drivers.claude_host_commitment",
    "experimental.drivers.claude_host_neutral",
    "experimental.drivers.gemini_host",
    "experimental.drivers.gemini_host_commitment",
    "experimental.drivers.gemini_host_neutral",
    "experimental.drivers.reference_host",
    "experimental.drivers.reference_host_commitment",
    "experimental.drivers.reference_host_neutral",
    "experimental.eval",
    "experimental.eval.artifacts",
    "experimental.eval.harness",
    "experimental.eval.packets",
    "experimental.sre",
    "experimental.sre.allocation",
    "experimental.sre.brake",
    "experimental.sre.executive_summary",
    "experimental.sre.families",
    "experimental.sre.feedback",
    "experimental.sre.goals",
    "experimental.sre.mediation",
    "experimental.sre.modulators",
    "experimental.sre.operator_routing",
    "experimental.sre.opportunities",
    "experimental.sre.policy",
    "experimental.sre.policy_view",
    "experimental.sre.reference_builder",
    "experimental.sre.reference_scoring",
    "experimental.sre.state",
    "experimental.sre.uncertainty",
    "experimental.runtime",
    "experimental.runtime.claude",
    "experimental.runtime.claude_cli",
    "experimental.runtime.claude_host_control",
    "experimental.runtime.claude_host_transport",
    "experimental.runtime.claude_ingress",
    "experimental.runtime.claude_ingress_cli",
    "experimental.runtime.claude_service",
    "experimental.runtime.claude_session_io",
    "experimental.runtime.gemini",
    "experimental.runtime.gemini_cli",
    "experimental.runtime.gemini_host_control",
    "experimental.runtime.gemini_host_transport",
    "experimental.runtime.gemini_ingress",
    "experimental.runtime.gemini_ingress_cli",
    "experimental.runtime.gemini_service",
    "experimental.runtime.gemini_session_io",
    "experimental.runtime.reference",
    "experimental.runtime.reference_cli",
    "experimental.runtime.reference_session_io",
]


@pytest.mark.parametrize("module_name", IMPORT_TARGETS)
def test_experimental_import_smoke(module_name: str) -> None:
    module = import_module(module_name)

    assert module.__name__ == module_name
