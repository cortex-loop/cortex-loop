"""Deterministic V2/V3 parity harness for the verified-work surface."""

from __future__ import annotations

import argparse
import difflib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cortex.runtime.verified_work_runtime import (
    build_verified_work_input_text as v2_build_input_text,
    build_verified_work_instructions as v2_build_instructions,
    build_verified_work_repair_ticket as v2_build_repair_ticket,
    verify_verified_work_result as v2_verify,
)
from cortex.sre.preservation import derive_preservation_state as v2_derive_preservation_state
from cortex.sre.verified_work import VerificationOutcome as V2VerificationOutcome
from cortex.sre.verified_work import WorkContract as V2WorkContract
from cortex_v3.contracts import VerificationOutcome as V3VerificationOutcome
from cortex_v3.contracts import WorkContract as V3WorkContract
from cortex_v3.preservation import derive_preservation_state as v3_derive_preservation_state
from cortex_v3.verifier import (
    build_verified_work_input_text as v3_build_input_text,
    build_verified_work_instructions as v3_build_instructions,
    build_verified_work_repair_ticket as v3_build_repair_ticket,
    verify_verified_work_result as v3_verify,
)
from lab.v3.parity_oracle import (
    broken_payload_for_task,
    v2_passing_payload_for_task,
    v3_passing_payload_for_task,
)


_BOOKMARKS_V2_CONTRACT = V2WorkContract(
    allowed_write_paths=(
        "src/bookmarks_api/main.py",
        "src/bookmarks_api/models.py",
        "src/bookmarks_api/store.py",
    ),
    verification_profile="python_workspace_pytest_v1",
    output_carrier="full_files",
    max_repair_turns=1,
)
_BOOKMARKS_V3_CONTRACT = V3WorkContract(
    allowed_write_paths=_BOOKMARKS_V2_CONTRACT.allowed_write_paths,
    verification_profile=_BOOKMARKS_V2_CONTRACT.verification_profile,
    output_carrier=_BOOKMARKS_V2_CONTRACT.output_carrier,
    max_repair_turns=_BOOKMARKS_V2_CONTRACT.max_repair_turns,
)
_PROJECT_V2_CONTRACT = V2WorkContract(
    allowed_write_paths=("src/normalize_port.py",),
    verification_profile="python_workspace_pytest_port_fix_v1",
    output_carrier="full_files",
    max_repair_turns=1,
)
_PROJECT_V3_CONTRACT = V3WorkContract(
    allowed_write_paths=_PROJECT_V2_CONTRACT.allowed_write_paths,
    verification_profile=_PROJECT_V2_CONTRACT.verification_profile,
    output_carrier=_PROJECT_V2_CONTRACT.output_carrier,
    max_repair_turns=_PROJECT_V2_CONTRACT.max_repair_turns,
)
_FEATURE_FLAGS_V2_CONTRACT = V2WorkContract(
    allowed_write_paths=(
        "src/feature_flags/models.py",
        "src/feature_flags/evaluator.py",
    ),
    verification_profile="python_workspace_pytest_feature_flags_v1",
    output_carrier="full_files",
    max_repair_turns=1,
)
_FEATURE_FLAGS_V3_CONTRACT = V3WorkContract(
    allowed_write_paths=_FEATURE_FLAGS_V2_CONTRACT.allowed_write_paths,
    verification_profile=_FEATURE_FLAGS_V2_CONTRACT.verification_profile,
    output_carrier=_FEATURE_FLAGS_V2_CONTRACT.output_carrier,
    max_repair_turns=_FEATURE_FLAGS_V2_CONTRACT.max_repair_turns,
)

_TASK_SPECS = (
    (
        "bookmarks_app_template",
        _BOOKMARKS_V2_CONTRACT,
        _BOOKMARKS_V3_CONTRACT,
        "build bookmarks app",
        v2_passing_payload_for_task("bookmarks_app_template"),
        v3_passing_payload_for_task("bookmarks_app_template"),
        broken_payload_for_task("bookmarks_app_template"),
    ),
    (
        "project_template",
        _PROJECT_V2_CONTRACT,
        _PROJECT_V3_CONTRACT,
        "fix normalize_port",
        v2_passing_payload_for_task("project_template"),
        v3_passing_payload_for_task("project_template"),
        broken_payload_for_task("project_template"),
    ),
    (
        "feature_flags_template",
        _FEATURE_FLAGS_V2_CONTRACT,
        _FEATURE_FLAGS_V3_CONTRACT,
        "fix feature flag evaluator",
        v2_passing_payload_for_task("feature_flags_template"),
        v3_passing_payload_for_task("feature_flags_template"),
        broken_payload_for_task("feature_flags_template"),
    ),
)


def compare_instructions(task: tuple[str, V2WorkContract, V3WorkContract, str, str, str, str]) -> dict[str, Any]:
    task_id, v2_contract, v3_contract, _task_prompt, _v2_completion_text, _v3_completion_text, _broken_completion_text = task
    v2_value = v2_build_instructions(v2_contract)
    v3_value = v3_build_instructions(v3_contract)
    return _string_row(
        axis="instructions",
        task_id=task_id,
        completion_source="shared",
        v2_value=v2_value,
        v3_value=v3_value,
    )


