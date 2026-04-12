from __future__ import annotations

import pytest

from cortex.core.support import SupportReference
from cortex.sre.families import SoftControlFamily
from cortex.sre.memory_priors import (
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)


def test_support_memory_prior_score_requires_bounded_score_and_typed_refs() -> None:
    score = SupportMemoryPriorScore(
        family=SoftControlFamily.CHECK,
        score=0.5,
        support_refs=(SupportReference("memory", "memo-1"),),
    )

    assert score.score == 0.5

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        SupportMemoryPriorScore(
            family=SoftControlFamily.CHECK,
            score=1.2,
        )

    with pytest.raises(TypeError, match="SupportReference"):
        SupportMemoryPriorScore(
            family=SoftControlFamily.CHECK,
            score=0.2,
            support_refs=("memo-1",),
        )


def test_support_memory_prior_appendix_keeps_single_score_per_family_and_defaults_missing_scores_to_zero() -> None:
    appendix = SupportMemoryPriorAppendix(
        scores=(
            SupportMemoryPriorScore(
                family=SoftControlFamily.BRANCH,
                score=0.7,
            ),
        ),
        appendix_tags=frozenset({"q_mem:explicit-aux"}),
    )

    assert appendix.active is True
    assert appendix.score_for(SoftControlFamily.BRANCH).score == pytest.approx(0.7)
    assert appendix.score_for(SoftControlFamily.CHECK).score == 0.0

    with pytest.raises(ValueError, match="at most one score per family"):
        SupportMemoryPriorAppendix(
            scores=(
                SupportMemoryPriorScore(
                    family=SoftControlFamily.BRANCH,
                    score=0.5,
                ),
                SupportMemoryPriorScore(
                    family=SoftControlFamily.BRANCH,
                    score=0.3,
                ),
            )
        )
