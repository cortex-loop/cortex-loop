from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from lab.invariant_runner import InvariantEvidence, evaluate_invariants, load_invariant_config, run_configured_checks
from lab import website_constraint_fidelity as harness


def test_initial_prompt_has_no_marker_and_is_reused_for_variants() -> None:
    prompt = harness.build_initial_prompt()

    assert not harness.prompt_has_cortex_marker(prompt)
    assert harness._stable_text_digest(prompt) == harness._stable_text_digest(prompt)


def test_summary_voids_non_discriminative_fixture() -> None:
    runs = [
        {"variant": "raw_host", "certification_status": "certified", "mechanical_score": 1.0},
        {"variant": "raw_host", "certification_status": "certified", "mechanical_score": 1.0},
        {"variant": "raw_host", "certification_status": "uncertified", "mechanical_score": 0.6},
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="reproduce",
        repeat_count=3,
        runs=runs,
    )

    assert summary["experiment_status"] == "void_fixture_not_discriminative"


def test_summary_accepts_kernel_conversion_smoke() -> None:
    runs = [
        {"variant": "raw_host", "certification_status": "uncertified", "mechanical_score": 0.4},
        {"variant": "raw_host", "certification_status": "uncertified", "mechanical_score": 0.5},
        {"variant": "raw_host", "certification_status": "uncertified", "mechanical_score": 0.6},
        {"variant": "kernel_only_cortex", "certification_status": "certified", "mechanical_score": 1.0},
        {"variant": "kernel_only_cortex", "certification_status": "certified", "mechanical_score": 1.0},
        {"variant": "kernel_only_cortex", "certification_status": "uncertified", "mechanical_score": 0.7},
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="all",
        repeat_count=3,
        runs=runs,
    )

    assert summary["experiment_status"] == "kernel_lift_smoke_passed"
    assert summary["kernel_certified_count"] == 2


