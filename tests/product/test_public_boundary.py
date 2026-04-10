"""Public-surface checks for the shipped Cortex package."""

from __future__ import annotations

import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
PRODUCT_SRE_DIR = REPO_ROOT / "cortex" / "sre"
HOSTS_DIR = REPO_ROOT / "cortex" / "hosts"


def test_public_readme_and_docs_index_are_product_first() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    docs_index = DOCS_INDEX_PATH.read_text(encoding="utf-8")

    assert "executive layer" in readme
    assert "`cortex` package" in readme
    assert "Current Status" in readme
    assert "Active docs:" in docs_index
    assert "Repo Workflow" in docs_index
    assert "Historical runtime, lab, and governance material now lives under" in docs_index


def test_public_package_scripts_are_openai_only() -> None:
    config = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))

    assert set(config["project"]["scripts"]) == {"cortex-openai-cli", "cortex-openai-service"}


def test_product_tree_exposes_shared_executive_and_host_realizations() -> None:
    sre_files = {path.name for path in PRODUCT_SRE_DIR.glob("*.py")}
    host_dirs = {path.name for path in HOSTS_DIR.iterdir() if path.is_dir()}

    assert {"branching.py", "verified_work.py", "mediation.py", "reference_builder.py"}.issubset(
        sre_files
    )
    assert {"openai", "claude", "gemini", "reference"}.issubset(host_dirs)
