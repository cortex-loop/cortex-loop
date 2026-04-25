from __future__ import annotations

try:
    from tools._compat import export_compat_module, run_compat_main
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools._compat import export_compat_module, run_compat_main

export_compat_module(globals(), "lab.agent_loop_guard")

if __name__ == "__main__":
    raise SystemExit(run_compat_main("lab.agent_loop_guard"))
