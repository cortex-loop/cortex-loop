"""Freeze guards that keep V3 isolated from V2 runtime implementation imports."""

from __future__ import annotations

import json
import subprocess
import sys


def test_cortex_v3_runtime_imports_do_not_pull_v2_runtime_modules() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                "import cortex_v3.engine, cortex_v3.verifier, cortex_v3.providers.openai.adapter; "
                "loaded = sorted(name for name in sys.modules "
                "if name.startswith('cortex.runtime') "
                "or name.startswith('cortex.sre') "
                "or name.startswith('cortex.aux')); "
                "print(json.dumps(loaded))"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    loaded = json.loads(result.stdout.strip())

    assert loaded == []
