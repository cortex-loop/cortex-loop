"""Product locks for shared tool-evidence classification."""

from __future__ import annotations

from cortex.sre.tool_evidence import (
    ToolEvidenceObservation,
    ToolEvidencePhase,
    classify_tool_evidence,
    tool_evidence_has_verification_marker,
)


def test_shared_classifier_detects_missing_artifact_before_readback() -> None:
    classification = classify_tool_evidence(
        ToolEvidenceObservation(
            tool_text="Bash wc -l exact_result.txt\nwc: exact_result.txt: No such file or directory",
            hook_event_name="PostToolUse",
            tool_response_present=True,
            path_anchors=("exact_result.txt",),
            count_completion_status_as_verification_marker=False,
        )
    )

    assert classification.phase is ToolEvidencePhase.PRE_ARTIFACT_MISSING
    assert classification.silence_reason == "pre_artifact_candidate_missing"
    assert classification.context_eligible is False


def test_shared_classifier_detects_line_shaped_failed_check() -> None:
    classification = classify_tool_evidence(
        ToolEvidenceObservation(
            tool_text=(
                "Bash cat -A exact_result.txt\n"
                "cat: illegal option -- A\n"
                "usage: cat [-belnstuv] [file ...]\n"
            ),
            hook_event_name="PostToolUse",
            tool_response_present=True,
            path_anchors=("exact_result.txt",),
            count_completion_status_as_verification_marker=False,
        )
    )

    assert classification.phase is ToolEvidencePhase.FAILED_CHECK
    assert classification.silence_reason == "phase_check_failed"


def test_shared_classifier_detects_candidate_artifact_without_status_marker() -> None:
    classification = classify_tool_evidence(
        ToolEvidenceObservation(
            tool_text="Bash {\"command\":\"printf 'alpha beta omega' > exact_result.txt\"}",
            hook_event_name="PostToolUse",
            tool_response_present=True,
            path_anchors=("exact_result.txt",),
            count_completion_status_as_verification_marker=False,
        )
    )

    assert classification.phase is ToolEvidencePhase.CANDIDATE_ARTIFACT_CREATED
    assert classification.has_verification_marker is False
    assert classification.context_eligible is True


def test_shared_classifier_detects_readback_with_command_marker() -> None:
    classification = classify_tool_evidence(
        ToolEvidenceObservation(
            tool_text="Bash {\"command\":\"wc -l exact_result.txt && cat -A exact_result.txt\"} 1 exact_result.txt alpha beta omega$",
            hook_event_name="PostToolUse",
            tool_response_present=True,
            path_anchors=("exact_result.txt",),
            count_completion_status_as_verification_marker=False,
        )
    )

    assert classification.phase is ToolEvidencePhase.READBACK_COMPLETED
    assert classification.has_verification_marker is True
    assert classification.context_eligible is True


def test_host_phase_does_not_treat_exit_code_as_verification_marker() -> None:
    assert tool_evidence_has_verification_marker(
        '{"exit_code":0}',
        count_completion_status=True,
    )
    assert not tool_evidence_has_verification_marker(
        '{"exit_code":0}',
        count_completion_status=False,
    )


def test_markerless_generic_output_stays_markerless_for_host_phase() -> None:
    classification = classify_tool_evidence(
        ToolEvidenceObservation(
            tool_text='Bash {"command":"printf alpha beta omega"} {"exit_code":0}',
            hook_event_name="PostToolUse",
            tool_response_present=True,
            path_anchors=("exact_result.txt",),
            count_completion_status_as_verification_marker=False,
        )
    )

    assert classification.phase is ToolEvidencePhase.MARKERLESS
    assert classification.silence_reason == "no_verification_marker"
