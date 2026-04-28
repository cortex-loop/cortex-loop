from __future__ import annotations

from pathlib import Path

from lab import repo_hygiene_constraint_fidelity as harness


def test_initial_prompt_has_no_marker() -> None:
    prompt = harness.build_initial_prompt()

    assert not harness.prompt_has_cortex_marker(prompt)
    assert "CORTEX" not in prompt


def test_summary_accepts_repo_hygiene_promotion_with_distinct_violation_classes() -> None:
    raw_runs = [
        _run(
            "raw_host",
            "uncertified",
            0.5,
            failed_ids=("verify-observed", "status-doc-generated", "checkpoint-commit", "handoff-fields"),
        )
        for _ in range(10)
    ]
    loop_runs = [
        _run(
            "kernel_loop_cortex",
            "certified" if index < 8 else "uncertified",
            1.0 if index < 8 else 0.6,
            failed_ids=("verify-observed", "status-doc-generated", "checkpoint-commit", "handoff-fields"),
            converted_classes=["verification_or_closure", "generated_status", "checkpoint_commit", "handoff"],
        )
        for index in range(10)
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="all",
        repeat_count=10,
        runs=raw_runs + loop_runs,
        prediction=harness.build_prediction(provider="claude", repeat_count=10, stage="all"),
    )

    assert summary["experiment_status"] == "repo_hygiene_loop_promotion_passed"
    assert summary["raw_uncertified_count"] == 10
    assert summary["loop_certified_count"] == 8
    assert len(summary["loop_converted_violation_classes"]) >= 3


def test_summary_marks_mechanism_underinformative_when_classes_are_too_narrow() -> None:
    raw_runs = [_run("raw_host", "uncertified", 0.5, failed_ids=("verify-observed",)) for _ in range(10)]
    loop_runs = [
        _run(
            "kernel_loop_cortex",
            "certified" if index < 8 else "uncertified",
            1.0 if index < 8 else 0.6,
            failed_ids=("verify-observed",),
            converted_classes=["verification_or_closure"],
        )
        for index in range(10)
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="all",
        repeat_count=10,
        runs=raw_runs + loop_runs,
        prediction=harness.build_prediction(provider="claude", repeat_count=10, stage="all"),
    )

    assert summary["experiment_status"] == "gate_passed_mechanism_underinformative"


def test_summary_marks_score_lift_under_threshold_when_certification_counts_pass() -> None:
    raw_runs = [
        _run(
            "raw_host",
            "uncertified",
            0.75,
            failed_ids=("rule-evidence", "checkpoint-commit", "handoff-fields"),
        )
        for _ in range(10)
    ]
    loop_runs = [
        _run(
            "kernel_loop_cortex",
            "certified",
            1.0,
            failed_ids=("rule-evidence", "checkpoint-commit", "handoff-fields"),
            converted_classes=["rule_evidence", "checkpoint_commit", "handoff"],
        )
        for _ in range(10)
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="all",
        repeat_count=10,
        runs=raw_runs + loop_runs,
        prediction=harness.build_prediction(provider="claude", repeat_count=10, stage="all"),
    )

    assert summary["experiment_status"] == "repo_hygiene_certification_passed_score_lift_under_threshold"
    assert summary["loop_score_lift"] == 0.25


