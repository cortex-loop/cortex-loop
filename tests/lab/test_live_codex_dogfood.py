"""Focused tests for the Codex App E23 dogfood wrapper."""

from __future__ import annotations

from pathlib import Path

from lab import live_codex_dogfood


def test_build_codex_dogfood_summary_is_ready_for_e23_session() -> None:
    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=_ready_preflight(),
        app_server_summary=_positive_app_server_summary(),
        comparison=_ready_comparison(),
    )

    assert summary["next_action"] == "ready_for_e23_session"
    assert summary["template_watchlist"]["watchlist_status"] == "positive"
    assert summary["compare_context"]["current_openai_canonical_status"] == "positive"
    assert (
        summary["manual_session_contract"]["prompt_profile_paths"]["session_start"]
        == "tests/lab/fixtures/live_validation/prompts/e23_codex_app_session_start.md"
    )


def test_build_codex_dogfood_summary_blocks_on_preflight_failures() -> None:
    preflight = _ready_preflight()
    preflight["auth_surfaces"]["codex_cli_session"]["logged_in"] = False
    preflight["operator_probe"]["openai"]["failure_class"] = "auth_missing"

    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=preflight,
        app_server_summary=_positive_app_server_summary(),
        comparison=_ready_comparison(),
    )

    assert summary["next_action"] == "blocked_by_preflight"
    assert summary["readiness"]["blocking_failures"] == [
        "codex_not_logged_in",
        "openai_operator_probe:auth_missing",
    ]


def test_build_codex_dogfood_summary_blocks_on_watchlist_failures() -> None:
    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=_ready_preflight(),
        app_server_summary={
            "runs": [
                {
                    "scenario_id": "pass_minimal",
                    "success": False,
                    "failure_class": "approval_requested",
                }
            ]
        },
        comparison=_comparison_with_watchlist_failure(),
    )

    assert summary["next_action"] == "blocked_by_watchlist"
    assert summary["template_watchlist"]["failure_classes"] == ["approval_requested"]


def test_build_codex_dogfood_summary_surfaces_watchlist_drift() -> None:
    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=_ready_preflight(),
        app_server_summary=_positive_app_server_summary(),
        comparison=_comparison_with_watchlist_drift(),
    )

    assert summary["next_action"] == "watchlist_drift_detected"
    assert summary["compare_context"]["accepted_watchlist_drift_detected"] is True


def test_build_codex_dogfood_summary_marks_missing_canonical_context() -> None:
    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=_ready_preflight(),
        app_server_summary=_positive_app_server_summary(),
        comparison=_comparison_without_canonical_context(),
    )

    assert summary["next_action"] == "canonical_context_missing"
    assert summary["compare_context"]["available"] is False


def test_main_uses_preflight_app_server_and_compare_only(monkeypatch, capsys) -> None:
    call_order: list[tuple[str, str]] = []

    def fake_load_local_env_file() -> None:
        call_order.append(("load_env", ""))

    def fake_ensure_live_validation_dirs() -> None:
        call_order.append(("ensure_dirs", ""))

    def fake_build_preflight_report(*, lane: str, skip_updates: bool) -> dict[str, object]:
        call_order.append(("preflight", f"{lane}:{skip_updates}"))
        return _ready_preflight()

    def fake_run_openai_app_server_validation(*, scenario: str) -> dict[str, object]:
        call_order.append(("app_server", scenario))
        return _positive_app_server_summary()

    def fake_build_comparison_artifacts(preflight: dict[str, object]) -> dict[str, object]:
        call_order.append(
            ("compare", str(preflight["auth_surfaces"]["codex_cli_session"]["logged_in"]))
        )
        return _ready_comparison()

    def fake_write_json(path: Path, payload: dict[str, object]) -> None:
        call_order.append(("write_json", path.name))

    monkeypatch.setattr(live_codex_dogfood, "load_local_env_file", fake_load_local_env_file)
    monkeypatch.setattr(
        live_codex_dogfood,
        "ensure_live_validation_dirs",
        fake_ensure_live_validation_dirs,
    )
    monkeypatch.setattr(
        live_codex_dogfood.live_preflight,
        "build_preflight_report",
        fake_build_preflight_report,
    )
    monkeypatch.setattr(
        live_codex_dogfood,
        "run_openai_app_server_validation",
        fake_run_openai_app_server_validation,
    )
    monkeypatch.setattr(
        live_codex_dogfood.live_compare,
        "build_comparison_artifacts",
        fake_build_comparison_artifacts,
    )
    monkeypatch.setattr(live_codex_dogfood, "write_json", fake_write_json)

    assert live_codex_dogfood.main([]) == 0

    assert call_order == [
        ("load_env", ""),
        ("ensure_dirs", ""),
        ("preflight", "all:True"),
        ("write_json", "preflight_report.json"),
        ("app_server", "all"),
        ("compare", "True"),
        ("write_json", "codex_dogfood_summary.json"),
    ]
    assert "ready_for_e23_session" in capsys.readouterr().out


