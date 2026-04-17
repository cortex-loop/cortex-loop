"""Lab-owned oracle payloads for deterministic V2/V3 parity checks."""

from __future__ import annotations

from lab.v3.fixture_payloads import fixture_payload_for_task

_TASK_IDS = (
    "bookmarks_app_template",
    "project_template",
    "feature_flags_template",
)

_V2_PASSING_RESULTS = {task_id: fixture_payload_for_task(task_id) for task_id in _TASK_IDS}
_V3_PASSING_RESULTS = {task_id: fixture_payload_for_task(task_id) for task_id in _TASK_IDS}

_BROKEN_FILE_BODIES = {
    "bookmarks_app_template": (
        "src/bookmarks_api/main.py",
        "from fastapi import FastAPI\napp = FastAPI(\n",
    ),
    "project_template": (
        "src/normalize_port.py",
        "from __future__ import annotations\n\n\n"
        "def normalize_port(value: int | str) -> int:\n"
        "    port = int(value)\n"
        "    if port < 0:\n"
        '        raise ValueError("port must be non-negative")\n'
        "    if port >= 65535:\n"
        '        raise ValueError("port must be <= 65535")\n'
        "    return port\n",
    ),
    "feature_flags_template": (
        "src/feature_flags/evaluator.py",
        "from __future__ import annotations\n\n"
        "from .models import FeatureFlag\n\n\n"
        "def is_flag_active(flag: FeatureFlag, *, user_key: str, country: str) -> bool:\n"
        "    return True\n",
    ),
}


def v2_passing_payload_for_task(task_id: str) -> str:
    return _lookup_payload(task_id, _V2_PASSING_RESULTS, label="V2 passing")


def v3_passing_payload_for_task(task_id: str) -> str:
    return _lookup_payload(task_id, _V3_PASSING_RESULTS, label="V3 passing")


def broken_payload_for_task(task_id: str) -> str:
    try:
        path, replacement = _BROKEN_FILE_BODIES[task_id]
    except KeyError as exc:
        raise ValueError(
            f"No deterministic broken parity payload is registered for task_id={task_id!r}."
        ) from exc
    return _replace_file_block(v2_passing_payload_for_task(task_id), path, replacement)


def _lookup_payload(task_id: str, payloads: dict[str, str], *, label: str) -> str:
    try:
        return payloads[task_id]
    except KeyError as exc:
        raise ValueError(
            f"No {label} parity payload is registered for task_id={task_id!r}."
        ) from exc


def _replace_file_block(result_text: str, path: str, replacement: str) -> str:
    header = f"=== FILE: {path} ===\n"
    body_start = result_text.find(header)
    if body_start < 0:
        raise ValueError(f"Parity oracle payload is missing file block for path={path!r}.")
    body_start += len(header)
    body_end = result_text.find("\n=== END FILE ===", body_start)
    if body_end < 0:
        raise ValueError(f"Parity oracle payload has an unterminated file block for path={path!r}.")
    return result_text[:body_start] + replacement.rstrip("\n") + result_text[body_end:]


__all__ = [
    "broken_payload_for_task",
    "v2_passing_payload_for_task",
    "v3_passing_payload_for_task",
]
