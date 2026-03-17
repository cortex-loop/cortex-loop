"""Focused tests for the narrow provenance helper slice."""

from pathlib import Path

from cortex.core.provenance import (
    RepositorySnapshot,
    changed_files_since_baseline,
    extract_requirement_ids,
    repository_snapshot,
)


def test_requirement_id_extraction_prefers_direct_ids_and_deduplicates() -> None:
    payload = {
        "required_requirement_ids": ["req-1", "req-1", "req-2"],
        "task_contract": {"required_requirement_ids": ["req-3"]},
    }

    result = extract_requirement_ids(payload)

    assert result == ("req-1", "req-2")


def test_requirement_id_extraction_falls_back_to_nested_contract_ids() -> None:
    payload = {
        "task": {
            "contract": {
                "required_ids": ["req-3", "req-3", "req-4"],
            }
        }
    }

    result = extract_requirement_ids(payload)

    assert result == ("req-3", "req-4")


def test_repository_snapshot_reports_unavailable_without_git_marker(tmp_path: Path) -> None:
    snapshot = repository_snapshot(tmp_path)

    assert snapshot.available is False
    assert snapshot.changed_files == ()
    assert snapshot.error_reason == "git repository marker not found"
    assert snapshot.repository_root is None


def test_changed_files_since_baseline_returns_delta_when_snapshots_are_available() -> None:
    baseline = RepositorySnapshot(
        available=True,
        changed_files=("docs/guide.md", "src/app.py"),
        repository_root=Path("/repo"),
    )
    current = RepositorySnapshot(
        available=True,
        changed_files=("docs/guide.md", "src/app.py", "tests/test_app.py"),
        repository_root=Path("/repo"),
    )

    delta = changed_files_since_baseline(
        baseline_snapshot=baseline,
        current_snapshot=current,
    )

    assert delta.changed_files == ("tests/test_app.py",)
    assert delta.reason is None


def test_changed_files_since_baseline_returns_reason_when_snapshot_unavailable() -> None:
    baseline = RepositorySnapshot(
        available=False,
        changed_files=(),
        error_reason="baseline repository snapshot unavailable",
        repository_root=None,
    )
    current = RepositorySnapshot(
        available=True,
        changed_files=("src/app.py",),
        repository_root=Path("/repo"),
    )

    delta = changed_files_since_baseline(
        baseline_snapshot=baseline,
        current_snapshot=current,
    )

    assert delta.changed_files is None
    assert delta.reason == "baseline repository snapshot unavailable"
