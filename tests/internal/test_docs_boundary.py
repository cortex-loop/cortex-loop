"""Boundary and mission-lock sync checks for the E22 repo split."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
PRODUCT_CHARTER_PATH = REPO_ROOT / "docs" / "CORTEX_PRODUCT_CHARTER.md"
PRODUCT_BOUNDARY_PATH = REPO_ROOT / "docs" / "CORTEX_PRODUCT_BOUNDARY.md"
WORKSTREAM_PATH = REPO_ROOT / "docs" / "internal" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
ROOT_MAKEFILE_PATH = REPO_ROOT / "Makefile"
DOCS_ROOT = REPO_ROOT / "docs"
SURFACE_DOC_ROOTS = (
    DOCS_ROOT / "experimental",
    DOCS_ROOT / "internal",
    DOCS_ROOT / "lab",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_agents_records_mission_lock_and_seam_fields() -> None:
    text = _read(AGENTS_PATH)

    assert "## Mission lock" in text
    assert "Does this make the shipped Cortex executive layer better" in text
    assert "## Seam declaration requirement" in text
    assert "`Surface:` `product | experimental | lab | internal`" in text
    assert "`Executive Benefit:`" in text
    assert "`Why this beats direct product work now:`" in text
    assert "Do not describe lab, evidence, or governance work as Cortex product progress" in text
    assert "Do not let evaluation machinery become the public or internal identity of Cortex." in text


def test_workstream_ledger_uses_product_first_fields() -> None:
    text = _read(WORKSTREAM_PATH)

    assert "Product target:" in text
    assert "Surface:" in text
    assert "Direct executive payoff:" in text
    assert "Why this seam exists instead of a narrower product seam:" in text
    assert "Parked evidence status:" in text
    assert "not product truth" in text


def test_public_docs_keep_lab_and_internal_out_of_the_front_door() -> None:
    readme = _read(README_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    charter = _read(PRODUCT_CHARTER_PATH)
    boundary = _read(PRODUCT_BOUNDARY_PATH)

    for text in (readme, docs_index, charter, boundary):
        assert "docs/internal/" not in text
        assert "docs/lab/" not in text

    assert "executive layer" in readme
    assert "Not the product:" in readme
    assert "train loops" in readme
    assert "governance records" in readme
    assert "active workstream ledger" in charter
    assert "not Cortex the product" in charter
    assert "public packaging exposes only `cortex`" in boundary


def test_doc_surface_tags_match_directory_placement() -> None:
    expected_surface_by_parent = {
        REPO_ROOT / "docs": "product",
        REPO_ROOT / "docs" / "experimental": "experimental",
        REPO_ROOT / "docs" / "lab": "lab",
        REPO_ROOT / "docs" / "internal": "internal",
    }

    for path in (REPO_ROOT / "docs").rglob("*.md"):
        if path.name.startswith("."):
            continue
        if path.is_relative_to(REPO_ROOT / "docs" / "lab" / "mediation_evidence"):
            continue
        if path.is_relative_to(REPO_ROOT / "docs" / "internal" / "archive"):
            continue
        text = _read(path)
        match = re.search(r"^Surface:\s+(\w+)\s*$", text, re.MULTILINE)
        assert match is not None, f"missing Surface tag: {path}"

        if path.parent == REPO_ROOT / "docs":
            expected = expected_surface_by_parent[REPO_ROOT / "docs"]
        elif path.is_relative_to(REPO_ROOT / "docs" / "experimental"):
            expected = expected_surface_by_parent[REPO_ROOT / "docs" / "experimental"]
        elif path.is_relative_to(REPO_ROOT / "docs" / "lab"):
            expected = expected_surface_by_parent[REPO_ROOT / "docs" / "lab"]
        elif path.is_relative_to(REPO_ROOT / "docs" / "internal"):
            expected = expected_surface_by_parent[REPO_ROOT / "docs" / "internal"]
        else:
            raise AssertionError(f"unexpected docs path: {path}")

        assert match.group(1) == expected, f"surface drift for {path}"


def test_root_docs_only_exposes_split_surface_directories() -> None:
    subdirs = sorted(path.name for path in DOCS_ROOT.iterdir() if path.is_dir())

    assert subdirs == ["experimental", "internal", "lab"]


def test_moved_doc_references_and_path_families_do_not_drift() -> None:
    text_roots = (
        REPO_ROOT / "docs",
        REPO_ROOT / "tests",
        REPO_ROOT / "experimental",
        REPO_ROOT / "lab",
        REPO_ROOT / "internal",
    )
    text_files = [
        path
        for root in text_roots
        for path in root.rglob("*")
        if path.is_file() and (path.suffix in {".md", ".py", ".toml"} or path.name == "Makefile")
    ]
    text_files.extend(
        [
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "README.md",
            REPO_ROOT / "Makefile",
        ]
    )
    text_files = [path for path in text_files if path != Path(__file__)]

    banned_literals = {
        "docs/archive/": "docs/internal/archive/",
        "docs/erika-visualizations/": "docs/lab/visualizations/",
        "docs/mediation_evidence/": "docs/lab/mediation_evidence/",
        "docs/internal/docs/internal/REPO_WORKFLOW.md": "docs/internal/REPO_WORKFLOW.md",
    }
    for doc_root in SURFACE_DOC_ROOTS:
        for moved_doc in doc_root.glob("*.md"):
            banned_literals[f"docs/{moved_doc.name}"] = str(moved_doc.relative_to(REPO_ROOT))

    offenders: list[str] = []
    for path in text_files:
        text = _read(path)
        for old, replacement in banned_literals.items():
            if old in text:
                offenders.append(f"{path}: replace {old} -> {replacement}")

    assert not offenders, "\n".join(offenders)


def test_product_package_does_not_import_non_product_surfaces() -> None:
    forbidden_patterns = (
        "from experimental",
        "import experimental",
        "from lab",
        "import lab",
        "from internal",
        "import internal",
    )

    for path in (REPO_ROOT / "cortex").rglob("*.py"):
        text = _read(path)
        for pattern in forbidden_patterns:
            assert pattern not in text, f"{path} imports non-product surface via {pattern!r}"


def test_public_packaging_surface_is_explicit() -> None:
    config = tomllib.loads(_read(PYPROJECT_PATH))

    scripts = config["project"]["scripts"]
    assert scripts == {
        "cortex-openai-cli": "cortex.runtime.openai_cli:main",
        "cortex-openai-service": "cortex.runtime.openai_service:main",
    }

    finder = config["tool"]["setuptools"]["packages"]["find"]
    assert finder["include"] == ["cortex", "cortex.*"]
    assert finder["exclude"] == [
        "experimental",
        "experimental.*",
        "lab",
        "lab.*",
        "internal",
        "internal.*",
        "tests",
        "tests.*",
    ]


def test_root_makefile_is_product_first() -> None:
    text = _read(ROOT_MAKEFILE_PATH)

    assert "product-test:" in text
    assert "product-openai-cli:" in text
    assert "product-openai-service:" in text
    assert "experimental-test:" in text
    assert "make $@ is internal and deprecated; use make -C lab $@" in text
    assert "make repo-hygiene is internal and deprecated; use make -C internal cleanup-report" in text
