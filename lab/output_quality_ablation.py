"""Internal-only ablation config for the E12 output-quality harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


VisibleContractBinding = Literal["on", "off"]
VerificationBinding = Literal["on", "off"]
RepairTurn = Literal["on", "off"]
RepairTicketStyle = Literal["factual", "minimal"]
VisibleContextVariant = Literal[
    "default",
    "writable_files_only",
    "writable_files_plus_visible_tests",
]


@dataclass(frozen=True, slots=True)
class OutputQualityAblationConfig:
    visible_contract_binding: VisibleContractBinding = "on"
    verification_binding: VerificationBinding = "on"
    repair_turn: RepairTurn = "on"
    repair_ticket_style: RepairTicketStyle = "factual"
    visible_context_variant: VisibleContextVariant = "default"

    def __post_init__(self) -> None:
        if self.visible_contract_binding not in {"on", "off"}:
            raise ValueError(
                "OutputQualityAblationConfig.visible_contract_binding must be `on` or `off`."
            )
        if self.verification_binding not in {"on", "off"}:
            raise ValueError(
                "OutputQualityAblationConfig.verification_binding must be `on` or `off`."
            )
        if self.repair_turn not in {"on", "off"}:
            raise ValueError("OutputQualityAblationConfig.repair_turn must be `on` or `off`.")
        if self.repair_ticket_style not in {"factual", "minimal"}:
            raise ValueError(
                "OutputQualityAblationConfig.repair_ticket_style must be `factual` or `minimal`."
            )
        if self.visible_context_variant not in {
            "default",
            "writable_files_only",
            "writable_files_plus_visible_tests",
        }:
            raise ValueError(
                "OutputQualityAblationConfig.visible_context_variant must be accepted."
            )

    def is_default(self) -> bool:
        return (
            self.visible_contract_binding == "on"
            and self.verification_binding == "on"
            and self.repair_turn == "on"
            and self.repair_ticket_style == "factual"
            and self.visible_context_variant == "default"
        )

    def as_payload(self) -> dict[str, str]:
        return {
            "visible_contract_binding": self.visible_contract_binding,
            "verification_binding": self.verification_binding,
            "repair_turn": self.repair_turn,
            "repair_ticket_style": self.repair_ticket_style,
            "visible_context_variant": self.visible_context_variant,
        }


__all__ = ["OutputQualityAblationConfig"]
