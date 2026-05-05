"""Lab locks for the Codex App/CLI task-standard spine replay."""

from __future__ import annotations

from lab import codex_app_cli_task_standard_spine as replay


def test_replay_rows_keeps_hidden_verifier_out_of_spine_inputs() -> None:
    rows = [
        _row(
            "astro_hidden_fail",
            hidden=False,
            output_excerpt="Done: implemented docs search and tag pages.",
            visible_command="npm run build",
        ),
        _row(
            "astro_hidden_pass",
            hidden=True,
            output_excerpt="Done: implemented docs search and tag pages.",
            visible_command="grep -R search src && grep -R tag src",
        ),
    ]

    report = replay.replay_rows(
        rows,
        prompt_text="Build a docs site with search and tag pages.",
        standard_block="\n".join(
            (
                "Work standard: docs search and tag pages are strong.",
                "Likely misses: search data and tag links.",
                "Closure evidence: inspect search data and tag pages.",
            )
        ),
    )

    assert report["hidden_verifier_read"] is False
    assert all(trial["hidden_verifier_read"] is False for trial in report["trials"])
    assert report["caught_hidden_failures"] == 1
    assert report["overblock_risk_count"] == 0


def test_replay_rows_reports_overblock_risk_when_generic_evidence_is_all_it_has() -> None:
    rows = [
        _row(
            "astro_hidden_fail",
            hidden=False,
            output_excerpt="Done: implemented docs search and tag pages.",
            visible_command="npm run build",
        ),
        _row(
            "astro_hidden_pass",
            hidden=True,
            output_excerpt="Done: implemented docs search and tag pages.",
            visible_command="npm run build",
        ),
    ]

    report = replay.replay_rows(
        rows,
        prompt_text="Build a docs site with search and tag pages.",
        standard_block="\n".join(
            (
                "Work standard: docs search and tag pages are strong.",
                "Likely misses: search data and tag links.",
                "Closure evidence: inspect search data and tag pages.",
            )
        ),
    )

    assert report["verdict"] == "standard_spine_overblocks_without_real_model_standard"
    assert report["caught_hidden_failures"] == 1
    assert report["overblock_risk_count"] == 1


def _row(
    trial_id: str,
    *,
    hidden: bool,
    output_excerpt: str,
    visible_command: str,
) -> dict[str, object]:
    return {
        "trial_id": trial_id,
        "hidden_quality_pass": hidden,
        "output_excerpt": output_excerpt,
        "artifacts": {},
        "extra": {
            "final_evaluation": {
                "checks": [
                    {
                        "check_name": "visible_test",
                        "command": visible_command,
                        "exit_code": 0,
                    },
                    {
                        "check_name": "hidden_test",
                        "command": "scripts/test-hidden.mjs",
                        "exit_code": 1 if not hidden else 0,
                    },
                ]
            }
        },
    }