def test_kernel_variant_runs_one_factual_repair_turn(tmp_path: Path, monkeypatch) -> None:
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
        status = "uncertified" if attempt_index == 1 else "certified"
        return {
            "attempt_index": attempt_index,
            "exit_code": 0,
            "failure_class": None,
            "prompt": prompt,
            "prompt_marker_absent": not harness.prompt_has_cortex_marker(prompt),
            "records": [{}],
            "result_text": "not done" if attempt_index == 1 else "Verification: passed\nBlockers: none",
            "modified_files": ["src/pages/resources.astro"],
            "tool_evidence": {"read_paths": [], "commands": []},
            "certification": {
                "status": status,
                "mechanical_score": 0.5 if attempt_index == 1 else 1.0,
                "required_pass_count": 1 if attempt_index == 1 else 2,
                "required_count": 2,
                "failed_repair_facts": ["`src/pages/resources.astro` is missing the required filter. Add it."],
                "env_failure_class": None,
                "results": [
                    {
                        "id": "filter",
                        "status": "failed" if attempt_index == 1 else "passed",
                        "required": True,
                        "message": "filter missing",
                        "repair_fact": "`src/pages/resources.astro` is missing the required filter. Add it.",
                    }
                ],
            },
        }

    monkeypatch.setattr(harness, "_run_claude_turn", fake_run)
    monkeypatch.setattr(harness, "_materialize_attempt", fake_materialize)

    payload = harness.run_variant(provider="claude", variant="kernel_only_cortex", repeat_index=1)

    assert payload["repair_turn_attempted"] is True
    assert payload["repair_policy"] == "single"
    assert payload["max_repair_turns"] == 1
    assert len(payload["repair_attempts"]) == 1
    assert payload["certification_status"] == "certified"
    assert prompts[0] == harness.build_initial_prompt()
    assert prompts[1].startswith("The previous result is not certifiable yet.")
    assert harness.first_forbidden_repair_term(prompts[1]) is None


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
        failed_facts = [] if status == "certified" else [f"`remaining-{attempt_index}` still needs repair."]
        return {
            "attempt_index": attempt_index,
            "exit_code": 0,
            "failure_class": "turn_budget_cutoff" if attempt_index == 2 else None,
            "prompt": prompt,
            "prompt_marker_absent": not harness.prompt_has_cortex_marker(prompt),
            "records": [{"type": "init", "session_id": "session-1"}],
            "result_text": "Verification: passed" if status == "certified" else "not done",
            "modified_files": ["src/pages/resources.astro"],
            "tool_evidence": {"read_paths": [], "commands": []},
            "certification": {
                "status": status,
                "mechanical_score": 1.0 if status == "certified" else 0.5,
                "required_pass_count": 2 if status == "certified" else 1,
                "required_count": 2,
                "failed_repair_facts": failed_facts,
                "env_failure_class": None,
                "results": [],
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
    assert "`remaining-1` still needs repair." in prompts[1]
    assert "`remaining-2` still needs repair." in prompts[2]
    assert payload["converted_failure_classes"] == ["turn_budget_cutoff"]
    assert all(harness.first_forbidden_repair_term(prompt) is None for prompt in prompts[1:])


def test_kernel_loop_stops_after_max_repair_turns(tmp_path: Path, monkeypatch) -> None:
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
        return {
            "attempt_index": attempt_index,
            "exit_code": 0,
            "failure_class": None,
            "prompt": prompt,
            "prompt_marker_absent": not harness.prompt_has_cortex_marker(prompt),
            "records": [{"type": "init", "session_id": "session-1"}],
            "result_text": "not done",
            "modified_files": ["src/pages/resources.astro"],
            "tool_evidence": {"read_paths": [], "commands": []},
            "certification": {
                "status": "uncertified",
                "mechanical_score": 0.5,
                "required_pass_count": 1,
                "required_count": 2,
                "failed_repair_facts": [f"`remaining-{attempt_index}` still needs repair."],
                "env_failure_class": None,
                "results": [],
            },
        }

    monkeypatch.setattr(harness, "_run_claude_turn", fake_run)
    monkeypatch.setattr(harness, "_materialize_attempt", fake_materialize)

    payload = harness.run_variant(provider="claude", variant="kernel_loop_cortex", repeat_index=1)

    assert payload["certification_status"] == "uncertified"
    assert len(payload["repair_attempts"]) == 3
    assert len(prompts) == 4


def test_historical_baseline_rejects_fixture_fingerprint_mismatch(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(
        '{"fixture_fingerprint": "old", "kernel_certified_count": 8, "repeat_count": 10}',
        encoding="utf-8",
    )

    baseline = harness._historical_single_repair_baseline(
        provider="claude",
        fixture_fingerprint="new",
        first_prompt_sha=harness.BASELINE_PROMPT_SHA,
        baseline_path=baseline_path,
    )

    assert baseline["usable"] is False
    assert baseline["reason"] == "fixture_fingerprint_mismatch"


def test_kernel_loop_summary_records_promotion_fields() -> None:
    runs = [
        {
            "variant": "kernel_loop_cortex",
            "certification_status": "certified" if index < 9 else "uncertified",
            "mechanical_score": 1.0 if index < 9 else 0.8,
            "fixture_fingerprint": "fixture-sha",
            "first_prompt_sha": harness.BASELINE_PROMPT_SHA,
            "prompt_marker_absent": True,
        }
        for index in range(10)
    ]

    summary = harness.build_summary(
        provider="claude",
        stage="kernel-loop",
        repeat_count=10,
        runs=runs,
    )

    assert summary["experiment_status"] == "kernel_loop_promotion_passed"
    assert summary["kernel_loop_certified_count"] == 9
    assert summary["fixture_fingerprint"] == "fixture-sha"
    assert summary["prompt_marker_absent_all"] is True


def test_website_fixture_valid_solution_passes_hidden_checks(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(harness.FIXTURE_ROOT, project_root)
    _apply_valid_fixture_solution(project_root)

    verify = subprocess.run(
        ["npm", "run", "verify"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    assert verify.returncode == 0, verify.stderr or verify.stdout

    config = load_invariant_config(project_root / "cortex-invariants.json")
    check_results = run_configured_checks(config, project_root=project_root)
    evaluation = evaluate_invariants(
        config,
        InvariantEvidence(
            modified_files=(
                "src/components/SiteHeader.astro",
                "src/components/islands/ResourceFilter.tsx",
                "src/content/resources.ts",
                "src/pages/resources.astro",
            ),
            read_paths=("FIXTURE_RULES.md", "CLAUDE.md"),
            commands=("npm run verify",),
            result_text="Verification: npm run verify passed.\nBlockers: none.",
            check_results=check_results,
        ),
        project_root=project_root,
    )

    assert evaluation.status == "certified"


def test_website_fixture_hidden_check_rejects_eager_hydration(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    shutil.copytree(harness.FIXTURE_ROOT, project_root)
    _apply_valid_fixture_solution(project_root)
    resources_page = project_root / "src/pages/resources.astro"
    resources_page.write_text(
        resources_page.read_text(encoding="utf-8").replace("client:idle", "client:load"),
        encoding="utf-8",
    )

    hidden = subprocess.run(
        ["npm", "run", "test:hidden"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )

    assert hidden.returncode != 0
    assert "over-eager hydration" in (hidden.stderr + hidden.stdout)


def _apply_valid_fixture_solution(project_root: Path) -> None:
    (project_root / "src/content").mkdir(parents=True, exist_ok=True)
    (project_root / "src/components/islands").mkdir(parents=True, exist_ok=True)
    (project_root / "src/content/resources.ts").write_text(
        "\n".join(
            (
                "export const resources = [",
                "  { title: 'Intake checklist', category: 'Guide', summary: 'Prepare a bounded request.' },",
                "  { title: 'Review packet', category: 'Reference', summary: 'Confirm scope before launch.' },",
                "];",
                "",
            )
        ),
        encoding="utf-8",
    )
    (project_root / "src/components/islands/ResourceFilter.tsx").write_text(
        "\n".join(
            (
                "export default function ResourceFilter() {",
                "  return <div data-resource-filter>Filter resources</div>;",
                "}",
                "",
            )
        ),
        encoding="utf-8",
    )
    (project_root / "src/pages/resources.astro").write_text(
        "\n".join(
            (
                "---",
                "import Layout from '../layouts/Layout.astro';",
                "import ApprovedResourceShell from '../components/ApprovedResourceShell.astro';",
                "import ResourceFilter from '../components/islands/ResourceFilter';",
                "import { resources } from '../content/resources';",
                "---",
                "<Layout title=\"Resources\">",
                "  <ApprovedResourceShell heading=\"Resources\">",
                "    <ResourceFilter client:idle />",
                "    <ul>",
                "      {resources.map((resource) => <li>{resource.title} {resource.category} {resource.summary}</li>)}",
                "    </ul>",
                "  </ApprovedResourceShell>",
                "</Layout>",
                "",
            )
        ),
        encoding="utf-8",
    )
    (project_root / "src/components/SiteHeader.astro").write_text(
        "\n".join(
            (
                "<header class=\"site-header\">",
                "  <a href=\"/\" class=\"site-header__brand\">Website Fixture</a>",
                "  <nav aria-label=\"Primary\">",
                "    <a href=\"/\">Home</a>",
                "    <a href=\"/resources/\">Resources</a>",
                "  </nav>",
                "</header>",
                "",
            )
        ),
        encoding="utf-8",
    )
