"""Boundary and single-truth sync checks for the repo reset."""

from __future__ import annotations

import json
import os
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
WORKFLOW_DOC_PATH = REPO_ROOT / "docs" / "internal" / "REPO_WORKFLOW.md"
ARCHIVE_MANIFEST_PATH = REPO_ROOT / "internal" / "archive" / "manifest.json"
ARCHIVE_INDEX_PATH = REPO_ROOT / "docs" / "archive" / "README.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
ROOT_MAKEFILE_PATH = REPO_ROOT / "Makefile"
DOCS_ROOT = REPO_ROOT / "docs"
SKIP_WALK_DIRS = {".git", ".cortex", ".claude", "node_modules", "__pycache__"}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_status() -> dict[str, object]:
    return json.loads(_read(STATUS_REGISTRY_PATH))


def _find_repo_files(filename: str) -> list[str]:
    matches: list[str] = []
    for current_root, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [dirname for dirname in dirnames if dirname not in SKIP_WALK_DIRS]
        if filename not in filenames:
            continue
        path = Path(current_root) / filename
        matches.append(str(path.relative_to(REPO_ROOT)))
    return sorted(matches)


def test_agents_records_mission_lock_and_single_truth_bootstrap() -> None:
    text = _read(AGENTS_PATH)
    lines = text.splitlines()
    sections = [line for line in lines if line.startswith("## ")]
    all_agents = _find_repo_files("AGENTS.md")

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
    assert "lead with shipping truth, conformance truth, the current train, and the active quality/risk focus" in text
    assert "bio-to-code matrix" in text
    assert "internal/truth/cortex_status.json" in text
    assert "docs/CORTEX_STATUS.md" in text
    assert "AGENTS.md" in text
    assert "git branch --show-current" in text
    assert "git status --short --untracked-files=all" in text
    assert "shipping truth" in text
    assert "conformance truth" in text
    assert "This root `AGENTS.md` is the only agent contract in the repo." in text
    assert "Do not run paid service-lane commands unless the user explicitly approves spend in the current chat." in text
    assert "Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED`" in text
    assert ".cortex/closeout_contract/" in text
    assert "Workflow-law seams are load-bearing too" in text
    assert "revalidates reviewed-path exactness after verification" in text
    assert "at least one law-to-code completeness row" in text
    assert "Fixed now" in text
    assert "Intentionally deferred" in text
    assert "Still underfit" in text
    assert "Zeroed or stubbed terms" in text
    assert "Hostile reviewer critiques" in text
    assert "Claim earned now" in text
    assert "Claim still forbidden" in text
    assert "Final Handoff Mirror" in text
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
    workflow = _read(WORKFLOW_DOC_PATH)

    assert "docs/CORTEX_STATUS.md" in readme
    assert "OpenAI product runtime on the CLI lane, with the direct service kept as a non-default backup surface" in readme
    assert "Current Status" in docs_index
    assert "archive/" in docs_index
    assert "active workstream ledger" in charter
    assert "internal/truth/cortex_status.json" in boundary
    assert "paid OpenAI service-lane proof is never part of the default bundle" in workflow
    assert "requires explicit user approval in the current chat" in workflow
    assert "closeout contract artifact" in workflow
    assert "load_bearing" in workflow
    assert "hard-fails" in workflow
    assert "workflow-law terms touched" in workflow
    assert "reviewed-path drift during verification" in workflow
    assert "Final Handoff Mirror" in workflow
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
    assert current_percent == 100
    assert current_percent >= status["executive_completion"]["shippable_threshold_percent"]
    matrix_status = {
        item["skill"]: item["status"] for item in status["bio_to_code_matrix"]
    }
    status_mix = {
        key: sum(1 for item in status["bio_to_code_matrix"] if item["status"] == key)
        for key in ("landed", "partial", "north_star")
    }
    assert status_mix == {"landed": 8, "partial": 0, "north_star": 0}
    assert matrix_status["Uncertainty handling and brake"] == "landed"
    assert (
        matrix_status["Branch continuity, suspend/resume, and truthful closure"]
        == "landed"
    )
    assert matrix_status["Intervention pricing versus neutrality"] == "landed"
    assert matrix_status["Blocker surfacing and goal-debt management"] == "landed"
    assert matrix_status["Multi-host executive continuity"] == "landed"
    assert matrix_status["Offline consolidation and support geometry"] == "landed"
    assert status["executive_completion"]["next_raise"] == [
        {
            "skill": "No remaining denominator row",
            "expected_points_if_landed": 0,
            "why": "The full executive denominator is already landed, so the active leverage is code-quality, proof-confidence, dead-weight elimination, and live-run reliability rather than score expansion.",
        }
    ]
    host_status = {
        item["name"]: item["conformance"] for item in status["hosts"]
    }
    host_surfaces = {
        item["name"]: item["strongest_surface"] for item in status["hosts"]
    }
    assert host_status == {
        "openai": "conformant",
        "claude": "conformant",
        "gemini": "conformant",
        "reference": "conformant",
    }
    assert host_surfaces == {
        "openai": "operator_cli",
        "claude": "operator_cli",
        "gemini": "operator_cli",
        "reference": "reference_cli",
    }
    assert status["conformance_summary"]["shipping_default"] == "openai:operator_cli"
    assert status["work_today"]["slug"] == "v2-full-communication-closure"
    assert "brake tonic quiescence-exit mismatch is closed" in status["work_today"]["note"]
    assert "V2 full communication closure" in status["work_today"]["note"]
    assert "Claude CLI and Codex CLI" in status["work_today"]["note"]
    assert "paid API service-lane commands remain blocked" in status["work_today"]["note"]
    assert "subscription CLI lanes are no-API-spend" in status["work_today"]["note"]
    assert "Q_mem = 0" in status["work_today"]["note"]
    assert status["next_product_train"]["slug"] == "v2-full-communication-closure"
    assert status["next_product_train"]["surface"] == "product + conformance + lab"
    assert "Core/SRE/AUX packet denominator" in status["next_product_train"]["executive_benefit"]
    assert "partial calculations" in status["next_product_train"]["why_now"]
    assert "agent-loop-guard closure report" in status["next_product_train"]["primary_metric"]
    assert "Claude live/watchlist evidence present" in status["next_product_train"]["primary_metric"]
    assert "Keep the bounded audit surface compact and truthful" in status["where_to_work"][0]
    assert "no-spend live evidence current and explicit" in status["where_to_work"][1]
    assert "posture-sensitive online control is s-tier closed" in status["where_to_work"][2].lower()
    assert "anti-thrash is landed" in status["where_to_work"][2]
    assert "posture truth is single-owned" in status["where_to_work"][2]
    assert "brake tonic EMA" in status["where_to_work"][2]
    assert "route truth stays bounded and non-sovereign" in status["where_to_work"][2]
    assert "live `Q_mem` stays zero" in status["where_to_work"][2]
    assert "host/tool reliability and affordance priors are earned" in status["where_to_work"][2]
    assert "active V2 full communication closure seam" in status["where_to_work"][3]
    assert "model-facing guidance" in status["where_to_work"][3]
    closure_gates = {gate["id"]: gate for gate in status["closure_gates"]}
    assert closure_gates["main_synced"]["status"] == "required"
    assert closure_gates["cleanup_report"]["status"] == "required"
    assert closure_gates["single_truth"]["status"] == "passed"
    assert "Required workflow gate" in closure_gates["main_synced"]["note"]
    assert "Required workflow gate" in closure_gates["cleanup_report"]["note"]


