"""Import smoke tests for the Phase 1 package skeleton."""

from importlib import import_module

import pytest


IMPORT_TARGETS = [
    "cortex",
    "cortex.core",
    "cortex.sre",
    "cortex.aux",
    "cortex.drivers",
    "cortex.runtime",
    "cortex.runtime.openai",
    "cortex.runtime.openai_cli",
    "cortex.runtime.openai_session_io",
    "cortex.eval",
    "cortex.core.lifecycle",
    "cortex.core.envelopes",
    "cortex.core.observation",
    "cortex.core.environment",
    "cortex.core.support",
    "cortex.core.commitments",
    "cortex.core.errors",
    "cortex.eval.artifacts",
    "cortex.eval.packets",
]


@pytest.mark.parametrize("module_name", IMPORT_TARGETS)
def test_import_smoke(module_name: str) -> None:
    """All Phase 1 package boundaries and shell modules should import cleanly."""

    module = import_module(module_name)

    assert module.__name__ == module_name
