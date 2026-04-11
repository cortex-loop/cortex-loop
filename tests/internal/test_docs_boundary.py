"""Boundary and single-truth sync checks for the repo reset."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
README_PATH = REPO_ROOT / "README.md"
DOCS_INDEX_PATH = REPO_ROOT / "docs" / "README.md"
PRODUCT_CHARTER_PATH = REPO_ROOT / "docs" / "CORTEX_PRODUCT_CHARTER.md"
PRODUCT_BOUNDARY_PATH = REPO_ROOT / "docs" / "CORTEX_PRODUCT_BOUNDARY.md"
STATUS_REGISTRY_PATH = REPO_ROOT / "internal" / "truth" / "cortex_status.json"
STATUS_DOC_PATH = REPO_ROOT / "docs" / "CORTEX_STATUS.md"
ARCHIVE_MANIFEST_PATH = REPO_ROOT / "internal" / "archive" / "manifest.json"
ARCHIVE_INDEX_PATH = REPO_ROOT / "docs" / "archive" / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
ROOT_MAKEFILE_PATH = REPO_ROOT / "Makefile"
DOCS_ROOT = REPO_ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_status() -> dict[str, object]:
    return json.loads(_read(STATUS_REGISTRY_PATH))


def test_agents_records_mission_lock_and_single_truth_bootstrap() -> None:
    text = _read(AGENTS_PATH)
    lines = text.splitlines()
    sections = [line for line in lines if line.startswith("## ")]
    all_agents = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.rglob("AGENTS.md")
        if ".git" not in path.parts and ".cortex" not in path.parts
    )

    assert all_agents == ["AGENTS.md"]
    assert len(lines) <= 180
    assert sections == [
        "## Mission",
        "## Authority",
        "## Non-Negotiables",
        "## Working Mode",
        "## Workflow",
        "## Codex App Dogfood Mode",
        "## Handoff",
    ]
    assert "rich multi-host executive layer" in text
    assert "installable executive layer" in text
    assert "human executive function" in text
    assert "live evidence" in text
    assert "full-executive completion percent versus the shippable threshold first" in text
    assert "bio-to-code matrix" in text
    assert "internal/truth/cortex_status.json" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "AGENTS.md" in text
    assert "git branch --show-current" in text
    assert "git status --short --untracked-files=all" in text
    assert "shipping truth" in text
    assert "conformance truth" in text
    assert "This root `AGENTS.md` is the only agent contract in the repo." in text
    assert "CORTEX_V2_ACTIVE_WORKSTREAM" not in text
    assert "CORTEX_V2_PHASE_GATES_2" not in text
    assert "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE" not in text
    assert "CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2" not in text
    assert "V1_CODE_PORT_DETERMINATION" not in text


def test_public_docs_point_to_status_and_keep_archive_out_of_the_front_door() -> None:
    readme = _read(README_PATH)
    docs_index = _read(DOCS_INDEX_PATH)
    charter = _read(PRODUCT_CHARTER_PATH)
    boundary = _read(PRODUCT_BOUNDARY_PATH)

    assert "docs/CORTEX_STATUS.md" in readme
    assert "Current Status" in docs_index
    assert "archive/" in docs_index
    assert "active workstream ledger" in charter
    assert "internal/truth/cortex_status.json" in boundary
    for text in (readme, docs_index, charter, boundary):
        assert "CORTEX_V2_ACTIVE_WORKSTREAM" not in text
        assert "CORTEX_V2_PHASE_GATES_2" not in text
        assert "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE" not in text


def test_active_doc_allowlist_matches_status_registry() -> None:
    status = _load_status()
    expected = set(status["active_docs"])
    actual = {
        str(path.relative_to(REPO_ROOT))
        for path in DOCS_ROOT.rglob("*.md")
        if not path.is_relative_to(DOCS_ROOT / "archive")
    }

    assert actual == expected


def test_docs_directory_only_exposes_archive_and_workflow_subtrees() -> None:
    subdirs = sorted(path.name for path in DOCS_ROOT.iterdir() if path.is_dir())

    assert subdirs == ["archive", "internal"]
    assert [path.name for path in (DOCS_ROOT / "internal").iterdir()] == ["REPO_WORKFLOW.md"]


def test_generated_status_doc_is_current() -> None:
    proc = subprocess.run(
        [sys.executable, "internal/truth/generate_status.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert STATUS_DOC_PATH.exists()


def test_status_registry_is_complete_and_stable() -> None:
    status = _load_status()

    assert set(status) >= {
        "resting_state",
        "bootstrap",
        "product_goal",
        "identity",
        "executive_completion",
        "bio_to_code_matrix",
        "math_to_code_rules",
        "work_today",
        "next_product_train",
        "system_map",
        "subsystems",
        "packet_to_code_anchors",
        "hosts",
        "conformance_summary",
        "closure_gates",
        "retained_evidence_refs",
        "proof_commands",
        "retained_data",
        "where_to_work",
        "blocked_moves",
        "active_docs",
    }
    assert status["resting_state"]["branch"] == "main"
    assert "installable executive layer" in status["identity"]["statement"]
    assert status["executive_completion"]["shippable_threshold_percent"] == 85
    assert status["bio_to_code_matrix"]
    assert status["math_to_code_rules"]["law_revision_rule"]
    assert sum(item["weight"] for item in status["bio_to_code_matrix"]) == 100
    current_percent = round(
        sum(
            status["executive_completion"]["status_fraction"][item["status"]] * item["weight"]
            for item in status["bio_to_code_matrix"]
        )
    )
    assert current_percent == 80
    assert current_percent < status["executive_completion"]["shippable_threshold_percent"]
    matrix_status = {
        item["skill"]: item["status"] for item in status["bio_to_code_matrix"]
    }
    assert matrix_status["Uncertainty handling and brake"] == "landed"
    assert (
        matrix_status["Branch continuity, suspend/resume, and truthful closure"]
        == "landed"
    )
    assert matrix_status["Intervention pricing versus neutrality"] == "landed"
    assert matrix_status["Blocker surfacing and goal-debt management"] == "landed"
    assert matrix_status["Multi-host executive continuity"] == "partial"
    assert matrix_status["Offline consolidation and support geometry"] == "north_star"
    assert status["executive_completion"]["next_raise"] == [
        {
            "skill": "Multi-host executive continuity",
            "expected_points_if_landed": 11,
            "why": "Largest remaining near-term executive lift now that the richer OpenAI-first law is landed and proven on the shipping lane.",
        }
    ]
    host_status = {
        item["name"]: item["conformance"] for item in status["hosts"]
    }
    assert host_status == {
        "openai": "conformant",
        "claude": "partial",
        "gemini": "partial",
        "reference": "conformant",
    }
    assert status["work_today"]["slug"]
    assert status["next_product_train"]["slug"] == "multi-host-executive-continuity"


def test_generated_status_doc_includes_system_map_and_next_product_train() -> None:
    text = _read(STATUS_DOC_PATH)

    assert "## System Map" in text
    assert "```mermaid" in text
    assert "## Identity And Research Stance" in text
    assert "## Executive Completion" in text
    assert "## Bio-To-Code Matrix" in text
    assert "## Math To Code Rules" in text
    assert "human executive function" in text
    assert "Current full-executive completion: `80%`" in text
    assert "Shippable threshold for the full executive: `85%`" in text
    assert "When user asks where Cortex is at:" in text
    assert "full executive denominator" in text
    assert "## Packet To Code" in text
    assert "## Next Product Train" in text
    assert "`multi-host-executive-continuity`" in text


def test_front_door_surfaces_point_to_one_command_managed_closeout() -> None:
    agents = _read(AGENTS_PATH)
    status = _read(STATUS_DOC_PATH)

    assert 'close-session --message "scope: end-state summary"' in status
    assert "cleanup-report" in status
    assert "manual publication" not in agents.lower()
    assert "manual publication" not in status.lower()
    assert "separate publication step" not in status.lower()


def test_generated_archive_index_is_current() -> None:
    proc = subprocess.run(
        [sys.executable, "internal/archive/generate_archive_index.py", "--check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert ARCHIVE_INDEX_PATH.exists()


def test_archive_manifest_tracks_retained_refs_and_offloaded_payloads() -> None:
    manifest = json.loads(_read(ARCHIVE_MANIFEST_PATH))

    assert manifest["retained_evidence_refs"]
    assert manifest["offloaded_payloads"]
    assert any(entry["ref"] == "archive/e23-preservation-state-machine" for entry in manifest["retained_evidence_refs"])


def test_no_active_code_homes_remain_under_experimental() -> None:
    experimental_python = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "experimental").rglob("*.py")
        if path.name != "__init__.py"
    )

    assert experimental_python == []


def test_legacy_test_buckets_are_removed() -> None:
    assert not (REPO_ROOT / "tests" / "unit").exists()
    assert not (REPO_ROOT / "tests" / "integration").exists()


def test_lab_output_quality_fixtures_are_source_only() -> None:
    forbidden = sorted(
        str(path.relative_to(REPO_ROOT))
        for path in (REPO_ROOT / "tests" / "lab" / "fixtures" / "output_quality").rglob("*")
        if path.is_dir() and path.name in {"node_modules", "dist", ".astro"}
    )

    assert forbidden == []


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
        "cortex-openai-cli": "cortex.hosts.openai.cli:main",
        "cortex-openai-service": "cortex.hosts.openai.service:main",
    }


def test_root_makefile_is_purpose_first() -> None:
    text = _read(ROOT_MAKEFILE_PATH)

    assert "product-test:" in text
    assert "conformance-test:" in text
    assert "experimental-test:" in text
    assert "lab-test:" in text
    assert "archive-test:" in text
    assert "make repo-hygiene is internal and deprecated; use make -C internal cleanup-report" in text
