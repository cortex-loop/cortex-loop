"""AUX package boundary for removable support-only seams."""

from .augmentation import AugmentedSupportSnapshot, AuxiliarySupportAppendix, augment_snapshot
from .cost import AuxBurdenReport
from .cross_host_shadow import (
    AUX_CROSS_HOST_SHADOW_FAILURE_LABELS,
    AuxCrossHostShadowCaseResult,
    AuxCrossHostShadowEvaluationResult,
    AuxCrossHostShadowScenario,
    evaluate_aux_cross_host_shadow,
)
from .distillation import (
    distill_offline_support_publication,
)
from .geometry import (
    AuxContradictionCluster,
    AuxGeometryReport,
    AuxMatchScore,
    build_aux_geometry_report,
)
from .evaluation import (
    AuxCorpusCaseResult,
    AuxCorpusEvaluationResult,
    AuxCorpusMetricSummary,
    AuxEvaluationResult,
    AuxTemporalScenario,
    evaluate_aux_support_corpus,
    evaluate_aux_support_snapshot,
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
    build_offline_support_publication,
    augment_snapshot_with_offline_publication,
)
from .persistence import (
    SqliteSupportMemoryStore,
    SupportEventSignature,
    SupportMemoryEpisode,
    episode_from_support_snapshot,
)
from .reference_replay import (
    AUX_REFERENCE_REPLAY_FAILURE_LABELS,
    AuxReferenceReplayCaseResult,
    AuxReferenceReplayEvaluationResult,
    AuxReferenceReplayScenario,
    evaluate_aux_reference_q_mem_replay,
)
from .support_priors import build_support_memory_prior_appendix

__all__ = [
    "AUX_CROSS_HOST_SHADOW_FAILURE_LABELS",
    "AUX_LIFT_DIRECTIONS",
    "AUX_REFERENCE_REPLAY_FAILURE_LABELS",
    "AugmentedSupportSnapshot",
    "AuxBurdenReport",
    "AuxContradictionCluster",
    "AuxCrossHostShadowCaseResult",
    "AuxCrossHostShadowEvaluationResult",
    "AuxCrossHostShadowScenario",
    "AuxCorpusCaseResult",
    "AuxCorpusEvaluationResult",
    "AuxCorpusMetricSummary",
    "AuxEvaluationResult",
    "AuxGeometryReport",
    "AuxLiftMetric",
    "AuxLiftReport",
    "AuxMatchScore",
    "AuxReferenceReplayCaseResult",
    "AuxReferenceReplayEvaluationResult",
    "AuxReferenceReplayScenario",
    "AuxTemporalScenario",
    "AuxiliarySupportAppendix",
    "OfflineSupportPublication",
    "SqliteSupportMemoryStore",
    "SupportEventSignature",
    "SupportMemoryEpisode",
    "augment_snapshot",
    "augment_snapshot_with_offline_publication",
    "build_aux_geometry_report",
    "build_aux_lift_report",
    "build_offline_support_publication",
    "build_support_memory_prior_appendix",
    "distill_offline_support_publication",
    "episode_from_support_snapshot",
    "evaluate_aux_cross_host_shadow",
    "evaluate_aux_reference_q_mem_replay",
    "evaluate_aux_support_corpus",
    "evaluate_aux_support_snapshot",
    "total_aux_burden",
]
