"""Mechanical ownership guards for the Gemini runtime shell."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_gemini_runtime_does_not_import_private_reference_runtime_helpers() -> None:
    text = (REPO_ROOT / "cortex" / "runtime" / "gemini.py").read_text(encoding="utf-8")

    assert "from cortex.runtime.reference import" not in text


def test_gemini_runtime_session_io_does_not_import_private_reference_session_io_helpers() -> None:
    text = (REPO_ROOT / "cortex" / "runtime" / "gemini_session_io.py").read_text(
        encoding="utf-8"
    )

    assert "from cortex.runtime.reference_session_io import" not in text
