#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import internal.workflow.repo_workflow as _impl
from internal.workflow.repo_workflow import main as _main


for _name in dir(_impl):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_impl, _name)


def main(argv: list[str] | None = None) -> int:
    print(
        "scripts/repo_workflow.py is deprecated; use internal/workflow/repo_workflow.py",
        file=sys.stderr,
    )
    return _main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
