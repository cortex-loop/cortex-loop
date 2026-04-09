from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class CleanBuildPy(_build_py):
    """Prevent stale deleted modules from leaking into rebuilt wheels."""

    def run(self) -> None:
        build_root = Path(self.build_lib) / "cortex"
        if build_root.exists():
            shutil.rmtree(build_root)
        super().run()


setup(cmdclass={"build_py": CleanBuildPy})
