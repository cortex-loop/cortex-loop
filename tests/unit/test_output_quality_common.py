"""Focused tests for the E12 output-quality common helpers."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from output_quality_ablation import OutputQualityAblationConfig
from output_quality_common import (
    OutputQualityTaskPack,
    build_output_quality_input_text,
    parse_output_quality_result,
)


def _task_pack(tmp_path: Path) -> OutputQualityTaskPack:
    template_root = tmp_path / "template"
    for relative_path, contents in {
        "src/app.ts": "export const value = 1;\n",
        "README_TASK.md": "Implement this cleanly.\n",
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
        hidden_test_command=("echo", "hidden"),
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
