from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def ensure_repo_root_on_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def export_compat_module(target_globals: dict[str, Any], module_name: str) -> None:
    ensure_repo_root_on_path()
    module = importlib.import_module(module_name)
    wrapper_name = target_globals.get("__name__")
    if isinstance(wrapper_name, str) and wrapper_name != "__main__":
        sys.modules[wrapper_name] = module
    export_names = [name for name in dir(module) if name not in {"__name__", "__file__", "__package__", "__spec__", "__loader__", "__cached__", "__builtins__"}]
    for name in export_names:
        target_globals[name] = getattr(module, name)
    public_names = getattr(module, "__all__", None)
    if public_names is None:
        public_names = [name for name in export_names if not name.startswith("_")]
    target_globals["__all__"] = list(public_names)


def run_compat_main(module_name: str, argv: list[str] | None = None) -> int:
    ensure_repo_root_on_path()
    print(
        f"tools compatibility wrapper is deprecated; use {module_name.replace('.', '/')}.py",
        file=sys.stderr,
    )
    module = importlib.import_module(module_name)
    main = getattr(module, "main", None)
    if not callable(main):
        raise SystemExit(f"{module_name} does not expose a callable main().")
    result = main(argv)
    return int(result) if isinstance(result, int) else 0
