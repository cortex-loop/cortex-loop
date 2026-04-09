"""Integration revalidation for the first Gemini-only mediated host-realization pair."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    REPO_ROOT,
    packet_without_path,
    parse_run_packet,
)
from tests.integration._gemini_host_realization_pair import (
    GEMINI_HOST_REALIZATION_PAIR_KEYS,
    GEMINI_HOST_REALIZATION_PAIR_SPECS,
)
from tests.integration._gemini_mediated_lane_packet_example import (
    build_gemini_host_realization_specialization_snapshot,
)
from tests.integration._gemini_mediation_baseline_packets import (
    build_gemini_host_realization_baseline_packet,
)
from tests.integration._gemini_mediation_host_realization_experimental import (
    GEMINI_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS,
    GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATHS,
    build_gemini_host_realization_comparator_snapshot,
    build_gemini_host_realization_mediated_packet,
    emit_gemini_mediated_host_realization_candidate,
)


def test_gemini_host_realization_mediated_packet_matches_committed_doc() -> None:
    for pair_key in GEMINI_HOST_REALIZATION_PAIR_KEYS:
        committed_packet = packet_without_path(
            parse_run_packet(REPO_ROOT / GEMINI_HOST_REALIZATION_MEDIATED_PACKET_PATHS[pair_key])
        )

        assert build_gemini_host_realization_mediated_packet(pair_key) == committed_packet


def test_gemini_host_realization_pair_remains_fair_and_changes_only_specialization() -> None:
    baseline_specialization = build_gemini_host_realization_specialization_snapshot(
        clearly_superior=False,
    )
    mediated_specialization = build_gemini_host_realization_specialization_snapshot(
        clearly_superior=True,
    )
    seen_ids: dict[str, set[str]] = {
        "pair_ids": set(),
        "session_ids": set(),
        "candidate_ids": set(),
        "commitment_ids": set(),
        "artifact_ids": set(),
        "baseline_trace_ids": set(),
        "mediated_trace_ids": set(),
        "contradiction_tags": set(),
        "contradiction_summaries": set(),
        "degradation_codes": set(),
    }

    for pair_key in GEMINI_HOST_REALIZATION_PAIR_KEYS:
        spec = GEMINI_HOST_REALIZATION_PAIR_SPECS[pair_key]
        baseline_packet = build_gemini_host_realization_baseline_packet(pair_key)
        mediated_packet = build_gemini_host_realization_mediated_packet(pair_key)
        comparator = build_gemini_host_realization_comparator_snapshot(pair_key)

        assert baseline_packet["header"]["scenario_id"] == mediated_packet["header"]["scenario_id"]
        assert baseline_packet["header"]["paired_episode_set_id"] == spec.pair_id
        assert mediated_packet["header"]["paired_episode_set_id"] == spec.pair_id
        assert baseline_packet["header"]["run_id"] == spec.baseline_run_id
        assert mediated_packet["header"]["run_id"] == spec.mediated_run_id
        assert baseline_packet["variant_metadata"]["host_family"] == "gemini"
        assert baseline_packet["variant_metadata"] == mediated_packet["variant_metadata"] | {
            "variant": "baseline_non_mediated"
        }
        assert baseline_packet["scenario_inputs"] == mediated_packet["scenario_inputs"]
        assert baseline_packet["invariant_lock"] == mediated_packet["invariant_lock"]
        assert comparator["selected_family"] == "seek-context"
        assert comparator["host_opportunity_refs"] == ["mcp.query"]
        assert comparator["baseline_direct_opportunity_specialization_used"] == 0
        assert comparator["mediated_direct_opportunity_specialization_used"] == 1
        assert baseline_specialization["preferred_opportunity_ref"] is None
        assert mediated_specialization["preferred_opportunity_ref"] == "mcp.query"
        assert baseline_specialization["direct_opportunity_specialization_used"] is False
        assert mediated_specialization["direct_opportunity_specialization_used"] is True
        assert comparator["baseline_packet_kind"] == "current-pair"
        assert comparator["mediated_packet_kind"] == "current-pair"
        assert comparator["baseline_verdict_status"] == "certified"
        assert comparator["mediated_verdict_status"] == "certified"
        contradiction_ref = comparator["contradiction_refs"][0]
        degradation_ref = comparator["degradation_refs"][0]
        assert contradiction_ref["source_tag"] == spec.contradiction_source_tag
        assert contradiction_ref["summary"] == spec.contradiction_summary
        assert degradation_ref["reason_code"] == spec.degradation_reason_code
        assert comparator["session_id"] == spec.session_id
        assert comparator["candidate_id"] == spec.candidate_id
        assert comparator["commitment_id"] == spec.commitment_id
        assert comparator["provenance_artifact_id"] == spec.provenance_artifact_id

        seen_ids["pair_ids"].add(spec.pair_id)
        seen_ids["session_ids"].add(spec.session_id)
        seen_ids["candidate_ids"].add(spec.candidate_id)
        seen_ids["commitment_ids"].add(spec.commitment_id)
        seen_ids["artifact_ids"].add(spec.provenance_artifact_id)
        seen_ids["baseline_trace_ids"].add(comparator["baseline_trace_id"])
        seen_ids["mediated_trace_ids"].add(comparator["mediated_trace_id"])
        seen_ids["contradiction_tags"].add(contradiction_ref["source_tag"])
        seen_ids["contradiction_summaries"].add(contradiction_ref["summary"])
        seen_ids["degradation_codes"].add(degradation_ref["reason_code"])

    for values in seen_ids.values():
        assert len(values) == len(GEMINI_HOST_REALIZATION_PAIR_KEYS)


def test_gemini_host_realization_mediated_candidate_emitter_prints_markdown(
    capsys, tmp_path: Path
) -> None:
    emit_gemini_mediated_host_realization_candidate()
    captured = capsys.readouterr().out

    for relative_path in GEMINI_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS:
        assert f"--- {relative_path}" in captured

    emitted_docs = _parse_emitted_docs(captured)
    assert set(emitted_docs) == set(GEMINI_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS)

    for relative_path, builder in GEMINI_HOST_REALIZATION_MEDIATED_PACKET_DOC_BUILDERS.items():
        temp_doc = tmp_path / Path(relative_path).name
        temp_doc.write_text(emitted_docs[relative_path], encoding="utf-8")
        emitted_packet = packet_without_path(parse_run_packet(temp_doc))
        assert emitted_packet == builder()


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
