"""Focused tests for the E12 comparative output-quality runner."""

from __future__ import annotations

import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import cortex_output_quality as output_quality
from output_quality_ablation import OutputQualityAblationConfig
from output_quality_grader import PairwiseJudgment


def test_supported_task_ids_cover_all_five_output_quality_tasks() -> None:
    assert output_quality.supported_task_ids() == (
        "astro_docs_site_v1",
        "astro_marketing_forms_v1",
        "react_dashboard_v1",
        "react_existing_feature_extension_v1",
        "frontend_bugfix_cleanup_v1",
    )


def test_task_prompts_use_human_language_without_hidden_rubric_leaks() -> None:
    banned_terms = (
        "waterfall",
        "back/forward",
        "server/client",
        "gratutious",
        "client-side fetch",
    )

    for task_id in output_quality.supported_task_ids():
        prompt = output_quality.task_pack_by_name(task_id).prompt_text
        normalized = prompt.lower()
        assert "maintainable" in normalized
        assert any(
            phrase in normalized
            for phrase in (
                "best practices",
                "keep the structure stable",
            )
        )
        assert "additional verifier-only checks may run" in prompt
        for banned_term in banned_terms:
            assert banned_term not in normalized


def test_build_pairwise_results_maps_blind_labels_back_to_arms(monkeypatch) -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")
    monkeypatch.setattr(output_quality, "stable_pair_order", lambda _seed: ("b", "a"))
    monkeypatch.setattr(
        output_quality,
        "judge_pairwise_merge_worthiness",
        lambda **_kwargs: PairwiseJudgment(
            winner="a",
            confidence="high",
            reason_tags=("maintainability",),
            objective_override=False,
        ),
    )

    pairwise = output_quality._build_pairwise_results(
        task_pack=task_pack,
        arms=("raw", "tooling_only", "cortex"),
        arm_results={
            "raw": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
            "tooling_only": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
            "cortex": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
        },
    )

    assert pairwise[0]["left_arm"] == "cortex"
    assert pairwise[0]["right_arm"] == "raw"
    assert pairwise[0]["winner_arm"] == "raw"
    assert pairwise[1]["winner_arm"] == "tooling_only"


def test_build_suite_summary_counts_pairwise_wins() -> None:
    summary = output_quality._build_suite_summary(
        run_root=Path("/tmp/output-quality"),
        task_ids=("astro_docs_site_v1",),
        arms=("raw", "tooling_only", "cortex"),
        model="gpt-5.4",
        task_results={},
        aggregate_objective={"raw": 0, "tooling_only": 1, "cortex": 1},
        aggregate_hidden={"raw": 0, "tooling_only": 1, "cortex": 1},
        pairwise_results=[
            {
                "task_id": "astro_docs_site_v1",
                "left_arm": "cortex",
                "right_arm": "raw",
                "winner_arm": "cortex",
                "confidence": "high",
                "reason_tags": ["quality"],
                "objective_override": False,
            },
            {
                "task_id": "astro_docs_site_v1",
                "left_arm": "cortex",
                "right_arm": "tooling_only",
                "winner_arm": None,
                "confidence": "low",
                "reason_tags": ["tie"],
                "objective_override": False,
            },
        ],
        env_blocked=False,
        ablation_config=OutputQualityAblationConfig(verification_binding="off"),
    )

    assert summary["pairwise_summary"]["cortex_vs_raw"]["wins"] == 1
    assert summary["pairwise_summary"]["cortex_vs_raw"]["win_rate"] == 1.0
    assert summary["pairwise_summary"]["cortex_vs_tooling_only"]["ties"] == 1
    assert summary["ablation_config"]["verification_binding"] == "off"


def test_run_arm_skips_repair_when_verification_binding_is_off(
    tmp_path: Path,
    monkeypatch,
) -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")
    execute_calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        output_quality,
        "_execute_openai_turn",
        lambda **kwargs: execute_calls.append(kwargs) or {
            "response_id": "resp-1",
            "output_text": "=== FILE: src/App.tsx ===\nexport default function App() { return null }\n=== END FILE ===\n",
            "raw_events": [],
        },
    )
    monkeypatch.setattr(
        output_quality,
        "prepare_seeded_workspace",
        lambda **_kwargs: tmp_path,
    )
    monkeypatch.setattr(
        output_quality,
        "_evaluate_turn_output",
        lambda **_kwargs: {
            "evaluation": {
                "status": "failed",
                "failure_class": "hidden_test_failed",
                "objective_pass": True,
                "hidden_quality_pass": False,
                "failing_checks": ["hidden_test"],
                "first_failure_excerpt": "missing hidden integration",
                "checks": [],
            },
            "changed_files": {},
            "repairable": True,
            "parse": {
                "parse_error": None,
                "blocked_reason": None,
                "blocked_message": None,
                "parsed_paths": [],
            },
        },
    )
    monkeypatch.setattr(output_quality, "write_json", lambda *_args, **_kwargs: None)

    result = output_quality._run_arm(
        task_pack=task_pack,
        arm="cortex",
        model="gpt-5.4",
        task_root=tmp_path,
        seed_workspace=tmp_path,
        shared_install_result={"exit_code": 0, "stdout": "", "stderr": ""},
        ablation_config=OutputQualityAblationConfig(
            verification_binding="off",
            repair_turn="on",
        ),
    )

    assert result["attempt_count"] == 1
    assert len(execute_calls) == 1