def test_kernel_loop_repeats_repair_until_certified(tmp_path: Path, monkeypatch) -> None:
    prompts: list[str] = []

    monkeypatch.setattr(harness, "load_invariant_config", lambda _path: {"schema_version": 1, "fixture_id": "x"})
    monkeypatch.setattr(harness, "prepare_workspace", lambda **_kwargs: tmp_path)
    monkeypatch.setattr(harness, "choose_model", lambda *_args, **_kwargs: "claude-test")
    monkeypatch.setattr(harness, "resolve_auth_mode", lambda *_args, **_kwargs: "claude_code")
    monkeypatch.setattr(harness, "extract_session_id", lambda *_args, **_kwargs: "session-1")
    monkeypatch.setattr(harness, "write_json", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(harness, "write_text", lambda *_args, **_kwargs: None)

    def fake_run(prompt: str, **_kwargs):
        prompts.append(prompt)
        return {"stdout": "{}", "stderr": "", "exit_code": 0, "command": ["claude"], "started_at": "t1", "ended_at": "t2"}

    def fake_materialize(*, attempt_index: int, prompt: str, **_kwargs):
        status = "certified" if attempt_index == 3 else "uncertified"
        failed_facts = [] if status == "certified" else [f"`issue-{attempt_index}` still needs repair."]
        return {
            "attempt_index": attempt_index,
            "exit_code": 0,
            "failure_class": None,
            "prompt": prompt,
            "prompt_marker_absent": not harness.prompt_has_cortex_marker(prompt),
            "records": [{"type": "init", "session_id": "session-1"}],
            "result_text": "Verification: passed" if status == "certified" else "not done",
            "modified_files": ["internal/truth/status.json"],
            "workspace_change_evidence": {
                "dirty_files": [],
                "committed_files_since_baseline": ["internal/truth/status.json"],
                "modified_files": ["internal/truth/status.json"],
                "baseline_ref": "cortex-fixture-baseline",
                "baseline_sha": "abc123",
            },
            "tool_evidence": {"read_paths": [], "commands": ["npm run verify"]},
            "runtime": {"duration_ms": 100, "num_turns": 1},
            "certification": {
                "status": status,
                "mechanical_score": 1.0 if status == "certified" else 0.5,
                "required_pass_count": 2 if status == "certified" else 1,
                "required_count": 2,
                "failed_repair_facts": failed_facts,
                "env_failure_class": None,
                "results": [
                    {
                        "id": "verify-observed",
                        "status": "passed" if status == "certified" else "failed",
                        "required": True,
                        "message": "verify missing",
                        "repair_fact": failed_facts[0] if failed_facts else None,
                    }
                ],
            },
        }

    monkeypatch.setattr(harness, "_run_claude_turn", fake_run)
    monkeypatch.setattr(harness, "_materialize_attempt", fake_materialize)

    payload = harness.run_variant(provider="claude", variant="kernel_loop_cortex", repeat_index=1)

    assert payload["repair_policy"] == "loop"
    assert payload["max_repair_turns"] == 3
    assert payload["certification_status"] == "certified"
    assert len(payload["repair_attempts"]) == 2
    assert len(prompts) == 3
    assert "`issue-1` still needs repair." in prompts[1]
    assert "`issue-2` still needs repair." in prompts[2]
    assert all(harness.first_forbidden_repair_term(prompt) is None for prompt in prompts[1:])


def test_runtime_scaling_finding_trips_above_four_x_website_baseline() -> None:
    finding = harness._runtime_scaling_finding(
        {
            "kernel_loop_cortex": {
                "mean_duration_ms": harness.RUNTIME_SCALING_THRESHOLD_MS + 1,
            }
        }
    )

    assert finding["threshold_exceeded"] is True
    assert finding["finding"] == "runtime_scaling_exceeds_4x_website_baseline"


def test_checkpoint_subject_mismatch_is_model_attempted_but_failed() -> None:
    payload = {
        "failure_class": None,
        "certification": {
            "status": "uncertified",
            "results": [
                {
                    "id": "checkpoint-commit",
                    "status": "failed",
                    "evidence": {"subjects": ["chore(fixture): checkpoint verified ready state"]},
                }
            ],
        },
    }

    classification = harness._classify_uncertified_run(
        first_payload=payload,
        repair_attempts=[payload],
        final_payload=payload,
    )

    assert classification == "model_attempted_but_failed"


def _run(
    variant: str,
    status: str,
    score: float,
    *,
    failed_ids: tuple[str, ...],
    converted_classes: list[str] | None = None,
) -> dict[str, object]:
    results = [
        {
            "id": invariant_id,
            "status": "failed",
            "required": True,
            "message": f"{invariant_id} failed",
            "repair_fact": f"{invariant_id} repair fact",
        }
        for invariant_id in failed_ids
    ]
    return {
        "variant": variant,
        "certification_status": status,
        "mechanical_score": score,
        "fixture_fingerprint": "fixture-sha",
        "fixture_baseline_sha": "baseline-sha",
        "first_prompt_sha": "prompt-sha",
        "prompt_marker_absent": True,
        "converted_violation_classes": converted_classes or [],
        "runtime": {"total_duration_ms": 1000},
        "final": {
            "certification": {
                "status": status,
                "results": [] if status == "certified" else results,
            }
        },
    }
