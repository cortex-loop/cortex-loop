"""Focused tests for narrow provenance evidence-reference helpers."""

from pathlib import Path

import pytest

from cortex.core.provenance import (
    EvidenceReferenceEvaluation,
    command_claim_matches,
    evaluate_evidence_reference,
    normalize_command_claim,
    normalize_repo_relative_file_claims,
)


def test_path_reference_verifies_when_file_exists_and_fails_when_missing(tmp_path: Path) -> None:
    existing = tmp_path / "src" / "module.py"
    existing.parent.mkdir(parents=True)
    existing.write_text("print('ok')\n", encoding="utf-8")

    verified = evaluate_evidence_reference("src/module.py#L10", root=tmp_path)
    missing = evaluate_evidence_reference("src/missing.py:12", root=tmp_path)

    assert verified.reference_kind == "path"
    assert verified.check_status == "verified"
    assert verified.normalized_reference == "src/module.py"
    assert missing.reference_kind == "path"
    assert missing.check_status == "unverified"
    assert missing.normalized_reference == "src/missing.py"


def test_tool_reference_verifies_or_becomes_uncheckable_without_tool_evidence(tmp_path: Path) -> None:
    verified = evaluate_evidence_reference(
        "tool:pytest",
        root=tmp_path,
        observed_tools=("pytest", "ruff"),
    )
    uncheckable = evaluate_evidence_reference("tool:pytest", root=tmp_path)

    assert verified.reference_kind == "tool"
    assert verified.check_status == "verified"
    assert uncheckable.reference_kind == "tool"
    assert uncheckable.check_status == "uncheckable"
    assert uncheckable.reason == "no observed tool evidence"


def test_evidence_reference_evaluation_requires_non_empty_reference_kind() -> None:
    direct = EvidenceReferenceEvaluation(
        reference_kind="path",
        check_status="verified",
        reason="path exists",
    )
    emitted = evaluate_evidence_reference("src/module.py#L10", root=Path("/repo"))

    assert direct.reference_kind == "path"
    assert emitted.reference_kind == "path"

    with pytest.raises(
        ValueError,
        match="reference_kind must be non-empty after trimming",
    ):
        EvidenceReferenceEvaluation(
            reference_kind="   ",
            check_status="verified",
            reason="ok",
        )


def test_evidence_reference_evaluation_requires_non_empty_check_status() -> None:
    direct = EvidenceReferenceEvaluation(
        reference_kind="path",
        check_status="verified",
        reason="path exists",
    )
    emitted = evaluate_evidence_reference("src/module.py#L10", root=Path("/repo"))

    assert direct.check_status == "verified"
    assert emitted.check_status == "unverified"

    with pytest.raises(
        ValueError,
        match="check_status must be non-empty after trimming",
    ):
        EvidenceReferenceEvaluation(
            reference_kind="path",
            check_status="   ",
            reason="ok",
        )


def test_evidence_reference_evaluation_requires_non_empty_reason() -> None:
    direct = EvidenceReferenceEvaluation(
        reference_kind="path",
        check_status="verified",
        reason="path exists",
    )
    emitted = evaluate_evidence_reference("src/module.py#L10", root=Path("/repo"))

    assert direct.reason == "path exists"
    assert emitted.reason == "path does not exist: src/module.py"

    with pytest.raises(
        ValueError,
        match="reason must be non-empty after trimming",
    ):
        EvidenceReferenceEvaluation(
            reference_kind="path",
            check_status="verified",
            reason="   ",
        )


def test_command_reference_matches_normalized_wrapper_variants(tmp_path: Path) -> None:
    assert command_claim_matches("pytest tests/unit/test_x.py", "python3 -m pytest tests/unit/test_x.py")

    evaluation = evaluate_evidence_reference(
        "pytest tests/unit/test_x.py",
        root=tmp_path,
        observed_commands=("python3 -m pytest tests/unit/test_x.py",),
    )

    assert evaluation.reference_kind == "command"
    assert evaluation.check_status == "verified"


def test_normalize_command_claim_cleans_backtick_wrapped_pass_note() -> None:
    assert (
        normalize_command_claim("`python3 -m pytest tests/unit` passed")
        == "python3 -m pytest tests/unit"
    )


def test_backtick_wrapped_pass_note_verifies_against_observed_command(tmp_path: Path) -> None:
    evaluation = evaluate_evidence_reference(
        "`python3 -m pytest tests/unit` passed",
        root=tmp_path,
        observed_commands=("python3 -m pytest tests/unit -q",),
    )

    assert evaluation.reference_kind == "command"
    assert evaluation.check_status == "verified"
    assert evaluation.normalized_reference == "python3 -m pytest tests/unit"


def test_note_text_is_classified_as_uncheckable_note_text(tmp_path: Path) -> None:
    evaluation = evaluate_evidence_reference("manual review note for operator", root=tmp_path)

    assert evaluation.reference_kind == "note"
    assert evaluation.check_status == "uncheckable"
    assert evaluation.reason == "reference is non-verifiable note text"


def test_repo_relative_file_claim_normalization_dedupes_and_strips_suffixes(tmp_path: Path) -> None:
    claims = normalize_repo_relative_file_claims(
        [
            "src/module.py#L10",
            "src/module.py:10:2",
            "./docs/guide.md",
            "./docs/guide.md",
        ],
        root=tmp_path,
    )

    assert claims == ("src/module.py", "docs/guide.md")
