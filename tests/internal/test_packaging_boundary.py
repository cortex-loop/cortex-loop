"""Packaging-boundary checks for the shipped Cortex wheel."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import shutil


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_wheel_build_cleans_stale_product_artifacts_and_exposes_only_public_scripts() -> None:
    stale_module = REPO_ROOT / "build" / "lib" / "cortex" / "sre" / "modulators.py"
    stale_module.parent.mkdir(parents=True, exist_ok=True)
    stale_module.write_text("stale = True\n", encoding="utf-8")
    egg_info_dir = REPO_ROOT / "cortex.egg-info"

    try:
        with tempfile.TemporaryDirectory(prefix="cortex-wheel-") as tmp_dir:
            outdir = Path(tmp_dir)
            subprocess.run(
                [sys.executable, "-m", "build", "--wheel", "--outdir", str(outdir)],
                cwd=REPO_ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            wheels = sorted(outdir.glob("cortex-*.whl"))
            assert len(wheels) == 1
            with zipfile.ZipFile(wheels[0]) as wheel:
                names = set(wheel.namelist())
                assert "cortex/sre/modulators.py" not in names
                assert "cortex/sre/executive_summary.py" not in names
                assert all(not name.startswith("experimental/") for name in names)
                assert all(not name.startswith("lab/") for name in names)
                assert all(not name.startswith("internal/") for name in names)
                entry_points = wheel.read("cortex-0.0.0.dist-info/entry_points.txt").decode("utf-8")
                assert "cortex-openai-cli" in entry_points
                assert "cortex-openai-service" in entry_points
                assert "claude" not in entry_points
                assert "gemini" not in entry_points
    finally:
        shutil.rmtree(REPO_ROOT / "build", ignore_errors=True)
        shutil.rmtree(egg_info_dir, ignore_errors=True)
