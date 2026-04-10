"""Mechanical ownership guards for the OpenAI runtime shell."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_openai_runtime_does_not_import_private_reference_runtime_helpers() -> None:
    text = (REPO_ROOT / "cortex" / "hosts" / "openai" / "runtime.py").read_text(encoding="utf-8")

    assert "from cortex.hosts.reference.runtime import" not in text


def test_openai_runtime_session_io_does_not_import_private_reference_session_io_helpers() -> None:
    text = (REPO_ROOT / "cortex" / "hosts" / "openai" / "session_io.py").read_text(
        encoding="utf-8"
    )

    assert "from cortex.hosts.reference.session_io import" not in text