def test_render_codex_dogfood_summary_includes_managed_session_contract() -> None:
    summary = live_codex_dogfood.build_codex_dogfood_summary(
        preflight=_ready_preflight(),
        app_server_summary=_positive_app_server_summary(),
        comparison=_ready_comparison(),
    )

    rendered = live_codex_dogfood.render_codex_dogfood_summary(summary)

    assert "python3 internal/workflow/repo_workflow.py sync-main" in rendered
    assert "start-session --agent codex --slug e23-kernel-extract" in rendered
    assert 'close-session --message "kernel: e23 kernel extract end-state summary"' in rendered
    assert "codex/<YYYYMMDD-HHMMSS>-<slug>" in rendered


def test_prompt_contract_requires_dogfood_signal_and_preserves_normal_handoff() -> None:
    session_start = (
        live_codex_dogfood.PROMPTS_ROOT / "e23_codex_app_session_start.md"
    ).read_text(encoding="utf-8")
    closeout = (
        live_codex_dogfood.PROMPTS_ROOT / "e23_codex_app_closeout.md"
    ).read_text(encoding="utf-8")

    for key in (
        "DOGFOOD_SIGNAL",
        "continuity_helped: yes|no",
        "blocker_surfaced: yes|no",
        "uncertainty_or_brake_used: yes|no",
        "truthful_closure: yes|no",
        "cortex_changed_next_action: yes|no",
        "note: <one sentence>",
    ):
        assert key in session_start
        assert key in closeout

    assert "Preserve the repo's normal final handoff contract." in session_start
    assert "Do not replace the normal handoff with lab text." in closeout


def _ready_preflight() -> dict[str, object]:
    return {
        "install_channels": {
            "codex": {
                "installed": True,
                "channel": "npm_global",
            }
        },
        "auth_surfaces": {
            "codex_cli_session": {
                "logged_in": True,
                "status_text": "Logged in using ChatGPT",
            },
            "automation": {
                "openai": {
                    "auth_mode": "api_key",
                    "status": "ready",
                    "spend_approved": True,
                    "api_key_present": True,
                }
            },
        },
        "operator_probe": {
            "openai": {
                "auth_mode": "codex_cli",
                "preferred_model": "gpt-5.3-codex",
                "model": "gpt-5.3-codex",
                "failure_class": None,
            }
        },
    }


def _positive_app_server_summary() -> dict[str, object]:
    return {
        "runs": [
            {
                "scenario_id": "pass_minimal",
                "success": True,
                "failure_class": None,
            },
            {
                "scenario_id": "truth_gap",
                "success": True,
                "truth_gap_kind": "truthful_incomplete",
                "failure_class": None,
            },
            {
                "scenario_id": "restart_continuity",
                "success": True,
                "failure_class": None,
            },
        ]
    }


def _ready_comparison() -> dict[str, object]:
    return {
        "verdict": "canonical runtime truth is re-earned for current scope",
        "service_lane_delta": "direct_api canonical truth is re-earned for current scope on `openai`.",
        "providers": {
            "openai": {
                "operator_lifecycle": {
                    "watchlist_status": "positive",
                    "warning_classes": [],
                    "failure_classes": [],
                    "accepted_watchlist_drift_detected": False,
                },
                "automation_service": {
                    "canonical_anchor": {
                        "cycle_count": 2,
                        "latest_cycle_status": "positive",
                        "repeat_stable_success": True,
                    }
                },
            }
        },
    }


def _comparison_with_watchlist_failure() -> dict[str, object]:
    payload = _ready_comparison()
    payload["providers"]["openai"]["operator_lifecycle"] = {
        "watchlist_status": "unresolved",
        "warning_classes": [],
        "failure_classes": ["approval_requested"],
        "accepted_watchlist_drift_detected": False,
    }
    return payload


def _comparison_with_watchlist_drift() -> dict[str, object]:
    payload = _ready_comparison()
    payload["providers"]["openai"]["operator_lifecycle"] = {
        "watchlist_status": "unresolved",
        "warning_classes": [],
        "failure_classes": [],
        "accepted_watchlist_drift_detected": True,
    }
    return payload


def _comparison_without_canonical_context() -> dict[str, object]:
    payload = _ready_comparison()
    payload["providers"]["openai"]["automation_service"] = {
        "canonical_anchor": {
            "cycle_count": 0,
            "latest_cycle_status": "absent",
            "repeat_stable_success": False,
        }
    }
    return payload
