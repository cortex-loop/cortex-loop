"""Integration revalidation for committed OpenAI mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    OPENAI_HOST_REALIZATION_PACKET_PATH,
    OPENAI_THRASH_BASELINE_PACKET_PATHS,
    OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._openai_mediation_baseline_packets import (
    OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
    OPENAI_THRASH_BASELINE_PACKET_PATHS as EMITTED_OPENAI_THRASH_PACKET_PATHS,
    OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS as EMITTED_OPENAI_PACKET_PATHS,
    build_openai_host_realization_baseline_packet,
    build_openai_thrash_baseline_packet,
    build_openai_uncertainty_baseline_packet,
    emit_openai_mediation_baseline_packets,
)
from tests.integration._openai_mediation_thrash_episode import (
    EXPECTED_OPENAI_THRASH_BRANCH_SEQUENCE,
    OPENAI_THRASH_PAIR_KEYS,
    OPENAI_THRASH_PAIR_SPECS,
    build_openai_thrash_episode_snapshot,
)
from tests.integration._openai_mediation_uncertainty_episode import (
    EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE,
    OPENAI_UNCERTAINTY_PAIR_KEYS,
    OPENAI_UNCERTAINTY_PAIR_SPECS,
    build_openai_uncertainty_episode_snapshot,
)


def test_openai_host_realization_baseline_packet_matches_committed_doc() -> None:
    committed_packet = packet_without_path(parse_run_packet(OPENAI_HOST_REALIZATION_PACKET_PATH))
    assert build_openai_host_realization_baseline_packet() == committed_packet


def test_openai_uncertainty_baseline_packet_matches_committed_doc() -> None:
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key])
        )
        assert build_openai_uncertainty_baseline_packet(pair_key) == committed_packet


def test_openai_uncertainty_baseline_series_records_expected_loop_shape() -> None:
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS:
        packet = build_openai_uncertainty_baseline_packet(pair_key)
        snapshot = build_openai_uncertainty_episode_snapshot(pair_key)

        assert packet["header"]["paired_episode_set_id"] == OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key].pair_id
        assert snapshot["step_sequence"] == list(EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE)
        assert snapshot["uncertified_loop_count"] == 2
        assert snapshot["steps"][0]["brake_state"] == "guarded"
        assert snapshot["steps"][1]["brake_state"] == "guarded"
        assert snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"


def test_openai_thrash_baseline_packet_matches_committed_doc() -> None:
    for pair_key in OPENAI_THRASH_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(OPENAI_THRASH_BASELINE_PACKET_PATHS[pair_key])
        )
        assert build_openai_thrash_baseline_packet(pair_key) == committed_packet


def test_openai_thrash_baseline_series_records_expected_branch_shape() -> None:
    for pair_key in OPENAI_THRASH_PAIR_KEYS:
        packet = build_openai_thrash_baseline_packet(pair_key)
        snapshot = build_openai_thrash_episode_snapshot(pair_key)

        assert packet["header"]["paired_episode_set_id"] == OPENAI_THRASH_PAIR_SPECS[pair_key].pair_id
        assert snapshot["branch_sequence"] == list(EXPECTED_OPENAI_THRASH_BRANCH_SEQUENCE)
        assert snapshot["steps"][1]["brake_state"] == "guarded"
        assert snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"


def test_candidate_emitter_prints_openai_baseline_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_openai_mediation_baseline_packets()
    captured = capsys.readouterr().out

    assert (
        "--- docs/mediation_evidence/openai/"
        "scenario_host_openai_01__baseline_non_mediated__run_001.md"
    ) in captured
    for relative_path in EMITTED_OPENAI_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured
    for relative_path in EMITTED_OPENAI_THRASH_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS)

    for relative_path, builder in OPENAI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


def test_openai_thrash_baseline_series_uses_distinct_predeclared_ids() -> None:
    assert len({spec.pair_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in OPENAI_THRASH_PAIR_SPECS.values()}) == 3


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []

    for line in output.splitlines():
        if line.startswith("--- docs/mediation_evidence/openai/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs
