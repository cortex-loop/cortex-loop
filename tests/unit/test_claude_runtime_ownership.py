"""Mechanical ownership guards for the Claude runtime shell."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_claude_runtime_does_not_import_private_reference_runtime_helpers() -> None:
    text = (REPO_ROOT / "experimental" / "runtime" / "claude.py").read_text(
        encoding="utf-8"
    )

    assert "from experimental.runtime.reference import" not in text


def test_claude_runtime_session_io_does_not_import_private_reference_session_io_helpers() -> None:
    text = (REPO_ROOT / "experimental" / "runtime" / "claude_session_io.py").read_text(
        encoding="utf-8"
    )

    assert "from experimental.runtime.reference_session_io import" not in text
