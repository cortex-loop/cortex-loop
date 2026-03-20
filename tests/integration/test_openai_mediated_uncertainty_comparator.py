"""Integration revalidation for the experimental OpenAI-only uncertainty comparator."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._openai_mediation_baseline_packets import (
    build_openai_uncertainty_baseline_packet,
)
from tests.integration._openai_mediation_uncertainty_episode import (
    EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE,
    OPENAI_UNCERTAINTY_PAIR_KEYS,
    OPENAI_UNCERTAINTY_PAIR_SPECS,
    build_openai_uncertainty_episode_snapshot,
)
from tests.integration._openai_mediation_uncertainty_experimental import (
    EXPERIMENTAL_OPENAI_UNCERTAINTY_STEP_SEQUENCE,
    OPENAI_UNCERTAINTY_MEDIATED_PACKET_DOC_BUILDERS,
    OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS as EMITTED_OPENAI_PACKET_PATHS,
    build_openai_mediated_uncertainty_episode_snapshot,
    build_openai_uncertainty_mediated_packet,
    emit_openai_mediated_uncertainty_candidate,
)


def test_openai_uncertainty_mediated_packet_matches_committed_doc() -> None:
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS[pair_key])
        )
        assert build_openai_uncertainty_mediated_packet(pair_key) == committed_packet


def test_openai_uncertainty_mediated_pair_remains_fair_and_reduces_uncertified_loops() -> None:
    for pair_key in OPENAI_UNCERTAINTY_PAIR_KEYS:
        baseline_packet = build_openai_uncertainty_baseline_packet(pair_key)
        mediated_packet = build_openai_uncertainty_mediated_packet(pair_key)
        baseline_snapshot = build_openai_uncertainty_episode_snapshot(pair_key)
        mediated_snapshot = build_openai_mediated_uncertainty_episode_snapshot(pair_key)

        assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
        assert (
            baseline_packet["header"]["paired_episode_set_id"]
            == OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key].pair_id
        )
        assert (
            mediated_packet["header"]["paired_episode_set_id"]
            == OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key].pair_id
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

        assert baseline_snapshot["step_sequence"] == list(EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE)
        assert mediated_snapshot["step_sequence"] == list(EXPERIMENTAL_OPENAI_UNCERTAINTY_STEP_SEQUENCE)
        assert baseline_snapshot["uncertified_loop_count"] == 2
        assert mediated_snapshot["uncertified_loop_count"] == 1
        assert baseline_snapshot["contradiction_ref"] == mediated_snapshot["contradiction_ref"]
        assert baseline_snapshot["degradation_ref"] == mediated_snapshot["degradation_ref"]
        assert baseline_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert mediated_snapshot["steps"][-1]["outcome_class"] == "certified-full-commitment"
        assert baseline_snapshot["steps"][0]["brake_state"] == "guarded"
        assert mediated_snapshot["steps"][0]["brake_state"] == "guarded"


def test_openai_uncertainty_mediated_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_openai_mediated_uncertainty_candidate()
    captured = capsys.readouterr().out

    for relative_path in EMITTED_OPENAI_PACKET_PATHS.values():
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(EMITTED_OPENAI_PACKET_PATHS.values())

    for relative_path, builder in OPENAI_UNCERTAINTY_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


def test_openai_uncertainty_pair_series_uses_distinct_predeclared_ids() -> None:
    baseline_paths = {path.name for path in OPENAI_UNCERTAINTY_BASELINE_PACKET_PATHS.values()}
    mediated_paths = {path.name for path in OPENAI_UNCERTAINTY_MEDIATED_PACKET_PATHS.values()}

    assert len({spec.pair_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_source_tag for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_summary for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.degradation_reason_code for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in OPENAI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len(baseline_paths) == 3
    assert len(mediated_paths) == 3


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
