"""Shared operator-brain capability registry for bounded capability adaptation.

The SRE-side capability mechanism (`OperatorBrainCapabilityEnvelope`,
`assess_operator_brain_capability`, threshold ladder, routing consequences)
is host-agnostic: per-host band registries may differ but the assessment
math and the routing consequences must be identical across hosts (see
SRE_2 §6.9.4 — forbidden moves).

Currently only OpenAI has a populated band registry below; Claude, Gemini,
and reference hosts return the standard envelope by default until per-host
registries earn their own seam. This is intentional, not an oversight: the
brain-capability-aware-routing seam earned the SRE-side mechanism on the
OpenAI lane first, and the per-host registries are queued as a follow-up
under the same bio_to_code skill (Intervention pricing versus neutrality).

The dynamic-detection follow-up seam
(`brain-capability-observation-and-inference`, see
`internal/truth/cortex_status.json::next_product_train`) will replace the
static name-based lookup with an observed-performance accumulator whose
inference function produces the same `OperatorBrainCapabilityEnvelope`
shape; the SRE-side assessment math and routing consequences are reusable
unchanged when inference replaces lookup.
"""

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
