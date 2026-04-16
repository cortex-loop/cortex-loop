"""Small typed allocation-score carriers for neutral-dominance checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Mapping

from .brake import BrakeTonic
from .families import SoftControlFamily
from .state import RiskWeight


@dataclass(frozen=True, slots=True)
class AllocationScore:
    family: SoftControlFamily
    score: float
    admissible: bool = True
    reason_tags: frozenset[str] = field(default_factory=frozenset)
    activation_threshold: float = 0.0
    online_score: float | None = None
    memory_score: float = 0.0
    allocated_score: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.family, SoftControlFamily):
            actual_type = type(self.family).__name__
            raise TypeError(
                "AllocationScore.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.score, Real):
            actual_type = type(self.score).__name__
            raise TypeError(
                "AllocationScore.score must be numeric, "
                f"got {actual_type}."
            )
        if not isinstance(self.admissible, bool):
            actual_type = type(self.admissible).__name__
            raise TypeError(
                "AllocationScore.admissible must be bool, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "AllocationScore.reason_tags must contain only non-empty values "
                "after trimming."
            )
        if not isinstance(self.activation_threshold, Real):
            actual_type = type(self.activation_threshold).__name__
            raise TypeError(
                "AllocationScore.activation_threshold must be numeric, "
                f"got {actual_type}."
            )
        if self.online_score is not None and not isinstance(self.online_score, Real):
            actual_type = type(self.online_score).__name__
            raise TypeError(
                "AllocationScore.online_score must be numeric when provided, "
                f"got {actual_type}."
            )
        if not isinstance(self.memory_score, Real):
            actual_type = type(self.memory_score).__name__
            raise TypeError(
                "AllocationScore.memory_score must be numeric, "
                f"got {actual_type}."
            )
        if self.allocated_score is not None and not isinstance(self.allocated_score, Real):
            actual_type = type(self.allocated_score).__name__
            raise TypeError(
                "AllocationScore.allocated_score must be numeric when provided, "
                f"got {actual_type}."
            )
        object.__setattr__(
            self,
            "allocated_score",
            float(self.score) if self.allocated_score is None else float(self.allocated_score),
        )
        object.__setattr__(
            self,
            "online_score",
            self.allocated_score if self.online_score is None else float(self.online_score),
        )

    def as_summary(self) -> dict[str, Any]:
        return {
            "family": self.family.value,
            "online_score": self.online_score,
            "memory_score": float(self.memory_score),
            "allocated_score": self.allocated_score,
            "activation_threshold": float(self.activation_threshold),
            "admissible": self.admissible,
            "reason_tags": sorted(self.reason_tags),
        }


@dataclass(frozen=True, slots=True)
class AllocationScorecard:
    scores: tuple[AllocationScore, ...]
    alpha_t: float = 1.0

    def __post_init__(self) -> None:
        if any(not isinstance(score, AllocationScore) for score in self.scores):
            raise TypeError(
                "AllocationScorecard.scores must contain only AllocationScore instances."
            )
        if not isinstance(self.alpha_t, Real):
            actual_type = type(self.alpha_t).__name__
            raise TypeError(
                "AllocationScorecard.alpha_t must be numeric, "
                f"got {actual_type}."
            )
        if not 0.0 <= float(self.alpha_t) <= 1.0:
            raise ValueError("AllocationScorecard.alpha_t must be between 0.0 and 1.0.")


def build_allocation_diagnostics_payload(
    scorecard: AllocationScorecard,
    *,
    selected_delta_over_neutral: float,
    applied_activation_threshold: float,
    chi_t: float,
    rejected_cheaper_families: tuple[str, ...] = (),
    probe_path_state: str = "absent",
    probe_unavailable_reason: str | None = None,
    probe_result_class: str | None = None,
    verification_state: str = "not-required",
    explainability_profile: str = "minimal",
    anti_thrash_state: str = "inactive",
    repetition_target_family: SoftControlFamily | None = None,
    repetition_tax: float = 0.0,
    anti_thrash_reason_tags: frozenset[str] = frozenset(),
    mediation_payload: dict[str, Any] | None = None,
    risk_weight: RiskWeight | None = None,
    brake_tonic: BrakeTonic | None = None,
) -> dict[str, Any]:
    if not isinstance(scorecard, AllocationScorecard):
        actual_type = type(scorecard).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.scorecard must be AllocationScorecard, "
            f"got {actual_type}."
        )
    if not isinstance(selected_delta_over_neutral, Real):
        actual_type = type(selected_delta_over_neutral).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.selected_delta_over_neutral must be numeric, "
            f"got {actual_type}."
        )
    if not isinstance(applied_activation_threshold, Real):
        actual_type = type(applied_activation_threshold).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.applied_activation_threshold must be numeric, "
            f"got {actual_type}."
        )
    if not isinstance(chi_t, Real):
        actual_type = type(chi_t).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.chi_t must be numeric, "
            f"got {actual_type}."
        )
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            "build_allocation_diagnostics_payload.rejected_cheaper_families must contain only non-empty strings."
        )
    if probe_path_state not in {"available", "unavailable", "absent"}:
        raise ValueError(
            "build_allocation_diagnostics_payload.probe_path_state must be one of "
            "['absent', 'available', 'unavailable']."
        )
    if probe_unavailable_reason is not None and not (
        isinstance(probe_unavailable_reason, str) and probe_unavailable_reason.strip()
    ):
        raise ValueError(
            "build_allocation_diagnostics_payload.probe_unavailable_reason must be "
            "non-empty after trimming when provided."
        )
    if probe_path_state == "unavailable" and probe_unavailable_reason is None:
        raise ValueError(
            "build_allocation_diagnostics_payload.probe_unavailable_reason is required "
            "when probe_path_state is `unavailable`."
        )
    if probe_path_state != "unavailable" and probe_unavailable_reason is not None:
        raise ValueError(
            "build_allocation_diagnostics_payload.probe_unavailable_reason is only valid "
            "when probe_path_state is `unavailable`."
        )
    if probe_result_class is not None and not (
        isinstance(probe_result_class, str) and probe_result_class.strip()
    ):
        raise ValueError(
            "build_allocation_diagnostics_payload.probe_result_class must be non-empty after trimming when provided."
        )
    if not (isinstance(verification_state, str) and verification_state.strip()):
        raise ValueError(
            "build_allocation_diagnostics_payload.verification_state must be non-empty after trimming."
        )
    if not (isinstance(explainability_profile, str) and explainability_profile.strip()):
        raise ValueError(
            "build_allocation_diagnostics_payload.explainability_profile must be non-empty after trimming."
        )
    if anti_thrash_state not in {"inactive", "taxed", "reopened"}:
        raise ValueError(
            "build_allocation_diagnostics_payload.anti_thrash_state must be one of "
            "['inactive', 'taxed', 'reopened']."
        )
    if repetition_target_family is not None and not isinstance(
        repetition_target_family, SoftControlFamily
    ):
        actual_type = type(repetition_target_family).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.repetition_target_family must be "
            f"SoftControlFamily | None, got {actual_type}."
        )
    if isinstance(repetition_tax, bool) or not isinstance(repetition_tax, Real):
        actual_type = type(repetition_tax).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.repetition_tax must be numeric, "
            f"got {actual_type}."
        )
    if float(repetition_tax) < 0.0:
        raise ValueError(
            "build_allocation_diagnostics_payload.repetition_tax must be non-negative."
        )
    if any(not tag.strip() for tag in anti_thrash_reason_tags):
        raise ValueError(
            "build_allocation_diagnostics_payload.anti_thrash_reason_tags must contain only non-empty values after trimming."
        )
    if anti_thrash_state == "taxed" and float(repetition_tax) <= 0.0:
        raise ValueError(
            "build_allocation_diagnostics_payload.repetition_tax must be positive when anti_thrash_state is `taxed`."
        )
    if anti_thrash_state == "taxed" and repetition_target_family is None:
        raise ValueError(
            "build_allocation_diagnostics_payload.repetition_target_family is required when anti_thrash_state is `taxed`."
        )
    if anti_thrash_state in {"inactive", "reopened"} and float(repetition_tax) != 0.0:
        raise ValueError(
            "build_allocation_diagnostics_payload.repetition_tax must be 0.0 unless anti_thrash_state is `taxed`."
        )
    if mediation_payload is not None and not isinstance(mediation_payload, dict):
        actual_type = type(mediation_payload).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.mediation_payload must be "
            f"dict[str, Any] | None, got {actual_type}."
        )
    if risk_weight is not None and not isinstance(risk_weight, RiskWeight):
        actual_type = type(risk_weight).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.risk_weight must be "
            f"RiskWeight | None, got {actual_type}."
        )
    if brake_tonic is not None and not isinstance(brake_tonic, BrakeTonic):
        actual_type = type(brake_tonic).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.brake_tonic must be "
            f"BrakeTonic | None, got {actual_type}."
        )
    resolved_risk_weight = risk_weight if risk_weight is not None else RiskWeight()
    payload = {
        "alpha_t": float(scorecard.alpha_t),
        "activation_threshold": float(applied_activation_threshold),
        "selected_delta_over_neutral": float(selected_delta_over_neutral),
        "chi_t": float(chi_t),
        "risk_weight": {
            "fn_cost_weight": float(resolved_risk_weight.fn_cost_weight),
            "fp_cost_weight": float(resolved_risk_weight.fp_cost_weight),
            "adjustment_sign": resolved_risk_weight.adjustment_sign,
            "dominant_risk_source": resolved_risk_weight.dominant_risk_source,
        },
        "brake_tonic": (
            {
                "tonic_pressure": float(brake_tonic.tonic_pressure),
                "tonic_quiescence": float(brake_tonic.tonic_quiescence),
            }
            if brake_tonic is not None
            else None
        ),
        "rejected_cheaper_families": list(rejected_cheaper_families),
        "probe_path_state": probe_path_state,
        "probe_unavailable_reason": probe_unavailable_reason,
        "probe_result_class": probe_result_class,
        "verification_state": verification_state,
        "explainability_profile": explainability_profile,
        "anti_thrash": {
            "state": anti_thrash_state,
            "target_family": (
                repetition_target_family.value
                if repetition_target_family is not None
                else None
            ),
            "repetition_tax": float(repetition_tax),
            "reason_tags": sorted(anti_thrash_reason_tags),
        },
        "scores": [score.as_summary() for score in scorecard.scores],
    }
    if mediation_payload is not None:
        payload["mediation"] = mediation_payload
    return payload


def build_audit_projection_payload(
    *,
    selected_family: SoftControlFamily,
    realized_family: SoftControlFamily,
    dominant_uncertainty_sources: tuple[str, ...],
    allocation_diagnostics: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(selected_family, SoftControlFamily):
        actual_type = type(selected_family).__name__
        raise TypeError(
            "build_audit_projection_payload.selected_family must be SoftControlFamily, "
            f"got {actual_type}."
        )
    if not isinstance(realized_family, SoftControlFamily):
        actual_type = type(realized_family).__name__
        raise TypeError(
            "build_audit_projection_payload.realized_family must be SoftControlFamily, "
            f"got {actual_type}."
        )
    if any(
        not (isinstance(source, str) and source.strip())
        for source in dominant_uncertainty_sources
    ):
        raise ValueError(
            "build_audit_projection_payload.dominant_uncertainty_sources must contain only non-empty strings."
        )
    if not isinstance(allocation_diagnostics, Mapping):
        actual_type = type(allocation_diagnostics).__name__
        raise TypeError(
            "build_audit_projection_payload.allocation_diagnostics must be a mapping, "
            f"got {actual_type}."
        )

    required_keys = (
        "activation_threshold",
        "selected_delta_over_neutral",
        "rejected_cheaper_families",
        "verification_state",
        "explainability_profile",
        "probe_path_state",
        "probe_unavailable_reason",
        "probe_result_class",
    )
    missing = [key for key in required_keys if key not in allocation_diagnostics]
    if missing:
        raise ValueError(
            "build_audit_projection_payload.allocation_diagnostics is missing required keys: "
            + ", ".join(missing)
        )

    rejected_cheaper_families = allocation_diagnostics["rejected_cheaper_families"]
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            "build_audit_projection_payload.rejected_cheaper_families must contain only non-empty strings."
        )

    return {
        "selected_family": selected_family.value,
        "realized_family": realized_family.value,
        "dominant_uncertainty_sources": list(dominant_uncertainty_sources),
        "activation_threshold": float(allocation_diagnostics["activation_threshold"]),
        "selected_delta_over_neutral": float(
            allocation_diagnostics["selected_delta_over_neutral"]
        ),
        "rejected_cheaper_families": list(rejected_cheaper_families),
        "verification_state": allocation_diagnostics["verification_state"],
        "explainability_profile": allocation_diagnostics["explainability_profile"],
        "probe_path_state": allocation_diagnostics["probe_path_state"],
        "probe_result_class": allocation_diagnostics["probe_result_class"],
        "probe_unavailable_reason": allocation_diagnostics["probe_unavailable_reason"],
    }


__all__ = [
    "AllocationScore",
    "AllocationScorecard",
    "build_audit_projection_payload",
    "build_allocation_diagnostics_payload",
]
