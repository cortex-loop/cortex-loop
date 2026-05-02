"""Small OpenAI operator-cli helpers for evaluation-only watchlist flows."""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:  # pragma: no cover
    from .live_validation_common import (
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        extract_result_text,
        parse_json_records,
        run_command,
        write_text,
    )
except ImportError:  # pragma: no cover
    from lab.live_validation_common import (
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        extract_result_text,
        parse_json_records,
        run_command,
        write_text,
    )


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
    state, failure_class = _run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=preferred_model,
        env=env,
        stderr_path=stderr_path,
        ephemeral=ephemeral,
    )
    chosen_model = preferred_model
    if model is None:
        fallback_model = choose_model("openai", "operator", first_failure=failure_class)
        if fallback_model != preferred_model:
            state, failure_class = _run_single_turn(
                project_root=project_root,
                prompt=prompt,
                auth_mode=auth_mode,
                model=fallback_model,
                env=env,
                stderr_path=stderr_path,
                ephemeral=ephemeral,
            )
            chosen_model = fallback_model
            attempted_models.append(fallback_model)
    return {
        "state": state,
        "failure_class": failure_class,
        "model": chosen_model,
        "attempted_models": attempted_models,
        "thread_id": state.get("thread_id"),
        "output_text": state.get("output_text"),
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
    state, failure_class = _run_resumed_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=model,
        thread_id=thread_id,
        env=env,
        stderr_path=stderr_path,
    )
    return {
        "state": state,
        "failure_class": failure_class,
        "model": model,
        "thread_id": state.get("thread_id"),
        "output_text": state.get("output_text"),
    }


def _run_single_turn(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    model: str,
    env: dict[str, str] | None,
    stderr_path: Path,
    ephemeral: bool,
) -> tuple[dict[str, Any], str | None]:
    return _run_codex_exec(
        project_root=project_root,
        prompt=prompt,
        model=model,
        auth_mode=auth_mode,
        env=env,
        stderr_path=stderr_path,
        resume_session=None,
        ephemeral=ephemeral,
    )


def _run_resumed_turn(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    model: str,
    thread_id: str | None,
    env: dict[str, str] | None,
    stderr_path: Path,
) -> tuple[dict[str, Any], str | None]:
    return _run_codex_exec(
        project_root=project_root,
        prompt=prompt,
        model=model,
        auth_mode=auth_mode,
        env=env,
        stderr_path=stderr_path,
        resume_session=thread_id,
        ephemeral=False,
    )


def build_codex_exec_command(
    *,
    prompt: str,
    model: str,
    resume_session: str | None = None,
    ephemeral: bool = True,
) -> list[str]:
    if resume_session:
        return [
            "codex",
            "exec",
            "resume",
            "--json",
            "--full-auto",
            *(["--ephemeral"] if ephemeral else []),
            resume_session,
            prompt,
        ]
    return [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        model,
        *(["--ephemeral"] if ephemeral else []),
        prompt,
    ]


def _run_codex_exec(
    *,
    project_root: Path,
    prompt: str,
    model: str,
    auth_mode: str,
    env: dict[str, str] | None,
    stderr_path: Path,
    resume_session: str | None,
    ephemeral: bool,
) -> tuple[dict[str, Any], str | None]:
    if auth_mode != "codex_cli":
        state = {
            "command": ["codex"],
            "exit_code": 1,
            "stdout": "",
            "stderr": (
                f"openai operator auth mode `{auth_mode}` is not supported by the "
                "OpenAI operator_cli harness."
            ),
            "thread_id": resume_session,
            "output_text": None,
            "started_at": None,
            "ended_at": None,
        }
        return state, "operator_surface_missing"

    command = build_codex_exec_command(
        prompt=prompt,
        model=model,
        resume_session=resume_session,
        ephemeral=ephemeral,
    )
    result = run_command(
        command,
        cwd=project_root,
        env=dict(env) if env is not None else None,
        timeout_seconds=180.0,
    )
    write_text(stderr_path, result["stderr"])
    records, _extraction_mode = parse_json_records(result["stdout"])
    state = {
        **result,
        "records": records,
        "thread_id": _extract_openai_session_id(records),
        "output_text": extract_result_text(records, result["stdout"]),
    }
    failure_class = classify_failure(f"{result['stdout']}\n{result['stderr']}")
    if failure_class is None and result["exit_code"] == 124:
        failure_class = "operator_timeout"
    return state, failure_class


def _extract_openai_session_id(records: list[dict[str, Any]]) -> str | None:
    for record in reversed(records):
        for key in ("session_id", "thread_id", "threadId"):
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


__all__ = [
    "build_codex_exec_command",
    "isolated_codex_home_env",
    "run_openai_operator_resumed_turn",
    "run_openai_operator_single_turn",
]