def test_generated_status_doc_includes_system_map_and_next_product_train() -> None:
    text = _read(STATUS_DOC_PATH)

    assert "## System Map" in text
    assert "```mermaid" in text
    assert "## Identity And Research Stance" in text
    assert "## Live Product Truth" in text
    assert "## Current Focus" in text
    assert "## Bio-To-Code Matrix" in text
    assert "## Math To Code Rules" in text
    assert "human executive function" in text
    assert text.index("## Live Product Truth") < text.index("## Bio-To-Code Matrix")
    assert "## Denominator / Completion Context" not in text
    assert "Current full-executive completion:" not in text
    assert "Shippable threshold for the full executive:" not in text
    assert "When user asks where Cortex is at now:" not in text
    assert "background completion context" not in text
    assert "Active quality/risk focus" in text
    assert "## Packet To Code" in text
    assert "## Next Product Train" in text
    assert "host/tool reliability and affordance priors are earned" in text
    assert "`v2-full-communication-closure`" in text
    assert "paid API service-lane command may run without explicit spend approval" in text
    assert "subscription CLI commands are the default no-API-spend watchlist route" in text
    assert "Shipping Product Lane\\nopenai:operator_cli" in text or "Shipping Product Lane" in text
    assert "Shipping default: `openai:operator_cli`" in text
    assert "Workflow gates marked `required` are contractual gates checked by `repo_workflow.py`" in text
    assert "| `main_synced` | `required` |" in text
    assert "| `cleanup_report` | `required` |" in text
    assert "unchanged-condition repetition is taxed only at the exact-family level" in text
    assert "Claude CLI and Codex CLI" in text
    assert "posture-sensitive online control is s-tier closed" in text.lower()
    assert "model-facing guidance" in text
    assert "`visible_burden_sensitivity`" in text


def test_next_product_train_sentence_fields_render_without_outer_backtick_wrap() -> None:
    """Render-quality pin: ``primary_metric``, ``guardrail``, and ``kill_rule`` are
    sentence-form fields whose values may contain inner backticks for inline code
    spans (for example, ``\\`tonic_quiescence\\```). Wrapping the entire value in
    outer backticks would create nested code spans that Markdown renders as
    alternating and reversed code regions (the inverse of intent). The renderer
    at ``internal/truth/generate_status.py`` must emit these three fields without
    an outer backtick wrap, matching the ``executive_benefit`` and ``why_now``
    pattern. Bare-identifier fields (``slug``, ``surface``) stay wrapped."""
    text = _read(STATUS_DOC_PATH)
    lines = text.splitlines()
    for prefix in ("- Primary metric: ", "- Guardrail: ", "- Kill rule: "):
        line = next((line for line in lines if line.startswith(prefix)), None)
        assert line is not None, f"missing {prefix!r} line in CORTEX_STATUS.md"
        first_char = line[len(prefix) : len(prefix) + 1]
        assert first_char != "`", (
            f"render regression: {prefix!r} line is outer-backtick-wrapped, which "
            f"creates nested code spans when the value contains inner backticks. "
            f"Drop the outer wrap in internal/truth/generate_status.py so this "
            f"field matches the executive_benefit / why_now pattern."
        )


def test_front_door_surfaces_point_to_local_first_and_explicit_publish_closeout() -> None:
    agents = _read(AGENTS_PATH)
    status = _read(STATUS_DOC_PATH)

    assert 'close-session --message "scope: end-state summary"' in status
    assert 'close-session --publish --message "scope: end-state summary"' in status
    assert "cleanup-report" in status
    assert "explicit denominator or progress-accounting questions" in agents
    assert "close-session --publish" in agents
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
