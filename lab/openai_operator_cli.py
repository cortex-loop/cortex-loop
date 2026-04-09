"""Small OpenAI operator-cli helpers for evaluation-only watchlist flows."""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:  # pragma: no cover
    from . import live_openai_app_server_operator as openai_operator
    from .live_validation_common import MODEL_MATRIX, choose_model
except ImportError:  # pragma: no cover
    import live_openai_app_server_operator as openai_operator
    from lab.live_validation_common import MODEL_MATRIX, choose_model


@contextmanager
def isolated_codex_home_env() -> Iterator[dict[str, str]]:
    """Provide a CODEX_HOME carrying only auth.json for raw/tooling watchlist runs."""
    codex_auth_path = Path.home() / ".codex" / "auth.json"
    if not codex_auth_path.exists():
        raise RuntimeError("OpenAI operator run requires ~/.codex/auth.json")
    tmp_root = Path(tempfile.mkdtemp(prefix="cortex-openai-operator-"))
    try:
        shutil.copy2(codex_auth_path, tmp_root / "auth.json")
        env = dict(os.environ)
        env["CODEX_HOME"] = str(tmp_root)
        yield env
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def run_openai_operator_single_turn(
    *,
    project_root: Path,
    prompt: str,
    scenario_id: str,
    stderr_path: Path,
    ephemeral: bool = True,
    env: dict[str, str] | None = None,
    model: str | None = None,
    auth_mode: str = "codex_cli",
) -> dict[str, Any]:
    preferred_model = model or MODEL_MATRIX["openai"]["operator"].preferred
    attempted_models = [preferred_model]
    state, failure_class = openai_operator._run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=preferred_model,
        scenario_id=scenario_id,
        ephemeral=ephemeral,
        env=env,
        stderr_path=stderr_path,
    )
    chosen_model = preferred_model
    if model is None:
        fallback_model = choose_model("openai", "operator", first_failure=failure_class)
        if fallback_model != preferred_model:
            state, failure_class = openai_operator._run_single_turn(
                project_root=project_root,
                prompt=prompt,
                auth_mode=auth_mode,
                model=fallback_model,
                scenario_id=scenario_id,
                ephemeral=ephemeral,
                env=env,
                stderr_path=stderr_path,
            )
            chosen_model = fallback_model
            attempted_models.append(fallback_model)
    lifecycle_summary = state.get("lifecycle_summary") or {}
    return {
        "state": state,
        "failure_class": failure_class,
        "model": chosen_model,
        "attempted_models": attempted_models,
        "thread_id": state.get("thread_id"),
        "output_text": lifecycle_summary.get("result_text"),
    }


def run_openai_operator_resumed_turn(
    *,
    project_root: Path,
    prompt: str,
    model: str,
    thread_id: str | None,
    stderr_path: Path,
    env: dict[str, str] | None = None,
    auth_mode: str = "codex_cli",
) -> dict[str, Any]:
    state, failure_class = openai_operator._run_resumed_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=model,
        thread_id=thread_id,
        env=env,
        stderr_path=stderr_path,
    )
    lifecycle_summary = state.get("lifecycle_summary") or {}
    return {
        "state": state,
        "failure_class": failure_class,
        "model": model,
        "thread_id": state.get("thread_id"),
        "output_text": lifecycle_summary.get("result_text"),
    }


__all__ = [
    "isolated_codex_home_env",
    "run_openai_operator_resumed_turn",
    "run_openai_operator_single_turn",
]
