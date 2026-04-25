"""Lab-surface checks for canonical commands and moved verification paths."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LAB_MAKEFILE_PATH = REPO_ROOT / "lab" / "Makefile"
TRAIN_LOOP_PATH = REPO_ROOT / "lab" / "cortex_train_loop.py"
AGENT_LOOP_GUARD_PATH = REPO_ROOT / "lab" / "agent_loop_guard.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_lab_makefile_runs_from_repo_root_and_uses_split_test_paths() -> None:
    text = _read(LAB_MAKEFILE_PATH)

    assert 'ROOT := $(abspath $(CURDIR)/..)' in text
    assert 'ROOT_PYTEST = cd "$(ROOT)" && $(PYTEST)' in text
    assert 'ROOT_PYTHON = cd "$(ROOT)" && $(PYTHON)' in text
    assert "tests/product/test_import_smoke.py" in text
    assert "tests/product/test_public_boundary.py" in text
    assert "tests/conformance/test_host_import_smoke.py" in text
    assert "tests/internal/test_docs_boundary.py" in text
    assert "tests/internal/test_workflow_boundary.py" in text
    assert "tests/lab/test_lab_surface.py" in text
    assert "\t$(PYTEST) tests/" not in text
    assert "\t$(PYTHON) lab/" not in text


def test_train_loop_uses_canonical_lab_and_internal_test_paths() -> None:
    text = _read(TRAIN_LOOP_PATH)

    assert "tests/internal/test_docs_boundary.py" in text
    assert "tests/product/test_import_smoke.py" in text
    assert "make -C lab revalidate-openai-host-control" in text
    assert "tests/unit/" not in text
    assert "tests/integration/" not in text
    assert '"make revalidate-openai-host-control"' not in text


def test_agent_loop_guard_is_lab_watchlist_only_and_bounded() -> None:
    text = _read(AGENT_LOOP_GUARD_PATH)
    makefile = _read(LAB_MAKEFILE_PATH)

    assert 'scope: str = "lab"' in text
    assert 'evidence_role: str = "watchlist"' in text
    assert "DEFAULT_MAX_CONTINUATIONS = 6" in text
    assert "Do not run paid service-lane commands" in text
    assert "do not reactivate V3 as product truth" in text
    assert "agent-loop-guard-init" in makefile
    assert "agent-loop-guard-evaluate" in makefile
