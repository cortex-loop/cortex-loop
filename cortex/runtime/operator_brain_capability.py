"""Shared operator-brain capability registry for bounded capability adaptation."""

from __future__ import annotations

from typing import Literal

from cortex.sre.operator_routing import OperatorBrainCapabilityEnvelope


OperatorBrainCapabilityBand = Literal["frontier", "standard", "bounded"]

_BRAIN_CAPABILITY_REGISTRY: dict[
    OperatorBrainCapabilityBand, OperatorBrainCapabilityEnvelope
] = {
    "frontier": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.90,
        verification_tolerance=0.90,
        output_contract_tolerance=0.90,
    ),
    "standard": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.75,
        verification_tolerance=0.75,
        output_contract_tolerance=0.65,
    ),
    "bounded": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.45,
        verification_tolerance=0.50,
        output_contract_tolerance=0.20,
    ),
}

_OPENAI_OPERATOR_BAND_BY_MODEL = {
    "gpt-5.4": "frontier",
    "gpt-5.3-codex": "standard",
    "gpt-5.3-codex-spark": "bounded",
}


def operator_brain_capability_for_band(
    band: OperatorBrainCapabilityBand,
) -> OperatorBrainCapabilityEnvelope:
    if band not in _BRAIN_CAPABILITY_REGISTRY:
        raise ValueError(f"unsupported operator brain capability band: {band}")
    return _BRAIN_CAPABILITY_REGISTRY[band]


def operator_brain_capability_band_for_openai_model(
    model: str | None,
) -> OperatorBrainCapabilityBand:
    if not isinstance(model, str) or not model.strip():
        return "standard"
    return _OPENAI_OPERATOR_BAND_BY_MODEL.get(model.strip(), "standard")


def operator_brain_capability_for_openai_model(
    model: str | None,
) -> tuple[OperatorBrainCapabilityBand, OperatorBrainCapabilityEnvelope]:
    band = operator_brain_capability_band_for_openai_model(model)
    return band, operator_brain_capability_for_band(band)


def brain_capability_band_for_envelope(
    envelope: OperatorBrainCapabilityEnvelope,
) -> OperatorBrainCapabilityBand:
    if not isinstance(envelope, OperatorBrainCapabilityEnvelope):
        actual_type = type(envelope).__name__
        raise TypeError(
            "brain_capability_band_for_envelope.envelope must be "
            f"OperatorBrainCapabilityEnvelope, got {actual_type}."
        )
    for band, candidate in _BRAIN_CAPABILITY_REGISTRY.items():
        if envelope == candidate:
            return band
    return "standard"


__all__ = [
    "OperatorBrainCapabilityBand",
    "brain_capability_band_for_envelope",
    "operator_brain_capability_band_for_openai_model",
    "operator_brain_capability_for_band",
    "operator_brain_capability_for_openai_model",
]
