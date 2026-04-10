"""Checks for the intentionally small experimental surface."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_experimental_package_is_placeholder_only() -> None:
    module = import_module("experimental")

    assert module.__name__ == "experimental"
    assert "off-by-default" in (module.__doc__ or "")


def test_experimental_tree_has_no_promoted_host_or_sre_modules() -> None:
    promoted_files = [
        path
        for path in (REPO_ROOT / "experimental").rglob("*.py")
        if path.name != "__init__.py"
    ]

    assert promoted_files == []
