"""Deterministic tests for the real-work replay pack miner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import real_work_replay_pack as replay_pack
from lab.output_quality_common import OutputQualityTaskPack


def _task_pack(tmp_path: Path, *, task_id: str, allowed_write_paths: tuple[str, ...]) -> OutputQualityTaskPack:
    template_root = tmp_path / "templates" / task_id
    template_root.mkdir(parents=True, exist_ok=True)
    return OutputQualityTaskPack(
        task_id=task_id,
        prompt_text=f"{task_id} prompt",
        template_root=template_root,
        allowed_write_paths=allowed_write_paths,
        visible_context_paths=(),
        verifier_only_paths=(),
        install_command=("npm", "ci"),
        lint_command=("npm", "run", "lint"),
        typecheck_command=("npm", "run", "typecheck"),
        build_command=("npm", "run", "build"),
        visible_test_command=("npm", "run", "test:visible"),
        hidden_test_command=("npm", "run", "test:hidden"),
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_case_artifacts(
    repo_root: Path,
    *,
    artifact_root_relpath: str,
    task_id: str,
    task_pack: OutputQualityTaskPack,
    changed_paths: tuple[str, ...],
    repairable: bool = True,
    failure_class: str = "output_invalid",
) -> dict:
    artifact_root = repo_root / artifact_root_relpath / task_id
    seed_root = artifact_root / "seed" / "project_a"
    workspace_root = artifact_root / "cortex" / "workspace" / "project_a"
    for relative_path in task_pack.allowed_write_paths:
        seed_text = f"seed::{task_id}::{relative_path}\n"
        workspace_text = (
            f"workspace::{task_id}::{relative_path}\n"
            if relative_path in changed_paths
            else seed_text
        )
        _write_text(seed_root / relative_path, seed_text)
        _write_text(workspace_root / relative_path, workspace_text)
    attempt1_payload = {
        "input_text": f"{task_id} prompt\n\nMore detail.",
        "evaluation": {
            "status": "failed",
            "failure_class": failure_class,
        },
        "parse": {
            "parse_error": f"unexpected line outside file block: {task_id}",
            "blocked_reason": None,
            "blocked_message": None,
            "parsed_paths": [],
        },
        "changed_files": {},
        "repairable": repairable,
    }
    _write_text(
        artifact_root / "cortex" / "attempt1" / "result.json",
        json.dumps(attempt1_payload, indent=2, sort_keys=True),
    )
    attempt2_payload = {
        "evaluation": {
            "status": "failed",
            "failure_class": failure_class,
        },
        "parse": {
            "parse_error": "operator completed without workspace edits",
            "blocked_reason": None,
            "blocked_message": None,
            "parsed_paths": [],
        },
        "changed_files": {},
    }
    _write_text(
        artifact_root / "cortex" / "attempt2" / "result.json",
        json.dumps(attempt2_payload, indent=2, sort_keys=True),
    )
    return {
        "arms": {
            "cortex": {
                "attempt1": attempt1_payload,
                "repairable": repairable,
            }
        }
    }


def test_build_real_work_replay_pack_recovers_changed_files_and_selects_one_per_framework(
    tmp_path: Path,
    monkeypatch,
) -> None:
    packs = {
        "astro_small_v1": _task_pack(
            tmp_path,
            task_id="astro_small_v1",
            allowed_write_paths=("src/pages/docs/index.astro",),
        ),
        "astro_large_v1": _task_pack(
            tmp_path,
            task_id="astro_large_v1",
            allowed_write_paths=("src/pages/docs/index.astro", "src/lib/docs.astro"),
        ),
        "react_alpha_v1": _task_pack(
            tmp_path,
            task_id="react_alpha_v1",
            allowed_write_paths=("src/App.tsx", "src/routes/Page.tsx"),
        ),
        "react_beta_v1": _task_pack(
            tmp_path,
            task_id="react_beta_v1",
            allowed_write_paths=("src/App.tsx", "src/routes/Page.tsx"),
        ),
    }
    monkeypatch.setattr(replay_pack, "task_pack_by_name", lambda task_id: packs[task_id])

    artifact_root_relpath = ".cortex/live_validation/output_quality/openai_operator_cli/run_test"
    task_results = {
        "astro_small_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="astro_small_v1",
            task_pack=packs["astro_small_v1"],
            changed_paths=("src/pages/docs/index.astro",),
        ),
        "astro_large_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="astro_large_v1",
            task_pack=packs["astro_large_v1"],
            changed_paths=("src/pages/docs/index.astro", "src/lib/docs.astro"),
        ),
        "react_alpha_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="react_alpha_v1",
            task_pack=packs["react_alpha_v1"],
            changed_paths=("src/App.tsx", "src/routes/Page.tsx"),
        ),
        "react_beta_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="react_beta_v1",
            task_pack=packs["react_beta_v1"],
            changed_paths=("src/App.tsx", "src/routes/Page.tsx"),
        ),
    }
    summary_path = tmp_path / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json"
    _write_text(
        summary_path,
        json.dumps(
            {
                "provider": "openai",
                "surface": "operator_cli",
                "artifact_root": artifact_root_relpath,
                "task_results": task_results,
            },
            indent=2,
            sort_keys=True,
        ),
    )

    pack = replay_pack.build_real_work_replay_pack(
        repo_root=tmp_path,
        summary_path=summary_path,
    )

    assert len(pack.cases) == 4
    assert pack.framework_coverage == ("astro", "react")
    assert pack.selected_case_ids == (
        "openai_operator_cli_astro_large_v1_output_invalid",
        "openai_operator_cli_react_alpha_v1_output_invalid",
    )
    astro_case = next(case for case in pack.cases if case.task_id == "astro_large_v1")
    assert astro_case.changed_paths == (
        "src/lib/docs.astro",
        "src/pages/docs/index.astro",
    )
    assert astro_case.final_workspace_matches_attempt1_candidate is True


def test_build_real_work_replay_pack_skips_nonreplayable_cases(
    tmp_path: Path,
    monkeypatch,
) -> None:
    packs = {
        "astro_valid_v1": _task_pack(
            tmp_path,
            task_id="astro_valid_v1",
            allowed_write_paths=("src/pages/docs/index.astro",),
        ),
        "react_empty_v1": _task_pack(
            tmp_path,
            task_id="react_empty_v1",
            allowed_write_paths=("src/App.tsx",),
        ),
    }
    monkeypatch.setattr(replay_pack, "task_pack_by_name", lambda task_id: packs[task_id])
    artifact_root_relpath = ".cortex/live_validation/output_quality/openai_operator_cli/run_test"
    task_results = {
        "astro_valid_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="astro_valid_v1",
            task_pack=packs["astro_valid_v1"],
            changed_paths=("src/pages/docs/index.astro",),
        ),
        "react_empty_v1": _write_case_artifacts(
            tmp_path,
            artifact_root_relpath=artifact_root_relpath,
            task_id="react_empty_v1",
            task_pack=packs["react_empty_v1"],
            changed_paths=(),
        ),
    }
    summary_path = tmp_path / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json"
    _write_text(
        summary_path,
        json.dumps(
            {
                "provider": "openai",
                "surface": "operator_cli",
                "artifact_root": artifact_root_relpath,
                "task_results": task_results,
            },
            indent=2,
            sort_keys=True,
        ),
    )

    pack = replay_pack.build_real_work_replay_pack(
        repo_root=tmp_path,
        summary_path=summary_path,
    )

    assert [case.task_id for case in pack.cases] == ["astro_valid_v1"]


def test_write_real_work_replay_pack_artifact_writes_file_maps(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pack_obj = _task_pack(
        tmp_path,
        task_id="astro_docs_site_v1",
        allowed_write_paths=("src/pages/docs/index.astro",),
    )
    monkeypatch.setattr(replay_pack, "task_pack_by_name", lambda task_id: pack_obj)
    artifact_root_relpath = ".cortex/live_validation/output_quality/openai_operator_cli/run_test"
    summary_path = tmp_path / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json"
    _write_text(
        summary_path,
        json.dumps(
            {
                "provider": "openai",
                "surface": "operator_cli",
                "artifact_root": artifact_root_relpath,
                "task_results": {
                    "astro_docs_site_v1": _write_case_artifacts(
                        tmp_path,
                        artifact_root_relpath=artifact_root_relpath,
                        task_id="astro_docs_site_v1",
                        task_pack=pack_obj,
                        changed_paths=("src/pages/docs/index.astro",),
                    )
                },
            },
            indent=2,
            sort_keys=True,
        ),
    )

    pack = replay_pack.build_real_work_replay_pack(repo_root=tmp_path, summary_path=summary_path)
    output_dir = tmp_path / "artifacts"
    payload = replay_pack.write_real_work_replay_pack_artifact(pack, output_dir=output_dir)

    assert (output_dir / "summary.json").exists()
    assert (output_dir / "summary.md").exists()
    relpath = payload["cases"][0]["recovered_file_map_relpath"]
    assert relpath == "cases/openai_operator_cli_astro_docs_site_v1_output_invalid/file_map.json"
    file_map = json.loads((output_dir / relpath).read_text(encoding="utf-8"))
    assert file_map == {"src/pages/docs/index.astro": "workspace::astro_docs_site_v1::src/pages/docs/index.astro\n"}
