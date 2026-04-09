"""Integration revalidation for committed Gemini mediation baseline packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REPO_ROOT,
    GEMINI_THRASH_BASELINE_PACKET_PATHS,
    GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    parse_aux_burden_artifact,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._gemini_host_realization_pair import (
    GEMINI_HOST_REALIZATION_PAIR_KEYS,
    GEMINI_HOST_REALIZATION_PAIR_SPECS,
)
from tests.integration._gemini_mediation_baseline_packets import (
    GEMINI_HOST_REALIZATION_BASELINE_PACKET_PATHS,
    GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS,
    GEMINI_THRASH_BASELINE_BURDEN_DOC_BUILDERS,
    GEMINI_THRASH_BASELINE_BURDEN_PATHS,
    build_gemini_host_realization_baseline_packet,
    build_gemini_thrash_baseline_burden_artifact,
    build_gemini_thrash_baseline_packet,
    build_gemini_uncertainty_baseline_packet,
    emit_gemini_mediation_baseline_packets,
)
from tests.integration._gemini_mediation_thrash_episode import (
    EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE,
    GEMINI_THRASH_PAIR_KEYS,
    GEMINI_THRASH_PAIR_SPECS,
    build_gemini_thrash_episode_snapshot,
)
from tests.integration._gemini_mediation_uncertainty_episode import (
    EXPECTED_GEMINI_UNCERTAINTY_STEP_SEQUENCE,
    GEMINI_UNCERTAINTY_PAIR_KEYS,
    GEMINI_UNCERTAINTY_PAIR_SPECS,
    build_gemini_uncertainty_episode_snapshot,
)


def test_gemini_uncertainty_baseline_packet_matches_committed_doc() -> None:
    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS[pair_key])
        )
        assert build_gemini_uncertainty_baseline_packet(pair_key) == committed_packet


def test_gemini_host_realization_baseline_packet_matches_committed_doc() -> None:
    for pair_key in GEMINI_HOST_REALIZATION_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(Path(GEMINI_HOST_REALIZATION_BASELINE_PACKET_PATHS[pair_key]))
        )

        assert build_gemini_host_realization_baseline_packet(pair_key) == committed_packet


def test_gemini_thrash_baseline_packet_matches_committed_doc() -> None:
    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(GEMINI_THRASH_BASELINE_PACKET_PATHS[pair_key])
        )
        assert build_gemini_thrash_baseline_packet(pair_key) == committed_packet


def test_gemini_thrash_baseline_burden_artifact_matches_committed_doc() -> None:
    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        committed_path = REPO_ROOT / GEMINI_THRASH_BASELINE_BURDEN_PATHS[pair_key]
        committed_artifact = {
            key: value
            for key, value in parse_aux_burden_artifact(committed_path).items()
            if key != "path"
        }
        assert build_gemini_thrash_baseline_burden_artifact(pair_key) == committed_artifact


def test_gemini_uncertainty_baseline_series_uses_distinct_predeclared_ids() -> None:
    baseline_paths = {path.name for path in GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS.values()}

    for pair_key in GEMINI_UNCERTAINTY_PAIR_KEYS:
        snapshot = build_gemini_uncertainty_episode_snapshot(pair_key)
        assert snapshot["step_sequence"] == list(EXPECTED_GEMINI_UNCERTAINTY_STEP_SEQUENCE)
        assert snapshot["uncertified_loop_count"] == 2

    assert len({spec.pair_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_source_tag for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_summary for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.degradation_reason_code for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in GEMINI_UNCERTAINTY_PAIR_SPECS.values()}) == 3
    assert len(baseline_paths) == 3


def test_gemini_thrash_baseline_series_uses_distinct_predeclared_ids() -> None:
    baseline_paths = {path.name for path in GEMINI_THRASH_BASELINE_PACKET_PATHS.values()}

    for pair_key in GEMINI_THRASH_PAIR_KEYS:
        snapshot = build_gemini_thrash_episode_snapshot(pair_key)
        assert snapshot["branch_sequence"] == list(EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE)

    assert len({spec.pair_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.branch_track_ref for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len({spec.uncertainty_spike_tag for spec in GEMINI_THRASH_PAIR_SPECS.values()}) == 3
    assert len(baseline_paths) == 3


def test_gemini_host_realization_baseline_series_uses_distinct_predeclared_ids() -> None:
    baseline_paths = {
        Path(path).name for path in GEMINI_HOST_REALIZATION_BASELINE_PACKET_PATHS.values()
    }

    for pair_key in GEMINI_HOST_REALIZATION_PAIR_KEYS:
        snapshot = build_gemini_host_realization_baseline_packet(pair_key)
        assert snapshot["header"]["scenario_id"] == "scenario_host_gemini_01"
        assert snapshot["variant_metadata"]["variant"] == "baseline_non_mediated"

    assert len({spec.pair_id for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.session_id for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.candidate_id for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.commitment_id for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.provenance_artifact_id for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_source_tag for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.contradiction_summary for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len({spec.degradation_reason_code for spec in GEMINI_HOST_REALIZATION_PAIR_SPECS.values()}) == 3
    assert len(baseline_paths) == 3


def test_candidate_emitter_prints_all_gemini_baseline_packets_as_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_gemini_mediation_baseline_packets()
    captured = capsys.readouterr().out

    for relative_path in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured
    for relative_path in GEMINI_THRASH_BASELINE_BURDEN_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS) | set(
        GEMINI_THRASH_BASELINE_BURDEN_DOC_BUILDERS
    )

    for relative_path, builder in GEMINI_MEDIATION_BASELINE_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()
    for relative_path, builder in GEMINI_THRASH_BASELINE_BURDEN_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_artifact = {
            key: value for key, value in parse_aux_burden_artifact(temp_doc).items() if key != "path"
        }
        assert emitted_artifact == builder()


def _parse_emitted_docs(output: str) -> dict[str, str]:
    docs: dict[str, str] = {}
    current_path: str | None = None
    current_lines: list[str] = []

    for line in output.splitlines():
        if line.startswith("--- docs/lab/mediation_evidence/gemini/"):
            if current_path is not None:
                docs[current_path] = "\n".join(current_lines).strip() + "\n"
            current_path = line[4:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_path is not None:
        docs[current_path] = "\n".join(current_lines).strip() + "\n"
    return docs
