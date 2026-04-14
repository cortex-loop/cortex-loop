"""Boundary checks that keep AUX support-side only and removable."""

from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
_RUNTIME_REPLAY_IMPORTER = "cortex/hosts/reference/runtime.py"
_EXPECTED_RUNTIME_REPLAY_IMPORTS = {
    ("cortex.aux.publication", ("OfflineSupportPublication", "augment_snapshot_with_offline_publication")),
    (
        "cortex.aux.support_priors",
        ("build_support_memory_prior_appendix", "filter_live_support_memory_prior_appendix"),
    ),
}


def _is_cortex_aux_import(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(
            alias.name == "cortex.aux" or alias.name.startswith("cortex.aux.")
            for alias in node.names
        )
    if isinstance(node, ast.ImportFrom):
        return node.module == "cortex.aux" or (
            node.module is not None and node.module.startswith("cortex.aux.")
        )
    return False


def _top_level_cortex_aux_imports(tree: ast.Module) -> list[ast.AST]:
    return [node for node in tree.body if _is_cortex_aux_import(node)]


def _runtime_replay_guard(function: ast.FunctionDef) -> ast.If | None:
    for node in function.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare):
            continue
        if not (
            isinstance(test.left, ast.Name)
            and test.left.id == "offline_publication"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.IsNot)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is None
        ):
            continue
        return node
    return None


def _guarded_aux_imports(node: ast.If) -> set[tuple[str | None, tuple[str, ...]]]:
    imports: set[tuple[str | None, tuple[str, ...]]] = set()
    for child in node.body:
        if isinstance(child, ast.Import):
            imports.add((None, tuple(alias.name for alias in child.names)))
        elif isinstance(child, ast.ImportFrom):
            imports.add((child.module, tuple(alias.name for alias in child.names)))
    return imports


def test_non_aux_runtime_and_product_modules_do_not_import_cortex_aux() -> None:
    offenders: list[str] = []

    for path in (REPO_ROOT / "cortex").rglob("*.py"):
        relative = path.relative_to(REPO_ROOT)
        if relative.parts[:2] == ("cortex", "aux"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if _top_level_cortex_aux_imports(tree):
            offenders.append(str(relative))
            continue
        if str(relative) == _RUNTIME_REPLAY_IMPORTER:
            runtime_function = next(
                node
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
                and node.name == "run_reference_runtime_step"
            )
            replay_guard = _runtime_replay_guard(runtime_function)
            assert replay_guard is not None
            assert _guarded_aux_imports(replay_guard) == _EXPECTED_RUNTIME_REPLAY_IMPORTS
            runtime_aux_nodes = [node for node in ast.walk(runtime_function) if _is_cortex_aux_import(node)]
            assert len(runtime_aux_nodes) == len(_EXPECTED_RUNTIME_REPLAY_IMPORTS)
            continue
        if any(_is_cortex_aux_import(node) for node in ast.walk(tree)):
            offenders.append(str(relative))

    assert offenders == []
