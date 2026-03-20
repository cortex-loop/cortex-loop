"""Integration revalidation for the experimental Gemini-only thrash comparator."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    GEMINI_THRASH_BASELINE_PACKET_PATHS,
    GEMINI_THRASH_MEDIATED_PACKET_PATHS,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._gemini_mediation_baseline_packets import (
    build_gemini_thrash_baseline_packet,
)
from tests.integration._gemini_mediation_thrash_episode import (
    EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE,
    GEMINI_THRASH_PAIR_KEYS,
    GEMINI_THRASH_PAIR_SPECS,
    build_gemini_thrash_episode_snapshot,
)
from tests.integration._gemini_mediation_thrash_experimental import (
    EXPERIMENTAL_GEMINI_THRASH_BRANCH_SEQUENCE,
    GEMINI_THRASH_MEDIATED_PACKET_DOC_BUILDERS,
    GEMINI_THRASH_MEDIATED_PACKET_PATHS as EMITTED_THRASH_PACKET_PATHS,
    build_gemini_mediated_thrash_episode_snapshot,
    build_gemini_thrash_mediated_packet,
    emit_gemini_mediated_thrash_candidate,
)


def test_gemini_thrash_mediated_packet_matches_committed_doc() -> None:
    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(GEMINI_THRASH_MEDIATED_PACKET_PATHS[pair_key])
        )
        assert build_gemini_thrash_mediated_packet(pair_key) == committed_packet


def test_gemini_thrash_mediated_pair_remains_fair_and_reduces_branch_ops() -> None:
    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        baseline_packet = build_gemini_thrash_baseline_packet(pair_key)
        mediated_packet = build_gemini_thrash_mediated_packet(pair_key)
        baseline_snapshot = build_gemini_thrash_episode_snapshot(pair_key)
        mediated_snapshot = build_gemini_mediated_thrash_episode_snapshot(pair_key)

        assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
        assert (
            baseline_packet["header"]["paired_episode_set_id"]
            == GEMINI_THRASH_PAIR_SPECS[pair_key].pair_id
        )
        assert (
            mediated_packet["header"]["paired_episode_set_id"]
            == GEMINI_THRASH_PAIR_SPECS[pair_key].pair_id
        )
        assert (
            baseline_packet["variant_metadata"]["host_family"]
            == mediated_packet["variant_metadata"]["host_family"]
        )
        assert (
            baseline_packet["variant_metadata"]["scenario_family"]
            == mediated_packet["variant_metadata"]["scenario_family"]
        )
        assert (
            baseline_packet["variant_metadata"]["task_value_rubric_id"]
            == mediated_packet["variant_metadata"]["task_value_rubric_id"]
        )
        assert (
            baseline_packet["variant_metadata"]["approval_or_environment_context_id"]
            == mediated_packet["variant_metadata"]["approval_or_environment_context_id"]
        )
        assert baseline_packet["scenario_inputs"] == mediated_packet["scenario_inputs"]
        assert baseline_packet["invariant_lock"] == mediated_packet["invariant_lock"]

        assert baseline_snapshot["branch_sequence"] == list(EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE)
        assert mediated_snapshot["branch_sequence"] == list(EXPERIMENTAL_GEMINI_THRASH_BRANCH_SEQUENCE)
        assert len(mediated_snapshot["branch_sequence"]) < len(baseline_snapshot["branch_sequence"])
        assert baseline_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert mediated_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert baseline_snapshot["steps"][1]["brake_state"] == "guarded"
        assert mediated_snapshot["steps"][1]["brake_state"] == "guarded"


def test_gemini_thrash_mediated_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_gemini_mediated_thrash_candidate()
    captured = capsys.readouterr().out

    for relative_path in EMITTED_THRASH_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(EMITTED_THRASH_PACKET_PATHS.values())

    for relative_path, builder in GEMINI_THRASH_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


def test_gemini_thrash_pair_series_uses_distinct_predeclared_ids() -> None:
    baseline_paths = {path.name for path in GEMINI_THRASH_BASELINE_PACKET_PATHS.values()}
    mediated_paths = {path.name for path in GEMINI_THRASH_MEDIATED_PACKET_PATHS.values()}

    assert len({spec.pair_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len(baseline_paths) == 3
    assert len(mediated_paths) == 3


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []

    for line in output.splitlines():
        if line.startswith("--- docs/mediation_evidence/gemini/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs
