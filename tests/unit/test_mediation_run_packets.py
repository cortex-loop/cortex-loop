"""Mechanical checks for committed mediation run packets."""

from __future__ import annotations

from pathlib import Path

from tests._mediation_evidence import (
    GEMINI_BASELINE_INDEX_PATH,
    GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS,
    GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATH,
    GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    GEMINI_UNCERTAINTY_PACKET_PATH,
    MEDIATION_REFERENCE_PACKET_ROOT,
    MEDIATION_GEMINI_PACKET_ROOT,
    REFERENCE_BASELINE_INDEX_PATH,
    REFERENCE_UNCERTAINTY_BASELINE_PACKET_PATHS,
    REFERENCE_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    REFERENCE_UNCERTAINTY_PACKET_PATH,
    REFERENCE_THRASH_BASELINE_PACKET_PATHS,
    REFERENCE_THRASH_MEDIATED_PACKET_PATHS,
    RUN_PACKET_INVARIANT_FIELDS,
    VERDICTS,
    all_tags_allowed,
    load_failure_tags,
    load_scenarios,
    parse_markdown_table,
    parse_run_packet,
    read,
    section,
    status,
)


def test_reference_baseline_index_is_reference_only_and_commits_all_reference_packets() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))

    assert REFERENCE_BASELINE_INDEX_PATH.is_file()
    assert status(REFERENCE_BASELINE_INDEX_PATH) == "reference mediation baseline run index (`active`, baseline-only)"
    assert len(rows) == 3
    assert {row["scenario_id"] for row in rows} == {
        "scenario_uncertainty_reference_01",
        "scenario_host_reference_01",
        "scenario_thrash_reference_01",
    }

    for row in rows:
        assert row["host_family"] == "reference"
        assert row["variant"] == "baseline_non_mediated"
        assert row["scenario_id"] in scenarios
        assert scenarios[row["scenario_id"]]["host_family"] == "reference"
        assert all_tags_allowed(row["failure_tags"], failure_tags)

        assert row["evidence_status"] == "baseline_packet_committed"
        packet_path = Path(row["packet_path"])
        assert packet_path.parts[:3] == ("docs", "mediation_evidence", "reference")
        assert (REFERENCE_BASELINE_INDEX_PATH.parents[1] / packet_path).is_file()
    assert row["failure_tags"] == "none"


def test_gemini_baseline_index_is_gemini_only_and_commits_one_gemini_anchor() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))

    assert GEMINI_BASELINE_INDEX_PATH.is_file()
    assert status(GEMINI_BASELINE_INDEX_PATH) == "gemini mediation baseline run index (`active`, baseline-only)"
    assert len(rows) == 1
    row = rows[0]

    assert row["scenario_id"] == "scenario_uncertainty_gemini_01"
    assert row["host_family"] == "gemini"
    assert row["variant"] == "baseline_non_mediated"
    assert row["paired_episode_set_id"] == "pair_gemini_uncertainty_001"
    assert row["scenario_id"] in scenarios
    assert scenarios[row["scenario_id"]]["host_family"] == "gemini"
    assert all_tags_allowed(row["failure_tags"], failure_tags)
    assert row["evidence_status"] == "baseline_packet_committed"
    packet_path = Path(row["packet_path"])
    assert packet_path.parts[:3] == ("docs", "mediation_evidence", "gemini")
    assert (GEMINI_BASELINE_INDEX_PATH.parents[1] / packet_path).is_file()
    assert row["failure_tags"] == "none"


def test_committed_reference_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    baseline_packets = sorted(MEDIATION_REFERENCE_PACKET_ROOT.glob("*__baseline_non_mediated__run_*.md"))

    assert len(baseline_packets) == 7

    for packet_path in baseline_packets:
        packet = parse_run_packet(packet_path)
        scenario = scenarios[packet["header"]["scenario_id"]]

        assert packet["status"] == "reviewed_evidence"
        assert packet["variant_metadata"]["variant"] == "baseline_non_mediated"
        assert packet["variant_metadata"]["host_family"] == "reference"
        assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
        assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
        assert (
            packet["variant_metadata"]["approval_or_environment_context_id"]
            == scenario["approval_or_environment_context_id"]
        )

        if packet["header"]["scenario_id"] == "scenario_host_reference_01":
            rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
            row = next(row for row in rows if row["scenario_id"] == packet["header"]["scenario_id"])
            assert packet["header"]["run_id"] == row["run_id"]
            assert packet["header"]["paired_episode_set_id"] == row["paired_episode_set_id"]
        elif packet["header"]["scenario_id"] == "scenario_uncertainty_reference_01":
            assert packet_path in REFERENCE_UNCERTAINTY_BASELINE_PACKET_PATHS.values()
            assert packet["header"]["run_id"].startswith("reference_uncertainty_baseline_run_")
            assert packet["header"]["paired_episode_set_id"].startswith(
                "pair_reference_uncertainty_"
            )
            if packet_path == REFERENCE_UNCERTAINTY_PACKET_PATH:
                rows = parse_markdown_table(section(read(REFERENCE_BASELINE_INDEX_PATH), "Index Rows"))
                row = next(row for row in rows if row["scenario_id"] == packet["header"]["scenario_id"])
                assert packet["header"]["run_id"] == row["run_id"]
                assert packet["header"]["paired_episode_set_id"] == row["paired_episode_set_id"]
        else:
            assert packet_path in REFERENCE_THRASH_BASELINE_PACKET_PATHS.values()
            assert packet["header"]["run_id"].startswith("reference_thrash_baseline_run_")
            assert packet["header"]["paired_episode_set_id"].startswith("pair_reference_thrash_")

        for field_name in RUN_PACKET_INVARIANT_FIELDS:
            assert packet["invariant_lock"][field_name] == "yes"

        for axis_payload in packet["lift_axes"].values():
            assert axis_payload["verdict"] in VERDICTS
            assert axis_payload["verdict"] == "insufficient"

        assert packet["exclusions"]["exclusion_status"] == "none"
        assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
        assert packet["exclusions"]["failure_tags"] == "none"
        reviewer_note = packet["reviewer_note"]["reviewer_note"]
        assert "baseline-only committed evidence" in reviewer_note
        assert "not comparative mediation evidence" in reviewer_note
        assert "does not justify mediation" in reviewer_note


def test_committed_gemini_baseline_packets_match_catalog_and_stay_baseline_only() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    baseline_packets = sorted(MEDIATION_GEMINI_PACKET_ROOT.glob("*__baseline_non_mediated__run_*.md"))

    assert len(baseline_packets) == 3

    for packet_path in baseline_packets:
        packet = parse_run_packet(packet_path)
        scenario = scenarios[packet["header"]["scenario_id"]]

        assert packet["status"] == "reviewed_evidence"
        assert packet["variant_metadata"]["variant"] == "baseline_non_mediated"
        assert packet["variant_metadata"]["host_family"] == "gemini"
        assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
        assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
        assert (
            packet["variant_metadata"]["approval_or_environment_context_id"]
            == scenario["approval_or_environment_context_id"]
        )
        assert packet["header"]["scenario_id"] == "scenario_uncertainty_gemini_01"
        assert packet_path in GEMINI_UNCERTAINTY_BASELINE_PACKET_PATHS.values()
        assert packet["header"]["run_id"].startswith("gemini_uncertainty_baseline_run_")
        assert packet["header"]["paired_episode_set_id"].startswith("pair_gemini_uncertainty_")

        if packet_path == GEMINI_UNCERTAINTY_PACKET_PATH:
            rows = parse_markdown_table(section(read(GEMINI_BASELINE_INDEX_PATH), "Index Rows"))
            row = next(row for row in rows if row["scenario_id"] == packet["header"]["scenario_id"])
            assert packet["header"]["run_id"] == row["run_id"]
            assert packet["header"]["paired_episode_set_id"] == row["paired_episode_set_id"]

        for field_name in RUN_PACKET_INVARIANT_FIELDS:
            assert packet["invariant_lock"][field_name] == "yes"

        for axis_payload in packet["lift_axes"].values():
            assert axis_payload["verdict"] in VERDICTS
            assert axis_payload["verdict"] == "insufficient"

        assert packet["exclusions"]["exclusion_status"] == "none"
        assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
        assert packet["exclusions"]["failure_tags"] == "none"
        reviewer_note = packet["reviewer_note"]["reviewer_note"]
        assert "baseline-only committed evidence" in reviewer_note
        assert "does not justify mediation" in reviewer_note


def test_experimental_gemini_packets_match_catalog_and_stay_experimental() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()

    for packet_path in GEMINI_UNCERTAINTY_MEDIATED_PACKET_PATHS.values():
        packet = parse_run_packet(packet_path)
        scenario = scenarios[packet["header"]["scenario_id"]]

        assert packet_path.is_file()
        assert packet["status"] == "reviewed_evidence"
        assert packet["header"]["scenario_id"] == "scenario_uncertainty_gemini_01"
        assert packet["header"]["run_id"].startswith("gemini_uncertainty_mediated_run_")
        assert packet["header"]["paired_episode_set_id"].startswith("pair_gemini_uncertainty_")
        assert packet["variant_metadata"]["variant"] == "experimental_mediated"
        assert packet["variant_metadata"]["host_family"] == "gemini"
        assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
        assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
        assert (
            packet["variant_metadata"]["approval_or_environment_context_id"]
            == scenario["approval_or_environment_context_id"]
        )

        for field_name in RUN_PACKET_INVARIANT_FIELDS:
            assert packet["invariant_lock"][field_name] == "yes"

        for axis_payload in packet["lift_axes"].values():
            assert axis_payload["verdict"] in VERDICTS
            assert axis_payload["verdict"] == "insufficient"

        assert packet["exclusions"]["exclusion_status"] == "none"
        assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
        assert packet["exclusions"]["failure_tags"] == "none"
        reviewer_note = packet["reviewer_note"]["reviewer_note"]
        assert "experimental mediated evidence only" in reviewer_note
        assert "Gemini-only" in reviewer_note
        assert "package-level evidence notes govern any verdict" in reviewer_note


