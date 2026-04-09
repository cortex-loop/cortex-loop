"""Integration revalidation for OpenAI branch-discipline comparators."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import REPO_ROOT, packet_without_path, parse_run_packet
from tests.integration._openai_mediation_branch_discipline_episode import (
    OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS,
    OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS,
    build_openai_branch_discipline_baseline_packet,
    build_openai_branch_discipline_episode_snapshot,
)
from tests.integration._openai_mediation_branch_discipline_experimental import (
    OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS,
    OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS,
    build_openai_branch_discipline_mediated_packet,
    build_openai_mediated_branch_discipline_episode_snapshot,
    emit_openai_mediated_branch_discipline_candidate,
)


def test_openai_branch_discipline_mediated_packet_matches_committed_doc() -> None:
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(REPO_ROOT / OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_PATHS[pair_key])
        )
        assert build_openai_branch_discipline_mediated_packet(pair_key) == committed_packet


def test_openai_branch_discipline_pair_reduces_branch_debt() -> None:
    for pair_key in OPENAI_BRANCH_DISCIPLINE_PAIR_KEYS:
        baseline_packet = build_openai_branch_discipline_baseline_packet(pair_key)
        mediated_packet = build_openai_branch_discipline_mediated_packet(pair_key)
        baseline_snapshot = build_openai_branch_discipline_episode_snapshot(pair_key)
        mediated_snapshot = build_openai_mediated_branch_discipline_episode_snapshot(pair_key)

        assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
        assert baseline_packet["header"]["paired_episode_set_id"] == OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].pair_id
        assert mediated_packet["header"]["paired_episode_set_id"] == OPENAI_BRANCH_DISCIPLINE_PAIR_SPECS[pair_key].pair_id
        assert baseline_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert mediated_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert mediated_snapshot["orphaned_branch_count"] == 0
        assert (
            mediated_snapshot["stale_branch_count"] + mediated_snapshot["unnecessary_branch_count"]
            < baseline_snapshot["stale_branch_count"] + baseline_snapshot["unnecessary_branch_count"]
        )
        assert mediated_snapshot["reopen_resume_count"] < baseline_snapshot["reopen_resume_count"]


def test_openai_branch_discipline_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_openai_mediated_branch_discipline_candidate()
    captured = capsys.readouterr().out

    for relative_path in OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS)

    for relative_path, builder in OPENAI_BRANCH_DISCIPLINE_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []
    for line in output.splitlines():
        if line.startswith("--- docs/lab/mediation_evidence/openai/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)
    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs

