from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab.invariant_runner import (
    CERTIFIED,
    UNCERTIFIED,
    InvariantEvidence,
    evaluate_invariants,
    extract_tool_evidence_from_records,
    first_forbidden_repair_term,
    load_invariant_config,
    render_factual_repair_ticket,
    validate_invariant_config,
)


def _base_config() -> dict[str, object]:
    return {
        "schema_version": 1,
        "fixture_id": "unit-fixture",
        "allowed_path_globs": ["src/**"],
        "forbidden_path_globs": [".github/**"],
        "required_reads": [],
        "required_commands": [],
        "source_patterns": [],
        "checks": [],
        "closure": {"require_verification_for_complete": True},
    }


def test_config_validation_rejects_unknown_schema() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        validate_invariant_config({"schema_version": 2, "fixture_id": "bad"})


def test_path_globs_fail_with_concrete_repair_fact(tmp_path: Path) -> None:
    config = _base_config()
    evidence = InvariantEvidence(
        modified_files=("src/pages/resources.astro", ".github/workflows/deploy.yml"),
        result_text="Done.",
        check_results=({"check_id": "verify", "exit_code": 0},),
    )

    evaluation = evaluate_invariants(config, evidence, project_root=tmp_path)
    ticket = render_factual_repair_ticket(evaluation)

    assert evaluation.status == UNCERTIFIED
    assert "`.github/workflows/deploy.yml` changed" in ticket
    assert "forbidden_path_drift" not in ticket
    assert first_forbidden_repair_term(ticket) is None


def test_source_patterns_are_generic_regex_checks(tmp_path: Path) -> None:
    page = tmp_path / "src/pages/resources.astro"
    page.parent.mkdir(parents=True)
    page.write_text("<ResourceFilter client:load />\n", encoding="utf-8")
    config = {
        **_base_config(),
        "allowed_path_globs": ["src/pages/resources.astro"],
        "forbidden_path_globs": [],
        "source_patterns": [
            {
                "id": "hydration",
                "path_globs": ["src/pages/resources.astro"],
                "required_regex": "ResourceFilter",
                "forbidden_regex": "client:(load|only)",
                "repair_fact": "`src/pages/resources.astro` must not use eager hydration.",
            }
        ],
    }

    evaluation = evaluate_invariants(
        config,
        InvariantEvidence(modified_files=("src/pages/resources.astro",), result_text="Blocked."),
        project_root=tmp_path,
    )

    assert evaluation.status == UNCERTIFIED
    assert evaluation.failed_repair_facts == ("`src/pages/resources.astro` must not use eager hydration.",)


def test_closure_claim_requires_check_evidence(tmp_path: Path) -> None:
    config = _base_config()
    evidence = InvariantEvidence(
        modified_files=("src/pages/resources.astro",),
        result_text="Done and verified.",
        check_results=({"check_id": "verify", "exit_code": 1, "stderr": "failed"},),
    )

    evaluation = evaluate_invariants(config, evidence, project_root=tmp_path)

    assert evaluation.status == UNCERTIFIED
    assert any(result.invariant_id == "closure_claim_evidence" for result in evaluation.results)


def test_closure_claim_fails_when_no_check_evidence_exists(tmp_path: Path) -> None:
    config = _base_config()
    evidence = InvariantEvidence(
        modified_files=("src/pages/resources.astro",),
        result_text="Done and verified.",
        check_results=(),
    )

    evaluation = evaluate_invariants(config, evidence, project_root=tmp_path)

    assert evaluation.status == UNCERTIFIED


def test_certified_when_required_invariants_pass(tmp_path: Path) -> None:
    config = {
        **_base_config(),
        "checks": [{"id": "verify", "command": ["npm", "run", "verify"]}],
    }
    evidence = InvariantEvidence(
        modified_files=("src/pages/resources.astro",),
        result_text="Verification: npm run verify passed.\nBlockers: none.",
        commands=("npm run verify",),
        check_results=({"check_id": "verify", "exit_code": 0},),
    )

    evaluation = evaluate_invariants(config, evidence, project_root=tmp_path)

    assert evaluation.status == CERTIFIED
    assert evaluation.mechanical_score == 1.0


def test_extract_tool_evidence_from_claude_stream_records(tmp_path: Path) -> None:
    records = [
        {
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": str(tmp_path / "AGENTS.md")},
                    },
                    {
                        "type": "tool_use",
                        "name": "Bash",
                        "input": {"command": "npm run verify"},
                    },
                ]
            }
        }
    ]

    evidence = extract_tool_evidence_from_records(records, project_root=tmp_path)

    assert evidence.read_paths == ("AGENTS.md",)
    assert evidence.commands == ("npm run verify",)


def test_load_invariant_config_reads_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_base_config()), encoding="utf-8")

    assert load_invariant_config(path)["fixture_id"] == "unit-fixture"
