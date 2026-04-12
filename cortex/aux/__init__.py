"""AUX package boundary for removable support-only seams."""

from .augmentation import AugmentedSupportSnapshot, AuxiliarySupportAppendix, augment_snapshot
from .cost import AuxBurdenReport
from .geometry import (
    AuxContradictionCluster,
    AuxGeometryReport,
    AuxMatchScore,
    build_aux_geometry_report,
)
from .lift import (
    AUX_LIFT_DIRECTIONS,
    AuxLiftMetric,
    AuxLiftReport,
    build_aux_lift_report,
    total_aux_burden,
)
from .publication import (
    OfflineSupportPublication,
    augment_snapshot_with_offline_publication,
)

__all__ = [
    "AUX_LIFT_DIRECTIONS",
    "AugmentedSupportSnapshot",
    "AuxBurdenReport",
    "AuxContradictionCluster",
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
    "total_aux_burden",
]
