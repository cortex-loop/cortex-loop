"""Import smoke tests for the shipped Cortex product surface."""

from importlib import import_module

import pytest


IMPORT_TARGETS = [
    "cortex",
    "cortex.core",
    "cortex.sre",
    "cortex.sre.branching",
    "cortex.sre.verified_work",
    "cortex.aux",
    "cortex.drivers",
    "cortex.drivers.common_normalization",
    "cortex.drivers.openai_host",
    "cortex.drivers.openai_host_commitment",
    "cortex.drivers.openai_host_neutral",
    "cortex.runtime",
    "cortex.hosts.openai.runtime",
    "cortex.hosts.openai.cli",
    "cortex.hosts.openai.ingress",
    "cortex.hosts.openai.ingress_cli",
    "cortex.hosts.openai.host_control",
    "cortex.hosts.openai.host_transport",
    "cortex.hosts.openai.service",
    "cortex.hosts.openai.session_io",
    "cortex.runtime.verified_work_runtime",
    "cortex.core.lifecycle",
    "cortex.core.envelopes",
    "cortex.core.observation",
    "cortex.core.environment",
    "cortex.core.support",
    "cortex.core.commitments",
    "cortex.core.errors",
]


@pytest.mark.parametrize("module_name", IMPORT_TARGETS)
def test_product_import_smoke(module_name: str) -> None:
    module = import_module(module_name)

    assert module.__name__ == module_name
