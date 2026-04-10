"""Mine a small replay pack from real OpenAI output-quality failures."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from lab.cortex_output_quality import task_pack_by_name
from lab.output_quality_common import OutputQualityTaskPack


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_QUALITY_SUMMARY_PATH = (
    ROOT / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json"
)

ReplaySurface = Literal["operator_cli", "service_api", "unknown"]


@dataclass(frozen=True, slots=True)
class RealWorkReplayCase:
    case_id: str
    task_id: str
    host: str
    surface: ReplaySurface
    framework_family: str
    failure_class: str
    parse_error: str | None
    repairable: bool
    prompt_head: str
    allowed_write_paths: tuple[str, ...]
    changed_paths: tuple[str, ...]
    changed_file_map: dict[str, str] = field(default_factory=dict)
    source_artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    final_workspace_matches_attempt1_candidate: bool = False

    def __post_init__(self) -> None:
        for label, value in (
            ("case_id", self.case_id),
            ("task_id", self.task_id),
            ("host", self.host),
            ("surface", self.surface),
            ("framework_family", self.framework_family),
            ("failure_class", self.failure_class),
            ("prompt_head", self.prompt_head),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"RealWorkReplayCase.{label} must be non-empty after trimming.")
        if not self.allowed_write_paths:
            raise ValueError("RealWorkReplayCase.allowed_write_paths must be non-empty.")
        if not self.changed_paths:
            raise ValueError("RealWorkReplayCase.changed_paths must be non-empty.")
        if not self.changed_file_map:
            raise ValueError("RealWorkReplayCase.changed_file_map must be non-empty.")
        if set(self.changed_paths) != set(self.changed_file_map):
            raise ValueError(
                "RealWorkReplayCase.changed_paths must match changed_file_map keys."
            )
        if not self.source_artifact_refs:
            raise ValueError("RealWorkReplayCase.source_artifact_refs must be non-empty.")

    def as_payload(self, *, recovered_file_map_relpath: str | None = None) -> dict[str, Any]:
        payload = {
            "case_id": self.case_id,
            "task_id": self.task_id,
            "host": self.host,
            "surface": self.surface,
            "framework_family": self.framework_family,
            "failure_class": self.failure_class,
            "parse_error": self.parse_error,
            "repairable": self.repairable,
            "prompt_head": self.prompt_head,
            "allowed_write_paths": list(self.allowed_write_paths),
            "changed_paths": list(self.changed_paths),
            "source_artifact_refs": list(self.source_artifact_refs),
            "final_workspace_matches_attempt1_candidate": (
                self.final_workspace_matches_attempt1_candidate
            ),
        }
        if recovered_file_map_relpath is not None:
            payload["recovered_file_map_relpath"] = recovered_file_map_relpath
        return payload


@dataclass(frozen=True, slots=True)
class RealWorkReplayPack:
    host: str
    surface: ReplaySurface
    source_summary_relpath: str
    source_artifact_root: str
    cases: tuple[RealWorkReplayCase, ...]
    selected_case_ids: tuple[str, ...]
    selection_rule: str
    recommended_target_metric: str
    follow_on_runtime_budget: int
    follow_on_kill_condition: str
    follow_on_guardrail: str

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("RealWorkReplayPack.host must be non-empty after trimming.")
        if not self.source_summary_relpath.strip():
            raise ValueError(
                "RealWorkReplayPack.source_summary_relpath must be non-empty after trimming."
            )
        if not self.source_artifact_root.strip():
            raise ValueError(
                "RealWorkReplayPack.source_artifact_root must be non-empty after trimming."
            )
        if not self.cases:
            raise ValueError("RealWorkReplayPack.cases must be non-empty.")
        if not self.selected_case_ids:
            raise ValueError("RealWorkReplayPack.selected_case_ids must be non-empty.")
        case_ids = {case.case_id for case in self.cases}
        if any(case_id not in case_ids for case_id in self.selected_case_ids):
            raise ValueError(
                "RealWorkReplayPack.selected_case_ids must refer to extracted cases."
            )
        if self.follow_on_runtime_budget <= 0:
            raise ValueError(
                "RealWorkReplayPack.follow_on_runtime_budget must be positive."
            )

    @property
    def selected_cases(self) -> tuple[RealWorkReplayCase, ...]:
        selected = set(self.selected_case_ids)
        return tuple(case for case in self.cases if case.case_id in selected)

    @property
    def framework_coverage(self) -> tuple[str, ...]:
        return tuple(sorted({case.framework_family for case in self.selected_cases}))

    def as_payload(
        self,
        *,
        recovered_file_map_relpaths: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        recovered_file_map_relpaths = recovered_file_map_relpaths or {}
        return {
            "host": self.host,
            "surface": self.surface,
            "source_summary_relpath": self.source_summary_relpath,
            "source_artifact_root": self.source_artifact_root,
            "extracted_case_count": len(self.cases),
            "selected_case_count": len(self.selected_case_ids),
            "selected_case_ids": list(self.selected_case_ids),
            "framework_coverage": list(self.framework_coverage),
            "selection_rule": self.selection_rule,
            "recommended_target_metric": self.recommended_target_metric,
            "follow_on_runtime_budget": self.follow_on_runtime_budget,
            "follow_on_kill_condition": self.follow_on_kill_condition,
            "follow_on_guardrail": self.follow_on_guardrail,
            "cases": [
                case.as_payload(
                    recovered_file_map_relpath=recovered_file_map_relpaths.get(case.case_id)
                )
                for case in self.cases
            ],
        }


def build_real_work_replay_pack(
    *,
    repo_root: Path = ROOT,
    summary_path: Path | None = None,
    max_cases_per_framework: int = 1,
) -> RealWorkReplayPack:
    if max_cases_per_framework <= 0:
        raise ValueError("max_cases_per_framework must be positive.")
    summary_path = summary_path or (
        repo_root / OUTPUT_QUALITY_SUMMARY_PATH.relative_to(ROOT)
    )
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    host = str(summary.get("provider") or "unknown")
    surface = _surface_from_value(summary.get("surface"))
    source_artifact_root = str(summary.get("artifact_root") or "").strip()
    if not source_artifact_root:
        raise ValueError("output-quality summary is missing artifact_root.")
    artifact_root = repo_root / source_artifact_root
    cases: list[RealWorkReplayCase] = []
    task_results = summary.get("task_results")
    if not isinstance(task_results, dict):
        raise ValueError("output-quality summary is missing task_results.")
    for task_id in sorted(task_results):
        task_result = task_results[task_id]
        if not isinstance(task_result, dict):
            continue
        case = _extract_case(
            repo_root=repo_root,
            artifact_root=artifact_root,
            summary_path=summary_path,
            host=host,
            surface=surface,
            task_id=task_id,
            task_result=task_result,
        )
        if case is not None:
            cases.append(case)
    if not cases:
        raise ValueError("no replayable real-work cases were recovered from the summary.")
    selected_case_ids = _select_case_ids(
        cases=tuple(cases),
        max_cases_per_framework=max_cases_per_framework,
    )
    return RealWorkReplayPack(
        host=host,
        surface=surface,
        source_summary_relpath=_relpath(repo_root, summary_path),
        source_artifact_root=source_artifact_root,
        cases=tuple(cases),
        selected_case_ids=selected_case_ids,
        selection_rule=(
            "select one highest-change replayable case per framework family, "
            "breaking ties lexicographically by task_id"
        ),
        recommended_target_metric=(
            "repair_conversion_lift_or_first_attempt_failure_replay_coverage"
        ),
        follow_on_runtime_budget=2,
        follow_on_kill_condition=(
            "cut after 2 non-lift iterations or no clearer divergence classification"
        ),
        follow_on_guardrail=(
            "no regression on accepted verified-work packs and no shipping-truth widening"
        ),
    )


def write_real_work_replay_pack_artifact(
    pack: RealWorkReplayPack,
    *,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    case_root = output_dir / "cases"
    recovered_file_map_relpaths: dict[str, str] = {}
    for case in pack.cases:
        target_dir = case_root / case.case_id
        target_dir.mkdir(parents=True, exist_ok=True)
        relpath = f"cases/{case.case_id}/file_map.json"
        (output_dir / relpath).write_text(
            json.dumps(case.changed_file_map, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        recovered_file_map_relpaths[case.case_id] = relpath
    payload = pack.as_payload(recovered_file_map_relpaths=recovered_file_map_relpaths)
    (output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "summary.md").write_text(
        render_real_work_replay_pack_markdown(pack, recovered_file_map_relpaths),
        encoding="utf-8",
    )
    return payload


def render_real_work_replay_pack_markdown(
    pack: RealWorkReplayPack,
    recovered_file_map_relpaths: dict[str, str],
) -> str:
    lines = [
        f"# Real-Work Replay Pack: {pack.host}",
        "",
        f"- surface: `{pack.surface}`",
        f"- source_summary_relpath: `{pack.source_summary_relpath}`",
        f"- source_artifact_root: `{pack.source_artifact_root}`",
        f"- extracted_case_count: `{len(pack.cases)}`",
        f"- selected_case_count: `{len(pack.selected_case_ids)}`",
        f"- framework_coverage: `{', '.join(pack.framework_coverage)}`",
        f"- selection_rule: {pack.selection_rule}",
        f"- recommended_target_metric: `{pack.recommended_target_metric}`",
        f"- follow_on_runtime_budget: `{pack.follow_on_runtime_budget}`",
        f"- follow_on_kill_condition: {pack.follow_on_kill_condition}",
        f"- follow_on_guardrail: {pack.follow_on_guardrail}",
        "",
        "## Selected Cases",
        "",
    ]
    selected = set(pack.selected_case_ids)
    for case in pack.cases:
        prefix = "selected" if case.case_id in selected else "candidate"
        recovered_relpath = recovered_file_map_relpaths.get(case.case_id)
        lines.extend(
            [
                f"### {case.task_id} ({prefix})",
                "",
                f"- case_id: `{case.case_id}`",
                f"- framework_family: `{case.framework_family}`",
                f"- failure_class: `{case.failure_class}`",
                f"- prompt_head: {case.prompt_head}",
                f"- changed_paths: `{', '.join(case.changed_paths)}`",
                f"- final_workspace_matches_attempt1_candidate: `{case.final_workspace_matches_attempt1_candidate}`",
                f"- recovered_file_map_relpath: `{recovered_relpath or 'not-written'}`",
                f"- source_artifact_refs: `{', '.join(case.source_artifact_refs)}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _extract_case(
    *,
    repo_root: Path,
    artifact_root: Path,
    summary_path: Path,
    host: str,
    surface: ReplaySurface,
    task_id: str,
    task_result: dict[str, Any],
) -> RealWorkReplayCase | None:
    arms = task_result.get("arms")
    if not isinstance(arms, dict):
        return None
    cortex_arm = arms.get("cortex")
    if not isinstance(cortex_arm, dict):
        return None
    attempt1 = cortex_arm.get("attempt1")
    if not isinstance(attempt1, dict):
        return None
    evaluation = attempt1.get("evaluation")
    parse = attempt1.get("parse")
    if not isinstance(evaluation, dict) or not isinstance(parse, dict):
        return None
    if evaluation.get("failure_class") != "output_invalid":
        return None
    if not bool(cortex_arm.get("repairable")):
        return None
    task_pack = task_pack_by_name(task_id)
    seed_root = artifact_root / task_id / "seed" / "project_a"
    workspace_root = artifact_root / task_id / "cortex" / "workspace" / "project_a"
    if not seed_root.is_dir() or not workspace_root.is_dir():
        return None
    changed_file_map = _recover_changed_file_map(
        seed_root=seed_root,
        workspace_root=workspace_root,
        task_pack=task_pack,
    )
    if not changed_file_map:
        return None
    prompt_head = _prompt_head(str(attempt1.get("input_text") or task_pack.prompt_text))
    attempt2_result = artifact_root / task_id / "cortex" / "attempt2" / "result.json"
    case_id = f"{host}_{surface}_{task_id}_output_invalid"
    refs = [
        _relpath(repo_root, summary_path),
        _relpath(repo_root, artifact_root / task_id / "cortex" / "attempt1" / "result.json"),
        _relpath(repo_root, seed_root),
        _relpath(repo_root, workspace_root),
    ]
    if attempt2_result.exists():
        refs.append(_relpath(repo_root, attempt2_result))
    return RealWorkReplayCase(
        case_id=case_id,
        task_id=task_id,
        host=host,
        surface=surface,
        framework_family=_infer_framework_family(task_pack),
        failure_class="output_invalid",
        parse_error=str(parse.get("parse_error") or "").strip() or None,
        repairable=True,
        prompt_head=prompt_head,
        allowed_write_paths=tuple(task_pack.allowed_write_paths),
        changed_paths=tuple(sorted(changed_file_map)),
        changed_file_map=changed_file_map,
        source_artifact_refs=tuple(refs),
        final_workspace_matches_attempt1_candidate=_attempt2_is_noop(attempt2_result),
    )


def _recover_changed_file_map(
    *,
    seed_root: Path,
    workspace_root: Path,
    task_pack: OutputQualityTaskPack,
) -> dict[str, str]:
    changed_file_map: dict[str, str] = {}
    for relative_path in task_pack.allowed_write_paths:
        seed_path = seed_root / relative_path
        workspace_path = workspace_root / relative_path
        if not seed_path.is_file() or not workspace_path.is_file():
            continue
        seed_text = seed_path.read_text(encoding="utf-8")
        workspace_text = workspace_path.read_text(encoding="utf-8")
        if seed_text != workspace_text:
            changed_file_map[relative_path] = workspace_text
    return changed_file_map


def _attempt2_is_noop(attempt2_result_path: Path) -> bool:
    if not attempt2_result_path.exists():
        return False
    payload = json.loads(attempt2_result_path.read_text(encoding="utf-8"))
    parse = payload.get("parse")
    changed_files = payload.get("changed_files")
    if not isinstance(parse, dict) or not isinstance(changed_files, dict):
        return False
    return (
        parse.get("parse_error") == "operator completed without workspace edits"
        and not changed_files
    )


def _select_case_ids(
    *,
    cases: tuple[RealWorkReplayCase, ...],
    max_cases_per_framework: int,
) -> tuple[str, ...]:
    grouped: dict[str, list[RealWorkReplayCase]] = {}
    for case in cases:
        grouped.setdefault(case.framework_family, []).append(case)
    selected: list[RealWorkReplayCase] = []
    for framework_family in sorted(grouped):
        ranked = sorted(
            grouped[framework_family],
            key=lambda case: (-len(case.changed_paths), case.task_id),
        )
        selected.extend(ranked[:max_cases_per_framework])
    selected.sort(key=lambda case: (case.framework_family, case.task_id))
    return tuple(case.case_id for case in selected)


def _prompt_head(prompt_text: str) -> str:
    for line in prompt_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return "(empty prompt)"


def _infer_framework_family(task_pack: OutputQualityTaskPack) -> str:
    if any(path.endswith(".astro") for path in task_pack.allowed_write_paths):
        return "astro"
    if any(path.endswith(".tsx") for path in task_pack.allowed_write_paths):
        return "react"
    return "unknown"


def _surface_from_value(value: Any) -> ReplaySurface:
    if value == "operator_cli":
        return "operator_cli"
    if value == "service_api":
        return "service_api"
    return "unknown"


def _relpath(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/real_work_replay_pack.py",
        description="Recover a tiny replay pack from real OpenAI output-quality artifacts.",
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--summary-path", default=None)
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
    )
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    summary_path = Path(args.summary_path).resolve() if args.summary_path else None
    pack = build_real_work_replay_pack(repo_root=repo_root, summary_path=summary_path)
    if args.format == "markdown":
        print(render_real_work_replay_pack_markdown(pack, recovered_file_map_relpaths={}))
    else:
        print(json.dumps(pack.as_payload(), indent=2, sort_keys=True))
    return 0


__all__ = [
    "RealWorkReplayCase",
    "RealWorkReplayPack",
    "build_real_work_replay_pack",
    "main",
    "render_real_work_replay_pack_markdown",
    "write_real_work_replay_pack_artifact",
]
