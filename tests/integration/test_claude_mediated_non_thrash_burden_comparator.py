"""Integration revalidation for Claude non-thrash burden comparators."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import REPO_ROOT, parse_aux_burden_artifact, packet_without_path, parse_run_packet
from tests.integration._claude_mediation_non_thrash_burden import (
    CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS,
    CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS,
    CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS,
    build_claude_mediated_non_thrash_burden_episode_snapshot,
    build_claude_non_thrash_burden_mediated_artifact,
    build_claude_non_thrash_burden_mediated_packet,
    emit_claude_mediated_non_thrash_burden_candidate,
)
from tests.integration._claude_mediation_non_thrash_burden_episode import (
    CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS,
    build_claude_non_thrash_burden_baseline_artifact,
    build_claude_non_thrash_burden_baseline_packet,
    build_claude_non_thrash_burden_episode_snapshot,
)


def test_claude_non_thrash_burden_mediated_packet_matches_committed_doc() -> None:
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(REPO_ROOT / CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_PATHS[pair_key])
        )
        assert build_claude_non_thrash_burden_mediated_packet(pair_key) == committed_packet


def test_claude_non_thrash_burden_pair_reduces_visible_burden_without_thrashing() -> None:
    for pair_key in CLAUDE_NON_THRASH_BURDEN_PAIR_KEYS:
        baseline_snapshot = build_claude_non_thrash_burden_episode_snapshot(pair_key)
        mediated_snapshot = build_claude_mediated_non_thrash_burden_episode_snapshot(pair_key)
        baseline_artifact = build_claude_non_thrash_burden_baseline_artifact(pair_key)
        mediated_artifact = build_claude_non_thrash_burden_mediated_artifact(pair_key)

        assert baseline_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert mediated_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert "open" not in baseline_snapshot["interaction_sequence"]
        assert "resume" not in baseline_snapshot["interaction_sequence"]
        assert float(mediated_artifact["aux_burden_report"]["intervention_burden"]) < float(
            baseline_artifact["aux_burden_report"]["intervention_burden"]
        )


def test_claude_non_thrash_burden_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_claude_mediated_non_thrash_burden_candidate()
    captured = capsys.readouterr().out

    for relative_path in CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured
    for relative_path in CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS) | set(
        CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS
    )

    for relative_path, builder in CLAUDE_NON_THRASH_BURDEN_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()
    for relative_path, builder in CLAUDE_NON_THRASH_BURDEN_MEDIATED_ARTIFACT_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_artifact = {k: v for k, v in parse_aux_burden_artifact(temp_doc).items() if k != "path"}
        assert emitted_artifact == builder()


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []
    for line in output.splitlines():
        if line.startswith("--- docs/lab/mediation_evidence/claude/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)
    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs

