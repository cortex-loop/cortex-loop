"""Focused tests for the E12 output-quality common helpers."""

from __future__ import annotations

from pathlib import Path

from lab.output_quality_ablation import OutputQualityAblationConfig
from lab.output_quality_common import (
    OutputQualityTaskPack,
    build_output_quality_capability_diagnostics,
    build_output_quality_input_text,
    build_file_block_protocol,
    parse_output_quality_result,
    prepare_output_quality_hidden_evaluator_workspace,
    prepare_output_quality_subject_workspace,
)


def _task_pack(tmp_path: Path) -> OutputQualityTaskPack:
    template_root = tmp_path / "template"
    for relative_path, contents in {
        "src/app.ts": "export const value = 1;\n",
        "README_TASK.md": "Implement this cleanly.\n",
        "package.json": (
            '{\n'
            '  "scripts": {\n'
            '    "test:visible": "echo visible",\n'
            '    "test:hidden": "echo hidden"\n'
            "  }\n"
            "}\n"
        ),
        "tests/visible.spec.ts": "expect(true).toBe(true);\n",
        "tests/_verifier/hidden.spec.ts": "expect(true).toBe(true);\n",
    }.items():
        target = template_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
    return OutputQualityTaskPack(
        task_id="sample",
        prompt_text="Implement this in a clean, maintainable way.",
        template_root=template_root,
        allowed_write_paths=("src/app.ts",),
        visible_context_paths=("README_TASK.md", "tests/visible.spec.ts"),
        verifier_only_paths=("tests/_verifier/hidden.spec.ts",),
        install_command=("echo", "install"),
        lint_command=("echo", "lint"),
        typecheck_command=("echo", "typecheck"),
        build_command=("echo", "build"),
        visible_test_command=("echo", "visible"),
        hidden_test_command=("npm", "run", "test:hidden"),
    )


def test_build_output_quality_input_text_hides_verifier_only_context(tmp_path: Path) -> None:
    task_pack = _task_pack(tmp_path)

    raw_input = build_output_quality_input_text(task_pack, arm="raw")
    tooling_input = build_output_quality_input_text(task_pack, arm="tooling_only")

    assert "=== CONTEXT FILE:" not in raw_input
    assert "Visible contract files follow. Additional verifier-only checks may run." in tooling_input
    assert "=== CONTEXT FILE: src/app.ts ===" in tooling_input
    assert "=== CONTEXT FILE: README_TASK.md ===" in tooling_input
    assert "hidden.spec.ts" not in tooling_input


def test_subject_workspace_hides_verifier_only_files_and_hidden_script(tmp_path: Path) -> None:
    task_pack = _task_pack(tmp_path)

    subject = prepare_output_quality_subject_workspace(
        task_pack=task_pack,
        run_root=tmp_path / "subject",
    )

    assert not (subject / "tests/_verifier/hidden.spec.ts").exists()
    assert "test:hidden" not in (subject / "package.json").read_text(encoding="utf-8")
    assert (subject / "tests/visible.spec.ts").exists()


def test_hidden_evaluator_workspace_restores_verifier_only_files(tmp_path: Path) -> None:
    task_pack = _task_pack(tmp_path)
    subject = prepare_output_quality_subject_workspace(
        task_pack=task_pack,
        run_root=tmp_path / "subject",
    )

    evaluator = prepare_output_quality_hidden_evaluator_workspace(
        task_pack=task_pack,
        subject_project_root=subject,
        run_root=tmp_path / "evaluator",
    )

    assert (evaluator / "tests/_verifier/hidden.spec.ts").exists()
    assert "test:hidden" in (evaluator / "package.json").read_text(encoding="utf-8")
    assert not (subject / "tests/_verifier/hidden.spec.ts").exists()


def test_build_output_quality_input_text_supports_ablation_variants(tmp_path: Path) -> None:
    task_pack = _task_pack(tmp_path)

    no_context = build_output_quality_input_text(
        task_pack,
        arm="cortex",
        ablation_config=OutputQualityAblationConfig(visible_contract_binding="off"),
    )
    writable_only = build_output_quality_input_text(
        task_pack,
        arm="cortex",
        ablation_config=OutputQualityAblationConfig(
            visible_context_variant="writable_files_only",
        ),
    )

    assert "=== CONTEXT FILE:" not in no_context
    assert "=== CONTEXT FILE: src/app.ts ===" in writable_only
    assert "=== CONTEXT FILE: README_TASK.md ===" not in writable_only
    assert "=== CONTEXT FILE: tests/visible.spec.ts ===" not in writable_only


def test_build_file_block_protocol_supports_lean_contract_profile() -> None:
    protocol = build_file_block_protocol(
        ("src/app.ts",),
        contract_binding_profile="lean",
    )

    assert "The output for this work is protocol blocks only." in protocol
    assert "Do not include explanations" not in protocol


def test_build_output_quality_capability_diagnostics_marks_spark_as_bounded_and_lean() -> None:
    diagnostics = build_output_quality_capability_diagnostics("gpt-5.3-codex-spark")

    assert diagnostics["brain_capability_band"] == "bounded"
    assert diagnostics["brain_capability_mismatch"]["level"] == "degrade"
    assert diagnostics["contract_binding_profile"] == "lean"


def test_parse_output_quality_result_accepts_full_file_blocks() -> None:
    result = parse_output_quality_result(
        "=== FILE: src/app.ts ===\nexport const value = 2;\n=== END FILE ===\n",
        allowed_write_paths=("src/app.ts",),
    )

    assert result.parse_error is None
    assert result.file_map == {"src/app.ts": "export const value = 2;\n"}
    assert result.failure_class is None


def test_parse_output_quality_result_rejects_unapproved_paths() -> None:
    result = parse_output_quality_result(
        "=== FILE: src/other.ts ===\nexport const value = 2;\n=== END FILE ===\n",
        allowed_write_paths=("src/app.ts",),
    )

    assert result.file_map is None
    assert result.failure_class == "output_invalid"
    assert "unapproved path" in (result.parse_error or "")


def test_parse_output_quality_result_accepts_blocked_marker() -> None:
    result = parse_output_quality_result(
        "=== BLOCKED: needs_user_input ===\nNeed the API schema.\n=== END BLOCKED ===\n",
        allowed_write_paths=("src/app.ts",),
    )

    assert result.file_map is None
    assert result.parse_error is None
    assert result.blocked_reason == "needs_user_input"
    assert result.blocked_message == "Need the API schema."
    assert result.failure_class == "blocked_missing_info"