def test_experimental_reference_packets_match_catalog_and_stay_experimental() -> None:
    scenarios = load_scenarios()
    failure_tags = load_failure_tags()
    mediated_packets = {
        **REFERENCE_THRASH_MEDIATED_PACKET_PATHS,
        **REFERENCE_UNCERTAINTY_MEDIATED_PACKET_PATHS,
    }

    for packet_path in mediated_packets.values():
        packet = parse_run_packet(packet_path)
        scenario = scenarios[packet["header"]["scenario_id"]]

        assert packet_path.is_file()
        assert packet["status"] == "reviewed_evidence"
        if packet["header"]["scenario_id"] == "scenario_thrash_reference_01":
            assert packet["header"]["run_id"].startswith("reference_thrash_mediated_run_")
            assert packet["header"]["paired_episode_set_id"].startswith("pair_reference_thrash_")
        else:
            assert packet["header"]["scenario_id"] == "scenario_uncertainty_reference_01"
            assert packet["header"]["run_id"].startswith("reference_uncertainty_mediated_run_")
            assert packet["header"]["paired_episode_set_id"].startswith(
                "pair_reference_uncertainty_"
            )
        assert packet["variant_metadata"]["variant"] == "experimental_mediated"
        assert packet["variant_metadata"]["host_family"] == "reference"
        assert packet["variant_metadata"]["scenario_family"] == scenario["scenario_family"]
        assert packet["variant_metadata"]["task_value_rubric_id"] == scenario["task_value_rubric_id"]
        assert (
            packet["variant_metadata"]["approval_or_environment_context_id"]
            == scenario["approval_or_environment_context_id"]
        )

        for field_name in RUN_PACKET_INVARIANT_FIELDS:
            assert packet["invariant_lock"][field_name] == "yes"

        for axis_payload in packet["lift_axes"].values():
            assert axis_payload["verdict"] in VERDICTS
            assert axis_payload["verdict"] == "insufficient"

        assert packet["exclusions"]["exclusion_status"] == "none"
        assert all_tags_allowed(packet["exclusions"]["failure_tags"], failure_tags)
        assert packet["exclusions"]["failure_tags"] == "none"
        reviewer_note = packet["reviewer_note"]["reviewer_note"]
        assert "experimental mediated evidence only" in reviewer_note
        assert "reference-only" in reviewer_note
        assert "package-level evidence notes govern any verdict" in reviewer_note


def test_reference_packet_directory_contains_seven_baselines_and_six_experimental_packets() -> None:
    packet_names = sorted(path.name for path in MEDIATION_REFERENCE_PACKET_ROOT.glob("*.md"))
    assert packet_names == [
        "scenario_host_reference_01__baseline_non_mediated__run_001.md",
        "scenario_thrash_reference_01__baseline_non_mediated__run_001.md",
        "scenario_thrash_reference_01__baseline_non_mediated__run_002.md",
        "scenario_thrash_reference_01__baseline_non_mediated__run_003.md",
        "scenario_thrash_reference_01__experimental_mediated__run_001.md",
        "scenario_thrash_reference_01__experimental_mediated__run_002.md",
        "scenario_thrash_reference_01__experimental_mediated__run_003.md",
        "scenario_uncertainty_reference_01__baseline_non_mediated__run_001.md",
        "scenario_uncertainty_reference_01__baseline_non_mediated__run_002.md",
        "scenario_uncertainty_reference_01__baseline_non_mediated__run_003.md",
        "scenario_uncertainty_reference_01__experimental_mediated__run_001.md",
        "scenario_uncertainty_reference_01__experimental_mediated__run_002.md",
        "scenario_uncertainty_reference_01__experimental_mediated__run_003.md",
    ]


def test_gemini_packet_directory_contains_three_baselines_and_three_experimental_packets() -> None:
    packet_names = sorted(path.name for path in MEDIATION_GEMINI_PACKET_ROOT.glob("*.md"))
    assert packet_names == [
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_001.md",
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_002.md",
        "scenario_uncertainty_gemini_01__baseline_non_mediated__run_003.md",
        "scenario_uncertainty_gemini_01__experimental_mediated__run_001.md",
        "scenario_uncertainty_gemini_01__experimental_mediated__run_002.md",
        "scenario_uncertainty_gemini_01__experimental_mediated__run_003.md",
    ]
