from __future__ import annotations

from pathlib import Path

from internal.workflow import product_spine


def test_fixture_identity_terms_include_output_quality_fixture_dirs(tmp_path: Path) -> None:
    fixture_root = tmp_path / "tests" / "lab" / "fixtures" / "output_quality"
    (fixture_root / "astro_docs_site_v1").mkdir(parents=True)
    (fixture_root / "kernel_optimization_v1").mkdir()

    terms = product_spine.fixture_identity_terms(tmp_path)

    assert "astro_docs_site_v1" in terms
    assert "kernel_optimization_v1" in terms
    assert "docs search dataset marker" in terms


def test_task_identity_terms_are_examples_not_closed_doctrine(tmp_path: Path) -> None:
    fixture_root = tmp_path / "tests" / "lab" / "fixtures" / "output_quality"
    (fixture_root / "astro_docs_site_v1").mkdir(parents=True)

    terms = product_spine.task_identity_terms(tmp_path)

    assert product_spine.TaskIdentityTerm(
        term="astro_docs_site_v1",
        category="lab_fixture_identity",
        source="tests/lab/fixtures/output_quality/astro_docs_site_v1",
    ) in terms
    assert product_spine.TaskIdentityTerm(
        term="docs search dataset marker",
        category="hidden_verifier_fact",
        source="static example",
    ) in terms


def test_product_fixture_leak_scanner_rejects_fixture_identity_in_cortex_code(
    tmp_path: Path,
) -> None:
    fixture_root = tmp_path / "tests" / "lab" / "fixtures" / "output_quality"
    (fixture_root / "astro_docs_site_v1").mkdir(parents=True)
    product_file = tmp_path / "cortex" / "hosts" / "openai" / "adapter.py"
    product_file.parent.mkdir(parents=True)
    product_file.write_text(
        "def route(task_id):\n"
        "    return task_id == 'astro_docs_site_v1'\n",
        encoding="utf-8",
    )

    leaks = product_spine.find_product_fixture_leaks(tmp_path)

    assert len(leaks) == 1
    assert leaks[0].path == "cortex/hosts/openai/adapter.py"
    assert leaks[0].term == "astro_docs_site_v1"
    assert leaks[0].category == "lab_fixture_identity"


def test_product_fixture_leak_scanner_allows_fixture_terms_outside_cortex(
    tmp_path: Path,
) -> None:
    fixture_root = tmp_path / "tests" / "lab" / "fixtures" / "output_quality"
    (fixture_root / "astro_docs_site_v1").mkdir(parents=True)
    lab_file = tmp_path / "lab" / "probe.py"
    lab_file.parent.mkdir()
    lab_file.write_text("TASK = 'astro_docs_site_v1'\n", encoding="utf-8")

    assert product_spine.find_product_fixture_leaks(tmp_path) == ()


def test_product_task_identity_leak_scanner_rejects_hidden_verifier_fact(
    tmp_path: Path,
) -> None:
    product_file = tmp_path / "cortex" / "hosts" / "openai" / "adapter.py"
    product_file.parent.mkdir(parents=True)
    product_file.write_text(
        "def route(message):\n"
        "    return 'docs search dataset marker' in message\n",
        encoding="utf-8",
    )

    leaks = product_spine.find_product_task_identity_leaks(tmp_path)

    assert len(leaks) == 1
    assert leaks[0].term == "docs search dataset marker"
    assert leaks[0].category == "hidden_verifier_fact"