def compare_input_text(task: tuple[str, V2WorkContract, V3WorkContract, str, str, str, str]) -> dict[str, Any]:
    task_id, v2_contract, v3_contract, task_prompt, _v2_completion_text, _v3_completion_text, _broken_completion_text = task
    v2_value = v2_build_input_text(task_prompt, v2_contract)
    v3_value = v3_build_input_text(task_prompt, v3_contract)
    return _string_row(
        axis="input_text",
        task_id=task_id,
        completion_source="shared",
        v2_value=v2_value,
        v3_value=v3_value,
    )


def compare_repair_ticket(task: tuple[str, V2WorkContract, V3WorkContract, str, str, str, str]) -> dict[str, Any]:
    task_id, v2_contract, v3_contract, _task_prompt, _v2_completion_text, _v3_completion_text, broken_completion_text = task
    _v2_file_map, v2_outcome = v2_verify(broken_completion_text, v2_contract)
    _v3_file_map, v3_outcome = v3_verify(broken_completion_text, v3_contract)
    _require_repairable_failure(task_id, "v2", v2_outcome)
    _require_repairable_failure(task_id, "v3", v3_outcome)
    v2_state = v2_derive_preservation_state(
        None,
        v2_contract,
        v2_outcome.parsed_paths,
        v2_outcome,
        remaining_repairs=1,
    )
    v3_state = v3_derive_preservation_state(
        None,
        v3_contract,
        v3_outcome,
        remaining_repairs=1,
    )
    return _string_row(
        axis="repair_ticket",
        task_id=task_id,
        completion_source="shared",
        v2_value=v2_build_repair_ticket(v2_state),
        v3_value=v3_build_repair_ticket(v3_state),
    )


def compare_verification(
    task: tuple[str, V2WorkContract, V3WorkContract, str, str, str, str],
    *,
    completion_source: str,
) -> dict[str, Any]:
    task_id, v2_contract, v3_contract, _task_prompt, v2_completion_text, v3_completion_text, _broken_completion_text = task
    completion_text = v2_completion_text if completion_source == "v2" else v3_completion_text
    _v2_file_map, v2_outcome = v2_verify(completion_text, v2_contract)
    _v3_file_map, v3_outcome = v3_verify(completion_text, v3_contract)
    v2_value = _normalize_outcome(v2_outcome)
    v3_value = _normalize_outcome(v3_outcome)
    divergence_keys = sorted(key for key in v2_value if v2_value[key] != v3_value[key])
    equal = not divergence_keys
    return {
        "axis": "verification",
        "task_id": task_id,
        "completion_source": completion_source,
        "v2": v2_value,
        "v3": v3_value,
        "equal": equal,
        "divergence_keys": divergence_keys,
        "diff_text": "" if equal else _diff_text(json.dumps(v2_value, indent=2, sort_keys=True), json.dumps(v3_value, indent=2, sort_keys=True)),
    }


def run_all_checks() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in _TASK_SPECS:
        rows.append(compare_instructions(task))
        rows.append(compare_input_text(task))
        rows.append(compare_repair_ticket(task))
        rows.append(compare_verification(task, completion_source="v2"))
        rows.append(compare_verification(task, completion_source="v3"))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    started_at = _timestamp()
    rows = run_all_checks()
    rows.sort(key=lambda row: (row["task_id"], row["axis"], row["completion_source"]))
    divergence_count = sum(1 for row in rows if not row["equal"])
    payload = {
        "started_at": started_at,
        "completed_at": _timestamp(),
        "rows": rows,
        "divergence_count": divergence_count,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} rows to {output_path}; divergence_count={divergence_count}")
    return 0


def _string_row(
    *,
    axis: str,
    task_id: str,
    completion_source: str,
    v2_value: str,
    v3_value: str,
) -> dict[str, Any]:
    equal = v2_value == v3_value
    return {
        "axis": axis,
        "task_id": task_id,
        "completion_source": completion_source,
        "v2": v2_value,
        "v3": v3_value,
        "equal": equal,
        "divergence_keys": [] if equal else ["text"],
        "diff_text": "" if equal else _diff_text(v2_value, v3_value),
    }


def _normalize_outcome(outcome: Any) -> dict[str, Any]:
    return {
        "status": outcome.status,
        "failure_class": outcome.failure_class,
        "parsed_paths": sorted(outcome.parsed_paths),
        "import_smoke_ok": outcome.import_smoke_ok,
        "pytest_passed": outcome.pytest_passed,
        "pytest_failed": outcome.pytest_failed,
        "failing_tests": sorted(outcome.failing_tests),
    }


def _require_repairable_failure(task_id: str, side: str, outcome: Any) -> None:
    if outcome.status != "failed" or outcome.failure_class not in {"import_smoke_failed", "test_failed"}:
        raise RuntimeError(
            f"Parity oracle for {task_id!r} did not produce a repairable {side} outcome: "
            f"status={outcome.status!r} failure_class={outcome.failure_class!r}."
        )


def _diff_text(v2_value: str, v3_value: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            v2_value.splitlines(),
            v3_value.splitlines(),
            fromfile="v2",
            tofile="v3",
            lineterm="",
        )
    )


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
