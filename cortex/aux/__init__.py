"""AUX package boundary for removable support-only seams."""

from .augmentation import AugmentedSupportSnapshot, AuxiliarySupportAppendix, augment_snapshot
from .cost import AuxBurdenReport
from .geometry import (
    AuxContradictionCluster,
    AuxGeometryReport,
    AuxMatchScore,
    build_aux_geometry_report,
)
from .evaluation import AuxEvaluationResult, evaluate_aux_support_snapshot
from .lift import (
    AUX_LIFT_DIRECTIONS,
    AuxLiftMetric,
    AuxLiftReport,
    build_aux_lift_report,
    total_aux_burden,
)
from .publication import (
    OfflineSupportPublication,
    build_offline_support_publication,
    augment_snapshot_with_offline_publication,
)
from .support_priors import build_support_memory_prior_appendix

__all__ = [
    "AUX_LIFT_DIRECTIONS",
    "AugmentedSupportSnapshot",
    "AuxBurdenReport",
    "AuxContradictionCluster",
    "AuxEvaluationResult",
    "AuxGeometryReport",
    "AuxLiftMetric",
    "AuxLiftReport",
    "AuxMatchScore",
    "AuxiliarySupportAppendix",
    "OfflineSupportPublication",
    "augment_snapshot",
    "augment_snapshot_with_offline_publication",
    "build_aux_geometry_report",
    "build_aux_lift_report",
    "build_offline_support_publication",
    "build_support_memory_prior_appendix",
    "evaluate_aux_support_snapshot",
    "total_aux_burden",
]
