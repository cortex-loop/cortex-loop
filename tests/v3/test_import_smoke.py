"""Import smoke tests for the Cortex v3 incubation surface."""

from importlib import import_module

import pytest


IMPORT_TARGETS = [
    "cortex_v3",
    "cortex_v3.contracts",
    "cortex_v3.preservation",
    "cortex_v3.verifier",
    "cortex_v3.engine",
    "cortex_v3.providers",
    "cortex_v3.providers.base",
    "cortex_v3.providers.openai",
    "cortex_v3.providers.openai.adapter",
    "cortex_v3.providers.claude",
    "cortex_v3.providers.claude.adapter",
    "cortex_v3.providers.gemini",
    "cortex_v3.providers.gemini.adapter",
]


@pytest.mark.parametrize("module_name", IMPORT_TARGETS)
def test_v3_import_smoke(module_name: str) -> None:
    module = import_module(module_name)

    assert module.__name__ == module_name
