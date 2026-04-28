"""Conservative output-closure assessment for Cortex product surfaces."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ClosureAssessmentStatus(str, Enum):
    NO_CLAIM = "no_claim"
    SUPPORTED = "supported"
    UNCERTIFIED = "uncertified"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ClosureAssessment:
    status: ClosureAssessmentStatus
    claim_detected: bool
    completion_claimed: bool
    verification_claimed: bool
    broad_product_claimed: bool
    refusal_or_limitation_present: bool
    reasons: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "claim_detected": self.claim_detected,
            "completion_claimed": self.completion_claimed,
            "verification_claimed": self.verification_claimed,
            "broad_product_claimed": self.broad_product_claimed,
            "refusal_or_limitation_present": self.refusal_or_limitation_present,
            "reasons": list(self.reasons),
        }


def assess_output_closure(
    result_text: str | None,
    *,
    commitment_result_kinds: Sequence[str | None] = (),
    verification_passed: bool | None = None,
    blocker_present: bool = False,
) -> ClosureAssessment:
    text = _normalized_text(result_text)
    if not text:
        return ClosureAssessment(
            status=ClosureAssessmentStatus.NO_CLAIM,
            claim_detected=False,
            completion_claimed=False,
            verification_claimed=False,
            broad_product_claimed=False,
            refusal_or_limitation_present=False,
        )
    completion_claimed = _contains_any(
        text,
        ("complete", "completed", "done", "finished", "fully fixed"),
    )
    verification_claimed = _contains_any(
        text,
        ("verified", "tests pass", "test passed", "green", "verification passed"),
    )
    broad_product_claimed = _contains_any(
        text,
        (
            "fully proven",
            "all hosts are proven",
            "proves every host",
            "product perfection",
            "generally improves models",
            "fully optimized across",
        ),
    )
    refusal_or_limitation_present = _contains_any(
        text,
        (
            "cannot claim",
            "can't claim",
            "can't truthfully claim",
            "can’t truthfully claim",
            "unsupported",
            "not supported",
            "not enough evidence",
            "unverified",
            "incomplete",
            "blocked",
        ),
    )
    claim_detected = completion_claimed or verification_claimed or broad_product_claimed
    if not claim_detected:
        return ClosureAssessment(
            status=ClosureAssessmentStatus.NO_CLAIM,
            claim_detected=False,
            completion_claimed=False,
            verification_claimed=False,
            broad_product_claimed=False,
            refusal_or_limitation_present=refusal_or_limitation_present,
        )

    reasons: list[str] = []
    if broad_product_claimed and not refusal_or_limitation_present:
        reasons.append("broad_product_claim_without_evidence")
    if verification_claimed and verification_passed is not True:
        reasons.append("verification_claim_without_passing_verification")
    certified_commitment = any(kind == "certified" for kind in commitment_result_kinds)
    if completion_claimed and not certified_commitment and verification_passed is not True:
        reasons.append("completion_claim_without_certification_or_verification")
    if blocker_present and completion_claimed and not refusal_or_limitation_present:
        reasons.append("completion_claim_hides_blocker")

    if reasons:
        return ClosureAssessment(
            status=ClosureAssessmentStatus.BLOCKED,
            claim_detected=True,
            completion_claimed=completion_claimed,
            verification_claimed=verification_claimed,
            broad_product_claimed=broad_product_claimed,
            refusal_or_limitation_present=refusal_or_limitation_present,
            reasons=tuple(reasons),
        )
    return ClosureAssessment(
        status=ClosureAssessmentStatus.SUPPORTED,
        claim_detected=True,
        completion_claimed=completion_claimed,
        verification_claimed=verification_claimed,
        broad_product_claimed=broad_product_claimed,
        refusal_or_limitation_present=refusal_or_limitation_present,
    )


def _normalized_text(value: str | None) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"result_text must be str | None, got {actual_type}.")
    return " ".join(value.lower().strip().split())


def _contains_any(value: str, needles: tuple[str, ...]) -> bool:
    return any(needle in value for needle in needles)


__all__ = [
    "ClosureAssessment",
    "ClosureAssessmentStatus",
    "assess_output_closure",
]
