"""Public-surface checks for the shipped Cortex package."""

from __future__ import annotations

import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
PRODUCT_SRE_DIR = REPO_ROOT / "cortex" / "sre"


def test_public_readme_and_docs_index_are_product_first() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    docs_index = DOCS_INDEX_PATH.read_text(encoding="utf-8")

    assert "executive layer" in readme
    assert "`cortex` package" in readme
    assert "Public product docs:" in docs_index
    assert "Public experimental docs:" in docs_index
    assert "Internal lab and governance records are intentionally excluded" in docs_index


def test_public_package_scripts_are_openai_only() -> None:
    config = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))

    assert set(config["project"]["scripts"]) == {"cortex-openai-cli", "cortex-openai-service"}


def test_product_sre_directory_only_contains_shipped_modules() -> None:
    shipped_files = sorted(path.name for path in PRODUCT_SRE_DIR.glob("*.py"))

    assert shipped_files == ["__init__.py", "branching.py", "verified_work.py"]
