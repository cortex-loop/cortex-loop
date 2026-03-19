"""Private helpers shared by neutral-only driver slices."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from cortex.core.dispatch import DispatchLane

NeutralCodeT = TypeVar("NeutralCodeT")


def extract_native_commitment_fields(payload: Mapping[str, Any]) -> Any | None:
    if payload.get("commitment_fields_source") != "native":
        return None
    if "commitment_fields" not in payload:
        return None
    return payload.get("commitment_fields")


def merge_warnings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    warnings: list[str] = []
    for group in groups:
        for warning in group:
            if warning not in warnings:
                warnings.append(warning)
    return tuple(warnings)


def neutral_outcome_for_lane(
    lane: DispatchLane,
    *,
    cheap_code: NeutralCodeT,
    candidate_code: NeutralCodeT,
    full_commitment_code: NeutralCodeT,
) -> tuple[bool, NeutralCodeT]:
    if lane is DispatchLane.CHEAP:
        return True, cheap_code
    if lane is DispatchLane.CANDIDATE_BEARING:
        return False, candidate_code
    return False, full_commitment_code
