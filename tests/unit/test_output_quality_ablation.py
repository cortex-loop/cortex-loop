"""Focused tests for the output-quality ablation config."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from output_quality_ablation import OutputQualityAblationConfig


def test_output_quality_ablation_config_defaults_match_accepted_control() -> None:
    config = OutputQualityAblationConfig()

    assert config.is_default() is True
    assert config.as_payload() == {
        "visible_contract_binding": "on",
        "verification_binding": "on",
        "repair_turn": "on",
        "repair_ticket_style": "factual",
        "visible_context_variant": "default",
    }


def test_output_quality_ablation_config_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="visible_contract_binding"):
        OutputQualityAblationConfig(visible_contract_binding="bad")  # type: ignore[arg-type]
