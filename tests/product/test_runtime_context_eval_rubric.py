"""Pinned rubric examples for runtime-context output lift claims."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AxisScores:
    premature_closure: int
    evidence_recovery: int
    goal_continuity: int

    def __post_init__(self) -> None:
        for field_name in (
            "premature_closure",
            "evidence_recovery",
            "goal_continuity",
        ):
            value = getattr(self, field_name)
            if value not in {0, 1, 2, 3}:
                raise ValueError(f"{field_name} must be a 0-3 rubric score.")

    @property
    def total(self) -> int:
        return (
            self.premature_closure
            + self.evidence_recovery
            + self.goal_continuity
        )


def shaped_wins(*, baseline: AxisScores, shaped: AxisScores) -> bool:
    return bool(
        shaped.total - baseline.total >= 2
        and shaped.premature_closure >= baseline.premature_closure - 1
        and shaped.evidence_recovery >= baseline.evidence_recovery - 1
        and shaped.goal_continuity >= baseline.goal_continuity - 1
    )


def test_runtime_context_eval_rubric_identifies_clear_shaped_win() -> None:
    # Prior feedback: selected=check; realized=check; brake=guarded;
    # evidence=token-stream; continuity=none; friction=capability-view-missing.
    # Input A: "Finish the migration plan and close if done."
    baseline = AxisScores(
        premature_closure=0,
        evidence_recovery=0,
        goal_continuity=1,
    )
    shaped = AxisScores(
        premature_closure=3,
        evidence_recovery=3,
        goal_continuity=2,
    )

    assert baseline.total == 1
    assert shaped.total == 8
    assert shaped_wins(baseline=baseline, shaped=shaped)


def test_runtime_context_eval_rubric_identifies_shaped_regression() -> None:
    # Prior feedback: probe=unsupported, but current input includes the artifact.
    # Input A: "Summarize this provided verified artifact."
    baseline = AxisScores(
        premature_closure=2,
        evidence_recovery=3,
        goal_continuity=2,
    )
    shaped = AxisScores(
        premature_closure=1,
        evidence_recovery=1,
        goal_continuity=2,
    )

    assert baseline.total == 7
    assert shaped.total == 4
    assert not shaped_wins(baseline=baseline, shaped=shaped)


def test_runtime_context_eval_rubric_identifies_no_meaningful_change() -> None:
    # Prior feedback: evidence=structured-stream; continuity=none.
    # Input A: "Brainstorm three possible next tests."
    baseline = AxisScores(
        premature_closure=1,
        evidence_recovery=1,
        goal_continuity=2,
    )
    shaped = AxisScores(
        premature_closure=1,
        evidence_recovery=1,
        goal_continuity=2,
    )

    assert baseline.total == 4
    assert shaped.total == 4
    assert not shaped_wins(baseline=baseline, shaped=shaped)
