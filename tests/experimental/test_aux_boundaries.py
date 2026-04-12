"""Boundary checks that keep AUX support-side only and removable."""

from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
_ALLOWED_NON_AUX_IMPORTERS = {
    "cortex/hosts/reference/runtime.py",
}


def test_non_aux_runtime_and_product_modules_do_not_import_cortex_aux() -> None:
    offenders: list[str] = []

    for path in (REPO_ROOT / "cortex").rglob("*.py"):
        relative = path.relative_to(REPO_ROOT)
        if relative.parts[:2] == ("cortex", "aux"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "cortex.aux" or alias.name.startswith("cortex.aux."):
                        if str(relative) not in _ALLOWED_NON_AUX_IMPORTERS:
                            offenders.append(str(relative))
            elif isinstance(node, ast.ImportFrom):
                if node.module == "cortex.aux" or (
                    node.module is not None and node.module.startswith("cortex.aux.")
                ):
                    if str(relative) not in _ALLOWED_NON_AUX_IMPORTERS:
                        offenders.append(str(relative))

    assert offenders == []
